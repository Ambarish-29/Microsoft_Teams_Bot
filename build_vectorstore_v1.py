import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Define embedding model (offline)
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Define input/output paths
paths = {
    "hrbot": "docs/hr_docs",
    "teamhelpbot": "docs/team_help"
}
VECTORSTORE_DIR = "vectorstores"

# Splitter config
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

for agent_name, folder_path in paths.items():
    print(f"\n🔨 Building vectorstore for: {agent_name}")

    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            path = os.path.join(folder_path, filename)
            print(f"📄 Loading {filename}")
            loader = TextLoader(path)
            docs.extend(loader.load())

    print(f"🪓 Splitting {len(docs)} docs into chunks...")
    splits = text_splitter.split_documents(docs)

    print(f"🔗 Embedding & indexing {len(splits)} chunks...")
    db = FAISS.from_documents(splits, embedding_model)

    # Save to local path
    save_path = os.path.join(VECTORSTORE_DIR, agent_name)
    db.save_local(save_path)
    print(f"✅ Saved FAISS vectorstore to: {save_path}")
