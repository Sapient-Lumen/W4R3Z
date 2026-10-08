# rev0156 — Mode Contract Hash Witness

## Problem

rev0153 split mode and target choice anchors, rev0154 sealed their anchor fields into `journal_hash(...)`, and rev0155 made target anchors prove exact ordered target vectors. The remaining asymmetry was on the mode side: a `choose_mode` row still proved only `choice_mode_index`. That ordinal is useful, but a replay/search/agent consumer still had to chase the current card definition to know which effect and target contract the selected mode represented.

For a transition kernel whose mission is canonical state plus explicit legal choice plus challengeable evidence, mode choice evidence should name the selected mode contract, not only its position in a modes vector.

## Change

rev0156 adds `EventRecord::choice_mode_contract_hash` and the public `mode_choice_contract_hash(...)` helper. Paid modal casts compute the hash from the selected `SpellModeDefinition` when emitting the `choose_mode` row. `hash_into(EventRecord)` includes the new payload, so tampering with the mode contract witness changes `journal_hash(...)`.

Validation now checks two additional conditions for mode choice witnesses:

- `stack_placement_record.choice_lock_mode_event_missing_contract_hash` when a `choose_mode` row has no selected-mode contract hash.
- `stack_placement_record.mode_choice_event_contract_hash_mismatch` when the anchor payload does not match the selected `SpellModeDefinition` named by `StackPlacementRecord::chosen_mode_index`.

The regression `test_mode_choice_anchor_hashes_selected_mode_contract` proves that a modal paid cast names the exact mode choice event, stores the selected mode's contract hash, rejects missing or mismatched contract hashes, and hash-seals the payload through `journal_hash(...)`.

## Why this matters

This makes the choice spine symmetric. Target choices now prove ordered target vectors, while mode choices prove the selected effect/target contract. Consumers no longer need to treat a mode ordinal as enough semantic evidence for what was announced before costs were paid.

## Next seam

The next deeper refactor remains a first-class `ChoiceDeclarationRecord`: a single pre-payment announcement record that can unite modes, target vectors, X values, alternative/additional costs, divisions, optional decisions, and order-dependent declarations before any payment mutation occurs.
