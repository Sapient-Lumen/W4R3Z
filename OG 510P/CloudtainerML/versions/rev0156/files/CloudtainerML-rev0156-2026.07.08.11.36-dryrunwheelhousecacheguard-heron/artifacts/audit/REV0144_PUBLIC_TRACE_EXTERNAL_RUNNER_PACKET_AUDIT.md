# Public trace external runner packet audit — REV0144

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

Builds and smoke-checks a compact external runner packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama trace on a machine with runtime, disk, and network. This is a refactor of the active surface, not a new doctrine layer. REV0144 also carries the stat-bound digest receipt cache, offline capture quarantine, and preflight-handoff contract so the first real trace does not waste time rehashing or silently depend on network during evidence capture.

Packet zip: `artifacts/external-runner/REV0144_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`  
Packet SHA-256: `cbb8049414243bf434759d5710327e6deae0488e9491b3fb9938cdfca13fbaff`

## Extracted smoke

- dependency closure return code: `0`
- first-trace surface audit return code: `0`
- first real trace return code: `2`
- run return code: `1`
- direct current alias return code: `1`
- first real trace reaches actionable gate/pass: `True`
- reaches intended preflight/pass: `True`
- direct current alias reaches intended preflight/pass: `True`

## Errors

- none

## Warnings

- `extracted_packet_current_environment_still_blocks_real_capture_expected_without_snapshot_or_transformers`

## Interpretation

The correction is operational: carry less, run sooner, and produce real receipts on an external runner rather than spending another turn expanding the registry surface.
