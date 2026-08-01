import os
from pathlib import Path

# Load .env if present
env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    PROJECT_NAME: str = "Resume ATS Reader"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MOCK: bool = os.getenv("GEMINI_MOCK", "true").lower() in ("true", "1", "yes")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    ONTOLOGIES_DIR: Path = DATA_DIR / "ontologies"
    SAMPLE_RESUMES_DIR: Path = DATA_DIR / "sample_resumes"
    JOB_DESCRIPTIONS_DIR: Path = DATA_DIR / "job_descriptions"
    
    DB_PATH: Path = DATA_DIR / "app.db"
    
    ENABLE_OCR: bool = os.getenv("ENABLE_OCR", "false").lower() in ("true", "1", "yes")
    
    def __init__(self):
        self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self.ONTOLOGIES_DIR.mkdir(parents=True, exist_ok=True)
        self.SAMPLE_RESUMES_DIR.mkdir(parents=True, exist_ok=True)
        self.JOB_DESCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
