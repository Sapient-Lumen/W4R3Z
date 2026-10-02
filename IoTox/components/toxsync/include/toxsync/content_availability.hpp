#pragma once

#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <utility>
#include <vector>

namespace toxsync {

inline constexpr std::uint16_t kAvailabilityFlagComplete = 1U << 0U;
inline constexpr std::uint16_t kAvailabilityFlagDigestVerified = 1U << 1U;
inline constexpr std::uint16_t kKnownAvailabilityFlags =
    kAvailabilityFlagComplete | kAvailabilityFlagDigestVerified;

struct ContentAvailabilityConfig {
    // Power-of-two storage keeps membership probes branch-light and replaces
    // integer division with a mask. 1 KiB plus the fixed header fits in one
    // IoTox custom-packet frame.
    std::size_t filter_bytes{1024U};
    std::uint8_t hash_functions{7U};
    std::uint64_t salt{0x7478796e632d7632ULL};
};

struct ContentAvailabilityMetadata {
    static constexpr std::uint16_t kFormatVersion = 1U;
    static constexpr std::size_t kHeaderBytes = 128U;

    Digest256 manifest{};
    std::uint64_t sequence{};
    std::uint64_t item_count{};
    std::uint64_t available_bytes{};
    std::uint32_t bit_count{};
    std::uint8_t hash_functions{};
    std::uint16_t flags{};
    std::uint64_t salt{};
    Digest256 filter_digest{};

    [[nodiscard]] std::size_t encoded_size() const noexcept {
        return kHeaderBytes + static_cast<std::size_t>(bit_count / 8U);
    }

    friend constexpr bool operator==(const ContentAvailabilityMetadata&,
                                     const ContentAvailabilityMetadata&) = default;
};

// Compact, conservative peer inventory. A negative answer is exact. A positive
// answer means "possibly present" and must still be followed by a verified
// chunk request. The object owns one fixed-size bitset and performs no
// allocation during add/probe operations.
class ContentAvailabilitySketch final {
public:
    explicit ContentAvailabilitySketch(
        const ContentAvailabilityConfig& config = {});

    void reset(const Digest256& manifest,
               std::uint64_t sequence = 0U,
               std::uint16_t flags = 0U);
    void clear_bits() noexcept;
    void set_flags(std::uint16_t flags);
    void add(const Digest256& chunk, std::uint64_t chunk_bytes = 0U) noexcept;

    [[nodiscard]] bool possibly_contains(const Digest256& chunk) const noexcept;
    [[nodiscard]] ContentAvailabilityMetadata metadata() const;
    [[nodiscard]] const Digest256& manifest() const noexcept { return manifest_; }
    [[nodiscard]] std::uint64_t sequence() const noexcept { return sequence_; }
    [[nodiscard]] std::uint64_t item_count() const noexcept { return item_count_; }
    [[nodiscard]] std::uint64_t available_bytes() const noexcept {
        return available_bytes_;
    }
    [[nodiscard]] std::uint16_t flags() const noexcept { return flags_; }
    [[nodiscard]] std::uint8_t hash_functions() const noexcept {
        return hash_functions_;
    }
    [[nodiscard]] std::uint64_t salt() const noexcept { return salt_; }
    [[nodiscard]] std::span<const std::byte> bits() const noexcept { return bits_; }
    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return bits_.capacity();
    }
    [[nodiscard]] double estimated_false_positive_rate() const noexcept;

private:
    friend std::vector<std::byte> encode_content_availability(
        const ContentAvailabilitySketch& sketch);
    friend ContentAvailabilitySketch decode_content_availability(
        std::span<const std::byte> bytes, std::size_t max_filter_bytes);

    ContentAvailabilitySketch(ContentAvailabilityMetadata metadata,
                              std::vector<std::byte> bits);
    [[nodiscard]] std::pair<std::uint64_t, std::uint64_t>
    hash_pair(const Digest256& chunk) const noexcept;

    Digest256 manifest_{};
    std::uint64_t sequence_{};
    std::uint64_t item_count_{};
    std::uint64_t available_bytes_{};
    std::uint16_t flags_{};
    std::uint8_t hash_functions_{};
    std::uint64_t salt_{};
    std::vector<std::byte> bits_{};
};

struct ContentAvailabilityBuildOptions {
    ContentAvailabilityConfig sketch{};
    bool verify_chunk_digests{false};
    std::size_t io_buffer_bytes{256U * 1024U};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

struct ContentAvailabilityBuildResult {
    ContentAvailabilitySketch sketch;
    ContentManifestMetadata manifest{};
    std::uint64_t available_chunks{};
    std::uint64_t missing_chunks{};
    std::uint64_t corrupt_chunks{};
    std::uint64_t available_bytes{};
    std::uint64_t missing_bytes{};
    std::size_t workspace_reserved_bytes{};
    std::size_t verification_buffer_bytes{};
    std::uint32_t workspace_growth_events{};
};

[[nodiscard]] ContentAvailabilityBuildResult build_content_availability(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t sequence = 0U,
    const ContentAvailabilityBuildOptions& options = {});

[[nodiscard]] ContentAvailabilityBuildResult build_content_availability(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    std::uint64_t sequence = 0U,
    const ContentAvailabilityBuildOptions& options = {});

[[nodiscard]] std::vector<std::byte> encode_content_availability(
    const ContentAvailabilitySketch& sketch);

[[nodiscard]] ContentAvailabilitySketch decode_content_availability(
    std::span<const std::byte> bytes,
    std::size_t max_filter_bytes = 1024U * 1024U);

} // namespace toxsync
