# Web Data Indexer

A production-oriented web intelligence platform for crawling, extracting, indexing, searching, and exploring web entities with provenance.

## Architecture

React + D3 dashboard → FastAPI REST API → PostgreSQL/TimescaleDB + pgvector → Celery workers + Redis.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000/docs  
Dashboard: http://localhost:5173

## Components

- **Frontend:** React, TypeScript, D3.js
- **API:** FastAPI, SQLAlchemy, Pydantic
- **Storage:** PostgreSQL + TimescaleDB, pgvector, tsvector
- **Workers:** Celery + Redis
- **Crawling:** httpx with robots/politeness controls
- **Observability:** health endpoints and structured logging

## Repository layout

See `docs/architecture.md` for system boundaries and `docs/api.md` for API contracts.
