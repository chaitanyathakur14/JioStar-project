# Improvement loop log (train split only)

Primary metric: R@8. Accept rule: (R@8 gain >= 0.005 and more queries better than worse) or (R@8 loss <= 0.005 and P@8 +10% relative); guardrails must hold (see contract_search/loop.py).

| it | proposal | proposed by | changes | R@8 | P@8 | DocHit@8 | false abst | correct abst | decision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | baseline | human | `{}` | 0.1002 | 0.0130 | 1.000 | 0.521 | 0.421 | baseline |
| 1 | recursive_chunker | rules (trigger: right_document_wrong_section) | `{"chunker": "recursive", "chunk_overlap": 0}` | 0.0806 | 0.0115 | 1.000 | 0.593 | 0.474 | rejected |
| 2 | clause_chunker | rules (trigger: right_document_wrong_section) | `{"chunker": "clause", "chunk_overlap": 0}` | 0.0789 | 0.0116 | 1.000 | 0.593 | 0.474 | rejected |
| 3 | stemming_on | rules (trigger: right_document_wrong_section) | `{"stem": true}` | 0.1285 | 0.0172 | 1.000 | 0.450 | 0.368 | rejected |
| 4 | bigger_chunks | rules (trigger: partial_span) | `{"chunk_size": 800}` | 0.2247 | 0.0186 | 1.000 | 0.436 | 0.263 | rejected |
| 5 | neighbor_expand | rules (trigger: partial_span) | `{"neighbor_expand": 1}` | 0.2602 | 0.0146 | 1.000 | 0.521 | 0.421 | rejected |
| 6 | smaller_chunks | rules (trigger: ok) | `{"chunk_size": 300}` | 0.0515 | 0.0111 | 1.000 | 0.629 | 0.421 | rejected |
| 7 | bm25_b_low | rules (trigger: any) | `{"bm25_b": 0.5}` | 0.1021 | 0.0134 | 1.000 | 0.529 | 0.421 | rejected |
| 8 | bm25_k1_high | rules (trigger: any) | `{"bm25_k1": 1.8}` | 0.1044 | 0.0131 | 1.000 | 0.550 | 0.421 | rejected |
| 9 | bm25_b_high | rules (trigger: any) | `{"bm25_b": 0.9}` | 0.1025 | 0.0129 | 1.000 | 0.543 | 0.421 | rejected |

## Details

**0. baseline** (baseline) — simplest reasonable pipeline  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  

**1. recursive_chunker** (rejected) — Fixed windows cut clauses mid-sentence; split on paragraph/sentence boundaries.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 -0.0196, P@8 -0.0015; 9 queries better / 17 worse; REJECT: R@8 gain -0.0196 < 0.005; per-query sign check failed (9 better / 17 worse); guardrail P@8 0.0115 < 90% of 0.0130; guardrail false abstention 0.593 > 0.1

**2. clause_chunker** (rejected) — Align chunks to section headings so each chunk holds one clause.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 -0.0213, P@8 -0.0014; 9 queries better / 19 worse; REJECT: R@8 gain -0.0213 < 0.005; per-query sign check failed (9 better / 19 worse); guardrail P@8 0.0116 < 90% of 0.0130; guardrail false abstention 0.593 > 0.1

**3. stemming_on** (rejected) — Vocabulary mismatch ('terminate' vs 'termination'); add light stemming.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 +0.0283, P@8 +0.0042; 8 queries better / 6 worse [precision path]; REJECT: guardrail false abstention 0.450 > 0.1

**4. bigger_chunks** (rejected) — Gold spans are only partly covered; larger chunks capture whole clauses.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 +0.1245, P@8 +0.0056; 34 queries better / 10 worse [precision path]; REJECT: guardrail abstention bal.acc 0.414 < 0.450-0.03; guardrail false abstention 0.436 > 0.1

**5. neighbor_expand** (rejected) — Return the neighbouring chunk with each hit to cover clauses that span a boundary.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 +0.1600, P@8 +0.0015; 38 queries better / 0 worse [precision path]; REJECT: guardrail false abstention 0.521 > 0.1

**6. smaller_chunks** (rejected) — Recall is healthy; smaller chunks would raise precision.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 -0.0487, P@8 -0.0019; 5 queries better / 27 worse; REJECT: R@8 gain -0.0487 < 0.005; per-query sign check failed (5 better / 27 worse); guardrail P@8 0.0111 < 90% of 0.0130; guardrail abstention bal.acc 0.396 < 0.450-0.03; guardrail false abstention 0.629 > 0.1

**7. bm25_b_low** (rejected) — Long contracts are over-penalised; lower BM25 length normalisation.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 +0.0019, P@8 +0.0004; 1 queries better / 0 worse; REJECT: R@8 gain +0.0019 < 0.005; guardrail false abstention 0.529 > 0.1

**8. bm25_k1_high** (rejected) — Let repeated terms count more (k1 up).  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 +0.0042, P@8 +0.0001; 1 queries better / 3 worse; REJECT: R@8 gain +0.0042 < 0.005; per-query sign check failed (1 better / 3 worse); guardrail false abstention 0.550 > 0.1

**9. bm25_b_high** (rejected) — Stronger length normalisation favours focused chunks.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 +0.0023, P@8 -0.0001; 1 queries better / 1 worse; REJECT: R@8 gain +0.0023 < 0.005; per-query sign check failed (1 better / 1 worse); guardrail false abstention 0.543 > 0.1
