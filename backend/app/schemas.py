from pydantic import BaseModel, HttpUrl
from typing import Any

class SearchResult(BaseModel):
    id: int
    url: HttpUrl
    title: str | None = None
    score: float = 0

class Entity(BaseModel):
    id: int
    canonical_name: str
    entity_type: str
    metadata: dict[str, Any] = {}

class CrawlRequest(BaseModel):
    url: HttpUrl
