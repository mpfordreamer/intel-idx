# Product Requirement Document (PRD)
## AI-Driven IDX Corporate Action & Multi-Market Sector Intelligence System (IDX-Intel AI)

---

| Parameter | Spesifikasi |
| :--- | :--- |
| **Nama Proyek** | IDX-Intel AI (Corporate Action, Sector & Global Commodity Intelligence) |
| **Versi Dokumen** | v2.2.0 (Enterprise Multi-Horizon, Multi-Market & Dedicated WA Groups Edition) |
| **Bahasa Pemrograman** | Python 3.12+ |
| **Core Architecture** | Router-Service-Repository Pattern (FastAPI APIRouter / Controller), SOLID Principles |
| **Core Stack** | FastAPI, LangGraph, WAHA (WhatsApp HTTP API), PostgreSQL, Redis |
| **Database Transaction** | Full ACID-Compliant Persistence (SQLAlchemy Async Engine + asyncpg) |

---

## 1. Executive Summary & Latar Belakang

Di Bursa Efek Indonesia (BEI / IHSG) serta pasar finansial global, pergerakan harga saham dan arus modal digerakkan oleh dua katalis utama:
1. **Aksi Korporasi & Konglo Moves di BEI:** Stock Split, Reverse Takeover, Injeksi Aset, Rights Issue, dan transaksi crossing oleh konglomerat utama (*Smart Money*).
2. **Sentimen Sektor Makro & Komoditas Dunia:** Fluktuasi harga komoditas strategis (Emas, Perak, Tembaga, Timah, Aluminium, Nikel, Minyak Mentah, Batu Bara, Litium, Uranium, CPO) serta rotasi modal di bursa global (S&P 500, US Tech & Semis, US Financials).

Sering kali investor ritel maupun institusi:
- **Terjebak kesimpulan sesaat (*momentary conclusion*):** Rekomendasi yang hanya melihat satu berita tanpa melihat rentetan aksi masa lalu emiten (misal: emiten sedang dililit utang gadai saham, namun disimpulkan *Strong Buy* hanya karena ada rumor konglo).
- **Template hardcoded yang kaku:** Notifikasi yang menyajikan bullet point statis 'Detail Aksi Korporasi' yang sering kali tidak relevan atau kosong jika rincian nominal tidak dipublikasikan lengkap.
- **Ketiadaan panduan horizon waktu:** Tidak membedakan antara potensi volatilitas jangka pendek (1–14 hari) dengan nilai fundamental jangka panjang (6–12 bulan).
- **Pencampuran audiens komunitas:** Pesan bursa Indonesia dan bursa Wall Street/S&P 500 tercampur dalam satu grup WhatsApp yang membingungkan anggota komunitas.

**IDX-Intel AI v2.2.0** hadir sebagai platform intelijen pasar otonom yang menggabungkan:
1. **Mesin Rekomendasi Kontekstual Berbasis Memori Historis:** Membaca kontinuitas aksi korporasi emiten di database sebelum menyimpulkan rekomendasi, menyajikan perspektif multi-horizon, dan menetapkan titik pembatalan analisis (*invalidation triggers*).
2. **100% Dynamic AI-Generated Message:** Menghilangkan template statis/manual 'Detail Aksi Korporasi'; seluruh narasi latar belakang, analisis aksi, dan horizon disusun secara cerdas oleh AI.
3. **Pemisahan Grup WhatsApp WAHA untuk Komunitas S&P 500:** Membedakan kanal pengiriman antara bursa lokal (`BROADCAST_CHAT_ID`) dan pasar global (`BROADCAST_CHAT_ID_SP500`).
4. **Intelijen Sektor Real-Time Multi-Market (`/api/v1/sectors`):** Mengagregasi berita real-time dari TradingView, Yahoo Finance, dan CNBC untuk merekomendasikan sektor terbaik di Komoditas, S&P 500, dan IDX.
5. **Format Notifikasi WhatsApp Terstandarisasi:** Mempertahankan label dengan format underscore (`_`) seperti `[Class: STRONG_BUY_AKUMULASI]`, `[Class: ACCUMULATE_ON_WEAKNESS]`, `[Class: HOLD_WATCH]`, dan `[Class: AVOID]`.

