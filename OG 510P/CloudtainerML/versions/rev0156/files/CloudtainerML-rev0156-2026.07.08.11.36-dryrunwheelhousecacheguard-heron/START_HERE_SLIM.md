# Start here slim — REV0156 / rev0156

Current trace entrypoints: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh` for the local-only capture lane, `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh` for the blocker-first first-real-trace command, and `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh` for the only network-enabled snapshot phase.

Run this first:

```bash
PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/REV0156_BOOTSTRAP_PUBLIC_TRACE_ENV.sh
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

Then fix `artifacts/audit/REV0156_PUBLIC_TRACE_FIRST_REAL_TRACE_STATUS.json:first_blocker_candidate` before adding any registry or doctrine work.
