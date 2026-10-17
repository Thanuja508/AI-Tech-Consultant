# AI Tech Consultant — Knowledge Brain

## Overview
A retrieval-augmented generation (RAG) system that answers technical questions using Brilliant Directories support documentation. It uses semantic search, ChromaDB, Sentence Transformers, FastAPI, Groq, and Streamlit.

## Features
- Collects and stores support articles as JSON files.
- Generates semantic embeddings using all-MiniLM-L6-v2.
- Searches a persistent ChromaDB knowledge base.
- Filters low-relevance search results.
- Generates answers using Groq's openai/gpt-oss-20b model.
- Returns article titles and source URLs.
- Creates human-review tasks when evidence is insufficient.
- Provides a Streamlit chat interface and FastAPI endpoints.
- Includes automated knowledge-base search tests.

## Project Structure
- app/scraper.py — discovers support article URLs.
- app/article_downloader.py — downloads and stores article content.
- app/knowledge_base.py — builds embeddings and performs semantic search.
- app/main.py — FastAPI endpoints and AI answer generation.
- chat_app.py — Streamlit user interface.
- data/articles/ — downloaded article JSON files.
- data/chroma_db/ — persistent vector database.
- data/expert_tasks.json — human-review task records.
- test_knowledge_brain.py — search unit tests.
- test_results.txt — saved test output.

## Setup
Use Python 3.12 or another Python version supported by the installed dependencies.

1. Create and activate a virtual environment.
2. Install project dependencies.
3. Create a .env file with your Groq API key:

   GROQ_API_KEY=your_groq_api_key

4. Ensure the support articles and ChromaDB index are available.
5. Start the API:

   python -m uvicorn app.main:app --reload

6. In a second terminal, start the UI:

   streamlit run chat_app.py

7. Open http://127.0.0.1:8000/docs for API testing and the Streamlit URL printed in the terminal for the chat interface.

## Run Tests
python -m unittest test_knowledge_brain -v

## Limitations
- Answer quality depends on the retrieved documentation and model output.
- The relevance threshold requires evaluation against representative questions.
- Human-review tasks are stored locally in a JSON file.
- This prototype uses Groq rather than Anthropic Claude.

## Security
Never commit .env, API keys, virtual environments, or private credentials to source control.


## Task 2 — Inbox Agent

The Inbox Agent classifies incoming support emails, retrieves supporting documentation from Task 1, drafts a reply, and allows the user to approve or reject it. Feedback is stored locally in `task2-inbox-agent/feedback.json`. Email sending is disabled in this prototype.

Start the application from the project root:

```powershell
cd task2-inbox-agent
python -m streamlit run app.py --server.port 8505
```

Open `http://localhost:8505` in your browser. Ensure the Task 1 API is running before using the Inbox Agent.

## Task 3 — Meeting-to-Scope

The Meeting-to-Scope application converts meeting notes into structured requirements, preliminary effort estimates, scope options, and a reviewable approval record. Decisions are stored in `task3-meeting-to-scope/scope_feedback.json`.

Start the application from the project root:

```powershell
cd task3-meeting-to-scope
python -m streamlit run app.py --server.port 8507
```

Open `http://localhost:8507` in your browser.

## Prototype Limitations

- The prototype uses Groq rather than Anthropic Claude.
- Estimates and generated responses require human review.
- Email sending is intentionally disabled.
- Run each application in a separate terminal and keep required services running.

## Security

Never commit `.env` files, API keys, virtual environments, or private credentials to source control.