# Design: Epic contribution decision journeys (2026 Q1)

## Goal
The archive already knows:
- which Rust ecosystem gaps rank highest;
- what the strongest contributions should look like in theory and practice;
- where they should live;
- how they should first enter the world; and
- what broad claims, watchcards, and control loops keep the canon honest.

What it still lacked was one sharper answer to a different practical question:

> when a real Rust team hits a consequential moment — a rebuild regression, a dependency-admission review, a debugger issue handoff, a release-boundary check, a safety-readiness evaluation, or a conservative default-selection decision — **how should the strongest seams compose into one decision journey instead of acting like isolated good ideas?**

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It adds a shared cross-seam layer for repeated operator moments.

Read with:
- `design/epic-contribution-launch-wedges-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `meta/DECISION_JOURNEY_PROTOCOL.md`
- `ledgers/portfolio-decision-journeys-v0/journeys.json`

## Why this pass is merited now
Current Rust signals keep describing recurring **decision moments**, not just abstract ecosystem desires.

Cargo's build-analysis goal is explicitly about recording build metadata across invocations and introducing unstable `cargo report` subcommands to explain rebuilds and surface timing history. That is not merely a new substrate; it is the start of a **build-regression triage journey**.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

The March 2026 build-dir-layout testing call says many projects still rely on unspecified build-dir details due to missing Cargo features, and asks people to run tests and release processes against `-Zbuild-dir-new-layout`. That is a strong sign that build-state work has to connect build facts, migration caveats, doctor posture, and issue handoff in one journey.  
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

The January 2026 crates.io update says crate owners can now enforce Trusted Publishing only mode and that dangerous GitHub Actions triggers are blocked from Trusted Publishing. That turns package-boundary work into a real **publish and admission review journey**, not just a static registry note.  
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

The `cargo-semver-checks` goal explicitly aims at the `cargo publish` workflow, including a default requirement for SemVer compliance with an override flag, and it explains why witness-program generation and cross-crate visibility matter. That is the clearest official sign that Rust increasingly needs a **release-boundary decision journey** with explicit waivers and proof.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

The libtest JSON goal says libtest ships with rustup and has compatibility guarantees like the standard library, while the docs.rs rustdoc JSON page says hosted rustdoc JSON is programmatic but format-version and rebuild caveats matter. Those are exactly the kinds of imported surfaces that only make sense when carried through actual review and issue-hand-off journeys.  
https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html  
https://docs.rs/about/rustdoc-json

The 2025 State of Rust survey and the March 2026 challenges post both still concentrate the practical pain around build/resource usage, debugging friction, crate choice/trust, and domain-specific maturity gaps rather than around one missing mega-framework. That is a strong signal that the archive should optimize for repeated operator moments instead of another platform fantasy.  
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/  
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2026 debugging survey is framed around debugger-version, OS, async, visualizer, and expression-evaluation coverage. That makes the missing thing less “a perfect debugger brand” and more a **debug issue handoff journey** with tuple identity and explicit degraded-state posture.  
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The safety-critical writeup says Rust is already in production in some safety-critical domains, but also emphasizes that ecosystem support thins out at higher criticality and that FFI/interop guidance remains important. That is a clear argument for a **readiness-evaluation journey** rather than certification theater.  
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## Headline answer
A worthy repo should now preserve not only seams, wedges, and claims, but also a small ledger of **decision journeys**.

A decision journey is a compact answer to:
1. what repeated decision moment is happening;
2. which seam starts the journey;
3. which supporting seams join it;
4. what artifacts must travel from step to step;
5. what proof ends the journey honestly; and
6. what bigger product temptation must still be refused.

The archive should prefer **journey-first composition** over inventing one new umbrella platform for all seams.

## What this layer governs
Use the decision-journey layer when the repo needs to answer:
- how several top seams should compose during one real workflow;
- which artifact should be produced first and which artifact should be imported later;
- where a watchcard, packet, wedge, or readiness card actually gets used;
- what a first useful operator playbook would look like; and
- whether a proposed contribution is really helping a repeated decision moment or only adding another tool noun.

Do **not** use this layer to:
- rerank the broad ladder;
- claim that every seam must participate in every journey;
- replace seam-local contracts or specimens; or
- imply that one successful journey justifies a hosted control plane.

## Cross-journey rules

### 1) A journey must end in a changed decision, not only a produced artifact
A pack, card, or report is not enough by itself. The journey should end with a triage, admit/quarantine, route, release, or readiness decision.

### 2) Journeys should compose seams asymmetrically
One seam usually starts the journey. Others join only when needed. Resist symmetric “everything everywhere” frameworks.

### 3) Imported truth stays imported truth
If a journey uses Cargo facts, crates.io service truth, docs.rs rustdoc JSON, or debugger tuple descriptors, the journey must preserve their caveats instead of laundering them into fake certainty.

### 4) Every journey needs a refusal clause
If a journey note cannot say what broader product temptation should still be refused, it is not yet honest.

### 5) Journeys should be short enough to use in anger
A good first journey fits one painful operator day or one bounded review cycle, not a quarter-long transformation program.

## The current core decision journeys

### 1) Build regression triage
**Starts with:** Build-State Evidence  
**Usually pulls in:** Compatibility Claims, Tooling Contract / Semantic Context  
**Ends with:** one reviewable explanation of why a rebuild or slowdown happened and what remains unknown

**First artifacts:** build-state pack, diff, doctor note, caveat receipt

**Why it matters:** current Cargo work is finally creating better recorded build facts, but teams still need a portable review path that survives CI, editor-triggered checks, and build-dir migration.

### 2) Dependency admission and publish review
**Starts with:** Package Intake + Release Boundary Review  
**Usually pulls in:** Compatibility Claims, Build-State Evidence  
**Ends with:** admit, quarantine, waive, or recheck decision

**First artifacts:** intake receipt, route profile, publishing posture, waiver note

**Why it matters:** service truth is improving, but the missing product is still the review journey, not another crate score.

### 3) Debug issue handoff
**Starts with:** Feedback / Debug Acceptance Commons  
**Usually pulls in:** Build-State Evidence, Tooling Contract / Semantic Context  
**Ends with:** issue-ready export with tuple identity and degraded-state posture

**First artifacts:** tuple card, session pack, unsupported-state receipt

**Why it matters:** official signals still define the gap in tuple coverage terms, so the first believable contribution is a better handoff journey.

### 4) Release-boundary review
**Starts with:** Compatibility Claims  
**Usually pulls in:** Package Intake + Release Boundary Review, docs.rs rustdoc JSON, libtest JSON, Build-State Evidence  
**Ends with:** release claim accepted, waived, or blocked with explicit proof posture

**First artifacts:** claim pack, diff, witness-program note, waiver note

**Why it matters:** official work around `cargo-semver-checks` is increasingly about making this a real pre-publish decision rather than an optional afterthought.

### 5) Safety readiness evaluation
**Starts with:** Safety-Critical + Institutional Readiness Commons  
**Usually pulls in:** Package Intake + Release Boundary Review, Compatibility Claims, Tooling Contract / Semantic Context  
**Ends with:** bounded yes / not yet / only with mitigations posture

**First artifacts:** readiness card, dependency lifecycle note, interop caveat, renewal owner receipt

**Why it matters:** the missing contribution is still shared readiness truth and stewardship, not a fake certification badge.

### 6) Conservative default selection
**Starts with:** Adoption Navigation + Ecosystem Atlas  
**Usually pulls in:** Package Intake + Release Boundary Review, Compatibility Claims  
**Ends with:** one conservative starting default with explicit stale, unknown, and reconsider triggers

**First artifacts:** default card, renewal receipt, boundary caveat links

**Why it matters:** the survey and challenges material keep showing that recommendation burden is real, but the archive still needs a narrow, evidence-bearing journey rather than a giant portal.

## What a worthy contribution should look like in theory and practice now
The practical standard is now higher:
- a strong seam should have a kernel;
- a believable first wedge;
- a claim/falsifier posture;
- and at least one **decision journey** where a real team would use it.

This means a proposed contribution should now be able to answer all of the following:
- what repeated decision does it change;
- what other seam artifacts does it need to import;
- what artifact should the user carry out of the journey;
- what proof shows the journey ended honestly; and
- what larger product story is still out of scope.

## Preferred deepen order from this layer
This note does not change the broad ladder, but it sharpens the practical buildout order:
1. deepen **build regression triage** first;
2. deepen **dependency admission / publish review** second;
3. deepen **debug issue handoff** third;
4. keep **release-boundary review** close behind because the official `cargo-semver-checks` direction is maturing;
5. keep **safety readiness evaluation** as the clearest stewardship-heavy journey; and
6. keep **conservative default selection** deliberately narrow until renewal burden improves.

## What should still be refused
Do not let this layer become:
- a universal workflow engine;
- a hosted project-management veneer over immature facts;
- a reason to centralize everything into Cargo core;
- or a substitute for seam-local contracts, witnesses, and proving grounds.

The right outcome is smaller and more useful: a repo that can now say **which real operator moments its best ideas are trying to change, and how those ideas should compose when that moment arrives**.
