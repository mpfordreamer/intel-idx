# Product Requirement Document (PRD)
## AI-Driven IDX Corporate Action & Market Intelligence System (IDX-Intel AI)

---

| Parameter | Spesifikasi |
| :--- | :--- |
| **Nama Proyek** | IDX-Intel AI (Corporate Action & IHSG Market Monitor) |
| **Versi Dokumen** | v2.0.0 |
| **Bahasa Pemrograman** | Python 3.12+ |
| **Core Architecture** | Router-Service-Repository Pattern (FastAPI APIRouter / Controller), SOLID Principles |
| **Core Stack** | FastAPI, LangGraph, WAHA (WhatsApp HTTP API), SQLite, Redis |
| **Database Transaction** | Full ACID-Compliant Persistence (SQLAlchemy Async Engine + asyncpg) |

---

## 1. Executive Summary & Latar Belakang

Di Bursa Efek Indonesia (BEI / IHSG), informasi seputar **Aksi Korporasi (Corporate Actions)** dan **Pergerakan Konglomerat / Pemain Kunci (Konglo Moves)** merupakan katalis utama (*market catalyst*) yang memicu pergeseran valuasi, akumulasi/distribusi saham, serta volatilitas harga. 

Informasi penting ini sering kali tersebar di berbagai kanal:
- Pengumuman Keterbukaan Informasi BEI (IDX Announcements dalam format PDF/Teks)
- Berita Pasar Modal & RSS Feeds (Bisnis, CNBC Indonesia, Kontan, Bloomberg Technoz)
- Laporan Kepemilikan Saham > 5% & Kustodian Sentral Efek Indonesia (KSEI)

Investor, analis, dan *trader* sering kali kehilangan momentum (*alpha*) karena keterlambatan dalam membaca, memverifikasi, dan menyimpulkan dampak dari pengumuman yang panjang dan kompleks.

**IDX-Intel AI** dirancang sebagai platform pemantauan (*monitoring system*) dan analisis otomatis berbasis **AI Orchestration (LangGraph)** dan **FastAPI**. Sistem ini secara kontinu mengagregasi data dari bursa dan media, mengekstrak fakta penting secara rasional dan terstruktur menggunakan Large Language Models (LLM), serta mendistribusikan *alert* ringkas secara *real-time* langsung ke WhatsApp pengguna melalui **WAHA (WhatsApp HTTP API)**.

---

## 2. Tujuan & Ruang Lingkup Sistem

### 2.1 Tujuan Utama (Primary Objectives)
1. **Automated Data Aggregation:** Monitoring 24/7 terhadap pengumuman BEI, KSEI, dan RSS feeds berita pasar saham.
2. **AI-Powered Event Extraction:** Identifikasi jenis aksi korporasi secara akurat, ekstraksi parameter kuantitatif (rasio, harga pelaksanaan, tanggal penting, nilai transaksi), dan analisis potensi dampak terhadap saham/sektor.
3. **Real-time WhatsApp Alerting:** Pengiriman notifikasi terstruktur, terformat, dan mudah dibaca langsung ke grup/nomor personal WhatsApp via WAHA.
4. **Interactive Inbound Commands:** Kemampuan menerima perintah interaktif dari pengguna WhatsApp (misal: `/cek BBCA`, `/summary`, `/subscribe`).
5. **Enterprise Engineering Standard:** Implementasi pola **Router-Service-Repository (FastAPI APIRouter)**, prinsip **SOLID**, serta jaminan transaksi **ACID** pada lapisan penyimpanan data.

### 2.2 Ruang Lingkup Event Saham yang Dipantau (Klasifikasi Ketat 3 Kategori)

Sistem menerapkan **penyaringan intelijen pasar (*Strict Filtering Pipeline*)** untuk mengeliminasi *noise* aksi korporasi rutin dan fokus 100% pada pergerakan *Smart Money* serta aksi korporasi berdaya ledak tinggi. Pengumuman dan berita HANYA diklasifikasikan ke dalam 3 (tiga) kategori berikut:

