# Epic proposal: Lint Baseline Kit (`cargo lintpack`, `lint-pack/v0`)

## One-liner
Ship a standard lint governance boundary for Rust: versioned lint profiles, explicit debt baselines, normalized finding reports, reviewable fix packs, and clean handoff into edit/policy/release consumers across rustc, Clippy, rustdoc, Cargo-side report families, and adjacent tools.

## Why this is worthy
Rust already has several strong lint engines, stable manifest/workspace lint configuration, and fix suggestion flows. The missing contribution is not “another linter”; it is the **shared policy/baseline/report/fix layer** around them.

That matters because Rust is increasingly using linting for more than style:
- safety-critical guidance,
- API hygiene,
- documentation quality,
- migration and edition prep,
- monorepo rollout governance,
- and release/policy evidence.

## Users
- application teams with nontrivial CI policy
- safety-heavy users that need curated lint subsets
- large monorepos rolling out stricter linting incrementally
- tool authors who want normalized report/fix artifacts
- release/policy/evidence pipelines that need structured lint outputs

## MVP (6–10 weeks)
- `lint-profile/v0`, `lint-baseline/v0`, `lint-report/v0`, `lint-pack/v0`
- `cargo lintpack profile`, `baseline`, `check`, `diff`, `pack`
- rustc + Clippy adapters
- manifest/workspace lint-origin and group-lock export
- finding normalization and fingerprinting
- baseline-aware diff mode (`new` vs `existing` findings)
- optional `rustfix` / `cargo fix`-derived `lint-fixpack/v0`

## Good v1 extensions
- rustdoc-lint adapter
- Cargo future-incompat / Cargo-lint import notes
- organization-level profile presets (for example `safety_critical`, `docs_strict`, `api_hygiene`)
- reviewable fix bundles with overlap/conflict analysis
- release-attachable `lint-pack/v0`
- richer suppression-expiry and owner metadata

## Non-goals (initially)
- replace Clippy, rustc, rustdoc, or Cargo report families
- decide the “right” lint policy for everyone
- guarantee perfectly stable fingerprints across every compiler release
- silently auto-apply all fixes
- become a universal code-mod tool
- become a hidden policy engine or repo-cleanliness score

## Risks and mitigations
- **Baseline abuse**
  - make debt explicit with reason, scope, and review metadata.
- **Group drift**
  - lock or record expanded group meaning inside the profile/report flow.
- **Inheritance confusion**
  - export manifest/workspace origin and override posture explicitly.
- **Too many engines**
  - start with rustc + Clippy, then add rustdoc and Cargo-side imports.
- **False precision in fix application**
  - carry machine-applicability grades and conflicts into `lint-fixpack/v0`.
- **Stack confusion**
  - keep authored guidance, observed findings, applied edits, and final verdicts as separate artifacts.

## Why now
Rust’s 2026 flagships explicitly include creating a place for safety-critical lints in Clippy. Cargo has already stabilized `[lints]` and `[workspace.lints]`, is experimenting with `[lints.cargo]`, and already exposes a machine-usable report lane for future incompatibilities. Meanwhile, `cargo fix` is valuable but still awkward for selective/config-sensitive rollouts. That makes this the right moment to add the missing governance contract before every organization invents a different lint stack.
