"""
Unit tests for LLM analysis module.
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the project root to the path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.llm.analysis import _build_user_prompt, _load_or_generate, find_clips


def test_build_user_prompt():
    """Test user prompt building."""
    prompt = _build_user_prompt(
        transcript="Halo dunia ini adalah test",
        min_dur=15,
        max_dur=60,
        max_clips=10,
        min_score=50,
        chunk_info="Info chunk",
    )

    # Check that all components are present
    assert "Analyze this transcript and extract every clip" in prompt
    assert "Duration: 15–60s" in prompt
    assert "Max 10 clips" in prompt
    assert "clip_score ≥ 50" in prompt
    assert "Info chunk" in prompt
    assert "TRANSKRIP:" in prompt
    assert "Halo dunia ini adalah test" in prompt


def test_build_user_prompt_no_chunk_info():
    """Test user prompt building without chunk info."""
    prompt = _build_user_prompt(
        transcript="Test transcript", min_dur=10, max_dur=30, max_clips=5, min_score=40
    )

    assert "Analyze this transcript and extract every clip" in prompt
    assert "Duration: 10–30s" in prompt
    assert "Max 5 clips" in prompt
    assert "clip_score ≥ 40" in prompt
    assert "TRANSKRIP:" in prompt
    assert "Test transcript" in prompt
    # Should not contain chunk info
    assert "Info chunk" not in prompt


@patch("app.llm.analysis._load_or_generate")
@patch("app.llm.analysis.chunk_segments")
@patch("app.llm.analysis.merge_chunk_clips")
@patch("app.llm.analysis.validate_clips")
def test_find_clips_single_chunk(mock_validate, mock_merge, mock_chunk, mock_load):
    """Test find_clips with single chunk (no merging needed)."""
    # Setup
    mock_chunk.return_value = [[{"start": 0, "end": 10, "text": "test"}]]  # Single chunk
    mock_load.return_value = [{"start": 0, "end": 10, "title": "Test clip"}]
    mock_validate.return_value = [{"start": 0, "end": 10, "title": "Test clip", "clip_score": 75}]

    # Execute
    result = find_clips(
        segments=[{"start": 0, "end": 10, "text": "test"}],
        min_duration=15,
        max_duration=60,
        max_clips=10,
        min_score=50,
    )

    # Verify
    assert len(result) == 1
    assert result[0]["title"] == "Test clip"
    assert result[0]["clip_score"] == 75
    mock_load.assert_called_once()
    mock_chunk.assert_called_once()
    mock_merge.assert_not_called()  # Should not merge for single chunk
    mock_validate.assert_called_once()


@patch("app.llm.analysis._load_or_generate")
@patch("app.llm.analysis.chunk_segments")
@patch("app.llm.analysis.merge_chunk_clips")
@patch("app.llm.analysis.validate_clips")
def test_find_clips_multiple_chunks(mock_validate, mock_merge, mock_chunk, mock_load):
    """Test find_clips with multiple chunks (merging needed)."""
    # Setup
    mock_chunk.return_value = [
        [{"start": 0, "end": 10, "text": "test1"}],
        [{"start": 15, "end": 25, "text": "test2"}],
    ]  # Two chunks
    mock_load.return_value = [
        {"start": 0, "end": 10, "title": "Test clip 1"},
        {"start": 15, "end": 25, "title": "Test clip 2"},
    ]
    mock_merge.return_value = [{"start": 0, "end": 10, "title": "Test clip 1", "clip_score": 80}]

    # Execute
    result = find_clips(
        segments=[
            {"start": 0, "end": 10, "text": "test1"},
            {"start": 15, "end": 25, "text": "test2"},
        ],
        min_duration=15,
        max_duration=60,
        max_clips=10,
        min_score=50,
        video_duration=30.0,
    )

    # Verify
    assert len(result) == 1
    assert result[0]["title"] == "Test clip 1"
    assert result[0]["clip_score"] == 80
    mock_load.assert_called_once()
    mock_chunk.assert_called_once()
    mock_merge.assert_called_once()  # Should merge for multiple chunks
    mock_validate.assert_not_called()  # Should not validate when merging


@patch("app.llm.analysis.chunk_segments")
@patch("app.llm.analysis.SYSTEM_PROMPT")
@patch("app.llm.analysis.call_llm")
def test_load_or_generate_no_cache(mock_call_llm, mock_system_prompt, mock_chunk):
    """Test _load_or_generate when no cache file exists."""
    # Setup
    mock_chunk.return_value = [[{"start": 0, "end": 10, "text": "test"}]]
    mock_system_prompt.format.return_value = "System prompt"
    mock_call_llm.return_value = [{"start": 0, "end": 10, "title": "Test clip", "clip_score": 75}]

    # Execute
    result = _load_or_generate(
        segments=[{"start": 0, "end": 10, "text": "test"}],
        min_duration=15,
        max_duration=60,
        max_clips=10,
        min_score=50,
        llm_model=None,
        api_key=None,
        chunk_duration=480.0,
        chunk_overlap=60.0,
        raw_clips_cache_file=None,  # No cache
    )

    # Verify
    assert len(result) == 1
    assert result[0]["title"] == "Test clip"
    assert result[0]["clip_score"] == 75
    # Check that call_llm was called with correct parameters
    mock_call_llm.assert_called_once()
    call_args = mock_call_llm.call_args[0]  # Get positional arguments
    assert call_args[0] == "System prompt"  # system prompt
    assert "Analyze this transcript and extract every clip" in call_args[1]  # user prompt
    assert "Duration: 15–60s" in call_args[1]
    assert "Max 10 clips" in call_args[1]
    assert "clip_score ≥ 50" in call_args[1]
    assert "TRANSKRIP:" in call_args[1]
    assert "[0-10]test" in call_args[1]  # The transcript portion
    assert call_args[2] is None  # api_key
    assert call_args[3] is None  # llm_model
    mock_system_prompt.format.assert_called_once_with(
        min_dur=15, max_dur=60, max_clips=10, min_score=50
    )


@patch("app.llm.analysis.Path")
def test_load_or_generate_with_cache(mock_path):
    """Test _load_or_generate when cache file exists."""
    # Setup
    mock_cache_path = MagicMock()
    mock_path.return_value = mock_cache_path
    mock_cache_path.exists.return_value = True
    mock_cache_path.read_text.return_value = json.dumps(
        [{"start": 0, "end": 10, "title": "Cached clip", "clip_score": 85}]
    )

    # Execute
    result = _load_or_generate(
        segments=[],  # Doesn't matter when cache exists
        min_duration=15,
        max_duration=60,
        max_clips=10,
        min_score=50,
        llm_model=None,
        api_key=None,
        chunk_duration=480.0,
        chunk_overlap=60.0,
        raw_clips_cache_file="/fake/path/cache.json",
    )

    # Verify
    assert len(result) == 1
    assert result[0]["title"] == "Cached clip"
    assert result[0]["clip_score"] == 85
    mock_path.assert_called_once_with("/fake/path/cache.json")
    mock_cache_path.exists.assert_called_once()
    mock_cache_path.read_text.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
