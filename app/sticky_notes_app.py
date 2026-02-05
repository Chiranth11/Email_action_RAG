import streamlit as st
import time

from retrieval.email_retriever import retrieve_relevant_emails
from generation.action_extractor import extract_actions_from_docs
from ranking.action_ranker import rank_actions, format_sticky

st.set_page_config(
    page_title="Email Action Sticky Notes",
    layout="centered"
)

st.title("📝 Action Sticky Notes")

REFRESH_SECONDS = 180  # 3 minutes

def run_pipeline():
    docs = retrieve_relevant_emails(
        "deadline submit reply event registration",
        k=3
    )

    actions = extract_actions_from_docs(docs)
    ranked_actions = rank_actions(actions)

    return format_sticky(ranked_actions)

# Display Sticky Note Content

content = run_pipeline()

if content.strip():
    st.markdown(
        f"""
        <div style="
            background-color:#fff9c4;
            padding:20px;
            border-radius:10px;
            box-shadow:2px 2px 10px rgba(0,0,0,0.1);
            font-size:16px;
            white-space:pre-line;
        ">
        {content}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("No actionable items found 🎉")


# Auto-Refresh (Simple & Reliable)

st.caption(f"Last updated: {time.strftime('%H:%M:%S')}")
time.sleep(REFRESH_SECONDS)
st.rerun()
