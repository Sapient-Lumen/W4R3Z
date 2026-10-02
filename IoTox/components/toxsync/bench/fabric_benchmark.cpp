#include "toxsync/content_availability.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"
#include "toxsync/lane_budget.hpp"
#include "toxsync/multisource.hpp"

#include <algorithm>
#include <array>
#include <charconv>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {
using Clock = std::chrono::steady_clock;

struct Arguments {
    std::uint64_t mib{128U};
    std::size_t window_chunks{4096U};
    std::size_t peers{16U};
};

[[nodiscard]] std::uint64_t parse_positive(std::string_view text,
                                           std::string_view label) {
    std::uint64_t value{};
    const auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size() ||
        value == 0U) {
        throw std::invalid_argument(std::string(label) +
                                    " must be a positive integer");
    }
    return value;
}

[[nodiscard]] Arguments parse_arguments(int argc, char** argv) {
    if (argc > 4) {
        throw std::invalid_argument(
            "usage: toxsync_fabric_bench [MiB] [window-chunks] [peers]");
    }
    Arguments result;
    if (argc >= 2) result.mib = parse_positive(argv[1], "MiB");
    if (argc >= 3) {
        const auto parsed = parse_positive(argv[2], "window chunks");
        if (parsed > 65536U) {
            throw std::invalid_argument("window chunks exceed benchmark ceiling");
        }
        result.window_chunks = static_cast<std::size_t>(parsed);
    }
    if (argc >= 4) {
        const auto parsed = parse_positive(argv[3], "peers");
        if (parsed > std::numeric_limits<std::uint16_t>::max()) {
            throw std::invalid_argument(
                "peers exceed the current uint16 benchmark/wire profile");
        }
        result.peers = static_cast<std::size_t>(parsed);
    }
    return result;
}

void create_pattern_file(const std::filesystem::path& path, std::uint64_t bytes) {
    constexpr std::size_t buffer_bytes = 1024U * 1024U;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(buffer_bytes);
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create benchmark basis");
    std::uint64_t state = 0x106689d45497fdb5ULL;
    std::uint64_t remaining = bytes;
    while (remaining != 0U) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(remaining, buffer_bytes));
        for (std::size_t index = 0U; index < count; ++index) {
            state ^= state << 7U;
            state ^= state >> 9U;
            state ^= state << 8U;
            buffer[index] = static_cast<std::byte>(state & 0xffU);
        }
        output.write(reinterpret_cast<const char*>(buffer.get()),
                     static_cast<std::streamsize>(count));
        if (!output) throw std::runtime_error("cannot write benchmark basis");
        remaining -= count;
    }
}

void create_prefixed_target(const std::filesystem::path& basis,
                            const std::filesystem::path& target,
                            std::uint64_t basis_bytes) {
    constexpr std::size_t buffer_bytes = 1024U * 1024U;
    constexpr std::size_t prefix_bytes = 12345U;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(buffer_bytes);
    std::ifstream input(basis, std::ios::binary);
    std::ofstream output(target, std::ios::binary | std::ios::trunc);
    if (!input || !output) throw std::runtime_error("cannot create benchmark target");
    for (std::size_t index = 0U; index < prefix_bytes; ++index) {
        buffer[index] = static_cast<std::byte>((index * 131U + 29U) & 0xffU);
    }
    output.write(reinterpret_cast<const char*>(buffer.get()),
                 static_cast<std::streamsize>(prefix_bytes));
    std::uint64_t copied{};
    while (copied < basis_bytes) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(basis_bytes - copied, buffer_bytes));
        input.read(reinterpret_cast<char*>(buffer.get()),
                   static_cast<std::streamsize>(count));
        if (static_cast<std::size_t>(input.gcount()) != count) {
            throw std::runtime_error("benchmark basis ended early");
        }
        output.write(reinterpret_cast<const char*>(buffer.get()),
                     static_cast<std::streamsize>(count));
        if (!output) throw std::runtime_error("cannot write benchmark target");
        copied += count;
    }
}

[[nodiscard]] double elapsed_seconds(Clock::time_point start,
                                     Clock::time_point end) {
    return std::chrono::duration<double>(end - start).count();
}

[[nodiscard]] double rate(std::uint64_t amount, double elapsed) {
    return elapsed == 0.0 ? 0.0 : static_cast<double>(amount) / elapsed;
}

[[nodiscard]] double mib_per_second(std::uint64_t bytes, double elapsed) {
    return rate(bytes, elapsed) / (1024.0 * 1024.0);
}

[[nodiscard]] std::uint64_t peak_rss_kib() {
#if defined(__linux__)
    std::ifstream status("/proc/self/status");
    std::string key;
    while (status >> key) {
        if (key == "VmHWM:") {
            std::uint64_t value{};
            std::string unit;
            status >> value >> unit;
            return value;
        }
        std::string rest;
        std::getline(status, rest);
    }
#endif
    return 0U;
}

