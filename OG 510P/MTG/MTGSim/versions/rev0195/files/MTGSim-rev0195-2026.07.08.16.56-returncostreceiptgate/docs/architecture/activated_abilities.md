# Activated abilities scaffold

Revision rev0023 adds the first generic non-mana activated ability path. This is intentionally narrow, but it is a major extensibility seam because it makes abilities data-bearing objects instead of one-off engine branches.

## C++ representation

`ActivatedAbilityDefinition` lives on `CardDefinition::activated_abilities`. Each definition carries:

- `name` for reports, scenarios, and action labels;
- `mana_cost` for simple mana payment;
- `tap_cost` for `T:`-style activation gates;
- `sacrifice_cost` for the rev0040 narrow fixture cost “sacrifice N permanents matching a type mask”;
- `sorcery_speed` as a local permission/restriction flag;
- `effect_kind`, `effect_amount`, `effect_counter_kind`, `target_mask`, and `created_token_definition_index` so activated abilities resolve through the same effect payload path as spells, modal spells, loyalty abilities, and triggered abilities.

This is not Oracle parsing. It is a structured fixture format that future generated card definitions can target.

## Activation flow

The public API is:

- `can_activate_activated_ability(game, controller, object, ability_index, target)`;
- `activate_activated_ability(game, controller, object, ability_index, target)`.

The legality helper checks priority, controller, battlefield presence, ability index, target legality, mana availability, tap-cost availability, sacrifice-cost availability, summoning sickness for creature tap costs, and the optional sorcery-speed gate. Activation now creates the synthetic stack object first, records any chosen target on that stack object, and only then pays automatic mana, tap, and sacrifice costs. Creating the stack object before costs lets a fixture model an ability that sacrifices its own source: the ability remains on the stack while any resulting dies trigger is queued for the pending-trigger gate.

The synthetic stack object stores the chosen target and copies the source's color/ability metadata into the stack definition. On resolution, `resolve_top_of_stack` calls the shared effect payload machinery. This preserves one resolver seam rather than adding an activated-ability-only effect switch. rev0042 adds explicit `choose_target` tracing for activated abilities so event-order tests can prove target choice is locked before activation costs are paid.

## Legal actions and ML shape

`LegalAction` now has `ability_index` in addition to `mode_index` and `target`. `enumerate_legal_actions` emits one action per legal target variant, so a simulator can distinguish:

```text
ActivateActivatedAbility(source=X, ability_index=1, target=player:1)
ActivateActivatedAbility(source=X, ability_index=1, target=player:2)
```

That matters for MCTS, batch simulation, and ML action masks. The action remains compact enough to serialize through Python harness reports later.

## Scenario DSL

The scenario DSL adds card options and actions:

```text
card Spark_Mage creature 1 1 activated=Ping:R:tap:damage:1:any
card Token_Engine artifact 0 0 activated=Make_Servo:0:notap:create_token:1:1:sorcery
card Blood_Celebrant artifact,creature 1 1 activated=Blood_Rite:-:no_tap:gainlife:1:none:sac=1,creature
action activate 1 1 ability=1 target=object:2
expect_actions 1 activate 4
```

The current grammar intentionally supports only simple mana costs, optional tap costs, optional sorcery-speed restriction, one optional sacrifice-cost suffix, one target group, and one effect payload.

## rev0040 activated sacrifice costs

rev0040 generalizes the rev0039 `SacrificeCostDefinition` from paid spells to activated abilities. `ActivatedAbilityDefinition::sacrifice_cost` is checked in `can_pay_activated_ability_costs(...)`, selected deterministically from the controller's battlefield, and paid through the same `sacrifice_permanent(...)` lifecycle path used by effect-based sacrifice. The focused regression intentionally lets the source permanent sacrifice itself to pay for its own ability. The synthetic ability object is already on the stack, the source moves to graveyard, the self-dies trigger is queued, and the pending-trigger action must put that trigger above the activated ability before priority can advance.

This remains a narrow cost spine, not a complete rollback/choice engine. The useful step is that spell and activated-ability costs now share the same sacrifice lifecycle and trigger-ordering seam.

## Limitations

This is not the full rule-602 engine. Missing pieces include a typed ordered list of arbitrary cost components, discard/life/untap-symbol costs, variable costs, cost reductions/increases, full rollback of partially paid complex activations, player-selected sacrifice choices, activation restrictions from Oracle text, target groups, modes on activated abilities, activated mana abilities beyond the existing tap-for-mana helper, split second, ability copying, complete last-known-information, and replacement/prevention ordering around activation.


## rev0024 cost-payment refactor

Activated abilities still resolve through synthetic stack objects, but simple mana costs now use `pay_mana_cost_with_mana_abilities(...)`. That gives activated abilities the same narrow rule-601/602/605 cost-payment seam as spells: available mana is checked first, then eligible modeled mana abilities may be activated before the mana component is paid. The scaffold remains intentionally limited to simple mana payloads and does not yet support nonmana costs beyond the existing tap-cost flag.


## rev0040 implementation note

The new scenario fixture `activated_sacrifice_cost_source_lki_stack_order.mtgscn` is deliberately small: it proves that an activated ability can pay a sacrifice cost using its own source, that the source leaves the battlefield, that the synthetic stack object survives independently, and that the dies trigger created during cost payment resolves above the ability.

## rev0042 activated-cost ordering correction

rev0042 fixes the same class of ordering bug for activated abilities that rev0041 fixed for paid spells. The previous path still paid automatic mana and tap costs before the synthetic ability object existed, even though the self-sacrifice fixture only proved the stack object existed before the sacrifice component. `activate_activated_ability(...)` now creates the stack object and records target choice before automatic mana planning, tap costs, and sacrifice costs.

The new fixture targets the source with its own activated ability, then sacrifices that source as a cost. The ability remains on the stack, but the stored object target becomes stale before resolution, proving the activation process has locked the target while still honoring resolution-time legality. Existing mana-cost and tap-cost activated ability tests now also assert that `activated_ability_put_on_stack` precedes `mana_auto_plan` and `tap` events.

## rev0055 stack-placement audit records

rev0055 adds `StackPlacementRecord` so casting and activation completion are no longer audited only through string events. A record is emitted when a spell card or synthetic activated/loyalty ability is placed on the stack. It snapshots the source object, stack object, source zone-change identity, chosen targets, stack size before/after, paid cost flags such as `tap_cost_paid`, and the priority handoff fields `priority_before` and `priority_after`.

The important correction is priority ownership after the action completes. Spell casts, activated abilities, and loyalty abilities now leave priority with the acting controller; opponents receive priority only after that player passes. Validation rejects a `StackPlacementRecord` whose `priority_after` is not the controller, or whose cost/target/stack-zone metadata contradicts the placement kind.
