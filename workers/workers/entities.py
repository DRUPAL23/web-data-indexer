import re

ENTITY_RE = re.compile(r'\b(?:[A-Z][\w.-]+(?:\s+[A-Z][\w.-]+){0,3})\b')


def extract_entities(title: str | None, content: str, max_entities: int = 50) -> list[str]:
    text = f'{title or ""}. {content[:12000]}'
    result, seen = [], set()
    for match in ENTITY_RE.findall(text):
        value = ' '.join(match.split()).strip('.,:;()[]{}')
        if len(value) < 3 or value.casefold() in {'the', 'this', 'that', 'web data'}:
            continue
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
        if len(result) >= max_entities:
            break
    return result
