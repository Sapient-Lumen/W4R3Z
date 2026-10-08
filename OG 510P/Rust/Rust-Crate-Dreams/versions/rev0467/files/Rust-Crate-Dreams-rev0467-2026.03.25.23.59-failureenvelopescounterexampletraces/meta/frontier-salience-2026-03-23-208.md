# Frontier salience 208 — dependency lifecycle now needs selection anchors and clean re-resolution honesty

## Main judgment

The next worthwhile deepening for **P-0535 Dependency Lifecycle Transition Kit** is no longer another dependency-policy dashboard.
It is a receiver-facing contract for **what currently anchors the claimed transition posture**, and what happens when that posture is tested by a clean re-resolve.

## Why this matters now

- the January 2026 safety-critical write-up still says teams often use crates early, then contain, fork, vendor, or replace them later as criticality rises;
- the January 2026 maintenance post makes dependency updates and keeping things working over time part of normal maintenance, not an edge case;
- Cargo still separates broad dependency intent in `Cargo.toml` from exact realized selections in `Cargo.lock`;
- Cargo explicitly allows `[patch]` to live in config or CLI for local-only testing, which means current behavior may not be shared team policy;
- source replacement still assumes the replacement is the same code, so a mirror/vendor route is not the same thing as fork progress;
- yanking still blocks future default selection without invalidating existing lockfiles;
- `rust-version` still influences `cargo add` and resolver choice, so selection can move when toolchain-floor context moves.

## What the sharper crate should provide

A stronger **P-0535** should now publish:

- `selection-anchor.receipt.json`
- `reresolution-risk.report.json`
- bundle inventory that keeps override authority, current anchor, and clean-resolve risk separate
- doctor rules that reject fake “the transition is durable because today’s lockfile is green” stories

## Boundary reminder

This is still **not** a generic update-policy crate, a vendoring-proof crate, or an off-ramp recommender.
It is the lifecycle-layer artifact that lets another team review:

- what currently keeps the dependency route stable,
- whether that route is shared or local-only,
- what would change if the lockfile were regenerated,
- and when human review is required.
