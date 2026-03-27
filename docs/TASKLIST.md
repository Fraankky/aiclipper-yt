# TASKLIST IMPLEMENTASI — AI Campaign Clip Workflow

**Project:** AI Campaign Clip Workflow
**Tipe:** Local-first production tool
**Target:** Siap pakai di localhost tanpa auth, untuk workflow pribadi / tim kecil
**Tujuan dokumen:** Memecah implementasi project menjadi task bertahap, realistis, dan bisa langsung dikerjakan.

---

## 1. Gambaran Umum

Dokumen ini memecah implementasi ke dalam beberapa fase agar project yang cukup kompleks ini tetap:

- terarah,
- tidak membingungkan,
- mudah diuji,
- dan tetap bisa menghasilkan progress nyata dari awal.

Walaupun target akhirnya adalah project yang “siap pakai”, implementasinya tetap paling sehat jika dibangun bertahap.

---

## 2. Prinsip Pengerjaan

Sebelum mulai, pegang 5 prinsip ini:

1. **Kerjakan fondasi dulu, bukan UI cantik dulu**
2. **Pastikan state dan data model rapi sejak awal**
3. **Pisahkan file besar dan metadata**
4. **Semua output AI harus bisa direview**
5. **Jangan render hal berat sebelum benar-benar dibutuhkan**

---

## 3. Urutan Besar Implementasi

Project dibagi menjadi 10 fase:

1. Setup project foundation
2. Core config dan storage
3. Domain model dan database
4. Campaign dan asset management
5. Ingest pipeline
6. Transcription pipeline
7. AI analysis dan candidate generation
8. Review workflow dan preview
9. Export workflow
10. Polishing, QA, dan dokumentasi akhir

---

## 4. Phase 0 — Project Initialization

## Tujuan
Menyiapkan fondasi repository dan environment agar semua langkah berikutnya rapi.

## Task

- [ ] buat struktur folder utama project
- [ ] buat folder:
  - [ ] `app/`
  - [ ] `app/api/`
  - [ ] `app/api/routes/`
  - [ ] `app/api/schemas/`
  - [ ] `app/core/`
  - [ ] `app/models/`
  - [ ] `app/repositories/`
  - [ ] `app/services/`
  - [ ] `app/workers/`
  - [ ] `app/prompts/`
  - [ ] `static/`
  - [ ] `static/assets/`
  - [ ] `static/assets/components/`
  - [ ] `static/assets/utils/`
  - [ ] `data/`
  - [ ] `docs/`
  - [ ] `scripts/`
  - [ ] `tests/`
- [ ] buat file dasar:
  - [ ] `.env.example`
  - [ ] `requirements.txt`
  - [ ] `README.md`
  - [ ] `app/main.py`
  - [ ] `app/config.py`
  - [ ] `app/constants.py`
  - [ ] `app/logging.py`
- [ ] tentukan versi Python target
- [ ] tentukan dependency awal minimal
- [ ] pastikan project bisa dijalankan minimal dengan server kosong

## Output akhir phase
- struktur repository sudah terbentuk
- server FastAPI bisa dijalankan
- file config dasar tersedia

---

## 5. Phase 1 — Core Configuration & App Bootstrap

## Tujuan
Menyiapkan aplikasi agar punya config, logging, dan bootstrap yang stabil.

## Task

### Config
- [ ] buat class config/settings
- [ ] baca env dari `.env`
- [ ] definisikan config:
  - [ ] host
  - [ ] port
  - [ ] data directory
  - [ ] log level
  - [ ] OpenRouter API key
  - [ ] base URL OpenRouter
  - [ ] default AI model
  - [ ] Whisper model
  - [ ] ffmpeg path
  - [ ] ffprobe path
  - [ ] yt-dlp path
  - [ ] auto cleanup
  - [ ] default language
  - [ ] default max candidates

### Logging
- [ ] setup structured logging sederhana
- [ ] buat app logger
- [ ] buat file logger untuk pipeline
- [ ] pastikan log bisa masuk ke console dan file

