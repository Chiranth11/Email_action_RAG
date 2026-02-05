'''
Priority order (highest first):

Explicit deadlines (earlier = higher)

Action verbs:

submit, upload, attend, reply → higher

Labels hint:

deadline, action_required → boost

'''
from datetime import datetime
from typing import List
from generation.action_extractor import ActionItem
from retrieval.email_retriever import retrieve_relevant_emails
from generation.action_extractor import extract_actions_from_docs

HIGH_ACTIONS = ["submit", "upload", "reply", "attend", "register"]

def score_action(action: ActionItem) -> int:
    score = 0

    if action.deadline:
        score += 50
        try:
            deadline_dt = datetime.fromisoformat(action.deadline)
            days_left = (deadline_dt - datetime.now()).days
            score += max(0, 100 - days_left)
        except:
            pass

    action_text = " ".join(action.action).lower()
    if any(v in action_text for v in HIGH_ACTIONS):
        score += 50

    if action.priority.lower() == "high":
        score += 50

    return score


def rank_actions(actions: List[ActionItem]) -> List[ActionItem]:
    return sorted(actions, key=score_action, reverse=True)

def format_sticky(actions: List[ActionItem]) -> str:
    lines = []

    for a in actions:
        for act in a.action:
            line = f"• {act}"
            if a.deadline:
                line += f" (by {a.deadline})"
            lines.append(line)

            # Context line (subject + sender)
            subject = a.subject
            sender = getattr(a, "sender", None)

            if sender:
                lines.append(f"  ↳ {subject} — {sender}")
            else:
                lines.append(f"  ↳ {subject}")

            lines.append("")  # spacing between tasks

    return "\n".join(lines).strip()



if __name__ == "__main__":

    docs = retrieve_relevant_emails("deadline submit reply", k=2)
    actions = extract_actions_from_docs(docs)

    ranked = rank_actions(actions)

    print("\n=== STICKY NOTE ===\n")
    print("Sticky Note:\n",format_sticky(ranked))

