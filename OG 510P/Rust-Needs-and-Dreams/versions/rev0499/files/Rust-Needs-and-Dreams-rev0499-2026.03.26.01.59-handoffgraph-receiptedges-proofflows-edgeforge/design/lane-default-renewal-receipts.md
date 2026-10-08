# Design: Lane Default Renewal Receipts

## Goal
Turn the lane-default evidence bundle into **concrete, reviewable receipts** that humans, assistants, and maintainers can re-read without reconstructing the whole research trail.

The archive now has:
- default cards in `defaults/`;
- a corpus discipline in `design/reviewable-lane-defaults-corpus.md`;
- an evaluation rubric in `design/lane-default-evaluation-framework.md`;
- and an evidence model in `design/lane-default-evidence-bundle.md`.

What it still lacked was the first honest answer to:
> show me the actual receipt behind this default, not just the theory of receipts.

This note defines that next step.

Read with:
- `design/lane-default-evidence-bundle.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/lane-default-evaluation-framework.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
- `meta/LANE_RENEWAL_RECEIPTS_WORKING_SET.md`
- `evidence/README.md`

## Why this seam matters now
Fresh official signals make receipt-first renewal more plausible and more necessary:

- Rust’s March 20, 2026 challenges post says the ecosystem still suffers from **choice paralysis** and **tacit knowledge**, with uneven maturity across domains.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while LLM/editor-mediated workflows are rising, which increases the cost of ungrounded recommendation folklore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io’s January 2026 update added public review surfaces that are useful in receipts: Security tab, Trusted Publishing only mode, SLOC, `pubtime`, and source browsing links.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec’s current advisories include multiple recently removed **malicious lookalike crates** with names close to familiar packages (`oncecell`, `serd`, `envlogger`, and others), which is a concrete reminder that exact package identity belongs in renewal hygiene.
  https://rustsec.org/advisories/
- Cargo’s current work on build analysis and build-dir layout shows a broader direction toward replayable, machine-usable evidence instead of terminal folklore.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo’s changelog and unstable docs now expose useful time/replay hooks like `--publish-time`, while `cargo-semver-checks` continues moving toward Cargo integration.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

Taken together, these signals say the archive should stop at theory no longer.
It should publish real receipts.

## The missing problem
A default card plus a list of source URLs is better than nothing, but still leaves too much implicit:
- what was actually rechecked this round;
- what changed versus merely remained acceptable;
- which claims are lane-level versus package-level;
- whether exact package identities were verified or only spoken about loosely;
- and what future reviewers should replay before reusing the result.

Without concrete receipts, the evidence bundle remains one layer too abstract.

## What a receipt is
A **lane default renewal receipt** is the attachable review artifact for one default card at one review date.

It is not the whole evidence model.
It is the concrete slice that says:
- which default card was reviewed;
- what evidence classes were imported;
- what the reviewer concluded;
- what stayed unresolved;
- and whether the card was kept, narrowed, replaced, demoted, or newly admitted.

## Receipt anatomy
Each receipt should make these sections obvious:

### 1) Subject and review boundary
- default-card id
- review date
- scope
- reviewer / archive revision
- explicit non-goals

### 2) Renewal verdict
One of:
- keep
- keep with caveats
- narrow
- replace
- demote to project-specific only
- add as new card

### 3) Canon import
The maintainer-authored or official docs actually checked this round.

### 4) Registry / supply-chain import
The public registry-facing and advisory-facing facts that matter for renewal.
This is also where the archive should record **exact package names** rather than relaxed colloquial names.

### 5) API / compatibility import
Public API / semver / dependency-surface / support-truth facts relevant to whether the lane remains sane.

### 6) Maintenance / support-envelope import
Support posture, runtime/ABI/platform assumptions, and obvious maintenance concerns.

### 7) Freshness / replay notes
What was checked now, what could be replayed later, and what to revisit at the next renewal.

### 8) Lane judgment
The final lane-level answer, separated from package-level anxieties or wider ecosystem narrative.

## Exact-identity hygiene
This seam deserves its own rule because assistants are bad at it by default.

A receipt that names external crates should prefer:
- exact crate identifiers;
- exact docs / registry links;
- explicit warnings when lookalike names are a live ecosystem hazard;
- and a statement of whether the receipt is making a **lane judgment** or a **package-admission judgment**.

The archive should not let:
- “once_cell” and “oncecell”;
- “serde” and “serd”;
- “env_logger” and “envlogger”;
- or any other high-confusion pair
collapse into one fuzzy memory.

## First receipt corpus
The first receipt set should cover:
1. `defaults/conservative-internal-cli-2026Q1.md`
2. `defaults/conservative-http-service-2026Q1.md`
3. `defaults/script-repro-tiny-utility-2026Q1.md`

Why this trio:
- CLI is the easiest renewal lane;
- HTTP/service is the consequential lane that most needs visible boundaries;
- script/repro is the bounded unstable-adjacent lane that tests whether the archive can publish honest caveats.

## MVP artifact family
A minimal v0 can stay simple and human-readable:
- `evidence/README.md`
- one markdown receipt per reviewed card
- optional later diff/index files
- cross-links from default cards to latest receipts
- compact working-set / protocol reminders

Do not require a giant database before publishing the first useful receipts.

## Later machine-usable expansion
Once the markdown receipts stabilize, the archive can add:
- `lane-renewal-receipt/v0`
- `lane-renewal-diff/v0`
- `lane-renewal-index/v0`

But the repo should prove the human review loop first.

## Success criteria
This seam succeeds when:
- a later reviewer can understand why a card remained the default;
- exact package names and evidence classes stay distinct;
- the archive can say “keep” without pretending that means “universally best”;
- and the receipt is useful even if the reader ignores the surrounding design notes.

## Non-goals
- replacing package-admission review;
- assigning universal crate scores;
- pretending one receipt settles all future renewals;
- or widening the defaults corpus faster than the receipts can support.