### App bootstrap
- [ ] setup FastAPI app instance
- [ ] setup CORS secukupnya untuk local
- [ ] setup static file serving
- [ ] setup root endpoint
- [ ] setup health endpoint
- [ ] setup basic error handler global

## Output akhir phase
- app bisa boot normal
- config terbaca
- logging berjalan
- health check tersedia

---

## 6. Phase 2 — Local Storage Foundation

## Tujuan
Menentukan dan mengimplementasikan storage strategy yang akan dipakai project.

## Task

### Direktori runtime
- [ ] pastikan app otomatis membuat folder:
  - [ ] `data/campaigns`
  - [ ] `data/assets`
  - [ ] `data/transcripts`
  - [ ] `data/candidates`
  - [ ] `data/exports`
  - [ ] `data/jobs`
  - [ ] `data/logs`
  - [ ] `data/temp`

### File manager
- [ ] buat helper file manager
- [ ] buat helper generate path campaign
- [ ] buat helper generate path asset
- [ ] buat helper generate path transcript
- [ ] buat helper generate path export
- [ ] buat helper sanitize filename
- [ ] buat helper cleanup temp files

### Hashing dan identity
- [ ] buat helper generate ID untuk:
  - [ ] campaign
  - [ ] asset
  - [ ] transcript
  - [ ] candidate
  - [ ] export
  - [ ] job
- [ ] buat helper file hash untuk deteksi source yang sama

## Output akhir phase
- semua folder runtime otomatis siap
- helper path management tersedia
- naming dasar rapi dan konsisten

---

## 7. Phase 3 — Database & Domain Model

## Tujuan
Menyiapkan metadata layer agar semua entitas penting bisa disimpan dengan stabil.

## Task

### Database
- [ ] pilih SQLite sebagai metadata store
- [ ] setup koneksi database
- [ ] buat initializer database
- [ ] buat script init DB
- [ ] buat migrasi sederhana atau bootstrap SQL awal

### Tabel utama
- [ ] buat tabel `campaigns`
- [ ] buat tabel `assets`
- [ ] buat tabel `transcripts`
- [ ] buat tabel `candidates`
- [ ] buat tabel `exports`
- [ ] buat tabel `jobs`
- [ ] buat tabel `audit_logs`

### Models
- [ ] buat model `Campaign`
- [ ] buat model `Asset`
- [ ] buat model `Transcript`
- [ ] buat model `CandidateClip`
- [ ] buat model `Export`
- [ ] buat model `Job`
- [ ] buat model `AuditLog`

### Repository layer
- [ ] buat `campaign_repo`
- [ ] buat `asset_repo`
- [ ] buat `transcript_repo`
- [ ] buat `candidate_repo`
- [ ] buat `export_repo`
- [ ] buat `job_repo`
- [ ] buat `audit_repo`

## Output akhir phase
- metadata bisa disimpan dan dibaca
- entitas utama sudah terdefinisi
- repository dasar tersedia

---

## 8. Phase 4 — State Machine & Validation Rules

## Tujuan
Mencegah workflow berantakan dengan state transition yang jelas.

## Task

### Definisikan state
- [ ] asset state:
  - [ ] `draft`
  - [ ] `ingesting`
  - [ ] `ready`
  - [ ] `transcribing`
  - [ ] `transcribed`
  - [ ] `analyzing`
  - [ ] `analyzed`
  - [ ] `review_ready`
  - [ ] `archived`
  - [ ] `failed`
- [ ] candidate state:
  - [ ] `suggested`
  - [ ] `needs_review`
  - [ ] `approved`
  - [ ] `rejected`
  - [ ] `exported`
- [ ] export state:
  - [ ] `queued`
  - [ ] `rendering`
  - [ ] `completed`
  - [ ] `failed`

### Validation rules
- [ ] asset tidak boleh dianalyze sebelum transcript siap
- [ ] candidate tidak boleh diexport sebelum approved
- [ ] source tanpa usage confirmation tidak boleh diproses
- [ ] asset invalid harus masuk state failed
- [ ] error transition harus jelas

