# Design: Maintainer Reality / Keystone Stewardship execution blueprint (2026 Q1)

## Goal
Turn one of the archive's clearest **program-shaped worthy contributions** into a sharper **buildable program**.

The missing contribution is not another crate score, another maintainer shaming dashboard, another private spreadsheet for funders, or another popularity ranking with governance vibes attached.
It is a disciplined companion layer that lets Rust teams carry **portable stewardship truth** across day-to-day maintenance work, keystone-project review, support routing, and continuity planning.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team, foundation-adjacent program, or ecosystem lab wants to build the archive's best maintainer/stewardship contribution, what should that project actually ship in theory and practice?

Read with:
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/maintenance-reality-stack.md`
- `design/maintenance-reality-lane-map.md`
- `design/keystone-stewardship-stack.md`
- `design/stewardship-pilot-program.md`
- `design/maintenance-reality-contract-2026Q1.md`

## Why this note is needed now
The archive already knew that **Maintainer Reality / Keystone Stewardship** mattered.
What it still lacked was a crisper answer to **what the worthy contribution should look like**.

Fresh official signals sharpen that answer:
- Rust's March 2026 challenges writeup says ecosystem navigation still depends on tacit knowledge and that maturity varies sharply across domains, which means teams still struggle to tell what they can responsibly bet on.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says there was a slight uptick for "developer and maintainers support", says funding should focus on retaining people who would otherwise leave after unpaid labor, and explicitly asks companies to support contributors and crate authors they rely on.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The Rust Foundation's 2026–2028 strategy makes **Sustainable Maintenance** a core pillar and says Rust needs a well-resourced, well-supported community of people who maintain and support it.
  https://rustfoundation.org/strategic-plan/
- The Foundation's January 2026 strategy/annual-report post says it invested $2.0M in 2025 on full-time Rust maintenance work, infrastructure, grants, and ecosystem support, which means maintainer sustainability is no longer just rhetoric.
  https://rustfoundation.org/media/annual-report-strategy-2025/
- The Maintainers Fund announcement says the goal is consistent, transparent, long-term support aligned with high-impact Rust priorities and maintainer continuity.
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- The Leadership Council's December 2025 update says the 2026 Project Priorities budget continues compiler operations and other maintenance support for the Rust project.
  https://blog.rust-lang.org/inside-rust/2025/12/10/leadership-council-update/
- Official writing on maintenance says the work includes triage, CI failures, security incidents, docs upkeep, review, refactoring, and contributor unblocking; it also says the work is hard to demonstrate precisely because success often looks like continued stability and because the effect is multiplicative.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- Compiler Operations and infrastructure updates make triage meetings, stale review follow-up, tooling upkeep, and triagebot ergonomics explicit project machinery rather than invisible volunteer glue.
  https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
  https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
- Rust Forge's issue and PR triage procedures already define real labels, thresholds, reports, and routing expectations, which means maintenance work has enough shared shape to export honestly.
  https://forge.rust-lang.org/release/issue-triaging.html
  https://forge.rust-lang.org/release/triage-procedure.html
- The Rust Innovation Lab says some Rust projects have matured into critical infrastructure and need neutral governance plus reliable institutional backing, which is direct evidence that keystone stewardship is a distinct layer above ordinary crate metadata.
  https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/

Taken together, those signals say the archive should stop describing maintainer reality only as a social concern or a future funding conversation.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's strongest maintainer/stewardship contribution, the answer should now be:

> Build a **Stewardship Truth layer** that records declared lifecycle, observed maintenance operations, keystone criticality, institutional support, continuity risk, and bounded support/funding handoffs in one reviewable pack.

That answer is deliberately narrower than “fix open-source sustainability”.
It is also deliberately stronger than “publish health metrics”.

## What this contribution should be in theory

### Core thesis
A stewardship system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what subject is under stewardship review;**
2. **what maintenance work and workflow policy are actually visible;**
3. **what lifecycle or support commitments are explicitly declared;**
4. **why the subject is ordinary, keystone, or keystone-adjacent infrastructure;**
5. **what institutional backing, continuity posture, and risk concentration actually exist;**
6. **what downstream consumers may honestly conclude, route, or fund from that evidence.**

If a project cannot answer those questions without commit-graph folklore, issue-thread archaeology, private spreadsheets, and blog-post memory, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable stewardship review and routing**.

It should include:
- declared lifecycle and support posture;
- workflow policy and observed maintenance operations;
- explicit help requests and routing posture;
- keystone criticality and obligation profiles;
- continuity and concentration risk facts;
- bounded handoffs for adoption, funding, governance, and support programs.

It should not become:
- a universal health score;
- an automatic grant allocator;
- a popularity ranking site;
- a mandatory registry badge program;
- or a replacement for local maintainer judgment.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **subject truth** — what project, crate, service, or workspace is actually under review;
- **lifecycle truth** — what support windows, deprecations, successors, or handoff intentions are explicitly declared;
- **operations truth** — what queue policy, queue state, review pressure, triage load, release/backport posture, or mentoring capacity is actually observed;
- **keystone truth** — why the subject is foundational enough to justify keystone review, and what blast radius matters;
- **support / institutional truth** — what volunteer, employer-backed, grant-backed, foundation-hosted, or mixed backing exists;
- **consumer truth** — what atlas/adoption, trust/policy, support/funding, or assistant consumers may conclude, with what lossiness.

This is the largest theory/practice guardrail in the design.
Without it, every stewardship summary turns into a confidence soup.

### Shape rule
This contribution should begin as a **reference layer + corpus/atlas + report/pack command**, with an optional stewarded-program overlay.
That means:
- a **reference layer** for lifecycle, operations, keystone, and continuity facts;
- a small **corpus/atlas** for keystone classes, obligation classes, routing classes, and risk categories;
- and a thin **command / pack layer** that imports local workflow evidence instead of replacing it.

It should not begin as a hosted dashboard, a ranking brand, or a funding committee in tool form.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo stewardship declare`
- `cargo stewardship observe`
- `cargo stewardship route`
- `cargo stewardship keystone`
- `cargo stewardship diff`
- `cargo stewardship doctor`
- `cargo stewardship export --consumer <atlas|fund|policy|support|docs|assistant>`
- `cargo stewardship pack`

