"""
RAG Agent for the Information and Methodological Hub (infohub.rs.ge).
Answers questions in Georgian and cites the hub as the source.
"""

from .agent import ask, ask_keywords

__all__ = ["ask", "ask_keywords"]
