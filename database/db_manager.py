"""
Database Manager untuk Chatbot Dispusipda
Mengelola koneksi dan operasi database MySQL
"""

import mysql.connector
from mysql.connector import pooling
import json
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG


class DatabaseManager:
    """Manager untuk operasi database MySQL"""
    
    def __init__(self):
        self.pool = None
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="chatbot_pool",
                pool_size=5,
                pool_reset_session=True,
                **DB_CONFIG
            )
            print("Database connection pool initialized")
        except Exception as e:
            print(f"Error initializing database pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""
        return self.pool.get_connection()
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_many(self, query, params_list):
        """Execute multiple queries"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # ==================== CATEGORY OPERATIONS ====================
    
    def get_all_categories(self):
        """Get all active categories"""
        query = """
            SELECT id, name, description, icon, display_order 
            FROM categories 
            WHERE is_active = TRUE 
            ORDER BY display_order
        """
        return self.execute_query(query)
    
    def get_category_by_name(self, name):
        """Get category by name"""
        query = "SELECT id, name FROM categories WHERE name = %s"
        result = self.execute_query(query, (name,))
        return result[0] if result else None
    
    # ==================== FAQ OPERATIONS ====================
    
    def insert_faq(self, category_name, question, answer, keywords='', source_url=''):
        """Insert a new FAQ"""
        # Get category id
        category = self.get_category_by_name(category_name)
        category_id = category['id'] if category else None
        
        query = """
            INSERT INTO faqs (category_id, question, answer, keywords, source_url)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (category_id, question, answer, keywords, source_url), fetch=False)
    
    def insert_faqs_bulk(self, faqs_list):
        """Insert multiple FAQs"""
        inserted_ids = []
        for faq in faqs_list:
            faq_id = self.insert_faq(
                category_name=faq.get('category', 'umum'),
                question=faq['question'],
                answer=faq['answer'],
                keywords=faq.get('keywords', ''),
                source_url=faq.get('source_url', '')
            )
            inserted_ids.append(faq_id)
        return inserted_ids
    
    def get_all_faqs(self, active_only=True):
        """Get all FAQs"""
        query = """
            SELECT f.id, f.question, f.answer, f.keywords, f.source_url,
                   c.name as category, c.icon as category_icon
            FROM faqs f
            LEFT JOIN categories c ON f.category_id = c.id
        """
        if active_only:
            query += " WHERE f.is_active = TRUE"
        query += " ORDER BY f.id"
        return self.execute_query(query)
    
    def get_faq_by_id(self, faq_id):
        """Get FAQ by ID"""
        query = """
            SELECT f.id, f.question, f.answer, f.keywords,
                   c.name as category
            FROM faqs f
            LEFT JOIN categories c ON f.category_id = c.id
            WHERE f.id = %s
        """
        result = self.execute_query(query, (faq_id,))
        return result[0] if result else None
    
    def search_faqs_fulltext(self, search_term, limit=5):
        """Search FAQs using MySQL fulltext search"""
        query = """
            SELECT f.id, f.question, f.answer, f.keywords,
                   c.name as category,
                   MATCH(f.question, f.answer, f.keywords) AGAINST(%s IN NATURAL LANGUAGE MODE) as score
            FROM faqs f
            LEFT JOIN categories c ON f.category_id = c.id
            WHERE f.is_active = TRUE
            AND MATCH(f.question, f.answer, f.keywords) AGAINST(%s IN NATURAL LANGUAGE MODE)
            ORDER BY score DESC
            LIMIT %s
        """
        return self.execute_query(query, (search_term, search_term, limit))
    
    def increment_faq_view(self, faq_id):
        """Increment FAQ view count"""
        query = "UPDATE faqs SET view_count = view_count + 1 WHERE id = %s"
        self.execute_query(query, (faq_id,), fetch=False)
    
    def update_faq_helpfulness(self, faq_id, is_helpful, session_id=None):
        """Update FAQ helpfulness count and save to feedback table"""
        # Update counter di tabel faqs
        if is_helpful:
            query = "UPDATE faqs SET helpful_count = helpful_count + 1 WHERE id = %s"
        else:
            query = "UPDATE faqs SET not_helpful_count = not_helpful_count + 1 WHERE id = %s"
        self.execute_query(query, (faq_id,), fetch=False)
        
        # Simpan ke tabel feedback dengan kolom yang proper
        rating = 5 if is_helpful else 1  # 5 = helpful, 1 = not helpful
        is_helpful_int = 1 if is_helpful else 0
        
        insert_query = """
            INSERT INTO feedback (faq_id, rating, is_helpful, feedback_text) 
            VALUES (%s, %s, %s, %s)
        """
        feedback_text = 'Helpful' if is_helpful else 'Not Helpful'
        self.execute_query(insert_query, (faq_id, rating, is_helpful_int, feedback_text), fetch=False)

    
    def clear_all_faqs(self):
        """Delete all FAQs (untuk re-import)"""
        self.execute_query("DELETE FROM faq_embeddings", fetch=False)
        self.execute_query("DELETE FROM faqs", fetch=False)
        print("All FAQs cleared")
    
    # ==================== EMBEDDING OPERATIONS ====================
    
    def save_embedding(self, faq_id, embedding_vector, model_name, dimension):
        """Save embedding vector for FAQ"""
        # Convert numpy array to bytes
        embedding_bytes = embedding_vector.tobytes()
        
        query = """
            INSERT INTO faq_embeddings (faq_id, embedding_vector, embedding_model, embedding_dimension)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                embedding_vector = VALUES(embedding_vector),
                embedding_model = VALUES(embedding_model),
                updated_at = CURRENT_TIMESTAMP
        """
        self.execute_query(query, (faq_id, embedding_bytes, model_name, dimension), fetch=False)
    
    def get_all_embeddings(self):
        """Get all embeddings with FAQ data"""
        query = """
            SELECT f.id as faq_id, f.question, f.answer, f.keywords,
                   c.name as category,
                   e.embedding_vector, e.embedding_dimension
            FROM faqs f
            JOIN faq_embeddings e ON f.id = e.faq_id
            LEFT JOIN categories c ON f.category_id = c.id
            WHERE f.is_active = TRUE
        """
        results = self.execute_query(query)
        
        # Convert bytes back to numpy arrays
        for result in results:
            if result['embedding_vector']:
                result['embedding_vector'] = np.frombuffer(
                    result['embedding_vector'], 
                    dtype=np.float32
                )
        
        return results
    
    def get_faqs_without_embeddings(self):
        """Get FAQs that don't have embeddings yet"""
        query = """
            SELECT f.id, f.question, f.answer, f.keywords
            FROM faqs f
            LEFT JOIN faq_embeddings e ON f.id = e.faq_id
            WHERE e.id IS NULL AND f.is_active = TRUE
        """
        return self.execute_query(query)
    
    # ==================== CHAT SESSION OPERATIONS ====================
    
    def session_exists(self, session_id):
        """Check if session exists in database"""
        query = "SELECT 1 FROM chat_sessions WHERE id = %s LIMIT 1"
        result = self.execute_query(query, (session_id,))
        return len(result) > 0
    
    def create_session(self, session_id, user_agent='', ip_address=''):
        """Create new chat session"""
        query = """
            INSERT INTO chat_sessions (id, user_agent, ip_address)
            VALUES (%s, %s, %s)
        """
        self.execute_query(query, (session_id, user_agent, ip_address), fetch=False)
        return session_id
    
    def update_session_activity(self, session_id):
        """Update session last activity and increment message count"""
        query = """
            UPDATE chat_sessions 
            SET last_activity = CURRENT_TIMESTAMP, message_count = message_count + 1
            WHERE id = %s
        """
        self.execute_query(query, (session_id,), fetch=False)
    
    def save_chat_message(self, session_id, role, content, matched_faq_ids=None, similarity_scores=None, response_time_ms=None):
        """Save chat message"""
        query = """
            INSERT INTO chat_messages (session_id, role, content, matched_faq_ids, similarity_scores, response_time_ms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.execute_query(query, (
            session_id,
            role,
            content,
            json.dumps(matched_faq_ids) if matched_faq_ids else None,
            json.dumps(similarity_scores) if similarity_scores else None,
            response_time_ms
        ), fetch=False)
        
        # Update session activity
        self.update_session_activity(session_id)
    
    def get_session_history(self, session_id, limit=10):
        """Get chat history for session"""
        query = """
            SELECT role, content, created_at
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        results = self.execute_query(query, (session_id, limit))
        return list(reversed(results))
    
    # ==================== LOGGING OPERATIONS ====================
    
    def log_event(self, log_type, message, details=None):
        """Log system event"""
        query = """
            INSERT INTO system_logs (log_type, message, details)
            VALUES (%s, %s, %s)
        """
        self.execute_query(query, (log_type, message, json.dumps(details) if details else None), fetch=False)
    
    # ==================== STATISTICS ====================
    
    def get_chat_statistics(self, days=30):
        """Get chat statistics for last N days"""
        query = """
            SELECT 
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(*) as total_messages,
                AVG(response_time_ms) as avg_response_time
            FROM chat_messages
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        result = self.execute_query(query, (days,))
        return result[0] if result else {}
    
    def get_popular_faqs(self, limit=10):
        """Get most viewed FAQs"""
        query = """
            SELECT f.id, f.question, f.view_count, f.helpful_count,
                   c.name as category
            FROM faqs f
            LEFT JOIN categories c ON f.category_id = c.id
            WHERE f.is_active = TRUE
            ORDER BY f.view_count DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))


# Singleton instance
_db_manager = None

def get_db_manager():
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


if __name__ == "__main__":
    # Test connection
    db = get_db_manager()
    print("Testing database connection...")
    
    categories = db.get_all_categories()
    print(f"Found {len(categories)} categories")
    for cat in categories:
        print(f"  - {cat['icon']} {cat['name']}: {cat['description']}")
