# DOKUMEN TEKNIKAL — AI Campaign Clip Workflow

**Project:** AI Campaign Clip Workflow
**Tipe:** Local-first internal production tool
**Platform:** Windows PC / localhost
**Status:** Technical design draft
**Tujuan:** Menjabarkan desain teknikal lengkap untuk aplikasi lokal yang membantu workflow clipping campaign influencer/source video menjadi candidate clips yang bisa direview, diedit, dan diexport secara fleksibel.

---

## 1. Ringkasan Teknis

Aplikasi ini adalah **tool produksi lokal** untuk membantu operator campaign memproses video yang **sudah dimiliki atau diizinkan untuk direpurpose** menjadi beberapa kandidat klip pendek untuk TikTok, Shorts, Reels, atau kebutuhan campaign lain.

Aplikasi ini **bukan**:

- sistem upload otomatis ke platform,
- sistem auth multi-user,
- SaaS publik,
- alat yang menjanjikan viral,
- alat yang menjamin payout campaign.

Aplikasi ini **adalah**:

- workflow engine lokal,
- pengolah asset video campaign,
- pembantu transkripsi,
- pembantu candidate segment suggestion,
- pembantu review metadata,
- pembantu rendering dan export.

Arsitektur dibuat untuk:

- jalan di localhost,
- dipakai 1 user atau tim kecil secara bergantian,
- tidak butuh auth,
- menyimpan semua data ke local filesystem,
- mudah dimodifikasi sesuai workflow pribadi.

---

## 2. Sasaran Sistem

### 2.1 Sasaran Utama

Sistem harus mampu:

1. menerima input campaign dan source video,
2. memvalidasi metadata dasar dan konfirmasi hak penggunaan,
3. mengimpor video dari file lokal atau URL yang diizinkan,
4. mengekstrak audio dan membuat transkrip,
5. menganalisis transkrip dengan AI untuk menghasilkan kandidat segmen,
6. menampilkan candidate clip untuk direview user,
7. memungkinkan user mengedit metadata dan timestamp,
8. mengekspor hanya clip yang sudah disetujui,
9. menyimpan jejak campaign, asset, candidate, dan output secara lokal.

### 2.2 Sasaran Tambahan

Sistem idealnya juga mendukung:

- beberapa preset output size,
- subtitle burn-in,
- metadata per clip,
- status approval,
- riwayat campaign,
- reuse hasil analisis tanpa perlu transcribe ulang,
- struktur data yang siap dikembangkan bila nanti ingin menambah automasi.

---

## 3. Prinsip Desain

### 3.1 Local-first

Semua proses inti sebisa mungkin berjalan lokal:

- file source disimpan lokal,
- transkripsi disimpan lokal,
- candidate metadata disimpan lokal,
- output render disimpan lokal.

AI eksternal hanya dipakai untuk:

- analisis transkrip,
- suggestion hook,
- title,
- CTA,
- tagging ringan.

### 3.2 Human-in-the-loop

Output AI tidak dianggap final.
Semua candidate clip harus bisa:

- dipreview,
- diedit,
- diapprove,
- direject,
- diexport hanya jika approved.

### 3.3 Flexible Workflow

Sistem tidak boleh terlalu memaksa satu pola campaign saja.
User harus bisa menyesuaikan:

- objective,
- target platform,
- max candidates,
- gaya output,
- prompt analysis,
- naming convention,
- workflow review.

### 3.4 Simple Operations

Karena ini tool pribadi lokal:

- tidak perlu auth,
- tidak perlu role system,
- tidak perlu database rumit di awal jika local file storage cukup,
- tidak perlu cloud infra.

### 3.5 Safe by Default

Sistem harus menekankan bahwa:

- hanya konten milik sendiri / approved yang diproses,
- AI suggestion bukan jaminan performa,
- payout campaign adalah konteks bisnis, bukan output sistem.

---

## 4. Ruang Lingkup Teknis

## 4.1 In Scope

- campaign management lokal
- asset ingest
- local file upload
- source download dari URL yang diizinkan
- transcript generation
- transcript storage
- AI candidate suggestion
- metadata suggestion
- review workflow
- render clip
- subtitle burn-in
- output export
- riwayat job/campaign
- log progress
- config lokal

## 4.2 Out of Scope

- authentication
- multi-tenant
- cloud deployment
- direct posting ke TikTok/YouTube/Instagram
- billing
- influencer outreach management
- campaign payment management
- analytics views dari platform
- kontrak/legal workflow management
- anti-ban automation
- browser automation upload

