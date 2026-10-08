#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"
export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"

# Prevent host-injected numerical runtimes from creating one native thread per
# visible CPU in the supervisor or each worker interpreter. Explicit caller
# choices remain authoritative.
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"
export BLIS_NUM_THREADS="${BLIS_NUM_THREADS:-1}"

# Route the ordinary test entrypoint through the existing process-group-aware
# runner.  An outer timeout or interrupt then terminates the active pytest tree
# instead of leaving parentless workers in the cloudtainer.
python tools/mxtest.py \
  --chunk-timeout "${MXTEST_CHUNK_TIMEOUT_SECONDS:-1800}" \
  -- "$@"
