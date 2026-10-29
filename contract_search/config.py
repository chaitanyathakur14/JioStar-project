"""Pipeline configuration. Every pipeline choice lives here so the improvement
loop can change it without touching code."""
from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Config:
    name: str = "baseline"

    # --- chunking ---
    chunker: str = "fixed"          # fixed | recursive | clause
    chunk_size: int = 500           # max characters per chunk
    chunk_overlap: int = 0          # only used by the fixed chunker
    title_prefix: bool = False      # index chunk text together with the contract title

    # --- text processing ---
    stem: bool = False              # light suffix stripping in the tokenizer

    # --- retrieval ---
    retriever: str = "bm25"         # bm25 | tfidf | dense | hybrid
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    dense_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rrf_k: int = 60                 # reciprocal-rank-fusion constant for hybrid

    # --- document routing ("Consider the X agreement; question") ---
    doc_routing: bool = False       # restrict chunk search to the best-matching contracts
    doc_top_n: int = 3
    query_mode: str = "full"        # full | question_only  (text used to score chunks)

    # --- reranking / post-processing ---
    rerank: bool = False
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_top: int = 30
    neighbor_expand: int = 0        # extend each hit by N neighbouring chunks

    # --- abstention ---
    calibrate_abstention: bool = True   # fit thresholds on train
    max_false_abstention: float = 0.10  # constraint used during calibration
    clause_threshold: float = 0.0       # idf-coverage of question terms in top chunk
    doc_threshold: float = 0.0          # idf-coverage of contract descriptor in best doc

    # --- evaluation ---
    k_values: list = field(default_factory=lambda: [1, 2, 4, 8, 16, 32])
    primary_k: int = 8

    # fields that change the index (used for caching)
    INDEX_FIELDS = ("chunker", "chunk_size", "chunk_overlap", "title_prefix", "stem",
                    "bm25_k1", "bm25_b", "retriever", "dense_model")

    def replace(self, **changes) -> "Config":
        return dataclasses.replace(self, **changes)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def index_key(self) -> str:
        d = {k: getattr(self, k) for k in self.INDEX_FIELDS}
        return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]

    def key(self) -> str:
        d = self.to_dict()
        d.pop("name", None)
        return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"Unknown config keys in {path}: {sorted(unknown)}")
        return cls(**data)

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(yaml.safe_dump(self.to_dict(), sort_keys=False), encoding="utf-8")
