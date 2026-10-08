# 44 — Aggregate publication cadence and privacy controls

rev0081 closes FT-0080 by adding a compact privacy-control surface to detached aggregate verifier audit summaries.

## Problem

rev0080 allowed aggregate summaries to suppress small compromise-era and recovery-audit subsets. That was not enough for repeated publication.

Repeated aggregate releases can leak suppressed cohorts through comparison across periods. Cross-operator rollups can also weaken privacy if one operator uses lower suppression thresholds than another. Noisy counts can help, but only if the noise claim is bound to external policy and is not used to bypass a minimum group-size rule.

## Placement

`aggregate_summary.aggregate_privacy_controls` is required for `aggregate_verifier_audit_summary` records.

It has three sub-surfaces:

1. `publication_cadence` — describes publication sequence and whether a prior publication can be differenced against the current one.
2. `suppression_threshold_equivalence` — describes whether the declared minimum group-size rule is local or digest-bound across compatible operators.
3. `statistical_noise` — describes whether counts are exact, thresholded, suppressed, or policy-bound noisy counts.

This surface is aggregate-only. It is not profile evidence, individual replay evidence, verifier authorization, actionability evidence, or provenance.

## Publication cadence

`publication_cadence` records the cadence, sequence number, previous-publication digest when applicable, relation to the previous window, and differencing-risk posture.

Rules:

- Publication sequence numbers after the first publication require a previous-publication digest.
- Previous-publication digests bind `aggregate_verifier_audit_summary`.
- Exact adjacent reporting windows are rejected.
- Unbounded or unknown differencing risk is rejected.
- Publication cadence may constrain only aggregate replay-review posture.
- It cannot update profile assessments.

## Suppression-threshold equivalence

`suppression_threshold_equivalence` records the threshold basis and whether cross-operator thresholds are digest-bound equivalent-or-stricter.

Rules:

- The aggregate privacy-control minimum group size cannot be weaker than `privacy_boundary.minimum_group_size`.
- Compatible-operator aggregate cohorts require digest-bound equivalent-or-stricter suppression-threshold equivalence.
- Weaker or unknown threshold equivalence is rejected.
- A compatibility digest can be referenced, but the compatibility statement material is not exported through the aggregate summary.

## Statistical noise

`statistical_noise` records only count semantics and policy binding.

Rules:

- `noisy_count` requires `noise_status: applied_policy_bound` and a digest that binds `aggregate_privacy_policy_rules`.
- Privacy-budget material is not exported.
- Noise parameters are not exported.
- Statistical noise cannot be used to de-suppress a group below the declared minimum group size.
- TimeSync does not define the noise mechanism, privacy accounting, or privacy-loss composition model.

## Non-provenance boundary

Aggregate privacy controls cannot export:

- verifier rosters or identities,
- challenge-result identifiers,
- exact adjacent release windows,
- cross-publication reconstruction material,
- privacy-budget internals,
- noise parameters,
- policy language,
- legal-authority details,
- external transparency/provenance semantics.

## Refactor note

rev0081 also refactors repeated aggregate validator checks with shared helpers for boolean non-leakage/non-upgrade boundaries and non-negative aggregate count normalization. This is not a semantic expansion; it reduces copy-paste drift between compromise-era suppression, recovery-audit rollups, and the new aggregate privacy-control surface.
