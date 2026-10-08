# Effects and targets through rev0044

rev0007 added the first target/effect pipeline. rev0009 refactored simple effect execution so spells and triggered abilities share payload machinery. rev0014 adds source-aware target legality so hexproof/shroud-style filters are checked during both legal-action generation and resolution.

## Current target model

- `TargetRef` can point to a player or object.
- `TargetMask` describes whether a spell/ability can target players, battlefield objects, and as of rev0044 stack objects.
- `target_ref_is_legal_for_source` adds source-controller context for battlefield hexproof/shroud scaffolds.
- `TargetRef::object_zone_change_index` stamps object identity for stack-stored choices.
- Stack objects may carry a target vector plus the legacy primary target view.
- Validation rejects target metadata outside the stack, target-count mismatches, duplicate choices, and missing object identity stamps on stack-stored object targets.

## Current effect model

`EffectKind` is still a compact enum/amount scaffold, not an Oracle instruction engine. Executable slices include targeted damage, gain life, draw cards, counter placement, destroy/regenerate, exile, token creation, gain control, copy/become-copy, temporary continuous-effect creation, and rev0044 stack-object counterspell resolution. Unsupported combinations log scaffold events rather than claiming full card-text behavior.

## rev0009 refactor

The shared effect payload dispatcher accepts controller, source, optional target, effect kind, and amount. That lets simple spells and synthetic triggered abilities resolve through the same path.

## rev0014 source-aware target refactor

Paid targeted casting now enumerates targets with `enumerate_legal_targets_for_source`. Resolution rechecks the same helper before applying the effect. That catches a narrow but important class of bugs: a target that was legal at cast time but gains hexproof or shroud before resolution should produce no effect in this scaffold.

The generic `target_ref_is_legal` still exists for non-spell/non-ability machinery such as direct validation and simple prevention-shield setup.

## Known gaps

Missing features include target groups with different restrictions, explicit "same target may be chosen more than once" text, target changes, richer modal text beyond the rev0021 one-mode scaffold, self-replacement, linked abilities, target restrictions from real Oracle text, full protection/ward, target-changing effects, multiple target qualities, and full shroud/hexproof edge cases.

See also `prevention_and_replacement.md` for the rev0010 damage-event prevention hook that now sits between targeted/combat damage events and actual life-loss/marked-damage application.


## rev0015 source-object target legality

Target legality now has a source-object overload. That matters for effects whose legality depends on source characteristics, such as protection from red. Casting and resolution use the same helper so a target can become illegal before resolution through source-aware rules. The current implementation is still single-target only and does not model target changing, target uniqueness, modes, ward costs, or Oracle-derived restrictions.

## rev0016 destroy/regeneration effects

`EffectKind` now includes `DestroyPermanent` and `RegeneratePermanent`. The shared payload dispatcher handles their single-target object case through the same source-aware target legality helper used by damage, counters, protection, hexproof, and shroud. That keeps target legality in one place while letting effect execution branch on a small enum.

The destroy effect calls `destroy_permanent(...)`. The regeneration effect creates a finite object-local regeneration shield. Unsupported target shapes continue to log scaffold/no-op events rather than pretending to implement full card text.

## rev0018 token/exile payloads

`EffectKind` now includes `CreateToken` and `ExilePermanent`. Both use the shared effect payload path that already handles damage, counters, destroy, regeneration, and simple triggered abilities. `CreateToken` consumes `effect_amount` plus `created_token_definition_index`; `ExilePermanent` uses the existing single-target stack-object target list and source-aware target legality recheck.

This is still not a full instruction engine. After rev0021 the current payload model can represent one selected spell mode, but it still cannot represent multiple simultaneous modes, arbitrary choices, multiple target groups, linked exile durations, token-copy characteristics, or sacrifice-as-cost. It is a narrow seam that keeps new effects from bypassing validation, zone movement, and the scenario harness.


## rev0019 loyalty payloads and planeswalker damage

The one-shot effect path now also carries synthetic loyalty ability payloads. Damage to a battlefield planeswalker removes loyalty counters through the shared target/damage path. This is deliberately narrow: it does not yet implement full planeswalker redirection/history, replacement ordering, or Oracle-derived target restrictions.


## rev0020 battle damage target behavior

The shared target/damage path can now send object-targeted damage to battles. Battle damage removes defense counters rather than marking creature damage or changing player life.


## rev0021 modal payload dispatch

Modal spells no longer have to use a single card-level `effect_kind`. A stack object can carry `chosen_mode_index`, and resolution selects the effect payload from `CardDefinition::modes`. Targeted mode resolution still uses the source-aware target recheck path; untargeted modes resolve without target metadata. The implementation remains single-mode and single-target-group only.
## rev0029 create-continuous payload

`EffectKind::CreateContinuousEffect` is now a resolver payload. Targeted temporary effects recheck source-aware target legality, then create a timestamped continuous-effect record locked to the selected object. The resolved spell still leaves the stack normally; the generated effect lives in `GameState::continuous_effects` until cleanup.

## rev0037 object target identity / zone-change snapshots

Object targets chosen for stack objects now carry an object target identity stamp: `TargetRef::object_zone_change_index`. The stamp records the target object's zone-change index at choice time for paid casts, modal casts, activated abilities, loyalty abilities, and simple targeted triggered abilities.

Resolution-time target legality rejects a stamped object target when the current object's zone-change index no longer matches. This means a target that leaves and re-enters before resolution is treated as a different object, even if a compact fixture reuses the same internal `ObjectId`. The scenario `target_blink_identity_stale_before_resolution.mtgscn` covers the bug class by casting a bolt at a creature, moving that creature to exile and back, and proving the spell no longer damages it.

