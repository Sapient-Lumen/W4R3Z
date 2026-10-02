#pragma once

#include "toxsync/planner.hpp"
#include "toxsync/range_source.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>

namespace toxsync {

struct ApplyOptions {
    std::size_t io_buffer_bytes{256U * 1024U};
    bool resume{true};
    bool fsync_on_commit{true};
};

struct ApplyStats {
    std::uint64_t resumed_bytes{};
    std::uint64_t reused_bytes{};
    std::uint64_t fetched_bytes{};
    std::uint64_t basis_runs{};
    std::uint64_t source_runs{};
    std::uint64_t partial_read_calls{};
    std::uint64_t basis_read_calls{};
    std::uint64_t source_read_calls{};
    std::uint64_t output_write_calls{};
    std::uint64_t sync_calls{};
    std::uint64_t buffer_bytes{};
    Digest256 output_digest{};
};

[[nodiscard]] ApplyStats apply_file(const Index& index,
                                    const Plan& plan,
                                    const std::filesystem::path& basis,
                                    RangeSource& source,
                                    const std::filesystem::path& output,
                                    const ApplyOptions& options = {});

[[nodiscard]] bool verify_file(const Index& index, const std::filesystem::path& path);

} // namespace toxsync
