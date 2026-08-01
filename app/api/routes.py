import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from pydantic import BaseModel, Field

from app.services.extractor import extractor
from app.services.nlp import nlp_service
from app.services.scoring import scoring_engine
from app.services.gemini_client import gemini_client
from app.services.rag_pipeline import rag_pipeline
from app.storage.file_store import file_store
from app.utils.text_cleaning import split_into_bullets
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

class UploadResponse(BaseModel):
    resume_id: str
    filename: str
    char_count: int
    word_count: int
    message: str

class SuggestRequest(BaseModel):
    target_domain: str = "ai_ml"
    bullet_ids: Optional[List[str]] = None
    custom_bullet: Optional[str] = None

class TailorRequest(BaseModel):
    job_description: str
    target_domain: Optional[str] = "ai_ml"

class RAGQueryRequest(BaseModel):
    query: str

@router.get("/health")
def health_check():
    return {"status": "ok", "mock_mode": gemini_client.mock_mode}

@router.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume (PDF, DOCX, TXT), extract tokens/entities, store file and database record."""
    filename = file.filename
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if extension not in [".pdf", ".docx", ".doc", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {extension}")

    resume_id = str(uuid.uuid4())
    content = await file.read()

    # Save to disk
    file_path = file_store.save_upload_file(resume_id, filename, content)

    # Extract text & sections
    try:
        extraction_res = extractor.extract_from_file(file_path)
    except Exception as e:
        logger.error(f"Extraction failed for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    extracted_text = extraction_res["extracted_text"]
    sections = extraction_res["sections"]

    # NLP processing
    nlp_res = nlp_service.process_text(extracted_text)

    # Save record
    record = {
        "id": resume_id,
        "filename": filename,
        "extracted_text": extracted_text,
        "sections": sections,
        "entities": nlp_res["entities"],
        "tokens": nlp_res["tokens"],
        "sentences": nlp_res["sentences"],
        "domain_scores": None,
        "suggestions": None,
        "embeddings_cached": 0
    }
    file_store.save_resume_record(record)

    return UploadResponse(
        resume_id=resume_id,
        filename=filename,
        char_count=extraction_res["char_count"],
        word_count=extraction_res["word_count"],
        message="Resume uploaded and processed successfully."
    )

@router.get("/score/{resume_id}")
def get_resume_score(resume_id: str):
    """Retrieve or compute domain scores, subscore breakdown, and matched keywords for a resume."""
    record = file_store.get_resume_record(resume_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    # Always re-evaluate against current JSON ontologies on disk
    domain_scores = scoring_engine.evaluate_resume(
        extracted_text=record["extracted_text"],
        sections=record["sections"],
        tokens=record["tokens"],
        sentences=record["sentences"],
        entities=record["entities"]
    )
    record["domain_scores"] = domain_scores
    file_store.save_resume_record(record)

    return {
        "resume_id": resume_id,
        "filename": record["filename"],
        "entities": record["entities"],
        "sections": record["sections"],
        "domain_scores": domain_scores
    }

@router.post("/suggest/{resume_id}")
def generate_suggestions(resume_id: str, request: SuggestRequest):
    """Generate conservative, truthful bullet rewrite suggestions obeying rules.md constraints."""
    record = file_store.get_resume_record(resume_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    target_domain = request.target_domain
    domain_scores = record.get("domain_scores") or scoring_engine.evaluate_resume(
        record["extracted_text"], record["sections"], record["tokens"], record["sentences"], record["entities"]
    )

    domain_data = domain_scores.get(target_domain, {})
    matched_kws = [m["kw"] for m in domain_data.get("matched_keywords", [])]

    # Determine missing high-weight keywords
    from app.services.ontology import ontology_loader
    all_domain_entries = ontology_loader.get_domain_ontology(target_domain)
    missing_kws = [e["keyword"] for e in all_domain_entries if e["keyword"] not in matched_kws][:5]

    # Select bullets to suggest rewrites for
    bullets = split_into_bullets(record["extracted_text"])
    target_bullet = request.custom_bullet or (bullets[0] if bullets else "Built software components.")

    candidate_skills = record.get("tokens", [])
    rewrites = gemini_client.generate_bullet_rewrites(
        original_bullet=target_bullet,
        target_keywords=missing_kws,
        target_domain=target_domain,
        candidate_skills=candidate_skills
    )

    # Format output according to Suggestion schema
    suggestions_list = []
    for idx, r in enumerate(rewrites):
        suggestions_list.append({
            "id": f"s_{idx+1}",
            "bullet_id": f"b_{idx+1}",
            "original": target_bullet,
            "rewrite": r.get("rewrite", ""),
            "reason": r.get("reason", "Adds targeted domain keyword while preserving facts."),
            "estimated_impact": r.get("estimated_impact", 3),
            "missing_keywords_addressed": missing_kws[:2]
        })

    return {
        "resume_id": resume_id,
        "target_domain": target_domain,
        "missing_keywords": missing_kws,
        "suggestions": suggestions_list
    }

@router.post("/tailor/{resume_id}")
def tailor_resume_to_job(resume_id: str, request: TailorRequest):
    """Tailor resume scoring against a pasted job description."""
    record = file_store.get_resume_record(resume_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    jd_text = request.job_description
    jd_nlp = nlp_service.process_text(jd_text)

    # Compute custom JD domain score using JD tokens as custom ontology entries
    jd_ontology = [{"keyword": tok.capitalize(), "weight": 1.0} for tok in jd_nlp["tokens"][:20]]
    custom_eval = scoring_engine.evaluate_domain(
        domain_key="custom_job",
        ontology_entries=jd_ontology,
        extracted_text=record["extracted_text"],
        sections=record["sections"],
        tokens=record["tokens"],
        sentences=record["sentences"],
        entities=record["entities"]
    )

    matched_kw_names = [m["kw"] for m in custom_eval.get("matched_keywords", [])]
    missing_jd_keywords = [tok.capitalize() for tok in jd_nlp["tokens"][:15] if tok.capitalize() not in matched_kw_names]

    return {
        "resume_id": resume_id,
        "tailored_score": custom_eval["score"],
        "subscores": custom_eval["subscores"],
        "matched_keywords": custom_eval["matched_keywords"],
        "missing_keywords": missing_jd_keywords[:8],
        "message": "Resume tailored successfully against job description."
    }

@router.post("/rag/query/{resume_id}")
def query_resume_rag(resume_id: str, request: RAGQueryRequest):
    """Execute vector retrieval and RAG Q&A against candidate resume chunks."""
    record = file_store.get_resume_record(resume_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    rag_result = rag_pipeline.answer_query(record, request.query)
    return rag_result

@router.delete("/upload/{resume_id}")
def delete_resume(resume_id: str):
    """Purge uploaded resume file and cached database records."""
    success = file_store.delete_resume_record(resume_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete resume record.")
    return {"message": f"Resume record and artifacts for {resume_id} deleted successfully."}
