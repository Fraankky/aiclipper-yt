# PRD — AI Campaign Clip Workflow

**Versi:** 2.0.0 | **Tanggal:** 27 Maret 2026 | **Status:** Revised Draft | **Target User:** Operator Campaign, Editor, dan Tim Eksekusi Influencer

> Tool lokal berbasis AI untuk membantu workflow clipping video influencer/sumber yang sudah disetujui menjadi beberapa kandidat klip campaign pendek yang siap direview, disetujui, dan dieksekusi — dengan user tetap memegang keputusan akhir.

---

## 1. Executive Summary

|                                      |                                                                                                                                                                  |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Masalah**                          | Workflow campaign clipping dari video influencer/sumber yang sudah approved masih lambat, manual, dan sulit distandardisasi antar campaign                       |
| **Solusi**                           | Pipeline semi-otomatis: ingest video approved → transkripsi → suggestion kandidat segmen → bantuan hook/metadata → review manusia → cut/reframe/caption → export |
| **Use Case Utama**                   | Eksekusi campaign influencer yang membutuhkan banyak kandidat short clip dari asset video yang sudah diizinkan untuk repurpose                                   |
| **Nilai Produk**                     | Mempercepat produksi tanpa menghilangkan kontrol user; fleksibel untuk berbagai brief, platform, dan target campaign                                             |
| **Monetisasi yang Diasumsikan User** | Nilai bisnis campaign dapat terkait performa hasil distribusi, mis. payout terjadi jika klip influencer mencapai target seperti 1 juta views                     |
| **Batasan Penting**                  | Produk ini adalah tool produksi fleksibel, bukan mesin uang otomatis, bukan pemberi jaminan viral, dan bukan pengganti judgement tim campaign                    |
| **Biaya Estimasi**                   | ~Rp 75–300/source video untuk analisis AI teks; pemrosesan lain berjalan lokal di PC sendiri                                                                     |

---

## 2. Latar Belakang

### 2.1 Konteks Produk

Dalam workflow campaign influencer, tim sering menerima video source yang sudah disetujui atau sudah memiliki izin pemakaian ulang untuk kebutuhan eksekusi campaign. Dari satu asset video, tim perlu menghasilkan beberapa kandidat klip pendek dengan angle berbeda untuk diuji atau dipublikasikan ke Shorts, TikTok, dan Reels.

Masalah utamanya bukan sekadar “memotong video panjang”, tetapi:

- menemukan bagian yang paling relevan dengan objective campaign,
- menyusun hook yang kuat tanpa keluar dari konteks,
- menjaga konsistensi metadata campaign,
- memastikan setiap output melalui review manusia sebelum dianggap final.

Di banyak situasi, keberhasilan campaign bisa berhubungan langsung dengan performa distribusi, misalnya payout berdasarkan tercapainya target views tertentu. Karena itu, tim membutuhkan tool yang mempercepat produksi dan membantu pengambilan keputusan, tetapi tetap realistis: performa akhir ditentukan oleh banyak faktor di luar clipping semata.

### 2.2 Perbandingan Kompetitor

| Produk                        | Model                   | Kelebihan                                                          | Kelemahan untuk Workflow Campaign                              |
| ----------------------------- | ----------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------- |
| Opus Clip                     | Cloud SaaS              | Cepat, polished                                                    | Fokus umum ke auto clipping, review campaign metadata terbatas |
| Vidyo.ai                      | Cloud SaaS              | Mudah dipakai                                                      | Kurang menekankan approval workflow dan fleksibilitas brief    |
| Tool editing umum             | Manual / semi-manual    | Kontrol tinggi                                                     | Lambat untuk volume campaign dan candidate generation          |
| **AI Campaign Clip Workflow** | **Lokal / PC + AI API** | **Fleksibel, biaya rendah, user tetap in control, approval-aware** | **Butuh setup sendiri, bukan one-click viral tool**            |

---

## 3. Goals & Non-Goals