[[nodiscard]] toxsync::Digest256 synthetic_digest(std::uint64_t value) {
    std::array<std::byte, sizeof(value)> encoded{};
    for (std::size_t index = 0U; index < encoded.size(); ++index) {
        encoded[index] = static_cast<std::byte>(value >> (index * 8U));
    }
    return toxsync::sha256(encoded);
}

[[nodiscard]] std::vector<toxsync::ContentChunkRef> synthetic_chunks(
    std::size_t count) {
    std::vector<toxsync::ContentChunkRef> chunks;
    chunks.reserve(count);
    std::uint64_t offset{};
    for (std::size_t index = 0U; index < count; ++index) {
        constexpr std::uint32_t length = 64U * 1024U;
        chunks.push_back({
            .index = static_cast<std::uint64_t>(index),
            .artifact_offset = offset,
            .length = length,
            .digest = synthetic_digest(static_cast<std::uint64_t>(index) + 1U),
        });
        offset += length;
    }
    return chunks;
}

void set_bitmap_bit(std::span<std::byte> bits, std::size_t index) {
    const auto byte_index = index / 8U;
    const auto bit_index = static_cast<unsigned>(index % 8U);
    const auto previous = std::to_integer<unsigned char>(bits[byte_index]);
    bits[byte_index] = static_cast<std::byte>(
        previous | static_cast<unsigned char>(1U << bit_index));
}

struct SchedulerMeasurement {
    std::uint64_t assignments{};
    double seconds{};
    std::size_t resident_bytes{};
    std::size_t availability_words_per_chunk{};
    std::size_t availability_bytes{};
    std::uint64_t completed_bytes{};
};

[[nodiscard]] SchedulerMeasurement measure_scheduler(std::size_t chunks_count,
                                                      std::size_t peers_count) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = peers_count;
    limits.maximum_window_chunks = chunks_count;
    limits.maximum_lanes_per_peer = 512U;
    limits.maximum_attempts_per_chunk = 4U;
    limits.maximum_inflight_requests =
        std::min<std::size_t>(chunks_count, 4096U);
    limits.workspace_budget_bytes = 256U * 1024U * 1024U;
    // ContentFabricSession borrows the already-decoded bounded manifest window,
    // so benchmark the production storage mode rather than a defensive copy.
    limits.window_storage = toxsync::MultiSourceWindowStorage::borrowed;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto chunks = synthetic_chunks(chunks_count);
    scheduler.set_window(0U, chunks);

    const auto bitmap_bytes = (chunks_count + 7U) / 8U;
    std::vector<std::byte> bits(bitmap_bytes);
    for (std::size_t peer = 0U; peer < peers_count; ++peer) {
        std::fill(bits.begin(), bits.end(), std::byte{0});
        for (std::size_t chunk = 0U; chunk < chunks_count; ++chunk) {
            // Deterministic overlapping inventories. Every chunk is present on
            // peer zero, while other peers create different rarity classes.
            if (peer == 0U || ((chunk * 17U + peer * 13U) % 11U) < 5U) {
                set_bitmap_bit(bits, chunk);
            }
        }
        scheduler.update_peer({
            .peer_id = static_cast<toxsync::SourcePeerId>(peer + 1U),
            .maximum_lanes = 512U,
            .useful_bytes_per_second =
                static_cast<std::uint64_t>(peers_count - peer) * 1024U * 1024U,
            .recent_failures = static_cast<std::uint32_t>(peer % 3U),
        }, 0U, static_cast<std::uint32_t>(chunks_count), bits);
    }

    std::uint64_t request_id = 1U;
    const auto start = Clock::now();
    while (true) {
        const auto assignment = scheduler.next(request_id);
        if (!assignment) break;
        if (!scheduler.complete(request_id)) {
            throw std::runtime_error("scheduler lost an in-flight request");
        }
        ++request_id;
    }
    const auto end = Clock::now();
    const auto stats = scheduler.stats();
    if (stats.completed_chunks != chunks_count || stats.failed_chunks != 0U) {
        throw std::runtime_error("scheduler did not complete the benchmark window");
    }
    return {
        .assignments = stats.assignments,
        .seconds = elapsed_seconds(start, end),
        .resident_bytes = scheduler.resident_bytes(),
        .availability_words_per_chunk = stats.availability_words_per_chunk,
        .availability_bytes = stats.availability_bytes,
        .completed_bytes = stats.completed_bytes,
    };
}

struct SketchMeasurement {
    std::uint64_t adds{};
    std::uint64_t probes{};
    std::uint64_t positive_hits{};
    double add_seconds{};
    double probe_seconds{};
    std::size_t resident_bytes{};
    double estimated_false_positive_rate{};
};

