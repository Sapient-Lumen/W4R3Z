# Gap: maintenance operations are real infrastructure, but Rust still lacks a portable stewardship substrate

Read this gap with [`design/maintenance-reality-contract-2026Q1.md`](../design/maintenance-reality-contract-2026Q1.md).

## What is missing
Rust has growing evidence that **maintenance is not just “someone eventually fixes bugs.”**
It is operational work:
- triaging regressions,
- keeping review queues moving,
- handling backports and release pressure,
- routing issues to the right people,
- keeping contributor intake and mentoring lanes open,
- and making sure maintenance load is visible before a project quietly stalls.

The Rust Project itself now talks about maintenance and operations in these terms, but most ecosystem crates and teams still lack a portable, reviewable way to publish or govern that work.
What is missing is a shared **stewardship-operations contract** that makes these questions explicit:
- what queues exist,
- what states and aging thresholds they use,
- where work is blocked,
- what help is being requested,
- where a project has single-maintainer or single-reviewer pressure,
- how newcomer-ready work and mentoring lanes are exposed,
- and what maintenance actions actually happened during a period.

Sources:
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- https://blog.rust-lang.org/inside-rust/2025/06/05/a-glance-at-the-team-compiler-operations/
- https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
- https://forge.rust-lang.org/release/triage-procedure.html
- https://blog.rust-lang.org/2025/05/08/gsoc-2025-selected-projects/
- https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The current seam is awkward
Rust increasingly has **pieces** of maintenance infrastructure, but they do not yet compose into a portable ecosystem substrate.
Recent signals sharpen the problem:
- the maintainer-fund design work explicitly asks what maintenance is and frames it as a broad class of labor that keeps the project healthy;
- program-management notes say features attract attention, but without code reviews, fixes, and general maintenance, desired capabilities slow down or stop landing;
- the Compiler Ops writeup makes unusually explicit that review monitoring, triage, meeting organization, documentation upkeep, and process-followthrough are part of the basic machinery that keeps the project rolling;
- infrastructure posts keep improving Triagebot workflows, showing that queue and routing ergonomics are real leverage points rather than incidental admin;
- the triage procedure itself is richly operational, with explicit states, aging thresholds, and reporting expectations;
- GSoC posts show that contributor intake and mentoring capacity are real bottlenecks, not optional niceties;
- and the 2025 survey still shows concern around developer and maintainer support.

What Rust still lacks is a good **portable form** for those truths.
Today they are scattered across:
- GitHub labels,
- ad hoc issue comments,
- Zulip habits,
- project-specific bots,
- meeting notes,
- mentorship spreadsheets,
- and vague community folklore about whether a project is “doing okay.”

That creates recurring failure modes:
- review queues age invisibly until contributors drift away,
- help-seeking only appears as a social plea instead of a consumable artifact,
- newcomer-friendly work is not separated from expert-only maintenance debt,
- lifecycle state gets published without the operational evidence that explains *why* it changed,
- and recommendation or trust layers can see that a crate exists but not whether its stewardship machinery is brittle.

## Why this matters
This is not just a project-internals concern.
A real stewardship-operations substrate would improve:
1. **maintainer sustainability** — review and triage load becomes legible before burnout or abandonment;
2. **contributor retention** — projects can expose newcomer-ready lanes and mentorship capacity in a structured way;
3. **ecosystem navigation** — Atlas-style recommendations can weight operational health instead of only popularity or recency;
4. **lifecycle truth** — lifecycle changes can point to concrete queue pressure, help requests, or succession needs instead of appearing from nowhere;
5. **governance and funding** — support programs can fund or staff the actual operational bottlenecks, not only visible feature work;
6. **release quality** — backport, regression, and blocked-work queues become easier to audit;
7. **LLM/tooling hygiene** — future assistants can summarize operational posture from bounded artifacts instead of guessing from commit activity.

## What “good” looks like
A worthy contribution here is **not** another maintainer leaderboard, productivity dashboard, or issue-count vanity score.
It is a shared stewardship boundary with at least:
- `steward-scope/v0` — what repos, trackers, release lines, and communication lanes are in scope;
- `queue-profile/v0` — the canonical queue states, aging thresholds, escalation policy, and routing rules;
- `queue-snapshot/v0` — a time-bounded operational snapshot of issue / PR / regression / backport / mentoring lanes;
- `review-pressure-report/v0` — where review load, stale work, or single-point-of-failure pressure is accumulating;
- `help-request/v0` — explicit asks for triage, review, backport, release, documentation, or succession help;
- `mentoring-lane/v0` — structured newcomer-ready / mentored / expert-only work categories;
- `steward-action-report/v0` — what triage, routing, escalation, and queue-maintenance work actually happened;
- `steward-pack/v0` — one attachable bundle for registries, Atlas, trust/policy, lifecycle, and project operations.

That would let Rust treat maintenance operations as first-class ecosystem infrastructure instead of leaving them buried in local workflow trivia.
