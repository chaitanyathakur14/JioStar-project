import random

import pytest

from contract_search.chunking import chunk_document
from contract_search.config import Config
from contract_search.data import assign_split, load_all, mini, verify_offsets
from contract_search.evaluate import evaluate
from contract_search.index import BM25, Index
from contract_search.loop import run_loop
from contract_search.metrics import char_precision_recall, merge_intervals
from contract_search.retrieve import Searcher
from contract_search.text import split_query, tokenize

DOC = ("1. Definitions\n\n\"Content\" means the films listed in Exhibit A.\n\n"
       "2. Grant of Rights\n\nLicensor grants Licensee an exclusive license. Licensee may not sublicense.\n\n"
       "3. Term\n\nThe term ends on December 31, 2027. " + "Filler sentence here. " * 60)


# ---------------------------------------------------------------- data
def test_split_is_deterministic_and_roughly_30_percent():
    qs = [f"question {i}" for i in range(2000)]
    test_share = sum(assign_split(q) == "test" for q in qs) / len(qs)
    assert 0.25 < test_share < 0.35
    assert assign_split("  hello ") == assign_split("hello")


def test_mini_is_order_independent():
    tests = [{"snippets": [{"file_path": f"f{i}"}], "i": i} for i in range(300)]
    a = mini(tests)
    shuffled = tests[:]
    random.Random(1).shuffle(shuffled)
    assert [t["i"] for t in a] == [t["i"] for t in mini(shuffled)]
    assert len(a) == 194


# ---------------------------------------------------------------- chunking
@pytest.mark.parametrize("method", ["fixed", "recursive", "clause"])
@pytest.mark.parametrize("size", [80, 200, 500])
def test_chunks_preserve_offsets_and_size(method, size):
    chunks = chunk_document("d", DOC, method, size, overlap=20 if method == "fixed" else 0)
    assert chunks
    for c in chunks:
        assert c.end - c.start <= size
        assert DOC[c.start:c.end].strip() == DOC[c.start:c.end]
    covered = "".join(DOC[c.start:c.end] for c in chunks)
    assert "Licensee may not sublicense" in covered or method == "fixed"


def test_clause_chunker_does_not_straddle_sections():
    chunks = chunk_document("d", DOC, "clause", 500)
    for c in chunks:
        text = DOC[c.start:c.end]
        assert not ("Grant of Rights" in text and "The term ends" in text)


# ---------------------------------------------------------------- text
def test_split_query():
    d, q = split_query("Consider the License Agreement between A Inc and B LLC; When does it end?")
    assert d == "License Agreement between A Inc and B LLC" and q == "When does it end?"
    assert split_query("When does it end?") == ("", "When does it end?")


def test_tokenize_stem():
    assert tokenize("Terminations of the Licenses", stem=True) == ["termin", "licens"]


# ---------------------------------------------------------------- metrics
def test_merge_intervals():
    assert merge_intervals([(5, 10), (0, 3), (8, 12), (12, 14)]) == [(0, 3), (5, 14)]


def test_char_precision_recall():
    gold = [("d", 10, 20)]
    assert char_precision_recall([("d", 10, 20)], gold) == (1.0, 1.0)
    p, r = char_precision_recall([("d", 0, 20)], gold)
    assert p == pytest.approx(0.5) and r == 1.0
    p, r = char_precision_recall([("d", 15, 30), ("d", 0, 12)], gold)
    assert r == pytest.approx(0.7) and p == pytest.approx(7 / 27)
    assert char_precision_recall([("other", 10, 20)], gold) == (0.0, 0.0)
    assert char_precision_recall([], gold) == (0.0, 0.0)
    # overlapping retrieved passages are not double counted
    assert char_precision_recall([("d", 10, 20), ("d", 10, 20)], gold) == (1.0, 1.0)


# ---------------------------------------------------------------- bm25
def test_bm25_ranks_matching_doc_first():
    bm = BM25([["cat", "sat"], ["dog", "barked", "loud"], ["sublicense", "rights", "third", "party"]])
    s = bm.score(["sublicense", "third"])
    assert s.argmax() == 2 and s[0] == 0
    assert bm.term_idf("unseen") >= bm.term_idf("cat")


# ---------------------------------------------------------------- end to end
def test_offsets_verify(dataset):
    root, up = dataset
    queries, docs = load_all(root, up)
    assert verify_offsets(queries, docs) == []
    assert sum(not q.answerable for q in queries) == 24


def test_search_finds_clause_and_abstains(dataset):
    root, up = dataset
    queries, docs = load_all(root, up)
    cfg = Config(chunker="recursive", chunk_size=300, doc_routing=True, query_mode="question_only")
    s = Searcher(Index(cfg, docs), cfg.replace(doc_threshold=0.5, clause_threshold=0.3))
    r = s.search("Consider the License Agreement between Acme Media Inc and Blue River Studios LLC; "
                 "Who owns intellectual property in derivative works?", 3)
    assert not r.abstained
    assert "AcmeMedia" in r.passages[0].doc_id and "derivative works" in r.passages[0].text
    r2 = s.search("Consider the Format License between Zyxquor Pictures and Plimbeth Media; What is the fee?", 3)
    assert r2.abstained and "corpus" in r2.reason


def test_evaluate_and_loop_end_to_end(dataset, tmp_path):
    root, up = dataset
    queries, docs = load_all(root, up)
    base = Config(k_values=[1, 4, 8], primary_k=8)
    out = evaluate(base, docs, queries, "train")
    m = out["metrics"]
    assert 0 <= m["R@8"] <= 1 and m["n_answerable"] > 0 and m["n_unanswerable"] > 0
    assert m["false_abstention_rate"] <= base.max_false_abstention + 1e-9
    final = run_loop(base, docs, queries, iterations=5, out_dir=tmp_path, final_path=tmp_path / "final.yaml")
    log = (tmp_path / "log.jsonl").read_text().strip().splitlines()
    assert len(log) >= 6  # baseline + 5 iterations
    assert (tmp_path / "LOG.md").exists() and (tmp_path / "final.yaml").exists()
    after = evaluate(final, docs, queries, "train")["metrics"]
    assert after["R@8"] >= m["R@8"]
