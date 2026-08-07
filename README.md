# Web Data Indexer

Initial scaffold implementing the architecture:

- Frontend: React + D3 (Vite)
- API: FastAPI with placeholder endpoints
- Workers: Celery + Redis for distributed crawling
- Database: PostgreSQL + TimescaleDB (docker-compose service)

Quickstart (requires Docker & Docker Compose):

1. Build and start all services:

   docker-compose up --build

2. API will be available at http://localhost:8000
3. Frontend Vite dev server at http://localhost:3000 (proxied to 5173)

Next steps:
- Implement DB models and migrations (Alembic)
- Add full-text search, pgvector integration, and Timescale hypertables
- Implement crawler politeness, rate-limiting, and storage of provenance metadata
- Build dashboard visualizations for entity graphs using D3
