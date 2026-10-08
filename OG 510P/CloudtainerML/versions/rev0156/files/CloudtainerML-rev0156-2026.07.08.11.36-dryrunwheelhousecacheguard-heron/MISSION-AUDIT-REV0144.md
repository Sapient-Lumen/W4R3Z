# Mission audit — REV0144

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current first-trace alias: `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Current capture alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Primary artifact: `artifacts/audit/REV0144_PUBLIC_TRACE_CAPTURE_PREFLIGHT_HANDOFF_AUDIT.md`  
External runner: `artifacts/external-runner/REV0144_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`

## Heart of the mission

CloudtainerML is still a claim compiler. The useful unit is not a persuasive note; it is a replayable claim with digest-bound source/model bytes, prompt/token/generation provenance, evaluator and selector receipts, a portable handoff archive, and named-hardware timing.

## Riskiest unfinished work

The riskiest unfinished work remains the first real TinyLlama trace. REV0144 targets a live-run waste/failure mode rather than expanding doctrine: after the stable wrapper has passed capture-start preflight, selected-snapshot binding, strict prereq gates, readiness, and static handoff audits, the revisioned one-shot no longer repeats the same front-gate block. The direct one-shot path still keeps the full fallback checks for forensic replay.

## Online-grounded pressure

This turn rechecked current Hugging Face docs for the path that matters. `huggingface_hub` environment variables are read at import time, so evidence capture must set offline/quarantine variables before importing Hub/Transformers runtime. Transformers offline use still requires downloaded/cached local files, and Hugging Face Hub/Xet docs continue to point toward `hf_xet`/Xet-aware large-file transfer paths for modern large snapshots. This reinforces the split already in the cube: allow network only in snapshot preparation, then capture from the selected digest-verified local snapshot.

## What went wrong or wasteful

The live path had become safer but still repetitive. The stable wrapper and one-shot both ran much of the same import-light preflight stack. On a capable machine this would waste time and, worse, blur the first real post-preflight blocker by rerunning checks already known to be complete. REV0144 narrows the active path without deleting the forensic fallback.

## What changed in REV0144

- Added `tools/public_trace_capture_preflight_handoff_audit.py`.
- Updated `REV0144_RUN_TINYLLAMA_PUBLIC_TRACE.sh` to export `PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE=1`, `PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT=capture_start_preflight_done_selected_snapshot_v1`, and the selected capture env after wrapper front gates pass.
- Updated `REV0144_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` to consume that handoff and skip duplicated preflight gates, while preserving direct full-preflight fallback when called alone.
- Wired the new handoff contract into live-script dependency audit, smoke validation, run-manifest coherence, top docs, run packet/source lock, and the compact external runner.
- Kept capture offline/local-only and non-promotional.

## Safety boundary

This is not evidence that TinyLlama was loaded here. This cloudtainer still lacks a complete digest-verified TinyLlama snapshot and an importable Transformers runtime. REV0144 only makes the next successful external trace path less wasteful and easier to diagnose.

## Decision

Run the first-real-trace command on a capable machine and repair the first concrete blocker it returns. Do not add a new registry layer before a real trace attempt.