1. **`"BACKDOOR_LISTING"`**:
   - Injeksi aset/bisnis baru ke perusahaan cangkang (*shell company*) / emiten *dormant*.
   - Perubahan kegiatan usaha utama secara drastis setelah pengambilalihan.
   - *Reverse takeover* / Penambahan Modal Tanpa HMETD jumbo yang mengubah lini bisnis inti.

2. **`"KONGLO_MOVE"`**:
   - Akumulasi saham oleh *Smart Money*, Konglomerat, Grup Bisnis Besar (misal: Barito/Prajogo Pangestu, Salim, Djarum, Bakrie, Agung Sedayu, Panin, Chandra Asri, dll.).
   - Transaksi *Crossing* Saham jumbo di Pasar Negosiasi oleh investor institusi/strategis.
   - Perubahan Pemegang Saham Pengendali (PSP) atau pembelian porsi kepemilikan > 5%.
   - *Mandatory Tender Offer* (MTO) yang dipicu oleh akuisisi grup besar.
   - *Right Issue* yang hype.

3. **`"IRRELEVANT"`**:
   - Berita aksi korporasi rutin: *Rights Issue* biasa tanpa pembeli siaga konglo, Pembagian Dividen, Laporan Keuangan rutin, UMA/Suspensi biasa, atau berita umum yang tidak melibatkan *Backdoor Listing* / *Smart Money Accumulation*.

> [!IMPORTANT]
> **Aturan Ketat:**  
> Jika berita **TIDAK** memuat indikasi jelas tentang *Backdoor Listing* atau Pergerakan *Smart Money* / Grup Besar, Kembalikan kategori **`"IRRELEVANT"`**.

### 2.3 Sumber Data & Target Scraping (Scraper Data Sources)

Sistem secara asinkron memantau **BEI (Bursa Efek Indonesia / IDX Announcements)** serta 5 (lima) mesin dan portal berita finansial dengan karakteristik, kecepatan, dan metode ekstraksi spesifik sebagai berikut:

| Sumber Media / Portal | Status Biaya | Karakteristik Kecepatan (*Fast News*) | Tingkat Keamanan Anti-Bot | Metode Ekstraksi & URL Target / Endpoint |
| :--- | :--- | :--- | :--- | :--- |
| **0. BEI / IDX Announcements**<br>(*Keterbukaan Informasi BEI*) | **100% GRATIS**<br>(Portal Resmi) | **Resmi & Otoritatif:** Sumber primer pengumuman emiten BEI dan jadwal aksi korporasi. | **Rendah - Sedang** | • **Metode:** Plain HTTP GET / JSON API IDX<br>• **Target:** `https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi` |
| **1. Google News RSS Engine**<br>(*Pilihan Terbaik & Paling Aman*) | **100% GRATIS**<br>(Tanpa API Key / Lisensi) | **Sangat Cepat:** Mengindeks artikel media finansial nasional (CNBC, Kontan, Bisnis.com, Investor Daily) hanya dalam hitungan detik hingga menit setelah tayang. | **Sangat Rendah (Nihil):** Request ke endpoint RSS Google, tanpa proteksi Cloudflare, Akamai, atau CAPTCHA. | • **Metode:** RSS Feed Aggregator (`httpx` + BeautifulSoup)<br>• **Endpoint:** `https://news.google.com/rss/search?q={QUERY}&hl=id-ID&gl=ID&ceid=ID:id`<br>• **Contoh Query:** `site:kontan.co.id OR site:cnbcindonesia.com ("stock split" OR "rights issue" OR "akuisisi" OR "backdoor listing")` |
| **2. RSS Feed Resmi CNBC Indonesia**<br>(*Section Market*) | **100% GRATIS** | **Sangat Cepat:** Portal paling agresif untuk *breaking news*, rumor pasar, pergerakan grup konglomerat (Barito, Salim, Bakrie, Djarum), dan UMA/Suspensi. | **Sangat Rendah:** Endpoint RSS bersih dari script & proteksi iklan web utama. | • **Metode:** RSS Feed Parsing<br>• **Endpoint:** `https://www.cnbcindonesia.com/market/rss/` |
| **3. RSS Feed Resmi Kontan Investasi** | **100% GRATIS** | **Cepat & Sangat Detail:** Standar media digital/cetak untuk perincian aksi korporasi secara mendetail (Stock Split, Rights Issue, Tender Offer, Warrant). | **Sangat Rendah** pada endpoint RSS. | • **Metode:** RSS Feed Parsing<br>• **Endpoint:** `https://rss.kontan.co.id/news/keuangan` atau `https://investasi.kontan.co.id/rss` |
| **4. IDN Financials**<br>(*Corporate Action Section*) | **100% GRATIS** | **Moderat:** Fokus pada kelengkapan data kuantitatif terstruktur (rasio pasti stock split, cum-date, kepemilikan >5%). | **Sangat Rendah:** Server-Side Rendering (SSR) murni tanpa proteksi WAF tingkat tinggi. | • **Metode:** Direct HTML Table Parsing<br>• **Target:** `https://www.idnfinancials.com/id/corporate-action` |
| **5. IPOTNews**<br>(*IndoPremier News Feed*) | **100% GRATIS** | **Sangat Cepat:** Menyalin teks ringkasan Keterbukaan Informasi resmi BEI secara otomatis ke dalam format web sederhana. | **Sangat Rendah:** HTML ringan dan mudah di-parse. | • **Metode:** Plain HTTP GET (`httpx` + BeautifulSoup)<br>• **Target:** `https://www.ipotnews.com` |

