import json
from typing import List, Dict


def load_emails(path: str) -> List[Dict]:
    """
    Loads emails from JSON and returns a list of normalized email dicts.
    """

    # -----------------------------
    # Load JSON
    # -----------------------------
    with open(path, "r", encoding="utf-8") as f:
        raw_emails = json.load(f)

    normalized_emails: List[Dict] = []

    # -----------------------------
    # Normalize + Validate
    # -----------------------------
    for idx, email in enumerate(raw_emails):
        subject = (email.get("subject") or "").strip()
        body = (email.get("body") or "").strip()

        # Basic validation (IMPORTANT)
        if not subject or not body:
            print(
                f"[SKIP] Email at index {idx} skipped "
                f"(empty subject or body)"
            )
            continue

        sender = (email.get("sender") or "").strip()

        # Lowercase only the domain part of sender
        if "@" in sender:
            local, domain = sender.split("@", 1)
            sender = f"{local}@{domain.lower()}"

        labels = email.get("labels")

        # Ensure labels is always a list
        if not isinstance(labels, list):
            labels = []

        normalized_email = {
            "id": (email.get("id") or "").strip(),
            "subject": subject,
            "sender": sender,
            "received_at": (email.get("received_at") or "").strip(),
            "body": body,
            "labels": labels,
        }

        normalized_emails.append(normalized_email)

    return normalized_emails

def label_summary(emails):
    from collections import Counter
    counter = Counter()
    for e in emails:
        counter.update(e["labels"])
    return counter


# -----------------------------
# Simple Sanity Test (Temporary)
# -----------------------------
if __name__ == "__main__":
    emails = load_emails("D:\Code_Work\Repository\AgenticAI\Email_action_RAG\Emails\emails.json")
    print(f"Loaded {len(emails)} emails")
    if emails:
        print(emails[0])
    print(label_summary(emails))
