#include "test_harness.hpp"

#include "toxsync/content_scheduler.hpp"
#include "toxsync/hash.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace {

toxsync::Digest256 digest_number(std::uint64_t value) {
    std::array<std::byte, sizeof(value)> bytes{};
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
        bytes[index] = static_cast<std::byte>(value >> (index * 8U));
    }
    return toxsync::sha256(bytes);
}

struct AvailabilityRow {
    std::uint32_t source{};
    std::vector<toxsync::Digest256> chunks;
};

struct AvailabilityTable {
    std::vector<AvailabilityRow> rows;
};

toxsync::ContentAvailabilityAnswer query_availability(
    void* opaque, std::uint32_t source,
    const toxsync::Digest256& chunk) noexcept {
    const auto& table = *static_cast<AvailabilityTable*>(opaque);
    for (const auto& row : table.rows) {
        if (row.source != source) continue;
        for (const auto& candidate : row.chunks) {
            if (candidate == chunk) {
                return toxsync::ContentAvailabilityAnswer::possibly_present;
            }
        }
        return toxsync::ContentAvailabilityAnswer::definitely_missing;
    }
    return toxsync::ContentAvailabilityAnswer::unknown;
}

toxsync::ContentChunkRef chunk(std::uint64_t index, std::uint32_t length) {
    return toxsync::ContentChunkRef{
        .index = index,
        .artifact_offset = index * 65536U,
        .length = length,
        .digest = digest_number(index + 1U),
    };
}

} // namespace

TOXSYNC_TEST(content_scheduler_uses_rarest_first_and_fastest_source) {
    toxsync::ContentSchedulerConfig config;
    config.max_sources = 4U;
    config.max_pending_chunks = 8U;
    config.max_inflight = 2U;
    config.max_inflight_per_source = 1U;
    toxsync::ContentScheduler scheduler(config);
    REQUIRE(scheduler.add_source(1U, 8U * 1024U * 1024U, 500U));
    REQUIRE(scheduler.add_source(2U, 1U * 1024U * 1024U, 5000U));
    REQUIRE(scheduler.add_source(3U, 2U * 1024U * 1024U, 2000U));

    const auto a = chunk(0U, 128U * 1024U);
    const auto b = chunk(1U, 64U * 1024U);
    const auto c = chunk(2U, 32U * 1024U);
    AvailabilityTable table{{
        {1U, {a.digest, b.digest}},
        {2U, {b.digest, c.digest}},
        {3U, {b.digest}},
    }};
    REQUIRE(scheduler.enqueue(b));
    REQUIRE(scheduler.enqueue(c));
    REQUIRE(scheduler.enqueue(a));

    const auto first = scheduler.next(100U, &query_availability, &table);
    REQUIRE(first.has_value());
    REQUIRE(first->chunk.digest == a.digest);
    REQUIRE(first->source_id == 1U);
    REQUIRE(scheduler.complete(first->lease_id, first->chunk.length,
                               10'000U, 110U) ==
            toxsync::ContentLeaseUpdate::completed);

    const auto second = scheduler.next(120U, &query_availability, &table);
    REQUIRE(second.has_value());
    REQUIRE(second->chunk.digest == c.digest);
    REQUIRE(second->source_id == 2U);
}

TOXSYNC_TEST(content_scheduler_fails_over_and_rejects_late_results) {
    toxsync::ContentSchedulerConfig config;
    config.max_sources = 2U;
    config.max_pending_chunks = 4U;
    config.max_inflight = 1U;
    config.max_inflight_per_source = 1U;
    config.retry_budget = 3U;
    config.base_backoff_ms = 10U;
    config.maximum_backoff_ms = 100U;
    toxsync::ContentScheduler scheduler(config);
    REQUIRE(scheduler.add_source(10U, 10U * 1024U * 1024U, 100U));
    REQUIRE(scheduler.add_source(20U, 1U * 1024U * 1024U, 1000U));
    const auto item = chunk(7U, 8192U);
    AvailabilityTable table{{
        {10U, {item.digest}},
        {20U, {item.digest}},
    }};
    REQUIRE(scheduler.enqueue(item));
    const auto first = scheduler.next(0U, &query_availability, &table);
    REQUIRE(first.has_value());
    REQUIRE(first->source_id == 10U);
    REQUIRE(scheduler.fail(first->lease_id,
                           toxsync::ContentLeaseFailure::unavailable,
                           1U) ==
            toxsync::ContentLeaseUpdate::retry_scheduled);

    const auto second = scheduler.next(11U, &query_availability, &table);
    REQUIRE(second.has_value());
    REQUIRE(second->source_id == 20U);
    REQUIRE(scheduler.complete(second->lease_id, item.length,
                               20'000U, 31U) ==
            toxsync::ContentLeaseUpdate::completed);
    REQUIRE(scheduler.complete(first->lease_id, item.length,
                               20'000U, 32U) ==
            toxsync::ContentLeaseUpdate::late_or_unknown);
    REQUIRE(scheduler.stats().late_results == 1U);
}

TOXSYNC_TEST(content_scheduler_timeout_retry_budget_and_fixed_resident_memory) {
    toxsync::ContentSchedulerConfig config;
    config.max_sources = 1U;
    config.max_pending_chunks = 2U;
    config.max_inflight = 1U;
    config.max_inflight_per_source = 1U;
    config.retry_budget = 2U;
    config.lease_timeout_ms = 5U;
    config.base_backoff_ms = 1U;
    config.maximum_backoff_ms = 2U;
    toxsync::ContentScheduler scheduler(config);
    const auto resident = scheduler.resident_bytes();
    REQUIRE(scheduler.add_source(1U));
    const auto item = chunk(3U, 4096U);
    REQUIRE(scheduler.enqueue(item));
    REQUIRE(scheduler.enqueue(item));
    REQUIRE(scheduler.stats().duplicate_chunks == 1U);

    auto lease = scheduler.next(0U);
    REQUIRE(lease.has_value());
    REQUIRE(scheduler.expire(5U) == 1U);
    lease = scheduler.next(6U);
    REQUIRE(lease.has_value());
    REQUIRE(scheduler.expire(11U) == 1U);
    REQUIRE(scheduler.empty());
    REQUIRE(scheduler.stats().chunks_terminally_failed == 1U);
    REQUIRE(scheduler.resident_bytes() == resident);
}

TOXSYNC_TEST(content_scheduler_readding_an_offline_source_restores_accounting) {
    toxsync::ContentScheduler scheduler;
    REQUIRE(scheduler.add_source(7U, 1024U, 50U));
    REQUIRE(scheduler.stats().sources == 1U);
    REQUIRE(scheduler.stats().online_sources == 1U);

    REQUIRE(scheduler.set_source_online(7U, false, 10U));
    REQUIRE(scheduler.stats().sources == 1U);
    REQUIRE(scheduler.stats().online_sources == 0U);

    REQUIRE(scheduler.add_source(7U, 2048U, 25U));
    REQUIRE(scheduler.stats().sources == 1U);
    REQUIRE(scheduler.stats().online_sources == 1U);
    const auto source = scheduler.source(7U);
    REQUIRE(source.has_value());
    REQUIRE(source->online);
    REQUIRE(source->goodput_bytes_per_second == 2048U);
    REQUIRE(source->round_trip_microseconds == 25U);

    // Exact repeats remain idempotent and must not double count the source.
    REQUIRE(scheduler.add_source(7U, 4096U, 10U));
    REQUIRE(scheduler.stats().sources == 1U);
    REQUIRE(scheduler.stats().online_sources == 1U);
}
