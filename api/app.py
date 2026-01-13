"""
Flask API Backend untuk Chatbot Dispusipda
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import API_CONFIG, CHATBOT_CONFIG
from services.chatbot_service import get_chatbot_service
from database.db_manager import get_db_manager

# Initialize Flask app
app = Flask(__name__)

# Configure CORS - allow all origins for development
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Initialize services (lazy loading)
chatbot = None
db = None

def get_services():
    """Lazy load services"""
    global chatbot, db
    if chatbot is None:
        chatbot = get_chatbot_service()
    if db is None:
        db = get_db_manager()
    return chatbot, db


# ==================== API ROUTES ====================

# Serve frontend static files (CSS, JS)
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    return send_from_directory(frontend_path, filename)


# Serve logo files
@app.route('/logo/<path:filename>')
def serve_logo(filename):
    """Serve logo files from frontend/logo directory"""
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'logo')
    return send_from_directory(logo_path, filename)


@app.route('/')
def index():
    """Serve the chatbot widget HTML"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    return send_from_directory(frontend_path, 'chatbot-widget.html')


@app.route('/presentasi')
def presentasi():
    """Serve the presentation version for seminar"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    return send_from_directory(frontend_path, 'chatbot-presentasi.html')


@app.route('/api/status')
def api_status():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Chatbot Dispusipda Pekanbaru',
        'version': '1.0.0'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check - just return ok"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chatbot Dispusipda',
        'message': 'Server is running'
    })


@app.route('/api/health/detailed', methods=['GET'])
def health_check_detailed():
    """Detailed health check with database status"""
    try:
        chatbot, db = get_services()
        
        # Check database connection
        db_status = 'ok'
        try:
            db.get_all_categories()
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        # Check embeddings
        embeddings_status = 'ok' if chatbot.embeddings_cache is not None else 'not loaded'
        faq_count = len(chatbot.faq_cache) if chatbot.faq_cache else 0
        
        return jsonify({
            'status': 'ok',
            'database': db_status,
            'embeddings': embeddings_status,
            'faq_count': faq_count,
            'llm_provider': CHATBOT_CONFIG['llm_provider']
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    
    Request body:
    {
        "message": "Pertanyaan pengguna",
        "session_id": "optional-session-id"
    }
    
    Response:
    {
        "session_id": "session-uuid",
        "response": "Jawaban chatbot",
        "matched_faqs": [...],
        "response_time_ms": 123
    }
    """
    try:
        chatbot_service, _ = get_services()
        
        # Get request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400
        
        session_id = data.get('session_id')
        
        # Get user info for logging
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        # Process chat
        response = chatbot_service.chat(
            message=message,
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return jsonify(response)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/greeting', methods=['GET'])
def get_greeting():
    """Get greeting message"""
    try:
        chatbot_service, _ = get_services()
        return jsonify({
            'greeting': chatbot_service.get_greeting()
        })
    except Exception as e:
        return jsonify({
            'greeting': CHATBOT_CONFIG['greeting_message']
        })


@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get suggested questions"""
    try:
        chatbot_service, _ = get_services()
        limit = request.args.get('limit', 5, type=int)
        suggestions = chatbot_service.get_suggested_questions(limit=limit)
        return jsonify({
            'suggestions': suggestions
        })
    except Exception as e:
        return jsonify({
            'suggestions': [
                'Bagaimana cara mendaftar anggota?',
                'Jam buka perpustakaan?',
                'Apa saja layanan yang tersedia?'
            ]
        })


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for FAQ response
    
    Request body:
    {
        "faq_id": 123,
        "is_helpful": true
    }
    """
    try:
        chatbot_service, _ = get_services()
        
        data = request.get_json()
        if not data or 'faq_id' not in data or 'is_helpful' not in data:
            return jsonify({
                'error': 'Missing required fields: faq_id, is_helpful'
            }), 400
        
        success = chatbot_service.submit_feedback(
            faq_id=data['faq_id'],
            is_helpful=data['is_helpful'],
            session_id=data.get('session_id')
        )
        
        return jsonify({
            'success': success
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all FAQ categories"""
    try:
        _, db = get_services()
        categories = db.get_all_categories()
        return jsonify({
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    """Get all FAQs (optional: filter by category)"""
    try:
        _, db = get_services()
        faqs = db.get_all_faqs()
        
        # Optional category filter
        category = request.args.get('category')
        if category:
            faqs = [f for f in faqs if f.get('category') == category]
        
        return jsonify({
            'faqs': faqs,
            'total': len(faqs)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get chat statistics"""
    try:
        _, db = get_services()
        days = request.args.get('days', 30, type=int)
        stats = db.get_chat_statistics(days=days)
        popular_faqs = db.get_popular_faqs(limit=10)
        
        return jsonify({
            'statistics': stats,
            'popular_faqs': popular_faqs
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/reload-cache', methods=['POST'])
def reload_cache():
    """Reload embeddings cache (admin endpoint)"""
    try:
        chatbot_service, _ = get_services()
        chatbot_service.reload_cache()
        return jsonify({
            'success': True,
            'message': 'Cache reloaded successfully',
            'faq_count': len(chatbot_service.faq_cache) if chatbot_service.faq_cache else 0
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error'
    }), 500


# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("="*60)
    print("CHATBOT API SERVER - DISPUSIPDA PEKANBARU")
    print("="*60)
    print(f"Starting server on {API_CONFIG['host']}:{API_CONFIG['port']}")
    print(f"Debug mode: {API_CONFIG['debug']}")
    print(f"LLM Provider: {CHATBOT_CONFIG['llm_provider']}")
    print("="*60)
    
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
