# ADR-0091: Product-profile default vocabulary boundary

- Status: Accepted
- Date: 2026-03-08

## Context

Risk 47 asked a narrow but expensive question:
what is the minimal stable vocabulary of defaults we encode in `product.profiles`
without turning product profiles into a second policy language?

The archive already had strong A/B/C/D posture decisions and a substantial
`tools/check_product_profiles.py` guardrail, but one important boundary was still soft:
`spec/product.profile.schema.json` allowed arbitrary keys under `defaults`.

That left two bad drift paths open:

1. new profile knobs could appear ad hoc without an explicit archive-level decision,
2. `product.profiles` could slowly absorb structured policy that belongs in dedicated specs.

## Decision

1. `product.profiles.defaults` stays a **flat, symbolic, compilation-target vocabulary**.

2. The allowed default keys are explicitly enumerated in `spec/product.profile.schema.json`.
   Arbitrary new keys are not allowed.

3. Default values stay **symbolic strings**, not nested policy objects.
   If a lane needs structured policy, it gets its own schema and the profile default only
   selects the posture/default lane.

4. The canonical default-key registry is documented in
   `docs/501-product-profile-default-vocabulary-boundary.md` and mechanically checked.

5. Adding, renaming, or removing a default key is an archive-level decision.
   It requires:
   - an ADR,
   - a schema update,
   - registry-doc wiring,
   - and guardrail updates.

6. Hard constraints remain in `required_invariants` and the dedicated per-lane docs,
   not in bespoke new default keys.

## Consequences

- A/B/C/D stay a real compilation target instead of a prose promise.
- Reviewers can distinguish stable product-shape knobs from full policy objects.
- New profile defaults become intentionally expensive enough to avoid casual sprawl.
- The archive keeps one profile vocabulary shared across all product shapes without forks.

## Why this is narrow enough

This ADR does not redesign any specific posture lane.
It only fixes the boundary around the **shape of the profile artifact itself**:

- flat symbolic defaults,
- explicit allowlist,
- dedicated schemas for structured policy,
- and one registry/check path for anti-drift.
