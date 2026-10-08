#!/usr/bin/env bash
# Common public-trace env contract for REV0156. Source this before any Python process
# that may import huggingface_hub or transformers. Hugging Face Hub reads cache/offline
# environment variables at import time, so duplicated late exports are a real blocker.

PUBLIC_TRACE_COMMON_ENV_MODE="${PUBLIC_TRACE_COMMON_ENV_MODE:-base}"

PUBLIC_TRACE_CACHE_ROOT="${PUBLIC_TRACE_CACHE_ROOT:-artifacts/runtime/public-trace-hf-cache}"
case "$PUBLIC_TRACE_CACHE_ROOT" in
  /*) PUBLIC_TRACE_CACHE_ROOT_ABS="$PUBLIC_TRACE_CACHE_ROOT" ;;
  *) PUBLIC_TRACE_CACHE_ROOT_ABS="$ROOT/$PUBLIC_TRACE_CACHE_ROOT" ;;
esac
export PUBLIC_TRACE_CACHE_ROOT="$PUBLIC_TRACE_CACHE_ROOT_ABS"
export HF_HOME="${HF_HOME:-$PUBLIC_TRACE_CACHE_ROOT/hf-home}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$PUBLIC_TRACE_CACHE_ROOT/hub}"
export HF_XET_CACHE="${HF_XET_CACHE:-$PUBLIC_TRACE_CACHE_ROOT/xet}"
export HF_ASSETS_CACHE="${HF_ASSETS_CACHE:-$PUBLIC_TRACE_CACHE_ROOT/assets}"
mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$HF_XET_CACHE" "$HF_ASSETS_CACHE"

# Guard a costly Hub cache footgun. Hugging Face documents that disabling Hub
# symlinks can duplicate huge files in snapshot directories. A TinyLlama trace
# snapshot is large enough that this must be a deliberate operator override.
case "${HF_HUB_DISABLE_SYMLINKS:-0}" in
  1|ON|On|on|YES|Yes|yes|TRUE|True|true)
    if [[ "${PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION:-0}" != "1" ]]; then
      echo "ERROR: HF_HUB_DISABLE_SYMLINKS=${HF_HUB_DISABLE_SYMLINKS} can duplicate large Hub files; set PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION=1 only if this is intentional." >&2
      exit 2
    fi
    ;;
esac

export MODEL_ID="${MODEL_ID:-TinyLlama/TinyLlama-1.1B-Chat-v1.0}"
export MODEL_REVISION="${MODEL_REVISION:-fe8a4ea1ffedaf415f4da2f062534de366a451e6}"
export TOKENIZER_REVISION="${TOKENIZER_REVISION:-$MODEL_REVISION}"
export WEIGHTS_SOURCE="${WEIGHTS_SOURCE:-https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/$MODEL_REVISION}"
export LICENSE="${LICENSE:-apache-2.0}"
export HASH_WEIGHTS="${HASH_WEIGHTS:-1}"
export REQUIRE_WEIGHT_HASH="${REQUIRE_WEIGHT_HASH:-1}"
export HF_HUB_DOWNLOAD_TIMEOUT="${HF_HUB_DOWNLOAD_TIMEOUT:-300}"
export HF_HUB_ETAG_TIMEOUT="${HF_HUB_ETAG_TIMEOUT:-60}"

export PROMPT_MANIFEST="${PROMPT_MANIFEST:-artifacts/prompts/${REVUP}_PUBLIC_TRACE_PROMPTS.txt}"
export PROMPT_SET_ID="${PROMPT_SET_ID:-rev0156_public_trace_prompt_set}"
export DECODE_STEPS="${DECODE_STEPS:-2}"
export MAX_ROWS="${MAX_ROWS:-128}"
export ATTENTION_IMPLEMENTATION="${ATTENTION_IMPLEMENTATION:-eager}"
export CACHE_IMPLEMENTATION="${CACHE_IMPLEMENTATION:-dynamic}"
export TRACE_TORCH_DTYPE="${TRACE_TORCH_DTYPE:-float32}"
export TRACE_DEVICE="${TRACE_DEVICE:-auto}"
export TRACE_GATE_STEP_TIMEOUT="${TRACE_GATE_STEP_TIMEOUT:-8}"
export CAPTURE_LOCAL_ONLY="${CAPTURE_LOCAL_ONLY:-1}"

if [[ "$PUBLIC_TRACE_COMMON_ENV_MODE" == "capture" ]]; then
  if [[ "${ALLOW_DOWNLOAD:-0}" == "1" ]]; then
    echo "NOTICE: ALLOW_DOWNLOAD=1 is ignored for evidence capture; run PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh for downloads, then capture local-only." >&2
  fi
  export ALLOW_DOWNLOAD=0
  export HF_HUB_OFFLINE=1
  export TRANSFORMERS_OFFLINE=1
  export HF_HUB_DISABLE_TELEMETRY=1
  export HF_HUB_DISABLE_IMPLICIT_TOKEN=1
  export HF_HUB_DISABLE_UPDATE_CHECK=1
  export PUBLIC_TRACE_CAPTURE_OFFLINE_QUARANTINE=hf_transformers_offline_env_before_runtime_import_v1
elif [[ "$PUBLIC_TRACE_COMMON_ENV_MODE" == "snapshot" ]]; then
  # Snapshot preparation is the only mode where ALLOW_DOWNLOAD may be 1.
  export HF_HUB_DISABLE_TELEMETRY="${HF_HUB_DISABLE_TELEMETRY:-1}"
else
  export HF_HUB_DISABLE_TELEMETRY="${HF_HUB_DISABLE_TELEMETRY:-1}"
fi
