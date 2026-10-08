#include "mtgsim/engine.hpp"
#include "mtgsim/validation.hpp"

#include <algorithm>
#include <chrono>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

struct ScenarioFailure : std::runtime_error {
    using std::runtime_error::runtime_error;
};

std::string trim(std::string value) {
    auto not_space = [](unsigned char ch) { return !std::isspace(ch); };
    value.erase(value.begin(), std::find_if(value.begin(), value.end(), not_space));
    value.erase(std::find_if(value.rbegin(), value.rend(), not_space).base(), value.end());
    return value;
}

std::vector<std::string> split_ws(const std::string& line) {
    std::istringstream in(line);
    std::vector<std::string> out;
    std::string token;
    while (in >> token) {
        out.push_back(token);
    }
    return out;
}

std::vector<std::string> split_on(std::string_view value, char sep) {
    std::vector<std::string> out;
    std::string current;
    for (char ch : value) {
        if (ch == sep) {
            out.push_back(current);
            current.clear();
        } else {
            current.push_back(ch);
        }
    }
    out.push_back(current);
    return out;
}

std::string json_escape(std::string_view value) {
    std::string out;
    out.reserve(value.size() + 8U);
    for (const char ch : value) {
        switch (ch) {
            case '\\': out += "\\\\"; break;
            case '"': out += "\\\""; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(ch) < 0x20U) {
                    out += "?";
                } else {
                    out += ch;
                }
        }
    }
    return out;
}

std::string dequote_name(std::string value) {
    std::replace(value.begin(), value.end(), '_', ' ');
    return value;
}

int parse_int(const std::string& token, std::string_view field) {
    std::size_t consumed = 0;
    const int value = std::stoi(token, &consumed);
    if (consumed != token.size()) {
        throw ScenarioFailure("invalid integer for " + std::string(field) + ": " + token);
    }
    return value;
}

mtgsim::u32 parse_u32(const std::string& token, std::string_view field) {
    const int value = parse_int(token, field);
    if (value < 0) {
        throw ScenarioFailure("negative integer for " + std::string(field) + ": " + token);
    }
    return static_cast<mtgsim::u32>(value);
}

bool parse_bool(const std::string& token) {
    if (token == "true" || token == "1" || token == "yes") {
        return true;
    }
    if (token == "false" || token == "0" || token == "no") {
        return false;
    }
    throw ScenarioFailure("invalid boolean: " + token);
}

std::string option_value(const std::string& token, std::string_view key) {
    const std::string prefix = std::string(key) + "=";
    if (token.rfind(prefix, 0) != 0U) {
        throw ScenarioFailure("expected option " + prefix + "..., got " + token);
    }
    return token.substr(prefix.size());
}

mtgsim::ManaSymbol parse_mana_symbol(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (value == "w" || value == "white") return mtgsim::ManaSymbol::White;
    if (value == "u" || value == "blue") return mtgsim::ManaSymbol::Blue;
    if (value == "b" || value == "black") return mtgsim::ManaSymbol::Black;
    if (value == "r" || value == "red") return mtgsim::ManaSymbol::Red;
    if (value == "g" || value == "green") return mtgsim::ManaSymbol::Green;
    if (value == "c" || value == "colorless") return mtgsim::ManaSymbol::Colorless;
    throw ScenarioFailure("invalid mana symbol: " + value);
}


mtgsim::u32 parse_color_mask(std::string token) {
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    mtgsim::u32 mask = mtgsim::ColorNone;
    if (token == "-" || token == "none" || token == "colorless") {
        return mask;
    }
    for (const auto& part : split_on(token, ',')) {
        if (part == "w" || part == "white") mask |= mtgsim::ColorWhite;
        else if (part == "u" || part == "blue") mask |= mtgsim::ColorBlue;
        else if (part == "b" || part == "black") mask |= mtgsim::ColorBlack;
        else if (part == "r" || part == "red") mask |= mtgsim::ColorRed;
        else if (part == "g" || part == "green") mask |= mtgsim::ColorGreen;
        else if (part == "all") mask |= mtgsim::ColorAll;
        else throw ScenarioFailure("invalid color: " + part);
    }
    return mask;
}

mtgsim::CounterKind parse_counter_kind(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (value == "+1/+1" || value == "plus1" || value == "plus_one_plus_one" || value == "p1p1") return mtgsim::CounterKind::PlusOnePlusOne;
    if (value == "-1/-1" || value == "minus1" || value == "minus_one_minus_one" || value == "m1m1") return mtgsim::CounterKind::MinusOneMinusOne;
    if (value == "loyalty") return mtgsim::CounterKind::Loyalty;
    if (value == "defense") return mtgsim::CounterKind::Defense;
    if (value == "charge") return mtgsim::CounterKind::Charge;
    if (value == "poison") return mtgsim::CounterKind::Poison;
    throw ScenarioFailure("invalid counter kind: " + value);
}

mtgsim::Zone parse_zone(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (value == "library") return mtgsim::Zone::Library;
    if (value == "hand") return mtgsim::Zone::Hand;
    if (value == "battlefield") return mtgsim::Zone::Battlefield;
    if (value == "graveyard") return mtgsim::Zone::Graveyard;
    if (value == "stack") return mtgsim::Zone::Stack;
    if (value == "exile") return mtgsim::Zone::Exile;
    if (value == "command") return mtgsim::Zone::Command;
    if (value == "ante") return mtgsim::Zone::Ante;
    throw ScenarioFailure("invalid zone: " + value);
}

mtgsim::Step parse_step(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (value == "untap") return mtgsim::Step::Untap;
    if (value == "upkeep") return mtgsim::Step::Upkeep;
    if (value == "draw") return mtgsim::Step::Draw;
    if (value == "main1" || value == "precombat_main" || value == "precombat") return mtgsim::Step::Main1;
    if (value == "beginning_of_combat" || value == "begincombat") return mtgsim::Step::BeginningOfCombat;
    if (value == "declare_attackers" || value == "attackers") return mtgsim::Step::DeclareAttackers;
    if (value == "declare_blockers" || value == "blockers") return mtgsim::Step::DeclareBlockers;
    if (value == "combat_damage" || value == "damage") return mtgsim::Step::CombatDamage;
    if (value == "end_of_combat" || value == "endcombat") return mtgsim::Step::EndOfCombat;
    if (value == "main2" || value == "postcombat_main" || value == "postcombat") return mtgsim::Step::Main2;
    if (value == "end") return mtgsim::Step::End;
    if (value == "cleanup") return mtgsim::Step::Cleanup;
    throw ScenarioFailure("invalid step: " + value);
}

mtgsim::u32 parse_type_mask(std::string token) {
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    mtgsim::u32 mask = mtgsim::TypeNone;
    for (const auto& part : split_on(token, ',')) {
        if (part == "any" || part == "permanent" || part == "permanents") mask |= mtgsim::TypeArtifact | mtgsim::TypeBattle | mtgsim::TypeCreature | mtgsim::TypeEnchantment | mtgsim::TypeLand | mtgsim::TypePlaneswalker;
        else if (part == "artifact") mask |= mtgsim::TypeArtifact;
        else if (part == "battle") mask |= mtgsim::TypeBattle;
        else if (part == "creature") mask |= mtgsim::TypeCreature;
        else if (part == "enchantment") mask |= mtgsim::TypeEnchantment;
        else if (part == "instant") mask |= mtgsim::TypeInstant;
        else if (part == "kindred") mask |= mtgsim::TypeKindred;
        else if (part == "land") mask |= mtgsim::TypeLand;
        else if (part == "planeswalker") mask |= mtgsim::TypePlaneswalker;
        else if (part == "sorcery") mask |= mtgsim::TypeSorcery;
        else if (part == "none") mask |= mtgsim::TypeNone;
        else throw ScenarioFailure("invalid card type: " + part);
    }
    return mask;
}

struct TargetSpec {
    mtgsim::u32 mask = mtgsim::TargetNone;
    mtgsim::u32 count = 0;
};

TargetSpec parse_target_spec(std::string token) {
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    mtgsim::u32 count = 0;
    const auto star = token.find('*');
    if (star != std::string::npos) {
        count = parse_u32(token.substr(star + 1U), "target count");
        token = token.substr(0U, star);
    }
    mtgsim::u32 mask = mtgsim::TargetNone;
    if (token == "-" || token == "none") mask = mtgsim::TargetNone;
    else if (token == "player" || token == "players") mask = mtgsim::TargetPlayer;
    else if (token == "object" || token == "permanent") mask = mtgsim::TargetObject;
    else if (token == "stack" || token == "spell" || token == "stack_object") mask = mtgsim::TargetStackObject;
    else if (token == "any" || token == "anytarget") mask = mtgsim::TargetAny;
    else throw ScenarioFailure("invalid target mask: " + token);
    if (mask == mtgsim::TargetNone && count != 0U) {
        throw ScenarioFailure("target count requires a non-none target mask");
    }
    return TargetSpec{.mask = mask, .count = count};
}

void apply_target_spec(mtgsim::u32& mask, mtgsim::u32& count, std::string token) {
    const auto spec = parse_target_spec(std::move(token));
    mask = spec.mask;
    count = spec.count;
}

mtgsim::AttachmentKind parse_attachment_kind(std::string token) {
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (token == "-" || token == "none") return mtgsim::AttachmentKind::None;
    if (token == "aura") return mtgsim::AttachmentKind::Aura;
    if (token == "equipment" || token == "equip") return mtgsim::AttachmentKind::Equipment;
    if (token == "fortification" || token == "fortify") return mtgsim::AttachmentKind::Fortification;
    throw ScenarioFailure("invalid attachment kind: " + token);
}

