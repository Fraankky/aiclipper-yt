"""LLM module for clip analysis and processing"""

from .analysis import find_clips as find_clips
from .backends.client import call_llm as call_llm
from .fix_clips import fix_and_improve_clips as fix_and_improve_clips
from .fix_clips import generate_single_clip_metadata as generate_single_clip_metadata
from .fix_clips import translate_subtitle_words as translate_subtitle_words
from .prompts.system_prompt import SYSTEM_PROMPT as SYSTEM_PROMPT
