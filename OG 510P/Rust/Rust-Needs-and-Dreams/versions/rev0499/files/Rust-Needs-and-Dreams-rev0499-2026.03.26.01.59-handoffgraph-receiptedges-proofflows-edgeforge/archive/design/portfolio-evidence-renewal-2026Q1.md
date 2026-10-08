## Addendum (rev0428)
For questions about **how the archive should keep its own strongest claims fresh, narrow them when upstream reality moves, and retire them when the evidence decays**, read this note right after `design/portfolio-pilot-evaluation-2026Q1.md`, `design/portfolio-selection-rubric-2026Q1.md`, and `design/portfolio-execution-sequencing-2026Q1.md`.

Interpretation rule:
- this note does **not** promote a new seam;
- it does **not** change the broad ladder, the active frontier, or the default build sequence;
- it exists to answer the missing maintenance question: **how should the repo detect evidence drift and refresh or narrow the canon without pretending old citations are timeless?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- and require every serious canon refresh to end in an explicit **confirmed / narrowed / degraded / superseded / retired** renewal outcome rather than silent evergreen prose.

# Design: Portfolio evidence renewal and drift discipline (2026 Q1)

## Goal
The archive can now:
- rank strong seams,
- describe what they should ship,
- define a thin shared grammar,
- stage the portfolio,
- triage new candidates,
- and score serious pilots.

What it still lacked was one canonical answer to a slower but equally important question:

> once the repo has a strong claim, how should it keep that claim fresh as Cargo, docs.rs, crates.io, goals, and ecosystem tooling continue to move?

This note is the archive's answer to **evidence renewal**, not frontier promotion.

Read with:
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `meta/EVIDENCE_RENEWAL_PROTOCOL.md`
- `meta/CANONICAL_RENEWAL_QUEUE.md`

## Why this note is needed now
The repo is now rich enough that **stale confidence** is a larger risk than missing one more clever idea.
Official Rust signals make that especially true:

- Rust's March 2026 challenges writeup says the ecosystem's pain pattern is stable enough to talk about recurring classes like compile/resource cost and tacit knowledge, but that still does **not** make every supporting fact evergreen. The broad ladder may move slowly; the evidence beneath it often does not.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey is valuable because it names stable pain and preference patterns, but by nature it is an annual snapshot. That means the repo needs an explicit way to keep survey-backed claims as **anchor evidence** without silently treating them as live operational truth.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The project-goals machinery and regular goals updates show that important upstream priorities, accepted goals, and milestone language move on a visible cadence. The current process discussion even considers cadence changes, which means any archive claim that leans on "current goals" needs an explicit renewal posture.
  https://rust-lang.github.io/rust-project-goals/
  https://blog.rust-lang.org/2025/11/19/project-goals-update-october-2025/
  https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/
- docs.rs is a powerful machine-usable source, but its own service behavior changes; the October 2025 default-target change is exactly the sort of thing that can quietly age a recommendation or semantic-context assumption. The rustdoc JSON page likewise warns that hosted JSON may have been built with an older rustdoc and that consumers should check `format_version`.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
  https://docs.rs/about/rustdoc-json
- crates.io and Cargo security/trust surfaces also move on operational timelines. The January 2026 crates.io update expanded trusted-publishing controls, while the March 21, 2026 Cargo extraction advisory changed what a careful package-intake argument must say about versions, alternate registries, and residual risk.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- Infrastructure and service-layer changes continue in the background. The infrastructure team's Q1 2026 plan notes that the crates.io index and docs.rs are now served via Fastly, which is a reminder that hosted-service assumptions and operational facts can move without changing the broad strategic ladder.
  https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/

Taken together, those signals say the archive needed a note for **freshness, drift, and renewal discipline**.

## Headline answer
A strong archive should not react to change in only two modes:
- "rewrite the ladder because a new post dropped", or
- "keep quoting the old note forever because the broad idea still sounds true".

The repo needs a third mode:

> keep the broad seam judgment when it still holds, but explicitly renew, narrow, degrade, supersede, or retire the specific supporting claims whose evidence changed.

In archive terms, every important canon note should now have a visible answer to five questions:
1. **what kind of claim is this?**
2. **what authority lane is it leaning on?**
3. **how quickly can that lane drift?**
4. **what event should force renewal even before the calendar says so?**
5. **what should happen if the claim no longer holds cleanly?**

## The five renewal truths

### 1) Claim class
Every serious canon claim should be understood as one of these:
- **structural claim** — broad ranking or seam logic that should move slowly;
- **substrate claim** — a claim that a specific machine-usable input or upstream capability exists or is ripening;
- **service-behavior claim** — a claim about docs.rs, crates.io, CI, hosted defaults, or tool output behavior;
- **security/incident claim** — a claim shaped by active advisories, incidents, or policy shifts;
- **ecosystem-tooling claim** — a claim about an external tool, crate family, or practice surface.

Why this matters:
structural claims may survive for months with narrowing language, while service-behavior and incident claims may need immediate review.

