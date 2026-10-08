# Scenario — Tokio internal use, runtime-neutral public API

This scenario exists to force **P-0510** to keep separate:

- internal Tokio use,
- public runtime-neutral claims,
- exported interop surfaces (`Future`, `Stream`, `http`, `tower-service`, etc.),
- and manual-review zones where runtime leakage is ambiguous.

## Why it matters

A crate may legitimately use Tokio internally while still presenting a public API that is mostly runtime-neutral.
A capability contract that only looks at dependencies will overstate lock-in.
A contract that only trusts maintainer prose will understate it.

## Expected artifact pressure

- `claim-class.policy.json` should mark the public runtime-neutral claim as `observed` only if the public API surface supports it.
- `support-obligation.receipt.json` should still record internal runtime coupling or feature-gated runtime obligations when they materially affect adoption.
- `profile-fidelity.report.json` should allow `mostly_observed` when public neutrality is clear but optional adapters or examples still need manual review.
