"""
Naver News body collector (single-string output)

Requirements implemented per user's precise prompt.
"""

import re
import requests
import html
from bs4 import BeautifulSoup
from tqdm import tqdm
import os

# Naver API credentials (hardcoded as requested)
NAVER_CLIENT_ID = "5HZ2JClfp4xSRJ1MIdAu"
NAVER_CLIENT_SECRET = "8z76y_JHgR"
ENDPOINT = "https://openapi.naver.com/v1/search/news.json"

HEADERS = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
}

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}


def search_news(query: str = "속보", display: int = 10):
    params = {"query": query, "display": display, "sort": "date"}
    try:
        resp = requests.get(ENDPOINT, headers=HEADERS, params=params, timeout=5)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        results = []
        for it in items:
            link = it.get("originallink") or it.get("link")
            title = re.sub(r"<[^>]+>", "", it.get("title", ""))
            title = html.unescape(title).strip()
            results.append({"title": title, "link": link})
        return results
    except Exception:
        return []


def clean_soup(soup: BeautifulSoup):
    # Remove unwanted tags
    for tag in soup.find_all(["script", "style", "header", "footer", "nav", "aside", "iframe"]):
        try:
            tag.decompose()
        except Exception:
            pass

    # remove ad-like wrappers
    for div in soup.find_all("div"):
        try:
            cls = " ".join(div.get("class", [])).lower()
            did = (div.get("id") or "").lower()
            if "ad" in cls or "ad" in did or "advert" in cls or "advert" in did:
                div.decompose()
        except Exception:
            pass


def extract_text_from_soup(soup: BeautifulSoup) -> str:
    # Priority selectors
    selectors = [
        "#articleBodyContents",
        ".article-body",
        ".article-content",
        "article[itemprop=articleBody]",
        "div[itemprop=articleBody]",
        "div[id*=content]",
        "div[class*=article]",
    ]

    for sel in selectors:
        node = soup.select_one(sel)
        if node and node.get_text(strip=True):
            text = node.get_text(separator=" ")
            return re.sub(r"\s+", " ", text).strip()

    # Try <article>
    art = soup.find("article")
    if art and art.get_text(strip=True):
        text = art.get_text(separator=" ")
        return re.sub(r"\s+", " ", text).strip()

    # Fallback: combine consecutive <p> tags with reasonable length
    paragraphs = [p.get_text().strip() for p in soup.find_all("p") if p.get_text()]
    good_pars = [p for p in paragraphs if len(p) >= 30]
    if good_pars:
        text = " ".join(good_pars)
        return re.sub(r"\s+", " ", text).strip()

    # As last resort, take body text
    body = soup.body
    if body and body.get_text(strip=True):
        text = body.get_text(separator=" ")
        return re.sub(r"\s+", " ", text).strip()

    return ""


def fetch_article_body(url: str) -> str:
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        clean_soup(soup)
        content = extract_text_from_soup(soup)
        return content
    except Exception:
        return ""


def preprocess_and_combine(list_of_texts):
    # Combine into single string
    combined = " ".join([t for t in list_of_texts if t])
    # Remove newlines
    combined = combined.replace("\n", " ")
    # Collapse multiple spaces
    combined = re.sub(r"\s{2,}", " ", combined)
    # Strip
    combined = combined.strip()
    return combined


def main():
    results = search_news("속보", display=10)
    links = [r.get("link") for r in results if r.get("link")]

    collected = []
    # Silent progress: only tqdm shown
    for link in tqdm(links, desc="수집 중", unit="link", ncols=80):
        if not link:
            continue
        text = fetch_article_body(link)
        if text:
            collected.append(text)

    final = preprocess_and_combine(collected)
    # Final single print
    print(final)


if __name__ == "__main__":
    main()
