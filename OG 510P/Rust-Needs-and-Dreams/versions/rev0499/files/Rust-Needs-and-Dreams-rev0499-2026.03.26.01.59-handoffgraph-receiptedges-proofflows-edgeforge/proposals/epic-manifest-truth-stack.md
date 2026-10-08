# Epic Proposal: Manifest Truth Stack (`cargo manifest-truth` + `manifest-pack/v0`)

## One-sentence pitch
Make Rust manifest behavior boring by standardizing a portable layer that keeps **authored fields, workspace/config discovery, packaged-manifest rewrites, script/frontmatter defaults, and consumer-import views** distinct instead of forcing every tool to silently tell its own incomplete manifest story.

## Deliverables
- reference command:
  - `cargo manifest-truth`
  - `cargo manifest` (or a compatible adapter surface)
- schemas:
  - `manifest-subject/v0`
  - `manifest-authored-report/v0`
  - `manifest-publish-diff/v0`
  - `feature-catalog/v0`
  - `manifest-consumer-report/v0`
  - `manifest-pack/v0`
  - `manifest-truth-handoff/v0`
- adapters/importers for:
  - `cargo metadata`
  - `cargo info`
  - packaged normalized `Cargo.toml` attachments from `cargo package`
  - workspace/config discovery imports from Repo Composition
  - script/frontmatter subject imports from ScriptKit
  - downstream imports for Package Admission, Library Productization, migration/support tools, and docs/registry consumers
- docs:
  - manifest lane-map guide
  - authored-vs-packaged manifest guide
  - workspace inheritance and discovery guide
  - single-file/frontmatter manifest guide
  - feature-surface vs activation guide
  - consumer-lossiness guide for metadata / info / registry / docs lanes

## Why now (signals)
- Cargo 1.94 makes manifest behavior look like active infrastructure, not frozen syntax: the cycle explicitly calls out TOML 1.1 work, `cargo-cargofmt`, and workspace/config discovery design discussions. Cargo 1.94 also stabilized the config `include` key, which strengthens the need to keep authored manifest truth separate from discovered configuration truth.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo packaging already creates a materially different published manifest: `cargo package` rewrites and normalizes `Cargo.toml`, removes `[patch]`, `[replace]`, and `[workspace]`, always includes `Cargo.lock` unless explicitly excluded, and adds `.cargo_vcs_info.json` as a best-effort hint. That means repo truth and package truth already diverge in ordinary workflows.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo’s external-tools lane is real but intentionally partial. The docs position `cargo metadata` as the machine-readable structure interface, and `cargo metadata` explicitly asks consumers to pin `--format-version`; meanwhile `cargo info` is a human-facing projection whose local-vs-registry behavior is itself evolving. Those are useful imports, not a full manifest-truth contract.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  https://doc.rust-lang.org/cargo/commands/cargo-info.html
- Workspace inheritance keeps widening the semantic surface of what a package manifest “means”: `workspace.package`, `workspace.dependencies`, and `workspace.lints` all affect package interpretation, and release notes now note automatic inheritance of workspace fields during `cargo new` / `cargo init`.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/beta/releases.html
- Single-file packages make manifest truth broader than `Cargo.toml`. The cargo-script/frontmatter RFCs and Cargo’s unstable docs define embedded manifests, defaulted package fields, disallowed fields, and the fact that single-file packages are selected via `--manifest-path` instead of auto-discovery.
  https://rust-lang.github.io/rfcs/3502-cargo-script.html
  https://rust-lang.github.io/rfcs/3503-frontmatter.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust’s 2026 flagship work keeps manifest-adjacent supply-chain semantics active by targeting stabilization of public/private dependencies and SBOM support. That raises the value of having a shared manifest truth boundary instead of letting package/release/admission tooling re-derive manifest meaning independently.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Non-goals
- replacing Cargo’s manifest semantics or becoming a second package manager;
- building one universal manifest editor or formatter crusade;
- collapsing manifest truth into dependency-resolution truth or publish-authority truth;
- making crates.io, docs.rs, or any single UI the only authoritative manifest view;
- pretending feature declarations, activated features, and public-API exposure are the same thing.

