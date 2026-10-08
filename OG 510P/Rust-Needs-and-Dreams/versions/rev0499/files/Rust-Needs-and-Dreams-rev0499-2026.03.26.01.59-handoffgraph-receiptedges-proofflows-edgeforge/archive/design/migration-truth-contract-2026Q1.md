## Execution addendum (rev0421)
For questions about what the archive's **release / upgrade portfolio seam** should actually ship, read `design/migration-public-api-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- keep **Migration Truth Contract** as the change-program / upgrade contract;
- do **not** promote a new frontier here;
- and treat the new blueprint as the **composition layer** that carries imported migration-program truth together with release-boundary evidence into bounded downstream handoffs.

# Design: Migration Truth Contract 2026Q1

## Goal
Promote the archive's existing migration substrate into a first-class **Migration Truth Contract**: a reviewable boundary for **what exact Rust subject state a project started from, what destination state it intended to reach, which edits were only suggested versus deliberately applied, what compatibility/support/docs/downstream evidence was actually imported, what waivers or partial residue remained, and what later release / policy / support / assistant consumers may legitimately conclude**.

This contract should sit:
- **above** shell history, CI YAML, issue comments, ad hoc branch discipline, and maintainer memory;
- **below** broader release, support, compatibility, and policy narratives;
- and **beside** Reviewable Edit, Compatibility Claims, Semantic Context, Maintenance Reality, Distribution, and Defect Escalation rather than replacing any of them.

The point is not to invent one universal upgrade bot.
The point is to stop losing truth whenever a Rust team says “we migrated this crate/workspace” and nobody can later tell whether that meant an edition ratchet, a `rust-version` policy change, a dependency wave, a semver-sensitive public API review, or all five at once.

## Why this seam matters now
The case for a first-class migration-truth contract is much stronger in 2026 than it was even a year ago:
- the Edition Guide still frames migration as a staged workflow that can require multiple passes, configuration slicing, and manual follow-up rather than one magic command;
- Cargo's `cargo fix` docs still say edition migration often needs multiple feature/target runs and can leave broken code for manual inspection;
- Rust 1.85 / Rust 2024 says `cargo fix` output is intentionally conservative and should not be treated as a recommendation;
- Cargo's 1.90 development-cycle report says the current `cargo fix` architecture is slow, hard to make selective, and awkward for interactive flows, while `cargo-fixit` proved a top-level orchestration approach;
- Cargo's `rust-version` docs say mixed workspace policies make verification complicated because dependencies are unified across semver-compatible versions;
- the 2026 flagship slate still includes **public/private dependencies** and **SBOM support**, which sharpens the downstream consequences of API-sensitive upgrades;
- the cargo-semver-checks goals still say cross-crate items and precise type-sensitive compatibility data remain on the path toward Cargo integration;
- docs.rs now hosts rustdoc JSON directly, which makes documentation/API imports more portable than before;
- and the 2025 State of Rust survey still says docs remain canonical while editor/LLM-mediated learning is rising, which raises the value of durable migration artifacts that survive past the original shell session.

That combination means the missing contribution is no longer “a nicer wrapper around `cargo fix`” or “a dependency-bump bot with better PR comments”.
It is a **portable migration-program contract**.

## References (signals)
- Edition Guide: transitioning and advanced migrations:
  https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo fix docs:
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Rust 1.85 / Rust 2024 announcement:
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo 1.90 development cycle (`cargo fix` architecture):
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- 2025 GSoC results (`cargo-fixit`, semver checks work):
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo `rust-version` docs and Rust 2024 resolver docs:
  https://doc.rust-lang.org/cargo/reference/rust-version.html
  https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
- Rust in 2026 / flagship themes:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- public/private dependencies goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- cargo-semver-checks goals:
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- docs.rs rustdoc JSON:
  https://docs.rs/about/rustdoc-json
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Working thesis
A worthy contribution here should make it easy to answer all of these without opening CI logs, shell history, merge requests, and release notes side by side:
1. What exact **source state** did the subject begin in?
2. What exact **destination intent** was being pursued?
3. Which **configuration slices / packages / targets / features** were actually in scope?
4. Which edits were only **conservative tool output** and which were deliberate human migration choices?
5. What **compatibility / support / docs / downstream** evidence was actually imported?
6. What **waivers, residue, or partial completion** remained?
7. What later consumers may **honestly conclude** from the migration?

If the design cannot answer those questions, then Rust still lacks the boring handoff that serious changes need.

## Contract shape
Read the existing migration substrate as a contract with six visibly separate layers:

### 1) Source-state truth
The contract must preserve what the subject started from:
- edition, toolchain, `rust-version`, resolver posture;
- dependency posture, lockfile posture, public/private dependency posture where relevant;
- support envelope and docs/support assumptions;
- selected package / target / feature / profile slices.

### 2) Destination-intent truth
The contract must preserve what the project is trying to reach:
- desired edition / resolver / MSRV / dependency posture;
- compatibility expectations and release posture;
- required approval rules, success criteria, and non-goals;
- intended downstream consumers.

