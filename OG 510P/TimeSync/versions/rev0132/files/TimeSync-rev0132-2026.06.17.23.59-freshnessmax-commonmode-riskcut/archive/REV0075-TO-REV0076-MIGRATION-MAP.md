# Migration map — rev0075 to rev0076

## Summary

rev0076 makes transparency trust-policy lifecycle explicit.

## Producers

When emitting a `transparency_trust_policy_reference`, add `lifecycle_status` with:

- `state`,
- `evaluated_at`,
- `not_before`,
- `not_after`,
- `revocation_check`,
- `drift_status`,
- `lifecycle_boundary`.

If a policy digest has rolled over, include successor/current digest information and a compatibility-statement digest when replay visibility is still claimed as current.

## Compatibility statements

When a compatibility statement advertises `replay_transparency_policy_equivalence`, add `policy_lifecycle_equivalence` to `transparency_policy_equivalence`.

Current equivalence requires active subject and related policies, an in-window equivalence evaluation, checked-not-revoked status, and non-weakening drift.

## Consumers

A rev0075 trust-policy reference without `lifecycle_status` should be treated as lifecycle-unknown for current replay-visibility decisions. It may remain useful as historical replay-review metadata.
