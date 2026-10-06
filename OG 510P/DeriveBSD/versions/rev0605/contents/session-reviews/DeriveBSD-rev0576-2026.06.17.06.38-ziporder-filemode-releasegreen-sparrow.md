# DeriveBSD rev0576 session review — sealed ZIP order and file-mode canonicality

## Purpose

This cut keeps pressure on the scarce FreeBSD real-host proof lane by tightening the sealed transport boundary instead of expanding doctrine. The previous cut rejected ZIP comments, entry extras, and non-Unix entry origins; this cut closes two remaining transport ambiguities: member order and regular-file type metadata.

## Substantive changes

- Hardened `tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py` so sealed archives are rejected before extraction when handoff members do not appear in canonical sorted order.
- Hardened sealed ZIP validation so each accepted entry must encode the exact shared regular-file mode, including the regular-file type bits, rather than only matching permission bits.
- Updated `HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY` in the shared FreeBSD host-proof contract to cover comments, extra fields, Unix origin, canonical entry order, and exact regular-file mode metadata.
- Extended the deterministic sealer/unsealer release-critical check with negative ZIP mutations for reordered handoff members and missing regular-file type bits.
- Extended the sealed importer release-critical check with the same reordered-entry and missing-file-type mutations so direct unseal and one-command sealed import reject the same archive ambiguity.
- Updated the real-host operator packet so the sealing rule names canonical sorted entries and exact regular-file mode metadata.
- Refreshed r604 generated/current surfaces, README, CHANGELOG, proof examples, validation proof-bundle fixture, generated docs, and hygiene evidence.

## Risk reduced

A sealed proof ZIP is only a transport for a finite handoff, but ZIP metadata can still create confusing byte-distinct carriers for the same visible handoff files. Before this cut, a sealed archive with correct names and bytes could still vary in entry order or omit the regular-file type bits while preserving permission bits. That would be avoidable ambiguity during the first real host-proof import. The unsealer and sealed importer now reject those archives before extraction or import.

## Audit/refactor note

The change deliberately reuses the shared host-proof contract instead of adding another registry surface. The audit narrowed the sealed transport policy to executable checks at the boundary where risk occurs: unseal and sealed import.

## Validation

- `tools/hygiene.py --profile release-critical --ledger-json /tmp/DeriveBSD-rev0576-release-critical-ledger.json --timeout-seconds 120`, completed by resumable chunks after the long FreeBSD proof-import segment crossed the outer cloudtainer command boundary.
- `tools/hygiene.py --profile schema-cube-audit --ledger-json /tmp/DeriveBSD-rev0576-schema-cube-audit-ledger.json --timeout-seconds 120`.
- `tools/validate_spec_examples.py` validated 469 examples.
- `tools/check_json_duplicate_key_rejection.py` scanned 1461 JSON files.
- `tools/check_generated_docs.py`, `tools/check_current_generated_surface_sync.py`, and `tools/check_no_python_bytecode_artifacts.py` passed.

## Remaining caveat

This still does not contain non-simulated FreeBSD host proof. The next true milestone remains a real `15.1-RELEASE` host run, sealed or loose handoff return, strict import, and audit as `real-host-proof` with `primary-production` target-tier evidence.
