# Evaluation Report — Contract Clause Search

> **TODO before submitting:** replace every `‹…›` placeholder with your own numbers. They come from
> `results/tables.md`, `experiments/LOG.md` and `results/errors.md`, which `scripts/reproduce.sh` produces.
> Then write the error-analysis diagnoses yourself. Delete this box.

## 1. Summary

I built a clause-search system over the CUAD contracts in LegalBench-RAG-mini. A question is routed to the
contract it names, contract chunks are ranked with BM25 (other retrievers are configurable), and the system
returns the top passages with document and character offsets. It abstains when the named contract is not in
the corpus, or when no top passage covers the question's key terms. On the held-out test split
(‹n›¹ answerable + ‹n› unanswerable queries), the final configuration reaches:

- character recall@8 of ‹x› (baseline ‹x›)
- precision@8 of ‹x› (baseline ‹x›)
- correct abstention on ‹x›% of unanswerable queries
- false abstention on ‹x›% of answerable queries

The test split was evaluated exactly twice, once for the baseline and once for the final config (see
`results/test_runs.log`).

## 2. System design

| Decision | Chosen | Alternatives considered / why |
|---|---|---|
| Retriever | BM25 implemented on a sparse matrix | TF-IDF; dense (MiniLM) and hybrid RRF are available as loop proposals. Legal questions share rare, exact vocabulary with the answering clause ("sublicense", "exclusivity", "governing law"), which favours lexical matching. BM25 also needs no GPU and keeps data local. |
| Chunking | fixed 500 (baseline); recursive and clause-aware chunkers as proposals | The paper's best CUAD setting used small recursive chunks. The clause chunker splits at section headings so a passage never straddles two clauses. |
| Contract routing | descriptor ("Consider the X;") matched against file-name title + first 3,000 chars | Without routing, near-identical boilerplate clauses from other contracts compete. Routing also gives a natural "contract not in corpus" signal. |
| Abstention | two calibrated gates: contract-match IDF coverage, then best question IDF coverage in the top-5 passages | Raw BM25 scores are not comparable across queries. IDF coverage is bounded in [0, 1] and interpretable ("72% of the rare question words appear in the passage"). Thresholds are fitted on train with a ≤10% false-abstention constraint. |
| Config | YAML + dataclass; the loop edits config, never code | Required for an automated loop and for reproducibility. |

Messy-contract handling:
- Title-prefixing chunks and routing address contract identity.
- The clause chunker addresses formatting.
- Cross-references ("as defined in Section 4.2") and definitions are **not** resolved. See §8.

## 3. LLM use

No LLM is used in the default pipeline or in the loop. Reasons:

1. **Privacy.** Real agreements are confidential, so a hosted LLM means sending contract text to a third
   party. A local model avoids that but adds GPU cost and latency.
2. **Scope.** Retrieval is the task, and the lexical pipeline is measurable and cheap.
3. **Time.** I prioritised a rigorous loop over an LLM stretch goal.

If one were added, the best place is reranking the top ~30 candidates with a local model (e.g. Qwen via
Ollama), with outputs cached so evaluation can be reproduced. It would be judged by the same loop criterion.
‹If you do add one, replace this section with the measured cost/benefit.›

## 4. Evaluation setup

**Queries.** The 194 CUAD-mini queries are split with `assign_split`: ‹n› train / ‹n› test. The 36
unanswerable queries split ‹n› train / ‹n› test (`python -m contract_search.cli verify` prints these counts).

**Retrieval metrics.** Character precision and recall at k ∈ {1, 2, 4, 8, 16, 32} (LegalBench-RAG
definition, using unions of intervals), plus DocHit@k (any top-k passage comes from a gold contract).
- Raw metrics score the ranking.
- Served metrics treat an abstention as returning nothing.

**Abstention metrics.**
- Correct-abstention rate on unanswerable queries.
- False-abstention rate on benchmark queries.
- Balanced accuracy of the two.

**Protocol.** All development and the loop used train only. Abstention thresholds are fitted on train and
applied unchanged to test. Gold spans are used only for scoring.

## 5. Results

‹paste the tables from results/tables.md›

| config | split | n | R@8 | P@8 | DocHit@8 | false abst. | correct abst. |
|---|---|---|---|---|---|---|---|
| baseline | train | ‹› | ‹› | ‹› | ‹› | ‹› | ‹› |
| final | train | ‹› | ‹› | ‹› | ‹› | ‹› | ‹› |
| baseline | test | ‹› | ‹› | ‹› | ‹› | ‹› | ‹› |
| final | test | ‹› | ‹› | ‹› | ‹› | ‹› | ‹› |

**Train/test gap.** ‹Discuss it. Examples: a few-point drop is expected because the loop selected changes on
train. The abstention gap is noisier because only ~12 unanswerable test queries exist, so one query moves
the rate by ~8 points.›

## 6. Iteration history

**Objective.** Primary metric: character **recall@8**. A missed clause is the costly failure, since a lawyer
who never sees the clause draws the wrong conclusion. Eight passages is a realistic reading budget.

**Guardrails.**
- P@8 must stay at or above 90% of its current value, so the system can't buy recall with ever-longer
  passages.
- Abstention balanced accuracy must not drop more than 0.03.
- False abstention must stay at or below 10%.

**Loop** (`python -m contract_search.cli loop`):
1. Evaluate on train and label each failure:
   - wrong document
   - right document but wrong section
   - partial span
   - false abstention
2. Pick the first untried rule-based proposal triggered by the most frequent failure. Parameter-search
   fallbacks run once the rules are exhausted.
3. Evaluate the candidate on train.
4. Accept if either path holds and all guardrails pass:
   - **(a) recall path:** R@8 gains at least 0.005 and more queries improve than worsen. The second
     condition is a sign check, so the loop doesn't accept noise on ~135 queries.
   - **(b) precision path:** R@8 changes by no more than ±0.005 and P@8 improves by at least 10%
     relative, i.e. same recall with less to read.

Every iteration is logged with what changed, why, who proposed it, metrics and the decision, including
rejections.

‹paste experiments/LOG.md table here and comment on 2–3 interesting accepts/rejects›

## 7. Error analysis

‹From results/errors.md, pick at least 10 failures, grouped by cause, and write your diagnosis under each.
Typical causes to look for:
- the question uses a CUAD category name the clause never uses (e.g. "anti-assignment" vs "may not assign")
- the gold span is a short date or party name buried in a long preamble
- the answer is spread over several non-adjacent spans
- the clause is reached only through a definition or cross-reference
- contract titles that are near-duplicates (amendments, exhibits)
- unanswerable queries that share vocabulary with real clauses (false answers)›

## 8. Limitations and next steps

- **Definitions and cross-references** are not resolved. A clause saying "Licensed Content as defined in
  Section 1" is retrieved without its definition. Next step: index-time expansion of defined terms and
  "Section X" links.
- **The abstention signal is lexical.** It can't tell "mentions the words" from "answers the question".
  A cross-encoder or local LLM relevance check should be measured as a gate.
- **Small evaluation sets.** About 58 answerable and about 12 unanswerable test queries give wide confidence
  intervals. Bootstrap CIs should be reported before any decision rests on these numbers.
- **The unanswerable set is mine.** It may be easier than real user questions.
- **Before legal users rely on it:**
  - always show the passage in context with a link to the source
  - never present it as a legal conclusion
  - evaluate on JioStar's own agreement types (media licences, not CUAD's commercial contracts)
  - keep everything on-premise

---
¹ Counts from `python -m contract_search.cli verify`.
