---
id: P-0055
title: Cargo Workspace Toolchain Manifest Kit — workspace-scoped tool dependencies, tool-route receipts, and install-root contracts
status: idea
domains: [cargo, devtools, reproducibility, workspace, policy, ux]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
  - https://doc.rust-lang.org/cargo/commands/cargo-install.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://rust-lang.github.io/rustup/overrides.html
  - https://rust-lang.github.io/rustup/concepts/proxies.html
  - https://rust-lang.github.io/rustup/concepts/components.html
  - https://github.com/rust-lang/cargo/issues/2267
  - https://docs.rs/cargo-run-bin/latest/cargo_run_bin/
  - https://docs.rs/crate/cargo-binstall/latest
---

# Problem

Rust teams keep accumulating an awkward gap around **tooling that is itself shipped as crates**:

- formatters,
- linters,
- generators,
- release helpers,
- test runners,
- and other `cargo-*` subcommands.

Cargo already has real substrate here:

- `cargo install` installs binaries into an installation root and treats that flow as a **system/user-level** command rather than a project-level one;
- installed executables land in the chosen root’s `bin` directory;
- Cargo custom subcommands are resolved from external executables such as `cargo-nextest` on the user’s path;
- Cargo defaults to preferring `$CARGO_HOME/bin` over the rest of `$PATH` for external subcommands;
- rustup directory overrides, `rust-toolchain.toml`, and `cargo +toolchain ...` all change the actual toolchain context in which those tools run;
- and by default `cargo install` ignores the packaged `Cargo.lock` unless `--locked` is requested.

That is useful substrate, but it still leaves ordinary teams with major missing workflow questions:

- how do we pin *workspace-local* tool dependencies without telling contributors to globally install random binaries,
- how do we keep install roots and runner shims reviewable,
- how do we prove **which exact executable actually ran** when a requested command name could resolve to multiple copies,
- how do we keep tool installation policy separate from rustup toolchain policy,
- how do we support “clone repo, sync tools, run commands” without pretending Cargo already has a first-class workspace tool dependency model,
- and how do we compare two CI/local runs without flattening `cargo install`, prebuilt-binary installers, workspace wrappers, and rustup overrides into one fake “same tool” story?

The missing crate is not just “another cargo plugin” and not just another binary downloader.
The missing crate is a **Cargo Workspace Toolchain Manifest Kit**: a crate and cargo-adjacent tool that gives workspaces a durable manifest, lock, install-root, and route-receipt layer for crate-shipped developer tools.

## 2026-03-23 implementation refresh — command authority, component availability, and fallback ceilings

Current rustup and Cargo docs make three additional review objects worth promoting.

### 1. Command authority needs to be first-class

Cargo external subcommands, rustup proxies, workspace-managed executables, and PATH fallbacks are not the same support surface.
Current docs are explicit enough that a worthy crate should promote **`command-authority.receipt.json`** into first-class status.

### 2. Component availability needs to stay separate from route resolution

Optional rustup components vary by toolchain and installation state.
A command can run while the expected rustup component is missing, irrelevant, or substituted by a fallback path.
A worthy crate should therefore promote **`component-availability.report.json`** into first-class status.

### 3. Fallback ceilings need to stay visible

The rustup 1.29 `rust-analyzer` fallback and Cargo’s `cargo-*` path resolution rules both make it possible for “the tool worked” to overclaim what kind of support actually existed.
A worthy crate should therefore promote **`fallback-ceiling.report.json`** and join it into one portable **`tool-support-bundle.manifest.json`**.

# Main judgment

This is worthy because it solves a broad, recurring seam across Rust teams:

- onboarding contributors without global tool drift,
- pinning formatter/linter/generator versions per repository,
- keeping CI and local runs aligned,
- making `cargo-*` plugin use reviewable,
- separating **workspace tool dependencies** from **rustup compiler/toolchain support policy**,
- and exposing whether a run went through a workspace-managed binary, a global `$CARGO_HOME/bin` install, some other `$PATH` entry, or a manual override.

The missing value is not one more installer.
The missing value is **workspace-scoped tool intent with receipts**.

# What it provides

