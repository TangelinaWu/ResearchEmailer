"""Interactively review drafted emails: approve or skip each before sending."""
import os
import sys

from contacts_store import load_contacts, save_contacts

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


def main():
    contacts = load_contacts()
    to_review = [c for c in contacts if c["status"] == "drafted"]
    if not to_review:
        print("No drafted contacts to review.")
        return

    print(f"{len(to_review)} drafts to review.\n")
    for i, c in enumerate(to_review, 1):
        draft_path = os.path.join(PROJECT_ROOT, c["draft_path"])
        with open(draft_path, encoding="utf-8") as f:
            content = f.read()

        domain = c["email"].split("@")[-1] if "@" in c["email"] else "?"
        print("=" * 70)
        print(f"[{i}/{len(to_review)}] {c['name']}  <{c['email']}>  (domain: {domain})")
        print(f"Paper: {c['paper_title']}")
        print("-" * 70)
        print(content)
        print("-" * 70)

        while True:
            choice = input("Approve / Skip / Quit? [a/s/q] ").strip().lower()
            if choice in ("a", "approve"):
                c["status"] = "approved"
                break
            if choice in ("s", "skip"):
                c["status"] = "skipped"
                break
            if choice in ("q", "quit"):
                save_contacts(contacts)
                print("Saved progress. Exiting.")
                sys.exit(0)
            print("Please enter a, s, or q.")

    save_contacts(contacts)
    approved = sum(1 for c in contacts if c["status"] == "approved")
    print(f"\nDone. {approved} contacts now approved and ready to send.")


if __name__ == "__main__":
    main()
