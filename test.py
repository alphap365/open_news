#!/usr/bin/env python3
"""
test.py - Test the open_news package with custom config file.
Usage: python test.py --config /path/to/config.json
"""

import argparse
import sys
import json

# Import package functions
from open-news import fetch_article, search_news, get_live_news, get_articles_from_website_rss, set_config_path



def main():
    parser = argparse.ArgumentParser(description="Test open_news package with custom config")
    parser.add_argument("--config", default="config.json",
                        help="Path to config.json (default: config.json)")
    args = parser.parse_args()

    # Set the configuration path used by the package
    set_config_path(args.config)
    print(f"Using config file: {args.config}")

    # Optional: verify config loads
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
        print("Config loaded successfully:", list(config.keys()))
    except Exception as e:
        print(f"Warning: Could not read config file: {e}")

    # ---------------------- Test 1: Live news from RSS feeds ----------------------
    print("\n--- 1. Fetching live news from configured RSS feeds ---")
    live_articles = get_live_news()
    print(f"Total articles: {len(live_articles)}")
    for i, art in enumerate(live_articles[:5], 1):
        print(f"{i}. [{art['source']}] {art['title']}")
        print(f"   URL: {art['url']}")
        print(f"   Published: {art['published']}")
        print(f"   Description: {art['description'][:150]}...\n")

    # ---------------------- Test 2: Search Google News ----------------------
    print("\n--- 2. Searching Google News for 'AI' ---")
    search_query = "AI"
    search_results = search_news(search_query, limit=5)
    print(f"Found {len(search_results)} articles")
    for i, art in enumerate(search_results, 1):
        print(f"{i}. {art['title']} ({art['source']})")
        print(f"   URL: {art['url']}")
        print(f"   Published: {art['published']}\n")

    # ---------------------- Test 3: Fetch full article text ----------------------
    if search_results:
        print("--- 3. Fetching full text of first search result ---")
        first_url = search_results[0]['url']
        print(f"URL: {first_url}")
        article_data = fetch_article(first_url)
        print(f"Title: {article_data['title']}")
        print(f"Publish date: {article_data['publish_date']}")
        print(f"Source: {article_data['source']}")
        print(f"Text preview: {article_data['text'][:300]}...\n")

    # ---------------------- Test 4: Discover RSS from a website ----------------------
    print("--- 4. Discovering RSS feed from a website (TechCrunch) ---")
    website = "https://techcrunch.com"
    rss_articles = get_articles_from_website_rss(website, limit=3)
    print(f"Discovered RSS feed for {website}, fetched {len(rss_articles)} articles")
    for i, art in enumerate(rss_articles, 1):
        print(f"{i}. {art['title']} ({art['source']})")
        print(f"   URL: {art['url']}\n")


if __name__ == "__main__":
    main()