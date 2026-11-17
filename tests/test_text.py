import pytest

from voice_studio.text import detect_language_hint, normalize_text, split_sentences


def test_normalize_text_preserves_hindi_and_collapses_whitespace():
    assert normalize_text("  नमस्ते\n  दुनिया  ") == "नमस्ते दुनिया"


def test_detect_language_hint_for_hindi_english_and_unknown():
    assert detect_language_hint("नमस्ते दुनिया") == "hi"
    assert detect_language_hint("Hello world") == "en"
    assert detect_language_hint("12345") == "auto"


def test_split_sentences_supports_hindi_and_english_punctuation():
    assert split_sentences("Hello. नमस्ते। How are you?") == ("Hello.", "नमस्ते।", "How are you?")


def test_text_validation_is_bounded_and_rejects_control_characters():
    with pytest.raises(ValueError, match="empty"):
        normalize_text("  ")
    with pytest.raises(ValueError, match="limit"):
        normalize_text("long text", max_characters=4)
    with pytest.raises(ValueError, match="control"):
        normalize_text("hello\x00world")
    with pytest.raises(TypeError):
        normalize_text(None)
