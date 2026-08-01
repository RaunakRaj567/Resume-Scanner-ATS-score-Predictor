TechSpec

Purpose

Resume ATS Reader — local-first tool that parses resumes (PDF DOCX TXT), extracts tokens and structured fields, computes per-domain ATS scores (AI ML, Data Science, Software Developer, Backend Developer, etc.), and generates actionable suggestions. Optional Gemini API for semantic matching and rewrites; mock mode for offline development.

High Level Architecture

Frontend: Streamlit demo for upload, preview, highlights, and suggestion acceptance.

Backend: FastAPI orchestrator for extraction, NLP, scoring, and Gemini orchestration.

Storage: Local filesystem for uploads; SQLite for caching embeddings and results.

NLP and Extraction: spaCy, rapidfuzz, pdfplumber/PyMuPDF, python-docx, optional pytesseract for OCR.

LLM: Gemini API optional; mock client for offline dev.

Core Components

Uploader app/api/routes.py — file upload and resume management endpoints.

Extractor app/services/extractor.py — text extraction, layout, bullets, OCR fallback.

NLP app/services/nlp.py — tokenization, lemmatization, sentence split, NER.

Ontology Loader app/services/ontology.py — load domain keyword JSONs.

Scoring Engine app/services/scoring.py — compute per-domain scores and subscores.

Gemini Client app/services/gemini_client.py — embeddings, rewrites, mock mode.

File Store app/storage/file_store.py — save and delete uploads.

UI web/streamlit_app.py — local demo and interaction.

Data Models

ResumeRecord: id, filename, extracted_text, entities, tokens, domain_scores, suggestions, created_at.

Ontology JSON fields: keyword, weight, synonyms, context_examples.

Job Corpus: stored under data/job_descriptions for TF‑IDF and domain vectors.

Scoring Formula

Final score per domain 0–100 computed as weighted sum:

Keyword Match 40% — exact and fuzzy matches, weighted by ontology.

Experience Signal 30% — years, seniority, relevant roles and projects.

Education and Certifications 20% — degree levels, academic depth, and cert matches.

Format and Readability 10% — headings, bullets, contact info, OCR artifacts.

Return detailed breakdown with matched keywords, locations, match type, and subscore contributions.

Gemini Integration

Use cases: embeddings for contextual scoring, domain classification, rewrite generation, explainability.

Pattern: batch sentences for embeddings, cache vectors in SQLite, limit rewrite calls to user-selected bullets.

Mock mode: deterministic embeddings and canned rewrites for offline development and CI.

API Endpoints

POST /upload — upload resume, returns resume_id.

GET /score/{resume_id} — per-domain scores, subscores, matched keywords.

POST /suggest/{resume_id} — request rewrites for selected bullets and target domain.

DELETE /upload/{resume_id} — delete file and cached data.

Performance Targets
Latency: extraction and scoring under 10 seconds for a 2‑page resume on a typical dev laptop without Gemini.

Accuracy: extraction ≥ 95% on clean PDFs/DOCX; keyword detection precision ≥ 90%.

Testing Strategy
Unit tests: extractor edge cases, tokenization, ontology matching, scoring math.

Integration tests: end-to-end pipeline on data/sample_resumes.

Gemini mock tests: deterministic behavior for embeddings and rewrites.

Security and Privacy
Local by default: no external storage unless user enables Gemini.

Secrets: GEMINI_API_KEY in .env; never commit.

Data deletion: delete endpoint and CLI script to purge data/uploads and caches.

Logging: mask PII in logs.

Local Run Notes

Create virtualenv and install requirements.txt.

Copy .env.example to .env and set GEMINI_MOCK=true for offline.

Start backend: uvicorn app.main:app --reload --port 8000.

Start UI: streamlit run web/streamlit_app.py.

Extensibility
Add domains by dropping JSON into data/ontologies.

Tune scoring weights in app/services/scoring.py or via a config file.

Swap Gemini for another embedding provider by implementing the same client interface.