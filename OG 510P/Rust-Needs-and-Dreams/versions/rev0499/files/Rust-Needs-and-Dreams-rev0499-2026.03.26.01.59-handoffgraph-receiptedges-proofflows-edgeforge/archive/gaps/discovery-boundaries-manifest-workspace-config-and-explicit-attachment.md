# Gap: Cargo discovery truth is still smeared across manifests, parent walks, workspace attachment, config layers, and consumer guesses

## Summary
Rust repos increasingly need a clear answer to a deceptively small question:
**what exactly did Cargo discover, from where, and why?**

Today that answer is still spread across several partial surfaces:
- upward manifest search from the current directory,
- upward workspace attachment via `[workspace]` or `package.workspace`,
- hierarchical `.cargo/config.toml` discovery through parent directories and `$CARGO_HOME`,
- command-level package-selection defaults that depend on where invocation started,
- and consumer-specific imports like `cargo locate-project`, `cargo metadata`, editor discovery hooks, or wrapper-local path guessing.

That is enough to make Cargo work, but not enough to make discovery **portable, reviewable, and diffable**.

## Ecosystem signals
- Cargo configuration is explicitly hierarchical: Cargo looks for config files in the current directory and all parent directories, then merges them with broader config layers. That means discovery is not just "find a manifest"; it also includes a config walk with behavioral consequences.
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspace semantics explicitly search parent directories for a `[workspace]` root, allow `package.workspace` to override that search, and make default package selection depend on whether invocation happened at a member or at the workspace root.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/cargo/reference/manifest.html
- `cargo locate-project` makes the split visible: it first searches upward for a `Cargo.toml`, and the workspace root is then found by traversing further upward or by using `package.workspace`.
  https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html
- Cargo commands like `cargo build` and `cargo metadata` still default to searching for `Cargo.toml` in the current directory or parent directories, and command-level working-directory changes also affect `.cargo/config.toml` discovery. That means invocation path is a real input, not just UI sugar.
  https://doc.rust-lang.org/cargo/commands/cargo-build.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo’s 1.94 development-cycle report says broken or nightly-only parent `Cargo.toml` or `.cargo/config.toml` files can break unrelated projects, suggests possible opt-out controls such as `package.workspace = false`, and notes that `cargo-script` is starting with workspace auto-discovery disabled. That is a direct signal that discovery is now a first-class design problem, not just incidental behavior.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The accepted Cargo plumbing goal starts the build pipeline with **Locate project** and **Read the manifests for a workspace**, and ends much later with planning, executing, and staging artifacts. That is a strong hint that discovery deserves a narrower public boundary instead of being repeatedly re-described inside every later layer.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo’s 1.90 development-cycle report says the `cargo-plumbing` prototype still had to re-read manifests within commands because Cargo’s Rust APIs were not yet exposing enough structure. That means discovery truth is still hard to import cleanly, even for tooling explicitly trying to build above Cargo.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

## What is missing
The missing contribution is a thin **Discovery Boundary Kit** that keeps five truths explicit and linked without pretending they are already one stable built-in Cargo report:
1. invocation subject truth (cwd / `--manifest-path` / explicit working-directory shifts / caller intent),
2. manifest-discovery walk truth,
3. workspace-attachment truth,
4. config-discovery truth,
5. consumer-import / lossiness truth.

## What "good" looks like
- A report that can say exactly which path or manifest was the starting subject.
- A reviewable manifest walk showing what parent manifests were considered and why a candidate was accepted, ignored, or rejected.
- A reviewable workspace-attachment explanation showing auto-discovery, explicit `package.workspace`, or explicit opt-out posture.
- A config-discovery report that shows which config files were considered, merged, skipped, or merely inherited from broader scope.
- Explicit separation between **discovery truth** and later **governance/selection/build-plan** conclusions.
- Consumer-import notes that say what `cargo locate-project`, `cargo metadata`, rust-analyzer, CI wrappers, or script runners imported or lost.

## Candidate contribution
Promote a **Discovery Boundary Kit** with:
1. `discovery-subject/v0` for invocation and path-intent truth,
2. `manifest-discovery-report/v0` for manifest search walks,
3. `workspace-attachment-report/v0` for auto/override/opt-out posture,
4. `config-discovery-report/v0` for config-layer search and merge provenance,
5. `discovery-consumer-import-report/v0` for tool-specific imports/lossiness,
6. `discovery-pack/v0` for the linked portable bundle.

## Distinction from nearby archive entries
- **Not Workspace Governance Kit:** that kit should own effective inheritance, ignored/shadowed settings, nested-workspace ambiguity, and package-selection explanation after discovery.
- **Not Repo Composition Stack:** that stack should compose Discovery Boundary + Workspace Governance + Config Set + Build Interop into a larger repo story.
- **Not Build Interop Kit:** that kit should own machine-facing graph/plan/event exports and editor/build-system bridges, not the canonical explanation of how Cargo found the subject in the first place.
- **Not ScriptKit:** that kit should own single-file package/frontmatter truth and explicit workspace posture for script lanes, while importing discovery-boundary facts when scripts opt into repo attachment.
- **Not Workspace Environment Stack:** that stack should own realized toolchain/native/runtime/credential environment after discovery decided what repo/package/workspace is even in play.
