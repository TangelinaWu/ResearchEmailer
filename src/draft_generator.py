"""Step 3: generate a personalized outreach email draft for each ready contact."""
import os
import re

import yaml

from contacts_store import load_contacts, save_contacts

DRAFTS_DIR = os.path.join(os.path.dirname(__file__), "..", "drafts")

SUBJECT_TEMPLATE = "Undergrad Researcher Interested in Your Work"

NYU_COLUMBIA_DOMAINS = {"nyu.edu", "nyulangone.org", "columbia.edu", "cumc.columbia.edu"}

NYC_UNPAID_ASK = (
    "I'd love to be considered for a paid position, though unpaid works for me too—the opportunity "
    "to learn under your mentorship matters more to me than compensation. I'm available part-time, "
    "on-site in the NYC area, to start now, fall 2026, or spring 2027. Would you be open to a "
    "brief call, or could you point me to how your lab/team typically brings on undergraduate "
    "researchers?"
)

NYU_COLUMBIA_ASK = (
    "I'd love to be considered for a paid position, though unpaid works for me too (ideally for "
    "NYU research credit)—the opportunity to learn under your mentorship matters more to me than "
    "compensation. I'm available part-time to start now, fall 2026, or spring 2027. Would you be "
    "open to a brief call, or could you point me to how your lab typically brings on NYU "
    "undergraduate researchers?"
)

UNPAID_REMOTE_ASK = (
    "I'd love to be considered for a paid position, though unpaid works for me too—the opportunity "
    "to learn under your mentorship matters more to me than compensation. I'm available part-time "
    "and remotely, to start now, fall 2026, or spring 2027. Would you be open to a brief call, or "
    "could you point me to how your lab/team typically brings on undergraduate researchers?"
)


def _is_nyu_columbia(domain):
    if domain in NYU_COLUMBIA_DOMAINS:
        return True
    return domain.endswith(".nyu.edu") or domain.endswith(".columbia.edu") or domain.endswith(".nyulangone.org")


def position_ask_for_region(region, email=""):
    """Return the right position-ask paragraph based on region and email domain."""
    if region == "nyc_tristate":
        domain = email.strip().lower().split("@")[-1] if "@" in email else ""
        return NYU_COLUMBIA_ASK if _is_nyu_columbia(domain) else NYC_UNPAID_ASK
    return UNPAID_REMOTE_ASK


BODY_TEMPLATE = """Dear {first_name},

My name is Angelina Wu. I'm an undergraduate studying Computer Science & Economics at NYU (Class of 2028). I recently read your paper, "{paper_title}" ({paper_url}). {topic_hook} I found that particularly compelling.

I'm currently a software engineering intern at Lea Technologies, where I work on document taxonomy, data validation, and parsing pipelines. I also have hands-on experience scraping, processing, and cleaning data from independent projects, and I'm especially interested in working with ML data. I primarily work in Python, using pandas, regex, and pypdf for parsing and cleaning, and SQL for data storage and querying.

{position_ask}

Thank you for your time and for the work you're putting into the field. I really enjoyed reading your paper. I've attached my resume for your reference.

Best,
Angelina Wu
aw5287@nyu.edu | {linkedin} | {github}
"""


def first_name(full_name):
    return full_name.strip().split()[0]


def topic_hook_from_abstract(abstract):
    """Pull a specific, personalized hook from the abstract as a standalone sentence.

    Prefers the sentence stating the paper's actual contribution ("We introduce/show/propose...")
    over the generic opening sentence, and rephrases it in second person.
    """
    sentences = re.split(r"(?<=[.!?])\s+", abstract.strip())
    contribution = next((s for s in sentences if re.match(r"^(We|Our)\b", s)), None)
    hook = (contribution or (sentences[0] if sentences else abstract)).rstrip(". ")

    hook = re.sub(r"^We\b", "You", hook)
    hook = re.sub(r"^Our\b", "Your", hook)
    hook = re.sub(r"\bwe\b", "you", hook)
    hook = re.sub(r"\bour\b", "your", hook)

    if len(hook) > 220:
        hook = hook[:220].rsplit(" ", 1)[0] + "..."
    if not hook.endswith("."):
        hook += "."
    return hook


def generate_draft(contact, sender_cfg):
    subject = SUBJECT_TEMPLATE
    body = BODY_TEMPLATE.format(
        first_name=first_name(contact["name"]),
        paper_title=contact["paper_title"],
        paper_url=contact["paper_url"],
        topic_hook=topic_hook_from_abstract(contact["abstract"]),
        position_ask=position_ask_for_region(contact.get("region", "remote"), contact.get("email", "")),
        linkedin=sender_cfg["linkedin"],
        github=sender_cfg["github"],
    )
    return subject, body


def safe_filename(name, arxiv_id):
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_")
    return f"{slug}_{arxiv_id}.txt"


def _nyu_columbia_first(c):
    domain = c["email"].split("@")[-1].lower() if "@" in c["email"] else ""
    return 0 if domain in NYU_COLUMBIA_DOMAINS else 1


def main():
    with open("../config.yaml") as f:
        cfg = yaml.safe_load(f)

    os.makedirs(DRAFTS_DIR, exist_ok=True)
    contacts = load_contacts()
    batch_size = cfg["target"]["batch_size"]

    # NYC metropolitan area only; NYU and Columbia contacts first
    eligible = [
        c for c in contacts
        if c["status"] == "ready" and c["email"] and c.get("region") == "nyc_tristate"
    ]
    eligible.sort(key=_nyu_columbia_first)
    batch = eligible[:batch_size]

    generated = 0
    for c in batch:
        subject, body = generate_draft(c, cfg["sender"])
        fname = safe_filename(c["name"], c["arxiv_id"])
        path = os.path.join(DRAFTS_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"TO: {c['email']}\nSUBJECT: {subject}\n\n{body}")

        c["draft_path"] = os.path.join("drafts", fname)
        c["status"] = "drafted"
        generated += 1

    save_contacts(contacts)
    nyu_col = sum(1 for c in batch if _nyu_columbia_first(c) == 0)
    print(f"Generated {generated} drafts in {DRAFTS_DIR}/  "
          f"({nyu_col} NYU/Columbia, {generated - nyu_col} other NYC)")


if __name__ == "__main__":
    main()
