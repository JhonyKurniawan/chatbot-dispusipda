"""
Auto Update Script - Re-scraping berkala dan update embeddings
Bisa dijalankan sebagai cron job atau background service
"""

import schedule
import time
import logging
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import AUTO_UPDATE_CONFIG


# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(AUTO_UPDATE_CONFIG['log_file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_scraper():
    """Jalankan web scraper"""
    logger.info("Starting web scraper...")
    try:
        from scraper.scraper import DispusipaScraper, FAQGenerator
        
        scraper = DispusipaScraper()
        scraped_data = scraper.crawl()
        scraper.save_raw_data()
        
        generator = FAQGenerator(scraped_data)
        faqs = generator.generate_faqs()
        generator.save_faqs()
        
        logger.info(f"Scraping complete: {len(scraped_data)} pages, {len(faqs)} FAQs")
        return True
    except Exception as e:
        logger.error(f"Scraper error: {e}")
        return False


def run_import():
    """Import FAQ ke database"""
    logger.info("Importing FAQs to database...")
    try:
        from scripts.import_faqs import import_faqs_from_json
        import_faqs_from_json(clear_existing=True)
        logger.info("FAQ import complete")
        return True
    except Exception as e:
        logger.error(f"Import error: {e}")
        return False


def run_embeddings():
    """Generate embeddings baru"""
    logger.info("Generating embeddings...")
    try:
        from scripts.generate_embeddings import generate_embeddings
        generate_embeddings()
        logger.info("Embeddings generation complete")
        return True
    except Exception as e:
        logger.error(f"Embeddings error: {e}")
        return False


def reload_chatbot_cache():
    """Reload cache chatbot"""
    logger.info("Reloading chatbot cache...")
    try:
        from services.chatbot_service import get_chatbot_service
        chatbot = get_chatbot_service()
        chatbot.reload_cache()
        logger.info("Cache reloaded")
        return True
    except Exception as e:
        logger.error(f"Cache reload error: {e}")
        return False


def full_update():
    """Jalankan full update: scrape -> import -> embeddings -> reload"""
    logger.info("="*60)
    logger.info(f"STARTING FULL UPDATE - {datetime.now()}")
    logger.info("="*60)
    
    start_time = time.time()
    
    # Step 1: Scrape
    if not run_scraper():
        logger.error("Update failed at scraping step")
        return False
    
    # Step 2: Import
    if not run_import():
        logger.error("Update failed at import step")
        return False
    
    # Step 3: Embeddings
    if not run_embeddings():
        logger.error("Update failed at embeddings step")
        return False
    
    # Step 4: Reload cache
    if not reload_chatbot_cache():
        logger.warning("Cache reload failed, may need manual restart")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Full update completed in {elapsed_time:.2f} seconds")
    
    # Log to database
    try:
        from database.db_manager import get_db_manager
        db = get_db_manager()
        db.log_event('scrape', 'Auto update completed', {
            'duration_seconds': elapsed_time,
            'timestamp': datetime.now().isoformat()
        })
    except:
        pass
    
    return True


def run_scheduled():
    """Jalankan scheduler untuk update berkala"""
    interval_hours = AUTO_UPDATE_CONFIG['interval_hours']
    
    logger.info(f"Starting auto-update scheduler (every {interval_hours} hours)")
    
    # Schedule the job
    schedule.every(interval_hours).hours.do(full_update)
    
    # Run immediately on start
    full_update()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def run_once():
    """Jalankan update sekali saja"""
    return full_update()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Update Script')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--scheduled', action='store_true', help='Run on schedule')
    parser.add_argument('--scrape-only', action='store_true', help='Only run scraper')
    parser.add_argument('--embeddings-only', action='store_true', help='Only regenerate embeddings')
    args = parser.parse_args()
    
    if args.scrape_only:
        run_scraper()
    elif args.embeddings_only:
        run_embeddings()
        reload_chatbot_cache()
    elif args.scheduled:
        run_scheduled()
    else:
        # Default: run once
        run_once()
