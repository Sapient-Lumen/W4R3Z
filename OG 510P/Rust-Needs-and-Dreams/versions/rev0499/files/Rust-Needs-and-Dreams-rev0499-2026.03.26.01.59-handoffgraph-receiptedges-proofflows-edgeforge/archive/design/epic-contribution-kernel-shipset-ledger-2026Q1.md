# Design: Epic contribution kernel shipset ledger (2026 Q1)

## Goal
The archive already knows:
- which Rust ecosystem seams rank highest;
- where those seams should live;
- what first wedges make them believable;
- what repeated decision journeys they should compose inside; and
- what older kernel briefs say about their first honest repo shapes.

What it still lacked was one compact, current, machine-checkable answer to a narrower practical question:

> once a worthy seam has already earned a bounded first build, **what exact shipset should a small team build first, what modules belong in that repo, and what proof assets must that shipset emit before we talk like it is a program?**

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It turns the older kernel-brief corpus into a **live kernel shipset ledger** that future revisions can validate instead of reconstructing from memory.

Read with:
- `design/epic-contribution-v0-kernel-briefs-2026Q1.md`
- `meta/V0_KERNEL_BRIEF_PROTOCOL.md`
- `design/epic-contribution-launch-wedges-2026Q1.md`
- `design/epic-contribution-decision-journeys-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`
- `ledgers/top-band-kernel-shipsets-v0/shipsets.json`
- `meta/KERNEL_SHIPSET_LEDGER_PROTOCOL.md`

## Why this pass is merited now
The strongest current Rust signals keep rewarding **bounded companion-first shipsets** over framework theater.

Cargo's build-analysis goal is still explicitly a prototype: Cargo would record build metadata across invocations, add unstable `cargo report` commands for rebuild reasons and timing, keep collection opt-in, and provide no user-facing stability guarantees during prototyping. That says the worthy contribution is still a bounded companion that can import unstable truth carefully, not a finished Cargo-core platform.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

Cargo's external-tools reference still describes stable integration around `cargo metadata`, `--message-format`, and custom subcommands, and it explicitly says `cargo metadata` is stable and versioned when called with an explicit `--format-version`. That keeps the first-build shape anchored in CLI-facing adapter seams rather than Cargo-as-a-library fantasies.  
https://doc.rust-lang.org/cargo/reference/external-tools.html

The build-dir-layout goal and testing call still describe real operator pain around whole-dir locking, Rust Analyzer contention, cache reuse, and tools depending on unspecified build-dir structure. That means Build-State Evidence still wants a first repo shaped around capture/diff/doctor and migration receipts, not around scraping internals or promising one magic cache.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html  
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

The January 2026 crates.io update and March 2026 Project Director update make package-boundary work more concrete: Trusted Publishing now supports GitLab.com in addition to GitHub, crate owners can enforce Trusted Publishing only mode, risky GitHub Actions triggers are blocked, vulnerability surfacing is now live, and `cargo-capslock` exists for static and runtime capability analysis. That strengthens the case for a local-first intake review kit with route profiles and waiver/quarantine receipts rather than a registry-global trust oracle.  
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/  
https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/

The `cargo-semver-checks` goal is still explicitly about the `cargo publish` workflow and depends on more precise rustdoc information plus witness-program generation. docs.rs also says its hosted rustdoc JSON is programmatic but caveat-heavy: consumers must check `format_version`, older releases may still lack downloads until rebuilds land, and redirect targets may temporarily not exist. That combination reinforces the archive's current instinct that compatibility and release-boundary logic should be imported into shipsets, not treated as magically stable substrate.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html  
https://docs.rs/about/rustdoc-json

The libtest JSON goal says libtest ships with rustup and carries standard-library-class compatibility guarantees, and it explicitly motivates shifting more reporting responsibility into Cargo so runners and custom harnesses can consume better machine-readable output. That strengthens the archive's insistence that first shipsets should emit bounded machine-readable artifacts instead of prose-only diagnostics.  
https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html

The 2025 State of Rust survey and the March 2026 challenges post still concentrate pain around compile/resource usage, debugging, crate-choice burden, constrained/embedded realities, and safety-critical maturity gaps rather than one absent flagship framework. That keeps the kernel shipset answer narrow: a handful of evidence/review/readiness families, not a new portal empire.  
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/  
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2026 goals overview also matters here. Rust now has annual goals with explicit champions and resource expectations. That further rewards shipset notes that are small enough for named owners and real review lanes, instead of vague mega-programs with no first maintainer story.  
https://rust-lang.github.io/rust-project-goals/2026/

## Headline answer
A worthy repo should now keep a **kernel shipset ledger**.

A kernel shipset card is a compact answer to:
1. which seam has actually earned a bounded first build;
2. what the kernel codename is;
3. what top-level modules or corpora belong in the first repo;
4. what commands, packs, or cards form the initial user surface;
5. what imported truths the shipset is allowed to depend on;
6. what proof artifacts and proving grounds make the shipset real;
7. what upkeep burden appears immediately; and
8. what larger product shape must still be refused.

The point is not to replace the prose kernel briefs.
The point is to stop future revisions from answering “what should a small team build first?” by re-inventing repo trees from packets, journeys, and vibes.

## What this layer governs
Use the kernel-shipset ledger when the repo needs to answer:
- what modules belong in the first repo for a top seam;
- what artifact family a first implementation must emit;
- what import surfaces are allowed in v0;
- what maintenance burden appears on day one; or
- whether a new proposal is really a first shipset or merely a renamed program dream.

Do **not** use this layer to:
- rerank the broad ladder;
- claim that every seam deserves kernelization right now;
- replace seam-local contracts, witnesses, fixtures, or schemas;
- or imply that one good shipset card means the broad program is already proven.

## Current ledger interpretation
The current first-class shipsets are still only four:
1. **Build-State Evidence** → `build-state-pack/v0`
2. **Package Intake + Release Boundary Review** → `intake-review-kit/v0`
3. **Feedback / Debug Acceptance Commons** → `debug-acceptance-matrix/v0`
4. **Safety-Critical + Institutional Readiness Commons** → `readiness-cards/v0`

That exclusion is important.
**Adoption Navigation + Ecosystem Atlas** is still strategically important, but it remains intentionally un-kernelized because the main blocker is renewal burden, not lack of imagination.

## Cross-card rules

### 1) Kernel cards must stay smaller than program charters
A kernel shipset names the first honest repo and artifact family.
It is not the whole roadmap, institution, or consortium.

### 2) Imported truth stays imported truth
If a shipset depends on unstable `cargo report` output, docs.rs rustdoc JSON, debugger exports, or crates.io service truth, the card must preserve the caveats instead of laundering them into a fake stable substrate.

### 3) Each card must carry its immediate upkeep burden
A card that names modules and commands but not adapter churn, matrix renewal, waiver expiry, or freshness debt is incomplete.

### 4) Kernel cards must compose with wedges and journeys
A strong first shipset should make it easier to identify one first adopter moment and one repeated operator journey.
If it cannot, the card is probably too abstract or too broad.

### 5) Refusal clauses are part of the design
Every card must say what bigger framework temptation is still out of bounds.

## What changed in this revision
The repo now keeps a machine-readable ledger and checker for first shipsets, and the older kernel-brief corpus becomes part of the live canon again.
This is a repo-construction improvement, not a strategy rewrite.

## Practical payoff
Future continue-research passes should now be able to say, quickly and concretely:
- which first repo shape is currently endorsed,
- which modules belong in it,
- what proof assets it must emit,
- what upstream/service truth it imports,
- and what broader build is still refused.

That makes “worthy contribution” answers more buildable and less atmospheric.
