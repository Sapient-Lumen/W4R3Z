# Gap: Repo composition discovery, package selection, and scope continuity

## What is missing
Rust has **workspace pieces** and **tooling pieces**, but it still lacks one portable contract for the question teams keep actually asking:

> **What repo/workspace/config scope did Cargo think we were operating on, why, and which downstream lane consumed that exact scope next?**

Today that answer is spread across:
- parent-directory manifest/config discovery,
- workspace membership and `package.workspace` attachment,
- `default-members` and current-working-directory selection,
- ad hoc CI/editor/docs/release package filters,
- partial machine-facing Cargo outputs.

The result is familiar: maintainers, CI, editors, wrappers, and outer build systems all say they are acting on “the workspace” while often meaning slightly different things.

## Why this matters now
Official Cargo signals make this seam sharper than it used to be.

- Cargo’s configuration docs say config files are probed in the current directory, all parent directories, and `$CARGO_HOME`, so discovery itself changes behavior.
- Cargo’s workspace docs say subdirectories automatically search upward for a `[workspace]`, `package.workspace` can override that search, and commands run at the workspace root use `default-members` when package-selection flags are absent.
- Cargo 1.94 explicitly called out workspace/config discovery as an active design problem, including broken parent `Cargo.toml` / `.cargo/config.toml` files and the possibility of `package.workspace = false`-style opt-out work.
- Cargo 1.93/1.94 stabilized the config `include` key and documented optional includes, which increases configuration-layer expressiveness and therefore the need for explanation and diffing.
- `cargo metadata` is useful but explicitly versioned/partial, while the accepted Cargo plumbing goal says current machine-facing commands remain too porcelain-oriented and describes the build as phases from locate-project through staging final artifacts.
- Cargo’s 1.90 development-cycle report says the `cargo-plumbing` prototype had to re-read manifests inside each command because Cargo’s current Rust APIs were not yet exposing the needed structure cleanly enough.

## References (signals)
- Cargo configuration reference: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspaces reference: https://doc.rust-lang.org/cargo/reference/workspaces.html
- `cargo locate-project`: https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html
- `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo changelog / release notes (`config include`, `workspace_default_members`): https://doc.rust-lang.org/cargo/CHANGELOG.html ; https://doc.rust-lang.org/beta/releases.html
- Cargo 1.90 dev-cycle note (`cargo-plumbing` prototype and limits): https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- Cargo 1.94 dev-cycle note (workspace/config discovery): https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Accepted Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html

## What the ecosystem keeps doing instead
When this gap is not filled, teams fall back to:
- CI shell glue that re-derives selected packages from path filters,
- editor/workspace adapters that quietly guess the wrong root,
- release/doc/test lanes that silently disagree about package scope,
- outer build systems scraping `cargo metadata` plus local heuristics,
- bespoke repo dashboards that flatten discovery, inheritance, and execution scope into one fake “workspace state”.

## What a worthy contribution would look like
A worthy contribution would **not** be another monorepo manager or repo-manifest format.
It would be a thin review layer that preserves:
- discovered manifest/workspace roots,
- discovered config layers and include chains,
- effective/ignored/inherited workspace governance,
- package-selection truth (`cwd`, `default-members`, flags, policy),
- bounded downstream scope handoffs into docs/test/release/CI/editor/build lanes.

The likely shape is a portable `repo-compose-pack/v0` above:
- `workspace-report/v0`
- `config-set/v0`
- `config-analysis-report/v0`
- selected Cargo machine-facing attachments (`cargo locate-project`, `cargo metadata`, optional plumbing/build-interop imports)

## Boundary to defend
Repo composition should stop at **discovery + governance + selection + handoff**.
It should import graph/build/runtime evidence from adjacent stacks instead of re-owning them.

That boundary matters because the missing thing is not “another build plan” or “another workspace diff”.
The missing thing is a way to say, reviewably and portably:
- what Cargo found,
- what scope that implied,
- what got selected,
- and which downstream consumer used that exact selection.
