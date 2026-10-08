#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

// MUC-5 one-action transition microkernel.
//
// Python remains the authoritative engine. This executable is a staged C++ port
// for stable, deterministic micro-transitions. Rev0018 expands the transport to
// include ordered libraries and pending choices so stack resolution and choice
// transitions can be differential-tested instead of trusted by inspection.

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
    while (std::getline(ss, item, delim)) out.push_back(item);
    if (!s.empty() && s.back() == delim) out.push_back("");
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

std::string join(const std::vector<std::string>& xs, char delim) {
    std::ostringstream os;
    for (size_t i = 0; i < xs.size(); ++i) {
        if (i) os << delim;
        os << xs[i];
    }
    return os.str();
}

std::string join_i(const std::vector<int>& xs, char delim) {
    std::ostringstream os;
    for (size_t i = 0; i < xs.size(); ++i) {
        if (i) os << delim;
        os << xs[i];
    }
    return os.str();
}

std::vector<int> split_ints(const std::string& s, char delim) {
    std::vector<int> out;
    if (s.empty()) return out;
    for (const auto& item : split(s, delim)) {
        if (!item.empty()) out.push_back(std::atoi(item.c_str()));
    }
    return out;
}

std::vector<std::string> split_strings(const std::string& s, char delim) {
    std::vector<std::string> out;
    if (s.empty()) return out;
    for (const auto& item : split(s, delim)) {
        if (!item.empty()) out.push_back(item);
    }
    return out;
}

struct Player {
    std::vector<int> v;
    std::vector<std::string> library;  // bottom-to-top; top is back().
    explicit Player(const std::string& blob = "", const std::string& lib_csv = "") {
        v.reserve(34);
        if (!blob.empty()) {
            for (const auto& x : split(blob, ':')) v.push_back(std::atoi(x.c_str()));
        }
        while (v.size() < 34) v.push_back(0);
        library = split_strings(lib_csv, ',');
    }
    std::string blob() const { return join_i(v, ':'); }
};

// Player blob indices. Keep locked with src/muc5/cpp_transition.py.
enum PIdx {
    LIFE = 0,
    MULL = 1,
    LIB_SIZE = 2,
    H_ISLAND = 3,
    H_COUNTER = 4,
    H_FORCE = 5,
    H_JACE = 6,
    H_OVERLORD = 7,
    G_ISLAND = 8,
    G_COUNTER = 9,
    G_FORCE = 10,
    G_JACE = 11,
    G_OVERLORD = 12,
    E_ISLAND = 13,
    E_COUNTER = 14,
    E_FORCE = 15,
    E_JACE = 16,
    E_OVERLORD = 17,
    L_ISLAND = 18,
    L_COUNTER = 19,
    L_FORCE = 20,
    L_JACE = 21,
    L_OVERLORD = 22,
    UNTAPPED = 23,
    TAPPED = 24,
    JACE_LOYALTY = 25,
    JACE_USED = 26,
    O_READY = 27,
    O_SICK = 28,
    O_TAPPED = 29,
    IMP4 = 30,
    IMP3 = 31,
    IMP2 = 32,
    IMP1 = 33,
};

int hand_idx(const std::string& card) {
    if (card == ISLAND) return H_ISLAND;
    if (card == COUNTER) return H_COUNTER;
    if (card == FORCE) return H_FORCE;
    if (card == JACE) return H_JACE;
    if (card == OVERLORD) return H_OVERLORD;
    return -1;
}

int grave_idx(const std::string& card) {
    if (card == ISLAND) return G_ISLAND;
    if (card == COUNTER) return G_COUNTER;
    if (card == FORCE) return G_FORCE;
    if (card == JACE) return G_JACE;
    if (card == OVERLORD) return G_OVERLORD;
    return -1;
}

int exile_idx(const std::string& card) {
    if (card == ISLAND) return E_ISLAND;
    if (card == COUNTER) return E_COUNTER;
    if (card == FORCE) return E_FORCE;
    if (card == JACE) return E_JACE;
    if (card == OVERLORD) return E_OVERLORD;
    return -1;
}

