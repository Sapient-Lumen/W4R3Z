
# MSRV artifact completeness plan — 2026-03-22

This note deepens **P-0036 MSRV Workspace Lab** around one product question:

> when a workspace says “our MSRV is X”, what exact artifacts should another engineer receive so mixed member promises, command-family floors, and lockfile-authoring truth stay reviewable instead of compressed into one number?

## Product stance

The crate should stay reviewer-facing, read-first, and conservative.
It should not become:

- a generic binary-search MSRV finder,
- a workspace manager,
- a huge CI matrix generator,
- or a policy-free “try old toolchains until green” helper.

Its job is to emit a compact pack that answers:

- what each member or lane actually promises,
- whether the intended resolver/MSRV policy activated,
- which command families hold at the policy floor,
- whether lockfile authoring needs a newer floor,
- how support promises changed across revisions,
- and what still needs manual review.

## New first-class artifacts

### `effective-workspace-promise.manifest.json`

Normalize workspace support promises after inheritance and policy splitting.

For each workspace bundle, record:

- workspace identifier,
- default promise class,
- per-member promise class (`public_library`, `published_cli`, `examples_and_docs`, `internal_tooling`, `manual_review_required`, ...),
- declared floor and optional effective floor,
- command families required for that member,
- lockfile support class (`pinned_build_only`, `authoring_supported`, `manual_review_required`),
- activation references and notes.

This keeps “library supports 1.70” separate from “workspace tooling also supports 1.70”.

### `policy-split-diff.report.json`

Compare two MSRV bundle states without flattening them into one raised/lowered number.

For each changed member, record:

- old/new floor,
- old/new promise class,
- affected command families,
- whether the change is `split_introduced`, `member_floor_raised`, `authoring_floor_raised_only`, `support_scope_reduced`, or `manual_review_required`,
- review notes.

This keeps “the CLI moved” separate from “the public library moved”.

### `msrv-support-bundle.manifest.json`

The portable thing another reviewer opens first.

For one exported pack, record:

- workspace identifier,
- included members / lanes,
- required artifacts,
- optional artifacts,
- manual-review gaps,
- share posture.

This bundle should join declared policy, policy activation, selected observations, command-family summaries, lockfile-floor receipts, and split-diff artifacts without pretending they mean the same thing.

## Receiver-facing workflow

### `inspect`
Capture policy activation and normalized workspace promises before expensive probing.

### `summarize`
Produce effective workspace promises plus command-family floor summaries.

### `diff`
Show whether a revision changed only authoring floor, one member’s promise, the default workspace promise, or policy activation itself.

### `pack`
Emit one `msrv-support-bundle.manifest.json` plus the underlying receipts and reports.

## Good first scenario families

1. **Virtual workspace expects fallback but never activates it at the root.**
2. **Public library stays on an older floor while CLI/examples move higher.**
3. **`cargo build` stays green while `cargo metadata` needs a newer floor because of an inactive target edge.**
4. **Lockfile update/generation moves upward while pinned-lockfile builds remain supported.**
5. **A release changes only one member promise, and the diff should say so explicitly.**

## Boundary reminders

Keep **P-0036** separate from:

- general dependency-lifecycle placement work (**P-0535**),
- target/toolchain support posture (**P-0484**),
- generic resolver explanation (**P-0468**),
- and Cargo update policy or off-ramp work.

The missing value here is the **joined MSRV support artifact** above Cargo policy surfaces and below a broader release/governance system.

## Sources

- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
- https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
- https://doc.rust-lang.org/cargo/reference/workspaces.html
- https://doc.rust-lang.org/cargo/CHANGELOG.html
- https://doc.rust-lang.org/beta/releases.html
- https://github.com/rust-lang/cargo/issues/16597
- https://github.com/rust-lang/cargo/issues/14414
- https://github.com/foresterre/cargo-msrv/blob/main/CHANGELOG.md
- https://github.com/foresterre/cargo-msrv
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
