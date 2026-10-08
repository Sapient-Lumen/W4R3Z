# Epic Proposal: Repo Composition Stack (`cargo repo-compose` + `repo-compose-pack/v0`)

## One-sentence pitch
Make Rust repo scope boring by standardizing a portable layer that records **what Cargo discovered, which workspace/config layers applied, which packages were actually in scope, and which downstream tools consumed that exact scope** without pretending those facts are the same thing as dependency resolution, build execution, or repo policy.

## Deliverables
- reference command:
  - `cargo repo-compose`
- schemas:
  - `workspace-report/v0`
  - `workspace-diff/v0`
  - `scope-selection-report/v0`
  - `tool-import-report/v0`
  - `repo-compose-pack/v0`
  - `repo-compose-handoff/v0`
- adapters/importers for:
  - `cargo locate-project`
  - `cargo metadata --format-version=1`
  - discovered `.cargo/config.toml` layer captures
  - `config-set/v0`
  - optional build-interop / plumbing attachments
  - editor / CI / docs / release / outer-build import profiles
- docs:
  - discovery-boundary guide
  - `default-members` / cwd / explicit-package-selection guide
  - parent-config interference guide
  - mixed-workspace / mixed-build adapter guide
  - consumer-lossiness guide

## Why now (signals)
- Cargo’s configuration reference says configuration is hierarchical across the current directory, all parent directories, and `$CARGO_HOME`, which means discovery itself changes behavior.
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo’s workspaces reference says Cargo searches upward for `[workspace]`, allows `package.workspace` to override that search, and uses `default-members` at the workspace root when package-selection flags are absent. Workspace inheritance now includes `workspace.package`, `workspace.dependencies`, `workspace.lints`, and tool-facing `workspace.metadata`.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo 1.94 explicitly called workspace/config discovery a live design problem, including broken parent manifests/config files and the idea of a `package.workspace = false`-style opt-out to avoid walking the directory tree.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo 1.93/1.94 made config layering more real, not less. The config `include` key is now stabilized, and the docs describe optional includes and merge-order behavior. That raises the value of explanation and diffing.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  https://doc.rust-lang.org/cargo/CHANGELOG.html
  https://doc.rust-lang.org/cargo/reference/config.html
- `cargo locate-project` and `cargo metadata` are useful but still partial: locate-project reports manifest/root discovery, while metadata is explicitly versioned and warns consumers to pin `--format-version` because the output evolves.
  https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- The accepted Cargo plumbing goal is explicit that Cargo’s machine-facing surfaces remain too porcelain-oriented and that build work naturally splits into phases like locate project, read manifests, lock dependencies, resolve features, plan, execute, and stage.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo’s 1.90 development-cycle report says the `cargo-plumbing` prototype had to re-read manifests within commands because Cargo’s current Rust APIs did not yet expose everything cleanly enough. That is strong evidence the ecosystem still lacks a clean repo-composition boundary.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

## Non-goals
- replacing Cargo workspaces, Cargo config, or repo layout conventions;
- becoming a universal monorepo manager or CI generator;
- pretending one repo/workspace report can replace graph/build/run evidence;
- hiding parent-config interference or selection drift behind a fake “effective workspace” badge;
- forcing one schema on non-Cargo tools instead of preserving adapter lossiness.

## Strategic value
This deserves promotion because it gives the archive a missing **scope continuity seam**.
With it:
- CI, editors, docs, release tooling, and wrappers can import the same selected-repo truth instead of re-deriving it;
- repo reviews can diff discovery and selection changes without rerunning builds just to understand scope;
- manifest/distribution/release/policy stacks get a cleaner import boundary for “what repo state was actually in play”;
- mixed-build environments can state exactly where Cargo-native truth ends and adapter approximations begin.

The prize is not a prettier workspace page.
The prize is a durable record of **what Cargo discovered, what governance applied, what package/config scope was chosen, and who consumed that scope next**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. make `workspace-report/v0` the canonical discovery/governance artifact for workspace roots, members, inheritance, ignored settings, and `default-members` posture;
2. make `scope-selection-report/v0` the canonical artifact for `cwd`, explicit `-p` / `--workspace`, default-member selection, policy-selected subsets, and bounded matrix handoff;
3. make `tool-import-report/v0` the canonical consumer artifact for editors, CI, docs, release, and outer-build tools, including explicit lossiness;
4. use `workspace-diff/v0` for PR/review-friendly drift across branches or revisions;
5. emit `repo-compose-pack/v0` and `repo-compose-handoff/v0` so downstream stacks can import scope truth instead of silently rebuilding it.

## Critical design bet
The critical bet is that **repo composition becomes useful as a review boundary before Cargo grows one universal built-in discovery/plumbing interface**.
That means:
- stable docs/commands can already anchor the basic contract,
- experimental/plumbing/build-interop lanes can attach explicitly,
- mixed-build adapters can report lossiness instead of pretending to be Cargo,
- and adjacent stacks can already stop guessing which repo/package scope they actually consumed.

Without that boundary, the stack either stays too vague to matter or bloats into a fake build-system replacement.

## Milestones
1. **v0 workspace truth lane**
   - `workspace-report/v0`
   - root/member/default-members/inheritance explanation
2. **v0.2 discovery-boundary lane**
   - config-layer capture
   - parent-file interference reports
   - explicit auto-search vs `package.workspace` posture
3. **v0.3 selection + matrix lane**
   - `scope-selection-report/v0`
   - import/export with `config-set/v0`
4. **v0.4 consumer lane**
   - editor / CI / docs / release / outer-build `tool-import-report/v0`
   - adapter-lossiness notes
5. **v1 handoff lane**
   - `repo-compose-pack/v0`
   - downstream imports for Manifest Truth, Tooling Contract, release/docs/support/policy consumers

## Execution order
Use [`design/repo-composition-pilot-program.md`](../design/repo-composition-pilot-program.md) as the stack-level rollout:
1. workspace truth lane,
2. discovery-boundary lane,
3. package-selection / `config-set` handoff lane,
4. tool/export consumer lane,
5. mixed-build / cross-tool lane.

Use [`design/workspace-governance-kit.md`](../design/workspace-governance-kit.md), [`design/config-set-kit.md`](../design/config-set-kit.md), and [`design/build-interop-kit.md`](../design/build-interop-kit.md) as the leaf-level substrates beneath it.

## Success metrics
- reviewers can answer which workspace/config scope Cargo saw without reverse-engineering shell context;
- teams can diff selection drift caused by `cwd`, `default-members`, explicit flags, or policy changes;
- at least two downstream consumers can import the same scope truth without scraping command output differently;
- mixed-build adapters can declare their lossiness instead of quietly inventing repo semantics;
- the ecosystem gets one explainable scope-continuity seam instead of many incompatible “what repo did we just build?” stories.
