# Design: Stewardship Pilot Program (`cargo steward pilot`, `steward-pilot-pack/v0`)

## Goal
Make the **Stewardship Ops Kit** real by starting with a ranked, reviewable pilot program instead of trying to model every maintainer workflow in one stroke.

The archive already argues that maintenance operations deserve first-class artifacts. The missing layer is now more practical:
- which stewardship workflows should go first,
- which of them are stable enough to export cleanly,
- how they should interact with support programs and maintainer-fund style decisions,
- and how to keep the kit from collapsing into another public “project health” dashboard.

A worthy contribution here is not just `cargo steward snapshot`. It is a disciplined rollout plan that proves Rust can publish **portable operational truth** for a few high-pressure workflows before widening the schema surface.

That rollout is now also the practical proving ground for [`proposals/epic-maintenance-reality-stack.md`](../proposals/epic-maintenance-reality-stack.md), which turns Lifecycle Ledger + Stewardship Ops into a thin `cargo maintenance-reality` / `maintenance-reality-pack/v0` consumer layer instead of stopping at lower-level exporters. It should also now be read as one proving ground for [`design/stewardship-support-routing-stack.md`](./stewardship-support-routing-stack.md), since explicit support-routing profiles are where maintenance evidence first turns into real intervention choices. Read it together with [`design/maintenance-reality-lane-map.md`](./maintenance-reality-lane-map.md), which now makes the key separation explicit: workflow policy, observed state, derived pressure findings, help-routing, mentoring capacity, and consumer handoffs are distinct lanes, not one maintainer-health bucket.

## References (signals)
- Rust’s maintainer-fund design work says maintenance is broader than bugfixing and asks the project to define what maintenance work actually is.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- The 2025 State of Rust survey still shows concern about developer and maintainer support, and explicitly calls for companies and organizations to help support Rust contributors and crate authors.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The Rust Foundation’s Maintainers Fund announcement says the initiative is meant to provide consistent, transparent, long-term support, including visibility into how funding is used and alignment with Rust Project priorities.
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- The Rust Foundation’s 2026-2028 strategic plan elevates **Sustainable Maintenance** as a core pillar and says Rust needs a well-resourced, well-supported community of people who maintain and support it.
  https://rustfoundation.org/strategic-plan/
- The Foundation’s sustainable-stewardship statement says the infrastructure Rust depends on carries real and rising costs in bandwidth, compute, storage, staff time, and volunteer time.
  https://rustfoundation.org/media/rust-foundation-signs-joint-statement-on-open-source-infrastructure-stewardship/
- The Compiler Ops writeup says teams are moving toward shared process assumptions and calls out regressions, backports, triage, reminders, and documentation/process work as recurring machinery.
  https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
- Triagebot and infrastructure updates keep adding queue-routing ergonomics such as label aliases, which is concrete evidence that stewardship workflow plumbing matters.
  https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
- Rust Forge’s release-triage and issue-triage procedures show that the project already has explicit queue states, aging thresholds, required fields, and report expectations.
  https://forge.rust-lang.org/release/triage-procedure.html
  https://forge.rust-lang.org/release/issue-triaging.html
  https://forge.rust-lang.org/compiler/prioritization.html

## Why this needs its own design layer
The Stewardship Ops Kit already defines the base artifact family: scope, queue profile, queue snapshot, pressure report, help request, mentoring lane, action report, diff report, and pack.

What it did **not** yet answer clearly enough is:
- which workflows deserve to be standardized first,
- where shared semantics already exist versus where local freedom is still too high,
- which consumers justify the work immediately,
- what a minimal “support-routing” integration looks like,
- and when a stewardship pilot should be considered successful.

Without that layer, stewardship work risks two bad outcomes:
1. **schema drift without adoption** — lots of nouns, little real export/use;
2. **dashboard theater** — queue snapshots get published, but nothing actually improves because no explicit consumer, escalation, or support path exists.

