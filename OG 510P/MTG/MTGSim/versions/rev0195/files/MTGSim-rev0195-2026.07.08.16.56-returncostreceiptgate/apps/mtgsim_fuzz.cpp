#include "mtgsim/engine.hpp"
#include "mtgsim/rng.hpp"
#include "mtgsim/validation.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

enum class FuzzProfile {
    Broad,
    RiskSeams
};

const char* profile_name(FuzzProfile profile) noexcept {
    switch (profile) {
        case FuzzProfile::Broad:
            return "broad";
        case FuzzProfile::RiskSeams:
            return "risk-seams";
    }
    return "broad";
}

FuzzProfile parse_profile_name(const std::string& value) {
    if (value == "broad") {
        return FuzzProfile::Broad;
    }
    if (value == "risk-seams") {
        return FuzzProfile::RiskSeams;
    }
    throw std::invalid_argument("invalid --profile=" + value + " (expected broad or risk-seams)");
}

struct Options {
    std::uint64_t seed = 7000;
    std::uint32_t steps = 120;
    FuzzProfile profile = FuzzProfile::Broad;
    bool require_risk_seams = false;
    bool json = false;
};

constexpr std::uint32_t fuzz_saproling_definition_index = 7;
constexpr std::uint32_t fuzz_warden_definition_index = 11;
constexpr std::uint32_t fuzz_artist_definition_index = 12;
constexpr std::uint32_t fuzz_walker_definition_index = 13;


std::uint64_t parse_u64(const char* value, const char* name) {
    char* end = nullptr;
    const unsigned long long parsed = std::strtoull(value, &end, 10);
    if (end == value || *end != '\0') {
        throw std::invalid_argument(std::string("invalid ") + name + "=" + value);
    }
    return static_cast<std::uint64_t>(parsed);
}

std::uint32_t parse_u32(const char* value, const char* name) {
    const std::uint64_t parsed = parse_u64(value, name);
    if (parsed > 100000000ULL) {
        throw std::invalid_argument(std::string(name) + " is too large");
    }
    return static_cast<std::uint32_t>(parsed);
}

Options parse_args(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--seed" && i + 1 < argc) {
            options.seed = parse_u64(argv[++i], "--seed");
        } else if (arg == "--steps" && i + 1 < argc) {
            options.steps = parse_u32(argv[++i], "--steps");
        } else if (arg == "--profile" && i + 1 < argc) {
            options.profile = parse_profile_name(argv[++i]);
        } else if (arg == "--require-risk-seams") {
            options.require_risk_seams = true;
        } else if (arg == "--json") {
            options.json = true;
        } else if (arg == "--help") {
            std::cout << "usage: mtgsim_fuzz [--seed N] [--steps N] [--profile broad|risk-seams] [--require-risk-seams] [--json]\n";
            std::exit(0);
        } else {
            throw std::invalid_argument("unknown argument: " + arg);
        }
    }
    return options;
}

