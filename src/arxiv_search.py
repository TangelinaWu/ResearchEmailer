"""Search arXiv for recent papers matching topic keywords/categories."""
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import requests

ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _build_query(categories, keywords):
    cat_clause = " OR ".join(f"cat:{c}" for c in categories)
    kw_clause = " OR ".join(f'abs:"{k}"' for k in keywords)
    return f"({cat_clause}) AND ({kw_clause})"


def search_papers(categories, keywords, max_results=150, days_back=60):
    """Query arXiv API, return list of paper dicts within days_back."""
    query = _build_query(categories, keywords)
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    resp = requests.get(ARXIV_API, params=params, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    papers = []
    for entry in root.findall("atom:entry", NS):
        published = entry.find("atom:published", NS).text
        pub_dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if pub_dt < cutoff:
            continue

        arxiv_id = entry.find("atom:id", NS).text.rsplit("/", 1)[-1]
        title = entry.find("atom:title", NS).text.strip().replace("\n", " ")
        abstract = entry.find("atom:summary", NS).text.strip().replace("\n", " ")
        authors = [a.find("atom:name", NS).text for a in entry.findall("atom:author", NS)]

        pdf_url = None
        for link in entry.findall("atom:link", NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

        papers.append(
            {
                "arxiv_id": arxiv_id,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "pdf_url": pdf_url,
                "published": published,
            }
        )

    return papers


if __name__ == "__main__":
    import yaml

    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    results = search_papers(**cfg["search"])
    print(f"Found {len(results)} papers")
    for p in results[:5]:
        print("-", p["title"], "|", p["authors"][:3])
