# Skema Database PostgreSQL (Ternak AI / Invest Automation)

Sistem IDX-Intel AI menggunakan **PostgreSQL** sebagai penyimpanan data relasional utama, yang dikelola secara asinkron menggunakan *SQLAlchemy 2.0 (asyncpg)*. Saat ini terdapat 4 buah tabel utama yang menyusun *database*:

## 1. Tabel `corporate_events`
**Tujuan:** Menyimpan seluruh berita, pengumuman BEI, dan hasil pemrosesan AI (LangGraph) agar dapat digunakan kembali (di-*cache*) dan mencegah agar bot AI tidak memproses ulang berita yang sama berulang kali.

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Auto-increment ID. |
| `event_hash` | String(64) | Kunci deduplikasi (SHA-256) gabungan antara *ticker*, tipe, tanggal, dan judul. |
| `ticker` | String(10) | Kode saham (contoh: BBCA, BUMI). |
| `event_type` | String(50) | Hasil klasifikasi AI: `BACKDOOR_LISTING`, `KONGLO_MOVE`, `Laporan Keuangan / Fundamental`, atau `IRRELEVANT`. |
| `title` | String(500) | Judul berita asli dari *scraper*. |
| `source_url` | String | Tautan menuju sumber berita asli. |
| `publication_date` | DateTime | Waktu publikasi berita (Timezone Aware). |
| `raw_text` | Text | Teks asli berita sebelum diringkas oleh AI. |
| `extracted_json` | JSONB | Data kuantitatif terstruktur (rasio saham, tanggal *ex-date*, dll) hasil dari *Extractor Node*. |
| `impact_analysis` | Text | Analisa sentimen dari LLM (Bullish / Bearish / Neutral). |
| `recommendation_class` | String(50) | Rekomendasi LLM (STRONG_BUY_AKUMULASI, BUY, dll). |
| `wa_formatted_message`| Text | Teks pesan final yang sudah dipercantik dengan emoji (siap dikirim ke WhatsApp). |

---

## 2. Tabel `users`
**Tujuan:** Menyimpan data pendaftaran akun WhatsApp yang pernah berinteraksi dengan sistem ini atau berlangganan notifikasi.

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Auto-increment ID pengguna. |
| `phone_number` | String(25) | ID WhatsApp pengguna. Jika ini adalah *Personal Chat*, formatnya adalah nomor HP (`62812...`). Jika *Grup*, formatnya menyimpan ID grup (`123456-123456@g.us`). |
| `is_active` | Boolean | Status apakah pengguna aktif atau diblokir. |
| `is_admin` | Boolean | Penanda apakah pengguna memiliki hak admin. |

---

## 3. Tabel `user_subscriptions`
**Tujuan:** Menyimpan preferensi langganan (fitur `/subscribe`) masing-masing *user* terhadap kode saham tertentu agar sistem *Push Notification* mengetahui siapa yang harus dikirimi pesan ketika ada berita baru.

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Auto-increment ID langganan. |
| `user_id` | Integer (FK) | Merujuk pada tabel `users.id` dengan relasi penghapusan kaskade (*CASCADE*). |
| `ticker` | String(10) | Kode saham langganan pengguna (contoh: BBCA). |
| `is_active` | Boolean | Status apakah *subscribe* ini masih aktif atau sudah di-*unsubscribe*. |

---

## 4. Tabel `alert_logs`
**Tujuan:** Mencatat log (buku kas) mengenai pengiriman pesan WhatsApp secara *outbound*. Tabel ini krusial untuk pelacakan error jika pesan WAHA gagal terkirim.

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Auto-increment ID log. |
| `event_id` | Integer (FK) | Merujuk pada berita/pengumuman `corporate_events.id`. |
| `phone_number` | String(25) | Nomor WhatsApp tujuan pesan. |
| `message_content` | Text | Isi pesan yang dikirimkan. |
| `status` | String(20) | Status pengiriman via WAHA (`PENDING`, `SENT`, atau `FAILED`). |
| `retry_count` | Integer | Berapa kali pengiriman ini diulangi jika sempat gagal. |
| `error_message` | Text | Menyimpan respon *error* HTTP dari WAHA jika gagal (`status=FAILED`). |