## Design principles
1. **Pilot workflows, not abstract maintainership.** Start from concrete operational loops with known labels, states, and reports.
2. **Prefer workflows with existing written procedure.** If Forge/blog posts already describe the process, standardization has a better chance.
3. **Support routing is part of the value.** A pilot should identify who can act on the exported evidence: maintainers, triagers, mentors, release leads, atlas curators, or fund/support programs.
4. **Operational truth is not a public score.** Reports must preserve uncertainty, local semantics, and explicit asks.
5. **Derived findings stay separate from snapshots.** Pressure reports, concentration findings, and continuity-risk notes should never silently rewrite the queue state that produced them.
6. **Mixed public/private posture must be expected.** Some snapshots can be public; some support requests or concentration findings may need restricted sharing.
7. **Service-level budgets should be explicit.** If a workflow uses aging or response thresholds, record them as declared policy, not hidden convention.
8. **Graduation requires a real consumer.** A pilot is not successful just because it renders nicely; some downstream process has to use the artifact.

## Artifact family
### 1. `steward-pilot-brief/v0`
Why this workflow is being piloted.

Should record:
- pilot id and summary
- workflow family (`pr-triage`, `issue-intake`, `release`, `mentoring`, `maintainer-help`)
- why this workflow is high-pressure enough to matter
- why it is tractable now
- intended consumers and action paths

### 2. `workflow-template/v0`
The minimum declared semantics required for a pilot.

Should record:
- queue families in scope
- required states / labels / transitions
- aging and escalation thresholds
- mandatory fields in reports
- local vocabulary that must be preserved verbatim
- unsupported or deferred semantics

### 3. `service-level-budget/v0`
The declared responsiveness/attention model.

Should record:
- expected first-touch or re-touch windows where meaningful
- stale thresholds
- escalation windows
- review / repro / prioritization / backport response expectations
- whether the values are goals, hard rules, or only reporting thresholds

Design rule: **do not smuggle service expectations into prose**.
If the pilot depends on them, make them artifacts.

### 4. `support-routing-profile/v0`
The downstream support map for a pilot.

Should record:
- who can act on the result (`triager`, `reviewer`, `mentor`, `release lead`, `fund program`, `infrastructure`, `community support`)
- what kinds of asks can be published publicly
- what should stay restricted
- how explicit help requests and queue pressure findings route onward
- whether external support/funding can be requested

Design rule: **pressure without routing is just observability**.
The pilot should show how exported evidence can move work or resources.

### 5. `steward-pilot-scorecard/v0`
Decides whether the pilot works.

Should ask:
- did the pilot preserve local semantics honestly?
- did it produce a reusable exporter/report, not just one blog post?
- did a real consumer use it?
- did it avoid collapsing into a scalar health score?
- did it make explicit help-seeking or workload concentration easier to see?
- does widening the pilot still look justified?

### 6. `steward-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- workflow template
- service-level budget
- support-routing profile
- associated stewardship artifacts
- current scorecard
- references and rendered summaries

## Ranked first pilots

### 1) PR status triage for large upstream repos
**Why first**
- Rust Forge already documents status labels, aging thresholds, and required report content for PR triage.
- This is one of the clearest existing stewardship workflows with portable semantics.
- It directly affects throughput, reviewer load, and contributor retention.

**Core artifacts**
- `queue-profile` for waiting states
- `queue-snapshot` by status/age bucket
- `service-level-budget` for 15-day thresholds and monthly blocked checks
- `review-pressure-report`
- `steward-action-report`

**Primary consumers**
- triagers and team leads
- release or compiler ops summaries
- support programs trying to spot review bottlenecks before they become attrition

### 2) Issue intake, repro, and prioritization lanes
**Why second**
- Rust Forge already documents needs-triage, needs-info, needs-repro, MCVE, regression, and prioritization flows.
- This pilot proves the kit can export *actionability* work, not just PR waiting states.
- It is also a good test of newcomer-accessible triage work.

