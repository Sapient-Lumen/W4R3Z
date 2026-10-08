# Design: Discovery Boundary Kit (`cargo discoverbound`, `discovery-pack/v0`)

## Goal
Define a thin, reviewable boundary for **what Cargo discovered and why** before later layers talk about inheritance, package selection, build graphs, reports, scripts, or realized environments.

This kit should make Cargo discovery boring in the best possible way:
- explicit invocation subject,
- explicit manifest walk,
- explicit workspace attachment or opt-out,
- explicit config walk,
- explicit consumer-import lossiness.

It should not replace Cargo’s actual discovery logic, nor should it pretend discovery already implies repo governance or build intent.

## Why this seam matters now
Cargo’s current documentation and design work keep pointing at the same underlying need:
- config discovery is hierarchical through parent directories and `$CARGO_HOME`;
- workspace attachment searches parent directories for `[workspace]` and allows `package.workspace` overrides;
- `cargo locate-project` still exposes only a partial answer,
- command-level working-directory and manifest-path choices materially affect discovery,
- Cargo 1.94 explicitly calls out broken parent files and possible opt-out controls,
- `cargo-script` is beginning with workspace auto-discovery disabled,
- and Cargo’s plumbing model begins with **Locate project** and **Read manifests for a workspace** before anything about build plans or final artifacts.

That is enough evidence that discovery itself deserves a portable contract.

