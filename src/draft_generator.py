"""Step 3: generate a personalized outreach email draft for each ready contact."""
import os
import re

import yaml

from contacts_store import load_contacts, save_contacts

DRAFTS_DIR = os.path.join(os.path.dirname(__file__), "..", "drafts")

SUBJECT_TEMPLATE = "Undergrad Researcher Interested in Your Work"

PAID_INPERSON_ASK = (
    "I'm looking for a paid, part-time undergraduate research position on-site in the NYC area "
    "for fall 2026 or spring 2027, and I'd love to work under your mentorship if that timeline "
    "works for you. Would you be open to a brief call, or could you point me to how your lab/team "
    "typically brings on undergraduate researchers?"
)

UNPAID_REMOTE_ASK = (
    "I'm looking for a remote, part-time undergraduate research position, unpaid to start, "
    "for fall 2026 or spring 2027, and I'd love to work under your mentorship if that timeline "
    "works for you. Would you be open to a brief call, or could you point me to how your lab/team "
    "typically brings on undergraduate researchers?"
)


def position_ask_for_region(region):
    """NYC tristate contacts get the paid/on-site pitch; everyone else gets remote/unpaid."""
    return PAID_INPERSON_ASK if region == "nyc_tristate" else UNPAID_REMOTE_ASK


BODY_TEMPLATE = """Dear {first_name},

My name is Angelina Wu. I'm an undergraduate studying Computer Science & Economics at NYU (Class of 2028). I recently read your paper, "{paper_title}" ({paper_url}). {topic_hook} I found that particularly compelling.

I'm currently a software engineering intern at Lea Technologies, where I work on document taxonomy, data validation, and parsing pipelines. I also have hands-on experience scraping, processing, and cleaning data from independent projects, and I'm especially interested in working with ML data. I primarily work in Python, using pandas, regex, and pypdf for parsing and cleaning, and SQL for data storage and querying.

{position_ask}

Thank you for your time and for the work you're putting into the field. I really enjoyed reading your paper.

Best,
Angelina Wu
{linkedin} | {github}
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
        position_ask=position_ask_for_region(contact.get("region", "remote")),
        linkedin=sender_cfg["linkedin"],
        github=sender_cfg["github"],
    )
    return subject, body


def safe_filename(name, arxiv_id):
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_")
    return f"{slug}_{arxiv_id}.txt"


def main():
    with open("../config.yaml") as f:
        cfg = yaml.safe_load(f)

    os.makedirs(DRAFTS_DIR, exist_ok=True)
    contacts = load_contacts()

    generated = 0
    for c in contacts:
        if c["status"] != "ready" or not c["email"]:
            continue

        subject, body = generate_draft(c, cfg["sender"])
        fname = safe_filename(c["name"], c["arxiv_id"])
        path = os.path.join(DRAFTS_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"TO: {c['email']}\nSUBJECT: {subject}\n\n{body}")

        c["draft_path"] = os.path.join("drafts", fname)
        c["status"] = "drafted"
        generated += 1

    save_contacts(contacts)
    print(f"Generated {generated} drafts in {DRAFTS_DIR}/")


if __name__ == "__main__":
    main()
