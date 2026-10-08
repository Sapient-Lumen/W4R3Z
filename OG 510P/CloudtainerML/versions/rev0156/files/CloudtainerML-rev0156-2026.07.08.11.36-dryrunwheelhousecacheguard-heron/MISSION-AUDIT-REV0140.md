# Mission audit — REV0140

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current first-trace alias: `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Current capture alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Primary artifact: `artifacts/external-runner/REV0140_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`

## Heart of the mission

CloudtainerML is a claim compiler. The useful unit is a claim that survives hostile falsification with digest-bound provenance, replayable receipts, and named-hardware timing. The mission is not to maximize registry coverage; it is to force one concrete path from public model snapshot to trace to evaluation/selector/handoff receipts.

## Riskiest unfinished work

The first real digest-bound TinyLlama trace is still the project-critical gap. The cube can explain the blocker, but that is not enough: a capable runner must be able to perform bootstrap, reviewed snapshot materialization, local-only capture, and receipt/status collection without hand-sequencing several wrapper layers.

## What changed in REV0140

- Added `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`, a stable one-command path for the first real trace.
- Added `artifacts/capture-kit/REV0140_FIRST_REAL_TRACE_ONE_COMMAND.sh`, which optionally bootstraps runtime, prepares/hashes the snapshot only when downloads are explicitly allowed, forces local-only capture, and writes a first-trace status audit on success or failure.
- Added `tools/public_trace_first_real_trace_audit.py` with surface and status modes.
- Moved active capture, one-shot capture, snapshot-prepare, bootstrap, prompt, requirements, run-packet, and source-lock files forward to REV0140.
- Refactored the external runner packet so it exposes `RUN_FIRST_REAL_TRACE.sh` instead of only manual phase scripts.
- Extended active dependency and smoke validation to include the first-real-trace runner.

## What is still missing

No real public trace was captured in this cloudtainer. The live blocker remains material: there is no complete digest-verified TinyLlama snapshot and `transformers` is not importable here. Promotion remains forbidden until the runner produces trace/provenance, gate, evaluation receipt, selector-entry receipt, replay, handoff archive, and named-hardware timing receipts.

## Online research pressure applied

External docs and recent reproducibility research pushed this turn toward executable runner work rather than another registry layer. Hugging Face Hub docs support full commit-pinned snapshot downloads, filtering, local folders, and dry-run planning. Transformers attention docs show backend-specific mask semantics, so trace capture stays on eager attention while fused backends remain timing baselines. Recent artifact-evaluation work frames progress as executable reproduction scripts, and recent LLM reproducibility work identifies environment/versioning/model-access gaps as persistent failure modes.

## Decision

Use `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh` on a capable machine, or set `LOCAL_SNAPSHOT_DIR=/path/to/reviewed-snapshot` and run the same alias. Do not add more doctrine until that path either produces receipts or returns a concrete external-runner failure.