int library_idx(const std::string& card) {
    if (card == ISLAND) return L_ISLAND;
    if (card == COUNTER) return L_COUNTER;
    if (card == FORCE) return L_FORCE;
    if (card == JACE) return L_JACE;
    if (card == OVERLORD) return L_OVERLORD;
    return -1;
}

int overlord_state_idx(const std::string& s) {
    if (s == "ready") return O_READY;
    if (s == "sick") return O_SICK;
    if (s == "tapped") return O_TAPPED;
    return -1;
}

int hand_total(const Player& p) {
    return p.v[H_ISLAND] + p.v[H_COUNTER] + p.v[H_FORCE] + p.v[H_JACE] + p.v[H_OVERLORD];
}

void remove_from_hand(Player& p, const std::string& card) {
    int idx = hand_idx(card);
    if (idx >= 0) p.v[idx] -= 1;
}

void add_to_hand(Player& p, const std::string& card) {
    int idx = hand_idx(card);
    if (idx >= 0) p.v[idx] += 1;
}

void add_to_grave(Player& p, const std::string& card) {
    int idx = grave_idx(card);
    if (idx >= 0) p.v[idx] += 1;
}

void clear_hand(Player& p) {
    p.v[H_ISLAND] = p.v[H_COUNTER] = p.v[H_FORCE] = p.v[H_JACE] = p.v[H_OVERLORD] = 0;
}

void clear_library_counts(Player& p) {
    p.v[L_ISLAND] = p.v[L_COUNTER] = p.v[L_FORCE] = p.v[L_JACE] = p.v[L_OVERLORD] = 0;
}

void set_library_from_csv(Player& p, const std::string& csv) {
    p.library = split_strings(csv, ',');
    clear_library_counts(p);
    p.v[LIB_SIZE] = static_cast<int>(p.library.size());
    for (const auto& card : p.library) {
        int idx = library_idx(card);
        if (idx >= 0) p.v[idx] += 1;
    }
}

void tap_islands(Player& p, int n) {
    p.v[UNTAPPED] -= n;
    p.v[TAPPED] += n;
}

struct PendingChoiceFlat {
    int player = -1;
    std::string kind;
    std::string resume;
    int remaining = 0;
    int triggers_remaining = 0;
    int target_player = -1;
    int old_loyalty = -1;
    int old_used = 0;
    int new_loyalty = -1;
};

struct State {
    std::string frame;
    std::string main_phase;
    int active_player = 0;
    int priority_player = -1;
    int actor = 0;
    int land_played = 0;
    int consecutive_passes = 0;
    int next_spell_id = 1;
    std::string pre_stack_frame;
    int winner = -1;
    int pc_attacker = -1;
    int pc_defender = -1;
    int pc_to_player = -1;
    int pc_to_jace = -1;
    PendingChoiceFlat pending;
    std::vector<int> stack_ids;
    std::vector<int> stack_controllers;
    std::vector<std::string> stack_cards;
    std::vector<std::string> stack_modes;
    std::vector<int> stack_targets;
    Player p[2];
};

void clear_pending(State& st) {
    st.pending = PendingChoiceFlat{};
}

void set_pending_discard(State& st, int player, const std::string& resume, int triggers_remaining) {
    st.pending.player = player;
    st.pending.kind = "discard";
    st.pending.resume = resume;
    st.pending.remaining = 1;
    st.pending.triggers_remaining = triggers_remaining;
}

void set_pending_cleanup(State& st, int player) {
    st.pending.player = player;
    st.pending.kind = "cleanup_discard";
    st.pending.resume = "NEXT_TURN";
}

void check_state_based(State& st) {
    for (int i = 0; i < 2; ++i) {
        if (st.p[i].v[LIFE] <= 0 && st.winner == -1) {
            st.winner = 1 - i;
            st.frame = "GAME_OVER";
        }
        if (st.p[i].v[JACE_LOYALTY] != -1 && st.p[i].v[JACE_LOYALTY] <= 0) {
            st.p[i].v[G_JACE] += 1;
            st.p[i].v[JACE_LOYALTY] = -1;
            st.p[i].v[JACE_USED] = 0;
        }
    }
}

