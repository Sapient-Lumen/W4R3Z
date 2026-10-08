# Audit — rev0110 aggregate privacy digest refactor

rev0110 continues FT-0090 with executable validation work only. The six-field TimeState core is unchanged.

## What was risky

The aggregate privacy-control branch still allowed several compact metadata surfaces to look digest-bound without proving that the digest object bound the expected artifact class.

The highest-risk case was suppression-threshold equivalence. Cross-operator aggregate publication and profile-compatibility threshold basis both rely on external compatibility semantics. Before rev0110, a `compatibility_statement_digest` object could be present but bind another artifact class, or the threshold basis could claim `profile_compatibility_statement` while omitting the digest entirely.

A second concrete case was noisy aggregate counts. The validator already required a privacy-policy digest for `noisy_count`, but this revision makes the digest-class check live in the aggregate privacy helper with direct negative coverage.

## What changed

New helper:

```text
tools/aggregate_privacy_semantics.py
```

Moved out of `tools/validate_archive.py`:

```text
aggregate_privacy_controls checks
compromise_era_suppression checks
recovery_audit_rollup checks
```

New executable checks:

```text
threshold_basis = profile_compatibility_statement requires compatibility_statement_digest binding profile_compatibility_statement
compatible_operator_equivalence = digest_bound_equivalent_or_stricter requires compatibility_statement_digest binding profile_compatibility_statement
compatible_operator_cohort aggregation requires compatibility_statement_digest binding profile_compatibility_statement
noisy_count requires privacy_policy_digest binding aggregate_privacy_policy_rules
```

## New regression fixtures

```text
examples/negative/aggregate-threshold-compatibility-wrong-bind-invalid.json
examples/negative/aggregate-threshold-profile-basis-missing-compat-invalid.json
examples/negative/aggregate-noise-policy-wrong-bind-invalid.json
```

Each is derivation-checked from a positive fixture through `tests/fixture-derivations.yaml`.

## Boundary intentionally preserved

rev0110 does not add a privacy ledger, budget accounting, operator registry, compatibility authority workflow, or aggregate publication repository. The only added requirement is that existing compact digest fields bind the artifact class their semantics depend on.

## Remaining risk

FT-0090 remains open. The remaining high-value work is continued validator decomposition and selective fixture-family derivation where it prevents real copy drift.
