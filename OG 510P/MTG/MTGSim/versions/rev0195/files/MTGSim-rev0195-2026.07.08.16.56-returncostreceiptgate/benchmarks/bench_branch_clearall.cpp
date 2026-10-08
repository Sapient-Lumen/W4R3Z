#include "mtgsim/engine.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

namespace {

struct Options {
    std::size_t journal_entries = 60000;
    int branches = 20;
    std::size_t kind_bytes = 40;
    std::size_t detail_bytes = 160;
    bool json = false;
};

std::size_t parse_size(const char* value, const char* name) {
    char* end = nullptr;
    const unsigned long long parsed = std::strtoull(value, &end, 10);
    if (end == value || *end != '\0' || parsed > std::numeric_limits<std::size_t>::max()) {
        throw std::invalid_argument(std::string("invalid ") + name + "=" + value);
    }
    return static_cast<std::size_t>(parsed);
}

int parse_int(const char* value, const char* name) {
    char* end = nullptr;
    const long parsed = std::strtol(value, &end, 10);
    if (end == value || *end != '\0' || parsed < 0 || parsed > std::numeric_limits<int>::max()) {
        throw std::invalid_argument(std::string("invalid ") + name + "=" + value);
    }
    return static_cast<int>(parsed);
}

Options parse_args(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--journal-entries" && i + 1 < argc) {
            options.journal_entries = parse_size(argv[++i], "--journal-entries");
        } else if (arg == "--branches" && i + 1 < argc) {
            options.branches = parse_int(argv[++i], "--branches");
        } else if (arg == "--kind-bytes" && i + 1 < argc) {
            options.kind_bytes = parse_size(argv[++i], "--kind-bytes");
        } else if (arg == "--detail-bytes" && i + 1 < argc) {
            options.detail_bytes = parse_size(argv[++i], "--detail-bytes");
        } else if (arg == "--json") {
            options.json = true;
        } else if (arg == "--help") {
            std::cout
                << "usage: bench_branch_clearall [--journal-entries N] [--branches N] "
                   "[--kind-bytes N] [--detail-bytes N] [--json]\n";
            std::exit(0);
        } else {
            throw std::invalid_argument("unknown or incomplete argument: " + arg);
        }
    }
    return options;
}

} // namespace

int main(int argc, char** argv) {
    const Options options = parse_args(argc, argv);
    mtgsim::GameState source{};
    source.events.reserve(options.journal_entries);
    for (std::size_t i = 0; i < options.journal_entries; ++i) {
        source.events.push_back(mtgsim::Event{
            .sequence = static_cast<mtgsim::u64>(i + 1),
            .kind = std::string(options.kind_bytes, 'k'),
            .detail = std::string(options.detail_bytes, 'd'),
        });
    }
    source.next_event_sequence = static_cast<mtgsim::u64>(options.journal_entries + 1);

    std::uint64_t sink = 0;
    const auto begin = std::chrono::steady_clock::now();
    for (int i = 0; i < options.branches; ++i) {
        const auto branch = mtgsim::make_branch_state(source, mtgsim::JournalRetention::ClearAll);
        sink += branch.next_event_sequence + static_cast<std::uint64_t>(branch.events.size());
    }
    const auto end = std::chrono::steady_clock::now();
    const auto elapsed_us = std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count();

    if (options.json) {
        std::cout << "{"
                  << "\"schema\":\"mtgsim.branch_clearall_microbenchmark.v1\","
                  << "\"scope\":\"isolates ClearAll branch construction from a source with heap-backed Event journal rows; not an end-to-end search benchmark\","
                  << "\"journal_entries\":" << options.journal_entries << ','
                  << "\"branches\":" << options.branches << ','
                  << "\"kind_bytes\":" << options.kind_bytes << ','
                  << "\"detail_bytes\":" << options.detail_bytes << ','
                  << "\"elapsed_us\":" << elapsed_us << ','
                  << "\"sink\":" << sink
                  << "}\n";
    } else {
        std::cout << "journal_entries=" << options.journal_entries
                  << " branches=" << options.branches
                  << " kind_bytes=" << options.kind_bytes
                  << " detail_bytes=" << options.detail_bytes
                  << " elapsed_us=" << elapsed_us
                  << " sink=" << sink << '\n';
    }
    return 0;
}
