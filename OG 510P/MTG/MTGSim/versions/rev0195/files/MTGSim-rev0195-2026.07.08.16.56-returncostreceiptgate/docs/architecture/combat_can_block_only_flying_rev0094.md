# rev0094 can-block-only-flying restriction solver

rev0094 moves a defender-specific blocker restriction into the same public blocker declaration and maximum-satisfaction requirement path as the previous combat work. `CardDefinition::can_block_only_flying` models a narrow “this creature can block only creatures with flying” family. It is intentionally narrower than a complete blocker-restriction language, but it is executable and replayable.

The key semantic edge is requirement analysis. A creature with both `blocks_each_combat_if_able` and `can_block_only_flying` is not forced to block a ground attacker, because there is no legal assignment. The same creature is forced to block an attacking creature with flying when it otherwise can block. The implementation routes this through `block_assignment_basic_legal(...)`, so enumeration, `can_declare_blockers(...)`, `apply_action(...)`, trace replay, and the max-satisfaction search all observe the same restriction.

The restriction composes with flying/reach evasion. A sky-only blocker still needs flying or reach to block a flying attacker; the regression fixture grants reach so the new restriction is tested rather than the older flying-evasion rule.

Validation emits `combat.can_block_only_flying_violation` if malformed StateCore marks a sky-only blocker as blocking a non-flying attacker. The field is included in canonical StateCore hashing and StateCore snapshot serialization.

This still is not a complete defender-specific restriction language. Open pieces include arbitrary “can block only one type/color/player/object” predicates, “can block only alone/with partner” variants beyond the current narrow fields, non-mana or choice-bearing declaration costs, and a general staged declaration rollback object.
