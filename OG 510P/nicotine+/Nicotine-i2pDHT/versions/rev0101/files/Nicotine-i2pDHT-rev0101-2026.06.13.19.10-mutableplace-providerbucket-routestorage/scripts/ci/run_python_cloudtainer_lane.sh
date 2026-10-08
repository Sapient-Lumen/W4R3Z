#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="src"
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

cleanup_transients() {
  # Cache directories may be created or removed while the lane is running.
  # Treat transient cleanup as best-effort hygiene rather than a failing proof step.
  find . -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} + 2>/dev/null || true
}

run_pytest_batched() {
  # The cube has many small regression files. In this cloudtainer a single
  # monolithic pytest process or a large batch can be killed by resource limits,
  # so the CI lane verifies the same active test surface in deterministic single-file
  # batches.
  mapfile -t test_files < <(find tests -maxdepth 1 -name 'test_*.py' | sort)
  local chunk_size=12
  local total=${#test_files[@]}
  local start=0
  while (( start < total )); do
    python3 -m pytest -q "${test_files[@]:start:chunk_size}"
    start=$(( start + chunk_size ))
  done
}

cleanup_transients
python3 scripts/evidence/check_surfaces.py
python3 scripts/evidence/run_micro_simulation.py
run_pytest_batched
python3 scripts/evidence/run_compile_check.py
cleanup_transients
python3 scripts/evidence/run_cube_audit.py
cleanup_transients
echo "python cloudtainer lane pass"
