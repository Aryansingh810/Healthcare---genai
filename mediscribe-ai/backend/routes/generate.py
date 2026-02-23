"""
MediScribe AI - Generate Summary Route
Retrieves data from vector DB, passes to LLM, returns clinical summary and PDF path.
"""

import uuid
from datetime import datetime
from pathlib import Path

from flask import Blueprint, request, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from config import BASE_DIR
from services.vector_service import store_patient_data, retrieve_patient_data
from services.llm_service import generate_summary, GroqAPIError

generate_bp = Blueprint("generate", __name__)


def _generate_pdf_report(summary_text: str) -> str:
    """
    Generate a PDF report for the given summary text.

    Saves to backend/reports/ and returns the web path (/reports/<filename>.pdf).
    """
    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    filename = f"summary_{uuid.uuid4().hex}.pdf"
    file_path = reports_dir / filename

    c = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4

    margin_x = 72
    y = height - margin_x

    # Fixed PDF format as specified
    lines = [
        "MediScribe AI – Patient Summary Report",
        "",
        "Chief Complaints:",
        "Clinical Findings:",
        "Assessment:",
        "Recommendations:",
        "",
        f"Generated On: {datetime.utcnow().isoformat()} UTC",
    ]

    c.setFont("Helvetica", 11)
    for line in lines:
        if y < margin_x:
            c.showPage()
            y = height - margin_x
            c.setFont("Helvetica", 11)
        c.drawString(margin_x, y, line)
        y -= 14

    c.save()

    # Web path exposed to frontend
    return f"/reports/{filename}"


@generate_bp.route("/generate-summary", methods=["POST"])
def generate():
    """
    POST /generate-summary
    Body: { "patient_input": "..." }
    
    Workflow:
    1. Store patient input in vector DB
    2. Retrieve relevant data from vector DB
    3. Generate summary via LLM
    4. Generate PDF report for summary
    5. Return structured response
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
        
        # Step 3: Generate summary via LLM
        summary = generate_summary(retrieved_text)

        # Step 4: Generate PDF report
        pdf_path = _generate_pdf_report(summary)
        
        return jsonify({
            "status": "success",
            "summary": summary,
            "pdf_path": pdf_path,
        }), 200
        
    except GroqAPIError as e:
        # Handle Groq API errors with proper status codes
        return jsonify({
            "error": e.message,
            "error_code": e.error_code
        }), e.status_code or 500
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        # Generic error handling
        error_msg = str(e)
        return jsonify({
            "error": f"An error occurred: {error_msg}"
        }), 500
