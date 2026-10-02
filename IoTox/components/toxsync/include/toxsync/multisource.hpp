#pragma once

#include "toxsync/content_store.hpp"

#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <span>

namespace toxsync {

using SourcePeerId = std::uint64_t;

enum class ScheduledChunkState : std::uint8_t {
    pending,
    in_flight,
    complete,
    failed,
};

enum class SourceFailureDisposition : std::uint8_t {
    retry_source,
    remove_source_for_chunk,
    permanent,
};

enum class MultiSourceWindowStorage : std::uint8_t {
    // The scheduler owns a fixed-capacity copy of the active manifest window.
    // This is the safest default for callers that cannot guarantee lifetime.
    owned,
    // The scheduler borrows the span passed to set_window(). The caller must
    // keep that storage alive and unchanged until set_window(), clear(), or
    // destruction. This avoids a second ContentChunkRef array in bounded
    // content-fabric workers.
    borrowed,
};

struct MultiSourceSchedulerLimits {
    // These are local resource reservations, not protocol-wide ceilings. The
    // scheduler has no special 32-peer/32-lane policy limit. Small deployments
    // retain a compact one-word fast path; larger deployments use a bounded
    // dynamic bitset selected from these values.
    std::size_t maximum_peers{16U};
    std::size_t maximum_window_chunks{4096U};
    std::uint16_t maximum_lanes_per_peer{8U};
    std::uint16_t maximum_attempts_per_chunk{8U};
    // Global simultaneous assignments. This decouples request-table memory
    // from maximum_peers * maximum_lanes_per_peer and is normally constrained
    // by transport/file-descriptor budgets rather than peer count.
    std::size_t maximum_inflight_requests{128U};
    // Constructor-time retained-memory guard. It covers scheduler-owned arrays
    // and makes very large configurations explicit. It is not a network limit.
    std::size_t workspace_budget_bytes{64U * 1024U * 1024U};
    MultiSourceWindowStorage window_storage{MultiSourceWindowStorage::owned};
};

struct SourcePeerUpdate {
    SourcePeerId peer_id{};
    std::uint16_t maximum_lanes{1U};
    std::uint64_t useful_bytes_per_second{};
    std::uint32_t recent_failures{};
};

struct ChunkAssignment {
    std::uint64_t request_id{};
    SourcePeerId peer_id{};
    ContentChunkRef chunk{};
    std::uint16_t attempt{};
    friend constexpr bool operator==(const ChunkAssignment&,
                                     const ChunkAssignment&) = default;
};

struct MultiSourceSchedulerStats {
    std::size_t peers{};
    std::size_t window_chunks{};
    std::size_t pending_chunks{};
    std::size_t in_flight_chunks{};
    std::size_t completed_chunks{};
    std::size_t failed_chunks{};
    std::size_t maximum_inflight_requests{};
    std::size_t availability_words_per_chunk{};
    std::size_t availability_bytes{};
    std::uint64_t completed_bytes{};
    std::uint64_t assignments{};
    std::uint64_t retries{};
    std::size_t resident_bytes{};
};

// Allocation-stable, bounded rarest-first scheduler. For up to 32 peers the
// active window keeps one inline 32-bit mask per chunk. Larger peer sets switch
// to a contiguous dynamic bitset of ceil(maximum_peers / 64) words per chunk.
// No allocation occurs after construction, and retained memory remains a
// direct, inspectable function of the configured peer/window/inflight budgets.
class MultiSourceScheduler final {
public:
    explicit MultiSourceScheduler(MultiSourceSchedulerLimits limits = {});
    ~MultiSourceScheduler();
    MultiSourceScheduler(MultiSourceScheduler&&) noexcept;
    MultiSourceScheduler& operator=(MultiSourceScheduler&&) noexcept;
    MultiSourceScheduler(const MultiSourceScheduler&) = delete;
    MultiSourceScheduler& operator=(const MultiSourceScheduler&) = delete;

    void set_window(std::uint64_t first_chunk,
                    std::span<const ContentChunkRef> chunks);
    void clear() noexcept;

    // Availability bits are little-endian within each byte: bit zero describes
    // first_chunk, bit one describes first_chunk + 1, and so on. The supplied
    // range may cover more than the active window; only its intersection is
    // retained.
    void update_peer(const SourcePeerUpdate& peer,
                     std::uint64_t first_chunk,
                     std::uint32_t bit_count,
                     std::span<const std::byte> availability_bits);
    void remove_peer(SourcePeerId peer_id) noexcept;

    [[nodiscard]] std::optional<ChunkAssignment> next(std::uint64_t request_id);
    [[nodiscard]] std::optional<ChunkAssignment> assignment(
        std::uint64_t request_id) const noexcept;
    [[nodiscard]] bool complete(std::uint64_t request_id) noexcept;
    [[nodiscard]] bool fail(std::uint64_t request_id,
                            SourceFailureDisposition disposition) noexcept;
    [[nodiscard]] bool mark_complete(std::uint64_t chunk_index) noexcept;

    [[nodiscard]] ScheduledChunkState state(std::uint64_t chunk_index) const;
    [[nodiscard]] MultiSourceSchedulerStats stats() const noexcept;
    [[nodiscard]] std::size_t resident_bytes() const noexcept;
    [[nodiscard]] std::uint64_t first_chunk() const noexcept;
    [[nodiscard]] std::size_t window_size() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace toxsync
