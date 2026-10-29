## Headline (k=8)

| config | split | n answerable | n unanswerable | R@8 | P@8 | DocHit@8 | served R@8 | false abstention | correct abstention | balanced acc |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | train | 140 | 19 | 0.100 | 0.0130 | 1.000 | 0.085 | 0.521 | 0.421 | 0.450 |
| final | train | 140 | 19 | 0.383 | 0.0557 | 0.864 | 0.383 | 0.014 | 1.000 | 0.993 |
| baseline | test | 54 | 17 | 0.135 | 0.0164 | 1.000 | 0.065 | 0.574 | 0.118 | 0.272 |
| final | test | 54 | 17 | 0.361 | 0.0650 | 0.944 | 0.336 | 0.056 | 1.000 | 0.972 |

## Precision / recall at k — train (raw ranking, before abstention)

| config | P@1 | P@2 | P@4 | P@8 | P@16 | P@32 | R@1 | R@2 | R@4 | R@8 | R@16 | R@32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0028 | 0.0098 | 0.0130 | 0.0121 | 0.0107 | 0.000 | 0.004 | 0.033 | 0.100 | 0.184 | 0.309 |
| final | 0.1456 | 0.1239 | 0.0814 | 0.0557 | 0.0361 | 0.0224 | 0.144 | 0.232 | 0.300 | 0.383 | 0.468 | 0.558 |

## Precision / recall at k — test (raw ranking, before abstention)

| config | P@1 | P@2 | P@4 | P@8 | P@16 | P@32 | R@1 | R@2 | R@4 | R@8 | R@16 | R@32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0000 | 0.0039 | 0.0164 | 0.0104 | 0.0080 | 0.000 | 0.000 | 0.039 | 0.135 | 0.172 | 0.227 |
| final | 0.0862 | 0.0953 | 0.0942 | 0.0650 | 0.0461 | 0.0297 | 0.072 | 0.180 | 0.315 | 0.361 | 0.490 | 0.623 |

## Failure causes (answerable queries at k=8; unanswerable shown as abstention outcome)

- **baseline / train**: `{"right_document_wrong_section": 45, "false_abstention": 73, "ok": 10, "partial_span": 12, "false_answer": 11, "correct_abstention": 8}`
- **final / train**: `{"right_document_wrong_section": 53, "ok": 55, "partial_span": 11, "wrong_document": 19, "false_abstention": 2, "correct_abstention": 19}`
- **baseline / test**: `{"ok": 2, "right_document_wrong_section": 15, "false_abstention": 31, "partial_span": 6, "false_answer": 15, "correct_abstention": 2}`
- **final / test**: `{"right_document_wrong_section": 21, "ok": 16, "false_abstention": 3, "partial_span": 11, "wrong_document": 3, "correct_abstention": 17}`