---

## 3. Arsitektur Perangkat Lunak & Prinsip Desain

Sistem dirancang secara modular dan *decoupled* menggunakan tiga pilar utama arsitektur modern:

### 3.1 Pattern Router-Service-Repository (FastAPI APIRouter / Controller)

```text
                  ┌──────────────────────────────────────────┐
                  │   Inbound Webhook / HTTP Client / Cron   │
                  └────────────────────┬─────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ ROUTER LAYER (FastAPI APIRouters - Controller Layer)                       │
│ • Validasi Request/Webhook Payload (Pydantic)                               │
│ • Mengembalikan HTTP Status & Response                                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SERVICE LAYER (Business Logic & LangGraph Workflow)                         │
│ • AgentService: Mengelola alur eksekusi LangGraph (StateGraph)              │
│ • ScraperService: Agregasi data dari BEI / RSS Feed                         │
│ • WahaService: Client API untuk kirim pesan ke WAHA                         │
│ • NotificationService: Merakit pesan & mengelola antrean notifikasi        │
└──────────────────┬──────────────────────────────────────┬───────────────────┘
                   │                                      │
                   ▼                                      ▼
┌──────────────────────────────────────┐┌─────────────────────────────────────┐
│ AI AGENT LAYER (LangGraph)           ││ REPOSITORY LAYER (Data Access)      │
│ • Ingestion -> Classify -> Extract   ││ • EventRepository                   │
│ • Impact Analysis -> WA Formatting   ││ • UserRepository                    │
│                                      ││ • AlertLogRepository                │
└──────────────────────────────────────┘└──────────────────┬──────────────────┘
                                                           │
                                                           ▼
                                        ┌─────────────────────────────────────┐
                                        │ DATABASE / CACHE LAYER              │
                                        │ • PostgreSQL (Asyncpg + SQLAlchemy) │
                                        │ • Redis (Cache & Session Store)     │
                                        └─────────────────────────────────────┘
```

1. **Router Layer (`app/routers/` — Controller):**
   - Bertanggung jawab penuh atas penanganan HTTP Request/Response.
   - Menggunakan Pydantic Schemas untuk validasi *payload* masukan dari Webhook WAHA maupun endpoint Admin.
   - Tidak memuat logika bisnis maupun panggilan database langsung.

2. **Service Layer (`app/services/`):**
   - Berisi seluruh logika bisnis utama aplikasi.
   - Mengkoordinasikan eksekusi *scrapers*, pemrosesan state *LangGraph*, pemformatan notifikasi, serta pemanggilan API eksternal WAHA.

3. **Repository Layer (`app/repositories/`):**
   - Menyediakan antarmuka terisolasi untuk akses data ke database PostgreSQL.
   - Menggunakan `SQLAlchemy` versi 2.0 dengan *async engine* (`asyncpg`) untuk menjamin performa tinggi dan keterpisahan logika query SQL dari logika bisnis.