---

## 2. Tujuan & Ruang Lingkup Sistem

### 2.1 Tujuan Utama (Primary Objectives)
1. **Continuous Multi-Source Aggregation:** Pemantauan kontinu terhadap pengumuman resmi BEI serta feed berita real-time (TradingView, Yahoo Finance, CNBC, Kontan, Google News).
2. **Context-Aware Corporate Action Analysis:** Menganalisis emiten dengan mempertimbangkan riwayat aksi korporasi sebelumnya di PostgreSQL, mengeliminasi kesimpulan sesaat, dan menetapkan *Invalidation Triggers*.
3. **100% Dynamic AI-Generated Outbound Alerts:** Seluruh pesan disusun dinamis dan cerdas oleh AI tanpa template isian hardcoded.
4. **Multi-Channel WAHA Dispatch:** Mendukung perutean notifikasi ke grup yang berbeda (`BROADCAST_CHAT_ID` untuk IDX vs `BROADCAST_CHAT_ID_SP500` untuk S&P 500).
5. **Real-Time Sector Recommendation Engine:** Memberikan peringkat rekomendasi sektor (Komoditas Strategis, S&P 500, dan 11 Sektor IDX-IC) melalui prefix endpoint `/api/v1/sectors`.
6. **Zero-Breaking-Change Guarantee:** Mempertahankan seluruh endpoint existing (`/api/v1/monitor`, `/events`, `/call/*`, `/chat`, `/health`) dan alur LangGraph lama tanpa interupsi.

---

### 2.2 Taksonomi Sektor Multi-Market (3 Pilar Lengkap)

#### Pilar A: Sektor Komoditas Strategis Dunia (Commodities)
1. **Timah (*Tin*):** Pasar LME-TIN, emiten terkait: `$TINS`.
2. **Aluminium:** Pasar LME-ALU, emiten terkait: `$INAI`, `$ALMI`, `$ALUM`.
3. **Tembaga (*Copper*):** Pasar HG1!, emiten terkait: `$AMMN`, `$MDKA`.
4. **Nikel (*Nickel*):** Pasar LME-NICKEL, emiten terkait: `$INCO`, `$ANTM`, `$NCKL`, `$MBMA`.
5. **Emas & Perak (*Precious Metals*):** XAUUSD, XAGUSD, emiten terkait: `$ANTM`, `$MDKA`, `$BRMS`, `$ARCI`, `$PSAB`.
6. **Litium & Logam Baterai:** Saham lithium global (ALB, SQM), mineral kritis.
7. **Platinum & Palladium:** PL1!, PA1! (industri otomotif & hidrogen hijau).
8. **Minyak Mentah (*Crude Oil*):** WTI (`CL`), Brent (`BRN`), emiten terkait: `$MEDC`, `$ENRG`, `$ELSA`.
9. **Batu Bara (*Thermal & Metallurgical Coal*):** Newcastle Coal, emiten terkait: `$ADRO`, `$PTBA`, `$ITMG`, `$BUMI`, `$BYAN`.
10. **Gas Alam (*Natural Gas*):** NG1!, emiten terkait: `$PGAS`, `$RAJA`.
11. **Uranium & Energi Nuklir:** Global Uranium ETF (URA), Cameco (CCJ).
12. **Minyak Kelapa Sawit (*CPO*):** MDEX CPO, emiten terkait: `$AALI`, `$LSIP`, `$TAPG`, `$DSNG`.

#### Pilar B: Sektor S&P 500 & Global Equities (Wall Street)
1. **Semiconductors & AI Hardware:** NVDA, TSM, AMD, AVGO, ASML, QCOM.
2. **Mega Tech & Cloud Platforms:** MSFT, AAPL, AMZN, GOOGL, META.
3. **US Mega Banks & Financial Services:** JPM, BAC, WFC, GS, MS.
4. **Aerospace & Defense:** LMT, RTX, BA, NOC.
5. **US Macro Indicators:** S&P 500 (`^GSPC`), Nasdaq 100 (`^IXIC`), US Dollar Index (`DXY`), US 10-Year Treasury Yield.

