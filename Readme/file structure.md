resume-ats-reader/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   ├── nlp.py
│   │   ├── ontology.py
│   │   ├── scoring.py
│   │   └── gemini_client.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── file_store.py
│   └── utils/
│       ├── __init__.py
│       ├── text_cleaning.py
│       └── logging.py
├── data/
│   ├── ontologies/
│   │   ├── ai_ml.json
│   │   ├── data_science.json
│   │   └── software_dev.json
│   ├── job_descriptions/
│   └── sample_resumes/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── architecture.md
│   ├── scoring.md
│   └── gemini_prompts.md
└── web/
    ├── streamlit_app.py
    └── static/
        └── css/
