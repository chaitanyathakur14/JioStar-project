# Evaluation Report — Contract Clause Search

## 1. Summary

I built a lexical clause-search system over the 29 CUAD contracts referenced by LegalBench-RAG-mini. It
works in four steps:

1. Route each question to the contract it names.
2. Rank that contract's clause-aware chunks with BM25 using only the question text.
3. Return the top passages with document and character offsets.
4. Abstain when the named contract isn't in the corpus, or when no top passage covers the question's rare
   terms.

A rule-based improvement loop, run on train only, took the system from the naive baseline to the final
configuration. On the held-out test split (54 answerable + 17 unanswerable queries):

| Metric | Final | Baseline |
|---|---|---|
| Character recall@8 | **0.361** | 0.135 |
| Precision@8 | **0.065** | 0.016 |
| Correct abstention, unanswerable queries | **17/17** | 2/17 |
| False abstention, answerable queries | **3/54 (5.6%)** | 57% |

Test-set runs are listed in `results/test_runs.log`; §4 explains why there are six entries.

## 2. System design

| Decision | Final choice | Alternatives considered |
|---|---|---|
| Retriever | BM25 implemented directly on a sparse term-weight matrix (`index.py`) | TF-IDF, dense (MiniLM) and hybrid RRF are implemented and configurable. Lexical matching suits legal questions that share rare, exact vocabulary with the answering clause. BM25 needs no GPU and keeps contract text on the machine. Dense was not evaluated in the loop (optional dependency, not installed). |
| Chunking | clause-aware, max 500 chars: split at section headings, then paragraph/sentence boundaries | fixed 500-char windows (baseline), recursive (paragraph/sentence) splitting, 300 and 800 chars. The loop measured each one. |
| Contract routing | the "Consider the X;" descriptor is matched by BM25 against each contract's file-name title and first 3,000 chars; chunks are searched only in the top 3 contracts | no routing (baseline); top 1 and top 5 (both measured, §6) |
| Query text for ranking | question only, after the contract is routed | full query including descriptor (baseline). Party names then dominate the ranking, see §6. |
| Text processing | stopwords, CUAD template words removed, light suffix stemming | no stemming |
| Abstention | two gates with thresholds fitted on train: (1) contract-match confidence; (2) best IDF coverage of the question in the top 5 passages | raw BM25 score thresholds, which aren't comparable across queries. Coverage is bounded in [0, 1] and explainable. |
| Configuration | YAML + dataclass. The loop edits config, never code. | — |

**Contract-match confidence** is the share of the descriptor's IDF mass found in the best-matching contract.
Party names are rare, so they dominate this score. A fictional company gets about 0.1, while real contracts
get at least 0.57 on train.

**Calibration.** Thresholds are fitted to maximise balanced accuracy on train, subject to a false-abstention
rate of at most 10%. If no threshold meets that cap, calibration falls back to the lowest achievable false
abstention.

## 3. LLM use

The pipeline and the loop use no LLM. Reasons:

1. **Privacy.** JioStar agreements are confidential. A hosted model would send contract text to a third
   party, and a local model needs GPU capacity for indexing and reranking.
2. **Retrieval is the task.** The lexical pipeline is measurable, cheap (whole evaluation in about a minute
   on a laptop CPU) and explainable.
3. **Time.** I put the time into a working loop and honest evaluation rather than the stretch goal.

The most promising place to add one is reranking the top ~30 candidates with a local model (e.g. Qwen via
Ollama), with outputs cached, judged by the same loop criterion. The two biggest error groups (§7) are
vocabulary mismatch and "right contract, wrong passage", which is exactly what a reranker targets.

## 4. Evaluation setup

**Queries.**

| Split | Benchmark | Unanswerable |
|---|---|---|
| Train | 140 | 19 |
| Test | 54 | 17 |

The 194 CUAD-mini queries are split with the given `assign_split`. The 36 unanswerable queries use the same
function; the split came out 19/17 rather than 70/30 by chance of the hash.

**Unanswerable set** (frozen and committed before the loop ran), three types of 12:
- named contracts that aren't in the corpus
- media-industry questions that name no contract
- real contract descriptions paired with media questions those contracts don't answer

