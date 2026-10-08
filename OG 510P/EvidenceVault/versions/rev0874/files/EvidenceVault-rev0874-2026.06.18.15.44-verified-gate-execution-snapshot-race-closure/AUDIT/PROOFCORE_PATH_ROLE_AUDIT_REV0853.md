# PROOFCORE path-role audit — rev0853

Created: 2026-06-16T22:46:00Z

## What changed

rev0853 adds `PROOFCORE/maps/canonical_path_to_role.rev0853.csv`, a concrete role map for the proof-adjacent subset of the carried canonical file index.

## Metrics

- Canonical index rows carried: `4586`
- Proof-signal paths mapped: `1374`
- Proof-signal bytes mapped: `30172510`
- Mapped proof payloads present in this overlay: `0`

## Role counts

```json
{
  "abi_ir_or_protocol_ir": 59,
  "accept_fixture": 44,
  "attestation_or_receipt": 711,
  "governance_or_rights": 8,
  "paper_or_render": 153,
  "public_input_or_commitment": 25,
  "reject_fixture": 7,
  "schema": 8,
  "source": 17,
  "unknown": 105,
  "verifier_code": 118,
  "witness_or_witness_policy": 119
}
```

## Main finding

The proofcore is no longer just a vague recovery idea. There is now a table that says which indexed files look like papers/renders, schemas, protocol IR, public inputs, witness policy, verifiers, fixtures, receipts/attestations, source, or governance. The result still confirms the same dangerous fact: the overlay carries the map, not the canonical proof payloads.

## Highest-risk next edge

Use the map to recover one P0 `zkrtp` or `streamfold` verifier/receipt/public-input edge and plug it into the same claim/public-input/verifier/fixture/certificate envelope introduced in rev0853.
