"""Dump concrete failures, grouped by diagnosed cause, with the gold text and
what the system returned -> results/errors.md. Use it to write the error
analysis section of REPORT.md (add your own diagnosis under each example).

    python scripts/error_examples.py results/final_train.json [per_group]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from contract_search.data import read_doc  # noqa: E402

DATA = Path("data/legalbench-rag/corpus")


def snippet(doc_id, s, e, n=350):
    try:
        t = read_doc(DATA / doc_id)[s:e]
    except FileNotFoundError:
        return "(doc not found)"
    t = " ".join(t.split())
    return t[:n] + ("…" if len(t) > n else "")


def main(path, per_group=4):
    rows = json.loads(Path(path).read_text())["per_query"]
    groups = defaultdict(list)
    for r in rows:
        if r["diagnosis"] not in ("ok", "correct_abstention"):
            groups[r["diagnosis"]].append(r)
    out = [f"# Failure examples from {path}", ""]
    for cause, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        out += [f"## {cause} ({len(items)} queries)", ""]
        for r in items[: int(per_group)]:
            out.append(f"**Q:** {r['query']}  ")
            out.append(f"doc_conf={r['doc_conf']} clause_conf={r['clause_conf']} abstained={r['abstained']}  ")
            for g in r.get("gold", [])[:2]:
                out.append(f"- GOLD `{g[0].split('/')[-1]}` [{g[1]}:{g[2]}]: {snippet(*g)}")
            for t in r.get("top", [])[:2]:
                out.append(f"- GOT  `{t[0].split('/')[-1]}` [{t[1]}:{t[2]}]: {snippet(*t, n=250)}")
            out += ["- DIAGNOSIS: _(write why this failed)_", ""]
    Path("results/errors.md").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote results/errors.md ({sum(len(v) for v in groups.values())} failures)")


if __name__ == "__main__":
    main(*sys.argv[1:])