**Core artifacts**
- `workflow-template` for intake labels and checkpoints
- `queue-snapshot` for intake / repro / minimization buckets
- `help-request` for areas needing extra triagers or domain experts
- `mentoring-lane` for newcomer triage contribution
- `steward-diff-report` across weeks or release cycles

**Primary consumers**
- triage volunteers
- compiler prioritization and team-routing processes
- contributor-onboarding surfaces

### 3) Release / regression / backport readiness
**Why third**
- Rust already treats regressions, release blockers, backports, crater checks, and perf runs as structured operational lanes.
- This pilot ties stewardship artifacts to release risk rather than abstract community support.
- It is a strong proving ground for explicit service-level budgets and escalation routing.

**Core artifacts**
- `steward-scope` for branch/release-line identity
- `queue-profile` for release/regr/backport lanes
- `queue-snapshot` and `review-pressure-report`
- `support-routing-profile` linking release leads, infra, perf, crater, and prioritization lanes
- `steward-pack` attachable to release-readiness review

**Primary consumers**
- release team and compiler ops
- lifecycle and support-envelope consumers
- policy/release evidence layers

### 4) Explicit maintainer-help and operational support requests
**Why fourth**
- The Rust Foundation’s Maintainers Fund and strategic plan mean support routing is no longer hypothetical.
- This pilot tests whether explicit asks can be exported cleanly without implying project abandonment.
- It gives Lifecycle Ledger and Atlas something better than repo-activity heuristics.

**Core artifacts**
- `help-request` with urgency/skills/publicity fields
- `support-routing-profile` for volunteer vs funded vs internal escalation paths
- `maintenance-report` import from Lifecycle Ledger when relevant
- `review-pressure-report` or `queue-snapshot` attachments proving the operational need

**Primary consumers**
- maintainers and co-maintainers
- support/funding programs
- atlas/lifecycle/trust consumers looking for declared operational reality

### 5) Mentoring and newcomer-intake lanes
**Why fifth**
- GSoC and community-health signals show mentorship capacity is a real constraint.
- This pilot helps the kit prove it is not only about backlog pressure.
- It makes discoverable, reviewable mentoring promises instead of leaving them in issue comments and sporadic social posts.

**Core artifacts**
- `mentoring-lane`
- `service-level-budget` for expected mentor response windows
- `help-request` when mentor capacity is needed
- `steward-action-report` for intake and follow-through

**Primary consumers**
- newcomers and mentors
- community coordinators
- atlas guidance around projects that are genuinely newcomer-friendly

## What should wait
Do **not** start with “all crates.io maintainers” or a global public ranking site.
Those are downstream views at best, and they would pressure the kit toward oversimplified metrics before the artifact boundaries are proven.

Also avoid starting with deeply bespoke internal workflows that have no written public semantics yet.
The point of the first pilots is to prove common structure where Rust already has process truth.

## Success bar
A stewardship pilot should be considered successful when it can show all of the following:
1. a workflow template that preserves local semantics honestly;
2. at least one exporter/report path that can be rerun;
3. a declared service-level budget or equivalent aging model where relevant;
4. a support-routing profile showing who can act on the output;
5. at least one real consumer (team lead, release process, mentorship process, lifecycle tool, atlas overlay, or support/fund program);
6. no fake scalar “health score” hidden in the rendering.

## Why this is an ecosystem contribution
Rust’s current signals are unusually aligned: formal triage processes exist, compiler and infrastructure teams already invest in queue ergonomics, survey data says maintainer support remains a concern, and the Foundation now has explicit sustainable-maintenance and maintainer-fund language.

That makes stewardship no longer just a soft community topic. It is becoming an **ecosystem substrate** problem: how to turn invisible maintenance operations into bounded, portable truth that real decision-makers can consume.

A good Stewardship Pilot Program would be one of the clearest “outside the box but still practical” contributions in this archive because it would improve how Rust sustains itself, not just how it compiles.
