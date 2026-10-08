# Sacrifice Cost Witness Receipts — rev0151

rev0151 narrows the sacrifice-cost evidence on `StackPlacementRecord`. The prior paid-action phase receipt named the broader paid-action zone-change span, which proved that a cost-time movement occurred before the final stack-placement receipt. That was enough for ordering, but not enough for consumers that want to inspect exactly which zone changes are the sacrifice payment.

## New receipt fields

- `first_sacrifice_cost_zone_change_record_index` — one-based index of the first `ZoneChangeRecord` that belongs to a paid sacrifice cost.
- `sacrifice_cost_zone_change_record_count` — count of sacrifice-cost zone-change rows in that contiguous witness range.
- `sacrifice_cost_event_sequence` — `EventRecord` sequence for the `pay_sacrifice_cost` log row that closes the payment.

These fields live beside the existing paid-action phase evidence and are sealed by `seal_sacrifice_cost_witness(...)` from inside `seal_paid_action_phase(...)`. The helper treats a sacrifice witness as a battlefield object whose requested destination is graveyard; the final destination may still differ if a zone-change replacement changes the event.

## Validator contract

`validate_game_state(...)` now rejects a paid sacrifice cost when the exact sacrifice witness range is absent, when the range points outside the journal, when a witness row is outside the paid-action window, when the movement does not request battlefield-to-graveyard, when a synthetic ability object is named as the sacrificed object, or when the `pay_sacrifice_cost` event witness is missing/wrong/out of order.

## Why this matters

The mission is not just to know that something happened during payment; it is to provide challengeable, typed evidence for the exact state transition. Sacrifice costs are especially important because they can stale targets, queue dies triggers, and move a source before its stack object resolves. This revision makes those movements locally auditable from the stack-placement receipt.

## Package-hygiene audit

rev0151 also keeps the shared cube easier to audit by compacting append-only C++/rule/audit history rows and SQLite metrics payloads into trend summaries. Full execution detail remains in the named latest reports, while history and metrics files stop tripping large-payload warnings or carrying transient Python cache artifacts.
