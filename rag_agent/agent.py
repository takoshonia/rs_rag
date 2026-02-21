from .config import load_config
from .retrieval import retrieve, extract_keywords
from .generation import generate


def ask(
    question: str,
    top_k: int | None = None,
    doc_type: str | None = None,
) -> tuple[str, list]:
    config = load_config()
    top_k = top_k or config["retrieval"]["top_k"]
    chunks = retrieve(question, top_k=top_k, doc_type=doc_type)
    answer, sources = generate(question, chunks)
    return answer, sources


def ask_keywords(question: str) -> list[str]:
    return extract_keywords(question)
