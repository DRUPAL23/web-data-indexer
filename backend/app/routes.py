from fastapi import APIRouter, Depends, Query
from celery import Celery
from sqlalchemy import text
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .schemas import CrawlRequest

router = APIRouter(prefix='/api/v1')
celery = Celery('api-producer', broker=settings.redis_url, backend=settings.redis_url)

@router.get('/search')
def search(q: str = Query(min_length=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    rows = db.execute(text('''
      SELECT id, url, title,
             ts_rank(search_vector, websearch_to_tsquery('english', :q)) AS score
      FROM documents WHERE search_vector @@ websearch_to_tsquery('english', :q)
      ORDER BY score DESC, fetched_at DESC LIMIT :limit
    '''), {'q': q, 'limit': limit}).mappings().all()
    return {'query': q, 'results': [dict(r) for r in rows]}

@router.get('/entities')
def entities(q: str | None = Query(default=None), limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    rows = db.execute(text('''
      SELECT id, canonical_name, entity_type, description, metadata FROM entities
      WHERE (:q IS NULL OR canonical_name ILIKE '%' || :q || '%')
      ORDER BY canonical_name LIMIT :limit
    '''), {'q': q, 'limit': limit}).mappings().all()
    return {'results': [dict(r) for r in rows]}

@router.get('/entities/{entity_id}/graph')
def entity_graph(entity_id: int, db: Session = Depends(get_db)):
    nodes = db.execute(text('''
      SELECT e.id, e.canonical_name, e.entity_type FROM entities e WHERE e.id = :id
      UNION SELECT e.id, e.canonical_name, e.entity_type FROM relationships r JOIN entities e ON e.id = r.target_entity_id WHERE r.source_entity_id = :id
      UNION SELECT e.id, e.canonical_name, e.entity_type FROM relationships r JOIN entities e ON e.id = r.source_entity_id WHERE r.target_entity_id = :id
    '''), {'id': entity_id}).mappings().all()
    edges = db.execute(text('''
      SELECT source_entity_id AS source, target_entity_id AS target, relation_type AS type, weight, document_id
      FROM relationships WHERE source_entity_id = :id OR target_entity_id = :id ORDER BY weight DESC
    '''), {'id': entity_id}).mappings().all()
    return {'entity_id': entity_id, 'nodes': [dict(r) for r in nodes], 'edges': [dict(r) for r in edges]}

@router.get('/documents/{document_id}/provenance')
def document_provenance(document_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text('''
      SELECT id, source_url, retrieved_at, extractor, checksum, metadata
      FROM provenance WHERE document_id = :id ORDER BY retrieved_at DESC
    '''), {'id': document_id}).mappings().all()
    return {'document_id': document_id, 'provenance': [dict(r) for r in rows]}

@router.post('/crawl')
def enqueue_crawl(request: CrawlRequest):
    job = celery.send_task('workers.tasks.crawl_url', args=[str(request.url)])
    return {'job_id': job.id, 'status': 'queued'}
