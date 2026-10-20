#include "iotox/mutorr/cube.hpp"
#include "iotox/mutorr/head.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace {

struct BenchmarkConfig {
    std::size_t nodes{30U};
    std::size_t namespaces{200000U};
    std::size_t rounds{5U};
};

bool parse_size(std::string_view text, std::size_t &output) {
    if (text.empty() || text.front() == '-') {
        return false;
    }
    try {
        std::size_t consumed = 0U;
        const unsigned long long value = std::stoull(std::string(text), &consumed, 10);
        if (consumed != text.size() || value > std::numeric_limits<std::size_t>::max()) {
            return false;
        }
        output = static_cast<std::size_t>(value);
        return true;
    } catch (...) {
        return false;
    }
}

bool parse_arguments(std::span<char *> arguments, BenchmarkConfig &config) {
    for (std::size_t index = 0U; index < arguments.size(); ++index) {
        const std::string_view option(arguments[index]);
        if (index + 1U >= arguments.size()) {
            return false;
        }
        if (option == "--nodes") {
            if (!parse_size(arguments[++index], config.nodes)) {
                return false;
            }
        } else if (option == "--namespaces") {
            if (!parse_size(arguments[++index], config.namespaces)) {
                return false;
            }
        } else if (option == "--rounds") {
            if (!parse_size(arguments[++index], config.rounds)) {
                return false;
            }
        } else {
            return false;
        }
    }
    return config.nodes > 0U && config.nodes <= 100000U && config.namespaces > 0U &&
           config.namespaces <= 10000000U && config.rounds > 0U && config.rounds <= 1000U;
}

std::vector<iotox::mutorr::Id256> make_members(std::size_t count) {
    std::vector<iotox::mutorr::Id256> members;
    members.reserve(count);
    for (std::size_t index = 0U; index < count; ++index) {
        members.push_back(
            iotox::mutorr::synthetic_id(static_cast<std::uint64_t>(index + 1U), 0x4E4F4445U));
    }
    return members;
}

}  // namespace

int main(int argc, char **argv) {
    BenchmarkConfig config;
    if (!parse_arguments(std::span<char *>(argv + 1, static_cast<std::size_t>(argc - 1)), config)) {
        std::cerr << "usage: iotox_bench [--nodes N] [--namespaces N] [--rounds N]\n";
        return EXIT_FAILURE;
    }

    const auto members = make_members(config.nodes);
    std::uint64_t checksum = 0U;

    const std::size_t build_iterations = config.rounds * 100U;
    const auto build_start = std::chrono::steady_clock::now();
    for (std::size_t iteration = 0U; iteration < build_iterations; ++iteration) {
        auto cube = iotox::mutorr::Cube::build(members);
        if (!cube) {
            std::cerr << cube.status().message() << '\n';
            return EXIT_FAILURE;
        }
        checksum += static_cast<std::uint64_t>(cube.value().edge_count());
    }
    const auto build_end = std::chrono::steady_clock::now();

    auto cube = iotox::mutorr::Cube::build(members);
    if (!cube) {
        std::cerr << cube.status().message() << '\n';
        return EXIT_FAILURE;
    }

    const std::size_t placement_operations = config.rounds * config.namespaces;
    std::array<std::size_t, 3U> selected{};
    const auto placement_start = std::chrono::steady_clock::now();
    for (std::size_t round = 0U; round < config.rounds; ++round) {
        for (std::size_t item = 0U; item < config.namespaces; ++item) {
            const auto namespace_id = iotox::mutorr::synthetic_id(
                static_cast<std::uint64_t>(item + round * config.namespaces + 1U), 0x4E414D45U);
            const std::size_t selected_count = cube.value().custodian_indices_into(namespace_id, selected);
            for (std::size_t selection = 0U; selection < selected_count; ++selection) {
                const std::size_t index = selected[selection];
                checksum ^= static_cast<std::uint64_t>(index + 1U) * 0x9E3779B97F4A7C15ULL;
            }
        }
    }
    const auto placement_end = std::chrono::steady_clock::now();

    iotox::mutorr::HeadRecord current;
    current.namespace_id = iotox::mutorr::synthetic_id(1U, 0x4E414D45U);
    current.writer_key = iotox::mutorr::synthetic_id(1U, 0x57524954U);
    current.root = iotox::mutorr::synthetic_id(1U, 0x524F4F54U);
    std::size_t head_operations = config.rounds * config.namespaces;
    const auto head_start = std::chrono::steady_clock::now();
    for (std::size_t operation = 0U; operation < head_operations; ++operation) {
        iotox::mutorr::HeadRecord candidate = current;
        candidate.generation = current.generation + 1U;
        candidate.previous = current.root;
        candidate.root = iotox::mutorr::synthetic_id(
            static_cast<std::uint64_t>(operation + 2U), 0x524F4F54U);
        const auto decision = iotox::mutorr::evaluate_head(&current, candidate);
        checksum += static_cast<std::uint64_t>(decision == iotox::mutorr::HeadDecision::accept_advance);
        current = candidate;
    }
    const auto head_end = std::chrono::steady_clock::now();

    const auto build_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(build_end - build_start).count();
    const auto placement_ns =
        std::chrono::duration_cast<std::chrono::nanoseconds>(placement_end - placement_start).count();
    const auto head_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(head_end - head_start).count();

    const auto per_operation = [](long long elapsed_ns, std::size_t operations) {
        return static_cast<double>(elapsed_ns) / static_cast<double>(operations);
    };
    const auto operations_per_second = [](long long elapsed_ns, std::size_t operations) {
        return 1.0e9 * static_cast<double>(operations) / static_cast<double>(elapsed_ns);
    };

    std::cout << std::fixed << std::setprecision(2)
              << "nodes=" << config.nodes << '\n'
              << "namespaces-per-round=" << config.namespaces << '\n'
              << "rounds=" << config.rounds << '\n'
              << "cube-build-ns-per-op=" << per_operation(build_ns, build_iterations) << '\n'
              << "cube-build-ops-per-second=" << operations_per_second(build_ns, build_iterations) << '\n'
              << "custodian-select-ns-per-op=" << per_operation(placement_ns, placement_operations) << '\n'
              << "custodian-select-ops-per-second="
              << operations_per_second(placement_ns, placement_operations) << '\n'
              << "head-evaluate-ns-per-op=" << per_operation(head_ns, head_operations) << '\n'
              << "head-evaluate-ops-per-second=" << operations_per_second(head_ns, head_operations) << '\n'
              << "checksum=" << checksum << '\n';
    return EXIT_SUCCESS;
}
