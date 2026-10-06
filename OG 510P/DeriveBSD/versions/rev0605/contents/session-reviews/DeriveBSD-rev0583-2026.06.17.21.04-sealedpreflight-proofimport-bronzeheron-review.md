# DeriveBSD rev0583 session review — sealed preflight proof import

Revision: `DeriveBSD-rev0583-2026.06.17.21.04-sealedpreflight-proofimport-bronzeheron`
Base: `DeriveBSD-rev0582-2026.06.17.20.25-workorderverify-proofkit-copperlynx`
Cube cut: `2026-06-17r609`

## Risk addressed

The highest-risk unfinished milestone remains the first imported, non-simulated FreeBSD host proof. rev0582 made the work order self-verifying, but a returned sealed handoff archive could still proceed directly to publish after unseal/import. rev0583 adds an explicit sealed-import preflight so scarce returned proof can be snapshotted, unsealed, reverified, copied through the importer staging path, and assigned a predicted import identity before anything is published into the checked-in import root.

## Substantive changes

- Added `tools/freebsd/preflight_sealed_removable_media_local_fallback_host_proof_import.py`.
- Added release-critical `tools/check_removable_media_local_fallback_freebsd_host_proof_sealed_preflight.py`.
- Updated `tools/freebsd/host_proof_contract.py` to bind the new sealed preflight policy/path and expand the proof-tool digest surface to 18 rows.
- Updated the staged real-host proof work order so `IMPORT_IN_CLOUDTAINER.sh` verifies the kit, runs sealed preflight with `--require-primary-target`, then runs the sealed importer, import audit, and proof-status reporter.
- Updated `tools/freebsd/verify_real_host_proof_work_order.py`, the work-order checker, and the real-host operator packet around preflight-first import.
- Promoted the new checker into `tools/hygiene.py` release-critical execution, raising the release-critical profile from 50 to 51 checks.
- Regenerated host-smoke/proof-bundle examples, work-order current artifacts, generated docs/catalogs, schema audit examples, hygiene checkset, and current operator surfaces for `2026-06-17r609`.
- Refactored the front-door `docs/00-index.md` release coverage after broad version edits had accidentally erased the r608 heading.

## Evidence

- Release-critical ledger: `session-reviews/DeriveBSD-rev0583-2026.06.17.21.04-sealedpreflight-proofimport-bronzeheron-release-critical-ledger.json`
- Schema-cube-audit ledger: `session-reviews/DeriveBSD-rev0583-2026.06.17.21.04-sealedpreflight-proofimport-bronzeheron-schema-cube-audit-ledger.json`
- Proof-status report: `session-reviews/DeriveBSD-rev0583-2026.06.17.21.04-sealedpreflight-proofimport-bronzeheron-proof-import-status.json`

## Remaining truth

The checked-in import root is still empty. The proof status remains `blocked-no-real-host-proof-import`; there is still no imported real FreeBSD host proof. This revision makes the returned-proof import path safer and more explicit, but it does not create the missing host evidence.