void draw_one(State& st, int player_i) {
    Player& p = st.p[player_i];
    if (p.library.empty()) {
        if (st.winner == -1) {
            st.winner = 1 - player_i;
            st.frame = "GAME_OVER";
        }
        return;
    }
    std::string card = p.library.back();
    p.library.pop_back();
    p.v[LIB_SIZE] -= 1;
    int lidx = library_idx(card);
    if (lidx >= 0) p.v[lidx] -= 1;
    add_to_hand(p, card);
}

void draw_n(State& st, int player_i, int n) {
    for (int i = 0; i < n && st.winner == -1; ++i) draw_one(st, player_i);
}

void push_spell(State& st, int controller, const std::string& card, const std::string& mode, int target_id) {
    st.stack_ids.push_back(st.next_spell_id++);
    st.stack_controllers.push_back(controller);
    st.stack_cards.push_back(card);
    st.stack_modes.push_back(mode.empty() ? "normal" : mode);
    st.stack_targets.push_back(target_id);
}

void begin_postcombat(State& st) {
    st.frame = "MAIN";
    st.main_phase = "postcombat";
    st.priority_player = -1;
    st.consecutive_passes = 0;
}

void start_turn(State& st, int player_i) {
    if (st.winner != -1) return;
    st.active_player = player_i;
    st.priority_player = -1;
    st.frame = "MAIN";
    st.main_phase = "precombat";
    st.land_played = 0;
    st.consecutive_passes = 0;
    Player& p = st.p[player_i];
    p.v[UNTAPPED] += p.v[TAPPED];
    p.v[TAPPED] = 0;
    p.v[O_READY] += p.v[O_SICK] + p.v[O_TAPPED];
    p.v[O_SICK] = 0;
    p.v[O_TAPPED] = 0;
    p.v[JACE_USED] = 0;
    draw_one(st, player_i);
}

void advance_to_next_turn(State& st) {
    start_turn(st, 1 - st.active_player);
}

void end_turn(State& st) {
    Player& p = st.p[st.active_player];
    int awakened = p.v[IMP1];
    p.v[O_READY] += awakened;
    p.v[IMP1] = p.v[IMP2];
    p.v[IMP2] = p.v[IMP3];
    p.v[IMP3] = p.v[IMP4];
    p.v[IMP4] = 0;
    if (hand_total(p) > 7) {
        set_pending_cleanup(st, st.active_player);
        st.frame = "MAIN";
        return;
    }
    advance_to_next_turn(st);
}

void resolve_combat(State& st, int bp_action, int bj_action) {
    const int attacker_i = st.pc_attacker;
    const int defender_i = st.pc_defender;
    Player& attacker = st.p[attacker_i];
    Player& defender = st.p[defender_i];
    int bp = std::min({bp_action, st.pc_to_player, defender.v[O_READY]});
    int bj = std::min({bj_action, st.pc_to_jace, defender.v[O_READY] - bp});
    int blocked = bp + bj;
    int unblocked_player = st.pc_to_player - bp;
    int unblocked_jace = st.pc_to_jace - bj;
    if (blocked > 0) {
        attacker.v[G_OVERLORD] += blocked;
        defender.v[G_OVERLORD] += blocked;
        defender.v[O_READY] -= blocked;
    }
    int survivors = unblocked_player + unblocked_jace;
    attacker.v[O_TAPPED] += survivors;
    if (unblocked_player > 0) defender.v[LIFE] -= 5 * unblocked_player;
    if (unblocked_jace > 0 && defender.v[JACE_LOYALTY] != -1) {
        defender.v[JACE_LOYALTY] -= 5 * unblocked_jace;
        // Sentinel collision guard: C++ uses -1 for "no Jace", but a
        // 4-loyalty Jace hit by one Overlord also becomes -1 before state-based
        // actions.  Resolve the planeswalker death here so exact -1 damage does
        // not masquerade as "already absent".
        if (defender.v[JACE_LOYALTY] <= 0) {
            defender.v[G_JACE] += 1;
            defender.v[JACE_LOYALTY] = -1;
            defender.v[JACE_USED] = 0;
        }
    }
    st.pc_attacker = st.pc_defender = st.pc_to_player = st.pc_to_jace = -1;
    check_state_based(st);
    if (st.winner == -1) begin_postcombat(st);
}

