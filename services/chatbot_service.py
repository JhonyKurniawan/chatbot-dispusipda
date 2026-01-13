"""
Chatbot Service untuk Dispusipda
Menggabungkan semantic search dan LLM untuk menjawab pertanyaan
"""

import numpy as np
import time
import uuid
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import CHATBOT_CONFIG, EMBEDDING_CONFIG
from services.embedding_service import get_embedding_service
from services.llm_service import get_llm_service
from database.db_manager import get_db_manager


class ChatbotService:
    """Main chatbot service yang menggabungkan semua komponen"""
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.llm_service = get_llm_service()
        self.db = get_db_manager()
        
        # Cache embeddings in memory for faster search
        self.faq_cache = None
        self.embeddings_cache = None
        self._load_embeddings_cache()
    
    def _load_embeddings_cache(self):
        """Load semua embeddings ke memory untuk fast search"""
        try:
            print("Loading FAQ embeddings to cache...")
            faqs_with_embeddings = self.db.get_all_embeddings()
            
            if not faqs_with_embeddings:
                print("Warning: No embeddings found in database")
                return
            
            self.faq_cache = []
            embeddings_list = []
            
            for faq in faqs_with_embeddings:
                self.faq_cache.append({
                    'id': faq['faq_id'],
                    'question': faq['question'],
                    'answer': faq['answer'],
                    'keywords': faq['keywords'],
                    'category': faq['category']
                })
                embeddings_list.append(faq['embedding_vector'])
            
            self.embeddings_cache = np.array(embeddings_list, dtype=np.float32)
            print(f"Loaded {len(self.faq_cache)} FAQs to cache")
            
        except Exception as e:
            print(f"Error loading embeddings cache: {e}")
            self.faq_cache = []
            self.embeddings_cache = None
    
    def reload_cache(self):
        """Reload embeddings cache (setelah update data)"""
        self._load_embeddings_cache()
    
    def semantic_search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Search FAQ menggunakan semantic similarity
        
        Args:
            query: User query
            top_k: Number of results to return
            
        Returns:
            List of matched FAQs with similarity scores
        """
        if self.embeddings_cache is None or len(self.faq_cache) == 0:
            print("Warning: No embeddings in cache, falling back to fulltext search")
            return self._fallback_search(query)
        
        top_k = top_k or CHATBOT_CONFIG['top_k_results']
        
        # Encode query
        query_embedding = self.embedding_service.encode_single(query)
        
        # Find similar
        similar_results = self.embedding_service.find_similar(
            query_embedding,
            self.embeddings_cache,
            top_k=top_k
        )
        
        # Build results
        results = []
        for idx, similarity in similar_results:
            if similarity >= CHATBOT_CONFIG['similarity_threshold']:
                faq = self.faq_cache[idx].copy()
                faq['similarity'] = similarity
                results.append(faq)
                
                # Increment view count
                self.db.increment_faq_view(faq['id'])
        
        return results
    
    def _fallback_search(self, query: str) -> List[Dict]:
        """Fallback ke MySQL fulltext search jika embeddings tidak tersedia"""
        results = self.db.search_faqs_fulltext(query, limit=CHATBOT_CONFIG['top_k_results'])
        for result in results:
            result['similarity'] = min(result.get('score', 0) / 10, 1.0)  # Normalize score
        return results
    
    def get_or_create_session(self, session_id: str = None, user_agent: str = '', ip_address: str = '') -> str:
        """Get existing session or create new one"""
        if session_id:
            # Check if session exists in database
            if not self.db.session_exists(session_id):
                # Session ID from frontend doesn't exist, create it
                self.db.create_session(session_id, user_agent, ip_address)
        else:
            # No session ID provided, create new one
            session_id = str(uuid.uuid4())
            self.db.create_session(session_id, user_agent, ip_address)
        return session_id
    
    def chat(self, message: str, session_id: str = None, user_agent: str = '', ip_address: str = '') -> Dict:
        """
        Main chat function
        
        Args:
            message: User message
            session_id: Optional session ID
            user_agent: User agent string
            ip_address: User IP address
            
        Returns:
            Response dictionary with answer and metadata
        """
        start_time = time.time()
        
        # Get or create session
        session_id = self.get_or_create_session(session_id, user_agent, ip_address)
        
        # Save user message
        self.db.save_chat_message(session_id, 'user', message)
        
        # Search for relevant FAQs
        matched_faqs = self.semantic_search(message)
        
        # Get chat history for context
        chat_history = self.db.get_session_history(session_id, limit=6)
        
        # Generate response
        if matched_faqs:
            # Use LLM to generate natural response based on FAQs
            response_text = self.llm_service.generate_response(
                message,
                matched_faqs,
                chat_history
            )
        else:
            # No relevant FAQs found
            response_text = CHATBOT_CONFIG['fallback_message']
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Save assistant message
        matched_faq_ids = [faq['id'] for faq in matched_faqs]
        similarity_scores = [faq['similarity'] for faq in matched_faqs]
        
        self.db.save_chat_message(
            session_id,
            'assistant',
            response_text,
            matched_faq_ids,
            similarity_scores,
            response_time_ms
        )
        
        # Log event
        self.db.log_event('chat', f'Chat response generated', {
            'session_id': session_id,
            'query_length': len(message),
            'matched_faqs': len(matched_faqs),
            'response_time_ms': response_time_ms
        })
        
        return {
            'session_id': session_id,
            'response': response_text,
            'matched_faqs': [
                {
                    'id': faq['id'],
                    'question': faq['question'],
                    'similarity': faq['similarity'],
                    'category': faq.get('category', 'umum')
                }
                for faq in matched_faqs[:3]  # Return top 3 matches
            ],
            'response_time_ms': response_time_ms
        }
    
    def get_greeting(self) -> str:
        """Get greeting message"""
        return CHATBOT_CONFIG['greeting_message']
    
    def submit_feedback(self, faq_id: int, is_helpful: bool, session_id: str = None) -> bool:
        """Submit feedback for FAQ"""
        try:
            self.db.update_faq_helpfulness(faq_id, is_helpful, session_id)
            return True
        except Exception as e:
            print(f"Error submitting feedback: {e}")
            return False
    
    def get_suggested_questions(self, category: str = None, limit: int = 5) -> List[str]:
        """Get suggested questions"""
        faqs = self.db.get_popular_faqs(limit=limit)
        return [faq['question'] for faq in faqs]


# Singleton instance
_chatbot_service = None

def get_chatbot_service():
    """Get singleton chatbot service instance"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service


if __name__ == "__main__":
    # Test chatbot service
    chatbot = get_chatbot_service()
    
    # Test greeting
    print("Greeting:", chatbot.get_greeting())
    print()
    
    # Test chat
    test_questions = [
        "Bagaimana cara mendaftar anggota?",
        "Jam buka perpustakaan hari apa saja?",
        "Apa saja koleksi yang tersedia?",
        "Berapa denda keterlambatan?"
    ]
    
    for question in test_questions:
        print(f"Q: {question}")
        response = chatbot.chat(question)
        print(f"A: {response['response']}")
        print(f"   (Response time: {response['response_time_ms']}ms)")
        print()
