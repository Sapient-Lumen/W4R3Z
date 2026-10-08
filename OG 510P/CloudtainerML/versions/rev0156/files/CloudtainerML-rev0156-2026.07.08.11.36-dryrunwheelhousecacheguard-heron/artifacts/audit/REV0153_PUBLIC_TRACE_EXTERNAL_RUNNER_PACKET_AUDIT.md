# Public trace external runner packet audit — REV0153

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

Builds and smoke-checks a live-closure external runner packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama trace on a machine with runtime, disk, and network. REV0153 keeps the live-closure packet trimmed and smoke-checked while adding semantic-currentness discipline around the runner-facing docs and metadata.

Packet zip: `artifacts/external-runner/REV0153_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`  
Packet SHA-256: `7252728abab2d0a7b95ee00c4dfd6caf0efa0521c9bc2a211981ed855f180fd0`

## Extracted smoke

- dependency closure return code: `0`
- live-closure trim audit return code: `0`
- runner manifest integrity audit return code: `0`
- runner smoke_validate fallback return code: `0`
- first-trace surface audit return code: `0`
- cache-root contract audit return code: `0`
- runtime requirement lock audit return code: `0`
- snapshot download-plan gate audit return code: `0`
- first real trace return code: `0`
- capture-start preflight return code: `1`
- direct current alias syntax return code: `0`
- first real trace reaches actionable gate/pass: `True`
- reaches intended preflight/pass: `True`
- direct current alias syntax/manifest-exec check passes: `True`

## Errors

- none

## Warnings

- `extracted_packet_current_environment_still_blocks_real_capture_expected_without_snapshot_or_transformers`

## Interpretation

The correction is operational: carry less, run sooner, and produce real receipts on an external runner rather than spending another turn expanding the registry surface; the packet now fails if a reachable script/import is missing, if unrelated tool/experiment files creep back into the runner, or if the runner-local manifest cannot substitute for full-cube CHECKSUMS.sha256 in the compact packet.
