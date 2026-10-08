# Frontier salience scan — 2026-03-16 (resolver explanation made fixture-first)

This pass did not add a new top-level proposal.
Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** into a fixture-first, more implementation-shaped lane.

## Main judgment

The strongest missing crate here is still not a replacement resolver.
It is the **proof-carrying explanation layer** above Cargo’s resolver surfaces.

The official picture now makes that sharper than before:

- the PubGrub-in-Cargo goal explicitly requires **complete output** with enough associated information to determine the resolver made the right decision,
- resolver docs still describe a two-pass world (lockfile graph as-if all workspace features are enabled, then actual compile-time features),
- unstable docs now define `selected`, `workspace`, and `package` feature-unification policies,
- and `cargo tree` still says its output is only *pretty close* to the real build plan.

That means the missing contribution is a boring support layer with:

1. a capture lock,
2. reusable report schemas,
3. an exactness/evidence receipt,
4. and a fixture corpus covering the most confusing resolver-pressure scenarios.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0429 rustc_public Analysis Workbench Kit**
3. **P-0055 Cargo Workspace Toolchain Manifest Kit**
4. **P-0056 Cargo Install Policy & Cooldown Kit**
5. **P-0489 Cargo Build-Dir Consumer Transition Kit**
6. **P-0508 Cargo Build Script Delegation Kit**
7. **P-0244 SemVer API Diff Evidence Kit**
8. **P-0507 Cargo Fix Campaign Kit**
9. **P-0478 Cargo Future-Incompat Triage Kit**
10. **P-0484 Toolchain & Target Support Contract Kit**
11. **P-0477 Cargo Publish Receipt Join Kit**
12. **P-0480 Cargo Global Cache Policy & GC Receipt Kit**

## Why P-0468 rose again

Earlier archive work already knew that resolver explanation mattered.
What it still lacked was the "someone else could actually implement against this" layer.

The new fixture pack closes that gap by freezing:

- `resolve-why.lock`,
- version-choice / feature-cause / duplicate-build artifacts,
- participant / intent / origin / identity reports,
- and an exactness receipt that says whether a conclusion was observed directly, reconstructed conservatively, or still needs manual review.

That is meaningfully stronger than another round of prose about confusing features.

## What this pass did not do

It did **not** collapse:

- the resolver implementation itself,
- PubGrub integration,
- build-analysis history,
- workspace boundary diagnosis,
- and mixed-MSRV planning

into one fake “Cargo dependency crate”.

That restraint improved the archive.

## Sources

- PubGrub in Cargo goal: https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo unstable features (`resolver.feature-unification`): https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
