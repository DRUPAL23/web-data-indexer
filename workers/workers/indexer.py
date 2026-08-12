import os
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://indexer:indexer@localhost:5432/indexer').replace('postgresql+psycopg://', 'postgresql://')
USER_AGENT = os.getenv('CRAWLER_USER_AGENT', 'WebDataIndexerBot/0.1')


def db_connect():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def allowed_by_robots(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f'{parsed.scheme}://{parsed.netloc}/robots.txt'
    parser = RobotFileParser(robots_url)
    try:
        parser.read()
        return parser.can_fetch(USER_AGENT, url)
    except Exception:
        return False


def upsert_document(url, title, content, content_hash, status='indexed'):
    with db_connect() as conn:
        row = conn.execute('''
            INSERT INTO documents(url,title,content,content_hash,status)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT(url) DO UPDATE SET title=EXCLUDED.title,
              content=EXCLUDED.content, content_hash=EXCLUDED.content_hash,
              fetched_at=now(), status=EXCLUDED.status
            RETURNING id
        ''', (url, title, content, content_hash, status)).fetchone()
        conn.commit()
        return row['id']


def add_provenance(document_id, url, checksum, extractor='beautifulsoup4'):
    with db_connect() as conn:
        conn.execute('''INSERT INTO provenance(document_id,source_url,extractor,checksum)
                        VALUES (%s,%s,%s,%s)''', (document_id, url, extractor, checksum))
        conn.commit()


def upsert_entity(name, entity_type='mention'):
    with db_connect() as conn:
        row = conn.execute('''
            INSERT INTO entities(canonical_name,entity_type) VALUES (%s,%s)
            ON CONFLICT(canonical_name,entity_type) DO UPDATE SET canonical_name=EXCLUDED.canonical_name
            RETURNING id
        ''', (name, entity_type)).fetchone()
        conn.commit()
        return row['id']
