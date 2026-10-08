# Next turn prompt — REV0156

Continue from `rev0156` / `CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron.zip`. Do not add doctrine unless it removes an executable blocker.

Highest priority:

```bash
BOOTSTRAP_RUNTIME=1 PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

If the capable host uses a prebuilt wheelhouse:

```bash
PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

If this cloudtainer still lacks runtime/snapshot capability, work only on concrete blockers or measurable waste: first-blocker receipt quality, bootstrap/wheelhouse path failures, active shell syntax/assignment hazards, stale current run-packet/source-lock identity, external-runner closure failures, duplicate generated payloads, or active-surface regressions.

Current stable capture alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh` pointing at `artifacts/capture-kit/REV0156_RUN_TINYLLAMA_PUBLIC_TRACE.sh`.
