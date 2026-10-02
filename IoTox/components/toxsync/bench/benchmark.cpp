#include "toxsync/apply.hpp"
#include "toxsync/index.hpp"
#include "toxsync/planner.hpp"
#include "toxsync/range_source.hpp"
#include "toxsync/rolling_checksum.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {
using Clock = std::chrono::steady_clock;

class TempWorkspace final {
public:
    TempWorkspace() {
        const auto seed = static_cast<unsigned long long>(Clock::now().time_since_epoch().count());
        const auto base = std::filesystem::temp_directory_path();
        for (unsigned attempt = 0; attempt < 100U; ++attempt) {
            path_ = base / ("toxsync-benchmark-" + std::to_string(seed) + "-" + std::to_string(attempt));
            std::error_code error;
            if (std::filesystem::create_directory(path_, error)) return;
            if (error && error != std::errc::file_exists) {
                throw std::runtime_error("cannot create benchmark workspace: " + error.message());
            }
        }
        throw std::runtime_error("cannot allocate a unique benchmark workspace");
    }

    ~TempWorkspace() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }

private:
    std::filesystem::path path_;
};

enum class FixtureMode : std::uint8_t { in_place_changes, shifted_prefix };

void generate_fixture(const std::filesystem::path& target_path,
                      const std::filesystem::path& basis_path,
                      std::uint64_t total,
                      std::size_t block_size,
                      std::size_t change_every,
                      FixtureMode mode) {
    std::ofstream target(target_path, std::ios::binary | std::ios::trunc);
    std::ofstream basis(basis_path, std::ios::binary | std::ios::trunc);
    if (!target || !basis) throw std::runtime_error("benchmark fixture open failed");

    constexpr std::size_t kBufferBytes = 1024U * 1024U;
    std::vector<std::byte> target_buffer(kBufferBytes);
    std::vector<std::byte> basis_buffer(kBufferBytes);
    if (mode == FixtureMode::shifted_prefix) {
        constexpr std::array<std::byte, 37> kPrefix{};
        basis.write(reinterpret_cast<const char*>(kPrefix.data()),
                    static_cast<std::streamsize>(kPrefix.size()));
    }
    std::uint64_t state = 0x123456789abcdef0ULL;
    std::uint64_t offset{};
    while (offset < total) {
        const auto count = static_cast<std::size_t>(std::min<std::uint64_t>(kBufferBytes, total - offset));
        for (std::size_t i = 0; i < count; ++i) {
            state ^= state << 13U;
            state ^= state >> 7U;
            state ^= state << 17U;
            const auto value = static_cast<std::byte>(state & 0xffU);
            target_buffer[i] = value;
            const auto block = (offset + i) / block_size;
            basis_buffer[i] = mode == FixtureMode::shifted_prefix
                ? value
                : (block % change_every == 0U ? std::byte{0x5a} : value);
        }
        target.write(reinterpret_cast<const char*>(target_buffer.data()), static_cast<std::streamsize>(count));
        basis.write(reinterpret_cast<const char*>(basis_buffer.data()), static_cast<std::streamsize>(count));
        if (!target || !basis) throw std::runtime_error("benchmark fixture write failed");
        offset += count;
    }
}

double seconds(Clock::time_point start, Clock::time_point end) {
    return std::chrono::duration<double>(end - start).count();
}

double mib_per_second(std::uint64_t bytes, double elapsed) {
    return elapsed == 0.0 ? 0.0 : static_cast<double>(bytes) / (1024.0 * 1024.0) / elapsed;
}