[[nodiscard]] SketchMeasurement measure_sketch() {
    constexpr std::size_t item_count = 512U;
    constexpr std::size_t iterations = 1024U;
    std::vector<toxsync::Digest256> present;
    std::vector<toxsync::Digest256> absent;
    present.reserve(item_count);
    absent.reserve(item_count);
    for (std::size_t index = 0U; index < item_count; ++index) {
        present.push_back(synthetic_digest(static_cast<std::uint64_t>(index) + 1U));
        absent.push_back(synthetic_digest(
            static_cast<std::uint64_t>(index) + 1U + 1000000U));
    }

    toxsync::ContentAvailabilitySketch sketch;
    const auto manifest = synthetic_digest(0xf00dU);
    const auto add_start = Clock::now();
    for (std::size_t iteration = 0U; iteration < iterations; ++iteration) {
        sketch.reset(manifest, static_cast<std::uint64_t>(iteration));
        for (const auto& digest : present) sketch.add(digest, 64U * 1024U);
    }
    const auto add_end = Clock::now();

    std::uint64_t positive_hits{};
    const auto probe_start = Clock::now();
    for (std::size_t iteration = 0U; iteration < iterations; ++iteration) {
        for (const auto& digest : present) {
            positive_hits += sketch.possibly_contains(digest) ? 1U : 0U;
        }
        for (const auto& digest : absent) {
            positive_hits += sketch.possibly_contains(digest) ? 1U : 0U;
        }
    }
    const auto probe_end = Clock::now();
    return {
        .adds = item_count * iterations,
        .probes = item_count * iterations * 2U,
        .positive_hits = positive_hits,
        .add_seconds = elapsed_seconds(add_start, add_end),
        .probe_seconds = elapsed_seconds(probe_start, probe_end),
        .resident_bytes = sketch.resident_bytes(),
        .estimated_false_positive_rate = sketch.estimated_false_positive_rate(),
    };
}

} // namespace

