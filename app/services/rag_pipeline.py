import numpy as np
from typing import List, Dict, Any
from app.services.gemini_client import gemini_client
from app.utils.logging import get_logger

logger = get_logger(__name__)

class RAGPipeline:
    def __init__(self):
        pass

    def chunk_resume(self, extracted_text: str, sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Split resume text into semantic chunks tagged by section."""
        chunks = []

        # Process structured sections if present
        for sec_name, lines in sections.items():
            if not lines:
                continue
            
            # Combine every 2-3 lines into a chunk
            chunk_text = ""
            for i, line in enumerate(lines):
                chunk_text += line + "\n"
                if (i + 1) % 3 == 0 or i == len(lines) - 1:
                    chunks.append({
                        "section": sec_name,
                        "text": chunk_text.strip()
                    })
                    chunk_text = ""

        # Fallback to paragraph splitting if no structured chunks were created
        if not chunks:
            paragraphs = [p.strip() for p in extracted_text.split("\n\n") if p.strip()]
            for i, p in enumerate(paragraphs):
                chunks.append({
                    "section": "general",
                    "text": p
                })

        return chunks

    def compute_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two 1D embedding vectors."""
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        denom = (np.linalg.norm(arr1) * np.linalg.norm(arr2))
        if denom == 0:
            return 0.0
        return float(np.dot(arr1, arr2) / denom)

    def retrieve_relevant_chunks(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Embed query, compute similarity against resume chunks, and return top-k matches."""
        if not chunks or not query:
            return []

        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = gemini_client.get_sentence_embeddings(chunk_texts)
        query_embedding = gemini_client.get_query_embedding(query)

        scored_chunks = []
        for i, chunk in enumerate(chunks):
            emb = chunk_embeddings[i] if i < len(chunk_embeddings) else gemini_client._mock_embedding(chunk["text"])
            sim = self.compute_cosine_similarity(query_embedding, emb)
            scored_chunks.append({
                "section": chunk["section"],
                "text": chunk["text"],
                "score": round(sim, 4)
            })

        # Sort by similarity score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def answer_query(self, record: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Perform local RAG retrieval and answer user question using context-augmented resume data."""
        extracted_text = record.get("extracted_text", "")
        sections = record.get("sections", {})

        # 1. Chunk and retrieve
        chunks = self.chunk_resume(extracted_text, sections)
        top_chunks = self.retrieve_relevant_chunks(chunks, query, top_k=3)

        # 2. Local grounded answer construction
        if top_chunks:
            answer_text = f"Based on candidate's {top_chunks[0]['section']} section: {top_chunks[0]['text']}"
        else:
            answer_text = "Information not found in candidate resume."

        return {
            "query": query,
            "answer": answer_text,
            "retrieved_chunks": top_chunks,
            "candidate_name": record.get("entities", {}).get("name", "Candidate")
        }

rag_pipeline = RAGPipeline()
