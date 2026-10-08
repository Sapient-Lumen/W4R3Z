## Execution addendum (rev0457)
Read this pilot program together with `design/tooling-contract-execution-blueprint-2026Q1.md`.

Interpretation rule:
- the ranked pilot order is unchanged;
- this revision says more explicitly what the **Tooling Contract** seam should become in theory and practice;
- keep the pilot focused on **discovery/scope first, graph/plan second, execution/build-state imports third, adapters fourth, and broader consumer handoffs last**;
- and refuse the tempting wrong shapes first: a Cargo daemon, a BSP-only bridge, or a target-dir/build-dir scraping stack that calls itself a protocol.

# Design: Tooling Contract Pilot Program

## Purpose
Turn the **Tooling Contract Stack** into an executable program instead of leaving it as an attractive synthesis.

The archive should evaluate machine-facing Cargo work as a **ranked pilot program** spanning discovery, package selection, graph/plan truth, execution/build-state truth, and downstream consumers.

## Why now
- The Rust 2026 roadmap puts Cargo integration into larger build systems and plumbing commands in the active flagship set.
- Cargo’s plumbing goal already names explicit phases from project location through final-artifact staging, which is exactly the decomposition this stack needs.
- Cargo’s stable external-tools surface remains intentionally small (`cargo metadata`, `--message-format=json`, custom subcommands), while new needs are piling up around feature resolution, build planning, rebuild reasons, and workspace/config discovery.
- The build-dir-v2 call for testing is the clearest current warning: too many tools still rely on unspecified layout details because the right contract surfaces are missing.
- Cargo’s build-analysis logs and `cargo report` commands prove that richer evidence is possible, but they are still import surfaces, not yet the one stable story.

## Shared artifact family across pilots
The pilot program should converge on a **small composition family** rather than inventing one huge schema:
- `tooling-subject/v0` — repo / cwd / invocation / toolchain identity for the slice under review
- `tooling-scope-report/v0` — discovery roots, config layers, selected packages, and explicit scope-changing inputs
- `tooling-plan-register/v0` — linked graph / plan artifacts with dynamic-expansion boundaries
- `tooling-evidence-register/v0` — execution and report imports with stable-vs-experimental posture markers
- `tooling-consumer-handoff/v0` — bounded import for one downstream class (IDE, CI, outer build, docs, release, support, assistant)
- `tooling-contract-pack/v0` — thin linked bundle of the above plus imported attachments

These artifacts should link existing `workspace-report`, `config-set`, `workspace-graph`, `build-plan`, and build-state/report attachments instead of re-normalizing them into one mega-report.

## References (signals)
- Rust 2026 roadmap: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo external tools reference: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build cache reference: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo unstable/build-analysis docs: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Build-dir-new-layout call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo 1.94 dev-cycle note: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Pilot ranking
### Pilot 1 — Discovery and package-selection lane
**Goal:** make discovery roots, config layers, and selected package scope reviewable.

Deliver:
- workspace/config discovery chain
- package-selection source (`cwd`, `default-members`, explicit flags, policy import)
- effective-vs-ignored settings
- `workspace-report/v0` → `config-set/v0` handoff

Success looks like:
- tools stop guessing what “the repo” or “the workspace” means in a given run.

### Pilot 2 — Graph and plan lane
**Goal:** make Cargo’s intended graph/plan explicit without pretending dynamic details are fully fixed in advance.

Deliver:
- `workspace-graph/v0`
- `build-plan/v0`
- explicit dynamic-expansion boundaries for build scripts/proc macros
- optional `--unit-graph` raw attachments

Success looks like:
- IDE/CI/build-bridge tools can consume a clearer plan than `cargo metadata` alone provides.

### Pilot 3 — Execution and build-state lane
**Goal:** join live execution signals to durable build-state evidence.

Deliver:
- `cargo-events/v0` or compatible execution/event stream imports
- rebuild-reason imports
- block/reuse/relink observations
- stable-vs-experimental evidence markers for report/log imports

Success looks like:
- the stack can explain not just what Cargo meant to do, but what actually happened and why.

### Pilot 4 — Consumer-adapter lane
**Goal:** prove the stack helps more than one downstream class.

Deliver:
- one IDE/rust-analyzer-adjacent consumer
- one CI/reporting consumer
- one non-Cargo or mixed-build adapter
- explicit adapter-lossiness notes

Success looks like:
- at least two materially different tool classes can reuse the same contract boundaries.
- adapter lossiness is visible instead of disappearing into one tool’s private compatibility layer.

### Pilot 5 — Artifact handoff lane
**Goal:** connect machine-facing build truth to downstream release/docs/support consumers.

Deliver:
- docs or release attachments importing package-selection and build-state truth
- support/incident handoff examples
- explicit note when final-artifact staging remains approximate or out of scope

Success looks like:
- the stack proves it helps humans and process tooling, not just build-tool specialists.

## Honest partial outcomes
A pilot may still succeed if it proves one of these narrower conclusions:
- discovery/package-selection truth is the real near-term bottleneck;
- graph/plan outputs are useful even before live-event schemas settle;
- build-analysis/report imports help more than new execution streams right now;
- IDE and outer-build consumers need different adapter layers while still sharing the same upstream boundaries.

## Failure modes to avoid
- inventing a giant canonical schema before proving consumers
- flattening discovery, plan, execution, and rebuild evidence into one report
- silently treating experimental report logs as stable contracts
- promising that build-dir internals are now safe to depend on
- turning the pilot into a universal build daemon or monorepo platform

## Archive policy
Future revisions should prefer:
- discovery-boundary truth,
- package-selection truth,
- graph/plan exports with explicit dynamic-expansion notes,
- build-analysis/report imports with stability posture,
- honest adapter-lossiness,
- and ranked consumer pilots

over another wrapper that still scrapes `target/`, a BSP-only bridge, or a giant Cargo-control-plane fantasy.

See also [`proposals/epic-tooling-contract-stack.md`](../proposals/epic-tooling-contract-stack.md) for the proposal-layer framing that turns these pilots into a concrete ecosystem contribution.
