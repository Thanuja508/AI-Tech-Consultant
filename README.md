# AI Tech Consultant

An AI-powered support prototype with three connected applications that use a shared Knowledge Brain.

## Project Structure

- `task1-knowledge-brain/` — Scrapes support documentation, indexes articles in ChromaDB, retrieves relevant information, generates grounded answers, and supports human review.
- `task2-inbox-agent/` — Classifies incoming support emails, retrieves documentation through Task 1's API, prepares editable replies, and records approval or rejection feedback.
- `task3-meeting-to-scope/` — Converts meeting notes into structured requirements, preliminary effort estimates, scope options, and an approval record.

## Technology Stack

- Python
- FastAPI
- Streamlit
- ChromaDB
- Sentence Transformers
- Groq API using `openai/gpt-oss-20b`

**Model note:** This prototype uses Groq rather than Anthropic Claude.

## Running the Applications

Open a separate VS Code terminal for each application.

### 1. Knowledge Brain

```powershell
cd task1-knowledge-brain
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Open the API documentation at `http://127.0.0.1:8000/docs`.

In another terminal:

```powershell
cd task1-knowledge-brain
.venv\Scripts\Activate.ps1
streamlit run chat_app.py
```

### 2. Inbox Agent

Keep the Knowledge Brain API running. In another terminal:

```powershell
cd task2-inbox-agent
python -m streamlit run app.py --server.port 8505
```

### 3. Meeting to Scope

In another terminal:

```powershell
cd task3-meeting-to-scope
python -m streamlit run app.py --server.port 8507
```

## Prototype Limitations

- AI answers depend on retrieved documentation and model output.
- Effort estimates are preliminary and require human review.
- Email sending is intentionally disabled.
- Feedback and approval records are stored locally.
- The applications must be started separately.

## Security

Keep API keys in local `.env` files. Never commit API keys, credentials, or virtual environments to source control.