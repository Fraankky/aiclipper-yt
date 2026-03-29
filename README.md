# AI Clipper App

AI-powered video clipping tool. Input video panjang → otomatis klip pendek siap pakai untuk TikTok/Reels/Shorts.

Pipeline architecture adopted from [ai-clipper-id](https://github.com/kira-id/ai-clipper-id) + **Layout Mode System**.

## Features

- 🎬 **Auto Transcription** — faster-whisper (GPU/CPU auto, VAD, batched, word_timestamps)
- 🧠 **AI Clip Extraction** — LLM analyzes transcript, auto-decides best clips (max 72)
- 🇮🇩 **Indonesian Optimized** — noise/filler/duplicate filter tuned for Bahasa Indonesia
- 📊 **Smart Scoring** — 5 dimensions: hook, insight, retention, emotion, clarity
- 📱 **Layout Mode System** — original, letterbox, center_crop_9_16, gaussian_blur, auto_magic
- 💬 **ASS Karaoke Subtitles** — word-by-word highlight with `\kf` tag
- 🔌 **Multi-LLM** — OpenRouter (free), Anthropic, OpenAI, Ollama
- ⚡ **Caching** — transcript & clips cached, skip re-processing on re-run

## Quick Start

```bash
# Install
pip install faster-whisper openai anthropic requests opencv-python-headless

# (Optional) GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Set API key
export OPENROUTER_API_KEY=sk-...

# Run
python main.py video.mp4
python main.py video.mp4 --model large-v3 --layout gaussian_blur
python main.py video.mp4 --min 15 --max 90 --max-clips 50
```

## Project Structure

```
aiclip-app/
├── app/
│   ├── cli.py              # CLI orchestration
│   ├── transcription.py    # faster-whisper wrapper
│   ├── prefilter.py        # noise/duplicate/music filter
│   ├── extraction.py       # ffmpeg clip extraction
│   ├── postprocess.py      # subtitle + title + layout mode
│   ├── subtitles.py        # ASS karaoke generation
│   ├── layout.py           # Layout Mode System (5 modes)
│   ├── utils.py            # logging, constants, ffmpeg detection
│   ├── llm/
│   │   ├── backends.py     # OpenRouter, Anthropic, OpenAI, Ollama
│   │   ├── analysis.py     # clip finding, chunking, scoring
│   │   ├── fix_clips.py    # translate, dedup, caption fix
│   │   └── prompts.py      # prompt templates
│   ├── api/                # FastAPI routes (web interface)
│   ├── core/               # database, config
│   ├── models/             # SQLAlchemy models
│   ├── services/           # business logic
│   └── workers/            # background jobs
├── clips/                  # Output clips
├── docs/
│   ├── PRD.md
│   ├── TEKNIKAL.md
│   ├── TASKLIST.md
│   └── prompts.md
├── main.py
├── requirements.txt
└── pyproject.toml
```

## Output

```
clips/{video_stem}/
├── clips.json               # Metadata (rank, score, hook, caption, topic, title)
├── rank01_Title.mp4         # Raw clip
└── rank01_Title_final.mp4   # Post-processed (subtitle + layout)
```

## CLI Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `video` | required | Input video path |
| `--model` | turbo | Whisper model (tiny/base/small/medium/large-v3/turbo) |
| `--lang` | id | Language (id/en/none=auto) |
| `--min` | 15 | Min clip duration (seconds) |
| `--max` | 180 | Max clip duration (seconds) |
| `--max-clips` | 72 | Max number of clips |
| `--min-score` | 55 | Min clip_score to keep |
| `--layout` | original | Layout mode |
| `--subtitles/--no-subtitles` | on | ASS subtitles |
| `--subtitle-position` | lower | Subtitle position (center/upper/lower) |
| `--output` | clips | Output directory |

## LLM Backend Priority

1. OpenRouter (`OPENROUTER_API_KEY`) — default free model
2. Anthropic (`ANTHROPIC_API_KEY`)
3. OpenAI (`OPENAI_API_KEY`)
4. Ollama (local, no key)

## Scoring

```
clip_score = hook×0.30 + insight×0.25 + retention×0.20 + emotion×0.15 + clarity×0.10
```

## Docs

- `docs/PRD.md` — Product requirements
- `docs/TEKNIKAL.md` — Technical design
- `docs/TASKLIST.md` — Implementation phases
- `docs/prompts.md` — LLM prompt templates

## License

Internal project.
