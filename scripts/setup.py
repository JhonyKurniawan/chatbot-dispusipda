"""
Setup Script - Inisialisasi lengkap sistem chatbot
Jalankan script ini untuk setup awal
"""

import subprocess
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_command(command, description):
    """Run a command and print output"""
    print(f"\n{'='*60}")
    print(f"[STEP] {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.output}")
        return False


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("\n" + "="*60)
    print("CHECKING PREREQUISITES")
    print("="*60)
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    if sys.version_info < (3, 8):
        print("Warning: Python 3.8+ recommended")
    
    # Check if .env exists
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_file):
        print("\n⚠️  File .env tidak ditemukan!")
        print("   Salin .env.example menjadi .env dan isi konfigurasi")
        return False
    
    print("\n✓ File .env ditemukan")
    return True


def setup_database():
    """Setup MySQL database"""
    print("\n" + "="*60)
    print("SETUP DATABASE")
    print("="*60)
    
    try:
        from database.db_manager import get_db_manager
        db = get_db_manager()
        
        # Test connection
        categories = db.get_all_categories()
        print(f"✓ Database terkoneksi")
        print(f"✓ Ditemukan {len(categories)} categories")
        return True
    except Exception as e:
        print(f"✗ Error database: {e}")
        print("\nPastikan:")
        print("1. MySQL server sudah berjalan")
        print("2. Database sudah dibuat (jalankan database/schema.sql)")
        print("3. Konfigurasi .env sudah benar")
        return False


def import_faqs():
    """Import FAQs ke database"""
    print("\n" + "="*60)
    print("IMPORT FAQ")
    print("="*60)
    
    try:
        from scripts.import_faqs import import_default_faqs
        import_default_faqs()
        return True
    except Exception as e:
        print(f"✗ Error import FAQ: {e}")
        return False


def generate_embeddings():
    """Generate embeddings untuk FAQ"""
    print("\n" + "="*60)
    print("GENERATE EMBEDDINGS")
    print("="*60)
    
    try:
        from scripts.generate_embeddings import generate_embeddings as gen_emb
        gen_emb()
        return True
    except Exception as e:
        print(f"✗ Error generate embeddings: {e}")
        return False


def test_chatbot():
    """Test chatbot"""
    print("\n" + "="*60)
    print("TEST CHATBOT")
    print("="*60)
    
    try:
        from services.chatbot_service import get_chatbot_service
        
        chatbot = get_chatbot_service()
        
        # Test greeting
        print(f"\nGreeting: {chatbot.get_greeting()}")
        
        # Test chat
        test_questions = [
            "Bagaimana cara mendaftar anggota?",
            "Jam buka perpustakaan?"
        ]
        
        for question in test_questions:
            print(f"\nQ: {question}")
            response = chatbot.chat(question)
            print(f"A: {response['response'][:200]}...")
            print(f"   (Time: {response['response_time_ms']}ms)")
        
        print("\n✓ Chatbot berfungsi dengan baik!")
        return True
    except Exception as e:
        print(f"✗ Error test chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║       SETUP CHATBOT FAQ - DISPUSIPDA PEKANBARU              ║
╠══════════════════════════════════════════════════════════════╣
║  Script ini akan:                                            ║
║  1. Memeriksa prerequisites                                  ║
║  2. Setup koneksi database                                   ║
║  3. Import FAQ default                                       ║
║  4. Generate embeddings                                      ║
║  5. Test chatbot                                             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites tidak terpenuhi. Setup dibatalkan.")
        return False
    
    # Step 2: Setup database
    if not setup_database():
        print("\n❌ Database tidak siap. Setup dibatalkan.")
        return False
    
    # Step 3: Import FAQs
    if not import_faqs():
        print("\n❌ Import FAQ gagal. Setup dibatalkan.")
        return False
    
    # Step 4: Generate embeddings
    if not generate_embeddings():
        print("\n❌ Generate embeddings gagal. Setup dibatalkan.")
        return False
    
    # Step 5: Test chatbot
    if not test_chatbot():
        print("\n⚠️ Test chatbot gagal, tapi setup mungkin masih berhasil.")
    
    # Summary
    print("\n" + "="*60)
    print("✅ SETUP SELESAI!")
    print("="*60)
    print("""
Langkah selanjutnya:
1. Jalankan API server:
   python api/app.py

2. Buka browser dan test endpoint:
   http://localhost:5000/api/health

3. Embed widget ke website PHP Anda:
   - Salin frontend/chatbot-widget.js ke folder website
   - Lihat contoh di frontend/example-implementation.php
    """)
    
    return True


if __name__ == "__main__":
    main()
