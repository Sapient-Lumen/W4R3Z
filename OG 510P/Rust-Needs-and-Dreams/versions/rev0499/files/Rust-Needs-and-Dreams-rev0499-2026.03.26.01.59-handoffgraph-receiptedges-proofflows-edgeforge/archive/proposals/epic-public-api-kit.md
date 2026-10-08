> Read together with `design/public-api-contract-2026Q1.md`, which frames this epic as a first-class **Public API Contract** rather than just a tool bundle.

# Epic Proposal: Public API Kit (`cargo api`)

## One-sentence pitch
Turn Rust library evolution into a first-class release and publish-admission artifact: export the public surface, report exposure drift, diff it, check semver, run witness-based compatibility checks, verify MSRV, and attach the results as one portable pack.

## Deliverables
- `cargo-api` reference implementation
- Schemas:
  - `api-surface/v0`
  - `api-exposure-report/v0`
  - `api-diff-report/v0`
  - `semver-report/v0`
  - `api-witness-report/v0`
  - `msrv-report/v0`
  - `api-pack/v0`
- Commands / adapters:
  - `cargo-public-api`
  - `cargo-semver-checks`
  - `cargo-msrv`
  - optional SBOM correlation via `cargo-cyclonedx`
- Docs:
  - release workflow for library maintainers
  - ranked pilot-program guide for publish-admission lanes
  - reason-code reference
  - witness-generation policy / caveats
  - policy patterns for CI / registries / distros / publish-time gating

## Why now (signals)
- Rust’s 2026 flagship supply-chain work explicitly includes public/private dependencies and SBOM support.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The public/private-dependency goal says the feature should help users catch accidental exposure of implementation details and help tooling understand what constitutes an API.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- Cargo’s unstable `public-dependency` support already exists and feeds the `exported_private_dependencies` lint.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The `cargo-semver-checks` goal explicitly targets eventual integration with `cargo publish`, says more than 90% of real-world false-positives trace back to cross-crate items, and calls out type-sensitive semver checking as a remaining blocker.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- The 2025 GSoC witness-generation project established a proof-of-concept for compiler-checked semver compatibility of type changes and is described as key to the 2026+ roadmap.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s newer structured-report and plumbing work makes a portable release-boundary artifact more realistic than it used to be.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Non-goals
- Stabilizing a Rust ABI
- Perfect semantic understanding of every behavior change in v0
- Exhaustive feature powerset checking
- Replacing the existing ecosystem tools immediately
- Hiding human waivers / overrides behind one fake green badge

## Strategic value
This kit has unusually high leverage because it connects:
- library maintainer workflows (`cargo publish`, changelogs, release CI)
- supply-chain policy (public dependency exposure, semver hygiene, SBOM correlation)
- downstream packaging and audit trails
- migration planning that needs honest API evidence
- future build-system work where interface boundaries should matter more than implementation churn

## Milestones
1. **Pilot 1 / v0**
   - wrap existing tools
   - emit `api-pack/v0`
   - stable reason-code surface
   - single-crate publish-check summary + waiver attachment model
   - declared-vs-inferred exposure reporting
2. **Pilot 2 / v0.2**
   - selective witness generation for type-sensitive changes
   - workspace aggregation without erasing per-crate truth
   - package-selection and baseline presets for release groups
3. **Pilot 3 / v0.3**
   - downstream-friendly attachment and checksum conventions
   - clearer matrix / comparison-subject identity
   - distro / enterprise intake guidance
4. **v1**
   - deeper Cargo integration
   - richer cross-crate provenance around reexports / foreign items
   - optional interface hashing for relink-oriented workflows
   - policy / trust / inventory and change-impact consumer hooks

## What success looks like
- A maintainer can attach one pack that answers “what changed, why it matters semver-wise, what the compiler proved, and whether our MSRV claim holds.”
- A registry or CI system can show “publish would require override” without reverse-engineering plugin-specific output.
- Workspace release groups can summarize multiple crates without hiding per-crate waivers or provenance gaps.
- Downstreams can inspect API evidence without rerunning bespoke pipelines.

## Execution order
For the ranked rollout order, see `design/public-api-pilot-program.md`. The archive should treat this epic as schema + integration design, and the pilot-program doc as the staging plan for which consumer lanes to win first.
