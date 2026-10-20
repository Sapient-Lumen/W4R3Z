#include "iotox/mutorr/cube.hpp"
#include "iotox/network.hpp"
#include "iotox/protocol/frame.hpp"
#include "iotox/security/recovery.hpp"
#include "iotox/toxcore/dynamic_library.hpp"
#include "iotox/transport.hpp"
#include "iotox/version.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

namespace {

void print_usage(std::ostream &output) {
    output << "IoTox " << iotox::kVersion << " (" << iotox::kRevision << ")\n"
           << "Usage:\n"
           << "  iotox info\n"
           << "  iotox frame-demo\n"
           << "  iotox cube-demo [--nodes N] [--neighbors N] [--replicas N] [--namespaces N]\n"
           << "  iotox recovery-contract\n"
           << "  iotox recovery-self-test [--argon2-library PATH] [--wordlist PATH]\n"
           << "  iotox toxcore-probe [--library PATH]\n"
           << "  iotox node [--library PATH] [--state PATH] [--network tox/native] [--run-ms N]\n"
           << "  iotox --version\n";
}

std::optional<std::string> option_value(
    std::span<const std::string_view> arguments, std::string_view option) {
    for (std::size_t index = 0; index < arguments.size(); ++index) {
        if (arguments[index] == option && index + 1U < arguments.size()) {
            return std::string(arguments[index + 1U]);
        }
    }
    return std::nullopt;
}

iotox::Result<std::uint64_t> parse_u64(std::string_view text, std::string_view label) {
    if (text.empty() || text.front() == '-') {
        return iotox::Status{iotox::ErrorCode::invalid_argument,
                             std::string(label) + " must be a non-negative integer"};
    }
    try {
        std::size_t consumed = 0;
        const unsigned long long value = std::stoull(std::string(text), &consumed, 10);
        if (consumed != text.size()) {
            return iotox::Status{iotox::ErrorCode::invalid_argument,
                                 std::string(label) + " contains trailing characters"};
        }
        if (value > std::numeric_limits<std::uint64_t>::max()) {
            return iotox::Status{iotox::ErrorCode::invalid_argument,
                                 std::string(label) + " is outside the supported range"};
        }
        return static_cast<std::uint64_t>(value);
    } catch (const std::exception &) {
        return iotox::Status{iotox::ErrorCode::invalid_argument,
                             std::string(label) + " must be a non-negative integer"};
    }
}

int command_info() {
    std::cout << "project=" << iotox::kProjectName << "\n"
              << "version=" << iotox::kVersion << "\n"
              << "revision=" << iotox::kRevision << "\n"
              << "codename=" << iotox::kCodename << "\n"
              << "language=C++20\n"
              << "mutorr-role=optional namespace replication planner\n"
              << "mutorr-topology=deterministic bounded-degree small circles\n"
              << "mutorr-placement=rendezvous custodians (research mixer)\n"
              << "mutorr-head=fixed-size linked canonical record (signing pending)\n"
              << "toxcore-target=" << iotox::kToxcoreTarget << "\n";

    for (const iotox::NetworkCapability &capability : iotox::network_capabilities()) {
        std::cout << capability.stack.name() << "=" << capability.status << " -- " << capability.intent << "\n";
    }
    return EXIT_SUCCESS;
}

int command_frame_demo() {
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::hello;
    frame.message_id = 1;
    frame.payload = {'I', 'o', 'T', 'o', 'x'};
    auto encoded = iotox::protocol::encode(frame);
    if (!encoded) {
        std::cerr << encoded.status().message() << "\n";
        return EXIT_FAILURE;
    }
    auto decoded = iotox::protocol::decode(encoded.value());
    if (!decoded) {
        std::cerr << decoded.status().message() << "\n";
        return EXIT_FAILURE;
    }
    std::cout << "encoded-bytes=" << encoded.value().size() << "\n"
              << "message-id=" << decoded.value().message_id << "\n"
              << "payload-bytes=" << decoded.value().payload.size() << "\n";
    return EXIT_SUCCESS;
}


int command_cube_demo(std::span<const std::string_view> arguments) {
    std::uint64_t node_count = 30U;
    std::uint64_t neighbor_count = 4U;
    std::uint64_t replica_count = 3U;
    std::uint64_t namespace_count = 4096U;

    const auto parse_option = [&](std::string_view option, std::uint64_t &destination) -> iotox::Status {
        if (const auto text = option_value(arguments, option)) {
            auto parsed = parse_u64(*text, option);
            if (!parsed) {
                return parsed.status();
            }
            destination = parsed.value();
        }
        return iotox::Status::success();
    };

    for (const auto &[option, destination] :
         {std::pair{"--nodes", &node_count}, std::pair{"--neighbors", &neighbor_count},
          std::pair{"--replicas", &replica_count}, std::pair{"--namespaces", &namespace_count}}) {
        const iotox::Status parsed = parse_option(option, *destination);
        if (!parsed.ok()) {
            std::cerr << parsed.message() << '\n';
            return 2;
        }
    }

    if (node_count == 0U || node_count > 100000U) {
        std::cerr << "--nodes must be between 1 and 100000\n";
        return 2;
    }
    if (neighbor_count > 64U || replica_count == 0U || replica_count > 32U ||
        namespace_count > 1000000U) {
        std::cerr << "cube-demo limits: neighbors<=64, replicas=1..32, namespaces<=1000000\n";
        return 2;
    }

    std::vector<iotox::mutorr::Id256> members;
    members.reserve(static_cast<std::size_t>(node_count));
    for (std::uint64_t index = 0U; index < node_count; ++index) {
        members.push_back(iotox::mutorr::synthetic_id(index + 1U, 0x4E4F4445U));
    }

    auto cube = iotox::mutorr::Cube::build(
        members,
        {.neighbor_count = static_cast<std::size_t>(neighbor_count),
         .replication_factor = static_cast<std::size_t>(replica_count)});
    if (!cube) {
        std::cerr << cube.status().message() << '\n';
        return 2;
    }

    std::vector<std::size_t> load(cube.value().size(), 0U);
    for (std::uint64_t index = 0U; index < namespace_count; ++index) {
        const auto namespace_id = iotox::mutorr::synthetic_id(index + 1U, 0x4E414D45U);
        for (const std::size_t custodian : cube.value().custodian_indices(namespace_id)) {
            ++load[custodian];
        }
    }

    const auto [minimum, maximum] = std::minmax_element(load.begin(), load.end());
    const std::uint64_t full_mesh_edges = node_count * (node_count - 1U) / 2U;
    const double reduction = full_mesh_edges == 0U
                                 ? 0.0
                                 : 100.0 * (1.0 - static_cast<double>(cube.value().edge_count()) /
                                                      static_cast<double>(full_mesh_edges));

    std::cout << "members=" << cube.value().size() << '\n'
              << "max-degree=" << cube.value().max_degree() << '\n'
              << "cube-edges=" << cube.value().edge_count() << '\n'
              << "full-mesh-edges=" << full_mesh_edges << '\n'
              << std::fixed << std::setprecision(2)
              << "edge-reduction-percent=" << reduction << '\n'
              << "diameter-hops=" << cube.value().diameter() << '\n'
              << "replication-factor="
              << std::min<std::size_t>(cube.value().config().replication_factor, cube.value().size()) << '\n'
              << "sampled-namespaces=" << namespace_count << '\n'
              << "custodian-load-min=" << *minimum << '\n'
              << "custodian-load-max=" << *maximum << '\n';

    const auto first_neighbors = cube.value().neighbor_indices(0U);
    std::cout << "member-0-neighbors=";
    for (std::size_t index = 0U; index < first_neighbors.size(); ++index) {
        if (index != 0U) {
            std::cout << ',';
        }
        std::cout << cube.value().member(first_neighbors[index]).hex().substr(0U, 12U);
    }
    std::cout << '\n';
    return EXIT_SUCCESS;
}


int command_recovery_contract() {
    using iotox::security::RecallContract;
    std::cout << "contract=" << RecallContract::id << "\n"
              << "algorithm=" << RecallContract::algorithm << "\n"
              << "argon2-version=" << RecallContract::argon2_version << "\n"
              << "memory-kib=" << RecallContract::memory_kib << "\n"
              << "iterations=" << RecallContract::iterations << "\n"
              << "parallelism=" << RecallContract::parallelism << "\n"
              << "output-bytes=" << RecallContract::output_bytes << "\n"
              << "salt-hex="
              << iotox::security::hex_encode(std::span<const std::uint8_t>(RecallContract::salt))
              << "\n"
              << "phrase-words=" << RecallContract::phrase_words << "\n"
              << "wordlist-entries=" << RecallContract::wordlist_entries << "\n"
              << std::fixed << std::setprecision(3)
              << "generated-entropy-bits=" << RecallContract::generated_entropy_bits << "\n"
              << "wordlist-sha256=" << RecallContract::wordlist_sha256 << "\n"
              << "offline-guessing=accepted-by-design\n"
              << "vendor-recovery-authority=none\n";
    return EXIT_SUCCESS;
}

int command_recovery_self_test(std::span<const std::string_view> arguments) {
    const std::filesystem::path library_path =
        option_value(arguments, "--argon2-library").value_or("");
    const std::filesystem::path wordlist_path = option_value(arguments, "--wordlist").value_or(
        "third_party/eff_large_wordlist_2016-07-18.txt");

    auto wordlist = iotox::security::RecallWordList::load(wordlist_path);
    if (!wordlist) {
        std::cerr << wordlist.status().message() << "\n";
        return 3;
    }
    auto phrase = iotox::security::RecallPhrase::parse(
        iotox::security::kRecoveryKnownAnswerPhrase, wordlist.value());
    if (!phrase) {
        std::cerr << phrase.status().message() << "\n";
        return 3;
    }
    auto library = iotox::security::DynamicArgon2::load(library_path);
    if (!library) {
        std::cerr << library.status().message();
        return 3;
    }
    auto root = library.value().derive(phrase.value());
    if (!root) {
        std::cerr << root.status().message() << "\n";
        return 3;
    }

    const std::string actual = iotox::security::hex_encode(root.value().bytes());
    const bool matches = actual == iotox::security::kRecoveryKnownAnswerHex;
    std::cout << "contract=" << iotox::security::RecallContract::id << "\n"
              << "argon2-library=" << library.value().loaded_path() << "\n"
              << "known-answer=" << (matches ? "pass" : "FAIL") << "\n"
              << "test-root=" << actual << "\n";
    return matches ? EXIT_SUCCESS : EXIT_FAILURE;
}

int command_probe(std::span<const std::string_view> arguments) {
    const std::filesystem::path library_path = option_value(arguments, "--library").value_or("");
    auto library = iotox::toxcore::DynamicToxcore::load(library_path);
    if (!library) {
        std::cerr << library.status().message();
        return 3;
    }
    std::cout << "loaded=" << library.value().loaded_path() << "\n"
              << "toxcore-version=" << library.value().version().str() << "\n";
    return EXIT_SUCCESS;
}

int command_node(std::span<const std::string_view> arguments) {
    iotox::ToxTransport::Config config;
    config.toxcore_library = option_value(arguments, "--library").value_or("");
    config.state_path = option_value(arguments, "--state").value_or(".iotox.toxsave");

    if (const auto network_text = option_value(arguments, "--network")) {
        auto network = iotox::parse_network_stack(*network_text);
        if (!network) {
            std::cerr << network.status().message() << "\n";
            return 2;
        }
        config.network = network.value();
    }

    std::uint64_t run_ms = 500;
    if (const auto run_text = option_value(arguments, "--run-ms")) {
        auto parsed = parse_u64(*run_text, "--run-ms");
        if (!parsed) {
            std::cerr << parsed.status().message() << "\n";
            return 2;
        }
        run_ms = parsed.value();
    }

    iotox::ToxTransport transport(std::move(config));
    const iotox::Status started = transport.start();
    if (!started.ok()) {
        std::cerr << started.message() << "\n";
        return 3;
    }

    std::cout << "address=" << transport.address_hex() << "\n";
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(run_ms);
    while (std::chrono::steady_clock::now() < deadline) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50))) {
            std::cout << "event=" << iotox::to_string(event->kind) << " message=" << event->message << "\n";
        }
    }
    transport.stop();
    return EXIT_SUCCESS;
}

}  // namespace