**Retrieval metrics.** Character precision and recall at k ∈ {1, 2, 4, 8, 16, 32}, as defined in
LegalBench-RAG. Retrieved and gold intervals are unioned per document, so overlapping passages aren't
double-counted. Two variants:
- *Raw* scores the ranking.
- *Served* treats an abstention as returning nothing (P = R = 0).

DocHit@k is a diagnostic: any top-k passage comes from a gold contract.

**Abstention metrics.**
- Correct abstention: share of unanswerable queries answered with nothing.
- False abstention: share of benchmark queries answered with nothing.
- Balanced accuracy of the two.

**Protocol.**
- The loop and all tuning saw train only.
- Abstention thresholds are fitted on train and applied unchanged to test.
- Gold spans are used only for scoring.

**Test runs.** `results/test_runs.log` has six entries:
1. Four from the first full run. The first loop run accepted nothing, so final = baseline and all four
   numbers are identical.
2. One baseline rerun after fixing the loop.
3. One run of the final configuration.

The test results did not influence any decision; the loop fix came from train diagnostics (§6). The numbers
reported here are from runs 5 and 6.

## 5. Results

**Headline at k = 8.**

| config | split | n (ans + unans) | R@8 | P@8 | DocHit@8 | served R@8 | false abst. | correct abst. | bal. acc |
|---|---|---|---|---|---|---|---|---|---|
| baseline | train | 140 + 19 | 0.100 | 0.0130 | 1.000 | 0.085 | 0.521 | 0.421 | 0.450 |
| final | train | 140 + 19 | **0.383** | **0.0557** | 0.864 | 0.383 | **0.014** | **1.000** | **0.993** |
| baseline | test | 54 + 17 | 0.135 | 0.0164 | 1.000 | 0.065 | 0.574 | 0.118 | 0.272 |
| final | test | 54 + 17 | **0.361** | **0.0650** | 0.944 | 0.336 | **0.056** | **1.000** | **0.972** |

**Precision and recall at k, test (raw ranking).**

| config | P@1 | P@2 | P@4 | P@8 | P@16 | P@32 | R@1 | R@2 | R@4 | R@8 | R@16 | R@32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.000 | 0.000 | 0.004 | 0.016 | 0.010 | 0.008 | 0.000 | 0.000 | 0.039 | 0.135 | 0.172 | 0.227 |
| final | 0.086 | 0.095 | 0.094 | 0.065 | 0.046 | 0.030 | 0.072 | 0.180 | 0.315 | 0.361 | 0.490 | 0.623 |

**Precision and recall at k, train (raw ranking).**

| config | P@1 | P@2 | P@4 | P@8 | P@16 | P@32 | R@1 | R@2 | R@4 | R@8 | R@16 | R@32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.000 | 0.003 | 0.010 | 0.013 | 0.012 | 0.011 | 0.000 | 0.004 | 0.033 | 0.100 | 0.184 | 0.309 |
| final | 0.146 | 0.124 | 0.081 | 0.056 | 0.036 | 0.022 | 0.144 | 0.232 | 0.300 | 0.383 | 0.468 | 0.558 |

**Train/test gap.**

- **Recall.** R@8 is 0.383 on train and 0.361 on test (−0.022), so the loop does not appear to have overfit.
  It changed only five discrete settings, each accepted with a per-query sign check.
- **Shape of the curve.** Test R@1 is lower (0.072 vs 0.144) but R@4 and R@32 are higher. With 54 queries,
  one query is about 1.9 points of recall, so these differences are within noise.
- **False abstention** rose from 1.4% (2/140) to 5.6% (3/54). That's one extra query in absolute terms, but
  it shows the thresholds are tight.
- **Correct abstention is 100% on both splits.** I read that as a sign the unanswerable set is easier than
  real user questions, not as proof that abstention is solved (§8).
- **Precision stays low in absolute terms** (P@8 = 0.065). Gold spans are short, often a sentence, while
  8 × 500-char passages return about 4,000 characters. The LegalBench-RAG paper reports similarly low
  character precision for the same reason.

## 6. Iteration history

**Objective.** The primary metric is character **recall@8**. Missing the clause is the costly failure: a
lawyer who never sees it draws the wrong conclusion, and eight passages is a realistic reading budget.

