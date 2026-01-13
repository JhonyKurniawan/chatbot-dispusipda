## Struktur Project

```
chatbot-dispusipda/
├── api/
│   └── app.py                 # Flask API server
├── config/
│   └── config.py              # Konfigurasi aplikasi
├── database/
│   ├── schema.sql             # Database schema MySQL
│   └── db_manager.py          # Database operations
├── scraper/
│   └── scraper.py             # Web scraper & FAQ generator
├── services/
│   ├── embedding_service.py   # Sentence Transformers
│   ├── llm_service.py         # Groq/Gemini API
│   └── chatbot_service.py     # Main chatbot logic
├── scripts/
│   ├── setup.py               # Setup awal
│   ├── import_faqs.py         # Import FAQ ke database
│   ├── generate_embeddings.py # Generate embeddings
│   └── auto_update.py         # Auto-update berkala
├── frontend/
│   ├── chatbot-widget.html    # Standalone widget demo
│   ├── chatbot-widget.js      # Widget JS (untuk embed)
│   └── example-implementation.php  # Contoh implementasi
├── data/                      # Data hasil scraping (auto-generated)
├── logs/                      # Log files (auto-generated)
├── .env.example               # Template environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # Dokumentasi ini
```

## Quick Start

### 1. Clone & Install Dependencies

```bash
# Clone repository (atau copy folder)
cd chatbot-dispusipda

# Buat virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment Variables

```bash
# Salin template
copy .env.example .env

# Edit .env dengan konfigurasi Anda
notepad .env
```

### 3. Setup Database MySQL

```sql
-- Jalankan di MySQL client/phpMyAdmin
SOURCE database/schema.sql;

-- Atau buat database manual dan import
CREATE DATABASE chatbot_dispusipda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Dapatkan API Key

Pilih salah satu (Groq lebih cepat, Gemini lebih mudah):

**Groq API (Recommended)**
1. Daftar di https://console.groq.com/
2. Buat API key di https://console.groq.com/keys
3. Copy API key ke `.env`: `GROQ_API_KEY=your_key`

**Google Gemini API**
1. Daftar di https://makersuite.google.com/
2. Buat API key di https://makersuite.google.com/app/apikey
3. Copy API key ke `.env`: `GEMINI_API_KEY=your_key`
4. Ubah provider: `LLM_PROVIDER=gemini`

### 5. Jalankan Setup

```bash
# Setup otomatis (import FAQ + generate embeddings)
python scripts/setup.py
```

### 6. Jalankan API Server

```bash
python api/app.py
```

Server berjalan di `http://localhost:5000`

### 7. Test API

**Linux/Mac (bash):**
```bash
# Health check
curl http://localhost:5000/api/health

# Test chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bagaimana cara mendaftar anggota?"}'
```

**Windows (PowerShell):**
```powershell
# Health check
Invoke-RestMethod http://localhost:5000/api/health

# Test chat (Cara 1 - Invoke-RestMethod)
$body = '{"message": "Bagaimana cara mendaftar anggota?"}'
Invoke-RestMethod -Uri "http://localhost:5000/api/chat" -Method POST -ContentType "application/json" -Body $body

# Test chat (Cara 2 - curl.exe native Windows)
curl.exe -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"Bagaimana cara mendaftar anggota?\"}"
```

**Atau buka browser:** `http://localhost:5000/api/health`

## Integrasi ke Website PHP

### Metode 1: Include File JS

```php
<!-- Tambahkan di footer website PHP Anda -->
<script src="/path/to/chatbot-widget.js"></script>
<script>
    ChatbotWidget.init({
        apiUrl: 'http://your-server:5000',
        primaryColor: '#1e88e5',
        position: 'right'
    });
</script>
```

### Metode 2: Embed Inline

Lihat contoh lengkap di `frontend/example-implementation.php`

### Konfigurasi Widget

```javascript
ChatbotWidget.init({
    // Required
    apiUrl: 'http://localhost:5000',
    
    // Optional
    position: 'right',              // 'right' atau 'left'
    primaryColor: '#1e88e5',        // Warna tema
    greetingMessage: 'Halo! Ada yang bisa dibantu?',
    greetingAutoCloseDelay: 8000,   // ms
    headerTitle: 'Asisten Dispusipda',
    headerSubtitle: 'Online',
    placeholder: 'Ketik pertanyaan...',
    suggestions: [
        'Cara mendaftar anggota?',
        'Jam buka perpustakaan?'
    ]
});
```

