---
id: P-0035
title: cargo-build-insights — imported session warehouse, trend adjudication, and reviewable build-regression receipts
status: idea
domains: [cargo, tooling, performance, enterprise, analytics]
last_reviewed: 2026-03-21
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
needs:
  - Teams need durable build history across branches, CI jobs, toolchain updates, and workspace-scope changes, not only one per-run support bundle.
  - Tool authors need a stable import layer above evolving Cargo build-analysis JSONL and `cargo report` surfaces.
  - Performance owners need reviewable regression artifacts that can explain what changed, what remained comparable, and where the comparison stopped being honest.
risks:
  - Upstream Cargo schemas and command UX are still evolving; imports must preserve provenance, unknown fields, and exactness status.
  - The crate could drift into a dashboard-first product that duplicates P-0469's per-run support bundle or Cargo's own report UX.
  - Historical build data can reveal paths, usernames, CI topology, and branch names; redaction and retention policy must be first-class.
---

# Problem

The archive's Cargo explainability stack is now much sharper than when this proposal was first drafted.

- **P-0469 Cargo Rebuild Explanation Kit** is the support-grade answer to: *why did this run rebuild?*
- **P-0468 Cargo Resolver Explanation Kit** is the proof-carrying answer to: *why is this version / feature state present?*
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** is the parity answer to: *did tool-oriented workflows diverge from fuller builds?*
- **P-0490 Cargo Lock Contention Witness Kit** is the blocking answer to: *what root / wait / workflow role stalled progress?*

What still remains missing is a **historical build-analysis warehouse** that can import Cargo's evolving session data and answer questions broader than one support incident:

- when did the regression start,
- which packages or targets are habitual rebuild offenders,
- which metric shifts are really toolchain/profile/scope splits rather than product regressions,
- and which conclusions are directly imported versus conservatively inferred?

Current upstream work makes this crate much more real than it used to be.

- The build-analysis goal explicitly says Cargo is recording build metadata across invocations and wants external tooling to analyze historical trends.
- The current unstable docs say `-Zbuild-analysis` persists JSONL logs in `$CARGO_HOME/log/`, gives each invocation a unique session id, and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.
- The Cargo 1.94 development-cycle update says `cargo report sessions` was added to find ids, `cargo report timings` kept gaining missing functionality, and unstable `--timings=FMT` was removed as redundant with `cargo report timings`.
- The build-analysis goal explicitly says no user-facing stability guarantees exist yet during prototyping.

That means **cargo-build-insights should stop pretending it needs to invent the recorder**.

Its worthy contribution is now the boring layer above Cargo's evolving session substrate:

1. import sessions conservatively,
2. freeze them into a stable warehouse schema,
3. join them with stable workspace/build context,
4. adjudicate comparability before claiming a regression,
5. and emit reviewable artifacts another human or tool can actually consume.

# What it provides

Core artifacts:

- `warehouse-policy.toml` — retention window, redaction settings, baseline policy, and branch/series naming rules.
- `session-series.index.json` — which imported sessions belong to which series, branches, and candidate comparison families.
- `comparison-window.receipt.json` — why a chosen baseline/head or rolling range was selected, what it excludes, and which review audience it is meant to inform.
- `build-insight-session.json` — one normalized imported session record with command, scope, metrics, provenance, and preserved unknown fields.
- `series-summary.json` — stable rollup for a chosen range or baseline/head comparison.
- `series-compatibility.report.json` — whether the selected sessions are comparable, comparable-with-caveats, or split into separate lanes.
- `regression-explanation.json` — smallest useful explanation of a baseline/head or series change with evidence pointers.
- `trend-alert.json` — rule-based alert for repeated slowdown, reuse collapse, rebuild growth, or series drift.
- `import.receipt.json` — exact upstream sources consumed, normalization steps applied, unknown-field policy, and redaction posture.
- `exactness.report.json` — claim-by-claim ledger for imported facts versus conservative inference versus manual review.
- `notes.md` — short human summary for PRs, CI uploads, or incident threads.

CLI surface:

- `cargo build-insights import-session`
- `cargo build-insights freeze-series`
- `cargo build-insights compare`
- `cargo build-insights regressions`
- `cargo build-insights trend-alerts`
- `cargo build-insights doctor`
- `cargo build-insights export`

# What the crate should provide other people

1. **A durable build-history layer** above nightly Cargo session surfaces.
2. **A stable normalized schema** that downstream tools can depend on without chasing Cargo's moving JSONL/report details directly.
3. **Comparison-window truth** so PR-vs-last-green, release-vs-release, and local-before-after reviews do not masquerade as the same judgment.
4. **Comparability adjudication** so teams stop treating toolchain changes, workspace-scope changes, and profile splits as if they were ordinary regressions.
5. **Confidence and exactness receipts** that separate imported Cargo fact, normalized observation, conservative inference, and manual-review-only judgments.
6. **Portable review bundles** that survive beyond one machine or CI log.
7. **A reusable Rust library** for dashboards, CI bots, and IDEs that should not parse HTML or ad-hoc logs themselves.

# Persona / who it’s for

- CI and build engineers
- workspace and monorepo maintainers
- performance / infra teams
- tool authors who need build-history queries without re-implementing Cargo ingestion

# Users & user stories

- **Infra owner**: “Show me which crates became slower over the last 20 builds on `main`, and whether the comparison is still apples-to-apples.”
- **Workspace maintainer**: “Tell me when reuse dropped, and whether a toolchain bump or target selection change means the series should have been split.”
- **Tool author**: “Give me a stable Rust library for imported Cargo sessions so I do not parse unstable JSONL by hand.”
- **Reviewer**: “Attach one bundle to the PR showing the build regression and what we know versus infer.”

