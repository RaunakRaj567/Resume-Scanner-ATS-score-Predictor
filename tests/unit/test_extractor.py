import pytest
from pathlib import Path
from app.services.extractor import ResumeExtractor

def test_extract_txt_file(tmp_path):
    txt_file = tmp_path / "test_resume.txt"
    txt_file.write_text("""
John Doe
Email: john@example.com

SUMMARY
Experienced software engineer.

EXPERIENCE
Senior Developer | Acme Corp | 2021 - Present
- Built REST APIs in Python and FastAPI.

SKILLS
Python, FastAPI, SQL, Docker
""")

    extractor = ResumeExtractor()
    result = extractor.extract_from_file(txt_file)

    assert "John Doe" in result["extracted_text"]
    assert "FastAPI" in result["extracted_text"]
    assert "experience" in result["sections"]
    assert "skills" in result["sections"]
    assert len(result["sections"]["skills"]) >= 1
