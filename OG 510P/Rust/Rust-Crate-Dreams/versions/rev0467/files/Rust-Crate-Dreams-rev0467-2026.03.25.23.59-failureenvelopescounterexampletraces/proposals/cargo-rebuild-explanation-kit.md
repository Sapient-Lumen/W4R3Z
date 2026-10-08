---
id: P-0469
title: Cargo Rebuild Explanation Kit — fingerprint-delta receipts, cache-conflict witnesses, and why-did-this-rebuild bundles
status: idea
domains: [cargo, build, performance, devtools, ci]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
  - https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  - https://doc.rust-lang.org/cargo/commands/cargo-build.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
  - https://github.com/rust-lang/cargo/issues/15844
  - https://github.com/rust-lang/cargo/issues/2904
  - https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  - https://rust-analyzer.github.io/book/configuration
  - https://doc.rust-lang.org/cargo/reference/build-cache.html
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
---

# Problem

Build and rebuild latency remain one of Rust’s most persistent day-to-day pain points.

The signals now line up unusually clearly:

- the 2025 State of Rust survey still reports resource usage (slow compile times and storage usage) as a major productivity problem,
- Cargo now has a nightly `-Zbuild-analysis` substrate with persisted sessions and `cargo report` commands for sessions, rebuilds, and timings,
- the tracking issue for that work still carries unresolved schema and UX questions,
- the long-running “why was this crate rebuilt?” issue remains part of Cargo’s history,
- the “Relink don’t Rebuild” goal exists because obviously-private edits still fan out into reverse-dependency rebuilds,
- and the build-dir-layout goal explicitly names coarse locking, Rust Analyzer interference, and shared-cache pain.

Cargo and rustc already expose *pieces* of the story:

- HTML timing reports,
- debug/fingerprint logging,
- machine-readable `--message-format=json` build messages,
- the new unstable `-Zbuild-analysis` persistence layer,
- `cargo report sessions`, `cargo report rebuilds`, and `cargo report timings`,
- build-cache knobs and directory controls,
- and ongoing work on finer-grained cacheable units.

But ordinary teams still lack a compact artifact answering:

- why did this unit rebuild instead of being reused,
- which evidence came from Cargo itself versus wrapper/env heuristics,
- whether the rebuild came from source edits, feature/resolver drift, profile/target changes, `RUSTFLAGS`, wrapper configuration, or cache-sharing conflicts,
- and whether a second run changed because Cargo lacked reuse opportunities or because the workflow assumptions changed.

Today the workflow is still too scattered:

- open a human-oriented timing HTML report,
- enable verbose Cargo logs,
- grep fingerprint debug output,
- guess whether rust-analyzer, `cargo check`, or a changed environment variable invalidated the cache,
- and then paste an incomplete story into a bug report or CI comment.

The missing crate is not a build accelerator and not a historical analytics warehouse.

The missing crate is a **rebuild explanation kit**: a per-run, reviewable artifact that captures observed rebuild causes and fingerprint deltas in a form humans and tools can actually exchange.

# Main judgment after the 2026-03-08 implementation pass

Cargo’s new reporting substrate makes this proposal **more buildable and more strategically narrow**.

That means the worthy crate is **not**:

- another build recorder competing with Cargo,
- another full-screen timings dashboard,
- another monorepo analytics warehouse,
- or a fragile parser that promises perfect invalidation proofs from unstable internals.

The worthy crate is the **stable receipt / diff / redaction / support-bundle layer** above Cargo’s evolving session and report surfaces.

## 2026-03-16 implementation refresh — session-freeze exactness and cause honesty

# 2026-03-22 implementation refresh — baseline authority and reverse-impact honesty

This proposal is more implementation-ready again because current Cargo docs and project goals make one more downstream boundary explicit: **a rebuild bundle is only as honest as its comparison window and its interpretation of reverse fanout**.

Five details especially matter now:

1. Cargo unstable docs now say build-analysis logs are persisted per invocation with unique session ids and queried through `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.
2. The Cargo 1.94 development-cycle update says `cargo report sessions` exists specifically to find the id needed for the other report commands.
3. The build-analysis goal says Cargo wants invocation metadata and rebuild reasons across runs, but keeps schema evolution open during the prototype.
4. The relink-don’t-rebuild goal explicitly says reverse dependencies still rebuild after non-interface edits.
5. The 2025 survey still says compile-time and resource-usage pain remains among the main productivity limits.

That means the crate should now freeze two more artifact lanes instead of burying them inside generic notes:

- one **`baseline-authority.receipt.json`** that records why a baseline was selected, which compatibility checks passed, and which nearer alternates were rejected;
- one **`reverse-impact.report.json`** that records which dependents rebuilt, whether fanout was directly observed, whether relink-only opportunity is plausible, and where interface change remains unproven.


Cargo’s current build-analysis story is now concrete enough that this proposal should stop hand-waving around its hardest boundary: **what exactly was observed, what was normalized, and what is still only a conservative judgment**.

The 1.94 Cargo development-cycle update makes three implementation details newly relevant:

1. `cargo report sessions` exists specifically to find the session id needed by the other report commands.
2. `cargo report timings` keeps gaining missing functionality, which means HTML timing replay is now more clearly a *consumer aid* than the machine contract.
3. `cargo report rebuild` / `cargo report rebuilds` is becoming a real user-facing explanation surface, which means downstream crates need to preserve wording drift and provenance rather than pretend Cargo’s unstable phrasing is a frozen schema.

That leads to two stronger artifact obligations for this crate:

- **`evidence-source.receipt.json`** — records exactly which Cargo report commands, JSONL/session logs, message streams, and optional overlays were imported, plus whether they were imported verbatim, normalized, or only summarized.
- **`exactness.report.json`** — records which bundle claims are `imported_verbatim`, `normalized_observed`, `conservative_inference`, or `manual_review_required`.

Those two artifacts are what keep the crate from lying when Cargo’s unstable report surfaces evolve underneath it.


# 2026-03-22 later implementation refresh — comparison-scope and route honesty

This proposal is more implementation-ready again because current Cargo docs and tooling now make one more receiver-facing boundary explicit: **a rebuild explanation is only as honest as its comparison scope and its artifact-route story**.

Five details especially matter now:

1. Cargo unstable docs now document persisted build-analysis sessions plus `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.
2. Cargo build-cache docs now keep `target-dir` and `build-dir` as first-class distinct routes for final versus intermediate artifacts.
3. The March 2026 Build Dir Layout v2 call for testing says users should test workflows that touch `build-dir` and `target-dir`, and notes that Cargo already lets them separate those routes.
4. rust-analyzer still documents a private `cargo.targetDir` escape hatch that prevents locking at the cost of duplicated artifacts.
5. Build pain remains prominent in the 2025 survey and March 2026 challenges write-up.

That means the crate should now freeze three more artifact lanes instead of burying them in notes:

- one **`comparison-scope.receipt.json`** that records whether candidate and baseline sessions really belong to the same explanatory lane;
- one **`artifact-route-drift.report.json`** that records build-dir / target-dir / tool-owned route changes and how they constrain reuse interpretation;
- one **`rebuild-support-bundle.manifest.json`** that keeps scope, route, evidence, exactness, cause, and imported adjacent-lane context separate.

# What it provides

- `rebuild-context.toml` — pins workspace selection, profile, target, toolchain, wrapper settings, target-dir/build-dir roots, and comparison baseline.
- `unit-rebuilds.json` — every rebuilt or reused unit with conservative cause categories and supporting facts.
- `fingerprint-delta.json` — normalized view of which relevant inputs changed between two runs when visible.
- `cache-conflict.report.json` — lock waits, shared-cache caveats, wrapper/cache-root mismatches, and concurrent-tool hints.
- `rebuild.receipt.json` — exact commands, observed data sources, imported Cargo report sessions, debug modes, fallbacks, and caveats.
- `baseline-authority.receipt.json` — why this baseline/session was selected, which compatibility checks passed, and which alternate baselines were rejected.
- `evidence-source.receipt.json` — exact upstream sources imported (`cargo report sessions`, `cargo report rebuilds`, `cargo report timings`, JSONL logs, Cargo message streams, manual notes), plus whether they were consumed verbatim or normalized.
- `session-index.json` — stable listing of imported or captured Cargo build-analysis sessions and the baseline selected for comparison.
- `reverse-impact.report.json` — reverse-dependency fanout summary that keeps observed rebuilds, relink-candidate judgments, and unproven interface-change claims separate.
- `timings-pointer.json` — points to a human timing replay for the same session without pretending the HTML report is itself the stable machine protocol.
- `exactness.report.json` — every high-value claim with an exactness class (`imported_verbatim`, `normalized_observed`, `conservative_inference`, `manual_review_required`).
- `cargo rebuild-why capture` — capture one run or compare two runs into a bundle.
- `cargo rebuild-why freeze-session <session-id>` — import a Cargo build-analysis session and freeze it into a smaller, stable contract.
- `cargo rebuild-why explain <unit>` — print the shortest useful explanation for one rebuilt unit.
- `cargo rebuild-why compare <old> <new>` — classify what changed between two builds.
- `cargo rebuild-why audit-exactness <bundle>` — summarize which claims were imported, normalized, inferred, or still need manual review.
- `*.rebuildbundle.zip` — portable artifact for CI, issue filing, and “why did this rebuild?” debugging.

