# Design: Maintenance Reality lane map

## Goal
Sharpen the archive’s existing **Maintenance Reality Stack** so future revisions stop flattening maintenance into one fake “healthy project” verdict.

The core move is simple:
- keep **declared lifecycle intent** separate from **observed operational state**;
- keep **observed state** separate from **derived pressure findings**;
- keep **help or funding requests** separate from both;
- keep **public views** separate from **restricted routing views**; and
- keep **consumer summaries** thinner than the imported evidence.

Read this with:
- [`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md)
- [`design/stewardship-pilot-program.md`](./stewardship-pilot-program.md)
- [`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md)
- [`design/stewardship-ops-kit.md`](./stewardship-ops-kit.md)
- [`proposals/epic-maintenance-reality-stack.md`](../proposals/epic-maintenance-reality-stack.md)

## Why this needs an explicit lane map now
Rust’s current signals are no longer saying only “maintenance matters”.
They are saying maintenance now spans **distinct operational and institutional lanes**:
- the Rust Foundation’s 2026–2028 strategy names **Sustainable Maintenance** as a core pillar;
- the Maintainers Fund announcement says support should be shaped in collaboration with the Rust Project and handled openly and with accountability;
- the maintainer-fund design note explicitly asks what maintenance even is and describes it as work whose success often looks like “things still work”;
- the Compiler Ops writeup frames review monitoring, triage, process upkeep, and coordination as real infrastructure;
- Forge triage docs already publish explicit queue states, thresholds, and routing semantics; and
- the 2025 State of Rust survey still shows support for developers and maintainers as an active concern while asking companies to support contributors and crate authors.

Those are not one lane. They are evidence that maintenance reality already has separable truths.

References:
- https://rustfoundation.org/strategic-plan/
- https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- https://rustfoundation.org/media/annual-report-strategy-2025/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
- https://forge.rust-lang.org/release/triage-procedure.html
- https://forge.rust-lang.org/release/issue-triaging.html
- https://forge.rust-lang.org/compiler/prioritization.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/

## The lane map

### 1) Lifecycle-intent lane
This lane is owned by **Lifecycle Ledger**.
It answers:
- what the project says about support windows, deprecation, successor relationships, co-maintainer posture, and handoff intent;
- which release lines are maintained;
- whether the project is stable, winding down, seeking help, or in transition.

Examples:
- `lifecycle-intent/v0`
- `support-window-map/v0`
- `handoff-consent/v0`
- `lifecycle-report/v0`

Design rule: **declared intent is not inferred from queue pressure.**

### 2) Workflow-policy lane
This lane is owned by **Stewardship Ops**.
It answers:
- which queues exist;
- which states and labels matter;
- what the stale or escalation thresholds are;
- what counts as blocked, ready, needs-info, needs-repro, backport-worthy, or mentoring-ready.

Examples:
- `queue-profile/v0`
- `workflow-template/v0`
- `service-level-budget/v0`

Design rule: **policy must stay separate from snapshots.**

### 3) Observed operational-state lane
This lane records what the workflow looked like during a bounded period:
- PRs waiting on review;
- issues needing repro or minimization;
- release/backport queues;
- mentoring or newcomer-intake activity;
- concrete action logs.

Examples:
- `queue-snapshot/v0`
- `steward-action-report/v0`

Design rule: **snapshots describe what was seen, not why it happened.**

### 4) Derived pressure-and-risk lane
This lane is analytic rather than declarative:
- reviewer concentration;
- aging queues;
- stale or blocked pockets;
- continuity risk;
- “single point of failure” observations;
- release-readiness or maintenance strain summaries.

Examples:
- `review-pressure-report/v0`
- `maintenance-reality-brief/v0` sections marked as derived
- `maintenance-transition-report/v0`

Design rule: **derived findings must not silently rewrite either lifecycle intent or raw snapshots.**

### 5) Help / succession / support-routing lane
This lane captures explicit asks and action paths:
- review help;
- release help;
- documentation or triage help;
- continuity or succession help;
- volunteer-only versus funded or institutional routing posture.

Examples:
- `help-request/v0`
- `support-routing-profile/v0`

Design rule: **pressure without routing is only observability; routing without explicit asks becomes guesswork.**

### 6) Mentoring and contributor-intake lane
This lane deserves its own identity because “newcomer friendly” and “maintained” are different truths.
It records:
- newcomer-ready work;
- mentored versus expert-only work;
- mentor capacity and response expectations;
- contributor intake follow-through.

Examples:
- `mentoring-lane/v0`

Design rule: **mentoring promises must not be inferred from a label alone.**

### 7) Visibility and redaction lane
Some maintenance facts are safe to publish broadly; some are only safe for restricted consumers.
This lane records:
- public versus restricted scope;
- redaction posture;
- whether concentration or burnout-adjacent findings are summarized rather than exposed raw;
- freshness and publication budgets.

Examples:
- visibility or redaction blocks inside `maintenance-reality-brief/v0`
- `maintenance-consumer-handoff/v0`

Design rule: **public and restricted maintenance views must never be confused.**

### 8) Consumer-handoff lane
This lane is where the stack becomes strategically useful.
It should provide thin summaries for:
- Atlas / adoption;
- release and policy review;
- keystone stewardship review;
- support or fund programs;
- bounded assistant contexts.

Examples:
- `maintenance-consumer-handoff/v0`
- `maintenance-reality-pack/v0`

Design rule: **consumers import selected facts; they do not redefine the source-of-truth lanes.**

## What a worthy contribution looks like after this sharpen
The worthy move is not a global health dashboard, abandonment badge, or hidden funding score.

It is a thin `cargo maintenance-reality` / `maintenance-reality-pack/v0` layer that:
1. imports lifecycle and stewardship artifacts rather than replacing them;
2. keeps policy, snapshot, findings, and routing lanes visibly separate;
3. emits bounded public and restricted handoffs;
4. proves at least one real consumer can act on the result honestly; and
5. makes future assistant summaries safer because they can summarize explicit lanes instead of guessing from repo activity.

## First execution order implied by the lane map
1. **Lifecycle + PR triage lane**
2. **Issue intake / repro / prioritization lane**
3. **Release / regression / backport lane**
4. **Explicit help-routing / support-program lane**
5. **Mentoring / intake lane**
6. **Atlas / keystone / assistant consumer lane**

That order matches the strongest official signals: Forge already gives queue-policy structure, current Foundation work gives support-routing urgency, and the survey plus challenge writeups make ecosystem maturity and maintainer support active pressures rather than archive-local theory.

## Non-goals
- one scalar maintainer-health score;
- deriving lifecycle state from commit or queue activity alone;
- a public feed that mixes restricted support asks with public evidence;
- pretending a funding recommendation is the same thing as a maintenance observation;
- or treating recommendation, policy, and keystone consumers as new source-of-truth owners.

## Hygiene rule
Future maintenance / lifecycle / keystone / trust / support revisions should keep **lifecycle intent, workflow policy, observed state, derived pressure findings, help-routing, mentoring capacity, visibility posture, and consumer handoffs** separate.
