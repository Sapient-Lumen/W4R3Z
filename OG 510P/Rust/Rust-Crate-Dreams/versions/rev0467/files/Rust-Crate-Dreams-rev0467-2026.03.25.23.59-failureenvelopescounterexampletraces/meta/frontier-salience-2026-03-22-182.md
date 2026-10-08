# Frontier salience — 2026-03-22 (182)

This pass did **not** open another stewardship-scoring or funding lane.
It deepened **P-0011 Crate Health Contract Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0011 Crate Health Contract Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0532 Async Runtime Assurance Profile Kit**
8. **P-0469 Cargo Rebuild Explanation Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0431 Public Dependency Boundary Kit**

## Why P-0011 was the right lane to deepen now

Fresh official Rust and ecosystem signals make the missing value here more specific than “improve crate status metadata”:

- the January 2026 maintenance post frames maintenance as broad, ongoing work rather than a simple release activity;
- the 2025 State of Rust survey shows concern around developer and maintainer support while still treating docs as canonical;
- the January 2026 crates.io update adds Security-tab visibility, Trusted Publishing Only Mode, SLOC, and `pubtime`, giving us more **importable context** without solving support-routing truth;
- GitHub’s docs keep CODEOWNERS focused on review routing and private vulnerability reporting focused on confidential vulnerability intake, which are valuable substrate but not a full stewardship contract;
- and the Rust Foundation strategic plan elevates **Sustainable Maintenance** into a core pillar.

That combination makes the missing crate less “another maintenance score” and more a **reviewable stewardship-routing and continuity contract**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. **imported stewardship-signal truth**,
2. **routing drift truth**,
3. **portable health-support bundles**,
4. **continuity posture across ownership/repository changes**,
5. and **manual-review honesty where host substrate stops**.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0011**, **P-0017**, **P-0509**, and **P-0515**.

Especially resist:

- another maintainer leaderboard,
- another donation or sponsor dashboard,
- another popularity-plus-trust score,
- or another “maintenance badge” wrapper that does not actually export reviewable routing and continuity receipts.