---

### 3.2 Penerapan Prinsip SOLID

- **Single Responsibility Principle (SRP):** Setiap modul memiliki satu fungsi spesifik. `WAHAService` hanya menangani komunikasi HTTP ke server WAHA, `EventRepository` hanya mengurus query tabel event, dan `ExtractorNode` pada LangGraph hanya mengekstrak fakta JSON.
- **Open/Closed Principle (OCP):** Penambahan sumber data baru (misal: Scraper KSEI) dilakukan dengan menambahkan class baru yang mengimplementasikan antarmuka `BaseScraper` tanpa perlu mengubah kode `ScraperService` utama.
- **Liskov Substitution Principle (LSP):** Antarmuka repositori abstrak (`BaseRepository`) memastikan bahwa implementasi repositori dapat diganti (misal: *In-Memory Repository* untuk testing vs *Postgres Repository* untuk produksi) tanpa merusak *Service Layer*.
- **Interface Segregation Principle (ISP):** Interface dirancang ringkas dan spesifik. Modul yang hanya memerlukan fungsi pengiriman notifikasi hanya mengimpor `INotificationService`.
- **Dependency Inversion Principle (DIP):** *Service Layer* dan *Router Layer (Controller)* tidak melakukan instansiasi dependensi secara langsung (*hardcoded*), melainkan memanfaatkan Dependency Injection yang disediakan oleh framework **FastAPI (`Depends`)**.

---

### 3.3 Jaminan Transaksi Database (ACID Compliance)

Penyimpanan data aksi korporasi dan log notifikasi mengutamakan integritas data sesuai standar **ACID**:

- **Atomicity (Keutuhan):** Operasi yang melibatkan penyimpanan event baru dan pembuatan log antrean notifikasi berada dalam satu transaksi (*Database Session Context Manager*). Jika terjadi kegagalan jaringan saat menyimpan event, transaksi di-`rollback` secara utuh.
- **Consistency (Konsistensi):** Setiap event memiliki unik hash (`event_hash = SHA256(ticker + event_type + publication_date + title)`). Skema database menerapkan *Unique Constraint* pada `event_hash` untuk memblokir duplikasi data secara permanen di level database.
- **Isolation (Isolasi):** Transaksi berjalan pada level isolasi `READ COMMITTED` (standar PostgreSQL) untuk mencegah kondisi *dirty read* saat multiple worker scraper berjalan secara simultan.
- **Durability (Ketahanan):** Setelah transaksi di-`commit`, data tersimpan di disk PostgreSQL dengan penulisan *Write-Ahead Logging (WAL)* yang tahan terhadap mati listrik atau *restart* server.

---

## 4. Alur Kerja Agentic AI (LangGraph StateGraph)

Sistem menggunakan **LangGraph** untuk mengarsitekturi proses analisis dokumen secara bertahap (*multi-step reasoning graph*), menggantikan pendekatan single-prompt yang rentan terhadap instruksi yang terlewat.

```text
                  ┌───────────────────────────────┐
                  │          [ START ]            │
                  └──────────────┬────────────────┘
                                 │
                                 ▼
                  ┌───────────────────────────────┐
                  │        IngestionNode          │
                  │  (Clean text, extract meta)   │
                  └──────────────┬────────────────┘
                                 │
                                 ▼
                  ┌───────────────────────────────┐
                  │         ClassifierNode        │
                  │  (Is Corporate Action? Type)  │
                  └──────────────┬────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │ Apakah Aksi Korporasi?    │
                   └──────┬─────────────┬──────┘
                       YA │             │ TIDAK
                          ▼             ▼
  ┌──────────────────────────┐   ┌──────────────────────────┐
  │      ExtractorNode       │   │          [ END ]         │
  │ (JSON Schema Extraction) │   │  (Ignore Non-Event Text) │
  └──────────────┬───────────┘   └──────────────────────────┘
                 │
                 ▼
  ┌──────────────────────────┐
  │      ImpactNode          │
  │ (Sentiment & Evaluation) │
  └──────────────┬───────────┘
                 │
                 ▼
  ┌──────────────────────────┐
  │     WAFormatterNode      │
  │ (Generate WA Markdown)   │
  └──────────────┬───────────┘
                 │
                 ▼
  ┌──────────────────────────┐
  │          [ END ]         │
  │ (Push to WAHA Dispatch)  │
  └──────────────────────────┘
```

