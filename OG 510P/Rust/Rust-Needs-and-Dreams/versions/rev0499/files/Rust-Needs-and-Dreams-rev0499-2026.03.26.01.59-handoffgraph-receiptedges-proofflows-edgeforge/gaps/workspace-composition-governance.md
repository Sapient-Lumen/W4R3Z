# Gap: Workspace Composition & Governance (nested workspaces, inheritance, profiles, lints)

## Summary
Cargo workspaces are the scaling unit for many Rust orgs, but teams still hit sharp edges when
repositories grow and subprojects need autonomy:

- **Nested workspaces**: “monorepo with sub-repos” patterns are common, but the UX for nested workspaces
  and top-level control is still evolving.
- **Inheritance semantics**: dependency inheritance exists, and lints now support workspace inheritance,
  but broader “workspace governance” remains fragmented (profiles, edition-like settings, policies).
- **Profiles and non-root crates**: there are recurring surprises where profile configuration in members
  is ignored or behaves unexpectedly, complicating large repos and “mixed targets” workspaces.

This gap is about making workspaces a first-class *composition* tool: scalable defaults, clear override
rules, explicit discovery boundaries, package-selection truth, and a unified “doctor” surface.

## Ecosystem signals
- The Cargo Book documents `workspace.lints` inheritance and the `lints.workspace = true` opt-in,
  showing that workspace-level governance is actively expanding.  
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- The Cargo team has ongoing design work around nested workspaces, including open questions about
  top-level control vs bottom-up control.  
  https://hackmd.io/%40rust-cargo-team/H1Oa5ILxj
- Cargo issue reports user confusion and surprising behavior around profiles in non-root packages.  
  https://github.com/rust-lang/cargo/issues/15262
- Cargo dev cycle updates discuss “workspace edition” and broader inheritance framing as ongoing design
  concerns.  
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo 1.94 explicitly calls out workspace/config discovery problems caused by stray parent `Cargo.toml` or `.cargo/config.toml` files, and explores opt-out ideas around workspace auto-discovery.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo’s workspaces docs and changelog also make package-selection posture more visible via `default-members` and `workspace_default_members` in `cargo metadata`.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/cargo/CHANGELOG.html

## What “good” looks like
- A coherent *model* of “what is governed at workspace scope” with explicit override rules and explicit discovery roots.
- A `cargo workspace doctor` that can explain:
  - which settings apply to which packages (and why),
  - which packages were selected by default (and why),
  - when member configuration is ignored,
  - where inheritance and discovery came from (root vs nested vs parent config).
- A portable report artifact for CI diffs (“workspace config drift”).
