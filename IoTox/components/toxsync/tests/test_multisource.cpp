#include "test_harness.hpp"

#include "toxsync/hash.hpp"
#include "toxsync/multisource.hpp"

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

std::vector<toxsync::ContentChunkRef> chunks(std::size_t count,
                                             std::uint64_t first = 100U) {
    std::vector<toxsync::ContentChunkRef> result;
    result.reserve(count);
    std::uint64_t offset{};
    for (std::size_t local = 0U; local < count; ++local) {
        const auto length = static_cast<std::uint32_t>(4096U + local);
        result.push_back({
            .index = first + local,
            .artifact_offset = offset,
            .length = length,
            .digest = digest_number(first + local),
        });
        offset += length;
    }
    return result;
}

std::array<std::byte, 1> bits(unsigned value) {
    return {static_cast<std::byte>(value)};
}

} // namespace

TOXSYNC_TEST(multisource_scheduler_selects_rarest_chunk_and_fastest_source) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 4U;
    limits.maximum_window_chunks = 8U;
    limits.maximum_lanes_per_peer = 2U;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto window = chunks(3U);
    scheduler.set_window(100U, window);

    const auto peer1 = bits(0b00000011U); // chunks 100,101
    const auto peer2 = bits(0b00000110U); // chunks 101,102
    const auto peer3 = bits(0b00000010U); // chunk 101
    scheduler.update_peer({.peer_id = 1U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 8U * 1024U * 1024U},
                          100U, 3U, peer1);
    scheduler.update_peer({.peer_id = 2U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 2U * 1024U * 1024U},
                          100U, 3U, peer2);
    scheduler.update_peer({.peer_id = 3U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 1U * 1024U * 1024U},
                          100U, 3U, peer3);

    const auto first = scheduler.next(1U);
    REQUIRE(first.has_value());
    REQUIRE(first->chunk.index == 100U);
    REQUIRE(first->peer_id == 1U);
    REQUIRE(scheduler.complete(first->request_id));

    const auto second = scheduler.next(2U);
    REQUIRE(second.has_value());
    REQUIRE(second->chunk.index == 102U);
    REQUIRE(second->peer_id == 2U);
    REQUIRE(scheduler.complete(second->request_id));
    REQUIRE(scheduler.stats().completed_bytes ==
            window[0].length + window[2].length);
}

TOXSYNC_TEST(multisource_scheduler_merges_inventory_pages_and_fails_over) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 2U;
    limits.maximum_window_chunks = 8U;
    limits.maximum_lanes_per_peer = 1U;
    limits.maximum_attempts_per_chunk = 3U;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto window = chunks(4U, 20U);
    scheduler.set_window(20U, window);

    const auto first_page = bits(0b00000011U);
    const auto second_page = bits(0b00000011U);
    scheduler.update_peer({.peer_id = 10U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 10U},
                          20U, 2U, first_page);
    scheduler.update_peer({.peer_id = 10U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 10U},
                          22U, 2U, second_page);
    const auto all = bits(0b00001111U);
    scheduler.update_peer({.peer_id = 20U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 1U},
                          20U, 4U, all);

    const auto first = scheduler.next(100U);
    REQUIRE(first.has_value());
    REQUIRE(first->peer_id == 10U);
    REQUIRE(scheduler.fail(first->request_id,
                           toxsync::SourceFailureDisposition::remove_source_for_chunk));
    const auto retry = scheduler.next(101U);
    REQUIRE(retry.has_value());
    REQUIRE(retry->chunk.index == first->chunk.index);
    REQUIRE(retry->peer_id == 20U);
    REQUIRE(scheduler.complete(retry->request_id));
}

TOXSYNC_TEST(multisource_scheduler_is_allocation_stable_and_enforces_lane_and_request_ids) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 2U;
    limits.maximum_window_chunks = 16U;
    limits.maximum_lanes_per_peer = 1U;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto resident = scheduler.resident_bytes();
    const auto window = chunks(2U, 1U);
    scheduler.set_window(1U, window);
    const auto all = bits(0b00000011U);
    scheduler.update_peer({.peer_id = 7U, .maximum_lanes = 1U}, 1U, 2U, all);
    const auto lease = scheduler.next(55U);
    REQUIRE(lease.has_value());
    REQUIRE(!scheduler.next(56U).has_value());
    REQUIRE_THROWS(scheduler.next(55U));
    REQUIRE(scheduler.complete(55U));
    REQUIRE(scheduler.next(56U).has_value());
    REQUIRE(scheduler.resident_bytes() == resident);
}

TOXSYNC_TEST(multisource_scheduler_skips_saturated_rare_chunk_for_feasible_work) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 2U;
    limits.maximum_window_chunks = 8U;
    limits.maximum_lanes_per_peer = 1U;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto window = chunks(3U, 40U);
    scheduler.set_window(40U, window);

    // Peer one owns the rare first chunk and the second chunk. Peer two owns
    // the second and third chunks. Once peer one is occupied, the rare first
    // chunk must not block scheduling the third chunk from peer two.
    const auto peer1 = bits(0b00000011U);
    const auto peer2 = bits(0b00000110U);
    scheduler.update_peer({.peer_id = 1U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 10U},
                          40U, 3U, peer1);
    scheduler.update_peer({.peer_id = 2U, .maximum_lanes = 1U,
                           .useful_bytes_per_second = 1U},
                          40U, 3U, peer2);

    const auto first = scheduler.next(1U);
    REQUIRE(first.has_value());
    REQUIRE(first->chunk.index == 40U);
    REQUIRE(first->peer_id == 1U);

    const auto second = scheduler.next(2U);
    REQUIRE(second.has_value());
    REQUIRE(second->chunk.index == 42U);
    REQUIRE(second->peer_id == 2U);
    REQUIRE(scheduler.complete(2U));
    REQUIRE(scheduler.complete(1U));
}