### Detail Node LangGraph:
1. **IngestionNode:** Membersihkan teks HTML/PDF mentah, mengekstrak metadata dasar (URL sumber, tanggal publikasi, ticker saham jika terdeteksi).
2. **ClassifierNode:** Mengklasifikasikan dokumen HANYA ke dalam 3 kategori ketat: `BACKDOOR_LISTING`, `KONGLO_MOVE`, atau `IRRELEVANT` (sesuai Aturan Ketat pemantauan *Smart Money* & *Konglomerat*).
3. **ExtractorNode:** Menggunakan *Structured Output* (Pydantic) untuk menarik parameter kunci seperti rasio, nominal, tanggal penting (*cum/ex date*), harga pelaksanaan, dan nama entitas akuisisi.
4. **ImpactNode:** Menganalisis dampak finansial dan sentimen (*Bullish / Bearish / Neutral*) terhadap likuiditas, struktur permodalan, dan respon pasar.
5. **WAFormatterNode:** Menyusun hasil analisis menjadi pesan teks yang memenuhi kaidah estetika pesan WhatsApp (menggunakan emoji, cetak tebal, bullet points, dan layout rapi).

### 4.2 LLM Prompt Engineering & Aturan Rekomendasi (`app/services/prompt.py`)
Sistem menyimpan seluruh instruksi, *system prompt*, dan logika *reasoning* LLM dalam modul terpusat pada layer Business Logic Service yaitu `app/services/prompt.py`. 

Modul ini mengimplementasikan dua aturan utama *prompting*:
1. **Aturan Klasifikasi Ketat (*Strict 3-Category Classification*):**  
   - LLM diinstruksikan untuk memvalidasi apakah pengumuman/berita secara spesifik menunjukkan **`BACKDOOR_LISTING`** atau **`KONGLO_MOVE`**.  
   - **Aturan Ketat:** Jika berita TIDAK memuat indikasi jelas tentang *Backdoor Listing* atau pergerakan *Smart Money* / Grup Besar, sistem wajib mengembalikan kategori **`IRRELEVANT`**.
2. **Aturan Rekomendasi Saham & Kelas Output (*Investment Recommendation Engine*):**  
   - LLM diinstruksikan menghasilkan klasifikasi kelas output rekomendasi (*Recommendation Class*) terstruktur dan mencantumkan *headline* **`🎯 Rekomendasi : [Class: <NAMA_KELAS>]`** setelah bagian Analisis dengan kriteria sebagai berikut:
   - **a. `STRONG_BUY_AKUMULASI` (Prioritas Tertinggi):**
     - Diberikan apabila aksi korporasi, perubahan kepemilikan saham (> 5%), atau berita pasar menunjukkan adanya pembelian/akumulasi nyata oleh **Top 200 Orang Terkaya & Terkenal di Indonesia atau Dunia** (misalnya: Prajogo Pangestu / Grup Barito, Anthoni Salim, Boy Thohir, Robert Budi Hartono, Sukanto Tanoto, BlackRock, Vanguard, dll.).
     - LLM diinstruksikan untuk menyoroti nama konglomerat/institusi, potensi aksi korporasi besar (*backdoor listing*, *M&A*, injeksi modal), serta strategi *following smart money*.
   - **b. `BUY`:**
     - Diberikan untuk aksi korporasi positif dengan valuasi dan dampak pertumbuhan organik yang jelas (misal: *Stock Split* rasio ideal, *Rights Issue* untuk ekspansi produktif tanpa dilusi berlebih).
   - **c. `HOLD_WATCH`:**
     - Diberikan pada aksi korporasi netral atau masih menunggu konfirmasi jadwal resmi.
   - **d. `AVOID`:**
     - Diberikan jika terdapat suspensi negatif, UMA berisiko tinggi tanpa fundamental, atau divestasi oleh pemegang saham pengendali.

---

## 5. Integrasi WhatsApp Gateway (WAHA)

