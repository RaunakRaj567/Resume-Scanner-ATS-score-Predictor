Product Requirements Document

Overview

Product: Resume ATS Reader
Description: Local-first tool that ingests resumes (PDF, DOCX, TXT), extracts every token and structured fields, computes per‑domain ATS scores (AI ML, Data Science, Software Developer, Backend Developer, etc.), and generates actionable, truthful suggestions to improve scores. Optional Gemini API integration for semantic matching and rewrite suggestions; mock mode for offline use.

Goals and Success Metrics

Primary goals: Accurate per‑domain scoring; actionable suggestions; preserve user privacy.

Success metrics:

Extraction accuracy ≥ 95% on clean PDFs and DOCX.

Keyword detection precision ≥ 90%.

Suggestion acceptance ≥ 30% in pilot.

Latency: analysis under 10 seconds for a 2‑page resume locally without Gemini.

Scope

In scope: Local resume ingestion; token and entity extraction; configurable domain ontologies; per‑domain scoring with subscore breakdowns; suggestion generation; Streamlit local UI; Gemini optional for embeddings and rewrites; mock mode.

Out of scope: Cloud deployment, multiuser SaaS features, automated job applications, resume writing service that fabricates experience.

Core Features

Ingestion: PDF DOCX TXT upload with optional OCR fallback.

Extraction: Full token extraction; entities: name, email, phone, education, companies, dates, durations, projects.

Scoring: Per‑domain score 0–100 with sub‑scores: Keyword Match, Contextual Relevance, Experience Signal, Education and Certifications, Format and Readability.

Suggestions: Exact keywords to add with placement guidance; 1–3 rewrite options per bullet that preserve truth; formatting and structural fixes.

Customization: Editable JSON ontologies per domain and configurable scoring weights.

Privacy: Local storage by default; delete endpoint and clear instructions to purge uploads.

Developer ergonomics: Gemini mock mode, local cache for embeddings, unit and integration tests.

User Flows

Analyze resume: Upload → extract → score per domain → view matched keywords and highlights → review suggestions → accept or copy edits → delete file.

Tailor to job: Paste job description → compute tailored score and targeted suggestions.

Offline dev: Toggle Gemini mock mode to develop without API calls.

Technical Summary and Roadmap
Tech stack: FastAPI backend, Streamlit UI, pdfplumber/PyMuPDF, python-docx, pytesseract optional, spaCy, rapidfuzz, SQLite cache, Gemini API optional.

MVP Milestone 1 Week 1–2: Extraction, simple keyword scoring, Streamlit UI, sample ontologies, unit tests.

Milestone 2 Week 2–4: Gemini integration for embeddings and rewrites, contextual scoring, suggestion generator.

Milestone 3 Week 4–6: Improve OCR and multi‑column parsing, job description tailoring, tuning, user testing, finalize docs.