**Guardrails.**
- P@8 must stay at or above 90% of its current value, so recall can't be bought with more text.
- Abstention balanced accuracy must not drop more than 0.03.
- False abstention must stay at or below 10%, or not get worse if the current config is already above it.

**Acceptance.** All guardrails must pass, plus one of two paths:
- **(a) Recall path:** R@8 gains at least 0.005 and more queries improve than worsen. The second condition
  is a cheap paired sign check that keeps the loop from accepting noise on 140 queries.
- **(b) Precision path:** R@8 changes by no more than ±0.005 and P@8 improves by at least 10% relative.

**How the loop works** (`python -m contract_search.cli loop`):
1. Evaluate on train and label every query: wrong document, right document but wrong section, partial span,
   false abstention, or OK.
2. Take the first untried proposal triggered by the most frequent failure type. Parameter-search fallbacks
   come last.
3. Evaluate the candidate and accept or reject it.
4. Log the change, the rationale, who proposed it, the metrics and the decision.

The proposer is rule-based: each rule maps a failure type to a hypothesis.

### Run 1 (`experiments/LOG_run1.md`): 9 proposals, all rejected

The baseline already had 52% false abstention, which breaks the absolute 10% false-abstention guardrail. So
every candidate was rejected, including `neighbor_expand`, which improved 38 queries and worsened none.
Calibration hit the same wall: no threshold met the cap, so it fell back to 0.

The diagnostics pointed at the real problem:
- DocHit@8 was 1.0, so the right contract was always found.
- Yet question-term coverage of the top passages was 0 for most answerable queries.
- Party names in the descriptor ("Consider the … between X and Y;") dominated BM25, so preamble and signature
  chunks won.
- The routing proposals were wired only to "wrong document" failures, which never occurred.

**Fixes, all to the loop and calibration, none to the metrics:**
1. The false-abstention guardrail became "≤ 10% or no worse than now".
2. Calibration falls back to minimum false abstention when the cap is infeasible.
3. Routing + question-only scoring is now also triggered by wrong-section and false-abstention failures.
4. CUAD template words ("reviewed by a lawyer") were added to the boilerplate list.

### Run 2 (`experiments/LOG.md`): 12 iterations, 4 accepted

| it | proposal | trigger | R@8 | P@8 | decision and reason |
|---|---|---|---|---|---|
| 0 | baseline | — | 0.100 | 0.0130 | — |
| 1 | route + question-only | wrong section | 0.292 | 0.0346 | **accepted**: 50 better / 16 worse |
| 2 | search top-1 contract | wrong section | +0.156 | +0.017 | rejected: abstention bal. acc 0.927 < 0.975 − 0.03 |
| 3 | recursive chunker | wrong section | 0.321 | 0.0441 | **accepted**: 27 / 21 |
| 4 | search top-1 contract | wrong section | +0.139 | +0.019 | rejected: abstention guardrail |
| 5 | clause chunker | wrong section | 0.340 | 0.0491 | **accepted**: 6 / 3 |
| 6 | search top-1 contract | wrong section | +0.128 | +0.018 | rejected: abstention guardrail |
| 7 | stemming | wrong section | **0.383** | **0.0557** | **accepted**: 16 / 8 |
| 8 | search top-1 contract | wrong section | +0.150 | +0.026 | rejected: abstention guardrail |
| 9 | title prefix on chunks | wrong document | 0.374 | 0.0525 | rejected: R@8 −0.009 |
| 10 | search top-5 contracts | wrong document | 0.326 | 0.0474 | rejected: 0 better / 10 worse |
| 11 | 800-char chunks | partial span | 0.476 | 0.0495 | rejected: P@8 below 90% of current |
| 12 | neighbour expansion | partial span | 0.509 | 0.0329 | rejected: P@8 guardrail |

Accepted rows show absolute values; rows 2–8 for top-1 show the change against the current config. Intermediate
accepted values are reconstructed from the logged gains, and `experiments/LOG.md` has the exact numbers.

**What I learned.**
- **Routing + question-only was the single biggest win.** It nearly tripled recall. It was also what made
  calibrated abstention possible: false abstention went from 52% to 1.4% by the final config.
