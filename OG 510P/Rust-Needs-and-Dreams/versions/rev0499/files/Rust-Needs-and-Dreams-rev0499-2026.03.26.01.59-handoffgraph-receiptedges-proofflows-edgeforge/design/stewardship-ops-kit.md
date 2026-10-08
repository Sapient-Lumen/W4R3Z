# Design: Stewardship Ops Kit (`cargo steward`, `steward-pack/v0`)

## Goal
Define a portable contract for **maintenance operations**: queue states, aging thresholds, review pressure, help requests, mentoring lanes, and action reports that make stewardship work legible and governable.

This should **not** replace project-specific bots, GitHub labels, Zulip norms, or lifecycle metadata.
It should make them compose better and stop forcing maintainers to communicate operational reality through scattered social signals.

See also [`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md) for the archive-level division of labor between declared lifecycle state and live stewardship evidence.

## References (signals)
- Rust’s maintainer-fund design work explicitly asks what maintenance is and frames it as critical, broad, often invisible labor.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- Program-management updates say features attract funding attention, but without code reviews, fixes, and general maintenance, desired capabilities become slow to impossible to land.
  https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- The Compiler Ops writeup explicitly treats triage, review monitoring, meeting organization, process followthrough, tooling, and documentation as the basic machinery that keeps the project rolling.
  https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
- Infrastructure updates keep improving Triagebot workflows such as label aliases and backport suggestion lanes, showing that queue-routing ergonomics are real leverage points.
  https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
- The release triage procedure documents explicit state labels, aging thresholds, and reporting expectations, which is exactly the kind of operational truth that should be portable.
  https://forge.rust-lang.org/release/triage-procedure.html
- GSoC posts show newcomer intake and mentorship capacity are real constraints, not decorative community work.
  https://blog.rust-lang.org/2025/05/08/gsoc-2025-selected-projects/
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- The 2025 State of Rust survey still records concern about developer and maintainer support.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The Rust Foundation’s 2026–2028 strategy elevates **Sustainable Maintenance** to a core pillar, which is unusually strong evidence that stewardship work is now ecosystem infrastructure rather than background social glue.
  https://rustfoundation.org/strategic-plan/
- The Foundation’s 2025 annual report says it invested materially in full-time Rust maintenance work, which strengthens the case for reviewable maintenance evidence and explicit support routing.
  https://rustfoundation.org/media/annual-report-strategy-2025/
- Cargo’s own 1.93 notes stress that Cargo cannot be everything to everyone and that plugins matter, which supports a companion-kit posture rather than assuming this all belongs in core Cargo.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## Core components

### 1) `steward-scope/v0`
The canonical identity and scope of a stewardship surface.

Should record:
- project / org / crate / workspace identity
- repo and tracker identity
- release lines or branches in scope
- whether the scope covers issues, PRs, regressions, backports, docs, mentoring, or release operations
- communication lanes (GitHub, Zulip, Discord, mailing list, etc.)
- update cadence and snapshot period

Design rule: **scope must be explicit**.
Do not pretend one queue snapshot covers every workflow a project runs.

### 2) `queue-profile/v0`
The declared operational model.

Should record:
- queue families (`issue`, `pr`, `regression`, `backport`, `release`, `docs`, `mentoring`)
- allowed states and labels
- aging thresholds and escalation thresholds
- routing rules and ownership expectations
- stale / blocked / experimental / newcomer-ready distinctions
- reason codes for state transitions

Design rule: **queue semantics are policy, not inference**.
This artifact says what the workflow *means*.

### 3) `queue-snapshot/v0`
A time-bounded operational snapshot.

Should record:
- subject scope + timestamp window
- item counts by queue/state
- aging buckets
- blocked/stalled counts
- unassigned / unrouted counts
- no-status / no-owner findings
- release-critical and regression-critical subsets when relevant

Design rule: **snapshots are observations, not verdicts**.
Counts alone are not health scores.

### 4) `review-pressure-report/v0`
Derived evidence about maintenance load.

Should record:
- review backlog pressure
- stale PR pressure
- reviewer concentration / single-point-of-failure findings
- untriaged regression pressure
- documentation or release queue pressure where modeled
- reason-coded hot spots

Design rule: **pressure reports must stay explainable**.
No opaque “maintainer health number.”

### 5) `help-request/v0`
Explicit asks for operational support.

Should record:
- request class (`triage`, `review`, `backport`, `release`, `docs`, `mentoring`, `co-maintainer`, `succession`)
- urgency and expiry
- prerequisites / skills needed
- contact path
- whether funding, sponsorship, or volunteer help is being sought
- whether the request is public or restricted

Design rule: **help-seeking must be publishable without implying abdication**.
A project can need help while still being healthy.

### 6) `mentoring-lane/v0`
A structured contributor-intake surface.

Should record:
- issue / task classes intended for newcomers
- mentorship availability or capacity
- expected response time
- skill prerequisites
- whether tasks are mentored, lightly-guided, or expert-only
- handoff or follow-up expectations

Design rule: **newcomer work should be discoverable without being fake-easy**.

### 7) `steward-action-report/v0`
Portable evidence that maintenance operations actually happened.

Should record:
- time window
- triage actions taken
- reminders or routing actions sent
- labels / state changes applied
- backport / regression / release actions performed
- mentoring and contributor-intake actions performed
- meeting / report generation links if relevant
- provenance (`manual`, `bot-assisted`, `mixed`)

Design rule: **maintenance operations should be visible without becoming performative theater**.

### 8) `steward-diff-report/v0`
Drift between two operational states.

Should capture:
- queue growth or shrinkage by state
- aging-bucket changes
- newly blocked or newly cleared hot spots
- newly posted or resolved help requests
- mentoring-capacity changes
- reviewer concentration drift

Design rule: operational changes should be reviewable like API, support, or lifecycle drift.

### 9) `steward-pack/v0`
Bundle format containing:
- `steward-scope/v0`
- optional `queue-profile/v0`
- optional `queue-snapshot/v0`
- optional `review-pressure-report/v0`
- optional `help-request/v0`
- optional `mentoring-lane/v0`
- optional `steward-action-report/v0`
- optional `steward-diff-report/v0`
- raw references / exports where needed

This is the unit that should travel through atlas overlays, maintainer-fund workflows, lifecycle tooling, and project archaeology.

### 10) `cargo steward`
Reference UX:
- `cargo steward init`
- `cargo steward profile`
- `cargo steward snapshot`
- `cargo steward pressure`
- `cargo steward help`
- `cargo steward report`
- `cargo steward diff`
- `cargo steward pack`

`cargo steward` should begin as a metadata + export + reporting adapter above existing forges and bots.
It should **not** begin as a mandatory hosted platform.

## Default policy
- **Separate declared workflow policy from observed queue state.**
- **Keep pressure reports reason-coded and explainable.**
- **Treat help requests as first-class artifacts.**
- **Make mentoring capacity explicit.**
- **Reward queue stewardship without turning it into vanity metrics.**

## What the kit should provide to others
- **Lifecycle Ledger Kit:** consume explicit operational evidence when lifecycle state changes or help is requested.
- **Ecosystem Atlas Kit:** weight active stewardship posture, mentoring openness, and queue reality instead of only popularity or release recency.
- **Trust Signals Kit:** import selected operational evidence as one dimension of trust without owning the schema.
- **Policy Kit:** gate on stale review pressure or unresolved release-critical queue states where organizations care.
- **Maintenance Reality Stack:** pair lifecycle declarations with live operational evidence without collapsing them into one health score.
- **Release Pipeline Kit:** connect backport / regression / blocked-work queues to release readiness.
- **Support programs / maintainer funds:** see where operational load actually accumulates.

## Overlap boundaries
- **Not Lifecycle Ledger Kit:** lifecycle owns support windows, deprecation, succession, and declared status. Stewardship Ops owns live operational load and queue mechanics.
- **Not Trust Signals Kit:** trust aggregates multiple assurance dimensions; stewardship remains its own source-of-truth layer.
- **Not Issue tracker replacement:** GitHub / Zulip / triagebot remain the execution environment.
- **Not a ranking site:** the point is portable artifacts and explainable posture, not public gamification.
- **Not a universal workflow mandate:** teams can have different queue models; the kit standardizes how they are declared and exported.

## Hard problems (explicitly scoped)
1. **Normalization versus local freedom**
   - Teams need local workflow vocabulary, but exported artifacts need enough shared shape to compare meaningfully.
2. **Operational privacy**
   - Some help requests or pressure findings may be public, some restricted.
3. **Avoiding score-theater**
   - The kit must resist collapsing into “X open issues = bad.”
4. **Low-friction adoption**
   - Projects will not adopt a giant process rewrite just to publish snapshots.
5. **Cross-tool integration**
   - GitHub labels, Zulip topics, Triagebot commands, and release docs all expose different kinds of truth.

## Minimal adoption path
1. Publish `steward-scope/v0`, `queue-profile/v0`, and `queue-snapshot/v0` with lightweight exporters.
2. Ship `cargo steward snapshot` and `cargo steward report` for one GitHub-native workflow.
3. Add `review-pressure-report/v0` and `help-request/v0`.
4. Add `mentoring-lane/v0` and diff support.
5. Pilot consumers in Atlas, Lifecycle Ledger, release workflows, and support-program dashboards.

See [`design/stewardship-pilot-program.md`](./stewardship-pilot-program.md) for the ranked rollout plan. The next credible move is not to widen the ontology indefinitely; it is to prove a few high-pressure workflows with explicit service-level budgets and support-routing profiles.

## Why this is an ecosystem contribution
Rust now has increasingly explicit evidence that operations work is fundamental: review queues, triage, routing, mentoring, and process followthrough are not secondary to the language — they are part of why the language and ecosystem continue to ship.

A good Stewardship Ops Kit would turn that reality into reusable infrastructure.
It would not replace people.
It would make their bottlenecks legible enough to support better tools, better funding, better navigation, and better continuity.
