# Mission audit — REV0154

Status: `pass_with_blockers`  
Promotion allowed: `false`

## Heart of the mission

CloudtainerML is now a claim compiler: the useful product is not a larger registry, but one digest-bound, replayable TinyLlama public-trace packet that can be accepted, evaluated, selector-entered, replayed, handed off, and timed on named hardware. This revision keeps the mission trace-first and converts a false-green blocker into executable checks.

## What was risky / at risk of not completing

The actual first-trace command in REV0153 stopped before runtime bootstrap or snapshot work because the current run packet and source lock still carried stale revision integers. Worse, full package smoke did not catch that because the run-manifest coherence audit was callable but not mandatory in the smoke validator. REV0154 repairs the payload and makes smoke validate the run packet/source lock identity directly.

## What changed

1. Fixed the current TinyLlama run packet and source lock identity fields: `revision`, `revision_number`, `revision_int`, `current_revision`, `current_revision_int`, package name, archive name, runtime lock path, prompt path, and external-runner path now point at REV0154.
2. Made `tools/smoke_validate.py` reject stale current run-packet/source-lock identity even if the dedicated audit was not run first.
3. Added `REV0154_COMMON_PUBLIC_TRACE_ENV.sh` and refactored the first-real-trace, prepare, capture, one-shot, and bootstrap wrappers to source a single cache/model/offline-env contract instead of carrying divergent copies.
4. Added `tools/public_trace_common_env_contract_audit.py` and taught the live-script/external-runner closure audits to follow sourced shell files, not just `bash`/`exec` calls.
5. Tightened the first-real-trace status path so failures in run-manifest coherence and other early static gates show a receipt-backed blocker instead of falling back to `runner_exit_code_1` at `start`.

## Online research basis

Hugging Face Hub environment variables are read at import time, which means cache roots and offline controls must be bound before any Python code imports `huggingface_hub`. The current Hub docs define `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, and `HF_ASSETS_CACHE`, which justifies consolidating those exports in the sourced common env script.

Transformers documentation says offline/firewalled use requires files to be downloaded and cached ahead of time, then loading can use local files only. Hugging Face Hub download docs also support dry-run planning for `snapshot_download`, reinforcing the separate prepare/download phase before local-only evidence capture.

TinyLlama remains an appropriate target for the first public trace because the model card describes the 1.1B Llama-family model and public Transformers usage, while the TinyLlama paper describes the compact 1.1B architecture/training project. That supports the trace surface, but not any performance promotion claim.

## Still blocked

This cloudtainer still has no `transformers` import and no complete digest-verified TinyLlama snapshot, so REV0154 remains non-promotional. The next material action is to run:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

and fix the first receipt-backed blocker, not add registry prose.
