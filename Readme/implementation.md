Sprint Tasks and Priorities
Phase 1 MVP Tasks (highest priority)
Task 1: Implement upload endpoint and local file store.
Owner: Backend; Notes: validate file types; store under data/uploads/<id>.

Task 2: Build extractor for PDF/DOCX/TXT using pdfplumber/PyMuPDF and python-docx.
Owner: Backend; Notes: preserve bullets/headings.

Task 3: Implement basic NLP pipeline with spaCy for tokens, sentences, and NER.
Owner: NLP; Notes: preserve tech tokens like C++.

Task 4: Create simple ontology loader and keyword matcher using rapidfuzz.
Owner: Backend; Notes: JSON files in data/ontologies.

Task 5: Streamlit demo UI for upload, preview, and per-domain scores.
Owner: Frontend; Notes: highlight matched keywords.

Task 6: Unit tests for extractor, tokenizer, and scoring math.
Owner: QA; Notes: include fixtures.

Phase 2 Tasks
Task 1: Implement Gemini client with mock mode and batching.

Task 2: Add embeddings cache (SQLite) and TF‑IDF fallback.

Task 3: Integrate contextual relevance into scoring engine.

Task 4: Add endpoint for suggestion generation (mock first).

Phase 3 Tasks
Task 1: Improve rewrite prompts and postprocessing to enforce rules.md constraints.

Task 2: Add evidence pointers to every suggestion and score contribution.

Task 3: Implement apply/copy/undo flows in UI.

Task 4: Accessibility and keyboard navigation fixes.

Phase 4 Tasks
Task 1: Integrate pytesseract OCR fallback and tune for multi-column layouts.

Task 2: Add extractor heuristics for dates, durations, and seniority.

Task 3: Performance profiling and optimization to meet latency targets.

Phase 5 Tasks
Task 1: End-to-end integration tests and CI pipeline.

Task 2: Run pilot user tests and collect metrics.

Task 3: Finalize docs and privacy checklist.

Phase 6 Tasks
Task 1: Add CLI batch mode and sample dataset.

Task 2: Final cleanup, version bump, and handoff package.

Dependencies and Risks
Key dependencies

Gemini API for embeddings and rewrites (optional; mock mode required).

OCR engine (Tesseract) for scanned PDFs.

spaCy models for NER and tokenization.

Risks and mitigations

Risk: External API outages. Mitigation: Mock mode and TF‑IDF fallback.

Risk: Fabricated rewrites. Mitigation: Enforce rules.md; automated tests to detect new entities/dates.

Risk: Poor OCR quality. Mitigation: Surface quality warnings and require reupload or manual correction.