void apply_attachment_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.empty() || parts.size() > 2U) {
        throw ScenarioFailure("attachment option expects KIND[:TARGET_MASK]");
    }
    def.attachment_kind = parse_attachment_kind(parts[0]);
    if (parts.size() == 2U) {
        apply_target_spec(def.target_mask, def.target_count, parts[1]);
    } else if (def.attachment_kind == mtgsim::AttachmentKind::Aura && def.target_mask == mtgsim::TargetNone) {
        def.target_mask = mtgsim::TargetObject;
    }
}

std::pair<int, int> parse_power_toughness_pair(std::string token) {
    std::replace(token.begin(), token.end(), '/', ',');
    const auto parts = split_on(token, ',');
    if (parts.size() != 2U) {
        throw ScenarioFailure("P/T pair expects POWER/TOUGHNESS");
    }
    return {parse_int(parts[0], "power bonus"), parse_int(parts[1], "toughness bonus")};
}

mtgsim::KeywordAbilityMask parse_keyword_ability(std::string token) {
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (token == "flying") return mtgsim::AbilityFlying;
    if (token == "reach") return mtgsim::AbilityReach;
    if (token == "deathtouch") return mtgsim::AbilityDeathtouch;
    if (token == "lifelink") return mtgsim::AbilityLifelink;
    if (token == "vigilance") return mtgsim::AbilityVigilance;
    if (token == "firststrike" || token == "first_strike") return mtgsim::AbilityFirstStrike;
    if (token == "doublestrike" || token == "double_strike") return mtgsim::AbilityDoubleStrike;
    if (token == "trample") return mtgsim::AbilityTrample;
    if (token == "indestructible") return mtgsim::AbilityIndestructible;
    if (token == "haste") return mtgsim::AbilityHaste;
    if (token == "defender") return mtgsim::AbilityDefender;
    if (token == "hexproof") return mtgsim::AbilityHexproof;
    if (token == "shroud") return mtgsim::AbilityShroud;
    if (token == "menace") return mtgsim::AbilityMenace;
    if (token == "flash") return mtgsim::AbilityFlash;
    if (token == "none" || token == "-") return mtgsim::AbilityNone;
    throw ScenarioFailure("invalid keyword ability: " + token);
}

mtgsim::u32 parse_ability_mask(std::string token) {
    mtgsim::u32 mask = mtgsim::AbilityNone;
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    for (const auto& part : split_on(token, ',')) {
        const auto ability = parse_keyword_ability(part);
        mask |= static_cast<mtgsim::u32>(ability);
    }
    return mask;
}

std::vector<std::string> parse_dependency_names(std::string token) {
    std::vector<std::string> out;
    if (token == "-" || token == "none") {
        return out;
    }
    for (auto part : split_on(token, ',')) {
        part = dequote_name(trim(part));
        if (!part.empty()) {
            out.push_back(part);
        }
    }
    return out;
}

mtgsim::StaticEffectScope parse_static_effect_scope(std::string token) {
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (token == "source" || token == "self") return mtgsim::StaticEffectScope::Source;
    if (token == "creatures_you_control" || token == "your_creatures" || token == "controller_creatures") return mtgsim::StaticEffectScope::CreaturesYouControl;
    if (token == "creatures_opponents_control" || token == "opponent_creatures" || token == "opponents_creatures") return mtgsim::StaticEffectScope::CreaturesOpponentsControl;
    if (token == "all_creatures" || token == "creatures") return mtgsim::StaticEffectScope::AllCreatures;
    if (token == "permanents_you_control" || token == "your_permanents" || token == "controller_permanents") return mtgsim::StaticEffectScope::PermanentsYouControl;
    if (token == "permanents_opponents_control" || token == "opponent_permanents" || token == "opponents_permanents") return mtgsim::StaticEffectScope::PermanentsOpponentsControl;
    if (token == "all_permanents" || token == "permanents") return mtgsim::StaticEffectScope::AllPermanents;
    if (token == "none" || token == "-") return mtgsim::StaticEffectScope::None;
    throw ScenarioFailure("invalid static-effect scope: " + token);
}

void apply_static_effect_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() < 4U) {
        throw ScenarioFailure("static option expects NAME:SCOPE:POWER/TOUGHNESS:ABILITIES[:TYPES][:add_types=TYPES][:remove_types=TYPES][:set_color=COLORS][:add_color=COLORS][:remove_color=COLORS][:set_pt=P/T][:remove_abilities=A,B][:depends=NAME[,NAME]]");
    }
    mtgsim::StaticEffectDefinition effect;
    effect.name = dequote_name(parts[0]);
    effect.scope = parse_static_effect_scope(parts[1]);
    const auto pt = parse_power_toughness_pair(parts[2]);
    effect.power_modifier = pt.first;
    effect.toughness_modifier = pt.second;
    effect.granted_ability_mask = parse_ability_mask(parts[3]);
    std::size_t option_start = 4U;
    if (parts.size() >= 5U && parts[4].find('=') == std::string::npos) {
        effect.affected_type_mask = parse_type_mask(parts[4]);
        option_start = 5U;
    } else {
        effect.affected_type_mask = mtgsim::TypeCreature;
    }
    for (std::size_t i = option_start; i < parts.size(); ++i) {
        const auto& part = parts[i];
        if (part.rfind("add_types=", 0) == 0U) {
            effect.added_type_mask = parse_type_mask(option_value(part, "add_types"));
        } else if (part.rfind("remove_types=", 0) == 0U) {
            effect.removed_type_mask = parse_type_mask(option_value(part, "remove_types"));
        } else if (part.rfind("set_color=", 0) == 0U) {
            effect.sets_color = true;
            effect.set_color_mask = parse_color_mask(option_value(part, "set_color"));
        } else if (part.rfind("add_color=", 0) == 0U) {
            effect.added_color_mask = parse_color_mask(option_value(part, "add_color"));
        } else if (part.rfind("remove_color=", 0) == 0U) {
            effect.removed_color_mask = parse_color_mask(option_value(part, "remove_color"));
        } else if (part.rfind("set_pt=", 0) == 0U) {
            const auto set_pt_pair = parse_power_toughness_pair(option_value(part, "set_pt"));
            effect.sets_power_toughness = true;
            effect.set_power = set_pt_pair.first;
            effect.set_toughness = set_pt_pair.second;
        } else if (part.rfind("base_pt=", 0) == 0U) {
            const auto set_pt_pair = parse_power_toughness_pair(option_value(part, "base_pt"));
            effect.sets_power_toughness = true;
            effect.set_power = set_pt_pair.first;
            effect.set_toughness = set_pt_pair.second;
        } else if (part.rfind("remove_abilities=", 0) == 0U) {
            effect.removed_ability_mask = parse_ability_mask(option_value(part, "remove_abilities"));
        } else if (part.rfind("remove_keywords=", 0) == 0U) {
            effect.removed_ability_mask = parse_ability_mask(option_value(part, "remove_keywords"));
        } else if (part.rfind("depends=", 0) == 0U) {
            effect.depends_on_effect_names = parse_dependency_names(option_value(part, "depends"));
        } else {
            throw ScenarioFailure("unknown static effect option: " + part);
        }
    }
    if (!effect.active()) {
        throw ScenarioFailure("static effect must modify type, color, P/T, grant an ability, remove an ability, or set base P/T");
    }
    def.static_effects.push_back(std::move(effect));
}


void apply_zone_change_replacement_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() < 5U) {
        throw ScenarioFailure("replacement option expects NAME:SCOPE:FROM_ZONE:TO_ZONE:REPLACEMENT_ZONE[:TYPES][:choice=N]");
    }
    mtgsim::ZoneChangeReplacementDefinition replacement;
    replacement.name = dequote_name(parts[0]);
    replacement.scope = parse_static_effect_scope(parts[1]);
    replacement.from_zone = parse_zone(parts[2]);
    replacement.to_zone = parse_zone(parts[3]);
    replacement.replacement_zone = parse_zone(parts[4]);
    replacement.affected_type_mask = mtgsim::TypeCreature;
    bool saw_type_filter = false;
    for (std::size_t i = 5; i < parts.size(); ++i) {
        const auto& part = parts[i];
        if (part.rfind("choice=", 0) == 0U) {
            replacement.choice_rank = parse_u32(option_value(part, "choice"), "replacement choice rank");
        } else if (part.rfind("priority=", 0) == 0U) {
            replacement.choice_rank = parse_u32(option_value(part, "priority"), "replacement choice rank");
        } else if (!saw_type_filter) {
            replacement.affected_type_mask = parse_type_mask(part);
            saw_type_filter = true;
        } else {
            throw ScenarioFailure("unknown zone-change replacement option: " + part);
        }
    }
    if (!replacement.active()) {
        throw ScenarioFailure("zone-change replacement must have a scope and replace one destination zone with a different zone");
    }
    def.zone_change_replacements.push_back(std::move(replacement));
}

void apply_continuous_effect_option(mtgsim::CardDefinition& def, std::string token) {
    mtgsim::CardDefinition scratch;
    apply_static_effect_option(scratch, std::move(token));
    if (scratch.static_effects.empty()) {
        throw ScenarioFailure("continuous effect option did not produce an effect");
    }
    def.continuous_effect = std::move(scratch.static_effects.back());
    def.continuous_effect_duration = mtgsim::ContinuousEffectDuration::UntilCleanup;
}

