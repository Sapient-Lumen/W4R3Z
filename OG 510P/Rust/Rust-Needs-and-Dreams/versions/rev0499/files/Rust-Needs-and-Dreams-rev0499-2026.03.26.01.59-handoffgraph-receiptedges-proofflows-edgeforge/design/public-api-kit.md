> Companion frontier: `design/public-api-contract-2026Q1.md` promotes this kit into the repo's explicit **Public API Contract**.

# Design: Public API Kit (`cargo api`, `api-pack/v0`)

## Goal
Make Rust library evolution **reviewable, portable, and automatable** by defining:
- a reference CLI (`cargo api`),
- a normalized public-surface schema (`api-surface/v0`),
- a public-exposure report (`api-exposure-report/v0`),
- standard diff and semver reports (`api-diff-report/v0`, `semver-report/v0`),
- a witness-evidence report for type-sensitive compatibility checks (`api-witness-report/v0`),
- an MSRV verification report (`msrv-report/v0`),
- and a release attachment format (`api-pack/v0`).

This is not just a nicer wrapper around existing tools. The point is to turn public API evolution into a **first-class release and publish-admission boundary** that other tools can consume.

## References (signals)
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Stabilize public/private dependencies: https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- Cargo unstable `public-dependency`: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog: `-Zpublic-dependency` status in `cargo metadata`: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Resolve blockers for integrating `cargo-semver-checks` into Cargo: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- Continue resolving those blockers, including witness-based type checking: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- GSoC 2025 witness-generation work: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo 1.94 dev cycle: structured logging, `cargo report`, and plumbing direction: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- docs.rs rustdoc JSON builds/hosting: https://docs.rs/about/rustdoc-json
- Pilot rollout order: ./public-api-pilot-program.md
- `cargo-public-api`: https://github.com/cargo-public-api/cargo-public-api
- `cargo-semver-checks`: https://github.com/obi1kenobi/cargo-semver-checks
- `cargo-msrv`: https://github.com/foresterre/cargo-msrv
- CycloneDX Cargo plugin: https://github.com/CycloneDX/cyclonedx-rust-cargo
- Relink don’t rebuild: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html

## Core UX: `cargo api`
- `cargo api export`
  - emit `api-surface/v0` for the selected crate/package/workspace member
- `cargo api exposure`
  - emit `api-exposure-report/v0` comparing declared versus inferred public-dependency exposure
- `cargo api diff --against <ref|version|path>`
  - compare surfaces and emit `api-diff-report/v0`
- `cargo api semver-check --against <ref|version|path>`
  - emit `semver-report/v0` with stable reason codes and witness requirements
- `cargo api witness --against <ref|version|path>`
  - generate and check witness crates for selected type-sensitive changes and emit `api-witness-report/v0`
- `cargo api msrv-verify [--toolchain <ver>]`
  - emit `msrv-report/v0`
- `cargo api publish-check --against <ref|version|path>`
  - summarize whether the release would pass, fail, or require explicit override in a publish-time compatibility gate
- `cargo api pack`
  - produce `api-pack/v0`
- `cargo api verify-pack <path>`
  - verify schema versions, checksums, and toolchain metadata
- `cargo api explain <reason-code>`
  - decode semver and API classifications into human guidance

## Artifacts
### `api-surface/v0`
A normalized description of the release boundary:
- crate identity, version, target, features, cfgs, edition
- public items and normalized signatures
- public trait impls and notable bounds
- annotations such as deprecation / `doc(hidden)` / feature gating where relevant
- per-item provenance:
  - defined here
  - reexported from another crate
  - synthetic / generated / unresolved
- generator identity:
  - rustc/rustdoc version
  - adapter/tool version
  - rustdoc JSON compatibility version if applicable

### `api-exposure-report/v0`
A normalized picture of dependency exposure:
- declared public dependencies when available
- inferred exposed dependencies where analysis can prove or strongly suspect exposure
- drift classes:
  - `DECLARED-PUBLIC-AND-EXPOSED`
  - `DECLARED-PUBLIC-BUT-NOT-OBSERVED`
  - `EXPOSED-BUT-UNDECLARED`
  - `CROSS-CRATE-PROVENANCE-UNKNOWN`
- item paths / reexports / trait bounds / associated types that caused the exposure
- confidence and unsupported-lane markers

### `api-diff-report/v0`
- change list with item paths and old/new normalized signatures
- per-change provenance and cfg/feature scope
- classifications:
  - additive
  - breaking
  - behaviorally suspicious but structurally ambiguous

### `semver-report/v0`
- stable reason codes such as:
  - `SEMVER:METHOD-REMOVED`
  - `SEMVER:TRAIT-BOUND-TIGHTENED`
  - `SEMVER:PUBLIC-DEPENDENCY-EXPOSURE-DRIFT`
  - `SEMVER:TYPE-CHANGE-NEEDS-WITNESS`
  - `SEMVER:CROSS-CRATE-PROVENANCE-MISSING`
