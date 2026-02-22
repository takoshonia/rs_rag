#!/usr/bin/env python3
"""
Streamlit ვებ-ინტერფეისი. ლოკალურად: streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from rag_agent import ask, ask_keywords

HUB_URL = "https://infohub.rs.ge/ka"
PAGE_TITLE = "RAG აგენტი — საგადასახადო და საბაჟო ინფორმაცია"
DESCRIPTION = "დასვით კითხვა ქართულად. პასუხი ეფუძნება საინფორმაციო და მეთოდოლოგიურ ჰაბზე განთავსებულ დოკუმენტებს."

SUGGESTED_QUESTIONS = [
    "როგორ ხდება საბაჟო გადასახადის გადახდა?",
    "როგორ ხდება გადასახადის გადამხდელად რეგისტრაცია?",
    "რა არის საბაჟო ღირებულების კონტროლი?",
    "როდის და როგორ უნდა განხორციელდეს გადახდა საგადასახადო ვალდებულებისთვის?",
    "საგადასახადო დეკლარაციის წარდგენის წესი.",
    "დღგ-ის გადახდა და დეკლარირება.",
    "იმპორტზე საბაჟო გადასახადების გაუქმება — როდის ვრცელდება?",
    "საბაჟო ორგანოს და საგადასახადო ორგანოს მიერ გადასახადის გადამხდელად აღრიცხვა.",
    "გადახდის წყაროსთან გადასახადის დაკავება — როგორ მუშაობს?",
    "ანაზღაურების გადახდა საქონლის მიწოდებამდე — დღგ-ის დრო.",
]


def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon="📄", layout="centered")
    st.title("📄 " + PAGE_TITLE)
    st.markdown(DESCRIPTION)
    st.markdown("---")

    st.subheader("შემოთავაზებული კითხვები")
    st.caption("პასუხს პროგრამა მოძიებულ დოკუმენტებში ძიებს. შეგიძლიათ ქვემოთ ჩამოთვლილი კითხვები დააკოპიროთ და ჩასვათ ველში:")
    questions_text = "\n".join(SUGGESTED_QUESTIONS)
    st.code(questions_text, language=None)
    st.markdown("---")

    question = st.text_area(
        "კითხვა ქართულად",
        placeholder="ჩაწერეთ ან ჩაიკოპირეთ ზემოთან კითხვა.",
        height=100,
        key="question_input",
    )

    if st.button("პასუხის მიღება", type="primary"):
        if not (question and question.strip()):
            st.warning("გთხოვთ შეიყვანოთ კითხვა.")
        else:
            with st.spinner("პასუხის მოძიება..."):
                try:
                    keywords = ask_keywords(question.strip())
                    answer, sources = ask(question.strip())
                    with st.expander("საკვანძო სიტყვები (ჰაბზე ძიებისთვის)", expanded=False):
                        st.write(", ".join(keywords) if keywords else "—")
                    st.subheader("პასუხი")
                    st.markdown(answer)
                    st.markdown("---")
                    st.caption("წყარო")
                    st.markdown(f"[{HUB_URL}]({HUB_URL})")
                    if sources:
                        st.caption("გამოყენებული დოკუმენტების ფრაგმენტები")
                        for s in sources:
                            title = s.get("title") or "—"
                            doc_type = s.get("doc_type") or ""
                            st.markdown(f"- **{title}** {doc_type}")
                except Exception as e:
                    st.error(f"შეცდომა: {e}")

    st.markdown("---")
    st.caption("წყარო: საინფორმაციო და მეთოდოლოგიური ჰაბი — [infohub.rs.ge](https://infohub.rs.ge/ka)")


if __name__ == "__main__":
    main()
