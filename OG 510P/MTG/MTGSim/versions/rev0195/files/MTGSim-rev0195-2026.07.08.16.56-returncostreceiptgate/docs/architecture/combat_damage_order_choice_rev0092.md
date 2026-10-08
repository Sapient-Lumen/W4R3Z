# rev0092 combat damage order choice

rev0092 turns the common multi-blocker damage assignment order into a required, replayable active-player choice. Before this revision, `assign_combat_damage(...)` effectively routed damage through sorted object ids when more than one blocker was present. That was deterministic, but not a player choice.

The new seam adds `ActionKind::OrderCombatDamage` / `ChoiceRequestKind::OrderCombatDamage`, stores the chosen blocker order as `GameObject::combat_damage_ordered_blockers`, and includes that field in canonical StateCore hashing and snapshot serialization. Public legality runs through `can_order_combat_damage(...)`; application runs through `order_combat_damage(...)`; traces use `make_order_combat_damage_action(...)` and `combat_damage_order_from_action(...)`.

The gate is intentionally narrow: it fires after all blocker declarations are complete, while the game is still in `DeclareBlockers`, when the active player controls an attacking creature blocked by two or more creatures and no order has been chosen for that attacker. Ordinary priority is not exposed until the required order is committed.

A regression covers enumeration, `current_choice_request(...)`, failed premature `PassPriority`, action receipt projection, checkpoint replay, and trample assignment records. The chosen order is then consumed by combat damage assignment.

This is not a complete CR 509/510 implementation. Banding, multi-attacker combat-damage ordering, replacement/prevention ordering, and more complex damage-assignment constraints remain future work.
