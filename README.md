# Contract Clause Search

*Chaitanya Thakur — JioStar take-home assignment*

## Overview

You ask a question about a contract, for example "Can the licensee sublicense to a third party?" or "When
does the exclusivity end?". The system answers with the passages most likely to contain the answer: the
contract they come from and the exact character offsets, so you can jump to the clause. If no passage is
relevant enough, it returns nothing and tells you why. Either the contract you named isn't in the corpus,
or nothing in it matches the question.

It runs on the CUAD part of LegalBench-RAG-mini (194 expert-annotated questions over 29 contracts) plus
36 unanswerable questions that I wrote myself. There's a command-line tool and a Streamlit web app. There's
also an evaluation harness for character-level precision/recall@k and abstention, and a self-improvement
loop that diagnoses what's going wrong and tries fixes by itself. It only ever sees the train split.

**Why I picked this up.** My earlier project was legal document summarization on 1,999 Indian Supreme Court
judgments, comparing TF-IDF, TextRank, BART and T5 with ROUGE, BERTScore and a blinded human evaluation.
That taught me two things I brought here:
- Legal text is long and repetitive, so finding the *right part* matters as much as processing it.
- An automatic metric only means something once you've looked at the cases where it disagrees with a
  human reading.

That's why this repo spends as much effort on evaluation and error analysis as on the retriever itself.

## Setup

- **Python:** 3.10 or newer. I developed and ran everything on Windows 11 with Python 3.13; the tests also
  pass on Linux.
- **API keys:** none needed. The default pipeline uses no LLM and makes no network calls at query time.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Mac / Linux
pip install -r requirements.txt

# optional: enables the dense / hybrid retriever and cross-encoder reranker proposals
pip install -r requirements-dense.txt
```

**Data.** This downloads only `benchmarks/cuad.json` and `corpus/cuad/` from the Hugging Face mirror into
`data/legalbench-rag/`:

```bash
python scripts/download_data.py
python -m contract_search.cli verify      # every gold span must match doc[start:end]
```

The unanswerable question set (`data/unanswerable.json`) is already committed and frozen. It was generated
once with `scripts/make_unanswerable.py` before the improvement loop ever ran; you can check this in the
commit history. Please don't re-run that script.

## How to run

| What | Command |
|---|---|
| Web app | `streamlit run app.py`, then open http://localhost:8501 |
| Ask a question (CLI) | `python -m contract_search.cli query "Consider the <contract>; Is sublicensing allowed?" -k 5` |
| Same, as JSON | add `--json` |
| Evaluate a config | `python -m contract_search.cli eval --config configs/final.yaml --split train` |
| Improvement loop | `python -m contract_search.cli loop --config configs/baseline.yaml --iterations 12` |
| Tests | `pytest -q` |

**Demo video:** [`docs/demo.mp4`](docs/demo.mp4) is a one-minute screen recording of the app answering a real question,
abstaining on a contract that isn't in the corpus, and abstaining on an off-topic question.

Tips:
- Start questions with **"Consider the \<contract description\>;"** to search one specific contract, which
  is the format the benchmark uses. Without that prefix, the whole corpus is searched.
- The app and `query` use `configs/final.yaml` by default. You can switch configs in the app's sidebar.

## Architecture

```
contract_search/
  data.py       load cuad.json → mini() → assign_split(); load only the referenced contracts; verify offsets
  text.py       tokenizer (stopwords, CUAD template words, optional stemming); splits "Consider the X; question"
  chunking.py   fixed | recursive | clause (section-heading aware); every chunk keeps exact offsets
  index.py      BM25 written from scratch on a sparse matrix, TF-IDF, optional dense encoder;
                plus a per-contract index (file-name title + opening text) used for routing
  retrieve.py   route to contract → score chunks → (fuse / rerank) → top-k passages → abstention signals
  metrics.py    character precision / recall (union of intervals, LegalBench-RAG definition)
  evaluate.py   calibrate abstention on train, compute metrics, label each failure with a cause
  loop.py       diagnose → propose → evaluate on train → accept / reject → log
  cli.py        command-line interface