# What the crate should provide other people

1. **A boring per-run rebuild explanation artifact** instead of shell-and-log folklore.
2. **Fingerprint-delta receipts** that make cache invalidation reviewable.
3. **A shared cause vocabulary** for Cargo, editors, CI, and performance investigations.
4. **A practical bridge** between raw timing/debug output and actionable team workflows.
5. **A compact witness** when shared-cache or wrapper assumptions are the real culprit.
6. **A stable import path** from evolving Cargo sessions/reports into something downstream tools can rely on.
7. **A visible baseline-selection story** so a reviewer knows why this comparison window was chosen.
8. **An exactness ledger** so unstable Cargo wording and downstream inference never get blurred into fake certainty.
9. **A reverse-impact report** that separates observed fanout from proven interface change.

# Persona / who it’s for

- developers waiting on slow rebuilds
- workspace and monorepo maintainers
- CI/build engineers
- Cargo-adjacent performance tool authors
- support engineers trying to explain “worked in editor, rebuilt in CI”

# Users & user stories

- **Developer**: “I changed one file; tell me why half the workspace rebuilt.”
- **CI engineer**: “Attach one artifact to the failing job that explains why cache reuse collapsed.”
- **Reviewer**: “Show me whether this rebuild storm came from public-interface drift, profile drift, or changed environment assumptions.”
- **Tool author**: “Consume rebuild-cause data through one schema instead of scraping logs and HTML.”
- **Maintainer using nightly Cargo reports**: “Freeze this session into a stable bundle I can share without telling everyone to use the same nightly.”

# Prior art (and why it’s insufficient)

- Cargo timing reports are useful but intentionally human-oriented.
- Cargo debug/fingerprint logging is powerful but too low-level and too improvised for ordinary review workflows.
- Cargo’s new `-Zbuild-analysis` + `cargo report` work is the right substrate, but its tracking issue is still open and still discussing schema/format and UX questions.
- Build-dir layout and user-wide-cache work explain why reuse and locking matter, but they do not answer one support incident by themselves.
- `cargo-build-insights` in this archive already targets persisted historical analysis, not compact per-run explanation bundles.
- `Cargo Lock Contention Witness Kit` in this archive already isolates *live blocking*; it should be importable context here, not swallowed whole.

What remains missing is a **fingerprint-delta / per-unit-cause / cache-conflict receipt layer** that captures one rebuild event cleanly enough for humans and tools to share.

## 2026-03-08 upstream-fit refresh

Cargo’s `-Zbuild-analysis` work makes this proposal **more buildable**, not less necessary.

That upstream work is adding persisted build sessions plus `cargo report sessions`, `cargo report rebuilds`, and `cargo report timings`, but the tracking issue is still explicitly carrying open questions around programmable formats, schema evolution, and end-user wording.

That means this crate should not compete with Cargo by inventing a parallel build-analysis recorder first.
It should instead provide the layer that ordinary teams actually need above that substrate:

- a stable, redaction-aware import path from evolving Cargo reports,
- a compact session index and comparison baseline,
- conservative rebuild-cause receipts that remain reviewable even when Cargo internals change,
- and one portable bundle suitable for CI, issue filing, and support handoff.

In other words: Cargo can evolve the **recording/query substrate**; this crate should own the **boring receipt, diff, redaction, and workflow contract** above it.

# Design goals

1. **Per-run explainability** — optimize for one concrete rebuild mystery first.
2. **Observed-facts first** — separate directly observed data from conservative inference.
3. **Evidence-lane explicit** — record whether a fact came from imported Cargo reports, live command capture, or optional fingerprint-log overlays.
4. **Cache-aware** — lock/contention/wrapper/target-dir facts must be part of the story.
5. **Diff-friendly** — comparing two runs should yield categorized reasons, not just raw logs.
6. **Cargo-adjacent** — consume current Cargo outputs without pretending unstable internals are fixed forever.
7. **Import-friendly** — treat `cargo report` sessions and JSON/event output as preferred substrate when available, not as a competing product surface.

# Minimal cause vocabulary (freeze early)

