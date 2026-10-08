# Transfer policy, throughput budget, and route-cost explanation spec

## Why this deserves its own layer

The archive already had route policy, route leases, transport runtimes, activity phases, and basic transfer objects.
What it still lacked was a full public contract for the operator question that appears as soon as a transfer feels slow, unfair, or mysteriously routed:

> why is this transfer using *this* path, at *this* speed, with *this* queue behavior, under *which* policy right now?

Resilio's current docs still answer that question through a scatter of separate surfaces and support rituals:

- direct connections are described as much faster than relayed ones, while relay use is shown as a separate per-peer icon and article rather than one integrated transfer explanation
- general bandwidth limits apply only to Internet connections unless `rate_limit_local_peers` is changed in power-user preferences
- LAN-only operation requires a mix of share settings, power-user settings, LAN discovery behavior, and even cache-expiration ritual if a global IP was learned previously
- speed advice also points operators toward `lan_encrypt_data`, static/predefined hosts, disk priority, and fragmentation rather than one coherent transfer-budget surface
- power-user preferences expose protocol forcing, interface binding, tracker/relay defaults, queue priority, keep-expired-transfer retention, piece-size behavior, and other performance-significant knobs in one long table
- newer file-download priority behavior can suspend lower-priority downloads, rebuild large queues, degrade performance on large changing datasets, and still render alphabetically in UI even when priority order differs
- per-extension delay behavior lives in a storage-folder JSON file instead of one explicit operator-facing policy surface
- performance graphs show per-peer speeds, RTT, protocol, and disk load, but they still leave policy, budget, and queue causality partly implicit

Those features are individually useful.
Together, they still scatter one important truth:

- which route classes are allowed
- which route class actually won
- which budgets are currently constraining throughput
- which transfers are waiting because of fairness, priority, delay, or source absence
- whether current behavior is durable policy or only a temporary window

AnonSync should not clone that shape.
The product should expose one public model for transfer policy, throughput budget, and transfer explanation so throughput behavior becomes inspectable state rather than troubleshooting folklore.

## Core stance

1. route permission is not the same thing as route preference
2. route preference is not the same thing as throughput budget
3. a transfer progress bar is not enough if the operator still cannot answer *why*
4. queue priority, fairness, and delay profile must be visible state rather than hidden tuning
5. relay usage and other expensive route classes should feel like explicit cost posture, not accidental fallback trivia
6. temporary bulk-speed windows and metered caps should reuse the same public transfer model as durable defaults
7. transfer explanation should name bottlenecks in operator language even when the underlying cause comes from disk, source availability, phase override, or route policy

## Terms

### Transfer policy

A durable policy describing how transfers in a scope should be ordered and preferred.
A transfer policy answers things like:

- preferred route classes
- priority strategy
- fairness posture
- whether interactive work should jump the queue
- whether relay-heavy routes are merely allowed or actively discouraged
- whether some file classes should be delayed before transmission

### Throughput budget

A policy object that caps or reserves bandwidth, concurrency, or route-cost consumption for a specific scope.
A throughput budget is not just “speed limit”; it can also express:

- separate ingress and egress ceilings
- route-class-specific caps
- concurrency limits
- relay byte/time budgets
- interactive reserve capacity
- LAN exemptions
- metered-window activation

### Transfer explanation

A derived, inspectable answer for one transfer or one transfer queue.
It should explain:

- what route class is being used
- what route class would have been preferred if available
- which budgets or overrides currently bind
- whether the transfer is active, queued, delayed, backpressured, suspended, blocked, or source-starved
- what would need to change for throughput or progress to improve

### Transfer budget receipt

A durable record proving that a throughput budget or temporary transfer-policy change was applied, changed, or expired.
This matters because route-speed posture should remain auditable after the temporary window ends.

## Public objects

### Transfer policy

Minimum fields:

