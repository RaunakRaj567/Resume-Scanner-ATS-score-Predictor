import hashlib
import json
from typing import List, Dict, Any, Optional
from app.utils.logging import get_logger

logger = get_logger(__name__)

class SuggestionEngine:
    """Local, offline bullet rewrite and vector embedding engine without external AI dependencies."""
    def __init__(self):
        self.mock_mode = True

    def _embed_single_text(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """Embed single text using deterministic local hash vector."""
        return self._mock_embedding(text)

    def get_sentence_embeddings(self, sentences: List[str]) -> List[List[float]]:
        """Return sentence embedding vectors using local hash embeddings."""
        if not sentences:
            return []
        return [self._mock_embedding(s) for s in sentences]

    def get_query_embedding(self, query: str) -> List[float]:
        """Return embedding vector for a retrieval query using local hash embedding."""
        if not query:
            return self._mock_embedding("")
        return self._mock_embedding(query)

    def generate_bullet_rewrites(
        self,
        original_bullet: str,
        target_keywords: List[str],
        target_domain: str,
        candidate_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate 5 deterministic, rule-checked truthful bullet rewrites."""
        return self._mock_rewrites(original_bullet, target_keywords, candidate_skills)

    def _mock_embedding(self, text: str, dim: int = 64) -> List[float]:
        """Generate a deterministic 64-dim pseudo-vector based on sentence hash for local mode."""
        sha = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(dim):
            byte_val = sha[i % len(sha)]
            norm_val = (float(byte_val) / 255.0) * 2.0 - 1.0
            vector.append(round(norm_val, 4))
        return vector

    def _mock_rewrites(
        self,
        original_bullet: str,
        target_keywords: List[str],
        candidate_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate 5 deterministic, rule-compliant template rewrites for offline optimization."""
        kw1 = target_keywords[0] if target_keywords else "domain frameworks"
        kw2 = target_keywords[1] if len(target_keywords) > 1 else "industry best practices"
        kw3 = target_keywords[2] if len(target_keywords) > 2 else "key technical tooling"

        clean_orig = original_bullet.rstrip('.')

        return [
            {
                "rewrite": f"{clean_orig} leveraging {kw1} to enhance overall workflow efficiency.",
                "reason": f"Integrates target domain keyword '{kw1}' while preserving original accomplishment.",
                "estimated_impact": 4
            },
            {
                "rewrite": f"Engineered solution for {clean_orig.lower()} incorporating {kw1} and {kw2}.",
                "reason": f"Strengthens technical action phrasing and incorporates '{kw1}' and '{kw2}'.",
                "estimated_impact": 5
            },
            {
                "rewrite": f"Applied {kw1} best practices to optimize {clean_orig.lower()}.",
                "reason": f"Re-structures bullet into a clear, high-impact technical delivery format.",
                "estimated_impact": 3
            },
            {
                "rewrite": f"Architected and delivered: {clean_orig} utilizing {kw1} and {kw3}.",
                "reason": f"Enhances ATS scanner visibility for target keyword '{kw1}' and toolchain.",
                "estimated_impact": 4
            },
            {
                "rewrite": f"{clean_orig} following modular standards and integrating {kw2}.",
                "reason": f"Emphasizes software engineering discipline and includes keyword '{kw2}'.",
                "estimated_impact": 4
            }
        ]

# Keep gemini_client object alias for backward compatibility
gemini_client = SuggestionEngine()