#### Pilar C: Sektor Bursa Efek Indonesia (IDX-IC 11 Sektor)
1. Keuangan (*Financials*): BBCA, BBRI, BMRI, BBNI.
2. Energi (*Energy*): ADRO, PTBA, PGAS, MEDC.
3. Barang Baku (*Basic Materials*): ANTM, MDKA, TPIA, INCO, BRPT.
4. Kesehatan (*Healthcare*): MIKA, HEAL, SILO, KLBF.
5. Teknologi (*Technology*): GOTO, BUKA, EMTK, DCII.
6. Infrastruktur (*Infrastructure*): TLKM, ISAT, TOWR, TBIG, JSMR.
7. Konsumer Primer (*Consumer Non-Cyclical*): ICBP, INDF, UNVR, MYOR.
8. Konsumer Non-Primer (*Consumer Cyclical*): ASII, ACES, MAPI.
9. Perindustrian (*Industrials*): UNTR, ARNA.
10. Properti & Real Estat (*Properties*): BSDE, CTRA, PWON, SMRA.
11. Transportasi & Logistik (*Transportation*): SMDR, TMAS, ASSA, BIRD.

---

### 2.3 Matriks Sumber Data & Target Scraper

| Sumber Media / Scraper | Target & Karakteristik | Metode & Endpoint |
| :--- | :--- | :--- |
| **TradingView Real-Time Scraper**<br>(*Baru*) | Breaking news real-time multi-market (IDX, S&P 500, Komoditas: Timah, Aluminium, Emas, Perak, Minyak) dari Reuters, Kontan, Dow Jones, FXStreet. | HTTP Async (`httpx`)<br>`https://news-headlines.tradingview.com/v2/headlines?client=web&lang=id` |
| **Yahoo Finance Scraper**<br>(*Baru*) | Feed terstruktur berita pasar global, komoditas energi, logam, dan makro Wall Street. | HTTP Async (`httpx`)<br>`https://query2.finance.yahoo.com/v1/finance/search` |
| **CNBC Indonesia Market RSS** | Breaking news emiten dan pergerakan konglomerat Indonesia. | RSS Feed Parsing (`feedparser`)<br>`https://www.cnbcindonesia.com/market/rss` |
| **BEI / IDX Announcements** | Pengumuman resmi bursa, Keterbukaan Informasi, dan prospektus emiten. | Plain HTTP GET / JSON API IDX |
| **Google News RSS Engine** | Aggregator berita pasar modal nasional tanpa CAPTCHA. | RSS Feed Engine (`feedparser`) |
| **Kontan Investasi RSS** | Detail aksi korporasi pasar modal Indonesia. | RSS Feed Parsing |
| **IDN Financials** | Data kuantitatif tabel aksi korporasi dan kepemilikan saham >5%. | HTML Table Scraping |
| **IPOTNews** | Ringkasan berita pasar modal IndoPremier. | HTML Parsing |

---

## 3. Arsitektur Router-Service-Repository & SOLID Compliance

```text
       REQUEST (WAHA Webhook / CRON / Client API)
                         │
                         ▼
   ┌───────────────────────────────────────────────┐
   │                 ROUTER LAYER                  │
   │  • health.py, webhook.py, monitor.py, call.py │ ◄── [Existing Endpoints TETAP UTUH]
   │  • sectors.py (/api/v1/sectors/*)             │ ◄── [Prefix Endpoint Sektor Baru]
   └──────────────────────┬────────────────────────┘
                          │
                          ▼
   ┌───────────────────────────────────────────────┐
   │                SERVICE LAYER                  │
   │  • AgentExecutionService & WahaService        │
   │  • SectorCoordinatorService                   │ ◄── [Aggregator Multi-Scraper]
   │  • SectorIntelligenceService                  │ ◄── [AI Sector Stance & Katalis]
   └──────────────────────┬────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
   ┌─────────────┐                 ┌─────────────┐
   │  AI AGENTS  │                 │ REPOSITORY  │
   │ (LangGraph) │                 │ (EventRepo) │ ◄── [Injeksi 5 Event Historis]
   └─────────────┘                 └──────┬──────┘
                                          │
                                          ▼
                                [ PostgreSQL / Redis ]
```

