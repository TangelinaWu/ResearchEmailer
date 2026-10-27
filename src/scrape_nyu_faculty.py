"""Scrape NYU faculty directories and generate Greene HPC sponsorship drafts.

Most NYU pages are JavaScript-rendered (require a real browser). This script
targets the subset of faculty pages that return usable static HTML:
  - Courant Math (math.nyu.edu)
  - Tandon BME and MAE department pages
  - Any page you add to SCHOOL_PAGES below

For everything else (Albert, CAS, Steinhardt, Law, Stern, etc.) use --import:

  Export a name list from Albert or any faculty page → save as a plain text
  file, one name per line → run:

    python3 scrape_nyu_faculty.py --import names.txt

  The script constructs best-guess NYU emails (firstname.lastname@nyu.edu)
  and writes a draft for each name.

Run from src/:
  python3 scrape_nyu_faculty.py              # scrape known-static pages
  python3 scrape_nyu_faculty.py --dry-run    # print names only, no files
  python3 scrape_nyu_faculty.py --import f   # import names from a text file

Then send via the normal pipeline:
  python3 review_drafts.py
  python3 gmail_client.py
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))
from contacts_store import load_contacts, save_contacts, upsert
from draft_generator import safe_filename

DRAFTS_DIR = Path(__file__).parent.parent / "drafts"
DATA_DIR = Path(__file__).parent.parent / "data"

SENDER_EMAIL = "angelina@getlea.io"
SUBJECT = "Request for Greene HPC Sponsorship — CNN/MRI Brain Aging Research"

GENERIC_OPENING = (
    "As an NYU faculty member you have the ability to sponsor external collaborators "
    "for access to university HPC resources, and I wanted to reach out to see if you "
    "might be willing to help our research team."
)

BODY_TEMPLATE = """\
Dear Professor {last_name},

I hope this message finds you well. {opening}

I am writing to ask if you would be willing to sponsor our research team for access \
to NYU's Greene GPU cluster. Our PI, Prof. Babak Ardekani, is affiliated with NYU \
Grossman School of Medicine rather than the main campus, so his lab does not \
automatically receive Greene access — a sponsoring NYU faculty member is all that is \
needed to bridge that gap.

**Our Team**

- Prof. Babak Ardekani, PhD (PI) — Nathan S. Kline Institute / NYU Grossman School of \
Medicine. Over 25 years in computational neuroimaging, author of the ART (Automatic \
Registration Toolbox) used by labs worldwide, with 100+ peer-reviewed publications on \
MRI brain registration and Alzheimer's detection.
- Angelina Wu — research engineer, NYU CS & Economics '28. Pipeline architecture, \
preprocessing, and model training.
- Amir — PhD student, HKUST. Deep learning architecture and longitudinal analysis.
- Nathan — undergraduate researcher, Northeastern University. Data processing and evaluation.

**The Project**

We are training 3D CNNs on structural MRI to predict brain age and compute the Brain Age \
Gap (BAG) — a biomarker for accelerated neurodegeneration linked to Alzheimer's disease \
and frontotemporal dementia. Our data comes from ADNI and OASIS-3 (several thousand scans). \
Training a single model takes 12–24 hours on an A100; across experiments we estimate \
500–800 GPU hours and ~2 TB of storage — well within a typical faculty allocation, and we \
would stay within any sub-limits you set.

Sponsoring us would mean a one-time administrative step to add Prof. Ardekani's account \
to your allocation. We would handle everything else independently and are happy to share \
results, include acknowledgments, or explore collaboration if there is interest.

I would love to get on a short call with you to discuss the specifics — 15 to 20 minutes \
at your convenience. Feel free to suggest a time, or just reply and I will send a \
calendar invite.

Thank you so much for considering this.

Warmly,
Angelina Wu
NYU, CS & Economics '28
{email}
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ── Faculty pages that return usable static HTML ──────────────────────────────
# Most NYU pages are JS-rendered (React/Drupal) and return an empty 202 body.
# These are the pages confirmed to work without a headless browser.
# Add more here if you find working ones.
SCHOOL_PAGES = [
    # Courant Math — static HTML, full faculty list
    ("Courant Math", "https://math.nyu.edu/dynamic/people/faculty/", "nyu_courant_math"),
    # Tandon department pages that serve static HTML
    ("Tandon BME", "https://engineering.nyu.edu/academics/departments/biomedical-engineering/faculty", "nyu_tandon_dept"),
    ("Tandon MAE", "https://engineering.nyu.edu/academics/departments/mechanical-and-aerospace-engineering/faculty", "nyu_tandon_dept"),
]


