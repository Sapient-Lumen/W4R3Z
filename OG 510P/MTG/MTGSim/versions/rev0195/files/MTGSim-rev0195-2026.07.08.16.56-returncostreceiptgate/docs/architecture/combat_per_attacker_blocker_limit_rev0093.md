# rev0093 per-attacker blocker-count restrictions

rev0093 moves the blocker-restriction solver beyond global battlefield caps by adding `CardDefinition::max_blockers_to_block_this`. A zero value means no per-attacker cap; a nonzero value models effects such as “this creature can't be blocked by more than one creature.” The field is part of canonical StateCore hashing and StateCore snapshot serialization.

The restriction is checked in `block_declaration_basic_constraints_satisfied(...)` after complete candidate batches are assembled. For each affected attacker, the engine computes the final blocker count, including existing blockers and the proposed assignments, rejects declarations exceeding the attacker's cap, and then applies menace's minimum-blocker rule. This ordering lets contradictory restrictions compose truthfully: a menace attacker with `max_blockers_to_block_this = 1` cannot be blocked legally.

The blocker requirement maximizer reuses the same complete-declaration predicate with combat-cost payability disabled for compulsory “if able” reasoning. As a result, lure-style `all_able_blockers_block_this_if_able` requirements maximize to a single legal blocker when the attacker itself allows only one blocker, while no-block remains illegal because one requirement can still be satisfied.

Validation now emits `combat.attacker_blocker_limit_exceeded` for malformed StateCore where more blockers are assigned to an attacking creature than its own per-attacker limit permits.

This remains a narrow CR 509 slice, not a complete blocker restriction language. Defender-specific restrictions, “can block only” families, banding-style multi-attacker blocker ordering, and replacement/prevention choices during combat damage remain future work.
