# Design: Repo Composition Pilot Program

## Purpose
Turn the repo-composition seam into an executable program instead of leaving it as an attractive synthesis.

The archive should evaluate repo-composition work as a **ranked pilot program** spanning discovery, workspace explanation, package selection, bounded matrices, and downstream consumers.

## Why now
- Cargo’s configuration system is hierarchical across parent directories and `$CARGO_HOME`, so accidental parent configs are part of real-world behavior.
- Cargo 1.93 resumed active `-Zconfig-include` work and Cargo 1.94 stabilized the config `include` key, including optional includes and defined merge order, which increases layering complexity.
- Cargo 1.94 explicitly called out workspace/config discovery as a design problem and discussed opt-out possibilities around auto-discovery.
- Workspaces now carry more governance weight (`default-members`, inherited package fields, dependency inheritance, workspace lints, tool metadata).
- `cargo metadata` now includes `workspace_default_members`, making package-selection truth more exportable, even though the metadata format remains explicitly versioned.
- Cargo’s 1.90 development-cycle note on `cargo-plumbing` showed the prototype still had to re-read manifests inside commands because Cargo’s Rust APIs were not yet exposing enough structure cleanly.


## References (signals)
- Cargo configuration reference: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspaces reference: https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo changelog / release notes: https://doc.rust-lang.org/cargo/CHANGELOG.html ; https://doc.rust-lang.org/beta/releases.html
- `cargo locate-project`: https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html
- `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo 1.90 dev-cycle note: https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- Cargo 1.93 dev-cycle note: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo 1.94 dev-cycle note: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Pilot ranking
### Pilot 1 — Workspace truth lane
**Goal:** make `workspace-report/v0` strong enough for human review and CI diffs.

Deliver:
- discovered root
- full member list
- nested-workspace structure
- `default-members` and root-package posture
- effective lints / profiles / inherited package fields
- ignored-setting warnings with concrete fixes

Success looks like:
- teams can review repo-composition drift in PRs without re-running the build locally just to understand scope.

### Pilot 2 — Discovery-boundary lane
**Goal:** make parent-file interference and attachment choices visible.

Deliver:
- discovery chain for parent `Cargo.toml` and `.cargo/config.toml`
- explicit note when discovery relied on auto-search versus `package.workspace`
- warnings for suspicious parent-file interference
- optional import of `-Zconfig-include` chain where available

Success looks like:
- the stack can explain “why is Cargo using *that* workspace/config?” instead of only “what was the final result?”

### Pilot 3 — Package-selection and matrix handoff lane
**Goal:** join workspace truth to actual work selection.

Deliver:
- import from `workspace-report/v0` into `config-set/v0`
- explicit source for selected packages/configs (`cwd`, `default-members`, `--workspace`, CI policy, docs lane, release lane)
- diffable selection changes across branches

Success looks like:
- CI/test/doc/release consumers stop re-deriving package scope from ad hoc shell logic.

### Pilot 4 — Tool/export consumer lane
**Goal:** make the stack useful beyond one CLI.

Deliver:
- interop attachment hooks for `cargo metadata`, discovery captures, and optional build-interop exports
- editor-friendly / CI-friendly JSON output
- imports for policy/perf/release consumers

Success looks like:
- at least two downstream consumers can use the exported scope truth without custom scraping.

### Pilot 5 — Cross-tool and mixed-build lane
**Goal:** prove the stack helps when Cargo is not the whole story.

Deliver:
- examples with non-Cargo or partially generated inputs
- workspace metadata conventions where appropriate
- explicit lossiness markers for external-tool adapters

Success looks like:
- the archive can say where Cargo-native truth ends and external-tool approximation begins.

## Honest partial outcomes
A pilot may still succeed if it only proves one of these:
- discovery diagnostics are the real near-term bottleneck,
- package-selection truth helps more than inheritance explanation,
- `workspace-report/v0` should stay Cargo-native while `config-set/v0` handles cross-tool scope,
- bundle-level composition is useful but a new universal schema is not.

## Failure modes to avoid
- inventing a giant schema before proving consumers
- flattening discovery, inheritance, and execution scope into one report
- silently assuming `default-members` is the same as “the repo”
- pretending user/global config files do not affect reproducibility
- turning the pilot into a universal monorepo policy platform

## Archive policy
Future revisions should prefer:
- discovery-boundary truth,
- package-selection truth,
- `workspace-report` ↔ `config-set` handoff,
- honest adapter-lossiness notes,
- and small, reviewable exports

over another one-off monorepo wrapper, workspace dashboard, or giant repo-manifest fantasy.

## Proposal-layer candidate
Use [`proposals/epic-repo-composition-stack.md`](../proposals/epic-repo-composition-stack.md) as the stack-level product-direction candidate: a thin `cargo repo-compose` / `repo-compose-pack/v0` layer above Workspace Governance + Config Set + Build Interop.
