# CV Analiz & ATS Skoru Servisi - Backend

**AI destekli CV analiz, ATS uyumluluk skorlama ve iş eşleştirme servisi.**

## ✨ Özellikler

- 📄 **PDF CV Analizi** — PyMuPDF + pdfplumber ile robust PDF parsing
- 🤖 **AI Powered Analysis** — OpenAI GPT-4o-mini ile detaylı CV analizi
- 📊 **ATS Scoring** — Format, anahtar kelime, deneyim ve uyumluluk skorları
- 🎯 **İş Eşleştirmesi** — CV ile iş ilanı arasında uyumluluk analizi
- 💳 **Ödeme Entegrasyonu** — Stripe + İyzico webhook desteği (signature verification)
- 🔐 **Güvenli Auth** — JWT token + Argon2 password hashing
- 📈 **Ücretsiz Tier** — 3 analiz/ay, Premium abonelik seçeneği

## 🚀 Hızlı Başlangıç

### 1. Ortamı Ayarla

```bash
# Python 3.11+ gerekli
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# NLP modellerini indir (opsiyonel, fallback yok)
python scripts/setup_nlp.py
```

### 2. Ortam Değişkenlerini Yapılandır

```bash
cp .env.example .env
# .env dosyasını düzenle:
# - SECRET_KEY: Güçlü bir secret key (production'da değiştir)
# - OPENAI_API_KEY: OpenAI API key (fallback analiz açık, API key isteğe bağlı)
# - IYZICO_API_KEY, STRIPE_SECRET_KEY: İsteğe bağlı
```

### 3. Veritabanını Oluştur

```bash
python -m alembic upgrade head
```

### 4. Sunucuyu Başlat

```bash
uvicorn app.main:app --reload --port 8000
```

**API Docs:** http://localhost:8000/docs

## 📚 API Endpoints

### Auth
- `POST /api/v1/auth/register` — Kullanıcı kayıt
- `POST /api/v1/auth/login` — Giriş (JWT token)

### CV Analysis
- `POST /api/v1/cv/upload` — PDF upload + analiz
- `GET /api/v1/cv/analyses` — Analiz geçmişi
- `GET /api/v1/cv/analyses/{id}` — Analiz detayları

### Job Matching
- `POST /api/v1/job/match` — CV ile iş eşleştirmesi

### Payment
- `POST /api/v1/payment/create` — Ödeme başlat
- `POST /api/v1/payment/callback/{provider}` — Webhook callback

## 🔧 Konfigürasyon

### Environment Variables

```ini
# Database
DATABASE_URL=sqlite+aiosqlite:///./cv_analiz.db

# Auth
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI
OPENAI_API_KEY=sk-...  # Opsiyonel, fallback analiz kullan

# Payment Providers
IYZICO_API_KEY=
IYZICO_SECRET_KEY=
IYZICO_BASE_URL=https://sandbox-api.iyzipay.com

STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# App Settings
MAX_FREE_ANALYSES=3
UPLOAD_DIR=uploads
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
API_BASE_URL=http://localhost:8000
```

## 🧪 Testleri Çalıştır

```bash
# Tüm testleri çalıştır
pytest -q

# Verbose output
pytest -v

# Spesifik test dosyası
pytest tests/test_cv.py -v

# Coverage
pytest --cov=app --cov-report=html
```

## 📊 Test Sonuçları

✅ **19/19 Tests Passing**
- Auth (register, login, token validation)
- CV Upload & Analysis
- ATS Scoring
- Job Matching
- Payment (iyzico, Stripe)

## 🏗️ Proje Yapısı

```
.
├── app/
│   ├── api/v1/
│   │   ├── endpoints/      # API endpoints
│   │   └── router.py       # Route registry
│   ├── core/
│   │   ├── exceptions.py   # Custom exceptions
│   │   ├── middleware.py   # App middleware
│   │   └── security.py     # JWT + password hashing
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic request/response
│   ├── services/           # Business logic
│   │   ├── auth_service.py
│   │   ├── cv_parser.py
│   │   ├── nlp_analyzer.py
│   │   ├── ats_scorer.py
│   │   ├── job_matcher.py
│   │   └── payment_service.py
│   ├── config.py           # Settings
│   ├── database.py         # Database setup
│   ├── logging_config.py   # Logging
│   └── main.py             # FastAPI app
├── alembic/                # Database migrations
├── scripts/
│   └── setup_nlp.py        # NLP model setup
├── tests/                  # Test suite
├── requirements.txt        # Dependencies
└── README.md
```

## 🔐 Güvenlik

- **Password Hashing:** Argon2 (bcrypt yerine, daha güvenli)
- **Authentication:** JWT Bearer tokens
- **Webhook Verification:** Stripe + İyzico signature doğrulama
- **CORS:** Configurable origins
- **Rate Limiting:** (Üretim'de eklenebilir)
- **Error Handling:** Detailed logging, generic error responses

## 📝 Logging

Tüm olaylar `logs/app.log` dosyasına yazılır:
- Request/Response logging
- Database errors
- API call traces
- Payment webhook events

```bash
# Logs klasörü otomatik oluşturulur
ls -la logs/
```

## 🚢 Deployment

### Docker (Recommended)

```dockerfile
# Dockerfile (örnek)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment (Production)

```bash
# Production settings
SECRET_KEY=generate-with-secrets.token_hex(32)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cv_db
OPENAI_API_KEY=sk-...
STRIP_WEBHOOK_SECRET=whsec_...
IYZICO_API_KEY=your-api-key
IYZICO_SECRET_KEY=your-secret-key
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/v1/payment/callback {
        # Webhook endpoint, rate limiting yok
        proxy_pass http://localhost:8000;
    }
}
```

## 🐛 Troubleshooting

### "OPENAI_API_KEY not set"
→ `.env` dosyasına `OPENAI_API_KEY` ekle veya fallback analiz kullan (ücretsiz, daha basit)

### "Payment webhook signature invalid"
→ Webhook header'ında `x-iyzico-signature` veya `stripe-signature` doğru mu?

### Database locked error
→ SQLite kullanıyorsan concurrent requests için PostgreSQL düşün

## 📦 Bağımlılıklar

- **FastAPI 0.115.0** — Web framework
- **SQLAlchemy 2.0.35** — ORM
- **Pydantic 2.9.2** — Data validation
- **OpenAI 1.47.0** — AI analysis
- **Stripe & İyzico SDKs** — Payment processing
- **PyMuPDF + pdfplumber** — PDF parsing
- **Argon2 + JWT** — Authentication

## 📄 Lisans

MIT License

## 👤 İletişim

Questions? Issues? Pull requests welcome!
