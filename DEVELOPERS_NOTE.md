# Developer's Note: Resume Scanner & ATS Predictor

Thank you for exploring the **Resume Scanner & ATS Predictor** project. This document outlines the technical stack, architecture, algorithms, and engineering decisions behind the application, followed by a note from the developer.

---

## Technical Stack & Architecture

### 1. Frontend & User Interface Layer
- **Framework**: Streamlit (v1.25+)
- **Styling & Design System**: Custom Vanilla CSS (`web/static/css/style.css`) with glassmorphic cards, custom progress bars, and SVG donut charts.
- **Theme Engine**: Session state runtime toggle supporting both **Light Mode** (default) and **Dark Mode** with high-contrast color variables.
- **Responsive Layout**: Fluid CSS media queries (`@media max-width: 768px`) for mobile viewports, single-column card stacking, touch-optimized spacing, and scrollbar clipping.

### 2. Backend & API Services
- **REST Framework**: FastAPI (v0.100+) & Pydantic (v2.0+)
- **Server**: Uvicorn (v0.22+) ASGI Server
- **Routing**: Clean modular API routes (`/upload`, `/evaluate`, `/ontologies`) with CORS middleware integration.

### 3. Document Parsing & Extraction Pipeline
- **PDF Extraction**: `pdfplumber` (layout and text positioning) with `pypdf` fast fallback parser.
- **DOCX Extraction**: `python-docx` for structured XML paragraph and bullet parsing.
- **TXT Extraction**: UTF-8/Latin-1 fallback reader.

### 4. Natural Language Processing (NLP)
- **Tokenization & Lemmatization**: Regex-based NLP engine with specialized token boundary rules to preserve technical symbols (e.g., `C++`, `.NET`, `Node.js`, `CI/CD`).
- **Entity Extraction**: Regex pattern matchers for candidate Name, Email, Phone Number, Degrees (B.Tech, B.S., M.S., Ph.D.), Employment Durations, and Years of Experience.
- **Text Preview Highlighting**: Single-occurrence highlighting algorithm (`replace(kw, ..., 1)`) ensuring technical terms are visually highlighted exactly once in the candidate text box.

### 5. ATS Fit Scoring Engine
- **4-Factor Weighted Formula**:
  - **Keyword Match (50% Weightage)**: Max 50.0 points.
  - **Experience Signal (25% Weightage)**: Max 25.0 points.
  - **Education & Certifications (15% Weightage)**: Max 15.0 points.
  - **Format & Readability (10% Weightage)**: Max 10.0 points.
- **Strict Marking Table (1 to 35 Words)**: Exact lookup dictionary (`KEYWORD_SCORE_TABLE`) mapping matched keyword counts (1 to 35) to percentage marks (`3%` for 1 match, `25%` for 10 matches, `50%` for 20 matches, `67%` for 25 matches, `100%` for 35+ matches).
- **Fuzzy Matching**: `RapidFuzz` string matching (`ratio >= 88`) for typo and variant handling.
- **1-Time Concept Deduplication**: Each technical skill concept is credited exactly once in score calculations to prevent keyword stuffing inflation.

### 6. Domain Ontologies
- **JSON Dictionaries**: Structured ontologies for 3 primary domains (`data/ontologies/`):
  - AI / ML Engineering (`ai_ml.json`)
  - Data Science (`data_science.json`)
  - Software Engineering (`software_dev.json`)

### 7. Deployment & WebAssembly
- **Client-Side Engine**: `stlite` (@stlite/mountable) WebAssembly runtime enabling zero-backend browser execution.
- **Static Builder**: `build_netlify.py` script bundling all application modules and ontologies into `public/index.html`.
- **Netlify Configuration**: `netlify.toml` defining build commands, header security policies, and single-page app rewrite rules.

### 8. Testing & Quality Assurance
- **Framework**: `pytest` (v7.3+) unit and integration test suite covering extractors, NLP tokenizers, ontology loaders, scoring engine, and API routes.

---

## Message from the Developer

Dear User,

Thank you very much for taking the time to use and test the **Resume Scanner & ATS Predictor**. 

This application was designed and engineered to provide a local-first, privacy-focused, and transparent resume evaluation experience without sending candidate data to third-party servers.

Please note that this is the **initial release version (v1.0)** of the application. While extensive care has been taken to test parsing, scoring, and UI responsiveness, you may occasionally encounter edge-case formatting variations with non-standard resume layouts, complex PDF structures, or unique font encodings. 

I sincerely apologize for any minor bugs, glitches, or unexpected errors you might experience while using this initial build. Your feedback, error reports, and feature suggestions are invaluable in helping refine the scoring algorithms, expand domain ontologies, and improve the user experience in upcoming versions.

Thank you again for your support and for using the software!

Warm regards,  
*The Development Team*