---

## 5. Tech Stack yang Disarankan

| Layer                 | Teknologi                                 | Alasan                                          |
| --------------------- | ----------------------------------------- | ----------------------------------------------- |
| Backend API           | FastAPI                                   | Cepat, sederhana, bagus untuk local API dan SSE |
| Frontend              | HTML + CSS + Vanilla JS / Alpine.js kecil | Ringan, cukup untuk tool internal               |
| Video Processing      | ffmpeg                                    | Stabil, fleksibel, battle-tested                |
| Download Source       | yt-dlp                                    | Praktis untuk source URL yang diizinkan         |
| STT                   | Whisper lokal                             | Akurat, offline, stabil                         |
| AI Analysis           | OpenRouter                                | Fleksibel memilih model                         |
| Reframe / Face detect | MediaPipe / OpenCV                        | Cukup untuk face-aware crop                     |
| Local Storage         | JSON + folder filesystem                  | Mudah dan cepat untuk local-first               |
| Optional DB           | SQLite                                    | Jika nanti metadata makin kompleks              |
| Background Jobs       | asyncio + thread pool / process pool      | Cukup untuk local async processing              |

### 5.1 Catatan Pemilihan Storage

Untuk versi awal yang siap pakai secara lokal, ada dua pendekatan:

#### Opsi A — File-based JSON

Cocok jika:

- hanya dipakai sendiri,
- volume belum terlalu besar,
- ingin setup sangat cepat.

Kelebihan:

- sangat mudah dipahami,
- mudah backup manual,
- mudah debug.

Kekurangan:

- query data tidak fleksibel,
- concurrency lebih sensitif,
- lama-lama bisa berantakan bila tanpa disiplin.

#### Opsi B — SQLite + filesystem

Cocok jika:

- ingin sistem lebih rapi,
- data campaign cukup banyak,
- ingin filtering lebih mudah.

Rekomendasi saya:

- **pakai SQLite untuk metadata**
- **pakai filesystem untuk file besar**
- sehingga:
  - video, audio, subtitle, output tetap di folder,
  - campaign, asset, candidate, export, log ringkas disimpan di SQLite.

Itu paling seimbang untuk local app yang serius.

---

## 6. Arsitektur Sistem

## 6.1 Gambaran Umum

Sistem terdiri dari 5 blok utama:

1. **UI Layer**
   - form campaign
   - asset upload/import
   - transcript viewer
   - candidate review queue
   - preview/export page
   - settings/config page

2. **API Layer**
   - REST endpoints
   - SSE event stream
   - validation
   - state transitions
   - orchestration

3. **Service Layer**
   - campaign service
   - asset service
   - transcription service
   - analysis service
   - candidate service
   - export service
   - subtitle service

4. **Worker / Pipeline Layer**
   - ingest worker
   - download worker
   - transcribe worker
   - analyze worker
   - render worker
   - cleanup worker

5. **Storage Layer**
   - SQLite metadata
   - filesystem untuk source/output/artifacts
   - config file
   - logs

---

## 6.2 Arsitektur Data Flow

### Flow Tingkat Tinggi

1. User membuat campaign
2. User menambahkan source asset
3. Asset disimpan ke workspace
4. Audio diekstrak
5. Whisper menghasilkan transkrip
6. Analyzer mengirim transkrip + brief ke AI
7. Sistem membuat candidate clips
8. User mereview candidate
9. User approve/reject/edit
10. User export clip
11. Output akhir disimpan dan siap dipakai

### Flow Internal

- `campaign` menjadi container utama
- `asset` menjadi sumber video mentah
- `transcript` menjadi basis analisis
- `candidate` menjadi unit review
- `export` menjadi hasil final yang sudah diapprove

---

## 7. Struktur Project yang Disarankan

