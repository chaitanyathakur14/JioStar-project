"""Build the frozen unanswerable query set (data/unanswerable.json).

= handwritten queries (data/unanswerable_handwritten.json)
+ "contract_present_topic_absent" queries: a REAL contract descriptor taken
  from the CUAD-mini queries, paired deterministically with a media-industry
  question that CUAD commercial contracts do not address. These are the
  hardest negatives: the contract exists, the clause does not.

Run ONCE after downloading the data, review the output (the script prints the
corpus hits for each question's key term so you can drop any that a contract
actually answers), then commit data/unanswerable.json BEFORE running the loop.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from contract_search.data import assign_split, load_benchmark, load_corpus  # noqa: E402
from contract_search.text import split_query  # noqa: E402

MEDIA_QUESTIONS = [
    ("What frame rate must delivered video masters use?", "frame rate"),
    ("Which subtitle languages must be delivered with the content?", "subtitle"),
    ("What is the holdback window before an SVOD premiere?", "svod"),
    ("Who pays the performing rights society fees for music cue sheets?", "cue sheet"),
    ("What blackout restrictions apply to live sports streaming?", "blackout"),
    ("Can episodes be clipped into short vertical videos for social media?", "vertical video"),
    ("What audio loudness level in LUFS is required for deliverables?", "lufs"),
    ("Which censor board certificate is required before release?", "censor"),
    ("Who has casting approval over the lead actors?", "casting"),
    ("How long is the catch-up viewing window after a live telecast?", "catch-up"),
    ("What dubbing languages does the licensee receive rights to?", "dubbing"),
    ("How many ad breaks per hour are permitted during streaming?", "ad break"),
]
N_GENERATED = 12


def main(data_root="data/legalbench-rag"):
    bench = load_benchmark(data_root)
    docs = load_corpus(data_root, bench)
    descriptors = {}
    for q in bench:
        d, _ = split_query(q.text)
        if d:
            descriptors[d] = q.spans[0].doc_id
    ordered = sorted(descriptors, key=lambda d: hashlib.sha256(d.encode()).hexdigest())
    hand = json.loads(Path("data/unanswerable_handwritten.json").read_text(encoding="utf-8"))
    gen = []
    for i, desc in enumerate(ordered[:N_GENERATED]):
        question, term = MEDIA_QUESTIONS[i % len(MEDIA_QUESTIONS)]
        doc = docs[descriptors[desc]].lower()
        hits = doc.count(term)
        print(f"[{'CHECK' if hits else 'ok   '}] '{term}' x{hits} in {descriptors[desc]}")
        gen.append({"type": "contract_present_topic_absent",
                    "query": f"Consider the {desc}; {question}",
                    "doc_id_named": descriptors[desc]})
    allq = hand + gen
    Path("data/unanswerable.json").write_text(json.dumps(allq, indent=1), encoding="utf-8")
    counts = {}
    for it in allq:
        counts[assign_split(it["query"])] = counts.get(assign_split(it["query"]), 0) + 1
    print(f"wrote {len(allq)} unanswerable queries -> data/unanswerable.json ; split counts {counts}")
    print("Review any CHECK lines, then: git add data/unanswerable.json && git commit")


if __name__ == "__main__":
    main(*sys.argv[1:])
