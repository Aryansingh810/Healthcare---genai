# MediScribe AI

AI-powered healthcare content generator that converts raw patient inputs (symptoms, reports, observations) into professional clinical summaries using **Google Gemini API** and a **Vector Database** (ChromaDB).

## Features

- Professional medical tone and structured output
- Store patient data in vector database (embeddings)
- Retrieve relevant context and generate summaries via Gemini
- Minimal, clinical-focused UI
- Modular architecture—easy to swap LLM or vector DB

## Tech Stack

- **Frontend:** HTML, Tailwind CSS
- **Backend:** Python, Flask
- **AI:** Google Gemini API (`google-generativeai` SDK)
- **Vector DB:** ChromaDB (replaceable with FAISS)

## Project Structure

```
mediscribe-ai/
├── backend/
│   ├── app.py              # Flask app
│   ├── config.py           # Environment config
│   ├── requirements.txt
│   ├── routes/
│   │   ├── store.py        # POST /api/store
│   │   └── generate.py     # POST /api/generate-summary
│   ├── services/
│   │   ├── llm_service.py      # Gemini API
│   │   ├── vector_service.py   # ChromaDB
│   │   └── prompt_templates.py
│   └── vector_db/
│       └── patient_records/
├── frontend/
│   ├── templates/
│   │   ├── index.html
│   │   ├── about.html
│   │   └── workspace.html
│   └── static/assets/
└── README.md
```

## Setup

1. **Clone and enter project:**
   ```bash
   cd mediscribe-ai/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:** (create `.env` in `backend/` from `.env.example`)
   ```bash
   copy .env.example .env   # Windows (run from backend/)
   # cp .env.example .env   # macOS/Linux
   ```
   Edit `.env` and add your `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/apikey).

5. **Run the app:**
   ```bash
   python app.py
   ```
   Open http://localhost:5000

## Workflow

1. Doctor submits patient input (symptoms, reports, observations)
2. Data is stored in the vector database (embedded and indexed)
3. Relevant data is retrieved from the vector database
4. Google Gemini generates a structured clinical summary from retrieved data

## API Endpoints

| Method | Endpoint            | Body                      | Description                    |
|--------|---------------------|---------------------------|--------------------------------|
| POST   | `/api/store`        | `{"patient_input": "..."}` | Store patient data in vector DB |
| POST   | `/api/generate-summary` | `{"patient_input": "..."}` | Store, retrieve, and generate summary |

## Output Format

```
Patient Summary
----------------
Chief Complaints:

Clinical Findings:

Assessment:

Recommendations:
```

## License

MIT