int main(int argc, char **argv) {
    try {
        std::vector<std::string_view> arguments;
        arguments.reserve(static_cast<std::size_t>(argc > 1 ? argc - 1 : 0));
        for (int index = 1; index < argc; ++index) {
            arguments.emplace_back(argv[index]);
        }

        if (arguments.empty()) {
            print_usage(std::cout);
            return EXIT_SUCCESS;
        }
        if (arguments.front() == "--version" || arguments.front() == "version") {
            std::cout << iotox::kProjectName << " " << iotox::kVersion << " " << iotox::kRevision << "\n";
            return EXIT_SUCCESS;
        }
        if (arguments.front() == "info") {
            return command_info();
        }
        if (arguments.front() == "frame-demo") {
            return command_frame_demo();
        }
        if (arguments.front() == "cube-demo") {
            return command_cube_demo(arguments);
        }
        if (arguments.front() == "recovery-contract") {
            return command_recovery_contract();
        }
        if (arguments.front() == "recovery-self-test") {
            return command_recovery_self_test(arguments);
        }
        if (arguments.front() == "toxcore-probe") {
            return command_probe(arguments);
        }
        if (arguments.front() == "node") {
            return command_node(arguments);
        }
        if (arguments.front() == "--help" || arguments.front() == "help") {
            print_usage(std::cout);
            return EXIT_SUCCESS;
        }

        std::cerr << "unknown command: " << arguments.front() << "\n";
        print_usage(std::cerr);
        return 2;
    } catch (const std::exception &exception) {
        std::cerr << "fatal: " << exception.what() << "\n";
        return EXIT_FAILURE;
    }
}
