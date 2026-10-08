# MTGSim rev0154 — Choice Anchor Hash Seal

rev0154 audits the receipt surface added in rev0153 and closes the hash boundary around it. rev0153 made `EventRecord::choice_mode_index`, `EventRecord::choice_target_count`, `StackPlacementRecord::mode_choice_event_sequence`, and `StackPlacementRecord::target_choice_event_sequence` validator-visible, but those new fields were not yet part of the Journal hash.

That left a narrow but important trust gap: a corrupted mode payload, target-count payload, or split choice-anchor sequence could be rejected by `validate_game_state(...)`, yet could still collide with the same `journal_hash(...)` as the uncorrupted journal. For a datacube whose mission is deterministic transition evidence, validation and hash sealing should agree about which receipt fields are semantically material.

## Code-bearing change

`hash_into(StableHasher&, const EventRecord&)` now includes:

- `EventRecord::choice_mode_index`
- `EventRecord::choice_target_count`

`hash_into(StableHasher&, const StackPlacementRecord&)` now includes:

- `StackPlacementRecord::mode_choice_event_sequence`
- `StackPlacementRecord::target_choice_event_sequence`

The change intentionally keeps the existing `MTGSim.Journal.v1` namespace: this is not a new journal object family, but completion of the rev0153 field surface inside the existing journal hash contract.

## Regression and audit guard

`test_choice_payload_and_anchor_fields_are_journal_hash_sealed` builds a targeted modal paid cast, records the baseline `journal_hash(...)`, then mutates each newly sealed field independently. The test requires the journal hash to change for all four payload/anchor drifts.

`audit_choice_anchor_hash_seal_wiring(...)` probes source, tests, architecture notes, audit notes, rules ledger, README, changelog, and artifact report so this closure remains visible in the cube rather than becoming an untracked hash helper edit.

## Next seam

The deeper next step is not another ad hoc choice field. It is a typed `ChoiceDeclarationRecord` that can unify mode, targets, X, alternative/additional costs, optional choices, divisions, and ordering choices under one pre-payment declaration hash. rev0154 only seals the current split-anchor surface so the existing paid-action receipt spine is trustworthy.
