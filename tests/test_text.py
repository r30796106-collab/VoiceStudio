import pytest

from voice_studio.text import normalize_text, segment_text


def test_normalizes_unicode_and_whitespace_without_translation():
    assert normalize_text("  नमस्ते\u00a0  दुनिया!  ") == "नमस्ते दुनिया!"


def test_empty_text_has_no_segments():
    assert segment_text(" \n\t ") == []


def test_prefers_sentence_boundaries_and_keeps_punctuation():
    result = segment_text("Hello world. नमस्ते दुनिया। Next line!", max_chars=20)
    assert [item.text for item in result] == [
        "Hello world.", "नमस्ते दुनिया।", "Next line!"
    ]


def test_splits_long_sentence_on_word_boundaries():
    result = segment_text("one two three four five", max_chars=9)
    assert [item.text for item in result] == ["one two", "three", "four five"]
    assert all(len(item.text) <= 9 for item in result)


def test_rejects_single_token_that_exceeds_limit():
    with pytest.raises(ValueError, match="token"):
        segment_text("extraordinary", max_chars=5)


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_rejects_invalid_segment_limits(limit):
    with pytest.raises(ValueError):
        segment_text("hello", max_chars=limit)


def test_rejects_non_string_text():
    with pytest.raises(TypeError):
        normalize_text(None)
