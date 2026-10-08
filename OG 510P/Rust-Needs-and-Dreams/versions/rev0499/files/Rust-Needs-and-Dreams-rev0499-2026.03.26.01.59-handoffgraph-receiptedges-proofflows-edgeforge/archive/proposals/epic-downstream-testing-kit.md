# Epic Proposal: Downstream Testing Kit

## One-sentence pitch
Give Rust library authors an adoption-ready, CI-friendly way to run and diff reverse-dependency tests, with portable reports and explainable failures.

## Deliverables
- `cargo-downstream` subcommand
- Schemas: `downstream-report/v0`, `downstream-plan/v0`
- Adapters:
  - crates.io reverse-dependency selection
  - curated lists + org-local registries
- CI templates (GitHub Actions + generic)
- Example repos + benchmarks
- Integration hooks:
  - `cargo cache` (speed)
  - `cargo api` / semver checks (classify `API_BREAK`)
  - Hermetic/Safe mode (reduce flakiness and risk)

## Why now
- The compiler ecosystem already uses Crater to protect Rust releases, but everyday crates lack a standard downstream workflow.  
  https://github.com/rust-lang/crater  
  https://rustc-dev-guide.rust-lang.org/tests/ecosystem.html
- Other ecosystems use reverse-dependency testing as a migration gate (autopkgtest/Britney analogy), suggesting a proven quality lever.  
  https://nesbitt.io/2026/03/01/downstream-testing.html

## Non-goals
- Replacing Crater
- Running the entire crates.io universe by default
- Forcing maintainers to support all downstreams (policy-driven expectations)

## Milestones
1) v0: curated-list runs + report artifact
2) v0.2: diff + explain + reason codes
3) v0.3: crates.io reverse-deps selection + sharding + caching integration
4) v1: stable schemas + CI templates + public corpus for regressions