Aplikasi memanfaatkan **WAHA (WhatsApp HTTP API)** sebagai gateway komunikasi dua arah.

### 5.1 Format Outbound Notification (Alert Otomatis)

Pada pesan notifikasi WAHA, *field* **Kategori** wajib diisi berdasarkan kelas aksi korporasi (*class of the action*) dari kategori utama yang teridentifikasi (`BACKDOOR_LISTING` atau `KONGLO_MOVE`), diikuti dengan rincian jenis pergerakannya, serta mencantumkan kelas rekomendasi yang dihasilkan oleh AI.

```text
🚨 [IDX-INTEL ALERT] AKSI KORPORASI 🚨
------------------------------------------------
Emiten  : $BUMI (PT Bumi Resources Tbk)
Kategori: 👑 KONGLO_MOVE (Akumulasi Saham oleh Smart Money / Grup Besar)

👤 Investor/Grup : Mach Energy (Grup Salim)
🔄 Jenis Transaksi: Crossing Pasar Negosiasi / Private Placement

📊 Detail Aksi Korporasi:
• Harga Eksekusi   : Rp 120 / saham
• Nilai Transaksi   : ± Rp 24 Triliun
• Total Kepemilikan : 37.1% (Joint Control dengan Grup Bakrie)

💡 Analisis:
Masuknya Grup Salim memperkuat struktur permodalan dan memangkas beban utang emiten secara signifikan. Sinyal akumulasi jangka panjang.

🎯 Rekomendasi [Class: STRONG_BUY_AKUMULASI] :
STRONG BUY / AKUMULASI — Aksi korporasi didukung oleh akumulasi kepemilikan oleh Top Konglomerat Indonesia (Anthoni Salim / Grup Salim), mengindikasikan prospek ekspansi jangka panjang yang sangat kuat dan partisipasi "smart money".
🔗 Sumber: Keterbukaan Informasi BEI (IDX Announcements)
```

### 5.2 Fitur Inbound Command (Command Handler)

Pengguna dapat mengirimkan perintah via pesan WhatsApp ke nomor bot WAHA:

| Perintah | Deskripsi | Contoh Respon / Output |
| :--- | :--- | :--- |
| `/cek <TICKER>` | Menampilkan riwayat aksi korporasi terbaru dari emiten tertentu. | Menampilkan 3 event aksi korporasi terbaru $BBCA lengkap dengan ringkasan AI. |
| `/summary` | Menampilkan ringkasan aksi korporasi di BEI dalam 24 jam terakhir. | Daftar *bullet point* aksi korporasi hari ini yang teridentifikasi oleh sistem. |
| `/subscribe <TICKER>` | Mendaftarkan akun WA untuk mendapatkan notifikasi prioritas emiten spesifik. | "Berhasil berlangganan notifikasi instan untuk saham $BREN." |
| `/unsubscribe <TICKER>` | Membatalkan langganan notifikasi prioritas emiten. | "Berhenti berlangganan notifikasi $BREN." |
| `/help` | Menampilkan daftar perintah yang tersedia. | Panduan penggunaan bot IDX-Intel AI. |

### 5.3 Optimasi Kinerja, Proteksi & Caching (Rate Limiting & Redis Cache)

- **Rate Limiting / Throttling:**  
  Pada perintah interaktif WhatsApp (`/cek`, `/summary`), dapat ditambahkan lapisan middleware *Rate Limiter* agar sistem terhindar dari *spam command* atau DDoS.
- **Redis Caching:**  
  Untuk perintah `/summary` atau `/cek <TICKER>`, hasil agregasi dapat disimpan di **Redis cache** selama **5–10 menit** guna mengurangi beban *query* ke PostgreSQL pada saat trafik tinggi.

---

## 6. Structure Folder & Layout Proyek (Python 3.12)

Proyek ini menggunakan struktur modular modern berstandar industri:

