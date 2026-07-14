"""Read/write the contacts.csv working set."""
import csv
import os

FIELDS = [
    "name",
    "email",
    "email_source",  # pdf | websearch | none
    "affiliation",
    "region",  # nyc_tristate | remote | unknown
    "us_verified",  # yes | no | unknown
    "paper_title",
    "arxiv_id",
    "paper_url",
    "abstract",
    "status",  # new | needs_lookup | ready | drafted | approved | sent | skipped
    "draft_path",
]

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contacts.csv")


def load_contacts(path=DEFAULT_PATH):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_contacts(contacts, path=DEFAULT_PATH):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for c in contacts:
            writer.writerow({k: c.get(k, "") for k in FIELDS})


def upsert(contacts, new_contact):
    """Dedup by (name, arxiv_id). Returns updated list."""
    key = (new_contact.get("name"), new_contact.get("arxiv_id"))
    for i, c in enumerate(contacts):
        if (c.get("name"), c.get("arxiv_id")) == key:
            contacts[i] = {**c, **new_contact}
            return contacts
    contacts.append(new_contact)
    return contacts
