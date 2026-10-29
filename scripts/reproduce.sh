#!/usr/bin/env bash
# Reproduce every number in REPORT.md from a fresh clone (data must be downloaded first).
set -euo pipefail
CLI="python -m contract_search.cli"

$CLI verify                                                   # offsets + split counts
$CLI eval --config configs/baseline.yaml --split train        # baseline, train
$CLI loop --config configs/baseline.yaml --iterations 12      # writes experiments/ + configs/final.yaml
$CLI eval --config configs/final.yaml --split train           # final, train
# test split: run ONCE per config, at the very end
$CLI eval --config configs/baseline.yaml --split test
$CLI eval --config configs/final.yaml --split test
python scripts/report_tables.py                               # -> results/tables.md
python scripts/error_examples.py results/final_train.json 4   # -> results/errors.md
