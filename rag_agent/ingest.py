import json
import re
from pathlib import Path

from .config import load_config, DATA_DIR, INDEX_DIR


def _tokenize_georgian(text: str) -> list[str]:
    tokens = re.findall(r"[\u10A0-\u10FFa-zA-Z0-9]+", text or "")
    return [t for t in tokens if len(t) > 1]


def chunk_text(text: str, size: int = 512, overlap: int = 64, by: str = "sentence") -> list[str]:
    if by == "sentence":
        sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
        sentences = [s.strip() for s in sentences if s.strip()]
        chunks = []
        current = []
        length = 0
        for s in sentences:
            current.append(s)
            length += len(s) + 1
            if length >= size:
                chunks.append(" ".join(current))
                overlap_len = 0
                keep = []
                for x in reversed(current):
                    overlap_len += len(x) + 1
                    keep.insert(0, x)
                    if overlap_len >= overlap:
                        break
                current = keep
                length = sum(len(x) + 1 for x in current)
        if current:
            chunks.append(" ".join(current))
        return chunks
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i : i + size])
    return [c for c in chunks if c.strip()]


def ingest_document(path: Path, doc_type: str | None = None) -> list[dict]:
    title = path.stem
    suffix = path.suffix.lower()
    text = ""
    if suffix == ".txt":
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            for p in reader.pages:
                text += (p.extract_text() or "") + "\n"
        except Exception:
            return []
    else:
        return []
    if not text.strip():
        return []
    cfg = load_config()
    ch_cfg = cfg.get("chunking", {})
    size = ch_cfg.get("size", 512)
    overlap = ch_cfg.get("overlap", 64)
    by = ch_cfg.get("by", "sentence")
    raw_chunks = chunk_text(text, size=size, overlap=overlap, by=by)
    return [
        {"title": title, "text": c, "doc_type": doc_type or "unknown", "source": str(path)}
        for c in raw_chunks
    ]


def run_ingest():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    all_chunks = []
    for path in sorted(DATA_DIR.rglob("*")):
        if path.suffix.lower() in (".txt", ".pdf"):
            doc_type = path.parent.name if path.parent != DATA_DIR else None
            all_chunks.extend(ingest_document(path, doc_type=doc_type))
    index_path = INDEX_DIR / "chunks.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"chunks": all_chunks}, f, ensure_ascii=False, indent=0)
    print(f"Indexed {len(all_chunks)} chunks from {index_path}")

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        texts = [c["text"] for c in all_chunks]
        embs = model.encode(texts, normalize_embeddings=True)
        np.save(INDEX_DIR / "embeddings.npy", embs)
        print("Saved embeddings to index/embeddings.npy")
    except Exception as e:
        print("Embeddings skipped:", e)


if __name__ == "__main__":
    run_ingest()