void after_attack_triggers(State& st) {
    if (st.pc_attacker < 0) {
        st.frame = "ATTACK";
        return;
    }
    Player& defender = st.p[st.pc_defender];
    int total = st.pc_to_player + st.pc_to_jace;
    if (defender.v[O_READY] > 0 && total > 0) {
        st.frame = "BLOCK";
    } else {
        resolve_combat(st, 0, 0);
    }
}

void begin_overlord_trigger_sequence(State& st, int player_i, int trigger_count, const std::string& resume) {
    if (trigger_count <= 0) {
        if (resume == "BLOCK_OR_DAMAGE") after_attack_triggers(st);
        else st.frame = resume;
        return;
    }
    draw_n(st, player_i, 2);
    if (st.winner != -1) return;
    set_pending_discard(st, player_i, resume, trigger_count - 1);
}

State parse_state(const std::vector<std::string>& c) {
    State st;
    // Column 19 is action_shuffle_csv, used only by Jace ultimate transport.
    st.pending.player = to_i(c, 20, -1);
    st.pending.kind = to_s(c, 21);
    st.pending.resume = to_s(c, 22);
    st.pending.remaining = to_i(c, 23);
    st.pending.triggers_remaining = to_i(c, 24);
    st.pending.target_player = to_i(c, 25, -1);
    st.pending.old_loyalty = to_i(c, 26, -1);
    st.pending.old_used = to_i(c, 27, 0);
    st.pending.new_loyalty = to_i(c, 28, -1);
    st.frame = to_s(c, 31);
    st.main_phase = to_s(c, 32);
    st.active_player = to_i(c, 33);
    st.priority_player = to_i(c, 34, -1);
    st.actor = to_i(c, 35);
    st.land_played = to_i(c, 36);
    st.consecutive_passes = to_i(c, 37);
    st.next_spell_id = to_i(c, 38);
    st.pre_stack_frame = to_s(c, 39);
    st.winner = to_i(c, 40, -1);
    st.pc_attacker = to_i(c, 41, -1);
    st.pc_defender = to_i(c, 42, -1);
    st.pc_to_player = to_i(c, 43, -1);
    st.pc_to_jace = to_i(c, 44, -1);
    st.stack_ids = split_ints(to_s(c, 45), ',');
    st.stack_controllers = split_ints(to_s(c, 46), ',');
    st.stack_cards = split_strings(to_s(c, 47), ',');
    st.stack_modes = split_strings(to_s(c, 48), ',');
    st.stack_targets = split_ints(to_s(c, 49), ',');
    st.p[0] = Player(to_s(c, 50), to_s(c, 29));
    st.p[1] = Player(to_s(c, 51), to_s(c, 30));
    return st;
}

std::string pending_signature(const State& st) {
    std::vector<std::string> fields = {
        std::to_string(st.pending.player),
        st.pending.kind,
        st.pending.resume,
        std::to_string(st.pending.remaining),
        std::to_string(st.pending.triggers_remaining),
        std::to_string(st.pending.target_player),
        std::to_string(st.pending.old_loyalty),
        std::to_string(st.pending.old_used),
        std::to_string(st.pending.new_loyalty),
    };
    return join(fields, '|');
}

std::string signature(const State& st) {
    std::vector<std::string> fields;
    fields.push_back("SIGv2");
    fields.push_back(st.frame);
    fields.push_back(st.main_phase);
    fields.push_back(std::to_string(st.active_player));
    fields.push_back(std::to_string(st.priority_player));
    fields.push_back(std::to_string(st.land_played));
    fields.push_back(std::to_string(st.consecutive_passes));
    fields.push_back(std::to_string(st.next_spell_id));
    fields.push_back(st.pre_stack_frame);
    fields.push_back(std::to_string(st.winner));
    fields.push_back(std::to_string(st.pc_attacker));
    fields.push_back(std::to_string(st.pc_defender));
    fields.push_back(std::to_string(st.pc_to_player));
    fields.push_back(std::to_string(st.pc_to_jace));
    fields.push_back(std::to_string(st.pending.player));
    fields.push_back(st.pending.kind);
    fields.push_back(st.pending.resume);
    fields.push_back(std::to_string(st.pending.remaining));
    fields.push_back(std::to_string(st.pending.triggers_remaining));
    fields.push_back(std::to_string(st.pending.target_player));
    fields.push_back(std::to_string(st.pending.old_loyalty));
    fields.push_back(std::to_string(st.pending.old_used));
    fields.push_back(std::to_string(st.pending.new_loyalty));
    fields.push_back(join_i(st.stack_ids, ','));
    fields.push_back(join_i(st.stack_controllers, ','));
    fields.push_back(join(st.stack_cards, ','));
    fields.push_back(join(st.stack_modes, ','));
    fields.push_back(join_i(st.stack_targets, ','));
    fields.push_back(join(st.p[0].library, ','));
    fields.push_back(join(st.p[1].library, ','));
    fields.push_back(st.p[0].blob());
    fields.push_back(st.p[1].blob());
    return join(fields, '|');
}

