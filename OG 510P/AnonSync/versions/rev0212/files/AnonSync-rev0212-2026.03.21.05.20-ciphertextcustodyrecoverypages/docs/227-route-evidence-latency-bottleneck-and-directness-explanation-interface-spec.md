# Route evidence, latency, bottleneck, and directness explanation interface spec

## Purpose

The archive already had transfer-policy and route-cost doctrine.
What it still lacked was one stricter interface contract for the operator question that shows up whenever syncing feels wrong:

> why is this transfer slow *right now*, is it direct or relayed, what else is constraining it, and where can I see one honest answer without reading three help pages?

Current Resilio docs still make this seam concrete.
They still say direct connections are significantly faster than relayed ones, that relay use is separately signaled by a peer-list icon, that performance graphs show per-peer upload/download speed, RTT, protocol, and disk queue, and that speed troubleshooting can still send the operator through LAN-only guidance, predefined hosts, local-peer rate-limit exceptions, and encryption toggles.

Those are useful diagnostics.
They are still not one explanation surface.

## Core decision

AnonSync should provide one **Transfer explanation** pane that merges:

- selected route class
- directness status
- current latency and disk pressure
- active caps or fairness budgets
- practical next actions

The operator should never have to cross-reference:

- a peer icon
- a graph
- a preferences page
- a support article

just to answer whether the transfer is slow because it is relayed, capped, delayed, or disk-bound.

## Why this matters

Current Resilio behavior still spreads one explanation across several surfaces:

- relay/direct class appears in peer status
- speed and RTT appear in performance graphs
- route prerequisites live in ports/protocols help
- improvement advice points toward LAN policy, predefined hosts, rate-limit exceptions, and encryption knobs

AnonSync should therefore keep one stronger rule:

> every slow or suspicious transfer should render a single human explanation before it renders advanced knobs.

## Fixed explanation order

Every transfer explanation should render the same sections in the same order:

1. **Current route**
2. **Observed bottleneck**
3. **Policy and budget constraints**
4. **Practical next actions**
5. **Receipt / evidence handle**

### 1) Current route

Show:

- selected route class (`lan-direct`, `known-host-direct`, `overlay`, `public-direct`, `relay`)
- current directness grade
- selected transport kind
- peer or seat pair involved
- last-known fallback reason if not direct

### 2) Observed bottleneck

Show the dominant current reason, such as:

- `relay path in use`
- `high latency`
- `disk queue pressure`
- `rate cap active`
- `fairness hold`
- `source unavailable`
- `policy-delayed`
- `insufficient evidence`

A single primary explanation must appear first, with secondary contributing factors listed underneath.

### 3) Policy and budget constraints

Show:

- active throughput caps
- fairness or lane rules
- any relay discouragement or cost budget
- LAN-only or known-host restrictions
- encryption/performance posture if it materially changes cost

### 4) Practical next actions

Good next actions include:

- `Inspect route candidates`
- `Open peer reachability review`
- `Temporarily widen allowed directness`
- `Lower relay cost posture`
- `Review bandwidth caps`
- `Review disk pressure`
- `Keep current posture and explain why`

### 5) Receipt / evidence handle

Every explanation pane should be deep-linkable and exportable as evidence.
The receipt must preserve:

- route chosen
- bottleneck summary
- active budgets
- latency / queue snapshot
- recommended next action shown at the time

## Main surface

Each live subject and each peer-transfer row should have a stable **Why this transfer looks this way** affordance.

The pane should open with one sentence such as:

- `This transfer is slower because it is relayed; direct path was not available.`
- `This transfer is direct, but disk queue pressure is now the main bottleneck.`
- `This transfer is route-eligible for LAN direct, but policy is currently capping local peers.`

## Object model implications

### Route evidence snapshot

Fields:

- `route_evidence_snapshot_id`
- `transfer_ref`
- `selected_route_class`
- `selected_transport_kind`
- `relay_in_use` boolean
- `latency_ms`
- `disk_queue_depth`
- `throughput_now`
- `captured_at`

### Bottleneck explanation

Fields:

- `bottleneck_explanation_id`
- `transfer_ref`
- `primary_bottleneck_kind`
- `secondary_bottleneck_kinds[]`
- `policy_refs[]`
- `budget_refs[]`
- `human_summary`
- `recommended_actions[]`

### Transfer explanation receipt

Fields:

- `transfer_explanation_receipt_id`
- `transfer_ref`
- `route_evidence_snapshot_ref`
- `bottleneck_explanation_ref`
- `policy_refs[]`
- `captured_at`

## Explicit non-goals

AnonSync should not:

- force the operator to infer relay/direct class from icons alone
- show RTT and queue graphs without turning them into an explanation
- bury the slow path cause behind advanced network settings
- present tuning options before stating the current bottleneck honestly

## Relationship to nearby specs

This spec is the interface-facing companion to:

- `53-transfer-policy-and-throughput-budget-spec.md`
- `217-discovery-bootstrap-catalog-outage-and-fallback-authority-interface-spec.md`
- `218-egress-only-proxy-and-relay-inevitability-interface-spec.md`

Those documents define route and budget doctrine.
This one fixes the everyday explanatory surface for a transfer that feels wrong.
