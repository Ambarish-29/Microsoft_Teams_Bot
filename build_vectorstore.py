import os
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

# Load environment variables if needed (e.g., GEMINI_API_KEY)
from dotenv import load_dotenv
load_dotenv()

# Function to load text files from a folder and create Document objects
def load_documents_from_folder(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append(Document(page_content=content, metadata={"source": filename}))
    return documents

def build_and_save_vectorstore(docs_folder, save_folder):
    print(f"Loading documents from {docs_folder}")
    documents = load_documents_from_folder(docs_folder)
    print(f"Loaded {len(documents)} documents")

    print("Creating embeddings...")
    embeddings = OpenAIEmbeddings()  # Uses OpenAI API key from env

    print("Building FAISS vector store...")
    vectorstore = FAISS.from_documents(documents, embeddings)

    print(f"Saving vectorstore to {save_folder} ...")
    vectorstore.save_local(save_folder)
    print("Done.")

if __name__ == "__main__":
    # Example usage for two agents
    agents_docs = {
        "team_help_bot": "docs/team_help",  # folder with text files for TeamHelpBot
        "hr_bot": "docs/hr_docs"            # folder with text files for HRBot
    }

    for agent_name, docs_folder in agents_docs.items():
        save_folder = f"vectorstores/{agent_name}"
        os.makedirs(save_folder, exist_ok=True)
        build_and_save_vectorstore(docs_folder, save_folder)
