# Start here — REV0156

Current revision: `rev0156`  
Package: `CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron.zip`  
One-command path: `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Bootstrap dry run: `BOOTSTRAP_RUNTIME=1 PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Wheelhouse bootstrap: `PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Capture-only alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Snapshot-prepare alias: `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`  
External runner: `artifacts/external-runner/REV0156_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`  
Runtime lock: `artifacts/runtime/REV0156_public_trace_requirements.txt`  
Run packet: `artifacts/run-manifests/REV0156_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json`

## First action

Run the dry bootstrap check through the same one-command wrapper, then the first-real-trace command. If it fails, read `artifacts/audit/REV0156_PUBLIC_TRACE_FIRST_REAL_TRACE_STATUS.json` and fix `first_blocker_candidate` before adding doctrine.

```bash
BOOTSTRAP_RUNTIME=1 PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

With an already reviewed local snapshot:

```bash
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

## Boundary

Network/download work belongs only to snapshot preparation. Evidence capture is local-only and must bind to a digest-verified local snapshot. The default cache root is project-local; accidental no-symlink cache duplication is refused unless explicitly approved. Until trace/provenance, evaluation, selector, replay, handoff, and named-hardware timing receipts exist, promotion remains false.
