# DeriveBSD rev0575 session review — ZIP canonical metadata guard

## Purpose

This cut continues the scarce FreeBSD real-host proof lane by removing another first-run integrity ambiguity rather than adding doctrine. The previous cut made the sealer archive a copied nofollow staging snapshot; this cut tightens what counts as a deterministic sealed ZIP transport before unseal/import.

## Substantive changes

- Added `HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY` to the shared FreeBSD host-proof contract.
- Hardened `tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py` so sealed archives are rejected before extraction when they carry:
  - archive-level ZIP comments,
  - per-entry ZIP comments,
  - per-entry ZIP extra fields,
  - non-Unix entry-origin metadata.
- Hardened the one-command sealed importer so `source_transport` and `archive_snapshot` provenance preserve the canonical ZIP metadata policy.
- Extended the import auditor to reject sealed import receipts that do not bind the canonical ZIP metadata policy.
- Extended release-critical sealed archive/import checks with negative mutations for archive comments and entry extra fields.
- Updated the sealer check to assert produced archives have no ZIP comments or extra fields and use Unix entry metadata.
- Refreshed r603 generated/current surfaces, README, CHANGELOG, host-smoke/proof-bundle examples, validation proof-bundle fixture, and generated docs.

## Risk reduced

A sealed proof ZIP is transport, not a second proof format. Before this cut, a ZIP could be byte-distinct and carry out-of-band comment/extra metadata even though the unsealed handoff bytes were unchanged. That could confuse archive digest provenance, allow hidden transport annotations, or create avoidable ambiguity during the first real host-proof import. The unsealer/importer now reject those bytes instead of letting them become durable proof context.

## Validation

- `tools/hygiene.py --profile release-critical --ledger-json spec/examples/cube.hygiene.run.ledger.json --timeout-seconds 120`, completed by a resumable chunk after the initial 35 passed rows.
- `tools/hygiene.py --profile schema-cube-audit --ledger-json /tmp/DeriveBSD-rev0575-schema-cube-audit-ledger.json --timeout-seconds 120`.
- `tools/validate_spec_examples.py` validated 469 examples.
- `tools/check_json_duplicate_key_rejection.py` scanned 1458 JSON files.
- `tools/check_generated_docs.py`, `tools/check_current_generated_surface_sync.py`, and `tools/check_frontdoor_budget.py` passed.

## Remaining caveat

This still does not contain non-simulated FreeBSD host proof. The next true milestone remains a real `15.1-RELEASE` host run, sealed or loose handoff return, strict import, and audit as `real-host-proof` with `primary-production` target-tier evidence.
