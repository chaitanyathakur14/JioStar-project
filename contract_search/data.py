"""Loading LegalBench-RAG CUAD, selecting the mini subset, splitting, and
verifying character offsets."""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path


# ---- functions prescribed by the brief (kept verbatim in behaviour) ----------

def mini(tests: list, n: int = 194) -> list:
    if len(tests) <= n:
        return tests

    def key(t):
        random.seed(t["snippets"][0]["file_path"])
        return random.random()

    return sorted(tests, key=key)[:n]


def assign_split(query: str) -> str:
    h = int(hashlib.sha256(query.strip().encode("utf-8")).hexdigest(), 16)
    return "test" if h % 10 < 3 else "train"


# ---- data model ---------------------------------------------------------------

@dataclass
class Span:
    doc_id: str
    start: int
    end: int
    answer: str = ""


@dataclass
class Query:
    qid: str
    text: str
    split: str
    answerable: bool
    spans: list = field(default_factory=list)   # list[Span]; empty if unanswerable
    kind: str = "benchmark"                      # benchmark | <unanswerable type>


def _qid(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def read_doc(path: Path) -> str:
    # Python default text mode + UTF-8, as the dataset card specifies.
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_benchmark(data_root: str | Path) -> list[Query]:
    root = Path(data_root)
    raw = (root / "benchmarks" / "cuad.json").read_text(encoding="utf-8")
    tests = json.loads(raw)["tests"]
    out = []
    for t in mini(tests):
        spans = [Span(s["file_path"], s["span"][0], s["span"][1], s.get("answer", ""))
                 for s in t["snippets"]]
        out.append(Query(_qid(t["query"]), t["query"], assign_split(t["query"]), True, spans))
    return out


def load_unanswerable(path: str | Path) -> list[Query]:
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Query(_qid(it["query"]), it["query"], assign_split(it["query"]), False, [],
                  it.get("type", "unanswerable")) for it in items]


def load_corpus(data_root: str | Path, queries: list[Query]) -> dict[str, str]:
    """Load only the contracts referenced by the benchmark queries."""
    root = Path(data_root) / "corpus"
    doc_ids = sorted({s.doc_id for q in queries for s in q.spans})
    return {d: read_doc(root / d) for d in doc_ids}


def verify_offsets(queries: list[Query], docs: dict[str, str]) -> list[str]:
    """Return a list of human-readable mismatches (empty == all good)."""
    problems = []
    for q in queries:
        for s in q.spans:
            text = docs[s.doc_id][s.start:s.end]
            if s.answer and text != s.answer:
                problems.append(f"{q.qid} {s.doc_id}[{s.start}:{s.end}] != answer text")
    return problems


def load_all(data_root: str | Path, unanswerable_path: str | Path | None):
    bench = load_benchmark(data_root)
    docs = load_corpus(data_root, bench)
    unans = load_unanswerable(unanswerable_path) if unanswerable_path and Path(unanswerable_path).exists() else []
    return bench + unans, docs


def split_counts(queries: list[Query]) -> dict:
    out = {}
    for q in queries:
        key = ("answerable" if q.answerable else "unanswerable", q.split)
        out[key] = out.get(key, 0) + 1
    return {f"{a}/{s}": n for (a, s), n in sorted(out.items())}
