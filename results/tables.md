## Headline (k=8)

| config | split | n answerable | n unanswerable | R@8 | P@8 | DocHit@8 | served R@8 | false abstention | correct abstention | balanced acc |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | train | 140 | 19 | 0.100 | 0.0130 | 1.000 | 0.085 | 0.521 | 0.421 | 0.450 |
| final | train | 140 | 19 | 0.100 | 0.0130 | 1.000 | 0.085 | 0.521 | 0.421 | 0.450 |
| baseline | test | 54 | 17 | 0.135 | 0.0164 | 1.000 | 0.065 | 0.574 | 0.118 | 0.272 |
| final | test | 54 | 17 | 0.135 | 0.0164 | 1.000 | 0.065 | 0.574 | 0.118 | 0.272 |

## Precision / recall at k — train (raw ranking, before abstention)

| config | P@1 | P@2 | P@4 | P@8 | P@16 | P@32 | R@1 | R@2 | R@4 | R@8 | R@16 | R@32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0028 | 0.0098 | 0.0130 | 0.0121 | 0.0107 | 0.000 | 0.004 | 0.033 | 0.100 | 0.184 | 0.309 |
| final | 0.0000 | 0.0028 | 0.0098 | 0.0130 | 0.0121 | 0.0107 | 0.000 | 0.004 | 0.033 | 0.100 | 0.184 | 0.309 |

## Precision / recall at k — test (raw ranking, before abstention)

| config | P@1 | P@2 | P@4 | P@8 | P@16 | P@32 | R@1 | R@2 | R@4 | R@8 | R@16 | R@32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0000 | 0.0039 | 0.0164 | 0.0104 | 0.0080 | 0.000 | 0.000 | 0.039 | 0.135 | 0.172 | 0.227 |
| final | 0.0000 | 0.0000 | 0.0039 | 0.0164 | 0.0104 | 0.0080 | 0.000 | 0.000 | 0.039 | 0.135 | 0.172 | 0.227 |

## Failure causes (answerable queries at k=8; unanswerable shown as abstention outcome)

- **baseline / train**: `{"right_document_wrong_section": 45, "false_abstention": 73, "ok": 10, "partial_span": 12, "false_answer": 11, "correct_abstention": 8}`
- **final / train**: `{"right_document_wrong_section": 45, "false_abstention": 73, "ok": 10, "partial_span": 12, "false_answer": 11, "correct_abstention": 8}`
- **baseline / test**: `{"ok": 2, "right_document_wrong_section": 15, "false_abstention": 31, "partial_span": 6, "false_answer": 15, "correct_abstention": 2}`
- **final / test**: `{"ok": 2, "right_document_wrong_section": 15, "false_abstention": 31, "partial_span": 6, "false_answer": 15, "correct_abstention": 2}`
