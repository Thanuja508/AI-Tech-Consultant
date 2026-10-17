# AI Development Log — Knowledge Brain

## AI Tools Used
- ChatGPT: Used for implementation guidance, debugging, test design, and documentation drafting.
- Groq-hosted `openai/gpt-oss-20b`: Used for generating answers from retrieved support documentation.
- Sentence Transformers `all-MiniLM-L6-v2`: Used to generate semantic embeddings for article retrieval.

## Development Work
- Implemented support article discovery and downloading.
- Stored downloaded article content as JSON files.
- Created a persistent ChromaDB collection for semantic search.
- Integrated the retrieval pipeline with FastAPI and a Groq-hosted language model.
- Built a Streamlit interface for asking technical questions.
- Added human-review task creation and expert-answer endpoints.
- Added an initial retrieval relevance threshold.
- Created automated tests for relevant search, source metadata, unrelated questions, and empty input.
- Documented the architecture, evaluation approach, and known limitations.

## Debugging and Validation
- Verified that the FastAPI application starts successfully.
- Tested article search and answer generation.
- Verified human-review task creation and answer submission.
- Tested an unsupported question and confirmed that it returned no sources and triggered human review.
- Ran five automated unit tests; all passed.

## Important Limitations
- The answer-generation model is Groq-hosted `openai/gpt-oss-20b`, not Anthropic Claude.
- Retrieval threshold calibration and comprehensive answer-quality evaluation remain incomplete.
- The implementation requires further work to satisfy all production-grade ingestion, image-processing, and evaluation requirements.

## Developer Responsibility
AI assistance was used during development. The implementation and test results should be reviewed by the developer, and any claims in the submission should reflect verified behavior.