- `Toolchain.toml` — declares workspace tool dependencies, requested commands, optional aliases, install strategy preferences, required features, and runner policy.
- `toolchain.lock` — records resolved tool package, exact version, source identity, selected binary, install strategy, target/profile, and digest facts when known.
- `tool-sync.plan.json` — a dry-run plan for what would be installed, where it would go, and why that version/source/strategy was selected.
- `install-root.receipt.json` — records the chosen root, whether it is workspace-local, shared, cargo-home-backed, ephemeral, or custom, plus collision and cleanup posture.
- `tool-route.receipt.json` — records the requested command, the resolved executable path, route class, source identity, why that route won, and which shadowing candidates existed.
- `tool-run.receipt.json` — records which exact executable was invoked, what rustup/toolchain context was active, and the arguments/environment policy used.
- `command-authority.receipt.json` — records whether a request was satisfied by a rustup proxy/component lane, Cargo external-subcommand lane, workspace-managed executable, or PATH fallback.
- `component-availability.report.json` — records what toolchain/context was checked for an expected component and whether that component was installed, merely available, missing, or irrelevant.
- `fallback-ceiling.report.json` — records where PATH fallback, cargo-home precedence, or toolchain drift stop stronger support claims.
- `tool-upgrade.diff.json` — compares two lockfiles or receipts and classifies `tool_added`, `tool_removed`, `source_changed`, `binary_changed`, `route_changed`, `install_root_changed`, and `toolchain_context_changed`.
- `cargo toolchain sync` — install or verify the workspace toolset into the configured root.
- `cargo toolchain run <tool> -- ...` — invoke a pinned tool through a runner shim while writing a route + run receipt.
- `cargo toolchain doctor` — diagnose missing tools, root collisions, path-shadowing, route drift, or rustup/tool-run mismatch.
- `tool-support-bundle.manifest.json` — keeps install-root posture, command authority, component availability, run receipts, and fallback ceilings distinct inside one portable bundle.
- `*.toolchainbundle.zip` — a portable artifact for CI, onboarding, and support tickets.

# What the crate should provide other people

1. **A boring workspace manifest** for tools that are currently managed by README folklore.
2. **A lockfile** for crate-shipped dev tools, separate from application dependency locks.
3. **Install-root receipts** so shared/global/local placement stops being implicit.
4. **Command-authority receipts** so reviewers can see whether a request was satisfied by a rustup component proxy, Cargo subcommand, workspace binary, or PATH fallback.
5. **Component-availability reports** so toolchain-specific optional component posture is reviewable.
6. **Fallback-ceiling reports** so “the tool ran” does not overclaim workspace governance or component parity.
7. **Runner receipts** so the active rustup/toolchain context for a run is reviewable.

# Persona / who it’s for

- workspace maintainers
- OSS projects with contributor tooling
- CI and developer-experience engineers
- teams shipping custom `cargo-*` subcommands internally
- polycrate repos that need pinned generators or linters

# Users & user stories

- **Maintainer**: “I want contributors to sync our formatter, linter, and generator versions without global installs.”
- **Contributor**: “I want one command that installs the right repo tools into an isolated root and tells me what happened.”
- **CI owner**: “I want cacheable, pinned tool installs and a receipt for the exact binary that ran.”
- **Reviewer**: “I want to know whether this command used a workspace-pinned binary, some global binary in `$PATH`, or a rustup component.”
- **Tool author**: “I want my `cargo-*` subcommand to fit into a boring workspace-managed runner flow.”

# Prior art (and why it’s insufficient)

- `cargo install` is the core substrate, but it is intentionally a user/system-level install command rather than a project-scoped tool dependency model.
- Cargo custom subcommands are real and useful, but the external-tools docs describe discovery and invocation, not workspace pinning, root isolation, or run receipts.
- rustup toolchain files and overrides already pin compiler/channel/components/targets, but that is a different problem from pinning *crate-shipped auxiliary tools*.
- `cargo-run-bin` shows there is real demand for locked, per-project execution of crate-shipped tools, but it does not try to become the general workspace manifest / install-root / route-authority layer.
- `cargo-binstall` shows there is real demand for alternate installation strategies and fast binary acquisition, but it is still an installer substrate rather than a workspace-scoped provenance contract.
- Teams can improvise shell scripts, Makefiles, or ad hoc wrappers, but those usually leave source/version/root/provenance implicit.

What remains missing is the **manifest + lock + install-root + route-receipt** layer above `cargo install` and beside rustup.

# Design goals

1. **Workspace-first** — the core unit is a repository’s toolset, not one user’s global install collection.
2. **Root-explicit** — installation location and collision policy must be first-class.
3. **Authority-honest** — keep rustup proxies, Cargo subcommands, workspace binaries, and PATH fallbacks distinct.
4. **Toolchain-aware** — preserve the active rustup context without turning into a rustup replacement.
5. **Fallback-explicit** — record when a successful run still fails to prove component parity or workspace governance.
6. **Strategy-pluggable** — support source-install, prebuilt-binary, or local-path strategies through adapters.
7. **Receipt-friendly** — optimize for review, CI support, and onboarding artifacts.

# MVP surface

- Minimal types: `WorkspaceToolManifest`, `WorkspaceToolLock`, `ToolSyncPlan`, `InstallRootReceipt`, `ToolRouteReceipt`, `ToolRunReceipt`, `CommandAuthorityReceipt`, `ComponentAvailabilityReport`, `FallbackCeilingReport`, `ToolUpgradeDiff`, `ToolchainBundle`
- Minimal functions:
  - `load_workspace_tool_manifest()`
  - `resolve_workspace_tools()`
  - `plan_tool_sync()`
  - `materialize_tool_root()`
  - `resolve_tool_route()`
  - `capture_command_authority()`
  - `inspect_component_availability()`
  - `compute_fallback_ceiling()`
  - `run_workspace_tool()`
  - `diff_tool_locks()`
- Feature flags:
  - `cargo`
  - `serde`
  - `runner`
  - `rustup-context`
  - `binstall-adapter`
  - `ci`

# Compatibility story