mtgsim::ManaCost parse_cost(std::string token) {
    mtgsim::ManaCost cost;
    if (token == "-" || token == "0" || token == "free") {
        return cost;
    }
    std::size_t i = 0;
    while (i < token.size()) {
        if (std::isdigit(static_cast<unsigned char>(token[i]))) {
            std::size_t j = i;
            while (j < token.size() && std::isdigit(static_cast<unsigned char>(token[j]))) {
                ++j;
            }
            cost.generic += parse_u32(token.substr(i, j - i), "mana cost");
            i = j;
            continue;
        }
        const char ch = static_cast<char>(std::toupper(static_cast<unsigned char>(token[i])));
        switch (ch) {
            case 'W': ++cost.white; break;
            case 'U': ++cost.blue; break;
            case 'B': ++cost.black; break;
            case 'R': ++cost.red; break;
            case 'G': ++cost.green; break;
            case 'C': ++cost.colorless; break;
            default: throw ScenarioFailure("invalid mana cost character: " + std::string(1, token[i]));
        }
        ++i;
    }
    return cost;
}

mtgsim::ManaPool parse_mana_pool_text(std::string token) {
    mtgsim::ManaPool pool;
    if (token == "-" || token == "0" || token == "none") {
        return pool;
    }
    std::size_t i = 0;
    while (i < token.size()) {
        if (std::isdigit(static_cast<unsigned char>(token[i]))) {
            std::size_t j = i;
            while (j < token.size() && std::isdigit(static_cast<unsigned char>(token[j]))) {
                ++j;
            }
            pool.colorless += parse_u32(token.substr(i, j - i), "mana produced");
            i = j;
            continue;
        }
        const char ch = static_cast<char>(std::toupper(static_cast<unsigned char>(token[i])));
        switch (ch) {
            case 'W': ++pool.white; break;
            case 'U': ++pool.blue; break;
            case 'B': ++pool.black; break;
            case 'R': ++pool.red; break;
            case 'G': ++pool.green; break;
            case 'C': ++pool.colorless; break;
            default: throw ScenarioFailure("invalid mana pool character: " + std::string(1, token[i]));
        }
        ++i;
    }
    return pool;
}

mtgsim::EffectKind parse_effect_kind(std::string kind) {
    std::transform(kind.begin(), kind.end(), kind.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (kind == "damage" || kind == "deal_damage") return mtgsim::EffectKind::DealDamage;
    if (kind == "draw") return mtgsim::EffectKind::DrawCards;
    if (kind == "gainlife" || kind == "gain_life") return mtgsim::EffectKind::GainLife;
    if (kind == "counter" || kind == "counters" || kind == "add_counter" || kind == "add_counters") return mtgsim::EffectKind::AddCounters;
    if (kind == "destroy" || kind == "destroy_permanent") return mtgsim::EffectKind::DestroyPermanent;
    if (kind == "regenerate" || kind == "regenerate_permanent") return mtgsim::EffectKind::RegeneratePermanent;
    if (kind == "exile" || kind == "exile_permanent") return mtgsim::EffectKind::ExilePermanent;
    if (kind == "create" || kind == "create_token" || kind == "tokens") return mtgsim::EffectKind::CreateToken;
    if (kind == "control" || kind == "gain_control" || kind == "gain_control_permanent") return mtgsim::EffectKind::GainControlPermanent;
    if (kind == "continuous" || kind == "temp" || kind == "temporary" || kind == "create_continuous") return mtgsim::EffectKind::CreateContinuousEffect;
    if (kind == "copy" || kind == "become_copy" || kind == "become_copy_permanent") return mtgsim::EffectKind::BecomeCopyPermanent;
    if (kind == "counterspell" || kind == "counter_spell" || kind == "counter_stack" || kind == "counter_target_spell") return mtgsim::EffectKind::CounterSpell;
    if (kind == "none" || kind == "-") return mtgsim::EffectKind::None;
    throw ScenarioFailure("invalid effect kind: " + kind);
}

mtgsim::TriggerEventKind parse_trigger_event(std::string kind) {
    std::transform(kind.begin(), kind.end(), kind.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (kind == "creature_etb" || kind == "creature_enters" || kind == "creature_enters_battlefield") return mtgsim::TriggerEventKind::CreatureEntersBattlefield;
    if (kind == "creature_dies" || kind == "dies") return mtgsim::TriggerEventKind::CreatureDies;
    if (kind == "none" || kind == "-") return mtgsim::TriggerEventKind::None;
    throw ScenarioFailure("invalid trigger event: " + kind);
}

mtgsim::SacrificeCostDefinition parse_sacrifice_cost_text(std::string token, char separator, std::string_view label) {
    const auto parts = split_on(token, separator);
    if (parts.size() != 2U) {
        throw ScenarioFailure(std::string(label) + " expects COUNT" + separator + "TYPES");
    }
    mtgsim::SacrificeCostDefinition cost;
    cost.count = parse_u32(parts[0], std::string(label) + " count");
    cost.required_type_mask = parse_type_mask(parts[1]);
    if (!cost.active()) {
        throw ScenarioFailure(std::string(label) + " must require at least one typed permanent");
    }
    return cost;
}

mtgsim::LifeCostDefinition parse_life_cost_text(std::string token, std::string_view label) {
    mtgsim::LifeCostDefinition cost;
    cost.amount = parse_u32(token, std::string(label) + " amount");
    if (!cost.active()) {
        throw ScenarioFailure(std::string(label) + " must require at least one life");
    }
    return cost;
}

void apply_sacrifice_cost_option(mtgsim::CardDefinition& def, std::string token) {
    def.sacrifice_cost = parse_sacrifice_cost_text(std::move(token), ':', "sacrifice_cost");
}

void apply_life_cost_option(mtgsim::CardDefinition& def, std::string token) {
    def.life_cost = parse_life_cost_text(std::move(token), "life_cost");
}

void apply_effect_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    const auto kind = parse_effect_kind(parts.empty() ? std::string{} : parts[0]);
    if (kind == mtgsim::EffectKind::AddCounters) {
        if (parts.size() != 4U) {
            throw ScenarioFailure("counter effect option expects counter:COUNTER_KIND:AMOUNT:TARGETS[*COUNT][*COUNT]");
        }
        def.effect_kind = kind;
        def.effect_counter_kind = parse_counter_kind(parts[1]);
        def.effect_amount = parse_u32(parts[2], "counter effect amount");
        apply_target_spec(def.target_mask, def.target_count, parts[3]);
        return;
    }
    if (kind == mtgsim::EffectKind::CreateToken) {
        if (parts.size() != 3U) {
            throw ScenarioFailure("create_token effect option expects create_token:COUNT:TOKEN_DEFINITION_INDEX");
        }
        def.effect_kind = kind;
        def.effect_amount = parse_u32(parts[1], "token count");
        def.target_mask = mtgsim::TargetNone;
        def.target_count = 0U;
        def.created_token_definition_index = parse_u32(parts[2], "token definition index");
        return;
    }
    if (parts.size() != 3U) {
        throw ScenarioFailure("effect option expects KIND:AMOUNT:TARGETS[*COUNT]");
    }
    def.effect_kind = kind;
    def.effect_amount = parse_u32(parts[1], "effect amount");
    apply_target_spec(def.target_mask, def.target_count, parts[2]);
}


void apply_mode_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() < 4U) {
        throw ScenarioFailure("mode option expects NAME:KIND:AMOUNT:TARGETS[*COUNT] or NAME:counter:COUNTER_KIND:AMOUNT:TARGETS[*COUNT][*COUNT] or NAME:create_token:COUNT:TOKEN_DEFINITION_INDEX");
    }
    mtgsim::SpellModeDefinition mode;
    mode.name = dequote_name(parts[0]);
    mode.effect_kind = parse_effect_kind(parts[1]);
    if (mode.effect_kind == mtgsim::EffectKind::AddCounters) {
        if (parts.size() != 5U) {
            throw ScenarioFailure("counter mode option expects NAME:counter:COUNTER_KIND:AMOUNT:TARGETS[*COUNT][*COUNT]");
        }
        mode.effect_counter_kind = parse_counter_kind(parts[2]);
        mode.effect_amount = parse_u32(parts[3], "counter mode effect amount");
        apply_target_spec(mode.target_mask, mode.target_count, parts[4]);
    } else if (mode.effect_kind == mtgsim::EffectKind::CreateToken) {
        if (parts.size() != 4U) {
            throw ScenarioFailure("create_token mode option expects NAME:create_token:COUNT:TOKEN_DEFINITION_INDEX");
        }
        mode.effect_amount = parse_u32(parts[2], "token count");
        mode.target_mask = mtgsim::TargetNone;
        mode.target_count = 0U;
        mode.created_token_definition_index = parse_u32(parts[3], "token definition index");
    } else {
        if (parts.size() != 4U) {
            throw ScenarioFailure("mode option expects NAME:KIND:AMOUNT:TARGETS[*COUNT]");
        }
        mode.effect_amount = parse_u32(parts[2], "mode effect amount");
        apply_target_spec(mode.target_mask, mode.target_count, parts[3]);
    }
    def.modes.push_back(std::move(mode));
}

void apply_loyalty_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() != 4U && parts.size() != 5U) {
        throw ScenarioFailure("loyalty_ability option expects COST:KIND:AMOUNT:TARGETS[*COUNT][:COUNTER_KIND]");
    }
    def.loyalty_ability.cost = parse_int(parts[0], "loyalty cost");
    def.loyalty_ability.effect_kind = parse_effect_kind(parts[1]);
    def.loyalty_ability.effect_amount = parse_u32(parts[2], "loyalty ability effect amount");
    apply_target_spec(def.loyalty_ability.target_mask, def.loyalty_ability.target_count, parts[3]);
    if (parts.size() == 5U) {
        def.loyalty_ability.effect_counter_kind = parse_counter_kind(parts[4]);
    }
}

