from typing import List
from generation.action_extractor import ActionItem

def evaluate_actions(actions: List[ActionItem], retrieved_docs) -> List[ActionItem]:

    for action in actions:

        email_body = None

        # Find matching source doc
        for doc in retrieved_docs:
            if doc.metadata.get("email_id") == action.source_email_id:
                email_body = doc.page_content.lower()
                break

        if not email_body:
            action.grounded = False
            action.confidence_score = 0.0
            continue

        # ---- Grounding Check ----
        grounded_hits = 0
        for act in action.action:
            if act.lower() in email_body:
                grounded_hits += 1

        action.grounded = grounded_hits > 0

        # ---- Confidence Score ----
        score = 0

        if action.grounded:
            score += 50

        if action.deadline:
            score += 20

        if action.priority.lower() == "high":
            score += 20

        # simple bonus if multiple actions found
        score += min(10, grounded_hits * 5)

        action.confidence_score = float(score)

    return actions