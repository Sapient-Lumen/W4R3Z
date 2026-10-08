# Public trace run-manifest coherence audit — REV0156

Status: `pass`  
Promotion allowed: `false`

Guards against a subtle but expensive handoff defect: a current external runner can carry stale revision integers, timestamps, or paths in the run packet/source lock even when the shell aliases are current.

## Files checked

- `artifacts/run-manifests/REV0156_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json`
- `artifacts/run-manifests/REV0156_TINYLLAMA_SOURCE_LOCK.json`

## Errors

- none
