"""Tokenisation and query parsing."""
from __future__ import annotations

import re

_TOKEN = re.compile(r"[a-z0-9]+")

STOPWORDS = set("""
a an the and or of to in on for by with as at from is are was were be been being this that these
those it its any all such may shall will would can could should does do did has have had not no
if than then there their they them which who whom whose what when where how whether into upon
under over between per each other same also only our we us you your i he she his her
""".split())

# Words that appear in nearly every CUAD query template and carry no signal
# about which clause is meant.
QUERY_BOILERPLATE = set("""
consider contract agreement highlight parts details related part clause if any
reviewed review lawyer should
""".split())

_SUFFIXES = ("ations", "ation", "ings", "ing", "ies", "ied", "ed", "es", "s")


def _stem(tok: str) -> str:
    for suf in _SUFFIXES:
        if len(tok) > len(suf) + 3 and tok.endswith(suf):
            if suf in ("ies", "ied"):
                return tok[: -len(suf)] + "y"
            return tok[: -len(suf)]
    return tok


def tokenize(text: str, stem: bool = False, drop: set | None = None) -> list[str]:
    toks = [t for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS]
    if drop:
        toks = [t for t in toks if t not in drop]
    if stem:
        toks = [_stem(t) for t in toks]
    return toks


_CONSIDER = re.compile(r"^\s*consider\s+(?:the\s+)?(.+?);\s*(.+)$", re.IGNORECASE | re.DOTALL)


def split_query(query: str) -> tuple[str, str]:
    """CUAD queries look like 'Consider the <contract description>; <question>'.
    Returns (descriptor, question). Descriptor is '' when the user names no contract."""
    m = _CONSIDER.match(query)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return "", query.strip()


def title_from_path(doc_id: str) -> str:
    """Make a searchable title out of a CUAD file name."""
    name = doc_id.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)      # CamelCase -> words
    name = re.sub(r"[_\-]+", " ", name)
    return name
