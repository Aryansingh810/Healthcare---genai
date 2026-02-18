"""
MediScribe AI - Generate Summary Route
Retrieves data from vector DB, passes to Gemini, returns clinical summary.
"""

from flask import Blueprint, request, jsonify
from services.vector_service import store_patient_data, retrieve_patient_data
from services.llm_service import generate_summary

generate_bp = Blueprint("generate", __name__)


@generate_bp.route("/generate-summary", methods=["POST"])
def generate():
    """
    POST /generate-summary
    Body: { "patient_input": "..." }
    
    Workflow:
    1. Store patient input in vector DB
    2. Retrieve relevant data from vector DB
    3. Generate summary via Gemini
    4. Return structured response
    """
    data = request.get_json() or {}
    patient_input = data.get("patient_input", "").strip()
    
    if not patient_input:
        return jsonify({
            "error": "patient_input is required and cannot be empty"
        }), 400
    
    try:
        # Step 1: Store in vector database (mandatory workflow)
        store_patient_data(patient_input)
        
        # Step 2: Retrieve from vector database
        retrieved_text = retrieve_patient_data(query=patient_input)
        
        if not retrieved_text:
            retrieved_text = patient_input  # Fallback if DB empty (first run)
        
        # Step 3: Generate summary via Gemini
        summary = generate_summary(retrieved_text)
        
        return jsonify({
            "status": "success",
            "summary": summary
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
