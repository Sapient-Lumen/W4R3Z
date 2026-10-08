# Public trace external runner packet audit — REV0139

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

Builds and smoke-checks a compact external runner packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama trace on a machine with runtime, disk, and network. This is a refactor of the active surface, not a new doctrine layer.

Packet zip: `artifacts/external-runner/REV0139_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`  
Packet SHA-256: `796ce3a868cae1c1dbf146e12af9b8a92142e49b6766193719425b4053380eff`

## Extracted smoke

- dependency closure return code: `0`
- run return code: `1`
- direct current alias return code: `1`
- reaches intended preflight/pass: `True`
- direct current alias reaches intended preflight/pass: `True`

## Errors

- none

## Warnings

- `extracted_packet_current_environment_still_blocks_real_capture_expected_without_snapshot_or_transformers`

## Interpretation

The correction is operational: carry less, run sooner, and produce real receipts on an external runner rather than spending another turn expanding the registry surface.
