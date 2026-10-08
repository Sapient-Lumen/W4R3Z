#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
REVUP="REV0156"

PUBLIC_TRACE_COMMON_ENV_MODE="capture"
source "$HERE/${REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"

if [[ "$ATTENTION_IMPLEMENTATION" != "eager" ]]; then
  echo "ERROR: ATTENTION_IMPLEMENTATION must be eager for public trace semantics; got $ATTENTION_IMPLEMENTATION" >&2
  exit 2
fi
if [[ "$CACHE_IMPLEMENTATION" != "dynamic" ]]; then
  echo "ERROR: CACHE_IMPLEMENTATION must be dynamic for public trace semantics; got $CACHE_IMPLEMENTATION" >&2
  exit 2
fi
if [[ ! -f "$PROMPT_MANIFEST" ]]; then
  echo "PROMPT_MANIFEST does not exist or is not a file: $PROMPT_MANIFEST" >&2
  exit 2
fi
python3 - <<'PY'
import os
try:
    steps=int(os.environ.get('DECODE_STEPS','0'))
    rows=int(os.environ.get('MAX_ROWS','0'))
except ValueError:
    raise SystemExit('DECODE_STEPS and MAX_ROWS must be integers')
if steps <= 0:
    raise SystemExit('DECODE_STEPS must be positive')
if rows <= 0:
    raise SystemExit('MAX_ROWS must be positive')
PY

OUT_DIR="${OUT_DIR:-artifacts/trace-bundles}"
mkdir -p "$OUT_DIR" artifacts/audit artifacts/probe-results
OUT_NPZ="${OUT_NPZ:-$OUT_DIR/${REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz}"
OUT_PROV="${OUT_PROV:-$OUT_DIR/${REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json}"
OUT_GATE="${OUT_GATE:-artifacts/probe-results/${REVUP}_PUBLIC_TRACE_GATE_REAL_MODEL.json}"
OUT_RECEIPT="${OUT_RECEIPT:-artifacts/probe-results/${REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT.json}"
OUT_SELECTOR="${OUT_SELECTOR:-artifacts/probe-results/${REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json}"
OUT_HANDOFF_DIR="${OUT_HANDOFF_DIR:-$OUT_DIR/${REVUP}_PUBLIC_TRACE_HANDOFF}"
OUT_HANDOFF_ZIP="${OUT_HANDOFF_ZIP:-$OUT_DIR/${REVUP}_PUBLIC_TRACE_HANDOFF.zip}"

if [[ "${PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE:-0}" == "1" ]]; then
  if [[ "${PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT:-}" != "capture_start_preflight_done_selected_snapshot_v1" ]]; then
    echo "ERROR: PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE was set without the expected contract" >&2
    exit 2
  fi
  CAPTURE_ENV="${PUBLIC_TRACE_CAPTURE_PREFLIGHT_ENV:-artifacts/runtime/CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh}"
  if [[ -f "$CAPTURE_ENV" ]]; then
    # Re-source to make this script robust across exec boundaries and external runners.
    source "$CAPTURE_ENV"
  else
    echo "ERROR: preflight handoff flag was set but capture env is missing: $CAPTURE_ENV" >&2
    exit 2
  fi
  python3 tools/public_trace_capture_preflight_handoff_audit.py
else
  # Direct one-shot execution path. Keep the full preflight stack here so the
  # revisioned one-shot can be run independently for forensic replay or manual
  # debugging. The stable wrapper sets PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE=1 to
  # avoid repeating this block.
  python3 tools/revision_metadata_coherence_audit.py
  python3 tools/public_trace_run_manifest_coherence_audit.py
  python3 tools/public_trace_bootstrap_runtime_audit.py
  python3 tools/current_entrypoint_consistency_audit.py
  python3 tools/current_live_script_dependency_audit.py
  python3 tools/capture_surface_refactor_audit.py
  python3 tools/active_surface_trim_audit.py
  python3 tools/public_trace_capture_decision_refactor_audit.py
  python3 tools/public_trace_live_prompt_manifest_audit.py
  python3 tools/public_trace_env_snapshot_integrity_audit.py
  python3 tools/public_trace_hash_preflight_contract_audit.py
  python3 tools/snapshot_digest_receipt_cache_audit.py
  python3 tools/public_trace_capture_local_only_contract_audit.py
  python3 tools/public_trace_offline_quarantine_audit.py
  python3 tools/public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only
  CAPTURE_ENV="artifacts/runtime/CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh"
  if [[ -f "$CAPTURE_ENV" ]]; then
    # Bind capture to the exact digest-verified local snapshot selected by preflight.
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
  python3 tools/public_trace_handoff_builder_audit.py
fi

