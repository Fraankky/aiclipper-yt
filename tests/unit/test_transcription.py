"""
Unit tests for transcription module.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys


def test_detect_device_cpu_fallback():
    """Test device detection when torch is not available."""
    # Temporarily remove torch from modules if it exists
    torch_modules = [key for key in sys.modules.keys() if key.startswith("torch")]
    original_torch = {}
    for mod in torch_modules:
        original_torch[mod] = sys.modules[mod]
        del sys.modules[mod]

    try:
        from app.transcription import _detect_device

        device = _detect_device()
        assert device == "cpu"
    finally:
        # Restore torch modules
        for mod, value in original_torch.items():
            sys.modules[mod] = value


def test_detect_device_cuda_unavailable():
    """Test device detection when CUDA is not available."""
    # Temporarily remove torch from modules if it exists
    torch_modules = [key for key in sys.modules.keys() if key.startswith("torch")]
    original_torch = {}
    for mod in torch_modules:
        original_torch[mod] = sys.modules[mod]
        del sys.modules[mod]

    try:
        # Create a mock torch module
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        sys.modules["torch"] = mock_torch
        sys.modules["torch.cuda"] = mock_torch.cuda

        from app.transcription import _detect_device

        device = _detect_device()
        assert device == "cpu"
    finally:
        # Clean up mock torch modules
        for mod in ["torch", "torch.cuda"]:
            if mod in sys.modules:
                del sys.modules[mod]
        # Restore original torch modules
        for mod, value in original_torch.items():
            sys.modules[mod] = value


def test_detect_device_cuda_available():
    """Test device detection when CUDA is available."""
    # Temporarily remove torch from modules if it exists
    torch_modules = [key for key in sys.modules.keys() if key.startswith("torch")]
    original_torch = {}
    for mod in torch_modules:
        original_torch[mod] = sys.modules[mod]
        del sys.modules[mod]

    try:
        # Create a mock torch module
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        sys.modules["torch"] = mock_torch
        sys.modules["torch.cuda"] = mock_torch.cuda

        from app.transcription import _detect_device

        device = _detect_device()
        assert device == "cuda"
    finally:
        # Clean up mock torch modules
        for mod in ["torch", "torch.cuda"]:
            if mod in sys.modules:
                del sys.modules[mod]
        # Restore original torch modules
        for mod, value in original_torch.items():
            sys.modules[mod] = value


def test_resolve_compute_type_auto_gpu():
    """Test compute type resolution for auto GPU."""
    from app.transcription import _resolve_compute_type

    compute_type = _resolve_compute_type("cuda", "auto")
    assert compute_type == "float16"


def test_resolve_compute_type_auto_cpu():
    """Test compute type resolution for auto CPU."""
    from app.transcription import _resolve_compute_type

    compute_type = _resolve_compute_type("cpu", "auto")
    assert compute_type == "int8"


def test_resolve_compute_type_explicit():
    """Test explicit compute type resolution."""
    from app.transcription import _resolve_compute_type

    compute_type = _resolve_compute_type("cuda", "int8")
    assert compute_type == "int8"


def test_resolve_compute_type_unsupported_on_cpu():
    """Test unsupported compute type on CPU falls back to int8."""
    from app.transcription import _resolve_compute_type

    compute_type = _resolve_compute_type("cpu", "float16")
    assert compute_type == "int8"


@patch("app.transcription._detect_device")
@patch("app.transcription._resolve_compute_type")
def test_transcribe_basic(mock_resolve_compute, mock_detect_device):
    """Test basic transcription function call."""
    # Setup mocks
    mock_detect_device.return_value = "cpu"
    mock_resolve_compute.return_value = "int8"

    # Mock the faster_whisper import inside the function
    with patch.dict("sys.modules"):
        # Create mock modules
        mock_faster_whisper = MagicMock()
        mock_whisper_model = MagicMock()
        mock_batched_pipeline = MagicMock()

        mock_faster_whisper.WhisperModel = mock_whisper_model
        mock_faster_whisper.BatchedInferencePipeline = mock_batched_pipeline

        sys.modules["faster_whisper"] = mock_faster_whisper
        sys.modules["huggingface_hub"] = MagicMock()

        # Setup WhisperModel instance mock
        mock_model_instance = MagicMock()
        mock_whisper_model.return_value = mock_model_instance

        # Mock transcription result
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 2.5
        mock_segment.text = "Halo dunia"
        mock_segment.words = [
            MagicMock(word="Halo", start=0.0, end=0.5),
            MagicMock(word="dunia", start=0.5, end=2.5),
        ]
        mock_segment.no_speech_prob = 0.1

        mock_info = MagicMock()
        mock_info.language = "id"
        mock_info.language_probability = 0.95

        mock_model_instance.transcribe.return_value = ([mock_segment], mock_info)

        # Import and call function
        from app.transcription import transcribe

        segments, language_info = transcribe("dummy_video.mp4", batch_size=1)

        # Assertions
        assert len(segments) == 1
        assert segments[0]["start"] == 0.0
        assert segments[0]["end"] == 2.5
        assert segments[0]["text"] == "Halo dunia"
        assert len(segments[0]["words"]) == 2
        assert language_info["language"] == "id"
        assert language_info["language_probability"] == 0.95


@patch("app.transcription._detect_device")
@patch("app.transcription._resolve_compute_type")
def test_transcribe_batched(mock_resolve_compute, mock_detect_device):
    """Test transcription with batched inference."""
    # Setup mocks
    mock_detect_device.return_value = "cuda"
    mock_resolve_compute.return_value = "float16"

    # Mock the faster_whisper import inside the function
    with patch.dict("sys.modules"):
        # Create mock modules
        mock_faster_whisper = MagicMock()
        mock_whisper_model = MagicMock()
        mock_batched_pipeline = MagicMock()

        mock_faster_whisper.WhisperModel = mock_whisper_model
        mock_faster_whisper.BatchedInferencePipeline = mock_batched_pipeline

        sys.modules["faster_whisper"] = mock_faster_whisper
        sys.modules["huggingface_hub"] = MagicMock()

        # Setup BatchedInferencePipeline instance mock
        mock_batched_instance = MagicMock()
        mock_batched_pipeline.return_value = mock_batched_instance

        # Mock transcription result
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 3.0
        mock_segment.text = "Ini adalah test"
        mock_segment.words = [
            MagicMock(word="Ini", start=0.0, end=0.5),
            MagicMock(word="adalah", start=0.5, end=1.5),
            MagicMock(word="test", start=1.5, end=3.0),
        ]
        mock_segment.no_speech_prob = 0.05

        mock_info = MagicMock()
        mock_info.language = "id"
        mock_info.language_probability = 0.9

        mock_batched_instance.transcribe.return_value = ([mock_segment], mock_info)

        # Import and call function
        from app.transcription import transcribe

        segments, language_info = transcribe("dummy_video.mp4", batch_size=4)

        # Assertions
        assert len(segments) == 1
        assert segments[0]["start"] == 0.0
        assert segments[0]["end"] == 3.0
        assert segments[0]["text"] == "Ini adalah test"
        assert len(segments[0]["words"]) == 3
        assert language_info["language"] == "id"
        assert language_info["language_probability"] == 0.9
