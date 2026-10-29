"""Offset-preserving chunkers. Every chunk satisfies doc[start:end] == chunk text."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    doc_id: str
    start: int
    end: int
    idx: int = 0  # position within its document

    def text(self, docs: dict) -> str:
        return docs[self.doc_id][self.start:self.end]


def _trim(text: str, s: int, e: int) -> tuple[int, int]:
    while s < e and text[s].isspace():
        s += 1
    while e > s and text[e - 1].isspace():
        e -= 1
    return s, e


def fixed_chunks(text: str, size: int, overlap: int = 0) -> list[tuple[int, int]]:
    step = max(1, size - overlap)
    return [(i, min(i + size, len(text))) for i in range(0, len(text), step)]


_SEPS = ["\n\n", "\n", ". ", "; ", " "]


def _split(text: str, start: int, end: int, seps: list[str], size: int) -> list[tuple[int, int]]:
    if end - start <= size:
        return [(start, end)]
    if not seps:
        return [(i, min(i + size, end)) for i in range(start, end, size)]
    sep = seps[0]
    pieces, pos = [], start
    i = text.find(sep, start, end)
    while i != -1:
        cut = i + len(sep)
        pieces.append((pos, cut))
        pos = cut
        i = text.find(sep, pos, end)
    if pos < end:
        pieces.append((pos, end))
    if len(pieces) == 1:
        return _split(text, start, end, seps[1:], size)
    out = []
    for a, b in pieces:
        out.extend(_split(text, a, b, seps[1:], size) if b - a > size else [(a, b)])
    return out


def _merge(pieces: list[tuple[int, int]], size: int) -> list[tuple[int, int]]:
    out = []
    for a, b in pieces:
        if out and b - out[-1][0] <= size:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def recursive_chunks(text: str, size: int, start: int = 0, end: int | None = None):
    """Like LangChain's RecursiveCharacterTextSplitter: split on the coarsest
    separator that works, then greedily merge neighbours up to `size`."""
    end = len(text) if end is None else end
    return _merge(_split(text, start, end, _SEPS, size), size)


# Section heading at a line start: "12.", "4.2", "Section 5", "ARTICLE III", "(a)"
_HEADING = re.compile(
    r"(?m)^[ \t]*(?:(?:ARTICLE|Article|SECTION|Section)\s+[0-9IVXLC]+|\d{1,2}(?:\.\d{1,2})*[.)]\s+\S|\([a-z]\)\s+\S)"
)


def clause_chunks(text: str, size: int, min_section: int = 120):
    """Split at section headings first so chunks never straddle two clauses,
    then recursively split long sections."""
    bounds = sorted({0, *[m.start() for m in _HEADING.finditer(text)], len(text)})
    sections = [(a, b) for a, b in zip(bounds, bounds[1:]) if b > a]
    # fold tiny sections (bare headings) into the next one
    merged = []
    carry = None
    for a, b in sections:
        if carry is not None:
            a = carry
            carry = None
        if b - a < min_section and (a, b) != sections[-1]:
            carry = a
            continue
        merged.append((a, b))
    if carry is not None:
        merged.append((carry, len(text)))
    out = []
    for a, b in merged:
        out.extend(recursive_chunks(text, size, a, b))
    return out


def chunk_document(doc_id: str, text: str, method: str, size: int, overlap: int = 0) -> list[Chunk]:
    if method == "fixed":
        spans = fixed_chunks(text, size, overlap)
    elif method == "recursive":
        spans = recursive_chunks(text, size)
    elif method == "clause":
        spans = clause_chunks(text, size)
    else:
        raise ValueError(f"unknown chunker {method}")
    out = []
    for s, e in spans:
        s, e = _trim(text, s, e)
        if e > s:
            out.append(Chunk(doc_id, s, e, len(out)))
    return out
