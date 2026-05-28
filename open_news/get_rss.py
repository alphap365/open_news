#!/usr/bin/env python3
"""
RSS feed handling: remote feed lists (from open-feeds repo), discovery, caching.
No config.json dependency.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Remote base URL for raw JSON files (open-feeds repository)
REMOTE_BASE = "https://raw.githubusercontent.com/alphap365/open-feeds/main/feeds"

# Cache directory
CACHE_DIR = os.path.expanduser("~/.open_news/feeds_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# TTL for cache (24 hours)
CACHE_TTL = 24 * 3600

def _get_cache_path(category: str, country: Optional[str] = None) -> str:
    """Return cache file path for a given category/country."""
    if country:
        filename = f"country_{country}.json"
    else:
        filename = f"{category}.json"
    return os.path.join(CACHE_DIR, filename)

def fetch_remote_feed_list(category: str = "news", country: Optional[str] = None, use_cache: bool = True) -> Dict:
    """
    Fetch feed JSON from the open-feeds repository.
    
    Args:
        category: 'news', 'business', 'politics', 'geopolitics' or any top-level JSON.
        country: if provided, fetches from feeds/country/<country>.json (e.g., 'india', 'usa').
        use_cache: if True, use cached copy if not expired.
    
    Returns:
        Dict with keys: 'feeds', 'max_articles_per_feed', etc.
    """
    cache_path = _get_cache_path(category, country)
    
    # Try cache
    if use_cache and os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            cached_time = data.get('_cached_at', 0)
            if time.time() - cached_time < CACHE_TTL:
                logger.debug(f"Using cached feed list for {category}/{country}")
                return data
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
    
    # Construct remote URL
    if country:
        url = f"{REMOTE_BASE}/country/{country}.json"
    else:
        url = f"{REMOTE_BASE}/{category}.json"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Add cache timestamp
        data['_cached_at'] = time.time()
        # Save to cache
        with open(cache_path, 'w') as f:
            json.dump(data, f)
        logger.info(f"Fetched fresh feed list from {url}")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        # Fallback to stale cache if available
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                data = json.load(f)
            logger.warning(f"Using stale cache for {category}/{country}")
            return data
        return {"feeds": [], "max_articles_per_feed": 8}

def discover_rss_feed(website_url: str) -> Optional[str]:
    """
    Find RSS/Atom feed URL from a website using BeautifulSoup.
    No feedfinder2 dependency, explicit lxml parser → no warnings.
    """
    try:
        headers = {"User-Agent": "open_news/1.0 (https://github.com/alphap365/open-news)"}
        resp = requests.get(website_url, timeout=10, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")  # explicit parser
        
        # Look for link tags with feed types
        for link in soup.find_all("link", type=["application/rss+xml", "application/atom+xml"]):
            href = link.get("href")
            if href:
                return urljoin(website_url, href)
        
        # Fallback: look for <a> with feed/rss in href
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if "feed" in href or "rss" in href or "atom" in href:
                return urljoin(website_url, a["href"])
        return None
    except Exception as e:
        logger.debug(f"Discovery failed for {website_url}: {e}")
        return None
