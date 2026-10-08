
# Session review — rev0852 SNARK-origin proofcore recovery

Created: 2026-06-16T12:46:00-04:00 / 2026-06-16T16:46:00Z

## User context applied

The project began as a SNARKs-adjacent proof exploration, and that was the core for most of its life. This reframes the mission from a general evidence vault into a **proof-carrying evidence vault**.

## What I found

The carried canonical index exposes 1067 broad proof-signal paths. `zkrtp` and `streamfold` are the clearest buried core: `zkrtp` has 193 files / 18,902,244 bytes in the rights ledger, and `streamfold` has 83 files / 2,778,263 bytes. The index also contains `sumcheck`, `FRI`, `PCS`, `Halo2`, lookup, folding, proof receipts, witnesses, verifiers, and policy-carrying receipt surfaces.

The important limitation is that this overlay ZIP contains 0 of the 1067 broad proof-signal payload paths as actual payload files. It carries indexes, ledgers, patches, and audit surfaces. It is a recovery map, not the proof tree.

## What changed in rev0852

- Added `AUDIT/SNARK_ORIGIN_PROOFCORE_RECOVERY_REV0852.md/json`.
- Added `PROOFCORE_RECOVERY_PLAN_REV0852.md`.
- Added `scripts/validate_snark_origin_proofcore_rev0852.py`.
- Updated `README.md`, `CHANGE_SUMMARY.md`, `OVERLAY_COMMANDS.md`, patch identity, provenance, patch hashes, and overlay manifest surfaces.
- Preserved the publication block.

## Best next move

Recover or mount the full canonical tree and build `PROOFCORE/maps/canonical_path_to_role.csv`. Start with one minimal green path: one claim, one public input/commitment, one verifier, one accept fixture, one reject fixture, and one explicit rights decision.

## Publication status

Still publication-blocked. No rights conclusion was added or inferred.