### Implementasi
- [ ] buat utility state machine
- [ ] buat validator transition
- [ ] tulis unit test untuk transition

## Output akhir phase
- state workflow aman
- logic proses lebih mudah dijaga
- UI nanti lebih gampang dibangun

---

## 9. Phase 5 — Campaign CRUD

## Tujuan
Menyediakan fondasi data campaign yang akan menjadi container utama workflow.

## Task

### Schema API
- [ ] buat request schema create campaign
- [ ] buat response schema campaign detail
- [ ] buat schema patch campaign

### Service
- [ ] buat `campaign_service.create()`
- [ ] buat `campaign_service.list()`
- [ ] buat `campaign_service.get()`
- [ ] buat `campaign_service.update()`
- [ ] buat `campaign_service.delete()`

### Route
- [ ] buat endpoint:
  - [ ] `POST /api/campaigns`
  - [ ] `GET /api/campaigns`
  - [ ] `GET /api/campaigns/{id}`
  - [ ] `PATCH /api/campaigns/{id}`
  - [ ] `DELETE /api/campaigns/{id}`

### Validasi field
- [ ] validasi nama campaign
- [ ] validasi target platforms
- [ ] validasi target view threshold
- [ ] validasi notes panjang maksimum

## Output akhir phase
- user bisa buat dan kelola campaign
- campaign sudah bisa jadi parent untuk asset

---

## 10. Phase 6 — Asset Management

## Tujuan
Menangani source video dan metadata dasar sebelum pipeline dimulai.

## Task

### Asset schema
- [ ] buat schema create asset
- [ ] buat schema asset detail
- [ ] buat schema asset list item

### Asset fields
- [ ] source type
- [ ] source URL
- [ ] source filename
- [ ] influencer/source name
- [ ] rights basis
- [ ] usage confirmation
- [ ] language
- [ ] max candidates
- [ ] output presets

### Service
- [ ] buat `asset_service.create()`
- [ ] buat `asset_service.get()`
- [ ] buat `asset_service.list_by_campaign()`
- [ ] buat `asset_service.update()`
- [ ] buat `asset_service.delete()`

### Route
- [ ] `POST /api/campaigns/{id}/assets`
- [ ] `GET /api/assets/{id}`
- [ ] `PATCH /api/assets/{id}`
- [ ] `DELETE /api/assets/{id}`

### Rules
- [ ] asset tidak boleh dibuat tanpa rights basis
- [ ] asset tidak boleh diproses tanpa usage confirmation
- [ ] language default ikut settings jika kosong

## Output akhir phase
- user bisa tambah asset ke campaign
- metadata asset sudah lengkap untuk pipeline

---

## 11. Phase 7 — Upload & Ingest Pipeline

## Tujuan
Memindahkan file source ke storage lokal dan membaca metadata video.

## Task

### Upload / ingest
- [ ] dukung upload file lokal
- [ ] dukung source URL approved
- [ ] copy file ke workspace
- [ ] download source via yt-dlp jika URL digunakan
- [ ] validasi extension file
- [ ] validasi file exists
- [ ] validasi ukuran file

### Metadata video
- [ ] integrasi ffprobe
- [ ] ambil:
  - [ ] durasi
  - [ ] resolusi
  - [ ] codec
  - [ ] fps
  - [ ] audio stream availability

### Job system dasar
- [ ] buat job record saat ingest dimulai
- [ ] update progress ingest
- [ ] tandai success/failure

### Logging
- [ ] simpan log ingest per asset

## Output akhir phase
- video source masuk ke storage lokal
- metadata video terbaca
- asset status menjadi `ready`

---

## 12. Phase 8 — Transcript Pipeline

## Tujuan
Menghasilkan transcript yang menjadi basis semua analisis dan subtitle.

## Task

### Audio extraction
- [ ] ekstrak audio ke `.wav`
- [ ] normalisasi audio bila perlu
- [ ] cek sample rate yang sesuai untuk Whisper

### Whisper runner
- [ ] integrasikan Whisper lokal
- [ ] pilih model dari config
- [ ] tangani bahasa default / auto detect
- [ ] simpan hasil raw