### Goals ✅

- Mempercepat workflow clipping dari video influencer/sumber yang sudah approved atau diizinkan untuk repurpose
- Menghasilkan beberapa **kandidat segmen** berdasarkan transkrip, konteks campaign, dan objective konten
- Memberikan **bantuan hook, judul, CTA, dan metadata** untuk tiap kandidat klip
- Menambahkan **human-in-the-loop review dan approval** sebelum output dianggap final
- Menyimpan **campaign metadata** dan status approval per candidate clip
- Tetap fleksibel untuk berbagai campaign, platform, angle, dan brief
- Menyediakan preview, export, dan jejak status yang jelas
- Menjaga biaya operasional tetap rendah dengan pemrosesan lokal sebanyak mungkin

### Non-Goals ❌

- Tidak menjanjikan bahwa klip akan viral
- Tidak menjanjikan payout campaign atau view threshold tercapai
- Tidak menjadi “AI money machine” atau mesin otomatis penghasil pendapatan
- Tidak mengambil keputusan final tanpa review user
- Tidak ditujukan sebagai workflow utama untuk konten brand-owned production dari nol
- Tidak menggantikan legal review, hak cipta, atau persetujuan talent
- Tidak memproses konten yang tidak dimiliki user atau tidak memiliki otorisasi penggunaan ulang
- Tidak menjadi sistem manajemen influencer end-to-end (briefing, kontrak, pembayaran, publishing) pada Phase 1

---

## 4. User Persona

**Rina — Campaign Content Operator**

- Usia 28 tahun | Jakarta | Windows PC, RAM 16GB
- Bekerja untuk agency kecil, studio performance content, atau tim eksekusi campaign
- Sering menerima video dari influencer, talent, atau source lain yang sudah approved untuk kebutuhan repurpose
- Harus menghasilkan beberapa kandidat short clip cepat untuk testing distribusi
- Pain point:
  - review footage dan menentukan potongan butuh waktu lama,
  - sulit menjaga konsistensi metadata campaign,
  - terlalu banyak trial-and-error manual untuk hook dan angle,
  - butuh approval internal sebelum export final
- Ekspektasi:
  - tool yang mempercepat seleksi candidate clip,
  - tetap bisa review, tolak, revisi, atau approve,
  - fleksibel untuk campaign yang berbeda-beda,
  - tidak memaksa workflow serba otomatis

---

## 5. Spesifikasi Fitur

### 5.1 Tabel Fitur

| Fitur                           | Deskripsi                                                                                       | Priority | Phase |
| ------------------------------- | ----------------------------------------------------------------------------------------------- | -------- | ----- |
| Input Source Video              | Upload file lokal atau URL sumber yang memang diizinkan                                         | P0       | 1     |
| Campaign Metadata Form          | Input campaign name, brand/client, influencer/source, platform target, KPI, due date, notes     | P0       | 1     |
| Rights Confirmation             | User wajib konfirmasi bahwa asset dimiliki atau diizinkan untuk diproses/repurpose              | P0       | 1     |
| Download / Ingest Asset         | Ambil dan simpan source video ke workspace                                                      | P0       | 1     |
| Transkripsi Audio               | Whisper untuk transkripsi Bahasa Indonesia + English dengan timestamp                           | P0       | 1     |
| AI Candidate Segment Suggestion | OpenRouter menganalisis transkrip + brief untuk memberi kandidat segmen, alasan, dan confidence | P0       | 1     |
| Hook Assistance                 | Saran hook pembuka, judul pendek, CTA, dan angle per kandidat clip                              | P0       | 1     |
| Review Queue                    | Daftar candidate clip dengan preview, alasan, metadata, dan status approval                     | P0       | 1     |
| Approval State Tracking         | Status seperti `suggested`, `needs_review`, `approved`, `rejected`, `exported`                  | P0       | 1     |
| Auto-Cut Video                  | ffmpeg memotong video sesuai timestamp kandidat yang dipilih                                    | P0       | 1     |
| Preview Klip                    | HTML5 player inline sebelum approval/export                                                     | P0       | 1     |
| Download / Export Klip          | Export satu klip atau beberapa klip yang sudah approved                                         | P0       | 1     |
| Caption Burn-in                 | Burn subtitle otomatis ke klip final                                                            | P1       | 1     |
| Output Size Selector            | 9:16, 1:1, 4:5, original, atau custom                                                           | P1       | 2     |
| Reframe + Face Tracking         | Auto-crop berbasis wajah untuk format vertikal                                                  | P1       | 2     |
| Metadata Editing                | User bisa revisi title, hook, CTA, hashtag, tags, dan notes per klip                            | P1       | 2     |
| Manual Trim Adjustment          | Geser start/end beberapa detik sebelum approve final                                            | P1       | 2     |
| Riwayat Campaign / Asset        | Simpan history per campaign, source asset, dan clip output                                      | P2       | 2     |
| Model Selection                 | Pilih model OpenRouter sesuai budget dan kebutuhan                                              | P2       | 2     |
| Prompt / Brief Template         | Template untuk campaign awareness, conversion, UGC, testimonial, dsb                            | P2       | 2     |
| Batch Processing                | Beberapa source video dalam satu campaign                                                       | P3       | 3     |
| Approval Notes / Audit Trail    | Catatan reviewer dan alasan approve/reject                                                      | P3       | 3     |

