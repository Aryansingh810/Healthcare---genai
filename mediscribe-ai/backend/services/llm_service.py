"""
MediScribe AI - LLM Service (Google Gemini)
Handles all Google Gemini API interactions.
Swap provider by replacing this module - no other code changes needed.
"""

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL
from services.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def configure_gemini():
    """Configure Gemini API with key from environment."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not set. Add it to .env or export in shell."
        )
    genai.configure(api_key=GEMINI_API_KEY)


def generate_summary(retrieved_text: str) -> str:
    """
    Generate clinical summary from retrieved patient data using Gemini.
    
    Args:
        retrieved_text: Patient data retrieved from vector database
        
    Returns:
        Formatted clinical summary string
    """
    configure_gemini()
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT
    )
    
    user_prompt = USER_PROMPT_TEMPLATE.format(retrieved_text=retrieved_text)
    response = model.generate_content(user_prompt)
    
    return response.text
