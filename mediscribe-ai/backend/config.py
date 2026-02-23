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

# Grok API - Load from environment (never hardcode)
# Point GROK_API_URL to your Grok-compatible endpoint.
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-1")
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")

# Vector Database - ChromaDB by default (easy to swap for FAISS)
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")
VECTOR_DB_COLLECTION = "patient_records"

# Retrieval settings
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
