import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_upload_score_suggest_delete_flow():
    resume_content = """
    Jane Candidate
    jane@test.org | 555-000-1111
    
    EXPERIENCE
    Backend Software Engineer | Cloud Inc | 2021-Present
    - Built REST APIs in Python using FastAPI, Docker, and PostgreSQL.
    - Optimized SQL query performance and implemented Redis cache.
    
    EDUCATION
    BS in Computer Science
    
    SKILLS
    Python, FastAPI, Docker, PostgreSQL, Redis, REST API, Git
    """

    # 1. Upload
    file_bytes = resume_content.encode("utf-8")
    upload_res = client.post(
        "/upload",
        files={"file": ("jane_resume.txt", io.BytesIO(file_bytes), "text/plain")}
    )
    assert upload_res.status_code == 200
    data = upload_res.json()
    resume_id = data["resume_id"]
    assert resume_id is not None

    # 2. Get Score
    score_res = client.get(f"/score/{resume_id}")
    assert score_res.status_code == 200
    score_data = score_res.json()
    assert "software_dev" in score_data["domain_scores"]
    software_score = score_data["domain_scores"]["software_dev"]["score"]
    assert software_score >= 25

    # 3. Suggest Rewrites
    suggest_res = client.post(
        f"/suggest/{resume_id}",
        json={"target_domain": "software_dev", "custom_bullet": "Built REST APIs in Python using FastAPI."}
    )
    assert suggest_res.status_code == 200
    suggestions = suggest_res.json()["suggestions"]
    assert len(suggestions) >= 1

    # 4. Tailor to Job
    tailor_res = client.post(
        f"/tailor/{resume_id}",
        json={"job_description": "Looking for Backend Engineer proficient in Python, FastAPI, Docker, and Kubernetes."}
    )
    assert tailor_res.status_code == 200
    assert "tailored_score" in tailor_res.json()

    # 5. Delete
    delete_res = client.delete(f"/upload/{resume_id}")
    assert delete_res.status_code == 200
