"""Self-improvement loop (train split only).

Each iteration: evaluate current config on train -> summarise failure causes ->
pick the next untried proposal whose trigger matches the dominant failure ->
evaluate the candidate on train -> accept/reject by the criterion below -> log.

Objective
  primary   : mean character recall@8 (raw ranking, before abstention)
  guardrails: precision@8 must not fall below 90% of current,
              abstention balanced accuracy must not drop by more than 0.03,
              false-abstention rate must stay <= 0.10, or not get worse if the
              current config already exceeds 0.10 (an absolute limit the
              baseline already breaks would block every change).
Acceptance (guardrails must hold in both paths)
  (a) recall path: R@8 improves by >= MIN_GAIN (absolute) AND more train
      queries improve than get worse (a cheap paired sign check against noise);
  (b) precision path: R@8 drops by no more than MIN_GAIN AND P@8 improves by
      >= PRECISION_GAIN relative. Lets the loop take 'same recall, less text
      to read' changes, which matter to a lawyer reading the results.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .config import Config
from .evaluate import evaluate, headline
from .index import dense_available

MIN_GAIN = 0.005
PRECISION_KEEP = 0.90
BAL_ACC_DROP = 0.03
MAX_FALSE_ABST = 0.10
PRECISION_GAIN = 0.10


@dataclass
class Proposal:
    name: str
    trigger: str            # failure category that motivates it ("any" = parameter search)
    rationale: str
    change: Callable[[Config], dict]
    available: Callable[[Config], bool] = lambda c: True


PROPOSALS = [
    Proposal("route_and_question_only", "right_document_wrong_section",
             "Right contract, wrong passage: the contract descriptor (party names) dominates BM25, so preamble "
             "and signature chunks win. Route to the named contract first, then score chunks with the question only.",
             lambda c: {"doc_routing": True, "query_mode": "question_only"},
             lambda c: not (c.doc_routing and c.query_mode == "question_only")),
    Proposal("route_and_question_only", "false_abstention",
             "Answerable queries abstain because no top passage contains the question's words: the descriptor "
             "dominates ranking. Route by descriptor, rank by question.",
             lambda c: {"doc_routing": True, "query_mode": "question_only"},
             lambda c: not (c.doc_routing and c.query_mode == "question_only")),
    Proposal("doc_top_n_one", "right_document_wrong_section",
             "Routing confidence is high; search only the single best-matching contract.",
             lambda c: {"doc_top_n": 1}, lambda c: c.doc_routing and c.doc_top_n > 1),
    Proposal("doc_routing_on", "wrong_document",
             "Queries name the contract ('Consider the X agreement; ...'); restricting search to the "
             "best-matching contracts should remove hits from look-alike clauses in other contracts.",
             lambda c: {"doc_routing": True, "doc_top_n": 3}, lambda c: not c.doc_routing),
    Proposal("title_prefix_on", "wrong_document",
             "Chunks lose the contract identity; prepending the file-name title lets the descriptor "
             "terms match the right contract's chunks.",
             lambda c: {"title_prefix": True}, lambda c: not c.title_prefix),
    Proposal("doc_top_n_up", "wrong_document",
             "Routing may cut the right contract; widen the routed set.",
             lambda c: {"doc_top_n": c.doc_top_n + 2}, lambda c: c.doc_routing),
    Proposal("question_only", "right_document_wrong_section",
             "Once the contract is routed, descriptor words (party names) dominate chunk scores and "
             "favour the preamble; score chunks with the question only.",
             lambda c: {"query_mode": "question_only"},
             lambda c: c.doc_routing and c.query_mode != "question_only"),
    Proposal("recursive_chunker", "right_document_wrong_section",
             "Fixed windows cut clauses mid-sentence; split on paragraph/sentence boundaries.",
             lambda c: {"chunker": "recursive", "chunk_overlap": 0}, lambda c: c.chunker == "fixed"),
    Proposal("clause_chunker", "right_document_wrong_section",
             "Align chunks to section headings so each chunk holds one clause.",
             lambda c: {"chunker": "clause", "chunk_overlap": 0}, lambda c: c.chunker != "clause"),
    Proposal("stemming_on", "right_document_wrong_section",
             "Vocabulary mismatch ('terminate' vs 'termination'); add light stemming.",
             lambda c: {"stem": True}, lambda c: not c.stem),
    Proposal("hybrid_dense", "right_document_wrong_section",
             "Lexical overlap misses paraphrases; fuse BM25 with a dense encoder (RRF).",
             lambda c: {"retriever": "hybrid"},
             lambda c: c.retriever == "bm25" and dense_available()),
    Proposal("cross_encoder_rerank", "right_document_wrong_section",
             "Re-score the top candidates jointly with the question using a cross-encoder.",
             lambda c: {"rerank": True}, lambda c: not c.rerank and dense_available()),
    Proposal("bigger_chunks", "partial_span",
             "Gold spans are only partly covered; larger chunks capture whole clauses.",
             lambda c: {"chunk_size": int(c.chunk_size * 1.6)}, lambda c: c.chunk_size < 1500),
    Proposal("neighbor_expand", "partial_span",
             "Return the neighbouring chunk with each hit to cover clauses that span a boundary.",
             lambda c: {"neighbor_expand": 1}, lambda c: c.neighbor_expand == 0),
    Proposal("smaller_chunks", "ok",
             "Recall is healthy; smaller chunks would raise precision.",
             lambda c: {"chunk_size": max(200, int(c.chunk_size * 0.6))}, lambda c: c.chunk_size > 250),
    # parameter search fallbacks
    Proposal("bm25_b_low", "any", "Long contracts are over-penalised; lower BM25 length normalisation.",
             lambda c: {"bm25_b": 0.5}, lambda c: c.bm25_b != 0.5),
    Proposal("bm25_k1_high", "any", "Let repeated terms count more (k1 up).",
             lambda c: {"bm25_k1": 1.8}, lambda c: c.bm25_k1 != 1.8),
    Proposal("bm25_b_high", "any", "Stronger length normalisation favours focused chunks.",
             lambda c: {"bm25_b": 0.9}, lambda c: c.bm25_b != 0.9),
]


def summarise(per_query: list[dict]) -> dict:
    counts: dict = {}
    for r in per_query:
        if r["answerable"]:
            counts[r["diagnosis"]] = counts.get(r["diagnosis"], 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def propose(cfg: Config, failures: dict, tried: set) -> Proposal | None:
    order = [k for k in failures if k != "ok"] + ["ok", "any"]
    for cat in order:
        for p in PROPOSALS:
            if p.trigger != cat or not p.available(cfg):
                continue
            fingerprint = cfg.replace(**p.change(cfg)).key()
            if fingerprint in tried:
                continue
            return p
    return None


def accept(cur: dict, cand: dict, cur_rows: list, cand_rows: list, k: int) -> tuple[bool, str]:
    m0, m1 = cur, cand
    gain = m1[f"R@{k}"] - m0[f"R@{k}"]
    by_q = {r["qid"]: r for r in cur_rows if r["answerable"]}
    better = sum(1 for r in cand_rows if r["answerable"] and r[f"R@{k}"] > by_q[r["qid"]][f"R@{k}"] + 1e-9)
    worse = sum(1 for r in cand_rows if r["answerable"] and r[f"R@{k}"] < by_q[r["qid"]][f"R@{k}"] - 1e-9)
    reasons = []
    p0, p1 = m0[f"P@{k}"], m1[f"P@{k}"]
    precision_path = gain >= -MIN_GAIN and p0 > 0 and p1 >= (1 + PRECISION_GAIN) * p0
    if not precision_path:
        if gain < MIN_GAIN:
            reasons.append(f"R@{k} gain {gain:+.4f} < {MIN_GAIN}")
        if better <= worse:
            reasons.append(f"per-query sign check failed ({better} better / {worse} worse)")
    if m1[f"P@{k}"] < PRECISION_KEEP * m0[f"P@{k}"]:
        reasons.append(f"guardrail P@{k} {m1[f'P@{k}']:.4f} < 90% of {m0[f'P@{k}']:.4f}")
    b0, b1 = m0["abstention_balanced_acc"], m1["abstention_balanced_acc"]
    if b0 == b0 and b1 == b1 and b1 < b0 - BAL_ACC_DROP:
        reasons.append(f"guardrail abstention bal.acc {b1:.3f} < {b0:.3f}-{BAL_ACC_DROP}")
    fa_limit = max(MAX_FALSE_ABST, m0["false_abstention_rate"])  # never worse than now, target <= 10%
    if m1["false_abstention_rate"] > fa_limit + 1e-9:
        reasons.append(f"guardrail false abstention {m1['false_abstention_rate']:.3f} > {fa_limit:.3f}")
    summary = (f"R@{k} {gain:+.4f}, P@{k} {p1 - p0:+.4f}; {better} queries better / {worse} worse"
               + (" [precision path]" if precision_path else ""))
    return (not reasons, summary if not reasons else summary + "; REJECT: " + "; ".join(reasons))


def _metric_view(m: dict, k: int) -> dict:
    keys = [f"R@{k}", f"P@{k}", f"DocHit@{k}", "R@1", "R@4", "R@32", "false_abstention_rate",
            "correct_abstention_rate", "abstention_balanced_acc"]
    return {x: round(m[x], 4) for x in keys if x in m}


def run_loop(cfg: Config, docs: dict, queries: list, iterations: int = 10,
             out_dir: str | Path = "experiments", final_path: str | Path = "configs/final.yaml") -> Config:
    train_only = [q for q in queries if q.split == "train"]  # the loop never sees test
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "log.jsonl"
    k = cfg.primary_k

    cur = evaluate(cfg, docs, train_only, "train")
    print("baseline", headline(cur["metrics"], k))
    tried = {cfg.key()}
    entries = [{"iteration": 0, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "proposal": "baseline",
                "proposed_by": "human", "rationale": "simplest reasonable pipeline",
                "changes": {}, "decision": "baseline", "detail": "",
                "failures_before": summarise(cur["per_query"]),
                "metrics": _metric_view(cur["metrics"], k), "config": cfg.to_dict()}]

    for it in range(1, iterations + 1):
        failures = summarise(cur["per_query"])
        p = propose(cfg, failures, tried)
        if p is None:
            print("no untried proposals left")
            break
        changes = p.change(cfg)
        cand_cfg = cfg.replace(name=f"iter{it}", **changes)
        tried.add(cand_cfg.key())
        cand = evaluate(cand_cfg, docs, train_only, "train")
        ok, detail = accept(cur["metrics"], cand["metrics"], cur["per_query"], cand["per_query"], k)
        print(f"iter {it}: {p.name} {changes} -> {'ACCEPT' if ok else 'reject'} | {detail}")
        entries.append({"iteration": it, "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "proposal": p.name, "proposed_by": f"rules (trigger: {p.trigger})",
                        "rationale": p.rationale, "changes": changes,
                        "decision": "accepted" if ok else "rejected", "detail": detail,
                        "failures_before": failures,
                        "metrics": _metric_view(cand["metrics"], k)})
        if ok:
            cfg, cur = cand_cfg, cand

    with open(log_path, "a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    _write_markdown_log(entries, out_dir / "LOG.md", k)

    final = cfg.replace(name="final", doc_threshold=cur["metrics"]["doc_threshold"],
                        clause_threshold=cur["metrics"]["clause_threshold"])
    final.save(final_path)
    print("final", headline(cur["metrics"], k), "->", final_path)
    return final


def _write_markdown_log(entries: list, path: Path, k: int) -> None:
    lines = ["# Improvement loop log (train split only)", "",
             f"Primary metric: R@{k}. Accept rule: (R@{k} gain >= {MIN_GAIN} and more queries better than worse) "
             f"or (R@{k} loss <= {MIN_GAIN} and P@{k} +{int(PRECISION_GAIN*100)}% relative); guardrails must hold "
             "(see contract_search/loop.py).", "",
             f"| it | proposal | proposed by | changes | R@{k} | P@{k} | DocHit@{k} | false abst | correct abst | decision |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for e in entries:
        m = e["metrics"]
        lines.append(f"| {e['iteration']} | {e['proposal']} | {e['proposed_by']} | `{json.dumps(e['changes'])}` | "
                     f"{m.get(f'R@{k}', 0):.4f} | {m.get(f'P@{k}', 0):.4f} | {m.get(f'DocHit@{k}', 0):.3f} | "
                     f"{m.get('false_abstention_rate', 0):.3f} | {m.get('correct_abstention_rate', 0):.3f} | "
                     f"{e['decision']} |")
    lines += ["", "## Details", ""]
    for e in entries:
        lines.append(f"**{e['iteration']}. {e['proposal']}** ({e['decision']}) — {e['rationale']}  ")
        lines.append(f"Failures before: `{json.dumps(e['failures_before'])}`  ")
        if e["detail"]:
            lines.append(f"Result: {e['detail']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
