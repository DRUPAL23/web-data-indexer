from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Web Data Indexer API")

class SearchQuery(BaseModel):
    q: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/search")
def search(query: SearchQuery):
    # TODO: integrate with Postgres full-text / pgvector
    return {"query": query.q, "results": []}

@app.get("/graph/{entity_id}")
def graph(entity_id: int):
    # TODO: construct entity relationship graph from DB
    return {"entity_id": entity_id, "nodes": [], "edges": []}

@app.get("/provenance/{entity_id}")
def provenance(entity_id: int):
    # TODO: return provenance metadata for an entity
    return {"entity_id": entity_id, "provenance": []}
