from .celery_app import celery
import requests
from bs4 import BeautifulSoup

@celery.task(bind=True)
def crawl_url(self, url):
    """Simple crawler task — fetches URL and extracts title/text.
    In production replace with a robust harvester and polite rate limiting.
    """
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else ""
        # Extracted content should be sent to the DB / processing pipeline
        return {"url": url, "title": title}
    except Exception as e:
        # Celery will capture exceptions; in production add retries & backoff
        return {"url": url, "error": str(e)}
