"""Command-line interface.

  python -m contract_search.cli verify
  python -m contract_search.cli query "Consider the ...; When does exclusivity end?" -k 5
  python -m contract_search.cli eval --config configs/baseline.yaml --split train
  python -m contract_search.cli loop --config configs/baseline.yaml --iterations 10
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from .config import Config
from .data import load_all, split_counts, verify_offsets
from .evaluate import calibrate, evaluate, get_index, headline, run_queries, save_eval
from .loop import run_loop
from .retrieve import Searcher

DATA = os.environ.get("CS_DATA", "data/legalbench-rag")
UNANS = os.environ.get("CS_UNANSWERABLE", "data/unanswerable.json")


def _load(args):
    return load_all(args.data, args.unanswerable)


def build_searcher(cfg: Config, data: str = DATA, unans: str = UNANS):
    """Searcher with abstention thresholds ready for interactive use. If the
    config asks for calibration, thresholds are fitted on train (cached)."""
    queries, docs = load_all(data, unans)
    if cfg.calibrate_abstention and cfg.doc_threshold == 0 and cfg.clause_threshold == 0:
        cache = Path("cache") / f"thresholds_{cfg.key()}.json"
        if cache.exists():
            dt, ct = json.loads(cache.read_text())
        else:
            train = [q for q in queries if q.split == "train"]
            dt, ct = calibrate(run_queries(cfg, docs, train), train, cfg.max_false_abstention)
            cache.parent.mkdir(exist_ok=True)
            cache.write_text(json.dumps([dt, ct]))
        cfg = cfg.replace(doc_threshold=dt, clause_threshold=ct)
    return Searcher(get_index(cfg, docs), cfg), cfg, docs


def cmd_verify(args):
    queries, docs = _load(args)
    bad = verify_offsets(queries, docs)
    print(f"{len(docs)} contracts indexed; queries: {split_counts(queries)}")
    print("offset check:", "all spans match" if not bad else f"{len(bad)} mismatches")
    from .text import split_query
    named = sum(bool(split_query(q.text)[0]) for q in queries if q.answerable)
    print(f"benchmark queries naming a contract ('Consider the X; ...'): {named}/{sum(q.answerable for q in queries)}")
    for b in bad[:20]:
        print("  ", b)
    return 1 if bad else 0


def cmd_query(args):
    cfg = Config.load(args.config)
    searcher, cfg, _ = build_searcher(cfg, args.data, args.unanswerable)
    res = searcher.search(args.question, args.k)
    if args.json:
        print(json.dumps({"abstained": res.abstained, "reason": res.reason,
                          "doc_conf": res.doc_conf, "clause_conf": res.clause_conf,
                          "passages": [] if res.abstained else
                          [p.__dict__ for p in res.passages]}, indent=1))
        return 0
    if res.abstained:
        print(f"NO ANSWER: {res.reason} (doc_conf={res.doc_conf:.2f}, clause_conf={res.clause_conf:.2f})")
        return 0
    for i, p in enumerate(res.passages, 1):
        print(f"\n#{i}  {p.doc_id}  [{p.start}:{p.end}]  score={p.score:.3f}")
        print("   " + p.text.replace("\n", " ")[:600])
    return 0


def cmd_eval(args):
    cfg = Config.load(args.config)
    queries, docs = _load(args)
    out = evaluate(cfg, docs, queries, args.split)
    print(headline(out["metrics"], cfg.primary_k))
    for k in cfg.k_values:
        m = out["metrics"]
        print(f"  k={k:<3} P={m[f'P@{k}']:.4f} R={m[f'R@{k}']:.4f}  served P={m[f'sP@{k}']:.4f} "
              f"R={m[f'sR@{k}']:.4f}  DocHit={m[f'DocHit@{k}']:.3f}")
    print("  diagnosis:", out["metrics"]["diagnosis_counts"])
    path = Path(args.out or f"results/{cfg.name}_{args.split}.json")
    save_eval(out, path)
    print("saved", path)
    if args.split == "test":
        with open("results/test_runs.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{cfg.name}\t{args.config}\t"
                    f"{headline(out['metrics'], cfg.primary_k)}\n")
        print("test-set run recorded in results/test_runs.log")
    return 0


def cmd_loop(args):
    cfg = Config.load(args.config)
    queries, docs = _load(args)
    run_loop(cfg, docs, queries, args.iterations, args.out_dir, args.final)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="contract_search")
    ap.add_argument("--data", default=DATA, help="folder with benchmarks/ and corpus/")
    ap.add_argument("--unanswerable", default=UNANS)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("verify", help="check offsets and split counts")

    q = sub.add_parser("query", help="search the contracts")
    q.add_argument("question")
    q.add_argument("-k", type=int, default=5)
    q.add_argument("--config", default="configs/final.yaml")
    q.add_argument("--json", action="store_true")

    e = sub.add_parser("eval", help="evaluate a config on a split")
    e.add_argument("--config", default="configs/baseline.yaml")
    e.add_argument("--split", choices=["train", "test"], default="train")
    e.add_argument("--out")

    lp = sub.add_parser("loop", help="run the self-improvement loop on train")
    lp.add_argument("--config", default="configs/baseline.yaml")
    lp.add_argument("--iterations", type=int, default=12)
    lp.add_argument("--out-dir", default="experiments")
    lp.add_argument("--final", default="configs/final.yaml")

    args = ap.parse_args(argv)
    return {"verify": cmd_verify, "query": cmd_query, "eval": cmd_eval, "loop": cmd_loop}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
