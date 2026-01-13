"""
Script untuk import FAQ ke database
"""

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_db_manager


def import_faqs_from_json(json_file='data/generated_faqs.json', clear_existing=False):
    """Import FAQs dari file JSON ke database"""
    print("="*60)
    print("IMPORT FAQ KE DATABASE")
    print("="*60)
    
    # Check if file exists
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} tidak ditemukan!")
        print("Jalankan scraper terlebih dahulu: python scraper/scraper.py")
        return False
    
    # Load FAQs from JSON
    print(f"\n[1/3] Membaca file {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        faqs = json.load(f)
    
    print(f"Ditemukan {len(faqs)} FAQ")
    
    # Initialize database
    db = get_db_manager()
    
    # Clear existing if requested
    if clear_existing:
        print("\n[2/3] Menghapus FAQ lama...")
        db.clear_all_faqs()
    else:
        print("\n[2/3] Menambahkan ke FAQ yang ada...")
    
    # Import FAQs
    print("\n[3/3] Mengimport FAQ ke database...")
    inserted_ids = db.insert_faqs_bulk(faqs)
    
    # Log event
    db.log_event('info', f'Imported {len(inserted_ids)} FAQs', {
        'source_file': json_file,
        'clear_existing': clear_existing
    })
    
    print("\n" + "="*60)
    print("SELESAI!")
    print(f"Total FAQ diimport: {len(inserted_ids)}")
    print("="*60)
    
    return True


def import_default_faqs():
    """Import FAQ default (tanpa scraping)"""
    print("="*60)
    print("IMPORT FAQ DEFAULT")
    print("="*60)
    
    # FAQ default
    default_faqs = [
        # ==================== LAYANAN ====================
        {
            'category': 'layanan',
            'question': 'Apa saja layanan yang tersedia di Dispusipda Pekanbaru?',
            'answer': 'Dispusipda Pekanbaru menyediakan berbagai layanan: 1) Layanan Sirkulasi (peminjaman/pengembalian buku), 2) Layanan Umum dengan 18.114 judul koleksi, 3) Layanan Anak dengan 8.828 judul koleksi, 4) Layanan Referensi, 5) Layanan i-Pekanbaru (perpustakaan digital dengan 8.527 e-book), 6) Layanan Penelusuran Literatur menggunakan OPAC, 7) Layanan Perpustakaan Keliling (MPK), dan 8) Layanan Kearsipan termasuk akses SIKN-JIKN.',
            'keywords': 'layanan, fasilitas, tersedia, dispusipda, jenis layanan'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu Layanan Sirkulasi?',
            'answer': 'Layanan Sirkulasi adalah kegiatan melayani pengguna perpustakaan dalam peminjaman dan pengembalian bahan pustaka beserta penyelesaian administrasinya seperti pendaftaran anggota perpustakaan.',
            'keywords': 'sirkulasi, peminjaman, pengembalian, administrasi'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu Layanan Umum di perpustakaan?',
            'answer': 'Layanan Umum adalah layanan yang menyediakan bahan perpustakaan untuk masyarakat umum remaja hingga dewasa. Layanan Umum DISPUSIP memiliki 18.114 judul koleksi perpustakaan.',
            'keywords': 'layanan umum, remaja, dewasa, koleksi umum'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu Layanan Anak di perpustakaan?',
            'answer': 'Layanan Anak adalah pelayanan perpustakaan yang ditujukan untuk anak berumur 12-13 tahun, didalamnya termasuk kegiatan mendongeng. Layanan Anak DISPUSIP memiliki 8.828 judul koleksi perpustakaan.',
            'keywords': 'layanan anak, anak-anak, mendongeng, koleksi anak'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu Layanan Referensi?',
            'answer': 'Layanan Referensi adalah layanan yang diberikan kepada pengguna perpustakaan yang bertujuan untuk membantu mereka dalam penelusuran informasi rujukan. Layanan ini membantu menelusur informasi secara lebih spesifik dengan pilihan subyek yang lebih luas.',
            'keywords': 'referensi, rujukan, penelusuran, informasi spesifik'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu Layanan i-Pekanbaru?',
            'answer': 'Layanan i-Pekanbaru adalah perpustakaan digital berbasis aplikasi yang menyediakan 8.527 eksemplar e-book. Aplikasi iPekanbaru tersedia untuk Android dan Desktop yang dapat diunduh secara gratis melalui link: https://ipekanbaru.moco.co.id/',
            'keywords': 'ipekanbaru, i-pekanbaru, digital, aplikasi, ebook, playstore, download'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu Layanan Penelusuran Literatur?',
            'answer': 'Layanan Penelusuran Literatur adalah kegiatan mencari atau menemukan kembali informasi kepustakaan mengenai suatu bidang tertentu yang ada di perpustakaan dengan menggunakan bantuan OPAC (Online Public Access Catalogue). Anda dapat mengakses katalog online di: https://pustaka.pekanbaru.go.id/Tenas.Efendy/opac/',
            'keywords': 'penelusuran literatur, opac, katalog online, cari buku'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu Layanan Perpustakaan Keliling?',
            'answer': 'Layanan Perpustakaan Keliling adalah kegiatan layanan perpustakaan yang bergerak dari satu tempat ke tempat lain dengan menggunakan Mobil Perpustakaan Keliling (MPK). Dispusipda juga memiliki layanan SipuSiaga (Sinergikan Perpustakaan Siap Antar Kewarga) yang siap melayani kebutuhan komunitas dan masyarakat.',
            'keywords': 'perpustakaan keliling, mobil perpustakaan, mpk, keliling, sipusiaga'
        },
        {
            'category': 'layanan',
            'question': 'Apa itu SipuSiaga atau Pusteling?',
            'answer': 'SipuSiaga (Sinergikan Perpustakaan Siap Antar Kewarga) atau Pusteling adalah sistem perpustakaan siaga yang siap melayani kebutuhan komunitas dan masyarakat. Layanan ini menggunakan Mobil Perpustakaan Keliling yang dapat datang ke lokasi Anda. Untuk mengundang Pusteling, hubungi Admin di nomor: 0813 7809 1515.',
            'keywords': 'sipusiaga, pusteling, perpustakaan siaga, mobil perpustakaan, keliling, antar kewarga'
        },
        {
            'category': 'layanan',
            'question': 'Bagaimana cara mengundang Pusteling atau mobil perpustakaan keliling?',
            'answer': 'Untuk mengundang Pusteling (Perpustakaan Keliling) ke lokasi Anda, silakan hubungi Admin SipuSiaga di nomor: 0813 7809 1515. Layanan ini siap melayani kebutuhan komunitas dan masyarakat di berbagai lokasi.',
            'keywords': 'undang pusteling, hubungi, nomor telepon, kontak pusteling, mobil perpustakaan'
        },
        {
            'category': 'layanan',
            'question': 'Bagaimana cara meminjam buku di perpustakaan?',
            'answer': 'Untuk meminjam buku: 1) Pastikan Anda sudah menjadi anggota dan memiliki Kartu Tanda Anggota (KTA), 2) Pilih buku yang ingin dipinjam, 3) Bawa buku ke meja sirkulasi bersama KTA, 4) Petugas akan memproses peminjaman. Batas peminjaman maksimal 2 eksemplar dalam jangka 1 minggu. Kegiatan membaca/meminjam/mengembalikan/memperpanjang buku wajib menggunakan Kartu Tanda Anggota.',
            'keywords': 'pinjam, meminjam, cara pinjam, buku'
        },
        {
            'category': 'layanan',
            'question': 'Berapa lama batas waktu peminjaman buku?',
            'answer': 'Batas waktu peminjaman buku adalah 1 minggu. Anda dapat meminjam maksimal 2 (dua) eksemplar buku dalam jangka waktu tersebut.',
            'keywords': 'batas, waktu, durasi, peminjaman, hari, minggu'
        },
        {
            'category': 'layanan',
            'question': 'Berapa banyak buku yang bisa dipinjam?',
            'answer': 'Setiap anggota perpustakaan berhak meminjam koleksi maksimal 2 (dua) eksemplar dalam jangka 1 minggu.',
            'keywords': 'jumlah pinjam, maksimal, berapa buku, eksemplar'
        },
        {
            'category': 'layanan',
            'question': 'Bagaimana cara memperpanjang peminjaman buku?',
            'answer': 'Perpanjangan pinjaman buku perpustakaan dapat dilakukan maksimal 1x dalam jangka 1 minggu. Anda bisa datang langsung ke perpustakaan dengan membawa buku dan Kartu Tanda Anggota (KTA).',
            'keywords': 'perpanjang, perpanjangan, extend'
        },
        {
            'category': 'layanan',
            'question': 'Apakah ada denda keterlambatan pengembalian buku?',
            'answer': 'Ya, setiap anggota perpustakaan wajib mengembalikan koleksi perpustakaan sesuai waktu yang telah ditetapkan. Jika terlambat atau buku hilang, anggota bertanggungjawab dengan mengganti buku atau membayar denda setara.',
            'keywords': 'denda, terlambat, keterlambatan, telat, hilang, ganti'
        },
        {
            'category': 'layanan',
            'question': 'Apa yang harus dilakukan jika buku perpustakaan hilang?',
            'answer': 'Setiap anggota perpustakaan bertanggungjawab atas koleksi perpustakaan yang hilang dengan mengganti buku atau membayar denda setara dengan nilai buku.',
            'keywords': 'hilang, kehilangan, buku hilang, ganti rugi'
        },
        {
            'category': 'layanan',
            'question': 'Apa saja hak anggota perpustakaan?',
            'answer': 'Setiap anggota perpustakaan berhak: 1) Menggunakan fasilitas perpustakaan, 2) Meminjam koleksi maksimal 2 (dua) eksemplar dalam jangka 1 minggu, 3) Memperpanjang pinjaman buku perpustakaan maksimal 1x dalam jangka 1 minggu.',
            'keywords': 'hak anggota, berhak, fasilitas, hak member'
        },
        {
            'category': 'layanan',
            'question': 'Apa saja kewajiban anggota perpustakaan?',
            'answer': 'Setiap anggota perpustakaan wajib: 1) Menjaga fasilitas perpustakaan dan mempergunakannya sebaik-baiknya, 2) Mengembalikan koleksi perpustakaan sesuai waktu yang telah ditetapkan, 3) Bertanggungjawab atas koleksi perpustakaan yang hilang dengan mengganti atau membayar denda setara.',
            'keywords': 'kewajiban, wajib, tanggung jawab, aturan'
        },
        
        # ==================== KEANGGOTAAN ====================
        {
            'category': 'keanggotaan',
            'question': 'Bagaimana cara mendaftar menjadi anggota perpustakaan?',
            'answer': 'Untuk mendaftar menjadi anggota dan membuat Kartu Tanda Anggota (KTA): 1) Mengisi formulir KTA pada link https://bit.ly/2T0EJcO, 2) Membawa formulir yang sudah diisi dan dilengkapi tanda tangan (untuk pelajar: stempel kepala sekolah/tata usaha), 3) Melampirkan fotokopi KTP/SIM/Kartu Pelajar/Kartu Keluarga (pilih salah satu), 4) Berfoto di ruang foto untuk KTA dan penyerahan KTA.',
            'keywords': 'daftar, mendaftar, registrasi, anggota, member, kta, kartu'
        },
        {
            'category': 'keanggotaan',
            'question': 'Dimana link untuk mendaftar anggota perpustakaan online?',
            'answer': 'Anda dapat mengisi formulir pendaftaran anggota perpustakaan (KTA) secara online melalui link: https://bit.ly/2T0EJcO',
            'keywords': 'link, online, formulir, daftar online, website'
        },
        {
            'category': 'keanggotaan',
            'question': 'Apa saja syarat menjadi anggota perpustakaan?',
            'answer': 'Syarat menjadi anggota: 1) Mengisi formulir KTA pada link https://bit.ly/2T0EJcO, 2) Membawa formulir yang sudah diisi dengan tanda tangan (pelajar: ditambah stempel kepala sekolah/tata usaha), 3) Melampirkan fotokopi KTP/SIM/Kartu Pelajar/Kartu Keluarga (pilih salah satu), 4) Berfoto di ruang foto perpustakaan untuk KTA.',
            'keywords': 'syarat, ketentuan, persyaratan, anggota, dokumen'
        },
        {
            'category': 'keanggotaan',
            'question': 'Apa saja dokumen yang diperlukan untuk mendaftar anggota?',
            'answer': 'Dokumen yang diperlukan untuk mendaftar anggota perpustakaan: 1) Formulir KTA yang sudah diisi (dari link https://bit.ly/2T0EJcO), 2) Fotokopi KTP/SIM/Kartu Pelajar/Kartu Keluarga (pilih salah satu), 3) Untuk pelajar: formulir harus dilengkapi tanda tangan dan stempel kepala sekolah/tata usaha.',
            'keywords': 'dokumen, berkas, persyaratan, ktp, sim, kartu pelajar'
        },
        {
            'category': 'keanggotaan',
            'question': 'Bagaimana syarat pendaftaran untuk pelajar?',
            'answer': 'Untuk pelajar yang ingin mendaftar anggota perpustakaan: 1) Mengisi formulir KTA dari link https://bit.ly/2T0EJcO, 2) Formulir harus dilengkapi dengan tanda tangan dan stempel kepala sekolah atau tata usaha, 3) Melampirkan fotokopi Kartu Pelajar atau Kartu Keluarga, 4) Berfoto di ruang foto perpustakaan.',
            'keywords': 'pelajar, siswa, sekolah, stempel, mahasiswa'
        },
        {
            'category': 'keanggotaan',
            'question': 'Apa itu Kartu Tanda Anggota (KTA)?',
            'answer': 'Kartu Tanda Anggota (KTA) adalah kartu identitas keanggotaan perpustakaan yang wajib digunakan untuk kegiatan membaca, meminjam, mengembalikan, dan memperpanjang buku di perpustakaan.',
            'keywords': 'kta, kartu anggota, kartu member, kartu perpustakaan'
        },
        {
            'category': 'keanggotaan',
            'question': 'Apakah pendaftaran anggota perpustakaan gratis?',
            'answer': 'Ya, pendaftaran anggota perpustakaan Dispusipda Pekanbaru GRATIS untuk seluruh masyarakat. Tidak ada biaya pembuatan Kartu Tanda Anggota (KTA).',
            'keywords': 'gratis, biaya, bayar, free, tarif'
        },
        
        # ==================== JAM OPERASIONAL ====================
        {
            'category': 'jam_operasional',
            'question': 'Jam berapa perpustakaan buka dan tutup?',
            'answer': 'Jadwal layanan Perpustakaan Tenas Effendy Dispusipda Pekanbaru: Senin-Kamis: 08.00-16.00 WIB, Jumat: 08.00-16.30 WIB (istirahat 11.30-13.30 WIB), Sabtu-Ahad: 08.00-14.00 WIB.',
            'keywords': 'jam, buka, tutup, operasional, waktu, jadwal'
        },
        {
            'category': 'jam_operasional',
            'question': 'Jam buka perpustakaan hari Senin sampai Kamis?',
            'answer': 'Perpustakaan Tenas Effendy buka hari Senin sampai Kamis pukul 08.00 - 16.00 WIB.',
            'keywords': 'senin, selasa, rabu, kamis, weekday'
        },
        {
            'category': 'jam_operasional',
            'question': 'Jam buka perpustakaan hari Jumat?',
            'answer': 'Perpustakaan Tenas Effendy buka hari Jumat pukul 08.00 - 16.30 WIB, dengan jam istirahat pukul 11.30 - 13.30 WIB.',
            'keywords': 'jumat, istirahat, sholat jumat'
        },
        {
            'category': 'jam_operasional',
            'question': 'Apakah perpustakaan buka di hari Sabtu dan Minggu?',
            'answer': 'Ya, perpustakaan buka di akhir pekan! Perpustakaan Tenas Effendy buka hari Sabtu dan Ahad (Minggu) pukul 08.00 - 14.00 WIB.',
            'keywords': 'sabtu, minggu, ahad, weekend, akhir pekan, libur'
        },
        {
            'category': 'jam_operasional',
            'question': 'Apa nama perpustakaan utama Dispusipda Pekanbaru?',
            'answer': 'Perpustakaan utama Dispusipda Pekanbaru bernama Perpustakaan Tenas Effendy.',
            'keywords': 'nama perpustakaan, tenas effendy, perpustakaan utama'
        },
        
        # ==================== KONTAK & SOSIAL MEDIA ====================
        {
            'category': 'kontak',
            'question': 'Dimana alamat Dispusipda Pekanbaru?',
            'answer': 'Alamat Dispusipda Pekanbaru (Perpustakaan Tenas Effendy) adalah: Jl. Dr. Sutomo No. 1, Kelurahan Suka Mulia, Kecamatan Sail, Kota Pekanbaru, Riau 28125. Lokasi ini berada di pusat kota Pekanbaru dan mudah dijangkau.',
            'keywords': 'alamat, lokasi, dimana, jalan, sutomo, gedung, tempat'
        },
        {
            'category': 'kontak',
            'question': 'Bagaimana cara ke Dispusipda Pekanbaru?',
            'answer': 'Dispusipda Pekanbaru (Perpustakaan Tenas Effendy) berlokasi di Jl. Dr. Sutomo No. 1, Kecamatan Sail, Pekanbaru. Perpustakaan ini berada di pusat kota dan dapat dijangkau dengan kendaraan umum maupun pribadi. Untuk navigasi, cari "Perpustakaan Tenas Effendy Pekanbaru" di Google Maps.',
            'keywords': 'cara ke, rute, navigasi, menuju, google maps'
        },
        {
            'category': 'kontak',
            'question': 'Bagaimana cara menghubungi Dispusipda Pekanbaru?',
            'answer': 'Anda dapat menghubungi Dispusipda Pekanbaru melalui: Email: bpadkotapekanbaru@gmail.com, Website: dispusipda.pekanbaru.go.id, YouTube: Dispusip Pekanbaru, Instagram: @dispusippku, Twitter: @DispusipPKU, Facebook: dispusip.pekanbaru',
            'keywords': 'kontak, hubungi, telepon, email, wa, whatsapp, sosmed'
        },
        {
            'category': 'kontak',
            'question': 'Apa email Dispusipda Pekanbaru?',
            'answer': 'Email resmi Dispusipda Pekanbaru adalah: bpadkotapekanbaru@gmail.com',
            'keywords': 'email, surat elektronik, gmail'
        },
        {
            'category': 'kontak',
            'question': 'Apa website resmi Dispusipda Pekanbaru?',
            'answer': 'Website resmi Dispusipda Pekanbaru adalah: dispusipda.pekanbaru.go.id',
            'keywords': 'website, web, situs, alamat web'
        },
        {
            'category': 'kontak',
            'question': 'Apa akun Instagram Dispusipda Pekanbaru?',
            'answer': 'Akun Instagram resmi Dispusipda Pekanbaru adalah: @dispusippku',
            'keywords': 'instagram, ig, sosmed, media sosial'
        },
        {
            'category': 'kontak',
            'question': 'Apa akun media sosial Dispusipda Pekanbaru?',
            'answer': 'Media sosial resmi Dispusipda Pekanbaru: YouTube: Dispusip Pekanbaru, Instagram: @dispusippku, Twitter: @DispusipPKU, Facebook: dispusip.pekanbaru',
            'keywords': 'sosmed, media sosial, youtube, twitter, facebook'
        },
        
        # ==================== KOLEKSI ====================
        {
            'category': 'koleksi',
            'question': 'Berapa jumlah koleksi perpustakaan Dispusipda?',
            'answer': 'Dispusipda Pekanbaru memiliki koleksi yang lengkap: Layanan Umum memiliki 18.114 judul koleksi, Layanan Anak memiliki 8.828 judul koleksi, dan Layanan i-Pekanbaru (digital) memiliki 8.527 eksemplar e-book.',
            'keywords': 'jumlah koleksi, berapa buku, total koleksi'
        },
        {
            'category': 'koleksi',
            'question': 'Apa saja jenis koleksi yang tersedia di perpustakaan?',
            'answer': 'Dispusipda Pekanbaru memiliki berbagai koleksi: Koleksi Umum (18.114 judul) untuk remaja dan dewasa, Koleksi Anak (8.828 judul) untuk anak usia 12-13 tahun, Koleksi Referensi untuk penelusuran informasi rujukan, dan Koleksi Digital/E-book (8.527 eksemplar) melalui aplikasi i-Pekanbaru.',
            'keywords': 'koleksi, buku, jenis, macam, tersedia'
        },
        {
            'category': 'koleksi',
            'question': 'Bagaimana cara mencari buku di katalog perpustakaan?',
            'answer': 'Anda dapat mencari buku menggunakan Layanan Penelusuran Literatur melalui OPAC (Online Public Access Catalogue) di website: https://pustaka.pekanbaru.go.id/Tenas.Efendy/opac/. OPAC membantu menemukan kembali informasi kepustakaan mengenai suatu bidang tertentu yang ada di perpustakaan.',
            'keywords': 'cari, katalog, opac, search, pencarian'
        },
        {
            'category': 'koleksi',
            'question': 'Dimana saya bisa melihat daftar buku yang tersedia di perpustakaan?',
            'answer': 'Anda dapat melihat daftar buku dan koleksi perpustakaan melalui OPAC (Online Public Access Catalogue) di website: https://pustaka.pekanbaru.go.id/Tenas.Efendy/opac/. Website ini menyediakan katalog lengkap koleksi Dispusipda Pekanbaru.',
            'keywords': 'daftar buku, lihat buku, katalog, koleksi tersedia, opac'
        },
        {
            'category': 'koleksi',
            'question': 'Bagaimana cara menyarankan buku untuk perpustakaan?',
            'answer': 'Jika Anda ingin menyarankan buku untuk ditambahkan ke koleksi perpustakaan, silakan isi formulir saran buku melalui link: https://docs.google.com/forms/d/e/1FAIpQLSd_Kw9UpL2zIHjlzBDHBrDORrlE-ETg09JG0jrYTbUvlSXN-A/viewform. Masukan Anda sangat berharga untuk pengembangan koleksi perpustakaan.',
            'keywords': 'saran buku, rekomendasi, usul buku, tambah koleksi, form saran'
        },
        
        # ==================== DIGITAL ====================
        {
            'category': 'digital',
            'question': 'Apakah ada layanan perpustakaan digital atau e-book?',
            'answer': 'Ya, Dispusipda Pekanbaru menyediakan layanan perpustakaan digital melalui aplikasi i-Pekanbaru. Aplikasi ini menyediakan 8.527 eksemplar e-book yang dapat diakses secara gratis. Download aplikasi di: https://ipekanbaru.moco.co.id/ (tersedia untuk Android dan Desktop).',
            'keywords': 'digital, online, e-book, ebook, internet, e-library'
        },
        {
            'category': 'digital',
            'question': 'Bagaimana cara mengakses e-book di Dispusipda?',
            'answer': 'Untuk mengakses e-book, download aplikasi i-Pekanbaru melalui link: https://ipekanbaru.moco.co.id/. Aplikasi ini tersedia untuk Android dan Desktop secara gratis. Aplikasi menyediakan 8.527 eksemplar e-book yang dapat dibaca kapan saja dan dimana saja.',
            'keywords': 'akses ebook, download, unduh, baca online'
        },
        {
            'category': 'digital',
            'question': 'Dimana saya bisa download aplikasi iPekanbaru?',
            'answer': 'Anda dapat mendownload aplikasi iPekanbaru (perpustakaan digital) melalui link: https://ipekanbaru.moco.co.id/. Aplikasi tersedia untuk Android dan Desktop. Dengan aplikasi ini, Anda bisa membaca 8.527 e-book secara gratis.',
            'keywords': 'download ipekanbaru, unduh aplikasi, playstore, app store'
        },
        {
            'category': 'digital',
            'question': 'Apakah ada layanan buku bersuara atau audiobook?',
            'answer': 'Ya, Dispusipda Pekanbaru menyediakan layanan buku anak bersuara (audiobook) melalui platform Membara. Anda dapat mengakses buku anak bersuara di website: https://membara.perpustakaanterbaik.com/. Layanan ini memudahkan anak-anak mendengarkan cerita dan buku tanpa harus membaca.',
            'keywords': 'audiobook, buku bersuara, audio, dengar buku, membara, buku anak'
        },
        {
            'category': 'digital',
            'question': 'Apa itu Membara?',
            'answer': 'Membara adalah platform buku anak bersuara (audiobook untuk anak-anak) yang disediakan oleh Dispusipda Pekanbaru. Anak-anak dapat mendengarkan berbagai koleksi buku cerita dan edukasi dalam format audio melalui website: https://membara.perpustakaanterbaik.com/. Layanan ini sangat cocok untuk menumbuhkan minat baca anak sejak dini.',
            'keywords': 'membara, buku bersuara, audiobook, platform audio, buku anak'
        },
        {
            'category': 'digital',
            'question': 'Bagaimana cara mendengarkan buku bersuara?',
            'answer': 'Untuk mendengarkan buku anak bersuara (audiobook), kunjungi website Membara di: https://membara.perpustakaanterbaik.com/. Di platform ini anak-anak bisa menemukan berbagai koleksi buku cerita dalam format audio yang bisa didengarkan kapan saja.',
            'keywords': 'cara audiobook, dengar buku, mendengarkan, audio, anak'
        },
        {
            'category': 'digital',
            'question': 'Apa itu OPAC?',
            'answer': 'OPAC adalah singkatan dari Online Public Access Catalogue. OPAC adalah sistem katalog online yang digunakan dalam Layanan Penelusuran Literatur untuk mencari atau menemukan kembali informasi kepustakaan. Akses OPAC Dispusipda di: https://pustaka.pekanbaru.go.id/Tenas.Efendy/opac/',
            'keywords': 'opac, katalog online, pencarian buku, catalogue'
        },
        
        # ==================== PROGRAM ====================
        {
            'category': 'program',
            'question': 'Apa saja program dan kegiatan di perpustakaan?',
            'answer': 'Dispusipda Pekanbaru menyelenggarakan berbagai program seperti: kegiatan mendongeng di Layanan Anak, Layanan Perpustakaan Keliling menggunakan Mobil Perpustakaan Keliling (MPK) yang bergerak ke berbagai tempat, serta layanan literasi digital melalui aplikasi i-Pekanbaru.',
            'keywords': 'program, kegiatan, acara, event, aktivitas'
        },
        {
            'category': 'program',
            'question': 'Apakah ada kegiatan mendongeng untuk anak?',
            'answer': 'Ya, kegiatan mendongeng tersedia di Layanan Anak perpustakaan. Layanan Anak ditujukan untuk anak berumur 12-13 tahun dan memiliki 8.828 judul koleksi perpustakaan khusus anak.',
            'keywords': 'mendongeng, dongeng, anak, storytelling'
        },
        
        # ==================== PERCOBAAN SAINS ====================
        {
            'category': 'program',
            'question': 'Apa saja percobaan sains yang tersedia di perpustakaan?',
            'answer': 'Dispusipda Pekanbaru menyediakan manual book percobaan sains sederhana untuk anak-anak, antara lain: 1) Percobaan Lava Lamp - membuat lampu lava dari bahan sederhana, 2) Percobaan Rainbow Lava - variasi lava lamp dengan efek pelangi. Percobaan ini mengajarkan konsep sains seperti densitas (massa jenis), polaritas molekul, dan reaksi kimia sederhana.',
            'keywords': 'percobaan sains, eksperimen, lava lamp, rainbow lava, sains anak'
        },
        {
            'category': 'program',
            'question': 'Apa itu percobaan Lava Lamp?',
            'answer': 'Lava Lamp adalah percobaan sains sederhana yang mengajarkan konsep densitas dan reaksi kimia. Bahan yang dibutuhkan: botol/gelas bening, air (1/4 bagian), minyak goreng (3/4 bagian), pewarna makanan, dan tablet effervescent. Cara membuat: 1) Tuang air ke botol (1/4), 2) Tambah minyak (3/4), 3) Tunggu terpisah, 4) Teteskan pewarna, 5) Masukkan tablet effervescent dan amati gelembung berwarna naik turun seperti lava.',
            'keywords': 'lava lamp, lampu lava, percobaan, eksperimen, minyak air'
        },
        {
            'category': 'program',
            'question': 'Bagaimana cara membuat Lava Lamp?',
            'answer': 'Langkah membuat Lava Lamp: 1) Siapkan botol/gelas bening, 2) Tuang air hingga 1/4 bagian, 3) Tambahkan minyak goreng hingga 3/4 bagian, 4) Tunggu hingga air dan minyak terpisah sempurna, 5) Teteskan pewarna makanan (akan turun ke air), 6) Patahkan tablet effervescent dan masukkan, 7) Amati gelembung berwarna yang naik turun seperti lava lamp!',
            'keywords': 'cara membuat lava lamp, langkah lava lamp, tutorial'
        },
        {
            'category': 'program',
            'question': 'Apa bahan-bahan untuk membuat Lava Lamp?',
            'answer': 'Bahan untuk percobaan Lava Lamp: 1) Botol atau gelas bening/transparan, 2) Air secukupnya (1/4 bagian), 3) Minyak goreng (3/4 bagian), 4) Pewarna makanan (warna sesuai selera), 5) Tablet effervescent (seperti vitamin C effervescent). Semua bahan mudah didapat di rumah atau minimarket.',
            'keywords': 'bahan lava lamp, alat lava lamp, perlengkapan'
        },
        {
            'category': 'program',
            'question': 'Mengapa minyak dan air tidak bisa bercampur di Lava Lamp?',
            'answer': 'Minyak dan air tidak bisa bercampur karena perbedaan polaritas molekul. Air adalah molekul polar sedangkan minyak adalah molekul non-polar. Selain itu, minyak memiliki densitas (massa jenis) lebih rendah dari air sehingga minyak selalu mengapung di atas air. Inilah prinsip sains di balik percobaan Lava Lamp.',
            'keywords': 'polaritas, densitas, massa jenis, sains lava lamp, mengapa'
        },
        {
            'category': 'program',
            'question': 'Bagaimana prinsip kerja Lava Lamp?',
            'answer': 'Prinsip kerja Lava Lamp: 1) Air dan minyak terpisah karena perbedaan densitas dan polaritas, 2) Pewarna larut di air (bukan minyak) karena sama-sama polar, 3) Tablet effervescent bereaksi dengan air menghasilkan gas CO2, 4) Gelembung gas membawa air berwarna naik ke permukaan, 5) Setelah gas lepas, air turun kembali. Siklus ini menciptakan efek "lava" yang bergerak naik-turun.',
            'keywords': 'prinsip lava lamp, cara kerja, mekanisme, sains'
        },
        {
            'category': 'program',
            'question': 'Apa itu percobaan Rainbow Lava?',
            'answer': 'Rainbow Lava adalah variasi percobaan Lava Lamp dengan efek pelangi/multi warna. Prinsipnya sama dengan Lava Lamp biasa, namun menggunakan beberapa warna pewarna makanan berbeda untuk menciptakan efek pelangi yang lebih menarik. Percobaan ini cocok untuk anak-anak karena lebih colorful dan menyenangkan.',
            'keywords': 'rainbow lava, pelangi, lava warna-warni, percobaan anak'
        },
        {
            'category': 'program',
            'question': 'Bagaimana cara membuat Rainbow Lava?',
            'answer': 'Cara membuat Rainbow Lava: 1) Siapkan botol/gelas bening, 2) Tuang air (1/4 bagian), 3) Tambah minyak goreng (3/4 bagian), 4) Tunggu terpisah, 5) Teteskan beberapa warna pewarna makanan berbeda (merah, kuning, biru, hijau), 6) Masukkan tablet effervescent, 7) Amati gelembung warna-warni seperti pelangi yang bergerak naik turun!',
            'keywords': 'cara rainbow lava, tutorial rainbow, langkah'
        },
        {
            'category': 'program',
            'question': 'Untuk usia berapa percobaan Lava Lamp cocok?',
            'answer': 'Percobaan Lava Lamp dan Rainbow Lava cocok untuk anak usia SD hingga SMP (sekitar 7-15 tahun). Percobaan ini aman karena menggunakan bahan-bahan rumah tangga yang tidak berbahaya. Namun, untuk anak usia lebih kecil sebaiknya didampingi orang dewasa, terutama saat menggunakan tablet effervescent.',
            'keywords': 'usia, umur, anak sd, anak smp, cocok untuk'
        },
        {
            'category': 'program',
            'question': 'Apa manfaat percobaan sains Lava Lamp untuk anak?',
            'answer': 'Manfaat percobaan Lava Lamp untuk anak: 1) Mengajarkan konsep densitas/massa jenis, 2) Memahami polaritas molekul (polar vs non-polar), 3) Mengenal reaksi kimia sederhana (effervescent + air = CO2), 4) Melatih keterampilan observasi, 5) Menumbuhkan minat sains sejak dini, 6) Aktivitas edukatif yang menyenangkan.',
            'keywords': 'manfaat, kegunaan, belajar sains, edukasi'
        },
        {
            'category': 'program',
            'question': 'Dimana bisa mendapatkan manual book percobaan sains?',
            'answer': 'Manual book percobaan sains seperti Lava Lamp dan Rainbow Lava tersedia di Dispusipda Pekanbaru, khususnya di Layanan Anak. Anda juga dapat mengikuti kegiatan sains dan eksperimen yang diadakan oleh perpustakaan. Untuk informasi jadwal kegiatan, silakan hubungi Dispusipda atau cek media sosial @dispusippku.',
            'keywords': 'manual book, buku panduan, dapat dimana, lokasi'
        },
        
        # ==================== KEARSIPAN ====================
        {
            'category': 'kearsipan',
            'question': 'Apa saja layanan kearsipan di Dispusipda Pekanbaru?',
            'answer': 'Dispusipda Pekanbaru menyediakan Layanan Kearsipan yang mencakup: 1) Konsultasi pengelolaan arsip untuk instansi/lembaga, 2) Bimbingan teknis kearsipan, 3) Akses informasi arsip statis melalui SIKN-JIKN, 4) Penyimpanan dan pemeliharaan arsip daerah, 5) Alih media arsip (digitalisasi).',
            'keywords': 'layanan kearsipan, arsip, konsultasi, bimbingan teknis'
        },
        {
            'category': 'kearsipan',
            'question': 'Apa itu SIKN-JIKN?',
            'answer': 'SIKN (Sistem Informasi Kearsipan Nasional) adalah sistem informasi kearsipan nasional yang dibangun oleh ANRI untuk menyediakan akses informasi arsip statis secara elektronik. JIKN (Jaringan Informasi Kearsipan Nasional) adalah jaringan yang menghubungkan sistem kearsipan antar lembaga. Dispusipda Pekanbaru tergabung dalam SIKN-JIKN untuk mempermudah akses informasi arsip.',
            'keywords': 'sikn, jikn, sistem informasi kearsipan, arsip nasional, anri'
        },
        {
            'category': 'kearsipan',
            'question': 'Bagaimana cara mengakses arsip di Dispusipda?',
            'answer': 'Untuk mengakses arsip statis di Dispusipda Pekanbaru, Anda dapat: 1) Datang langsung ke ruang layanan kearsipan dengan membawa identitas diri, 2) Mengakses arsip digital melalui SIKN-JIKN, 3) Mengajukan permohonan tertulis untuk arsip tertentu. Layanan ini terbuka untuk peneliti, mahasiswa, dan masyarakat umum.',
            'keywords': 'akses arsip, cara, lihat arsip, penelitian'
        },
        {
            'category': 'kearsipan',
            'question': 'Apakah Dispusipda melayani konsultasi kearsipan?',
            'answer': 'Ya, Dispusipda Pekanbaru menyediakan layanan konsultasi kearsipan untuk instansi pemerintah, lembaga swasta, dan masyarakat. Konsultasi meliputi: pengelolaan arsip, penyusutan arsip, jadwal retensi arsip (JRA), dan alih media arsip. Silakan hubungi Dispusipda untuk membuat janji konsultasi.',
            'keywords': 'konsultasi, bimbingan, arsip, pengelolaan arsip'
        },
        {
            'category': 'kearsipan',
            'question': 'Apa itu arsip statis?',
            'answer': 'Arsip statis adalah arsip yang dihasilkan oleh pencipta arsip karena memiliki nilai guna kesejarahan, telah habis retensinya, dan berketerangan dipermanenkan. Arsip statis disimpan secara permanen di lembaga kearsipan seperti Dispusipda dan dapat diakses oleh publik untuk kepentingan penelitian dan pendidikan.',
            'keywords': 'arsip statis, permanen, kesejarahan, nilai guna'
        },
        {
            'category': 'kearsipan',
            'question': 'Apa itu arsip dinamis?',
            'answer': 'Arsip dinamis adalah arsip yang digunakan secara langsung dalam kegiatan pencipta arsip dan disimpan selama jangka waktu tertentu. Arsip dinamis terbagi menjadi: 1) Arsip aktif - masih sering digunakan, 2) Arsip inaktif - jarang digunakan tapi masih diperlukan. Dispusipda dapat memberikan bimbingan pengelolaan arsip dinamis.',
            'keywords': 'arsip dinamis, aktif, inaktif, pengelolaan'
        },
        {
            'category': 'kearsipan',
            'question': 'Bagaimana cara mendapatkan bimbingan teknis kearsipan?',
            'answer': 'Untuk mendapatkan bimbingan teknis kearsipan dari Dispusipda Pekanbaru: 1) Ajukan permohonan tertulis ke Dispusipda, 2) Jelaskan kebutuhan bimbingan (pengelolaan arsip, penyusutan, alih media, dll), 3) Koordinasi jadwal dengan tim kearsipan. Layanan ini tersedia untuk instansi pemerintah dan swasta.',
            'keywords': 'bimbingan teknis, bimtek, pelatihan, kearsipan'
        },
        
        # ==================== UMUM ====================
        {
            'category': 'umum',
            'question': 'Apa itu Dispusipda Pekanbaru?',
            'answer': 'Dispusipda (Dinas Perpustakaan dan Kearsipan) Kota Pekanbaru adalah instansi pemerintah yang bertugas mengelola perpustakaan umum dan kearsipan daerah. Perpustakaan utamanya bernama Perpustakaan Tenas Effendy yang menyediakan 7 jenis layanan untuk masyarakat.',
            'keywords': 'dispusipda, apa, perpustakaan, dinas'
        },
        {
            'category': 'umum',
            'question': 'Siapa saja yang boleh mengunjungi perpustakaan?',
            'answer': 'Perpustakaan Dispusipda Pekanbaru terbuka untuk umum. Siapa saja boleh berkunjung untuk membaca di tempat. Untuk meminjam buku, Anda perlu membuat Kartu Tanda Anggota (KTA) terlebih dahulu melalui link https://bit.ly/2T0EJcO.',
            'keywords': 'siapa, boleh, umum, pengunjung, akses'
        }
    ]
    
    db = get_db_manager()
    
    # Clear existing
    print("Menghapus FAQ lama...")
    db.clear_all_faqs()
    
    # Import
    print("Mengimport FAQ default...")
    inserted_ids = db.insert_faqs_bulk(default_faqs)
    
    db.log_event('info', f'Imported {len(inserted_ids)} default FAQs', {})
    
    print(f"\nSelesai! Total FAQ diimport: {len(inserted_ids)}")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import FAQ ke database')
    parser.add_argument('--file', default='data/generated_faqs.json', help='Path ke file JSON FAQ')
    parser.add_argument('--clear', action='store_true', help='Hapus FAQ yang ada sebelum import')
    parser.add_argument('--default', action='store_true', help='Import FAQ default (tanpa file JSON)')
    args = parser.parse_args()
    
    if args.default:
        import_default_faqs()
    else:
        import_faqs_from_json(args.file, args.clear)
