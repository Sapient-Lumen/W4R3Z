# rev0187 — Trigger target-choice seal

rev0187 audits the seam left by rev0186's trigger stack barrier. Rev0186 stopped targeted triggers with no legal choices from creating targetless synthetic stack objects, but the durable `TriggerRecord` did not yet prove the choice surface seen at the 603.3d stack gate.

## Risk addressed

A triggered ability can later resolve, leave the stack, and clear or mutate its synthetic stack object. If the only durable record says "a trigger was stacked" without recording the required target count, selected targets, legal target-set cardinality, and target-set hash, audit consumers have to infer the 603.3d choice gate from transient stack-object state.

That is brittle in exactly the failure modes this cube is trying to make replayable: no-legal-choice drops, source-color/protection target filters, and target-selection corruption after the fact.

## Code-bearing change

`TriggerRecord` now carries a small target-choice seal:

- `required_target_count`
- `chosen_targets`
- `legal_target_set_count`
- `choice_target_set_hash`
- `target_choice_recorded`
- `no_legal_choices`

`choose_default_trigger_targets(...)` computes this evidence as it enumerates the deterministic legal target sets. `seal_trigger_target_choice(...)` writes it to the already-linked `TriggerRecord` before the trigger either becomes a stack object or is dropped for no legal choices.

The validator now rejects forged or incomplete target-choice evidence, including mismatched target counts, tampered target-set hashes, stacked triggers without a recorded choice gate, no-legal-choice rows that still stack, and live stack-object targets that diverge from the sealed record while the ability remains on the stack.

## Regression coverage

- `test_targeted_trigger_without_legal_targets_is_dropped_before_stack` now checks the no-legal-choice seal.
- `test_targeted_trigger_chooses_legal_target_when_put_on_stack` checks the successful player-target seal.
- `test_self_dies_targeted_trigger_uses_source_color_snapshot_for_protection` checks the successful object-target seal with source-color/protection filtering.
- `test_trigger_record_choice_seal_validation_rejects_tampered_payload` corrupts the hash, target vector, missing gate flag, and no-legal-choice flag to prove validation fails closed.

## Remaining gaps

This still uses the cube's deterministic first-legal-set policy for simple triggers. Full player-selected target/mode choices, optional triggers, intervening-if handling, delayed/reflexive triggers, and richer 603.3 APNAP choice transactions remain future high-risk seams.
