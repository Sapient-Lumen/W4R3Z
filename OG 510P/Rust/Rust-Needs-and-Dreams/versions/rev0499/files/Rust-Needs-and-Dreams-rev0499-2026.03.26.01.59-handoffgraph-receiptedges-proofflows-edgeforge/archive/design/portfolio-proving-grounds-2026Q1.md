## Addendum (rev0433)
For questions about **how the archive should compare serious pilots on shared ground instead of letting each proposal choose its own flattering demo lane**, read this note right after `design/portfolio-pilot-evaluation-2026Q1.md`, `design/portfolio-execution-sequencing-2026Q1.md`, and `meta/PROVING_GROUNDS_PROTOCOL.md`.

Interpretation rule:
- this note does **not** promote a new seam;
- it does **not** change the broad ladder or the default portfolio order;
- it exists to answer the missing execution question: **what thin proving-grounds matrix should serious seams use so their pilots become comparable, auditable, and easier to fund or kill?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- and require every serious pilot to name a scenario, a decision class, and a skip reason instead of claiming generality by tone.

# Design: Portfolio proving grounds and scenario matrix (2026 Q1)

## Goal
The archive can now:
- rank strong seams,
- specify what they should ship,
- stage the portfolio,
- triage additions,
- score pilots,
- route consumer slices,
- validate a thin shared envelope,
- maintain specimens,
- and run a thin archive-doctor pass.

What it still lacked was one canonical answer to a narrower but increasingly practical question:

> if two worthy pilots both look good in isolation, what common proving grounds should the archive use so they can be compared on shared terrain instead of on each team’s favorite demo setup?

This note is the archive's answer to **portfolio proving grounds**, not frontier promotion.

Read with:
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-consumer-routing-2026Q1.md`
- `meta/PROVING_GROUNDS_PROTOCOL.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Why this note is needed now
The repo is now good enough at saying what looks worthy that a new failure mode matters more: pilots can win by choosing incomparable, unusually kind scenarios.

Current Rust signals make a proving-grounds layer more necessary, not less:

- Rust's March 2026 challenges writeup says the pain is not one universal beginner problem. Compilation performance is universal, but the rest of the friction is domain-shaped: async for network developers, certification gaps for safety-critical teams, maturity gaps for embedded teams, and ecosystem navigation pain across all cohorts.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says resource usage remains a major productivity limiter, debugging remains a top non-trivial problem, and online docs remain canonical while editor / LLM-mediated learning rises. That means pilots need shared lanes that stress real productivity taxes and emit reusable evidence, not just attractive UX.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The February 2026 program-management update says annual goals now sit under longer-lived roadmaps and application areas meant to focus industry funding. That makes scenario choice more strategic: a pilot should be able to say which roadmap or application area it exercised instead of only saying “it worked on my repo”.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The 2026 flagships explicitly include supply-chain control, public/private dependency work, breaking-change detection, and SBOM support. That means at least one shared proving ground should exercise release / package / policy reality rather than only inner-loop ergonomics.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo's build-analysis goal and the Cargo 1.94 development-cycle update both emphasize recorded build metadata, `cargo report rebuild`, `cargo report sessions`, and structured logging. That makes it more realistic to compare pilots on named scenarios using machine-usable receipts rather than anecdotes.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The March 2026 Build Dir Layout v2 testing call says many tools still rely on unspecified Cargo details due to missing features. docs.rs changed default targets in October 2025. Those are concrete reminders that environment assumptions drift and that cross-target or tool-adjacent pilots should say exactly which scenario they exercised.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The Rust debugging survey launched in February 2026 explicitly asks where debugging support breaks down across debuggers and operating systems. That is another sign that scenario coverage matters: “works for me on Linux with one debugger” is not the same thing as “represents Rust's debugging tax”.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The Rust Foundation's 2026–2028 strategy pairs stable infrastructure, sustainable maintenance, responsible growth in adoption, and meaningful engagement from organizations. That argues for pilots that can be funded and maintained against named scenarios rather than vague promises of ecosystem reach.
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say the archive needed a **shared scenario matrix**.

## Headline answer
A serious portfolio should maintain a **thin proving-grounds matrix**.
It is not a universal benchmark empire and not a mandatory end-to-end distro of repos.
It exists for a smaller question:

> before a pilot claims broad relevance, which named Rust realities did it actually exercise, what decisions did it improve there, and what realities did it explicitly skip?

The proving-grounds matrix should therefore:
1. define a small set of representative scenario cards;
2. require each serious pilot to bind itself to one or more cards;
3. require explicit skip reasons when a scenario is out of scope;
4. keep scenario identity separate from seam identity;
5. keep benchmark/evidence artifacts separate from policy or recommendation conclusions.

## What this note is for
Use the proving-grounds layer when the archive needs to answer:
- which scenarios are representative enough to compare pilots;
- what a pilot is allowed to generalize from;
- which scenario classes deserve first-party example artifacts;
- and what “not yet proven” should mean when a proposal only exercised one lane.