A zero stamp remains a wildcard for transient refs such as UI selections, combat helpers, attachment lookups, direct API probes, and old non-stack scaffolds. Validation emits `target.missing_object_lki` when a stack object carries an unstamped object target so the missing last-known-identity metadata is visible without making unrelated fixture helpers brittle.



## rev0043 multi-target partial resolution

rev0043 changes the target model from an API that mostly exposed one `TargetRef` into a small target-vector seam. Definitions can declare `target_count`; legal actions can carry `LegalAction::targets`; scenario fixtures can use `TARGETS*COUNT` and `targets=object:3,object:4`; and the engine can enumerate deterministic target sets with `enumerate_legal_target_sets_for_source_object(...)`. The older single `LegalAction::target` remains as the primary/legacy target for narrow callers.

Resolution now distinguishes all-targets-illegal from partial-target legality. If every stored target is illegal at resolution, the effect payload is skipped and `resolve_spell_no_legal_targets` / `resolve_ability_no_legal_targets` is logged. If at least one target remains legal, the shared effect payload applies only to legal targets and logs `resolve_spell_partial_legal_targets` / `resolve_ability_partial_legal_targets` before applying the legal portion. This is a 608.2b-oriented scaffold, not a full Oracle instruction engine: it still treats the target list as one homogeneous group and disallows duplicate target identities in this initial target-set enumerator.

Validation now audits stack target counts and duplicate choices (`target.count_mismatch`, `target.duplicate_choice`) so a stack object cannot silently carry the wrong number of targets for its selected card or mode.


## rev0044 stack-object targets and counterspell scaffold

rev0044 extends `TargetMask` beyond players and battlefield permanents with `TargetStackObject`. Legal target enumeration now includes objects in `game.stack`, chosen stack targets receive the same `TargetRef::object_zone_change_index` identity stamp as battlefield object targets, and resolution rechecks that stamp before applying an effect.

`EffectKind::CounterSpell` is the first consumer of this stack-object target seam. A targeted counterspell effect can target a spell object on the stack, move that target spell to its owner's graveyard, log `counter_spell`, and prevent the target spell payload from resolving because the object is no longer on the stack when its old stack entry is encountered. Synthetic ability objects are routed to exile and log `counter_ability` in this narrow scaffold.

The target legality refactor deliberately keeps battlefield-only filters scoped to battlefield objects: protection, shroud, and hexproof checks still protect battlefield targets, while stack-object targets use stack membership plus object identity. This avoids treating a spell on the stack as if it were a permanent for keyword filtering.

Scenario fixtures can now use `stack`, `spell`, or `stack_object` target masks and `target=stack:N` / `target=s:N` action choices. `expect_event_count KIND COUNT` was added so regressions can prove that a countered stack object never reaches its payload event. The regression `stack_counterspell_targets_stack_object.mtgscn` casts a damage spell, counters that stack object, and asserts no `damage_player` event occurs.

Current limits: this is not a full countering engine. It does not yet implement "can't be countered," refund/illegal-target nuances beyond the existing stack skip, spell copies, replacement effects that modify countering, target groups with independent restrictions, or real Oracle-derived counterspell text. It is intentionally the smallest stack-targetable seam that can support later 405/608/701-style work without bypassing the shared target and resolution path.

## rev0050 stack-resolution records and late Aura target failure

rev0050 adds `StackResolutionRecord` and `GameState::stack_resolution_records` as the typed companion to stack-object resolution. The record snapshots the resolving stack object, controller, payload, chosen targets, target-count requirements, late legal-target count, failure flags, outcome, stack-zone identity, stack-leave `ZoneChangeRecord` link, and final zone immediately after resolution.

This closes a high-risk CR 608.2b seam. Resolution-time target checks are now visible as typed data rather than only string events. Aura spells are included in the required-target calculation even when their effect payload is `EffectKind::None`; an Aura whose enchant target is illegal at resolution records outcome `NoLegalTargets`, emits `resolve_aura_no_legal_enchant`, and moves directly from stack to owner graveyard without a temporary battlefield transit.

The record is intentionally a resolution audit spine, not a new Oracle text engine. It makes no claims about target-changing effects, fizzle variants beyond current scaffolds, or full attachment restrictions, but it gives future effect payloads and agent/replay consumers a durable place to observe why a stack object resolved, failed, or left the stack.

## rev0173 target-legality receipts

rev0173 promotes the CR 608.2b late target check from aggregate `StackResolutionRecord` counts into ordered per-target `TargetResolutionCheckRecord` receipts. Each chosen target now records the source controller, legal/illegal result, failure kind, and object zone/zone-change identity observed when resolution begins.

The resolver now computes that check set once, derives `legal_targets_on_resolution`, and feeds only those legal targets to `apply_effect_payload(...)`. Targeted effect branches no longer perform their own second legality scan while applying payloads. This makes partial resolution replayable as a single target-legality transaction boundary: auditors can see the target that failed because it was in the graveyard, the target that failed because its object identity changed after a blink, and the target that was legal before lethal damage or other payload movement changed the later state.

Current failure kinds remain scaffold-level: empty target, disallowed target kind, missing/lost player, missing object, object zone not allowed, object zone-change identity mismatch, shroud, hexproof, and protection. The model still does not implement target-changing effects, independent target groups, ward, arbitrary Oracle target restrictions, or duplicate-target exceptions.
