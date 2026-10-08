# rev0763 canonical projection integrity audit (fallback boundary)

## Invariant

Canonical envelope bytes are authoritative. A duplicated parent/queue column is usable only after all canonical-derived fields are checked together. Missing values are contradictions, not defaults. The verifier returns canonical values through a distinct `VerifiedIngressProjection` type; the unverified projection type cannot be passed off as verified evidence.

## Threat model

An attacker, filesystem fault, partial migration, buggy maintenance command, or stale process may alter a redundant peer, logical path, timestamp, size, digest, or envelope version while leaving canonical bytes and their digest valid. Digest-only restart checks do not detect that split-brain state. A scheduler using the forged projection could route, deduplicate, claim, complete, or report the wrong object.

## Refactor boundary added

`src/persistence/canonical_projection_verifier.*` owns the projection comparison, safe field-only diagnostics, verified type, and migration-chain validation. `tests/persistence/canonical_projection_verifier_tests.cpp` exercises each field independently, NULL-vs-default semantics, multi-field contradictions, safe logging, and migration continuity.

This boundary is intentionally conservative and wire/on-disk neutral. It does not silently repair a row and it does not log peer/path values. The adjacent source-location inventory records every likely SQLite/canonical/claim/schema call site for integration review.

## Integration requirement

No persisted row should reach read, claim, completion, recovery, reconciliation, or operator projection code as an ambient struct. Each row decoder must reconstruct canonical metadata from durable envelope bytes, construct `PersistedIngressProjection` with explicit NULL handling and checked integer conversions, call `CanonicalProjectionVerifier::verify`, and hand downstream code only `VerifiedIngressProjection`. Contradictions should use the repository's immutable incident/quarantine mechanism.

## Residual risk

This standalone boundary does not by itself prove that all existing call sites use it. The source-location TSV is the checklist. The strongest next step is to make the existing persisted-row constructor private and require a verified factory, then add a structural test that fails on direct `sqlite3_column_*` use outside the persistence decoder.

## Adjacent conversion defect corrected

`SqliteProjectionDecoder` centralizes storage-class, NULL, signedness, range, digest-length, and column-index handling. In particular it refuses SQLite's coercion of text to integer and rejects negative values before conversion to unsigned sizes/versions. This prevents a malformed row from becoming a plausible C++ projection before canonical comparison.
