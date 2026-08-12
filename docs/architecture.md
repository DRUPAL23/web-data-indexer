# Architecture

```text
React/D3 dashboard
        |
   REST / GraphQL
        |
      FastAPI
        |
PostgreSQL + TimescaleDB + pgvector
        |
 Redis <-> Celery workers
        |
 crawler -> parser -> extractor -> indexer
```

## Data flow

1. Crawl jobs enter Redis through Celery.
2. Workers fetch public resources while respecting timeout, rate, and payload limits.
3. HTML is normalized and extracted into documents.
4. Documents receive full-text vectors and optional semantic embeddings.
5. Entities and relationships are persisted with provenance references.
6. API clients query lexical search, graph neighborhoods, and provenance.
