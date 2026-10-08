# Gap: Lint profiles, baselines, and fix packs in Rust

## What is missing
Rust has many high-quality lint engines and some machine-applicable fix machinery, but it still lacks a **boring, reviewable policy/baseline/report boundary** across them.

Today teams can separately use:
- `rustc` lints,
- Clippy lint groups,
- rustdoc lints,
- Cargo manifest/workspace lint configuration,
- JSON diagnostics from the compiler,
- Cargo future-incompat reports,
- and machine-applicable fixes via `cargo fix` / `rustfix`.

What is still missing is the shared layer that answers:
- which lint profiles a project actually intends to enforce,
- how workspace inheritance and lint-group expansion are pinned,
- which existing findings are accepted as baseline debt,
- which newly introduced findings should fail CI,
- how suggested fixes should be packaged and reviewed,
- how Cargo-side warning/report lanes fit into the same governance story,
- and what release / CI / safety / migration tooling should consume.

## Why it matters
This is no longer just “run Clippy in CI”.

Rust’s 2026 flagships explicitly include establishing a spot for **safety-critical lints in Clippy**. That changes the expected rigor of lint policy from convenience to governance. At the same time, the lint surface is already broad and becoming more tool-facing:
- Cargo manifests now expose stable `[lints]` and `[workspace.lints]` configuration.
- Cargo is experimenting with `[lints.cargo]`, which means Cargo-native warning families are moving toward the same policy plane.
- Cargo 1.94 added the `cargo report` subcommand and moved future-incompat reporting under that report surface.
- `cargo fix` and `rustfix` prove there is real fixability value in the toolchain, but edition migrations and conditional builds still require multiple passes and careful review.
- Clippy’s current config-file docs still say `clippy.toml` is unstable and may be deprecated, which makes reviewable exported policy artifacts more valuable than hidden tool-local state.
- `rustc` already emits machine-readable JSON diagnostics.

The substrate is real; the policy/baseline/report layer is still missing.

## Existing building blocks worth composing
- Rust’s 2026 flagships include the Clippy safety-critical-lints milestone.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo supports package-level `[lints]` and workspace-level `[workspace.lints]` on stable Rust.
  https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo is experimenting with `[lints.cargo]` for Cargo-native lints.
  https://doc.rust-lang.org/cargo/reference/unstable.html#lintscargo
- Cargo 1.94 added the `cargo report` subcommand and renamed the old future-incompat reporting command; `cargo report` currently exposes future-incompat reports as a first-class report family.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- Clippy exposes named lint groups such as `all`, `pedantic`, `restriction`, `nursery`, and `cargo`.
  https://rust-lang.github.io/rust-clippy/stable/index.html
- rustc documents its built-in lint listings and lint levels.
  https://doc.rust-lang.org/rustc/lints/listing/index.html
  https://doc.rust-lang.org/rustc/lints/levels.html
- rustdoc documents its own lint space.
  https://doc.rust-lang.org/rustdoc/lints.html
- rustc has a stable JSON diagnostics format.
  https://doc.rust-lang.org/rustc/json.html
- `cargo fix` applies compiler / Clippy suggestions, and `rustfix` exposes the underlying code-fix machinery as a library.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  https://docs.rs/rustfix
- Cargo’s 1.90 development report explains why selective and interactive fixing remain awkward under the current `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The Edition Guide is explicit that `cargo fix` can only work with one configuration at a time and often needs multiple passes across targets or features.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html

## Why existing tools are not yet the whole answer
The ecosystem has **engines, manifests, reports, and suggestions**, but not one **stable lint-governance contract**. The next worthy contribution is therefore not another preset or CI wrapper, but a thin stack-level orchestration/evidence layer above the existing engines.

Today teams still have to invent their own answers for:
- canonical profile definitions,
- group expansion locking,
- inheritance review,
- debt baselining and expiry,
- diffing old vs new findings,
- multi-tool aggregation,
- Cargo-native report imports,
- and how to carry fix suggestions forward without auto-applying everything blindly.

The result is familiar from elsewhere in the archive: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “these are the lint profiles we enforce and where they came from,”
- “these existing findings are baseline debt and these are not,”
- “this PR introduced these new findings under these exact tool versions and group expansions,”
- “these fixes are machine-applicable and reviewable as a pack,”
- “these Cargo-side future-incompat findings were imported with these caveats,”
- and “this is the portable bundle CI, release tooling, migration tooling, and safety evidence tooling can consume.”

That is bigger than a config file and smaller than replacing Clippy or rustc.