---

## 4. Mesin Rekomendasi Kontekstual Multi-Horizon

### 4.1 Injeksi Memori Historis Emiten
Sebelum `recommendation_node` memproses dokumen berita emiten, sistem mengeksekusi:
```python
past_events = await event_repo.get_latest_by_ticker(ticker, limit=5)
```
Ringkasan peristiwa masa lalu emiten (seperti gadai saham, restrukturisasi utang, atau akuisisi) diinjeksikan ke prompt LLM, memastikan sistem memahami *arah cerita* emiten dan tidak tertipu oleh fluktuasi sesaat.

### 4.2 Standar Kelas Rekomendasi dengan Underscore (`_`)
Output rekomendasi dikirim dengan format headline baku:
`🎯 Rekomendasi : [Class: <LABEL_UNDERSCORE>]`

Daftar Stance Baku:
- `STRONG_BUY_AKUMULASI`: Akumulasi nyata oleh Top Konglomerat / Smart Money dengan fundamental kuat.
- `BUY`: Aksi korporasi positif dengan ekspansi organik yang jelas.
- `ACCUMULATE_ON_WEAKNESS`: Beli bertahap saat harga mengalami koreksi teknikal ke area support.
- `MOMENTUM_BUY`: Beli saat terjadi breakout volume tinggi.
- `STRATEGIC_HOLD`: Tahan untuk investasi jangka panjang.
- `HOLD_WATCH`: Pantau konfirmasi prospektus resmi.
- `WAIT_AND_SEE`: Tunggu kejelasan regulasi atau pemenuhan kuota.
- `AVOID`: Suspensi berisiko, delisting, atau wanprestasi.
- `AVOID_HIGH_RISK`: Risiko likuidasi repo / utang macet.

### 4.3 Multi-Horizon Outlook & Invalidation Triggers
Pesan rekomendasi wajib memuat:
- **Horizon Investasi:**
  * Jangka Pendek (1–14 hari): Sentimen sesaat & likuiditas.
  * Jangka Menengah (1–3 bulan): Realisasi aksi korporasi & RUPS.
  * Jangka Panjang (6–12+ bulan): Valuasi fundamental & sinergi grup.
- **Invalidation Trigger:** Kondisi spesifik di mana analisis ini batal/gugur.

---

## 5. Spesifikasi Prefix Endpoint `/api/v1/sectors` & Konfigurasi Multi-Grup WAHA

### 5.1 Konfigurasi Target Grup WAHA (`app/config.py`)
```python
BROADCAST_CHAT_ID: str = Field(description="Target WhatsApp Group ID for IDX Corporate Actions & IDX Sector Alerts")
BROADCAST_CHAT_ID_SP500: str | None = Field(default=None, description="Dedicated WhatsApp Group ID for S&P 500 & Global Sector Intelligence")
```

### 5.2 Daftar Endpoint REST API:

| Method | Endpoint | Deskripsi |
| :--- | :--- | :--- |
| `GET` | `/api/v1/sectors/recommendations` | Mengembalikan rekomendasi sektor AI (Komoditas, S&P 500, IDX). Query: `?category=commodity`, `sp500`, `idx`. |
| `POST` | `/api/v1/sectors/scrape-and-analyze` | Trigger scraping simultan TradingView, Yahoo Finance, CNBC, lalu menjalankan sintesis AI. Mendukung param `?broadcast=true` untuk mem-push alert ke grup masing-masing (IDX ke `BROADCAST_CHAT_ID`, S&P 500 ke `BROADCAST_CHAT_ID_SP500`). |
| `GET` | `/api/v1/sectors/{category}/{sector_name}` | Deep-dive analisis mendalam untuk satu sektor tertentu (misal: `commodity/tin` atau `idx/energy`). |
| `GET` | `/api/v1/sectors/news/realtime` | Feed berita real-time terkonsolidasi dari ketiga sumber yang telah dipetakan ke sektor. |

