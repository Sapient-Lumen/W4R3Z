# Epic Proposal: Stewardship Ops Kit (`cargo steward`, `steward-pack/v0`)

## One-sentence pitch
Make Rust maintenance operations — queue states, review pressure, help requests, mentoring lanes, and stewardship actions — first-class artifacts so projects can govern and communicate operational reality without relying on folklore, issue-count theater, or bespoke internal dashboards.

## Deliverables
- `cargo steward` reference tool
- Schemas:
  - `steward-scope/v0`
  - `queue-profile/v0`
  - `queue-snapshot/v0`
  - `review-pressure-report/v0`
  - `help-request/v0`
  - `mentoring-lane/v0`
  - `steward-action-report/v0`
  - `steward-diff-report/v0`
  - `steward-pack/v0`
- Adapters / integrations for:
  - GitHub issue / PR labels and searches
  - triagebot-driven workflows
  - release / backport queues
  - project mentoring entrypoints
  - Lifecycle Ledger, Atlas, Trust Signals, and Policy consumers
- Docs:
  - queue semantics guidance
  - help-request publication guidance
  - mentoring-lane guidance
  - “declared workflow vs observed pressure” semantics
  - ranked stewardship pilot-program guidance

## Why now (signals)
- The maintainer-fund design work asks what maintenance is and frames it as broad, critical labor instead of a thin synonym for bugfixing.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- Program-management notes explicitly say that without code reviews, fixes, and general maintenance, desired capabilities become slow to impossible to land.
  https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- The Compiler Ops writeup says review monitoring, triage, reminders, meeting organization, documentation, and process-followthrough are part of the basic machinery that keeps the project rolling.
  https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
- Infrastructure posts keep extending Triagebot with queue-routing and backport-flow improvements, which is strong evidence that operational ergonomics matter.
  https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
- The release triage procedure shows Rust already has mature state/aging/reporting conventions for queue work.
  https://forge.rust-lang.org/release/triage-procedure.html
- GSoC posts show contributor intake is constrained by mentor time and capacity, and that the pipeline works when structured support exists.
  https://blog.rust-lang.org/2025/05/08/gsoc-2025-selected-projects/
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- The 2025 survey still flags developer and maintainer support as a concern.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The Rust Foundation’s 2026–2028 strategy makes Sustainable Maintenance a core pillar, which is strong evidence that better maintenance operations are now strategic Rust infrastructure.
  https://rustfoundation.org/strategic-plan/
- The Foundation’s 2025 annual report says it invested materially in full-time Rust maintenance work, which makes explicit support-routing and evidence consumers more plausible than they looked a year ago.
  https://rustfoundation.org/media/annual-report-strategy-2025/
- Cargo’s plugin stance suggests a companion-kit posture is appropriate here.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## Non-goals
- One universal maintainer productivity score
- Mandatory public dashboards for every crate
- Replacing GitHub, Zulip, or Triagebot
- Declaring projects “healthy” or “unhealthy” from counts alone
- Using queue pressure as an automatic ownership-transfer trigger

## Strategic value
This is a worthy contribution because it upgrades invisible coordination work into reusable infrastructure.

It unlocks:
- earlier visibility into review and triage bottlenecks,
- structured publishing of help requests and mentoring capacity,
- better lifecycle explanations when a crate needs succession or extra help,
- better Atlas guidance that can weight operational health,
- stronger maintainer-fund and governance decisions,
- and more bounded tool / assistant outputs about project stewardship.

The archive already has Lifecycle Ledger for declared state.
Stewardship Ops fills the missing **live operational substrate** beneath it.
See also [`design/maintenance-reality-stack.md`](../design/maintenance-reality-stack.md) for the archive-level composition note that keeps declared lifecycle, observed queue state, and support-routing policy distinct.

## Proposed shape
Ship a narrow but composable reference stack:
1. schemas for scope, queue policy, snapshots, pressure, help requests, mentoring lanes, actions, diffs, and packs;
2. one GitHub-native exporter using labels / searches / config;
3. one triagebot-aware adapter proving Rust-forge-style workflows can be exported cleanly;
4. one maintainer-help publishing flow with support-routing semantics;
5. one Atlas consumer and one Lifecycle Ledger consumer proving cross-kit value;
6. one ranked pilot-program layer proving which workflows should go first.

## Milestones
### Milestone 1: Queue core
- publish `steward-scope`, `queue-profile`, `queue-snapshot`
- support one real GitHub-native workflow
- generate human-readable and machine-readable reports

### Milestone 2: Pressure + help
- add `review-pressure-report` and `help-request`
- prove that explicit asks are more useful than issue-count heuristics
- add one maintainer-facing report view and one external consumer view

### Milestone 3: Mentoring + diffs
- add `mentoring-lane` and `steward-diff-report`
- support newcomer-ready and mentored queues explicitly
- show drift across releases or quarters

### Milestone 4: Pilot program + cross-kit adoption
- publish a ranked stewardship pilot program for PR triage, issue intake, release/backport readiness, maintainer-help routing, and mentoring lanes
- Atlas weights stewardship inputs
- Lifecycle Ledger references stewardship evidence during help / handoff / succession phases
- support-program or fund-style consumers can ingest the same artifacts

## Success metrics
- Projects can publish explicit help requests without improvised social posts.
- Review / triage pressure becomes easier to spot before contributors disappear.
- Newcomer-ready and mentored lanes become discoverable and auditable.
- Atlas recommendations stop confusing popularity with stewardability.
- Lifecycle state changes can cite operational evidence.
- The kit remains explainable and avoids collapsing into one fake “project health” number.

## Archive fit
This proposal should sit near:
- **Lifecycle Ledger Kit** — declared lifecycle state and succession
- **Trust Signals Kit** — trust imports selected stewardship signals
- **Policy Kit** — org policy may care about unresolved operational pressure
- **Ecosystem Atlas Kit** — recommendations should weight operational reality
- **Release Pipeline Kit** — release readiness depends on queue and backport posture
- **Support Envelope Kit** — support claims and operational capacity often interact

What none of those owns is the portable representation of **maintenance operations themselves**.
That is why this can be an epic contribution: it would make Rust better at sustaining its own ecosystem, not just growing it.
