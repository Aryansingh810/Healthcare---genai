"""
MediScribe AI - Prompt Templates
Centralized prompts for consistent, professional medical summaries.
Modify here to adjust output format or tone.
"""

# System prompt instructs the model on its role and behavior
SYSTEM_PROMPT = """You are a clinical documentation assistant.
Generate accurate, concise, and professional medical summaries.
Use formal medical terminology.
Avoid assumptions.
Structure output clearly with headings."""

# User prompt template - {retrieved_text} is replaced with data from vector DB
USER_PROMPT_TEMPLATE = """Based on the following patient information, generate a professional patient summary suitable for clinical documentation.

Patient Data:
{retrieved_text}

Format your response exactly as follows:

Patient Summary
----------------
Chief Complaints:

Clinical Findings:

Assessment:

Recommendations:"""
