# Epic proposal: Manifest Surface Kit

## One-line pitch
Build a portable **manifest-truth substrate** for Rust so that authored manifests, packaged manifests, feature-surface metadata, and consumer-import views become reviewable and diffable instead of living in separate layers of Cargo lore.

## Why this could be epic
Cargo’s manifest layer is quietly becoming one of the most strategic seams in the ecosystem:
- Cargo keeps evolving manifest syntax/style/discovery behavior.
- `cargo package` already rewrites the published manifest.
- feature metadata / visibility / deprecation are active Cargo design topics.
- single-file packages put manifests inside source files.
- external tools increasingly depend on stable machine-readable manifest projections.

An epic contribution here would not be “another TOML tool.”
It would become the common language between authoring, publication, scripts, registries, docs hosts, migration tooling, and package-admission/policy consumers.

## Proposed core
- `manifest-subject/v0`
- `manifest-authored-report/v0`
- `manifest-publish-diff/v0`
- `feature-catalog/v0`
- `manifest-consumer-report/v0`
- `manifest-pack/v0`
- `cargo manifest` reference UX

## What success would look like
- PR/release review can see what a manifest change *means*, not just how TOML text changed.
- published-manifest drift becomes attachable evidence instead of tarball archaeology.
- feature-surface visibility/deprecation can travel without activation confusion.
- script/frontmatter manifests and workspace manifests share one subject model.
- downstream tools import manifest packs instead of silently re-parsing and disagreeing.

## Why this should not be absorbed elsewhere
- **Not just Repo Composition:** discovery/config truth is only part of the problem.
- **Not just ScriptKit:** scripts widen manifest scope but do not define authored/published truth for ordinary packages.
- **Not just Dependency Control:** declared feature surface is not activated feature reality.
- **Not just Package Admission or Policy:** those are downstream verdict layers.
- **Not just Cargo metadata:** stable structure output is necessary, but not sufficient for authored/published/consumer diffs.

## First rollout
Follow the ranked pilots in [`design/manifest-truth-pilot-program.md`](../design/manifest-truth-pilot-program.md):
1. ordinary package lane,
2. publish-diff lane,
3. workspace/discovery lane,
4. script/frontmatter lane,
5. consumer-import lane.

## Anti-goals
- one universal manifest editor,
- one style-enforcement crusade,
- one replacement for Cargo’s own semantics,
- one registry-controlled truth page,
- or one hidden dependency/feature graph engine pretending to be manifest infrastructure.

The point is to make manifest truth **portable, explicit, and attachable**.
