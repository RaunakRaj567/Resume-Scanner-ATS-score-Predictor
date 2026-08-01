from app.services.scoring import scoring_engine, PurePythonFuzz

def test_pure_python_fuzz_fallback():
    assert PurePythonFuzz.ratio("python", "pythn") > 88
    assert PurePythonFuzz.ratio("", "") == 100.0
    assert PurePythonFuzz.ratio("python", "") == 0.0

def test_scoring_math():
    extracted_text = """
    Alex Johnson
    alex@example.com | 555-1234
    
    EXPERIENCE
    Senior ML Engineer with 4 years building PyTorch and TensorFlow deep learning models.
    
    EDUCATION
    Master of Science in Computer Science
    
    SKILLS
    Python, PyTorch, TensorFlow, Machine Learning, Deep Learning, Scikit-Learn
    """

    sections = {
        "experience": ["Senior ML Engineer with 4 years building PyTorch and TensorFlow deep learning models."],
        "education": ["Master of Science in Computer Science"],
        "skills": ["Python, PyTorch, TensorFlow, Machine Learning, Deep Learning, Scikit-Learn"],
        "projects": ["Built PyTorch deep learning classifier deployed on AWS."]
    }
    tokens = ["python", "pytorch", "tensorflow", "machine learning", "deep learning", "scikit-learn"]
    sentences = ["Senior ML Engineer with 4 years building PyTorch and TensorFlow deep learning models."]
    entities = {"email": "alex@example.com", "degrees": ["Master of Science"], "durations_found": [("4",)]}

    res = scoring_engine.evaluate_resume(extracted_text, sections, tokens, sentences, entities)
    assert "ai_ml" in res
    score_data = res["ai_ml"]

    assert 0 <= score_data["score"] <= 100
    assert score_data["score"] >= 45
    assert "subscores" in score_data
    assert "keyword" in score_data["subscores"]
    assert "experience" in score_data["subscores"]
    assert "matched_keywords" in score_data
    assert len(score_data["matched_keywords"]) >= 3
