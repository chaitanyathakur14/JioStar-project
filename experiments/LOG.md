# Improvement loop log (train split only)

Primary metric: R@8. Accept rule: (R@8 gain >= 0.005 and more queries better than worse) or (R@8 loss <= 0.005 and P@8 +10% relative); guardrails must hold (see contract_search/loop.py).

| it | proposal | proposed by | changes | R@8 | P@8 | DocHit@8 | false abst | correct abst | decision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | baseline | human | `{}` | 0.1002 | 0.0130 | 1.000 | 0.521 | 0.421 | baseline |
| 1 | route_and_question_only | rules (trigger: false_abstention) | `{"doc_routing": true, "query_mode": "question_only"}` | 0.2925 | 0.0346 | 0.857 | 0.050 | 1.000 | accepted |
| 2 | doc_top_n_one | rules (trigger: right_document_wrong_section) | `{"doc_top_n": 1}` | 0.4485 | 0.0518 | 1.000 | 0.093 | 0.947 | rejected |
| 3 | recursive_chunker | rules (trigger: right_document_wrong_section) | `{"chunker": "recursive", "chunk_overlap": 0}` | 0.3211 | 0.0441 | 0.864 | 0.043 | 1.000 | accepted |
| 4 | doc_top_n_one | rules (trigger: right_document_wrong_section) | `{"doc_top_n": 1}` | 0.4603 | 0.0629 | 1.000 | 0.093 | 0.895 | rejected |
| 5 | clause_chunker | rules (trigger: right_document_wrong_section) | `{"chunker": "clause", "chunk_overlap": 0}` | 0.3398 | 0.0491 | 0.857 | 0.043 | 1.000 | accepted |
| 6 | doc_top_n_one | rules (trigger: right_document_wrong_section) | `{"doc_top_n": 1}` | 0.4681 | 0.0674 | 1.000 | 0.093 | 0.947 | rejected |
| 7 | stemming_on | rules (trigger: right_document_wrong_section) | `{"stem": true}` | 0.3834 | 0.0557 | 0.864 | 0.014 | 1.000 | accepted |
| 8 | doc_top_n_one | rules (trigger: right_document_wrong_section) | `{"doc_top_n": 1}` | 0.5330 | 0.0812 | 1.000 | 0.057 | 0.947 | rejected |
| 9 | title_prefix_on | rules (trigger: wrong_document) | `{"title_prefix": true}` | 0.3743 | 0.0524 | 0.850 | 0.014 | 1.000 | rejected |
| 10 | doc_top_n_up | rules (trigger: wrong_document) | `{"doc_top_n": 5}` | 0.3263 | 0.0474 | 0.764 | 0.029 | 1.000 | rejected |
| 11 | bigger_chunks | rules (trigger: partial_span) | `{"chunk_size": 800}` | 0.4761 | 0.0495 | 0.886 | 0.021 | 1.000 | rejected |
| 12 | neighbor_expand | rules (trigger: partial_span) | `{"neighbor_expand": 1}` | 0.5084 | 0.0329 | 0.864 | 0.014 | 1.000 | rejected |

## Details

**0. baseline** (baseline) — simplest reasonable pipeline  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  

**1. route_and_question_only** (accepted) — Answerable queries abstain because no top passage contains the question's words: the descriptor dominates ranking. Route by descriptor, rank by question.  
Failures before: `{"false_abstention": 73, "right_document_wrong_section": 45, "partial_span": 12, "ok": 10}`  
Result: R@8 +0.1923, P@8 +0.0216; 50 queries better / 16 worse [precision path]

**2. doc_top_n_one** (rejected) — Routing confidence is high; search only the single best-matching contract.  
Failures before: `{"right_document_wrong_section": 58, "ok": 44, "wrong_document": 17, "partial_span": 14, "false_abstention": 7}`  
Result: R@8 +0.1560, P@8 +0.0172; 36 queries better / 1 worse [precision path]; REJECT: guardrail abstention bal.acc 0.927 < 0.975-0.03

