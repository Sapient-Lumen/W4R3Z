---
id: P-0478
title: Cargo Future-Incompat Triage Kit — capture locks, owner ledgers, waiver expiry, and release-gate receipts
status: idea
domains: [cargo, dependency-management, diagnostics, upgrade-planning, ci, release-engineering]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
  - https://doc.rust-lang.org/cargo/commands/cargo-report.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://doc.rust-lang.org/beta/rustc/json.html
---

# Problem

Cargo already has real future-incompatibility substrate:

- it checks future-incompatible warnings in all dependencies,
- it can print a full report during a build,
- `cargo report` can revisit stored reports and filter by report id or package,
- Cargo has a dedicated `[future-incompat-report]` config surface,
- and Cargo already caches future-incompat reports strongly enough that the build-analysis goal can cite them as one of the few persisted build-adjacent artifacts.

That means the missing crate is **not** “make Cargo notice future incompatibility”.
Cargo already notices it.

The missing crate is the boring layer above that substrate:

- what exact build or report lookup produced this snapshot,
- which findings are new versus historical,
- who owns each warning in a real workspace,
- which waivers are temporary and when they expire,
- which release branch or milestone should block on them,
- and how to compare toolchain bumps without pasting terminal output into issue trackers.

The problem gets sharper as the contents of future-incompat reports expand.
Rust release notes already record that **const-eval errors are now included in future incompatibility reports**, which means a real triage layer must handle findings that appear or reclassify across toolchain eras without pretending they are all the same old lint backlog.

# Main judgment

A worthy crate contribution here is a **future-incompat triage kit**:

- capture Cargo's existing report surfaces into durable artifacts,
- keep ownership / waiver / release-window memory next to those artifacts,
- make diffing and gating reviewable,
- and stay honest about whether a result came from a live build, a cached report id, or a later package-filtered recall.

This is an unusually good crate lane because it gives other people a thing Cargo still does not hand them directly:
**shared memory with receipts**.

## 2026-03-20 visibility / suppression refinement

One more ordinary bluff is still available on top of the current Cargo substrate:

> a team can treat “the build looked clean” as proof that no future-incompat debt exists, even though Cargo and rustc can preserve findings that were only visible in a recalled report, hidden by a package-filtered view, or suppressed in user-facing output while still present in machine-readable capture.

Current official surfaces make that sharper now than it used to be:

- Cargo can show the full report during a build or later via `cargo report future-incompat --id ...`;
- Cargo can narrow that recall to one package, which changes what is visible without changing the original workspace capture;
- Cargo config can suppress terminal notifications with `future-incompat-report.frequency = "never"`;
- and rustc's future-incompat JSON explicitly says diagnostic information may still be emitted even when the warning itself was suppressed by `#[allow]` or `--cap-lints`.

That means the sharper missing crate layer is no longer only **memory / ownership / waiver / release-gate**.
It is also **visibility honesty**.

This pass therefore promotes two more first-class artifacts for **P-0478**:

- `finding-visibility.report.json` — whether a finding was `terminal_visible`, `report_visible_only`, `suppressed_but_recorded`, `package_filtered_hidden`, or otherwise visibility-limited;
- `suppression-basis.receipt.json` — why that visibility posture happened and whether the result still counts as `latent_debt`, `display_suppressed`, or `recall_narrowed`.

A worthy crate here should now help other people answer not just “what findings exist?” but also:

- **what did reviewers actually see,**
- **what stayed latent but recorded,**
- **what became hidden only because the recall surface narrowed,**
- and **what release-gate meaning still remains honest.**

# What it should provide other people

1. **A capture lock** that says exactly how the report was obtained.
2. **A normalized finding snapshot** that survives past one terminal session.
3. **An owner-aware triage ledger** so teams stop rediscovering the same dependency risk.
4. **A waiver ledger with expiry** so tolerated debt has a clock and a named owner.
5. **A release-gate report** that distinguishes advisory backlog from actual shipment blockers.
6. **A remediation-candidate report** that points at likely dependency updates or escalation paths without pretending they are guaranteed fixes.
7. **An evidence-source receipt** that says whether the bundle came from a live command, a recalled report id, or a cached/latest view.
8. **A diff surface** that compares snapshots across lockfile changes, branch cutoffs, or toolchain bumps.

# Proposed artifacts

- `future-incompat.capture-lock.json`
  - workspace / package selection
  - command family (`build`, `check`, `rustc`, or report recall)
  - target/profile scope
  - toolchain channel / version string if known
  - acquisition mode (`live_build_flag`, `report_by_id`, `latest_cached`, `package_filtered_recall`)
  - policy knobs such as advisory vs blocking mode

