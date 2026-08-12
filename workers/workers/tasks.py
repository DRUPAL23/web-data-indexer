import os
import time
import hashlib
import httpx
from .celery_app import celery_app
from .crawler import fetch_html
from .entities import extract_entities
from .indexer import allowed_by_robots, add_provenance, db_connect, upsert_document, upsert_entity

USER_AGENT = os.getenv('CRAWLER_USER_AGENT', 'WebDataIndexerBot/0.1')
TIMEOUT = float(os.getenv('CRAWLER_TIMEOUT_SECONDS', '15'))
MAX_BYTES = int(os.getenv('CRAWLER_MAX_BYTES', '5000000'))
MIN_DELAY = float(os.getenv('CRAWLER_MIN_DELAY_SECONDS', '1.0'))

@celery_app.task(bind=True, autoretry_for=(httpx.HTTPError,), retry_backoff=True, max_retries=3)
def crawl_url(self, url: str):
    started = time.monotonic()
    if not allowed_by_robots(url):
        return {'url': url, 'status': 'blocked_by_robots'}

    title, content, status_code = fetch_html(url, USER_AGENT, TIMEOUT, MAX_BYTES)
    checksum = hashlib.sha256(content.encode('utf-8', errors='ignore')).hexdigest()
    document_id = upsert_document(url, title, content, checksum)
    add_provenance(document_id, url, checksum)

    names = extract_entities(title, content)
    entity_ids = [upsert_entity(name) for name in names]

    with db_connect() as conn:
        for entity_id in entity_ids:
            conn.execute('''
                INSERT INTO document_entities(document_id, entity_id, mention_count)
                VALUES (%s,%s,1)
                ON CONFLICT(document_id, entity_id)
                DO UPDATE SET mention_count = document_entities.mention_count + 1
            ''', (document_id, entity_id))
        for left, right in zip(entity_ids, entity_ids[1:]):
            if left == right:
                continue
            conn.execute('''
                INSERT INTO relationships(source_entity_id,target_entity_id,relation_type,weight,document_id)
                VALUES (%s,%s,'co_occurs',1,%s)
            ''', (left, right, document_id))
        conn.commit()

    elapsed = round(time.monotonic() - started, 3)
    if MIN_DELAY > 0:
        time.sleep(MIN_DELAY)
    return {'document_id': document_id, 'url': url, 'status': status_code,
            'entities_indexed': len(entity_ids), 'content_hash': checksum,
            'elapsed_seconds': elapsed}
