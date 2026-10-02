#pragma once

#include "toxsync/hash.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <vector>

namespace toxsync {

struct BlockRecord {
    std::uint32_t weak{};
    std::uint32_t length{};
    Hash128 strong{};
    friend constexpr bool operator==(const BlockRecord&, const BlockRecord&) = default;
};
static_assert(sizeof(BlockRecord) == 24);

struct IndexLimits {
    std::uint64_t max_target_size{1ULL << 44U};
    std::uint64_t max_blocks{1ULL << 31U};
    std::uint32_t min_block_size{128};
    std::uint32_t max_block_size{16U * 1024U * 1024U};
};

struct IndexBuildOptions {
    std::uint32_t block_size{4096};
    std::size_t io_buffer_bytes{64U * 1024U};
    IndexLimits limits{};
};

class Index final {
public:
    static constexpr std::uint16_t kFormatVersion = 1;
    static constexpr std::size_t kHeaderBytes = 64;
    static constexpr std::size_t kRecordBytes = 24;

    std::uint32_t block_size{4096};
    std::uint64_t target_size{};
    Digest256 target_digest{};
    std::vector<BlockRecord> blocks{};

    [[nodiscard]] static Index build_file(const std::filesystem::path& target,
                                          std::uint32_t block_size = 4096);
    [[nodiscard]] static Index build_file(const std::filesystem::path& target,
                                          const IndexBuildOptions& options);
    void write_file(const std::filesystem::path& path) const;
    [[nodiscard]] static Index read_file(const std::filesystem::path& path,
                                         const IndexLimits& limits = {});
    [[nodiscard]] std::vector<std::byte> encode() const;
    [[nodiscard]] static Index decode(std::span<const std::byte> bytes,
                                      const IndexLimits& limits = {});
    [[nodiscard]] std::uint64_t expected_block_count() const noexcept;
    [[nodiscard]] std::uint64_t encoded_size() const noexcept;
    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return sizeof(*this) + blocks.capacity() * sizeof(BlockRecord);
    }
    void validate(const IndexLimits& limits = {}) const;
};

} // namespace toxsync
