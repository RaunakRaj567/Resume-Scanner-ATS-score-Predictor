from app.services.ontology import ontology_loader

def test_ontology_loader():
    domains = ontology_loader.list_available_domains()
    assert "ai_ml" in domains
    assert "software_dev" in domains

    ai_ml_entries = ontology_loader.get_domain_ontology("ai_ml")
    assert len(ai_ml_entries) > 0
    
    keywords = [e["keyword"] for e in ai_ml_entries]
    assert "TensorFlow" in keywords or "PyTorch" in keywords