- **Searching only the top-1 contract** was retried four times and improved recall by 0.13–0.16 each time,
  with almost no queries worse. The abstention guardrail blocked it every time. My reading: with one
  contract, the passages surfaced for unanswerable "real contract, missing topic" queries also cover more of
  the question's terms, so the two abstention distributions overlap more. This is a genuine
  recall-versus-abstention trade-off. A better abstention signal (§8) would unlock it.
- **Bigger chunks and neighbour expansion** raised R@8 by 0.09–0.13 but were blocked by the precision
  guardrail. That is the guardrail doing its job: they win by returning more text, not better text.
- **Searching more contracts (top-5) and title prefixes** made things worse. With routing already in place,
  extra contracts only add near-duplicate boilerplate.

## 7. Error analysis

Final config, train split, k = 8. Of 140 answerable queries:

| Cause | Count |
|---|---|
| OK | 55 |
| Right contract, wrong section | 53 |
| Wrong document | 19 |
| Partial span | 11 |
| False abstention | 2 |

I read all the examples in `results/errors.md`. The loop's automatic labels turned out to be too coarse:
"right document, wrong section" only means *some* top-8 passage came from the gold contract. Below, failures
are grouped by the cause I found on reading them, with the automatic label in brackets.

### 7.1 Routed set ranked flat: a same-type contract outranks the named one (largest group)

Routing keeps the top 3 contracts, but their chunks are then ranked purely on the question. If another
contract of the same type answers the generic question more literally, it wins.

1. **Fox Mobile / Glu Mobile amendment, "What is the expiration date?"** [wrong section]
   - Returned: two Sucampo *Strategic Alliance* passages about confidentiality and representations.
   - Gold: the "shall expire on December 31, 2006" sentence in the Glu contract.
   - Diagnosis: contract confidence was 1.0, so routing found Glu, but the flat ranking over 3 contracts
     let unrelated text win.
2. **Information System Associates / Rubicon strategic alliance, "expiration date?"** [wrong document]
   - The descriptor matched the *type* "Strategic Alliance Agreement" in two file names.
   - The party names don't appear in the gold file name (`DUOSTECHNOLOGIES…`, the filing company), so the
     Sucampo strategic alliance took both top slots.
3. **Same contract, "exclusivity agreement?"** [partial span]
   - Returned: Sucampo's interpretation clause and a Theravance *Service Agreement* definition.
   - The gold "exclusive, non-transferable license" text was below them.
4. **R.C. Boyd / Cano Petroleum sponsorship, "expiration date?"** [wrong document]
   - Returned: ArcGroup's and Vitamin Shoppe's *Sponsorship Agreements*, whose term clauses literally say
     "expire".
   - Gold: Cano's "ending on December 31, 2008".
5. **Town of Vinton / Roanoke Gas franchise, "expiration date?"** [wrong document]
   - Returned: PennTex *Transportation Agreement* survival clauses ("survive the expiration…").
   - Gold: "twenty (20) years, commencing on January 1, 2016".

**Diagnosis.** The routing confidence is computed but not used in ranking. A routed contract with confidence
1.0 is treated the same as the third-choice contract. This is why "search top-1 contract" gained 0.13–0.16
R@8 in every trial.

**Fix:**
- multiply chunk scores by the contract's routing score; or
- search only the top contract when its confidence is far ahead of the second.

The fix must be paired with a better abstention signal, because top-1 is what broke the abstention guardrail.

### 7.2 Vocabulary mismatch between question and clause

6. **HPIL / GINARES, "What is the expiration date?"**
   - Gold: "The term of this Agreement shall be one (1) year…". It contains neither "expiration" nor "date".
   - Returned: a Holiday RV clause that does say "expiring".
   - BM25 rewards literal overlap, so a duration phrased as a term loses.
7. **HPIL / GINARES, "Is there a cap on liability?"**
   - Gold: "the sole and exclusive remedy for money damages … shall be the rights to indemnification".
   - That is a cap in substance, with no "cap" or "limit" wording.
   - Returned: Loop Industries text that literally says "LIMITATIONS OF LIABILITY".
8. **Purolator / Dynamex, "exceptions to competitive restrictions?"** [false abstention]
   - Gold: "Dynamex … may provide pick-up and/or delivery services for other … courier service providers,
     provided…".
   - Almost no shared words, so question coverage was 0.27, below the threshold, and the system abstained.

