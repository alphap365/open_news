"""Fetch full article text and metadata using newspaper4k, trafilatura, or BeautifulSoup fallback."""

import logging
from typing import Dict, Optional, Tuple

try:
    from newspaper import Article
except ImportError:
    Article = None
try:
    import trafilatura
except ImportError:
    trafilatura = None
from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)

def _extract_with_newspaper(url: str) -> Tuple[str, Dict]:
    """Return (text, metadata). Metadata dict may contain title, publish_date, source."""
    if not Article:
        return "", {}
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text or ""
        meta = {
            "title": article.title or "",
            "publish_date": article.publish_date.isoformat() if article.publish_date else "",
            "source": article.source_url or "",
        }
        return text, meta
    except Exception as e:
        logger.debug(f"newspaper failed for {url}: {e}")
        return "", {}

def _extract_with_trafilatura(url: str) -> Tuple[str, Dict]:
    """Return (text, {}) – no metadata from trafilatura alone."""
    if not trafilatura:
        return "", {}
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text or "", {}
    except Exception as e:
        logger.debug(f"trafilatura failed for {url}: {e}")
    return "", {}

def _extract_with_bs4(url: str) -> Tuple[str, Dict]:
    """Fallback: extract text and try to guess title from HTML."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'lxml')
            # remove noisy tags
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator='\n')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # try to get title from <title> tag
            title = ""
            if soup.title:
                title = soup.title.get_text(strip=True)
            meta = {"title": title, "publish_date": "", "source": ""}
            return text, meta
    except Exception as e:
        logger.debug(f"bs4 fallback failed for {url}: {e}")
        return "", {}

def fetch_article(url: str) -> Dict:
    """
    Fetch full article content and metadata.
    Returns dict with keys: url, title, text, publish_date, source.
    """
    logger.info(f"Fetching article: {url}")

    # Try newspaper (gives best metadata)
    text, meta = _extract_with_newspaper(url)
    if text and len(text) > 200:
        logger.debug("newspaper4k success")
        return {
            "url": url,
            "title": meta.get("title", ""),
            "text": text,
            "publish_date": meta.get("publish_date", ""),
            "source": meta.get("source", "")
        }

    # Try trafilatura
    text, _ = _extract_with_trafilatura(url)
    if text and len(text) > 200:
        logger.debug("trafilatura success")
        # If trafilatura succeeded, try to get title with a quick bs4 fallback
        _, fallback_meta = _extract_with_bs4(url)  # only for title
        return {
            "url": url,
            "title": fallback_meta.get("title", ""),
            "text": text,
            "publish_date": "",
            "source": ""
        }

    # Fallback to bs4
    text, bs4_meta = _extract_with_bs4(url)
    if text and len(text) > 200:
        logger.debug("bs4 fallback success")
        return {
            "url": url,
            "title": bs4_meta.get("title", ""),
            "text": text,
            "publish_date": "",
            "source": ""
        }

    logger.warning(f"All extraction methods failed for {url}")
    return {"url": url, "title": "", "text": "", "publish_date": "", "source": ""}