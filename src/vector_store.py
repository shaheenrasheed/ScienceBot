import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import Config
import pickle
import os

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.index = None
        self.chunks = [] # To store the actual text corresponding to vectors

    def create_index(self, chunks):
        """Creates FAISS index from text chunks."""
        print("Generating embeddings (this might take a moment on M3)...")
        texts = [c['text'] for c in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # FAISS setup
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        self.chunks = chunks
        
        print("Vector Database built successfully.")

    def search(self, query, k=3):
        """Returns top k relevant chunks."""
        query_vector = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                results.append(self.chunks[idx])
        return results