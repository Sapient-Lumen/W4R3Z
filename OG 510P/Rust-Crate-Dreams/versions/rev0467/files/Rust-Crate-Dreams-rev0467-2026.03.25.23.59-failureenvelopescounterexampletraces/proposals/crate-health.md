---
id: P-0011
title: Crate Health Contract Kit — maintenance windows, succession maps, and support-intent receipts
status: idea
domains: [ecosystem, crates-io, maintenance, metadata, governance]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
  - https://doc.rust-lang.org/cargo/reference/manifest.html#the-badges-section
  - https://github.com/rust-lang/rfcs/blob/master/text/3537-msrv-resolver.md
  - https://github.com/rust-lang/crates.io/issues/2437
  - https://internals.rust-lang.org/t/more-metrics-for-crate-maintenance-status-in-crates-io/20855
  - https://rustfoundation.org/strategic-plan/
  - https://openssf.org/blog/2025/09/23/open-infrastructure-is-not-free-a-joint-statement-on-sustainable-stewardship/
  - https://docs.github.com/articles/about-code-owners
  - https://docs.github.com/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability
---

# Problem

Rust users increasingly need more than “popular” and more than “published recently.”
They need to know whether a crate is:

- still actively developed,
- quietly but honestly reactively maintained,
- only taking critical fixes,
- entering a sunset phase,
- or depending on one maintainer with no visible backup.

Today those answers are scattered across:

- Cargo badge metadata,
- crate pages,
- README notes,
- GitHub issue response patterns,
- RustSec / security surfaces,
- trusted-publishing settings,
- and release history heuristics.

Worse, the old maintenance-status story has a known staleness problem: the long-running crates.io issue about moving maintenance status into the UI exists because keeping the field in `Cargo.toml` means maintainers may need a **new release just to update support posture**.

The missing crate is not another popularity score and not a moral ranking of maintainers.

The missing crate is a **crate health contract kit** that gives other people one compact, reviewable answer to the support and stewardship posture of a crate.

# What it provides

- `crate-health.toml` — maintainer-authored health declaration with explicit scope and support horizon.
- `health-profile.report.json` — normalized declared posture such as `active_development`, `reactive_maintenance`, or `critical_fixes_only`.
- `maintenance-window.report.json` — what kinds of changes are still in scope and for which version window.
- `succession-map.report.json` — backup/handoff/successor posture.
- `support-intent.report.json` — MSRV, security contact, issue-response, and release-expectation posture.
- `health-check.report.json` — conservative consistency check that flags gaps and overclaims.
- `maintenance-coverage.report.json` — explicit map of keep-the-lights-on and enable-evolution work classes, coverage state, and visible gaps.
- `registry-signal.import.json` — imported crates.io and repository stewardship-adjacent facts, kept distinct from declarations.
- `routing-drift.diff.json` — diffable change report for routing, channels, and continuity posture across snapshots.
- `health-support-bundle.manifest.json` — portable manifest joining declared artifacts, imported artifacts, and manual-review gaps.
- `cargo crate-health capture` — capture maintainer declarations plus imported registry/repo signals.
- `cargo crate-health check` — run consistency checks and export warnings/manual-review zones.
- `cargo crate-health diff` — compare two health bundles across releases or stewardship changes.
- `*.cratehealthbundle.zip` — portable artifact for pathfinder tools, platform teams, and downstream adopters.

# What the crate should provide other people

1. **One health profile** instead of README / issue / registry spelunking.
2. **One maintenance-window answer** instead of guessing from last publish date.
3. **One succession map** instead of unspoken bus-factor risk.
4. **One support-intent receipt** that distinguishes explicit promises from imported signals.
5. **One maintenance-coverage report** that says which invisible work is actually covered instead of assuming one status word tells the whole story.
6. **One imported-signal receipt** that keeps crates.io and host-platform context useful without letting it impersonate maintainer promises.
7. **One routing drift report** that says what actually changed across releases, transfers, or stewardship edits.
8. **One portable support bundle** another team can inspect without reconstructing the support story from scattered surfaces.
9. **One conservative health check** that refuses to flatten security/publishing signals into support truth.

# Persona / who it’s for

- crate maintainers
- downstream adopters evaluating survivability risk
- platform teams curating internal approved-crate sets
- pathfinder / policy / docs tooling authors
- ecosystem stewards trying to improve support clarity without inventing a global score

# Users & user stories

- **Maintainer**: “Publish an honest reactive-maintenance promise without cutting a fake release just to update metadata.”
- **Platform team**: “Import one bundle that tells us whether this dependency has a support horizon and succession path.”
- **User choosing between crates**: “Distinguish stable-but-supported from quietly abandoned.”
- **Security reviewer**: “See whether trusted publishing and security-tab visibility are being over-read as actual maintainer support.”

# Prior art (and why it’s insufficient)

