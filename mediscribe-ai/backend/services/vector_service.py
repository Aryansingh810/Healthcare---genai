"""
MediScribe AI - Vector Database Service (ChromaDB)
Stores and retrieves patient data using embeddings.
Uses ChromaDB's default embedding function (no extra deps).
Swap for FAISS by implementing same interface in a new module.
"""

import uuid
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from config import VECTOR_DB_PATH, VECTOR_DB_COLLECTION, RETRIEVAL_TOP_K

# ChromaDB default uses ONNX/all-MiniLM-L6-v2 - no sentence-transformers needed
DEFAULT_EF = embedding_functions.DefaultEmbeddingFunction()


def _get_client():
    """Get or create ChromaDB client with persistent storage."""
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH),
        settings=Settings(anonymized_telemetry=False)
    )


def store_patient_data(patient_input: str) -> dict:
    """
    Convert patient input to embeddings and store in vector database.
    ChromaDB handles embedding via default embedding function.

    Args:
        patient_input: Raw text (symptoms, reports, observations)

    Returns:
        dict with status and record id
    """
    client = _get_client()
    collection = client.get_or_create_collection(
        name=VECTOR_DB_COLLECTION,
        embedding_function=DEFAULT_EF,
        metadata={"description": "Patient clinical records"}
    )

    record_id = str(uuid.uuid4())
    collection.add(
        ids=[record_id],
        documents=[patient_input],
        metadatas=[{"source": "workspace_input"}]
    )

    return {"status": "stored", "id": record_id}


def retrieve_patient_data(query: str = None, top_k: int = None) -> str:
    """
    Retrieve relevant patient data from vector database.
    If no query, returns most recent documents.

    Args:
        query: Optional search query (uses patient_input if from same session)
        top_k: Number of documents to retrieve

    Returns:
        Concatenated retrieved text for LLM consumption
    """
    top_k = top_k or RETRIEVAL_TOP_K
    client = _get_client()

    try:
        collection = client.get_collection(
            name=VECTOR_DB_COLLECTION,
            embedding_function=DEFAULT_EF
        )
    except Exception:
        return ""

    count = collection.count()
    if count == 0:
        return ""

    if query and query.strip():
        results = collection.query(
            query_texts=[query.strip()],
            n_results=min(top_k, count)
        )
    else:
        results = collection.get(
            limit=min(top_k, count),
            include=["documents"]
        )

    documents = results.get("documents") or []
    if documents and isinstance(documents[0], list):
        documents = documents[0]

    return "\n\n---\n\n".join(documents) if documents else ""
