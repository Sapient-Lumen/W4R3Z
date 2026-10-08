# Combat scaffold

rev0008 added explicit combat state to the C++ core. rev0013 refactored the combat-damage path around blocked-attacker memory and split damage batches. rev0014 adds summoning-sickness, haste, and defender gates to attacker legality, while still keeping the scope deliberately small.

## Data model

`GameObject` carries transient combat metadata:

- `attacking`: the object has been declared as an attacker;
- `blocked`: at least one blocker has been declared for this attacker this combat;
- `defending_player`: the player currently being attacked by that object;
- `blocking`: for a blocker, the attacking object it blocks.

`GameState` also carries `combat_damage_assigned_this_step` so repeated step advancement does not double-assign damage.

This metadata is object-local and transient. Zone movement and end-of-combat cleanup clear it, and validation rejects impossible combat metadata.

## Current legal actions

`enumerate_legal_actions(game, player)` emits:

- `DeclareAttacker` during declare attackers for the active player;
- `DeclareBlocker` during declare blockers for the defending player;
- pass-priority, paid-cast, targeted paid-cast, tap-mana, and pending-trigger actions from earlier slices.

The action surface is still a scaffold. It does not yet encode attack requirements, evasion beyond flying/reach, haste/defender/summoning-sickness gates, planeswalker/battle attack choices, multi-opponent semantics, or multi-block damage-order choices.

## Current combat damage

`assign_combat_damage(game)` now performs deterministic combat-damage batches:

1. If any first-strike or double-strike creature is involved, a first-strike batch runs.
2. State-based actions run after that batch.
3. The regular batch runs. Double-strike creatures participate again; first-strike-only creatures do not.
4. State-based actions run after regular damage.

Within a batch:

- never-blocked attackers damage the defending player;
- non-trampling blocked attackers damage the first blocker in object-id order;
- trampling blocked attackers assign deterministic lethal damage to blockers in object-id order, then excess to the defending player;
- blockers damage the attacker they block;
- damage flows through `deal_damage_to_target`, so prevention, lifelink, deathtouch metadata, and indestructible/SBA behavior share one path.

This is enough to test object lifecycles, action enumeration, damage, SBAs, keyword hooks, and blocked-attacker state. It is not enough for real games.

## Validation invariants

`validate_game_state` checks that combat metadata is coherent:

- no attacker/blocker metadata outside battlefield;
- no noncreature attacker/blocker metadata;
- no combat metadata outside combat steps;
- no object both attacking and blocking;
- a blocked object must also be attacking;
- attackers must have a valid defending player different from their controller;
- attackers cannot have defender and cannot be summoning sick;
- blockers must point at a valid attacking creature;
- blocker controller must match the defending player attacked by that attacker;
- a blocker cannot point at an attacker that is not marked blocked;
- a ground creature cannot be recorded as blocking a flying attacker unless it has flying or reach;
- `combat_damage_assigned_this_step` may be set only during combat damage.

## Next combat work

The highest-value next slices are:

1. attack requirements/restrictions and costs to attack/block beyond defender;
2. multiple defending entities: players, planeswalkers, battles;
3. multi-block ordering and player-selected damage assignment order;
4. menace and other evasion/restriction hooks;
5. protection/ward and damage-prevention/replacement interactions;
6. richer combat event records for attack/block/damage triggers;
7. control-change effects that update the summoning-sickness timestamp seam.


## rev0015 batch blocking and protection

Combat declaration now has both `declare_blocker` and `declare_blockers`. The one-blocker helper remains convenient for ordinary tests, while the batch helper is the first step toward a real blocker-declaration solver. Menace uses that seam: single blocks are illegal, but a two-blocker batch is accepted. Protection-from-color also feeds `can_block_attacker_by_evasion`, so a blocker with a protected color is filtered before combat metadata is committed.


## rev0019 planeswalker combat targets

Attacker declaration now has a target-ref based path. The old player-only helper delegates to it, and a new object-target path accepts opposing battlefield planeswalkers. Combat metadata records `attacked_object` separately from `defending_player`; validation rejects illegal planeswalker combat targets, stale attacked-object references, and self-controlled planeswalker targets.


## rev0020 battle combat target seam

`rev0020` generalizes the planeswalker object-combat path so attackers can also target battles. The attacker stores `attacked_object`; `defending_player` remains the player who may block. For planeswalkers, that player is the object's controller. For battles, that player is the battle protector. This is still a scaffold and does not implement all battle subtype or multiplayer attack-option rules.

## rev0025 continuous-effect consumers

Combat now benefits from the shared static-effect seam. Evasion checks can see statically granted flying, attacker legality can see statically granted haste, and combat damage continues to use derived power rather than printed power. This is still a tiny subset of layers, but it reduces future refactor pressure.


## rev0053 typed combat-damage assignment records

rev0053 adds `CombatDamageAssignmentRecord` as the typed audit trail for combat damage assignment. The previous `DamageRecord` seam recorded requested/prevented/dealt damage, but combat routing itself still lived in log strings. That was risky around trample, first strike, double strike, blocker damage, and blocked-attacker memory because consumers could see damage but could not reliably explain assignment context.

Each assignment record snapshots the damage source, source controller, source zone-change identity, assigned target, target zone-change identity for object targets, assigned amount, first-strike-batch and split-combat flags, whether the source was an attacker or blocker, whether the attacker was blocked, blocker count, trample status, excess-trample routing, and the linked `DamageRecord` emitted by `deal_damage_to_target(...)`.

The focused regression uses a trampler blocked by a bear. The attacker-to-blocker lethal assignment, attacker excess to the defending player, and blocker damage back to the attacker all leave typed records. Validation rejects records with broken damage links, impossible source-role flags, missing source/target zone snapshots, and `excess_trample` without an attacking trampler.

## rev0054 typed combat-declaration records

rev0054 adds `CombatDeclarationRecord` as the typed audit trail for attacker and blocker declaration. Combat damage assignment already had durable records in rev0053, but its preconditions still depended on object metadata and string events. That was risky around vigilance, tapped state, player/object attack targets, flying/reach snapshots, menace batch blocking, and blocked-attacker memory.

Each attacker declaration record snapshots the actor, controller, defender, target, object zone-change identity, target zone-change identity for planeswalkers or battles, tapped-before/tapped-after state, and whether vigilance explains a no-tap result. Each blocker declaration record snapshots blocker and attacker zone-change identity, flying/reach/evasion context, blocker batch size, final blocker count for the attacker, whether `menace_satisfied`, and whether the attacker was marked blocked after declaration.

The focused regression covers a vigilant attacker that remains untapped and a menace attacker blocked by a legal two-blocker batch. Validation rejects records with broken event links, stale actor/target snapshots, invalid attack/block role fields, vigilance tap mismatches, blocker tap-state mutation, flying/reach snapshot corruption, and menace records whose final blocker count no longer satisfies the recorded batch.


## rev0084 declaration-completion state

The combat scaffold now records whether the attacker declaration has been completed in the current declare-attackers step and which defending players have completed blocker declarations in the current declare-blockers step. This allows explicit empty declarations to be replayable actions without reopening the declaration window. These fields are part of StateCore snapshot and hash identity, but they remain scaffolding until a full CR 508/509 declaration solver replaces the current bounded enumeration.