**3. recursive_chunker** (accepted) — Fixed windows cut clauses mid-sentence; split on paragraph/sentence boundaries.  
Failures before: `{"right_document_wrong_section": 58, "ok": 44, "wrong_document": 17, "partial_span": 14, "false_abstention": 7}`  
Result: R@8 +0.0286, P@8 +0.0095; 27 queries better / 21 worse [precision path]

**4. doc_top_n_one** (rejected) — Routing confidence is high; search only the single best-matching contract.  
Failures before: `{"right_document_wrong_section": 60, "ok": 44, "wrong_document": 17, "partial_span": 13, "false_abstention": 6}`  
Result: R@8 +0.1392, P@8 +0.0188; 28 queries better / 0 worse [precision path]; REJECT: guardrail abstention bal.acc 0.901 < 0.979-0.03

**5. clause_chunker** (accepted) — Align chunks to section headings so each chunk holds one clause.  
Failures before: `{"right_document_wrong_section": 60, "ok": 44, "wrong_document": 17, "partial_span": 13, "false_abstention": 6}`  
Result: R@8 +0.0187, P@8 +0.0050; 6 queries better / 3 worse [precision path]

**6. doc_top_n_one** (rejected) — Routing confidence is high; search only the single best-matching contract.  
Failures before: `{"right_document_wrong_section": 58, "ok": 47, "wrong_document": 18, "partial_span": 11, "false_abstention": 6}`  
Result: R@8 +0.1283, P@8 +0.0183; 27 queries better / 1 worse [precision path]; REJECT: guardrail abstention bal.acc 0.927 < 0.979-0.03

**7. stemming_on** (accepted) — Vocabulary mismatch ('terminate' vs 'termination'); add light stemming.  
Failures before: `{"right_document_wrong_section": 58, "ok": 47, "wrong_document": 18, "partial_span": 11, "false_abstention": 6}`  
Result: R@8 +0.0436, P@8 +0.0065; 16 queries better / 8 worse [precision path]

**8. doc_top_n_one** (rejected) — Routing confidence is high; search only the single best-matching contract.  
Failures before: `{"ok": 55, "right_document_wrong_section": 53, "wrong_document": 19, "partial_span": 11, "false_abstention": 2}`  
Result: R@8 +0.1497, P@8 +0.0256; 32 queries better / 0 worse [precision path]; REJECT: guardrail abstention bal.acc 0.945 < 0.993-0.03

**9. title_prefix_on** (rejected) — Chunks lose the contract identity; prepending the file-name title lets the descriptor terms match the right contract's chunks.  
Failures before: `{"ok": 55, "right_document_wrong_section": 53, "wrong_document": 19, "partial_span": 11, "false_abstention": 2}`  
Result: R@8 -0.0091, P@8 -0.0032; 1 queries better / 2 worse; REJECT: R@8 gain -0.0091 < 0.005; per-query sign check failed (1 better / 2 worse)

**10. doc_top_n_up** (rejected) — Routing may cut the right contract; widen the routed set.  
Failures before: `{"ok": 55, "right_document_wrong_section": 53, "wrong_document": 19, "partial_span": 11, "false_abstention": 2}`  
Result: R@8 -0.0571, P@8 -0.0082; 0 queries better / 10 worse; REJECT: R@8 gain -0.0571 < 0.005; per-query sign check failed (0 better / 10 worse); guardrail P@8 0.0474 < 90% of 0.0557

**11. bigger_chunks** (rejected) — Gold spans are only partly covered; larger chunks capture whole clauses.  
Failures before: `{"ok": 55, "right_document_wrong_section": 53, "wrong_document": 19, "partial_span": 11, "false_abstention": 2}`  
Result: R@8 +0.0927, P@8 -0.0062; 31 queries better / 2 worse; REJECT: guardrail P@8 0.0495 < 90% of 0.0557

**12. neighbor_expand** (rejected) — Return the neighbouring chunk with each hit to cover clauses that span a boundary.  
Failures before: `{"ok": 55, "right_document_wrong_section": 53, "wrong_document": 19, "partial_span": 11, "false_abstention": 2}`  
Result: R@8 +0.1251, P@8 -0.0228; 33 queries better / 0 worse; REJECT: guardrail P@8 0.0329 < 90% of 0.0557
