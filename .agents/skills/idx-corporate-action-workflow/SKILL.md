---
name: idx-corporate-action-workflow
description: Panduan pengembangan dan pemeliharaan pipeline scraper bursa, orkestrasi LangGraph StateGraph, dan pengiriman notifikasi WAHA pada IDX-Intel AI
---

# IDX-Intel Corporate Action Intelligence Workflow

Skill ini memandu alur kerja teknis multi-step untuk pengembangan modul-modul dalam IDX-Intel AI:

## 1. Web Scraping & Ingestion Workflow
- Seluruh scraper mewarisi kelas abstrak `BaseScraper`.
- Mendukung 6 sumber data:
  1. BEI / IDX Announcements (HTTP GET / JSON API)
  2. Google News RSS Engine (Aggregator berita finansial tanpa auth/CAPTCHA)
  3. CNBC Indonesia Market RSS
  4. Kontan Investasi RSS
  5. IDN Financials Corporate Action (HTML Table Parser)
  6. IPOTNews Feed
- Standarisasi output scraper ke DTO raw ingestion sebelum masuk ke LangGraph.

## 2. LangGraph StateGraph Execution Pipeline
1. **IngestionNode:** Pembersihan teks (HTML/PDF), ekstraksi metadata, URL, tanggal, ticker.
2. **ClassifierNode:** Validasi ketat 3 kategori (`BACKDOOR_LISTING`, `KONGLO_MOVE`, `IRRELEVANT`). Jika `IRRELEVANT`, langsung rute ke `END`.
3. **ExtractorNode:** Ekstraksi JSON terstruktur via Pydantic model (`rasio`, `harga_pelaksanaan`, `cum_date`, `ex_date`, dll.).
4. **ImpactNode:** Evaluasi sentimen finansial (Bullish/Bearish/Neutral) dan kalkulasi rekomendasi (`STRONG_BUY_AKUMULASI`, dll.).
5. **WAFormatterNode:** Format output WhatsApp markdown dengan emoji, layout rapi, bullet points, dan headline `🎯 Rekomendasi : [Class: ...]`.

## 3. WAHA Integration & Command Handling
- **Outbound Alert:** Pengiriman pesan via `httpx.AsyncClient` ke endpoint WAHA dengan retry backoff.
- **Inbound Commands:**
  - `/cek <TICKER>`: Ambil max 3 corporate events terbaru dari PostgreSQL + kesimpulan AI. Cache Redis 5-10 menit.
  - `/summary`: Ringkasan 24 jam terakhir aksi korporasi BEI. Cache Redis 5-10 menit.
  - `/subscribe <TICKER>` & `/unsubscribe <TICKER>`: Kelola data langganan di PostgreSQL.
  - `/help`: Daftar panduan interaktif.
- **Rate Limiting:** Proteksi command handler dari spamming/throttling.