std::uint64_t peak_rss_kib() {
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

std::size_t parse_positive(int argc,
                           char** argv,
                           int position,
                           std::size_t fallback,
                           std::string_view label,
                           std::size_t multiplier = 1U) {
    if (argc <= position) return fallback;
    const auto value = std::stoull(argv[position]);
    if (value == 0U || value > std::numeric_limits<std::size_t>::max() / multiplier) {
        throw std::invalid_argument(std::string(label) + " is outside benchmark limits");
    }
    return static_cast<std::size_t>(value) * multiplier;
}

std::pair<toxsync::PlannerSearchMode, std::string_view> parse_mode(int argc, char** argv) {
    if (argc <= 7) return {toxsync::PlannerSearchMode::adaptive, "adaptive"};
    const std::string_view mode(argv[7]);
    if (mode == "adaptive") return {toxsync::PlannerSearchMode::adaptive, mode};
    if (mode == "rolling") return {toxsync::PlannerSearchMode::exhaustive_rolling, mode};
    if (mode == "aligned") return {toxsync::PlannerSearchMode::aligned_only, mode};
    throw std::invalid_argument("planner mode must be adaptive, rolling, or aligned");
}

std::pair<FixtureMode, std::string_view> parse_fixture_mode(int argc, char** argv) {
    if (argc <= 8) return {FixtureMode::in_place_changes, "in-place-changes"};
    const std::string_view mode(argv[8]);
    if (mode == "inplace") return {FixtureMode::in_place_changes, "in-place-changes"};
    if (mode == "shifted") return {FixtureMode::shifted_prefix, "shifted-prefix"};
    throw std::invalid_argument("fixture mode must be inplace or shifted");
}
} // namespace

