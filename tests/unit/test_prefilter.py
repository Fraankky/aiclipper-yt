"""
Unit tests for prefilter module.
"""

import pytest
from app.prefilter import _wps, _jaccard, _is_likely_music, prefilter_segments


def test_wps_calculation():
    """Test words per second calculation."""
    segment = {"start": 0.0, "end": 2.0, "text": "Halo dunia ini adalah test"}
    wps = _wps(segment)
    assert wps == 5.0 / 2.0  # 5 words / 2 seconds


def test_wps_zero_duration():
    """Test words per second with zero duration."""
    segment = {"start": 0.0, "end": 0.0, "text": "Halo"}
    wps = _wps(segment)
    assert wps == 0.0


def test_jaccard_similarity():
    """Test Jaccard similarity calculation."""
    # Identical strings
    assert _jaccard("hello world", "hello world") == 1.0

    # Completely different strings
    assert _jaccard("hello world", "foo bar") == 0.0

    # Partially similar strings: "hello world" vs "hello universe"
    # Words: {"hello", "world"} vs {"hello", "universe"}
    # Intersection: {"hello"} (size 1)
    # Union: {"hello", "world", "universe"} (size 3)
    # Jaccard: 1/3 ≈ 0.333
    assert abs(_jaccard("hello world", "hello universe") - 0.333) < 0.001

    # Empty strings
    assert _jaccard("", "") == 0.0
    assert _jaccard("hello", "") == 0.0


def test_is_likely_music_high_no_speech():
    """Test music detection with high no_speech_prob."""
    assert _is_likely_music("some text", 0.8) == True
    assert _is_likely_music("some text", 0.7) == False  # Below threshold


def test_is_likely_music_onomatopoeia():
    """Test music detection with pure onomatopoeia."""
    assert _is_likely_music("la la la", 0.0) == True
    assert _is_likely_music("na na na", 0.0) == True
    assert _is_likely_music("doo doo doo", 0.0) == True
    assert _is_likely_music("woo woo woo", 0.0) == True
    assert _is_likely_music("ooh ooh ooh", 0.0) == True
    assert _is_likely_music("ahh ahh ahh", 0.0) == True
    assert _is_likely_music("mm mm mm", 0.0) == True
    assert _is_likely_music("ohh ohh ohh", 0.0) == True
    assert _is_likely_music("woah woah woah", 0.0) == True

    # Mixed with other words should not be detected as music
    assert _is_likely_music("la la la hello", 0.0) == False


def test_is_likely_music_stage_directions():
    """Test music detection with stage directions."""
    assert _is_likely_music("[instrumental]", 0.0) == True
    assert _is_likely_music("[music]", 0.0) == True
    assert _is_likely_music("[background music]", 0.0) == True
    assert _is_likely_music("(instrumental)", 0.0) == True
    assert _is_likely_music("(music)", 0.0) == True
    assert _is_likely_music("(singing)", 0.0) == True
    assert _is_likely_music("[singing]", 0.0) == True
    assert _is_likely_music("♪", 0.0) == True
    assert _is_likely_music("♫", 0.0) == True

    # Partial matches SHOULD trigger (substring matching)
    assert _is_likely_music("this [instrumental] section", 0.0) == True
    assert _is_likely_music("check (music) here", 0.0) == True
    assert _is_likely_music("start ♪ end", 0.0) == True


def test_prefilter_segments_basic():
    """Test basic prefilter functionality."""
    segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.0,
            "text": "Halo selamat datang",
            "tokens": [1, 2, 3],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.1,
            "words": [],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 3.5,  # Increased gap to prevent merging (gap = 1.5 > merge_gap=1.0)
            "end": 5.5,
            "text": "Ini adalah video test",
            "tokens": [4, 5, 6],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
            "words": [],
        },
    ]

    filtered, stats = prefilter_segments(segments)

    # Should keep both segments (no filtering should occur and no merging due to gap)
    assert len(filtered) == 2
    assert stats["original"] == 2
    assert stats["kept"] == 2  # After filtering, before merging
    assert stats["dropped"] == 0
    assert stats["merged"] == 0  # No merging should occur with increased gap


