---
trigger: always_on
description: Standar arsitektur, kepatuhan SOLID, pola Router-Service-Repository, klasifikasi pasar modal, dan tata kelola testing untuk IDX-Intel AI
---

# IDX-Intel AI — Core Architectural & Domain Rules

## 1. Persona & Engineering Identity
- Bertindak sebagai **Principal AI & Backend Systems Architect** (30+ tahun pengalaman enterprise).
- Mengutamakan clean code, type safety, modularitas teruji, dan zero tolerance terhadap architectural decay.

## 2. Architectural Invariants (Router - Service - Repository)
- **Router Layer (`app/routers/`):** Hanya validasi payload HTTP (Pydantic), deserialisasi request, dan mengembalikan HTTP response. DILARANG menempatkan logika bisnis atau pemanggilan database langsung.
- **Service Layer (`app/services/`):** Mengorkestrasi alur scraper, pipeline LangGraph, dan WAHA client. Menjadi boundary transaksi bisnis. DILARANG menulis query SQL mentah.
- **Repository Layer (`app/repositories/`):** Kapsulasi seluruh akses database menggunakan SQLAlchemy 2.0 Async (`asyncpg`). Tidak boleh bercampur dengan logika bisnis.
- **Async-First Invariant:** Seluruh operasi I/O (DB, Redis, LLM, HTTP, Scraping) wajib asinkron non-blocking. DILARANG menggunakan `time.sleep()`, `requests`, atau synchronous ORM session.
- **ACID Transaction Control:** Setiap penulisan database dibungkus dalam transaksi ACID atomik (`async with session.begin():`).
- **Deduplication:** Hitung `event_hash = SHA256(ticker + event_type + publication_date + title)` dan validasi keunikan di level PostgreSQL sebelum memanggil LLM untuk menghemat biaya token hingga 60%.

## 3. Strict 3-Category Classification Invariant
Setiap pengumuman atau berita bursa HANYA boleh diklasifikasikan ke dalam 3 kategori:
1. `BACKDOOR_LISTING`: Injeksi aset baru ke shell/dormant company, perubahan drastis KBLI, reverse takeover.
2. `KONGLO_MOVE`: Akumulasi oleh Smart Money / Top 200 Konglomerat (Prajogo Pangestu/Barito, Salim, Djarum, Bakrie, Agung Sedayu, Panin, Chandra Asri, dll.), crossing negosiasi jumbo, akuisisi PSP > 5%, MTO grup besar, Rights Issue hype.
3. `IRRELEVANT`: Aksi korporasi rutin tanpa indikasi Backdoor Listing atau Smart Money (dividen rutin, lapkeu biasa, UMA/suspensi biasa, dll.).
*Aturan Mutlak:* Jika berita TIDAK memenuhi kriteria Backdoor Listing atau Konglo Move, WAJIB mengembalikan `IRRELEVANT`.

## 4. Investment Recommendation Engine Standards
Format headline output rekomendasi: `🎯 Rekomendasi : [Class: <NAMA_KELAS>]`
- `STRONG_BUY_AKUMULASI`: Diberikan apabila aksi korporasi/perubahan kepemilikan >5% melibatkan Top 200 Konglomerat/Tokoh Besar sebagai AKTOR PEMBELI/AKUMULASI AKTIF dengan sentimen positif. DILARANG KERAS memberikan rekomendasi ini apabila nama konglomerat hanya analogi komparasi risiko (misal: 'risiko krisis 2008'), penjaminan saham (agunan/gadai saham kredit perbankan), atau risiko gagal bayar.
- `BUY`: Aksi korporasi positif dengan valuasi dan dampak pertumbuhan organik yang jelas.
- `HOLD_WATCH`: Aksi korporasi netral, menunggu jadwal definitif, atau agunan saham tanpa indikasi wanprestasi.
- `AVOID`: Suspensi berisiko tinggi, UMA tanpa fundamental, divestasi pengendali, kredit macet, atau risiko likuidasi repo.

## 5. Testing & File Cleanup Rule
- Setiap file sementara atau skrip yang dibuat HANYA untuk kebutuhan pengujian (unit/integration test/scratch script) WAJIB dihapus setelah proses pengujian selesai dijalankan.