- `transfer_policy_id`
- `scope_ref`
- `default_lane` (`interactive`, `normal`, `background`, `bulk`, `maintenance`)
- `priority_policy` (`daemon-default`, `smaller-first`, `larger-first`, `older-first`, `newer-first`, `manual-lane`)
- `preferred_route_classes[]` (`lan-direct`, `known-host-direct`, `overlay`, `public-direct`, `relay`)
- `discouraged_route_classes[]`
- `fairness_mode` (`equal-share`, `foreground-first`, `per-peer-fair`, `per-share-fair`, `manual-reserve`)
- `interactive_reserve` nullable
- `delay_profile_ref` nullable
- `relay_cost_posture` (`allowed`, `discourage`, `budgeted`, `blocked`)
- `disk_backpressure_posture` (`adaptive`, `protect-latency`, `throughput-first`)
- `provenance`
- `status` (`active`, `shadowed`, `superseded`)

### Throughput budget

Minimum fields:

- `throughput_budget_id`
- `scope_ref`
- `route_scope` (`all`, `lan`, `overlay`, `public-direct`, `relay`)
- `ingress_limit`
- `egress_limit`
- `burst_limit` nullable
- `concurrency_limit` nullable
- `relay_byte_budget` nullable
- `relay_time_budget` nullable
- `lan_exempt` boolean
- `effective_window` (`durable`, `lease`, `schedule-window`, `manual-override`)
- `origin_ref`
- `expires_at` nullable
- `status` (`active`, `scheduled`, `expired`, `superseded`)

### Transfer explanation

Minimum fields:

- `transfer_explanation_id`
- `transfer_ref`
- `selected_route_class`
- `selected_transport_kind`
- `candidate_route_classes[]`
- `lane`
- `queue_state` (`running`, `queued`, `delayed`, `suspended`, `blocked`, `source-unavailable`, `completed`)
- `budget_refs[]`
- `policy_refs[]`
- `phase_refs[]`
- `bottleneck_kind` (`none`, `route-blocked`, `budget-capped`, `peer-fairness`, `queue-priority`, `delay-profile`, `disk-backpressure`, `source-unavailable`, `phase-suppressed`)
- `current_answer`
- `next_change_hint`
- `captured_at`

### Transfer budget receipt

Minimum fields:

- `transfer_budget_receipt_id`
- `subject_ref`
- `budget_ref`
- `change_kind` (`created`, `amended`, `expired`, `canceled`, `schedule-entered`, `schedule-left`)
- `effective_route_scope`
- `effective_limits`
- `source_refs[]`
- `reason`
- `captured_at`

## Principles

1. **Every active transfer should have an inspectable current answer.**  
   A transfer card should not stop at bytes done and rate. It should be able to say `Using relay because no allowed direct or overlay path is currently healthy; capped to 2 MiB/s by weekday metered budget.`

2. **Permission, preference, and budget must stay separate.**  
   A route may be allowed but not preferred, preferred but not selected, or selected but still capped. Those are different truths and should never collapse into one generic “network settings” explanation.

3. **Priority should explain queue movement honestly.**  
   If an interactive transfer jumps ahead of a background bulk transfer, the lower-priority item should show that it was suspended by queue policy rather than simply looking stalled.

4. **Relay cost should be visible.**  
   A relay path is not morally wrong, but it does carry different performance and exposure tradeoffs. If the product tolerates it, it should show whether relay is merely allowed, currently used, or burning through an explicit budget.

5. **Delay profiles must be public policy, not storage-folder lore.**  
   If office files or other classes are intentionally delayed before transmission to reduce churn or lock conflicts, that should show up in transfer explanation rather than hiding inside local config files.

6. **Budget changes should leave receipts.**  
   Operators should later be able to tell whether a slow or fast period came from durable policy, a time-bounded schedule window, or a one-shot override.

7. **Disk and filesystem bottlenecks belong in transfer explanation too.**  
   Throughput truth is not only about network. A backpressured disk or heavy verification path is still part of “why is this transfer slow?” and should render through the same public explanation grammar.

## Interface implications

The workbench and CLI should each have one coherent transfer surface.
They should not force the operator to triangulate between a progress bar, a route page, a schedule page, a settings dialog, and hidden advanced knobs.