The tool should **import** existing workflow and governance surfaces when available rather than replacing them.

### Public artifact spine

#### Imported/internal families
- `lifecycle-pack/v0`
- `steward-pack/v0`
- `maintenance-reality-pack/v0`
- `keystone-pack/v0`
- optional release / trust / support attachments

#### Public review families
- `stewardship-subject/v0`
- `lifecycle-support-profile/v0`
- `maintenance-operations-report/v0`
- `keystone-criticality-profile/v0`
- `institutional-support-profile/v0`
- `continuity-risk-register/v0`
- `stewardship-routing-brief/v0`
- `stewardship-truth-pack/v0`
- `stewardship-handoff/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — crate/workspace/service/org identity, scope, included and excluded lanes, and review intent;
- **authority posture** — declared by maintainers, observed from workflow state, imported from public governance/foundation/support artifacts, or inferred;
- **visibility posture** — public, mixed, restricted-summary, or restricted-only;
- **coverage / completeness** — exact, partial, stale, mixed, or unavailable;
- **steward anchors** — maintainer role classes, governance posture, workflow lane, release/support obligations, and review horizon;
- **criticality anchors** — keystone class, ecosystem role, blast radius, dependency posture, and non-claims;
- **risk anchors** — single-maintainer concentration, release-authority concentration, funding uncertainty, governance ambiguity, or infrastructure concentration;
- **reason-coded conclusions** — committed / best-effort / partial / watch / unsupported / inconclusive with explicit ambiguity;
- **consumer limits** — what atlas/fund/policy/support/assistant consumers may and may not claim.

### Commands and what they should emit

#### `cargo stewardship declare`
Purpose:
- record lifecycle and support intent;
- capture support windows, deprecation/successor posture, help-seeking posture, and declared obligations;
- emit `lifecycle-support-profile/v0`.

Important rule:
- declared intent must never be inferred from repo activity alone.

#### `cargo stewardship observe`
Purpose:
- attach queue policy and observed operations evidence;
- preserve review pressure, triage load, stale states, release/backport posture, and mentoring intake;
- emit `maintenance-operations-report/v0`.

Important rule:
- observed operations and derived pressure findings must stay separate.

#### `cargo stewardship route`
Purpose:
- turn explicit help requests and pressure findings into bounded routing facts;
- preserve public vs restricted posture, escalation targets, and action classes;
- emit `stewardship-routing-brief/v0`.

Important rule:
- pressure without routing is only observability, but routing without visibility policy becomes coercive.

#### `cargo stewardship keystone`
Purpose:
- attach keystone-criticality, obligation, institutional-support, and continuity-risk facts;
- emit `keystone-criticality-profile/v0`, `institutional-support-profile/v0`, and `continuity-risk-register/v0` as appropriate.

Important rule:
- keystone status is not a compliment and not a popularity rank; it is a status with obligations and explicit non-claims.

#### `cargo stewardship diff`
Purpose:
- compare two stewardship packs while preserving the distinction between:
  - changed lifecycle declarations,
  - changed workflow/operations posture,
  - changed keystone status,
  - changed institutional backing,
  - and changed consumer-allowed conclusions.

#### `cargo stewardship doctor`
Purpose:
- attach bounded next-step suggestions such as “declare support window”, “separate public help request from restricted capacity note”, “explicitly name successor/handoff posture”, “recheck keystone criticality”, or “record release-authority concentration”.

Important rule:
- suggestions should always point back to explicit fact gaps rather than moralize.

#### `cargo stewardship export`
Purpose:
- emit smaller adoption/fund/policy/docs/assistant slices without making those slices canonical by themselves.

## Ranked feature set

### P0 — required for a worthy v0
- explicit subject + scope capture;
- declared lifecycle / support posture;
- workflow policy + observed operations import for at least one real lane;
- explicit help request + routing posture;
- keystone criticality profile with non-claims;
- institutional-support posture and continuity-risk register;
- one portable brief plus one portable pack;
- lossiness-visible exports for atlas/fund/policy consumers.

### P1 — very strong early multiplier
- release/backport / security-response obligation lanes;
- mixed public/private posture support;
- transition reporting for governance or funding changes;
- maintainer concentration deltas over time;
- mentor / newcomer intake capacity tracking;
- bounded assistant-ready and docs-ready summaries.

### P2 — useful only after P0/P1 are solid
- cross-project comparison overlays;
- ecosystem keystone atlases;
- sponsor-facing portfolio summaries;
- service integrations and hosted views.

## Ranked proving lanes

### 1) PR triage / stale review lane
Why first:
- Forge already defines labels, thresholds, and report shape;
- it proves operations truth without inventing a new workflow;
- and it makes invisible review burden visible without claiming to solve governance by itself.

### 2) Maintainer-help routing lane
Why second:
- the ecosystem now has real support programs and funding conversations;
- it proves the layer can move from evidence to action without becoming a private spreadsheet;
- and it is the cleanest way to show the value of explicit asks.

### 3) Keystone security / foundational library lane
Why third:
- it proves criticality, obligation, and institutional-backing fields on a subject where the blast radius is real;
- and it exercises continuity-risk and public-vs-restricted posture honestly.

### 4) Release / backport continuity lane
Why fourth:
- it shows that stewardship truth is not only social metadata but also shipping risk;
- and it connects maintenance reality to operational release obligations.

### 5) Consumer-import lane
Why fifth:
- atlas/adoption, fund/support, and policy/trust consumers should prove they can import bounded summaries without silently redefining the source of truth.

## What the first serious v0 should look like
A worthy first release should likely be:
- one thin `cargo stewardship` companion tool;
- one public pack family centered on `stewardship-truth-pack/v0`;
- one lifecycle/support declaration path;
- one operations importer for a real triage workflow;
- one help-routing path;
- one keystone criticality + continuity overlay;
- and one bounded consumer export for a fund/program or atlas/adoption lane.

That is enough to prove the contribution shape.
It is not enough to justify a global ranking site, and it should not try.

## Strong default design choices

### Choose declarations plus observations, not heuristics alone
The system should prefer:
- declared lifecycle/support posture from maintainers,
- explicit workflow policy and snapshots,
- explicit institutional-backing records,
- and explicit non-claims.

It should distrust:
- stars,
- downloads,
- commit counts,
- contributor counts,
- or issue volume by themselves.

### Start with keystone reviews, not all crates.io
The best proving subjects are keystone or keystone-adjacent projects where obligations and continuity actually matter.
Do not begin by claiming universal registry coverage.

### Treat restricted details as first-class
Some continuity, funding, and capacity details may be sensitive.
The system should support honest public summaries with bounded omissions rather than forcing total disclosure or total silence.

### Keep adoption/funding consumers downstream
The canonical artifact is the stewardship pack.
Atlas/adoption, fund/program, and policy consumers should import it rather than replace it.

## What this contribution should not become
Do not let it become:
- a public leaderboard of “healthy” crates;
- a fund-allocation oracle;
- a universal badge program for crates.io;
- a hidden governance registry with public relations dressing;
- or a vague sustainability microsite that never reaches decision-grade artifacts.

## Why this counts as a worthy contribution
Ideal Rust is not only a language and tooling story.
It is also a stewardship story.
As Rust becomes more widely adopted and more central to critical systems, the ecosystem needs better ways to represent what maintenance, keystone status, continuity, and support actually look like.

A successful **Stewardship Truth** layer would not solve maintainer sustainability by itself.
But it would give maintainers, adopters, funders, and ecosystem programs a far better common surface than folklore, social graphs, or repo-activity vibes.
That is worthy.

## Default archive interpretation after this note
- **Build-State Evidence** still remains the strongest one-project answer overall.
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked missing middle in the daily developer loop.
- **Maintainer Reality / Keystone Stewardship** is now the clearest worthy **program-shaped execution blueprint** the archive has for ecosystem continuity and support truth.
- Its primary shape is now **reference layer + corpus/atlas + report/pack command**, optionally feeding stewarded programs.
- The right first proving lane is **triage + routing + keystone review**, not a registry-wide scoring dashboard.
- Future maintainer/stewardship revisions should keep **lifecycle truth**, **operations truth**, **keystone truth**, **institutional-support truth**, **continuity-risk truth**, and **consumer truth** separate.