bool parse_tap_cost(std::string token) {
    std::transform(token.begin(), token.end(), token.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (token == "tap" || token == "t" || token == "true" || token == "yes" || token == "1") {
        return true;
    }
    if (token == "notap" || token == "no_tap" || token == "false" || token == "no" || token == "0" || token == "-") {
        return false;
    }
    throw ScenarioFailure("invalid tap-cost token: " + token);
}

void apply_mana_ability_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() != 3U) {
        throw ScenarioFailure("mana_ability option expects NAME:TAP:PRODUCES");
    }
    mtgsim::ManaAbilityDefinition ability;
    ability.name = dequote_name(parts[0]);
    ability.tap_cost = parse_tap_cost(parts[1]);
    ability.produces = parse_mana_pool_text(parts[2]);
    if (!ability.active()) {
        throw ScenarioFailure("mana_ability must produce at least one mana");
    }
    def.mana_abilities.push_back(std::move(ability));
}

void apply_activated_suffix(mtgsim::ActivatedAbilityDefinition& ability, std::string token) {
    std::string lower = token;
    std::transform(lower.begin(), lower.end(), lower.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (lower == "sorcery" || lower == "main") {
        ability.sorcery_speed = true;
        return;
    }
    if (lower == "instant" || lower == "any") {
        ability.sorcery_speed = false;
        return;
    }
    const std::vector<std::string> sacrifice_prefixes = {"sac=", "sacrifice=", "sac_cost=", "sacrifice_cost="};
    for (const auto& prefix : sacrifice_prefixes) {
        if (lower.rfind(prefix, 0) == 0U) {
            ability.sacrifice_cost = parse_sacrifice_cost_text(token.substr(prefix.size()), ',', "activated sacrifice cost");
            return;
        }
    }
    const std::vector<std::string> life_prefixes = {"life=", "life_cost=", "pay_life="};
    for (const auto& prefix : life_prefixes) {
        if (lower.rfind(prefix, 0) == 0U) {
            ability.life_cost = parse_life_cost_text(token.substr(prefix.size()), "activated life cost");
            return;
        }
    }
    throw ScenarioFailure("unknown activated ability suffix: " + token);
}

void apply_activated_suffixes(mtgsim::ActivatedAbilityDefinition& ability, const std::vector<std::string>& parts, std::size_t start) {
    for (std::size_t i = start; i < parts.size(); ++i) {
        apply_activated_suffix(ability, parts[i]);
    }
}

void apply_activated_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() < 6U) {
        throw ScenarioFailure("activated option expects NAME:COST:TAP:KIND:AMOUNT:TARGETS[*COUNT][:sorcery][:sac=COUNT,TYPES][:life=N]");
    }
    mtgsim::ActivatedAbilityDefinition ability;
    ability.name = dequote_name(parts[0]);
    ability.mana_cost = parse_cost(parts[1]);
    ability.tap_cost = parse_tap_cost(parts[2]);
    ability.effect_kind = parse_effect_kind(parts[3]);
    if (ability.effect_kind == mtgsim::EffectKind::AddCounters) {
        if (parts.size() < 7U) {
            throw ScenarioFailure("activated counter option expects NAME:COST:TAP:counter:COUNTER_KIND:AMOUNT:TARGETS[*COUNT][*COUNT][:sorcery][:sac=COUNT,TYPES][:life=N]");
        }
        ability.effect_counter_kind = parse_counter_kind(parts[4]);
        ability.effect_amount = parse_u32(parts[5], "activated counter amount");
        apply_target_spec(ability.target_mask, ability.target_count, parts[6]);
        apply_activated_suffixes(ability, parts, 7U);
    } else if (ability.effect_kind == mtgsim::EffectKind::CreateToken) {
        if (parts.size() < 6U) {
            throw ScenarioFailure("activated create_token option expects NAME:COST:TAP:create_token:COUNT:DEF_INDEX[:sorcery][:sac=COUNT,TYPES][:life=N]");
        }
        ability.effect_amount = parse_u32(parts[4], "activated token count");
        ability.created_token_definition_index = parse_u32(parts[5], "token definition index");
        ability.target_mask = mtgsim::TargetNone;
        ability.target_count = 0U;
        apply_activated_suffixes(ability, parts, 6U);
    } else {
        if (parts.size() < 6U) {
            throw ScenarioFailure("activated option expects NAME:COST:TAP:KIND:AMOUNT:TARGETS[*COUNT][:sorcery][:sac=COUNT,TYPES][:life=N]");
        }
        ability.effect_amount = parse_u32(parts[4], "activated ability effect amount");
        apply_target_spec(ability.target_mask, ability.target_count, parts[5]);
        apply_activated_suffixes(ability, parts, 6U);
    }
    def.activated_abilities.push_back(std::move(ability));
}

bool apply_trigger_self_mode(mtgsim::TriggerDefinition& trigger, std::string mode) {
    std::transform(mode.begin(), mode.end(), mode.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (mode == "self" || mode == "include_self") {
        trigger.exclude_source = false;
        return true;
    }
    if (mode == "other" || mode == "exclude_self") {
        trigger.exclude_source = true;
        return true;
    }
    return false;
}

void apply_trigger_option(mtgsim::CardDefinition& def, std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() < 3U || parts.size() > 5U) {
        throw ScenarioFailure("trigger option expects EVENT:EFFECT:AMOUNT[:TARGETS][:self|other]");
    }
    def.trigger.event = parse_trigger_event(parts[0]);
    def.trigger.effect_kind = parse_effect_kind(parts[1]);
    def.trigger.effect_amount = parse_u32(parts[2], "trigger effect amount");
    def.trigger.target_mask = mtgsim::TargetNone;
    def.trigger.exclude_source = true;
    if (parts.size() >= 4U) {
        if (!apply_trigger_self_mode(def.trigger, parts[3])) {
            apply_target_spec(def.trigger.target_mask, def.trigger.target_count, parts[3]);
        }
    }
    if (parts.size() == 5U && !apply_trigger_self_mode(def.trigger, parts[4])) {
        throw ScenarioFailure("invalid trigger self mode: " + parts[4]);
    }
}

