# Public trace external runner packet audit — REV0145

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

Builds and smoke-checks a compact external runner packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama trace on a machine with runtime, disk, and network. This is a refactor of the active surface, not a new doctrine layer. REV0145 also carries a runtime import/surface smoke, the stat-bound digest receipt cache, offline capture quarantine, and preflight-handoff contract so the first real trace does not waste time downloading/materializing, rehashing, or silently depending on network during evidence capture.

Packet zip: `artifacts/external-runner/REV0145_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`  
Packet SHA-256: `a0e3cf440dad49ccf916016cb0b4ef5e3b86188b45fdf0ad4ad274dc19088cc6`

## Extracted smoke

- dependency closure return code: `0`
- first-trace surface audit return code: `0`
- first real trace return code: `1`
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
