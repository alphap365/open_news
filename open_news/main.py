"""High-level endpoints: fetch article, search news, live news from remote feeds."""

import logging
from typing import List, Dict, Optional

from .get_article import fetch_article as _fetch_article
from .get_url import get_urls_from_rss_feed, get_urls_from_google_news_search
from .get_rss import fetch_remote_feed_list

logger = logging.getLogger(__name__)

def fetch_article(url: str) -> Dict:
    """Fetch full article text and metadata."""
    return _fetch_article(url)

def search_news(query: str, limit: int = 10) -> List[Dict]:
    """Search Google News for a query."""
    return get_urls_from_google_news_search(query, limit)

def get_live_news(category: str = "news", country: Optional[str] = None, limit_per_feed: Optional[int] = None) -> List[Dict]:
    """
    Fetch articles from RSS feeds defined in the remote feed list (rss-feeds branch).
    
    Args:
        category: 'news', 'business', 'politics', 'geopolitics' (or any top-level JSON).
        country: if provided, overrides category and fetches from feeds/country/<country>.json.
        limit_per_feed: max articles per feed (default from remote JSON or 8).
    
    Returns:
        List of article dicts with keys: title, url, source, published, description.
    """
    # Fetch feed list
    if country:
        feed_data = fetch_remote_feed_list(category="news", country=country.lower())
    else:
        feed_data = fetch_remote_feed_list(category=category)
    
    feeds = feed_data.get("feeds", [])
    if not feeds:
        logger.warning(f"No feeds found for category={category}, country={country}")
        return []
    
    limit = limit_per_feed or feed_data.get("max_articles_per_feed", 8)
    
    all_articles = []
    for feed in feeds:
        feed_url = feed.get("url")
        feed_name = feed.get("name", "Unknown")
        if not feed_url:
            continue
        articles = get_urls_from_rss_feed(feed_url, limit=limit)
        # Override source name with the one from feed list
        for art in articles:
            art["source"] = feed_name
        all_articles.extend(articles)
    
    logger.info(f"Fetched {len(all_articles)} articles from {len(feeds)} feeds")
    return all_articles

def get_articles_from_website_rss(website_url: str, limit: int = 10) -> List[Dict]:
    """
    Discover RSS feed from a website URL, then fetch articles from that feed.
    Uses custom discovery (no feedfinder2).
    """
    from .get_rss import discover_rss_feed
    rss_url = discover_rss_feed(website_url)
    if not rss_url:
        logger.warning(f"Could not discover RSS feed for {website_url}")
        return []
    return get_urls_from_rss_feed(rss_url, limit)