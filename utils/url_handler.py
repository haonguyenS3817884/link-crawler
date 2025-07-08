from urllib.parse import urlparse

def get_domain(url: str) -> str:
    return urlparse(url).netloc

def get_domain_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"