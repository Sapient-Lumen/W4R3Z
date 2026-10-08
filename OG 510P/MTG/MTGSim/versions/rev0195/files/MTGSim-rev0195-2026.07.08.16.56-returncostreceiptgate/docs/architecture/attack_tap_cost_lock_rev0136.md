# rev0136 — Attack Tap-Cost Lock

## Why this cut exists

rev0134 locked activated-ability tap-cost sources out of their own auto-mana payment plans. rev0135 then refined a sacrifice-cost body inside that transaction shell. The next audit found the same shape in combat attack costs: a nonvigilance creature chosen as an attacker was still visible to the generic auto-mana planner before the engine tapped it as part of the attack declaration.

That let a hasty creature with an attack cost and a tap-for-mana ability self-fund the cost by tapping itself, then still become an attacking nonvigilance creature. In the modeled turn-based action, the declared nonvigilance attacker is a locked tap source for the attack declaration; it should not be selected as a tap-mana source for that same cost.

## What changed

rev0136 adds `attack_declaration_locked_tap_sources(...)`, which derives the tap-source lock set from the selected attack assignments. Nonvigilance assigned attackers are locked because the declaration will tap them; vigilance attackers are not locked by that declaration-tap step.

Attack-cost preflight now calls `can_pay_mana_cost_with_available_mana_excluding_tap_sources(...)` with that lock set. Attack-cost payment now uses `pay_combat_declaration_mana_cost_excluding_tap_sources(...)`, which delegates to the same locked-source auto-mana path introduced for rev0134 activated abilities while preserving the declaration action's priority snapshot.

Block costs deliberately remain on the generic combat cost helper because blockers are not tapped by the modeled declaration step.

## Regression

`test_attack_cost_locks_nonvigilance_attackers_out_of_auto_mana_payment` proves the seam end to end:

- a hasty nonvigilance attacker with `{G}` attack cost and a tap-for-green mana ability cannot self-fund its own attack cost;
- legal-action enumeration omits that self-funded declaration;
- direct declaration fails without creating combat records, stack entries, tapped state, attacking metadata, floating mana, or a closed attacker-declaration window;
- adding an external Forest makes the same attack legal, taps the external source for the cost, taps the attacker only through declaration, and leaves no floating mana.

## Relationship to the paid-action transaction spine

This is a sibling of the activated-ability tap-cost lock, not a replacement for broader phase evidence. The shared point is that cost payment needs an explicit lock set derived from the chosen action before auto-mana planning begins. In rev0136 that lock set is still local to combat attack costs. Future named paid-action phases should make the lock set a first-class part of transition evidence.

## Remaining gaps

The combat cost scaffold is still mana-only. It does not model arbitrary attack costs, optional attack costs, cost reducers/increasers, replacement effects during cost payment, or explicit player-chosen mana plans. The next useful refactor is to unify the activated/cast/combat lock-set helpers into a named cost-plan phase that can be audited and replayed independently.