### Output transcript
- [ ] simpan `transcript.txt`
- [ ] simpan `transcript.json`
- [ ] simpan `words.json` bila ada
- [ ] simpan `.srt`
- [ ] simpan metadata transcript ke DB

### Endpoint
- [ ] `POST /api/assets/{id}/transcribe`
- [ ] `GET /api/assets/{id}/transcript`

### Optimasi
- [ ] cache transcript jika source hash sama
- [ ] jangan transcribe ulang jika sudah ada dan user belum force rerun

## Output akhir phase
- transcript tersedia
- transcript file tersimpan rapi
- asset status menjadi `transcribed`

---

## 13. Phase 9 — Transcript Viewer & Search

## Tujuan
Membuat transcript benar-benar berguna untuk review manual.

## Task

### Transcript viewer backend
- [ ] parse transcript segments
- [ ] endpoint transcript detail
- [ ] endpoint transcript search
- [ ] support keyword search
- [ ] support timestamp jump

### Frontend
- [ ] panel transcript viewer
- [ ] tampilkan transcript per segment
- [ ] highlight hasil search
- [ ] klik timestamp untuk lompat preview
- [ ] tampilkan bagian transcript yang terkait candidate

### Route
- [ ] `GET /api/assets/{id}/transcript/search?q=...`
- [ ] optional `POST /api/assets/{id}/transcript/import`

## Output akhir phase
- transcript bisa dicari
- user bisa review manual lebih cepat
- transcript tidak hanya jadi artifact pasif

---

## 14. Phase 10 — AI Analysis Foundation

## Tujuan
Menyusun integrasi AI yang fokus pada candidate suggestion, bukan auto-final.

## Task

### OpenRouter client
- [ ] buat wrapper client OpenRouter
- [ ] support model default
- [ ] support override model per request
- [ ] timeout handling
- [ ] retry ringan
- [ ] error parsing

### Prompt files
- [ ] buat prompt `candidate_segments`
- [ ] buat prompt `hook_assist`
- [ ] buat prompt schema JSON
- [ ] buat prompt guardrail tech
- [ ] buat prompt guardrail finance

### Output schema
- [ ] definisikan schema candidate result:
  - [ ] start
  - [ ] end
  - [ ] reason
  - [ ] confidence
  - [ ] hook
  - [ ] title
  - [ ] CTA
  - [ ] tags

### Validation
- [ ] validasi candidate duration minimum
- [ ] validasi duration maximum
- [ ] validasi start < end
- [ ] validasi overlap berlebihan
- [ ] validasi data mandatory

## Output akhir phase
- integrasi AI siap
- prompt dasar siap
- schema hasil AI jelas

---

## 15. Phase 11 — Candidate Generation Pipeline

## Tujuan
Menghasilkan candidate clips dari transcript + brief campaign.

## Task

### Pipeline logic
- [ ] baca transcript
- [ ] baca metadata campaign
- [ ] baca metadata asset
- [ ] susun payload ke AI
- [ ] kirim request AI
- [ ] parse response
- [ ] validasi schema
- [ ] normalisasi timestamp
- [ ] simpan candidate ke DB
- [ ] simpan analysis output raw ke file

### Candidate persistence
- [ ] buat candidate records
- [ ] default state `suggested`
- [ ] simpan reason
- [ ] simpan suggested hook
- [ ] simpan suggested title
- [ ] simpan suggested CTA
- [ ] simpan tags

### Endpoint
- [ ] `POST /api/assets/{id}/analyze`
- [ ] `GET /api/assets/{id}/candidates`

### Error handling
- [ ] tangani AI timeout
- [ ] tangani schema invalid
- [ ] tangani empty results
- [ ] tangani transcript kosong

## Output akhir phase
- candidate list bisa dihasilkan otomatis
- candidate tersimpan dan siap direview

---

## 16. Phase 12 — Manual Candidate Support

## Tujuan
Karena AI tidak selalu bagus, user harus bisa membuat candidate manual.

## Task