TOXSYNC_TEST(multisource_scheduler_borrows_window_and_exposes_inflight_assignment) {
    toxsync::MultiSourceSchedulerLimits borrowed_limits;
    borrowed_limits.maximum_peers = 4U;
    borrowed_limits.maximum_window_chunks = 64U;
    borrowed_limits.maximum_lanes_per_peer = 2U;
    borrowed_limits.window_storage =
        toxsync::MultiSourceWindowStorage::borrowed;
    toxsync::MultiSourceScheduler borrowed(borrowed_limits);

    auto owned_limits = borrowed_limits;
    owned_limits.window_storage = toxsync::MultiSourceWindowStorage::owned;
    toxsync::MultiSourceScheduler owned(owned_limits);
    REQUIRE(borrowed.resident_bytes() +
                borrowed_limits.maximum_window_chunks *
                    sizeof(toxsync::ContentChunkRef) ==
            owned.resident_bytes());

    const auto window = chunks(4U, 300U);
    borrowed.set_window(300U, window);
    const auto all = bits(0b00001111U);
    borrowed.update_peer({.peer_id = 9U, .maximum_lanes = 2U},
                         300U, 4U, all);
    const auto issued = borrowed.next(777U);
    REQUIRE(issued.has_value());
    const auto lookup = borrowed.assignment(777U);
    REQUIRE(lookup.has_value());
    REQUIRE(*lookup == *issued);
    REQUIRE(borrowed.complete(777U));
    REQUIRE(!borrowed.assignment(777U).has_value());
}

TOXSYNC_TEST(multisource_scheduler_supports_dynamic_peer_sets_beyond_thirty_two) {
    constexpr std::size_t peer_count = 96U;
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = peer_count;
    limits.maximum_window_chunks = 8U;
    limits.maximum_lanes_per_peer = 64U;
    limits.maximum_inflight_requests = 256U;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto window = chunks(4U, 500U);
    scheduler.set_window(500U, window);

    const auto only_first = bits(0b00000001U);
    for (std::size_t peer = 0U; peer < peer_count; ++peer) {
        scheduler.update_peer({
            .peer_id = static_cast<toxsync::SourcePeerId>(peer + 1U),
            .maximum_lanes = 64U,
            .useful_bytes_per_second = static_cast<std::uint64_t>(peer + 1U),
        }, 500U, 1U, only_first);
    }

    const auto assignment = scheduler.next(1U);
    REQUIRE(assignment.has_value());
    REQUIRE(assignment->chunk.index == 500U);
    REQUIRE(assignment->peer_id == peer_count);
    REQUIRE(scheduler.complete(assignment->request_id));
    const auto stats = scheduler.stats();
    REQUIRE(stats.peers == peer_count);
    REQUIRE(stats.availability_words_per_chunk == 2U);
}

TOXSYNC_TEST(multisource_scheduler_enforces_global_inflight_budget_without_lane_ceiling) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 2U;
    limits.maximum_window_chunks = 8U;
    limits.maximum_lanes_per_peer = 1024U;
    limits.maximum_inflight_requests = 3U;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto window = chunks(4U, 700U);
    scheduler.set_window(700U, window);
    const auto all = bits(0b00001111U);
    scheduler.update_peer({.peer_id = 1U, .maximum_lanes = 1024U},
                          700U, 4U, all);

    REQUIRE(scheduler.next(1U).has_value());
    REQUIRE(scheduler.next(2U).has_value());
    REQUIRE(scheduler.next(3U).has_value());
    REQUIRE(!scheduler.next(4U).has_value());
    REQUIRE(scheduler.complete(1U));
    REQUIRE(scheduler.next(4U).has_value());
}

TOXSYNC_TEST(multisource_scheduler_rejects_configuration_over_workspace_budget) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 4096U;
    limits.maximum_window_chunks = 4096U;
    limits.workspace_budget_bytes = 1024U * 1024U;
    REQUIRE_THROWS(toxsync::MultiSourceScheduler(limits));
}

TOXSYNC_TEST(multisource_scheduler_zero_peer_removal_is_a_noop) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 2U;
    limits.maximum_window_chunks = 1U;
    toxsync::MultiSourceScheduler scheduler(limits);
    const auto window = chunks(1U, 0U);
    scheduler.set_window(0U, window);
    const std::array<std::byte, 1U> available{std::byte{1U}};
    scheduler.update_peer({
        .peer_id = 7U,
        .maximum_lanes = 1U,
        .useful_bytes_per_second = 1000U,
    }, 0U, 1U, available);

    scheduler.remove_peer(0U);
    REQUIRE(scheduler.stats().peers == 1U);
    const auto assignment = scheduler.next(1U);
    REQUIRE(assignment.has_value());
    REQUIRE(assignment->peer_id == 7U);
}

TOXSYNC_TEST(multisource_scheduler_transposed_masks_reduce_default_residency) {
    toxsync::MultiSourceSchedulerLimits limits;
    limits.maximum_peers = 16U;
    limits.maximum_window_chunks = 4096U;
    limits.maximum_lanes_per_peer = 8U;
    limits.window_storage = toxsync::MultiSourceWindowStorage::borrowed;
    toxsync::MultiSourceScheduler scheduler(limits);

    // rev0008's transposed mask design stays comfortably below the former
    // peer-bitmap plus larger chunk-slot implementation (roughly 374 KiB here).
    REQUIRE(scheduler.resident_bytes() < 256U * 1024U);
}
