# Design: Epic contribution decision-rights map (2026Q1)

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
- a distortion-risk map for how the best ideas most easily go wrong while still looking successful; and
- a boundary-fit map for where the value should actually live.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **who actually has to agree before value appears?**
> Which contributions can help one team immediately? Which need narrow upstream permission? Which need operator or service-owner opt-in? Which demand debugger/tool/vendor tuple agreement? Which are inherently consortium or standards programs?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** replace the support-bundle map.
It does **not** replace the boundary-fit map.
It explains the **decision-rights burden** or **consensus drag** attached to each worthy contribution, so future portfolio passes stop treating every strong idea as if it had the same path to first value.

Read with:
- `design/epic-contribution-support-bundle-map-2026Q1.md`
- `design/epic-contribution-boundary-map-2026Q1.md`
- `design/epic-contribution-proof-burden-map-2026Q1.md`
- `design/epic-contribution-renewal-burden-map-2026Q1.md`
- `design/epic-contribution-distortion-risk-map-2026Q1.md`
- `design/epic-contribution-compounding-map-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-exemplar-federation-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
Current Rust signals are no longer just telling us “what is missing”, “what is fundable”, or “what should stay outside upstream”.
They are telling us something stricter:
**several of the strongest bets differ mainly in how much agreement they require before users feel any value at all.**
That is not the same as rank, proof burden, or owner fit.

The 2026 goals overview makes the first part explicit: accepted Rust goals require identified champions and review support, and new goals may only be added if the required resources are already known. That means “good idea” and “work that can actually move now” are distinct categories in the project's own process.
https://rust-lang.github.io/rust-project-goals/2026/
https://rust-lang.github.io/rust-project-goals/about/owners.html

Cargo's own posture shows the opposite side of the same lesson. The external-tools chapter routes integrations through metadata, JSON messages, and custom subcommands. The Cargo plumbing goal explicitly says to prototype a **third-party cargo subcommand** to learn what Cargo should eventually integrate. Cargo's 1.93 and 1.94 cycle posts repeat that Cargo cannot be everything to everyone because of compatibility guarantees. Together these sources show that some high-value work can create immediate local value without waiting for global agreement, so long as it stays companion-first and honest about its imports.
https://doc.rust-lang.org/cargo/reference/external-tools.html
https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

`cargo clippy` adds a useful middle example: it is an **external command distributed with the Rust toolchain as an optional component**, not built into Cargo itself. That is a real delivery/decision-rights shape the archive should name more often: some ecosystem value does not need to become Cargo core to become broadly reachable.
https://doc.rust-lang.org/cargo/commands/cargo-clippy.html

The project-wide challenges writeup and the 2025 State of Rust survey reinforce why this matters strategically. Practical pain remains concentrated in compile/resource costs, debugging, tacit knowledge, and domain-specific friction — but those pains are not all blocked on the same people. Some can be relieved by one team using a companion report locally; others need many maintainers, vendors, or operators to agree on shared tuples, norms, or evidence families.
https://blog.rust-lang.org/2026/03/20/rust-challenges/
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The debugging survey is especially clarifying. It frames “truly stellar” debugger support as spanning debugger versions, operating systems, visualizers, async support, and expression evaluation. That is not the decision-rights profile of a bootstrap companion tool; it is a cross-tool acceptance problem.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

Registry and security updates show another distinct case. The crates.io malicious-crate notification policy now narrows public notifications to reduce noise, and the March 2026 Cargo advisory distinguishes crates.io mitigation posture from alternate-registry exposure. That means package-ingress work often depends on **operator and vendor route decisions**, not just on one checker existing.
https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

The missing layer is therefore not another ranking rewrite.
It is a **decision-rights map**.

## Headline answer
The archive should now assume:

> every worthy Rust contribution needs an explicit **decision-rights claim**:
> **single-team / unilateral**, **local-first with narrow upstream asks**, **operator/service opt-in**, **cross-tool tuple agreement**, or **consortium / standards / governance-grade**.
> If the archive cannot say who must agree before value appears, it is still reasoning at the wrong level.

Decision-rights burden is not the same as importance.
High-consensus work can still be the most strategically important work.
The point is to stop confusing **“strongest idea”** with **“fastest path to first real value”**.

## The five decision-rights families

### 1) Single-team / unilateral value
Use this when one team can adopt the contribution locally and get real value without waiting for upstream, vendors, or a consortium.

Typical shape:
- local report command;
- CI-importable checker;
- reviewable evidence pack;
- exemplar-backed companion CLI.

Typical permission burden:
- one team decides to run it;
- maybe one maintainer chooses to carry the artifact in CI.

Wrong shape:
- pretending a local improvement already implies ecosystem-wide recommendation.

### 2) Local-first value with narrow upstream asks
Use this when the first value is still unilateral or team-local, but the contribution becomes far cleaner if upstream exposes one or two better machine-facing surfaces.

Typical shape:
- companion tool first;
- narrow request for stable IDs, structured outputs, or metadata carriage later;
- optional toolchain distribution after proof exists.

Typical permission burden:
- one team can start now;
- broader adoption improves when a relevant upstream team agrees to a bounded hook.

Wrong shape:
- blocking the whole effort on full upstream merger.

### 3) Operator / service-owner opt-in
Use this when the value depends on registry owners, CI/platform operators, mirror vendors, docs/build services, or security responders making route-specific choices.

Typical shape:
- ingress gateway;
- policy bridge;
- operator-facing checker plus receipts;
- service-specific pack import.

Typical permission burden:
- value is real only when the service or operator controlling the route chooses to enforce or import it.

Wrong shape:
- pretending a public dashboard or local scanner settles operator posture.

### 4) Cross-tool / tuple agreement
Use this when the seam is only real if several tools, versions, platforms, or runtime tuples agree on behavior, acceptance criteria, or regression signals.

Typical shape:
- acceptance matrix;
- shared fixtures;
- per-tuple receipts and regressions;
- consortium or interoperability loop.

Typical permission burden:
- several maintainers or tool owners must keep accepting the shared tuple discipline.

Wrong shape:
- shipping one plugin or one golden demo and calling the problem solved.

### 5) Consortium / standards / governance-grade agreement
Use this when the value depends on shared readiness profiles, coding rules, assurance cases, procurement posture, or long-horizon cross-organization stewardship.

Typical shape:
- readiness commons;
- profile/checklist corpus;
- standards-adjacent evidence library;
- ongoing consortium program.

Typical permission burden:
- many institutions must keep the artifact alive and trustworthy over time.

Wrong shape:
- pretending one crate, one badge, or one startup makes the seam real.

## Decision-rights-adjusted view of the strongest contributions
This is **not** a broad-importance rerank.
It is a “who has to agree before value appears?” comparison.

### 1) Build-State Evidence
**Decision-rights family:** 1 → 2

Why:
- one team can gain immediate value from local build-state reports, lineaged explanation packs, and CI receipts;
- Cargo build-analysis work helps, but the first useful artifact does not require full upstream blessing;
- narrow upstream hooks make the companion layer better later.

What a good first move looks like:
- local-first `cargo` companion reports;
- exemplar-backed receipts;
- explicit “imported from Cargo” versus “derived locally” boundaries.

Strategic consequence:
- this remains the strongest broad first build **and** one of the lowest-consensus-drag builds.

### 2) Semantic Context / Tooling Contract / Shared Spine
**Decision-rights family:** 1 → 2

Why:
- these are hidden multipliers that can start as companion contracts and validators;
- they benefit from better upstream surfaces, but they do not need ecosystem consensus to prove local value;
- their early job is to make later evidence packs and assistants more honest.

What a good first move looks like:
- local validator/linter;
- explicit lineage envelope;
- fixture corpus and import-strength markers.

Strategic consequence:
- these remain strong early substrate bets precisely because their decision-rights burden is modest compared with their multiplier value.

### 3) Adoption Navigation + Ecosystem Atlas
**Decision-rights family:** 2 → 3

Why:
- one team can publish better maps and defaults without asking permission from Cargo;
- but honest widening needs maintainers, exemplar donors, and service-specific freshness work;
- once defaults start influencing many teams, the burden becomes partly editorial and partly operator-shaped.

What a good first move looks like:
- editorial commons first;
- clearly scoped consumer classes;
- freshness receipts and local-fit warnings rather than universal verdicts.

Strategic consequence:
- still worthy, but not a zero-consensus bet once it starts guiding many downstream decisions.

### 4) Package Intake Gateway
**Decision-rights family:** 3

Why:
- this seam lives at registry, mirror, CI, and operator boundaries;
- local analysis can help, but actual protection or routing value depends on the people who own the route;
- public-registry posture and alternate-registry posture are not the same thing.

What a good first move looks like:
- operator bridge with fail-closed imports;
- route-aware receipts;
- vendor- or operator-specific posture cards rather than universal trust scores.

Strategic consequence:
- urgent and real, but not a unilateral build in the same way build evidence is.

### 5) Feedback Loop / Debuggability Acceptance
**Decision-rights family:** 4

Why:
- the value is only real if debugger, version, OS, visualization, and async tuples hold together;
- one tool plugin or one IDE feature can help locally, but the seam the archive cares about is ecosystem acceptance.

What a good first move looks like:
- shared acceptance matrix;
- fixtures and regression receipts;
- explicit per-tuple states.

Strategic consequence:
- still the clearest second serious build, but also a high-consensus-drag program that should not be budgeted like a two-person sidecar.

### 6) Safety-Critical Readiness Commons
**Decision-rights family:** 5

Why:
- value depends on cross-organization confidence, profile maintenance, dependency-lifecycle guidance, and institutional stewardship;
- one evidence kit can help, but readiness is not real until many actors agree on what counts.

What a good first move looks like:
- consortium-backed profiles and receipts;
- named owners;
- explicit expiry and renewal rules.

Strategic consequence:
- still one of the most worthy long-horizon seams, but the archive should never confuse it with a unilateral product bet.

## The main portfolio lesson
The archive should now assume three different early-build postures:

1. **Low-consensus, high-leverage first builds**
   - Build-State Evidence
   - Shared Spine / Tooling Contract / Semantic Context

2. **Medium-consensus wideners and bridges**
   - Adoption Navigation
   - Package Intake Gateway

3. **High-consensus program seams**
   - Feedback Loop / Debuggability Acceptance
   - Safety-Critical Readiness Commons

That is not a value judgment.
It is a decision-latency judgment.

## What a distortion-resistant portfolio answer looks like now
Future portfolio recommendations should now say all of the following explicitly:
- **what the contribution is worth**;
- **where it should live**;
- **what it should ask for**;
- **what it must prove**;
- **what it costs to renew**;
- and **who must agree before users feel value**.

If one of those is missing, the answer is still under-specified.

## Practical design rules
1. Prefer **low-consensus, high-leverage** first builds when choosing a bootstrap portfolio.
2. Do not demote a contribution just because it is high-consensus; instead, change its vehicle and time horizon.
3. Do not let one local proof masquerade as cross-tool agreement.
4. Do not let one public-registry or hosted-service posture masquerade as all routes.
5. Do not let “upstream champion exists” masquerade as “ecosystem consensus exists”.
6. Do not let a toolchain-distributed optional component masquerade as Cargo core.
7. Do not let consortium language masquerade as live fixtures, matrices, owners, or renewal receipts.

## Bottom line
The strongest early Rust portfolio is still not “pick the coolest idea and go all in”.
It is:
- start with the contributions whose value can appear under **unilateral or local-first** decision rights;
- use those to generate stronger artifacts, exemplar packs, and bounded upstream asks;
- then spend coalition energy on the seams that are genuinely **cross-tool** or **consortium-grade**;
- and never confuse **importance** with **how many people must agree before the idea becomes real**.
