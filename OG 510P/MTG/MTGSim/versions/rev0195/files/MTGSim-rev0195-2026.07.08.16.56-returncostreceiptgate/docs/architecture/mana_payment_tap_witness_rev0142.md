# rev0142 — Mana Payment Tap Witness

## Mission slice

rev0141 made automatic mana-payment production evidence bidirectional: a planned mana-ability step points to the `Produced` `ManaChangeRecord`, and that produced row points back to the plan step. One ordered execution fact still lived only in the plain event stream: when a selected mana ability had a tap cost, the readable plan did not name the tap row that paid that source tap before mana production.

rev0142 adds a narrow bridge witness, not a full tap-record model. `ManaPaymentPlanStepRecord::tap_event_sequence` records the ordered `tap` Event/EventRecord sequence for tap-cost mana-ability steps selected by automatic payment. The plan now proves the local execution order:

1. `mana_auto_plan` records the typed plan.
2. A tap-cost step records the tap-event witness that paid the source tap.
3. The step records the `Produced` `ManaChangeRecord` witness for the mana output.
4. The final automatic `Paid` `ManaChangeRecord` spends the resulting pool.

## Why this is the right next seam

The project’s center is trusted transition evidence. A full `TapRecord` family would be useful, but it is larger than this adjacent cost-plan seam: it would touch ordinary tap actions, untap-step batching, combat declarations, activation costs, and event-record link taxonomy. rev0142 keeps scope tight by making automatic payment plans auditable against the existing ordered event stream while leaving a future typed tap/untap journal record as an explicit next refactor.

## Invariants

- Tap-cost plan steps must have a nonzero `tap_event_sequence`.
- Non-tap plan steps must not carry a tap witness.
- The witness must point to a plain `EventRecordKind::Log` row whose `log_kind` is `tap`.
- The tap witness must occur after the plan event and before the linked `Produced ManaChangeRecord`.
- The tap witness must occur before the final paid mana row.
- Planned steps may not share the same tap-event witness.

## Boundaries

This slice does not claim the tap event itself is fully typed. It deliberately records a sequence witness to the current event/log spine and adds validator checks around ordering and event kind. The future stronger version should introduce a typed `TapStatusRecord`/`TapChangeRecord` family and then replace the sequence bridge with a typed record index.
