# Contract Clause Search

## Overview

Given a natural-language question about a contract, the system returns a ranked list of passages likely to
answer it, each with its source document and character offsets. When nothing is relevant enough, it returns
nothing and says why ("the named contract is not in the corpus" or "no relevant passage"). It runs on the
CUAD portion of LegalBench-RAG-mini (194 queries) plus a hand-built set of unanswerable queries. It ships
with a CLI, a Streamlit web app, an evaluation harness (character-level precision/recall@k plus abstention
metrics), and a self-improvement loop that changes the pipeline configuration based on diagnosed failures.

## Setup

- Python 3.10+ (developed on 3.13)
- No API keys: the default pipeline uses no LLM and no network at query time.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# optional: enables hybrid (BM25+dense) and cross-encoder reranking proposals in the loop
pip install -r requirements-dense.txt

# data (~CUAD corpus + benchmark only) -> data/legalbench-rag/
python scripts/download_data.py
```

The unanswerable set `data/unanswerable.json` is committed and frozen. It was built once with
`python scripts/make_unanswerable.py` from `data/unanswerable_handwritten.json`. Do not re-run that script.

## How to run

| What | Command |
|---|---|
| Check offsets and split counts | `python -m contract_search.cli verify` |
| Web app | `streamlit run app.py` |
| CLI search | `python -m contract_search.cli query "Consider the <contract>; Is sublicensing allowed?" -k 5` |
| CLI search (JSON output) | add `--json` |
| Evaluate a config | `python -m contract_search.cli eval --config configs/baseline.yaml --split train` |
| Improvement loop | `python -m contract_search.cli loop --config configs/baseline.yaml --iterations 12` |
| Tests | `pytest -q` |

`query` and the app use `configs/final.yaml` by default. Pass `--config` (or pick one in the app sidebar)
to use another.

## Architecture

```
data.py        load cuad.json -> mini(194) -> assign_split; load only referenced contracts; verify offsets
text.py        tokenizer (stopwords, optional stemming), "Consider the X; question" parser, file-name titles
chunking.py    fixed | recursive (paragraph/sentence) | clause (section-heading aware); offsets preserved
index.py       BM25 (own sparse implementation), TF-IDF, optional dense encoder; per-contract index for routing
retrieve.py    route to contracts -> score chunks -> (fuse/rerank) -> top-k passages -> abstention signals
evaluate.py    calibrate abstention on train, char P/R@k, DocHit@k, abstention rates, per-query diagnosis
loop.py        diagnose -> propose -> evaluate on train -> accept/reject -> log (experiments/)
cli.py, app.py interfaces
```

Data flow for one query: the parser splits off the contract descriptor. The descriptor is matched against the
per-contract index, which gives a contract-match confidence and, if routing is on, the candidate contracts.
The question is then matched against chunks of those contracts, giving a ranked list. Two signals decide
abstention: contract-match confidence and the share of the question's IDF mass covered by the best of the
top passages. Both thresholds are fitted on train.

**Configuration.** Every pipeline choice lives in a YAML file under `configs/`, with fields documented in
`contract_search/config.py`. `configs/baseline.yaml` is the starting point and `configs/final.yaml` is
written by the loop.

Outputs:
- `results/<config>_<split>.json` holds metrics plus per-query rows.
- `results/test_runs.log` records every test-split run.
- `experiments/log.jsonl` and `experiments/LOG.md` hold the loop history.

## Reproducing results

```bash
bash scripts/reproduce.sh
```

This runs `verify`, a baseline eval on train, the loop, a final eval on train, then baseline and final on
test (once each), and writes `results/tables.md` and `results/errors.md`.

Approximate times on a laptop CPU with BM25 only:
- index build: a few seconds per configuration
- eval: under a minute per split
- loop with 12 iterations: a few minutes

Dense or rerank proposals add several minutes the first time. Embeddings are cached in `cache/`.

## Assumptions

- **Mini selection and split** use the authors' `mini()` and the given `assign_split()` unchanged. Only
  contracts referenced by the 194 queries are indexed.
- **Offsets.** Files are read with `open(path, encoding="utf-8")`, i.e. default text mode. `verify` checks
  `doc[start:end] == answer` for every span.
- **Metric definition.** Character precision and recall use the *union* of retrieved intervals and the union
  of gold intervals per document, so overlapping passages are not double counted. "Raw" metrics score the
  ranking before abstention. "Served" metrics (`sP`, `sR`) count an abstention on an answerable query as
  P = R = 0.
- **Abstention thresholds** are fitted on train only. The objective maximises balanced accuracy over
  answerable and unanswerable train queries, subject to a false-abstention rate of at most 10%.
- **Contract naming.** Queries of the form "Consider the <contract>; <question>" name a contract. Queries
  without that prefix search the whole corpus.
- **Unanswerable set** (36 queries) covers three types:
  - 12 name contracts that are not in the corpus
  - 12 ask media-industry questions without naming a contract
  - 12 pair a real indexed contract's description with a media-specific question that contract does not
    answer. These are generated deterministically by `scripts/make_unanswerable.py`, and each was checked
    with a keyword count against the named contract.
- **No LLM** in the default pipeline. See REPORT.md for the reasoning.
- _Add any further assumptions you make here._

## AI tool usage

_Write this section yourself and make it accurate, for example: which assistant you used (e.g. Claude), for
which parts (scaffolding, specific modules, tests, docs), and what you reviewed, changed and verified by hand._
