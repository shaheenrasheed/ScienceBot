import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="data/.env")

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_DOCS_ID = os.getenv("GOOGLE_DOCS_ID") # Create a blank Doc and get ID from URL
    
    # Paths
    PDF_PATH = "data/textbook.pdf"
    VECTOR_DB_PATH = "data/faiss_index"
    KG_PATH = "data/knowledge_graph.pkl"
    
    # Models
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "gemini-2.0-flash" # Fast and free
    
    # Parsing
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 50