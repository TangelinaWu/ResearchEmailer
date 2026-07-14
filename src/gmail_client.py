"""Step 4: send approved drafts via the Gmail API (OAuth)."""
import base64
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from contacts_store import load_contacts, save_contacts

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")
RESUME_PATH = os.path.join(os.path.dirname(__file__), "..", "resume.pdf")
RESUME_FILENAME = "Angelina Wu Resume.pdf"


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def parse_draft(draft_path):
    with open(draft_path, encoding="utf-8") as f:
        content = f.read()
    to_line, subject_line, _, *body_lines = content.split("\n")
    to = to_line.replace("TO: ", "").strip()
    subject = subject_line.replace("SUBJECT: ", "").strip()
    body = "\n".join(body_lines)
    return to, subject, body


def send_message(service, sender, to, subject, body):
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    message.attach(MIMEText(body))

    with open(RESUME_PATH, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=RESUME_FILENAME)
    message.attach(attachment)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main():
    with open("../config.yaml") as f:
        cfg = yaml.safe_load(f)
    sender = cfg["sender"]["email"]
    if not sender:
        raise SystemExit("Set sender.email in config.yaml before sending.")

    service = get_gmail_service()
    contacts = load_contacts()

    to_send = [c for c in contacts if c["status"] == "approved"]
    print(f"{len(to_send)} approved drafts to send")

    for c in to_send:
        draft_path = os.path.join(os.path.dirname(__file__), "..", c["draft_path"])
        to, subject, body = parse_draft(draft_path)
        try:
            send_message(service, sender, to, subject, body)
            c["status"] = "sent"
            print(f"  sent -> {c['name']} <{to}>")
        except Exception as e:
            print(f"  FAILED -> {c['name']} <{to}>: {e}")

    save_contacts(contacts)


if __name__ == "__main__":
    main()