```text
idx_intel_ai/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI & Lifespan Handler
│   ├── config.py                   # Configuration Loader (Pydantic Settings)
│   │
│   ├── routers/                    # Layer 1: HTTP API Routers & Webhooks (APIRouter / Controller)
│   │   ├── __init__.py
│   │   ├── health.py               # Endpoint /health & /metrics
│   │   ├── webhook.py              # Endpoint /webhook/waha (Inbound Messages)
│   │   └── monitor.py              # Endpoint /api/v1/monitor (Manual Trigger)
│   │
│   ├── services/                   # Layer 2: Business Logic Services
│   │   ├── __init__.py
│   │   ├── prompt.py               # Pusat Instruksi, System Prompt & Aturan Rekomendasi LLM
│   │   ├── scraper.py              # Agregasi & Koordinasi Scraper
│   │   ├── agent.py                # Pengelola Eksekusi LangGraph Pipeline
│   │   ├── waha.py                 # HTTP Client untuk WAHA API Endpoint
│   │   └── notification.py         # Logika Format & Dispatch Notifikasi
│   │
│   ├── agents/                     # AI Orchestration (LangGraph)
│   │   ├── __init__.py
│   │   ├── graph.py                # Konstruksi StateGraph & Compilation
│   │   ├── state.py                # Definisi TypedDict State
│   │   └── nodes/                  # Node Implementations
│   │       ├── __init__.py
│   │       ├── ingestion_node.py
│   │       ├── classifier_node.py
│   │       ├── extractor_node.py
│   │       ├── impact_node.py
│   │       └── formatter_node.py
│   │
│   ├── repositories/               # Layer 3: Database Access (ACID)
│   │   ├── __init__.py
│   │   ├── base_repository.py      # Abstract Generic Repository Interface
│   │   ├── event_repository.py     # SQLAlchemy Async Event Queries
│   │   ├── user_repository.py      # Management User & Subscriptions
│   │   └── alert_log_repository.py # History Log Pengiriman Notifikasi
│   │
│   ├── models/                     # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── base.py                 # Declarative Base Class
│   │   ├── event_model.py          # Tabel corporate_events
│   │   ├── user_model.py           # Tabel users & subscriptions
│   │   └── alert_log_model.py      # Tabel alert_logs
│   │
│   ├── schemas/                    # Pydantic Schemas / DTOs
│   │   ├── __init__.py
│   │   ├── waha_schema.py          # Payload Model WAHA Webhook
│   │   ├── event_schema.py         # Schema Extracted Event Fact
│   │   └── response_schema.py      # Standard HTTP API Response Format
│   │
│   ├── scrapers/                   # Data Acquisition Module (OCP)
│   │   ├── __init__.py
│   │   ├── base_scraper.py         # Abstract Base Scraper Interface
│   │   ├── idx_announcement_scraper.py # Scraper Keterbukaan Informasi Resmi BEI
│   │   ├── google_news_rss_scraper.py # Scraper Google News RSS Engine (Aggregator)
│   │   ├── cnbc_rss_scraper.py     # Scraper RSS Resmi CNBC Indonesia Market
│   │   ├── kontan_rss_scraper.py   # Scraper RSS Resmi Kontan Investasi
│   │   ├── idn_financials_scraper.py # Scraper IDN Financials Corporate Action (Tabel HTML)
│   │   └── ipotnews_scraper.py     # Scraper IPOTNews / IndoPremier News Feed
│   │
│   └── utils/                      # Utilities & Helpers
│       ├── __init__.py
│       ├── logger.py               # Structured Logging (structlog)
│       └── db_session.py           # Async Database Session Generator
│
├── docker/
│   ├── Dockerfile                  # Multi-stage Python 3.12 Dockerfile
│   └── docker-compose.yml          # Compose File: App + Postgres + Redis + WAHA
│
├── migrations/                     # Database Migrations (Alembic)
│   ├── versions/
│   └── env.py
│
├── tests/                          # Automated Tests
│   ├── unit/                       # Unit Test Services & Nodes
│   └── integration/                # Integration Test Webhooks & Repositories
│
├── .env.example                    # Sample Environment Variables
├── .env                            # Environment Variables
├── .gitignore
├── alembic.ini                     # Configuration Alembic
├── README.md                       # Dokumentasi Instalasi & Cara Jalankan
└── requirements.txt                # Dependensi Python 3.12
```

---

## 7. Dependensi & Library (`requirements.txt`)

Seluruh library telah diuji kompatibilitasnya dengan **Python 3.12**:

