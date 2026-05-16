"""Discover RSS feeds from a website URL and load feeds from config.json."""

import os
import json
import logging
from typing import List, Dict, Optional

try:
    import feedfinder2
except ImportError:
    feedfinder2 = None

logger = logging.getLogger(__name__)

# Allow override via environment variable OPEN_NEWS_CONFIG
CONFIG_PATH = os.environ.get("OPEN_NEWS_CONFIG", "config.json")

def set_config_path(path: str):
    """Set the path to config.json at runtime."""
    global CONFIG_PATH
    CONFIG_PATH = path

def load_rss_feeds_from_config() -> List[Dict]:
    """Load RSS feed list from config.json (key 'rss_feeds'). Each dict: name, url."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        feeds = config.get("rss_feeds", [])
        logger.info(f"Loaded {len(feeds)} RSS feeds from config")
        return feeds
    except FileNotFoundError:
        logger.warning(f"Config file {CONFIG_PATH} not found, using empty feed list")
        return []
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return []

def discover_rss_feed(website_url: str) -> Optional[str]:
    """
    Use feedfinder2 to discover RSS feed URL from a website.
    Returns first feed URL or None.
    """
    if not feedfinder2:
        logger.warning("feedfinder2 not installed, cannot auto-discover RSS")
        return None
    try:
        feeds = feedfinder2.find_feeds(website_url)
        if feeds:
            logger.info(f"Found RSS feed for {website_url}: {feeds[0]}")
            return feeds[0]
        else:
            logger.info(f"No RSS feed found for {website_url}")
            return None
    except Exception as e:
        logger.error(f"Feed discovery failed for {website_url}: {e}")
        return None