### 5.2 Campaign Metadata yang Disimpan

Setiap job/asset minimal menyimpan metadata berikut:

| Field                   | Contoh                                                    | Wajib |
| ----------------------- | --------------------------------------------------------- | ----- |
| `campaign_id`           | `cmp-2026-041`                                            | Ya    |
| `campaign_name`         | `Ramadan Push 2026`                                       | Ya    |
| `client_or_brand`       | `Brand X`                                                 | Ya    |
| `influencer_name`       | `Nadia A.`                                                | Tidak |
| `source_asset_id`       | `asset-07`                                                | Ya    |
| `source_type`           | `upload` / `approved_url`                                 | Ya    |
| `target_platform`       | `TikTok`, `Reels`, `Shorts`                               | Ya    |
| `campaign_goal`         | `reach`, `engagement`, `traffic`, `awareness`             | Ya    |
| `target_view_threshold` | `1000000`                                                 | Tidak |
| `payout_context`        | `bonus jika >1M views`                                    | Tidak |
| `rights_basis`          | `owned`, `licensed`, `client-approved`, `talent-approved` | Ya    |
| `due_date`              | `2026-04-10`                                              | Tidak |
| `notes`                 | catatan brief / mandatory talking point                   | Tidak |

### 5.3 Approval States

Workflow approval per candidate clip:

| State          | Arti                                                        |
| -------------- | ----------------------------------------------------------- |
| `suggested`    | Kandidat baru dihasilkan AI, belum dicek user               |
| `needs_review` | Kandidat perlu dilihat ulang atau diedit metadata/timestamp |
| `approved`     | Kandidat disetujui user untuk diexport                      |
| `rejected`     | Kandidat ditolak dan tidak akan dipakai                     |
| `exported`     | Klip final sudah diexport                                   |

### 5.4 Detail Fitur Review & Human-in-the-Loop

Sistem tidak boleh menganggap output AI sebagai final. Alur minimum:

- AI menghasilkan kandidat segmen dan metadata awal
- User melihat preview, alasan pemilihan, dan hook suggestion
- User dapat:
  - approve,
  - reject,
  - mengubah hook/title/CTA,
  - menyesuaikan timestamp ringan,
  - memilih format output
- Hanya kandidat berstatus `approved` yang dapat diexport sebagai final

### 5.5 Detail Fitur Output Size & Reframe

Reframe tetap fleksibel dan bukan kewajiban untuk semua campaign.

**Mode Output yang Tersedia:**

