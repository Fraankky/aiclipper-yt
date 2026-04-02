import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_video_path(temp_dir):
    """Create a dummy video file for testing."""
    video_file = temp_dir / "test_video.mp4"
    video_file.touch()  # Create empty file
    return str(video_file)


@pytest.fixture
def sample_transcript_segments():
    """Sample transcript segments for testing."""
    return [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.5,
            "text": "Halo selamat datang di channel ini",
            "tokens": [123, 456, 789],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.1,
            "words": [
                {"word": "Halo", "start": 0.0, "end": 0.5, "probability": 0.9},
                {"word": "selamat", "start": 0.5, "end": 1.0, "probability": 0.8},
                {"word": "datang", "start": 1.0, "end": 1.5, "probability": 0.85},
                {"word": "di", "start": 1.5, "end": 1.7, "probability": 0.9},
                {"word": "channel", "start": 1.7, "end": 2.2, "probability": 0.8},
                {"word": "ini", "start": 2.2, "end": 2.5, "probability": 0.85},
            ],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 3.0,
            "end": 5.5,
            "text": "Video ini akan membahas tutorial editing",
            "tokens": [234, 567, 890],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
            "words": [
                {"word": "Video", "start": 3.0, "end": 3.3, "probability": 0.9},
                {"word": "ini", "start": 3.3, "end": 3.5, "probability": 0.85},
                {"word": "akan", "start": 3.5, "end": 3.8, "probability": 0.9},
                {"word": "membahas", "start": 3.8, "end": 4.3, "probability": 0.8},
                {"word": "tutorial", "start": 4.3, "end": 4.9, "probability": 0.85},
                {"word": "editing", "start": 4.9, "end": 5.5, "probability": 0.9},
            ],
        },
    ]


@pytest.fixture
def sample_clips_data():
    """Sample clips data for testing."""
    return [
        {
            "start": 0.0,
            "end": 5.0,
            "title": "Pembukaan Video",
            "topic": "Pengantar",
            "caption": "Video pembuka yang menarik",
            "clip_score": 85,
            "score_hook": 9,
            "score_insight_density": 8,
            "score_retention": 9,
            "score_emotional_payoff": 7,
            "score_clarity": 10,
            "rank": 1,
        },
        {
            "start": 10.0,
            "end": 18.0,
            "title": "Tips Editing",
            "topic": "Tutorial Editing",
            "caption": "Tips mudah untuk editing video",
            "clip_score": 78,
            "score_hook": 8,
            "score_insight_density": 7,
            "score_retention": 8,
            "score_emotional_payoff": 6,
            "score_clarity": 9,
            "rank": 2,
        },
    ]
