# rev0087 — Combat Alone Restrictions

rev0087 moves the combat requirement maximizer from pure global declaration caps into a narrow per-creature restriction family:

- `CardDefinition::cant_attack_alone`
- `CardDefinition::cant_block_alone`

These fields intentionally do **not** claim full CR 508/509 restriction or cost solving. They cover the high-risk pattern where a required creature is only able to attack or block when at least one partner is included in the same legal declaration.

## Why this slice mattered

rev0086 could maximize must-attack and must-block requirements under global caps, but it still treated each required attacker as independently able if it had a legal target. That was wrong for restriction families that require a second participant. A creature that must attack if able but cannot attack alone is not able in a singleton declaration; it becomes able only when the declaration includes a legal partner.

The same issue exists for blocking. A must-block creature that cannot block alone is not able by itself, but an optional partner can make the must-block requirement satisfiable.

## Implementation shape

Attack declaration legality now runs through `attack_declaration_basic_constraints_satisfied(...)`, which checks:

1. active global attack caps;
2. duplicate attackers;
3. existing per-attacker legality and legal defending target;
4. `cant_attack_alone` after the whole proposed declaration is known.

`maximum_satisfied_attack_requirements(...)` now searches legal attack declaration candidates instead of reducing the problem to `min(required_count, cap)`. This is the important semantic change: optional attackers can make a required restricted attacker able.

Block declarations reuse the existing whole-batch basic constraint path and add `cant_block_alone` before menace finality checks. The existing block requirement search then naturally maximizes over partnered declarations.

## Executable coverage

New C++ tests cover:

- a must-attack creature with `cant_attack_alone` requiring an optional partner;
- the same creature becoming genuinely unable when no partner exists;
- a must-block creature with `cant_block_alone` requiring an optional partner;
- the same blocker becoming genuinely unable when no partner exists;
- validator diagnostics for malformed committed metadata that violates the alone restrictions.

## Remaining risk

Still open:

- arbitrary attack/block costs;
- defender-specific and attacker-specific restrictions beyond the alone family;
- “must be blocked” and lure-style requirements;
- damage-order choices;
- staged declaration rollback as a general transaction primitive.

The key gain is that another rules-correctness seam now crosses the public `LegalAction` enumeration, application, receipt, StateCore snapshot/hash, validation, and trace-replay path instead of living only as a note.

This is not a complete CR 508/509 solver. The purpose of this revision is specifically to make optional partners participate in able/unable reasoning for the narrow alone-restriction family while leaving costs, broader restrictions, damage ordering, and rollback for later work.
