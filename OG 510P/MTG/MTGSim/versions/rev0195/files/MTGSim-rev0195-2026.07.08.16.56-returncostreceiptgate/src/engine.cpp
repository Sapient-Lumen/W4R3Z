#include "mtgsim/engine.hpp"

#include "mtgsim/rng.hpp"

#include <algorithm>
#include <charconv>
#include <cstddef>
#include <functional>
#include <initializer_list>
#include <cassert>
#include <sstream>
#include <stdexcept>
#include <string_view>
#include <type_traits>
#include <unordered_map>
#include <utility>

namespace mtgsim {

bool discard_card_for_reason(GameState& game, PlayerId player_id, ObjectId object_id, DiscardRecordKind kind);

namespace {

struct EventRecordLinks {
    EventRecordKind kind = EventRecordKind::Log;
    ObjectId object{};
    u64 object_zone_change_index = 0;
    PlayerId player{};
    TargetRef target{};
    u32 choice_mode_index = 0;
    u64 choice_mode_contract_hash = 0;
    u32 choice_target_count = 0;
    u64 choice_target_set_hash = 0;
    u32 zone_change_record_index = 0;
    u32 zone_replacement_record_index = 0;
    u32 damage_record_index = 0;
    u32 damage_prevention_record_index = 0;
    u32 life_change_record_index = 0;
    u32 mana_change_record_index = 0;
    u32 counter_change_record_index = 0;
    u32 discard_record_index = 0;
    u32 trigger_record_index = 0;
    u32 stack_placement_record_index = 0;
    u32 stack_resolution_record_index = 0;
    u32 priority_transition_record_index = 0;
    u32 state_based_action_record_index = 0;
    u32 combat_declaration_record_index = 0;
    u32 combat_damage_assignment_record_index = 0;
    u32 mana_payment_plan_record_index = 0;
    u32 draw_record_index = 0;
    u32 mulligan_record_index = 0;
    u32 mulligan_keep_record_index = 0;
    u32 paid_action_declaration_record_index = 0;
    u32 paid_action_transaction_record_index = 0;
};

void record_event_with_links(GameState& game, std::string kind, std::string detail, EventRecordLinks links);
void record_damage_prevention_change(GameState& game, DamagePreventionRecord record, std::string log_kind, std::string detail);
void record_discard_record(GameState& game, DiscardRecord record);
void link_damage_prevention_record_range_to_damage(GameState& game, u32 first_record_index, u32 record_count, u32 damage_record_index);
void link_life_change_record_range_to_damage(GameState& game,
                                             u32 first_record_index,
                                             u32 record_count,
                                             u32 damage_record_index,
                                             ObjectId damage_source,
                                             u64 damage_source_zone_change_index,
                                             TargetRef damage_target,
                                             bool source_had_lifelink);
void record_object_counter_change(GameState& game,
                                  ObjectId object_id,
                                  CounterKind counter_kind,
                                  CounterChangeKind change_kind,
                                  u32 amount,
                                  u32 before,
                                  u32 after,
                                  std::string log_kind,
                                  std::string detail,
                                  ObjectId source = {},
                                  bool damage_result = false,
                                  u32 zone_change_record_index = 0,
                                  bool cost_payment = false,
                                  bool zone_change_cleanup = false);

void record_player_counter_change(GameState& game,
                                  PlayerId player_id,
                                  CounterKind counter_kind,
                                  CounterChangeKind change_kind,
                                  u32 amount,
                                  u32 before,
                                  u32 after,
                                  std::string log_kind,
                                  std::string detail);

class StableHasher {
public:
    void add_u64(u64 value) noexcept {
        value += 0x9e3779b97f4a7c15ULL;
        value = (value ^ (value >> 30U)) * 0xbf58476d1ce4e5b9ULL;
        value = (value ^ (value >> 27U)) * 0x94d049bb133111ebULL;
        value ^= value >> 31U;
        state_ ^= value + 0x9e3779b97f4a7c15ULL + (state_ << 6U) + (state_ >> 2U);
    }

    void add_bool(bool value) noexcept { add_u64(value ? 1U : 0U); }
    void add_size(std::size_t value) noexcept { add_u64(static_cast<u64>(value)); }
    void add_string(std::string_view value) noexcept {
        add_size(value.size());
        u64 chunk = 0;
        u32 shift = 0;
        for (const char raw : value) {
            const auto c = static_cast<unsigned char>(raw);
            chunk |= static_cast<u64>(c) << shift;
            shift += 8U;
            if (shift == 64U) {
                add_u64(chunk);
                chunk = 0;
                shift = 0;
            }
        }
        if (shift != 0U) {
            add_u64(chunk);
        }
    }

    [[nodiscard]] u64 value() const noexcept { return state_; }

private:
    u64 state_ = 0xcbf29ce484222325ULL;
};

void hash_into(StableHasher& h, bool value) noexcept { h.add_bool(value); }
void hash_into(StableHasher& h, u32 value) noexcept { h.add_u64(value); }
void hash_into(StableHasher& h, u64 value) noexcept { h.add_u64(value); }
void hash_into(StableHasher& h, std::int32_t value) noexcept { h.add_u64(static_cast<u64>(static_cast<std::int64_t>(value))); }
void hash_into(StableHasher& h, const std::string& value) noexcept { h.add_string(value); }
void hash_into(StableHasher& h, PlayerId value) noexcept { h.add_u64(value.value); }
void hash_into(StableHasher& h, ObjectId value) noexcept { h.add_u64(value.value); }

#define MTGSIM_HASH_ENUM(value) h.add_u64(static_cast<u64>(value))

template <typename T>
void hash_vector(StableHasher& h, const std::vector<T>& values) noexcept {
    h.add_size(values.size());
    for (const auto& value : values) {
        hash_into(h, value);
    }
}

void hash_into(StableHasher& h, const ManaPool& value) noexcept {
    hash_into(h, value.white); hash_into(h, value.blue); hash_into(h, value.black);
    hash_into(h, value.red); hash_into(h, value.green); hash_into(h, value.colorless);
}

void hash_into(StableHasher& h, const ManaCost& value) noexcept {
    hash_into(h, value.generic); hash_into(h, value.white); hash_into(h, value.blue); hash_into(h, value.black);
    hash_into(h, value.red); hash_into(h, value.green); hash_into(h, value.colorless);
}

void hash_into(StableHasher& h, const CounterSet& value) noexcept {
    hash_into(h, value.plus_one_plus_one); hash_into(h, value.minus_one_minus_one);
    hash_into(h, value.loyalty); hash_into(h, value.defense); hash_into(h, value.charge);
}

void hash_into(StableHasher& h, TargetRef value) noexcept {
    MTGSIM_HASH_ENUM(value.kind);
    hash_into(h, value.player);
    hash_into(h, value.object);
    hash_into(h, value.object_zone_change_index);
}

std::uint64_t target_choice_set_hash_impl(const std::vector<TargetRef>& targets) noexcept {
    StableHasher h;
    hash_vector(h, targets);
    return h.value();
}

void hash_into(StableHasher& h, const TriggerDefinition& value) noexcept {
    MTGSIM_HASH_ENUM(value.event); MTGSIM_HASH_ENUM(value.effect_kind); hash_into(h, value.effect_amount);
    MTGSIM_HASH_ENUM(value.effect_counter_kind); hash_into(h, value.target_mask); hash_into(h, value.target_count);
    hash_into(h, value.created_token_definition_index); hash_into(h, value.exclude_source);
}

void hash_into(StableHasher& h, const LoyaltyAbilityDefinition& value) noexcept {
    hash_into(h, value.cost); MTGSIM_HASH_ENUM(value.effect_kind); hash_into(h, value.effect_amount);
    MTGSIM_HASH_ENUM(value.effect_counter_kind); hash_into(h, value.target_mask); hash_into(h, value.target_count);
    hash_into(h, value.created_token_definition_index);
}

void hash_into(StableHasher& h, const SpellModeDefinition& value) noexcept {
    hash_into(h, value.name); MTGSIM_HASH_ENUM(value.effect_kind); hash_into(h, value.effect_amount);
    MTGSIM_HASH_ENUM(value.effect_counter_kind); hash_into(h, value.target_mask); hash_into(h, value.target_count);
    hash_into(h, value.created_token_definition_index);
}

std::uint64_t mode_choice_contract_hash_impl(const SpellModeDefinition& mode) noexcept {
    StableHasher h;
    hash_into(h, mode);
    return h.value();
}

void hash_into(StableHasher& h, const ManaAbilityDefinition& value) noexcept {
    hash_into(h, value.name); hash_into(h, value.tap_cost); hash_into(h, value.produces);
}

void hash_into(StableHasher& h, const SacrificeCostDefinition& value) noexcept {
    hash_into(h, value.count); hash_into(h, value.required_type_mask);
}

void hash_into(StableHasher& h, const DiscardCostDefinition& value) noexcept {
    hash_into(h, value.count);
}

void hash_into(StableHasher& h, const LifeCostDefinition& value) noexcept {
    hash_into(h, value.amount);
}

void hash_into(StableHasher& h, const ReturnCostDefinition& value) noexcept {
    hash_into(h, value.count); hash_into(h, value.required_type_mask); hash_into(h, value.require_tapped);
}

void hash_sacrifice_cost_payment_identity(StableHasher& h, const SacrificeCostPaymentRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.payer); hash_into(h, value.source_object);
    hash_into(h, value.cost); hash_vector(h, value.selected_objects);
    hash_vector(h, value.selected_zone_change_indices_before);
    hash_into(h, value.first_zone_change_record_index); hash_into(h, value.zone_change_record_count);
}

void hash_into(StableHasher& h, const SacrificeCostPaymentRecord& value) noexcept {
    hash_sacrifice_cost_payment_identity(h, value);
    hash_into(h, value.payment_hash);
}

void hash_discard_cost_payment_identity(StableHasher& h, const DiscardCostPaymentRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.payer); hash_into(h, value.source_object);
    hash_into(h, value.cost); hash_vector(h, value.selected_cards);
    hash_vector(h, value.selected_zone_change_indices_before);
    hash_into(h, value.first_discard_record_index); hash_into(h, value.discard_record_count);
    hash_into(h, value.first_zone_change_record_index); hash_into(h, value.zone_change_record_count);
}

void hash_into(StableHasher& h, const DiscardCostPaymentRecord& value) noexcept {
    hash_discard_cost_payment_identity(h, value);
    hash_into(h, value.payment_hash);
}

void hash_life_cost_payment_identity(StableHasher& h, const LifeCostPaymentRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.payer); hash_into(h, value.source_object);
    hash_into(h, value.cost); hash_into(h, value.life_before); hash_into(h, value.life_after);
    hash_into(h, value.life_change_record_index);
}

void hash_into(StableHasher& h, const LifeCostPaymentRecord& value) noexcept {
    hash_life_cost_payment_identity(h, value);
    hash_into(h, value.payment_hash);
}

void hash_return_cost_payment_identity(StableHasher& h, const ReturnCostPaymentRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.payer); hash_into(h, value.source_object);
    hash_into(h, value.cost); hash_vector(h, value.selected_objects);
    hash_vector(h, value.selected_zone_change_indices_before);
    hash_into(h, value.first_zone_change_record_index); hash_into(h, value.zone_change_record_count);
}

void hash_into(StableHasher& h, const ReturnCostPaymentRecord& value) noexcept {
    hash_return_cost_payment_identity(h, value);
    hash_into(h, value.payment_hash);
}

void hash_loyalty_cost_payment_identity(StableHasher& h, const LoyaltyCostPaymentRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.payer); hash_into(h, value.source_object);
    hash_into(h, value.source_zone_change_index_before); hash_into(h, value.cost_delta);
    hash_into(h, value.loyalty_before); hash_into(h, value.loyalty_after);
    hash_into(h, value.counter_change_record_index);
}

void hash_into(StableHasher& h, const LoyaltyCostPaymentRecord& value) noexcept {
    hash_loyalty_cost_payment_identity(h, value);
    hash_into(h, value.payment_hash);
}

void hash_tap_cost_payment_identity(StableHasher& h, const TapCostPaymentRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.payer); hash_into(h, value.source_object);
    hash_into(h, value.source_zone_change_index_before); hash_into(h, value.tapped_before);
    hash_into(h, value.tapped_after); hash_into(h, value.tap_event_sequence);
}

void hash_into(StableHasher& h, const TapCostPaymentRecord& value) noexcept {
    hash_tap_cost_payment_identity(h, value);
    hash_into(h, value.payment_hash);
}

void hash_into(StableHasher& h, const ActivatedAbilityDefinition& value) noexcept {
    hash_into(h, value.name); hash_into(h, value.mana_cost); hash_into(h, value.sacrifice_cost); hash_into(h, value.discard_cost);
    hash_into(h, value.life_cost); hash_into(h, value.return_cost); hash_into(h, value.tap_cost); hash_into(h, value.sorcery_speed); MTGSIM_HASH_ENUM(value.effect_kind);
    hash_into(h, value.effect_amount); MTGSIM_HASH_ENUM(value.effect_counter_kind); hash_into(h, value.target_mask);
    hash_into(h, value.target_count); hash_into(h, value.created_token_definition_index);
}

void hash_into(StableHasher& h, const StaticEffectDefinition& value) noexcept {
    hash_into(h, value.name); hash_vector(h, value.depends_on_effect_names); MTGSIM_HASH_ENUM(value.scope);
    hash_into(h, value.affected_type_mask); hash_into(h, value.added_type_mask); hash_into(h, value.removed_type_mask);
    hash_into(h, value.sets_color); hash_into(h, value.set_color_mask); hash_into(h, value.added_color_mask);
    hash_into(h, value.removed_color_mask); hash_into(h, value.sets_power_toughness); hash_into(h, value.set_power);
    hash_into(h, value.set_toughness); hash_into(h, value.power_modifier); hash_into(h, value.toughness_modifier);
    hash_into(h, value.granted_ability_mask); hash_into(h, value.removed_ability_mask);
}

void hash_into(StableHasher& h, const ZoneChangeReplacementDefinition& value) noexcept {
    hash_into(h, value.name); MTGSIM_HASH_ENUM(value.scope); MTGSIM_HASH_ENUM(value.from_zone); MTGSIM_HASH_ENUM(value.to_zone);
    MTGSIM_HASH_ENUM(value.replacement_zone); hash_into(h, value.affected_type_mask); MTGSIM_HASH_ENUM(value.priority_tier); hash_into(h, value.choice_rank);
}

void hash_into(StableHasher& h, const CardDefinition& value) noexcept {
    hash_into(h, value.name); hash_into(h, value.type_mask); hash_into(h, value.printed_power); hash_into(h, value.printed_toughness);
    hash_into(h, value.printed_loyalty); hash_into(h, value.printed_defense); hash_into(h, value.mana_cost);
    hash_into(h, value.taps_for_mana); MTGSIM_HASH_ENUM(value.tap_mana_symbol); hash_vector(h, value.mana_abilities);
    MTGSIM_HASH_ENUM(value.effect_kind); hash_into(h, value.effect_amount); MTGSIM_HASH_ENUM(value.effect_counter_kind);
    hash_into(h, value.target_mask); hash_into(h, value.target_count); hash_into(h, value.created_token_definition_index);
    hash_into(h, value.trigger); hash_into(h, value.color_mask); hash_into(h, value.protection_color_mask); hash_into(h, value.ability_mask);
    hash_into(h, value.attacks_each_combat_if_able); hash_into(h, value.blocks_each_combat_if_able);
    hash_into(h, value.must_be_blocked_if_able); hash_into(h, value.all_able_blockers_block_this_if_able);
    hash_into(h, value.cant_attack_alone); hash_into(h, value.cant_block_alone); hash_into(h, value.can_block_only_flying);
    hash_into(h, value.max_attackers_each_combat); hash_into(h, value.max_blockers_each_combat);
    hash_into(h, value.max_blockers_to_block_this);
    hash_into(h, value.attack_cost); hash_into(h, value.block_cost);
    MTGSIM_HASH_ENUM(value.attachment_kind); hash_into(h, value.attachment_power_bonus); hash_into(h, value.attachment_toughness_bonus);
    hash_into(h, value.attachment_granted_ability_mask); hash_into(h, value.loyalty_ability); hash_vector(h, value.modes);
    hash_vector(h, value.activated_abilities); hash_vector(h, value.static_effects); hash_vector(h, value.zone_change_replacements);
    hash_into(h, value.sacrifice_cost); hash_into(h, value.discard_cost); hash_into(h, value.life_cost); hash_into(h, value.return_cost);
    hash_into(h, value.continuous_effect); MTGSIM_HASH_ENUM(value.continuous_effect_duration);
}

void hash_into(StableHasher& h, const GameObject& value) noexcept {
    hash_into(h, value.id); hash_into(h, value.definition_index); hash_into(h, value.has_copy_effect);
    hash_into(h, value.copied_definition_index); hash_into(h, value.owner); hash_into(h, value.controller);
    MTGSIM_HASH_ENUM(value.zone); hash_into(h, value.tapped); hash_into(h, value.token); hash_into(h, value.ceased_to_exist);
    hash_into(h, value.power); hash_into(h, value.toughness); hash_into(h, value.damage_marked);
    hash_into(h, value.deathtouch_damage_marked); hash_into(h, value.counters); hash_vector(h, value.targets);
    hash_into(h, value.chosen_mode_index); hash_into(h, value.ability_object); hash_into(h, value.regeneration_shields);
    hash_into(h, value.attached_to); hash_into(h, value.attacking); hash_into(h, value.blocked); hash_into(h, value.defending_player);
    hash_into(h, value.attacked_object); hash_into(h, value.blocking); hash_vector(h, value.combat_damage_ordered_blockers);
    hash_into(h, value.battle_protector); hash_into(h, value.controlled_since_turn_start_index); hash_into(h, value.loyalty_ability_activated_turn);
    hash_into(h, value.zone_change_index); hash_into(h, value.layer_timestamp);
}

void hash_into(StableHasher& h, const PlayerState& value) noexcept {
    hash_into(h, value.id); hash_into(h, value.name); hash_into(h, value.life); hash_into(h, value.poison);
    hash_into(h, value.max_hand_size); hash_into(h, value.max_land_plays_per_turn); hash_into(h, value.lands_played_this_turn);
    hash_into(h, value.mana_pool); hash_into(h, value.lost); hash_into(h, value.empty_library_draw_attempts);
    hash_into(h, value.mulligans_taken); hash_into(h, value.turn_start_index);
    for (const auto& zone_objects : value.zones) {
        hash_vector(h, zone_objects);
    }
}

void hash_into(StableHasher& h, const PendingTrigger& value) noexcept {
    hash_into(h, value.controller); hash_into(h, value.source); hash_into(h, value.subject); hash_into(h, value.subject_zone_change_index);
    hash_into(h, value.source_name); MTGSIM_HASH_ENUM(value.event); MTGSIM_HASH_ENUM(value.effect_kind); hash_into(h, value.effect_amount);
    MTGSIM_HASH_ENUM(value.effect_counter_kind); hash_into(h, value.target_mask); hash_into(h, value.target_count);
    hash_into(h, value.created_token_definition_index); hash_into(h, value.source_color_mask); hash_into(h, value.source_ability_mask);
    hash_into(h, value.source_zone_change_index); hash_into(h, value.caused_by_event_sequence);
    // trigger_record_index is deliberately excluded: it is a journal anchor, not a continuation fact.
}

void hash_into(StableHasher& h, const DamagePreventionShield& value) noexcept {
    hash_into(h, value.id); hash_into(h, value.target); hash_into(h, value.remaining); hash_into(h, value.choice_rank); hash_into(h, value.label);
}

void hash_into(StableHasher& h, const ContinuousEffectTarget& value) noexcept {
    hash_into(h, value.target); hash_into(h, value.object_zone_change_index);
}

void hash_into(StableHasher& h, const ContinuousEffectDefinition& value) noexcept {
    hash_into(h, value.name); hash_into(h, value.effect); MTGSIM_HASH_ENUM(value.duration); hash_into(h, value.controller);
    hash_into(h, value.source); hash_vector(h, value.locked_targets); hash_into(h, value.timestamp);
}

void hash_into(StableHasher& h, const Event& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.kind); hash_into(h, value.detail);
}

void hash_into(StableHasher& h, const EventRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.log_kind); hash_into(h, value.object);
    hash_into(h, value.object_zone_change_index); hash_into(h, value.player); hash_into(h, value.target);
    hash_into(h, value.choice_mode_index); hash_into(h, value.choice_mode_contract_hash);
    hash_into(h, value.choice_target_count); hash_into(h, value.choice_target_set_hash);
    hash_into(h, value.zone_change_record_index);
    hash_into(h, value.zone_replacement_record_index); hash_into(h, value.damage_record_index); hash_into(h, value.damage_prevention_record_index);
    hash_into(h, value.life_change_record_index); hash_into(h, value.mana_change_record_index); hash_into(h, value.counter_change_record_index);
    hash_into(h, value.discard_record_index); hash_into(h, value.trigger_record_index); hash_into(h, value.stack_placement_record_index);
    hash_into(h, value.stack_resolution_record_index); hash_into(h, value.priority_transition_record_index); hash_into(h, value.state_based_action_record_index);
    hash_into(h, value.combat_declaration_record_index); hash_into(h, value.combat_damage_assignment_record_index);
    hash_into(h, value.mana_payment_plan_record_index); hash_into(h, value.draw_record_index);
    hash_into(h, value.mulligan_record_index); hash_into(h, value.mulligan_keep_record_index);
    hash_into(h, value.paid_action_declaration_record_index);
    hash_into(h, value.paid_action_transaction_record_index);
}

void hash_into(StableHasher& h, const StackPlacementRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.source_object); hash_into(h, value.stack_object);
    hash_into(h, value.controller); MTGSIM_HASH_ENUM(value.source_zone_before); hash_into(h, value.source_zone_change_index_before);
    hash_into(h, value.stack_zone_change_index); hash_into(h, value.stack_enter_zone_change_record_index); hash_into(h, value.ability_index);
    hash_into(h, value.loyalty_cost_delta); hash_into(h, value.chosen_mode_index); hash_into(h, value.target_mask); hash_into(h, value.target_count);
    hash_vector(h, value.chosen_targets); hash_into(h, value.stack_size_before); hash_into(h, value.stack_size_after); hash_into(h, value.priority_before);
    hash_into(h, value.priority_after); hash_into(h, value.physical_card); hash_into(h, value.ability_object); hash_into(h, value.modal_choice);
    hash_into(h, value.target_choice); hash_into(h, value.mana_cost_required); hash_into(h, value.mana_cost_paid); hash_into(h, value.tap_cost_required);
    hash_into(h, value.tap_cost_paid); hash_into(h, value.sacrifice_cost_required); hash_into(h, value.sacrifice_cost_paid);
    hash_into(h, value.discard_cost_required); hash_into(h, value.discard_cost_paid); hash_into(h, value.loyalty_cost_paid);
    hash_into(h, value.paid_action_phase_recorded); hash_into(h, value.stack_object_on_stack_before_costs);
    hash_into(h, value.choices_locked_before_costs); hash_into(h, value.paid_action_events_before_stack_placement);
    hash_into(h, value.stack_object_entered_sequence); hash_into(h, value.choices_locked_sequence);
    hash_into(h, value.first_paid_action_event_sequence); hash_into(h, value.last_paid_action_event_sequence);
    hash_into(h, value.first_mana_payment_plan_record_index); hash_into(h, value.mana_payment_plan_record_count);
    hash_into(h, value.first_mana_change_record_index); hash_into(h, value.mana_change_record_count);
    hash_into(h, value.first_paid_action_counter_change_record_index); hash_into(h, value.paid_action_counter_change_record_count);
    hash_into(h, value.first_paid_action_zone_change_record_index); hash_into(h, value.paid_action_zone_change_record_count);
    hash_into(h, value.first_choice_event_sequence); hash_into(h, value.last_choice_event_sequence); hash_into(h, value.choice_event_count);
    hash_into(h, value.mode_choice_event_sequence); hash_into(h, value.target_choice_event_sequence);
    hash_into(h, value.first_sacrifice_cost_zone_change_record_index); hash_into(h, value.sacrifice_cost_zone_change_record_count);
    hash_into(h, value.sacrifice_cost_event_sequence); hash_into(h, value.first_sacrifice_cost_payment_record_index);
    hash_into(h, value.sacrifice_cost_payment_record_count); hash_into(h, value.sacrifice_cost_payment_hash);
    hash_into(h, value.first_discard_cost_record_index); hash_into(h, value.discard_cost_record_count);
    hash_into(h, value.first_discard_cost_zone_change_record_index); hash_into(h, value.discard_cost_zone_change_record_count);
    hash_into(h, value.discard_cost_event_sequence); hash_into(h, value.first_discard_cost_payment_record_index);
    hash_into(h, value.discard_cost_payment_record_count); hash_into(h, value.discard_cost_payment_hash);
    hash_into(h, value.first_tap_cost_payment_record_index); hash_into(h, value.tap_cost_payment_record_count);
    hash_into(h, value.tap_cost_payment_hash); hash_into(h, value.tap_cost_event_sequence);
    hash_into(h, value.life_cost_required); hash_into(h, value.life_cost_paid);
    hash_into(h, value.first_life_cost_payment_record_index); hash_into(h, value.life_cost_payment_record_count);
    hash_into(h, value.life_cost_payment_hash); hash_into(h, value.first_life_cost_life_change_record_index);
    hash_into(h, value.life_cost_life_change_record_count); hash_into(h, value.life_cost_event_sequence);
    hash_into(h, value.return_cost_required); hash_into(h, value.return_cost_paid);
    hash_into(h, value.first_return_cost_zone_change_record_index); hash_into(h, value.return_cost_zone_change_record_count);
    hash_into(h, value.return_cost_event_sequence); hash_into(h, value.first_return_cost_payment_record_index);
    hash_into(h, value.return_cost_payment_record_count); hash_into(h, value.return_cost_payment_hash);
    hash_into(h, value.first_loyalty_cost_payment_record_index);
    hash_into(h, value.loyalty_cost_payment_record_count);
    hash_into(h, value.loyalty_cost_payment_hash); hash_into(h, value.loyalty_cost_event_sequence);
    hash_into(h, value.paid_action_declaration_record_index); hash_into(h, value.paid_action_declaration_hash);
}

void hash_into(StableHasher& h, const TargetResolutionCheckRecord& value) noexcept {
    hash_into(h, value.target_index); hash_into(h, value.target); hash_into(h, value.source_controller);
    hash_into(h, value.legal_on_resolution); MTGSIM_HASH_ENUM(value.failure_kind);
    MTGSIM_HASH_ENUM(value.object_zone_on_resolution); hash_into(h, value.object_zone_change_index_on_resolution);
}

void hash_into(StableHasher& h, const StackResolutionRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.stack_object); hash_into(h, value.controller); hash_into(h, value.ability_object);
    hash_into(h, value.permanent_spell); hash_into(h, value.aura_spell); hash_into(h, value.modal_spell); hash_into(h, value.chosen_mode_index);
    MTGSIM_HASH_ENUM(value.effect_kind); hash_into(h, value.effect_amount); MTGSIM_HASH_ENUM(value.effect_counter_kind); hash_into(h, value.target_mask);
    hash_into(h, value.target_count); hash_vector(h, value.chosen_targets); hash_vector(h, value.target_resolution_checks); hash_into(h, value.trigger_record_index);
    hash_into(h, value.required_target_count); hash_into(h, value.legal_target_count);
    hash_into(h, value.missing_required_targets); hash_into(h, value.all_targets_illegal); hash_into(h, value.required_target_failed); hash_into(h, value.modal_choice_invalid);
    hash_into(h, value.effect_payload_applied); MTGSIM_HASH_ENUM(value.outcome); hash_into(h, value.stack_zone_change_index); hash_into(h, value.stack_leave_zone_change_record_index);
    hash_into(h, value.stack_object_left_stack); MTGSIM_HASH_ENUM(value.final_zone);
}

void hash_into(StableHasher& h, const PriorityTransitionRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.outcome); hash_into(h, value.player); hash_into(h, value.active_player);
    hash_into(h, value.priority_before); hash_into(h, value.priority_after); MTGSIM_HASH_ENUM(value.step_before); MTGSIM_HASH_ENUM(value.step_after);
    hash_into(h, value.stack_size_before); hash_into(h, value.stack_size_after); hash_into(h, value.stack_top_before); hash_into(h, value.stack_top_after);
    hash_into(h, value.consecutive_passes_before); hash_into(h, value.consecutive_passes_after_pass); hash_into(h, value.consecutive_passes_after);
    hash_into(h, value.alive_players); hash_into(h, value.pending_triggers_before); hash_into(h, value.pending_triggers_after); hash_into(h, value.stack_resolution_record_index);
    hash_into(h, value.trigger_stack_record_count_before); hash_into(h, value.trigger_stack_record_count_after); hash_into(h, value.pass_count_incremented);
    hash_into(h, value.priority_changed); hash_into(h, value.stack_resolved); hash_into(h, value.step_advanced); hash_into(h, value.pending_triggers_put_on_stack);
}

void hash_into(StableHasher& h, const StateBasedActionRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.check_index); hash_into(h, value.pass_index); hash_into(h, value.pass_candidate_count); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.object); hash_into(h, value.player); MTGSIM_HASH_ENUM(value.object_zone);
    hash_into(h, value.object_zone_change_index); hash_into(h, value.effective_power); hash_into(h, value.effective_toughness); hash_into(h, value.damage_marked);
    hash_into(h, value.deathtouch_damage_marked); hash_into(h, value.plus_one_plus_one_counters); hash_into(h, value.minus_one_minus_one_counters);
    hash_into(h, value.loyalty_counters); hash_into(h, value.defense_counters); hash_into(h, value.regeneration_shields_before); hash_into(h, value.regeneration_shields_after);
    hash_into(h, value.regeneration_applied); hash_into(h, value.indestructible); hash_into(h, value.object_left_battlefield); hash_into(h, value.attachment_detached);
    hash_into(h, value.token_ceased); hash_into(h, value.zone_change_record_index);
}

void hash_into(StableHasher& h, const ZoneChangeRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.object); hash_into(h, value.owner); hash_into(h, value.previous_controller); hash_into(h, value.new_controller);
    MTGSIM_HASH_ENUM(value.from_zone); MTGSIM_HASH_ENUM(value.requested_zone); MTGSIM_HASH_ENUM(value.to_zone); hash_into(h, value.from_zone_change_index); hash_into(h, value.to_zone_change_index);
    hash_into(h, value.first_replacement_record_index); hash_into(h, value.replacement_record_count); hash_into(h, value.first_counter_change_record_index); hash_into(h, value.counter_change_record_count);
    hash_into(h, value.first_damage_prevention_record_index); hash_into(h, value.damage_prevention_record_count); hash_into(h, value.replacement_applied); hash_into(h, value.was_token);
    hash_into(h, value.was_ability_object); hash_into(h, value.was_battlefield_creature); hash_into(h, value.creature_died);
}

void hash_into(StableHasher& h, const ZoneChangeReplacementRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.object); hash_into(h, value.affected_player); hash_into(h, value.controller); hash_into(h, value.source);
    hash_into(h, value.name); MTGSIM_HASH_ENUM(value.from_zone); MTGSIM_HASH_ENUM(value.event_to_zone); MTGSIM_HASH_ENUM(value.replacement_zone);
    hash_into(h, value.definition_index); MTGSIM_HASH_ENUM(value.priority_tier); MTGSIM_HASH_ENUM(value.candidate_min_priority_tier);
    hash_into(h, value.choice_rank); hash_into(h, value.candidate_count); hash_into(h, value.eligible_candidate_count); hash_into(h, value.pass_index);
    hash_into(h, value.zone_change_record_index); hash_into(h, value.source_zone_change_index); hash_into(h, value.chosen_among_multiple);
}

void hash_into(StableHasher& h, const CombatDeclarationRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.controller); hash_into(h, value.actor); hash_into(h, value.actor_zone_change_index);
    hash_into(h, value.target); hash_into(h, value.target_zone_change_index); hash_into(h, value.defending_player); hash_into(h, value.attacker); hash_into(h, value.blocker);
    hash_into(h, value.attacked_object); hash_into(h, value.attacker_zone_change_index); hash_into(h, value.blocker_zone_change_index); hash_into(h, value.target_is_player);
    hash_into(h, value.target_is_planeswalker); hash_into(h, value.target_is_battle); hash_into(h, value.tapped_before); hash_into(h, value.tapped_after); hash_into(h, value.vigilance);
    hash_into(h, value.attacker_had_flying); hash_into(h, value.blocker_had_flying); hash_into(h, value.blocker_had_reach); hash_into(h, value.attacker_had_menace);
    hash_into(h, value.blocker_batch_size); hash_into(h, value.final_blocker_count_for_attacker); hash_into(h, value.menace_satisfied); hash_into(h, value.attacker_marked_blocked_after);
}

void hash_into(StableHasher& h, const CombatDamageAssignmentRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.source); hash_into(h, value.source_controller); hash_into(h, value.source_zone_change_index); hash_into(h, value.target);
    hash_into(h, value.target_zone_change_index); hash_into(h, value.assigned); hash_into(h, value.damage_record_index); hash_into(h, value.first_strike_batch);
    hash_into(h, value.split_combat_damage); hash_into(h, value.source_was_attacker); hash_into(h, value.source_was_blocker); hash_into(h, value.attacker_was_blocked);
    hash_into(h, value.blocker_count); hash_into(h, value.source_had_trample); hash_into(h, value.excess_trample);
}

void hash_into(StableHasher& h, const DamageRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.source); hash_into(h, value.source_controller); hash_into(h, value.target); hash_into(h, value.amount);
    hash_into(h, value.prevented); hash_into(h, value.dealt); hash_into(h, value.not_dealt); hash_into(h, value.prevented_by_protection); hash_into(h, value.unpreventable);
    hash_into(h, value.protection_prevention_ignored); hash_into(h, value.source_had_lifelink);
    hash_into(h, value.source_had_deathtouch); hash_into(h, value.source_color_mask); hash_into(h, value.source_ability_mask); hash_into(h, value.source_zone_change_index);
    hash_into(h, value.target_zone_change_index); hash_into(h, value.target_was_creature); hash_into(h, value.target_was_planeswalker); hash_into(h, value.target_was_battle);
    hash_into(h, value.target_was_damageable); hash_into(h, value.damage_disallowed_by_target_type); hash_into(h, value.counters_removed);
    hash_into(h, value.first_damage_counter_change_record_index); hash_into(h, value.damage_counter_change_record_count);
    hash_into(h, value.first_damage_life_change_record_index); hash_into(h, value.damage_life_change_record_count);
    hash_into(h, value.first_damage_prevention_record_index); hash_into(h, value.damage_prevention_record_count);
}

void hash_into(StableHasher& h, const DamagePreventionRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.shield_id); hash_into(h, value.target); hash_into(h, value.amount);
    hash_into(h, value.remaining_before); hash_into(h, value.remaining_after); hash_into(h, value.damage_record_index); hash_into(h, value.zone_change_record_index);
    hash_into(h, value.affected_player); hash_into(h, value.choice_rank); hash_into(h, value.candidate_count); hash_into(h, value.pass_index);
    hash_into(h, value.chosen_among_multiple); hash_into(h, value.label);
}

void hash_into(StableHasher& h, const LifeChangeRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.player); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.amount); hash_into(h, value.life_before); hash_into(h, value.life_after);
    hash_into(h, value.damage_source); hash_into(h, value.damage_source_zone_change_index); hash_into(h, value.damage_target); hash_into(h, value.damage_record_index);
    hash_into(h, value.damage_result); hash_into(h, value.lifelink_result);
}

void hash_into(StableHasher& h, const ManaChangeRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.player); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.pool_before); hash_into(h, value.pool_after);
    hash_into(h, value.added); hash_into(h, value.spent); hash_into(h, value.cost); hash_into(h, value.source); hash_into(h, value.source_zone_change_index);
    hash_into(h, value.mana_ability_index); hash_into(h, value.auto_payment_mana_ability_count);
    hash_into(h, value.auto_payment_locked_tap_source_count); hash_into(h, value.auto_payment_plan_hash);
    hash_into(h, value.auto_payment_plan_record_index); hash_into(h, value.auto_payment_producer_plan_record_index);
    hash_into(h, value.auto_payment_producer_plan_step_index); hash_into(h, value.auto_payment);
}

void hash_into(StableHasher& h, const ManaPaymentPlanLockedSourceRecord& value) noexcept {
    hash_into(h, value.source); hash_into(h, value.source_zone_change_index);
}

void hash_mana_payment_plan_step_identity(StableHasher& h, const ManaPaymentPlanStepRecord& value) noexcept {
    hash_into(h, value.source); hash_into(h, value.source_zone_change_index); hash_into(h, value.mana_ability_index);
    hash_into(h, value.produces); hash_into(h, value.tap_cost);
}

void hash_into(StableHasher& h, const ManaPaymentPlanStepRecord& value) noexcept {
    hash_mana_payment_plan_step_identity(h, value);
    hash_into(h, value.produced_mana_change_record_index);
    hash_into(h, value.tap_event_sequence);
}

void hash_into(StableHasher& h, const ManaPaymentPlanRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.player); hash_into(h, value.cost);
    hash_into(h, value.pool_before_plan); hash_into(h, value.pool_before_payment);
    hash_vector(h, value.locked_tap_sources); hash_vector(h, value.mana_ability_steps);
    hash_into(h, value.plan_hash); hash_into(h, value.paid_mana_change_record_index);
}

void hash_paid_action_declaration_identity(StableHasher& h, const PaidActionDeclarationRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.schema_version); MTGSIM_HASH_ENUM(value.action_kind);
    hash_into(h, value.player); hash_into(h, value.source_object); hash_into(h, value.stack_object);
    hash_into(h, value.definition_index); MTGSIM_HASH_ENUM(value.source_zone_before); hash_into(h, value.source_zone_change_index_before);
    hash_into(h, value.stack_zone_change_index); hash_into(h, value.stack_enter_zone_change_record_index);
    hash_into(h, value.stack_object_entered_sequence); hash_into(h, value.choices_locked_sequence);
    hash_into(h, value.ability_index); hash_into(h, value.loyalty_cost_delta);
    hash_into(h, value.declared_mode_index); hash_into(h, value.declared_mode_contract_hash);
    hash_into(h, value.target_mask); hash_into(h, value.target_count); hash_vector(h, value.declared_targets);
    hash_into(h, value.declared_target_set_hash); hash_into(h, value.total_mana_cost);
    hash_into(h, value.sacrifice_cost.count); hash_into(h, value.sacrifice_cost.required_type_mask);
    hash_into(h, value.discard_cost.count); hash_into(h, value.life_cost.amount); hash_into(h, value.return_cost);
    hash_into(h, value.total_cost_locked); hash_into(h, value.mana_cost_required); hash_into(h, value.tap_cost_required);
    hash_into(h, value.sacrifice_cost_required); hash_into(h, value.discard_cost_required); hash_into(h, value.life_cost_required);
    hash_into(h, value.return_cost_required); hash_into(h, value.loyalty_cost_required);
    hash_into(h, value.modal_choice_declared); hash_into(h, value.target_choice_declared);
    hash_into(h, value.payment_attempted); hash_into(h, value.first_payment_event_sequence); hash_into(h, value.last_payment_event_sequence);
    hash_into(h, value.first_sacrifice_cost_payment_record_index);
    hash_into(h, value.sacrifice_cost_payment_record_count);
    hash_into(h, value.sacrifice_cost_payment_hash);
    hash_into(h, value.first_discard_cost_payment_record_index);
    hash_into(h, value.discard_cost_payment_record_count);
    hash_into(h, value.discard_cost_payment_hash);
    hash_into(h, value.first_tap_cost_payment_record_index);
    hash_into(h, value.tap_cost_payment_record_count);
    hash_into(h, value.tap_cost_payment_hash);
    hash_into(h, value.first_life_cost_payment_record_index);
    hash_into(h, value.life_cost_payment_record_count);
    hash_into(h, value.life_cost_payment_hash);
    hash_into(h, value.first_return_cost_payment_record_index);
    hash_into(h, value.return_cost_payment_record_count);
    hash_into(h, value.return_cost_payment_hash);
    hash_into(h, value.first_loyalty_cost_payment_record_index);
    hash_into(h, value.loyalty_cost_payment_record_count);
    hash_into(h, value.loyalty_cost_payment_hash);
}

void hash_into(StableHasher& h, const PaidActionDeclarationRecord& value) noexcept {
    hash_paid_action_declaration_identity(h, value);
    hash_into(h, value.stack_placement_record_index);
    hash_into(h, value.declaration_hash);
}

void hash_paid_action_transaction_identity(StableHasher& h, const PaidActionTransactionRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.schema_version); MTGSIM_HASH_ENUM(value.outcome); MTGSIM_HASH_ENUM(value.action_kind);
    hash_into(h, value.player); hash_into(h, value.source_object); hash_into(h, value.stack_object);
    hash_into(h, value.stack_placement_record_index); hash_into(h, value.paid_action_declaration_record_index);
    hash_into(h, value.paid_action_declaration_hash); hash_into(h, value.committed_paid_action_declaration_snapshot_present);
    hash_into(h, value.committed_paid_action_declaration_snapshot); hash_into(h, value.stack_object_entered_sequence);
    hash_into(h, value.choices_locked_sequence); hash_into(h, value.first_paid_action_event_sequence);
    hash_into(h, value.last_paid_action_event_sequence); hash_into(h, value.first_mana_payment_plan_record_index);
    hash_into(h, value.mana_payment_plan_record_count); hash_into(h, value.first_mana_change_record_index);
    hash_into(h, value.mana_change_record_count); hash_into(h, value.first_paid_action_counter_change_record_index);
    hash_into(h, value.paid_action_counter_change_record_count); hash_into(h, value.first_paid_action_zone_change_record_index);
    hash_into(h, value.paid_action_zone_change_record_count);
    hash_into(h, value.first_sacrifice_cost_payment_record_index);
    hash_into(h, value.sacrifice_cost_payment_record_count);
    hash_into(h, value.sacrifice_cost_payment_hash);
    hash_into(h, value.first_discard_cost_payment_record_index);
    hash_into(h, value.discard_cost_payment_record_count);
    hash_into(h, value.discard_cost_payment_hash);
    hash_into(h, value.first_tap_cost_payment_record_index);
    hash_into(h, value.tap_cost_payment_record_count);
    hash_into(h, value.tap_cost_payment_hash);
    hash_into(h, value.first_life_cost_payment_record_index);
    hash_into(h, value.life_cost_payment_record_count);
    hash_into(h, value.life_cost_payment_hash);
    hash_into(h, value.first_return_cost_payment_record_index);
    hash_into(h, value.return_cost_payment_record_count);
    hash_into(h, value.return_cost_payment_hash);
    hash_into(h, value.first_loyalty_cost_payment_record_index);
    hash_into(h, value.loyalty_cost_payment_record_count);
    hash_into(h, value.loyalty_cost_payment_hash);
    hash_into(h, value.speculative_event_count);
    hash_into(h, value.speculative_event_record_count); hash_into(h, value.speculative_stack_placement_record_count);
    hash_into(h, value.speculative_paid_action_declaration_record_count);
    hash_into(h, value.speculative_paid_action_declaration_sequence); hash_into(h, value.speculative_paid_action_declaration_hash);
    hash_into(h, value.speculative_paid_action_declaration_snapshot_present);
    hash_into(h, value.speculative_paid_action_declaration_snapshot);
    hash_into(h, value.speculative_first_payment_event_sequence); hash_into(h, value.speculative_last_payment_event_sequence);
    hash_into(h, value.physical_state_hash_before);
    hash_into(h, value.physical_state_hash_after); hash_into(h, value.next_event_sequence_before);
    hash_into(h, value.speculative_next_event_sequence_after); hash_into(h, value.committed); hash_into(h, value.rolled_back);
    hash_into(h, value.physical_state_preserved_on_rollback); hash_into(h, value.choices_before_payment);
    hash_into(h, value.payments_before_placement); hash_into(h, value.placement_before_transaction);
}

void hash_into(StableHasher& h, const PaidActionTransactionRecord& value) noexcept {
    hash_paid_action_transaction_identity(h, value);
    hash_into(h, value.transaction_hash);
}

void hash_into(StableHasher& h, const CounterChangeRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.kind); MTGSIM_HASH_ENUM(value.counter_kind); hash_into(h, value.object); hash_into(h, value.player);
    hash_into(h, value.object_zone_change_index); hash_into(h, value.amount); hash_into(h, value.count_before); hash_into(h, value.count_after); hash_into(h, value.source);
    hash_into(h, value.source_zone_change_index); hash_into(h, value.zone_change_record_index); hash_into(h, value.damage_result); hash_into(h, value.cost_payment); hash_into(h, value.zone_change_cleanup);
}

void hash_into(StableHasher& h, const DiscardRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.player); hash_into(h, value.card); hash_into(h, value.hand_size_before);
    hash_into(h, value.hand_size_after); hash_into(h, value.graveyard_size_before); hash_into(h, value.graveyard_size_after); hash_into(h, value.max_hand_size);
    hash_into(h, value.card_zone_change_index_before); hash_into(h, value.card_zone_change_index_after); hash_into(h, value.zone_change_record_index); hash_into(h, value.explicit_choice);
    hash_into(h, value.cleanup_hand_size); hash_into(h, value.cost_payment); hash_into(h, value.used_zone_change_pipeline);
}

void hash_into(StableHasher& h, const DrawRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.outcome); hash_into(h, value.player); hash_into(h, value.card); hash_into(h, value.library_size_before);
    hash_into(h, value.library_size_after); hash_into(h, value.hand_size_before); hash_into(h, value.hand_size_after); hash_into(h, value.empty_library_draw_attempts_before);
    hash_into(h, value.empty_library_draw_attempts_after); hash_into(h, value.card_zone_change_index_before); hash_into(h, value.card_zone_change_index_after);
    hash_into(h, value.zone_change_record_index); hash_into(h, value.card_moved); hash_into(h, value.empty_library_attempt);
}

void hash_into(StableHasher& h, const MulliganRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.player); hash_into(h, value.mulligans_before); hash_into(h, value.mulligans_after); hash_into(h, value.opening_hand_size);
    hash_into(h, value.returned_count); hash_into(h, value.draw_attempt_count); hash_into(h, value.successful_draw_count); hash_into(h, value.library_size_before); hash_into(h, value.library_size_after_return);
    hash_into(h, value.library_size_after_shuffle); hash_into(h, value.library_size_after); hash_into(h, value.hand_size_before); hash_into(h, value.hand_size_after_return); hash_into(h, value.hand_size_after);
    hash_into(h, value.empty_library_draw_attempts_before); hash_into(h, value.empty_library_draw_attempts_after); hash_into(h, value.rng_state_before); hash_into(h, value.rng_state_after);
    hash_into(h, value.first_return_zone_change_record_index); hash_into(h, value.return_zone_change_record_count); hash_into(h, value.first_draw_record_index); hash_into(h, value.draw_record_count);
    hash_into(h, value.shuffled); hash_into(h, value.used_zone_change_pipeline); hash_into(h, value.used_draw_pipeline);
}

void hash_into(StableHasher& h, const MulliganKeepRecord& value) noexcept {
    hash_into(h, value.sequence); hash_into(h, value.player); hash_into(h, value.mulligans_taken); hash_into(h, value.bottom_count_required); hash_into(h, value.bottom_count);
    hash_into(h, value.hand_size_before); hash_into(h, value.hand_size_after); hash_into(h, value.library_size_before); hash_into(h, value.library_size_after);
    hash_into(h, value.first_bottom_zone_change_record_index); hash_into(h, value.bottom_zone_change_record_count); hash_vector(h, value.bottomed_cards); hash_into(h, value.explicit_choice);
    hash_into(h, value.deterministic_fallback); hash_into(h, value.used_zone_change_pipeline); hash_into(h, value.placed_on_bottom);
}

void hash_into(StableHasher& h, const ActionReceiptRecord& value) noexcept {
    hash_into(h, value.receipt_index); MTGSIM_HASH_ENUM(value.kind); hash_into(h, value.player); hash_into(h, value.object);
    hash_vector(h, value.targets); hash_into(h, value.mode_index); hash_into(h, value.ability_index); hash_into(h, value.mana_ability_index); hash_vector(h, value.trigger_order);
    MTGSIM_HASH_ENUM(value.choice_kind); hash_into(h, value.choice_request_schema_version); hash_into(h, value.choice_request_hash); hash_into(h, value.choice_action_count); hash_into(h, value.choice_required);
    hash_into(h, value.choice_action_frontier_complete); hash_into(h, value.choice_action_generation_limit); MTGSIM_HASH_ENUM(value.choice_validation_source);
    hash_into(h, value.choice_page_location_found); hash_into(h, value.choice_page_location_checked); hash_into(h, value.choice_page_schema_version); hash_into(h, value.choice_page_state_hash); hash_into(h, value.choice_page_choice_request_hash); hash_into(h, value.choice_page_requested_limit); hash_into(h, value.choice_page_effective_limit);
    hash_into(h, value.choice_page_cursor); hash_into(h, value.choice_action_cursor); hash_into(h, value.choice_page_index);
    hash_into(h, value.choice_page_next_cursor); hash_into(h, value.choice_page_actions_seen); hash_into(h, value.choice_page_scanned_pages); hash_into(h, value.choice_page_complete);
    hash_into(h, value.choice_page_total_actions_lower_bound); hash_into(h, value.choice_page_total_actions_exact); hash_into(h, value.choice_page_remaining_actions_lower_bound);
    hash_into(h, value.choice_page_hash); hash_into(h, value.choice_page_location_hash);
    hash_into(h, value.choice_queue_schema_version); hash_into(h, value.choice_queue_hash); hash_into(h, value.choice_queue_index); hash_into(h, value.choice_queue_size); hash_into(h, value.choice_queue_location_schema_version); hash_into(h, value.choice_queue_location_found); hash_into(h, value.choice_queue_location_checked); hash_into(h, value.choice_queue_location_hash);
    hash_into(h, value.action_schema_version); hash_into(h, value.action_hash); hash_into(h, value.state_schema_version); hash_into(h, value.state_hash_before); hash_into(h, value.state_hash_after);
    hash_into(h, value.journal_hash_before); hash_into(h, value.journal_hash_after); hash_into(h, value.journal_hash_after_action);
    hash_into(h, value.journal_entries_before); hash_into(h, value.journal_entries_after_action); hash_into(h, value.journal_entries_after);
    hash_into(h, value.next_event_sequence_before); hash_into(h, value.next_event_sequence_after);
    hash_into(h, value.legal_before); hash_into(h, value.applied);
}

void hash_into(StableHasher& h, const TriggerRecord& value) noexcept {
    hash_into(h, value.sequence); MTGSIM_HASH_ENUM(value.event); hash_into(h, value.subject); hash_into(h, value.subject_zone_change_index); hash_into(h, value.controller);
    hash_into(h, value.source); hash_into(h, value.source_name); hash_into(h, value.source_color_mask); hash_into(h, value.source_ability_mask); hash_into(h, value.source_zone_change_index);
    MTGSIM_HASH_ENUM(value.effect_kind); hash_into(h, value.effect_amount); MTGSIM_HASH_ENUM(value.effect_counter_kind); hash_into(h, value.target_mask); hash_into(h, value.target_count);
    hash_into(h, value.required_target_count); hash_vector(h, value.chosen_targets); hash_into(h, value.legal_target_set_count); hash_into(h, value.choice_target_set_hash);
    hash_into(h, value.target_choice_recorded); hash_into(h, value.no_legal_choices);
    hash_into(h, value.created_token_definition_index); hash_into(h, value.caused_by_event_sequence); hash_into(h, value.stack_object); hash_into(h, value.put_on_stack_sequence);
    hash_into(h, value.stack_order); hash_into(h, value.stack_resolution_record_index); hash_into(h, value.resolved_sequence);
    MTGSIM_HASH_ENUM(value.resolution_outcome); hash_into(h, value.resolved_effect_payload_applied);
    hash_into(h, value.dropped); hash_into(h, value.dropped_sequence);
}

#undef MTGSIM_HASH_ENUM

std::string object_label(const GameState& game, ObjectId id);
std::string target_label(const GameState& game, TargetRef target);
[[nodiscard]] const CardDefinition* current_definition_for_object(const GameState& game, const GameObject& obj) noexcept;
[[nodiscard]] bool continuous_target_matches(const GameState& game, const ContinuousEffectTarget& locked, ObjectId target_id) noexcept;

std::vector<ObjectId>& container_for_object(GameState& game, const GameObject& obj, Zone zone_name) {
    if (zone_is_global(zone_name)) {
        return game.stack;
    }
    return zone(game, expected_zone_container_player(obj, zone_name), zone_name);
}

[[nodiscard]] bool object_is_creature(const GameState& game, const GameObject& obj) {
    return obj.id.valid() && has_type_mask(object_type_mask(game, obj.id), TypeCreature);
}

[[nodiscard]] bool object_is_planeswalker(const GameState& game, const GameObject& obj) {
    return obj.id.valid() && has_type_mask(object_type_mask(game, obj.id), TypePlaneswalker);
}

[[nodiscard]] bool object_is_battle(const GameState& game, const GameObject& obj) {
    return obj.id.valid() && has_type_mask(object_type_mask(game, obj.id), TypeBattle);
}

[[nodiscard]] bool object_is_battlefield_planeswalker(const GameState& game, ObjectId id) {
    return id.valid() && id.value <= game.objects.size() &&
           object(game, id).zone == Zone::Battlefield && object_is_planeswalker(game, object(game, id));
}

[[nodiscard]] bool object_is_battlefield_battle(const GameState& game, ObjectId id) {
    return id.valid() && id.value <= game.objects.size() &&
           object(game, id).zone == Zone::Battlefield && object_is_battle(game, object(game, id));
}

[[nodiscard]] bool object_is_battlefield_combat_target(const GameState& game, ObjectId id) {
    return object_is_battlefield_planeswalker(game, id) || object_is_battlefield_battle(game, id);
}

[[nodiscard]] bool object_is_battlefield_creature(const GameState& game, ObjectId id) {
    return id.valid() && id.value <= game.objects.size() &&
           object(game, id).zone == Zone::Battlefield && object_is_creature(game, object(game, id));
}

[[nodiscard]] bool definition_is_land(const CardDefinition& def) noexcept {
    return (def.type_mask & TypeLand) != 0U;
}

[[nodiscard]] bool definition_is_instant(const CardDefinition& def) noexcept {
    return (def.type_mask & TypeInstant) != 0U;
}

[[nodiscard]] bool definition_has_flash(const CardDefinition& def) noexcept {
    return def.has_ability(AbilityFlash);
}

[[nodiscard]] bool player_has_sorcery_speed_window(const GameState& game, PlayerId player_id) noexcept {
    const Phase phase = phase_for_step(game.step);
    return game.active_player == player_id &&
           (phase == Phase::PrecombatMain || phase == Phase::PostcombatMain) &&
           game.stack.empty();
}

[[nodiscard]] bool object_in_player_hand(const GameState& game, PlayerId player_id, ObjectId object_id) noexcept {
    if (!player_id.valid() || player_id.value > game.players.size() || !object_id.valid() || object_id.value > game.objects.size()) {
        return false;
    }
    const auto& hand = zone(game, player_id, Zone::Hand);
    return std::find(hand.begin(), hand.end(), object_id) != hand.end();
}

[[nodiscard]] bool target_refs_equal(TargetRef a, TargetRef b) noexcept {
    return a == b;
}

[[nodiscard]] TargetRef stamp_target_for_choice(const GameState& game, TargetRef target) noexcept {
    if (target.kind == TargetKind::Object && target.object.valid() && target.object.value <= game.objects.size()) {
        target.object_zone_change_index = game.objects[target.object.value - 1U].zone_change_index;
    }
    return target;
}

[[nodiscard]] std::vector<TargetRef> single_target_vector(TargetRef target) {
    return target.valid() ? std::vector<TargetRef>{target} : std::vector<TargetRef>{};
}

[[nodiscard]] std::vector<TargetRef> action_target_vector(const LegalAction& action) {
    if (!action.targets.empty()) {
        return action.targets;
    }
    return single_target_vector(action.target);
}

[[nodiscard]] LegalAction canonicalize_legal_action(const LegalAction& action) {
    LegalAction canonical = action;
    canonical.label.clear();
    canonical.targets = action_target_vector(action);
    canonical.target = canonical.targets.size() == 1U ? canonical.targets.front() : TargetRef{};
    return canonical;
}

[[nodiscard]] std::string canonical_target_string(TargetRef target) {
    std::ostringstream out;
    out << static_cast<unsigned>(target.kind);
    switch (target.kind) {
        case TargetKind::Player:
            out << ":p" << target.player.value;
            break;
        case TargetKind::Object:
            out << ":o" << target.object.value << "@zc" << target.object_zone_change_index;
            break;
        case TargetKind::None:
            out << ":none";
            break;
    }
    return out.str();
}

void hash_action_fields(StableHasher& h, const LegalAction& action) noexcept {
    h.add_string("MTGSim.Action.v2");
    h.add_u64(static_cast<u64>(action.kind));
    hash_into(h, action.player);
    hash_into(h, action.object);
    hash_vector(h, action_target_vector(action));
    hash_into(h, action.mode_index);
    hash_into(h, action.ability_index);
    hash_into(h, action.mana_ability_index);
    hash_vector(h, action.trigger_order);
}

[[nodiscard]] std::vector<TargetRef> stamp_targets_for_choice(const GameState& game, const std::vector<TargetRef>& targets) {
    std::vector<TargetRef> stamped;
    stamped.reserve(targets.size());
    for (const auto target : targets) {
        stamped.push_back(stamp_target_for_choice(game, target));
    }
    return stamped;
}

[[nodiscard]] u32 required_target_count_for_mask(u32 target_mask, u32 explicit_count) noexcept {
    if (target_mask == TargetNone) {
        return 0U;
    }
    return explicit_count == 0U ? 1U : explicit_count;
}

[[nodiscard]] u32 required_target_count_for_spell(const CardDefinition& def) noexcept {
    return required_target_count_for_mask(def.target_mask, def.target_count);
}

[[nodiscard]] u32 required_target_count_for_mode(const SpellModeDefinition& mode) noexcept {
    return required_target_count_for_mask(mode.target_mask, mode.target_count);
}

[[nodiscard]] u32 required_target_count_for_activated_ability(const ActivatedAbilityDefinition& ability) noexcept {
    return required_target_count_for_mask(ability.target_mask, ability.target_count);
}

[[nodiscard]] u32 required_target_count_for_loyalty_ability(const LoyaltyAbilityDefinition& ability) noexcept {
    return required_target_count_for_mask(ability.target_mask, ability.target_count);
}

[[nodiscard]] u32 required_target_count_for_trigger(const PendingTrigger& trigger) noexcept {
    return required_target_count_for_mask(trigger.target_mask, trigger.target_count);
}

[[nodiscard]] bool same_target_choice_identity(TargetRef a, TargetRef b) noexcept {
    if (a.kind != b.kind) {
        return false;
    }
    switch (a.kind) {
        case TargetKind::Player:
            return a.player == b.player;
        case TargetKind::Object:
            return a.object == b.object;
        case TargetKind::None:
            return true;
    }
    return false;
}

[[nodiscard]] bool target_set_has_duplicate_choice(const std::vector<TargetRef>& targets) noexcept {
    for (std::size_t i = 0; i < targets.size(); ++i) {
        for (std::size_t j = i + 1U; j < targets.size(); ++j) {
            if (same_target_choice_identity(targets[i], targets[j])) {
                return true;
            }
        }
    }
    return false;
}

[[nodiscard]] bool target_set_is_legal_for_source_object(const GameState& game,
                                                        const std::vector<TargetRef>& targets,
                                                        u32 target_mask,
                                                        u32 target_count,
                                                        ObjectId source_id) noexcept {
    if (target_count == 0U) {
        return targets.empty();
    }
    if (targets.size() != target_count || target_set_has_duplicate_choice(targets)) {
        return false;
    }
    return std::all_of(targets.begin(), targets.end(), [&](TargetRef target) {
        return target_ref_is_legal_for_source_object(game, target, target_mask, source_id);
    });
}

[[nodiscard]] bool static_effect_has_type_layer_payload(const StaticEffectDefinition& effect) noexcept {
    return effect.added_type_mask != TypeNone || effect.removed_type_mask != TypeNone;
}

[[nodiscard]] bool static_effect_has_color_layer_payload(const StaticEffectDefinition& effect) noexcept {
    return effect.sets_color || effect.added_color_mask != ColorNone || effect.removed_color_mask != ColorNone;
}

[[nodiscard]] bool static_effect_has_ability_layer_payload(const StaticEffectDefinition& effect) noexcept {
    return effect.granted_ability_mask != AbilityNone || effect.removed_ability_mask != AbilityNone;
}

struct StaticBasePowerToughness {
    bool active = false;
    std::int32_t power = 0;
    std::int32_t toughness = 0;
};


[[nodiscard]] bool static_effect_has_base_pt_set_payload(const StaticEffectDefinition& effect) noexcept {
    return effect.sets_power_toughness;
}

[[nodiscard]] bool static_effect_has_power_modifier_payload(const StaticEffectDefinition& effect) noexcept {
    return effect.power_modifier != 0;
}

[[nodiscard]] bool static_effect_has_toughness_modifier_payload(const StaticEffectDefinition& effect) noexcept {
    return effect.toughness_modifier != 0;
}

struct LayerEffectApplication {
    const StaticEffectDefinition* effect = nullptr;
    u64 timestamp = 0;
    u32 discovery_order = 0;
};

[[nodiscard]] u64 source_static_effect_timestamp(const GameObject& source) noexcept {
    if (source.layer_timestamp != 0U) {
        return source.layer_timestamp;
    }
    return source.zone_change_index;
}

[[nodiscard]] bool static_scope_matches(const GameObject& source, const GameObject& target, StaticEffectScope scope) noexcept {
    switch (scope) {
        case StaticEffectScope::Source:
            return target.id == source.id;
        case StaticEffectScope::CreaturesYouControl:
        case StaticEffectScope::PermanentsYouControl:
            return target.controller == source.controller;
        case StaticEffectScope::CreaturesOpponentsControl:
        case StaticEffectScope::PermanentsOpponentsControl:
            return target.controller.valid() && source.controller.valid() && target.controller != source.controller;
        case StaticEffectScope::AllCreatures:
        case StaticEffectScope::AllPermanents:
            return true;
        case StaticEffectScope::None:
        case StaticEffectScope::Count:
            return false;
    }
    return false;
}

[[nodiscard]] bool continuous_scope_matches(PlayerId controller, const GameObject& target, StaticEffectScope scope) noexcept {
    switch (scope) {
        case StaticEffectScope::Source:
            return false;
        case StaticEffectScope::CreaturesYouControl:
        case StaticEffectScope::PermanentsYouControl:
            return target.controller == controller;
        case StaticEffectScope::CreaturesOpponentsControl:
        case StaticEffectScope::PermanentsOpponentsControl:
            return target.controller.valid() && controller.valid() && target.controller != controller;
        case StaticEffectScope::AllCreatures:
        case StaticEffectScope::AllPermanents:
            return true;
        case StaticEffectScope::None:
        case StaticEffectScope::Count:
            return false;
    }
    return false;
}

[[nodiscard]] bool static_effect_candidate_applies_to_object(const GameState& game,
                                                             const GameObject& source,
                                                             const StaticEffectDefinition& effect,
                                                             ObjectId target_id) noexcept {
    if (!effect.active() || source.zone != Zone::Battlefield || !source.id.valid() || source.ceased_to_exist ||
        !target_id.valid() || target_id.value > game.objects.size()) {
        return false;
    }
    const auto& target = game.objects[target_id.value - 1U];
    return target.zone == Zone::Battlefield && !target.ceased_to_exist && static_scope_matches(source, target, effect.scope);
}

[[nodiscard]] bool continuous_effect_candidate_applies_to_object(const GameState& game,
                                                                 const ContinuousEffectDefinition& continuous,
                                                                 ObjectId target_id) noexcept {
    if (!continuous.active() || !target_id.valid() || target_id.value > game.objects.size()) {
        return false;
    }
    const auto& target = game.objects[target_id.value - 1U];
    if (target.zone != Zone::Battlefield || target.ceased_to_exist) {
        return false;
    }
    if (!continuous.locked_targets.empty()) {
        return std::any_of(continuous.locked_targets.begin(), continuous.locked_targets.end(), [&](const ContinuousEffectTarget& locked) {
            return continuous_target_matches(game, locked, target_id);
        });
    }
    if (continuous.effect.scope == StaticEffectScope::Source) {
        if (!continuous.source.valid() || continuous.source.value > game.objects.size() || target_id != continuous.source) {
            return false;
        }
        const auto& source = object(game, continuous.source);
        return source.zone == Zone::Battlefield && !source.ceased_to_exist;
    }
    return continuous_scope_matches(continuous.controller, target, continuous.effect.scope);
}

[[nodiscard]] bool effect_names_match_dependency(const StaticEffectDefinition& dependent, const StaticEffectDefinition& prerequisite) noexcept {
    if (prerequisite.name.empty()) {
        return false;
    }
    return std::find(dependent.depends_on_effect_names.begin(),
                     dependent.depends_on_effect_names.end(),
                     prerequisite.name) != dependent.depends_on_effect_names.end();
}

void sort_layer_effects_by_timestamp(std::vector<LayerEffectApplication>& applications) {
    std::stable_sort(applications.begin(), applications.end(), [](const LayerEffectApplication& a, const LayerEffectApplication& b) {
        if (a.timestamp != b.timestamp) {
            return a.timestamp < b.timestamp;
        }
        return a.discovery_order < b.discovery_order;
    });
}

[[nodiscard]] std::vector<LayerEffectApplication> dependency_ordered_layer_effects(std::vector<LayerEffectApplication> applications) {
    sort_layer_effects_by_timestamp(applications);
    const std::size_t count = applications.size();
    if (count < 2U) {
        return applications;
    }

    std::vector<std::vector<std::size_t>> outgoing(count);
    std::vector<u32> incoming(count, 0U);
    u32 edges = 0;
    for (std::size_t dependent = 0; dependent < count; ++dependent) {
        if (applications[dependent].effect == nullptr) {
            continue;
        }
        for (std::size_t prerequisite = 0; prerequisite < count; ++prerequisite) {
            if (dependent == prerequisite || applications[prerequisite].effect == nullptr) {
                continue;
            }
            if (!effect_names_match_dependency(*applications[dependent].effect, *applications[prerequisite].effect)) {
                continue;
            }
            outgoing[prerequisite].push_back(dependent);
            ++incoming[dependent];
            ++edges;
        }
    }
    if (edges == 0U) {
        return applications;
    }

    std::vector<LayerEffectApplication> ordered;
    ordered.reserve(count);
    std::vector<bool> emitted(count, false);
    std::size_t emitted_count = 0;
    while (emitted_count < count) {
        bool made_progress = false;
        for (std::size_t i = 0; i < count; ++i) {
            if (emitted[i] || incoming[i] != 0U) {
                continue;
            }
            ordered.push_back(applications[i]);
            emitted[i] = true;
            ++emitted_count;
            made_progress = true;
            for (const auto child : outgoing[i]) {
                if (incoming[child] != 0U) {
                    --incoming[child];
                }
            }
        }
        if (!made_progress) {
            // Dependency loops fall back to the pre-sorted timestamp order for the remaining loop.
            for (std::size_t i = 0; i < count; ++i) {
                if (!emitted[i]) {
                    ordered.push_back(applications[i]);
                    emitted[i] = true;
                    ++emitted_count;
                }
            }
        }
    }
    return ordered;
}

[[nodiscard]] std::vector<LayerEffectApplication> collect_layer_effects(const GameState& game,
                                                                        ObjectId target_id,
                                                                        bool (*has_payload)(const StaticEffectDefinition&)) {
    std::vector<LayerEffectApplication> applications;
    u32 discovery = 0;
    for (const auto& source : game.objects) {
        const auto* source_def = current_definition_for_object(game, source);
        if (source_def == nullptr) {
            continue;
        }
        for (const auto& effect : source_def->static_effects) {
            ++discovery;
            if (!has_payload(effect) || !static_effect_candidate_applies_to_object(game, source, effect, target_id)) {
                continue;
            }
            applications.push_back(LayerEffectApplication{.effect = &effect, .timestamp = source_static_effect_timestamp(source), .discovery_order = discovery});
        }
    }
    for (const auto& continuous : game.continuous_effects) {
        ++discovery;
        if (!has_payload(continuous.effect) || !continuous_effect_candidate_applies_to_object(game, continuous, target_id)) {
            continue;
        }
        applications.push_back(LayerEffectApplication{.effect = &continuous.effect, .timestamp = continuous.timestamp, .discovery_order = discovery});
    }
    return dependency_ordered_layer_effects(std::move(applications));
}

[[nodiscard]] bool type_mask_matches_static_effect(u32 target_type_mask, u32 affected_type_mask) noexcept {
    if (affected_type_mask == TypeNone) {
        return true;
    }
    return type_masks_overlap(target_type_mask, affected_type_mask);
}

[[nodiscard]] bool static_effect_applies_to_types(const GameState& game,
                                                  const GameObject& source,
                                                  const StaticEffectDefinition& effect,
                                                  ObjectId target_id,
                                                  u32 target_type_mask) noexcept {
    if (!static_effect_candidate_applies_to_object(game, source, effect, target_id)) {
        return false;
    }
    return type_mask_matches_static_effect(target_type_mask, effect.affected_type_mask);
}

[[maybe_unused]] [[nodiscard]] bool static_effect_applies_to(const GameState& game, const GameObject& source, const StaticEffectDefinition& effect, ObjectId target_id) noexcept {
    if (!target_id.valid() || target_id.value > game.objects.size()) {
        return false;
    }
    return static_effect_applies_to_types(game, source, effect, target_id, object_type_mask(game, target_id));
}

[[nodiscard]] bool continuous_target_matches(const GameState& game, const ContinuousEffectTarget& locked, ObjectId target_id) noexcept {
    if (locked.target.kind != TargetKind::Object || locked.target.object != target_id || !target_id.valid() || target_id.value > game.objects.size()) {
        return false;
    }
    const auto& target = game.objects[target_id.value - 1U];
    return target.zone == Zone::Battlefield && !target.ceased_to_exist && target.zone_change_index == locked.object_zone_change_index;
}

[[nodiscard]] bool continuous_effect_applies_to_types(const GameState& game,
                                                      const ContinuousEffectDefinition& continuous,
                                                      ObjectId target_id,
                                                      u32 target_type_mask) noexcept {
    if (!continuous_effect_candidate_applies_to_object(game, continuous, target_id)) {
        return false;
    }
    return type_mask_matches_static_effect(target_type_mask, continuous.effect.affected_type_mask);
}

[[maybe_unused]] [[nodiscard]] bool continuous_effect_applies_to(const GameState& game, const ContinuousEffectDefinition& continuous, ObjectId target_id) noexcept {
    if (!target_id.valid() || target_id.value > game.objects.size()) {
        return false;
    }
    return continuous_effect_applies_to_types(game, continuous, target_id, object_type_mask(game, target_id));
}

[[nodiscard]] u32 current_definition_index_for_object(const GameState& game, const GameObject& obj) noexcept {
    if (obj.has_copy_effect && obj.copied_definition_index < game.definitions.size()) {
        return obj.copied_definition_index;
    }
    return obj.definition_index;
}

[[nodiscard]] const CardDefinition* current_definition_for_object(const GameState& game, const GameObject& obj) noexcept {
    const u32 index = current_definition_index_for_object(game, obj);
    if (index >= game.definitions.size()) {
        return nullptr;
    }
    return &game.definitions[index];
}


[[nodiscard]] u32 derived_ability_mask(const GameState& game, ObjectId id) noexcept {
    if (!id.valid() || id.value > game.objects.size()) {
        return AbilityNone;
    }
    const auto& obj = game.objects[id.value - 1U];
    u32 abilities = AbilityNone;
    if (const auto* def = current_definition_for_object(game, obj)) {
        abilities |= def->ability_mask;
    }
    const auto target = TargetRef{.kind = TargetKind::Object, .object = id};
    for (const auto& attachment : game.objects) {
        if (attachment.zone != Zone::Battlefield || !target_refs_equal(attachment.attached_to, target)) {
            continue;
        }
        if (const auto* attachment_def = current_definition_for_object(game, attachment)) {
            abilities |= attachment_def->attachment_granted_ability_mask;
        }
    }
    const u32 layer4_types = object_type_mask(game, id);
    auto apply_layer6_payload = [&](const StaticEffectDefinition& effect) {
        abilities |= effect.granted_ability_mask;
        abilities &= ~effect.removed_ability_mask;
    };
    for (const auto& application : collect_layer_effects(game, id, static_effect_has_ability_layer_payload)) {
        if (application.effect != nullptr && type_mask_matches_static_effect(layer4_types, application.effect->affected_type_mask)) {
            apply_layer6_payload(*application.effect);
        }
    }
    return abilities;
}

[[nodiscard]] bool source_has_keyword(const GameState& game, ObjectId id, KeywordAbilityMask ability) noexcept {
    return has_ability_mask(derived_ability_mask(game, id), ability);
}

[[nodiscard]] u32 colors_from_mana_cost(const ManaCost& cost) noexcept {
    u32 colors = ColorNone;
    if (cost.white != 0U) { colors |= ColorWhite; }
    if (cost.blue != 0U) { colors |= ColorBlue; }
    if (cost.black != 0U) { colors |= ColorBlack; }
    if (cost.red != 0U) { colors |= ColorRed; }
    if (cost.green != 0U) { colors |= ColorGreen; }
    return colors;
}

[[nodiscard]] u32 legal_color_mask(u32 colors) noexcept {
    return colors & static_cast<u32>(ColorAll);
}

[[nodiscard]] bool valid_player_index(const GameState& game, PlayerId id) noexcept {
    return id.valid() && id.value <= game.players.size();
}

[[nodiscard]] bool valid_object_index(const GameState& game, ObjectId id) noexcept {
    return id.valid() && id.value <= game.objects.size();
}

[[nodiscard]] bool same_target(TargetRef a, TargetRef b) noexcept {
    return target_refs_equal(a, b);
}

[[nodiscard]] bool counter_kind_is_object(CounterKind counter_kind) noexcept {
    switch (counter_kind) {
        case CounterKind::PlusOnePlusOne:
        case CounterKind::MinusOneMinusOne:
        case CounterKind::Loyalty:
        case CounterKind::Defense:
        case CounterKind::Charge:
            return true;
        case CounterKind::Poison:
        case CounterKind::Count:
            return false;
    }
    return false;
}

u32& counter_slot(CounterSet& counters, CounterKind counter_kind) {
    switch (counter_kind) {
        case CounterKind::PlusOnePlusOne: return counters.plus_one_plus_one;
        case CounterKind::MinusOneMinusOne: return counters.minus_one_minus_one;
        case CounterKind::Loyalty: return counters.loyalty;
        case CounterKind::Defense: return counters.defense;
        case CounterKind::Charge: return counters.charge;
        case CounterKind::Poison:
        case CounterKind::Count:
            break;
    }
    throw std::invalid_argument("counter kind is not an object counter in this scaffold");
}

u32 counter_slot(const CounterSet& counters, CounterKind counter_kind) noexcept {
    switch (counter_kind) {
        case CounterKind::PlusOnePlusOne: return counters.plus_one_plus_one;
        case CounterKind::MinusOneMinusOne: return counters.minus_one_minus_one;
        case CounterKind::Loyalty: return counters.loyalty;
        case CounterKind::Defense: return counters.defense;
        case CounterKind::Charge: return counters.charge;
        case CounterKind::Poison:
        case CounterKind::Count:
            break;
    }
    return 0U;
}

u32 record_state_based_action(GameState& game,
                              StateBasedActionKind kind,
                              ObjectId object_id,
                              PlayerId player_id,
                              std::string log_kind,
                              std::string detail,
                              u32 check_index = 1U,
                              u32 pass_index = 1U,
                              u32 pass_candidate_count = 1U) {
    StateBasedActionRecord record{};
    record.sequence = game.next_event_sequence;
    record.check_index = check_index;
    record.pass_index = pass_index;
    record.pass_candidate_count = pass_candidate_count;
    record.kind = kind;
    record.object = object_id;
    record.player = player_id;
    if (valid_object_index(game, object_id)) {
        const auto& obj = object(game, object_id);
        record.object_zone = obj.zone;
        record.object_zone_change_index = obj.zone_change_index;
        record.damage_marked = obj.damage_marked;
        record.deathtouch_damage_marked = obj.deathtouch_damage_marked;
        record.plus_one_plus_one_counters = obj.counters.plus_one_plus_one;
        record.minus_one_minus_one_counters = obj.counters.minus_one_minus_one;
        record.loyalty_counters = obj.counters.loyalty;
        record.defense_counters = obj.counters.defense;
        record.regeneration_shields_before = obj.regeneration_shields;
        record.regeneration_shields_after = obj.regeneration_shields;
        record.indestructible = object_has_ability(game, object_id, AbilityIndestructible);
        if (obj.zone == Zone::Battlefield && !obj.ceased_to_exist) {
            record.effective_power = effective_power(game, object_id);
            record.effective_toughness = effective_toughness(game, object_id);
        }
        if (!record.player.valid()) {
            record.player = obj.controller;
        }
    }
    const u32 record_index = static_cast<u32>(game.state_based_action_records.size() + 1U);
    game.state_based_action_records.push_back(std::move(record));
    record_event_with_links(game,
                            std::move(log_kind),
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::StateBasedAction,
                                .object = object_id,
                                .player = game.state_based_action_records.back().player,
                                .state_based_action_record_index = record_index
                            });
    return record_index;
}

void link_state_based_action_to_zone_change(GameState& game, u32 record_index, std::size_t first_zone_change_index) {
    if (record_index == 0U || record_index > game.state_based_action_records.size()) {
        return;
    }
    auto& record = game.state_based_action_records[record_index - 1U];
    if (!record.object.valid()) {
        return;
    }
    for (std::size_t i = first_zone_change_index; i < game.zone_change_records.size(); ++i) {
        const auto& zone_record = game.zone_change_records[i];
        if (zone_record.object == record.object) {
            record.zone_change_record_index = static_cast<u32>(i + 1U);
            record.object_left_battlefield = zone_record.from_zone == Zone::Battlefield && zone_record.to_zone != Zone::Battlefield;
            return;
        }
    }
}

void finish_state_based_action_regeneration_snapshot(GameState& game, u32 record_index) {
    if (record_index == 0U || record_index > game.state_based_action_records.size()) {
        return;
    }
    auto& record = game.state_based_action_records[record_index - 1U];
    if (!valid_object_index(game, record.object)) {
        return;
    }
    const auto& obj = object(game, record.object);
    record.regeneration_shields_after = obj.regeneration_shields;
    record.regeneration_applied = record.kind == StateBasedActionKind::CreatureDamageDestroy &&
                                  obj.zone == Zone::Battlefield &&
                                  record.regeneration_shields_before > record.regeneration_shields_after;
}

bool cancel_opposing_power_toughness_counters(GameState& game, ObjectId object_id, u32 check_index = 1U, u32 pass_index = 1U, u32 pass_candidate_count = 1U) {
    auto& obj = object(game, object_id);
    const u32 pairs = std::min(obj.counters.plus_one_plus_one, obj.counters.minus_one_minus_one);
    if (pairs == 0U) {
        return false;
    }
    record_state_based_action(game,
                              StateBasedActionKind::CounterPairCancel,
                              object_id,
                              obj.controller,
                              "sba_counter_pair_cancel",
                              object_label(game, object_id) + " removed " + std::to_string(pairs) + " +1/+1 and -1/-1 counter pair(s)",
                              check_index,
                              pass_index,
                              pass_candidate_count);
    const u32 plus_before = obj.counters.plus_one_plus_one;
    const u32 minus_before = obj.counters.minus_one_minus_one;
    obj.counters.plus_one_plus_one -= pairs;
    obj.counters.minus_one_minus_one -= pairs;
    record_object_counter_change(game,
                                 object_id,
                                 CounterKind::PlusOnePlusOne,
                                 CounterChangeKind::ObjectRemoved,
                                 pairs,
                                 plus_before,
                                 obj.counters.plus_one_plus_one,
                                 "sba_counter_removed",
                                 object_label(game, object_id) + " removed " + std::to_string(pairs) + " +1/+1 counter(s) for SBA pair cancellation");
    record_object_counter_change(game,
                                 object_id,
                                 CounterKind::MinusOneMinusOne,
                                 CounterChangeKind::ObjectRemoved,
                                 pairs,
                                 minus_before,
                                 obj.counters.minus_one_minus_one,
                                 "sba_counter_removed",
                                 object_label(game, object_id) + " removed " + std::to_string(pairs) + " -1/-1 counter(s) for SBA pair cancellation");
    return true;
}

struct DamagePreventionResult {
    u32 remaining = 0;
    u32 prevented = 0;
    u32 first_record_index = 0;
    u32 record_count = 0;
};

struct DamagePreventionCandidate {
    std::size_t shield_index = 0;
    u32 discovery_order = 0;
};

[[nodiscard]] PlayerId damage_prevention_affected_player(const GameState& game, TargetRef target) noexcept {
    if (target.kind == TargetKind::Player) {
        return target.player;
    }
    if (target.kind == TargetKind::Object && valid_object_index(game, target.object)) {
        const auto& obj = object(game, target.object);
        return obj.controller.valid() ? obj.controller : obj.owner;
    }
    return PlayerId{};
}

[[nodiscard]] std::vector<DamagePreventionCandidate> collect_damage_prevention_candidates(const GameState& game, TargetRef target) {
    std::vector<DamagePreventionCandidate> candidates;
    candidates.reserve(game.damage_prevention_shields.size());
    u32 discovery_order = 0U;
    for (std::size_t i = 0; i < game.damage_prevention_shields.size(); ++i) {
        ++discovery_order;
        const auto& shield = game.damage_prevention_shields[i];
        if (shield.remaining == 0U || !same_target(shield.target, target)) {
            continue;
        }
        candidates.push_back(DamagePreventionCandidate{.shield_index = i, .discovery_order = discovery_order});
    }
    std::stable_sort(candidates.begin(), candidates.end(), [&game](const DamagePreventionCandidate& lhs, const DamagePreventionCandidate& rhs) {
        const auto& left = game.damage_prevention_shields[lhs.shield_index];
        const auto& right = game.damage_prevention_shields[rhs.shield_index];
        if (left.choice_rank != right.choice_rank) {
            return left.choice_rank > right.choice_rank;
        }
        if (left.id != right.id) {
            return left.id < right.id;
        }
        return lhs.discovery_order < rhs.discovery_order;
    });
    return candidates;
}

DamagePreventionResult apply_damage_prevention(GameState& game, TargetRef target, u32 amount) {
    if (amount == 0U || game.damage_prevention_shields.empty()) {
        return DamagePreventionResult{.remaining = amount};
    }

    DamagePreventionResult result{.remaining = amount};
    u32 remaining_damage = amount;
    u32 prevented_total = 0;
    u32 pass_index = 0U;
    const PlayerId affected_player = damage_prevention_affected_player(game, target);

    while (remaining_damage != 0U) {
        const auto candidates = collect_damage_prevention_candidates(game, target);
        if (candidates.empty()) {
            break;
        }
        ++pass_index;
        const u32 candidate_count = static_cast<u32>(candidates.size());
        auto& shield = game.damage_prevention_shields[candidates.front().shield_index];
        const u32 before = shield.remaining;
        const u32 prevented = std::min(shield.remaining, remaining_damage);
        shield.remaining -= prevented;
        remaining_damage -= prevented;
        prevented_total += prevented;
        const std::string label = shield.label.empty() ? "damage prevention shield" : shield.label;
        if (result.first_record_index == 0U) {
            result.first_record_index = static_cast<u32>(game.damage_prevention_records.size() + 1U);
        }
        ++result.record_count;
        record_damage_prevention_change(game,
                                        DamagePreventionRecord{
                                            .kind = DamagePreventionRecordKind::ShieldConsumed,
                                            .shield_id = shield.id,
                                            .target = shield.target,
                                            .amount = prevented,
                                            .remaining_before = before,
                                            .remaining_after = shield.remaining,
                                            .affected_player = affected_player,
                                            .choice_rank = shield.choice_rank,
                                            .candidate_count = candidate_count,
                                            .pass_index = pass_index,
                                            .chosen_among_multiple = candidate_count > 1U,
                                            .label = shield.label
                                        },
                                        "damage_prevented",
                                        label + " prevented " + std::to_string(prevented) + " damage to " + target_label(game, target));
    }
    game.damage_prevention_shields.erase(
        std::remove_if(game.damage_prevention_shields.begin(), game.damage_prevention_shields.end(), [](const DamagePreventionShield& shield) {
            return shield.remaining == 0U;
        }),
        game.damage_prevention_shields.end());
    if (prevented_total != 0U && remaining_damage == 0U) {
        record_event(game, "damage_fully_prevented", target_label(game, target) + " prevented all " + std::to_string(amount) + " damage");
    }
    result.remaining = remaining_damage;
    result.prevented = prevented_total;
    return result;
}

DamagePreventionResult apply_unpreventable_damage_prevention(GameState& game, TargetRef target, u32 amount) {
    DamagePreventionResult result{.remaining = amount};
    if (amount == 0U || game.damage_prevention_shields.empty()) {
        return result;
    }

    const auto candidates = collect_damage_prevention_candidates(game, target);
    const PlayerId affected_player = damage_prevention_affected_player(game, target);
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        const auto& shield = game.damage_prevention_shields[candidates[i].shield_index];
        const u32 pass_index = static_cast<u32>(i + 1U);
        const u32 candidate_count = static_cast<u32>(candidates.size() - i);
        const std::string label = shield.label.empty() ? "damage prevention shield" : shield.label;
        if (result.first_record_index == 0U) {
            result.first_record_index = static_cast<u32>(game.damage_prevention_records.size() + 1U);
        }
        ++result.record_count;
        record_damage_prevention_change(game,
                                        DamagePreventionRecord{
                                            .kind = DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage,
                                            .shield_id = shield.id,
                                            .target = shield.target,
                                            .amount = std::min(shield.remaining, amount),
                                            .remaining_before = shield.remaining,
                                            .remaining_after = shield.remaining,
                                            .affected_player = affected_player,
                                            .choice_rank = shield.choice_rank,
                                            .candidate_count = candidate_count,
                                            .pass_index = pass_index,
                                            .chosen_among_multiple = candidate_count > 1U,
                                            .label = shield.label
                                        },
                                        "damage_prevention_applied_unpreventable",
                                        label + " applied to unpreventable damage to " + target_label(game, target) + " without reducing the shield");
    }
    return result;
}

[[nodiscard]] TargetRef damage_target_snapshot(const GameState& game, TargetRef target) {
    if (target.kind == TargetKind::Object && valid_object_index(game, target.object)) {
        target.object_zone_change_index = object(game, target.object).zone_change_index;
    }
    return target;
}

[[nodiscard]] std::string target_label(const GameState& game, TargetRef target) {
    switch (target.kind) {
        case TargetKind::Player:
            return valid_player_index(game, target.player) ? player(game, target.player).name : ("player#" + std::to_string(target.player.value));
        case TargetKind::Object:
            return valid_object_index(game, target.object) ? object_label(game, target.object) : ("object#" + std::to_string(target.object.value));
        case TargetKind::None:
            return "<no target>";
    }
    return "<unknown target>";
}

[[nodiscard]] std::string target_list_label(const GameState& game, const std::vector<TargetRef>& targets) {
    if (targets.empty()) {
        return "<no targets>";
    }
    std::string out;
    for (std::size_t i = 0; i < targets.size(); ++i) {
        if (i != 0U) {
            out += ",";
        }
        out += target_label(game, targets[i]);
    }
    return out;
}

[[nodiscard]] u32& mana_slot(ManaPool& pool, ManaSymbol symbol) {
    switch (symbol) {
        case ManaSymbol::White: return pool.white;
        case ManaSymbol::Blue: return pool.blue;
        case ManaSymbol::Black: return pool.black;
        case ManaSymbol::Red: return pool.red;
        case ManaSymbol::Green: return pool.green;
        case ManaSymbol::Colorless: return pool.colorless;
        case ManaSymbol::Count: break;
    }
    throw std::invalid_argument("invalid mana symbol");
}

[[nodiscard]] bool spend_mana_from_copy(ManaPool& pool, const ManaCost& cost) noexcept {
    if (pool.white < cost.white || pool.blue < cost.blue || pool.black < cost.black ||
        pool.red < cost.red || pool.green < cost.green || pool.colorless < cost.colorless) {
        return false;
    }
    pool.white -= cost.white;
    pool.blue -= cost.blue;
    pool.black -= cost.black;
    pool.red -= cost.red;
    pool.green -= cost.green;
    pool.colorless -= cost.colorless;

    u32 generic_remaining = cost.generic;
    auto spend_generic = [&generic_remaining](u32& bucket) {
        const u32 spent = std::min(bucket, generic_remaining);
        bucket -= spent;
        generic_remaining -= spent;
    };
    spend_generic(pool.colorless);
    spend_generic(pool.white);
    spend_generic(pool.blue);
    spend_generic(pool.black);
    spend_generic(pool.red);
    spend_generic(pool.green);
    return generic_remaining == 0U;
}

[[nodiscard]] std::string mana_pool_summary(const ManaPool& pool) {
    std::ostringstream out;
    out << "W=" << pool.white
        << " U=" << pool.blue
        << " B=" << pool.black
        << " R=" << pool.red
        << " G=" << pool.green
        << " C=" << pool.colorless;
    return out.str();
}

[[nodiscard]] std::string mana_cost_summary(const ManaCost& cost) {
    std::ostringstream out;
    out << "generic=" << cost.generic
        << " W=" << cost.white
        << " U=" << cost.blue
        << " B=" << cost.black
        << " R=" << cost.red
        << " G=" << cost.green
        << " C=" << cost.colorless;
    return out.str();
}


void add_mana_pool_to_pool(ManaPool& pool, const ManaPool& produced) noexcept {
    pool.white += produced.white;
    pool.blue += produced.blue;
    pool.black += produced.black;
    pool.red += produced.red;
    pool.green += produced.green;
    pool.colorless += produced.colorless;
}

[[nodiscard]] ManaPool single_mana_pool(ManaSymbol symbol, u32 amount = 1U) {
    ManaPool pool;
    mana_slot(pool, symbol) = amount;
    return pool;
}

[[nodiscard]] u32 total_mana_ability_count_for_definition(const CardDefinition& def) noexcept {
    return (def.taps_for_mana ? 1U : 0U) + static_cast<u32>(def.mana_abilities.size());
}

[[nodiscard]] bool mana_ability_definition_for_index(const CardDefinition& def, u32 index, ManaAbilityDefinition& out) noexcept {
    if (index == 0U) {
        return false;
    }
    u32 offset = index;
    if (def.taps_for_mana) {
        if (offset == 1U) {
            out = ManaAbilityDefinition{};
            out.name = "tap_for_mana";
            out.tap_cost = true;
            out.produces = single_mana_pool(def.tap_mana_symbol, 1U);
            return true;
        }
        --offset;
    }
    if (offset == 0U || offset > def.mana_abilities.size()) {
        return false;
    }
    out = def.mana_abilities[offset - 1U];
    return true;
}

[[nodiscard]] std::string mana_ability_label(const CardDefinition& def, u32 index) {
    ManaAbilityDefinition ability;
    if (!mana_ability_definition_for_index(def, index, ability)) {
        return "mana_ability#" + std::to_string(index);
    }
    if (!ability.name.empty()) {
        return "mana_ability#" + std::to_string(index) + ":" + ability.name;
    }
    return "mana_ability#" + std::to_string(index);
}

struct ManaAbilityCandidate {
    ObjectId object_id{};
    u32 ability_index = 0;
    ManaPool produces{};
    bool tap_cost = false;
};

[[nodiscard]] bool candidate_tap_source_already_used(const std::vector<ObjectId>& tapped_sources, ObjectId id) noexcept {
    return std::find(tapped_sources.begin(), tapped_sources.end(), id) != tapped_sources.end();
}

[[nodiscard]] std::vector<ObjectId> activation_locked_tap_sources(const ActivatedAbilityDefinition& ability,
                                                                  ObjectId source_object) {
    if (!ability.tap_cost || !source_object.valid()) {
        return {};
    }
    return {source_object};
}

[[nodiscard]] bool select_mana_ability_pay_plan_excluding_tap_sources(const GameState& game,
                                                                      PlayerId player_id,
                                                                      const ManaCost& cost,
                                                                      const std::vector<ObjectId>& locked_tap_sources,
                                                                      std::vector<ManaAbilityCandidate>& plan) noexcept {
    plan.clear();
    if (!valid_player_index(game, player_id)) {
        return false;
    }
    const ManaPool initial_pool = player(game, player_id).mana_pool;
    ManaPool copy = initial_pool;
    if (spend_mana_from_copy(copy, cost)) {
        return true;
    }

    std::vector<ManaAbilityCandidate> candidates;
    const auto& battlefield = zone(game, player_id, Zone::Battlefield);
    for (const auto object_id : battlefield) {
        if (!valid_object_index(game, object_id)) {
            continue;
        }
        const auto& obj = object(game, object_id);
        const auto* def_ptr = current_definition_for_object(game, obj);
        if (def_ptr == nullptr) {
            continue;
        }
        const auto& def = *def_ptr;
        const u32 count = total_mana_ability_count_for_definition(def);
        for (u32 ability_index = 1U; ability_index <= count; ++ability_index) {
            ManaAbilityDefinition ability;
            if (!mana_ability_definition_for_index(def, ability_index, ability) || !ability.active()) {
                continue;
            }
            if (!can_activate_mana_ability(game, player_id, object_id, ability_index)) {
                continue;
            }
            if (ability.tap_cost && candidate_tap_source_already_used(locked_tap_sources, object_id)) {
                continue;
            }
            candidates.push_back(ManaAbilityCandidate{.object_id = object_id, .ability_index = ability_index, .produces = ability.produces, .tap_cost = ability.tap_cost});
        }
    }
    if (candidates.empty()) {
        return false;
    }

    std::vector<std::size_t> chosen;
    std::vector<ObjectId> tapped_sources;
    std::vector<std::size_t> best_indices;
    u32 best_leftover = 0U;
    u32 best_produced = 0U;
    bool found = false;
    constexpr std::uint64_t max_search_nodes = 250000U;
    std::uint64_t visited = 0U;

    auto candidate_available = [&](std::size_t idx) noexcept {
        const auto& candidate = candidates[idx];
        return !candidate.tap_cost || !candidate_tap_source_already_used(tapped_sources, candidate.object_id);
    };

    auto better_than_best = [&](const std::vector<std::size_t>& indices, u32 leftover, u32 produced) noexcept {
        if (!found) {
            return true;
        }
        if (indices.size() != best_indices.size()) {
            return indices.size() < best_indices.size();
        }
        if (leftover != best_leftover) {
            return leftover < best_leftover;
        }
        if (produced != best_produced) {
            return produced < best_produced;
        }
        return indices < best_indices;
    };

    auto evaluate_selection = [&]() {
        ManaPool simulated = initial_pool;
        u32 produced = 0U;
        for (const auto idx : chosen) {
            add_mana_pool_to_pool(simulated, candidates[idx].produces);
            produced += candidates[idx].produces.total();
        }
        ManaPool after = simulated;
        if (!spend_mana_from_copy(after, cost)) {
            return;
        }
        const u32 leftover = after.total();
        if (better_than_best(chosen, leftover, produced)) {
            best_indices = chosen;
            best_leftover = leftover;
            best_produced = produced;
            found = true;
        }
    };

    auto dfs = [&](auto&& self, std::size_t start) -> void {
        if (visited++ >= max_search_nodes) {
            return;
        }
        if (found && chosen.size() >= best_indices.size()) {
            return;
        }
        evaluate_selection();
        if (found && chosen.size() >= best_indices.size()) {
            return;
        }
        for (std::size_t idx = start; idx < candidates.size(); ++idx) {
            if (!candidate_available(idx)) {
                continue;
            }
            chosen.push_back(idx);
            const bool pushed_tap_source = candidates[idx].tap_cost;
            if (pushed_tap_source) {
                tapped_sources.push_back(candidates[idx].object_id);
            }
            self(self, idx + 1U);
            if (pushed_tap_source) {
                tapped_sources.pop_back();
            }
            chosen.pop_back();
        }
    };

    dfs(dfs, 0U);
    if (!found) {
        return false;
    }
    for (const auto idx : best_indices) {
        plan.push_back(candidates[idx]);
    }
    return true;
}

[[nodiscard]] bool select_mana_ability_pay_plan(const GameState& game,
                                                PlayerId player_id,
                                                const ManaCost& cost,
                                                std::vector<ManaAbilityCandidate>& plan) noexcept {
    return select_mana_ability_pay_plan_excluding_tap_sources(game, player_id, cost, {}, plan);
}

[[nodiscard]] bool can_pay_mana_cost_with_available_mana_excluding_tap_sources(const GameState& game,
                                                                              PlayerId player_id,
                                                                              const ManaCost& cost,
                                                                              const std::vector<ObjectId>& locked_tap_sources) noexcept {
    std::vector<ManaAbilityCandidate> plan;
    return select_mana_ability_pay_plan_excluding_tap_sources(game, player_id, cost, locked_tap_sources, plan);
}

[[nodiscard]] std::vector<ManaPaymentPlanLockedSourceRecord> mana_payment_locked_source_records(const GameState& game,
                                                                                                     const std::vector<ObjectId>& locked_tap_sources) {
    std::vector<ManaPaymentPlanLockedSourceRecord> records;
    records.reserve(locked_tap_sources.size());
    for (const auto locked_source : locked_tap_sources) {
        records.push_back(ManaPaymentPlanLockedSourceRecord{
            .source = locked_source,
            .source_zone_change_index = valid_object_index(game, locked_source) ? object(game, locked_source).zone_change_index : 0U
        });
    }
    return records;
}

[[nodiscard]] std::vector<ManaPaymentPlanStepRecord> mana_payment_step_records(const GameState& game,
                                                                              const std::vector<ManaAbilityCandidate>& plan) {
    std::vector<ManaPaymentPlanStepRecord> records;
    records.reserve(plan.size());
    for (const auto& step : plan) {
        records.push_back(ManaPaymentPlanStepRecord{
            .source = step.object_id,
            .source_zone_change_index = valid_object_index(game, step.object_id) ? object(game, step.object_id).zone_change_index : 0U,
            .mana_ability_index = step.ability_index,
            .produces = step.produces,
            .produced_mana_change_record_index = 0U,
            .tap_cost = step.tap_cost
        });
    }
    return records;
}

[[nodiscard]] u64 mana_payment_plan_hash_from_records(PlayerId player_id,
                                                     const ManaCost& cost,
                                                     const ManaPool& pool_before_plan,
                                                     const std::vector<ManaPaymentPlanLockedSourceRecord>& locked_tap_sources,
                                                     const std::vector<ManaPaymentPlanStepRecord>& steps) noexcept {
    StableHasher h;
    hash_into(h, std::string("MTGSim.ManaAutoPaymentPlan.v4"));
    hash_into(h, player_id);
    hash_into(h, cost);
    hash_into(h, pool_before_plan);
    hash_vector(h, locked_tap_sources);
    hash_into(h, static_cast<u64>(steps.size()));
    for (const auto& step : steps) {
        hash_mana_payment_plan_step_identity(h, step);
    }
    return h.value();
}

[[nodiscard]] u64 mana_payment_plan_hash(const GameState& game,
                                         PlayerId player_id,
                                         const ManaCost& cost,
                                         const std::vector<ManaAbilityCandidate>& plan,
                                         const std::vector<ObjectId>& locked_tap_sources) {
    const auto locked_records = mana_payment_locked_source_records(game, locked_tap_sources);
    const auto step_records = mana_payment_step_records(game, plan);
    return mana_payment_plan_hash_from_records(player_id, cost, player(game, player_id).mana_pool, locked_records, step_records);
}

[[nodiscard]] u32 record_mana_payment_plan(GameState& game,
                                           PlayerId player_id,
                                           const ManaCost& cost,
                                           const std::vector<ManaAbilityCandidate>& plan,
                                           const std::vector<ObjectId>& locked_tap_sources,
                                           u64 plan_hash) {
    ManaPaymentPlanRecord record{};
    record.sequence = game.next_event_sequence;
    record.player = player_id;
    record.cost = cost;
    record.pool_before_plan = player(game, player_id).mana_pool;
    record.locked_tap_sources = mana_payment_locked_source_records(game, locked_tap_sources);
    record.mana_ability_steps = mana_payment_step_records(game, plan);
    record.plan_hash = plan_hash;
    const u32 record_index = static_cast<u32>(game.mana_payment_plan_records.size() + 1U);
    game.mana_payment_plan_records.push_back(std::move(record));
    record_event_with_links(game,
                            "mana_auto_plan",
                            player(game, player_id).name + " selected " + std::to_string(plan.size()) +
                                " mana ability activation(s), locked " + std::to_string(locked_tap_sources.size()) +
                                " tap source(s), plan_hash=" + std::to_string(plan_hash) + " for cost " + mana_cost_summary(cost),
                            EventRecordLinks{
                                .kind = EventRecordKind::ManaPaymentPlan,
                                .player = player_id,
                                .mana_payment_plan_record_index = record_index
                            });
    return record_index;
}

[[nodiscard]] bool sacrifice_cost_matches_object(const GameState& game,
                                                 PlayerId payer,
                                                 const SacrificeCostDefinition& cost,
                                                 ObjectId object_id) noexcept {
    if (!cost.active() || !valid_player_index(game, payer) || !valid_object_index(game, object_id)) {
        return false;
    }
    const auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield || obj.controller != payer || obj.ceased_to_exist) {
        return false;
    }
    const u32 types = object_type_mask(game, object_id);
    return type_masks_overlap(types, cost.required_type_mask);
}

[[nodiscard]] std::vector<ObjectId> select_sacrifice_cost_objects(const GameState& game,
                                                                  PlayerId payer,
                                                                  const SacrificeCostDefinition& cost) {
    std::vector<ObjectId> selected;
    if (!cost.active() || !valid_player_index(game, payer)) {
        return selected;
    }
    for (const auto object_id : zone(game, payer, Zone::Battlefield)) {
        if (sacrifice_cost_matches_object(game, payer, cost, object_id)) {
            selected.push_back(object_id);
            if (selected.size() == cost.count) {
                return selected;
            }
        }
    }
    selected.clear();
    return selected;
}

[[nodiscard]] bool can_pay_sacrifice_cost(const GameState& game, PlayerId payer, const SacrificeCostDefinition& cost) {
    if (!cost.active()) {
        return true;
    }
    return select_sacrifice_cost_objects(game, payer, cost).size() == cost.count;
}

[[nodiscard]] std::string sacrifice_cost_summary(const SacrificeCostDefinition& cost) {
    return "count=" + std::to_string(cost.count) + " type_mask=" + std::to_string(cost.required_type_mask);
}

[[nodiscard]] bool object_id_in_selection(const std::vector<ObjectId>& selected, ObjectId id) noexcept {
    return std::find(selected.begin(), selected.end(), id) != selected.end();
}

[[nodiscard]] u32 selected_attachment_depth(const GameState& game,
                                            ObjectId object_id,
                                            const std::vector<ObjectId>& selected) noexcept {
    u32 depth = 0U;
    ObjectId current = object_id;
    std::vector<ObjectId> seen;
    while (valid_object_index(game, current)) {
        if (object_id_in_selection(seen, current)) {
            break;
        }
        seen.push_back(current);
        const auto& obj = object(game, current);
        if (obj.attached_to.kind != TargetKind::Object || !obj.attached_to.object.valid() ||
            !object_id_in_selection(selected, obj.attached_to.object)) {
            break;
        }
        ++depth;
        current = obj.attached_to.object;
    }
    return depth;
}

void order_sacrifice_cost_objects_for_payment(const GameState& game, std::vector<ObjectId>& selected) {
    if (selected.size() < 2U) {
        return;
    }
    std::stable_sort(selected.begin(), selected.end(), [&](ObjectId lhs, ObjectId rhs) {
        const u32 lhs_depth = selected_attachment_depth(game, lhs, selected);
        const u32 rhs_depth = selected_attachment_depth(game, rhs, selected);
        if (lhs_depth != rhs_depth) {
            return lhs_depth > rhs_depth;
        }
        return false;
    });
}

[[nodiscard]] std::vector<u64> selected_zone_change_indices_before_payment(const GameState& game,
                                                                            const std::vector<ObjectId>& selected) {
    std::vector<u64> indices;
    indices.reserve(selected.size());
    for (const auto object_id : selected) {
        indices.push_back(valid_object_index(game, object_id) ? object(game, object_id).zone_change_index : 0U);
    }
    return indices;
}

[[nodiscard]] u64 sacrifice_cost_payment_record_identity_hash(const SacrificeCostPaymentRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.SacrificeCostPaymentRecord.v1");
    hash_sacrifice_cost_payment_identity(h, record);
    return h.value();
}

u32 record_sacrifice_cost_payment(GameState& game, SacrificeCostPaymentRecord record) {
    record.payment_hash = sacrifice_cost_payment_record_identity_hash(record);
    const u32 record_index = static_cast<u32>(game.sacrifice_cost_payment_records.size() + 1U);
    game.sacrifice_cost_payment_records.push_back(std::move(record));
    return record_index;
}

bool pay_selected_sacrifice_cost(GameState& game,
                                  PlayerId payer,
                                  const SacrificeCostDefinition& cost,
                                  const std::vector<ObjectId>& selected,
                                  std::string_view source_label,
                                  ObjectId source_object = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    if (selected.size() != cost.count) {
        record_event(game, "pay_sacrifice_cost_failed", player(game, payer).name + " could not pay sacrifice cost for " + std::string(source_label) + " " + sacrifice_cost_summary(cost));
        return false;
    }
    for (const auto object_id : selected) {
        if (!sacrifice_cost_matches_object(game, payer, cost, object_id)) {
            record_event(game, "pay_sacrifice_cost_failed", player(game, payer).name + " selected illegal sacrifice " + object_label(game, object_id) + " for " + std::string(source_label));
            return false;
        }
    }
    auto ordered_selection = selected;
    order_sacrifice_cost_objects_for_payment(game, ordered_selection);
    auto selected_zone_indices_before = selected_zone_change_indices_before_payment(game, ordered_selection);
    const u32 first_zone_change_record_index = static_cast<u32>(game.zone_change_records.size() + 1U);
    std::string detail = player(game, payer).name + " sacrificed";
    for (const auto object_id : ordered_selection) {
        detail += " " + object_label(game, object_id);
    }
    detail += " for " + std::string(source_label);
    for (const auto object_id : ordered_selection) {
        if (!sacrifice_permanent(game, payer, object_id)) {
            record_event(game, "pay_sacrifice_cost_failed", player(game, payer).name + " selected illegal sacrifice " + object_label(game, object_id) + " for " + std::string(source_label));
            return false;
        }
    }
    const u32 zone_change_record_count = static_cast<u32>(game.zone_change_records.size() + 1U - first_zone_change_record_index);
    const u64 payment_event_sequence = game.next_event_sequence;
    record_event(game, "pay_sacrifice_cost", detail);

    SacrificeCostPaymentRecord payment{};
    payment.sequence = payment_event_sequence;
    payment.payer = payer;
    payment.source_object = source_object;
    payment.cost = cost;
    payment.selected_objects = std::move(ordered_selection);
    payment.selected_zone_change_indices_before = std::move(selected_zone_indices_before);
    payment.first_zone_change_record_index = first_zone_change_record_index;
    payment.zone_change_record_count = zone_change_record_count;
    record_sacrifice_cost_payment(game, std::move(payment));
    return true;
}

bool pay_sacrifice_cost(GameState& game, PlayerId payer, const SacrificeCostDefinition& cost, std::string_view source_label, ObjectId source_object = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    return pay_selected_sacrifice_cost(game, payer, cost, select_sacrifice_cost_objects(game, payer, cost), source_label, source_object);
}

[[nodiscard]] std::vector<ObjectId> select_discard_cost_cards(const GameState& game,
                                                             PlayerId payer,
                                                             const DiscardCostDefinition& cost) {
    std::vector<ObjectId> selected;
    if (!cost.active() || !valid_player_index(game, payer)) {
        return selected;
    }
    const auto& hand = zone(game, payer, Zone::Hand);
    for (const auto card_id : hand) {
        if (!valid_object_index(game, card_id)) {
            continue;
        }
        const auto& card = object(game, card_id);
        if (card.zone == Zone::Hand && !card.ceased_to_exist) {
            selected.push_back(card_id);
            if (selected.size() == cost.count) {
                return selected;
            }
        }
    }
    selected.clear();
    return selected;
}

[[nodiscard]] bool can_pay_discard_cost_from_current_hand(const GameState& game,
                                                         PlayerId payer,
                                                         const DiscardCostDefinition& cost) {
    if (!cost.active()) {
        return true;
    }
    return select_discard_cost_cards(game, payer, cost).size() == cost.count;
}

[[nodiscard]] bool can_pay_discard_cost_after_moving_source_to_stack(const GameState& game,
                                                                    PlayerId payer,
                                                                    ObjectId source_object,
                                                                    const DiscardCostDefinition& cost) {
    if (!cost.active()) {
        return true;
    }
    if (!valid_player_index(game, payer)) {
        return false;
    }
    u32 available = 0U;
    for (const auto card_id : zone(game, payer, Zone::Hand)) {
        if (card_id == source_object) {
            continue;
        }
        if (valid_object_index(game, card_id) && object(game, card_id).zone == Zone::Hand && !object(game, card_id).ceased_to_exist) {
            ++available;
        }
    }
    return available >= cost.count;
}

[[nodiscard]] std::string discard_cost_summary(const DiscardCostDefinition& cost) {
    return "count=" + std::to_string(cost.count);
}

[[nodiscard]] u64 discard_cost_payment_record_identity_hash(const DiscardCostPaymentRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.DiscardCostPaymentRecord.v1");
    hash_discard_cost_payment_identity(h, record);
    return h.value();
}

u32 record_discard_cost_payment(GameState& game, DiscardCostPaymentRecord record) {
    record.payment_hash = discard_cost_payment_record_identity_hash(record);
    const u32 record_index = static_cast<u32>(game.discard_cost_payment_records.size() + 1U);
    game.discard_cost_payment_records.push_back(std::move(record));
    return record_index;
}

[[nodiscard]] std::string life_cost_summary(const LifeCostDefinition& cost) {
    return "amount=" + std::to_string(cost.amount);
}

[[nodiscard]] bool can_pay_life_cost(const GameState& game, PlayerId payer, const LifeCostDefinition& cost) {
    if (!cost.active()) {
        return true;
    }
    if (!valid_player_index(game, payer)) {
        return false;
    }
    const auto amount = static_cast<std::int64_t>(cost.amount);
    return amount >= 0 && static_cast<std::int64_t>(player(game, payer).life) >= amount;
}

[[nodiscard]] u64 life_cost_payment_record_identity_hash(const LifeCostPaymentRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.LifeCostPaymentRecord.v1");
    hash_life_cost_payment_identity(h, record);
    return h.value();
}

[[nodiscard]] u64 return_cost_payment_record_identity_hash(const ReturnCostPaymentRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ReturnCostPaymentRecord.v1");
    hash_return_cost_payment_identity(h, record);
    return h.value();
}

u32 record_life_cost_payment(GameState& game, LifeCostPaymentRecord record) {
    record.payment_hash = life_cost_payment_record_identity_hash(record);
    const u32 record_index = static_cast<u32>(game.life_cost_payment_records.size() + 1U);
    game.life_cost_payment_records.push_back(std::move(record));
    return record_index;
}

u32 record_return_cost_payment(GameState& game, ReturnCostPaymentRecord record) {
    record.payment_hash = return_cost_payment_record_identity_hash(record);
    const u32 record_index = static_cast<u32>(game.return_cost_payment_records.size() + 1U);
    game.return_cost_payment_records.push_back(std::move(record));
    return record_index;
}

[[nodiscard]] u64 loyalty_cost_payment_record_identity_hash(const LoyaltyCostPaymentRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.LoyaltyCostPaymentRecord.v1");
    hash_loyalty_cost_payment_identity(h, record);
    return h.value();
}

u32 record_loyalty_cost_payment(GameState& game, LoyaltyCostPaymentRecord record) {
    record.payment_hash = loyalty_cost_payment_record_identity_hash(record);
    const u32 record_index = static_cast<u32>(game.loyalty_cost_payment_records.size() + 1U);
    game.loyalty_cost_payment_records.push_back(std::move(record));
    return record_index;
}

[[nodiscard]] u64 tap_cost_payment_record_identity_hash(const TapCostPaymentRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.TapCostPaymentRecord.v1");
    hash_tap_cost_payment_identity(h, record);
    return h.value();
}

u32 record_tap_cost_payment(GameState& game, TapCostPaymentRecord record) {
    record.payment_hash = tap_cost_payment_record_identity_hash(record);
    const u32 record_index = static_cast<u32>(game.tap_cost_payment_records.size() + 1U);
    game.tap_cost_payment_records.push_back(std::move(record));
    return record_index;
}

bool pay_tap_cost(GameState& game,
                  PlayerId payer,
                  ObjectId source_object,
                  std::string_view source_label) {
    if (!valid_player_index(game, payer) || !valid_object_index(game, source_object)) {
        record_event(game, "pay_tap_cost_failed", "invalid tap cost source for " + std::string(source_label));
        return false;
    }
    const auto& before_obj = object(game, source_object);
    if (before_obj.zone != Zone::Battlefield || before_obj.controller != payer || before_obj.tapped) {
        record_event(game, "pay_tap_cost_failed", player(game, payer).name + " could not tap " + object_label(game, source_object) + " for " + std::string(source_label));
        return false;
    }
    if (object_is_creature(game, before_obj) && object_has_summoning_sickness(game, source_object)) {
        record_event(game, "pay_tap_cost_failed", player(game, payer).name + " could not tap summoning-sick " + object_label(game, source_object) + " for " + std::string(source_label));
        return false;
    }

    const u64 tap_event_sequence = game.next_event_sequence;
    const u64 source_zone_change_index_before = before_obj.zone_change_index;
    const bool tapped_before = before_obj.tapped;
    tap_object(game, payer, source_object);
    const bool tapped_after = object(game, source_object).tapped;

    TapCostPaymentRecord payment{};
    payment.sequence = tap_event_sequence;
    payment.payer = payer;
    payment.source_object = source_object;
    payment.source_zone_change_index_before = source_zone_change_index_before;
    payment.tapped_before = tapped_before;
    payment.tapped_after = tapped_after;
    payment.tap_event_sequence = tap_event_sequence;
    record_tap_cost_payment(game, std::move(payment));
    return true;
}

bool pay_selected_discard_cost(GameState& game,
                               PlayerId payer,
                               const DiscardCostDefinition& cost,
                               const std::vector<ObjectId>& selected,
                               std::string_view source_label,
                               ObjectId source_object = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    if (selected.size() != cost.count) {
        record_event(game, "pay_discard_cost_failed", player(game, payer).name + " could not pay discard cost for " + std::string(source_label) + " " + discard_cost_summary(cost));
        return false;
    }
    std::vector<ObjectId> seen;
    for (const auto card_id : selected) {
        if (object_id_in_selection(seen, card_id) || !object_in_player_hand(game, payer, card_id)) {
            record_event(game, "pay_discard_cost_failed", player(game, payer).name + " selected illegal discard " + object_label(game, card_id) + " for " + std::string(source_label));
            return false;
        }
        seen.push_back(card_id);
    }

    auto selected_zone_indices_before = selected_zone_change_indices_before_payment(game, selected);
    const u32 first_discard_record_index = static_cast<u32>(game.discard_records.size() + 1U);
    const u32 first_zone_change_record_index = static_cast<u32>(game.zone_change_records.size() + 1U);
    std::string detail = player(game, payer).name + " discarded";
    for (const auto card_id : selected) {
        detail += " " + object_label(game, card_id);
    }
    detail += " for " + std::string(source_label);

    for (const auto card_id : selected) {
        if (!discard_card_for_reason(game, payer, card_id, DiscardRecordKind::CostPayment)) {
            record_event(game, "pay_discard_cost_failed", player(game, payer).name + " selected illegal discard " + object_label(game, card_id) + " for " + std::string(source_label));
            return false;
        }
    }

    const u32 discard_record_count = static_cast<u32>(game.discard_records.size() + 1U - first_discard_record_index);
    const u32 zone_change_record_count = static_cast<u32>(game.zone_change_records.size() + 1U - first_zone_change_record_index);
    const u64 payment_event_sequence = game.next_event_sequence;
    record_event(game, "pay_discard_cost", detail);

    DiscardCostPaymentRecord payment{};
    payment.sequence = payment_event_sequence;
    payment.payer = payer;
    payment.source_object = source_object;
    payment.cost = cost;
    payment.selected_cards = selected;
    payment.selected_zone_change_indices_before = std::move(selected_zone_indices_before);
    payment.first_discard_record_index = first_discard_record_index;
    payment.discard_record_count = discard_record_count;
    payment.first_zone_change_record_index = first_zone_change_record_index;
    payment.zone_change_record_count = zone_change_record_count;
    record_discard_cost_payment(game, std::move(payment));
    return true;
}

bool pay_discard_cost(GameState& game, PlayerId payer, const DiscardCostDefinition& cost, std::string_view source_label, ObjectId source_object = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    return pay_selected_discard_cost(game, payer, cost, select_discard_cost_cards(game, payer, cost), source_label, source_object);
}

bool pay_life_cost(GameState& game, PlayerId payer, const LifeCostDefinition& cost, std::string_view source_label, ObjectId source_object = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    if (!can_pay_life_cost(game, payer, cost)) {
        record_event(game, "pay_life_cost_failed", "player#" + std::to_string(payer.value) + " could not pay life cost for " + std::string(source_label) + " " + life_cost_summary(cost));
        return false;
    }
    const u32 life_change_record_index = static_cast<u32>(game.life_change_records.size() + 1U);
    const std::int32_t life_before = player(game, payer).life;
    lose_life(game, payer, static_cast<std::int32_t>(cost.amount));
    const std::int32_t life_after = player(game, payer).life;
    const u64 payment_event_sequence = game.next_event_sequence;
    record_event_with_links(game,
                            "pay_life_cost",
                            player(game, payer).name + " paid " + std::to_string(cost.amount) + " life for " + std::string(source_label),
                            EventRecordLinks{.object = source_object, .player = payer});

    LifeCostPaymentRecord payment{};
    payment.sequence = payment_event_sequence;
    payment.payer = payer;
    payment.source_object = source_object;
    payment.cost = cost;
    payment.life_before = life_before;
    payment.life_after = life_after;
    payment.life_change_record_index = life_change_record_index;
    record_life_cost_payment(game, std::move(payment));
    return true;
}

[[nodiscard]] bool return_cost_matches_object(const GameState& game,
                                             PlayerId payer,
                                             const ReturnCostDefinition& cost,
                                             ObjectId object_id,
                                             ObjectId prospective_tapped_source = ObjectId{}) noexcept {
    if (!cost.active() || !valid_player_index(game, payer) || !valid_object_index(game, object_id)) {
        return false;
    }
    const auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield || obj.controller != payer || obj.ceased_to_exist) {
        return false;
    }
    const u32 types = object_type_mask(game, object_id);
    if (!type_masks_overlap(types, cost.required_type_mask)) {
        return false;
    }
    if (cost.require_tapped && !obj.tapped && object_id != prospective_tapped_source) {
        return false;
    }
    return true;
}

[[nodiscard]] std::vector<ObjectId> select_return_cost_objects(const GameState& game,
                                                              PlayerId payer,
                                                              const ReturnCostDefinition& cost,
                                                              ObjectId prospective_tapped_source = ObjectId{}) {
    std::vector<ObjectId> selected;
    if (!cost.active() || !valid_player_index(game, payer)) {
        return selected;
    }
    for (const auto object_id : zone(game, payer, Zone::Battlefield)) {
        if (return_cost_matches_object(game, payer, cost, object_id, prospective_tapped_source)) {
            selected.push_back(object_id);
            if (selected.size() == cost.count) {
                return selected;
            }
        }
    }
    selected.clear();
    return selected;
}

[[nodiscard]] bool can_pay_return_cost(const GameState& game,
                                      PlayerId payer,
                                      const ReturnCostDefinition& cost,
                                      ObjectId prospective_tapped_source = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    return select_return_cost_objects(game, payer, cost, prospective_tapped_source).size() == cost.count;
}

[[nodiscard]] std::string return_cost_summary(const ReturnCostDefinition& cost) {
    std::string text = "count=" + std::to_string(cost.count) + " type_mask=" + std::to_string(cost.required_type_mask);
    if (cost.require_tapped) {
        text += " tapped=1";
    }
    return text;
}

bool pay_selected_return_cost(GameState& game,
                              PlayerId payer,
                              const ReturnCostDefinition& cost,
                              std::vector<ObjectId> selected,
                              std::string_view source_label,
                              ObjectId source_object = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    if (selected.size() != cost.count) {
        record_event(game, "pay_return_cost_failed", player(game, payer).name + " could not pay return cost for " + std::string(source_label) + " " + return_cost_summary(cost));
        return false;
    }
    std::vector<ObjectId> seen;
    for (const auto object_id : selected) {
        if (object_id_in_selection(seen, object_id) || !return_cost_matches_object(game, payer, cost, object_id)) {
            record_event(game, "pay_return_cost_failed", player(game, payer).name + " selected illegal return " + object_label(game, object_id) + " for " + std::string(source_label));
            return false;
        }
        seen.push_back(object_id);
    }

    auto selected_zone_indices_before = selected_zone_change_indices_before_payment(game, selected);
    const u32 first_zone_change_record_index = static_cast<u32>(game.zone_change_records.size() + 1U);
    std::string detail = player(game, payer).name + " returned";
    for (const auto object_id : selected) {
        detail += " ";
        detail += object_label(game, object_id);
    }
    detail += " for ";
    detail += std::string(source_label);

    for (const auto object_id : selected) {
        const PlayerId owner = object(game, object_id).owner;
        move_object(game, object_id, owner, Zone::Hand);
    }

    const u32 zone_change_record_count = static_cast<u32>(game.zone_change_records.size() + 1U - first_zone_change_record_index);
    const u64 payment_event_sequence = game.next_event_sequence;
    record_event_with_links(game,
                            "pay_return_cost",
                            std::move(detail),
                            EventRecordLinks{.object = source_object, .player = payer});

    ReturnCostPaymentRecord payment{};
    payment.sequence = payment_event_sequence;
    payment.payer = payer;
    payment.source_object = source_object;
    payment.cost = cost;
    payment.selected_objects = std::move(selected);
    payment.selected_zone_change_indices_before = std::move(selected_zone_indices_before);
    payment.first_zone_change_record_index = first_zone_change_record_index;
    payment.zone_change_record_count = zone_change_record_count;
    record_return_cost_payment(game, std::move(payment));
    return true;
}

bool pay_return_cost(GameState& game, PlayerId payer, const ReturnCostDefinition& cost, std::string_view source_label, ObjectId source_object = ObjectId{}) {
    if (!cost.active()) {
        return true;
    }
    return pay_selected_return_cost(game, payer, cost, select_return_cost_objects(game, payer, cost), source_label, source_object);
}

[[nodiscard]] bool can_pay_spell_costs(const GameState& game, PlayerId payer, ObjectId source_object, const CardDefinition& def) {
    return can_pay_mana_cost_with_available_mana(game, payer, def.mana_cost) &&
           can_pay_sacrifice_cost(game, payer, def.sacrifice_cost) &&
           can_pay_discard_cost_after_moving_source_to_stack(game, payer, source_object, def.discard_cost) &&
           can_pay_life_cost(game, payer, def.life_cost) &&
           can_pay_return_cost(game, payer, def.return_cost);
}

[[nodiscard]] bool can_pay_activated_ability_costs(const GameState& game,
                                                         PlayerId payer,
                                                         ObjectId source_object,
                                                         const ActivatedAbilityDefinition& ability) {
    const auto locked_tap_sources = activation_locked_tap_sources(ability, source_object);
    return can_pay_mana_cost_with_available_mana_excluding_tap_sources(game, payer, ability.mana_cost, locked_tap_sources) &&
           can_pay_sacrifice_cost(game, payer, ability.sacrifice_cost) &&
           can_pay_discard_cost_from_current_hand(game, payer, ability.discard_cost) &&
           can_pay_life_cost(game, payer, ability.life_cost) &&
           can_pay_return_cost(game, payer, ability.return_cost, ability.tap_cost ? source_object : ObjectId{});
}

void erase_object_from_container(std::vector<ObjectId>& objects, ObjectId id) {
    const auto it = std::find(objects.begin(), objects.end(), id);
    if (it == objects.end()) {
        throw std::logic_error("object not found in its source zone");
    }
    objects.erase(it);
}

bool erase_object_from_container_if_present(std::vector<ObjectId>& objects, ObjectId id) {
    const auto it = std::find(objects.begin(), objects.end(), id);
    if (it == objects.end()) {
        return false;
    }
    objects.erase(it);
    return true;
}

Step next_step_value(Step step) {
    switch (step) {
        case Step::Untap: return Step::Upkeep;
        case Step::Upkeep: return Step::Draw;
        case Step::Draw: return Step::Main1;
        case Step::Main1: return Step::BeginningOfCombat;
        case Step::BeginningOfCombat: return Step::DeclareAttackers;
        case Step::DeclareAttackers: return Step::DeclareBlockers;
        case Step::DeclareBlockers: return Step::CombatDamage;
        case Step::CombatDamage: return Step::EndOfCombat;
        case Step::EndOfCombat: return Step::Main2;
        case Step::Main2: return Step::End;
        case Step::End: return Step::Cleanup;
        case Step::Cleanup: return Step::Untap;
    }
    return Step::Untap;
}

std::string object_label(const GameState& game, ObjectId id) {
    const auto& obj = object(game, id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return "<unknown object>";
    }
    return def->name + "#" + std::to_string(id.value);
}

void cease_token_object(GameState& game, ObjectId id) {
    if (!valid_object_index(game, id)) {
        return;
    }
    auto& obj = object(game, id);
    if (obj.ceased_to_exist) {
        return;
    }
    auto& src = container_for_object(game, obj, obj.zone);
    (void)erase_object_from_container_if_present(src, id);
    obj.ceased_to_exist = true;
    obj.tapped = false;
    obj.damage_marked = 0;
    obj.deathtouch_damage_marked = false;
    obj.counters = CounterSet{};
    obj.regeneration_shields = 0;
    obj.targets.clear();
    obj.has_copy_effect = false;
    obj.copied_definition_index = 0U;
    obj.attached_to = TargetRef{};
    obj.attacking = false;
    obj.blocked = false;
    obj.defending_player = PlayerId{};
    obj.attacked_object = ObjectId{};
    obj.blocking = ObjectId{};
    obj.combat_damage_ordered_blockers.clear();
    obj.battle_protector = PlayerId{};
    obj.controlled_since_turn_start_index = 0U;
    obj.loyalty_ability_activated_turn = 0U;
    obj.zone_change_index = game.next_zone_change_index++;
    record_event(game, "token_ceased_to_exist", object_label(game, id) + " ceased to exist from " + to_string(obj.zone));
}

void remove_all_marked_damage(GameState& game) {
    for (auto& obj : game.objects) {
        obj.damage_marked = 0;
        obj.deathtouch_damage_marked = false;
    }
    record_event(game, "cleanup_remove_damage", "all marked damage removed");
}

void clear_all_regeneration_shields(GameState& game) {
    u32 removed = 0;
    for (auto& obj : game.objects) {
        removed += obj.regeneration_shields;
        obj.regeneration_shields = 0;
    }
    if (removed != 0U) {
        record_event(game, "cleanup_remove_regeneration", "removed " + std::to_string(removed) + " regeneration shield(s)");
    }
}

void perform_cleanup(GameState& game) {
    if (game.active_player.valid()) {
        discard_down_to_max_hand_size(game, game.active_player);
    }
    expire_continuous_effects(game, ContinuousEffectDuration::UntilCleanup);
    remove_all_marked_damage(game);
    clear_all_regeneration_shields(game);
}



[[nodiscard]] u32 turn_order_distance(const GameState& game, PlayerId player_id) noexcept {
    if (!player_id.valid() || game.players.empty()) {
        return static_cast<u32>(game.players.size() + 1U);
    }
    const u32 player_count = static_cast<u32>(game.players.size());
    const u32 active = game.active_player.valid() ? game.active_player.value : 1U;
    return (player_id.value + player_count - active) % player_count;
}

[[nodiscard]] bool trigger_event_matches(const TriggerDefinition& trigger, TriggerEventKind event) noexcept {
    return trigger.active() && trigger.event == event;
}


inline constexpr u64 kMaxPendingTriggerOrderActions = 128U;

[[nodiscard]] bool pending_trigger_has_order_key(const PendingTrigger& trigger) noexcept {
    return trigger.trigger_record_index != 0U;
}

[[nodiscard]] bool pending_trigger_default_less(const GameState& game, const PendingTrigger& a, const PendingTrigger& b) noexcept {
    const u32 da = turn_order_distance(game, a.controller);
    const u32 db = turn_order_distance(game, b.controller);
    if (da != db) {
        return da < db;
    }
    if (a.caused_by_event_sequence != b.caused_by_event_sequence) {
        return a.caused_by_event_sequence < b.caused_by_event_sequence;
    }
    return a.source.value < b.source.value;
}

[[nodiscard]] std::vector<PendingTrigger> default_ordered_pending_triggers(const GameState& game) {
    std::vector<PendingTrigger> pending = game.pending_triggers;
    std::stable_sort(pending.begin(), pending.end(), [&game](const PendingTrigger& a, const PendingTrigger& b) {
        return pending_trigger_default_less(game, a, b);
    });
    return pending;
}

[[nodiscard]] std::vector<u32> pending_trigger_default_order_keys(const GameState& game) {
    std::vector<u32> keys;
    const auto pending = default_ordered_pending_triggers(game);
    keys.reserve(pending.size());
    for (const auto& trigger : pending) {
        if (!pending_trigger_has_order_key(trigger)) {
            keys.clear();
            return keys;
        }
        keys.push_back(trigger.trigger_record_index);
    }
    return keys;
}

[[nodiscard]] bool pending_trigger_order_is_apnap_blocked(const GameState& game, const std::vector<u32>& order) noexcept {
    u32 last_distance = 0U;
    bool first = true;
    for (const u32 key : order) {
        const auto it = std::find_if(game.pending_triggers.begin(), game.pending_triggers.end(), [key](const PendingTrigger& trigger) {
            return trigger.trigger_record_index == key;
        });
        if (it == game.pending_triggers.end()) {
            return false;
        }
        const u32 distance = turn_order_distance(game, it->controller);
        if (!first && distance < last_distance) {
            return false;
        }
        first = false;
        last_distance = distance;
    }
    return true;
}

[[nodiscard]] bool valid_pending_trigger_order(const GameState& game, const std::vector<u32>& order) noexcept {
    if (game.pending_triggers.empty()) {
        return order.empty();
    }
    if (order.empty()) {
        return true; // legacy deterministic fallback; explicit legal actions carry a non-empty order.
    }
    if (order.size() != game.pending_triggers.size()) {
        return false;
    }
    std::vector<u32> expected;
    expected.reserve(game.pending_triggers.size());
    for (const auto& trigger : game.pending_triggers) {
        if (!pending_trigger_has_order_key(trigger)) {
            return false;
        }
        expected.push_back(trigger.trigger_record_index);
    }
    auto actual = order;
    std::sort(expected.begin(), expected.end());
    std::sort(actual.begin(), actual.end());
    if (std::adjacent_find(actual.begin(), actual.end()) != actual.end() || expected != actual) {
        return false;
    }
    return pending_trigger_order_is_apnap_blocked(game, order);
}

[[nodiscard]] std::string trigger_order_label(const std::vector<u32>& order) {
    if (order.empty()) {
        return "default";
    }
    std::ostringstream out;
    out << "triggers=";
    for (std::size_t i = 0; i < order.size(); ++i) {
        if (i != 0U) {
            out << ",";
        }
        out << order[i];
    }
    return out.str();
}

[[nodiscard]] LegalAction make_put_pending_triggers_action(PlayerId player_id, std::vector<u32> trigger_order) {
    LegalAction action{};
    action.kind = ActionKind::PutPendingTriggersOnStack;
    action.player = player_id;
    action.trigger_order = std::move(trigger_order);
    action.label = std::string(to_string(ActionKind::PutPendingTriggersOnStack)) + ":" + trigger_order_label(action.trigger_order);
    return action;
}

void append_pending_trigger_order_actions(const GameState& game, PlayerId player_id, LegalActionFrontier& frontier) {
    frontier.generation_limit = kMaxPendingTriggerOrderActions;
    if (game.pending_triggers.empty()) {
        return;
    }
    const auto default_keys = pending_trigger_default_order_keys(game);
    if (default_keys.empty()) {
        frontier.actions.push_back(make_put_pending_triggers_action(player_id, {}));
        return;
    }

    const auto sorted_pending = default_ordered_pending_triggers(game);
    std::vector<std::vector<u32>> groups;
    for (const auto& trigger : sorted_pending) {
        if (groups.empty()) {
            groups.push_back({trigger.trigger_record_index});
            continue;
        }
        const u32 current_distance = turn_order_distance(game, trigger.controller);
        const auto previous_key = groups.back().empty() ? 0U : groups.back().front();
        const auto previous_it = std::find_if(sorted_pending.begin(), sorted_pending.end(), [previous_key](const PendingTrigger& candidate) {
            return candidate.trigger_record_index == previous_key;
        });
        const u32 previous_distance = previous_it == sorted_pending.end() ? current_distance : turn_order_distance(game, previous_it->controller);
        if (current_distance == previous_distance) {
            groups.back().push_back(trigger.trigger_record_index);
        } else {
            groups.push_back({trigger.trigger_record_index});
        }
    }

    std::vector<u32> current;
    current.reserve(default_keys.size());
    bool truncated = false;
    auto emit = [&](const std::vector<u32>& order) {
        if (frontier.actions.size() >= kMaxPendingTriggerOrderActions) {
            truncated = true;
            return false;
        }
        frontier.actions.push_back(make_put_pending_triggers_action(player_id, order));
        return true;
    };

    std::function<bool(std::size_t)> visit_group = [&](std::size_t group_index) -> bool {
        if (group_index == groups.size()) {
            return emit(current);
        }
        auto group = groups[group_index];
        std::sort(group.begin(), group.end());
        do {
            const auto original_size = current.size();
            current.insert(current.end(), group.begin(), group.end());
            if (!visit_group(group_index + 1U)) {
                current.resize(original_size);
                return false;
            }
            current.resize(original_size);
        } while (std::next_permutation(group.begin(), group.end()));
        return true;
    };
    (void)visit_group(0U);
    if (truncated) {
        frontier.complete = false;
        if (frontier.actions.size() > kMaxPendingTriggerOrderActions) {
            frontier.actions.resize(static_cast<std::size_t>(kMaxPendingTriggerOrderActions));
        }
    }
}

struct TriggerSourceSnapshot {
    PlayerId controller{};
    ObjectId source{};
    std::string source_name;
    TriggerDefinition trigger{};
    u32 source_color_mask = ColorNone;
    u32 source_ability_mask = AbilityNone;
    u64 source_zone_change_index = 0;
};

[[nodiscard]] TriggerSourceSnapshot snapshot_trigger_source(const GameState& game, ObjectId source_id) {
    const auto& source_obj = object(game, source_id);
    const auto* source_def = current_definition_for_object(game, source_obj);
    if (source_def == nullptr) {
        return TriggerSourceSnapshot{
            .controller = source_obj.controller,
            .source = source_id,
            .source_name = "<unknown trigger source>",
            .source_zone_change_index = source_obj.zone_change_index
        };
    }
    return TriggerSourceSnapshot{
        .controller = source_obj.controller,
        .source = source_id,
        .source_name = source_def->name,
        .trigger = source_def->trigger,
        .source_color_mask = object_color_mask(game, source_id),
        .source_ability_mask = derived_ability_mask(game, source_id),
        .source_zone_change_index = source_obj.zone_change_index
    };
}

void move_object_with_precomputed_ltb_snapshots(GameState& game,
                                                ObjectId object_id,
                                                PlayerId target_controller,
                                                Zone target_zone,
                                                const std::vector<TriggerSourceSnapshot>* precomputed_ltb_snapshots);

[[nodiscard]] std::vector<TriggerSourceSnapshot> capture_battlefield_trigger_sources(const GameState& game) {
    std::vector<TriggerSourceSnapshot> snapshots;
    for (const auto& p : game.players) {
        for (const auto source_id : p.zones[zone_index(Zone::Battlefield)]) {
            if (!valid_object_index(game, source_id)) {
                continue;
            }
            const auto& source_obj = object(game, source_id);
            const auto* source_def = current_definition_for_object(game, source_obj);
            if (source_def == nullptr || !source_def->trigger.active()) {
                continue;
            }
            snapshots.push_back(snapshot_trigger_source(game, source_id));
        }
    }
    return snapshots;
}

[[nodiscard]] std::string effect_payload_label(EffectKind kind, u32 amount, CounterKind counter_kind) {
    if (kind == EffectKind::AddCounters) {
        return std::string(to_string(kind)) + ":" + to_string(counter_kind) + ":" + std::to_string(amount);
    }
    return std::string(to_string(kind)) + ":" + std::to_string(amount);
}

[[nodiscard]] bool valid_spell_mode_index(const CardDefinition& def, u32 mode_index) noexcept {
    return mode_index != 0U && mode_index <= def.modes.size();
}

[[nodiscard]] const SpellModeDefinition& spell_mode_definition(const CardDefinition& def, u32 mode_index) {
    if (!valid_spell_mode_index(def, mode_index)) {
        throw std::out_of_range("invalid spell mode index");
    }
    return def.modes[mode_index - 1U];
}

[[nodiscard]] std::string mode_label(const CardDefinition& def, u32 mode_index) {
    if (!valid_spell_mode_index(def, mode_index)) {
        return "mode#" + std::to_string(mode_index);
    }
    const auto& mode = def.modes[mode_index - 1U];
    if (!mode.name.empty()) {
        return "mode#" + std::to_string(mode_index) + ":" + mode.name;
    }
    return "mode#" + std::to_string(mode_index);
}

[[nodiscard]] bool valid_activated_ability_index(const CardDefinition& def, u32 ability_index) noexcept {
    return ability_index != 0U && ability_index <= def.activated_abilities.size();
}

[[nodiscard]] const ActivatedAbilityDefinition& activated_ability_definition(const CardDefinition& def, u32 ability_index) {
    if (!valid_activated_ability_index(def, ability_index)) {
        throw std::out_of_range("invalid activated ability index");
    }
    return def.activated_abilities[ability_index - 1U];
}

[[nodiscard]] std::string activated_ability_label(const CardDefinition& def, u32 ability_index) {
    if (!valid_activated_ability_index(def, ability_index)) {
        return "ability#" + std::to_string(ability_index);
    }
    const auto& ability = def.activated_abilities[ability_index - 1U];
    if (!ability.name.empty()) {
        return "ability#" + std::to_string(ability_index) + ":" + ability.name;
    }
    return "ability#" + std::to_string(ability_index);
}

[[nodiscard]] bool object_is_stack_object(const GameState& game, ObjectId object_id) noexcept {
    return valid_object_index(game, object_id) && object(game, object_id).zone == Zone::Stack;
}

void counter_stack_object(GameState& game, ObjectId source_id, ObjectId target_id) {
    if (!object_is_stack_object(game, target_id)) {
        record_event(game, "counter_stack_object_failed", "target object#" + std::to_string(target_id.value) + " is not on the stack");
        return;
    }
    if (source_id == target_id) {
        record_event(game, "counter_stack_object_failed", object_label(game, source_id) + " cannot counter itself");
        return;
    }
    const std::string source_label = valid_object_index(game, source_id) ? object_label(game, source_id) : std::string("<source>");
    const std::string target_label_text = object_label(game, target_id);
    const bool target_is_ability = object(game, target_id).ability_object;
    const PlayerId destination_controller = target_is_ability ? object(game, target_id).controller : object(game, target_id).owner;
    move_object(game, target_id, destination_controller, target_is_ability ? Zone::Exile : Zone::Graveyard);
    record_event(game, target_is_ability ? "counter_ability" : "counter_spell", source_label + " countered " + target_label_text);
}

void apply_effect_payload(GameState& game,
                          ObjectId source_id,
                          PlayerId controller,
                          EffectKind effect_kind,
                          u32 amount,
                          CounterKind counter_kind,
                          u32 target_mask,
                          u32 created_token_definition_index,
                          const std::vector<TargetRef>& legal_targets_on_resolution) {
    if (effect_kind == EffectKind::None || (amount == 0U && effect_kind != EffectKind::CounterSpell)) {
        return;
    }

    if (target_mask == TargetNone) {
        switch (effect_kind) {
            case EffectKind::GainLife:
                gain_life(game, controller, static_cast<std::int32_t>(amount));
                break;
            case EffectKind::DrawCards:
                for (u32 i = 0; i < amount; ++i) {
                    draw_card(game, controller);
                }
                break;
            case EffectKind::DealDamage:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot deal damage without a target in current scaffold");
                break;
            case EffectKind::AddCounters:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot add counters without a target in current scaffold");
                break;
            case EffectKind::DestroyPermanent:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot destroy without a target in current scaffold");
                break;
            case EffectKind::RegeneratePermanent:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot create a regeneration shield without a target in current scaffold");
                break;
            case EffectKind::ExilePermanent:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot exile without a target in current scaffold");
                break;
            case EffectKind::CreateToken:
                (void)create_tokens(game, controller, created_token_definition_index, amount);
                break;
            case EffectKind::GainControlPermanent:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot gain control without a target in current scaffold");
                break;
            case EffectKind::CreateContinuousEffect: {
                if (valid_object_index(game, source_id)) {
                    const auto* source_def = current_definition_for_object(game, object(game, source_id));
                    if (source_def != nullptr) {
                        create_continuous_effect(game, source_id, controller, source_def->continuous_effect, source_def->continuous_effect_duration, {});
                    }
                }
                break;
            }
            case EffectKind::BecomeCopyPermanent:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot become a copy without a target in current scaffold");
                break;
            case EffectKind::CounterSpell:
                record_event(game, "effect_no_target_unsupported", object_label(game, source_id) + " cannot counter without a stack target in current scaffold");
                break;
            case EffectKind::None:
            case EffectKind::Count:
                break;
        }
        record_event(game, "resolve_effect_controller", object_label(game, source_id) + " effect=" + effect_payload_label(effect_kind, amount, counter_kind) + " controller=" + player(game, controller).name);
        return;
    }

    switch (effect_kind) {
        case EffectKind::DealDamage:
            for (const auto target : legal_targets_on_resolution) {
                deal_damage_to_target(game, source_id, target, amount);
            }
            break;
        case EffectKind::DrawCards:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Player) {
                    for (u32 i = 0; i < amount; ++i) {
                        draw_card(game, target.player);
                    }
                }
            }
            break;
        case EffectKind::GainLife:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Player) {
                    gain_life(game, target.player, static_cast<std::int32_t>(amount));
                }
            }
            break;
        case EffectKind::AddCounters:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Object) {
                    add_counter_to_object(game, target.object, counter_kind, amount);
                } else if (target.kind == TargetKind::Player) {
                    add_counter_to_player(game, target.player, counter_kind, amount);
                }
            }
            break;
        case EffectKind::DestroyPermanent:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Object) {
                    (void)destroy_permanent(game, target.object, true);
                }
            }
            break;
        case EffectKind::RegeneratePermanent:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Object) {
                    add_regeneration_shield(game, target.object, std::max(1U, amount));
                }
            }
            break;
        case EffectKind::ExilePermanent:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Object) {
                    (void)exile_permanent(game, target.object);
                }
            }
            break;
        case EffectKind::CreateToken:
            (void)create_tokens(game, controller, created_token_definition_index, amount);
            break;
        case EffectKind::GainControlPermanent:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Object) {
                    (void)gain_control_of_permanent(game, controller, target.object);
                }
            }
            break;
        case EffectKind::CreateContinuousEffect:
            if (valid_object_index(game, source_id)) {
                const auto* source_def = current_definition_for_object(game, object(game, source_id));
                if (source_def != nullptr) {
                    create_continuous_effect(game, source_id, controller, source_def->continuous_effect, source_def->continuous_effect_duration, legal_targets_on_resolution);
                }
            }
            break;
        case EffectKind::BecomeCopyPermanent:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Object) {
                    (void)become_copy_of_permanent(game, source_id, target.object);
                }
            }
            break;
        case EffectKind::CounterSpell:
            for (const auto target : legal_targets_on_resolution) {
                if (target.kind == TargetKind::Object) {
                    counter_stack_object(game, source_id, target.object);
                }
            }
            break;
        case EffectKind::None:
        case EffectKind::Count:
            break;
    }
}

void queue_matching_triggers_from_snapshots(GameState& game,
                                            TriggerEventKind event,
                                            ObjectId subject,
                                            const std::vector<TriggerSourceSnapshot>& snapshots) {
    if (event == TriggerEventKind::None || !subject.valid()) {
        return;
    }
    const u64 caused_by = game.next_event_sequence == 0U ? 0U : game.next_event_sequence - 1U;
    for (const auto& snapshot : snapshots) {
        const auto& trigger = snapshot.trigger;
        if (!trigger_event_matches(trigger, event)) {
            continue;
        }
        if (trigger.exclude_source && snapshot.source == subject) {
            continue;
        }
        const u32 trigger_record_index = static_cast<u32>(game.trigger_records.size() + 1U);
        const u64 queued_sequence = game.next_event_sequence;
        const u64 subject_zone_change_index = valid_object_index(game, subject) ? object(game, subject).zone_change_index : 0U;
        game.trigger_records.push_back(TriggerRecord{
            .sequence = queued_sequence,
            .event = event,
            .subject = subject,
            .subject_zone_change_index = subject_zone_change_index,
            .controller = snapshot.controller,
            .source = snapshot.source,
            .source_name = snapshot.source_name,
            .source_color_mask = legal_color_mask(snapshot.source_color_mask),
            .source_ability_mask = snapshot.source_ability_mask,
            .source_zone_change_index = snapshot.source_zone_change_index,
            .effect_kind = trigger.effect_kind,
            .effect_amount = trigger.effect_amount,
            .effect_counter_kind = trigger.effect_counter_kind,
            .target_mask = trigger.target_mask,
            .target_count = trigger.target_count,
            .created_token_definition_index = trigger.created_token_definition_index,
            .caused_by_event_sequence = caused_by
        });
        game.pending_triggers.push_back(PendingTrigger{
            .controller = snapshot.controller,
            .source = snapshot.source,
            .subject = subject,
            .subject_zone_change_index = subject_zone_change_index,
            .source_name = snapshot.source_name,
            .event = event,
            .effect_kind = trigger.effect_kind,
            .effect_amount = trigger.effect_amount,
            .effect_counter_kind = trigger.effect_counter_kind,
            .target_mask = trigger.target_mask,
            .target_count = trigger.target_count,
            .created_token_definition_index = trigger.created_token_definition_index,
            .source_color_mask = legal_color_mask(snapshot.source_color_mask),
            .source_ability_mask = snapshot.source_ability_mask,
            .source_zone_change_index = snapshot.source_zone_change_index,
            .caused_by_event_sequence = caused_by,
            .trigger_record_index = trigger_record_index
        });
        record_event_with_links(game,
                                "trigger_queued",
                                snapshot.source_name + " saw " + to_string(event) + " from " + object_label(game, subject),
                                EventRecordLinks{
                                    .kind = EventRecordKind::TriggerQueued,
                                    .object = subject,
                                    .player = snapshot.controller,
                                    .trigger_record_index = trigger_record_index
                                });
    }
}

void queue_matching_triggers_for_event(GameState& game, TriggerEventKind event, ObjectId subject) {
    queue_matching_triggers_from_snapshots(game, event, subject, capture_battlefield_trigger_sources(game));
}

struct TriggerTargetChoice {
    bool legal = true;
    std::vector<TargetRef> targets{};
    u32 required_target_count = 0;
    u32 legal_target_set_count = 0;
    u64 choice_target_set_hash = 0;
    bool target_choice_recorded = false;
    bool no_legal_choices = false;
};

[[nodiscard]] bool target_has_protection_from_source_characteristics(const GameState& game,
                                                                    TargetRef target,
                                                                    u32 source_color_mask) noexcept {
    if (target.kind != TargetKind::Object || !valid_object_index(game, target.object)) {
        return false;
    }
    const auto& obj = object(game, target.object);
    if (obj.zone != Zone::Battlefield) {
        return false;
    }
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return false;
    }
    return color_masks_overlap(legal_color_mask(def->protection_color_mask), legal_color_mask(source_color_mask));
}

[[nodiscard]] bool target_ref_is_legal_for_source_characteristics(const GameState& game,
                                                                 TargetRef target,
                                                                 u32 target_mask,
                                                                 PlayerId source_controller,
                                                                 u32 source_color_mask) noexcept {
    if (!target_ref_is_legal_for_source(game, target, target_mask, source_controller)) {
        return false;
    }
    if (target_has_protection_from_source_characteristics(game, target, source_color_mask)) {
        return false;
    }
    return true;
}

[[nodiscard]] std::vector<TargetRef> enumerate_legal_targets_for_source_characteristics(const GameState& game,
                                                                                       u32 target_mask,
                                                                                       PlayerId source_controller,
                                                                                       u32 source_color_mask) {
    std::vector<TargetRef> filtered;
    for (const auto target : enumerate_legal_targets(game, target_mask)) {
        if (target_ref_is_legal_for_source_characteristics(game, target, target_mask, source_controller, source_color_mask)) {
            filtered.push_back(target);
        }
    }
    return filtered;
}

[[nodiscard]] std::vector<std::vector<TargetRef>> enumerate_legal_trigger_target_sets(const GameState& game,
                                                                                      const PendingTrigger& trigger,
                                                                                      u32 target_count) {
    std::vector<std::vector<TargetRef>> sets;
    if (target_count == 0U || trigger.target_mask == TargetNone) {
        if (target_count == 0U && trigger.target_mask == TargetNone) {
            sets.push_back({});
        }
        return sets;
    }
    const auto legal_targets = enumerate_legal_targets_for_source_characteristics(game,
                                                                                 trigger.target_mask,
                                                                                 trigger.controller,
                                                                                 trigger.source_color_mask);
    if (legal_targets.size() < target_count) {
        return sets;
    }
    std::vector<TargetRef> current;
    current.reserve(target_count);
    auto build = [&](auto&& self, std::size_t start) -> void {
        if (current.size() == target_count) {
            sets.push_back(current);
            return;
        }
        const std::size_t remaining = static_cast<std::size_t>(target_count - current.size());
        if (legal_targets.size() < remaining || start > legal_targets.size() - remaining) {
            return;
        }
        for (std::size_t i = start; i <= legal_targets.size() - remaining; ++i) {
            current.push_back(legal_targets[i]);
            self(self, i + 1U);
            current.pop_back();
        }
    };
    build(build, 0U);
    return sets;
}

[[nodiscard]] TriggerTargetChoice choose_default_trigger_targets(GameState& game, const PendingTrigger& trigger) {
    TriggerTargetChoice choice{};
    choice.required_target_count = required_target_count_for_trigger(trigger);
    choice.target_choice_recorded = true;
    if (choice.required_target_count == 0U) {
        choice.legal_target_set_count = 1U;
        choice.choice_target_set_hash = target_choice_set_hash_impl(choice.targets);
        return choice;
    }
    const auto legal_target_sets = enumerate_legal_trigger_target_sets(game, trigger, choice.required_target_count);
    choice.legal_target_set_count = static_cast<u32>(legal_target_sets.size());
    if (legal_target_sets.empty()) {
        choice.legal = false;
        choice.no_legal_choices = true;
        choice.choice_target_set_hash = target_choice_set_hash_impl(choice.targets);
        record_event(game, "trigger_no_legal_targets", trigger.source_name + " has no legal target set for triggered ability");
        return choice;
    }
    choice.targets = stamp_targets_for_choice(game, legal_target_sets.front());
    choice.choice_target_set_hash = target_choice_set_hash_impl(choice.targets);
    record_event(game,
                 "trigger_choose_target",
                 trigger.source_name + " chose " + target_list_label(game, choice.targets) +
                     " for triggered ability candidates=" + std::to_string(choice.legal_target_set_count) +
                     " target_set_hash=" + std::to_string(choice.choice_target_set_hash));
    return choice;
}

void seal_trigger_target_choice(TriggerRecord& record, const TriggerTargetChoice& choice) {
    record.required_target_count = choice.required_target_count;
    record.chosen_targets = choice.targets;
    record.legal_target_set_count = choice.legal_target_set_count;
    record.choice_target_set_hash = choice.choice_target_set_hash;
    record.target_choice_recorded = choice.target_choice_recorded;
    record.no_legal_choices = choice.no_legal_choices;
}

[[nodiscard]] u32 trigger_record_index_for_stack_object(const GameState& game, ObjectId stack_object) noexcept {
    if (!stack_object.valid()) {
        return 0U;
    }
    for (std::size_t i = 0; i < game.trigger_records.size(); ++i) {
        const auto& record = game.trigger_records[i];
        if (!record.dropped && record.stack_object == stack_object && record.put_on_stack_sequence != 0U) {
            return static_cast<u32>(i + 1U);
        }
    }
    return 0U;
}

ObjectId create_triggered_ability_stack_object(GameState& game, const PendingTrigger& trigger, const std::vector<TargetRef>& chosen_targets) {
    CardDefinition def;
    def.name = "Triggered ability - " + trigger.source_name;
    def.effect_kind = trigger.effect_kind;
    def.effect_amount = trigger.effect_amount;
    def.effect_counter_kind = trigger.effect_counter_kind;
    def.target_mask = trigger.target_mask;
    def.target_count = trigger.target_count;
    def.created_token_definition_index = trigger.created_token_definition_index;
    def.color_mask = legal_color_mask(trigger.source_color_mask);
    def.ability_mask = trigger.source_ability_mask;
    const u32 def_index = static_cast<u32>(game.definitions.size());
    game.definitions.push_back(std::move(def));

    const ObjectId id{static_cast<u32>(game.objects.size() + 1U)};
    game.objects.push_back(GameObject{
        .id = id,
        .definition_index = def_index,
        .owner = trigger.controller,
        .controller = trigger.controller,
        .zone = Zone::Stack,
        .tapped = false,
        .token = true,
        .power = 0,
        .toughness = 0,
        .damage_marked = 0,
        .targets = {},
        .ability_object = true,
        .zone_change_index = game.next_zone_change_index++
    });
    object(game, id).targets = chosen_targets;
    game.stack.push_back(id);
    record_event_with_links(game,
                            "trigger_put_on_stack",
                            object_label(game, id) + " controller=" + player(game, trigger.controller).name,
                            EventRecordLinks{
                                .kind = EventRecordKind::TriggerPutOnStack,
                                .object = id,
                                .player = trigger.controller,
                                .trigger_record_index = trigger.trigger_record_index
                            });
    return id;
}

ObjectId create_loyalty_ability_stack_object(GameState& game, ObjectId source_id, const LoyaltyAbilityDefinition& ability, PlayerId controller, const std::vector<TargetRef>& targets) {
    const auto* source_def = valid_object_index(game, source_id) ? current_definition_for_object(game, object(game, source_id)) : nullptr;
    if (source_def == nullptr) {
        throw std::logic_error("loyalty ability source has invalid current definition");
    }
    CardDefinition def;
    def.name = "Loyalty ability - " + source_def->name;
    def.effect_kind = ability.effect_kind;
    def.effect_amount = ability.effect_amount;
    def.effect_counter_kind = ability.effect_counter_kind;
    def.target_mask = ability.target_mask;
    def.target_count = ability.target_count;
    def.created_token_definition_index = ability.created_token_definition_index;
    def.color_mask = card_color_mask(*source_def);
    def.ability_mask = source_def->ability_mask;
    def.continuous_effect = source_def->continuous_effect;
    def.continuous_effect_duration = source_def->continuous_effect_duration;
    const u32 def_index = static_cast<u32>(game.definitions.size());
    game.definitions.push_back(std::move(def));

    const ObjectId id{static_cast<u32>(game.objects.size() + 1U)};
    game.objects.push_back(GameObject{
        .id = id,
        .definition_index = def_index,
        .owner = controller,
        .controller = controller,
        .zone = Zone::Stack,
        .tapped = false,
        .token = true,
        .power = 0,
        .toughness = 0,
        .damage_marked = 0,
        .targets = stamp_targets_for_choice(game, targets),
        .ability_object = true,
        .zone_change_index = game.next_zone_change_index++
    });
    game.stack.push_back(id);
    record_event(game, "loyalty_ability_put_on_stack", object_label(game, id) + " from " + object_label(game, source_id));
    if (!targets.empty()) {
        const auto& stamped_targets = object(game, id).targets;
        const TargetRef event_target = stamped_targets.size() == 1U ? stamped_targets.front() : TargetRef{};
        record_event_with_links(game,
                                "choose_target",
                                object_label(game, id) + " targets " + target_list_label(game, targets),
                                EventRecordLinks{.object = id, .player = controller, .target = event_target, .choice_target_count = static_cast<u32>(stamped_targets.size()), .choice_target_set_hash = target_choice_set_hash_impl(stamped_targets)});
    }
    return id;
}

ObjectId create_activated_ability_stack_object(GameState& game, ObjectId source_id, const ActivatedAbilityDefinition& ability, PlayerId controller, const std::vector<TargetRef>& targets) {
    const auto* source_def = valid_object_index(game, source_id) ? current_definition_for_object(game, object(game, source_id)) : nullptr;
    if (source_def == nullptr) {
        throw std::logic_error("activated ability source has invalid current definition");
    }
    CardDefinition def;
    def.name = "Activated ability - " + source_def->name;
    if (!ability.name.empty()) {
        def.name += " - " + ability.name;
    }
    def.effect_kind = ability.effect_kind;
    def.effect_amount = ability.effect_amount;
    def.effect_counter_kind = ability.effect_counter_kind;
    def.target_mask = ability.target_mask;
    def.target_count = ability.target_count;
    def.created_token_definition_index = ability.created_token_definition_index;
    def.color_mask = card_color_mask(*source_def);
    def.ability_mask = source_def->ability_mask;
    def.continuous_effect = source_def->continuous_effect;
    def.continuous_effect_duration = source_def->continuous_effect_duration;
    const u32 def_index = static_cast<u32>(game.definitions.size());
    game.definitions.push_back(std::move(def));

    const ObjectId id{static_cast<u32>(game.objects.size() + 1U)};
    game.objects.push_back(GameObject{
        .id = id,
        .definition_index = def_index,
        .owner = controller,
        .controller = controller,
        .zone = Zone::Stack,
        .tapped = false,
        .token = true,
        .power = 0,
        .toughness = 0,
        .damage_marked = 0,
        .targets = stamp_targets_for_choice(game, targets),
        .ability_object = true,
        .zone_change_index = game.next_zone_change_index++
    });
    game.stack.push_back(id);
    record_event(game, "activated_ability_put_on_stack", object_label(game, id) + " from " + object_label(game, source_id));
    if (!targets.empty()) {
        const auto& stamped_targets = object(game, id).targets;
        const TargetRef event_target = stamped_targets.size() == 1U ? stamped_targets.front() : TargetRef{};
        record_event_with_links(game,
                                "choose_target",
                                object_label(game, id) + " targets " + target_list_label(game, targets),
                                EventRecordLinks{.object = id, .player = controller, .target = event_target, .choice_target_count = static_cast<u32>(stamped_targets.size()), .choice_target_set_hash = target_choice_set_hash_impl(stamped_targets)});
    }
    return id;
}

void add_entering_planeswalker_loyalty(GameState& game, ObjectId id) {
    if (!valid_object_index(game, id)) {
        return;
    }
    auto& obj = object(game, id);
    const auto* def = current_definition_for_object(game, obj);
    if (obj.zone != Zone::Battlefield || !object_is_planeswalker(game, obj) || def == nullptr) {
        return;
    }
    const auto printed = def->printed_loyalty;
    if (printed <= 0) {
        record_event(game, "planeswalker_enters_loyalty", object_label(game, id) + " entered with no loyalty counters");
        return;
    }
    const u32 before = obj.counters.loyalty;
    obj.counters.loyalty += static_cast<u32>(printed);
    record_object_counter_change(game,
                                 id,
                                 CounterKind::Loyalty,
                                 CounterChangeKind::ObjectAdded,
                                 static_cast<u32>(printed),
                                 before,
                                 obj.counters.loyalty,
                                 "planeswalker_enters_loyalty",
                                 object_label(game, id) + " entered with " + std::to_string(printed) + " loyalty counter(s)");
}

PlayerId default_battle_protector(const GameState& game, PlayerId controller) noexcept {
    if (!valid_player_index(game, controller)) {
        return PlayerId{};
    }
    const PlayerId next = next_player_in_turn_order(game, controller);
    if (valid_player_index(game, next) && next != controller && !player(game, next).lost) {
        return next;
    }
    for (const auto& candidate : game.players) {
        if (candidate.id != controller && !candidate.lost) {
            return candidate.id;
        }
    }
    return controller;
}

void add_entering_battle_defense_and_protector(GameState& game, ObjectId id) {
    if (!valid_object_index(game, id)) {
        return;
    }
    auto& obj = object(game, id);
    const auto* def = current_definition_for_object(game, obj);
    if (obj.zone != Zone::Battlefield || !object_is_battle(game, obj) || def == nullptr) {
        return;
    }
    const auto printed = def->printed_defense;
    const u32 before = obj.counters.defense;
    if (printed > 0) {
        obj.counters.defense += static_cast<u32>(printed);
    }
    obj.battle_protector = default_battle_protector(game, obj.controller);
    const std::string protector_name = valid_player_index(game, obj.battle_protector) ? player(game, obj.battle_protector).name : std::string("<none>");
    const std::string detail = object_label(game, id) + " entered with " + std::to_string(std::max(0, printed)) + " defense counter(s), protector=" + protector_name;
    if (printed > 0) {
        record_object_counter_change(game,
                                     id,
                                     CounterKind::Defense,
                                     CounterChangeKind::ObjectAdded,
                                     static_cast<u32>(printed),
                                     before,
                                     obj.counters.defense,
                                     "battle_enters_defense",
                                     detail);
    } else {
        record_event(game, "battle_enters_defense", detail);
    }
}

void clear_combat_links_for_object(GameState& game, ObjectId moved) {
    if (!moved.valid()) {
        return;
    }
    for (auto& other : game.objects) {
        if (other.id == moved) {
            other.attacking = false;
            other.blocked = false;
            other.defending_player = PlayerId{};
            other.attacked_object = ObjectId{};
            other.blocking = ObjectId{};
            other.combat_damage_ordered_blockers.clear();
        } else if (other.blocking == moved) {
            other.blocking = ObjectId{};
        }
        other.combat_damage_ordered_blockers.erase(
            std::remove(other.combat_damage_ordered_blockers.begin(), other.combat_damage_ordered_blockers.end(), moved),
            other.combat_damage_ordered_blockers.end());
        if (other.attacked_object == moved) {
            other.attacked_object = ObjectId{};
            other.blocked = true;
            record_event(game, "combat_attack_target_left", object_label(game, other.id) + " lost attacked object " + object_label(game, moved));
        }
    }
}

u32 clear_prevention_links_for_object(GameState& game, ObjectId moved, u32 zone_change_record_index) {
    if (!moved.valid() || game.damage_prevention_shields.empty()) {
        return 0U;
    }
    const u32 first_record_index = static_cast<u32>(game.damage_prevention_records.size() + 1U);
    u32 expired_count = 0;
    auto write = game.damage_prevention_shields.begin();
    for (auto read = game.damage_prevention_shields.begin(); read != game.damage_prevention_shields.end(); ++read) {
        if (read->target.kind == TargetKind::Object && read->target.object == moved) {
            const std::string label = read->label.empty() ? "damage prevention shield" : read->label;
            record_damage_prevention_change(game,
                                            DamagePreventionRecord{
                                                .kind = DamagePreventionRecordKind::ShieldExpired,
                                                .shield_id = read->id,
                                                .target = read->target,
                                                .amount = read->remaining,
                                                .remaining_before = read->remaining,
                                                .remaining_after = 0U,
                                                .zone_change_record_index = zone_change_record_index,
                                                .choice_rank = read->choice_rank,
                                                .label = read->label
                                            },
                                            "damage_prevention_shield_expired",
                                            object_label(game, moved) + " moved zones; " + label + " expired with " + std::to_string(read->remaining) + " remaining");
            ++expired_count;
            continue;
        }
        if (write != read) {
            *write = std::move(*read);
        }
        ++write;
    }
    game.damage_prevention_shields.erase(write, game.damage_prevention_shields.end());
    if (expired_count != 0U && zone_change_record_index != 0U && zone_change_record_index <= game.zone_change_records.size()) {
        auto& zone_record = game.zone_change_records[zone_change_record_index - 1U];
        zone_record.first_damage_prevention_record_index = first_record_index;
        zone_record.damage_prevention_record_count = expired_count;
    }
    return expired_count;
}

u32 clear_counters_for_zone_change(GameState& game, ObjectId moved, u32 zone_change_record_index, Zone from_zone, Zone to_zone) {
    if (!moved.valid() || from_zone == to_zone) {
        return 0U;
    }
    auto& obj = object(game, moved);
    const CounterSet before = obj.counters;
    const u32 removed = before.total();
    if (removed == 0U) {
        return 0U;
    }
    obj.counters = CounterSet{};

    u32 records = 0U;
    auto record_removed = [&](CounterKind kind, u32 amount) {
        if (amount == 0U) {
            return;
        }
        ++records;
        record_object_counter_change(game,
                                     moved,
                                     kind,
                                     CounterChangeKind::ObjectRemoved,
                                     amount,
                                     amount,
                                     0U,
                                     "counters_removed_on_zone_change",
                                     object_label(game, moved) + " lost " + std::to_string(amount) + " " + to_string(kind) + " counter(s) on zone change",
                                     ObjectId{},
                                     false,
                                     zone_change_record_index,
                                     false,
                                     true);
    };
    record_removed(CounterKind::PlusOnePlusOne, before.plus_one_plus_one);
    record_removed(CounterKind::MinusOneMinusOne, before.minus_one_minus_one);
    record_removed(CounterKind::Loyalty, before.loyalty);
    record_removed(CounterKind::Defense, before.defense);
    record_removed(CounterKind::Charge, before.charge);
    return records;
}

[[nodiscard]] AttachmentKind attachment_kind_for_object(const GameState& game, ObjectId attachment_id) noexcept {
    if (!valid_object_index(game, attachment_id)) {
        return AttachmentKind::None;
    }
    const auto& obj = object(game, attachment_id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return AttachmentKind::None;
    }
    return def->attachment_kind;
}

void clear_attachment_links_for_zone_change(GameState& game, ObjectId moved) {
    if (!moved.valid() || !valid_object_index(game, moved)) {
        return;
    }

    if (object(game, moved).attached_to.valid()) {
        detach_object(game, moved);
    }

    const auto moved_target = TargetRef{.kind = TargetKind::Object, .object = moved};
    std::vector<ObjectId> to_detach;
    for (const auto& candidate : game.objects) {
        if (candidate.id == moved || candidate.zone != Zone::Battlefield ||
            !target_refs_equal(candidate.attached_to, moved_target)) {
            continue;
        }
        to_detach.push_back(candidate.id);
    }

    for (const auto attachment_id : to_detach) {
        if (valid_object_index(game, attachment_id) && object(game, attachment_id).zone == Zone::Battlefield) {
            if (attachment_kind_for_object(game, attachment_id) == AttachmentKind::Aura) {
                record_event(game, "aura_lost_enchanted_object", object_label(game, attachment_id) + " lost " + object_label(game, moved) + "; pending SBA cleanup");
            }
            detach_object(game, attachment_id);
        }
    }
}

[[nodiscard]] bool creature_replacement_scope(StaticEffectScope scope) noexcept {
    return scope == StaticEffectScope::CreaturesYouControl ||
           scope == StaticEffectScope::CreaturesOpponentsControl ||
           scope == StaticEffectScope::AllCreatures;
}

[[nodiscard]] bool zone_change_replacement_applies_to_object(const GameState& game,
                                                             const GameObject& source,
                                                             const ZoneChangeReplacementDefinition& replacement,
                                                             ObjectId target_id,
                                                             Zone source_zone,
                                                             Zone requested_zone,
                                                             u32 target_type_mask) noexcept {
    if (!replacement.active() || source.zone != Zone::Battlefield || source.ceased_to_exist ||
        !source.id.valid() || !target_id.valid() || target_id.value > game.objects.size() ||
        replacement.from_zone != source_zone || replacement.to_zone != requested_zone) {
        return false;
    }
    const auto& target = game.objects[target_id.value - 1U];
    if (target.zone != source_zone || target.ceased_to_exist || !static_scope_matches(source, target, replacement.scope)) {
        return false;
    }
    if (creature_replacement_scope(replacement.scope) && !has_type_mask(target_type_mask, TypeCreature)) {
        return false;
    }
    return type_mask_matches_static_effect(target_type_mask, replacement.affected_type_mask);
}

struct ZoneChangeReplacementCandidate {
    PlayerId controller{};
    ObjectId source{};
    std::string name;
    Zone replacement_zone = Zone::Graveyard;
    u32 definition_index = 0;
    ReplacementPriorityTier priority_tier = ReplacementPriorityTier::General;
    u32 choice_rank = 0;
    u32 discovery_order = 0;
    u64 source_zone_change_index = 0;
};

struct ZoneChangeReplacementChoice {
    ZoneChangeReplacementCandidate chosen{};
    u32 candidate_count = 0;
    u32 eligible_candidate_count = 0;
    ReplacementPriorityTier candidate_min_priority_tier = ReplacementPriorityTier::General;
};

struct AppliedZoneChangeReplacement {
    ObjectId source{};
    u32 definition_index = 0;
    u64 source_zone_change_index = 0;
};

struct ZoneChangeReplacementResult {
    Zone final_zone = Zone::Library;
    u32 first_record_index = 0;
    u32 record_count = 0;
};

[[nodiscard]] bool same_applied_zone_replacement(const AppliedZoneChangeReplacement& applied,
                                                 const ZoneChangeReplacementCandidate& candidate) noexcept {
    return applied.source == candidate.source &&
           applied.definition_index == candidate.definition_index &&
           applied.source_zone_change_index == candidate.source_zone_change_index;
}

[[nodiscard]] PlayerId zone_change_affected_player(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return PlayerId{};
    }
    const auto& target = object(game, object_id);
    if (target.controller.valid()) {
        return target.controller;
    }
    return target.owner;
}

[[nodiscard]] std::vector<ZoneChangeReplacementCandidate> collect_zone_change_replacement_candidates(
    const GameState& game,
    ObjectId object_id,
    Zone source_zone,
    Zone requested_zone,
    u32 target_type_mask,
    const std::vector<AppliedZoneChangeReplacement>& already_applied) {
    std::vector<ZoneChangeReplacementCandidate> candidates;
    u32 discovery = 0;
    for (const auto& p : game.players) {
        for (const auto source_id : p.zones[zone_index(Zone::Battlefield)]) {
            if (!valid_object_index(game, source_id)) {
                continue;
            }
            const auto& source = object(game, source_id);
            const auto* source_def = current_definition_for_object(game, source);
            if (source_def == nullptr || source_def->zone_change_replacements.empty()) {
                continue;
            }
            for (std::size_t replacement_index = 0; replacement_index < source_def->zone_change_replacements.size(); ++replacement_index) {
                ++discovery;
                const auto& replacement = source_def->zone_change_replacements[replacement_index];
                if (!zone_change_replacement_applies_to_object(game, source, replacement, object_id, source_zone, requested_zone, target_type_mask)) {
                    continue;
                }
                ZoneChangeReplacementCandidate candidate{
                    .controller = source.controller,
                    .source = source_id,
                    .name = replacement.name.empty() ? source_def->name : replacement.name,
                    .replacement_zone = replacement.replacement_zone,
                    .definition_index = static_cast<u32>(replacement_index),
                    .priority_tier = replacement.priority_tier,
                    .choice_rank = replacement.choice_rank,
                    .discovery_order = discovery,
                    .source_zone_change_index = source.zone_change_index
                };
                const bool already_used = std::any_of(already_applied.begin(), already_applied.end(), [&](const AppliedZoneChangeReplacement& applied) {
                    return same_applied_zone_replacement(applied, candidate);
                });
                if (!already_used) {
                    candidates.push_back(std::move(candidate));
                }
            }
        }
    }
    return candidates;
}

[[nodiscard]] ZoneChangeReplacementChoice choose_zone_change_replacement_candidate(
    GameState& game,
    ObjectId object_id,
    Zone source_zone,
    Zone requested_zone,
    std::vector<ZoneChangeReplacementCandidate> candidates) {
    const PlayerId chooser = zone_change_affected_player(game, object_id);
    ReplacementPriorityTier min_tier = ReplacementPriorityTier::Count;
    for (const auto& candidate : candidates) {
        if (static_cast<u8>(candidate.priority_tier) < static_cast<u8>(min_tier)) {
            min_tier = candidate.priority_tier;
        }
    }
    std::vector<ZoneChangeReplacementCandidate> eligible;
    eligible.reserve(candidates.size());
    for (const auto& candidate : candidates) {
        if (candidate.priority_tier == min_tier) {
            eligible.push_back(candidate);
        }
    }
    std::stable_sort(eligible.begin(), eligible.end(), [](const ZoneChangeReplacementCandidate& a, const ZoneChangeReplacementCandidate& b) {
        if (a.choice_rank != b.choice_rank) {
            return a.choice_rank > b.choice_rank;
        }
        if (a.source.value != b.source.value) {
            return a.source.value < b.source.value;
        }
        return a.discovery_order < b.discovery_order;
    });
    const auto chosen = eligible.front();
    if (candidates.size() > 1U || eligible.size() > 1U) {
        record_event(game,
                     "zone_change_replacement_choice",
                     object_label(game, object_id) + " " + to_string(source_zone) + " -> " + to_string(requested_zone) +
                         " chooser=" + (valid_player_index(game, chooser) ? player(game, chooser).name : std::string("<none>")) +
                         " candidates=" + std::to_string(candidates.size()) +
                         " eligible=" + std::to_string(eligible.size()) +
                         " tier=" + to_string(min_tier) +
                         " chose=" + chosen.name +
                         " rank=" + std::to_string(chosen.choice_rank));
    }
    return ZoneChangeReplacementChoice{
        .chosen = chosen,
        .candidate_count = static_cast<u32>(candidates.size()),
        .eligible_candidate_count = static_cast<u32>(eligible.size()),
        .candidate_min_priority_tier = min_tier
    };
}

[[nodiscard]] ZoneChangeReplacementResult apply_zone_change_replacement(GameState& game, ObjectId object_id, Zone source_zone, Zone requested_zone) {
    ZoneChangeReplacementResult result{.final_zone = requested_zone};
    if (!valid_object_index(game, object_id) || source_zone != Zone::Battlefield || requested_zone == source_zone) {
        return result;
    }

    const u32 target_type_mask = object_type_mask(game, object_id);
    const PlayerId affected_player = zone_change_affected_player(game, object_id);
    Zone current_destination = requested_zone;
    std::vector<AppliedZoneChangeReplacement> already_applied;
    constexpr std::size_t max_replacement_passes = 32U;

    for (std::size_t pass = 0; pass < max_replacement_passes; ++pass) {
        auto candidates = collect_zone_change_replacement_candidates(
            game,
            object_id,
            source_zone,
            current_destination,
            target_type_mask,
            already_applied);
        if (candidates.empty()) {
            result.final_zone = current_destination;
            return result;
        }

        const auto choice = choose_zone_change_replacement_candidate(game, object_id, source_zone, current_destination, std::move(candidates));
        const auto& chosen = choice.chosen;
        already_applied.push_back(AppliedZoneChangeReplacement{
            .source = chosen.source,
            .definition_index = chosen.definition_index,
            .source_zone_change_index = chosen.source_zone_change_index
        });

        const u32 replacement_record_index = static_cast<u32>(game.zone_change_replacement_records.size() + 1U);
        if (result.first_record_index == 0U) {
            result.first_record_index = replacement_record_index;
        }
        ++result.record_count;
        game.zone_change_replacement_records.push_back(ZoneChangeReplacementRecord{
            .sequence = game.next_event_sequence,
            .object = object_id,
            .affected_player = affected_player,
            .controller = chosen.controller,
            .source = chosen.source,
            .name = chosen.name,
            .from_zone = source_zone,
            .event_to_zone = current_destination,
            .replacement_zone = chosen.replacement_zone,
            .definition_index = chosen.definition_index,
            .priority_tier = chosen.priority_tier,
            .candidate_min_priority_tier = choice.candidate_min_priority_tier,
            .choice_rank = chosen.choice_rank,
            .candidate_count = choice.candidate_count,
            .eligible_candidate_count = choice.eligible_candidate_count,
            .pass_index = static_cast<u32>(pass + 1U),
            .zone_change_record_index = 0,
            .source_zone_change_index = chosen.source_zone_change_index,
            .chosen_among_multiple = choice.eligible_candidate_count > 1U
        });
        record_event_with_links(game,
                                "zone_change_replaced",
                                object_label(game, object_id) + " " + to_string(source_zone) + " -> " + to_string(current_destination) +
                                    " replaced by " + chosen.name + " from " + object_label(game, chosen.source) +
                                    " with " + to_string(chosen.replacement_zone),
                                EventRecordLinks{
                                    .kind = EventRecordKind::ZoneReplacement,
                                    .object = object_id,
                                    .player = affected_player,
                                    .zone_replacement_record_index = replacement_record_index
                                });
        current_destination = chosen.replacement_zone;
    }

    record_event(game,
                 "zone_change_replacement_pass_limit",
                 object_label(game, object_id) + " " + to_string(source_zone) + " -> " + to_string(requested_zone) +
                     " reached replacement pass limit; using " + to_string(current_destination));
    result.final_zone = current_destination;
    return result;
}

void record_event_with_links(GameState& game, std::string kind, std::string detail, EventRecordLinks links) {
    const u64 sequence = game.next_event_sequence++;
    const std::string log_kind = kind;
    game.events.push_back(Event{sequence, std::move(kind), std::move(detail)});
    game.event_records.push_back(EventRecord{
        .sequence = sequence,
        .kind = links.kind,
        .log_kind = log_kind,
        .object = links.object,
        .object_zone_change_index = links.object_zone_change_index,
        .player = links.player,
        .target = links.target,
        .choice_mode_index = links.choice_mode_index,
        .choice_mode_contract_hash = links.choice_mode_contract_hash,
        .choice_target_count = links.choice_target_count,
        .choice_target_set_hash = links.choice_target_set_hash,
        .zone_change_record_index = links.zone_change_record_index,
        .zone_replacement_record_index = links.zone_replacement_record_index,
        .damage_record_index = links.damage_record_index,
        .damage_prevention_record_index = links.damage_prevention_record_index,
        .life_change_record_index = links.life_change_record_index,
        .mana_change_record_index = links.mana_change_record_index,
        .counter_change_record_index = links.counter_change_record_index,
        .discard_record_index = links.discard_record_index,
        .trigger_record_index = links.trigger_record_index,
        .stack_placement_record_index = links.stack_placement_record_index,
        .stack_resolution_record_index = links.stack_resolution_record_index,
        .priority_transition_record_index = links.priority_transition_record_index,
        .state_based_action_record_index = links.state_based_action_record_index,
        .combat_declaration_record_index = links.combat_declaration_record_index,
        .combat_damage_assignment_record_index = links.combat_damage_assignment_record_index,
        .mana_payment_plan_record_index = links.mana_payment_plan_record_index,
        .draw_record_index = links.draw_record_index,
        .mulligan_record_index = links.mulligan_record_index,
        .mulligan_keep_record_index = links.mulligan_keep_record_index,
        .paid_action_declaration_record_index = links.paid_action_declaration_record_index,
        .paid_action_transaction_record_index = links.paid_action_transaction_record_index
    });
}

struct StackPlacementContext {
    PlayerId priority_before{};
    Zone source_zone_before = Zone::Library;
    u64 source_zone_change_index_before = 0;
    u32 stack_size_before = 0;
    u32 stack_enter_zone_change_record_index = 0;
};

[[nodiscard]] StackPlacementContext capture_stack_placement_context(const GameState& game, ObjectId source_object) {
    StackPlacementContext ctx{};
    ctx.priority_before = game.priority_player;
    ctx.stack_size_before = static_cast<u32>(game.stack.size());
    if (valid_object_index(game, source_object)) {
        const auto& source = object(game, source_object);
        ctx.source_zone_before = source.zone;
        ctx.source_zone_change_index_before = source.zone_change_index;
    }
    return ctx;
}

u32 record_stack_placement(GameState& game, StackPlacementRecord record) {
    record.sequence = game.next_event_sequence;
    record.priority_after = game.priority_player;
    record.stack_size_after = static_cast<u32>(game.stack.size());
    const u32 record_index = static_cast<u32>(game.stack_placement_records.size() + 1U);
    const ObjectId stack_object = record.stack_object;
    const PlayerId controller = record.controller;
    const StackPlacementKind placement_kind = record.kind;
    game.stack_placement_records.push_back(std::move(record));
    std::string detail = object_label(game, stack_object) + " placement=" + to_string(placement_kind) +
        " priority=" + (controller.valid() ? player(game, controller).name : std::string("<none>"));
    record_event_with_links(game,
                            "stack_placement_recorded",
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::StackPlacement,
                                .object = stack_object,
                                .player = controller,
                                .stack_placement_record_index = record_index
                            });
    return record_index;
}


void record_draw_record(GameState& game, DrawRecord record) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.draw_records.size() + 1U);
    const PlayerId drawing_player = record.player;
    const ObjectId drawn_card = record.card;
    const DrawRecordOutcome outcome = record.outcome;
    game.draw_records.push_back(std::move(record));

    std::string detail = drawing_player.valid() ? player(game, drawing_player).name : std::string("<invalid player>");
    detail += " outcome=";
    detail += to_string(outcome);
    if (drawn_card.valid()) {
        detail += " card=";
        detail += object_label(game, drawn_card);
    }
    record_event_with_links(game,
                            outcome == DrawRecordOutcome::EmptyLibrary ? "draw_empty_library" : "draw",
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::Draw,
                                .object = drawn_card,
                                .player = drawing_player,
                                .draw_record_index = record_index
                            });
}

void record_mulligan_record(GameState& game, MulliganRecord record) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.mulligan_records.size() + 1U);
    const PlayerId mulligan_player = record.player;
    game.mulligan_records.push_back(std::move(record));

    std::string detail = mulligan_player.valid() ? player(game, mulligan_player).name : std::string("<invalid player>");
    const auto& stored = game.mulligan_records.back();
    detail += " mulligans=" + std::to_string(stored.mulligans_after);
    detail += " returned=" + std::to_string(stored.returned_count);
    detail += " drew=" + std::to_string(stored.successful_draw_count);
    record_event_with_links(game,
                            "mulligan",
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::Mulligan,
                                .player = mulligan_player,
                                .mulligan_record_index = record_index
                            });
}

void record_mulligan_keep_record(GameState& game, MulliganKeepRecord record) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.mulligan_keep_records.size() + 1U);
    const PlayerId keep_player = record.player;
    game.mulligan_keep_records.push_back(std::move(record));

    std::string detail = keep_player.valid() ? player(game, keep_player).name : std::string("<invalid player>");
    const auto& stored = game.mulligan_keep_records.back();
    detail += " keep_mulligans=" + std::to_string(stored.mulligans_taken);
    detail += " bottomed=" + std::to_string(stored.bottom_count);
    detail += stored.explicit_choice ? " explicit" : " fallback";
    record_event_with_links(game,
                            "mulligan_keep",
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::MulliganKeep,
                                .player = keep_player,
                                .mulligan_keep_record_index = record_index
                            });
}

void record_discard_record(GameState& game, DiscardRecord record) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.discard_records.size() + 1U);
    const PlayerId discard_player = record.player;
    const ObjectId discarded_card = record.card;
    const DiscardRecordKind discard_kind = record.kind;
    game.discard_records.push_back(std::move(record));

    std::string detail = discard_player.valid() ? player(game, discard_player).name : std::string("<invalid player>");
    detail += " discarded ";
    detail += discarded_card.valid() && valid_object_index(game, discarded_card) ? object_label(game, discarded_card) : std::string("<invalid card>");
    detail += " kind=";
    detail += to_string(discard_kind);
    const std::string log_kind = discard_kind == DiscardRecordKind::CleanupHandSize ? "discard_cleanup" :
        (discard_kind == DiscardRecordKind::CostPayment ? "discard_cost_payment" : "discard");
    record_event_with_links(game,
                            log_kind,
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::Discard,
                                .object = discarded_card,
                                .player = discard_player,
                                .discard_record_index = record_index
                            });
}

void place_library_object_on_bottom(GameState& game, PlayerId player_id, ObjectId object_id, u32 bottom_slot) {
    auto& library = zone(game, player_id, Zone::Library);
    const auto it = std::find(library.begin(), library.end(), object_id);
    if (it == library.end()) {
        throw std::logic_error("bottomed mulligan card not found in library after movement");
    }
    const ObjectId moved = *it;
    library.erase(it);
    const auto clamped_slot = std::min<std::size_t>(bottom_slot, library.size());
    library.insert(library.begin() + static_cast<std::ptrdiff_t>(clamped_slot), moved);
}

struct PriorityTransitionSnapshot {
    PlayerId player{};
    PlayerId active_player{};
    PlayerId priority_before{};
    Step step_before = Step::Untap;
    u32 stack_size_before = 0;
    ObjectId stack_top_before{};
    u32 consecutive_passes_before = 0;
    u32 alive_players = 0;
    u32 pending_triggers_before = 0;
    u32 trigger_stack_record_count_before = 0;
};

[[nodiscard]] ObjectId stack_top_or_none(const GameState& game) noexcept {
    return game.stack.empty() ? ObjectId{} : game.stack.back();
}

[[nodiscard]] PriorityTransitionSnapshot capture_priority_transition_snapshot(const GameState& game) {
    PriorityTransitionSnapshot snapshot{};
    snapshot.player = game.priority_player;
    snapshot.active_player = game.active_player;
    snapshot.priority_before = game.priority_player;
    snapshot.step_before = game.step;
    snapshot.stack_size_before = static_cast<u32>(game.stack.size());
    snapshot.stack_top_before = stack_top_or_none(game);
    snapshot.consecutive_passes_before = game.consecutive_priority_passes;
    snapshot.alive_players = alive_player_count(game);
    snapshot.pending_triggers_before = static_cast<u32>(game.pending_triggers.size());
    snapshot.trigger_stack_record_count_before = static_cast<u32>(std::count_if(game.trigger_records.begin(), game.trigger_records.end(), [](const TriggerRecord& record) {
        return record.put_on_stack_sequence != 0U;
    }));
    return snapshot;
}

void record_priority_transition(GameState& game, const PriorityTransitionSnapshot& snapshot, PriorityTransitionOutcome outcome, u32 stack_resolution_record_index = 0U) {
    PriorityTransitionRecord record{};
    record.sequence = game.next_event_sequence;
    record.outcome = outcome;
    record.player = snapshot.player;
    record.active_player = snapshot.active_player;
    record.priority_before = snapshot.priority_before;
    record.priority_after = game.priority_player;
    record.step_before = snapshot.step_before;
    record.step_after = game.step;
    record.stack_size_before = snapshot.stack_size_before;
    record.stack_size_after = static_cast<u32>(game.stack.size());
    record.stack_top_before = snapshot.stack_top_before;
    record.stack_top_after = stack_top_or_none(game);
    record.consecutive_passes_before = snapshot.consecutive_passes_before;
    record.consecutive_passes_after_pass = outcome == PriorityTransitionOutcome::PendingTriggersPutOnStack
        ? snapshot.consecutive_passes_before
        : snapshot.consecutive_passes_before + 1U;
    record.consecutive_passes_after = game.consecutive_priority_passes;
    record.alive_players = snapshot.alive_players;
    record.pending_triggers_before = snapshot.pending_triggers_before;
    record.pending_triggers_after = static_cast<u32>(game.pending_triggers.size());
    record.stack_resolution_record_index = stack_resolution_record_index;
    record.trigger_stack_record_count_before = snapshot.trigger_stack_record_count_before;
    record.trigger_stack_record_count_after = static_cast<u32>(std::count_if(game.trigger_records.begin(), game.trigger_records.end(), [](const TriggerRecord& trigger_record) {
        return trigger_record.put_on_stack_sequence != 0U;
    }));
    record.pass_count_incremented = record.consecutive_passes_after_pass > record.consecutive_passes_before;
    record.priority_changed = record.priority_before != record.priority_after;
    record.stack_resolved = outcome == PriorityTransitionOutcome::StackResolved;
    record.step_advanced = outcome == PriorityTransitionOutcome::StepAdvanced;
    record.pending_triggers_put_on_stack = outcome == PriorityTransitionOutcome::PendingTriggersPutOnStack;

    const u32 record_index = static_cast<u32>(game.priority_transition_records.size() + 1U);
    game.priority_transition_records.push_back(std::move(record));
    record_event_with_links(game,
                            "priority_transition_recorded",
                            (snapshot.player.valid() ? player(game, snapshot.player).name : std::string("<none>")) +
                                " outcome=" + to_string(outcome) +
                                " passes=" + std::to_string(game.priority_transition_records.back().consecutive_passes_before) +
                                "->" + std::to_string(game.priority_transition_records.back().consecutive_passes_after_pass) +
                                " final=" + std::to_string(game.priority_transition_records.back().consecutive_passes_after),
                            EventRecordLinks{
                                .kind = EventRecordKind::PriorityTransition,
                                .player = snapshot.player,
                                .priority_transition_record_index = record_index
                            });
}

[[nodiscard]] StackPlacementContext move_spell_card_to_stack_for_cast(GameState& game, PlayerId caster, ObjectId object_id) {
    StackPlacementContext ctx = capture_stack_placement_context(game, object_id);
    const std::size_t before_zone_records = game.zone_change_records.size();
    move_object(game, object_id, caster, Zone::Stack);
    if (game.zone_change_records.size() > before_zone_records) {
        ctx.stack_enter_zone_change_record_index = static_cast<u32>(before_zone_records + 1U);
    }
    game.priority_player = caster;
    game.consecutive_priority_passes = 0;
    record_event(game, "cast_spell", player(game, caster).name + " cast " + object_label(game, object_id));
    return ctx;
}

[[nodiscard]] StackPlacementRecord make_spell_stack_placement_record(const GameState& game,
                                                                     PlayerId caster,
                                                                     ObjectId object_id,
                                                                     const StackPlacementContext& ctx,
                                                                     bool mana_cost_required,
                                                                     bool mana_cost_paid,
                                                                     bool sacrifice_cost_required,
                                                                     bool sacrifice_cost_paid,
                                                                     bool discard_cost_required,
                                                                     bool discard_cost_paid,
                                                                     bool life_cost_required,
                                                                     bool life_cost_paid,
                                                                     bool return_cost_required,
                                                                     bool return_cost_paid) {
    const auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    StackPlacementRecord record{};
    record.kind = StackPlacementKind::SpellCast;
    record.source_object = object_id;
    record.stack_object = object_id;
    record.controller = caster;
    record.source_zone_before = ctx.source_zone_before;
    record.source_zone_change_index_before = ctx.source_zone_change_index_before;
    record.stack_zone_change_index = obj.zone_change_index;
    record.stack_enter_zone_change_record_index = ctx.stack_enter_zone_change_record_index;
    record.chosen_mode_index = obj.chosen_mode_index;
    if (def != nullptr) {
        record.target_mask = def->target_mask;
        record.target_count = def->target_count;
        if (def->is_modal() && valid_spell_mode_index(*def, obj.chosen_mode_index)) {
            const auto& mode = spell_mode_definition(*def, obj.chosen_mode_index);
            record.target_mask = mode.target_mask;
            record.target_count = mode.target_count;
        }
    }
    record.chosen_targets = obj.targets;
    record.stack_size_before = ctx.stack_size_before;
    record.priority_before = ctx.priority_before;
    record.physical_card = true;
    record.ability_object = false;
    record.modal_choice = def != nullptr && def->is_modal();
    record.target_choice = !obj.targets.empty();
    record.mana_cost_required = mana_cost_required;
    record.mana_cost_paid = mana_cost_paid;
    record.sacrifice_cost_required = sacrifice_cost_required;
    record.sacrifice_cost_paid = sacrifice_cost_paid;
    record.discard_cost_required = discard_cost_required;
    record.discard_cost_paid = discard_cost_paid;
    record.life_cost_required = life_cost_required;
    record.life_cost_paid = life_cost_paid;
    record.return_cost_required = return_cost_required;
    record.return_cost_paid = return_cost_paid;
    return record;
}

u32 record_paid_action_declaration(GameState& game, PaidActionDeclarationRecord record) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.paid_action_declaration_records.size() + 1U);
    game.paid_action_declaration_records.push_back(std::move(record));
    const auto& stored = game.paid_action_declaration_records.back();
    std::string detail = std::string(to_string(stored.action_kind)) + " declare ";
    detail += stored.stack_object.valid() ? object_label(game, stored.stack_object) : std::string("<invalid>");
    detail += " cost_locked=";
    detail += stored.total_cost_locked ? "true" : "false";
    record_event_with_links(game,
                            "paid_action_declaration_recorded",
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::PaidActionDeclaration,
                                .object = stored.stack_object,
                                .player = stored.player,
                                .paid_action_declaration_record_index = record_index
                            });
    return record_index;
}

u32 record_spell_paid_action_declaration(GameState& game,
                                         PlayerId caster,
                                         ObjectId object_id,
                                         const CardDefinition& def,
                                         const StackPlacementContext& ctx,
                                         u64 stack_object_entered_sequence) {
    const auto& stack_obj = object(game, object_id);
    PaidActionDeclarationRecord record{};
    record.action_kind = ActionKind::CastSpellFromHandPaid;
    record.player = caster;
    record.source_object = object_id;
    record.stack_object = object_id;
    record.definition_index = stack_obj.definition_index;
    record.source_zone_before = ctx.source_zone_before;
    record.source_zone_change_index_before = ctx.source_zone_change_index_before;
    record.stack_zone_change_index = stack_obj.zone_change_index;
    record.stack_enter_zone_change_record_index = ctx.stack_enter_zone_change_record_index;
    record.stack_object_entered_sequence = stack_object_entered_sequence;
    record.choices_locked_sequence = game.next_event_sequence > 1U ? game.next_event_sequence - 1U : 0U;
    record.declared_mode_index = stack_obj.chosen_mode_index;
    record.target_mask = def.target_mask;
    record.target_count = def.target_count;
    if (def.is_modal() && valid_spell_mode_index(def, stack_obj.chosen_mode_index)) {
        const auto& mode = spell_mode_definition(def, stack_obj.chosen_mode_index);
        record.declared_mode_contract_hash = mode_choice_contract_hash_impl(mode);
        record.target_mask = mode.target_mask;
        record.target_count = mode.target_count;
    }
    record.declared_targets = stack_obj.targets;
    record.declared_target_set_hash = target_choice_set_hash_impl(stack_obj.targets);
    record.total_mana_cost = def.mana_cost;
    record.sacrifice_cost = def.sacrifice_cost;
    record.discard_cost = def.discard_cost;
    record.life_cost = def.life_cost;
    record.return_cost = def.return_cost;
    record.total_cost_locked = true;
    record.mana_cost_required = !def.mana_cost.free();
    record.sacrifice_cost_required = def.sacrifice_cost.active();
    record.discard_cost_required = def.discard_cost.active();
    record.life_cost_required = def.life_cost.active();
    record.return_cost_required = def.return_cost.active();
    record.modal_choice_declared = def.is_modal();
    record.target_choice_declared = !stack_obj.targets.empty();
    return record_paid_action_declaration(game, std::move(record));
}

u32 record_activated_ability_paid_action_declaration(GameState& game,
                                                     PlayerId controller,
                                                     ObjectId source_object,
                                                     ObjectId stack_object,
                                                     const ActivatedAbilityDefinition& ability,
                                                     const StackPlacementContext& ctx,
                                                     u32 ability_index,
                                                     u64 stack_object_entered_sequence,
                                                     u64 choices_locked_sequence) {
    const auto& stack_obj = object(game, stack_object);
    PaidActionDeclarationRecord record{};
    record.action_kind = ActionKind::ActivateActivatedAbility;
    record.player = controller;
    record.source_object = source_object;
    record.stack_object = stack_object;
    record.definition_index = stack_obj.definition_index;
    record.source_zone_before = ctx.source_zone_before;
    record.source_zone_change_index_before = ctx.source_zone_change_index_before;
    record.stack_zone_change_index = stack_obj.zone_change_index;
    record.stack_enter_zone_change_record_index = 0U;
    record.stack_object_entered_sequence = stack_object_entered_sequence;
    record.choices_locked_sequence = choices_locked_sequence;
    record.ability_index = ability_index;
    record.target_mask = ability.target_mask;
    record.target_count = ability.target_count;
    record.declared_targets = stack_obj.targets;
    record.declared_target_set_hash = target_choice_set_hash_impl(stack_obj.targets);
    record.total_mana_cost = ability.mana_cost;
    record.sacrifice_cost = ability.sacrifice_cost;
    record.discard_cost = ability.discard_cost;
    record.life_cost = ability.life_cost;
    record.return_cost = ability.return_cost;
    record.total_cost_locked = true;
    record.mana_cost_required = !ability.mana_cost.free();
    record.tap_cost_required = ability.tap_cost;
    record.sacrifice_cost_required = ability.sacrifice_cost.active();
    record.discard_cost_required = ability.discard_cost.active();
    record.life_cost_required = ability.life_cost.active();
    record.return_cost_required = ability.return_cost.active();
    record.target_choice_declared = !stack_obj.targets.empty();
    return record_paid_action_declaration(game, std::move(record));
}

u32 record_loyalty_ability_paid_action_declaration(GameState& game,
                                                   PlayerId controller,
                                                   ObjectId source_object,
                                                   ObjectId stack_object,
                                                   const LoyaltyAbilityDefinition& ability,
                                                   const StackPlacementContext& ctx,
                                                   u64 stack_object_entered_sequence,
                                                   u64 choices_locked_sequence) {
    const auto& stack_obj = object(game, stack_object);
    PaidActionDeclarationRecord record{};
    record.action_kind = ActionKind::ActivateLoyaltyAbility;
    record.player = controller;
    record.source_object = source_object;
    record.stack_object = stack_object;
    record.definition_index = stack_obj.definition_index;
    record.source_zone_before = ctx.source_zone_before;
    record.source_zone_change_index_before = ctx.source_zone_change_index_before;
    record.stack_zone_change_index = stack_obj.zone_change_index;
    record.stack_enter_zone_change_record_index = 0U;
    record.stack_object_entered_sequence = stack_object_entered_sequence;
    record.choices_locked_sequence = choices_locked_sequence;
    record.ability_index = 1U;
    record.loyalty_cost_delta = ability.cost;
    record.target_mask = ability.target_mask;
    record.target_count = ability.target_count;
    record.declared_targets = stack_obj.targets;
    record.declared_target_set_hash = target_choice_set_hash_impl(stack_obj.targets);
    record.total_cost_locked = true;
    record.loyalty_cost_required = true;
    record.target_choice_declared = !stack_obj.targets.empty();
    return record_paid_action_declaration(game, std::move(record));
}

void seal_paid_action_declaration_for_stack_placement(GameState& game,
                                                      u32 declaration_record_index,
                                                      StackPlacementRecord& placement) noexcept {
    if (declaration_record_index == 0U || declaration_record_index > game.paid_action_declaration_records.size()) {
        return;
    }
    auto& declaration = game.paid_action_declaration_records[declaration_record_index - 1U];
    declaration.payment_attempted = placement.first_paid_action_event_sequence != 0U;
    declaration.first_payment_event_sequence = placement.first_paid_action_event_sequence;
    declaration.last_payment_event_sequence = placement.last_paid_action_event_sequence;
    declaration.first_sacrifice_cost_payment_record_index = placement.first_sacrifice_cost_payment_record_index;
    declaration.sacrifice_cost_payment_record_count = placement.sacrifice_cost_payment_record_count;
    declaration.sacrifice_cost_payment_hash = placement.sacrifice_cost_payment_hash;
    declaration.first_discard_cost_payment_record_index = placement.first_discard_cost_payment_record_index;
    declaration.discard_cost_payment_record_count = placement.discard_cost_payment_record_count;
    declaration.discard_cost_payment_hash = placement.discard_cost_payment_hash;
    declaration.first_tap_cost_payment_record_index = placement.first_tap_cost_payment_record_index;
    declaration.tap_cost_payment_record_count = placement.tap_cost_payment_record_count;
    declaration.tap_cost_payment_hash = placement.tap_cost_payment_hash;
    declaration.first_life_cost_payment_record_index = placement.first_life_cost_payment_record_index;
    declaration.life_cost_payment_record_count = placement.life_cost_payment_record_count;
    declaration.life_cost_payment_hash = placement.life_cost_payment_hash;
    declaration.first_return_cost_payment_record_index = placement.first_return_cost_payment_record_index;
    declaration.return_cost_payment_record_count = placement.return_cost_payment_record_count;
    declaration.return_cost_payment_hash = placement.return_cost_payment_hash;
    declaration.first_loyalty_cost_payment_record_index = placement.first_loyalty_cost_payment_record_index;
    declaration.loyalty_cost_payment_record_count = placement.loyalty_cost_payment_record_count;
    declaration.loyalty_cost_payment_hash = placement.loyalty_cost_payment_hash;
    declaration.stack_placement_record_index = static_cast<u32>(game.stack_placement_records.size() + 1U);
    declaration.declaration_hash = paid_action_declaration_record_hash(declaration);
    placement.paid_action_declaration_record_index = declaration_record_index;
    placement.paid_action_declaration_hash = declaration.declaration_hash;
}

u32 record_paid_action_transaction_commit(GameState& game,
                                          ActionKind action_kind,
                                          u32 stack_placement_record_index,
                                          u64 physical_state_hash_before_action) {
    if (stack_placement_record_index == 0U || stack_placement_record_index > game.stack_placement_records.size()) {
        return 0U;
    }
    const auto& placement = game.stack_placement_records[stack_placement_record_index - 1U];
    PaidActionTransactionRecord record{};
    record.sequence = game.next_event_sequence;
    record.outcome = PaidActionTransactionOutcome::Committed;
    record.action_kind = action_kind;
    record.player = placement.controller;
    record.source_object = placement.source_object;
    record.stack_object = placement.stack_object;
    record.stack_placement_record_index = stack_placement_record_index;
    record.paid_action_declaration_record_index = placement.paid_action_declaration_record_index;
    record.paid_action_declaration_hash = placement.paid_action_declaration_hash;
    if (record.paid_action_declaration_record_index != 0U &&
        record.paid_action_declaration_record_index <= game.paid_action_declaration_records.size()) {
        record.committed_paid_action_declaration_snapshot_present = true;
        record.committed_paid_action_declaration_snapshot = game.paid_action_declaration_records[record.paid_action_declaration_record_index - 1U];
    }
    record.stack_object_entered_sequence = placement.stack_object_entered_sequence;
    record.choices_locked_sequence = placement.choices_locked_sequence;
    record.first_paid_action_event_sequence = placement.first_paid_action_event_sequence;
    record.last_paid_action_event_sequence = placement.last_paid_action_event_sequence;
    record.first_mana_payment_plan_record_index = placement.first_mana_payment_plan_record_index;
    record.mana_payment_plan_record_count = placement.mana_payment_plan_record_count;
    record.first_mana_change_record_index = placement.first_mana_change_record_index;
    record.mana_change_record_count = placement.mana_change_record_count;
    record.first_paid_action_counter_change_record_index = placement.first_paid_action_counter_change_record_index;
    record.paid_action_counter_change_record_count = placement.paid_action_counter_change_record_count;
    record.first_paid_action_zone_change_record_index = placement.first_paid_action_zone_change_record_index;
    record.paid_action_zone_change_record_count = placement.paid_action_zone_change_record_count;
    record.first_sacrifice_cost_payment_record_index = placement.first_sacrifice_cost_payment_record_index;
    record.sacrifice_cost_payment_record_count = placement.sacrifice_cost_payment_record_count;
    record.sacrifice_cost_payment_hash = placement.sacrifice_cost_payment_hash;
    record.first_discard_cost_payment_record_index = placement.first_discard_cost_payment_record_index;
    record.discard_cost_payment_record_count = placement.discard_cost_payment_record_count;
    record.discard_cost_payment_hash = placement.discard_cost_payment_hash;
    record.first_tap_cost_payment_record_index = placement.first_tap_cost_payment_record_index;
    record.tap_cost_payment_record_count = placement.tap_cost_payment_record_count;
    record.tap_cost_payment_hash = placement.tap_cost_payment_hash;
    record.first_life_cost_payment_record_index = placement.first_life_cost_payment_record_index;
    record.life_cost_payment_record_count = placement.life_cost_payment_record_count;
    record.life_cost_payment_hash = placement.life_cost_payment_hash;
    record.first_return_cost_payment_record_index = placement.first_return_cost_payment_record_index;
    record.return_cost_payment_record_count = placement.return_cost_payment_record_count;
    record.return_cost_payment_hash = placement.return_cost_payment_hash;
    record.first_loyalty_cost_payment_record_index = placement.first_loyalty_cost_payment_record_index;
    record.loyalty_cost_payment_record_count = placement.loyalty_cost_payment_record_count;
    record.loyalty_cost_payment_hash = placement.loyalty_cost_payment_hash;
    record.physical_state_hash_before = physical_state_hash_before_action;
    record.physical_state_hash_after = canonical_state_hash(game);
    record.next_event_sequence_before = placement.stack_object_entered_sequence != 0U
        ? placement.stack_object_entered_sequence
        : placement.sequence;
    record.speculative_next_event_sequence_after = game.next_event_sequence;
    record.committed = true;
    record.rolled_back = false;
    record.physical_state_preserved_on_rollback = false;
    record.choices_before_payment = placement.choices_locked_before_costs;
    record.payments_before_placement = placement.paid_action_events_before_stack_placement;
    record.placement_before_transaction = placement.sequence < game.next_event_sequence;
    record.transaction_hash = paid_action_transaction_record_hash(record);

    const u32 record_index = static_cast<u32>(game.paid_action_transaction_records.size() + 1U);
    game.paid_action_transaction_records.push_back(record);
    std::string detail = std::string(to_string(action_kind)) + " outcome=" + to_string(record.outcome);
    detail += " placement#" + std::to_string(stack_placement_record_index);
    if (record.paid_action_declaration_record_index != 0U) {
        detail += " declaration#" + std::to_string(record.paid_action_declaration_record_index);
    }
    record_event_with_links(game,
                            "paid_action_transaction_recorded",
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::PaidActionTransaction,
                                .object = record.stack_object,
                                .player = record.player,
                                .paid_action_transaction_record_index = record_index
                            });
    return record_index;
}

struct PaidActionTransactionContext {
    ActionKind action_kind = ActionKind::Count;
    PlayerId player{};
    ObjectId source_object{};
};

[[nodiscard]] u64 first_event_sequence_after(const GameState& game, u64 sequence) noexcept {
    for (const auto& event : game.events) {
        if (event.sequence > sequence) {
            return event.sequence;
        }
    }
    return 0U;
}

[[nodiscard]] u64 last_event_sequence_after(const GameState& game, u64 sequence) noexcept {
    u64 result = 0U;
    for (const auto& event : game.events) {
        if (event.sequence > sequence) {
            result = event.sequence;
        }
    }
    return result;
}

void record_paid_action_transaction_rollback(GameState& game,
                                             const PaidActionTransactionContext& context,
                                             const GameState& staged_game,
                                             u64 physical_state_hash_before,
                                             u64 next_event_sequence_before) {
    PaidActionTransactionRecord record{};
    record.sequence = game.next_event_sequence;
    record.outcome = PaidActionTransactionOutcome::RolledBack;
    record.action_kind = context.action_kind;
    record.player = context.player;
    record.source_object = context.source_object;
    record.stack_object = context.source_object;
    record.speculative_event_count = static_cast<u32>(staged_game.events.size() >= game.events.size() ? staged_game.events.size() - game.events.size() : 0U);
    record.speculative_event_record_count = static_cast<u32>(staged_game.event_records.size() >= game.event_records.size() ? staged_game.event_records.size() - game.event_records.size() : 0U);
    record.speculative_stack_placement_record_count = static_cast<u32>(staged_game.stack_placement_records.size() >= game.stack_placement_records.size() ? staged_game.stack_placement_records.size() - game.stack_placement_records.size() : 0U);
    record.speculative_paid_action_declaration_record_count = static_cast<u32>(staged_game.paid_action_declaration_records.size() >= game.paid_action_declaration_records.size() ? staged_game.paid_action_declaration_records.size() - game.paid_action_declaration_records.size() : 0U);
    if (staged_game.paid_action_declaration_records.size() > game.paid_action_declaration_records.size()) {
        PaidActionDeclarationRecord speculative_declaration = staged_game.paid_action_declaration_records.back();
        const u64 first_payment_sequence = first_event_sequence_after(staged_game, speculative_declaration.sequence);
        const u64 last_payment_sequence = last_event_sequence_after(staged_game, speculative_declaration.sequence);
        speculative_declaration.payment_attempted = first_payment_sequence != 0U;
        speculative_declaration.first_payment_event_sequence = first_payment_sequence;
        speculative_declaration.last_payment_event_sequence = last_payment_sequence;
        speculative_declaration.stack_placement_record_index = 0U;
        speculative_declaration.declaration_hash = 0U;
        record.speculative_paid_action_declaration_sequence = speculative_declaration.sequence;
        record.speculative_paid_action_declaration_hash = paid_action_declaration_record_hash(speculative_declaration);
        record.speculative_paid_action_declaration_snapshot_present = true;
        record.speculative_paid_action_declaration_snapshot = speculative_declaration;
        record.speculative_first_payment_event_sequence = first_payment_sequence;
        record.speculative_last_payment_event_sequence = last_payment_sequence;
        record.stack_object_entered_sequence = speculative_declaration.stack_object_entered_sequence;
        record.choices_locked_sequence = speculative_declaration.choices_locked_sequence;
        record.first_paid_action_event_sequence = first_payment_sequence;
        record.last_paid_action_event_sequence = last_payment_sequence;
        record.choices_before_payment = first_payment_sequence != 0U && speculative_declaration.choices_locked_sequence != 0U &&
                                        speculative_declaration.choices_locked_sequence < first_payment_sequence;
    }
    record.physical_state_hash_before = physical_state_hash_before;
    record.physical_state_hash_after = canonical_state_hash(game);
    record.next_event_sequence_before = next_event_sequence_before;
    record.speculative_next_event_sequence_after = staged_game.next_event_sequence;
    record.committed = false;
    record.rolled_back = true;
    record.physical_state_preserved_on_rollback = record.physical_state_hash_before == record.physical_state_hash_after;
    record.transaction_hash = paid_action_transaction_record_hash(record);

    const u32 record_index = static_cast<u32>(game.paid_action_transaction_records.size() + 1U);
    game.paid_action_transaction_records.push_back(record);
    std::string detail = std::string(to_string(record.action_kind)) + " outcome=" + to_string(record.outcome) +
                         " speculative_events=" + std::to_string(record.speculative_event_count);
    if (record.speculative_paid_action_declaration_hash != 0U) {
        detail += " speculative_declaration_hash=" + std::to_string(record.speculative_paid_action_declaration_hash);
    }
    record_event_with_links(game,
                            "paid_action_transaction_rolled_back",
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::PaidActionTransaction,
                                .object = record.source_object,
                                .player = record.player,
                                .paid_action_transaction_record_index = record_index
                            });
}

[[nodiscard]] StackPlacementRecord make_ability_stack_placement_record(const GameState& game,
                                                                       StackPlacementKind kind,
                                                                       PlayerId controller,
                                                                       ObjectId source_object,
                                                                       ObjectId stack_object,
                                                                       const StackPlacementContext& ctx,
                                                                       u32 ability_index,
                                                                       std::int32_t loyalty_cost_delta,
                                                                       u32 target_mask,
                                                                       u32 target_count,
                                                                       bool mana_cost_required,
                                                                       bool mana_cost_paid,
                                                                       bool tap_cost_required,
                                                                       bool tap_cost_paid,
                                                                       bool sacrifice_cost_required,
                                                                       bool sacrifice_cost_paid,
                                                                       bool discard_cost_required,
                                                                       bool discard_cost_paid,
                                                                       bool life_cost_required,
                                                                       bool life_cost_paid,
                                                                       bool return_cost_required,
                                                                       bool return_cost_paid,
                                                                       bool loyalty_cost_paid) {
    const auto& stack_obj = object(game, stack_object);
    StackPlacementRecord record{};
    record.kind = kind;
    record.source_object = source_object;
    record.stack_object = stack_object;
    record.controller = controller;
    record.source_zone_before = ctx.source_zone_before;
    record.source_zone_change_index_before = ctx.source_zone_change_index_before;
    record.stack_zone_change_index = stack_obj.zone_change_index;
    record.stack_enter_zone_change_record_index = 0U;
    record.ability_index = ability_index;
    record.loyalty_cost_delta = loyalty_cost_delta;
    record.target_mask = target_mask;
    record.target_count = target_count;
    record.chosen_targets = stack_obj.targets;
    record.stack_size_before = ctx.stack_size_before;
    record.priority_before = ctx.priority_before;
    record.physical_card = false;
    record.ability_object = true;
    record.target_choice = !stack_obj.targets.empty();
    record.mana_cost_required = mana_cost_required;
    record.mana_cost_paid = mana_cost_paid;
    record.tap_cost_required = tap_cost_required;
    record.tap_cost_paid = tap_cost_paid;
    record.sacrifice_cost_required = sacrifice_cost_required;
    record.sacrifice_cost_paid = sacrifice_cost_paid;
    record.discard_cost_required = discard_cost_required;
    record.discard_cost_paid = discard_cost_paid;
    record.life_cost_required = life_cost_required;
    record.life_cost_paid = life_cost_paid;
    record.return_cost_required = return_cost_required;
    record.return_cost_paid = return_cost_paid;
    record.loyalty_cost_paid = loyalty_cost_paid;
    return record;
}


[[nodiscard]] ManaPool spent_delta_between(const ManaPool& before, const ManaPool& after) noexcept {
    ManaPool spent{};
    spent.white = before.white - after.white;
    spent.blue = before.blue - after.blue;
    spent.black = before.black - after.black;
    spent.red = before.red - after.red;
    spent.green = before.green - after.green;
    spent.colorless = before.colorless - after.colorless;
    return spent;
}

void record_mana_change(GameState& game, ManaChangeRecord record, std::string log_kind, std::string detail) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.mana_change_records.size() + 1U);
    const PlayerId mana_player = record.player;
    const ObjectId source_object = record.source;
    game.mana_change_records.push_back(std::move(record));
    record_event_with_links(game,
                            std::move(log_kind),
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::ManaChange,
                                .object = source_object,
                                .player = mana_player,
                                .mana_change_record_index = record_index
                            });
}

void add_mana_pool_recorded(GameState& game,
                            PlayerId player_id,
                            const ManaPool& produced,
                            ObjectId source = {},
                            u32 mana_ability_index = 0U) {
    if (produced.empty()) {
        return;
    }
    auto& p = player(game, player_id);
    const ManaPool before = p.mana_pool;
    add_mana_pool_to_pool(p.mana_pool, produced);
    const ManaPool after = p.mana_pool;
    ManaChangeRecord record{};
    record.player = player_id;
    record.kind = ManaChangeKind::Produced;
    record.pool_before = before;
    record.pool_after = after;
    record.added = produced;
    record.source = source;
    record.mana_ability_index = mana_ability_index;
    if (valid_object_index(game, source)) {
        record.source_zone_change_index = object(game, source).zone_change_index;
    }
    std::string detail = p.name + " added " + mana_pool_summary(produced) + " pool=" + mana_pool_summary(after);
    if (source.valid() && valid_object_index(game, source)) {
        detail += " source=";
        detail += object_label(game, source);
        if (mana_ability_index != 0U) {
            detail += " ability#" + std::to_string(mana_ability_index);
        }
    }
    record_mana_change(game, std::move(record), "add_mana", std::move(detail));
}

bool pay_mana_cost_recorded(GameState& game,
                            PlayerId player_id,
                            const ManaCost& cost,
                            bool auto_payment,
                            u32 auto_payment_mana_ability_count = 0U,
                            u32 auto_payment_locked_tap_source_count = 0U,
                            u64 auto_payment_plan_hash = 0U,
                            u32 auto_payment_plan_record_index = 0U) {
    auto& p = player(game, player_id);
    const ManaPool before = p.mana_pool;
    ManaPool copy = before;
    if (!spend_mana_from_copy(copy, cost)) {
        record_event(game,
                     auto_payment ? "pay_mana_auto_failed" : "pay_mana_failed",
                     p.name + " pool=" + mana_pool_summary(p.mana_pool));
        return false;
    }
    p.mana_pool = copy;
    const ManaPool after = p.mana_pool;
    const ManaPool spent = spent_delta_between(before, after);
    if (spent.empty() && cost.free()) {
        record_event(game, "pay_mana", p.name + " pool=" + mana_pool_summary(p.mana_pool));
        return true;
    }
    ManaChangeRecord record{};
    record.player = player_id;
    record.kind = ManaChangeKind::Paid;
    record.pool_before = before;
    record.pool_after = after;
    record.spent = spent;
    record.cost = cost;
    record.auto_payment = auto_payment;
    if (auto_payment) {
        record.auto_payment_mana_ability_count = auto_payment_mana_ability_count;
        record.auto_payment_locked_tap_source_count = auto_payment_locked_tap_source_count;
        record.auto_payment_plan_hash = auto_payment_plan_hash;
        record.auto_payment_plan_record_index = auto_payment_plan_record_index;
    }
    const u32 paid_record_index = static_cast<u32>(game.mana_change_records.size() + 1U);
    record_mana_change(game,
                       std::move(record),
                       "pay_mana",
                       p.name + " paid cost=" + mana_cost_summary(cost) + " spent=" + mana_pool_summary(spent) + " pool=" + mana_pool_summary(after));
    if (auto_payment_plan_record_index != 0U && auto_payment_plan_record_index <= game.mana_payment_plan_records.size()) {
        game.mana_payment_plan_records[auto_payment_plan_record_index - 1U].paid_mana_change_record_index = paid_record_index;
    }
    return true;
}

[[nodiscard]] u64 find_tap_event_sequence_since(const GameState& game, std::size_t first_event_record_index, u64 before_sequence) noexcept {
    for (std::size_t i = first_event_record_index; i < game.event_records.size(); ++i) {
        const auto& event_record = game.event_records[i];
        if (event_record.sequence > before_sequence && event_record.kind == EventRecordKind::Log && event_record.log_kind == "tap") {
            return event_record.sequence;
        }
    }
    return 0U;
}

bool pay_mana_cost_with_mana_abilities_excluding_tap_sources(GameState& game,
                                                            PlayerId player_id,
                                                            const ManaCost& cost,
                                                            const std::vector<ObjectId>& locked_tap_sources) {
    if (cost.free()) {
        return true;
    }
    std::vector<ManaAbilityCandidate> plan;
    if (!select_mana_ability_pay_plan_excluding_tap_sources(game, player_id, cost, locked_tap_sources, plan)) {
        record_event(game, "pay_mana_auto_failed", player(game, player_id).name + " pool=" + mana_pool_summary(player(game, player_id).mana_pool));
        return false;
    }
    const u64 plan_hash = mana_payment_plan_hash(game, player_id, cost, plan, locked_tap_sources);
    const u32 plan_record_index = record_mana_payment_plan(game, player_id, cost, plan, locked_tap_sources, plan_hash);
    for (std::size_t step_index = 0; step_index < plan.size(); ++step_index) {
        const auto& step = plan[step_index];
        const auto mana_change_count_before = game.mana_change_records.size();
        const auto event_record_count_before = game.event_records.size();
        const u64 event_sequence_before_step = game.next_event_sequence - 1U;
        if (!activate_mana_ability(game, player_id, step.object_id, step.ability_index)) {
            record_event(game, "pay_mana_auto_failed", "selected mana ability became illegal during payment");
            return false;
        }
        const auto mana_change_count_after = game.mana_change_records.size();
        if (mana_change_count_after <= mana_change_count_before) {
            record_event(game, "pay_mana_auto_failed", "selected mana ability produced no typed mana-change witness");
            return false;
        }
        const u32 produced_record_index = static_cast<u32>(mana_change_count_after);
        auto& plan_record = game.mana_payment_plan_records[plan_record_index - 1U];
        if (step_index >= plan_record.mana_ability_steps.size()) {
            record_event(game, "pay_mana_auto_failed", "typed mana-payment plan lost a step before execution witness linking");
            return false;
        }
        auto& plan_step_record = plan_record.mana_ability_steps[step_index];
        plan_step_record.produced_mana_change_record_index = produced_record_index;
        if (step.tap_cost) {
            plan_step_record.tap_event_sequence = find_tap_event_sequence_since(game, event_record_count_before, event_sequence_before_step);
            if (plan_step_record.tap_event_sequence == 0U) {
                record_event(game, "pay_mana_auto_failed", "selected tap-cost mana ability did not leave a tap event witness");
                return false;
            }
        }
        auto& produced_record = game.mana_change_records[produced_record_index - 1U];
        produced_record.auto_payment_producer_plan_record_index = plan_record_index;
        produced_record.auto_payment_producer_plan_step_index = static_cast<u32>(step_index + 1U);
    }
    auto& plan_record = game.mana_payment_plan_records[plan_record_index - 1U];
    plan_record.pool_before_payment = player(game, player_id).mana_pool;
    return pay_mana_cost_recorded(game,
                                  player_id,
                                  cost,
                                  true,
                                  static_cast<u32>(plan.size()),
                                  static_cast<u32>(locked_tap_sources.size()),
                                  plan_hash,
                                  plan_record_index);
}

template <typename Mutator>
bool commit_paid_action_body_transaction(GameState& game, PaidActionTransactionContext context, Mutator&& mutator) {
    const u64 physical_state_hash_before = canonical_state_hash(game);
    const u64 next_event_sequence_before = game.next_event_sequence;
    GameState staged_game = game;
    try {
        if (!std::forward<Mutator>(mutator)(staged_game, physical_state_hash_before)) {
            record_paid_action_transaction_rollback(game, context, staged_game, physical_state_hash_before, next_event_sequence_before);
            return false;
        }
    } catch (const std::exception&) {
        record_paid_action_transaction_rollback(game, context, staged_game, physical_state_hash_before, next_event_sequence_before);
        return false;
    }
    game = std::move(staged_game);
    return true;
}

struct PaidActionPhaseSnapshot {
    std::size_t event_count_before = 0;
    std::size_t mana_payment_plan_count_before = 0;
    std::size_t mana_change_count_before = 0;
    std::size_t tap_cost_payment_count_before = 0;
    std::size_t sacrifice_cost_payment_count_before = 0;
    std::size_t discard_cost_payment_count_before = 0;
    std::size_t life_cost_payment_count_before = 0;
    std::size_t return_cost_payment_count_before = 0;
    std::size_t loyalty_cost_payment_count_before = 0;
    std::size_t life_change_count_before = 0;
    std::size_t discard_record_count_before = 0;
    std::size_t counter_change_count_before = 0;
    std::size_t zone_change_count_before = 0;
    u64 stack_object_entered_sequence = 0;
    u64 choices_locked_sequence = 0;
};

[[nodiscard]] u64 latest_event_sequence(const GameState& game) noexcept {
    return game.events.empty() ? 0U : game.events.back().sequence;
}

[[nodiscard]] bool stack_contains_object(const GameState& game, ObjectId object_id) noexcept {
    return std::find(game.stack.begin(), game.stack.end(), object_id) != game.stack.end();
}

[[nodiscard]] u64 stack_enter_sequence_for_context(const GameState& game, const StackPlacementContext& ctx) noexcept {
    if (ctx.stack_enter_zone_change_record_index != 0U &&
        ctx.stack_enter_zone_change_record_index <= game.zone_change_records.size()) {
        return game.zone_change_records[ctx.stack_enter_zone_change_record_index - 1U].sequence;
    }
    return latest_event_sequence(game);
}

[[nodiscard]] u64 first_event_sequence_at_or_after(const GameState& game,
                                                   std::size_t first_event_index,
                                                   std::string_view kind) noexcept {
    for (std::size_t i = first_event_index; i < game.events.size(); ++i) {
        if (game.events[i].kind == kind) {
            return game.events[i].sequence;
        }
    }
    return 0U;
}

[[nodiscard]] bool zone_change_looks_like_sacrifice_cost(const ZoneChangeRecord& record) noexcept {
    return record.from_zone == Zone::Battlefield && record.requested_zone == Zone::Graveyard &&
        !record.was_ability_object;
}

[[nodiscard]] bool zone_change_looks_like_discard_cost(const ZoneChangeRecord& record) noexcept {
    return record.from_zone == Zone::Hand && record.requested_zone == Zone::Graveyard &&
        !record.was_ability_object;
}

[[nodiscard]] bool event_record_is_paid_choice_lock(const EventRecord& record) noexcept {
    return record.kind == EventRecordKind::Log &&
        (record.log_kind == "choose_mode" || record.log_kind == "choose_target");
}

void seal_choice_lock_witness(StackPlacementRecord& record, const GameState& game) noexcept {
    if (record.stack_object_entered_sequence == 0U || record.choices_locked_sequence == 0U) {
        return;
    }
    for (const auto& event_record : game.event_records) {
        if (event_record.sequence <= record.stack_object_entered_sequence ||
            event_record.sequence > record.choices_locked_sequence ||
            !event_record_is_paid_choice_lock(event_record)) {
            continue;
        }
        if (record.first_choice_event_sequence == 0U) {
            record.first_choice_event_sequence = event_record.sequence;
        }
        record.last_choice_event_sequence = event_record.sequence;
        ++record.choice_event_count;
        if (event_record.log_kind == "choose_mode") {
            record.mode_choice_event_sequence = event_record.sequence;
        } else if (event_record.log_kind == "choose_target") {
            record.target_choice_event_sequence = event_record.sequence;
        }
    }
}

void seal_sacrifice_cost_witness(StackPlacementRecord& record,
                                 const GameState& game,
                                 const PaidActionPhaseSnapshot& snapshot) noexcept {
    if (!record.sacrifice_cost_paid) {
        return;
    }

    for (std::size_t i = snapshot.zone_change_count_before; i < game.zone_change_records.size(); ++i) {
        const auto& zone_record = game.zone_change_records[i];
        if (!zone_change_looks_like_sacrifice_cost(zone_record)) {
            continue;
        }
        if (record.first_sacrifice_cost_zone_change_record_index == 0U) {
            record.first_sacrifice_cost_zone_change_record_index = static_cast<u32>(i + 1U);
        }
        ++record.sacrifice_cost_zone_change_record_count;
    }

    for (std::size_t i = snapshot.event_count_before; i < game.event_records.size(); ++i) {
        const auto& event_record = game.event_records[i];
        if (event_record.kind == EventRecordKind::Log && event_record.log_kind == "pay_sacrifice_cost") {
            record.sacrifice_cost_event_sequence = event_record.sequence;
            break;
        }
    }
}

void seal_discard_cost_witness(StackPlacementRecord& record,
                               const GameState& game,
                               const PaidActionPhaseSnapshot& snapshot) noexcept {
    if (!record.discard_cost_paid) {
        return;
    }

    for (std::size_t i = snapshot.discard_record_count_before; i < game.discard_records.size(); ++i) {
        const auto& discard_record = game.discard_records[i];
        if (discard_record.kind != DiscardRecordKind::CostPayment) {
            continue;
        }
        if (record.first_discard_cost_record_index == 0U) {
            record.first_discard_cost_record_index = static_cast<u32>(i + 1U);
        }
        ++record.discard_cost_record_count;
    }

    for (std::size_t i = snapshot.zone_change_count_before; i < game.zone_change_records.size(); ++i) {
        const auto& zone_record = game.zone_change_records[i];
        if (!zone_change_looks_like_discard_cost(zone_record)) {
            continue;
        }
        if (record.first_discard_cost_zone_change_record_index == 0U) {
            record.first_discard_cost_zone_change_record_index = static_cast<u32>(i + 1U);
        }
        ++record.discard_cost_zone_change_record_count;
    }

    for (std::size_t i = snapshot.event_count_before; i < game.event_records.size(); ++i) {
        const auto& event_record = game.event_records[i];
        if (event_record.kind == EventRecordKind::Log && event_record.log_kind == "pay_discard_cost") {
            record.discard_cost_event_sequence = event_record.sequence;
            break;
        }
    }
}

[[nodiscard]] PaidActionPhaseSnapshot capture_paid_action_phase_snapshot(const GameState& game,
                                                                         u64 stack_object_entered_sequence = 0U,
                                                                         u64 choices_locked_sequence_override = 0U) noexcept {
    const u64 latest_sequence = latest_event_sequence(game);
    const u64 choices_locked_sequence = choices_locked_sequence_override == 0U ? latest_sequence : choices_locked_sequence_override;
    return PaidActionPhaseSnapshot{
        .event_count_before = game.events.size(),
        .mana_payment_plan_count_before = game.mana_payment_plan_records.size(),
        .mana_change_count_before = game.mana_change_records.size(),
        .tap_cost_payment_count_before = game.tap_cost_payment_records.size(),
        .sacrifice_cost_payment_count_before = game.sacrifice_cost_payment_records.size(),
        .discard_cost_payment_count_before = game.discard_cost_payment_records.size(),
        .life_cost_payment_count_before = game.life_cost_payment_records.size(),
        .return_cost_payment_count_before = game.return_cost_payment_records.size(),
        .loyalty_cost_payment_count_before = game.loyalty_cost_payment_records.size(),
        .life_change_count_before = game.life_change_records.size(),
        .discard_record_count_before = game.discard_records.size(),
        .counter_change_count_before = game.counter_change_records.size(),
        .zone_change_count_before = game.zone_change_records.size(),
        .stack_object_entered_sequence = stack_object_entered_sequence == 0U ? choices_locked_sequence : stack_object_entered_sequence,
        .choices_locked_sequence = choices_locked_sequence
    };
}

void seal_paid_action_phase(StackPlacementRecord& record,
                            const GameState& game,
                            const PaidActionPhaseSnapshot& snapshot) {
    record.paid_action_phase_recorded = true;
    record.stack_object_entered_sequence = snapshot.stack_object_entered_sequence;
    record.choices_locked_sequence = snapshot.choices_locked_sequence;

    if (game.events.size() > snapshot.event_count_before) {
        record.first_paid_action_event_sequence = game.events[snapshot.event_count_before].sequence;
        record.last_paid_action_event_sequence = game.events.back().sequence;
    }

    if (game.mana_payment_plan_records.size() > snapshot.mana_payment_plan_count_before) {
        record.first_mana_payment_plan_record_index = static_cast<u32>(snapshot.mana_payment_plan_count_before + 1U);
        record.mana_payment_plan_record_count = static_cast<u32>(game.mana_payment_plan_records.size() - snapshot.mana_payment_plan_count_before);
    }
    if (game.mana_change_records.size() > snapshot.mana_change_count_before) {
        record.first_mana_change_record_index = static_cast<u32>(snapshot.mana_change_count_before + 1U);
        record.mana_change_record_count = static_cast<u32>(game.mana_change_records.size() - snapshot.mana_change_count_before);
    }
    if (game.tap_cost_payment_records.size() > snapshot.tap_cost_payment_count_before) {
        record.first_tap_cost_payment_record_index = static_cast<u32>(snapshot.tap_cost_payment_count_before + 1U);
        record.tap_cost_payment_record_count = static_cast<u32>(game.tap_cost_payment_records.size() - snapshot.tap_cost_payment_count_before);
        if (record.tap_cost_payment_record_count == 1U) {
            record.tap_cost_payment_hash = game.tap_cost_payment_records[record.first_tap_cost_payment_record_index - 1U].payment_hash;
        }
    }
    if (game.sacrifice_cost_payment_records.size() > snapshot.sacrifice_cost_payment_count_before) {
        record.first_sacrifice_cost_payment_record_index = static_cast<u32>(snapshot.sacrifice_cost_payment_count_before + 1U);
        record.sacrifice_cost_payment_record_count = static_cast<u32>(game.sacrifice_cost_payment_records.size() - snapshot.sacrifice_cost_payment_count_before);
        if (record.sacrifice_cost_payment_record_count == 1U) {
            record.sacrifice_cost_payment_hash = game.sacrifice_cost_payment_records[record.first_sacrifice_cost_payment_record_index - 1U].payment_hash;
        }
    }
    if (game.discard_cost_payment_records.size() > snapshot.discard_cost_payment_count_before) {
        record.first_discard_cost_payment_record_index = static_cast<u32>(snapshot.discard_cost_payment_count_before + 1U);
        record.discard_cost_payment_record_count = static_cast<u32>(game.discard_cost_payment_records.size() - snapshot.discard_cost_payment_count_before);
        if (record.discard_cost_payment_record_count == 1U) {
            record.discard_cost_payment_hash = game.discard_cost_payment_records[record.first_discard_cost_payment_record_index - 1U].payment_hash;
        }
    }
    if (game.life_cost_payment_records.size() > snapshot.life_cost_payment_count_before) {
        record.first_life_cost_payment_record_index = static_cast<u32>(snapshot.life_cost_payment_count_before + 1U);
        record.life_cost_payment_record_count = static_cast<u32>(game.life_cost_payment_records.size() - snapshot.life_cost_payment_count_before);
        if (record.life_cost_payment_record_count == 1U) {
            record.life_cost_payment_hash = game.life_cost_payment_records[record.first_life_cost_payment_record_index - 1U].payment_hash;
        }
    }
    if (game.return_cost_payment_records.size() > snapshot.return_cost_payment_count_before) {
        record.first_return_cost_payment_record_index = static_cast<u32>(snapshot.return_cost_payment_count_before + 1U);
        record.return_cost_payment_record_count = static_cast<u32>(game.return_cost_payment_records.size() - snapshot.return_cost_payment_count_before);
        if (record.return_cost_payment_record_count == 1U) {
            record.return_cost_payment_hash = game.return_cost_payment_records[record.first_return_cost_payment_record_index - 1U].payment_hash;
        }
    }
    if (game.loyalty_cost_payment_records.size() > snapshot.loyalty_cost_payment_count_before) {
        record.first_loyalty_cost_payment_record_index = static_cast<u32>(snapshot.loyalty_cost_payment_count_before + 1U);
        record.loyalty_cost_payment_record_count = static_cast<u32>(game.loyalty_cost_payment_records.size() - snapshot.loyalty_cost_payment_count_before);
        if (record.loyalty_cost_payment_record_count == 1U) {
            record.loyalty_cost_payment_hash = game.loyalty_cost_payment_records[record.first_loyalty_cost_payment_record_index - 1U].payment_hash;
        }
    }
    if (game.life_change_records.size() > snapshot.life_change_count_before) {
        record.first_life_cost_life_change_record_index = static_cast<u32>(snapshot.life_change_count_before + 1U);
        record.life_cost_life_change_record_count = static_cast<u32>(game.life_change_records.size() - snapshot.life_change_count_before);
    }
    if (game.counter_change_records.size() > snapshot.counter_change_count_before) {
        record.first_paid_action_counter_change_record_index = static_cast<u32>(snapshot.counter_change_count_before + 1U);
        record.paid_action_counter_change_record_count = static_cast<u32>(game.counter_change_records.size() - snapshot.counter_change_count_before);
    }
    if (game.zone_change_records.size() > snapshot.zone_change_count_before) {
        record.first_paid_action_zone_change_record_index = static_cast<u32>(snapshot.zone_change_count_before + 1U);
        record.paid_action_zone_change_record_count = static_cast<u32>(game.zone_change_records.size() - snapshot.zone_change_count_before);
    }
    seal_choice_lock_witness(record, game);
    seal_sacrifice_cost_witness(record, game, snapshot);
    seal_discard_cost_witness(record, game, snapshot);
    if (record.tap_cost_paid && record.tap_cost_payment_record_count == 1U &&
        record.first_tap_cost_payment_record_index != 0U &&
        record.first_tap_cost_payment_record_index <= game.tap_cost_payment_records.size()) {
        record.tap_cost_event_sequence = game.tap_cost_payment_records[record.first_tap_cost_payment_record_index - 1U].tap_event_sequence;
    }
    if (record.tap_cost_paid && record.tap_cost_event_sequence == 0U) {
        for (std::size_t i = snapshot.event_count_before; i < game.event_records.size(); ++i) {
            const auto& event_record = game.event_records[i];
            if (event_record.kind == EventRecordKind::Log && event_record.log_kind == "tap" &&
                event_record.object == record.source_object && event_record.player == record.controller &&
                event_record.object_zone_change_index == record.source_zone_change_index_before) {
                record.tap_cost_event_sequence = event_record.sequence;
                break;
            }
        }
    }
    if (record.life_cost_paid && record.life_cost_payment_record_count == 1U &&
        record.first_life_cost_payment_record_index != 0U &&
        record.first_life_cost_payment_record_index <= game.life_cost_payment_records.size()) {
        record.life_cost_event_sequence = game.life_cost_payment_records[record.first_life_cost_payment_record_index - 1U].sequence;
    }
    if (record.life_cost_paid && record.life_cost_event_sequence == 0U) {
        for (std::size_t i = snapshot.event_count_before; i < game.event_records.size(); ++i) {
            const auto& event_record = game.event_records[i];
            if (event_record.kind == EventRecordKind::Log && event_record.log_kind == "pay_life_cost" &&
                event_record.player == record.controller) {
                record.life_cost_event_sequence = event_record.sequence;
                break;
            }
        }
    }
    if (record.return_cost_paid && record.return_cost_payment_record_count == 1U &&
        record.first_return_cost_payment_record_index != 0U &&
        record.first_return_cost_payment_record_index <= game.return_cost_payment_records.size()) {
        const auto& payment = game.return_cost_payment_records[record.first_return_cost_payment_record_index - 1U];
        record.return_cost_event_sequence = payment.sequence;
        record.first_return_cost_zone_change_record_index = payment.first_zone_change_record_index;
        record.return_cost_zone_change_record_count = payment.zone_change_record_count;
    }
    if (record.return_cost_paid && record.return_cost_event_sequence == 0U) {
        for (std::size_t i = snapshot.event_count_before; i < game.event_records.size(); ++i) {
            const auto& event_record = game.event_records[i];
            if (event_record.kind == EventRecordKind::Log && event_record.log_kind == "pay_return_cost" &&
                event_record.player == record.controller) {
                record.return_cost_event_sequence = event_record.sequence;
                break;
            }
        }
    }
    if (record.loyalty_cost_paid && record.loyalty_cost_payment_record_count == 1U &&
        record.first_loyalty_cost_payment_record_index != 0U &&
        record.first_loyalty_cost_payment_record_index <= game.loyalty_cost_payment_records.size()) {
        record.loyalty_cost_event_sequence = game.loyalty_cost_payment_records[record.first_loyalty_cost_payment_record_index - 1U].sequence;
    }
    if (record.loyalty_cost_paid && record.loyalty_cost_event_sequence == 0U) {
        for (std::size_t i = snapshot.event_count_before; i < game.event_records.size(); ++i) {
            const auto& event_record = game.event_records[i];
            if (event_record.kind == EventRecordKind::CounterChange && event_record.log_kind == "loyalty_cost_paid" &&
                event_record.object == record.source_object && event_record.player == record.controller) {
                record.loyalty_cost_event_sequence = event_record.sequence;
                break;
            }
        }
    }

    record.stack_object_on_stack_before_costs = record.stack_object_entered_sequence != 0U &&
        valid_object_index(game, record.stack_object) && object(game, record.stack_object).zone == Zone::Stack &&
        stack_contains_object(game, record.stack_object);
    record.choices_locked_before_costs = record.choices_locked_sequence != 0U &&
        (record.first_paid_action_event_sequence == 0U || record.choices_locked_sequence < record.first_paid_action_event_sequence);
    record.paid_action_events_before_stack_placement = record.last_paid_action_event_sequence == 0U ||
        record.last_paid_action_event_sequence < game.next_event_sequence;
}

void clear_mana_pool_recorded(GameState& game, PlayerId player_id) {
    auto& p = player(game, player_id);
    if (p.mana_pool.empty()) {
        return;
    }
    const ManaPool before = p.mana_pool;
    p.mana_pool = ManaPool{};
    ManaChangeRecord record{};
    record.player = player_id;
    record.kind = ManaChangeKind::Emptied;
    record.pool_before = before;
    record.pool_after = p.mana_pool;
    record.spent = before;
    record_mana_change(game,
                       std::move(record),
                       "clear_mana_pool",
                       p.name + " cleared " + mana_pool_summary(before));
}

void record_life_change(GameState& game, PlayerId player_id, LifeChangeKind kind, std::int32_t amount) {
    auto& p = player(game, player_id);
    const std::int32_t before = p.life;
    switch (kind) {
        case LifeChangeKind::Loss:
            p.life -= amount;
            break;
        case LifeChangeKind::Gain:
            p.life += amount;
            break;
        case LifeChangeKind::Count:
            throw std::logic_error("invalid life-change kind");
    }
    const std::int32_t after = p.life;
    const u32 record_index = static_cast<u32>(game.life_change_records.size() + 1U);
    game.life_change_records.push_back(LifeChangeRecord{
        .sequence = game.next_event_sequence,
        .player = player_id,
        .kind = kind,
        .amount = amount,
        .life_before = before,
        .life_after = after
    });
    const bool loss = kind == LifeChangeKind::Loss;
    record_event_with_links(game,
                            loss ? "lose_life" : "gain_life",
                            p.name + (loss ? " lost " : " gained ") + std::to_string(amount),
                            EventRecordLinks{
                                .kind = EventRecordKind::LifeChange,
                                .player = player_id,
                                .life_change_record_index = record_index
                            });
}

void record_counter_change(GameState& game, CounterChangeRecord record, std::string log_kind, std::string detail) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.counter_change_records.size() + 1U);
    const ObjectId changed_object = record.object;
    const PlayerId changed_player = record.player;
    game.counter_change_records.push_back(std::move(record));
    record_event_with_links(game,
                            std::move(log_kind),
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::CounterChange,
                                .object = changed_object,
                                .player = changed_player,
                                .counter_change_record_index = record_index
                            });
}

void record_damage_prevention_change(GameState& game, DamagePreventionRecord record, std::string log_kind, std::string detail) {
    record.sequence = game.next_event_sequence;
    const u32 record_index = static_cast<u32>(game.damage_prevention_records.size() + 1U);
    const TargetRef target = record.target;
    const ObjectId event_object = target.kind == TargetKind::Object ? target.object : ObjectId{};
    const PlayerId event_player = target.kind == TargetKind::Player ? target.player : PlayerId{};
    game.damage_prevention_records.push_back(std::move(record));
    record_event_with_links(game,
                            std::move(log_kind),
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::DamagePrevention,
                                .object = event_object,
                                .player = event_player,
                                .target = target,
                                .damage_prevention_record_index = record_index
                            });
}

void link_damage_prevention_record_range_to_damage(GameState& game, u32 first_record_index, u32 record_count, u32 damage_record_index) {
    if (first_record_index == 0U || record_count == 0U) {
        return;
    }
    if (damage_record_index == 0U || damage_record_index > game.damage_records.size()) {
        return;
    }
    const u32 last_record_index = first_record_index + record_count - 1U;
    if (last_record_index > game.damage_prevention_records.size()) {
        return;
    }
    for (u32 index = first_record_index; index <= last_record_index; ++index) {
        auto& record = game.damage_prevention_records[index - 1U];
        if (record.kind == DamagePreventionRecordKind::ShieldConsumed ||
            record.kind == DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage) {
            record.damage_record_index = damage_record_index;
        }
    }
}

void link_life_change_record_range_to_damage(GameState& game,
                                             u32 first_record_index,
                                             u32 record_count,
                                             u32 damage_record_index,
                                             ObjectId damage_source,
                                             u64 damage_source_zone_change_index,
                                             TargetRef damage_target,
                                             bool source_had_lifelink) {
    if (first_record_index == 0U || record_count == 0U) {
        return;
    }
    if (damage_record_index == 0U || damage_record_index > game.damage_records.size()) {
        return;
    }
    const u32 last_record_index = first_record_index + record_count - 1U;
    if (last_record_index > game.life_change_records.size()) {
        return;
    }
    for (u32 index = first_record_index; index <= last_record_index; ++index) {
        auto& record = game.life_change_records[index - 1U];
        record.damage_record_index = damage_record_index;
        record.damage_source = damage_source;
        record.damage_source_zone_change_index = damage_source_zone_change_index;
        record.damage_target = damage_target;
        record.damage_result = true;
        record.lifelink_result = source_had_lifelink && record.kind == LifeChangeKind::Gain;
    }
}

void record_object_counter_change(GameState& game,
                                  ObjectId object_id,
                                  CounterKind counter_kind,
                                  CounterChangeKind change_kind,
                                  u32 amount,
                                  u32 before,
                                  u32 after,
                                  std::string log_kind,
                                  std::string detail,
                                  ObjectId source,
                                  bool damage_result,
                                  u32 zone_change_record_index,
                                  bool cost_payment,
                                  bool zone_change_cleanup) {
    CounterChangeRecord record{};
    record.kind = change_kind;
    record.counter_kind = counter_kind;
    record.object = object_id;
    if (valid_object_index(game, object_id)) {
        const auto& obj = object(game, object_id);
        record.player = obj.controller;
        record.object_zone_change_index = obj.zone_change_index;
    }
    record.amount = amount;
    record.count_before = before;
    record.count_after = after;
    record.source = source;
    if (valid_object_index(game, source)) {
        record.source_zone_change_index = object(game, source).zone_change_index;
    }
    record.zone_change_record_index = zone_change_record_index;
    record.damage_result = damage_result;
    record.cost_payment = cost_payment;
    record.zone_change_cleanup = zone_change_cleanup;
    record_counter_change(game, std::move(record), std::move(log_kind), std::move(detail));
}

void record_player_counter_change(GameState& game,
                                  PlayerId player_id,
                                  CounterKind counter_kind,
                                  CounterChangeKind change_kind,
                                  u32 amount,
                                  u32 before,
                                  u32 after,
                                  std::string log_kind,
                                  std::string detail) {
    CounterChangeRecord record{};
    record.kind = change_kind;
    record.counter_kind = counter_kind;
    record.player = player_id;
    record.amount = amount;
    record.count_before = before;
    record.count_after = after;
    record_counter_change(game, std::move(record), std::move(log_kind), std::move(detail));
}

} // namespace

std::uint64_t target_choice_set_hash(const std::vector<TargetRef>& targets) noexcept {
    return target_choice_set_hash_impl(targets);
}

std::uint64_t mode_choice_contract_hash(const SpellModeDefinition& mode) noexcept {
    return mode_choice_contract_hash_impl(mode);
}

std::uint64_t mana_payment_plan_record_identity_hash(const ManaPaymentPlanRecord& record) noexcept {
    return mana_payment_plan_hash_from_records(record.player, record.cost, record.pool_before_plan, record.locked_tap_sources, record.mana_ability_steps);
}

std::uint64_t sacrifice_cost_payment_record_hash(const SacrificeCostPaymentRecord& record) noexcept {
    return sacrifice_cost_payment_record_identity_hash(record);
}

std::size_t discard_cost_payment_record_count(const GameState& game) noexcept {
    return game.discard_cost_payment_records.size();
}

const DiscardCostPaymentRecord* latest_discard_cost_payment_record(const GameState& game) noexcept {
    if (game.discard_cost_payment_records.empty()) {
        return nullptr;
    }
    return &game.discard_cost_payment_records.back();
}

std::uint64_t discard_cost_payment_record_hash(const DiscardCostPaymentRecord& record) noexcept {
    return discard_cost_payment_record_identity_hash(record);
}

std::size_t life_cost_payment_record_count(const GameState& game) noexcept {
    return game.life_cost_payment_records.size();
}

const LifeCostPaymentRecord* latest_life_cost_payment_record(const GameState& game) noexcept {
    if (game.life_cost_payment_records.empty()) {
        return nullptr;
    }
    return &game.life_cost_payment_records.back();
}

std::uint64_t life_cost_payment_record_hash(const LifeCostPaymentRecord& record) noexcept {
    return life_cost_payment_record_identity_hash(record);
}

std::size_t return_cost_payment_record_count(const GameState& game) noexcept {
    return game.return_cost_payment_records.size();
}

const ReturnCostPaymentRecord* latest_return_cost_payment_record(const GameState& game) noexcept {
    if (game.return_cost_payment_records.empty()) {
        return nullptr;
    }
    return &game.return_cost_payment_records.back();
}

std::uint64_t return_cost_payment_record_hash(const ReturnCostPaymentRecord& record) noexcept {
    return return_cost_payment_record_identity_hash(record);
}

std::size_t loyalty_cost_payment_record_count(const GameState& game) noexcept {
    return game.loyalty_cost_payment_records.size();
}

const LoyaltyCostPaymentRecord* latest_loyalty_cost_payment_record(const GameState& game) noexcept {
    if (game.loyalty_cost_payment_records.empty()) {
        return nullptr;
    }
    return &game.loyalty_cost_payment_records.back();
}

std::uint64_t loyalty_cost_payment_record_hash(const LoyaltyCostPaymentRecord& record) noexcept {
    return loyalty_cost_payment_record_identity_hash(record);
}

std::uint64_t paid_action_declaration_record_hash(const PaidActionDeclarationRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.PaidActionDeclarationRecord.v7");
    hash_paid_action_declaration_identity(h, record);
    return h.value();
}

std::uint64_t paid_action_transaction_record_hash(const PaidActionTransactionRecord& record) noexcept {
    StableHasher h;
    h.add_string("MTGSim.PaidActionTransactionRecord.v11");
    hash_paid_action_transaction_identity(h, record);
    return h.value();
}

namespace {

[[nodiscard]] std::string serialize_paid_action_mana_cost(const ManaCost& cost) {
    std::ostringstream out;
    out << cost.generic << ':' << cost.white << ':' << cost.blue << ':' << cost.black << ':'
        << cost.red << ':' << cost.green << ':' << cost.colorless;
    return out.str();
}

[[nodiscard]] std::string serialize_paid_action_snapshot_target(TargetRef target) {
    std::ostringstream out;
    out << to_string(target.kind) << ':'
        << target.player.value << ':'
        << target.object.value << ':'
        << target.object_zone_change_index;
    return out.str();
}

[[nodiscard]] std::string serialize_paid_action_snapshot_targets(const std::vector<TargetRef>& targets) {
    if (targets.empty()) {
        return "-";
    }
    std::ostringstream out;
    for (std::size_t i = 0; i < targets.size(); ++i) {
        if (i != 0U) {
            out << ',';
        }
        out << serialize_paid_action_snapshot_target(targets[i]);
    }
    return out.str();
}

void write_paid_action_declaration_snapshot_text(std::ostream& out,
                                                 std::string_view prefix,
                                                 const PaidActionDeclarationRecord& record) {
    out << ' ' << prefix << ".sequence=" << record.sequence
        << ' ' << prefix << ".schema=" << record.schema_version
        << ' ' << prefix << ".action=" << to_string(record.action_kind)
        << ' ' << prefix << ".player=" << record.player.value
        << ' ' << prefix << ".source=" << record.source_object.value
        << ' ' << prefix << ".stack_object=" << record.stack_object.value
        << ' ' << prefix << ".definition=" << record.definition_index
        << ' ' << prefix << ".source_zone_before=" << to_string(record.source_zone_before)
        << ' ' << prefix << ".source_zone_change_index_before=" << record.source_zone_change_index_before
        << ' ' << prefix << ".stack_zone_change_index=" << record.stack_zone_change_index
        << ' ' << prefix << ".stack_enter_record=" << record.stack_enter_zone_change_record_index
        << ' ' << prefix << ".stack_entered=" << record.stack_object_entered_sequence
        << ' ' << prefix << ".choices_locked=" << record.choices_locked_sequence
        << ' ' << prefix << ".ability=" << record.ability_index
        << ' ' << prefix << ".loyalty_delta=" << record.loyalty_cost_delta
        << ' ' << prefix << ".mode=" << record.declared_mode_index
        << ' ' << prefix << ".mode_hash=" << record.declared_mode_contract_hash
        << ' ' << prefix << ".target_mask=" << record.target_mask
        << ' ' << prefix << ".target_count=" << record.target_count
        << ' ' << prefix << ".targets=" << serialize_paid_action_snapshot_targets(record.declared_targets)
        << ' ' << prefix << ".target_hash=" << record.declared_target_set_hash
        << ' ' << prefix << ".mana_cost=" << serialize_paid_action_mana_cost(record.total_mana_cost)
        << ' ' << prefix << ".sacrifice_count=" << record.sacrifice_cost.count
        << ' ' << prefix << ".sacrifice_type_mask=" << record.sacrifice_cost.required_type_mask
        << ' ' << prefix << ".discard_count=" << record.discard_cost.count
        << ' ' << prefix << ".life_amount=" << record.life_cost.amount
        << ' ' << prefix << ".return_count=" << record.return_cost.count
        << ' ' << prefix << ".return_type_mask=" << record.return_cost.required_type_mask
        << ' ' << prefix << ".return_require_tapped=" << (record.return_cost.require_tapped ? 1 : 0)
        << ' ' << prefix << ".total_cost_locked=" << (record.total_cost_locked ? 1 : 0)
        << ' ' << prefix << ".mana_cost_required=" << (record.mana_cost_required ? 1 : 0)
        << ' ' << prefix << ".tap_cost_required=" << (record.tap_cost_required ? 1 : 0)
        << ' ' << prefix << ".sacrifice_cost_required=" << (record.sacrifice_cost_required ? 1 : 0)
        << ' ' << prefix << ".discard_cost_required=" << (record.discard_cost_required ? 1 : 0)
        << ' ' << prefix << ".life_cost_required=" << (record.life_cost_required ? 1 : 0)
        << ' ' << prefix << ".return_cost_required=" << (record.return_cost_required ? 1 : 0)
        << ' ' << prefix << ".loyalty_cost_required=" << (record.loyalty_cost_required ? 1 : 0)
        << ' ' << prefix << ".modal_choice_declared=" << (record.modal_choice_declared ? 1 : 0)
        << ' ' << prefix << ".target_choice_declared=" << (record.target_choice_declared ? 1 : 0)
        << ' ' << prefix << ".payment_attempted=" << (record.payment_attempted ? 1 : 0)
        << ' ' << prefix << ".first_payment=" << record.first_payment_event_sequence
        << ' ' << prefix << ".last_payment=" << record.last_payment_event_sequence
        << ' ' << prefix << ".sacrifice_payment_first=" << record.first_sacrifice_cost_payment_record_index
        << ' ' << prefix << ".sacrifice_payment_count=" << record.sacrifice_cost_payment_record_count
        << ' ' << prefix << ".sacrifice_payment_hash=" << record.sacrifice_cost_payment_hash
        << ' ' << prefix << ".discard_payment_first=" << record.first_discard_cost_payment_record_index
        << ' ' << prefix << ".discard_payment_count=" << record.discard_cost_payment_record_count
        << ' ' << prefix << ".discard_payment_hash=" << record.discard_cost_payment_hash
        << ' ' << prefix << ".tap_payment_first=" << record.first_tap_cost_payment_record_index
        << ' ' << prefix << ".tap_payment_count=" << record.tap_cost_payment_record_count
        << ' ' << prefix << ".tap_payment_hash=" << record.tap_cost_payment_hash
        << ' ' << prefix << ".life_payment_first=" << record.first_life_cost_payment_record_index
        << ' ' << prefix << ".life_payment_count=" << record.life_cost_payment_record_count
        << ' ' << prefix << ".life_payment_hash=" << record.life_cost_payment_hash
        << ' ' << prefix << ".return_payment_first=" << record.first_return_cost_payment_record_index
        << ' ' << prefix << ".return_payment_count=" << record.return_cost_payment_record_count
        << ' ' << prefix << ".return_payment_hash=" << record.return_cost_payment_hash
        << ' ' << prefix << ".loyalty_payment_first=" << record.first_loyalty_cost_payment_record_index
        << ' ' << prefix << ".loyalty_payment_count=" << record.loyalty_cost_payment_record_count
        << ' ' << prefix << ".loyalty_payment_hash=" << record.loyalty_cost_payment_hash
        << ' ' << prefix << ".placement_index=" << record.stack_placement_record_index
        << ' ' << prefix << ".declaration_hash=" << record.declaration_hash
        << ' ' << prefix << ".recomputed_hash=" << paid_action_declaration_record_hash(record);
}


void hash_paid_action_transaction_journal_payload_row(StableHasher& h,
                                                      u32 index,
                                                      const PaidActionTransactionRecord& record,
                                                      u64 exported_recomputed_transaction_hash,
                                                      u64 exported_committed_snapshot_recomputed_hash,
                                                      u64 exported_speculative_snapshot_recomputed_hash) noexcept {
    h.add_u64(index);
    hash_into(h, record);
    h.add_u64(exported_recomputed_transaction_hash);
    h.add_u64(exported_committed_snapshot_recomputed_hash);
    h.add_u64(exported_speculative_snapshot_recomputed_hash);
}

[[nodiscard]] u64 paid_action_transaction_journal_payload_hash_from_records(const std::vector<PaidActionTransactionRecord>& records) noexcept {
    StableHasher h;
    h.add_string("MTGSim.PaidActionTransactionJournalPayload.v1");
    h.add_u64(static_cast<u64>(records.size()));
    for (std::size_t i = 0; i < records.size(); ++i) {
        const auto& record = records[i];
        const u64 committed_snapshot_hash = record.committed_paid_action_declaration_snapshot_present
            ? paid_action_declaration_record_hash(record.committed_paid_action_declaration_snapshot)
            : 0U;
        const u64 speculative_snapshot_hash = record.speculative_paid_action_declaration_snapshot_present
            ? paid_action_declaration_record_hash(record.speculative_paid_action_declaration_snapshot)
            : 0U;
        hash_paid_action_transaction_journal_payload_row(h,
                                                         static_cast<u32>(i + 1U),
                                                         record,
                                                         paid_action_transaction_record_hash(record),
                                                         committed_snapshot_hash,
                                                         speculative_snapshot_hash);
    }
    return h.value();
}

[[nodiscard]] u64 paid_action_transaction_journal_payload_hash_from_parsed_records(const std::vector<PaidActionTransactionJournalRecord>& records) noexcept {
    StableHasher h;
    h.add_string("MTGSim.PaidActionTransactionJournalPayload.v1");
    h.add_u64(static_cast<u64>(records.size()));
    for (const auto& row : records) {
        hash_paid_action_transaction_journal_payload_row(h,
                                                         row.index,
                                                         row.transaction,
                                                         row.exported_recomputed_transaction_hash,
                                                         row.exported_committed_snapshot_recomputed_hash,
                                                         row.exported_speculative_snapshot_recomputed_hash);
    }
    return h.value();
}

} // namespace

std::string serialize_paid_action_transaction_journal(const GameState& game) {
    std::ostringstream out;
    const u64 first_transaction_sequence = game.paid_action_transaction_records.empty()
        ? 0U
        : game.paid_action_transaction_records.front().sequence;
    const u64 last_transaction_sequence = game.paid_action_transaction_records.empty()
        ? 0U
        : game.paid_action_transaction_records.back().sequence;
    out << "MTGSim.PaidActionTransactionJournal.v" << kPaidActionTransactionJournalSchemaVersion << "\n";
    out << "record_count=" << game.paid_action_transaction_records.size()
        << " declaration_record_count=" << game.paid_action_declaration_records.size()
        << " stack_placement_record_count=" << game.stack_placement_records.size()
        << " journal_hash=" << journal_hash(game)
        << " state_hash=" << canonical_state_hash(game)
        << " record_payload_hash=" << paid_action_transaction_journal_payload_hash_from_records(game.paid_action_transaction_records)
        << " first_transaction_sequence=" << first_transaction_sequence
        << " last_transaction_sequence=" << last_transaction_sequence
        << "\n";
    for (std::size_t i = 0; i < game.paid_action_transaction_records.size(); ++i) {
        const auto& record = game.paid_action_transaction_records[i];
        out << "record index=" << (i + 1U)
            << " sequence=" << record.sequence
            << " schema=" << record.schema_version
            << " outcome=" << to_string(record.outcome)
            << " action=" << to_string(record.action_kind)
            << " player=" << record.player.value
            << " source=" << record.source_object.value
            << " stack_object=" << record.stack_object.value
            << " stack_placement=" << record.stack_placement_record_index
            << " declaration_index=" << record.paid_action_declaration_record_index
            << " declaration_hash=" << record.paid_action_declaration_hash
            << " stack_entered=" << record.stack_object_entered_sequence
            << " choices_locked=" << record.choices_locked_sequence
            << " first_paid_event=" << record.first_paid_action_event_sequence
            << " last_paid_event=" << record.last_paid_action_event_sequence
            << " mana_plan_first=" << record.first_mana_payment_plan_record_index
            << " mana_plan_count=" << record.mana_payment_plan_record_count
            << " mana_change_first=" << record.first_mana_change_record_index
            << " mana_change_count=" << record.mana_change_record_count
            << " counter_change_first=" << record.first_paid_action_counter_change_record_index
            << " counter_change_count=" << record.paid_action_counter_change_record_count
            << " zone_change_first=" << record.first_paid_action_zone_change_record_index
            << " zone_change_count=" << record.paid_action_zone_change_record_count
            << " sacrifice_payment_first=" << record.first_sacrifice_cost_payment_record_index
            << " sacrifice_payment_count=" << record.sacrifice_cost_payment_record_count
            << " sacrifice_payment_hash=" << record.sacrifice_cost_payment_hash
            << " discard_payment_first=" << record.first_discard_cost_payment_record_index
            << " discard_payment_count=" << record.discard_cost_payment_record_count
            << " discard_payment_hash=" << record.discard_cost_payment_hash
            << " tap_payment_first=" << record.first_tap_cost_payment_record_index
            << " tap_payment_count=" << record.tap_cost_payment_record_count
            << " tap_payment_hash=" << record.tap_cost_payment_hash
            << " life_payment_first=" << record.first_life_cost_payment_record_index
            << " life_payment_count=" << record.life_cost_payment_record_count
            << " life_payment_hash=" << record.life_cost_payment_hash
            << " return_payment_first=" << record.first_return_cost_payment_record_index
            << " return_payment_count=" << record.return_cost_payment_record_count
            << " return_payment_hash=" << record.return_cost_payment_hash
            << " loyalty_payment_first=" << record.first_loyalty_cost_payment_record_index
            << " loyalty_payment_count=" << record.loyalty_cost_payment_record_count
            << " loyalty_payment_hash=" << record.loyalty_cost_payment_hash
            << " speculative_event_count=" << record.speculative_event_count
            << " speculative_event_record_count=" << record.speculative_event_record_count
            << " speculative_stack_placement_count=" << record.speculative_stack_placement_record_count
            << " speculative_declaration_count=" << record.speculative_paid_action_declaration_record_count
            << " speculative_declaration_sequence=" << record.speculative_paid_action_declaration_sequence
            << " speculative_declaration_hash=" << record.speculative_paid_action_declaration_hash
            << " speculative_first_payment=" << record.speculative_first_payment_event_sequence
            << " speculative_last_payment=" << record.speculative_last_payment_event_sequence
            << " physical_before=" << record.physical_state_hash_before
            << " physical_after=" << record.physical_state_hash_after
            << " next_event_before=" << record.next_event_sequence_before
            << " speculative_next_event_after=" << record.speculative_next_event_sequence_after
            << " committed=" << (record.committed ? 1 : 0)
            << " rolled_back=" << (record.rolled_back ? 1 : 0)
            << " physical_state_preserved_on_rollback=" << (record.physical_state_preserved_on_rollback ? 1 : 0)
            << " choices_before_payment=" << (record.choices_before_payment ? 1 : 0)
            << " payments_before_placement=" << (record.payments_before_placement ? 1 : 0)
            << " placement_before_transaction=" << (record.placement_before_transaction ? 1 : 0)
            << " transaction_hash=" << record.transaction_hash
            << " recomputed_transaction_hash=" << paid_action_transaction_record_hash(record)
            << " committed_snapshot_present=" << (record.committed_paid_action_declaration_snapshot_present ? 1 : 0);
        if (record.committed_paid_action_declaration_snapshot_present) {
            write_paid_action_declaration_snapshot_text(out, "committed_snapshot", record.committed_paid_action_declaration_snapshot);
        }
        out << " speculative_snapshot_present=" << (record.speculative_paid_action_declaration_snapshot_present ? 1 : 0);
        if (record.speculative_paid_action_declaration_snapshot_present) {
            write_paid_action_declaration_snapshot_text(out, "speculative_snapshot", record.speculative_paid_action_declaration_snapshot);
        }
        out << "\n";
    }
    return out.str();
}

std::uint64_t paid_action_transaction_journal_text_hash(std::string_view text) noexcept {
    return replay_artifact_text_hash(text);
}

void record_event(GameState& game, std::string kind, std::string detail) {
    record_event_with_links(game, std::move(kind), std::move(detail), EventRecordLinks{});
}

GameState make_game(std::vector<CardDefinition> definitions,
                    const std::vector<PlayerDeck>& decks,
                    std::uint64_t seed) {
    if (decks.size() < 2) {
        throw std::invalid_argument("MTGSim requires at least two players");
    }
    GameState game;
    game.definitions = std::move(definitions);
    game.rng_state = seed;
    game.players.reserve(decks.size());

    for (std::size_t i = 0; i < decks.size(); ++i) {
        PlayerState p;
        p.id = PlayerId{static_cast<u32>(i + 1)};
        p.name = decks[i].player_name.empty() ? ("Player " + std::to_string(i + 1)) : decks[i].player_name;
        game.players.push_back(std::move(p));
    }

    for (std::size_t player_index = 0; player_index < decks.size(); ++player_index) {
        const PlayerId owner{static_cast<u32>(player_index + 1)};
        auto& library = zone(game, owner, Zone::Library);
        library.reserve(decks[player_index].definition_indices.size());
        for (const auto def_index : decks[player_index].definition_indices) {
            if (def_index >= game.definitions.size()) {
                throw std::out_of_range("deck references missing card definition");
            }
            const ObjectId id{static_cast<u32>(game.objects.size() + 1)};
            const auto& def = game.definitions[def_index];
            game.objects.push_back(GameObject{
                .id = id,
                .definition_index = def_index,
                .owner = owner,
                .controller = owner,
                .zone = Zone::Library,
                .tapped = false,
                .token = false,
                .power = def.printed_power,
                .toughness = def.printed_toughness,
                .damage_marked = 0,
                .targets = {}
            });
            game.objects.back().zone_change_index = game.next_zone_change_index++;
            library.push_back(id);
        }
    }

    game.starting_player = PlayerId{1};
    game.active_player = PlayerId{1};
    game.priority_player = PlayerId{1};
    record_event(game, "game_created", "players=" + std::to_string(game.players.size()));
    return game;
}

void start_game(GameState& game, const StartOptions& options) {
    SplitMix64 rng(game.rng_state);
    for (auto& p : game.players) {
        p.life = options.starting_life_total;
        p.turn_start_index = 0;
        p.mulligans_taken = 0;
        p.lands_played_this_turn = 0;
        if (options.shuffle_libraries) {
            rng.shuffle(p.zones[zone_index(Zone::Library)].begin(), p.zones[zone_index(Zone::Library)].end());
        }
    }
    game.rng_state = rng.state();
    game.turn_number = 1;
    game.step = Step::Untap;
    game.active_player = game.starting_player;
    game.priority_player = game.starting_player;
    if (game.active_player.valid()) {
        auto& active = player(game, game.active_player);
        active.turn_start_index += 1U;
        active.lands_played_this_turn = 0;
    }
    game.consecutive_priority_passes = 0;
    game.attackers_declared_this_step = false;
    game.combat_damage_assigned_this_step = false;
    game.blocker_declaration_complete_players.clear();
    clear_combat_assignments(game);

    for (auto& p : game.players) {
        for (u32 i = 0; i < options.opening_hand_size; ++i) {
            draw_card(game, p.id);
        }
    }
    apply_state_based_actions(game);
    record_event(game, "game_started", "opening_hand_size=" + std::to_string(options.opening_hand_size));
}

void draw_card(GameState& game, PlayerId player_id) {
    auto& p = player(game, player_id);
    const u32 library_size_before = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
    const u32 hand_size_before = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    const u32 empty_attempts_before = p.empty_library_draw_attempts;
    if (p.zones[zone_index(Zone::Library)].empty()) {
        ++p.empty_library_draw_attempts;
        DrawRecord record{};
        record.outcome = DrawRecordOutcome::EmptyLibrary;
        record.player = player_id;
        record.library_size_before = library_size_before;
        record.library_size_after = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
        record.hand_size_before = hand_size_before;
        record.hand_size_after = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
        record.empty_library_draw_attempts_before = empty_attempts_before;
        record.empty_library_draw_attempts_after = p.empty_library_draw_attempts;
        record.empty_library_attempt = true;
        record_draw_record(game, std::move(record));
        return;
    }

    const ObjectId top = p.zones[zone_index(Zone::Library)].back();
    const u64 zone_change_before = object(game, top).zone_change_index;
    const std::size_t zone_record_count_before = game.zone_change_records.size();
    move_object(game, top, player_id, Zone::Hand);

    DrawRecord record{};
    record.outcome = DrawRecordOutcome::DrewCard;
    record.player = player_id;
    record.card = top;
    record.library_size_before = library_size_before;
    record.library_size_after = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
    record.hand_size_before = hand_size_before;
    record.hand_size_after = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    record.empty_library_draw_attempts_before = empty_attempts_before;
    record.empty_library_draw_attempts_after = p.empty_library_draw_attempts;
    record.card_zone_change_index_before = zone_change_before;
    record.card_zone_change_index_after = object(game, top).zone_change_index;
    if (game.zone_change_records.size() > zone_record_count_before) {
        record.zone_change_record_index = static_cast<u32>(zone_record_count_before + 1U);
    }
    record.card_moved = true;
    record_draw_record(game, std::move(record));
}

bool take_mulligan(GameState& game, PlayerId player_id, std::uint32_t opening_hand_size) {
    auto& p = player(game, player_id);
    const u32 hand_size_before = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    const u32 library_size_before = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
    const u32 mulligans_before = p.mulligans_taken;
    const u32 empty_attempts_before = p.empty_library_draw_attempts;
    const u64 rng_state_before = game.rng_state;
    const std::size_t zone_records_before = game.zone_change_records.size();
    const std::size_t draw_records_before = game.draw_records.size();

    const std::vector<ObjectId> returned_cards = p.zones[zone_index(Zone::Hand)];
    for (auto it = returned_cards.rbegin(); it != returned_cards.rend(); ++it) {
        move_object(game, *it, player_id, Zone::Library);
    }

    const u32 library_size_after_return = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
    const u32 hand_size_after_return = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    const std::size_t zone_records_after_return = game.zone_change_records.size();

    SplitMix64 rng(game.rng_state);
    rng.shuffle(p.zones[zone_index(Zone::Library)].begin(), p.zones[zone_index(Zone::Library)].end());
    game.rng_state = rng.state();
    const u64 rng_state_after = game.rng_state;
    const u32 library_size_after_shuffle = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());

    for (u32 i = 0; i < opening_hand_size; ++i) {
        draw_card(game, player_id);
    }

    u32 successful_draws = 0;
    for (std::size_t i = draw_records_before; i < game.draw_records.size(); ++i) {
        if (game.draw_records[i].player == player_id && game.draw_records[i].outcome == DrawRecordOutcome::DrewCard) {
            ++successful_draws;
        }
    }

    ++p.mulligans_taken;

    MulliganRecord record{};
    record.player = player_id;
    record.mulligans_before = mulligans_before;
    record.mulligans_after = p.mulligans_taken;
    record.opening_hand_size = opening_hand_size;
    record.returned_count = hand_size_before;
    record.draw_attempt_count = opening_hand_size;
    record.successful_draw_count = successful_draws;
    record.library_size_before = library_size_before;
    record.library_size_after_return = library_size_after_return;
    record.library_size_after_shuffle = library_size_after_shuffle;
    record.library_size_after = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
    record.hand_size_before = hand_size_before;
    record.hand_size_after_return = hand_size_after_return;
    record.hand_size_after = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    record.empty_library_draw_attempts_before = empty_attempts_before;
    record.empty_library_draw_attempts_after = p.empty_library_draw_attempts;
    record.rng_state_before = rng_state_before;
    record.rng_state_after = rng_state_after;
    if (zone_records_after_return > zone_records_before) {
        record.first_return_zone_change_record_index = static_cast<u32>(zone_records_before + 1U);
        record.return_zone_change_record_count = static_cast<u32>(zone_records_after_return - zone_records_before);
    }
    if (game.draw_records.size() > draw_records_before) {
        record.first_draw_record_index = static_cast<u32>(draw_records_before + 1U);
        record.draw_record_count = static_cast<u32>(game.draw_records.size() - draw_records_before);
    }
    record.shuffled = true;
    record.used_zone_change_pipeline = hand_size_before == 0U || record.return_zone_change_record_count >= hand_size_before;
    record.used_draw_pipeline = opening_hand_size == 0U || record.draw_record_count == opening_hand_size;
    record_mulligan_record(game, std::move(record));
    return true;
}

bool keep_mulligan_hand(GameState& game, PlayerId player_id, const std::vector<ObjectId>& bottom_cards) {
    auto& p = player(game, player_id);
    const u32 required_bottom_count = p.mulligans_taken;
    const u32 hand_size_before = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    const u32 library_size_before = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
    if (required_bottom_count > hand_size_before) {
        record_event(game, "mulligan_keep_failed", p.name + " cannot bottom " + std::to_string(required_bottom_count) + " from hand size " + std::to_string(hand_size_before));
        return false;
    }
    if (!bottom_cards.empty() && bottom_cards.size() != required_bottom_count) {
        record_event(game, "mulligan_keep_failed", p.name + " provided " + std::to_string(bottom_cards.size()) + " bottom choices for required count " + std::to_string(required_bottom_count));
        return false;
    }

    std::vector<ObjectId> chosen;
    chosen.reserve(required_bottom_count);
    const bool explicit_choice = !bottom_cards.empty() || required_bottom_count == 0U;
    if (!bottom_cards.empty()) {
        for (const auto id : bottom_cards) {
            if (!object_in_player_hand(game, player_id, id) || std::find(chosen.begin(), chosen.end(), id) != chosen.end()) {
                record_event(game, "mulligan_keep_failed", p.name + " chose invalid bottom card " + std::to_string(id.value));
                return false;
            }
            chosen.push_back(id);
        }
    } else {
        const auto& hand = p.zones[zone_index(Zone::Hand)];
        for (u32 i = 0; i < required_bottom_count; ++i) {
            chosen.push_back(hand[hand.size() - 1U - i]);
        }
    }

    const std::size_t zone_records_before = game.zone_change_records.size();
    for (u32 i = 0; i < chosen.size(); ++i) {
        move_object(game, chosen[i], player_id, Zone::Library);
        if (object(game, chosen[i]).zone == Zone::Library && object(game, chosen[i]).owner == player_id) {
            place_library_object_on_bottom(game, player_id, chosen[i], i);
        }
    }

    const std::size_t zone_records_after = game.zone_change_records.size();
    MulliganKeepRecord record{};
    record.player = player_id;
    record.mulligans_taken = p.mulligans_taken;
    record.bottom_count_required = required_bottom_count;
    record.bottom_count = static_cast<u32>(chosen.size());
    record.hand_size_before = hand_size_before;
    record.hand_size_after = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    record.library_size_before = library_size_before;
    record.library_size_after = static_cast<u32>(p.zones[zone_index(Zone::Library)].size());
    if (zone_records_after > zone_records_before) {
        record.first_bottom_zone_change_record_index = static_cast<u32>(zone_records_before + 1U);
        record.bottom_zone_change_record_count = static_cast<u32>(zone_records_after - zone_records_before);
    }
    record.bottomed_cards = chosen;
    record.explicit_choice = explicit_choice;
    record.deterministic_fallback = bottom_cards.empty() && required_bottom_count != 0U;
    record.used_zone_change_pipeline = required_bottom_count == 0U || record.bottom_zone_change_record_count == required_bottom_count;
    record.placed_on_bottom = true;
    if (record.bottom_count != 0U) {
        const auto& library = p.zones[zone_index(Zone::Library)];
        if (library.size() < record.bottom_count) {
            record.placed_on_bottom = false;
        } else {
            for (u32 i = 0; i < record.bottom_count; ++i) {
                if (library[i] != record.bottomed_cards[i]) {
                    record.placed_on_bottom = false;
                    break;
                }
            }
        }
    }
    record_mulligan_keep_record(game, std::move(record));
    return true;
}

bool discard_card_for_reason(GameState& game, PlayerId player_id, ObjectId object_id, DiscardRecordKind kind) {
    if (!valid_player_index(game, player_id) || !valid_object_index(game, object_id) ||
        !object_in_player_hand(game, player_id, object_id)) {
        record_event(game,
                     kind == DiscardRecordKind::CleanupHandSize ? "discard_cleanup_failed" :
                         (kind == DiscardRecordKind::CostPayment ? "discard_cost_payment_failed" : "discard_failed"),
                     "player#" + std::to_string(player_id.value) + " could not discard object#" + std::to_string(object_id.value));
        return false;
    }

    auto& p = player(game, player_id);
    const u32 hand_size_before = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    const u32 graveyard_size_before = static_cast<u32>(p.zones[zone_index(Zone::Graveyard)].size());
    const u64 card_zone_change_index_before = object(game, object_id).zone_change_index;
    const std::size_t zone_record_count_before = game.zone_change_records.size();

    move_object(game, object_id, player_id, Zone::Graveyard);

    const std::size_t zone_record_count_after = game.zone_change_records.size();
    DiscardRecord record{};
    record.kind = kind;
    record.player = player_id;
    record.card = object_id;
    record.hand_size_before = hand_size_before;
    record.hand_size_after = static_cast<u32>(p.zones[zone_index(Zone::Hand)].size());
    record.graveyard_size_before = graveyard_size_before;
    record.graveyard_size_after = static_cast<u32>(p.zones[zone_index(Zone::Graveyard)].size());
    record.max_hand_size = p.max_hand_size;
    record.card_zone_change_index_before = card_zone_change_index_before;
    record.card_zone_change_index_after = object(game, object_id).zone_change_index;
    if (zone_record_count_after > zone_record_count_before) {
        record.zone_change_record_index = static_cast<u32>(zone_record_count_before + 1U);
    }
    record.explicit_choice = kind == DiscardRecordKind::ExplicitChoice;
    record.cleanup_hand_size = kind == DiscardRecordKind::CleanupHandSize;
    record.cost_payment = kind == DiscardRecordKind::CostPayment;
    record.used_zone_change_pipeline = zone_record_count_after == zone_record_count_before + 1U;
    record_discard_record(game, std::move(record));
    return true;
}

bool discard_card(GameState& game, PlayerId player_id, ObjectId object_id) {
    return discard_card_for_reason(game, player_id, object_id, DiscardRecordKind::ExplicitChoice);
}

void lose_life(GameState& game, PlayerId player_id, std::int32_t amount) {
    if (amount < 0) {
        throw std::invalid_argument("lose_life amount must be non-negative");
    }
    record_life_change(game, player_id, LifeChangeKind::Loss, amount);
}

void gain_life(GameState& game, PlayerId player_id, std::int32_t amount) {
    if (amount < 0) {
        throw std::invalid_argument("gain_life amount must be non-negative");
    }
    record_life_change(game, player_id, LifeChangeKind::Gain, amount);
}

void add_mana(GameState& game, PlayerId player_id, ManaSymbol symbol, std::uint32_t amount) {
    if (amount == 0U) {
        return;
    }
    add_mana_pool_recorded(game, player_id, single_mana_pool(symbol, amount));
}

bool can_pay_mana_cost(const ManaPool& pool, const ManaCost& cost) noexcept {
    ManaPool copy = pool;
    return spend_mana_from_copy(copy, cost);
}

bool pay_mana_cost(GameState& game, PlayerId player_id, const ManaCost& cost) {
    return pay_mana_cost_recorded(game, player_id, cost, false);
}

void clear_mana_pool(GameState& game, PlayerId player_id) {
    clear_mana_pool_recorded(game, player_id);
}

void clear_all_mana_pools(GameState& game) {
    for (const auto& p : game.players) {
        clear_mana_pool(game, p.id);
    }
}

void tap_object(GameState& game, PlayerId controller, ObjectId object_id) {
    auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield) {
        throw std::logic_error("can only tap a permanent on the battlefield");
    }
    if (obj.controller != controller) {
        throw std::logic_error("only a permanent's controller can tap it through this API");
    }
    if (obj.tapped) {
        throw std::logic_error("object is already tapped");
    }
    obj.tapped = true;
    record_event_with_links(game,
                            "tap",
                            player(game, controller).name + " tapped " + object_label(game, object_id),
                            EventRecordLinks{
                                .object = object_id,
                                .object_zone_change_index = obj.zone_change_index,
                                .player = controller
                            });
}

std::uint32_t mana_ability_count(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return 0U;
    }
    const auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return 0U;
    }
    return total_mana_ability_count_for_definition(*def);
}

bool can_activate_mana_ability(const GameState& game, PlayerId controller, ObjectId object_id, u32 mana_ability_index) noexcept {
    if (!valid_player_index(game, controller) || !valid_object_index(game, object_id)) {
        return false;
    }
    const auto& p = player(game, controller);
    if (p.lost) {
        return false;
    }
    const auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (obj.zone != Zone::Battlefield || obj.controller != controller || def == nullptr) {
        return false;
    }
    ManaAbilityDefinition ability;
    if (!mana_ability_definition_for_index(*def, mana_ability_index, ability) || !ability.active()) {
        return false;
    }
    if (ability.tap_cost) {
        if (obj.tapped) {
            return false;
        }
        if (object_is_creature(game, obj) && object_has_summoning_sickness(game, object_id)) {
            return false;
        }
    }
    return true;
}

bool activate_mana_ability(GameState& game, PlayerId controller, ObjectId object_id, u32 mana_ability_index) {
    if (!can_activate_mana_ability(game, controller, object_id, mana_ability_index)) {
        record_event(game, "mana_ability_failed", "object#" + std::to_string(object_id.value) + " ability#" + std::to_string(mana_ability_index));
        return false;
    }
    auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return false;
    }
    ManaAbilityDefinition ability;
    (void)mana_ability_definition_for_index(*def, mana_ability_index, ability);
    const auto label = object_label(game, object_id) + " " + mana_ability_label(*def, mana_ability_index);
    if (ability.tap_cost) {
        tap_object(game, controller, object_id);
    }
    add_mana_pool_recorded(game, controller, ability.produces, object_id, mana_ability_index);
    game.priority_player = controller;
    game.consecutive_priority_passes = 0;
    record_event(game, "mana_ability", label + " produced " + mana_pool_summary(ability.produces));
    return true;
}

void tap_permanent_for_mana(GameState& game, PlayerId controller, ObjectId object_id) {
    const auto& obj_before = object(game, object_id);
    const auto* def_ptr = current_definition_for_object(game, obj_before);
    if (def_ptr == nullptr) {
        throw std::logic_error("object has invalid card definition");
    }
    const auto& def = *def_ptr;
    if (!def.taps_for_mana) {
        throw std::logic_error("permanent has no built-in tap-for-mana scaffold ability");
    }
    if (!activate_mana_ability(game, controller, object_id, 1U)) {
        throw std::logic_error("permanent mana ability was not legal to activate");
    }
}

bool can_pay_mana_cost_with_available_mana(const GameState& game, PlayerId player_id, const ManaCost& cost) noexcept {
    std::vector<ManaAbilityCandidate> plan;
    return select_mana_ability_pay_plan(game, player_id, cost, plan);
}

bool pay_mana_cost_with_mana_abilities(GameState& game, PlayerId player_id, const ManaCost& cost) {
    return pay_mana_cost_with_mana_abilities_excluding_tap_sources(game, player_id, cost, {});
}


bool can_cast_spell_now(const GameState& game, PlayerId caster, ObjectId object_id) noexcept {
    if (!valid_player_index(game, caster) || !valid_object_index(game, object_id)) {
        return false;
    }
    if (player(game, caster).lost || game.priority_player != caster || !object_in_player_hand(game, caster, object_id)) {
        return false;
    }
    const auto& obj = object(game, object_id);
    if (obj.definition_index >= game.definitions.size()) {
        return false;
    }
    const auto& def = game.definitions[obj.definition_index];
    if (definition_is_land(def)) {
        return false;
    }
    if (definition_is_instant(def) || definition_has_flash(def)) {
        return true;
    }
    return player_has_sorcery_speed_window(game, caster);
}

bool can_play_land(const GameState& game, PlayerId player_id, ObjectId object_id) noexcept {
    if (!valid_player_index(game, player_id) || !valid_object_index(game, object_id)) {
        return false;
    }
    const auto& p = player(game, player_id);
    if (p.lost || game.priority_player != player_id || !object_in_player_hand(game, player_id, object_id)) {
        return false;
    }
    const auto& obj = object(game, object_id);
    if (obj.definition_index >= game.definitions.size() || !definition_is_land(game.definitions[obj.definition_index])) {
        return false;
    }
    if (!player_has_sorcery_speed_window(game, player_id)) {
        return false;
    }
    return p.lands_played_this_turn < p.max_land_plays_per_turn;
}

bool play_land_from_hand(GameState& game, PlayerId player_id, ObjectId object_id) {
    if (!can_play_land(game, player_id, object_id)) {
        record_event(game, "play_land_failed", "player#" + std::to_string(player_id.value) + " could not play object#" + std::to_string(object_id.value));
        return false;
    }
    auto& p = player(game, player_id);
    const std::string label = object_label(game, object_id);
    move_object(game, object_id, player_id, Zone::Battlefield);
    ++p.lands_played_this_turn;
    game.priority_player = player_id;
    game.consecutive_priority_passes = 0;
    record_event(game, "play_land", p.name + " played " + label + " lands_played=" + std::to_string(p.lands_played_this_turn));
    return true;
}

void untap_permanents(GameState& game, PlayerId controller) {
    auto& battlefield = zone(game, controller, Zone::Battlefield);
    u32 changed = 0;
    for (const auto id : battlefield) {
        auto& obj = object(game, id);
        if (obj.tapped) {
            obj.tapped = false;
            ++changed;
        }
    }
    if (changed != 0U) {
        record_event(game, "untap", player(game, controller).name + " untapped " + std::to_string(changed) + " permanent(s)");
    }
}

void mark_damage(GameState& game, ObjectId object_id, std::uint32_t amount) {
    auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield) {
        throw std::logic_error("can only mark damage on an object on the battlefield");
    }
    obj.damage_marked += amount;
    record_event(game, "mark_damage", object_label(game, object_id) + " damage=" + std::to_string(obj.damage_marked));
}

ObjectId create_token(GameState& game, PlayerId controller, std::uint32_t definition_index) {
    if (!valid_player_index(game, controller)) {
        throw std::logic_error("token controller is invalid");
    }
    if (definition_index >= game.definitions.size()) {
        throw std::logic_error("token definition index is invalid");
    }
    const auto& def = game.definitions[definition_index];
    const ObjectId id{static_cast<u32>(game.objects.size() + 1U)};
    GameObject obj;
    obj.id = id;
    obj.definition_index = definition_index;
    obj.owner = controller;
    obj.controller = controller;
    obj.zone = Zone::Battlefield;
    obj.token = true;
    obj.power = def.printed_power;
    obj.toughness = def.printed_toughness;
    obj.controlled_since_turn_start_index = player(game, controller).turn_start_index;
    obj.zone_change_index = game.next_zone_change_index++;
    obj.layer_timestamp = game.next_layer_timestamp++;
    game.objects.push_back(obj);
    zone(game, controller, Zone::Battlefield).push_back(id);
    add_entering_planeswalker_loyalty(game, id);
    add_entering_battle_defense_and_protector(game, id);
    record_event(game, "create_token", player(game, controller).name + " created " + object_label(game, id));
    if (object_is_creature(game, object(game, id))) {
        queue_matching_triggers_for_event(game, TriggerEventKind::CreatureEntersBattlefield, id);
    }
    return id;
}

std::vector<ObjectId> create_tokens(GameState& game, PlayerId controller, std::uint32_t definition_index, std::uint32_t count) {
    std::vector<ObjectId> ids;
    ids.reserve(count);
    for (u32 i = 0; i < count; ++i) {
        ids.push_back(create_token(game, controller, definition_index));
    }
    return ids;
}

bool object_ceased_to_exist(const GameState& game, ObjectId object_id) noexcept {
    return valid_object_index(game, object_id) && object(game, object_id).ceased_to_exist;
}

std::size_t zone_change_record_count(const GameState& game) noexcept {
    return game.zone_change_records.size();
}

const ZoneChangeRecord* latest_zone_change_record(const GameState& game) noexcept {
    if (game.zone_change_records.empty()) {
        return nullptr;
    }
    return &game.zone_change_records.back();
}

std::size_t zone_change_replacement_record_count(const GameState& game) noexcept {
    return game.zone_change_replacement_records.size();
}

const ZoneChangeReplacementRecord* latest_zone_change_replacement_record(const GameState& game) noexcept {
    if (game.zone_change_replacement_records.empty()) {
        return nullptr;
    }
    return &game.zone_change_replacement_records.back();
}

std::size_t damage_record_count(const GameState& game) noexcept {
    return game.damage_records.size();
}

const DamageRecord* latest_damage_record(const GameState& game) noexcept {
    if (game.damage_records.empty()) {
        return nullptr;
    }
    return &game.damage_records.back();
}

std::size_t damage_prevention_record_count(const GameState& game) noexcept {
    return game.damage_prevention_records.size();
}

const DamagePreventionRecord* latest_damage_prevention_record(const GameState& game) noexcept {
    if (game.damage_prevention_records.empty()) {
        return nullptr;
    }
    return &game.damage_prevention_records.back();
}

std::size_t life_change_record_count(const GameState& game) noexcept {
    return game.life_change_records.size();
}

const LifeChangeRecord* latest_life_change_record(const GameState& game) noexcept {
    if (game.life_change_records.empty()) {
        return nullptr;
    }
    return &game.life_change_records.back();
}

std::size_t mana_change_record_count(const GameState& game) noexcept {
    return game.mana_change_records.size();
}

const ManaChangeRecord* latest_mana_change_record(const GameState& game) noexcept {
    if (game.mana_change_records.empty()) {
        return nullptr;
    }
    return &game.mana_change_records.back();
}

std::size_t mana_payment_plan_record_count(const GameState& game) noexcept {
    return game.mana_payment_plan_records.size();
}

const ManaPaymentPlanRecord* latest_mana_payment_plan_record(const GameState& game) noexcept {
    if (game.mana_payment_plan_records.empty()) {
        return nullptr;
    }
    return &game.mana_payment_plan_records.back();
}

std::size_t tap_cost_payment_record_count(const GameState& game) noexcept {
    return game.tap_cost_payment_records.size();
}

const TapCostPaymentRecord* latest_tap_cost_payment_record(const GameState& game) noexcept {
    if (game.tap_cost_payment_records.empty()) {
        return nullptr;
    }
    return &game.tap_cost_payment_records.back();
}

std::uint64_t tap_cost_payment_record_hash(const TapCostPaymentRecord& record) noexcept {
    return tap_cost_payment_record_identity_hash(record);
}

std::size_t sacrifice_cost_payment_record_count(const GameState& game) noexcept {
    return game.sacrifice_cost_payment_records.size();
}

const SacrificeCostPaymentRecord* latest_sacrifice_cost_payment_record(const GameState& game) noexcept {
    if (game.sacrifice_cost_payment_records.empty()) {
        return nullptr;
    }
    return &game.sacrifice_cost_payment_records.back();
}

std::size_t paid_action_declaration_record_count(const GameState& game) noexcept {
    return game.paid_action_declaration_records.size();
}

const PaidActionDeclarationRecord* latest_paid_action_declaration_record(const GameState& game) noexcept {
    if (game.paid_action_declaration_records.empty()) {
        return nullptr;
    }
    return &game.paid_action_declaration_records.back();
}

std::size_t paid_action_transaction_record_count(const GameState& game) noexcept {
    return game.paid_action_transaction_records.size();
}

const PaidActionTransactionRecord* latest_paid_action_transaction_record(const GameState& game) noexcept {
    if (game.paid_action_transaction_records.empty()) {
        return nullptr;
    }
    return &game.paid_action_transaction_records.back();
}

std::size_t counter_change_record_count(const GameState& game) noexcept {
    return game.counter_change_records.size();
}

const CounterChangeRecord* latest_counter_change_record(const GameState& game) noexcept {
    if (game.counter_change_records.empty()) {
        return nullptr;
    }
    return &game.counter_change_records.back();
}

std::size_t discard_record_count(const GameState& game) noexcept {
    return game.discard_records.size();
}

const DiscardRecord* latest_discard_record(const GameState& game) noexcept {
    if (game.discard_records.empty()) {
        return nullptr;
    }
    return &game.discard_records.back();
}

std::size_t trigger_record_count(const GameState& game) noexcept {
    return game.trigger_records.size();
}

const TriggerRecord* latest_trigger_record(const GameState& game) noexcept {
    if (game.trigger_records.empty()) {
        return nullptr;
    }
    return &game.trigger_records.back();
}

std::size_t event_record_count(const GameState& game) noexcept {
    return game.event_records.size();
}

const EventRecord* latest_event_record(const GameState& game) noexcept {
    if (game.event_records.empty()) {
        return nullptr;
    }
    return &game.event_records.back();
}

std::size_t stack_placement_record_count(const GameState& game) noexcept {
    return game.stack_placement_records.size();
}

const StackPlacementRecord* latest_stack_placement_record(const GameState& game) noexcept {
    if (game.stack_placement_records.empty()) {
        return nullptr;
    }
    return &game.stack_placement_records.back();
}

std::size_t stack_resolution_record_count(const GameState& game) noexcept {
    return game.stack_resolution_records.size();
}

const StackResolutionRecord* latest_stack_resolution_record(const GameState& game) noexcept {
    if (game.stack_resolution_records.empty()) {
        return nullptr;
    }
    return &game.stack_resolution_records.back();
}

std::size_t priority_transition_record_count(const GameState& game) noexcept {
    return game.priority_transition_records.size();
}

const PriorityTransitionRecord* latest_priority_transition_record(const GameState& game) noexcept {
    if (game.priority_transition_records.empty()) {
        return nullptr;
    }
    return &game.priority_transition_records.back();
}

std::size_t state_based_action_record_count(const GameState& game) noexcept {
    return game.state_based_action_records.size();
}

const StateBasedActionRecord* latest_state_based_action_record(const GameState& game) noexcept {
    if (game.state_based_action_records.empty()) {
        return nullptr;
    }
    return &game.state_based_action_records.back();
}

std::size_t combat_declaration_record_count(const GameState& game) noexcept {
    return game.combat_declaration_records.size();
}

const CombatDeclarationRecord* latest_combat_declaration_record(const GameState& game) noexcept {
    if (game.combat_declaration_records.empty()) {
        return nullptr;
    }
    return &game.combat_declaration_records.back();
}

std::size_t combat_damage_assignment_record_count(const GameState& game) noexcept {
    return game.combat_damage_assignment_records.size();
}

const CombatDamageAssignmentRecord* latest_combat_damage_assignment_record(const GameState& game) noexcept {
    if (game.combat_damage_assignment_records.empty()) {
        return nullptr;
    }
    return &game.combat_damage_assignment_records.back();
}

std::size_t draw_record_count(const GameState& game) noexcept {
    return game.draw_records.size();
}

const DrawRecord* latest_draw_record(const GameState& game) noexcept {
    if (game.draw_records.empty()) {
        return nullptr;
    }
    return &game.draw_records.back();
}

std::size_t mulligan_record_count(const GameState& game) noexcept {
    return game.mulligan_records.size();
}

const MulliganRecord* latest_mulligan_record(const GameState& game) noexcept {
    if (game.mulligan_records.empty()) {
        return nullptr;
    }
    return &game.mulligan_records.back();
}

std::size_t mulligan_keep_record_count(const GameState& game) noexcept {
    return game.mulligan_keep_records.size();
}

const MulliganKeepRecord* latest_mulligan_keep_record(const GameState& game) noexcept {
    if (game.mulligan_keep_records.empty()) {
        return nullptr;
    }
    return &game.mulligan_keep_records.back();
}

std::size_t action_receipt_record_count(const GameState& game) noexcept {
    return game.action_receipt_records.size();
}

const ActionReceiptRecord* latest_action_receipt_record(const GameState& game) noexcept {
    if (game.action_receipt_records.empty()) {
        return nullptr;
    }
    return &game.action_receipt_records.back();
}

std::uint64_t action_receipt_hash(const ActionReceiptRecord& receipt) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ActionReceiptRecord.v1");
    hash_into(h, receipt);
    return h.value();
}

std::string canonical_action_string(const LegalAction& action) {
    std::ostringstream out;
    out << "MTGSim.Action.v2"
        << "|kind=" << static_cast<unsigned>(action.kind)
        << "|player=" << action.player.value
        << "|object=" << action.object.value
        << "|mode=" << action.mode_index
        << "|ability=" << action.ability_index
        << "|mana=" << action.mana_ability_index
        << "|trigger_order=";
    for (std::size_t i = 0; i < action.trigger_order.size(); ++i) {
        if (i != 0U) {
            out << ",";
        }
        out << action.trigger_order[i];
    }
    out << "|targets=";
    const auto targets = action_target_vector(action);
    out << targets.size() << "[";
    for (std::size_t i = 0; i < targets.size(); ++i) {
        if (i != 0U) {
            out << ",";
        }
        out << canonical_target_string(targets[i]);
    }
    out << "]";
    return out.str();
}

std::uint64_t legal_action_hash(const LegalAction& action) noexcept {
    StableHasher h;
    hash_action_fields(h, action);
    return h.value();
}

namespace {

[[nodiscard]] std::string compact_target_label(TargetRef target) {
    switch (target.kind) {
        case TargetKind::Player:
            return "p" + std::to_string(target.player.value);
        case TargetKind::Object:
            return "o" + std::to_string(target.object.value);
        case TargetKind::None:
            return "none";
    }
    return "none";
}

} // namespace

LegalAction make_declare_attackers_action(PlayerId attacker_controller, const std::vector<AttackAssignment>& assignments) {
    LegalAction action{};
    action.kind = ActionKind::DeclareAttacker;
    action.player = attacker_controller;

    if (assignments.empty()) {
        action.label = "declare_attackers:none";
        return action;
    }

    if (assignments.size() == 1U) {
        action.object = assignments.front().attacker;
        action.target = assignments.front().target;
        action.label = "declare_attacker:o" + std::to_string(assignments.front().attacker.value) +
            "->" + compact_target_label(assignments.front().target);
        return action;
    }

    action.targets.reserve(assignments.size() * 2U);
    for (const auto assignment : assignments) {
        action.targets.push_back(TargetRef{.kind = TargetKind::Object, .object = assignment.attacker});
        action.targets.push_back(assignment.target);
    }
    action.label = "declare_attackers:" + std::to_string(assignments.size());
    return action;
}

std::vector<AttackAssignment> attack_assignments_from_action(const LegalAction& action) {
    if (action.kind != ActionKind::DeclareAttacker) {
        return {};
    }

    if (!action.targets.empty()) {
        if (action.targets.size() == 1U && action.object.valid() && action.targets.front().valid()) {
            return std::vector<AttackAssignment>{{.attacker = action.object, .target = action.targets.front()}};
        }
        if ((action.targets.size() % 2U) != 0U) {
            return {};
        }
        std::vector<AttackAssignment> assignments;
        assignments.reserve(action.targets.size() / 2U);
        for (std::size_t i = 0; i < action.targets.size(); i += 2U) {
            const auto attacker = action.targets[i];
            const auto target = action.targets[i + 1U];
            if (attacker.kind != TargetKind::Object || !attacker.object.valid() || !target.valid()) {
                return {};
            }
            assignments.push_back(AttackAssignment{.attacker = attacker.object, .target = target});
        }
        return assignments;
    }

    if (action.object.valid() && action.target.valid()) {
        return std::vector<AttackAssignment>{{.attacker = action.object, .target = action.target}};
    }

    return {};
}

LegalAction make_declare_blockers_action(PlayerId blocker_controller, const std::vector<BlockAssignment>& assignments) {
    LegalAction action{};
    action.kind = ActionKind::DeclareBlocker;
    action.player = blocker_controller;

    if (assignments.empty()) {
        action.label = "declare_blockers:none";
        return action;
    }

    if (assignments.size() == 1U) {
        action.object = assignments.front().blocker;
        action.target = TargetRef{.kind = TargetKind::Object, .object = assignments.front().attacker};
        action.label = "declare_blocker:o" + std::to_string(assignments.front().blocker.value) +
            "->o" + std::to_string(assignments.front().attacker.value);
        return action;
    }

    action.targets.reserve(assignments.size() * 2U);
    for (const auto assignment : assignments) {
        action.targets.push_back(TargetRef{.kind = TargetKind::Object, .object = assignment.blocker});
        action.targets.push_back(TargetRef{.kind = TargetKind::Object, .object = assignment.attacker});
    }
    action.label = "declare_blockers:" + std::to_string(assignments.size());
    return action;
}

std::vector<BlockAssignment> block_assignments_from_action(const LegalAction& action) {
    if (action.kind != ActionKind::DeclareBlocker) {
        return {};
    }

    if (!action.targets.empty()) {
        if (action.targets.size() == 1U && action.object.valid() &&
            action.targets.front().kind == TargetKind::Object && action.targets.front().object.valid()) {
            return std::vector<BlockAssignment>{{.blocker = action.object, .attacker = action.targets.front().object}};
        }
        if ((action.targets.size() % 2U) != 0U) {
            return {};
        }
        std::vector<BlockAssignment> assignments;
        assignments.reserve(action.targets.size() / 2U);
        for (std::size_t i = 0; i < action.targets.size(); i += 2U) {
            const auto blocker = action.targets[i];
            const auto attacker = action.targets[i + 1U];
            if (blocker.kind != TargetKind::Object || attacker.kind != TargetKind::Object ||
                !blocker.object.valid() || !attacker.object.valid()) {
                return {};
            }
            assignments.push_back(BlockAssignment{.blocker = blocker.object, .attacker = attacker.object});
        }
        return assignments;
    }

    if (action.object.valid() && action.target.kind == TargetKind::Object && action.target.object.valid()) {
        return std::vector<BlockAssignment>{{.blocker = action.object, .attacker = action.target.object}};
    }

    return {};
}

LegalAction make_order_combat_damage_action(PlayerId controller, ObjectId attacker_id, const std::vector<ObjectId>& blocker_order) {
    LegalAction action{};
    action.kind = ActionKind::OrderCombatDamage;
    action.player = controller;
    action.object = attacker_id;
    action.targets.reserve(blocker_order.size());
    for (const auto blocker_id : blocker_order) {
        action.targets.push_back(TargetRef{.kind = TargetKind::Object, .object = blocker_id});
    }
    action.label = "order_combat_damage:o" + std::to_string(attacker_id.value) + ":" + std::to_string(blocker_order.size());
    return action;
}

std::vector<ObjectId> combat_damage_order_from_action(const LegalAction& action) {
    if (action.kind != ActionKind::OrderCombatDamage) {
        return {};
    }
    std::vector<ObjectId> order;
    order.reserve(action.targets.size());
    for (const auto target : action.targets) {
        if (target.kind != TargetKind::Object || !target.object.valid()) {
            return {};
        }
        order.push_back(target.object);
    }
    return order;
}

std::uint64_t choice_request_hash(const ChoiceRequest& request) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ChoiceRequest.v2");
    hash_into(h, request.schema_version);
    h.add_u64(static_cast<u64>(request.kind));
    hash_into(h, request.chooser);
    hash_into(h, request.required);
    hash_into(h, request.action_frontier_complete);
    hash_into(h, request.action_generation_limit);
    hash_into(h, request.state_hash);
    h.add_size(request.actions.size());
    for (const auto& action : request.actions) {
        hash_into(h, legal_action_hash(action));
    }
    return h.value();
}

std::uint64_t legal_action_page_hash(const LegalActionPage& page) noexcept {
    StableHasher h;
    h.add_string("MTGSim.LegalActionPage.v3");
    hash_into(h, page.schema_version);
    h.add_u64(static_cast<u64>(page.kind));
    hash_into(h, page.chooser);
    hash_into(h, page.state_hash);
    hash_into(h, page.choice_request_hash);
    hash_into(h, page.cursor);
    hash_into(h, page.next_cursor);
    hash_into(h, page.requested_limit);
    hash_into(h, page.effective_limit);
    hash_into(h, page.actions_seen);
    hash_into(h, page.complete);
    hash_into(h, page.total_actions_lower_bound);
    hash_into(h, page.total_actions_exact);
    hash_into(h, page.remaining_actions_lower_bound);
    h.add_size(page.actions.size());
    for (const auto& action : page.actions) {
        hash_into(h, legal_action_hash(action));
    }
    return h.value();
}

std::uint64_t legal_action_page_location_hash(const LegalActionPageLocation& location) noexcept {
    StableHasher h;
    h.add_string("MTGSim.LegalActionPageLocation.v1");
    hash_into(h, location.found);
    hash_into(h, location.page_schema_version);
    h.add_u64(static_cast<u64>(location.kind));
    hash_into(h, location.chooser);
    hash_into(h, location.page_state_hash);
    hash_into(h, location.page_choice_request_hash);
    hash_into(h, location.requested_page_limit);
    hash_into(h, location.effective_page_limit);
    hash_into(h, location.page_cursor);
    hash_into(h, location.action_cursor);
    hash_into(h, location.index_in_page);
    hash_into(h, location.next_cursor);
    hash_into(h, location.actions_seen);
    hash_into(h, location.scanned_pages);
    hash_into(h, location.page_complete);
    hash_into(h, location.total_actions_lower_bound);
    hash_into(h, location.total_actions_exact);
    hash_into(h, location.remaining_actions_lower_bound);
    hash_into(h, location.page_hash);
    hash_into(h, location.action_hash);
    return h.value();
}

std::uint64_t choice_request_queue_hash(const ChoiceRequestQueue& queue) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ChoiceRequestQueue.v1");
    hash_into(h, queue.schema_version);
    hash_into(h, queue.state_hash);
    h.add_size(queue.requests.size());
    for (std::size_t i = 0; i < queue.requests.size(); ++i) {
        const auto& request = queue.requests[i];
        h.add_u64(static_cast<u64>(i + 1U));
        hash_into(h, request.schema_version);
        h.add_u64(static_cast<u64>(request.kind));
        hash_into(h, request.chooser);
        hash_into(h, request.required);
        hash_into(h, request.action_set_hash);
        h.add_size(request.actions.size());
    }
    return h.value();
}

std::uint64_t choice_queue_location_hash(const ChoiceQueueLocation& location) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ChoiceQueueLocation.v1");
    hash_into(h, location.found);
    hash_into(h, location.schema_version);
    hash_into(h, location.state_hash);
    hash_into(h, location.queue_hash);
    hash_into(h, location.queue_index);
    hash_into(h, location.queue_size);
    h.add_u64(static_cast<u64>(location.request_kind));
    hash_into(h, location.chooser);
    hash_into(h, location.request_required);
    hash_into(h, location.action_frontier_complete);
    hash_into(h, location.action_generation_limit);
    hash_into(h, location.choice_request_hash);
    hash_into(h, location.choice_action_count);
    hash_into(h, location.action_hash);
    return h.value();
}

LegalAction action_from_receipt(const ActionReceiptRecord& receipt) {
    LegalAction action{};
    action.kind = receipt.kind;
    action.player = receipt.player;
    action.object = receipt.object;
    action.targets = receipt.targets;
    if (receipt.targets.size() == 1U) {
        action.target = receipt.targets.front();
    }
    action.mode_index = receipt.mode_index;
    action.ability_index = receipt.ability_index;
    action.mana_ability_index = receipt.mana_ability_index;
    action.trigger_order = receipt.trigger_order;
    return action;
}

namespace {

[[nodiscard]] ActionTraceEntry action_trace_entry_from_receipt_record(const ActionReceiptRecord& receipt) {
    ActionTraceEntry entry{};
    entry.action = action_from_receipt(receipt);
    entry.expected_choice_kind = receipt.choice_kind;
    entry.expected_choice_request_schema_version = receipt.choice_request_schema_version;
    entry.expected_choice_request_hash = receipt.choice_request_hash;
    entry.expected_choice_action_count = receipt.choice_action_count;
    entry.expected_choice_required = receipt.choice_required;
    entry.expected_choice_action_frontier_complete = receipt.choice_action_frontier_complete;
    entry.expected_choice_action_generation_limit = receipt.choice_action_generation_limit;
    entry.expected_choice_validation_source = receipt.choice_validation_source;
    entry.expected_choice_validation_source_present = true;
    entry.expected_choice_page_location_present = true;
    entry.expected_choice_page_location_found = receipt.choice_page_location_found;
    entry.expected_choice_page_location_checked = receipt.choice_page_location_checked;
    entry.expected_choice_page_schema_version = receipt.choice_page_schema_version;
    entry.expected_choice_page_context_present = true;
    entry.expected_choice_page_state_hash = receipt.choice_page_state_hash;
    entry.expected_choice_page_choice_request_hash = receipt.choice_page_choice_request_hash;
    entry.expected_choice_page_requested_limit = receipt.choice_page_requested_limit;
    entry.expected_choice_page_effective_limit = receipt.choice_page_effective_limit;
    entry.expected_choice_page_cursor = receipt.choice_page_cursor;
    entry.expected_choice_action_cursor = receipt.choice_action_cursor;
    entry.expected_choice_page_index = receipt.choice_page_index;
    entry.expected_choice_page_next_cursor = receipt.choice_page_next_cursor;
    entry.expected_choice_page_actions_seen = receipt.choice_page_actions_seen;
    entry.expected_choice_page_scanned_pages = receipt.choice_page_scanned_pages;
    entry.expected_choice_page_complete = receipt.choice_page_complete;
    entry.expected_choice_page_count_present = true;
    entry.expected_choice_page_total_actions_lower_bound = receipt.choice_page_total_actions_lower_bound;
    entry.expected_choice_page_total_actions_exact = receipt.choice_page_total_actions_exact;
    entry.expected_choice_page_remaining_actions_lower_bound = receipt.choice_page_remaining_actions_lower_bound;
    entry.expected_choice_page_hash = receipt.choice_page_hash;
    entry.expected_choice_page_location_hash = receipt.choice_page_location_hash;
    entry.expected_choice_queue_schema_version = receipt.choice_queue_schema_version;
    entry.expected_choice_queue_hash = receipt.choice_queue_hash;
    entry.expected_choice_queue_index = receipt.choice_queue_index;
    entry.expected_choice_queue_size = receipt.choice_queue_size;
    entry.expected_choice_queue_location_schema_version = receipt.choice_queue_location_schema_version;
    entry.expected_choice_queue_location_found = receipt.choice_queue_location_found;
    entry.expected_choice_queue_location_checked = receipt.choice_queue_location_checked;
    entry.expected_choice_queue_location_hash = receipt.choice_queue_location_hash;
    entry.expected_action_schema_version = receipt.action_schema_version;
    entry.expected_action_hash = receipt.action_hash;
    entry.expected_state_schema_version = receipt.state_schema_version;
    entry.expected_state_hash_before = receipt.state_hash_before;
    entry.expected_state_hash_after = receipt.state_hash_after;
    entry.expected_applied = receipt.applied;
    return entry;
}

void hash_action_trace_entry_fields(StableHasher& h, const ActionTraceEntry& entry) noexcept {
    hash_into(h, legal_action_hash(entry.action));
    h.add_u64(static_cast<u64>(entry.expected_choice_kind));
    hash_into(h, entry.expected_choice_request_schema_version);
    hash_into(h, entry.expected_choice_request_hash);
    hash_into(h, entry.expected_choice_action_count);
    hash_into(h, entry.expected_choice_required);
    hash_into(h, entry.expected_choice_action_frontier_complete);
    hash_into(h, entry.expected_choice_action_generation_limit);
    h.add_u64(static_cast<u64>(entry.expected_choice_validation_source));
    hash_into(h, entry.expected_choice_validation_source_present);
    hash_into(h, entry.expected_choice_page_location_present);
    hash_into(h, entry.expected_choice_page_location_found);
    hash_into(h, entry.expected_choice_page_location_checked);
    hash_into(h, entry.expected_choice_page_schema_version);
    hash_into(h, entry.expected_choice_page_context_present);
    hash_into(h, entry.expected_choice_page_state_hash);
    hash_into(h, entry.expected_choice_page_choice_request_hash);
    hash_into(h, entry.expected_choice_page_requested_limit);
    hash_into(h, entry.expected_choice_page_effective_limit);
    hash_into(h, entry.expected_choice_page_cursor);
    hash_into(h, entry.expected_choice_action_cursor);
    hash_into(h, entry.expected_choice_page_index);
    hash_into(h, entry.expected_choice_page_next_cursor);
    hash_into(h, entry.expected_choice_page_actions_seen);
    hash_into(h, entry.expected_choice_page_scanned_pages);
    hash_into(h, entry.expected_choice_page_complete);
    hash_into(h, entry.expected_choice_page_count_present);
    hash_into(h, entry.expected_choice_page_total_actions_lower_bound);
    hash_into(h, entry.expected_choice_page_total_actions_exact);
    hash_into(h, entry.expected_choice_page_remaining_actions_lower_bound);
    hash_into(h, entry.expected_choice_page_hash);
    hash_into(h, entry.expected_choice_page_location_hash);
    hash_into(h, entry.expected_choice_queue_schema_version);
    hash_into(h, entry.expected_choice_queue_hash);
    hash_into(h, entry.expected_choice_queue_index);
    hash_into(h, entry.expected_choice_queue_size);
    hash_into(h, entry.expected_choice_queue_location_schema_version);
    hash_into(h, entry.expected_choice_queue_location_found);
    hash_into(h, entry.expected_choice_queue_location_checked);
    hash_into(h, entry.expected_choice_queue_location_hash);
    hash_into(h, entry.expected_action_schema_version);
    hash_into(h, entry.expected_action_hash);
    hash_into(h, entry.expected_state_schema_version);
    hash_into(h, entry.expected_state_hash_before);
    hash_into(h, entry.expected_state_hash_after);
    hash_into(h, entry.expected_applied);
}

} // namespace

std::uint64_t action_trace_entry_hash(const ActionTraceEntry& entry) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ActionTraceEntry.v1");
    hash_action_trace_entry_fields(h, entry);
    return h.value();
}

std::vector<ActionTraceEntry> export_action_trace(const GameState& game, bool applied_only) {
    std::vector<ActionTraceEntry> trace;
    trace.reserve(game.action_receipt_records.size());
    for (const auto& receipt : game.action_receipt_records) {
        if (applied_only && !receipt.applied) {
            continue;
        }
        trace.push_back(action_trace_entry_from_receipt_record(receipt));
    }
    return trace;
}

namespace {

[[nodiscard]] bool parse_u64_text(std::string_view text, u64& out) noexcept {
    if (text.empty()) {
        return false;
    }
    u64 value = 0;
    const auto* first = text.data();
    const auto* last = text.data() + text.size();
    const auto parsed = std::from_chars(first, last, value);
    if (parsed.ec != std::errc{} || parsed.ptr != last) {
        return false;
    }
    out = value;
    return true;
}

[[nodiscard]] bool parse_u32_text(std::string_view text, u32& out) noexcept {
    u64 value = 0;
    if (!parse_u64_text(text, value) || value > static_cast<u64>(UINT32_MAX)) {
        return false;
    }
    out = static_cast<u32>(value);
    return true;
}

[[nodiscard]] bool parse_bool_text(std::string_view text, bool& out) noexcept {
    if (text == "0") {
        out = false;
        return true;
    }
    if (text == "1") {
        out = true;
        return true;
    }
    return false;
}

[[nodiscard]] bool parse_action_kind_text(std::string_view text, ActionKind& out) noexcept {
    for (u32 raw = 0; raw < static_cast<u32>(ActionKind::Count); ++raw) {
        const auto kind = static_cast<ActionKind>(raw);
        if (text == to_string(kind)) {
            out = kind;
            return true;
        }
    }
    return false;
}

[[nodiscard]] bool parse_choice_request_kind_text(std::string_view text, ChoiceRequestKind& out) noexcept {
    for (u32 raw = 0; raw < static_cast<u32>(ChoiceRequestKind::Count); ++raw) {
        const auto kind = static_cast<ChoiceRequestKind>(raw);
        if (text == to_string(kind)) {
            out = kind;
            return true;
        }
    }
    return false;
}

[[nodiscard]] bool parse_legal_action_validation_source_text(std::string_view text, LegalActionValidationSource& out) noexcept {
    for (u32 raw = 0; raw < static_cast<u32>(LegalActionValidationSource::Count); ++raw) {
        const auto source = static_cast<LegalActionValidationSource>(raw);
        if (text == to_string(source)) {
            out = source;
            return true;
        }
    }
    return false;
}

[[nodiscard]] bool parse_target_kind_text(std::string_view text, TargetKind& out) noexcept {
    if (text == to_string(TargetKind::None)) {
        out = TargetKind::None;
        return true;
    }
    if (text == to_string(TargetKind::Player)) {
        out = TargetKind::Player;
        return true;
    }
    if (text == to_string(TargetKind::Object)) {
        out = TargetKind::Object;
        return true;
    }
    return false;
}

[[nodiscard]] bool parse_step_text(std::string_view text, Step& out) noexcept {
    for (u32 raw = 0; raw <= static_cast<u32>(Step::Cleanup); ++raw) {
        const auto step = static_cast<Step>(raw);
        if (text == to_string(step)) {
            out = step;
            return true;
        }
    }
    return false;
}

[[nodiscard]] bool parse_i32_text(std::string_view text, std::int32_t& out) noexcept {
    if (text.empty()) {
        return false;
    }
    std::int32_t value = 0;
    const auto* first = text.data();
    const auto* last = text.data() + text.size();
    const auto parsed = std::from_chars(first, last, value);
    if (parsed.ec != std::errc{} || parsed.ptr != last) {
        return false;
    }
    out = value;
    return true;
}

[[nodiscard]] bool parse_zone_text(std::string_view text, Zone& out) noexcept {
    for (u32 raw = 0; raw < static_cast<u32>(Zone::Count); ++raw) {
        const auto zone = static_cast<Zone>(raw);
        if (text == to_string(zone)) {
            out = zone;
            return true;
        }
    }
    return false;
}

[[nodiscard]] bool parse_paid_action_transaction_outcome_text(std::string_view text, PaidActionTransactionOutcome& out) noexcept {
    for (u32 raw = 0; raw < static_cast<u32>(PaidActionTransactionOutcome::Count); ++raw) {
        const auto outcome = static_cast<PaidActionTransactionOutcome>(raw);
        if (text == to_string(outcome)) {
            out = outcome;
            return true;
        }
    }
    return false;
}

using JournalFieldMap = std::unordered_map<std::string, std::string>;

[[nodiscard]] bool parse_journal_fields(std::string_view line, JournalFieldMap& out, std::string& error) {
    out.clear();
    std::istringstream fields{std::string(line)};
    std::string field;
    while (fields >> field) {
        const auto eq = field.find('=');
        if (eq == std::string::npos || eq == 0U) {
            error = "malformed field: " + field;
            return false;
        }
        const auto key = field.substr(0, eq);
        const auto value = field.substr(eq + 1U);
        if (!out.emplace(key, value).second) {
            error = "duplicate field: " + key;
            return false;
        }
    }
    if (out.empty()) {
        error = "missing fields";
        return false;
    }
    return true;
}

[[nodiscard]] const std::string* find_journal_field(const JournalFieldMap& fields, const std::string& key) noexcept {
    const auto it = fields.find(key);
    if (it == fields.end()) {
        return nullptr;
    }
    return &it->second;
}


[[nodiscard]] bool journal_field_is_one_of(std::string_view key, std::initializer_list<std::string_view> allowed) noexcept {
    for (const auto candidate : allowed) {
        if (key == candidate) {
            return true;
        }
    }
    return false;
}

[[nodiscard]] bool journal_field_has_prefix(std::string_view key, std::string_view prefix) noexcept {
    return key.size() >= prefix.size() && key.substr(0, prefix.size()) == prefix;
}

[[nodiscard]] bool is_paid_action_declaration_snapshot_field_suffix(std::string_view suffix) noexcept {
    return journal_field_is_one_of(suffix,
                                   {"sequence",
                                    "schema",
                                    "action",
                                    "player",
                                    "source",
                                    "stack_object",
                                    "definition",
                                    "source_zone_before",
                                    "source_zone_change_index_before",
                                    "stack_zone_change_index",
                                    "stack_enter_record",
                                    "stack_entered",
                                    "choices_locked",
                                    "ability",
                                    "loyalty_delta",
                                    "mode",
                                    "mode_hash",
                                    "target_mask",
                                    "target_count",
                                    "targets",
                                    "target_hash",
                                    "mana_cost",
                                    "sacrifice_count",
                                    "sacrifice_type_mask",
                                    "discard_count",
                                    "life_amount",
                                    "return_count",
                                    "return_type_mask",
                                    "return_require_tapped",
                                    "total_cost_locked",
                                    "mana_cost_required",
                                    "tap_cost_required",
                                    "sacrifice_cost_required",
                                    "discard_cost_required",
                                    "life_cost_required",
                                    "return_cost_required",
                                    "loyalty_cost_required",
                                    "modal_choice_declared",
                                    "target_choice_declared",
                                    "payment_attempted",
                                    "first_payment",
                                    "last_payment",
                                    "sacrifice_payment_first",
                                    "sacrifice_payment_count",
                                    "sacrifice_payment_hash",
                                    "discard_payment_first",
                                    "discard_payment_count",
                                    "discard_payment_hash",
                                    "tap_payment_first",
                                    "tap_payment_count",
                                    "tap_payment_hash",
                                    "life_payment_first",
                                    "life_payment_count",
                                    "life_payment_hash",
                                    "return_payment_first",
                                    "return_payment_count",
                                    "return_payment_hash",
                                    "loyalty_payment_first",
                                    "loyalty_payment_count",
                                    "loyalty_payment_hash",
                                    "placement_index",
                                    "declaration_hash",
                                    "recomputed_hash"});
}

[[nodiscard]] bool check_no_unknown_journal_header_fields(const JournalFieldMap& fields,
                                                          u32 schema_version,
                                                          std::string& error) {
    for (const auto& [key, value] : fields) {
        (void)value;
        const bool known_v1 = journal_field_is_one_of(key,
                                                      {"record_count",
                                                       "declaration_record_count",
                                                       "stack_placement_record_count",
                                                       "journal_hash",
                                                       "state_hash"});
        const bool known_v2 = schema_version >= 2U && key == "record_payload_hash";
        const bool known_v3 = schema_version >= 3U &&
            journal_field_is_one_of(key, {"first_transaction_sequence", "last_transaction_sequence"});
        if (!known_v1 && !known_v2 && !known_v3) {
            error = "unknown header field: " + key;
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool check_no_unknown_paid_action_record_fields(const JournalFieldMap& fields,
                                                              bool committed_snapshot_present,
                                                              bool speculative_snapshot_present,
                                                              std::string& error) {
    for (const auto& [key, value] : fields) {
        (void)value;
        if (journal_field_is_one_of(key,
                                    {"index",
                                     "sequence",
                                     "schema",
                                     "outcome",
                                     "action",
                                     "player",
                                     "source",
                                     "stack_object",
                                     "stack_placement",
                                     "declaration_index",
                                     "declaration_hash",
                                     "stack_entered",
                                     "choices_locked",
                                     "first_paid_event",
                                     "last_paid_event",
                                     "mana_plan_first",
                                     "mana_plan_count",
                                     "mana_change_first",
                                     "mana_change_count",
                                     "counter_change_first",
                                     "counter_change_count",
                                     "zone_change_first",
                                     "zone_change_count",
                                     "sacrifice_payment_first",
                                     "sacrifice_payment_count",
                                     "sacrifice_payment_hash",
                                     "discard_payment_first",
                                     "discard_payment_count",
                                     "discard_payment_hash",
                                     "tap_payment_first",
                                     "tap_payment_count",
                                     "tap_payment_hash",
                                     "life_payment_first",
                                     "life_payment_count",
                                     "life_payment_hash",
                                     "return_payment_first",
                                     "return_payment_count",
                                     "return_payment_hash",
                                     "loyalty_payment_first",
                                     "loyalty_payment_count",
                                     "loyalty_payment_hash",
                                     "speculative_event_count",
                                     "speculative_event_record_count",
                                     "speculative_stack_placement_count",
                                     "speculative_declaration_count",
                                     "speculative_declaration_sequence",
                                     "speculative_declaration_hash",
                                     "speculative_first_payment",
                                     "speculative_last_payment",
                                     "physical_before",
                                     "physical_after",
                                     "next_event_before",
                                     "speculative_next_event_after",
                                     "committed",
                                     "rolled_back",
                                     "physical_state_preserved_on_rollback",
                                     "choices_before_payment",
                                     "payments_before_placement",
                                     "placement_before_transaction",
                                     "transaction_hash",
                                     "recomputed_transaction_hash",
                                     "committed_snapshot_present",
                                     "speculative_snapshot_present"})) {
            continue;
        }
        constexpr std::string_view committed_prefix = "committed_snapshot.";
        if (journal_field_has_prefix(key, committed_prefix)) {
            const auto suffix = std::string_view(key).substr(committed_prefix.size());
            if (committed_snapshot_present && is_paid_action_declaration_snapshot_field_suffix(suffix)) {
                continue;
            }
            error = committed_snapshot_present ? "unknown committed snapshot field: " + key
                                               : "unexpected committed snapshot field: " + key;
            return false;
        }
        constexpr std::string_view speculative_prefix = "speculative_snapshot.";
        if (journal_field_has_prefix(key, speculative_prefix)) {
            const auto suffix = std::string_view(key).substr(speculative_prefix.size());
            if (speculative_snapshot_present && is_paid_action_declaration_snapshot_field_suffix(suffix)) {
                continue;
            }
            error = speculative_snapshot_present ? "unknown speculative snapshot field: " + key
                                                 : "unexpected speculative snapshot field: " + key;
            return false;
        }
        error = "unknown record field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_required_u64_field(const JournalFieldMap& fields, const std::string& key, u64& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_u64_text(*value, out)) {
        error = "invalid u64 field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_required_u32_field(const JournalFieldMap& fields, const std::string& key, u32& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_u32_text(*value, out)) {
        error = "invalid u32 field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_required_i32_field(const JournalFieldMap& fields, const std::string& key, std::int32_t& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_i32_text(*value, out)) {
        error = "invalid i32 field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_required_bool_field(const JournalFieldMap& fields, const std::string& key, bool& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_bool_text(*value, out)) {
        error = "invalid bool field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_required_action_kind_field(const JournalFieldMap& fields, const std::string& key, ActionKind& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_action_kind_text(*value, out)) {
        error = "invalid action kind field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_required_zone_field(const JournalFieldMap& fields, const std::string& key, Zone& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_zone_text(*value, out)) {
        error = "invalid zone field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_required_paid_action_outcome_field(const JournalFieldMap& fields, const std::string& key, PaidActionTransactionOutcome& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_paid_action_transaction_outcome_text(*value, out)) {
        error = "invalid paid-action transaction outcome field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] std::vector<std::string_view> split_journal_delimited_fields(std::string_view text, char delim) {
    std::vector<std::string_view> parts;
    std::size_t begin = 0;
    while (begin <= text.size()) {
        const std::size_t end = text.find(delim, begin);
        if (end == std::string_view::npos) {
            parts.push_back(text.substr(begin));
            break;
        }
        parts.push_back(text.substr(begin, end - begin));
        begin = end + 1U;
    }
    return parts;
}

[[nodiscard]] bool parse_paid_action_mana_cost_text(std::string_view text, ManaCost& out) {
    const auto parts = split_journal_delimited_fields(text, ':');
    if (parts.size() != 7U) {
        return false;
    }
    ManaCost parsed{};
    return parse_u32_text(parts[0], parsed.generic) &&
           parse_u32_text(parts[1], parsed.white) &&
           parse_u32_text(parts[2], parsed.blue) &&
           parse_u32_text(parts[3], parsed.black) &&
           parse_u32_text(parts[4], parsed.red) &&
           parse_u32_text(parts[5], parsed.green) &&
           parse_u32_text(parts[6], parsed.colorless) &&
           (out = parsed, true);
}

[[nodiscard]] bool parse_required_mana_cost_field(const JournalFieldMap& fields, const std::string& key, ManaCost& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_paid_action_mana_cost_text(*value, out)) {
        error = "invalid mana cost field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_paid_action_snapshot_targets_text(std::string_view text, std::vector<TargetRef>& out) {
    out.clear();
    if (text == "-") {
        return true;
    }
    const auto parts = split_journal_delimited_fields(text, ',');
    if (parts.empty()) {
        return false;
    }
    std::vector<TargetRef> parsed;
    parsed.reserve(parts.size());
    for (const auto part : parts) {
        if (part.empty()) {
            return false;
        }
        const auto target_parts = split_journal_delimited_fields(part, ':');
        if (target_parts.size() != 4U) {
            return false;
        }
        TargetKind kind = TargetKind::None;
        u32 player_id = 0;
        u32 object_id = 0;
        u64 zone_change_index = 0;
        if (!parse_target_kind_text(target_parts[0], kind) ||
            !parse_u32_text(target_parts[1], player_id) ||
            !parse_u32_text(target_parts[2], object_id) ||
            !parse_u64_text(target_parts[3], zone_change_index)) {
            return false;
        }
        if (kind == TargetKind::Player && player_id == 0U) {
            return false;
        }
        if (kind == TargetKind::Object && object_id == 0U) {
            return false;
        }
        parsed.push_back(TargetRef{.kind = kind, .player = PlayerId{player_id}, .object = ObjectId{object_id}, .object_zone_change_index = zone_change_index});
    }
    out = std::move(parsed);
    return true;
}

[[nodiscard]] bool parse_required_targets_field(const JournalFieldMap& fields, const std::string& key, std::vector<TargetRef>& out, std::string& error) {
    const auto* value = find_journal_field(fields, key);
    if (value == nullptr) {
        error = "missing field: " + key;
        return false;
    }
    if (!parse_paid_action_snapshot_targets_text(*value, out)) {
        error = "invalid target list field: " + key;
        return false;
    }
    return true;
}

[[nodiscard]] bool parse_paid_action_declaration_snapshot_fields(const JournalFieldMap& fields,
                                                                const std::string& prefix,
                                                                PaidActionDeclarationRecord& record,
                                                                u64& exported_recomputed_hash,
                                                                std::string& error) {
    const auto key = [&prefix](std::string_view suffix) { return prefix + "." + std::string(suffix); };
    return parse_required_u64_field(fields, key("sequence"), record.sequence, error) &&
           parse_required_u32_field(fields, key("schema"), record.schema_version, error) &&
           parse_required_action_kind_field(fields, key("action"), record.action_kind, error) &&
           parse_required_u32_field(fields, key("player"), record.player.value, error) &&
           parse_required_u32_field(fields, key("source"), record.source_object.value, error) &&
           parse_required_u32_field(fields, key("stack_object"), record.stack_object.value, error) &&
           parse_required_u32_field(fields, key("definition"), record.definition_index, error) &&
           parse_required_zone_field(fields, key("source_zone_before"), record.source_zone_before, error) &&
           parse_required_u64_field(fields, key("source_zone_change_index_before"), record.source_zone_change_index_before, error) &&
           parse_required_u64_field(fields, key("stack_zone_change_index"), record.stack_zone_change_index, error) &&
           parse_required_u32_field(fields, key("stack_enter_record"), record.stack_enter_zone_change_record_index, error) &&
           parse_required_u64_field(fields, key("stack_entered"), record.stack_object_entered_sequence, error) &&
           parse_required_u64_field(fields, key("choices_locked"), record.choices_locked_sequence, error) &&
           parse_required_u32_field(fields, key("ability"), record.ability_index, error) &&
           parse_required_i32_field(fields, key("loyalty_delta"), record.loyalty_cost_delta, error) &&
           parse_required_u32_field(fields, key("mode"), record.declared_mode_index, error) &&
           parse_required_u64_field(fields, key("mode_hash"), record.declared_mode_contract_hash, error) &&
           parse_required_u32_field(fields, key("target_mask"), record.target_mask, error) &&
           parse_required_u32_field(fields, key("target_count"), record.target_count, error) &&
           parse_required_targets_field(fields, key("targets"), record.declared_targets, error) &&
           parse_required_u64_field(fields, key("target_hash"), record.declared_target_set_hash, error) &&
           parse_required_mana_cost_field(fields, key("mana_cost"), record.total_mana_cost, error) &&
           parse_required_u32_field(fields, key("sacrifice_count"), record.sacrifice_cost.count, error) &&
           parse_required_u32_field(fields, key("sacrifice_type_mask"), record.sacrifice_cost.required_type_mask, error) &&
           parse_required_u32_field(fields, key("discard_count"), record.discard_cost.count, error) &&
           parse_required_u32_field(fields, key("life_amount"), record.life_cost.amount, error) &&
           parse_required_u32_field(fields, key("return_count"), record.return_cost.count, error) &&
           parse_required_u32_field(fields, key("return_type_mask"), record.return_cost.required_type_mask, error) &&
           parse_required_bool_field(fields, key("return_require_tapped"), record.return_cost.require_tapped, error) &&
           parse_required_bool_field(fields, key("total_cost_locked"), record.total_cost_locked, error) &&
           parse_required_bool_field(fields, key("mana_cost_required"), record.mana_cost_required, error) &&
           parse_required_bool_field(fields, key("tap_cost_required"), record.tap_cost_required, error) &&
           parse_required_bool_field(fields, key("sacrifice_cost_required"), record.sacrifice_cost_required, error) &&
           parse_required_bool_field(fields, key("discard_cost_required"), record.discard_cost_required, error) &&
           parse_required_bool_field(fields, key("life_cost_required"), record.life_cost_required, error) &&
           parse_required_bool_field(fields, key("return_cost_required"), record.return_cost_required, error) &&
           parse_required_bool_field(fields, key("loyalty_cost_required"), record.loyalty_cost_required, error) &&
           parse_required_bool_field(fields, key("modal_choice_declared"), record.modal_choice_declared, error) &&
           parse_required_bool_field(fields, key("target_choice_declared"), record.target_choice_declared, error) &&
           parse_required_bool_field(fields, key("payment_attempted"), record.payment_attempted, error) &&
           parse_required_u64_field(fields, key("first_payment"), record.first_payment_event_sequence, error) &&
           parse_required_u64_field(fields, key("last_payment"), record.last_payment_event_sequence, error) &&
           parse_required_u32_field(fields, key("sacrifice_payment_first"), record.first_sacrifice_cost_payment_record_index, error) &&
           parse_required_u32_field(fields, key("sacrifice_payment_count"), record.sacrifice_cost_payment_record_count, error) &&
           parse_required_u64_field(fields, key("sacrifice_payment_hash"), record.sacrifice_cost_payment_hash, error) &&
           parse_required_u32_field(fields, key("discard_payment_first"), record.first_discard_cost_payment_record_index, error) &&
           parse_required_u32_field(fields, key("discard_payment_count"), record.discard_cost_payment_record_count, error) &&
           parse_required_u64_field(fields, key("discard_payment_hash"), record.discard_cost_payment_hash, error) &&
           parse_required_u32_field(fields, key("tap_payment_first"), record.first_tap_cost_payment_record_index, error) &&
           parse_required_u32_field(fields, key("tap_payment_count"), record.tap_cost_payment_record_count, error) &&
           parse_required_u64_field(fields, key("tap_payment_hash"), record.tap_cost_payment_hash, error) &&
           parse_required_u32_field(fields, key("life_payment_first"), record.first_life_cost_payment_record_index, error) &&
           parse_required_u32_field(fields, key("life_payment_count"), record.life_cost_payment_record_count, error) &&
           parse_required_u64_field(fields, key("life_payment_hash"), record.life_cost_payment_hash, error) &&
           parse_required_u32_field(fields, key("return_payment_first"), record.first_return_cost_payment_record_index, error) &&
           parse_required_u32_field(fields, key("return_payment_count"), record.return_cost_payment_record_count, error) &&
           parse_required_u64_field(fields, key("return_payment_hash"), record.return_cost_payment_hash, error) &&
           parse_required_u32_field(fields, key("loyalty_payment_first"), record.first_loyalty_cost_payment_record_index, error) &&
           parse_required_u32_field(fields, key("loyalty_payment_count"), record.loyalty_cost_payment_record_count, error) &&
           parse_required_u64_field(fields, key("loyalty_payment_hash"), record.loyalty_cost_payment_hash, error) &&
           parse_required_u32_field(fields, key("placement_index"), record.stack_placement_record_index, error) &&
           parse_required_u64_field(fields, key("declaration_hash"), record.declaration_hash, error) &&
           parse_required_u64_field(fields, key("recomputed_hash"), exported_recomputed_hash, error);
}


[[nodiscard]] std::vector<std::string_view> split_trace_fields(std::string_view text, char delim) {
    std::vector<std::string_view> parts;
    std::size_t begin = 0;
    while (begin <= text.size()) {
        const std::size_t end = text.find(delim, begin);
        if (end == std::string_view::npos) {
            parts.push_back(text.substr(begin));
            break;
        }
        parts.push_back(text.substr(begin, end - begin));
        begin = end + 1U;
    }
    return parts;
}

[[nodiscard]] std::string serialize_trace_target(TargetRef target) {
    std::ostringstream out;
    out << to_string(target.kind) << ':'
        << target.player.value << ':'
        << target.object.value << ':'
        << target.object_zone_change_index;
    return out.str();
}

[[nodiscard]] std::string serialize_trace_targets(const std::vector<TargetRef>& targets) {
    if (targets.empty()) {
        return "-";
    }
    std::ostringstream out;
    for (std::size_t i = 0; i < targets.size(); ++i) {
        if (i != 0U) {
            out << ',';
        }
        out << serialize_trace_target(targets[i]);
    }
    return out.str();
}

[[nodiscard]] std::string serialize_trace_u32_list(const std::vector<u32>& values) {
    if (values.empty()) {
        return "-";
    }
    std::ostringstream out;
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0U) {
            out << ',';
        }
        out << values[i];
    }
    return out.str();
}

[[nodiscard]] bool parse_trace_u32_list(std::string_view text, std::vector<u32>& out) {
    out.clear();
    if (text == "-") {
        return true;
    }
    const auto parts = split_trace_fields(text, ',');
    if (parts.empty()) {
        return false;
    }
    out.reserve(parts.size());
    for (const auto part : parts) {
        if (part.empty()) {
            return false;
        }
        u32 value = 0U;
        if (!parse_u32_text(part, value) || value == 0U) {
            return false;
        }
        out.push_back(value);
    }
    return true;
}

[[nodiscard]] bool parse_trace_target(std::string_view text, TargetRef& out) {
    const auto parts = split_trace_fields(text, ':');
    if (parts.size() != 4U) {
        return false;
    }
    TargetKind kind = TargetKind::None;
    u32 player_id = 0;
    u32 object_id = 0;
    u64 zone_change_index = 0;
    if (!parse_target_kind_text(parts[0], kind) ||
        !parse_u32_text(parts[1], player_id) ||
        !parse_u32_text(parts[2], object_id) ||
        !parse_u64_text(parts[3], zone_change_index)) {
        return false;
    }
    if (kind == TargetKind::Player && player_id == 0U) {
        return false;
    }
    if (kind == TargetKind::Object && object_id == 0U) {
        return false;
    }
    out = TargetRef{.kind = kind, .player = PlayerId{player_id}, .object = ObjectId{object_id}, .object_zone_change_index = zone_change_index};
    return true;
}

[[nodiscard]] bool parse_trace_targets(std::string_view text, LegalAction& action) {
    action.target = TargetRef{};
    action.targets.clear();
    if (text == "-") {
        return true;
    }
    const auto parts = split_trace_fields(text, ',');
    if (parts.empty()) {
        return false;
    }
    std::vector<TargetRef> parsed;
    parsed.reserve(parts.size());
    for (const auto part : parts) {
        if (part.empty()) {
            return false;
        }
        TargetRef target{};
        if (!parse_trace_target(part, target)) {
            return false;
        }
        parsed.push_back(target);
    }
    action.targets = parsed;
    if (parsed.size() == 1U) {
        action.target = parsed.front();
    }
    return true;
}

[[nodiscard]] char hex_digit(unsigned value) noexcept {
    static constexpr char digits[] = "0123456789abcdef";
    return digits[value & 0xFU];
}

[[nodiscard]] std::string hex_encode(std::string_view value) {
    std::string out;
    out.reserve(value.size() * 2U);
    for (const char raw : value) {
        const auto ch = static_cast<unsigned char>(raw);
        out.push_back(hex_digit(static_cast<unsigned>(ch >> 4U)));
        out.push_back(hex_digit(static_cast<unsigned>(ch)));
    }
    return out;
}

[[nodiscard]] bool from_hex_digit(char ch, unsigned& out) noexcept {
    if (ch >= '0' && ch <= '9') {
        out = static_cast<unsigned>(ch - '0');
        return true;
    }
    if (ch >= 'a' && ch <= 'f') {
        out = static_cast<unsigned>(ch - 'a' + 10);
        return true;
    }
    if (ch >= 'A' && ch <= 'F') {
        out = static_cast<unsigned>(ch - 'A' + 10);
        return true;
    }
    return false;
}

[[nodiscard]] bool hex_decode(std::string_view text, std::string& out) {
    if ((text.size() % 2U) != 0U) {
        return false;
    }
    std::string decoded;
    decoded.reserve(text.size() / 2U);
    for (std::size_t i = 0; i < text.size(); i += 2U) {
        unsigned hi = 0;
        unsigned lo = 0;
        if (!from_hex_digit(text[i], hi) || !from_hex_digit(text[i + 1U], lo)) {
            return false;
        }
        decoded.push_back(static_cast<char>((hi << 4U) | lo));
    }
    out = std::move(decoded);
    return true;
}

struct StateCoreSnapshotWriter {
    std::ostringstream out;

    void line(std::string_view name, std::string_view value) {
        out << name << '=' << value << '\n';
    }

    void u32_value(std::string_view name, u32 value) { out << name << '=' << value << '\n'; }
    void u64_value(std::string_view name, u64 value) { out << name << '=' << value << '\n'; }
    void i32_value(std::string_view name, std::int32_t value) { out << name << '=' << value << '\n'; }
    void bool_value(std::string_view name, bool value) { out << name << '=' << (value ? 1 : 0) << '\n'; }
    void string_value(std::string_view name, std::string_view value) {
        out << name << "=hex:" << hex_encode(value) << '\n';
    }
};

struct StateCoreSnapshotReader {
    explicit StateCoreSnapshotReader(std::string_view text) : input(std::string(text)) {}

    std::istringstream input;
    u64 line_number = 0;
    std::string line;
    std::string error;

    [[nodiscard]] bool fail(std::string message) {
        if (error.empty()) {
            error = std::move(message);
        }
        return false;
    }

    [[nodiscard]] bool read_raw_line() {
        if (!std::getline(input, line)) {
            ++line_number;
            return fail("unexpected end of StateCore snapshot");
        }
        ++line_number;
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        return true;
    }

    [[nodiscard]] bool read_header(std::string_view expected) {
        if (!read_raw_line()) {
            return false;
        }
        if (line != expected) {
            return fail("missing " + std::string(expected) + " header");
        }
        return true;
    }

    [[nodiscard]] bool read_value(std::string_view name, std::string& out) {
        if (!read_raw_line()) {
            return false;
        }
        const std::string prefix = std::string(name) + '=';
        if (line.rfind(prefix, 0U) != 0U) {
            return fail("expected snapshot field " + std::string(name));
        }
        out = line.substr(prefix.size());
        return true;
    }

    [[nodiscard]] bool read_u64(std::string_view name, u64& out) {
        std::string value;
        if (!read_value(name, value) || !parse_u64_text(value, out)) {
            return fail("invalid u64 snapshot field " + std::string(name));
        }
        return true;
    }

    [[nodiscard]] bool read_u32(std::string_view name, u32& out) {
        std::string value;
        if (!read_value(name, value) || !parse_u32_text(value, out)) {
            return fail("invalid u32 snapshot field " + std::string(name));
        }
        return true;
    }

    [[nodiscard]] bool read_i32(std::string_view name, std::int32_t& out) {
        std::string value;
        if (!read_value(name, value) || !parse_i32_text(value, out)) {
            return fail("invalid i32 snapshot field " + std::string(name));
        }
        return true;
    }

    [[nodiscard]] bool read_bool(std::string_view name, bool& out) {
        std::string value;
        if (!read_value(name, value) || !parse_bool_text(value, out)) {
            return fail("invalid bool snapshot field " + std::string(name));
        }
        return true;
    }

    [[nodiscard]] bool read_string(std::string_view name, std::string& out) {
        std::string value;
        if (!read_value(name, value)) {
            return false;
        }
        constexpr std::string_view marker = "hex:";
        if (value.rfind(marker, 0U) != 0U || !hex_decode(std::string_view(value).substr(marker.size()), out)) {
            return fail("invalid string snapshot field " + std::string(name));
        }
        return true;
    }

    [[nodiscard]] bool finish() {
        while (std::getline(input, line)) {
            ++line_number;
            if (!line.empty() && line.back() == '\r') {
                line.pop_back();
            }
            if (!line.empty()) {
                return fail("unexpected trailing StateCore snapshot field");
            }
        }
        return true;
    }
};

constexpr u64 max_snapshot_vector_size = 1'000'000ULL;

[[nodiscard]] std::string field_name(std::string_view prefix, std::string_view suffix) {
    std::string out(prefix);
    out.push_back('.');
    out.append(suffix);
    return out;
}

[[nodiscard]] std::string indexed_prefix(std::string_view prefix, std::size_t index) {
    std::string out(prefix);
    out.push_back('.');
    out.append(std::to_string(index));
    return out;
}

template <typename Enum>
void write_enum_snapshot(StateCoreSnapshotWriter& writer, std::string_view name, Enum value) {
    writer.u32_value(name, static_cast<u32>(value));
}

template <typename Enum>
[[nodiscard]] bool read_enum_snapshot(StateCoreSnapshotReader& reader, std::string_view name, Enum& out, u32 max_exclusive) {
    u32 raw = 0;
    if (!reader.read_u32(name, raw)) {
        return false;
    }
    if (raw >= max_exclusive) {
        return reader.fail("snapshot enum field out of range " + std::string(name));
    }
    out = static_cast<Enum>(raw);
    return true;
}

void write_player_id_snapshot(StateCoreSnapshotWriter& writer, std::string_view name, PlayerId id) {
    writer.u32_value(name, id.value);
}

[[nodiscard]] bool read_player_id_snapshot(StateCoreSnapshotReader& reader, std::string_view name, PlayerId& id) {
    u32 raw = 0;
    if (!reader.read_u32(name, raw)) {
        return false;
    }
    id = PlayerId{raw};
    return true;
}

void write_object_id_snapshot(StateCoreSnapshotWriter& writer, std::string_view name, ObjectId id) {
    writer.u32_value(name, id.value);
}

[[nodiscard]] bool read_object_id_snapshot(StateCoreSnapshotReader& reader, std::string_view name, ObjectId& id) {
    u32 raw = 0;
    if (!reader.read_u32(name, raw)) {
        return false;
    }
    id = ObjectId{raw};
    return true;
}

void write_mana_pool_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const ManaPool& value) {
    writer.u32_value(field_name(prefix, "white"), value.white);
    writer.u32_value(field_name(prefix, "blue"), value.blue);
    writer.u32_value(field_name(prefix, "black"), value.black);
    writer.u32_value(field_name(prefix, "red"), value.red);
    writer.u32_value(field_name(prefix, "green"), value.green);
    writer.u32_value(field_name(prefix, "colorless"), value.colorless);
}

[[nodiscard]] bool read_mana_pool_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, ManaPool& value) {
    return reader.read_u32(field_name(prefix, "white"), value.white) &&
           reader.read_u32(field_name(prefix, "blue"), value.blue) &&
           reader.read_u32(field_name(prefix, "black"), value.black) &&
           reader.read_u32(field_name(prefix, "red"), value.red) &&
           reader.read_u32(field_name(prefix, "green"), value.green) &&
           reader.read_u32(field_name(prefix, "colorless"), value.colorless);
}

void write_mana_cost_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const ManaCost& value) {
    writer.u32_value(field_name(prefix, "generic"), value.generic);
    writer.u32_value(field_name(prefix, "white"), value.white);
    writer.u32_value(field_name(prefix, "blue"), value.blue);
    writer.u32_value(field_name(prefix, "black"), value.black);
    writer.u32_value(field_name(prefix, "red"), value.red);
    writer.u32_value(field_name(prefix, "green"), value.green);
    writer.u32_value(field_name(prefix, "colorless"), value.colorless);
}

[[nodiscard]] bool read_mana_cost_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, ManaCost& value) {
    return reader.read_u32(field_name(prefix, "generic"), value.generic) &&
           reader.read_u32(field_name(prefix, "white"), value.white) &&
           reader.read_u32(field_name(prefix, "blue"), value.blue) &&
           reader.read_u32(field_name(prefix, "black"), value.black) &&
           reader.read_u32(field_name(prefix, "red"), value.red) &&
           reader.read_u32(field_name(prefix, "green"), value.green) &&
           reader.read_u32(field_name(prefix, "colorless"), value.colorless);
}

void write_counter_set_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const CounterSet& value) {
    writer.u32_value(field_name(prefix, "plus_one_plus_one"), value.plus_one_plus_one);
    writer.u32_value(field_name(prefix, "minus_one_minus_one"), value.minus_one_minus_one);
    writer.u32_value(field_name(prefix, "loyalty"), value.loyalty);
    writer.u32_value(field_name(prefix, "defense"), value.defense);
    writer.u32_value(field_name(prefix, "charge"), value.charge);
}

[[nodiscard]] bool read_counter_set_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, CounterSet& value) {
    return reader.read_u32(field_name(prefix, "plus_one_plus_one"), value.plus_one_plus_one) &&
           reader.read_u32(field_name(prefix, "minus_one_minus_one"), value.minus_one_minus_one) &&
           reader.read_u32(field_name(prefix, "loyalty"), value.loyalty) &&
           reader.read_u32(field_name(prefix, "defense"), value.defense) &&
           reader.read_u32(field_name(prefix, "charge"), value.charge);
}

void write_target_ref_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, TargetRef value) {
    write_enum_snapshot(writer, field_name(prefix, "kind"), value.kind);
    write_player_id_snapshot(writer, field_name(prefix, "player"), value.player);
    write_object_id_snapshot(writer, field_name(prefix, "object"), value.object);
    writer.u64_value(field_name(prefix, "object_zone_change_index"), value.object_zone_change_index);
}

[[nodiscard]] bool read_target_ref_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, TargetRef& value) {
    return read_enum_snapshot(reader, field_name(prefix, "kind"), value.kind, 3U) &&
           read_player_id_snapshot(reader, field_name(prefix, "player"), value.player) &&
           read_object_id_snapshot(reader, field_name(prefix, "object"), value.object) &&
           reader.read_u64(field_name(prefix, "object_zone_change_index"), value.object_zone_change_index);
}

template <typename T, typename WriteValue>
void write_vector_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const std::vector<T>& values, WriteValue write_value) {
    writer.u64_value(field_name(prefix, "size"), static_cast<u64>(values.size()));
    for (std::size_t i = 0; i < values.size(); ++i) {
        write_value(writer, indexed_prefix(prefix, i), values[i]);
    }
}

template <typename T, typename ReadValue>
[[nodiscard]] bool read_vector_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, std::vector<T>& values, ReadValue read_value) {
    u64 size = 0;
    if (!reader.read_u64(field_name(prefix, "size"), size)) {
        return false;
    }
    if (size > max_snapshot_vector_size) {
        return reader.fail("snapshot vector too large " + std::string(prefix));
    }
    std::vector<T> parsed;
    parsed.reserve(static_cast<std::size_t>(size));
    for (u64 i = 0; i < size; ++i) {
        T value{};
        if (!read_value(reader, indexed_prefix(prefix, static_cast<std::size_t>(i)), value)) {
            return false;
        }
        parsed.push_back(std::move(value));
    }
    values = std::move(parsed);
    return true;
}

void write_string_vector_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const std::vector<std::string>& values) {
    write_vector_snapshot(writer, prefix, values, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const std::string& value) {
        w.string_value(item_prefix, value);
    });
}

[[nodiscard]] bool read_string_vector_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, std::vector<std::string>& values) {
    return read_vector_snapshot(reader, prefix, values, [](StateCoreSnapshotReader& r, const std::string& item_prefix, std::string& value) {
        return r.read_string(item_prefix, value);
    });
}

void write_object_id_vector_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const std::vector<ObjectId>& values) {
    write_vector_snapshot(writer, prefix, values, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, ObjectId value) {
        write_object_id_snapshot(w, item_prefix, value);
    });
}

[[nodiscard]] bool read_object_id_vector_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, std::vector<ObjectId>& values) {
    return read_vector_snapshot(reader, prefix, values, [](StateCoreSnapshotReader& r, const std::string& item_prefix, ObjectId& value) {
        return read_object_id_snapshot(r, item_prefix, value);
    });
}

void write_player_id_vector_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const std::vector<PlayerId>& values) {
    write_vector_snapshot(writer, prefix, values, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, PlayerId value) {
        write_player_id_snapshot(w, item_prefix, value);
    });
}

[[nodiscard]] bool read_player_id_vector_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, std::vector<PlayerId>& values) {
    return read_vector_snapshot(reader, prefix, values, [](StateCoreSnapshotReader& r, const std::string& item_prefix, PlayerId& value) {
        return read_player_id_snapshot(r, item_prefix, value);
    });
}

void write_target_ref_vector_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const std::vector<TargetRef>& values) {
    write_vector_snapshot(writer, prefix, values, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, TargetRef value) {
        write_target_ref_snapshot(w, item_prefix, value);
    });
}

[[nodiscard]] bool read_target_ref_vector_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, std::vector<TargetRef>& values) {
    return read_vector_snapshot(reader, prefix, values, [](StateCoreSnapshotReader& r, const std::string& item_prefix, TargetRef& value) {
        return read_target_ref_snapshot(r, item_prefix, value);
    });
}

void write_trigger_definition_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const TriggerDefinition& value) {
    write_enum_snapshot(writer, field_name(prefix, "event"), value.event);
    write_enum_snapshot(writer, field_name(prefix, "effect_kind"), value.effect_kind);
    writer.u32_value(field_name(prefix, "effect_amount"), value.effect_amount);
    write_enum_snapshot(writer, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind);
    writer.u32_value(field_name(prefix, "target_mask"), value.target_mask);
    writer.u32_value(field_name(prefix, "target_count"), value.target_count);
    writer.u32_value(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
    writer.bool_value(field_name(prefix, "exclude_source"), value.exclude_source);
}

[[nodiscard]] bool read_trigger_definition_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, TriggerDefinition& value) {
    return read_enum_snapshot(reader, field_name(prefix, "event"), value.event, static_cast<u32>(TriggerEventKind::Count)) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_kind"), value.effect_kind, static_cast<u32>(EffectKind::Count)) &&
           reader.read_u32(field_name(prefix, "effect_amount"), value.effect_amount) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind, static_cast<u32>(CounterKind::Count)) &&
           reader.read_u32(field_name(prefix, "target_mask"), value.target_mask) &&
           reader.read_u32(field_name(prefix, "target_count"), value.target_count) &&
           reader.read_u32(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index) &&
           reader.read_bool(field_name(prefix, "exclude_source"), value.exclude_source);
}

void write_loyalty_ability_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const LoyaltyAbilityDefinition& value) {
    writer.i32_value(field_name(prefix, "cost"), value.cost);
    write_enum_snapshot(writer, field_name(prefix, "effect_kind"), value.effect_kind);
    writer.u32_value(field_name(prefix, "effect_amount"), value.effect_amount);
    write_enum_snapshot(writer, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind);
    writer.u32_value(field_name(prefix, "target_mask"), value.target_mask);
    writer.u32_value(field_name(prefix, "target_count"), value.target_count);
    writer.u32_value(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
}

[[nodiscard]] bool read_loyalty_ability_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, LoyaltyAbilityDefinition& value) {
    return reader.read_i32(field_name(prefix, "cost"), value.cost) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_kind"), value.effect_kind, static_cast<u32>(EffectKind::Count)) &&
           reader.read_u32(field_name(prefix, "effect_amount"), value.effect_amount) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind, static_cast<u32>(CounterKind::Count)) &&
           reader.read_u32(field_name(prefix, "target_mask"), value.target_mask) &&
           reader.read_u32(field_name(prefix, "target_count"), value.target_count) &&
           reader.read_u32(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
}

void write_spell_mode_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const SpellModeDefinition& value) {
    writer.string_value(field_name(prefix, "name"), value.name);
    write_enum_snapshot(writer, field_name(prefix, "effect_kind"), value.effect_kind);
    writer.u32_value(field_name(prefix, "effect_amount"), value.effect_amount);
    write_enum_snapshot(writer, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind);
    writer.u32_value(field_name(prefix, "target_mask"), value.target_mask);
    writer.u32_value(field_name(prefix, "target_count"), value.target_count);
    writer.u32_value(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
}

[[nodiscard]] bool read_spell_mode_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, SpellModeDefinition& value) {
    return reader.read_string(field_name(prefix, "name"), value.name) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_kind"), value.effect_kind, static_cast<u32>(EffectKind::Count)) &&
           reader.read_u32(field_name(prefix, "effect_amount"), value.effect_amount) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind, static_cast<u32>(CounterKind::Count)) &&
           reader.read_u32(field_name(prefix, "target_mask"), value.target_mask) &&
           reader.read_u32(field_name(prefix, "target_count"), value.target_count) &&
           reader.read_u32(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
}

void write_mana_ability_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const ManaAbilityDefinition& value) {
    writer.string_value(field_name(prefix, "name"), value.name);
    writer.bool_value(field_name(prefix, "tap_cost"), value.tap_cost);
    write_mana_pool_snapshot(writer, field_name(prefix, "produces"), value.produces);
}

[[nodiscard]] bool read_mana_ability_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, ManaAbilityDefinition& value) {
    return reader.read_string(field_name(prefix, "name"), value.name) &&
           reader.read_bool(field_name(prefix, "tap_cost"), value.tap_cost) &&
           read_mana_pool_snapshot(reader, field_name(prefix, "produces"), value.produces);
}

void write_sacrifice_cost_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const SacrificeCostDefinition& value) {
    writer.u32_value(field_name(prefix, "count"), value.count);
    writer.u32_value(field_name(prefix, "required_type_mask"), value.required_type_mask);
}

[[nodiscard]] bool read_sacrifice_cost_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, SacrificeCostDefinition& value) {
    return reader.read_u32(field_name(prefix, "count"), value.count) &&
           reader.read_u32(field_name(prefix, "required_type_mask"), value.required_type_mask);
}

void write_discard_cost_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const DiscardCostDefinition& value) {
    writer.u32_value(field_name(prefix, "count"), value.count);
}

[[nodiscard]] bool read_discard_cost_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, DiscardCostDefinition& value) {
    return reader.read_u32(field_name(prefix, "count"), value.count);
}

void write_activated_ability_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const ActivatedAbilityDefinition& value) {
    writer.string_value(field_name(prefix, "name"), value.name);
    write_mana_cost_snapshot(writer, field_name(prefix, "mana_cost"), value.mana_cost);
    write_sacrifice_cost_snapshot(writer, field_name(prefix, "sacrifice_cost"), value.sacrifice_cost);
    write_discard_cost_snapshot(writer, field_name(prefix, "discard_cost"), value.discard_cost);
    writer.bool_value(field_name(prefix, "tap_cost"), value.tap_cost);
    writer.bool_value(field_name(prefix, "sorcery_speed"), value.sorcery_speed);
    write_enum_snapshot(writer, field_name(prefix, "effect_kind"), value.effect_kind);
    writer.u32_value(field_name(prefix, "effect_amount"), value.effect_amount);
    write_enum_snapshot(writer, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind);
    writer.u32_value(field_name(prefix, "target_mask"), value.target_mask);
    writer.u32_value(field_name(prefix, "target_count"), value.target_count);
    writer.u32_value(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
}

[[nodiscard]] bool read_activated_ability_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, ActivatedAbilityDefinition& value) {
    return reader.read_string(field_name(prefix, "name"), value.name) &&
           read_mana_cost_snapshot(reader, field_name(prefix, "mana_cost"), value.mana_cost) &&
           read_sacrifice_cost_snapshot(reader, field_name(prefix, "sacrifice_cost"), value.sacrifice_cost) &&
           read_discard_cost_snapshot(reader, field_name(prefix, "discard_cost"), value.discard_cost) &&
           reader.read_bool(field_name(prefix, "tap_cost"), value.tap_cost) &&
           reader.read_bool(field_name(prefix, "sorcery_speed"), value.sorcery_speed) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_kind"), value.effect_kind, static_cast<u32>(EffectKind::Count)) &&
           reader.read_u32(field_name(prefix, "effect_amount"), value.effect_amount) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind, static_cast<u32>(CounterKind::Count)) &&
           reader.read_u32(field_name(prefix, "target_mask"), value.target_mask) &&
           reader.read_u32(field_name(prefix, "target_count"), value.target_count) &&
           reader.read_u32(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
}

void write_static_effect_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const StaticEffectDefinition& value) {
    writer.string_value(field_name(prefix, "name"), value.name);
    write_string_vector_snapshot(writer, field_name(prefix, "depends_on_effect_names"), value.depends_on_effect_names);
    write_enum_snapshot(writer, field_name(prefix, "scope"), value.scope);
    writer.u32_value(field_name(prefix, "affected_type_mask"), value.affected_type_mask);
    writer.u32_value(field_name(prefix, "added_type_mask"), value.added_type_mask);
    writer.u32_value(field_name(prefix, "removed_type_mask"), value.removed_type_mask);
    writer.bool_value(field_name(prefix, "sets_color"), value.sets_color);
    writer.u32_value(field_name(prefix, "set_color_mask"), value.set_color_mask);
    writer.u32_value(field_name(prefix, "added_color_mask"), value.added_color_mask);
    writer.u32_value(field_name(prefix, "removed_color_mask"), value.removed_color_mask);
    writer.bool_value(field_name(prefix, "sets_power_toughness"), value.sets_power_toughness);
    writer.i32_value(field_name(prefix, "set_power"), value.set_power);
    writer.i32_value(field_name(prefix, "set_toughness"), value.set_toughness);
    writer.i32_value(field_name(prefix, "power_modifier"), value.power_modifier);
    writer.i32_value(field_name(prefix, "toughness_modifier"), value.toughness_modifier);
    writer.u32_value(field_name(prefix, "granted_ability_mask"), value.granted_ability_mask);
    writer.u32_value(field_name(prefix, "removed_ability_mask"), value.removed_ability_mask);
}

[[nodiscard]] bool read_static_effect_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, StaticEffectDefinition& value) {
    return reader.read_string(field_name(prefix, "name"), value.name) &&
           read_string_vector_snapshot(reader, field_name(prefix, "depends_on_effect_names"), value.depends_on_effect_names) &&
           read_enum_snapshot(reader, field_name(prefix, "scope"), value.scope, static_cast<u32>(StaticEffectScope::Count)) &&
           reader.read_u32(field_name(prefix, "affected_type_mask"), value.affected_type_mask) &&
           reader.read_u32(field_name(prefix, "added_type_mask"), value.added_type_mask) &&
           reader.read_u32(field_name(prefix, "removed_type_mask"), value.removed_type_mask) &&
           reader.read_bool(field_name(prefix, "sets_color"), value.sets_color) &&
           reader.read_u32(field_name(prefix, "set_color_mask"), value.set_color_mask) &&
           reader.read_u32(field_name(prefix, "added_color_mask"), value.added_color_mask) &&
           reader.read_u32(field_name(prefix, "removed_color_mask"), value.removed_color_mask) &&
           reader.read_bool(field_name(prefix, "sets_power_toughness"), value.sets_power_toughness) &&
           reader.read_i32(field_name(prefix, "set_power"), value.set_power) &&
           reader.read_i32(field_name(prefix, "set_toughness"), value.set_toughness) &&
           reader.read_i32(field_name(prefix, "power_modifier"), value.power_modifier) &&
           reader.read_i32(field_name(prefix, "toughness_modifier"), value.toughness_modifier) &&
           reader.read_u32(field_name(prefix, "granted_ability_mask"), value.granted_ability_mask) &&
           reader.read_u32(field_name(prefix, "removed_ability_mask"), value.removed_ability_mask);
}

void write_zone_change_replacement_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const ZoneChangeReplacementDefinition& value) {
    writer.string_value(field_name(prefix, "name"), value.name);
    write_enum_snapshot(writer, field_name(prefix, "scope"), value.scope);
    write_enum_snapshot(writer, field_name(prefix, "from_zone"), value.from_zone);
    write_enum_snapshot(writer, field_name(prefix, "to_zone"), value.to_zone);
    write_enum_snapshot(writer, field_name(prefix, "replacement_zone"), value.replacement_zone);
    writer.u32_value(field_name(prefix, "affected_type_mask"), value.affected_type_mask);
    writer.u32_value(field_name(prefix, "choice_rank"), value.choice_rank);
}

[[nodiscard]] bool read_zone_change_replacement_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, ZoneChangeReplacementDefinition& value) {
    return reader.read_string(field_name(prefix, "name"), value.name) &&
           read_enum_snapshot(reader, field_name(prefix, "scope"), value.scope, static_cast<u32>(StaticEffectScope::Count)) &&
           read_enum_snapshot(reader, field_name(prefix, "from_zone"), value.from_zone, static_cast<u32>(Zone::Count)) &&
           read_enum_snapshot(reader, field_name(prefix, "to_zone"), value.to_zone, static_cast<u32>(Zone::Count)) &&
           read_enum_snapshot(reader, field_name(prefix, "replacement_zone"), value.replacement_zone, static_cast<u32>(Zone::Count)) &&
           reader.read_u32(field_name(prefix, "affected_type_mask"), value.affected_type_mask) &&
           reader.read_u32(field_name(prefix, "choice_rank"), value.choice_rank);
}

void write_card_definition_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const CardDefinition& value) {
    writer.string_value(field_name(prefix, "name"), value.name);
    writer.u32_value(field_name(prefix, "type_mask"), value.type_mask);
    writer.i32_value(field_name(prefix, "printed_power"), value.printed_power);
    writer.i32_value(field_name(prefix, "printed_toughness"), value.printed_toughness);
    writer.i32_value(field_name(prefix, "printed_loyalty"), value.printed_loyalty);
    writer.i32_value(field_name(prefix, "printed_defense"), value.printed_defense);
    write_mana_cost_snapshot(writer, field_name(prefix, "mana_cost"), value.mana_cost);
    writer.bool_value(field_name(prefix, "taps_for_mana"), value.taps_for_mana);
    write_enum_snapshot(writer, field_name(prefix, "tap_mana_symbol"), value.tap_mana_symbol);
    write_vector_snapshot(writer, field_name(prefix, "mana_abilities"), value.mana_abilities, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const ManaAbilityDefinition& item) { write_mana_ability_snapshot(w, item_prefix, item); });
    write_enum_snapshot(writer, field_name(prefix, "effect_kind"), value.effect_kind);
    writer.u32_value(field_name(prefix, "effect_amount"), value.effect_amount);
    write_enum_snapshot(writer, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind);
    writer.u32_value(field_name(prefix, "target_mask"), value.target_mask);
    writer.u32_value(field_name(prefix, "target_count"), value.target_count);
    writer.u32_value(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
    write_trigger_definition_snapshot(writer, field_name(prefix, "trigger"), value.trigger);
    writer.u32_value(field_name(prefix, "color_mask"), value.color_mask);
    writer.u32_value(field_name(prefix, "protection_color_mask"), value.protection_color_mask);
    writer.u32_value(field_name(prefix, "ability_mask"), value.ability_mask);
    writer.bool_value(field_name(prefix, "attacks_each_combat_if_able"), value.attacks_each_combat_if_able);
    writer.bool_value(field_name(prefix, "blocks_each_combat_if_able"), value.blocks_each_combat_if_able);
    writer.bool_value(field_name(prefix, "must_be_blocked_if_able"), value.must_be_blocked_if_able);
    writer.bool_value(field_name(prefix, "all_able_blockers_block_this_if_able"), value.all_able_blockers_block_this_if_able);
    writer.bool_value(field_name(prefix, "cant_attack_alone"), value.cant_attack_alone);
    writer.bool_value(field_name(prefix, "cant_block_alone"), value.cant_block_alone);
    writer.bool_value(field_name(prefix, "can_block_only_flying"), value.can_block_only_flying);
    writer.u32_value(field_name(prefix, "max_attackers_each_combat"), value.max_attackers_each_combat);
    writer.u32_value(field_name(prefix, "max_blockers_each_combat"), value.max_blockers_each_combat);
    writer.u32_value(field_name(prefix, "max_blockers_to_block_this"), value.max_blockers_to_block_this);
    write_mana_cost_snapshot(writer, field_name(prefix, "attack_cost"), value.attack_cost);
    write_mana_cost_snapshot(writer, field_name(prefix, "block_cost"), value.block_cost);
    write_enum_snapshot(writer, field_name(prefix, "attachment_kind"), value.attachment_kind);
    writer.i32_value(field_name(prefix, "attachment_power_bonus"), value.attachment_power_bonus);
    writer.i32_value(field_name(prefix, "attachment_toughness_bonus"), value.attachment_toughness_bonus);
    writer.u32_value(field_name(prefix, "attachment_granted_ability_mask"), value.attachment_granted_ability_mask);
    write_loyalty_ability_snapshot(writer, field_name(prefix, "loyalty_ability"), value.loyalty_ability);
    write_vector_snapshot(writer, field_name(prefix, "modes"), value.modes, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const SpellModeDefinition& item) { write_spell_mode_snapshot(w, item_prefix, item); });
    write_vector_snapshot(writer, field_name(prefix, "activated_abilities"), value.activated_abilities, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const ActivatedAbilityDefinition& item) { write_activated_ability_snapshot(w, item_prefix, item); });
    write_vector_snapshot(writer, field_name(prefix, "static_effects"), value.static_effects, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const StaticEffectDefinition& item) { write_static_effect_snapshot(w, item_prefix, item); });
    write_vector_snapshot(writer, field_name(prefix, "zone_change_replacements"), value.zone_change_replacements, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const ZoneChangeReplacementDefinition& item) { write_zone_change_replacement_snapshot(w, item_prefix, item); });
    write_sacrifice_cost_snapshot(writer, field_name(prefix, "sacrifice_cost"), value.sacrifice_cost);
    write_discard_cost_snapshot(writer, field_name(prefix, "discard_cost"), value.discard_cost);
    write_static_effect_snapshot(writer, field_name(prefix, "continuous_effect"), value.continuous_effect);
    write_enum_snapshot(writer, field_name(prefix, "continuous_effect_duration"), value.continuous_effect_duration);
}

[[nodiscard]] bool read_card_definition_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, CardDefinition& value) {
    return reader.read_string(field_name(prefix, "name"), value.name) &&
           reader.read_u32(field_name(prefix, "type_mask"), value.type_mask) &&
           reader.read_i32(field_name(prefix, "printed_power"), value.printed_power) &&
           reader.read_i32(field_name(prefix, "printed_toughness"), value.printed_toughness) &&
           reader.read_i32(field_name(prefix, "printed_loyalty"), value.printed_loyalty) &&
           reader.read_i32(field_name(prefix, "printed_defense"), value.printed_defense) &&
           read_mana_cost_snapshot(reader, field_name(prefix, "mana_cost"), value.mana_cost) &&
           reader.read_bool(field_name(prefix, "taps_for_mana"), value.taps_for_mana) &&
           read_enum_snapshot(reader, field_name(prefix, "tap_mana_symbol"), value.tap_mana_symbol, static_cast<u32>(ManaSymbol::Count)) &&
           read_vector_snapshot(reader, field_name(prefix, "mana_abilities"), value.mana_abilities, [](StateCoreSnapshotReader& r, const std::string& item_prefix, ManaAbilityDefinition& item) { return read_mana_ability_snapshot(r, item_prefix, item); }) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_kind"), value.effect_kind, static_cast<u32>(EffectKind::Count)) &&
           reader.read_u32(field_name(prefix, "effect_amount"), value.effect_amount) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind, static_cast<u32>(CounterKind::Count)) &&
           reader.read_u32(field_name(prefix, "target_mask"), value.target_mask) &&
           reader.read_u32(field_name(prefix, "target_count"), value.target_count) &&
           reader.read_u32(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index) &&
           read_trigger_definition_snapshot(reader, field_name(prefix, "trigger"), value.trigger) &&
           reader.read_u32(field_name(prefix, "color_mask"), value.color_mask) &&
           reader.read_u32(field_name(prefix, "protection_color_mask"), value.protection_color_mask) &&
           reader.read_u32(field_name(prefix, "ability_mask"), value.ability_mask) &&
           reader.read_bool(field_name(prefix, "attacks_each_combat_if_able"), value.attacks_each_combat_if_able) &&
           reader.read_bool(field_name(prefix, "blocks_each_combat_if_able"), value.blocks_each_combat_if_able) &&
           reader.read_bool(field_name(prefix, "must_be_blocked_if_able"), value.must_be_blocked_if_able) &&
           reader.read_bool(field_name(prefix, "all_able_blockers_block_this_if_able"), value.all_able_blockers_block_this_if_able) &&
           reader.read_bool(field_name(prefix, "cant_attack_alone"), value.cant_attack_alone) &&
           reader.read_bool(field_name(prefix, "cant_block_alone"), value.cant_block_alone) &&
           reader.read_bool(field_name(prefix, "can_block_only_flying"), value.can_block_only_flying) &&
           reader.read_u32(field_name(prefix, "max_attackers_each_combat"), value.max_attackers_each_combat) &&
           reader.read_u32(field_name(prefix, "max_blockers_each_combat"), value.max_blockers_each_combat) &&
           reader.read_u32(field_name(prefix, "max_blockers_to_block_this"), value.max_blockers_to_block_this) &&
           read_mana_cost_snapshot(reader, field_name(prefix, "attack_cost"), value.attack_cost) &&
           read_mana_cost_snapshot(reader, field_name(prefix, "block_cost"), value.block_cost) &&
           read_enum_snapshot(reader, field_name(prefix, "attachment_kind"), value.attachment_kind, static_cast<u32>(AttachmentKind::Count)) &&
           reader.read_i32(field_name(prefix, "attachment_power_bonus"), value.attachment_power_bonus) &&
           reader.read_i32(field_name(prefix, "attachment_toughness_bonus"), value.attachment_toughness_bonus) &&
           reader.read_u32(field_name(prefix, "attachment_granted_ability_mask"), value.attachment_granted_ability_mask) &&
           read_loyalty_ability_snapshot(reader, field_name(prefix, "loyalty_ability"), value.loyalty_ability) &&
           read_vector_snapshot(reader, field_name(prefix, "modes"), value.modes, [](StateCoreSnapshotReader& r, const std::string& item_prefix, SpellModeDefinition& item) { return read_spell_mode_snapshot(r, item_prefix, item); }) &&
           read_vector_snapshot(reader, field_name(prefix, "activated_abilities"), value.activated_abilities, [](StateCoreSnapshotReader& r, const std::string& item_prefix, ActivatedAbilityDefinition& item) { return read_activated_ability_snapshot(r, item_prefix, item); }) &&
           read_vector_snapshot(reader, field_name(prefix, "static_effects"), value.static_effects, [](StateCoreSnapshotReader& r, const std::string& item_prefix, StaticEffectDefinition& item) { return read_static_effect_snapshot(r, item_prefix, item); }) &&
           read_vector_snapshot(reader, field_name(prefix, "zone_change_replacements"), value.zone_change_replacements, [](StateCoreSnapshotReader& r, const std::string& item_prefix, ZoneChangeReplacementDefinition& item) { return read_zone_change_replacement_snapshot(r, item_prefix, item); }) &&
           read_sacrifice_cost_snapshot(reader, field_name(prefix, "sacrifice_cost"), value.sacrifice_cost) &&
           read_discard_cost_snapshot(reader, field_name(prefix, "discard_cost"), value.discard_cost) &&
           read_static_effect_snapshot(reader, field_name(prefix, "continuous_effect"), value.continuous_effect) &&
           read_enum_snapshot(reader, field_name(prefix, "continuous_effect_duration"), value.continuous_effect_duration, static_cast<u32>(ContinuousEffectDuration::Count));
}

void write_game_object_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const GameObject& value) {
    write_object_id_snapshot(writer, field_name(prefix, "id"), value.id);
    writer.u32_value(field_name(prefix, "definition_index"), value.definition_index);
    writer.bool_value(field_name(prefix, "has_copy_effect"), value.has_copy_effect);
    writer.u32_value(field_name(prefix, "copied_definition_index"), value.copied_definition_index);
    write_player_id_snapshot(writer, field_name(prefix, "owner"), value.owner);
    write_player_id_snapshot(writer, field_name(prefix, "controller"), value.controller);
    write_enum_snapshot(writer, field_name(prefix, "zone"), value.zone);
    writer.bool_value(field_name(prefix, "tapped"), value.tapped);
    writer.bool_value(field_name(prefix, "token"), value.token);
    writer.bool_value(field_name(prefix, "ceased_to_exist"), value.ceased_to_exist);
    writer.i32_value(field_name(prefix, "power"), value.power);
    writer.i32_value(field_name(prefix, "toughness"), value.toughness);
    writer.u32_value(field_name(prefix, "damage_marked"), value.damage_marked);
    writer.bool_value(field_name(prefix, "deathtouch_damage_marked"), value.deathtouch_damage_marked);
    write_counter_set_snapshot(writer, field_name(prefix, "counters"), value.counters);
    write_target_ref_vector_snapshot(writer, field_name(prefix, "targets"), value.targets);
    writer.u32_value(field_name(prefix, "chosen_mode_index"), value.chosen_mode_index);
    writer.bool_value(field_name(prefix, "ability_object"), value.ability_object);
    writer.u32_value(field_name(prefix, "regeneration_shields"), value.regeneration_shields);
    write_target_ref_snapshot(writer, field_name(prefix, "attached_to"), value.attached_to);
    writer.bool_value(field_name(prefix, "attacking"), value.attacking);
    writer.bool_value(field_name(prefix, "blocked"), value.blocked);
    write_player_id_snapshot(writer, field_name(prefix, "defending_player"), value.defending_player);
    write_object_id_snapshot(writer, field_name(prefix, "attacked_object"), value.attacked_object);
    write_object_id_snapshot(writer, field_name(prefix, "blocking"), value.blocking);
    write_object_id_vector_snapshot(writer, field_name(prefix, "combat_damage_ordered_blockers"), value.combat_damage_ordered_blockers);
    write_player_id_snapshot(writer, field_name(prefix, "battle_protector"), value.battle_protector);
    writer.u32_value(field_name(prefix, "controlled_since_turn_start_index"), value.controlled_since_turn_start_index);
    writer.u32_value(field_name(prefix, "loyalty_ability_activated_turn"), value.loyalty_ability_activated_turn);
    writer.u64_value(field_name(prefix, "zone_change_index"), value.zone_change_index);
    writer.u64_value(field_name(prefix, "layer_timestamp"), value.layer_timestamp);
}

[[nodiscard]] bool read_game_object_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, GameObject& value) {
    return read_object_id_snapshot(reader, field_name(prefix, "id"), value.id) &&
           reader.read_u32(field_name(prefix, "definition_index"), value.definition_index) &&
           reader.read_bool(field_name(prefix, "has_copy_effect"), value.has_copy_effect) &&
           reader.read_u32(field_name(prefix, "copied_definition_index"), value.copied_definition_index) &&
           read_player_id_snapshot(reader, field_name(prefix, "owner"), value.owner) &&
           read_player_id_snapshot(reader, field_name(prefix, "controller"), value.controller) &&
           read_enum_snapshot(reader, field_name(prefix, "zone"), value.zone, static_cast<u32>(Zone::Count)) &&
           reader.read_bool(field_name(prefix, "tapped"), value.tapped) &&
           reader.read_bool(field_name(prefix, "token"), value.token) &&
           reader.read_bool(field_name(prefix, "ceased_to_exist"), value.ceased_to_exist) &&
           reader.read_i32(field_name(prefix, "power"), value.power) &&
           reader.read_i32(field_name(prefix, "toughness"), value.toughness) &&
           reader.read_u32(field_name(prefix, "damage_marked"), value.damage_marked) &&
           reader.read_bool(field_name(prefix, "deathtouch_damage_marked"), value.deathtouch_damage_marked) &&
           read_counter_set_snapshot(reader, field_name(prefix, "counters"), value.counters) &&
           read_target_ref_vector_snapshot(reader, field_name(prefix, "targets"), value.targets) &&
           reader.read_u32(field_name(prefix, "chosen_mode_index"), value.chosen_mode_index) &&
           reader.read_bool(field_name(prefix, "ability_object"), value.ability_object) &&
           reader.read_u32(field_name(prefix, "regeneration_shields"), value.regeneration_shields) &&
           read_target_ref_snapshot(reader, field_name(prefix, "attached_to"), value.attached_to) &&
           reader.read_bool(field_name(prefix, "attacking"), value.attacking) &&
           reader.read_bool(field_name(prefix, "blocked"), value.blocked) &&
           read_player_id_snapshot(reader, field_name(prefix, "defending_player"), value.defending_player) &&
           read_object_id_snapshot(reader, field_name(prefix, "attacked_object"), value.attacked_object) &&
           read_object_id_snapshot(reader, field_name(prefix, "blocking"), value.blocking) &&
           read_object_id_vector_snapshot(reader, field_name(prefix, "combat_damage_ordered_blockers"), value.combat_damage_ordered_blockers) &&
           read_player_id_snapshot(reader, field_name(prefix, "battle_protector"), value.battle_protector) &&
           reader.read_u32(field_name(prefix, "controlled_since_turn_start_index"), value.controlled_since_turn_start_index) &&
           reader.read_u32(field_name(prefix, "loyalty_ability_activated_turn"), value.loyalty_ability_activated_turn) &&
           reader.read_u64(field_name(prefix, "zone_change_index"), value.zone_change_index) &&
           reader.read_u64(field_name(prefix, "layer_timestamp"), value.layer_timestamp);
}

void write_player_state_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const PlayerState& value) {
    write_player_id_snapshot(writer, field_name(prefix, "id"), value.id);
    writer.string_value(field_name(prefix, "name"), value.name);
    writer.i32_value(field_name(prefix, "life"), value.life);
    writer.u32_value(field_name(prefix, "poison"), value.poison);
    writer.u32_value(field_name(prefix, "max_hand_size"), value.max_hand_size);
    writer.u32_value(field_name(prefix, "max_land_plays_per_turn"), value.max_land_plays_per_turn);
    writer.u32_value(field_name(prefix, "lands_played_this_turn"), value.lands_played_this_turn);
    write_mana_pool_snapshot(writer, field_name(prefix, "mana_pool"), value.mana_pool);
    writer.bool_value(field_name(prefix, "lost"), value.lost);
    writer.u32_value(field_name(prefix, "empty_library_draw_attempts"), value.empty_library_draw_attempts);
    writer.u32_value(field_name(prefix, "mulligans_taken"), value.mulligans_taken);
    writer.u32_value(field_name(prefix, "turn_start_index"), value.turn_start_index);
    for (u32 raw_zone = 0; raw_zone < static_cast<u32>(Zone::Count); ++raw_zone) {
        write_object_id_vector_snapshot(writer, field_name(prefix, "zone" + std::to_string(raw_zone)), value.zones[raw_zone]);
    }
}

[[nodiscard]] bool read_player_state_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, PlayerState& value) {
    if (!(read_player_id_snapshot(reader, field_name(prefix, "id"), value.id) &&
          reader.read_string(field_name(prefix, "name"), value.name) &&
          reader.read_i32(field_name(prefix, "life"), value.life) &&
          reader.read_u32(field_name(prefix, "poison"), value.poison) &&
          reader.read_u32(field_name(prefix, "max_hand_size"), value.max_hand_size) &&
          reader.read_u32(field_name(prefix, "max_land_plays_per_turn"), value.max_land_plays_per_turn) &&
          reader.read_u32(field_name(prefix, "lands_played_this_turn"), value.lands_played_this_turn) &&
          read_mana_pool_snapshot(reader, field_name(prefix, "mana_pool"), value.mana_pool) &&
          reader.read_bool(field_name(prefix, "lost"), value.lost) &&
          reader.read_u32(field_name(prefix, "empty_library_draw_attempts"), value.empty_library_draw_attempts) &&
          reader.read_u32(field_name(prefix, "mulligans_taken"), value.mulligans_taken) &&
          reader.read_u32(field_name(prefix, "turn_start_index"), value.turn_start_index))) {
        return false;
    }
    for (u32 raw_zone = 0; raw_zone < static_cast<u32>(Zone::Count); ++raw_zone) {
        if (!read_object_id_vector_snapshot(reader, field_name(prefix, "zone" + std::to_string(raw_zone)), value.zones[raw_zone])) {
            return false;
        }
    }
    return true;
}

void write_pending_trigger_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const PendingTrigger& value) {
    write_player_id_snapshot(writer, field_name(prefix, "controller"), value.controller);
    write_object_id_snapshot(writer, field_name(prefix, "source"), value.source);
    write_object_id_snapshot(writer, field_name(prefix, "subject"), value.subject);
    writer.u64_value(field_name(prefix, "subject_zone_change_index"), value.subject_zone_change_index);
    writer.string_value(field_name(prefix, "source_name"), value.source_name);
    write_enum_snapshot(writer, field_name(prefix, "event"), value.event);
    write_enum_snapshot(writer, field_name(prefix, "effect_kind"), value.effect_kind);
    writer.u32_value(field_name(prefix, "effect_amount"), value.effect_amount);
    write_enum_snapshot(writer, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind);
    writer.u32_value(field_name(prefix, "target_mask"), value.target_mask);
    writer.u32_value(field_name(prefix, "target_count"), value.target_count);
    writer.u32_value(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index);
    writer.u32_value(field_name(prefix, "source_color_mask"), value.source_color_mask);
    writer.u32_value(field_name(prefix, "source_ability_mask"), value.source_ability_mask);
    writer.u64_value(field_name(prefix, "source_zone_change_index"), value.source_zone_change_index);
    writer.u64_value(field_name(prefix, "caused_by_event_sequence"), value.caused_by_event_sequence);
}

[[nodiscard]] bool read_pending_trigger_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, PendingTrigger& value) {
    return read_player_id_snapshot(reader, field_name(prefix, "controller"), value.controller) &&
           read_object_id_snapshot(reader, field_name(prefix, "source"), value.source) &&
           read_object_id_snapshot(reader, field_name(prefix, "subject"), value.subject) &&
           reader.read_u64(field_name(prefix, "subject_zone_change_index"), value.subject_zone_change_index) &&
           reader.read_string(field_name(prefix, "source_name"), value.source_name) &&
           read_enum_snapshot(reader, field_name(prefix, "event"), value.event, static_cast<u32>(TriggerEventKind::Count)) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_kind"), value.effect_kind, static_cast<u32>(EffectKind::Count)) &&
           reader.read_u32(field_name(prefix, "effect_amount"), value.effect_amount) &&
           read_enum_snapshot(reader, field_name(prefix, "effect_counter_kind"), value.effect_counter_kind, static_cast<u32>(CounterKind::Count)) &&
           reader.read_u32(field_name(prefix, "target_mask"), value.target_mask) &&
           reader.read_u32(field_name(prefix, "target_count"), value.target_count) &&
           reader.read_u32(field_name(prefix, "created_token_definition_index"), value.created_token_definition_index) &&
           reader.read_u32(field_name(prefix, "source_color_mask"), value.source_color_mask) &&
           reader.read_u32(field_name(prefix, "source_ability_mask"), value.source_ability_mask) &&
           reader.read_u64(field_name(prefix, "source_zone_change_index"), value.source_zone_change_index) &&
           reader.read_u64(field_name(prefix, "caused_by_event_sequence"), value.caused_by_event_sequence);
}

void write_damage_prevention_shield_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const DamagePreventionShield& value) {
    writer.u64_value(field_name(prefix, "id"), value.id);
    write_target_ref_snapshot(writer, field_name(prefix, "target"), value.target);
    writer.u32_value(field_name(prefix, "remaining"), value.remaining);
    writer.u32_value(field_name(prefix, "choice_rank"), value.choice_rank);
    writer.string_value(field_name(prefix, "label"), value.label);
}

[[nodiscard]] bool read_damage_prevention_shield_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, DamagePreventionShield& value) {
    return reader.read_u64(field_name(prefix, "id"), value.id) &&
           read_target_ref_snapshot(reader, field_name(prefix, "target"), value.target) &&
           reader.read_u32(field_name(prefix, "remaining"), value.remaining) &&
           reader.read_u32(field_name(prefix, "choice_rank"), value.choice_rank) &&
           reader.read_string(field_name(prefix, "label"), value.label);
}

void write_continuous_effect_target_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const ContinuousEffectTarget& value) {
    write_target_ref_snapshot(writer, field_name(prefix, "target"), value.target);
    writer.u64_value(field_name(prefix, "object_zone_change_index"), value.object_zone_change_index);
}

[[nodiscard]] bool read_continuous_effect_target_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, ContinuousEffectTarget& value) {
    return read_target_ref_snapshot(reader, field_name(prefix, "target"), value.target) &&
           reader.read_u64(field_name(prefix, "object_zone_change_index"), value.object_zone_change_index);
}

void write_continuous_effect_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const ContinuousEffectDefinition& value) {
    writer.string_value(field_name(prefix, "name"), value.name);
    write_static_effect_snapshot(writer, field_name(prefix, "effect"), value.effect);
    write_enum_snapshot(writer, field_name(prefix, "duration"), value.duration);
    write_player_id_snapshot(writer, field_name(prefix, "controller"), value.controller);
    write_object_id_snapshot(writer, field_name(prefix, "source"), value.source);
    write_vector_snapshot(writer, field_name(prefix, "locked_targets"), value.locked_targets, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const ContinuousEffectTarget& item) { write_continuous_effect_target_snapshot(w, item_prefix, item); });
    writer.u64_value(field_name(prefix, "timestamp"), value.timestamp);
}

[[nodiscard]] bool read_continuous_effect_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, ContinuousEffectDefinition& value) {
    return reader.read_string(field_name(prefix, "name"), value.name) &&
           read_static_effect_snapshot(reader, field_name(prefix, "effect"), value.effect) &&
           read_enum_snapshot(reader, field_name(prefix, "duration"), value.duration, static_cast<u32>(ContinuousEffectDuration::Count)) &&
           read_player_id_snapshot(reader, field_name(prefix, "controller"), value.controller) &&
           read_object_id_snapshot(reader, field_name(prefix, "source"), value.source) &&
           read_vector_snapshot(reader, field_name(prefix, "locked_targets"), value.locked_targets, [](StateCoreSnapshotReader& r, const std::string& item_prefix, ContinuousEffectTarget& item) { return read_continuous_effect_target_snapshot(r, item_prefix, item); }) &&
           reader.read_u64(field_name(prefix, "timestamp"), value.timestamp);
}

void write_checkpoint_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const StateCheckpointSeal& value) {
    writer.u64_value(field_name(prefix, "state_hash"), value.state_hash);
    writer.u64_value(field_name(prefix, "journal_hash"), value.journal_hash);
    writer.u64_value(field_name(prefix, "journal_entries"), value.journal_entries);
    writer.u64_value(field_name(prefix, "action_receipts"), value.action_receipts);
    writer.u64_value(field_name(prefix, "object_count"), value.object_count);
    writer.u64_value(field_name(prefix, "player_count"), value.player_count);
    writer.u64_value(field_name(prefix, "stack_size"), value.stack_size);
    writer.u64_value(field_name(prefix, "rng_state"), value.rng_state);
    writer.u64_value(field_name(prefix, "next_zone_change_index"), value.next_zone_change_index);
    writer.u64_value(field_name(prefix, "next_event_sequence"), value.next_event_sequence);
    writer.u32_value(field_name(prefix, "turn_number"), value.turn_number);
    write_enum_snapshot(writer, field_name(prefix, "step"), value.step);
    write_player_id_snapshot(writer, field_name(prefix, "active_player"), value.active_player);
    write_player_id_snapshot(writer, field_name(prefix, "priority_player"), value.priority_player);
    writer.bool_value(field_name(prefix, "journal_trimmed"), value.journal_trimmed);
}

[[nodiscard]] bool read_checkpoint_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, StateCheckpointSeal& value) {
    return reader.read_u64(field_name(prefix, "state_hash"), value.state_hash) &&
           reader.read_u64(field_name(prefix, "journal_hash"), value.journal_hash) &&
           reader.read_u64(field_name(prefix, "journal_entries"), value.journal_entries) &&
           reader.read_u64(field_name(prefix, "action_receipts"), value.action_receipts) &&
           reader.read_u64(field_name(prefix, "object_count"), value.object_count) &&
           reader.read_u64(field_name(prefix, "player_count"), value.player_count) &&
           reader.read_u64(field_name(prefix, "stack_size"), value.stack_size) &&
           reader.read_u64(field_name(prefix, "rng_state"), value.rng_state) &&
           reader.read_u64(field_name(prefix, "next_zone_change_index"), value.next_zone_change_index) &&
           reader.read_u64(field_name(prefix, "next_event_sequence"), value.next_event_sequence) &&
           reader.read_u32(field_name(prefix, "turn_number"), value.turn_number) &&
           read_enum_snapshot(reader, field_name(prefix, "step"), value.step, static_cast<u32>(Step::Cleanup) + 1U) &&
           read_player_id_snapshot(reader, field_name(prefix, "active_player"), value.active_player) &&
           read_player_id_snapshot(reader, field_name(prefix, "priority_player"), value.priority_player) &&
           reader.read_bool(field_name(prefix, "journal_trimmed"), value.journal_trimmed);
}

void write_game_core_snapshot(StateCoreSnapshotWriter& writer, std::string_view prefix, const GameState& game) {
    write_vector_snapshot(writer, field_name(prefix, "definitions"), game.definitions, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const CardDefinition& item) { write_card_definition_snapshot(w, item_prefix, item); });
    write_vector_snapshot(writer, field_name(prefix, "objects"), game.objects, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const GameObject& item) { write_game_object_snapshot(w, item_prefix, item); });
    write_vector_snapshot(writer, field_name(prefix, "players"), game.players, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const PlayerState& item) { write_player_state_snapshot(w, item_prefix, item); });
    write_object_id_vector_snapshot(writer, field_name(prefix, "stack"), game.stack);
    writer.u64_value(field_name(prefix, "rng_state"), game.rng_state);
    writer.u64_value(field_name(prefix, "next_event_sequence"), game.next_event_sequence);
    writer.u64_value(field_name(prefix, "next_zone_change_index"), game.next_zone_change_index);
    writer.u64_value(field_name(prefix, "next_damage_prevention_shield_id"), game.next_damage_prevention_shield_id);
    writer.u64_value(field_name(prefix, "next_continuous_effect_timestamp"), game.next_continuous_effect_timestamp);
    writer.u64_value(field_name(prefix, "next_layer_timestamp"), game.next_layer_timestamp);
    write_player_id_snapshot(writer, field_name(prefix, "starting_player"), game.starting_player);
    write_player_id_snapshot(writer, field_name(prefix, "active_player"), game.active_player);
    write_player_id_snapshot(writer, field_name(prefix, "priority_player"), game.priority_player);
    writer.u32_value(field_name(prefix, "turn_number"), game.turn_number);
    write_enum_snapshot(writer, field_name(prefix, "step"), game.step);
    writer.u32_value(field_name(prefix, "consecutive_priority_passes"), game.consecutive_priority_passes);
    writer.bool_value(field_name(prefix, "attackers_declared_this_step"), game.attackers_declared_this_step);
    writer.bool_value(field_name(prefix, "combat_damage_assigned_this_step"), game.combat_damage_assigned_this_step);
    write_player_id_vector_snapshot(writer, field_name(prefix, "blocker_declaration_complete_players"), game.blocker_declaration_complete_players);
    write_vector_snapshot(writer, field_name(prefix, "pending_triggers"), game.pending_triggers, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const PendingTrigger& item) { write_pending_trigger_snapshot(w, item_prefix, item); });
    write_vector_snapshot(writer, field_name(prefix, "damage_prevention_shields"), game.damage_prevention_shields, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const DamagePreventionShield& item) { write_damage_prevention_shield_snapshot(w, item_prefix, item); });
    write_vector_snapshot(writer, field_name(prefix, "continuous_effects"), game.continuous_effects, [](StateCoreSnapshotWriter& w, const std::string& item_prefix, const ContinuousEffectDefinition& item) { write_continuous_effect_snapshot(w, item_prefix, item); });
}

[[nodiscard]] bool read_game_core_snapshot(StateCoreSnapshotReader& reader, std::string_view prefix, GameState& game) {
    if (!(read_vector_snapshot(reader, field_name(prefix, "definitions"), game.definitions, [](StateCoreSnapshotReader& r, const std::string& item_prefix, CardDefinition& item) { return read_card_definition_snapshot(r, item_prefix, item); }) &&
          read_vector_snapshot(reader, field_name(prefix, "objects"), game.objects, [](StateCoreSnapshotReader& r, const std::string& item_prefix, GameObject& item) { return read_game_object_snapshot(r, item_prefix, item); }) &&
          read_vector_snapshot(reader, field_name(prefix, "players"), game.players, [](StateCoreSnapshotReader& r, const std::string& item_prefix, PlayerState& item) { return read_player_state_snapshot(r, item_prefix, item); }) &&
          read_object_id_vector_snapshot(reader, field_name(prefix, "stack"), game.stack) &&
          reader.read_u64(field_name(prefix, "rng_state"), game.rng_state) &&
          reader.read_u64(field_name(prefix, "next_event_sequence"), game.next_event_sequence) &&
          reader.read_u64(field_name(prefix, "next_zone_change_index"), game.next_zone_change_index) &&
          reader.read_u64(field_name(prefix, "next_damage_prevention_shield_id"), game.next_damage_prevention_shield_id) &&
          reader.read_u64(field_name(prefix, "next_continuous_effect_timestamp"), game.next_continuous_effect_timestamp) &&
          reader.read_u64(field_name(prefix, "next_layer_timestamp"), game.next_layer_timestamp) &&
          read_player_id_snapshot(reader, field_name(prefix, "starting_player"), game.starting_player) &&
          read_player_id_snapshot(reader, field_name(prefix, "active_player"), game.active_player) &&
          read_player_id_snapshot(reader, field_name(prefix, "priority_player"), game.priority_player) &&
          reader.read_u32(field_name(prefix, "turn_number"), game.turn_number) &&
          read_enum_snapshot(reader, field_name(prefix, "step"), game.step, static_cast<u32>(Step::Cleanup) + 1U) &&
          reader.read_u32(field_name(prefix, "consecutive_priority_passes"), game.consecutive_priority_passes) &&
          reader.read_bool(field_name(prefix, "attackers_declared_this_step"), game.attackers_declared_this_step) &&
          reader.read_bool(field_name(prefix, "combat_damage_assigned_this_step"), game.combat_damage_assigned_this_step) &&
          read_player_id_vector_snapshot(reader, field_name(prefix, "blocker_declaration_complete_players"), game.blocker_declaration_complete_players) &&
          read_vector_snapshot(reader, field_name(prefix, "pending_triggers"), game.pending_triggers, [](StateCoreSnapshotReader& r, const std::string& item_prefix, PendingTrigger& item) { return read_pending_trigger_snapshot(r, item_prefix, item); }) &&
          read_vector_snapshot(reader, field_name(prefix, "damage_prevention_shields"), game.damage_prevention_shields, [](StateCoreSnapshotReader& r, const std::string& item_prefix, DamagePreventionShield& item) { return read_damage_prevention_shield_snapshot(r, item_prefix, item); }) &&
          read_vector_snapshot(reader, field_name(prefix, "continuous_effects"), game.continuous_effects, [](StateCoreSnapshotReader& r, const std::string& item_prefix, ContinuousEffectDefinition& item) { return read_continuous_effect_snapshot(r, item_prefix, item); }))) {
        return false;
    }
    game.journal_trimmed = true;
    return true;
}

} // namespace

PaidActionTransactionJournalParseResult parse_paid_action_transaction_journal(std::string_view text) {
    PaidActionTransactionJournalParseResult result{};
    auto fail = [&result](u64 line, std::string message) -> PaidActionTransactionJournalParseResult {
        result.ok = false;
        result.journal = PaidActionTransactionJournal{};
        result.error_line = line;
        result.error = std::move(message);
        return result;
    };

    std::istringstream input{std::string(text)};
    std::string line;
    u64 line_number = 0;
    if (!std::getline(input, line)) {
        return fail(1, "empty paid-action transaction journal");
    }
    ++line_number;
    if (!line.empty() && line.back() == '\r') {
        line.pop_back();
    }
    if (line == "MTGSim.PaidActionTransactionJournal.v1") {
        result.journal.header.schema_version = 1U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v2") {
        result.journal.header.schema_version = 2U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v3") {
        result.journal.header.schema_version = 3U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v4") {
        result.journal.header.schema_version = 4U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v5") {
        result.journal.header.schema_version = 5U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v6") {
        result.journal.header.schema_version = 6U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v7") {
        result.journal.header.schema_version = 7U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v8") {
        result.journal.header.schema_version = 8U;
    } else if (line == "MTGSim.PaidActionTransactionJournal.v9") {
        result.journal.header.schema_version = 9U;
    } else {
        return fail(line_number, "missing MTGSim.PaidActionTransactionJournal.v1/v2/v3/v4/v5/v6/v7/v8/v9 header");
    }

    bool seen_header_counts = false;
    while (std::getline(input, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty()) {
            return fail(line_number, "blank lines are not allowed inside paid-action transaction journals");
        }
        JournalFieldMap fields;
        std::string error;
        if (!seen_header_counts) {
            if (!parse_journal_fields(line, fields, error)) {
                return fail(line_number, error);
            }
            seen_header_counts = true;
            if (!parse_required_u64_field(fields, "record_count", result.journal.header.record_count, error) ||
                !parse_required_u64_field(fields, "declaration_record_count", result.journal.header.declaration_record_count, error) ||
                !parse_required_u64_field(fields, "stack_placement_record_count", result.journal.header.stack_placement_record_count, error) ||
                !parse_required_u64_field(fields, "journal_hash", result.journal.header.journal_hash, error) ||
                !parse_required_u64_field(fields, "state_hash", result.journal.header.state_hash, error)) {
                return fail(line_number, error);
            }
            if (result.journal.header.schema_version >= 2U &&
                !parse_required_u64_field(fields, "record_payload_hash", result.journal.header.record_payload_hash, error)) {
                return fail(line_number, error);
            }
            if (result.journal.header.schema_version >= 3U &&
                (!parse_required_u64_field(fields, "first_transaction_sequence", result.journal.header.first_transaction_sequence, error) ||
                 !parse_required_u64_field(fields, "last_transaction_sequence", result.journal.header.last_transaction_sequence, error))) {
                return fail(line_number, error);
            }
            if (!check_no_unknown_journal_header_fields(fields, result.journal.header.schema_version, error)) {
                return fail(line_number, error);
            }
            continue;
        }

        constexpr std::string_view record_prefix = "record ";
        if (line.rfind(std::string(record_prefix), 0) != 0U) {
            return fail(line_number, "expected record line");
        }
        const auto record_fields_text = std::string_view(line).substr(record_prefix.size());
        if (!parse_journal_fields(record_fields_text, fields, error)) {
            return fail(line_number, error);
        }

        PaidActionTransactionJournalRecord parsed{};
        parsed.line_number = line_number;
        auto& record = parsed.transaction;
        if (!parse_required_u32_field(fields, "index", parsed.index, error) ||
            !parse_required_u64_field(fields, "sequence", record.sequence, error) ||
            !parse_required_u32_field(fields, "schema", record.schema_version, error) ||
            !parse_required_paid_action_outcome_field(fields, "outcome", record.outcome, error) ||
            !parse_required_action_kind_field(fields, "action", record.action_kind, error) ||
            !parse_required_u32_field(fields, "player", record.player.value, error) ||
            !parse_required_u32_field(fields, "source", record.source_object.value, error) ||
            !parse_required_u32_field(fields, "stack_object", record.stack_object.value, error) ||
            !parse_required_u32_field(fields, "stack_placement", record.stack_placement_record_index, error) ||
            !parse_required_u32_field(fields, "declaration_index", record.paid_action_declaration_record_index, error) ||
            !parse_required_u64_field(fields, "declaration_hash", record.paid_action_declaration_hash, error) ||
            !parse_required_u64_field(fields, "stack_entered", record.stack_object_entered_sequence, error) ||
            !parse_required_u64_field(fields, "choices_locked", record.choices_locked_sequence, error) ||
            !parse_required_u64_field(fields, "first_paid_event", record.first_paid_action_event_sequence, error) ||
            !parse_required_u64_field(fields, "last_paid_event", record.last_paid_action_event_sequence, error) ||
            !parse_required_u32_field(fields, "mana_plan_first", record.first_mana_payment_plan_record_index, error) ||
            !parse_required_u32_field(fields, "mana_plan_count", record.mana_payment_plan_record_count, error) ||
            !parse_required_u32_field(fields, "mana_change_first", record.first_mana_change_record_index, error) ||
            !parse_required_u32_field(fields, "mana_change_count", record.mana_change_record_count, error) ||
            !parse_required_u32_field(fields, "counter_change_first", record.first_paid_action_counter_change_record_index, error) ||
            !parse_required_u32_field(fields, "counter_change_count", record.paid_action_counter_change_record_count, error) ||
            !parse_required_u32_field(fields, "zone_change_first", record.first_paid_action_zone_change_record_index, error) ||
            !parse_required_u32_field(fields, "zone_change_count", record.paid_action_zone_change_record_count, error) ||
            !parse_required_u32_field(fields, "sacrifice_payment_first", record.first_sacrifice_cost_payment_record_index, error) ||
            !parse_required_u32_field(fields, "sacrifice_payment_count", record.sacrifice_cost_payment_record_count, error) ||
            !parse_required_u64_field(fields, "sacrifice_payment_hash", record.sacrifice_cost_payment_hash, error) ||
            !parse_required_u32_field(fields, "discard_payment_first", record.first_discard_cost_payment_record_index, error) ||
            !parse_required_u32_field(fields, "discard_payment_count", record.discard_cost_payment_record_count, error) ||
            !parse_required_u64_field(fields, "discard_payment_hash", record.discard_cost_payment_hash, error) ||
            !parse_required_u32_field(fields, "tap_payment_first", record.first_tap_cost_payment_record_index, error) ||
            !parse_required_u32_field(fields, "tap_payment_count", record.tap_cost_payment_record_count, error) ||
            !parse_required_u64_field(fields, "tap_payment_hash", record.tap_cost_payment_hash, error) ||
            !parse_required_u32_field(fields, "life_payment_first", record.first_life_cost_payment_record_index, error) ||
            !parse_required_u32_field(fields, "life_payment_count", record.life_cost_payment_record_count, error) ||
            !parse_required_u64_field(fields, "life_payment_hash", record.life_cost_payment_hash, error) ||
            !parse_required_u32_field(fields, "return_payment_first", record.first_return_cost_payment_record_index, error) ||
            !parse_required_u32_field(fields, "return_payment_count", record.return_cost_payment_record_count, error) ||
            !parse_required_u64_field(fields, "return_payment_hash", record.return_cost_payment_hash, error) ||
            !parse_required_u32_field(fields, "loyalty_payment_first", record.first_loyalty_cost_payment_record_index, error) ||
            !parse_required_u32_field(fields, "loyalty_payment_count", record.loyalty_cost_payment_record_count, error) ||
            !parse_required_u64_field(fields, "loyalty_payment_hash", record.loyalty_cost_payment_hash, error) ||
            !parse_required_u32_field(fields, "speculative_event_count", record.speculative_event_count, error) ||
            !parse_required_u32_field(fields, "speculative_event_record_count", record.speculative_event_record_count, error) ||
            !parse_required_u32_field(fields, "speculative_stack_placement_count", record.speculative_stack_placement_record_count, error) ||
            !parse_required_u32_field(fields, "speculative_declaration_count", record.speculative_paid_action_declaration_record_count, error) ||
            !parse_required_u64_field(fields, "speculative_declaration_sequence", record.speculative_paid_action_declaration_sequence, error) ||
            !parse_required_u64_field(fields, "speculative_declaration_hash", record.speculative_paid_action_declaration_hash, error) ||
            !parse_required_u64_field(fields, "speculative_first_payment", record.speculative_first_payment_event_sequence, error) ||
            !parse_required_u64_field(fields, "speculative_last_payment", record.speculative_last_payment_event_sequence, error) ||
            !parse_required_u64_field(fields, "physical_before", record.physical_state_hash_before, error) ||
            !parse_required_u64_field(fields, "physical_after", record.physical_state_hash_after, error) ||
            !parse_required_u64_field(fields, "next_event_before", record.next_event_sequence_before, error) ||
            !parse_required_u64_field(fields, "speculative_next_event_after", record.speculative_next_event_sequence_after, error) ||
            !parse_required_bool_field(fields, "committed", record.committed, error) ||
            !parse_required_bool_field(fields, "rolled_back", record.rolled_back, error) ||
            !parse_required_bool_field(fields, "physical_state_preserved_on_rollback", record.physical_state_preserved_on_rollback, error) ||
            !parse_required_bool_field(fields, "choices_before_payment", record.choices_before_payment, error) ||
            !parse_required_bool_field(fields, "payments_before_placement", record.payments_before_placement, error) ||
            !parse_required_bool_field(fields, "placement_before_transaction", record.placement_before_transaction, error) ||
            !parse_required_u64_field(fields, "transaction_hash", record.transaction_hash, error) ||
            !parse_required_u64_field(fields, "recomputed_transaction_hash", parsed.exported_recomputed_transaction_hash, error) ||
            !parse_required_bool_field(fields, "committed_snapshot_present", record.committed_paid_action_declaration_snapshot_present, error)) {
            return fail(line_number, error);
        }
        if (record.committed_paid_action_declaration_snapshot_present &&
            !parse_paid_action_declaration_snapshot_fields(fields,
                                                           "committed_snapshot",
                                                           record.committed_paid_action_declaration_snapshot,
                                                           parsed.exported_committed_snapshot_recomputed_hash,
                                                           error)) {
            return fail(line_number, error);
        }
        if (!parse_required_bool_field(fields, "speculative_snapshot_present", record.speculative_paid_action_declaration_snapshot_present, error)) {
            return fail(line_number, error);
        }
        if (record.speculative_paid_action_declaration_snapshot_present &&
            !parse_paid_action_declaration_snapshot_fields(fields,
                                                           "speculative_snapshot",
                                                           record.speculative_paid_action_declaration_snapshot,
                                                           parsed.exported_speculative_snapshot_recomputed_hash,
                                                           error)) {
            return fail(line_number, error);
        }
        if (!check_no_unknown_paid_action_record_fields(fields,
                                                        record.committed_paid_action_declaration_snapshot_present,
                                                        record.speculative_paid_action_declaration_snapshot_present,
                                                        error)) {
            return fail(line_number, error);
        }
        result.journal.records.push_back(std::move(parsed));
    }

    if (!seen_header_counts) {
        return fail(line_number == 0U ? 1U : line_number, "missing paid-action journal count/hash line");
    }
    result.ok = true;
    return result;
}

PaidActionTransactionJournalVerifyResult verify_paid_action_transaction_journal(std::string_view text) {
    PaidActionTransactionJournalVerifyResult result{};
    result.text_hash = paid_action_transaction_journal_text_hash(text);
    auto fail = [&result](PaidActionTransactionJournalVerifyFailureKind failure,
                          const PaidActionTransactionJournalParseResult& parse,
                          u64 line,
                          u64 record_index,
                          std::string message,
                          u64 expected = 0,
                          u64 actual = 0) -> PaidActionTransactionJournalVerifyResult {
        result.ok = false;
        result.failure = failure;
        result.parse = parse;
        result.error_line = line;
        result.record_index = record_index;
        result.error = std::move(message);
        result.expected = expected;
        result.actual = actual;
        return result;
    };

    auto parsed = parse_paid_action_transaction_journal(text);
    if (!parsed.ok) {
        return fail(PaidActionTransactionJournalVerifyFailureKind::ParseFailed,
                    parsed,
                    parsed.error_line,
                    0,
                    parsed.error);
    }
    if (parsed.journal.header.schema_version != kPaidActionTransactionJournalSchemaVersion) {
        return fail(PaidActionTransactionJournalVerifyFailureKind::UnsupportedSchema,
                    parsed,
                    1,
                    0,
                    "paid-action transaction journal schema is not the current fail-closed verifier schema",
                    kPaidActionTransactionJournalSchemaVersion,
                    parsed.journal.header.schema_version);
    }
    if (parsed.journal.header.record_count != parsed.journal.records.size()) {
        return fail(PaidActionTransactionJournalVerifyFailureKind::RecordCountMismatch,
                    parsed,
                    2,
                    0,
                    "journal record_count does not match parsed record lines",
                    parsed.journal.header.record_count,
                    parsed.journal.records.size());
    }

    u64 first_parsed_sequence = 0;
    u64 last_parsed_sequence = 0;
    for (std::size_t i = 0; i < parsed.journal.records.size(); ++i) {
        const auto& row = parsed.journal.records[i];
        const auto& record = row.transaction;
        const u64 expected_index = i + 1U;
        if (row.index != expected_index) {
            return fail(PaidActionTransactionJournalVerifyFailureKind::RecordCountMismatch,
                        parsed,
                        row.line_number,
                        row.index,
                        "record index is not contiguous",
                        expected_index,
                        row.index);
        }
        if (record.sequence == 0U) {
            return fail(PaidActionTransactionJournalVerifyFailureKind::RecordSequenceMismatch,
                        parsed,
                        row.line_number,
                        row.index,
                        "transaction record sequence must be nonzero");
        }
        if (last_parsed_sequence != 0U && record.sequence <= last_parsed_sequence) {
            return fail(PaidActionTransactionJournalVerifyFailureKind::RecordSequenceMismatch,
                        parsed,
                        row.line_number,
                        row.index,
                        "transaction record sequences must be strictly increasing",
                        last_parsed_sequence,
                        record.sequence);
        }
        if (first_parsed_sequence == 0U) {
            first_parsed_sequence = record.sequence;
        }
        last_parsed_sequence = record.sequence;
        const auto recomputed_transaction = paid_action_transaction_record_hash(record);
        if (row.exported_recomputed_transaction_hash != recomputed_transaction) {
            return fail(PaidActionTransactionJournalVerifyFailureKind::ExportedTransactionHashMismatch,
                        parsed,
                        row.line_number,
                        row.index,
                        "exported recomputed_transaction_hash does not match parsed transaction payload",
                        row.exported_recomputed_transaction_hash,
                        recomputed_transaction);
        }
        if (record.transaction_hash != recomputed_transaction) {
            return fail(PaidActionTransactionJournalVerifyFailureKind::TransactionHashMismatch,
                        parsed,
                        row.line_number,
                        row.index,
                        "transaction_hash does not match parsed transaction payload",
                        record.transaction_hash,
                        recomputed_transaction);
        }

        const bool committed_outcome = record.outcome == PaidActionTransactionOutcome::Committed;
        const bool rollback_outcome = record.outcome == PaidActionTransactionOutcome::RolledBack;
        if ((!committed_outcome && !rollback_outcome) ||
            record.committed != committed_outcome ||
            record.rolled_back != rollback_outcome ||
            (record.committed && record.rolled_back)) {
            return fail(PaidActionTransactionJournalVerifyFailureKind::OutcomeFlagMismatch,
                        parsed,
                        row.line_number,
                        row.index,
                        "transaction outcome and committed/rolled_back flags disagree");
        }
        if (record.schema_version != kPaidActionTransactionRecordSchemaVersion) {
            return fail(PaidActionTransactionJournalVerifyFailureKind::UnsupportedSchema,
                        parsed,
                        row.line_number,
                        row.index,
                        "transaction record schema is not the current fail-closed verifier schema",
                        kPaidActionTransactionRecordSchemaVersion,
                        record.schema_version);
        }
        if (committed_outcome) {
            if (record.physical_state_hash_before == 0U || record.physical_state_hash_after == 0U ||
                record.physical_state_hash_before == record.physical_state_hash_after) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::OutcomeFlagMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "committed transaction must expose distinct nonzero pre/post physical-state hashes",
                            record.physical_state_hash_before,
                            record.physical_state_hash_after);
            }
            if (!record.committed_paid_action_declaration_snapshot_present ||
                record.speculative_paid_action_declaration_snapshot_present) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::SnapshotPresenceMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "committed transaction must expose exactly one committed declaration snapshot");
            }
            const auto recomputed_snapshot = paid_action_declaration_record_hash(record.committed_paid_action_declaration_snapshot);
            if (row.exported_committed_snapshot_recomputed_hash != recomputed_snapshot) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::CommittedSnapshotHashMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "committed snapshot recomputed_hash field does not match parsed snapshot payload",
                            row.exported_committed_snapshot_recomputed_hash,
                            recomputed_snapshot);
            }
            if (record.committed_paid_action_declaration_snapshot.declaration_hash != recomputed_snapshot ||
                record.paid_action_declaration_hash != recomputed_snapshot) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::CommittedSnapshotHashMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "committed snapshot declaration hash does not match the transaction declaration link",
                            record.paid_action_declaration_hash,
                            recomputed_snapshot);
            }
        }
        if (rollback_outcome) {
            if (record.committed_paid_action_declaration_snapshot_present ||
                !record.speculative_paid_action_declaration_snapshot_present) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::SnapshotPresenceMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "rollback transaction must expose exactly one speculative declaration snapshot");
            }
            const auto recomputed_snapshot = paid_action_declaration_record_hash(record.speculative_paid_action_declaration_snapshot);
            if (row.exported_speculative_snapshot_recomputed_hash != recomputed_snapshot) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::SpeculativeSnapshotHashMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "speculative snapshot recomputed_hash field does not match parsed snapshot payload",
                            row.exported_speculative_snapshot_recomputed_hash,
                            recomputed_snapshot);
            }
            if (record.speculative_paid_action_declaration_hash != recomputed_snapshot) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::SpeculativeSnapshotHashMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "speculative declaration hash does not match parsed snapshot payload",
                            record.speculative_paid_action_declaration_hash,
                            recomputed_snapshot);
            }
            if (record.speculative_paid_action_declaration_snapshot.declaration_hash != 0U) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::SpeculativeSnapshotHashMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "rollback speculative snapshot must not claim a committed declaration row hash");
            }
            if (record.physical_state_preserved_on_rollback && record.physical_state_hash_before != record.physical_state_hash_after) {
                return fail(PaidActionTransactionJournalVerifyFailureKind::OutcomeFlagMismatch,
                            parsed,
                            row.line_number,
                            row.index,
                            "rollback marked physical_state_preserved_on_rollback but before/after hashes differ",
                            record.physical_state_hash_before,
                            record.physical_state_hash_after);
            }
        }
    }

    if (parsed.journal.header.first_transaction_sequence != first_parsed_sequence) {
        return fail(PaidActionTransactionJournalVerifyFailureKind::RecordSequenceMismatch,
                    parsed,
                    2,
                    0,
                    "first_transaction_sequence does not match the first parsed transaction row",
                    parsed.journal.header.first_transaction_sequence,
                    first_parsed_sequence);
    }
    if (parsed.journal.header.last_transaction_sequence != last_parsed_sequence) {
        return fail(PaidActionTransactionJournalVerifyFailureKind::RecordSequenceMismatch,
                    parsed,
                    2,
                    0,
                    "last_transaction_sequence does not match the last parsed transaction row",
                    parsed.journal.header.last_transaction_sequence,
                    last_parsed_sequence);
    }

    const auto recomputed_payload_hash = paid_action_transaction_journal_payload_hash_from_parsed_records(parsed.journal.records);
    if (parsed.journal.header.record_payload_hash != recomputed_payload_hash) {
        return fail(PaidActionTransactionJournalVerifyFailureKind::RecordPayloadHashMismatch,
                    parsed,
                    2,
                    0,
                    "record_payload_hash does not match the ordered parsed transaction rows",
                    parsed.journal.header.record_payload_hash,
                    recomputed_payload_hash);
    }

    result.ok = true;
    result.failure = PaidActionTransactionJournalVerifyFailureKind::None;
    result.parse = std::move(parsed);
    return result;
}

PaidActionTransactionJournalVerifyResult verify_paid_action_transaction_journal_for_state(const GameState& game, std::string_view text) {
    auto result = verify_paid_action_transaction_journal(text);
    if (!result.ok) {
        return result;
    }
    auto fail = [&result](u64 expected, u64 actual, std::string message) -> PaidActionTransactionJournalVerifyResult {
        result.ok = false;
        result.failure = PaidActionTransactionJournalVerifyFailureKind::StateBindingMismatch;
        result.error_line = 2;
        result.error = std::move(message);
        result.expected = expected;
        result.actual = actual;
        return result;
    };

    const auto& header = result.parse.journal.header;
    if (header.record_count != game.paid_action_transaction_records.size()) {
        return fail(header.record_count, game.paid_action_transaction_records.size(), "journal record_count does not match GameState");
    }
    if (header.declaration_record_count != game.paid_action_declaration_records.size()) {
        return fail(header.declaration_record_count, game.paid_action_declaration_records.size(), "journal declaration_record_count does not match GameState");
    }
    if (header.stack_placement_record_count != game.stack_placement_records.size()) {
        return fail(header.stack_placement_record_count, game.stack_placement_records.size(), "journal stack_placement_record_count does not match GameState");
    }
    const auto actual_journal_hash = journal_hash(game);
    if (header.journal_hash != actual_journal_hash) {
        return fail(header.journal_hash, actual_journal_hash, "journal_hash does not match GameState");
    }
    const auto actual_state_hash = canonical_state_hash(game);
    if (header.state_hash != actual_state_hash) {
        return fail(header.state_hash, actual_state_hash, "state_hash does not match GameState");
    }
    for (std::size_t i = 0; i < result.parse.journal.records.size(); ++i) {
        const auto& parsed_record = result.parse.journal.records[i].transaction;
        const auto& state_record = game.paid_action_transaction_records[i];
        if (parsed_record.transaction_hash != state_record.transaction_hash) {
            result.ok = false;
            result.failure = PaidActionTransactionJournalVerifyFailureKind::StateBindingMismatch;
            result.error_line = result.parse.journal.records[i].line_number;
            result.record_index = i + 1U;
            result.error = "parsed transaction hash does not match GameState transaction row";
            result.expected = state_record.transaction_hash;
            result.actual = parsed_record.transaction_hash;
            return result;
        }
    }
    return result;
}

std::string serialize_action_trace(const std::vector<ActionTraceEntry>& trace) {
    std::ostringstream out;
    out << "MTGSim.ActionTrace.v17\n";
    for (std::size_t i = 0; i < trace.size(); ++i) {
        const auto& entry = trace[i];
        const auto& action = entry.action;
        const auto targets = action_target_vector(action);
        out << "step=" << (i + 1U)
            << " kind=" << to_string(action.kind)
            << " player=" << action.player.value
            << " object=" << action.object.value
            << " mode=" << action.mode_index
            << " ability=" << action.ability_index
            << " mana=" << action.mana_ability_index
            << " applied=" << (entry.expected_applied ? 1 : 0)
            << " choice_kind=" << to_string(entry.expected_choice_kind)
            << " choice_schema=" << (entry.expected_choice_request_schema_version == 0U ? kChoiceRequestSchemaVersion : entry.expected_choice_request_schema_version)
            << " choice_hash=" << entry.expected_choice_request_hash
            << " choice_count=" << entry.expected_choice_action_count
            << " choice_required=" << (entry.expected_choice_required ? 1 : 0)
            << " choice_frontier_complete=" << (entry.expected_choice_action_frontier_complete ? 1 : 0)
            << " choice_generation_limit=" << entry.expected_choice_action_generation_limit
            << " choice_source=" << (entry.expected_choice_validation_source_present ? to_string(entry.expected_choice_validation_source) : "wildcard")
            << " choice_page_found=" << (entry.expected_choice_page_location_found ? 1 : 0)
            << " choice_page_checked=" << (entry.expected_choice_page_location_checked ? 1 : 0)
            << " choice_page_schema=" << entry.expected_choice_page_schema_version
            << " choice_page_state=" << entry.expected_choice_page_state_hash
            << " choice_page_request_hash=" << entry.expected_choice_page_choice_request_hash
            << " choice_page_requested=" << entry.expected_choice_page_requested_limit
            << " choice_page_limit=" << entry.expected_choice_page_effective_limit
            << " choice_page_cursor=" << entry.expected_choice_page_cursor
            << " choice_action_cursor=" << entry.expected_choice_action_cursor
            << " choice_page_index=" << entry.expected_choice_page_index
            << " choice_page_next=" << entry.expected_choice_page_next_cursor
            << " choice_page_seen=" << entry.expected_choice_page_actions_seen
            << " choice_page_scanned=" << entry.expected_choice_page_scanned_pages
            << " choice_page_complete=" << (entry.expected_choice_page_complete ? 1 : 0)
            << " choice_page_total_lower=" << entry.expected_choice_page_total_actions_lower_bound
            << " choice_page_total_exact=" << (entry.expected_choice_page_total_actions_exact ? 1 : 0)
            << " choice_page_remaining_lower=" << entry.expected_choice_page_remaining_actions_lower_bound
            << " choice_page_hash=" << entry.expected_choice_page_hash
            << " choice_page_location_hash=" << entry.expected_choice_page_location_hash
            << " choice_queue_schema=" << (entry.expected_choice_queue_schema_version == 0U ? kChoiceRequestQueueSchemaVersion : entry.expected_choice_queue_schema_version)
            << " choice_queue_hash=" << entry.expected_choice_queue_hash
            << " choice_queue_index=" << entry.expected_choice_queue_index
            << " choice_queue_size=" << entry.expected_choice_queue_size
            << " choice_queue_location_schema=" << entry.expected_choice_queue_location_schema_version
            << " choice_queue_found=" << (entry.expected_choice_queue_location_found ? 1 : 0)
            << " choice_queue_checked=" << (entry.expected_choice_queue_location_checked ? 1 : 0)
            << " choice_queue_location_hash=" << entry.expected_choice_queue_location_hash
            << " action_schema=" << (entry.expected_action_schema_version == 0U ? kLegalActionSchemaVersion : entry.expected_action_schema_version)
            << " action_hash=" << entry.expected_action_hash
            << " state_schema=" << (entry.expected_state_schema_version == 0U ? kStateCoreSchemaVersion : entry.expected_state_schema_version)
            << " state_before=" << entry.expected_state_hash_before
            << " state_after=" << entry.expected_state_hash_after
            << " trigger_order=" << serialize_trace_u32_list(action.trigger_order)
            << " targets=" << serialize_trace_targets(targets)
            << "\n";
    }
    return out.str();
}

ActionTraceParseResult parse_action_trace(std::string_view text) {
    ActionTraceParseResult result{};
    auto fail = [&result](u64 line, std::string message) -> ActionTraceParseResult {
        result.ok = false;
        result.trace.clear();
        result.error_line = line;
        result.error = std::move(message);
        return result;
    };

    std::istringstream input{std::string(text)};
    std::string line;
    u64 line_number = 0;
    if (!std::getline(input, line)) {
        return fail(1, "empty action trace");
    }
    ++line_number;
    if (!line.empty() && line.back() == '\r') {
        line.pop_back();
    }
    const bool is_v1_trace = line == "MTGSim.ActionTrace.v1";
    const bool is_v2_trace = line == "MTGSim.ActionTrace.v2";
    const bool is_v3_trace = line == "MTGSim.ActionTrace.v3";
    const bool is_v4_trace = line == "MTGSim.ActionTrace.v4";
    const bool is_v5_trace = line == "MTGSim.ActionTrace.v5";
    const bool is_v6_trace = line == "MTGSim.ActionTrace.v6";
    const bool is_v7_trace = line == "MTGSim.ActionTrace.v7";
    const bool is_v8_trace = line == "MTGSim.ActionTrace.v8";
    const bool is_v9_trace = line == "MTGSim.ActionTrace.v9";
    const bool is_v10_trace = line == "MTGSim.ActionTrace.v10";
    const bool is_v11_trace = line == "MTGSim.ActionTrace.v11";
    const bool is_v12_trace = line == "MTGSim.ActionTrace.v12";
    const bool is_v13_trace = line == "MTGSim.ActionTrace.v13";
    const bool is_v14_trace = line == "MTGSim.ActionTrace.v14";
    const bool is_v15_trace = line == "MTGSim.ActionTrace.v15";
    const bool is_v16_trace = line == "MTGSim.ActionTrace.v16";
    const bool is_v17_trace = line == "MTGSim.ActionTrace.v17";
    if (!is_v1_trace && !is_v2_trace && !is_v3_trace && !is_v4_trace && !is_v5_trace && !is_v6_trace && !is_v7_trace && !is_v8_trace && !is_v9_trace && !is_v10_trace && !is_v11_trace && !is_v12_trace && !is_v13_trace && !is_v14_trace && !is_v15_trace && !is_v16_trace && !is_v17_trace) {
        return fail(line_number, "missing MTGSim.ActionTrace.v1/v2/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16/v17 header");
    }

    u64 expected_step = 1;
    while (std::getline(input, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty()) {
            continue;
        }

        ActionTraceEntry entry{};
        u64 step = 0;
        bool seen_step = false;
        bool seen_kind = false;
        bool seen_player = false;
        bool seen_object = false;
        bool seen_mode = false;
        bool seen_ability = false;
        bool seen_mana = false;
        bool seen_applied = false;
        bool seen_choice_kind = false;
        bool seen_choice_schema = false;
        bool seen_choice_hash = false;
        bool seen_choice_count = false;
        bool seen_choice_required = false;
        bool seen_choice_frontier_complete = false;
        bool seen_choice_generation_limit = false;
        bool seen_choice_source = false;
        bool seen_choice_page_found = false;
        bool seen_choice_page_checked = false;
        bool seen_choice_page_schema = false;
        bool seen_choice_page_state = false;
        bool seen_choice_page_request_hash = false;
        bool seen_choice_page_requested = false;
        bool seen_choice_page_limit = false;
        bool seen_choice_page_cursor = false;
        bool seen_choice_action_cursor = false;
        bool seen_choice_page_index = false;
        bool seen_choice_page_next = false;
        bool seen_choice_page_seen = false;
        bool seen_choice_page_scanned = false;
        bool seen_choice_page_complete = false;
        bool seen_choice_page_total_lower = false;
        bool seen_choice_page_total_exact = false;
        bool seen_choice_page_remaining_lower = false;
        bool seen_choice_page_hash = false;
        bool seen_choice_page_location_hash = false;
        bool seen_choice_queue_schema = false;
        bool seen_choice_queue_hash = false;
        bool seen_choice_queue_index = false;
        bool seen_choice_queue_size = false;
        bool seen_choice_queue_location_schema = false;
        bool seen_choice_queue_found = false;
        bool seen_choice_queue_checked = false;
        bool seen_choice_queue_location_hash = false;
        bool seen_action_schema = false;
        bool seen_action_hash = false;
        bool seen_state_schema = false;
        bool seen_state_before = false;
        bool seen_state_after = false;
        bool seen_trigger_order = false;
        bool seen_targets = false;

        std::istringstream fields{line};
        std::string field;
        while (fields >> field) {
            const auto eq = field.find('=');
            if (eq == std::string::npos || eq == 0U) {
                return fail(line_number, "malformed key=value token");
            }
            const std::string_view key(field.data(), eq);
            const std::string_view value(field.data() + eq + 1U, field.size() - eq - 1U);
            if (key == "step") {
                if (seen_step || !parse_u64_text(value, step)) {
                    return fail(line_number, "invalid or duplicate step");
                }
                seen_step = true;
            } else if (key == "kind") {
                if (seen_kind || !parse_action_kind_text(value, entry.action.kind)) {
                    return fail(line_number, "invalid or duplicate action kind");
                }
                seen_kind = true;
            } else if (key == "player") {
                u32 parsed = 0;
                if (seen_player || !parse_u32_text(value, parsed)) {
                    return fail(line_number, "invalid or duplicate player");
                }
                entry.action.player = PlayerId{parsed};
                seen_player = true;
            } else if (key == "object") {
                u32 parsed = 0;
                if (seen_object || !parse_u32_text(value, parsed)) {
                    return fail(line_number, "invalid or duplicate object");
                }
                entry.action.object = ObjectId{parsed};
                seen_object = true;
            } else if (key == "mode") {
                if (seen_mode || !parse_u32_text(value, entry.action.mode_index)) {
                    return fail(line_number, "invalid or duplicate mode");
                }
                seen_mode = true;
            } else if (key == "ability") {
                if (seen_ability || !parse_u32_text(value, entry.action.ability_index)) {
                    return fail(line_number, "invalid or duplicate ability");
                }
                seen_ability = true;
            } else if (key == "mana") {
                if (seen_mana || !parse_u32_text(value, entry.action.mana_ability_index)) {
                    return fail(line_number, "invalid or duplicate mana ability");
                }
                seen_mana = true;
            } else if (key == "applied") {
                if (seen_applied || !parse_bool_text(value, entry.expected_applied)) {
                    return fail(line_number, "invalid or duplicate applied flag");
                }
                seen_applied = true;
            } else if (key == "choice_kind") {
                if (seen_choice_kind || !parse_choice_request_kind_text(value, entry.expected_choice_kind)) {
                    return fail(line_number, "invalid or duplicate choice kind");
                }
                seen_choice_kind = true;
            } else if (key == "choice_schema") {
                if (seen_choice_schema || !parse_u32_text(value, entry.expected_choice_request_schema_version)) {
                    return fail(line_number, "invalid or duplicate choice_schema");
                }
                seen_choice_schema = true;
            } else if (key == "choice_hash") {
                if (seen_choice_hash || !parse_u64_text(value, entry.expected_choice_request_hash)) {
                    return fail(line_number, "invalid or duplicate choice hash");
                }
                seen_choice_hash = true;
            } else if (key == "choice_count") {
                if (seen_choice_count || !parse_u64_text(value, entry.expected_choice_action_count)) {
                    return fail(line_number, "invalid or duplicate choice count");
                }
                seen_choice_count = true;
            } else if (key == "choice_required") {
                if (seen_choice_required || !parse_bool_text(value, entry.expected_choice_required)) {
                    return fail(line_number, "invalid or duplicate choice_required flag");
                }
                seen_choice_required = true;
            } else if (key == "choice_frontier_complete") {
                if (seen_choice_frontier_complete || !parse_bool_text(value, entry.expected_choice_action_frontier_complete)) {
                    return fail(line_number, "invalid or duplicate choice_frontier_complete flag");
                }
                seen_choice_frontier_complete = true;
            } else if (key == "choice_generation_limit") {
                if (seen_choice_generation_limit || !parse_u64_text(value, entry.expected_choice_action_generation_limit)) {
                    return fail(line_number, "invalid or duplicate choice_generation_limit");
                }
                seen_choice_generation_limit = true;
            } else if (key == "choice_source") {
                if (seen_choice_source) {
                    return fail(line_number, "invalid or duplicate choice_source");
                }
                if (value == "wildcard") {
                    entry.expected_choice_validation_source = LegalActionValidationSource::None;
                    entry.expected_choice_validation_source_present = false;
                } else {
                    if (!parse_legal_action_validation_source_text(value, entry.expected_choice_validation_source)) {
                        return fail(line_number, "invalid or duplicate choice_source");
                    }
                    entry.expected_choice_validation_source_present = true;
                }
                seen_choice_source = true;
            } else if (key == "choice_page_found") {
                if (seen_choice_page_found || !parse_bool_text(value, entry.expected_choice_page_location_found)) {
                    return fail(line_number, "invalid or duplicate choice_page_found flag");
                }
                seen_choice_page_found = true;
            } else if (key == "choice_page_checked") {
                if (seen_choice_page_checked || !parse_bool_text(value, entry.expected_choice_page_location_checked)) {
                    return fail(line_number, "invalid or duplicate choice_page_checked flag");
                }
                seen_choice_page_checked = true;
            } else if (key == "choice_page_schema") {
                if (seen_choice_page_schema || !parse_u32_text(value, entry.expected_choice_page_schema_version)) {
                    return fail(line_number, "invalid or duplicate choice_page_schema");
                }
                seen_choice_page_schema = true;
            } else if (key == "choice_page_state") {
                if (seen_choice_page_state || !parse_u64_text(value, entry.expected_choice_page_state_hash)) {
                    return fail(line_number, "invalid or duplicate choice_page_state");
                }
                seen_choice_page_state = true;
            } else if (key == "choice_page_request_hash") {
                if (seen_choice_page_request_hash || !parse_u64_text(value, entry.expected_choice_page_choice_request_hash)) {
                    return fail(line_number, "invalid or duplicate choice_page_request_hash");
                }
                seen_choice_page_request_hash = true;
            } else if (key == "choice_page_requested") {
                if (seen_choice_page_requested || !parse_u64_text(value, entry.expected_choice_page_requested_limit)) {
                    return fail(line_number, "invalid or duplicate choice_page_requested");
                }
                seen_choice_page_requested = true;
            } else if (key == "choice_page_limit") {
                if (seen_choice_page_limit || !parse_u64_text(value, entry.expected_choice_page_effective_limit)) {
                    return fail(line_number, "invalid or duplicate choice_page_limit");
                }
                seen_choice_page_limit = true;
            } else if (key == "choice_page_cursor") {
                if (seen_choice_page_cursor || !parse_u64_text(value, entry.expected_choice_page_cursor)) {
                    return fail(line_number, "invalid or duplicate choice_page_cursor");
                }
                seen_choice_page_cursor = true;
            } else if (key == "choice_action_cursor") {
                if (seen_choice_action_cursor || !parse_u64_text(value, entry.expected_choice_action_cursor)) {
                    return fail(line_number, "invalid or duplicate choice_action_cursor");
                }
                seen_choice_action_cursor = true;
            } else if (key == "choice_page_index") {
                if (seen_choice_page_index || !parse_u64_text(value, entry.expected_choice_page_index)) {
                    return fail(line_number, "invalid or duplicate choice_page_index");
                }
                seen_choice_page_index = true;
            } else if (key == "choice_page_next") {
                if (seen_choice_page_next || !parse_u64_text(value, entry.expected_choice_page_next_cursor)) {
                    return fail(line_number, "invalid or duplicate choice_page_next");
                }
                seen_choice_page_next = true;
            } else if (key == "choice_page_seen") {
                if (seen_choice_page_seen || !parse_u64_text(value, entry.expected_choice_page_actions_seen)) {
                    return fail(line_number, "invalid or duplicate choice_page_seen");
                }
                seen_choice_page_seen = true;
            } else if (key == "choice_page_scanned") {
                if (seen_choice_page_scanned || !parse_u64_text(value, entry.expected_choice_page_scanned_pages)) {
                    return fail(line_number, "invalid or duplicate choice_page_scanned");
                }
                seen_choice_page_scanned = true;
            } else if (key == "choice_page_complete") {
                if (seen_choice_page_complete || !parse_bool_text(value, entry.expected_choice_page_complete)) {
                    return fail(line_number, "invalid or duplicate choice_page_complete flag");
                }
                seen_choice_page_complete = true;
            } else if (key == "choice_page_total_lower") {
                if (seen_choice_page_total_lower || !parse_u64_text(value, entry.expected_choice_page_total_actions_lower_bound)) {
                    return fail(line_number, "invalid or duplicate choice_page_total_lower");
                }
                seen_choice_page_total_lower = true;
            } else if (key == "choice_page_total_exact") {
                if (seen_choice_page_total_exact || !parse_bool_text(value, entry.expected_choice_page_total_actions_exact)) {
                    return fail(line_number, "invalid or duplicate choice_page_total_exact flag");
                }
                seen_choice_page_total_exact = true;
            } else if (key == "choice_page_remaining_lower") {
                if (seen_choice_page_remaining_lower || !parse_u64_text(value, entry.expected_choice_page_remaining_actions_lower_bound)) {
                    return fail(line_number, "invalid or duplicate choice_page_remaining_lower");
                }
                seen_choice_page_remaining_lower = true;
            } else if (key == "choice_page_hash") {
                if (seen_choice_page_hash || !parse_u64_text(value, entry.expected_choice_page_hash)) {
                    return fail(line_number, "invalid or duplicate choice_page_hash");
                }
                seen_choice_page_hash = true;
            } else if (key == "choice_page_location_hash") {
                if (seen_choice_page_location_hash || !parse_u64_text(value, entry.expected_choice_page_location_hash)) {
                    return fail(line_number, "invalid or duplicate choice_page_location_hash");
                }
                seen_choice_page_location_hash = true;
            } else if (key == "choice_queue_schema") {
                if (is_v15_trace || is_v16_trace || is_v17_trace) {
                    if (seen_choice_queue_schema || !parse_u32_text(value, entry.expected_choice_queue_schema_version)) {
                        return fail(line_number, "invalid or duplicate choice_queue_schema");
                    }
                    seen_choice_queue_schema = true;
                } else {
                    // Backward compatibility: ActionTrace.v12-v14 used choice_queue_schema
                    // for the queue-location schema. v15 gives the queue hash protocol its
                    // own explicit field and moves the locator schema to choice_queue_location_schema.
                    if (seen_choice_queue_location_schema || !parse_u32_text(value, entry.expected_choice_queue_location_schema_version)) {
                        return fail(line_number, "invalid or duplicate choice_queue_schema");
                    }
                    seen_choice_queue_location_schema = true;
                }
            } else if (key == "choice_queue_hash") {
                if (seen_choice_queue_hash || !parse_u64_text(value, entry.expected_choice_queue_hash)) {
                    return fail(line_number, "invalid or duplicate choice queue hash");
                }
                seen_choice_queue_hash = true;
            } else if (key == "choice_queue_index") {
                if (seen_choice_queue_index || !parse_u64_text(value, entry.expected_choice_queue_index)) {
                    return fail(line_number, "invalid or duplicate choice queue index");
                }
                seen_choice_queue_index = true;
            } else if (key == "choice_queue_size") {
                if (seen_choice_queue_size || !parse_u64_text(value, entry.expected_choice_queue_size)) {
                    return fail(line_number, "invalid or duplicate choice queue size");
                }
                seen_choice_queue_size = true;
            } else if (key == "choice_queue_location_schema") {
                if (seen_choice_queue_location_schema || !parse_u32_text(value, entry.expected_choice_queue_location_schema_version)) {
                    return fail(line_number, "invalid or duplicate choice_queue_location_schema");
                }
                seen_choice_queue_location_schema = true;
            } else if (key == "choice_queue_found") {
                if (seen_choice_queue_found || !parse_bool_text(value, entry.expected_choice_queue_location_found)) {
                    return fail(line_number, "invalid or duplicate choice_queue_found flag");
                }
                seen_choice_queue_found = true;
            } else if (key == "choice_queue_checked") {
                if (seen_choice_queue_checked || !parse_bool_text(value, entry.expected_choice_queue_location_checked)) {
                    return fail(line_number, "invalid or duplicate choice_queue_checked flag");
                }
                seen_choice_queue_checked = true;
            } else if (key == "choice_queue_location_hash") {
                if (seen_choice_queue_location_hash || !parse_u64_text(value, entry.expected_choice_queue_location_hash)) {
                    return fail(line_number, "invalid or duplicate choice queue location hash");
                }
                seen_choice_queue_location_hash = true;
            } else if (key == "action_schema") {
                if (seen_action_schema || !parse_u32_text(value, entry.expected_action_schema_version)) {
                    return fail(line_number, "invalid or duplicate action_schema");
                }
                seen_action_schema = true;
            } else if (key == "action_hash") {
                if (seen_action_hash || !parse_u64_text(value, entry.expected_action_hash)) {
                    return fail(line_number, "invalid or duplicate action hash");
                }
                seen_action_hash = true;
            } else if (key == "state_schema") {
                if (seen_state_schema || !parse_u32_text(value, entry.expected_state_schema_version)) {
                    return fail(line_number, "invalid or duplicate state_schema");
                }
                seen_state_schema = true;
            } else if (key == "state_before") {
                if (seen_state_before || !parse_u64_text(value, entry.expected_state_hash_before)) {
                    return fail(line_number, "invalid or duplicate state_before hash");
                }
                seen_state_before = true;
            } else if (key == "state_after") {
                if (seen_state_after || !parse_u64_text(value, entry.expected_state_hash_after)) {
                    return fail(line_number, "invalid or duplicate state_after hash");
                }
                seen_state_after = true;
            } else if (key == "trigger_order") {
                if (seen_trigger_order || !parse_trace_u32_list(value, entry.action.trigger_order)) {
                    return fail(line_number, "invalid or duplicate trigger_order");
                }
                seen_trigger_order = true;
            } else if (key == "targets") {
                if (seen_targets || !parse_trace_targets(value, entry.action)) {
                    return fail(line_number, "invalid or duplicate targets");
                }
                seen_targets = true;
            } else {
                return fail(line_number, "unknown trace field: " + std::string(key));
            }
        }

        if (!seen_step || !seen_kind || !seen_player || !seen_object || !seen_mode ||
            !seen_ability || !seen_mana || !seen_applied || !seen_action_hash ||
            !seen_state_before || !seen_state_after || !seen_targets) {
            return fail(line_number, "missing required trace field");
        }
        if ((seen_choice_kind || seen_choice_schema || seen_choice_hash || seen_choice_count || seen_choice_required) &&
            !(seen_choice_kind && seen_choice_hash && seen_choice_count && seen_choice_required)) {
            return fail(line_number, "incomplete choice request fields");
        }
        const bool seen_any_choice_page_count = seen_choice_page_total_lower || seen_choice_page_total_exact || seen_choice_page_remaining_lower;
        const bool seen_all_v6_choice_page_count = seen_choice_page_total_lower && seen_choice_page_total_exact && seen_choice_page_remaining_lower;
        const bool seen_any_choice_page_context = seen_choice_page_state || seen_choice_page_request_hash;
        const bool seen_all_v7_choice_page_context = seen_choice_page_state && seen_choice_page_request_hash;
        const bool seen_any_choice_page_location_hash = seen_choice_page_location_hash;
        const bool seen_any_choice_page_location = seen_choice_page_found || seen_choice_page_schema || seen_choice_page_requested || seen_choice_page_limit ||
            seen_choice_page_cursor || seen_choice_action_cursor || seen_choice_page_index || seen_choice_page_next ||
            seen_choice_page_seen || seen_choice_page_scanned || seen_choice_page_complete || seen_choice_page_hash || seen_any_choice_page_location_hash || seen_any_choice_page_count || seen_any_choice_page_context;
        const bool seen_all_v3_choice_page_location = seen_choice_page_found && seen_choice_page_requested && seen_choice_page_limit &&
            seen_choice_page_cursor && seen_choice_action_cursor && seen_choice_page_index && seen_choice_page_next &&
            seen_choice_page_seen && seen_choice_page_scanned && seen_choice_page_complete;
        const bool seen_all_v4_choice_page_location = seen_all_v3_choice_page_location && seen_choice_page_hash;
        const bool seen_all_v5_choice_page_location = seen_all_v4_choice_page_location && seen_choice_page_schema;
        const bool seen_all_v6_choice_page_location = seen_all_v5_choice_page_location && seen_all_v6_choice_page_count;
        const bool seen_all_v7_choice_page_location = seen_all_v6_choice_page_location && seen_all_v7_choice_page_context;
        const bool seen_all_v8_choice_page_location = seen_all_v7_choice_page_location && seen_choice_page_checked;
        const bool seen_all_v9_choice_page_location = seen_all_v8_choice_page_location && seen_choice_page_location_hash;
        const bool is_v9_or_newer = is_v9_trace || is_v10_trace || is_v11_trace || is_v12_trace || is_v13_trace || is_v14_trace || is_v15_trace || is_v16_trace || is_v17_trace;
        const bool is_v8_or_newer = is_v8_trace || is_v9_or_newer;
        const bool is_v7_or_newer = is_v7_trace || is_v8_or_newer;
        const bool is_v6_or_newer = is_v6_trace || is_v7_or_newer;
        const bool is_v5_or_newer = is_v5_trace || is_v6_or_newer;
        const bool is_v4_or_newer = is_v4_trace || is_v5_or_newer;
        const bool is_v3_or_newer = is_v3_trace || is_v4_or_newer;
        const bool is_v2_or_newer = is_v2_trace || is_v3_or_newer;
        const bool seen_all_choice_page_location = is_v9_or_newer ? seen_all_v9_choice_page_location : (is_v8_trace ? seen_all_v8_choice_page_location : (is_v7_trace ? seen_all_v7_choice_page_location : (is_v6_trace ? seen_all_v6_choice_page_location : (is_v5_trace ? seen_all_v5_choice_page_location : (is_v4_trace ? seen_all_v4_choice_page_location : seen_all_v3_choice_page_location)))));
        if (is_v2_or_newer && !(seen_choice_frontier_complete && seen_choice_generation_limit && seen_choice_source)) {
            return fail(line_number, "missing v2/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16 choice frontier/source fields");
        }
        if (is_v3_trace && !seen_all_v3_choice_page_location) {
            return fail(line_number, "missing v3 choice page-location fields");
        }
        if (is_v4_trace && !seen_all_v4_choice_page_location) {
            return fail(line_number, "missing v4 choice page-location hash fields");
        }
        if (is_v5_trace && !seen_all_v5_choice_page_location) {
            return fail(line_number, "missing v5 choice page schema/hash fields");
        }
        if (is_v6_trace && !seen_all_v6_choice_page_location) {
            return fail(line_number, "missing v6 choice page count/schema/hash fields");
        }
        if (is_v7_trace && !seen_all_v7_choice_page_location) {
            return fail(line_number, "missing v7 choice page context/count/schema/hash fields");
        }
        if (is_v8_trace && !seen_all_v8_choice_page_location) {
            return fail(line_number, "missing v8 choice page proof/context/count/schema/hash fields");
        }
        if (is_v9_trace && !seen_all_v9_choice_page_location) {
            return fail(line_number, "missing v9 choice page proof location hash fields");
        }
        if (!is_v4_or_newer && seen_choice_page_hash) {
            return fail(line_number, "v4/v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16 choice page hash field in older trace");
        }
        if (!is_v5_or_newer && seen_choice_page_schema) {
            return fail(line_number, "v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16 choice page schema field in older trace");
        }
        if (!is_v6_or_newer && seen_any_choice_page_count) {
            return fail(line_number, "v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16 choice page count field in older trace");
        }
        if (!is_v7_or_newer && seen_any_choice_page_context) {
            return fail(line_number, "v7/v8/v9/v10/v11/v12/v13/v14/v15/v16 choice page context field in older trace");
        }
        if (!is_v8_or_newer && seen_choice_page_checked) {
            return fail(line_number, "v8/v9/v10/v11/v12/v13/v14/v15/v16 choice page proof field in older trace");
        }
        if (!is_v9_or_newer && seen_choice_page_location_hash) {
            return fail(line_number, "v9/v10/v11/v12/v13/v14/v15/v16 choice page location hash field in older trace");
        }
        if (!is_v3_or_newer && seen_any_choice_page_location) {
            return fail(line_number, "v3/v4/v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16 choice page-location field in older trace");
        }
        if (seen_any_choice_page_location && !seen_all_choice_page_location) {
            return fail(line_number, "incomplete choice page-location fields");
        }
        entry.expected_choice_page_location_present = seen_all_choice_page_location;
        entry.expected_choice_page_count_present = seen_all_v6_choice_page_count;
        entry.expected_choice_page_context_present = seen_all_v7_choice_page_context;
        if (!is_v8_or_newer && entry.expected_choice_page_location_present) {
            entry.expected_choice_page_location_checked = entry.expected_choice_page_location_found;
        }
        if (is_v8_or_newer && entry.expected_applied && !entry.expected_choice_page_location_checked) {
            return fail(line_number, "applied v8/v9/v10/v11/v12/v13/v14/v15/v16 action lacks checked choice page proof");
        }
        if (is_v9_or_newer && entry.expected_applied && entry.expected_choice_page_location_checked && entry.expected_choice_page_location_hash == 0U) {
            return fail(line_number, "applied v9/v10/v11/v12/v13/v14/v15/v16 action lacks nonzero choice page location hash");
        }
        if (is_v1_trace && (seen_choice_frontier_complete || seen_choice_generation_limit || seen_choice_source)) {
            return fail(line_number, "v2/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16 choice frontier/source field in v1 trace");
        }

        const bool is_v10_or_newer = is_v10_trace || is_v11_trace || is_v12_trace || is_v13_trace || is_v14_trace || is_v15_trace || is_v16_trace || is_v17_trace;
        const bool is_v11_or_newer = is_v11_trace || is_v12_trace || is_v13_trace || is_v14_trace || is_v15_trace || is_v16_trace || is_v17_trace;
        const bool is_v12_or_newer = is_v12_trace || is_v13_trace || is_v14_trace || is_v15_trace || is_v16_trace || is_v17_trace;
        const bool is_v13_or_newer = is_v13_trace || is_v14_trace || is_v15_trace || is_v16_trace || is_v17_trace;
        const bool is_v14_or_newer = is_v14_trace || is_v15_trace || is_v16_trace || is_v17_trace;
        const bool seen_any_choice_queue_proof = seen_choice_queue_location_hash || seen_choice_queue_location_schema || seen_choice_queue_found || seen_choice_queue_checked;
        const bool seen_all_v11_choice_queue_proof = seen_choice_queue_location_hash && seen_choice_queue_found && seen_choice_queue_checked;
        const bool seen_all_v12_choice_queue_proof = seen_all_v11_choice_queue_proof && seen_choice_queue_location_schema;
        if (!is_v10_or_newer && seen_choice_queue_location_hash) {
            return fail(line_number, "v10/v11/v12/v13/v14/v15/v16 choice queue location hash field in older trace");
        }
        if (!is_v11_or_newer && (seen_choice_queue_found || seen_choice_queue_checked)) {
            return fail(line_number, "v11/v12/v13/v14/v15/v16 choice queue proof sentinel field in older trace");
        }
        if (!is_v12_or_newer && seen_choice_queue_location_schema) {
            return fail(line_number, "v12/v13/v14/v15/v16 choice queue location schema field in older trace");
        }
        if (is_v10_or_newer && !seen_choice_queue_location_hash) {
            return fail(line_number, "missing v10/v11/v12/v13/v14/v15/v16 choice queue location hash field");
        }
        if (is_v11_trace && !seen_all_v11_choice_queue_proof) {
            return fail(line_number, "missing v11 choice queue proof sentinel fields");
        }
        if (is_v12_or_newer && !seen_all_v12_choice_queue_proof) {
            return fail(line_number, "missing v12/v13/v14/v15/v16 choice queue location schema/proof sentinel fields");
        }
        if (is_v10_trace && entry.expected_choice_queue_location_hash != 0U) {
            entry.expected_choice_queue_location_schema_version = kChoiceQueueLocationSchemaVersion;
            entry.expected_choice_queue_location_found = true;
            entry.expected_choice_queue_location_checked = true;
        }
        if (is_v11_trace && entry.expected_choice_queue_location_hash != 0U) {
            entry.expected_choice_queue_location_schema_version = kChoiceQueueLocationSchemaVersion;
        }
        if (is_v11_or_newer && entry.expected_applied && !entry.expected_choice_queue_location_checked) {
            return fail(line_number, "applied v11/v12/v13/v14/v15/v16 action lacks checked choice queue proof");
        }
        if (is_v11_or_newer && entry.expected_applied && !entry.expected_choice_queue_location_found) {
            return fail(line_number, "applied v11/v12/v13/v14/v15/v16 action lacks positive choice queue proof");
        }
        if ((is_v10_trace && entry.expected_applied && entry.expected_choice_queue_location_hash == 0U) ||
            (is_v11_or_newer && entry.expected_choice_queue_location_checked && entry.expected_choice_queue_location_hash == 0U)) {
            return fail(line_number, "checked v10/v11/v12/v13/v14/v15/v16 choice queue proof lacks nonzero location hash");
        }
        if (is_v12_or_newer && entry.expected_choice_queue_location_checked && entry.expected_choice_queue_location_schema_version == 0U) {
            return fail(line_number, "checked v12/v13/v14/v15/v16 choice queue proof lacks nonzero location schema version");
        }
        if ((seen_choice_queue_hash || seen_choice_queue_index || seen_choice_queue_size || seen_any_choice_queue_proof) &&
            !(seen_choice_queue_hash && seen_choice_queue_index && seen_choice_queue_size &&
              ((!is_v10_or_newer) || (is_v10_trace && seen_choice_queue_location_hash) || (is_v11_trace && seen_all_v11_choice_queue_proof) || (is_v12_or_newer && seen_all_v12_choice_queue_proof)))) {
            return fail(line_number, "incomplete choice queue fields");
        }

        const bool is_v15_or_newer = is_v15_trace || is_v16_trace || is_v17_trace;
        if (!is_v15_or_newer && seen_choice_queue_schema) {
            return fail(line_number, "v15/v16 choice queue schema field in older trace");
        }
        if (is_v15_or_newer && !seen_choice_queue_schema) {
            return fail(line_number, "missing v15/v16 choice queue schema field");
        }
        if (!is_v15_or_newer && seen_choice_queue_hash) {
            entry.expected_choice_queue_schema_version = kChoiceRequestQueueSchemaVersion;
        }
        if (is_v15_or_newer && entry.expected_choice_queue_schema_version == 0U) {
            return fail(line_number, "v15/v16 choice queue schema must be nonzero");
        }

        if (!is_v14_or_newer && seen_choice_schema) {
            return fail(line_number, "v14 choice request schema field in older trace");
        }
        if (is_v14_or_newer && !seen_choice_schema) {
            return fail(line_number, "missing v14/v15/v16 choice request schema field");
        }
        if (!is_v14_or_newer && seen_choice_hash) {
            entry.expected_choice_request_schema_version = kChoiceRequestSchemaVersion;
        }
        if (is_v14_or_newer && entry.expected_choice_request_schema_version == 0U) {
            return fail(line_number, "v14/v15/v16 choice request schema must be nonzero");
        }
        if (!is_v13_or_newer && seen_action_schema) {
            return fail(line_number, "v13/v14/v15/v16 action schema field in older trace");
        }
        if (is_v13_or_newer && !seen_action_schema) {
            return fail(line_number, "missing v13/v14/v15/v16 action schema field");
        }
        if (!is_v13_or_newer && seen_action_hash) {
            entry.expected_action_schema_version = kLegalActionSchemaVersion;
        }
        if (is_v13_or_newer && entry.expected_action_schema_version == 0U) {
            return fail(line_number, "v13/v14/v15/v16 action schema must be nonzero");
        }
        const bool is_v16_or_newer = is_v16_trace || is_v17_trace;
        if (!is_v16_or_newer && seen_state_schema) {
            return fail(line_number, "v16/v17 state schema field in older trace");
        }
        if (is_v16_or_newer && !seen_state_schema) {
            return fail(line_number, "missing v16/v17 state schema field");
        }
        if (!is_v16_or_newer && (seen_state_before || seen_state_after)) {
            entry.expected_state_schema_version = kStateCoreSchemaVersion;
        }
        if (is_v16_or_newer && entry.expected_state_schema_version == 0U) {
            return fail(line_number, "v16/v17 state schema must be nonzero");
        }
        if (!is_v17_trace && seen_trigger_order) {
            return fail(line_number, "v17 trigger_order field in older trace");
        }
        if (is_v17_trace && !seen_trigger_order) {
            return fail(line_number, "missing v17 trigger_order field");
        }
        if (step != expected_step) {
            return fail(line_number, "non-contiguous trace step");
        }

        result.trace.push_back(std::move(entry));
        ++expected_step;
    }

    result.ok = true;
    return result;
}

StateCheckpointSeal make_state_checkpoint_seal(const GameState& game) noexcept {
    StateCheckpointSeal checkpoint{};
    checkpoint.state_hash = canonical_state_hash(game);
    checkpoint.journal_hash = journal_hash(game);
    checkpoint.journal_entries = static_cast<u64>(journal_entry_count(game));
    checkpoint.action_receipts = static_cast<u64>(game.action_receipt_records.size());
    checkpoint.object_count = static_cast<u64>(game.objects.size());
    checkpoint.player_count = static_cast<u64>(game.players.size());
    checkpoint.stack_size = static_cast<u64>(game.stack.size());
    checkpoint.rng_state = game.rng_state;
    checkpoint.next_zone_change_index = game.next_zone_change_index;
    checkpoint.next_event_sequence = game.next_event_sequence;
    checkpoint.turn_number = game.turn_number;
    checkpoint.step = game.step;
    checkpoint.active_player = game.active_player;
    checkpoint.priority_player = game.priority_player;
    checkpoint.journal_trimmed = game.journal_trimmed;
    return checkpoint;
}

bool verify_state_checkpoint_seal(const GameState& game, const StateCheckpointSeal& checkpoint) noexcept {
    return checkpoint.schema_version == kStateCheckpointSealSchemaVersion &&
           checkpoint.state_hash == canonical_state_hash(game) &&
           checkpoint.journal_hash == journal_hash(game) &&
           checkpoint.journal_entries == static_cast<u64>(journal_entry_count(game)) &&
           checkpoint.action_receipts == static_cast<u64>(game.action_receipt_records.size()) &&
           checkpoint.object_count == static_cast<u64>(game.objects.size()) &&
           checkpoint.player_count == static_cast<u64>(game.players.size()) &&
           checkpoint.stack_size == static_cast<u64>(game.stack.size()) &&
           checkpoint.rng_state == game.rng_state &&
           checkpoint.next_zone_change_index == game.next_zone_change_index &&
           checkpoint.next_event_sequence == game.next_event_sequence &&
           checkpoint.turn_number == game.turn_number &&
           checkpoint.step == game.step &&
           checkpoint.active_player == game.active_player &&
           checkpoint.priority_player == game.priority_player &&
           checkpoint.journal_trimmed == game.journal_trimmed;
}

std::string serialize_state_checkpoint_seal(const StateCheckpointSeal& checkpoint) {
    std::ostringstream out;
    out << "MTGSim.StateCheckpointSeal.v2\n"
        << "checkpoint_schema=" << checkpoint.schema_version
        << " state_hash=" << checkpoint.state_hash
        << " journal_hash=" << checkpoint.journal_hash
        << " journal_entries=" << checkpoint.journal_entries
        << " action_receipts=" << checkpoint.action_receipts
        << " objects=" << checkpoint.object_count
        << " players=" << checkpoint.player_count
        << " stack=" << checkpoint.stack_size
        << " rng=" << checkpoint.rng_state
        << " next_zone_change=" << checkpoint.next_zone_change_index
        << " next_event_sequence=" << checkpoint.next_event_sequence
        << " turn=" << checkpoint.turn_number
        << " step=" << to_string(checkpoint.step)
        << " active=" << checkpoint.active_player.value
        << " priority=" << checkpoint.priority_player.value
        << " journal_trimmed=" << (checkpoint.journal_trimmed ? 1 : 0)
        << "\n";
    return out.str();
}

StateCheckpointParseResult parse_state_checkpoint_seal(std::string_view text) {
    StateCheckpointParseResult result{};
    auto fail = [&result](u64 line, std::string message) -> StateCheckpointParseResult {
        result.ok = false;
        result.checkpoint = StateCheckpointSeal{};
        result.error_line = line;
        result.error = std::move(message);
        return result;
    };

    std::istringstream input{std::string(text)};
    std::string line;
    u64 line_number = 0;
    if (!std::getline(input, line)) {
        return fail(1, "empty checkpoint seal");
    }
    ++line_number;
    if (!line.empty() && line.back() == '\r') {
        line.pop_back();
    }
    const bool is_v1_checkpoint = line == "MTGSim.StateCheckpointSeal.v1";
    const bool is_v2_checkpoint = line == "MTGSim.StateCheckpointSeal.v2";
    if (!is_v1_checkpoint && !is_v2_checkpoint) {
        return fail(line_number, "missing MTGSim.StateCheckpointSeal.v1/v2 header");
    }
    result.checkpoint.schema_version = is_v1_checkpoint ? 1U : kStateCheckpointSealSchemaVersion;

    bool seen_data = false;
    while (std::getline(input, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty()) {
            continue;
        }
        if (seen_data) {
            return fail(line_number, "checkpoint seal should contain exactly one data line");
        }
        seen_data = true;

        bool seen_checkpoint_schema = false;
        bool seen_state_hash = false;
        bool seen_journal_hash = false;
        bool seen_journal_entries = false;
        bool seen_action_receipts = false;
        bool seen_objects = false;
        bool seen_players = false;
        bool seen_stack = false;
        bool seen_rng = false;
        bool seen_next_zone_change = false;
        bool seen_next_event_sequence = false;
        bool seen_turn = false;
        bool seen_step = false;
        bool seen_active = false;
        bool seen_priority = false;
        bool seen_journal_trimmed = false;

        std::istringstream fields{line};
        std::string field;
        while (fields >> field) {
            const auto eq = field.find('=');
            if (eq == std::string::npos || eq == 0U) {
                return fail(line_number, "malformed checkpoint key=value token");
            }
            const std::string_view key(field.data(), eq);
            const std::string_view value(field.data() + eq + 1U, field.size() - eq - 1U);
            if (key == "checkpoint_schema") {
                if (!is_v2_checkpoint || seen_checkpoint_schema || !parse_u32_text(value, result.checkpoint.schema_version) || result.checkpoint.schema_version == 0U) {
                    return fail(line_number, "invalid or duplicate checkpoint_schema");
                }
                seen_checkpoint_schema = true;
            } else if (key == "state_hash") {
                if (seen_state_hash || !parse_u64_text(value, result.checkpoint.state_hash)) {
                    return fail(line_number, "invalid or duplicate state_hash");
                }
                seen_state_hash = true;
            } else if (key == "journal_hash") {
                if (seen_journal_hash || !parse_u64_text(value, result.checkpoint.journal_hash)) {
                    return fail(line_number, "invalid or duplicate journal_hash");
                }
                seen_journal_hash = true;
            } else if (key == "journal_entries") {
                if (seen_journal_entries || !parse_u64_text(value, result.checkpoint.journal_entries)) {
                    return fail(line_number, "invalid or duplicate journal_entries");
                }
                seen_journal_entries = true;
            } else if (key == "action_receipts") {
                if (seen_action_receipts || !parse_u64_text(value, result.checkpoint.action_receipts)) {
                    return fail(line_number, "invalid or duplicate action_receipts");
                }
                seen_action_receipts = true;
            } else if (key == "objects") {
                if (seen_objects || !parse_u64_text(value, result.checkpoint.object_count)) {
                    return fail(line_number, "invalid or duplicate objects");
                }
                seen_objects = true;
            } else if (key == "players") {
                if (seen_players || !parse_u64_text(value, result.checkpoint.player_count)) {
                    return fail(line_number, "invalid or duplicate players");
                }
                seen_players = true;
            } else if (key == "stack") {
                if (seen_stack || !parse_u64_text(value, result.checkpoint.stack_size)) {
                    return fail(line_number, "invalid or duplicate stack");
                }
                seen_stack = true;
            } else if (key == "rng") {
                if (seen_rng || !parse_u64_text(value, result.checkpoint.rng_state)) {
                    return fail(line_number, "invalid or duplicate rng");
                }
                seen_rng = true;
            } else if (key == "next_zone_change") {
                if (seen_next_zone_change || !parse_u64_text(value, result.checkpoint.next_zone_change_index)) {
                    return fail(line_number, "invalid or duplicate next_zone_change");
                }
                seen_next_zone_change = true;
            } else if (key == "next_event_sequence") {
                if (seen_next_event_sequence || !parse_u64_text(value, result.checkpoint.next_event_sequence)) {
                    return fail(line_number, "invalid or duplicate next_event_sequence");
                }
                seen_next_event_sequence = true;
            } else if (key == "turn") {
                if (seen_turn || !parse_u32_text(value, result.checkpoint.turn_number)) {
                    return fail(line_number, "invalid or duplicate turn");
                }
                seen_turn = true;
            } else if (key == "step") {
                if (seen_step || !parse_step_text(value, result.checkpoint.step)) {
                    return fail(line_number, "invalid or duplicate step");
                }
                seen_step = true;
            } else if (key == "active") {
                u32 parsed = 0;
                if (seen_active || !parse_u32_text(value, parsed)) {
                    return fail(line_number, "invalid or duplicate active player");
                }
                result.checkpoint.active_player = PlayerId{parsed};
                seen_active = true;
            } else if (key == "priority") {
                u32 parsed = 0;
                if (seen_priority || !parse_u32_text(value, parsed)) {
                    return fail(line_number, "invalid or duplicate priority player");
                }
                result.checkpoint.priority_player = PlayerId{parsed};
                seen_priority = true;
            } else if (key == "journal_trimmed") {
                if (seen_journal_trimmed || !parse_bool_text(value, result.checkpoint.journal_trimmed)) {
                    return fail(line_number, "invalid or duplicate journal_trimmed flag");
                }
                seen_journal_trimmed = true;
            } else {
                return fail(line_number, "unknown checkpoint field: " + std::string(key));
            }
        }

        if ((is_v2_checkpoint && !seen_checkpoint_schema) || !seen_state_hash || !seen_journal_hash || !seen_journal_entries || !seen_action_receipts ||
            !seen_objects || !seen_players || !seen_stack || !seen_rng || !seen_next_zone_change ||
            !seen_next_event_sequence || !seen_turn || !seen_step || !seen_active || !seen_priority ||
            !seen_journal_trimmed) {
            return fail(line_number, "missing required checkpoint field");
        }
    }

    if (!seen_data) {
        return fail(line_number + 1U, "missing checkpoint seal data line");
    }
    result.ok = true;
    return result;
}


std::string serialize_state_core_snapshot(const GameState& game) {
    StateCoreSnapshotWriter writer;
    writer.out << "MTGSim.StateCoreSnapshot.v1\n";
    write_checkpoint_snapshot(writer, "source_checkpoint", make_state_checkpoint_seal(game));
    write_game_core_snapshot(writer, "game", game);
    writer.u64_value("snapshot.state_hash", canonical_state_hash(game));
    return writer.out.str();
}

StateCoreSnapshotParseResult parse_state_core_snapshot(std::string_view text) {
    StateCoreSnapshotParseResult result{};
    auto fail = [&result](u64 line, std::string message) -> StateCoreSnapshotParseResult {
        result.ok = false;
        result.game = GameState{};
        result.source_checkpoint = StateCheckpointSeal{};
        result.error_line = line;
        result.error = std::move(message);
        return result;
    };

    StateCoreSnapshotReader reader{text};
    if (!reader.read_header("MTGSim.StateCoreSnapshot.v1")) {
        return fail(reader.line_number == 0U ? 1U : reader.line_number, reader.error);
    }

    StateCheckpointSeal checkpoint{};
    GameState parsed{};
    u64 expected_state_hash = 0;
    if (!read_checkpoint_snapshot(reader, "source_checkpoint", checkpoint) ||
        !read_game_core_snapshot(reader, "game", parsed) ||
        !reader.read_u64("snapshot.state_hash", expected_state_hash) ||
        !reader.finish()) {
        return fail(reader.line_number == 0U ? 1U : reader.line_number, reader.error);
    }

    const auto actual_state_hash = canonical_state_hash(parsed);
    if (expected_state_hash != actual_state_hash) {
        return fail(reader.line_number, "StateCore snapshot hash mismatch");
    }
    if (checkpoint.state_hash != expected_state_hash) {
        return fail(reader.line_number, "source checkpoint hash does not match snapshot StateCore");
    }
    if (checkpoint.object_count != static_cast<u64>(parsed.objects.size()) ||
        checkpoint.player_count != static_cast<u64>(parsed.players.size()) ||
        checkpoint.stack_size != static_cast<u64>(parsed.stack.size()) ||
        checkpoint.rng_state != parsed.rng_state ||
        checkpoint.next_zone_change_index != parsed.next_zone_change_index ||
        checkpoint.next_event_sequence != parsed.next_event_sequence ||
        checkpoint.turn_number != parsed.turn_number ||
        checkpoint.step != parsed.step ||
        checkpoint.active_player != parsed.active_player ||
        checkpoint.priority_player != parsed.priority_player) {
        return fail(reader.line_number, "source checkpoint metadata does not match snapshot StateCore");
    }

    result.ok = true;
    result.game = std::move(parsed);
    result.source_checkpoint = checkpoint;
    return result;
}

namespace {

[[nodiscard]] u64 replay_artifact_manifest_payload_hash_v1(const ReplayArtifactManifest& manifest) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ReplayArtifactManifest.v1.payload");
    hash_into(h, manifest.snapshot_format);
    hash_into(h, manifest.trace_format);
    hash_into(h, manifest.snapshot_text_hash);
    hash_into(h, manifest.trace_text_hash);
    hash_into(h, manifest.checkpoint_state_hash);
    hash_into(h, manifest.checkpoint_journal_hash);
    hash_into(h, manifest.checkpoint_journal_entries);
    hash_into(h, manifest.action_count);
    hash_into(h, manifest.final_state_hash);
    hash_into(h, manifest.applied_only);
    return h.value();
}

[[nodiscard]] u64 replay_artifact_manifest_payload_hash_v2(const ReplayArtifactManifest& manifest) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ReplayArtifactManifest.v2.payload");
    hash_into(h, manifest.schema_version);
    hash_into(h, manifest.snapshot_format);
    hash_into(h, manifest.trace_format);
    hash_into(h, manifest.snapshot_text_hash);
    hash_into(h, manifest.trace_text_hash);
    hash_into(h, manifest.checkpoint_state_hash);
    hash_into(h, manifest.checkpoint_journal_hash);
    hash_into(h, manifest.checkpoint_journal_entries);
    hash_into(h, manifest.action_count);
    hash_into(h, manifest.final_state_hash);
    hash_into(h, manifest.applied_only);
    return h.value();
}

[[nodiscard]] u64 replay_artifact_manifest_payload_hash(const ReplayArtifactManifest& manifest) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ReplayArtifactManifest.v3.payload");
    hash_into(h, manifest.schema_version);
    hash_into(h, manifest.snapshot_format);
    hash_into(h, manifest.trace_format);
    hash_into(h, manifest.snapshot_text_hash);
    hash_into(h, manifest.trace_text_hash);
    hash_into(h, manifest.checkpoint_state_hash);
    hash_into(h, manifest.checkpoint_journal_hash);
    hash_into(h, manifest.checkpoint_journal_entries);
    hash_into(h, manifest.action_count);
    hash_into(h, manifest.final_state_hash);
    hash_into(h, manifest.applied_only);
    hash_into(h, manifest.paid_action_journal_attached);
    hash_into(h, manifest.paid_action_journal_format);
    hash_into(h, manifest.paid_action_journal_text_hash);
    hash_into(h, manifest.paid_action_journal_record_count);
    hash_into(h, manifest.paid_action_journal_state_hash);
    hash_into(h, manifest.paid_action_journal_journal_hash);
    hash_into(h, manifest.paid_action_journal_record_payload_hash);
    return h.value();
}

[[nodiscard]] bool manifest_format_fields_are_current(const ReplayArtifactManifest& manifest) noexcept {
    const bool paid_action_journal_format_ok = manifest.paid_action_journal_attached
        ? manifest.paid_action_journal_format == "MTGSim.PaidActionTransactionJournal.v9"
        : manifest.paid_action_journal_format == "none";
    return manifest.schema_version == kReplayArtifactManifestSchemaVersion &&
           manifest.snapshot_format == "MTGSim.StateCoreSnapshot.v1" &&
           (manifest.trace_format == "MTGSim.ActionTrace.v10" ||
            manifest.trace_format == "MTGSim.ActionTrace.v11" ||
            manifest.trace_format == "MTGSim.ActionTrace.v12" ||
            manifest.trace_format == "MTGSim.ActionTrace.v13" ||
            manifest.trace_format == "MTGSim.ActionTrace.v14" ||
            manifest.trace_format == "MTGSim.ActionTrace.v15" ||
            manifest.trace_format == "MTGSim.ActionTrace.v16" ||
            manifest.trace_format == "MTGSim.ActionTrace.v17") &&
           paid_action_journal_format_ok;
}

[[nodiscard]] ReplayArtifactManifest make_replay_artifact_manifest_with_expected_final(std::string_view snapshot_text,
                                                                                       std::string_view trace_text,
                                                                                       u64 expected_final_state_hash,
                                                                                       bool applied_only) {
    ReplayArtifactManifest manifest{};
    manifest.snapshot_text_hash = replay_artifact_text_hash(snapshot_text);
    manifest.trace_text_hash = replay_artifact_text_hash(trace_text);
    const auto snapshot = parse_state_core_snapshot(snapshot_text);
    if (snapshot.ok) {
        manifest.checkpoint_state_hash = snapshot.source_checkpoint.state_hash;
        manifest.checkpoint_journal_hash = snapshot.source_checkpoint.journal_hash;
        manifest.checkpoint_journal_entries = snapshot.source_checkpoint.journal_entries;
    }
    const auto trace = parse_action_trace(trace_text);
    if (trace.ok) {
        manifest.action_count = static_cast<u64>(trace.trace.size());
    }
    manifest.final_state_hash = expected_final_state_hash;
    manifest.applied_only = applied_only;
    manifest.bundle_hash = replay_artifact_manifest_payload_hash(manifest);
    return manifest;
}

} // namespace

std::uint64_t replay_artifact_text_hash(std::string_view text) noexcept {
    StableHasher h;
    h.add_string("MTGSim.ReplayArtifactText.v1");
    h.add_string(text);
    return h.value();
}

ReplayArtifactManifest make_replay_artifact_manifest(std::string_view snapshot_text,
                                                     std::string_view trace_text,
                                                     const GameState& final_state,
                                                     bool applied_only) {
    ReplayArtifactManifest manifest{};
    manifest.snapshot_text_hash = replay_artifact_text_hash(snapshot_text);
    manifest.trace_text_hash = replay_artifact_text_hash(trace_text);
    const auto snapshot = parse_state_core_snapshot(snapshot_text);
    if (snapshot.ok) {
        manifest.checkpoint_state_hash = snapshot.source_checkpoint.state_hash;
        manifest.checkpoint_journal_hash = snapshot.source_checkpoint.journal_hash;
        manifest.checkpoint_journal_entries = snapshot.source_checkpoint.journal_entries;
    }
    const auto trace = parse_action_trace(trace_text);
    if (trace.ok) {
        manifest.action_count = static_cast<u64>(trace.trace.size());
    }
    manifest.final_state_hash = canonical_state_hash(final_state);
    manifest.applied_only = applied_only;
    manifest.paid_action_journal_attached = false;
    manifest.paid_action_journal_format = "none";
    manifest.bundle_hash = replay_artifact_manifest_payload_hash(manifest);
    return manifest;
}

ReplayArtifactManifest make_replay_artifact_manifest_with_paid_action_journal(std::string_view snapshot_text,
                                                                             std::string_view trace_text,
                                                                             const GameState& final_state,
                                                                             std::string_view paid_action_journal_text,
                                                                             bool applied_only) {
    ReplayArtifactManifest manifest = make_replay_artifact_manifest(snapshot_text, trace_text, final_state, applied_only);
    manifest.paid_action_journal_attached = true;
    manifest.paid_action_journal_format = "MTGSim.PaidActionTransactionJournal.v9";
    manifest.paid_action_journal_text_hash = paid_action_transaction_journal_text_hash(paid_action_journal_text);
    const auto parsed = parse_paid_action_transaction_journal(paid_action_journal_text);
    if (parsed.ok) {
        manifest.paid_action_journal_record_count = parsed.journal.header.record_count;
        manifest.paid_action_journal_state_hash = parsed.journal.header.state_hash;
        manifest.paid_action_journal_journal_hash = parsed.journal.header.journal_hash;
        manifest.paid_action_journal_record_payload_hash = parsed.journal.header.record_payload_hash;
    }
    manifest.bundle_hash = replay_artifact_manifest_payload_hash(manifest);
    return manifest;
}

std::string serialize_replay_artifact_manifest(const ReplayArtifactManifest& manifest) {
    ReplayArtifactManifest normalized = manifest;
    if (!normalized.paid_action_journal_attached) {
        normalized.paid_action_journal_format = "none";
        normalized.paid_action_journal_text_hash = 0;
        normalized.paid_action_journal_record_count = 0;
        normalized.paid_action_journal_state_hash = 0;
        normalized.paid_action_journal_journal_hash = 0;
        normalized.paid_action_journal_record_payload_hash = 0;
    }
    normalized.bundle_hash = replay_artifact_manifest_payload_hash(normalized);
    std::ostringstream out;
    out << "MTGSim.ReplayArtifactManifest.v3\n"
        << "manifest_schema=" << normalized.schema_version
        << " snapshot_format=" << normalized.snapshot_format
        << " trace_format=" << normalized.trace_format
        << " snapshot_hash=" << normalized.snapshot_text_hash
        << " trace_hash=" << normalized.trace_text_hash
        << " checkpoint_state_hash=" << normalized.checkpoint_state_hash
        << " checkpoint_journal_hash=" << normalized.checkpoint_journal_hash
        << " checkpoint_journal_entries=" << normalized.checkpoint_journal_entries
        << " action_count=" << normalized.action_count
        << " final_state_hash=" << normalized.final_state_hash
        << " applied_only=" << (normalized.applied_only ? 1 : 0)
        << " paid_action_journal_attached=" << (normalized.paid_action_journal_attached ? 1 : 0)
        << " paid_action_journal_format=" << normalized.paid_action_journal_format
        << " paid_action_journal_text_hash=" << normalized.paid_action_journal_text_hash
        << " paid_action_journal_record_count=" << normalized.paid_action_journal_record_count
        << " paid_action_journal_state_hash=" << normalized.paid_action_journal_state_hash
        << " paid_action_journal_journal_hash=" << normalized.paid_action_journal_journal_hash
        << " paid_action_journal_record_payload_hash=" << normalized.paid_action_journal_record_payload_hash
        << " bundle_hash=" << normalized.bundle_hash
        << "\n";
    return out.str();
}

ReplayArtifactManifestParseResult parse_replay_artifact_manifest(std::string_view text) {
    ReplayArtifactManifestParseResult result{};
    auto fail = [&result](u64 line, std::string message) -> ReplayArtifactManifestParseResult {
        result.ok = false;
        result.manifest = ReplayArtifactManifest{};
        result.error_line = line;
        result.error = std::move(message);
        return result;
    };

    std::istringstream input{std::string(text)};
    std::string line;
    u64 line_number = 0;
    if (!std::getline(input, line)) {
        return fail(1, "empty replay artifact manifest");
    }
    ++line_number;
    if (!line.empty() && line.back() == '\r') {
        line.pop_back();
    }
    const bool is_v1_manifest = line == "MTGSim.ReplayArtifactManifest.v1";
    const bool is_v2_manifest = line == "MTGSim.ReplayArtifactManifest.v2";
    const bool is_v3_manifest = line == "MTGSim.ReplayArtifactManifest.v3";
    if (!is_v1_manifest && !is_v2_manifest && !is_v3_manifest) {
        return fail(line_number, "missing MTGSim.ReplayArtifactManifest.v1/v2/v3 header");
    }
    result.manifest.schema_version = is_v1_manifest ? 1U : (is_v2_manifest ? 2U : kReplayArtifactManifestSchemaVersion);

    bool seen_data = false;
    while (std::getline(input, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty()) {
            continue;
        }
        if (seen_data) {
            return fail(line_number, "replay artifact manifest should contain exactly one data line");
        }
        seen_data = true;

        bool seen_manifest_schema = false;
        bool seen_snapshot_format = false;
        bool seen_trace_format = false;
        bool seen_snapshot_hash = false;
        bool seen_trace_hash = false;
        bool seen_checkpoint_state_hash = false;
        bool seen_checkpoint_journal_hash = false;
        bool seen_checkpoint_journal_entries = false;
        bool seen_action_count = false;
        bool seen_final_state_hash = false;
        bool seen_applied_only = false;
        bool seen_paid_action_journal_attached = false;
        bool seen_paid_action_journal_format = false;
        bool seen_paid_action_journal_text_hash = false;
        bool seen_paid_action_journal_record_count = false;
        bool seen_paid_action_journal_state_hash = false;
        bool seen_paid_action_journal_journal_hash = false;
        bool seen_paid_action_journal_record_payload_hash = false;
        bool seen_bundle_hash = false;

        std::istringstream fields{line};
        std::string field;
        while (fields >> field) {
            const auto eq = field.find('=');
            if (eq == std::string::npos || eq == 0U) {
                return fail(line_number, "malformed manifest key=value token");
            }
            const std::string_view key(field.data(), eq);
            const std::string_view value(field.data() + eq + 1U, field.size() - eq - 1U);
            if (key == "manifest_schema") {
                if ((!is_v2_manifest && !is_v3_manifest) || seen_manifest_schema || !parse_u32_text(value, result.manifest.schema_version) || result.manifest.schema_version == 0U) {
                    return fail(line_number, "invalid or duplicate manifest_schema");
                }
                seen_manifest_schema = true;
            } else if (key == "snapshot_format") {
                if (seen_snapshot_format || value.empty()) {
                    return fail(line_number, "invalid or duplicate snapshot_format");
                }
                result.manifest.snapshot_format = std::string(value);
                seen_snapshot_format = true;
            } else if (key == "trace_format") {
                if (seen_trace_format || value.empty()) {
                    return fail(line_number, "invalid or duplicate trace_format");
                }
                result.manifest.trace_format = std::string(value);
                seen_trace_format = true;
            } else if (key == "snapshot_hash") {
                if (seen_snapshot_hash || !parse_u64_text(value, result.manifest.snapshot_text_hash)) {
                    return fail(line_number, "invalid or duplicate snapshot_hash");
                }
                seen_snapshot_hash = true;
            } else if (key == "trace_hash") {
                if (seen_trace_hash || !parse_u64_text(value, result.manifest.trace_text_hash)) {
                    return fail(line_number, "invalid or duplicate trace_hash");
                }
                seen_trace_hash = true;
            } else if (key == "checkpoint_state_hash") {
                if (seen_checkpoint_state_hash || !parse_u64_text(value, result.manifest.checkpoint_state_hash)) {
                    return fail(line_number, "invalid or duplicate checkpoint_state_hash");
                }
                seen_checkpoint_state_hash = true;
            } else if (key == "checkpoint_journal_hash") {
                if (seen_checkpoint_journal_hash || !parse_u64_text(value, result.manifest.checkpoint_journal_hash)) {
                    return fail(line_number, "invalid or duplicate checkpoint_journal_hash");
                }
                seen_checkpoint_journal_hash = true;
            } else if (key == "checkpoint_journal_entries") {
                if (seen_checkpoint_journal_entries || !parse_u64_text(value, result.manifest.checkpoint_journal_entries)) {
                    return fail(line_number, "invalid or duplicate checkpoint_journal_entries");
                }
                seen_checkpoint_journal_entries = true;
            } else if (key == "action_count") {
                if (seen_action_count || !parse_u64_text(value, result.manifest.action_count)) {
                    return fail(line_number, "invalid or duplicate action_count");
                }
                seen_action_count = true;
            } else if (key == "final_state_hash") {
                if (seen_final_state_hash || !parse_u64_text(value, result.manifest.final_state_hash)) {
                    return fail(line_number, "invalid or duplicate final_state_hash");
                }
                seen_final_state_hash = true;
            } else if (key == "applied_only") {
                if (seen_applied_only || !parse_bool_text(value, result.manifest.applied_only)) {
                    return fail(line_number, "invalid or duplicate applied_only flag");
                }
                seen_applied_only = true;
            } else if (key == "paid_action_journal_attached") {
                if (!is_v3_manifest || seen_paid_action_journal_attached || !parse_bool_text(value, result.manifest.paid_action_journal_attached)) {
                    return fail(line_number, "invalid or duplicate paid_action_journal_attached flag");
                }
                seen_paid_action_journal_attached = true;
            } else if (key == "paid_action_journal_format") {
                if (!is_v3_manifest || seen_paid_action_journal_format || value.empty()) {
                    return fail(line_number, "invalid or duplicate paid_action_journal_format");
                }
                result.manifest.paid_action_journal_format = std::string(value);
                seen_paid_action_journal_format = true;
            } else if (key == "paid_action_journal_text_hash") {
                if (!is_v3_manifest || seen_paid_action_journal_text_hash || !parse_u64_text(value, result.manifest.paid_action_journal_text_hash)) {
                    return fail(line_number, "invalid or duplicate paid_action_journal_text_hash");
                }
                seen_paid_action_journal_text_hash = true;
            } else if (key == "paid_action_journal_record_count") {
                if (!is_v3_manifest || seen_paid_action_journal_record_count || !parse_u64_text(value, result.manifest.paid_action_journal_record_count)) {
                    return fail(line_number, "invalid or duplicate paid_action_journal_record_count");
                }
                seen_paid_action_journal_record_count = true;
            } else if (key == "paid_action_journal_state_hash") {
                if (!is_v3_manifest || seen_paid_action_journal_state_hash || !parse_u64_text(value, result.manifest.paid_action_journal_state_hash)) {
                    return fail(line_number, "invalid or duplicate paid_action_journal_state_hash");
                }
                seen_paid_action_journal_state_hash = true;
            } else if (key == "paid_action_journal_journal_hash") {
                if (!is_v3_manifest || seen_paid_action_journal_journal_hash || !parse_u64_text(value, result.manifest.paid_action_journal_journal_hash)) {
                    return fail(line_number, "invalid or duplicate paid_action_journal_journal_hash");
                }
                seen_paid_action_journal_journal_hash = true;
            } else if (key == "paid_action_journal_record_payload_hash") {
                if (!is_v3_manifest || seen_paid_action_journal_record_payload_hash || !parse_u64_text(value, result.manifest.paid_action_journal_record_payload_hash)) {
                    return fail(line_number, "invalid or duplicate paid_action_journal_record_payload_hash");
                }
                seen_paid_action_journal_record_payload_hash = true;
            } else if (key == "bundle_hash") {
                if (seen_bundle_hash || !parse_u64_text(value, result.manifest.bundle_hash)) {
                    return fail(line_number, "invalid or duplicate bundle_hash");
                }
                seen_bundle_hash = true;
            } else {
                return fail(line_number, "unknown manifest field: " + std::string(key));
            }
        }

        if (((is_v2_manifest || is_v3_manifest) && !seen_manifest_schema) || !seen_snapshot_format || !seen_trace_format || !seen_snapshot_hash || !seen_trace_hash ||
            !seen_checkpoint_state_hash || !seen_checkpoint_journal_hash || !seen_checkpoint_journal_entries ||
            !seen_action_count || !seen_final_state_hash || !seen_applied_only || !seen_bundle_hash) {
            return fail(line_number, "missing required manifest field");
        }
        if (is_v3_manifest && (!seen_paid_action_journal_attached || !seen_paid_action_journal_format ||
                              !seen_paid_action_journal_text_hash || !seen_paid_action_journal_record_count ||
                              !seen_paid_action_journal_state_hash || !seen_paid_action_journal_journal_hash ||
                              !seen_paid_action_journal_record_payload_hash)) {
            return fail(line_number, "missing required manifest paid-action journal field");
        }
        if (is_v3_manifest && !result.manifest.paid_action_journal_attached &&
            (result.manifest.paid_action_journal_format != "none" ||
             result.manifest.paid_action_journal_text_hash != 0U ||
             result.manifest.paid_action_journal_record_count != 0U ||
             result.manifest.paid_action_journal_state_hash != 0U ||
             result.manifest.paid_action_journal_journal_hash != 0U ||
             result.manifest.paid_action_journal_record_payload_hash != 0U)) {
            return fail(line_number, "unattached paid-action journal fields must be zero/none");
        }
        const u64 expected_bundle_hash = is_v1_manifest
            ? replay_artifact_manifest_payload_hash_v1(result.manifest)
            : (is_v2_manifest ? replay_artifact_manifest_payload_hash_v2(result.manifest)
                              : replay_artifact_manifest_payload_hash(result.manifest));
        if (result.manifest.bundle_hash != expected_bundle_hash) {
            return fail(line_number, "replay artifact manifest bundle hash mismatch");
        }
    }

    if (!seen_data) {
        return fail(line_number + 1U, "missing replay artifact manifest data line");
    }
    result.ok = true;
    return result;
}

ReplayArtifactVerifyResult verify_replay_artifact_bundle_impl(std::string_view snapshot_text,
                                                              std::string_view trace_text,
                                                              std::string_view paid_action_journal_text,
                                                              bool paid_action_journal_supplied,
                                                              const ReplayArtifactManifest& manifest) {
    ReplayArtifactVerifyResult result{};
    result.expected_manifest_schema_version = manifest.schema_version;
    result.actual_manifest_schema_version = kReplayArtifactManifestSchemaVersion;
    result.expected_snapshot_text_hash = manifest.snapshot_text_hash;
    result.actual_snapshot_text_hash = replay_artifact_text_hash(snapshot_text);
    result.expected_trace_text_hash = manifest.trace_text_hash;
    result.actual_trace_text_hash = replay_artifact_text_hash(trace_text);
    result.expected_checkpoint_state_hash = manifest.checkpoint_state_hash;
    result.expected_checkpoint_journal_hash = manifest.checkpoint_journal_hash;
    result.expected_checkpoint_journal_entries = manifest.checkpoint_journal_entries;
    result.expected_action_count = manifest.action_count;
    result.expected_final_state_hash = manifest.final_state_hash;
    result.expected_paid_action_journal_text_hash = manifest.paid_action_journal_text_hash;
    result.expected_paid_action_journal_record_count = manifest.paid_action_journal_record_count;
    result.expected_paid_action_journal_state_hash = manifest.paid_action_journal_state_hash;
    result.expected_paid_action_journal_journal_hash = manifest.paid_action_journal_journal_hash;
    result.expected_paid_action_journal_record_payload_hash = manifest.paid_action_journal_record_payload_hash;
    result.actual_paid_action_journal_text_hash = paid_action_journal_supplied
        ? paid_action_transaction_journal_text_hash(paid_action_journal_text)
        : 0U;
    result.action_count = manifest.action_count;

    if (manifest.schema_version != kReplayArtifactManifestSchemaVersion) {
        result.failure = ReplayArtifactFailureKind::ManifestSchemaMismatch;
        result.error = "manifest schema mismatch";
        return result;
    }
    if (!manifest_format_fields_are_current(manifest)) {
        result.failure = ReplayArtifactFailureKind::UnsupportedFormat;
        result.error = "unsupported replay artifact format";
        return result;
    }
    if (manifest.bundle_hash != replay_artifact_manifest_payload_hash(manifest)) {
        result.failure = ReplayArtifactFailureKind::ManifestBundleHashMismatch;
        result.error = "manifest bundle hash mismatch";
        return result;
    }
    if (manifest.paid_action_journal_attached && !paid_action_journal_supplied) {
        result.failure = ReplayArtifactFailureKind::PaidActionJournalMissing;
        result.error = "manifest requires a paid-action transaction journal attachment";
        return result;
    }
    if (manifest.paid_action_journal_attached &&
        result.expected_paid_action_journal_text_hash != result.actual_paid_action_journal_text_hash) {
        result.failure = ReplayArtifactFailureKind::PaidActionJournalTextHashMismatch;
        result.error = "paid-action transaction journal text hash mismatch";
        return result;
    }
    if (result.expected_snapshot_text_hash != result.actual_snapshot_text_hash) {
        result.failure = ReplayArtifactFailureKind::SnapshotTextHashMismatch;
        result.error = "snapshot text hash mismatch";
        return result;
    }
    if (result.expected_trace_text_hash != result.actual_trace_text_hash) {
        result.failure = ReplayArtifactFailureKind::TraceTextHashMismatch;
        result.error = "trace text hash mismatch";
        return result;
    }

    const auto snapshot = parse_state_core_snapshot(snapshot_text);
    if (!snapshot.ok) {
        result.failure = ReplayArtifactFailureKind::SnapshotParseFailed;
        result.error = "snapshot parse failed: " + snapshot.error;
        result.error_line = snapshot.error_line;
        return result;
    }
    result.actual_checkpoint_state_hash = snapshot.source_checkpoint.state_hash;
    result.actual_checkpoint_journal_hash = snapshot.source_checkpoint.journal_hash;
    result.actual_checkpoint_journal_entries = snapshot.source_checkpoint.journal_entries;
    if (snapshot.source_checkpoint.state_hash != manifest.checkpoint_state_hash ||
        snapshot.source_checkpoint.journal_hash != manifest.checkpoint_journal_hash ||
        snapshot.source_checkpoint.journal_entries != manifest.checkpoint_journal_entries) {
        result.failure = ReplayArtifactFailureKind::CheckpointSealMismatch;
        result.error = "manifest checkpoint seal does not match snapshot source checkpoint";
        return result;
    }

    const auto trace = parse_action_trace(trace_text);
    if (!trace.ok) {
        result.failure = ReplayArtifactFailureKind::TraceParseFailed;
        result.error = "trace parse failed: " + trace.error;
        result.error_line = trace.error_line;
        return result;
    }
    result.actual_action_count = static_cast<u64>(trace.trace.size());
    if (result.actual_action_count != manifest.action_count) {
        result.failure = ReplayArtifactFailureKind::ActionCountMismatch;
        result.error = "manifest action_count does not match parsed trace";
        return result;
    }

    auto replay = snapshot.game;
    result.replay = replay_action_trace(replay, trace.trace);
    if (!result.replay.ok) {
        result.failure = ReplayArtifactFailureKind::TraceReplayFailed;
        result.error = "trace replay failed";
        result.actual_final_state_hash = canonical_state_hash(replay);
        return result;
    }

    result.actual_final_state_hash = canonical_state_hash(replay);
    if (result.expected_final_state_hash != result.actual_final_state_hash) {
        result.failure = ReplayArtifactFailureKind::FinalStateHashMismatch;
        result.error = "final StateCore hash mismatch";
        return result;
    }

    if (manifest.paid_action_journal_attached) {
        result.paid_action_journal_verify = verify_paid_action_transaction_journal_for_state(replay, paid_action_journal_text);
        if (!result.paid_action_journal_verify.ok) {
            result.failure = ReplayArtifactFailureKind::PaidActionJournalVerifyFailed;
            result.error = "paid-action transaction journal verification failed: " + result.paid_action_journal_verify.error;
            result.error_line = result.paid_action_journal_verify.error_line;
            return result;
        }
        const auto& header = result.paid_action_journal_verify.parse.journal.header;
        result.actual_paid_action_journal_record_count = header.record_count;
        result.actual_paid_action_journal_state_hash = header.state_hash;
        result.actual_paid_action_journal_journal_hash = header.journal_hash;
        result.actual_paid_action_journal_record_payload_hash = header.record_payload_hash;
        if (result.expected_paid_action_journal_record_count != result.actual_paid_action_journal_record_count) {
            result.failure = ReplayArtifactFailureKind::PaidActionJournalRecordCountMismatch;
            result.error = "paid-action transaction journal record count mismatch";
            return result;
        }
        if (result.expected_paid_action_journal_state_hash != result.actual_paid_action_journal_state_hash) {
            result.failure = ReplayArtifactFailureKind::PaidActionJournalStateHashMismatch;
            result.error = "paid-action transaction journal state hash mismatch";
            return result;
        }
        if (result.expected_paid_action_journal_journal_hash != result.actual_paid_action_journal_journal_hash) {
            result.failure = ReplayArtifactFailureKind::PaidActionJournalHashMismatch;
            result.error = "paid-action transaction journal hash mismatch";
            return result;
        }
        if (result.expected_paid_action_journal_record_payload_hash != result.actual_paid_action_journal_record_payload_hash) {
            result.failure = ReplayArtifactFailureKind::PaidActionJournalPayloadHashMismatch;
            result.error = "paid-action transaction journal payload hash mismatch";
            return result;
        }
    }

    result.ok = true;
    result.failure = ReplayArtifactFailureKind::None;
    return result;
}

ReplayArtifactVerifyResult verify_replay_artifact_bundle(std::string_view snapshot_text,
                                                         std::string_view trace_text,
                                                         const ReplayArtifactManifest& manifest) {
    return verify_replay_artifact_bundle_impl(snapshot_text, trace_text, std::string_view{}, false, manifest);
}

ReplayArtifactVerifyResult verify_replay_artifact_bundle_with_paid_action_journal(std::string_view snapshot_text,
                                                                                  std::string_view trace_text,
                                                                                  std::string_view paid_action_journal_text,
                                                                                  const ReplayArtifactManifest& manifest) {
    return verify_replay_artifact_bundle_impl(snapshot_text, trace_text, paid_action_journal_text, true, manifest);
}


ReplayArtifactPrefixResult make_replay_artifact_prefix_bundle(std::string_view snapshot_text,
                                                              std::string_view trace_text,
                                                              const ReplayArtifactManifest& manifest) {
    // Build a manifest-bound longest known-good prefix so replay failures can
    // be reduced to a small artifact and a next_bad_step instead of only prose.
    ReplayArtifactPrefixResult result{};
    result.source_verify = verify_replay_artifact_bundle(snapshot_text, trace_text, manifest);
    result.source_failure = result.source_verify.failure;

    auto fail = [&result](std::string message) -> ReplayArtifactPrefixResult {
        result.ok = false;
        result.error = std::move(message);
        return result;
    };

    switch (result.source_verify.failure) {
        case ReplayArtifactFailureKind::None:
        case ReplayArtifactFailureKind::ActionCountMismatch:
        case ReplayArtifactFailureKind::TraceReplayFailed:
        case ReplayArtifactFailureKind::FinalStateHashMismatch:
            break;
        case ReplayArtifactFailureKind::UnsupportedFormat:
        case ReplayArtifactFailureKind::ManifestSchemaMismatch:
        case ReplayArtifactFailureKind::ManifestBundleHashMismatch:
        case ReplayArtifactFailureKind::SnapshotTextHashMismatch:
        case ReplayArtifactFailureKind::TraceTextHashMismatch:
        case ReplayArtifactFailureKind::SnapshotParseFailed:
        case ReplayArtifactFailureKind::CheckpointSealMismatch:
        case ReplayArtifactFailureKind::TraceParseFailed:
        case ReplayArtifactFailureKind::PaidActionJournalMissing:
        case ReplayArtifactFailureKind::PaidActionJournalTextHashMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalVerifyFailed:
        case ReplayArtifactFailureKind::PaidActionJournalRecordCountMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalStateHashMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalHashMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalPayloadHashMismatch:
        case ReplayArtifactFailureKind::Count:
            return fail("source bundle did not reach a replay-localizable boundary: " + result.source_verify.error);
    }

    const auto snapshot = parse_state_core_snapshot(snapshot_text);
    if (!snapshot.ok) {
        return fail("snapshot parse failed while building prefix: " + snapshot.error);
    }
    const auto trace = parse_action_trace(trace_text);
    if (!trace.ok) {
        return fail("trace parse failed while building prefix: " + trace.error);
    }

    u64 prefix_count = static_cast<u64>(trace.trace.size());
    u64 next_bad_step = 0;
    if (!result.source_verify.ok) {
        if (result.source_verify.failure == ReplayArtifactFailureKind::TraceReplayFailed) {
            const u64 mismatch = result.source_verify.replay.mismatch_index;
            if (mismatch == 0U) {
                return fail("trace replay failed without a mismatch index");
            }
            prefix_count = mismatch - 1U;
            next_bad_step = mismatch;
        } else if (result.source_verify.failure == ReplayArtifactFailureKind::ActionCountMismatch) {
            const u64 actual_count = static_cast<u64>(trace.trace.size());
            prefix_count = std::min(manifest.action_count, actual_count);
            next_bad_step = prefix_count + 1U;
        } else if (result.source_verify.failure == ReplayArtifactFailureKind::FinalStateHashMismatch) {
            prefix_count = static_cast<u64>(trace.trace.size());
            next_bad_step = 0;
        }
    }

    if (prefix_count > static_cast<u64>(trace.trace.size())) {
        prefix_count = static_cast<u64>(trace.trace.size());
    }

    result.prefix_trace.assign(trace.trace.begin(), trace.trace.begin() + static_cast<std::ptrdiff_t>(prefix_count));

    auto replay_prefix = snapshot.game;
    auto prefix_replay = replay_action_trace(replay_prefix, result.prefix_trace);
    if (!prefix_replay.ok) {
        if (prefix_replay.mismatch_index == 0U) {
            return fail("chosen prefix did not replay and had no mismatch index");
        }
        next_bad_step = prefix_replay.mismatch_index;
        const u64 reduced = prefix_replay.mismatch_index - 1U;
        result.prefix_trace.assign(trace.trace.begin(), trace.trace.begin() + static_cast<std::ptrdiff_t>(reduced));
        replay_prefix = snapshot.game;
        prefix_replay = replay_action_trace(replay_prefix, result.prefix_trace);
        if (!prefix_replay.ok) {
            return fail("reduced prefix still did not replay cleanly");
        }
        prefix_count = reduced;
    }

    result.prefix_trace_text = serialize_action_trace(result.prefix_trace);
    result.prefix_manifest = make_replay_artifact_manifest(snapshot_text, result.prefix_trace_text, replay_prefix, manifest.applied_only);
    result.prefix_manifest_text = serialize_replay_artifact_manifest(result.prefix_manifest);
    result.prefix_action_count = static_cast<u64>(result.prefix_trace.size());
    result.next_bad_step = next_bad_step;
    result.prefix_final_state_hash = canonical_state_hash(replay_prefix);
    result.ok = true;
    return result;
}

ReplayArtifactResumeResult make_replay_artifact_resume_probe(std::string_view snapshot_text,
                                                             std::string_view trace_text,
                                                             const ReplayArtifactManifest& manifest) {
    // Convert a full bundle into a smaller resume probe rooted at the longest
    // known-good prefix. For replay failures, the first suffix action is the
    // suspect transition; for final-hash mismatches, the suffix is empty and the
    // manifest expectation remains the thing under test.
    ReplayArtifactResumeResult result{};
    result.source_verify = verify_replay_artifact_bundle(snapshot_text, trace_text, manifest);
    result.source_failure = result.source_verify.failure;

    auto fail = [&result](std::string message) -> ReplayArtifactResumeResult {
        result.ok = false;
        result.error = std::move(message);
        return result;
    };

    switch (result.source_verify.failure) {
        case ReplayArtifactFailureKind::None:
        case ReplayArtifactFailureKind::ActionCountMismatch:
        case ReplayArtifactFailureKind::TraceReplayFailed:
        case ReplayArtifactFailureKind::FinalStateHashMismatch:
            break;
        case ReplayArtifactFailureKind::UnsupportedFormat:
        case ReplayArtifactFailureKind::ManifestSchemaMismatch:
        case ReplayArtifactFailureKind::ManifestBundleHashMismatch:
        case ReplayArtifactFailureKind::SnapshotTextHashMismatch:
        case ReplayArtifactFailureKind::TraceTextHashMismatch:
        case ReplayArtifactFailureKind::SnapshotParseFailed:
        case ReplayArtifactFailureKind::CheckpointSealMismatch:
        case ReplayArtifactFailureKind::TraceParseFailed:
        case ReplayArtifactFailureKind::PaidActionJournalMissing:
        case ReplayArtifactFailureKind::PaidActionJournalTextHashMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalVerifyFailed:
        case ReplayArtifactFailureKind::PaidActionJournalRecordCountMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalStateHashMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalHashMismatch:
        case ReplayArtifactFailureKind::PaidActionJournalPayloadHashMismatch:
        case ReplayArtifactFailureKind::Count:
            return fail("source bundle did not reach a resume-localizable boundary: " + result.source_verify.error);
    }

    const auto snapshot = parse_state_core_snapshot(snapshot_text);
    if (!snapshot.ok) {
        return fail("snapshot parse failed while building resume probe: " + snapshot.error);
    }
    const auto trace = parse_action_trace(trace_text);
    if (!trace.ok) {
        return fail("trace parse failed while building resume probe: " + trace.error);
    }

    u64 prefix_count = static_cast<u64>(trace.trace.size());
    u64 next_bad_step = 0;
    if (!result.source_verify.ok) {
        if (result.source_verify.failure == ReplayArtifactFailureKind::TraceReplayFailed) {
            const u64 mismatch = result.source_verify.replay.mismatch_index;
            if (mismatch == 0U) {
                return fail("trace replay failed without a mismatch index");
            }
            prefix_count = mismatch - 1U;
            next_bad_step = mismatch;
        } else if (result.source_verify.failure == ReplayArtifactFailureKind::ActionCountMismatch) {
            const u64 actual_count = static_cast<u64>(trace.trace.size());
            prefix_count = std::min(manifest.action_count, actual_count);
            next_bad_step = prefix_count + 1U;
        } else if (result.source_verify.failure == ReplayArtifactFailureKind::FinalStateHashMismatch) {
            prefix_count = static_cast<u64>(trace.trace.size());
            next_bad_step = 0;
        }
    }

    if (prefix_count > static_cast<u64>(trace.trace.size())) {
        prefix_count = static_cast<u64>(trace.trace.size());
    }

    std::vector<ActionTraceEntry> prefix_trace;
    prefix_trace.assign(trace.trace.begin(), trace.trace.begin() + static_cast<std::ptrdiff_t>(prefix_count));

    auto resume_state = snapshot.game;
    auto prefix_replay = replay_action_trace(resume_state, prefix_trace);
    if (!prefix_replay.ok) {
        if (prefix_replay.mismatch_index == 0U) {
            return fail("chosen resume prefix did not replay and had no mismatch index");
        }
        next_bad_step = prefix_replay.mismatch_index;
        const u64 reduced = prefix_replay.mismatch_index - 1U;
        prefix_trace.assign(trace.trace.begin(), trace.trace.begin() + static_cast<std::ptrdiff_t>(reduced));
        resume_state = snapshot.game;
        prefix_replay = replay_action_trace(resume_state, prefix_trace);
        if (!prefix_replay.ok) {
            return fail("reduced resume prefix still did not replay cleanly");
        }
        prefix_count = reduced;
    }

    const GameState resume_checkpoint = make_branch_state(resume_state, JournalRetention::ClearAll);
    result.resume_snapshot_text = serialize_state_core_snapshot(resume_checkpoint);
    result.resume_state_hash = canonical_state_hash(resume_checkpoint);

    result.suffix_trace.assign(trace.trace.begin() + static_cast<std::ptrdiff_t>(prefix_count), trace.trace.end());
    result.suffix_trace_text = serialize_action_trace(result.suffix_trace);
    result.suffix_manifest = make_replay_artifact_manifest_with_expected_final(result.resume_snapshot_text,
                                                                               result.suffix_trace_text,
                                                                               manifest.final_state_hash,
                                                                               manifest.applied_only);
    result.suffix_manifest_text = serialize_replay_artifact_manifest(result.suffix_manifest);
    result.suffix_verify = verify_replay_artifact_bundle(result.resume_snapshot_text,
                                                         result.suffix_trace_text,
                                                         result.suffix_manifest);
    result.prefix_action_count = prefix_count;
    result.suffix_action_count = static_cast<u64>(result.suffix_trace.size());
    result.next_bad_step = next_bad_step;
    result.ok = true;
    return result;
}

std::uint64_t canonical_state_hash(const GameState& game) noexcept {
    StableHasher h;
    h.add_string("MTGSim.StateCore.v1");
    hash_vector(h, game.definitions);
    hash_vector(h, game.objects);
    hash_vector(h, game.players);
    hash_vector(h, game.stack);
    hash_into(h, game.rng_state);
    // next_event_sequence is intentionally excluded: it is a journal sequence
    // allocator. Pending triggers carry the ordering data that affects play.
    hash_into(h, game.next_zone_change_index);
    hash_into(h, game.next_damage_prevention_shield_id);
    hash_into(h, game.next_continuous_effect_timestamp);
    hash_into(h, game.next_layer_timestamp);
    hash_into(h, game.starting_player);
    hash_into(h, game.active_player);
    hash_into(h, game.priority_player);
    hash_into(h, game.turn_number);
    h.add_u64(static_cast<u64>(game.step));
    hash_into(h, game.consecutive_priority_passes);
    hash_into(h, game.attackers_declared_this_step);
    hash_into(h, game.combat_damage_assigned_this_step);
    hash_vector(h, game.blocker_declaration_complete_players);
    hash_vector(h, game.pending_triggers);
    hash_vector(h, game.damage_prevention_shields);
    hash_vector(h, game.continuous_effects);
    return h.value();
}

std::uint64_t journal_hash(const GameState& game) noexcept {
    StableHasher h;
    h.add_string("MTGSim.Journal.v1");
    hash_into(h, game.journal_trimmed);
    hash_into(h, game.next_event_sequence);
    hash_vector(h, game.events);
    hash_vector(h, game.event_records);
    hash_vector(h, game.trigger_records);
    hash_vector(h, game.stack_placement_records);
    hash_vector(h, game.stack_resolution_records);
    hash_vector(h, game.priority_transition_records);
    hash_vector(h, game.state_based_action_records);
    hash_vector(h, game.zone_change_records);
    hash_vector(h, game.zone_change_replacement_records);
    hash_vector(h, game.combat_declaration_records);
    hash_vector(h, game.combat_damage_assignment_records);
    hash_vector(h, game.damage_records);
    hash_vector(h, game.damage_prevention_records);
    hash_vector(h, game.life_change_records);
    hash_vector(h, game.mana_change_records);
    hash_vector(h, game.mana_payment_plan_records);
    hash_vector(h, game.tap_cost_payment_records);
    hash_vector(h, game.sacrifice_cost_payment_records);
    hash_vector(h, game.discard_cost_payment_records);
    hash_vector(h, game.life_cost_payment_records);
    hash_vector(h, game.return_cost_payment_records);
    hash_vector(h, game.loyalty_cost_payment_records);
    hash_vector(h, game.counter_change_records);
    hash_vector(h, game.discard_records);
    hash_vector(h, game.draw_records);
    hash_vector(h, game.mulligan_records);
    hash_vector(h, game.mulligan_keep_records);
    hash_vector(h, game.paid_action_declaration_records);
    hash_vector(h, game.paid_action_transaction_records);
    hash_vector(h, game.action_receipt_records);
    return h.value();
}

std::size_t journal_entry_count(const GameState& game) noexcept {
    return game.events.size() + game.event_records.size() + game.trigger_records.size() +
           game.stack_placement_records.size() + game.stack_resolution_records.size() +
           game.priority_transition_records.size() + game.state_based_action_records.size() +
           game.zone_change_records.size() + game.zone_change_replacement_records.size() +
           game.combat_declaration_records.size() + game.combat_damage_assignment_records.size() +
           game.damage_records.size() + game.damage_prevention_records.size() +
           game.life_change_records.size() + game.mana_change_records.size() +
           game.mana_payment_plan_records.size() + game.tap_cost_payment_records.size() +
           game.sacrifice_cost_payment_records.size() + game.discard_cost_payment_records.size() +
           game.life_cost_payment_records.size() + game.loyalty_cost_payment_records.size() +
           game.counter_change_records.size() + game.discard_records.size() +
           game.draw_records.size() + game.mulligan_records.size() + game.mulligan_keep_records.size() +
           game.paid_action_declaration_records.size() + game.paid_action_transaction_records.size() +
           game.action_receipt_records.size();
}

template <typename T>
std::size_t vector_capacity_bytes(const std::vector<T>& values) noexcept {
    return values.capacity() * sizeof(T);
}

std::size_t journal_reserved_capacity_bytes(const GameState& game) noexcept {
    return vector_capacity_bytes(game.events) + vector_capacity_bytes(game.event_records) +
           vector_capacity_bytes(game.trigger_records) + vector_capacity_bytes(game.stack_placement_records) +
           vector_capacity_bytes(game.stack_resolution_records) + vector_capacity_bytes(game.priority_transition_records) +
           vector_capacity_bytes(game.state_based_action_records) + vector_capacity_bytes(game.zone_change_records) +
           vector_capacity_bytes(game.zone_change_replacement_records) + vector_capacity_bytes(game.combat_declaration_records) +
           vector_capacity_bytes(game.combat_damage_assignment_records) + vector_capacity_bytes(game.damage_records) +
           vector_capacity_bytes(game.damage_prevention_records) + vector_capacity_bytes(game.life_change_records) +
           vector_capacity_bytes(game.mana_change_records) + vector_capacity_bytes(game.mana_payment_plan_records) +
           vector_capacity_bytes(game.tap_cost_payment_records) + vector_capacity_bytes(game.sacrifice_cost_payment_records) +
           vector_capacity_bytes(game.discard_cost_payment_records) +
           vector_capacity_bytes(game.life_cost_payment_records) +
           vector_capacity_bytes(game.counter_change_records) +
           vector_capacity_bytes(game.discard_records) + vector_capacity_bytes(game.draw_records) +
           vector_capacity_bytes(game.mulligan_records) + vector_capacity_bytes(game.mulligan_keep_records) +
           vector_capacity_bytes(game.paid_action_declaration_records) + vector_capacity_bytes(game.paid_action_transaction_records) +
           vector_capacity_bytes(game.action_receipt_records);
}

namespace {

[[nodiscard]] GameState copy_state_core_without_journal(const GameState& source) {
    // ClearAll is the search/branch path. Do not implement it as
    // `GameState branch = source; clear_journal(branch);`: that performs an
    // O(journal) deep copy only to release every copied journal allocation.
    GameState branch{};
    branch.definitions = source.definitions;
    branch.objects = source.objects;
    branch.players = source.players;
    branch.stack = source.stack;
    branch.rng_state = source.rng_state;
    branch.next_event_sequence = source.next_event_sequence;
    branch.next_zone_change_index = source.next_zone_change_index;
    branch.next_damage_prevention_shield_id = source.next_damage_prevention_shield_id;
    branch.next_continuous_effect_timestamp = source.next_continuous_effect_timestamp;
    branch.next_layer_timestamp = source.next_layer_timestamp;
    branch.starting_player = source.starting_player;
    branch.active_player = source.active_player;
    branch.priority_player = source.priority_player;
    branch.turn_number = source.turn_number;
    branch.step = source.step;
    branch.consecutive_priority_passes = source.consecutive_priority_passes;
    branch.attackers_declared_this_step = source.attackers_declared_this_step;
    branch.combat_damage_assigned_this_step = source.combat_damage_assigned_this_step;
    branch.journal_trimmed = true;
    branch.blocker_declaration_complete_players = source.blocker_declaration_complete_players;
    branch.pending_triggers = source.pending_triggers;
    branch.damage_prevention_shields = source.damage_prevention_shields;
    branch.continuous_effects = source.continuous_effects;
    for (auto& trigger : branch.pending_triggers) {
        trigger.trigger_record_index = 0;
    }
    return branch;
}

} // namespace

GameState make_branch_state(const GameState& source, JournalRetention retention) {
    if (retention == JournalRetention::ClearAll) {
        return copy_state_core_without_journal(source);
    }
    return source;
}

bool exile_permanent(GameState& game, ObjectId object_id) {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield) {
        record_event(game, "exile_permanent_ignored", "object#" + std::to_string(object_id.value) + " is not on the battlefield");
        return false;
    }
    record_event(game, "exile_permanent", object_label(game, object_id) + " exiled");
    move_object(game, object_id, obj.owner, Zone::Exile);
    return true;
}

bool sacrifice_permanent(GameState& game, PlayerId controller, ObjectId object_id) {
    if (!valid_player_index(game, controller) || !valid_object_index(game, object_id)) {
        return false;
    }
    auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (obj.zone != Zone::Battlefield || obj.controller != controller || def == nullptr || !def->is_permanent()) {
        record_event(game, "sacrifice_failed", player(game, controller).name + " could not sacrifice object#" + std::to_string(object_id.value));
        return false;
    }
    record_event(game, "sacrifice_permanent", player(game, controller).name + " sacrificed " + object_label(game, object_id));
    move_object(game, object_id, obj.owner, Zone::Graveyard);
    return true;
}

bool gain_control_of_permanent(GameState& game, PlayerId new_controller, ObjectId object_id) {
    if (!valid_player_index(game, new_controller) || player(game, new_controller).lost || !valid_object_index(game, object_id)) {
        record_event(game, "gain_control_failed", "invalid controller/object for object#" + std::to_string(object_id.value));
        return false;
    }
    auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (obj.zone != Zone::Battlefield || def == nullptr || !def->is_permanent()) {
        record_event(game, "gain_control_failed", "object#" + std::to_string(object_id.value) + " is not a battlefield permanent");
        return false;
    }
    if (obj.controller == new_controller) {
        record_event(game, "gain_control_noop", player(game, new_controller).name + " already controls " + object_label(game, object_id));
        return true;
    }
    const PlayerId old_controller = obj.controller;
    auto& old_container = zone(game, old_controller, Zone::Battlefield);
    if (!erase_object_from_container_if_present(old_container, object_id)) {
        record_event(game, "gain_control_failed", object_label(game, object_id) + " missing from old controller battlefield container");
        return false;
    }
    obj.controller = new_controller;
    obj.controlled_since_turn_start_index = player(game, new_controller).turn_start_index;
    clear_combat_links_for_object(game, object_id);
    zone(game, new_controller, Zone::Battlefield).push_back(object_id);
    record_event(game, "gain_control", player(game, new_controller).name + " gained control of " + object_label(game, object_id) + " from " + player(game, old_controller).name);
    return true;
}

bool object_has_copy_effect(const GameState& game, ObjectId object_id) noexcept {
    return valid_object_index(game, object_id) && object(game, object_id).has_copy_effect;
}

std::uint32_t object_copiable_definition_index(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return 0U;
    }
    return current_definition_index_for_object(game, object(game, object_id));
}

void clear_copy_effect(GameState& game, ObjectId object_id) {
    if (!valid_object_index(game, object_id)) {
        return;
    }
    auto& obj = object(game, object_id);
    if (!obj.has_copy_effect) {
        return;
    }
    obj.has_copy_effect = false;
    obj.copied_definition_index = 0U;
    record_event(game, "copy_effect_cleared", object_label(game, object_id) + " reverted to its printed definition");
}

bool become_copy_of_permanent(GameState& game, ObjectId object_id, ObjectId source_id) {
    if (!valid_object_index(game, object_id) || !valid_object_index(game, source_id)) {
        record_event(game, "become_copy_failed", "invalid object/source pair");
        return false;
    }
    auto& target = object(game, object_id);
    const auto& source = object(game, source_id);
    if (target.zone != Zone::Battlefield || source.zone != Zone::Battlefield || target.ceased_to_exist || source.ceased_to_exist) {
        record_event(game, "become_copy_failed", object_label(game, object_id) + " could not copy " + object_label(game, source_id) + " because both objects must be battlefield permanents");
        return false;
    }
    const std::uint32_t source_definition_index = current_definition_index_for_object(game, source);
    if (source_definition_index >= game.definitions.size()) {
        record_event(game, "become_copy_failed", object_label(game, source_id) + " has no valid copiable definition");
        return false;
    }
    target.has_copy_effect = true;
    target.copied_definition_index = source_definition_index;
    clear_combat_links_for_object(game, object_id);
    if (const auto* new_def = current_definition_for_object(game, target); new_def != nullptr && new_def->attachment_kind == AttachmentKind::None) {
        target.attached_to = TargetRef{};
    }
    record_event(game, "become_copy", object_label(game, object_id) + " became a copy of " + object_label(game, source_id) + " using definition#" + std::to_string(source_definition_index));
    return true;
}

void add_regeneration_shield(GameState& game, ObjectId object_id, std::uint32_t amount) {
    if (amount == 0U) {
        return;
    }
    auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield) {
        throw std::logic_error("can only regenerate a permanent on the battlefield in this scaffold");
    }
    obj.regeneration_shields += amount;
    record_event(game, "regeneration_shield_added", object_label(game, object_id) + " shields=" + std::to_string(obj.regeneration_shields));
}

std::uint32_t regeneration_shield_count(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return 0U;
    }
    return object(game, object_id).regeneration_shields;
}

bool destroy_permanent_with_precomputed_ltb_snapshots(GameState& game,
                                                        ObjectId object_id,
                                                        bool allow_regeneration,
                                                        const std::vector<TriggerSourceSnapshot>* precomputed_ltb_snapshots) {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield) {
        record_event(game, "destroy_permanent_ignored", "object#" + std::to_string(object_id.value) + " is not on the battlefield");
        return false;
    }
    if (object_has_ability(game, object_id, AbilityIndestructible)) {
        record_event(game, "destroy_permanent_indestructible", object_label(game, object_id) + " ignored destroy due to indestructible");
        return false;
    }
    if (allow_regeneration && obj.regeneration_shields != 0U) {
        --obj.regeneration_shields;
        obj.tapped = true;
        obj.damage_marked = 0;
        obj.deathtouch_damage_marked = false;
        clear_combat_links_for_object(game, object_id);
        record_event(game, "regenerated", object_label(game, object_id) + " replaced destruction; remaining shields=" + std::to_string(obj.regeneration_shields));
        return true;
    }
    record_event(game, "destroy_permanent", object_label(game, object_id) + " destroyed");
    move_object_with_precomputed_ltb_snapshots(game, object_id, obj.owner, Zone::Graveyard, precomputed_ltb_snapshots);
    return true;
}

bool destroy_permanent(GameState& game, ObjectId object_id, bool allow_regeneration) {
    return destroy_permanent_with_precomputed_ltb_snapshots(game, object_id, allow_regeneration, nullptr);
}

void add_counter_to_object(GameState& game, ObjectId object_id, CounterKind counter_kind, std::uint32_t amount) {
    if (amount == 0U) {
        return;
    }
    if (!counter_kind_is_object(counter_kind)) {
        throw std::logic_error("counter kind is not valid for objects in this scaffold");
    }
    auto& obj = object(game, object_id);
    if (obj.zone != Zone::Battlefield) {
        throw std::logic_error("can only add counters to an object on the battlefield");
    }
    auto& slot = counter_slot(obj.counters, counter_kind);
    const u32 before = slot;
    slot += amount;
    record_object_counter_change(game,
                                 object_id,
                                 counter_kind,
                                 CounterChangeKind::ObjectAdded,
                                 amount,
                                 before,
                                 slot,
                                 "add_object_counter",
                                 object_label(game, object_id) + " +" + std::to_string(amount) + " " + to_string(counter_kind));
}

void remove_counter_from_object(GameState& game, ObjectId object_id, CounterKind counter_kind, std::uint32_t amount) {
    if (amount == 0U) {
        return;
    }
    if (!counter_kind_is_object(counter_kind)) {
        throw std::logic_error("counter kind is not valid for objects in this scaffold");
    }
    auto& obj = object(game, object_id);
    auto& slot = counter_slot(obj.counters, counter_kind);
    const u32 before = slot;
    const u32 removed = std::min(slot, amount);
    slot -= removed;
    if (removed != 0U) {
        record_object_counter_change(game,
                                     object_id,
                                     counter_kind,
                                     CounterChangeKind::ObjectRemoved,
                                     removed,
                                     before,
                                     slot,
                                     "remove_object_counter",
                                     object_label(game, object_id) + " -" + std::to_string(removed) + " " + to_string(counter_kind));
    }
}

void add_counter_to_player(GameState& game, PlayerId player_id, CounterKind counter_kind, std::uint32_t amount) {
    if (amount == 0U) {
        return;
    }
    if (counter_kind != CounterKind::Poison) {
        throw std::logic_error("only poison counters are supported on players in this scaffold");
    }
    auto& p = player(game, player_id);
    const u32 before = p.poison;
    p.poison += amount;
    record_player_counter_change(game,
                                 player_id,
                                 counter_kind,
                                 CounterChangeKind::PlayerAdded,
                                 amount,
                                 before,
                                 p.poison,
                                 "add_player_counter",
                                 p.name + " +" + std::to_string(amount) + " poison");
}

std::uint32_t object_counter_count(const GameState& game, ObjectId object_id, CounterKind counter_kind) noexcept {
    if (!valid_object_index(game, object_id) || !counter_kind_is_object(counter_kind)) {
        return 0U;
    }
    return counter_slot(object(game, object_id).counters, counter_kind);
}

std::uint32_t player_counter_count(const GameState& game, PlayerId player_id, CounterKind counter_kind) noexcept {
    if (!valid_player_index(game, player_id) || counter_kind != CounterKind::Poison) {
        return 0U;
    }
    return game.players[player_id.value - 1U].poison;
}

std::uint32_t planeswalker_loyalty(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return 0U;
    }
    return object(game, object_id).counters.loyalty;
}

std::uint32_t battle_defense(const GameState& game, ObjectId object_id) noexcept {
    if (!object_is_battlefield_battle(game, object_id)) {
        return 0U;
    }
    return object(game, object_id).counters.defense;
}

PlayerId battle_protector(const GameState& game, ObjectId object_id) noexcept {
    if (!object_is_battlefield_battle(game, object_id)) {
        return PlayerId{};
    }
    return object(game, object_id).battle_protector;
}

bool set_battle_protector(GameState& game, ObjectId object_id, PlayerId protector) {
    if (!object_is_battlefield_battle(game, object_id) || !valid_player_index(game, protector) || player(game, protector).lost) {
        record_event(game, "battle_protector_failed", "object#" + std::to_string(object_id.value) + " protector#" + std::to_string(protector.value));
        return false;
    }
    object(game, object_id).battle_protector = protector;
    record_event(game, "battle_protector_set", object_label(game, object_id) + " protector=" + player(game, protector).name);
    return true;
}

[[nodiscard]] bool can_begin_activated_ability_before_payment(const GameState& game,
                                                                  PlayerId controller,
                                                                  ObjectId object_id,
                                                                  u32 ability_index,
                                                                  const std::vector<TargetRef>& targets) noexcept {
    if (!valid_player_index(game, controller) || !valid_object_index(game, object_id)) {
        return false;
    }
    const auto& p = player(game, controller);
    if (p.lost || game.priority_player != controller) {
        return false;
    }
    const auto& obj = object(game, object_id);
    const auto* def_ptr = current_definition_for_object(game, obj);
    if (obj.zone != Zone::Battlefield || obj.controller != controller || def_ptr == nullptr) {
        return false;
    }
    const auto& def = *def_ptr;
    if (!valid_activated_ability_index(def, ability_index)) {
        return false;
    }
    const auto& ability = def.activated_abilities[ability_index - 1U];
    if (!ability.active()) {
        return false;
    }
    if (ability.sorcery_speed && !player_has_sorcery_speed_window(game, controller)) {
        return false;
    }
    if (ability.tap_cost) {
        if (obj.tapped) {
            return false;
        }
        if (object_is_creature(game, obj) && object_has_summoning_sickness(game, object_id)) {
            return false;
        }
    }
    const u32 needed_targets = required_target_count_for_activated_ability(ability);
    return target_set_is_legal_for_source_object(game, targets, ability.target_mask, needed_targets, object_id);
}

bool can_activate_activated_ability(const GameState& game, PlayerId controller, ObjectId object_id, u32 ability_index, TargetRef target) noexcept {
    return can_activate_activated_ability_with_targets(game, controller, object_id, ability_index, single_target_vector(target));
}

bool can_activate_activated_ability_with_targets(const GameState& game, PlayerId controller, ObjectId object_id, u32 ability_index, const std::vector<TargetRef>& targets) noexcept {
    if (!can_begin_activated_ability_before_payment(game, controller, object_id, ability_index, targets)) {
        return false;
    }
    const auto& ability = current_definition_for_object(game, object(game, object_id))->activated_abilities[ability_index - 1U];
    return can_pay_activated_ability_costs(game, controller, object_id, ability);
}

bool activate_activated_ability(GameState& game, PlayerId controller, ObjectId object_id, u32 ability_index, TargetRef target) {
    return activate_activated_ability_with_targets(game, controller, object_id, ability_index, single_target_vector(target));
}

bool activate_activated_ability_with_targets(GameState& game, PlayerId controller, ObjectId object_id, u32 ability_index, const std::vector<TargetRef>& targets) {
    if (!can_begin_activated_ability_before_payment(game, controller, object_id, ability_index, targets)) {
        record_event(game, "activated_ability_failed", "object#" + std::to_string(object_id.value) + " ability#" + std::to_string(ability_index));
        return false;
    }
    auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr || ability_index == 0U || ability_index > def->activated_abilities.size()) {
        return false;
    }
    const auto ability = def->activated_abilities[ability_index - 1U];
    const auto label = object_label(game, object_id) + " " + activated_ability_label(*def, ability_index);
    const auto locked_tap_sources = activation_locked_tap_sources(ability, object_id);
    return commit_paid_action_body_transaction(game,
                                               PaidActionTransactionContext{.action_kind = ActionKind::ActivateActivatedAbility, .player = controller, .source_object = object_id},
                                               [&](GameState& staged_game, u64 physical_state_hash_before) {
        const auto ctx = capture_stack_placement_context(staged_game, object_id);
        const auto stack_event_count_before = staged_game.events.size();
        const ObjectId ability_id = create_activated_ability_stack_object(staged_game, object_id, ability, controller, targets);
        const auto stack_enter_sequence = first_event_sequence_at_or_after(staged_game, stack_event_count_before, "activated_ability_put_on_stack");
        const u64 choices_locked_sequence = latest_event_sequence(staged_game);
        const u32 declaration_record_index = record_activated_ability_paid_action_declaration(staged_game,
                                                                                              controller,
                                                                                              object_id,
                                                                                              ability_id,
                                                                                              ability,
                                                                                              ctx,
                                                                                              ability_index,
                                                                                              stack_enter_sequence,
                                                                                              choices_locked_sequence);
        const auto paid_phase = capture_paid_action_phase_snapshot(staged_game, stack_enter_sequence, choices_locked_sequence);
        if (!pay_mana_cost_with_mana_abilities_excluding_tap_sources(staged_game, controller, ability.mana_cost, locked_tap_sources)) {
            return false;
        }
        if (ability.tap_cost && !pay_tap_cost(staged_game, controller, object_id, label)) {
            return false;
        }
        const auto sacrifice_selection = select_sacrifice_cost_objects(staged_game, controller, ability.sacrifice_cost);
        if (ability.sacrifice_cost.active() && sacrifice_selection.size() != ability.sacrifice_cost.count) {
            return false;
        }
        if (!pay_selected_sacrifice_cost(staged_game, controller, ability.sacrifice_cost, sacrifice_selection, label, object_id)) {
            return false;
        }
        if (!pay_discard_cost(staged_game, controller, ability.discard_cost, label, object_id)) {
            return false;
        }
        if (!pay_life_cost(staged_game, controller, ability.life_cost, label, object_id)) {
            return false;
        }
        if (!pay_return_cost(staged_game, controller, ability.return_cost, label, object_id)) {
            return false;
        }
        staged_game.priority_player = controller;
        staged_game.consecutive_priority_passes = 0;
        record_event(staged_game, "activated_ability_activated", player(staged_game, controller).name + " activated " + label);
        auto placement_record = make_ability_stack_placement_record(staged_game,
                                                                    StackPlacementKind::ActivatedAbility,
                                                                    controller,
                                                                    object_id,
                                                                    ability_id,
                                                                    ctx,
                                                                    ability_index,
                                                                    0,
                                                                    ability.target_mask,
                                                                    ability.target_count,
                                                                    !ability.mana_cost.free(),
                                                                    !ability.mana_cost.free(),
                                                                    ability.tap_cost,
                                                                    ability.tap_cost,
                                                                    ability.sacrifice_cost.active(),
                                                                    ability.sacrifice_cost.active(),
                                                                    ability.discard_cost.active(),
                                                                    ability.discard_cost.active(),
                                                                    ability.life_cost.active(),
                                                                    ability.life_cost.active(),
                                                                    ability.return_cost.active(),
                                                                    ability.return_cost.active(),
                                                                    false);
        seal_paid_action_phase(placement_record, staged_game, paid_phase);
        seal_paid_action_declaration_for_stack_placement(staged_game, declaration_record_index, placement_record);
        const u32 placement_record_index = record_stack_placement(staged_game, std::move(placement_record));
        record_paid_action_transaction_commit(staged_game, ActionKind::ActivateActivatedAbility, placement_record_index, physical_state_hash_before);
        return true;
    });
}

[[nodiscard]] bool can_begin_loyalty_ability_before_payment(const GameState& game,
                                                                 PlayerId controller,
                                                                 ObjectId object_id,
                                                                 const std::vector<TargetRef>& targets) noexcept {
    if (!valid_player_index(game, controller) || !valid_object_index(game, object_id)) {
        return false;
    }
    if (player(game, controller).lost || game.priority_player != controller || game.active_player != controller || !game.stack.empty()) {
        return false;
    }
    const auto phase = phase_for_step(game.step);
    if (phase != Phase::PrecombatMain && phase != Phase::PostcombatMain) {
        return false;
    }
    const auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (obj.zone != Zone::Battlefield || obj.controller != controller || !object_is_planeswalker(game, obj) || def == nullptr) {
        return false;
    }
    if (obj.loyalty_ability_activated_turn == game.turn_number) {
        return false;
    }
    const auto& ability = def->loyalty_ability;
    if (!ability.active()) {
        return false;
    }
    const u32 needed_targets = required_target_count_for_loyalty_ability(ability);
    return target_set_is_legal_for_source_object(game, targets, ability.target_mask, needed_targets, object_id);
}

bool can_activate_loyalty_ability(const GameState& game, PlayerId controller, ObjectId object_id, TargetRef target) noexcept {
    return can_activate_loyalty_ability_with_targets(game, controller, object_id, single_target_vector(target));
}

bool can_activate_loyalty_ability_with_targets(const GameState& game, PlayerId controller, ObjectId object_id, const std::vector<TargetRef>& targets) noexcept {
    if (!can_begin_loyalty_ability_before_payment(game, controller, object_id, targets)) {
        return false;
    }
    const auto& obj = object(game, object_id);
    const auto& ability = current_definition_for_object(game, obj)->loyalty_ability;
    return !(ability.cost < 0 && obj.counters.loyalty < static_cast<u32>(-ability.cost));
}

bool activate_loyalty_ability(GameState& game, PlayerId controller, ObjectId object_id, TargetRef target) {
    return activate_loyalty_ability_with_targets(game, controller, object_id, single_target_vector(target));
}

bool activate_loyalty_ability_with_targets(GameState& game, PlayerId controller, ObjectId object_id, const std::vector<TargetRef>& targets) {
    if (!can_begin_loyalty_ability_before_payment(game, controller, object_id, targets)) {
        record_event(game, "loyalty_ability_failed", "object#" + std::to_string(object_id.value));
        return false;
    }
    const auto* source_def = current_definition_for_object(game, object(game, object_id));
    if (source_def == nullptr) {
        return false;
    }
    const auto ability = source_def->loyalty_ability;
    return commit_paid_action_body_transaction(game,
                                               PaidActionTransactionContext{.action_kind = ActionKind::ActivateLoyaltyAbility, .player = controller, .source_object = object_id},
                                               [&](GameState& staged_game, u64 physical_state_hash_before) {
        const auto ctx = capture_stack_placement_context(staged_game, object_id);
        const auto stack_event_count_before = staged_game.events.size();
        const ObjectId ability_id = create_loyalty_ability_stack_object(staged_game, object_id, ability, controller, targets);
        const auto stack_enter_sequence = first_event_sequence_at_or_after(staged_game, stack_event_count_before, "loyalty_ability_put_on_stack");
        const u64 choices_locked_sequence = latest_event_sequence(staged_game);
        const u32 declaration_record_index = record_loyalty_ability_paid_action_declaration(staged_game,
                                                                                            controller,
                                                                                            object_id,
                                                                                            ability_id,
                                                                                            ability,
                                                                                            ctx,
                                                                                            stack_enter_sequence,
                                                                                            choices_locked_sequence);
        const auto paid_phase = capture_paid_action_phase_snapshot(staged_game, stack_enter_sequence, choices_locked_sequence);

        auto& source_obj = object(staged_game, object_id);
        const u32 loyalty_before = source_obj.counters.loyalty;
        const u32 loyalty_delta = ability.cost >= 0
            ? static_cast<u32>(ability.cost)
            : static_cast<u32>(-ability.cost);
        if (ability.cost >= 0) {
            source_obj.counters.loyalty += loyalty_delta;
        } else {
            if (source_obj.counters.loyalty < loyalty_delta) {
                record_event(staged_game,
                             "loyalty_cost_payment_failed",
                             object_label(staged_game, object_id) + " unable to pay loyalty cost " + std::to_string(ability.cost) +
                                 " loyalty=" + std::to_string(source_obj.counters.loyalty));
                return false;
            }
            source_obj.counters.loyalty -= loyalty_delta;
        }
        if (loyalty_delta != 0U) {
            const u32 counter_change_record_index = static_cast<u32>(staged_game.counter_change_records.size() + 1U);
            record_object_counter_change(staged_game,
                                         object_id,
                                         CounterKind::Loyalty,
                                         ability.cost >= 0 ? CounterChangeKind::ObjectAdded : CounterChangeKind::ObjectRemoved,
                                         loyalty_delta,
                                         loyalty_before,
                                         source_obj.counters.loyalty,
                                         "loyalty_cost_paid",
                                         object_label(staged_game, object_id) + " paid loyalty cost " + std::to_string(ability.cost),
                                         object_id,
                                         false,
                                         0U,
                                         true,
                                         false);
            LoyaltyCostPaymentRecord payment{};
            payment.sequence = counter_change_record_index <= staged_game.counter_change_records.size()
                ? staged_game.counter_change_records[counter_change_record_index - 1U].sequence
                : 0U;
            payment.payer = controller;
            payment.source_object = object_id;
            payment.source_zone_change_index_before = ctx.source_zone_change_index_before;
            payment.cost_delta = ability.cost;
            payment.loyalty_before = loyalty_before;
            payment.loyalty_after = source_obj.counters.loyalty;
            payment.counter_change_record_index = counter_change_record_index;
            record_loyalty_cost_payment(staged_game, std::move(payment));
        }
        source_obj.loyalty_ability_activated_turn = staged_game.turn_number;
        record_event(staged_game,
                     "loyalty_ability_activated",
                     player(staged_game, controller).name + " activated " + object_label(staged_game, object_id) +
                         " cost=" + std::to_string(ability.cost) + " loyalty=" + std::to_string(source_obj.counters.loyalty));
        staged_game.priority_player = controller;
        staged_game.consecutive_priority_passes = 0;
        auto placement_record = make_ability_stack_placement_record(staged_game,
                                                                    StackPlacementKind::LoyaltyAbility,
                                                                    controller,
                                                                    object_id,
                                                                    ability_id,
                                                                    ctx,
                                                                    1U,
                                                                    ability.cost,
                                                                    ability.target_mask,
                                                                    ability.target_count,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    false,
                                                                    true);
        seal_paid_action_phase(placement_record, staged_game, paid_phase);
        seal_paid_action_declaration_for_stack_placement(staged_game, declaration_record_index, placement_record);
        const u32 placement_record_index = record_stack_placement(staged_game, std::move(placement_record));
        record_paid_action_transaction_commit(staged_game, ActionKind::ActivateLoyaltyAbility, placement_record_index, physical_state_hash_before);
        apply_state_based_actions(staged_game);
        return true;
    });
}
bool object_has_ability(const GameState& game, ObjectId object_id, KeywordAbilityMask ability) noexcept {
    return source_has_keyword(game, object_id, ability);
}

void create_continuous_effect(GameState& game, ObjectId source_id, PlayerId controller, const StaticEffectDefinition& effect, ContinuousEffectDuration duration, const std::vector<TargetRef>& targets) {
    if (duration == ContinuousEffectDuration::None || !effect.active()) {
        return;
    }
    ContinuousEffectDefinition continuous;
    continuous.name = effect.name.empty() ? "continuous effect" : effect.name;
    continuous.effect = effect;
    continuous.duration = duration;
    continuous.controller = controller;
    continuous.source = source_id;
    continuous.timestamp = game.next_layer_timestamp++;
    game.next_continuous_effect_timestamp = std::max(game.next_continuous_effect_timestamp, continuous.timestamp + 1U);
    for (const auto target : targets) {
        ContinuousEffectTarget locked;
        locked.target = target;
        if (target.kind == TargetKind::Object && valid_object_index(game, target.object)) {
            locked.object_zone_change_index = object(game, target.object).zone_change_index;
        }
        continuous.locked_targets.push_back(locked);
    }
    game.continuous_effects.push_back(std::move(continuous));
    record_event(game, "continuous_effect_created", object_label(game, source_id) + " duration=" + to_string(duration) + " count=" + std::to_string(game.continuous_effects.size()));
}

std::size_t continuous_effect_count(const GameState& game) noexcept {
    return game.continuous_effects.size();
}

void expire_continuous_effects(GameState& game, ContinuousEffectDuration duration) {
    const auto before = game.continuous_effects.size();
    game.continuous_effects.erase(std::remove_if(game.continuous_effects.begin(), game.continuous_effects.end(), [&](const ContinuousEffectDefinition& effect) {
        return effect.duration == duration;
    }), game.continuous_effects.end());
    const auto removed = before - game.continuous_effects.size();
    if (removed != 0U) {
        record_event(game, "continuous_effects_expired", std::to_string(removed) + " " + to_string(duration) + " effect(s) expired");
    }
}

namespace {
[[nodiscard]] StaticBasePowerToughness static_power_toughness_set(const GameState& game, ObjectId object_id) noexcept {
    StaticBasePowerToughness result{};
    if (!valid_object_index(game, object_id)) {
        return result;
    }
    const u32 layer4_types = object_type_mask(game, object_id);
    for (const auto& application : collect_layer_effects(game, object_id, static_effect_has_base_pt_set_payload)) {
        if (application.effect == nullptr || !type_mask_matches_static_effect(layer4_types, application.effect->affected_type_mask)) {
            continue;
        }
        result.active = true;
        result.power = application.effect->set_power;
        result.toughness = application.effect->set_toughness;
    }
    return result;
}
} // namespace

std::int32_t static_power_modifier(const GameState& game, ObjectId object_id) noexcept {
    std::int32_t value = 0;
    const u32 layer4_types = object_type_mask(game, object_id);
    for (const auto& application : collect_layer_effects(game, object_id, static_effect_has_power_modifier_payload)) {
        if (application.effect != nullptr && type_mask_matches_static_effect(layer4_types, application.effect->affected_type_mask)) {
            value += application.effect->power_modifier;
        }
    }
    return value;
}

std::int32_t static_toughness_modifier(const GameState& game, ObjectId object_id) noexcept {
    std::int32_t value = 0;
    const u32 layer4_types = object_type_mask(game, object_id);
    for (const auto& application : collect_layer_effects(game, object_id, static_effect_has_toughness_modifier_payload)) {
        if (application.effect != nullptr && type_mask_matches_static_effect(layer4_types, application.effect->affected_type_mask)) {
            value += application.effect->toughness_modifier;
        }
    }
    return value;
}

bool can_attach_object(const GameState& game, ObjectId attachment_id, TargetRef target) noexcept {
    if (!valid_object_index(game, attachment_id)) {
        return false;
    }
    const auto& attachment = object(game, attachment_id);
    if (attachment.zone != Zone::Battlefield) {
        return false;
    }
    const auto* def_ptr = current_definition_for_object(game, attachment);
    if (def_ptr == nullptr) {
        return false;
    }
    const auto& def = *def_ptr;
    if (def.attachment_kind == AttachmentKind::None || def.attachment_kind == AttachmentKind::Count) {
        return false;
    }
    // This intentionally models the common rule seam that an Aura/Equipment/Fortification
    // that is also a creature cannot legally be attached in this scaffold.
    if (object_is_creature(game, attachment)) {
        return false;
    }
    if (!target.valid()) {
        return false;
    }

    switch (def.attachment_kind) {
        case AttachmentKind::Aura: {
            const u32 mask = def.target_mask == TargetNone ? TargetObject : def.target_mask;
            return target_ref_is_legal_for_source_object(game, target, mask, attachment_id);
        }
        case AttachmentKind::Equipment:
            return target.kind == TargetKind::Object &&
                   object_is_battlefield_creature(game, target.object) &&
                   target_ref_is_legal_for_source_object(game, target, TargetObject, attachment_id);
        case AttachmentKind::Fortification:
            if (target.kind != TargetKind::Object || !target_ref_is_legal_for_source_object(game, target, TargetObject, attachment_id)) {
                return false;
            }
            return object_has_type(game, target.object, TypeLand);
        case AttachmentKind::None:
        case AttachmentKind::Count:
            return false;
    }
    return false;
}

bool attach_object_to(GameState& game, ObjectId attachment_id, TargetRef target) {
    if (!valid_object_index(game, attachment_id)) {
        return false;
    }
    if (!can_attach_object(game, attachment_id, target)) {
        record_event(game, "attach_failed", object_label(game, attachment_id) + " could not attach to " + target_label(game, target));
        return false;
    }
    auto& attachment = object(game, attachment_id);
    if (target_refs_equal(attachment.attached_to, target)) {
        record_event(game, "attach_noop", object_label(game, attachment_id) + " was already attached to " + target_label(game, target));
        return true;
    }
    attachment.attached_to = target;
    if (attachment.zone == Zone::Battlefield) {
        attachment.layer_timestamp = game.next_layer_timestamp++;
    }
    record_event(game, "attach", object_label(game, attachment_id) + " attached to " + target_label(game, target));
    return true;
}

void detach_object(GameState& game, ObjectId attachment_id) {
    if (!valid_object_index(game, attachment_id)) {
        return;
    }
    auto& attachment = object(game, attachment_id);
    if (!attachment.attached_to.valid()) {
        return;
    }
    const auto old_target = attachment.attached_to;
    attachment.attached_to = TargetRef{};
    record_event(game, "detach", object_label(game, attachment_id) + " detached from " + target_label(game, old_target));
}

TargetRef object_attachment_target(const GameState& game, ObjectId attachment_id) noexcept {
    if (!valid_object_index(game, attachment_id)) {
        return TargetRef{};
    }
    return object(game, attachment_id).attached_to;
}

std::uint32_t attachment_count_for_target(const GameState& game, TargetRef target) noexcept {
    u32 count = 0;
    for (const auto& candidate : game.objects) {
        if (candidate.zone == Zone::Battlefield && target_refs_equal(candidate.attached_to, target)) {
            ++count;
        }
    }
    return count;
}

std::uint32_t card_color_mask(const CardDefinition& definition) noexcept {
    const u32 explicit_colors = legal_color_mask(definition.color_mask);
    if (explicit_colors != ColorNone) {
        return explicit_colors;
    }
    return colors_from_mana_cost(definition.mana_cost);
}

std::uint32_t object_type_mask(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return TypeNone;
    }
    const auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return TypeNone;
    }
    u32 types = def->type_mask;
    if (obj.zone != Zone::Battlefield || obj.ceased_to_exist) {
        return types;
    }
    for (const auto& application : collect_layer_effects(game, object_id, static_effect_has_type_layer_payload)) {
        if (application.effect != nullptr && type_mask_matches_static_effect(types, application.effect->affected_type_mask)) {
            types &= ~application.effect->removed_type_mask;
            types |= application.effect->added_type_mask;
        }
    }
    return types;
}

bool object_has_type(const GameState& game, ObjectId object_id, CardTypeMask type) noexcept {
    return has_type_mask(object_type_mask(game, object_id), type);
}

std::uint32_t object_color_mask(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return ColorNone;
    }
    const auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return ColorNone;
    }
    u32 colors = card_color_mask(*def);
    if (obj.zone != Zone::Battlefield || obj.ceased_to_exist) {
        return colors;
    }
    const u32 layer4_types = object_type_mask(game, object_id);
    for (const auto& application : collect_layer_effects(game, object_id, static_effect_has_color_layer_payload)) {
        if (application.effect == nullptr || !type_mask_matches_static_effect(layer4_types, application.effect->affected_type_mask)) {
            continue;
        }
        if (application.effect->sets_color) {
            colors = legal_color_mask(application.effect->set_color_mask);
        }
        colors &= ~legal_color_mask(application.effect->removed_color_mask);
        colors |= legal_color_mask(application.effect->added_color_mask);
        colors = legal_color_mask(colors);
    }
    return colors;
}

bool object_has_protection_from_color(const GameState& game, ObjectId object_id, CardColorMask color) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto& obj = object(game, object_id);
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return false;
    }
    return color_masks_overlap(def->protection_color_mask, static_cast<u32>(color));
}

bool target_has_protection_from_source(const GameState& game, TargetRef target, ObjectId source_id) noexcept {
    if (target.kind != TargetKind::Object || !valid_object_index(game, target.object) || !valid_object_index(game, source_id)) {
        return false;
    }
    const auto& obj = object(game, target.object);
    if (obj.zone != Zone::Battlefield) {
        return false;
    }
    const auto* def = current_definition_for_object(game, obj);
    if (def == nullptr) {
        return false;
    }
    const u32 protection_colors = legal_color_mask(def->protection_color_mask);
    if (protection_colors == ColorNone) {
        return false;
    }
    const u32 source_colors = object_color_mask(game, source_id);
    return color_masks_overlap(protection_colors, source_colors);
}

bool object_has_summoning_sickness(const GameState& game, ObjectId object_id) noexcept {
    if (!object_is_battlefield_creature(game, object_id)) {
        return false;
    }
    if (object_has_ability(game, object_id, AbilityHaste)) {
        return false;
    }
    const auto& obj = object(game, object_id);
    if (!valid_player_index(game, obj.controller)) {
        return false;
    }
    const auto& controller = game.players[obj.controller.value - 1U];
    return controller.turn_start_index <= obj.controlled_since_turn_start_index;
}

std::int32_t effective_power(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return 0;
    }
    const auto& obj = object(game, object_id);
    const auto base = static_power_toughness_set(game, object_id);
    const auto* current_def = current_definition_for_object(game, obj);
    std::int32_t value = base.active ? base.power : (current_def != nullptr ? current_def->printed_power : obj.power);
    value += static_cast<std::int32_t>(obj.counters.plus_one_plus_one) - static_cast<std::int32_t>(obj.counters.minus_one_minus_one);
    const auto target = TargetRef{.kind = TargetKind::Object, .object = object_id};
    for (const auto& attachment : game.objects) {
        if (attachment.zone != Zone::Battlefield || !target_refs_equal(attachment.attached_to, target)) {
            continue;
        }
        const auto* attachment_def = current_definition_for_object(game, attachment);
        if (attachment_def == nullptr) {
            continue;
        }
        value += attachment_def->attachment_power_bonus;
    }
    value += static_power_modifier(game, object_id);
    return value;
}

std::int32_t effective_toughness(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return 0;
    }
    const auto& obj = object(game, object_id);
    const auto base = static_power_toughness_set(game, object_id);
    const auto* current_def = current_definition_for_object(game, obj);
    std::int32_t value = base.active ? base.toughness : (current_def != nullptr ? current_def->printed_toughness : obj.toughness);
    value += static_cast<std::int32_t>(obj.counters.plus_one_plus_one) - static_cast<std::int32_t>(obj.counters.minus_one_minus_one);
    const auto target = TargetRef{.kind = TargetKind::Object, .object = object_id};
    for (const auto& attachment : game.objects) {
        if (attachment.zone != Zone::Battlefield || !target_refs_equal(attachment.attached_to, target)) {
            continue;
        }
        const auto* attachment_def = current_definition_for_object(game, attachment);
        if (attachment_def == nullptr) {
            continue;
        }
        value += attachment_def->attachment_toughness_bonus;
    }
    value += static_toughness_modifier(game, object_id);
    return value;
}

void add_damage_prevention_shield(GameState& game, TargetRef target, std::uint32_t amount, std::string label, std::uint32_t choice_rank) {
    if (amount == 0U) {
        return;
    }
    if (!target_ref_is_legal(game, target, TargetAny)) {
        throw std::logic_error("damage prevention target is not legal in current scaffold");
    }
    TargetRef stamped_target = stamp_target_for_choice(game, target);
    const u64 shield_id = game.next_damage_prevention_shield_id++;
    std::string stored_label = std::move(label);
    game.damage_prevention_shields.push_back(DamagePreventionShield{
        .id = shield_id,
        .target = stamped_target,
        .remaining = amount,
        .choice_rank = choice_rank,
        .label = stored_label
    });
    const std::string detail = target_label(game, stamped_target) + " amount=" + std::to_string(amount);
    record_damage_prevention_change(game,
                                    DamagePreventionRecord{
                                        .kind = DamagePreventionRecordKind::ShieldAdded,
                                        .shield_id = shield_id,
                                        .target = stamped_target,
                                        .amount = amount,
                                        .remaining_before = 0U,
                                        .remaining_after = amount,
                                        .choice_rank = choice_rank,
                                        .label = std::move(stored_label)
                                    },
                                    "damage_prevention_shield_added",
                                    detail);
}

std::uint32_t damage_prevention_shield_total(const GameState& game, TargetRef target) noexcept {
    u32 total = 0;
    for (const auto& shield : game.damage_prevention_shields) {
        if (same_target(shield.target, target)) {
            total += shield.remaining;
        }
    }
    return total;
}

std::size_t damage_prevention_shield_count(const GameState& game) noexcept {
    return game.damage_prevention_shields.size();
}

bool target_ref_is_legal(const GameState& game, TargetRef target, std::uint32_t target_mask) noexcept {
    switch (target.kind) {
        case TargetKind::Player:
            return (target_mask & TargetPlayer) != 0U &&
                   target.player.valid() &&
                   target.player.value <= game.players.size() &&
                   !game.players[target.player.value - 1U].lost;
        case TargetKind::Object: {
            if (!target.object.valid() || target.object.value > game.objects.size()) {
                return false;
            }
            const auto& obj = game.objects[target.object.value - 1U];
            const bool battlefield_target_allowed = (target_mask & TargetObject) != 0U && obj.zone == Zone::Battlefield;
            const bool stack_target_allowed = (target_mask & TargetStackObject) != 0U && obj.zone == Zone::Stack;
            if (!battlefield_target_allowed && !stack_target_allowed) {
                return false;
            }
            if (target.object_zone_change_index != 0U && obj.zone_change_index != target.object_zone_change_index) {
                return false;
            }
            return true;
        }
        case TargetKind::None:
            return false;
    }
    return false;
}

bool target_ref_is_legal_for_source(const GameState& game, TargetRef target, std::uint32_t target_mask, PlayerId source_controller) noexcept {
    if (!target_ref_is_legal(game, target, target_mask)) {
        return false;
    }
    if (target.kind == TargetKind::Object) {
        const auto& obj = object(game, target.object);
        if (obj.zone == Zone::Battlefield) {
            if (source_has_keyword(game, target.object, AbilityShroud)) {
                return false;
            }
            if (source_has_keyword(game, target.object, AbilityHexproof) && obj.controller != source_controller) {
                return false;
            }
        }
    }
    return true;
}


bool target_ref_is_legal_for_source_object(const GameState& game, TargetRef target, std::uint32_t target_mask, ObjectId source_id) noexcept {
    PlayerId source_controller{};
    if (valid_object_index(game, source_id)) {
        source_controller = object(game, source_id).controller;
    }
    if (!target_ref_is_legal_for_source(game, target, target_mask, source_controller)) {
        return false;
    }
    if (target_has_protection_from_source(game, target, source_id)) {
        return false;
    }
    return true;
}

[[nodiscard]] TargetResolutionCheckRecord make_target_resolution_check_record(const GameState& game,
                                                                              TargetRef target,
                                                                              u32 target_index,
                                                                              std::uint32_t target_mask,
                                                                              ObjectId source_id) noexcept {
    PlayerId source_controller{};
    if (valid_object_index(game, source_id)) {
        source_controller = object(game, source_id).controller;
    }

    TargetResolutionCheckRecord record{
        .target_index = target_index,
        .target = target,
        .source_controller = source_controller,
        .legal_on_resolution = false,
        .failure_kind = TargetLegalityFailureKind::None,
        .object_zone_on_resolution = Zone::Count,
        .object_zone_change_index_on_resolution = 0U
    };

    switch (target.kind) {
        case TargetKind::None:
            record.failure_kind = TargetLegalityFailureKind::EmptyTarget;
            return record;
        case TargetKind::Player:
            if ((target_mask & TargetPlayer) == 0U) {
                record.failure_kind = TargetLegalityFailureKind::TargetKindNotAllowed;
                return record;
            }
            if (!target.player.valid() || target.player.value > game.players.size() || game.players[target.player.value - 1U].lost) {
                record.failure_kind = TargetLegalityFailureKind::PlayerMissingOrLost;
                return record;
            }
            record.legal_on_resolution = true;
            return record;
        case TargetKind::Object:
            if ((target_mask & (TargetObject | TargetStackObject)) == 0U) {
                record.failure_kind = TargetLegalityFailureKind::TargetKindNotAllowed;
                return record;
            }
            if (!target.object.valid() || target.object.value > game.objects.size()) {
                record.failure_kind = TargetLegalityFailureKind::ObjectMissing;
                return record;
            }
            break;
    }

    const auto& obj = game.objects[target.object.value - 1U];
    record.object_zone_on_resolution = obj.zone;
    record.object_zone_change_index_on_resolution = obj.zone_change_index;
    const bool battlefield_target_allowed = (target_mask & TargetObject) != 0U && obj.zone == Zone::Battlefield;
    const bool stack_target_allowed = (target_mask & TargetStackObject) != 0U && obj.zone == Zone::Stack;
    if (!battlefield_target_allowed && !stack_target_allowed) {
        record.failure_kind = TargetLegalityFailureKind::ObjectZoneNotAllowed;
        return record;
    }
    if (target.object_zone_change_index != 0U && obj.zone_change_index != target.object_zone_change_index) {
        record.failure_kind = TargetLegalityFailureKind::ObjectZoneChangeMismatch;
        return record;
    }
    if (obj.zone == Zone::Battlefield) {
        if (source_has_keyword(game, target.object, AbilityShroud)) {
            record.failure_kind = TargetLegalityFailureKind::Shroud;
            return record;
        }
        if (source_has_keyword(game, target.object, AbilityHexproof) && obj.controller != source_controller) {
            record.failure_kind = TargetLegalityFailureKind::Hexproof;
            return record;
        }
    }
    if (target_has_protection_from_source(game, target, source_id)) {
        record.failure_kind = TargetLegalityFailureKind::Protection;
        return record;
    }

    record.legal_on_resolution = true;
    return record;
}

[[nodiscard]] std::vector<TargetResolutionCheckRecord> make_target_resolution_checks(const GameState& game,
                                                                                      const std::vector<TargetRef>& targets,
                                                                                      std::uint32_t target_mask,
                                                                                      ObjectId source_id) {
    std::vector<TargetResolutionCheckRecord> checks;
    checks.reserve(targets.size());
    for (std::size_t i = 0; i < targets.size(); ++i) {
        checks.push_back(make_target_resolution_check_record(game, targets[i], static_cast<u32>(i + 1U), target_mask, source_id));
    }
    return checks;
}

[[nodiscard]] std::vector<TargetRef> legal_targets_from_resolution_checks(const std::vector<TargetResolutionCheckRecord>& checks) {
    std::vector<TargetRef> targets;
    targets.reserve(checks.size());
    for (const auto& check : checks) {
        if (check.legal_on_resolution) {
            targets.push_back(check.target);
        }
    }
    return targets;
}

std::vector<TargetRef> enumerate_legal_targets(const GameState& game, std::uint32_t target_mask) {
    std::vector<TargetRef> targets;
    if ((target_mask & TargetPlayer) != 0U) {
        for (const auto& p : game.players) {
            if (!p.lost) {
                targets.push_back(TargetRef{.kind = TargetKind::Player, .player = p.id});
            }
        }
    }
    if ((target_mask & TargetObject) != 0U) {
        for (const auto& p : game.players) {
            for (const auto id : p.zones[zone_index(Zone::Battlefield)]) {
                targets.push_back(TargetRef{.kind = TargetKind::Object, .object = id, .object_zone_change_index = object(game, id).zone_change_index});
            }
        }
    }
    if ((target_mask & TargetStackObject) != 0U) {
        for (const auto id : game.stack) {
            targets.push_back(TargetRef{.kind = TargetKind::Object, .object = id, .object_zone_change_index = object(game, id).zone_change_index});
        }
    }
    return targets;
}

std::vector<TargetRef> enumerate_legal_targets_for_source(const GameState& game, std::uint32_t target_mask, PlayerId source_controller) {
    std::vector<TargetRef> filtered;
    for (const auto target : enumerate_legal_targets(game, target_mask)) {
        if (target_ref_is_legal_for_source(game, target, target_mask, source_controller)) {
            filtered.push_back(target);
        }
    }
    return filtered;
}

std::vector<TargetRef> enumerate_legal_targets_for_source_object(const GameState& game, std::uint32_t target_mask, ObjectId source_id) {
    std::vector<TargetRef> filtered;
    for (const auto target : enumerate_legal_targets(game, target_mask)) {
        if (target_ref_is_legal_for_source_object(game, target, target_mask, source_id)) {
            filtered.push_back(target);
        }
    }
    return filtered;
}

std::vector<std::vector<TargetRef>> enumerate_legal_target_sets_for_source_object(const GameState& game,
                                                                                  std::uint32_t target_mask,
                                                                                  std::uint32_t target_count,
                                                                                  ObjectId source_id) {
    std::vector<std::vector<TargetRef>> sets;
    if (target_count == 0U || target_mask == TargetNone) {
        if (target_count == 0U && target_mask == TargetNone) {
            sets.push_back({});
        }
        return sets;
    }
    const auto legal_targets = enumerate_legal_targets_for_source_object(game, target_mask, source_id);
    if (legal_targets.size() < target_count) {
        return sets;
    }
    std::vector<TargetRef> current;
    current.reserve(target_count);
    auto build = [&](auto&& self, std::size_t start) -> void {
        if (current.size() == target_count) {
            sets.push_back(current);
            return;
        }
        const std::size_t remaining = static_cast<std::size_t>(target_count - current.size());
        if (legal_targets.size() < remaining || start > legal_targets.size() - remaining) {
            return;
        }
        for (std::size_t i = start; i <= legal_targets.size() - remaining; ++i) {
            current.push_back(legal_targets[i]);
            self(self, i + 1U);
            current.pop_back();
        }
    };
    build(build, 0U);
    return sets;
}

void deal_damage_to_target_impl(GameState& game, ObjectId source_id, TargetRef target, std::uint32_t amount, bool unpreventable) {
    if (amount == 0U) {
        return;
    }
    const std::string source = source_id.valid() && valid_object_index(game, source_id) ? object_label(game, source_id) : "<source>";
    const TargetRef target_snapshot = damage_target_snapshot(game, target);
    PlayerId source_controller{};
    u32 source_color_mask = ColorNone;
    u32 source_ability_mask = AbilityNone;
    u64 source_zone_change_index = 0;
    if (source_id.valid() && valid_object_index(game, source_id)) {
        const auto& source_obj = object(game, source_id);
        source_controller = source_obj.controller;
        source_color_mask = object_color_mask(game, source_id);
        source_ability_mask = derived_ability_mask(game, source_id);
        source_zone_change_index = source_obj.zone_change_index;
    }
    const bool source_has_lifelink = has_ability_mask(source_ability_mask, AbilityLifelink);
    const bool source_has_deathtouch = has_ability_mask(source_ability_mask, AbilityDeathtouch);
    const bool target_was_creature = target_snapshot.kind == TargetKind::Object && valid_object_index(game, target_snapshot.object) && object_is_battlefield_creature(game, target_snapshot.object);
    const bool target_was_planeswalker = target_snapshot.kind == TargetKind::Object && valid_object_index(game, target_snapshot.object) && object_is_battlefield_planeswalker(game, target_snapshot.object);
    const bool target_was_battle = target_snapshot.kind == TargetKind::Object && valid_object_index(game, target_snapshot.object) && object_is_battlefield_battle(game, target_snapshot.object);
    const bool target_was_damageable = target_snapshot.kind == TargetKind::Player || target_was_creature || target_was_planeswalker || target_was_battle;
    const u64 target_zone_change_index = target_snapshot.kind == TargetKind::Object ? target_snapshot.object_zone_change_index : 0U;
    const bool protection_would_prevent = target_has_protection_from_source(game, target_snapshot, source_id);

    auto append_damage_record = [&](u64 sequence,
                                    u32 prevented,
                                    u32 dealt,
                                    u32 not_dealt,
                                    bool prevented_by_protection,
                                    bool damage_disallowed_by_target_type,
                                    u32 counters_removed,
                                    u32 first_damage_counter_change_record_index,
                                    u32 damage_counter_change_record_count,
                                    u32 first_damage_life_change_record_index,
                                    u32 damage_life_change_record_count,
                                    u32 first_prevention_record_index,
                                    u32 prevention_record_count) -> u32 {
        const u32 damage_record_index = static_cast<u32>(game.damage_records.size() + 1U);
        game.damage_records.push_back(DamageRecord{
            .sequence = sequence,
            .source = source_id,
            .source_controller = source_controller,
            .target = target_snapshot,
            .amount = amount,
            .prevented = prevented,
            .dealt = dealt,
            .not_dealt = not_dealt,
            .prevented_by_protection = prevented_by_protection,
            .unpreventable = unpreventable,
            .protection_prevention_ignored = unpreventable && protection_would_prevent,
            .source_had_lifelink = source_has_lifelink,
            .source_had_deathtouch = source_has_deathtouch,
            .source_color_mask = legal_color_mask(source_color_mask),
            .source_ability_mask = source_ability_mask,
            .source_zone_change_index = source_zone_change_index,
            .target_zone_change_index = target_zone_change_index,
            .target_was_creature = target_was_creature,
            .target_was_planeswalker = target_was_planeswalker,
            .target_was_battle = target_was_battle,
            .target_was_damageable = target_was_damageable,
            .damage_disallowed_by_target_type = damage_disallowed_by_target_type,
            .counters_removed = counters_removed,
            .first_damage_counter_change_record_index = first_damage_counter_change_record_index,
            .damage_counter_change_record_count = damage_counter_change_record_count,
            .first_damage_life_change_record_index = first_damage_life_change_record_index,
            .damage_life_change_record_count = damage_life_change_record_count,
            .first_damage_prevention_record_index = first_prevention_record_index,
            .damage_prevention_record_count = prevention_record_count
        });
        return damage_record_index;
    };

    if (target_snapshot.kind == TargetKind::Object && !valid_object_index(game, target_snapshot.object)) {
        throw std::logic_error("damage target object is invalid");
    }
    if (target_snapshot.kind == TargetKind::Object && !target_was_damageable) {
        const u64 sequence = game.next_event_sequence;
        const u32 damage_record_index = append_damage_record(sequence, 0U, 0U, amount, false, true, 0U, 0U, 0U, 0U, 0U, 0U, 0U);
        record_event_with_links(game,
                                "damage_disallowed_target_type",
                                source + " could not deal " + std::to_string(amount) + " damage to " + target_label(game, target_snapshot) + " because the target is not a battle, creature, or planeswalker",
                                EventRecordLinks{
                                    .kind = EventRecordKind::Damage,
                                    .object = source_id,
                                    .player = source_controller,
                                    .target = target_snapshot,
                                    .damage_record_index = damage_record_index
                                });
        return;
    }

    if (protection_would_prevent && !unpreventable) {
        const u64 sequence = game.next_event_sequence;
        const u32 damage_record_index = append_damage_record(sequence, amount, 0U, 0U, true, false, 0U, 0U, 0U, 0U, 0U, 0U, 0U);
        record_event_with_links(game,
                                "damage_prevented_by_protection",
                                source + " damage to " + target_label(game, target_snapshot) + " was prevented by protection",
                                EventRecordLinks{
                                    .kind = EventRecordKind::Damage,
                                    .object = source_id,
                                    .player = source_controller,
                                    .target = target_snapshot,
                                    .damage_record_index = damage_record_index
                                });
        return;
    }
    const auto prevention = unpreventable ? apply_unpreventable_damage_prevention(game, target_snapshot, amount) :
        apply_damage_prevention(game, target_snapshot, amount);
    const u32 remaining_damage = prevention.remaining;
    if (remaining_damage == 0U) {
        const u64 sequence = game.next_event_sequence;
        const u32 damage_record_index = append_damage_record(sequence, prevention.prevented, 0U, 0U, false, false, 0U, 0U, 0U, 0U, 0U, prevention.first_record_index, prevention.record_count);
        link_damage_prevention_record_range_to_damage(game, prevention.first_record_index, prevention.record_count, damage_record_index);
        record_event_with_links(game,
                                "damage_event_prevented",
                                source + " dealt no damage to " + target_label(game, target_snapshot),
                                EventRecordLinks{
                                    .kind = EventRecordKind::Damage,
                                    .object = source_id,
                                    .player = source_controller,
                                    .target = target_snapshot,
                                    .damage_record_index = damage_record_index
                                });
        return;
    }
    switch (target_snapshot.kind) {
        case TargetKind::Player: {
            if (!valid_player_index(game, target_snapshot.player)) {
                throw std::logic_error("damage target player is invalid");
            }
            const u32 life_change_records_before_damage_results = static_cast<u32>(game.life_change_records.size());
            lose_life(game, target_snapshot.player, static_cast<std::int32_t>(remaining_damage));
            if (source_has_lifelink && valid_player_index(game, source_controller)) {
                gain_life(game, source_controller, static_cast<std::int32_t>(remaining_damage));
                record_event(game, "lifelink_gain", source + " caused " + player(game, source_controller).name + " to gain " + std::to_string(remaining_damage));
            }
            const u32 damage_life_change_record_count = game.life_change_records.size() > life_change_records_before_damage_results
                ? static_cast<u32>(game.life_change_records.size() - life_change_records_before_damage_results)
                : 0U;
            const u32 first_damage_life_change_record_index = damage_life_change_record_count != 0U
                ? life_change_records_before_damage_results + 1U
                : 0U;
            const u32 damage_record_index = append_damage_record(game.next_event_sequence, prevention.prevented, remaining_damage, 0U, false, false, 0U, 0U, 0U, first_damage_life_change_record_index, damage_life_change_record_count, prevention.first_record_index, prevention.record_count);
            link_life_change_record_range_to_damage(game, first_damage_life_change_record_index, damage_life_change_record_count, damage_record_index, source_id, source_zone_change_index, target_snapshot, source_has_lifelink);
            link_damage_prevention_record_range_to_damage(game, prevention.first_record_index, prevention.record_count, damage_record_index);
            record_event_with_links(game,
                                    "damage_player",
                                    source + " dealt " + std::to_string(remaining_damage) + " damage to " + player(game, target_snapshot.player).name,
                                    EventRecordLinks{
                                        .kind = EventRecordKind::Damage,
                                        .object = source_id,
                                        .player = source_controller,
                                        .target = target_snapshot,
                                        .damage_record_index = damage_record_index
                                    });
            return;
        }
        case TargetKind::Object: {
            if (!valid_object_index(game, target_snapshot.object)) {
                throw std::logic_error("damage target object is invalid");
            }
            u32 counters_removed = 0;
            const u32 counter_change_records_before_damage_results = static_cast<u32>(game.counter_change_records.size());
            if (object_is_battlefield_planeswalker(game, target_snapshot.object)) {
                auto& loyalty = object(game, target_snapshot.object).counters.loyalty;
                const auto before = loyalty;
                const auto removed = std::min(before, remaining_damage);
                loyalty -= removed;
                counters_removed += removed;
                const std::string detail = source + " dealt " + std::to_string(remaining_damage) + " damage to " + object_label(game, target_snapshot.object) + "; removed " + std::to_string(removed) + " loyalty counter(s)";
                if (removed != 0U) {
                    record_object_counter_change(game,
                                                 target_snapshot.object,
                                                 CounterKind::Loyalty,
                                                 CounterChangeKind::ObjectRemoved,
                                                 removed,
                                                 before,
                                                 loyalty,
                                                 "damage_planeswalker",
                                                 detail,
                                                 source_id,
                                                 true);
                } else {
                    record_event(game, "damage_planeswalker", detail);
                }
            }
            if (object_is_battlefield_battle(game, target_snapshot.object)) {
                auto& defense = object(game, target_snapshot.object).counters.defense;
                const auto before = defense;
                const auto removed = std::min(before, remaining_damage);
                defense -= removed;
                counters_removed += removed;
                const std::string detail = source + " dealt " + std::to_string(remaining_damage) + " damage to " + object_label(game, target_snapshot.object) + "; removed " + std::to_string(removed) + " defense counter(s)";
                if (removed != 0U) {
                    record_object_counter_change(game,
                                                 target_snapshot.object,
                                                 CounterKind::Defense,
                                                 CounterChangeKind::ObjectRemoved,
                                                 removed,
                                                 before,
                                                 defense,
                                                 "damage_battle",
                                                 detail,
                                                 source_id,
                                                 true);
                } else {
                    record_event(game, "damage_battle", detail);
                }
            }
            if (object_is_battlefield_creature(game, target_snapshot.object)) {
                mark_damage(game, target_snapshot.object, remaining_damage);
                if (source_has_deathtouch) {
                    object(game, target_snapshot.object).deathtouch_damage_marked = true;
                    record_event(game, "deathtouch_damage", source + " marked deathtouch damage on " + object_label(game, target_snapshot.object));
                }
            }
            const u32 damage_counter_change_record_count = game.counter_change_records.size() > counter_change_records_before_damage_results
                ? static_cast<u32>(game.counter_change_records.size() - counter_change_records_before_damage_results)
                : 0U;
            const u32 first_damage_counter_change_record_index = damage_counter_change_record_count != 0U
                ? counter_change_records_before_damage_results + 1U
                : 0U;
            const u32 life_change_records_before_damage_results = static_cast<u32>(game.life_change_records.size());
            if (source_has_lifelink && valid_player_index(game, source_controller)) {
                gain_life(game, source_controller, static_cast<std::int32_t>(remaining_damage));
                record_event(game, "lifelink_gain", source + " caused " + player(game, source_controller).name + " to gain " + std::to_string(remaining_damage));
            }
            const u32 damage_life_change_record_count = game.life_change_records.size() > life_change_records_before_damage_results
                ? static_cast<u32>(game.life_change_records.size() - life_change_records_before_damage_results)
                : 0U;
            const u32 first_damage_life_change_record_index = damage_life_change_record_count != 0U
                ? life_change_records_before_damage_results + 1U
                : 0U;
            const u32 damage_record_index = append_damage_record(game.next_event_sequence, prevention.prevented, remaining_damage, 0U, false, false, counters_removed, first_damage_counter_change_record_index, damage_counter_change_record_count, first_damage_life_change_record_index, damage_life_change_record_count, prevention.first_record_index, prevention.record_count);
            link_life_change_record_range_to_damage(game, first_damage_life_change_record_index, damage_life_change_record_count, damage_record_index, source_id, source_zone_change_index, target_snapshot, source_has_lifelink);
            link_damage_prevention_record_range_to_damage(game, prevention.first_record_index, prevention.record_count, damage_record_index);
            record_event_with_links(game,
                                    "damage_object",
                                    source + " dealt " + std::to_string(remaining_damage) + " damage to " + object_label(game, target_snapshot.object),
                                    EventRecordLinks{
                                        .kind = EventRecordKind::Damage,
                                        .object = source_id,
                                        .player = source_controller,
                                        .target = target_snapshot,
                                        .damage_record_index = damage_record_index
                                    });
            return;
        }
        case TargetKind::None:
            throw std::logic_error("damage target is missing");
    }
}

void deal_damage_to_target(GameState& game, ObjectId source_id, TargetRef target, std::uint32_t amount) {
    deal_damage_to_target_impl(game, source_id, target, amount, false);
}

void deal_unpreventable_damage_to_target(GameState& game, ObjectId source_id, TargetRef target, std::uint32_t amount) {
    deal_damage_to_target_impl(game, source_id, target, amount, true);
}


std::size_t pending_trigger_count(const GameState& game) noexcept {
    return game.pending_triggers.size();
}

void ensure_pending_trigger_record(GameState& game, PendingTrigger& trigger) {
    if (trigger.trigger_record_index != 0U && trigger.trigger_record_index <= game.trigger_records.size()) {
        return;
    }
    const u32 trigger_record_index = static_cast<u32>(game.trigger_records.size() + 1U);
    const u64 queued_sequence = game.next_event_sequence;
    game.trigger_records.push_back(TriggerRecord{
        .sequence = queued_sequence,
        .event = trigger.event,
        .subject = trigger.subject,
        .subject_zone_change_index = trigger.subject_zone_change_index,
        .controller = trigger.controller,
        .source = trigger.source,
        .source_name = trigger.source_name,
        .source_color_mask = legal_color_mask(trigger.source_color_mask),
        .source_ability_mask = trigger.source_ability_mask,
        .source_zone_change_index = trigger.source_zone_change_index,
        .effect_kind = trigger.effect_kind,
        .effect_amount = trigger.effect_amount,
        .effect_counter_kind = trigger.effect_counter_kind,
        .target_mask = trigger.target_mask,
        .target_count = trigger.target_count,
        .created_token_definition_index = trigger.created_token_definition_index,
        .caused_by_event_sequence = trigger.caused_by_event_sequence
    });
    trigger.trigger_record_index = trigger_record_index;
    record_event_with_links(game,
                            game.journal_trimmed ? "trigger_queued_reconstructed" : "trigger_queued_unlinked",
                            trigger.source_name + " pending trigger anchor rebuilt for branch journal",
                            EventRecordLinks{
                                .kind = EventRecordKind::TriggerQueued,
                                .object = trigger.subject,
                                .player = trigger.controller,
                                .trigger_record_index = trigger_record_index
                            });
}

bool put_pending_triggers_on_stack(GameState& game, const std::vector<u32>& trigger_order) {
    if (game.pending_triggers.empty()) {
        return trigger_order.empty();
    }
    if (!valid_pending_trigger_order(game, trigger_order)) {
        return false;
    }

    std::vector<PendingTrigger> pending;
    if (trigger_order.empty()) {
        pending = default_ordered_pending_triggers(game);
    } else {
        pending.reserve(trigger_order.size());
        for (const u32 key : trigger_order) {
            const auto it = std::find_if(game.pending_triggers.begin(), game.pending_triggers.end(), [key](const PendingTrigger& trigger) {
                return trigger.trigger_record_index == key;
            });
            if (it == game.pending_triggers.end()) {
                return false;
            }
            pending.push_back(*it);
        }
    }
    game.pending_triggers.clear();

    u32 stack_order = 1U;
    for (auto trigger : pending) {
        ensure_pending_trigger_record(game, trigger);
        auto* record = (trigger.trigger_record_index != 0U && trigger.trigger_record_index <= game.trigger_records.size())
            ? &game.trigger_records[trigger.trigger_record_index - 1U]
            : nullptr;
        if (!valid_player_index(game, trigger.controller) || player(game, trigger.controller).lost) {
            if (record != nullptr) {
                record->dropped = true;
                record->dropped_sequence = game.next_event_sequence;
                record->stack_order = stack_order;
            }
            record_event_with_links(game,
                                    "trigger_dropped",
                                    trigger.source_name + " has invalid/lost controller",
                                    EventRecordLinks{
                                        .kind = EventRecordKind::TriggerDropped,
                                        .object = trigger.source,
                                        .player = trigger.controller,
                                        .trigger_record_index = trigger.trigger_record_index
                                    });
            ++stack_order;
            continue;
        }
        const auto target_choice = choose_default_trigger_targets(game, trigger);
        if (record != nullptr) {
            seal_trigger_target_choice(*record, target_choice);
        }
        if (!target_choice.legal) {
            if (record != nullptr) {
                record->dropped = true;
                record->dropped_sequence = game.next_event_sequence;
                record->stack_order = stack_order;
            }
            record_event_with_links(game,
                                    "trigger_dropped_no_legal_choices",
                                    trigger.source_name + " could not be put on the stack because no legal choices were available",
                                    EventRecordLinks{
                                        .kind = EventRecordKind::TriggerDropped,
                                        .object = trigger.source,
                                        .player = trigger.controller,
                                        .trigger_record_index = trigger.trigger_record_index
                                    });
            ++stack_order;
            continue;
        }
        const auto ability_id = create_triggered_ability_stack_object(game, trigger, target_choice.targets);
        if (record != nullptr) {
            record->stack_object = ability_id;
            record->put_on_stack_sequence = game.next_event_sequence == 0U ? 0U : game.next_event_sequence - 1U;
            record->stack_order = stack_order;
        }
        ++stack_order;
    }
    game.consecutive_priority_passes = 0;
    game.priority_player = game.active_player;
    return true;
}

void put_pending_triggers_on_stack(GameState& game) {
    (void)put_pending_triggers_on_stack(game, {});
}



std::vector<ObjectId> current_blockers_for_attacker(const GameState& game, ObjectId attacker_id) {
    std::vector<ObjectId> blockers;
    if (!valid_object_index(game, attacker_id)) {
        return blockers;
    }
    const PlayerId defender = object(game, attacker_id).defending_player;
    if (!valid_player_index(game, defender)) {
        return blockers;
    }
    for (const auto id : zone(game, defender, Zone::Battlefield)) {
        if (valid_object_index(game, id) && object(game, id).blocking == attacker_id &&
            object_is_creature(game, object(game, id))) {
            blockers.push_back(id);
        }
    }
    std::sort(blockers.begin(), blockers.end(), [](ObjectId a, ObjectId b) { return a.value < b.value; });
    return blockers;
}

[[nodiscard]] bool same_object_id_set(std::vector<ObjectId> a, std::vector<ObjectId> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }
    std::sort(a.begin(), a.end(), [](ObjectId left, ObjectId right) { return left.value < right.value; });
    std::sort(b.begin(), b.end(), [](ObjectId left, ObjectId right) { return left.value < right.value; });
    for (std::size_t i = 1U; i < a.size(); ++i) {
        if (a[i - 1U] == a[i] || b[i - 1U] == b[i]) {
            return false;
        }
    }
    return a == b;
}

[[nodiscard]] std::vector<ObjectId> ordered_blockers_for_combat_damage(const GameState& game, ObjectId attacker_id) {
    std::vector<ObjectId> current = current_blockers_for_attacker(game, attacker_id);
    if (!valid_object_index(game, attacker_id) || current.size() <= 1U) {
        return current;
    }

    std::vector<ObjectId> ordered;
    ordered.reserve(current.size());
    for (const auto blocker_id : object(game, attacker_id).combat_damage_ordered_blockers) {
        if (std::find(current.begin(), current.end(), blocker_id) != current.end() &&
            std::find(ordered.begin(), ordered.end(), blocker_id) == ordered.end()) {
            ordered.push_back(blocker_id);
        }
    }
    for (const auto blocker_id : current) {
        if (std::find(ordered.begin(), ordered.end(), blocker_id) == ordered.end()) {
            ordered.push_back(blocker_id);
        }
    }
    return ordered;
}


u32 blocker_count_for_attacker(const GameState& game, ObjectId attacker_id) noexcept {
    u32 count = 0;
    if (!valid_object_index(game, attacker_id)) {
        return count;
    }
    for (const auto& p : game.players) {
        for (const auto id : p.zones[zone_index(Zone::Battlefield)]) {
            if (valid_object_index(game, id) && object(game, id).blocking == attacker_id) {
                ++count;
            }
        }
    }
    return count;
}

void record_combat_declaration(GameState& game,
                               CombatDeclarationKind declaration_kind,
                               std::string log_kind,
                               std::string detail,
                               PlayerId controller,
                               ObjectId actor_id,
                               TargetRef target,
                               PlayerId defending_player,
                               bool tapped_before,
                               bool tapped_after,
                               u32 blocker_batch_size,
                               u32 final_blocker_count_for_attacker) {
    const TargetRef target_snapshot = damage_target_snapshot(game, target);
    CombatDeclarationRecord record{};
    record.sequence = game.next_event_sequence;
    record.kind = declaration_kind;
    record.controller = controller;
    record.actor = actor_id;
    record.target = target_snapshot;
    record.target_zone_change_index = target_snapshot.kind == TargetKind::Object ? target_snapshot.object_zone_change_index : 0U;
    record.defending_player = defending_player;
    record.tapped_before = tapped_before;
    record.tapped_after = tapped_after;
    if (valid_object_index(game, actor_id)) {
        const auto& actor = object(game, actor_id);
        record.actor_zone_change_index = actor.zone_change_index;
    }

    switch (declaration_kind) {
        case CombatDeclarationKind::Attacker:
            record.attacker = actor_id;
            record.attacker_zone_change_index = record.actor_zone_change_index;
            record.target_is_player = target_snapshot.kind == TargetKind::Player;
            if (target_snapshot.kind == TargetKind::Object) {
                record.attacked_object = target_snapshot.object;
                record.target_is_planeswalker = object_is_battlefield_planeswalker(game, target_snapshot.object);
                record.target_is_battle = object_is_battlefield_battle(game, target_snapshot.object);
            }
            if (valid_object_index(game, actor_id)) {
                record.vigilance = object_has_ability(game, actor_id, AbilityVigilance);
                record.attacker_had_flying = object_has_ability(game, actor_id, AbilityFlying);
                record.attacker_had_menace = object_has_ability(game, actor_id, AbilityMenace);
                record.attacker_marked_blocked_after = object(game, actor_id).blocked;
            }
            break;
        case CombatDeclarationKind::Blocker:
            record.blocker = actor_id;
            record.blocker_zone_change_index = record.actor_zone_change_index;
            record.attacker = target_snapshot.kind == TargetKind::Object ? target_snapshot.object : ObjectId{};
            record.attacker_zone_change_index = target_snapshot.kind == TargetKind::Object ? target_snapshot.object_zone_change_index : 0U;
            record.blocker_batch_size = blocker_batch_size;
            record.final_blocker_count_for_attacker = final_blocker_count_for_attacker;
            if (valid_object_index(game, record.attacker)) {
                record.defending_player = object(game, record.attacker).defending_player;
                record.attacker_had_flying = object_has_ability(game, record.attacker, AbilityFlying);
                record.attacker_had_menace = object_has_ability(game, record.attacker, AbilityMenace);
                record.menace_satisfied = !record.attacker_had_menace || final_blocker_count_for_attacker >= 2U;
                record.attacker_marked_blocked_after = object(game, record.attacker).blocked;
            }
            if (valid_object_index(game, actor_id)) {
                record.blocker_had_flying = object_has_ability(game, actor_id, AbilityFlying);
                record.blocker_had_reach = object_has_ability(game, actor_id, AbilityReach);
            }
            break;
        case CombatDeclarationKind::Count:
            break;
    }

    const u32 declaration_record_index = static_cast<u32>(game.combat_declaration_records.size() + 1U);
    game.combat_declaration_records.push_back(std::move(record));
    record_event_with_links(game,
                            std::move(log_kind),
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::CombatDeclaration,
                                .object = actor_id,
                                .player = controller,
                                .target = target_snapshot,
                                .combat_declaration_record_index = declaration_record_index
                            });
}

namespace {

[[nodiscard]] bool resolve_attack_defending_target(const GameState& game,
                                                   PlayerId attacker_controller,
                                                   TargetRef defending_target,
                                                   PlayerId& defending_player,
                                                   ObjectId& attacked_object) noexcept {
    defending_player = PlayerId{};
    attacked_object = ObjectId{};
    if (defending_target.kind == TargetKind::Player) {
        if (!valid_player_index(game, defending_target.player) || attacker_controller == defending_target.player || player(game, defending_target.player).lost) {
            return false;
        }
        defending_player = defending_target.player;
        return true;
    }
    if (defending_target.kind != TargetKind::Object) {
        return false;
    }
    if (object_is_battlefield_planeswalker(game, defending_target.object)) {
        const auto& defender = object(game, defending_target.object);
        if (!valid_player_index(game, defender.controller) || attacker_controller == defender.controller || player(game, defender.controller).lost) {
            return false;
        }
        defending_player = defender.controller;
        attacked_object = defending_target.object;
        return true;
    }
    if (object_is_battlefield_battle(game, defending_target.object)) {
        const auto& battle = object(game, defending_target.object);
        defending_player = battle.battle_protector;
        if (!valid_player_index(game, defending_player) || attacker_controller == defending_player || player(game, defending_player).lost) {
            return false;
        }
        attacked_object = defending_target.object;
        return true;
    }
    return false;
}

[[nodiscard]] bool blocker_declaration_completed_for_player(const GameState& game, PlayerId player_id) noexcept {
    return std::find(game.blocker_declaration_complete_players.begin(), game.blocker_declaration_complete_players.end(), player_id) !=
           game.blocker_declaration_complete_players.end();
}

[[nodiscard]] bool player_has_attackers_to_block(const GameState& game, PlayerId blocker_controller) noexcept {
    if (!valid_player_index(game, blocker_controller) || player(game, blocker_controller).lost) {
        return false;
    }
    for (const auto& attacker_owner : game.players) {
        for (const auto attacker_id : attacker_owner.zones[zone_index(Zone::Battlefield)]) {
            if (object_is_battlefield_creature(game, attacker_id) && object(game, attacker_id).attacking &&
                object(game, attacker_id).defending_player == blocker_controller) {
                return true;
            }
        }
    }
    return false;
}

[[nodiscard]] bool all_blocker_declarations_complete(const GameState& game) noexcept {
    if (game.step != Step::DeclareBlockers || !game.stack.empty()) {
        return false;
    }
    for (const auto& candidate : game.players) {
        if (!candidate.lost && player_has_attackers_to_block(game, candidate.id) &&
            !blocker_declaration_completed_for_player(game, candidate.id)) {
            return false;
        }
    }
    return true;
}

} // namespace

bool can_declare_attacker_to_target(const GameState& game, PlayerId attacker_controller, ObjectId attacker_id, TargetRef defending_target) noexcept {
    if (game.step != Step::DeclareAttackers || game.active_player != attacker_controller || game.stack.size() != 0U ||
        game.attackers_declared_this_step) {
        return false;
    }
    if (!valid_player_index(game, attacker_controller) || player(game, attacker_controller).lost) {
        return false;
    }

    PlayerId defending_player{};
    ObjectId attacked_object{};
    if (!resolve_attack_defending_target(game, attacker_controller, defending_target, defending_player, attacked_object)) {
        return false;
    }

    if (!object_is_battlefield_creature(game, attacker_id)) {
        return false;
    }
    const auto& obj = object(game, attacker_id);
    if (obj.controller != attacker_controller || obj.tapped || obj.attacking || obj.blocking.valid()) {
        return false;
    }
    if (object_has_ability(game, attacker_id, AbilityDefender)) {
        return false;
    }
    if (object_has_summoning_sickness(game, attacker_id)) {
        return false;
    }
    (void)defending_player;
    (void)attacked_object;
    return true;
}

bool can_declare_attacker(const GameState& game, PlayerId attacker_controller, ObjectId attacker_id, PlayerId defending_player) noexcept {
    return can_declare_attacker_to_target(game, attacker_controller, attacker_id, TargetRef{.kind = TargetKind::Player, .player = defending_player});
}

namespace {

constexpr u32 kNoCombatDeclarationLimit = ~u32{0};

[[nodiscard]] u32 active_attack_declaration_limit(const GameState& game) noexcept {
    u32 limit = kNoCombatDeclarationLimit;
    for (const auto& obj : game.objects) {
        if (obj.zone != Zone::Battlefield || obj.ceased_to_exist) {
            continue;
        }
        const auto* def = current_definition_for_object(game, obj);
        if (def != nullptr && def->max_attackers_each_combat != 0U) {
            limit = std::min(limit, def->max_attackers_each_combat);
        }
    }
    return limit;
}

[[nodiscard]] u32 active_block_declaration_limit(const GameState& game) noexcept {
    u32 limit = kNoCombatDeclarationLimit;
    for (const auto& obj : game.objects) {
        if (obj.zone != Zone::Battlefield || obj.ceased_to_exist) {
            continue;
        }
        const auto* def = current_definition_for_object(game, obj);
        if (def != nullptr && def->max_blockers_each_combat != 0U) {
            limit = std::min(limit, def->max_blockers_each_combat);
        }
    }
    return limit;
}

[[nodiscard]] u32 current_attacking_creature_count(const GameState& game) noexcept {
    u32 count = 0;
    for (const auto& obj : game.objects) {
        if (obj.zone == Zone::Battlefield && obj.attacking) {
            ++count;
        }
    }
    return count;
}

[[nodiscard]] u32 current_blocking_creature_count(const GameState& game) noexcept {
    u32 count = 0;
    for (const auto& obj : game.objects) {
        if (obj.zone == Zone::Battlefield && obj.blocking.valid()) {
            ++count;
        }
    }
    return count;
}

[[nodiscard]] bool object_attacks_each_combat_if_able(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def != nullptr && def->attacks_each_combat_if_able;
}

[[nodiscard]] bool object_cant_attack_alone(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def != nullptr && def->cant_attack_alone;
}

void add_mana_cost_to_total(ManaCost& total, const ManaCost& cost) noexcept {
    total.generic += cost.generic;
    total.white += cost.white;
    total.blue += cost.blue;
    total.black += cost.black;
    total.red += cost.red;
    total.green += cost.green;
    total.colorless += cost.colorless;
}

[[nodiscard]] ManaCost object_attack_cost(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return ManaCost{};
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def == nullptr ? ManaCost{} : def->attack_cost;
}

[[nodiscard]] ManaCost attack_declaration_cost(const GameState& game,
                                               const std::vector<AttackAssignment>& assignments) noexcept {
    ManaCost total{};
    for (const auto assignment : assignments) {
        add_mana_cost_to_total(total, object_attack_cost(game, assignment.attacker));
    }
    return total;
}

[[nodiscard]] std::vector<ObjectId> attack_declaration_locked_tap_sources(const GameState& game,
                                                                          const std::vector<AttackAssignment>& assignments) {
    std::vector<ObjectId> locked;
    locked.reserve(assignments.size());
    for (const auto assignment : assignments) {
        if (valid_object_index(game, assignment.attacker) &&
            !object_has_ability(game, assignment.attacker, AbilityVigilance)) {
            locked.push_back(assignment.attacker);
        }
    }
    return locked;
}

[[nodiscard]] bool combat_attack_cost_payable(const GameState& game,
                                              PlayerId payer,
                                              const std::vector<AttackAssignment>& assignments) noexcept {
    const ManaCost cost = attack_declaration_cost(game, assignments);
    const auto locked_tap_sources = attack_declaration_locked_tap_sources(game, assignments);
    return cost.free() || can_pay_mana_cost_with_available_mana_excluding_tap_sources(game, payer, cost, locked_tap_sources);
}

bool pay_combat_declaration_mana_cost(GameState& game,
                                      PlayerId payer,
                                      const ManaCost& cost,
                                      std::string_view event_kind,
                                      std::string_view label);

bool pay_combat_declaration_mana_cost_excluding_tap_sources(GameState& game,
                                                            PlayerId payer,
                                                            const ManaCost& cost,
                                                            std::string_view event_kind,
                                                            std::string_view label,
                                                            const std::vector<ObjectId>& locked_tap_sources);

[[nodiscard]] bool attacker_has_any_legal_defending_target(const GameState& game, PlayerId attacker_controller, ObjectId attacker_id) noexcept {
    for (const auto& defender : game.players) {
        if (can_declare_attacker_to_target(game, attacker_controller, attacker_id, TargetRef{.kind = TargetKind::Player, .player = defender.id})) {
            return true;
        }
    }
    for (const auto& defender : game.players) {
        for (const auto target_id : defender.zones[zone_index(Zone::Battlefield)]) {
            if (!object_is_battlefield_combat_target(game, target_id)) {
                continue;
            }
            if (can_declare_attacker_to_target(game, attacker_controller, attacker_id, TargetRef{.kind = TargetKind::Object, .object = target_id})) {
                return true;
            }
        }
    }
    return false;
}

[[nodiscard]] bool attack_declaration_restrictions_satisfied(const GameState& game,
                                                             const std::vector<AttackAssignment>& assignments) noexcept {
    const u32 limit = active_attack_declaration_limit(game);
    if (limit == kNoCombatDeclarationLimit) {
        return true;
    }
    const u32 already_attacking = current_attacking_creature_count(game);
    if (already_attacking > limit) {
        return false;
    }
    return assignments.size() <= static_cast<std::size_t>(limit - already_attacking);
}

[[nodiscard]] bool attack_declaration_basic_constraints_satisfied(const GameState& game,
                                                                  PlayerId attacker_controller,
                                                                  const std::vector<AttackAssignment>& assignments,
                                                                  bool require_payable_combat_costs = true) noexcept {
    if (!attack_declaration_restrictions_satisfied(game, assignments)) {
        return false;
    }

    std::vector<ObjectId> assigned_attackers;
    assigned_attackers.reserve(assignments.size());
    for (const auto assignment : assignments) {
        if (std::find(assigned_attackers.begin(), assigned_attackers.end(), assignment.attacker) != assigned_attackers.end()) {
            return false;
        }
        if (!can_declare_attacker_to_target(game, attacker_controller, assignment.attacker, assignment.target)) {
            return false;
        }
        assigned_attackers.push_back(assignment.attacker);
    }

    const u32 final_attacker_count = current_attacking_creature_count(game) + static_cast<u32>(assignments.size());
    if (final_attacker_count < 2U) {
        for (const auto attacker_id : assigned_attackers) {
            if (object_cant_attack_alone(game, attacker_id)) {
                return false;
            }
        }
    }
    if (require_payable_combat_costs && !combat_attack_cost_payable(game, attacker_controller, assignments)) {
        return false;
    }
    return true;
}

[[nodiscard]] u32 satisfied_attack_requirement_count(const GameState& game,
                                                     PlayerId attacker_controller,
                                                     const std::vector<ObjectId>& assigned_attackers) noexcept {
    if (!valid_player_index(game, attacker_controller)) {
        return 0;
    }
    u32 count = 0;
    for (const auto attacker_id : assigned_attackers) {
        if (object_attacks_each_combat_if_able(game, attacker_id) && object_attack_cost(game, attacker_id).free() &&
            attacker_has_any_legal_defending_target(game, attacker_controller, attacker_id)) {
            ++count;
        }
    }
    return count;
}

[[nodiscard]] u32 maximum_satisfied_attack_requirements(const GameState& game, PlayerId attacker_controller) noexcept {
    if (!valid_player_index(game, attacker_controller)) {
        return 0;
    }

    const bool has_live_requirement = std::any_of(
        player(game, attacker_controller).zones[zone_index(Zone::Battlefield)].begin(),
        player(game, attacker_controller).zones[zone_index(Zone::Battlefield)].end(),
        [&](ObjectId attacker_id) {
            return object_attacks_each_combat_if_able(game, attacker_id) &&
                   object_attack_cost(game, attacker_id).free() &&
                   attacker_has_any_legal_defending_target(game, attacker_controller, attacker_id);
        });
    if (!has_live_requirement) {
        return 0;
    }

    std::vector<std::vector<AttackAssignment>> choices_by_attacker;
    for (const auto attacker_id : player(game, attacker_controller).zones[zone_index(Zone::Battlefield)]) {
        if (!object_attack_cost(game, attacker_id).free()) {
            continue;
        }
        std::vector<AttackAssignment> choices;
        for (const auto& defender : game.players) {
            const TargetRef defender_target{.kind = TargetKind::Player, .player = defender.id};
            if (can_declare_attacker_to_target(game, attacker_controller, attacker_id, defender_target)) {
                choices.push_back(AttackAssignment{.attacker = attacker_id, .target = defender_target});
            }
        }
        for (const auto& defender : game.players) {
            for (const auto target_id : defender.zones[zone_index(Zone::Battlefield)]) {
                if (!object_is_battlefield_combat_target(game, target_id)) {
                    continue;
                }
                const TargetRef object_target{.kind = TargetKind::Object, .object = target_id};
                if (can_declare_attacker_to_target(game, attacker_controller, attacker_id, object_target)) {
                    choices.push_back(AttackAssignment{.attacker = attacker_id, .target = object_target});
                }
            }
        }
        if (!choices.empty()) {
            choices_by_attacker.push_back(std::move(choices));
        }
    }

    u32 best = 0;
    std::vector<AttackAssignment> current_assignments;
    std::vector<ObjectId> current_attackers;
    auto search = [&](auto&& self, std::size_t index) -> void {
        if (index == choices_by_attacker.size()) {
            if (attack_declaration_basic_constraints_satisfied(game, attacker_controller, current_assignments, false)) {
                best = std::max(best, satisfied_attack_requirement_count(game, attacker_controller, current_attackers));
            }
            return;
        }

        self(self, index + 1U);
        for (const auto assignment : choices_by_attacker[index]) {
            current_assignments.push_back(assignment);
            current_attackers.push_back(assignment.attacker);
            if (attack_declaration_restrictions_satisfied(game, current_assignments)) {
                self(self, index + 1U);
            }
            current_attackers.pop_back();
            current_assignments.pop_back();
        }
    };
    search(search, 0U);
    return best;
}

[[nodiscard]] bool attack_requirements_satisfied_maximally(const GameState& game,
                                                           PlayerId attacker_controller,
                                                           const std::vector<ObjectId>& assigned_attackers,
                                                           u32 maximum_requirement_count) noexcept {
    return satisfied_attack_requirement_count(game, attacker_controller, assigned_attackers) >=
           maximum_requirement_count;
}

[[nodiscard]] bool can_declare_attackers_with_requirement_max(const GameState& game,
                                                              PlayerId attacker_controller,
                                                              const std::vector<AttackAssignment>& assignments,
                                                              u32 maximum_requirement_count) noexcept {
    if (game.step != Step::DeclareAttackers || game.active_player != attacker_controller || game.stack.size() != 0U ||
        game.attackers_declared_this_step) {
        return false;
    }
    if (!valid_player_index(game, attacker_controller) || player(game, attacker_controller).lost) {
        return false;
    }
    if (!attack_declaration_basic_constraints_satisfied(game, attacker_controller, assignments)) {
        return false;
    }
    std::vector<ObjectId> assigned_attackers;
    assigned_attackers.reserve(assignments.size());
    for (const auto assignment : assignments) {
        assigned_attackers.push_back(assignment.attacker);
    }
    return attack_requirements_satisfied_maximally(game, attacker_controller, assigned_attackers, maximum_requirement_count);
}

} // namespace

bool can_declare_attackers(const GameState& game, PlayerId attacker_controller, const std::vector<AttackAssignment>& assignments) noexcept {
    return can_declare_attackers_with_requirement_max(
        game,
        attacker_controller,
        assignments,
        maximum_satisfied_attack_requirements(game, attacker_controller));
}

bool declare_attackers(GameState& game, PlayerId attacker_controller, const std::vector<AttackAssignment>& assignments) {
    if (!can_declare_attackers(game, attacker_controller, assignments)) {
        record_event(game, "declare_attackers_failed", "controller#" + std::to_string(attacker_controller.value) + " assignments=" + std::to_string(assignments.size()));
        return false;
    }

    if (assignments.empty()) {
        game.attackers_declared_this_step = true;
        record_event(game, "declare_attackers_none", player(game, attacker_controller).name + " declared no attackers");
        return true;
    }

    struct AttackCommitSnapshot {
        PlayerId defending_player{};
        ObjectId attacked_object{};
        std::string target_description;
        bool tapped_before = false;
    };
    std::vector<AttackCommitSnapshot> snapshots;
    snapshots.reserve(assignments.size());
    for (const auto assignment : assignments) {
        AttackCommitSnapshot snapshot{};
        if (!resolve_attack_defending_target(game, attacker_controller, assignment.target, snapshot.defending_player, snapshot.attacked_object)) {
            record_event(game, "declare_attackers_failed", "controller#" + std::to_string(attacker_controller.value) + " assignments=" + std::to_string(assignments.size()));
            return false;
        }
        snapshot.target_description = assignment.target.kind == TargetKind::Player
            ? player(game, snapshot.defending_player).name
            : object_label(game, snapshot.attacked_object);
        snapshot.tapped_before = object(game, assignment.attacker).tapped;
        snapshots.push_back(std::move(snapshot));
    }

    const ManaCost locked_attack_cost = attack_declaration_cost(game, assignments);
    const auto locked_attack_tap_sources = attack_declaration_locked_tap_sources(game, assignments);
    if (!locked_attack_cost.free()) {
        GameState before_payment = game;
        if (!pay_combat_declaration_mana_cost_excluding_tap_sources(game,
                                                                     attacker_controller,
                                                                     locked_attack_cost,
                                                                     "pay_attack_cost",
                                                                     "attack cost",
                                                                     locked_attack_tap_sources)) {
            game = std::move(before_payment);
            record_event(game,
                         "declare_attackers_failed",
                         "controller#" + std::to_string(attacker_controller.value) + " could not pay attack cost " + mana_cost_summary(locked_attack_cost));
            return false;
        }
    }

    for (std::size_t i = 0; i < assignments.size(); ++i) {
        const auto assignment = assignments[i];
        const auto& snapshot = snapshots[i];
        auto& attacker = object(game, assignment.attacker);
        if (!object_has_ability(game, assignment.attacker, AbilityVigilance)) {
            attacker.tapped = true;
        }
        attacker.attacking = true;
        attacker.blocked = false;
        attacker.defending_player = snapshot.defending_player;
        attacker.attacked_object = snapshot.attacked_object;
        attacker.blocking = ObjectId{};
        record_combat_declaration(game,
                                  CombatDeclarationKind::Attacker,
                                  "declare_attacker",
                                  player(game, attacker_controller).name + " attacked " + snapshot.target_description + " with " + object_label(game, assignment.attacker),
                                  attacker_controller,
                                  assignment.attacker,
                                  assignment.target,
                                  snapshot.defending_player,
                                  snapshot.tapped_before,
                                  attacker.tapped,
                                  0U,
                                  0U);
    }
    game.attackers_declared_this_step = true;
    return true;
}

bool declare_attacker_to_target(GameState& game, PlayerId attacker_controller, ObjectId attacker_id, TargetRef defending_target) {
    return declare_attackers(game, attacker_controller, std::vector<AttackAssignment>{{.attacker = attacker_id, .target = defending_target}});
}

bool declare_attacker(GameState& game, PlayerId attacker_controller, ObjectId attacker_id, PlayerId defending_player) {
    return declare_attacker_to_target(game, attacker_controller, attacker_id, TargetRef{.kind = TargetKind::Player, .player = defending_player});
}

bool can_block_attacker_by_evasion(const GameState& game, ObjectId blocker_id, ObjectId attacker_id) noexcept {
    if (!object_is_battlefield_creature(game, blocker_id) || !object_is_battlefield_creature(game, attacker_id)) {
        return false;
    }
    if (object_has_ability(game, attacker_id, AbilityFlying) &&
        !object_has_ability(game, blocker_id, AbilityFlying) &&
        !object_has_ability(game, blocker_id, AbilityReach)) {
        return false;
    }
    if (target_has_protection_from_source(game, TargetRef{.kind = TargetKind::Object, .object = attacker_id}, blocker_id)) {
        return false;
    }
    return true;
}

namespace {

[[nodiscard]] bool object_can_block_only_flying(const GameState& game, ObjectId object_id) noexcept;

[[nodiscard]] bool block_assignment_basic_legal(const GameState& game, PlayerId blocker_controller, BlockAssignment assignment) noexcept {
    if (!object_is_battlefield_creature(game, assignment.blocker) || !object_is_battlefield_creature(game, assignment.attacker)) {
        return false;
    }
    if (!can_block_attacker_by_evasion(game, assignment.blocker, assignment.attacker)) {
        return false;
    }
    const auto& blocker = object(game, assignment.blocker);
    const auto& attacker = object(game, assignment.attacker);
    if (blocker.controller != blocker_controller || blocker.tapped || blocker.attacking || blocker.blocking.valid()) {
        return false;
    }
    if (!attacker.attacking || attacker.defending_player != blocker_controller) {
        return false;
    }
    if (object_can_block_only_flying(game, assignment.blocker) &&
        !object_has_ability(game, assignment.attacker, AbilityFlying)) {
        return false;
    }
    return true;
}

[[nodiscard]] bool object_blocks_each_combat_if_able(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def != nullptr && def->blocks_each_combat_if_able;
}

[[nodiscard]] bool object_must_be_blocked_if_able(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def != nullptr && def->must_be_blocked_if_able;
}

[[nodiscard]] bool object_requires_all_able_blockers(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def != nullptr && def->all_able_blockers_block_this_if_able;
}

[[nodiscard]] bool object_cant_block_alone(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def != nullptr && def->cant_block_alone;
}

[[nodiscard]] bool object_can_block_only_flying(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return false;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def != nullptr && def->can_block_only_flying;
}

[[nodiscard]] u32 object_max_blockers_to_block_this(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return 0U;
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def == nullptr ? 0U : def->max_blockers_to_block_this;
}

[[nodiscard]] ManaCost object_block_cost(const GameState& game, ObjectId object_id) noexcept {
    if (!valid_object_index(game, object_id)) {
        return ManaCost{};
    }
    const auto* def = current_definition_for_object(game, object(game, object_id));
    return def == nullptr ? ManaCost{} : def->block_cost;
}

[[nodiscard]] ManaCost block_declaration_cost(const GameState& game,
                                              const std::vector<BlockAssignment>& assignments) noexcept {
    ManaCost total{};
    for (const auto assignment : assignments) {
        add_mana_cost_to_total(total, object_block_cost(game, assignment.blocker));
    }
    return total;
}

[[nodiscard]] bool combat_block_cost_payable(const GameState& game,
                                             PlayerId payer,
                                             const std::vector<BlockAssignment>& assignments) noexcept {
    const ManaCost cost = block_declaration_cost(game, assignments);
    return cost.free() || can_pay_mana_cost_with_available_mana(game, payer, cost);
}

bool pay_combat_declaration_mana_cost_excluding_tap_sources(GameState& game,
                                                            PlayerId payer,
                                                            const ManaCost& cost,
                                                            std::string_view event_kind,
                                                            std::string_view label,
                                                            const std::vector<ObjectId>& locked_tap_sources) {
    if (cost.free()) {
        return true;
    }
    const PlayerId priority_before = game.priority_player;
    const u32 consecutive_passes_before = game.consecutive_priority_passes;
    if (!pay_mana_cost_with_mana_abilities_excluding_tap_sources(game, payer, cost, locked_tap_sources)) {
        return false;
    }
    game.priority_player = priority_before;
    game.consecutive_priority_passes = consecutive_passes_before;
    record_event(game,
                 std::string(event_kind),
                 player(game, payer).name + " paid " + std::string(label) + " " + mana_cost_summary(cost));
    return true;
}

bool pay_combat_declaration_mana_cost(GameState& game,
                                      PlayerId payer,
                                      const ManaCost& cost,
                                      std::string_view event_kind,
                                      std::string_view label) {
    return pay_combat_declaration_mana_cost_excluding_tap_sources(game, payer, cost, event_kind, label, {});
}

[[nodiscard]] bool block_declaration_restrictions_satisfied(const GameState& game,
                                                             const std::vector<BlockAssignment>& assignments) noexcept {
    const u32 limit = active_block_declaration_limit(game);
    if (limit == kNoCombatDeclarationLimit) {
        return true;
    }
    const u32 already_blocking = current_blocking_creature_count(game);
    if (already_blocking > limit) {
        return false;
    }
    return assignments.size() <= static_cast<std::size_t>(limit - already_blocking);
}

[[nodiscard]] bool block_declaration_basic_constraints_satisfied(const GameState& game,
                                                                 PlayerId blocker_controller,
                                                                 const std::vector<BlockAssignment>& assignments,
                                                                 bool require_payable_combat_costs = true) noexcept {
    if (!block_declaration_restrictions_satisfied(game, assignments)) {
        return false;
    }

    std::vector<ObjectId> assigned_blockers;
    assigned_blockers.reserve(assignments.size());
    std::vector<ObjectId> affected_attackers;
    affected_attackers.reserve(assignments.size());

    for (const auto assignment : assignments) {
        if (!block_assignment_basic_legal(game, blocker_controller, assignment)) {
            return false;
        }
        if (std::find(assigned_blockers.begin(), assigned_blockers.end(), assignment.blocker) != assigned_blockers.end()) {
            return false;
        }
        assigned_blockers.push_back(assignment.blocker);
        if (std::find(affected_attackers.begin(), affected_attackers.end(), assignment.attacker) == affected_attackers.end()) {
            affected_attackers.push_back(assignment.attacker);
        }
    }

    const u32 final_blocker_count_for_controller = current_blocking_creature_count(game) + static_cast<u32>(assignments.size());
    if (final_blocker_count_for_controller < 2U) {
        for (const auto blocker_id : assigned_blockers) {
            if (object_cant_block_alone(game, blocker_id)) {
                return false;
            }
        }
    }

    for (const auto attacker_id : affected_attackers) {
        u32 final_blocker_count = 0;
        for (const auto& p : game.players) {
            for (const auto id : p.zones[zone_index(Zone::Battlefield)]) {
                if (object(game, id).blocking == attacker_id) {
                    ++final_blocker_count;
                }
            }
        }
        for (const auto assignment : assignments) {
            if (assignment.attacker == attacker_id) {
                ++final_blocker_count;
            }
        }

        const u32 attacker_blocker_limit = object_max_blockers_to_block_this(game, attacker_id);
        if (attacker_blocker_limit != 0U && final_blocker_count > attacker_blocker_limit) {
            return false;
        }
        if (object_has_ability(game, attacker_id, AbilityMenace) && final_blocker_count < 2U) {
            return false;
        }
    }
    if (require_payable_combat_costs && !combat_block_cost_payable(game, blocker_controller, assignments)) {
        return false;
    }
    return true;
}

[[nodiscard]] u32 satisfied_block_requirement_count(const GameState& game,
                                                    PlayerId blocker_controller,
                                                    const std::vector<BlockAssignment>& assignments) noexcept {
    u32 count = 0;
    std::vector<ObjectId> assigned_blockers;
    assigned_blockers.reserve(assignments.size());
    for (const auto assignment : assignments) {
        if (std::find(assigned_blockers.begin(), assigned_blockers.end(), assignment.blocker) != assigned_blockers.end()) {
            continue;
        }
        assigned_blockers.push_back(assignment.blocker);
        const bool free_to_block_for_requirement = object_block_cost(game, assignment.blocker).free();
        if (free_to_block_for_requirement && object_blocks_each_combat_if_able(game, assignment.blocker)) {
            ++count;
        }
        if (free_to_block_for_requirement && object_requires_all_able_blockers(game, assignment.attacker)) {
            ++count;
        }
    }

    for (const auto& attacker_owner : game.players) {
        for (const auto attacker_id : attacker_owner.zones[zone_index(Zone::Battlefield)]) {
            if (!object_is_battlefield_creature(game, attacker_id)) {
                continue;
            }
            const auto& attacker = object(game, attacker_id);
            if (!attacker.attacking || attacker.defending_player != blocker_controller ||
                !object_must_be_blocked_if_able(game, attacker_id)) {
                continue;
            }
            const bool already_blocked = blocker_count_for_attacker(game, attacker_id) != 0U;
            const bool blocked_by_cost_free_current_assignment = std::any_of(assignments.begin(), assignments.end(), [&](const BlockAssignment assignment) {
                return assignment.attacker == attacker_id && object_block_cost(game, assignment.blocker).free();
            });
            if (already_blocked || blocked_by_cost_free_current_assignment) {
                ++count;
            }
        }
    }
    return count;
}

[[nodiscard]] u32 maximum_satisfied_block_requirements(const GameState& game, PlayerId blocker_controller) noexcept {
    if (!valid_player_index(game, blocker_controller)) {
        return 0;
    }

    bool has_live_requirement = false;
    for (const auto blocker_id : player(game, blocker_controller).zones[zone_index(Zone::Battlefield)]) {
        if (!object_block_cost(game, blocker_id).free()) {
            continue;
        }
        for (const auto& attacker_owner : game.players) {
            for (const auto attacker_id : attacker_owner.zones[zone_index(Zone::Battlefield)]) {
                const BlockAssignment assignment{.blocker = blocker_id, .attacker = attacker_id};
                if (!block_assignment_basic_legal(game, blocker_controller, assignment)) {
                    continue;
                }
                if (object_blocks_each_combat_if_able(game, blocker_id) ||
                    object_requires_all_able_blockers(game, attacker_id) ||
                    object_must_be_blocked_if_able(game, attacker_id)) {
                    has_live_requirement = true;
                    break;
                }
            }
            if (has_live_requirement) {
                break;
            }
        }
        if (has_live_requirement) {
            break;
        }
    }
    if (!has_live_requirement) {
        return 0;
    }

    std::vector<std::vector<BlockAssignment>> choices_by_blocker;
    for (const auto blocker_id : player(game, blocker_controller).zones[zone_index(Zone::Battlefield)]) {
        if (!object_block_cost(game, blocker_id).free()) {
            continue;
        }
        std::vector<BlockAssignment> choices;
        for (const auto& attacker_owner : game.players) {
            for (const auto attacker_id : attacker_owner.zones[zone_index(Zone::Battlefield)]) {
                const BlockAssignment assignment{.blocker = blocker_id, .attacker = attacker_id};
                if (block_assignment_basic_legal(game, blocker_controller, assignment)) {
                    choices.push_back(assignment);
                }
            }
        }
        if (!choices.empty()) {
            choices_by_blocker.push_back(std::move(choices));
        }
    }

    u32 best = 0;
    std::vector<BlockAssignment> current_assignments;
    auto search = [&](auto&& self, std::size_t index) -> void {
        if (index == choices_by_blocker.size()) {
            if (block_declaration_basic_constraints_satisfied(game, blocker_controller, current_assignments, false)) {
                best = std::max(best, satisfied_block_requirement_count(game, blocker_controller, current_assignments));
            }
            return;
        }

        self(self, index + 1U);
        for (const auto assignment : choices_by_blocker[index]) {
            current_assignments.push_back(assignment);
            if (block_declaration_restrictions_satisfied(game, current_assignments)) {
                self(self, index + 1U);
            }
            current_assignments.pop_back();
        }
    };
    search(search, 0U);
    return best;
}

[[nodiscard]] bool block_requirements_satisfied_maximally(const GameState& game,
                                                          PlayerId blocker_controller,
                                                          const std::vector<BlockAssignment>& assignments,
                                                          u32 maximum_requirement_count) noexcept {
    return satisfied_block_requirement_count(game, blocker_controller, assignments) >=
           maximum_requirement_count;
}

[[nodiscard]] bool can_declare_blockers_with_requirement_max(const GameState& game,
                                                             PlayerId blocker_controller,
                                                             const std::vector<BlockAssignment>& assignments,
                                                             u32 maximum_requirement_count) noexcept {
    if (game.step != Step::DeclareBlockers || game.stack.size() != 0U || blocker_declaration_completed_for_player(game, blocker_controller)) {
        return false;
    }
    if (!valid_player_index(game, blocker_controller) || player(game, blocker_controller).lost) {
        return false;
    }
    if (assignments.empty()) {
        return player_has_attackers_to_block(game, blocker_controller) &&
               block_declaration_basic_constraints_satisfied(game, blocker_controller, assignments) &&
               block_requirements_satisfied_maximally(game, blocker_controller, assignments, maximum_requirement_count);
    }

    if (!block_declaration_basic_constraints_satisfied(game, blocker_controller, assignments)) {
        return false;
    }

    return block_requirements_satisfied_maximally(game, blocker_controller, assignments, maximum_requirement_count);
}

} // namespace

bool can_declare_blockers(const GameState& game, PlayerId blocker_controller, const std::vector<BlockAssignment>& assignments) noexcept {
    return can_declare_blockers_with_requirement_max(
        game,
        blocker_controller,
        assignments,
        maximum_satisfied_block_requirements(game, blocker_controller));
}

bool can_declare_blocker(const GameState& game, PlayerId blocker_controller, ObjectId blocker_id, ObjectId attacker_id) noexcept {
    return can_declare_blockers(game, blocker_controller, std::vector<BlockAssignment>{{.blocker = blocker_id, .attacker = attacker_id}});
}

bool declare_blockers(GameState& game, PlayerId blocker_controller, const std::vector<BlockAssignment>& assignments) {
    if (!can_declare_blockers(game, blocker_controller, assignments)) {
        record_event(game, "declare_blockers_failed", "controller#" + std::to_string(blocker_controller.value) + " assignments=" + std::to_string(assignments.size()));
        return false;
    }

    if (assignments.empty()) {
        game.blocker_declaration_complete_players.push_back(blocker_controller);
        record_event(game, "declare_blockers_none", player(game, blocker_controller).name + " declared no blockers");
        return true;
    }

    std::vector<bool> tapped_before;
    tapped_before.reserve(assignments.size());
    for (const auto assignment : assignments) {
        tapped_before.push_back(object(game, assignment.blocker).tapped);
    }

    const ManaCost locked_block_cost = block_declaration_cost(game, assignments);
    if (!locked_block_cost.free()) {
        GameState before_payment = game;
        if (!pay_combat_declaration_mana_cost(game, blocker_controller, locked_block_cost, "pay_block_cost", "block cost")) {
            game = std::move(before_payment);
            record_event(game,
                         "declare_blockers_failed",
                         "controller#" + std::to_string(blocker_controller.value) + " could not pay block cost " + mana_cost_summary(locked_block_cost));
            return false;
        }
    }

    for (const auto assignment : assignments) {
        auto& blocker = object(game, assignment.blocker);
        blocker.blocking = assignment.attacker;
        blocker.attacking = false;
        blocker.blocked = false;
        blocker.defending_player = PlayerId{};
        object(game, assignment.attacker).blocked = true;
    }

    for (std::size_t i = 0; i < assignments.size(); ++i) {
        const auto assignment = assignments[i];
        const auto& blocker = object(game, assignment.blocker);
        record_combat_declaration(game,
                                  CombatDeclarationKind::Blocker,
                                  "declare_blocker",
                                  player(game, blocker_controller).name + " blocked " + object_label(game, assignment.attacker) + " with " + object_label(game, assignment.blocker),
                                  blocker_controller,
                                  assignment.blocker,
                                  TargetRef{.kind = TargetKind::Object, .object = assignment.attacker},
                                  object(game, assignment.attacker).defending_player,
                                  tapped_before[i],
                                  blocker.tapped,
                                  static_cast<u32>(assignments.size()),
                                  blocker_count_for_attacker(game, assignment.attacker));
    }
    game.blocker_declaration_complete_players.push_back(blocker_controller);
    return true;
}

bool declare_blocker(GameState& game, PlayerId blocker_controller, ObjectId blocker_id, ObjectId attacker_id) {
    if (!declare_blockers(game, blocker_controller, std::vector<BlockAssignment>{{.blocker = blocker_id, .attacker = attacker_id}})) {
        record_event(game, "declare_blocker_failed", "blocker#" + std::to_string(blocker_id.value) + " attacker#" + std::to_string(attacker_id.value));
        return false;
    }
    return true;
}

bool can_order_combat_damage(const GameState& game, PlayerId controller, ObjectId attacker_id, const std::vector<ObjectId>& blocker_order) {
    if (game.step != Step::DeclareBlockers || !game.stack.empty() || controller != game.active_player ||
        !valid_player_index(game, controller) || player(game, controller).lost ||
        !valid_object_index(game, attacker_id) || object(game, attacker_id).controller != controller ||
        !object_is_battlefield_creature(game, attacker_id) || !object(game, attacker_id).attacking ||
        !all_blocker_declarations_complete(game) || !object(game, attacker_id).combat_damage_ordered_blockers.empty()) {
        return false;
    }

    const auto blockers = current_blockers_for_attacker(game, attacker_id);
    if (blockers.size() < 2U) {
        return false;
    }
    return same_object_id_set(blocker_order, blockers);
}

bool order_combat_damage(GameState& game, PlayerId controller, ObjectId attacker_id, const std::vector<ObjectId>& blocker_order) {
    if (!can_order_combat_damage(game, controller, attacker_id, blocker_order)) {
        record_event(game, "order_combat_damage_failed", "controller#" + std::to_string(controller.value) +
            " attacker#" + std::to_string(attacker_id.value) + " blockers=" + std::to_string(blocker_order.size()));
        return false;
    }

    object(game, attacker_id).combat_damage_ordered_blockers = blocker_order;
    std::string detail = object_label(game, attacker_id) + " damage order";
    for (const auto blocker_id : blocker_order) {
        detail += " -> " + object_label(game, blocker_id);
    }
    record_event(game, "order_combat_damage", std::move(detail));
    return true;
}

void record_combat_damage_assignment(GameState& game,
                                     std::string log_kind,
                                     std::string detail,
                                     ObjectId source_id,
                                     TargetRef target,
                                     u32 assigned,
                                     u32 damage_record_index,
                                     bool first_strike_batch,
                                     bool split_combat_damage,
                                     bool source_was_attacker,
                                     bool source_was_blocker,
                                     bool attacker_was_blocked,
                                     u32 blocker_count,
                                     bool source_had_trample,
                                     bool excess_trample) {
    if (assigned == 0U) {
        return;
    }
    const TargetRef target_snapshot = damage_target_snapshot(game, target);
    PlayerId source_controller{};
    u64 source_zone_change_index = 0;
    if (valid_object_index(game, source_id)) {
        const auto& source_obj = object(game, source_id);
        source_controller = source_obj.controller;
        source_zone_change_index = source_obj.zone_change_index;
    }
    const u32 assignment_record_index = static_cast<u32>(game.combat_damage_assignment_records.size() + 1U);
    game.combat_damage_assignment_records.push_back(CombatDamageAssignmentRecord{
        .sequence = game.next_event_sequence,
        .source = source_id,
        .source_controller = source_controller,
        .source_zone_change_index = source_zone_change_index,
        .target = target_snapshot,
        .target_zone_change_index = target_snapshot.kind == TargetKind::Object ? target_snapshot.object_zone_change_index : 0U,
        .assigned = assigned,
        .damage_record_index = damage_record_index,
        .first_strike_batch = first_strike_batch,
        .split_combat_damage = split_combat_damage,
        .source_was_attacker = source_was_attacker,
        .source_was_blocker = source_was_blocker,
        .attacker_was_blocked = attacker_was_blocked,
        .blocker_count = blocker_count,
        .source_had_trample = source_had_trample,
        .excess_trample = excess_trample
    });
    record_event_with_links(game,
                            std::move(log_kind),
                            std::move(detail),
                            EventRecordLinks{
                                .kind = EventRecordKind::CombatDamageAssignment,
                                .object = source_id,
                                .player = source_controller,
                                .target = target_snapshot,
                                .combat_damage_assignment_record_index = assignment_record_index
                            });
}

void assign_combat_damage(GameState& game) {
    if (game.step != Step::CombatDamage || game.combat_damage_assigned_this_step) {
        return;
    }
    game.combat_damage_assigned_this_step = true;

    auto collect_attackers = [&game]() {
        std::vector<ObjectId> attackers;
        for (const auto& p : game.players) {
            for (const auto id : p.zones[zone_index(Zone::Battlefield)]) {
                const auto& obj = object(game, id);
                if (obj.attacking && object_is_creature(game, obj)) {
                    attackers.push_back(id);
                }
            }
        }
        std::sort(attackers.begin(), attackers.end(), [](ObjectId a, ObjectId b) { return a.value < b.value; });
        return attackers;
    };

    auto participates_in_batch = [&game](ObjectId source_id, bool first_strike_batch, bool split_combat_damage) {
        if (!split_combat_damage) {
            return true;
        }
        const bool first_strike = object_has_ability(game, source_id, AbilityFirstStrike);
        const bool double_strike = object_has_ability(game, source_id, AbilityDoubleStrike);
        return first_strike_batch ? (first_strike || double_strike) : (!first_strike || double_strike);
    };

    auto lethal_assignment = [&game](ObjectId source_id, ObjectId damaged_id) -> u32 {
        if (!object_is_battlefield_creature(game, damaged_id)) {
            return 0U;
        }
        const auto toughness = effective_toughness(game, damaged_id);
        if (toughness <= 0) {
            return 0U;
        }
        if (object_has_ability(game, source_id, AbilityDeathtouch)) {
            return object(game, damaged_id).damage_marked == 0U ? 1U : 0U;
        }
        const auto marked = object(game, damaged_id).damage_marked;
        const auto needed = static_cast<u32>(toughness);
        return marked >= needed ? 0U : needed - marked;
    };

    auto run_damage_batch = [&](bool first_strike_batch, bool split_combat_damage) {
        auto assign_and_record = [&](ObjectId source_id,
                                     TargetRef target,
                                     u32 assigned,
                                     std::string log_kind,
                                     std::string detail,
                                     bool source_was_attacker,
                                     bool source_was_blocker,
                                     bool attacker_was_blocked,
                                     u32 blocker_count,
                                     bool source_had_trample,
                                     bool excess_trample) {
            const u32 before_damage_records = static_cast<u32>(game.damage_records.size());
            deal_damage_to_target(game, source_id, target, assigned);
            const u32 damage_record_index = game.damage_records.size() > before_damage_records ? before_damage_records + 1U : 0U;
            record_combat_damage_assignment(game,
                                            std::move(log_kind),
                                            std::move(detail),
                                            source_id,
                                            target,
                                            assigned,
                                            damage_record_index,
                                            first_strike_batch,
                                            split_combat_damage,
                                            source_was_attacker,
                                            source_was_blocker,
                                            attacker_was_blocked,
                                            blocker_count,
                                            source_had_trample,
                                            excess_trample);
        };
        const auto attackers = collect_attackers();
        for (const auto attacker_id : attackers) {
            if (!object_is_battlefield_creature(game, attacker_id)) {
                continue;
            }
            const bool attacker_participates = participates_in_batch(attacker_id, first_strike_batch, split_combat_damage);
            const auto& attacker_before = object(game, attacker_id);
            const PlayerId defender = attacker_before.defending_player;
            if (!valid_player_index(game, defender) || player(game, defender).lost) {
                continue;
            }
            const TargetRef combat_damage_target = object_is_battlefield_combat_target(game, attacker_before.attacked_object)
                ? TargetRef{.kind = TargetKind::Object, .object = attacker_before.attacked_object}
                : TargetRef{.kind = TargetKind::Player, .player = defender};
            std::vector<ObjectId> blockers = ordered_blockers_for_combat_damage(game, attacker_id);
            auto attacker_power = attacker_participates ? std::max(0, effective_power(game, attacker_id)) : 0;
            const bool attacker_has_trample = object_has_ability(game, attacker_id, AbilityTrample);
            const bool attacker_is_blocked = attacker_before.blocked || !blockers.empty();
            if (!attacker_is_blocked) {
                if (attacker_power > 0) {
                    assign_and_record(attacker_id,
                                      combat_damage_target,
                                      static_cast<u32>(attacker_power),
                                      first_strike_batch ? "combat_damage_defender_first" : "combat_damage_defender",
                                      object_label(game, attacker_id) + " assigned " + std::to_string(attacker_power) + " combat damage to " + target_label(game, combat_damage_target),
                                      true,
                                      false,
                                      false,
                                      0U,
                                      attacker_has_trample,
                                      false);
                }
            } else if (attacker_power > 0) {
                u32 remaining = static_cast<u32>(attacker_power);
                if (!blockers.empty()) {
                    for (const auto blocker_id : blockers) {
                        if (remaining == 0U || !object_is_battlefield_creature(game, blocker_id)) {
                            continue;
                        }
                        const u32 assign = attacker_has_trample ? std::min(remaining, lethal_assignment(attacker_id, blocker_id)) : remaining;
                        if (assign != 0U) {
                            assign_and_record(attacker_id,
                                              TargetRef{.kind = TargetKind::Object, .object = blocker_id},
                                              assign,
                                              first_strike_batch ? "combat_damage_object_first" : "combat_damage_object",
                                              object_label(game, attacker_id) + " assigned " + std::to_string(assign) + " combat damage to " + object_label(game, blocker_id),
                                              true,
                                              false,
                                              attacker_is_blocked,
                                              static_cast<u32>(blockers.size()),
                                              attacker_has_trample,
                                              false);
                            remaining -= assign;
                        }
                        if (!attacker_has_trample) {
                            break;
                        }
                    }
                }
                if (attacker_has_trample && remaining > 0U) {
                    assign_and_record(attacker_id,
                                      combat_damage_target,
                                      remaining,
                                      first_strike_batch ? "combat_damage_trample_defender_first" : "combat_damage_trample_defender",
                                      object_label(game, attacker_id) + " assigned " + std::to_string(remaining) + " excess trample combat damage to " + target_label(game, combat_damage_target),
                                      true,
                                      false,
                                      attacker_is_blocked,
                                      static_cast<u32>(blockers.size()),
                                      attacker_has_trample,
                                      true);
                }
            }

            for (const auto blocker_id : blockers) {
                if (!object_is_battlefield_creature(game, blocker_id) || !object_is_battlefield_creature(game, attacker_id) || !participates_in_batch(blocker_id, first_strike_batch, split_combat_damage)) {
                    continue;
                }
                const auto blocker_power = std::max(0, effective_power(game, blocker_id));
                if (blocker_power > 0) {
                    assign_and_record(blocker_id,
                                      TargetRef{.kind = TargetKind::Object, .object = attacker_id},
                                      static_cast<u32>(blocker_power),
                                      first_strike_batch ? "combat_damage_object_first" : "combat_damage_object",
                                      object_label(game, blocker_id) + " assigned " + std::to_string(blocker_power) + " combat damage to " + object_label(game, attacker_id),
                                      false,
                                      true,
                                      true,
                                      static_cast<u32>(blockers.size()),
                                      false,
                                      false);
                }
            }
        }
    };

    bool split_combat_damage = false;
    for (const auto id : collect_attackers()) {
        if (object_has_ability(game, id, AbilityFirstStrike) || object_has_ability(game, id, AbilityDoubleStrike)) {
            split_combat_damage = true;
            break;
        }
        const auto defender = object(game, id).defending_player;
        if (valid_player_index(game, defender)) {
            for (const auto blocker_id : zone(game, defender, Zone::Battlefield)) {
                if (object(game, blocker_id).blocking == id &&
                    (object_has_ability(game, blocker_id, AbilityFirstStrike) || object_has_ability(game, blocker_id, AbilityDoubleStrike))) {
                    split_combat_damage = true;
                    break;
                }
            }
        }
        if (split_combat_damage) {
            break;
        }
    }

    if (split_combat_damage) {
        run_damage_batch(true, true);
        apply_state_based_actions(game);
        run_damage_batch(false, true);
    } else {
        run_damage_batch(false, false);
    }
    apply_state_based_actions(game);
}


void clear_combat_assignments(GameState& game) {
    u32 changed = 0;
    for (auto& obj : game.objects) {
        if (obj.attacking || obj.blocked || obj.defending_player.valid() || obj.attacked_object.valid() || obj.blocking.valid()) {
            obj.attacking = false;
            obj.blocked = false;
            obj.defending_player = PlayerId{};
            obj.attacked_object = ObjectId{};
            obj.blocking = ObjectId{};
            obj.combat_damage_ordered_blockers.clear();
            ++changed;
        }
    }
    game.attackers_declared_this_step = false;
    game.combat_damage_assigned_this_step = false;
    game.blocker_declaration_complete_players.clear();
    if (changed != 0U) {
        record_event(game, "clear_combat", "cleared " + std::to_string(changed) + " combat assignment(s)");
    }
}

void discard_down_to_max_hand_size(GameState& game, PlayerId player_id) {
    auto& p = player(game, player_id);
    while (p.zones[zone_index(Zone::Hand)].size() > p.max_hand_size) {
        const ObjectId discarded = p.zones[zone_index(Zone::Hand)].back();
        if (!discard_card_for_reason(game, player_id, discarded, DiscardRecordKind::CleanupHandSize)) {
            break;
        }
    }
}

void apply_state_based_actions(GameState& game) {
    struct PlayerLossCandidate {
        PlayerId player{};
        std::string detail;
    };

    const u32 check_index = game.state_based_action_records.empty()
        ? 1U
        : game.state_based_action_records.back().check_index + 1U;
    u32 pass_index = 0U;
    while (true) {
        ++pass_index;

        std::vector<PlayerLossCandidate> player_losses;
        std::vector<ObjectId> tokens_to_cease;
        std::vector<ObjectId> counter_pair_objects;
        std::vector<ObjectId> creatures_to_graveyard;
        std::vector<ObjectId> creatures_to_destroy;
        std::vector<ObjectId> planeswalkers_to_graveyard;
        std::vector<ObjectId> battles_to_graveyard;
        std::vector<ObjectId> illegal_equipment;
        std::vector<ObjectId> unattached_or_illegal_auras;

        for (const auto& p : game.players) {
            if (p.lost) {
                continue;
            }
            if (p.life <= 0) {
                player_losses.push_back(PlayerLossCandidate{.player = p.id, .detail = p.name + " has non-positive life"});
            } else if (p.poison >= 10) {
                player_losses.push_back(PlayerLossCandidate{.player = p.id, .detail = p.name + " has ten or more poison counters"});
            } else if (p.empty_library_draw_attempts > 0) {
                player_losses.push_back(PlayerLossCandidate{.player = p.id, .detail = p.name + " attempted to draw from an empty library"});
            }
        }

        for (const auto& obj : game.objects) {
            if (obj.token && !obj.ability_object && !obj.ceased_to_exist && obj.zone != Zone::Battlefield) {
                tokens_to_cease.push_back(obj.id);
            }
        }

        for (const auto& p : game.players) {
            for (const ObjectId id : p.zones[zone_index(Zone::Battlefield)]) {
                const auto& obj = object(game, id);
                if (std::min(obj.counters.plus_one_plus_one, obj.counters.minus_one_minus_one) != 0U) {
                    counter_pair_objects.push_back(id);
                }

                if (object_is_creature(game, obj)) {
                    const auto current_toughness = effective_toughness(game, id);
                    const bool zero_or_less_toughness = current_toughness <= 0;
                    const bool lethal_damage = current_toughness > 0 && obj.damage_marked >= static_cast<u32>(current_toughness);
                    const bool deathtouch_lethal_damage = current_toughness > 0 && obj.damage_marked > 0U && obj.deathtouch_damage_marked;
                    const bool damage_destroy_would_apply = lethal_damage || deathtouch_lethal_damage;
                    const bool survives_damage_destroy = damage_destroy_would_apply && object_has_ability(game, id, AbilityIndestructible);
                    if (zero_or_less_toughness) {
                        creatures_to_graveyard.push_back(id);
                    } else if (damage_destroy_would_apply && !survives_damage_destroy) {
                        creatures_to_destroy.push_back(id);
                    }
                }

                if (object_is_battlefield_planeswalker(game, id) && obj.counters.loyalty == 0U) {
                    planeswalkers_to_graveyard.push_back(id);
                }
                if (object_is_battlefield_battle(game, id) && obj.counters.defense == 0U) {
                    battles_to_graveyard.push_back(id);
                }

                const auto attachment_kind = attachment_kind_for_object(game, id);
                if (attachment_kind == AttachmentKind::Aura) {
                    if (!obj.attached_to.valid() || !can_attach_object(game, id, obj.attached_to)) {
                        unattached_or_illegal_auras.push_back(id);
                    }
                } else if ((attachment_kind == AttachmentKind::Equipment || attachment_kind == AttachmentKind::Fortification) && obj.attached_to.valid()) {
                    if (!can_attach_object(game, id, obj.attached_to)) {
                        illegal_equipment.push_back(id);
                    }
                }
            }
        }

        const u32 pass_candidate_count = static_cast<u32>(player_losses.size() +
                                                          tokens_to_cease.size() +
                                                          counter_pair_objects.size() +
                                                          creatures_to_graveyard.size() +
                                                          creatures_to_destroy.size() +
                                                          planeswalkers_to_graveyard.size() +
                                                          battles_to_graveyard.size() +
                                                          illegal_equipment.size() +
                                                          unattached_or_illegal_auras.size());
        if (pass_candidate_count == 0U) {
            break;
        }

        const auto pre_creature_sba_ltb_snapshots = (!creatures_to_graveyard.empty() || !creatures_to_destroy.empty())
            ? capture_battlefield_trigger_sources(game)
            : std::vector<TriggerSourceSnapshot>{};

        bool pass_changed = false;

        for (const auto& candidate : player_losses) {
            if (!valid_player_index(game, candidate.player)) {
                continue;
            }
            auto& p = player(game, candidate.player);
            if (p.lost) {
                continue;
            }
            p.lost = true;
            record_state_based_action(game,
                                      StateBasedActionKind::PlayerLost,
                                      ObjectId{},
                                      p.id,
                                      "sba_player_loses",
                                      candidate.detail,
                                      check_index,
                                      pass_index,
                                      pass_candidate_count);
            pass_changed = true;
        }

        for (const auto id : tokens_to_cease) {
            if (!valid_object_index(game, id)) {
                continue;
            }
            const auto& obj = object(game, id);
            if (!obj.token || obj.ability_object || obj.ceased_to_exist || obj.zone == Zone::Battlefield) {
                continue;
            }
            const u32 sba_record_index = record_state_based_action(game,
                                                                   StateBasedActionKind::TokenCease,
                                                                   id,
                                                                   obj.controller,
                                                                   "sba_token_cease",
                                                                   object_label(game, id) + " is a token outside the battlefield and will cease to exist",
                                                                   check_index,
                                                                   pass_index,
                                                                   pass_candidate_count);
            cease_token_object(game, id);
            if (sba_record_index != 0U && sba_record_index <= game.state_based_action_records.size()) {
                game.state_based_action_records[sba_record_index - 1U].token_ceased = object_ceased_to_exist(game, id);
            }
            pass_changed = true;
        }

        for (const auto id : counter_pair_objects) {
            if (valid_object_index(game, id) && object(game, id).zone == Zone::Battlefield && cancel_opposing_power_toughness_counters(game, id, check_index, pass_index, pass_candidate_count)) {
                pass_changed = true;
            }
        }

        for (const ObjectId id : creatures_to_graveyard) {
            if (!valid_object_index(game, id) || object(game, id).zone != Zone::Battlefield) {
                continue;
            }
            const auto first_zone_record = game.zone_change_records.size();
            const u32 sba_record_index = record_state_based_action(game,
                                                                   StateBasedActionKind::CreatureToughnessGraveyard,
                                                                   id,
                                                                   object(game, id).controller,
                                                                   "sba_creature_graveyard",
                                                                   object_label(game, id) + " has non-positive toughness; regeneration cannot replace this event",
                                                                   check_index,
                                                                   pass_index,
                                                                   pass_candidate_count);
            move_object_with_precomputed_ltb_snapshots(game, id, object(game, id).owner, Zone::Graveyard, &pre_creature_sba_ltb_snapshots);
            link_state_based_action_to_zone_change(game, sba_record_index, first_zone_record);
            pass_changed = true;
        }

        for (const ObjectId id : creatures_to_destroy) {
            if (!valid_object_index(game, id) || object(game, id).zone != Zone::Battlefield) {
                continue;
            }
            const auto first_zone_record = game.zone_change_records.size();
            const u32 sba_record_index = record_state_based_action(game,
                                                                   StateBasedActionKind::CreatureDamageDestroy,
                                                                   id,
                                                                   object(game, id).controller,
                                                                   "sba_creature_destroy",
                                                                   object_label(game, id) + " has lethal damage or deathtouch damage",
                                                                   check_index,
                                                                   pass_index,
                                                                   pass_candidate_count);
            const auto before_zone = object(game, id).zone;
            const auto before_shields = object(game, id).regeneration_shields;
            (void)destroy_permanent_with_precomputed_ltb_snapshots(game, id, true, &pre_creature_sba_ltb_snapshots);
            link_state_based_action_to_zone_change(game, sba_record_index, first_zone_record);
            finish_state_based_action_regeneration_snapshot(game, sba_record_index);
            if (object(game, id).zone != before_zone || object(game, id).regeneration_shields != before_shields) {
                pass_changed = true;
            }
        }

        for (const auto id : planeswalkers_to_graveyard) {
            if (!valid_object_index(game, id) || object(game, id).zone != Zone::Battlefield || object(game, id).counters.loyalty != 0U) {
                continue;
            }
            const auto first_zone_record = game.zone_change_records.size();
            const u32 sba_record_index = record_state_based_action(game,
                                                                   StateBasedActionKind::PlaneswalkerLoyaltyGraveyard,
                                                                   id,
                                                                   object(game, id).controller,
                                                                   "sba_planeswalker_graveyard",
                                                                   object_label(game, id) + " has zero loyalty",
                                                                   check_index,
                                                                   pass_index,
                                                                   pass_candidate_count);
            move_object(game, id, object(game, id).owner, Zone::Graveyard);
            link_state_based_action_to_zone_change(game, sba_record_index, first_zone_record);
            pass_changed = true;
        }

        for (const auto id : battles_to_graveyard) {
            if (!valid_object_index(game, id) || object(game, id).zone != Zone::Battlefield || object(game, id).counters.defense != 0U) {
                continue;
            }
            const auto first_zone_record = game.zone_change_records.size();
            const u32 sba_record_index = record_state_based_action(game,
                                                                   StateBasedActionKind::BattleDefenseGraveyard,
                                                                   id,
                                                                   object(game, id).controller,
                                                                   "sba_battle_graveyard",
                                                                   object_label(game, id) + " has zero defense",
                                                                   check_index,
                                                                   pass_index,
                                                                   pass_candidate_count);
            move_object(game, id, object(game, id).owner, Zone::Graveyard);
            link_state_based_action_to_zone_change(game, sba_record_index, first_zone_record);
            pass_changed = true;
        }

        for (const auto id : illegal_equipment) {
            if (!valid_object_index(game, id) || object(game, id).zone != Zone::Battlefield) {
                continue;
            }
            const u32 sba_record_index = record_state_based_action(game,
                                                                   StateBasedActionKind::AttachmentUnattach,
                                                                   id,
                                                                   object(game, id).controller,
                                                                   "sba_attachment_unattach",
                                                                   object_label(game, id) + " is illegally attached and becomes unattached",
                                                                   check_index,
                                                                   pass_index,
                                                                   pass_candidate_count);
            detach_object(game, id);
            if (sba_record_index != 0U && sba_record_index <= game.state_based_action_records.size()) {
                game.state_based_action_records[sba_record_index - 1U].attachment_detached = !object(game, id).attached_to.valid();
            }
            pass_changed = true;
        }

        for (const auto id : unattached_or_illegal_auras) {
            if (!valid_object_index(game, id) || object(game, id).zone != Zone::Battlefield) {
                continue;
            }
            const auto first_zone_record = game.zone_change_records.size();
            const u32 sba_record_index = record_state_based_action(game,
                                                                   StateBasedActionKind::AuraGraveyard,
                                                                   id,
                                                                   object(game, id).controller,
                                                                   "sba_aura_graveyard",
                                                                   object_label(game, id) + " is unattached or illegally attached",
                                                                   check_index,
                                                                   pass_index,
                                                                   pass_candidate_count);
            move_object(game, id, object(game, id).owner, Zone::Graveyard);
            link_state_based_action_to_zone_change(game, sba_record_index, first_zone_record);
            pass_changed = true;
        }

        if (!pass_changed) {
            break;
        }
    }
}

namespace {

void move_object_with_precomputed_ltb_snapshots(GameState& game,
                                                ObjectId object_id,
                                                PlayerId target_controller,
                                                Zone target_zone,
                                                const std::vector<TriggerSourceSnapshot>* precomputed_ltb_snapshots) {
    auto& obj = object(game, object_id);
    if (obj.ceased_to_exist) {
        record_event(game, "move_ceased_object_ignored", "object#" + std::to_string(object_id.value) + " has ceased to exist");
        return;
    }
    const Zone source_zone = obj.zone;
    const Zone requested_zone = target_zone;
    const PlayerId previous_controller = obj.controller;
    const PlayerId owner = obj.owner;
    const u64 source_zone_change_index = obj.zone_change_index;
    const bool was_token = obj.token;
    const bool was_ability_object = obj.ability_object;
    if (obj.token && !obj.ability_object && source_zone != Zone::Battlefield && target_zone != source_zone) {
        record_event(game, "move_token_after_leave_ignored", object_label(game, object_id) + " already left the battlefield and cannot move to " + to_string(target_zone));
        return;
    }
    const auto replacement_result = apply_zone_change_replacement(game, object_id, source_zone, target_zone);
    target_zone = replacement_result.final_zone;
    const bool replacement_applied = replacement_result.record_count != 0U;
    const bool was_battlefield_creature = source_zone == Zone::Battlefield && object_is_creature(game, obj);
    const bool would_die = was_battlefield_creature && target_zone == Zone::Graveyard;
    const auto pre_zone_change_trigger_sources = would_die
        ? (precomputed_ltb_snapshots != nullptr ? *precomputed_ltb_snapshots : capture_battlefield_trigger_sources(game))
        : std::vector<TriggerSourceSnapshot>{};
    auto& src = container_for_object(game, obj, obj.zone);
    erase_object_from_container(src, object_id);

    const PlayerId requested_controller = target_controller.valid() ? target_controller : obj.owner;
    obj.zone = target_zone;
    obj.controller = zone_uses_controller_container(target_zone) || zone_is_global(target_zone)
        ? requested_controller
        : obj.owner;
    obj.zone_change_index = game.next_zone_change_index++;
    if (source_zone != Zone::Battlefield && target_zone == Zone::Battlefield) {
        obj.layer_timestamp = game.next_layer_timestamp++;
    } else if (target_zone != Zone::Battlefield) {
        obj.layer_timestamp = 0U;
    }
    if (target_zone == Zone::Battlefield && valid_player_index(game, obj.controller)) {
        obj.controlled_since_turn_start_index = player(game, obj.controller).turn_start_index;
    } else if (target_zone != Zone::Battlefield) {
        obj.controlled_since_turn_start_index = 0U;
        obj.battle_protector = PlayerId{};
    }
    obj.tapped = false;
    obj.damage_marked = 0;
    obj.deathtouch_damage_marked = false;
    if (obj.regeneration_shields != 0U) {
        record_event(game, "regeneration_shields_expired", object_label(game, object_id) + " moved zones; removed " + std::to_string(obj.regeneration_shields) + " regeneration shield(s)");
        obj.regeneration_shields = 0;
    }
    obj.targets.clear();
    if (target_zone != Zone::Stack) {
        obj.chosen_mode_index = 0U;
    }
    if (target_zone != Zone::Battlefield && obj.has_copy_effect) {
        record_event(game, "copy_effect_expired", object_label(game, object_id) + " moved zones; copy effect cleared");
        obj.has_copy_effect = false;
        obj.copied_definition_index = 0U;
    }
    clear_combat_links_for_object(game, object_id);
    clear_attachment_links_for_zone_change(game, object_id);

    auto& dst = container_for_object(game, obj, target_zone);
    dst.push_back(object_id);
    const u32 zone_change_record_index = static_cast<u32>(game.zone_change_records.size() + 1U);
    if (replacement_result.first_record_index != 0U) {
        for (u32 offset = 0; offset < replacement_result.record_count; ++offset) {
            const u32 replacement_index = replacement_result.first_record_index + offset;
            if (replacement_index != 0U && replacement_index <= game.zone_change_replacement_records.size()) {
                game.zone_change_replacement_records[replacement_index - 1U].zone_change_record_index = zone_change_record_index;
            }
        }
    }
    game.zone_change_records.push_back(ZoneChangeRecord{
        .sequence = game.next_event_sequence,
        .object = object_id,
        .owner = owner,
        .previous_controller = previous_controller,
        .new_controller = obj.controller,
        .from_zone = source_zone,
        .requested_zone = requested_zone,
        .to_zone = target_zone,
        .from_zone_change_index = source_zone_change_index,
        .to_zone_change_index = obj.zone_change_index,
        .first_replacement_record_index = replacement_result.first_record_index,
        .replacement_record_count = replacement_result.record_count,
        .first_counter_change_record_index = 0U,
        .counter_change_record_count = 0U,
        .first_damage_prevention_record_index = 0U,
        .damage_prevention_record_count = 0U,
        .replacement_applied = replacement_applied,
        .was_token = was_token,
        .was_ability_object = was_ability_object,
        .was_battlefield_creature = was_battlefield_creature,
        .creature_died = would_die
    });
    record_event_with_links(game,
                            "move_object",
                            object_label(game, object_id) + " " + to_string(source_zone) + " -> " + to_string(target_zone),
                            EventRecordLinks{
                                .kind = EventRecordKind::ZoneChange,
                                .object = object_id,
                                .player = obj.controller,
                                .zone_change_record_index = zone_change_record_index
                            });
    clear_prevention_links_for_object(game, object_id, zone_change_record_index);
    const std::size_t first_counter_change_index = game.counter_change_records.size();
    const u32 counter_cleanup_records = clear_counters_for_zone_change(game, object_id, zone_change_record_index, source_zone, target_zone);
    if (counter_cleanup_records != 0U && zone_change_record_index != 0U && zone_change_record_index <= game.zone_change_records.size()) {
        auto& zone_record = game.zone_change_records[zone_change_record_index - 1U];
        zone_record.first_counter_change_record_index = static_cast<u32>(first_counter_change_index + 1U);
        zone_record.counter_change_record_count = counter_cleanup_records;
    }
    if (source_zone != Zone::Battlefield && target_zone == Zone::Battlefield) {
        add_entering_planeswalker_loyalty(game, object_id);
        add_entering_battle_defense_and_protector(game, object_id);
    }

    const bool enters_battlefield_as_creature = target_zone == Zone::Battlefield && object_is_creature(game, obj);
    if (enters_battlefield_as_creature) {
        queue_matching_triggers_for_event(game, TriggerEventKind::CreatureEntersBattlefield, object_id);
    }
    if (would_die) {
        queue_matching_triggers_from_snapshots(game, TriggerEventKind::CreatureDies, object_id, pre_zone_change_trigger_sources);
    }
}

} // namespace

void move_object(GameState& game, ObjectId object_id, PlayerId target_controller, Zone target_zone) {
    move_object_with_precomputed_ltb_snapshots(game, object_id, target_controller, target_zone, nullptr);
}

void cast_from_hand_to_stack(GameState& game, PlayerId caster, ObjectId object_id) {
    const auto& p = player(game, caster);
    const auto& hand = p.zones[zone_index(Zone::Hand)];
    if (std::find(hand.begin(), hand.end(), object_id) == hand.end()) {
        throw std::logic_error("object is not in caster's hand");
    }
    const auto ctx = move_spell_card_to_stack_for_cast(game, caster, object_id);
    record_stack_placement(game, make_spell_stack_placement_record(game, caster, object_id, ctx, false, false, false, false, false, false, false, false, false, false));
}

void finish_paid_cast_after_costs(GameState& game, PlayerId caster) {
    // CR 117.3c: the player who had priority when they cast the spell receives
    // priority afterward. Mana abilities and cost helpers are immediate effects
    // and may also leave priority on the caster while payment is being made.
    game.priority_player = caster;
    game.consecutive_priority_passes = 0;
}

bool cast_from_hand_to_stack_paying_mana(GameState& game, PlayerId caster, ObjectId object_id) {
    const auto& p = player(game, caster);
    const auto& hand = p.zones[zone_index(Zone::Hand)];
    if (std::find(hand.begin(), hand.end(), object_id) == hand.end()) {
        throw std::logic_error("object is not in caster's hand");
    }
    const auto& obj = object(game, object_id);
    if (obj.definition_index >= game.definitions.size()) {
        throw std::logic_error("object has invalid card definition");
    }
    const auto& def = game.definitions[obj.definition_index];
    if (!can_cast_spell_now(game, caster, object_id)) {
        record_event(game, "cast_spell_failed", p.name + " lacks timing permission for " + object_label(game, object_id));
        return false;
    }
    if (def.is_modal()) {
        record_event(game, "cast_spell_failed", p.name + " did not choose a mode for " + object_label(game, object_id));
        return false;
    }
    if (def.requires_target()) {
        record_event(game, "cast_spell_failed", p.name + " did not choose a target for " + object_label(game, object_id));
        return false;
    }
    const ManaCost cost = def.mana_cost;
    const std::string spell_label = object_label(game, object_id);
    return commit_paid_action_body_transaction(game,
                                               PaidActionTransactionContext{.action_kind = ActionKind::CastSpellFromHandPaid, .player = caster, .source_object = object_id},
                                               [&](GameState& staged_game, u64 physical_state_hash_before) {
        const auto ctx = move_spell_card_to_stack_for_cast(staged_game, caster, object_id);
        const auto stack_enter_sequence = stack_enter_sequence_for_context(staged_game, ctx);
        const u64 choices_locked_sequence = staged_game.next_event_sequence > 1U ? staged_game.next_event_sequence - 1U : 0U;
        const u32 declaration_record_index = record_spell_paid_action_declaration(staged_game, caster, object_id, def, ctx, stack_enter_sequence);
        const auto paid_phase = capture_paid_action_phase_snapshot(staged_game, stack_enter_sequence, choices_locked_sequence);
        if (!pay_mana_cost_with_mana_abilities(staged_game, caster, cost)) {
            return false;
        }
        if (!pay_sacrifice_cost(staged_game, caster, def.sacrifice_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_discard_cost(staged_game, caster, def.discard_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_life_cost(staged_game, caster, def.life_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_return_cost(staged_game, caster, def.return_cost, spell_label, object_id)) {
            return false;
        }
        finish_paid_cast_after_costs(staged_game, caster);
        auto placement_record = make_spell_stack_placement_record(staged_game, caster, object_id, ctx, !cost.free(), !cost.free(), def.sacrifice_cost.active(), def.sacrifice_cost.active(), def.discard_cost.active(), def.discard_cost.active(), def.life_cost.active(), def.life_cost.active(), def.return_cost.active(), def.return_cost.active());
        seal_paid_action_phase(placement_record, staged_game, paid_phase);
        seal_paid_action_declaration_for_stack_placement(staged_game, declaration_record_index, placement_record);
        const u32 placement_record_index = record_stack_placement(staged_game, std::move(placement_record));
        record_paid_action_transaction_commit(staged_game, ActionKind::CastSpellFromHandPaid, placement_record_index, physical_state_hash_before);
        return true;
    });
}

bool cast_from_hand_to_stack_paying_mana_with_target(GameState& game, PlayerId caster, ObjectId object_id, TargetRef target) {
    return cast_from_hand_to_stack_paying_mana_with_targets(game, caster, object_id, single_target_vector(target));
}

bool cast_from_hand_to_stack_paying_mana_with_targets(GameState& game, PlayerId caster, ObjectId object_id, const std::vector<TargetRef>& targets) {
    const auto& p = player(game, caster);
    const auto& hand = p.zones[zone_index(Zone::Hand)];
    if (std::find(hand.begin(), hand.end(), object_id) == hand.end()) {
        throw std::logic_error("object is not in caster's hand");
    }
    const auto& obj = object(game, object_id);
    if (obj.definition_index >= game.definitions.size()) {
        throw std::logic_error("object has invalid card definition");
    }
    const auto& def = game.definitions[obj.definition_index];
    if (!can_cast_spell_now(game, caster, object_id)) {
        record_event(game, "cast_spell_failed", p.name + " lacks timing permission for " + object_label(game, object_id));
        return false;
    }
    if (def.is_modal()) {
        record_event(game, "cast_spell_failed", p.name + " did not choose a mode for modal " + object_label(game, object_id));
        return false;
    }
    const u32 needed_targets = required_target_count_for_spell(def);
    if (!target_set_is_legal_for_source_object(game, targets, def.target_mask, needed_targets, object_id)) {
        const std::string reason = needed_targets == 0U ? "chose target(s) for untargeted " : "chose illegal/missing target set ";
        record_event(game, "cast_spell_failed", p.name + " " + reason + target_list_label(game, targets) + " for " + object_label(game, object_id));
        return false;
    }
    const ManaCost cost = def.mana_cost;
    const std::string spell_label = object_label(game, object_id);
    return commit_paid_action_body_transaction(game,
                                               PaidActionTransactionContext{.action_kind = ActionKind::CastSpellFromHandPaid, .player = caster, .source_object = object_id},
                                               [&](GameState& staged_game, u64 physical_state_hash_before) {
        const auto ctx = move_spell_card_to_stack_for_cast(staged_game, caster, object_id);
        const auto stack_enter_sequence = stack_enter_sequence_for_context(staged_game, ctx);
        if (needed_targets != 0U) {
            auto& stack_obj = object(staged_game, object_id);
            stack_obj.targets = stamp_targets_for_choice(staged_game, targets);
            const TargetRef event_target = stack_obj.targets.size() == 1U ? stack_obj.targets.front() : TargetRef{};
            record_event_with_links(staged_game,
                                    "choose_target",
                                    object_label(staged_game, object_id) + " targets " + target_list_label(staged_game, targets),
                                    EventRecordLinks{.object = object_id, .player = caster, .target = event_target, .choice_target_count = static_cast<u32>(stack_obj.targets.size()), .choice_target_set_hash = target_choice_set_hash_impl(stack_obj.targets)});
        }
        const u64 choices_locked_sequence = staged_game.next_event_sequence > 1U ? staged_game.next_event_sequence - 1U : 0U;
        const u32 declaration_record_index = record_spell_paid_action_declaration(staged_game, caster, object_id, def, ctx, stack_enter_sequence);
        const auto paid_phase = capture_paid_action_phase_snapshot(staged_game, stack_enter_sequence, choices_locked_sequence);
        if (!pay_mana_cost_with_mana_abilities(staged_game, caster, cost)) {
            return false;
        }
        if (!pay_sacrifice_cost(staged_game, caster, def.sacrifice_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_discard_cost(staged_game, caster, def.discard_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_life_cost(staged_game, caster, def.life_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_return_cost(staged_game, caster, def.return_cost, spell_label, object_id)) {
            return false;
        }
        finish_paid_cast_after_costs(staged_game, caster);
        auto placement_record = make_spell_stack_placement_record(staged_game, caster, object_id, ctx, !cost.free(), !cost.free(), def.sacrifice_cost.active(), def.sacrifice_cost.active(), def.discard_cost.active(), def.discard_cost.active(), def.life_cost.active(), def.life_cost.active(), def.return_cost.active(), def.return_cost.active());
        seal_paid_action_phase(placement_record, staged_game, paid_phase);
        seal_paid_action_declaration_for_stack_placement(staged_game, declaration_record_index, placement_record);
        const u32 placement_record_index = record_stack_placement(staged_game, std::move(placement_record));
        record_paid_action_transaction_commit(staged_game, ActionKind::CastSpellFromHandPaid, placement_record_index, physical_state_hash_before);
        return true;
    });
}

bool cast_from_hand_to_stack_paying_mana_with_mode(GameState& game, PlayerId caster, ObjectId object_id, std::uint32_t mode_index, TargetRef target) {
    return cast_from_hand_to_stack_paying_mana_with_mode_and_targets(game, caster, object_id, mode_index, single_target_vector(target));
}

bool cast_from_hand_to_stack_paying_mana_with_mode_and_targets(GameState& game, PlayerId caster, ObjectId object_id, std::uint32_t mode_index, const std::vector<TargetRef>& targets) {
    const auto& p = player(game, caster);
    const auto& hand = p.zones[zone_index(Zone::Hand)];
    if (std::find(hand.begin(), hand.end(), object_id) == hand.end()) {
        throw std::logic_error("object is not in caster's hand");
    }
    const auto& obj_ref = object(game, object_id);
    if (obj_ref.definition_index >= game.definitions.size()) {
        throw std::logic_error("object has invalid card definition");
    }
    const auto& def = game.definitions[obj_ref.definition_index];
    if (!can_cast_spell_now(game, caster, object_id)) {
        record_event(game, "cast_spell_failed", p.name + " lacks timing permission for " + object_label(game, object_id));
        return false;
    }
    if (!def.is_modal()) {
        record_event(game, "cast_spell_failed", p.name + " chose a mode for nonmodal " + object_label(game, object_id));
        return false;
    }
    if (!valid_spell_mode_index(def, mode_index)) {
        record_event(game, "cast_spell_failed", p.name + " chose invalid " + mode_label(def, mode_index) + " for " + object_label(game, object_id));
        return false;
    }
    const auto& mode = spell_mode_definition(def, mode_index);
    if (!mode.active()) {
        record_event(game, "cast_spell_failed", p.name + " chose inactive " + mode_label(def, mode_index) + " for " + object_label(game, object_id));
        return false;
    }
    const u32 needed_targets = required_target_count_for_mode(mode);
    if (!target_set_is_legal_for_source_object(game, targets, mode.target_mask, needed_targets, object_id)) {
        const std::string reason = needed_targets == 0U ? "chose target(s) for untargeted " : "chose illegal/missing target set ";
        record_event(game, "cast_spell_failed", p.name + " " + reason + target_list_label(game, targets) + " for " + object_label(game, object_id) + " " + mode_label(def, mode_index));
        return false;
    }
    const ManaCost cost = def.mana_cost;
    const std::string spell_label = object_label(game, object_id);
    return commit_paid_action_body_transaction(game,
                                               PaidActionTransactionContext{.action_kind = ActionKind::CastSpellFromHandPaid, .player = caster, .source_object = object_id},
                                               [&](GameState& staged_game, u64 physical_state_hash_before) {
        const auto ctx = move_spell_card_to_stack_for_cast(staged_game, caster, object_id);
        const auto stack_enter_sequence = stack_enter_sequence_for_context(staged_game, ctx);
        auto& stack_obj = object(staged_game, object_id);
        stack_obj.chosen_mode_index = mode_index;
        record_event_with_links(staged_game,
                                "choose_mode",
                                object_label(staged_game, object_id) + " chose " + mode_label(def, mode_index),
                                EventRecordLinks{.object = object_id, .player = caster, .choice_mode_index = mode_index, .choice_mode_contract_hash = mode_choice_contract_hash_impl(mode)});
        if (needed_targets != 0U) {
            stack_obj.targets = stamp_targets_for_choice(staged_game, targets);
            const TargetRef event_target = stack_obj.targets.size() == 1U ? stack_obj.targets.front() : TargetRef{};
            record_event_with_links(staged_game,
                                    "choose_target",
                                    object_label(staged_game, object_id) + " " + mode_label(def, mode_index) + " targets " + target_list_label(staged_game, targets),
                                    EventRecordLinks{.object = object_id, .player = caster, .target = event_target, .choice_target_count = static_cast<u32>(stack_obj.targets.size()), .choice_target_set_hash = target_choice_set_hash_impl(stack_obj.targets)});
        }
        const u64 choices_locked_sequence = staged_game.next_event_sequence > 1U ? staged_game.next_event_sequence - 1U : 0U;
        const u32 declaration_record_index = record_spell_paid_action_declaration(staged_game, caster, object_id, def, ctx, stack_enter_sequence);
        const auto paid_phase = capture_paid_action_phase_snapshot(staged_game, stack_enter_sequence, choices_locked_sequence);
        if (!pay_mana_cost_with_mana_abilities(staged_game, caster, cost)) {
            return false;
        }
        if (!pay_sacrifice_cost(staged_game, caster, def.sacrifice_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_discard_cost(staged_game, caster, def.discard_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_life_cost(staged_game, caster, def.life_cost, spell_label, object_id)) {
            return false;
        }
        if (!pay_return_cost(staged_game, caster, def.return_cost, spell_label, object_id)) {
            return false;
        }
        finish_paid_cast_after_costs(staged_game, caster);
        auto placement_record = make_spell_stack_placement_record(staged_game, caster, object_id, ctx, !cost.free(), !cost.free(), def.sacrifice_cost.active(), def.sacrifice_cost.active(), def.discard_cost.active(), def.discard_cost.active(), def.life_cost.active(), def.life_cost.active(), def.return_cost.active(), def.return_cost.active());
        seal_paid_action_phase(placement_record, staged_game, paid_phase);
        seal_paid_action_declaration_for_stack_placement(staged_game, declaration_record_index, placement_record);
        const u32 placement_record_index = record_stack_placement(staged_game, std::move(placement_record));
        record_paid_action_transaction_commit(staged_game, ActionKind::CastSpellFromHandPaid, placement_record_index, physical_state_hash_before);
        return true;
    });
}

void resolve_top_of_stack(GameState& game) {
    if (game.stack.empty()) {
        throw std::logic_error("cannot resolve an empty stack");
    }
    const ObjectId top = game.stack.back();
    const auto& obj = object(game, top);
    const auto& def = game.definitions[obj.definition_index];
    const PlayerId controller = obj.controller;
    const bool ability_object = obj.ability_object;
    const bool permanent_spell = !ability_object && def.is_permanent();
    const bool aura_spell = !ability_object && def.attachment_kind == AttachmentKind::Aura;
    const bool modal_spell = def.is_modal();
    const u32 chosen_mode_index = obj.chosen_mode_index;
    const u64 stack_zone_change_index = obj.zone_change_index;
    const std::vector<TargetRef> chosen_targets = obj.targets;
    const u32 linked_trigger_record_index = ability_object ? trigger_record_index_for_stack_object(game, top) : 0U;

    EffectKind effect_kind = def.effect_kind;
    u32 effect_amount = def.effect_amount;
    CounterKind effect_counter_kind = def.effect_counter_kind;
    u32 target_mask = def.target_mask;
    u32 target_count = def.target_count;
    u32 created_token_definition_index = def.created_token_definition_index;
    bool modal_choice_invalid = false;
    std::string resolved_mode_label;
    if (modal_spell) {
        if (!valid_spell_mode_index(def, chosen_mode_index)) {
            modal_choice_invalid = true;
            resolved_mode_label = mode_label(def, chosen_mode_index);
        } else {
            const auto& mode = spell_mode_definition(def, chosen_mode_index);
            effect_kind = mode.effect_kind;
            effect_amount = mode.effect_amount;
            effect_counter_kind = mode.effect_counter_kind;
            target_mask = mode.target_mask;
            target_count = mode.target_count;
            created_token_definition_index = mode.created_token_definition_index;
            resolved_mode_label = mode_label(def, chosen_mode_index);
        }
    }

    const u32 needed_targets = required_target_count_for_mask(target_mask, target_count);
    const bool has_targets = !chosen_targets.empty();
    const std::vector<TargetResolutionCheckRecord> target_resolution_checks = make_target_resolution_checks(game, chosen_targets, target_mask, top);
    const std::vector<TargetRef> legal_targets_on_resolution = legal_targets_from_resolution_checks(target_resolution_checks);
    const auto legal_target_count = static_cast<u32>(legal_targets_on_resolution.size());
    const bool all_targets_illegal = has_targets && legal_target_count == 0U;
    const bool missing_required_targets = chosen_targets.size() < needed_targets;
    const bool target_required = needed_targets != 0U && (effect_kind != EffectKind::None || aura_spell);
    const bool required_target_failed = target_required && (missing_required_targets || all_targets_illegal);

    StackResolutionRecord resolution_record{
        .stack_object = top,
        .controller = controller,
        .ability_object = ability_object,
        .permanent_spell = permanent_spell,
        .aura_spell = aura_spell,
        .modal_spell = modal_spell,
        .chosen_mode_index = chosen_mode_index,
        .effect_kind = effect_kind,
        .effect_amount = effect_amount,
        .effect_counter_kind = effect_counter_kind,
        .target_mask = target_mask,
        .target_count = target_count,
        .chosen_targets = chosen_targets,
        .target_resolution_checks = target_resolution_checks,
        .trigger_record_index = linked_trigger_record_index,
        .required_target_count = needed_targets,
        .legal_target_count = legal_target_count,
        .missing_required_targets = missing_required_targets,
        .all_targets_illegal = all_targets_illegal,
        .required_target_failed = required_target_failed,
        .modal_choice_invalid = modal_choice_invalid,
        .effect_payload_applied = false,
        .outcome = StackResolutionOutcome::Resolved,
        .stack_zone_change_index = stack_zone_change_index,
        .stack_leave_zone_change_record_index = 0,
        .stack_object_left_stack = false,
        .final_zone = Zone::Stack
    };

    if (has_targets && legal_target_count != 0U && legal_target_count < chosen_targets.size()) {
        record_event(game, ability_object ? "resolve_ability_partial_legal_targets" : "resolve_spell_partial_legal_targets",
                     object_label(game, top) + " legal_targets=" + std::to_string(legal_target_count) + "/" + std::to_string(chosen_targets.size()));
    }

    if (modal_choice_invalid) {
        resolution_record.outcome = StackResolutionOutcome::InvalidMode;
        record_event(game, ability_object ? "resolve_ability_invalid_mode" : "resolve_spell_invalid_mode", object_label(game, top));
    } else if (effect_kind != EffectKind::None) {
        if (required_target_failed) {
            resolution_record.outcome = StackResolutionOutcome::NoLegalTargets;
            record_event(game, ability_object ? "resolve_ability_no_legal_targets" : "resolve_spell_no_legal_targets", object_label(game, top));
        } else {
            resolution_record.effect_payload_applied = true;
            apply_effect_payload(game, top, controller, effect_kind, effect_amount, effect_counter_kind, target_mask, created_token_definition_index, legal_targets_on_resolution);
            std::string detail = object_label(game, top) + " effect=" + to_string(effect_kind);
            if (!resolved_mode_label.empty()) {
                detail += " " + resolved_mode_label;
            }
            record_event(game, "resolve_effect", detail);
        }
    } else if (required_target_failed) {
        resolution_record.outcome = StackResolutionOutcome::NoLegalTargets;
        record_event(game, ability_object ? "resolve_ability_no_legal_targets" : "resolve_spell_no_legal_targets", object_label(game, top));
    }

    auto move_resolving_stack_object = [&](PlayerId destination_controller, Zone destination_zone) {
        const auto before_zone_records = game.zone_change_records.size();
        move_object(game, top, destination_controller, destination_zone);
        if (game.zone_change_records.size() > before_zone_records && resolution_record.stack_leave_zone_change_record_index == 0U) {
            resolution_record.stack_leave_zone_change_record_index = static_cast<u32>(before_zone_records + 1U);
        }
    };

    if (ability_object) {
        move_resolving_stack_object(controller, Zone::Exile);
        record_event(game, "resolve_triggered_ability", object_label(game, top) + " resolved and ceased to exist scaffold");
    } else if (permanent_spell) {
        if (aura_spell) {
            if (required_target_failed) {
                move_resolving_stack_object(controller, Zone::Graveyard);
                record_event(game, "resolve_aura_no_legal_enchant", object_label(game, top) + " went to graveyard without entering because its enchant target was illegal");
            } else {
                const TargetRef enchant_target = chosen_targets.front();
                move_resolving_stack_object(controller, Zone::Battlefield);
                if (!attach_object_to(game, top, enchant_target)) {
                    resolution_record.outcome = StackResolutionOutcome::AuraAttachFailed;
                    move_object(game, top, object(game, top).owner, Zone::Graveyard);
                    record_event(game, "resolve_aura_attach_failed", object_label(game, top) + " could not legally attach after entering and moved to graveyard");
                } else {
                    record_event(game, "resolve_spell", object_label(game, top) + " resolved as attached aura");
                }
            }
        } else {
            move_resolving_stack_object(controller, Zone::Battlefield);
            record_event(game, "resolve_spell", object_label(game, top) + " resolved as permanent");
        }
    } else {
        move_resolving_stack_object(controller, Zone::Graveyard);
        record_event(game, "resolve_spell", object_label(game, top) + " resolved to graveyard");
    }

    if (valid_object_index(game, top)) {
        resolution_record.final_zone = object(game, top).zone;
        resolution_record.stack_object_left_stack = object(game, top).zone != Zone::Stack;
    }
    resolution_record.sequence = game.next_event_sequence;
    const u32 resolution_record_index = static_cast<u32>(game.stack_resolution_records.size() + 1U);
    game.stack_resolution_records.push_back(std::move(resolution_record));
    if (linked_trigger_record_index != 0U && linked_trigger_record_index <= game.trigger_records.size()) {
        auto& trigger_record = game.trigger_records[linked_trigger_record_index - 1U];
        const auto& stored_resolution_record = game.stack_resolution_records.back();
        trigger_record.stack_resolution_record_index = resolution_record_index;
        trigger_record.resolved_sequence = stored_resolution_record.sequence;
        trigger_record.resolution_outcome = stored_resolution_record.outcome;
        trigger_record.resolved_effect_payload_applied = stored_resolution_record.effect_payload_applied;
    }
    record_event_with_links(game,
                            "stack_resolution_recorded",
                            object_label(game, top) + " outcome=" + to_string(game.stack_resolution_records.back().outcome) +
                                " final_zone=" + to_string(game.stack_resolution_records.back().final_zone),
                            EventRecordLinks{
                                .kind = EventRecordKind::StackResolution,
                                .object = top,
                                .player = controller,
                                .trigger_record_index = linked_trigger_record_index,
                                .stack_resolution_record_index = resolution_record_index
                            });

    game.priority_player = game.active_player;
    game.consecutive_priority_passes = 0;
    apply_state_based_actions(game);
}



namespace {

constexpr std::size_t kMaxDeclarationActionsPerPlayer = 128U;

[[nodiscard]] ChoiceRequest choice_request_for_player_with_state_hash(const GameState& game, PlayerId player_id, u64 state_hash);

[[nodiscard]] bool attack_declaration_choice_pending(const GameState& game) noexcept {
    return game.step == Step::DeclareAttackers && game.stack.empty() && !game.attackers_declared_this_step &&
           valid_player_index(game, game.active_player) && !player(game, game.active_player).lost;
}

[[nodiscard]] bool blocker_declaration_choice_pending_for_player(const GameState& game, PlayerId player_id) noexcept {
    return game.step == Step::DeclareBlockers && game.stack.empty() && valid_player_index(game, player_id) &&
           !player(game, player_id).lost && !blocker_declaration_completed_for_player(game, player_id) &&
           player_has_attackers_to_block(game, player_id);
}

[[nodiscard]] bool any_blocker_declaration_choice_pending(const GameState& game) noexcept {
    if (game.step != Step::DeclareBlockers || !game.stack.empty()) {
        return false;
    }
    for (const auto& candidate : game.players) {
        if (blocker_declaration_choice_pending_for_player(game, candidate.id)) {
            return true;
        }
    }
    return false;
}

[[nodiscard]] ObjectId first_attacker_needing_damage_order(const GameState& game) {
    if (!all_blocker_declarations_complete(game) || !valid_player_index(game, game.active_player) ||
        player(game, game.active_player).lost) {
        return ObjectId{};
    }

    std::vector<ObjectId> attackers;
    for (const auto attacker_id : zone(game, game.active_player, Zone::Battlefield)) {
        if (object_is_battlefield_creature(game, attacker_id) && object(game, attacker_id).attacking &&
            current_blockers_for_attacker(game, attacker_id).size() >= 2U &&
            object(game, attacker_id).combat_damage_ordered_blockers.empty()) {
            attackers.push_back(attacker_id);
        }
    }
    std::sort(attackers.begin(), attackers.end(), [](ObjectId a, ObjectId b) { return a.value < b.value; });
    return attackers.empty() ? ObjectId{} : attackers.front();
}

[[nodiscard]] bool damage_order_choice_pending(const GameState& game) {
    return first_attacker_needing_damage_order(game).valid();
}

void label_attack_declaration_action(const GameState& game, LegalAction& action, const std::vector<AttackAssignment>& assignments) {
    if (assignments.size() > 1U) {
        action.label = std::string(to_string(ActionKind::DeclareAttacker)) + ":batch:" + std::to_string(assignments.size());
    } else if (assignments.empty()) {
        action.label = std::string(to_string(ActionKind::DeclareAttacker)) + ":none";
    } else {
        action.label = std::string(to_string(ActionKind::DeclareAttacker)) + ":" +
            object_label(game, assignments.front().attacker) + "->" + target_label(game, assignments.front().target);
    }
}

void label_block_declaration_action(const GameState& game, LegalAction& action, const std::vector<BlockAssignment>& assignments) {
    if (assignments.size() > 1U) {
        action.label = std::string(to_string(ActionKind::DeclareBlocker)) + ":batch:" + std::to_string(assignments.size());
    } else if (assignments.empty()) {
        action.label = std::string(to_string(ActionKind::DeclareBlocker)) + ":none";
    } else {
        action.label = std::string(to_string(ActionKind::DeclareBlocker)) + ":" +
            object_label(game, assignments.front().blocker) + "->" + object_label(game, assignments.front().attacker);
    }
}

void label_combat_damage_order_action(const GameState& game, LegalAction& action, ObjectId attacker_id, const std::vector<ObjectId>& blocker_order) {
    action.label = std::string(to_string(ActionKind::OrderCombatDamage)) + ":" + object_label(game, attacker_id) + "->";
    for (std::size_t i = 0; i < blocker_order.size(); ++i) {
        if (i != 0U) {
            action.label += ",";
        }
        action.label += object_label(game, blocker_order[i]);
    }
}

using LegalActionEmitter = std::function<bool(LegalAction)>;
using LegalActionProducer = std::function<void(const LegalActionEmitter&)>;

void for_each_legal_attack_declaration(const GameState& game, PlayerId player_id, const LegalActionEmitter& emit) {
    const u32 maximum_requirement_count = maximum_satisfied_attack_requirements(game, player_id);
    auto emit_declaration = [&](const std::vector<AttackAssignment>& assignments) -> bool {
        if (!can_declare_attackers_with_requirement_max(game, player_id, assignments, maximum_requirement_count)) {
            return true;
        }
        auto action = make_declare_attackers_action(player_id, assignments);
        label_attack_declaration_action(game, action, assignments);
        return emit(std::move(action));
    };

    if (!emit_declaration(std::vector<AttackAssignment>{})) {
        return;
    }

    std::vector<std::vector<AttackAssignment>> choices_by_attacker;
    for (const auto object_id : player(game, player_id).zones[zone_index(Zone::Battlefield)]) {
        std::vector<AttackAssignment> choices;
        for (const auto& defender : game.players) {
            const TargetRef defender_target{.kind = TargetKind::Player, .player = defender.id};
            if (can_declare_attacker_to_target(game, player_id, object_id, defender_target)) {
                choices.push_back(AttackAssignment{.attacker = object_id, .target = defender_target});
            }
        }
        for (const auto& defender : game.players) {
            for (const auto target_id : defender.zones[zone_index(Zone::Battlefield)]) {
                if (!object_is_battlefield_combat_target(game, target_id)) {
                    continue;
                }
                const TargetRef object_target{.kind = TargetKind::Object, .object = target_id};
                if (can_declare_attacker_to_target(game, player_id, object_id, object_target)) {
                    choices.push_back(AttackAssignment{.attacker = object_id, .target = object_target});
                }
            }
        }
        if (!choices.empty()) {
            choices_by_attacker.push_back(std::move(choices));
        }
    }

    bool stopped = false;
    std::vector<AttackAssignment> current_assignments;
    auto enumerate_attack_declarations = [&](auto&& self, std::size_t index) -> void {
        if (stopped) {
            return;
        }
        if (index == choices_by_attacker.size()) {
            if (!current_assignments.empty() && !emit_declaration(current_assignments)) {
                stopped = true;
            }
            return;
        }
        self(self, index + 1U);
        if (stopped) {
            return;
        }
        for (const auto assignment : choices_by_attacker[index]) {
            current_assignments.push_back(assignment);
            self(self, index + 1U);
            current_assignments.pop_back();
            if (stopped) {
                return;
            }
        }
    };
    enumerate_attack_declarations(enumerate_attack_declarations, 0U);
}

void for_each_legal_block_declaration(const GameState& game, PlayerId player_id, const LegalActionEmitter& emit) {
    const u32 maximum_requirement_count = maximum_satisfied_block_requirements(game, player_id);
    auto emit_declaration = [&](const std::vector<BlockAssignment>& assignments) -> bool {
        if (!can_declare_blockers_with_requirement_max(game, player_id, assignments, maximum_requirement_count)) {
            return true;
        }
        auto action = make_declare_blockers_action(player_id, assignments);
        label_block_declaration_action(game, action, assignments);
        return emit(std::move(action));
    };

    if (!emit_declaration(std::vector<BlockAssignment>{})) {
        return;
    }

    std::vector<ObjectId> blockable_attackers;
    for (const auto& maybe_attacker_owner : game.players) {
        for (const auto attacker_id : maybe_attacker_owner.zones[zone_index(Zone::Battlefield)]) {
            if (object_is_battlefield_creature(game, attacker_id) && object(game, attacker_id).attacking &&
                object(game, attacker_id).defending_player == player_id) {
                blockable_attackers.push_back(attacker_id);
            }
        }
    }

    std::vector<std::vector<BlockAssignment>> choices_by_blocker;
    for (const auto blocker_id : player(game, player_id).zones[zone_index(Zone::Battlefield)]) {
        std::vector<BlockAssignment> choices;
        for (const auto attacker_id : blockable_attackers) {
            const BlockAssignment assignment{.blocker = blocker_id, .attacker = attacker_id};
            if (block_assignment_basic_legal(game, player_id, assignment)) {
                choices.push_back(assignment);
            }
        }
        if (!choices.empty()) {
            choices_by_blocker.push_back(std::move(choices));
        }
    }

    bool stopped = false;
    std::vector<BlockAssignment> current_assignments;
    auto enumerate_block_declarations = [&](auto&& self, std::size_t index) -> void {
        if (stopped) {
            return;
        }
        if (index == choices_by_blocker.size()) {
            if (!current_assignments.empty() && !emit_declaration(current_assignments)) {
                stopped = true;
            }
            return;
        }
        self(self, index + 1U);
        if (stopped) {
            return;
        }
        for (const auto assignment : choices_by_blocker[index]) {
            current_assignments.push_back(assignment);
            self(self, index + 1U);
            current_assignments.pop_back();
            if (stopped) {
                return;
            }
        }
    };
    enumerate_block_declarations(enumerate_block_declarations, 0U);
}

void for_each_legal_combat_damage_order(const GameState& game, PlayerId player_id, const LegalActionEmitter& emit) {
    if (player_id != game.active_player) {
        return;
    }
    const ObjectId attacker_id = first_attacker_needing_damage_order(game);
    if (!attacker_id.valid()) {
        return;
    }

    std::vector<ObjectId> blocker_order = current_blockers_for_attacker(game, attacker_id);
    while (true) {
        if (can_order_combat_damage(game, player_id, attacker_id, blocker_order)) {
            auto action = make_order_combat_damage_action(player_id, attacker_id, blocker_order);
            label_combat_damage_order_action(game, action, attacker_id, blocker_order);
            if (!emit(std::move(action))) {
                return;
            }
        }
        if (!std::next_permutation(blocker_order.begin(), blocker_order.end(), [](ObjectId a, ObjectId b) { return a.value < b.value; })) {
            break;
        }
    }
}

void finalize_legal_action_page(LegalActionPage& page) noexcept {
    page.total_actions_lower_bound = page.actions_seen;
    page.total_actions_exact = page.complete;
    page.remaining_actions_lower_bound = 0U;
    if (!page.complete && page.actions_seen > page.next_cursor) {
        page.remaining_actions_lower_bound = page.actions_seen - page.next_cursor;
    }
    page.page_hash = legal_action_page_hash(page);
}

struct LegalActionPageBuilder {
    LegalActionPage page{};

    LegalActionPageBuilder(ChoiceRequestKind kind, PlayerId chooser, u64 cursor, u64 limit, u64 state_hash, u64 choice_request_hash) {
        page.kind = kind;
        page.chooser = chooser;
        page.state_hash = state_hash;
        page.choice_request_hash = choice_request_hash;
        page.cursor = cursor;
        page.next_cursor = cursor;
        page.requested_limit = limit;
        page.effective_limit = limit == 0U ? 1U : limit;
    }

    [[nodiscard]] bool accept(LegalAction action) {
        ++page.actions_seen;
        if (page.actions_seen <= page.cursor) {
            return true;
        }
        if (static_cast<u64>(page.actions.size()) < page.effective_limit) {
            page.actions.push_back(std::move(action));
            page.next_cursor = page.cursor + static_cast<u64>(page.actions.size());
            return true;
        }
        page.complete = false;
        page.next_cursor = page.cursor + static_cast<u64>(page.actions.size());
        return false;
    }

    [[nodiscard]] LegalActionPage finish() {
        finalize_legal_action_page(page);
        return std::move(page);
    }
};

LegalActionPage make_attack_declaration_page(const GameState& game, PlayerId player_id, u64 cursor, u64 limit, u64 state_hash, u64 choice_request_hash) {
    LegalActionPageBuilder builder{ChoiceRequestKind::DeclareAttackers, player_id, cursor, limit, state_hash, choice_request_hash};
    for_each_legal_attack_declaration(game, player_id, [&](LegalAction action) {
        return builder.accept(std::move(action));
    });
    return builder.finish();
}

LegalActionPage make_block_declaration_page(const GameState& game, PlayerId player_id, u64 cursor, u64 limit, u64 state_hash, u64 choice_request_hash) {
    LegalActionPageBuilder builder{ChoiceRequestKind::DeclareBlockers, player_id, cursor, limit, state_hash, choice_request_hash};
    for_each_legal_block_declaration(game, player_id, [&](LegalAction action) {
        return builder.accept(std::move(action));
    });
    return builder.finish();
}

LegalActionPage make_combat_damage_order_page(const GameState& game, PlayerId player_id, u64 cursor, u64 limit, u64 state_hash, u64 choice_request_hash) {
    LegalActionPageBuilder builder{ChoiceRequestKind::OrderCombatDamage, player_id, cursor, limit, state_hash, choice_request_hash};
    for_each_legal_combat_damage_order(game, player_id, [&](LegalAction action) {
        return builder.accept(std::move(action));
    });
    return builder.finish();
}

void append_bounded_frontier_actions(LegalActionFrontier& frontier, const LegalActionProducer& enumerate_actions) {
    frontier.generation_limit = static_cast<u64>(kMaxDeclarationActionsPerPlayer);
    auto& actions = frontier.actions;
    std::size_t generated = 0U;
    enumerate_actions([&](LegalAction action) {
        if (generated >= kMaxDeclarationActionsPerPlayer) {
            frontier.complete = false;
            return false;
        }
        actions.push_back(std::move(action));
        ++generated;
        return true;
    });
}

void append_attack_declaration_actions(const GameState& game, PlayerId player_id, LegalActionFrontier& frontier) {
    append_bounded_frontier_actions(frontier, [&](const LegalActionEmitter& emit) {
        for_each_legal_attack_declaration(game, player_id, emit);
    });
}

void append_combat_damage_order_actions(const GameState& game, PlayerId player_id, LegalActionFrontier& frontier) {
    append_bounded_frontier_actions(frontier, [&](const LegalActionEmitter& emit) {
        for_each_legal_combat_damage_order(game, player_id, emit);
    });
}

void append_block_declaration_actions(const GameState& game, PlayerId player_id, LegalActionFrontier& frontier) {
    append_bounded_frontier_actions(frontier, [&](const LegalActionEmitter& emit) {
        for_each_legal_block_declaration(game, player_id, emit);
    });
}


} // namespace

LegalActionFrontier enumerate_legal_action_frontier(const GameState& game, PlayerId player_id) {
    LegalActionFrontier frontier{};
    if (!valid_player_index(game, player_id)) {
        return frontier;
    }
    const auto& p = player(game, player_id);
    auto& actions = frontier.actions;
    if (p.lost) {
        return frontier;
    }

    // Turn-based combat declaration choices are mandatory gates. Do not expose
    // ordinary priority actions until the relevant declaration window has been
    // explicitly completed, including by a legal empty declaration.
    if (attack_declaration_choice_pending(game)) {
        if (game.active_player == player_id) {
            append_attack_declaration_actions(game, player_id, frontier);
        }
        return frontier;
    }

    if (any_blocker_declaration_choice_pending(game)) {
        if (blocker_declaration_choice_pending_for_player(game, player_id)) {
            append_block_declaration_actions(game, player_id, frontier);
        }
        return frontier;
    }

    if (damage_order_choice_pending(game)) {
        if (game.active_player == player_id) {
            append_combat_damage_order_actions(game, player_id, frontier);
        }
        return frontier;
    }

    const bool has_priority = game.priority_player == player_id;
    if (has_priority) {
        if (!game.pending_triggers.empty()) {
            append_pending_trigger_order_actions(game, player_id, frontier);
            return frontier;
        }

        actions.push_back(LegalAction{
            .kind = ActionKind::PassPriority,
            .player = player_id,
            .object = ObjectId{},
            .label = std::string(to_string(ActionKind::PassPriority))
        });

        for (const auto object_id : p.zones[zone_index(Zone::Hand)]) {
            const auto& obj = object(game, object_id);
            if (obj.definition_index >= game.definitions.size()) {
                continue;
            }
            const auto& def = game.definitions[obj.definition_index];
            if (can_play_land(game, player_id, object_id)) {
                actions.push_back(LegalAction{
                    .kind = ActionKind::PlayLand,
                    .player = player_id,
                    .object = object_id,
                    .label = std::string(to_string(ActionKind::PlayLand)) + ":" + def.name
                });
                continue;
            }
            if (can_cast_spell_now(game, player_id, object_id) && can_pay_spell_costs(game, player_id, object_id, def)) {
                const std::string base_label = std::string(to_string(ActionKind::CastSpellFromHandPaid)) + ":" + def.name;
                if (def.is_modal()) {
                    for (u32 mode_index = 1U; mode_index <= def.modes.size(); ++mode_index) {
                        const auto& mode = spell_mode_definition(def, mode_index);
                        if (!mode.active()) {
                            continue;
                        }
                        const std::string label = base_label + ":" + mode_label(def, mode_index);
                        const u32 needed_targets = required_target_count_for_mode(mode);
                        if (needed_targets != 0U && mode.effect_kind != EffectKind::None) {
                            for (const auto& targets : enumerate_legal_target_sets_for_source_object(game, mode.target_mask, needed_targets, object_id)) {
                                const auto primary = targets.empty() ? TargetRef{} : targets.front();
                                actions.push_back(LegalAction{
                                    .kind = ActionKind::CastSpellFromHandPaid,
                                    .player = player_id,
                                    .object = object_id,
                                    .label = label + "->" + target_list_label(game, targets),
                                    .target = primary,
                                    .targets = targets,
                                    .mode_index = mode_index
                                });
                            }
                        } else {
                            actions.push_back(LegalAction{
                                .kind = ActionKind::CastSpellFromHandPaid,
                                .player = player_id,
                                .object = object_id,
                                .label = label,
                                .mode_index = mode_index
                            });
                        }
                    }
                } else if (def.requires_target()) {
                    const u32 needed_targets = required_target_count_for_spell(def);
                    for (const auto& targets : enumerate_legal_target_sets_for_source_object(game, def.target_mask, needed_targets, object_id)) {
                        const auto primary = targets.empty() ? TargetRef{} : targets.front();
                        actions.push_back(LegalAction{
                            .kind = ActionKind::CastSpellFromHandPaid,
                            .player = player_id,
                            .object = object_id,
                            .label = base_label + "->" + target_list_label(game, targets),
                            .target = primary,
                            .targets = targets
                        });
                    }
                } else {
                    actions.push_back(LegalAction{
                        .kind = ActionKind::CastSpellFromHandPaid,
                        .player = player_id,
                        .object = object_id,
                        .label = base_label
                    });
                }
            }
        }

        for (const auto object_id : p.zones[zone_index(Zone::Battlefield)]) {
            const auto& obj = object(game, object_id);
            const auto* def_ptr = current_definition_for_object(game, obj);
            if (def_ptr == nullptr) {
                continue;
            }
            const auto& def = *def_ptr;
            const u32 count = total_mana_ability_count_for_definition(def);
            for (u32 mana_ability_index = 1U; mana_ability_index <= count; ++mana_ability_index) {
                if (!can_activate_mana_ability(game, player_id, object_id, mana_ability_index)) {
                    continue;
                }
                const bool legacy_builtin = def.taps_for_mana && mana_ability_index == 1U;
                actions.push_back(LegalAction{
                    .kind = legacy_builtin ? ActionKind::ActivateTapManaAbility : ActionKind::ActivateManaAbility,
                    .player = player_id,
                    .object = object_id,
                    .label = std::string(to_string(legacy_builtin ? ActionKind::ActivateTapManaAbility : ActionKind::ActivateManaAbility)) + ":" + def.name + ":" + mana_ability_label(def, mana_ability_index),
                    .mana_ability_index = mana_ability_index
                });
            }
        }

        for (const auto object_id : p.zones[zone_index(Zone::Battlefield)]) {
            const auto& obj = object(game, object_id);
            const auto* def_ptr = current_definition_for_object(game, obj);
            if (def_ptr == nullptr) {
                continue;
            }
            const auto& def = *def_ptr;
            for (u32 ability_index = 1U; ability_index <= def.activated_abilities.size(); ++ability_index) {
                const auto& ability = activated_ability_definition(def, ability_index);
                if (!ability.active()) {
                    continue;
                }
                const std::string base_label = std::string(to_string(ActionKind::ActivateActivatedAbility)) + ":" + def.name + ":" + activated_ability_label(def, ability_index);
                const u32 needed_targets = required_target_count_for_activated_ability(ability);
                if (needed_targets == 0U) {
                    if (can_activate_activated_ability_with_targets(game, player_id, object_id, ability_index, {})) {
                        actions.push_back(LegalAction{
                            .kind = ActionKind::ActivateActivatedAbility,
                            .player = player_id,
                            .object = object_id,
                            .label = base_label,
                            .ability_index = ability_index
                        });
                    }
                } else {
                    for (const auto& targets : enumerate_legal_target_sets_for_source_object(game, ability.target_mask, needed_targets, object_id)) {
                        if (can_activate_activated_ability_with_targets(game, player_id, object_id, ability_index, targets)) {
                            const auto primary = targets.empty() ? TargetRef{} : targets.front();
                            actions.push_back(LegalAction{
                                .kind = ActionKind::ActivateActivatedAbility,
                                .player = player_id,
                                .object = object_id,
                                .label = base_label + "->" + target_list_label(game, targets),
                                .target = primary,
                                .targets = targets,
                                .ability_index = ability_index
                            });
                        }
                    }
                }
            }
        }

        for (const auto object_id : p.zones[zone_index(Zone::Battlefield)]) {
            const auto& obj = object(game, object_id);
            const auto* def_ptr = current_definition_for_object(game, obj);
            if (def_ptr == nullptr) {
                continue;
            }
            const auto& def = *def_ptr;
            if (!def.loyalty_ability.active()) {
                continue;
            }
            const std::string base_label = std::string(to_string(ActionKind::ActivateLoyaltyAbility)) + ":" + def.name;
            const u32 needed_targets = required_target_count_for_loyalty_ability(def.loyalty_ability);
            if (needed_targets == 0U) {
                if (can_activate_loyalty_ability_with_targets(game, player_id, object_id, {})) {
                    actions.push_back(LegalAction{
                        .kind = ActionKind::ActivateLoyaltyAbility,
                        .player = player_id,
                        .object = object_id,
                        .label = base_label
                    });
                }
            } else {
                for (const auto& targets : enumerate_legal_target_sets_for_source_object(game, def.loyalty_ability.target_mask, needed_targets, object_id)) {
                    if (can_activate_loyalty_ability_with_targets(game, player_id, object_id, targets)) {
                        const auto primary = targets.empty() ? TargetRef{} : targets.front();
                        actions.push_back(LegalAction{
                            .kind = ActionKind::ActivateLoyaltyAbility,
                            .player = player_id,
                            .object = object_id,
                            .label = base_label + "->" + target_list_label(game, targets),
                            .target = primary,
                            .targets = targets
                        });
                    }
                }
            }
        }
    }


    return frontier;
}

std::vector<LegalAction> enumerate_legal_actions(const GameState& game, PlayerId player_id) {
    return enumerate_legal_action_frontier(game, player_id).actions;
}

LegalActionPage enumerate_legal_action_page(const GameState& game, PlayerId player_id, u64 cursor, u64 limit) {
    const u64 state_hash = canonical_state_hash(game);
    const ChoiceRequest request_context = choice_request_for_player_with_state_hash(game, player_id, state_hash);
    LegalActionPage empty{};
    empty.kind = request_context.kind;
    empty.chooser = player_id;
    empty.state_hash = state_hash;
    empty.choice_request_hash = request_context.action_set_hash;
    empty.cursor = cursor;
    empty.next_cursor = cursor;
    empty.requested_limit = limit;
    empty.effective_limit = limit == 0U ? 1U : limit;
    if (!valid_player_index(game, player_id) || player(game, player_id).lost) {
        finalize_legal_action_page(empty);
        return empty;
    }

    if (attack_declaration_choice_pending(game)) {
        if (game.active_player == player_id) {
            return make_attack_declaration_page(game, player_id, cursor, limit, state_hash, request_context.action_set_hash);
        }
        finalize_legal_action_page(empty);
        return empty;
    }

    if (any_blocker_declaration_choice_pending(game)) {
        if (blocker_declaration_choice_pending_for_player(game, player_id)) {
            return make_block_declaration_page(game, player_id, cursor, limit, state_hash, request_context.action_set_hash);
        }
        finalize_legal_action_page(empty);
        return empty;
    }

    if (damage_order_choice_pending(game)) {
        if (game.active_player == player_id) {
            return make_combat_damage_order_page(game, player_id, cursor, limit, state_hash, request_context.action_set_hash);
        }
        finalize_legal_action_page(empty);
        return empty;
    }

    const auto frontier = enumerate_legal_action_frontier(game, player_id);
    const ChoiceRequestKind kind = request_context.kind;
    LegalActionPageBuilder builder{kind, player_id, cursor, limit, state_hash, request_context.action_set_hash};
    for (const auto& action : frontier.actions) {
        if (!builder.accept(action)) {
            break;
        }
    }
    if (!frontier.complete) {
        builder.page.complete = false;
    }
    return builder.finish();
}

namespace {

[[nodiscard]] bool choice_actions_contain_kind(const std::vector<LegalAction>& actions, ActionKind kind) noexcept {
    return std::any_of(actions.begin(), actions.end(), [kind](const LegalAction& action) {
        return action.kind == kind;
    });
}

[[nodiscard]] ChoiceRequestKind classify_choice_request(const GameState& game, PlayerId player_id, const std::vector<LegalAction>& actions) noexcept {
    if (actions.empty()) {
        return ChoiceRequestKind::None;
    }
    if (player_id == game.priority_player && !game.pending_triggers.empty() &&
        choice_actions_contain_kind(actions, ActionKind::PutPendingTriggersOnStack)) {
        return ChoiceRequestKind::PendingTriggersToStack;
    }
    if (game.step == Step::DeclareAttackers && game.active_player == player_id &&
        choice_actions_contain_kind(actions, ActionKind::DeclareAttacker)) {
        return ChoiceRequestKind::DeclareAttackers;
    }
    if (game.step == Step::DeclareBlockers && choice_actions_contain_kind(actions, ActionKind::DeclareBlocker)) {
        return ChoiceRequestKind::DeclareBlockers;
    }
    if (game.step == Step::DeclareBlockers && choice_actions_contain_kind(actions, ActionKind::OrderCombatDamage)) {
        return ChoiceRequestKind::OrderCombatDamage;
    }
    if (player_id == game.priority_player) {
        return ChoiceRequestKind::PriorityAction;
    }
    return ChoiceRequestKind::PriorityAction;
}

} // namespace

std::vector<PlayerId> apnap_ordered_players(const GameState& game) {
    std::vector<PlayerId> order;
    if (game.players.empty()) {
        return order;
    }

    PlayerId start = game.active_player;
    if (!valid_player_index(game, start) || player(game, start).lost) {
        start = PlayerId{};
        for (const auto& candidate : game.players) {
            if (!candidate.lost) {
                start = candidate.id;
                break;
            }
        }
    }
    if (!start.valid()) {
        return order;
    }

    const u32 player_count = static_cast<u32>(game.players.size());
    order.reserve(player_count);
    for (u32 offset = 0; offset < player_count; ++offset) {
        const u32 candidate_value = ((start.value - 1U + offset) % player_count) + 1U;
        const PlayerId candidate{candidate_value};
        if (valid_player_index(game, candidate) && !player(game, candidate).lost) {
            order.push_back(candidate);
        }
    }
    return order;
}

namespace {

[[nodiscard]] ChoiceRequest choice_request_for_player_with_state_hash(const GameState& game,
                                                                       PlayerId player_id,
                                                                       u64 state_hash) {
    ChoiceRequest request{};
    request.chooser = player_id;
    request.state_hash = state_hash;
    if (!valid_player_index(game, player_id) || player(game, player_id).lost) {
        request.kind = ChoiceRequestKind::None;
        request.action_set_hash = choice_request_hash(request);
        return request;
    }
    auto frontier = enumerate_legal_action_frontier(game, player_id);
    request.action_frontier_complete = frontier.complete;
    request.action_generation_limit = frontier.generation_limit;
    request.actions = std::move(frontier.actions);
    request.kind = classify_choice_request(game, player_id, request.actions);
    request.required = request.kind == ChoiceRequestKind::PendingTriggersToStack ||
                       request.kind == ChoiceRequestKind::DeclareAttackers ||
                       request.kind == ChoiceRequestKind::DeclareBlockers ||
                       request.kind == ChoiceRequestKind::OrderCombatDamage;
    request.action_set_hash = choice_request_hash(request);
    return request;
}

[[nodiscard]] ChoiceRequestQueue choice_request_queue_with_state_hash(const GameState& game, u64 state_hash) {
    ChoiceRequestQueue queue{};
    queue.state_hash = state_hash;
    const auto order = apnap_ordered_players(game);
    queue.requests.reserve(order.size());
    for (const auto player_id : order) {
        auto request = choice_request_for_player_with_state_hash(game, player_id, state_hash);
        if (!request.actions.empty()) {
            queue.requests.push_back(std::move(request));
        }
    }
    queue.queue_hash = choice_request_queue_hash(queue);
    return queue;
}

} // namespace

ChoiceRequest choice_request_for_player(const GameState& game, PlayerId player_id) {
    return choice_request_for_player_with_state_hash(game, player_id, canonical_state_hash(game));
}

ChoiceRequestQueue choice_request_queue(const GameState& game) {
    return choice_request_queue_with_state_hash(game, canonical_state_hash(game));
}

ChoiceRequest current_choice_request(const GameState& game) {
    auto queue = choice_request_queue(game);
    if (!queue.requests.empty()) {
        return queue.requests.front();
    }
    ChoiceRequest none{};
    none.state_hash = queue.state_hash;
    none.action_set_hash = choice_request_hash(none);
    return none;
}

namespace {

[[nodiscard]] bool legal_action_fields_match(const LegalAction& candidate, const LegalAction& action) {
    const auto requested_targets = action_target_vector(action);
    const bool mana_index_matches = candidate.mana_ability_index == action.mana_ability_index ||
        (action.kind == ActionKind::ActivateTapManaAbility && action.mana_ability_index == 0U && candidate.mana_ability_index == 1U);
    const bool trigger_order_matches = candidate.trigger_order == action.trigger_order ||
        (action.kind == ActionKind::PutPendingTriggersOnStack && action.trigger_order.empty());
    return candidate.kind == action.kind && candidate.player == action.player &&
           candidate.object == action.object && action_target_vector(candidate) == requested_targets &&
           candidate.mode_index == action.mode_index && candidate.ability_index == action.ability_index &&
           mana_index_matches && trigger_order_matches;
}

[[nodiscard]] bool choice_request_contains_action(const ChoiceRequest& request, const LegalAction& action) {
    return std::any_of(request.actions.begin(), request.actions.end(), [&](const LegalAction& candidate) {
        return legal_action_fields_match(candidate, action);
    });
}

[[nodiscard]] bool directly_validate_unlisted_frontier_action(const GameState& game,
                                                              const ChoiceRequest& request,
                                                              const LegalAction& action) {
    if (request.action_frontier_complete || request.chooser != action.player) {
        return false;
    }

    switch (request.kind) {
        case ChoiceRequestKind::DeclareAttackers: {
            if (action.kind != ActionKind::DeclareAttacker) {
                return false;
            }
            const auto assignments = attack_assignments_from_action(action);
            const auto canonical = make_declare_attackers_action(action.player, assignments);
            return legal_action_fields_match(canonical, action) &&
                   can_declare_attackers(game, action.player, assignments);
        }
        case ChoiceRequestKind::DeclareBlockers: {
            if (action.kind != ActionKind::DeclareBlocker) {
                return false;
            }
            const auto assignments = block_assignments_from_action(action);
            const auto canonical = make_declare_blockers_action(action.player, assignments);
            return legal_action_fields_match(canonical, action) &&
                   can_declare_blockers(game, action.player, assignments);
        }
        case ChoiceRequestKind::OrderCombatDamage: {
            if (action.kind != ActionKind::OrderCombatDamage) {
                return false;
            }
            const auto blocker_order = combat_damage_order_from_action(action);
            const auto canonical = make_order_combat_damage_action(action.player, action.object, blocker_order);
            return legal_action_fields_match(canonical, action) &&
                   can_order_combat_damage(game, action.player, action.object, blocker_order);
        }
        case ChoiceRequestKind::PendingTriggersToStack:
            return action.kind == ActionKind::PutPendingTriggersOnStack &&
                   action.object.value == 0U && action.mode_index == 0U && action.ability_index == 0U &&
                   action.mana_ability_index == 0U && action_target_vector(action).empty() &&
                   valid_pending_trigger_order(game, action.trigger_order);
        case ChoiceRequestKind::None:
        case ChoiceRequestKind::PriorityAction:
        case ChoiceRequestKind::Count:
            return false;
    }
    return false;
}

[[nodiscard]] LegalActionValidation validate_action_for_choice_request(const GameState& game,
                                                                     const ChoiceRequest& request,
                                                                     const LegalAction& action) {
    LegalActionValidation validation{};
    validation.choice_kind = request.kind;
    validation.choice_required = request.required;
    validation.action_frontier_complete = request.action_frontier_complete;
    validation.action_generation_limit = request.action_generation_limit;
    validation.action_count = static_cast<u64>(request.actions.size());
    validation.choice_request_hash = request.action_set_hash;

    if (choice_request_contains_action(request, action)) {
        validation.legal = true;
        validation.source = LegalActionValidationSource::OfferedAction;
        return validation;
    }
    if (directly_validate_unlisted_frontier_action(game, request, action)) {
        validation.legal = true;
        validation.source = LegalActionValidationSource::DirectDomainValidation;
        return validation;
    }
    return validation;
}


} // namespace

LegalActionPageLocation locate_legal_action_page(const GameState& game, const LegalAction& action, u64 page_limit) {
    LegalActionPageLocation location{};
    location.chooser = action.player;
    location.requested_page_limit = page_limit;
    location.effective_page_limit = page_limit == 0U ? 1U : page_limit;
    location.action_hash = legal_action_hash(action);
    auto finalize_location = [&location]() -> LegalActionPageLocation {
        location.location_hash = legal_action_page_location_hash(location);
        return location;
    };

    u64 cursor = 0U;
    while (true) {
        const auto page = enumerate_legal_action_page(game, action.player, cursor, location.effective_page_limit);
        ++location.scanned_pages;
        location.page_schema_version = page.schema_version;
        location.kind = page.kind;
        location.chooser = page.chooser;
        location.page_state_hash = page.state_hash;
        location.page_choice_request_hash = page.choice_request_hash;
        location.page_cursor = page.cursor;
        location.next_cursor = page.next_cursor;
        location.actions_seen = page.actions_seen;
        location.page_complete = page.complete;
        location.total_actions_lower_bound = page.total_actions_lower_bound;
        location.total_actions_exact = page.total_actions_exact;
        location.remaining_actions_lower_bound = page.remaining_actions_lower_bound;
        location.page_hash = page.page_hash;

        for (std::size_t i = 0; i < page.actions.size(); ++i) {
            if (legal_action_fields_match(page.actions[i], action)) {
                location.found = true;
                location.index_in_page = static_cast<u64>(i);
                location.action_cursor = page.cursor + static_cast<u64>(i);
                return finalize_location();
            }
        }

        if (page.complete || page.next_cursor <= cursor) {
            return finalize_location();
        }
        cursor = page.next_cursor;
    }
}

LegalActionValidation validate_legal_action(const GameState& game, const LegalAction& action) {
    const ChoiceRequest request = choice_request_for_player(game, action.player);
    return validate_action_for_choice_request(game, request, action);
}

bool is_legal_action(const GameState& game, const LegalAction& action) {
    return validate_legal_action(game, action).legal;
}

namespace {

[[nodiscard]] const ChoiceRequest* find_choice_request_for_player(const ChoiceRequestQueue& queue, PlayerId player_id, u64* one_based_index = nullptr) noexcept {
    for (std::size_t i = 0; i < queue.requests.size(); ++i) {
        if (queue.requests[i].chooser == player_id) {
            if (one_based_index != nullptr) {
                *one_based_index = static_cast<u64>(i + 1U);
            }
            return &queue.requests[i];
        }
    }
    if (one_based_index != nullptr) {
        *one_based_index = 0;
    }
    return nullptr;
}

[[nodiscard]] ChoiceQueueLocation make_choice_queue_location(const ChoiceRequestQueue& queue,
                                                            const ChoiceRequest* request,
                                                            u64 one_based_index,
                                                            const LegalAction& action,
                                                            u64 action_hash) noexcept {
    ChoiceQueueLocation location{};
    location.found = request != nullptr && one_based_index != 0U;
    location.state_hash = queue.state_hash;
    location.queue_hash = queue.queue_hash;
    location.queue_index = one_based_index;
    location.queue_size = static_cast<u64>(queue.requests.size());
    location.chooser = action.player;
    location.action_hash = action_hash;
    if (request != nullptr) {
        location.request_kind = request->kind;
        location.chooser = request->chooser;
        location.request_required = request->required;
        location.action_frontier_complete = request->action_frontier_complete;
        location.action_generation_limit = request->action_generation_limit;
        location.choice_request_hash = request->action_set_hash;
        location.choice_action_count = static_cast<u64>(request->actions.size());
    }
    location.location_hash = choice_queue_location_hash(location);
    return location;
}

[[nodiscard]] bool queue_location_matches_trace(const ActionTraceEntry& entry, const ChoiceQueueLocation& actual) noexcept {
    return actual.location_hash == entry.expected_choice_queue_location_hash &&
           actual.found == entry.expected_choice_queue_location_found &&
           actual.schema_version == entry.expected_choice_queue_location_schema_version &&
           actual.queue_hash == entry.expected_choice_queue_hash &&
           actual.queue_index == entry.expected_choice_queue_index &&
           actual.queue_size == entry.expected_choice_queue_size &&
           actual.request_kind == entry.expected_choice_kind &&
           actual.chooser == entry.action.player &&
           actual.request_required == entry.expected_choice_required &&
           actual.action_frontier_complete == entry.expected_choice_action_frontier_complete &&
           actual.action_generation_limit == entry.expected_choice_action_generation_limit &&
           actual.choice_request_hash == entry.expected_choice_request_hash &&
           actual.choice_action_count == entry.expected_choice_action_count &&
           actual.action_hash == (entry.expected_action_hash == 0U ? legal_action_hash(entry.action) : entry.expected_action_hash);
}

[[nodiscard]] u64 choice_page_location_limit_for_request(const ChoiceRequest& request) noexcept {
    return request.action_generation_limit == 0U ? 128U : request.action_generation_limit;
}

[[nodiscard]] LegalActionPageLocation trace_expected_page_location(const ActionTraceEntry& entry) noexcept {
    LegalActionPageLocation location{};
    location.found = entry.expected_choice_page_location_found;
    location.page_schema_version = entry.expected_choice_page_schema_version;
    location.kind = entry.expected_choice_kind;
    location.chooser = entry.action.player;
    location.page_state_hash = entry.expected_choice_page_state_hash;
    location.page_choice_request_hash = entry.expected_choice_page_choice_request_hash;
    location.requested_page_limit = entry.expected_choice_page_requested_limit;
    location.effective_page_limit = entry.expected_choice_page_effective_limit;
    location.page_cursor = entry.expected_choice_page_cursor;
    location.action_cursor = entry.expected_choice_action_cursor;
    location.index_in_page = entry.expected_choice_page_index;
    location.next_cursor = entry.expected_choice_page_next_cursor;
    location.actions_seen = entry.expected_choice_page_actions_seen;
    location.scanned_pages = entry.expected_choice_page_scanned_pages;
    location.page_complete = entry.expected_choice_page_complete;
    location.total_actions_lower_bound = entry.expected_choice_page_total_actions_lower_bound;
    location.total_actions_exact = entry.expected_choice_page_total_actions_exact;
    location.remaining_actions_lower_bound = entry.expected_choice_page_remaining_actions_lower_bound;
    location.page_hash = entry.expected_choice_page_hash;
    location.action_hash = entry.expected_action_hash == 0U ? legal_action_hash(entry.action) : entry.expected_action_hash;
    location.location_hash = entry.expected_choice_page_location_hash;
    return location;
}

[[nodiscard]] bool page_location_matches_trace(const ActionTraceEntry& entry, const LegalActionPageLocation& actual) noexcept {
    return entry.expected_choice_page_location_found == actual.found &&
           entry.expected_choice_kind == actual.kind &&
           entry.action.player == actual.chooser &&
           (entry.expected_choice_page_schema_version == 0U || entry.expected_choice_page_schema_version == actual.page_schema_version) &&
           (!entry.expected_choice_page_context_present ||
            (entry.expected_choice_page_state_hash == actual.page_state_hash &&
             entry.expected_choice_page_choice_request_hash == actual.page_choice_request_hash)) &&
           entry.expected_choice_page_requested_limit == actual.requested_page_limit &&
           entry.expected_choice_page_effective_limit == actual.effective_page_limit &&
           entry.expected_choice_page_cursor == actual.page_cursor &&
           entry.expected_choice_action_cursor == actual.action_cursor &&
           entry.expected_choice_page_index == actual.index_in_page &&
           entry.expected_choice_page_next_cursor == actual.next_cursor &&
           entry.expected_choice_page_actions_seen == actual.actions_seen &&
           entry.expected_choice_page_scanned_pages == actual.scanned_pages &&
           entry.expected_choice_page_complete == actual.page_complete &&
           (!entry.expected_choice_page_count_present ||
            (entry.expected_choice_page_total_actions_lower_bound == actual.total_actions_lower_bound &&
             entry.expected_choice_page_total_actions_exact == actual.total_actions_exact &&
             entry.expected_choice_page_remaining_actions_lower_bound == actual.remaining_actions_lower_bound)) &&
           (entry.expected_choice_page_hash == 0U || entry.expected_choice_page_hash == actual.page_hash) &&
           (entry.expected_choice_page_location_hash == 0U || entry.expected_choice_page_location_hash == actual.location_hash);
}

[[nodiscard]] bool transition_receipt_matches_result(const ActionReceiptRecord& receipt, const TransitionResult& result) noexcept {
    return result.has_transition_checkpoint_seals() &&
           receipt.receipt_index == result.action_receipts_after &&
           receipt.receipt_index == result.action_receipts_before + 1U &&
           receipt.kind == result.action.kind &&
           receipt.player == result.action.player &&
           receipt.object == result.action.object &&
           receipt.targets == action_target_vector(result.action) &&
           receipt.mode_index == result.action.mode_index &&
           receipt.ability_index == result.action.ability_index &&
           receipt.mana_ability_index == result.action.mana_ability_index &&
           receipt.action_schema_version == result.action_schema_version &&
           receipt.action_hash == result.action_hash &&
           receipt.action_hash == legal_action_hash(result.action) &&
           receipt.state_schema_version == result.state_schema_version &&
           receipt.state_hash_before == result.state_hash_before &&
           receipt.state_hash_after == result.state_hash_after &&
           receipt.journal_hash_before == result.journal_hash_before &&
           receipt.journal_hash_after == result.journal_hash_after_action &&
           receipt.journal_hash_after_action == result.journal_hash_after_action &&
           receipt.journal_entries_before == result.journal_entries_before &&
           receipt.journal_entries_after == result.journal_entries_after_action &&
           receipt.journal_entries_after_action == result.journal_entries_after_action &&
           receipt.journal_entries_after_action + 1U == result.journal_entries_after &&
           receipt.has_post_action_journal_seal() &&
           receipt.next_event_sequence_before == result.next_event_sequence_before &&
           receipt.next_event_sequence_after == result.next_event_sequence_after &&
           receipt.legal_before == result.legal_before &&
           receipt.applied == result.applied &&
           receipt.choice_kind == result.choice_request.kind &&
           receipt.choice_request_schema_version == result.choice_request.schema_version &&
           receipt.choice_request_hash == result.choice_request.action_set_hash &&
           receipt.choice_action_count == static_cast<u64>(result.choice_request.actions.size()) &&
           receipt.choice_required == result.choice_request.required &&
           receipt.choice_action_frontier_complete == result.choice_request.action_frontier_complete &&
           receipt.choice_action_generation_limit == result.choice_request.action_generation_limit &&
           receipt.choice_validation_source == result.validation.source &&
           receipt.choice_page_location_checked == result.choice_page_location_checked &&
           receipt.choice_page_location_found == result.page_location.found &&
           receipt.choice_page_schema_version == result.page_location.page_schema_version &&
           receipt.choice_page_location_hash == result.page_location.location_hash &&
           receipt.choice_queue_schema_version == result.choice_queue.schema_version &&
           receipt.choice_queue_hash == result.choice_queue.queue_hash &&
           receipt.choice_queue_index == result.choice_queue_index &&
           receipt.choice_queue_size == static_cast<u64>(result.choice_queue.requests.size()) &&
           receipt.choice_queue_location_schema_version == result.queue_location.schema_version &&
           receipt.choice_queue_location_checked == result.choice_queue_location_checked &&
           receipt.choice_queue_location_found == result.choice_queue_location_found &&
           receipt.choice_queue_location_hash == (result.choice_queue_location_found ? result.queue_location.location_hash : 0U);
}

void capture_transition_before(TransitionResult& result, const GameState& game) {
    result.checkpoint_before = make_state_checkpoint_seal(game);
    result.checkpoint_after = result.checkpoint_before;
    result.state_hash_before = result.checkpoint_before.state_hash;
    result.state_hash_after = result.state_hash_before;
    result.journal_hash_before = result.checkpoint_before.journal_hash;
    result.journal_hash_after = result.journal_hash_before;
    result.journal_hash_after_action = result.journal_hash_before;
    result.journal_entries_before = result.checkpoint_before.journal_entries;
    result.journal_entries_after_action = result.journal_entries_before;
    result.journal_entries_after = result.journal_entries_before;
    result.action_receipts_before = result.checkpoint_before.action_receipts;
    result.action_receipts_after = result.action_receipts_before;
    result.next_event_sequence_before = result.checkpoint_before.next_event_sequence;
    result.next_event_sequence_after = result.next_event_sequence_before;
}

void capture_transition_after(TransitionResult& result, const GameState& game) {
    result.checkpoint_after = make_state_checkpoint_seal(game);
    result.state_hash_after = result.checkpoint_after.state_hash;
    result.journal_hash_after = result.checkpoint_after.journal_hash;
    result.journal_entries_after = result.checkpoint_after.journal_entries;
    result.action_receipts_after = result.checkpoint_after.action_receipts;
    result.next_event_sequence_after = result.checkpoint_after.next_event_sequence;
}

void attach_choice_context(TransitionResult& result, const GameState& game, PlayerId player_id) {
    result.choice_queue = choice_request_queue_with_state_hash(game, result.state_hash_before);
    result.choice_queue_index = 0U;
    const ChoiceRequest* queued_choice_request = find_choice_request_for_player(result.choice_queue, player_id, &result.choice_queue_index);
    if (queued_choice_request != nullptr) {
        result.choice_request = *queued_choice_request;
        return;
    }
    result.choice_request = choice_request_for_player_with_state_hash(game, player_id, result.state_hash_before);
}

struct ActionTransitionPreflight {
    ChoiceRequest choice_request{};
    ChoiceRequestQueue choice_queue{};
    u64 choice_queue_index = 0;
    LegalActionValidation validation{};
    LegalActionPageLocation page_location{};
    bool legal_before = false;
};

[[nodiscard]] ActionTransitionPreflight preflight_action_transition(const GameState& game,
                                                                    const LegalAction& action,
                                                                    u64 state_hash_before) {
    ActionTransitionPreflight preflight{};
    preflight.choice_queue = choice_request_queue_with_state_hash(game, state_hash_before);
    const ChoiceRequest* queued_choice_request = find_choice_request_for_player(preflight.choice_queue,
                                                                                action.player,
                                                                                &preflight.choice_queue_index);
    if (queued_choice_request != nullptr) {
        preflight.choice_request = *queued_choice_request;
    } else {
        preflight.choice_request = choice_request_for_player_with_state_hash(game, action.player, state_hash_before);
    }
    preflight.validation = validate_action_for_choice_request(game, preflight.choice_request, action);
    preflight.legal_before = preflight.validation.legal;
    if (preflight.legal_before) {
        preflight.page_location = locate_legal_action_page(game,
                                                           action,
                                                           choice_page_location_limit_for_request(preflight.choice_request));
    }
    return preflight;
}

void attach_preflight_to_result(TransitionResult& result, const ActionTransitionPreflight& preflight) {
    result.choice_request = preflight.choice_request;
    result.choice_queue = preflight.choice_queue;
    result.choice_queue_index = preflight.choice_queue_index;
    result.validation = preflight.validation;
    result.legal_before = preflight.legal_before;
    if (preflight.legal_before) {
        result.page_location = preflight.page_location;
        result.choice_page_location_checked = true;
    }
}


void hash_transition_checkpoint_seal(StableHasher& h, const StateCheckpointSeal& checkpoint) noexcept {
    hash_into(h, checkpoint.schema_version);
    hash_into(h, checkpoint.state_hash);
    hash_into(h, checkpoint.journal_hash);
    hash_into(h, checkpoint.journal_entries);
    hash_into(h, checkpoint.action_receipts);
    hash_into(h, checkpoint.object_count);
    hash_into(h, checkpoint.player_count);
    hash_into(h, checkpoint.stack_size);
    hash_into(h, checkpoint.rng_state);
    hash_into(h, checkpoint.next_zone_change_index);
    hash_into(h, checkpoint.next_event_sequence);
    hash_into(h, checkpoint.turn_number);
    h.add_u64(static_cast<u64>(checkpoint.step));
    hash_into(h, checkpoint.active_player);
    hash_into(h, checkpoint.priority_player);
    hash_into(h, checkpoint.journal_trimmed);
}

void hash_transition_choice_request(StableHasher& h, const ChoiceRequest& request) noexcept {
    hash_into(h, request.schema_version);
    h.add_u64(static_cast<u64>(request.kind));
    hash_into(h, request.chooser);
    hash_into(h, request.required);
    hash_into(h, request.action_frontier_complete);
    hash_into(h, request.action_generation_limit);
    hash_into(h, request.state_hash);
    hash_into(h, request.action_set_hash);
    hash_into(h, choice_request_hash(request));
    h.add_size(request.actions.size());
    for (const auto& action : request.actions) {
        hash_into(h, legal_action_hash(action));
    }
}

void hash_transition_choice_queue(StableHasher& h, const ChoiceRequestQueue& queue) noexcept {
    hash_into(h, queue.schema_version);
    hash_into(h, queue.state_hash);
    hash_into(h, queue.queue_hash);
    hash_into(h, choice_request_queue_hash(queue));
    h.add_size(queue.requests.size());
    for (const auto& request : queue.requests) {
        hash_transition_choice_request(h, request);
    }
}

void hash_transition_validation(StableHasher& h, const LegalActionValidation& validation) noexcept {
    hash_into(h, validation.legal);
    h.add_u64(static_cast<u64>(validation.source));
    h.add_u64(static_cast<u64>(validation.choice_kind));
    hash_into(h, validation.choice_required);
    hash_into(h, validation.action_frontier_complete);
    hash_into(h, validation.action_generation_limit);
    hash_into(h, validation.action_count);
    hash_into(h, validation.choice_request_hash);
}

void hash_transition_page_location(StableHasher& h, const LegalActionPageLocation& location) noexcept {
    hash_into(h, location.found);
    hash_into(h, location.page_schema_version);
    h.add_u64(static_cast<u64>(location.kind));
    hash_into(h, location.chooser);
    hash_into(h, location.page_state_hash);
    hash_into(h, location.page_choice_request_hash);
    hash_into(h, location.requested_page_limit);
    hash_into(h, location.effective_page_limit);
    hash_into(h, location.page_cursor);
    hash_into(h, location.action_cursor);
    hash_into(h, location.index_in_page);
    hash_into(h, location.next_cursor);
    hash_into(h, location.actions_seen);
    hash_into(h, location.scanned_pages);
    hash_into(h, location.page_complete);
    hash_into(h, location.total_actions_lower_bound);
    hash_into(h, location.total_actions_exact);
    hash_into(h, location.remaining_actions_lower_bound);
    hash_into(h, location.page_hash);
    hash_into(h, location.action_hash);
    hash_into(h, location.location_hash);
    hash_into(h, legal_action_page_location_hash(location));
}

void hash_transition_queue_location(StableHasher& h, const ChoiceQueueLocation& location) noexcept {
    hash_into(h, location.found);
    hash_into(h, location.schema_version);
    hash_into(h, location.state_hash);
    hash_into(h, location.queue_hash);
    hash_into(h, location.queue_index);
    hash_into(h, location.queue_size);
    h.add_u64(static_cast<u64>(location.request_kind));
    hash_into(h, location.chooser);
    hash_into(h, location.request_required);
    hash_into(h, location.action_frontier_complete);
    hash_into(h, location.action_generation_limit);
    hash_into(h, location.choice_request_hash);
    hash_into(h, location.choice_action_count);
    hash_into(h, location.action_hash);
    hash_into(h, location.location_hash);
    hash_into(h, choice_queue_location_hash(location));
}

void seal_transition_result_preflight(TransitionResult& result) noexcept {
    result.transition_preflight_schema_version = kTransitionPreflightSealSchemaVersion;
    result.transition_preflight_hash = 0U;
    result.transition_preflight_hash = transition_result_preflight_hash(result);
}

void seal_transition_result_boundary(TransitionResult& result) noexcept {
    result.transition_boundary_schema_version = kTransitionBoundarySealSchemaVersion;
    result.transition_boundary_hash = 0U;
    result.transition_boundary_hash = transition_result_boundary_hash(result);
}

[[nodiscard]] bool apply_legal_action_mutation(GameState& game, const LegalAction& action) {
    switch (action.kind) {
        case ActionKind::PassPriority:
            pass_priority(game);
            return true;
        case ActionKind::CastSpellFromHandPaid:
            if (action.mode_index != 0U) {
                return cast_from_hand_to_stack_paying_mana_with_mode_and_targets(game, action.player, action.object, action.mode_index, action_target_vector(action));
            }
            return cast_from_hand_to_stack_paying_mana_with_targets(game, action.player, action.object, action_target_vector(action));
        case ActionKind::PlayLand:
            return play_land_from_hand(game, action.player, action.object);
        case ActionKind::ActivateTapManaAbility:
            tap_permanent_for_mana(game, action.player, action.object);
            return true;
        case ActionKind::ActivateManaAbility:
            return activate_mana_ability(game, action.player, action.object, action.mana_ability_index == 0U ? 1U : action.mana_ability_index);
        case ActionKind::ActivateActivatedAbility:
            return activate_activated_ability_with_targets(game, action.player, action.object, action.ability_index, action_target_vector(action));
        case ActionKind::ActivateLoyaltyAbility:
            return activate_loyalty_ability_with_targets(game, action.player, action.object, action_target_vector(action));
        case ActionKind::DeclareAttacker:
            return declare_attackers(game, action.player, attack_assignments_from_action(action));
        case ActionKind::DeclareBlocker:
            return declare_blockers(game, action.player, block_assignments_from_action(action));
        case ActionKind::OrderCombatDamage:
            return order_combat_damage(game, action.player, action.object, combat_damage_order_from_action(action));
        case ActionKind::PutPendingTriggersOnStack:
            return put_pending_triggers_on_stack(game, action.trigger_order);
        case ActionKind::Count:
            return false;
    }
    return false;
}

} // namespace

void append_action_receipt(GameState& game,
                           const LegalAction& action,
                           const ChoiceRequest& choice_request,
                           const ChoiceRequestQueue& choice_queue,
                           u64 choice_queue_index,
                           u64 state_hash_before,
                           u64 journal_hash_before,
                           u64 journal_entries_before,
                           u64 next_event_sequence_before,
                           const LegalActionPageLocation& page_location,
                           bool legal_before,
                           LegalActionValidationSource validation_source,
                           bool applied);

std::uint64_t transition_result_preflight_hash(const TransitionResult& result) noexcept {
    StableHasher h;
    h.add_string("MTGSim.TransitionPreflightSeal.v1");
    hash_into(h, result.transition_preflight_schema_version);
    hash_transition_checkpoint_seal(h, result.checkpoint_before);
    hash_into(h, result.state_schema_version);
    hash_into(h, result.state_hash_before);
    hash_into(h, result.journal_hash_before);
    hash_into(h, result.journal_entries_before);
    hash_into(h, result.action_receipts_before);
    hash_into(h, result.next_event_sequence_before);

    hash_into(h, result.action_schema_version);
    hash_into(h, result.action_hash);
    hash_into(h, legal_action_hash(result.action));
    hash_transition_choice_request(h, result.choice_request);
    hash_transition_choice_queue(h, result.choice_queue);
    hash_into(h, result.choice_queue_index);
    hash_transition_validation(h, result.validation);
    hash_transition_page_location(h, result.page_location);
    hash_transition_queue_location(h, result.queue_location);
    hash_into(h, result.choice_page_location_checked);
    hash_into(h, result.choice_queue_location_checked);
    hash_into(h, result.choice_queue_location_found);
    hash_into(h, result.legal_before);
    return h.value();
}

std::uint64_t transition_result_boundary_hash(const TransitionResult& result) noexcept {
    StableHasher h;
    h.add_string("MTGSim.TransitionBoundarySeal.v1");
    hash_into(h, result.transition_boundary_schema_version);
    h.add_u64(static_cast<u64>(result.status));
    hash_into(h, result.reason);

    hash_into(h, result.action_schema_version);
    hash_into(h, result.action_hash);
    hash_into(h, legal_action_hash(result.action));
    hash_transition_choice_request(h, result.choice_request);
    hash_transition_choice_queue(h, result.choice_queue);
    hash_into(h, result.choice_queue_index);
    hash_transition_validation(h, result.validation);
    hash_transition_page_location(h, result.page_location);
    hash_transition_queue_location(h, result.queue_location);
    hash_into(h, result.choice_page_location_checked);
    hash_into(h, result.choice_queue_location_checked);
    hash_into(h, result.choice_queue_location_found);

    hash_into(h, result.state_schema_version);
    hash_transition_checkpoint_seal(h, result.checkpoint_before);
    hash_transition_checkpoint_seal(h, result.checkpoint_after);
    hash_into(h, result.state_hash_before);
    hash_into(h, result.state_hash_after);
    hash_into(h, result.journal_hash_before);
    hash_into(h, result.journal_hash_after);
    hash_into(h, result.journal_hash_after_action);
    hash_into(h, result.journal_entries_before);
    hash_into(h, result.journal_entries_after_action);
    hash_into(h, result.journal_entries_after);
    hash_into(h, result.action_receipts_before);
    hash_into(h, result.action_receipts_after);
    hash_into(h, result.next_event_sequence_before);
    hash_into(h, result.next_event_sequence_after);
    hash_into(h, result.causal_receipt_index);
    hash_into(h, result.action_receipt_schema_version);
    hash_into(h, result.causal_receipt_hash);
    hash_into(h, result.action_trace_entry_schema_version);
    hash_into(h, result.action_trace_entry_hash);
    hash_into(h, result.transition_preflight_schema_version);
    hash_into(h, result.transition_preflight_hash);
    hash_into(h, result.transition_trace_handoff_schema_version);
    hash_into(h, result.transition_trace_handoff_hash);

    hash_into(h, result.legal_before);
    hash_into(h, result.applied);
    hash_into(h, result.staged_commit_attempted);
    hash_into(h, result.staged_commit_applied);
    hash_into(h, result.staged_receipt_checked);
    hash_into(h, result.staged_receipt_consistent);
    hash_into(h, result.staged_adoption_guard_passed);
    hash_into(h, result.staged_commit_adopted);
    return h.value();
}

bool transition_result_matches_receipt(const TransitionResult& result, const ActionReceiptRecord& receipt) noexcept {
    return transition_receipt_matches_result(receipt, result);
}

ActionTraceEntry action_trace_entry_from_transition_result(const TransitionResult& result) {
    ActionTraceEntry entry{};
    entry.action = result.action;
    entry.expected_choice_kind = result.choice_request.kind;
    entry.expected_choice_request_schema_version = result.choice_request.schema_version;
    entry.expected_choice_request_hash = result.choice_request.action_set_hash;
    entry.expected_choice_action_count = static_cast<u64>(result.choice_request.actions.size());
    entry.expected_choice_required = result.choice_request.required;
    entry.expected_choice_action_frontier_complete = result.choice_request.action_frontier_complete;
    entry.expected_choice_action_generation_limit = result.choice_request.action_generation_limit;
    entry.expected_choice_validation_source = result.validation.source;
    entry.expected_choice_validation_source_present = true;
    entry.expected_choice_page_location_present = result.choice_page_location_checked || result.page_location.location_hash != 0U;
    entry.expected_choice_page_location_found = result.page_location.found;
    entry.expected_choice_page_location_checked = result.choice_page_location_checked;
    entry.expected_choice_page_schema_version = result.page_location.page_schema_version;
    entry.expected_choice_page_context_present = true;
    entry.expected_choice_page_state_hash = result.page_location.page_state_hash;
    entry.expected_choice_page_choice_request_hash = result.page_location.page_choice_request_hash;
    entry.expected_choice_page_requested_limit = result.page_location.requested_page_limit;
    entry.expected_choice_page_effective_limit = result.page_location.effective_page_limit;
    entry.expected_choice_page_cursor = result.page_location.page_cursor;
    entry.expected_choice_action_cursor = result.page_location.action_cursor;
    entry.expected_choice_page_index = result.page_location.index_in_page;
    entry.expected_choice_page_next_cursor = result.page_location.next_cursor;
    entry.expected_choice_page_actions_seen = result.page_location.actions_seen;
    entry.expected_choice_page_scanned_pages = result.page_location.scanned_pages;
    entry.expected_choice_page_complete = result.page_location.page_complete;
    entry.expected_choice_page_count_present = entry.expected_choice_page_location_present;
    entry.expected_choice_page_total_actions_lower_bound = result.page_location.total_actions_lower_bound;
    entry.expected_choice_page_total_actions_exact = result.page_location.total_actions_exact;
    entry.expected_choice_page_remaining_actions_lower_bound = result.page_location.remaining_actions_lower_bound;
    entry.expected_choice_page_hash = result.page_location.page_hash;
    entry.expected_choice_page_location_hash = result.page_location.location_hash;
    entry.expected_choice_queue_schema_version = result.choice_queue.schema_version;
    entry.expected_choice_queue_hash = result.choice_queue.queue_hash;
    entry.expected_choice_queue_index = result.choice_queue_index;
    entry.expected_choice_queue_size = static_cast<u64>(result.choice_queue.requests.size());
    entry.expected_choice_queue_location_schema_version = result.queue_location.schema_version;
    entry.expected_choice_queue_location_found = result.choice_queue_location_found;
    entry.expected_choice_queue_location_checked = result.choice_queue_location_checked;
    entry.expected_choice_queue_location_hash = result.choice_queue_location_found ? result.queue_location.location_hash : 0U;
    entry.expected_action_schema_version = result.action_schema_version;
    entry.expected_action_hash = result.action_hash;
    entry.expected_state_schema_version = result.state_schema_version;
    entry.expected_state_hash_before = result.state_hash_before;
    entry.expected_state_hash_after = result.state_hash_after;
    entry.expected_applied = result.applied;
    return entry;
}

bool transition_result_matches_action_trace_entry(const TransitionResult& result, const ActionTraceEntry& entry) noexcept {
    return legal_action_hash(entry.action) == result.action_hash &&
           entry.expected_choice_kind == result.choice_request.kind &&
           entry.expected_choice_request_schema_version == result.choice_request.schema_version &&
           entry.expected_choice_request_hash == result.choice_request.action_set_hash &&
           entry.expected_choice_action_count == static_cast<u64>(result.choice_request.actions.size()) &&
           entry.expected_choice_required == result.choice_request.required &&
           entry.expected_choice_action_frontier_complete == result.choice_request.action_frontier_complete &&
           entry.expected_choice_action_generation_limit == result.choice_request.action_generation_limit &&
           entry.expected_choice_validation_source == result.validation.source &&
           entry.expected_choice_validation_source_present &&
           entry.expected_choice_page_location_present == (result.choice_page_location_checked || result.page_location.location_hash != 0U) &&
           entry.expected_choice_page_location_found == result.page_location.found &&
           entry.expected_choice_page_location_checked == result.choice_page_location_checked &&
           entry.expected_choice_page_schema_version == result.page_location.page_schema_version &&
           entry.expected_choice_page_context_present &&
           entry.expected_choice_page_state_hash == result.page_location.page_state_hash &&
           entry.expected_choice_page_choice_request_hash == result.page_location.page_choice_request_hash &&
           entry.expected_choice_page_requested_limit == result.page_location.requested_page_limit &&
           entry.expected_choice_page_effective_limit == result.page_location.effective_page_limit &&
           entry.expected_choice_page_cursor == result.page_location.page_cursor &&
           entry.expected_choice_action_cursor == result.page_location.action_cursor &&
           entry.expected_choice_page_index == result.page_location.index_in_page &&
           entry.expected_choice_page_next_cursor == result.page_location.next_cursor &&
           entry.expected_choice_page_actions_seen == result.page_location.actions_seen &&
           entry.expected_choice_page_scanned_pages == result.page_location.scanned_pages &&
           entry.expected_choice_page_complete == result.page_location.page_complete &&
           entry.expected_choice_page_count_present == entry.expected_choice_page_location_present &&
           entry.expected_choice_page_total_actions_lower_bound == result.page_location.total_actions_lower_bound &&
           entry.expected_choice_page_total_actions_exact == result.page_location.total_actions_exact &&
           entry.expected_choice_page_remaining_actions_lower_bound == result.page_location.remaining_actions_lower_bound &&
           entry.expected_choice_page_hash == result.page_location.page_hash &&
           entry.expected_choice_page_location_hash == result.page_location.location_hash &&
           entry.expected_choice_queue_schema_version == result.choice_queue.schema_version &&
           entry.expected_choice_queue_hash == result.choice_queue.queue_hash &&
           entry.expected_choice_queue_index == result.choice_queue_index &&
           entry.expected_choice_queue_size == static_cast<u64>(result.choice_queue.requests.size()) &&
           entry.expected_choice_queue_location_schema_version == result.queue_location.schema_version &&
           entry.expected_choice_queue_location_found == result.choice_queue_location_found &&
           entry.expected_choice_queue_location_checked == result.choice_queue_location_checked &&
           entry.expected_choice_queue_location_hash == (result.choice_queue_location_found ? result.queue_location.location_hash : 0U) &&
           entry.expected_action_schema_version == result.action_schema_version &&
           entry.expected_action_hash == result.action_hash &&
           entry.expected_state_schema_version == result.state_schema_version &&
           entry.expected_state_hash_before == result.state_hash_before &&
           entry.expected_state_hash_after == result.state_hash_after &&
           entry.expected_applied == result.applied;
}

std::uint64_t transition_result_trace_entry_hash(const TransitionResult& result) noexcept {
    return action_trace_entry_hash(action_trace_entry_from_transition_result(result));
}

std::uint64_t transition_result_trace_handoff_hash(const TransitionResult& result) noexcept {
    StableHasher h;
    h.add_string("MTGSim.TransitionTraceHandoffSeal.v1");
    hash_into(h, result.transition_trace_handoff_schema_version);
    h.add_u64(static_cast<u64>(result.status));
    hash_into(h, result.action_receipt_schema_version);
    hash_into(h, result.causal_receipt_index);
    hash_into(h, result.causal_receipt_hash);
    hash_into(h, result.action_trace_entry_schema_version);
    hash_into(h, result.action_trace_entry_hash);
    hash_into(h, transition_result_trace_entry_hash(result));
    hash_into(h, result.transition_preflight_schema_version);
    hash_into(h, result.transition_preflight_hash);
    return h.value();
}

TransitionBoundaryVerifyResult check_transition_result_boundary(const TransitionResult& result, const GameState& before, const GameState& after) noexcept {
    TransitionBoundaryVerifyResult out{};
    out.expected_transition_boundary_hash = transition_result_boundary_hash(result);
    out.observed_transition_boundary_hash = result.transition_boundary_hash;
    out.expected_transition_preflight_hash = transition_result_preflight_hash(result);
    out.observed_transition_preflight_hash = result.transition_preflight_hash;
    out.expected_action_trace_entry_schema_version = result.committed() ? kActionTraceEntrySchemaVersion : 0U;
    out.observed_action_trace_entry_schema_version = result.action_trace_entry_schema_version;
    out.expected_action_trace_entry_hash = result.committed() ? transition_result_trace_entry_hash(result) : 0U;
    out.observed_action_trace_entry_hash = result.action_trace_entry_hash;
    out.expected_transition_trace_handoff_hash = result.committed() ? transition_result_trace_handoff_hash(result) : 0U;
    out.observed_transition_trace_handoff_hash = result.transition_trace_handoff_hash;
    out.observed_causal_receipt_hash = result.causal_receipt_hash;
    out.causal_receipt_index = result.causal_receipt_index;

    const auto fail = [&out](TransitionBoundaryFailureKind failure) noexcept {
        out.ok = false;
        out.failure = failure;
        return out;
    };
    const auto pass = [&out]() noexcept {
        out.ok = true;
        out.failure = TransitionBoundaryFailureKind::None;
        return out;
    };

    if (static_cast<u8>(result.status) >= static_cast<u8>(TransitionStatus::Count)) {
        return fail(TransitionBoundaryFailureKind::StatusInvalid);
    }
    if (!result.has_transition_boundary_seal()) {
        return fail(TransitionBoundaryFailureKind::BoundarySealMissing);
    }
    if (out.expected_transition_boundary_hash != result.transition_boundary_hash) {
        return fail(TransitionBoundaryFailureKind::BoundarySealMismatch);
    }
    if (!result.has_transition_preflight_seal()) {
        return fail(TransitionBoundaryFailureKind::PreflightSealMissing);
    }
    if (out.expected_transition_preflight_hash != result.transition_preflight_hash) {
        return fail(TransitionBoundaryFailureKind::PreflightSealMismatch);
    }
    if (!result.has_transition_checkpoint_seals()) {
        return fail(TransitionBoundaryFailureKind::CheckpointSealMismatch);
    }
    if (!verify_state_checkpoint_seal(before, result.checkpoint_before)) {
        return fail(TransitionBoundaryFailureKind::BeforeCheckpointMismatch);
    }
    if (!verify_state_checkpoint_seal(after, result.checkpoint_after)) {
        return fail(TransitionBoundaryFailureKind::AfterCheckpointMismatch);
    }

    if (result.need_choice()) {
        if (result.causal_receipt_index != 0U || result.causal_receipt_hash != 0U) {
            return fail(TransitionBoundaryFailureKind::NeedChoiceCausalReceipt);
        }
        if (!result.checkpoint_stable() ||
            !result.state_core_unchanged() ||
            !result.journal_unchanged() ||
            result.applied ||
            result.staged_commit_attempted ||
            result.staged_commit_adopted) {
            return fail(TransitionBoundaryFailureKind::NeedChoiceMutation);
        }
        if (result.choice_request.actions.empty()) {
            return fail(TransitionBoundaryFailureKind::NeedChoiceMissingActions);
        }
        return pass();
    }

    if (result.rejected()) {
        if (result.causal_receipt_index != 0U || result.causal_receipt_hash != 0U) {
            return fail(TransitionBoundaryFailureKind::RejectedCausalReceipt);
        }
        if (!result.rejected_with_checkpoint_stability() ||
            result.applied ||
            result.staged_commit_adopted) {
            return fail(TransitionBoundaryFailureKind::RejectedMutation);
        }
        return pass();
    }

    if (!result.committed_with_atomic_adoption_guard()) {
        return fail(TransitionBoundaryFailureKind::CommittedAtomicGuardMissing);
    }

    if (result.action_trace_entry_hash == 0U) {
        return fail(TransitionBoundaryFailureKind::TraceEntrySealMissing);
    }
    if (result.action_trace_entry_schema_version != kActionTraceEntrySchemaVersion ||
        out.expected_action_trace_entry_hash != result.action_trace_entry_hash) {
        return fail(TransitionBoundaryFailureKind::TraceEntrySealMismatch);
    }

    if (!result.has_transition_trace_handoff_seal()) {
        return fail(TransitionBoundaryFailureKind::TraceHandoffSealMissing);
    }
    if (out.expected_transition_trace_handoff_hash != result.transition_trace_handoff_hash) {
        return fail(TransitionBoundaryFailureKind::TraceHandoffSealMismatch);
    }

    if (result.action_receipts_after != static_cast<u64>(action_receipt_record_count(after)) ||
        result.action_receipts_after == 0U) {
        return fail(TransitionBoundaryFailureKind::ReceiptCountMismatch);
    }

    const auto* receipt = latest_action_receipt_record(after);
    if (receipt == nullptr) {
        return fail(TransitionBoundaryFailureKind::ReceiptMissing);
    }
    out.expected_causal_receipt_hash = action_receipt_hash(*receipt);
    if (receipt->receipt_index != result.causal_receipt_index) {
        return fail(TransitionBoundaryFailureKind::ReceiptIndexMismatch);
    }
    if (out.expected_causal_receipt_hash != result.causal_receipt_hash) {
        return fail(TransitionBoundaryFailureKind::ReceiptHashMismatch);
    }
    if (!transition_receipt_matches_result(*receipt, result)) {
        return fail(TransitionBoundaryFailureKind::ReceiptResultMismatch);
    }

    return pass();
}

bool verify_transition_result_boundary(const TransitionResult& result, const GameState& before, const GameState& after) noexcept {
    return check_transition_result_boundary(result, before, after).passed();
}

TransitionResult pending_transition_for_player(const GameState& game, PlayerId player_id) {
    TransitionResult result{};
    capture_transition_before(result, game);
    attach_choice_context(result, game, player_id);
    seal_transition_result_preflight(result);
    capture_transition_after(result, game);

    if (!result.choice_request.actions.empty()) {
        result.status = TransitionStatus::NeedChoice;
        result.reason = result.choice_request.required ? "required_choice_available" : "choice_available";
    } else {
        result.status = TransitionStatus::Rejected;
        result.reason = "no_choice_available";
    }
    seal_transition_result_boundary(result);
    return result;
}

TransitionResult commit_action_transition(GameState& game, const LegalAction& action) {
    const LegalAction transition_action = canonicalize_legal_action(action);
    TransitionResult result{};
    capture_transition_before(result, game);
    result.action = transition_action;
    result.action_schema_version = kLegalActionSchemaVersion;
    result.action_hash = legal_action_hash(transition_action);
    result.state_schema_version = kStateCoreSchemaVersion;

    const auto preflight = preflight_action_transition(game, transition_action, result.state_hash_before);
    attach_preflight_to_result(result, preflight);
    if (result.legal_before) {
        result.queue_location = make_choice_queue_location(result.choice_queue,
                                                           result.choice_queue_index != 0U ? &result.choice_request : nullptr,
                                                           result.choice_queue_index,
                                                           transition_action,
                                                           result.action_hash);
        result.choice_queue_location_checked = true;
        result.choice_queue_location_found = result.queue_location.found;
    }
    seal_transition_result_preflight(result);

    if (!result.legal_before) {
        result.status = TransitionStatus::Rejected;
        result.reason = "illegal_action";
        capture_transition_after(result, game);
        seal_transition_result_boundary(result);
        return result;
    }

    result.staged_commit_attempted = true;
    GameState staged_game = game;
    result.applied = apply_legal_action_mutation(staged_game, transition_action);
    result.staged_commit_applied = result.applied;
    if (!result.applied) {
        result.status = TransitionStatus::Rejected;
        result.reason = "commit_failed_without_adoption";
        capture_transition_after(result, game);
        seal_transition_result_boundary(result);
        return result;
    }

    result.journal_hash_after_action = journal_hash(staged_game);
    result.journal_entries_after_action = static_cast<u64>(journal_entry_count(staged_game));

    append_action_receipt(staged_game,
                          transition_action,
                          result.choice_request,
                          result.choice_queue,
                          result.choice_queue_index,
                          result.state_hash_before,
                          result.journal_hash_before,
                          result.journal_entries_before,
                          result.next_event_sequence_before,
                          result.page_location,
                          result.legal_before,
                          result.validation.source,
                          result.applied);
    capture_transition_after(result, staged_game);
    result.staged_receipt_checked = true;
    if (result.action_receipts_after == result.action_receipts_before + 1U) {
        const auto* receipt = latest_action_receipt_record(staged_game);
        if (receipt != nullptr) {
            result.action_receipt_schema_version = kActionReceiptRecordSchemaVersion;
            result.causal_receipt_hash = action_receipt_hash(*receipt);
            result.staged_receipt_consistent = transition_receipt_matches_result(*receipt, result);
            if (result.staged_receipt_consistent) {
                result.causal_receipt_index = receipt->receipt_index;
            }
        }
    }
    result.staged_adoption_guard_passed = result.staged_receipt_consistent &&
                                          result.has_checked_page_location() &&
                                          result.has_checked_queue_location();
    if (!result.staged_adoption_guard_passed) {
        result.status = TransitionStatus::Rejected;
        result.reason = "staged_receipt_guard_failed";
        result.causal_receipt_index = 0U;
        result.causal_receipt_hash = 0U;
        capture_transition_after(result, game);
        seal_transition_result_boundary(result);
        return result;
    }

    result.status = TransitionStatus::Committed;
    result.reason = "committed";
    result.staged_commit_adopted = true;
    result.action_trace_entry_schema_version = kActionTraceEntrySchemaVersion;
    result.action_trace_entry_hash = transition_result_trace_entry_hash(result);
    result.transition_trace_handoff_schema_version = kTransitionTraceHandoffSealSchemaVersion;
    result.transition_trace_handoff_hash = transition_result_trace_handoff_hash(result);
    seal_transition_result_boundary(result);
    game = std::move(staged_game);
    return result;
}

void append_action_receipt(GameState& game,
                           const LegalAction& action,
                           const ChoiceRequest& choice_request,
                           const ChoiceRequestQueue& choice_queue,
                           u64 choice_queue_index,
                           u64 state_hash_before,
                           u64 journal_hash_before,
                           u64 journal_entries_before,
                           u64 next_event_sequence_before,
                           const LegalActionPageLocation& page_location,
                           bool legal_before,
                           LegalActionValidationSource validation_source,
                           bool applied) {
    ActionReceiptRecord record{};
    record.receipt_index = static_cast<u64>(game.action_receipt_records.size() + 1U);
    record.kind = action.kind;
    record.player = action.player;
    record.object = action.object;
    record.targets = action_target_vector(action);
    record.mode_index = action.mode_index;
    record.ability_index = action.ability_index;
    record.mana_ability_index = action.mana_ability_index;
    record.trigger_order = action.trigger_order;
    record.choice_kind = choice_request.kind;
    record.choice_request_schema_version = choice_request.schema_version;
    record.choice_request_hash = choice_request.action_set_hash;
    record.choice_action_count = static_cast<u64>(choice_request.actions.size());
    record.choice_required = choice_request.required;
    record.choice_action_frontier_complete = choice_request.action_frontier_complete;
    record.choice_action_generation_limit = choice_request.action_generation_limit;
    record.choice_validation_source = validation_source;
    record.choice_page_location_found = page_location.found;
    record.choice_page_location_checked = legal_before;
    record.choice_page_schema_version = page_location.page_schema_version;
    record.choice_page_state_hash = page_location.page_state_hash;
    record.choice_page_choice_request_hash = page_location.page_choice_request_hash;
    record.choice_page_requested_limit = page_location.requested_page_limit;
    record.choice_page_effective_limit = page_location.effective_page_limit;
    record.choice_page_cursor = page_location.page_cursor;
    record.choice_action_cursor = page_location.action_cursor;
    record.choice_page_index = page_location.index_in_page;
    record.choice_page_next_cursor = page_location.next_cursor;
    record.choice_page_actions_seen = page_location.actions_seen;
    record.choice_page_scanned_pages = page_location.scanned_pages;
    record.choice_page_complete = page_location.page_complete;
    record.choice_page_total_actions_lower_bound = page_location.total_actions_lower_bound;
    record.choice_page_total_actions_exact = page_location.total_actions_exact;
    record.choice_page_remaining_actions_lower_bound = page_location.remaining_actions_lower_bound;
    record.choice_page_hash = page_location.page_hash;
    record.choice_page_location_hash = page_location.location_hash;
    record.choice_queue_schema_version = choice_queue.schema_version;
    record.choice_queue_hash = choice_queue.queue_hash;
    record.choice_queue_index = choice_queue_index;
    record.choice_queue_size = static_cast<u64>(choice_queue.requests.size());
    record.action_schema_version = kLegalActionSchemaVersion;
    record.action_hash = legal_action_hash(action);
    record.state_schema_version = kStateCoreSchemaVersion;
    const auto queue_location = make_choice_queue_location(choice_queue,
                                                           (legal_before && choice_queue_index != 0U) ? &choice_request : nullptr,
                                                           choice_queue_index,
                                                           action,
                                                           record.action_hash);
    record.choice_queue_location_schema_version = queue_location.schema_version;
    record.choice_queue_location_checked = legal_before;
    record.choice_queue_location_found = legal_before && queue_location.found;
    record.choice_queue_location_hash = record.choice_queue_location_found ? queue_location.location_hash : 0U;
    record.state_hash_before = state_hash_before;
    record.state_hash_after = canonical_state_hash(game);
    record.journal_hash_before = journal_hash_before;
    record.journal_hash_after = journal_hash(game);
    record.journal_hash_after_action = record.journal_hash_after;
    record.journal_entries_before = journal_entries_before;
    record.journal_entries_after = static_cast<u64>(journal_entry_count(game));
    record.journal_entries_after_action = record.journal_entries_after;
    record.next_event_sequence_before = next_event_sequence_before;
    record.next_event_sequence_after = game.next_event_sequence;
    record.legal_before = legal_before;
    record.applied = applied;
    game.action_receipt_records.push_back(std::move(record));
}

bool apply_action(GameState& game, const LegalAction& action) {
    const u64 state_hash_before = canonical_state_hash(game);
    const u64 journal_hash_before = journal_hash(game);
    const u64 journal_entries_before = static_cast<u64>(journal_entry_count(game));
    const u64 next_event_sequence_before = game.next_event_sequence;

    const auto preflight = preflight_action_transition(game, action, state_hash_before);
    if (!preflight.legal_before) {
        record_event(game, "illegal_action", std::string(to_string(action.kind)) + " by player#" + std::to_string(action.player.value));
        append_action_receipt(game,
                              action,
                              preflight.choice_request,
                              preflight.choice_queue,
                              preflight.choice_queue_index,
                              state_hash_before,
                              journal_hash_before,
                              journal_entries_before,
                              next_event_sequence_before,
                              preflight.page_location,
                              false,
                              preflight.validation.source,
                              false);
        return false;
    }

    const bool applied = apply_legal_action_mutation(game, action);

    append_action_receipt(game,
                          action,
                          preflight.choice_request,
                          preflight.choice_queue,
                          preflight.choice_queue_index,
                          state_hash_before,
                          journal_hash_before,
                          journal_entries_before,
                          next_event_sequence_before,
                          preflight.page_location,
                          preflight.legal_before,
                          preflight.validation.source,
                          applied);
    return applied;
}

ActionReplayResult replay_action_trace(GameState& game, const std::vector<ActionTraceEntry>& trace) {
    ActionReplayResult result{};
    for (std::size_t i = 0; i < trace.size(); ++i) {
        const auto& entry = trace[i];
        result.attempted = static_cast<u64>(i + 1U);
        result.mismatch_index = static_cast<u64>(i + 1U);

        const u64 action_hash = legal_action_hash(entry.action);
        if (entry.expected_action_schema_version != 0U && entry.expected_action_schema_version != kLegalActionSchemaVersion) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::ActionHashMismatch;
            result.expected_action_hash = entry.expected_action_hash;
            result.actual_action_hash = action_hash;
            result.expected_action_schema_version = entry.expected_action_schema_version;
            result.actual_action_schema_version = kLegalActionSchemaVersion;
            return result;
        }
        if (entry.expected_action_hash != 0U && entry.expected_action_hash != action_hash) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::ActionHashMismatch;
            result.expected_action_hash = entry.expected_action_hash;
            result.actual_action_hash = action_hash;
            result.expected_action_schema_version = entry.expected_action_schema_version;
            result.actual_action_schema_version = kLegalActionSchemaVersion;
            return result;
        }

        const u64 state_hash_before = canonical_state_hash(game);
        const ChoiceRequestQueue queue = choice_request_queue_with_state_hash(game, state_hash_before);
        u64 actual_choice_queue_index = 0;
        const ChoiceRequest* queued_request = find_choice_request_for_player(queue, entry.action.player, &actual_choice_queue_index);
        if (entry.expected_choice_queue_schema_version != 0U && entry.expected_choice_queue_schema_version != queue.schema_version) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::ChoiceQueueHashMismatch;
            result.expected_choice_queue_schema_version = entry.expected_choice_queue_schema_version;
            result.actual_choice_queue_schema_version = queue.schema_version;
            result.expected_choice_queue_hash = entry.expected_choice_queue_hash;
            result.actual_choice_queue_hash = queue.queue_hash;
            result.expected_choice_queue_index = entry.expected_choice_queue_index;
            result.actual_choice_queue_index = actual_choice_queue_index;
            result.expected_choice_queue_size = entry.expected_choice_queue_size;
            result.actual_choice_queue_size = static_cast<u64>(queue.requests.size());
            result.expected_choice_queue_location_schema_version = entry.expected_choice_queue_location_schema_version;
            result.actual_choice_queue_location_schema_version = kChoiceQueueLocationSchemaVersion;
            return result;
        }
        if (entry.expected_choice_queue_hash != 0U) {
            if (queue.queue_hash != entry.expected_choice_queue_hash ||
                actual_choice_queue_index != entry.expected_choice_queue_index ||
                static_cast<u64>(queue.requests.size()) != entry.expected_choice_queue_size) {
                result.ok = false;
                result.failure = ActionReplayFailureKind::ChoiceQueueHashMismatch;
                result.expected_choice_queue_schema_version = entry.expected_choice_queue_schema_version;
                result.actual_choice_queue_schema_version = queue.schema_version;
                result.expected_choice_queue_hash = entry.expected_choice_queue_hash;
                result.actual_choice_queue_hash = queue.queue_hash;
                result.expected_choice_queue_index = entry.expected_choice_queue_index;
                result.actual_choice_queue_index = actual_choice_queue_index;
                result.expected_choice_queue_size = entry.expected_choice_queue_size;
                result.actual_choice_queue_size = static_cast<u64>(queue.requests.size());
                result.expected_choice_queue_location_schema_version = entry.expected_choice_queue_location_schema_version;
                result.actual_choice_queue_location_schema_version = kChoiceQueueLocationSchemaVersion;
                return result;
            }
        }
        const ChoiceRequest fallback_request = queued_request == nullptr
            ? choice_request_for_player_with_state_hash(game, entry.action.player, state_hash_before)
            : ChoiceRequest{};
        const ChoiceRequest& request = queued_request == nullptr ? fallback_request : *queued_request;
        if (entry.expected_choice_request_schema_version != 0U && entry.expected_choice_request_schema_version != request.schema_version) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::ChoiceRequestHashMismatch;
            result.expected_choice_request_schema_version = entry.expected_choice_request_schema_version;
            result.actual_choice_request_schema_version = request.schema_version;
            result.expected_choice_request_hash = entry.expected_choice_request_hash;
            result.actual_choice_request_hash = request.action_set_hash;
            result.expected_choice_action_count = entry.expected_choice_action_count;
            result.actual_choice_action_count = static_cast<u64>(request.actions.size());
            result.expected_choice_kind = entry.expected_choice_kind;
            result.actual_choice_kind = request.kind;
            return result;
        }
        if (entry.expected_choice_request_hash != 0U) {
            if (request.action_set_hash != entry.expected_choice_request_hash ||
                static_cast<u64>(request.actions.size()) != entry.expected_choice_action_count ||
                request.kind != entry.expected_choice_kind ||
                (entry.expected_choice_validation_source_present &&
                 (request.action_frontier_complete != entry.expected_choice_action_frontier_complete ||
                  request.action_generation_limit != entry.expected_choice_action_generation_limit))) {
                result.ok = false;
                result.failure = ActionReplayFailureKind::ChoiceRequestHashMismatch;
                result.expected_choice_request_schema_version = entry.expected_choice_request_schema_version;
                result.actual_choice_request_schema_version = request.schema_version;
                result.expected_choice_request_hash = entry.expected_choice_request_hash;
                result.actual_choice_request_hash = request.action_set_hash;
                result.expected_choice_action_count = entry.expected_choice_action_count;
                result.actual_choice_action_count = static_cast<u64>(request.actions.size());
                result.expected_choice_kind = entry.expected_choice_kind;
                result.actual_choice_kind = request.kind;
                return result;
            }
        }

        if (entry.expected_choice_queue_location_checked || entry.expected_choice_queue_location_hash != 0U) {
            const auto actual_queue_location = make_choice_queue_location(queue, queued_request, actual_choice_queue_index, entry.action, action_hash);
            if (entry.expected_applied && entry.expected_choice_queue_location_hash != 0U && !entry.expected_choice_queue_location_checked) {
                result.ok = false;
                result.failure = ActionReplayFailureKind::ChoiceQueueHashMismatch;
                result.expected_choice_queue_schema_version = entry.expected_choice_queue_schema_version;
                result.actual_choice_queue_schema_version = queue.schema_version;
                result.expected_choice_queue_hash = entry.expected_choice_queue_hash;
                result.actual_choice_queue_hash = queue.queue_hash;
                result.expected_choice_queue_index = entry.expected_choice_queue_index;
                result.actual_choice_queue_index = actual_choice_queue_index;
                result.expected_choice_queue_size = entry.expected_choice_queue_size;
                result.actual_choice_queue_size = static_cast<u64>(queue.requests.size());
                result.expected_choice_queue_location_schema_version = entry.expected_choice_queue_location_schema_version;
                result.actual_choice_queue_location_schema_version = actual_queue_location.schema_version;
                result.expected_choice_queue_location_hash = entry.expected_choice_queue_location_hash;
                result.actual_choice_queue_location_hash = actual_queue_location.location_hash;
                return result;
            }
            if (!queue_location_matches_trace(entry, actual_queue_location)) {
                result.ok = false;
                result.failure = ActionReplayFailureKind::ChoiceQueueHashMismatch;
                result.expected_choice_queue_schema_version = entry.expected_choice_queue_schema_version;
                result.actual_choice_queue_schema_version = queue.schema_version;
                result.expected_choice_queue_hash = entry.expected_choice_queue_hash;
                result.actual_choice_queue_hash = queue.queue_hash;
                result.expected_choice_queue_index = entry.expected_choice_queue_index;
                result.actual_choice_queue_index = actual_choice_queue_index;
                result.expected_choice_queue_size = entry.expected_choice_queue_size;
                result.actual_choice_queue_size = static_cast<u64>(queue.requests.size());
                result.expected_choice_queue_location_schema_version = entry.expected_choice_queue_location_schema_version;
                result.actual_choice_queue_location_schema_version = actual_queue_location.schema_version;
                result.expected_choice_queue_location_hash = entry.expected_choice_queue_location_hash;
                result.actual_choice_queue_location_hash = actual_queue_location.location_hash;
                return result;
            }
        }

        if (entry.expected_choice_validation_source_present) {
            const LegalActionValidation validation = validate_action_for_choice_request(game, request, entry.action);
            if (validation.source != entry.expected_choice_validation_source) {
                result.ok = false;
                result.failure = ActionReplayFailureKind::ChoiceValidationSourceMismatch;
                result.expected_choice_validation_source = entry.expected_choice_validation_source;
                result.actual_choice_validation_source = validation.source;
                return result;
            }
        }

        if (entry.expected_choice_page_location_present) {
            if (entry.expected_applied && !entry.expected_choice_page_location_checked) {
                result.ok = false;
                result.failure = ActionReplayFailureKind::ChoicePageLocationMismatch;
                result.expected_choice_page_location = trace_expected_page_location(entry);
                result.actual_choice_page_location = locate_legal_action_page(game, entry.action, entry.expected_choice_page_requested_limit);
                return result;
            }
            if (entry.expected_choice_page_location_checked) {
                const auto actual_page_location = locate_legal_action_page(game, entry.action, entry.expected_choice_page_requested_limit);
                if (!page_location_matches_trace(entry, actual_page_location)) {
                    result.ok = false;
                    result.failure = ActionReplayFailureKind::ChoicePageLocationMismatch;
                    result.expected_choice_page_location = trace_expected_page_location(entry);
                    result.actual_choice_page_location = actual_page_location;
                    return result;
                }
            }
        }

        if (entry.expected_state_schema_version != 0U && entry.expected_state_schema_version != kStateCoreSchemaVersion) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::StateHashSchemaMismatch;
            result.expected_state_schema_version = entry.expected_state_schema_version;
            result.actual_state_schema_version = kStateCoreSchemaVersion;
            result.expected_state_hash = entry.expected_state_hash_before;
            result.actual_state_hash = state_hash_before;
            return result;
        }

        if (entry.expected_state_hash_before != 0U && entry.expected_state_hash_before != state_hash_before) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::StateHashBeforeMismatch;
            result.expected_state_hash = entry.expected_state_hash_before;
            result.actual_state_hash = state_hash_before;
            return result;
        }

        const bool applied = apply_action(game, entry.action);
        result.actual_applied = applied;
        result.expected_applied = entry.expected_applied;
        if (applied) {
            ++result.applied;
        }
        if (applied != entry.expected_applied) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::ApplyResultMismatch;
            return result;
        }

        const u64 state_hash_after = canonical_state_hash(game);
        if (entry.expected_state_hash_after != 0U && entry.expected_state_hash_after != state_hash_after) {
            result.ok = false;
            result.failure = ActionReplayFailureKind::StateHashAfterMismatch;
            result.expected_state_hash = entry.expected_state_hash_after;
            result.actual_state_hash = state_hash_after;
            return result;
        }
    }
    result.mismatch_index = 0;
    return result;
}

ActionReplayResult replay_action_trace_from_checkpoint(GameState& game, const StateCheckpointSeal& checkpoint, const std::vector<ActionTraceEntry>& trace) {
    ActionReplayResult result{};
    if (checkpoint.schema_version != kStateCheckpointSealSchemaVersion) {
        result.ok = false;
        result.failure = ActionReplayFailureKind::CheckpointSchemaMismatch;
        result.expected_checkpoint_schema_version = checkpoint.schema_version;
        result.actual_checkpoint_schema_version = kStateCheckpointSealSchemaVersion;
        result.expected_state_hash = checkpoint.state_hash;
        result.actual_state_hash = canonical_state_hash(game);
        result.expected_action_hash = checkpoint.journal_hash;
        result.actual_action_hash = journal_hash(game);
        result.mismatch_index = 0;
        return result;
    }
    if (!verify_state_checkpoint_seal(game, checkpoint)) {
        result.ok = false;
        result.failure = ActionReplayFailureKind::CheckpointHashMismatch;
        result.expected_state_hash = checkpoint.state_hash;
        result.actual_state_hash = canonical_state_hash(game);
        result.expected_action_hash = checkpoint.journal_hash;
        result.actual_action_hash = journal_hash(game);
        result.mismatch_index = 0;
        return result;
    }
    return replay_action_trace(game, trace);
}

PlayerId next_player_in_turn_order(const GameState& game, PlayerId from) {
    if (game.players.empty()) {
        return PlayerId{};
    }
    const u32 player_count = static_cast<u32>(game.players.size());
    u32 current = from.valid() ? from.value : 1U;
    for (u32 offset = 1; offset <= player_count; ++offset) {
        const u32 candidate = ((current - 1U + offset) % player_count) + 1U;
        if (!player(game, PlayerId{candidate}).lost) {
            return PlayerId{candidate};
        }
    }
    return PlayerId{};
}

std::uint32_t alive_player_count(const GameState& game) {
    return static_cast<u32>(std::count_if(game.players.begin(), game.players.end(), [](const PlayerState& p) {
        return !p.lost;
    }));
}

void pass_priority(GameState& game) {
    if (!game.priority_player.valid()) {
        return;
    }

    auto snapshot = capture_priority_transition_snapshot(game);
    if (!game.pending_triggers.empty()) {
        put_pending_triggers_on_stack(game);
        record_priority_transition(game, snapshot, PriorityTransitionOutcome::PendingTriggersPutOnStack);
        return;
    }

    ++game.consecutive_priority_passes;
    record_event(game, "pass_priority", player(game, game.priority_player).name);

    const u32 alive = alive_player_count(game);
    if (alive == 0U) {
        game.priority_player = PlayerId{};
        record_priority_transition(game, snapshot, PriorityTransitionOutcome::NoAlivePlayers);
        return;
    }
    if (game.consecutive_priority_passes >= alive) {
        if (!game.stack.empty()) {
            const auto resolution_records_before = game.stack_resolution_records.size();
            resolve_top_of_stack(game);
            const u32 resolution_record_index = game.stack_resolution_records.size() > resolution_records_before
                ? static_cast<u32>(game.stack_resolution_records.size())
                : 0U;
            record_priority_transition(game, snapshot, PriorityTransitionOutcome::StackResolved, resolution_record_index);
        } else {
            advance_step(game);
            record_priority_transition(game, snapshot, PriorityTransitionOutcome::StepAdvanced);
        }
        return;
    }
    game.priority_player = next_player_in_turn_order(game, game.priority_player);
    record_priority_transition(game, snapshot, PriorityTransitionOutcome::PriorityAdvanced);
}

void advance_step(GameState& game) {
    const Step previous = game.step;
    game.step = next_step_value(game.step);
    game.consecutive_priority_passes = 0;
    game.attackers_declared_this_step = false;
    game.combat_damage_assigned_this_step = false;
    game.blocker_declaration_complete_players.clear();

    if (previous == Step::EndOfCombat) {
        clear_combat_assignments(game);
    }

    if (previous == Step::Cleanup) {
        perform_cleanup(game);
        clear_all_mana_pools(game);
        game.active_player = next_player_in_turn_order(game, game.active_player);
        ++game.turn_number;
        if (game.active_player.valid()) {
            auto& active = player(game, game.active_player);
            active.turn_start_index += 1U;
            active.lands_played_this_turn = 0;
        }
    } else {
        clear_all_mana_pools(game);
    }

    if (game.step == Step::Untap && game.active_player.valid()) {
        untap_permanents(game, game.active_player);
    }

    game.priority_player = game.active_player;
    record_event(game, "advance_step", std::string(to_string(previous)) + " -> " + to_string(game.step));

    if (game.step == Step::CombatDamage) {
        assign_combat_damage(game);
    }

    if (game.step == Step::Draw) {
        const bool two_player_first_draw_skip = game.players.size() == 2U &&
            game.turn_number == 1U &&
            game.active_player == game.starting_player;
        if (!two_player_first_draw_skip) {
            draw_card(game, game.active_player);
            apply_state_based_actions(game);
        } else {
            record_event(game, "skip_draw", player(game, game.active_player).name + " skipped first-turn draw");
        }
    }
}

std::string debug_summary(const GameState& game) {
    std::ostringstream out;
    out << "turn=" << game.turn_number
        << " step=" << to_string(game.step)
        << " active=" << (game.active_player.valid() ? player(game, game.active_player).name : "<none>")
        << " priority=" << (game.priority_player.valid() ? player(game, game.priority_player).name : "<none>")
        << " stack=" << game.stack.size();
    for (const auto& p : game.players) {
        out << "\n" << p.name
            << " life=" << p.life
            << " mana=" << p.mana_pool.total()
            << " lost=" << (p.lost ? "true" : "false")
            << " lib=" << p.zones[zone_index(Zone::Library)].size()
            << " hand=" << p.zones[zone_index(Zone::Hand)].size()
            << " battlefield=" << p.zones[zone_index(Zone::Battlefield)].size()
            << " graveyard=" << p.zones[zone_index(Zone::Graveyard)].size();
    }
    return out.str();
}

} // namespace mtgsim
