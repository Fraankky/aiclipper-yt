#!/usr/bin/env python3
"""
AI Clipper App — CLI entry point.

Usage:
  python main.py video.mp4
  python main.py video.mp4 --model large-v3
  python main.py video.mp4 --layout gaussian_blur
  OPENROUTER_API_KEY=sk-... python main.py video.mp4
"""

from app.cli import main

if __name__ == "__main__":
    main()