## Strategic value
This deserves promotion because it gives the archive a missing **manifest continuity seam**.
With the new lane map, that seam is no longer “all manifest facts in one blob”; it is an explicit family of lanes that can travel together without semantic flattening.
With it:
- authors can review what a manifest change *means* without reverse-engineering Cargo behavior from raw TOML diffs;
- maintainers can see what publication changed without unpacking `.crate` files by hand;
- script/frontmatter lanes can share one subject model with ordinary packages instead of becoming a side universe;
- downstream consumers can import one pack and say what they omitted or transformed instead of each re-parsing and disagreeing;
- adjacent stacks like Library Productization, Package Admission, Publisher & Source Identity, and Migration Truth get a cleaner import boundary.

The prize is not a prettier manifest page.
The prize is a durable record of **what was written, what was inherited or defaulted, what got packaged, what consumers actually saw, and what downstream tools may honestly conclude next**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. make `manifest-subject/v0` the canonical identity artifact for one manifest-bearing subject, including ordinary packages and embedded-frontmatter scripts;
2. make `manifest-authored-report/v0` the canonical explicit/defaulted/inferred report for package-facing manifest fields;
3. make `manifest-publish-diff/v0` the canonical authored-vs-packaged manifest diff, with lockfile/include/exclude posture attached explicitly;
4. make `feature-catalog/v0` the canonical declared feature-surface artifact, including documentation / visibility / deprecation posture where available;
5. make `manifest-consumer-report/v0` the canonical import artifact for named consumers like `cargo metadata`, `cargo info`, registry/docs projections, or package-admission consumers;
6. emit `manifest-pack/v0` and `manifest-truth-handoff/v0` so downstream stacks can import manifest facts without silently rebuilding them.
7. keep lane identity explicit in every report so authored text, inherited/defaulted interpretation, packaged truth, script subjects, machine-consumer imports, human projections, and watch-lane metadata remain reviewable instead of collapsing into one fake manifest state.

## Critical design bet
The critical bet is that **manifest truth becomes useful before Cargo converges every adjacent discovery/config/style/design question**.
That means:
- authored-vs-packaged truth is still worth preserving while Cargo evolves syntax/style and discovery semantics,
- workspace inheritance and config inclusion can attach as context without being flattened into authored manifest truth,
- script/frontmatter lanes can use the same subject model without pretending auto-discovery works the same way,
- and downstream tools can already benefit from portable consumer-lossiness reports even while some manifest-native metadata remains in flight.

Without that boundary, the stack either stays too thin to matter or bloats into a fake one-true Cargo meta-platform.

## Milestones
1. **v0 subject + authored lane**
   - `manifest-subject/v0`
   - `manifest-authored-report/v0`
   - ordinary package examples
2. **v0.2 packaged-manifest lane**
   - `manifest-publish-diff/v0`
   - normalized packaged manifest attachments
3. **v0.3 workspace/discovery lane**
   - imports from Repo Composition
   - explicit inheritance/discovery lossiness notes
4. **v0.4 script/frontmatter lane**
   - embedded-manifest subject identity
   - explicit defaulted/disallowed-field posture
5. **v1 consumer handoffs**
   - `cargo metadata`, `cargo info`, docs/registry, admission/migration/support consumers
   - `manifest-pack/v0` and `manifest-truth-handoff/v0`

## Execution order
Use [`design/manifest-truth-pilot-program.md`](../design/manifest-truth-pilot-program.md) as the stack-level rollout:
1. authored package-manifest lane,
2. inherited/defaulted/discovered lane,
3. packaged publish-diff lane,
4. script/frontmatter lane,
5. machine-consumer import lane,
6. human projection lane,
7. evolving schema/watch lane.

Use [`design/manifest-surface-kit.md`](../design/manifest-surface-kit.md) plus [`design/manifest-surface-lane-map.md`](../design/manifest-surface-lane-map.md) as the leaf-level substrate beneath it.

## Success metrics
- maintainers can distinguish authored, inherited/defaulted, packaged, and consumer-imported manifest truth without reading Cargo source;
- package reviews can attach packaged-manifest diffs instead of relying on folklore about what `cargo package` strips or rewrites;
- script/frontmatter subjects can be reviewed with the same subject vocabulary as ordinary packages;
- downstream consumers can import `manifest-pack/v0` and state their lossiness explicitly;
- the ecosystem gets one explainable manifest continuity seam instead of multiple incompatible mini-views.
