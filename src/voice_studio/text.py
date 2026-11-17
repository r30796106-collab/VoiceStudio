"""Lightweight Hindi/English text preparation without model dependencies."""
from __future__ import annotations

import unicodedata


def normalize_text(text: str, *, max_characters: int = 100_000) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if type(max_characters) is not int or max_characters < 1:
        raise ValueError("max_characters must be a positive integer")
    normalized = unicodedata.normalize("NFC", text)
    normalized = " ".join(normalized.split())
    if not normalized:
        raise ValueError("text must not be empty")
    if len(normalized) > max_characters:
        raise ValueError("text exceeds the configured character limit")
    if any(unicodedata.category(char) in {"Cc", "Cs"} for char in normalized):
        raise ValueError("text contains unsupported control or surrogate characters")
    return normalized


def detect_language_hint(text: str) -> str:
    normalized = normalize_text(text)
    if any("\u0900" <= char <= "\u097f" for char in normalized):
        return "hi"
    if any(char.isascii() and char.isalpha() for char in normalized):
        return "en"
    return "auto"


def split_sentences(text: str) -> tuple[str, ...]:
    normalized = normalize_text(text)
    chunks: list[str] = []
    current: list[str] = []
    for char in normalized:
        current.append(char)
        if char in ".!?।":
            sentence = "".join(current).strip()
            if sentence:
                chunks.append(sentence)
            current = []
    tail = "".join(current).strip()
    if tail:
        chunks.append(tail)
    return tuple(chunks)
