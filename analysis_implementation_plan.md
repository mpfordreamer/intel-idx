# Expert System Analysis & Implementation Plan
**Project:** IDX-Intel AI (Corporate Action & IHSG Market Monitor)
**Role:** Senior Backend & AI Engineer
**Date:** August 2026

## 1. System Rating & Evaluation
**Overall System Rating: 85 / 100 (Sangat Baik / Enterprise-Grade Foundation)**

Berdasarkan audit arsitektur *Backend* dan sinkronisasinya dengan *Frontend*, sistem ini sudah memiliki fondasi yang sangat kuat dan *modern*. Anda telah menerapkan pola yang luar biasa.

### 🌟 Strengths (Kekuatan Utama - Mengapa sistem ini mendapat nilai 85):
1. **LangGraph State-Machine AI:** Penggunaan LangGraph untuk memecah proses AI menjadi *pipeline* yang terisolasi (*Ingestion -> Classifier -> Extractor -> Impact -> Formatter*) adalah strategi paling brilian untuk mencegah halusinasi *zero-shot prompt* pada LLM lokal.
2. **SOLID & Clean Architecture:** Struktur direktori (`routers`, `services`, `repositories`, `agents`) dipisahkan secara sempurna. FastAPI tidak memiliki *business logic* di *route*, semuanya di-didelegasikan ke *Service Layer*.
3. **Async I/O First:** Penggunaan `asyncpg` dengan SQLAlchemy 2.0 dan `httpx` memastikan sistem ini *non-blocking* dan sangat efisien dalam penggunaan memori/CPU saat melakukan *scraping* multipel.
4. **API-Frontend Alignment:** Kontrak API (*JSON response shape*) dari `/api/v1/monitor` dan `/api/v1/events` sudah **100% *MATCH*** dengan properti yang diharapkan oleh `demo.html` (`ticker`, `category`, `impact_analysis`, `recommendation`, dll).

### 🚧 Weaknesses (Area of Improvements - Perjalanan menuju 95+):
1. **Tidak Ada Sinkronisasi Real-Time (WebSockets / SSE):** 
   Saat ini *Background Scheduler* (Cron) berjalan otomatis setiap 5 menit. Namun, **Frontend tidak akan tahu** jika ada berita baru kecuali user melakukan *refresh* atau klik *Trigger AI Pipeline*.
2. **Server-Side Filtering & Pagination:**
   Endpoint `/events` masih menggunakan `limit(50)` *hardcoded* dan filter dilakukan di *Client-Side* (JavaScript). Seharusnya filter (`?category=KONGLO_MOVE`) dilakukan di level SQL (Server-Side) untuk performa data besar.
3. **Validasi & Fallback LLM Lokal:**
   LLM lokal (Qwen 14B) berpotensi sesekali gagal menghasilkan JSON yang valid pada `ExtractorNode`. Belum ada mekanisme *Retry* atau *Self-Correction* otomatis pada *graph*.
4. **Redis Caching Belum Diimplementasikan Penuh:**
   Di PRD disebutkan ada Redis, tetapi endpoint `/events` masih menembak langsung ke PostgreSQL secara *direct*.

---

## 2. Implementation Plan (Rekomendasi Peningkatan Sistem)

Sebagai *Engineer*, ini adalah saran *upgrade* teknis (*Best Advice*) yang saya ajukan untuk Anda agar aplikasi ini naik ke level *Production-Perfect*:

### Phase 1: Real-Time Frontend Sync (Server-Sent Events / WebSockets)
Untuk memastikan *Frontend* selalu sinkron secara *live* dengan *Scheduler Backend*:
1. **[NEW] `app/routers/stream.py`**: Buat endpoint WebSocket atau Server-Sent Events (SSE) `GET /api/v1/stream`.
2. **[MODIFY] `app/services/agent.py`**: Setelah *pipeline* selesai dan data disimpan, *publish event* ke *Channel* SSE.
3. **[MODIFY] `demo.html`**: Tambahkan `EventSource` di JS untuk mendengarkan *event* baru secara *live* dan langsung *render* ke layar tanpa *refresh*.

### Phase 2: Server-Side Filtering & Pagination pada API
1. **[MODIFY] `app/routers/monitor.py`**: 
   Ubah endpoint `/events` agar menerima *Query Parameters*:
   ```python
   async def get_recent_events(limit: int = 50, category: str = None, ticker: str = None):
       # Modifikasi SQLAlchemy statement dengan Where conditions
   ```
2. **[MODIFY] `demo.html`**:
   Fungsi `filterCards(category)` akan menembak API ulang dengan parameter `?category=...` alih-alih menyembunyikan *div* HTML (*display: none*).

### Phase 3: LangGraph Retry Mechanism & Resilience
1. **[MODIFY] `app/agents/nodes/extractor_node.py`**:
   Bungkus pemanggilan `with_structured_output` dengan fitur `with_fallbacks` atau blok `try-except` di mana node akan me-rutekan kembali (*loop back*) ke dirinya sendiri maksimal 2 kali jika terjadi *ValidationError* dari Pydantic.

### Phase 4: Integrasi Redis Caching API
1. **[MODIFY] `app/routers/monitor.py`**:
   Simpan hasil query `events` di Redis dengan `TTL 5 menit`. Jika ada *Request* masuk ke `/events`, baca dari Redis. *Cache* akan di-invalidasi/dihapus setiap kali ada event baru masuk dari `AgentExecutionService`.

---

## Kesimpulan & Permintaan Persetujuan
Desain integrasi *Frontend* dan *Backend* Anda saat ini **sudah tersinkronisasi dengan sangat baik secara struktur data**. Kode HTML JavaScript di `demo.html` dan Python di `monitor.py` sudah berbicara bahasa *JSON* yang sama.

Jika Anda ingin melanjutkan implementasi dari analisis di atas, **saya menyarankan kita memulai dari Phase 1 (WebSockets/SSE)** agar UI di *demo.html* bisa otomatis berkedip/muncul berita baru saat *cron scheduler* mendeteksi pengumuman BEI di latar belakang.

Apakah Anda setuju dengan hasil audit ini? Jika ya, fitur apa yang ingin kita implementasikan terlebih dahulu? Silakan klik **Proceed** dan beri arahan!