The first useful taxonomy should stay small:

- `fingerprint_changed`
- `public_interface_possible`
- `target_profile_split`
- `wrapper_or_flags_changed`
- `tool_invocation_drift_possible`
- `build_script_or_proc_macro_input_changed`
- `cache_conflict_possible`
- `manual_review_required`

Each verdict should preserve:
- the supporting facts,
- whether the verdict is directly observed or conservatively inferred,
- and which evidence lane supplied the fact.

# Implementation shape in theory and practice

## Three evidence lanes

### 1. Imported Cargo report lane
Best when nightly `-Zbuild-analysis` is available.

Inputs:
- session ID
- `cargo report sessions`
- `cargo report rebuilds`
- `cargo report timings`

Why it matters:
- lets the crate piggyback on the official recorder,
- keeps the crate from reverse-engineering everything from scratch,
- and gives a good path for future compatibility as Cargo improves.

### 2. Live capture lane
Best stable-first path.

Inputs:
- command line
- target/profile/workspace selection
- env/wrapper/config roots
- `--message-format=json`
- optional timing artifacts

Why it matters:
- provides value on stable Cargo today,
- captures workflow assumptions even when Cargo cannot explain every rebuild cause,
- and creates a conservative support bundle rather than a nightly-only niche.

### 3. Fingerprint overlay lane
Optional deeper evidence.

Inputs:
- targeted fingerprint logs
- wrapper/tool hints
- imported contention witness or path-layout witness artifacts

Why it matters:
- explains more when teams opt in,
- but stays an overlay so 0.1 is not blocked on unstable internals or noisy logs.

## Product shape

The crate should be two things:

### Library
- stable schema types
- import adapters
- redaction helpers
- diff/classification engine

### Cargo subcommand
- `capture`
- `freeze-session`
- `compare`
- `explain`
- `bundle doctor` (short textual summary over an existing bundle)

The CLI should stay small and artifact-first.
Do not turn the first release into a new profiler UI.

# MVP surface

- Minimal types: `RebuildContext`, `SessionIndex`, `UnitRebuild`, `FingerprintDelta`, `CacheConflictReport`, `RebuildReceipt`, `TimingsPointer`, `RebuildBundle`
- Minimal functions:
  - `capture_run_context()`
  - `import_build_analysis_session()`
  - `classify_unit_rebuilds()`
  - `summarize_fingerprint_delta()`
  - `detect_cache_conflicts()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `timings`
  - `fingerprint-logs`
  - `ci`

# Compatibility story

- Works with current Cargo timing output, `--message-format=json`, optional debug/fingerprint logs, and the new `-Zbuild-analysis` session/report surface.
- Can integrate with future finer-grained Cargo cache/build-unit surfaces when available.
- Must label whether a cause came from direct evidence, normalized heuristics, imported Cargo reports, or manual-review-required inference.
- Should remain useful even if relink/reuse improves upstream, because teams will still need explanations for the misses.
- Must stay valuable even while Cargo’s unstable report/session format evolves, by freezing its own exported bundle schema conservatively.

# Conformance & fixtures

- `build_analysis_import_only` — import a Cargo session and freeze it into a smaller stable receipt.
- `check_then_build_workspace` — a tool-oriented invocation is followed by a fuller build and reuse drops.
- `wrapper_rustflags_drift` — changed wrapper or flag posture invalidates reuse.
- `shared_target_lock_hint` — concurrent tool or shared cache root creates conflict hints rather than a clean proof.
- later: `source_edit_reverse_dep_fanout` — private edit still causes dependent rebuilds.

Goldens should cover:

- `fingerprint_changed`
- `wrapper_or_flags_changed`
- `tool_invocation_drift_possible`
- `cache_conflict_possible`
- `public_interface_possible`
- `manual_review_required`

# Path to boring stability

- Stabilize cause categories before broadening data ingestion.
- Start with read-only capture and comparison.
- Keep the first schema small and explanation-heavy.
- Prefer explicit unknowns over pretending Cargo exposed full invalidation provenance.
- Treat timing HTML as a pointer, not the core contract.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one build or check run, classify rebuilt versus reused units conservatively, summarize visible fingerprint changes, optionally import a Cargo build-analysis session, and export a shareable rebuild bundle.

# De-risk plan

1. Start with one-run and two-run comparisons rather than historical warehousing.
2. Make imported Cargo sessions first-class, but never required for baseline usefulness.
3. Treat fingerprint details as optional overlays when Cargo logs are available.
4. Validate on workspaces with known `cargo check` / `cargo build` / rust-analyzer contention pain.
5. Keep the cause taxonomy intentionally coarse until real fixtures prove it needs more detail.

# Non-goals

- Not a replacement for Cargo.
- Not a full profiler or build dashboard.
- Not an exact model of rustc incremental compilation internals.
- Not a promise to explain every rebuild without optional evidence sources.
- Not the historical warehouse / regression-adjudication layer from **P-0035**.
- Not a substitute for the more specialized lock-contention witness from **P-0490**.

# Architecture & API sketch

```rust
pub enum EvidenceLane {
    CargoReportImport,
    LiveCapture,
    FingerprintOverlay,
}

