# Design note: Maintenance Reality Stack (Lifecycle Ledger + Stewardship Ops)

Read this stack through [`design/maintenance-reality-contract-2026Q1.md`](./maintenance-reality-contract-2026Q1.md).
That note is now the archive's explicit statement of the maintenance boundary; this stack note remains the composition map beneath it.

## Goal
Define the **division of labor and consumer flow** between declared lifecycle state and live stewardship operations so Rust can treat maintenance as real ecosystem infrastructure without collapsing everything into one fake health score.

This note is now sharpened by [`design/maintenance-reality-lane-map.md`](./maintenance-reality-lane-map.md).
Read that file as the concrete rule for what must stay separate.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose:
- [`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md)
- [`design/stewardship-ops-kit.md`](./stewardship-ops-kit.md)
- [`design/stewardship-pilot-program.md`](./stewardship-pilot-program.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/ecosystem-atlas-kit.md`](./ecosystem-atlas-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/keystone-stewardship-stack.md`](./keystone-stewardship-stack.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “maintenance matters in principle.”
They are saying maintenance is now a **strategic, fundable, operational concern**:
- the Rust Foundation’s 2026–2028 strategy names **Sustainable Maintenance** as a core pillar;
- the Maintainers Fund announcement frames long-term support for maintainers as essential to Rust’s future and says the work should be done openly and with accountability;
- the Foundation’s January 2026 strategy/annual-report post says it invested materially in full-time Rust maintenance work in 2025;
- the maintainer-fund design note says maintenance is hard to demonstrate precisely because success often looks like continued stability;
- Compiler Ops and Infrastructure posts describe review routing, stale-queue handling, and ownership repair as project machinery rather than invisible volunteer glue;
- Forge procedures already encode status labels, aging thresholds, and prioritization flows, which means maintenance operations have enough shared shape to export honestly; and
- Cargo’s current plugin stance is still a reminder that companion tools are appropriate when Cargo itself cannot be everything to everyone.

Together these signals justify treating maintenance reality as a **frontier-worthy ecosystem seam** rather than a soft social afterthought.

## Stack layers

### 1) Lifecycle Ledger: declared maintainer intent
Lifecycle Ledger owns the **declared state** of a crate or project:
- support windows
- deprecation and successor relationships
- handoff / co-maintainer consent
- declared maintenance posture
- lifecycle diffs across releases or periods

Lifecycle answers questions like:
- “Is this crate still supported?”
- “Which version lines are maintained?”
- “Is a successor verified?”
- “Is the project explicitly seeking a co-maintainer or handoff?”

Design rule: **declared lifecycle intent must not be inferred from queue pressure alone.**

### 2) Stewardship Ops: workflow policy + observed operations
Stewardship Ops owns the **live operating picture** of maintenance work, but the new lane map now makes two parts explicit:
- **workflow policy** — queue semantics, label meanings, thresholds, escalation budgets, routing rules;
- **observed operations** — queue snapshots, action logs, release/backport state, mentoring intake state, explicit help requests.

Stewardship answers questions like:
- “Where is review pressure accumulating?”
- “Which queues are aging out?”
- “Does this project need more triagers, reviewers, or release help?”
- “Are newcomer-intake promises actually staffed?”

Design rule: **declared policy, observed state, and derived pressure findings must not silently collapse into one another.**

### 3) Support-routing and visibility policy
Some maintenance reality can be published broadly; some should stay restricted.

This layer decides:
- which queue snapshots are public versus internal;
- whether a help request is public, private, or fund-program-only;
- whether reviewer-concentration or burnout-adjacent findings should be summarized rather than exposed raw;
- which consumers can act on the evidence.

Design rule: **pressure without routing is just observability, but routing without visibility policy can become coercive or invasive.**

### 4) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Atlas** can weight operational clarity and mentoring posture without pretending popularity equals maintainability.
- **Policy** can gate on explicit lifecycle or release-readiness conditions without inventing a universal health score.
- **Release Pipeline** can attach stewardship evidence to release readiness and backport posture.
- **Trust Signals / Trust Decision** can import selected maintenance facts as one dimension among many.
- **Keystone stewardship** can distinguish ordinary stewardship strain from institutional-support obligations.
- **Support programs / maintainer funds** can route help or funding using explicit asks and evidence instead of social-media archaeology.
- **Bounded assistants** can summarize public maintenance posture from explicit artifacts instead of guessing from commit activity.

Design rule: **consumers import selected evidence; they do not redefine the source-of-truth schemas.**

## What an epic contribution should look like in practice
A worthy contribution here is not “build the world’s maintainer dashboard.”
It is a portable, reviewable stack with clear boundaries:

1. **Lifecycle first**
   - publish `lifecycle-intent`, `support-window-map`, `handoff-consent`, and `lifecycle-report` cleanly;
2. **Stewardship core second**
   - export queue policy, queue snapshots, pressure findings, and help requests for one real workflow;
3. **Routing third**
   - add explicit visibility posture and public-versus-restricted consumer handoffs;
4. **Consumer proof fourth**
   - prove one Atlas/policy/release/support-program/keystone consumer can use the data honestly;
5. **Only then consider wider aggregation**
   - cross-project views should remain overlays, not the canonical truth.

That proposal shape is now explicit in [`proposals/epic-maintenance-reality-stack.md`](../proposals/epic-maintenance-reality-stack.md): a thin `cargo maintenance-reality` / `maintenance-reality-pack/v0` composition layer above Lifecycle Ledger + Stewardship Ops rather than a global dashboard, hidden fund allocator, or abandoned-project badge system.

## Proposed stack-facing artifact family
The lower kits should keep owning their native artifacts. The stack layer should stay thin and consumer-facing:
- `maintenance-subject/v0` — the crate/workspace/project/org lane being reviewed;
- `maintenance-reality-brief/v0` — declared lifecycle + workflow policy + observed stewardship + derived findings + visibility posture + explicit unknowns;
- `maintenance-transition-report/v0` — what changed since the last review;
- `maintenance-consumer-handoff/v0` — bounded summaries for Atlas/adoption, release/policy, fund/support, keystone, or assistant consumers;
- `maintenance-reality-pack/v0` — the linked bundle.

Design rule: **the stack should import lifecycle and stewardship artifacts; it should not replace them.**

## Ranked first execution lanes
1. **PR triage / stale-review lane**
   - best first exporter because Forge already documents label meaning and aging thresholds.
2. **Issue intake / repro / prioritization lane**
   - proves the stack can model actionability and newcomer triage work, not only reviewer waiting time.
3. **Release / regression / backport readiness lane**
   - ties maintenance operations directly to shipping risk and release governance.
4. **Maintainer-help routing lane**
   - exports explicit asks with urgency, skills needed, visibility policy, and public-versus-restricted routing.
5. **Mentoring / newcomer intake lane**
   - makes mentor capacity and follow-through visible without pretending every tagged issue is truly newcomer-ready.
6. **Atlas / keystone / assistant consumer lane**
   - proves the stack can yield thin, honest downstream summaries after the evidence exists.

## Non-goals
- one scalar maintainer-health score;
- automatic ownership-transfer decisions from queue pressure;
- a universal hosted dashboard as the primary artifact;
- flattening public lifecycle metadata and restricted support requests into one public feed;
- treating lack of queue activity as proof of health or abandonment.

## Archive implications
- The archive should now treat **Lifecycle Ledger + Stewardship Ops** as a coupled **Maintenance Reality Stack** whose concrete lane boundaries live in [`design/maintenance-reality-lane-map.md`](./maintenance-reality-lane-map.md).
- Future revisions should prefer **lane-aware stewardship pilots, explicit visibility policy, support-routing profiles, and consumer proofs** over more vague talk about sustainability.
- When Policy, Atlas, Release Pipeline, Trust Decision, Keystone, or Foundation/support-program ideas cite maintenance reality, they should import **declared lifecycle state**, **workflow policy**, **observed state**, and **derived pressure findings** separately.

## References (signals)
- Rust Foundation strategic plan (2026–2028):
  https://rustfoundation.org/strategic-plan/
- Rust Foundation Maintainers Fund announcement:
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- Rust Foundation 2025 annual report / 2026 strategy summary:
  https://rustfoundation.org/media/annual-report-strategy-2025/
- What is maintenance, anyway?
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- A glance at compiler team operations:
  https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
- Infrastructure Team 2025 Q4 recap and Q1 2026 plan:
  https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- What we heard about Rust’s challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Cargo development cycle 1.94:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Rust Forge triage procedure / issue triaging / prioritization:
  https://forge.rust-lang.org/release/triage-procedure.html
  https://forge.rust-lang.org/release/issue-triaging.html
  https://forge.rust-lang.org/compiler/prioritization.html