mtgsim::GameState make_fuzz_game(std::uint64_t seed) {
    mtgsim::CardDefinition forest;
    forest.name = "Fuzz Forest";
    forest.type_mask = mtgsim::TypeLand;
    forest.taps_for_mana = true;
    forest.tap_mana_symbol = mtgsim::ManaSymbol::Green;

    mtgsim::CardDefinition mountain;
    mountain.name = "Fuzz Mountain";
    mountain.type_mask = mtgsim::TypeLand;
    mountain.taps_for_mana = true;
    mountain.tap_mana_symbol = mtgsim::ManaSymbol::Red;

    mtgsim::CardDefinition bear;
    bear.name = "Fuzz Bear";
    bear.type_mask = mtgsim::TypeCreature;
    bear.printed_power = 2;
    bear.printed_toughness = 2;
    // The fuzz fixture gives seeded creatures haste so short fuzz runs reach combat seams.
    bear.ability_mask = mtgsim::AbilityHaste;
    bear.mana_cost.generic = 1;
    bear.mana_cost.green = 1;
    mtgsim::ActivatedAbilityDefinition cheer;
    cheer.name = "Fuzz cheer";
    cheer.effect_kind = mtgsim::EffectKind::GainLife;
    cheer.effect_amount = 1;
    // Keep release fuzz from being dominated by an always-free optional priority loop.
    cheer.tap_cost = true;
    cheer.target_mask = mtgsim::TargetPlayer;
    bear.activated_abilities.push_back(cheer);

    mtgsim::CardDefinition bolt;
    bolt.name = "Fuzz Bolt";
    bolt.type_mask = mtgsim::TypeInstant;
    bolt.mana_cost.red = 1;
    bolt.effect_kind = mtgsim::EffectKind::DealDamage;
    bolt.effect_amount = 3;
    bolt.target_mask = mtgsim::TargetAny;

    mtgsim::CardDefinition growth;
    growth.name = "Fuzz Growth";
    growth.type_mask = mtgsim::TypeSorcery;
    growth.mana_cost.green = 1;
    growth.effect_kind = mtgsim::EffectKind::AddCounters;
    growth.effect_counter_kind = mtgsim::CounterKind::PlusOnePlusOne;
    growth.effect_amount = 1;
    growth.target_mask = mtgsim::TargetObject;

    mtgsim::CardDefinition doom;
    doom.name = "Fuzz Doom";
    doom.type_mask = mtgsim::TypeSorcery;
    doom.mana_cost.red = 1;
    doom.effect_kind = mtgsim::EffectKind::DestroyPermanent;
    doom.effect_amount = 1;
    doom.target_mask = mtgsim::TargetObject;

    mtgsim::CardDefinition mend;
    mend.name = "Fuzz Mend";
    mend.type_mask = mtgsim::TypeInstant;
    mend.mana_cost.green = 1;
    mend.effect_kind = mtgsim::EffectKind::RegeneratePermanent;
    mend.effect_amount = 1;
    mend.target_mask = mtgsim::TargetObject;

    mtgsim::CardDefinition saproling;
    saproling.name = "Fuzz Saproling Token";
    saproling.type_mask = mtgsim::TypeCreature;
    saproling.printed_power = 1;
    saproling.printed_toughness = 1;
    saproling.color_mask = mtgsim::ColorGreen;
    saproling.ability_mask = mtgsim::AbilityHaste;

    mtgsim::CardDefinition sprout;
    sprout.name = "Fuzz Sprout";
    sprout.type_mask = mtgsim::TypeSorcery;
    sprout.mana_cost.green = 1;
    sprout.effect_kind = mtgsim::EffectKind::CreateToken;
    sprout.effect_amount = 1;
    sprout.created_token_definition_index = fuzz_saproling_definition_index;

    mtgsim::CardDefinition banish;
    banish.name = "Fuzz Banish";
    banish.type_mask = mtgsim::TypeSorcery;
    banish.mana_cost.red = 1;
    banish.effect_kind = mtgsim::EffectKind::ExilePermanent;
    banish.effect_amount = 1;
    banish.target_mask = mtgsim::TargetObject;

    mtgsim::CardDefinition steal;
    steal.name = "Fuzz Steal";
    steal.type_mask = mtgsim::TypeSorcery;
    steal.mana_cost.red = 1;
    steal.effect_kind = mtgsim::EffectKind::GainControlPermanent;
    steal.effect_amount = 1;
    steal.target_mask = mtgsim::TargetObject;

    mtgsim::CardDefinition warden;
    warden.name = "Fuzz Warden";
    warden.type_mask = mtgsim::TypeCreature;
    warden.printed_power = 1;
    warden.printed_toughness = 3;
    warden.color_mask = mtgsim::ColorGreen;
    warden.trigger.event = mtgsim::TriggerEventKind::CreatureEntersBattlefield;
    warden.trigger.effect_kind = mtgsim::EffectKind::GainLife;
    warden.trigger.effect_amount = 1;
    warden.trigger.exclude_source = true;

    mtgsim::CardDefinition artist;
    artist.name = "Fuzz Artist";
    artist.type_mask = mtgsim::TypeCreature;
    artist.printed_power = 0;
    artist.printed_toughness = 1;
    artist.color_mask = mtgsim::ColorBlack;
    artist.trigger.event = mtgsim::TriggerEventKind::CreatureDies;
    artist.trigger.effect_kind = mtgsim::EffectKind::GainLife;
    artist.trigger.effect_amount = 1;
    artist.trigger.exclude_source = true;

    mtgsim::CardDefinition walker;
    walker.name = "Fuzz Walker";
    walker.type_mask = mtgsim::TypePlaneswalker;
    walker.printed_loyalty = 4;
    walker.color_mask = mtgsim::ColorBlue;
    walker.loyalty_ability.cost = 1;
    walker.loyalty_ability.effect_kind = mtgsim::EffectKind::DealDamage;
    walker.loyalty_ability.effect_amount = 1;
    walker.loyalty_ability.target_mask = mtgsim::TargetAny;

    std::vector<mtgsim::CardDefinition> defs = {forest, mountain, bear, bolt, growth, doom, mend, saproling, sprout, banish, steal, warden, artist, walker};
    std::vector<mtgsim::PlayerDeck> decks = {
        {"Alpha", {0, 1, 11, 13, 2, 3, 4, 5, 6, 8, 9, 10, 12, 2, 3, 0, 1}},
        {"Beta", {0, 1, 11, 13, 2, 3, 4, 5, 6, 8, 9, 10, 12, 2, 3, 0, 1}}
    };
    return mtgsim::make_game(std::move(defs), decks, seed);
}