Do **not** use it to claim:
- that every seam must support every scenario;
- that one scenario matrix replaces seam-local fixtures or benchmarks;
- that one passed scenario means a contribution is default-ready;
- or that scenario coverage is the same thing as evidence freshness.

## The proving-grounds model

### 1) Scenario card
A scenario card is a named Rust reality.
It should include:
- scenario ID and short title;
- the recurring tax or decision class it exists to stress;
- topology and environment facts;
- target user/operator class;
- relevant seam families;
- minimum artifacts a pilot should emit there;
- and explicit non-claims.

### 2) Scenario matrix
The matrix is the maintained list of scenario cards.
It should stay small enough that humans can remember it and tools can validate it.
The first matrix should prefer **representative coverage** over exhaustiveness.

### 3) Scenario binding
A pilot scorecard should name which scenario cards it exercised.
If it did not exercise a card that readers may reasonably expect, it should say why.

### 4) Skip receipts
A skipped scenario is acceptable when the pilot states:
- why the scenario is out of scope,
- what would have to change before the pilot should be tried there,
- and which conclusions are forbidden until that happens.

## The first thin matrix
The archive's first proving-grounds matrix should cover five realities:

### A) Inner-loop workspace pressure
Purpose:
- stress compile / rebuild / edit-loop taxes,
- cargo / editor coordination,
- and machine-usable build receipts.

Good for:
- **Build-State Evidence**,
- **Semantic Context** consumers tied to active editing,
- build-dir / lock / timings / sessions work,
- debugging and compile-guidance adjacent ideas.

Non-goal:
- this card does not prove release, semver, or package-ingress claims.

### B) Public-library release boundary
Purpose:
- stress public API, semver, migration, docs, and release-boundary truth.

Good for:
- **Migration/Public API**,
- **Semantic Context**,
- semver witness / docs / rustdoc JSON consumers,
- recommendation surfaces that need publishable-library posture.

Non-goal:
- this card does not prove native-edge or restricted-environment claims.

### C) Locked-down intake and policy lane
Purpose:
- stress package ingress, extraction, registry / source-path authority, trusted publishing posture, and review-before-use controls.

Good for:
- **Package Intake Gateway**,
- release / admission / policy review adjacencies,
- evidence packs for security and compliance operators.

Non-goal:
- this card does not prove inner-loop throughput or foreign-build ergonomics.

### D) Native-edge polyglot lane
Purpose:
- stress Rust↔native boundary truth, build-script and provider/link handoff, host-vs-target distinctions, and foreign-build coordination.

Good for:
- **Native Edge Contract**,
- cross-language interop roadmaps,
- toolchain / sysroot / `-sys` / generated bindings adjacencies.

Non-goal:
- this card does not prove release-boundary or recommendation quality by itself.

### E) Cross-target docs / consumer drift lane
Purpose:
- stress docs.rs target defaults, rustdoc JSON format awareness, consumer routing, and evidence that changes when target or host assumptions shift.

Good for:
- **Semantic Context**,
- **Adoption Navigation**,
- any seam that wants to summarize canonical docs or support posture safely.

Non-goal:
- this card does not prove build-state or package-intake performance directly.

## Required scenario-card fields
The repo-level minimum lives in `meta/PROVING_GROUNDS_PROTOCOL.md`, but the short version is:
- `scenario_id`
- `title`
- `scenario_class`
- `primary_tax`
- `topology`
- `environment`
- `decision_classes`
- `relevant_seams`
- `minimum_artifacts`
- `must_prove`
- `must_not_claim`
- `skip_conditions`

These fields keep the matrix honest without swallowing seam-local detail.

## What makes this a worthy repo increment
This note does not invent a new strategic winner.
It makes the existing winners more comparable.

That is valuable because the archive's strongest answers increasingly depend on **reviewable artifacts and bounded claims**. A proving-grounds layer gives those answers shared terrain:
- **Build-State Evidence** can be compared on inner-loop and build-analysis lanes;
- **Migration/Public API** can be compared on release-boundary lanes;
- **Package Intake Gateway** can be compared on locked-down ingress lanes;
- **Native Edge** can be compared on polyglot boundary lanes;
- **Semantic Context** and **Adoption Navigation** can be compared on cross-target docs and consumer-drift lanes.

So the proving-grounds layer does not compete with the portfolio. It makes the portfolio falsifiable.

## Default anti-goals
Do not let this become:
- a universal benchmark leaderboard;
- a giant fleet of maintained sample repos before the matrix has proven its value;
- a hidden reranking mechanism that changes the ladder without saying so;
- or a pretext to force every seam through every scenario.

The archive wants a **small representative scenario matrix**, not an empire of synthetic tests.

## Practical default
Until stronger evidence arrives, the default proving-grounds answer is:
- keep the broad ladder intact;
- keep proving grounds as **deepening + hygiene**, not promotion;
- require new serious pilots to name one or more scenario cards explicitly;
- require them to state which cards were skipped and why;
- and prefer a thinner honest matrix over a larger fake-complete corpus.