A trustworthy transfer surface should make it easy to answer:

- which route class is currently winning
- whether a better route exists but is disallowed, degraded, or merely not chosen
- which budgets are currently active
- whether the transfer is waiting because of fairness, priority, delay, disk pressure, or source absence
- what would most directly improve this transfer
- which receipt proves a temporary transfer-budget change was in effect

## CLI shape

### `anonsync transfer`

Inspect, explain, and tune transfer behavior without hiding semantics behind generic “speed” preferences.

```text
anonsync transfer list
anonsync transfer show trf_01J...
anonsync transfer explain trf_01J...
anonsync transfer policy show --share media
anonsync transfer policy set --share media --priority newer-first --fairness per-peer-fair --prefer-route overlay
anonsync transfer budget show --share media
anonsync transfer budget set --share media --internet-up 2MiB/s --internet-down 8MiB/s --relay-byte-budget 10GiB/day --reason "hotspot week"
anonsync transfer set trf_01J... --lane interactive
anonsync transfer receipt list --share media
anonsync transfer receipt show tbr_01J...
```

Semantics:

- `transfer explain` should render one current-answer sentence plus structured causality
- `transfer policy show` should separate durable preference from temporary budget state
- `transfer budget set` should emit a receipt whenever it mutates effective throughput posture
- `transfer set --lane ...` should be explicit about which competing transfers may be suspended as a result
- receipt listing should allow later audit of whether a metered window, bulk window, or fairness tweak was in force at the time

## Daemon/API implications

A local daemon should expose transfer policy, throughput budgets, and derived explanations separately from raw transfer progress.

Minimum surface:

```text
GET   /v1/transfers
GET   /v1/transfers/{transfer_id}
PATCH /v1/transfers/{transfer_id}
GET   /v1/transfers/{transfer_id}/explanation
GET   /v1/transfer-policies
POST  /v1/transfer-policies
GET   /v1/transfer-policies/{transfer_policy_id}
PATCH /v1/transfer-policies/{transfer_policy_id}
GET   /v1/throughput-budgets
POST  /v1/throughput-budgets
GET   /v1/throughput-budgets/{throughput_budget_id}
PATCH /v1/throughput-budgets/{throughput_budget_id}
GET   /v1/transfer-budget-receipts
GET   /v1/transfer-budget-receipts/{transfer_budget_receipt_id}
```

The key point is that raw transfer bytes are not enough.
A client should be able to inspect current route class, active policy, active budgets, queue state, and bottleneck reasons without scraping several pages.

## Workbench implications

The workbench should have:

- a transfer detail drawer with current answer, route class, lane, and bottleneck summary
- a budget card showing durable policy plus temporary caps and exemptions
- a queue panel showing which transfers are suspended for priority/fairness reasons rather than just stalled visually
- a receipt trail for temporary metered or bulk-window posture

A mature implementation should let the operator move from `Why is this slow?` to `Show me the cap/policy/route that caused it` in one click.

## Canonical questions this layer must answer

A mature operator surface should be able to answer all of these without support-lore reconstruction:

- “Why is this transfer on relay instead of overlay or direct?”
- “Is this capped because of durable policy, a temporary window, or LAN-only exemption?”
- “What jumped ahead of this transfer in the queue?”
- “Is the bottleneck the network, disk backpressure, source absence, or a delay profile?”
- “Which budget receipt proves the hotspot cap that was active yesterday?”
- “If I widen route permission, will the cap still apply?”

## Non-clone conclusion

Resilio's current docs are strong enough to teach two useful lessons at once.
First, direct/relay choice, queue priority, LAN-specific tuning, and performance graphs are genuinely useful.
Second, they still leave too much of transfer truth spread across icons, articles, settings tables, and storage-folder config.

AnonSync should keep the usefulness while replacing the fragmentation.
The product should expose one explicit transfer-policy, throughput-budget, and route-cost explanation model so transfer behavior remains inspectable public state instead of operator folklore.
