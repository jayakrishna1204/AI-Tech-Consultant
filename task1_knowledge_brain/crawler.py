
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from task1_knowledge_brain.database import save_article

SITEMAP_URL = (
    "https://support.brilliantdirectories.com/support/sitemap.xml"
)


def get_sitemap_urls(max_pages: int | None = 20) -> list[str]:
    """Read article URLs from the help-center sitemap."""
    response = httpx.get(
        SITEMAP_URL,
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": "JD4KnowledgeBrain/1.0"},
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    urls = [
        node.text.strip()
        for node in root.iter()
        if node.tag.endswith("loc") and node.text
    ]

    # Support both a sitemap index and a normal URL sitemap.
    if urls and all(urlparse(url).path.endswith(".xml") for url in urls):
        expanded = []
        for sitemap_url in urls:
            sitemap_response = httpx.get(
                sitemap_url,
                timeout=30,
                follow_redirects=True,
                headers={"User-Agent": "JD4KnowledgeBrain/1.0"},
            )
            sitemap_response.raise_for_status()
            sitemap_root = ET.fromstring(sitemap_response.content)
            expanded.extend(
                node.text.strip()
                for node in sitemap_root.iter()
                if node.tag.endswith("loc") and node.text
            )
        urls = expanded

    if max_pages is not None:
        urls = urls[:max_pages]

    return urls


def crawl_article(url: str) -> dict | None:
    """Extract readable text from one help-center article."""
    try:
        response = httpx.get(
            url,
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": "JD4KnowledgeBrain/1.0"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup.select(
            "script, style, nav, footer, header, noscript"
        ):
            element.decompose()

        main = soup.find("main") or soup.find("article") or soup.body
        if main is None:
            return None

        title_tag = soup.find("h1") or soup.find("title")
        title = (
            title_tag.get_text(" ", strip=True)
            if title_tag
            else url
        )
        content = main.get_text(" ", strip=True)

        if len(content) < 80:
            return None

        return {
            "url": url,
            "title": title,
            "content": content,
        }

    except (httpx.HTTPError, ET.ParseError) as exc:
        print(f"Could not crawl {url}: {exc}")
        return None


def sync_articles(
    max_pages: int | None = 20,
    delay_seconds: float = 1.0,
) -> dict:
    """Fetch sitemap articles and save successfully extracted content."""
    urls = get_sitemap_urls(max_pages=max_pages)
    saved = 0
    failed = 0

    for index, url in enumerate(urls, start=1):
        article = crawl_article(url)

        if article:
            save_article(
                article["url"],
                article["title"],
                article["content"],
            )
            saved += 1
            print(f"[{index}/{len(urls)}] Saved: {article['title']}")
        else:
            failed += 1
            print(f"[{index}/{len(urls)}] Skipped: {url}")

        if index < len(urls):
            time.sleep(delay_seconds)

    return {
        "discovered": len(urls),
        "saved": saved,
        "failed": failed,
    }
