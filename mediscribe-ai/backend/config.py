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

# Groq API - Load from environment (never hardcode)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# Vector Database - ChromaDB by default (easy to swap for FAISS)
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")
VECTOR_DB_COLLECTION = "patient_records"

# Retrieval settings
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
