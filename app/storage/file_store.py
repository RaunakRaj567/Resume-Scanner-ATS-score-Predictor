import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

class FileStore:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.DB_PATH
        self.uploads_dir = settings.UPLOADS_DIR
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize SQLite tables for resumes, embeddings, and rewrite caches."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_records (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    extracted_text TEXT NOT NULL,
                    sections TEXT NOT NULL,
                    entities TEXT NOT NULL,
                    tokens TEXT NOT NULL,
                    sentences TEXT NOT NULL,
                    domain_scores TEXT,
                    suggestions TEXT,
                    embeddings_cached INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings_cache (
                    id TEXT PRIMARY KEY,
                    resume_id TEXT NOT NULL,
                    sentence_hash TEXT NOT NULL,
                    vector TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rewrite_cache (
                    id TEXT PRIMARY KEY,
                    bullet_hash TEXT NOT NULL,
                    target_domain TEXT NOT NULL,
                    rewrites TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_upload_file(self, resume_id: str, filename: str, file_content: bytes) -> Path:
        """Save file bytes to disk under data/uploads/<resume_id>/<filename>."""
        target_dir = self.uploads_dir / resume_id
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        logger.info(f"Saved uploaded file for resume {resume_id} to {file_path}")
        return file_path

    def save_resume_record(self, record: Dict[str, Any]) -> None:
        """Insert or update a ResumeRecord in SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO resume_records (
                    id, filename, extracted_text, sections, entities, tokens, sentences,
                    domain_scores, suggestions, embeddings_cached, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record["id"],
                record["filename"],
                record["extracted_text"],
                json.dumps(record.get("sections", {})),
                json.dumps(record.get("entities", {})),
                json.dumps(record.get("tokens", [])),
                json.dumps(record.get("sentences", [])),
                json.dumps(record.get("domain_scores", {})) if record.get("domain_scores") else None,
                json.dumps(record.get("suggestions", [])) if record.get("suggestions") else None,
                1 if record.get("embeddings_cached") else 0,
                record.get("created_at", datetime.utcnow().isoformat() + "Z")
            ))
            conn.commit()

    def get_resume_record(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Fetch ResumeRecord from SQLite by resume_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resume_records WHERE id = ?", (resume_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "filename": row["filename"],
                "extracted_text": row["extracted_text"],
                "sections": json.loads(row["sections"]),
                "entities": json.loads(row["entities"]),
                "tokens": json.loads(row["tokens"]),
                "sentences": json.loads(row["sentences"]),
                "domain_scores": json.loads(row["domain_scores"]) if row["domain_scores"] else {},
                "suggestions": json.loads(row["suggestions"]) if row["suggestions"] else [],
                "embeddings_cached": bool(row["embeddings_cached"]),
                "created_at": row["created_at"]
            }

    def delete_resume_record(self, resume_id: str) -> bool:
        """Delete uploaded file and all cached records for resume_id."""
        # Delete directory
        target_dir = self.uploads_dir / resume_id
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
            
        # Delete from DB
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resume_records WHERE id = ?", (resume_id,))
            cursor.execute("DELETE FROM embeddings_cache WHERE resume_id = ?", (resume_id,))
            conn.commit()
        logger.info(f"Deleted resume record and file artifacts for resume_id: {resume_id}")
        return True

    def get_embedding_vector(self, sentence_hash: str) -> Optional[List[float]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT vector FROM embeddings_cache WHERE sentence_hash = ?", (sentence_hash,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["vector"])
        return None

    def save_embedding_vector(self, entry_id: str, resume_id: str, sentence_hash: str, vector: List[float]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO embeddings_cache (id, resume_id, sentence_hash, vector, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (entry_id, resume_id, sentence_hash, json.dumps(vector), datetime.utcnow().isoformat() + "Z"))
            conn.commit()

file_store = FileStore()