- Stable Cargo first for planning, root selection, and route/run receipts.
- Works with source installs first; binary-install adapters can remain optional.
- Must preserve rustup context because `cargo +toolchain ...` and `rust-toolchain.toml` overrides change the execution environment.
- Must keep rustup proxy/component lanes distinct from Cargo external-subcommand lanes and PATH fallback lanes.
- Must preserve rustup 1.29-style PATH fallback observations without upgrading them into “component installed” claims.
- Must not assume every workspace wants tools in `$CARGO_HOME/bin`; isolated roots should be a first-class option.
- Must keep `$CARGO_HOME/bin` precedence and manual PATH shadowing visible rather than quietly “fixing” them behind the user’s back.

# Conformance & fixtures

- One fixture for a workspace-local tool root with formatter + linter pins.
- One fixture where `rust-analyzer` falls back to a PATH binary because the rustup-managed one is absent.
- One fixture where a `cargo-*` plugin in `$CARGO_HOME/bin` would shadow a workspace-managed or system copy.
- One fixture where the expected `rustfmt` component changes with toolchain selection context.
- One fixture where the same resolved binary still needs a different receipt because a rustup override changed the toolchain context.
- Goldens for `route_changed`, `install_root_changed`, `component_missing`, `path_fallback_observed`, `shadowing_detected`, and `toolchain_context_changed`.

# Path to boring stability

- Freeze manifest, lock, install-root, and route-receipt vocabulary before fancy TUI/editor integration.
- Start with read-only `plan` and explicit `sync` rather than magical auto-install.
- Prefer explicit install roots and wrappers over mutating a user’s global Cargo home by default.
- Treat rustup/compiler context as imported facts, not as something this crate owns.
- Prefer `manual_review_required` over pretending every route/source can be inferred perfectly.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that read a workspace tool manifest, resolve/install pinned crate-shipped tools into an isolated root, generate a lockfile, and emit install-root, command-authority, component-availability, and fallback-ceiling artifacts whenever a pinned tool is synced or invoked.

# De-risk plan

1. Start with workspace-local roots and report-only planning.
2. Support a tiny manifest vocabulary before adding aliases, groups, or remote policy packs.
3. Add rustup-context capture and command-authority classification early so “it worked on my machine” reports are explainable.
4. Keep binary-install adapters optional until the manifest and receipt shapes settle.
5. Keep shadowing/collision detection and fallback ceilings explicit instead of auto-rewriting PATH.

# Non-goals

- Not a replacement for rustup.
- Not a general-purpose package manager.
- Not a promise that every external tool should be installed this way.
- Not a new Cargo subcommand discovery mechanism.
- Not a hidden PATH mutator that silently rewrites the user’s shell environment.

# Architecture & API sketch

```rust
pub struct ToolRouteReceipt {
    pub requested_name: String,
    pub resolved_executable_path: String,
    pub route_class: RouteClass,
    pub install_root_class: InstallRootClass,
    pub source_id: String,
    pub rustup_context: Option<String>,
}

pub struct CommandAuthorityReceipt {
    pub requested_command: String,
    pub authority_class: AuthorityClass,
    pub support_class: SupportClass,
    pub route_summary: Vec<String>,
}

pub fn plan_tool_sync(root: &Path, manifest: &WorkspaceToolManifest) -> Result<ToolSyncPlan>;
pub fn resolve_tool_route(root: &Path, tool: &str) -> Result<ToolRouteReceipt>;
pub fn capture_command_authority(root: &Path, tool: &str) -> Result<CommandAuthorityReceipt>;
pub fn inspect_component_availability(root: &Path, tool: &str) -> Result<ComponentAvailabilityReport>;
pub fn compute_fallback_ceiling(root: &Path, tool: &str) -> Result<FallbackCeilingReport>;
pub fn run_workspace_tool(root: &Path, tool: &str, args: &[String]) -> Result<ToolRunReceipt>;
```

# Maintenance & governance plan

- Keep the manifest and receipt schemas compact and versioned.
- Maintain adapters to Cargo install flows and optional binary-install backends as thin layers.
- Keep rustup-context capture conservative and observational.
- Prefer fixture-driven compatibility tests across Linux/macOS/Windows.
- Keep route/preference policy overrideable by the workspace so the crate reports policy rather than hard-coding one community norm.

# Adoption plan

1. Start as a standalone cargo subcommand and library.
2. Prove value on formatter/linter/generator/test-runner workflows.
3. Add CI recipes and workspace-local root defaults.
4. Add optional adapters for `cargo-binstall` / prebuilt-binary acquisition without making them the default truth surface.
5. Only later consider tighter integration with install-policy crates.

# Open questions

- Best default root: workspace-local, shared user cache, or CI-specific ephemeral root?
- How opinionated should runner shims be about PATH mutation?
- Should `Toolchain.toml` stay separate from Cargo manifest metadata indefinitely?
- How much source/binary strategy choice belongs here versus in install-policy crates?
- Should this crate ever expose a `cargo foo` alias surface, or stay on explicit `cargo toolchain run foo -- ...` boundaries?

# Sources

See front matter links.
