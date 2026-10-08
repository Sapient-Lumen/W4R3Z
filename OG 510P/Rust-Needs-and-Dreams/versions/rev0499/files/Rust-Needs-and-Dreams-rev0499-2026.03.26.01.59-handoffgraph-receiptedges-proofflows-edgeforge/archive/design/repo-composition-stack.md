# Design: Repo Composition Stack (Workspace Governance + Config Set + Build Interop)

## Goal
Treat **repo composition** as an ecosystem seam in its own right.

Rust repos do not just need better build speed or prettier workspace docs. They need one reviewable story for:
- **discovery** — which workspace and config layers Cargo found,
- **governance** — which inherited/effective values actually apply,
- **selection** — which packages/configurations are in scope for a given lane,
- **handoff** — which tools consume that scope next.

The archive should therefore stop treating workspace governance, config matrices, and build discovery as unrelated conveniences. Together they form a reusable stack for monorepos, split workspaces, CI, docs, editors, wrappers, and release pipelines.

With **Discovery Boundary Kit** now explicit, this stack should stop letting raw invocation/root/config-walk truth hide inside later workspace/build explanations. Repo Composition should compose discovery, governance, bounded config sets, and build interop instead of re-owning discovery as an implementation detail.

## Why this seam matters now
Official Cargo signals are increasingly saying the same thing from different angles:
- Cargo config is hierarchical and parent-directory sensitive, so discovery itself can change behavior.
- Cargo 1.94 explicitly called out workspace/config discovery as a live design problem because stray parent `Cargo.toml` or `.cargo/config.toml` files can break unrelated work.
- Cargo 1.93 resumed work on `-Zconfig-include`, and Cargo 1.94 stabilized the config `include` key, including optional includes and defined merge order. That makes config layering more expressive and therefore more deserving of explanation.
- Workspace semantics now include `default-members`, `workspace.package`, `workspace.dependencies`, `workspace.lints`, and tool-facing `workspace.metadata`.
- `cargo metadata` now includes `workspace_default_members`, which means package-selection truth is becoming machine-readable instead of purely implicit, even if the metadata format remains an explicitly versioned consumer interface.
- The accepted Cargo plumbing goal says Cargo’s current machine-facing surface is still too porcelain-oriented, and Cargo’s 1.90 development-cycle report says the `cargo-plumbing` prototype still had to re-read manifests within commands because Cargo’s current Rust APIs were not yet exposing the right structure. That makes a stack of companion artifacts more realistic than waiting for one built-in mega-command.


## References (signals)
- Cargo configuration reference (hierarchical parent-directory probing): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspaces reference (`default-members`, `package.workspace`, inherited workspace tables, `workspace.metadata`): https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo changelog / release notes (`workspace_default_members` in `cargo metadata`, auto-inherit workspace fields in `cargo new` / `cargo init`, stabilized config `include`): https://doc.rust-lang.org/cargo/CHANGELOG.html ; https://doc.rust-lang.org/beta/releases.html
- `cargo locate-project`: https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html
- `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo 1.90 dev-cycle note (`cargo-plumbing` prototype and API limitations): https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- Cargo 1.93 dev-cycle note (`-Zconfig-include` progress): https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo 1.94 dev-cycle note (workspace/config discovery discussion): https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Accepted Cargo plumbing goal (discovery / read / lock / resolve / plan / execute / stage phases): https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html

## Current archive decision
The right contribution is **not** a new universal monorepo manager.
It is a stack with explicit boundaries:
- [`design/discovery-boundary-kit.md`](./discovery-boundary-kit.md) owns invocation subject, manifest walk, workspace attachment, config discovery, and consumer-import lossiness.
- [`design/workspace-governance-kit.md`](./workspace-governance-kit.md) owns effective inheritance, ignored/shadowed settings, and package-selection explanation after discovery.
- [`design/config-set-kit.md`](./config-set-kit.md) owns bounded matrices for actual work lanes (check/test/doc/coverage/fuzz/release).
- [`design/build-interop-kit.md`](./build-interop-kit.md) owns machine-facing graph/plan/event exports for tools that sit around Cargo.

## What a worthy contribution would look like in practice
### 1) Start with paired artifacts, not a new mega-schema
Use existing artifacts as the canonical pieces:
- `discovery-pack/v0`
- `workspace-report/v0`
- `config-set/v0`
- `config-analysis-report/v0`
- optional raw discovery attachments (`cargo metadata`, config-layer captures, `--unit-graph` or interop attachments where needed)

Only add a tiny glue bundle if needed, e.g. `repo-compose-pack/v0`, and even then keep it as a bundle of linked truths rather than a giant normalized super-schema.

### 2) Make package selection first-class
A credible repo-composition contribution must say:
- what the full workspace is,
- what `default-members` says,
- what command/package flags changed,
- what the working directory implied,
- and what bounded config matrix was actually selected downstream.

Without that, CI and editor integrations keep guessing wrong while still claiming to represent “the workspace”.

### 3) Keep discovery boundaries visible
The stack must expose when behavior came from:
- repo manifest/workspace structure,
- parent config files,
- user config files,
- `package.workspace` attachment/override,
- generated tool inputs.

This matters because the current Cargo pain is not only “inheritance is confusing”; it is also “the wrong root or config got discovered”.

### 4) Prefer import/export seams over tool replacement
The stack should help:
- CI generators,
- editors / rust-analyzer-adjacent tools,
- policy/release/perf consumers,
- non-Cargo build bridges,
- docs and test lanes.

It should not try to become a new build system, new workspace format, or one tool that owns every repo decision.

## Shared success criteria
A strong repo-composition contribution should let a reviewer answer five questions quickly:
1. Which workspace did Cargo think this repo belongs to?
2. Which packages were in scope by default and why?
3. Which settings were inherited, ignored, or shadowed?
4. Which bounded configurations did we actually run or plan to run?
5. Which downstream tools consumed that exact scope, and which discovery facts did they import or lose?

If the stack cannot answer those questions, it is not yet ecosystem infrastructure.

## Ranked opportunity inside this stack
1. **Workspace explanation and diffing**
2. **Discovery-boundary diagnostics**
3. **Package-selection / `default-members` truth**
4. **Import into bounded config matrices**
5. **Tool/export consumers**

That order matters. The archive should not jump straight to “one repo format for all tools”.


Treat [`proposals/epic-repo-composition-stack.md`](../proposals/epic-repo-composition-stack.md) as the stack-level product-direction candidate: a thin `cargo repo-compose` / `repo-compose-pack/v0` layer above Workspace Governance + Config Set + Build Interop rather than a monorepo manager, repo daemon, or universal repo manifest format.

## Boundaries / non-goals
- not a replacement for Cargo workspaces
- not a replacement for Cargo config
- not a universal CI generator
- not a universal monorepo policy engine
- not a single giant `cargo compose` fantasy command

## Why this is an ecosystem contribution, not just big-company tooling
Smaller Rust repos also hit the same seam whenever docs, tests, examples, editors, release lanes, and package-selection defaults drift apart. Large repos make the pain louder, but the missing contract is broadly reusable.
