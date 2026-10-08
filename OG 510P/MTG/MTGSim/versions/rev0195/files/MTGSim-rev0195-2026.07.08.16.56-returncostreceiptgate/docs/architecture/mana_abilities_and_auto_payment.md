# Mana abilities and auto-payment scaffold

Revision rev0024 turns the old single `tap_permanent_for_mana` helper into a small reusable mana-ability and payment seam. This is still a scaffold, but it removes a brittle testing pattern where scenarios had to manually tap mana sources before every paid cast or activation.

## C++ representation

`ManaAbilityDefinition` lives on `CardDefinition::mana_abilities`. A definition currently carries:

- a report-friendly `name`;
- a `tap_cost` flag;
- a compact `ManaPool produces` payload.

The legacy `CardDefinition::taps_for_mana` / `tap_mana_symbol` field remains as a compatibility shim and is exposed as mana ability index `1`. Explicit vector-defined mana abilities are indexed after that shim. This preserves older tests while letting future generated card definitions emit structured mana abilities.

## Public API seams

The new public helpers are:

```text
mana_ability_count(game, source)
can_activate_mana_ability(game, player, source, ability_index)
activate_mana_ability(game, player, source, ability_index)
can_pay_mana_cost_with_available_mana(game, player, cost)
pay_mana_cost_with_mana_abilities(game, player, cost)
```

`activate_mana_ability` mutates the mana pool immediately and does not create a stack object. Through rev0037, the auto-payment helper used a deterministic greedy plan: satisfy colored/colorless requirements first, then generic costs, without tapping the same source twice in one payment plan. rev0038 replaces that brittle planner with a bounded deterministic search over legal mana-ability activations. It still forbids tapping the same source twice in one payment plan, but it can choose a wider tap mode when a narrower colored mode would strand an unpaid generic component. The search prefers fewer activations, then less leftover mana, then less produced mana, then stable candidate order.

## Legal actions and ML shape

`ActionKind::ActivateManaAbility` and `LegalAction::mana_ability_index` let the action enumerator distinguish explicit mana abilities. The legacy `ActivateTapManaAbility` action is still emitted for old one-symbol tap sources. This makes action masks more stable for simulation: mana production can be represented either as explicit actions or as an internal payment plan when a spell or ability is otherwise castable.


## rev0038 non-greedy payment search

The riskiest prior behavior was not syntax; it was planner incompleteness. A permanent with two tap-cost mana modes, such as `W` and `WG`, could make a `1W` spell castable only through the wider `WG` mode. The old greedy colored-first strategy could choose the narrow `W` mode, mark that source tapped for the plan, and then fail to pay the generic portion even though a legal plan existed.

`select_mana_ability_pay_plan` now performs a bounded exact search over the candidate activation set (the bounded search is deliberately small and deterministic). Candidate order remains deterministic, and each modeled mana ability can be used at most once in a plan. Tap-cost candidates from the same object are mutually exclusive, preserving the important physical-source constraint. The selected plan is emitted through `mana_auto_plan` before activations, making planner choices auditable in scenario and fuzz traces.

## Scenario DSL

The scenario runner adds fixture syntax for explicit mana abilities and mana-pool assertions:

```text
card Prism artifact 0 0 mana_ability=Make_Two:tap:C2
card Bolt instant 0 0 cost=R effect=damage:3 target=any color=R
create 1 Prism battlefield controller=1
create 2 Bolt hand controller=1
ready 1
action mana 1 1 ability=1
expect_mana 1 C 2
```

`action cast_paid` and `action activate` can now succeed through auto-payment if legal untapped mana sources exist.

## Rule mapping

The scaffold is aimed at the shape of rules `601.2g`, `601.2h`, `605.1a`, `605.3a`, `605.3b`, and `405.6c`: mana abilities can be activated during cost payment, they resolve immediately, and payment then consumes the resulting mana. MTGSim keeps this as metadata-plus-tests rather than bundling rules text.

## Limitations

This is not a full mana engine. Missing pieces include triggered mana abilities, mana abilities with non-tap costs, choice-heavy mana production, spending restrictions, hybrid/Phyrexian/snow symbols, cost reducers/increasers, alternate/additional costs, recursive mana activation edge cases, full illegal-action rollback, player prompts, and Oracle-text-derived mana abilities.

