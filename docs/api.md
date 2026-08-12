# API

- `GET /health` — service health.
- `GET /api/v1/search?q=<query>&limit=<n>` — PostgreSQL full-text search.
- `GET /api/v1/entities/{id}/graph` — relationship neighborhood.
- `POST /api/v1/crawl` with `{ "url": "https://example.com" }` — enqueue crawl job.

GraphQL is reserved for the next API milestone so the REST contract can stabilize first.
