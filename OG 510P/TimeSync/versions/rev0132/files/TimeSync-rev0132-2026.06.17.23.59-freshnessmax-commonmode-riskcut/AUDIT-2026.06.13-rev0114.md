# rev0114 audit — policy authority digest binding

## Focus

rev0114 continues FT-0090 by closing an executable digest-binding seam in policy lifecycle-authority references. The prior revisions had already made many digest-looking surfaces fail closed when the `binds` value named the wrong artifact class. The policy lifecycle-authority branch still had broad schema enums for compact rotation/status/compromise summaries and several inline `isinstance` checks, so wrong artifact-class bindings could look acceptable.

## Findings

The risky pattern was a compact lifecycle-authority summary that carried a SHA-256 digest object, but the digest bound a different class of artifact than the field name and semantics required. Examples include:

```text
anti_rollback_sequence.status_record_digest.binds = profile_compatibility_statement
rotation_statement_digest.binds = transparency_trust_policy_lifecycle_status
successor_authority_digest.binds = profile_compatibility_statement
```

Those are not schema-shape errors in the embedded policy lifecycle-authority reference surface. They are semantic binding errors: the digest object exists, but it points at the wrong kind of thing.

## Changes

- Added `tools/policy_authority_digest_semantics.py`.
- Wired it into `check_policy_lifecycle_authority_reference` and `check_policy_lifecycle_authority_recovery_attestation`.
- Added helper self-tests.
- Added three derivation-checked negative fixtures and vectors `TV-N311` through `TV-N313`.

## Boundary

This does not introduce a lifecycle-authority registry, repository verifier, rotation protocol, or recovery workflow. It only enforces that compact summary digest fields bind the artifact class they claim to summarize.

## Remaining risk

FT-0090 remains open. The next practical targets are still the largest inline branches in `tools/validate_archive.py`, especially aggregate correction-authority reference/lifecycle checks and transparency trust-policy reference checks, but only where extraction closes executable gaps or reduces copy drift.