### 2) Authority lane
Every serious canon claim should say which lane it trusts most:
- official language/tool docs;
- project goals / official status updates;
- hosted service docs or service announcements;
- maintainer-authored tool docs;
- survey / research snapshot;
- or mixed evidence.

Why this matters:
not all stale evidence fails the same way.
A six-month-old survey can still anchor strategic pain.
A six-month-old service-behavior statement may already be misleading.

### 3) Drift horizon
Every note should have a practical drift posture:
- **hot** — renew on visible upstream change or within weeks;
- **warm** — renew roughly each quarter or when adjacent inputs move;
- **cool** — renew semiannually or on contradiction;
- **cold** — renew only when the broader ladder is reconsidered or the claim is challenged.

Default mapping:
- service behavior, security, and active goals = **hot**;
- execution blueprints tied to active upstream inputs = **warm**;
- portfolio grammar, sequencing, and selection rules = **cool**;
- broad ladder and frontier synthesis = **cold**, unless a stronger contradiction appears.

### 4) Renewal triggers
Calendar time is not enough.
The repo should renew a note early when any of these happen:
- an official service default changes;
- an accepted goal lands, stalls, or is dropped;
- a security advisory changes the threat model of an argument;
- a quoted machine-usable format changes version or scope;
- a steward/maintainer source contradicts a prior assumption;
- or the archive starts leaning on an old claim for a stronger conclusion than it originally supported.

### 5) Renewal outcome
Renewal should end with an explicit verdict:
- **confirmed** — claim still holds with minor freshness touchups;
- **narrowed** — broad seam still holds, but some supporting scope shrank;
- **degraded** — the claim is still somewhat useful but should no longer carry the same argumentative weight;
- **superseded** — a newer note or stronger source should replace it;
- **retired** — the claim should no longer guide the canon.

The archive should prefer **narrowed** or **degraded** over pretending a note is either perfectly fresh or fully dead.

## Renewal classes for this repo

### A) Hot surfaces
Examples:
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`

Why hot:
these notes lean on live service behavior, current goals, security posture, and current project narratives.
A default-target change, a security advisory, or a goals shift can narrow their support quickly.

### B) Warm surfaces
Examples:
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/native-edge-execution-blueprint-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`

Why warm:
the broad seam logic is likely to survive, but the substrate readiness claims beneath it can age within a quarter.

### C) Cool surfaces
Examples:
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`

Why cool:
these are mostly repo-level theory-of-change notes.
They should change when practice disproves them, not because one upstream service changed a default.

### D) Cold surfaces
Examples:
- broad ladder / broad ranking notes;
- older foundational stack notes whose purpose is taxonomy rather than live service guidance.

Why cold:
these should move deliberately and only when the archive has real contradictory evidence.

## What a renewal should emit
A serious renewal should leave behind a compact packet, not only quiet edits:
- note renewed;
- prior revision and current revision;
- claim class and drift horizon;
- sources re-checked;
- triggers observed;
- verdict: confirmed / narrowed / degraded / superseded / retired;
- exact sentences or sections materially changed;
- what broad conclusion remains unchanged;
- and what follow-up note now carries the fresher argument if scope moved.

The canonical template lives in `meta/EVIDENCE_RENEWAL_PROTOCOL.md`.

## How renewal should interact with other portfolio notes

### With Selection Rubric
A fresh candidate can still fail selection even if the old evidence drifted.
Renewal is not a loophole for promotion.
Use renewal to clarify what the current canon still means; use selection to decide whether something new deserves a place.

### With Pilot Evaluation
A pilot scorecard can go stale too.
If the ecosystem substrate moved, the pilot may remain historically valuable but lose force as a present-tense proof.
Renew the scorecard verdict or degrade its current weight rather than silently carrying it forward.

### With Sequencing
A stage order can remain right even if some stage-local inputs drift.
Renew the stage-local justifications first.
Only re-sequence the portfolio when the changed evidence is strong enough to alter the default build order.

### With Shared Grammar
Freshness fields, lineage receipts, and handoff lossiness should stay inside the shared grammar.
But the shared grammar should not pretend to solve subject-specific renewal.
Each seam still owns its own drift triggers and likely failure modes.

## Common failure modes this note is meant to prevent
- treating annual survey signals as live operational defaults;
- treating old goal pages as if they still describe the current accepted motion;
- leaving service-behavior assumptions untouched after docs.rs or crates.io changes;
- quoting a security advisory once and then letting it silently stand in for a permanent model;
- rewriting the broad ladder every time a fresh upstream post appears;
- or letting LLM-friendly prose summaries outlive the stronger cited claim they were derived from.

## Default repo policy after this revision
From here on, the archive should prefer:
- **renew** before **re-rank** when the broad seam still holds;
- **narrow** before **retire** when only some supporting scope drifted;
- **degrade** before **pretend** when the evidence is aging but not fully invalid;
- and a visible renewal packet over silent freshness edits.

In practical terms:
- the strongest one-project answer remains **Build-State Evidence**;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- **Native Edge Contract** remains the active specialist frontier;
- but the repo now has a canonical way to say **which of its present-tense claims still hold strongly, which are narrowing, and which need refresh work first**.
