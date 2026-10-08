# Audit/refactor — profile compatibility drift and rendered profile consistency

## Audit result

The rev0086 profile catalog and profile Markdown renderings had diverged in one human-facing place: the catalog included `portable_digest_binding_policy_summary` in every forbidden evidence-class set, but the rendered profile files did not show it.

## Refactor

The validator now separates profile compatibility checks into:

```text
check_profile_compatibility_drift_matrix(...)
check_profile_compatibility_drift_decision(...)
check_downgrade_proof_metadata(...)
check_profile_markdown_digests(...)
```

The last helper now checks rendered forbidden evidence classes, not only digest presence.

## Negative cases added

- weaker drift treated as current
- unknown drift treated as current
- digest rollover without equivalence treated as current
- named drift/portability workflow without a drift decision
- current downgraded result without proof
- current downgraded result with weaker semantics
- negotiation policy allowing weaker downgrade current use