- Cargo badge metadata and the historical maintenance-status field exist, but they can go stale and are too narrow.
- crates.io now has stronger registry substrate: a Security tab, trusted publishing, report-crate flows, publish notifications, and other support signals.
- The MSRV-resolver RFC explicitly notes that mutable crates.io metadata could let Cargo report whether a version is still supported.
- Community discussion keeps asking for better maintenance metrics, and lib.rs already uses heuristics beyond the badge field.

What remains missing is a **crate-authored support/succession contract** that other tools can import without pretending heuristics are the same thing as intent.

# Design goals

1. **Contract, not score** — publish support/stewardship posture rather than one number.
2. **Maintenance-class aware** — keep keep-the-lights-on duties distinct from contributor-enabling duties.
3. **Mutable without fake releases** — health posture should be easy to update outside a code release cadence.
4. **Imported-versus-declared honesty** — never blur registry signals into maintainer promises.
5. **Succession is first-class** — health should say who carries the crate next, not only whether it looks busy today.
6. **Composable** — pathfinder, off-ramp, and policy tools should be able to import the artifacts.

# MVP surface

- Minimal types: `HealthProfileReport`, `MaintenanceWindowReport`, `SuccessionMapReport`, `SupportIntentReport`, `MaintenanceCoverageReport`, `RegistrySignalImport`, `RoutingDriftDiff`, `HealthSupportBundleManifest`, `HealthCheckReport`
- Minimal functions:
  - `capture_health_profile()`
  - `capture_maintenance_window()`
  - `capture_succession_map()`
  - `capture_support_intent()`
  - `capture_maintenance_coverage()`
  - `check_health_consistency()`
  - `diff_health_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cratesio-import`
  - `github-import`
  - `serde`
  - `bundle`

# Compatibility story

- Starts with maintainer-authored files plus imported crates.io/repo signals.
- Keeps room for future mutable crates.io metadata without depending on it today.
- Can be consumed by pathfinder and policy tooling without becoming a ranking engine.
- Degrades honestly to `manual_review_required` when support or succession posture is unclear.

# Conformance & fixtures

- quiet-but-supported release stream
- frozen-but-supported maintenance mode
- single-maintainer crate with explicit backup contact
- single-maintainer crate with no backup disclosure
- quiet-but-supported crate with lights-on coverage but weak review capacity
- fast-moving crate with feature momentum but weak CI/security/docs ownership
- sunset-in-progress with no successor or horizon
- trusted-publishing/security signals present but support intent absent

# Path to boring stability

- Stabilize `health-profile`, `maintenance-window`, `succession-map`, and `health-check` before adding many optional analytics.
- Treat `manual_review_required` as a first-class honest outcome.
- Prefer importing a few boring registry/repo signals well over scraping dozens of soft heuristics.
- Keep pathfinder choice, off-ramp exit, and trust/security posture as adjacent but separate lanes.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A crate that captures one maintainer-authored health file, imports a small set of crates.io/repo signals, emits health-profile / maintenance-window / succession-map / support-intent / maintenance-coverage reports, and produces a conservative health-check verdict another team can actually review.

# De-risk plan

1. Keep `0.1` focused on support horizon and succession, not giant analytics.
2. Treat release cadence only as an imported signal, not the verdict.
3. Keep registry-signal imports small and explicit.
4. Prove usefulness first with pathfinder and internal approved-dependency workflows.

# Non-goals

- Not a global crate ranking or recommendation engine.
- Not a replacement for off-ramp / successor planning.
- Not a security score.
- Not a hosted social dashboard telling maintainers whether they are “good enough.”

# Architecture & API sketch

```rust
pub fn capture_health_profile(input: &HealthInput) -> Result<HealthProfileReport>;
pub fn capture_maintenance_window(input: &HealthInput) -> Result<MaintenanceWindowReport>;
pub fn capture_succession_map(input: &HealthInput) -> Result<SuccessionMapReport>;
pub fn capture_support_intent(input: &HealthInput) -> Result<SupportIntentReport>;
pub fn capture_maintenance_coverage(input: &HealthInput) -> Result<MaintenanceCoverageReport>;
pub fn check_health_consistency(bundle: &HealthBundle) -> Result<HealthCheckReport>;
pub fn write_bundle(bundle: &HealthBundle, out: &Path) -> Result<()>;
```

Bundle draft: `crate-health.toml`, `health-profile.report.json`, `maintenance-window.report.json`, `succession-map.report.json`, `support-intent.report.json`, `maintenance-coverage.report.json`, `work-routing.report.json`, `response-channel.receipt.json`, `continuity-backstop.report.json`, `registry-signal.import.json`, `routing-drift.diff.json`, `health-support-bundle.manifest.json`, `health-check.report.json`, `notes.md`.

# Security / safety model

