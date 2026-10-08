# rev0155 — Target Set Hash Witness

## Problem

The rev0153 choice payload anchors separated `choose_mode` and `choose_target` rows, and rev0154 sealed those fields into the Journal hash. That still left a narrow multi-target hole: a `choose_target` EventRecord could state `choice_target_count == 2`, but the row did not carry the exact ordered target vector it represented. Single-target anchors had `target`; multi-target anchors intentionally left `target` empty.

For agents and replay auditors, count-only evidence is not enough. Target order is part of the explicit choice surface, and a later stack-placement receipt should be able to prove that its chosen target vector is the same target vector announced before costs were paid.

## Change

rev0155 adds `EventRecord::choice_target_set_hash` and the public `target_choice_set_hash(...)` helper. Paid spell casts, activated abilities, and loyalty abilities compute the hash from stamped `TargetRef` vectors after zone-change identity has been locked. `hash_into(EventRecord)` includes the new field, so tampering with the target-set payload changes `journal_hash(...)`.

Validation now checks two additional conditions for target choice witnesses:

- `stack_placement_record.choice_lock_target_event_missing_set_hash` when a `choose_target` row has no ordered target-set hash.
- `stack_placement_record.target_choice_event_set_hash_mismatch` when the anchor payload does not match `StackPlacementRecord::chosen_targets`.

The regression `test_multi_target_choice_anchor_hashes_ordered_target_set` proves the seam on a two-target paid spell: the target anchor count is two, the single-target payload remains empty, the ordered set hash matches the placement vector, corrupted hashes are rejected and hash-sealed, and reordering `chosen_targets` is rejected even though the count stays unchanged.

## Why this matters

This keeps MTGSim moving toward the mission heart: canonical state plus explicit legal choice yields one deterministic next state and typed evidence that replay, audit, search, fuzzing, and future agents can challenge. Target choices are now represented as content-addressed choice evidence instead of prose plus a count.

## Next seam

The next deeper refactor is still a first-class `ChoiceDeclarationRecord`: a single pre-payment announcement record that can unite modes, target vectors, X values, alternative/additional costs, divisions, optional decisions, and order-dependent declarations before any payment mutation occurs.