- [ ] buat endpoint `POST /api/assets/{id}/candidates/manual`
- [ ] user bisa isi:
  - [ ] start
  - [ ] end
  - [ ] title
  - [ ] CTA
  - [ ] notes
- [ ] tandai source candidate:
  - [ ] `ai`
  - [ ] `manual`
- [ ] validasi durasi manual clip
- [ ] tampilkan candidate manual di review list

## Output akhir phase
- user tidak tergantung penuh ke AI
- workflow tetap fleksibel saat suggestion AI kurang baik

---

## 17. Phase 13 — Candidate Review Workflow

## Tujuan
Membuat candidate clip menjadi unit kerja utama yang bisa dikontrol manusia.

## Task

### Review actions
- [ ] approve candidate
- [ ] reject candidate
- [ ] mark needs review
- [ ] update notes
- [ ] edit title
- [ ] edit hook
- [ ] edit CTA
- [ ] edit tags
- [ ] edit start/end

### Endpoint
- [ ] `GET /api/candidates/{id}`
- [ ] `PATCH /api/candidates/{id}`
- [ ] `PATCH /api/candidates/{id}/approve`
- [ ] `PATCH /api/candidates/{id}/reject`
- [ ] `PATCH /api/candidates/{id}/needs-review`

### Rules
- [ ] simpan `approved_at`
- [ ] simpan `rejected_at`
- [ ] simpan manual override timestamp
- [ ] audit log setiap perubahan penting

## Output akhir phase
- user punya kontrol nyata atas candidate
- human-in-the-loop benar-benar terimplementasi

---

## 18. Phase 14 — Preview Clip Generation

## Tujuan
Memberi preview cepat sebelum export final.

## Task

### Preview generation
- [ ] buat fungsi render preview low-res
- [ ] gunakan timestamp candidate
- [ ] hasilkan file preview ringan
- [ ] simpan lokasi preview
- [ ] regenerate preview jika timestamp diubah

### Endpoint
- [ ] `GET /api/candidates/{id}/preview`
- [ ] atau gunakan `stream` dari file preview

### Frontend
- [ ] player preview
- [ ] tombol play/pause
- [ ] tampilkan duration
- [ ] tampilkan metadata candidate di samping player

## Output akhir phase
- setiap candidate bisa dipreview
- review lebih cepat sebelum export final

---

## 19. Phase 15 — Subtitle System

## Tujuan
Mengubah transcript menjadi subtitle yang siap dipakai untuk export.

## Task

### Subtitle generation
- [ ] buat helper SRT generator
- [ ] potong subtitle sesuai range candidate
- [ ] offset timestamp subtitle relatif ke clip
- [ ] simpan subtitle per candidate jika perlu

### Styling
- [ ] tentukan default subtitle style
- [ ] tentukan font fallback
- [ ] tentukan outline/shadow
- [ ] tentukan margin bawah aman

### Mode subtitle
- [ ] subtitle external
- [ ] subtitle burn-in

## Output akhir phase
- subtitle usable untuk candidate clip
- siap dipakai saat final render

---

## 20. Phase 16 — Final Export Pipeline

## Tujuan
Mengekspor clip final yang sudah disetujui.

## Task

### Rules
- [ ] hanya candidate `approved` yang boleh diexport
- [ ] gunakan effective timestamps hasil edit manual jika ada
- [ ] metadata export wajib tersimpan

### Preset output
- [ ] `9:16`
- [ ] `1:1`
- [ ] `4:5`
- [ ] `original`

### Reframe modes
- [ ] `none`
- [ ] `center`
- [ ] `face_track` placeholder dulu bila belum final

### Export action
- [ ] render final via ffmpeg
- [ ] subtitle on/off
- [ ] simpan `.mp4`
- [ ] simpan metadata `.json`
- [ ] simpan `.srt` bila diminta

### Endpoint
- [ ] `POST /api/candidates/{id}/exports`
- [ ] `GET /api/exports/{id}`
- [ ] `GET /api/exports/{id}/download`
- [ ] `GET /api/exports/{id}/stream`

