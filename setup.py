#!/usr/bin/env python3
"""Setup script for open_news package."""

from setuptools import setup, find_packages

# Read requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="open-news",
    version="0.1.0",
    author="ARAJIT PAUL",
    author_email="",
    description="Minimal news fetching: article text, RSS, Google News search, RSS discovery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/open_news",
    packages=find_packages(),
    package_data={
        "open_news": ["py.typed"],  # optional, for type hints
    },
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News",
    ],
    python_requires=">=3.7",
    keywords="news rss google-news article-extraction feedparser newspaper",
)