# Prior art (and why it’s insufficient)

- `cargo build --timings` remains a useful per-run human surface, but the build-analysis goal itself says the preexisting timings path is not enough for historical analysis.
- `cargo report timings` / `rebuilds` / `sessions` are the right upstream substrate, but they are still unstable and intentionally not the downstream stable warehouse contract.
- `--message-format=json` is a valuable live build stream, but it is not a historical session store.
- `cargo metadata --format-version` is the stable graph/context substrate, but it does not answer build-history questions by itself.
- **P-0469** remains the better answer for one support incident; **P-0035** is the stronger answer for *history, trend, and regression adjudication across many runs*.

# Design goals

- **Import-first:** treat Cargo's build-analysis/session surfaces as substrate, not competition.
- **Comparability-first:** decide whether sessions belong in one lane before claiming a regression.
- **Comparison-window honesty:** a claim about “regressed” must say which baseline or rolling window it compared against.
- **Stable normalized schema:** version the warehouse schema independently and preserve unknown upstream fields.
- **Exactness honesty:** clearly separate imported fact from normalized observation from inference.
- **Privacy-aware by default:** retention, redaction, and series labeling are first-class.
- **Bundle-first:** the reviewable artifact contract should become useful before any UI does.

## Non-goals

- Replacing Cargo's own recorder or `cargo report` commands.
- Replacing P-0469's support-grade per-run rebuild bundle.
- Becoming an always-on telemetry backend or SaaS product.
- Pretending imported HTML timing replay is the machine contract.
- Deciding graph-cause truth that belongs in resolver explanation or contention diagnosis lanes.

# Architecture & API sketch

## Crates

- `cargo_build_insights_core`
  - importers
  - schema upgrade / downgrade
  - normalized query model
  - comparability / regression rules
- `cargo-build-insights`
  - CLI for import, freeze, compare, alerts, doctor, and export
- optional `cargo_build_insights_store`
  - SQLite / filesystem backing store
- optional `cargo_build_insights_rules`
  - declarative rule packs for alerts and comparison gates

## Import sources

### Primary
- Cargo `-Zbuild-analysis` JSONL logs
- `cargo report sessions`
- `cargo report timings`
- `cargo report rebuilds`

### Stable context joiners
- `cargo metadata --format-version`
- Cargo external-tools JSON (`--message-format=json`)

### Optional overlays
- `cargo build --timings` HTML attachment
- manual annotations for branch labels / benchmark intent

## Stable query primitives

- `InsightSessionId`
- `SeriesId`
- `ComparisonWindowId`
- `ImportedSourceKind`
- `SeriesComparability`
- `ComparisonAudience`
- `ObservedMetric`
- `ExactnessClass`
- `RegressionJudgment`

# Security / safety model

- local-first by default
- explicit retention windows
- explicit redaction of paths, usernames, CI job ids, and branch labels
- preserved raw imports only when the user explicitly requests them
- imported unstable data always tagged with provenance and schema uncertainty

# Maintenance & governance plan

- compatibility matrix for imported Cargo session/report surfaces
- golden fixture bundles for baseline, branch, toolchain, and scope-drift scenarios
- schema evolution rules with unknown-field preservation
- keep UI optional so the bundle contract can stabilize first

# Milestones

## 0.1

- import one or more Cargo build-analysis sessions
- normalize them into `build-insight-session.json`
- write `session-series.index.json`, `comparison-window.receipt.json`, `series-summary.json`, `import.receipt.json`, and `exactness.report.json`
- compare a baseline/head or tiny series range
- emit `series-compatibility.report.json` whenever lane-split or caveat decisions matter
- export one portable `*.buildinsights.zip`

## 0.2

- trend alerts across configurable series
- explicit comparability reports for toolchain/profile/workspace-scope splits
- richer joins with stable Cargo message / metadata inputs

## 1.0

- multi-schema import stability table
- library API solid enough for downstream tools
- redaction and retention rules boring enough for CI / org-wide adoption

# Adjacent archive relationship

- **P-0469** should answer: *why did this rebuild today?*
- **P-0035** should answer: *when did this regress, how often, and which series are still legitimately comparable?*
- **P-0494** should answer: *did a tool-only or editor-oriented workflow diverge from a fuller build?*
- **P-0490** should answer: *was the slowdown really a wait / lock / shared-root story?*
- **P-0468** should answer: *why is this graph choice / feature / duplicate-build state present?*

If a future pass tries to merge all of those into one crate, that is almost certainly a repo regression.

# Open questions

- What is the smallest useful normalized metric set for 0.1?
- Should trend rules be declarative from day one, or should rule packs come after the bundle contract hardens?
- When Cargo session wording or field shape changes, which fields should be preserved raw versus normalized into stable enums?

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that can import a small set of Cargo build-analysis sessions, separate them into comparable versus split series, emit one stable regression/trend bundle with provenance and exactness receipts, and hand another person one zip that says what changed, what stayed comparable, and where the story still requires manual review.

# Sources

- Rust Project Goal — Prototype Cargo build analysis: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo Book — Unstable features (`-Zbuild-analysis`, `cargo report sessions`, `cargo report timings`, `cargo report rebuilds`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Inside Rust — This Development-cycle in Cargo 1.94: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo Book — External tools (`cargo metadata`, `--message-format=json`): https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo Book — `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo Book — Cargo changelog (`-Zbuild-analysis` landing): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust Project Goal — Relink don’t Rebuild: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Rust Blog — 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust Blog — Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
