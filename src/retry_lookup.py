"""Retry PDF email extraction for contacts still marked needs_lookup."""
import time

from contacts_store import load_contacts, save_contacts
from email_extractor import extract_emails_from_pdf, match_email_to_author


def main():
    contacts = load_contacts()
    pending = [c for c in contacts if c["status"] == "needs_lookup"]
    print(f"Retrying {len(pending)} contacts...")

    found = 0
    for c in pending:
        pdf_url = f"https://arxiv.org/pdf/{c['arxiv_id']}"
        emails = extract_emails_from_pdf(pdf_url)
        time.sleep(1)  # be polite to arxiv.org

        matched = match_email_to_author(c["name"], emails)
        if matched:
            c["email"] = matched
            c["email_source"] = "pdf"
            c["status"] = "ready"
            found += 1
            print(f"  [found] {c['name']} -> {matched}")
        else:
            print(f"  [still missing] {c['name']}")

    save_contacts(contacts)
    print(f"\n{found}/{len(pending)} resolved. {len(pending) - found} still need manual lookup.")


if __name__ == "__main__":
    main()
