# Cargo resolver explanation — exactness + MSRV boundaries (2026-03-08)

Purpose: keep **P-0468 Cargo Resolver Explanation Kit** focused on the part of the problem that is still genuinely missing.

## Main judgment

The next worthwhile work on P-0468 is **not** another graph API or another Cargo wrapper.
It is a support artifact that freezes:

1. **selection scope**,
2. **resolver/MSRV policy**,
3. **evidence sources**, and
4. **exactness boundaries**.

That sharper boundary is justified by four current facts:

- Cargo’s resolver docs now make MSRV-aware version preference and mixed-workspace heuristics explicit.
- Cargo’s resolver docs also make the two-pass feature story explicit: Cargo resolves the lockfile graph as if all workspace features are enabled, then resolves actual compile-time features again for the selected build.
- `cargo tree` is useful but explicitly only “pretty close” to what Cargo will build and does **not** guarantee exact equivalence.
- The Cargo plumbing goal says `cargo metadata` can include dependency resolution but excludes feature resolution, while `--unit-graph` remains unstable and its tracking issue still carries unresolved design questions.

So the missing crate layer is the **why-bundle with boundary metadata**, not another promise of perfect solver truth.

## Why MSRV belongs inside the receipt

Cargo’s resolver docs now make mixed-MSRV behavior concrete enough that it should be a first-class field in the bundle, not a troubleshooting footnote.

Important consequences:

- a chosen version can be lower than one member needs because another member’s `rust-version` pulled it down,
- or a chosen version can still be higher than one member’s MSRV because version unification forced one compromise,
- so a usable receipt needs to say whether a version choice reflects a hard requirement, a lockfile carry-forward, or a heuristic “good enough” workspace compromise.

That is why `resolve-why.lock` should pin `resolver.incompatible-rust-versions` and why `version-choices.json` should treat MSRV influence as first-class.

## Why manual-review boundaries belong inside the receipt

A resolver explanation bundle should be allowed to say:

- “observed in `cargo tree`,”
- “consistent with `cargo metadata`,”
- “strengthened by `--unit-graph`,”
- or “manual review required.”

That is not weakness.
That is the missing professionalism layer.

A good support artifact is one that stays useful **without** claiming certainty Cargo itself has not stabilized.

## Concrete scenario pressure

Two current scenario families are especially important:

### 1. Mixed-MSRV workspace version choice

Cargo documents that mixed-Rust-version workspaces can produce lower-than-necessary or higher-than-desired shared versions because the resolver is searching for one “good enough” unified answer.

That means P-0468 should not just say “selected `clap 4.0.32`.”
It should say whether that choice was influenced by:
- lockfile carry-forward,
- resolver version,
- `resolver.incompatible-rust-versions`,
- or mixed-workspace MSRV pressure.

### 2. Workspace selection masks missing features

Real issue reports show that `cargo check --workspace` or similarly broad selections can hide missing per-member feature declarations that only fail when one member is built on its own.

That means the bundle must freeze:
- selected members,
- selected targets,
- whether the explanation is for a workspace-wide or package-specific command,
- and whether the resulting explanation is exact, approximate, or selection-sensitive.

## Recommended archive stance

For the next few passes, prefer:

- `resolve-why.lock` schema work,
- small MSRV and selection-sensitive scenario bundles,
- clearer manual-review vocabulary,
- and proposal-file upgrades for **P-0468**.

Avoid drifting into:

- another generic graph-query crate,
- another full build doctor,
- or an overconfident “Cargo truth extractor” that claims more exactness than the current surfaces justify.

## Sources

- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- Cargo unstable features (`--unit-graph`, `resolver.feature-unification`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Tracking issue for `--unit-graph`: https://github.com/rust-lang/cargo/issues/8002
- Tracking issue for workspace feature-unification: https://github.com/rust-lang/cargo/issues/14774
- Cargo issue on workspace selection masking too-few features: https://github.com/rust-lang/cargo/issues/14021
