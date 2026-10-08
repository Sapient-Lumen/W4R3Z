# Streamfold sumcheck toy v2 recovery checklist — rev0855

This is the narrow recovery target selected by the rev0854 frontier. The rev0855 work does **not** recover these canonical files; it makes their absence executable and makes the first mathematical harness concrete.

## First recovery set

Recover these four files first from the full canonical tree and verify exact SHA-256/byte matches:

1. `artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2.json`
2. `artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2_digest.json`
3. `artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2_1_meta.json`
4. `certs/curated/streamfold/examples/evidence_bundle_scitt_demo/sumcheck_abi_v2/stmt_sumcheck_abi_v2.dsse.json`

## Full lane payload gate

The complete lane has `17` expected paths, `25066` bytes, and these roles: `abi_ir_or_protocol_ir:7, attestation_or_receipt:9, public_input_or_commitment:1`.

The exact gate is `payload_manifest.rev0855.json`. A candidate canonical mount can be checked with:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py \
  --fixture PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-lane.rev0855.accept.json \
  --candidate-root /path/to/full/canonical/tree
```

## Non-claims

This checklist is not a rights grant, not a SNARK proof, not zero knowledge, and not a replacement for the missing canonical streamfold payloads.
