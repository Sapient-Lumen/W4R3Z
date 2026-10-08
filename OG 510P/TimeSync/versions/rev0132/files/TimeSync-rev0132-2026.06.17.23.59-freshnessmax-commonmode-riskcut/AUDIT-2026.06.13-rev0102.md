# TimeSync rev0102 audit — policy-equivalence temporal fixture refactor

## Focus

rev0102 continues FT-0090 by targeting a concrete profile-compatibility stale/future-evidence seam rather than adding registry or doctrine surface.

The risky pattern was a compatibility statement that claims to cover replay-transparency policy equivalence while the lifecycle-equivalence evidence inside the statement is evaluated after the statement signature, or while its revocation/drift checks occur after the equivalence evaluation that consumes them.

## What changed

- Added `tools/policy_equivalence_temporal.py`.
- Wired that helper into `check_profile_compatibility_statement` through `check_policy_lifecycle_equivalence`.
- Moved policy lifecycle equivalence interval/window checks out of `tools/validate_archive.py`.
- Added checks for:
  - `policy_lifecycle_equivalence.revocation_check.checked_at <= policy_lifecycle_equivalence.evaluated_at`
  - `policy_lifecycle_equivalence.drift_check.checked_at <= policy_lifecycle_equivalence.evaluated_at`
  - `policy_lifecycle_equivalence.evaluated_at <= compatibility_statement.binding.signed_at`
  - `policy_lifecycle_equivalence.evaluated_at <= compatibility_statement.expires_at`
- Added three derivation-checked negative fixtures and semantic vectors `TV-N273` through `TV-N275`.

## Positive fixture correction

`profiles/compatibility/p3-replay-transparency-policy-equivalence.json` previously had:

```text
binding.signed_at = 2026-05-22T19:45:05Z
policy_lifecycle_equivalence.evaluated_at = 2026-05-22T19:45:10Z
```

That meant the statement signature predated material it claimed to bind. rev0102 moves the signature to `2026-05-22T19:45:15Z` and normalizes copied negative fixtures that inherited the same incidental timestamp flaw.

## Waste/refactor note

The new helper is small and executable. It replaces inline parse/order logic in the monolithic validator and adds a self-test. The rendered negative JSON fixtures remain for audit review, but all three new negatives are derivation-checked from the positive compatibility fixture.

Generated `__pycache__` directories are removed before packaging rev0102. They are not semantic material and were cloudtainer/archive noise.

## Boundary retained

Policy equivalence and compatibility statements still do not become TimeState freshness, profile evidence, actionability evidence, or transport security evidence. rev0102 only enforces artifact-time coherence for policy-equivalence evidence that a compatibility statement already claims to cover.

## Remaining risk

FT-0090 remains open. The remaining work is mostly maintainability: continue extracting validator concern families only where code gets smaller, testable, or harder to misuse, and keep converting bulky fixture families to patch-derived rendered examples when that prevents real drift.
