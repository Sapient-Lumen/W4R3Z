# REV0101 to REV0102 migration map

## Revision intent

rev0102 narrows FT-0090 by extracting transparency-policy lifecycle-equivalence timing from the validator and making compatibility statement signature/evidence ordering executable.

## New files

- `tools/policy_equivalence_temporal.py`
- `examples/negative/profile-compatibility-policy-equivalence-after-signature-invalid.json`
- `examples/negative/profile-compatibility-policy-revocation-after-equivalence-invalid.json`
- `examples/negative/profile-compatibility-policy-drift-after-equivalence-invalid.json`
- `AUDIT-2026.06.13-rev0102.md`
- `archive/REV0102-AUDIT-POLICY-EQUIVALENCE-TEMPORAL-REFACTOR.md`
- `archive/REV0101-TO-REV0102-MIGRATION-MAP.md`

## Changed files

- `tools/validate_archive.py`
  - imports the new policy-equivalence helper and self-test
  - delegates policy lifecycle equivalence timing to the helper
  - reports rev0102 validation output
- `profiles/compatibility/p3-replay-transparency-policy-equivalence.json`
  - moves `binding.signed_at` after the lifecycle-equivalence evaluation it covers
- copied profile-compatibility negative fixtures derived from that positive
  - normalized incidental signature timing so intended negative conditions remain clear
- `tests/semantic-test-vectors.yaml`
  - adds `TV-N273` through `TV-N275`
- `tests/fixture-derivations.yaml`
  - adds `DF-0102-001` through `DF-0102-003`
- `README.md`, `START_HERE.md`, `INDEX.md`, `VALIDATION-REPORT.md`, `REVISION-RECEIPT.json`, `CHANGELOG.md`, `frontier-ticket.json`, `MANIFEST.json`

## Compatibility notes

No TimeState core field changed. No schemas were expanded. Existing valid artifacts remain valid except for compatibility statements whose policy-equivalence evidence is evaluated after the statement signature or whose revocation/drift checks happen after the lifecycle-equivalence evaluation they support.
