Design
A concise design spec for the three UI screens you requested: Upload, Dashboard, and ATS Score Breakdown. This file describes structure, visual language, interactions, microcopy, accessibility considerations, and implementation notes so developers and designers can build a faithful local demo.

Overview
Purpose: Help users upload a resume, see per‑domain ATS scores, inspect matched keywords, and get actionable suggestions to improve fit for specific technical domains (AI/ML, Data Science, Software Developer, Backend Developer).
Primary users: Job seekers and engineers who want quick, explainable feedback on resume ATS fit.
Core goals: fast upload → clear score → actionable suggestions → safe local processing.

Layout and Navigation
Global layout

Three-panel flow (left → center → right on wide screens; stacked vertically on small screens):

Left / Dashboard panel: resume preview, quick summary, domain scores, top suggestions.

Center / Upload panel: drag‑and‑drop area and upload controls.

Right / Breakdown panel: detailed score visualization and matched keywords.

Top navigation

Tabs: Home, Tailor to Job, Settings.

Primary actions: View Details, Export Report (export only local file or copy text; note: export behavior implemented locally).

Responsive behavior

Desktop: three columns visible.

Tablet: two columns (Upload + either Dashboard or Breakdown).

Mobile: stacked screens with quick nav to switch between Dashboard, Upload, Breakdown.

Screens and Components
Upload screen (center)
Hero area: large dashed rectangle with cloud/upload icon and text: “Drag & Drop Your Resume Here or Click to Upload”.

Supported formats: small caption: PDF, DOCX, TXT.

Primary CTA: Upload Resume (prominent, filled button).

Secondary: Upload Sample Resume for demo/testing.

States: empty, dragging (highlight border + subtle shadow), uploading (progress bar), error (inline message with retry).

Dashboard screen (left)
Resume preview: scrollable pane showing parsed sections (Experience, Education, Skills). Highlight matched keywords inline.

ATS Scores by Domain: vertical list with domain name + numeric score and colored progress bar. Color mapping: green ≥75, yellow 60–74, orange 50–59, red <50.

Suggestions to Improve: prioritized list of short, actionable items (keyword to add, section to expand, bullet rewrite hints). Each suggestion shows estimated score impact and a small “Apply / Copy” action.

Quick actions: View Details (open breakdown) and Export Report.

ATS Score Breakdown (right)
Primary visualization: circular/donut chart with final domain score in center.

Subscore list: five rows with label and fraction (e.g., Keyword Match 32 / 40). Each row has a small horizontal bar and a short qualitative tag (Excellent / Strong / Good / Needs work).

Top Keywords Found: list with match type badges (Exact, Contextual, Fuzzy) and location tags (Skills, Experience, Project).

Suggestion panel: contextual rewrites (1–3) for selected bullets with a short reason and estimated impact.

Visual Design & Assets
Color palette

Primary: #1E6FF3 (blue) — CTAs, active states.

Success: #2ECC71 (green) — high scores.

Warning: #F1C40F (yellow) — medium scores.

Alert: #E67E22 (orange) / #E74C3C (red) — low scores / errors.

Background: #FFFFFF and #F6F8FA for panels.

Text: #0B1A2B (primary), #4B5563 (secondary).

Typography

Headings: Sans-serif, medium weight (e.g., Inter / Roboto).

Body: Sans-serif, regular.

Sizes: H1 20–24px, H2 16–18px, body 14px, captions 12px.

Spacing & layout

8px baseline grid; 16–24px gutters between panels.

Cards with 8–12px radius and subtle elevation (box-shadow) for separation.

Icons & imagery

Simple line icons for upload, download, copy, and domain badges.

Use small colored badges for match types and score tags.

Charts use distinct, colorblind‑friendly palette.

Interaction, Microcopy & States
Primary interactions

Upload: drag/drop or click → show progress → parse → show results.

Highlighting: hover keyword in preview to show tooltip with match reason and weight.

Suggestions: Apply inserts suggested rewrite into a local edit buffer; Copy copies text to clipboard.

Tailor to Job: paste JD → recompute contextual relevance and reorder suggestions.

Microcopy examples

Upload hint: “Drag & drop your resume (PDF, DOCX, TXT) — local processing only.”

Suggestion reason: “Add ‘TensorFlow’ to Skills — common keyword in ML job descriptions; increases contextual relevance.”

Error: “Couldn’t extract text. Try a different file or enable OCR in Settings.”

Edge states

No resume uploaded: show friendly empty state with sample resume CTA.

Partial results: show partial=true badge and continue background processing.

Gemini unavailable: show fallback notice and use TF‑IDF fallback.

Accessibility & Performance
Accessibility

Contrast: meet WCAG AA for text and UI elements.

Keyboard: all actions reachable via keyboard (upload via file dialog, navigate suggestions, apply/copy).

Screen reader: semantic HTML roles for upload area, lists, and charts; aria labels for match badges and buttons.

Color independence: do not rely on color alone — include icons/labels for score states.

Performance

Local-first: parsing and keyword matching run locally; Gemini calls optional and cached.

Latency targets: extraction + scoring under 10s for 2‑page resume on typical dev laptop (without Gemini).

Caching: cache embeddings and rewrite results to avoid repeated API calls.

Implementation Notes
Data & config

Ontologies editable as JSON; weights drive suggestion priority.

Keep PII local; provide explicit delete action for uploaded files.

Developer ergonomics

Provide mock Gemini mode for offline development.

Expose feature flags for OCR, Gemini, and advanced scoring.

Deliverables

High‑fidelity mockups for each screen (desktop + mobile).

Component library: UploadCard, ResumePreview, DomainScoreList, DonutChart, SuggestionCard.

Accessibility checklist and microcopy file.