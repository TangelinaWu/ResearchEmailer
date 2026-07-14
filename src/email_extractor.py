"""Download an arXiv PDF and try to extract author emails from the first page."""
import io
import re
import unicodedata

import requests
from pypdf import PdfReader

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def _strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def extract_emails_from_pdf(pdf_url, timeout=30):
    """Return a list of emails found on the first three pages of the PDF."""
    try:
        resp = requests.get(pdf_url, timeout=timeout)
        resp.raise_for_status()
        reader = PdfReader(io.BytesIO(resp.content))
        text = ""
        for page in reader.pages[:3]:
            text += page.extract_text() or ""
        emails = sorted(set(EMAIL_RE.findall(text)))
        return emails
    except Exception:
        return []


def match_email_to_author(author_name, emails):
    """Best-effort: match an email to an author by last name substring (accent-insensitive)."""
    if not emails:
        return None
    last = _strip_accents(author_name.strip().split()[-1].lower())
    for e in emails:
        if last in _strip_accents(e.lower()):
            return e
    return None
