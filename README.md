# ResearchEmailer

A small pipeline for finding recent arXiv papers, extracting author contact
info, drafting personalized outreach emails, and sending them via Gmail.

Built to help find and reach out to researchers/labs for undergraduate
research opportunities.

## How it works

1. **Search & build contacts** (`src/build_contacts.py`) — queries the arXiv
   API for recent papers matching configured categories/keywords, downloads
   each PDF and tries to extract author emails from the first few pages,
   classifies the contact's region (NYC tristate vs. remote) from their email
   domain, and writes everything to `data/contacts.csv`.
2. **Retry lookups** (`src/retry_lookup.py`) — re-attempts email extraction
   for contacts that came back as `needs_lookup`.
3. **Generate drafts** (`src/draft_generator.py`) — writes a personalized
   outreach email to `drafts/` for each contact marked `ready`, using a
   templated hook plus a region-specific ask (paid/on-site for NYC tristate,
   remote/unpaid otherwise).
4. **Review** (`src/review_drafts.py`) — an interactive CLI to approve or
   skip each drafted email before anything gets sent.
5. **Send** (`src/gmail_client.py`) — sends approved drafts through the
   Gmail API (OAuth), attaching a resume.

`src/generate_cbi_drafts.py` is a one-off variant for NYU Center for Brain
Imaging PIs, where each opening paragraph is hand-written per contact instead
of templated from a paper.

## Contact status flow

`new → needs_lookup / ready → drafted → approved / skipped → sent`

Statuses are tracked per-contact in `data/contacts.csv` (see
`src/contacts_store.py` for the schema).

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll also need:

- **`config.yaml`** — arXiv search categories/keywords, target region filter,
  batch size, and your sender info (name, email, LinkedIn, GitHub).
- **`credentials.json`** — Google OAuth client credentials for Gmail send
  access (from the Google Cloud Console). Not checked into this repo.
- **`resume.pdf`** — attached to sent emails. Not checked into this repo.

`token.json` is created automatically on first Gmail auth.

## Usage

```bash
cd src
python build_contacts.py      # search arXiv, populate data/contacts.csv
python retry_lookup.py        # retry any contacts still missing an email
python draft_generator.py     # write drafts/ for all "ready" contacts
python review_drafts.py       # approve/skip drafts interactively
python gmail_client.py        # send approved drafts
```

## Notes

- Region classification (`src/region.py`) is a best-effort heuristic based on
  a hardcoded list of email domains — arXiv PDFs don't reliably expose an
  affiliation field to scrape.
- `data/contacts.csv`, `drafts/*.txt`, `credentials.json`, `token.json`, and
  `resume.pdf` are gitignored since they contain personal data or secrets.
