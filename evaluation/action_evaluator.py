from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from generation.action_extractor import ActionItem


def semantic_similarity(text1: str, text2: str) -> float:
    """
    Computes cosine similarity between two texts using TF-IDF.
    Lightweight and fast.
    """
    docs = [text1, text2]
    tfidf = TfidfVectorizer().fit_transform(docs)
    sim_score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return sim_score


def evaluate_actions(actions: List[ActionItem], retrieved_docs) -> List[ActionItem]:

    for action in actions:

        email_body = None

        # Find matching source doc
        for doc in retrieved_docs:
            if doc.metadata.get("email_id") == action.source_email_id:
                email_body = doc.page_content
                break

        if not email_body:
            action.grounded = False
            action.confidence_score = 0.0
            continue

        grounded_hits = 0
        max_similarity = 0.0

        # ---- Semantic Grounding Check ----
        for act in action.action:
            sim = semantic_similarity(act.lower(), email_body.lower())
            max_similarity = max(max_similarity, sim)

            # Threshold can be tuned (0.3–0.5 works well)
            if sim >= 0.35:
                grounded_hits += 1

        action.grounded = grounded_hits > 0

        # ---- Confidence Score Logic ----
        score = 0

        # Grounding weight (strongest signal)
        if action.grounded:
            score += 50

        # Deadline weight
        if action.deadline:
            score += 20

        # Priority weight
        if action.priority and action.priority.lower() == "high":
            score += 20

        # Similarity bonus
        score += int(max_similarity * 10)

        action.confidence_score = float(score)

    return actions