---

## 6. Format Pesan WhatsApp (100% Dynamic AI-Generated & Dedicated Groups)

### 6.1 Format Alert Aksi Korporasi Emiten (100% Narasi AI — Tanpa Template Detail Statis)
*Target: `BROADCAST_CHAT_ID` (Grup Saham IDX / Indonesia)*
```markdown
🚨 *[IDX-INTEL ALERT] KONGLO MOVE / AKUMULASI STRATEGIS* 🚨
Emiten: $BUMI

PT Bumi Resources Tbk terdeteksi mengalami manuver aksi korporasi strategis dengan keterlibatan aktif Mach Energy (konsorsium Grup Salim bersama Grup Bakrie). Masuknya modal institusi berskala jumbo ini secara fundamental mentransformasi struktur neraca keuangan emiten dengan memangkas beban utang historis dan mengamankan kepemilikan pengendali bersama sebesar 37,1%.

*Analisis Dampak & Strategi:*
Injeksi likuiditas dan masuknya Grup Salim memberikan stabilitas arus kas operasional jangka panjang dan mempercepat diversifikasi ke hilirisasi mineral energi baru. Hal ini menjadi katalis penting re-rating valuasi emiten dari persepsi saham berisiko tinggi menjadi emiten komoditas terintegrasi konglomerasi tier-1.

*🎯 Rekomendasi : [Class: STRONG_BUY_AKUMULASI]*
💡 STRONG_BUY_AKUMULASI — Didukung oleh pergerakan tier-1 konglomerat / prospek ekspansi kuat.

*Horizon Investasi:*
• Jangka Pendek (1-14 hr): Momentum volume transaksi pasar reguler sangat tinggi, waspadai fluktuasi jangka pendek saat menguji area resisten psikologis.
• Jangka Menengah (1-3 bln): Menunggu konfirmasi prospektus resmi RUPSLB dan jadwal penyesuaian hak suara di KSEI.
• Jangka Panjang (6-12+ bln): Struktur modal yang lebih sehat membuka ruang pembagian dividen dan pertumbuhan laba bersih tahunan yang berkelanjutan.

*Batas Pembatalan Analisis (Invalidation Trigger):*
⚠️ Transaksi pengalihan saham gagal diselesaikan di kustodian (KSEI) atau terjadi sengketa restrukturisasi utang baru yang tidak terselesaikan.
⚠️ Harga saham menembus ke bawah batas level support kritis Rp 95 dengan volume jual masif.

*Panduan Aksi:*
💡 Akumulasi bertahap saat harga mengalami koreksi teknikal ke area support, hindari membeli saat lonjakan sesaat di awal pembukaan sesi.

Sumber Berita: https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi
```

