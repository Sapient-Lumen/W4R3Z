# rev0089 — All-Able Blockers Requirement Solver

rev0089 extends the blocker declaration maximizer and maximum-satisfaction search with a narrow lure-style requirement: an attacking creature can require every able blocker controlled by the defending player to block it if a legal declaration can satisfy that obligation.

## Implemented seam

- `CardDefinition::all_able_blockers_block_this_if_able` marks an attacker as contributing blocker-specific requirements.
- StateCore hashing and snapshot serialization include the new field.
- `object_requires_all_able_blockers(...)` projects the flag through the current object definition.
- `satisfied_block_requirement_count(...)` now counts each legal blocker assigned to such an attacker as one satisfied requirement.
- `maximum_satisfied_block_requirements(...)` continues to enumerate complete candidate declarations and therefore composes this requirement with menace, `cant_block_alone`, and `max_blockers_each_combat`.

## Regression shape

- With two able blockers and no cap, no-block and either single-block declaration are filtered; the complete two-blocker declaration is exposed and replayable.
- With a one-blocker cap, no-block is filtered, either single blocker maximizes the legal requirement count, and the two-blocker declaration remains illegal.

## Still missing

This is not a complete CR 509 solver. It does not implement arbitrary block costs, banding, damage-order choices, or a staged rollback API for failed declaration attempts.
