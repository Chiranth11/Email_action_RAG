import os
import json
import uuid
from datetime import timezone
import extract_msg
from bs4 import BeautifulSoup

# -----------------------------
# CONFIG
# -----------------------------
MSG_FOLDER = "D:\Code_Work\Repository\AgenticAI\Email_action_RAG\Emails"          # folder containing .msg files
OUTPUT_JSON = "emails.json"    # output JSON file

# -----------------------------
# Helpers
# -----------------------------
def to_iso(dt):
    """Convert datetime to ISO-8601 string."""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def html_to_text(html: str) -> str:
    """Convert HTML body to clean plain text."""
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator="\n", strip=True)

def extract_email_body(msg) -> str:
    """
    Robust body extraction:
    1. Plain text
    2. HTML → clean text
    3. RTF (fallback)
    """
    if msg.body:
        return msg.body.strip()

    if msg.htmlBody:
        return html_to_text(msg.htmlBody)

    if msg.rtfBody:
        if isinstance(msg.rtfBody, bytes):
            return msg.rtfBody.decode(errors="ignore")
        return str(msg.rtfBody)

    return ""

# -----------------------------
# Main conversion logic
# -----------------------------
emails = []

for filename in os.listdir(MSG_FOLDER):
    if not filename.lower().endswith(".msg"):
        continue

    path = os.path.join(MSG_FOLDER, filename)
    msg = extract_msg.Message(path)

    email_record = {
        "id": str(uuid.uuid4()),
        "subject": msg.subject or "",
        "sender": msg.sender or "",
        "received_at": to_iso(msg.date),
        "body": extract_email_body(msg),
        "labels": []
    }

    emails.append(email_record)
    msg.close()

# -----------------------------
# Write combined JSON
# -----------------------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(emails, f, indent=2, ensure_ascii=False)

print(f"Converted {len(emails)} emails into '{OUTPUT_JSON}'")
