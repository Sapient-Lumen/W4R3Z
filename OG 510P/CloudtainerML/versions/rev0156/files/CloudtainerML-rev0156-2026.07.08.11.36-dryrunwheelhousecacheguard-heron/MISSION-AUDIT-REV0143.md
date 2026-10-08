# Mission audit — REV0143

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current first-trace alias: `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Current capture alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Primary artifact: `artifacts/audit/REV0143_PUBLIC_TRACE_OFFLINE_QUARANTINE_AUDIT.md`  
External runner: `artifacts/external-runner/REV0143_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`

## Heart of the mission

CloudtainerML is still a claim compiler, not a repository of aspirations. The useful unit is a claim that survives hostile replay: digest-bound source and model bytes, exact prompt/token/generation provenance, evaluator and selector receipts, a portable handoff archive, and named-hardware timing. The immediate mission remains unchanged: produce one real public TinyLlama trace that can be replayed and used to promote, kill, or pivot selector claims.

## Riskiest unfinished work

The riskiest unfinished work is not another doctrine pass. It is the first real trace. REV0142 made the first trace less wasteful by caching the full `model.safetensors` digest after the first verified hash. REV0143 hardens the next boundary: after the allowed snapshot-preparation phase, evidence capture must not silently call the Hub, use an implicit token, or resolve a different remote/cache object.

## Online-grounded pressure

The Hugging Face Hub documentation says environment variables are read at import time and that `HF_HUB_OFFLINE=1` prevents HTTP calls and skips the usual cache freshness request. Transformers documentation says offline use requires downloaded/cached files ahead of time and can load a local directory with `local_files_only=True`. The Transformers model API also accepts a local directory as `pretrained_model_name_or_path` and exposes `local_files_only`. Source basis: https://huggingface.co/docs/huggingface_hub/main/en/package_reference/environment_variables, https://huggingface.co/docs/transformers/en/installation, https://huggingface.co/docs/transformers/en/main_classes/model.

The implication for this cube is direct: the system should allow network only while materializing the reviewed snapshot, then set offline controls before importing `transformers`/`huggingface_hub` for capture. Otherwise a “local-only” public trace is only partly local-only; it may still depend on import-time env state, implicit Hub token behavior, or a cache freshness call outside the receipt boundary.

## What went wrong or wasteful

The active capture helper already passed `local_files_only=True`, and wrappers forced `ALLOW_DOWNLOAD=0`. That was necessary but not sufficient. It did not explicitly set `HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`, telemetry/update-check disablement, or implicit-token disablement before runtime import. This was a high-risk omission because the first successful real trace should be auditable as a local digest-selected capture, not as a run whose behavior might vary with ambient Hub state.

A second waste pattern remains visible: the run wrapper and one-shot wrapper still duplicate several audits. REV0143 does not collapse that yet because direct one-shot execution must remain self-contained. The next safe refactor is to add a preflight-done handoff flag so the stable wrapper can skip duplicated checks while preserving the direct one-shot path.

## What changed in REV0143

- Added `tools/public_trace_offline_quarantine_audit.py`.
- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` to set `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `HF_HUB_DISABLE_IMPLICIT_TOKEN=1`, and `HF_HUB_DISABLE_UPDATE_CHECK=1` before importing Hugging Face runtime when capture is local-only.
- Added a public-claim fail-closed guard if Hugging Face runtime was already imported before quarantine.
- Added quarantine provenance fields to the NPZ and provenance JSON surface.
- Added the same quarantine exports to the current capture wrappers and to the capture-start preflight env file.
- Kept snapshot preparation as the only allowed download phase.
- Moved current capture wrappers, run packet, source lock, prompt manifest, runtime requirements, and external runner to REV0143.
- Rebuilt the compact external runner so a capable machine uses the hardened path.

## Safety boundary

This is not evidence that TinyLlama was loaded here. This cloudtainer still lacks a complete digest-verified TinyLlama snapshot and an importable Transformers runtime. REV0143 only makes the next successful external trace less ambiguous and less wasteful.

## Decision

Run the same first-real-trace command on a capable machine:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

After snapshot preparation, capture is forced local-only and offline-quarantined. If it fails, repair the first concrete blocker returned by the runner before adding new registries or claim families.
