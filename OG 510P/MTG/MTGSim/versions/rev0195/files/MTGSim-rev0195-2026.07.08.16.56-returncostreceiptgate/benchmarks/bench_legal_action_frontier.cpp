#include "mtgsim/engine.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct Options {
    std::size_t min_attackers = 2U;
    std::size_t max_attackers = 12U;
    int iterations = 20;
    bool json = false;
};

std::size_t parse_size(const char* value, const char* name) {
    char* end = nullptr;
    const unsigned long long parsed = std::strtoull(value, &end, 10);
    if (end == value || *end != '\0') {
        throw std::invalid_argument(std::string("invalid ") + name + "=" + value);
    }
    return static_cast<std::size_t>(parsed);
}

int parse_int(const char* value, const char* name) {
    char* end = nullptr;
    const long parsed = std::strtol(value, &end, 10);
    if (end == value || *end != '\0' || parsed <= 0) {
        throw std::invalid_argument(std::string("invalid ") + name + "=" + value);
    }
    return static_cast<int>(parsed);
}

Options parse_args(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--min-attackers" && i + 1 < argc) {
            options.min_attackers = parse_size(argv[++i], "--min-attackers");
        } else if (arg == "--max-attackers" && i + 1 < argc) {
            options.max_attackers = parse_size(argv[++i], "--max-attackers");
        } else if (arg == "--iterations" && i + 1 < argc) {
            options.iterations = parse_int(argv[++i], "--iterations");
        } else if (arg == "--json") {
            options.json = true;
        } else if (arg == "--help") {
            std::cout << "usage: bench_legal_action_frontier [--min-attackers N] [--max-attackers N] [--iterations N] [--json]\n";
            std::exit(0);
        } else {
            throw std::invalid_argument("unknown or incomplete argument: " + arg);
        }
    }
    if (options.min_attackers > options.max_attackers) {
        throw std::invalid_argument("--min-attackers must not exceed --max-attackers");
    }
    return options;
}

mtgsim::GameState make_attack_game(std::size_t attacker_count) {
    mtgsim::CardDefinition attacker;
    attacker.name = "Frontier Benchmark Raider";
    attacker.type_mask = mtgsim::TypeCreature;
    attacker.printed_power = 1;
    attacker.printed_toughness = 1;

    std::vector<mtgsim::CardDefinition> definitions = {attacker};
    std::vector<mtgsim::PlayerDeck> decks = {
        {"Alpha", std::vector<mtgsim::u32>(attacker_count, 0U)},
        {"Beta", {0U}},
    };
    auto game = mtgsim::make_game(std::move(definitions), decks, 508128U + static_cast<std::uint64_t>(attacker_count));
    mtgsim::StartOptions options;
    options.opening_hand_size = 0U;
    options.shuffle_libraries = false;
    mtgsim::start_game(game, options);

    const auto attackers = mtgsim::zone(game, mtgsim::PlayerId{1}, mtgsim::Zone::Library);
    for (const auto attacker_id : attackers) {
        mtgsim::move_object(game, attacker_id, mtgsim::PlayerId{1}, mtgsim::Zone::Battlefield);
        auto& attacker_object = mtgsim::object(game, attacker_id);
        const auto& controller = mtgsim::player(game, attacker_object.controller);
        attacker_object.controlled_since_turn_start_index = controller.turn_start_index == 0U ? 0U : controller.turn_start_index - 1U;
    }
    game.step = mtgsim::Step::DeclareAttackers;
    game.priority_player = mtgsim::PlayerId{1};
    return game;
}

struct Row {
    std::size_t attackers = 0U;
    std::size_t actions = 0U;
    bool complete = true;
    mtgsim::u64 generation_limit = 0U;
    double average_microseconds = 0.0;
};

} // namespace

int main(int argc, char** argv) {
    const auto options = parse_args(argc, argv);
    std::vector<Row> rows;
    for (std::size_t attacker_count = options.min_attackers; attacker_count <= options.max_attackers; ++attacker_count) {
        const auto game = make_attack_game(attacker_count);
        mtgsim::LegalActionFrontier last{};
        const auto begin = std::chrono::steady_clock::now();
        for (int iteration = 0; iteration < options.iterations; ++iteration) {
            last = mtgsim::enumerate_legal_action_frontier(game, mtgsim::PlayerId{1});
        }
        const auto end = std::chrono::steady_clock::now();
        const auto elapsed_us = std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count();
        rows.push_back(Row{
            .attackers = attacker_count,
            .actions = last.actions.size(),
            .complete = last.complete,
            .generation_limit = last.generation_limit,
            .average_microseconds = static_cast<double>(elapsed_us) / static_cast<double>(options.iterations),
        });
        if (attacker_count == options.max_attackers) {
            break;
        }
    }

    if (options.json) {
        std::cout << "{\"schema\":\"mtgsim.legal_action_frontier_microbenchmark.v1\","
                  << "\"scope\":\"declare-attackers frontier generation with no attack requirements; reports bounded-prefix truth and generation cost\","
                  << "\"iterations\":" << options.iterations << ",\"rows\":[";
        for (std::size_t i = 0; i < rows.size(); ++i) {
            if (i != 0U) {
                std::cout << ',';
            }
            const auto& row = rows[i];
            std::cout << "{\"attackers\":" << row.attackers
                      << ",\"actions\":" << row.actions
                      << ",\"complete\":" << (row.complete ? "true" : "false")
                      << ",\"generation_limit\":" << row.generation_limit
                      << ",\"average_microseconds\":" << row.average_microseconds
                      << '}';
        }
        std::cout << "]}\n";
    } else {
        for (const auto& row : rows) {
            std::cout << "attackers=" << row.attackers
                      << " actions=" << row.actions
                      << " complete=" << (row.complete ? 1 : 0)
                      << " generation_limit=" << row.generation_limit
                      << " average_us=" << row.average_microseconds << '\n';
        }
    }
    return 0;
}
