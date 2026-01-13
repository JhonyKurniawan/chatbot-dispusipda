"""
Konfigurasi aplikasi chatbot Dispusipda Pekanbaru
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== DATABASE CONFIG ====================
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'chatbot_dispusipda'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# ==================== WEB SCRAPING CONFIG ====================
SCRAPING_CONFIG = {
    'base_url': 'https://dispusipda.pekanbaru.go.id/',
    'max_pages': 100,  # Maksimal halaman yang di-scrape
    'delay_between_requests': 1,  # Detik antara request
    'timeout': 30,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'excluded_extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'],
    'excluded_paths': ['/wp-admin', '/wp-login', '/wp-includes', '/feed', '/comment']
}

# ==================== AI/ML CONFIG ====================
# Sentence Transformer untuk embeddings
EMBEDDING_CONFIG = {
    'model_name': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Model multilingual untuk Bahasa Indonesia
    'embedding_dimension': 384,
    'batch_size': 32
}

# Groq API Config (Primary)
GROQ_CONFIG = {
    'api_key': os.getenv('GROQ_API_KEY', ''),
    'model': 'llama-3.3-70b-versatile',  # Model terbaru yang powerful dan cepat
    'max_tokens': 1024,
    'temperature': 0.7
}

# Google Gemini API Config (Alternative)
GEMINI_CONFIG = {
    'api_key': os.getenv('GEMINI_API_KEY', ''),
    'model': 'gemini-2.0-flash',  # Model terbaru yang cepat
    'max_tokens': 1024,
    'temperature': 0.7
}

# ==================== CHATBOT CONFIG ====================
CHATBOT_CONFIG = {
    'llm_provider': os.getenv('LLM_PROVIDER', 'groq'),  # 'groq' atau 'gemini'
    'similarity_threshold': 0.5,  # Threshold minimum untuk FAQ match
    'top_k_results': 5,  # Jumlah FAQ teratas yang diambil
    'greeting_message': 'Halo! 👋 Saya asisten virtual Dispusipda Pekanbaru. Ada yang bisa saya bantu tentang layanan perpustakaan?',
    'fallback_message': 'Maaf, saya tidak menemukan informasi yang relevan. Silakan hubungi petugas perpustakaan untuk bantuan lebih lanjut atau kunjungi website resmi kami.',
    'system_prompt': """Anda adalah asisten virtual Dinas Perpustakaan dan Kearsipan (Dispusipda) Kota Pekanbaru. 
Tugas Anda adalah membantu pengunjung dengan informasi tentang:
- Layanan perpustakaan (peminjaman, pengembalian, perpanjangan)
- Keanggotaan dan cara mendaftar
- Koleksi buku dan katalog
- Jam operasional dan lokasi
- Program dan kegiatan perpustakaan
- Layanan digital dan e-resources

Jawab dalam Bahasa Indonesia yang ramah, sopan, dan informatif.
Berikan jawaban yang singkat, jelas, dan langsung ke poinnya.
Jika tidak yakin dengan jawabannya, sarankan untuk menghubungi petugas perpustakaan."""
}

# ==================== FLASK API CONFIG ====================
API_CONFIG = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', 5000)),
    'debug': os.getenv('API_DEBUG', 'False').lower() == 'true',
    'cors_origins': os.getenv('CORS_ORIGINS', '*').split(',')
}

# ==================== AUTO UPDATE CONFIG ====================
AUTO_UPDATE_CONFIG = {
    'enabled': os.getenv('AUTO_UPDATE_ENABLED', 'False').lower() == 'true',
    'interval_hours': int(os.getenv('AUTO_UPDATE_INTERVAL', 24)),  # Interval re-scraping dalam jam
    'log_file': 'logs/auto_update.log'
}