**Diagnosis.** These are the paraphrase cases a dense retriever or cross-encoder reranker targets. Both are
implemented but not evaluated (§8). A query expansion map for CUAD categories would also help, e.g.
"expiration date" → "term, expire, terminate, years".

### 7.3 Chunk boundaries split the clause

9. **PC Quote / A.B. Watley, "cap on liability?"** [partial span]
   - The clause chunker made the heading "6. Limitations of Liability, Remedies On Default A." a 56-character
     chunk of its own. It ranked high because it is dense with question words.
   - The liability-cap body that follows was not returned.
   - Diagnosis: a clause-chunker bug. A bare heading should be merged into the following text, but my
     minimum-section merge doesn't catch headings followed by a sub-clause marker ("A.").
10. **BicycleTX / Crockett, "How is IP ownership assigned?"** [partial span]
    - The returned chunk [44547:45041] overlaps the start of the gold span [44840:45359], but the clause runs
      on past the chunk end.
    - Neighbour expansion fixes exactly this case, but the loop rejected it for lowering P@8 (§6).

### 7.4 Weak abstention signal on paraphrased questions

11. **PennTex / MRD gas transportation, "Is there uncapped liability?"** [false abstention]
    - The gold clause is a consequential-damages exclusion with a carve-out ("NO PARTY SHALL BE LIABLE …
      PROVIDED, HOWEVER…").
    - "Uncapped" never appears in it, and the top passages came from other routed contracts (Bon-Ton,
      Sucampo; see 7.1).
    - Coverage of 0.26 fell below the threshold. Two causes compound: flat ranking and lexical coverage.

### 7.5 Questionable gold labels

12. **BicycleTX / Crockett, "right of first refusal, first offer or first negotiation?"**
    - The gold spans describe share option grants ("you will be granted an option … to acquire 107,417
      ordinary shares"), not a ROFR/ROFO.
    - I'd argue no passage answers this question, so it would belong in the unanswerable set. Counting it as
      a miss is probably label noise.
13. **BicycleTX / Crockett, "exceptions to competitive restrictions?"** [partial span]
    - The system returned paragraphs 14.2–14.5 on restrictions.
    - Gold is the carve-out in 13.2 ("nothing in this paragraph shall prevent you from holding … up to three
      percent").
    - It's a defensible miss: the restriction clauses are relevant context a lawyer would also need.

### 7.6 Noise in the corpus
Redacted exhibits made of `[***]` placeholders and tables are indexed like any other text and sometimes
outrank real clauses.

## 8. Limitations and next steps

- **Definitions and cross-references are not resolved.** A clause on "Licensed Content as defined in
  Section 1" is retrieved without its definition. Next step: index-time expansion of defined terms and
  "Section X" links.
- **Routing confidence is not used in ranking** (§7.1). This is the largest single failure group and the
  next change I would make: weight chunk scores by contract-match score, then re-run the loop.
- **The automatic failure labels are too coarse.** "Right document" should check the *top-ranked* contract,
  not any of the top 8. Several "wrong section" failures were really wrong-contract failures.
- **Clause chunker heading bug** (§7.3): bare headings followed by sub-clause markers become their own
  chunks.
- **The abstention signal is lexical.** It can't tell "mentions the words" from "answers the question", and
  it is what blocked the top-1 routing gain. Next step: a cross-encoder or local-LLM relevance gate,
  measured with the same loop.
- **The unanswerable set is probably too easy.** 100% correct abstention on both splits reflects my own
  query set, not real users.
- **Small samples.** 54 answerable and 17 unanswerable test queries mean one query moves R@8 by about 2
  points and abstention rates by about 6 points. Bootstrap confidence intervals should come before any
  decision rests on these numbers.
- **Dense, hybrid and rerank were implemented but not evaluated**, because the optional dependency wasn't
  installed.
- **Before legal users rely on it:**
  - always show the passage in context with a link to the source
  - never present output as a legal conclusion
  - re-evaluate on JioStar's own media agreements, which differ from CUAD's commercial contracts
  - keep indexing and any model on-premise
  - log queries where users override the system, and feed them back into the evaluation set
