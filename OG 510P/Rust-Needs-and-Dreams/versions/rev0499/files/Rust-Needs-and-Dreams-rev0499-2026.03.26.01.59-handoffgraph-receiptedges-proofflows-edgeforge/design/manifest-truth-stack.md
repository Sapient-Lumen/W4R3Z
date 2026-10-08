# Design note: Manifest Truth Stack (Manifest Surface + Repo Composition + ScriptKit + Dependency Control + Publisher/Source Identity)

## Goal
Define the **division of labor** around one recurring Cargo confusion:

> What is the difference between the manifest someone wrote, the manifest Cargo packaged, the manifest context Cargo discovered, the feature surface a consumer sees, and the conclusions downstream tools draw from that?

This note does not invent a mega-tool.
It explains how these pieces should compose:
- [`design/manifest-surface-kit.md`](./manifest-surface-kit.md)
- [`design/manifest-surface-lane-map.md`](./manifest-surface-lane-map.md)
- [`design/repo-composition-stack.md`](./repo-composition-stack.md)
- [`design/scriptkit.md`](./scriptkit.md)
- [`design/dependency-control-stack.md`](./dependency-control-stack.md)
- [`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md)
- [`design/package-admission-stack.md`](./package-admission-stack.md)

## Why this note is needed now
Current Rust/Cargo signals are pushing manifest truth on several fronts at once:
- manifest syntax and style compatibility still matter because Cargo is navigating TOML 1.1 support and manifest formatting expectations;
- Cargo 1.94 stabilized the config `include` key, which makes discovery/config layering more useful but also sharper to separate from authored manifest truth;
- workspace/config discovery remains an active design topic, while workspace inheritance now spans package metadata, dependencies, and lints;
- feature metadata, visibility, and deprecation are being treated as manifest-native concepts;
- single-file scripts/frontmatter make manifests appear outside ordinary package roots and introduce explicit defaulting/disallowed-field posture;
- `cargo package` already produces a normalized manifest that differs from the authored one;
- `cargo info` and `cargo metadata` are both valuable consumer lanes, but neither is the full manifest-truth boundary;
- and Rust’s 2026 supply-chain work raises the cost of every downstream tool silently re-deriving manifest meaning.

That means ideal Rust needs a cleaner story for manifest truth than “just parse `Cargo.toml` and hope.”

## Lane map discipline
The stack should now be read through [`design/manifest-surface-lane-map.md`](./manifest-surface-lane-map.md).

That lane map exists to keep these truths separate:
- authored package text,
- inherited/defaulted/discovered interpretation,
- packaged publish-normalized manifest truth,
- script/frontmatter subject truth,
- machine-consumer imports,
- human projections,
- evolving schema/watch posture.

If any stack-layer output cannot say which of those lanes it is speaking for, the stack is overclaiming.

## Division of labor
### 1) Manifest Surface Kit owns authored/published/consumer manifest reports
It answers:
> what was written, what was inferred, what was rewritten for publication, and what do named consumers actually import?

It should own:
- `manifest-subject/v0`
- `manifest-authored-report/v0`
- `manifest-publish-diff/v0`
- `feature-catalog/v0`
- `manifest-consumer-report/v0`
- `manifest-pack/v0`

It should **not** own discovery/config lookup, graph activation, issuer-backed authority, or admission/policy verdicts.

### 2) Repo Composition Stack owns discovery and effective context
It answers:
> which manifest/config roots were discovered, which settings were effective, and which packages were actually in scope?

This matters because the same authored manifest can behave differently under different discovery roots or config layers.

### 3) ScriptKit owns single-file execution posture
It answers:
> how did an embedded manifest participate in script execution, caching, and workspace posture?

Script manifests should import Manifest Surface reports rather than redefining authored/defaulted truth.

### 4) Dependency Control Stack owns chosen-graph and activation truth
It answers:
> after resolution, which packages/features/optional deps actually became active, and why?

Manifest Surface should hand off declared feature and dependency intent without pretending that declared surface equals activated graph reality.

### 5) Publisher & Source Identity Stack owns authority and origin truth
It answers:
> who was allowed to publish, through which source/auth posture, and how should downstream consumers interpret origin claims?

Manifest declarations like `package.publish` are useful inputs, but they are not the same as issuer-backed publish authority.

### 6) Package Admission / Policy / Distribution own downstream conclusions
They answer:
> given manifest, graph, identity, trust, inventory, and artifact evidence, what may be published, trusted, installed, or supported?

They should import manifest facts instead of silently re-parsing repo state and telling a different story.

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without reading Cargo source, reverse-engineering registry tarballs, or guessing from editor behavior:
1. Which manifest-bearing subject are we talking about?
2. Which fields were explicit, inferred, defaulted, or ignored?
3. What changed when Cargo packaged the subject?
4. Which consumer lane is seeing which projection of that manifest?
5. Which feature-surface changes are declarations versus activated graph outcomes?
6. Which downstream identity/admission/policy consumers imported the result next?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## What an epic contribution would look like in practice
A serious contribution here would:
- make authored-vs-packaged manifest drift diffable in ordinary review,
- attach feature-surface visibility/deprecation truth without confusing it for activation truth,
- let script/frontmatter lanes and workspace lanes import the same subject model,
- give package-admission/trust/support/release tools a stable import boundary,
- keep consumer-lossiness visible instead of pretending every UI or machine reader sees the same manifest,
- preserve the lane identity of every statement so authored text, inherited meaning, packaged truth, and consumer projections can all travel together without semantic flattening,
- and provide a stack-level `cargo manifest-truth` / `manifest-pack/v0` layer so manifest review can travel without forcing every downstream tool to become a Cargo-semantic clone.

## Anti-goals
Do not turn this stack into:
- one canonical registry page,
- one universal manifest editor,
- one manifest-style crusade,
- one universal dependency/feature graph tool,
- or one policy/trust verdict engine.

The stack is a **truth boundary**, not a new package manager and not a new registry.

## Proposal-layer candidate
The archive should now treat [`proposals/epic-manifest-truth-stack.md`](../proposals/epic-manifest-truth-stack.md) as the stack-level product-direction candidate: a thin `cargo manifest-truth` / `manifest-pack/v0` layer above Manifest Surface + Repo Composition + ScriptKit + Dependency Control + Publisher & Source Identity rather than another formatter, editor shell, or registry/docs-only projection.