app.py          Streamlit app
scripts/        data download, unanswerable-set builder, report tables, failure examples, reproduce.sh
configs/        baseline.yaml (starting point), final.yaml (written by the loop)
experiments/    LOG.md / log.jsonl (loop run 2), LOG_run1.md (first run, see REPORT §6)
results/        metrics per config & split, tables.md, errors.md, test_runs.log
```

**What happens to one question:**
1. The "Consider the X;" part is matched against every contract, which gives a contract-match confidence
   and the candidate contracts.
2. The question part alone is matched against chunks of those contracts, which gives a ranked list.
3. Two numbers decide whether to abstain: how well the named contract matched, and how much of the
   question's rare vocabulary the best passages cover. Both thresholds are fitted on train.

**Configuration.** Every pipeline choice lives in a YAML file in `configs/`. The fields are documented in
`contract_search/config.py`. The loop only ever changes the config, never the code.

## Reproducing results

Run from the repo root after downloading the data.

Mac / Linux:
```bash
bash scripts/reproduce.sh
```

Windows (PowerShell), the same steps one at a time:
```
python -m contract_search.cli verify
python -m contract_search.cli eval --config configs/baseline.yaml --split train
python -m contract_search.cli loop --config configs/baseline.yaml --iterations 12
python -m contract_search.cli eval --config configs/final.yaml --split train
python -m contract_search.cli eval --config configs/baseline.yaml --split test
python -m contract_search.cli eval --config configs/final.yaml --split test
python scripts/report_tables.py
python scripts/error_examples.py results/final_train.json 4
```

Outputs:
- `results/tables.md` and `experiments/LOG.md` contain the numbers in REPORT.md.
- Every test-split run is appended to `results/test_runs.log`.

Rough timings on my laptop CPU (BM25 only):
- `verify`: a few seconds
- each `eval`: under a minute
- the 12-iteration loop: about 3–5 minutes
- the full sequence: about 10 minutes

The optional dense or reranker models add several minutes the first time. Embeddings are cached in
`cache/`.

## Assumptions

The brief left some things open, so here is what I assumed and why.

- **Mini set and split.** I used the authors' `mini()` and the given `assign_split()` exactly as provided,
  and indexed only the 29 contracts that the 194 queries refer to.
- **Offsets.** Files are read with `open(path, encoding="utf-8")` (default text mode), and `verify` checks
  every span before anything else runs.
- **Metric details.**
  - Precision and recall use the *union* of retrieved intervals per document, so two overlapping passages
    aren't counted twice.
  - I report two versions. *Raw* scores the ranking even when the system abstains. *Served* counts an
    abstention on an answerable question as returning nothing (P = R = 0).
- **Primary metric.** Recall@8, because missing the clause is the expensive mistake for a lawyer, and
  eight passages is a realistic amount to read. The guardrails are explained in REPORT §6.
- **Abstention thresholds** are fitted on train only. The fit maximises balanced accuracy with false
  abstention capped at 10%; if the cap is impossible to meet, it minimises false abstention instead.
- **Contract naming.** A question that starts with "Consider the …;" names a contract. Anything else
  searches all contracts.
- **Unanswerable set** (36 questions, 19 train / 17 test), three types of 12:
  - named contracts that aren't in the corpus
  - media-industry questions that name no contract (frame rates, LUFS, SVOD holdbacks…)
  - a real contract's description paired with a media question that contract doesn't answer, generated
    deterministically and checked with a keyword count against the named contract
- **No LLM.** Real contracts are confidential, and I wanted the evaluation to be cheap and reproducible.
  Reasons are in REPORT §3.
- **Dense / reranker** proposals are skipped automatically if `sentence-transformers` isn't installed. They
  weren't evaluated in my runs.
- **Loop fix between runs.** The first loop run rejected everything because of a guardrail design flaw. I
  fixed the loop logic (not the metrics or data) and ran it again. Both logs are kept, and the details are
  in REPORT §4 and §6.

## AI tool usage

I used **Claude (Anthropic)** as a coding assistant throughout:
- **Code and docs.** Claude wrote the first version of the code (data loading, chunkers, BM25, metrics,
  evaluation, loop, CLI, Streamlit app), the test suite, and drafts of this README and the report.
- **Debugging.** I ran everything on my own machine with the real data and brought the outputs back to
  Claude, and we fixed problems together:
  - a Windows path bug in the app
  - stale abstention thresholds in the cache
  - most importantly, the first loop run accepting nothing because the baseline itself broke the
    false-abstention guardrail
- **Error analysis.** Claude helped turn `results/errors.md` into the grouped failure analysis in the
  report. I read the examples and checked the diagnoses against the contracts.

I've gone through every module and can explain and change any part of it.