```text
# Web Framework & API Server
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
pydantic-settings>=2.2.0

# AI Orchestration & LLM Integration
langgraph>=0.1.5
langchain>=0.2.0
langchain-openai>=0.1.7
langchain-community>=0.2.0

# Web Scraping & Data Acquisition
httpx>=0.27.0
beautifulsoup4>=4.12.3
feedparser>=6.0.10
playwright>=1.44.0

# Database Persistence (ACID & Async)
SQLAlchemy[asyncio]>=2.0.30
asyncpg>=0.29.0
alembic>=1.13.1
redis>=5.0.4

# Task Scheduling & Background Jobs
apscheduler>=3.10.4

# Security, Logging & Helpers
python-dotenv>=1.0.1
structlog>=24.1.0

# Testing Suite
pytest>=8.2.0
pytest-asyncio>=0.23.0
```

---

## 8. Requirements Non-Fungsional & Keamanan

1. **Performansi & Caching (Performance):**
   - Latensi respon HTTP Webhook WAHA < 1.5 detik (menggunakan pemrosesan *async background task*).
   - Waktu eksekusi siklus *LangGraph* per dokumen pengumuman < 8.0 detik.
   - **Redis Caching:** Untuk perintah `/summary` atau `/cek <TICKER>`, hasil agregasi disimpan di Redis cache selama 5–10 menit guna mengurangi beban query ke PostgreSQL pada saat trafik tinggi.
2. **Keandalan (Reliability & Deduplication):**
   - Mekanisme *retry* otomatis dengan *Exponential Backoff* saat memanggil WAHA API jika terjadi gangguan koneksi sementara.
   - Pengecekan *duplicate event* berbasis SHA-256 Hash di level *Repository* sebelum memicu *LangGraph Agent*, menghemat penggunaan kredit LLM API hingga 60%.
3. **Keamanan & Proteksi Trafik (Security & Throttling):**
   - Otentikasi Webhook WAHA menggunakan header `X-Api-Key` atau Secret Token.
   - Sanitasi input pesan teks dari pengguna WhatsApp untuk mencegah serangan *Prompt Injection* ke modul LLM.
   - **Rate Limiting / Throttling:** Pada perintah interaktif WhatsApp (`/cek`, `/summary`), ditambahkan lapisan middleware *Rate Limiter* agar sistem terhindar dari *spam command* atau DDoS.

---

## 9. Roadmap Pengembangan & Milestone

| Fase | Target | Luaran Utama (Deliverables) |
| :--- | :--- | :--- |
| **Fase 1** | Setup Proyek, Environment Python 3.12, Docker Compose (FastAPI + PostgreSQL + Redis + WAHA), Schema DB & Migrasi Alembic. |
| **Fase 2** | Implementasi `BaseScraper`, `IDXAnnouncementScraper`, `GoogleNewsRSSScraper`, `CNBCRSSScraper`, `KontanRSSScraper`, `IDNFinancialsScraper`, `IPOTNewsScraper`, dan `EventRepository` dengan jaminan transaksi ACID. |
| **Fase 3** | Pembangunan StateGraph **LangGraph**: Ingestion, Classifier, Extractor, Impact Evaluator, dan WA Formatter Nodes. |
| **Fase 4** | Integrasi `WAHAService` & Webhook Handler, Pengolahan Inbound Commands (`/cek`, `/summary`, `/subscribe`). |
| **Fase 5** | Unit & Integration Testing, Optimasi Prompt LLM, Stress Test Webhook, serta Deployment ke Server Staging. |

---

## 10. Kesimpulan

PRD versi ini memberikan panduan komprehensif dalam membangun sistem pemantau aksi korporasi **IDX-Intel AI**. Melalui kombinasi arsitektur **Router-Service-Repository (FastAPI APIRouter)**, kepatuhan penuh terhadap **Prinsip SOLID**, pengelolaan transaksi berjaminan **ACID**, *orchestration* berbasis **LangGraph**, serta integrasi **WAHA**, sistem ini menjamin keandalan, skalabilitas, dan kecepatan penyampaian *market intelligence* bagi para pelaku pasar saham Indonesia.
