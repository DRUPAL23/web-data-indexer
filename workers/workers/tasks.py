from bs4 import BeautifulSoup
import hashlib
import httpx
from .celery_app import celery_app

@celery_app.task(bind=True, autoretry_for=(httpx.HTTPError,), retry_backoff=True, max_retries=3)
def crawl_url(self, url: str):
    headers = {'User-Agent': 'WebDataIndexerBot/0.1 (+https://example.com/bot)'}
    with httpx.Client(timeout=15, follow_redirects=True, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup(['script','style','noscript']): tag.decompose()
    title = soup.title.get_text(' ', strip=True) if soup.title else None
    text = soup.get_text(' ', strip=True)
    return {'url': str(response.url), 'status': response.status_code, 'title': title, 'content_hash': hashlib.sha256(text.encode()).hexdigest(), 'content_length': len(text)}
