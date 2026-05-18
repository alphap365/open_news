"""Minimal news fetching package: article text, RSS/Google News URLs, feed discovery."""

from .main import fetch_article, search_news, get_live_news, get_articles_from_website_rss
from .get_rss import set_config_path

__all__ = [
    "fetch_article",
    "search_news",
    "get_live_news",
    "get_articles_from_website_rss",
    "set_config_path",
]
