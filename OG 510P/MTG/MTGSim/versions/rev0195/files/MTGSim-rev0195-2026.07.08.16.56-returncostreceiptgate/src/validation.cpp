#include "mtgsim/validation.hpp"

#include "mtgsim/engine.hpp"

#include <algorithm>
#include <sstream>
#include <string_view>
#include <stdexcept>
#include <unordered_map>
#include <vector>

namespace mtgsim {
namespace {

void add_error(std::vector<InvariantViolation>& out, std::string code, std::string detail) {
    out.push_back(InvariantViolation{ViolationSeverity::Error, std::move(code), std::move(detail)});
}

void add_warning(std::vector<InvariantViolation>& out, std::string code, std::string detail) {
    out.push_back(InvariantViolation{ViolationSeverity::Warning, std::move(code), std::move(detail)});
}

[[nodiscard]] bool is_valid_player_ref(const GameState& game, PlayerId id) noexcept {
    return id.valid() && id.value <= game.players.size();
}

[[nodiscard]] bool is_valid_object_ref(const GameState& game, ObjectId id) noexcept {
    return id.valid() && id.value <= game.objects.size();
}

[[nodiscard]] bool is_valid_zone_ref(Zone zone_name) noexcept {
    return zone_name != Zone::Count && static_cast<u8>(zone_name) < static_cast<u8>(Zone::Count);
}

[[nodiscard]] bool is_valid_step_ref(Step step) noexcept {
    return static_cast<u8>(step) <= static_cast<u8>(Step::Cleanup);
}

[[nodiscard]] bool same_mana_cost_for_validation(const ManaCost& lhs, const ManaCost& rhs) noexcept {
    return lhs.generic == rhs.generic && lhs.white == rhs.white && lhs.blue == rhs.blue && lhs.black == rhs.black &&
           lhs.red == rhs.red && lhs.green == rhs.green && lhs.colorless == rhs.colorless;
}

[[nodiscard]] std::string object_ref(ObjectId id) {
    return "object#" + std::to_string(id.value);
}

[[nodiscard]] std::string player_ref(PlayerId id) {
    return "player#" + std::to_string(id.value);
}

[[nodiscard]] std::string target_ref(TargetRef target) {
    switch (target.kind) {
        case TargetKind::Player: return "target:player#" + std::to_string(target.player.value);
        case TargetKind::Object: {
            std::string out = "target:object#" + std::to_string(target.object.value);
            if (target.object_zone_change_index != 0U) {
                out += "@zc" + std::to_string(target.object_zone_change_index);
            }
            return out;
        }
        case TargetKind::None: return "target:none";
    }
    return "target:unknown";
}

[[nodiscard]] std::string zone_ref(PlayerId player_id, Zone zone_name) {
    return player_ref(player_id) + ":" + to_string(zone_name);
}

[[nodiscard]] bool object_is_current_type(const GameState& game, const GameObject& obj, CardTypeMask type) noexcept {
    return obj.id.valid() && object_has_type(game, obj.id, type);
}

[[nodiscard]] bool object_currently_has_ability(const GameState& game, const GameObject& obj, KeywordAbilityMask ability) noexcept {
    return obj.id.valid() && object_has_ability(game, obj.id, ability);
}

constexpr u32 kNoCombatDeclarationLimitForValidation = ~u32{0};

[[nodiscard]] const CardDefinition* current_definition_for_validation(const GameState& game, const GameObject& obj) noexcept {
    const u32 definition_index = obj.has_copy_effect ? obj.copied_definition_index : obj.definition_index;
    if (definition_index >= game.definitions.size()) {
        return nullptr;
    }
    return &game.definitions[definition_index];
}

[[nodiscard]] u32 active_attack_declaration_limit_for_validation(const GameState& game) noexcept {
    u32 limit = kNoCombatDeclarationLimitForValidation;
    for (const auto& obj : game.objects) {
        if (obj.zone != Zone::Battlefield || obj.ceased_to_exist) {
            continue;
        }
        const auto* def = current_definition_for_validation(game, obj);
        if (def != nullptr && def->max_attackers_each_combat != 0U) {
            limit = std::min(limit, def->max_attackers_each_combat);
        }
    }
    return limit;
}

[[nodiscard]] u32 active_block_declaration_limit_for_validation(const GameState& game) noexcept {
    u32 limit = kNoCombatDeclarationLimitForValidation;
    for (const auto& obj : game.objects) {
        if (obj.zone != Zone::Battlefield || obj.ceased_to_exist) {
            continue;
        }
        const auto* def = current_definition_for_validation(game, obj);
        if (def != nullptr && def->max_blockers_each_combat != 0U) {
            limit = std::min(limit, def->max_blockers_each_combat);
        }
    }
    return limit;
}

[[nodiscard]] u32 required_target_count_for_validation(u32 target_mask, u32 target_count) noexcept {
    if (target_mask == TargetNone) {
        return 0U;
    }
    return target_count == 0U ? 1U : target_count;
}

[[nodiscard]] bool same_target_choice_for_validation(TargetRef a, TargetRef b) noexcept {
    if (a.kind != b.kind) {
        return false;
    }
    switch (a.kind) {
        case TargetKind::Player: return a.player == b.player;
        case TargetKind::Object: return a.object == b.object;
        case TargetKind::None: return true;
    }
    return false;
}

[[nodiscard]] bool same_target_snapshot_for_validation(TargetRef a, TargetRef b) noexcept {
    if (a.kind != b.kind) {
        return false;
    }
    switch (a.kind) {
        case TargetKind::Player: return a.player == b.player;
        case TargetKind::Object: return a.object == b.object && a.object_zone_change_index == b.object_zone_change_index;
        case TargetKind::None: return true;
    }
    return false;
}

[[nodiscard]] bool target_vector_has_duplicate_choices(const std::vector<TargetRef>& targets) noexcept {
    for (std::size_t i = 0; i < targets.size(); ++i) {
        for (std::size_t j = i + 1U; j < targets.size(); ++j) {
            if (same_target_choice_for_validation(targets[i], targets[j])) {
                return true;
            }
        }
    }
    return false;
}

[[nodiscard]] bool mana_pool_is_empty(const ManaPool& pool) noexcept {
    return pool.total() == 0U;
}

[[nodiscard]] bool mana_pool_equals(const ManaPool& lhs, const ManaPool& rhs) noexcept {
    return lhs.white == rhs.white && lhs.blue == rhs.blue && lhs.black == rhs.black &&
           lhs.red == rhs.red && lhs.green == rhs.green && lhs.colorless == rhs.colorless;
}

void add_mana_pool_for_validation(ManaPool& pool, const ManaPool& added) noexcept {
    pool.white += added.white;
    pool.blue += added.blue;
    pool.black += added.black;
    pool.red += added.red;
    pool.green += added.green;
    pool.colorless += added.colorless;
}

[[nodiscard]] bool mana_pool_add_delta_matches(const ManaPool& before, const ManaPool& added, const ManaPool& after) noexcept {
    return before.white + added.white == after.white &&
           before.blue + added.blue == after.blue &&
           before.black + added.black == after.black &&
           before.red + added.red == after.red &&
           before.green + added.green == after.green &&
           before.colorless + added.colorless == after.colorless;
}

[[nodiscard]] bool mana_pool_spend_delta_matches(const ManaPool& before, const ManaPool& spent, const ManaPool& after) noexcept {
    return before.white == after.white + spent.white &&
           before.blue == after.blue + spent.blue &&
           before.black == after.black + spent.black &&
           before.red == after.red + spent.red &&
           before.green == after.green + spent.green &&
           before.colorless == after.colorless + spent.colorless;
}

[[nodiscard]] bool counter_kind_is_object_for_validation(CounterKind counter_kind) noexcept {
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

void validate_target_definition(std::vector<InvariantViolation>& out,
                                std::string code_prefix,
                                std::string prefix,
                                u32 target_mask,
                                u32 target_count) {
    constexpr u32 legal_target_mask = TargetPlayer | TargetObject | TargetStackObject;
    if ((target_mask & ~legal_target_mask) != 0U) {
        add_error(out, code_prefix + ".invalid_target_mask", prefix + " has unknown target-mask bits");
    }
    if (target_mask == TargetNone && target_count != 0U) {
        add_error(out, code_prefix + ".target_count_without_mask", prefix + " has target_count=" + std::to_string(target_count) + " with no target mask");
    }
    if (target_count > 4U) {
        add_warning(out, code_prefix + ".high_target_count", prefix + " has target_count=" + std::to_string(target_count) + " beyond the current small-set search comfort zone");
    }
}

[[nodiscard]] bool exact_target_ref_equal(TargetRef lhs, TargetRef rhs) noexcept {
    return lhs.kind == rhs.kind && lhs.player == rhs.player && lhs.object == rhs.object &&
           lhs.object_zone_change_index == rhs.object_zone_change_index;
}

[[nodiscard]] bool exact_target_vectors_equal(const std::vector<TargetRef>& lhs, const std::vector<TargetRef>& rhs) noexcept {
    if (lhs.size() != rhs.size()) {
        return false;
    }
    for (std::size_t i = 0; i < lhs.size(); ++i) {
        if (!exact_target_ref_equal(lhs[i], rhs[i])) {
            return false;
        }
    }
    return true;
}

void validate_trigger_choice_targets(std::vector<InvariantViolation>& out,
                                     const GameState& game,
                                     const std::string& prefix,
                                     const TriggerRecord& record,
                                     u32 expected_required_targets) {
    if (!record.target_choice_recorded) {
        if (record.required_target_count != 0U || !record.chosen_targets.empty() || record.legal_target_set_count != 0U ||
            record.choice_target_set_hash != 0U || record.no_legal_choices) {
            add_error(out, "trigger_record.choice_fields_without_record", prefix + " carries trigger choice fields without target_choice_recorded");
        }
        return;
    }

    if (record.required_target_count != expected_required_targets) {
        add_error(out, "trigger_record.required_target_count_mismatch", prefix + " required target count does not match target mask/count");
    }
    if (record.choice_target_set_hash != target_choice_set_hash(record.chosen_targets)) {
        add_error(out, "trigger_record.choice_target_set_hash_mismatch", prefix + " choice_target_set_hash does not match chosen_targets");
    }
    if (record.no_legal_choices) {
        if (!record.dropped) {
            add_error(out, "trigger_record.no_legal_choices_not_dropped", prefix + " marks no legal choices but was not dropped");
        }
        if (expected_required_targets == 0U) {
            add_error(out, "trigger_record.no_legal_choices_without_target_requirement", prefix + " marks no legal choices for a trigger with no required targets");
        }
        if (record.legal_target_set_count != 0U || !record.chosen_targets.empty()) {
            add_error(out, "trigger_record.no_legal_choices_has_choice_payload", prefix + " no-legal-choice drop should not carry selected targets or legal sets");
        }
        return;
    }

    if (record.legal_target_set_count == 0U) {
        add_error(out, "trigger_record.zero_legal_target_sets", prefix + " has recorded choices but no legal target set count");
    }
    if (record.chosen_targets.size() != expected_required_targets) {
        add_error(out, "trigger_record.chosen_target_count_mismatch", prefix + " chosen target count does not match required target count");
    }
    for (const auto target : record.chosen_targets) {
        if (target.kind == TargetKind::Player) {
            if (!is_valid_player_ref(game, target.player)) {
                add_error(out, "trigger_record.invalid_chosen_player", prefix + " chose " + target_ref(target));
            }
        } else if (target.kind == TargetKind::Object) {
            if (!is_valid_object_ref(game, target.object)) {
                add_error(out, "trigger_record.invalid_chosen_object", prefix + " chose " + target_ref(target));
            } else if (target.object_zone_change_index == 0U) {
                add_error(out, "trigger_record.missing_chosen_object_zone_change_index", prefix + " chose object target without zone-change identity");
            }
        } else {
            add_error(out, "trigger_record.empty_chosen_target", prefix + " carries an empty chosen target");
        }
    }
}

void validate_static_effect_dependencies(std::vector<InvariantViolation>& out,
                                         const StaticEffectDefinition& effect,
                                         const std::string& prefix,
                                         const std::string& code_prefix) {
    for (const auto& dependency_name : effect.depends_on_effect_names) {
        if (dependency_name.empty()) {
            add_error(out, code_prefix + ".empty_dependency_name", prefix + " has an empty dependency effect name");
        }
        if (!effect.name.empty() && dependency_name == effect.name) {
            add_error(out, code_prefix + ".self_dependency", prefix + " depends on itself by name=" + dependency_name);
        }
    }
}

[[nodiscard]] bool is_combat_step(Step step) noexcept {
    return step == Step::BeginningOfCombat || step == Step::DeclareAttackers ||
           step == Step::DeclareBlockers || step == Step::CombatDamage ||
           step == Step::EndOfCombat;
}

void validate_container(const GameState& game,
                        std::vector<InvariantViolation>& out,
                        std::vector<u32>& seen,
                        const std::vector<ObjectId>& ids,
                        PlayerId containing_player,
                        Zone expected_zone) {
    for (const auto id : ids) {
        if (!is_valid_object_ref(game, id)) {
            add_error(out, "zone.invalid_object_id", zone_ref(containing_player, expected_zone) + " contains invalid " + object_ref(id));
            continue;
        }
        ++seen[id.value - 1U];
        const auto& obj = object(game, id);
        if (obj.ceased_to_exist) {
            add_error(out, "zone.ceased_object_contained", object_ref(id) + " has ceased to exist but still appears in " + zone_ref(containing_player, expected_zone));
        }
        if (obj.zone != expected_zone) {
            add_error(out, "zone.object_zone_mismatch", object_ref(id) + " lives in " + zone_ref(containing_player, expected_zone) + " but records zone=" + to_string(obj.zone));
        }
        if (expected_zone != Zone::Stack) {
            const PlayerId expected_player = expected_zone_container_player(obj, expected_zone);
            if (expected_player != containing_player) {
                add_error(out, "zone.container_player_mismatch", object_ref(id) + " is in " + zone_ref(containing_player, expected_zone) + " but expected container=" + player_ref(expected_player));
            }
        }
    }
}

} // namespace

const char* to_string(ViolationSeverity severity) noexcept {
    switch (severity) {
        case ViolationSeverity::Warning: return "warning";
        case ViolationSeverity::Error: return "error";
    }
    return "unknown";
}

std::vector<InvariantViolation> validate_game_state(const GameState& game) {
    std::vector<InvariantViolation> out;

    for (std::size_t i = 0; i < game.players.size(); ++i) {
        const auto expected = static_cast<u32>(i + 1U);
        if (game.players[i].id.value != expected) {
            add_error(out, "player.non_contiguous_id", "players[" + std::to_string(i) + "] has id=" + std::to_string(game.players[i].id.value) + " expected=" + std::to_string(expected));
        }
        if (game.players[i].lands_played_this_turn > game.players[i].max_land_plays_per_turn) {
            add_error(out, "player.land_play_limit_exceeded", player_ref(game.players[i].id) + " has lands_played=" + std::to_string(game.players[i].lands_played_this_turn) + " max=" + std::to_string(game.players[i].max_land_plays_per_turn));
        }
    }

    constexpr u32 legal_type_mask = TypeArtifact | TypeBattle | TypeCreature | TypeEnchantment | TypeInstant | TypeKindred | TypeLand | TypePlaneswalker | TypeSorcery;
    constexpr u32 legal_ability_mask = AbilityFlying | AbilityReach | AbilityDeathtouch | AbilityLifelink | AbilityVigilance | AbilityFirstStrike | AbilityDoubleStrike | AbilityTrample | AbilityIndestructible | AbilityHaste | AbilityDefender | AbilityHexproof | AbilityShroud | AbilityMenace | AbilityFlash;
    for (std::size_t i = 0; i < game.definitions.size(); ++i) {
        const auto& def = game.definitions[i];
        for (std::size_t j = 0; j < def.static_effects.size(); ++j) {
            const auto& effect = def.static_effects[j];
            const std::string prefix = "definition#" + std::to_string(i) + ":static#" + std::to_string(j + 1U);
            if (effect.scope == StaticEffectScope::None || effect.scope == StaticEffectScope::Count) {
                add_error(out, "static_effect.invalid_scope", prefix + " has scope=" + std::string(to_string(effect.scope)));
            }
            if ((effect.affected_type_mask & ~legal_type_mask) != 0U ||
                (effect.added_type_mask & ~legal_type_mask) != 0U ||
                (effect.removed_type_mask & ~legal_type_mask) != 0U) {
                add_error(out, "static_effect.invalid_type_mask", prefix + " has unknown type-layer bits");
            }
            if ((effect.set_color_mask & ~static_cast<u32>(ColorAll)) != 0U ||
                (effect.added_color_mask & ~static_cast<u32>(ColorAll)) != 0U ||
                (effect.removed_color_mask & ~static_cast<u32>(ColorAll)) != 0U) {
                add_error(out, "static_effect.invalid_color_mask", prefix + " has unknown color-layer bits");
            }
            if ((effect.granted_ability_mask & ~legal_ability_mask) != 0U ||
                (effect.removed_ability_mask & ~legal_ability_mask) != 0U) {
                add_error(out, "static_effect.invalid_ability_mask", prefix + " has unknown ability-layer bits");
            }
            validate_static_effect_dependencies(out, effect, prefix, "static_effect");
            if (!effect.active()) {
                add_error(out, "static_effect.inactive", prefix + " has no active type/color/P/T/ability payload");
            }
        }
        for (std::size_t j = 0; j < def.zone_change_replacements.size(); ++j) {
            const auto& replacement = def.zone_change_replacements[j];
            const std::string prefix = "definition#" + std::to_string(i) + ":zone_replacement#" + std::to_string(j + 1U);
            if (replacement.scope == StaticEffectScope::None || replacement.scope == StaticEffectScope::Count) {
                add_error(out, "zone_replacement.invalid_scope", prefix + " has scope=" + std::string(to_string(replacement.scope)));
            }
            if ((replacement.affected_type_mask & ~legal_type_mask) != 0U) {
                add_error(out, "zone_replacement.invalid_type_mask", prefix + " has unknown affected-type bits");
            }
            if (static_cast<u8>(replacement.from_zone) >= static_cast<u8>(Zone::Count) ||
                static_cast<u8>(replacement.to_zone) >= static_cast<u8>(Zone::Count) ||
                static_cast<u8>(replacement.replacement_zone) >= static_cast<u8>(Zone::Count)) {
                add_error(out, "zone_replacement.invalid_zone", prefix + " has an invalid zone endpoint");
            }
            if (static_cast<u8>(replacement.priority_tier) >= static_cast<u8>(ReplacementPriorityTier::Count)) {
                add_error(out, "zone_replacement.invalid_priority_tier", prefix + " has priority_tier=" + std::string(to_string(replacement.priority_tier)));
            }
            if (!replacement.active()) {
                add_error(out, "zone_replacement.inactive", prefix + " has no active replacement payload");
            }
        }
        if (def.sacrifice_cost.count != 0U) {
            const std::string prefix = "definition#" + std::to_string(i) + ":sacrifice_cost";
            if ((def.sacrifice_cost.required_type_mask & ~legal_type_mask) != 0U) {
                add_error(out, "sacrifice_cost.invalid_type_mask", prefix + " has unknown required-type bits");
            }
            if (!def.sacrifice_cost.active()) {
                add_error(out, "sacrifice_cost.inactive", prefix + " has count=" + std::to_string(def.sacrifice_cost.count) + " but no required permanent type");
            }
        }
        validate_target_definition(out, "definition", "definition#" + std::to_string(i), def.target_mask, def.target_count);
        if (def.trigger.active()) {
            validate_target_definition(out, "trigger", "definition#" + std::to_string(i) + ":trigger", def.trigger.target_mask, def.trigger.target_count);
        }
        for (std::size_t j = 0; j < def.modes.size(); ++j) {
            const auto& mode = def.modes[j];
            validate_target_definition(out, "mode", "definition#" + std::to_string(i) + ":mode#" + std::to_string(j + 1U), mode.target_mask, mode.target_count);
        }
        if (def.loyalty_ability.active()) {
            validate_target_definition(out, "loyalty", "definition#" + std::to_string(i) + ":loyalty", def.loyalty_ability.target_mask, def.loyalty_ability.target_count);
        }
        for (std::size_t j = 0; j < def.activated_abilities.size(); ++j) {
            const auto& ability = def.activated_abilities[j];
            validate_target_definition(out, "activated", "definition#" + std::to_string(i) + ":activated#" + std::to_string(j + 1U), ability.target_mask, ability.target_count);
            if (ability.sacrifice_cost.count == 0U) {
                continue;
            }
            const std::string prefix = "definition#" + std::to_string(i) + ":activated#" + std::to_string(j + 1U) + ":sacrifice_cost";
            if ((ability.sacrifice_cost.required_type_mask & ~legal_type_mask) != 0U) {
                add_error(out, "activated.sacrifice_cost.invalid_type_mask", prefix + " has unknown required-type bits");
            }
            if (!ability.sacrifice_cost.active()) {
                add_error(out, "activated.sacrifice_cost.inactive", prefix + " has count=" + std::to_string(ability.sacrifice_cost.count) + " but no required permanent type");
            }
        }
        if (def.effect_kind == EffectKind::CreateContinuousEffect && !def.continuous_effect.active()) {
            add_error(out, "continuous_effect.missing_payload", "definition#" + std::to_string(i) + " creates a continuous effect without an active payload");
        }
        if (def.continuous_effect.active()) {
            const auto& effect = def.continuous_effect;
            const std::string prefix = "definition#" + std::to_string(i) + ":continuous_payload";
            if (effect.scope == StaticEffectScope::None || effect.scope == StaticEffectScope::Count) {
                add_error(out, "continuous_effect.invalid_scope", prefix + " has scope=" + std::string(to_string(effect.scope)));
            }
            if ((effect.affected_type_mask & ~legal_type_mask) != 0U ||
                (effect.added_type_mask & ~legal_type_mask) != 0U ||
                (effect.removed_type_mask & ~legal_type_mask) != 0U) {
                add_error(out, "continuous_effect.invalid_type_mask", prefix + " has unknown type-layer bits");
            }
            if ((effect.set_color_mask & ~static_cast<u32>(ColorAll)) != 0U ||
                (effect.added_color_mask & ~static_cast<u32>(ColorAll)) != 0U ||
                (effect.removed_color_mask & ~static_cast<u32>(ColorAll)) != 0U) {
                add_error(out, "continuous_effect.invalid_color_mask", prefix + " has unknown color-layer bits");
            }
            if ((effect.granted_ability_mask & ~legal_ability_mask) != 0U ||
                (effect.removed_ability_mask & ~legal_ability_mask) != 0U) {
                add_error(out, "continuous_effect.invalid_ability_mask", prefix + " has unknown ability-layer bits");
            }
            validate_static_effect_dependencies(out, effect, prefix, "continuous_effect");
            if (def.continuous_effect_duration == ContinuousEffectDuration::None || def.continuous_effect_duration == ContinuousEffectDuration::Count) {
                add_error(out, "continuous_effect.invalid_duration", prefix + " has duration=" + std::string(to_string(def.continuous_effect_duration)));
            }
        }
    }

    for (std::size_t i = 0; i < game.objects.size(); ++i) {
        const auto expected = static_cast<u32>(i + 1U);
        const auto& obj = game.objects[i];
        if (obj.id.value != expected) {
            add_error(out, "object.non_contiguous_id", "objects[" + std::to_string(i) + "] has id=" + std::to_string(obj.id.value) + " expected=" + std::to_string(expected));
        }
        if (obj.definition_index >= game.definitions.size()) {
            add_error(out, "object.invalid_definition", object_ref(obj.id) + " references definition_index=" + std::to_string(obj.definition_index));
        }
        if (obj.has_copy_effect) {
            if (obj.zone != Zone::Battlefield) {
                add_error(out, "copy.outside_battlefield", object_ref(obj.id) + " has copy-effect metadata outside the battlefield");
            }
            if (obj.copied_definition_index >= game.definitions.size()) {
                add_error(out, "copy.invalid_definition", object_ref(obj.id) + " copies invalid definition_index=" + std::to_string(obj.copied_definition_index));
            }
        } else if (obj.copied_definition_index != 0U) {
            add_error(out, "copy.stale_definition", object_ref(obj.id) + " stores copied_definition_index without an active copy effect");
        }
        if (!is_valid_player_ref(game, obj.owner)) {
            add_error(out, "object.invalid_owner", object_ref(obj.id) + " has invalid owner " + player_ref(obj.owner));
        }
        if (!is_valid_player_ref(game, obj.controller)) {
            add_error(out, "object.invalid_controller", object_ref(obj.id) + " has invalid controller " + player_ref(obj.controller));
        }
        if (obj.ceased_to_exist) {
            if (!obj.token || obj.ability_object) {
                add_error(out, "object.invalid_ceased_object", object_ref(obj.id) + " has ceased-to-exist metadata but is not a regular token");
            }
            if (obj.attached_to.valid() || obj.attacking || obj.blocked || obj.defending_player.valid() || obj.attacked_object.valid() || obj.blocking.valid() || obj.battle_protector.valid() || !obj.targets.empty() || obj.chosen_mode_index != 0U) {
                add_error(out, "object.ceased_metadata", object_ref(obj.id) + " has ceased to exist but still has live metadata");
            }
        }
        if (obj.zone != Zone::Battlefield && obj.damage_marked != 0U) {
            add_error(out, "object.damage_outside_battlefield", object_ref(obj.id) + " has marked damage outside the battlefield");
        }
        if (obj.deathtouch_damage_marked && obj.zone != Zone::Battlefield) {
            add_error(out, "object.deathtouch_damage_outside_battlefield", object_ref(obj.id) + " has deathtouch damage metadata outside the battlefield");
        }
        if (obj.deathtouch_damage_marked && obj.damage_marked == 0U) {
            add_error(out, "object.deathtouch_damage_without_damage", object_ref(obj.id) + " has deathtouch metadata but no marked damage");
        }
        if (obj.zone != Zone::Battlefield && !obj.counters.empty()) {
            add_error(out, "object.counters_outside_battlefield", object_ref(obj.id) + " has counters outside the battlefield");
        }
        if (obj.zone == Zone::Battlefield && !object_is_current_type(game, obj, TypePlaneswalker) && obj.counters.loyalty != 0U) {
            add_error(out, "object.loyalty_on_non_planeswalker", object_ref(obj.id) + " has loyalty counters but is not a planeswalker");
        }
        if (obj.zone == Zone::Battlefield && !object_is_current_type(game, obj, TypeBattle) && obj.counters.defense != 0U) {
            add_error(out, "object.defense_on_non_battle", object_ref(obj.id) + " has defense counters but is not a battle");
        }
        if (obj.zone == Zone::Battlefield && object_is_current_type(game, obj, TypePlaneswalker) && obj.counters.loyalty == 0U) {
            add_warning(out, "planeswalker.zero_loyalty_pending_sba", object_ref(obj.id) + " is a planeswalker with zero loyalty before SBA cleanup");
        }
        if (obj.zone == Zone::Battlefield && object_is_current_type(game, obj, TypeBattle) && obj.counters.defense == 0U) {
            add_warning(out, "battle.zero_defense_pending_sba", object_ref(obj.id) + " is a battle with zero defense before SBA cleanup");
        }
        if (obj.battle_protector.valid()) {
            if (obj.zone != Zone::Battlefield) {
                add_error(out, "battle.protector_outside_battlefield", object_ref(obj.id) + " has a battle protector outside the battlefield");
            } else if (!object_is_current_type(game, obj, TypeBattle)) {
                add_error(out, "battle.protector_on_non_battle", object_ref(obj.id) + " has a battle protector but is not a battle");
            } else if (!is_valid_player_ref(game, obj.battle_protector) || player(game, obj.battle_protector).lost) {
                add_error(out, "battle.invalid_protector", object_ref(obj.id) + " has invalid/lost protector " + player_ref(obj.battle_protector));
            }
        } else if (obj.zone == Zone::Battlefield && object_is_current_type(game, obj, TypeBattle)) {
            add_error(out, "battle.missing_protector", object_ref(obj.id) + " is a battle with no protector");
        }
        if (obj.zone != Zone::Battlefield && obj.regeneration_shields != 0U) {
            add_error(out, "object.regeneration_outside_battlefield", object_ref(obj.id) + " has regeneration shields outside the battlefield");
        }
        if (obj.zone != Zone::Battlefield && obj.controlled_since_turn_start_index != 0U) {
            add_error(out, "object.control_timestamp_outside_battlefield", object_ref(obj.id) + " has a control-start index outside the battlefield");
        }
        if (obj.zone == Zone::Battlefield && !obj.ability_object && obj.layer_timestamp == 0U) {
            add_error(out, "object.missing_layer_timestamp", object_ref(obj.id) + " is on the battlefield without a layer timestamp");
        }
        if (obj.zone != Zone::Battlefield && obj.layer_timestamp != 0U) {
            add_error(out, "object.layer_timestamp_outside_battlefield", object_ref(obj.id) + " has a layer timestamp outside the battlefield");
        }
        if (obj.zone != Zone::Stack && !obj.targets.empty()) {
            add_error(out, "object.targets_outside_stack", object_ref(obj.id) + " stores targets outside the stack");
        }
        if (obj.zone != Zone::Stack && obj.chosen_mode_index != 0U) {
            add_error(out, "object.chosen_mode_outside_stack", object_ref(obj.id) + " stores a modal choice outside the stack");
        }
        if (obj.zone == Zone::Stack && obj.definition_index < game.definitions.size()) {
            const auto& def = game.definitions[obj.definition_index];
            u32 stack_target_mask = def.target_mask;
            u32 stack_target_count = def.target_count;
            if (obj.chosen_mode_index != 0U && !def.is_modal()) {
                add_error(out, "modal.choice_on_nonmodal", object_ref(obj.id) + " has a chosen mode but its definition is nonmodal");
            }
            if (def.is_modal()) {
                if (obj.chosen_mode_index == 0U) {
                    add_error(out, "modal.missing_choice", object_ref(obj.id) + " is modal on the stack but has no chosen mode");
                } else if (obj.chosen_mode_index > def.modes.size()) {
                    add_error(out, "modal.invalid_choice", object_ref(obj.id) + " chose mode " + std::to_string(obj.chosen_mode_index) + " but definition has " + std::to_string(def.modes.size()) + " modes");
                } else {
                    const auto& mode = def.modes[obj.chosen_mode_index - 1U];
                    stack_target_mask = mode.target_mask;
                    stack_target_count = mode.target_count;
                }
            }
            const auto expected_targets = required_target_count_for_validation(stack_target_mask, stack_target_count);
            if (expected_targets == 0U && !obj.targets.empty()) {
                add_error(out, "target.unexpected", object_ref(obj.id) + " stores targets for an untargeted stack object");
            }
            if (expected_targets != 0U && obj.targets.size() != expected_targets) {
                add_error(out, "target.count_mismatch", object_ref(obj.id) + " stores " + std::to_string(obj.targets.size()) + " targets but expected " + std::to_string(expected_targets));
            }
            if (target_vector_has_duplicate_choices(obj.targets)) {
                add_error(out, "target.duplicate_choice", object_ref(obj.id) + " stores the same target identity more than once");
            }
        }
        if (obj.attached_to.valid()) {
            if (obj.zone != Zone::Battlefield) {
                add_error(out, "attachment.outside_battlefield", object_ref(obj.id) + " is attached outside the battlefield");
            }
            const auto* current_def = current_definition_for_validation(game, obj);
            const auto kind = current_def != nullptr ? current_def->attachment_kind : AttachmentKind::None;
            if (kind == AttachmentKind::None || kind == AttachmentKind::Count) {
                add_error(out, "attachment.non_attachment_attached", object_ref(obj.id) + " is attached but its definition is not an attachment");
            }
            if (obj.attached_to.kind == TargetKind::Object) {
                if (!is_valid_object_ref(game, obj.attached_to.object)) {
                    add_error(out, "attachment.invalid_object_target", object_ref(obj.id) + " is attached to invalid " + object_ref(obj.attached_to.object));
                } else if (obj.attached_to.object == obj.id) {
                    add_error(out, "attachment.self_attached", object_ref(obj.id) + " is attached to itself");
                } else if (object(game, obj.attached_to.object).zone != Zone::Battlefield) {
                    add_error(out, "attachment.object_target_not_battlefield", object_ref(obj.id) + " is attached to non-battlefield " + object_ref(obj.attached_to.object));
                }
            } else if (obj.attached_to.kind == TargetKind::Player) {
                if (!is_valid_player_ref(game, obj.attached_to.player) || player(game, obj.attached_to.player).lost) {
                    add_error(out, "attachment.invalid_player_target", object_ref(obj.id) + " is attached to invalid/lost " + player_ref(obj.attached_to.player));
                }
            }
            if (obj.zone == Zone::Battlefield && kind != AttachmentKind::None && kind != AttachmentKind::Count &&
                !can_attach_object(game, obj.id, obj.attached_to)) {
                add_error(out, "attachment.illegal_attachment", object_ref(obj.id) + " is illegally attached as " + std::string(to_string(kind)));
            }
        } else if (obj.zone == Zone::Battlefield && current_definition_for_validation(game, obj) != nullptr &&
                   current_definition_for_validation(game, obj)->attachment_kind == AttachmentKind::Aura) {
            add_error(out, "attachment.aura_unattached", object_ref(obj.id) + " is an unattached Aura on the battlefield");
        }
        if (obj.ability_object) {
            if (!obj.token) {
                add_error(out, "ability.not_token", object_ref(obj.id) + " is an ability object but is not marked token/synthetic");
            }
            if (obj.zone != Zone::Stack && obj.zone != Zone::Exile) {
                add_error(out, "ability.invalid_zone", object_ref(obj.id) + " ability object is in " + std::string(to_string(obj.zone)));
            }
        }
        for (const auto target : obj.targets) {
            if (target.kind == TargetKind::None) {
                add_error(out, "target.empty", object_ref(obj.id) + " has empty target entry");
            } else if (target.kind == TargetKind::Player && !is_valid_player_ref(game, target.player)) {
                add_error(out, "target.invalid_player", object_ref(obj.id) + " has " + target_ref(target));
            } else if (target.kind == TargetKind::Object && !is_valid_object_ref(game, target.object)) {
                add_error(out, "target.invalid_object", object_ref(obj.id) + " has " + target_ref(target));
            } else if (target.kind == TargetKind::Object && obj.zone == Zone::Stack && target.object_zone_change_index == 0U) {
                add_warning(out, "target.missing_object_lki", object_ref(obj.id) + " stores object target without a zone-change snapshot: " + target_ref(target));
            }
        }
        const bool has_combat_metadata = obj.attacking || obj.blocked || obj.defending_player.valid() || obj.attacked_object.valid() || obj.blocking.valid();
        if (has_combat_metadata && obj.zone != Zone::Battlefield) {
            add_error(out, "combat.metadata_outside_battlefield", object_ref(obj.id) + " carries combat metadata outside the battlefield");
        }
        if (has_combat_metadata && !object_is_current_type(game, obj, TypeCreature)) {
            add_error(out, "combat.noncreature_assignment", object_ref(obj.id) + " carries attacker/blocker metadata but is not a creature");
        }
        if (has_combat_metadata && !is_combat_step(game.step)) {
            add_error(out, "combat.metadata_outside_combat_step", object_ref(obj.id) + " carries combat metadata during " + std::string(to_string(game.step)));
        }
        if (obj.attacking && obj.blocking.valid()) {
            add_error(out, "combat.attacking_and_blocking", object_ref(obj.id) + " is both attacking and blocking");
        }
        if (obj.blocked && !obj.attacking) {
            add_error(out, "combat.blocked_without_attacking", object_ref(obj.id) + " is marked blocked while not attacking");
        }
        if (obj.attacking) {
            if (object_currently_has_ability(game, obj, AbilityDefender)) {
                add_error(out, "combat.defender_attacking", object_ref(obj.id) + " has defender but is marked attacking");
            }
            if (object_has_summoning_sickness(game, obj.id)) {
                add_error(out, "combat.summoning_sick_attacker", object_ref(obj.id) + " is marked attacking while summoning sick");
            }
            if (!is_valid_player_ref(game, obj.defending_player)) {
                add_error(out, "combat.invalid_defender", object_ref(obj.id) + " attacks invalid " + player_ref(obj.defending_player));
            } else if (obj.defending_player == obj.controller) {
                add_error(out, "combat.self_attack", object_ref(obj.id) + " attacks its own controller");
            }
            if (obj.attacked_object.valid()) {
                if (!is_valid_object_ref(game, obj.attacked_object)) {
                    add_error(out, "combat.invalid_attacked_object", object_ref(obj.id) + " attacks invalid " + object_ref(obj.attacked_object));
                } else {
                    const auto& attacked = object(game, obj.attacked_object);
                    if (attacked.zone != Zone::Battlefield) {
                        add_error(out, "combat.attacked_object_not_battlefield", object_ref(obj.id) + " attacks non-battlefield " + object_ref(obj.attacked_object));
                    }
                    const bool attacked_planeswalker = object_is_current_type(game, attacked, TypePlaneswalker);
                    const bool attacked_battle = object_is_current_type(game, attacked, TypeBattle);
                    if (!attacked_planeswalker && !attacked_battle) {
                        add_error(out, "combat.attacked_object_not_combat_target", object_ref(obj.id) + " attacks non-planeswalker/non-battle " + object_ref(obj.attacked_object));
                    }
                    if (attacked_planeswalker) {
                        if (attacked.controller != obj.defending_player) {
                            add_error(out, "combat.attacked_object_wrong_controller", object_ref(obj.id) + " attacks planeswalker not controlled by defending player");
                        }
                        if (attacked.controller == obj.controller) {
                            add_error(out, "combat.self_attack_object", object_ref(obj.id) + " attacks an object its controller controls");
                        }
                    }
                    if (attacked_battle) {
                        if (attacked.battle_protector != obj.defending_player) {
                            add_error(out, "combat.attacked_battle_wrong_protector", object_ref(obj.id) + " attacks battle not protected by defending player");
                        }
                        if (attacked.battle_protector == obj.controller) {
                            add_error(out, "combat.battle_protector_attacking", object_ref(obj.id) + " attacks a battle protected by its controller");
                        }
                    }
                }
            }

            if (object_currently_has_ability(game, obj, AbilityMenace) && obj.blocked) {
                u32 blocker_count = 0;
                for (const auto& maybe_blocker : game.objects) {
                    if (maybe_blocker.zone == Zone::Battlefield && maybe_blocker.blocking == obj.id) {
                        ++blocker_count;
                    }
                }
                if (blocker_count < 2U) {
                    add_error(out, "combat.menace_underblocked", object_ref(obj.id) + " has menace but is blocked by fewer than two creatures");
                }
            }
        } else if (obj.defending_player.valid() || obj.attacked_object.valid()) {
            add_error(out, "combat.defender_without_attack", object_ref(obj.id) + " has combat target metadata while not attacking");
        }
        if (obj.blocking.valid()) {
            if (!is_valid_object_ref(game, obj.blocking)) {
                add_error(out, "combat.invalid_block_target", object_ref(obj.id) + " blocks invalid " + object_ref(obj.blocking));
            } else {
                const auto& attacker = object(game, obj.blocking);
                if (!attacker.attacking || attacker.zone != Zone::Battlefield) {
                    add_error(out, "combat.block_target_not_attacking", object_ref(obj.id) + " blocks non-attacking " + object_ref(obj.blocking));
                } else if (attacker.defending_player != obj.controller) {
                    add_error(out, "combat.blocker_wrong_defender", object_ref(obj.id) + " blocks attacker not attacking its controller");
                } else if (!attacker.blocked) {
                    add_error(out, "combat.blocker_without_attacker_blocked", object_ref(obj.id) + " blocks " + object_ref(obj.blocking) + " but attacker is not marked blocked");
                }
                if (object_currently_has_ability(game, attacker, AbilityFlying) &&
                    !object_currently_has_ability(game, obj, AbilityFlying) &&
                    !object_currently_has_ability(game, obj, AbilityReach)) {
                    add_error(out, "combat.illegal_flying_block", object_ref(obj.id) + " blocks flying attacker " + object_ref(obj.blocking) + " without flying or reach");
                }

                const auto* blocker_def = current_definition_for_validation(game, obj);
                if (blocker_def != nullptr && blocker_def->can_block_only_flying &&
                    !object_currently_has_ability(game, attacker, AbilityFlying)) {
                    add_error(out, "combat.can_block_only_flying_violation", object_ref(obj.id) + " blocks non-flying attacker " + object_ref(obj.blocking));
                }

                if (target_has_protection_from_source(game, TargetRef{.kind = TargetKind::Object, .object = obj.blocking}, obj.id)) {
                    add_error(out, "combat.illegal_protection_block", object_ref(obj.id) + " blocks attacker " + object_ref(obj.blocking) + " despite protection from that source");
                }
            }
        }
    }

    u32 attacking_creature_count = 0;
    u32 blocking_creature_count = 0;
    for (const auto& obj : game.objects) {
        if (obj.zone == Zone::Battlefield && obj.attacking) {
            ++attacking_creature_count;
        }
        if (obj.zone == Zone::Battlefield && obj.blocking.valid()) {
            ++blocking_creature_count;
        }
    }
    if (attacking_creature_count < 2U) {
        for (const auto& obj : game.objects) {
            if (obj.zone != Zone::Battlefield || !obj.attacking) {
                continue;
            }
            const auto* def = current_definition_for_validation(game, obj);
            if (def != nullptr && def->cant_attack_alone) {
                add_error(out, "combat.cant_attack_alone_violation", object_ref(obj.id) + " is attacking without another attacking creature");
            }
        }
    }
    if (blocking_creature_count < 2U) {
        for (const auto& obj : game.objects) {
            if (obj.zone != Zone::Battlefield || !obj.blocking.valid()) {
                continue;
            }
            const auto* def = current_definition_for_validation(game, obj);
            if (def != nullptr && def->cant_block_alone) {
                add_error(out, "combat.cant_block_alone_violation", object_ref(obj.id) + " is blocking without another blocking creature");
            }
        }
    }

    const u32 attack_limit = active_attack_declaration_limit_for_validation(game);
    if (attack_limit != kNoCombatDeclarationLimitForValidation && attacking_creature_count > attack_limit) {
        add_error(out, "combat.attack_limit_exceeded", "attacking creatures=" + std::to_string(attacking_creature_count) + " exceeds active max_attackers_each_combat=" + std::to_string(attack_limit));
    }
    const u32 block_limit = active_block_declaration_limit_for_validation(game);
    if (block_limit != kNoCombatDeclarationLimitForValidation && blocking_creature_count > block_limit) {
        add_error(out, "combat.block_limit_exceeded", "blocking creatures=" + std::to_string(blocking_creature_count) + " exceeds active max_blockers_each_combat=" + std::to_string(block_limit));
    }

    for (const auto& attacker : game.objects) {
        if (attacker.zone != Zone::Battlefield || !attacker.attacking) {
            continue;
        }
        const auto* def = current_definition_for_validation(game, attacker);
        if (def == nullptr || def->max_blockers_to_block_this == 0U) {
            continue;
        }
        u32 blockers_for_attacker = 0;
        for (const auto& maybe_blocker : game.objects) {
            if (maybe_blocker.zone == Zone::Battlefield && maybe_blocker.blocking == attacker.id) {
                ++blockers_for_attacker;
            }
        }
        if (blockers_for_attacker > def->max_blockers_to_block_this) {
            add_error(out,
                      "combat.attacker_blocker_limit_exceeded",
                      object_ref(attacker.id) + " has blockers=" + std::to_string(blockers_for_attacker) +
                          " exceeding max_blockers_to_block_this=" + std::to_string(def->max_blockers_to_block_this));
        }
    }

    if (game.attackers_declared_this_step && game.step != Step::DeclareAttackers) {
        add_warning(out, "combat.attackers_declared_flag_wrong_step", "attacker declaration completion flag is set during " + std::string(to_string(game.step)));
    }
    if (!game.blocker_declaration_complete_players.empty() && game.step != Step::DeclareBlockers) {
        add_warning(out, "combat.blockers_declared_flag_wrong_step", "blocker declaration completion list is set during " + std::string(to_string(game.step)));
    }
    std::vector<PlayerId> blocker_completion_seen;
    for (const auto completed_player : game.blocker_declaration_complete_players) {
        if (!is_valid_player_ref(game, completed_player)) {
            add_error(out, "combat.blockers_declared_invalid_player", "blocker declaration completion list contains invalid player " + std::to_string(completed_player.value));
            continue;
        }
        if (std::find(blocker_completion_seen.begin(), blocker_completion_seen.end(), completed_player) != blocker_completion_seen.end()) {
            add_error(out, "combat.blockers_declared_duplicate_player", "blocker declaration completion list repeats player " + std::to_string(completed_player.value));
        }
        blocker_completion_seen.push_back(completed_player);
    }

    if (game.combat_damage_assigned_this_step && game.step != Step::CombatDamage) {
        add_error(out, "combat.damage_assigned_flag_wrong_step", "combat damage assignment flag is set during " + std::string(to_string(game.step)));
    }

    if (game.events.size() + 1U < game.next_event_sequence) {
        add_warning(out, "event.sequence_gap", "event vector has fewer records than next_event_sequence implies");
    }
    if (game.event_records.size() != game.events.size()) {
        add_error(out, "event_record.count_mismatch", "typed event-record stream size=" + std::to_string(game.event_records.size()) + " does not match log event size=" + std::to_string(game.events.size()));
    }

    for (std::size_t i = 0; i < game.action_receipt_records.size(); ++i) {
        const auto& receipt = game.action_receipt_records[i];
        const std::string prefix = "action_receipt#" + std::to_string(i + 1U);
        if (receipt.receipt_index != i + 1U) {
            add_error(out, "action_receipt.non_contiguous_index", prefix + " has receipt_index=" + std::to_string(receipt.receipt_index));
        }
        if (receipt.kind == ActionKind::Count || static_cast<u8>(receipt.kind) >= static_cast<u8>(ActionKind::Count)) {
            add_error(out, "action_receipt.invalid_kind", prefix + " has invalid action kind");
        }
        if (receipt.choice_kind == ChoiceRequestKind::Count || static_cast<u8>(receipt.choice_kind) >= static_cast<u8>(ChoiceRequestKind::Count)) {
            add_error(out, "action_receipt.invalid_choice_kind", prefix + " has invalid choice request kind");
        }
        if (receipt.choice_validation_source == LegalActionValidationSource::Count ||
            static_cast<u8>(receipt.choice_validation_source) >= static_cast<u8>(LegalActionValidationSource::Count)) {
            add_error(out, "action_receipt.invalid_choice_validation_source", prefix + " has invalid choice validation source");
        }
        if (receipt.choice_request_schema_version != kChoiceRequestSchemaVersion) {
            add_error(out, "action_receipt.choice_request_schema_version", prefix + " records an unsupported choice request schema version");
        }
        if (receipt.choice_request_hash == 0U) {
            add_error(out, "action_receipt.zero_choice_hash", prefix + " has zero choice request hash");
        }
        if (receipt.choice_queue_schema_version != kChoiceRequestQueueSchemaVersion) {
            add_error(out, "action_receipt.choice_queue_schema_version", prefix + " records an unsupported APNAP choice queue schema version");
        }
        if (receipt.choice_queue_hash == 0U) {
            add_error(out, "action_receipt.zero_choice_queue_hash", prefix + " has zero APNAP choice queue hash");
        }
        if (receipt.legal_before && receipt.choice_action_count == 0U) {
            add_error(out, "action_receipt.legal_without_choices", prefix + " was legal but records no offered choices");
        }
        if (!receipt.choice_action_frontier_complete) {
            if (receipt.choice_action_generation_limit == 0U) {
                add_error(out, "action_receipt.incomplete_frontier_without_limit", prefix + " marks an incomplete action frontier without a generation limit");
            }
            if (receipt.choice_action_count != receipt.choice_action_generation_limit) {
                add_error(out, "action_receipt.incomplete_frontier_count_mismatch", prefix + " incomplete frontier count does not equal its generation limit");
            }
            if (receipt.choice_kind != ChoiceRequestKind::DeclareAttackers &&
                receipt.choice_kind != ChoiceRequestKind::DeclareBlockers &&
                receipt.choice_kind != ChoiceRequestKind::OrderCombatDamage &&
                receipt.choice_kind != ChoiceRequestKind::PendingTriggersToStack) {
                add_error(out, "action_receipt.incomplete_frontier_wrong_kind", prefix + " marks an unsupported choice kind as generation-bounded");
            }
        }
        if (receipt.choice_action_generation_limit != 0U && receipt.choice_action_count > receipt.choice_action_generation_limit) {
            add_error(out, "action_receipt.frontier_exceeds_limit", prefix + " records more actions than its generation limit");
        }
        if (receipt.legal_before && receipt.choice_kind == ChoiceRequestKind::None) {
            add_error(out, "action_receipt.legal_without_choice_kind", prefix + " was legal but has no choice request kind");
        }
        if (receipt.legal_before && receipt.choice_validation_source == LegalActionValidationSource::None) {
            add_error(out, "action_receipt.legal_without_validation_source", prefix + " was legal but records no validation source");
        }
        if (!receipt.legal_before && receipt.choice_validation_source != LegalActionValidationSource::None) {
            add_error(out, "action_receipt.illegal_with_validation_source", prefix + " was illegal but records a positive validation source");
        }
        if (receipt.choice_validation_source == LegalActionValidationSource::DirectDomainValidation && receipt.choice_action_frontier_complete) {
            add_error(out, "action_receipt.direct_validation_complete_frontier", prefix + " records direct domain validation for a complete offered frontier");
        }
        if (receipt.choice_validation_source == LegalActionValidationSource::DirectDomainValidation &&
            receipt.choice_kind != ChoiceRequestKind::DeclareAttackers &&
            receipt.choice_kind != ChoiceRequestKind::DeclareBlockers &&
            receipt.choice_kind != ChoiceRequestKind::OrderCombatDamage &&
            receipt.choice_kind != ChoiceRequestKind::PendingTriggersToStack) {
            add_error(out, "action_receipt.direct_validation_wrong_kind", prefix + " records direct domain validation for an unsupported choice kind");
        }
        if (receipt.legal_before && !receipt.choice_page_location_checked) {
            add_error(out, "action_receipt.legal_without_page_location_check", prefix + " was legal but records no checked deterministic page proof");
        }
        if (receipt.legal_before && !receipt.choice_page_location_found) {
            add_error(out, "action_receipt.legal_without_page_location", prefix + " was legal but records no deterministic page location");
        }
        if (!receipt.legal_before && receipt.choice_page_location_checked) {
            add_error(out, "action_receipt.illegal_with_page_location_check", prefix + " was illegal but records a checked page proof");
        }
        if (!receipt.legal_before && receipt.choice_page_location_found) {
            add_error(out, "action_receipt.illegal_with_page_location", prefix + " was illegal but records a positive page location");
        }
        if (receipt.choice_page_location_found && !receipt.choice_page_location_checked) {
            add_error(out, "action_receipt.page_location_found_without_check", prefix + " records a positive page location without marking the page proof checked");
        }
        if (!receipt.choice_page_location_checked && receipt.choice_page_location_hash != 0U) {
            add_error(out, "action_receipt.page_location_hash_without_check", prefix + " records a page-location hash without a checked page proof");
        }
        if (receipt.choice_page_location_found) {
            if (receipt.choice_page_schema_version != kLegalActionPageSchemaVersion) {
                add_error(out, "action_receipt.page_location_schema_version", prefix + " records an unsupported legal-action page schema version");
            }
            if (receipt.choice_page_state_hash != receipt.state_hash_before) {
                add_error(out, "action_receipt.page_location_state_hash", prefix + " page location is not bound to the pre-action StateCore hash");
            }
            if (receipt.choice_page_choice_request_hash != receipt.choice_request_hash) {
                add_error(out, "action_receipt.page_location_choice_request_hash", prefix + " page location is not bound to the offered choice request hash");
            }
            if (receipt.choice_page_effective_limit == 0U) {
                add_error(out, "action_receipt.page_location_zero_limit", prefix + " records a page location with zero effective limit");
            }
            if (receipt.choice_page_scanned_pages == 0U) {
                add_error(out, "action_receipt.page_location_zero_scanned_pages", prefix + " records a page location without scanning any pages");
            }
            if (receipt.choice_action_cursor != receipt.choice_page_cursor + receipt.choice_page_index) {
                add_error(out, "action_receipt.page_location_cursor_mismatch", prefix + " page cursor plus index does not equal action cursor");
            }
            if (receipt.choice_action_cursor < receipt.choice_page_cursor || receipt.choice_action_cursor >= receipt.choice_page_next_cursor) {
                add_error(out, "action_receipt.page_location_action_outside_page", prefix + " action cursor is outside its located page");
            }
            if (receipt.choice_page_index >= receipt.choice_page_effective_limit) {
                add_error(out, "action_receipt.page_location_index_exceeds_limit", prefix + " page index is not below the effective page limit");
            }
            if (receipt.choice_page_next_cursor <= receipt.choice_page_cursor) {
                add_error(out, "action_receipt.page_location_nonprogressing_page", prefix + " located page does not advance its cursor");
            }
            if (receipt.choice_page_hash == 0U) {
                add_error(out, "action_receipt.page_location_zero_hash", prefix + " records a located page without a page hash");
            }
            if (receipt.choice_page_location_hash == 0U) {
                add_error(out, "action_receipt.page_location_zero_location_hash", prefix + " records a located page without a page-location hash");
            } else {
                LegalActionPageLocation expected_location{};
                expected_location.found = receipt.choice_page_location_found;
                expected_location.page_schema_version = receipt.choice_page_schema_version;
                expected_location.kind = receipt.choice_kind;
                expected_location.chooser = receipt.player;
                expected_location.page_state_hash = receipt.choice_page_state_hash;
                expected_location.page_choice_request_hash = receipt.choice_page_choice_request_hash;
                expected_location.requested_page_limit = receipt.choice_page_requested_limit;
                expected_location.effective_page_limit = receipt.choice_page_effective_limit;
                expected_location.page_cursor = receipt.choice_page_cursor;
                expected_location.action_cursor = receipt.choice_action_cursor;
                expected_location.index_in_page = receipt.choice_page_index;
                expected_location.next_cursor = receipt.choice_page_next_cursor;
                expected_location.actions_seen = receipt.choice_page_actions_seen;
                expected_location.scanned_pages = receipt.choice_page_scanned_pages;
                expected_location.page_complete = receipt.choice_page_complete;
                expected_location.total_actions_lower_bound = receipt.choice_page_total_actions_lower_bound;
                expected_location.total_actions_exact = receipt.choice_page_total_actions_exact;
                expected_location.remaining_actions_lower_bound = receipt.choice_page_remaining_actions_lower_bound;
                expected_location.page_hash = receipt.choice_page_hash;
                expected_location.action_hash = receipt.action_hash;
                const u64 expected_location_hash = legal_action_page_location_hash(expected_location);
                if (receipt.choice_page_location_hash != expected_location_hash) {
                    add_error(out, "action_receipt.page_location_hash_mismatch", prefix + " page-location hash does not match its typed locator fields");
                }
            }
            if (receipt.choice_page_total_actions_lower_bound != receipt.choice_page_actions_seen) {
                add_error(out, "action_receipt.page_count_lower_bound_mismatch", prefix + " page total lower bound no longer matches actions_seen");
            }
            if (receipt.choice_page_total_actions_exact != receipt.choice_page_complete) {
                add_error(out, "action_receipt.page_count_exact_flag_mismatch", prefix + " page exact-total flag disagrees with page completion");
            }
            const u64 expected_remaining_lower_bound = receipt.choice_page_complete || receipt.choice_page_actions_seen <= receipt.choice_page_next_cursor
                ? 0U
                : receipt.choice_page_actions_seen - receipt.choice_page_next_cursor;
            if (receipt.choice_page_remaining_actions_lower_bound != expected_remaining_lower_bound) {
                add_error(out, "action_receipt.page_count_remaining_lower_bound_mismatch", prefix + " page remaining lower bound is inconsistent with actions_seen and next_cursor");
            }
        }
        if (receipt.legal_before && receipt.choice_queue_size == 0U) {
            add_error(out, "action_receipt.legal_without_choice_queue", prefix + " was legal but records no APNAP choice queue");
        }
        if (receipt.legal_before && (receipt.choice_queue_index == 0U || receipt.choice_queue_index > receipt.choice_queue_size)) {
            add_error(out, "action_receipt.choice_queue_index_out_of_range", prefix + " records an invalid APNAP queue index");
        }
        if (!receipt.legal_before && (receipt.choice_queue_location_checked || receipt.choice_queue_location_found || receipt.choice_queue_location_hash != 0U)) {
            add_error(out, "action_receipt.illegal_with_choice_queue_location_proof", prefix + " was illegal but records checked APNAP queue-location proof");
        }
        if (receipt.legal_before) {
            if (receipt.choice_queue_location_schema_version != kChoiceQueueLocationSchemaVersion) {
                add_error(out, "action_receipt.choice_queue_location_schema_version", prefix + " records an unsupported APNAP queue-location schema version");
            }
            if (!receipt.choice_queue_location_checked) {
                add_error(out, "action_receipt.unchecked_choice_queue_location", prefix + " was legal but did not mark APNAP queue proof as checked");
            }
            if (!receipt.choice_queue_location_found) {
                add_error(out, "action_receipt.unfound_choice_queue_location", prefix + " was legal but did not record a positive APNAP queue-location proof");
            }
            if (receipt.choice_queue_location_hash == 0U) {
                add_error(out, "action_receipt.zero_choice_queue_location_hash", prefix + " was legal but records no APNAP queue-location hash");
            } else {
                ChoiceQueueLocation expected_location{};
                expected_location.found = receipt.choice_queue_location_found;
                expected_location.schema_version = receipt.choice_queue_location_schema_version;
                expected_location.state_hash = receipt.state_hash_before;
                expected_location.queue_hash = receipt.choice_queue_hash;
                expected_location.queue_index = receipt.choice_queue_index;
                expected_location.queue_size = receipt.choice_queue_size;
                expected_location.request_kind = receipt.choice_kind;
                expected_location.chooser = receipt.player;
                expected_location.request_required = receipt.choice_required;
                expected_location.action_frontier_complete = receipt.choice_action_frontier_complete;
                expected_location.action_generation_limit = receipt.choice_action_generation_limit;
                expected_location.choice_request_hash = receipt.choice_request_hash;
                expected_location.choice_action_count = receipt.choice_action_count;
                expected_location.action_hash = receipt.action_hash;
                const u64 expected_location_hash = choice_queue_location_hash(expected_location);
                if (receipt.choice_queue_location_hash != expected_location_hash) {
                    add_error(out, "action_receipt.choice_queue_location_hash_mismatch", prefix + " APNAP queue-location hash does not match its typed queue/request/action fields");
                }
            }
        }
        if (!is_valid_player_ref(game, receipt.player)) {
            add_error(out, "action_receipt.invalid_player", prefix + " has " + player_ref(receipt.player));
        }
        if (receipt.object.valid() && !is_valid_object_ref(game, receipt.object)) {
            add_error(out, "action_receipt.invalid_object", prefix + " has " + object_ref(receipt.object));
        }
        for (const auto target : receipt.targets) {
            if (target.kind == TargetKind::Player && !is_valid_player_ref(game, target.player)) {
                add_error(out, "action_receipt.invalid_target_player", prefix + " has " + target_ref(target));
            } else if (target.kind == TargetKind::Object && !is_valid_object_ref(game, target.object)) {
                add_error(out, "action_receipt.invalid_target_object", prefix + " has " + target_ref(target));
            }
        }
        if (receipt.kind != ActionKind::PutPendingTriggersOnStack && !receipt.trigger_order.empty()) {
            add_error(out, "action_receipt.trigger_order_wrong_kind", prefix + " carries trigger_order on a non-trigger-stack action");
        }
        if (!receipt.trigger_order.empty()) {
            auto sorted_trigger_order = receipt.trigger_order;
            std::sort(sorted_trigger_order.begin(), sorted_trigger_order.end());
            if (std::adjacent_find(sorted_trigger_order.begin(), sorted_trigger_order.end()) != sorted_trigger_order.end()) {
                add_error(out, "action_receipt.trigger_order_duplicate", prefix + " repeats a trigger record index in trigger_order");
            }
            for (const u32 trigger_record_index : sorted_trigger_order) {
                if (trigger_record_index == 0U || trigger_record_index > game.trigger_records.size()) {
                    add_error(out, "action_receipt.trigger_order_invalid_record", prefix + " references invalid trigger_record#" + std::to_string(trigger_record_index));
                }
            }
            if (receipt.kind == ActionKind::PutPendingTriggersOnStack && receipt.legal_before && receipt.applied) {
                for (std::size_t order_index = 0; order_index < receipt.trigger_order.size(); ++order_index) {
                    const u32 trigger_record_index = receipt.trigger_order[order_index];
                    if (trigger_record_index != 0U && trigger_record_index <= game.trigger_records.size()) {
                        const auto& trigger_record = game.trigger_records[trigger_record_index - 1U];
                        if (trigger_record.stack_order != order_index + 1U) {
                            add_error(out,
                                      "action_receipt.trigger_order_stack_mismatch",
                                      prefix + " trigger_order position " + std::to_string(order_index + 1U) +
                                          " does not match TriggerRecord stack_order=" + std::to_string(trigger_record.stack_order));
                        }
                    }
                }
            }
        }
        const auto canonical_action = action_from_receipt(receipt);
        if (receipt.action_schema_version != kLegalActionSchemaVersion) {
            add_error(out, "action_receipt.action_schema_version", prefix + " records an unsupported canonical action schema version");
        }
        const auto expected_action_hash = legal_action_hash(canonical_action);
        if (receipt.action_hash != expected_action_hash) {
            add_error(out, "action_receipt.action_hash_mismatch", prefix + " hash does not match its canonical action fields");
        }
        if (receipt.state_schema_version != kStateCoreSchemaVersion) {
            add_error(out, "action_receipt.state_schema_version", prefix + " records an unsupported StateCore hash schema version");
        }
        if (receipt.state_hash_before == 0U || receipt.state_hash_after == 0U) {
            add_error(out, "action_receipt.zero_state_hash", prefix + " has zero StateCore hash");
        }
        if (receipt.journal_hash_before == 0U || receipt.journal_hash_after == 0U || receipt.journal_hash_after_action == 0U) {
            add_error(out, "action_receipt.zero_journal_hash", prefix + " has zero journal boundary hash");
        }
        if (receipt.journal_entries_after < receipt.journal_entries_before ||
            receipt.journal_entries_after_action < receipt.journal_entries_before) {
            add_error(out, "action_receipt.journal_count_reversed", prefix + " journal entry count went backwards");
        }
        if (receipt.journal_hash_after_action != receipt.journal_hash_after) {
            add_error(out, "action_receipt.post_action_journal_hash_alias_mismatch", prefix + " explicit post-action journal hash does not match legacy post-action hash field");
        }
        if (receipt.journal_entries_after_action != receipt.journal_entries_after) {
            add_error(out, "action_receipt.post_action_journal_count_alias_mismatch", prefix + " explicit post-action journal count does not match legacy post-action count field");
        }
        if (!receipt.has_post_action_journal_seal()) {
            add_error(out, "action_receipt.post_action_journal_seal_missing", prefix + " does not carry a complete post-action/pre-receipt journal seal");
        }
        if (receipt.next_event_sequence_after < receipt.next_event_sequence_before) {
            add_error(out, "action_receipt.event_sequence_reversed", prefix + " next_event_sequence went backwards");
        }
        if (!receipt.legal_before && receipt.applied) {
            add_error(out, "action_receipt.illegal_applied", prefix + " says an illegal action was applied");
        }
    }

    std::vector<u32> zone_change_event_links(game.zone_change_records.size() + 1U, 0U);
    std::vector<u32> zone_replacement_event_links(game.zone_change_replacement_records.size() + 1U, 0U);
    std::vector<u32> damage_event_links(game.damage_records.size() + 1U, 0U);
    std::vector<u32> damage_prevention_event_links(game.damage_prevention_records.size() + 1U, 0U);
    std::vector<u32> life_change_event_links(game.life_change_records.size() + 1U, 0U);
    std::vector<u32> mana_change_event_links(game.mana_change_records.size() + 1U, 0U);
    std::vector<u32> mana_payment_plan_event_links(game.mana_payment_plan_records.size() + 1U, 0U);
    std::vector<u32> paid_action_declaration_event_links(game.paid_action_declaration_records.size() + 1U, 0U);
    std::vector<u32> paid_action_transaction_event_links(game.paid_action_transaction_records.size() + 1U, 0U);
    std::vector<u32> counter_change_event_links(game.counter_change_records.size() + 1U, 0U);
    std::vector<u32> discard_event_links(game.discard_records.size() + 1U, 0U);
    std::vector<u32> trigger_queued_event_links(game.trigger_records.size() + 1U, 0U);
    std::vector<u32> trigger_stacked_event_links(game.trigger_records.size() + 1U, 0U);
    std::vector<u32> trigger_dropped_event_links(game.trigger_records.size() + 1U, 0U);
    std::vector<u32> stack_placement_event_links(game.stack_placement_records.size() + 1U, 0U);
    std::vector<u32> stack_resolution_event_links(game.stack_resolution_records.size() + 1U, 0U);
    std::vector<u32> priority_transition_event_links(game.priority_transition_records.size() + 1U, 0U);
    std::vector<u32> state_based_action_event_links(game.state_based_action_records.size() + 1U, 0U);
    std::vector<u32> combat_declaration_event_links(game.combat_declaration_records.size() + 1U, 0U);
    std::vector<u32> combat_damage_assignment_event_links(game.combat_damage_assignment_records.size() + 1U, 0U);
    std::vector<u32> draw_event_links(game.draw_records.size() + 1U, 0U);
    std::vector<u32> mulligan_event_links(game.mulligan_records.size() + 1U, 0U);
    std::vector<u32> mulligan_keep_event_links(game.mulligan_keep_records.size() + 1U, 0U);

    u64 last_event_record_sequence = 0;
    for (std::size_t i = 0; i < game.event_records.size(); ++i) {
        const auto& record = game.event_records[i];
        const std::string prefix = "event_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "event_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "event_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_event_record_sequence != 0U && record.sequence <= last_event_record_sequence) {
            add_error(out, "event_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_event_record_sequence = record.sequence;
        if (i < game.events.size()) {
            const auto& event = game.events[i];
            if (record.sequence != event.sequence) {
                add_error(out, "event_record.sequence_mismatch", prefix + " sequence does not match Event sequence at same stream index");
            }
            if (record.log_kind != event.kind) {
                add_error(out, "event_record.log_kind_mismatch", prefix + " log_kind=" + record.log_kind + " does not match Event kind=" + event.kind);
            }
        }
        if (record.kind == EventRecordKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(EventRecordKind::Count)) {
            add_error(out, "event_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (record.object.valid() && !is_valid_object_ref(game, record.object)) {
            add_error(out, "event_record.invalid_object", prefix + " object=" + object_ref(record.object));
        }
        if (record.player.valid() && !is_valid_player_ref(game, record.player)) {
            add_error(out, "event_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.target.kind == TargetKind::Player && !is_valid_player_ref(game, record.target.player)) {
            add_error(out, "event_record.invalid_target_player", prefix + " target=" + player_ref(record.target.player));
        } else if (record.target.kind == TargetKind::Object && !is_valid_object_ref(game, record.target.object)) {
            add_error(out, "event_record.invalid_target_object", prefix + " target=" + object_ref(record.target.object));
        }

        // A StackResolution row may carry trigger_record_index as an auxiliary
        // rev0188 backlink in addition to its primary StackResolutionRecord
        // payload. For every other EventRecordKind, trigger_record_index remains
        // a primary typed payload and counts toward the exactly-one invariant.
        const bool trigger_link_is_auxiliary =
            record.kind == EventRecordKind::StackResolution && record.trigger_record_index != 0U;
        const u32 typed_link_count =
            (record.zone_change_record_index != 0U ? 1U : 0U) +
            (record.zone_replacement_record_index != 0U ? 1U : 0U) +
            (record.damage_record_index != 0U ? 1U : 0U) +
            (record.damage_prevention_record_index != 0U ? 1U : 0U) +
            (record.life_change_record_index != 0U ? 1U : 0U) +
            (record.mana_change_record_index != 0U ? 1U : 0U) +
            (record.counter_change_record_index != 0U ? 1U : 0U) +
            (record.discard_record_index != 0U ? 1U : 0U) +
            ((record.trigger_record_index != 0U && !trigger_link_is_auxiliary) ? 1U : 0U) +
            (record.stack_placement_record_index != 0U ? 1U : 0U) +
            (record.stack_resolution_record_index != 0U ? 1U : 0U) +
            (record.priority_transition_record_index != 0U ? 1U : 0U) +
            (record.state_based_action_record_index != 0U ? 1U : 0U) +
            (record.combat_declaration_record_index != 0U ? 1U : 0U) +
            (record.combat_damage_assignment_record_index != 0U ? 1U : 0U) +
            (record.mana_payment_plan_record_index != 0U ? 1U : 0U) +
            (record.paid_action_declaration_record_index != 0U ? 1U : 0U) +
            (record.paid_action_transaction_record_index != 0U ? 1U : 0U) +
            (record.draw_record_index != 0U ? 1U : 0U) +
            (record.mulligan_record_index != 0U ? 1U : 0U) +
            (record.mulligan_keep_record_index != 0U ? 1U : 0U);
        if (record.kind != EventRecordKind::Log && record.kind != EventRecordKind::Count && typed_link_count != 1U) {
            add_error(out, "event_record.typed_link_count", prefix + " should have exactly one typed payload link for kind=" + std::string(to_string(record.kind)) + ", found=" + std::to_string(typed_link_count));
        }

        switch (record.kind) {
            case EventRecordKind::Log:
                if (typed_link_count != 0U) {
                    add_error(out, "event_record.log_has_typed_link", prefix + " is a plain log row but links to a typed payload");
                }
                if (record.log_kind == "tap") {
                    if (!record.object.valid()) {
                        add_error(out, "event_record.tap_log_missing_object", prefix + " tap log row does not identify the tapped object");
                    }
                    if (record.object_zone_change_index == 0U) {
                        add_error(out, "event_record.tap_log_missing_object_zone_index", prefix + " tap log row does not preserve the tapped object zone-change snapshot");
                    }
                    if (!record.player.valid()) {
                        add_error(out, "event_record.tap_log_missing_player", prefix + " tap log row does not identify the tapping player");
                    }
                }
                break;
            case EventRecordKind::ZoneChange:
                if (record.zone_change_record_index == 0U || record.zone_change_record_index >= zone_change_event_links.size()) {
                    add_error(out, "event_record.invalid_zone_change_link", prefix + " links invalid zone_change_record_index=" + std::to_string(record.zone_change_record_index));
                } else {
                    ++zone_change_event_links[record.zone_change_record_index];
                    const auto& zone_record = game.zone_change_records[record.zone_change_record_index - 1U];
                    if (zone_record.sequence != record.sequence) {
                        add_error(out, "event_record.zone_change_sequence_mismatch", prefix + " sequence does not match linked ZoneChangeRecord");
                    }
                    if (record.object.valid() && zone_record.object != record.object) {
                        add_error(out, "event_record.zone_change_object_mismatch", prefix + " object does not match linked ZoneChangeRecord");
                    }
                }
                if (record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " zone-change row carries unrelated typed links");
                }
                break;
            case EventRecordKind::ZoneReplacement:
                if (record.zone_replacement_record_index == 0U || record.zone_replacement_record_index >= zone_replacement_event_links.size()) {
                    add_error(out, "event_record.invalid_zone_replacement_link", prefix + " links invalid zone_replacement_record_index=" + std::to_string(record.zone_replacement_record_index));
                } else {
                    ++zone_replacement_event_links[record.zone_replacement_record_index];
                    const auto& replacement_record = game.zone_change_replacement_records[record.zone_replacement_record_index - 1U];
                    if (replacement_record.sequence != record.sequence) {
                        add_error(out, "event_record.zone_replacement_sequence_mismatch", prefix + " sequence does not match linked ZoneChangeReplacementRecord");
                    }
                    if (record.object.valid() && replacement_record.object != record.object) {
                        add_error(out, "event_record.zone_replacement_object_mismatch", prefix + " object does not match linked ZoneChangeReplacementRecord");
                    }
                    if (record.player.valid() && replacement_record.affected_player != record.player) {
                        add_error(out, "event_record.zone_replacement_affected_player_mismatch", prefix + " player does not match linked ZoneChangeReplacementRecord affected player");
                    }
                }
                if (record.zone_change_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " zone-replacement row carries unrelated typed links");
                }
                break;
            case EventRecordKind::Damage:
                if (record.damage_record_index == 0U || record.damage_record_index >= damage_event_links.size()) {
                    add_error(out, "event_record.invalid_damage_link", prefix + " links invalid damage_record_index=" + std::to_string(record.damage_record_index));
                } else {
                    ++damage_event_links[record.damage_record_index];
                    const auto& damage_record = game.damage_records[record.damage_record_index - 1U];
                    if (damage_record.sequence != record.sequence) {
                        add_error(out, "event_record.damage_sequence_mismatch", prefix + " sequence does not match linked DamageRecord");
                    }
                    if (record.object.valid() && damage_record.source != record.object) {
                        add_error(out, "event_record.damage_source_mismatch", prefix + " object does not match linked DamageRecord source");
                    }
                    if (record.target.valid() && !(record.target == damage_record.target)) {
                        add_error(out, "event_record.damage_target_mismatch", prefix + " target does not match linked DamageRecord target");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_prevention_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " damage row carries unrelated typed links");
                }
                break;
            case EventRecordKind::DamagePrevention:
                if (record.damage_prevention_record_index == 0U || record.damage_prevention_record_index >= damage_prevention_event_links.size()) {
                    add_error(out, "event_record.invalid_damage_prevention_link", prefix + " links invalid damage_prevention_record_index=" + std::to_string(record.damage_prevention_record_index));
                } else {
                    ++damage_prevention_event_links[record.damage_prevention_record_index];
                    const auto& prevention_record = game.damage_prevention_records[record.damage_prevention_record_index - 1U];
                    if (prevention_record.sequence != record.sequence) {
                        add_error(out, "event_record.damage_prevention_sequence_mismatch", prefix + " sequence does not match linked DamagePreventionRecord");
                    }
                    if (record.target.valid() && !(record.target == prevention_record.target)) {
                        add_error(out, "event_record.damage_prevention_target_mismatch", prefix + " target does not match linked DamagePreventionRecord target");
                    }
                    if (record.object.valid() && (prevention_record.target.kind != TargetKind::Object || prevention_record.target.object != record.object)) {
                        add_error(out, "event_record.damage_prevention_object_mismatch", prefix + " object does not match linked DamagePreventionRecord target object");
                    }
                    if (record.player.valid() && (prevention_record.target.kind != TargetKind::Player || prevention_record.target.player != record.player)) {
                        add_error(out, "event_record.damage_prevention_player_mismatch", prefix + " player does not match linked DamagePreventionRecord target player");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.mana_change_record_index != 0U || record.counter_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.draw_record_index != 0U || record.mulligan_record_index != 0U || record.mulligan_keep_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " damage-prevention row carries unrelated typed links");
                }
                break;
            case EventRecordKind::LifeChange:
                if (record.life_change_record_index == 0U || record.life_change_record_index >= life_change_event_links.size()) {
                    add_error(out, "event_record.invalid_life_change_link", prefix + " links invalid life_change_record_index=" + std::to_string(record.life_change_record_index));
                } else {
                    ++life_change_event_links[record.life_change_record_index];
                    const auto& life_record = game.life_change_records[record.life_change_record_index - 1U];
                    if (life_record.sequence != record.sequence) {
                        add_error(out, "event_record.life_change_sequence_mismatch", prefix + " sequence does not match linked LifeChangeRecord");
                    }
                    if (record.player.valid() && life_record.player != record.player) {
                        add_error(out, "event_record.life_change_player_mismatch", prefix + " player does not match linked LifeChangeRecord");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.mana_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.draw_record_index != 0U || record.mulligan_record_index != 0U || record.mulligan_keep_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " life-change row carries unrelated typed links");
                }
                break;
            case EventRecordKind::ManaChange:
                if (record.mana_change_record_index == 0U || record.mana_change_record_index >= mana_change_event_links.size()) {
                    add_error(out, "event_record.invalid_mana_change_link", prefix + " links invalid mana_change_record_index=" + std::to_string(record.mana_change_record_index));
                } else {
                    ++mana_change_event_links[record.mana_change_record_index];
                    const auto& mana_record = game.mana_change_records[record.mana_change_record_index - 1U];
                    if (mana_record.sequence != record.sequence) {
                        add_error(out, "event_record.mana_change_sequence_mismatch", prefix + " sequence does not match linked ManaChangeRecord");
                    }
                    if (record.player.valid() && mana_record.player != record.player) {
                        add_error(out, "event_record.mana_change_player_mismatch", prefix + " player does not match linked ManaChangeRecord");
                    }
                    if (record.object.valid() && mana_record.source != record.object) {
                        add_error(out, "event_record.mana_change_source_mismatch", prefix + " object does not match linked ManaChangeRecord source");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.counter_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.draw_record_index != 0U || record.mulligan_record_index != 0U || record.mulligan_keep_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " mana-change row carries unrelated typed links");
                }
                break;
            case EventRecordKind::CounterChange:
                if (record.counter_change_record_index == 0U || record.counter_change_record_index >= counter_change_event_links.size()) {
                    add_error(out, "event_record.invalid_counter_change_link", prefix + " links invalid counter_change_record_index=" + std::to_string(record.counter_change_record_index));
                } else {
                    ++counter_change_event_links[record.counter_change_record_index];
                    const auto& counter_record = game.counter_change_records[record.counter_change_record_index - 1U];
                    if (counter_record.sequence != record.sequence) {
                        add_error(out, "event_record.counter_change_sequence_mismatch", prefix + " sequence does not match linked CounterChangeRecord");
                    }
                    if (record.player.valid() && counter_record.player != record.player) {
                        add_error(out, "event_record.counter_change_player_mismatch", prefix + " player does not match linked CounterChangeRecord");
                    }
                    if (record.object.valid() && counter_record.object != record.object) {
                        add_error(out, "event_record.counter_change_object_mismatch", prefix + " object does not match linked CounterChangeRecord");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.mana_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.draw_record_index != 0U || record.mulligan_record_index != 0U || record.mulligan_keep_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " counter-change row carries unrelated typed links");
                }
                break;
            case EventRecordKind::Discard:
                if (record.discard_record_index == 0U || record.discard_record_index >= discard_event_links.size()) {
                    add_error(out, "event_record.invalid_discard_link", prefix + " links invalid discard_record_index=" + std::to_string(record.discard_record_index));
                } else {
                    ++discard_event_links[record.discard_record_index];
                    const auto& discard_record = game.discard_records[record.discard_record_index - 1U];
                    if (discard_record.sequence != record.sequence) {
                        add_error(out, "event_record.discard_sequence_mismatch", prefix + " sequence does not match linked DiscardRecord");
                    }
                    if (record.player.valid() && discard_record.player != record.player) {
                        add_error(out, "event_record.discard_player_mismatch", prefix + " player does not match linked DiscardRecord");
                    }
                    if (record.object.valid() && discard_record.card != record.object) {
                        add_error(out, "event_record.discard_card_mismatch", prefix + " object does not match linked DiscardRecord card");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.damage_prevention_record_index != 0U || record.life_change_record_index != 0U || record.mana_change_record_index != 0U || record.counter_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.draw_record_index != 0U || record.mulligan_record_index != 0U || record.mulligan_keep_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " discard row carries unrelated typed links");
                }
                break;
            case EventRecordKind::TriggerQueued:
            case EventRecordKind::TriggerPutOnStack:
            case EventRecordKind::TriggerDropped:
                if (record.trigger_record_index == 0U || record.trigger_record_index >= trigger_queued_event_links.size()) {
                    add_error(out, "event_record.invalid_trigger_link", prefix + " links invalid trigger_record_index=" + std::to_string(record.trigger_record_index));
                } else {
                    const auto& trigger_record = game.trigger_records[record.trigger_record_index - 1U];
                    if (record.kind == EventRecordKind::TriggerQueued) {
                        ++trigger_queued_event_links[record.trigger_record_index];
                        if (trigger_record.sequence != record.sequence) {
                            add_error(out, "event_record.trigger_queue_sequence_mismatch", prefix + " sequence does not match TriggerRecord queue sequence");
                        }
                    } else if (record.kind == EventRecordKind::TriggerPutOnStack) {
                        ++trigger_stacked_event_links[record.trigger_record_index];
                        if (trigger_record.put_on_stack_sequence != record.sequence) {
                            add_error(out, "event_record.trigger_stack_sequence_mismatch", prefix + " sequence does not match TriggerRecord put-on-stack sequence");
                        }
                    } else {
                        ++trigger_dropped_event_links[record.trigger_record_index];
                        if (trigger_record.dropped_sequence != record.sequence) {
                            add_error(out, "event_record.trigger_drop_sequence_mismatch", prefix + " sequence does not match TriggerRecord dropped sequence");
                        }
                    }
                    if (record.player.valid() && trigger_record.controller != record.player) {
                        add_error(out, "event_record.trigger_controller_mismatch", prefix + " player does not match linked TriggerRecord controller");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " trigger row carries unrelated typed links");
                }
                break;
            case EventRecordKind::StackPlacement:
                if (record.stack_placement_record_index == 0U || record.stack_placement_record_index >= stack_placement_event_links.size()) {
                    add_error(out, "event_record.invalid_stack_placement_link", prefix + " links invalid stack_placement_record_index=" + std::to_string(record.stack_placement_record_index));
                } else {
                    ++stack_placement_event_links[record.stack_placement_record_index];
                    const auto& placement_record = game.stack_placement_records[record.stack_placement_record_index - 1U];
                    if (placement_record.sequence != record.sequence) {
                        add_error(out, "event_record.stack_placement_sequence_mismatch", prefix + " sequence does not match linked StackPlacementRecord");
                    }
                    if (record.object.valid() && placement_record.stack_object != record.object) {
                        add_error(out, "event_record.stack_placement_object_mismatch", prefix + " object does not match linked StackPlacementRecord stack object");
                    }
                    if (record.player.valid() && placement_record.controller != record.player) {
                        add_error(out, "event_record.stack_placement_controller_mismatch", prefix + " player does not match linked StackPlacementRecord controller");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " stack-placement row carries unrelated typed links");
                }
                break;
            case EventRecordKind::StackResolution:
                if (record.stack_resolution_record_index == 0U || record.stack_resolution_record_index >= stack_resolution_event_links.size()) {
                    add_error(out, "event_record.invalid_stack_resolution_link", prefix + " links invalid stack_resolution_record_index=" + std::to_string(record.stack_resolution_record_index));
                } else {
                    ++stack_resolution_event_links[record.stack_resolution_record_index];
                    const auto& resolution_record = game.stack_resolution_records[record.stack_resolution_record_index - 1U];
                    if (resolution_record.sequence != record.sequence) {
                        add_error(out, "event_record.stack_resolution_sequence_mismatch", prefix + " sequence does not match linked StackResolutionRecord");
                    }
                    if (record.object.valid() && resolution_record.stack_object != record.object) {
                        add_error(out, "event_record.stack_resolution_object_mismatch", prefix + " object does not match linked StackResolutionRecord");
                    }
                    if (record.player.valid() && resolution_record.controller != record.player) {
                        add_error(out, "event_record.stack_resolution_controller_mismatch", prefix + " player does not match linked StackResolutionRecord controller");
                    }
                    if (record.trigger_record_index != resolution_record.trigger_record_index) {
                        add_error(out, "event_record.stack_resolution_trigger_link_mismatch", prefix + " trigger_record_index does not match linked StackResolutionRecord");
                    }
                }
                if (record.trigger_record_index != 0U) {
                    if (record.trigger_record_index >= trigger_queued_event_links.size()) {
                        add_error(out, "event_record.invalid_stack_resolution_trigger_link", prefix + " links invalid trigger_record_index=" + std::to_string(record.trigger_record_index));
                    } else {
                        const auto& trigger_record = game.trigger_records[record.trigger_record_index - 1U];
                        if (record.object.valid() && trigger_record.stack_object != record.object) {
                            add_error(out, "event_record.stack_resolution_trigger_object_mismatch", prefix + " trigger_record_index names a different stack object");
                        }
                        if (trigger_record.stack_resolution_record_index != record.stack_resolution_record_index) {
                            add_error(out, "event_record.stack_resolution_trigger_backlink_mismatch", prefix + " TriggerRecord does not point back to this StackResolutionRecord");
                        }
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.stack_placement_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " stack-resolution row carries unrelated typed links");
                }
                break;
            case EventRecordKind::PriorityTransition:
                if (record.priority_transition_record_index == 0U || record.priority_transition_record_index >= priority_transition_event_links.size()) {
                    add_error(out, "event_record.invalid_priority_transition_link", prefix + " links invalid priority_transition_record_index=" + std::to_string(record.priority_transition_record_index));
                } else {
                    ++priority_transition_event_links[record.priority_transition_record_index];
                    const auto& priority_record = game.priority_transition_records[record.priority_transition_record_index - 1U];
                    if (priority_record.sequence != record.sequence) {
                        add_error(out, "event_record.priority_transition_sequence_mismatch", prefix + " sequence does not match linked PriorityTransitionRecord");
                    }
                    if (record.player.valid() && priority_record.player != record.player) {
                        add_error(out, "event_record.priority_transition_player_mismatch", prefix + " player does not match linked PriorityTransitionRecord");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " priority-transition row carries unrelated typed links");
                }
                break;
            case EventRecordKind::StateBasedAction:
                if (record.state_based_action_record_index == 0U || record.state_based_action_record_index >= state_based_action_event_links.size()) {
                    add_error(out, "event_record.invalid_state_based_action_link", prefix + " links invalid state_based_action_record_index=" + std::to_string(record.state_based_action_record_index));
                } else {
                    ++state_based_action_event_links[record.state_based_action_record_index];
                    const auto& sba_record = game.state_based_action_records[record.state_based_action_record_index - 1U];
                    if (sba_record.sequence != record.sequence) {
                        add_error(out, "event_record.state_based_action_sequence_mismatch", prefix + " sequence does not match linked StateBasedActionRecord");
                    }
                    if (record.object.valid() && sba_record.object != record.object) {
                        add_error(out, "event_record.state_based_action_object_mismatch", prefix + " object does not match linked StateBasedActionRecord");
                    }
                    if (record.player.valid() && sba_record.player != record.player) {
                        add_error(out, "event_record.state_based_action_player_mismatch", prefix + " player does not match linked StateBasedActionRecord");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " state-based-action row carries unrelated typed links");
                }
                break;
            case EventRecordKind::CombatDeclaration:
                if (record.combat_declaration_record_index == 0U || record.combat_declaration_record_index >= combat_declaration_event_links.size()) {
                    add_error(out, "event_record.invalid_combat_declaration_link", prefix + " links invalid combat_declaration_record_index=" + std::to_string(record.combat_declaration_record_index));
                } else {
                    ++combat_declaration_event_links[record.combat_declaration_record_index];
                    const auto& declaration_record = game.combat_declaration_records[record.combat_declaration_record_index - 1U];
                    if (declaration_record.sequence != record.sequence) {
                        add_error(out, "event_record.combat_declaration_sequence_mismatch", prefix + " sequence does not match linked CombatDeclarationRecord");
                    }
                    if (record.object.valid() && declaration_record.actor != record.object) {
                        add_error(out, "event_record.combat_declaration_actor_mismatch", prefix + " object does not match linked CombatDeclarationRecord actor");
                    }
                    if (record.player.valid() && declaration_record.controller != record.player) {
                        add_error(out, "event_record.combat_declaration_controller_mismatch", prefix + " player does not match linked CombatDeclarationRecord controller");
                    }
                    if (record.target.valid() && !(record.target == declaration_record.target)) {
                        add_error(out, "event_record.combat_declaration_target_mismatch", prefix + " target does not match linked CombatDeclarationRecord target");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_damage_assignment_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " combat-declaration row carries unrelated typed links");
                }
                break;
            case EventRecordKind::CombatDamageAssignment:
                if (record.combat_damage_assignment_record_index == 0U || record.combat_damage_assignment_record_index >= combat_damage_assignment_event_links.size()) {
                    add_error(out, "event_record.invalid_combat_damage_assignment_link", prefix + " links invalid combat_damage_assignment_record_index=" + std::to_string(record.combat_damage_assignment_record_index));
                } else {
                    ++combat_damage_assignment_event_links[record.combat_damage_assignment_record_index];
                    const auto& assignment_record = game.combat_damage_assignment_records[record.combat_damage_assignment_record_index - 1U];
                    if (assignment_record.sequence != record.sequence) {
                        add_error(out, "event_record.combat_damage_assignment_sequence_mismatch", prefix + " sequence does not match linked CombatDamageAssignmentRecord");
                    }
                    if (record.object.valid() && assignment_record.source != record.object) {
                        add_error(out, "event_record.combat_damage_assignment_source_mismatch", prefix + " object does not match linked CombatDamageAssignmentRecord source");
                    }
                    if (record.player.valid() && assignment_record.source_controller != record.player) {
                        add_error(out, "event_record.combat_damage_assignment_controller_mismatch", prefix + " player does not match linked CombatDamageAssignmentRecord controller");
                    }
                    if (record.target.valid() && !(record.target == assignment_record.target)) {
                        add_error(out, "event_record.combat_damage_assignment_target_mismatch", prefix + " target does not match linked CombatDamageAssignmentRecord target");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " combat-damage-assignment row carries unrelated typed links");
                }
                break;
            case EventRecordKind::PaidActionDeclaration:
                if (record.paid_action_declaration_record_index == 0U || record.paid_action_declaration_record_index >= paid_action_declaration_event_links.size()) {
                    add_error(out, "event_record.invalid_paid_action_declaration_link", prefix + " links invalid paid_action_declaration_record_index=" + std::to_string(record.paid_action_declaration_record_index));
                } else {
                    ++paid_action_declaration_event_links[record.paid_action_declaration_record_index];
                    const auto& declaration_record = game.paid_action_declaration_records[record.paid_action_declaration_record_index - 1U];
                    if (declaration_record.sequence != record.sequence) {
                        add_error(out, "event_record.paid_action_declaration_sequence_mismatch", prefix + " sequence does not match linked PaidActionDeclarationRecord");
                    }
                    if (record.object.valid() && declaration_record.stack_object != record.object) {
                        add_error(out, "event_record.paid_action_declaration_object_mismatch", prefix + " object does not match linked PaidActionDeclarationRecord stack object");
                    }
                    if (record.player.valid() && declaration_record.player != record.player) {
                        add_error(out, "event_record.paid_action_declaration_player_mismatch", prefix + " player does not match linked PaidActionDeclarationRecord");
                    }
                }
                break;
            case EventRecordKind::PaidActionTransaction:
                if (record.paid_action_transaction_record_index == 0U || record.paid_action_transaction_record_index >= paid_action_transaction_event_links.size()) {
                    add_error(out, "event_record.invalid_paid_action_transaction_link", prefix + " links invalid paid_action_transaction_record_index=" + std::to_string(record.paid_action_transaction_record_index));
                } else {
                    ++paid_action_transaction_event_links[record.paid_action_transaction_record_index];
                    const auto& transaction_record = game.paid_action_transaction_records[record.paid_action_transaction_record_index - 1U];
                    if (transaction_record.sequence != record.sequence) {
                        add_error(out, "event_record.paid_action_transaction_sequence_mismatch", prefix + " sequence does not match linked PaidActionTransactionRecord");
                    }
                    if (record.object.valid() && transaction_record.stack_object != record.object && transaction_record.source_object != record.object) {
                        add_error(out, "event_record.paid_action_transaction_object_mismatch", prefix + " object does not match linked PaidActionTransactionRecord");
                    }
                    if (record.player.valid() && transaction_record.player != record.player) {
                        add_error(out, "event_record.paid_action_transaction_player_mismatch", prefix + " player does not match linked PaidActionTransactionRecord");
                    }
                }
                break;
            case EventRecordKind::ManaPaymentPlan:
                if (record.mana_payment_plan_record_index == 0U || record.mana_payment_plan_record_index >= mana_payment_plan_event_links.size()) {
                    add_error(out, "event_record.invalid_mana_payment_plan_link", prefix + " links invalid mana_payment_plan_record_index=" + std::to_string(record.mana_payment_plan_record_index));
                } else {
                    ++mana_payment_plan_event_links[record.mana_payment_plan_record_index];
                    const auto& plan_record = game.mana_payment_plan_records[record.mana_payment_plan_record_index - 1U];
                    if (plan_record.sequence != record.sequence) {
                        add_error(out, "event_record.mana_payment_plan_sequence_mismatch", prefix + " sequence does not match linked ManaPaymentPlanRecord");
                    }
                    if (record.player.valid() && plan_record.player != record.player) {
                        add_error(out, "event_record.mana_payment_plan_player_mismatch", prefix + " player does not match linked ManaPaymentPlanRecord");
                    }
                }
                break;
            case EventRecordKind::Draw:
                if (record.draw_record_index == 0U || record.draw_record_index >= draw_event_links.size()) {
                    add_error(out, "event_record.invalid_draw_link", prefix + " links invalid draw_record_index=" + std::to_string(record.draw_record_index));
                } else {
                    ++draw_event_links[record.draw_record_index];
                    const auto& draw_record = game.draw_records[record.draw_record_index - 1U];
                    if (draw_record.sequence != record.sequence) {
                        add_error(out, "event_record.draw_sequence_mismatch", prefix + " sequence does not match linked DrawRecord");
                    }
                    if (record.player.valid() && draw_record.player != record.player) {
                        add_error(out, "event_record.draw_player_mismatch", prefix + " player does not match linked DrawRecord");
                    }
                    if (record.object.valid() && draw_record.card != record.object) {
                        add_error(out, "event_record.draw_card_mismatch", prefix + " object does not match linked DrawRecord card");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.mulligan_record_index != 0U || record.mulligan_keep_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " draw row carries unrelated typed links");
                }
                break;
            case EventRecordKind::Mulligan:
                if (record.mulligan_record_index == 0U || record.mulligan_record_index >= mulligan_event_links.size()) {
                    add_error(out, "event_record.invalid_mulligan_link", prefix + " links invalid mulligan_record_index=" + std::to_string(record.mulligan_record_index));
                } else {
                    ++mulligan_event_links[record.mulligan_record_index];
                    const auto& mulligan_record = game.mulligan_records[record.mulligan_record_index - 1U];
                    if (mulligan_record.sequence != record.sequence) {
                        add_error(out, "event_record.mulligan_sequence_mismatch", prefix + " sequence does not match linked MulliganRecord");
                    }
                    if (record.player.valid() && mulligan_record.player != record.player) {
                        add_error(out, "event_record.mulligan_player_mismatch", prefix + " player does not match linked MulliganRecord");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.draw_record_index != 0U || record.mulligan_keep_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " mulligan row carries unrelated typed links");
                }
                break;
            case EventRecordKind::MulliganKeep:
                if (record.mulligan_keep_record_index == 0U || record.mulligan_keep_record_index >= mulligan_keep_event_links.size()) {
                    add_error(out, "event_record.invalid_mulligan_keep_link", prefix + " links invalid mulligan_keep_record_index=" + std::to_string(record.mulligan_keep_record_index));
                } else {
                    ++mulligan_keep_event_links[record.mulligan_keep_record_index];
                    const auto& keep_record = game.mulligan_keep_records[record.mulligan_keep_record_index - 1U];
                    if (keep_record.sequence != record.sequence) {
                        add_error(out, "event_record.mulligan_keep_sequence_mismatch", prefix + " sequence does not match linked MulliganKeepRecord");
                    }
                    if (record.player.valid() && keep_record.player != record.player) {
                        add_error(out, "event_record.mulligan_keep_player_mismatch", prefix + " player does not match linked MulliganKeepRecord");
                    }
                }
                if (record.zone_change_record_index != 0U || record.zone_replacement_record_index != 0U || record.damage_record_index != 0U || record.life_change_record_index != 0U || record.trigger_record_index != 0U || record.stack_placement_record_index != 0U || record.stack_resolution_record_index != 0U || record.priority_transition_record_index != 0U || record.state_based_action_record_index != 0U || record.combat_declaration_record_index != 0U || record.combat_damage_assignment_record_index != 0U || record.draw_record_index != 0U || record.mulligan_record_index != 0U) {
                    add_error(out, "event_record.extra_typed_link", prefix + " mulligan-keep row carries unrelated typed links");
                }
                break;
            case EventRecordKind::Count:
                break;
        }
    }

    u64 last_discard_sequence = 0;
    for (std::size_t i = 0; i < game.discard_records.size(); ++i) {
        const auto& record = game.discard_records[i];
        const std::string prefix = "discard_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "discard_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "discard_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_discard_sequence != 0U && record.sequence <= last_discard_sequence) {
            add_error(out, "discard_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_discard_sequence = record.sequence;
        if (i + 1U < discard_event_links.size() && discard_event_links[i + 1U] != 1U) {
            add_error(out, "discard_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(discard_event_links[i + 1U]));
        }
        if (record.kind == DiscardRecordKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(DiscardRecordKind::Count)) {
            add_error(out, "discard_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "discard_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (!is_valid_object_ref(game, record.card)) {
            add_error(out, "discard_record.invalid_card", prefix + " card=" + object_ref(record.card));
        }
        if (record.hand_size_before == 0U || record.hand_size_after + 1U != record.hand_size_before) {
            add_error(out, "discard_record.hand_size_mismatch", prefix + " discard should shrink hand size by one");
        }
        if (record.graveyard_size_after != record.graveyard_size_before + 1U) {
            add_error(out, "discard_record.graveyard_size_mismatch", prefix + " discard should increase graveyard size by one");
        }
        if (record.card_zone_change_index_before == 0U || record.card_zone_change_index_after == 0U || record.card_zone_change_index_after <= record.card_zone_change_index_before) {
            add_error(out, "discard_record.zone_change_index_not_advanced", prefix + " should advance the discarded card zone-change index");
        }
        if (!record.used_zone_change_pipeline) {
            add_error(out, "discard_record.zone_pipeline_not_used", prefix + " should use move_object for discard movement");
        }
        if (record.kind == DiscardRecordKind::CleanupHandSize) {
            if (!record.cleanup_hand_size || record.explicit_choice) {
                add_error(out, "discard_record.cleanup_flag_mismatch", prefix + " cleanup discard should be marked cleanup-only, not explicit-choice");
            }
            if (record.hand_size_before <= record.max_hand_size) {
                add_error(out, "discard_record.cleanup_not_required", prefix + " cleanup discard should only occur while hand size exceeds max_hand_size");
            }
        } else if (record.kind == DiscardRecordKind::ExplicitChoice) {
            if (!record.explicit_choice || record.cleanup_hand_size || record.cost_payment) {
                add_error(out, "discard_record.explicit_flag_mismatch", prefix + " explicit discard should be marked explicit-choice only");
            }
        } else if (record.kind == DiscardRecordKind::CostPayment) {
            if (!record.cost_payment || record.explicit_choice || record.cleanup_hand_size) {
                add_error(out, "discard_record.cost_payment_flag_mismatch", prefix + " cost-payment discard should be marked cost-payment only");
            }
        } else if (record.cost_payment) {
            add_error(out, "discard_record.unexpected_cost_payment_flag", prefix + " carries cost-payment metadata outside a cost-payment discard");
        }
        if (record.zone_change_record_index == 0U || record.zone_change_record_index > game.zone_change_records.size()) {
            add_error(out, "discard_record.invalid_zone_change_link", prefix + " links invalid zone_change_record_index=" + std::to_string(record.zone_change_record_index));
        } else {
            const auto& zone_record = game.zone_change_records[record.zone_change_record_index - 1U];
            if (zone_record.object != record.card) {
                add_error(out, "discard_record.zone_object_mismatch", prefix + " linked ZoneChangeRecord object does not match discarded card");
            }
            if (zone_record.previous_controller != record.player || zone_record.new_controller != record.player) {
                add_error(out, "discard_record.zone_controller_mismatch", prefix + " discard movement has wrong controller");
            }
            if (zone_record.from_zone != Zone::Hand || zone_record.requested_zone != Zone::Graveyard || zone_record.to_zone != Zone::Graveyard) {
                add_error(out, "discard_record.zone_path_mismatch", prefix + " discard movement should be hand->graveyard");
            }
        }
    }

    u64 last_draw_sequence = 0;
    for (std::size_t i = 0; i < game.draw_records.size(); ++i) {
        const auto& record = game.draw_records[i];
        const std::string prefix = "draw_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "draw_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "draw_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_draw_sequence != 0U && record.sequence <= last_draw_sequence) {
            add_error(out, "draw_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_draw_sequence = record.sequence;
        if (i + 1U < draw_event_links.size() && draw_event_links[i + 1U] != 1U) {
            add_error(out, "draw_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(draw_event_links[i + 1U]));
        }
        if (record.outcome == DrawRecordOutcome::Count || static_cast<u8>(record.outcome) >= static_cast<u8>(DrawRecordOutcome::Count)) {
            add_error(out, "draw_record.invalid_outcome", prefix + " has invalid outcome=" + std::string(to_string(record.outcome)));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "draw_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        switch (record.outcome) {
            case DrawRecordOutcome::DrewCard:
                if (!is_valid_object_ref(game, record.card)) {
                    add_error(out, "draw_record.invalid_card", prefix + " card=" + object_ref(record.card));
                }
                if (!record.card_moved) {
                    add_error(out, "draw_record.card_not_moved", prefix + " drew a card but card_moved=false");
                }
                if (record.empty_library_attempt) {
                    add_error(out, "draw_record.draw_marked_empty", prefix + " drew a card but empty_library_attempt=true");
                }
                if (record.library_size_before == 0U || record.library_size_after + 1U != record.library_size_before) {
                    add_error(out, "draw_record.library_size_mismatch", prefix + " draw should decrease library size by one");
                }
                if (record.hand_size_after != record.hand_size_before + 1U) {
                    add_error(out, "draw_record.hand_size_mismatch", prefix + " draw should increase hand size by one");
                }
                if (record.empty_library_draw_attempts_after != record.empty_library_draw_attempts_before) {
                    add_error(out, "draw_record.empty_attempt_changed", prefix + " successful draw changed empty-library attempt count");
                }
                if (record.card_zone_change_index_before == 0U || record.card_zone_change_index_after == 0U || record.card_zone_change_index_after <= record.card_zone_change_index_before) {
                    add_error(out, "draw_record.zone_change_index_not_advanced", prefix + " should advance the drawn card zone-change index");
                }
                if (record.zone_change_record_index == 0U || record.zone_change_record_index > game.zone_change_records.size()) {
                    add_error(out, "draw_record.invalid_zone_change_link", prefix + " links invalid zone_change_record_index=" + std::to_string(record.zone_change_record_index));
                } else {
                    const auto& zone_record = game.zone_change_records[record.zone_change_record_index - 1U];
                    if (zone_record.object != record.card) {
                        add_error(out, "draw_record.zone_change_object_mismatch", prefix + " linked ZoneChangeRecord belongs to a different card");
                    }
                    if (zone_record.from_zone != Zone::Library || zone_record.requested_zone != Zone::Hand || zone_record.to_zone != Zone::Hand) {
                        add_error(out, "draw_record.zone_change_path_mismatch", prefix + " linked movement should be library->hand");
                    }
                    if (zone_record.from_zone_change_index != record.card_zone_change_index_before || zone_record.to_zone_change_index != record.card_zone_change_index_after) {
                        add_error(out, "draw_record.zone_change_index_mismatch", prefix + " card and ZoneChangeRecord zone-change indexes disagree");
                    }
                }
                break;
            case DrawRecordOutcome::EmptyLibrary:
                if (record.card.valid()) {
                    add_error(out, "draw_record.empty_has_card", prefix + " empty-library draw unexpectedly has a card");
                }
                if (record.card_moved) {
                    add_error(out, "draw_record.empty_card_moved", prefix + " empty-library draw has card_moved=true");
                }
                if (!record.empty_library_attempt) {
                    add_error(out, "draw_record.empty_attempt_flag_missing", prefix + " empty-library draw missing empty_library_attempt flag");
                }
                if (record.zone_change_record_index != 0U || record.card_zone_change_index_before != 0U || record.card_zone_change_index_after != 0U) {
                    add_error(out, "draw_record.empty_zone_change", prefix + " empty-library draw should not have card movement metadata");
                }
                if (record.library_size_before != 0U || record.library_size_after != 0U || record.hand_size_after != record.hand_size_before) {
                    add_error(out, "draw_record.empty_size_mismatch", prefix + " empty-library draw should not move cards");
                }
                if (record.empty_library_draw_attempts_after != record.empty_library_draw_attempts_before + 1U) {
                    add_error(out, "draw_record.empty_attempt_count_mismatch", prefix + " empty-library attempt count should increase by one");
                }
                break;
            case DrawRecordOutcome::Count:
                break;
        }
    }

    u64 last_mulligan_sequence = 0;
    for (std::size_t i = 0; i < game.mulligan_records.size(); ++i) {
        const auto& record = game.mulligan_records[i];
        const std::string prefix = "mulligan_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "mulligan_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "mulligan_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_mulligan_sequence != 0U && record.sequence <= last_mulligan_sequence) {
            add_error(out, "mulligan_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_mulligan_sequence = record.sequence;
        if (i + 1U < mulligan_event_links.size() && mulligan_event_links[i + 1U] != 1U) {
            add_error(out, "mulligan_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(mulligan_event_links[i + 1U]));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "mulligan_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.mulligans_after != record.mulligans_before + 1U) {
            add_error(out, "mulligan_record.count_not_incremented", prefix + " should increment mulligans_taken by one");
        }
        if (record.returned_count != record.hand_size_before) {
            add_error(out, "mulligan_record.returned_count_mismatch", prefix + " returned_count should equal the hand size before the mulligan");
        }
        if (record.hand_size_after_return != 0U) {
            add_error(out, "mulligan_record.hand_not_cleared", prefix + " should return the whole hand to the library before drawing");
        }
        if (record.library_size_after_return != record.library_size_before + record.returned_count) {
            add_error(out, "mulligan_record.return_library_size_mismatch", prefix + " hand-to-library return should increase library size by returned_count");
        }
        if (record.library_size_after_shuffle != record.library_size_after_return) {
            add_error(out, "mulligan_record.shuffle_size_mismatch", prefix + " shuffle should not change library size");
        }
        if (record.draw_attempt_count != record.opening_hand_size || record.draw_record_count != record.draw_attempt_count) {
            add_error(out, "mulligan_record.draw_attempt_count_mismatch", prefix + " draw records should match opening_hand_size attempts");
        }
        if (record.hand_size_after != record.successful_draw_count) {
            add_error(out, "mulligan_record.hand_after_mismatch", prefix + " final hand size should equal successful mulligan draws");
        }
        if (record.library_size_after + record.successful_draw_count != record.library_size_after_shuffle) {
            add_error(out, "mulligan_record.draw_library_size_mismatch", prefix + " successful draws should reduce the post-shuffle library");
        }
        if (record.empty_library_draw_attempts_after != record.empty_library_draw_attempts_before + (record.draw_record_count - record.successful_draw_count)) {
            add_error(out, "mulligan_record.empty_attempt_count_mismatch", prefix + " empty-library attempt delta should match failed mulligan draws");
        }
        if (!record.shuffled) {
            add_error(out, "mulligan_record.not_shuffled", prefix + " should mark the deterministic library shuffle");
        }
        if (!record.used_zone_change_pipeline) {
            add_error(out, "mulligan_record.zone_pipeline_not_used", prefix + " should use move_object for hand-to-library returns");
        }
        if (!record.used_draw_pipeline) {
            add_error(out, "mulligan_record.draw_pipeline_not_used", prefix + " should use draw_card for redraw attempts");
        }
        if (record.returned_count == 0U) {
            if (record.first_return_zone_change_record_index != 0U || record.return_zone_change_record_count != 0U) {
                add_error(out, "mulligan_record.empty_return_has_zone_links", prefix + " should not link return movements when no cards were returned");
            }
        } else if (record.first_return_zone_change_record_index == 0U || record.return_zone_change_record_count != record.returned_count ||
                   record.first_return_zone_change_record_index + record.return_zone_change_record_count - 1U > game.zone_change_records.size()) {
            add_error(out, "mulligan_record.invalid_return_zone_change_range", prefix + " has an invalid hand-to-library ZoneChangeRecord range");
        } else {
            for (u32 j = 0; j < record.return_zone_change_record_count; ++j) {
                const auto& zone_record = game.zone_change_records[record.first_return_zone_change_record_index - 1U + j];
                if (zone_record.previous_controller != record.player || zone_record.new_controller != record.player) {
                    add_error(out, "mulligan_record.return_controller_mismatch", prefix + " return movement has the wrong controller");
                }
                if (zone_record.from_zone != Zone::Hand || zone_record.requested_zone != Zone::Library || zone_record.to_zone != Zone::Library) {
                    add_error(out, "mulligan_record.return_zone_path_mismatch", prefix + " return movement should be hand->library");
                }
            }
        }
        if (record.draw_record_count == 0U) {
            if (record.first_draw_record_index != 0U) {
                add_error(out, "mulligan_record.empty_draw_has_range", prefix + " should not link draw records when opening_hand_size is zero");
            }
        } else if (record.first_draw_record_index == 0U || record.first_draw_record_index + record.draw_record_count - 1U > game.draw_records.size()) {
            add_error(out, "mulligan_record.invalid_draw_record_range", prefix + " has an invalid DrawRecord range");
        } else {
            u32 successful_in_range = 0;
            for (u32 j = 0; j < record.draw_record_count; ++j) {
                const auto& draw_record = game.draw_records[record.first_draw_record_index - 1U + j];
                if (draw_record.player != record.player) {
                    add_error(out, "mulligan_record.draw_player_mismatch", prefix + " linked draw belongs to a different player");
                }
                if (draw_record.outcome == DrawRecordOutcome::DrewCard) {
                    ++successful_in_range;
                }
            }
            if (successful_in_range != record.successful_draw_count) {
                add_error(out, "mulligan_record.successful_draw_count_mismatch", prefix + " successful_draw_count disagrees with linked DrawRecords");
            }
        }
    }

    u64 last_mulligan_keep_sequence = 0;
    for (std::size_t i = 0; i < game.mulligan_keep_records.size(); ++i) {
        const auto& record = game.mulligan_keep_records[i];
        const std::string prefix = "mulligan_keep_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "mulligan_keep_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "mulligan_keep_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_mulligan_keep_sequence != 0U && record.sequence <= last_mulligan_keep_sequence) {
            add_error(out, "mulligan_keep_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_mulligan_keep_sequence = record.sequence;
        if (i + 1U < mulligan_keep_event_links.size() && mulligan_keep_event_links[i + 1U] != 1U) {
            add_error(out, "mulligan_keep_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(mulligan_keep_event_links[i + 1U]));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "mulligan_keep_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.bottom_count_required != record.mulligans_taken) {
            add_error(out, "mulligan_keep_record.required_count_mismatch", prefix + " bottom count should equal mulligans_taken");
        }
        if (record.bottom_count != record.bottom_count_required || record.bottom_count != record.bottomed_cards.size()) {
            add_error(out, "mulligan_keep_record.bottom_count_mismatch", prefix + " bottom_count should match required count and bottomed_cards size");
        }
        if (record.hand_size_before < record.bottom_count || record.hand_size_after + record.bottom_count != record.hand_size_before) {
            add_error(out, "mulligan_keep_record.hand_size_mismatch", prefix + " hand size should shrink by bottom_count");
        }
        if (record.library_size_after != record.library_size_before + record.bottom_count) {
            add_error(out, "mulligan_keep_record.library_size_mismatch", prefix + " library size should grow by bottom_count");
        }
        if (!record.explicit_choice && !record.deterministic_fallback && record.bottom_count != 0U) {
            add_error(out, "mulligan_keep_record.choice_source_missing", prefix + " should record explicit choice or deterministic fallback");
        }
        if (!record.used_zone_change_pipeline) {
            add_error(out, "mulligan_keep_record.zone_pipeline_not_used", prefix + " should use move_object for hand-to-library bottoming");
        }
        if (!record.placed_on_bottom) {
            add_error(out, "mulligan_keep_record.not_placed_on_bottom", prefix + " should record that bottomed cards were inserted at the library bottom");
        }
        std::vector<ObjectId> seen_bottomed;
        for (const auto card : record.bottomed_cards) {
            if (!is_valid_object_ref(game, card)) {
                add_error(out, "mulligan_keep_record.invalid_bottomed_card", prefix + " has invalid bottomed card " + object_ref(card));
            }
            if (std::find(seen_bottomed.begin(), seen_bottomed.end(), card) != seen_bottomed.end()) {
                add_error(out, "mulligan_keep_record.duplicate_bottomed_card", prefix + " lists a bottomed card more than once");
            }
            seen_bottomed.push_back(card);
        }
        if (record.bottom_count == 0U) {
            if (record.first_bottom_zone_change_record_index != 0U || record.bottom_zone_change_record_count != 0U) {
                add_error(out, "mulligan_keep_record.empty_bottom_has_zone_links", prefix + " should not link movements when no cards were bottomed");
            }
        } else if (record.first_bottom_zone_change_record_index == 0U || record.bottom_zone_change_record_count != record.bottom_count ||
                   record.first_bottom_zone_change_record_index + record.bottom_zone_change_record_count - 1U > game.zone_change_records.size()) {
            add_error(out, "mulligan_keep_record.invalid_bottom_zone_change_range", prefix + " has an invalid hand-to-library bottom ZoneChangeRecord range");
        } else {
            for (u32 j = 0; j < record.bottom_zone_change_record_count; ++j) {
                const auto& zone_record = game.zone_change_records[record.first_bottom_zone_change_record_index - 1U + j];
                if (j < record.bottomed_cards.size() && zone_record.object != record.bottomed_cards[j]) {
                    add_error(out, "mulligan_keep_record.bottom_object_mismatch", prefix + " linked ZoneChangeRecord does not match bottomed_cards order");
                }
                if (zone_record.previous_controller != record.player || zone_record.new_controller != record.player) {
                    add_error(out, "mulligan_keep_record.bottom_controller_mismatch", prefix + " bottom movement has the wrong controller");
                }
                if (zone_record.from_zone != Zone::Hand || zone_record.requested_zone != Zone::Library || zone_record.to_zone != Zone::Library) {
                    add_error(out, "mulligan_keep_record.bottom_zone_path_mismatch", prefix + " bottom movement should be hand->library");
                }
            }
        }
    }

    for (const auto& trigger : game.pending_triggers) {
        if (!is_valid_player_ref(game, trigger.controller)) {
            add_error(out, "trigger.invalid_controller", "pending trigger from " + trigger.source_name + " has " + player_ref(trigger.controller));
        }
        if (!is_valid_object_ref(game, trigger.source)) {
            add_error(out, "trigger.invalid_source", "pending trigger from " + trigger.source_name + " has " + object_ref(trigger.source));
        }
        if (!is_valid_object_ref(game, trigger.subject)) {
            add_error(out, "trigger.invalid_subject", "pending trigger from " + trigger.source_name + " has subject=" + object_ref(trigger.subject));
        }
        if (trigger.subject_zone_change_index == 0U) {
            add_error(out, "trigger.missing_subject_lki", "pending trigger from " + trigger.source_name + " has no subject zone-change snapshot");
        }
        if (trigger.event == TriggerEventKind::None || trigger.effect_kind == EffectKind::None) {
            add_error(out, "trigger.empty_payload", "pending trigger from " + trigger.source_name + " has no event/effect payload");
        }
        validate_target_definition(out, "trigger", "pending trigger from " + trigger.source_name, trigger.target_mask, trigger.target_count);
        if (trigger.source_zone_change_index == 0U) {
            add_warning(out, "trigger.missing_source_lki", "pending trigger from " + trigger.source_name + " has no source zone-change snapshot");
        }
        if (trigger.trigger_record_index == 0U) {
            if (!game.journal_trimmed) {
                add_error(out, "trigger.missing_record", "pending trigger from " + trigger.source_name + " is not linked to a valid TriggerRecord");
            }
        } else if (trigger.trigger_record_index > game.trigger_records.size()) {
            add_error(out, "trigger.missing_record", "pending trigger from " + trigger.source_name + " is not linked to a valid TriggerRecord");
        }
    }

    u64 last_trigger_sequence = 0;
    for (std::size_t i = 0; i < game.trigger_records.size(); ++i) {
        const auto& record = game.trigger_records[i];
        const std::string prefix = "trigger_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "trigger_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "trigger_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_trigger_sequence != 0U && record.sequence <= last_trigger_sequence) {
            add_error(out, "trigger_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_trigger_sequence = record.sequence;
        if (i + 1U < trigger_queued_event_links.size() && trigger_queued_event_links[i + 1U] != 1U) {
            add_error(out, "trigger_record.queue_event_record_link_count", prefix + " should have exactly one queued EventRecord link, found=" + std::to_string(trigger_queued_event_links[i + 1U]));
        }
        if (record.event == TriggerEventKind::None || record.event == TriggerEventKind::Count) {
            add_error(out, "trigger_record.invalid_event", prefix + " has no valid trigger event");
        }
        if (record.effect_kind == EffectKind::None || record.effect_kind == EffectKind::Count) {
            add_error(out, "trigger_record.invalid_effect", prefix + " has no valid effect payload");
        }
        validate_target_definition(out, "trigger_record", prefix, record.target_mask, record.target_count);
        const u32 expected_trigger_required_targets = required_target_count_for_validation(record.target_mask, record.target_count);
        validate_trigger_choice_targets(out, game, prefix, record, expected_trigger_required_targets);
        if (!is_valid_object_ref(game, record.subject)) {
            add_error(out, "trigger_record.invalid_subject", prefix + " subject=" + object_ref(record.subject));
        }
        if (record.subject_zone_change_index == 0U) {
            add_error(out, "trigger_record.missing_subject_zone_change_index", prefix + " missing subject zone-change snapshot");
        }
        if (!is_valid_player_ref(game, record.controller)) {
            add_error(out, "trigger_record.invalid_controller", prefix + " controller=" + player_ref(record.controller));
        }
        if (!is_valid_object_ref(game, record.source)) {
            add_error(out, "trigger_record.invalid_source", prefix + " source=" + object_ref(record.source));
        }
        if (record.source_zone_change_index == 0U) {
            add_error(out, "trigger_record.missing_source_zone_change_index", prefix + " missing source zone-change snapshot");
        }
        if ((record.source_color_mask & ~static_cast<u32>(ColorAll)) != 0U) {
            add_error(out, "trigger_record.invalid_source_color_mask", prefix + " has unknown source-color bits");
        }
        if ((record.source_ability_mask & ~legal_ability_mask) != 0U) {
            add_error(out, "trigger_record.invalid_source_ability_mask", prefix + " has unknown source-ability bits");
        }
        if (record.caused_by_event_sequence == 0U || record.caused_by_event_sequence >= game.next_event_sequence) {
            add_error(out, "trigger_record.invalid_cause_sequence", prefix + " has invalid caused-by sequence");
        }
        if (record.stack_resolution_record_index == 0U) {
            if (record.resolved_sequence != 0U || record.resolution_outcome != StackResolutionOutcome::Count || record.resolved_effect_payload_applied) {
                add_error(out, "trigger_record.resolution_fields_without_link", prefix + " carries resolution evidence without a StackResolutionRecord link");
            }
        } else {
            if (record.dropped) {
                add_error(out, "trigger_record.dropped_with_resolution_link", prefix + " is both dropped and linked to resolution");
            }
            if (record.put_on_stack_sequence == 0U || !record.stack_object.valid()) {
                add_error(out, "trigger_record.resolution_without_stack_object", prefix + " links resolution without a stacked ability object");
            }
            if (record.stack_resolution_record_index > game.stack_resolution_records.size()) {
                add_error(out, "trigger_record.invalid_stack_resolution_link", prefix + " links invalid StackResolutionRecord index=" + std::to_string(record.stack_resolution_record_index));
            } else {
                const auto& resolution_record = game.stack_resolution_records[record.stack_resolution_record_index - 1U];
                if (resolution_record.trigger_record_index != i + 1U) {
                    add_error(out, "trigger_record.resolution_backlink_mismatch", prefix + " linked StackResolutionRecord does not point back to this TriggerRecord");
                }
                if (resolution_record.stack_object != record.stack_object) {
                    add_error(out, "trigger_record.resolution_stack_object_mismatch", prefix + " linked StackResolutionRecord resolved a different stack object");
                }
                if (!resolution_record.ability_object) {
                    add_error(out, "trigger_record.resolution_not_ability", prefix + " linked StackResolutionRecord is not an ability resolution");
                }
                if (record.resolved_sequence != resolution_record.sequence) {
                    add_error(out, "trigger_record.resolution_sequence_mismatch", prefix + " resolved_sequence disagrees with linked StackResolutionRecord");
                }
                if (record.resolved_sequence <= record.put_on_stack_sequence) {
                    add_error(out, "trigger_record.resolution_not_after_stack", prefix + " resolved before or at its put-on-stack sequence");
                }
                if (record.resolution_outcome != resolution_record.outcome) {
                    add_error(out, "trigger_record.resolution_outcome_mismatch", prefix + " resolution_outcome disagrees with linked StackResolutionRecord");
                }
                if (record.resolved_effect_payload_applied != resolution_record.effect_payload_applied) {
                    add_error(out, "trigger_record.resolution_effect_payload_mismatch", prefix + " resolved_effect_payload_applied disagrees with linked StackResolutionRecord");
                }
                if (!exact_target_vectors_equal(record.chosen_targets, resolution_record.chosen_targets)) {
                    add_error(out, "trigger_record.resolution_targets_mismatch", prefix + " linked StackResolutionRecord chose different targets");
                }
                if (record.effect_kind != resolution_record.effect_kind || record.effect_amount != resolution_record.effect_amount ||
                    record.effect_counter_kind != resolution_record.effect_counter_kind || record.target_mask != resolution_record.target_mask ||
                    record.target_count != resolution_record.target_count) {
                    add_error(out, "trigger_record.resolution_payload_mismatch", prefix + " linked StackResolutionRecord payload differs from TriggerRecord payload");
                }
            }
        }
        if (record.put_on_stack_sequence != 0U) {
            if (record.put_on_stack_sequence < record.sequence || record.put_on_stack_sequence >= game.next_event_sequence) {
                add_error(out, "trigger_record.invalid_put_on_stack_sequence", prefix + " has invalid put-on-stack sequence");
            }
            if (!is_valid_object_ref(game, record.stack_object)) {
                add_error(out, "trigger_record.invalid_stack_object", prefix + " stack_object=" + object_ref(record.stack_object));
            } else if (!object(game, record.stack_object).ability_object) {
                add_error(out, "trigger_record.stack_object_not_ability", prefix + " stack_object is not an ability object");
            }
            if (record.stack_order == 0U) {
                add_error(out, "trigger_record.missing_stack_order", prefix + " was put on stack without stack_order");
            }
            if (!record.target_choice_recorded) {
                add_error(out, "trigger_record.stacked_without_choice_record", prefix + " was put on the stack without trigger target-choice evidence");
            }
            if (record.no_legal_choices) {
                add_error(out, "trigger_record.stacked_with_no_legal_choices", prefix + " was put on the stack despite no_legal_choices");
            }
            if (is_valid_object_ref(game, record.stack_object) && object(game, record.stack_object).zone == Zone::Stack &&
                !exact_target_vectors_equal(object(game, record.stack_object).targets, record.chosen_targets)) {
                add_error(out, "trigger_record.stack_object_targets_mismatch", prefix + " stack object targets differ from TriggerRecord chosen_targets while still on the stack");
            }
            if (i + 1U < trigger_stacked_event_links.size() && trigger_stacked_event_links[i + 1U] != 1U) {
                add_error(out, "trigger_record.stack_event_record_link_count", prefix + " should have exactly one put-on-stack EventRecord link, found=" + std::to_string(trigger_stacked_event_links[i + 1U]));
            }
        }
        if (record.dropped) {
            if (record.no_legal_choices && !record.target_choice_recorded) {
                add_error(out, "trigger_record.no_legal_drop_without_choice_record", prefix + " no-legal-choice drop is missing target-choice evidence");
            }
            if (record.dropped_sequence == 0U || record.dropped_sequence < record.sequence || record.dropped_sequence >= game.next_event_sequence) {
                add_error(out, "trigger_record.invalid_dropped_sequence", prefix + " has invalid dropped sequence");
            }
            if (record.stack_object.valid() || record.put_on_stack_sequence != 0U) {
                add_error(out, "trigger_record.dropped_and_stacked", prefix + " is both dropped and put on stack");
            }
            if (i + 1U < trigger_dropped_event_links.size() && trigger_dropped_event_links[i + 1U] != 1U) {
                add_error(out, "trigger_record.drop_event_record_link_count", prefix + " should have exactly one dropped EventRecord link, found=" + std::to_string(trigger_dropped_event_links[i + 1U]));
            }
        } else if (record.dropped_sequence != 0U) {
            add_error(out, "trigger_record.dropped_sequence_without_flag", prefix + " has dropped_sequence without dropped flag");
        }
    }

    for (const auto& shield : game.damage_prevention_shields) {
        if (shield.id == 0U) {
            add_error(out, "prevention.zero_shield_id", "damage-prevention shield has id=0");
        }
        if (shield.remaining == 0U) {
            add_error(out, "prevention.empty_shield", "damage-prevention shield has zero remaining amount");
        }
        if (shield.target.kind == TargetKind::None) {
            add_error(out, "prevention.empty_target", "damage-prevention shield has no target");
        } else if (shield.target.kind == TargetKind::Player) {
            if (!is_valid_player_ref(game, shield.target.player)) {
                add_error(out, "prevention.invalid_player", "damage-prevention shield targets " + player_ref(shield.target.player));
            }
        } else if (shield.target.kind == TargetKind::Object) {
            if (!is_valid_object_ref(game, shield.target.object)) {
                add_error(out, "prevention.invalid_object", "damage-prevention shield targets " + object_ref(shield.target.object));
            } else if (object(game, shield.target.object).zone != Zone::Battlefield) {
                add_error(out, "prevention.object_not_battlefield", "damage-prevention shield targets non-battlefield " + object_ref(shield.target.object));
            } else if (shield.target.object_zone_change_index == 0U) {
                add_error(out, "prevention.missing_target_zone_change_index", "object-targeted damage-prevention shield has no zone-change snapshot");
            } else if (shield.target.object_zone_change_index != object(game, shield.target.object).zone_change_index) {
                add_error(out, "prevention.stale_target_zone_change_index", "object-targeted damage-prevention shield has stale zone-change snapshot");
            }
        }
    }

    for (const auto& continuous : game.continuous_effects) {
        validate_static_effect_dependencies(out, continuous.effect, "continuous effect timestamp=" + std::to_string(continuous.timestamp), "continuous_effect");
        if (!continuous.active()) {
            add_error(out, "continuous_effect.inactive", "continuous effect timestamp=" + std::to_string(continuous.timestamp) + " has no active payload");
        }
        if (continuous.timestamp == 0U) {
            add_error(out, "continuous_effect.missing_timestamp", "continuous effect has timestamp 0");
        }
        if (continuous.duration == ContinuousEffectDuration::None || continuous.duration == ContinuousEffectDuration::Count) {
            add_error(out, "continuous_effect.invalid_duration", "continuous effect timestamp=" + std::to_string(continuous.timestamp) + " has duration=" + std::string(to_string(continuous.duration)));
        }
        if (!is_valid_player_ref(game, continuous.controller)) {
            add_error(out, "continuous_effect.invalid_controller", "continuous effect has " + player_ref(continuous.controller));
        }
        if (continuous.source.valid() && !is_valid_object_ref(game, continuous.source)) {
            add_error(out, "continuous_effect.invalid_source", "continuous effect source is " + object_ref(continuous.source));
        }
        for (const auto& locked : continuous.locked_targets) {
            if (locked.target.kind == TargetKind::Object) {
                if (!is_valid_object_ref(game, locked.target.object)) {
                    add_error(out, "continuous_effect.invalid_locked_object", "continuous effect target is " + object_ref(locked.target.object));
                }
            } else if (locked.target.kind == TargetKind::Player) {
                if (!is_valid_player_ref(game, locked.target.player)) {
                    add_error(out, "continuous_effect.invalid_locked_player", "continuous effect target is " + player_ref(locked.target.player));
                }
            } else {
                add_error(out, "continuous_effect.empty_locked_target", "continuous effect has an empty locked target");
            }
        }
    }

    if (!is_valid_player_ref(game, game.starting_player)) {
        add_error(out, "turn.invalid_starting_player", "starting_player=" + player_ref(game.starting_player));
    }
    if (!is_valid_player_ref(game, game.active_player)) {
        add_error(out, "turn.invalid_active_player", "active_player=" + player_ref(game.active_player));
    }
    if (game.priority_player.valid() && !is_valid_player_ref(game, game.priority_player)) {
        add_error(out, "turn.invalid_priority_player", "priority_player=" + player_ref(game.priority_player));
    }

    std::vector<u32> seen(game.objects.size(), 0U);
    for (const auto& p : game.players) {
        for (std::size_t zone_index_value = 0; zone_index_value < p.zones.size(); ++zone_index_value) {
            const auto zone_name = static_cast<Zone>(zone_index_value);
            if (zone_name == Zone::Stack || zone_name == Zone::Count) {
                if (!p.zones[zone_index_value].empty()) {
                    add_error(out, "zone.stack_stored_per_player", zone_ref(p.id, zone_name) + " should be empty; stack is game-global");
                }
                continue;
            }
            validate_container(game, out, seen, p.zones[zone_index_value], p.id, zone_name);
        }
    }
    validate_container(game, out, seen, game.stack, PlayerId{0}, Zone::Stack);

    for (std::size_t i = 0; i < seen.size(); ++i) {
        if (seen[i] == 0U) {
            if (!game.objects[i].ceased_to_exist) {
                add_error(out, "object.uncontained", "object#" + std::to_string(i + 1U) + " appears in no zone");
            }
        } else if (seen[i] > 1U) {
            add_error(out, "object.duplicated", "object#" + std::to_string(i + 1U) + " appears in " + std::to_string(seen[i]) + " zones/containers");
        }
    }

    const auto alive = alive_player_count(game);
    if (alive == 0U) {
        add_warning(out, "game.no_alive_players", "all players are currently marked lost");
    }
    u64 last_zone_change_sequence = 0;
    for (std::size_t i = 0; i < game.zone_change_records.size(); ++i) {
        const auto& record = game.zone_change_records[i];
        const std::string prefix = "zone_change_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "zone_change_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "zone_change_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_zone_change_sequence != 0U && record.sequence <= last_zone_change_sequence) {
            add_error(out, "zone_change_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_zone_change_sequence = record.sequence;
        if (i + 1U < zone_change_event_links.size() && zone_change_event_links[i + 1U] != 1U) {
            add_error(out, "zone_change_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(zone_change_event_links[i + 1U]));
        }
        if (!is_valid_object_ref(game, record.object)) {
            add_error(out, "zone_change_record.invalid_object", prefix + " references " + object_ref(record.object));
        }
        if (!is_valid_player_ref(game, record.owner)) {
            add_error(out, "zone_change_record.invalid_owner", prefix + " owner=" + player_ref(record.owner));
        }
        if (record.previous_controller.valid() && !is_valid_player_ref(game, record.previous_controller)) {
            add_error(out, "zone_change_record.invalid_previous_controller", prefix + " previous_controller=" + player_ref(record.previous_controller));
        }
        if (!is_valid_player_ref(game, record.new_controller)) {
            add_error(out, "zone_change_record.invalid_new_controller", prefix + " new_controller=" + player_ref(record.new_controller));
        }
        if (!is_valid_zone_ref(record.from_zone) || !is_valid_zone_ref(record.requested_zone) || !is_valid_zone_ref(record.to_zone)) {
            add_error(out, "zone_change_record.invalid_zone", prefix + " contains an invalid zone enum");
        }
        if (record.to_zone_change_index == 0U) {
            add_error(out, "zone_change_record.missing_to_zone_change_index", prefix + " missing finalized zone-change index");
        }
        if (record.from_zone_change_index != 0U && record.to_zone_change_index <= record.from_zone_change_index) {
            add_error(out, "zone_change_record.nonadvancing_zone_change_index", prefix + " finalized zone-change index did not advance");
        }
        if (record.replacement_applied != (record.replacement_record_count != 0U)) {
            add_error(out, "zone_change_record.replacement_count_mismatch", prefix + " replacement_applied flag disagrees with linked replacement-record count");
        }
        if (record.first_replacement_record_index == 0U && record.replacement_record_count != 0U) {
            add_error(out, "zone_change_record.missing_first_replacement", prefix + " has replacement records but no first_replacement_record_index");
        }
        if (record.first_replacement_record_index != 0U) {
            const u64 last_index = static_cast<u64>(record.first_replacement_record_index) + static_cast<u64>(record.replacement_record_count) - 1ULL;
            if (record.replacement_record_count == 0U || last_index > game.zone_change_replacement_records.size()) {
                add_error(out, "zone_change_record.invalid_replacement_range", prefix + " links replacement-record range outside GameState::zone_change_replacement_records");
            } else {
                Zone expected_event_to_zone = record.requested_zone;
                std::vector<std::size_t> applied_replacement_offsets;
                applied_replacement_offsets.reserve(record.replacement_record_count);
                const PlayerId expected_affected_player = record.previous_controller.valid() ? record.previous_controller : record.owner;
                for (u32 offset = 0; offset < record.replacement_record_count; ++offset) {
                    const auto& replacement_record = game.zone_change_replacement_records[record.first_replacement_record_index - 1U + offset];
                    if (replacement_record.zone_change_record_index != i + 1U) {
                        add_error(out, "zone_change_record.replacement_backlink_mismatch", prefix + " linked replacement record does not point back to this ZoneChangeRecord");
                    }
                    if (replacement_record.object != record.object || replacement_record.from_zone != record.from_zone) {
                        add_error(out, "zone_change_record.replacement_subject_mismatch", prefix + " linked replacement record has a different object or source zone");
                    }
                    if (replacement_record.affected_player != expected_affected_player) {
                        add_error(out, "zone_change_record.replacement_affected_player_mismatch", prefix + " linked replacement record affected player does not match the moved object's pre-move controller/owner");
                    }
                    if (replacement_record.pass_index != offset + 1U) {
                        add_error(out, "zone_change_record.replacement_pass_mismatch", prefix + " linked replacement record pass_index does not match its contiguous range position");
                    }
                    if (replacement_record.event_to_zone != expected_event_to_zone) {
                        add_error(out,
                                  offset == 0U ? "zone_change_record.first_replacement_request_mismatch" : "zone_change_record.replacement_chain_mismatch",
                                  prefix + " replacement chain event_to_zone does not match the requested destination or previous replacement result");
                    }
                    for (const auto seen_offset : applied_replacement_offsets) {
                        const auto& seen_replacement = game.zone_change_replacement_records[record.first_replacement_record_index - 1U + static_cast<u32>(seen_offset)];
                        if (seen_replacement.source == replacement_record.source &&
                            seen_replacement.definition_index == replacement_record.definition_index &&
                            seen_replacement.source_zone_change_index == replacement_record.source_zone_change_index) {
                            add_error(out, "zone_change_record.duplicate_replacement_effect", prefix + " applies the same replacement source/definition/LKI more than once in one event chain");
                        }
                    }
                    applied_replacement_offsets.push_back(offset);
                    expected_event_to_zone = replacement_record.replacement_zone;
                    if (offset + 1U == record.replacement_record_count && replacement_record.replacement_zone != record.to_zone) {
                        add_error(out, "zone_change_record.final_replacement_zone_mismatch", prefix + " final replacement record does not match finalized destination");
                    }
                }
            }
        }
        if (record.first_counter_change_record_index == 0U && record.counter_change_record_count != 0U) {
            add_error(out, "zone_change_record.missing_first_counter_change", prefix + " has counter cleanup records but no first_counter_change_record_index");
        }
        if (record.first_counter_change_record_index != 0U) {
            const u64 last_index = static_cast<u64>(record.first_counter_change_record_index) + static_cast<u64>(record.counter_change_record_count) - 1ULL;
            if (record.counter_change_record_count == 0U || last_index > game.counter_change_records.size()) {
                add_error(out, "zone_change_record.invalid_counter_change_range", prefix + " links counter-change range outside GameState::counter_change_records");
            } else {
                for (u32 offset = 0; offset < record.counter_change_record_count; ++offset) {
                    const auto& counter_record = game.counter_change_records[record.first_counter_change_record_index - 1U + offset];
                    if (counter_record.zone_change_record_index != i + 1U) {
                        add_error(out, "zone_change_record.counter_change_backlink_mismatch", prefix + " linked CounterChangeRecord does not point back to this ZoneChangeRecord");
                    }
                    if (counter_record.object != record.object) {
                        add_error(out, "zone_change_record.counter_change_object_mismatch", prefix + " linked CounterChangeRecord belongs to a different object");
                    }
                    if (!counter_record.zone_change_cleanup || counter_record.kind != CounterChangeKind::ObjectRemoved || counter_record.count_after != 0U) {
                        add_error(out, "zone_change_record.counter_change_not_cleanup", prefix + " linked CounterChangeRecord is not an object counter cleanup removal");
                    }
                    if (counter_record.sequence <= record.sequence) {
                        add_error(out, "zone_change_record.counter_change_sequence_order", prefix + " linked counter cleanup should be recorded after the zone-change event");
                    }
                }
            }
        }
        if (record.first_damage_prevention_record_index == 0U && record.damage_prevention_record_count != 0U) {
            add_error(out, "zone_change_record.missing_first_damage_prevention", prefix + " has prevention-expiry records but no first_damage_prevention_record_index");
        }
        if (record.first_damage_prevention_record_index != 0U) {
            const u64 last_index = static_cast<u64>(record.first_damage_prevention_record_index) + static_cast<u64>(record.damage_prevention_record_count) - 1ULL;
            if (record.damage_prevention_record_count == 0U || last_index > game.damage_prevention_records.size()) {
                add_error(out, "zone_change_record.invalid_damage_prevention_range", prefix + " links prevention-record range outside GameState::damage_prevention_records");
            } else {
                for (u32 offset = 0; offset < record.damage_prevention_record_count; ++offset) {
                    const auto& prevention_record = game.damage_prevention_records[record.first_damage_prevention_record_index - 1U + offset];
                    if (prevention_record.zone_change_record_index != i + 1U) {
                        add_error(out, "zone_change_record.damage_prevention_backlink_mismatch", prefix + " linked DamagePreventionRecord does not point back to this ZoneChangeRecord");
                    }
                    if (prevention_record.kind != DamagePreventionRecordKind::ShieldExpired) {
                        add_error(out, "zone_change_record.damage_prevention_not_expiry", prefix + " linked DamagePreventionRecord is not a shield-expiry row");
                    }
                    if (prevention_record.target.kind != TargetKind::Object || prevention_record.target.object != record.object) {
                        add_error(out, "zone_change_record.damage_prevention_object_mismatch", prefix + " linked DamagePreventionRecord belongs to a different object");
                    }
                    if (prevention_record.sequence <= record.sequence) {
                        add_error(out, "zone_change_record.damage_prevention_sequence_order", prefix + " linked prevention expiry should be recorded after the zone-change event");
                    }
                }
            }
        }
    }

    u64 last_zone_replacement_sequence = 0;
    for (std::size_t i = 0; i < game.zone_change_replacement_records.size(); ++i) {
        const auto& record = game.zone_change_replacement_records[i];
        const std::string prefix = "zone_replacement_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "zone_replacement_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "zone_replacement_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_zone_replacement_sequence != 0U && record.sequence <= last_zone_replacement_sequence) {
            add_error(out, "zone_replacement_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_zone_replacement_sequence = record.sequence;
        if (i + 1U < zone_replacement_event_links.size() && zone_replacement_event_links[i + 1U] != 1U) {
            add_error(out, "zone_replacement_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(zone_replacement_event_links[i + 1U]));
        }
        if (!is_valid_object_ref(game, record.object)) {
            add_error(out, "zone_replacement_record.invalid_object", prefix + " object=" + object_ref(record.object));
        }
        if (!is_valid_player_ref(game, record.affected_player)) {
            add_error(out, "zone_replacement_record.invalid_affected_player", prefix + " affected_player=" + player_ref(record.affected_player));
        }
        if (!is_valid_player_ref(game, record.controller)) {
            add_error(out, "zone_replacement_record.invalid_controller", prefix + " controller=" + player_ref(record.controller));
        }
        if (!is_valid_object_ref(game, record.source)) {
            add_error(out, "zone_replacement_record.invalid_source", prefix + " source=" + object_ref(record.source));
        }
        if (!is_valid_zone_ref(record.from_zone) || !is_valid_zone_ref(record.event_to_zone) || !is_valid_zone_ref(record.replacement_zone)) {
            add_error(out, "zone_replacement_record.invalid_zone", prefix + " contains an invalid zone enum");
        }
        if (record.event_to_zone == record.replacement_zone) {
            add_error(out, "zone_replacement_record.noop_replacement", prefix + " does not change the destination zone");
        }
        if (static_cast<u8>(record.priority_tier) >= static_cast<u8>(ReplacementPriorityTier::Count)) {
            add_error(out, "zone_replacement_record.invalid_priority_tier", prefix + " has priority_tier=" + std::string(to_string(record.priority_tier)));
        }
        if (static_cast<u8>(record.candidate_min_priority_tier) >= static_cast<u8>(ReplacementPriorityTier::Count)) {
            add_error(out, "zone_replacement_record.invalid_candidate_min_priority_tier", prefix + " has candidate_min_priority_tier=" + std::string(to_string(record.candidate_min_priority_tier)));
        }
        if (record.candidate_count == 0U) {
            add_error(out, "zone_replacement_record.zero_candidates", prefix + " has candidate_count=0");
        }
        if (record.eligible_candidate_count == 0U) {
            add_error(out, "zone_replacement_record.zero_eligible_candidates", prefix + " has eligible_candidate_count=0");
        }
        if (record.eligible_candidate_count > record.candidate_count) {
            add_error(out, "zone_replacement_record.eligible_candidates_exceed_candidates", prefix + " has eligible_candidate_count greater than candidate_count");
        }
        if (record.priority_tier != record.candidate_min_priority_tier &&
            static_cast<u8>(record.priority_tier) < static_cast<u8>(ReplacementPriorityTier::Count) &&
            static_cast<u8>(record.candidate_min_priority_tier) < static_cast<u8>(ReplacementPriorityTier::Count)) {
            add_error(out, "zone_replacement_record.priority_tier_skip", prefix + " chose priority_tier=" + std::string(to_string(record.priority_tier)) +
                          " while candidate_min_priority_tier=" + std::string(to_string(record.candidate_min_priority_tier)));
        }
        if (record.chosen_among_multiple != (record.eligible_candidate_count > 1U)) {
            add_error(out, "zone_replacement_record.choice_flag_mismatch", prefix + " chosen_among_multiple disagrees with eligible_candidate_count");
        }
        if (record.pass_index == 0U) {
            add_error(out, "zone_replacement_record.zero_pass_index", prefix + " has pass_index=0");
        }
        if (record.source_zone_change_index == 0U) {
            add_error(out, "zone_replacement_record.missing_source_zone_change_index", prefix + " missing source zone-change LKI");
        }
        if (record.zone_change_record_index == 0U || record.zone_change_record_index > game.zone_change_records.size()) {
            add_error(out, "zone_replacement_record.invalid_zone_change_link", prefix + " links invalid zone_change_record_index=" + std::to_string(record.zone_change_record_index));
        } else {
            const auto& zone_record = game.zone_change_records[record.zone_change_record_index - 1U];
            if (zone_record.object != record.object) {
                add_error(out, "zone_replacement_record.zone_change_object_mismatch", prefix + " linked ZoneChangeRecord belongs to a different object");
            }
            if (zone_record.from_zone != record.from_zone) {
                add_error(out, "zone_replacement_record.zone_change_from_mismatch", prefix + " linked ZoneChangeRecord has a different source zone");
            }
            const u32 self_index = static_cast<u32>(i + 1U);
            const u32 first_index = zone_record.first_replacement_record_index;
            const u32 count = zone_record.replacement_record_count;
            const bool owned_by_linked_range = first_index != 0U && count != 0U &&
                self_index >= first_index && self_index < first_index + count;
            if (!owned_by_linked_range) {
                add_error(out, "zone_replacement_record.zone_change_range_ownership_mismatch", prefix + " points at a ZoneChangeRecord that does not own this replacement row in its contiguous range");
            }
        }
    }

    u64 last_damage_sequence = 0;
    for (std::size_t i = 0; i < game.damage_records.size(); ++i) {
        const auto& record = game.damage_records[i];
        const std::string prefix = "damage_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "damage_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "damage_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_damage_sequence != 0U && record.sequence <= last_damage_sequence) {
            add_error(out, "damage_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_damage_sequence = record.sequence;
        if (i + 1U < damage_event_links.size() && damage_event_links[i + 1U] != 1U) {
            add_error(out, "damage_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(damage_event_links[i + 1U]));
        }
        if (record.source.valid() && !is_valid_object_ref(game, record.source)) {
            add_error(out, "damage_record.invalid_source", prefix + " source=" + object_ref(record.source));
        }
        if (record.source.valid() && record.source_zone_change_index == 0U) {
            add_error(out, "damage_record.missing_source_zone_change_index", prefix + " has a source but no source zone-change index");
        }
        if (record.source_controller.valid() && !is_valid_player_ref(game, record.source_controller)) {
            add_error(out, "damage_record.invalid_source_controller", prefix + " source_controller=" + player_ref(record.source_controller));
        }
        if ((record.source_color_mask & ~static_cast<u32>(ColorAll)) != 0U) {
            add_error(out, "damage_record.invalid_source_color_mask", prefix + " has unknown source-color bits");
        }
        if ((record.source_ability_mask & ~legal_ability_mask) != 0U) {
            add_error(out, "damage_record.invalid_source_ability_mask", prefix + " has unknown source-ability bits");
        }
        if (record.amount == 0U) {
            add_error(out, "damage_record.zero_amount", prefix + " has amount=0");
        }
        if (static_cast<u64>(record.prevented) + static_cast<u64>(record.dealt) + static_cast<u64>(record.not_dealt) != static_cast<u64>(record.amount)) {
            add_error(out, "damage_record.amount_mismatch", prefix + " has prevented+dealt+not_dealt != amount");
        }
        if (record.prevented_by_protection && (record.prevented != record.amount || record.dealt != 0U || record.not_dealt != 0U)) {
            add_error(out, "damage_record.protection_amount_mismatch", prefix + " was protection-prevented but does not have prevented=amount and dealt=0 and not_dealt=0");
        }
        if (record.not_dealt != 0U && !record.damage_disallowed_by_target_type) {
            add_error(out, "damage_record.not_dealt_without_disallowance", prefix + " records not_dealt without a target-type disallowance");
        }
        if (record.damage_disallowed_by_target_type) {
            if (record.target.kind != TargetKind::Object) {
                add_error(out, "damage_record.disallowed_non_object_target", prefix + " disallowed target-type damage for a non-object target");
            }
            if (record.target_was_damageable) {
                add_error(out, "damage_record.disallowed_damageable_target", prefix + " disallowed damage even though the target snapshot was damageable");
            }
            if (record.not_dealt != record.amount || record.prevented != 0U || record.dealt != 0U) {
                add_error(out, "damage_record.disallowed_amount_mismatch", prefix + " should record all requested damage as not_dealt and none prevented/dealt");
            }
            if (record.prevented_by_protection || record.protection_prevention_ignored || record.damage_prevention_record_count != 0U || record.first_damage_prevention_record_index != 0U) {
                add_error(out, "damage_record.disallowed_has_prevention_metadata", prefix + " target-type-disallowed damage should not consume protection/prevention evidence");
            }
            if (record.counters_removed != 0U || record.first_damage_counter_change_record_index != 0U || record.damage_counter_change_record_count != 0U) {
                add_error(out, "damage_record.disallowed_has_counter_metadata", prefix + " target-type-disallowed damage should not carry counter-result evidence");
            }
            if (record.first_damage_life_change_record_index != 0U || record.damage_life_change_record_count != 0U) {
                add_error(out, "damage_record.disallowed_has_life_metadata", prefix + " target-type-disallowed damage should not carry life-result evidence");
            }
        }
        if (record.unpreventable && record.prevented != 0U) {
            add_error(out, "damage_record.unpreventable_has_prevented_amount", prefix + " is unpreventable but records prevented damage");
        }
        if (record.unpreventable && record.prevented_by_protection) {
            add_error(out, "damage_record.unpreventable_protection_prevented", prefix + " cannot be both unpreventable and protection-prevented");
        }
        if (record.protection_prevention_ignored && !record.unpreventable) {
            add_error(out, "damage_record.protection_ignored_not_unpreventable", prefix + " ignored protection without unpreventable damage");
        }
        if (record.protection_prevention_ignored && record.prevented_by_protection) {
            add_error(out, "damage_record.protection_ignored_and_prevented", prefix + " both ignored and applied protection prevention");
        }
        switch (record.target.kind) {
            case TargetKind::Player:
                if (!is_valid_player_ref(game, record.target.player)) {
                    add_error(out, "damage_record.invalid_target_player", prefix + " target=" + player_ref(record.target.player));
                }
                if (record.target_zone_change_index != 0U) {
                    add_error(out, "damage_record.player_target_zone_change_index", prefix + " player target unexpectedly has object zone-change metadata");
                }
                if (!record.target_was_damageable) {
                    add_error(out, "damage_record.player_target_not_damageable", prefix + " player target should be damageable");
                }
                if (record.target_was_creature || record.target_was_planeswalker || record.target_was_battle) {
                    add_error(out, "damage_record.player_target_has_object_kind_flags", prefix + " player target unexpectedly has object kind flags");
                }
                break;
            case TargetKind::Object:
                if (!is_valid_object_ref(game, record.target.object)) {
                    add_error(out, "damage_record.invalid_target_object", prefix + " target=" + object_ref(record.target.object));
                }
                if (record.target_zone_change_index == 0U) {
                    add_error(out, "damage_record.missing_target_zone_change_index", prefix + " object target missing zone-change snapshot");
                }
                if (record.target.object_zone_change_index != record.target_zone_change_index) {
                    add_error(out, "damage_record.target_zone_change_index_mismatch", prefix + " target ref and record disagree on object zone-change snapshot");
                }
                if (record.target_was_damageable != (record.target_was_creature || record.target_was_planeswalker || record.target_was_battle)) {
                    add_error(out, "damage_record.object_damageable_flag_mismatch", prefix + " object target damageability flag disagrees with creature/planeswalker/battle snapshot flags");
                }
                if (!record.target_was_damageable && !record.damage_disallowed_by_target_type) {
                    add_error(out, "damage_record.undamageable_object_dealt", prefix + " object target was not a battle, creature, or planeswalker but damage was not disallowed");
                }
                break;
            case TargetKind::None:
                add_error(out, "damage_record.missing_target", prefix + " has no target");
                break;
        }
        if (record.prevented_by_protection && record.damage_prevention_record_count != 0U) {
            add_error(out, "damage_record.protection_has_shield_records", prefix + " was protection-prevented but links shield prevention records");
        }
        if (!record.prevented_by_protection && record.prevented != 0U && record.damage_prevention_record_count == 0U) {
            add_error(out, "damage_record.missing_prevention_record_range", prefix + " prevented shield damage but has no DamagePreventionRecord range");
        }
        if (!record.unpreventable && record.prevented == 0U && record.damage_prevention_record_count != 0U) {
            add_error(out, "damage_record.unexpected_prevention_record_range", prefix + " links shield records without prevented or unpreventable damage");
        }
        if (record.first_damage_prevention_record_index == 0U && record.damage_prevention_record_count != 0U) {
            add_error(out, "damage_record.missing_first_prevention_record", prefix + " has prevention records but no first_damage_prevention_record_index");
        }
        if (record.first_damage_prevention_record_index != 0U) {
            const u64 last_index = static_cast<u64>(record.first_damage_prevention_record_index) + static_cast<u64>(record.damage_prevention_record_count) - 1ULL;
            if (record.damage_prevention_record_count == 0U || last_index > game.damage_prevention_records.size()) {
                add_error(out, "damage_record.invalid_prevention_record_range", prefix + " links prevention-record range outside GameState::damage_prevention_records");
            } else {
                u32 prevented_from_records = 0;
                for (u32 offset = 0; offset < record.damage_prevention_record_count; ++offset) {
                    const auto& prevention_record = game.damage_prevention_records[record.first_damage_prevention_record_index - 1U + offset];
                    if (prevention_record.kind != DamagePreventionRecordKind::ShieldConsumed &&
                        prevention_record.kind != DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage) {
                        add_error(out, "damage_record.prevention_range_invalid_kind", prefix + " linked prevention record is not applicable to a damage event");
                    }
                    if (prevention_record.kind == DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage && !record.unpreventable) {
                        add_error(out, "damage_record.unpreventable_prevention_record_on_preventable_damage", prefix + " links unpreventable shield-application row for preventable damage");
                    }
                    if (prevention_record.kind == DamagePreventionRecordKind::ShieldConsumed && record.unpreventable) {
                        add_error(out, "damage_record.consumed_prevention_on_unpreventable_damage", prefix + " consumed a shield for unpreventable damage");
                    }
                    if (prevention_record.damage_record_index != i + 1U) {
                        add_error(out, "damage_record.prevention_backlink_mismatch", prefix + " linked prevention record does not point back to this DamageRecord");
                    }
                    if (!(prevention_record.target == record.target)) {
                        add_error(out, "damage_record.prevention_target_mismatch", prefix + " linked prevention record target differs from damage target");
                    }
                    if (prevention_record.sequence >= record.sequence) {
                        add_error(out, "damage_record.prevention_sequence_order", prefix + " linked prevention record should be recorded before the final DamageRecord");
                    }
                    if (prevention_record.kind == DamagePreventionRecordKind::ShieldConsumed) {
                        prevented_from_records += prevention_record.amount;
                    }
                }
                if (prevented_from_records != record.prevented) {
                    add_error(out, "damage_record.prevention_amount_mismatch", prefix + " linked prevention rows do not sum to DamageRecord::prevented");
                }
            }
        }
        if (record.first_damage_counter_change_record_index == 0U && record.damage_counter_change_record_count != 0U) {
            add_error(out, "damage_record.missing_first_counter_change_record", prefix + " has damage counter-change records but no first_damage_counter_change_record_index");
        }
        if (record.counters_removed != 0U && record.damage_counter_change_record_count == 0U) {
            add_error(out, "damage_record.missing_counter_change_range", prefix + " removed loyalty/defense counters but has no CounterChangeRecord range");
        }
        if (record.counters_removed == 0U && record.damage_counter_change_record_count != 0U) {
            add_error(out, "damage_record.unexpected_counter_change_range", prefix + " links counter-change records without removed counters");
        }
        if ((record.target.kind != TargetKind::Object || (!record.target_was_planeswalker && !record.target_was_battle)) &&
            (record.counters_removed != 0U || record.first_damage_counter_change_record_index != 0U || record.damage_counter_change_record_count != 0U)) {
            add_error(out, "damage_record.counter_range_on_non_counter_damage_target", prefix + " carries loyalty/defense counter evidence for a non-planeswalker/non-battle damage target");
        }
        if (record.first_damage_counter_change_record_index != 0U) {
            const u64 last_index = static_cast<u64>(record.first_damage_counter_change_record_index) + static_cast<u64>(record.damage_counter_change_record_count) - 1ULL;
            if (record.damage_counter_change_record_count == 0U || last_index > game.counter_change_records.size()) {
                add_error(out, "damage_record.invalid_counter_change_range", prefix + " links counter-change range outside GameState::counter_change_records");
            } else {
                u32 counters_from_records = 0;
                for (u32 offset = 0; offset < record.damage_counter_change_record_count; ++offset) {
                    const auto& counter_record = game.counter_change_records[record.first_damage_counter_change_record_index - 1U + offset];
                    if (!counter_record.damage_result) {
                        add_error(out, "damage_record.counter_change_not_damage_result", prefix + " linked counter-change row is not marked as a damage result");
                    }
                    if (counter_record.cost_payment || counter_record.zone_change_cleanup) {
                        add_error(out, "damage_record.counter_change_wrong_cause", prefix + " linked damage-result counter-change row is also marked as a cost or zone cleanup");
                    }
                    if (counter_record.kind != CounterChangeKind::ObjectRemoved) {
                        add_error(out, "damage_record.counter_change_not_object_removed", prefix + " linked damage-result counter-change row did not remove object counters");
                    }
                    if (record.target.kind != TargetKind::Object || counter_record.object != record.target.object) {
                        add_error(out, "damage_record.counter_change_object_mismatch", prefix + " linked damage-result counter-change row targets a different object");
                    }
                    if (counter_record.source != record.source) {
                        add_error(out, "damage_record.counter_change_source_mismatch", prefix + " linked damage-result counter-change row has a different damage source");
                    }
                    if (record.source.valid() && counter_record.source_zone_change_index != record.source_zone_change_index) {
                        add_error(out, "damage_record.counter_change_source_zone_mismatch", prefix + " linked damage-result counter-change row has a different source zone identity");
                    }
                    if (counter_record.sequence >= record.sequence) {
                        add_error(out, "damage_record.counter_change_sequence_order", prefix + " linked counter-change row should be recorded before the final DamageRecord");
                    }
                    if (counter_record.counter_kind == CounterKind::Loyalty) {
                        if (!record.target_was_planeswalker) {
                            add_error(out, "damage_record.loyalty_counter_change_on_non_planeswalker", prefix + " links loyalty damage-result counters for a target that was not a planeswalker");
                        }
                    } else if (counter_record.counter_kind == CounterKind::Defense) {
                        if (!record.target_was_battle) {
                            add_error(out, "damage_record.defense_counter_change_on_non_battle", prefix + " links defense damage-result counters for a target that was not a battle");
                        }
                    } else {
                        add_error(out, "damage_record.counter_change_kind_mismatch", prefix + " linked damage-result counter-change row is not loyalty or defense");
                    }
                    counters_from_records += counter_record.amount;
                }
                if (counters_from_records != record.counters_removed) {
                    add_error(out, "damage_record.counter_change_amount_mismatch", prefix + " linked damage-result counter-change rows do not sum to DamageRecord::counters_removed");
                }
            }
        }
        if (record.first_damage_life_change_record_index == 0U && record.damage_life_change_record_count != 0U) {
            add_error(out, "damage_record.missing_first_life_change_record", prefix + " has damage life-change records but no first_damage_life_change_record_index");
        }
        if (record.dealt == 0U && record.damage_life_change_record_count != 0U) {
            add_error(out, "damage_record.life_change_range_without_dealt_damage", prefix + " links life-change records even though no damage was dealt");
        }
        if (record.target.kind == TargetKind::Player && record.dealt != 0U && record.damage_life_change_record_count == 0U) {
            add_error(out, "damage_record.missing_player_life_change_range", prefix + " dealt damage to a player but has no LifeChangeRecord range");
        }
        if (record.source_had_lifelink && record.dealt != 0U && is_valid_player_ref(game, record.source_controller) && record.damage_life_change_record_count == 0U) {
            add_error(out, "damage_record.missing_lifelink_life_change_range", prefix + " dealt lifelink damage but has no LifeChangeRecord range");
        }
        if (record.target.kind != TargetKind::Player && !record.source_had_lifelink && record.damage_life_change_record_count != 0U) {
            add_error(out, "damage_record.unexpected_nonplayer_life_change_range", prefix + " links life-change records for non-player, non-lifelink damage");
        }
        if (record.first_damage_life_change_record_index != 0U) {
            const u64 last_index = static_cast<u64>(record.first_damage_life_change_record_index) + static_cast<u64>(record.damage_life_change_record_count) - 1ULL;
            if (record.damage_life_change_record_count == 0U || last_index > game.life_change_records.size()) {
                add_error(out, "damage_record.invalid_life_change_range", prefix + " links life-change range outside GameState::life_change_records");
            } else {
                u32 loss_rows = 0;
                u32 gain_rows = 0;
                for (u32 offset = 0; offset < record.damage_life_change_record_count; ++offset) {
                    const auto& life_record = game.life_change_records[record.first_damage_life_change_record_index - 1U + offset];
                    if (!life_record.damage_result) {
                        add_error(out, "damage_record.life_change_not_damage_result", prefix + " linked LifeChangeRecord is not marked as a damage result");
                    }
                    if (life_record.damage_record_index != i + 1U) {
                        add_error(out, "damage_record.life_change_backlink_mismatch", prefix + " linked LifeChangeRecord does not point back to this DamageRecord");
                    }
                    if (!same_target_snapshot_for_validation(life_record.damage_target, record.target)) {
                        add_error(out, "damage_record.life_change_target_mismatch", prefix + " linked LifeChangeRecord has a different damage target snapshot");
                    }
                    if (life_record.damage_source != record.source) {
                        add_error(out, "damage_record.life_change_source_mismatch", prefix + " linked LifeChangeRecord has a different damage source");
                    }
                    if (record.source.valid() && life_record.damage_source_zone_change_index != record.source_zone_change_index) {
                        add_error(out, "damage_record.life_change_source_zone_mismatch", prefix + " linked LifeChangeRecord has a different source zone identity");
                    }
                    if (life_record.sequence >= record.sequence) {
                        add_error(out, "damage_record.life_change_sequence_order", prefix + " linked LifeChangeRecord should be recorded before the final DamageRecord");
                    }
                    if (life_record.amount != static_cast<std::int32_t>(record.dealt)) {
                        add_error(out, "damage_record.life_change_amount_mismatch", prefix + " linked LifeChangeRecord amount does not equal DamageRecord::dealt");
                    }
                    if (life_record.kind == LifeChangeKind::Loss) {
                        ++loss_rows;
                        if (record.target.kind != TargetKind::Player || life_record.player != record.target.player) {
                            add_error(out, "damage_record.life_loss_target_mismatch", prefix + " linked life-loss row does not belong to the damaged player");
                        }
                        if (life_record.lifelink_result) {
                            add_error(out, "damage_record.life_loss_marked_lifelink", prefix + " linked life-loss row is incorrectly marked as lifelink");
                        }
                    } else if (life_record.kind == LifeChangeKind::Gain) {
                        ++gain_rows;
                        if (!record.source_had_lifelink) {
                            add_error(out, "damage_record.life_gain_without_lifelink", prefix + " links a life-gain row for non-lifelink damage");
                        }
                        if (is_valid_player_ref(game, record.source_controller) && life_record.player != record.source_controller) {
                            add_error(out, "damage_record.lifelink_controller_mismatch", prefix + " linked lifelink gain row does not belong to the source controller");
                        }
                        if (!life_record.lifelink_result) {
                            add_error(out, "damage_record.life_gain_missing_lifelink_flag", prefix + " linked life-gain row is not marked as a lifelink result");
                        }
                    }
                }
                if (record.target.kind == TargetKind::Player && record.dealt != 0U && loss_rows != 1U) {
                    add_error(out, "damage_record.player_life_loss_count_mismatch", prefix + " player damage should link exactly one life-loss row");
                }
                if ((record.target.kind != TargetKind::Player || record.dealt == 0U) && loss_rows != 0U) {
                    add_error(out, "damage_record.unexpected_life_loss_row", prefix + " links a life-loss row for non-player or zero-dealt damage");
                }
                if (record.source_had_lifelink && record.dealt != 0U && is_valid_player_ref(game, record.source_controller)) {
                    if (gain_rows != 1U) {
                        add_error(out, "damage_record.lifelink_gain_count_mismatch", prefix + " lifelink damage should link exactly one life-gain row");
                    }
                } else if (gain_rows != 0U) {
                    add_error(out, "damage_record.unexpected_life_gain_row", prefix + " links a life-gain row without lifelink damage");
                }
            }
        }
    }

    u64 last_damage_prevention_sequence = 0;
    for (std::size_t i = 0; i < game.damage_prevention_records.size(); ++i) {
        const auto& record = game.damage_prevention_records[i];
        const std::string prefix = "damage_prevention_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "damage_prevention_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "damage_prevention_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_damage_prevention_sequence != 0U && record.sequence <= last_damage_prevention_sequence) {
            add_error(out, "damage_prevention_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_damage_prevention_sequence = record.sequence;
        if (i + 1U < damage_prevention_event_links.size() && damage_prevention_event_links[i + 1U] != 1U) {
            add_error(out, "damage_prevention_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(damage_prevention_event_links[i + 1U]));
        }
        if (record.kind == DamagePreventionRecordKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(DamagePreventionRecordKind::Count)) {
            add_error(out, "damage_prevention_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (record.shield_id == 0U) {
            add_error(out, "damage_prevention_record.zero_shield_id", prefix + " has shield_id=0");
        }
        if (record.amount == 0U) {
            add_error(out, "damage_prevention_record.zero_amount", prefix + " records a zero prevention amount");
        }
        switch (record.target.kind) {
            case TargetKind::Player:
                if (!is_valid_player_ref(game, record.target.player)) {
                    add_error(out, "damage_prevention_record.invalid_target_player", prefix + " target=" + player_ref(record.target.player));
                }
                if (record.target.object_zone_change_index != 0U) {
                    add_error(out, "damage_prevention_record.player_target_zone_change_index", prefix + " player target unexpectedly has object zone-change metadata");
                }
                break;
            case TargetKind::Object:
                if (!is_valid_object_ref(game, record.target.object)) {
                    add_error(out, "damage_prevention_record.invalid_target_object", prefix + " target=" + object_ref(record.target.object));
                }
                if (record.target.object_zone_change_index == 0U) {
                    add_error(out, "damage_prevention_record.missing_target_zone_change_index", prefix + " object target missing zone-change snapshot");
                }
                break;
            case TargetKind::None:
                add_error(out, "damage_prevention_record.missing_target", prefix + " has no target");
                break;
        }
        const bool damage_prevention_application = record.kind == DamagePreventionRecordKind::ShieldConsumed ||
                                                   record.kind == DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage;
        if (damage_prevention_application) {
            if (!is_valid_player_ref(game, record.affected_player)) {
                add_error(out, "damage_prevention_record.invalid_affected_player", prefix + " has affected_player=" + player_ref(record.affected_player));
            } else if (record.target.kind == TargetKind::Player) {
                if (record.affected_player != record.target.player) {
                    add_error(out, "damage_prevention_record.affected_player_target_mismatch", prefix + " affected_player does not match the damaged player");
                }
            } else if (record.target.kind == TargetKind::Object && is_valid_object_ref(game, record.target.object)) {
                const auto& target_object = object(game, record.target.object);
                const PlayerId expected_affected_player = target_object.controller.valid() ? target_object.controller : target_object.owner;
                if (is_valid_player_ref(game, expected_affected_player) && record.affected_player != expected_affected_player) {
                    add_error(out, "damage_prevention_record.affected_player_object_controller_mismatch", prefix + " affected_player does not match the damaged object's controller/owner fallback");
                }
            }
            if (record.candidate_count == 0U) {
                add_error(out, "damage_prevention_record.zero_candidate_count", prefix + " damage-application row should record at least one applicable shield candidate");
            }
            if (record.pass_index == 0U) {
                add_error(out, "damage_prevention_record.zero_pass_index", prefix + " damage-application row should record a one-based prevention pass index");
            }
            if (record.chosen_among_multiple != (record.candidate_count > 1U)) {
                add_error(out, "damage_prevention_record.choice_flag_mismatch", prefix + " chosen_among_multiple does not match candidate_count");
            }
        } else if (record.affected_player.valid() || record.candidate_count != 0U || record.pass_index != 0U || record.chosen_among_multiple) {
            add_error(out, "damage_prevention_record.stray_choice_metadata", prefix + " non-damage row should not carry affected-player/candidate/pass choice metadata");
        }
        switch (record.kind) {
            case DamagePreventionRecordKind::ShieldAdded:
                if (record.remaining_before != 0U || record.remaining_after != record.amount) {
                    add_error(out, "damage_prevention_record.add_delta_mismatch", prefix + " shield-add row should go 0 -> amount");
                }
                if (record.damage_record_index != 0U || record.zone_change_record_index != 0U) {
                    add_error(out, "damage_prevention_record.add_has_resolution_link", prefix + " shield-add row should not link damage or zone-change records");
                }
                break;
            case DamagePreventionRecordKind::ShieldConsumed:
                if (record.remaining_before <= record.remaining_after || record.remaining_before != record.remaining_after + record.amount) {
                    add_error(out, "damage_prevention_record.consume_delta_mismatch", prefix + " shield-consume row delta does not match before/after remaining amount");
                }
                if (record.damage_record_index == 0U || record.damage_record_index > game.damage_records.size()) {
                    add_error(out, "damage_prevention_record.invalid_damage_link", prefix + " links invalid damage_record_index=" + std::to_string(record.damage_record_index));
                } else {
                    const auto& damage_record = game.damage_records[record.damage_record_index - 1U];
                    if (!(record.target == damage_record.target)) {
                        add_error(out, "damage_prevention_record.damage_target_mismatch", prefix + " linked DamageRecord has a different target");
                    }
                    if (damage_record.unpreventable) {
                        add_error(out, "damage_prevention_record.consume_linked_unpreventable_damage", prefix + " consumed a shield for unpreventable damage");
                    }
                    if (record.sequence >= damage_record.sequence) {
                        add_error(out, "damage_prevention_record.damage_sequence_order", prefix + " shield consumption should occur before the final DamageRecord");
                    }
                }
                if (record.zone_change_record_index != 0U) {
                    add_error(out, "damage_prevention_record.consume_has_zone_link", prefix + " shield-consume row should not link a ZoneChangeRecord");
                }
                break;
            case DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage:
                if (record.remaining_before != record.remaining_after || record.remaining_before == 0U) {
                    add_error(out, "damage_prevention_record.unpreventable_delta_mismatch", prefix + " unpreventable shield-application row should leave shield remaining unchanged");
                }
                if (record.damage_record_index == 0U || record.damage_record_index > game.damage_records.size()) {
                    add_error(out, "damage_prevention_record.invalid_unpreventable_damage_link", prefix + " links invalid damage_record_index=" + std::to_string(record.damage_record_index));
                } else {
                    const auto& damage_record = game.damage_records[record.damage_record_index - 1U];
                    if (!damage_record.unpreventable) {
                        add_error(out, "damage_prevention_record.unpreventable_linked_preventable_damage", prefix + " shield no-effect row links preventable damage");
                    }
                    if (!(record.target == damage_record.target)) {
                        add_error(out, "damage_prevention_record.unpreventable_damage_target_mismatch", prefix + " linked DamageRecord has a different target");
                    }
                    if (record.sequence >= damage_record.sequence) {
                        add_error(out, "damage_prevention_record.unpreventable_damage_sequence_order", prefix + " shield no-effect row should occur before the final DamageRecord");
                    }
                }
                if (record.zone_change_record_index != 0U) {
                    add_error(out, "damage_prevention_record.unpreventable_has_zone_link", prefix + " shield no-effect row should not link a ZoneChangeRecord");
                }
                break;
            case DamagePreventionRecordKind::ShieldExpired:
                if (record.remaining_after != 0U || record.amount != record.remaining_before) {
                    add_error(out, "damage_prevention_record.expire_delta_mismatch", prefix + " shield-expire row should remove all remaining prevention");
                }
                if (record.zone_change_record_index == 0U || record.zone_change_record_index > game.zone_change_records.size()) {
                    add_error(out, "damage_prevention_record.invalid_zone_change_link", prefix + " links invalid zone_change_record_index=" + std::to_string(record.zone_change_record_index));
                } else {
                    const auto& zone_record = game.zone_change_records[record.zone_change_record_index - 1U];
                    if (record.target.kind != TargetKind::Object || zone_record.object != record.target.object) {
                        add_error(out, "damage_prevention_record.zone_change_object_mismatch", prefix + " linked ZoneChangeRecord belongs to a different object");
                    }
                    if (record.sequence <= zone_record.sequence) {
                        add_error(out, "damage_prevention_record.zone_change_sequence_order", prefix + " shield expiration should be recorded after the zone-change event");
                    }
                }
                if (record.damage_record_index != 0U) {
                    add_error(out, "damage_prevention_record.expire_has_damage_link", prefix + " shield-expire row should not link a DamageRecord");
                }
                break;
            case DamagePreventionRecordKind::Count:
                break;
        }
    }

    u64 last_life_change_sequence = 0;
    for (std::size_t i = 0; i < game.life_change_records.size(); ++i) {
        const auto& record = game.life_change_records[i];
        const std::string prefix = "life_change_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "life_change_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "life_change_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_life_change_sequence != 0U && record.sequence <= last_life_change_sequence) {
            add_error(out, "life_change_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_life_change_sequence = record.sequence;
        if (i + 1U < life_change_event_links.size() && life_change_event_links[i + 1U] != 1U) {
            add_error(out, "life_change_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(life_change_event_links[i + 1U]));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "life_change_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.kind == LifeChangeKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(LifeChangeKind::Count)) {
            add_error(out, "life_change_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (record.amount < 0) {
            add_error(out, "life_change_record.negative_amount", prefix + " has negative amount=" + std::to_string(record.amount));
        }
        if (record.kind == LifeChangeKind::Loss && record.life_after != record.life_before - record.amount) {
            add_error(out, "life_change_record.loss_delta_mismatch", prefix + " loss delta does not match before/after life totals");
        }
        if (record.kind == LifeChangeKind::Gain && record.life_after != record.life_before + record.amount) {
            add_error(out, "life_change_record.gain_delta_mismatch", prefix + " gain delta does not match before/after life totals");
        }
        if (!record.damage_result) {
            if (record.damage_record_index != 0U || record.damage_source.valid() || record.damage_source_zone_change_index != 0U || record.damage_target.valid() || record.lifelink_result) {
                add_error(out, "life_change_record.stray_damage_metadata", prefix + " carries damage metadata without damage_result=true");
            }
        } else {
            if (record.damage_record_index == 0U || record.damage_record_index > game.damage_records.size()) {
                add_error(out, "life_change_record.invalid_damage_link", prefix + " links invalid damage_record_index=" + std::to_string(record.damage_record_index));
            } else {
                const auto& damage_record = game.damage_records[record.damage_record_index - 1U];
                if (record.sequence >= damage_record.sequence) {
                    add_error(out, "life_change_record.damage_sequence_order", prefix + " should be emitted before its final DamageRecord");
                }
                if (!same_target_snapshot_for_validation(record.damage_target, damage_record.target)) {
                    add_error(out, "life_change_record.damage_target_mismatch", prefix + " damage target snapshot differs from linked DamageRecord");
                }
                if (record.damage_source != damage_record.source) {
                    add_error(out, "life_change_record.damage_source_mismatch", prefix + " damage source differs from linked DamageRecord");
                }
                if (damage_record.source.valid() && record.damage_source_zone_change_index != damage_record.source_zone_change_index) {
                    add_error(out, "life_change_record.damage_source_zone_mismatch", prefix + " source zone identity differs from linked DamageRecord");
                }
                if (record.amount != static_cast<std::int32_t>(damage_record.dealt)) {
                    add_error(out, "life_change_record.damage_amount_mismatch", prefix + " amount does not equal linked DamageRecord::dealt");
                }
                if (record.kind == LifeChangeKind::Loss) {
                    if (damage_record.target.kind != TargetKind::Player || record.player != damage_record.target.player) {
                        add_error(out, "life_change_record.damage_loss_player_mismatch", prefix + " loss row does not belong to the damaged player");
                    }
                    if (record.lifelink_result) {
                        add_error(out, "life_change_record.loss_marked_lifelink", prefix + " life-loss row should not be marked as lifelink");
                    }
                } else if (record.kind == LifeChangeKind::Gain) {
                    if (!damage_record.source_had_lifelink) {
                        add_error(out, "life_change_record.gain_without_lifelink", prefix + " gain row links damage whose source lacked lifelink");
                    }
                    if (!record.lifelink_result) {
                        add_error(out, "life_change_record.gain_missing_lifelink_flag", prefix + " damage life-gain row is missing lifelink_result=true");
                    }
                    if (is_valid_player_ref(game, damage_record.source_controller) && record.player != damage_record.source_controller) {
                        add_error(out, "life_change_record.lifelink_controller_mismatch", prefix + " gain row does not belong to the linked damage source controller");
                    }
                }
            }
        }
    }

    u64 last_paid_action_transaction_sequence = 0;
    for (std::size_t i = 0; i < game.paid_action_transaction_records.size(); ++i) {
        const auto& record = game.paid_action_transaction_records[i];
        const std::string prefix = "paid_action_transaction_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "paid_action_transaction_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "paid_action_transaction_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_paid_action_transaction_sequence != 0U && record.sequence <= last_paid_action_transaction_sequence) {
            add_error(out, "paid_action_transaction_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_paid_action_transaction_sequence = record.sequence;
        if (i + 1U < paid_action_transaction_event_links.size() && paid_action_transaction_event_links[i + 1U] != 1U) {
            add_error(out, "paid_action_transaction_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(paid_action_transaction_event_links[i + 1U]));
        }
        if (record.schema_version != kPaidActionTransactionRecordSchemaVersion) {
            add_error(out, "paid_action_transaction_record.schema_mismatch", prefix + " has unsupported schema_version=" + std::to_string(record.schema_version));
        }
        if (record.outcome == PaidActionTransactionOutcome::Count || static_cast<u8>(record.outcome) >= static_cast<u8>(PaidActionTransactionOutcome::Count)) {
            add_error(out, "paid_action_transaction_record.invalid_outcome", prefix + " has invalid outcome=" + std::string(to_string(record.outcome)));
        }
        if (record.action_kind == ActionKind::Count || static_cast<u8>(record.action_kind) >= static_cast<u8>(ActionKind::Count)) {
            add_error(out, "paid_action_transaction_record.invalid_action_kind", prefix + " has invalid action kind");
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "paid_action_transaction_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.source_object.valid() && !is_valid_object_ref(game, record.source_object)) {
            add_error(out, "paid_action_transaction_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (record.stack_object.valid() && !is_valid_object_ref(game, record.stack_object)) {
            add_error(out, "paid_action_transaction_record.invalid_stack_object", prefix + " stack_object=" + object_ref(record.stack_object));
        }
        if (record.transaction_hash == 0U) {
            add_error(out, "paid_action_transaction_record.zero_hash", prefix + " has transaction_hash=0");
        } else if (record.transaction_hash != paid_action_transaction_record_hash(record)) {
            add_error(out, "paid_action_transaction_record.hash_mismatch", prefix + " transaction_hash does not match the sealed payload");
        }

        switch (record.outcome) {
            case PaidActionTransactionOutcome::Committed:
                if (!record.committed || record.rolled_back) {
                    add_error(out, "paid_action_transaction_record.commit_flags", prefix + " committed transaction has inconsistent committed/rolled_back flags");
                }
                if (record.physical_state_hash_before == 0U || record.physical_state_hash_after == 0U) {
                    add_error(out, "paid_action_transaction_record.commit_missing_state_transition_hash",
                              prefix + " committed transaction must carry nonzero pre/post StateCore hashes");
                } else if (record.physical_state_hash_before == record.physical_state_hash_after) {
                    add_error(out, "paid_action_transaction_record.commit_no_state_transition",
                              prefix + " committed paid action did not prove a changed pre/post physical-state hash");
                }
                if (record.speculative_paid_action_declaration_snapshot_present) {
                    add_error(out, "paid_action_transaction_record.commit_unexpected_speculative_declaration_snapshot",
                              prefix + " committed transaction should not carry a rollback declaration snapshot");
                }
                if (!record.committed_paid_action_declaration_snapshot_present) {
                    add_error(out, "paid_action_transaction_record.commit_missing_declaration_snapshot",
                              prefix + " committed paid action lacks a replayable declaration snapshot");
                } else {
                    const auto& snapshot = record.committed_paid_action_declaration_snapshot;
                    if (paid_action_declaration_record_hash(snapshot) != record.paid_action_declaration_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_hash_mismatch",
                                  prefix + " committed declaration snapshot does not recompute the sealed declaration hash");
                    }
                    if (snapshot.sequence == 0U || snapshot.action_kind != record.action_kind ||
                        snapshot.player != record.player || snapshot.source_object != record.source_object ||
                        snapshot.stack_object != record.stack_object) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_identity_mismatch",
                                  prefix + " committed declaration snapshot identity differs from the transaction receipt");
                    }
                    if (snapshot.stack_placement_record_index != record.stack_placement_record_index ||
                        snapshot.declaration_hash != record.paid_action_declaration_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_link_mismatch",
                                  prefix + " committed declaration snapshot does not link the sealed placement/hash");
                    }
                    if (snapshot.stack_object_entered_sequence != record.stack_object_entered_sequence ||
                        snapshot.choices_locked_sequence != record.choices_locked_sequence ||
                        snapshot.first_payment_event_sequence != record.first_paid_action_event_sequence ||
                        snapshot.last_payment_event_sequence != record.last_paid_action_event_sequence) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_phase_mismatch",
                                  prefix + " committed declaration snapshot phase spans differ from the transaction receipt");
                    }
                    if (snapshot.first_sacrifice_cost_payment_record_index != record.first_sacrifice_cost_payment_record_index ||
                        snapshot.sacrifice_cost_payment_record_count != record.sacrifice_cost_payment_record_count ||
                        snapshot.sacrifice_cost_payment_hash != record.sacrifice_cost_payment_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_sacrifice_payment_mismatch",
                                  prefix + " committed declaration snapshot sacrifice-cost receipt range differs from the transaction receipt");
                    }
                    if (snapshot.first_discard_cost_payment_record_index != record.first_discard_cost_payment_record_index ||
                        snapshot.discard_cost_payment_record_count != record.discard_cost_payment_record_count ||
                        snapshot.discard_cost_payment_hash != record.discard_cost_payment_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_discard_payment_mismatch",
                                  prefix + " committed declaration snapshot discard-cost receipt range differs from the transaction receipt");
                    }
                    if (snapshot.first_tap_cost_payment_record_index != record.first_tap_cost_payment_record_index ||
                        snapshot.tap_cost_payment_record_count != record.tap_cost_payment_record_count ||
                        snapshot.tap_cost_payment_hash != record.tap_cost_payment_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_tap_payment_mismatch",
                                  prefix + " committed declaration snapshot tap-cost receipt range differs from the transaction receipt");
                    }
                    if (snapshot.first_life_cost_payment_record_index != record.first_life_cost_payment_record_index ||
                        snapshot.life_cost_payment_record_count != record.life_cost_payment_record_count ||
                        snapshot.life_cost_payment_hash != record.life_cost_payment_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_life_payment_mismatch",
                                  prefix + " committed declaration snapshot life-cost receipt range differs from the transaction receipt");
                    }
                    if (snapshot.first_return_cost_payment_record_index != record.first_return_cost_payment_record_index ||
                        snapshot.return_cost_payment_record_count != record.return_cost_payment_record_count ||
                        snapshot.return_cost_payment_hash != record.return_cost_payment_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_return_payment_mismatch",
                                  prefix + " committed declaration snapshot return-cost receipt range differs from the transaction receipt");
                    }
                    if (snapshot.first_loyalty_cost_payment_record_index != record.first_loyalty_cost_payment_record_index ||
                        snapshot.loyalty_cost_payment_record_count != record.loyalty_cost_payment_record_count ||
                        snapshot.loyalty_cost_payment_hash != record.loyalty_cost_payment_hash) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_loyalty_payment_mismatch",
                                  prefix + " committed declaration snapshot loyalty-cost receipt range differs from the transaction receipt");
                    }
                    if (!snapshot.total_cost_locked) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_cost_unsealed",
                                  prefix + " committed declaration snapshot did not preserve locked-cost evidence");
                    }
                    if (record.first_paid_action_event_sequence != 0U && !snapshot.payment_attempted) {
                        add_error(out, "paid_action_transaction_record.commit_declaration_snapshot_payment_unsealed",
                                  prefix + " committed declaration snapshot did not preserve payment-attempt evidence");
                    }
                }
        if (record.stack_placement_record_index == 0U || record.stack_placement_record_index > game.stack_placement_records.size()) {
                    add_error(out, "paid_action_transaction_record.invalid_stack_placement_link", prefix + " links invalid stack_placement_record_index=" + std::to_string(record.stack_placement_record_index));
                } else {
                    const auto& placement = game.stack_placement_records[record.stack_placement_record_index - 1U];
                    if (placement.sequence >= record.sequence) {
                        add_error(out, "paid_action_transaction_record.placement_not_before_transaction", prefix + " should be emitted after the stack-placement receipt");
                    }
                    if (placement.controller != record.player || placement.source_object != record.source_object || placement.stack_object != record.stack_object) {
                        add_error(out, "paid_action_transaction_record.placement_identity_mismatch", prefix + " does not match linked StackPlacementRecord identity");
                    }
                    if (placement.paid_action_declaration_record_index != record.paid_action_declaration_record_index ||
                        placement.paid_action_declaration_hash != record.paid_action_declaration_hash) {
                        add_error(out, "paid_action_transaction_record.declaration_link_mismatch", prefix + " declaration link does not match linked StackPlacementRecord");
                    }
                    if (placement.stack_object_entered_sequence != record.stack_object_entered_sequence ||
                        placement.choices_locked_sequence != record.choices_locked_sequence ||
                        placement.first_paid_action_event_sequence != record.first_paid_action_event_sequence ||
                        placement.last_paid_action_event_sequence != record.last_paid_action_event_sequence) {
                        add_error(out, "paid_action_transaction_record.phase_span_mismatch", prefix + " phase sequences do not match linked StackPlacementRecord");
                    }
                    if (placement.first_mana_payment_plan_record_index != record.first_mana_payment_plan_record_index ||
                        placement.mana_payment_plan_record_count != record.mana_payment_plan_record_count ||
                        placement.first_mana_change_record_index != record.first_mana_change_record_index ||
                        placement.mana_change_record_count != record.mana_change_record_count ||
                        placement.first_paid_action_counter_change_record_index != record.first_paid_action_counter_change_record_index ||
                        placement.paid_action_counter_change_record_count != record.paid_action_counter_change_record_count ||
                        placement.first_paid_action_zone_change_record_index != record.first_paid_action_zone_change_record_index ||
                        placement.paid_action_zone_change_record_count != record.paid_action_zone_change_record_count ||
                        placement.first_sacrifice_cost_payment_record_index != record.first_sacrifice_cost_payment_record_index ||
                        placement.sacrifice_cost_payment_record_count != record.sacrifice_cost_payment_record_count ||
                        placement.sacrifice_cost_payment_hash != record.sacrifice_cost_payment_hash ||
                        placement.first_discard_cost_payment_record_index != record.first_discard_cost_payment_record_index ||
                        placement.discard_cost_payment_record_count != record.discard_cost_payment_record_count ||
                        placement.discard_cost_payment_hash != record.discard_cost_payment_hash ||
                        placement.first_tap_cost_payment_record_index != record.first_tap_cost_payment_record_index ||
                        placement.tap_cost_payment_record_count != record.tap_cost_payment_record_count ||
                        placement.tap_cost_payment_hash != record.tap_cost_payment_hash ||
                        placement.first_life_cost_payment_record_index != record.first_life_cost_payment_record_index ||
                        placement.life_cost_payment_record_count != record.life_cost_payment_record_count ||
                        placement.life_cost_payment_hash != record.life_cost_payment_hash ||
                        placement.first_return_cost_payment_record_index != record.first_return_cost_payment_record_index ||
                        placement.return_cost_payment_record_count != record.return_cost_payment_record_count ||
                        placement.return_cost_payment_hash != record.return_cost_payment_hash ||
                        placement.first_loyalty_cost_payment_record_index != record.first_loyalty_cost_payment_record_index ||
                        placement.loyalty_cost_payment_record_count != record.loyalty_cost_payment_record_count ||
                        placement.loyalty_cost_payment_hash != record.loyalty_cost_payment_hash) {
                        add_error(out, "paid_action_transaction_record.phase_range_mismatch", prefix + " phase record ranges do not match linked StackPlacementRecord");
                    }
                    if (record.paid_action_declaration_record_index == 0U) {
                        add_error(out, "paid_action_transaction_record.missing_declaration", prefix + " committed paid action lacks a declaration/cost-lock link");
                    } else if (record.paid_action_declaration_record_index <= game.paid_action_declaration_records.size()) {
                        const auto& declaration = game.paid_action_declaration_records[record.paid_action_declaration_record_index - 1U];
                        if (declaration.action_kind != record.action_kind || declaration.player != record.player ||
                            declaration.source_object != record.source_object || declaration.stack_object != record.stack_object) {
                            add_error(out, "paid_action_transaction_record.declaration_identity_mismatch", prefix + " linked declaration identity differs from the transaction receipt");
                        }
                        if (declaration.declaration_hash != record.paid_action_declaration_hash) {
                            add_error(out, "paid_action_transaction_record.declaration_hash_mismatch", prefix + " linked declaration hash differs from the transaction receipt");
                        }
                        if (declaration.first_sacrifice_cost_payment_record_index != record.first_sacrifice_cost_payment_record_index ||
                            declaration.sacrifice_cost_payment_record_count != record.sacrifice_cost_payment_record_count ||
                            declaration.sacrifice_cost_payment_hash != record.sacrifice_cost_payment_hash) {
                            add_error(out, "paid_action_transaction_record.declaration_sacrifice_payment_mismatch", prefix + " linked declaration sacrifice-cost receipt range differs from the transaction receipt");
                        }
                        if (declaration.first_discard_cost_payment_record_index != record.first_discard_cost_payment_record_index ||
                            declaration.discard_cost_payment_record_count != record.discard_cost_payment_record_count ||
                            declaration.discard_cost_payment_hash != record.discard_cost_payment_hash) {
                            add_error(out, "paid_action_transaction_record.declaration_discard_payment_mismatch", prefix + " linked declaration discard-cost receipt range differs from the transaction receipt");
                        }
                        if (declaration.first_tap_cost_payment_record_index != record.first_tap_cost_payment_record_index ||
                            declaration.tap_cost_payment_record_count != record.tap_cost_payment_record_count ||
                            declaration.tap_cost_payment_hash != record.tap_cost_payment_hash) {
                            add_error(out, "paid_action_transaction_record.declaration_tap_payment_mismatch", prefix + " linked declaration tap-cost receipt range differs from the transaction receipt");
                        }
                        if (declaration.first_life_cost_payment_record_index != record.first_life_cost_payment_record_index ||
                            declaration.life_cost_payment_record_count != record.life_cost_payment_record_count ||
                            declaration.life_cost_payment_hash != record.life_cost_payment_hash) {
                            add_error(out, "paid_action_transaction_record.declaration_life_payment_mismatch", prefix + " linked declaration life-cost receipt range differs from the transaction receipt");
                        }
                        if (declaration.first_return_cost_payment_record_index != record.first_return_cost_payment_record_index ||
                            declaration.return_cost_payment_record_count != record.return_cost_payment_record_count ||
                            declaration.return_cost_payment_hash != record.return_cost_payment_hash) {
                            add_error(out, "paid_action_transaction_record.declaration_return_payment_mismatch", prefix + " linked declaration return-cost receipt range differs from the transaction receipt");
                        }
                        if (declaration.first_loyalty_cost_payment_record_index != record.first_loyalty_cost_payment_record_index ||
                            declaration.loyalty_cost_payment_record_count != record.loyalty_cost_payment_record_count ||
                            declaration.loyalty_cost_payment_hash != record.loyalty_cost_payment_hash) {
                            add_error(out, "paid_action_transaction_record.declaration_loyalty_payment_mismatch", prefix + " linked declaration loyalty-cost receipt range differs from the transaction receipt");
                        }
                        if (record.committed_paid_action_declaration_snapshot_present) {
                            const auto& snapshot = record.committed_paid_action_declaration_snapshot;
                            if (snapshot.sequence != declaration.sequence ||
                                snapshot.declaration_hash != declaration.declaration_hash ||
                                paid_action_declaration_record_hash(snapshot) != declaration.declaration_hash) {
                                add_error(out, "paid_action_transaction_record.declaration_snapshot_linked_payload_mismatch",
                                          prefix + " committed declaration snapshot does not match the linked declaration payload");
                            }
                        }
                    }
                }
                if (record.sacrifice_cost_payment_record_count == 0U) {
                    if (record.first_sacrifice_cost_payment_record_index != 0U || record.sacrifice_cost_payment_hash != 0U) {
                        add_error(out, "paid_action_transaction_record.unexpected_sacrifice_payment_receipt", prefix + " carries sacrifice-cost payment receipt metadata without a receipt count");
                    }
                } else {
                    if (record.first_sacrifice_cost_payment_record_index == 0U ||
                        static_cast<u64>(record.first_sacrifice_cost_payment_record_index) + static_cast<u64>(record.sacrifice_cost_payment_record_count) - 1U > game.sacrifice_cost_payment_records.size()) {
                        add_error(out, "paid_action_transaction_record.invalid_sacrifice_payment_range", prefix + " links a sacrifice-cost payment receipt range outside the journal");
                    } else {
                        for (u32 offset = 0; offset < record.sacrifice_cost_payment_record_count; ++offset) {
                            const auto& payment = game.sacrifice_cost_payment_records[record.first_sacrifice_cost_payment_record_index + offset - 1U];
                            if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                                add_error(out, "paid_action_transaction_record.sacrifice_payment_sequence_outside_span", prefix + " linked sacrifice-cost receipt is outside the paid-action transaction window");
                            }
                            if (payment.payer != record.player) {
                                add_error(out, "paid_action_transaction_record.sacrifice_payment_payer_mismatch", prefix + " linked sacrifice-cost payment has a different payer");
                            }
                            if (payment.source_object.valid() && payment.source_object != record.source_object) {
                                add_error(out, "paid_action_transaction_record.sacrifice_payment_source_mismatch", prefix + " linked sacrifice-cost payment has a different source object");
                            }
                            if (record.sacrifice_cost_payment_record_count == 1U && payment.payment_hash != record.sacrifice_cost_payment_hash) {
                                add_error(out, "paid_action_transaction_record.sacrifice_payment_hash_mismatch", prefix + " sacrifice-cost payment hash differs from the linked receipt");
                            }
                        }
                    }
                    if (record.sacrifice_cost_payment_record_count == 1U && record.sacrifice_cost_payment_hash == 0U) {
                        add_error(out, "paid_action_transaction_record.missing_sacrifice_payment_hash", prefix + " links one sacrifice-cost payment receipt but stores no receipt hash");
                    }
                }
                if (record.discard_cost_payment_record_count == 0U) {
                    if (record.first_discard_cost_payment_record_index != 0U || record.discard_cost_payment_hash != 0U) {
                        add_error(out, "paid_action_transaction_record.unexpected_discard_payment_receipt", prefix + " carries discard-cost payment receipt metadata without a receipt count");
                    }
                } else {
                    if (record.first_discard_cost_payment_record_index == 0U ||
                        static_cast<u64>(record.first_discard_cost_payment_record_index) + static_cast<u64>(record.discard_cost_payment_record_count) - 1U > game.discard_cost_payment_records.size()) {
                        add_error(out, "paid_action_transaction_record.invalid_discard_payment_range", prefix + " links a discard-cost payment receipt range outside the journal");
                    } else {
                        for (u32 offset = 0; offset < record.discard_cost_payment_record_count; ++offset) {
                            const auto& payment = game.discard_cost_payment_records[record.first_discard_cost_payment_record_index + offset - 1U];
                            if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                                add_error(out, "paid_action_transaction_record.discard_payment_sequence_outside_span", prefix + " linked discard-cost receipt is outside the paid-action transaction window");
                            }
                            if (payment.payer != record.player) {
                                add_error(out, "paid_action_transaction_record.discard_payment_payer_mismatch", prefix + " linked discard-cost payment has a different payer");
                            }
                            if (payment.source_object.valid() && payment.source_object != record.source_object) {
                                add_error(out, "paid_action_transaction_record.discard_payment_source_mismatch", prefix + " linked discard-cost payment has a different source object");
                            }
                            if (record.discard_cost_payment_record_count == 1U && payment.payment_hash != record.discard_cost_payment_hash) {
                                add_error(out, "paid_action_transaction_record.discard_payment_hash_mismatch", prefix + " discard-cost payment hash differs from the linked receipt");
                            }
                        }
                    }
                    if (record.discard_cost_payment_record_count == 1U && record.discard_cost_payment_hash == 0U) {
                        add_error(out, "paid_action_transaction_record.missing_discard_payment_hash", prefix + " links one discard-cost payment receipt but stores no receipt hash");
                    }
                }
                if (record.tap_cost_payment_record_count == 0U) {
                    if (record.first_tap_cost_payment_record_index != 0U || record.tap_cost_payment_hash != 0U) {
                        add_error(out, "paid_action_transaction_record.unexpected_tap_payment_receipt", prefix + " carries tap-cost payment receipt metadata without a receipt count");
                    }
                } else {
                    if (record.first_tap_cost_payment_record_index == 0U ||
                        static_cast<u64>(record.first_tap_cost_payment_record_index) + static_cast<u64>(record.tap_cost_payment_record_count) - 1U > game.tap_cost_payment_records.size()) {
                        add_error(out, "paid_action_transaction_record.invalid_tap_payment_range", prefix + " links a tap-cost payment receipt range outside the journal");
                    } else {
                        for (u32 offset = 0; offset < record.tap_cost_payment_record_count; ++offset) {
                            const auto& payment = game.tap_cost_payment_records[record.first_tap_cost_payment_record_index + offset - 1U];
                            if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                                add_error(out, "paid_action_transaction_record.tap_payment_sequence_outside_span", prefix + " linked tap-cost receipt is outside the paid-action transaction window");
                            }
                            if (payment.payer != record.player) {
                                add_error(out, "paid_action_transaction_record.tap_payment_payer_mismatch", prefix + " linked tap-cost payment has a different payer");
                            }
                            if (payment.source_object != record.source_object) {
                                add_error(out, "paid_action_transaction_record.tap_payment_source_mismatch", prefix + " linked tap-cost payment has a different source object");
                            }
                            if (record.tap_cost_payment_record_count == 1U && payment.payment_hash != record.tap_cost_payment_hash) {
                                add_error(out, "paid_action_transaction_record.tap_payment_hash_mismatch", prefix + " tap-cost payment hash differs from the linked receipt");
                            }
                        }
                    }
                    if (record.tap_cost_payment_record_count == 1U && record.tap_cost_payment_hash == 0U) {
                        add_error(out, "paid_action_transaction_record.missing_tap_payment_hash", prefix + " links one tap-cost payment receipt but stores no receipt hash");
                    }
                }
                if (record.life_cost_payment_record_count == 0U) {
                    if (record.first_life_cost_payment_record_index != 0U || record.life_cost_payment_hash != 0U) {
                        add_error(out, "paid_action_transaction_record.unexpected_life_payment_receipt", prefix + " carries life-cost payment receipt metadata without a receipt count");
                    }
                } else {
                    if (record.first_life_cost_payment_record_index == 0U ||
                        static_cast<u64>(record.first_life_cost_payment_record_index) + static_cast<u64>(record.life_cost_payment_record_count) - 1U > game.life_cost_payment_records.size()) {
                        add_error(out, "paid_action_transaction_record.invalid_life_payment_range", prefix + " links a life-cost payment receipt range outside the journal");
                    } else {
                        for (u32 offset = 0; offset < record.life_cost_payment_record_count; ++offset) {
                            const auto& payment = game.life_cost_payment_records[record.first_life_cost_payment_record_index + offset - 1U];
                            if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                                add_error(out, "paid_action_transaction_record.life_payment_sequence_outside_span", prefix + " linked life-cost receipt is outside the paid-action transaction window");
                            }
                            if (payment.payer != record.player) {
                                add_error(out, "paid_action_transaction_record.life_payment_payer_mismatch", prefix + " linked life-cost payment has a different payer");
                            }
                            if (payment.source_object.valid() && payment.source_object != record.source_object) {
                                add_error(out, "paid_action_transaction_record.life_payment_source_mismatch", prefix + " linked life-cost payment has a different source object");
                            }
                            if (record.life_cost_payment_record_count == 1U && payment.payment_hash != record.life_cost_payment_hash) {
                                add_error(out, "paid_action_transaction_record.life_payment_hash_mismatch", prefix + " life-cost payment hash differs from the linked receipt");
                            }
                        }
                    }
                    if (record.life_cost_payment_record_count == 1U && record.life_cost_payment_hash == 0U) {
                        add_error(out, "paid_action_transaction_record.missing_life_payment_hash", prefix + " links one life-cost payment receipt but stores no receipt hash");
                    }
                }
                if (record.return_cost_payment_record_count == 0U) {
                    if (record.first_return_cost_payment_record_index != 0U || record.return_cost_payment_hash != 0U) {
                        add_error(out, "paid_action_transaction_record.unexpected_return_payment_receipt", prefix + " carries return-cost payment receipt metadata without a receipt count");
                    }
                } else {
                    if (record.first_return_cost_payment_record_index == 0U ||
                        static_cast<u64>(record.first_return_cost_payment_record_index) + static_cast<u64>(record.return_cost_payment_record_count) - 1U > game.return_cost_payment_records.size()) {
                        add_error(out, "paid_action_transaction_record.invalid_return_payment_range", prefix + " links a return-cost payment receipt range outside the journal");
                    } else {
                        for (u32 offset = 0; offset < record.return_cost_payment_record_count; ++offset) {
                            const auto& payment = game.return_cost_payment_records[record.first_return_cost_payment_record_index + offset - 1U];
                            if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                                add_error(out, "paid_action_transaction_record.return_payment_sequence_outside_span", prefix + " linked return-cost receipt is outside the paid-action transaction window");
                            }
                            if (payment.payer != record.player) {
                                add_error(out, "paid_action_transaction_record.return_payment_payer_mismatch", prefix + " linked return-cost payment has a different payer");
                            }
                            if (payment.source_object.valid() && payment.source_object != record.source_object) {
                                add_error(out, "paid_action_transaction_record.return_payment_source_mismatch", prefix + " linked return-cost payment has a different source object");
                            }
                            if (record.return_cost_payment_record_count == 1U && payment.payment_hash != record.return_cost_payment_hash) {
                                add_error(out, "paid_action_transaction_record.return_payment_hash_mismatch", prefix + " return-cost payment hash differs from the linked receipt");
                            }
                        }
                    }
                    if (record.return_cost_payment_record_count == 1U && record.return_cost_payment_hash == 0U) {
                        add_error(out, "paid_action_transaction_record.missing_return_payment_hash", prefix + " links one return-cost payment receipt but stores no receipt hash");
                    }
                }
                if (record.loyalty_cost_payment_record_count == 0U) {
                    if (record.first_loyalty_cost_payment_record_index != 0U || record.loyalty_cost_payment_hash != 0U) {
                        add_error(out, "paid_action_transaction_record.unexpected_loyalty_payment_receipt", prefix + " carries loyalty-cost payment receipt metadata without a receipt count");
                    }
                } else {
                    if (record.first_loyalty_cost_payment_record_index == 0U ||
                        static_cast<u64>(record.first_loyalty_cost_payment_record_index) + static_cast<u64>(record.loyalty_cost_payment_record_count) - 1U > game.loyalty_cost_payment_records.size()) {
                        add_error(out, "paid_action_transaction_record.invalid_loyalty_payment_range", prefix + " links a loyalty-cost payment receipt range outside the journal");
                    } else {
                        for (u32 offset = 0; offset < record.loyalty_cost_payment_record_count; ++offset) {
                            const auto& payment = game.loyalty_cost_payment_records[record.first_loyalty_cost_payment_record_index + offset - 1U];
                            if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                                add_error(out, "paid_action_transaction_record.loyalty_payment_sequence_outside_span", prefix + " linked loyalty-cost receipt is outside the paid-action transaction window");
                            }
                            if (payment.payer != record.player) {
                                add_error(out, "paid_action_transaction_record.loyalty_payment_payer_mismatch", prefix + " linked loyalty-cost payment has a different payer");
                            }
                            if (payment.source_object != record.source_object) {
                                add_error(out, "paid_action_transaction_record.loyalty_payment_source_mismatch", prefix + " linked loyalty-cost payment has a different source object");
                            }
                            if (record.loyalty_cost_payment_record_count == 1U && payment.payment_hash != record.loyalty_cost_payment_hash) {
                                add_error(out, "paid_action_transaction_record.loyalty_payment_hash_mismatch", prefix + " loyalty-cost payment hash differs from the linked receipt");
                            }
                        }
                    }
                    if (record.loyalty_cost_payment_record_count == 1U && record.loyalty_cost_payment_hash == 0U) {
                        add_error(out, "paid_action_transaction_record.missing_loyalty_payment_hash", prefix + " links one loyalty-cost payment receipt but stores no receipt hash");
                    }
                }
                if (!record.choices_before_payment || !record.payments_before_placement || !record.placement_before_transaction) {
                    add_error(out, "paid_action_transaction_record.order_flags", prefix + " committed transaction did not preserve declaration/payment/placement ordering flags");
                }
                break;
            case PaidActionTransactionOutcome::RolledBack:
                if (record.committed || !record.rolled_back) {
                    add_error(out, "paid_action_transaction_record.rollback_flags", prefix + " rollback transaction has inconsistent committed/rolled_back flags");
                }
                if (record.stack_placement_record_index != 0U || record.paid_action_declaration_record_index != 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_committed_links", prefix + " rollback transaction should not link committed placement/declaration records");
                }
                if (record.committed_paid_action_declaration_snapshot_present) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_committed_declaration_snapshot",
                              prefix + " rollback transaction should not carry a committed declaration snapshot");
                }
                if (record.first_sacrifice_cost_payment_record_index != 0U ||
                    record.sacrifice_cost_payment_record_count != 0U ||
                    record.sacrifice_cost_payment_hash != 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_sacrifice_payment_receipt",
                              prefix + " rollback transaction should not carry committed sacrifice-cost payment receipt links");
                }
                if (record.first_discard_cost_payment_record_index != 0U ||
                    record.discard_cost_payment_record_count != 0U ||
                    record.discard_cost_payment_hash != 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_discard_payment_receipt",
                              prefix + " rollback transaction should not carry committed discard-cost payment receipt links");
                }
                if (record.first_tap_cost_payment_record_index != 0U ||
                    record.tap_cost_payment_record_count != 0U ||
                    record.tap_cost_payment_hash != 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_tap_payment_receipt",
                              prefix + " rollback transaction should not carry committed tap-cost payment receipt links");
                }
                if (record.first_life_cost_payment_record_index != 0U ||
                    record.life_cost_payment_record_count != 0U ||
                    record.life_cost_payment_hash != 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_life_payment_receipt",
                              prefix + " rollback transaction should not carry committed life-cost payment receipt links");
                }
                if (record.first_return_cost_payment_record_index != 0U ||
                    record.return_cost_payment_record_count != 0U ||
                    record.return_cost_payment_hash != 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_return_payment_receipt",
                              prefix + " rollback transaction should not carry committed return-cost payment receipt links");
                }
                if (record.first_loyalty_cost_payment_record_index != 0U ||
                    record.loyalty_cost_payment_record_count != 0U ||
                    record.loyalty_cost_payment_hash != 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_loyalty_payment_receipt",
                              prefix + " rollback transaction should not carry committed loyalty-cost payment receipt links");
                }
                if (!record.physical_state_preserved_on_rollback || record.physical_state_hash_before != record.physical_state_hash_after) {
                    add_error(out, "paid_action_transaction_record.rollback_state_not_preserved", prefix + " rollback did not preserve the source physical-state hash");
                }
                if (record.speculative_next_event_sequence_after < record.next_event_sequence_before) {
                    add_error(out, "paid_action_transaction_record.rollback_sequence_reversed", prefix + " speculative event sequence moved backwards");
                }
                if (record.speculative_event_count == 0U) {
                    add_error(out, "paid_action_transaction_record.rollback_no_speculative_events", prefix + " rollback transaction did not retain speculative event-count evidence");
                }
                if (record.action_kind == ActionKind::CastSpellFromHandPaid ||
                    record.action_kind == ActionKind::ActivateActivatedAbility ||
                    record.action_kind == ActionKind::ActivateLoyaltyAbility) {
                    if (record.speculative_paid_action_declaration_record_count == 0U) {
                        add_error(out, "paid_action_transaction_record.rollback_missing_speculative_declaration",
                                  prefix + " rollback paid action lacks speculative declaration/cost-lock evidence");
                    }
                    if (record.speculative_paid_action_declaration_sequence == 0U || record.speculative_paid_action_declaration_hash == 0U) {
                        add_error(out, "paid_action_transaction_record.rollback_missing_speculative_declaration_hash",
                                  prefix + " rollback paid action lacks the speculative declaration identity hash");
                    }
                    if (!record.speculative_paid_action_declaration_snapshot_present) {
                        add_error(out, "paid_action_transaction_record.rollback_missing_speculative_declaration_snapshot",
                                  prefix + " rollback paid action lacks the replayable speculative declaration snapshot");
                    } else {
                        const auto& snapshot = record.speculative_paid_action_declaration_snapshot;
                        const u64 snapshot_hash = paid_action_declaration_record_hash(snapshot);
                        if (snapshot_hash != record.speculative_paid_action_declaration_hash) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_hash_mismatch",
                                      prefix + " speculative declaration snapshot does not recompute the sealed identity hash");
                        }
                        if (snapshot.sequence != record.speculative_paid_action_declaration_sequence ||
                            snapshot.action_kind != record.action_kind ||
                            snapshot.player != record.player ||
                            snapshot.source_object != record.source_object) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_identity_mismatch",
                                      prefix + " speculative declaration snapshot does not match the rollback receipt identity");
                        }
                        if (record.action_kind == ActionKind::CastSpellFromHandPaid && snapshot.stack_object != record.stack_object) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_stack_object_mismatch",
                                      prefix + " speculative spell declaration snapshot stack object does not match the rollback receipt");
                        }
                        if ((record.action_kind == ActionKind::ActivateActivatedAbility ||
                             record.action_kind == ActionKind::ActivateLoyaltyAbility) &&
                            !snapshot.stack_object.valid()) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_missing_speculative_stack_object",
                                      prefix + " speculative ability declaration snapshot lacks the rolled-back stack object identity");
                        }
                        if (!snapshot.total_cost_locked) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_cost_unlocked",
                                      prefix + " speculative declaration snapshot did not lock the total cost");
                        }
                        if (snapshot.stack_placement_record_index != 0U || snapshot.declaration_hash != 0U) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_committed_links",
                                      prefix + " speculative declaration snapshot should not carry committed placement/hash links");
                        }
                        if (snapshot.stack_object_entered_sequence != record.stack_object_entered_sequence ||
                            snapshot.choices_locked_sequence != record.choices_locked_sequence ||
                            snapshot.first_payment_event_sequence != record.speculative_first_payment_event_sequence ||
                            snapshot.last_payment_event_sequence != record.speculative_last_payment_event_sequence) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_phase_mismatch",
                                      prefix + " speculative declaration snapshot phase spans differ from the rollback receipt");
                        }
                        if (snapshot.payment_attempted != (record.speculative_first_payment_event_sequence != 0U)) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_snapshot_payment_flag_mismatch",
                                      prefix + " speculative declaration snapshot payment flag does not match the rollback payment span");
                        }
                    }
                    if (record.speculative_paid_action_declaration_sequence != 0U) {
                        if (record.speculative_paid_action_declaration_sequence < record.next_event_sequence_before ||
                            record.speculative_paid_action_declaration_sequence >= record.speculative_next_event_sequence_after) {
                            add_error(out, "paid_action_transaction_record.rollback_declaration_sequence_outside_branch",
                                      prefix + " speculative declaration sequence is outside the rolled-back branch");
                        }
                        if (record.stack_object_entered_sequence != 0U && record.stack_object_entered_sequence >= record.speculative_paid_action_declaration_sequence) {
                            add_error(out, "paid_action_transaction_record.rollback_stack_entry_not_before_declaration",
                                      prefix + " speculative stack entry should precede the speculative declaration");
                        }
                        if (record.choices_locked_sequence != 0U && record.choices_locked_sequence > record.speculative_paid_action_declaration_sequence) {
                            add_error(out, "paid_action_transaction_record.rollback_choices_after_declaration",
                                      prefix + " speculative choices should not be locked after the declaration");
                        }
                    }
                    if ((record.speculative_first_payment_event_sequence == 0U) != (record.speculative_last_payment_event_sequence == 0U)) {
                        add_error(out, "paid_action_transaction_record.rollback_payment_span_incomplete",
                                  prefix + " carries only one side of the speculative payment span");
                    }
                    if (record.speculative_first_payment_event_sequence != 0U) {
                        if (record.speculative_first_payment_event_sequence <= record.speculative_paid_action_declaration_sequence ||
                            record.speculative_last_payment_event_sequence < record.speculative_first_payment_event_sequence ||
                            record.speculative_last_payment_event_sequence >= record.speculative_next_event_sequence_after) {
                            add_error(out, "paid_action_transaction_record.rollback_payment_span_invalid",
                                      prefix + " speculative payment span is not inside the rolled-back branch after declaration");
                        }
                        if (record.first_paid_action_event_sequence != record.speculative_first_payment_event_sequence ||
                            record.last_paid_action_event_sequence != record.speculative_last_payment_event_sequence) {
                            add_error(out, "paid_action_transaction_record.rollback_payment_span_alias_mismatch",
                                      prefix + " generic paid-action span aliases do not match speculative payment span");
                        }
                    }
                } else if (record.speculative_paid_action_declaration_sequence != 0U ||
                           record.speculative_paid_action_declaration_hash != 0U ||
                           record.speculative_paid_action_declaration_snapshot_present) {
                    add_error(out, "paid_action_transaction_record.rollback_unexpected_speculative_declaration",
                              prefix + " non-paid rollback should not carry speculative paid declaration evidence");
                }
                break;
            case PaidActionTransactionOutcome::Count:
                break;
        }
    }

    u64 last_mana_payment_plan_sequence = 0;
    for (std::size_t i = 0; i < game.mana_payment_plan_records.size(); ++i) {
        const auto& record = game.mana_payment_plan_records[i];
        const std::string prefix = "mana_payment_plan_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "mana_payment_plan_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "mana_payment_plan_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_mana_payment_plan_sequence != 0U && record.sequence <= last_mana_payment_plan_sequence) {
            add_error(out, "mana_payment_plan_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_mana_payment_plan_sequence = record.sequence;
        if (i + 1U < mana_payment_plan_event_links.size() && mana_payment_plan_event_links[i + 1U] != 1U) {
            add_error(out, "mana_payment_plan_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(mana_payment_plan_event_links[i + 1U]));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "mana_payment_plan_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.cost.free()) {
            add_error(out, "mana_payment_plan_record.free_cost", prefix + " records an automatic plan for a free mana cost");
        }
        if (record.plan_hash == 0U) {
            add_error(out, "mana_payment_plan_record.zero_hash", prefix + " has plan_hash=0");
        }
        if (record.plan_hash != 0U && record.plan_hash != mana_payment_plan_record_identity_hash(record)) {
            add_error(out, "mana_payment_plan_record.identity_hash_mismatch", prefix + " plan_hash does not match the locked-source and step identity payload");
        }
        const ManaChangeRecord* linked_paid_record = nullptr;
        if (record.paid_mana_change_record_index == 0U || record.paid_mana_change_record_index > game.mana_change_records.size()) {
            add_error(out, "mana_payment_plan_record.invalid_paid_link", prefix + " links invalid paid_mana_change_record_index=" + std::to_string(record.paid_mana_change_record_index));
        } else {
            const auto& paid_record = game.mana_change_records[record.paid_mana_change_record_index - 1U];
            linked_paid_record = &paid_record;
            if (!paid_record.auto_payment || paid_record.kind != ManaChangeKind::Paid) {
                add_error(out, "mana_payment_plan_record.link_not_auto_payment", prefix + " does not link an automatic paid ManaChangeRecord");
            }
            if (paid_record.auto_payment_plan_record_index != i + 1U) {
                add_error(out, "mana_payment_plan_record.backlink_mismatch", prefix + " paid ManaChangeRecord does not point back to this plan record");
            }
            if (paid_record.player != record.player) {
                add_error(out, "mana_payment_plan_record.player_mismatch", prefix + " player does not match linked paid record");
            }
            if (!same_mana_cost_for_validation(paid_record.cost, record.cost)) {
                add_error(out, "mana_payment_plan_record.cost_mismatch", prefix + " cost does not match linked paid record");
            }
            if (paid_record.auto_payment_plan_hash != record.plan_hash) {
                add_error(out, "mana_payment_plan_record.hash_mismatch", prefix + " plan hash does not match linked paid record");
            }
            if (paid_record.auto_payment_mana_ability_count != record.mana_ability_steps.size()) {
                add_error(out, "mana_payment_plan_record.step_count_mismatch", prefix + " step count does not match linked paid record");
            }
            if (paid_record.auto_payment_locked_tap_source_count != record.locked_tap_sources.size()) {
                add_error(out, "mana_payment_plan_record.locked_count_mismatch", prefix + " locked tap-source count does not match linked paid record");
            }
            if (record.sequence >= paid_record.sequence) {
                add_error(out, "mana_payment_plan_record.not_before_payment", prefix + " should be recorded before the linked paid ManaChangeRecord");
            }
            if (!mana_pool_equals(record.pool_before_payment, paid_record.pool_before)) {
                add_error(out, "mana_payment_plan_record.pool_before_payment_mismatch", prefix + " pool_before_payment does not match the linked paid record pool_before");
            }
        }
        for (std::size_t j = 0; j < record.locked_tap_sources.size(); ++j) {
            const auto& locked = record.locked_tap_sources[j];
            const std::string locked_prefix = prefix + ":locked#" + std::to_string(j + 1U);
            if (!is_valid_object_ref(game, locked.source)) {
                add_error(out, "mana_payment_plan_record.invalid_locked_source", locked_prefix + " source=" + object_ref(locked.source));
            }
            if (locked.source_zone_change_index == 0U) {
                add_error(out, "mana_payment_plan_record.locked_source_missing_zone_index", locked_prefix + " has no source zone-change snapshot");
            }
        }
        ManaPool expected_pool_before_payment = record.pool_before_plan;
        u64 last_step_production_sequence = 0U;
        u64 last_step_tap_sequence = 0U;
        for (std::size_t j = 0; j < record.mana_ability_steps.size(); ++j) {
            const auto& step = record.mana_ability_steps[j];
            add_mana_pool_for_validation(expected_pool_before_payment, step.produces);
            const std::string step_prefix = prefix + ":step#" + std::to_string(j + 1U);
            if (!is_valid_object_ref(game, step.source)) {
                add_error(out, "mana_payment_plan_record.invalid_step_source", step_prefix + " source=" + object_ref(step.source));
            }
            if (step.source_zone_change_index == 0U) {
                add_error(out, "mana_payment_plan_record.step_source_missing_zone_index", step_prefix + " has no source zone-change snapshot");
            }
            if (step.mana_ability_index == 0U) {
                add_error(out, "mana_payment_plan_record.zero_mana_ability_index", step_prefix + " has mana_ability_index=0");
            }
            if (mana_pool_is_empty(step.produces)) {
                add_error(out, "mana_payment_plan_record.empty_step_produces", step_prefix + " records a mana ability step that produces no mana");
            }
            if (step.tap_cost) {
                for (const auto& locked : record.locked_tap_sources) {
                    if (locked.source == step.source && locked.source_zone_change_index == step.source_zone_change_index) {
                        add_error(out, "mana_payment_plan_record.locked_source_used_as_tap_step", step_prefix + " uses a tap source that the same payment plan locked out before auto-mana planning");
                        break;
                    }
                }
            }
            const EventRecord* tap_event_record = nullptr;
            if (step.tap_cost) {
                if (step.tap_event_sequence == 0U) {
                    add_error(out, "mana_payment_plan_record.step_missing_tap_event_witness", step_prefix + " tap-cost mana step has no tap_event_sequence witness");
                } else {
                    for (const auto& event_record : game.event_records) {
                        if (event_record.sequence == step.tap_event_sequence) {
                            tap_event_record = &event_record;
                            break;
                        }
                    }
                    if (tap_event_record == nullptr) {
                        add_error(out, "mana_payment_plan_record.invalid_tap_event_witness", step_prefix + " links missing tap_event_sequence=" + std::to_string(step.tap_event_sequence));
                    } else {
                        if (tap_event_record->kind != EventRecordKind::Log || tap_event_record->log_kind != "tap") {
                            add_error(out, "mana_payment_plan_record.tap_event_witness_not_tap", step_prefix + " tap_event_sequence does not point to a plain tap log row");
                        }
                        if (tap_event_record->object != step.source) {
                            add_error(out, "mana_payment_plan_record.tap_event_witness_source_mismatch", step_prefix + " tap_event_sequence does not identify the planned mana source");
                        }
                        if (tap_event_record->object_zone_change_index != step.source_zone_change_index) {
                            add_error(out, "mana_payment_plan_record.tap_event_witness_zone_index_mismatch", step_prefix + " tap_event_sequence does not identify the planned mana source zone-change snapshot");
                        }
                        if (tap_event_record->player != record.player) {
                            add_error(out, "mana_payment_plan_record.tap_event_witness_player_mismatch", step_prefix + " tap_event_sequence does not identify the payment player");
                        }
                        if (tap_event_record->sequence <= record.sequence) {
                            add_error(out, "mana_payment_plan_record.step_tap_before_plan", step_prefix + " links tap before the plan event");
                        }
                        if (linked_paid_record != nullptr && tap_event_record->sequence >= linked_paid_record->sequence) {
                            add_error(out, "mana_payment_plan_record.step_tap_after_payment", step_prefix + " links tap after the paid mana record");
                        }
                        if (last_step_tap_sequence != 0U && tap_event_record->sequence <= last_step_tap_sequence) {
                            add_error(out, "mana_payment_plan_record.step_tap_order", step_prefix + " tap sequence is not in planned step order");
                        }
                        last_step_tap_sequence = tap_event_record->sequence;
                    }
                }
            } else if (step.tap_event_sequence != 0U) {
                add_error(out, "mana_payment_plan_record.step_tap_event_without_tap_cost", step_prefix + " non-tap mana step carries a tap_event_sequence witness");
            }
            if (step.produced_mana_change_record_index == 0U || step.produced_mana_change_record_index > game.mana_change_records.size()) {
                add_error(out, "mana_payment_plan_record.step_missing_produced_link", step_prefix + " links invalid produced_mana_change_record_index=" + std::to_string(step.produced_mana_change_record_index));
            } else {
                const auto& production_record = game.mana_change_records[step.produced_mana_change_record_index - 1U];
                if (production_record.kind != ManaChangeKind::Produced) {
                    add_error(out, "mana_payment_plan_record.step_link_not_production", step_prefix + " does not link a Produced ManaChangeRecord");
                }
                if (production_record.player != record.player) {
                    add_error(out, "mana_payment_plan_record.step_production_player_mismatch", step_prefix + " produced mana for a different player");
                }
                if (production_record.source != step.source) {
                    add_error(out, "mana_payment_plan_record.step_production_source_mismatch", step_prefix + " produced mana from a different source");
                }
                if (production_record.source_zone_change_index != step.source_zone_change_index) {
                    add_error(out, "mana_payment_plan_record.step_production_zone_index_mismatch", step_prefix + " produced mana with a different source zone-change snapshot");
                }
                if (production_record.mana_ability_index != step.mana_ability_index) {
                    add_error(out, "mana_payment_plan_record.step_production_ability_mismatch", step_prefix + " produced mana with a different mana ability index");
                }
                if (!mana_pool_equals(production_record.added, step.produces)) {
                    add_error(out, "mana_payment_plan_record.step_production_pool_mismatch", step_prefix + " produced mana payload differs from the planned step");
                }
                if (production_record.sequence <= record.sequence) {
                    add_error(out, "mana_payment_plan_record.step_production_before_plan", step_prefix + " links production before the plan event");
                }
                if (step.tap_event_sequence != 0U && step.tap_event_sequence >= production_record.sequence) {
                    add_error(out, "mana_payment_plan_record.step_tap_after_production", step_prefix + " tap-event witness should precede the produced mana record");
                }
                if (linked_paid_record != nullptr && production_record.sequence >= linked_paid_record->sequence) {
                    add_error(out, "mana_payment_plan_record.step_production_after_payment", step_prefix + " links production after the paid mana record");
                }
                if (last_step_production_sequence != 0U && production_record.sequence <= last_step_production_sequence) {
                    add_error(out, "mana_payment_plan_record.step_production_order", step_prefix + " production sequence is not in planned step order");
                }
                if (production_record.auto_payment_producer_plan_record_index != i + 1U ||
                    production_record.auto_payment_producer_plan_step_index != j + 1U) {
                    add_error(out, "mana_payment_plan_record.step_production_backlink_mismatch", step_prefix + " produced ManaChangeRecord does not point back to this plan step");
                }
                last_step_production_sequence = production_record.sequence;
            }
            for (std::size_t k = j + 1U; k < record.mana_ability_steps.size(); ++k) {
                if (step.produced_mana_change_record_index != 0U &&
                    step.produced_mana_change_record_index == record.mana_ability_steps[k].produced_mana_change_record_index) {
                    add_error(out, "mana_payment_plan_record.duplicate_step_production_link", step_prefix + " shares a produced ManaChangeRecord with a later plan step");
                    break;
                }
                if (step.tap_event_sequence != 0U &&
                    step.tap_event_sequence == record.mana_ability_steps[k].tap_event_sequence) {
                    add_error(out, "mana_payment_plan_record.duplicate_step_tap_event_witness", step_prefix + " shares a tap event witness with a later plan step");
                    break;
                }
            }
        }
        if (!mana_pool_equals(expected_pool_before_payment, record.pool_before_payment)) {
            add_error(out, "mana_payment_plan_record.pool_span_mismatch", prefix + " pool_before_plan plus planned production does not equal pool_before_payment");
        }
    }

    u64 last_sacrifice_payment_sequence = 0;
    for (std::size_t i = 0; i < game.sacrifice_cost_payment_records.size(); ++i) {
        const auto& record = game.sacrifice_cost_payment_records[i];
        const std::string prefix = "sacrifice_cost_payment_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "sacrifice_cost_payment_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "sacrifice_cost_payment_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_sacrifice_payment_sequence != 0U && record.sequence <= last_sacrifice_payment_sequence) {
            add_error(out, "sacrifice_cost_payment_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_sacrifice_payment_sequence = record.sequence;
        if (!is_valid_player_ref(game, record.payer)) {
            add_error(out, "sacrifice_cost_payment_record.invalid_payer", prefix + " payer=" + player_ref(record.payer));
        }
        if (record.source_object.valid() && !is_valid_object_ref(game, record.source_object)) {
            add_error(out, "sacrifice_cost_payment_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (!record.cost.active()) {
            add_error(out, "sacrifice_cost_payment_record.inactive_cost", prefix + " records no active sacrifice cost");
        }
        if (record.selected_objects.size() != record.cost.count) {
            add_error(out, "sacrifice_cost_payment_record.selection_count_mismatch", prefix + " selected object count does not match the cost");
        }
        if (record.selected_zone_change_indices_before.size() != record.selected_objects.size()) {
            add_error(out, "sacrifice_cost_payment_record.zone_snapshot_count_mismatch", prefix + " zone snapshot count does not match selected object count");
        }
        if (record.payment_hash == 0U) {
            add_error(out, "sacrifice_cost_payment_record.zero_hash", prefix + " has payment_hash=0");
        } else if (record.payment_hash != sacrifice_cost_payment_record_hash(record)) {
            add_error(out, "sacrifice_cost_payment_record.hash_mismatch", prefix + " payment_hash does not match the sealed payment payload");
        }

        bool zone_range_ok = true;
        if (record.zone_change_record_count == 0U) {
            if (record.first_zone_change_record_index != 0U) {
                add_error(out, "sacrifice_cost_payment_record.invalid_zone_change_range", prefix + " has first zone-change index without a count");
            }
            zone_range_ok = false;
        } else if (record.first_zone_change_record_index == 0U ||
                   record.first_zone_change_record_index > game.zone_change_records.size() ||
                   record.zone_change_record_count > game.zone_change_records.size() - record.first_zone_change_record_index + 1U) {
            add_error(out, "sacrifice_cost_payment_record.invalid_zone_change_range", prefix + " links a zone-change range outside the journal");
            zone_range_ok = false;
        }
        if (zone_range_ok && record.zone_change_record_count < record.selected_objects.size()) {
            add_error(out, "sacrifice_cost_payment_record.zone_range_shorter_than_selection", prefix + " zone-change range is shorter than the selected sacrifice set");
        }
        if (zone_range_ok) {
            const auto comparable_count = std::min<std::size_t>(record.selected_objects.size(), record.zone_change_record_count);
            for (std::size_t offset = 0; offset < comparable_count; ++offset) {
                const auto selected_object = record.selected_objects[offset];
                const auto& zone_record = game.zone_change_records[record.first_zone_change_record_index + static_cast<u32>(offset) - 1U];
                if (!is_valid_object_ref(game, selected_object)) {
                    add_error(out, "sacrifice_cost_payment_record.invalid_selected_object", prefix + " selected " + object_ref(selected_object));
                }
                if (zone_record.object != selected_object) {
                    add_error(out, "sacrifice_cost_payment_record.zone_object_mismatch", prefix + " zone-change range does not match the ordered sacrifice selection");
                }
                if (offset < record.selected_zone_change_indices_before.size() &&
                    zone_record.from_zone_change_index != record.selected_zone_change_indices_before[offset]) {
                    add_error(out, "sacrifice_cost_payment_record.zone_snapshot_mismatch", prefix + " zone-change before snapshot does not match the selected object's pre-payment snapshot");
                }
                if (zone_record.from_zone != Zone::Battlefield || zone_record.requested_zone != Zone::Graveyard || zone_record.was_ability_object) {
                    add_error(out, "sacrifice_cost_payment_record.zone_shape_mismatch", prefix + " payment zone-change is not a physical battlefield-to-graveyard sacrifice request");
                }
                if (zone_record.sequence >= record.sequence) {
                    add_error(out, "sacrifice_cost_payment_record.zone_sequence_not_before_payment_event", prefix + " zone-change did not occur before the summary pay_sacrifice_cost event");
                }
            }
        }
        const auto payment_event_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
            return event_record.sequence == record.sequence;
        });
        if (payment_event_it == game.event_records.end()) {
            add_error(out, "sacrifice_cost_payment_record.event_witness_missing", prefix + " sequence does not name an EventRecord");
        } else if (payment_event_it->kind != EventRecordKind::Log || payment_event_it->log_kind != "pay_sacrifice_cost") {
            add_error(out, "sacrifice_cost_payment_record.event_witness_not_payment", prefix + " sequence does not name a pay_sacrifice_cost log row");
        }
    }

    u64 last_discard_payment_sequence = 0;
    for (std::size_t i = 0; i < game.discard_cost_payment_records.size(); ++i) {
        const auto& record = game.discard_cost_payment_records[i];
        const std::string prefix = "discard_cost_payment_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "discard_cost_payment_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "discard_cost_payment_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_discard_payment_sequence != 0U && record.sequence <= last_discard_payment_sequence) {
            add_error(out, "discard_cost_payment_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_discard_payment_sequence = record.sequence;
        if (!is_valid_player_ref(game, record.payer)) {
            add_error(out, "discard_cost_payment_record.invalid_payer", prefix + " payer=" + player_ref(record.payer));
        }
        if (record.source_object.valid() && !is_valid_object_ref(game, record.source_object)) {
            add_error(out, "discard_cost_payment_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (!record.cost.active()) {
            add_error(out, "discard_cost_payment_record.inactive_cost", prefix + " records no active discard cost");
        }
        if (record.selected_cards.size() != record.cost.count) {
            add_error(out, "discard_cost_payment_record.selection_count_mismatch", prefix + " selected card count does not match the cost");
        }
        if (record.selected_zone_change_indices_before.size() != record.selected_cards.size()) {
            add_error(out, "discard_cost_payment_record.zone_snapshot_count_mismatch", prefix + " zone snapshot count does not match selected card count");
        }
        if (record.payment_hash == 0U) {
            add_error(out, "discard_cost_payment_record.zero_hash", prefix + " has payment_hash=0");
        } else if (record.payment_hash != discard_cost_payment_record_hash(record)) {
            add_error(out, "discard_cost_payment_record.hash_mismatch", prefix + " payment_hash does not match the sealed payment payload");
        }

        bool discard_range_ok = true;
        if (record.discard_record_count == 0U) {
            if (record.first_discard_record_index != 0U) {
                add_error(out, "discard_cost_payment_record.invalid_discard_range", prefix + " has first discard index without a count");
            }
            discard_range_ok = false;
        } else if (record.first_discard_record_index == 0U ||
                   record.first_discard_record_index > game.discard_records.size() ||
                   record.discard_record_count > game.discard_records.size() - record.first_discard_record_index + 1U) {
            add_error(out, "discard_cost_payment_record.invalid_discard_range", prefix + " links a discard-record range outside the journal");
            discard_range_ok = false;
        }
        if (discard_range_ok && record.discard_record_count < record.selected_cards.size()) {
            add_error(out, "discard_cost_payment_record.discard_range_shorter_than_selection", prefix + " discard-record range is shorter than the selected discard set");
        }
        if (discard_range_ok) {
            const auto comparable_count = std::min<std::size_t>(record.selected_cards.size(), record.discard_record_count);
            for (std::size_t offset = 0; offset < comparable_count; ++offset) {
                const auto selected_card = record.selected_cards[offset];
                const auto& discard_record = game.discard_records[record.first_discard_record_index + static_cast<u32>(offset) - 1U];
                if (!is_valid_object_ref(game, selected_card)) {
                    add_error(out, "discard_cost_payment_record.invalid_selected_card", prefix + " selected " + object_ref(selected_card));
                }
                if (discard_record.card != selected_card) {
                    add_error(out, "discard_cost_payment_record.discard_card_mismatch", prefix + " discard-record range does not match the ordered discard selection");
                }
                if (discard_record.player != record.payer) {
                    add_error(out, "discard_cost_payment_record.discard_payer_mismatch", prefix + " discard-record range names a different player");
                }
                if (discard_record.kind != DiscardRecordKind::CostPayment || !discard_record.cost_payment) {
                    add_error(out, "discard_cost_payment_record.discard_not_cost_payment", prefix + " linked discard row is not marked as a cost payment");
                }
                if (discard_record.explicit_choice || discard_record.cleanup_hand_size) {
                    add_error(out, "discard_cost_payment_record.discard_flag_overlap", prefix + " linked cost-payment discard has explicit/cleanup flags");
                }
                if (discard_record.sequence >= record.sequence) {
                    add_error(out, "discard_cost_payment_record.discard_sequence_not_before_payment_event", prefix + " discard row did not occur before the summary pay_discard_cost event");
                }
            }
        }

        bool zone_range_ok = true;
        if (record.zone_change_record_count == 0U) {
            if (record.first_zone_change_record_index != 0U) {
                add_error(out, "discard_cost_payment_record.invalid_zone_change_range", prefix + " has first zone-change index without a count");
            }
            zone_range_ok = false;
        } else if (record.first_zone_change_record_index == 0U ||
                   record.first_zone_change_record_index > game.zone_change_records.size() ||
                   record.zone_change_record_count > game.zone_change_records.size() - record.first_zone_change_record_index + 1U) {
            add_error(out, "discard_cost_payment_record.invalid_zone_change_range", prefix + " links a zone-change range outside the journal");
            zone_range_ok = false;
        }
        if (zone_range_ok && record.zone_change_record_count < record.selected_cards.size()) {
            add_error(out, "discard_cost_payment_record.zone_range_shorter_than_selection", prefix + " zone-change range is shorter than the selected discard set");
        }
        if (zone_range_ok) {
            const auto comparable_count = std::min<std::size_t>(record.selected_cards.size(), record.zone_change_record_count);
            for (std::size_t offset = 0; offset < comparable_count; ++offset) {
                const auto selected_card = record.selected_cards[offset];
                const auto& zone_record = game.zone_change_records[record.first_zone_change_record_index + static_cast<u32>(offset) - 1U];
                if (!is_valid_object_ref(game, selected_card)) {
                    add_error(out, "discard_cost_payment_record.invalid_selected_card", prefix + " selected " + object_ref(selected_card));
                }
                if (zone_record.object != selected_card) {
                    add_error(out, "discard_cost_payment_record.zone_object_mismatch", prefix + " zone-change range does not match the ordered discard selection");
                }
                if (offset < record.selected_zone_change_indices_before.size() &&
                    zone_record.from_zone_change_index != record.selected_zone_change_indices_before[offset]) {
                    add_error(out, "discard_cost_payment_record.zone_snapshot_mismatch", prefix + " zone-change before snapshot does not match the selected card's pre-payment snapshot");
                }
                if (zone_record.from_zone != Zone::Hand || zone_record.requested_zone != Zone::Graveyard || zone_record.to_zone != Zone::Graveyard || zone_record.was_ability_object) {
                    add_error(out, "discard_cost_payment_record.zone_shape_mismatch", prefix + " payment zone-change is not a physical hand-to-graveyard discard request");
                }
                if (zone_record.sequence >= record.sequence) {
                    add_error(out, "discard_cost_payment_record.zone_sequence_not_before_payment_event", prefix + " zone-change did not occur before the summary pay_discard_cost event");
                }
            }
        }
        const auto payment_event_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
            return event_record.sequence == record.sequence;
        });
        if (payment_event_it == game.event_records.end()) {
            add_error(out, "discard_cost_payment_record.event_witness_missing", prefix + " sequence does not name an EventRecord");
        } else if (payment_event_it->kind != EventRecordKind::Log || payment_event_it->log_kind != "pay_discard_cost") {
            add_error(out, "discard_cost_payment_record.event_witness_not_payment", prefix + " sequence does not name a pay_discard_cost log row");
        }
    }

    u64 last_tap_payment_sequence = 0;
    for (std::size_t i = 0; i < game.tap_cost_payment_records.size(); ++i) {
        const auto& record = game.tap_cost_payment_records[i];
        const std::string prefix = "tap_cost_payment_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "tap_cost_payment_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "tap_cost_payment_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_tap_payment_sequence != 0U && record.sequence <= last_tap_payment_sequence) {
            add_error(out, "tap_cost_payment_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_tap_payment_sequence = record.sequence;
        if (!is_valid_player_ref(game, record.payer)) {
            add_error(out, "tap_cost_payment_record.invalid_payer", prefix + " payer=" + player_ref(record.payer));
        }
        if (!is_valid_object_ref(game, record.source_object)) {
            add_error(out, "tap_cost_payment_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (record.source_zone_change_index_before == 0U) {
            add_error(out, "tap_cost_payment_record.zero_source_zone_snapshot", prefix + " has source_zone_change_index_before=0");
        }
        if (record.tapped_before) {
            add_error(out, "tap_cost_payment_record.source_already_tapped", prefix + " records tapped_before=true for a tap cost");
        }
        if (!record.tapped_after) {
            add_error(out, "tap_cost_payment_record.source_not_tapped_after", prefix + " records tapped_after=false after paying a tap cost");
        }
        if (record.tap_event_sequence == 0U) {
            add_error(out, "tap_cost_payment_record.missing_tap_event", prefix + " has tap_event_sequence=0");
        }
        if (record.tap_event_sequence != record.sequence) {
            add_error(out, "tap_cost_payment_record.tap_event_sequence_mismatch", prefix + " tap_event_sequence does not match payment sequence");
        }
        if (record.payment_hash == 0U) {
            add_error(out, "tap_cost_payment_record.zero_hash", prefix + " has payment_hash=0");
        } else if (record.payment_hash != tap_cost_payment_record_hash(record)) {
            add_error(out, "tap_cost_payment_record.hash_mismatch", prefix + " payment_hash does not match the sealed payment payload");
        }
        const auto tap_event_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
            return event_record.sequence == record.tap_event_sequence;
        });
        if (tap_event_it == game.event_records.end()) {
            add_error(out, "tap_cost_payment_record.event_witness_missing", prefix + " tap_event_sequence does not name an EventRecord");
        } else {
            const auto& event_record = *tap_event_it;
            if (event_record.kind != EventRecordKind::Log || event_record.log_kind != "tap") {
                add_error(out, "tap_cost_payment_record.event_witness_not_tap", prefix + " tap_event_sequence does not name a tap log row");
            }
            if (event_record.player != record.payer) {
                add_error(out, "tap_cost_payment_record.event_witness_payer_mismatch", prefix + " tap event names a different payer");
            }
            if (event_record.object != record.source_object) {
                add_error(out, "tap_cost_payment_record.event_witness_source_mismatch", prefix + " tap event names a different source object");
            }
            if (event_record.object_zone_change_index != record.source_zone_change_index_before) {
                add_error(out, "tap_cost_payment_record.event_witness_zone_index_mismatch", prefix + " tap event names a different source zone-change snapshot");
            }
        }
    }

    u64 last_life_payment_sequence = 0;
    for (std::size_t i = 0; i < game.life_cost_payment_records.size(); ++i) {
        const auto& record = game.life_cost_payment_records[i];
        const std::string prefix = "life_cost_payment_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "life_cost_payment_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "life_cost_payment_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_life_payment_sequence != 0U && record.sequence <= last_life_payment_sequence) {
            add_error(out, "life_cost_payment_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_life_payment_sequence = record.sequence;
        if (!is_valid_player_ref(game, record.payer)) {
            add_error(out, "life_cost_payment_record.invalid_payer", prefix + " payer=" + player_ref(record.payer));
        }
        if (record.source_object.valid() && !is_valid_object_ref(game, record.source_object)) {
            add_error(out, "life_cost_payment_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (!record.cost.active()) {
            add_error(out, "life_cost_payment_record.inactive_cost", prefix + " records no active life cost");
        }
        if (record.payment_hash == 0U) {
            add_error(out, "life_cost_payment_record.zero_hash", prefix + " has payment_hash=0");
        } else if (record.payment_hash != life_cost_payment_record_hash(record)) {
            add_error(out, "life_cost_payment_record.hash_mismatch", prefix + " payment_hash does not match the sealed payment payload");
        }
        if (record.life_change_record_index == 0U || record.life_change_record_index > game.life_change_records.size()) {
            add_error(out, "life_cost_payment_record.invalid_life_change_link", prefix + " links a life-change record outside the journal");
        } else {
            const auto& life = game.life_change_records[record.life_change_record_index - 1U];
            if (life.player != record.payer) {
                add_error(out, "life_cost_payment_record.life_change_payer_mismatch", prefix + " linked life change names a different player");
            }
            if (life.kind != LifeChangeKind::Loss || life.amount != static_cast<std::int32_t>(record.cost.amount)) {
                add_error(out, "life_cost_payment_record.life_change_shape_mismatch", prefix + " linked life change is not the expected life loss");
            }
            if (life.life_before != record.life_before || life.life_after != record.life_after) {
                add_error(out, "life_cost_payment_record.life_change_total_mismatch", prefix + " linked life totals differ from the payment receipt");
            }
            if (life.damage_result || life.lifelink_result || life.damage_record_index != 0U) {
                add_error(out, "life_cost_payment_record.life_change_not_pure_cost", prefix + " linked life change carries damage/lifelink metadata instead of pure cost payment");
            }
            if (life.sequence >= record.sequence) {
                add_error(out, "life_cost_payment_record.life_change_sequence_not_before_payment_event", prefix + " life loss did not occur before the summary pay_life_cost event");
            }
        }
        const auto payment_event_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
            return event_record.sequence == record.sequence;
        });
        if (payment_event_it == game.event_records.end()) {
            add_error(out, "life_cost_payment_record.event_witness_missing", prefix + " sequence does not name an EventRecord");
        } else {
            const auto& event_record = *payment_event_it;
            if (event_record.kind != EventRecordKind::Log || event_record.log_kind != "pay_life_cost") {
                add_error(out, "life_cost_payment_record.event_witness_not_payment", prefix + " sequence does not name a pay_life_cost log row");
            }
            if (event_record.player != record.payer) {
                add_error(out, "life_cost_payment_record.event_witness_payer_mismatch", prefix + " pay_life_cost event names a different payer");
            }
        }
    }

    u64 last_return_payment_sequence = 0;
    for (std::size_t i = 0; i < game.return_cost_payment_records.size(); ++i) {
        const auto& record = game.return_cost_payment_records[i];
        const std::string prefix = "return_cost_payment_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "return_cost_payment_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "return_cost_payment_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_return_payment_sequence != 0U && record.sequence <= last_return_payment_sequence) {
            add_error(out, "return_cost_payment_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_return_payment_sequence = record.sequence;
        if (!is_valid_player_ref(game, record.payer)) {
            add_error(out, "return_cost_payment_record.invalid_payer", prefix + " payer=" + player_ref(record.payer));
        }
        if (record.source_object.valid() && !is_valid_object_ref(game, record.source_object)) {
            add_error(out, "return_cost_payment_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (!record.cost.active()) {
            add_error(out, "return_cost_payment_record.inactive_cost", prefix + " records no active return cost");
        }
        if (record.selected_objects.size() != record.cost.count) {
            add_error(out, "return_cost_payment_record.selection_count_mismatch", prefix + " selected object count differs from the locked return cost");
        }
        if (record.selected_zone_change_indices_before.size() != record.selected_objects.size()) {
            add_error(out, "return_cost_payment_record.zone_snapshot_count_mismatch", prefix + " selected zone snapshot count differs from selected object count");
        }
        if (record.payment_hash == 0U) {
            add_error(out, "return_cost_payment_record.zero_hash", prefix + " has payment_hash=0");
        } else if (record.payment_hash != return_cost_payment_record_hash(record)) {
            add_error(out, "return_cost_payment_record.hash_mismatch", prefix + " payment_hash does not match the sealed payment payload");
        }
        if (record.zone_change_record_count == 0U || record.first_zone_change_record_index == 0U ||
            record.first_zone_change_record_index > game.zone_change_records.size() ||
            record.zone_change_record_count > game.zone_change_records.size() - record.first_zone_change_record_index + 1U) {
            add_error(out, "return_cost_payment_record.invalid_zone_change_range", prefix + " links a return zone-change range outside the journal");
        } else {
            std::vector<ObjectId> witnessed_objects;
            for (u32 offset = 0; offset < record.zone_change_record_count; ++offset) {
                const auto& zone_record = game.zone_change_records[record.first_zone_change_record_index + offset - 1U];
                const auto found = std::find(record.selected_objects.begin(), record.selected_objects.end(), zone_record.object);
                if (found == record.selected_objects.end()) {
                    add_error(out, "return_cost_payment_record.zone_change_unselected_object", prefix + " return-cost zone-change witness moves an object outside the sealed selection");
                } else {
                    const auto selected_index = static_cast<std::size_t>(std::distance(record.selected_objects.begin(), found));
                    if (selected_index < record.selected_zone_change_indices_before.size() &&
                        zone_record.from_zone_change_index != record.selected_zone_change_indices_before[selected_index]) {
                        add_error(out, "return_cost_payment_record.zone_change_snapshot_mismatch", prefix + " return-cost zone-change witness does not use the selected object's pre-payment zone snapshot");
                    }
                    if (std::find(witnessed_objects.begin(), witnessed_objects.end(), zone_record.object) != witnessed_objects.end()) {
                        add_error(out, "return_cost_payment_record.duplicate_zone_change_witness", prefix + " has multiple return-cost zone-change witnesses for one selected object");
                    } else {
                        witnessed_objects.push_back(zone_record.object);
                    }
                }
                if (zone_record.from_zone != Zone::Battlefield || zone_record.requested_zone != Zone::Hand || zone_record.to_zone != Zone::Hand) {
                    add_error(out, "return_cost_payment_record.zone_change_shape_mismatch", prefix + " linked zone change is not battlefield-to-hand return movement");
                }
                if (zone_record.previous_controller != record.payer) {
                    add_error(out, "return_cost_payment_record.zone_change_payer_mismatch", prefix + " linked zone change names a different previous controller");
                }
                if (zone_record.sequence >= record.sequence) {
                    add_error(out, "return_cost_payment_record.zone_change_sequence_not_before_payment_event", prefix + " returned object movement did not occur before the summary pay_return_cost event");
                }
            }
            if (witnessed_objects.size() != record.selected_objects.size()) {
                add_error(out, "return_cost_payment_record.missing_zone_change_witness", prefix + " does not witness every selected returned object");
            }
        }
        const auto payment_event_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
            return event_record.sequence == record.sequence;
        });
        if (payment_event_it == game.event_records.end()) {
            add_error(out, "return_cost_payment_record.event_witness_missing", prefix + " sequence does not name an EventRecord");
        } else {
            const auto& event_record = *payment_event_it;
            if (event_record.kind != EventRecordKind::Log || event_record.log_kind != "pay_return_cost") {
                add_error(out, "return_cost_payment_record.event_witness_not_payment", prefix + " sequence does not name a pay_return_cost log row");
            }
            if (event_record.player != record.payer) {
                add_error(out, "return_cost_payment_record.event_witness_payer_mismatch", prefix + " pay_return_cost event names a different payer");
            }
            if (record.source_object.valid() && event_record.object != record.source_object) {
                add_error(out, "return_cost_payment_record.event_witness_source_mismatch", prefix + " pay_return_cost event names a different source object");
            }
        }
    }

    u64 last_loyalty_payment_sequence = 0;
    for (std::size_t i = 0; i < game.loyalty_cost_payment_records.size(); ++i) {
        const auto& record = game.loyalty_cost_payment_records[i];
        const std::string prefix = "loyalty_cost_payment_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "loyalty_cost_payment_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "loyalty_cost_payment_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_loyalty_payment_sequence != 0U && record.sequence <= last_loyalty_payment_sequence) {
            add_error(out, "loyalty_cost_payment_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_loyalty_payment_sequence = record.sequence;
        if (!is_valid_player_ref(game, record.payer)) {
            add_error(out, "loyalty_cost_payment_record.invalid_payer", prefix + " payer=" + player_ref(record.payer));
        }
        if (!is_valid_object_ref(game, record.source_object)) {
            add_error(out, "loyalty_cost_payment_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (record.source_zone_change_index_before == 0U) {
            add_error(out, "loyalty_cost_payment_record.missing_source_zone_change_index", prefix + " has no source zone-change snapshot");
        }
        if (record.cost_delta == 0) {
            add_error(out, "loyalty_cost_payment_record.zero_cost_delta", prefix + " records no active loyalty cost");
        }
        if (record.payment_hash == 0U) {
            add_error(out, "loyalty_cost_payment_record.zero_hash", prefix + " has payment_hash=0");
        } else if (record.payment_hash != loyalty_cost_payment_record_hash(record)) {
            add_error(out, "loyalty_cost_payment_record.hash_mismatch", prefix + " payment_hash does not match the sealed payment payload");
        }
        if (record.counter_change_record_index == 0U || record.counter_change_record_index > game.counter_change_records.size()) {
            add_error(out, "loyalty_cost_payment_record.invalid_counter_change_link", prefix + " links a counter-change record outside the journal");
        } else {
            const auto& counter = game.counter_change_records[record.counter_change_record_index - 1U];
            const u32 absolute_delta = record.cost_delta < 0 ? static_cast<u32>(-record.cost_delta) : static_cast<u32>(record.cost_delta);
            const auto expected_kind = record.cost_delta > 0 ? CounterChangeKind::ObjectAdded : CounterChangeKind::ObjectRemoved;
            if (counter.sequence != record.sequence) {
                add_error(out, "loyalty_cost_payment_record.counter_change_sequence_mismatch", prefix + " linked counter-change sequence differs from the payment receipt");
            }
            if (counter.kind != expected_kind || counter.counter_kind != CounterKind::Loyalty || counter.amount != absolute_delta) {
                add_error(out, "loyalty_cost_payment_record.counter_change_shape_mismatch", prefix + " linked counter change is not the expected loyalty-cost mutation");
            }
            if (counter.object != record.source_object) {
                add_error(out, "loyalty_cost_payment_record.counter_change_source_mismatch", prefix + " linked counter change names a different permanent");
            }
            if (counter.player != record.payer) {
                add_error(out, "loyalty_cost_payment_record.counter_change_payer_mismatch", prefix + " linked counter change names a different controller");
            }
            if (counter.object_zone_change_index != record.source_zone_change_index_before) {
                add_error(out, "loyalty_cost_payment_record.counter_change_zone_snapshot_mismatch", prefix + " linked counter change names a different zone-change snapshot");
            }
            const std::int64_t expected_after = static_cast<std::int64_t>(record.loyalty_before) + static_cast<std::int64_t>(record.cost_delta);
            if (expected_after < 0 || static_cast<u32>(expected_after) != record.loyalty_after ||
                counter.count_before != record.loyalty_before || counter.count_after != record.loyalty_after) {
                add_error(out, "loyalty_cost_payment_record.counter_change_total_mismatch", prefix + " linked loyalty totals differ from the payment receipt");
            }
            if (counter.source != record.source_object || counter.source_zone_change_index != record.source_zone_change_index_before) {
                add_error(out, "loyalty_cost_payment_record.counter_change_cost_source_mismatch", prefix + " linked counter change does not identify the paying permanent as source");
            }
            if (!counter.cost_payment || counter.damage_result || counter.zone_change_cleanup) {
                add_error(out, "loyalty_cost_payment_record.counter_change_not_pure_cost", prefix + " linked counter change carries non-cost metadata");
            }
        }
        const auto payment_event_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
            return event_record.sequence == record.sequence;
        });
        if (payment_event_it == game.event_records.end()) {
            add_error(out, "loyalty_cost_payment_record.event_witness_missing", prefix + " sequence does not name an EventRecord");
        } else {
            const auto& event_record = *payment_event_it;
            if (event_record.kind != EventRecordKind::CounterChange || event_record.log_kind != "loyalty_cost_paid") {
                add_error(out, "loyalty_cost_payment_record.event_witness_not_payment", prefix + " sequence does not name a loyalty_cost_paid CounterChange row");
            }
            if (event_record.player != record.payer) {
                add_error(out, "loyalty_cost_payment_record.event_witness_payer_mismatch", prefix + " loyalty_cost_paid event names a different payer");
            }
            if (event_record.object != record.source_object) {
                add_error(out, "loyalty_cost_payment_record.event_witness_source_mismatch", prefix + " loyalty_cost_paid event names a different source object");
            }
            if (event_record.counter_change_record_index != record.counter_change_record_index) {
                add_error(out, "loyalty_cost_payment_record.event_witness_counter_change_mismatch", prefix + " loyalty_cost_paid event names a different counter-change record");
            }
        }
    }


    u64 last_mana_change_sequence = 0;
    for (std::size_t i = 0; i < game.mana_change_records.size(); ++i) {
        const auto& record = game.mana_change_records[i];
        const std::string prefix = "mana_change_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "mana_change_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "mana_change_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_mana_change_sequence != 0U && record.sequence <= last_mana_change_sequence) {
            add_error(out, "mana_change_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_mana_change_sequence = record.sequence;
        if (i + 1U < mana_change_event_links.size() && mana_change_event_links[i + 1U] != 1U) {
            add_error(out, "mana_change_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(mana_change_event_links[i + 1U]));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "mana_change_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.kind == ManaChangeKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(ManaChangeKind::Count)) {
            add_error(out, "mana_change_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (record.source.valid()) {
            if (!is_valid_object_ref(game, record.source)) {
                add_error(out, "mana_change_record.invalid_source", prefix + " source=" + object_ref(record.source));
            }
            if (record.source_zone_change_index == 0U) {
                add_error(out, "mana_change_record.missing_source_zone_change_index", prefix + " source has no zone-change snapshot");
            }
        } else if (record.source_zone_change_index != 0U) {
            add_error(out, "mana_change_record.source_zone_change_without_source", prefix + " has source zone-change metadata without a source");
        }
        if (record.mana_ability_index != 0U && !record.source.valid()) {
            add_error(out, "mana_change_record.ability_index_without_source", prefix + " has mana_ability_index without a source object");
        }
        const bool has_auto_plan_metadata = record.auto_payment_mana_ability_count != 0U ||
                                            record.auto_payment_locked_tap_source_count != 0U;
        const bool has_auto_plan_hash = record.auto_payment_plan_hash != 0U;
        const bool has_auto_plan_record = record.auto_payment_plan_record_index != 0U;
        const bool has_auto_plan_producer_link = record.auto_payment_producer_plan_record_index != 0U ||
                                                record.auto_payment_producer_plan_step_index != 0U;
        if (record.kind != ManaChangeKind::Paid && record.auto_payment) {
            add_error(out, "mana_change_record.auto_payment_on_nonpayment", prefix + " marks auto_payment outside a paid record");
        }
        if (record.kind != ManaChangeKind::Paid && has_auto_plan_metadata) {
            add_error(out, "mana_change_record.plan_metadata_on_nonpayment", prefix + " carries auto-payment plan metadata outside a paid record");
        }
        if (record.kind != ManaChangeKind::Paid && has_auto_plan_hash) {
            add_error(out, "mana_change_record.plan_hash_on_nonpayment", prefix + " carries auto-payment plan hash outside a paid record");
        }
        if (record.kind != ManaChangeKind::Paid && has_auto_plan_record) {
            add_error(out, "mana_change_record.plan_record_on_nonpayment", prefix + " carries an auto-payment plan record link outside a paid record");
        }
        if (record.kind != ManaChangeKind::Produced && has_auto_plan_producer_link) {
            add_error(out, "mana_change_record.producer_plan_link_on_nonproduction", prefix + " carries an auto-payment producer plan link outside a produced record");
        }
        if (has_auto_plan_metadata && !record.auto_payment) {
            add_error(out, "mana_change_record.plan_metadata_without_auto_payment", prefix + " carries auto-payment plan metadata without auto_payment=true");
        }
        if (has_auto_plan_hash && !record.auto_payment) {
            add_error(out, "mana_change_record.plan_hash_without_auto_payment", prefix + " carries auto-payment plan hash without auto_payment=true");
        }
        if (has_auto_plan_record && !record.auto_payment) {
            add_error(out, "mana_change_record.plan_record_without_auto_payment", prefix + " carries an auto-payment plan record link without auto_payment=true");
        }
        if (record.kind == ManaChangeKind::Paid && record.auto_payment && record.auto_payment_plan_hash == 0U) {
            add_error(out, "mana_change_record.auto_payment_plan_hash_missing", prefix + " marks automatic payment without a stable plan hash");
        }
        if (record.kind == ManaChangeKind::Paid && record.auto_payment && record.auto_payment_plan_record_index == 0U) {
            add_error(out, "mana_change_record.auto_payment_plan_record_missing", prefix + " marks automatic payment without a typed plan record link");
        }
        if (record.auto_payment_plan_record_index > game.mana_payment_plan_records.size()) {
            add_error(out, "mana_change_record.invalid_auto_payment_plan_record", prefix + " links invalid auto_payment_plan_record_index=" + std::to_string(record.auto_payment_plan_record_index));
        } else if (record.auto_payment_plan_record_index != 0U) {
            const auto& plan_record = game.mana_payment_plan_records[record.auto_payment_plan_record_index - 1U];
            if (plan_record.paid_mana_change_record_index != i + 1U) {
                add_error(out, "mana_change_record.plan_record_backlink_mismatch", prefix + " linked plan record does not point back to this paid record");
            }
            if (plan_record.player != record.player) {
                add_error(out, "mana_change_record.plan_record_player_mismatch", prefix + " linked plan record has a different player");
            }
            if (!same_mana_cost_for_validation(plan_record.cost, record.cost)) {
                add_error(out, "mana_change_record.plan_record_cost_mismatch", prefix + " linked plan record has a different cost");
            }
            if (plan_record.plan_hash != record.auto_payment_plan_hash) {
                add_error(out, "mana_change_record.plan_record_hash_mismatch", prefix + " linked plan record has a different hash");
            }
            if (record.kind == ManaChangeKind::Paid && !mana_pool_equals(plan_record.pool_before_payment, record.pool_before)) {
                add_error(out, "mana_change_record.plan_record_pool_before_payment_mismatch", prefix + " linked plan record pool_before_payment does not match this paid record pool_before");
            }
        }
        if ((record.auto_payment_producer_plan_record_index == 0U) != (record.auto_payment_producer_plan_step_index == 0U)) {
            add_error(out, "mana_change_record.incomplete_producer_plan_link", prefix + " carries only one side of the auto-payment producer plan-step backlink");
        }
        if (record.auto_payment_producer_plan_record_index > game.mana_payment_plan_records.size()) {
            add_error(out, "mana_change_record.invalid_producer_plan_record_link", prefix + " links invalid auto_payment_producer_plan_record_index=" + std::to_string(record.auto_payment_producer_plan_record_index));
        } else if (record.auto_payment_producer_plan_record_index != 0U) {
            const auto& plan_record = game.mana_payment_plan_records[record.auto_payment_producer_plan_record_index - 1U];
            if (record.auto_payment_producer_plan_step_index == 0U ||
                record.auto_payment_producer_plan_step_index > plan_record.mana_ability_steps.size()) {
                add_error(out, "mana_change_record.invalid_producer_plan_step_link", prefix + " links invalid auto_payment_producer_plan_step_index=" + std::to_string(record.auto_payment_producer_plan_step_index));
            } else {
                const auto& plan_step = plan_record.mana_ability_steps[record.auto_payment_producer_plan_step_index - 1U];
                if (plan_step.produced_mana_change_record_index != i + 1U) {
                    add_error(out, "mana_change_record.producer_plan_step_backlink_mismatch", prefix + " linked plan step does not point back to this produced ManaChangeRecord");
                }
            }
        }
        switch (record.kind) {
            case ManaChangeKind::Produced:
                if (mana_pool_is_empty(record.added)) {
                    add_error(out, "mana_change_record.produced_empty", prefix + " produced no mana");
                }
                if (!mana_pool_is_empty(record.spent)) {
                    add_error(out, "mana_change_record.produced_has_spent", prefix + " produced mana but also records spent mana");
                }
                if (!record.cost.free()) {
                    add_error(out, "mana_change_record.produced_has_cost", prefix + " produced mana but carries a cost payload");
                }
                if (!mana_pool_add_delta_matches(record.pool_before, record.added, record.pool_after)) {
                    add_error(out, "mana_change_record.produced_delta_mismatch", prefix + " produced mana does not match before/after pools");
                }
                break;
            case ManaChangeKind::Paid:
                if (mana_pool_is_empty(record.spent)) {
                    add_error(out, "mana_change_record.paid_empty_spent", prefix + " paid cost without recording spent mana");
                }
                if (!mana_pool_is_empty(record.added)) {
                    add_error(out, "mana_change_record.paid_has_added", prefix + " paid cost but also records added mana");
                }
                if (!mana_pool_spend_delta_matches(record.pool_before, record.spent, record.pool_after)) {
                    add_error(out, "mana_change_record.paid_delta_mismatch", prefix + " spent mana does not match before/after pools");
                }
                if (record.spent.total() != record.cost.total_symbols()) {
                    add_error(out, "mana_change_record.paid_cost_total_mismatch", prefix + " spent total does not match mana cost total");
                }
                if (record.spent.white < record.cost.white || record.spent.blue < record.cost.blue ||
                    record.spent.black < record.cost.black || record.spent.red < record.cost.red ||
                    record.spent.green < record.cost.green) {
                    add_error(out, "mana_change_record.paid_colored_cost_mismatch", prefix + " spent colored mana does not satisfy colored requirements");
                }
                if (record.spent.colorless < record.cost.colorless) {
                    add_error(out, "mana_change_record.paid_colorless_cost_mismatch", prefix + " spent colorless mana does not satisfy colorless requirements");
                }
                break;
            case ManaChangeKind::Emptied:
                if (!mana_pool_is_empty(record.added)) {
                    add_error(out, "mana_change_record.emptied_has_added", prefix + " emptied pool but records added mana");
                }
                if (!record.cost.free()) {
                    add_error(out, "mana_change_record.emptied_has_cost", prefix + " emptied pool but carries a cost payload");
                }
                if (!mana_pool_is_empty(record.pool_after)) {
                    add_error(out, "mana_change_record.emptied_after_not_empty", prefix + " pool should be empty after clearing");
                }
                if (!mana_pool_equals(record.spent, record.pool_before)) {
                    add_error(out, "mana_change_record.emptied_spent_mismatch", prefix + " spent payload should equal the cleared pool");
                }
                if (!mana_pool_spend_delta_matches(record.pool_before, record.spent, record.pool_after)) {
                    add_error(out, "mana_change_record.emptied_delta_mismatch", prefix + " cleared mana does not match before/after pools");
                }
                break;
            case ManaChangeKind::Count:
                break;
        }
    }

    u64 last_paid_action_declaration_sequence = 0;
    for (std::size_t i = 0; i < game.paid_action_declaration_records.size(); ++i) {
        const auto& record = game.paid_action_declaration_records[i];
        const std::string prefix = "paid_action_declaration_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "paid_action_declaration_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "paid_action_declaration_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_paid_action_declaration_sequence != 0U && record.sequence <= last_paid_action_declaration_sequence) {
            add_error(out, "paid_action_declaration_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_paid_action_declaration_sequence = record.sequence;
        if (i + 1U < paid_action_declaration_event_links.size() && paid_action_declaration_event_links[i + 1U] != 1U) {
            add_error(out, "paid_action_declaration_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(paid_action_declaration_event_links[i + 1U]));
        }
        if (record.schema_version != kPaidActionDeclarationRecordSchemaVersion) {
            add_error(out, "paid_action_declaration_record.schema_mismatch", prefix + " has unsupported schema_version=" + std::to_string(record.schema_version));
        }
        const bool declaration_is_spell = record.action_kind == ActionKind::CastSpellFromHandPaid;
        const bool declaration_is_activated = record.action_kind == ActionKind::ActivateActivatedAbility;
        const bool declaration_is_loyalty = record.action_kind == ActionKind::ActivateLoyaltyAbility;
        if (!declaration_is_spell && !declaration_is_activated && !declaration_is_loyalty) {
            add_error(out, "paid_action_declaration_record.invalid_action_kind", prefix + " action_kind is not a supported paid declaration kind");
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "paid_action_declaration_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (!is_valid_object_ref(game, record.source_object)) {
            add_error(out, "paid_action_declaration_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (!is_valid_object_ref(game, record.stack_object)) {
            add_error(out, "paid_action_declaration_record.invalid_stack_object", prefix + " stack_object=" + object_ref(record.stack_object));
        }
        if (record.definition_index >= game.definitions.size()) {
            add_error(out, "paid_action_declaration_record.invalid_definition_index", prefix + " links invalid definition_index=" + std::to_string(record.definition_index));
        }
        if (record.source_zone_change_index_before == 0U || record.stack_zone_change_index == 0U) {
            add_error(out, "paid_action_declaration_record.missing_zone_anchor", prefix + " lacks source/stack zone-change anchors");
        }
        if (declaration_is_spell) {
            if (record.source_object != record.stack_object) {
                add_error(out, "paid_action_declaration_record.source_stack_mismatch", prefix + " paid spell declaration should keep source and stack object identical");
            }
            if (record.source_zone_before != Zone::Hand) {
                add_error(out, "paid_action_declaration_record.source_zone_not_hand", prefix + " paid spell declaration should start from hand");
            }
            if (record.stack_enter_zone_change_record_index == 0U) {
                add_error(out, "paid_action_declaration_record.missing_stack_enter_zone_change", prefix + " paid spell declaration lacks a stack-enter ZoneChangeRecord link");
            }
            if (record.ability_index != 0U || record.tap_cost_required || record.loyalty_cost_required || record.loyalty_cost_delta != 0) {
                add_error(out, "paid_action_declaration_record.spell_has_ability_cost_shape", prefix + " paid spell declaration unexpectedly carries ability cost/index fields");
            }
        } else if (declaration_is_activated || declaration_is_loyalty) {
            if (record.source_object == record.stack_object) {
                add_error(out, "paid_action_declaration_record.ability_source_stack_same", prefix + " ability declaration should separate source and synthetic stack object");
            }
            if (record.source_zone_before != Zone::Battlefield) {
                add_error(out, "paid_action_declaration_record.ability_source_zone_not_battlefield", prefix + " ability declaration should start from battlefield");
            }
            if (record.stack_enter_zone_change_record_index != 0U) {
                add_error(out, "paid_action_declaration_record.ability_has_stack_enter_zone_change", prefix + " synthetic ability declaration should not link a card-move ZoneChangeRecord");
            }
            if (record.ability_index == 0U) {
                add_error(out, "paid_action_declaration_record.ability_missing_index", prefix + " ability declaration missing ability_index");
            }
            if (declaration_is_activated && (record.loyalty_cost_required || record.loyalty_cost_delta != 0)) {
                add_error(out, "paid_action_declaration_record.activated_has_loyalty_cost", prefix + " activated ability declaration unexpectedly carries loyalty cost state");
            }
            if (declaration_is_loyalty) {
                if (!record.loyalty_cost_required) {
                    add_error(out, "paid_action_declaration_record.loyalty_cost_not_required", prefix + " loyalty ability declaration should lock a loyalty cost");
                }
                if (record.mana_cost_required || record.tap_cost_required || record.sacrifice_cost_required || record.discard_cost_required || record.life_cost_required) {
                    add_error(out, "paid_action_declaration_record.loyalty_has_nonloyalty_cost", prefix + " loyalty ability declaration unexpectedly carries mana/tap/sacrifice/discard/life costs");
                }
            }
        }
        if (record.stack_object_entered_sequence == 0U || record.stack_object_entered_sequence >= record.sequence) {
            add_error(out, "paid_action_declaration_record.stack_entry_order", prefix + " declaration should follow stack entry");
        }
        if (record.choices_locked_sequence != 0U && record.choices_locked_sequence > record.sequence) {
            add_error(out, "paid_action_declaration_record.choice_lock_after_declaration", prefix + " choice-lock sequence should not be after declaration");
        }
        if (!record.total_cost_locked) {
            add_error(out, "paid_action_declaration_record.total_cost_not_locked", prefix + " does not mark total cost as locked");
        }
        if (record.declaration_hash == 0U) {
            add_error(out, "paid_action_declaration_record.zero_hash", prefix + " has declaration_hash=0");
        } else if (record.declaration_hash != paid_action_declaration_record_hash(record)) {
            add_error(out, "paid_action_declaration_record.hash_mismatch", prefix + " declaration_hash does not match the declaration/cost-lock payload");
        }
        if (record.declared_target_set_hash != target_choice_set_hash(record.declared_targets)) {
            add_error(out, "paid_action_declaration_record.target_set_hash_mismatch", prefix + " target-set hash disagrees with declared_targets");
        }
        if (record.declared_targets.size() > record.target_count && record.target_count != 0U) {
            add_error(out, "paid_action_declaration_record.too_many_targets", prefix + " declared more targets than target_count");
        }
        if ((record.first_payment_event_sequence == 0U) != (record.last_payment_event_sequence == 0U)) {
            add_error(out, "paid_action_declaration_record.payment_span_incomplete", prefix + " carries only one side of the payment span");
        }
        if (record.payment_attempted && record.first_payment_event_sequence == 0U) {
            add_error(out, "paid_action_declaration_record.payment_attempt_without_span", prefix + " marks payment_attempted without a payment event span");
        }
        if (record.first_payment_event_sequence != 0U) {
            if (record.first_payment_event_sequence <= record.sequence) {
                add_error(out, "paid_action_declaration_record.payment_not_after_declaration", prefix + " payment span should begin after declaration");
            }
            if (record.first_payment_event_sequence > record.last_payment_event_sequence) {
                add_error(out, "paid_action_declaration_record.payment_span_reversed", prefix + " payment event span is reversed");
            }
        }
        if (record.sacrifice_cost_payment_record_count == 0U) {
            if (record.first_sacrifice_cost_payment_record_index != 0U || record.sacrifice_cost_payment_hash != 0U) {
                add_error(out, "paid_action_declaration_record.unexpected_sacrifice_payment_receipt", prefix + " carries sacrifice-cost payment receipt metadata without a receipt count");
            }
        } else {
            if (!record.sacrifice_cost_required) {
                add_error(out, "paid_action_declaration_record.unexpected_sacrifice_payment_receipt", prefix + " links sacrifice-cost payment receipts without locking a sacrifice cost");
            }
            if (record.first_sacrifice_cost_payment_record_index == 0U ||
                static_cast<u64>(record.first_sacrifice_cost_payment_record_index) + static_cast<u64>(record.sacrifice_cost_payment_record_count) - 1U > game.sacrifice_cost_payment_records.size()) {
                add_error(out, "paid_action_declaration_record.invalid_sacrifice_payment_range", prefix + " links a sacrifice-cost payment receipt range outside the journal");
            } else {
                for (u32 offset = 0; offset < record.sacrifice_cost_payment_record_count; ++offset) {
                    const auto& payment = game.sacrifice_cost_payment_records[record.first_sacrifice_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.sequence) {
                        add_error(out, "paid_action_declaration_record.sacrifice_payment_not_after_declaration", prefix + " sacrifice-cost receipt should be after the declaration/cost lock");
                    }
                    if (payment.payer != record.player) {
                        add_error(out, "paid_action_declaration_record.sacrifice_payment_payer_mismatch", prefix + " linked sacrifice-cost payment has a different payer");
                    }
                    if (payment.source_object.valid() && payment.source_object != record.source_object) {
                        add_error(out, "paid_action_declaration_record.sacrifice_payment_source_mismatch", prefix + " linked sacrifice-cost payment has a different source object");
                    }
                    if (record.sacrifice_cost_payment_record_count == 1U && payment.payment_hash != record.sacrifice_cost_payment_hash) {
                        add_error(out, "paid_action_declaration_record.sacrifice_payment_hash_mismatch", prefix + " sacrifice-cost payment hash differs from the linked receipt");
                    }
                }
            }
            if (record.sacrifice_cost_payment_record_count == 1U && record.sacrifice_cost_payment_hash == 0U) {
                add_error(out, "paid_action_declaration_record.missing_sacrifice_payment_hash", prefix + " links one sacrifice-cost payment receipt but stores no receipt hash");
            }
        }
        if (record.discard_cost_payment_record_count == 0U) {
            if (record.first_discard_cost_payment_record_index != 0U || record.discard_cost_payment_hash != 0U) {
                add_error(out, "paid_action_declaration_record.unexpected_discard_payment_receipt", prefix + " carries discard-cost payment receipt metadata without a receipt count");
            }
        } else {
            if (!record.discard_cost_required) {
                add_error(out, "paid_action_declaration_record.unexpected_discard_payment_receipt", prefix + " links discard-cost payment receipts without locking a discard cost");
            }
            if (record.first_discard_cost_payment_record_index == 0U ||
                static_cast<u64>(record.first_discard_cost_payment_record_index) + static_cast<u64>(record.discard_cost_payment_record_count) - 1U > game.discard_cost_payment_records.size()) {
                add_error(out, "paid_action_declaration_record.invalid_discard_payment_range", prefix + " links a discard-cost payment receipt range outside the journal");
            } else {
                for (u32 offset = 0; offset < record.discard_cost_payment_record_count; ++offset) {
                    const auto& payment = game.discard_cost_payment_records[record.first_discard_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.sequence) {
                        add_error(out, "paid_action_declaration_record.discard_payment_not_after_declaration", prefix + " discard-cost receipt should be after the declaration/cost lock");
                    }
                    if (payment.payer != record.player) {
                        add_error(out, "paid_action_declaration_record.discard_payment_payer_mismatch", prefix + " linked discard-cost payment has a different payer");
                    }
                    if (payment.source_object.valid() && payment.source_object != record.source_object) {
                        add_error(out, "paid_action_declaration_record.discard_payment_source_mismatch", prefix + " linked discard-cost payment has a different source object");
                    }
                    if (record.discard_cost_payment_record_count == 1U && payment.payment_hash != record.discard_cost_payment_hash) {
                        add_error(out, "paid_action_declaration_record.discard_payment_hash_mismatch", prefix + " discard-cost payment hash differs from the linked receipt");
                    }
                }
            }
            if (record.discard_cost_payment_record_count == 1U && record.discard_cost_payment_hash == 0U) {
                add_error(out, "paid_action_declaration_record.missing_discard_payment_hash", prefix + " links one discard-cost payment receipt but stores no receipt hash");
            }
        }
        if (record.tap_cost_payment_record_count == 0U) {
            if (record.first_tap_cost_payment_record_index != 0U || record.tap_cost_payment_hash != 0U) {
                add_error(out, "paid_action_declaration_record.unexpected_tap_payment_receipt", prefix + " carries tap-cost payment receipt metadata without a receipt count");
            }
        } else {
            if (!record.tap_cost_required) {
                add_error(out, "paid_action_declaration_record.unexpected_tap_payment_receipt", prefix + " links tap-cost payment receipts without locking a tap cost");
            }
            if (record.first_tap_cost_payment_record_index == 0U ||
                static_cast<u64>(record.first_tap_cost_payment_record_index) + static_cast<u64>(record.tap_cost_payment_record_count) - 1U > game.tap_cost_payment_records.size()) {
                add_error(out, "paid_action_declaration_record.invalid_tap_payment_range", prefix + " links a tap-cost payment receipt range outside the journal");
            } else {
                for (u32 offset = 0; offset < record.tap_cost_payment_record_count; ++offset) {
                    const auto& payment = game.tap_cost_payment_records[record.first_tap_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.sequence) {
                        add_error(out, "paid_action_declaration_record.tap_payment_not_after_declaration", prefix + " tap-cost receipt should be after the declaration/cost lock");
                    }
                    if (payment.payer != record.player) {
                        add_error(out, "paid_action_declaration_record.tap_payment_payer_mismatch", prefix + " linked tap-cost payment has a different payer");
                    }
                    if (payment.source_object != record.source_object) {
                        add_error(out, "paid_action_declaration_record.tap_payment_source_mismatch", prefix + " linked tap-cost payment has a different source object");
                    }
                    if (record.tap_cost_payment_record_count == 1U && payment.payment_hash != record.tap_cost_payment_hash) {
                        add_error(out, "paid_action_declaration_record.tap_payment_hash_mismatch", prefix + " tap-cost payment hash differs from the linked receipt");
                    }
                }
            }
            if (record.tap_cost_payment_record_count == 1U && record.tap_cost_payment_hash == 0U) {
                add_error(out, "paid_action_declaration_record.missing_tap_payment_hash", prefix + " links one tap-cost payment receipt but stores no receipt hash");
            }
        }
        if (record.life_cost_payment_record_count == 0U) {
            if (record.first_life_cost_payment_record_index != 0U || record.life_cost_payment_hash != 0U) {
                add_error(out, "paid_action_declaration_record.unexpected_life_payment_receipt", prefix + " carries life-cost payment receipt metadata without a receipt count");
            }
        } else {
            if (!record.life_cost_required) {
                add_error(out, "paid_action_declaration_record.unexpected_life_payment_receipt", prefix + " links life-cost payment receipts without locking a life cost");
            }
            if (record.first_life_cost_payment_record_index == 0U ||
                static_cast<u64>(record.first_life_cost_payment_record_index) + static_cast<u64>(record.life_cost_payment_record_count) - 1U > game.life_cost_payment_records.size()) {
                add_error(out, "paid_action_declaration_record.invalid_life_payment_range", prefix + " links a life-cost payment receipt range outside the journal");
            } else {
                for (u32 offset = 0; offset < record.life_cost_payment_record_count; ++offset) {
                    const auto& payment = game.life_cost_payment_records[record.first_life_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.sequence) {
                        add_error(out, "paid_action_declaration_record.life_payment_not_after_declaration", prefix + " life-cost receipt should be after the declaration/cost lock");
                    }
                    if (payment.payer != record.player) {
                        add_error(out, "paid_action_declaration_record.life_payment_payer_mismatch", prefix + " linked life-cost payment has a different payer");
                    }
                    if (payment.source_object.valid() && payment.source_object != record.source_object) {
                        add_error(out, "paid_action_declaration_record.life_payment_source_mismatch", prefix + " linked life-cost payment has a different source object");
                    }
                    if (payment.cost.amount != record.life_cost.amount) {
                        add_error(out, "paid_action_declaration_record.life_payment_amount_mismatch", prefix + " linked life-cost payment amount differs from the locked cost");
                    }
                    if (record.life_cost_payment_record_count == 1U && payment.payment_hash != record.life_cost_payment_hash) {
                        add_error(out, "paid_action_declaration_record.life_payment_hash_mismatch", prefix + " life-cost payment hash differs from the linked receipt");
                    }
                }
            }
            if (record.life_cost_payment_record_count == 1U && record.life_cost_payment_hash == 0U) {
                add_error(out, "paid_action_declaration_record.missing_life_payment_hash", prefix + " links one life-cost payment receipt but stores no receipt hash");
            }
        }
        if (record.loyalty_cost_payment_record_count == 0U) {
            if (record.first_loyalty_cost_payment_record_index != 0U || record.loyalty_cost_payment_hash != 0U) {
                add_error(out, "paid_action_declaration_record.unexpected_loyalty_payment_receipt", prefix + " carries loyalty-cost payment receipt metadata without a receipt count");
            }
        } else {
            if (!record.loyalty_cost_required) {
                add_error(out, "paid_action_declaration_record.unexpected_loyalty_payment_receipt", prefix + " links loyalty-cost payment receipts without locking a loyalty cost");
            }
            if (record.first_loyalty_cost_payment_record_index == 0U ||
                static_cast<u64>(record.first_loyalty_cost_payment_record_index) + static_cast<u64>(record.loyalty_cost_payment_record_count) - 1U > game.loyalty_cost_payment_records.size()) {
                add_error(out, "paid_action_declaration_record.invalid_loyalty_payment_range", prefix + " links a loyalty-cost payment receipt range outside the journal");
            } else {
                for (u32 offset = 0; offset < record.loyalty_cost_payment_record_count; ++offset) {
                    const auto& payment = game.loyalty_cost_payment_records[record.first_loyalty_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.sequence) {
                        add_error(out, "paid_action_declaration_record.loyalty_payment_not_after_declaration", prefix + " loyalty-cost receipt should be after the declaration/cost lock");
                    }
                    if (payment.payer != record.player) {
                        add_error(out, "paid_action_declaration_record.loyalty_payment_payer_mismatch", prefix + " linked loyalty-cost payment has a different payer");
                    }
                    if (payment.source_object != record.source_object) {
                        add_error(out, "paid_action_declaration_record.loyalty_payment_source_mismatch", prefix + " linked loyalty-cost payment has a different source object");
                    }
                    if (payment.source_zone_change_index_before != record.source_zone_change_index_before) {
                        add_error(out, "paid_action_declaration_record.loyalty_payment_zone_snapshot_mismatch", prefix + " linked loyalty-cost payment names a different source zone-change snapshot");
                    }
                    if (payment.cost_delta != record.loyalty_cost_delta) {
                        add_error(out, "paid_action_declaration_record.loyalty_payment_cost_delta_mismatch", prefix + " linked loyalty-cost payment delta differs from the locked cost");
                    }
                    if (record.loyalty_cost_payment_record_count == 1U && payment.payment_hash != record.loyalty_cost_payment_hash) {
                        add_error(out, "paid_action_declaration_record.loyalty_payment_hash_mismatch", prefix + " loyalty-cost payment hash differs from the linked receipt");
                    }
                }
            }
            if (record.loyalty_cost_payment_record_count == 1U && record.loyalty_cost_payment_hash == 0U) {
                add_error(out, "paid_action_declaration_record.missing_loyalty_payment_hash", prefix + " links one loyalty-cost payment receipt but stores no receipt hash");
            }
        }
        if (record.stack_placement_record_index == 0U || record.stack_placement_record_index > game.stack_placement_records.size()) {
            add_error(out, "paid_action_declaration_record.invalid_stack_placement_link", prefix + " links invalid stack_placement_record_index=" + std::to_string(record.stack_placement_record_index));
        } else {
            const auto& placement = game.stack_placement_records[record.stack_placement_record_index - 1U];
            if (placement.paid_action_declaration_record_index != i + 1U) {
                add_error(out, "paid_action_declaration_record.backlink_mismatch", prefix + " linked StackPlacementRecord does not point back to this declaration");
            }
            if (placement.paid_action_declaration_hash != record.declaration_hash) {
                add_error(out, "paid_action_declaration_record.stack_hash_mismatch", prefix + " linked StackPlacementRecord stores a different declaration hash");
            }
            const StackPlacementKind expected_placement_kind = declaration_is_spell
                ? StackPlacementKind::SpellCast
                : (declaration_is_activated ? StackPlacementKind::ActivatedAbility : StackPlacementKind::LoyaltyAbility);
            if (placement.kind != expected_placement_kind || placement.source_object != record.source_object ||
                placement.stack_object != record.stack_object || placement.controller != record.player) {
                add_error(out, "paid_action_declaration_record.stack_identity_mismatch", prefix + " linked StackPlacementRecord identity differs from declaration");
            }
            if (placement.sequence <= record.sequence) {
                add_error(out, "paid_action_declaration_record.stack_placement_not_after_declaration", prefix + " placement should occur after declaration");
            }
            if (placement.ability_index != record.ability_index || placement.loyalty_cost_delta != record.loyalty_cost_delta ||
                placement.chosen_mode_index != record.declared_mode_index || placement.target_mask != record.target_mask || placement.target_count != record.target_count ||
                target_choice_set_hash(placement.chosen_targets) != record.declared_target_set_hash) {
                add_error(out, "paid_action_declaration_record.choice_payload_mismatch", prefix + " linked StackPlacementRecord choice payload differs from declaration");
            }
            if (placement.mana_cost_required != record.mana_cost_required || placement.tap_cost_required != record.tap_cost_required ||
                placement.sacrifice_cost_required != record.sacrifice_cost_required ||
                placement.discard_cost_required != record.discard_cost_required ||
                placement.life_cost_required != record.life_cost_required ||
                placement.loyalty_cost_paid != record.loyalty_cost_required) {
                add_error(out, "paid_action_declaration_record.cost_flag_mismatch", prefix + " linked StackPlacementRecord cost flags differ from declaration");
            }
            if (placement.first_sacrifice_cost_payment_record_index != record.first_sacrifice_cost_payment_record_index ||
                placement.sacrifice_cost_payment_record_count != record.sacrifice_cost_payment_record_count ||
                placement.sacrifice_cost_payment_hash != record.sacrifice_cost_payment_hash) {
                add_error(out, "paid_action_declaration_record.sacrifice_payment_receipt_mismatch", prefix + " linked StackPlacementRecord sacrifice-cost payment receipt range differs from declaration");
            }
            if (placement.first_discard_cost_payment_record_index != record.first_discard_cost_payment_record_index ||
                placement.discard_cost_payment_record_count != record.discard_cost_payment_record_count ||
                placement.discard_cost_payment_hash != record.discard_cost_payment_hash) {
                add_error(out, "paid_action_declaration_record.discard_payment_receipt_mismatch", prefix + " linked StackPlacementRecord discard-cost payment receipt range differs from declaration");
            }
            if (placement.first_tap_cost_payment_record_index != record.first_tap_cost_payment_record_index ||
                placement.tap_cost_payment_record_count != record.tap_cost_payment_record_count ||
                placement.tap_cost_payment_hash != record.tap_cost_payment_hash) {
                add_error(out, "paid_action_declaration_record.tap_payment_receipt_mismatch", prefix + " linked StackPlacementRecord tap-cost payment receipt range differs from declaration");
            }
            if (placement.first_life_cost_payment_record_index != record.first_life_cost_payment_record_index ||
                placement.life_cost_payment_record_count != record.life_cost_payment_record_count ||
                placement.life_cost_payment_hash != record.life_cost_payment_hash) {
                add_error(out, "paid_action_declaration_record.life_payment_receipt_mismatch", prefix + " linked StackPlacementRecord life-cost payment receipt range differs from declaration");
            }
            if (placement.first_loyalty_cost_payment_record_index != record.first_loyalty_cost_payment_record_index ||
                placement.loyalty_cost_payment_record_count != record.loyalty_cost_payment_record_count ||
                placement.loyalty_cost_payment_hash != record.loyalty_cost_payment_hash) {
                add_error(out, "paid_action_declaration_record.loyalty_payment_receipt_mismatch", prefix + " linked StackPlacementRecord loyalty-cost payment receipt range differs from declaration");
            }
        }
    }

    u64 last_counter_change_sequence = 0;
    for (std::size_t i = 0; i < game.counter_change_records.size(); ++i) {
        const auto& record = game.counter_change_records[i];
        const std::string prefix = "counter_change_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "counter_change_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "counter_change_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_counter_change_sequence != 0U && record.sequence <= last_counter_change_sequence) {
            add_error(out, "counter_change_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_counter_change_sequence = record.sequence;
        if (i + 1U < counter_change_event_links.size() && counter_change_event_links[i + 1U] != 1U) {
            add_error(out, "counter_change_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(counter_change_event_links[i + 1U]));
        }
        if (record.kind == CounterChangeKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(CounterChangeKind::Count)) {
            add_error(out, "counter_change_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (record.counter_kind == CounterKind::Count || static_cast<u8>(record.counter_kind) >= static_cast<u8>(CounterKind::Count)) {
            add_error(out, "counter_change_record.invalid_counter_kind", prefix + " has invalid counter kind=" + std::string(to_string(record.counter_kind)));
        }
        if (record.amount == 0U) {
            add_error(out, "counter_change_record.zero_amount", prefix + " records a zero counter delta");
        }
        if (record.source.valid()) {
            if (!is_valid_object_ref(game, record.source)) {
                add_error(out, "counter_change_record.invalid_source", prefix + " source=" + object_ref(record.source));
            }
            if (record.source_zone_change_index == 0U) {
                add_error(out, "counter_change_record.missing_source_zone_change_index", prefix + " source has no zone-change snapshot");
            }
        } else if (record.source_zone_change_index != 0U) {
            add_error(out, "counter_change_record.source_zone_change_without_source", prefix + " has source zone-change metadata without a source");
        }
        if (record.zone_change_record_index != 0U) {
            if (record.zone_change_record_index > game.zone_change_records.size()) {
                add_error(out, "counter_change_record.invalid_zone_change_link", prefix + " links invalid zone_change_record_index=" + std::to_string(record.zone_change_record_index));
            } else {
                const auto& zone_record = game.zone_change_records[record.zone_change_record_index - 1U];
                if (zone_record.object != record.object) {
                    add_error(out, "counter_change_record.zone_change_object_mismatch", prefix + " linked ZoneChangeRecord belongs to a different object");
                }
            }
            if (!record.zone_change_cleanup) {
                add_error(out, "counter_change_record.zone_change_link_without_cleanup", prefix + " links a ZoneChangeRecord without marking zone_change_cleanup");
            }
        } else if (record.zone_change_cleanup) {
            add_error(out, "counter_change_record.cleanup_missing_zone_change_link", prefix + " marks zone_change_cleanup without a ZoneChangeRecord link");
        }
        if (record.cost_payment && record.zone_change_cleanup) {
            add_error(out, "counter_change_record.cost_cleanup_overlap", prefix + " cannot be both cost payment and zone-change cleanup");
        }
        if (record.cost_payment && (record.source != record.object || !record.source.valid())) {
            add_error(out, "counter_change_record.cost_source_mismatch", prefix + " cost-payment counter change should identify its source object");
        }
        switch (record.kind) {
            case CounterChangeKind::ObjectAdded:
            case CounterChangeKind::ObjectRemoved:
                if (!is_valid_object_ref(game, record.object)) {
                    add_error(out, "counter_change_record.invalid_object", prefix + " object=" + object_ref(record.object));
                }
                if (!is_valid_player_ref(game, record.player)) {
                    add_error(out, "counter_change_record.invalid_player", prefix + " player=" + player_ref(record.player));
                }
                if (record.object_zone_change_index == 0U) {
                    add_error(out, "counter_change_record.missing_object_zone_change_index", prefix + " object counter change lacks object zone identity");
                }
                if (!counter_kind_is_object_for_validation(record.counter_kind)) {
                    add_error(out, "counter_change_record.nonobject_counter_on_object", prefix + " uses non-object counter kind for an object mutation");
                }
                if (record.kind == CounterChangeKind::ObjectAdded && record.count_before + record.amount != record.count_after) {
                    add_error(out, "counter_change_record.object_add_delta_mismatch", prefix + " added counter delta does not match before/after counts");
                }
                if (record.kind == CounterChangeKind::ObjectRemoved && record.count_before != record.count_after + record.amount) {
                    add_error(out, "counter_change_record.object_remove_delta_mismatch", prefix + " removed counter delta does not match before/after counts");
                }
                if (record.zone_change_cleanup) {
                    if (record.kind != CounterChangeKind::ObjectRemoved || record.count_after != 0U) {
                        add_error(out, "counter_change_record.cleanup_not_full_removal", prefix + " zone-change cleanup should remove all counters of that kind");
                    }
                    if (record.source.valid() || record.source_zone_change_index != 0U || record.damage_result || record.cost_payment) {
                        add_error(out, "counter_change_record.cleanup_has_cause_payload", prefix + " zone-change cleanup should not carry source, damage, or cost payloads");
                    }
                }
                break;
            case CounterChangeKind::PlayerAdded:
                if (record.object.valid() || record.object_zone_change_index != 0U) {
                    add_error(out, "counter_change_record.player_change_has_object", prefix + " player counter change should not carry object identity");
                }
                if (!is_valid_player_ref(game, record.player)) {
                    add_error(out, "counter_change_record.invalid_player", prefix + " player=" + player_ref(record.player));
                }
                if (record.counter_kind != CounterKind::Poison) {
                    add_error(out, "counter_change_record.unsupported_player_counter", prefix + " uses a non-poison counter on a player");
                }
                if (record.count_before + record.amount != record.count_after) {
                    add_error(out, "counter_change_record.player_add_delta_mismatch", prefix + " added player-counter delta does not match before/after counts");
                }
                if (record.damage_result) {
                    add_error(out, "counter_change_record.player_damage_result", prefix + " player counter change unexpectedly marks damage_result");
                }
                if (record.cost_payment || record.zone_change_cleanup || record.zone_change_record_index != 0U) {
                    add_error(out, "counter_change_record.player_unexpected_cause_payload", prefix + " player counter changes should not carry cost or zone-cleanup payloads");
                }
                break;
            case CounterChangeKind::Count:
                break;
        }
    }


    u64 last_combat_declaration_sequence = 0;
    for (std::size_t i = 0; i < game.combat_declaration_records.size(); ++i) {
        const auto& record = game.combat_declaration_records[i];
        const std::string prefix = "combat_declaration_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "combat_declaration_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "combat_declaration_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_combat_declaration_sequence != 0U && record.sequence <= last_combat_declaration_sequence) {
            add_error(out, "combat_declaration_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_combat_declaration_sequence = record.sequence;
        if (i + 1U < combat_declaration_event_links.size() && combat_declaration_event_links[i + 1U] != 1U) {
            add_error(out, "combat_declaration_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(combat_declaration_event_links[i + 1U]));
        }
        if (record.kind == CombatDeclarationKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(CombatDeclarationKind::Count)) {
            add_error(out, "combat_declaration_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (!is_valid_object_ref(game, record.actor)) {
            add_error(out, "combat_declaration_record.invalid_actor", prefix + " actor=" + object_ref(record.actor));
        }
        if (!is_valid_player_ref(game, record.controller)) {
            add_error(out, "combat_declaration_record.invalid_controller", prefix + " controller=" + player_ref(record.controller));
        }
        if (record.actor_zone_change_index == 0U) {
            add_error(out, "combat_declaration_record.missing_actor_zone_change_index", prefix + " missing actor zone-change snapshot");
        }
        if (!is_valid_player_ref(game, record.defending_player)) {
            add_error(out, "combat_declaration_record.invalid_defending_player", prefix + " defending_player=" + player_ref(record.defending_player));
        }
        switch (record.target.kind) {
            case TargetKind::Player:
                if (!is_valid_player_ref(game, record.target.player)) {
                    add_error(out, "combat_declaration_record.invalid_target_player", prefix + " target=" + player_ref(record.target.player));
                }
                if (record.target_zone_change_index != 0U) {
                    add_error(out, "combat_declaration_record.player_target_zone_change_index", prefix + " player target unexpectedly has object zone-change metadata");
                }
                break;
            case TargetKind::Object:
                if (!is_valid_object_ref(game, record.target.object)) {
                    add_error(out, "combat_declaration_record.invalid_target_object", prefix + " target=" + object_ref(record.target.object));
                }
                if (record.target_zone_change_index == 0U) {
                    add_error(out, "combat_declaration_record.missing_target_zone_change_index", prefix + " object target missing zone-change snapshot");
                }
                if (record.target.object_zone_change_index != record.target_zone_change_index) {
                    add_error(out, "combat_declaration_record.target_zone_change_index_mismatch", prefix + " target ref and record disagree on object zone-change snapshot");
                }
                break;
            case TargetKind::None:
                add_error(out, "combat_declaration_record.missing_target", prefix + " has no target");
                break;
        }

        if (record.kind == CombatDeclarationKind::Attacker) {
            if (record.attacker != record.actor || !is_valid_object_ref(game, record.attacker)) {
                add_error(out, "combat_declaration_record.attacker_actor_mismatch", prefix + " attacker should equal actor for attacker declarations");
            }
            if (record.blocker.valid()) {
                add_error(out, "combat_declaration_record.attacker_has_blocker", prefix + " attacker declaration unexpectedly stores a blocker");
            }
            if (record.attacker_zone_change_index == 0U || record.attacker_zone_change_index != record.actor_zone_change_index) {
                add_error(out, "combat_declaration_record.attacker_zone_change_mismatch", prefix + " attacker zone-change snapshot should match actor");
            }
            if (record.blocker_zone_change_index != 0U) {
                add_error(out, "combat_declaration_record.attacker_blocker_zone_change_index", prefix + " attacker declaration unexpectedly stores blocker zone-change metadata");
            }
            if (record.blocker_batch_size != 0U || record.final_blocker_count_for_attacker != 0U || record.menace_satisfied) {
                add_error(out, "combat_declaration_record.attacker_blocker_context", prefix + " attacker declaration should not carry blocker batch metadata");
            }
            if (record.target.kind == TargetKind::Player) {
                if (!record.target_is_player || record.attacked_object.valid() || record.target_is_planeswalker || record.target_is_battle) {
                    add_error(out, "combat_declaration_record.attacker_player_target_flags", prefix + " player attack has inconsistent target flags");
                }
            } else if (record.target.kind == TargetKind::Object) {
                if (record.target_is_player || record.attacked_object != record.target.object) {
                    add_error(out, "combat_declaration_record.attacker_object_target_flags", prefix + " object attack has inconsistent target identity");
                }
                if (record.target_is_planeswalker == record.target_is_battle) {
                    add_error(out, "combat_declaration_record.attacker_object_target_type", prefix + " object attack should identify exactly one planeswalker/battle target kind");
                }
            }
            if (record.vigilance) {
                if (record.tapped_after != record.tapped_before) {
                    add_error(out, "combat_declaration_record.vigilance_tap_mismatch", prefix + " vigilance attacker changed tapped state");
                }
            } else if (!record.tapped_after) {
                add_error(out, "combat_declaration_record.nonvigilance_not_tapped", prefix + " non-vigilance attacker was not tapped by declaration");
            }
        } else if (record.kind == CombatDeclarationKind::Blocker) {
            if (record.blocker != record.actor || !is_valid_object_ref(game, record.blocker)) {
                add_error(out, "combat_declaration_record.blocker_actor_mismatch", prefix + " blocker should equal actor for blocker declarations");
            }
            if (record.target.kind != TargetKind::Object || record.attacker != record.target.object || !is_valid_object_ref(game, record.attacker)) {
                add_error(out, "combat_declaration_record.blocker_target_mismatch", prefix + " blocker declaration should target the blocked attacker object");
            }
            if (record.blocker_zone_change_index == 0U || record.blocker_zone_change_index != record.actor_zone_change_index) {
                add_error(out, "combat_declaration_record.blocker_zone_change_mismatch", prefix + " blocker zone-change snapshot should match actor");
            }
            if (record.attacker_zone_change_index == 0U || record.attacker_zone_change_index != record.target_zone_change_index) {
                add_error(out, "combat_declaration_record.blocker_attacker_zone_change_mismatch", prefix + " attacker target snapshot should match target zone-change metadata");
            }
            if (record.target_is_player || record.target_is_planeswalker || record.target_is_battle || record.attacked_object.valid()) {
                add_error(out, "combat_declaration_record.blocker_target_flags", prefix + " blocker declaration should not carry attack-target flags");
            }
            if (record.tapped_after != record.tapped_before) {
                add_error(out, "combat_declaration_record.blocker_tap_changed", prefix + " blockers should not tap as part of declaration in this scaffold");
            }
            if (record.blocker_batch_size == 0U || record.final_blocker_count_for_attacker == 0U) {
                add_error(out, "combat_declaration_record.blocker_count_missing", prefix + " blocker declaration missing batch/final blocker counts");
            }
            if (!record.attacker_marked_blocked_after) {
                add_error(out, "combat_declaration_record.attacker_not_marked_blocked", prefix + " blocker declaration did not snapshot attacker as blocked");
            }
            if (record.attacker_had_flying && !record.blocker_had_flying && !record.blocker_had_reach) {
                add_error(out, "combat_declaration_record.illegal_flying_block_snapshot", prefix + " flying attacker was blocked without flying or reach snapshot");
            }
            if (record.attacker_had_menace && (!record.menace_satisfied || record.final_blocker_count_for_attacker < 2U)) {
                add_error(out, "combat_declaration_record.menace_not_satisfied", prefix + " menace attacker did not have enough blockers in the recorded batch");
            }
        }
    }

    u64 last_combat_damage_assignment_sequence = 0;
    for (std::size_t i = 0; i < game.combat_damage_assignment_records.size(); ++i) {
        const auto& record = game.combat_damage_assignment_records[i];
        const std::string prefix = "combat_damage_assignment_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "combat_damage_assignment_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "combat_damage_assignment_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_combat_damage_assignment_sequence != 0U && record.sequence <= last_combat_damage_assignment_sequence) {
            add_error(out, "combat_damage_assignment_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_combat_damage_assignment_sequence = record.sequence;
        if (i + 1U < combat_damage_assignment_event_links.size() && combat_damage_assignment_event_links[i + 1U] != 1U) {
            add_error(out, "combat_damage_assignment_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(combat_damage_assignment_event_links[i + 1U]));
        }
        if (!is_valid_object_ref(game, record.source)) {
            add_error(out, "combat_damage_assignment_record.invalid_source", prefix + " source=" + object_ref(record.source));
        }
        if (!is_valid_player_ref(game, record.source_controller)) {
            add_error(out, "combat_damage_assignment_record.invalid_source_controller", prefix + " source_controller=" + player_ref(record.source_controller));
        }
        if (record.source_zone_change_index == 0U) {
            add_error(out, "combat_damage_assignment_record.missing_source_zone_change_index", prefix + " missing source zone-change snapshot");
        }
        if (record.assigned == 0U) {
            add_error(out, "combat_damage_assignment_record.zero_assigned", prefix + " assigned zero damage");
        }
        switch (record.target.kind) {
            case TargetKind::Player:
                if (!is_valid_player_ref(game, record.target.player)) {
                    add_error(out, "combat_damage_assignment_record.invalid_target_player", prefix + " target=" + player_ref(record.target.player));
                }
                if (record.target_zone_change_index != 0U) {
                    add_error(out, "combat_damage_assignment_record.player_target_zone_change_index", prefix + " player target unexpectedly has object zone-change metadata");
                }
                break;
            case TargetKind::Object:
                if (!is_valid_object_ref(game, record.target.object)) {
                    add_error(out, "combat_damage_assignment_record.invalid_target_object", prefix + " target=" + object_ref(record.target.object));
                }
                if (record.target_zone_change_index == 0U) {
                    add_error(out, "combat_damage_assignment_record.missing_target_zone_change_index", prefix + " object target missing zone-change snapshot");
                }
                if (record.target.object_zone_change_index != record.target_zone_change_index) {
                    add_error(out, "combat_damage_assignment_record.target_zone_change_index_mismatch", prefix + " target ref and record disagree on object zone-change snapshot");
                }
                break;
            case TargetKind::None:
                add_error(out, "combat_damage_assignment_record.missing_target", prefix + " has no target");
                break;
        }
        if (record.damage_record_index == 0U || record.damage_record_index > game.damage_records.size()) {
            add_error(out, "combat_damage_assignment_record.invalid_damage_link", prefix + " links invalid damage_record_index=" + std::to_string(record.damage_record_index));
        } else {
            const auto& damage_record = game.damage_records[record.damage_record_index - 1U];
            if (damage_record.source != record.source) {
                add_error(out, "combat_damage_assignment_record.damage_source_mismatch", prefix + " linked DamageRecord has a different source");
            }
            if (!(damage_record.target == record.target)) {
                add_error(out, "combat_damage_assignment_record.damage_target_mismatch", prefix + " linked DamageRecord has a different target");
            }
            if (damage_record.amount != record.assigned) {
                add_error(out, "combat_damage_assignment_record.damage_amount_mismatch", prefix + " assigned amount disagrees with linked DamageRecord amount");
            }
            if (damage_record.sequence >= record.sequence) {
                add_error(out, "combat_damage_assignment_record.damage_sequence_mismatch", prefix + " linked DamageRecord was not emitted before the assignment record");
            }
        }
        if (record.source_was_attacker == record.source_was_blocker) {
            add_error(out, "combat_damage_assignment_record.source_role_mismatch", prefix + " must mark exactly one of source_was_attacker/source_was_blocker");
        }
        if (record.source_was_blocker) {
            if (record.target.kind != TargetKind::Object) {
                add_error(out, "combat_damage_assignment_record.blocker_target_not_object", prefix + " blocker combat damage should target the blocked attacker object");
            }
            if (record.source_had_trample || record.excess_trample) {
                add_error(out, "combat_damage_assignment_record.blocker_trample_flags", prefix + " blocker assignment should not carry attacker trample flags in this scaffold");
            }
            if (record.blocker_count == 0U) {
                add_error(out, "combat_damage_assignment_record.blocker_count_missing", prefix + " blocker-source assignment should snapshot blocker_count>0");
            }
        }
        if (record.excess_trample && (!record.source_was_attacker || !record.source_had_trample)) {
            add_error(out, "combat_damage_assignment_record.excess_without_trample", prefix + " excess trample assignment lacks attacker/trample flags");
        }
        if (record.attacker_was_blocked && record.blocker_count == 0U && !record.excess_trample) {
            add_error(out, "combat_damage_assignment_record.blocked_without_blocker_context", prefix + " blocked attacker assignment lacks blocker context or excess-trample routing");
        }
    }

    u64 last_stack_placement_sequence = 0;
    for (std::size_t i = 0; i < game.stack_placement_records.size(); ++i) {
        const auto& record = game.stack_placement_records[i];
        const std::string prefix = "stack_placement_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "stack_placement_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "stack_placement_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_stack_placement_sequence != 0U && record.sequence <= last_stack_placement_sequence) {
            add_error(out, "stack_placement_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_stack_placement_sequence = record.sequence;
        if (i + 1U < stack_placement_event_links.size() && stack_placement_event_links[i + 1U] != 1U) {
            add_error(out, "stack_placement_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(stack_placement_event_links[i + 1U]));
        }
        if (record.kind == StackPlacementKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(StackPlacementKind::Count)) {
            add_error(out, "stack_placement_record.invalid_kind", prefix + " has invalid kind=" + std::string(to_string(record.kind)));
        }
        if (!is_valid_object_ref(game, record.source_object)) {
            add_error(out, "stack_placement_record.invalid_source_object", prefix + " source_object=" + object_ref(record.source_object));
        }
        if (!is_valid_object_ref(game, record.stack_object)) {
            add_error(out, "stack_placement_record.invalid_stack_object", prefix + " stack_object=" + object_ref(record.stack_object));
        }
        if (!is_valid_player_ref(game, record.controller)) {
            add_error(out, "stack_placement_record.invalid_controller", prefix + " controller=" + player_ref(record.controller));
        }
        if (!is_valid_zone_ref(record.source_zone_before)) {
            add_error(out, "stack_placement_record.invalid_source_zone", prefix + " source_zone_before is invalid");
        }
        if (record.source_zone_change_index_before == 0U) {
            add_error(out, "stack_placement_record.missing_source_zone_change_index", prefix + " missing source zone-change snapshot");
        }
        if (record.stack_zone_change_index == 0U) {
            add_error(out, "stack_placement_record.missing_stack_zone_change_index", prefix + " missing stack-object zone-change snapshot");
        }
        if (record.stack_size_after != record.stack_size_before + 1U) {
            add_error(out, "stack_placement_record.stack_size_mismatch", prefix + " stack_size_after should be stack_size_before+1");
        }
        if (record.priority_after != record.controller) {
            add_error(out, "stack_placement_record.priority_after_not_controller", prefix + " priority_after does not remain with the acting controller");
        }
        validate_target_definition(out, "stack_placement_record", prefix, record.target_mask, record.target_count);
        if (record.target_choice != !record.chosen_targets.empty()) {
            add_error(out, "stack_placement_record.target_choice_mismatch", prefix + " target_choice flag disagrees with chosen target list");
        }
        if (record.chosen_targets.size() > record.target_count && record.target_count != 0U) {
            add_error(out, "stack_placement_record.too_many_targets", prefix + " chose more targets than target_count");
        }
        for (const auto target : record.chosen_targets) {
            if (target.kind == TargetKind::Player && !is_valid_player_ref(game, target.player)) {
                add_error(out, "stack_placement_record.invalid_target_player", prefix + " contains " + target_ref(target));
            } else if (target.kind == TargetKind::Object && !is_valid_object_ref(game, target.object)) {
                add_error(out, "stack_placement_record.invalid_target_object", prefix + " contains " + target_ref(target));
            } else if (target.kind == TargetKind::None) {
                add_error(out, "stack_placement_record.empty_target", prefix + " contains target:none");
            }
        }

        const bool stack_placement_has_paid_shape = record.mana_cost_paid || record.tap_cost_paid ||
            record.sacrifice_cost_paid || record.discard_cost_paid || record.loyalty_cost_paid ||
            record.modal_choice || record.target_choice;
        if (stack_placement_has_paid_shape && !record.paid_action_phase_recorded) {
            add_error(out, "stack_placement_record.paid_phase_missing", prefix + " has paid/choice shape but no paid-action phase evidence");
        }
        if (record.paid_action_phase_recorded) {
            if (record.paid_action_declaration_record_index == 0U) {
                add_error(out, "stack_placement_record.missing_paid_action_declaration_record", prefix + " paid placement lacks a typed declaration/cost-lock record");
            } else if (record.paid_action_declaration_record_index > game.paid_action_declaration_records.size()) {
                add_error(out, "stack_placement_record.invalid_paid_action_declaration_record", prefix + " links invalid paid_action_declaration_record_index=" + std::to_string(record.paid_action_declaration_record_index));
            } else {
                const auto& declaration = game.paid_action_declaration_records[record.paid_action_declaration_record_index - 1U];
                if (declaration.stack_placement_record_index != i + 1U) {
                    add_error(out, "stack_placement_record.paid_action_declaration_backlink_mismatch", prefix + " linked declaration does not point back to this placement");
                }
                if (record.paid_action_declaration_hash == 0U || record.paid_action_declaration_hash != declaration.declaration_hash) {
                    add_error(out, "stack_placement_record.paid_action_declaration_hash_mismatch", prefix + " declaration hash does not match linked declaration");
                }
                if (declaration.sequence <= record.stack_object_entered_sequence || declaration.sequence >= record.sequence) {
                    add_error(out, "stack_placement_record.paid_action_declaration_sequence_outside_window", prefix + " declaration is not between stack entry and placement");
                }
                const ActionKind expected_action_kind = record.kind == StackPlacementKind::SpellCast
                    ? ActionKind::CastSpellFromHandPaid
                    : (record.kind == StackPlacementKind::ActivatedAbility ? ActionKind::ActivateActivatedAbility : ActionKind::ActivateLoyaltyAbility);
                if (declaration.action_kind != expected_action_kind || declaration.source_object != record.source_object ||
                    declaration.stack_object != record.stack_object || declaration.player != record.controller) {
                    add_error(out, "stack_placement_record.paid_action_declaration_identity_mismatch", prefix + " linked declaration identity does not match this placement");
                }
            }
        }
        if (!record.paid_action_phase_recorded) {
            if (record.stack_object_on_stack_before_costs || record.choices_locked_before_costs ||
                record.paid_action_events_before_stack_placement || record.stack_object_entered_sequence != 0U ||
                record.choices_locked_sequence != 0U || record.first_paid_action_event_sequence != 0U ||
                record.last_paid_action_event_sequence != 0U || record.first_mana_payment_plan_record_index != 0U ||
                record.mana_payment_plan_record_count != 0U || record.first_mana_change_record_index != 0U ||
                record.mana_change_record_count != 0U || record.first_paid_action_counter_change_record_index != 0U ||
                record.paid_action_counter_change_record_count != 0U || record.first_paid_action_zone_change_record_index != 0U ||
                record.paid_action_zone_change_record_count != 0U || record.first_choice_event_sequence != 0U ||
                record.last_choice_event_sequence != 0U || record.choice_event_count != 0U ||
                record.mode_choice_event_sequence != 0U || record.target_choice_event_sequence != 0U ||
                record.first_sacrifice_cost_zone_change_record_index != 0U ||
                record.sacrifice_cost_zone_change_record_count != 0U || record.sacrifice_cost_event_sequence != 0U ||
                record.first_sacrifice_cost_payment_record_index != 0U ||
                record.sacrifice_cost_payment_record_count != 0U || record.sacrifice_cost_payment_hash != 0U ||
                record.first_discard_cost_record_index != 0U || record.discard_cost_record_count != 0U ||
                record.first_discard_cost_zone_change_record_index != 0U ||
                record.discard_cost_zone_change_record_count != 0U || record.discard_cost_event_sequence != 0U ||
                record.first_discard_cost_payment_record_index != 0U ||
                record.discard_cost_payment_record_count != 0U || record.discard_cost_payment_hash != 0U ||
                record.tap_cost_event_sequence != 0U || record.paid_action_declaration_record_index != 0U ||
                record.paid_action_declaration_hash != 0U) {
                add_error(out, "stack_placement_record.paid_phase_fields_without_flag", prefix + " carries paid-action phase fields without the phase flag");
            }
        } else {
            auto sequence_exists = [&](u64 sequence) {
                return std::any_of(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                    return event_record.sequence == sequence;
                });
            };
            auto validate_range = [&](u32 first, u32 count, std::size_t total, std::string code, std::string label) {
                if (count == 0U) {
                    if (first != 0U) {
                        add_error(out, std::move(code), prefix + " has first " + label + " index without a count");
                    }
                    return false;
                }
                if (first == 0U) {
                    add_error(out, std::move(code), prefix + " has " + label + " count without first index");
                    return false;
                }
                const u64 last = static_cast<u64>(first) + static_cast<u64>(count) - 1U;
                if (last > total) {
                    add_error(out, std::move(code), prefix + " has " + label + " range outside journal vector");
                    return false;
                }
                return true;
            };

            if (record.stack_object_entered_sequence == 0U) {
                add_error(out, "stack_placement_record.paid_phase_missing_stack_enter_sequence", prefix + " paid phase lacks a stack-object entry sequence");
            } else if (record.stack_object_entered_sequence >= record.sequence) {
                add_error(out, "stack_placement_record.paid_phase_stack_enter_after_placement", prefix + " stack object entry sequence is not before placement");
            }
            if (!record.stack_object_on_stack_before_costs) {
                add_error(out, "stack_placement_record.paid_phase_stack_object_not_on_stack", prefix + " does not prove stack object was on stack before costs");
            }
            if (record.choices_locked_sequence == 0U) {
                add_error(out, "stack_placement_record.paid_phase_missing_choice_lock_sequence", prefix + " paid phase lacks a choice-lock sequence");
            } else if (record.choices_locked_sequence >= record.sequence) {
                add_error(out, "stack_placement_record.paid_phase_choice_lock_after_placement", prefix + " choice-lock sequence is not before placement");
            }
            if (!record.choices_locked_before_costs) {
                add_error(out, "stack_placement_record.paid_phase_choices_not_locked_before_costs", prefix + " does not prove choices were locked before paid-action events");
            }
            if (!record.paid_action_events_before_stack_placement) {
                add_error(out, "stack_placement_record.paid_phase_events_after_placement", prefix + " does not prove paid-action events occurred before placement");
            }
            auto event_for_sequence = [&](u64 sequence) -> const EventRecord* {
                const auto it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                    return event_record.sequence == sequence;
                });
                return it == game.event_records.end() ? nullptr : &(*it);
            };
            auto is_choice_lock_event = [](const EventRecord& event_record) {
                return event_record.kind == EventRecordKind::Log &&
                    (event_record.log_kind == "choose_mode" || event_record.log_kind == "choose_target");
            };
            auto validate_choice_anchor = [&](u64 sequence,
                                             std::string_view expected_kind,
                                             std::string code_prefix) -> const EventRecord* {
                if (sequence == 0U) {
                    return nullptr;
                }
                const EventRecord* anchor = event_for_sequence(sequence);
                if (anchor == nullptr) {
                    add_error(out, code_prefix + "_missing", prefix + " choice anchor sequence does not name an EventRecord");
                    return nullptr;
                }
                if (anchor->kind != EventRecordKind::Log || anchor->log_kind != expected_kind) {
                    add_error(out, code_prefix + "_wrong_kind", prefix + " choice anchor does not name the expected choice log row");
                }
                if (anchor->sequence <= record.stack_object_entered_sequence || anchor->sequence > record.choices_locked_sequence || anchor->sequence >= record.sequence) {
                    add_error(out, code_prefix + "_sequence_outside_lock_window", prefix + " choice anchor is outside the stack-entry/choice-lock window");
                }
                if (record.first_choice_event_sequence != 0U && record.last_choice_event_sequence != 0U &&
                    (anchor->sequence < record.first_choice_event_sequence || anchor->sequence > record.last_choice_event_sequence)) {
                    add_error(out, code_prefix + "_outside_choice_span", prefix + " choice anchor is outside the named choice-event span");
                }
                if (anchor->object != record.stack_object) {
                    add_error(out, code_prefix + "_object_mismatch", prefix + " choice anchor names a different stack object");
                }
                if (anchor->player != record.controller) {
                    add_error(out, code_prefix + "_player_mismatch", prefix + " choice anchor names a different controller");
                }
                return anchor;
            };

            if ((record.first_choice_event_sequence == 0U) != (record.last_choice_event_sequence == 0U)) {
                add_error(out, "stack_placement_record.choice_lock_incomplete_event_span", prefix + " carries only one side of the choice-lock event span");
            }
            if (record.choice_event_count == 0U && (record.first_choice_event_sequence != 0U || record.last_choice_event_sequence != 0U)) {
                add_error(out, "stack_placement_record.choice_lock_span_without_count", prefix + " carries choice-lock event span endpoints without a count");
            }
            if ((record.modal_choice || record.target_choice) && record.choice_event_count == 0U) {
                add_error(out, "stack_placement_record.missing_choice_lock_event_witness", prefix + " has mode/target choices without explicit choice-lock event witnesses");
            }
            if (!record.modal_choice && !record.target_choice && record.choice_event_count != 0U) {
                add_error(out, "stack_placement_record.unexpected_choice_lock_event_witness", prefix + " has choice-lock event witnesses despite no mode/target choice");
            }
            if (record.choice_event_count != 0U) {
                if (record.first_choice_event_sequence == 0U || record.last_choice_event_sequence == 0U) {
                    add_error(out, "stack_placement_record.choice_lock_count_without_span", prefix + " carries a choice-lock count without both span endpoints");
                } else {
                    if (record.first_choice_event_sequence > record.last_choice_event_sequence) {
                        add_error(out, "stack_placement_record.choice_lock_event_span_reversed", prefix + " choice-lock event span is reversed");
                    }
                    if (record.first_choice_event_sequence <= record.stack_object_entered_sequence) {
                        add_error(out, "stack_placement_record.choice_lock_event_before_stack_entry", prefix + " choice-lock event span starts before stack entry");
                    }
                    if (record.last_choice_event_sequence > record.choices_locked_sequence) {
                        add_error(out, "stack_placement_record.choice_lock_event_after_choice_lock", prefix + " choice-lock event span extends after the sealed choice-lock sequence");
                    }
                    if (record.last_choice_event_sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.choice_lock_event_not_before_placement", prefix + " choice-lock event span reaches placement sequence");
                    }
                    const EventRecord* first_choice = event_for_sequence(record.first_choice_event_sequence);
                    const EventRecord* last_choice = event_for_sequence(record.last_choice_event_sequence);
                    if (first_choice == nullptr || last_choice == nullptr) {
                        add_error(out, "stack_placement_record.choice_lock_event_sequence_missing", prefix + " choice-lock event span names a missing EventRecord sequence");
                    } else if (!is_choice_lock_event(*first_choice) || !is_choice_lock_event(*last_choice)) {
                        add_error(out, "stack_placement_record.choice_lock_event_span_endpoint_not_choice", prefix + " choice-lock event span endpoints must name choose_mode/choose_target rows");
                    }
                    u32 observed_choice_events = 0U;
                    bool saw_mode_choice = false;
                    bool saw_target_choice = false;
                    for (const auto& event_record : game.event_records) {
                        if (event_record.sequence < record.first_choice_event_sequence || event_record.sequence > record.last_choice_event_sequence ||
                            !is_choice_lock_event(event_record)) {
                            continue;
                        }
                        ++observed_choice_events;
                        saw_mode_choice = saw_mode_choice || event_record.log_kind == "choose_mode";
                        saw_target_choice = saw_target_choice || event_record.log_kind == "choose_target";
                        if (event_record.log_kind == "choose_mode" && event_record.choice_mode_index == 0U) {
                            add_error(out, "stack_placement_record.choice_lock_mode_event_missing_index", prefix + " choose_mode witness lacks a selected mode index payload");
                        }
                        if (event_record.log_kind == "choose_mode" && event_record.choice_mode_contract_hash == 0U) {
                            add_error(out, "stack_placement_record.choice_lock_mode_event_missing_contract_hash", prefix + " choose_mode witness lacks a selected-mode contract hash payload");
                        }
                        if (event_record.log_kind == "choose_target" && event_record.choice_target_count == 0U) {
                            add_error(out, "stack_placement_record.choice_lock_target_event_missing_count", prefix + " choose_target witness lacks a chosen-target count payload");
                        }
                        if (event_record.log_kind == "choose_target" && event_record.choice_target_set_hash == 0U) {
                            add_error(out, "stack_placement_record.choice_lock_target_event_missing_set_hash", prefix + " choose_target witness lacks an ordered target-set hash payload");
                        }
                        if (event_record.sequence <= record.stack_object_entered_sequence || event_record.sequence > record.choices_locked_sequence) {
                            add_error(out, "stack_placement_record.choice_lock_event_sequence_outside_lock_window", prefix + " choice-lock event is outside stack-entry/choice-lock window");
                        }
                        if (event_record.object != record.stack_object) {
                            add_error(out, "stack_placement_record.choice_lock_event_object_mismatch", prefix + " choice-lock event names a different stack object");
                        }
                        if (event_record.player != record.controller) {
                            add_error(out, "stack_placement_record.choice_lock_event_player_mismatch", prefix + " choice-lock event names a different controller");
                        }
                    }
                    if (observed_choice_events != record.choice_event_count) {
                        add_error(out, "stack_placement_record.choice_lock_event_count_mismatch", prefix + " choice-lock event count does not match the named span");
                    }
                    if (record.modal_choice && !saw_mode_choice) {
                        add_error(out, "stack_placement_record.choice_lock_missing_mode_event", prefix + " modal choice lacks a choose_mode witness");
                    }
                    if (!record.modal_choice && saw_mode_choice) {
                        add_error(out, "stack_placement_record.choice_lock_unexpected_mode_event", prefix + " nonmodal placement has a choose_mode witness");
                    }
                    if (record.target_choice && !saw_target_choice) {
                        add_error(out, "stack_placement_record.choice_lock_missing_target_event", prefix + " target choice lacks a choose_target witness");
                    }
                    if (!record.target_choice && saw_target_choice) {
                        add_error(out, "stack_placement_record.choice_lock_unexpected_target_event", prefix + " untargeted placement has a choose_target witness");
                    }
                }
            }

            if (record.modal_choice && record.mode_choice_event_sequence == 0U) {
                add_error(out, "stack_placement_record.missing_mode_choice_event_anchor", prefix + " modal choice lacks a named choose_mode event anchor");
            }
            if (!record.modal_choice && record.mode_choice_event_sequence != 0U) {
                add_error(out, "stack_placement_record.unexpected_mode_choice_event_anchor", prefix + " nonmodal placement has a named choose_mode event anchor");
            }
            if (record.target_choice && record.target_choice_event_sequence == 0U) {
                add_error(out, "stack_placement_record.missing_target_choice_event_anchor", prefix + " target choice lacks a named choose_target event anchor");
            }
            if (!record.target_choice && record.target_choice_event_sequence != 0U) {
                add_error(out, "stack_placement_record.unexpected_target_choice_event_anchor", prefix + " untargeted placement has a named choose_target event anchor");
            }
            if (record.mode_choice_event_sequence != 0U) {
                const EventRecord* mode_anchor = validate_choice_anchor(record.mode_choice_event_sequence,
                                                                        "choose_mode",
                                                                        "stack_placement_record.mode_choice_event_anchor");
                if (mode_anchor != nullptr && mode_anchor->choice_mode_index != record.chosen_mode_index) {
                    add_error(out, "stack_placement_record.mode_choice_event_index_mismatch", prefix + " choose_mode anchor payload disagrees with chosen_mode_index");
                }
                if (mode_anchor != nullptr && is_valid_object_ref(game, record.stack_object)) {
                    const auto& stack_obj = object(game, record.stack_object);
                    const auto* def = current_definition_for_validation(game, stack_obj);
                    if (def != nullptr && record.chosen_mode_index != 0U && record.chosen_mode_index <= def->modes.size()) {
                        const u64 expected_mode_contract_hash = mode_choice_contract_hash(def->modes[record.chosen_mode_index - 1U]);
                        if (mode_anchor->choice_mode_contract_hash != expected_mode_contract_hash) {
                            add_error(out, "stack_placement_record.mode_choice_event_contract_hash_mismatch", prefix + " choose_mode anchor contract hash disagrees with the selected mode definition");
                        }
                    }
                }
            }
            if (record.target_choice_event_sequence != 0U) {
                const EventRecord* target_anchor = validate_choice_anchor(record.target_choice_event_sequence,
                                                                          "choose_target",
                                                                          "stack_placement_record.target_choice_event_anchor");
                if (target_anchor != nullptr) {
                    if (target_anchor->choice_target_count != record.chosen_targets.size()) {
                        add_error(out, "stack_placement_record.target_choice_event_count_mismatch", prefix + " choose_target anchor target count disagrees with chosen_targets");
                    }
                    if (target_anchor->choice_target_set_hash != target_choice_set_hash(record.chosen_targets)) {
                        add_error(out, "stack_placement_record.target_choice_event_set_hash_mismatch", prefix + " choose_target anchor target-set hash disagrees with chosen_targets");
                    }
                    if (record.chosen_targets.size() == 1U) {
                        if (!same_target_choice_for_validation(target_anchor->target, record.chosen_targets.front())) {
                            add_error(out, "stack_placement_record.target_choice_event_target_mismatch", prefix + " choose_target anchor target disagrees with chosen target");
                        }
                    } else if (target_anchor->target.kind != TargetKind::None) {
                        add_error(out, "stack_placement_record.target_choice_event_unexpected_single_target", prefix + " multi-target choose_target anchor should not carry a single target payload");
                    }
                }
            }

            if ((record.first_paid_action_event_sequence == 0U) != (record.last_paid_action_event_sequence == 0U)) {
                add_error(out, "stack_placement_record.paid_phase_incomplete_event_span", prefix + " carries only one side of the paid-action event span");
            }
            if (record.first_paid_action_event_sequence != 0U) {
                if (record.first_paid_action_event_sequence > record.last_paid_action_event_sequence) {
                    add_error(out, "stack_placement_record.paid_phase_event_span_reversed", prefix + " paid-action event span is reversed");
                }
                if (record.first_paid_action_event_sequence <= record.choices_locked_sequence) {
                    add_error(out, "stack_placement_record.paid_phase_event_before_choice_lock", prefix + " paid-action event span starts before choices were locked");
                }
                if (record.last_paid_action_event_sequence >= record.sequence) {
                    add_error(out, "stack_placement_record.paid_phase_event_not_before_placement", prefix + " paid-action event span reaches placement sequence");
                }
                if (!sequence_exists(record.first_paid_action_event_sequence) || !sequence_exists(record.last_paid_action_event_sequence)) {
                    add_error(out, "stack_placement_record.paid_phase_event_sequence_missing", prefix + " paid-action event span names a missing EventRecord sequence");
                }
            }

            const bool plan_range_ok = validate_range(record.first_mana_payment_plan_record_index,
                                                      record.mana_payment_plan_record_count,
                                                      game.mana_payment_plan_records.size(),
                                                      "stack_placement_record.invalid_paid_phase_mana_plan_range",
                                                      "mana-payment-plan");
            if (plan_range_ok) {
                for (u32 offset = 0; offset < record.mana_payment_plan_record_count; ++offset) {
                    const auto& plan = game.mana_payment_plan_records[record.first_mana_payment_plan_record_index + offset - 1U];
                    if (plan.sequence <= record.choices_locked_sequence || plan.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.paid_phase_mana_plan_sequence_outside_span", prefix + " has a mana-payment plan outside the paid-action sequence window");
                    }
                }
            }
            const bool mana_change_range_ok = validate_range(record.first_mana_change_record_index,
                                                             record.mana_change_record_count,
                                                             game.mana_change_records.size(),
                                                             "stack_placement_record.invalid_paid_phase_mana_change_range",
                                                             "mana-change");
            if (mana_change_range_ok) {
                for (u32 offset = 0; offset < record.mana_change_record_count; ++offset) {
                    const auto& mana_record = game.mana_change_records[record.first_mana_change_record_index + offset - 1U];
                    if (mana_record.sequence <= record.choices_locked_sequence || mana_record.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.paid_phase_mana_change_sequence_outside_span", prefix + " has a mana-change record outside the paid-action sequence window");
                    }
                }
            }
            const bool counter_change_range_ok = validate_range(record.first_paid_action_counter_change_record_index,
                                                                record.paid_action_counter_change_record_count,
                                                                game.counter_change_records.size(),
                                                                "stack_placement_record.invalid_paid_phase_counter_change_range",
                                                                "paid-action counter-change");
            if (counter_change_range_ok) {
                for (u32 offset = 0; offset < record.paid_action_counter_change_record_count; ++offset) {
                    const auto& counter_record = game.counter_change_records[record.first_paid_action_counter_change_record_index + offset - 1U];
                    if (counter_record.sequence <= record.choices_locked_sequence || counter_record.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.paid_phase_counter_change_sequence_outside_span", prefix + " has a counter-change record outside the paid-action sequence window");
                    }
                    if (record.kind == StackPlacementKind::LoyaltyAbility && counter_record.object != record.source_object) {
                        add_error(out, "stack_placement_record.paid_phase_loyalty_counter_source_mismatch", prefix + " has a loyalty cost counter-change for a different object");
                    }
                    if (record.kind == StackPlacementKind::LoyaltyAbility && counter_record.counter_kind != CounterKind::Loyalty) {
                        add_error(out, "stack_placement_record.paid_phase_loyalty_counter_kind_mismatch", prefix + " has a loyalty cost range with a non-loyalty counter change");
                    }
                }
            }
            const bool zone_change_range_ok = validate_range(record.first_paid_action_zone_change_record_index,
                                                             record.paid_action_zone_change_record_count,
                                                             game.zone_change_records.size(),
                                                             "stack_placement_record.invalid_paid_phase_zone_change_range",
                                                             "paid-action zone-change");
            if (zone_change_range_ok) {
                for (u32 offset = 0; offset < record.paid_action_zone_change_record_count; ++offset) {
                    const auto& zone_record = game.zone_change_records[record.first_paid_action_zone_change_record_index + offset - 1U];
                    if (zone_record.sequence <= record.choices_locked_sequence || zone_record.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.paid_phase_zone_change_sequence_outside_span", prefix + " has a zone-change record outside the paid-action sequence window");
                    }
                }
            }
            const bool sacrifice_zone_range_ok = validate_range(record.first_sacrifice_cost_zone_change_record_index,
                                                                record.sacrifice_cost_zone_change_record_count,
                                                                game.zone_change_records.size(),
                                                                "stack_placement_record.invalid_sacrifice_cost_zone_change_range",
                                                                "sacrifice-cost zone-change");
            if (sacrifice_zone_range_ok) {
                for (u32 offset = 0; offset < record.sacrifice_cost_zone_change_record_count; ++offset) {
                    const auto& zone_record = game.zone_change_records[record.first_sacrifice_cost_zone_change_record_index + offset - 1U];
                    if (zone_record.sequence <= record.choices_locked_sequence || zone_record.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.sacrifice_cost_zone_change_sequence_outside_span", prefix + " has a sacrifice-cost zone change outside the paid-action sequence window");
                    }
                    if (zone_record.from_zone != Zone::Battlefield || zone_record.requested_zone != Zone::Graveyard) {
                        add_error(out, "stack_placement_record.sacrifice_cost_zone_change_shape_mismatch", prefix + " sacrifice-cost witness does not request movement from battlefield to graveyard");
                    }
                    if (zone_record.was_ability_object) {
                        add_error(out, "stack_placement_record.sacrifice_cost_zone_change_ability_object", prefix + " sacrifice-cost witness points at a synthetic ability object");
                    }
                }
            }
            const bool sacrifice_payment_range_ok = validate_range(record.first_sacrifice_cost_payment_record_index,
                                                                   record.sacrifice_cost_payment_record_count,
                                                                   game.sacrifice_cost_payment_records.size(),
                                                                   "stack_placement_record.invalid_sacrifice_cost_payment_record_range",
                                                                   "sacrifice-cost payment");
            if (sacrifice_payment_range_ok) {
                for (u32 offset = 0; offset < record.sacrifice_cost_payment_record_count; ++offset) {
                    const auto& payment = game.sacrifice_cost_payment_records[record.first_sacrifice_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.sacrifice_cost_payment_sequence_outside_span", prefix + " has a sacrifice-cost payment receipt outside the paid-action window");
                    }
                    if (payment.payer != record.controller) {
                        add_error(out, "stack_placement_record.sacrifice_cost_payment_payer_mismatch", prefix + " linked sacrifice-cost payment has a different payer");
                    }
                    if (payment.source_object.valid() && payment.source_object != record.source_object) {
                        add_error(out, "stack_placement_record.sacrifice_cost_payment_source_mismatch", prefix + " linked sacrifice-cost payment has a different source object");
                    }
                    if (record.sacrifice_cost_payment_record_count == 1U && payment.payment_hash != record.sacrifice_cost_payment_hash) {
                        add_error(out, "stack_placement_record.sacrifice_cost_payment_hash_mismatch", prefix + " sacrifice-cost payment hash does not match the linked receipt");
                    }
                    if (record.sacrifice_cost_zone_change_record_count != 0U &&
                        (payment.first_zone_change_record_index != record.first_sacrifice_cost_zone_change_record_index ||
                         payment.zone_change_record_count != record.sacrifice_cost_zone_change_record_count)) {
                        add_error(out, "stack_placement_record.sacrifice_cost_payment_zone_range_mismatch", prefix + " linked sacrifice-cost payment names a different exact sacrifice zone-change range");
                    }
                    if (record.sacrifice_cost_event_sequence != 0U && payment.sequence != record.sacrifice_cost_event_sequence) {
                        add_error(out, "stack_placement_record.sacrifice_cost_payment_event_mismatch", prefix + " linked sacrifice-cost payment sequence differs from the payment event witness");
                    }
                }
            }

            const bool discard_record_range_ok = validate_range(record.first_discard_cost_record_index,
                                                                record.discard_cost_record_count,
                                                                game.discard_records.size(),
                                                                "stack_placement_record.invalid_discard_cost_record_range",
                                                                "discard-cost discard-record");
            if (discard_record_range_ok) {
                for (u32 offset = 0; offset < record.discard_cost_record_count; ++offset) {
                    const auto& discard_record = game.discard_records[record.first_discard_cost_record_index + offset - 1U];
                    if (discard_record.sequence <= record.choices_locked_sequence || discard_record.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.discard_cost_record_sequence_outside_span", prefix + " has a discard-cost discard row outside the paid-action sequence window");
                    }
                    if (discard_record.kind != DiscardRecordKind::CostPayment || !discard_record.cost_payment) {
                        add_error(out, "stack_placement_record.discard_cost_record_not_cost_payment", prefix + " discard-cost witness is not marked as a cost-payment discard");
                    }
                    if (discard_record.player != record.controller) {
                        add_error(out, "stack_placement_record.discard_cost_record_player_mismatch", prefix + " discard-cost witness names a different player");
                    }
                }
            }
            const bool discard_zone_range_ok = validate_range(record.first_discard_cost_zone_change_record_index,
                                                              record.discard_cost_zone_change_record_count,
                                                              game.zone_change_records.size(),
                                                              "stack_placement_record.invalid_discard_cost_zone_change_range",
                                                              "discard-cost zone-change");
            if (discard_zone_range_ok) {
                for (u32 offset = 0; offset < record.discard_cost_zone_change_record_count; ++offset) {
                    const auto& zone_record = game.zone_change_records[record.first_discard_cost_zone_change_record_index + offset - 1U];
                    if (zone_record.sequence <= record.choices_locked_sequence || zone_record.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.discard_cost_zone_change_sequence_outside_span", prefix + " has a discard-cost zone change outside the paid-action sequence window");
                    }
                    if (zone_record.from_zone != Zone::Hand || zone_record.requested_zone != Zone::Graveyard || zone_record.to_zone != Zone::Graveyard) {
                        add_error(out, "stack_placement_record.discard_cost_zone_change_shape_mismatch", prefix + " discard-cost witness does not request movement from hand to graveyard");
                    }
                    if (zone_record.was_ability_object) {
                        add_error(out, "stack_placement_record.discard_cost_zone_change_ability_object", prefix + " discard-cost witness points at a synthetic ability object");
                    }
                }
            }
            const bool discard_payment_range_ok = validate_range(record.first_discard_cost_payment_record_index,
                                                                 record.discard_cost_payment_record_count,
                                                                 game.discard_cost_payment_records.size(),
                                                                 "stack_placement_record.invalid_discard_cost_payment_record_range",
                                                                 "discard-cost payment");
            if (discard_payment_range_ok) {
                for (u32 offset = 0; offset < record.discard_cost_payment_record_count; ++offset) {
                    const auto& payment = game.discard_cost_payment_records[record.first_discard_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.discard_cost_payment_sequence_outside_span", prefix + " has a discard-cost payment receipt outside the paid-action window");
                    }
                    if (payment.payer != record.controller) {
                        add_error(out, "stack_placement_record.discard_cost_payment_payer_mismatch", prefix + " linked discard-cost payment has a different payer");
                    }
                    if (payment.source_object.valid() && payment.source_object != record.source_object) {
                        add_error(out, "stack_placement_record.discard_cost_payment_source_mismatch", prefix + " linked discard-cost payment has a different source object");
                    }
                    if (record.discard_cost_payment_record_count == 1U && payment.payment_hash != record.discard_cost_payment_hash) {
                        add_error(out, "stack_placement_record.discard_cost_payment_hash_mismatch", prefix + " discard-cost payment hash does not match the linked receipt");
                    }
                    if (record.discard_cost_record_count != 0U &&
                        (payment.first_discard_record_index != record.first_discard_cost_record_index ||
                         payment.discard_record_count != record.discard_cost_record_count)) {
                        add_error(out, "stack_placement_record.discard_cost_payment_discard_range_mismatch", prefix + " linked discard-cost payment names a different discard-record range");
                    }
                    if (record.discard_cost_zone_change_record_count != 0U &&
                        (payment.first_zone_change_record_index != record.first_discard_cost_zone_change_record_index ||
                         payment.zone_change_record_count != record.discard_cost_zone_change_record_count)) {
                        add_error(out, "stack_placement_record.discard_cost_payment_zone_range_mismatch", prefix + " linked discard-cost payment names a different exact discard zone-change range");
                    }
                    if (record.discard_cost_event_sequence != 0U && payment.sequence != record.discard_cost_event_sequence) {
                        add_error(out, "stack_placement_record.discard_cost_payment_event_mismatch", prefix + " linked discard-cost payment sequence differs from the payment event witness");
                    }
                }
            }
            const bool tap_payment_range_ok = validate_range(record.first_tap_cost_payment_record_index,
                                                             record.tap_cost_payment_record_count,
                                                             game.tap_cost_payment_records.size(),
                                                             "stack_placement_record.invalid_tap_cost_payment_record_range",
                                                             "tap-cost payment");
            if (tap_payment_range_ok) {
                for (u32 offset = 0; offset < record.tap_cost_payment_record_count; ++offset) {
                    const auto& payment = game.tap_cost_payment_records[record.first_tap_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.tap_cost_payment_sequence_outside_span", prefix + " has a tap-cost payment receipt outside the paid-action window");
                    }
                    if (payment.payer != record.controller) {
                        add_error(out, "stack_placement_record.tap_cost_payment_payer_mismatch", prefix + " linked tap-cost payment has a different payer");
                    }
                    if (payment.source_object != record.source_object) {
                        add_error(out, "stack_placement_record.tap_cost_payment_source_mismatch", prefix + " linked tap-cost payment has a different source object");
                    }
                    if (payment.source_zone_change_index_before != record.source_zone_change_index_before) {
                        add_error(out, "stack_placement_record.tap_cost_payment_zone_snapshot_mismatch", prefix + " linked tap-cost payment names a different source zone-change snapshot");
                    }
                    if (record.tap_cost_payment_record_count == 1U && payment.payment_hash != record.tap_cost_payment_hash) {
                        add_error(out, "stack_placement_record.tap_cost_payment_hash_mismatch", prefix + " tap-cost payment hash does not match the linked receipt");
                    }
                    if (record.tap_cost_event_sequence != 0U && payment.tap_event_sequence != record.tap_cost_event_sequence) {
                        add_error(out, "stack_placement_record.tap_cost_payment_event_mismatch", prefix + " linked tap-cost payment event differs from the tap EventRecord witness");
                    }
                }
            }
            const bool life_payment_range_ok = validate_range(record.first_life_cost_payment_record_index,
                                                              record.life_cost_payment_record_count,
                                                              game.life_cost_payment_records.size(),
                                                              "stack_placement_record.invalid_life_cost_payment_record_range",
                                                              "life-cost payment");
            if (life_payment_range_ok) {
                for (u32 offset = 0; offset < record.life_cost_payment_record_count; ++offset) {
                    const auto& payment = game.life_cost_payment_records[record.first_life_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.life_cost_payment_sequence_outside_span", prefix + " has a life-cost payment receipt outside the paid-action window");
                    }
                    if (payment.payer != record.controller) {
                        add_error(out, "stack_placement_record.life_cost_payment_payer_mismatch", prefix + " linked life-cost payment has a different payer");
                    }
                    if (payment.source_object.valid() && payment.source_object != record.source_object) {
                        add_error(out, "stack_placement_record.life_cost_payment_source_mismatch", prefix + " linked life-cost payment has a different source object");
                    }
                    if (record.life_cost_payment_record_count == 1U && payment.payment_hash != record.life_cost_payment_hash) {
                        add_error(out, "stack_placement_record.life_cost_payment_hash_mismatch", prefix + " life-cost payment hash does not match the linked receipt");
                    }
                    if (record.life_cost_life_change_record_count != 0U &&
                        payment.life_change_record_index != record.first_life_cost_life_change_record_index) {
                        add_error(out, "stack_placement_record.life_cost_payment_life_change_range_mismatch", prefix + " linked life-cost payment names a different life-change witness");
                    }
                    if (record.life_cost_event_sequence != 0U && payment.sequence != record.life_cost_event_sequence) {
                        add_error(out, "stack_placement_record.life_cost_payment_event_mismatch", prefix + " linked life-cost payment sequence differs from the payment event witness");
                    }
                }
            }
            const bool return_zone_range_ok = validate_range(record.first_return_cost_zone_change_record_index,
                                                             record.return_cost_zone_change_record_count,
                                                             game.zone_change_records.size(),
                                                             "stack_placement_record.invalid_return_cost_zone_change_range",
                                                             "return-cost zone-change");
            if (return_zone_range_ok) {
                for (u32 offset = 0; offset < record.return_cost_zone_change_record_count; ++offset) {
                    const auto& zone_record = game.zone_change_records[record.first_return_cost_zone_change_record_index + offset - 1U];
                    if (zone_record.sequence <= record.choices_locked_sequence || zone_record.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.return_cost_zone_change_sequence_outside_span", prefix + " has a return-cost zone change outside the paid-action sequence window");
                    }
                    if (zone_record.from_zone != Zone::Battlefield || zone_record.requested_zone != Zone::Hand || zone_record.to_zone != Zone::Hand) {
                        add_error(out, "stack_placement_record.return_cost_zone_change_shape_mismatch", prefix + " return-cost witness is not battlefield-to-hand movement");
                    }
                    if (zone_record.was_ability_object) {
                        add_error(out, "stack_placement_record.return_cost_zone_change_ability_object", prefix + " return-cost witness points at a synthetic ability object");
                    }
                }
            }
            const bool return_payment_range_ok = validate_range(record.first_return_cost_payment_record_index,
                                                               record.return_cost_payment_record_count,
                                                               game.return_cost_payment_records.size(),
                                                               "stack_placement_record.invalid_return_cost_payment_record_range",
                                                               "return-cost payment");
            if (return_payment_range_ok) {
                for (u32 offset = 0; offset < record.return_cost_payment_record_count; ++offset) {
                    const auto& payment = game.return_cost_payment_records[record.first_return_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.return_cost_payment_sequence_outside_span", prefix + " has a return-cost payment receipt outside the paid-action window");
                    }
                    if (payment.payer != record.controller) {
                        add_error(out, "stack_placement_record.return_cost_payment_payer_mismatch", prefix + " linked return-cost payment has a different payer");
                    }
                    if (payment.source_object.valid() && payment.source_object != record.source_object) {
                        add_error(out, "stack_placement_record.return_cost_payment_source_mismatch", prefix + " linked return-cost payment has a different source object");
                    }
                    if (record.return_cost_payment_record_count == 1U && payment.payment_hash != record.return_cost_payment_hash) {
                        add_error(out, "stack_placement_record.return_cost_payment_hash_mismatch", prefix + " return-cost payment hash does not match the linked receipt");
                    }
                    if (record.return_cost_zone_change_record_count != 0U &&
                        (payment.first_zone_change_record_index != record.first_return_cost_zone_change_record_index ||
                         payment.zone_change_record_count != record.return_cost_zone_change_record_count)) {
                        add_error(out, "stack_placement_record.return_cost_payment_zone_range_mismatch", prefix + " linked return-cost payment names a different exact return zone-change range");
                    }
                    if (record.return_cost_event_sequence != 0U && payment.sequence != record.return_cost_event_sequence) {
                        add_error(out, "stack_placement_record.return_cost_payment_event_mismatch", prefix + " linked return-cost payment sequence differs from the payment event witness");
                    }
                }
            }
            const bool loyalty_payment_range_ok = validate_range(record.first_loyalty_cost_payment_record_index,
                                                                 record.loyalty_cost_payment_record_count,
                                                                 game.loyalty_cost_payment_records.size(),
                                                                 "stack_placement_record.invalid_loyalty_cost_payment_record_range",
                                                                 "loyalty-cost payment");
            if (loyalty_payment_range_ok) {
                for (u32 offset = 0; offset < record.loyalty_cost_payment_record_count; ++offset) {
                    const auto& payment = game.loyalty_cost_payment_records[record.first_loyalty_cost_payment_record_index + offset - 1U];
                    if (payment.sequence <= record.choices_locked_sequence || payment.sequence >= record.sequence) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_sequence_outside_span", prefix + " has a loyalty-cost payment receipt outside the paid-action window");
                    }
                    if (payment.payer != record.controller) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_payer_mismatch", prefix + " linked loyalty-cost payment has a different payer");
                    }
                    if (payment.source_object != record.source_object) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_source_mismatch", prefix + " linked loyalty-cost payment has a different source object");
                    }
                    if (payment.source_zone_change_index_before != record.source_zone_change_index_before) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_zone_snapshot_mismatch", prefix + " linked loyalty-cost payment names a different source zone-change snapshot");
                    }
                    if (payment.cost_delta != record.loyalty_cost_delta) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_delta_mismatch", prefix + " linked loyalty-cost payment differs from the stack placement loyalty delta");
                    }
                    if (record.loyalty_cost_payment_record_count == 1U && payment.payment_hash != record.loyalty_cost_payment_hash) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_hash_mismatch", prefix + " loyalty-cost payment hash does not match the linked receipt");
                    }
                    if (record.paid_action_counter_change_record_count != 0U &&
                        (payment.counter_change_record_index < record.first_paid_action_counter_change_record_index ||
                         payment.counter_change_record_index >= record.first_paid_action_counter_change_record_index + record.paid_action_counter_change_record_count)) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_counter_range_mismatch", prefix + " linked loyalty-cost payment names a counter-change row outside the paid-action counter range");
                    }
                    if (record.loyalty_cost_event_sequence != 0U && payment.sequence != record.loyalty_cost_event_sequence) {
                        add_error(out, "stack_placement_record.loyalty_cost_payment_event_mismatch", prefix + " linked loyalty-cost payment sequence differs from the counter-change event witness");
                    }
                }
            }

            if (record.mana_cost_required && record.mana_cost_paid && record.mana_payment_plan_record_count == 0U) {
                add_error(out, "stack_placement_record.paid_phase_missing_mana_plan", prefix + " paid mana cost lacks a linked mana-payment plan range");
            }
            if (record.mana_cost_required && record.mana_cost_paid && record.mana_change_record_count == 0U) {
                add_error(out, "stack_placement_record.paid_phase_missing_mana_change", prefix + " paid mana cost lacks a linked mana-change range");
            }
            if (record.sacrifice_cost_paid && record.paid_action_zone_change_record_count == 0U) {
                add_error(out, "stack_placement_record.paid_phase_missing_sacrifice_zone_change", prefix + " paid sacrifice cost lacks a cost-zone-change range");
            }
            if (record.sacrifice_cost_paid && record.sacrifice_cost_zone_change_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_sacrifice_cost_zone_change_witness", prefix + " paid sacrifice cost lacks an exact sacrifice-zone-change witness range");
            }
            if (record.sacrifice_cost_paid && record.sacrifice_cost_payment_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_sacrifice_cost_payment_record", prefix + " paid sacrifice cost lacks a typed sacrifice-cost payment receipt");
            }
            if (record.sacrifice_cost_paid && record.sacrifice_cost_payment_record_count == 1U && record.sacrifice_cost_payment_hash == 0U) {
                add_error(out, "stack_placement_record.missing_sacrifice_cost_payment_hash", prefix + " paid sacrifice cost links one payment receipt but stores no receipt hash");
            }
            if (!record.sacrifice_cost_paid && (record.first_sacrifice_cost_payment_record_index != 0U ||
                                                record.sacrifice_cost_payment_record_count != 0U ||
                                                record.sacrifice_cost_payment_hash != 0U)) {
                add_error(out, "stack_placement_record.unexpected_sacrifice_cost_payment_record", prefix + " links sacrifice-cost payment receipts without a paid sacrifice cost");
            }
            if (record.sacrifice_cost_paid) {
                if (record.sacrifice_cost_event_sequence == 0U) {
                    add_error(out, "stack_placement_record.missing_sacrifice_cost_event_witness", prefix + " paid sacrifice cost lacks the summary pay_sacrifice_cost event witness");
                } else {
                    const auto sacrifice_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                        return event_record.sequence == record.sacrifice_cost_event_sequence;
                    });
                    if (sacrifice_it == game.event_records.end()) {
                        add_error(out, "stack_placement_record.sacrifice_cost_event_witness_missing", prefix + " sacrifice-cost event witness sequence does not name an EventRecord");
                    } else {
                        const auto& sacrifice_record = *sacrifice_it;
                        if (sacrifice_record.kind != EventRecordKind::Log || sacrifice_record.log_kind != "pay_sacrifice_cost") {
                            add_error(out, "stack_placement_record.sacrifice_cost_event_witness_not_payment", prefix + " sacrifice-cost event witness does not name a pay_sacrifice_cost log row");
                        }
                        if (sacrifice_record.sequence <= record.choices_locked_sequence || sacrifice_record.sequence >= record.sequence) {
                            add_error(out, "stack_placement_record.sacrifice_cost_event_witness_sequence_outside_span", prefix + " sacrifice-cost event witness is outside the paid-action window");
                        }
                    }
                }
            }
            if (record.discard_cost_paid && record.paid_action_zone_change_record_count == 0U) {
                add_error(out, "stack_placement_record.paid_phase_missing_discard_zone_change", prefix + " paid discard cost lacks a cost-zone-change range");
            }
            if (record.discard_cost_paid && record.discard_cost_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_discard_cost_discard_witness", prefix + " paid discard cost lacks an exact discard-record witness range");
            }
            if (record.discard_cost_paid && record.discard_cost_zone_change_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_discard_cost_zone_change_witness", prefix + " paid discard cost lacks an exact hand-to-graveyard witness range");
            }
            if (record.discard_cost_paid && record.discard_cost_payment_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_discard_cost_payment_record", prefix + " paid discard cost lacks a typed discard-cost payment receipt");
            }
            if (record.discard_cost_paid && record.discard_cost_payment_record_count == 1U && record.discard_cost_payment_hash == 0U) {
                add_error(out, "stack_placement_record.missing_discard_cost_payment_hash", prefix + " paid discard cost links one payment receipt but stores no receipt hash");
            }
            if (!record.discard_cost_paid && (record.first_discard_cost_payment_record_index != 0U ||
                                               record.discard_cost_payment_record_count != 0U ||
                                               record.discard_cost_payment_hash != 0U ||
                                               record.first_discard_cost_record_index != 0U ||
                                               record.discard_cost_record_count != 0U ||
                                               record.first_discard_cost_zone_change_record_index != 0U ||
                                               record.discard_cost_zone_change_record_count != 0U ||
                                               record.discard_cost_event_sequence != 0U)) {
                add_error(out, "stack_placement_record.unexpected_discard_cost_payment_record", prefix + " links discard-cost payment receipts without a paid discard cost");
            }
            if (record.discard_cost_paid) {
                if (record.discard_cost_event_sequence == 0U) {
                    add_error(out, "stack_placement_record.missing_discard_cost_event_witness", prefix + " paid discard cost lacks the summary pay_discard_cost event witness");
                } else {
                    const auto discard_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                        return event_record.sequence == record.discard_cost_event_sequence;
                    });
                    if (discard_it == game.event_records.end()) {
                        add_error(out, "stack_placement_record.discard_cost_event_witness_missing", prefix + " discard-cost event witness sequence does not name an EventRecord");
                    } else {
                        const auto& discard_event = *discard_it;
                        if (discard_event.kind != EventRecordKind::Log || discard_event.log_kind != "pay_discard_cost") {
                            add_error(out, "stack_placement_record.discard_cost_event_witness_not_payment", prefix + " discard-cost event witness does not name a pay_discard_cost log row");
                        }
                        if (discard_event.sequence <= record.choices_locked_sequence || discard_event.sequence >= record.sequence) {
                            add_error(out, "stack_placement_record.discard_cost_event_witness_sequence_outside_span", prefix + " discard-cost event witness is outside the paid-action window");
                        }
                    }
                }
            }
            if (record.life_cost_paid && record.life_cost_payment_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_life_cost_payment_record", prefix + " paid life cost lacks a typed life-cost payment receipt");
            }
            if (record.life_cost_paid && record.life_cost_payment_record_count == 1U && record.life_cost_payment_hash == 0U) {
                add_error(out, "stack_placement_record.missing_life_cost_payment_hash", prefix + " paid life cost links one payment receipt but stores no receipt hash");
            }
            if (record.life_cost_paid && record.life_cost_life_change_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_life_cost_life_change_witness", prefix + " paid life cost lacks a life-change witness range");
            }
            if (!record.life_cost_paid && (record.first_life_cost_payment_record_index != 0U ||
                                           record.life_cost_payment_record_count != 0U ||
                                           record.life_cost_payment_hash != 0U ||
                                           record.first_life_cost_life_change_record_index != 0U ||
                                           record.life_cost_life_change_record_count != 0U ||
                                           record.life_cost_event_sequence != 0U)) {
                add_error(out, "stack_placement_record.unexpected_life_cost_payment_record", prefix + " links life-cost payment receipts without a paid life cost");
            }
            if (record.life_cost_paid) {
                if (record.life_cost_event_sequence == 0U) {
                    add_error(out, "stack_placement_record.missing_life_cost_event_witness", prefix + " paid life cost lacks the summary pay_life_cost event witness");
                } else {
                    const auto life_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                        return event_record.sequence == record.life_cost_event_sequence;
                    });
                    if (life_it == game.event_records.end()) {
                        add_error(out, "stack_placement_record.life_cost_event_witness_missing", prefix + " life-cost event witness sequence does not name an EventRecord");
                    } else {
                        const auto& life_event = *life_it;
                        if (life_event.kind != EventRecordKind::Log || life_event.log_kind != "pay_life_cost") {
                            add_error(out, "stack_placement_record.life_cost_event_witness_not_payment", prefix + " life-cost event witness does not name a pay_life_cost log row");
                        }
                        if (life_event.sequence <= record.choices_locked_sequence || life_event.sequence >= record.sequence) {
                            add_error(out, "stack_placement_record.life_cost_event_witness_sequence_outside_span", prefix + " life-cost event witness is outside the paid-action window");
                        }
                        if (life_event.player != record.controller) {
                            add_error(out, "stack_placement_record.life_cost_event_witness_player_mismatch", prefix + " life-cost event witness names a different controller");
                        }
                    }
                }
            }
            if (record.return_cost_paid && record.return_cost_payment_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_return_cost_payment_record", prefix + " paid return cost lacks a typed return-cost payment receipt");
            }
            if (record.return_cost_paid && record.return_cost_payment_record_count == 1U && record.return_cost_payment_hash == 0U) {
                add_error(out, "stack_placement_record.missing_return_cost_payment_hash", prefix + " paid return cost links one payment receipt but stores no receipt hash");
            }
            if (record.return_cost_paid && record.return_cost_zone_change_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_return_cost_zone_change_witness", prefix + " paid return cost lacks a zone-change witness range");
            }
            if (!record.return_cost_paid && (record.first_return_cost_payment_record_index != 0U ||
                                             record.return_cost_payment_record_count != 0U ||
                                             record.return_cost_payment_hash != 0U ||
                                             record.first_return_cost_zone_change_record_index != 0U ||
                                             record.return_cost_zone_change_record_count != 0U ||
                                             record.return_cost_event_sequence != 0U)) {
                add_error(out, "stack_placement_record.unexpected_return_cost_payment_record", prefix + " links return-cost payment receipts without a paid return cost");
            }
            if (record.return_cost_paid) {
                if (record.return_cost_event_sequence == 0U) {
                    add_error(out, "stack_placement_record.missing_return_cost_event_witness", prefix + " paid return cost lacks the summary pay_return_cost event witness");
                } else {
                    const auto return_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                        return event_record.sequence == record.return_cost_event_sequence;
                    });
                    if (return_it == game.event_records.end()) {
                        add_error(out, "stack_placement_record.return_cost_event_witness_missing", prefix + " return-cost event witness sequence does not name an EventRecord");
                    } else {
                        const auto& return_event = *return_it;
                        if (return_event.kind != EventRecordKind::Log || return_event.log_kind != "pay_return_cost") {
                            add_error(out, "stack_placement_record.return_cost_event_witness_not_payment", prefix + " return-cost event witness does not name a pay_return_cost log row");
                        }
                        if (return_event.sequence <= record.choices_locked_sequence || return_event.sequence >= record.sequence) {
                            add_error(out, "stack_placement_record.return_cost_event_witness_sequence_outside_span", prefix + " return-cost event witness is outside the paid-action window");
                        }
                        if (return_event.player != record.controller) {
                            add_error(out, "stack_placement_record.return_cost_event_witness_player_mismatch", prefix + " return-cost event witness names a different controller");
                        }
                        if (return_event.object != record.source_object) {
                            add_error(out, "stack_placement_record.return_cost_event_witness_source_mismatch", prefix + " return-cost event witness names a different source object");
                        }
                    }
                }
            }
            if (record.loyalty_cost_paid && record.loyalty_cost_delta != 0 && record.paid_action_counter_change_record_count == 0U) {
                add_error(out, "stack_placement_record.paid_phase_missing_loyalty_counter_change", prefix + " paid loyalty cost lacks a counter-change range");
            }
            if (record.loyalty_cost_paid && record.loyalty_cost_delta != 0 && record.loyalty_cost_payment_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_loyalty_cost_payment_record", prefix + " paid loyalty cost lacks a typed loyalty-cost payment receipt");
            }
            if (record.loyalty_cost_paid && record.loyalty_cost_delta != 0 && record.loyalty_cost_payment_record_count == 1U && record.loyalty_cost_payment_hash == 0U) {
                add_error(out, "stack_placement_record.missing_loyalty_cost_payment_hash", prefix + " paid loyalty cost links one payment receipt but stores no receipt hash");
            }
            if (!record.loyalty_cost_paid && (record.first_loyalty_cost_payment_record_index != 0U ||
                                               record.loyalty_cost_payment_record_count != 0U ||
                                               record.loyalty_cost_payment_hash != 0U ||
                                               record.loyalty_cost_event_sequence != 0U)) {
                add_error(out, "stack_placement_record.unexpected_loyalty_cost_payment_record", prefix + " links loyalty-cost payment receipts without a paid loyalty cost");
            }
            if (record.loyalty_cost_paid && record.loyalty_cost_delta != 0) {
                if (record.loyalty_cost_event_sequence == 0U) {
                    add_error(out, "stack_placement_record.missing_loyalty_cost_event_witness", prefix + " paid loyalty cost lacks the loyalty_cost_paid CounterChange event witness");
                } else {
                    const auto loyalty_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                        return event_record.sequence == record.loyalty_cost_event_sequence;
                    });
                    if (loyalty_it == game.event_records.end()) {
                        add_error(out, "stack_placement_record.loyalty_cost_event_witness_missing", prefix + " loyalty-cost event witness sequence does not name an EventRecord");
                    } else {
                        const auto& loyalty_event = *loyalty_it;
                        if (loyalty_event.kind != EventRecordKind::CounterChange || loyalty_event.log_kind != "loyalty_cost_paid") {
                            add_error(out, "stack_placement_record.loyalty_cost_event_witness_not_payment", prefix + " loyalty-cost event witness does not name a loyalty_cost_paid CounterChange row");
                        }
                        if (loyalty_event.sequence <= record.choices_locked_sequence || loyalty_event.sequence >= record.sequence) {
                            add_error(out, "stack_placement_record.loyalty_cost_event_witness_sequence_outside_span", prefix + " loyalty-cost event witness is outside the paid-action window");
                        }
                        if (loyalty_event.object != record.source_object) {
                            add_error(out, "stack_placement_record.loyalty_cost_event_witness_source_mismatch", prefix + " loyalty-cost event witness names a different source object");
                        }
                        if (loyalty_event.player != record.controller) {
                            add_error(out, "stack_placement_record.loyalty_cost_event_witness_player_mismatch", prefix + " loyalty-cost event witness names a different controller");
                        }
                        if (loyalty_event.counter_change_record_index == 0U) {
                            add_error(out, "stack_placement_record.loyalty_cost_event_witness_missing_counter_link", prefix + " loyalty-cost event witness lacks a counter-change backlink");
                        }
                    }
                }
            }
            if (record.tap_cost_paid && record.tap_cost_payment_record_count == 0U) {
                add_error(out, "stack_placement_record.missing_tap_cost_payment_record", prefix + " paid tap cost lacks a typed tap-cost payment receipt");
            }
            if (record.tap_cost_paid && record.tap_cost_payment_record_count == 1U && record.tap_cost_payment_hash == 0U) {
                add_error(out, "stack_placement_record.missing_tap_cost_payment_hash", prefix + " paid tap cost links one payment receipt but stores no receipt hash");
            }
            if (!record.tap_cost_paid && (record.first_tap_cost_payment_record_index != 0U ||
                                         record.tap_cost_payment_record_count != 0U ||
                                         record.tap_cost_payment_hash != 0U ||
                                         record.tap_cost_event_sequence != 0U)) {
                add_error(out, "stack_placement_record.unexpected_tap_cost_payment_record", prefix + " links tap-cost payment receipts without a paid tap cost");
            }
            if (record.tap_cost_paid) {
                if (record.tap_cost_event_sequence == 0U) {
                    add_error(out, "stack_placement_record.paid_phase_missing_tap_witness", prefix + " paid tap cost lacks an exact tap EventRecord witness");
                } else {
                    const auto tap_it = std::find_if(game.event_records.begin(), game.event_records.end(), [&](const EventRecord& event_record) {
                        return event_record.sequence == record.tap_cost_event_sequence;
                    });
                    if (tap_it == game.event_records.end()) {
                        add_error(out, "stack_placement_record.paid_phase_tap_witness_missing", prefix + " tap-cost witness sequence does not name an EventRecord");
                    } else {
                        const auto& tap_record = *tap_it;
                        if (tap_record.kind != EventRecordKind::Log || tap_record.log_kind != "tap") {
                            add_error(out, "stack_placement_record.paid_phase_tap_witness_not_tap", prefix + " tap-cost witness does not name a tap log row");
                        }
                        if (tap_record.sequence <= record.choices_locked_sequence || tap_record.sequence >= record.sequence) {
                            add_error(out, "stack_placement_record.paid_phase_tap_witness_sequence_outside_span", prefix + " tap-cost witness is outside the paid-action window");
                        }
                        if (tap_record.object != record.source_object) {
                            add_error(out, "stack_placement_record.paid_phase_tap_witness_source_mismatch", prefix + " tap-cost witness names a different source object");
                        }
                        if (tap_record.player != record.controller) {
                            add_error(out, "stack_placement_record.paid_phase_tap_witness_player_mismatch", prefix + " tap-cost witness names a different controller");
                        }
                        if (tap_record.object_zone_change_index != record.source_zone_change_index_before) {
                            add_error(out, "stack_placement_record.paid_phase_tap_witness_zone_index_mismatch", prefix + " tap-cost witness names a different source zone-change snapshot");
                        }
                    }
                }
            }
        }

        if (record.kind == StackPlacementKind::SpellCast) {
            if (!record.physical_card || record.ability_object) {
                add_error(out, "stack_placement_record.spell_shape_mismatch", prefix + " spell casts must be physical-card placements, not ability objects");
            }
            if (record.source_object != record.stack_object) {
                add_error(out, "stack_placement_record.spell_source_stack_mismatch", prefix + " spell source and stack object should be the same object");
            }
            if (record.source_zone_before != Zone::Hand) {
                add_error(out, "stack_placement_record.spell_source_zone_not_hand", prefix + " spell cast source_zone_before should be hand");
            }
            if (record.stack_enter_zone_change_record_index == 0U || record.stack_enter_zone_change_record_index > game.zone_change_records.size()) {
                add_error(out, "stack_placement_record.invalid_stack_enter_zone_change", prefix + " links invalid stack-enter ZoneChangeRecord");
            } else {
                const auto& zone_record = game.zone_change_records[record.stack_enter_zone_change_record_index - 1U];
                if (zone_record.object != record.stack_object || zone_record.to_zone != Zone::Stack) {
                    add_error(out, "stack_placement_record.stack_enter_zone_change_mismatch", prefix + " linked ZoneChangeRecord does not move the stack object to the stack");
                }
                if (zone_record.to_zone_change_index != record.stack_zone_change_index) {
                    add_error(out, "stack_placement_record.stack_zone_change_index_mismatch", prefix + " stack zone-change snapshot disagrees with linked ZoneChangeRecord");
                }
            }
            if (record.ability_index != 0U) {
                add_error(out, "stack_placement_record.spell_has_ability_index", prefix + " spell cast unexpectedly records an ability index");
            }
            if (record.tap_cost_required || record.tap_cost_paid || record.loyalty_cost_paid) {
                add_error(out, "stack_placement_record.spell_has_ability_cost", prefix + " spell cast unexpectedly records tap or loyalty costs");
            }
        } else if (record.kind == StackPlacementKind::ActivatedAbility || record.kind == StackPlacementKind::LoyaltyAbility) {
            if (record.physical_card || !record.ability_object) {
                add_error(out, "stack_placement_record.ability_shape_mismatch", prefix + " ability placements must be synthetic ability objects");
            }
            if (record.source_object == record.stack_object) {
                add_error(out, "stack_placement_record.ability_source_stack_same", prefix + " ability source and stack object should be distinct objects");
            }
            if (record.source_zone_before != Zone::Battlefield) {
                add_error(out, "stack_placement_record.ability_source_zone_not_battlefield", prefix + " ability source_zone_before should be battlefield");
            }
            if (record.stack_enter_zone_change_record_index != 0U) {
                add_error(out, "stack_placement_record.ability_has_stack_enter_zone_change", prefix + " synthetic ability objects should not link a card-move ZoneChangeRecord");
            }
            if (record.ability_index == 0U) {
                add_error(out, "stack_placement_record.ability_missing_index", prefix + " ability placement missing ability_index");
            }
            if (is_valid_object_ref(game, record.stack_object) && !object(game, record.stack_object).ability_object) {
                add_error(out, "stack_placement_record.stack_object_not_ability", prefix + " stack_object is not marked ability_object");
            }
        }

        if (record.kind == StackPlacementKind::ActivatedAbility) {
            if (record.loyalty_cost_paid || record.loyalty_cost_delta != 0) {
                add_error(out, "stack_placement_record.activated_has_loyalty_cost", prefix + " activated ability unexpectedly records loyalty cost state");
            }
            if (record.mana_cost_required != record.mana_cost_paid) {
                add_error(out, "stack_placement_record.mana_cost_unpaid", prefix + " activated ability mana-cost flags disagree");
            }
            if (record.tap_cost_required != record.tap_cost_paid) {
                add_error(out, "stack_placement_record.tap_cost_unpaid", prefix + " activated ability tap-cost flags disagree");
            }
            if (record.sacrifice_cost_required != record.sacrifice_cost_paid) {
                add_error(out, "stack_placement_record.sacrifice_cost_unpaid", prefix + " activated ability sacrifice-cost flags disagree");
            }
            if (record.discard_cost_required != record.discard_cost_paid) {
                add_error(out, "stack_placement_record.discard_cost_unpaid", prefix + " activated ability discard-cost flags disagree");
            }
        } else if (record.kind == StackPlacementKind::LoyaltyAbility) {
            if (!record.loyalty_cost_paid) {
                add_error(out, "stack_placement_record.loyalty_cost_unpaid", prefix + " loyalty ability missing paid loyalty-cost marker");
            }
            if (record.mana_cost_required || record.mana_cost_paid || record.tap_cost_required || record.tap_cost_paid ||
                record.sacrifice_cost_required || record.sacrifice_cost_paid || record.discard_cost_required || record.discard_cost_paid) {
                add_error(out, "stack_placement_record.loyalty_has_nonloyalty_cost", prefix + " loyalty ability unexpectedly records mana/tap/sacrifice/discard cost state");
            }
        }
        if (record.mana_cost_required && !record.mana_cost_paid) {
            add_error(out, "stack_placement_record.mana_cost_unpaid", prefix + " required mana cost was not recorded as paid");
        }
        if (record.sacrifice_cost_required && !record.sacrifice_cost_paid) {
            add_error(out, "stack_placement_record.sacrifice_cost_unpaid", prefix + " required sacrifice cost was not recorded as paid");
        }
        if (record.discard_cost_required && !record.discard_cost_paid) {
            add_error(out, "stack_placement_record.discard_cost_unpaid", prefix + " required discard cost was not recorded as paid");
        }
    }

    u64 last_stack_resolution_sequence = 0;
    for (std::size_t i = 0; i < game.stack_resolution_records.size(); ++i) {
        const auto& record = game.stack_resolution_records[i];
        const std::string prefix = "stack_resolution_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "stack_resolution_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "stack_resolution_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_stack_resolution_sequence != 0U && record.sequence <= last_stack_resolution_sequence) {
            add_error(out, "stack_resolution_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_stack_resolution_sequence = record.sequence;
        if (i + 1U < stack_resolution_event_links.size() && stack_resolution_event_links[i + 1U] != 1U) {
            add_error(out, "stack_resolution_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(stack_resolution_event_links[i + 1U]));
        }
        if (!is_valid_object_ref(game, record.stack_object)) {
            add_error(out, "stack_resolution_record.invalid_stack_object", prefix + " stack_object=" + object_ref(record.stack_object));
        }
        if (!is_valid_player_ref(game, record.controller)) {
            add_error(out, "stack_resolution_record.invalid_controller", prefix + " controller=" + player_ref(record.controller));
        }
        u32 observed_trigger_record_index = 0U;
        bool duplicate_trigger_stack_object = false;
        for (std::size_t trigger_index = 0; trigger_index < game.trigger_records.size(); ++trigger_index) {
            const auto& trigger_record = game.trigger_records[trigger_index];
            if (!trigger_record.dropped && trigger_record.put_on_stack_sequence != 0U && trigger_record.stack_object == record.stack_object) {
                if (observed_trigger_record_index != 0U) {
                    duplicate_trigger_stack_object = true;
                }
                observed_trigger_record_index = static_cast<u32>(trigger_index + 1U);
            }
        }
        if (duplicate_trigger_stack_object) {
            add_error(out, "stack_resolution_record.duplicate_trigger_stack_object", prefix + " resolved a stack object claimed by multiple TriggerRecords");
        }
        if (observed_trigger_record_index != 0U && record.trigger_record_index == 0U) {
            add_error(out, "stack_resolution_record.missing_trigger_record_link", prefix + " resolved a triggered ability object without a TriggerRecord link");
        }
        if (record.trigger_record_index != 0U) {
            if (!record.ability_object) {
                add_error(out, "stack_resolution_record.trigger_link_on_nonability", prefix + " links a TriggerRecord from a non-ability resolution");
            }
            if (record.trigger_record_index > game.trigger_records.size()) {
                add_error(out, "stack_resolution_record.invalid_trigger_record_link", prefix + " links invalid TriggerRecord index=" + std::to_string(record.trigger_record_index));
            } else {
                const auto& trigger_record = game.trigger_records[record.trigger_record_index - 1U];
                if (observed_trigger_record_index != 0U && observed_trigger_record_index != record.trigger_record_index) {
                    add_error(out, "stack_resolution_record.trigger_record_identity_mismatch", prefix + " trigger_record_index does not match the TriggerRecord owning this stack object");
                }
                if (trigger_record.stack_object != record.stack_object) {
                    add_error(out, "stack_resolution_record.trigger_stack_object_mismatch", prefix + " linked TriggerRecord names a different stack object");
                }
                if (trigger_record.stack_resolution_record_index != i + 1U) {
                    add_error(out, "stack_resolution_record.trigger_record_backlink_mismatch", prefix + " linked TriggerRecord does not point back to this resolution record");
                }
                if (trigger_record.resolved_sequence != record.sequence) {
                    add_error(out, "stack_resolution_record.trigger_resolved_sequence_mismatch", prefix + " linked TriggerRecord resolved_sequence disagrees with this record");
                }
                if (trigger_record.resolution_outcome != record.outcome) {
                    add_error(out, "stack_resolution_record.trigger_resolution_outcome_mismatch", prefix + " linked TriggerRecord outcome disagrees with this record");
                }
                if (!exact_target_vectors_equal(trigger_record.chosen_targets, record.chosen_targets)) {
                    add_error(out, "stack_resolution_record.trigger_targets_mismatch", prefix + " linked TriggerRecord target vector disagrees with this record");
                }
            }
        }
        if (record.outcome == StackResolutionOutcome::Count || static_cast<u8>(record.outcome) >= static_cast<u8>(StackResolutionOutcome::Count)) {
            add_error(out, "stack_resolution_record.invalid_outcome", prefix + " outcome=" + std::string(to_string(record.outcome)));
        }
        if (!is_valid_zone_ref(record.final_zone)) {
            add_error(out, "stack_resolution_record.invalid_final_zone", prefix + " final_zone=" + std::string(to_string(record.final_zone)));
        }
        if (record.stack_zone_change_index == 0U) {
            add_error(out, "stack_resolution_record.missing_stack_zone_change_index", prefix + " missing the stack object's pre-resolution zone-change identity");
        }
        if (record.stack_object_left_stack && record.stack_leave_zone_change_record_index == 0U) {
            add_error(out, "stack_resolution_record.missing_leave_zone_change", prefix + " says stack object left the stack but has no ZoneChangeRecord link");
        }
        if (record.stack_leave_zone_change_record_index != 0U) {
            if (record.stack_leave_zone_change_record_index > game.zone_change_records.size()) {
                add_error(out, "stack_resolution_record.invalid_leave_zone_change", prefix + " links invalid stack_leave_zone_change_record_index=" + std::to_string(record.stack_leave_zone_change_record_index));
            } else {
                const auto& zone_record = game.zone_change_records[record.stack_leave_zone_change_record_index - 1U];
                if (zone_record.object != record.stack_object) {
                    add_error(out, "stack_resolution_record.leave_zone_change_object_mismatch", prefix + " linked ZoneChangeRecord belongs to a different object");
                }
                if (zone_record.from_zone != Zone::Stack) {
                    add_error(out, "stack_resolution_record.leave_zone_change_not_from_stack", prefix + " linked ZoneChangeRecord did not move from the stack");
                }
                if (zone_record.from_zone_change_index != record.stack_zone_change_index) {
                    add_error(out, "stack_resolution_record.leave_zone_change_index_mismatch", prefix + " linked ZoneChangeRecord does not start from the recorded stack identity");
                }
            }
        }
        if (record.effect_kind == EffectKind::Count) {
            add_error(out, "stack_resolution_record.invalid_effect", prefix + " effect_kind=count");
        }
        validate_target_definition(out, "stack_resolution_record", prefix, record.target_mask, record.target_count);
        const u32 expected_required_targets = required_target_count_for_validation(record.target_mask, record.target_count);
        if (record.required_target_count != expected_required_targets) {
            add_error(out, "stack_resolution_record.required_target_count_mismatch", prefix + " required_target_count=" + std::to_string(record.required_target_count) + " expected=" + std::to_string(expected_required_targets));
        }
        if (record.legal_target_count > record.chosen_targets.size()) {
            add_error(out, "stack_resolution_record.legal_target_overflow", prefix + " legal_target_count exceeds chosen target count");
        }
        if (record.target_resolution_checks.size() != record.chosen_targets.size()) {
            add_error(out, "stack_resolution_record.target_check_count_mismatch", prefix + " target_resolution_checks size disagrees with chosen target count");
        }
        u32 legal_target_check_count = 0;
        for (std::size_t target_index = 0; target_index < record.target_resolution_checks.size(); ++target_index) {
            const auto& check = record.target_resolution_checks[target_index];
            const std::string check_prefix = prefix + ".target_resolution_check#" + std::to_string(target_index + 1U);
            if (check.target_index != target_index + 1U) {
                add_error(out, "stack_resolution_record.target_check_index_mismatch", check_prefix + " has target_index=" + std::to_string(check.target_index));
            }
            if (target_index < record.chosen_targets.size() && !same_target_snapshot_for_validation(check.target, record.chosen_targets[target_index])) {
                add_error(out, "stack_resolution_record.target_check_target_mismatch", check_prefix + " does not match the chosen target snapshot");
            }
            if (check.legal_on_resolution) {
                ++legal_target_check_count;
                if (check.failure_kind != TargetLegalityFailureKind::None) {
                    add_error(out, "stack_resolution_record.legal_target_has_failure", check_prefix + " is legal but failure_kind=" + std::string(to_string(check.failure_kind)));
                }
            } else if (check.failure_kind == TargetLegalityFailureKind::None) {
                add_error(out, "stack_resolution_record.illegal_target_missing_failure", check_prefix + " is illegal but has no failure_kind");
            }
            if (check.failure_kind == TargetLegalityFailureKind::Count || static_cast<u8>(check.failure_kind) >= static_cast<u8>(TargetLegalityFailureKind::Count)) {
                add_error(out, "stack_resolution_record.invalid_target_failure_kind", check_prefix + " failure_kind=" + std::string(to_string(check.failure_kind)));
            }
            if (check.target.kind == TargetKind::Player && !is_valid_player_ref(game, check.target.player)) {
                add_error(out, "stack_resolution_record.target_check_invalid_player", check_prefix + " has " + target_ref(check.target));
            } else if (check.target.kind == TargetKind::Object && !is_valid_object_ref(game, check.target.object)) {
                add_error(out, "stack_resolution_record.target_check_invalid_object", check_prefix + " has " + target_ref(check.target));
            } else if (check.target.kind == TargetKind::None && check.failure_kind != TargetLegalityFailureKind::EmptyTarget) {
                add_error(out, "stack_resolution_record.target_check_empty_target_kind", check_prefix + " has target:none without empty_target failure");
            }
            if (check.target.kind == TargetKind::Object && check.failure_kind != TargetLegalityFailureKind::ObjectMissing && check.object_zone_on_resolution == Zone::Count) {
                add_error(out, "stack_resolution_record.target_check_missing_object_zone", check_prefix + " lacks object_zone_on_resolution");
            }
            if (check.target.kind == TargetKind::Object && check.failure_kind == TargetLegalityFailureKind::ObjectZoneChangeMismatch && check.object_zone_change_index_on_resolution == check.target.object_zone_change_index) {
                add_error(out, "stack_resolution_record.target_check_identity_failure_not_mismatched", check_prefix + " records an identity mismatch but the zone-change indexes match");
            }
            if (check.target.kind != TargetKind::Object && (check.object_zone_on_resolution != Zone::Count || check.object_zone_change_index_on_resolution != 0U)) {
                add_error(out, "stack_resolution_record.target_check_nonobject_zone_snapshot", check_prefix + " carries object zone data for a non-object target");
            }
            if (!check.source_controller.valid()) {
                add_error(out, "stack_resolution_record.target_check_missing_source_controller", check_prefix + " missing source controller snapshot");
            } else if (!is_valid_player_ref(game, check.source_controller)) {
                add_error(out, "stack_resolution_record.target_check_invalid_source_controller", check_prefix + " source_controller=" + player_ref(check.source_controller));
            }
        }
        if (record.legal_target_count != legal_target_check_count) {
            add_error(out, "stack_resolution_record.legal_target_check_count_mismatch", prefix + " legal_target_count disagrees with per-target checks");
        }
        if (record.missing_required_targets != (record.chosen_targets.size() < record.required_target_count)) {
            add_error(out, "stack_resolution_record.missing_required_target_mismatch", prefix + " missing_required_targets flag disagrees with target counts");
        }
        if (record.all_targets_illegal != (!record.chosen_targets.empty() && record.legal_target_count == 0U)) {
            add_error(out, "stack_resolution_record.all_targets_illegal_mismatch", prefix + " all_targets_illegal flag disagrees with chosen/legal target counts");
        }
        const bool expected_target_failed = record.required_target_count != 0U && (record.effect_kind != EffectKind::None || record.aura_spell) && (record.missing_required_targets || record.all_targets_illegal);
        if (record.required_target_failed != expected_target_failed) {
            add_error(out, "stack_resolution_record.required_target_failed_mismatch", prefix + " required_target_failed flag disagrees with late target legality fields");
        }
        if (record.required_target_failed && record.outcome != StackResolutionOutcome::NoLegalTargets) {
            add_error(out, "stack_resolution_record.target_failure_outcome_mismatch", prefix + " failed required targets but outcome is not NoLegalTargets");
        }
        if (record.modal_choice_invalid && record.outcome != StackResolutionOutcome::InvalidMode) {
            add_error(out, "stack_resolution_record.modal_failure_outcome_mismatch", prefix + " invalid modal choice but outcome is not InvalidMode");
        }
        if (record.effect_payload_applied && (record.effect_kind == EffectKind::None || record.required_target_failed || record.modal_choice_invalid)) {
            add_error(out, "stack_resolution_record.effect_applied_when_blocked", prefix + " applied an effect despite no effect or blocked resolution");
        }
        for (const auto target : record.chosen_targets) {
            if (target.kind == TargetKind::Player && !is_valid_player_ref(game, target.player)) {
                add_error(out, "stack_resolution_record.invalid_target_player", prefix + " contains " + target_ref(target));
            } else if (target.kind == TargetKind::Object && !is_valid_object_ref(game, target.object)) {
                add_error(out, "stack_resolution_record.invalid_target_object", prefix + " contains " + target_ref(target));
            } else if (target.kind == TargetKind::None) {
                add_error(out, "stack_resolution_record.empty_target", prefix + " contains target:none");
            }
        }
    }

    u64 last_priority_transition_sequence = 0;
    for (std::size_t i = 0; i < game.priority_transition_records.size(); ++i) {
        const auto& record = game.priority_transition_records[i];
        const std::string prefix = "priority_transition_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "priority_transition_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "priority_transition_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_priority_transition_sequence != 0U && record.sequence <= last_priority_transition_sequence) {
            add_error(out, "priority_transition_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_priority_transition_sequence = record.sequence;
        if (i + 1U < priority_transition_event_links.size() && priority_transition_event_links[i + 1U] != 1U) {
            add_error(out, "priority_transition_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(priority_transition_event_links[i + 1U]));
        }
        if (record.outcome == PriorityTransitionOutcome::Count || static_cast<u8>(record.outcome) >= static_cast<u8>(PriorityTransitionOutcome::Count)) {
            add_error(out, "priority_transition_record.invalid_outcome", prefix + " outcome=" + std::string(to_string(record.outcome)));
        }
        if (!is_valid_player_ref(game, record.player)) {
            add_error(out, "priority_transition_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (!is_valid_player_ref(game, record.active_player)) {
            add_error(out, "priority_transition_record.invalid_active_player", prefix + " active_player=" + player_ref(record.active_player));
        }
        if (!is_valid_player_ref(game, record.priority_before)) {
            add_error(out, "priority_transition_record.invalid_priority_before", prefix + " priority_before=" + player_ref(record.priority_before));
        }
        if (record.priority_after.valid() && !is_valid_player_ref(game, record.priority_after)) {
            add_error(out, "priority_transition_record.invalid_priority_after", prefix + " priority_after=" + player_ref(record.priority_after));
        }
        if (!is_valid_step_ref(record.step_before)) {
            add_error(out, "priority_transition_record.invalid_step_before", prefix + " step_before=" + std::string(to_string(record.step_before)));
        }
        if (!is_valid_step_ref(record.step_after)) {
            add_error(out, "priority_transition_record.invalid_step_after", prefix + " step_after=" + std::string(to_string(record.step_after)));
        }
        if (record.stack_top_before.valid() && !is_valid_object_ref(game, record.stack_top_before)) {
            add_error(out, "priority_transition_record.invalid_stack_top_before", prefix + " stack_top_before=" + object_ref(record.stack_top_before));
        }
        if (record.stack_top_after.valid() && !is_valid_object_ref(game, record.stack_top_after)) {
            add_error(out, "priority_transition_record.invalid_stack_top_after", prefix + " stack_top_after=" + object_ref(record.stack_top_after));
        }
        if (record.stack_size_before == 0U && record.stack_top_before.valid()) {
            add_error(out, "priority_transition_record.stack_top_before_without_stack", prefix + " has stack_top_before but stack_size_before=0");
        }
        if (record.stack_size_after == 0U && record.stack_top_after.valid()) {
            add_error(out, "priority_transition_record.stack_top_after_without_stack", prefix + " has stack_top_after but stack_size_after=0");
        }
        if (record.pending_triggers_after > record.pending_triggers_before && record.outcome == PriorityTransitionOutcome::PendingTriggersPutOnStack) {
            add_error(out, "priority_transition_record.pending_trigger_count_increased", prefix + " increased pending trigger count while putting triggers on stack");
        }
        const bool expected_increment = record.outcome != PriorityTransitionOutcome::PendingTriggersPutOnStack;
        if (record.pass_count_incremented != expected_increment) {
            add_error(out, "priority_transition_record.pass_increment_flag_mismatch", prefix + " pass_count_incremented disagrees with outcome");
        }
        const u32 expected_after_pass = expected_increment ? record.consecutive_passes_before + 1U : record.consecutive_passes_before;
        if (record.consecutive_passes_after_pass != expected_after_pass) {
            add_error(out, "priority_transition_record.after_pass_count_mismatch", prefix + " consecutive_passes_after_pass does not match the expected pass increment");
        }
        if (record.priority_changed != (record.priority_before != record.priority_after)) {
            add_error(out, "priority_transition_record.priority_changed_mismatch", prefix + " priority_changed flag disagrees with before/after priority");
        }
        if (record.stack_resolved != (record.outcome == PriorityTransitionOutcome::StackResolved)) {
            add_error(out, "priority_transition_record.stack_resolved_flag_mismatch", prefix + " stack_resolved flag disagrees with outcome");
        }
        if (record.step_advanced != (record.outcome == PriorityTransitionOutcome::StepAdvanced)) {
            add_error(out, "priority_transition_record.step_advanced_flag_mismatch", prefix + " step_advanced flag disagrees with outcome");
        }
        if (record.pending_triggers_put_on_stack != (record.outcome == PriorityTransitionOutcome::PendingTriggersPutOnStack)) {
            add_error(out, "priority_transition_record.pending_trigger_flag_mismatch", prefix + " pending_triggers_put_on_stack flag disagrees with outcome");
        }

        switch (record.outcome) {
            case PriorityTransitionOutcome::PriorityAdvanced:
                if (record.stack_resolution_record_index != 0U || record.stack_resolved || record.step_advanced || record.pending_triggers_put_on_stack) {
                    add_error(out, "priority_transition_record.priority_advanced_extra_outcome", prefix + " priority advance should not link resolution/step/trigger outcomes");
                }
                if (record.step_after != record.step_before || record.stack_size_after != record.stack_size_before) {
                    add_error(out, "priority_transition_record.priority_advanced_state_changed", prefix + " priority-only pass changed stack or step state");
                }
                if (record.consecutive_passes_after != record.consecutive_passes_after_pass) {
                    add_error(out, "priority_transition_record.priority_advanced_pass_count", prefix + " priority-only pass should preserve the incremented consecutive pass count");
                }
                break;
            case PriorityTransitionOutcome::StackResolved:
                if (record.stack_resolution_record_index == 0U || record.stack_resolution_record_index > game.stack_resolution_records.size()) {
                    add_error(out, "priority_transition_record.invalid_stack_resolution_link", prefix + " stack-resolved outcome lacks a valid StackResolutionRecord link");
                } else {
                    const auto& resolution_record = game.stack_resolution_records[record.stack_resolution_record_index - 1U];
                    if (resolution_record.sequence >= record.sequence) {
                        add_error(out, "priority_transition_record.stack_resolution_sequence_order", prefix + " linked StackResolutionRecord was not emitted before the priority transition summary");
                    }
                    if (record.stack_top_before.valid() && resolution_record.stack_object != record.stack_top_before) {
                        add_error(out, "priority_transition_record.stack_resolution_object_mismatch", prefix + " linked StackResolutionRecord resolved a different stack object");
                    }
                }
                if (record.stack_size_before == 0U || record.stack_size_after >= record.stack_size_before) {
                    add_error(out, "priority_transition_record.stack_resolved_size_mismatch", prefix + " stack-resolved outcome did not reduce stack size");
                }
                if (record.consecutive_passes_after != 0U) {
                    add_error(out, "priority_transition_record.stack_resolved_passes_not_reset", prefix + " stack-resolved outcome should reset consecutive passes");
                }
                break;
            case PriorityTransitionOutcome::StepAdvanced:
                if (record.stack_resolution_record_index != 0U || record.stack_resolved || record.pending_triggers_put_on_stack) {
                    add_error(out, "priority_transition_record.step_advanced_extra_outcome", prefix + " step advance should not link resolution/trigger outcomes");
                }
                if (record.stack_size_before != 0U || record.stack_size_after != 0U) {
                    add_error(out, "priority_transition_record.step_advanced_nonempty_stack", prefix + " step advance happened with nonempty stack snapshot");
                }
                if (record.step_after == record.step_before) {
                    add_error(out, "priority_transition_record.step_did_not_advance", prefix + " step-advanced outcome kept the same step");
                }
                if (record.consecutive_passes_after != 0U) {
                    add_error(out, "priority_transition_record.step_advanced_passes_not_reset", prefix + " step advance should reset consecutive passes");
                }
                break;
            case PriorityTransitionOutcome::PendingTriggersPutOnStack:
                if (record.pending_triggers_before == 0U) {
                    add_error(out, "priority_transition_record.pending_trigger_outcome_without_pending", prefix + " claims pending triggers were put on stack but none were pending");
                }
                if (record.consecutive_passes_after != 0U) {
                    add_error(out, "priority_transition_record.pending_trigger_passes_not_reset", prefix + " putting pending triggers on stack should reset consecutive passes");
                }
                if (record.stack_resolution_record_index != 0U || record.stack_resolved || record.step_advanced) {
                    add_error(out, "priority_transition_record.pending_trigger_extra_outcome", prefix + " pending-trigger outcome should not also resolve stack or advance step");
                }
                break;
            case PriorityTransitionOutcome::NoAlivePlayers:
                if (record.alive_players != 0U || record.priority_after.valid()) {
                    add_error(out, "priority_transition_record.no_alive_state_mismatch", prefix + " no-alive outcome should have alive_players=0 and no priority_after");
                }
                break;
            case PriorityTransitionOutcome::Count:
                break;
        }
    }

    u64 last_sba_sequence = 0;
    u32 last_sba_check_index = 0;
    u32 last_sba_pass_index = 0;
    u32 last_sba_pass_candidate_count = 0;
    for (std::size_t i = 0; i < game.state_based_action_records.size(); ++i) {
        const auto& record = game.state_based_action_records[i];
        const std::string prefix = "state_based_action_record#" + std::to_string(i + 1U);
        if (record.sequence == 0U) {
            add_error(out, "state_based_action_record.zero_sequence", prefix + " has sequence=0");
        }
        if (record.sequence >= game.next_event_sequence) {
            add_error(out, "state_based_action_record.future_sequence", prefix + " has sequence beyond next_event_sequence");
        }
        if (last_sba_sequence != 0U && record.sequence <= last_sba_sequence) {
            add_error(out, "state_based_action_record.non_monotonic_sequence", prefix + " is not ordered by event sequence");
        }
        last_sba_sequence = record.sequence;
        if (record.check_index == 0U) {
            add_error(out, "state_based_action_record.zero_check_index", prefix + " has check_index=0");
        }
        if (record.pass_index == 0U) {
            add_error(out, "state_based_action_record.zero_pass_index", prefix + " has pass_index=0");
        }
        if (record.pass_candidate_count == 0U) {
            add_error(out, "state_based_action_record.zero_pass_candidate_count", prefix + " has pass_candidate_count=0");
        }
        if (last_sba_check_index != 0U && record.check_index < last_sba_check_index) {
            add_error(out, "state_based_action_record.check_index_regressed", prefix + " has check_index lower than the previous SBA record");
        }
        if (record.check_index != last_sba_check_index) {
            if (record.pass_index != 1U) {
                add_error(out, "state_based_action_record.first_pass_not_one", prefix + " starts a new SBA check without pass_index=1");
            }
            last_sba_check_index = record.check_index;
            last_sba_pass_index = record.pass_index;
            last_sba_pass_candidate_count = record.pass_candidate_count;
        } else {
            if (last_sba_pass_index != 0U && record.pass_index < last_sba_pass_index) {
                add_error(out, "state_based_action_record.pass_index_regressed", prefix + " has pass_index lower than the previous SBA record in the same SBA check");
            }
            if (record.pass_index == last_sba_pass_index && record.pass_candidate_count != last_sba_pass_candidate_count) {
                add_error(out, "state_based_action_record.pass_candidate_count_changed", prefix + " changes pass_candidate_count within the same SBA check/pass");
            }
            if (record.pass_index != last_sba_pass_index) {
                last_sba_pass_index = record.pass_index;
                last_sba_pass_candidate_count = record.pass_candidate_count;
            }
        }
        if (i + 1U < state_based_action_event_links.size() && state_based_action_event_links[i + 1U] != 1U) {
            add_error(out, "state_based_action_record.event_record_link_count", prefix + " should have exactly one typed EventRecord link, found=" + std::to_string(state_based_action_event_links[i + 1U]));
        }
        if (record.kind == StateBasedActionKind::Count || static_cast<u8>(record.kind) >= static_cast<u8>(StateBasedActionKind::Count)) {
            add_error(out, "state_based_action_record.invalid_kind", prefix + " kind=" + std::string(to_string(record.kind)));
        }
        if (record.object.valid()) {
            if (!is_valid_object_ref(game, record.object)) {
                add_error(out, "state_based_action_record.invalid_object", prefix + " object=" + object_ref(record.object));
            }
            if (!is_valid_zone_ref(record.object_zone)) {
                add_error(out, "state_based_action_record.invalid_object_zone", prefix + " object_zone=" + std::string(to_string(record.object_zone)));
            }
            if (record.object_zone_change_index == 0U) {
                add_error(out, "state_based_action_record.missing_object_zone_change_index", prefix + " has an object but no zone-change snapshot");
            }
        } else if (record.kind != StateBasedActionKind::PlayerLost) {
            add_error(out, "state_based_action_record.missing_object", prefix + " has no object for kind=" + std::string(to_string(record.kind)));
        }
        if (record.player.valid() && !is_valid_player_ref(game, record.player)) {
            add_error(out, "state_based_action_record.invalid_player", prefix + " player=" + player_ref(record.player));
        }
        if (record.regeneration_shields_after > record.regeneration_shields_before) {
            add_error(out, "state_based_action_record.regeneration_shields_increased", prefix + " has more regeneration shields after the SBA than before");
        }
        if (record.regeneration_applied && record.kind != StateBasedActionKind::CreatureDamageDestroy) {
            add_error(out, "state_based_action_record.unexpected_regeneration", prefix + " marks regeneration for non-damage-destroy SBA");
        }
        if (record.zone_change_record_index != 0U) {
            if (record.zone_change_record_index > game.zone_change_records.size()) {
                add_error(out, "state_based_action_record.invalid_zone_change_link", prefix + " links invalid zone_change_record_index=" + std::to_string(record.zone_change_record_index));
            } else {
                const auto& zone_record = game.zone_change_records[record.zone_change_record_index - 1U];
                if (zone_record.object != record.object) {
                    add_error(out, "state_based_action_record.zone_change_object_mismatch", prefix + " linked ZoneChangeRecord belongs to a different object");
                }
                if (zone_record.sequence <= record.sequence) {
                    add_error(out, "state_based_action_record.zone_change_sequence_mismatch", prefix + " linked ZoneChangeRecord was not emitted after the SBA record");
                }
                if (zone_record.from_zone != record.object_zone) {
                    add_error(out, "state_based_action_record.zone_change_from_mismatch", prefix + " linked ZoneChangeRecord does not start from the recorded object zone");
                }
                const bool expected_left_battlefield = zone_record.from_zone == Zone::Battlefield && zone_record.to_zone != Zone::Battlefield;
                if (record.object_left_battlefield != expected_left_battlefield) {
                    add_error(out, "state_based_action_record.left_battlefield_mismatch", prefix + " object_left_battlefield flag disagrees with linked ZoneChangeRecord");
                }
            }
        }
        switch (record.kind) {
            case StateBasedActionKind::PlayerLost:
                if (!is_valid_player_ref(game, record.player)) {
                    add_error(out, "state_based_action_record.player_lost_invalid_player", prefix + " does not name a valid losing player");
                }
                if (record.object.valid()) {
                    add_error(out, "state_based_action_record.player_lost_object", prefix + " unexpectedly names an object");
                }
                break;
            case StateBasedActionKind::CounterPairCancel:
                if (record.plus_one_plus_one_counters == 0U || record.minus_one_minus_one_counters == 0U) {
                    add_error(out, "state_based_action_record.counter_pair_without_pair", prefix + " lacks a +1/+1 and -1/-1 pair snapshot");
                }
                if (record.zone_change_record_index != 0U) {
                    add_error(out, "state_based_action_record.counter_pair_zone_change", prefix + " counter-pair cancellation should not link a zone change");
                }
                break;
            case StateBasedActionKind::CreatureToughnessGraveyard:
                if (record.effective_toughness > 0) {
                    add_error(out, "state_based_action_record.positive_toughness_graveyard", prefix + " non-positive-toughness SBA recorded positive toughness");
                }
                if (record.zone_change_record_index == 0U) {
                    add_error(out, "state_based_action_record.missing_zone_change", prefix + " creature graveyard SBA should link a ZoneChangeRecord");
                }
                if (record.regeneration_applied) {
                    add_error(out, "state_based_action_record.toughness_regenerated", prefix + " non-positive toughness cannot be regenerated");
                }
                break;
            case StateBasedActionKind::CreatureDamageDestroy:
                if (record.damage_marked == 0U && !record.deathtouch_damage_marked) {
                    add_error(out, "state_based_action_record.damage_destroy_without_damage", prefix + " damage-destroy SBA lacks marked/deathtouch damage snapshot");
                }
                if (record.zone_change_record_index == 0U && !record.regeneration_applied) {
                    add_error(out, "state_based_action_record.damage_destroy_no_result", prefix + " damage-destroy SBA neither moved the object nor applied regeneration");
                }
                if (record.regeneration_applied && record.regeneration_shields_before <= record.regeneration_shields_after) {
                    add_error(out, "state_based_action_record.regeneration_not_consumed", prefix + " regeneration applied without consuming a shield");
                }
                break;
            case StateBasedActionKind::PlaneswalkerLoyaltyGraveyard:
                if (record.loyalty_counters != 0U) {
                    add_error(out, "state_based_action_record.nonzero_loyalty_graveyard", prefix + " zero-loyalty SBA recorded nonzero loyalty");
                }
                if (record.zone_change_record_index == 0U) {
                    add_error(out, "state_based_action_record.missing_zone_change", prefix + " planeswalker graveyard SBA should link a ZoneChangeRecord");
                }
                break;
            case StateBasedActionKind::BattleDefenseGraveyard:
                if (record.defense_counters != 0U) {
                    add_error(out, "state_based_action_record.nonzero_defense_graveyard", prefix + " zero-defense SBA recorded nonzero defense");
                }
                if (record.zone_change_record_index == 0U) {
                    add_error(out, "state_based_action_record.missing_zone_change", prefix + " battle graveyard SBA should link a ZoneChangeRecord");
                }
                break;
            case StateBasedActionKind::AttachmentUnattach:
                if (!record.attachment_detached) {
                    add_error(out, "state_based_action_record.attachment_not_detached", prefix + " attachment-unattach SBA did not mark the attachment detached");
                }
                if (record.zone_change_record_index != 0U) {
                    add_error(out, "state_based_action_record.attachment_unattach_zone_change", prefix + " equipment/fortification unattach SBA should not link a zone change");
                }
                break;
            case StateBasedActionKind::AuraGraveyard:
                if (record.zone_change_record_index == 0U) {
                    add_error(out, "state_based_action_record.missing_zone_change", prefix + " Aura graveyard SBA should link a ZoneChangeRecord");
                }
                break;
            case StateBasedActionKind::TokenCease:
                if (!record.token_ceased) {
                    add_error(out, "state_based_action_record.token_not_ceased", prefix + " token-cease SBA did not mark the token ceased");
                }
                if (record.zone_change_record_index != 0U) {
                    add_error(out, "state_based_action_record.token_cease_zone_change", prefix + " token-cease SBA should not link a ZoneChangeRecord");
                }
                break;
            case StateBasedActionKind::Count:
                break;
        }
    }


    return out;
}

void assert_valid_game_state(const GameState& game) {
    const auto violations = validate_game_state(game);
    std::ostringstream message;
    bool has_error = false;
    for (const auto& violation : violations) {
        if (violation.severity == ViolationSeverity::Error) {
            has_error = true;
        }
        message << to_string(violation.severity) << " " << violation.code << ": " << violation.detail << "\n";
    }
    if (has_error) {
        throw std::logic_error(message.str());
    }
}

} // namespace mtgsim
