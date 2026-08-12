import httpx
from bs4 import BeautifulSoup


def fetch_html(url: str, user_agent: str, timeout: float, max_bytes: int):
    headers = {'User-Agent': user_agent, 'Accept': 'text/html,application/xhtml+xml'}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        with client.stream('GET', url) as response:
            response.raise_for_status()
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
                raise ValueError(f'Unsupported content type: {content_type}')
            chunks, total = [], 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError('Response exceeds crawler byte limit')
                chunks.append(chunk)
            raw = b''.join(chunks)
            encoding = response.encoding or 'utf-8'
            html = raw.decode(encoding, errors='replace')
            status = response.status_code

    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'template']):
        tag.decompose()
    title = soup.title.get_text(' ', strip=True) if soup.title else ''
    text = soup.get_text(' ', strip=True)
    return title, text, status
