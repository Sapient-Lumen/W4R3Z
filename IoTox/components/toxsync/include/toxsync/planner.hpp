#pragma once

#include "toxsync/index.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <limits>
#include <vector>

namespace toxsync {

inline constexpr std::uint64_t kMissingBasisOffset = std::numeric_limits<std::uint64_t>::max();

struct MissingRange {
    std::uint64_t offset{};
    std::uint64_t length{};
    friend constexpr bool operator==(const MissingRange&, const MissingRange&) = default;
};

enum class PlannerSearchMode : std::uint8_t {
    adaptive,
    exhaustive_rolling,
    aligned_only,
};

struct PlanStats {
    std::uint64_t basis_size{};
    std::uint64_t scanned_windows{};
    std::uint64_t weak_hits{};
    std::uint64_t strong_checks{};
    std::uint64_t matched_blocks{};
    std::uint64_t reused_bytes{};
    std::uint64_t missing_bytes{};
    std::uint64_t basis_read_calls{};
    std::uint64_t aligned_blocks_checked{};
    std::uint64_t aligned_blocks_matched{};
    std::uint64_t aligned_reused_bytes{};
    std::uint64_t aligned_bytes_examined{};
    std::uint64_t rolling_passes{};
    std::uint64_t temporary_bytes_peak{};
    bool aligned_probe_aborted_early{};
};

struct Plan {
    std::vector<std::uint64_t> basis_offsets;
    std::vector<MissingRange> missing_ranges;
    PlanStats stats{};

    [[nodiscard]] bool complete_without_source() const noexcept {
        return stats.missing_bytes == 0;
    }

    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return sizeof(*this) + basis_offsets.capacity() * sizeof(std::uint64_t) +
               missing_ranges.capacity() * sizeof(MissingRange);
    }
};

struct PlannerOptions {
    std::uint64_t max_basis_size{1ULL << 44U};
    std::size_t aligned_buffer_bytes{1024U * 1024U};
    std::size_t rolling_buffer_bytes{256U * 1024U};
    PlannerSearchMode search_mode{PlannerSearchMode::adaptive};
    std::uint8_t adaptive_min_aligned_reuse_percent{85};
};

[[nodiscard]] Plan plan_file(const Index& index,
                             const std::filesystem::path& basis,
                             const PlannerOptions& options = {});

} // namespace toxsync
