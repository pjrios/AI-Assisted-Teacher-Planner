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

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env  # create if needed
   ```

   Update the `.env` file with:

   - `DATABASE_URL` – PostgreSQL connection string.
   - `OPENAI_API_KEY` – API key used for embeddings and lesson generation.
   - `CHROMA_PERSIST_DIRECTORY` – Optional override for Chroma storage.

3. **Run the API server**

   ```bash
   uvicorn backend.app.main:app --reload
   ```

   Visit `http://localhost:8000/docs` to explore the interactive API documentation.

4. **Ingest a plan with one command**

   Once your environment variables are configured, the `run_pipeline.py` script handles
   bootstrapping the environment (ensuring the PostgreSQL schema exists and the Chroma
   persistence directory is created), parsing a yearly plan, exporting the normalized
   JSON, and storing semantic chunks in Chroma:

   ```bash
   python run_pipeline.py path/to/plan.docx --output-json data/plan.json
   ```

   The script prints the structured plan (or writes it to `--output-json`) and confirms the
   number of chunks saved to the configured Chroma collection. Ensure that the
   `DATABASE_URL` points to a reachable PostgreSQL instance and that `OPENAI_API_KEY` is
   populated; the pipeline will stop with a clear error if either requirement is missing.

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
