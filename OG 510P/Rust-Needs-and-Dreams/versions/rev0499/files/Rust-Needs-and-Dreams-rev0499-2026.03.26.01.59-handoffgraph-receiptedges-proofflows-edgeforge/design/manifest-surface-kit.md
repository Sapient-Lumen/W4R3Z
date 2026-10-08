# Design: Manifest Surface Kit (`cargo manifest`, `manifest-pack/v0`)

## Goal
Define a portable review layer for Rust manifests so that **authored manifest intent, publish-time rewriting, feature-surface metadata, and consumer-import truth** can be inspected and diffed without re-implementing Cargo behavior in every tool.

This should **not** replace `cargo metadata`, `cargo info`, `cargo package`, `cargo-edit`, `cargo-cargofmt`, workspace/config discovery, or cargo-script frontmatter.
It should give them a shared semantic boundary.

The lane rule for this kit is now explicit in [`design/manifest-surface-lane-map.md`](./manifest-surface-lane-map.md): authored package text, inherited/defaulted interpretation, packaged normalized truth, script/frontmatter subjects, machine-consumer imports, human projections, and evolving watch lanes must stay distinct.

## References (signals)
- Cargo 1.94 highlights TOML 1.1 transition issues, `cargo-cargofmt`, and workspace/config discovery as active concerns, which is strong evidence that manifest behavior remains a live ecosystem seam.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- `cargo package` rewrites and normalizes the manifest, removes `[patch]`, `[replace]`, and `[workspace]`, and includes `Cargo.lock` by default.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- RFC 3416 makes feature descriptions, visibility, and deprecation manifest-native concepts, and Cargo planning still tracks visibility/deprecation as follow-on work.
  https://rust-lang.github.io/rfcs/3416-feature-metadata.html
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo script/frontmatter RFCs explicitly allow embedded manifests with defaulted/inferred fields and special restrictions.
  https://rust-lang.github.io/rfcs/3502-cargo-script.html
  https://rust-lang.github.io/rfcs/3503-frontmatter.html
- Cargo’s external-tools docs say `cargo metadata` is the stable, versioned machine-readable interface, which makes it the right import lane rather than something to replace.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- `cargo info` is an official human-readable manifest/package consumer surface, which is useful prior art for the consumer-report side.
  https://doc.rust-lang.org/cargo/commands/cargo-info.html

