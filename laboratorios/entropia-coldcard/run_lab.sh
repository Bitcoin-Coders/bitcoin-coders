#!/usr/bin/env bash

set -euo pipefail

SAMPLES="${SAMPLES:-50000}"
SAMPLE_BYTES="${SAMPLE_BYTES:-32}"
STATE_BITS="${STATE_BITS:-20}"

mkdir -p data results

python3 generate_datasets.py \
  --samples "$SAMPLES" \
  --sample-bytes "$SAMPLE_BYTES" \
  --state-bits "$STATE_BITS" \
  --output-dir data

python3 analyze_entropy.py \
  data/uniform_reference.bin \
  --sample-bytes "$SAMPLE_BYTES" \
  --output results/uniform_report.json

python3 analyze_entropy.py \
  data/reduced_state.bin \
  --sample-bytes "$SAMPLE_BYTES" \
  --output results/reduced_report.json

python3 plot_results.py \
  --uniform data/uniform_reference.bin \
  --reduced data/reduced_state.bin \
  --sample-bytes "$SAMPLE_BYTES" \
  --output results/entropy_comparison.png

python3 compare_reports.py \
  --uniform results/uniform_report.json \
  --reduced results/reduced_report.json \
  --output results/summary.md

echo
echo "Experimento concluído."
echo
echo "Resultados:"
echo "  results/uniform_report.json"
echo "  results/reduced_report.json"
echo "  results/entropy_comparison.png"
echo "  results/summary.md"
