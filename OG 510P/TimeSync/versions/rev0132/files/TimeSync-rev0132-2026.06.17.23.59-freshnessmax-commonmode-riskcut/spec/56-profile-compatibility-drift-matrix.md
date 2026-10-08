# 56 — Profile compatibility drift matrix

rev0087 closes FT-0086 by making profile compatibility drift an explicit decision surface.

## Problem

Profile references can drift without a transport or byte-level failure. A receiver may see the same profile identifier with a different digest, a partner authority asserting stricter-or-equal rules, a digest rollover, a weaker policy relation, or an unknown newer surface returned through discovery negotiation. Treating all of these as "compatible" creates a fail-open path.

## Decision vocabulary

`compatibility_drift.drift_class` is one of:

```text
equivalent
stricter_or_equal
weaker
incomparable
unknown
digest_rollover_compatible
digest_rollover_without_equivalence
```

`compatibility_drift.compatibility_decision` is one of:

```text
current_use_allowed
current_use_guarded
metadata_only
historical_only
suppressed_by_weaker_profile
suppressed_by_unknown_drift
suppressed_by_incomparable_profile
suppressed_by_digest_rollover
suppressed_by_downgrade_without_proof
```

## Hard rules

- Equivalent digests may be current-use when the compatibility statement is still valid.
- Stricter-or-equal drift may be current-use only as `current_use_guarded` and only when digest-bound.
- Weaker, unknown, incomparable, or digest-rollover-without-equivalence drift cannot support current compatibility interpretation.
- Drift decisions update only compatibility interpretation. They do not update TimeState, profile conformance, actionability, evidence sufficiency, replay visibility, or TimeSync provenance.
- Profile-rule deltas, profile-authority registries, and raw policy text remain out of ordinary TimeSync export.

## Executable matrix

The source of truth for row semantics is:

```text
tests/profile-compatibility-drift-matrix.yaml
schema/profile-compatibility-drift-matrix.schema.json
schema/profile-compatibility-drift-decision.schema.json
```

The validator checks row completeness and verifies every embedded `compatibility_drift` decision in profile compatibility statements.