## Konfigurasi Lanjutan

### Environment Variables (.env)

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=chatbot_dispusipda

# LLM Provider
LLM_PROVIDER=groq              # atau 'gemini'
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# API Server
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False
CORS_ORIGINS=*                 # atau domain spesifik

# Auto Update
AUTO_UPDATE_ENABLED=False
AUTO_UPDATE_INTERVAL=24        # jam
```

### Menambah FAQ Kustom

1. Edit file `data/generated_faqs.json`
2. Jalankan import:
   ```bash
   python scripts/import_faqs.py --file data/generated_faqs.json --clear
   ```
3. Generate embeddings:
   ```bash
   python scripts/generate_embeddings.py
   ```

### Web Scraping Manual

```bash
# Scrape website dan generate FAQ
python scraper/scraper.py

# Hasil disimpan di:
# - data/raw_scraped_data.json
# - data/generated_faqs.json
```

## Auto Update (Optional)

### Cron Job (Linux)

```bash
# Edit crontab
crontab -e

# Tambahkan untuk update setiap hari jam 2 pagi
0 2 * * * cd /path/to/chatbot-dispusipda && /path/to/venv/bin/python scripts/auto_update.py --once
```

### Task Scheduler (Windows)

1. Buka Task Scheduler
2. Create Basic Task
3. Set trigger (daily)
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `scripts\auto_update.py --once`
   - Start in: `D:\Project\kp\chatbot-dispusipda`

### Background Service

```bash
# Jalankan sebagai daemon
python scripts/auto_update.py --scheduled
```

## Deployment Production

### Deploy dengan Gunicorn (Linux)

```bash
# Install gunicorn
pip install gunicorn

# Jalankan
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

### Deploy dengan Waitress (Windows)

```bash
# Install waitress
pip install waitress

# Jalankan
waitress-serve --host=0.0.0.0 --port=5000 api.app:app
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name chatbot.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/chatbot-dispusipda.service
[Unit]
Description=Chatbot Dispusipda API
After=network.target mysql.service

[Service]
User=www-data
WorkingDirectory=/var/www/chatbot-dispusipda
Environment="PATH=/var/www/chatbot-dispusipda/venv/bin"
ExecStart=/var/www/chatbot-dispusipda/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 api.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable dan start service
sudo systemctl enable chatbot-dispusipda
sudo systemctl start chatbot-dispusipda
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/health` | GET | Detailed health status |
| `/api/chat` | POST | Main chat endpoint |
| `/api/greeting` | GET | Get greeting message |
| `/api/suggestions` | GET | Get suggested questions |
| `/api/feedback` | POST | Submit feedback |
| `/api/categories` | GET | Get FAQ categories |
| `/api/faqs` | GET | Get all FAQs |
| `/api/stats` | GET | Get statistics |
| `/api/reload-cache` | POST | Reload embeddings cache |

### Chat Request Example

```json
POST /api/chat
{
    "message": "Bagaimana cara mendaftar anggota?",
    "session_id": "optional-session-id"
}
```

### Chat Response Example

```json
{
    "session_id": "uuid-string",
    "response": "Untuk mendaftar menjadi anggota perpustakaan...",
    "matched_faqs": [
        {
            "id": 1,
            "question": "Bagaimana cara mendaftar...",
            "similarity": 0.92,
            "category": "keanggotaan"
        }
    ],
    "response_time_ms": 234
}
```

## Security Notes

1. **API Key**: Jangan expose API key di frontend
2. **CORS**: Set domain spesifik di production
3. **Rate Limiting**: Tambahkan rate limiter untuk production
4. **HTTPS**: Gunakan SSL certificate di production
5. **Database**: Gunakan user dengan limited privileges

## 🐛 Troubleshooting

### Database Connection Error
```
Error: Can't connect to MySQL server
```
- Pastikan MySQL server berjalan
- Cek konfigurasi di `.env`
- Cek firewall/port

### Embedding Model Download Slow
```
Downloading model...
```
- Model akan di-download saat pertama kali (~500MB)
- Pastikan koneksi internet stabil

### LLM API Error
```
Error: Invalid API key
```
- Cek API key di `.env`
- Pastikan masih valid di console Groq/Gemini

### CORS Error
```
Access-Control-Allow-Origin
```
- Set `CORS_ORIGINS` di `.env`
- Atau gunakan proxy di Nginx

## 📝 License

MIT License - Bebas digunakan untuk keperluan apapun.
