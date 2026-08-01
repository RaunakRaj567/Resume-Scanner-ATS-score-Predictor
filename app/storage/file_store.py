import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import sqlite3
    HAS_SQLITE = True
except (ImportError, ModuleNotFoundError):
    sqlite3 = None
    HAS_SQLITE = False
    logger.warning("sqlite3 module not available in this environment. Falling back to in-memory FileStore.")

class FileStore:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.DB_PATH
        self.uploads_dir = settings.UPLOADS_DIR
        self.mem_records = {}
        self.mem_embeddings = {}
        if HAS_SQLITE:
            try:
                self._init_db()
            except Exception as e:
                logger.warning(f"Failed to initialize SQLite database: {e}. Switching to in-memory store.")
                self.has_sqlite = False
            else:
                self.has_sqlite = True
        else:
            self.has_sqlite = False

    def _get_connection(self):
        if not self.has_sqlite or not sqlite3:
            return None
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize SQLite tables for resumes, embeddings, and rewrite caches."""
        if not self.has_sqlite or not sqlite3:
            return
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
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Saved uploaded file for resume {resume_id} to {file_path}")
        except Exception as e:
            logger.warning(f"Could not save file to disk ({e}). Storing in memory.")
        return file_path

    def save_resume_record(self, record: Dict[str, Any]) -> None:
        """Insert or update a ResumeRecord in SQLite or in-memory fallback."""
        self.mem_records[record["id"]] = record
        if not self.has_sqlite:
            return
        try:
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
        except Exception as e:
            logger.warning(f"Failed to write resume record to SQLite ({e}). Saved in memory.")

    def get_resume_record(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Fetch ResumeRecord from SQLite or memory by resume_id."""
        if resume_id in self.mem_records:
            return self.mem_records[resume_id]
        if not self.has_sqlite:
            return None
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM resume_records WHERE id = ?", (resume_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                rec = {
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
                self.mem_records[resume_id] = rec
                return rec
        except Exception as e:
            logger.warning(f"Failed to fetch record from SQLite ({e}).")
            return self.mem_records.get(resume_id)

    def delete_resume_record(self, resume_id: str) -> bool:
        """Delete uploaded file and all cached records for resume_id."""
        self.mem_records.pop(resume_id, None)
        target_dir = self.uploads_dir / resume_id
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
            
        if self.has_sqlite:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM resume_records WHERE id = ?", (resume_id,))
                    cursor.execute("DELETE FROM embeddings_cache WHERE resume_id = ?", (resume_id,))
                    conn.commit()
            except Exception as e:
                logger.warning(f"Failed to delete record from SQLite ({e}).")
        logger.info(f"Deleted resume record and file artifacts for resume_id: {resume_id}")
        return True

    def get_embedding_vector(self, sentence_hash: str) -> Optional[List[float]]:
        if sentence_hash in self.mem_embeddings:
            return self.mem_embeddings[sentence_hash]
        if not self.has_sqlite:
            return None
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT vector FROM embeddings_cache WHERE sentence_hash = ?", (sentence_hash,))
                row = cursor.fetchone()
                if row:
                    vec = json.loads(row["vector"])
                    self.mem_embeddings[sentence_hash] = vec
                    return vec
        except Exception as e:
            logger.warning(f"Failed to read vector from SQLite ({e}).")
            return self.mem_embeddings.get(sentence_hash)
        return None

    def save_embedding_vector(self, entry_id: str, resume_id: str, sentence_hash: str, vector: List[float]) -> None:
        self.mem_embeddings[sentence_hash] = vector
        if not self.has_sqlite:
            return
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO embeddings_cache (id, resume_id, sentence_hash, vector, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (entry_id, resume_id, sentence_hash, json.dumps(vector), datetime.utcnow().isoformat() + "Z"))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to save vector to SQLite ({e}).")

file_store = FileStore()
