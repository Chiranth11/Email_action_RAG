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
    subject: str
    action: str
    deadline: Optional[str]
    priority: str   # High | Medium | Low
    source_email_id: str


# ----------------------------
# 2️ LLM Setup
# ----------------------------
llm = Ollama(model="qwen2.5:7b-instruct")

PROMPT = """
You are an assistant that extracts ACTIONABLE TASKS from emails.

Rules:
- Use ONLY the provided email content.
- Do NOT invent actions or deadlines.
- If no action is required, return an empty list.
- Be concise.

For each action, return:
- subject
- action
- deadline (or null)
- priority (High, Medium, Low)
- source_email_id
- sender

Email content:
{email_text}

Return output strictly as JSON array.
"""

def safe_json_loads(text: str):
    if not text or not text.strip():
        return []

    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print("JSON parsing failed")
        print("Raw LLM output:")
        print(text)
        return []


def extract_actions(doc):
    prompt = PROMPT.format(email_text=doc.page_content)
    response = llm.invoke(prompt)
    return safe_json_loads(response)

def extract_actions_from_docs(docs):
    actions = []
    for d in docs:
        extracted = extract_actions(d)
        for a in extracted:
            a["source_email_id"] = d.metadata["email_id"]
            actions.append(a)
    return actions

if __name__ == "__main__":
    from retrieval.email_retriever import retrieve_relevant_emails

    docs = retrieve_relevant_emails("deadline submit assignment", k=2)
    actions = extract_actions_from_docs(docs)

    for a in actions:
        print(a)
