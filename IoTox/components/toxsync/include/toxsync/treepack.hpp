#pragma once

#include <cstdint>
#include <filesystem>

namespace toxsync {

struct TreePackLimits {
    std::uint64_t max_entries{1'000'000U};
    std::uint64_t max_file_size{1ULL << 40U};
    // Complete canonical artifact ceiling, including headers, paths, file
    // content, and the terminal record. Publishers check it before copying an
    // entry and subscribers reject an oversized artifact before extraction.
    std::uint64_t max_artifact_bytes{1ULL << 40U};
    std::uint32_t max_path_bytes{64U * 1024U};
    // Publisher path sorting spills canonical runs once this approximate
    // resident budget is reached. It bounds memory by active path bytes rather
    // than by the complete directory entry count.
    std::uint64_t sort_memory_bytes{32ULL * 1024ULL * 1024ULL};
    // Multi-pass merge bounds both file descriptors and one-record-per-run
    // memory. Values below two cannot make progress and are rejected.
    std::uint32_t max_open_sort_runs{64U};
};

struct TreePackStats {
    std::uint64_t directories{};
    std::uint64_t files{};
    std::uint64_t content_bytes{};
    std::uint64_t artifact_bytes{};
    std::uint64_t sort_runs{};
    std::uint64_t sort_merge_passes{};
    std::uint64_t peak_sort_buffer_bytes{};
};

[[nodiscard]] TreePackStats pack_tree(const std::filesystem::path& root,
                                      const std::filesystem::path& artifact,
                                      const TreePackLimits& limits = {});

[[nodiscard]] TreePackStats unpack_tree(const std::filesystem::path& artifact,
                                        const std::filesystem::path& destination,
                                        const TreePackLimits& limits = {});

} // namespace toxsync