- Do not treat absence of advisories as proof of active maintenance.
- Do not treat trusted publishing as proof of support horizon.
- Keep imported signals auditable and versioned.
- Avoid scraping private or unstable maintainer data.

# Maintenance & governance plan

- Version the health artifacts carefully.
- Keep importers modular.
- Publish lane boundaries so future revisions do not flatten health into pathfinder, off-ramp, or trust scoring.
- Prefer opt-in, explicit declarations over aggressive inference.

# Milestones

## 0.1
- health profile
- maintenance window
- succession map
- support intent
- maintenance coverage
- health check

## 0.2
- diff support
- richer repo/import adapters
- org-policy export helpers

## 1.0
- stable artifact core
- ecosystem integration guidance
- importer compatibility matrix

# Open questions

- Which health fields should be mutable without a new crate release?
- What is the smallest honest succession vocabulary?
- How should supported-version windows interact with MSRV policy and off-ramp planning?

# 2026-03-21 maintenance-coverage refresh — stewardship classes must stay explicit

This proposal is stronger now because the next useful move was **not** another crate ranking, maintainer leaderboard, or funding dashboard.
It was to make **P-0011** honest about the actual maintenance work a crate is promising to cover.

Three things needed to become explicit that had still been too implicit:

- **maintenance-coverage truth** — which keep-the-lights-on and enable-evolution duties are actually covered;
- **duty-map honesty** — whether issue triage, CI breakage, security response, docs freshness, review capacity, and contributor enablement are all being flattened into one status word;
- **visible-versus-invisible work balance** — whether recent releases or visible feature work are masking gaps in the less glamorous maintenance classes that keep a crate usable.

That boundary matters because current official signals now say several awkward things very plainly:

- the Inside Rust maintenance post says maintenance includes issue triage, bug fixing, CI failures, security incidents, performance regressions, dependency updates, docs upkeep, review, refactoring, and mentoring;
- the State of Rust survey says concern about developer and maintainer support ticked upward;
- Cargo still documents maintenance status mainly as badge-era metadata and explicitly notes crates.io does not currently use it;
- the crates.io UI/API issue exists because release-bound status tends to go stale;
- crates.io now exposes stronger imported signals such as the Security tab, Trusted Publishing, SLOC, and `pubtime`, but those still do not name who owns invisible maintenance work.

So the sharper `0.1` is now:

- a small capture/check/diff/bundle tool,
- a `maintenance-coverage.report`,
- a conservative split between **keep_the_lights_on** and **enable_evolution**,
- and a health check that fails closed when important duty classes are only implied or unowned.

# Sources

- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- What is maintenance, anyway?: https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- crates.io development update (2026): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io development update (2025): https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- Cargo manifest badges docs: https://doc.rust-lang.org/cargo/reference/manifest.html#the-badges-section
- MSRV resolver RFC: https://github.com/rust-lang/rfcs/blob/master/text/3537-msrv-resolver.md
- crates.io maintenance-status issue: https://github.com/rust-lang/crates.io/issues/2437
- maintenance-metrics discussion: https://internals.rust-lang.org/t/more-metrics-for-crate-maintenance-status-in-crates-io/20855


# 2026-03-22 routing / continuity refresh — stewardship must be operational

This proposal is stronger now because the next useful move was **not** more status words.
It was to make **P-0011** honest about where maintenance work actually goes.

Three things needed to become explicit that had still been too implicit:

- **work-routing truth** — where ordinary bugs, docs drift, CI breakage, release problems, and security incidents are supposed to enter;
- **response-channel truth** — which routes are public, private, structured, ad-hoc, or still manual-review-only;
- **continuity-backstop truth** — what keeps the crate responsive when the obvious maintainer is absent, overloaded, or stepping back.

That boundary matters because current official and ecosystem signals now say several awkward things very plainly:

- the Inside Rust maintenance post says maintenance includes issue triaging, bug fixing, CI failures, security incidents, performance regressions, dependency updates, docs freshness, review, and contributor enablement;
- the State of Rust survey says concern about developer and maintainer support ticked upward while online documentation remains the preferred canonical reference;
- the Rust Foundation strategic plan makes **Sustainable Maintenance** a core pillar;
- the open-infrastructure stewardship statement says ecosystems need to move from invisible dependence to shared responsibility;
- crates.io now exposes stronger support-adjacent signals such as the Security tab, Trusted Publishing Only Mode, SLOC, and `pubtime`, but those still do not say where maintenance work goes;
- GitHub’s CODEOWNERS and private vulnerability-reporting features are useful substrate, but they still do not by themselves define a full crate stewardship contract.

So the sharper next pass is now:

- a small capture/check/diff/bundle tool,
- a `work-routing.report`,
- one or more `response-channel.receipt` artifacts,
- a `continuity-backstop.report`,
- and a conservative health check that fails closed when route or backstop claims are only implied.
