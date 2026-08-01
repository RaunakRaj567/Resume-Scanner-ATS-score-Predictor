import os
import sys
import json
import uuid
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path for app module imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Setup page layout and title
st.set_page_config(
    page_title="Resume Scanner & ATS Predictor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS stylesheet
css_path = Path(__file__).resolve().parent / "static" / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Import backend services directly for seamless local execution
from app.services.extractor import extractor
from app.services.nlp import nlp_service
from app.services.scoring import scoring_engine, get_keyword_pct
from app.services.ontology import ontology_loader
from app.services.gemini_client import gemini_client
from app.services.rag_pipeline import rag_pipeline
from app.storage.file_store import file_store
from app.utils.text_cleaning import split_into_bullets

# Initialize Session State
if "resume_record" not in st.session_state:
    st.session_state["resume_record"] = None
if "applied_rewrites" not in st.session_state:
    st.session_state["applied_rewrites"] = []
if "target_domain" not in st.session_state:
    st.session_state["target_domain"] = "ai_ml"
if "last_processed_file" not in st.session_state:
    st.session_state["last_processed_file"] = None
# App Header Banner
st.markdown("""
<div class="main-header">
    <h1>Resume Scanner & ATS Predictor</h1>
    <p>Local-First Intelligent Resume Parser, Per-Domain ATS Scoring Engine & Truthful Suggestion Optimizer</p>
</div>
""", unsafe_allow_html=True)

# Inject explicit Light Mode CSS styles
st.markdown("""
<style>
    .stApp, div[data-testid="stAppViewContainer"], div[data-testid="stHeader"] { background-color: #F8FAFC !important; color: #0F172A !important; }
    .main-header { background: linear-gradient(135deg, #1E6FF3 0%, #0F4CB8 100%) !important; box-shadow: 0 4px 16px rgba(30, 111, 243, 0.2) !important; border: none !important; }
    .donut-score-box, .subscore-card, .suggestion-card { background-color: #FFFFFF !important; border-color: #E2E8F0 !important; color: #0F172A !important; }
    .subscore-header, .suggestion-rewrite { color: #0F172A !important; }
    .subscore-bar-bg { background-color: #E2E8F0 !important; }
    .resume-preview-box { background-color: #FFFFFF !important; border-color: #CBD5E1 !important; color: #0F172A !important; }
    div[data-testid="stVerticalBlock"] > div[style*="border"] { background-color: #FFFFFF !important; border-color: #E2E8F0 !important; color: #0F172A !important; }
    .donut-label { color: #475569 !important; }
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, div[data-testid="stMarkdownContainer"] { color: #0F172A !important; }
    div[data-baseweb="select"] > div, input, textarea { background-color: #FFFFFF !important; color: #0F172A !important; border-color: #CBD5E1 !important; }
    div[data-testid="stFileUploader"] section { background-color: #FFFFFF !important; border-color: #CBD5E1 !important; color: #0F172A !important; }
    div[data-testid="stFileUploader"] section * { color: #334155 !important; }
</style>
""", unsafe_allow_html=True)

def process_file_content(filename: str, content_bytes: bytes, file_path: Path = None):
    """Process uploaded file bytes or path through extraction, NLP, and scoring."""
    resume_id = str(uuid.uuid4())
    if file_path:
        saved_path = file_path
    else:
        saved_path = file_store.save_upload_file(resume_id, filename, content_bytes)

    extraction = extractor.extract_from_file(saved_path)
    nlp_res = nlp_service.process_text(extraction["extracted_text"])

    domain_scores = scoring_engine.evaluate_resume(
        extracted_text=extraction["extracted_text"],
        sections=extraction["sections"],
        tokens=nlp_res["tokens"],
        sentences=nlp_res["sentences"],
        entities=nlp_res["entities"]
    )

    record = {
        "id": resume_id,
        "filename": filename,
        "extracted_text": extraction["extracted_text"],
        "sections": extraction["sections"],
        "entities": nlp_res["entities"],
        "tokens": nlp_res["tokens"],
        "sentences": nlp_res["sentences"],
        "domain_scores": domain_scores,
        "suggestions": []
    }
    file_store.save_resume_record(record)
    st.session_state["resume_record"] = record
    st.session_state["last_processed_file"] = filename
    st.success(f"Successfully processed: {filename}")

# --- TOP CONTROL BAR: UPLOAD SECTION ---
with st.container(border=True):
    st.subheader("Upload Resume File")
    
    col_up, col_samples = st.columns([2, 1], gap="medium")
    with col_up:
        uploaded_file = st.file_uploader(
            "Select or drag & drop your resume (PDF, DOCX, TXT):",
            type=["pdf", "docx", "txt"],
            help="Processed 100% locally on your machine."
        )
        if uploaded_file is not None:
            if st.session_state.get("last_processed_file") != uploaded_file.name:
                with st.spinner(f"Analyzing {uploaded_file.name}..."):
                    file_bytes = uploaded_file.getvalue()
                    process_file_content(uploaded_file.name, file_bytes)

    with col_samples:
        st.markdown("**Or Load Test Sample Resume:**")
        sample_options = {
            "AI / ML Engineer": "sample_ai_ml_resume.txt",
            "Data Scientist": "sample_data_science_resume.txt",
            "Software Engineer": "sample_software_dev_resume.txt"
        }
        selected_sample_role = st.selectbox("Select Role Sample:", options=list(sample_options.keys()))
        if st.button("Load Selected Sample Resume", use_container_width=True, type="secondary"):
            sample_filename = sample_options[selected_sample_role]
            sample_path = Path("data/sample_resumes") / sample_filename
            if sample_path.exists():
                with open(sample_path, "rb") as f:
                    process_file_content(sample_filename, f.read(), sample_path)

record = st.session_state.get("resume_record")

if not record:
    st.info("Upload a PDF, DOCX, or TXT resume above to begin ATS scoring and keyword analysis.")
else:
    st.divider()
    
    # Always compute fresh scores against current JSON files on disk
    domain_scores = scoring_engine.evaluate_resume(
        extracted_text=record["extracted_text"],
        sections=record["sections"],
        tokens=record["tokens"],
        sentences=record["sentences"],
        entities=record["entities"]
    )
    record["domain_scores"] = domain_scores

    # Candidate Metadata & Domain Selector Bar
    col_meta, col_sel = st.columns([2, 1])
    with col_meta:
        st.markdown(f"**Candidate:** `{record['entities'].get('name', 'N/A')}` | **Email:** `{record['entities'].get('email', 'N/A')}` | **File:** `{record['filename']}`")
    with col_sel:
        selected_domain = st.selectbox(
            "Target Industry Domain:",
            options=list(domain_scores.keys()),
            format_func=lambda x: x.replace("_", " ").upper(),
            key="domain_selector"
        )
        st.session_state["target_domain"] = selected_domain

    # --- 3 SPACIOUS COLUMNS ---
    col_preview, col_scores, col_suggestions = st.columns([1, 1, 1], gap="large")

    # --- COLUMN 1: CANDIDATE INFO & TEXT PREVIEW ---
    with col_preview:
        with st.container(border=True):
            st.subheader("Candidate Overview & Text")
            st.markdown(f"**Name:** `{record['entities'].get('name', 'N/A')}`")
            st.markdown(f"**Email:** `{record['entities'].get('email', 'N/A')}`")
            st.markdown(f"**Phone:** `{record['entities'].get('phone', 'N/A')}`")
            st.markdown(f"**File:** `{record['filename']}`")

            st.markdown("---")
            st.markdown("**Parsed Text Preview (Matched Keywords Highlighted)**")
            
            domain_key = selected_domain
            domain_data = record.get("domain_scores", {}).get(domain_key, {})
            
            preview_text = record["extracted_text"]
            highlighted_text = preview_text
            seen_preview_kws = set()
            for m in domain_data.get("matched_keywords", []):
                kw = m["kw"]
                kw_lower = kw.strip().lower()
                if kw_lower not in seen_preview_kws:
                    seen_preview_kws.add(kw_lower)
                    # Replace ONLY the first occurrence (1 time only)
                    highlighted_text = highlighted_text.replace(kw, f'<span class="highlight-kw">{kw}</span>', 1)

            st.markdown(f'<div class="resume-preview-box">{highlighted_text}</div>', unsafe_allow_html=True)

    # --- COLUMN 2: ATS SCORES & SUBSCORES ---
    with col_scores:
        with st.container(border=True):
            st.subheader("Per-Domain ATS Scores")

            for dom_key, dom_data in domain_scores.items():
                score_val = dom_data["score"]
                st.markdown(f"**{dom_key.replace('_', ' ').title()}**: {score_val} / 100")
                st.progress(score_val / 100.0)

            st.markdown("---")
            selected_domain_data = domain_scores.get(selected_domain, {})
            subscores = selected_domain_data.get("subscores", {})
            subscore_meta = [
                ("Keyword Match", min(50.0, subscores.get("keyword", 0)), 50, "50%"),
                ("Experience Signal", min(25.0, subscores.get("experience", 0)), 25, "25%"),
                ("Education & Certs", min(15.0, subscores.get("education", 0)), 15, "15%"),
                ("Format & Readability", min(10.0, subscores.get("format", 0)), 10, "10%")
            ]

            score_color = "#16A34A" if selected_domain_data.get("score", 0) >= 75 else ("#CA8A04" if selected_domain_data.get("score", 0) >= 60 else "#DC2626")

            for label, val, max_val, weight_str in subscore_meta:
                val = min(float(max_val), round(float(val), 1))
                pct = min(1.0, (val / max_val)) if max_val > 0 else 0
                tag_class = "tag-excellent" if pct >= 0.85 else ("tag-strong" if pct >= 0.7 else ("tag-good" if pct >= 0.5 else "tag-work"))
                tag_name = "Excellent" if pct >= 0.85 else ("Strong" if pct >= 0.7 else ("Good" if pct >= 0.5 else "Needs Work"))
                
                st.markdown(f"""
                <div class="subscore-card">
                    <div class="subscore-header">
                        <span>{label} ({weight_str})</span>
                        <span>{val} / {max_val} <span class="subscore-tag {tag_class}">{tag_name}</span></span>
                    </div>
                    <div class="subscore-bar-bg">
                        <div class="subscore-bar-fill" style="width: {pct*100}%; background-color: {score_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- COLUMN 3: DONUT CHART & KEYWORD EVIDENCE ---
    with col_suggestions:
        with st.container(border=True):
            st.subheader("Score Visualization & Keyword Evidence")

            domain_key = st.session_state.get("target_domain", "ai_ml")
            domain_data = record.get("domain_scores", {}).get(domain_key, {})
            final_score = domain_data.get("score", 0)

            score_color = "#16A34A" if final_score >= 75 else ("#CA8A04" if final_score >= 60 else ("#EA580C" if final_score >= 50 else "#DC2626"))

            # Donut Chart SVG
            donut_svg = f"""
            <div class="donut-score-box">
                <svg width="110" height="110" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="48" fill="none" stroke="#E2E8F0" stroke-width="12"/>
                    <circle cx="60" cy="60" r="48" fill="none" stroke="{score_color}" stroke-width="12"
                            stroke-dasharray="{3.14159 * 96}" stroke-dashoffset="{3.14159 * 96 * (1 - final_score/100.0)}"
                            stroke-linecap="round" transform="rotate(-90 60 60)"/>
                </svg>
                <div class="donut-score-number" style="color: {score_color};">{final_score}</div>
                <div style="font-size: 13px; font-weight: 700;" class="donut-label">{domain_key.replace('_', ' ').upper()} ATS FIT SCORE</div>
            </div>
            """
            st.markdown(donut_svg, unsafe_allow_html=True)

            st.markdown("**Matched Keyword Evidence**")
            raw_matched_kws = domain_data.get("matched_keywords", [])
            # Deduplicate keywords by lowercased keyword name
            unique_matched_kws = []
            seen_kw_names = set()
            for mk in raw_matched_kws:
                kw_val = mk["kw"] if isinstance(mk, dict) else str(mk)
                kw_lower = kw_val.strip().lower()
                if kw_lower not in seen_kw_names:
                    seen_kw_names.add(kw_lower)
                    unique_matched_kws.append(mk if isinstance(mk, dict) else {"kw": mk, "type": "exact", "location": "summary"})

            total_ontology_kws = len(ontology_loader.get_domain_ontology(domain_key))
            matched_count = len(unique_matched_kws)
            benchmark_pct = round(get_keyword_pct(matched_count), 1)

            st.info(f"**Matched:** `{matched_count} Keywords` | **Target Benchmark:** `20 Matches (50%) -> 35 Matches (100%)` | **Keyword Coverage:** `{benchmark_pct}%` *(Total in Dictionary: {total_ontology_kws})*")

            if not unique_matched_kws:
                st.caption("No domain keywords matched yet.")
            else:
                badges_html = '<div class="badge-group">'
                for mk in unique_matched_kws[:15]:
                    badge_type = f"badge-{mk['type']}"
                    badges_html += f'<span class="badge {badge_type}">{mk["kw"]} ({mk["location"]})</span>'
                badges_html += '</div>'
                st.markdown(badges_html, unsafe_allow_html=True)

