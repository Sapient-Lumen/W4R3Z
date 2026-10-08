# Audit — rev0112 profile drift equivalence refactor

rev0112 continues FT-0090 with executable validation work only. The six-field TimeState core is unchanged.

## What was risky

Profile compatibility drift decisions are used to decide whether a digest-distinct related profile can be reused for current compatibility workflows. rev0111 already checked obvious weaker/unknown drift, but it still allowed a sharper bypass:

```text
current_use_allowed = true
drift_class = stricter_or_equal
digest_relation = different_digest_without_equivalence
```

or a current digest-distinct decision that simply omitted `compatibility_statement_digest`. In both cases the decision looked like a compatibility gate but did not prove the digest-distinct equivalence it relied on.

Digest rollover had a similar incompleteness path: a current digest-rollover-compatible decision could claim equivalence without carrying bound prior/current profile digests or a successor compatibility statement digest.

## What changed

New helper:

```text
tools/profile_drift_semantics.py
```

The helper now owns profile compatibility drift matrix and decision semantic checks. It rejects:

```text
current decisions with different_digest_without_equivalence
current decisions with unknown_or_redacted digest relation
current different_digest_with_equivalence decisions without compatibility_statement_digest binding profile_compatibility_statement
current digest-rollover-compatible decisions without prior/current profile digests binding normative_profile_rules
current digest-rollover-compatible decisions without successor_compatibility_statement_digest binding profile_compatibility_statement
```

## Refactor result

`tools/validate_archive.py` no longer owns the profile-drift matrix/decision logic inline. The validator delegates to `tools/profile_drift_semantics.py`, reducing the monolith and making the drift gate self-testable.

## New regression coverage

```text
examples/negative/profile-compatibility-drift-current-missing-compat-digest-invalid.json
examples/negative/profile-compatibility-drift-current-without-digest-equivalence-invalid.json
examples/negative/profile-compatibility-drift-rollover-missing-bound-digests-invalid.json
```

These are derivation-checked through `tests/fixture-derivations.yaml` and covered by semantic vectors `TV-N305` through `TV-N307`.

## Boundary

rev0112 does not introduce a profile authority registry, credential system, proof exchange, compatibility repository, or profile publication workflow. It only requires existing compact current-use drift claims to bind the equivalence/digest material they already semantically depend on.