void erase_stack_at(State& st, size_t idx) {
    st.stack_ids.erase(st.stack_ids.begin() + idx);
    st.stack_controllers.erase(st.stack_controllers.begin() + idx);
    st.stack_cards.erase(st.stack_cards.begin() + idx);
    st.stack_modes.erase(st.stack_modes.begin() + idx);
    st.stack_targets.erase(st.stack_targets.begin() + idx);
}

void resolve_top_of_stack(State& st) {
    if (st.stack_ids.empty()) {
        st.frame = st.pre_stack_frame;
        st.priority_player = -1;
        st.consecutive_passes = 0;
        return;
    }
    const int spell_id = st.stack_ids.back();
    const int controller_i = st.stack_controllers.back();
    const std::string card = st.stack_cards.back();
    const std::string mode = st.stack_modes.back();
    const int target_id = st.stack_targets.back();
    st.stack_ids.pop_back();
    st.stack_controllers.pop_back();
    st.stack_cards.pop_back();
    st.stack_modes.pop_back();
    st.stack_targets.pop_back();

    Player& controller = st.p[controller_i];
    if (card == COUNTER || card == FORCE) {
        for (size_t i = 0; i < st.stack_ids.size(); ++i) {
            if (st.stack_ids[i] == target_id) {
                const int tc = st.stack_controllers[i];
                const std::string tcard = st.stack_cards[i];
                add_to_grave(st.p[tc], tcard);
                erase_stack_at(st, i);
                break;
            }
        }
        add_to_grave(controller, card);
    } else if (card == JACE) {
        if (controller.v[JACE_LOYALTY] == -1) {
            controller.v[JACE_LOYALTY] = 3;
        } else {
            st.pending.player = controller_i;
            st.pending.kind = "jace_legend";
            st.pending.old_loyalty = controller.v[JACE_LOYALTY];
            st.pending.old_used = controller.v[JACE_USED];
            st.pending.new_loyalty = 3;
            controller.v[JACE_LOYALTY] = 3;
            controller.v[JACE_USED] = 0;
        }
    } else if (card == OVERLORD) {
        if (mode == "impending") controller.v[IMP4] += 1;
        else controller.v[O_SICK] += 1;
        begin_overlord_trigger_sequence(st, controller_i, 1, st.pre_stack_frame);
    }

    if (st.pending.player == -1 && st.winner == -1) {
        if (!st.stack_ids.empty()) {
            st.frame = "RESPONSE";
            st.priority_player = st.active_player;
            st.consecutive_passes = 0;
        } else {
            st.frame = st.pre_stack_frame;
            st.priority_player = -1;
            st.consecutive_passes = 0;
        }
    }
}

