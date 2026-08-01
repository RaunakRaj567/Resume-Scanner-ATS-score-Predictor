from app.services.rag_pipeline import rag_pipeline

def test_rag_chunking_and_retrieval():
    extracted_text = """
    Alex Johnson
    alex@example.com | 555-0192

    SUMMARY
    Senior ML Engineer with 4 years building PyTorch and TensorFlow deep learning models.

    EXPERIENCE
    Senior ML Developer | TechCorp | 2021 - Present
    - Architected scalable machine learning microservices in Python and FastAPI.
    - Automated deployment pipelines using Docker and GitHub Actions.

    EDUCATION
    Master of Science in Computer Science | Columbia University

    SKILLS
    Python, PyTorch, TensorFlow, FastAPI, Docker, Git
    """

    sections = {
        "summary": ["Senior ML Engineer with 4 years building PyTorch and TensorFlow deep learning models."],
        "experience": [
            "Senior ML Developer | TechCorp | 2021 - Present",
            "- Architected scalable machine learning microservices in Python and FastAPI.",
            "- Automated deployment pipelines using Docker and GitHub Actions."
        ],
        "education": ["Master of Science in Computer Science | Columbia University"],
        "skills": ["Python, PyTorch, TensorFlow, FastAPI, Docker, Git"]
    }

    record = {
        "extracted_text": extracted_text,
        "sections": sections,
        "entities": {"name": "Alex Johnson", "email": "alex@example.com"}
    }

    # Test chunking
    chunks = rag_pipeline.chunk_resume(extracted_text, sections)
    assert len(chunks) >= 4

    # Test retrieval
    query = "What framework is used for machine learning models?"
    top_chunks = rag_pipeline.retrieve_relevant_chunks(chunks, query, top_k=2)
    assert len(top_chunks) == 2
    assert "score" in top_chunks[0]

    # Test Q&A
    rag_res = rag_pipeline.answer_query(record, query)
    assert "answer" in rag_res
    assert len(rag_res["retrieved_chunks"]) > 0
