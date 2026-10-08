# Design: Workspace Governance Kit (`cargo workspace doctor`, `workspace-report/v0`)

## Goal
Make large Rust repos easier to understand and evolve by exporting **reviewable repo-composition truth**:
- which workspace Cargo discovered,
- which packages are selected by default,
- which workspace/package/config layers contributed effective settings,
- which member-local settings are ignored or shadowed,
- and where nested or split-workspace setups become ambiguous.

This is still a companion kit, not a replacement for Cargo. The point is to make Cargo’s current and emerging workspace semantics explainable and diffable for humans, CI, editors, and adjacent tools.

With **Discovery Boundary Kit** now explicit in the archive, this kit should import raw invocation / manifest-walk / workspace-attachment / config-discovery facts from `discovery-pack/v0` or equivalent attachments rather than quietly re-owning discovery as if it were identical to governance.

## Why now
Recent Cargo signals make this more urgent and more practical than when the archive first added the kit:
- workspace inheritance is expanding beyond dependencies into `workspace.package` and `workspace.lints`;
- `cargo metadata` now exposes `workspace_default_members`, which means package-selection truth is increasingly machine-consumable;
- `cargo new` / `cargo init` now inherit workspace fields automatically, so repo scaffolding itself participates in workspace governance;
- Cargo 1.94 explicitly called out **workspace and configuration discovery** as a design discussion because broken parent `Cargo.toml` or `.cargo/config.toml` files can interfere with unrelated workspaces;
- Cargo 1.93 revived `-Zconfig-include` work, which means the config-layer story is becoming more expressive and therefore more in need of explanation.

## References (signals)
- Workspaces reference (`default-members`, `package.workspace`, `workspace.package`, `workspace.dependencies`, `workspace.lints`, `workspace.metadata`): https://doc.rust-lang.org/cargo/reference/workspaces.html
- Profiles reference (root-workspace-only profile settings): https://doc.rust-lang.org/cargo/reference/profiles.html
- Configuration reference (hierarchical `.cargo/config.toml` probing through parent directories and `$CARGO_HOME`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo 1.71 release/changelog (`workspace_default_members` in `cargo metadata`, auto-inherit workspace fields in `cargo new` / `cargo init`): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo 1.93 dev-cycle note on inheritance framing and a possible workspace `edition`: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo 1.94 design discussion on workspace/config discovery, parent-file interference, and possible `package.workspace = false`-style opt-out: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Nested workspaces design notes: https://hackmd.io/%40rust-cargo-team/H1Oa5ILxj
- Profiles confusion issue: https://github.com/rust-lang/cargo/issues/15262

## Core UX: `cargo workspace doctor`
- `cargo workspace doctor`
  - summarize discovered workspace root, package-selection basis, members, nested-workspace structure, and effective governance values per package.
- `cargo workspace explain <package>`
  - show why each effective setting is what it is:
    - source: root workspace / nested workspace / package manifest / config layer / default
    - override or inheritance chain
    - whether the setting is active, ignored, or only advisory.
- `cargo workspace discover`
  - print the discovery chain Cargo walked:
    - parent `Cargo.toml` files considered,
    - parent `.cargo/config.toml` files considered,
    - whether a nightly-only or broken parent file influenced discovery,
    - whether the package is attached through auto-discovery or explicit `package.workspace`.
- `cargo workspace diff <A> <B>`
  - diff two `workspace-report/v0` artifacts (PR vs main):
    - behavioral changes in package selection,
    - changes in effective lints, profiles, inherited package fields, dependency inheritance, and discovery roots.
- `cargo workspace lint`
  - run high-value governance checks:
    - member profile ignored,
    - ambiguous nested-workspace membership,
    - package selected unexpectedly because of `default-members`,
    - discovery affected by parent config / manifest files,
    - missing `lints.workspace = true`,
    - workspace/package metadata drift where the repo expected tool inheritance.

## Report artifact: `workspace-report/v0`
A portable JSON report with five distinct truth layers.

### 1) Discovery (usually imported from `discovery-pack/v0`)
- invocation directory
- discovered workspace root
- discovery chain for parent manifests/config files
- explicit `package.workspace` overrides if present
- config-layer files considered
- toolchain / channel / Cargo version

### 2) Membership and package selection
- full member list
- nested-workspace structure if any
- root package presence / virtual-workspace posture
- `default-members` declaration
- effective selected members for common command lanes
- source of package selection (`cwd package`, `default-members`, `--workspace`, explicit package list, tool import)

### 3) Effective governance values by package
- inherited package fields
- dependency inheritance sources
- effective lints (including workspace opt-in status)
- effective profile posture and warnings about ignored member profiles
- future-compatible slot for workspace-edition-like semantics if upstream lands them

### 4) Diagnostics
Reason-coded findings such as:
- `NON_ROOT_PROFILE_IGNORED`
- `NESTED_WORKSPACE_CONFLICT`
- `INHERITANCE_AMBIGUOUS`
- `DISCOVERY_PARENT_FILE_INTERFERENCE`
- `DEFAULT_MEMBERS_SURPRISE`
- `LINTS_NOT_INHERITED`
- `WORKSPACE_METADATA_FALLBACK_IN_USE`

### 5) Attachments / imports
- optional raw `cargo metadata` snapshot hash
- optional config-layer attachments
- optional imported `config-set/v0` ids for downstream execution lanes
- optional policy / support / perf consumer links

## Integration points
- **Config Set Kit:** import discovered package-selection truth and emit bounded execution matrices instead of guessing workspace scope from CI YAML.
- **Build Interop Kit:** share discovery-root and selection truth with editors, wrappers, and non-Cargo build-system bridges.
- **Policy Kit:** treat workspace governance drift as a policy decision point.
- **Perf Labs / Cargo Report Kit:** correlate profile and package-selection changes with rebuild or perf differences.
- **Compile-Time Capabilities Kit:** keep build-dependency and proc-macro governance visible instead of flattening them into ordinary package config.

## What this kit should provide to others
- a stable explanation layer for large repos,
- diffable workspace-governance evidence in PR review,
- explicit discovery-root and package-selection truth for tools,
- a bridge between Cargo-native semantics and repo-local policy,
- a place to record current sharp edges honestly while upstream behavior evolves.

## Hard problems (explicitly scoped)
1. **Discovery and governance are related but not identical**
   - a repo can have correct inheritance rules yet still surprise users because a parent manifest or config file changed discovery.
2. **Package selection is part of repo composition truth**
   - `default-members`, root-package behavior, and working-directory defaults can change what commands act on even when manifests are unchanged.
3. **Config layers are not just local repo files**
   - user and parent-directory config files matter; the tool must expose them without pretending it owns their semantics.
4. **Nested workspaces are real even if upstream UX is still evolving**
   - the archive should model ambiguity and conflict honestly rather than waiting for one final upstream answer.
5. **This kit must not become a fake universal policy engine**
   - it should export evidence and warnings, not silently choose governance for every repo.

## Minimal adoption path
1. export `workspace-report/v0` with discovery, membership, default-members, and profile/lint warnings.
2. add `cargo workspace explain` and `cargo workspace diff` with concrete fix suggestions.
3. import config-layer and `cargo metadata` attachments for better provenance.
4. add `config-set/v0` handoff for CI/test/doc/release consumers.
5. only after that, widen into editor/build-system/export lanes and upstream-facing proposals.
