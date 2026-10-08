# rev0177 — damage counter-result links

## Why this cut exists

rev0176 made impossible object damage explicit, but the planeswalker/battle side of the same damage seam still carried a risky aggregate. `DamageRecord::counters_removed` said that damage removed loyalty or defense counters, while the actual counter mutation lived elsewhere as one or more `CounterChangeRecord` rows. Replay, audit, and future replacement/prevention consumers had to trust that the aggregate and the counter log still described the same event.

The online grounding for the cut is narrow: current public Comprehensive Rules observations identify damage to planeswalkers as loyalty-counter removal and damage to battles as defense-counter removal, while the official rules page remains the consulted source rather than an executable spec. This revision does not bundle Wizards rules text; it only records the local implementation seam that needs to be challengeable.

## What changed

`DamageRecord` now owns the counter-result evidence it summarizes:

- `first_damage_counter_change_record_index`
- `damage_counter_change_record_count`

During `deal_damage_to_target(...)`, the engine snapshots the current `GameState::counter_change_records` length before applying damage to a planeswalker or battle. If the damage removes loyalty or defense counters, the final `DamageRecord` points at the contiguous counter-change rows created by that damage result.

Validation then rejects drift instead of leaving it to readers:

- a nonzero `counters_removed` total must have a counter-change range;
- a range without removed counters is invalid;
- only planeswalker/battle damage records may carry such a range;
- each linked row must be a `damage_result` object-removal row;
- linked rows must match damage source, source zone-change identity, target object, sequence order, and counter kind;
- linked row amounts must sum back to `DamageRecord::counters_removed`.

The regression coverage extends the existing counter-change receipt tests. Planeswalker damage now proves the linked loyalty row is present and rejects a missing range or source mismatch. Battle damage now proves the linked defense row is present and rejects a missing range.

## What did not change

This is not a full damage-result replacement layer. Infect, wither, poison result substitution, replacement effects that modify counter removal, damage redirection, and affected-player choice ordering remain future work. The narrow forward motion is that current loyalty/defense damage results are no longer hidden behind an aggregate field or human event text.

## Audit/refactor note

The refactor is deliberately small: it binds an existing typed damage receipt to existing typed counter-change receipts. That reduces inference debt without adding another registry table or doctrine layer.