### 6.2 Format Alert Intelijen Sektor Indonesia `[IDX-INTEL SECTOR INTELLIGENCE]`
*Target: `BROADCAST_CHAT_ID` (Grup Saham IDX / Indonesia)*
```markdown
🇮🇩 *[IDX-INTEL SECTOR INTELLIGENCE]* 🌐
Tanggal: 16 Oktober 2026 | Sesi: Real-Time Market Update
------------------------------------------------

🔥 SEKTOR UNGGULAN BURSA EFEK INDONESIA:
• Sektor Logam & Bahan Baku (Timah & Nikel) : [Class: OVERWEIGHT] (Skor: +0.78)
  - Analisis AI: Pengetatan kuota ekspor RKAB timah dan lonjakan permintaan nikel kelas baterai memicu potensi ekspansi margin emiten tambang domestik.
  - Top Picks: $TINS, $INCO, $NCKL
• Sektor Energi (Minyak & Batu Bara) : [Class: NEUTRAL] (Skor: +0.25)
  - Analisis AI: Harga minyak Brent bertahan di atas US$100 mengimbangi tren konsolidasi harga batu bara Newcastle di kisaran US$145.
  - Top Picks: $MEDC, $ADRO, $PTBA
• Sektor Keuangan (Big Banks) : [Class: HOLD_WATCH] (Skor: +0.05)
  - Analisis AI: Pasar sedang mencerna dinamika peninjauan status pasar saham oleh MSCI; valuasi perbankan besar tetap atraktif untuk horizon jangka panjang.
  - Top Picks: $BBCA, $BMRI

💡 Rekomendasi Rotasi Sektor:
Alokasikan porsi portofolio secara terukur pada sektor komoditas logam timah ($TINS) dan nikel sebagai hedging portofolio jangka pendek.
```

### 6.3 Format Alert Intelijen Sektor S&P 500 `[S&P500-INTEL AI SECTOR INTELLIGENCE]`
*Target: `BROADCAST_CHAT_ID_SP500` (Grup Khusus S&P 500 & Global)*
```markdown
🇺🇸 *[S&P500-INTEL AI SECTOR INTELLIGENCE]* 🌐
Tanggal: 16 Oktober 2026 | Sesi: Wall Street & Global Market Outlook
------------------------------------------------

⚡ 1. WALL STREET & S&P 500 LEADING SECTORS:
• US Semiconductors & AI Infrastructure : [Class: OVERWEIGHT] (Skor: +0.84)
  - Analisis AI: Permintaan GPU enterprise dan akselerasi infrastruktur server AI melampaui ekspektasi konsensus analis; belanja modal hyperscaler tetap agresif.
  - Top Picks: NVDA, TSM, AMD, AVGO
• Cloud Computing & Cybersecurity : [Class: OVERWEIGHT] (Skor: +0.70)
  - Analisis AI: Ketahanan pengeluaran korporasi terhadap keamanan siber dan adopsi cloud hybrid memberikan visibilitas pendapatan tahunan yang solid.
  - Top Picks: MSFT, CRWD, PANW
• US Mega Financials : [Class: NEUTRAL] (Skor: +0.15)
  - Analisis AI: Margin bunga bersih bank Wall Street stabil, namun provisi kredit konsumen mulai menunjukkan normalisasi.
  - Top Picks: JPM, GS, MS

🌍 2. GLOBAL COMMODITIES & MACRO:
• Logam Mulia (Gold & Silver) : [Class: OVERWEIGHT] (Skor: +0.85)
  - Analisis AI: Pelemahan Indeks Dolar AS (DXY ke 101.8) dan permintaan lindung nilai safe-haven di tengah ketegangan geopolitik mendorong reli emas & perak.
  - Top Picks: XAUUSD, XAGUSD
• Logam Industri (Aluminium & Tembaga) : [Class: ACCUMULATE_ON_WEAKNESS] (Skor: +0.65)
  - Analisis AI: Kebijakan stimulus manufaktur global dan proyek transmisi jaringan energi hijau menopang konsumsi tembaga dan aluminium dunia.
  - Top Picks: LME-Copper, LME-Aluminium

💡 S&P 500 Portfolio Stance:
Pertahankan bobot Overweight pada semikonduktor AI hardware dan aset lindung nilai emas (Gold).
```

---

## 7. Structure Folder & File Layout Proyek