| Mode          | Rasio | Target Umum                              |
| ------------- | ----- | ---------------------------------------- |
| Portrait Full | 9:16  | TikTok, Shorts, Reels                    |
| Square        | 1:1   | Feed / paid placements tertentu          |
| Portrait Soft | 4:5   | Instagram portrait feed                  |
| No Reframe    | Asli  | Review internal atau penggunaan lanjutan |
| Custom        | Bebas | Kebutuhan campaign spesifik              |

**Perilaku Reframe & Background:**

- Wajah terdeteksi → crop difokuskan ke wajah dominan
- Wajah tidak terdeteksi → fallback ke center-crop
- Area kosong dapat diisi background hitam
- User tetap dapat memilih mode `original` bila crop tidak sesuai kebutuhan campaign

---

## 6. Arsitektur Teknis

### 6.1 Tech Stack

| Layer             | Technology                 | Fungsi                                                |
| ----------------- | -------------------------- | ----------------------------------------------------- |
| Backend Framework | **FastAPI** (Python)       | REST API, SSE, orchestration job                      |
| Source Ingest     | **Upload lokal / yt-dlp**  | Ambil asset dari file lokal atau URL yang diizinkan   |
| Video Processing  | **ffmpeg**                 | Cut, reframe, subtitle burn-in, export                |
| Speech-to-Text    | **OpenAI Whisper** (lokal) | Transkripsi + timestamp                               |
| AI Assistance     | **OpenRouter API**         | Kandidat segmen, hook assistance, metadata suggestion |
| Face Detection    | **MediaPipe** (lokal)      | Smart crop untuk Phase 2                              |
| Frontend          | **HTML + Vanilla JS**      | UI lokal sederhana untuk operator                     |
| Task Processing   | **asyncio + threading**    | Background processing tanpa block UI                  |
| Storage           | **Local filesystem**       | Workspace, transcript, candidate data, output klip    |

### 6.2 Mengapa OpenRouter?

OpenRouter tetap relevan karena kebutuhan produk ini bukan satu model tunggal, tetapi kemampuan memilih model yang sesuai biaya, kecepatan, dan kualitas analisis teks campaign.

Keuntungan:

- tidak terikat ke satu provider,
- bisa menyesuaikan model dengan kompleksitas brief,
- kompatibel dengan format OpenAI SDK,
- cocok untuk candidate suggestion dan metadata assistance,
- mudah diberi fallback model bila salah satu provider lambat.

**Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
**Default Model Phase 1:** `anthropic/claude-3.5-haiku`

### 6.3 Alur Data (Pipeline)

1. User membuat campaign atau memilih campaign aktif
2. User mengisi metadata campaign dan konfirmasi hak penggunaan asset
3. User upload video lokal atau memasukkan URL source yang approved
4. Sistem ingest/download asset ke workspace
5. Audio diekstrak dan ditranskripsi dengan Whisper
6. Transkrip + campaign brief dikirim ke OpenRouter untuk menghasilkan:
   - kandidat segmen,
   - alasan segment selection,
   - saran hook,
   - judul pendek,
   - CTA / metadata awal
7. Sistem membuat preview candidate clip
8. User melakukan review:
   - approve,
   - reject,
   - edit metadata,
   - koreksi timestamp ringan,
   - pilih output size
9. Sistem export hanya candidate yang approved
10. Output akhir disimpan beserta metadata dan approval state

### 6.4 Struktur Direktori Project

ai-campaign-clipper/
├── app.py
├── pipeline/
│ ├── ingest.py
│ ├── downloader.py
│ ├── transcriber.py
│ ├── analyzer.py
│ ├── cutter.py
│ ├── captioner.py
│ └── face_tracker.py
├── static/
│ └── index.html
├── workspace/
│ └── {campaign_id}/
│ └── {asset_id}/
├── outputs/
│ └── {campaign_id}/
├── data/
│ ├── campaigns/
│ ├── assets/
│ └── approvals/
├── .env
└── requirements.txt

