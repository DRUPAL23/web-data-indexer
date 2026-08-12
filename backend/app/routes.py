from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from .db import get_db
from .schemas import CrawlRequest

router = APIRouter(prefix="/api/v1")

@router.get('/search')
def search(q: str = Query(min_length=1), limit: int = Query(20, le=100), db: Session = Depends(get_db)):
    rows = db.execute(text("""
      SELECT id, url, title, ts_rank(search_vector, websearch_to_tsquery('english', :q)) score
      FROM documents WHERE search_vector @@ websearch_to_tsquery('english', :q)
      ORDER BY score DESC LIMIT :limit
    """), {'q': q, 'limit': limit}).mappings().all()
    return {'query': q, 'results': [dict(r) for r in rows]}

@router.get('/entities/{entity_id}/graph')
def entity_graph(entity_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text("""
      SELECT e.id, e.canonical_name, e.entity_type, r.relation_type, r.weight
      FROM relationships r JOIN entities e ON e.id = r.target_entity_id
      WHERE r.source_entity_id = :id
      UNION ALL
      SELECT e.id, e.canonical_name, e.entity_type, r.relation_type, r.weight
      FROM relationships r JOIN entities e ON e.id = r.source_entity_id
      WHERE r.target_entity_id = :id
    """), {'id': entity_id}).mappings().all()
    return {'entity_id': entity_id, 'neighbors': [dict(r) for r in rows]}

@router.post('/crawl')
def enqueue_crawl(request: CrawlRequest):
    from workers.tasks import crawl_url
    job = crawl_url.delay(str(request.url))
    return {'job_id': job.id, 'status': 'queued'}
