#include "mtgsim/engine.hpp"

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct BenchOptions {
    int games = 10000;
    int priority_pass_pairs_per_game = 24;
    std::uint64_t seed_base = 1;
    bool json = false;
};

int parse_int(const char* value, const char* name) {
    char* end = nullptr;
    const long parsed = std::strtol(value, &end, 10);
    if (end == value || *end != '\0' || parsed < 0) {
        throw std::invalid_argument(std::string("invalid ") + name + "=" + value);
    }
    return static_cast<int>(parsed);
}

std::uint64_t parse_u64(const char* value, const char* name) {
    char* end = nullptr;
    const unsigned long long parsed = std::strtoull(value, &end, 10);
    if (end == value || *end != '\0') {
        throw std::invalid_argument(std::string("invalid ") + name + "=" + value);
    }
    return static_cast<std::uint64_t>(parsed);
}

BenchOptions parse_args(int argc, char** argv) {
    BenchOptions options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--json") {
            options.json = true;
        } else if (arg == "--games" && i + 1 < argc) {
            options.games = parse_int(argv[++i], "--games");
        } else if ((arg == "--pass-pairs" || arg == "--passes") && i + 1 < argc) {
            options.priority_pass_pairs_per_game = parse_int(argv[++i], arg.c_str());
        } else if (arg == "--seed-base" && i + 1 < argc) {
            options.seed_base = parse_u64(argv[++i], "--seed-base");
        } else if (arg == "--help") {
            std::cout << "usage: bench_turns [--games N] [--pass-pairs N] [--seed-base N] [--json]\n"
                         "       --passes is retained as a compatibility alias for --pass-pairs\n";
            std::exit(0);
        } else {
            throw std::invalid_argument("unknown argument: " + arg);
        }
    }
    return options;
}

} // namespace

int main(int argc, char** argv) {
    const auto options = parse_args(argc, argv);
    std::vector<mtgsim::CardDefinition> defs = {{"Sample Permanent", mtgsim::TypeCreature, 1, 1}};
    std::vector<mtgsim::PlayerDeck> decks = {
        {"A", std::vector<mtgsim::u32>(60, 0)},
        {"B", std::vector<mtgsim::u32>(60, 0)}
    };

    const auto begin = std::chrono::steady_clock::now();
    std::uint64_t events = 0;
    for (int i = 0; i < options.games; ++i) {
        auto game = mtgsim::make_game(defs, decks, options.seed_base + static_cast<std::uint64_t>(i));
        mtgsim::start_game(game);
        for (int p = 0; p < options.priority_pass_pairs_per_game; ++p) {
            mtgsim::pass_priority(game);
            mtgsim::pass_priority(game);
        }
        events += game.events.size();
    }
    const auto end = std::chrono::steady_clock::now();
    const auto us = std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count();
    const double seconds = static_cast<double>(us) / 1000000.0;
    const double games_per_second = seconds > 0.0 ? static_cast<double>(options.games) / seconds : 0.0;
    const int priority_pass_calls_per_game = options.priority_pass_pairs_per_game * 2;
    const double events_per_game = options.games > 0 ? static_cast<double>(events) / static_cast<double>(options.games) : 0.0;

    if (options.json) {
        std::cout << "{"
                  << "\"schema\":\"mtgsim.priority_pass_microbenchmark.v2\","
                  << "\"scope\":\"game setup plus direct priority-pass transitions; not representative full-game throughput\","
                  << "\"games\":" << options.games << ","
                  << "\"pass_pairs_per_game\":" << options.priority_pass_pairs_per_game << ","
                  << "\"priority_pass_calls_per_game\":" << priority_pass_calls_per_game << ","
                  << "\"passes_per_game\":" << priority_pass_calls_per_game << ","
                  << "\"events\":" << events << ","
                  << "\"events_per_game\":" << events_per_game << ","
                  << "\"microseconds\":" << us << ","
                  << "\"games_per_second\":" << games_per_second
                  << "}\n";
    } else {
        std::cout << "games=" << options.games
                  << " pass_pairs_per_game=" << options.priority_pass_pairs_per_game
                  << " priority_pass_calls_per_game=" << priority_pass_calls_per_game
                  << " events=" << events
                  << " us=" << us
                  << " priority_pass_microbenchmark_games_per_second=" << games_per_second << "\n";
    }
    return 0;
}