bool object_has_any_type(const mtgsim::GameState& game, mtgsim::ObjectId id, mtgsim::u32 type_mask) {
    return (mtgsim::object_type_mask(game, id) & type_mask) != 0U;
}

void seed_battlefield_by_type(mtgsim::GameState& game, mtgsim::PlayerId player_id, mtgsim::u32 type_mask, std::uint32_t count) {
    std::vector<mtgsim::ObjectId> chosen;
    for (const auto id : mtgsim::zone(game, player_id, mtgsim::Zone::Library)) {
        if (object_has_any_type(game, id, type_mask)) {
            chosen.push_back(id);
            if (chosen.size() >= static_cast<std::size_t>(count)) {
                break;
            }
        }
    }
    for (const auto id : chosen) {
        if (mtgsim::object(game, id).zone == mtgsim::Zone::Library) {
            mtgsim::move_object(game, id, player_id, mtgsim::Zone::Battlefield);
        }
    }
}

bool seed_battlefield_by_definition(mtgsim::GameState& game, mtgsim::PlayerId player_id, std::uint32_t definition_index) {
    for (const auto& obj : game.objects) {
        if (obj.owner == player_id && obj.definition_index == definition_index &&
            obj.zone == mtgsim::Zone::Battlefield && !obj.ceased_to_exist) {
            return true;
        }
    }
    for (const auto& obj : game.objects) {
        if (obj.owner == player_id && obj.definition_index == definition_index &&
            obj.zone != mtgsim::Zone::Battlefield && obj.zone != mtgsim::Zone::Stack && !obj.ceased_to_exist) {
            mtgsim::move_object(game, obj.id, player_id, mtgsim::Zone::Battlefield);
            return true;
        }
    }
    return false;
}

void configure_risk_seam_fixture(mtgsim::GameState& game) {
    for (const auto player_id : {mtgsim::PlayerId{1}, mtgsim::PlayerId{2}}) {
        (void)seed_battlefield_by_definition(game, player_id, fuzz_warden_definition_index);
        (void)seed_battlefield_by_definition(game, player_id, fuzz_artist_definition_index);
        (void)seed_battlefield_by_definition(game, player_id, fuzz_walker_definition_index);
    }
    game.step = mtgsim::Step::Main1;
    game.active_player = mtgsim::PlayerId{1};
    game.priority_player = mtgsim::PlayerId{1};
    game.consecutive_priority_passes = 0;
}