## References (signals)
- Cargo configuration reference (hierarchical probing through current dir, parent dirs, and `$CARGO_HOME`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspaces reference (upward `[workspace]` search, `package.workspace`, `default-members`, cwd-sensitive package selection): https://doc.rust-lang.org/cargo/reference/workspaces.html
- Manifest reference (`package.workspace` field): https://doc.rust-lang.org/cargo/reference/manifest.html
- `cargo locate-project`: https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html
- `cargo build` / `cargo metadata` manifest-search defaults and cwd effects: https://doc.rust-lang.org/cargo/commands/cargo-build.html ; https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo 1.94 dev-cycle note (parent-file interference, discovery improvements, possible `package.workspace = false`, cargo-script auto-discovery disabled): https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Accepted Cargo plumbing goal (Locate project → Read manifests → ...): https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo 1.90 dev-cycle note (`cargo-plumbing` prototype had to re-read manifests within commands): https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

## Current archive decision
The right contribution is **not** another workspace manager, config wrapper, repo daemon, or editor-only discover hook.

It is a thinner kit with explicit boundaries:
- **Discovery Boundary Kit** owns invocation subject, manifest walk, workspace attachment, config discovery, and consumer-import lossiness.
- **Workspace Governance Kit** imports discovery truth and owns effective inheritance, ignored/shadowed settings, nested-workspace ambiguity, and package-selection explanation.
- **Config Set Kit** imports selected scope and owns bounded execution matrices for real work lanes.
- **Build Interop Kit** imports discovery truth and owns machine-facing graph/plan/event exports for tools around Cargo.
- **ScriptKit** owns script subject/frontmatter/workspace posture for single-file lanes.
- **Workspace Environment Stack** owns the realized toolchain/native/runtime/credential environment after discovery selected the repo/package/workspace subject.

## Core artifact family
### 1) `discovery-subject/v0`
A small record describing how discovery started:
- invocation cwd
- explicit `--manifest-path` or equivalent
- explicit working-directory shift (`cargo -C` or wrapper-local equivalent)
- caller class (human CLI / script runner / editor / CI / outer build)
- intended subject class (manifest, member package, workspace root, standalone script)

### 2) `manifest-discovery-report/v0`
A reviewable walk of manifest search:
- candidate paths considered
- why a candidate was accepted, skipped, rejected, or errored
- whether failures were syntax, nightly-feature, missing-file, or policy-related
- whether the final manifest came from direct path, cwd search, or wrapper import

### 3) `workspace-attachment-report/v0`
How the subject became attached to a workspace:
- auto-upward discovery
- explicit `package.workspace`
- explicit opt-out / detached posture
- nested or ambiguous attachment candidates
- package-selection consequences that should be handed to governance rather than decided here

### 4) `config-discovery-report/v0`
How config search worked:
- config files considered in current dir / parent dirs / `$CARGO_HOME`
- inclusion / optional-inclusion provenance where relevant
- merge order and shadowing notes
- files skipped because they were absent, unreadable, unsupported, or out of scope
- user-home or machine-wide layers distinguished from repo-local layers

### 5) `discovery-consumer-import-report/v0`
What a consumer imported from the above truths:
- `cargo locate-project`
- `cargo metadata`
- rust-analyzer or other editor discovery hooks
- CI wrappers / shell scripts / repo-local helper tools
- script runners such as cargo-script-style lanes
- explicit lossiness notes and unsupported assumptions

### 6) `discovery-pack/v0`
A linked bundle that carries the subject, manifest walk, workspace attachment, config walk, consumer imports, and raw attachments.

### 7) `discovery-diff/v0`
A diff artifact for PR review or migration review, split into:
- invocation-subject drift
- manifest-walk drift
- workspace-attachment drift
- config-discovery drift
- consumer-import drift

## Reference UX
A reference tool should expose something like:
- `cargo discoverbound explain`
  - summarize the current discovery story in one human-readable view.
- `cargo discoverbound walk`
  - print the exact manifest and config search walk.
- `cargo discoverbound attach`
  - explain workspace attachment, override, or opt-out posture.
- `cargo discoverbound diff <A> <B>`
  - compare two discovery situations.
- `cargo discoverbound pack`
  - emit `discovery-pack/v0`.
- `cargo discoverbound verify-pack`
  - validate that a pack is internally consistent and honestly marked for lossiness.

## What a worthy contribution would look like in practice
### 1) Start with explanation and provenance, not policy
The first version should answer:
- where did discovery start,
- which manifest candidates were considered,
- how did workspace attachment happen,
- which config files influenced discovery,
- and what later consumers imported.

It should not silently choose governance, package selection, or build plans.

### 2) Make opt-out and override posture explicit
Discovery becomes much more reviewable if reports can say whether a workspace relationship was:
- implicit by upward search,
- explicit via `package.workspace`,
- explicitly disabled,
- or merely assumed by a consumer.

### 3) Keep consumer lossiness visible
`cargo locate-project`, `cargo metadata`, editor wrappers, script runners, and outer build systems should be modeled as importers with partial views, not as the source of truth.

### 4) Prefer linked artifacts over one mega-report
A discovery kit should stay smaller than Repo Composition or Tooling Contract. The pack can link several precise artifacts without re-normalizing the whole world.

## Shared success criteria
A strong Discovery Boundary Kit should let a reviewer answer five questions quickly:
1. What was the intended subject of this invocation?
2. Which manifests were walked and why did Cargo stop where it did?
3. How did the subject attach to a workspace, or why did it stay detached?
4. Which config layers were actually discovered and considered?
5. Which downstream consumers imported the story, and what did they lose?

If the kit cannot answer those questions, later repo/build/environment layers are still rebuilding discovery folklore by hand.

## Boundaries / non-goals
- not a replacement for Cargo workspace semantics
- not a replacement for config files or `cargo metadata`
- not a universal repo policy engine
- not a build-plan or execution-event protocol
- not a script runner
- not a hidden attempt to standardize one repo layout

## Why this is an ecosystem contribution, not only a large-repo tool
The same discovery mistakes hit many scales:
- a single crate unexpectedly joining a parent workspace,
- a script lane that should stay detached,
- an editor and CLI disagreeing about the repo root,
- CI running from a different cwd than developers,
- or a home-directory config/manifest affecting unrelated work.

Large monorepos make the pain louder, but the missing boundary is broadly reusable.
