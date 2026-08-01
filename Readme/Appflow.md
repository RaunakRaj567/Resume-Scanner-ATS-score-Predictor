AppFlow
Purpose
Describe the end‑to‑end runtime flow for the Resume ATS Reader: how user actions map to backend processing, data artifacts produced, Gemini interactions, caching, and error handling.

Primary flows overview
Analyze Resume — Upload file → Extract → NLP → Score → Suggestions → UI display.

Request Suggestions — Select bullets → Generate rewrites via Gemini → Present edits.

Tailor to Job — Paste job description → Build domain vector → Recompute scores and suggestions.

Delete Resume — Remove file and cached artifacts.

Upload and Extraction Flow
User action: Upload file via Streamlit UI or POST /upload.

API: POST /upload returns resume_id and stores file in data/uploads/<resume_id>.

Extractor (extractor.py):

Detect file type (PDF/DOCX/TXT).

If PDF and textless, optionally run OCR (Tesseract).

Extract raw text, preserve bullets, headings, and simple layout.

Produce extracted_text, sections (summary, experience, education, skills), and raw_tokens.

Persist: Save extraction result to SQLite cache and filesystem: ResumeRecord(extracted_text, sections, tokens).

Return: API responds with resume_id and extraction summary.

Tokenization and NLP Flow
Trigger: After extraction, call NLP service (nlp.py).

Operations:

Tokenize and lemmatize (spaCy).

Extract entities: name, email, phone, dates, durations, degrees, company names.

Split into sentences and bullets for contextual scoring.

Output: tokens, lemmas, entities, sentences. Store in cache.

Ontology Loading and Domain Preparation
Load: ontology.py loads JSON files from data/ontologies/.

Prepare: Build per‑domain keyword maps, weights, synonyms, and precompute domain TF‑IDF vectors from data/job_descriptions/ if available.

Cache: Keep in memory for scoring requests.

Scoring Flow
Request: UI calls GET /score/{resume_id}.

Keyword Match: Match tokens against ontology using exact and fuzzy matching (rapidfuzz). Compute keyword subscore.

Contextual Relevance:

If Gemini enabled: batch sentences, call Gemini embeddings, compute cosine similarity to domain vectors.

If Gemini mock or disabled: use TF‑IDF sentence vectors.

Experience Signal: Extract years and seniority keywords; map to normalized score.

Education and Format: Check degrees, certs, headings, bullets, contact info.

Aggregate: Combine subscores using configured weights into final 0–100 per domain.

Explainability: Produce matched keyword list with location, match type, and subscore contribution.

Return: JSON with domain_scores, subscores, matched_keywords, and highlights.

Suggestion Generation Flow
User action: Select a bullet or request suggestions for a domain.

API: POST /suggest/{resume_id} with bullet_ids and target_domain.

Local precheck: Identify missing high‑weight keywords for the domain and prepare prompt context (original bullet, target keywords, constraints).

Gemini interaction:

Mock mode: return deterministic template rewrites.

Real mode: call Gemini to generate 1–3 rewrites and short explanations.

Postprocess: Validate rewrites (length, no fabrication), score each rewrite for keyword inclusion and readability.

Return: Suggestions with rewrite_text, reason, and estimated_score_impact.

Tailor to Job Flow
User action: Paste job description and request tailoring.

API: POST /tailor builds a job vector (Gemini embeddings or TF‑IDF).

Compute: Recompute contextual relevance and final scores using job vector as domain reference.

Suggest: Provide prioritized keyword additions and rewrites tailored to the job description.

Return: Tailored domain_scores and suggestions.

Caching and Rate Control
Embeddings cache: Store sentence embeddings keyed by resume_id + sentence hash in SQLite.

Rewrite cache: Cache generated rewrites for identical bullet + keyword sets.

Batching: Batch sentences for Gemini embedding calls to reduce API calls.

Rate control: Limit concurrent Gemini calls; queue requests if necessary.

Error Handling and Retries
Extraction errors: Return extraction status with error field; provide fallback to plain text extraction.

OCR failures: Notify user to reupload a higher quality scan.

Gemini failures: Fall back to TF‑IDF similarity and mock rewrite templates; return a clear gemini_status flag.

Timeouts: If scoring exceeds threshold, return partial results with partial=true and continue background processing.

Delete safety: DELETE /upload/{resume_id} removes file and all cached artifacts; return confirmation.

Background and Long Running Tasks
Synchronous: Extraction and basic scoring for small resumes.

Asynchronous: Large OCR, full embedding generation, and batch rewrite jobs run in a simple in‑process queue or worker thread for local mode. UI polls job status endpoint.

Data Artifacts
On disk: data/uploads/<resume_id>/<file>; data/sample_resumes/ for tests.

SQLite cache: resume_records, embeddings_cache, rewrite_cache.

In memory: loaded ontologies and domain vectors.

Observability
Logs: Extraction steps, NLP warnings, Gemini call outcomes (success/fail), and cache hits. Mask PII in logs.

Metrics: Extraction time, scoring time, Gemini call count, cache hit rate.

Performance Targets
Local target: Extraction + scoring under 10 seconds for a 2‑page resume without Gemini.

Gemini latency: Dependent on API; mitigate with batching and caching.

Notes for Developers
Keep Gemini calls idempotent and cacheable.

Validate all rewrites to avoid fabricating facts.

Make ontologies editable JSON files so domain updates do not require code changes.