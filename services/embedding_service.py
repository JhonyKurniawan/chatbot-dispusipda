"""
Embedding Service untuk Chatbot Dispusipda
Menggunakan Sentence Transformers (lokal) untuk semantic search
Tidak membutuhkan API key - model dijalankan langsung di komputer
"""

import numpy as np
import os
from typing import List, Tuple
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import EMBEDDING_CONFIG


class EmbeddingService:
    """Service untuk mengelola embeddings menggunakan Sentence Transformers (lokal)"""
    
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model_name = EMBEDDING_CONFIG['model_name']
        self.dimension = EMBEDDING_CONFIG['embedding_dimension']
        print(f"Loading embedding model '{self.model_name}' (pertama kali akan download ~500MB)...")
        self.model = SentenceTransformer(self.model_name)
        print(f"Embedding service initialized (local mode)")
    
    def encode(self, texts: List[str], show_progress: bool = False) -> np.ndarray:
        """
        Encode texts menjadi embeddings secara lokal
        
        Args:
            texts: List of texts to encode
            show_progress: Show progress bar
            
        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts, 
            show_progress_bar=show_progress,
            normalize_embeddings=True,  # Sudah normalized untuk cosine similarity
            batch_size=EMBEDDING_CONFIG.get('batch_size', 32)
        )
        
        return np.array(embeddings, dtype=np.float32)
    
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