pub enum RebuildCause {
    FingerprintChanged,
    PublicInterfacePossible,
    TargetProfileSplit,
    WrapperOrFlagsChanged,
    ToolInvocationDriftPossible,
    BuildScriptOrProcMacroInputChanged,
    CacheConflictPossible,
    ManualReviewRequired,
}

pub struct UnitRebuild {
    pub unit: String,
    pub status: ReuseStatus,
    pub causes: Vec<RebuildCause>,
    pub evidence_lanes: Vec<EvidenceLane>,
}

pub fn capture_run_context(root: &Path) -> Result<RebuildContext>;
pub fn import_build_analysis_session(session_id: &str) -> Result<SessionIndex>;
pub fn classify_unit_rebuilds(ctx: &RebuildContext) -> Result<Vec<UnitRebuild>>;
pub fn summarize_fingerprint_delta(old: &RebuildBundle, new: &RebuildBundle) -> FingerprintDelta;
pub fn detect_cache_conflicts(ctx: &RebuildContext) -> CacheConflictReport;
```

Bundle draft:
- `rebuild-context.toml`
- `session-index.json`
- `unit-rebuilds.json`
- `fingerprint-delta.json`
- `cache-conflict.report.json`
- `rebuild.receipt.json`
- `timings-pointer.json`
- `evidence-source.receipt.json`
- `exactness.report.json`
- `notes.md`

# Security / safety model

- Support redaction of local paths, usernames, and private workspace names in exported bundles.
- Never claim a rebuild cause is certain when it was inferred from partial logs.
- Preserve wrapper/toolchain/profile/target assumptions exactly.
- Keep optional debug logging opt-in and clearly disclosed in receipts.
- Treat imported Cargo report data as authoritative about what Cargo recorded, not as proof that Cargo exposed every relevant cause.

# Maintenance & governance plan

- Track Cargo build-dir-layout and reuse-related work closely.
- Track `-Zbuild-analysis` session/report changes and keep the import layer conservative.
- Keep cause categories small, stable, and aligned with observed evidence.
- Maintain fixtures for lock contention, wrapper drift, build-analysis session import, wording drift, compile-time-deps parity overlap, and common cache splits.
- Publish guidance for interpreting “public-interface-change possible” conservatively.

# Milestones

## 0.1
- one-run capture
- `build_analysis_import_only`
- unit classification
- receipt writer
- first stable schemas for `unit-rebuilds`, `rebuild.receipt`, `session-index`, `timings-pointer`, `evidence-source.receipt`, and `exactness.report`

## 0.2
- two-run comparison
- `fingerprint-delta` summaries
- `cache-conflict` reporting
- `check_then_build_workspace` and `wrapper_rustflags_drift` fixtures

## 1.0
- stable bundle schema
- curated fixture corpus
- adapters for newer Cargo build-unit signals
- integrations that can ingest P-0490 lock-contention artifacts instead of duplicating them

# Open questions

- What is the smallest useful rebuild-cause taxonomy that still helps real teams?
- How much optional fingerprint logging should the crate rely on for a good MVP?
- Should cache-conflict reporting live in the core schema or as an optional overlay once Cargo build-dir work advances?
- Which imported Cargo report facts are stable enough to normalize immediately and which should be preserved as opaque provenance?

# Sources

- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Relink don’t Rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo build command docs (`--timings`): https://doc.rust-lang.org/cargo/commands/cargo-build.html
- Cargo unstable docs (`-Zbuild-analysis`, `cargo report`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- This development-cycle in Cargo 1.94: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Tracking issue for `-Zbuild-analysis`: https://github.com/rust-lang/cargo/issues/15844
- “Provide better diagnostics for why crates are rebuilt”: https://github.com/rust-lang/cargo/issues/2904
- This development-cycle in Cargo 1.84 (`RUSTFLAGS` and caching): https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/
