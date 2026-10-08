# Mission audit — REV0141

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current first-trace alias: `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Current capture alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Primary artifact: `artifacts/external-runner/REV0141_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`

## Heart of the mission

CloudtainerML is a claim compiler. The useful unit is not a registry entry or a paper summary; it is a claim that survives hostile falsification with digest-bound provenance, replayable receipts, and named-hardware timing. The immediate mission is one concrete public-model trace that can be inspected, replayed, handed off, and then used to promote or kill a selector claim.

## Riskiest unfinished work

The first real digest-bound TinyLlama trace still has not been captured in this cloudtainer. The highest-risk remaining work is therefore not new doctrine; it is getting the external runner to survive the boring operational hazards between an archive and the first trace receipts: Python environment setup, model snapshot materialization, local-only binding, and coherent handoff identity.

## What went wrong or wasteful

Two operational problems were likely to waste the next real run:

1. The one-command runner's bootstrap phase installed requirements into ambient `python3` via a child shell. On modern systems, that can fail under externally managed Python rules; even when it succeeds, activation state would not persist into the parent runner.
2. The active run packet/source lock carried current `revision` strings but stale `revision_int`/`current_revision_int` fields from the previous packet lineage. That is not a science failure, but it is a handoff integrity defect: the external runner could produce receipts whose shell surface says current while its identity packet says otherwise.

## What changed in REV0141

- Added `tools/public_trace_bootstrap_runtime_audit.py`.
- Added `tools/public_trace_run_manifest_coherence_audit.py`.
- Refactored `REV0141_BOOTSTRAP_PUBLIC_TRACE_ENV.sh` to create/use `.venv-public-trace`, install active requirements there, and emit `artifacts/runtime/CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh`.
- Refactored `REV0141_FIRST_REAL_TRACE_ONE_COMMAND.sh` to source the generated bootstrap env so the venv PATH persists into snapshot and capture phases.
- Added `hf_xet` to `artifacts/runtime/REV0141_public_trace_requirements.txt`.
- Fixed active run-packet/source-lock revision identity fields and made the new coherence audit part of the live path.
- Rebuilt the compact external runner so `BOOTSTRAP_RUNTIME.sh` calls the same project-local bootstrap wrapper instead of writing into system Python.

## What is still missing

No real public trace was captured here. Promotion remains forbidden until a capable runner produces trace/provenance, gate, evaluation receipt, selector-entry receipt, replay, handoff archive, and named-hardware timing receipts. The expected local blocker remains the lack of a complete digest-verified TinyLlama snapshot and capture runtime in this cloudtainer.

## Decision

Use the external runner and run:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

If that fails, fix the first concrete blocker returned by the runner before expanding registries, doctrine, or new experiment families.
