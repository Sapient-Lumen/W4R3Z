#include "mtgsim/rules.hpp"

#include <algorithm>
#include <unordered_map>
#include <unordered_set>

namespace mtgsim {
namespace {

const std::vector<RuleModuleDescriptor>& modules() {
    static const std::vector<RuleModuleDescriptor> value = {
        {"core.game", "Game/state identity", "100-123,105,109,202", "GameState, PlayerState, ObjectId, source color/characteristic metadata, EventRecord typed event spine, PlayerState::mulligans_taken", true, {}},
        {"core.zones", "Zones and movement", "400-408,406", "Zone enum, exile zone containers, move_object, ZoneChangeRecord movement log, ZoneChangeReplacementRecord applied replacement links, EventRecord links, validation", true, {"core.game"}},
        {"core.tokens", "Token lifecycle scaffold", "111,406,701.7,701.13,701.21,704.5d", "GameObject::token/ceased_to_exist, create_token/create_tokens, exile/sacrifice helpers, token ceases-to-exist SBA cleanup", true, {"core.game", "core.zones"}},
        {"core.draw", "Draw-card scaffold", "121", "draw_card, DrawRecord, take_mulligan redraw DrawRecord range", true, {"core.game", "core.zones"}},
        {"core.mana", "Mana pool and payment scaffold", "106", "ManaPool, ManaCost, add/pay/clear mana, available-mana payment predicates, bounded auto-payment search, Paid ManaChangeRecord auto-payment plan count/hash evidence", true, {"core.game"}},
        {"core.timing", "Spell timing permissions scaffold", "117.1a,304,307,702.8", "can_cast_spell_now, instant timing, sorcery-speed main-phase/empty-stack gate, flash permission", true, {"core.game", "core.zones", "core.priority", "core.keywords"}},
        {"core.land_play", "Land-play special action scaffold", "116,305.1,305.2,305.2a,305.2b,305.3,305.9", "PlayerState land-play counters, can_play_land, play_land_from_hand, ActionKind::PlayLand", true, {"core.game", "core.zones", "core.timing"}},
        {"core.targets", "Targets scaffold", "115", "TargetRef, TargetStackObject, source-object target legality, protection/hexproof/shroud battlefield filtering, object identity snapshots, multi-target vectors, enumerate_legal_targets", true, {"core.game", "core.zones", "core.keywords"}},
        {"core.counters", "Counters scaffold", "122", "CounterKind, CounterSet, add/remove counters, effective P/T helpers, counter-pair SBA hook", true, {"core.game", "core.zones"}},
        {"core.planeswalkers", "Planeswalker/loyalty scaffold", "306,306.5,306.6,306.8,606,606.3,606.4,606.6,704.5i", "CardDefinition::printed_loyalty, LoyaltyAbilityDefinition, planeswalker attack targets, damage-to-loyalty, zero-loyalty SBA hook, loyalty activation stack objects", true, {"core.game", "core.zones", "core.counters"}},
        {"core.activated", "Activated ability scaffold", "602,602.1,602.2,602.2a,602.2b,602.2g,117.1b,601.2g", "ActivatedAbilityDefinition, CardDefinition::activated_abilities, can_activate_activated_ability, activate_activated_ability, synthetic activated ability stack objects before target/mana/tap/sacrifice/discard cost payment, LegalAction::ActivateActivatedAbility, auto mana payment for simple mana costs, sacrifice_cost and discard_cost payment for deterministic fixture activations", true, {"core.game", "core.zones", "core.priority", "core.mana", "core.mana_abilities", "core.targets", "core.summoning_sickness", "core.stack", "core.effects", "core.costs"}},
        {"core.battles", "Battle/defense/protector scaffold", "310,310.4,310.5,310.6,310.7,310.8,310.8b,310.8c,122.1g,704.5v", "CardDefinition::printed_defense, defense counters, battle protector metadata, battle attack targets, damage-to-defense, zero-defense SBA hook", true, {"core.game", "core.zones", "core.counters"}},
        {"core.keywords", "Keyword/static ability scaffold", "702,702.2,702.3,702.4,702.7,702.9,702.10,702.11,702.12,702.15,702.16,702.18,702.19,702.111,702.8", "CardDefinition::ability_mask, CardDefinition::protection_color_mask, object_has_ability, protection/flying/reach/vigilance/lifelink/deathtouch/first strike/double strike/trample/indestructible/haste/defender/hexproof/shroud/menace/flash hooks; object_has_ability observes attachment and static-effect granted/removed ability masks", true, {"core.game"}},
        {"core.types_colors", "Derived type/color characteristic scaffold", "105,109,205,613.1d,613.1e", "object_type_mask, object_has_type, object_color_mask, narrow static layer-4 type add/remove and layer-5 color set/add/remove seams", true, {"core.game"}},
        {"core.static_effects", "Static continuous-effect scaffold", "604,611,613,613.1d,613.1e,613.1f,613.1g,613.4b,613.4c", "StaticEffectDefinition, StaticEffectScope, source-on-battlefield applicability, layer-4-style type changes, layer-5-style color changes, layer-6-style keyword grants/removals, layer-7b-style base P/T setting, and layer-7c-style P/T modifiers feeding timestamp-aware derived characteristics, combat, and SBAs", true, {"core.game", "core.types_colors", "core.keywords", "core.counters"}},
        {"core.copy", "Copy-effect/copied-definition scaffold", "707,707.2,707.2b,613.1a,613.2a", "GameObject::has_copy_effect and copied_definition_index, object_copiable_definition_index, become_copy_of_permanent, layer-1a-style current-definition projection for derived type/color/ability/P/T helpers", true, {"core.game", "core.types_colors", "core.keywords"}},
        {"core.temporary_continuous", "Temporary continuous-effect scaffold", "611.2a,611.2c,613.7,514.2", "EffectKind::CreateContinuousEffect, ContinuousEffectDefinition, until-cleanup effects generated by resolving spells/abilities, locked target snapshots, cleanup expiry", true, {"core.game", "core.types_colors", "core.keywords", "core.static_effects", "core.effects", "core.cleanup"}},
        {"core.layer_timestamps", "Layer timestamp ordering scaffold", "613.7,613.7a,613.7b,613.7d,613.7e,613.9", "GameObject::layer_timestamp, GameState::next_layer_timestamp, timestamp-sorted static and generated continuous effect applications for narrow layer-4/type, layer-5/color, layer-6/ability, and layer-7b/base-P/T seams; attachment timestamp refresh", true, {"core.static_effects", "core.temporary_continuous", "core.attachments"}},
        {"core.layer_dependencies", "Layer dependency ordering scaffold", "613.8,613.8a,613.8b,613.8c", "StaticEffectDefinition::depends_on_effect_names, dependency-aware topological ordering over timestamp-sorted layer applications, deterministic timestamp fallback for dependency cycles, scenario/validation/card-catalog dependency metadata", true, {"core.static_effects", "core.layer_timestamps"}},
        {"core.control", "Control-changing scaffold", "108.4,109.4,110.2,613.1b", "gain_control_of_permanent, controller battlefield-container transfer, control-start timestamp refresh, combat metadata cleanup, controller-scoped static-effect recomputation", true, {"core.game", "core.zones", "core.summoning_sickness", "core.static_effects"}},
        {"core.attachments", "Aura/Equipment attachment scaffold", "301.5,303.4,303.4a,303.4b,303.4g,701.3,704.5m,704.5n", "AttachmentKind, attached_to metadata, can_attach_object/attach/detach helpers, Aura spell attachment, Equipment attach helper, attachment P/T and ability grants", true, {"core.game", "core.zones", "core.targets", "core.keywords"}},
        {"core.summoning_sickness", "Summoning sickness/control-start scaffold", "302.6", "PlayerState::turn_start_index, GameObject::controlled_since_turn_start_index, object_has_summoning_sickness", true, {"core.game", "core.zones", "core.keywords", "core.static_effects"}},
        {"core.damage", "Damage-marking scaffold", "120,306.8,310.6", "mark_damage, deal_damage_to_target, GameObject::damage_marked, planeswalker damage-to-loyalty, battle damage-to-defense, non-damageable object target gate, protection prevention, lifelink/deathtouch/indestructible damage hooks, DamageRecord/EventRecord links", true, {"core.game", "core.zones", "core.targets", "core.keywords", "core.planeswalkers"}},
        {"core.prevention", "Damage prevention / replacement-event scaffold", "614,615,616,701.19", "DamagePreventionShield, add_damage_prevention_shield choice-rank ordering, DamagePreventionRecord affected-player/candidate/pass evidence, regeneration shield hook, damage/destroy event hooks, requested-vs-final ZoneChangeRecord movement records, applied ZoneChangeReplacementRecord replacement-chain records", true, {"core.game", "core.targets", "core.damage"}},
        {"core.destroy", "Destroy/regeneration scaffold", "701.8,701.19,704.5f,704.5g,704.5h", "destroy_permanent, add_regeneration_shield, SBA destruction replacement, indestructible bypass", true, {"core.game", "core.zones", "core.damage", "core.prevention", "core.keywords"}},
        {"core.sba", "State-based actions scaffold", "704,704.5i,704.5v", "apply_state_based_actions, lethal damage, deathtouch lethal flag, zero-loyalty planeswalker cleanup, zero-defense battle cleanup, indestructible damage-destroy bypass, regeneration replacement for destroy SBAs, counter-pair cancellation, token cease cleanup, attachment cleanup", true, {"core.game", "core.draw", "core.damage", "core.counters", "core.keywords", "core.static_effects", "core.destroy", "core.attachments", "core.tokens", "core.planeswalkers", "core.battles"}},
        {"core.priority", "Priority scaffold", "117,117.3c", "pass_priority plus stack-placement priority retention after casting or activating spells/abilities", true, {"core.game"}},
        {"core.stack", "Stack resolution scaffold", "405,117.3c,601.2i,602.2,701.6", "cast_from_hand_to_stack, StackPlacementRecord stack-entry/activation audit trail, targetable stack objects, countered stack objects, trigger EventRecord stack links, cast_from_hand_to_stack_paying_mana_with_mode, resolve_top_of_stack", true, {"core.zones", "core.priority", "core.timing"}},
        {"core.modal", "Modal spell choice scaffold", "700.2,700.2a,700.2c,700.2f,115.8", "SpellModeDefinition, CardDefinition::modes, GameObject::chosen_mode_index, LegalAction::mode_index, selected-mode target and payload dispatch", true, {"core.stack", "core.targets", "core.effects", "core.costs"}},
        {"core.effects", "One-shot and continuous-effect creation scaffold", "608,310.6,700.2,611.2a,613.1a,613.1b,701.6,707", "EffectKind, targeted damage/draw/life/counter/destroy/regenerate/exile/create-token/gain-control/become-copy/create-continuous/counterspell resolution, selected modal spell payload dispatch, loyalty and activated ability payload resolution, plus Aura spell attachment resolution", true, {"core.stack", "core.targets", "core.damage", "core.prevention", "core.counters", "core.destroy", "core.attachments", "core.tokens", "core.planeswalkers", "core.control", "core.static_effects", "core.copy"}},
        {"core.triggers", "Triggered abilities scaffold", "603", "TriggerDefinition, PendingTrigger, TriggerRecord, created-token trigger payloads, put_pending_triggers_on_stack, triggered ability stack objects, queued-to-stack typed lifecycle records, EventRecord queue/stack links", true, {"core.game", "core.stack", "core.effects", "core.zones", "core.tokens"}},
        {"core.costs", "Cost payment / casting scaffold", "117,117.1a,508.1h,508.1i,508.1j,509.1d,509.1e,509.1f,601,601.2c,601.2g,601.2h,602.2b,700.2a", "pay_mana_cost, can_pay_mana_cost_with_available_mana, bounded pay_mana_cost_with_mana_abilities search, auto-payment plan count/hash evidence on Paid ManaChangeRecord, mana-only combat declaration costs, SacrificeCostDefinition/pay_sacrifice_cost, DiscardCostDefinition/pay_discard_cost, selected sacrifice/discard cost payment for spells and activated abilities, cast_from_hand_to_stack_paying_mana* stack-first ordering, activated ability stack-before-cost ordering, StackPlacementRecord and finish_paid_cast_after_costs priority retention", true, {"core.mana", "core.mana_abilities", "core.stack", "core.timing", "core.triggers", "core.targets"}},
        {"core.mana_abilities", "Mana ability scaffold", "605,605.1a,605.3a,605.3b,405.6c,601.2g", "ManaAbilityDefinition, CardDefinition::mana_abilities, can_activate_mana_ability, activate_mana_ability, bounded select_mana_ability_pay_plan, mana_auto_plan tracing, Paid ManaChangeRecord auto-payment plan counts and hash, pay_mana_cost_with_mana_abilities, ActionKind::ActivateManaAbility, legacy tap_permanent_for_mana wrapper", true, {"core.mana", "core.zones", "core.summoning_sickness"}},
        {"core.combat", "Combat declaration/damage scaffold", "506,508,508.1g,508.1h,508.1i,508.1j,509,509.1d,509.1e,509.1f,510,306.6,310.5,310.8,613.1b", "declare_attacker/declare_attackers, declare_blocker/declare_blockers, explicit empty declarations, max-satisfaction must-attack/must-block/must-be-blocked/all-able-blockers solver, narrow max attacker/blocker caps, cant_attack_alone/cant_block_alone/can_block_only_flying restrictions, mana-only attack/block declaration costs, assign_combat_damage, planeswalker/battle attack targets, blocked-attacker memory, effective-power combat math, attachment-granted P/T/ability bonuses, protection/flying/reach/vigilance/first strike/double strike/trample/menace hooks, regeneration removes combat metadata, combat metadata validation", true, {"core.game", "core.zones", "core.damage", "core.prevention", "core.counters", "core.keywords", "core.static_effects", "core.attachments", "core.summoning_sickness", "core.destroy", "core.sba", "core.planeswalkers", "core.battles", "core.costs", "core.mana_abilities"}},
        {"core.actions", "Player action enumeration scaffold", "117,601,602,605,115,305,506,509,603,606,702,310,700.2", "LegalAction, enumerate_legal_actions, apply_action, modal mode variants, land-play special actions, generic activated ability actions, explicit mana ability actions, source-aware target variants, planeswalker loyalty actions, keyword-aware combat, and pending-trigger expansion/gating", true, {"core.priority", "core.costs", "core.land_play", "core.mana_abilities", "core.activated", "core.targets", "core.combat", "core.triggers", "core.summoning_sickness", "core.planeswalkers", "core.battles", "core.modal"}},
        {"core.cleanup", "Cleanup-step scaffold", "514,514.2,701.9", "discard_down_to_max_hand_size, discard_card, DiscardRecord cleanup/choice evidence, until-cleanup continuous-effect expiry, marked-damage cleanup, regeneration-shield expiration", true, {"core.game", "core.zones", "core.damage", "core.destroy"}},
        {"core.untap", "Untap-step scaffold", "502", "untap_permanents", true, {"core.game", "core.zones"}},
        {"core.turn", "Turn structure scaffold", "500-514", "Step enum, advance_step, active-player turn wrap and land-play counter reset", true, {"core.priority", "core.draw", "core.sba", "core.cleanup", "core.mana", "core.untap", "core.land_play"}},
        {"future.effects", "Effects pipeline", "600-616", "full event/effect/replacement pipeline beyond current one-shot, modal, temporary continuous, activated, mana-ability payment, loyalty, triggered-ability, and structured zone-change/replacement/damage/trigger record scaffolds", false, {"core.game", "core.stack", "core.costs", "core.actions", "core.effects", "core.triggers", "core.summoning_sickness", "core.static_effects", "core.temporary_continuous", "core.copy", "core.control", "core.planeswalkers", "core.modal", "core.timing", "core.activated", "core.mana_abilities"}},
        {"future.layers", "Continuous effects and layers", "613", "full layer engine with automatic dependency detection and all missing layer categories; rev0032 adds explicit dependency metadata and cycle-safe ordering over the narrow layer projection seams", false, {"future.effects", "core.counters", "core.types_colors", "core.static_effects", "core.temporary_continuous", "core.copy", "core.layer_timestamps", "core.layer_dependencies"}},
        {"future.formats", "Variant/format modules", "800-905", "format module registry", false, {"core.game"}},
    };
    return value;
}

enum class VisitState { Unvisited, Visiting, Done };

bool visit(std::string_view id,
           const std::unordered_map<std::string_view, const RuleModuleDescriptor*>& by_id,
           std::unordered_map<std::string_view, VisitState>& state) {
    const auto it_state = state.find(id);
    if (it_state != state.end()) {
        if (it_state->second == VisitState::Visiting) {
            return false;
        }
        if (it_state->second == VisitState::Done) {
            return true;
        }
    }

    const auto it = by_id.find(id);
    if (it == by_id.end()) {
        return false;
    }

    state[id] = VisitState::Visiting;
    for (const auto dependency : it->second->dependencies) {
        if (!visit(dependency, by_id, state)) {
            return false;
        }
    }
    state[id] = VisitState::Done;
    return true;
}

} // namespace

const std::vector<RuleModuleDescriptor>& builtin_rule_modules() {
    return modules();
}

const RuleModuleDescriptor* find_rule_module(std::string_view id) noexcept {
    const auto& all = modules();
    const auto it = std::find_if(all.begin(), all.end(), [id](const RuleModuleDescriptor& module) {
        return module.id == id;
    });
    return it == all.end() ? nullptr : &*it;
}

bool rule_module_graph_is_acyclic() {
    std::unordered_map<std::string_view, const RuleModuleDescriptor*> by_id;
    by_id.reserve(modules().size());
    for (const auto& module : modules()) {
        if (!by_id.emplace(module.id, &module).second) {
            return false;
        }
    }

    std::unordered_map<std::string_view, VisitState> state;
    state.reserve(modules().size());
    for (const auto& module : modules()) {
        if (!visit(module.id, by_id, state)) {
            return false;
        }
    }
    return true;
}

std::vector<std::string_view> executable_rule_module_ids() {
    std::vector<std::string_view> out;
    for (const auto& module : modules()) {
        if (module.executable) {
            out.push_back(module.id);
        }
    }
    return out;
}

} // namespace mtgsim
