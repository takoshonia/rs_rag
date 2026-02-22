import os
from .config import load_config, get_openai_client, get_citation_text


SYSTEM_PROMPT_KA = """შენ ხარ დამხმარე აგენტი, რომელიც უპასუხებს კითხვებს საგადასახადო და საბაჟო ადმინისტრაციასთან დაკავშირებით.
გამოიყენე მხოლოდ მოწოდებული კონტექსტი (დოკუმენტების ფრაგმენტები).
მნიშვნელოვანი: თუ კონტექსტში ნებისმიერი ინფორმაციაა საბაჟოს, გადასახადის, გადახდის, დეკლარაციის ან ადმინისტრირების შესახებ — აუცილებლად ჩამოაყალიბე პასუხი ამ ინფორმაციის საფუძველზე ქართულად. ნუ დაწერთ "ამ ინფორმაციის მოძიება მოწოდებულ დოკუმენტებში ვერ მოხერხდა" თუ კონტექსტი შეიცავს დაკავშირებულ ტექსტს.
"ვერ მოხერხდა" დაწერე მხოლოდ იმ შემთხვევაში, როდესაც კონტექსტში საერთოდ არ არის არანაირი შესაბამისი ან დაკავშირებული ინფორმაცია.
ყოველთვის უპასუხე ქართულ ენაზე.
პასუხის ბოლოს ყოველთვის დაამატე წყაროს ციტატა ქართულად შემდეგი ფორმატით:
"საინფორმაციო და მეთოდოლოგიური ჰაბზე განთავსებული დოკუმენტების მიხედვით (საგადასახადო და საბაჟო ადმინისტრირებასთან დაკავშირებული დოკუმენტები და ინფორმაცია ერთ სივრცეში)" - https://infohub.rs.ge/ka
"""


def build_messages(query: str, chunks: list[dict]) -> list[dict]:
    if not chunks:
        context = "No relevant documents were retrieved."
    else:
        parts = []
        for i, c in enumerate(chunks, 1):
            title = c.get("title", "Document")
            text = c.get("text", "")
            parts.append(f"[{i}] ({title})\n{text}")
        context = "\n\n".join(parts)
    user = f"""კონტექსტი (დოკუმენტების ფრაგმენტები):
{context}

კითხვა: {query}

პასუხი (ქართულად, ციტატით ბოლოში):"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT_KA},
        {"role": "user", "content": user},
    ]


def generate(query: str, chunks: list[dict]) -> tuple[str, list[dict]]:
    config = load_config()
    gen_cfg = config["generation"]
    client = get_openai_client()
    messages = build_messages(query, chunks)
    if os.environ.get("DEBUG_RAG"):
        ctx = messages[1]["content"]
        print("[DEBUG] Context sent to model (first 1200 chars):", ctx[:1200], "...", sep="\n")
    citation = get_citation_text()
    try:
        resp = client.chat.completions.create(
            model=gen_cfg.get("model", "gpt-4o-mini"),
            messages=messages,
            max_tokens=gen_cfg.get("max_tokens", 1024),
            temperature=gen_cfg.get("temperature", 0.2),
        )
        answer = (resp.choices[0].message.content or "").strip()
        if citation not in answer and "infohub.rs.ge" not in answer:
            answer += f"\n\n{citation}"
        sources = [{"title": c.get("title"), "doc_type": c.get("doc_type"), "score": c.get("score")} for c in chunks]
        return answer, sources
    except Exception as e:
        fallback = f"პასუხის ფორმირება ვერ მოხერხდა: {e}. გთხოვთ სცადოთ ხელახლა ან შეამოწმოთ წყარო ჰაბზე."
        fallback += f"\n\n{citation}"
        return fallback, []
