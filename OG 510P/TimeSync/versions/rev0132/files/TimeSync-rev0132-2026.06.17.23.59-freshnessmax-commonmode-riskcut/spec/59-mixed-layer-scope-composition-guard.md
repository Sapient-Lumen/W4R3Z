# 59 — Mixed-layer scope composition guard

rev0088 closes the mixed-layer portability frontier by adding an explicit guard object for surfaces that are safe in isolation but unsafe when composed across scope boundaries.

The guard covers profile-compatibility drift, discovery semantic-version downgrade, digest binding, aggregate correction-authority lifecycle, aggregate lifecycle rollups, transparency trust-policy lifecycle, replay-transparency policy equivalence, and external transparency receipts.

The guard is not a new source of timing evidence. It cannot update TimeState, profile conformance, profile assessment, current actionability, individual replay visibility, aggregate lifecycle suppression, or TimeSync provenance. It records whether composed metadata remains current-use guarded, historical-only, metadata-only, suppressed, or fail-closed.

## Required behavior

A mixed-layer portability review must include decisions for these surfaces:

```text
profile_compatibility_drift
discovery_version_negotiation
discovery_digest_binding
aggregate_correction_authority_lifecycle
aggregate_lifecycle_rollup
transparency_trust_policy_lifecycle
```

Each surface declares its interpretation scope and whether current use is allowed. A current guard cannot be produced when any composed surface is non-current, suppressed, historical-only, or unknown. A valid discovery downgrade proof cannot bypass aggregate lifecycle suppression. A current lifecycle rollup cannot bypass weaker or unknown profile drift. Transparency policy equivalence cannot reopen profile assessment.

## Digest binding

The guard carries `guard_digest` with `binds = scope_composition_guard`. Mixed-layer review also carries `matrix_digest` with `binds = scope_composition_decision_matrix`.

## Boundary

The guard may constrain interpretation of metadata. It may not export raw surface material, profile-rule deltas, authority registries, verifier rosters, lifecycle incident material, notification recipient details, or external provenance graphs.
