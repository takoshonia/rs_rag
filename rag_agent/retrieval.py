import re
import json

from .config import load_config, INDEX_DIR


def _tokenize_georgian(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    tokens = re.findall(r"[\u10A0-\u10FFa-zA-Z0-9]+", text)
    return [t for t in tokens if len(t) > 1]


def extract_keywords(query: str, max_terms: int = 5) -> list[str]:
    tokens = _tokenize_georgian(query)
    keywords = [t for t in tokens if len(t) >= 2 or t.isdigit()]
    return keywords[:max_terms]


class Retriever:
    def __init__(self, use_semantic: bool = True):
        self.config = load_config()
        self.use_semantic = use_semantic
        self._bm25 = None
        self._docs = None
        self._embeddings = None
        self._embed_model = None

    def _ensure_index(self):
        if self._docs is not None:
            return
        index_path = INDEX_DIR / "chunks.json"
        if not index_path.exists():
            self._docs = []
            self._bm25 = None
            self._embeddings = None
            return
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._docs = data.get("chunks", [])
        if not self._docs:
            return
        from rank_bm25 import BM25Okapi
        tokenized = [_tokenize_georgian(d.get("text", "")) for d in self._docs]
        self._bm25 = BM25Okapi(tokenized)
        if self.use_semantic and (INDEX_DIR / "embeddings.npy").exists():
            import numpy as np
            self._embeddings = np.load(INDEX_DIR / "embeddings.npy")

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        doc_type: str | None = None,
    ) -> list[dict]:
        self._ensure_index()
        top_k = top_k or self.config["retrieval"]["top_k"]
        if not self._docs:
            return []

        candidates = self._docs
        if doc_type:
            candidates = [d for d in self._docs if d.get("doc_type") == doc_type]
            if not candidates:
                candidates = self._docs

        q_tokens = _tokenize_georgian(query)
        if not q_tokens:
            return candidates[:top_k]

        cand_texts = [c.get("text", "") for c in candidates]
        cand_tok = [_tokenize_georgian(t) for t in cand_texts]
        from rank_bm25 import BM25Okapi
        bm25 = BM25Okapi(cand_tok)
        bm25_scores = bm25.get_scores(q_tokens)

        import numpy as np
        if bm25_scores.size > 0 and bm25_scores.max() > 0:
            bm25_norm = bm25_scores / (bm25_scores.max() + 1e-9)
        else:
            bm25_norm = np.zeros(len(candidates))

        if self._embeddings is not None and self.use_semantic:
            cand_indices = [self._docs.index(c) for c in candidates]
            cand_emb = self._embeddings[cand_indices]
            q_emb = self._embed_query(query)
            if q_emb is not None and cand_emb.shape[0] > 0:
                sim = np.dot(cand_emb, q_emb) / (
                    np.linalg.norm(cand_emb, axis=1) * np.linalg.norm(q_emb) + 1e-9
                )
                kw = self.config["retrieval"].get("keyword_weight", 0.6)
                sw = self.config["retrieval"].get("semantic_weight", 0.4)
                combined = kw * bm25_norm + sw * (sim + 1) / 2
            else:
                combined = bm25_norm
        else:
            combined = bm25_norm

        top_idx = np.argsort(combined)[::-1][:top_k]
        min_score = self.config["retrieval"].get("min_score", 0.0)
        out = []
        for i in top_idx:
            if combined[i] >= min_score:
                chunk = dict(candidates[i])
                chunk["score"] = float(combined[i])
                out.append(chunk)
        return out

    def _embed_query(self, query: str):
        if self._embed_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embed_model = SentenceTransformer(
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
            except Exception:
                return None
        try:
            return self._embed_model.encode([query], normalize_embeddings=True)[0]
        except Exception:
            return None


def retrieve(query: str, top_k: int | None = None, doc_type: str | None = None) -> list[dict]:
    r = Retriever(use_semantic=True)
    return r.retrieve(query, top_k=top_k, doc_type=doc_type)