def test_prefilter_segments_short_duration():
    """Test filtering of segments with short duration."""
    segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 0.2,  # Too short (< 0.3s default)
            "text": "Hi",
            "tokens": [1],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.1,
            "words": [],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 0.5,
            "end": 2.0,
            "text": "This is a valid segment",
            "tokens": [2, 3, 4],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
            "words": [],
        },
    ]

    filtered, stats = prefilter_segments(segments)

    # Should filter out short duration segment
    assert len(filtered) == 1
    assert stats["dropped"] == 1
    assert stats["reasons"]["short_dur"] == 1


def test_prefilter_segments_few_words():
    """Test filtering of segments with too few words."""
    segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.0,
            "text": "Hi",  # Only 1 word (< min_words default of 1? Actually min_words=1 so this should pass)
            "tokens": [1],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.1,
            "words": [],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 2.5,
            "end": 4.0,
            "text": "Hello world",  # 2 words
            "tokens": [2, 3],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
            "words": [],
        },
    ]

    filtered, stats = prefilter_segments(segments, min_words=2)  # Require at least 2 words

    # Should filter out segment with only 1 word
    assert len(filtered) == 1
    assert stats["dropped"] == 1
    assert stats["reasons"]["few_words"] == 1


def test_prefilter_segments_high_no_speech():
    """Test filtering of segments with high no_speech_prob."""
    segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.0,
            "text": "Probably music",
            "tokens": [1, 2, 3],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.95,  # Very high
            "words": [],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 2.5,
            "end": 4.0,
            "text": "This is clear speech",
            "tokens": [4, 5, 6, 7],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.1,
            "words": [],
        },
    ]

    filtered, stats = prefilter_segments(segments)

    # Should filter out high no_speech_prob segment
    assert len(filtered) == 1
    assert stats["dropped"] == 1
    assert stats["reasons"]["no_speech"] == 1


def test_prefilter_segments_music_detection():
    """Test filtering of music-like segments."""
    segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.0,
            "text": "la la la",  # Pure music marker
            "tokens": [1, 2, 3],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.0,
            "words": [],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 2.5,
            "end": 4.0,
            "text": "This is clear speech",
            "tokens": [4, 5, 6, 7],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
            "words": [],
        },
    ]

    filtered, stats = prefilter_segments(segments)

    # Should filter out music segment
    assert len(filtered) == 1
    assert stats["dropped"] == 1
    assert stats["reasons"]["music"] == 1


def test_prefilter_segments_duplicate_detection():
    """Test filtering of duplicate segments."""
    segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.0,
            "text": "Hello world test",
            "tokens": [1, 2, 3, 4],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.1,
            "words": [],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 2.5,
            "end": 4.5,
            "text": "Hello world test",  # Duplicate
            "tokens": [1, 2, 3, 4],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
            "words": [],
        },
        {
            "id": 2,
            "seek": 0,
            "start": 5.0,
            "end": 7.0,
            "text": "Different content here",
            "tokens": [5, 6, 7, 8],
            "temperature": 0.0,
            "avg_logprob": -0.3,
            "compression_ratio": 1.0,
            "no_speech_prob": 0.05,
            "words": [],
        },
    ]

    filtered, stats = prefilter_segments(segments)

    # Should filter out duplicate segment
    assert len(filtered) == 2
    assert stats["dropped"] == 1
    assert stats["reasons"]["duplicate"] == 1


def test_prefilter_segments_merging():
    """Test merging of adjacent segments."""
    segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.0,
            "text": "First segment",
            "tokens": [1, 2, 3],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.1,
            "words": [],
        },
        {
            "id": 1,
            "seek": 0,
            "start": 2.5,  # Gap of 0.5s (< merge_gap default of 1.0)
            "end": 4.0,
            "text": "Second segment",
            "tokens": [4, 5, 6],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
            "words": [],
        },
    ]

    filtered, stats = prefilter_segments(segments)

    # Should merge the two segments
    assert len(filtered) == 1
    assert stats["merged"] == 1
    assert filtered[0]["text"] == "First segment Second segment"
    assert filtered[0]["start"] == 0.0
    assert filtered[0]["end"] == 4.0


if __name__ == "__main__":
    pytest.main([__file__])
