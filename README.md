# AIClip App

Backend service untuk workflow **AI Campaign Clip** berbasis FastAPI.

## Status

Project ini masih tahap awal (Phase 0: Project Initialization).
Saat ini fokus pada fondasi struktur repository, konfigurasi dasar, dan bootstrap server.

## Tech Stack (awal)

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic + pydantic-settings
- Ruff (lint + format)

## Struktur Direktori

```/dev/null/tree.txt#L1-24
aiclip-app/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── schemas/
│   ├── core/
│   ├── models/
│   ├── prompts/
│   ├── repositories/
│   ├── services/
│   ├── workers/
│   ├── config.py
│   ├── constants.py
│   ├── logging.py
│   └── main.py
├── data/
├── docs/
├── scripts/
├── static/
│   └── assets/
├── tests/
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## Prerequisites

- Python **3.14** ter-install
- `pip` aktif
- (Opsional) virtual environment (`.venv`)

## Setup Lokal

1. Buat virtual environment:

```/dev/null/setup.sh#L1-1
python -m venv .venv
```

2. Aktifkan virtual environment:

```/dev/null/activate.sh#L1-2
# macOS/Linux
source .venv/bin/activate
```

```/dev/null/activate.ps1#L1-2
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```/dev/null/install.sh#L1-1
pip install -r requirements.txt
```

4. Buat file environment dari template:

```/dev/null/env-copy.sh#L1-1
cp .env.example .env
```

> Di Windows CMD bisa pakai:
> `copy .env.example .env`

## Menjalankan Server

Jalankan FastAPI dev server:

```/dev/null/run.sh#L1-1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Endpoint Dasar

Setelah server hidup:

- Root: `GET /`
- Health: `GET /health`
- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`

Contoh cek health:

```/dev/null/curl.sh#L1-1
curl http://127.0.0.1:8000/health
```

Expected response:

```/dev/null/health.json#L1-3
{
  "status": "ok"
}
```

## Lint & Format

Project menggunakan Ruff via `pyproject.toml`.

- Cek lint:

```/dev/null/lint.sh#L1-1
ruff check .
```

- Auto-fix lint issues:

```/dev/null/lint-fix.sh#L1-1
ruff check . --fix
```

- Format code:

```/dev/null/format.sh#L1-1
ruff format .
```

## Konfigurasi Environment

Variabel awal tersedia di `.env.example`, termasuk:

- App (`APP_*`)
- API (`API_PREFIX`, `CORS_ALLOW_ORIGINS`)
- Database (`DATABASE_URL`)
- Storage (`DATA_DIR`, `STATIC_DIR`, `ASSETS_DIR`)
- AI provider (`OPENROUTER_*`)
- Pipeline (`FFMPEG_BIN`, `WHISPER_MODEL`, dll)
- Worker (`JOB_*`)
- Security (`SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`)

> Untuk production, wajib ganti nilai sensitif seperti `SECRET_KEY`.

## Roadmap Implementasi

Rencana implementasi detail ada di:

- `docs/TASKLIST.md`

## Catatan

- README ini adalah starter docs.
- Akan terus diupdate seiring progres phase berikutnya (config, database, workflow, AI pipeline, dan UI).
