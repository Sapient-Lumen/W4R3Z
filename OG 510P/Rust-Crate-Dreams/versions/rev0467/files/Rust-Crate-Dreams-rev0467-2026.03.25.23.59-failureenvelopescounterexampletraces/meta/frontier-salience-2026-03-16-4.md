# Frontier salience scan — 2026-03-16 (support-surface truth refresh)

This pass again avoided adding another top-level proposal.
The stronger move was to deepen two already-worthy cross-cutting crates with fresher official signals and more implementation-shaped fixture packs:

- **P-0484 Toolchain & Target Support Contract Kit**
- **P-0472 Docs.rs Build Parity & Evidence Kit**

## Main judgment

The Rust ecosystem still looks likelier to benefit from **coordination artifacts above real substrate** than from another clever leaf library.
In this pass, the clearest underbuilt frontier is **support-surface truth**:

- what a project claims to support,
- what rustup and docs.rs actually made visible,
- what drifted,
- and which support lane a failure belongs to.

Three current signals especially matter:

1. docs.rs changed its default targets in October 2025, so leaving docs posture implicit can now change what users see without any local source change,
2. the current docs.rs builds page now spells out concrete runtime facts like nightly version, cross-compilation behavior, the `docsrs` / `DOCS_RS` split, and hard sandbox limits,
3. rustup 1.29 expanded official host support and made environment/tooling behavior a little more plural, which makes project support claims less likely to fit in one hidden “works on my machine” assumption.

Together, those make **support contracts** and **docs parity issue bundles** look more urgent than another new protocol-specific idea this week.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0489 Cargo Build-Dir Consumer Transition Kit**
3. **P-0484 Toolchain & Target Support Contract Kit**
4. **P-0472 Docs.rs Build Parity & Evidence Kit**
5. **P-0486 Debuggability Support Contract Kit**
6. **P-0242 Reproducible Build Evidence Kit**
7. **P-0036 MSRV Workspace Lab**
8. **P-0506 Cargo Workspace Boundary Doctor Kit**
9. **P-0465 BorrowSanitizer Workflow & Evidence Kit**
10. **P-0256 Evidence Bundle Core Kit**
11. **P-0458 Async Dyn Transition Kit**
12. **P-0435 Cargo Script Workbench Kit**

## Why P-0484 rose now

The docs.rs target change made support drift less theoretical.
A crate that left its docs surface implicit could now be publishing a different Apple/Linux target posture than before.
At the same time, rustup’s override rules, profile rules, and path-toolchain caveats make it obvious that “we have a `rust-toolchain.toml`” is not the same as “our support contract is legible.”

That makes a crate which emits **toolchain intent snapshots, environment receipts, support-surface reports, and drift diffs** feel increasingly concrete.

## Why P-0472 rose now

The docs.rs builds page now gives a sharper boundary than older folklore:

- all non-`x86_64-unknown-linux-gnu` targets are cross-compiled,
- `#[cfg(docsrs)]` only applies to the final rustdoc invocation,
- `DOCS_RS` is the build-script lane,
- and the published limits include 6.44 GB RAM, 15 minutes of rustdoc time, 102.4 kB of build log, blocked network, and a maximum of 10 build targets.

That means the crate can stop being vague “docs preflight” talk and become a real **parity receipt / issue-bundle** plan.

## Why this pass did not add another proposal

The archive already has enough proposal count.
The missing value here was **handoff quality**:

- better lane boundaries,
- fixture-shaped artifact contracts,
- and stronger distinctions between project support promises and hosted docs behavior.

## Working rule for the next few passes

Prefer upgrades that add:

- support-lane boundary notes,
- scenario packs tied to named docs.rs / rustup behaviors,
- explicit drift vocabularies,
- and sharper “what this artifact is for” language.

The archive is big enough now that **proposal clarity beats proposal count** surprisingly often.

## Sources

- rustup 1.29: https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- docs.rs builds: https://docs.rs/about/builds
- docs.rs metadata: https://docs.rs/about/metadata
- docs.rs target changes: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
