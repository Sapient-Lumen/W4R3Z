# DeriveBSD-rev0587-2026.06.17.23.31-importlock-raceguard-blackbear session review

## Risk focus

The first real FreeBSD proof is still the scarce milestone. This revision hardens the returned sealed-proof importer against concurrent cloudtainer sessions so publish, verified reuse, and replacement decisions cannot interleave around the first import root.

## Substantive changes

- Added `SEALED_IMPORT_LOCK_POLICY` to the shared FreeBSD host-proof contract.
- Wrapped sealed publish/reuse/replace decisions in an exclusive sibling `.sealed-import.lock` held by `tools/freebsd/import_sealed_removable_media_local_fallback_host_proof_handoff.py`.
- Active or stale lock state now fails before import-root mutation; successful imports remove the lock directory and fsync the parent.
- Sealed `import.receipt.json` now records `sealed_import_lock_policy` and `sealed_import_lock_path` in source-transport evidence.
- The import auditor rejects sealed imports missing expected lock policy/path evidence.
- The sealed importer release check now proves active-lock refusal leaves the import root untouched, successful sealed import cleans lock state, and receipts bind the lock policy/path.
- Regenerated the real-host proof work order, verifier-bound manifest, operator packet, current docs, generated catalogs, schema examples, and proof fixtures for `2026-06-17r613`.

## Audit/refactor

The r613 generated examples exposed stale schema constants and a stale bootstrap hygiene-ledger fingerprint. This revision updates those surfaces instead of letting schema/example drift accumulate behind a green local proof-path check.

## Validation

- Release-critical hygiene: `51/51` passed.
- Schema-cube-audit profile: `3/3` passed.
- Proof status: `blocked-no-real-host-proof-import`.
- Real host proof count: `0`.
- Primary-production real host proof count: `0`.

## Remaining truth

There is still no imported real FreeBSD host proof. The live import root remains empty and `proof_complete=false`.

## Next highest-risk step

Run the r613 work order on a primary-production FreeBSD 15.1 host and import the sealed returned handoff. After a real import lands, audit whether some guard scaffolding can collapse into a simpler operator path.
