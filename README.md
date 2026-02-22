---
title: RAG RS — საგადასახადო და საბაჟო ინფორმაცია
emoji: 📄
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
---

# RAG RS

მცირე RAG-აპლიკაცია საგადასახადო და საბაჟო კითხვებისთვის — პასუხობს ქართულად და ეყრდნობა მხოლოდ იმ დოკუმენტებს, რაც `data/`-ში გაქვს. ყოველ პასუხში ბოლოში ერთვის წყაროს ციტატა და ბმული [infohub.rs.ge](https://infohub.rs.ge/ka)-ზე.

**როგორ არის გაკეთებული**

ინფოჰაბს საჯარო API არ აქვს, ამიტომ ყველაფერი ლოკალურ ინდექსზე მუშაობს — დოკუმენტებს ვაგროვებ `data/`-ში, შემდეგ `python -m rag_agent.ingest` ჭრის ტექსტს ფრაგმენტებად (წინადადება/პარაგრაფი, გადაფარვით) და ინახავს `index/chunks.json`-ში; sentence-transformers-ის არსებობის შემთხვევაში ვექტორებსაც — `index/embeddings.npy`-ში. ძიება ჰიბრიდულია: BM25 + embeddings. ტოპ-კ ჩანკები გადაეცემა Gemini-ს (OpenAI-თან შესათავსებელი API), პრომპტი კი ითხოვს პასუხს მხოლოდ მოწოდებული კონტექსტიდან, ქართულად, ბოლოში ციტატით. ციტატის ტექსტი და ბმული `config.yaml`-შია.

**საჭიროა:** Python 3.10+, Gemini API key.

---

**დაყენება**

1. პროექტის საქაღალდიდან:

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. ფესვში შექმენით `.env` (შეგიძლიათ `.env.example`-იდან დააკოპირო):
   - `GEMINI_API_KEY` — [aistudio.google.com/apikey](https://aistudio.google.com/apikey)-დან
   - `GEMINI_BASE_URL` — დააკვირდი `.env.example`-ს

3. დოკუმენტები (`.txt` ან `.pdf`) ჩადე `data/`-ში. სურვილისამებრ გამოიყენეთ ქვესაქაღალდეები (მაგ. `data/legislative/`) — საქაღალდის სახელი გამოდის როგორც დოკუმენტის ტიპი ფილტრაციისთვის.

4. ინდექსის აგება:

   ```bash
   python -m rag_agent.ingest
   ```

5. ტერმინალიდან კითხვის დასმა:

   ```bash
   python main.py "როგორ ხდება საბაჟო გადასახადის გადახდა?"
   ```

პასუხი ქართულად იქნება, ბოლოში ციტატა და ბმული infohub.rs.ge/ka-ზე.

---

**ვებ-დემოს გაშვება**

დაყენებისა და ინდექსის აგების შემდეგ (ზემოთ 1–4):

- ვირტუალური გარემო უნდა იყოს ჩართული (თუ არა: `.venv\Scripts\Activate.ps1`).
- გაუშვი:
  ```bash
  streamlit run app.py
  ```
  (ლოკალურად და Hugging Face Space-ზე იგივე `app.py` იშვება.)
- ბრაუზერში გაიხსნება (ჩვეულებრივ http://localhost:8501): იქ ჩაწერეთ კითხვა ქართულად და დააჭირეთ „პასუხის მიღება“. შეგიძლია გამოიყენო გვერდზე მოცემული შემოთავაზებული კითხვები — დააკოპირე და ჩასვი ველში.

**კონფიგურაცია**

- `config.yaml` — მოდელის სახელი (მაგ. `gemini-2.5-flash`), ჩანკის ზომა, retrieval-ის პარამეტრები და ციტატის ტექსტი.
- `.env` — მხოლოდ `GEMINI_API_KEY` და `GEMINI_BASE_URL`.

**კოდიდან გამოყენება**

```python
from rag_agent import ask

answer, sources = ask("შენი კითხვა ქართულად")
print(answer)
```

სურვილისამებრ: `ask("კითხვა", doc_type="legislative")` — მხოლოდ იმ ჩანკების მიღება, რომლებიც ამ დოკუმენტის ტიპის საქაღალდიდანაა (`data/`-ის ქვეშ).

**რა არის რეპოში**

- `rag_agent/` — retrieval (BM25 + embeddings), გენერაცია (Gemini, OpenAI-თან შესათავსებელი API-ით), ingest, კონფიგის ჩატვირთვა.
- `main.py` — CLI შესასვლელი.
- `app.py` — ვებ-ინტერფეისი (Streamlit); ლოკალურად და Hugging Face Space-ზე.
- `data/` — წყაროს დოკუმენტები (ხელით ჩამატებული).
- `index/` — ingest-ის შედეგი (`chunks.json`, `embeddings.npy`). `data/`-ში ფაილების დამატების ან შეცვლის შემდეგ თავიდან გაშვება: `python -m rag_agent.ingest`.