---

## 7. API Endpoints (FastAPI)

| Method   | Endpoint                      | Phase | Deskripsi                                            |
| -------- | ----------------------------- | ----- | ---------------------------------------------------- |
| `POST`   | `/api/campaigns`              | 1     | Buat campaign baru                                   |
| `GET`    | `/api/campaigns/{id}`         | 1     | Ambil detail campaign + asset terkait                |
| `POST`   | `/api/campaigns/{id}/assets`  | 1     | Tambah source video ke campaign                      |
| `POST`   | `/api/assets/{id}/analyze`    | 1     | Mulai transkripsi + candidate suggestion             |
| `GET`    | `/api/assets/{id}`            | 1     | Status job, logs, progress                           |
| `GET`    | `/api/assets/{id}/candidates` | 1     | List candidate clip + metadata                       |
| `PATCH`  | `/api/candidates/{id}`        | 1     | Edit metadata kandidat atau timestamp ringan         |
| `PATCH`  | `/api/candidates/{id}/review` | 1     | Set status approval: approve / reject / needs_review |
| `POST`   | `/api/candidates/{id}/export` | 1     | Export candidate yang sudah approved                 |
| `GET`    | `/api/exports/{id}/download`  | 1     | Download clip final                                  |
| `GET`    | `/api/campaigns/{id}/events`  | 2     | SSE progress & activity feed                         |
| `GET`    | `/api/campaigns`              | 2     | Riwayat campaign                                     |
| `DELETE` | `/api/assets/{id}`            | 2     | Hapus asset + workspace                              |
| `PATCH`  | `/api/campaigns/{id}/config`  | 2     | Update default model, template, output preset        |

### Contoh Request — Buat Campaign

| Field                   | Contoh                                             |
| ----------------------- | -------------------------------------------------- |
| `campaign_name`         | `Ramadan Push 2026`                                |
| `client_or_brand`       | `Brand X`                                          |
| `campaign_goal`         | `reach`                                            |
| `target_platforms`      | `["TikTok", "Shorts"]`                             |
| `target_view_threshold` | `1000000`                                          |
| `payout_context`        | `Bonus jika 1 klip tembus 1M views`                |
| `notes`                 | `Fokus hook 2 detik pertama dan angle testimonial` |

### Contoh Request — Tambah Source Asset

| Field                | Contoh            |
| -------------------- | ----------------- |
| `source_type`        | `upload`          |
| `source_url`         | `https://...`     |
| `influencer_name`    | `Nadia A.`        |
| `rights_basis`       | `client-approved` |
| `usage_confirmation` | `true`            |
| `language`           | `id`              |
| `max_candidates`     | `8`               |
| `output_presets`     | `["9:16", "1:1"]` |

### Contoh Response — Candidate Clip

| Field            | Contoh                                                                    |
| ---------------- | ------------------------------------------------------------------------- |
| `candidate_id`   | `cand_01`                                                                 |
| `asset_id`       | `asset-07`                                                                |
| `start`          | `00:02:14.200`                                                            |
| `end`            | `00:02:49.800`                                                            |
| `state`          | `suggested`                                                               |
| `confidence`     | `0.78`                                                                    |
| `reason`         | `Ada hook kuat di 3 detik pertama dan relevan dengan objective awareness` |
| `suggested_hook` | `“Banyak orang salah paham soal ini...”`                                  |
| `title`          | `Hook testimonial singkat`                                                |
| `cta`            | `Lihat hasil lengkapnya di caption`                                       |
| `tags`           | `testimonial, awareness, creator-led`                                     |

---

## 8. Analisis Biaya

### 8.1 Per Komponen

