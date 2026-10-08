# Pathfinder review-packet workflows — 2026-03-24

This note deepens **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** around the next missing implementation layer:
**receiver workflows**.

The archive already had good material for:
- lane catalogs,
- candidate import,
- evidence origin,
- elimination / re-entry,
- replay / timebox,
- and starter-set readiness.

What it still lacked was one practical answer to:

> What exact packet should `cargo pathfinder` hand different people on day one?

## Main judgment

A credible `0.1` should not stop at “generate a decision pack.”
It should ship **receiver-specific review packets** that match real Rust workflows.

At minimum, `cargo pathfinder` should support four workflows.

## Workflow 1 — selection under time pressure

Audience:
- staff engineer, team lead, consultant, or experienced maintainer choosing a starter stack.

Packet:
- `decision-brief.md`
- `starter-set.bundle.json`
- `candidate-elimination.receipt.json`
- `adoption-checklist.md`

What the crate should provide other people:
- one short answer to “use this starter set first, here is why, and here is what we intentionally left out.”

CLI shape:
- `cargo pathfinder review --lane async_backend_stack`
- `cargo pathfinder brief --lane desktop_gui_stack`

## Workflow 2 — architecture / ADR review

Audience:
- reviewer, approver, principal engineer, platform committee.

Packet:
- `decision-brief.md`
- `manual-review.note.md`
- `role-coverage.report.json`
- `candidate-reentry.policy.json`

What the crate should provide other people:
- one compact review packet that names tradeoffs, missing roles, and what evidence would justify reopening the decision.

CLI shape:
- `cargo pathfinder packet --for adr`
- `cargo pathfinder review --include manual-review`

## Workflow 3 — pre-merge / CI drift watch

Audience:
- CI maintainer, dependency owner, tool/assistant importing watch signals.

Packet:
- `decision-watch.report.json`
- `revisit-trigger.policy.json`
- `freshness-window.policy.json`
- optional `decision-delta.report.json`

What the crate should provide other people:
- one answer to “should we re-open this frozen choice or keep the current starter set?”

CLI shape:
- `cargo pathfinder watch --frozen starter-set.lock`
- `cargo pathfinder delta --as-of current`

## Workflow 4 — scheduled re-evaluation

Audience:
- long-lived team, regulated adopter, enterprise platform group.

Packet:
- `as-of-replay.report.json`
- `candidate-import.report.json`
- `candidate-reentry.policy.json`
- `manual-review.note.md`

What the crate should provide other people:
- one replay packet that makes it safe to ask “has anything changed enough to justify re-evaluating our stack?”

CLI shape:
- `cargo pathfinder replay --from starter-set.lock`
- `cargo pathfinder reconsider --policy revisit-trigger.policy.json`

## Recommended first packet family

A good `0.1` should ship this exact compact family before it expands into dashboards or recommendation UIs:

1. `decision-brief.md`
2. `starter-set.bundle.json`
3. `candidate-elimination.receipt.json`
4. `manual-review.note.md`
5. `revisit-trigger.policy.json`
6. `adoption-checklist.md`

Why this family:
- it serves humans and tools,
- it covers first choice and later drift,
- and it remains small enough to review.

## Scenario families that most need these packets next

1. `desktop_gui_stack`
2. `wasm_component_plugin_stack`
3. `mixed_language_interop_stack`
4. `local_first_sync_stack`
5. `safety_critical_boundary_stack`
6. `air_gapped_enterprise_stack`
7. `robotics_control_vs_ops_stack`
8. `data_lakehouse_open_table_stack`

## Guardrails

### Do not confuse search with decision authority
`cargo search`, crates.io, docs.rs, and security tabs are inputs, not verdicts.

### Do not flatten teaching, shipping, and regulated defaults together
Those are different packets and sometimes different answers.

### Do not hide manual-review triggers
If the lane depends on native prerequisites, target quirks, debugger posture, or certification evidence, the packet should say so explicitly.

### Do not overfit to “best crate” language
A worthy packet tells another person which answer fits a frozen task profile.
It does not pretend to settle the ecosystem forever.
