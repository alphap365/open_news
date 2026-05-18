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
# FIX (Bug 4): keep the global for backward compat, but callers should prefer
#              passing config_path explicitly to avoid thread-safety issues.
CONFIG_PATH = os.environ.get("OPEN_NEWS_CONFIG", "config.json")


def set_config_path(path: str) -> None:
    """
    Set the global config path at runtime.

    WARNING: This mutates a module-level global and is NOT thread-safe.
    In multi-threaded or async contexts, pass `config_path` explicitly
    to load_rss_feeds_from_config() instead.
    """
    global CONFIG_PATH
    CONFIG_PATH = path


def load_rss_feeds_from_config(config_path: Optional[str] = None) -> Dict:
    """
    Load the full config dict from config.json (or the given path).

    Returns the parsed config dict, or {} on failure.
    Callers can pull 'rss_feeds' and 'max_articles_per_feed' from it directly,
    eliminating the need to re-read the file elsewhere.

    FIX (Bug 5 / Bug 9): config is loaded once and returned in full so that
    main.py can read both rss_feeds and max_articles_per_feed from a single
    parse — no second open("config.json") required.
    """
    path = config_path or CONFIG_PATH
    try:
        with open(path, "r") as f:
            config = json.load(f)
        feeds = config.get("rss_feeds", [])
        logger.info(f"Loaded {len(feeds)} RSS feeds from {path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Config file {path} not found, using empty config")
        return {}
    except Exception as e:
        logger.error(f"Error loading config from {path}: {e}")
        return {}


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
