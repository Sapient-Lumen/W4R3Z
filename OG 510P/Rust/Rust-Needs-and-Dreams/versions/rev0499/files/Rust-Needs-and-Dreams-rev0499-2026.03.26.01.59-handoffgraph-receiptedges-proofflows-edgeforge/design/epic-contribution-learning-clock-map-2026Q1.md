# Design: Epic contribution learning-clock map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- scorecards for comparing already-worthy contributions;
- a delivery matrix for what each candidate should ship;
- an incubation map for what vehicle each candidate should start in;
- a proof-burden map for what each candidate must prove;
- a bet-sizing map for what capital band each candidate honestly needs;
- a compounding map for what unlocks later work;
- a support-bundle map for what each candidate should ask from the ecosystem;
- a renewal-burden map for what it costs to keep each one honest after launch;
- a distortion-risk map for how the best ideas most easily go wrong while still looking successful;
- a boundary map for where the value should live first;
- a decision-rights map for who must agree before value appears; and
- a reversibility map for how safely a worthy contribution should begin.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **how fast can it learn whether the latest change helped, hurt, drifted, or simply failed to generalize?**
> Is this a same-day local-truth seam? A per-commit evidence seam? A nightly/beta/stable release-train seam? A cross-tool tuple-acceptance seam? An incident-driven operator seam? Or a slow institutional/program seam?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** replace the proof-burden map.
It does **not** replace the renewal-burden map.
It explains the **learning clock** or **time-to-truth profile** attached to each worthy contribution so future portfolio passes stop budgeting six different tempo classes as if they were interchangeable.