```text
idx_intel_ai/
├── app/
│   ├── main.py                     # Entry point FastAPI & Router Registration
│   ├── config.py                   # Pydantic Settings (BROADCAST_CHAT_ID & BROADCAST_CHAT_ID_SP500)
│   │
│   ├── routers/                    # Layer 1: HTTP API Routers (Controller)
│   │   ├── health.py               # /health
│   │   ├── webhook.py              # /webhook/waha
│   │   ├── monitor.py              # /api/v1/monitor & /events [TETAP UTUH]
│   │   ├── call.py                 # /call/* [TETAP UTUH]
│   │   ├── chat.py                 # /api/v1/chat [TETAP UTUH]
│   │   └── sectors.py              # /api/v1/sectors/* [ROUTER BARU]
│   │
│   ├── services/                   # Layer 2: Business Logic Services
│   │   ├── prompt.py               # Pusat Prompt LLM & WA Formatter (100% Dynamic AI)
│   │   ├── scraper.py              # ScraperCoordinatorService
│   │   ├── agent.py                # AgentExecutionService
│   │   ├── waha.py                 # WAHA Client API
│   │   ├── sector_mapping.py       # [BARU] Pemetaan IDX, S&P 500, Komoditas Lengkap
│   │   └── sector_service.py       # [BARU] SectorIntelligenceService & Multi-WAHA Group Dispatch
│   │
│   ├── agents/                     # AI Orchestration (LangGraph)
│   │   ├── workflow.py             # Konstruksi StateGraph
│   │   ├── state.py                # TypedDict AgentState
│   │   └── nodes/
│   │       ├── ingestion_node.py
│   │       ├── classifier_node.py
│   │       ├── extractor_node.py
│   │       ├── impact_node.py
│   │       ├── recommendation_node.py # [ENHANCED] Memori Historis & Multi-Horizon
│   │       └── wa_formatter_node.py
│   │
│   ├── repositories/               # Layer 3: Database Access (ACID)
│   │   ├── event_repository.py     # get_latest_by_ticker (History fetcher)
│   │   └── ...
│   │
│   ├── scrapers/                   # Data Ingestion (BaseScraper Pattern)
│   │   ├── base_scraper.py
│   │   ├── cnbc_rss_scraper.py
│   │   ├── tradingview_news_scraper.py # [BARU] Real-Time Multi-Market Scraper
│   │   ├── yahoo_finance_scraper.py    # [BARU] Real-Time Global & Commodity Scraper
│   │   └── ...
│   │
│   └── schemas/
│       ├── event_schema.py         # MultiHorizonOutlook & InvestmentThesis
│       └── ...
│
└── tests/
    ├── test_sector_intelligence.py # [BARU] Unit Tests Scrapers & Sector Mapper
    └── test_recommendation_engine.py
```

---

## 8. Panduan Eksekusi Terminal (Code in Terminal)

```bash
# 1. Menjalankan pengujian otomatis:
cd backend
python -m pytest tests/test_sector_intelligence.py -v
python -m pytest tests/test_recommendation_engine.py -v

# 2. Trigger Scraping & Analisis Sektor Real-Time:
curl.exe -X POST "http://localhost:8045/api/v1/sectors/scrape-and-analyze" -H "Content-Type: application/json"

# 3. Mengambil Rekomendasi Sektor (Semua Kategori):
curl.exe -s "http://localhost:8045/api/v1/sectors/recommendations" | jq .

# 4. Mengambil Rekomendasi Sektor Khusus Komoditas (Timah, Aluminium, Emas, dll.):
curl.exe -s "http://localhost:8045/api/v1/sectors/recommendations?category=commodity" | jq .

# 5. Deep-Dive Sektor Tertentu (Contoh: Timah / Tin):
curl.exe -s "http://localhost:8045/api/v1/sectors/commodity/tin" | jq .
```

---

## 9. Kesimpulan

Dokumen PRD v2.2.0 ini menetapkan standar arsitektural yang kokoh untuk **IDX-Intel AI**. Melalui peningkatan mesin rekomendasi berbasis memori historis multi-horizon, narasi pesan yang 100% dinamis buatan AI, penambahan intelijen sektor real-time (IDX, S&P 500, dan Komoditas Strategis Lengkap), serta pemisahan target grup WhatsApp WAHA untuk komunitas IDX dan S&P 500, sistem memberikan keunggulan kompetitif bernilai tinggi bagi pengambilan keputusan investasi.