### 3) Mechanical-edit truth
The contract must preserve what edits were proposed and what happened to them:
- suggested fixes and their provenance;
- selection / ordering decisions;
- applied, rejected, deferred, and manual edits;
- config and manifest edits distinct from source edits.

### 4) Compatibility-import truth
The contract must preserve what consequences were actually checked:
- public API / semver imports;
- support-envelope changes;
- docs / examples / doctest validity;
- downstream or integration-test imports;
- explicit unknowns and unsupported areas.

### 5) Run / outcome truth
The contract must preserve what was actually exercised:
- executed steps and exercised slices;
- partial runs, blocked stages, and accepted waivers;
- final supported claim versus provisional or incomplete state;
- migration diff / before-after summary.

### 6) Consumer-handoff truth
The contract must tell later consumers what they may honestly import:
- release and changelog consumers can import the migration outcome without re-running it;
- support and maintenance consumers can import bounded support changes and residue;
- downstream packagers and policy review can import compatibility-sensitive conclusions;
- assistants may summarize the pack, but must not claim more authority than the pack carries.

## What the MVP should look like in theory
A realistic v0 is not “solve every Rust upgrade”.
It is:
- one schema family for source state, destination intent, plan/run/outcome, waivers, and bundle packaging;
- one edition-migration proof;
- one workspace `rust-version` / toolchain-ratchet proof;
- one dependency/API/MSRV-sensitive proof;
- one docs/support/downstream import proof;
- and one downstream consumer handoff proof.

Required artifacts:
- `migration-subject/v0`
- `migration-intent/v0`
- `migration-analysis-report/v0`
- `migration-plan/v0`
- `migration-run-report/v0`
- `migration-outcome-report/v0`
- optional `migration-waiver/v0`
- `migration-pack/v0`
- `migration-diff/v0`
- `migration-handoff/v0`

Required rules:
- keep **source state** distinct from **destination intent**;
- keep **destination intent** distinct from **mechanical edit output**;
- keep **mechanical edit output** distinct from **compatibility/support/docs/downstream imports**;
- keep **run/outcome truth** distinct from **consumer summaries**;
- keep **migration truth** distinct from **edit workflow**, **public API**, **support envelope**, and **distribution/update continuity**.

## What the MVP should look like in practice
### Pilot 1 — edition transition lane
Show one pack that starts from an explicit source edition, records multi-pass `cargo fix --edition` execution across declared slices, preserves manual follow-up, and ends with a bounded destination claim.

### Pilot 2 — workspace toolchain / `rust-version` lane
Show one pack that records mixed-policy workspace verification, selected package slices, toolchain imports, and explicit unsupported residue.

### Pilot 3 — dependency / API / MSRV lane
Show one pack that records dependency movement, imported semver/MSRV evidence, and public/private-dependency-sensitive consequences without flattening them into “updated successfully”.

### Pilot 4 — docs / support / downstream lane
Show one pack that imports docs/example/doctest/downstream testing evidence and preserves incompleteness honestly.

### Pilot 5 — archaeology / consumer handoff lane
Show one migration diff and handoff note that a release reviewer, maintainer six months later, or assistant can import without replaying the original branch.

## Why this should be promoted instead of “just improving cargo fix”
The archive already had strong notes on Migration Kit, Edit Workflow, Public API, Support Envelope, and Update Continuity.
Those are still right, but the next sharpening move here is **not** another lower-level fixer or another release checklist.

Why this promotion wins now:
- official signals are strongest on **staged edition migration**, **conservative but non-recommendatory fix output**, **workspace `rust-version` complexity**, **public/private dependency stabilization**, **cargo-semver-checks toward Cargo integration**, and **durable docs/API imports**;
- the archive already has enough substrate to justify a composition layer;
- promoting the contract reduces the risk that one `cargo fix` run, one green CI pass, one dependency bump PR, or one assistant patch silently defines the whole migration story.

So this revision promotes the **source state / destination intent / applied edits / compatibility imports / outcome / handoff boundary**, not one winning edit engine.

## Ranking impact
This does **not** reorder the archive's top band.
It adds one more explicit frontier beneath the current map:
- Build-State Evidence stays #1 overall.
- Adoption Navigation remains the strongest anti-tacit-knowledge frontier.
- Debuggability stays high.
- Rust inner-loop and Workspace Environment remain the clearest build/debug and environment bundle-shaping moves.
- Toolchain Productization remains the clearest toolchain-variant / sysroot move.
- Migration Truth Contract becomes the clearest next **change-program / upgrade-shaping** move.

That means it should sit above another round of ad hoc upgrade scripts, one-off PR templates, or post-hoc archaeology notes, but below the broad build/debug/resource band.

## What not to build
Do **not** build:
- a universal upgrade bot;
- a scalar “migration health” score;
- another dependency updater pretending to own semver, docs, and support;
- a release checklist that swallows edit provenance;
- or an assistant wrapper that treats one transcript as the whole migration.

The winning contribution is thinner and more durable:
**publish explicit source-state truth, explicit destination-intent truth, explicit suggested-vs-applied edit truth, explicit compatibility/support/docs/downstream import truth, explicit run/outcome truth, and hand that off honestly to multiple consumers without flattening unlike migrations into one story.**
