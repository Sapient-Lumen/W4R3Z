#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
REVUP="REV0156"

PUBLIC_TRACE_COMMON_ENV_MODE="capture"
source "$HERE/${REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"

python3 tools/public_trace_runtime_requirement_lock_audit.py
python3 tools/public_trace_common_env_contract_audit.py
python3 tools/public_trace_cache_root_contract_audit.py
python3 tools/public_trace_cache_duplication_guard_audit.py

# Cheap front gate first: stop known dependency/snapshot blockers before the
# broader readiness gate spawns many Python probes. It subsumes the active
# shell dependency-closure check for blocked capsules; the full chain still
# reruns current_live_script_dependency_audit.py after it passes.
python3 tools/public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only
CAPTURE_ENV="artifacts/runtime/CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh"
if [[ -f "$CAPTURE_ENV" ]]; then
  # Bind capture to the exact digest-verified local snapshot selected by preflight.
  # This prevents proving one cache candidate while loading another via model-id resolution.
  source "$CAPTURE_ENV"
else
  echo "ERROR: capture-start preflight did not write $CAPTURE_ENV" >&2
  exit 2
fi
python3 tools/public_trace_selected_snapshot_contract_audit.py
python3 tools/public_trace_loader_snapshot_binding_audit.py
python3 tools/public_trace_acceptance_loader_binding_audit.py
python3 tools/public_trace_downstream_identity_receipt_audit.py
python3 tools/public_trace_selector_receipt_chain_binding_audit.py
python3 tools/public_trace_selector_receipt_replay_enforcement_harness.py
python3 tools/public_trace_fast_prereq_gate.py --phase capture --local-only --strict --require-weight-hash --capture-local-only

# Minimal static guards first. The broad metadata/surface audits are run by the
# readiness gate or after prerequisites pass; blocked capsules should not spend
# time in handoff/archive probes before runtime and snapshot readiness are known.
python3 tools/readiness_failfast_contract_audit.py
python3 tools/public_trace_digest_acceptance_audit.py
python3 tools/public_trace_hash_preflight_contract_audit.py
python3 tools/snapshot_digest_receipt_cache_audit.py
python3 tools/public_trace_capture_local_only_contract_audit.py
python3 tools/public_trace_offline_quarantine_audit.py
python3 tools/public_trace_selected_snapshot_contract_audit.py
python3 tools/public_trace_loader_snapshot_binding_audit.py
python3 tools/public_trace_capture_decision_refactor_audit.py
python3 tools/public_trace_live_prompt_manifest_audit.py
python3 tools/public_trace_env_snapshot_integrity_audit.py
python3 tools/public_trace_snapshot_local_only_gate_audit.py
python3 tools/current_live_script_dependency_audit.py

python3 tools/public_trace_readiness_gate.py --local-only --strict

# Only after readiness passes do the broader execution-surface and handoff-builder
# audits matter for an actual capture attempt.
python3 tools/revision_metadata_coherence_audit.py
python3 tools/public_trace_run_manifest_coherence_audit.py
python3 tools/public_trace_bootstrap_runtime_audit.py
python3 tools/current_entrypoint_consistency_audit.py
python3 tools/capture_surface_refactor_audit.py
python3 tools/active_surface_trim_audit.py
python3 tools/public_trace_handoff_builder_audit.py
python3 tools/public_trace_capture_preflight_handoff_audit.py

# Handoff to the one-shot capture: this wrapper has already run the import-light
# capture-start preflight, selected-snapshot binding, fail-fast prerequisite
# gates, and static handoff audits. The one-shot remains directly runnable, but
# when reached through the stable wrapper it should not repeat the same gates.
export PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE=1
export PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT="capture_start_preflight_done_selected_snapshot_v1"
export PUBLIC_TRACE_CAPTURE_PREFLIGHT_ENV="$CAPTURE_ENV"
export PUBLIC_TRACE_CAPTURE_PREFLIGHT_SOURCE="${REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"

exec bash "$HERE/${REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh" "$@"
