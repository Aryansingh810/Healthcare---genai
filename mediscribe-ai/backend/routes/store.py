"""
MediScribe AI - Store Route
Accepts raw patient input, converts to embeddings, stores in vector DB.
"""

from flask import Blueprint, request, jsonify
from services.vector_service import store_patient_data

store_bp = Blueprint("store", __name__)


@store_bp.route("/store", methods=["POST"])
def store():
    """
    POST /store
    Body: { "patient_input": "..." }
    Stores patient data in vector database.
    """
    data = request.get_json() or {}
    patient_input = data.get("patient_input", "").strip()
    
    if not patient_input:
        return jsonify({
            "error": "patient_input is required and cannot be empty"
        }), 400
    
    try:
        result = store_patient_data(patient_input)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
