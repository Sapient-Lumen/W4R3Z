# Combat Requirement Solver — rev0085

rev0085 implements a deliberately narrow requirement solver at the public combat declaration boundary.

## What became executable

- `CardDefinition::attacks_each_combat_if_able` marks creatures that must attack each combat if they can.
- `CardDefinition::blocks_each_combat_if_able` marks creatures that must block each combat if they can.
- `can_declare_attackers(...)` now rejects empty and subset declarations when a required attacker has at least one legal defending target.
- `can_declare_blockers(...)` now rejects empty and subset declarations when a required blocker can participate in a legal block declaration.
- Menace is handled in the ability-to-block test: one required blocker alone is not able to block a menace attacker, but a second legal blocker makes the complete batch required.

## Why this was the right next slice

rev0083 and rev0084 made batch and empty declarations replayable. The highest-risk remaining gap was that legality still treated declarations as shape-correct rather than requirement-correct. This revision moves one real rule family from notes into executable state transitions without expanding the registry surface.

## Important non-claims

- This is not a complete CR 508/509 solver.
- It does not maximize among conflicting requirements.
- It does not implement attack or block costs.
- It does not implement all restrictions, bands, blocking damage-order choices, or rollback for failed staged declarations.
- Snapshot payloads now include the new requirement flags; no backward compatibility claim is made for older snapshot payloads.

## Acceptance tests added

- `test_combat_attack_requirement_filters_empty_and_subset_declarations`
- `test_combat_block_requirement_filters_empty_and_subset_declarations`
- `test_must_block_menace_requires_complete_legal_declaration`

These tests exercise `enumerate_legal_actions(...)`, `apply_action(...)`, receipt classification, and trace replay where applicable.