| Komponen              | Tool             | Cost                        | Keterangan                                      |
| --------------------- | ---------------- | --------------------------- | ----------------------------------------------- |
| Upload / ingest lokal | Local filesystem | **Gratis**                  | Tidak perlu cloud storage                       |
| yt-dlp                | CLI              | **Gratis**                  | Hanya dipakai bila source URL memang diizinkan  |
| ffmpeg                | CLI              | **Gratis**                  | Cut, reframe, export                            |
| Whisper               | Lokal            | **Gratis**                  | CPU-friendly, offline                           |
| MediaPipe             | Lokal            | **Gratis**                  | Phase 2 untuk smart crop                        |
| AI Assistance         | OpenRouter API   | **~Rp 75–300/source video** | Bergantung panjang transkrip dan jumlah iterasi |
| Hosting               | PC sendiri       | **Gratis**                  | localhost                                       |
| Storage               | Local disk       | **Gratis**                  | Bisa dibersihkan otomatis                       |

### 8.2 Estimasi Bulanan

| Volume                 | Estimasi Biaya      |
| ---------------------- | ------------------- |
| 25 source video/bulan  | ~Rp 2.000 – 7.500   |
| 100 source video/bulan | ~Rp 7.500 – 30.000  |
| 200 source video/bulan | ~Rp 15.000 – 60.000 |

### 8.3 Catatan Penting

Biaya tool tidak identik dengan hasil campaign. Walau payout campaign bisa dipengaruhi performa views, tool ini hanya membantu proses produksi dan review. Outcome distribusi tetap dipengaruhi creative quality, talent fit, media strategy, timing, dan platform dynamics.

---

## 9. Phase Roadmap

| Phase | Nama                       | Scope                                                                                                                                          | Durasi     | Status      |
| ----- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------- |
| **1** | Core Campaign Workflow MVP | Campaign metadata, rights confirmation, ingest asset, transkripsi, candidate suggestion, hook assistance, review queue, approval state, export | 2–3 minggu | 🟢 MVP      |
| **2** | Review & Output Polish     | Reframe, output size selector, burn caption, metadata editing, trim adjustment, history, model selection, template brief                       | 2–3 minggu | 🟡 Next     |
| **3** | Campaign Scale Features    | Batch asset per campaign, approval notes, audit trail, reusable presets, performance tuning                                                    | 2–4 minggu | 🔵 Advanced |
| **4** | Optional Integrations      | Export package, handoff metadata, downstream integrations                                                                                      | TBD        | ⚪ Future   |

### 9.1 Detail Phase 1 — Core Campaign Workflow MVP

1. Setup project, struktur folder, `.env`, local storage
2. Form campaign metadata + rights confirmation
3. Ingest asset dari upload atau approved URL
4. Whisper transcription dengan timestamp
5. OpenRouter analysis untuk candidate segment suggestion
6. Generate hook/title/CTA suggestion per kandidat
7. Review queue dengan preview dan approval state
8. Export hanya untuk kandidat yang di-approve
9. Testing end-to-end dengan beberapa skenario campaign influencer

### 9.2 Detail Phase 2 — Review & Output Polish

1. Reframe dan output size selector
2. Burn caption ke klip final
3. Edit metadata kandidat di UI
4. Manual trim adjustment ringan
5. Dropdown model OpenRouter
6. Template prompt berdasarkan tipe campaign
7. History campaign dan asset

---

## 10. Acceptance Criteria

### Phase 1 selesai jika:

- [ ] User dapat membuat campaign dan mengisi metadata dasar
- [ ] User wajib mengonfirmasi hak penggunaan asset sebelum proses dimulai
- [ ] Source video approved dapat di-upload atau di-ingest dengan sukses
- [ ] Sistem menghasilkan minimal 3 kandidat klip dari video berdurasi 30–60 menit
- [ ] Tiap kandidat memiliki timestamp, alasan pemilihan, dan saran hook/metadata
- [ ] User dapat preview kandidat sebelum mengambil keputusan
- [ ] Tidak ada klip yang bisa diexport tanpa status `approved`
- [ ] Status `suggested`, `needs_review`, `approved`, `rejected`, dan `exported` tercatat dengan benar
- [ ] Export menghasilkan file `.mp4` yang dapat dipakai untuk workflow distribusi
- [ ] Error handling jelas untuk source invalid, rights belum dikonfirmasi, atau proses analisis gagal
- [ ] Sistem tetap berguna sebagai assistive production tool, bukan full-auto generator final output