- verdict classes:
  - pass
  - breaking
  - ambiguous-needs-witness
  - unsupported-analysis-lane
  - waived-by-publisher
- optional publish-check summary for CI / release review

### `api-witness-report/v0`
Records compiler-checked compatibility evidence for type-sensitive changes.

Should capture:
- baseline crate identity and comparison target
- witness-program generation strategy and tool version
- selected changes or reason codes that triggered witness generation
- compilation verdicts for old/new witness crates
- unsupported lanes or witness-generation failures
- normalized diagnostics / attachment pointers
- confidence level and explicit statement that witness evidence supplements, rather than replaces, structural diffing

### `msrv-report/v0`
- declared `rust-version`
- toolchains tested
- commands run and matrix policy
- pass/fail plus failure classification:
  - compiler feature mismatch
  - dependency MSRV mismatch
  - build script / proc-macro incompatibility
  - test-only failure

### `api-pack/v0`
- `manifest.json`
- `api-surface.json`
- `api-exposure-report.json` (optional)
- `api-diff-report.json` (optional)
- `semver-report.json` (optional)
- `api-witness-report.json` (optional)
- `msrv-report.json` (optional)
- checksums and provenance fields
- optional inventory-pack pointer / digest so supply-chain tools can correlate API boundary and dependency inventory
- optional publish-check / waiver attachment

## Design principles
- **One release boundary, many consumers.** CI, registries, distros, scanners, and human reviewers should all read the same pack.
- **Separate structure from proof.** Item diffs, semver reasoning, and witness-based compiler evidence are related but not identical.
- **Declared + inferred boundary.** Use Cargo’s declared public/private dependency model where available, but also support analysis that catches accidental exposure.
- **Evidence, not aspiration.** MSRV must be tested, not just copied from `Cargo.toml`.
- **Publish-gate friendly, not publish-gate monopolistic.** The kit should be able to power a `cargo publish` gate without assuming Cargo is the only consumer.
- **Tool-neutral adapters first.** Build on existing tools before replacing them.

## Integration points
- **Policy Kit** for gating on public dependency exposure and semver hygiene
- **Trust Signals Kit** for release trust summaries
- **Lifecycle Ledger Kit** for deprecations / successor notes that are attached to, but not replaced by, API evidence
- **Migration Kit** for source→destination change plans that consume API evidence
- **Cargo Report Kit** for shared reporting conventions
- **SBOM Evidence Kit / Signed Binaries / Release Pipeline Kit** for release attachments
- **Workspace Governance Kit** for workspace-level package selection and inherited policy
- **FFI Boundary Kit** for crates that expose native boundaries alongside Rust APIs
- future build-graph work such as relink-oriented interface hashing

## Hard problems (explicitly scoped)
1. **rustdoc JSON churn**
   - v0 should pin or record compatibility metadata rather than pretending the input is stable.
2. **Cross-crate provenance gaps**
   - public API and semver reasoning often depend on foreign items and reexports.
3. **Witness compile cost and coverage**
   - witness generation should be selective, explainable, and honest about unsupported lanes.
4. **Feature/cfg matrix explosion**
   - v0 should support a policy-selected matrix, not powerset exhaustiveness.
5. **Public dependency truthfulness**
   - manifests may underdeclare; analysis should be able to emit declared-vs-inferred drift.
6. **Workspace ergonomics**
   - large workspaces need package selection, baselines, and aggregation modes.

## Overlap boundaries
- **Not Migration Kit:** Migration owns source→destination plans and execution history; Public API Kit owns release-boundary evidence.
- **Not Change Impact Kit:** change-impact owns required rebuild/relink scope across many edit kinds; Public API Kit supplies one especially important signal when the public surface itself changed.
- **Not Lifecycle Ledger Kit:** deprecation/support/successor intent stays separate even when it references API evidence.
- **Not Policy Kit:** policy decides what to block or allow; Public API Kit supplies normalized evidence.
- **Not Release Pipeline Kit:** release tooling carries and publishes packs; this kit defines the API evidence inside them.
- **Not one big semver score:** preserve multiple reports and attachments instead of flattening everything into one badge.

## Evaluation plan
Use the ranked rollout in [`design/public-api-pilot-program.md`](./public-api-pilot-program.md):
1. single-crate release gate
2. workspace release group
3. downstream packaging / distro intake
4. policy / trust / inventory correlation
5. change-impact / relink consumer lane

Success bar:
- a maintainer can attach one `api-pack/v0` to a release
- workspace summaries do not erase per-crate provenance gaps or waivers
- CI can gate on stable reason codes without scraping freeform output
- downstream consumers can inspect public surface, exposure drift, witness verdicts, and MSRV evidence without rerunning all tools
- later policy/build consumers can ingest the same pack without forcing all consumers into one verdict model
- a future `cargo publish` integration has an obvious evidence boundary instead of bespoke CLI output
