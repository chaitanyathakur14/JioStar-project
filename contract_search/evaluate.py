"""Run a configuration over a split, calibrate abstention on train, compute
retrieval + abstention metrics, and label each failure with a cause."""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

import numpy as np

from .config import Config
from .data import Query
from .index import Index
from .metrics import char_precision_recall, mean
from .retrieve import Searcher, SearchResult

_INDEX_CACHE: dict = {}


def get_index(cfg: Config, docs: dict) -> Index:
    key = (cfg.index_key(), id(docs))
    if key not in _INDEX_CACHE:
        if len(_INDEX_CACHE) > 4:
            _INDEX_CACHE.clear()
        _INDEX_CACHE[key] = Index(cfg, docs)
    return _INDEX_CACHE[key]


# ---------------------------------------------------------------- abstention

def calibrate(results: list[SearchResult], queries: list[Query], max_false: float) -> tuple[float, float]:
    """Pick (doc_threshold, clause_threshold) that maximise balanced accuracy on
    the given (train) queries, subject to false abstention on answerable
    queries <= max_false. Grid = observed signal values."""
    ans = [r for r, q in zip(results, queries) if q.answerable]
    una = [r for r, q in zip(results, queries) if not q.answerable]
    if not ans or not una:
        return 0.0, 0.0
    doc_grid = np.array(sorted({0.0, *[r.doc_conf + 1e-6 for r in results if r.named_contract]}))
    cl_grid = np.array(sorted({0.0, *[r.clause_conf + 1e-6 for r in results]}))

    def abst_matrix(rs):  # shape (len(doc_grid), len(cl_grid), len(rs))
        named = np.array([r.named_contract for r in rs])
        dc = np.array([r.doc_conf for r in rs])
        cc = np.array([r.clause_conf for r in rs])
        empty = np.array([(not r.passages) or r.clause_conf <= 0 for r in rs])
        doc_ab = named[None, :] & (dc[None, :] < doc_grid[:, None])            # (D, n)
        cl_ab = (cc[None, :] < cl_grid[:, None]) | empty[None, :]              # (C, n)
        return doc_ab[:, None, :] | cl_ab[None, :, :]

    fa = abst_matrix(ans).mean(axis=2)
    ca = abst_matrix(una).mean(axis=2)
    bal = (ca + 1 - fa) / 2
    bal[fa > max_false] = -1
    # tie-break toward lower thresholds (abstain as little as needed)
    penalty = (doc_grid[:, None] + cl_grid[None, :]) * 1e-6
    i, j = np.unravel_index(np.argmax(bal - penalty), bal.shape)
    return float(doc_grid[i]), float(cl_grid[j])


# ---------------------------------------------------------------- diagnosis

def diagnose(q: Query, r: SearchResult, k: int) -> str:
    if not q.answerable:
        return "correct_abstention" if r.abstained else "false_answer"
    if r.abstained:
        return "false_abstention"
    top = r.passages[:k]
    gold_docs = {s.doc_id for s in q.spans}
    if not any(p.doc_id in gold_docs for p in top):
        return "wrong_document"
    p, rec = char_precision_recall([(x.doc_id, x.start, x.end) for x in top],
                                   [(s.doc_id, s.start, s.end) for s in q.spans])
    if rec == 0:
        return "right_document_wrong_section"
    if rec < 0.5:
        return "partial_span"
    return "ok"


# ---------------------------------------------------------------- main

def run_queries(cfg: Config, docs: dict, queries: list[Query]) -> list[SearchResult]:
    s = Searcher(get_index(cfg, docs), cfg)
    kmax = max(cfg.k_values)
    return [s.search(q.text, kmax) for q in queries]


def evaluate(cfg: Config, docs: dict, all_queries: list[Query], split: str = "train") -> dict:
    t0 = time.time()
    train = [q for q in all_queries if q.split == "train"]
    target = [q for q in all_queries if q.split == split]

    train_res = run_queries(cfg, docs, train)
    if cfg.calibrate_abstention:
        doc_t, cl_t = calibrate(train_res, train, cfg.max_false_abstention)
    else:
        doc_t, cl_t = cfg.doc_threshold, cfg.clause_threshold
    results = train_res if split == "train" else run_queries(cfg, docs, target)
    for r in results:
        Searcher.apply_abstention(r, doc_t, cl_t)

    m: dict = {"config": cfg.name, "split": split, "doc_threshold": doc_t, "clause_threshold": cl_t}
    ans = [(q, r) for q, r in zip(target, results) if q.answerable]
    una = [(q, r) for q, r in zip(target, results) if not q.answerable]
    m["n_answerable"], m["n_unanswerable"] = len(ans), len(una)

    per_query = []
    for q, r in zip(target, results):
        row = {"qid": q.qid, "query": q.text, "answerable": q.answerable, "kind": q.kind,
               "abstained": r.abstained, "doc_conf": round(r.doc_conf, 4),
               "clause_conf": round(r.clause_conf, 4),
               "diagnosis": diagnose(q, r, cfg.primary_k)}
        if q.answerable:
            gold = [(s.doc_id, s.start, s.end) for s in q.spans]
            row["gold"] = gold
            row["top"] = [(p.doc_id, p.start, p.end) for p in r.passages[:3]]
            for k in cfg.k_values:
                ret = [(p.doc_id, p.start, p.end) for p in r.passages[:k]]
                p_, r_ = char_precision_recall(ret, gold)
                row[f"P@{k}"], row[f"R@{k}"] = p_, r_
                # "served" metrics: what the user actually sees (abstention -> nothing)
                row[f"sP@{k}"], row[f"sR@{k}"] = (0.0, 0.0) if r.abstained else (p_, r_)
                gd = {s.doc_id for s in q.spans}
                row[f"DocHit@{k}"] = float(any(p.doc_id in gd for p in r.passages[:k]))
        per_query.append(row)

    rows_a = [x for x in per_query if x["answerable"]]
    for k in cfg.k_values:
        for pre in ("P", "R", "sP", "sR", "DocHit"):
            m[f"{pre}@{k}"] = mean(x[f"{pre}@{k}"] for x in rows_a)
    m["false_abstention_rate"] = mean(r.abstained for _, r in ans)
    m["correct_abstention_rate"] = mean(r.abstained for _, r in una) if una else float("nan")
    m["abstention_balanced_acc"] = ((m["correct_abstention_rate"] + 1 - m["false_abstention_rate"]) / 2
                                    if una else float("nan"))
    m["diagnosis_counts"] = dict(Counter(x["diagnosis"] for x in per_query))
    m["seconds"] = round(time.time() - t0, 1)
    return {"metrics": m, "per_query": per_query}


def save_eval(out: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")


def headline(m: dict, k: int = 8) -> str:
    return (f"[{m['split']}] n={m['n_answerable']}+{m['n_unanswerable']}u  "
            f"R@{k}={m[f'R@{k}']:.3f} P@{k}={m[f'P@{k}']:.4f} DocHit@{k}={m[f'DocHit@{k}']:.3f}  "
            f"falseAbst={m['false_abstention_rate']:.3f} correctAbst={m['correct_abstention_rate']:.3f}")
