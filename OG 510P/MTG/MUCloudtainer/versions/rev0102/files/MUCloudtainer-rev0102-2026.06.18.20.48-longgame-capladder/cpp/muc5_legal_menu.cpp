#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

// Standalone MUC-5 legal macro-action menu kernel.
//
// This is deliberately NOT the authoritative game engine yet. Python remains the
// semantic oracle. The purpose of this C++ kernel is differential testing for a
// stable, hot boundary: state summary -> legal macro-action strings. It gives us
// a safe bridge toward a long-haul C++ referee without prematurely porting state
// transitions, hidden-information redaction, replay, or reward accounting.

namespace {

const std::string ISLAND = "Island";
const std::string COUNTER = "Counterspell";
const std::string FORCE = "ForceOfWill";
const std::string JACE = "JaceTheMindSculptor";
const std::string OVERLORD = "OverlordOfTheFloodpits";

std::vector<std::string> split(const std::string& s, char delim) {
    std::vector<std::string> out;
    std::string item;
    std::stringstream ss(s);
    while (std::getline(ss, item, delim)) {
        out.push_back(item);
    }
    // std::getline does not produce the final empty field for a trailing
    // delimiter; preserve it because our TSV schema has positional columns.
    if (!s.empty() && s.back() == delim) out.push_back("");
    return out;
}

std::vector<std::string> split_nonempty(const std::string& s, char delim) {
    std::vector<std::string> raw = split(s, delim);
    std::vector<std::string> out;
    for (const auto& item : raw) {
        if (!item.empty()) out.push_back(item);
    }
    return out;
}

int to_i(const std::vector<std::string>& cols, size_t idx, int fallback = 0) {
    if (idx >= cols.size() || cols[idx].empty()) return fallback;
    return std::atoi(cols[idx].c_str());
}

std::string to_s(const std::vector<std::string>& cols, size_t idx, const std::string& fallback = "") {
    if (idx >= cols.size()) return fallback;
    return cols[idx];
}

bool can_pay(int untapped_islands, int generic, int blue) {
    // MUC-5 has only Islands. Blue + generic is simply this many untapped Islands.
    return untapped_islands >= generic + blue;
}

void add(std::vector<std::string>& out, const std::string& s) { out.push_back(s); }

std::string cast_jace() { return "CAST(card=JaceTheMindSculptor)"; }
std::string cast_overlord(const std::string& mode) {
    return "CAST(card=OverlordOfTheFloodpits, mode=" + mode + ")";
}
std::string cast_counterspell(int target_id, const std::string& target_card) {
    return "CAST(card=Counterspell, target_card=" + target_card + ", target_id=" + std::to_string(target_id) + ")";
}
std::string cast_force_mana(int target_id, const std::string& target_card) {
    return "CAST(card=ForceOfWill, payment=mana, target_card=" + target_card + ", target_id=" + std::to_string(target_id) + ")";
}
std::string cast_force_pitch(const std::string& pitch_card, int target_id, const std::string& target_card) {
    return "CAST(card=ForceOfWill, payment=pitch, pitch_card=" + pitch_card + ", target_card=" + target_card + ", target_id=" + std::to_string(target_id) + ")";
}
std::string jace_act(const std::string& mode, const std::string& target_player = "", const std::string& target_state = "") {
    if (!target_player.empty() && !target_state.empty()) {
        return "ACTIVATE_JACE(mode=" + mode + ", target_player=" + target_player + ", target_state=" + target_state + ")";
    }
    if (!target_player.empty()) {
        return "ACTIVATE_JACE(mode=" + mode + ", target_player=" + target_player + ")";
    }
    return "ACTIVATE_JACE(mode=" + mode + ")";
}
std::string choose_discard(const std::string& effect, const std::string& card) {
    return "CHOOSE_FOR_EFFECT(discard=" + card + ", effect=" + effect + ")";
}
std::string choose_jace_plus2(const std::string& put) {
    return "CHOOSE_FOR_EFFECT(effect=jace_plus2, put=" + put + ")";
}
std::string choose_brainstorm(const std::string& first, const std::string& second) {
    return "CHOOSE_FOR_EFFECT(effect=jace_brainstorm_putback, first_draw=" + first + ", second_draw=" + second + ")";
}
std::string choose_legend(const std::string& keep) {
    return "CHOOSE_FOR_EFFECT(effect=jace_legend, keep=" + keep + ")";
}
std::string attack_action(int to_player, int to_jace) {
    return "ATTACK(to_jace=" + std::to_string(to_jace) + ", to_player=" + std::to_string(to_player) + ")";
}
std::string block_action(int bp, int bj) {
    return "BLOCK(block_jace_attackers=" + std::to_string(bj) + ", block_player_attackers=" + std::to_string(bp) + ")";
}

std::vector<std::string> legal_menu_for_columns(const std::vector<std::string>& c) {
    // Schema columns, kept in lockstep with src/muc5/cpp_legal.py:
    // 0 frame, 1 main_phase, 2 pending_kind, 3 land_played,
    // 4 h_island, 5 h_counter, 6 h_force, 7 h_jace, 8 h_overlord,
    // 9 untapped, 10 life, 11 jace_loyalty, 12 jace_used,
    // 13 self_ready, 14 self_sick, 15 self_tapped,
    // 16 opp_jace_loyalty, 17 opp_ready, 18 opp_sick, 19 opp_tapped,
    // 20 stack_ids_csv, 21 stack_cards_csv,
    // 22 combat_to_player, 23 combat_to_jace, 24 defender_ready
    const std::string frame = to_s(c, 0);
    const std::string main_phase = to_s(c, 1);
    const std::string pending = to_s(c, 2);
    const int land_played = to_i(c, 3);
    const int h_island = to_i(c, 4);
    const int h_counter = to_i(c, 5);
    const int h_force = to_i(c, 6);
    const int h_jace = to_i(c, 7);
    const int h_overlord = to_i(c, 8);
    const int untapped = to_i(c, 9);
    const int life = to_i(c, 10);
    const int jace_loyalty = to_i(c, 11, -1);
    const int jace_used = to_i(c, 12);
    const int self_ready = to_i(c, 13);
    const int self_sick = to_i(c, 14);
    const int self_tapped = to_i(c, 15);
    const int opp_jace_loyalty = to_i(c, 16, -1);
    const int opp_ready = to_i(c, 17);
    const int opp_sick = to_i(c, 18);
    const int opp_tapped = to_i(c, 19);
    const std::vector<std::string> stack_ids_s = split_nonempty(to_s(c, 20), ',');
    const std::vector<std::string> stack_cards = split_nonempty(to_s(c, 21), ',');
    const int combat_to_player = to_i(c, 22);
    const int combat_to_jace = to_i(c, 23);
    const int defender_ready = to_i(c, 24);

    std::vector<std::string> out;

    if (!pending.empty() && pending != "None") {
        if (pending == "discard" || pending == "cleanup_discard") {
            // Python sorted(player.hand.items()) order for these card ids.
            if (h_counter > 0) add(out, choose_discard(pending, COUNTER));
            if (h_force > 0) add(out, choose_discard(pending, FORCE));
            if (h_island > 0) add(out, choose_discard(pending, ISLAND));
            if (h_jace > 0) add(out, choose_discard(pending, JACE));
            if (h_overlord > 0) add(out, choose_discard(pending, OVERLORD));
            return out;
        }
        if (pending == "jace_plus2") {
            add(out, choose_jace_plus2("leave"));
            add(out, choose_jace_plus2("bottom"));
            return out;
        }
        if (pending == "jace_brainstorm_putback") {
            struct CardCount { std::string card; int count; };
            std::vector<CardCount> cards = {
                {COUNTER, h_counter}, {FORCE, h_force}, {ISLAND, h_island}, {JACE, h_jace}, {OVERLORD, h_overlord}
            };
            for (const auto& a : cards) {
                if (a.count <= 0) continue;
                for (const auto& b : cards) {
                    if (b.count <= 0) continue;
                    if (a.card == b.card && a.count < 2) continue;
                    add(out, choose_brainstorm(a.card, b.card));
                }
            }
            return out;
        }
        if (pending == "jace_legend") {
            add(out, choose_legend("old"));
            add(out, choose_legend("new"));
            return out;
        }
        add(out, "PASS");
        return out;
    }

    if (frame == "RESPONSE") {
        add(out, "PASS");
        const size_t n = std::min(stack_ids_s.size(), stack_cards.size());
        for (size_t i = 0; i < n; ++i) {
            const int target_id = std::atoi(stack_ids_s[i].c_str());
            const std::string& target_card = stack_cards[i];
            if (h_counter > 0 && can_pay(untapped, 0, 2)) add(out, cast_counterspell(target_id, target_card));
            if (h_force > 0 && can_pay(untapped, 3, 2)) add(out, cast_force_mana(target_id, target_card));
            if (h_force > 0 && life >= 1) {
                if (h_counter > 0) add(out, cast_force_pitch(COUNTER, target_id, target_card));
                if (h_force > 1) add(out, cast_force_pitch(FORCE, target_id, target_card));
                if (h_jace > 0) add(out, cast_force_pitch(JACE, target_id, target_card));
                if (h_overlord > 0) add(out, cast_force_pitch(OVERLORD, target_id, target_card));
            }
        }
        return out;
    }

    if (frame == "MAIN") {
        add(out, "PASS");
        if (!land_played && h_island > 0) add(out, "PLAY_ISLAND");
        if (h_jace > 0 && can_pay(untapped, 2, 2)) add(out, cast_jace());
        if (h_overlord > 0 && can_pay(untapped, 1, 2)) add(out, cast_overlord("impending"));
        if (h_overlord > 0 && can_pay(untapped, 3, 2)) add(out, cast_overlord("full_cost"));
        if (jace_loyalty >= 0 && !jace_used) {
            add(out, jace_act("plus2", "self"));
            add(out, jace_act("plus2", "opponent"));
            add(out, jace_act("zero"));
            if (jace_loyalty >= 1) {
                if (opp_ready > 0) add(out, jace_act("minus1", "opponent", "ready"));
                if (opp_sick > 0) add(out, jace_act("minus1", "opponent", "sick"));
                if (opp_tapped > 0) add(out, jace_act("minus1", "opponent", "tapped"));
                if (self_ready > 0) add(out, jace_act("minus1", "self", "ready"));
                if (self_sick > 0) add(out, jace_act("minus1", "self", "sick"));
                if (self_tapped > 0) add(out, jace_act("minus1", "self", "tapped"));
            }
            if (jace_loyalty >= 12) {
                add(out, jace_act("ultimate", "opponent"));
                add(out, jace_act("ultimate", "self"));
            }
        }
        return out;
    }

    if (frame == "ATTACK") {
        add(out, "PASS");
        const int n = self_ready;
        for (int to_player = 0; to_player <= n; ++to_player) {
            const int max_to_jace = (opp_jace_loyalty >= 0) ? (n - to_player) : 0;
            for (int to_jace = 0; to_jace <= max_to_jace; ++to_jace) {
                if (to_player + to_jace > 0) add(out, attack_action(to_player, to_jace));
            }
        }
        return out;
    }

    if (frame == "BLOCK") {
        add(out, "PASS");
        const int ready = defender_ready;
        for (int bp = 0; bp <= std::min(combat_to_player, ready); ++bp) {
            const int remain = ready - bp;
            for (int bj = 0; bj <= std::min(combat_to_jace, remain); ++bj) {
                if (bp + bj > 0) add(out, block_action(bp, bj));
            }
        }
        return out;
    }

    add(out, "PASS");
    return out;
}

} // namespace

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) {
            std::cout << "\n";
            continue;
        }
        std::vector<std::string> cols = split(line, '\t');
        std::vector<std::string> menu = legal_menu_for_columns(cols);
        for (size_t i = 0; i < menu.size(); ++i) {
            if (i) std::cout << "||";
            std::cout << menu[i];
        }
        std::cout << "\n";
    }
    return 0;
}