struct Counters {
    std::uint32_t steps_executed = 0;
    std::uint32_t applied_actions = 0;
    std::uint32_t pass_actions = 0;
    std::uint32_t cast_actions = 0;
    std::uint32_t land_actions = 0;
    std::uint32_t mana_actions = 0;
    std::uint32_t activated_actions = 0;
    std::uint32_t attack_actions = 0;
    std::uint32_t block_actions = 0;
    std::uint32_t combat_damage_order_actions = 0;
    std::uint32_t trigger_stack_actions = 0;
    std::uint32_t loyalty_actions = 0;
    std::uint32_t forced_advances = 0;
    std::uint32_t invariant_checks = 0;
};

void increment_action_counter(Counters& counters, mtgsim::ActionKind kind) {
    ++counters.applied_actions;
    switch (kind) {
        case mtgsim::ActionKind::PassPriority:
            ++counters.pass_actions;
            break;
        case mtgsim::ActionKind::CastSpellFromHandPaid:
            ++counters.cast_actions;
            break;
        case mtgsim::ActionKind::PlayLand:
            ++counters.land_actions;
            break;
        case mtgsim::ActionKind::ActivateTapManaAbility:
        case mtgsim::ActionKind::ActivateManaAbility:
            ++counters.mana_actions;
            break;
        case mtgsim::ActionKind::ActivateActivatedAbility:
            ++counters.activated_actions;
            break;
        case mtgsim::ActionKind::DeclareAttacker:
            ++counters.attack_actions;
            break;
        case mtgsim::ActionKind::DeclareBlocker:
            ++counters.block_actions;
            break;
        case mtgsim::ActionKind::OrderCombatDamage:
            ++counters.combat_damage_order_actions;
            break;
        case mtgsim::ActionKind::PutPendingTriggersOnStack:
            ++counters.trigger_stack_actions;
            break;
        case mtgsim::ActionKind::ActivateLoyaltyAbility:
            ++counters.loyalty_actions;
            break;
        case mtgsim::ActionKind::Count:
            break;
    }
}

std::optional<std::size_t> random_action_of_kind(
    const std::vector<mtgsim::LegalAction>& actions,
    mtgsim::ActionKind kind,
    mtgsim::SplitMix64& rng) {
    std::vector<std::size_t> matches;
    for (std::size_t index = 0; index < actions.size(); ++index) {
        if (actions[index].kind == kind) {
            matches.push_back(index);
        }
    }
    if (matches.empty()) {
        return std::nullopt;
    }
    return matches[static_cast<std::size_t>(rng.uniform_u32(static_cast<std::uint32_t>(matches.size())))];
}

std::optional<std::size_t> random_non_pass_action(
    const std::vector<mtgsim::LegalAction>& actions,
    mtgsim::SplitMix64& rng) {
    std::vector<std::size_t> matches;
    for (std::size_t index = 0; index < actions.size(); ++index) {
        if (actions[index].kind != mtgsim::ActionKind::PassPriority) {
            matches.push_back(index);
        }
    }
    if (matches.empty()) {
        return std::nullopt;
    }
    return matches[static_cast<std::size_t>(rng.uniform_u32(static_cast<std::uint32_t>(matches.size())))];
}


std::vector<mtgsim::LegalAction> collect_fuzz_actions(const mtgsim::GameState& game) {
    std::vector<mtgsim::LegalAction> actions;
    if (game.priority_player.valid()) {
        actions = mtgsim::enumerate_legal_actions(game, game.priority_player);
    }
    if (game.step == mtgsim::Step::DeclareBlockers && game.stack.empty()) {
        for (const auto& candidate_player : game.players) {
            if (candidate_player.lost || candidate_player.id == game.priority_player) {
                continue;
            }
            const auto extra = mtgsim::enumerate_legal_actions(game, candidate_player.id);
            for (const auto& action : extra) {
                if (action.kind == mtgsim::ActionKind::DeclareBlocker) {
                    actions.push_back(action);
                }
            }
        }
    }
    return actions;
}

