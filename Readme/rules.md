Purpose
Define clear, enforceable rules that constrain the AI to produce reliable, predictable, and non‑overreaching outputs for the Resume ATS Reader project. These rules keep suggestions truthful, avoid fabrication, and preserve the expected quality of results.

Scope
Applies to all AI components that analyze resumes, generate scores, propose rewrites, or produce explanations.

Covers content generation, scoring logic, rewrite suggestions, and external API usage.

Does not replace human review or legal compliance checks.

Core Rules
Truthfulness First

Never invent facts about a candidate. If a claim cannot be verified from the resume or user input, mark it as inferred and show the inference confidence.

No Fabrication of Experience

Suggested rewrites must not add roles, projects, durations, or achievements that are not present in the resume. Rewrites may rephrase and emphasize existing content only.

Conservative Rewriting

Rewrites must preserve factual anchors such as technologies, project names, company names, dates, and metrics. If a keyword is missing, suggest how to truthfully surface related experience instead of inventing it.

Explainability and Traceability

Every score and suggestion must include a short rationale and the evidence source such as a sentence, bullet id, or section name from the resume.

Bounded Creativity

Use creative phrasing only to improve clarity and keyword density. Avoid speculative language, hypothetical achievements, or claims of outcomes not supported by the resume.

Respect Ontology Weights

Scoring and suggestion prioritization must follow configured ontology weights. Do not override weights without explicit configuration changes.

Fallbacks and Limits

If semantic models are unavailable, fall back to deterministic TF IDF and fuzzy matching. Indicate fallback mode in results.

Rate and Cost Awareness

Batch external calls and cache embeddings and rewrites. Do not call external APIs for every minor UI interaction.

Privacy and Locality

Default to local processing. Only call external services when the user explicitly enables them and provides credentials. Log external calls and show status to the user.

Safety and Non Deceptive Output

Do not produce content that could be used to misrepresent a candidate to an employer. Flag any suggestion that materially changes a candidate profile for manual review.

Allowed Examples
Acceptable rewrite

Original bullet: Built image classifier using open source libraries.

Rewrite: Built image classifier using TensorFlow and Keras to improve accuracy.

Rationale: Adds a specific technology that the candidate listed elsewhere in the resume.

Acceptable suggestion

Suggestion: Add a short summary line listing top technologies to increase keyword density.

Rationale: Structural change that does not invent facts.

Disallowed Examples
Not allowed rewrite

Original bullet: Implemented data pipeline.

Rewrite that is forbidden: Led a team of five to build a production data pipeline that processed 1 million events per day.

Reason: Adds team size, production status, and throughput not present in the resume.

Not allowed suggestion

Suggestion: Add certification X even if the candidate has not completed it.

Reason: Encourages fabrication.

Enforcement and Versioning
Validation checks

Automated tests must verify that rewrites do not introduce new named entities or dates unless the user confirms them.

Scoring outputs must include evidence pointers for at least 80 percent of the top contributing items.

Audit logs

Record all generated rewrites, the evidence used, and whether the user applied the suggestion.

Schema and config

Keep ontology weights and rewrite constraints in versioned JSON files. Changes require a changelog entry.

Review cadence

Conduct a quarterly review of suggestion quality using a labeled sample set and update rules if degradation is detected.

Quick operational checklist for AI responses
Did I preserve facts? If no, mark as inferred and lower confidence.

Did I add new entities or dates? If yes, block the change until user confirmation.

Did I cite evidence? If no, include the source sentence or bullet id.

Is the suggestion actionable and minimal? If not, simplify it.