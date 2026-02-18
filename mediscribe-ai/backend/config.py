"""
MediScribe AI - Configuration Module
Loads settings from environment variables for easy deployment and security.
Swap LLM or Vector DB by changing these configuration values.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
VECTOR_DB_PATH = BASE_DIR / "vector_db" / "patient_records"

# Google Gemini API - Load from environment (never hardcode)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")

# Vector Database - ChromaDB by default (easy to swap for FAISS)
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")
VECTOR_DB_COLLECTION = "patient_records"

# Retrieval settings
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
