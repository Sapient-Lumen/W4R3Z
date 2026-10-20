#pragma once

#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"

#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>

namespace toxsync {

enum class ContentAvailabilityAnswer : std::uint8_t {
    definitely_missing = 0U,
    possibly_present = 1U,
    unknown = 2U,
};

using ContentAvailabilityQuery = ContentAvailabilityAnswer (*)(
    void* context, std::uint32_t source_id, const Digest256& chunk) noexcept;

enum class ContentLeaseFailure : std::uint8_t {
    busy,
    timeout,
    unavailable,
    protocol_error,
    verification_failed,
    cancelled,
};

enum class ContentLeaseUpdate : std::uint8_t {
    completed,
    retry_scheduled,
    terminal_failure,
    late_or_unknown,
};

struct ContentSchedulerConfig {
    std::size_t max_sources{16U};
    std::size_t max_pending_chunks{256U};
    std::size_t max_inflight{8U};
    std::size_t max_inflight_per_source{4U};
    std::uint8_t retry_budget{5U};
    std::uint64_t lease_timeout_ms{30'000U};
    std::uint64_t base_backoff_ms{250U};
    std::uint64_t maximum_backoff_ms{30'000U};
    std::uint64_t initial_goodput_bytes_per_second{256U * 1024U};
};

struct ContentSourceSnapshot {
    std::uint32_t source_id{};
    bool online{};
    std::uint16_t inflight{};
    std::uint64_t inflight_bytes{};
    std::uint64_t goodput_bytes_per_second{};
    std::uint64_t round_trip_microseconds{};
    std::uint64_t backoff_until_ms{};
    std::uint64_t completed_chunks{};
    std::uint64_t failed_chunks{};
};

struct ContentChunkLease {
    std::uint64_t lease_id{};
    std::uint32_t source_id{};
    ContentChunkRef chunk{};
    std::uint64_t deadline_ms{};
    std::uint8_t attempt{};
    ContentAvailabilityAnswer availability{ContentAvailabilityAnswer::unknown};
};

struct ContentSchedulerStats {
    std::size_t sources{};
    std::size_t online_sources{};
    std::size_t pending_chunks{};
    std::size_t inflight_chunks{};
    std::uint64_t chunks_enqueued{};
    std::uint64_t duplicate_chunks{};
    std::uint64_t queue_full_events{};
    std::uint64_t leases_issued{};
    std::uint64_t chunks_completed{};
    std::uint64_t chunks_terminally_failed{};
    std::uint64_t retries_scheduled{};
    std::uint64_t leases_timed_out{};
    std::uint64_t late_results{};
    std::uint64_t completed_bytes{};
};

// Allocation-stable, bounded scheduler for content-addressed chunks. Pending
// work, source state, and leases live in three contiguous arrays allocated by
// the constructor. The hot enqueue/issue/complete/fail paths never allocate.
class ContentScheduler final {
public:
    explicit ContentScheduler(const ContentSchedulerConfig& config = {});
    ~ContentScheduler();
    ContentScheduler(ContentScheduler&&) noexcept;
    ContentScheduler& operator=(ContentScheduler&&) noexcept;
    ContentScheduler(const ContentScheduler&) = delete;
    ContentScheduler& operator=(const ContentScheduler&) = delete;

    [[nodiscard]] bool add_source(
        std::uint32_t source_id,
        std::uint64_t goodput_bytes_per_second = 0U,
        std::uint64_t round_trip_microseconds = 0U);
    [[nodiscard]] bool remove_source(std::uint32_t source_id,
                                     std::uint64_t now_ms = 0U) noexcept;
    [[nodiscard]] bool set_source_online(std::uint32_t source_id,
                                         bool online,
                                         std::uint64_t now_ms = 0U) noexcept;
    [[nodiscard]] bool update_source_hint(
        std::uint32_t source_id,
        std::uint64_t goodput_bytes_per_second,
        std::uint64_t round_trip_microseconds) noexcept;

    // Digest-level deduplication is intentional: repeated manifest entries need
    // one stored chunk, not multiple network transfers.
    [[nodiscard]] bool enqueue(const ContentChunkRef& chunk) noexcept;

    [[nodiscard]] std::optional<ContentChunkLease> next(
        std::uint64_t now_ms,
        ContentAvailabilityQuery availability = nullptr,
        void* availability_context = nullptr) noexcept;

    [[nodiscard]] ContentLeaseUpdate complete(
        std::uint64_t lease_id,
        std::uint64_t bytes_received,
        std::uint64_t elapsed_microseconds,
        std::uint64_t now_ms,
        bool digest_verified = true) noexcept;

    [[nodiscard]] ContentLeaseUpdate fail(
        std::uint64_t lease_id,
        ContentLeaseFailure failure,
        std::uint64_t now_ms,
        std::uint64_t retry_after_ms = 0U) noexcept;

    [[nodiscard]] std::size_t expire(std::uint64_t now_ms) noexcept;
    void cancel_all(std::uint64_t now_ms = 0U) noexcept;

    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] bool has_capacity() const noexcept;
    [[nodiscard]] ContentSchedulerStats stats() const noexcept;
    [[nodiscard]] std::optional<ContentSourceSnapshot> source(
        std::uint32_t source_id) const noexcept;
    [[nodiscard]] std::size_t resident_bytes() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace toxsync
