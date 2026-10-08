# Protection, menace, and color/source characteristics scaffold

rev0015 adds the first explicit source-characteristic seam. `CardDefinition::color_mask` stores W/U/B/R/G metadata, and `object_color_mask(...)` derives a simple mask from colored mana-cost fields when the card definition does not set one explicitly. This is deliberately narrow: it is enough for deterministic source-aware tests, but it is not a full characteristic/layer system.

Protection is represented as `CardDefinition::protection_color_mask`. The current executable behavior covers three high-value seams:

- source-aware targeting rejects targets protected from the source object's colors;
- damage from a source with a protected color is prevented before shield-style prevention is applied;
- a creature with protection from a blocker color cannot be blocked by that blocker.

Menace used to expose a serious public-action seam: `declare_blockers(...)` could accept a two-creature `BlockAssignment` batch, but `LegalAction` enumeration, receipts, and trace replay could express only one blocker/attacker pair. rev0083 closes that narrow end-to-end gap. `make_declare_blockers_action(...)` encodes multi-blocker declarations as blocker/attacker object-target pairs, `block_assignments_from_action(...)` decodes both the old one-target shape and the new pair-vector shape, and menace batches now travel through enumerate -> apply_action -> ActionReceiptRecord -> ActionTrace replay.

This is still a bridge, not the final combat architecture. The engine still needs a true whole-declaration payload for all attackers/blockers, explicit empty declarations, restrictions/requirements solving across every candidate assignment, and rollback before priority resumes. The current pair-vector action is deliberately limited to making the existing legal menace batch observable and replayable through the public boundary.

Current known gaps: no protection from non-color qualities, no player protection, no Aura/Equipment/Fortification attachment rules, no full trample/protection assignment nuance, no layers/timestamps/color-changing effects, no color indicators/devoid/characteristic-defining abilities, no complete blocker restriction/requirement solver, no full multi-attacker blocker-declaration enumeration, and no Oracle-text parser.

The important refactor is that color/protection/blocking checks now live behind shared helpers (`target_ref_is_legal_for_source_object`, `target_has_protection_from_source`, `object_color_mask`, `can_declare_blockers`, `make_declare_blockers_action`, `block_assignments_from_action`) rather than being hand-coded in individual spell/combat paths.

## rev0084 note — declaration finality around menace

rev0084 keeps the rev0083 menace batch bridge and adds the surrounding declaration-finality scaffolding. A defending player can now explicitly choose a no-block declaration, while a legal nonempty blocker batch still records all blocker/attacker pairs. The shared `block_assignment_basic_legal(...)` helper keeps protection, controller, combat-state, and evasion prechecks consistent before the final batch-level menace count is evaluated.
