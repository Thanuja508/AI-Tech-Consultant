# Design Document — AI Tech Consultant Knowledge Brain

## 1. Purpose

The Knowledge Brain provides a single source of technical knowledge for AI assistants. It retrieves relevant Brilliant Directories support articles and uses a language model to generate answers grounded in that documentation.

The design aims to reduce unsupported answers, provide source links, and route questions to human review when the available evidence is insufficient.

## 2. Architecture

The system has five main components:

1. **Article discovery and ingestion:** The scraper discovers support article URLs. The downloader retrieves article content and stores it as JSON.
2. **Embedding generation:** Sentence Transformers converts article text into numerical vectors using `all-MiniLM-L6-v2`.
3. **Vector storage and retrieval:** ChromaDB stores article text, metadata, and embeddings. User questions are embedded and compared with stored vectors.
4. **Answer generation:** FastAPI sends retrieved articles and the question to Groq's `openai/gpt-oss-20b` model. The model is instructed to answer from the supplied documentation.
5. **Human review and interface:** Unsupported questions can create review tasks. Streamlit provides a chat interface, and FastAPI exposes endpoints for search, answers, and expert tasks.

## 3. Data Flow

1. Discover support article URLs.
2. Download and parse article content.
3. Store articles as JSON files.
4. Generate embeddings and upsert article records into ChromaDB.
5. Receive a user's question through the API or chat interface.
6. Generate a query embedding and retrieve nearest articles.
7. Filter results using an initial relevance threshold.
8. Supply the retrieved text to the language model.
9. Return the answer and source URLs.
10. Create a human-review task if no evidence is retrieved or the model reports insufficient evidence.

## 4. Technology Choices

| Component | Technology | Reason |
|---|---|---|
| Language | Python | Supports the API, scraping, and ML libraries |
| API | FastAPI | Provides typed requests and documented endpoints |
| Embeddings | Sentence Transformers | Creates semantic text representations |
| Vector database | ChromaDB | Persists embeddings and supports similarity search |
| Language model | Groq-hosted `openai/gpt-oss-20b` | Generates answers without requiring a paid Claude API |
| User interface | Streamlit | Provides a simple interactive chat interface |
| Task storage | JSON file | Keeps the prototype's human-review tasks persistent |

The implementation currently uses Groq rather than Anthropic Claude. If Claude is a strict assignment requirement, this substitution must be disclosed.

## 5. Retrieval and Relevance

The knowledge base uses normalized embeddings for semantic search. ChromaDB returns candidate articles ranked by vector distance. The search function converts distances into an approximate similarity score and applies an initial threshold.

This threshold is a heuristic, not a calibrated confidence probability. Its effectiveness must be measured using relevant and irrelevant questions. The current implementation should be evaluated before being used for production decisions.

## 6. Grounded Answer Generation

The API provides the language model with the question and retrieved article content. The system prompt instructs the model to avoid inventing product details and to report insufficient evidence when the retrieved content does not answer the question.

The response includes source titles and URLs. If no relevant articles are returned, the API creates a human-review task rather than asking the model to invent an answer.

Model-generated answers and source relevance still require evaluation. Source links alone do not guarantee that every statement is supported.

## 7. Human Review

Expert tasks are stored in `data/expert_tasks.json`. Each task includes an identifier, question, reason, sources, status, and timestamps. A reviewer can submit an answer, which changes the task status to `answered`.

The JSON-file approach is appropriate for a local prototype. A production deployment should use a transactional database, authentication, authorization, and an audit trail.

## 8. Reliability and Security

- Request models validate input lengths and search limits.
- Article files that cannot be parsed are skipped during indexing.
- Vector records use stable IDs derived from article filenames.
- API keys are read from environment variables.
- Secrets and local databases must not be committed to a public repository.
- API errors should not expose credentials or sensitive environment details.
- Concurrent writes and multiple server instances require stronger storage controls than a local JSON file.

## 9. Current Limitations and Future Work

The current prototype provides article retrieval, answer generation, source links, and human-review endpoints. Further work is required to satisfy a full production-grade knowledge service:

- Calibrate retrieval thresholds with a representative evaluation set.
- Add hybrid keyword and vector retrieval.
- Add incremental ingestion, deletion handling, retries, and ingestion status tracking.
- Support image downloads and image descriptions if required by the source material.
- Expand automated evaluation beyond the current five unit tests.
- Add authenticated reviewer workflows and durable task storage.
- Measure retrieval accuracy, answer groundedness, latency, and cost.
- Verify all assignment-specific requirements before submission.
-