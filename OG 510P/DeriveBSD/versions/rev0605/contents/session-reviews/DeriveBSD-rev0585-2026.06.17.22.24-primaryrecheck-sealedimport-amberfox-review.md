# DeriveBSD rev0585 session review — primary recheck sealed import

## Cut

- Version: `2026-06-17r611`
- Archive stem: `DeriveBSD-rev0585-2026.06.17.22.24-primaryrecheck-sealedimport-amberfox`

## Risk targeted

The riskiest unfinished milestone remains the first non-simulated FreeBSD host proof. This cut focuses on the returned sealed proof path: preflight already required the primary-production target, but the actual sealed importer did not repeat that requirement. A swapped archive between preflight and import could therefore publish a non-primary import before later audit failure.

## Substance changed

- `tools/freebsd/import_sealed_removable_media_local_fallback_host_proof_handoff.py` now accepts `--require-primary-target` and enforces primary-production target evidence after archive snapshot/unseal and before publish.
- The sealed importer now audits the import root before publish, so a dirty checked-in root is refused before a returned archive can add more state.
- If post-import audit fails, the sealed importer removes the newly published import by default; `--keep-failed-import` is the explicit forensics escape hatch.
- `validation/freebsd-real-host-proof-work-order/current/IMPORT_IN_CLOUDTAINER.sh` now passes `--require-primary-target` to both sealed preflight and sealed import.
- `tools/check_removable_media_local_fallback_freebsd_host_proof_sealed_importer.py` now proves the new gate by building a temporary synthetic real-like supported-floor handoff and showing that primary-target sealed import rejects it before publishing.
- Current docs, operator packet, generated catalogs, schema/cube examples, and front-door index were refreshed for `2026-06-17r611`.

## Audit/refactor notes

- Corrected stale host-smoke schema example drift by restoring the canonical cloudtainer refusal receipt as the schema example.
- Regenerated context-pack and document catalog surfaces after the new changelog/index/doc changes.
- Trimmed `docs/00-index.md` back under the front-door budget without removing required `## New in ...` coverage headings.

## Validation evidence

- Release-critical hygiene ledger: `DeriveBSD-rev0585-2026.06.17.22.24-primaryrecheck-sealedimport-amberfox-release-critical-ledger.json` — 51/51 passed.
- Schema-cube-audit ledger: `DeriveBSD-rev0585-2026.06.17.22.24-primaryrecheck-sealedimport-amberfox-schema-cube-audit-ledger.json` — 3/3 passed.
- Proof import status: `DeriveBSD-rev0585-2026.06.17.22.24-primaryrecheck-sealedimport-amberfox-proof-import-status.json` — `blocked-no-real-host-proof-import`, `real_host_proof=0`, `primary_production_real_host_proof=0`.

## Remaining truth

No real FreeBSD host proof is checked in. The import root remains empty by design; this cut reduces the risk that the first returned proof archive can contaminate the import root or pass a weaker gate than the preflight path.
