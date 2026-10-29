"""Character-level precision/recall as defined in LegalBench-RAG.

For one query, take the union of character intervals retrieved (top-k) and
the union of ground-truth intervals, per document:
    precision = |retrieved ∩ gold| / |retrieved|
    recall    = |retrieved ∩ gold| / |gold|
Unions are used so overlapping/expanded passages are not double counted."""
from __future__ import annotations

from collections import defaultdict


def merge_intervals(ivs):
    out = []
    for s, e in sorted(ivs):
        if e <= s:
            continue
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [tuple(x) for x in out]


def _by_doc(triples):
    d = defaultdict(list)
    for doc, s, e in triples:
        d[doc].append((s, e))
    return {k: merge_intervals(v) for k, v in d.items()}


def _length(ivs):
    return sum(e - s for s, e in ivs)


def _intersection(a, b):
    i = j = total = 0
    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if hi > lo:
            total += hi - lo
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return total


def char_precision_recall(retrieved, gold):
    """retrieved, gold: iterables of (doc_id, start, end). Returns (precision, recall)."""
    r, g = _by_doc(retrieved), _by_doc(gold)
    r_len = sum(_length(v) for v in r.values())
    g_len = sum(_length(v) for v in g.values())
    inter = sum(_intersection(r[d], g[d]) for d in r if d in g)
    precision = inter / r_len if r_len else 0.0
    recall = inter / g_len if g_len else 0.0
    return precision, recall


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0
