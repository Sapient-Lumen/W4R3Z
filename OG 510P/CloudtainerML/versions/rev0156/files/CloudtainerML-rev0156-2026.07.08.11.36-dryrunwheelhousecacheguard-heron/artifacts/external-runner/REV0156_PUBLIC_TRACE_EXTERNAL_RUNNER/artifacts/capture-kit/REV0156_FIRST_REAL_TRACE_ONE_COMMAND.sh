#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
REVUP="REV0156"

PUBLIC_TRACE_COMMON_ENV_MODE="base"
source "$HERE/${REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"

LAST_PHASE="start"
finish_status() {
  rc=$?
  python3 tools/public_trace_first_real_trace_audit.py --mode status --runner-exit-code "$rc" --last-phase "$LAST_PHASE" >/dev/null 2>&1 || true
  exit "$rc"
}
trap finish_status EXIT

run_gate() {
  LAST_PHASE="$1"
  shift
  "$@"
}

run_gate runtime_requirement_lock python3 tools/public_trace_runtime_requirement_lock_audit.py
run_gate common_env_contract python3 tools/public_trace_common_env_contract_audit.py
run_gate first_trace_surface python3 tools/public_trace_first_real_trace_audit.py --mode surface
run_gate run_manifest_coherence python3 tools/public_trace_run_manifest_coherence_audit.py
run_gate bootstrap_runtime_audit python3 tools/public_trace_bootstrap_runtime_audit.py
run_gate cache_root_contract python3 tools/public_trace_cache_root_contract_audit.py
run_gate cache_duplication_guard python3 tools/public_trace_cache_duplication_guard_audit.py
run_gate snapshot_digest_receipt_cache python3 tools/snapshot_digest_receipt_cache_audit.py
run_gate snapshot_download_plan_gate python3 tools/public_trace_snapshot_download_plan_gate_audit.py
run_gate offline_quarantine python3 tools/public_trace_offline_quarantine_audit.py
run_gate live_script_dependency python3 tools/current_live_script_dependency_audit.py

if [[ "${BOOTSTRAP_RUNTIME:-0}" == "1" ]]; then
  LAST_PHASE="bootstrap_runtime"
  bash "$HERE/${REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh"
  if [[ "${PUBLIC_TRACE_BOOTSTRAP_DRY_RUN:-0}" == "1" ]]; then
    LAST_PHASE="bootstrap_runtime_dry_run"
    echo "bootstrap dry run completed; no venv activation, snapshot download, or capture attempted." >&2
    python3 tools/public_trace_first_real_trace_audit.py --mode status --runner-exit-code 0 --last-phase "$LAST_PHASE"
    exit 0
  fi
  BOOTSTRAP_ENV="artifacts/runtime/CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh"
  if [[ -f "$BOOTSTRAP_ENV" ]]; then
    # Persist the venv PATH in this parent runner; child bootstrap activation alone would be lost.
    # shellcheck disable=SC1090
    source "$BOOTSTRAP_ENV"
  elif [[ -x "${PUBLIC_TRACE_VENV_DIR:-.venv-public-trace}/bin/python" ]]; then
    export PATH="$ROOT/${PUBLIC_TRACE_VENV_DIR:-.venv-public-trace}/bin:$PATH"
    export PYTHONNOUSERSITE="1"
  else
    echo "ERROR: bootstrap completed without a usable project-local venv or $BOOTSTRAP_ENV" >&2
    exit 2
  fi
  python3 tools/public_trace_bootstrap_runtime_audit.py
fi

# One-command first trace must not spend network/disk on a 2.2GB snapshot if
# the Python runtime that will run capture cannot import the required stack.
RUNTIME_SMOKE_ARGS=(--strict)
if [[ -n "${PUBLIC_TRACE_VENV_DIR:-}" ]]; then
  RUNTIME_SMOKE_ARGS+=(--require-project-venv)
fi
LAST_PHASE="runtime_import_smoke"
python3 tools/public_trace_runtime_import_smoke.py "${RUNTIME_SMOKE_ARGS[@]}"

# Snapshot materialization is the only phase where network is allowed. The
# capture phase below forcibly closes downloads and binds to the preflight-
# selected digest-verified local snapshot.
PREPARE_MODE="${PREPARE_SNAPSHOT:-auto}"
if [[ "$PREPARE_MODE" != "0" && "$PREPARE_MODE" != "false" && "$PREPARE_MODE" != "skip" ]]; then
  if [[ -n "${LOCAL_SNAPSHOT_DIR:-}" && -d "${LOCAL_SNAPSHOT_DIR:-}" ]]; then
    echo "Using supplied LOCAL_SNAPSHOT_DIR=$LOCAL_SNAPSHOT_DIR; snapshot preparation download is skipped." >&2
  else
    if [[ "${ALLOW_DOWNLOAD:-0}" != "1" ]]; then
      echo "ERROR: first real trace needs either LOCAL_SNAPSHOT_DIR=/path/to/digest-verified snapshot or ALLOW_DOWNLOAD=1 for the snapshot-preparation phase." >&2
      echo "       Example: BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh" >&2
      exit 2
    fi
    LAST_PHASE="prepare_snapshot"
    ALLOW_DOWNLOAD=1 HASH_WEIGHTS="${HASH_WEIGHTS:-1}" bash "$HERE/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh"
  fi
fi

LAST_PHASE="capture_local_only"
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 HF_HUB_DISABLE_UPDATE_CHECK=1 \
  ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 HASH_WEIGHTS="${HASH_WEIGHTS:-1}" bash "$HERE/RUN_CURRENT_PUBLIC_TRACE.sh" "$@"
LAST_PHASE="final_status"
python3 tools/public_trace_first_real_trace_audit.py --mode status --runner-exit-code 0 --last-phase "$LAST_PHASE"
