<?php
/**
 * Contoh implementasi Chatbot Widget di website PHP
 * Salin file ini ke root website PHP Anda
 */
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Dispusipda Pekanbaru</title>
    <style>
        /* Style contoh untuk halaman */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #1e88e5, #1565c0);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1, h2 { margin-top: 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Dinas Perpustakaan dan Kearsipan</h1>
        <p>Kota Pekanbaru</p>
    </div>

    <div class="content">
        <div class="card">
            <h2>Selamat Datang</h2>
            <p>Selamat datang di website Dispusipda Kota Pekanbaru. Kami menyediakan berbagai layanan perpustakaan untuk masyarakat.</p>
        </div>

        <div class="card">
            <h2>Layanan Kami</h2>
            <ul>
                <li>Peminjaman dan pengembalian buku</li>
                <li>Layanan referensi</li>
                <li>Ruang baca</li>
                <li>Perpustakaan keliling</li>
                <li>E-Resources digital</li>
            </ul>
        </div>

        <div class="card">
            <h2>Butuh Bantuan?</h2>
            <p>Klik tombol chat di pojok kanan bawah untuk bertanya kepada asisten virtual kami!</p>
        </div>
    </div>

    <!-- ========================================== -->
    <!-- CHATBOT WIDGET - Tambahkan kode ini -->
    <!-- ========================================== -->
    
    <!-- Opsi 1: Load dari file lokal -->
    <script src="chatbot-widget.js"></script>
    
    <!-- Opsi 2: Load dari CDN/URL external (jika sudah di-host) -->
    <!-- <script src="https://your-domain.com/chatbot/chatbot-widget.js"></script> -->
    
    <script>
        // Inisialisasi chatbot widget
        document.addEventListener('DOMContentLoaded', function() {
            ChatbotWidget.init({
                // URL API backend (sesuaikan dengan server Anda)
                apiUrl: 'http://localhost:5000',
                
                // Posisi widget: 'right' atau 'left'
                position: 'right',
                
                // Warna tema (biru default)
                primaryColor: '#1e88e5',
                
                // Pesan greeting
                greetingMessage: 'Halo! 👋 Ada yang bisa saya bantu tentang layanan perpustakaan?',
                
                // Durasi auto-close greeting (ms)
                greetingAutoCloseDelay: 8000,
                
                // Judul header chat
                headerTitle: 'Asisten Dispusipda',
                headerSubtitle: 'Online',
                
                // Placeholder input
                placeholder: 'Ketik pertanyaan Anda...',
                
                // Saran pertanyaan
                suggestions: [
                    'Cara mendaftar anggota?',
                    'Jam buka perpustakaan?',
                    'Layanan yang tersedia?'
                ]
            });
        });
    </script>
    <!-- ========================================== -->
    <!-- END CHATBOT WIDGET -->
    <!-- ========================================== -->

</body>
</html>
