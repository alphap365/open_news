<p align="center">
    <!-- Add a stylish banner image here (recommended size: 1200x600px) -->
    <!-- <img src="banner.png" alt="open-news Banner" width="100%"> -->

<h1 align="center">📰 open_news</h1>

<p align="center">
    <strong>Zero‑config news fetching & article extraction in Python</strong>
</p>

<p align="center">
    <!-- CI Status Badge (You can find the correct URL in your repository's Actions settings) -->
    <a href="https://github.com/alphap365/open-news/actions">
        <img src="https://img.shields.io/github/actions/workflow/status/alphap365/open-news/ci.yml?style=flat-square&label=CI&logo=github-actions&logoColor=white" alt="CI">
    </a>
    <!-- License Badge -->
    <a href="https://github.com/alphap365/open-news/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/alphap365/open-news?style=flat-square" alt="License">
    </a>
    <!-- Python Version Badge -->
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.7%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python Version">
    </a>
    <!-- Optional: PyPI Downloads Badge (if the project is published on PyPI) -->
    <!--
    <a href="https://pypi.org/project/open-news/">
        <img src="https://img.shields.io/pypi/dm/open-news?style=flat-square&logo=pypi&logoColor=white" alt="PyPI Downloads">
    </a>
    -->
</p>

A lightweight Python package to fetch news articles, extract full text and metadata, retrieve RSS feeds, search Google News, and auto‑discover RSS feeds from any website.
No configuration file needed – feeds are curated in a separate Git branch and updated automatically.

## Features

- **Extract article text and metadata**  
  Uses `newspaper4k` → `trafilatura` → BeautifulSoup fallback pipeline.  
  Returns: `url`, `title`, `text`, `publish_date`, `source`.

- **Fetch live news from curated RSS feeds**  
  No local config file needed. Pre‑defined feeds are stored in a separate Git branch (`rss‑feeds`) and automatically updated.  
  Supports **country‑specific** (e.g., `india`, `usa`) and **category** (e.g., `business`, `politics`) feeds.

- **Search Google News**  
  Query news via Google News RSS. Redirect URLs are decoded using `googlenewsdecoder` where available, with automatic fallback to the raw redirect URL.

- **Discover RSS feed from any website**  
  Built‑in discovery using `BeautifulSoup` + `lxml` – no `feedfinder2` warnings.

- **Automatic caching**  
  Feeds are cached locally (24 hours by default) to reduce network requests.

## Installation

Clone this repository:

```bash
git clone https://github.com/alphap365/open-news.git
cd open-news
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/alphap365/open-news.git
```

**Dependencies** (automatically installed):

- `newspaper4k`
- `trafilatura`
- `beautifulsoup4`
- `lxml`
- `feedparser`
- `googlenewsdecoder`
- `httpx`
- `requests`

## Usage

### Basic examples

```python
from open_news import fetch_article, search_news, get_live_news, get_articles_from_website_rss

# 1. Fetch full article text and metadata
article = fetch_article("https://www.bbc.com/news/world-us-canada-12345678")
print(article["title"])
print(article["text"][:200])

# 2. Search Google News
results = search_news("climate change", limit=5)
for r in results:
    print(r["title"], r["url"])

# 3. Get live news from India (country-specific feeds)
india_news = get_live_news(country="india", limit_per_feed=3)
for art in india_news:
    print(f"{art['source']}: {art['title']}")

# 4. Get live news by category (business, politics, geopolitics, news)
business_news = get_live_news(category="business", limit_per_feed=2)

# 5. Discover RSS feed from a website and fetch its articles
articles = get_articles_from_website_rss("https://techcrunch.com", limit=3)
for a in articles:
    print(a["title"])
```

### Available parameters for `get_live_news()`

- `country` – two‑letter code for country‑specific feeds (e.g., `"india"`, `"usa"`, `"pakistan"`).  
  If provided, `category` is ignored.
- `category` – one of `"news"`, `"business"`, `"politics"`, `"geopolitics"`.  
  Defaults to `"news"` if no country is given.
- `limit_per_feed` – maximum articles per feed. Defaults to the value stored in the remote JSON (usually 8).

### Caching

Feeds are cached in `~/.open_news/feeds_cache/` for 24 hours.  
To force a refresh, set `use_cache=False` (not exposed in the high‑level function yet, but you can call `fetch_remote_feed_list` directly).

## How feeds are maintained

The feed definitions are stored **in the same repository** but in a separate branch: `rss‑feeds`.  
The package fetches them from:

```
https://raw.githubusercontent.com/alphap365/open-news/rss-feeds/feeds/
```

The branch contains JSON files like:
- `feeds/news.json` – general news
- `feeds/business.json`
- `feeds/country/india.json`
- `feeds/country/usa.json`

These files can be updated independently of the package code. An update script (`scripts/update_feeds.py` in the `rss‑feeds` branch) uses the package’s own `discover_rss_feed()` to refresh URLs periodically.

## API Reference

### `fetch_article(url: str) -> Dict`

Tries `newspaper4k`, then `trafilatura` (with metadata), then BeautifulSoup.  
All string fields are always present; `text` is an empty string on complete failure.

```python
{
    "url": str,
    "title": str,
    "text": str,
    "publish_date": str,   # ISO 8601 if available, else ""
    "source": str
}
```

### `search_news(query: str, limit: int = 10) -> List[Dict]`

Searches Google News RSS. URLs are decoded to the real article link where possible; if decoding fails or `googlenewsdecoder` is not installed, the raw redirect URL is returned instead of dropping the article.

Returns list of dicts with keys: `title`, `url`, `source`, `published`, `description`.

### `get_live_news(country: str = None, category: str = "news", limit_per_feed: int = None) -> List[Dict]`

Fetches articles from the remote feed list. If `country` is given, ignores `category` and loads from `feeds/country/<country>.json`. Otherwise loads from `feeds/<category>.json`.  
Each article dict: `title`, `url`, `source`, `published`, `description`.

### `get_articles_from_website_rss(website_url: str, limit: int = 10) -> List[Dict]`

Discovers the RSS feed of `website_url` using the built‑in discovery (no external `feedfinder2`), then fetches articles. Returns the same structure as `get_live_news()`.

## Requirements

- Python 3.8+
- Internet connection

## License

MIT – see [LICENSE](LICENSE) file.

## Contributing

Contributions are welcome! Whether it’s a bug report, a feature request, or a pull request, please check out our [Contributing Guide](CONTRIBUTING.md) before getting started.

We appreciate all kinds of help – code, documentation, testing, or even just spreading the word. 🚀

## Acknowledgements

Built on the shoulders of:
- [newspaper4k](https://github.com/codelucas/newspaper)
- [trafilatura](https://github.com/adbar/trafilatura)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [googlenewsdecoder](https://github.com/HeiseL/GoogleNewsDecoder)
