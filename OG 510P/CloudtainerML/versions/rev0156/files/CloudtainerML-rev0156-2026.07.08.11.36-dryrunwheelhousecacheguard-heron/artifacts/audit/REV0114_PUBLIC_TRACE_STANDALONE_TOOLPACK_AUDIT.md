# Public trace standalone toolpack audit — REV0114

Status: `pass_with_blockers`  
Verdict: `standalone_toolpack_replay_verified_not_promotion`  
Promotion allowed: `false`

Adds an executable self-contained handoff-toolpack self-check. The gate is run from an extracted archive with no manifest/handoff-dir arguments, without CUBE-META or the source cube checkout, and rejects a tampered bundled replay tool by digest.

## Research basis

- SLSA build provenance treats provenance as data consumers verify against expected artifact production: https://slsa.dev/spec/v1.2/build-provenance
- in-toto link attestations bind step products in `subject` and inputs in `materials`: https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md
- Hugging Face `snapshot_download()` needs an explicit `revision` for immutable model snapshots: https://huggingface.co/docs/huggingface_hub/en/guides/download

## Checks

- extracted standalone gate return code: `0`
- tampered standalone gate return code: `1`

## Blockers

- `real_public_trace_and_named_hardware_timing_still_required_for_promotion`

## Errors

- none
