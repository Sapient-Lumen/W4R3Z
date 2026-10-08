# Battles, defense counters, and protectors

Revision `rev0020` adds the first battle-card scaffold. It is intentionally narrow, but it forces several useful refactor seams:

- battles are combat targets through the same `TargetRef` attacker path introduced for planeswalkers;
- battles enter the battlefield with defense counters from `CardDefinition::printed_defense`;
- each battlefield battle stores a `battle_protector` player reference;
- damage to a battle removes defense counters instead of marking damage or changing life;
- a zero-defense battle is moved to its owner's graveyard by state-based actions;
- legal action enumeration can emit attacks toward battles;
- only the battle's protector can block creatures attacking that battle.

The current default protector policy is a two-player/Siege-like convenience: when a battle enters, MTGSim chooses the next alive opponent as protector. A future subtype-aware implementation must move that choice out of the generic battle hook and into the appropriate battle subtype or replacement/entry pipeline.

## Why this was a useful audit/refactor slice

Planeswalker combat in `rev0019` still looked somewhat special. Battles require a similar but not identical target shape: an attacking creature can attack an object, but the defending player is the battle's protector rather than the object's controller. That pressure pushed combat metadata toward:

- `attacked_object` as the durable object target;
- `defending_player` as the player allowed to block;
- validation checks that reconcile those two fields by object type.

That keeps future combat targets, such as battles with subtype-specific behavior, from becoming a pile of ad hoc player-only conditionals.

## Current limitations

This is not full battle support. It does not yet implement Siege-specific intrinsic triggered abilities, transforming/casting the back face, subtype-specific protector choices, battle defense modification replacement effects, copied battles, battle control-change protector repair, attack restrictions/requirements, all multiplayer attack-option nuances, or state-based actions for unresolved battle triggers. The ledger rows are therefore marked as scaffold/tested, not complete.