## rev0039 sacrifice-as-cost spine

rev0039 adds the first non-mana spell-cost seam. `SacrificeCostDefinition` lives on `CardDefinition::sacrifice_cost` and currently represents a deterministic fixture cost of “sacrifice N permanents matching this type mask.” The engine checks this alongside mana before a paid cast is listed as legal. During payment, it selects matching permanents from the caster’s battlefield order and routes them through `sacrifice_permanent`, so the cost payment produces the same zone-change and dies-trigger events as effect-based sacrifice.

The important stack consequence is now tested: if a creature sacrificed to cast a spell has a dies trigger, the spell is placed on the stack, the pending trigger gate prevents priority from advancing, and the trigger is put on the stack above the original spell before either object resolves. This is deliberately a narrow casting-cost spine, not a full additional-cost choice engine. Activated-ability sacrifice costs, discard costs, alternate costs, cost increases/reductions, rollback of partially paid complex costs, player-selected sacrifice choices, and Oracle-derived cost parsing remain future work.

## rev0040 activated sacrifice-cost bridge

rev0040 carries the same `SacrificeCostDefinition` into `ActivatedAbilityDefinition::sacrifice_cost`. The activated-ability path now checks sacrifice availability before enumeration, creates the synthetic activated-ability stack object, and pays the selected sacrifice cost through `sacrifice_permanent(...)`. That ordering matters for source-sacrifice abilities: the source can move to the graveyard as a cost while the already-created stack object remains available to resolve, and any dies-trigger events from the sacrificed source are queued above that ability through the same pending-trigger gate. This is still a fixture-oriented deterministic selection, not player choice or rollback.

## rev0041 paid-cast ordering correction

rev0041 fixes an important casting-order bug in the sacrifice-cost spine. Paid spell helpers now move the spell from hand to the stack before automatic mana payment and sacrifice-cost payment. Targeted and modal helpers also store the chosen target/mode on the stack object before costs are paid, then `finish_paid_cast_after_costs(...)` restores priority to the next player after immediate mana abilities and cost helpers have mutated state.

The new regression intentionally targets a creature, then sacrifices that same creature as the spell's deterministic sacrifice cost. The spell remains on the stack, but its stored `TargetRef` becomes stale before resolution, so the targeted effect does nothing and the spell still leaves the stack normally. This catches the prior false confidence where the final stack shape looked right even though the internal casting sequence was wrong.

Limitations remain: the engine still does not implement full announcement rollback, player-selected sacrifice choices, alternate-cost prompts, cost reducers/increasers, or spending restrictions. The value of this revision is narrower but structural: the stack object now exists while costs are paid, which future replacement, trigger, LKI, and target-choice work can rely on.

## rev0042 activated-cost ordering correction

rev0042 extends the stack-first cost-payment correction from paid spells to activated abilities. Activated abilities using automatic mana payment now create their synthetic stack object before `mana_auto_plan` and before any selected mana source is tapped. This matters because target/mode/source snapshots must exist before the payment steps that can tap permanents, move permanents, or queue triggered abilities.

The scope remains intentionally narrow: the engine still preflights costs and does not implement general rollback for arbitrary cost bundles. The progress is that both paid spells and ordinary activated abilities now have the same durable ordering anchor for future cost components.

## rev0062 typed mana-change records

rev0062 turns the mana scaffold's highest-risk mutation path into typed evidence. Mana production, explicit payment, automatic payment, and pool emptying now emit `ManaChangeRecord` payloads linked through `EventRecordKind::ManaChange`. Each record preserves the player, before/after pool snapshots, added or spent mana, paid `ManaCost`, source object, source zone-change index, mana-ability index, and an `auto_payment` flag.

This does not make the mana engine complete. It deliberately leaves spending restrictions, hybrid/Phyrexian/snow symbols, cost modification, rollback, and choice-heavy production for later. The point of this slice is that future cost work can attach to a replayable transaction seam instead of reverse-engineering mana changes from human log strings.

