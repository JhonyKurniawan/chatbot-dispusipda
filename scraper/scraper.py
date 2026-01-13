"""
Web Scraper untuk website Dispusipda Pekanbaru
Mengumpulkan informasi dari semua halaman untuk generate FAQ
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import json
from collections import defaultdict
from tqdm import tqdm
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import SCRAPING_CONFIG


class DispusipaScraper:
    """Web scraper untuk mengumpulkan informasi dari website Dispusipda"""
    
    def __init__(self):
        self.base_url = SCRAPING_CONFIG['base_url']
        self.visited_urls = set()
        self.scraped_data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPING_CONFIG['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        
    def is_valid_url(self, url):
        """Cek apakah URL valid untuk di-scrape"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(self.base_url)
            
            # Harus dari domain yang sama
            if parsed.netloc and parsed.netloc != base_parsed.netloc:
                return False
            
            # Exclude file extensions tertentu
            for ext in SCRAPING_CONFIG['excluded_extensions']:
                if url.lower().endswith(ext):
                    return False
            
            # Exclude paths tertentu
            for path in SCRAPING_CONFIG['excluded_paths']:
                if path in url.lower():
                    return False
                    
            return True
        except:
            return False
    
    def clean_text(self, text):
        """Bersihkan teks dari karakter yang tidak perlu"""
        if not text:
            return ""
        # Hapus multiple whitespace
        text = re.sub(r'\s+', ' ', text)
        # Hapus leading/trailing whitespace
        text = text.strip()
        return text
    
    def extract_page_content(self, soup, url):
        """Extract konten penting dari halaman"""
        content = {
            'url': url,
            'title': '',
            'meta_description': '',
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'tables': [],
            'contact_info': [],
            'schedule_info': [],
            'service_info': []
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = self.clean_text(title_tag.get_text())
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content['meta_description'] = meta_desc.get('content', '')
        
        # Extract headings (h1-h4)
        for i in range(1, 5):
            for heading in soup.find_all(f'h{i}'):
                text = self.clean_text(heading.get_text())
                if text and len(text) > 3:
                    content['headings'].append({'level': i, 'text': text})
        
        # Extract paragraphs
        for p in soup.find_all('p'):
            text = self.clean_text(p.get_text())
            if text and len(text) > 20:
                content['paragraphs'].append(text)
        
        # Extract lists
        for ul in soup.find_all(['ul', 'ol']):
            items = []
            for li in ul.find_all('li', recursive=False):
                text = self.clean_text(li.get_text())
                if text:
                    items.append(text)
            if items:
                content['lists'].append(items)
        
        # Extract tables
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    text = self.clean_text(cell.get_text())
                    row_data.append(text)
                if row_data:
                    table_data.append(row_data)
            if table_data:
                content['tables'].append(table_data)
        
        # Extract contact info patterns
        text_content = soup.get_text()
        
        # Phone numbers
        phone_pattern = r'(?:telp|telepon|phone|hp|wa|whatsapp)?[:\s]*(?:\+62|62|0)[\d\s\-\.]{8,15}'
        phones = re.findall(phone_pattern, text_content, re.IGNORECASE)
        content['contact_info'].extend([p.strip() for p in phones])
        
        # Email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text_content)
        content['contact_info'].extend(emails)
        
        # Schedule/time patterns (Indonesian)
        schedule_pattern = r'(?:senin|selasa|rabu|kamis|jumat|sabtu|minggu|setiap hari)[^.]*(?:pukul|jam|wib|wita|wit)[^.]*'
        schedules = re.findall(schedule_pattern, text_content, re.IGNORECASE)
        content['schedule_info'].extend([s.strip() for s in schedules])
        
        # Time patterns
        time_pattern = r'(?:pukul|jam)\s*\d{1,2}[:.]\d{2}\s*[-–]\s*\d{1,2}[:.]\d{2}\s*(?:wib|wita|wit)?'
        times = re.findall(time_pattern, text_content, re.IGNORECASE)
        content['schedule_info'].extend([t.strip() for t in times])
        
        return content
    
    def get_all_links(self, soup, current_url):
        """Extract semua link dari halaman"""
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Convert to absolute URL
            full_url = urljoin(current_url, href)
            # Remove fragment
            full_url = full_url.split('#')[0]
            # Remove query string jika perlu
            if '?' in full_url:
                full_url = full_url.split('?')[0]
            
            if self.is_valid_url(full_url):
                links.add(full_url)
        
        return links
    
    def scrape_page(self, url):
        """Scrape satu halaman"""
        try:
            response = self.session.get(
                url, 
                timeout=SCRAPING_CONFIG['timeout'],
                verify=True
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract content
            content = self.extract_page_content(soup, url)
            
            # Get links for crawling
            links = self.get_all_links(soup, url)
            
            return content, links
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None, set()
    
    def crawl(self):
        """Crawl seluruh website"""
        print(f"Memulai crawling dari: {self.base_url}")
        
        urls_to_visit = {self.base_url}
        
        with tqdm(total=SCRAPING_CONFIG['max_pages'], desc="Scraping") as pbar:
            while urls_to_visit and len(self.visited_urls) < SCRAPING_CONFIG['max_pages']:
                url = urls_to_visit.pop()
                
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                
                content, new_links = self.scrape_page(url)
                
                if content:
                    self.scraped_data.append(content)
                    pbar.update(1)
                    pbar.set_postfix({'url': url[:50] + '...' if len(url) > 50 else url})
                
                # Add new links to visit
                for link in new_links:
                    if link not in self.visited_urls:
                        urls_to_visit.add(link)
                
                # Delay between requests
                time.sleep(SCRAPING_CONFIG['delay_between_requests'])
        
        print(f"\nSelesai! Total halaman di-scrape: {len(self.scraped_data)}")
        return self.scraped_data
    
    def save_raw_data(self, filename='data/raw_scraped_data.json'):
        """Simpan data mentah ke file JSON"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
        print(f"Data mentah disimpan ke: {filename}")


class FAQGenerator:
    """Generate FAQ terstruktur dari data scraping"""
    
    def __init__(self, scraped_data):
        self.scraped_data = scraped_data
        self.faqs = []
        
    def extract_info_by_category(self):
        """Kategorikan informasi dari data scraping"""
        categories = {
            'layanan': [],
            'keanggotaan': [],
            'koleksi': [],
            'jam_operasional': [],
            'lokasi': [],
            'kontak': [],
            'program': [],
            'digital': [],
            'umum': []
        }
        
        # Keywords untuk kategorisasi
        keywords = {
            'layanan': ['layanan', 'peminjaman', 'pengembalian', 'perpanjangan', 'baca', 'pinjam', 'kembali', 'denda', 'keterlambatan'],
            'keanggotaan': ['anggota', 'kartu', 'daftar', 'registrasi', 'membership', 'syarat', 'pendaftaran'],
            'koleksi': ['koleksi', 'buku', 'katalog', 'judul', 'penulis', 'isbn', 'ebook', 'jurnal', 'referensi'],
            'jam_operasional': ['jam', 'buka', 'tutup', 'operasional', 'senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu', 'libur', 'pukul'],
            'lokasi': ['alamat', 'lokasi', 'gedung', 'lantai', 'ruang', 'tempat', 'jalan', 'kota'],
            'kontak': ['telepon', 'telp', 'email', 'whatsapp', 'wa', 'hubungi', 'contact'],
            'program': ['program', 'kegiatan', 'acara', 'event', 'workshop', 'pelatihan', 'literasi', 'sosialisasi'],
            'digital': ['digital', 'online', 'website', 'aplikasi', 'app', 'e-library', 'e-book', 'internet']
        }
        
        for page in self.scraped_data:
            page_text = ' '.join([
                page.get('title', ''),
                page.get('meta_description', ''),
                ' '.join([h['text'] for h in page.get('headings', [])]),
                ' '.join(page.get('paragraphs', []))
            ]).lower()
            
            # Kategorisasi berdasarkan keywords
            for category, kw_list in keywords.items():
                for kw in kw_list:
                    if kw in page_text:
                        categories[category].append(page)
                        break
            
            # Informasi schedule
            if page.get('schedule_info'):
                categories['jam_operasional'].append(page)
            
            # Informasi kontak
            if page.get('contact_info'):
                categories['kontak'].append(page)
        
        return categories
    
    def generate_faqs(self):
        """Generate FAQ dari data yang dikategorikan"""
        
        # FAQ statis berdasarkan informasi umum perpustakaan
        static_faqs = [
            # Layanan
            {
                'category': 'layanan',
                'question': 'Apa saja layanan yang tersedia di Dispusipda Pekanbaru?',
                'answer': 'Dispusipda Pekanbaru menyediakan berbagai layanan meliputi: peminjaman dan pengembalian buku, layanan referensi, ruang baca, layanan anak, layanan internet/wifi gratis, perpustakaan keliling, dan layanan e-resources digital.',
                'keywords': 'layanan, fasilitas, tersedia, dispusipda'
            },
            {
                'category': 'layanan',
                'question': 'Bagaimana cara meminjam buku di perpustakaan?',
                'answer': 'Untuk meminjam buku: 1) Pastikan Anda sudah menjadi anggota perpustakaan, 2) Pilih buku yang ingin dipinjam, 3) Bawa buku ke meja sirkulasi bersama kartu anggota, 4) Petugas akan memproses peminjaman. Batas peminjaman umumnya 2-3 buku selama 7-14 hari.',
                'keywords': 'pinjam, meminjam, cara pinjam, buku'
            },
            {
                'category': 'layanan',
                'question': 'Berapa lama batas waktu peminjaman buku?',
                'answer': 'Batas waktu peminjaman buku umumnya adalah 7-14 hari kerja. Anda dapat memperpanjang masa peminjaman jika buku tidak sedang dipesan oleh anggota lain. Perpanjangan dapat dilakukan 1x untuk periode yang sama.',
                'keywords': 'batas, waktu, durasi, peminjaman, hari'
            },
            {
                'category': 'layanan',
                'question': 'Bagaimana cara memperpanjang peminjaman buku?',
                'answer': 'Perpanjangan peminjaman dapat dilakukan dengan: 1) Datang langsung ke perpustakaan dengan membawa buku dan kartu anggota, 2) Menghubungi via telepon/WhatsApp, atau 3) Melalui sistem online jika tersedia. Perpanjangan hanya bisa dilakukan jika buku tidak sedang dipesan anggota lain.',
                'keywords': 'perpanjang, perpanjangan, extend'
            },
            {
                'category': 'layanan',
                'question': 'Apakah ada denda keterlambatan pengembalian buku?',
                'answer': 'Ya, keterlambatan pengembalian buku dikenakan denda. Besaran denda bervariasi, umumnya Rp 500 - Rp 1.000 per hari per buku. Untuk informasi detail besaran denda, silakan hubungi petugas perpustakaan.',
                'keywords': 'denda, terlambat, keterlambatan, telat'
            },
            
            # Keanggotaan
            {
                'category': 'keanggotaan',
                'question': 'Bagaimana cara mendaftar menjadi anggota perpustakaan?',
                'answer': 'Untuk mendaftar menjadi anggota: 1) Datang ke perpustakaan dengan membawa KTP/kartu identitas, 2) Isi formulir pendaftaran, 3) Foto untuk kartu anggota (biasanya disediakan di tempat), 4) Kartu anggota akan diproses. Pendaftaran gratis untuk warga Pekanbaru.',
                'keywords': 'daftar, mendaftar, registrasi, anggota, member'
            },
            {
                'category': 'keanggotaan',
                'question': 'Apa saja syarat menjadi anggota perpustakaan?',
                'answer': 'Syarat menjadi anggota: 1) Warga Negara Indonesia, 2) Membawa fotokopi KTP/KK untuk dewasa atau kartu pelajar untuk pelajar, 3) Pas foto ukuran 2x3 atau 3x4 (2 lembar), 4) Mengisi formulir pendaftaran. Keanggotaan gratis untuk masyarakat umum.',
                'keywords': 'syarat, ketentuan, persyaratan, anggota'
            },
            {
                'category': 'keanggotaan',
                'question': 'Apakah pendaftaran anggota perpustakaan gratis?',
                'answer': 'Ya, pendaftaran anggota perpustakaan Dispusipda Pekanbaru GRATIS untuk seluruh masyarakat. Tidak ada biaya pembuatan kartu anggota.',
                'keywords': 'gratis, biaya, bayar, free'
            },
            {
                'category': 'keanggotaan',
                'question': 'Berapa lama masa berlaku kartu anggota?',
                'answer': 'Kartu anggota perpustakaan umumnya berlaku selama 1-2 tahun dan dapat diperpanjang. Untuk memperpanjang, cukup datang ke perpustakaan dengan membawa kartu anggota lama.',
                'keywords': 'masa berlaku, expired, kadaluarsa, perpanjang kartu'
            },
            
            # Jam Operasional
            {
                'category': 'jam_operasional',
                'question': 'Jam berapa perpustakaan buka dan tutup?',
                'answer': 'Jam operasional Dispusipda Pekanbaru: Senin-Kamis: 08.00-16.00 WIB, Jumat: 08.00-11.30 WIB dan 14.00-16.00 WIB. Sabtu-Minggu: Tutup. Jam operasional dapat berubah pada hari libur nasional.',
                'keywords': 'jam, buka, tutup, operasional, waktu'
            },
            {
                'category': 'jam_operasional',
                'question': 'Apakah perpustakaan buka di hari Sabtu dan Minggu?',
                'answer': 'Untuk informasi terkini mengenai jadwal operasional di akhir pekan, silakan menghubungi perpustakaan langsung atau cek website resmi. Umumnya perpustakaan pemerintah tutup di akhir pekan.',
                'keywords': 'sabtu, minggu, weekend, akhir pekan, libur'
            },
            {
                'category': 'jam_operasional', 
                'question': 'Apakah perpustakaan buka saat hari libur nasional?',
                'answer': 'Perpustakaan tutup pada hari libur nasional. Untuk jadwal khusus atau perubahan jam operasional, silakan cek pengumuman di website resmi atau media sosial Dispusipda Pekanbaru.',
                'keywords': 'libur, nasional, tutup, cuti'
            },
            
            # Lokasi & Kontak
            {
                'category': 'lokasi',
                'question': 'Dimana alamat Dispusipda Pekanbaru?',
                'answer': 'Dinas Perpustakaan dan Kearsipan (Dispusipda) Kota Pekanbaru berlokasi di Kota Pekanbaru, Provinsi Riau. Untuk alamat lengkap dan petunjuk arah, silakan kunjungi website resmi atau hubungi kontak yang tersedia.',
                'keywords': 'alamat, lokasi, dimana, tempat, letak'
            },
            {
                'category': 'kontak',
                'question': 'Bagaimana cara menghubungi Dispusipda Pekanbaru?',
                'answer': 'Anda dapat menghubungi Dispusipda Pekanbaru melalui: Website: https://dispusipda.pekanbaru.go.id/, atau datang langsung ke kantor perpustakaan. Untuk informasi kontak terbaru (telepon, email, WhatsApp), silakan cek website resmi.',
                'keywords': 'kontak, hubungi, telepon, telp, email, wa, whatsapp'
            },
            
            # Koleksi
            {
                'category': 'koleksi',
                'question': 'Apa saja jenis koleksi yang tersedia di perpustakaan?',
                'answer': 'Dispusipda Pekanbaru memiliki berbagai koleksi meliputi: buku fiksi dan non-fiksi, buku anak-anak, buku referensi, majalah dan surat kabar, koleksi lokal/daerah, serta koleksi digital (e-book dan e-journal).',
                'keywords': 'koleksi, buku, jenis, macam, tersedia'
            },
            {
                'category': 'koleksi',
                'question': 'Bagaimana cara mencari buku di katalog perpustakaan?',
                'answer': 'Anda dapat mencari buku melalui: 1) Komputer katalog OPAC yang tersedia di perpustakaan, 2) Bertanya langsung kepada petugas, 3) Sistem pencarian online di website perpustakaan (jika tersedia). Pencarian bisa berdasarkan judul, pengarang, atau subjek.',
                'keywords': 'cari, katalog, opac, search, pencarian'
            },
            
            # Digital/Online
            {
                'category': 'digital',
                'question': 'Apakah ada layanan perpustakaan digital atau e-book?',
                'answer': 'Ya, Dispusipda Pekanbaru menyediakan layanan digital termasuk akses e-book dan e-resources. Untuk mengakses layanan digital, Anda perlu menjadi anggota dan mendapatkan akun. Silakan hubungi petugas untuk informasi lebih lanjut.',
                'keywords': 'digital, online, e-book, ebook, internet, e-library'
            },
            {
                'category': 'digital',
                'question': 'Apakah tersedia WiFi gratis di perpustakaan?',
                'answer': 'Ya, perpustakaan menyediakan akses WiFi/internet gratis untuk pengunjung. Anda dapat menggunakan fasilitas ini untuk keperluan belajar dan penelusuran informasi.',
                'keywords': 'wifi, internet, gratis, hotspot'
            },
            
            # Program
            {
                'category': 'program',
                'question': 'Apa saja program dan kegiatan di perpustakaan?',
                'answer': 'Dispusipda Pekanbaru menyelenggarakan berbagai program seperti: storytelling untuk anak, bedah buku, pelatihan literasi, perpustakaan keliling, dan program literasi masyarakat. Informasi kegiatan terbaru dapat dilihat di website dan media sosial resmi.',
                'keywords': 'program, kegiatan, acara, event, aktivitas'
            },
            
            # Umum
            {
                'category': 'umum',
                'question': 'Apa itu Dispusipda Pekanbaru?',
                'answer': 'Dispusipda (Dinas Perpustakaan dan Kearsipan) Kota Pekanbaru adalah instansi pemerintah yang bertugas mengelola perpustakaan umum dan kearsipan daerah. Dispusipda menyediakan layanan perpustakaan gratis untuk masyarakat Kota Pekanbaru dan sekitarnya.',
                'keywords': 'dispusipda, apa, perpustakaan, dinas'
            },
            {
                'category': 'umum',
                'question': 'Siapa saja yang boleh mengunjungi perpustakaan?',
                'answer': 'Perpustakaan Dispusipda Pekanbaru terbuka untuk umum. Siapa saja boleh berkunjung untuk membaca di tempat. Untuk meminjam buku, Anda perlu menjadi anggota terlebih dahulu.',
                'keywords': 'siapa, boleh, umum, pengunjung, akses'
            }
        ]
        
        self.faqs = static_faqs
        
        # Generate FAQ tambahan dari data scraping
        categories = self.extract_info_by_category()
        
        # Tambahkan FAQ dinamis dari konten yang di-scrape
        for page in self.scraped_data:
            # Cari halaman dengan konten spesifik tentang layanan
            title = page.get('title', '').lower()
            paragraphs = page.get('paragraphs', [])
            
            if paragraphs and len(paragraphs) > 0:
                # Buat FAQ dari konten halaman jika relevan
                relevant_content = ' '.join(paragraphs[:3])  # Ambil 3 paragraf pertama
                
                if len(relevant_content) > 100:
                    # Cek apakah konten ini sudah tercakup di FAQ statis
                    is_duplicate = False
                    for faq in self.faqs:
                        if any(kw in relevant_content.lower() for kw in faq.get('keywords', '').split(', ')):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate and page.get('title'):
                        # Buat FAQ baru dari konten halaman
                        self.faqs.append({
                            'category': 'umum',
                            'question': f"Informasi tentang: {page.get('title', 'Dispusipda Pekanbaru')}",
                            'answer': relevant_content[:500] + ('...' if len(relevant_content) > 500 else ''),
                            'keywords': page.get('title', '').lower(),
                            'source_url': page.get('url', '')
                        })
        
        return self.faqs
    
    def save_faqs(self, filename='data/generated_faqs.json'):
        """Simpan FAQ ke file JSON"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.faqs, f, ensure_ascii=False, indent=2)
        print(f"FAQ disimpan ke: {filename}")
        print(f"Total FAQ: {len(self.faqs)}")


def main():
    """Main function untuk menjalankan scraper dan generator FAQ"""
    print("="*60)
    print("SCRAPER & FAQ GENERATOR - DISPUSIPDA PEKANBARU")
    print("="*60)
    
    # Step 1: Scraping website
    print("\n[1/3] Memulai web scraping...")
    scraper = DispusipaScraper()
    
    try:
        scraped_data = scraper.crawl()
        scraper.save_raw_data()
    except Exception as e:
        print(f"Error saat scraping: {e}")
        print("Menggunakan data kosong untuk generate FAQ statis...")
        scraped_data = []
    
    # Step 2: Generate FAQ
    print("\n[2/3] Generating FAQ...")
    generator = FAQGenerator(scraped_data)
    faqs = generator.generate_faqs()
    generator.save_faqs()
    
    # Step 3: Summary
    print("\n[3/3] Selesai!")
    print(f"Total halaman di-scrape: {len(scraped_data)}")
    print(f"Total FAQ dihasilkan: {len(faqs)}")
    print("\nFile output:")
    print("  - data/raw_scraped_data.json (data mentah)")
    print("  - data/generated_faqs.json (FAQ terstruktur)")
    
    return scraped_data, faqs


if __name__ == "__main__":
    main()
