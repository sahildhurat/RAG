import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# We will use HuggingFace BGE-m3 as per the architecture document.
# For local execution, BAAI/bge-m3 or BAAI/bge-small-en-v1.5 are great choices.
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5" # Using small version to fit within Render free tier (512MB RAM)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_DIRECTORY = os.path.join(PROJECT_ROOT, "chroma_db")

def get_embeddings_model():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def get_vector_store():
    """
    Initializes and returns the ChromaDB vector store.
    """
    embeddings = get_embeddings_model()
    
    # Ensure the directory exists
    os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
    
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )
    return vectorstore

def get_retriever(search_type="similarity", search_kwargs=None):
    """
    Returns a retriever configured with specific search type and arguments.
    """
    if search_kwargs is None:
        search_kwargs = {"k": 4}
        
    vectorstore = get_vector_store()
    return vectorstore.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