def get(url: str, timeout: int = 15):
    try:
        r = SESSION.get(url, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  [WARN] {url}: {e}", file=sys.stderr)
        return None


def extract_email(text: str) -> str:
    m = re.search(r"[a-zA-Z0-9._%+\-]+@(?:nyu\.edu|nyulangone\.org)", text)
    return m.group(0).lower() if m else ""


def guess_email(name: str) -> str:
    """Best-guess NYU email: firstname.lastname@nyu.edu"""
    parts = name.lower().split()
    if len(parts) >= 2:
        first = re.sub(r"[^a-z]", "", parts[0])
        last = re.sub(r"[^a-z]", "", parts[-1])
        if first and last:
            return f"{first}.{last}@nyu.edu"
    return ""


def clean_name(raw: str) -> str:
    name = re.sub(r"\s+", " ", raw).strip()
    # Drop titles / credentials after comma
    name = re.split(r",\s*(Ph\.?D|M\.?D|J\.?D|Ed\.?D|Dr\.)", name, flags=re.I)[0].strip()
    # Drop "Professor", "Dr.", "Prof."
    name = re.sub(r"^(Professor|Prof\.|Dr\.)\s+", "", name, flags=re.I).strip()
    return name


# ── Strategy implementations ──────────────────────────────────────────────────

def scrape_nyu_courant_math(soup: BeautifulSoup) -> list[dict]:
    """Courant Math: names are in <h2 class="name"> inside <a class="people-link">."""
    results = []
    seen = set()
    for link in soup.select("a.people-link"):
        name_el = link.select_one("h2.name, figcaption.name")
        if not name_el:
            continue
        name = clean_name(name_el.get_text())
        if not name or len(name) < 4 or name in seen:
            continue
        seen.add(name)
        email = extract_email(link.get_text()) or guess_email(name)
        results.append({"name": name, "email": email})
    return results


def scrape_nyu_tandon_dept(soup: BeautifulSoup) -> list[dict]:
    """Tandon dept pages: faculty names are in <h3> inside article cards."""
    results = []
    seen = set()
    for h3 in soup.select("h3"):
        name = clean_name(h3.get_text())
        if not name or len(name) < 5 or len(name) > 60 or name in seen:
            continue
        # Must look like "First Last" — at least two words, each capitalised
        if not re.match(r"[A-Z][a-zA-Z'\-]+ .+", name):
            continue
        seen.add(name)
        email = guess_email(name)
        results.append({"name": name, "email": email})
    return results


STRATEGY_MAP = {
    "nyu_courant_math": scrape_nyu_courant_math,
    "nyu_tandon_dept": scrape_nyu_tandon_dept,
}


def slug(name: str) -> str:
    return "albert-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def write_draft(prof: dict, opening: str) -> str:
    last = prof["name"].split()[-1]
    body = BODY_TEMPLATE.format(
        last_name=last,
        opening=opening,
        email=SENDER_EMAIL,
    )
    arxiv_id = slug(prof["name"])
    fname = safe_filename(prof["name"], arxiv_id)
    path = DRAFTS_DIR / fname
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"TO: {prof['email']}\nSUBJECT: {SUBJECT}\n\n{body}")
    return str(Path("drafts") / fname)


def import_from_file(path: str) -> list[dict]:
    """Read a plain-text file (one name per line) and return faculty dicts."""
    faculty = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            name = clean_name(line.strip())
            if not name or len(name) < 4:
                continue
            if not re.search(r"[A-Za-z]+ [A-Za-z]+", name):
                continue
            faculty.append({"name": name, "email": guess_email(name), "school": "Imported"})
    return faculty


def process_faculty(all_faculty: list[dict], dry_run: bool):
    contacts = load_contacts()
    if not dry_run:
        DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    if dry_run:
        for f in all_faculty:
            print(f"  {f['name']:<35} {f['school']:<25} {f['email']}")
        print(f"\nTotal: {len(all_faculty)}")
        return

    generated = 0
    for prof in all_faculty:
        arxiv_id = slug(prof["name"])
        email = prof["email"]

        contact = {
            "name": prof["name"],
            "email": email,
            "email_source": "guessed",
            "affiliation": f"NYU ({prof['school']})",
            "region": "nyc_tristate",
            "us_verified": "yes",
            "paper_title": f"NYU faculty — {prof['school']}",
            "arxiv_id": arxiv_id,
            "paper_url": "",
            "abstract": "",
            "status": "drafted" if email else "needs_lookup",
            "draft_path": "",
        }

        if email:
            draft_path = write_draft(prof, GENERIC_OPENING)
            contact["draft_path"] = draft_path
            generated += 1

        contacts = upsert(contacts, contact)

    save_contacts(contacts)
    print(f"\nGenerated {generated} drafts in {DRAFTS_DIR}/")
    print(f"{len(all_faculty) - generated} still need email lookup.")
    print("\nNext steps:")
    print("  python3 review_drafts.py")
    print("  python3 gmail_client.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print names only, no files")
    parser.add_argument("--import", dest="import_file", metavar="FILE",
                        help="Import names from a plain-text file (one per line) instead of scraping")
    args = parser.parse_args()

    if args.import_file:
        faculty = import_from_file(args.import_file)
        print(f"Imported {len(faculty)} names from {args.import_file}")
        process_faculty(faculty, args.dry_run)
        return

    # Scrape known-static pages
    all_faculty: list[dict] = []
    seen_names: set[str] = set()

    for school, url, strategy in SCHOOL_PAGES:
        print(f"  Scraping {school} …")
        soup = get(url)
        if not soup:
            print(f"    [SKIP] Could not fetch {url}")
            continue

        scraper = STRATEGY_MAP.get(strategy)
        if not scraper:
            print(f"    [SKIP] Unknown strategy: {strategy}")
            continue

        faculty = scraper(soup)
        new_count = 0
        for f in faculty:
            name = f["name"]
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            all_faculty.append({**f, "school": school})
            new_count += 1

        print(f"    → {new_count} faculty found")
        time.sleep(0.5)

    print(f"\nTotal unique faculty scraped: {len(all_faculty)}")
    process_faculty(all_faculty, args.dry_run)


if __name__ == "__main__":
    main()
