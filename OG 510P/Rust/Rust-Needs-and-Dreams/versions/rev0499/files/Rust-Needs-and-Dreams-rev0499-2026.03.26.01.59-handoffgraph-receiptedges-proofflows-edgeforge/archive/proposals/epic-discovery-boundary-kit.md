# Epic proposal: Discovery Boundary Kit (`cargo discoverbound`, `discovery-pack/v0`)

## One-line thesis
Build a thin Cargo companion layer for **discovery truth** that links **invocation subject**, **manifest walk**, **workspace attachment or opt-out**, **config discovery provenance**, and **consumer-import lossiness** into one portable review boundary without pretending repo governance, package selection, build plans, and realized environments are all the same thing.

## Why this is now worth doing
Rust now has enough evidence that discovery itself is a distinct missing layer:
- Cargo config discovery is hierarchical through parent directories and `$CARGO_HOME`;
- workspace attachment searches upward and supports `package.workspace` overrides;
- default package selection depends on where invocation begins;
- `cargo locate-project` and `cargo metadata` still expose only partial discovery views;
- Cargo 1.94 explicitly calls out broken parent files, possible workspace-auto-discovery opt-outs, and cargo-script starting detached;
- the accepted Cargo plumbing model begins with **Locate project** and **Read the manifests for a workspace**;
- and the 1.90 plumbing prototype still had to re-read manifests because Cargo’s Rust APIs were not yet exposing the right structure.

What is still missing is the **kit-level boundary that says this invocation intended this subject, Cargo walked these manifests and config layers, attached this way to a workspace or detached on purpose, and these consumers imported the result with these losses**.

## Working name
- CLI: `cargo discoverbound`
- primary artifact: `discovery-pack/v0`

## Scope
### This epic should own
- invocation subject truth
- manifest search / stop / rejection provenance
- workspace attachment / override / opt-out truth
- config discovery provenance and merge-order notes
- consumer import and lossiness notes
- diffable review points across cwd / manifest-path / repo-layout / wrapper changes

### This epic should not own
- effective workspace inheritance and policy
- bounded execution matrices
- build graphs, build plans, or execution events
- target-dir/build-dir/output truth
- toolchain/native/runtime/credential realization
- one fake “workspace health” score

## Candidate artifact family
### `discovery-brief/v0`
Why this invocation matters, what subject was intended, and where uncertainty remains.

### `discovery-subject/v0`
Invocation cwd, explicit manifest-path, caller class, and intended subject class.

### `manifest-discovery-report/v0`
The manifest walk and stop/rejection reasons.

### `workspace-attachment-report/v0`
Auto-discovery, override, opt-out, or ambiguity posture.

### `config-discovery-report/v0`
Config-file search, include/merge provenance, and scope classification.

### `discovery-consumer-import-report/v0`
What each consumer imported, omitted, or reinterpreted.

### `discovery-pack/v0`
The portable bundle linking the above artifacts and raw attachments.

### `discovery-diff/v0`
What changed between two discovery situations, split by subject, manifest walk, workspace attachment, config discovery, and consumer imports.

## Recommended rollout
1. plain Cargo member/workspace lane
2. explicit `--manifest-path` / cwd-shift lane
3. detached and opt-out workspace lane
4. script-runner / cargo-script-style lane
5. editor and CI wrapper import lane
6. repo-composition / workspace-governance / build-interop handoff lane

This should be driven by `design/discovery-boundary-kit.md`, with Repo Composition, Workspace Governance, Build Interop, ScriptKit, Manifest Truth, and Workspace Environment importing the result rather than quietly re-owning it.

## What makes this epic “epic” rather than incremental
An incremental tool would improve one symptom:
- a better `cargo locate-project` wrapper,
- a nicer workspace-root detector,
- a config-layer explainer,
- or another editor-specific discovery hook.

An epic contribution here instead gives Rust one **portable discovery contract** above those ingredients.
That is strategically different because it can:
- stop discovery from being repeatedly re-described inside repo, script, editor, CI, and environment layers;
- make accidental parent-file interference reviewable;
- make detached/attached posture explicit instead of folkloric;
- keep consumer lossiness visible;
- and give future Cargo discovery changes one reusable place to land.

## Design principles
- **Invocation subject truth is not workspace governance truth.**
- **Workspace attachment is not package-selection policy.**
- **Config discovery is not environment realization.**
- **Consumer imports are views, not the source of truth.**
- **Lossiness and instability are explicit.**
- **The kit remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact subject the caller intended,”
- “this is the manifest walk Cargo took,”
- “this is how the subject attached to a workspace or stayed detached,”
- “these are the config layers that actually influenced discovery,”
- “these are the consumers that imported the story,”
- and “here is what later repo/build/environment layers may safely conclude next,”

without reconstructing the story from cwd guesses, manifest-path glue, parent-directory archaeology, and wrapper-specific heuristics.

## Read this with
- `gaps/discovery-boundaries-manifest-workspace-config-and-explicit-attachment.md`
- `design/discovery-boundary-kit.md`
- `design/workspace-governance-kit.md`
- `design/repo-composition-stack.md`
- `design/build-interop-kit.md`
- `design/scriptkit.md`
- `design/manifest-truth-stack.md`
- `design/workspace-environment-stack.md`