std::size_t choose_fuzz_action_index(const std::vector<mtgsim::LegalAction>& actions, mtgsim::SplitMix64& rng, FuzzProfile profile) {
    // Release fuzz is a coverage profile, not a player strategy: prefer visible state-changing
    // seams when they are legal so the budget is not spent mostly on voluntary passes.
    const std::array<mtgsim::ActionKind, 8> broad_priority_kinds = {
        mtgsim::ActionKind::OrderCombatDamage,
        mtgsim::ActionKind::DeclareBlocker,
        mtgsim::ActionKind::DeclareAttacker,
        mtgsim::ActionKind::PlayLand,
        mtgsim::ActionKind::CastSpellFromHandPaid,
        mtgsim::ActionKind::PutPendingTriggersOnStack,
        mtgsim::ActionKind::ActivateLoyaltyAbility,
        mtgsim::ActionKind::ActivateActivatedAbility,
    };
    const std::array<mtgsim::ActionKind, 8> risk_priority_kinds = {
        mtgsim::ActionKind::OrderCombatDamage,
        mtgsim::ActionKind::PutPendingTriggersOnStack,
        mtgsim::ActionKind::ActivateLoyaltyAbility,
        mtgsim::ActionKind::ActivateActivatedAbility,
        mtgsim::ActionKind::CastSpellFromHandPaid,
        mtgsim::ActionKind::PlayLand,
        mtgsim::ActionKind::DeclareAttacker,
        mtgsim::ActionKind::DeclareBlocker,
    };
    const auto& priority_kinds = profile == FuzzProfile::RiskSeams ? risk_priority_kinds : broad_priority_kinds;
    for (const auto kind : priority_kinds) {
        if (const auto match = random_action_of_kind(actions, kind, rng)) {
            return *match;
        }
    }
    if (const auto non_pass = random_non_pass_action(actions, rng)) {
        return *non_pass;
    }
    return static_cast<std::size_t>(rng.uniform_u32(static_cast<std::uint32_t>(actions.size())));
}

Counters run_fuzz(mtgsim::GameState& game, std::uint64_t seed, std::uint32_t steps, FuzzProfile profile) {
    mtgsim::StartOptions opts;
    opts.opening_hand_size = 3;
    opts.shuffle_libraries = true;
    mtgsim::start_game(game, opts);
    seed_battlefield_by_type(game, mtgsim::PlayerId{1}, mtgsim::TypeLand, 2);
    seed_battlefield_by_type(game, mtgsim::PlayerId{2}, mtgsim::TypeLand, 2);
    seed_battlefield_by_type(game, mtgsim::PlayerId{1}, mtgsim::TypeCreature, 1);
    seed_battlefield_by_type(game, mtgsim::PlayerId{2}, mtgsim::TypeCreature, 1);
    if (profile == FuzzProfile::RiskSeams) {
        configure_risk_seam_fixture(game);
    }
    // Seed a stable pair of hasty token bodies so short release fuzz reaches both
    // attacker and blocker seams even when shuffled hands draw the creature cards.
    // In the risk-seams profile, creating these after the Warden fixture also
    // guarantees pending trigger-stack work inside the first few actions.
    (void)mtgsim::create_tokens(game, mtgsim::PlayerId{1}, fuzz_saproling_definition_index, 2);
    (void)mtgsim::create_tokens(game, mtgsim::PlayerId{2}, fuzz_saproling_definition_index, 2);

    mtgsim::SplitMix64 rng(seed ^ 0x9e3779b97f4a7c15ULL);
    Counters counters;
    for (std::uint32_t step = 0; step < steps; ++step) {
        mtgsim::apply_state_based_actions(game);
        mtgsim::assert_valid_game_state(game);
        ++counters.invariant_checks;

        if (!game.priority_player.valid() || mtgsim::alive_player_count(game) == 0U) {
            mtgsim::advance_step(game);
            ++counters.forced_advances;
            ++counters.steps_executed;
            continue;
        }

        const auto actions = collect_fuzz_actions(game);
        if (actions.empty()) {
            mtgsim::advance_step(game);
            ++counters.forced_advances;
            ++counters.steps_executed;
            continue;
        }
        const auto index = choose_fuzz_action_index(actions, rng, profile);
        const auto action = actions[index];
        const bool applied = mtgsim::apply_action(game, action);
        if (!applied) {
            throw std::logic_error("enumerated action was rejected by apply_action");
        }
        increment_action_counter(counters, action.kind);
        ++counters.steps_executed;
    }
    mtgsim::apply_state_based_actions(game);
    mtgsim::assert_valid_game_state(game);
    ++counters.invariant_checks;
    return counters;
}

} // namespace

