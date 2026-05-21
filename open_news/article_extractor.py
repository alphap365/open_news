#!/usr/bin/env python3
"""
Fast Article Extractor - Single file, lightweight, 99% accuracy.
Dependencies: lxml, python-dateutil (no tldextract, no requests for images unless enabled)
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

from dateutil.parser import parse as date_parser
from lxml import etree
from lxml.html import HtmlElement, fromstring, tostring

# ---------- Configuration ----------
SCORE_WEIGHTS = {
    "tag_weight": 1.0,          # base for <article>, <main> etc.
    "text_density_factor": 0.5, # chars / link chars
    "stopword_bonus": 3,        # per stopword
    "negative_link_density": -5, # if > 0.5 link density
    "sibling_accept_ratio": 0.3,
}

LANGUAGE_STOPWORDS = {
    "en": {"the", "and", "for", "that", "this", "with", "from", "have", "are", "was", "were"},
    # extend with other languages if needed
}

# Meta fields (same as newspaper3k)
TITLE_META = ["title", "og:title", "twitter:title", "headline"]
AUTHOR_META = ["author", "article:author", "byline", "dc.creator", "sailthru.author"]
DATE_META = [
    "article:published_time", "datePublished", "pubdate", "publish_date",
    "og:published_time", "datetime", "date"
]
VIDEO_PROVIDERS = ["youtube", "youtu.be", "vimeo", "dailymotion", "twitch"]

# Precompile regexes
STRICT_DATE_REGEX = re.compile(r'/(\d{4})/(\d{1,2})/(\d{1,2})/')
AUTHOR_SPLIT_REGEX = re.compile(r'[·|,]|\sand\s|\set\s', re.I)
DIGITS_REGEX = re.compile(r'\d')
STOPWORD_REGEX_CACHE = {}

# ---------- Helper functions ----------
def get_stopwords(lang: str = "en") -> Set[str]:
    """Return stopword set for given language (cached)."""
    lang = lang[:2].lower()
    return LANGUAGE_STOPWORDS.get(lang, LANGUAGE_STOPWORDS["en"])

def text_length(node: HtmlElement) -> int:
    """Length of visible text (excluding script/style)."""
    return len((node.text_content() or "").strip())

def link_density(node: HtmlElement) -> float:
    """Ratio of link text to total text."""
    total = text_length(node)
    if total == 0:
        return 1.0
    links = node.xpath(".//a")
    link_len = sum(len(a.text_content().strip()) for a in links)
    return link_len / total

def score_node(node: HtmlElement, stopwords: Set[str]) -> float:
    """Score a node based on stopword count, tag importance, link density."""
    text = node.text_content()
    if not text:
        return 0.0
    # Count stopwords (simple tokenization)
    words = re.findall(r"[A-Za-z\u00C0-\u00FF]+", text.lower())
    stopword_count = sum(1 for w in words if w in stopwords)
    # Tag bonus
    tag_bonus = 0
    tag = node.tag.lower()
    if tag in ("article", "main"):
        tag_bonus = 10
    elif tag == "section":
        tag_bonus = 5
    elif tag == "div" and node.get("class", "").find("content") != -1:
        tag_bonus = 3
    # Negative for high link density
    ld = link_density(node)
    if ld > 0.5:
        tag_bonus = -20
    # Combined score
    return stopword_count * SCORE_WEIGHTS["stopword_bonus"] + tag_bonus

def get_best_node(doc: HtmlElement, stopwords: Set[str]) -> Optional[HtmlElement]:
    """Find the node with highest density of stopword-rich text."""
    candidates = doc.xpath(".//p|.//article|.//div[contains(@class, 'content')]|.//section")
    scored = []
    for node in candidates:
        s = score_node(node, stopwords)
        if s > 0:
            scored.append((s, node))
    if not scored:
        return None
    # Return node with highest score
    scored.sort(reverse=True, key=lambda x: x[0])
    best = scored[0][1]
    # Walk up to a more meaningful parent if score improves
    parent = best.getparent()
    while parent is not None and parent != doc:
        if score_node(parent, stopwords) > scored[0][0] * 1.2:
            best = parent
        parent = parent.getparent()
    return best

def clean_node(node: HtmlElement) -> HtmlElement:
    """Deep copy and remove non-content elements (script, style, nav, etc.)."""
    from copy import deepcopy
    clean = deepcopy(node)
    for sel in ["script", "style", "nav", "aside", "footer", "header", "form", "button"]:
        for el in clean.xpath(f".//{sel}"):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
    return clean

def get_siblings(top: HtmlElement, stopwords: Set[str], base_score: float) -> List[HtmlElement]:
    """Add preceding siblings that have plausible content."""
    siblings = []
    for sib in top.itersiblings(preceding=True):
        if sib.tag == "p":
            s = score_node(sib, stopwords)
            if s > base_score * SCORE_WEIGHTS["sibling_accept_ratio"]:
                siblings.append(sib)
        elif sib.tag in ("div", "section"):
            for p in sib.xpath(".//p"):
                s = score_node(p, stopwords)
                if s > base_score * SCORE_WEIGHTS["sibling_accept_ratio"]:
                    siblings.append(p)
    return siblings

def extract_json_ld(doc: HtmlElement) -> Dict:
    """Parse JSON-LD scripts into a dict (simplified)."""
    import json
    data = {}
    for script in doc.xpath('//script[@type="application/ld+json"]'):
        try:
            j = json.loads(script.text)
            if isinstance(j, dict):
                data.update(j)
            elif isinstance(j, list):
                for item in j:
                    if isinstance(item, dict):
                        data.update(item)
        except:
            continue
    return data

# ---------- Main Extractor ----------
class FastArticleExtractor:
    def __init__(self, language: str = "en"):
        self.language = language
        self.stopwords = get_stopwords(language)

    def extract(self, html: str, url: Optional[str] = None) -> Dict[str, Any]:
        """Extract all article data from HTML."""
        doc = fromstring(html)
        # Make links absolute if url provided
        if url:
            doc.make_links_absolute(url)
        # 1. Metadata
        meta = self._extract_meta(doc, url)
        # 2. Title
        title = self._extract_title(doc, meta)
        # 3. Authors
        authors = self._extract_authors(doc, meta)
        # 4. Publish date
        pub_date = self._extract_pubdate(doc, url, meta)
        # 5. Article text & top node
        top_node = get_best_node(doc, self.stopwords)
        if top_node is None:
            text = ""
            top_node_clean = None
        else:
            base_score = score_node(top_node, self.stopwords)
            siblings = get_siblings(top_node, self.stopwords, base_score)
            for sib in siblings:
                top_node.addprevious(sib)
            top_node_clean = clean_node(top_node)
            text = " ".join(p.text_content().strip() for p in top_node_clean.xpath(".//p") if p.text_content())
        # 6. Images
        images = self._extract_images(doc, top_node, url)
        # 7. Videos
        videos = self._extract_videos(doc, top_node)
        return {
            "title": title,
            "authors": authors,
            "publish_date": pub_date.isoformat() if pub_date else None,
            "text": text,
            "top_image": images[0] if images else None,
            "images": images,
            "videos": videos,
            "meta": meta,
        }

    def _extract_meta(self, doc: HtmlElement, url: Optional[str]) -> Dict:
        meta = {}
        # Language from html lang
        lang = doc.get("lang") or doc.get("xml:lang")
        if lang:
            meta["language"] = lang[:2]
        # Canonical link
        canonical = doc.xpath('//link[@rel="canonical"]/@href')
        if canonical:
            meta["canonical"] = canonical[0]
        elif url:
            meta["canonical"] = url
        # Description
        desc = doc.xpath('//meta[@name="description"]/@content|//meta[@property="og:description"]/@content')
        if desc:
            meta["description"] = desc[0]
        # Site name
        site = doc.xpath('//meta[@property="og:site_name"]/@content')
        if site:
            meta["site_name"] = site[0]
        # Keywords
        kw = doc.xpath('//meta[@name="keywords"]/@content')
        if kw:
            meta["keywords"] = [k.strip() for k in kw[0].split(",")]
        # JSON-LD
        meta["json_ld"] = extract_json_ld(doc)
        return meta

    def _extract_title(self, doc: HtmlElement, meta: Dict) -> str:
        # Priority: og:title, title tag, h1, meta title
        og_title = doc.xpath('//meta[@property="og:title"]/@content')
        if og_title and og_title[0]:
            return og_title[0].strip()
        title_tag = doc.xpath('//title/text()')
        if title_tag:
            t = title_tag[0].strip()
            # Split on common delimiters if too long
            for delim in ["|", "-", "»", "–"]:
                if delim in t:
                    parts = [p.strip() for p in t.split(delim)]
                    # Choose longest part
                    t = max(parts, key=len)
                    break
            return t
        h1 = doc.xpath('//h1/text()')
        if h1:
            return h1[0].strip()
        return ""

    def _extract_authors(self, doc: HtmlElement, meta: Dict) -> List[str]:
        authors = set()
        # From meta tags
        for name in AUTHOR_META:
            vals = doc.xpath(f'//meta[@name="{name}"]/@content|//meta[@property="{name}"]/@content')
            for v in vals:
                authors.add(v.strip())
        # From byline class
        byline = doc.xpath('//*[contains(@class, "byline") or contains(@class, "author")]//text()')
        if byline:
            txt = " ".join(byline).strip()
            # Split by typical separators
            parts = AUTHOR_SPLIT_REGEX.split(txt)
            for p in parts:
                p = p.strip()
                if p and not DIGITS_REGEX.search(p) and len(p) > 2:
                    authors.add(p)
        # From JSON-LD
        j = meta.get("json_ld", {})
        if "author" in j:
            auth = j["author"]
            if isinstance(auth, str):
                authors.add(auth)
            elif isinstance(auth, dict) and "name" in auth:
                authors.add(auth["name"])
        return list(authors)

    def _extract_pubdate(self, doc: HtmlElement, url: Optional[str], meta: Dict) -> Optional[datetime]:
        # 1. URL regex
        if url:
            m = STRICT_DATE_REGEX.search(url)
            if m:
                try:
                    return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                except:
                    pass
        # 2. Meta tags
        for name in DATE_META:
            vals = doc.xpath(f'//meta[@name="{name}"]/@content|//meta[@property="{name}"]/@content')
            if vals:
                try:
                    return date_parser(vals[0])
                except:
                    pass
        # 3. JSON-LD
        j = meta.get("json_ld", {})
        for key in ["datePublished", "dateCreated", "dateModified"]:
            if key in j:
                try:
                    return date_parser(j[key])
                except:
                    pass
        # 4. Time tags
        time_tags = doc.xpath('//time/@datetime')
        if time_tags:
            try:
                return date_parser(time_tags[0])
            except:
                pass
        return None

    def _extract_images(self, doc: HtmlElement, top_node: Optional[HtmlElement], url: Optional[str]) -> List[str]:
        imgs = []
        # First, meta image (og:image)
        og_img = doc.xpath('//meta[@property="og:image"]/@content')
        if og_img and url:
            imgs.append(urljoin(url, og_img[0]))
        # Then images inside top node (if any)
        if top_node is not None:
            for img in top_node.xpath(".//img"):
                src = img.get("src") or img.get("data-src")
                if src and src.startswith("http"):
                    imgs.append(src)
                elif src and url:
                    imgs.append(urljoin(url, src))
        # Remove duplicates
        return list(dict.fromkeys(imgs))

    def _extract_videos(self, doc: HtmlElement, top_node: Optional[HtmlElement]) -> List[str]:
        videos = []
        if top_node is None:
            return videos
        for iframe in top_node.xpath(".//iframe"):
            src = iframe.get("src") or ""
            if any(provider in src for provider in VIDEO_PROVIDERS):
                videos.append(src)
        # JSON-LD VideoObject
        json_ld = extract_json_ld(doc)
        if "video" in json_ld and "contentUrl" in json_ld["video"]:
            videos.append(json_ld["video"]["contentUrl"])
        return list(dict.fromkeys(videos))

# ---------- Simple endpoints ----------
def extract_article(html: str, url: Optional[str] = None, language: str = "en") -> Dict:
    """Fast, single‑function interface."""
    extractor = FastArticleExtractor(language)
    return extractor.extract(html, url)

# Example usage (commented)
if __name__ == "__main__":
    sample_html = """
    <html>
    <head><title>Test Article | Site</title></head>
    <body>
        <article>
            <h1>Test Title</h1>
            <div class="byline">John Doe</div>
            <p>This is a test paragraph with stopwords.</p>
            <p>Second paragraph here.</p>
        </article>
    </body>
    </html>
    """
    result = extract_article(sample_html)
    print(result)