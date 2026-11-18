"""Language-neutral text preparation for Hindi/English speech workflows."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_WHITESPACE = re.compile(r"\s+")
_SENTENCE_END = re.compile(r"(?<=[.!?।॥])\s+")


@dataclass(frozen=True, slots=True)
class TextSegment:
    index: int
    text: str


def normalize_text(value: str) -> str:
    """Normalize Unicode and whitespace without translating or changing words."""
    if not isinstance(value, str):
        raise TypeError("text must be a string")
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.replace("\u00a0", " ")
    return _WHITESPACE.sub(" ", normalized).strip()


def segment_text(value: str, *, max_chars: int = 240) -> list[TextSegment]:
    """Split speech text into bounded segments, preferring sentence boundaries.

    Oversized sentences are split at whitespace; a single token longer than the
    limit is rejected rather than silently cut or corrupted.
    """
    if type(max_chars) is not int or max_chars < 1:
        raise ValueError("max_chars must be a positive integer")
    text = normalize_text(value)
    if not text:
        return []

    sentences = _SENTENCE_END.split(text)
    chunks: list[str] = []
    current = ""

    def append_piece(piece: str) -> None:
        nonlocal current
        if not piece:
            return
        if len(piece) > max_chars:
            words = piece.split(" ")
            for word in words:
                if len(word) > max_chars:
                    raise ValueError("a single token exceeds max_chars")
                candidate = f"{current} {word}".strip()
                if len(candidate) <= max_chars:
                    current = candidate
                else:
                    if current:
                        chunks.append(current)
                    current = word
        else:
            candidate = f"{current} {piece}".strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = piece

    for sentence in sentences:
        append_piece(sentence)
    if current:
        chunks.append(current)
    return [TextSegment(index=index, text=chunk) for index, chunk in enumerate(chunks)]
