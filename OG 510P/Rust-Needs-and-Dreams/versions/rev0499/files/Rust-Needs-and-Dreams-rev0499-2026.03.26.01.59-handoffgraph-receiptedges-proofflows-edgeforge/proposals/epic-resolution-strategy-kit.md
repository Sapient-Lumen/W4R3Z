# Epic proposal: Resolution Strategy Kit

## Why this could matter
Rust is crossing a threshold where dependency resolution is no longer one silent, obvious choice.
MSRV-aware resolution is now part of normal Cargo posture, direct-minimal validation remains important for lower-bound honesty, publish-time-aware exploration is emerging, and future resolution extensions are explicitly on Cargo’s radar.

That means a worthy ecosystem contribution is no longer just “better resolver diagnostics”.
It is a **reviewable strategy layer** that tells maintainers and downstream tools:
- what kind of resolution was intended,
- what alternatives mattered,
- what tradeoffs were accepted,
- and what later consumers may reuse.

## Deliverables
1. A reference CLI: `cargo resolve-plan`
2. Stable machine-readable artifacts:
   - `resolution-objective/v0`
   - `resolution-candidate-report/v0`
   - `resolution-decision-report/v0`
   - `resolution-strategy-diff/v0`
   - `resolution-strategy-pack/v0`
3. Import adapters for:
   - `resolve-report/v0`
   - `feature-report/v0`
   - workspace/config posture
   - manifest-truth posture where relevant
4. Ranked pilots from [`design/resolution-strategy-pilot-program.md`](../design/resolution-strategy-pilot-program.md)
5. Explicit handoff guidance for Migration, Public API, Policy, Support, and Release consumers

## What makes it epic instead of merely nice
An epic contribution here would give Rust something unusually durable:
- lockfile review that preserves objective and tradeoff truth,
- multi-MSRV workspace strategy reports that stop living in tribal knowledge,
- a bounded way to compare latest / minimal / publish-time / MSRV-shaped outcomes,
- and a substrate that later Cargo-native work could plausibly import rather than replace.

## Non-goals
Do not make this:
- a solver fork,
- a universal dependency policy engine,
- a replacement for lockfiles,
- a cargo-vet clone,
- or a giant dashboard about “dependency health”.

The point is narrower and stronger:
**make resolution strategy reviewable.**
