# PROOFCORE PCD lane audit — rev0853

Created: 2026-06-16T22:46:00Z

## Substance added

rev0853 creates the first executable proof-carrying-data lane:

```text
claim -> public inputs -> witness policy -> commitments -> certificate -> verifier -> accept/reject fixtures
```

The implemented claim is deliberately modest: overlay integrity, patch-chain continuity, proofcore lane presence, path-role-map consistency, and rights-block preservation. This is a transparent deterministic verifier, not a SNARK.

## Why this is the right first lane

The full `zkrtp` and `streamfold` proof payloads are indexed but absent from this overlay. A real cryptographic verifier lane therefore cannot honestly be completed here. The safe forward move is to create the envelope and prove one local claim now, then swap in a recovered cryptographic proof/receipt later.

## Commands

```bash
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/accept/ev-overlay-integrity.rev0853.accept.json
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/reject/ev-overlay-integrity.rev0853.reject.json --expect-fail
python3 scripts/validate_proofcore_pcd_rev0853.py
```

## Non-claims preserved

No zero-knowledge, succinctness, recursive-composition, zkVM receipt, SNARK soundness, or publication-rights claim was added.
