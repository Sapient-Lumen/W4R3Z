// MUC-5 no-choice segment checker.
//
// This file intentionally reuses the rev0018+ one-action transition microkernel
// instead of copying its transition logic.  Python remains the semantic
// authority.  The segment executable receives contiguous forced-action segment
// records as:
//
//   segment_id \t <TransitionMicroRecord TSV fields>
//
// For each segment, C++ parses the first row's state, then applies every action
// in the segment sequentially using only the action fields from each record.  It
// outputs one final SIGv2 per segment.  This catches drift across multi-action
// forced runs and is a safer intermediate step than declaring a full C++ rollout
// engine authoritative.

#define main muc5_transition_micro_unused_main
#include "muc5_transition_micro.cpp"
#undef main

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string line;
    std::string current_segment;
    bool active = false;
    State st;

    auto flush_segment = [&]() {
        if (active) {
            std::cout << current_segment << "\t" << signature(st) << "\n";
        }
    };

    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        std::vector<std::string> cols = split(line, '\t');
        if (cols.size() < 2) continue;
        std::string segment_id = cols[0];
        std::vector<std::string> rec(cols.begin() + 1, cols.end());

        if (!active || segment_id != current_segment) {
            flush_segment();
            current_segment = segment_id;
            st = parse_state(rec);
            active = true;
        } else {
            // ``actor`` is per-action metadata, not an engine state variable.
            // The one-action microkernel receives it by parsing each full
            // record.  The segment kernel carries state across records, so it
            // must refresh only this action-local field before applying the
            // next forced action.  Do not refresh active/priority/frame here;
            // those must be produced by the previous C++ transition or the
            // segment parity check would stop being meaningful.
            st.actor = to_i(rec, 35, st.actor);
        }
        apply_micro_transition(st, rec);
    }
    flush_segment();
    return 0;
}
