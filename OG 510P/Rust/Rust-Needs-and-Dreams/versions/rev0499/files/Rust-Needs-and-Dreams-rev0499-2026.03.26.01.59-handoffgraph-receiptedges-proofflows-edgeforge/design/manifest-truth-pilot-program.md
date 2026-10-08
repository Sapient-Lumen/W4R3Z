# Design: Manifest Truth pilot program

## Goal
Prove that **manifest truth can become a reviewable substrate** before the ecosystem tries to standardize every last Cargo/editor/registry behavior.

This pilot program is the execution layer for:
- [`design/manifest-surface-kit.md`](./manifest-surface-kit.md)
- [`design/manifest-surface-lane-map.md`](./manifest-surface-lane-map.md)
- [`design/manifest-truth-stack.md`](./manifest-truth-stack.md)

## Why now
- Cargo 1.94 still treats manifest syntax/style/discovery as active design space, and the config `include` key is now stable.
- `cargo package` already produces materially different packaged manifests.
- feature metadata / visibility / deprecation work is still active.
- cargo-script/frontmatter widens the set of manifest-bearing subjects and makes defaulted/disallowed-field posture reviewable.
- workspace inheritance now spans package metadata, dependencies, and lints.
- `cargo metadata` and `cargo info` are stable enough that adapter/report work can start now without pretending they already cover the entire seam.

That combination makes this a good time for a **review boundary** contribution instead of waiting for all manifest-adjacent RFC work to finish.

Pilot rule: each lane below should be evaluated against the explicit split in [`design/manifest-surface-lane-map.md`](./manifest-surface-lane-map.md), especially the difference between authored text, inherited/defaulted interpretation, packaged truth, and consumer projections.

## What this pilot must prove
1. **subject identity** — we can point at one manifest-bearing thing without ambiguity.
2. **authored truth** — explicit vs inferred/defaulted fields can be reported honestly.
3. **publish truth** — authored vs packaged manifest differences can be reviewed semantically.
4. **consumer truth** — named consumers can import different slices without silent drift.
5. **handoff truth** — downstream tools can consume manifest packs without re-parsing everything.

## Failure modes to avoid
1. **formatter theater** — lots of style or normalization output, little semantic review value.
2. **metadata collapse** — treating authored, published, discovered, and consumed manifests as one truth.
3. **feature confusion** — declared feature surface getting flattened into activated feature results.
4. **script exceptionalism** — embedded manifests becoming a separate universe instead of another subject lane.
5. **consumer overclaiming** — registry/docs/editor views being mistaken for the authoritative manifest.

## Ranked pilot lanes

### 1) Ordinary library/package lane
Subject:
- one library crate with feature declarations, optional dependencies, publish restrictions, and meaningful package metadata

Artifacts to prove:
- `manifest-subject/v0`
- `manifest-authored-report/v0`
- `feature-catalog/v0`
- one `manifest-consumer-report/v0` for `cargo metadata`
- one `manifest-consumer-report/v0` for `cargo info`

Success bar:
- a maintainer can review semantic manifest changes without reading raw TOML only;
- declared features are visible without claiming activation/runtime truth.

### 2) Packaged publish-diff lane
Subject:
- one published crate or release candidate where `cargo package` materially rewrites the manifest

Artifacts to prove:
- `manifest-publish-diff/v0`
- packaged normalized manifest attachment
- file include/exclude and lockfile posture notes where relevant

Success bar:
- repo review can see what the published manifest actually looks like;
- removed or normalized sections are no longer folklore.

### 3) Workspace/discovery lane
Subject:
- one multi-package workspace with inheritance and nontrivial config/discovery behavior

Artifacts to prove:
- `manifest-authored-report/v0`
- imported `workspace-report` / config-set references from Repo Composition
- consumer-lossiness notes when package-local vs workspace-root semantics differ

Success bar:
- manifest truth and discovery truth are linked without being collapsed.

### 4) Script/frontmatter lane
Subject:
- one single-file package using embedded frontmatter

Artifacts to prove:
- `manifest-subject/v0` for embedded frontmatter
- `manifest-authored-report/v0` with explicit/defaulted/disallowed-field posture
- one `manifest-consumer-report/v0` for the script/frontmatter consumer lane
- handoff reference into ScriptKit receipts

Success bar:
- single-file packages stop being treated as unreviewable side doors.

### 5) Consumer-import lane
Subject:
- one subject consumed by at least three downstream lanes (for example `cargo metadata`, registry/docs display, and package-admission or migration tooling)

Artifacts to prove:
- multiple `manifest-consumer-report/v0`
- `manifest-pack/v0`
- import notes for at least one downstream tool family

Success bar:
- downstream tools can import one pack and say what they omitted or reinterpreted;
- consumer lossiness becomes explicit.

## Graduation criteria
The pilot graduates when:
- authored/published/consumer manifest truths are all explicit,
- feature-surface metadata can travel without activation confusion,
- script and workspace lanes fit the same subject model,
- and at least one downstream consumer imports `manifest-pack/v0` instead of silently rebuilding the model.

## Watch/wait criteria
Keep this seam in watch/wait if:
- feature metadata support remains too speculative to model honestly,
- publish-diff behavior proves too tool-specific to report portably,
- or no downstream consumer actually benefits from the pack.

## Anti-goals
Do **not** start with:
- a universal manifest editor,
- a style-enforcement campaign,
- a registry replacement view,
- or another graph/resolver UI that forgets authored vs published truth.

The first win should be **honest manifest review artifacts**, not a perfect one-true manifest platform.

This pilot is the rollout path for the stack-level proposal candidate in [`proposals/epic-manifest-truth-stack.md`](../proposals/epic-manifest-truth-stack.md).
