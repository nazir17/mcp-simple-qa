from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from typing import List, Dict, Tuple


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """
    Chunk text by characters (approx). chunk_size and overlap are character counts.
    Returns list of chunks.
    """
    text = text.replace("\r\n", " ")
    n = len(text)
    chunks = []
    start = 0
    while start < n:
        end = start + chunk_size
        chunk = text[start:end]
        if end < n:
            window = text[end:end+100]
            sep_pos = None
            for sep in ['\n\n', '\n', '. ', '? ', '! ']:
                p = window.find(sep)
                if p != -1:
                    sep_pos = p
                    break
            if sep_pos is not None:
                end = end + sep_pos + len(sep)
                chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if c]

class QAIndex:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", embedding_dim: int = 384):
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = embedding_dim
        self.index = None
        self.id_to_meta: Dict[int, Dict] = {}
        self.next_id = 0

    def _ensure_index(self):
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

    def add_document(self, text: str, doc_id: str = None):
        """
        Splits text, computes embeddings and adds to FAISS index.
        doc_id: optional string to identify the document.
        """
        chunks = chunk_text(text, chunk_size=1200, overlap=250)
        if not chunks:
            return 0

        embeddings = self.model.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        embeddings = embeddings / norms

        self._ensure_index()

        self.index.add(embeddings.astype('float32'))
        count = embeddings.shape[0]
        for i in range(count):
            idx = self.next_id
            self.id_to_meta[idx] = {
                "doc_id": doc_id or "doc",
                "chunk_text": chunks[i],
                "chunk_len": len(chunks[i])
            }
            self.next_id += 1
        return count

    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict]]:
        """
        Returns list of (score, meta) for top_k.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        q_emb = self.model.encode([query], convert_to_numpy=True)
        q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-10)
        q_emb = q_emb.astype('float32')
        D, I = self.index.search(q_emb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            meta = self.id_to_meta.get(int(idx), {})
            results.append((float(score), meta))
        return results

    def stats(self):
        return {
            "n_vectors": 0 if self.index is None else int(self.index.ntotal),
            "n_documents": len({m["doc_id"] for m in self.id_to_meta.values()}) if self.id_to_meta else 0
        }
