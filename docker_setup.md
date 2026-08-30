# Panduan Setup Docker & Eksekusi IDX-Intel AI

Berikut adalah panduan langkah demi langkah untuk menjalankan [docker-compose.yml](file:///c:/Users/dewam/Dokumen/Project%20AI%20and%20Website/Ternak%20AI/Invest-Automation/docker-compose.yml), menerapkan migrasi database (Alembic), menjalankan server backend **IDX-Intel AI**, dan menghubungkan WhatsApp melalui WAHA.

---

## Prasyarat (.env)
- Anda **tidak wajib** mengisi `.env` untuk menjalankan container Docker karena kredensial sudah diatur mandiri di [docker-compose.yml](file:///c:/Users/dewam/Dokumen/Project%20AI%20and%20Website/Ternak%20AI/Invest-Automation/docker-compose.yml).
- File [.env](file:///c:/Users/dewam/Dokumen/Project%20AI%20and%20Website/Ternak%20AI/Invest-Automation/.env) baru dibutuhkan saat menjalankan migrasi dan server FastAPI. Kredensial default untuk database dan Redis sudah disesuaikan (`password123.`).
- Anda hanya perlu mengisi `OPENAI_API_KEY=sk-xxx` di dalam `.env` apabila ingin menggunakan analisis LLM aktif (jika kosong, sistem tetap berjalan menggunakan *rule-based fallback*).

---

## Step 1: Jalankan Seluruh Ekosistem (PostgreSQL, Redis, WAHA, dan FastAPI Backend)

Buka terminal di folder project (`Invest-Automation`) dan jalankan perintah Docker Compose dengan flag `--build`:

```powershell
docker compose up -d --build
```

> [!NOTE]
> - **Satu Perintah untuk Semua (Zero-Setup Deployment)**: Seluruh layanan kini berjalan dalam Docker!
> - **PostgreSQL 16 (`idx_intel_postgres`)**: Berjalan di port `5432`.
> - **Redis 7 (`idx_intel_redis`)**: Berjalan di port `6379`.
> - **WAHA WhatsApp API (`idx_intel_waha`)**: Berjalan di port `3002`.
> - **FastAPI Backend (`idx_intel_backend`)**: Berjalan di port `8002` (di-map ke port internal 8002 agar tidak bertabrakan dengan server lokal lain di port 8000/8001). Kontainer ini **otomatis menjalankan migrasi database (`alembic upgrade head`)** sebelum meluncurkan server Uvicorn.

Untuk mengecek apakah keempat container sudah berstatus **healthy / running**:
```powershell
docker compose ps
```

Setelah semua kontainer aktif, Anda dapat langsung membuka di browser:
- **🇮🇩 Demo Dashboard "Merah Putih"**: http://localhost:8002/demo
- **API Swagger Documentation**: http://localhost:8002/docs
- **Health Check Endpoint**: http://localhost:8002/health
- **WAHA Dashboard (Port 3002)**: http://localhost:3002/dashboard

---

## Step 2: Hubungkan Nomor WhatsApp ke WAHA

1. Buka browser dan akses **WAHA Dashboard**: http://localhost:3002/dashboard
2. Pada session `default`, klik tombol **START / QR CODE**.
3. Scan **QR Code** menggunakan aplikasi WhatsApp di HP Anda (**WhatsApp > Perangkat Tertaut > Tautkan Perangkat**).
4. Setelah berstatus **CONNECTED / WORKING**, sistem siap menerima dan mengirim notifikasi aksi korporasi dan perintah interaktif (`/cek <TICKER>`, `/summary`, `/subscribe <TICKER>`).

---

## Step 3: (Opsional) Trigger Scraping & Analisis AI Secara Manual

Untuk menguji pengumpulan berita secara instan tanpa menunggu scheduler:
- Buka http://localhost:8002/docs
- Cari endpoint **`POST /api/v1/monitor`** lalu klik **Try it out > Execute**, atau jalankan lewat terminal:

```powershell
curl -X POST "http://localhost:8002/api/v1/monitor"
```

---

## Cara Menghentikan Container

Jika sudah selesai dan ingin mematikan container:
```powershell
docker compose down
```

*(Gunakan `docker compose down -v` apabila ingin menghapus data volume database sekaligus).*