void apply_choice(State& st, const std::vector<std::string>& c) {
    const std::string action_discard = to_s(c, 14);
    const std::string action_put = to_s(c, 15);
    const std::string action_first = to_s(c, 16);
    const std::string action_second = to_s(c, 17);
    const std::string action_keep = to_s(c, 18);
    const int player_i = st.pending.player;
    Player& p = st.p[player_i];

    if (st.pending.kind == "discard" || st.pending.kind == "cleanup_discard") {
        remove_from_hand(p, action_discard);
        add_to_grave(p, action_discard);
        if (st.pending.kind == "cleanup_discard") {
            if (hand_total(p) > 7) {
                set_pending_cleanup(st, player_i);
            } else {
                clear_pending(st);
                advance_to_next_turn(st);
            }
            return;
        }
        int remaining = st.pending.remaining - 1;
        std::string resume = st.pending.resume.empty() ? "MAIN" : st.pending.resume;
        int triggers = st.pending.triggers_remaining;
        if (remaining > 0) {
            st.pending.remaining = remaining;
            return;
        }
        clear_pending(st);
        if (triggers > 0) {
            begin_overlord_trigger_sequence(st, player_i, triggers, resume);
            return;
        }
        if (resume == "BLOCK_OR_DAMAGE") after_attack_triggers(st);
        else st.frame = resume;
        return;
    }

    if (st.pending.kind == "jace_plus2") {
        int target = st.pending.target_player;
        if (action_put == "bottom" && target >= 0 && !st.p[target].library.empty()) {
            std::string card = st.p[target].library.back();
            st.p[target].library.pop_back();
            st.p[target].library.insert(st.p[target].library.begin(), card);
        }
        std::string resume = st.pending.resume.empty() ? "MAIN" : st.pending.resume;
        clear_pending(st);
        st.frame = resume;
        return;
    }

    if (st.pending.kind == "jace_brainstorm_putback") {
        remove_from_hand(p, action_first);
        remove_from_hand(p, action_second);
        // Python appends second, then first; top of library is back().
        p.library.push_back(action_second);
        p.library.push_back(action_first);
        p.v[LIB_SIZE] += 2;
        int l2 = library_idx(action_second);
        int l1 = library_idx(action_first);
        if (l2 >= 0) p.v[l2] += 1;
        if (l1 >= 0) p.v[l1] += 1;
        std::string resume = st.pending.resume.empty() ? "MAIN" : st.pending.resume;
        clear_pending(st);
        st.frame = resume;
        return;
    }

    if (st.pending.kind == "jace_legend") {
        if (action_keep == "old") {
            p.v[JACE_LOYALTY] = st.pending.old_loyalty;
            p.v[JACE_USED] = st.pending.old_used;
        } else {
            p.v[JACE_LOYALTY] = st.pending.new_loyalty;
            p.v[JACE_USED] = 0;
        }
        p.v[G_JACE] += 1;
        clear_pending(st);
        if (!st.stack_ids.empty()) {
            st.frame = "RESPONSE";
            st.priority_player = st.active_player;
            st.consecutive_passes = 0;
        } else {
            st.frame = st.pre_stack_frame;
            st.priority_player = -1;
            st.consecutive_passes = 0;
        }
        return;
    }
}