Read with:
- `design/epic-contribution-proof-burden-map-2026Q1.md`
- `design/epic-contribution-renewal-burden-map-2026Q1.md`
- `design/epic-contribution-reversibility-map-2026Q1.md`
- `design/epic-contribution-decision-rights-map-2026Q1.md`
- `design/epic-contribution-compounding-map-2026Q1.md`
- `design/epic-contribution-boundary-map-2026Q1.md`
- `design/portfolio-exemplar-federation-2026Q1.md`
- `design/shared-spine-execution-blueprint-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
Current Rust signals are no longer just telling us what hurts, what is fundable, what must be proven, or how safely something should roll out.
They are also telling us something stricter:
**several of the strongest bets differ mainly in how long it takes to get a trustworthy signal after a change.**
That is not the same as importance, proof burden, or upkeep burden.

The compiler-performance picture is the clearest reason.
The 2025 compiler performance survey results break the pain into incremental rebuilds, IDE/type-checking, clean and CI builds, debug info, and understanding why builds are slow. That is a strong sign that the broadest practical pain is not just “compilation is bad”; it is “teams need faster, more truthful loops for understanding what just happened.”
https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Cargo build-analysis work makes the second reason explicit. The current goal is to record build metadata across invocations and surface why crates rebuilt and what prior builds took. That is a direct attempt to shorten the time from “the build felt wrong” to “we have a machine-usable explanation tied to a concrete invocation history.”
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

The rustc-perf improvements goal sharpens the same point from the infrastructure side. It is not just about collecting more numbers. It is explicitly about multiple collectors, configuration-specific comparison, coverage expansion, and status/health surfaces. That is learning-clock design: some truths only become honest if they are compared within the right configuration and renewed continuously.
https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html

The build-dir layout testing call adds a third lesson. Cargo could not learn enough from internal reasoning alone; downstream tools were explicitly asked to run real tests because a crater-style pass would not be the whole story. That is an example of a seam whose learning clock is slower and wider than one local patch cycle.
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

The debugging survey makes a fourth lesson explicit. “Truly stellar” debugging spans debugger versions, operating systems, visualizers, async support, and expression evaluation. That is not a same-day local truth seam. It is a multi-tuple acceptance seam whose trustworthy clock is inherently slower than a local CLI report.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The release model matters too. Rust still uses nightly, beta, and stable release channels, with nightly every day and beta/stable moving on a train schedule. Some worthy contributions therefore live on a release-train clock whether they like it or not: they only become honest after nightly exposure, beta soak, or stable fallout.
https://doc.rust-lang.org/book/appendix-07-nightly-rust.html

Registry and operator work reveal a different clock again. The February 2026 crates.io notification-policy update and the March 2026 Cargo advisory both show that package-ingress truth can be quiet for weeks and then suddenly become urgent when a real route, registry, or extraction boundary is involved. That is not a steady inner loop. It is an incident-and-operator loop.
https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

Finally, the 2026 goals overview and the Foundation's 2026–2028 strategy remind us that some seams are simply slower because they are program-shaped. Annual goals, sustainable maintenance, and institutional adoption work are real — but they do not learn on the same cadence as a companion build doctor.
https://rust-lang.github.io/rust-project-goals/2026/
https://rustfoundation.org/strategic-plan/

The missing layer is therefore not another ranking rewrite.
It is a **learning-clock map**.

## Headline answer
The archive should now assume:

> every worthy Rust contribution needs an explicit **learning-clock claim**:
> **same-day local truth**, **cross-invocation / per-commit truth**, **release-train truth**, **tuple-matrix acceptance truth**, **incident / route-owner truth**, or **institutional / program truth**.
> If the archive cannot say how long it takes for a change to produce a trustworthy signal, it is still reasoning at the wrong level.

Fast clock does **not** mean more important.
Slow clock does **not** mean unworthy.
The point is to stop confusing **“important problem”** with **“fast-learning first build”**.

## The six learning-clock families

### 1) Same-day local truth
Use this when one team can change something in the morning and get a meaningful, replayable, locally-trustworthy answer by the end of the day.

Typical shape:
- local report or doctor command;
- comparison pack for one workspace;
- exemplar-backed before/after diff;
- lineaged receipt attached to a single developer workflow.

Typical artifacts:
- report JSON plus human explanation;
- diff receipt;
- workspace-local repro pack;
- CI attachment that does not need ecosystem consensus.

Wrong shape:
- making same-day local evidence pretend it already settled cross-tool or ecosystem truth.

### 2) Cross-invocation / per-commit truth
Use this when the signal is still local or team-controlled, but only becomes honest after repeated runs, commit comparisons, or a small rolling corpus.

Typical shape:
- build metadata across invocations;
- regression/watch receipts in CI;
- compare-within-configuration perf data;
- witness programs or compatibility exemplars rerun across releases.

Typical artifacts:
- per-commit comparison pack;
- rolling benchmark history;
- witness-result ledger;
- expiry-tagged evidence bundle.

Wrong shape:
- collapsing a multi-run or history-sensitive seam into a one-shot benchmark screenshot.

### 3) Release-train truth
Use this when a change only becomes honest after exposure on nightly, beta, stable, docs/build services, or other release-driven routes.

Typical shape:
- nightly feature/testing lane;
- beta soak or migration rehearsal;
- stable release watch;
- docs.rs/default or target posture confirmation.

Typical artifacts:
- nightly/beta/stable status slice;
- release-note-linked diff pack;
- stable-fallout triage board;
- release-window renewal receipt.

Wrong shape:
- claiming release-train truth on the basis of one nightly success or one pre-release anecdote.

### 4) Tuple-matrix acceptance truth
Use this when the seam is only real if several tools, operating systems, debuggers, targets, or surrounding tuples keep accepting the same artifact family.

Typical shape:
- debugger acceptance matrix;
- cross-tool fixture corpus;
- per-tuple screenshot/log/result pack;
- interoperability regression board.

Typical artifacts:
- tuple matrix with explicit pass/fail receipts;
- fixture replays;
- expected-behavior corpus;
- per-tuple exception records.

Wrong shape:
- treating one tuple, one debugger, or one polished demo as the real acceptance surface.

### 5) Incident / route-owner truth
Use this when the seam only becomes fully honest under security incidents, package ingress, registry routes, quarantines, or operator response pressure.

Typical shape:
- dry-run gateway plus operator policy table;
- incident replay corpus;
- quarantine/extraction sandbox;
- tabletop exercises and route-specific exception handling.

Typical artifacts:
- route-decision logs;
- incident replay packs;
- allow/deny receipts;
- escalation and override records.

Wrong shape:
- waiting for a real production incident as the only proving ground.

### 6) Institutional / program truth
Use this when the seam is fundamentally slower because it depends on standards-adjacent corpora, readiness profiles, adoption programs, procurement posture, or multi-organization stewardship.

Typical shape:
- readiness commons;
- profile/checklist corpus;
- domain pilot program;
- annual or quarterly governance review.

Typical artifacts:
- versioned readiness profiles;
- renewal agenda and decision log;
- named steward commitments;
- domain pilot receipts and exception records.

Wrong shape:
- demanding same-week product metrics from a seam whose real clock is standards, policy, or institutional adoption.

## Learning-clock-adjusted view of the strongest contributions
This is **not** a broad-importance rerank.
It is a “how fast can this seam learn something truthful after a change?” comparison.

### 1) Build-State Evidence
**Learning-clock family:** 1 -> 2

Why:
- the pain is broad and the loop can be short;
- Cargo's build-analysis direction is explicitly about surfacing why a build rebuilt and what timing history looked like;
- compiler-performance survey results show that incremental rebuilds, understanding slowness, and inner-loop cost are exactly where faster truth matters most.

What a good first move looks like:
- local report command;
- per-invocation lineage receipts;
- CI comparison pack;
- exemplar federation coverage for at least one public inner-loop workspace and one shadow/private twin.

What to refuse:
- a hosted “build score” portal before a replayable local pack exists;
- one benchmark hero number standing in for build-state truth.

### 2) Semantic Context / Tooling Contract / Shared Spine
**Learning-clock family:** 1 -> 2

Why:
- these are hidden multipliers only if they shorten downstream learning loops;
- they should make build evidence, compatibility claims, and adoption guidance cheaper to regenerate and compare;
- they fail when they become an abstract schema empire whose own learning clock is slower than the seams it supposedly helps.

What a good first move looks like:
- thin envelope with lineage and expiry;
- stable-to-unstable surface labeling;
- linter/validator that catches overclaim quickly;
- exemplar-backed fixture packs used by at least two other seams.

What to refuse:
- giant universal schema work before it makes any existing pack faster or more honest.

### 3) Feedback Loop / Debuggability Acceptance
**Learning-clock family:** 4

Why:
- the seam is real and under-served, but its honest clock is slower because the survey explicitly frames the gap across debuggers, operating systems, visualizers, async workflows, and expression evaluation;
- a local debugger demo can teach something, but it cannot settle the acceptance problem.

What a good first move looks like:
- fixture matrix for debugger tuples;
- expected async-stepping and expression-evaluation receipts;
- screenshot/log pack plus replay harness;
- explicit per-tuple exceptions instead of blanket support claims.

What to refuse:
- “we debugged one Tokio app in one debugger once, so Rust debugging is solved now.”

### 4) Adoption Navigation + Ecosystem Atlas
**Learning-clock family:** 1 -> 3

Why:
- editorial/default guidance can be published quickly, but it only stays honest if it is tethered to faster evidence seams and release-train drift checks;
- the 2025 survey says docs remain canonical while editor/LLM mediation rises, which means this seam is strategically real but unusually vulnerable to publishing faster than it learns.

What a good first move looks like:
- default-lane cards with source lineage;
- expiry and renewal tags;
- “what changed since last pass” receipts;
- explicit fallback to canonical docs and evidence packs.

What to refuse:
- recommendation portals that move faster than source renewal;
- editorial summaries that cannot point back to current proving grounds.

### 5) Compatibility Claims
**Learning-clock family:** 2 -> 3

Why:
- witness programs, semver checks, and compatibility exemplars can learn on a rolling rerun clock, but default policy should widen only after release-train evidence is clean;
- this seam is faster than debugging acceptance and slower than a local report.

What a good first move looks like:
- witness-program corpus;
- rerunnable claim receipts;
- default-with-override rollout;
- release-window renewal before stronger defaults.

What to refuse:
- turning one witness pass into permanent ecosystem law.

### 6) Package Intake Gateway
**Learning-clock family:** 5, with synthetic 1 -> 2 rehearsal loops

Why:
- the operator/security seam is route-shaped and incident-shaped;
- the recent crates.io policy and Cargo advisory show that route ownership and real exposure matter;
- if this seam waits for live incidents to learn, it is too late.

What a good first move looks like:
- dry-run classifier;
- extraction sandbox;
- incident replay corpus;
- tabletop and quarantine receipts;
- operator-visible staged enforcement path.

What to refuse:
- trust-score theater detached from route control;
- “we'll know whether it works at the next real incident” as the whole plan.

### 7) Safety-Critical Readiness Commons
**Learning-clock family:** 6

Why:
- this seam is strategically important but learns slowly because it depends on shared profiles, traceability, procurement/adoption posture, and named long-horizon stewardship;
- it should not be forced to impersonate a same-day product loop.

What a good first move looks like:
- readiness profile corpus;
- dependency lifecycle templates;
- domain pilot receipts;
- quarterly or release-bound review cadence with named stewards.

What to refuse:
- one checklist PDF or one badge marketed as readiness completion.

### 8) StableMIR / rustc_public / build-std / Rust-for-Linux stable tooling
**Learning-clock family:** 3 -> 6

Why:
- these are substrate or stabilization seams;
- they may produce local wins, but their honest public learning clock is usually release-train or institutional because toolchain stabilization, downstream adoption, and maintained compatibility all matter.

What a good first move looks like:
- sharply bounded unstable-to-stable milestones;
- versioned support story;
- named downstream pilots;
- release-bound compatibility watch.

What to refuse:
- dressing a stabilization program up as a quick public-platform epic.

## Portfolio consequence
The archive should now say something stricter than “Build-State Evidence ranks first.”
It should say:

> **Build-State Evidence** remains the strongest broad first build partly because it has the best combination of broad pain and fast truthful learning clock.
> **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build partly because it solves a real pain but carries a slower tuple-matrix acceptance clock.
> **Adoption Navigation** should widen only as fast as its evidence imports renew.
> **Package Intake Gateway** is strategically urgent but learns on an incident/operator clock and therefore needs synthetic proving grounds.
> **Safety-Critical Readiness Commons** remains real but should not be used as the first public portfolio bet because its honest clock is institutional and slow.

## Design rules the archive should now enforce
For any proposed worthy contribution, the repo should now require five explicit statements:

1. **Fastest truthful loop** — what is the shortest honest learning cycle this contribution can run on?
2. **Graduation loop** — what slower loop must still pass before stronger claims or defaults are justified?
3. **Synthetic proving ground** — what replay, fixture, exemplar, tabletop, or witness pack avoids waiting for live incidents or broad fallout?
4. **Expiry boundary** — when does the current evidence go stale?
5. **Wrong tempo to refuse** — what would count as widening or canonicalizing the seam faster than it can honestly learn?

## What this means in practice
The archive should now prefer:
- first builds that can create **same-day or per-commit truth** against broad pain;
- hidden substrate work only when it **shortens later learning clocks** rather than merely adding structure;
- explicit release-train receipts for anything that claims stable default posture;
- tuple matrices for debugger or interoperability claims;
- synthetic incident replays for intake/security work; and
- named quarterly or annual stewardship loops for readiness or standards-adjacent programs.

It should now refuse:
- platform ideas whose learning clock is slower than their rollout ambition;
- editorial/default layers that publish faster than their evidence renewal;
- security/intake designs that only learn under live fire;
- debugger claims that skip tuple coverage; and
- institutional seams forced into startup-style product metrics.

## Net effect on the archive
This note does not change the broad ladder.
It changes how the archive chooses **what should happen first under real tempo constraints**.
The repo should now say explicitly not only **what is missing**, **what should be built**, **who should support it**, **where it should live**, **what it must prove**, **how safely it should roll out**, and **who must agree** — but also **how quickly it can learn something truthful once work begins**.
