# Design note: Manifest Surface lane map

## Goal
Make it impossible to blur **what was authored**, **what was inherited or defaulted**, **what got packaged**, **what single-file/script lanes imply**, and **what named consumers actually imported** into one fake sentence like “the manifest says …”.

A Cargo manifest is not one lane.
It is at least a family of related lanes that often start from the same text but diverge materially in meaning, authority, and downstream use.

## Why this lane map is needed now
- Cargo 1.94 still treats workspace/config discovery as active design space, and explicitly calls out broken parent `Cargo.toml` / `.cargo/config.toml` files as a real user problem.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- `cargo package` still rewrites and normalizes `Cargo.toml`, removes `[patch]`, `[replace]`, and `[workspace]`, always includes `Cargo.lock` unless excluded, and emits `.cargo_vcs_info.json`.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo metadata` is still the stable machine-readable import lane, but its docs still recommend pinning `--format-version`, which is direct evidence that consumer lanes must stay explicit.
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- workspace inheritance now clearly spans `workspace.package`, `workspace.dependencies`, and `workspace.lints`, so authored package meaning can depend on a wider root context than the package-local file alone.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- single-file scripts are no longer speculative folklore: the cargo-script goal is active, RFCs 3502/3503 are approved, and nightly Cargo/rustc support exists.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html
  https://rust-lang.github.io/rfcs/3502-cargo-script.html
  https://rust-lang.github.io/rfcs/3503-frontmatter.html
- Rust 1.93 pulled out `cargo-util-schemas` as a crate, which is a useful signal that schema types are getting clearer while final semantic meaning still lives elsewhere.
  https://doc.rust-lang.org/beta/releases.html

## The lanes

### 1) Authored package-manifest lane
This is the ordinary `Cargo.toml` or embedded package-facing TOML that a maintainer wrote.

Questions it answers:
- which keys were explicitly present,
- which dependency declarations and features were written,
- which metadata fields were declared,
- which publish/install/build-facing intentions were recorded.

What must stay explicit:
- raw authored path,
- explicit field presence,
- package-vs-workspace subject identity,
- unstable syntax usage when present.

This lane is closest to “what the author meant”, but it is still not the whole story.

### 2) Inherited / defaulted / discovered-manifest lane
This is the lane where authored text is interpreted with Cargo’s discovery and inheritance rules.

Questions it answers:
- which workspace root or `package.workspace` attachment applied,
- which `workspace.package`, `workspace.dependencies`, or `workspace.lints` fields were inherited,
- which values were defaulted or inferred,
- which config/discovery context materially changed interpretation.

Design rule:
- this lane must attach Repo Composition / discovery context instead of pretending the package file alone was sufficient.

### 3) Packaged / publish-normalized lane
This is the `.crate`-facing manifest Cargo actually packages.

Questions it answers:
- what Cargo rewrote or normalized,
- which sections were removed,
- which files and lockfile posture shipped,
- what `.cargo_vcs_info.json` best-effort source hint was emitted.

Design rule:
- authored and packaged manifest truth must stay diffable, not merely implied.

### 4) Script / frontmatter subject lane
This is the lane for manifest-bearing `.rs` scripts and frontmatter-defined single-file packages.

Questions it answers:
- what the embedded subject identity was,
- which fields were explicit, defaulted, or disallowed,
- which package metadata Cargo inferred,
- which script-only constraints applied.

Design rule:
- single-file packages are another subject lane, not a separate universe and not ordinary package-root discovery.

### 5) Machine-consumer import lane
This is the lane for named machine-readable consumers like `cargo metadata`, package/release tooling, and other external-tool imports.

Questions it answers:
- which projection a named consumer imported,
- which fields were omitted or normalized,
- which compatibility/version contract governed that projection,
- which parts of manifest truth must be reattached from other packs instead of guessed.

Design rule:
- the consumer name and version contract must be explicit.

### 6) Human projection lane
This is the lane for named human-facing projections like `cargo info`, registry/docs pages, and review UIs.

Questions it answers:
- what a human-oriented consumer displayed,
- whether the source of truth was local, packaged, or registry-side,
- which fields are suppressed, summarized, or audience-shaped.

Design rule:
- a readable projection is not the authoritative manifest boundary.

### 7) Evolving schema / watch lane
This is the lane for manifest-native concepts that are real enough to track but not yet safe to flatten into stable universal semantics.

Examples:
- feature descriptions / visibility / deprecation,
- public/private dependency posture,
- future schema crates or JSON-schema exports,
- frontmatter or consumer support that is implemented but still moving.

Design rule:
- track active motion without pretending the ecosystem has already converged.

## What must never be collapsed
Do not collapse these into one fake manifest verdict:
- authored text vs inherited/defaulted meaning,
- inherited/defaulted meaning vs packaged `.crate` truth,
- ordinary package roots vs embedded script/frontmatter subjects,
- machine-readable imports vs human-readable projections,
- stable imported semantics vs watch-lane evolving metadata.

## What a worthy contribution looks like now
A worthy contribution here is **not** another manifest formatter, editor shell, registry page, or one more thin wrapper around `cargo metadata`.

It is a thin `cargo manifest` / `manifest-pack/v0` layer that:
- records the lane of every report,
- emits authored/inherited/packaged/consumer diffs explicitly,
- preserves consumer-lossiness instead of hiding it,
- and gives downstream publish, admission, support, migration, and docs consumers one portable manifest continuity substrate.

## Recommended first rollout order
1. authored package-manifest lane,
2. inherited/defaulted/discovered lane,
3. packaged/publish-normalized lane,
4. script/frontmatter lane,
5. machine-consumer import lane,
6. human projection lane,
7. evolving schema/watch lane.

This ordering keeps the archive focused on facts Cargo already exposes before it widens to more volatile UI and standards-adjacent consumers.
