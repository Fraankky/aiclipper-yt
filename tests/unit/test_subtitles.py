"""
Unit tests for subtitles module.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.subtitles import _rgb_to_ass, _seconds_to_ass_time, _group_words, get_clip_words


def test_rgb_to_ass():
    """Test RGB to ASS color conversion."""
    # Test basic RGB conversion (note: ASS format is &HAABBGGRR)
    assert _rgb_to_ass(255, 0, 0) == "&H000000FF"  # Red: Alpha=00, Blue=00, Green=00, Red=FF
    assert _rgb_to_ass(0, 255, 0) == "&H0000FF00"  # Green: Alpha=00, Blue=00, Green=FF, Red=00
    assert _rgb_to_ass(0, 0, 255) == "&H00FF0000"  # Blue: Alpha=00, Blue=FF, Green=00, Red=00

    # Test with alpha
    assert (
        _rgb_to_ass(255, 255, 255, 128) == "&H80FFFFFF"
    )  # White with 50% alpha: Alpha=80, Blue=FF, Green=FF, Red=FF
    assert _rgb_to_ass(0, 0, 0, 0) == "&H00000000"  # Transparent black
    assert (
        _rgb_to_ass(0, 0, 0, 255) == "&HFF000000"
    )  # Opaque black: Alpha=FF, Blue=00, Green=00, Red=00

    # Verify constants from the actual file
    from app.subtitles import COLOR_HIGHLIGHT, COLOR_NORMAL, COLOR_OUTLINE, COLOR_SHADOW

    assert COLOR_HIGHLIGHT == "&H0035E1FF"  # Yellow (255,225,53)
    assert COLOR_NORMAL == "&H00FFFFFF"  # White (255,255,255)
    assert COLOR_OUTLINE == "&H00000000"  # Black outline (0,0,0)
    assert COLOR_SHADOW == "&H50000000"  # Subtle shadow (0,0,0,80)


def test_seconds_to_ass_time():
    """Test seconds to ASS time conversion."""
    # Test basic conversions
    assert _seconds_to_ass_time(0) == "0:00:00.00"
    assert _seconds_to_ass_time(1) == "0:00:01.00"
    assert _seconds_to_ass_time(60) == "0:01:00.00"
    assert _seconds_to_ass_time(3600) == "1:00:00.00"
    assert _seconds_to_ass_time(3661) == "1:01:01.00"

    # Test fractional seconds
    assert _seconds_to_ass_time(1.5) == "0:00:01.50"
    assert _seconds_to_ass_time(1.05) == "0:00:01.05"
    # Note: 1.005 due to floating point precision formats as 1.00, not 1.01
    assert _seconds_to_ass_time(1.005) == "0:00:01.00"

    # Test edge cases
    assert _seconds_to_ass_time(-1) == "0:00:00.00"  # Negative becomes 0
    assert _seconds_to_ass_time(0.001) == "0:00:00.00"  # Very small rounds to 0


def test_group_words_empty():
    """Test word grouping with empty list."""
    assert _group_words([]) == []


def test_group_words_single_word():
    """Test word grouping with single word."""
    words = [{"word": "Hello", "start": 0.0, "end": 0.5}]
    result = _group_words(words)
    assert len(result) == 1
    assert result[0] == words


def test_group_words_within_limits():
    """Test word grouping when all words fit in one group."""
    words = [
        {"word": "Hello", "start": 0.0, "end": 0.5},
        {"word": "world", "start": 0.5, "end": 1.0},
        {"word": "test", "start": 1.0, "end": 1.5},
    ]
    result = _group_words(words, max_words=10, max_duration=10.0, max_gap=2.0)
    assert len(result) == 1
    assert len(result[0]) == 3
    assert result[0] == words


def test_group_words_split_by_max_words():
    """Test word grouping splits when max_words exceeded."""
    words = [
        {"word": f"Word{i}", "start": i * 0.5, "end": (i * 0.5) + 0.5}
        for i in range(10)  # 10 words
    ]
    result = _group_words(words, max_words=3, max_duration=10.0, max_gap=2.0)
    assert len(result) == 4  # 3+3+3+1 = 10 words
    assert len(result[0]) == 3
    assert len(result[1]) == 3
    assert len(result[2]) == 3
    assert len(result[3]) == 1


def test_group_words_split_by_max_duration():
    """Test word grouping splits when max_duration exceeded."""
    words = [
        {"word": "Word1", "start": 0.0, "end": 1.0},
        {"word": "Word2", "start": 1.0, "end": 2.0},
        {"word": "Word3", "start": 2.0, "end": 3.0},
        {"word": "Word4", "start": 3.0, "end": 4.0},  # This would make duration 4.0 > 3.0
    ]
    result = _group_words(words, max_words=10, max_duration=3.0, max_gap=2.0)
    assert len(result) == 2
    assert len(result[0]) == 3  # First three words (duration 3.0)
    assert len(result[1]) == 1  # Last word


def test_group_words_split_by_max_gap():
    """Test word grouping splits when max_gap exceeded."""
    words = [
        {"word": "Word1", "start": 0.0, "end": 0.5},
        {"word": "Word2", "start": 0.5, "end": 1.0},  # 0.0 gap
        {"word": "Word3", "start": 2.0, "end": 2.5},  # 1.0 gap > 0.6
        {"word": "Word4", "start": 2.5, "end": 3.0},  # 0.0 gap
    ]
    result = _group_words(words, max_words=10, max_duration=10.0, max_gap=0.6)
    assert len(result) == 2
    assert len(result[0]) == 2  # First two words
    assert len(result[1]) == 2  # Last two words


def test_get_clip_words_empty_segments():
    """Test get_clip_words with empty segments."""
    result = get_clip_words([], 0.0, 10.0)
    assert result == []


def test_get_clip_words_no_match():
    """Test get_clip_words when no words match clip range."""
    segments = [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "First segment",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5},
                {"word": "world", "start": 0.5, "end": 1.0},
            ],
        }
    ]
    result = get_clip_words(segments, 10.0, 20.0)  # Outside range
    assert result == []


def test_get_clip_words_partial_match():
    """Test get_clip_words with partial segment overlap."""
    segments = [
        {
            "start": 0.0,
            "end": 10.0,
            "text": "Hello world this is a test",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5},
                {"word": "world", "start": 0.5, "end": 1.0},
                {"word": "this", "start": 1.0, "end": 1.5},
                {"word": "is", "start": 1.5, "end": 2.0},
                {"word": "a", "start": 2.0, "end": 2.5},
                {"word": "test", "start": 2.5, "end": 3.0},
                {"word": "extra", "start": 5.0, "end": 5.5},
                {"word": "words", "start": 5.5, "end": 6.0},
            ],
        }
    ]

    # Get words from 1.0 to 4.0 seconds (should get "this is a test")
    result = get_clip_words(segments, 1.0, 4.0)

    assert len(result) == 4
    assert result[0]["word"] == "this"
    assert result[0]["start"] == 0.0  # Adjusted to be relative to clip start (1.0 - 1.0)
    assert result[0]["end"] == 0.5  # Adjusted to be relative to clip start (1.5 - 1.0)

    assert result[1]["word"] == "is"
    assert result[1]["start"] == 0.5  # Adjusted (1.5 - 1.0)
    assert result[1]["end"] == 1.0  # Adjusted (2.0 - 1.0)

    assert result[2]["word"] == "a"
    assert result[2]["start"] == 1.0  # Adjusted (2.0 - 1.0)
    assert result[2]["end"] == 1.5  # Adjusted (2.5 - 1.0)

    assert result[3]["word"] == "test"
    assert result[3]["start"] == 1.5  # Adjusted (2.5 - 1.0)
    assert result[3]["end"] == 2.0  # Adjusted (3.0 - 1.0)


def test_get_clip_words_multiple_segments():
    """Test get_clip_words with multiple segments."""
    segments = [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "First segment",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5},
                {"word": "world", "start": 0.5, "end": 1.0},
            ],
        },
        {
            "start": 5.0,
            "end": 10.0,
            "text": "Second segment",
            "words": [
                {"word": "This", "start": 5.0, "end": 5.5},
                {"word": "is", "start": 5.5, "end": 6.0},
                {"word": "test", "start": 6.0, "end": 6.5},
            ],
        },
    ]

    # Get words from 3.0 to 7.0 seconds (should get parts from both segments)
    result = get_clip_words(segments, 3.0, 7.0)

    # From first segment: "world" (0.5-1.0) midpoint 0.75 < 3.0, so NOT included
    # From second segment: "This" (5.0-5.5) midpoint 5.25, "is" (5.5-6.0) midpoint 5.75
    # "test" (6.0-6.5) midpoint 6.25

    assert len(result) == 3
    assert result[0]["word"] == "This"
    assert result[0]["start"] == 2.0  # Adjusted (5.0 - 3.0)
    assert result[0]["end"] == 2.5  # Adjusted (5.5 - 3.0)

    assert result[1]["word"] == "is"
    assert result[1]["start"] == 2.5  # Adjusted (5.5 - 3.0)
    assert result[1]["end"] == 3.0  # Adjusted (6.0 - 3.0)

    assert result[2]["word"] == "test"
    assert result[2]["start"] == 3.0  # Adjusted (6.0 - 3.0)
    assert result[2]["end"] == 3.5  # Adjusted (6.5 - 3.0)


def test_get_clip_words_no_words_field():
    """Test get_clip_words when segments have no words field."""
    segments = [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "Hello world",
            # No "words" field
        }
    ]
    result = get_clip_words(segments, 0.0, 5.0)
    assert result == []  # Should return empty list when no words


def test_get_clip_words_empty_word_text():
    """Test get_clip_words when word text is empty."""
    segments = [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "Hello world",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5},
                {"word": "", "start": 0.5, "end": 1.0},  # Empty word
                {"word": "world", "start": 1.0, "end": 1.5},
            ],
        }
    ]
    result = get_clip_words(segments, 0.0, 5.0)
    assert len(result) == 2
    assert result[0]["word"] == "Hello"
    assert result[1]["word"] == "world"


if __name__ == "__main__":
    pytest.main([__file__])
