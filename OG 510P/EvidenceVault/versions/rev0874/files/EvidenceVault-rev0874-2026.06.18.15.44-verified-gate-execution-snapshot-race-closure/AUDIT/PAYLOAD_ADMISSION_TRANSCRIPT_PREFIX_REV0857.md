# Payload admission and transcript-prefix audit — rev0857

## Status

`payload_admission_executable_transcript_prefix_bound_payloads_still_missing`

rev0857 addresses the highest-risk live gap in the streamfold PCD lane: the 17 canonical `streamfold_sumcheck_toy_v2_family` payloads are still absent, but candidate-root admission is now executable instead of prose-only.

## What changed

- Added `PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py`.
- Added `PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py`.
- Added `PROOFCORE/verifiers/verify_streamfold_payload_admission_lane_rev0857.py`.
- Added a parent-linked rev0857 PCD-shaped lane that replays rev0856 from `PATCHES/rev0856-to-rev0857-overlay.patch` plus `PROOFCORE/parent_snapshots/rev0856/*`.

## Payload admission

Expected payloads: **17**  
Expected bytes: **25066**  
Still absent from this overlay: **17**

Role counts:

```json
{
  "abi_ir_or_protocol_ir": 7,
  "attestation_or_receipt": 9,
  "public_input_or_commitment": 1
}
```

Minimum first recovery set:

```text
artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2.json
artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2_digest.json
artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2_1_meta.json
certs/curated/streamfold/examples/evidence_bundle_scitt_demo/sumcheck_abi_v2/stmt_sumcheck_abi_v2.dsse.json
```

Candidate-root commands:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode minimum
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode full
```

The verifier checks exact path, size, SHA-256, `INDEX/files.csv` agreement, JSON object parseability, and role coverage. It does not copy payloads and does not grant publication rights.

## Transcript-prefix hardening

The accept fixture now derives challenges from public context, claim hash, verifier/contract identities, current running claim, current round polynomial, and previous public transcript-message hashes.

Derived challenges over `Fp97`: `[66, 52]`  
Final evaluation: `87`  
Final transcript-prefix hash: `87e0069cba29d3a3a540dce1138de73a4819e0199745f7360f5c78ebb030ad59`

Reject fixtures now cover:

1. Bad previous transcript prefix in round 2.
2. Tampered payload-admission-contract hash in public context.

## Audit/refactor result

The active verifier surface is now `verify_streamfold_payload_admission_lane_rev0857.py`; older lanes remain historical checkpoints. This is a proof-carrying-data-shaped chain of deterministic checks, not a SNARK, not zero knowledge, not succinct, not a streamfold correctness proof, and not a rights grant.
