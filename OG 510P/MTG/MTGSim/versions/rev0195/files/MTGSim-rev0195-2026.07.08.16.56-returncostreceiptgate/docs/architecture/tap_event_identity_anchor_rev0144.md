# rev0144 — Tap Event Identity Anchor

## Mission slice

rev0142 made automatic mana-payment plan steps point at the ordered `tap` Event that paid a tap-cost mana ability, and rev0143 gave the plan a local mana-pool span. The remaining weakness was identity: the witness could prove that *some* plain tap row happened between the plan and production, but the tap row itself did not carry structured object/player anchors.

rev0144 keeps tap rows as plain log events while making them identity-bearing:

- `tap_object(...)` now emits the `tap` log row through `record_event_with_links(...)` with `EventRecord::object` set to the tapped permanent and `EventRecord::player` set to the tapping controller.
- `validate_game_state(...)` rejects tap log rows without object/player anchors.
- `ManaPaymentPlanStepRecord::tap_event_sequence` validation now requires the witnessed tap row to identify the planned mana source and the payment player.

## Why this matters

The automatic payment plan is becoming a replayable execution witness: plan row, tap row, produced mana row, paid row, and pool span. Without object/player anchors on the tap row, a consumer could only infer that a tap happened in the right interval. That was enough for ordering, but not for identity.

The new anchor makes a tap-cost payment step answer a stronger question without parsing prose:

1. Which planned source was supposed to tap?
2. Which tap event paid that source tap?
3. Did the tap event identify the same source and payer as the payment plan?

## Invariants

- Plain `tap` EventRecord rows must carry a valid object anchor and player anchor.
- A tap-cost mana-payment plan step must still point to a plain `tap` Event row.
- That tap row must occur after the plan row and before the produced mana row.
- That tap row must identify the same planned mana source and payment player as the plan step.

## Boundary

This is still not the full typed tap/untap journal family. It intentionally keeps `tap` as a plain log row with identity anchors, so the rev0144 slice stays narrow and preserves the current journal shape while preparing the seam for a future `TapStateChangeRecord` refactor.
