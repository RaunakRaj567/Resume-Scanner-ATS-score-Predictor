from app.services.nlp import nlp_service

def test_nlp_tokenization_and_entities():
    sample_text = """
    Jane Smith
    Email: jane.smith@tech.org | Phone: +1-555-987-6543
    
    EXPERIENCE
    Lead Engineer with 5 years experience in Python, C++, Node.js, and PyTorch.
    Earned Bachelor of Science in Computer Science in 2019.
    """

    res = nlp_service.process_text(sample_text)

    assert "jane.smith@tech.org" in res["entities"]["email"]
    assert "+1-555-987-6543" in res["entities"]["phone"]
    assert len(res["sentences"]) >= 1
    
    # Check tech tokens preservation
    tokens_lower = [t.lower() for t in res["tokens"]]
    assert "python" in tokens_lower
    assert "c++" in tokens_lower or "c++" in sample_text.lower()