- `finding-snapshot.report.json`
  - normalized list of findings from one capture
  - package identity
  - report id if Cargo provided one
  - diagnostic fingerprint / message digest / category
  - whether the finding was observed directly in this capture or reconstructed from a later lookup

- `triage-ledger.report.json`
  - one durable ledger of findings across time
  - first-seen / last-seen timestamps
  - owner and escalation path
  - release-window classification
  - current triage status: `new`, `persisting`, `resolved`, `waived`, `expired_waiver`, `unknown_owner`

- `owner-map.policy.json`
  - package-pattern → team / human / escalation group mapping
  - optional branch or workspace overrides

- `waiver-ledger.policy.json`
  - explicit temporary tolerations
  - reason / approver / owner / expiry / review date
  - scope on which package / finding / toolchain window the waiver applies to

- `release-gate.report.json`
  - `ship_blockers`, `needs_review`, `advisory_only`, `resolved_since_last_cut`
  - summarized counts plus references into the ledger

- `remediation-candidates.report.json`
  - candidate dependency update paths
  - upstream issue / release references when known
  - confidence field so guesses stay labeled as guesses

- `evidence-source.receipt.json`
  - whether the report was captured from a live build or replayed via `cargo report`
  - whether the snapshot is exact, stale, conservative, or manual-review-required
  - whether package filtering happened after the original report was stored

- `future-incompat.diff.json`
  - `new`, `resolved`, `persisting`, `owner_changed`, `waiver_expired`, `reclassified_by_toolchain`, `needs_review`

- `*.futureincompat.zip`
  - portable artifact for CI, release meetings, and dependency-upgrade review

# Commands / UX sketch

- `cargo future-incompat capture`
  - run Cargo or recall an existing report and emit a bundle
- `cargo future-incompat triage`
  - apply owner maps, waivers, and release-window labels
- `cargo future-incompat diff old.zip new.zip`
  - produce a reviewable diff artifact
- `cargo future-incompat gate`
  - fail only on policy-relevant findings such as `new`, `expired_waiver`, or `unknown_owner`
- `cargo future-incompat explain <finding>`
  - summarize owner, waiver, last-seen status, and likely remediation path

# Persona / who it’s for

- workspace maintainers with many transitive dependencies
- release engineers who need a boring dependency-risk check before a cut
- platform teams managing ownership and waiver policy across many crates
- library maintainers who want warnings to become tracked work instead of terminal confetti

# User stories

- **Release maintainer**: “Show me only findings that still matter for the release branch and are not covered by an active waiver.”
- **Dependency owner**: “Tell me which warnings belong to my crate set and whether there is a plausible upgrade path.”
- **CI owner**: “Fail only on newly introduced or expired-waiver findings, not on the historical backlog.”
- **Toolchain upgrader**: “Compare the same workspace on two toolchains and tell me which findings were reclassified or newly surfaced.”
- **Reviewer**: “Open one zip and see capture truth, owner truth, waiver truth, and release truth without recreating the build.”

# Prior art (and why it’s insufficient)

- Cargo’s future-incompat report docs already describe detection and display.
- `cargo report` already recalls the latest or a chosen report id, and can narrow to a package.
- Cargo config already controls notification frequency.
- Cargo changelog history shows this surface has evolved over time, including command naming changes and fixes for duplicate saved reports.
- The build-analysis goal explicitly names future-incompat reports as one of the few persisted build-adjacent artifacts Cargo already has.

What is still missing is a **durable memory / ownership / waiver / release-gate layer** above those official surfaces.

# Design goals

1. **Memory-first** — preserve what was seen, when, and under what capture mode.
2. **Owner-first** — findings must become someone’s work or an explicitly accepted temporary risk.
3. **Release-aware** — distinguish backlog from actual shipment blockers.
4. **Toolchain-honest** — allow reclassification across compiler eras without pretending identity is perfect.
5. **Cargo-grounded** — preserve report ids, package ids, and raw Cargo facts whenever available.
6. **Diff-friendly** — across time, branch, and toolchain.
7. **Partial-data honest** — if remediation is guessed, say so.

# Scope boundaries

This crate is **not**:

- a replacement for Cargo’s built-in report display,
- a general dependency updater,
- a cargo-fix or lint-edit orchestration tool,
- a broad build-history warehouse,
- or a promise that every finding has an automatic remediation.

# MVP surface

## Core types