## Stack boundaries
This kit should be treated as the authoring/rewriting/reporting layer inside a broader **Manifest Truth Stack**:
- [`design/manifest-surface-kit.md`](./manifest-surface-kit.md) owns authored/published/consumer manifest reports and `manifest-pack/v0`.
- [`design/manifest-surface-lane-map.md`](./manifest-surface-lane-map.md) owns the explicit lane split that prevents authored text, inherited meaning, packaged truth, script subjects, and consumer projections from collapsing into one fake manifest verdict.
- [`design/repo-composition-stack.md`](./repo-composition-stack.md) owns discovery roots, config layers, workspace inheritance, and package-selection scope.
- [`design/scriptkit.md`](./scriptkit.md) owns single-file execution posture and script-run receipts.
- [`design/dependency-control-stack.md`](./dependency-control-stack.md) owns chosen-graph / activation / selection-policy truth after resolution.
- [`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md) owns source/auth/publish-authority facts and downstream identity handoffs.

Design rule: **manifest truth starts before graph selection and ends before policy/install conclusions.**

## Lane discipline
Read this kit through [`design/manifest-surface-lane-map.md`](./manifest-surface-lane-map.md).

Minimum lanes to preserve in every review/report:
- authored package-manifest lane,
- inherited/defaulted/discovered lane,
- packaged/publish-normalized lane,
- script/frontmatter subject lane,
- machine-consumer import lane,
- human projection lane,
- evolving schema/watch lane.

Design rule: a `manifest-pack/v0` consumer must always be able to tell **which lane produced which statement**.

## Core components

### 1) `manifest-subject/v0`
Canonical identity for one manifest-bearing subject:
- workspace/package/script identity
- manifest path or embedded-manifest location
- source revision / file digest
- host package selection context when relevant
- authored kind:
  - package manifest
  - virtual-workspace manifest
  - embedded script frontmatter
  - generated/normalized packaged manifest

Design rule: every later diff/report must name **which subject and lane** it is describing.

### 2) `manifest-authored-report/v0`
A normalized report of what the author wrote and what Cargo inferred.

Fields:
- explicit sections/keys present
- inferred/defaulted fields
- unknown/ignored fields where relevant
- manifest edition / rust-version posture
- package metadata fields
- dependency declarations and feature declarations as written
- `workspace = true` inheritance posture when relevant
- warnings about version/compatibility-sensitive syntax

Design rule: preserve **explicit vs inferred/defaulted** truth rather than flattening everything into one normalized map.

### 3) `manifest-publish-diff/v0`
A semantic diff between authored manifest truth and packaged/published truth.

Fields:
- removed sections/keys (`[patch]`, `[replace]`, `[workspace]`, etc.)
- normalized values or rewritten formatting-sensitive fields
- included/excluded file policy references
- lockfile posture
- publish restrictions / registry target posture
- warnings about authored fields that do not survive publication or change meaning downstream

Design rule: this is the missing bridge between repo review and `.crate` reality.

### 4) `feature-catalog/v0`
A declared feature-surface catalog.

Fields:
- feature names
- descriptions when available
- visibility posture (`public`, `hidden`, `internal`, `tooling-only`, etc. when available)
- deprecation/replacement posture
- optional-dependency links
- default-feature membership
- mutually-exclusive or global constraints when declared
- docs/consumer-display posture

Design rule: keep **declared feature surface** separate from **activated feature result**; Dependency Control owns the latter.

### 5) `manifest-consumer-report/v0`
A report of what specific consumers can or do import.

Fields:
- consumer class:
  - `cargo-metadata`
  - `cargo-info`
  - `cargo-package`
  - registry/docs surface
  - script/frontmatter consumer
  - editor/import consumer
- imported fields
- omitted or lossy fields
- stability/versioning contract of the consumer lane when relevant
- reason codes for mismatch or lossiness

Design rule: do not pretend all manifest consumers see the same thing.

### 6) `manifest-pack/v0`
Bundle format:
- `manifest-subject/v0`
- `manifest-authored-report/v0`
- optional `manifest-publish-diff/v0`
- optional `feature-catalog/v0`
- one or more `manifest-consumer-report/v0`
- optional raw attachments:
  - original `Cargo.toml`
  - packaged normalized manifest
  - embedded frontmatter fragment
  - `cargo metadata` snapshot
  - `cargo info` snapshot

### 7) `cargo manifest`
Reference UX:
- `cargo manifest inspect`
- `cargo manifest publish-diff`
- `cargo manifest features`
- `cargo manifest consumers`
- `cargo manifest pack`
- `cargo manifest diff --against <pack|path|crate>`

`cargo manifest` should start as an **adapter and report layer**, not as a new source of manifest semantics.

## What the kit should provide to others
- **Maintainers:** reviewable manifest changes instead of raw TOML churn.
- **Registry/release tooling:** a clean authored → packaged handoff.
- **Docs/atlas/support tooling:** a stable import boundary for package metadata and feature surfaces.
- **Migration tooling:** explicit edition/rust-version/frontmatter/defaulting diffs.
- **Policy/trust/package-admission tooling:** attachable manifest evidence without silently re-parsing repo state.

## Integration points
- **Repo Composition Stack:** attach discovery/config/workspace-selection reports; Manifest Surface must not redefine them.
- **ScriptKit:** import embedded-manifest/frontmatter truth for scripts; Manifest Surface must not claim execution receipts.
- **Dependency Control Stack:** import `feature-catalog/v0` as declared feature surface; activation/unification stays downstream.
- **Public API / Package Admission:** import publish-diff and feature-catalog data without pretending those conclusions live in the manifest layer.
- **Publisher & Source Identity:** import publish/registry declarations without turning manifest declaration into issuer-backed authority.

## Hard problems (explicitly scoped)
1. **Authored and published truth differ**
   - The kit must preserve both instead of blessing one and discarding the other.
2. **Discovery matters but belongs elsewhere**
   - Workspace/config lookup changes what manifest is active, but Repo Composition owns that evidence.
3. **Feature metadata is evolving**
   - v0 must handle partial support and absent fields honestly.
4. **Consumer lossiness is real**
   - `cargo metadata`, `cargo info`, registries, docs hosts, and scripts each see different slices.
5. **Manifest style is not the same as semantic truth**
   - Formatting tools are useful, but the kit should report semantics, not merely style.

## Evaluation plan
Use the ranked rollout in [`design/manifest-truth-pilot-program.md`](./manifest-truth-pilot-program.md):
1. ordinary library/package manifest lane,
2. packaged publish-diff lane,
3. workspace/discovery lane,
4. script/frontmatter lane,
5. consumer-import lane, read through the lane map so machine and human consumer projections stay separate.

Success bar:
- ordinary manifest edits become semantically reviewable,
- publish-time rewrites become explicit instead of folklore,
- feature-surface metadata can travel without activation confusion,
- and downstream consumers can import one pack instead of reconstructing their own partial manifest truth.