```aiclip-app/docs/TEKNIKAL.md#L1-200
aiclip-app/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── constants.py
│   ├── logging.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── campaigns.py
│   │   │   ├── assets.py
│   │   │   ├── transcripts.py
│   │   │   ├── candidates.py
│   │   │   ├── exports.py
│   │   │   ├── jobs.py
│   │   │   └── settings.py
│   │   ├── schemas/
│   │   │   ├── common.py
│   │   │   ├── campaign.py
│   │   │   ├── asset.py
│   │   │   ├── transcript.py
│   │   │   ├── candidate.py
│   │   │   ├── export.py
│   │   │   └── job.py
│   │   └── errors.py
│   │
│   ├── core/
│   │   ├── database.py
│   │   ├── events.py
│   │   ├── state_machine.py
│   │   ├── file_manager.py
│   │   ├── ffmpeg.py
│   │   ├── ytdlp.py
│   │   ├── whisper_runner.py
│   │   ├── openrouter.py
│   │   └── subtitle.py
│   │
│   ├── models/
│   │   ├── campaign.py
│   │   ├── asset.py
│   │   ├── transcript.py
│   │   ├── candidate.py
│   │   ├── export.py
│   │   ├── job.py
│   │   └── audit_log.py
│   │
│   ├── repositories/
│   │   ├── campaign_repo.py
│   │   ├── asset_repo.py
│   │   ├── transcript_repo.py
│   │   ├── candidate_repo.py
│   │   ├── export_repo.py
│   │   ├── job_repo.py
│   │   └── audit_repo.py
│   │
│   ├── services/
│   │   ├── campaign_service.py
│   │   ├── asset_service.py
│   │   ├── ingest_service.py
│   │   ├── transcription_service.py
│   │   ├── analysis_service.py
│   │   ├── candidate_service.py
│   │   ├── review_service.py
│   │   ├── rendering_service.py
│   │   ├── subtitle_service.py
│   │   ├── export_service.py
│   │   ├── settings_service.py
│   │   └── cleanup_service.py
│   │
│   ├── workers/
│   │   ├── queue.py
│   │   ├── job_runner.py
│   │   ├── ingest_worker.py
│   │   ├── transcribe_worker.py
│   │   ├── analyze_worker.py
│   │   ├── render_worker.py
│   │   └── cleanup_worker.py
│   │
│   └── prompts/
│       ├── candidate_segments.md
│       ├── hook_assist.md
│       ├── finance_guardrails.md
│       ├── tech_guardrails.md
│       └── output_schema.md
│
├── static/
│   ├── index.html
│   ├── assets/
│   │   ├── app.css
│   │   ├── app.js
│   │   ├── api.js
│   │   ├── state.js
│   │   ├── components/
│   │   │   ├── campaign-form.js
│   │   │   ├── asset-upload.js
│   │   │   ├── transcript-viewer.js
│   │   │   ├── candidate-list.js
│   │   │   ├── candidate-editor.js
│   │   │   ├── preview-player.js
│   │   │   ├── export-panel.js
│   │   │   └── settings-panel.js
│   │   └── utils/
│   │       ├── time.js
│   │       ├── format.js
│   │       └── validation.js
│
├── data/
│   ├── app.db
│   ├── campaigns/
│   ├── assets/
│   ├── transcripts/
│   ├── candidates/
│   ├── exports/
│   ├── jobs/
│   ├── logs/
│   └── temp/
│
├── docs/
│   ├── PRD.md
│   └── TEKNIKAL.md
│
├── scripts/
│   ├── init_db.py
│   ├── reindex_files.py
│   ├── cleanup_temp.py
│   └── dev_run.py
│
├── tests/
│   ├── test_campaign_service.py
│   ├── test_asset_service.py
│   ├── test_candidate_service.py
│   ├── test_rendering_service.py
│   ├── test_state_machine.py
│   └── test_api_smoke.py
│
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## 8. Struktur Direktori Data Runtime

### 8.1 Struktur Fisik File

Setiap campaign dan asset sebaiknya punya folder sendiri agar rapi.

```aiclip-app/docs/TEKNIKAL.md#L201-280
data/
├── campaigns/
│   └── cmp_20260327_001/
│       ├── campaign.json
│       ├── notes.md
│       ├── assets/
│       │   └── asset_001/
│       │       ├── source.mp4
│       │       ├── audio.wav
│       │       ├── transcript.json
│       │       ├── transcript.txt
│       │       ├── transcript.srt
│       │       ├── analysis_input.json
│       │       ├── analysis_output.json
│       │       ├── candidates/
│       │       │   ├── cand_001.json
│       │       │   ├── cand_002.json
│       │       │   └── cand_003.json
│       │       ├── previews/
│       │       │   ├── cand_001_preview.mp4
│       │       │   └── cand_002_preview.mp4
│       │       ├── exports/
│       │       │   ├── cand_001_9x16.mp4
│       │       │   ├── cand_001_1x1.mp4
│       │       │   └── cand_001_metadata.json
│       │       └── logs/
│       │           ├── ingest.log
│       │           ├── transcribe.log
│       │           ├── analyze.log
│       │           └── render.log
│       └── audit/
│           └── activity.log
```

### 8.2 Kenapa Struktur Ini Bagus

- campaign mudah dipisah
- asset mudah dicari
- output mudah diarsip
- debugging mudah
- backup manual mudah
- tidak tergantung cloud storage

---

## 9. Domain Model

## 9.1 Entitas Utama

### Campaign

Mewakili satu konteks campaign.

Field penting:

- `id`
- `name`
- `client_or_brand`
- `goal`
- `target_platforms`
- `target_view_threshold`
- `payout_context`
- `notes`
- `default_output_presets`
- `default_language`
- `status`
- `created_at`
- `updated_at`

### Asset

Mewakili satu sumber video dalam campaign.

Field penting:

- `id`
- `campaign_id`
- `source_type`
- `source_url`
- `source_filename`
- `storage_path`
- `duration_seconds`
- `language`
- `rights_basis`
- `usage_confirmation`
- `influencer_name`
- `status`
- `created_at`
- `updated_at`

### Transcript

Hasil transkripsi dari asset.

Field penting:

- `id`
- `asset_id`
- `text`
- `language`
- `segments_json_path`
- `words_json_path`
- `srt_path`
- `txt_path`
- `status`
- `created_at`

### CandidateClip

Unit utama untuk review.

Field penting:

- `id`
- `asset_id`
- `start_ms`
- `end_ms`
- `duration_ms`
- `confidence_score`
- `reason`
- `suggested_hook`
- `suggested_title`
- `suggested_cta`
- `tags`
- `state`
- `manual_notes`
- `edited_start_ms`
- `edited_end_ms`
- `approved_at`
- `rejected_at`
- `created_at`
- `updated_at`

### Export

Representasi hasil render final.

Field penting:

- `id`
- `candidate_id`
- `output_preset`
- `output_path`
- `with_caption`
- `render_status`
- `render_log_path`
- `created_at`

### Job

Representasi proses background.

Field penting:

- `id`
- `type`
- `entity_type`
- `entity_id`
- `status`
- `progress`
- `message`
- `started_at`
- `finished_at`

### AuditLog

Jejak perubahan.

Field penting:

- `id`
- `entity_type`
- `entity_id`
- `action`
- `payload_json`
- `created_at`

---

## 10. State Machine

## 10.1 Asset State

```aiclip-app/docs/TEKNIKAL.md#L281-330
draft
→ ingesting
→ ready
→ transcribing
→ transcribed
→ analyzing
→ analyzed
→ review_ready
→ archived
→ failed
```

## 10.2 Candidate State

```aiclip-app/docs/TEKNIKAL.md#L331-360
suggested
→ needs_review
→ approved
→ rejected
→ exported
```

## 10.3 Export State

```aiclip-app/docs/TEKNIKAL.md#L361-390
queued
→ rendering
→ completed
→ failed
```

### 10.4 Kenapa State Machine Penting

Karena project ini punya alur yang jelas dan asynchronous.
State machine membantu:

- mencegah export sebelum approve,
- mencegah analyze sebelum transcript siap,
- mempermudah UI,
- mempermudah debugging.

---

## 11. Flow User End-to-End

## 11.1 Flow Utama

### Langkah 1 — Buka app lokal

User menjalankan app di localhost.

### Langkah 2 — Buat campaign

User mengisi:

- nama campaign
- goal
- target platforms
- notes
- target view threshold jika ada
- payout context jika mau dicatat

### Langkah 3 — Tambah source asset

User bisa:

- upload file video
- input URL yang approved

Lalu user isi:

- influencer/source name
- rights basis
- konfirmasi penggunaan legal
- bahasa
- max candidates
- output preset default

### Langkah 4 — Ingest asset

Sistem:

- menyimpan file
- membaca metadata video
- membuat job
- menampilkan progress

### Langkah 5 — Transcribe

Sistem:

- extract audio
- jalankan Whisper
- simpan transcript
- buat transcript viewer

### Langkah 6 — Analyze

Sistem:

- susun prompt analysis
- kirim transcript + brief
- terima candidate segments
- validasi schema output
- simpan candidate

### Langkah 7 — Review candidate

User melihat:

- preview klip
- alasan AI
- hook/title/CTA
- duration
- score/confidence

User bisa:

- approve
- reject
- edit title
- edit CTA
- edit timestamp
- ganti output preset

### Langkah 8 — Export

Untuk candidate approved:

- pilih preset
- pilih subtitle on/off
- render
- unduh hasil

### Langkah 9 — Simpan dan arsip

Campaign, metadata, output, dan log tetap tersedia lokal.

---

## 11.2 Flow Alternatif

### Jika transcript sudah ada

User bisa skip transcribe dan import transcript.

### Jika candidate AI jelek

User bisa:

- re-run analyze dengan prompt lain,
- tambah notes campaign,
- ubah max candidates,
- pilih candidate manual dari transcript viewer.

### Jika output framing jelek

User bisa:

- pilih original
- pilih center crop
- pilih face-track
- edit start/end ulang lalu render lagi

---

## 12. Rancangan UI

## 12.1 Halaman / Panel Utama

### 1. Dashboard

Menampilkan:

- daftar campaign
- asset terbaru
- job berjalan
- export terbaru
- shortcut create campaign

### 2. Campaign Detail

Menampilkan:

- metadata campaign
- daftar asset
- jumlah candidate
- jumlah approved
- jumlah export
- activity log

### 3. Asset Detail

Menampilkan:

- preview source video
- transcript summary
- tombol transcribe/analyze
- daftar candidate
- log proses

### 4. Transcript Viewer

Menampilkan:

- transcript per segment
- search keyword
- timestamp clickable
- highlight candidate ranges

### 5. Candidate Review Panel

Menampilkan:

- player preview
- suggested hook/title/CTA
- state badge
- confidence
- reason
- tags
- edit form
- approve/reject/export actions

### 6. Export Panel

Menampilkan:

- daftar output
- preset yang tersedia
- subtitle options
- file paths
- tombol download / open folder

### 7. Settings

Menampilkan:

- OpenRouter model default
- Whisper model
- output presets default
- ffmpeg path bila manual
- workspace path
- cleanup policy

---

## 12.2 Prinsip UI

- satu halaman utama dengan panel kanan/kiri cukup
- minim klik
- semua state terlihat jelas
- log proses mudah dibaca
- preview cepat diakses
- edit candidate tidak membingungkan
- warna state konsisten:
  - suggested = biru
  - needs_review = kuning
  - approved = hijau
  - rejected = merah
  - exported = ungu/abu

---

## 13. API Design

## 13.1 Campaign Endpoints

- `POST /api/campaigns`
- `GET /api/campaigns`
- `GET /api/campaigns/{id}`
- `PATCH /api/campaigns/{id}`
- `DELETE /api/campaigns/{id}`

## 13.2 Asset Endpoints

- `POST /api/campaigns/{id}/assets`
- `GET /api/assets/{id}`
- `PATCH /api/assets/{id}`
- `DELETE /api/assets/{id}`
- `POST /api/assets/{id}/ingest`
- `POST /api/assets/{id}/transcribe`
- `POST /api/assets/{id}/analyze`

## 13.3 Transcript Endpoints

- `GET /api/assets/{id}/transcript`
- `GET /api/assets/{id}/transcript/search?q=...`
- `POST /api/assets/{id}/transcript/import`

## 13.4 Candidate Endpoints

- `GET /api/assets/{id}/candidates`
- `POST /api/assets/{id}/candidates/manual`
- `GET /api/candidates/{id}`
- `PATCH /api/candidates/{id}`
- `PATCH /api/candidates/{id}/approve`
- `PATCH /api/candidates/{id}/reject`
- `PATCH /api/candidates/{id}/needs-review`

## 13.5 Export Endpoints

- `POST /api/candidates/{id}/exports`
- `GET /api/exports/{id}`
- `GET /api/exports/{id}/download`
- `GET /api/exports/{id}/stream`

## 13.6 Job / Event Endpoints

- `GET /api/jobs`
- `GET /api/jobs/{id}`
- `GET /api/events`
- `GET /api/campaigns/{id}/events`

## 13.7 Settings Endpoints

- `GET /api/settings`
- `PATCH /api/settings`

---

## 14. Request / Response Model

## 14.1 Create Campaign

Request:

```aiclip-app/docs/TEKNIKAL.md#L391-410
{
  "name": "Tech Creator Push April",
  "client_or_brand": "Internal",
  "goal": "reach",
  "target_platforms": ["TikTok", "Shorts"],
  "target_view_threshold": 1000000,
  "payout_context": "Payout jika 1 klip mencapai 1 juta views",
  "notes": "Fokus potongan yang punya hook kuat dan mudah dipahami tanpa konteks panjang"
}
```

## 14.2 Add Asset

Request:

```aiclip-app/docs/TEKNIKAL.md#L411-435
{
  "source_type": "upload",
  "source_url": null,
  "influencer_name": "Creator A",
  "rights_basis": "approved",
  "usage_confirmation": true,
  "language": "id",
  "max_candidates": 8,
  "output_presets": ["9:16", "1:1"]
}
```

## 14.3 Candidate Object

Response:

```aiclip-app/docs/TEKNIKAL.md#L436-458
{
  "id": "cand_001",
  "asset_id": "asset_001",
  "start_ms": 134000,
  "end_ms": 169000,
  "duration_ms": 35000,
  "confidence_score": 0.82,
  "reason": "Kalimat pembuka langsung problem statement dan cocok untuk angle awareness",
  "suggested_hook": "Masalah terbesar orang saat pakai tools AI itu bukan fiturnya...",
  "suggested_title": "Hook problem-solution singkat",
  "suggested_cta": "Lanjutkan di caption",
  "tags": ["awareness", "hook", "creator"],
  "state": "suggested"
}
```

---

## 15. Pipeline Teknis

## 15.1 Ingest Pipeline

Langkah:

1. validasi input
2. simpan metadata asset
3. copy/upload file atau download URL
4. cek ffprobe untuk metadata
5. simpan duration, resolution, codec
6. update state ke `ready`

Failure case:

- file corrupt
- URL gagal diambil
- unsupported format
- storage tidak cukup

## 15.2 Transcription Pipeline

Langkah:

1. extract audio dengan ffmpeg
2. normalize audio jika perlu
3. jalankan Whisper
4. simpan:
   - raw segments
   - text full
   - word timestamps
   - srt
5. update state ke `transcribed`

Optimasi:

- cache transcript
- jangan transcribe ulang bila source hash sama
- model whisper configurable

## 15.3 Analysis Pipeline

Langkah:

1. baca transcript
2. ambil campaign brief
3. build prompt berdasarkan niche/goal
4. kirim ke AI model
5. minta output JSON schema ketat
6. validasi output
7. normalisasi candidate timestamps
8. simpan candidate ke DB
9. update state ke `review_ready`

Failure case:

- output AI tidak valid
- model timeout
- candidate overlapping berlebihan
- segmen terlalu pendek/panjang

## 15.4 Preview Pipeline

Untuk setiap candidate:

1. buat preview clip cepat
2. optional low-res untuk preview agar ringan
3. tampilkan di UI

## 15.5 Export Pipeline

Langkah:

1. pastikan candidate `approved`
2. ambil effective timestamps
3. render clip dengan ffmpeg
4. reframe jika dipilih
5. burn subtitle jika dipilih
6. simpan metadata export
7. update state ke `completed`

---

## 16. AI Layer Design

## 16.1 Tujuan AI di Sistem Ini

AI hanya untuk:

- candidate segment suggestion
- reason generation
- hook suggestion
- title suggestion
- CTA ringan
- tag extraction
- optional guardrail hint

AI tidak untuk:

- auto-final publish decision
- prediksi views yang pasti
- legal guarantee
- final compliance decision

## 16.2 Input AI

Input ideal ke AI:

- transcript full atau chunk yang relevan
- campaign goal
- target platform
- niche
- notes campaign
- target duration
- max candidates
- guardrail notes

## 16.3 Output AI yang Diminta

AI harus mengembalikan:

- list candidate
- start/end references
- confidence / priority
- reason
- hook
- title
- CTA
- tags

Format harus JSON yang ketat agar mudah diparse.

## 16.4 Prompt Strategy

Pisahkan prompt:

1. candidate extraction
2. hook/title suggestion
3. niche guardrails
4. output schema enforcement

Dengan cara ini, jika satu bagian buruk, mudah diperbaiki.

## 16.5 Guardrails

Untuk niche finance:

- hindari klaim kepastian cuan
- hindari nasihat investasi eksplisit
- tandai angka sensitif
- tandai potongan yang berisiko misleading

Untuk niche technology:

- tandai klaim produk
- tandai fitur yang belum tentu rilis
- tandai komparasi yang terlalu agresif

---

## 17. Subtitle System

## 17.1 Jenis Subtitle

Minimal dukung:

- external `.srt`
- burned-in subtitle

## 17.2 Sumber Subtitle

Dari Whisper timestamps.

## 17.3 Styling Awal

Preset awal cukup:

- font sans-serif
- size sedang
- outline hitam
- posisi bawah aman
- 2 line max
- line break sederhana

## 17.4 Advanced Nanti

- keyword highlight
- word-by-word animation
- tech preset
- finance preset
- top caption mode

---

## 18. Rendering Strategy

## 18.1 Preset Output

Minimal:

- `9:16`
- `1:1`
- `4:5`
- `original`

## 18.2 Reframe Mode

- `none`
- `center`
- `face_track`

## 18.3 Rendering Levels

### Preview Render

- resolusi lebih rendah
- cepat
- untuk review

### Final Render

- kualitas lebih baik
- subtitle final
- naming final
- metadata lengkap

## 18.4 Naming Convention

Format nama file yang konsisten:

- `{campaign}_{asset}_{candidate}_{preset}.mp4`
- `{campaign}_{asset}_{candidate}_metadata.json`
- `{campaign}_{asset}_{candidate}.srt`

Contoh:

- `techpush_asset001_cand003_9x16.mp4`

---

## 19. Logging dan Observability

## 19.1 Log yang Perlu Ada

- app log
- ingest log
- transcribe log
- analyze log
- render log
- audit log

## 19.2 Isi Log Minimal

- timestamp
- entity
- action
- status
- error bila ada
- duration step

## 19.3 UI Feedback

User harus melihat:

- progress per step
- pesan error yang manusiawi
- status entity
- history job

---

## 20. Error Handling

## 20.1 Error yang Harus Ditangani

- source invalid
- file terlalu besar
- download gagal
- ffmpeg tidak tersedia
- whisper gagal load
- AI timeout
- JSON output AI invalid
- subtitle generation gagal
- export gagal
- disk penuh

## 20.2 Prinsip Error Message

Jangan hanya tampilkan:

- `Unknown Error`

Lebih baik:

- step mana gagal
- kemungkinan penyebab
- tindakan user berikutnya

Contoh:

- “Transkripsi gagal karena model Whisper tidak bisa dimuat. Cek setting model dan RAM tersedia.”
- “Candidate analysis gagal karena respons AI tidak sesuai format. Coba ulangi analisis atau ganti model.”

---

## 21. Konfigurasi

## 21.1 `.env`

Contoh:

```aiclip-app/docs/TEKNIKAL.md#L459-480
APP_ENV=local
APP_HOST=127.0.0.1
APP_PORT=8000

