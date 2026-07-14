"""Step 1: search arXiv, extract emails where possible, write data/contacts.csv."""
import sys
import time

import yaml

from arxiv_search import search_papers
from email_extractor import extract_emails_from_pdf, match_email_to_author
from contacts_store import load_contacts, save_contacts, upsert
from region import classify_region


def main():
    with open("../config.yaml") as f:
        cfg = yaml.safe_load(f)

    papers = search_papers(**cfg["search"])
    print(f"Found {len(papers)} papers in the last {cfg['search']['days_back']} days")

    contacts = load_contacts()
    batch_size = cfg["target"]["batch_size"]

    for paper in papers:
        if len(contacts) >= batch_size * 3:
            # keep a generous working pool; final batch selection happens later
            break

        emails = extract_emails_from_pdf(paper["pdf_url"])
        time.sleep(1)  # be polite to arxiv.org

        # first author is usually the corresponding/lead author for undergrad outreach
        primary_author = paper["authors"][0] if paper["authors"] else None
        if not primary_author:
            continue

        matched_email = match_email_to_author(primary_author, emails)

        contact = {
            "name": primary_author,
            "email": matched_email or "",
            "email_source": "pdf" if matched_email else "",
            "affiliation": "",
            "region": classify_region(matched_email) if matched_email else "unknown",
            "us_verified": "",
            "paper_title": paper["title"],
            "arxiv_id": paper["arxiv_id"],
            "paper_url": f"https://arxiv.org/abs/{paper['arxiv_id']}",
            "abstract": paper["abstract"],
            "status": "ready" if matched_email else "needs_lookup",
            "draft_path": "",
        }
        contacts = upsert(contacts, contact)
        print(f"  {'[email found]' if matched_email else '[needs lookup]'} {primary_author} - {paper['title'][:60]}")

    save_contacts(contacts)
    found = sum(1 for c in contacts if c["status"] == "ready")
    needs_lookup = sum(1 for c in contacts if c["status"] == "needs_lookup")
    print(f"\nTotal contacts: {len(contacts)} | emails found via PDF: {found} | needs manual lookup: {needs_lookup}")


if __name__ == "__main__":
    main()
