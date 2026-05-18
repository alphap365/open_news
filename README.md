# open_news

A minimal, modular Python package to fetch news articles, extract full text and metadata, retrieve RSS feeds, search Google News, and auto‑discover RSS feeds from any website.

Designed to be lightweight and easy to integrate.


## Features

- **Extract article text and metadata**  
  Uses `newspaper4k` → `trafilatura` → BeautifulSoup fallback pipeline.  
  Returns: `url`, `title`, `text`, `publish_date`, `source`.

- **Fetch live news from RSS feeds**  
  Load feeds from `config.json`. Returns articles with title, URL, source, publish date, and description.

- **Search Google News**  
  Query news via Google News RSS. Redirect URLs are decoded using `googlenewsdecoder` where available, with automatic fallback to the raw redirect URL.

- **Discover RSS feed from any website**  
  Uses `feedfinder2` to find the RSS feed URL, then fetches articles from it.


## Installation

Clone this repository:

```bash
git clone https://github.com/alphap365/open-news.git
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
- `feedfinder2`
- `googlenewsdecoder`
- `httpx`


## Configuration

Create a `config.json` file (default path) with your RSS feeds and limits:

```json
{
    "rss_feeds": [
        {
            "name": "BBC News",
            "url": "http://feeds.bbci.co.uk/news/rss.xml"
        },
        {
            "name": "CNN Top Stories",
            "url": "http://rss.cnn.com/rss/edition.rss"
        }
    ],
    "max_articles_per_feed": 8,
    "search_limit": 10
}
```

You can specify a custom config path at runtime (see examples below).


## Usage

### Basic example

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

# 3. Get live news from configured RSS feeds
live = get_live_news()
for art in live:
    print(f"{art['source']}: {art['title']}")

# 4. Discover RSS feed from a website and fetch its articles
articles = get_articles_from_website_rss("https://techcrunch.com", limit=3)
for a in articles:
    print(a["title"])
```

### Using a custom config file

Pass the path explicitly (preferred — thread-safe):

```python
from open_news import get_live_news
from open_news.get_rss import load_rss_feeds_from_config

config = load_rss_feeds_from_config("/home/user/my_config.json")
articles = get_live_news()
```

Or set a global config path (single-threaded use only):

```python
from open_news import set_config_path, get_live_news

# NOTE: set_config_path mutates a global and is not thread-safe.
# Prefer passing config_path explicitly in multi-threaded contexts.
set_config_path("/home/user/my_config.json")
articles = get_live_news()
```

### Command-line test script

```bash
python test.py --config /path/to/config.json
```


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

Searches Google News RSS. URLs are decoded to the real article link where possible;
if decoding fails or `googlenewsdecoder` is not installed, the raw redirect URL is
returned instead of dropping the article.

Returns list of dicts with keys: `title`, `url`, `source`, `published`, `description`.

### `get_live_news(limit_per_feed: int = None) -> List[Dict]`

Fetches articles from all RSS feeds in `config.json`. `limit_per_feed` defaults to
`max_articles_per_feed` from config, or `8` if not set. Config is read once per call.

Each article dict: `title`, `url`, `source`, `published`, `description`.

### `get_articles_from_website_rss(website_url: str, limit: int = 10) -> List[Dict]`

Discovers the RSS feed of `website_url` using `feedfinder2`, then fetches articles.  
Returns the same structure as `get_live_news()`.

### `set_config_path(path: str) -> None`

Sets the global config path. **Not thread-safe** — use the explicit `config_path`
parameter on `load_rss_feeds_from_config()` in concurrent contexts.


## Requirements

- Python 3.8+
- Internet connection


## License

MIT – see [LICENSE](LICENSE) file.


## Contributing

Pull requests and issues are welcome. Keep the module minimal – no caching, summarization, or grouping.


## Acknowledgements

Built on the shoulders of:
- [newspaper4k](https://github.com/codelucas/newspaper)
- [trafilatura](https://github.com/adbar/trafilatura)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [feedfinder2](https://github.com/DF7CB/feedfinder2)
- [googlenewsdecoder](https://github.com/HeiseL/GoogleNewsDecoder)