int main(int argc, char** argv) {
    try {
        constexpr std::size_t kKiB = 1024U;
        constexpr std::size_t kMiB = 1024U * 1024U;
        const auto artifact_bytes = parse_positive(argc, argv, 1, 64U * kMiB,
                                                   "artifact MiB", kMiB);
        const auto change_every = parse_positive(argc, argv, 2, 10U, "change stride");
        const auto index_buffer = parse_positive(argc, argv, 3, 64U * kKiB,
                                                 "index buffer KiB", kKiB);
        const auto aligned_buffer = parse_positive(argc, argv, 4, 1024U * kKiB,
                                                   "aligned planner buffer KiB", kKiB);
        const auto rolling_buffer = parse_positive(argc, argv, 5, 256U * kKiB,
                                                   "rolling planner buffer KiB", kKiB);
        const auto apply_buffer = parse_positive(argc, argv, 6, 256U * kKiB,
                                                 "apply buffer KiB", kKiB);
        const auto [planner_mode, planner_mode_name] = parse_mode(argc, argv);
        const auto [fixture_mode, fixture_mode_name] = parse_fixture_mode(argc, argv);
        constexpr std::size_t block_size = 4096U;
        const auto total = static_cast<std::uint64_t>(artifact_bytes);
        TempWorkspace workspace;
        const auto target_path = workspace.path() / "target.bin";
        const auto basis_path = workspace.path() / "basis.bin";
        const auto output_path = workspace.path() / "output.bin";
        generate_fixture(target_path, basis_path, total, block_size, change_every, fixture_mode);

        toxsync::IndexBuildOptions index_options;
        index_options.block_size = static_cast<std::uint32_t>(block_size);
        index_options.io_buffer_bytes = index_buffer;
        const auto index_start = Clock::now();
        const auto index = toxsync::Index::build_file(target_path, index_options);
        const auto index_end = Clock::now();

        toxsync::PlannerOptions planner_options;
        planner_options.aligned_buffer_bytes = aligned_buffer;
        planner_options.rolling_buffer_bytes = rolling_buffer;
        planner_options.search_mode = planner_mode;
        const auto plan_start = Clock::now();
        const auto plan = toxsync::plan_file(index, basis_path, planner_options);
        const auto plan_end = Clock::now();

        toxsync::FileRangeSource source(target_path);
        toxsync::ApplyOptions apply_options;
        apply_options.io_buffer_bytes = apply_buffer;
        apply_options.fsync_on_commit = false;
        const auto apply_start = Clock::now();
        const auto applied = toxsync::apply_file(index, plan, basis_path, source,
                                                  output_path, apply_options);
        const auto apply_end = Clock::now();

        const auto index_s = seconds(index_start, index_end);
        const auto plan_s = seconds(plan_start, plan_end);
        const auto apply_s = seconds(apply_start, apply_end);
        const auto verified = toxsync::verify_file(index, output_path);

        std::cout << std::fixed << std::setprecision(3)
                  << "engine=toxsync-range-v1\n"
                  << "sha256-backend=" << toxsync::sha256_backend_name() << '\n'
                  << "rolling-checksum-backend=" << toxsync::rolling_checksum_backend_name() << '\n'
                  << "artifact-mib=" << artifact_bytes / kMiB << '\n'
                  << "block-size=" << block_size << '\n'
                  << "fixture-mode=" << fixture_mode_name << '\n'
                  << "changed-block-stride=" << change_every << '\n'
                  << "planner-mode=" << planner_mode_name << '\n'
                  << "index-buffer-bytes=" << index_buffer << '\n'
                  << "planner-aligned-buffer-bytes=" << aligned_buffer << '\n'
                  << "planner-rolling-buffer-bytes=" << rolling_buffer << '\n'
                  << "requested-apply-buffer-bytes=" << apply_buffer << '\n'
                  << "blocks=" << index.blocks.size() << '\n'
                  << "index-bytes=" << index.encoded_size() << '\n'
                  << "index-seconds=" << index_s << '\n'
                  << "scan-seconds=" << plan_s << '\n'
                  << "apply-seconds=" << apply_s << '\n'
                  << "index-mib-per-second=" << mib_per_second(total, index_s) << '\n'
                  << "scan-mib-per-second=" << mib_per_second(total, plan_s) << '\n'
                  << "apply-mib-per-second=" << mib_per_second(total, apply_s) << '\n'
                  << "index-resident-bytes=" << index.resident_bytes() << '\n'
                  << "plan-resident-bytes=" << plan.resident_bytes() << '\n'
                  << "planner-temporary-peak-bytes=" << plan.stats.temporary_bytes_peak << '\n'
                  << "planner-file-read-calls=" << plan.stats.basis_read_calls << '\n'
                  << "planner-aligned-blocks-checked=" << plan.stats.aligned_blocks_checked << '\n'
                  << "planner-aligned-blocks-matched=" << plan.stats.aligned_blocks_matched << '\n'
                  << "planner-aligned-bytes-examined=" << plan.stats.aligned_bytes_examined << '\n'
                  << "planner-aligned-probe-aborted-early="
                  << (plan.stats.aligned_probe_aborted_early ? 1 : 0) << '\n'
                  << "planner-aligned-reused-bytes=" << plan.stats.aligned_reused_bytes << '\n'
                  << "planner-rolling-passes=" << plan.stats.rolling_passes << '\n'
                  << "reused-bytes=" << plan.stats.reused_bytes << '\n'
                  << "missing-bytes=" << plan.stats.missing_bytes << '\n'
                  << "missing-ranges=" << plan.missing_ranges.size() << '\n'
                  << "resumed-bytes=" << applied.resumed_bytes << '\n'
                  << "fetched-bytes=" << applied.fetched_bytes << '\n'
                  << "apply-buffer-bytes=" << applied.buffer_bytes << '\n'
                  << "apply-basis-runs=" << applied.basis_runs << '\n'
                  << "apply-source-runs=" << applied.source_runs << '\n'
                  << "apply-partial-read-calls=" << applied.partial_read_calls << '\n'
                  << "apply-basis-read-calls=" << applied.basis_read_calls << '\n'
                  << "apply-source-read-calls=" << applied.source_read_calls << '\n'
                  << "apply-output-write-calls=" << applied.output_write_calls << '\n'
                  << "apply-sync-calls=" << applied.sync_calls << '\n'
                  << "peak-rss-kib=" << peak_rss_kib() << '\n'
                  << "verified=" << (verified ? 1 : 0) << '\n';
        return verified ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "toxsync_bench: " << error.what() << '\n';
        return 1;
    }
}
