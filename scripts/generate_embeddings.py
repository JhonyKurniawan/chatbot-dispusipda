"""
Script untuk generate embeddings dari FAQ
Jalankan setelah import FAQ ke database
"""

import json
import sys
import os
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import EMBEDDING_CONFIG
from database.db_manager import get_db_manager
from services.embedding_service import get_embedding_service


def generate_embeddings():
    """Generate embeddings untuk semua FAQ di database"""
    print("="*60)
    print("GENERATE FAQ EMBEDDINGS")
    print("="*60)
    
    # Initialize services
    db = get_db_manager()
    embedding_service = get_embedding_service()
    
    # Get all FAQs
    print("\n[1/3] Mengambil FAQ dari database...")
    faqs = db.get_all_faqs()
    print(f"Ditemukan {len(faqs)} FAQ")
    
    if not faqs:
        print("Tidak ada FAQ untuk diproses!")
        return
    
    # Prepare texts for embedding
    print("\n[2/3] Generating embeddings...")
    texts = []
    faq_ids = []
    
    for faq in faqs:
        # Combine question, answer, and keywords for better semantic representation
        combined_text = f"{faq['question']} {faq['answer']} {faq.get('keywords', '')}"
        texts.append(combined_text)
        faq_ids.append(faq['id'])
    
    # Generate embeddings in batches
    embeddings = embedding_service.encode(texts, show_progress=True)
    
    # Save embeddings to database
    print("\n[3/3] Menyimpan embeddings ke database...")
    for i, (faq_id, embedding) in enumerate(tqdm(zip(faq_ids, embeddings), total=len(faq_ids))):
        db.save_embedding(
            faq_id=faq_id,
            embedding_vector=embedding,
            model_name=EMBEDDING_CONFIG['model_name'],
            dimension=EMBEDDING_CONFIG['embedding_dimension']
        )
    
    # Log event
    db.log_event('embedding', f'Generated embeddings for {len(faq_ids)} FAQs', {
        'model': EMBEDDING_CONFIG['model_name'],
        'dimension': EMBEDDING_CONFIG['embedding_dimension']
    })
    
    print("\n" + "="*60)
    print("SELESAI!")
    print(f"Total embeddings generated: {len(faq_ids)}")
    print("="*60)


def regenerate_missing_embeddings():
    """Generate embeddings hanya untuk FAQ yang belum punya embedding"""
    print("Checking for FAQs without embeddings...")
    
    db = get_db_manager()
    embedding_service = get_embedding_service()
    
    # Get FAQs without embeddings
    faqs = db.get_faqs_without_embeddings()
    
    if not faqs:
        print("Semua FAQ sudah memiliki embeddings!")
        return
    
    print(f"Ditemukan {len(faqs)} FAQ tanpa embeddings")
    
    for faq in tqdm(faqs):
        combined_text = f"{faq['question']} {faq['answer']} {faq.get('keywords', '')}"
        embedding = embedding_service.encode_single(combined_text)
        
        db.save_embedding(
            faq_id=faq['id'],
            embedding_vector=embedding,
            model_name=EMBEDDING_CONFIG['model_name'],
            dimension=EMBEDDING_CONFIG['embedding_dimension']
        )
    
    print(f"Generated {len(faqs)} missing embeddings")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate FAQ embeddings')
    parser.add_argument('--missing-only', action='store_true', help='Only generate for FAQs without embeddings')
    args = parser.parse_args()
    
    if args.missing_only:
        regenerate_missing_embeddings()
    else:
        generate_embeddings()