int main(int argc, char** argv) {
    try {
        const auto options = parse_args(argc, argv);
        auto game = make_fuzz_game(options.seed);
        const auto begin = std::chrono::steady_clock::now();
        const auto counters = run_fuzz(game, options.seed, options.steps, options.profile);
        if (options.require_risk_seams && (counters.trigger_stack_actions == 0U || counters.loyalty_actions == 0U)) {
            throw std::logic_error("required risk seams were not exercised by this seed");
        }
        const auto end = std::chrono::steady_clock::now();
        const double duration = static_cast<double>(std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count()) / 1000000.0;
        if (options.json) {
            std::cout << "{\"schema\":\"mtgsim.fuzz_binary_report.v1\",";
            std::cout << "\"status\":\"passed\",";
            std::cout << "\"profile\":\"" << profile_name(options.profile) << "\",";
            std::cout << "\"seed\":" << options.seed << ",";
            std::cout << "\"duration_sec\":" << duration << ",";
            std::cout << "\"steps_requested\":" << options.steps << ",";
            std::cout << "\"steps_executed\":" << counters.steps_executed << ",";
            std::cout << "\"applied_actions\":" << counters.applied_actions << ",";
            std::cout << "\"pass_actions\":" << counters.pass_actions << ",";
            std::cout << "\"cast_actions\":" << counters.cast_actions << ",";
            std::cout << "\"land_actions\":" << counters.land_actions << ",";
            std::cout << "\"mana_actions\":" << counters.mana_actions << ",";
            std::cout << "\"activated_actions\":" << counters.activated_actions << ",";
            std::cout << "\"attack_actions\":" << counters.attack_actions << ",";
            std::cout << "\"block_actions\":" << counters.block_actions << ",";
            std::cout << "\"combat_damage_order_actions\":" << counters.combat_damage_order_actions << ",";
            std::cout << "\"trigger_stack_actions\":" << counters.trigger_stack_actions << ",";
            std::cout << "\"loyalty_actions\":" << counters.loyalty_actions << ",";
            std::cout << "\"forced_advances\":" << counters.forced_advances << ",";
            std::cout << "\"invariant_checks\":" << counters.invariant_checks << ",";
            std::cout << "\"event_count\":" << game.events.size() << ",";
            std::cout << "\"alive_players\":" << mtgsim::alive_player_count(game) << "}\n";
        } else {
            std::cout << "fuzz seed=" << options.seed << " profile=" << profile_name(options.profile) << " status=passed steps=" << counters.steps_executed
                      << " actions=" << counters.applied_actions
                      << " land_actions=" << counters.land_actions
                      << " activated_actions=" << counters.activated_actions
                      << " loyalty_actions=" << counters.loyalty_actions
                      << " combat_damage_order_actions=" << counters.combat_damage_order_actions
                      << " time=" << duration << "s\n";
        }
        return 0;
    } catch (const std::exception& exc) {
        std::cerr << "mtgsim_fuzz: " << exc.what() << "\n";
        return 2;
    }
}