### State update
- [ ] export state `queued`
- [ ] export state `rendering`
- [ ] export state `completed`
- [ ] export state `failed`
- [ ] candidate bisa berubah ke `exported` saat final selesai

## Output akhir phase
- candidate approved bisa jadi file final
- hasil export bisa diunduh dan diputar

---

## 21. Phase 17 — Dashboard & Frontend Shell

## Tujuan
Membuat shell UI yang benar-benar bisa dipakai.

## Task

### Layout
- [ ] buat `index.html`
- [ ] buat layout dashboard utama
- [ ] buat sidebar / navigation sederhana
- [ ] buat panel utama konten

### State frontend
- [ ] buat API helper JS
- [ ] buat state manager ringan
- [ ] buat loading state
- [ ] buat toast/error message sederhana

### Component awal
- [ ] campaign list
- [ ] campaign form
- [ ] asset upload form
- [ ] transcript viewer
- [ ] candidate list
- [ ] candidate editor
- [ ] preview player
- [ ] export panel
- [ ] settings panel

## Output akhir phase
- UI dasar usable
- semua modul backend mulai terhubung ke frontend

---

## 22. Phase 18 — Jobs, Queue, dan Progress Tracking

## Tujuan
Karena proses berat berjalan async, user perlu melihat progress yang jelas.

## Task

### Job system
- [ ] buat tabel jobs benar-benar dipakai
- [ ] setiap proses berat membuat job
- [ ] update progress per step
- [ ] update message yang manusiawi

### Queue
- [ ] buat queue sederhana in-memory / persisted ringan
- [ ] satu job berat per waktu
- [ ] job kecil bisa menunggu antrean

### SSE / event stream
- [ ] endpoint event global
- [ ] endpoint event per campaign
- [ ] push progress update ke UI

### UI progress
- [ ] tampilkan running jobs
- [ ] tampilkan progress bar
- [ ] tampilkan current step
- [ ] tampilkan last error

## Output akhir phase
- user tahu proses sedang di tahap mana
- experience local app jadi jauh lebih enak

---

## 23. Phase 19 — Settings & Operational Controls

## Tujuan
Memberikan kontrol agar app bisa dipakai fleksibel sesuai PC dan workflow user.

## Task

### Settings fields
- [ ] default AI model
- [ ] Whisper model
- [ ] workspace directory
- [ ] cleanup policy
- [ ] preview quality
- [ ] default output presets
- [ ] default max candidates
- [ ] default language

### Settings backend
- [ ] `GET /api/settings`
- [ ] `PATCH /api/settings`

### Settings frontend
- [ ] form settings
- [ ] save settings
- [ ] validate input settings

## Output akhir phase
- app bisa disesuaikan tanpa edit file manual terus-menerus

---

## 24. Phase 20 — Audit Log & History

## Tujuan
Menyimpan jejak perubahan agar workflow lebih bisa ditelusuri.

## Task

### Audit
- [ ] log create/update/delete campaign
- [ ] log add/delete asset
- [ ] log transcribe start/end
- [ ] log analyze start/end
- [ ] log candidate approve/reject/edit
- [ ] log export start/end

### History UI
- [ ] tampilkan activity log per campaign
- [ ] tampilkan export history
- [ ] tampilkan last updated timestamps

## Output akhir phase
- perubahan bisa ditracking
- debugging dan review lebih mudah

---

## 25. Phase 21 — Error Handling & Recovery

## Tujuan
Membuat app kuat untuk penggunaan harian, bukan hanya demo.

## Task

### Tangani error utama
- [ ] source file invalid
- [ ] unsupported format
- [ ] download gagal
- [ ] ffmpeg missing
- [ ] Whisper gagal load
- [ ] AI timeout
- [ ] JSON AI invalid
- [ ] subtitle gagal
- [ ] render gagal
- [ ] disk penuh

### Recovery tools
- [ ] retry analyze
- [ ] retry render
- [ ] force re-transcribe
- [ ] force regenerate preview
- [ ] cleanup orphan temp files

### UI messages
- [ ] tampilkan error manusiawi
- [ ] tampilkan possible fix
- [ ] tampilkan step yang gagal

