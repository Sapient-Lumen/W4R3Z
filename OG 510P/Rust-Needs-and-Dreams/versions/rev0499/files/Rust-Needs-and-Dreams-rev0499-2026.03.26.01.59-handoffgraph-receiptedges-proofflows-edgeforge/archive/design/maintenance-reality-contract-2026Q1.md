# Design note: Maintenance Reality Contract (2026Q1)

## Goal
Promote the archive's existing **Maintenance Reality Stack** into an explicit contract boundary between:
- **what a project declares about support, deprecation, succession, and continuity**;
- **what its stewardship machinery actually looks like in operation**; and
- **what Atlas, trust, release, keystone, support-program, and assistant consumers may honestly conclude from those facts**.

Read this with:
- [`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md)
- [`design/maintenance-reality-lane-map.md`](./maintenance-reality-lane-map.md)
- [`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md)
- [`design/stewardship-ops-kit.md`](./stewardship-ops-kit.md)
- [`proposals/epic-maintenance-reality-stack.md`](../proposals/epic-maintenance-reality-stack.md)

This note does **not** argue that Rust needs a universal maintainer-health score.
It argues that Rust increasingly needs a **portable maintenance handoff** that stops forcing lifecycle and stewardship meaning to be reconstructed from issue trackers, labels, sporadic blog posts, private memory, and social inference.

## Why this is the right promotion now
Rust's current signals are unusually aligned around one point: maintenance is now being treated as real infrastructure, but its portable artifacts still lag behind that reality.

The strongest current signals are:
- the Rust Foundation's 2026–2028 strategy names **Sustainable Maintenance** as a core strategic pillar rather than a side concern;
- the Rust Foundation Maintainers Fund announcement says support should be **consistent, transparent, and long term**, developed with Rust Project collaboration and accountability;
- the Inside Rust post **What is maintenance, anyway?** exists because the ecosystem is actively trying to define which maintainer labor should count for funding and support;
- compiler-team operations writing describes regressions, prioritization, routing, review follow-through, and release protection as basic project machinery;
- Rust Forge triage docs already define explicit queue states, thresholds, and routing rules, which means maintenance semantics are not purely tacit anymore;
- infrastructure planning still contains visible unfinished stewardship work such as docs.rs modernization and external-hardware-CI policy work; and
- the 2025 State of Rust survey says online docs remain canonical while LLM/editor mediation rises, which increases the value of bounded maintenance artifacts that assistants can summarize without freelancing from repo activity.

Those signals justify promoting **Maintenance Reality** from a strategic stack into an explicit **contract**.

## The contract layers
### 1) Lifecycle intent
This is the declared side:
- support windows;
- maintained release lines;
- deprecation posture;
- successor relationships;
- co-maintainer / handoff consent;
- “seeking help” versus “winding down” versus “stable and staffed”.

Source of truth: **Lifecycle Ledger**.

### 2) Workflow policy
This is the operational rules side:
- which queues exist;
- what labels and states mean;
- stale thresholds;
- blocked / experimental / needs-repro semantics;
- escalation or service-level budgets;
- mentoring-ready versus expert-only expectations.

Source of truth: **Stewardship Ops**.

### 3) Observed stewardship state
This is the bounded snapshot side:
- what the queues looked like in a period;
- what was aging;
- what had no reviewer or no status;
- what regression or backport pressure existed;
- what actual stewardship actions happened.

Source of truth: **Stewardship Ops exports**, not inferred popularity metrics.

### 4) Derived pressure and continuity findings
This is the analytic side:
- reviewer concentration;
- stale pockets;
- release-readiness pressure;
- continuity risk;
- understaffed intake or mentoring promises;
- succession risk summaries.

Design rule: these findings must stay visibly **derived**, not masquerade as raw state or declared support.

### 5) Explicit help and succession routing
This is the action side:
- review help requests;
- release or backport help requests;
- documentation or triage requests;
- continuity / succession requests;
- volunteer-only versus fund-program versus restricted institutional routing.

Design rule: help must be exportable without being read as abandonment.

### 6) Visibility and consumer handoff
This is the bounded-publication side:
- what is public;
- what is restricted or summarized;
- what Atlas/adoption consumers may import;
- what release/policy/keystone/fund consumers may import;
- what assistants may say without overclaiming.

Design rule: the contract is only useful if it preserves **public versus restricted** truth explicitly.

## What a worthy contribution looks like in practice
A worthy contribution here is a thin **`cargo maintenance-reality` / `maintenance-reality-pack/v0`** layer above the archive's existing Lifecycle Ledger and Stewardship Ops kits.

It should:
- import lifecycle declarations rather than replacing them;
- import stewardship queue policy and snapshots rather than inventing a new hosted workflow;
- emit a `maintenance-reality-brief/v0` that keeps lifecycle, policy, state, pressure, help, and visibility separate;
- emit `maintenance-transition-report/v0` for “what changed since last review?”;
- emit bounded `maintenance-consumer-handoff/v0` slices for Atlas/adoption, release/policy, support-program/fund, keystone, and assistant consumers; and
- make it easy to say **unknown**, **restricted**, or **inconclusive** instead of flattening everything into a health verdict.

The missing artifact family remains intentionally small:
- `maintenance-subject/v0`
- `maintenance-reality-brief/v0`
- `maintenance-transition-report/v0`
- `maintenance-consumer-handoff/v0`
- `maintenance-reality-pack/v0`

## Ranked first execution lanes
1. **lifecycle + PR triage lane**
   - combine declared support posture with real review-queue posture.
2. **issue intake / repro / prioritization lane**
   - prove maintenance reality is not only about PR waiting time.
3. **release / regression / backport lane**
   - prove stewardship imports can affect shipping risk honestly.
4. **help-routing / support-program lane**
   - prove explicit asks and visibility policy survive export.
5. **keystone / Atlas / assistant lane**
   - prove downstream consumers can use thinner views without becoming new truth owners.

## Non-goals
- a public maintainer leaderboard;
- a universal maintainer-health score;
- automated abandonment or ownership-transfer decisions;
- a hidden funding oracle disguised as artifact math;
- or a dashboard that flattens private and public maintenance evidence together.

## Archive fit refresh
This promotion should **not** rewrite the broad ladder.
The archive still most urgently needs build-state truth, adoption navigation, and stronger build/debug control planes.

What changes here is that **Maintenance Reality Contract** is now the clearest explicit **stewardship / continuity / support-routing** seam:
- adjacent to **Publisher & Source Identity Contract**, **Distribution Contract**, and **Consumer Lifecycle Continuity Bundle**;
- downstream from lifecycle declarations and stewardship exports;
- upstream of Atlas/adoption, trust/policy, release/governance, keystone stewardship, and fund/support consumers.

That makes it a strategically worthy contribution precisely because it helps later layers stop guessing.