mtgsim::TargetRef parse_target_ref(std::string token) {
    const auto parts = split_on(token, ':');
    if (parts.size() != 2U) {
        throw ScenarioFailure("target expects player:N, object:N, or stack:N");
    }
    std::string kind = parts[0];
    std::transform(kind.begin(), kind.end(), kind.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (kind == "player" || kind == "p") {
        return mtgsim::TargetRef{.kind = mtgsim::TargetKind::Player, .player = mtgsim::PlayerId{parse_u32(parts[1], "target player")}};
    }
    if (kind == "object" || kind == "o" || kind == "stack" || kind == "s") {
        return mtgsim::TargetRef{.kind = mtgsim::TargetKind::Object, .object = mtgsim::ObjectId{parse_u32(parts[1], "target object")}};
    }
    throw ScenarioFailure("invalid target kind: " + parts[0]);
}

std::vector<mtgsim::TargetRef> parse_target_refs(std::string token) {
    std::vector<mtgsim::TargetRef> targets;
    if (token == "-" || token == "none" || token.empty()) {
        return targets;
    }
    for (const auto& part : split_on(token, ',')) {
        targets.push_back(parse_target_ref(part));
    }
    return targets;
}

mtgsim::TargetRef parse_optional_target_ref(std::string token) {
    std::string lowered = token;
    std::transform(lowered.begin(), lowered.end(), lowered.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    if (lowered == "none" || lowered == "-" || lowered == "0") {
        return mtgsim::TargetRef{};
    }
    return parse_target_ref(token);
}

struct ScenarioRunner {
    std::vector<mtgsim::CardDefinition> definitions;
    std::vector<mtgsim::PlayerDeck> decks;
    std::optional<mtgsim::GameState> game;
    std::uint64_t seed = 1;
    std::size_t assertions = 0;
    std::vector<std::string> trace;

    mtgsim::GameState& state() {
        if (!game.has_value()) {
            throw ScenarioFailure("game has not been created yet; use create before game actions");
        }
        return *game;
    }

    void expect(bool condition, const std::string& message) {
        ++assertions;
        if (!condition) {
            throw ScenarioFailure(message);
        }
    }

    std::size_t first_event_index(std::string_view kind) {
        const auto& current = state();
        for (std::size_t i = 0; i < current.events.size(); ++i) {
            if (current.events[i].kind == kind) {
                return i;
            }
        }
        return current.events.size();
    }

    std::size_t event_count(std::string_view kind) {
        const auto& current = state();
        return static_cast<std::size_t>(std::count_if(current.events.begin(), current.events.end(), [kind](const mtgsim::Event& event) {
            return event.kind == kind;
        }));
    }

    void run_line(const std::vector<std::string>& tokens) {
        if (tokens.empty()) {
            return;
        }
        const auto& op = tokens[0];
        if (op == "seed") {
            if (tokens.size() != 2U) throw ScenarioFailure("seed expects 1 argument");
            seed = static_cast<std::uint64_t>(std::stoull(tokens[1]));
        } else if (op == "card") {
            if (tokens.size() < 5U) throw ScenarioFailure("card NAME TYPES POWER TOUGHNESS [cost=X] [tap=SYMBOL] [mana_ability=NAME:TAP:PRODUCES] [color=C,C] [loyalty=N] [defense=N] [loyalty_ability=COST:KIND:AMOUNT:TARGETS[*COUNT][:COUNTER_KIND]] [activated=NAME:COST:TAP:KIND:AMOUNT:TARGETS[*COUNT][:COUNTER_KIND][:sorcery][:sac=COUNT,TYPES][:life=N]] [static=NAME:SCOPE:POWER/TOUGHNESS:ABILITIES[:TYPES][:add_types=TYPES][:remove_types=TYPES][:set_color=COLORS][:add_color=COLORS][:remove_color=COLORS][:set_pt=P/T][:remove_abilities=A,B][:depends=NAME[,NAME]]] [continuous=NAME:SCOPE:POWER/TOUGHNESS:ABILITIES[:TYPES][:add_types=TYPES][:remove_types=TYPES][:set_color=COLORS][:add_color=COLORS][:remove_color=COLORS][:set_pt=P/T][:remove_abilities=A,B][:depends=NAME[,NAME]]] [protection=C,C] [abilities=A,B] [attachment=KIND[:TARGETS]] [attach_bonus=P/T] [grants=A,B] [effect=KIND:AMOUNT:TARGETS[*COUNT]|counter:COUNTER_KIND:AMOUNT:TARGETS[*COUNT][*COUNT]|counterspell:1:stack|create_token:COUNT:DEF_INDEX] [sacrifice_cost=COUNT:TYPES] [life_cost=N] [mode=NAME:KIND:AMOUNT:TARGETS[*COUNT]|NAME:counter:COUNTER_KIND:AMOUNT:TARGETS[*COUNT][*COUNT]|NAME:create_token:COUNT:DEF_INDEX] [trigger=EVENT:EFFECT:AMOUNT[:TARGETS][:self|other]] [replacement=NAME:SCOPE:FROM_ZONE:TO_ZONE:REPLACEMENT_ZONE[:TYPES][:choice=N]]");
            mtgsim::CardDefinition def;
            def.name = dequote_name(tokens[1]);
            def.type_mask = parse_type_mask(tokens[2]);
            def.printed_power = parse_int(tokens[3], "power");
            def.printed_toughness = parse_int(tokens[4], "toughness");
            def.mana_cost = mtgsim::ManaCost{};
            for (std::size_t i = 5; i < tokens.size(); ++i) {
                if (tokens[i].rfind("cost=", 0) == 0U) {
                    def.mana_cost = parse_cost(option_value(tokens[i], "cost"));
                } else if (tokens[i].rfind("tap=", 0) == 0U) {
                    const auto value = option_value(tokens[i], "tap");
                    if (value != "none" && value != "-") {
                        def.taps_for_mana = true;
                        def.tap_mana_symbol = parse_mana_symbol(value);
                    }
                } else if (tokens[i].rfind("color=", 0) == 0U) {
                    def.color_mask = parse_color_mask(option_value(tokens[i], "color"));
                } else if (tokens[i].rfind("loyalty=", 0) == 0U) {
                    def.printed_loyalty = parse_int(option_value(tokens[i], "loyalty"), "loyalty");
                } else if (tokens[i].rfind("defense=", 0) == 0U) {
                    def.printed_defense = parse_int(option_value(tokens[i], "defense"), "defense");
                } else if (tokens[i].rfind("loyalty_ability=", 0) == 0U) {
                    apply_loyalty_option(def, option_value(tokens[i], "loyalty_ability"));
                } else if (tokens[i].rfind("activated=", 0) == 0U) {
                    apply_activated_option(def, option_value(tokens[i], "activated"));
                } else if (tokens[i].rfind("mana_ability=", 0) == 0U) {
                    apply_mana_ability_option(def, option_value(tokens[i], "mana_ability"));
                } else if (tokens[i].rfind("static=", 0) == 0U) {
                    apply_static_effect_option(def, option_value(tokens[i], "static"));
                } else if (tokens[i].rfind("continuous=", 0) == 0U) {
                    apply_continuous_effect_option(def, option_value(tokens[i], "continuous"));
                } else if (tokens[i].rfind("replacement=", 0) == 0U) {
                    apply_zone_change_replacement_option(def, option_value(tokens[i], "replacement"));
                } else if (tokens[i].rfind("zone_replacement=", 0) == 0U) {
                    apply_zone_change_replacement_option(def, option_value(tokens[i], "zone_replacement"));
                } else if (tokens[i].rfind("protection=", 0) == 0U) {
                    def.protection_color_mask = parse_color_mask(option_value(tokens[i], "protection"));
                } else if (tokens[i].rfind("protect=", 0) == 0U) {
                    def.protection_color_mask = parse_color_mask(option_value(tokens[i], "protect"));
                } else if (tokens[i].rfind("abilities=", 0) == 0U) {
                    def.ability_mask = parse_ability_mask(option_value(tokens[i], "abilities"));
                } else if (tokens[i].rfind("attachment=", 0) == 0U) {
                    apply_attachment_option(def, option_value(tokens[i], "attachment"));
                } else if (tokens[i].rfind("attach_bonus=", 0) == 0U) {
                    const auto bonus = parse_power_toughness_pair(option_value(tokens[i], "attach_bonus"));
                    def.attachment_power_bonus = bonus.first;
                    def.attachment_toughness_bonus = bonus.second;
                } else if (tokens[i].rfind("grants=", 0) == 0U) {
                    def.attachment_granted_ability_mask = parse_ability_mask(option_value(tokens[i], "grants"));
                } else if (tokens[i].rfind("mode=", 0) == 0U) {
                    apply_mode_option(def, option_value(tokens[i], "mode"));
                } else if (tokens[i].rfind("effect=", 0) == 0U) {
                    apply_effect_option(def, option_value(tokens[i], "effect"));
                } else if (tokens[i].rfind("sacrifice_cost=", 0) == 0U) {
                    apply_sacrifice_cost_option(def, option_value(tokens[i], "sacrifice_cost"));
                } else if (tokens[i].rfind("sac_cost=", 0) == 0U) {
                    apply_sacrifice_cost_option(def, option_value(tokens[i], "sac_cost"));
                } else if (tokens[i].rfind("life_cost=", 0) == 0U) {
                    apply_life_cost_option(def, option_value(tokens[i], "life_cost"));
                } else if (tokens[i].rfind("pay_life=", 0) == 0U) {
                    apply_life_cost_option(def, option_value(tokens[i], "pay_life"));
                } else if (tokens[i].rfind("trigger=", 0) == 0U) {
                    apply_trigger_option(def, option_value(tokens[i], "trigger"));
                } else {
                    throw ScenarioFailure("unknown card option: " + tokens[i]);
                }
            }
            definitions.push_back(std::move(def));
        } else if (op == "deck") {
            if (tokens.size() != 3U) throw ScenarioFailure("deck PLAYER_NAME IDX,IDX,...");
            mtgsim::PlayerDeck deck;
            deck.player_name = dequote_name(tokens[1]);
            if (tokens[2] != "-") {
                for (const auto& part : split_on(tokens[2], ',')) {
                    deck.definition_indices.push_back(parse_u32(part, "deck definition index"));
                }
            }
            decks.push_back(std::move(deck));
        } else if (op == "create") {
            if (decks.size() < 2U) throw ScenarioFailure("create requires at least two deck lines");
            game = mtgsim::make_game(definitions, decks, seed);
        } else if (op == "start") {
            mtgsim::StartOptions opts;
            for (std::size_t i = 1; i < tokens.size(); ++i) {
                if (tokens[i].rfind("opening=", 0) == 0U) {
                    opts.opening_hand_size = parse_u32(option_value(tokens[i], "opening"), "opening");
                } else if (tokens[i].rfind("shuffle=", 0) == 0U) {
                    opts.shuffle_libraries = parse_bool(option_value(tokens[i], "shuffle"));
                } else if (tokens[i].rfind("life=", 0) == 0U) {
                    opts.starting_life_total = parse_int(option_value(tokens[i], "life"), "life");
                } else {
                    throw ScenarioFailure("unknown start option: " + tokens[i]);
                }
            }
            mtgsim::start_game(state(), opts);
        } else if (op == "main_phase") {
            if (tokens.size() != 2U && tokens.size() != 3U) throw ScenarioFailure("main_phase PLAYER [main1|main2]");
            const auto player_id = mtgsim::PlayerId{parse_u32(tokens[1], "player")};
            state().active_player = player_id;
            state().priority_player = player_id;
            state().step = (tokens.size() == 3U && tokens[2] == "main2") ? mtgsim::Step::Main2 : mtgsim::Step::Main1;
            state().consecutive_priority_passes = 0;
        } else if (op == "priority") {
            if (tokens.size() != 3U && tokens.size() != 4U) throw ScenarioFailure("priority PLAYER STEP [ACTIVE_PLAYER]");
            const auto priority_player = mtgsim::PlayerId{parse_u32(tokens[1], "priority player")};
            state().priority_player = priority_player;
            state().active_player = tokens.size() == 4U ? mtgsim::PlayerId{parse_u32(tokens[3], "active player")} : priority_player;
            state().step = parse_step(tokens[2]);
            state().consecutive_priority_passes = 0;
        } else if (op == "draw") {
            if (tokens.size() != 2U) throw ScenarioFailure("draw PLAYER");
            mtgsim::draw_card(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")});
        } else if (op == "move") {
            if (tokens.size() != 4U) throw ScenarioFailure("move OBJECT CONTROLLER ZONE");
            mtgsim::move_object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}, mtgsim::PlayerId{parse_u32(tokens[2], "controller")}, parse_zone(tokens[3]));
        } else if (op == "add_mana") {
            if (tokens.size() != 4U) throw ScenarioFailure("add_mana PLAYER SYMBOL AMOUNT");
            mtgsim::add_mana(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}, parse_mana_symbol(tokens[2]), parse_u32(tokens[3], "amount"));
        } else if (op == "ready") {
            if (tokens.size() != 2U) throw ScenarioFailure("ready OBJECT");
            auto& obj = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto& controller = mtgsim::player(state(), obj.controller);
            obj.controlled_since_turn_start_index = controller.turn_start_index == 0U ? 0U : controller.turn_start_index - 1U;
        } else if (op == "protector") {
            if (tokens.size() != 3U) throw ScenarioFailure("protector BATTLE_OBJECT PLAYER");
            expect(mtgsim::set_battle_protector(state(), mtgsim::ObjectId{parse_u32(tokens[1], "battle object")}, mtgsim::PlayerId{parse_u32(tokens[2], "protector")}), "expected battle protector assignment to be legal");
        } else if (op == "action") {
            if (tokens.size() < 3U) throw ScenarioFailure("action KIND PLAYER [OBJECT]");
            mtgsim::LegalAction action;
            action.player = mtgsim::PlayerId{parse_u32(tokens[2], "player")};
            if (tokens[1] == "pass") {
                action.kind = mtgsim::ActionKind::PassPriority;
            } else if (tokens[1] == "cast_paid") {
                if (tokens.size() < 4U || tokens.size() > 6U) throw ScenarioFailure("action cast_paid PLAYER OBJECT [mode=N] [target=player:N|object:N|stack:N|targets=player:N,object:N,stack:N]");
                action.kind = mtgsim::ActionKind::CastSpellFromHandPaid;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
                for (std::size_t i = 4; i < tokens.size(); ++i) {
                    if (tokens[i].rfind("target=", 0) == 0U) {
                        action.target = parse_target_ref(option_value(tokens[i], "target"));
                        action.targets = {action.target};
                    } else if (tokens[i].rfind("targets=", 0) == 0U) {
                        action.targets = parse_target_refs(option_value(tokens[i], "targets"));
                        action.target = action.targets.empty() ? mtgsim::TargetRef{} : action.targets.front();
                    } else if (tokens[i].rfind("mode=", 0) == 0U) {
                        action.mode_index = parse_u32(option_value(tokens[i], "mode"), "mode index");
                    } else {
                        throw ScenarioFailure("unknown cast_paid option: " + tokens[i]);
                    }
                }
            } else if (tokens[1] == "play_land") {
                if (tokens.size() != 4U) throw ScenarioFailure("action play_land PLAYER OBJECT");
                action.kind = mtgsim::ActionKind::PlayLand;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
            } else if (tokens[1] == "tap_mana") {
                if (tokens.size() != 4U) throw ScenarioFailure("action tap_mana PLAYER OBJECT");
                action.kind = mtgsim::ActionKind::ActivateTapManaAbility;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
            } else if (tokens[1] == "mana" || tokens[1] == "mana_ability") {
                if (tokens.size() != 4U && tokens.size() != 5U) throw ScenarioFailure("action mana PLAYER OBJECT [ability=N]");
                action.kind = mtgsim::ActionKind::ActivateManaAbility;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
                action.mana_ability_index = 1U;
                if (tokens.size() == 5U) {
                    action.mana_ability_index = parse_u32(option_value(tokens[4], "ability"), "mana ability index");
                }
            } else if (tokens[1] == "activate") {
                if (tokens.size() < 4U || tokens.size() > 6U) throw ScenarioFailure("action activate PLAYER OBJECT [ability=N] [target=player:N|object:N|stack:N|targets=player:N,object:N,stack:N]");
                action.kind = mtgsim::ActionKind::ActivateActivatedAbility;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
                action.ability_index = 1U;
                for (std::size_t i = 4; i < tokens.size(); ++i) {
                    if (tokens[i].rfind("ability=", 0) == 0U) {
                        action.ability_index = parse_u32(option_value(tokens[i], "ability"), "ability index");
                    } else if (tokens[i].rfind("target=", 0) == 0U) {
                        action.target = parse_target_ref(option_value(tokens[i], "target"));
                        action.targets = {action.target};
                    } else if (tokens[i].rfind("targets=", 0) == 0U) {
                        action.targets = parse_target_refs(option_value(tokens[i], "targets"));
                        action.target = action.targets.empty() ? mtgsim::TargetRef{} : action.targets.front();
                    } else {
                        throw ScenarioFailure("unknown activate option: " + tokens[i]);
                    }
                }
            } else if (tokens[1] == "loyalty") {
                if (tokens.size() < 4U || tokens.size() > 5U) throw ScenarioFailure("action loyalty PLAYER OBJECT [target=player:N|object:N|stack:N|targets=player:N,object:N,stack:N]");
                action.kind = mtgsim::ActionKind::ActivateLoyaltyAbility;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
                if (tokens.size() == 5U) {
                    if (tokens[4].rfind("targets=", 0) == 0U) {
                        action.targets = parse_target_refs(option_value(tokens[4], "targets"));
                        action.target = action.targets.empty() ? mtgsim::TargetRef{} : action.targets.front();
                    } else {
                        action.target = parse_target_ref(option_value(tokens[4], "target"));
                        action.targets = {action.target};
                    }
                }
            } else if (tokens[1] == "attack") {
                if (tokens.size() != 5U) throw ScenarioFailure("action attack PLAYER OBJECT target=player:N|object:N");
                action.kind = mtgsim::ActionKind::DeclareAttacker;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
                action.target = parse_target_ref(option_value(tokens[4], "target"));
            } else if (tokens[1] == "block") {
                if (tokens.size() != 5U) throw ScenarioFailure("action block PLAYER OBJECT target=object:N");
                action.kind = mtgsim::ActionKind::DeclareBlocker;
                action.object = mtgsim::ObjectId{parse_u32(tokens[3], "object")};
                action.target = parse_target_ref(option_value(tokens[4], "target"));
            } else if (tokens[1] == "block_batch") {
                if (tokens.size() != 4U) throw ScenarioFailure("action block_batch PLAYER BLOCKER:ATTACKER[,BLOCKER:ATTACKER...]");
                std::vector<mtgsim::BlockAssignment> assignments;
                for (const auto& part : split_on(tokens[3], ',')) {
                    const auto pair = split_on(part, ':');
                    if (pair.size() != 2U) throw ScenarioFailure("block_batch assignment must be BLOCKER:ATTACKER");
                    assignments.push_back(mtgsim::BlockAssignment{.blocker = mtgsim::ObjectId{parse_u32(pair[0], "blocker")}, .attacker = mtgsim::ObjectId{parse_u32(pair[1], "attacker")}});
                }
                action = mtgsim::make_declare_blockers_action(action.player, assignments);
                expect(mtgsim::apply_action(state(), action), "expected block_batch action to be legal");
                return;
            } else if (tokens[1] == "put_triggers") {
                if (tokens.size() != 3U) throw ScenarioFailure("action put_triggers PLAYER");
                action.kind = mtgsim::ActionKind::PutPendingTriggersOnStack;
            } else {
                throw ScenarioFailure("unknown action kind: " + tokens[1]);
            }
            expect(mtgsim::apply_action(state(), action), "expected action to be legal: " + tokens[1]);
        } else if (op == "pass") {
            const int count = tokens.size() == 1U ? 1 : parse_int(tokens[1], "pass count");
            for (int i = 0; i < count; ++i) {
                mtgsim::pass_priority(state());
            }
        } else if (op == "advance") {
            mtgsim::advance_step(state());
        } else if (op == "mark_damage") {
            if (tokens.size() != 3U) throw ScenarioFailure("mark_damage OBJECT AMOUNT");
            mtgsim::mark_damage(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}, parse_u32(tokens[2], "amount"));
        } else if (op == "deal_damage") {
            if (tokens.size() != 4U) throw ScenarioFailure("deal_damage SOURCE_OBJECT player:N|object:N AMOUNT");
            mtgsim::deal_damage_to_target(state(), mtgsim::ObjectId{parse_u32(tokens[1], "source")}, parse_target_ref(tokens[2]), parse_u32(tokens[3], "amount"));
        } else if (op == "add_counter") {
            if (tokens.size() != 4U) throw ScenarioFailure("add_counter OBJECT COUNTER_KIND AMOUNT");
            mtgsim::add_counter_to_object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}, parse_counter_kind(tokens[2]), parse_u32(tokens[3], "amount"));
        } else if (op == "prevent_damage") {
            if (tokens.size() != 3U && tokens.size() != 4U) throw ScenarioFailure("prevent_damage player:N|object:N AMOUNT [LABEL]");
            const std::string label = tokens.size() == 4U ? dequote_name(tokens[3]) : std::string{};
            mtgsim::add_damage_prevention_shield(state(), parse_target_ref(tokens[1]), parse_u32(tokens[2], "amount"), label);
        } else if (op == "regenerate") {
            if (tokens.size() != 2U && tokens.size() != 3U) throw ScenarioFailure("regenerate OBJECT [AMOUNT]");
            const auto amount = tokens.size() == 3U ? parse_u32(tokens[2], "amount") : 1U;
            mtgsim::add_regeneration_shield(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}, amount);
        } else if (op == "destroy") {
            if (tokens.size() != 2U && tokens.size() != 3U) throw ScenarioFailure("destroy OBJECT [allow_regeneration=true|false]");
            const auto allow = tokens.size() == 3U ? parse_bool(tokens[2]) : true;
            (void)mtgsim::destroy_permanent(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}, allow);
        } else if (op == "exile") {
            if (tokens.size() != 2U) throw ScenarioFailure("exile OBJECT");
            (void)mtgsim::exile_permanent(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
        } else if (op == "sacrifice") {
            if (tokens.size() != 3U) throw ScenarioFailure("sacrifice PLAYER OBJECT");
            expect(mtgsim::sacrifice_permanent(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}, mtgsim::ObjectId{parse_u32(tokens[2], "object")}), "expected sacrifice to be legal");
        } else if (op == "gain_control") {
            if (tokens.size() != 3U) throw ScenarioFailure("gain_control PLAYER OBJECT");
            expect(mtgsim::gain_control_of_permanent(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}, mtgsim::ObjectId{parse_u32(tokens[2], "object")}), "expected gain_control to be legal");
        } else if (op == "create_token") {
            if (tokens.size() != 3U && tokens.size() != 4U) throw ScenarioFailure("create_token PLAYER DEF_INDEX [COUNT]");
            const auto count = tokens.size() == 4U ? parse_u32(tokens[3], "count") : 1U;
            (void)mtgsim::create_tokens(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}, parse_u32(tokens[2], "definition index"), count);
        } else if (op == "attach") {
            if (tokens.size() != 3U) throw ScenarioFailure("attach ATTACHMENT_OBJECT player:N|object:N");
            expect(mtgsim::attach_object_to(state(), mtgsim::ObjectId{parse_u32(tokens[1], "attachment")}, parse_target_ref(tokens[2])), "expected attachment to be legal");
        } else if (op == "detach") {
            if (tokens.size() != 2U) throw ScenarioFailure("detach ATTACHMENT_OBJECT");
            mtgsim::detach_object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "attachment")});
        } else if (op == "copy") {
            if (tokens.size() != 3U) throw ScenarioFailure("copy OBJECT SOURCE_OBJECT");
            expect(mtgsim::become_copy_of_permanent(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}, mtgsim::ObjectId{parse_u32(tokens[2], "source")}), "copy helper failed for object " + tokens[1] + " source " + tokens[2]);
        } else if (op == "clear_copy") {
            if (tokens.size() != 2U) throw ScenarioFailure("clear_copy OBJECT");
            mtgsim::clear_copy_effect(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
        } else if (op == "sba") {
            mtgsim::apply_state_based_actions(state());
        } else if (op == "expect_zone_count") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_zone_count PLAYER ZONE COUNT");
            const auto got = mtgsim::zone(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}, parse_zone(tokens[2])).size();
            const auto want = static_cast<std::size_t>(parse_u32(tokens[3], "count"));
            expect(got == want, "zone count mismatch for player " + tokens[1] + " " + tokens[2] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_continuous_effects") {
            if (tokens.size() != 2U) throw ScenarioFailure("expect_continuous_effects COUNT");
            const auto got = mtgsim::continuous_effect_count(state());
            const auto want = static_cast<std::size_t>(parse_u32(tokens[1], "continuous effect count"));
            expect(got == want, "continuous effect count mismatch: got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_stack_size") {
            if (tokens.size() != 2U) throw ScenarioFailure("expect_stack_size COUNT");
            const auto want = static_cast<std::size_t>(parse_u32(tokens[1], "count"));
            expect(state().stack.size() == want, "stack size mismatch: got " + std::to_string(state().stack.size()) + " want " + std::to_string(want));
        } else if (op == "expect_event_order") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_event_order BEFORE_KIND AFTER_KIND");
            const auto before = first_event_index(tokens[1]);
            const auto after = first_event_index(tokens[2]);
            expect(before < state().events.size(), "missing event kind for order check: " + tokens[1]);
            expect(after < state().events.size(), "missing event kind for order check: " + tokens[2]);
            expect(before < after, "event order mismatch: expected " + tokens[1] + " before " + tokens[2]);
        } else if (op == "expect_event_count") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_event_count KIND COUNT");
            const auto got = event_count(tokens[1]);
            const auto want = static_cast<std::size_t>(parse_u32(tokens[2], "event count"));
            expect(got == want, "event count mismatch for " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_mode") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_mode STACK_OBJECT MODE_INDEX");
            const auto& obj = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_u32(tokens[2], "mode index");
            expect(obj.chosen_mode_index == want, "mode mismatch for object " + tokens[1] + ": got " + std::to_string(obj.chosen_mode_index) + " want " + std::to_string(want));
        } else if (op == "expect_pending_triggers") {
            if (tokens.size() != 2U) throw ScenarioFailure("expect_pending_triggers COUNT");
            const auto want = static_cast<std::size_t>(parse_u32(tokens[1], "count"));
            const auto got = mtgsim::pending_trigger_count(state());
            expect(got == want, "pending trigger count mismatch: got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_prevention") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_prevention player:N|object:N AMOUNT");
            const auto target = parse_target_ref(tokens[1]);
            const auto got = mtgsim::damage_prevention_shield_total(state(), target);
            const auto want = parse_u32(tokens[2], "prevention amount");
            expect(got == want, "prevention shield mismatch: got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_counter") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_counter OBJECT COUNTER_KIND AMOUNT");
            const auto got = mtgsim::object_counter_count(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}, parse_counter_kind(tokens[2]));
            const auto want = parse_u32(tokens[3], "counter amount");
            expect(got == want, "counter mismatch for object " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_loyalty") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_loyalty OBJECT AMOUNT");
            const auto got = mtgsim::planeswalker_loyalty(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_u32(tokens[2], "loyalty amount");
            expect(got == want, "loyalty mismatch for object " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_defense") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_defense OBJECT AMOUNT");
            const auto got = mtgsim::battle_defense(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_u32(tokens[2], "defense amount");
            expect(got == want, "defense mismatch for object " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_battle_protector") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_battle_protector OBJECT PLAYER");
            const auto got = mtgsim::battle_protector(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = mtgsim::PlayerId{parse_u32(tokens[2], "protector")};
            expect(got == want, "battle protector mismatch for object " + tokens[1] + ": got " + std::to_string(got.value) + " want " + std::to_string(want.value));
        } else if (op == "expect_regeneration") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_regeneration OBJECT COUNT");
            const auto got = mtgsim::regeneration_shield_count(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_u32(tokens[2], "regeneration count");
            expect(got == want, "regeneration shield mismatch for object " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_effective_pt") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_effective_pt OBJECT POWER TOUGHNESS");
            const auto object_id = mtgsim::ObjectId{parse_u32(tokens[1], "object")};
            const auto got_power = mtgsim::effective_power(state(), object_id);
            const auto got_toughness = mtgsim::effective_toughness(state(), object_id);
            const auto want_power = parse_int(tokens[2], "power");
            const auto want_toughness = parse_int(tokens[3], "toughness");
            expect(got_power == want_power && got_toughness == want_toughness, "effective P/T mismatch for object " + tokens[1] + ": got " + std::to_string(got_power) + "/" + std::to_string(got_toughness) + " want " + std::to_string(want_power) + "/" + std::to_string(want_toughness));
        } else if (op == "expect_attached") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_attached ATTACHMENT_OBJECT none|player:N|object:N");
            const auto got = mtgsim::object_attachment_target(state(), mtgsim::ObjectId{parse_u32(tokens[1], "attachment")});
            const auto want = parse_optional_target_ref(tokens[2]);
            expect(got == want, "attachment target mismatch for object " + tokens[1]);
        } else if (op == "expect_attachment_count") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_attachment_count player:N|object:N COUNT");
            const auto got = mtgsim::attachment_count_for_target(state(), parse_target_ref(tokens[1]));
            const auto want = parse_u32(tokens[2], "attachment count");
            expect(got == want, "attachment count mismatch: got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_ability") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_ability OBJECT ABILITY BOOL");
            const auto object_id = mtgsim::ObjectId{parse_u32(tokens[1], "object")};
            const auto ability = parse_keyword_ability(tokens[2]);
            const auto got = mtgsim::object_has_ability(state(), object_id, ability);
            const auto want = parse_bool(tokens[3]);
            expect(got == want, "keyword ability mismatch for object " + tokens[1] + " ability " + tokens[2]);
        } else if (op == "expect_type") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_type OBJECT TYPE_MASK BOOL");
            const auto object_id = mtgsim::ObjectId{parse_u32(tokens[1], "object")};
            const auto got = (mtgsim::object_type_mask(state(), object_id) & parse_type_mask(tokens[2])) != 0U;
            const auto want = parse_bool(tokens[3]);
            expect(got == want, "type mask mismatch for object " + tokens[1] + " type " + tokens[2]);
        } else if (op == "expect_color") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_color OBJECT COLOR_MASK");
            const auto got = mtgsim::object_color_mask(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_color_mask(tokens[2]);
            expect(got == want, "color mask mismatch for object " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_protection") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_protection OBJECT COLOR BOOL");
            const auto object_id = mtgsim::ObjectId{parse_u32(tokens[1], "object")};
            const auto colors = parse_color_mask(tokens[2]);
            bool got = false;
            for (const auto color : {mtgsim::ColorWhite, mtgsim::ColorBlue, mtgsim::ColorBlack, mtgsim::ColorRed, mtgsim::ColorGreen}) {
                if ((colors & static_cast<mtgsim::u32>(color)) != 0U) {
                    got = got || mtgsim::object_has_protection_from_color(state(), object_id, color);
                }
            }
            const auto want = parse_bool(tokens[3]);
            expect(got == want, "protection mismatch for object " + tokens[1] + " color " + tokens[2]);
        } else if (op == "expect_token") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_token OBJECT BOOL");
            const auto got = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}).token;
            const auto want = parse_bool(tokens[2]);
            expect(got == want, "token flag mismatch for object " + tokens[1]);
        } else if (op == "expect_ceased") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_ceased OBJECT BOOL");
            const auto got = mtgsim::object_ceased_to_exist(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_bool(tokens[2]);
            expect(got == want, "ceased-to-exist mismatch for object " + tokens[1]);
        } else if (op == "expect_object_zone") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_object_zone OBJECT ZONE");
            const auto got = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}).zone;
            const auto want = parse_zone(tokens[2]);
            expect(got == want, "object zone mismatch for object " + tokens[1] + ": got " + mtgsim::to_string(got) + " want " + mtgsim::to_string(want));
        } else if (op == "expect_controller") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_controller OBJECT PLAYER");
            const auto got = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}).controller;
            const auto want = mtgsim::PlayerId{parse_u32(tokens[2], "player")};
            expect(got == want, "controller mismatch for object " + tokens[1] + ": got " + std::to_string(got.value) + " want " + std::to_string(want.value));
        } else if (op == "expect_copy") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_copy OBJECT BOOL");
            const auto got = mtgsim::object_has_copy_effect(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_bool(tokens[2]);
            expect(got == want, "copy-effect flag mismatch for object " + tokens[1]);
        } else if (op == "expect_copiable_definition") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_copiable_definition OBJECT DEFINITION_INDEX");
            const auto got = mtgsim::object_copiable_definition_index(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_u32(tokens[2], "definition index");
            expect(got == want, "copiable definition mismatch for object " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_mana_total") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_mana_total PLAYER TOTAL");
            const auto got = mtgsim::player(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}).mana_pool.total();
            const auto want = parse_u32(tokens[2], "total");
            expect(got == want, "mana total mismatch for player " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_mana") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_mana PLAYER SYMBOL AMOUNT");
            const auto& pool = mtgsim::player(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}).mana_pool;
            const auto symbol = parse_mana_symbol(tokens[2]);
            mtgsim::u32 got = 0;
            switch (symbol) {
                case mtgsim::ManaSymbol::White: got = pool.white; break;
                case mtgsim::ManaSymbol::Blue: got = pool.blue; break;
                case mtgsim::ManaSymbol::Black: got = pool.black; break;
                case mtgsim::ManaSymbol::Red: got = pool.red; break;
                case mtgsim::ManaSymbol::Green: got = pool.green; break;
                case mtgsim::ManaSymbol::Colorless: got = pool.colorless; break;
                case mtgsim::ManaSymbol::Count: break;
            }
            const auto want = parse_u32(tokens[3], "mana amount");
            expect(got == want, "mana symbol mismatch for player " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_tapped") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_tapped OBJECT BOOL");
            const auto got = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}).tapped;
            const auto want = parse_bool(tokens[2]);
            expect(got == want, "tapped mismatch for object " + tokens[1]);
        } else if (op == "expect_summoning_sick") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_summoning_sick OBJECT BOOL");
            const auto got = mtgsim::object_has_summoning_sickness(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_bool(tokens[2]);
            expect(got == want, "summoning-sickness mismatch for object " + tokens[1]);
        } else if (op == "expect_actions") {
            if (tokens.size() != 4U) throw ScenarioFailure("expect_actions PLAYER KIND COUNT");
            mtgsim::ActionKind kind = mtgsim::ActionKind::PassPriority;
            if (tokens[2] == "pass") kind = mtgsim::ActionKind::PassPriority;
            else if (tokens[2] == "cast_paid") kind = mtgsim::ActionKind::CastSpellFromHandPaid;
            else if (tokens[2] == "play_land") kind = mtgsim::ActionKind::PlayLand;
            else if (tokens[2] == "tap_mana") kind = mtgsim::ActionKind::ActivateTapManaAbility;
            else if (tokens[2] == "mana") kind = mtgsim::ActionKind::ActivateManaAbility;
            else if (tokens[2] == "activate") kind = mtgsim::ActionKind::ActivateActivatedAbility;
            else if (tokens[2] == "loyalty") kind = mtgsim::ActionKind::ActivateLoyaltyAbility;
            else if (tokens[2] == "attack") kind = mtgsim::ActionKind::DeclareAttacker;
            else if (tokens[2] == "block") kind = mtgsim::ActionKind::DeclareBlocker;
            else if (tokens[2] == "put_triggers") kind = mtgsim::ActionKind::PutPendingTriggersOnStack;
            else throw ScenarioFailure("unknown expect_actions kind: " + tokens[2]);
            const auto actions = mtgsim::enumerate_legal_actions(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")});
            const auto got = static_cast<mtgsim::u32>(std::count_if(actions.begin(), actions.end(), [kind](const mtgsim::LegalAction& action) { return action.kind == kind; }));
            const auto want = parse_u32(tokens[3], "count");
            expect(got == want, "action count mismatch for " + tokens[2] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_land_plays") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_land_plays PLAYER COUNT");
            const auto got = mtgsim::player(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}).lands_played_this_turn;
            const auto want = parse_u32(tokens[2], "land plays");
            expect(got == want, "land-play count mismatch for player " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_life") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_life PLAYER LIFE");
            const auto got = mtgsim::player(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}).life;
            const auto want = parse_int(tokens[2], "life");
            expect(got == want, "life mismatch for player " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_damage") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_damage OBJECT AMOUNT");
            const auto got = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")}).damage_marked;
            const auto want = parse_u32(tokens[2], "damage");
            expect(got == want, "damage mismatch for object " + tokens[1] + ": got " + std::to_string(got) + " want " + std::to_string(want));
        } else if (op == "expect_lost") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_lost PLAYER BOOL");
            const auto got = mtgsim::player(state(), mtgsim::PlayerId{parse_u32(tokens[1], "player")}).lost;
            const auto want = parse_bool(tokens[2]);
            expect(got == want, "lost mismatch for player " + tokens[1]);
        } else if (op == "expect_attacking") {
            if (tokens.size() != 3U && tokens.size() != 4U) throw ScenarioFailure("expect_attacking OBJECT BOOL [DEFENDER]");
            const auto& obj = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_bool(tokens[2]);
            expect(obj.attacking == want, "attacking mismatch for object " + tokens[1]);
            if (tokens.size() == 4U) {
                const auto want_defender = mtgsim::PlayerId{parse_u32(tokens[3], "defender")};
                expect(obj.defending_player == want_defender, "defender mismatch for object " + tokens[1]);
            }
        } else if (op == "expect_attacking_target") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_attacking_target OBJECT player:N|object:N");
            const auto& obj = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_target_ref(tokens[2]);
            expect(obj.attacking, "object " + tokens[1] + " should be attacking");
            if (want.kind == mtgsim::TargetKind::Player) {
                expect(obj.defending_player == want.player && obj.attacked_object.value == 0U, "attacking player target mismatch for object " + tokens[1]);
            } else {
                expect(obj.attacked_object == want.object, "attacked object mismatch for object " + tokens[1]);
            }
        } else if (op == "expect_blocked") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_blocked OBJECT BOOL");
            const auto& obj = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want = parse_bool(tokens[2]);
            expect(obj.blocked == want, "blocked mismatch for object " + tokens[1]);
        } else if (op == "expect_blocking") {
            if (tokens.size() != 3U) throw ScenarioFailure("expect_blocking OBJECT ATTACKER_OR_0");
            const auto& obj = mtgsim::object(state(), mtgsim::ObjectId{parse_u32(tokens[1], "object")});
            const auto want_value = parse_u32(tokens[2], "attacker");
            expect(obj.blocking.value == want_value, "blocking mismatch for object " + tokens[1] + ": got " + std::to_string(obj.blocking.value) + " want " + std::to_string(want_value));
        } else if (op == "validate") {
            mtgsim::assert_valid_game_state(state());
        } else {
            throw ScenarioFailure("unknown operation: " + op);
        }
    }
};

