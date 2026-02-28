import os
# New 2026 Import Paths
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Directories
DATA_PATH = "data/"
DB_PATH = "vector_store/db"

def build_vector_store():
    """Loads PDFs, splits into chunks, and saves to a local vector database."""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        return "Please add PDFs to the 'data' folder first."

    # 1. Load PDFs
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    
    if not documents:
        return "No documents found in the data folder."
    
    # 2. Split Text 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Create Embeddings (Local & Free)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 4. Save to Disk
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    # Note: .persist() is now handled automatically in newer Chroma versions, 
    # but we keep it for backward compatibility.
    return "Vector store built successfully!"

def get_retriever():
    """Returns a retriever object to find relevant medical snippets."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    return vector_db.as_retriever(search_kwargs={"k": 3})