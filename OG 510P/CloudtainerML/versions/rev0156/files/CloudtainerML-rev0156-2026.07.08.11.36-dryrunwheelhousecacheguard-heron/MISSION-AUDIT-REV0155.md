# Mission audit — REV0155

Status: `pass_with_blockers`  
Promotion allowed: `false`

## Heart of the mission

CloudtainerML is a claim compiler. The live deliverable is still one digest-bound TinyLlama public-trace packet that can be captured locally, evaluated, selector-entered, replayed, handed off, and timed on named hardware. This revision stays away from doctrine and fixes the path that would stop an operator before the trace can even start.

## Highest-risk finding

REV0154's first-real-trace static gates passed, but the bootstrap branch was broken: `REQ="...txt"REQ="...txt"` made the requirements path resolve to a non-existent concatenated string, so `BOOTSTRAP_RUNTIME=1` failed before it could install `transformers`. The snapshot preparation wrapper also contained `HASH_ARG=()HASH_ARG=()`, which is a Bash syntax error hidden behind the earlier runtime-smoke blocker.

## Substance changes

1. Fixed the bootstrap requirements assignment so `artifacts/runtime/REV0155_public_trace_requirements.txt` resolves as the actual install lock.
2. Added `PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1` to verify bootstrap path/venv resolution without invoking pip or network.
3. Fixed the snapshot-prepare `HASH_ARG` Bash syntax error and the duplicate `LAST_PHASE` noise in the first-trace wrapper.
4. Refactored the live dependency audit and smoke validator to run `bash -n` over every active capture wrapper and to reject adjacent assignment concatenation hazards that Bash syntax alone can miss.
5. Deduplicated first-blocker/status receipt blockers so the next operator sees one actionable cause instead of repeated noise.

## Online research basis

Hugging Face Hub docs define `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, and timeout controls, which supports keeping the project-local cache contract in the sourced common env. Hub download docs support full commit revisions, `snapshot_download`, filtering, local dirs, and dry-run planning. Transformers docs show `from_pretrained(..., local_files_only=...)` and `attn_implementation="eager"`, reinforcing the prepare-then-local-only-capture split. The TinyLlama model tree still shows a 2.2 GB Xet-backed safetensors model at the pinned public target, so avoiding wasted repeated bootstrap/syntax failures before snapshot work is material.

## Still blocked here

This chat container still lacks `transformers` in the runtime used by the current shell and does not contain the full digest-verified TinyLlama snapshot. The next material action on a capable host is:

```bash
PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/REV0155_BOOTSTRAP_PUBLIC_TRACE_ENV.sh
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```