struct Options {
    std::filesystem::path scenario;
    bool json = false;
};

Options parse_args(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if ((arg == "--scenario" || arg == "-s") && i + 1 < argc) {
            options.scenario = argv[++i];
        } else if (arg == "--json") {
            options.json = true;
        } else if (arg == "--help") {
            std::cout << "usage: mtgsim_scenario --scenario FILE [--json]\n";
            std::exit(0);
        } else {
            throw std::invalid_argument("unknown argument: " + arg);
        }
    }
    if (options.scenario.empty()) {
        throw std::invalid_argument("--scenario FILE is required");
    }
    return options;
}

int run_scenario(const std::filesystem::path& path, bool json) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("unable to open scenario: " + path.string());
    }
    ScenarioRunner runner;
    const auto begin = std::chrono::steady_clock::now();
    std::string status = "passed";
    std::string message;
    std::size_t lines = 0;
    try {
        std::string line;
        while (std::getline(input, line)) {
            ++lines;
            const auto hash = line.find('#');
            if (hash != std::string::npos) {
                line.erase(hash);
            }
            line = trim(line);
            if (line.empty()) {
                continue;
            }
            runner.trace.push_back(std::to_string(lines) + ":" + line);
            try {
                runner.run_line(split_ws(line));
            } catch (const std::exception& exc) {
                throw ScenarioFailure(path.string() + ":" + std::to_string(lines) + ": " + exc.what());
            }
        }
        if (runner.game.has_value()) {
            mtgsim::assert_valid_game_state(*runner.game);
        }
    } catch (const std::exception& exc) {
        status = "failed";
        message = exc.what();
    }
    const auto end = std::chrono::steady_clock::now();
    const double duration = static_cast<double>(std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count()) / 1000000.0;
    if (json) {
        std::cout << "{\"schema\":\"mtgsim.scenario_binary_report.v1\",";
        std::cout << "\"status\":\"" << status << "\",";
        std::cout << "\"path\":\"" << json_escape(path.string()) << "\",";
        std::cout << "\"name\":\"" << json_escape(path.filename().string()) << "\",";
        std::cout << "\"duration_sec\":" << duration << ",";
        std::cout << "\"assertions\":" << runner.assertions << ",";
        std::cout << "\"lines\":" << lines << ",";
        std::cout << "\"message\":\"" << json_escape(message) << "\"}\n";
    } else {
        std::cout << "[" << status << "] " << path << " assertions=" << runner.assertions << " time=" << duration << "s";
        if (!message.empty()) {
            std::cout << " message=" << message;
        }
        std::cout << "\n";
    }
    return status == "passed" ? 0 : 1;
}

} // namespace

int main(int argc, char** argv) {
    try {
        const auto options = parse_args(argc, argv);
        return run_scenario(options.scenario, options.json);
    } catch (const std::exception& exc) {
        std::cerr << "mtgsim_scenario: " << exc.what() << "\n";
        return 2;
    }
}
