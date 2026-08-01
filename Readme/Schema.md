Schema
Overview
Purpose: Define canonical data shapes for Resume ATS Reader to ensure consistent API contracts, storage, and tests.
Schema version: 1.0

Data models
ResumeRecord
Field	Type	Required	Example	Notes
id	string (uuid)	yes	a1b2c3d4-...	primary key
filename	string	yes	john_doe.pdf	stored in uploads path
extracted_text	string	yes	"Full extracted resume text..."	raw extractor output
sections	object	yes	{"experience":[...],"skills":[...],"education":[...]}	parsed sections
entities	object	yes	{"email":"x@x.com","phone":"+91...","name":"John Doe"}	NER output
tokens	array[string]	yes	["python","tensorflow","nlp"]	lemmatized tokens
sentences	array[string]	yes	["Built model to..."]	sentence-level units
domain_scores	object	yes	{"ai_ml":82,"data_science":76}	see DomainScore
suggestions	array[Suggestion]	no	[...]	generated edits
embeddings_cached	boolean	no	true	cache flag
created_at	string (ISO8601)	yes	2026-07-30T19:22:00Z	timestamp


DomainScore
Field	Type	Required	Example	Notes
score	number (0–100)	yes	82	aggregated final score
subscores	object	yes	{"keyword":32,"context":21,"experience":12,"education":8,"format":9}	raw subscore values
matched_keywords	array[MatchedKeyword]	yes	see below	per-match detail
confidence	number (0–1)	no	0.92	optional model confidence


MatchedKeyword

Field	Type	Example
kw	string	TensorFlow
type	string enum	exact \	fuzzy \	contextual
location	string	skills \	experience \	project
contribution	number	5


OntologyEntry
Field	Type	Required	Example	Notes
keyword	string	yes	TensorFlow	canonical token
weight	number (0.0–1.0)	yes	0.9	importance for scoring
synonyms	array[string]	no	["tf","tensorflow 2"]	fuzzy mapping
context_examples	array[string]	no	["Built model using TensorFlow"]	optional usage examples


Suggestion
Field	Type	Required	Example	Notes
id	string	yes	s1	suggestion id
bullet_id	string	no	b1	reference to resume bullet
rewrite	string	yes	"Built CNN using TensorFlow..."	suggested text
reason	string	yes	"Adds high-weight keyword"	short explanation
estimated_impact	number	no	4	estimated score delta
applied	boolean	no	false	local session state


EmbeddingCacheEntry
Field	Type	Required	Example	Notes
id	string	yes	e1	uuid
resume_id	string	yes	a1b2...	foreign key
sentence_hash	string	yes	sha256(...)	deterministic key
vector	array[number]	yes	[0.001, -0.23, ...]	embedding vector
created_at	string (ISO8601)	yes	2026-07-30T19:22:00Z	timestamp