## Output akhir phase
- app lebih tahan dipakai real-world
- user tidak bingung saat error terjadi

---

## 26. Phase 22 — Performance Pass

## Tujuan
Mengurangi delay yang tidak perlu di local machine.

## Task

### Optimasi ringan
- [ ] cache transcript
- [ ] cache analysis output
- [ ] preview low resolution
- [ ] lazy load candidate preview
- [ ] batasi preview generation bersamaan
- [ ] gunakan temp directory terpisah
- [ ] pastikan file cleanup berjalan

### Render optimization
- [ ] preset cepat untuk preview
- [ ] preset kualitas untuk final
- [ ] hindari burn subtitle saat preview jika tidak perlu

## Output akhir phase
- aplikasi terasa lebih ringan
- resource lokal lebih terkendali

---

## 27. Phase 23 — Security & Safety Pass

## Tujuan
Walaupun lokal, aplikasi tetap harus aman secara dasar.

## Task

- [ ] simpan API key hanya di env/config
- [ ] sanitasi nama file upload
- [ ] hindari command injection
- [ ] gunakan subprocess aman
- [ ] validasi URL input
- [ ] validasi file type upload
- [ ] jangan expose folder sensitif sembarangan
- [ ] tampilkan legal note di UI ingest
- [ ] wajibkan usage confirmation sebelum process

## Output akhir phase
- local app lebih aman dan disiplin
- risiko misuse lebih kecil

---

## 28. Phase 24 — Testing

## Tujuan
Menjaga kualitas sistem sebelum dianggap siap dipakai harian.

## Task

### Unit tests
- [ ] config loader
- [ ] ID generator
- [ ] file sanitizer
- [ ] state machine
- [ ] candidate validator
- [ ] naming convention helper
- [ ] subtitle offset helper

### Integration tests
- [ ] create campaign
- [ ] add asset
- [ ] ingest mock
- [ ] transcribe mock
- [ ] analyze mock
- [ ] approve candidate
- [ ] export candidate

### Manual QA checklist
- [ ] buat campaign berhasil
- [ ] tambah asset berhasil
- [ ] upload file berhasil
- [ ] transcript muncul
- [ ] candidate muncul
- [ ] preview berjalan
- [ ] approve/reject berjalan
- [ ] export berjalan
- [ ] hasil video bisa diputar
- [ ] subtitle sinkron
- [ ] log terbaca
- [ ] error ditampilkan dengan jelas

## Output akhir phase
- confidence project meningkat
- bug besar bisa ditangkap sebelum dipakai rutin

---

## 29. Phase 25 — Documentation & Ready-to-Use Pass

## Tujuan
Menjadikan project benar-benar nyaman digunakan sendiri.

## Task

### README
- [ ] cara install dependency
- [ ] cara setup `.env`
- [ ] cara install ffmpeg
- [ ] cara install yt-dlp
- [ ] cara install Whisper dependencies
- [ ] cara run app
- [ ] cara troubleshoot error umum

### Internal docs
- [ ] update `PRD.md` bila perlu
- [ ] sinkronkan `TEKNIKAL.md`
- [ ] dokumentasikan struktur folder runtime
- [ ] dokumentasikan state machine singkat
- [ ] dokumentasikan endpoint utama

### Scripts
- [ ] script init DB
- [ ] script run dev
- [ ] script cleanup temp
- [ ] script reindex files bila diperlukan

## Output akhir phase
- project lebih mudah dipasang ulang
- project siap dipakai sebagai tool pribadi

---

## 30. Prioritas Implementasi Nyata

Kalau kamu mulai besok, urutan kerja yang paling masuk akal adalah:

### Batch 1 — Fondasi
- [ ] phase 0
- [ ] phase 1
- [ ] phase 2
- [ ] phase 3
- [ ] phase 4

### Batch 2 — Data Workflow
- [ ] phase 5
- [ ] phase 6
- [ ] phase 7
- [ ] phase 8
- [ ] phase 9

