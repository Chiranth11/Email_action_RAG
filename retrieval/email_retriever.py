from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

embedding = OllamaEmbeddings(model="mahonzhan/all-MiniLM-L6-v2")

vectorstore = FAISS.load_local(
    "D:\Code_Work\Repository\AgenticAI\Email_action_RAG\data\email_faiss_index",
    embedding,
    allow_dangerous_deserialization=True
)

def retrieve_relevant_emails(query: str, k: int = 5):
    # Step 1: initial similarity search
    initial_docs = vectorstore.similarity_search(query, k=k)

    # Step 2: collect matched email_ids
    email_ids = set(d.metadata["email_id"] for d in initial_docs)

    # Step 3: expand to ALL chunks for those emails
    all_docs = vectorstore.docstore._dict.values()
    full_docs = [
        d for d in all_docs
        if d.metadata["email_id"] in email_ids
    ]

    return full_docs


QUERIES = [
    "deadline submit assignment",
    "reply required email",
    "upcoming event registration"
]

if __name__ == "__main__":
    for q in QUERIES:
        print(f"\nQuery: {q}")
        results = retrieve_relevant_emails(q, k=3)
        print("\n Results : \n",results)
        for r in results:
            print("\n - ", r.metadata["subject"])
