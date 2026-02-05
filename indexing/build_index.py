from ingestion.email_loader import load_emails
from langchain_community.embeddings import  OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


emails = load_emails("D:\Code_Work\Repository\AgenticAI\Email_action_RAG\Emails\emails.json")


'''
We can't use RecursiveCharacterTextSplitter.split_documents() expects a list of LangChain Document objects, not raw dicts.
So  we convert the Emails to  Langchain Documents  
'''

def convert_email_to_document(email):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
    )

    documents = []
    for email in emails:
        chunks = text_splitter.split_text(email["body"])

        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "email_id": email["id"],
                        "subject": email["subject"],
                        "sender": email["sender"],
                        "received_at": email["received_at"],
                        "labels": email["labels"]
                    }
                )
            )
    return documents


# embedding = OllamaEmbeddings(model="embeddinggemma:latest")
embedding =  OllamaEmbeddings(model="mahonzhan/all-MiniLM-L6-v2")
documents = convert_email_to_document(emails)

vectorstore_db = FAISS.from_documents(
    documents,
    embedding
)

vectorstore_db.save_local("D:\\Code_Work\\Repository\\AgenticAI\\Email_action_RAG\\data\\email_faiss_index")

'''
Verying the  implementation
'''

vectorstore = FAISS.load_local(
    "D:\\Code_Work\\Repository\\AgenticAI\\Email_action_RAG\\data\\email_faiss_index",
    embedding,
    allow_dangerous_deserialization=True
)

results = vectorstore.similarity_search("assignment deadline", k=5)

for doc in results:
    print(doc.metadata)
    print("-" * 20) 