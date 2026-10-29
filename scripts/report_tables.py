"""Turn results/*.json into markdown tables for REPORT.md -> results/tables.md"""
import json
import sys
from pathlib import Path

RES = Path("results")


def load(name):
    p = RES / f"{name}.json"
    return json.loads(p.read_text())["metrics"] if p.exists() else None


def fmt(x, d=3):
    return "–" if x is None or x != x else f"{x:.{d}f}"


def main():
    runs = [("baseline", "train"), ("final", "train"), ("baseline", "test"), ("final", "test")]
    ms = {r: load(f"{r[0]}_{r[1]}") for r in runs}
    ks = next((m for m in ms.values() if m), None)
    if ks is None:
        sys.exit("no results found; run the evaluation first")
    k_values = sorted(int(x.split("@")[1]) for x in ks if x.startswith("R@"))
    out = ["## Headline (k=8)", "",
           "| config | split | n answerable | n unanswerable | R@8 | P@8 | DocHit@8 | served R@8 | false abstention | correct abstention | balanced acc |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for (c, s), m in ms.items():
        if m:
            out.append(f"| {c} | {s} | {m['n_answerable']} | {m['n_unanswerable']} | {fmt(m['R@8'])} | {fmt(m['P@8'], 4)} | "
                       f"{fmt(m['DocHit@8'])} | {fmt(m['sR@8'])} | {fmt(m['false_abstention_rate'])} | "
                       f"{fmt(m['correct_abstention_rate'])} | {fmt(m['abstention_balanced_acc'])} |")
    for split in ("train", "test"):
        out += ["", f"## Precision / recall at k — {split} (raw ranking, before abstention)", "",
                "| config | " + " | ".join(f"P@{k}" for k in k_values) + " | " + " | ".join(f"R@{k}" for k in k_values) + " |",
                "|---|" + "---|" * (2 * len(k_values))]
        for c in ("baseline", "final"):
            m = ms.get((c, split))
            if m:
                out.append(f"| {c} | " + " | ".join(fmt(m[f'P@{k}'], 4) for k in k_values) + " | "
                           + " | ".join(fmt(m[f'R@{k}']) for k in k_values) + " |")
    out += ["", "## Failure causes (answerable queries at k=8; unanswerable shown as abstention outcome)", ""]
    for (c, s), m in ms.items():
        if m:
            out.append(f"- **{c} / {s}**: `{json.dumps(m['diagnosis_counts'])}`")
    Path(RES / "tables.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