---

## 11. Risiko & Mitigasi

| Risiko                                                  | Probabilitas | Mitigasi                                                                                   |
| ------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------ |
| User mencoba memproses konten tanpa izin                | Sedang       | Rights confirmation wajib, legal note jelas, metadata `rights_basis` wajib                 |
| AI suggestion dianggap sebagai jaminan performa         | Tinggi       | Copy produk dan UI harus menekankan “candidate suggestion”, bukan prediksi viral           |
| Stakeholder salah memahami target views sebagai jaminan | Sedang       | Cantumkan bahwa target campaign adalah context bisnis, bukan output yang dijanjikan sistem |
| Kualitas candidate tidak cocok untuk semua brief        | Sedang       | Brief template fleksibel, edit metadata, review manusia wajib                              |
| Whisper lambat di CPU                                   | Tinggi       | Sediakan opsi model lebih ringan untuk draft                                               |
| OpenRouter rate limit / model tidak stabil              | Rendah       | Retry logic, fallback model, schema validation                                             |
| Reframe tidak sesuai framing campaign                   | Sedang       | Preview sebelum export dan opsi `original`                                                 |
| Storage penuh karena asset besar                        | Sedang       | Auto-cleanup workspace setelah export                                                      |
| Workflow terlalu mirip auto content factory             | Sedang       | Wajibkan review/approval dan fokuskan positioning sebagai production assist tool           |

---

## 12. Dependencies

### requirements.txt

fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-dotenv>=1.0.0
yt-dlp>=2024.3.10
openai-whisper>=20231117
openai>=1.0.0
mediapipe>=0.10.9
opencv-python>=4.9.0
numpy>=1.26.0
python-multipart>=0.0.9
aiofiles>=23.2.1

> OpenRouter menggunakan format API yang kompatibel dengan OpenAI SDK.
> Set `base_url="https://openrouter.ai/api/v1"` dan `api_key=OPENROUTER_API_KEY`.

### System Requirements

- Python 3.10+
- `ffmpeg` terinstall dan ada di PATH
- RAM minimal 8GB, direkomendasikan 16GB
- Storage minimal 10GB kosong untuk workspace
- Koneksi internet untuk ingest URL dan OpenRouter API
- `OPENROUTER_API_KEY` dari openrouter.ai

### .env Template

OPENROUTER_API_KEY=sk-or-...
DEFAULT_MODEL=anthropic/claude-3.5-haiku
WHISPER_MODEL=medium
MAX_CANDIDATES=8
DEFAULT_REVIEW_REQUIRED=true
AUTO_CLEANUP=true

---

## 13. Disclaimer & Legal

> ⚠️ **LEGAL NOTE:** Aplikasi ini dirancang untuk memproses video yang **kamu miliki** atau yang **secara eksplisit diizinkan untuk kamu repurpose** dalam konteks campaign. Ini termasuk asset influencer/source video yang sudah approved oleh pihak yang berwenang. Jangan gunakan aplikasi ini untuk mendownload, memotong, atau mendistribusikan konten yang tidak kamu miliki dan tidak kamu miliki otorisasi penggunaannya.

> ⚠️ **PRODUCT POSITIONING NOTE:** Aplikasi ini membantu produksi kandidat klip campaign dengan AI assistance, metadata suggestion, dan workflow review. Aplikasi ini **bukan** alat yang menjanjikan viral, payout, atau performa distribusi tertentu.

---

_Dokumen ini adalah living document dan akan diupdate seiring perkembangan implementasi._
_v2.0.0 — Revisi arah produk untuk workflow campaign influencer — 27 Maret 2026_
