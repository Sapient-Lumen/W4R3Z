#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
REVUP="REV0156"

PUBLIC_TRACE_COMMON_ENV_MODE="snapshot"
source "$HERE/${REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"

HASH_ARG=()
INTAKE_HASH_ARG=()
HASH_GATE_ARG=()
if [[ "${HASH_WEIGHTS:-1}" == "1" ]]; then
  HASH_ARG=(--include-hashes)
  INTAKE_HASH_ARG=(--hash-weights)
  HASH_GATE_ARG=(--require-weight-hash)
fi

# Phase A: snapshot/materialization checks only. Missing `transformers` is a
# capture-runtime blocker, not a reason to stop before the immutable model files
# have been downloaded or verified.
if [[ "${ALLOW_DOWNLOAD:-0}" == "1" ]]; then
  python3 tools/public_trace_fast_prereq_gate.py --phase snapshot --download --strict
else
  python3 tools/public_trace_fast_prereq_gate.py --phase snapshot --local-only --strict "${HASH_GATE_ARG[@]}"
fi

python3 tools/public_trace_runtime_requirement_lock_audit.py
python3 tools/public_trace_common_env_contract_audit.py
python3 tools/revision_metadata_coherence_audit.py
python3 tools/public_trace_run_manifest_coherence_audit.py
python3 tools/public_trace_bootstrap_runtime_audit.py
python3 tools/public_trace_cache_root_contract_audit.py
python3 tools/public_trace_cache_duplication_guard_audit.py
python3 tools/snapshot_digest_receipt_cache_audit.py
python3 tools/public_trace_snapshot_download_plan_gate_audit.py
python3 tools/current_live_script_dependency_audit.py
python3 tools/current_entrypoint_consistency_audit.py
python3 tools/public_trace_env_snapshot_integrity_audit.py
python3 tools/public_trace_snapshot_local_only_gate_audit.py
python3 tools/source_lock_audit.py
python3 tools/trace_run_packet_audit.py
python3 tools/snapshot_prepare_phase_order_audit.py
python3 tools/snapshot_integrity_contract_audit.py
python3 tools/tinyllama_snapshot_threshold_audit.py
python3 tools/public_trace_digest_acceptance_audit.py
python3 tools/public_trace_hash_preflight_contract_audit.py
python3 tools/public_trace_acceptance_loader_binding_audit.py
python3 tools/public_trace_capture_local_only_contract_audit.py

if [[ "${ALLOW_DOWNLOAD:-0}" == "1" ]]; then
  export ALLOW_NETWORK_DRY_RUN="${ALLOW_NETWORK_DRY_RUN:-1}"
  if [[ "${PUBLIC_TRACE_SKIP_DOWNLOAD_PLAN:-0}" == "1" ]]; then
    echo "WARNING: PUBLIC_TRACE_SKIP_DOWNLOAD_PLAN=1; writing skipped download-plan receipt before materialization." >&2
    python3 tools/public_trace_snapshot_download_plan.py --skip-network || true
  else
    python3 tools/public_trace_snapshot_download_plan.py --strict
  fi
  python3 tools/hf_snapshot_dry_run_audit.py --require-network --strict
  python3 tools/hf_snapshot_materializer.py --download --strict "${HASH_ARG[@]}"
else
  python3 tools/public_trace_snapshot_download_plan.py --skip-network || true
  python3 tools/hf_snapshot_dry_run_audit.py --skip-network
  python3 tools/hf_snapshot_materializer.py --local-only --strict "${HASH_ARG[@]}"
fi

if [[ -n "${HF_SNAPSHOT_DIR:-}" ]]; then
  python3 tools/public_trace_snapshot_intake_audit.py --snapshot-dir "$HF_SNAPSHOT_DIR" "${INTAKE_HASH_ARG[@]}" || true
elif [[ -n "${LOCAL_SNAPSHOT_DIR:-}" ]]; then
  python3 tools/public_trace_snapshot_intake_audit.py --snapshot-dir "$LOCAL_SNAPSHOT_DIR" "${INTAKE_HASH_ARG[@]}" || true
else
  python3 tools/public_trace_snapshot_intake_audit.py "${INTAKE_HASH_ARG[@]}" || true
fi

# Phase B: collect capture-runtime blockers after the snapshot phase. These are
# intentionally nonfatal for snapshot preparation; RUN_CURRENT_PUBLIC_TRACE.sh is
# the strict capture gate.
python3 tools/public_trace_dependency_lock_audit.py || true
python3 tools/public_trace_env_preflight.py --strict trace --require-weight-hash || true
python3 tools/snapshot_prepare_phase_order_audit.py

echo "snapshot preparation phase completed for ${REVUP}; use artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh for strict capture readiness."
