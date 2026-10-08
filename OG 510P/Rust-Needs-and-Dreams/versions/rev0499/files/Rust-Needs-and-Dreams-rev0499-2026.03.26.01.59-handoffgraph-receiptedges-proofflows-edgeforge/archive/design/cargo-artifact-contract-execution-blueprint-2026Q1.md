# Design: Cargo Artifact Contract execution blueprint (2026 Q1)

## Goal
Turn the archive's clearest still-unresolved **final-output / handoff-shaping seam** into a concrete answer to:

> if ideal Rust wants a trustworthy way to tell tools and humans what Cargo actually produced, what should that contribution ship in theory and practice beyond `target/` archaeology, JSON scraping, or one more release manifest?

This note does **not** promote a new frontier.
It deepens an already-promoted seam into a real execution blueprint.

## Why this now deserves execution treatment
The upstream signals are unusually aligned around final-artifact boundaries rather than only around build internals:
- Rust's 2026 flagship roadmap keeps **prototype cargo plumbing commands** under “Building blocks”.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The accepted Cargo plumbing goal already decomposes build orchestration into locate/read/lock/resolve/plan/execute/**stage final artifacts**, and says later commands should accept the outputs of earlier ones.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo's March 13, 2026 build-dir-layout-v2 testing call says many projects still rely on unspecified build-dir details because Cargo is missing features, while also making explicit that users can separate intermediate build artifacts from final artifacts.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Nightly rustc's Cargo layout docs now say `artifact-dir` is part of Cargo's **public API**, while `build-dir` remains an internal implementation detail.
  https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/layout/index.html
- Cargo's `--artifact-dir` docs explicitly say exact final filenames are otherwise awkward to determine.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93's custom-final-artifacts discussion shows Cargo reasoning explicitly about staged final artifacts, selected-package uplift rules, collision reporting, and concurrent safety.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo's external-tools docs still say the stable third-party surfaces are mainly `cargo metadata`, `--message-format=json`, and custom subcommands. Those are real ingredients, but they are still a patchwork rather than one final-output contract.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- SBOM precursor files are now defined as artifact-linked sidecars generated for executable and linkable outputs uplifted into target or artifact directories.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust release notes now clarify that `.crate` tarballs should be treated as **intermediate** unless you are using `cargo package`, which sharpens the line between packaged outputs and other final artifacts.
  https://doc.rust-lang.org/beta/releases.html
- Cargo plugins are still the official escape hatch when Cargo itself cannot be everything to everyone.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

Taken together, those signals say the archive should stop talking about artifact truth as only a kit or a frontier note.
It should name the actual build plan.

## Headline answer
If one serious team or coalition wants to build the archive's strongest artifact-side contribution, the answer should now be:

> Build a **Cargo Artifact Contract** that preserves selected-subject truth, evidence-path truth, final-artifact identity, origin/staging truth, sidecar truth, and downstream-handoff truth, then emits reviewable packs for release, inventory, repro, install, support, and larger-build-system consumers.

That answer is deliberately thinner than “replace release tooling”.
It is also deliberately stronger than “parse Cargo JSON better”.

## What this contribution should be in theory

### Core thesis
An artifact contract becomes real ecosystem infrastructure when one portable pack can answer all of these honestly:
1. **what exact build subject was selected;**
2. **what evidence path observed the result;**
3. **which final outputs belong to that subject;**
4. **which of those outputs are Cargo-native, package/doc outputs, or Cargo-mediated uplift/staging results;**
5. **which sidecars attach to which artifact entries;**
6. **which downstream consumers may conclude what, without replaying the build or scraping the target directory.**

If a project still needs to reconstruct that story from `cargo metadata`, `--message-format=json`, ad hoc `target/` walks, build-script folklore, package listings, and downstream release manifests, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable final-output review and handoff**.

It should include:
- selected build-subject identity;
- evidence-path / observation-path posture;
- final artifact identity and class;
- origin / staging / copy posture;
- artifact-sidecar attachment;
- bounded handoffs to downstream consumers.

It should not become:
- a replacement build system;
- a release orchestration suite;
- a hosted artifact inventory portal first;
- or a universal package/install/update manager.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **selected-subject truth** — workspace/package/target/profile/features/toolchain/command scope;
- **evidence-path truth** — JSON build events, artifact-dir copies, package/doc surfaces, build-script directives, or bounded imports;
- **final-artifact identity truth** — what concrete outputs exist, their class, and which Cargo subject they belong to;
- **origin/staging truth** — Cargo-native output, package/doc output, Cargo-mediated uplift, or imported attachment;
- **sidecar truth** — which SBOM or other sidecars attach to an artifact entry without replacing the entry itself;
- **consumer truth** — what release, inventory, repro, install, support, or external-build consumers may and may not conclude.

Without those separations, “artifact contract” turns back into target-dir lore.

### Shape rule
This contribution should begin as a **reference layer + report/pack command + acceptance corpus**.
That means:
- a **reference layer** for selected subjects, artifact entries, and handoff vocabulary;
- a thin **report/pack command** for collecting, diffing, and exporting artifact packs;
- and an **acceptance corpus** that proves the contract across binary, example, doc, package, build-script uplift, and sidecar lanes.

It should not begin as a giant service, a frozen universal schema for every downstream tool, or a wide build-system abstraction.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion command and schema family:
- `cargo artifacts subject`
- `cargo artifacts collect`
- `cargo artifacts report`
- `cargo artifacts diff`
- `cargo artifacts handoff --consumer <release|inventory|repro|install|support|buildsystem>`
- `cargo artifacts pack`

