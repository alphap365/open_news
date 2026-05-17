"""High-level endpoints: fetch article, search news, live news from config, RSS from website."""

import json
import logging
from typing import List, Dict, Optional

from .get_article import fetch_article as _fetch_article
from .get_url import get_urls_from_rss_feed, get_urls_from_google_news_search
from .get_rss import load_rss_feeds_from_config, discover_rss_feed

logger = logging.getLogger(__name__)

def fetch_article(url: str) -> Dict:
    """
    Fetch full article text and metadata.
    Returns dict with keys: url, title, text, publish_date, source.
    """
    return _fetch_article(url)

def search_news(query: str, limit: int = 10) -> List[Dict]:
    """
    Search Google News for a query.
    Returns list of article dicts (title, url, source, published, description).
    Note: Full text not included; use fetch_article(url) on each url to get content.
    """
    return get_urls_from_google_news_search(query, limit)

def get_live_news(limit_per_feed: Optional[int] = None) -> List[Dict]:
    """
    Fetch articles from all RSS feeds defined in config.json.
    limit_per_feed: max articles per feed (default from config or 8).
    Returns list of article dicts (title, url, source, published, description).
    """
    feeds = load_rss_feeds_from_config()
    if not feeds:
        logger.warning("No RSS feeds configured in config.json")
        return []

    # Determine limit per feed
    if limit_per_feed is None:
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            limit_per_feed = config.get("max_articles_per_feed", 8)
        except:
            limit_per_feed = 8

    all_articles = []
    for feed in feeds:
        feed_url = feed.get("url")
        if not feed_url:
            continue
        articles = get_urls_from_rss_feed(feed_url, limit=limit_per_feed)
        # Optionally override source with configured name
        if feed.get("name"):
            for art in articles:
                art["source"] = feed["name"]
        all_articles.extend(articles)
    logger.info(f"Total live news articles fetched: {len(all_articles)}")
    return all_articles

def get_articles_from_website_rss(website_url: str, limit: int = 10) -> List[Dict]:
    """
    Discover RSS feed from a website URL, then fetch articles from that feed.
    Returns list of article dicts (same as from get_urls_from_rss_feed).
    """
    rss_url = discover_rss_feed(website_url)
    if not rss_url:
        logger.warning(f"Could not discover RSS feed for {website_url}")
        return []
    return get_urls_from_rss_feed(rss_url, limit)
