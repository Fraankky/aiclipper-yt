"""
Simple unit tests for LLM analysis module functions that don't require complex mocking.
"""

import sys
import os

# Add the project root to the path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.llm.analysis import _build_user_prompt


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


if __name__ == "__main__":
    test_build_user_prompt()
    test_build_user_prompt_no_chunk_info()
    print("All tests passed!")
