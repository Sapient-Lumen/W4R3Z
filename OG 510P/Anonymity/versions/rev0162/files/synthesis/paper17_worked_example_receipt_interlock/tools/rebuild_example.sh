#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python tools/materialize_example.py
python tools/emit_compare_report.py
python tools/validate_example.py
pdflatex -interaction=nonstopmode paper.tex >/dev/null
pdflatex -interaction=nonstopmode paper.tex >/dev/null
rm -f paper.aux paper.log paper.out
find . -type d -name __pycache__ -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
