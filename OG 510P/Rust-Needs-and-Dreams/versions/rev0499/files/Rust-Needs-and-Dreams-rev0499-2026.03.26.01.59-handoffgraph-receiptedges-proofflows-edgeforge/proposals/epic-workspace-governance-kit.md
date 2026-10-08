# Epic Proposal: Workspace Governance Kit

## One-sentence pitch
Make Cargo workspaces scale by giving teams an explainable, diffable view of discovery, package selection, inheritance, and overrides (profiles, lints, nested workspaces), via `cargo workspace doctor` and `workspace-report/v0`.

## Deliverables
- `cargo-workspace-doctor` reference implementation
- Schemas:
  - `workspace-report/v0`
  - `workspace-policy/v0` (optional org rules)
- Discovery / selection checks:
  - parent config or manifest interference detector
  - default-members / package-selection explainer
- Checks:
  - non-root profile ignored detector
  - nested workspace conflicts / ambiguity detector
  - “effective lint set” inspector
- CI templates:
  - generate report on PR + diff against main
- Example repos + fixtures:
  - nested workspaces example (root + subworkspace)
  - mixed targets example (WASM + native)

## Why now
- Cargo is actively expanding workspace-level governance (e.g., `workspace.lints`).  
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Nested workspaces are an active design area with open questions about control boundaries.  
  https://hackmd.io/%40rust-cargo-team/H1Oa5ILxj
- Real users hit confusing profile behavior in large workspaces.  
  https://github.com/rust-lang/cargo/issues/15262
- Cargo dev cycle updates highlight ongoing inheritance framing issues (and the “workspace edition” need).  
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo 1.94 makes workspace/config discovery itself an explicit design concern because stray parent files can interfere with unrelated projects.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- `default-members` and `workspace_default_members` make package-selection truth increasingly machine-visible.  
  https://doc.rust-lang.org/cargo/reference/workspaces.html  
  https://doc.rust-lang.org/cargo/CHANGELOG.html

## Non-goals
- Defining the upstream “workspace edition” feature (we provide an adoption bridge and diagnostics)
- Replacing Cargo’s config system
- Forcing one governance model on all repos

## Milestones
1) v0: report + explain + a few high-value warnings (profiles ignored, nested conflicts, selection surprises)
2) v0.2: discovery-chain output + diff + CI templates + lint governance summaries
3) v0.3: `config-set` handoff and integration hooks (policy/perf/interop) + fixtures/corpus
4) v1: stable schemas and upstream proposal pathway
