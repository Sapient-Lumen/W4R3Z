# Planeswalkers and loyalty scaffold

rev0019 adds the first narrow planeswalker slice. The point is not to claim full planeswalker support; it is to create the state and test seams that later work can extend without rewriting combat, damage, state-based actions, and legal-action enumeration.

## Implemented shape

- `CardDefinition::printed_loyalty` is local metadata for fictional/sample cards.
- Planeswalkers entering the battlefield receive loyalty counters through the same battlefield-entry seam used by zone movement and token creation.
- `planeswalker_loyalty(...)` is the public query helper.
- Damage to a battlefield planeswalker removes loyalty counters through the shared damage target path instead of marking creature damage or changing player life.
- `apply_state_based_actions(...)` moves a zero-loyalty battlefield planeswalker to its owner's graveyard.
- Attacker declaration now accepts a `TargetRef` combat target. Player targets remain supported, and opposing battlefield planeswalkers can be attacked.
- Combat damage to an unblocked attacker’s planeswalker target removes loyalty.
- `LoyaltyAbilityDefinition` models one scaffold ability payload per card definition. `activate_loyalty_ability(...)` pays loyalty, gates timing, records once-per-turn activation, creates a synthetic stack object, and resolves through the same effect payload machinery as other synthetic abilities.

## Refactor/audit slice

Before this revision, attacking metadata only stored `defending_player`. rev0019 keeps that for compatibility but adds `GameObject::attacked_object` so planeswalker combat targets can flow through validation, combat damage, zone-change cleanup, and scenario assertions. This avoids hard-coding a second combat path for planeswalkers.

The audit now checks planeswalker and loyalty wiring across core types, engine APIs, validation codes, scenario syntax, CMake smoke tests, rule modules, card DB schema, sample catalog entries, docs, and rules-ledger rows.

## Scenario syntax

```text
card Training_Walker planeswalker 0 0 loyalty=4 color=blue loyalty_ability=+1:damage:2:player
action attack 1 7 target=object:3
action loyalty 1 3 target=player:2
expect_loyalty 3 5
expect_attacking_target 7 object:3
```

## Limitations

This is not a complete planeswalker implementation. Missing areas include multiple loyalty abilities, full timing exceptions, modal loyalty abilities, loyalty abilities with non-loyalty costs, target-changing effects, effects that modify printed/starting loyalty, redirection/history edge cases, complete multiplayer attack-option support, copied planeswalkers/abilities, control-changing nuance, complete replacement/prevention ordering around damage and counters, and Oracle-text-derived abilities.

## Design direction

The important long-term seam is that planeswalkers cut across four independent engines:

1. card/object metadata and counters;
2. combat attack target selection;
3. damage and state-based actions;
4. activated ability timing/cost/stack resolution.

Keeping those as small composable helpers makes future rule changes easier: a rules-diff that changes a planeswalker subrule should usually touch a ledger row, a scenario, a focused C++ case, and one helper seam rather than a monolithic resolver.

## rev0064 loyalty cost evidence

Loyalty ability activation no longer changes loyalty counters as an untyped side effect. Positive and negative loyalty costs now append `CounterChangeRecord` rows with `cost_payment=true`, the planeswalker as both source and changed object, the loyalty counter kind, and before/after loyalty totals. The activation still creates the same stack object and still runs SBAs afterward, so a negative cost that leaves the planeswalker at zero can move the source to the graveyard while the ability remains on the stack.
