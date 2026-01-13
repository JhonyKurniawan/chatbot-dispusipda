"""
Embedding Service untuk Chatbot Dispusipda
Menggunakan HuggingFace Inference API untuk semantic search (lightweight, no PyTorch)
"""

import numpy as np
import requests
import os
from typing import List, Tuple
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import EMBEDDING_CONFIG

# HuggingFace Inference API
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    """Service untuk mengelola embeddings menggunakan HuggingFace API"""
    
    def __init__(self):
        self.model_name = EMBEDDING_CONFIG['model_name']
        self.dimension = EMBEDDING_CONFIG['embedding_dimension']
        self.hf_token = os.getenv('HF_TOKEN', '')
        self.headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        print(f"Embedding service initialized (API mode)")
    
    def _call_api(self, texts: List[str]) -> List[List[float]]:
        """Call HuggingFace Inference API"""
        try:
            response = requests.post(
                HF_API_URL,
                headers=self.headers,
                json={"inputs": texts, "options": {"wait_for_model": True}},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HF API error: {response.status_code} - {response.text}")
                # Fallback: return zero vectors
                return [[0.0] * self.dimension for _ in texts]
        except Exception as e:
            print(f"HF API exception: {e}")
            return [[0.0] * self.dimension for _ in texts]
    
    def encode(self, texts: List[str], show_progress: bool = False) -> np.ndarray:
        """
        Encode texts menjadi embeddings via API
        
        Args:
            texts: List of texts to encode
            show_progress: Show progress bar (ignored in API mode)
            
        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # API has limit, batch if needed
        batch_size = 50
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings = self._call_api(batch)
            all_embeddings.extend(embeddings)
        
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        embeddings_array = embeddings_array / norms
        
        return embeddings_array
    
    def encode_single(self, text: str) -> np.ndarray:
        """Encode single text"""
        return self.encode([text])[0]
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity antara dua embeddings
        Karena embeddings sudah normalized, dot product = cosine similarity
        """
        return float(np.dot(embedding1, embedding2))
    
    def find_similar(
        self, 
        query_embedding: np.ndarray, 
        corpus_embeddings: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar embeddings dari corpus
        
        Args:
            query_embedding: Embedding dari query
            corpus_embeddings: Array of embeddings to search
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        # Calculate similarities (dot product karena sudah normalized)
        similarities = np.dot(corpus_embeddings, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [(int(idx), float(similarities[idx])) for idx in top_indices]
        return results


# Singleton instance
_embedding_service = None

def get_embedding_service():
    """Get singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


if __name__ == "__main__":
    # Test embedding service
    service = get_embedding_service()
    
    # Test encode
    texts = [
        "Bagaimana cara mendaftar anggota perpustakaan?",
        "Jam buka perpustakaan hari senin",
        "Cara meminjam buku"
    ]
    
    embeddings = service.encode(texts, show_progress=True)
    print(f"Encoded {len(texts)} texts")
    print(f"Embedding shape: {embeddings.shape}")
    
    # Test similarity
    query = "Cara daftar member perpustakaan"
    query_embedding = service.encode_single(query)
    
    print(f"\nQuery: {query}")
    print("Similarities:")
    for i, text in enumerate(texts):
        sim = service.cosine_similarity(query_embedding, embeddings[i])
        print(f"  {sim:.4f} - {text}")