python3 tools/public_trace_runtime_requirement_lock_audit.py
python3 tools/public_trace_common_env_contract_audit.py
python3 tools/public_trace_dependency_lock_audit.py
python3 tools/public_trace_cache_root_contract_audit.py
python3 tools/public_trace_cache_duplication_guard_audit.py
python3 tools/source_lock_audit.py
python3 tools/trace_run_packet_audit.py
python3 tools/public_trace_env_preflight.py --strict trace --require-weight-hash --capture-local-only
python3 tools/transformers_llama_surface_probe.py
python3 tools/public_trace_backend_identity_probe.py
python3 tools/public_trace_cache_implementation_audit.py
python3 tools/public_trace_prompt_manifest_audit.py
python3 tools/public_trace_device_dtype_timing_audit.py
python3 tools/public_trace_hardware_timing_boundary_audit.py
python3 tools/public_trace_acceptance_bundle_audit.py

if [[ -z "${LOCAL_SNAPSHOT_DIR:-}" ]]; then
  echo "ERROR: selected digest-verified LOCAL_SNAPSHOT_DIR was not exported by preflight" >&2
  exit 2
fi
if [[ ! -d "$LOCAL_SNAPSHOT_DIR" ]]; then
  echo "LOCAL_SNAPSHOT_DIR does not exist or is not a directory: $LOCAL_SNAPSHOT_DIR" >&2
  exit 2
fi
CAPTURE_MODEL="${CAPTURE_MODEL:-$LOCAL_SNAPSHOT_DIR}"
if [[ "$CAPTURE_MODEL" != "$LOCAL_SNAPSHOT_DIR" ]]; then
  echo "ERROR: CAPTURE_MODEL must equal selected LOCAL_SNAPSHOT_DIR for public evidence capture" >&2
  exit 2
fi
# Evidence capture must be local-files-only and must load the exact digest-verified
# LOCAL_SNAPSHOT_DIR selected by the capture-start preflight. Use PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
# with ALLOW_DOWNLOAD=1 before this wrapper if the reviewed snapshot is not
# already cached; the capture itself must not depend on network state.

python3 experiments/public_trace_capture/hf_attention_trace_capture.py \
  --model "$CAPTURE_MODEL" \
  --public-model-id "$MODEL_ID" \
  --model-revision "$MODEL_REVISION" \
  --tokenizer-revision "$TOKENIZER_REVISION" \
  --attention-implementation "$ATTENTION_IMPLEMENTATION" \
  --cache-implementation "$CACHE_IMPLEMENTATION" \
  --torch-dtype "$TRACE_TORCH_DTYPE" \
  --device "$TRACE_DEVICE" \
  --prompts-file "$PROMPT_MANIFEST" \
  --position-policy last_and_mid \
  --decode-steps "$DECODE_STEPS" \
  --max-rows "$MAX_ROWS" \
  --public-pretrained-trace \
  --require-model-safetensors-sha256 \
  --require-loader-snapshot-bind \
  --provenance-reviewed \
  --weights-source "$WEIGHTS_SOURCE" \
  --license "$LICENSE" \
  --out "$OUT_NPZ" \
  --provenance-out "$OUT_PROV"

python3 experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py \
  --trace-npz "$OUT_NPZ" \
  --public-pretrained-trace \
  --provenance-json "$OUT_PROV" \
  --trace-source-label public_llama_post_transform_prefill_cached_decode_active_key_kv_group_rope_probability_prompt_generation_token_determinism_dynamic_cache_backend_identity_runtime_snapshot_intake_handoff_builder \
  --bundle-model-id "$MODEL_ID" \
  --bundle-license "$LICENSE" \
  --out "$OUT_GATE"

python3 tools/public_trace_surrogate_rejection_audit.py --trace-npz "$OUT_NPZ" --provenance-json "$OUT_PROV"
python3 tools/public_trace_evaluation_verdict_audit.py --strict-require-trace --trace-npz "$OUT_NPZ" --provenance-json "$OUT_PROV" --receipt-json "$OUT_RECEIPT"
python3 tools/public_trace_selector_entry_gate.py --strict --trace-npz "$OUT_NPZ" --provenance-json "$OUT_PROV" --receipt-json "$OUT_RECEIPT" --selector-entry-receipt-json "$OUT_SELECTOR"
python3 tools/public_trace_selector_receipt_replay_gate.py --strict --trace-npz "$OUT_NPZ" --provenance-json "$OUT_PROV" --selector-entry-receipt-json "$OUT_SELECTOR"
python3 tools/public_trace_handoff_builder.py \
  --trace-npz "$OUT_NPZ" \
  --provenance-json "$OUT_PROV" \
  --evaluation-receipt-json "$OUT_RECEIPT" \
  --selector-entry-receipt-json "$OUT_SELECTOR" \
  --out-dir "$OUT_HANDOFF_DIR" \
  --out-zip "$OUT_HANDOFF_ZIP" \
  --clean \
  --verify-strict
python3 tools/public_trace_handoff_archive_gate.py --handoff-dir "$OUT_HANDOFF_DIR" --manifest "$OUT_HANDOFF_DIR/PUBLIC_TRACE_HANDOFF_MANIFEST.json" --strict
python3 tools/public_trace_current_trace_lane_audit.py
python3 tools/smoke_validate.py

echo "handoff_dir=$OUT_HANDOFF_DIR"
echo "handoff_zip=$OUT_HANDOFF_ZIP"
