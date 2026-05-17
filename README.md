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
  Query news via Google News RSS, automatically decode redirect URLs using `googlenewsdecoder`.

- **Discover RSS feed from any website**  
  Uses `feedfinder2` to find the RSS feed URL, then fetches articles from it.


## Installation

Clone this repository to your computer by using:

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

You can specify a custom config path at runtime (see examples).


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

Set the config path before calling any function:

```python
from open_news import get_live_news, set_config_path

set_config_path("/home/user/my_config.json")

# Now call any function – it will use your custom config
articles = get_live_news()
```

### Command-line test script

A test script is included in the repository (`test.py`) that demonstrates all features:

```bash
python test.py --config /path/to/config.json
```


## API Reference

### `fetch_article(url: str) -> Dict`
Returns:
```python
{
    "url": str,
    "title": str,
    "text": str,
    "publish_date": str,   # ISO format if available
    "source": str
}
```

### `search_news(query: str, limit: int = 10) -> List[Dict]`
Returns list of articles with keys: `title`, `url`, `source`, `published`, `description`.  
The `url` is already decoded to the original article link.

### `get_live_news(limit_per_feed: int = None) -> List[Dict]`
Fetches articles from all RSS feeds defined in `config.json`.  
Each article dict contains: `title`, `url`, `source`, `published`, `description`.

### `get_articles_from_website_rss(website_url: str, limit: int = 10) -> List[Dict]`
Discovers the RSS feed of `website_url` using `feedfinder2`, then fetches articles from it.  
Returns same structure as `get_live_news()`.


## Requirements

- Python 3.7+
- Internet connection for fetching articles and feeds


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
```