DATA_DIR=./data
LOG_LEVEL=INFO

OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-3.5-haiku

WHISPER_MODEL=medium
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe
YTDLP_PATH=yt-dlp

DEFAULT_MAX_CANDIDATES=8
DEFAULT_LANGUAGE=id
DEFAULT_REVIEW_REQUIRED=true
AUTO_CLEANUP=false
```

## 21.2 Settings UI

Semua config penting idealnya juga bisa diubah dari UI:

- whisper model
- AI model
- output defaults
- temp directory
- cleanup behavior
- preview quality

---

## 22. Database Design Awal

Jika pakai SQLite, tabel minimal:

### campaigns

- id
- name
- client_or_brand
- goal
- target_platforms_json
- target_view_threshold
- payout_context
- notes
- status
- created_at
- updated_at

### assets

- id
- campaign_id
- source_type
- source_url
- source_filename
- storage_path
- duration_seconds
- language
- rights_basis
- usage_confirmation
- influencer_name
- status
- created_at
- updated_at

### transcripts

- id
- asset_id
- text_path
- srt_path
- words_json_path
- language
- status
- created_at

### candidates

- id
- asset_id
- start_ms
- end_ms
- edited_start_ms
- edited_end_ms
- confidence_score
- reason
- suggested_hook
- suggested_title
- suggested_cta
- tags_json
- state
- manual_notes
- created_at
- updated_at

### exports

- id
- candidate_id
- output_preset
- output_path
- with_caption
- render_status
- created_at

### jobs

- id
- type
- entity_type
- entity_id
- status
- progress
- message
- created_at
- updated_at

### audit_logs

- id
- entity_type
- entity_id
- action
- payload_json
- created_at

---

## 23. Security untuk Local App

Walaupun lokal, tetap ada hal yang perlu dijaga:

- jangan hardcode API key
- simpan API key di `.env`
- jangan expose folder data ke publik
- jangan auto-download dari source ilegal
- validasi file upload
- sanitasi nama file
- hindari command injection saat menjalankan ffmpeg / yt-dlp
- pakai subprocess dengan arg list, bukan shell string raw jika implementasi Python

---

## 24. Performance Considerations

## 24.1 Bottleneck Utama

- transkripsi
- render video
- burning subtitle
- face tracking
- preview generation

## 24.2 Optimasi Awal

- preview low-res
- cache transcript
- cache analysis result
- render final hanya saat approved
- batasi jumlah preview bersamaan
- gunakan temp cleanup
- gunakan ffmpeg parameters yang cukup cepat untuk preview

## 24.3 Resource Strategy

Karena lokal:

- satu job berat aktif per waktu lebih aman
- job kecil bisa diantrikan
- tampilkan queue ke user

---

## 25. Testing Strategy

## 25.1 Unit Tests

Test:

- validation
- state transitions
- transcript parser
- candidate normalization
- naming convention
- settings loader

## 25.2 Integration Tests

Test:

- create campaign
- add asset
- run transcribe mock
- run analyze mock
- approve candidate
- export candidate

## 25.3 Manual QA

Checklist:

- video upload sukses
- URL ingest sukses
- transcript tampil
- candidate list tampil
- approve/reject jalan
- export hanya untuk approved
- file output bisa diputar
- subtitle sinkron
- logs terbaca

---

## 26. Implementasi Bertahap yang Disarankan

Walau kamu minta tidak dibatasi MVP sempit, secara teknikal tetap lebih sehat bila implementasi dilakukan berlapis.

### Layer 1 — Fondasi

- config
- DB
- filesystem manager
- campaign CRUD
- asset CRUD

### Layer 2 — Pipeline Dasar

- ingest
- transcript
- analyze
- candidate persistence

### Layer 3 — Review Layer

- candidate editor
- approval states
- preview render
- transcript viewer

### Layer 4 — Finalization

- export
- subtitle burn-in
- output presets
- naming metadata

### Layer 5 — Polishing

- history
- logs di UI
- settings UI
- cleanup
- prompt templates

---

## 27. Rekomendasi Teknis Final

Kalau tujuanmu adalah **project lokal siap pakai** dan fleksibel untuk workflow pribadi campaign clipping, maka pendekatan terbaik adalah:

1. **FastAPI + static frontend sederhana**
2. **SQLite untuk metadata**
3. **filesystem untuk semua file besar**
4. **Whisper lokal untuk transcript**
5. **OpenRouter hanya untuk suggestion**
6. **ffmpeg sebagai tulang punggung video pipeline**
7. **human approval sebagai aturan inti**
8. **state machine yang tegas**
9. **struktur campaign/asset/candidate/export yang rapi**
10. **tanpa auth, tanpa cloud, tanpa upload automation**

Dengan desain ini, aplikasi tetap:

- ringan,
- realistis dibangun,
- mudah dipakai sendiri,
- fleksibel untuk berbagai campaign,
- dan cukup kuat untuk berkembang nanti.

---

## 28. Checklist Build Teknis

### Setup Dasar

- [ ] buat struktur folder project
- [ ] setup FastAPI app
- [ ] setup static frontend
- [ ] setup SQLite
- [ ] setup file manager
- [ ] setup config `.env`

### Core Domain

- [ ] model campaign
- [ ] model asset
- [ ] model transcript
- [ ] model candidate
- [ ] model export
- [ ] model job

### Core Pipeline

- [ ] upload/local ingest
- [ ] URL ingest
- [ ] ffprobe metadata read
- [ ] audio extraction
- [ ] whisper transcription
- [ ] transcript save
- [ ] AI analysis
- [ ] schema validation hasil AI

### Review Workflow

- [ ] candidate list
- [ ] preview generation
- [ ] approve/reject
- [ ] edit title/hook/cta
- [ ] edit timestamps

### Export Workflow

- [ ] final render
- [ ] subtitle burn-in
- [ ] output preset support
- [ ] metadata export
- [ ] download endpoint

### Operasional

- [ ] logs
- [ ] error handling
- [ ] cleanup temp
- [ ] settings page
- [ ] history page

---

## 29. Penutup

Dokumen ini mendefinisikan bentuk teknikal dari aplikasi **AI Campaign Clip Workflow** sebagai tool lokal pribadi yang fokus pada:

- efisiensi workflow,
- fleksibilitas campaign,
- review manusia,
- dan output siap pakai.

Arah desain ini sengaja menghindari janji “AI auto viral” dan lebih menempatkan sistem sebagai **production assistant** yang solid, transparan, dan bisa benar-benar dipakai sehari-hari.

Jika nanti project ini berkembang, fondasi di dokumen ini sudah cukup kuat untuk:

- menambah analytics,
- menambah batch processing,
- menambah preset niche,
- menambah integrasi downstream,
- atau memindahkan sebagian metadata ke arsitektur yang lebih besar.
