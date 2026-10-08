# Public trace external runner packet audit — REV0149

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

Builds and smoke-checks a live-closure external runner packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama trace on a machine with runtime, disk, and network. REV0149 stops copying the entire tools directory; it carries only the active first-real-trace closure plus generated runner scripts, while preserving snapshot download-plan, runtime lock, cache-root, digest-receipt, offline-quarantine, and preflight-handoff gates.

Packet zip: `artifacts/external-runner/REV0149_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`  
Packet SHA-256: `cabb5771defbf3c2102b3bf1d1dcb68dcc87d7b4098a26deef7e12c1d8325f5b`

## Extracted smoke

- dependency closure return code: `0`
- live-closure trim audit return code: `0`
- first-trace surface audit return code: `0`
- cache-root contract audit return code: `0`
- runtime requirement lock audit return code: `0`
- snapshot download-plan gate audit return code: `0`
- first real trace return code: `0`
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

The correction is operational: carry less, run sooner, and produce real receipts on an external runner rather than spending another turn expanding the registry surface; the packet now fails if a reachable script/import is missing or if unrelated tool/experiment files creep back into the runner.
