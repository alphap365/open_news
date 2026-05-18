"""Retrieve article URLs and basic metadata from RSS feeds or Google News search."""

import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlparse  # FIX (Bug 6): top-level import, not inside loop

import feedparser
from bs4 import BeautifulSoup

try:
    from googlenewsdecoder import new_decoderv1
except ImportError:
    new_decoderv1 = None

logger = logging.getLogger(__name__)


def decode_google_news_url(url: str) -> Optional[str]:
    """Decode a Google News redirect URL to the original article URL."""
    if not new_decoderv1:
        logger.warning("googlenewsdecoder not installed, cannot decode URLs")
        return None
    try:
        result = new_decoderv1(url)
        if result and result.get("decoded_url"):
            return result["decoded_url"]
        else:
            logger.debug(f"Decoder returned no URL for {url[:80]}")
            return None
    except Exception as e:
        logger.error(f"Failed to decode Google News URL: {e}")
        return None


def get_urls_from_rss_feed(feed_url: str, limit: int = 10) -> List[Dict]:
    """
    Parse an RSS feed and return a list of article dicts with keys:
    title, url, source (feed name), published, description.
    """
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            title = entry.get("title", "No title")
            link = entry.get("link", "")
            if not link:
                continue
            published = entry.get("published", entry.get("pubDate", ""))
            description = entry.get("description", entry.get("summary", ""))
            if description:
                soup = BeautifulSoup(description, "html.parser")
                description = soup.get_text()
            source = feed.feed.get("title", "Unknown RSS")
            articles.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": published,
                    "description": description[:500],
                }
            )
        logger.info(f"Fetched {len(articles)} articles from RSS {feed_url}")
    except Exception as e:
        logger.error(f"Error fetching RSS {feed_url}: {e}")
    return articles


def get_urls_from_google_news_search(query: str, limit: int = 10) -> List[Dict]:
    """
    Search Google News RSS, decode redirect URLs, and return article dicts.
    Keys: title, url (decoded or raw fallback), source, published, description.

    FIX (Bug 8): when googlenewsdecoder is missing or decoding fails, the raw
    redirect URL is used as a fallback instead of silently dropping the article.
    """
    encoded_query = quote_plus(query)
    search_url = (
        f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    )
    articles = []
    try:
        feed = feedparser.parse(search_url)
        for entry in feed.entries[:limit]:
            title = entry.get("title", "No title")
            redirect_url = entry.get("link", "")
            if not redirect_url:
                continue

            # FIX (Bug 8): fall back to the raw redirect URL instead of skipping
            real_url = decode_google_news_url(redirect_url)
            if not real_url:
                logger.debug(
                    f"Could not decode URL for '{title}'; using raw redirect URL"
                )
                real_url = redirect_url

            # Extract source from feed's source element, title suffix, or domain
            source = entry.get("source", {}).get("title", "")
            if not source and " - " in title:
                # Google News title format: "Headline - Publisher Name"
                source = title.split(" - ")[-1]
            if not source and real_url:
                domain = urlparse(real_url).netloc  # FIX (Bug 6): no longer imported here
                source = domain.replace("www.", "").split(".")[0].title()

            published = entry.get("published", "")
            description = entry.get("description", entry.get("summary", ""))
            if description:
                soup = BeautifulSoup(description, "html.parser")
                description = soup.get_text()
            articles.append(
                {
                    "title": title,
                    "url": real_url,
                    "source": source or "Google News",
                    "published": published,
                    "description": description[:500],
                }
            )
        logger.info(f"Search '{query}' returned {len(articles)} articles")
    except Exception as e:
        logger.error(f"Google News search error: {e}")
    return articles
