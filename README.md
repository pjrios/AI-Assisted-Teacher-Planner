# AI Assisted Teacher Planner

This repository provides a reference implementation of the AI-assisted planning workflow
outlined in the developer brief. It combines structured storage with semantic search to
extract yearly plans, embed their content, and generate lesson agendas.

## Features

- **Yearly plan ingestion** – Upload `.docx` files and convert them into a normalized JSON
  representation ready for relational storage.
- **Vector database integration** – Automatically chunk each learning area and store
  embeddings with metadata in a persistent Chroma collection.
- **Lesson generation service** – Retrieve the most relevant context for a topic and prompt
  the OpenAI Responses API to create pre/while/post lesson activities.
- **FastAPI backend** – A lightweight API layer exposing health checks, ingestion, and
  lesson-generation endpoints.

## Project Structure

```text
backend/
  app/
    api/            # FastAPI routes
    ingestion/      # File parsing, chunking, embeddings
    services/       # AI orchestration utilities
    config.py       # Environment configuration via Pydantic settings
    crud.py         # Database helper functions
    db.py           # SQLAlchemy engine and session helpers
    main.py         # FastAPI app entrypoint
    models.py       # SQLAlchemy ORM models for the planner domain
    schemas.py      # Pydantic schemas shared across API and services
requirements.txt    # Python dependencies
```

## Getting Started

### One-command bootstrap

Run the pipeline script directly and it will take care of the rest:

```bash
python run_pipeline.py path/to/plan.docx --output-json data/plan.json
```

On first launch the script will:

- Create a `.venv` virtual environment in the project directory.
- Install dependencies from `requirements.txt`.
- Prompt for an `OPENAI_API_KEY` if one is not already configured and persist it to `.env`.
- Initialize the PostgreSQL schema configured by `DATABASE_URL`.
- Parse the yearly plan, emit the normalized JSON (printing to stdout or `--output-json`),
  and store semantic chunks in the Chroma vector database.

Subsequent runs reuse the prepared environment automatically. Ensure that
`DATABASE_URL` points to a reachable PostgreSQL instance before running the script.

### Optional: run the API server

If you want to explore the FastAPI endpoints after the pipeline has prepared the
environment, activate the virtual environment and start the server:

```bash
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
uvicorn backend.app.main:app --reload
```

Visit `http://localhost:8000/docs` to explore the interactive API documentation.

## Key Workflows

### Ingest a yearly plan

Send a multipart request to `/plans/ingest` with the `.docx` file. The server will:

1. Parse the document into structured trimesters, areas, and learning artifacts.
2. Generate semantic chunks and embeddings.
3. Persist vectors in the Chroma collection for semantic retrieval.

The endpoint returns the normalized `YearlyPlan` schema, which can be stored in PostgreSQL
or used to seed additional data.

### Generate lesson activities

Use the `/plans/{plan_id}/topics/{topic_id}/generate` endpoint with a topic metadata payload
(e.g., topic name, grade, trimester) and a schedule array of `(date, start, end)` tuples.
The planner fetches relevant context from Chroma, crafts an instructional prompt, and
returns structured sessions ready to be saved as class and activity records.

## Next Steps

- Connect the CRUD utilities to persistence workflows for levels, trimesters, and topics.
- Expand the ingestion pipeline to handle `.pdf` and `.xlsx` files.
- Add background tasks for long-running embedding jobs and lesson generation.
- Build the React/Tailwind front-end and integrate with the FastAPI backend.
