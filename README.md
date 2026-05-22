<div align="center">

# 📰 open-news

**Zero-Config News Fetching & Article Extraction for Python**

[![License](https://img.shields.io/github/license/alphap365/open-news?style=for-the-badge&color=blue)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)](https://github.com/alphap365/open-news)

*A lightweight, batteries-included Python package for fetching news articles, extracting content, and discovering RSS feeds.*

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 🎯 Features

<table>
<tr>
<td>

### 📄 Article Extraction
Extract full text and rich metadata from any news article with a smart fallback pipeline:
- `newspaper4k` → `trafilatura` → BeautifulSoup
- Returns: title, text, publish date, source URL

</td>
<td>

### 📡 Live News Feeds
Access curated RSS feeds with zero local configuration:
- **50+ country-specific feeds** (India, USA, Pakistan, etc.)
- **Category feeds** (business, politics, geopolitics)
- Auto-updating via Git branch

</td>
</tr>
<tr>
<td>

### 🔍 Google News Search
Search across Google News with decoded URLs:
- Real article links (via `googlenewsdecoder`)
- Fallback to raw URLs if needed
- Rich metadata included

</td>
<td>

### 🔗 RSS Discovery
Auto-discover RSS feeds from any website:
- No external `feedfinder2` dependency
- Built with BeautifulSoup + lxml
- Fetch articles from discovered feeds instantly

</td>
</tr>
<tr>
<td colspan="2">

### ⚡ Smart Caching
24-hour feed caching to minimize network requests and improve performance

</td>
</tr>
</table>

---

## 📦 Installation

### From GitHub
```bash
git clone https://github.com/alphap365/open-news.git
cd open-news
pip install -e .
```

### Direct Install
```bash
pip install git+https://github.com/alphap365/open-news.git
```

**All dependencies installed automatically:**
- `newspaper4k` • `trafilatura` • `beautifulsoup4` • `lxml`
- `feedparser` • `googlenewsdecoder` • `httpx` • `requests`

---

## 🚀 Quick Start

### 1️⃣ Extract Article Content
```python
from open_news import fetch_article

article = fetch_article("https://www.bbc.com/news/world-us-canada-12345678")

print(article["title"])
print(article["text"][:500])
print(f"Source: {article['source']}")
print(f"Published: {article['publish_date']}")
```

### 2️⃣ Search Google News
```python
from open_news import search_news

results = search_news("artificial intelligence", limit=5)

for article in results:
    print(f"✓ {article['title']}")
    print(f"  → {article['url']}\n")
```

### 3️⃣ Get Live News (Country-Specific)
```python
from open_news import get_live_news

# Get top news from India
india_news = get_live_news(country="india", limit_per_feed=3)

for article in india_news:
    print(f"[{article['source']}] {article['title']}")
    print(f"Published: {article['published']}\n")
```

### 4️⃣ Get Category News
```python
# Business news from curated feeds
business = get_live_news(category="business", limit_per_feed=2)

for article in business:
    print(f"{article['title']}")
```

### 5️⃣ Discover & Fetch RSS Feeds
```python
from open_news import get_articles_from_website_rss

# Auto-discover RSS from any website
articles = get_articles_from_website_rss("https://techcrunch.com", limit=5)

for article in articles:
    print(f"✓ {article['title']}")
```

---

## 📚 API Reference

### `fetch_article(url: str) → Dict`

Extract article content and metadata from a given URL.

**Returns:**
```python
{
    "url": str,           # Original article URL
    "title": str,         # Article headline
    "text": str,          # Full article text
    "publish_date": str,  # ISO 8601 timestamp (or empty string)
    "source": str         # Website domain
}
```

**Example:**
```python
article = fetch_article("https://example.com/article")
if article["text"]:
    print(f"✓ Successfully extracted: {article['title']}")
else:
    print("✗ Could not extract article content")
```

---

### `search_news(query: str, limit: int = 10) → List[Dict]`

Search Google News for recent articles.

**Parameters:**
- `query` (str): Search terms
- `limit` (int): Maximum results to return (default: 10)

**Returns:**
```python
[
    {
        "title": str,
        "url": str,           # Decoded real URL (when possible)
        "source": str,
        "published": str,     # ISO 8601 timestamp
        "description": str
    },
    ...
]
```

**Example:**
```python
results = search_news("climate change", limit=5)
print(f"Found {len(results)} articles")
```

---

### `get_live_news(country: str = None, category: str = "news", limit_per_feed: int = None) → List[Dict]`

Fetch articles from curated RSS feeds.

**Parameters:**
- `country` (str, optional): Two-letter country code
  - Examples: `"india"`, `"usa"`, `"uk"`, `"pakistan"`
  - When set, `category` is ignored
- `category` (str): News category when no country specified
  - Options: `"news"`, `"business"`, `"politics"`, `"geopolitics"`
  - Default: `"news"`
- `limit_per_feed` (int, optional): Articles per feed (default from remote config)

**Returns:**
```python
[
    {
        "title": str,
        "url": str,
        "source": str,
        "published": str,
        "description": str
    },
    ...
]
```

**Examples:**
```python
# Country-specific
india_news = get_live_news(country="india", limit_per_feed=5)

# Category-specific
business = get_live_news(category="business")

# Default news
general = get_live_news()
```

---

### `get_articles_from_website_rss(website_url: str, limit: int = 10) → List[Dict]`

Discover and fetch articles from a website's RSS feed.

**Parameters:**
- `website_url` (str): Website homepage URL
- `limit` (int): Maximum articles to return

**Returns:** Same structure as `get_live_news()`

**Example:**
```python
articles = get_articles_from_website_rss("https://hackernews.com", limit=10)
for article in articles:
    print(f"• {article['title']}")
```

---

## 🗂️ How Feeds Are Maintained

Feed definitions are stored **in a separate Git branch** (`rss-feeds`) within the same repository. This allows:

✅ Independent feed updates without code changes  
✅ Version control for feed list history  
✅ Easy contributions for new feeds

**Feed location:**
```
https://raw.githubusercontent.com/alphap365/open-news/rss-feeds/feeds/
```

**Structure:**
```
feeds/
├── news.json              # General news feeds
├── business.json          # Business news feeds
├── politics.json          # Political news feeds
├── geopolitics.json       # Geopolitical analysis
└── country/
    ├── india.json         # India-specific feeds
    ├── usa.json           # USA-specific feeds
    └── ...                # Other countries
```

---

## 📡 RSS Feeds Directory

For detailed documentation on available RSS feeds, feed configuration, and how to contribute new feeds, see the [**RSS Feeds README**](rss-feeds/README.md).

### Available Feed Categories:

- **[General News](rss-feeds/README.md#general-news)** – Top news feeds across categories
- **[Business News](rss-feeds/README.md#business-news)** – Financial and business-focused feeds
- **[Politics](rss-feeds/README.md#politics)** – Political news and analysis
- **[Geopolitics](rss-feeds/README.md#geopolitics)** – International relations and geopolitical coverage
- **[Country-Specific](rss-feeds/README.md#country-specific-feeds)** – Feeds by country (India, USA, UK, Pakistan, etc.)

👉 **[View all available feeds →](rss-feeds/README.md)**

---

## ⚙️ Caching

Feeds are automatically cached for **24 hours** in `~/.open_news/feeds_cache/` to reduce network requests.

**Current implementation:** Cache is managed internally. Force refresh by clearing the cache directory if needed.

---

## 🔧 Requirements

- **Python:** 3.7+
- **Network:** Internet connection for live feeds

---

## 📝 License

Licensed under the **MIT License** – see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We'd love your contributions! Whether it's:
- 🐛 Bug reports
- ✨ Feature requests
- 📝 Documentation improvements
- 🔗 New feed suggestions
- 💻 Pull requests

Please check out our [Contributing Guide](CONTRIBUTING.md) before getting started.

**Ways to help:**
- Submit new feeds for the `rss-feeds` branch
- Improve article extraction quality
- Add language/region support
- Write tests and documentation
- Share and star the project ⭐

---

## 🙏 Acknowledgements

Built on the shoulders of amazing open-source projects:

- [**newspaper4k**](https://github.com/codelucas/newspaper) – Article extraction
- [**trafilatura**](https://github.com/adbar/trafilatura) – Content extraction
- [**feedparser**](https://github.com/kurtmckee/feedparser) – RSS parsing
- [**googlenewsdecoder**](https://github.com/HeiseL/GoogleNewsDecoder) – URL decoding
- [**BeautifulSoup4**](https://www.crummy.com/software/BeautifulSoup/) – HTML parsing
- [**lxml**](https://lxml.de/) – XML processing

---

<div align="center">

**Made with ❤️ by [Arajit Paul](https://github.com/alphap365)**

[⭐ Star us on GitHub](https://github.com/alphap365/open-news) | [📧 Email](mailto:dev.arajit.2010@gmail.com)

</div>
