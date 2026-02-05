import json
from collections import defaultdict
from typing import List, Optional

from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_core.documents import Document

from retrieval.email_retriever import retrieve_relevant_emails


# ----------------------------
# 1️ Output Schema 
# ----------------------------
class ActionItem(BaseModel):
    sender: Optional[str] = None
    subject: str
    action: list[str]
    deadline: Optional[str]
    priority: str   # High | Medium | Low
    source_email_id: str


# ----------------------------
# 2️ LLM Setup
# ----------------------------
llm = Ollama(model="qwen2.5:7b-instruct")


# ----------------------------
# 3️ Prompt (LOCKED)
# ----------------------------
PROMPT = """
You are an assistant that extracts ACTIONABLE TASKS from emails.

Rules:
- Use ONLY the provided email.
- Do NOT invent actions or deadlines.
- If no action is required, return an empty JSON array.
- Be concise and precise.

Email Subject:
{subject}

Email Body:
{body}

Return output strictly as a JSON array with fields:
- subject
- sender
- action
- deadline (or null)
- priority (High | Medium | Low)
"""


# ----------------------------
# 4️ Group retrieved chunks by email
# ----------------------------
def group_docs_by_email(docs: List[Document]):
    grouped = defaultdict(list)
    for d in docs:
        grouped[d.metadata["email_id"]].append(d)
    return grouped


# ----------------------------
# 5️ Reconstruct full email context
# ----------------------------
def build_email_context(docs: List[Document]):
    metadata = docs[0].metadata

    full_body = "\n\n".join(d.page_content for d in docs)

    return {
        "email_id": metadata["email_id"],
        "subject": metadata["subject"],
        "sender": metadata["sender"],
        "received_at": metadata["received_at"],
        "labels": metadata["labels"],
        "body": full_body
    }

def safe_json_loads(text: str):
    if not text or not text.strip():
        return []

    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()

    # 🔥 NEW FIX: remove leading "json"
    if text.lower().startswith("json"):
        text = text[4:].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("JSON parsing failed")
        print("Raw LLM output:")
        print(text)
        return []


def normalize_llm_item(item: dict) -> dict:
    # ---- Normalize action ----
    if isinstance(item.get("action"), str):
        item["action"] = [item["action"]]
    elif item.get("action") is None:
        item["action"] = []

    # ---- Normalize deadline ----
    deadline = item.get("deadline")

    # list → string
    if isinstance(deadline, list):
        deadline = deadline[0] if deadline else None

    # non-ISO natural language → keep as string (DO NOT parse here)
    if isinstance(deadline, str):
        deadline = deadline.strip()

    item["deadline"] = deadline

    return item


# ----------------------------
# 6️ Extract actions PER EMAIL
# ----------------------------
def extract_actions_from_docs(docs: List[Document]) -> List[ActionItem]:
    grouped_docs = group_docs_by_email(docs)
    actions: List[ActionItem] = []

    for email_id, email_docs in grouped_docs.items():
        email = build_email_context(email_docs)
        prompt = PROMPT.format(
            subject=email["subject"],
            body=email["body"]
        )

        try:
            response = llm.invoke(prompt)
            parsed =  safe_json_loads(response)

            for item in parsed:
                item = normalize_llm_item(item)
                item["source_email_id"] = email_id
                item["sender"] = email["sender"]
                actions.append(ActionItem(**item))

        except Exception as e:
            print(f"[WARN] Skipping email {email_id}: {e}")

    return actions


# ----------------------------
# 7️ Sanity Test
# ----------------------------
if __name__ == "__main__":
    query = "reply required email"
    docs = retrieve_relevant_emails(query, k=2)

    actions = extract_actions_from_docs(docs)

    print("\n=== EXTRACTED ACTIONS ===\n")
    for a in actions:
        print(a.model_dump())
