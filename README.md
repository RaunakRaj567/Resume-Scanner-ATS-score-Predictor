# Resume Scanner & ATS Predictor

Local-first intelligent tool that ingests resumes (PDF, DOCX, TXT), extracts tokens and entities, computes per-domain ATS fit scores (AI/ML, Data Science, Software Engineering), and presents high-contrast interactive analytics.

## Features

- **Multi-Format Extraction**: Parses PDF (`pdfplumber`/`pypdf`), DOCX (`python-docx`), and TXT.
- **NLP & Entity Extraction**: Tokenization, lemmatization, sentence splitting, and entity recognition (Name, Email, Phone, Degrees, Companies, Dates), preserving technical tokens (`C++`, `.NET`, `Node.js`).
- **Configurable Ontologies**: JSON-driven keyword ontologies for AI/ML, Data Science, and Software Engineering.
- **4-Factor ATS Scoring Engine**:
  - Keyword Match (50%) — Strict piecewise marking scheme lookup (1 to 35 words)
  - Experience Signal (25%) — Employment history and seniority titles
  - Education & Certifications (15%) — Degrees and academic qualifications
  - Format & Readability (10%) — Structure, contact info, and bullet formatting
- **Mobile Responsive & High Contrast**: Fluid mobile responsiveness (`@media max-width: 768px`) with Light Mode by default and optional Dark Mode toggle.
- **Netlify WebAssembly Ready**: Includes zero-backend Stlite builder (`build_netlify.py` & `netlify.toml`) for instant static deployment on Netlify.

## Installation & Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Running Locally**:
```bash
python run.py
```
Or start Streamlit directly:
```bash
streamlit run web/streamlit_app.py
```

## Deployment on Netlify

This project is fully configured for 1-click Netlify deployment using Stlite (Streamlit in WebAssembly).

### Option 1: Netlify CLI
```bash
python build_netlify.py
netlify deploy --prod --dir=public
```

### Option 2: Netlify Git Repository (Automatic Deployment)
1. Push your code to GitHub / GitLab / Bitbucket.
2. Log into **[Netlify](https://app.netlify.com)** and click **Add new site > Import an existing project**.
3. Select your repository. Netlify will automatically detect `netlify.toml`:
   - **Build Command**: `python build_netlify.py`
   - **Publish Directory**: `public`
4. Click **Deploy Site**. Your app will be live globally!

## Running Tests

Run the full automated pytest suite:
```bash
pytest
```