int main(int argc, char** argv) {
    try {
        const auto arguments = parse_arguments(argc, argv);
        constexpr std::uint64_t unit = 1024U * 1024U;
        if (arguments.mib > std::numeric_limits<std::uint64_t>::max() / unit) {
            throw std::overflow_error("benchmark size overflows");
        }
        const auto basis_bytes = arguments.mib * unit;
        const auto stamp = Clock::now().time_since_epoch().count();
        const auto root = std::filesystem::temp_directory_path() /
            ("toxsync-fabric-bench-" + std::to_string(stamp));
        std::filesystem::create_directories(root);
        struct Cleanup {
            std::filesystem::path path;
            ~Cleanup() {
                std::error_code ignored;
                std::filesystem::remove_all(path, ignored);
            }
        } cleanup{root};

        create_pattern_file(root / "basis", basis_bytes);
        create_prefixed_target(root / "basis", root / "target", basis_bytes);
        const auto target_bytes = std::filesystem::file_size(root / "target");

        toxsync::PagedContentStoreOptions options;
        options.chunking = {
            .min_bytes = 16U * 1024U,
            .average_bytes = 64U * 1024U,
            .max_bytes = 256U * 1024U,
        };
        options.entries_per_page = 256U;
        options.fsync_on_commit = false;
        options.verify_existing_objects = false;
        toxsync::ContentStoreWorkspace workspace;

        const auto basis_start = Clock::now();
        const auto basis = toxsync::build_paged_content_store(
            root / "basis", root / "store", root / "basis.txp", workspace, options);
        const auto basis_end = Clock::now();
        const auto target_start = Clock::now();
        const auto target = toxsync::build_paged_content_store(
            root / "target", root / "store", root / "target.txp", workspace, options);
        const auto target_end = Clock::now();

        toxsync::ContentReconstructOptions reconstruct_options;
        reconstruct_options.fsync_on_commit = false;
        const auto reconstruct_start = Clock::now();
        const auto reconstructed = toxsync::reconstruct_paged_content_manifest(
            root / "target.txp", root / "store", root / "output", workspace,
            reconstruct_options);
        const auto reconstruct_end = Clock::now();

        const auto inventory_count = static_cast<std::uint32_t>(
            std::min<std::uint64_t>(target.metadata.chunk_count, 4096U));
        std::vector<std::byte> inventory_bits(
            (static_cast<std::size_t>(inventory_count) + 7U) / 8U);
        const auto inventory_start = Clock::now();
        const auto inventory = toxsync::fill_content_availability(
            root / "target.txp", root / "store", 0U, inventory_count,
            inventory_bits, false, &workspace);
        const auto inventory_end = Clock::now();

        const auto scheduler = measure_scheduler(
            arguments.window_chunks, arguments.peers);
        toxsync::LaneResourceBudget lane_resources;
        lane_resources.requested_lanes = 4096U;
        lane_resources.peer_advertised_lanes = 8192U;
        lane_resources.transport_slots = 6000U;
        lane_resources.global_inflight_slots = 5000U;
        lane_resources.descriptor_slots = 4500U;
        lane_resources.command_queue_slots = 4300U;
        lane_resources.memory_budget_bytes = 2U * 1024U * 1024U * 1024U;
        lane_resources.reserved_memory_bytes = 64U * 1024U * 1024U;
        lane_resources.bytes_per_lane = 256U * 1024U;
        const auto lane_budget = toxsync::derive_lane_budget(lane_resources);
        const auto sketch = measure_sketch();

        const bool valid =
            reconstructed.metadata.artifact_digest == target.metadata.artifact_digest &&
            reconstructed.metadata.artifact_size == target_bytes &&
            inventory.available_count == inventory_count &&
            inventory.unknown_count == 0U;

        const auto basis_elapsed = elapsed_seconds(basis_start, basis_end);
        const auto target_elapsed = elapsed_seconds(target_start, target_end);
        const auto reconstruct_elapsed =
            elapsed_seconds(reconstruct_start, reconstruct_end);
        const auto inventory_elapsed =
            elapsed_seconds(inventory_start, inventory_end);

        std::cout << std::fixed << std::setprecision(3)
                  << "engine=toxsync-content-store-v2-paged-swarm\n"
                  << "basis-bytes=" << basis_bytes << '\n'
                  << "target-bytes=" << target_bytes << '\n'
                  << "chunk-min=" << options.chunking.min_bytes << '\n'
                  << "chunk-average=" << options.chunking.average_bytes << '\n'
                  << "chunk-max=" << options.chunking.max_bytes << '\n'
                  << "entries-per-page=" << options.entries_per_page << '\n'
                  << "basis-chunks=" << basis.metadata.chunk_count << '\n'
                  << "basis-pages=" << basis.metadata.page_count << '\n'
                  << "target-chunks=" << target.metadata.chunk_count << '\n'
                  << "target-pages=" << target.metadata.page_count << '\n'
                  << "root-manifest-bytes=" << target.metadata.encoded_size() << '\n'
                  << "basis-build-mib-per-second="
                  << mib_per_second(basis_bytes, basis_elapsed) << '\n'
                  << "target-build-mib-per-second="
                  << mib_per_second(target_bytes, target_elapsed) << '\n'
                  << "reconstruct-mib-per-second="
                  << mib_per_second(target_bytes, reconstruct_elapsed) << '\n'
                  << "target-created-bytes=" << target.chunk_bytes_created << '\n'
                  << "target-reused-bytes=" << target.chunk_bytes_reused << '\n'
                  << "target-reuse-percent="
                  << static_cast<double>(target.chunk_bytes_reused) * 100.0 /
                         static_cast<double>(target_bytes) << '\n'
                  << "inventory-chunks=" << inventory_count << '\n'
                  << "inventory-chunks-per-second="
                  << rate(inventory_count, inventory_elapsed) << '\n'
                  << "workspace-resident-bytes=" << workspace.resident_bytes() << '\n'
                  << "scheduler-window-chunks=" << arguments.window_chunks << '\n'
                  << "scheduler-peers=" << arguments.peers << '\n'
                  << "scheduler-resident-bytes=" << scheduler.resident_bytes << '\n'
                  << "scheduler-availability-words-per-chunk="
                  << scheduler.availability_words_per_chunk << '\n'
                  << "scheduler-availability-bytes="
                  << scheduler.availability_bytes << '\n'
                  << "scheduler-assignments-per-second="
                  << rate(scheduler.assignments, scheduler.seconds) << '\n'
                  << "scheduler-completed-bytes=" << scheduler.completed_bytes << '\n'
                  << "resource-derived-lanes=" << lane_budget.lanes << '\n'
                  << "resource-derived-lane-reason="
                  << toxsync::lane_limit_reason_name(lane_budget.limiting_reason) << '\n'
                  << "availability-filter-bytes=" << sketch.resident_bytes << '\n'
                  << "availability-adds-per-second="
                  << rate(sketch.adds, sketch.add_seconds) << '\n'
                  << "availability-probes-per-second="
                  << rate(sketch.probes, sketch.probe_seconds) << '\n'
                  << "availability-positive-hits=" << sketch.positive_hits << '\n'
                  << "availability-estimated-fpr="
                  << sketch.estimated_false_positive_rate << '\n'
                  << "peak-rss-kib=" << peak_rss_kib() << '\n'
                  << "verified=" << (valid ? 1 : 0) << '\n';
        return valid ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "toxsync_fabric_bench: " << error.what() << '\n';
        return 1;
    }
}