- `CaptureLock`
- `FindingSnapshot`
- `TriageLedger`
- `OwnerMapPolicy`
- `WaiverLedger`
- `ReleaseGateReport`
- `RemediationCandidates`
- `EvidenceSourceReceipt`
- `FutureIncompatDiff`
- `FutureIncompatBundle`

## Core functions

- `capture_bundle()`
- `recall_report_by_id()`
- `normalize_snapshot()`
- `apply_owner_map()`
- `apply_waivers()`
- `build_release_gate()`
- `diff_bundles()`
- `write_bundle()`

## Feature flags

- `cargo`
- `serde`
- `ci`
- `markdown`
- `owners`
- `remediation-hints`

# Architecture & API sketch

```rust
pub enum AcquisitionMode {
    LiveBuildFlag,
    ReportById,
    LatestCached,
    PackageFilteredRecall,
}

pub struct FindingKey {
    pub package_id: String,
    pub diagnostic_fingerprint: String,
    pub target_scope: Option<String>,
}

pub struct EvidenceSourceReceipt {
    pub acquisition_mode: AcquisitionMode,
    pub exactness: Exactness,
    pub cargo_report_id: Option<String>,
}

pub fn capture_bundle(root: &Path) -> Result<FutureIncompatBundle>;
pub fn recall_report_by_id(root: &Path, id: &str) -> Result<FutureIncompatBundle>;
pub fn apply_waivers(bundle: &mut FutureIncompatBundle, waivers: &WaiverLedger) -> Result<()>;
pub fn build_release_gate(bundle: &FutureIncompatBundle) -> ReleaseGateReport;
```

# Compatibility story

- Start with stable Cargo future-incompat reporting.
- Support both live `--future-incompat-report` capture and later `cargo report` recall.
- Preserve command-family differences (`build`, `check`, `rustc`, etc.) instead of flattening them.
- Treat finding identity across toolchain versions as best-effort and keep an explicit `reclassified_by_toolchain` state.
- Stay useful even if Cargo later grows richer report commands, because ownership / waivers / release policy still live above raw display.

# Conformance & fixtures

This lane should now be fixture-first.

Minimum scenario families:

1. **`transitive_new_warning_unknown_owner/`**
   - new finding appears in a transitive dependency
   - no owner map match yet
   - release gate should say `needs_review`

2. **`waiver_expires_on_release_branch/`**
   - historical finding persists
   - waiver was valid on main but expired for the release cut
   - release gate should surface `expired_waiver`

3. **`toolchain_bump_const_eval_reclassification/`**
   - newer compiler surfaces a const-eval future incompatibility that older snapshots did not include
   - diff should say `reclassified_by_toolchain`, not blindly “brand new ownerless bug”

Goldens should cover:
- `new`
- `persisting`
- `resolved`
- `unknown_owner`
- `waived`
- `expired_waiver`
- `reclassified_by_toolchain`
- `advisory_only`
- `ship_blocker`

# Path to boring stability

1. Stabilize the capture / snapshot / ledger / gate vocabulary first.
2. Keep waiver and owner formats tiny and explicit.
3. Let remediation hints stay conservative and optional.
4. Prefer exactness receipts over hidden inference.
5. Build credibility on a few real workspaces before adding broad automation.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 28/30**

# Minimum lovable MVP

A library and cargo subcommand that can capture or recall one Cargo future-incompat report, normalize it into a structured snapshot, apply owner/waiver policy, and emit a release-gate bundle that is reviewable in CI and release meetings.

# De-risk plan

1. Start with live-capture plus recall-by-id, not with deep remediation automation.
2. Keep finding identity conservative and visible.
3. Validate on one small library workspace and one large application workspace.
4. Add const-eval/toolchain reclassification fixtures early so the ledger learns compiler-era drift from day one.

# Open questions

- What is the smallest durable identity for a finding across toolchain releases?
- When should package-filtered recall be considered exact versus conservative?
- Which remediation hints are useful enough to include without creating false confidence?
- Should waivers be branch-scoped, milestone-scoped, or both?

# Sources

- Cargo future incompat report reference: https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- `cargo report` docs: https://doc.rust-lang.org/cargo/commands/cargo-report.html
- Cargo configuration reference (`[future-incompat-report]`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo build analysis goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Rust release notes (const-eval errors added to future incompat reports): https://doc.rust-lang.org/beta/releases.html
- Cargo changelog (`cargo report` evolution and duplicate-save fix): https://doc.rust-lang.org/cargo/CHANGELOG.html
