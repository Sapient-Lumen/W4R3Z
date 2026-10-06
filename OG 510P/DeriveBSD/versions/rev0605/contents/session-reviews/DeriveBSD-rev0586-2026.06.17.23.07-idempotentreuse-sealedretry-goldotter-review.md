# DeriveBSD-rev0586-2026.06.17.23.07-idempotentreuse-sealedretry-goldotter session review

## Risk focus

The first real FreeBSD proof is still the scarce milestone. This revision hardens the retry path around returned sealed proof archives so an interrupted or repeated cloudtainer import can reuse an already-published matching digest import without overwriting evidence or failing as a duplicate.

## Substantive changes

- Added `--reuse-existing-import` to sealed returned-proof preflight and importer.
- Duplicate sealed imports remain rejected by default unless `--reuse-existing-import` or `--replace` is explicit.
- Reuse now validates the existing predicted digest import with the import auditor and requires the same copied handoff snapshot, sealed archive SHA-256, sealed archive size, and sealed source-transport evidence.
- `IMPORT_IN_CLOUDTAINER.sh` now runs sealed preflight and sealed import with `--require-primary-target --reuse-existing-import`.
- Sealed preflight now reports `ready-to-reuse-existing-*` statuses so retry readiness is visible before publish.
- Sealed importer and preflight release checks now prove default duplicate refusal plus audit-clean digest-bound reuse.
- Regenerated proof bundle, host-smoke fixtures, work order, operator packet, current docs, generated catalogs, and schema/cube audit examples for `2026-06-17r612`.

## Audit/refactor

The current hygiene-ledger surface was misleading: the canonical spec example can be a bootstrap artifact, while full release evidence belongs in session-review ledgers. This revision makes that distinction explicit in `docs/current/hygiene-run-ledger.md` and keeps the full `51/51` evidence in `DeriveBSD-rev0586-2026.06.17.23.07-idempotentreuse-sealedretry-goldotter-release-critical-ledger.json`.

## Validation

- Release-critical hygiene: `51/51` passed.
- Schema-cube-audit profile: `3/3` passed.
- Proof status: `blocked-no-real-host-proof-import`.
- Real host proof count: `0`.
- Primary-production real host proof count: `0`.

## Remaining truth

There is still no imported real FreeBSD host proof. The live import root remains empty and `proof_complete=false`.

## Next highest-risk step

Run the r612 work order on a primary-production FreeBSD 15.1 host and import the sealed returned handoff. After a real import lands, collapse any proof-path scaffolding that becomes redundant rather than continuing to add guards around absence.
