# IDX-Intel AI — Enterprise Corporate Action Intelligence Bot

Autonomous AI Agent Backend for IDX Corporate Action Intelligence & WhatsApp Alerting, built with **Python 3.11+**, **FastAPI**, **SQLAlchemy 2.0 (Async)**, **LangGraph (StateGraph)**, **Redis**, and **WAHA (WhatsApp HTTP API)**.

## Architectural Highlights
- **Strict 3-Category Classification**:
  - `BACKDOOR_LISTING`: Injeksi aset baru, perubahan kegiatan usaha drastis, reverse takeover.
  - `KONGLO_MOVE`: Akumulasi oleh Top 200 Konglomerat (Salim, Barito/Prajogo Pangestu, Bakrie, Djarum, Agung Sedayu, Panin, Chandra Asri, dll.), crossing pasar negosiasi jumbo, akuisisi PSP > 5%.
  - `IRRELEVANT`: Berita rutin tanpa pembeli konglo (dividen biasa, laporan keuangan, UMA biasa). *(Aturan Ketat: tidak memuat kriteria di atas = IRRELEVANT)*.
- **Top 200 Konglomerat Recommendation Engine**:
  - `STRONG_BUY_AKUMULASI`: Wajib apabila Top 200 Konglomerat / tokoh besar terdeteksi dalam corporate action strategis.
  - `BUY`: Aksi korporasi positif oleh investor institusi umum.
  - `HOLD_WATCH` / `AVOID`.
- **Deduplication Strategy**:
  - SHA-256 deterministic hash (`ticker + event_type + publication_date + title`) saved in PostgreSQL ACID transaction.
- **Interactive WhatsApp Commands**:
  - `/cek <TICKER>`: Cek laporan aksi korporasi terakhir emiten.
  - `/summary`: Ringkasan 5 aksi korporasi strategis terbaru.
  - `/subscribe <TICKER>` / `/unsubscribe <TICKER>`.
  - Equipped with **Rate Limiter (Throttling)** & **Redis Cache (5–10 min TTL)**.

## Getting Started

### 1. Installation
```bash
pip install -e .
```

### 2. Run Database Migrations
```bash
alembic upgrade head
```

### 3. Run FastAPI Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 4. Run Automated Unit Tests
```bash
pytest tests/ -v
```
