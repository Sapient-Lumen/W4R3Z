# rev0088 — Combat Must-Be-Blocked Requirements

rev0088 moves another risky CR 509 declaration seam into executable legality: attacker-side “must be blocked if able” requirements.

Before this revision, the blocker maximizer counted only required blockers (`blocks_each_combat_if_able`). That was insufficient because some requirements live on the attacking creature: a blocker declaration may need to block a particular attacker even when no blocker itself is required to block.

## Implemented slice

- `CardDefinition::must_be_blocked_if_able` marks an attacking creature as contributing an attacker-side block requirement.
- The field participates in canonical StateCore hashing and `StateCoreSnapshot.v1` serialization.
- `maximum_satisfied_block_requirements(...)` now scores both sides of the blocking transaction:
  - required blockers that are assigned to block;
  - attacking creatures with `must_be_blocked_if_able` that become blocked by the declaration.
- Public `LegalAction` enumeration and `apply_action(...)` filter to declarations that satisfy the maximum legal requirement count.
- Menace remains part of basic declaration legality, so a must-be-blocked menace attacker requires a complete two-blocker declaration when one exists, but no-block remains legal if only one blocker exists.

## Why this matters

This is the first slice where the block requirement solver has to optimize across **blocker-side** and **attacker-side** obligations in the same search. It prevents a misleading “zero required blockers means no-block is legal” shortcut.

## Tests added

- `test_combat_must_be_blocked_filters_empty_declarations`
- `test_combat_must_be_blocked_maximizes_under_single_blocker_choice`
- `test_must_be_blocked_menace_requires_complete_pair_or_none_when_unable`

## Still not claimed

This is still not a complete CR 509 solver. The engine still needs arbitrary blocking costs, defender- or attacker-specific restrictions, “all creatures able to block this creature do so” families, damage-order choices, and rollback for failed staged declarations.