### Batch 3 — AI & Candidate
- [ ] phase 10
- [ ] phase 11
- [ ] phase 12
- [ ] phase 13
- [ ] phase 14

### Batch 4 — Output
- [ ] phase 15
- [ ] phase 16

### Batch 5 — Usability
- [ ] phase 17
- [ ] phase 18
- [ ] phase 19
- [ ] phase 20
- [ ] phase 21

### Batch 6 — Stabilization
- [ ] phase 22
- [ ] phase 23
- [ ] phase 24
- [ ] phase 25

---

## 31. Milestone Praktis

## Milestone A — App bisa hidup
Selesai jika:
- server jalan
- config jalan
- DB jalan
- campaign CRUD jalan

## Milestone B — Asset bisa diproses
Selesai jika:
- upload asset jalan
- ffprobe jalan
- transcript berhasil dibuat

## Milestone C — Candidate muncul
Selesai jika:
- AI analysis jalan
- candidate tersimpan
- transcript viewer tersedia

## Milestone D — Review usable
Selesai jika:
- preview clip ada
- approve/reject ada
- edit timestamp ada

## Milestone E — Final output usable
Selesai jika:
- approved candidate bisa diexport
- subtitle bisa diburn
- output bisa diputar dan didownload

## Milestone F — Siap dipakai harian
Selesai jika:
- history ada
- logs jelas
- settings usable
- error handling cukup baik
- dokumentasi cukup lengkap

---

## 32. Catatan Penting Selama Implementasi

- Jangan buat AI terlalu dominan; posisi AI hanya pembantu.
- Jangan buru-buru membuat fitur upload otomatis ke platform.
- Jangan gabungkan semua logic ke route; simpan di service layer.
- Jangan biarkan state berubah tanpa validasi.
- Jangan render final sebelum preview/review flow nyaman.
- Jangan abaikan logging; project seperti ini sangat butuh log jelas.
- Jangan anggap transcript pasti sempurna; selalu sediakan jalur review manual.

---

## 33. Estimasi Kompleksitas

Secara jujur, project ini memang **lumayan kompleks** karena menggabungkan:

- backend API,
- file processing,
- AI integration,
- video rendering,
- async jobs,
- dan review workflow.

Tapi kompleksitasnya masih **sangat masuk akal** jika dibangun modular.

### Bagian paling mudah
- campaign CRUD
- asset CRUD
- settings
- basic frontend shell

### Bagian paling sedang
- transcript viewer
- candidate review flow
- preview system
- subtitle generation

### Bagian paling rawan / berat
- ffmpeg pipeline
- Whisper processing di local PC
- AI output validation
- async jobs dan progress tracking
- reframe / face tracking

---

## 34. Rekomendasi Pengerjaan Nyata

Kalau kamu ingin menjaga momentum, saya sarankan pola kerja begini:

### Sprint 1
- setup app
- config
- DB
- campaign CRUD
- asset CRUD

### Sprint 2
- ingest
- ffprobe
- transcript pipeline
- transcript storage

### Sprint 3
- OpenRouter integration
- candidate generation
- candidate persistence

### Sprint 4
- transcript viewer
- review panel
- preview generation

### Sprint 5
- export final
- subtitle burn-in
- output presets

### Sprint 6
- jobs/progress
- settings
- logs
- cleanup
- testing

---

## 35. Penutup

Ya, benar: **project ini lumayan complex**.
Tapi kompleksitasnya bukan berarti buruk — justru karena workflow yang kamu inginkan memang sudah mendekati tool produksi sungguhan, bukan sekadar demo kecil.

Dengan tasklist ini, kamu sekarang punya:

- jalur implementasi yang jelas,
- prioritas yang lebih rapi,
- pembagian fase yang realistis,
- dan checklist yang bisa langsung dicentang satu per satu.

Kalau nanti dibutuhkan, tasklist ini bisa dipecah lagi menjadi:

- `TASKLIST_BACKEND.md`
- `TASKLIST_FRONTEND.md`
- `TASKLIST_FFMPEG.md`
- `TASKLIST_AI.md`

agar pengerjaannya makin fokus.
