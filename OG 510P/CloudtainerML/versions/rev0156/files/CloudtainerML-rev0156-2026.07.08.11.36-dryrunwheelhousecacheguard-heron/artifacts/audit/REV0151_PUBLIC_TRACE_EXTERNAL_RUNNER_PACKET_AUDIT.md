# Public trace external runner packet audit — REV0151

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

Builds and smoke-checks a live-closure external runner packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama trace on a machine with runtime, disk, and network. REV0150 stops copying the entire tools directory; it carries only the active first-real-trace closure plus generated runner scripts, while preserving snapshot download-plan, runtime lock, cache-root, digest-receipt, offline-quarantine, and preflight-handoff gates.

Packet zip: `artifacts/external-runner/REV0151_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`  
Packet SHA-256: `b4538ad99143eb574011a86de57ace606ee6ed4fa02558db921aad628a8ddc9a`

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