void apply_micro_transition(State& st, const std::vector<std::string>& c) {
    const std::string action_kind = to_s(c, 1);
    const std::string action_card = to_s(c, 2);
    const std::string action_mode = to_s(c, 3);
    const std::string action_payment = to_s(c, 4);
    const std::string action_pitch = to_s(c, 5);
    const int action_target_id = to_i(c, 6, -1);
    const std::string action_target_player = to_s(c, 7);
    const std::string action_target_state = to_s(c, 8);
    const int action_to_player = to_i(c, 9);
    const int action_to_jace = to_i(c, 10);
    const int action_block_player = to_i(c, 11);
    const int action_block_jace = to_i(c, 12);
    const std::string action_shuffle_csv = to_s(c, 19);

    Player& actor = st.p[st.actor];

    if (action_kind == "CHOOSE_FOR_EFFECT") {
        apply_choice(st, c);
    } else if (action_kind == "PLAY_ISLAND") {
        remove_from_hand(actor, ISLAND);
        actor.v[UNTAPPED] += 1;
        st.land_played = 1;
    } else if (action_kind == "PASS" && st.frame == "MAIN" && st.main_phase == "precombat") {
        st.frame = "ATTACK";
    } else if (action_kind == "PASS" && st.frame == "MAIN" && st.main_phase == "postcombat") {
        end_turn(st);
    } else if (action_kind == "PASS" && st.frame == "ATTACK") {
        begin_postcombat(st);
    } else if (action_kind == "ATTACK" && st.frame == "ATTACK") {
        int total = action_to_player + action_to_jace;
        actor.v[O_READY] -= total;
        st.pc_attacker = st.actor;
        st.pc_defender = 1 - st.actor;
        st.pc_to_player = action_to_player;
        st.pc_to_jace = action_to_jace;
        if (total > 0) begin_overlord_trigger_sequence(st, st.actor, total, "BLOCK_OR_DAMAGE");
        else after_attack_triggers(st);
    } else if (st.frame == "BLOCK" && action_kind == "PASS") {
        resolve_combat(st, 0, 0);
    } else if (st.frame == "BLOCK" && action_kind == "BLOCK") {
        resolve_combat(st, action_block_player, action_block_jace);
    } else if (action_kind == "PASS" && st.frame == "RESPONSE") {
        st.consecutive_passes += 1;
        if (st.consecutive_passes >= 2) {
            resolve_top_of_stack(st);
        } else {
            st.priority_player = 1 - st.actor;
        }
    } else if (action_kind == "CAST" && st.frame == "MAIN") {
        if (action_card == JACE) {
            remove_from_hand(actor, JACE);
            tap_islands(actor, 4);
            push_spell(st, st.actor, JACE, "normal", -1);
        } else if (action_card == OVERLORD) {
            remove_from_hand(actor, OVERLORD);
            if (action_mode == "impending") {
                tap_islands(actor, 3);
                push_spell(st, st.actor, OVERLORD, "impending", -1);
            } else {
                tap_islands(actor, 5);
                push_spell(st, st.actor, OVERLORD, "full_cost", -1);
            }
        }
        st.pre_stack_frame = st.frame;
        st.frame = "RESPONSE";
        st.priority_player = st.actor;
        st.consecutive_passes = 0;
    } else if (action_kind == "CAST" && st.frame == "RESPONSE") {
        if (action_card == COUNTER) {
            remove_from_hand(actor, COUNTER);
            tap_islands(actor, 2);
            push_spell(st, st.actor, COUNTER, "normal", action_target_id);
        } else if (action_card == FORCE) {
            remove_from_hand(actor, FORCE);
            if (action_payment == "mana") {
                tap_islands(actor, 5);
                push_spell(st, st.actor, FORCE, "mana", action_target_id);
            } else {
                remove_from_hand(actor, action_pitch);
                int eidx = exile_idx(action_pitch);
                if (eidx >= 0) actor.v[eidx] += 1;
                actor.v[LIFE] -= 1;
                push_spell(st, st.actor, FORCE, "pitch", action_target_id);
            }
        }
        st.priority_player = st.actor;
        st.consecutive_passes = 0;
    } else if (action_kind == "ACTIVATE_JACE") {
        actor.v[JACE_USED] = 1;
        if (action_mode == "plus2") {
            actor.v[JACE_LOYALTY] += 2;
            int target_i = (action_target_player == "self") ? st.actor : (1 - st.actor);
            if (!st.p[target_i].library.empty()) {
                st.pending.player = st.actor;
                st.pending.kind = "jace_plus2";
                st.pending.resume = "MAIN";
                st.pending.target_player = target_i;
            }
        } else if (action_mode == "zero") {
            draw_n(st, st.actor, 3);
            if (st.winner == -1) {
                st.pending.player = st.actor;
                st.pending.kind = "jace_brainstorm_putback";
                st.pending.resume = "MAIN";
            }
        } else if (action_mode == "minus1") {
            actor.v[JACE_LOYALTY] -= 1;
            int target_i = (action_target_player == "self") ? st.actor : (1 - st.actor);
            int oidx = overlord_state_idx(action_target_state);
            if (oidx >= 0 && st.p[target_i].v[oidx] > 0) {
                st.p[target_i].v[oidx] -= 1;
                st.p[target_i].v[H_OVERLORD] += 1;
            }
        } else if (action_mode == "ultimate") {
            actor.v[JACE_LOYALTY] -= 12;
            int target_i = (action_target_player == "self") ? st.actor : (1 - st.actor);
            Player& target = st.p[target_i];
            for (const auto& card : target.library) {
                int eidx = exile_idx(card);
                if (eidx >= 0) target.v[eidx] += 1;
            }
            target.library.clear();
            clear_library_counts(target);
            target.v[LIB_SIZE] = 0;
            clear_hand(target);
            set_library_from_csv(target, action_shuffle_csv);
        }
    }
    check_state_based(st);
}

}  // namespace

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
        State st = parse_state(cols);
        apply_micro_transition(st, cols);
        std::cout << signature(st) << "\n";
    }
    return 0;
}
