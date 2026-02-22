#!/usr/bin/env python3
"""
CLI for the RAG agent. Answers questions in Georgian and cites the Information and Methodological Hub.
Usage: python main.py "როგორ უნდა დავრეგისტრირდე დღგ-ზე?"
"""

import sys
from pathlib import Path

# Ensure package is on path when run as script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag_agent import ask, ask_keywords


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<question in Georgian>\"")
        print("Example: python main.py \"როგორ უნდა დავრეგისტრირდე დღგ-ზე?\"")
        sys.exit(1)
    question = " ".join(sys.argv[1:])
    keywords = ask_keywords(question)
    print("Keywords (for hub search):", keywords)
    print("-" * 60)
    answer, sources = ask(question)
    print(answer)
    if sources:
        print("-" * 60)
        print("Sources:", sources)


if __name__ == "__main__":
    main()
