# Frontier salience scan — 2026-03-16 (release-surface truth)

This pass again avoided adding another top-level proposal.
The stronger move was to sharpen two already-worthy crates whose value became more concrete after recent official Rust/Cargo signals:

- **P-0244 SemVer API Diff Evidence Kit**
- **P-0431 Public Dependency Boundary Kit**

## Main judgment

The repo’s next strong move was not “more public API tooling” in the abstract.
It was to sharpen the **foundation** underneath a future fearless publish workflow.

Three current signals matter most:

1. Cargo semver checking is still on an explicit path toward the `cargo publish` workflow.
2. The current plan for many hard type-shape semver cases is witness-program generation plus `cargo check`.
3. Public/private dependencies are now both an active MVP stabilization goal and a named 2026 flagship milestone.

Together, those make **release-surface truth** feel much sharper than another general release dashboard.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0489 Cargo Build-Dir Consumer Transition Kit**
3. **P-0244 SemVer API Diff Evidence Kit**
4. **P-0431 Public Dependency Boundary Kit**
5. **P-0496 Cargo Vendor & Source Parity Kit**
6. **P-0435 Cargo Script Workbench Kit**
7. **P-0484 Toolchain & Target Support Contract Kit**
8. **P-0483 Public API Readiness Bundle Kit**
9. **P-0472 Docs.rs Build Parity & Evidence Kit**
10. **P-0486 Debuggability Support Contract Kit**
11. **P-0036 MSRV Workspace Lab**
12. **P-0506 Cargo Workspace Boundary Doctor Kit**

## Why P-0244 rose now

The earlier version of this proposal was too easy to read as “stable API diff IR”.
That is not wrong, but it is no longer sharp enough.

The more interesting missing value is a **witness-aware SemVer evidence bundle** that can survive:
- multi-version rustdoc JSON,
- path/git/registry source identities,
- rule-based versus witness-based judgments,
- and publish-facing review.

That is newly timely because official Rust work now openly describes witness generation as the path through hard type-related semver checks.

## Why P-0431 rose now

Public/private dependencies are no longer just an old RFC-shaped aspiration.
They now have:
- a current MVP stabilization goal,
- unstable Cargo UX and manifest support,
- compiler-lint relevance,
- and a 2026 flagship tie to supply-chain/public-API control.

That makes the missing value much more concrete:
- a **boundary receipt**,
- a **reason taxonomy**,
- and a **migration plan** that stays honest about workspace limitations.

## Why this pass did not widen P-0483 instead

The archive already has a good “joined release-review bundle” idea in **P-0483**.
But broadening that further before the lower layers are sharper would make the repo more hand-wavy, not less.

The better move was to strengthen:
- the SemVer evidence substrate,
- the public dependency boundary substrate,
- and the lane note that keeps them separate from the higher-level readiness bundle.

## Working rule for the next few passes

Prefer upgrades that add:
- witness-plan / witness-result contracts,
- public-dependency reason taxonomies,
- compact scenario packs,
- and explicit import boundaries between low-level evidence crates and higher-level release bundles.

The repo is large enough now that **artifact sharpness beats proposal count** surprisingly often.

## Sources

- Continue resolving `cargo-semver-checks` blockers for merging into cargo: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Google Summer of Code 2025 results: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Stabilize public/private dependencies: https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
- Cargo unstable docs (`public-dependency`): https://doc.rust-lang.org/cargo/reference/unstable.html#public-dependency
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