The tool should import native Cargo surfaces where possible and say explicitly when it relied on unstable or lossy paths.

### Public artifact spine

#### Imported/internal families
- `artifact-subject/v0`
- `artifact-entry/v0`
- `artifact-sidecar-index/v0`
- `artifact-evidence-route/v0`
- `artifact-handoff-limits/v0`

#### Public review families
- `artifact-brief/v0`
- `artifact-report/v0`
- `artifact-diff/v0`
- `artifact-pack/v0`
- `artifact-handoff/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject anchors** — package selection, command class, targets, profile, features, toolchain, and directory posture;
- **evidence anchors** — which Cargo or adjacent surfaces were observed and which were inferred;
- **artifact anchors** — output class, package target, logical artifact identity, path/location facts, and omission markers;
- **origin anchors** — Cargo-native, package/doc-native, staged/uplifted, copied-to-artifact-dir, or imported sidecar;
- **sidecar anchors** — artifact-linked SBOM and similar attachments;
- **consumer limits** — what downstream consumers may conclude without re-deriving the build.

## Commands and what they should emit

### `cargo artifacts subject`
Purpose:
- freeze the selected build subject;
- emit `artifact-subject/v0`.

Important rule:
- package, command, target, profile, and feature scope must be explicit; do not let a path or one observed file stand in for the selected subject.

### `cargo artifacts collect`
Purpose:
- collect final-output entries and their observation paths;
- emit `artifact-entry/v0`, `artifact-sidecar-index/v0`, and `artifact-evidence-route/v0`.

Important rule:
- enumerate what was observed, then mark what is inferred or omitted; do not silently widen from one JSON line or one copied path to a stronger claim.

### `cargo artifacts report`
Purpose:
- emit a human-reviewable summary of output classes, uncertainty, collisions, staging posture, and prohibited conclusions;
- emit `artifact-report/v0`.

Important rule:
- collision posture, uplift posture, and path lossiness must be explicit.

### `cargo artifacts diff`
Purpose:
- compare two artifact packs while preserving the difference between:
  - subject drift,
  - output-set drift,
  - origin/staging drift,
  - sidecar drift,
  - and consumer-handoff drift.

### `cargo artifacts handoff`
Purpose:
- emit smaller consumer handoffs for release review, inventory, reproducibility checks, install planning, support intake, or larger-build-system import.

Important rule:
- a handoff is lossy and subordinate to the pack; it must never become the canonical artifact record by itself.

## Ranked feature set

### P0 — required for a worthy v0
- freeze selected-subject truth explicitly;
- enumerate final outputs for at least bin/lib/example/doc/package lanes;
- preserve origin/staging/copy posture;
- attach artifact-linked sidecars without flattening artifact identity into sidecars;
- emit one portable report and one portable pack;
- support one consumer handoff lane;
- surface `partial`, `lossy`, `unstable`, `copied`, `uplifted`, and `unsupported` honestly.

### P1 — strong near-term extensions
- build-script directive / uplift lanes;
- collision and selected-package uplift reports;
- release/import handoffs to `cargo-dist`-class tooling without pretending release manifests are the canonical artifact truth;
- inventory / SBOM handoffs that stay linked to artifact entries;
- repro/import handoffs that preserve exact output-set identity.

### P2 — do later or fold elsewhere
- hosted artifact browsing portals;
- install/update orchestration;
- artifact signing/provenance ecosystems as if they were the same thing as artifact identity;
- universal external-build-system control planes.

## Pilot lanes that best prove the idea

### 1) Cargo-native bin/lib/example lane
Prove:
- that one selected subject can yield a stable artifact pack without target-dir scraping.

### 2) Doc + package lane
Prove:
- that docs and `.crate` package outputs are distinct artifact classes with different semantics and should not be flattened into “final files”.

### 3) Build-script uplift lane
Prove:
- that staged/custom final artifacts can be represented honestly, with collision and selection posture visible.

### 4) Sidecar lane
Prove:
- that SBOM precursor attachments can ride alongside artifact entries without replacing artifact truth.

### 5) Downstream handoff lane
Prove:
- that release, inventory, repro, or support consumers can import bounded artifact truth rather than reconstructing it independently.

## Dependencies and imports
This blueprint should import rather than replace:
- Cargo external-tool surfaces;
- Cargo build-analysis/report work where useful;
- package/doc outputs from Cargo itself;
- inventory / SBOM work;
- release, install, repro, and support layers as downstream consumers.

Read with:
- `design/cargo-artifact-contract-2026Q1.md`
- `design/artifact-surface-kit.md`
- `proposals/epic-artifact-surface-kit.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/release-truth-stack.md`
- `design/inventory-evidence-stack.md`
- `design/repro-build-kit.md`
- `design/consumer-install-kit.md`

## Anti-goals worth refusing early
Refuse these tempting wrong shapes early:
- “just bless `target/` paths and call that the contract”;
- “just reuse release manifests as build truth”;
- “just surface every file Cargo touched”;
- “just ship a dashboard over JSON events”;
- “just build a universal package/install/release platform”.

## Ranking / portfolio position
This blueprint does **not** outrank Build-State Evidence.
It also does **not** replace Build Interop, Release Truth, Inventory Evidence, or Consumer Install.

What it does is sharpen the archive's repeatedly named next move:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Cargo Artifact Contract** is now the clearest remaining **final-output / sidecar / downstream-handoff execution blueprint**;
- and future artifact/release/install/repro work should import this layer rather than rediscovering final-output truth privately.
