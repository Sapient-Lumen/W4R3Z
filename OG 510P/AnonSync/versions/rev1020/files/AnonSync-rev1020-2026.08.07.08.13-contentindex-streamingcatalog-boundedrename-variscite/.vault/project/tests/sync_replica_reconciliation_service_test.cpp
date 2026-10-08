#include "sha256_digest.hpp"
#include "sync_replica_delivery_test_channel.hpp"
#include "sync_replica_file_payload_terminal_verification_state.hpp"
#include "sync_replica_reconciliation_service.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

#include <sqlite3.h>
#include <sys/stat.h>
#include <unistd.h>

namespace anonsync {

struct SyncReplicaFilePayloadStoreTestAccess final {
    using SourceCheckpointPublicationSignature = void (
        SyncReplicaFilePayloadStore::*)(
            SyncReplicaSourceManifestCheckpoint&,
            std::string_view) const;
    static_assert(std::is_same_v<
                  decltype(&SyncReplicaFilePayloadStore::
                               publish_source_manifest_checkpoint_or_throw),
                  SourceCheckpointPublicationSignature>,
                  "source checkpoint publication must retain caller-owned chunk storage");

    [[nodiscard]] static SyncReplicaFilePayloadStoreLiveCapabilityCutpoint
    live_cutpoint_excluding_snapshot_or_throw(
        const SyncReplicaFilePayloadStore& store,
        const SyncReplicaFilePayloadStoreSnapshot& snapshot) {
        return store.live_capability_cutpoint_excluding_snapshot_or_throw(
            snapshot, "reconciliation-service request-scope proof");
    }
};

}  // namespace anonsync

namespace {

namespace fs = std::filesystem;

std::uint64_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected_fragment,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected_fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

struct ReplicaHistoryReadTrace final {
    std::uint64_t exact_visible_path_read_count = 0U;
    std::uint64_t complete_visible_projection_read_count = 0U;
    std::uint64_t exact_operation_read_count = 0U;
    std::uint64_t evidence_page_range_read_count = 0U;
    std::uint64_t visible_file_candidate_range_read_count = 0U;
    std::uint64_t complete_operation_projection_read_count = 0U;
    std::uint64_t metadata_row_read_count = 0U;
};

int count_replica_history_reads(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (trace_kind != SQLITE_TRACE_STMT || context == nullptr ||
        statement_pointer == nullptr) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr) return 0;
    auto& trace = *static_cast<ReplicaHistoryReadTrace*>(context);
    const std::string_view text(sql);
    if (text.find("FROM main.sync_replica_visible") !=
        std::string_view::npos) {
        if (text.find("WHERE canonical_path=?") !=
            std::string_view::npos) {
            ++trace.exact_visible_path_read_count;
        } else if (text.find("WHERE v.canonical_path>?") !=
                   std::string_view::npos) {
            ++trace.visible_file_candidate_range_read_count;
        } else if (text.find("ORDER BY canonical_path,visible_ordinal") !=
                   std::string_view::npos) {
            ++trace.complete_visible_projection_read_count;
        }
    }
    if (text.find("FROM main.sync_replica_operations") !=
        std::string_view::npos) {
        if (text.find("WHERE operation_id=?") !=
            std::string_view::npos) {
            ++trace.exact_operation_read_count;
        } else if (text.find("WHERE operation_id>?") !=
                   std::string_view::npos) {
            ++trace.evidence_page_range_read_count;
        } else if (text.find("ORDER BY operation_id") !=
                   std::string_view::npos) {
            ++trace.complete_operation_projection_read_count;
        }
    }
    if (text.find("FROM main.sync_replica_meta WHERE id=1") !=
        std::string_view::npos) {
        ++trace.metadata_row_read_count;
    }
    return 0;
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        path_ = fs::temp_directory_path() /
                ("anonsync-reconciliation-service-" +
                 std::to_string(static_cast<unsigned long long>(::getpid())) +
                 "-" + std::to_string(tick));
        fs::create_directory(path_);
        if (::chmod(path_.c_str(), 0700) != 0) {
            fail("could not make reconciliation-service test root private");
        }
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] fs::path make_private_directory(
        std::string_view name) const {
        const fs::path path = path_ / std::string(name);
        fs::create_directory(path);
        if (::chmod(path.c_str(), 0700) != 0) {
            fail("could not make reconciliation fixture directory private");
        }
        return path;
    }

    [[nodiscard]] fs::path database_path(std::string_view name) const {
        return path_ / (std::string(name) + ".sqlite3");
    }

private:
    fs::path path_;
};

anonsync::SyncSqliteDb open_database(const fs::path& path) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "reconciliation service test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "reconciliation service test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "reconciliation service test durability profile");
    return owner;
}

anonsync::SyncReplicaSqliteOwnerLimits owner_limits(
    std::uint64_t max_operations) {
    anonsync::SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = max_operations;
    value.model.max_context_entries = 256U;
    value.model.max_predecessor_ids = 256U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 32U * 1024U * 1024U;
    value.model.max_retained_context_entries = 32768U;
    value.model.max_retained_predecessor_ids = 32768U;
    value.max_outbox_intents = 256U;
    value.max_outbox_destination_bytes = 64U * 1024U;
    return value;
}

anonsync::SyncReplicaFilePayloadStoreLimits payload_limits() {
    anonsync::SyncReplicaFilePayloadStoreLimits value;
    value.max_entries = 256U;
    value.max_payload_bytes = 1024U * 1024U;
    value.max_indexed_bytes = 64U * 1024U * 1024U;
    value.max_transient_entries = 256U;
    value.max_transient_bytes = 16U * 1024U * 1024U;
    return value;
}

anonsync::SyncReplicaReconciliationProtocolLimits protocol_limits(
    std::uint64_t operations_per_page = 2U) {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model = owner_limits(256U).model;
    value.max_operations_per_page = operations_per_page;
    value.max_canonical_operation_bytes_per_page = 2U * 1024U * 1024U;
    value.max_payloads_per_page = 8U;
    value.max_single_payload_bytes = 1024U * 1024U;
    value.max_payload_bytes_per_page = 4U * 1024U * 1024U;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 8U * 1024U * 1024U;
    return value;
}

class ReplicaFixture final {
public:
    ReplicaFixture(
        const TemporaryDirectory& temporary,
        std::string name,
        std::string folder,
        anonsync::SyncReplicaActor actor,
        anonsync::SyncReplicaSqliteOwnerLimits durable_limits,
        anonsync::SyncReplicaReconciliationProtocolLimits wire_limits,
        anonsync::SyncReplicaFilePayloadStoreLimits store_limits =
            payload_limits(),
        anonsync::SyncReplicaSelectiveSyncPolicy selective_sync_policy =
            anonsync::sync_replica_default_selective_sync_policy(),
        std::uint64_t max_local_reuse_bytes_per_apply =
            anonsync::
                kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        std::uint64_t max_predecessor_projection_bytes_per_apply =
            anonsync::
                kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        std::uint64_t max_terminal_verification_steps_per_apply =
            anonsync::
                kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
        std::uint64_t max_source_manifest_projection_bytes_per_request =
            anonsync::
                kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest)
        : db_(open_database(temporary.database_path(name))),
          payload_root_(temporary.make_private_directory(name + "-payloads")),
          owner_(
              db_.db, folder, actor, durable_limits,
              name + " replica owner"),
          payload_store_(
              folder, payload_root_,
              anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
              store_limits, name + " payload store"),
          service_(
              owner_, payload_store_, std::move(wire_limits),
              name + " reconciliation service",
              std::move(selective_sync_policy),
              max_local_reuse_bytes_per_apply,
              max_predecessor_projection_bytes_per_apply,
              max_terminal_verification_steps_per_apply,
              max_source_manifest_projection_bytes_per_request) {}

    [[nodiscard]] anonsync::SyncReplicaOperation publish_file(
        std::string path,
        std::string payload) {
        const auto put = payload_store_.put_payload_or_throw(payload);
        return owner_.publish_local_file_or_throw(
            std::move(path), put.size_bytes, put.content_sha256);
    }

    [[nodiscard]] anonsync::SyncReplicaOperation publish_file_without_payload(
        std::string path,
        std::string payload) {
        return owner_.publish_local_file_or_throw(
            std::move(path), payload.size(), anonsync::sha256_hex(payload));
    }

    [[nodiscard]] anonsync::SyncReplicaOperation publish_tombstone(
        std::string path) {
        return owner_.publish_local_tombstone_or_throw(std::move(path));
    }

    anonsync::SyncSqliteDb db_;
    fs::path payload_root_;
    anonsync::SyncReplicaSqliteOwner owner_;
    anonsync::SyncReplicaFilePayloadStore payload_store_;
    anonsync::SyncReplicaReconciliationService service_;
};

using Channel = anonsync::SyncReplicaDeliveryChannelAuthority;

Channel channel_to(
    const anonsync::SyncReplicaActor& peer,
    std::string_view transcript) {
    return anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
        peer, transcript, "test-reconciliation-channel");
}

struct PullSummary final {
    std::uint64_t page_count = 0U;
    std::uint64_t reset_count = 0U;
    std::uint64_t inserted_operations = 0U;
    std::uint64_t duplicate_operations = 0U;
    std::uint64_t inserted_payloads = 0U;
    std::uint64_t existing_payloads = 0U;
    anonsync::SyncReplicaReconciliationApplyDisposition terminal =
        anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied;
    std::optional<std::string> blocked_operation_id;
};

PullSummary pull_until_stop(
    ReplicaFixture& requester,
    ReplicaFixture& responder,
    const Channel& requester_channel,
    const Channel& responder_channel,
    std::uint64_t maximum_pages = 64U) {
    PullSummary summary;
    std::optional<std::string> cursor;
    std::optional<std::string> source_digest;
    for (std::uint64_t iteration = 0U; iteration < maximum_pages;
         ++iteration) {
        const auto outbound = requester.service_.make_request_or_throw(
            requester_channel, cursor, source_digest);
        const auto inbound = responder.service_.serve_request_or_throw(
            responder_channel, outbound.request_frame);
        const auto applied = requester.service_.apply_response_or_throw(
            requester_channel, outbound.request, inbound.response_frame);
        ++summary.page_count;
        summary.inserted_operations +=
            applied.inserted_active + applied.inserted_pending +
            applied.inserted_quarantined;
        summary.duplicate_operations += applied.duplicate_operations;
        summary.inserted_payloads += applied.inserted_payloads;
        summary.existing_payloads += applied.existing_payloads;
        summary.terminal = applied.disposition;
        summary.blocked_operation_id = applied.blocked_operation_id;

        if (applied.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::SourceChanged) {
            ++summary.reset_count;
            cursor.reset();
            source_digest.reset();
            continue;
        }
        if (applied.disposition !=
            anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied) {
            return summary;
        }
        if (!applied.has_more) return summary;
        if (!applied.next_after_operation_id.has_value()) {
            fail("nonterminal reconciliation page did not provide a cursor");
        }
        cursor = applied.next_after_operation_id;
        source_digest = applied.source_evidence_set_digest;
    }
    fail("reconciliation pull exceeded its explicit page bound");
}

void require_payload_available(
    anonsync::SyncReplicaFilePayloadStore& store,
    const anonsync::SyncReplicaOperation& operation,
    const std::string& expected,
    const std::string& message) {
    auto snapshot = store.snapshot_or_throw();
    require(
        snapshot.copy_payload_for_operation_or_throw(operation) == expected,
        message);
}

void test_range_and_page_ceiling_are_independent_from_complete_payload_ceiling() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-range-vs-durable-ceiling";
    const anonsync::SyncReplicaActor actor{
        "device-range-vs-durable-ceiling", 1U};
    anonsync::SyncSqliteDb database =
        open_database(temporary.database_path("range-vs-durable"));
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, folder, actor, owner_limits(256U),
        "range-vs-durable replica owner");

    auto large_store_limits = payload_limits();
    large_store_limits.max_payload_bytes = 8U * 1024U * 1024U;
    const fs::path large_root =
        temporary.make_private_directory("range-vs-durable-payloads");
    anonsync::SyncReplicaFilePayloadStore large_store(
        folder, large_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        large_store_limits, "range-vs-durable payload store");
    auto ranged_wire = protocol_limits();
    ranged_wire.max_single_payload_bytes = 1024U * 1024U;
    ranged_wire.max_payload_bytes_per_page = 4U * 1024U * 1024U;
    ranged_wire.max_payload_extent_bytes = 8U * 1024U * 1024U;
    anonsync::SyncReplicaReconciliationService ranged_service(
        owner, large_store, ranged_wire,
        "range-vs-durable reconciliation service");
    (void)ranged_service;
    ++checks;
    require_error(
        [&] {
            anonsync::SyncReplicaReconciliationService rejected(
                owner, large_store, ranged_wire,
                "zero-local-reuse-frontier reconciliation service",
                anonsync::sync_replica_default_selective_sync_policy(), 0U);
            (void)rejected;
        },
        "local reuse byte frontier",
        "reconciliation accepted a zero local-reuse byte frontier");
    require_error(
        [&] {
            anonsync::SyncReplicaReconciliationService rejected(
                owner, large_store, ranged_wire,
                "oversized-local-reuse-frontier reconciliation service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::
                    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply +
                    1U);
            (void)rejected;
        },
        "local reuse byte frontier",
        "reconciliation accepted a local-reuse frontier above the shipping maximum");
    require_error(
        [&] {
            anonsync::SyncReplicaReconciliationService rejected(
                owner, large_store, ranged_wire,
                "zero-predecessor-projection-frontier reconciliation service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::
                    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                0U);
            (void)rejected;
        },
        "predecessor projection byte frontier",
        "reconciliation accepted a zero predecessor-projection byte frontier");
    require_error(
        [&] {
            anonsync::SyncReplicaReconciliationService rejected(
                owner, large_store, ranged_wire,
                "oversized-predecessor-projection-frontier reconciliation service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::
                    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                anonsync::
                    kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply +
                    1U);
            (void)rejected;
        },
        "predecessor projection byte frontier",
        "reconciliation accepted a predecessor-projection frontier above the shipping maximum");

    require_error(
        [&] {
            anonsync::SyncReplicaReconciliationService rejected(
                owner, large_store, ranged_wire,
                "zero-terminal-verification-frontier reconciliation service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::
                    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                anonsync::
                    kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                0U);
            (void)rejected;
        },
        "terminal verification step frontier",
        "reconciliation accepted a zero terminal-verification frontier");
    require_error(
        [&] {
            anonsync::SyncReplicaReconciliationService rejected(
                owner, large_store, ranged_wire,
                "oversized-terminal-verification-frontier reconciliation service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::
                    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                anonsync::
                    kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                anonsync::
                    kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply +
                    1U);
            (void)rejected;
        },
        "terminal verification step frontier",
        "reconciliation accepted a terminal-verification frontier above the shipping maximum");

    anonsync::SyncSqliteDb undersized_database =
        open_database(temporary.database_path("extent-too-small"));
    anonsync::SyncReplicaSqliteOwner undersized_owner(
        undersized_database.db, folder,
        anonsync::SyncReplicaActor{
            "device-extent-too-small", 1U},
        owner_limits(256U), "extent-too-small replica owner");
    const fs::path undersized_root =
        temporary.make_private_directory("extent-too-small-payloads");
    anonsync::SyncReplicaFilePayloadStore undersized_store(
        folder, undersized_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        large_store_limits, "extent-too-small payload store");
    auto extent_too_small = protocol_limits();
    extent_too_small.max_single_payload_bytes = 1024U * 1024U;
    extent_too_small.max_payload_bytes_per_page = 4U * 1024U * 1024U;
    extent_too_small.max_payload_extent_bytes = 4U * 1024U * 1024U;
    require_error(
        [&] {
            anonsync::SyncReplicaReconciliationService rejected(
                undersized_owner, undersized_store, extent_too_small,
                "extent-too-small reconciliation service");
            (void)rejected;
        },
        "wire payload extent cannot describe every payload admitted by the store",
        "reconciliation accepted a complete-file extent below the durable ceiling");
}

void test_empty_share_is_one_bounded_noop_page() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-empty";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-empty-source", 11001U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-empty-receiver", 11002U};
    ReplicaFixture source(
        temporary, "empty-source", folder, source_actor, owner_limits(16U),
        protocol_limits(2U));
    ReplicaFixture receiver(
        temporary, "empty-receiver", folder, receiver_actor,
        owner_limits(16U), protocol_limits(2U));

    const auto receiver_before = receiver.owner_.snapshot_or_throw();
    const auto receiver_channel =
        channel_to(source_actor, "empty-reconciliation-session");
    const auto source_channel =
        channel_to(receiver_actor, "empty-reconciliation-session");
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel);
    const auto response = source.service_.serve_request_or_throw(
        source_channel, request.request_frame);
    require(
        response.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
            response.response.operations.empty() &&
            response.response.payloads.empty() &&
            !response.response.has_more &&
            !response.response.next_after_operation_id.has_value(),
        "empty source did not produce one terminal empty page");

    const auto applied = receiver.service_.apply_response_or_throw(
        receiver_channel, request.request, response.response_frame);
    require(
        applied.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            !applied.has_more &&
            !applied.next_after_operation_id.has_value(),
        "empty source response did not apply as a terminal no-op");
    require(
        receiver.owner_.snapshot_or_throw() == receiver_before,
        "empty reconciliation page changed receiver durable state");
}

void test_share_global_multi_page_convergence_and_reverse_flow() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-multipage";
    const anonsync::SyncReplicaActor actor_a{
        "device-reconciliation-a", 12001U};
    const anonsync::SyncReplicaActor actor_b{
        "device-reconciliation-b", 12002U};
    ReplicaFixture a(
        temporary, "peer-a", folder, actor_a, owner_limits(64U),
        protocol_limits(1U));
    ReplicaFixture b(
        temporary, "peer-b", folder, actor_b, owner_limits(64U),
        protocol_limits(1U));

    const auto alpha = a.publish_file("tree/alpha.txt", "alpha-bytes");
    const auto beta = a.publish_file("tree/beta.txt", "beta-bytes");
    const auto deleted = a.publish_tombstone("tree/old.txt");
    (void)deleted;
    require(
        a.owner_.snapshot_or_throw().outbox.empty(),
        "destination-free publication unexpectedly created outbox rows");

    const auto requester_channel = channel_to(actor_a, "multipage-session-a");
    const auto responder_channel = channel_to(actor_b, "multipage-session-a");
    const PullSummary first = pull_until_stop(
        b, a, requester_channel, responder_channel);
    const auto a_after_first = a.owner_.snapshot_or_throw();
    const auto b_after_first = b.owner_.snapshot_or_throw();
    require(
        first.terminal ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            first.page_count == 3U && first.inserted_operations == 3U,
        "bounded one-operation pages did not transfer the complete share");
    require(
        b_after_first.evidence_set_digest ==
                a_after_first.evidence_set_digest &&
            b_after_first.durable.operations ==
                a_after_first.durable.operations,
        "independent replicas did not converge on exact retained evidence");
    require(
        a_after_first.outbox.empty() && b_after_first.outbox.empty(),
        "share-global reconciliation depended on courier outbox state");
    require_payload_available(
        b.payload_store_, alpha, "alpha-bytes",
        "receiver did not retain alpha payload bytes");
    require_payload_available(
        b.payload_store_, beta, "beta-bytes",
        "receiver did not retain beta payload bytes");

    const auto before_repeat = b.owner_.snapshot_or_throw();
    const PullSummary repeated = pull_until_stop(
        b, a, requester_channel, responder_channel);
    require(
        repeated.inserted_operations == 0U &&
            repeated.duplicate_operations == 3U &&
            repeated.inserted_payloads == 0U &&
            repeated.existing_payloads == 2U,
        "repeat catch-up was not an idempotent evidence/payload no-op");
    require(
        b.owner_.snapshot_or_throw() == before_repeat,
        "repeat catch-up changed the receiver durable cutpoint");

    const auto from_b =
        b.publish_file("tree/from-b.txt", "bytes-originating-at-b");
    const auto a_requests_b = channel_to(actor_b, "reverse-session-b");
    const auto b_serves_a = channel_to(actor_a, "reverse-session-b");
    const PullSummary reverse = pull_until_stop(
        a, b, a_requests_b, b_serves_a);
    require(
        reverse.terminal ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            reverse.inserted_operations == 1U,
        "reverse-direction peer publication did not enter the first peer");
    const auto a_final = a.owner_.snapshot_or_throw();
    const auto b_final = b.owner_.snapshot_or_throw();
    require(
        a_final.evidence_set_digest == b_final.evidence_set_digest &&
            a_final.durable.operations == b_final.durable.operations,
        "symmetric peers did not converge after reverse publication");
    require_payload_available(
        a.payload_store_, from_b, "bytes-originating-at-b",
        "reverse-origin payload was not retained by the first peer");
    require(
        a_final.outbox.empty() && b_final.outbox.empty(),
        "reverse reconciliation manufactured destination outbox state");

    auto wrong_peer = channel_to(
        anonsync::SyncReplicaActor{actor_b.device_id, actor_b.epoch + 1U},
        "multipage-session-a");
    const auto request = b.service_.make_request_or_throw(
        requester_channel);
    const auto source_before_wrong = a.owner_.snapshot_or_throw();
    require_error(
        [&] {
            (void)a.service_.serve_request_or_throw(
                wrong_peer, request.request_frame);
        },
        "does not bind",
        "request crossed an unauthenticated peer actor epoch");
    require(
        a.owner_.snapshot_or_throw() == source_before_wrong,
        "wrong-peer request mutated source durable state");
}

void test_outbox_churn_does_not_break_cursor_but_evidence_change_does() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-source-change";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-source", 13001U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-receiver", 13002U};
    ReplicaFixture source(
        temporary, "source-change-source", folder, source_actor,
        owner_limits(64U), protocol_limits(1U));
    ReplicaFixture receiver(
        temporary, "source-change-receiver", folder, receiver_actor,
        owner_limits(64U), protocol_limits(1U));
    const auto first = source.publish_tombstone("history/one");
    const auto second = source.publish_tombstone("history/two");
    (void)second;

    const auto receiver_channel =
        channel_to(source_actor, "source-change-session");
    const auto source_channel =
        channel_to(receiver_actor, "source-change-session");
    const auto request_one = receiver.service_.make_request_or_throw(
        receiver_channel);
    const auto response_one = source.service_.serve_request_or_throw(
        source_channel, request_one.request_frame);
    const auto apply_one = receiver.service_.apply_response_or_throw(
        receiver_channel, request_one.request, response_one.response_frame);
    require(
        apply_one.has_more &&
            apply_one.next_after_operation_id.has_value(),
        "first bounded source page did not expose a continuation cursor");

    const std::vector<std::string> unrelated_destination{
        "device-unrelated-courier"};
    const auto enqueued =
        source.owner_.enqueue_operation_for_destinations_or_throw(
            first.operation_id, unrelated_destination);
    require(
        enqueued.added_intent_count == 1U,
        "test could not create unrelated courier scheduling churn");

    const auto request_two = receiver.service_.make_request_or_throw(
        receiver_channel, apply_one.next_after_operation_id,
        apply_one.source_evidence_set_digest);
    const auto response_two = source.service_.serve_request_or_throw(
        source_channel, request_two.request_frame);
    require(
        response_two.response.disposition ==
            anonsync::SyncReplicaReconciliationResponseDisposition::Page,
        "outbox-only mutation incorrectly invalidated share evidence paging");
    const auto apply_two = receiver.service_.apply_response_or_throw(
        receiver_channel, request_two.request, response_two.response_frame);
    require(
        apply_two.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied,
        "continued page failed after unrelated outbox mutation");

    (void)source.publish_tombstone("history/three");
    const auto request_three = receiver.service_.make_request_or_throw(
        receiver_channel, apply_two.next_after_operation_id,
        apply_two.source_evidence_set_digest);
    const auto response_three = source.service_.serve_request_or_throw(
        source_channel, request_three.request_frame);
    require(
        response_three.response.disposition ==
            anonsync::SyncReplicaReconciliationResponseDisposition::SourceChanged &&
            response_three.response.operations.empty(),
        "evidence mutation did not force an explicit cursor reset");
    const auto receiver_before_reset = receiver.owner_.snapshot_or_throw();
    const auto reset = receiver.service_.apply_response_or_throw(
        receiver_channel, request_three.request,
        response_three.response_frame);
    require(
        reset.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::SourceChanged &&
            receiver.owner_.snapshot_or_throw() == receiver_before_reset,
        "source reset response mutated receiver evidence");

    const PullSummary converged = pull_until_stop(
        receiver, source, receiver_channel, source_channel);
    require(
        converged.reset_count == 0U &&
            receiver.owner_.snapshot_or_throw().evidence_set_digest ==
                source.owner_.snapshot_or_throw().evidence_set_digest,
        "fresh cursor did not converge after an explicit source reset");

    const auto fabricated = receiver.service_.make_request_or_throw(
        receiver_channel, anonsync::sha256_hex("fabricated-cursor"),
        source.owner_.snapshot_or_throw().evidence_set_digest);
    require_error(
        [&] {
            (void)source.service_.serve_request_or_throw(
                source_channel, fabricated.request_frame);
        },
        "cursor is absent",
        "fabricated lexical cursor skipped a source prefix");
}

void test_missing_payload_stalls_exactly_and_recovers_without_evidence_change() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-missing-payload";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-missing-source", 14001U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-missing-receiver", 14002U};
    ReplicaFixture source(
        temporary, "missing-source", folder, source_actor,
        owner_limits(256U), protocol_limits(128U));
    ReplicaFixture receiver(
        temporary, "missing-receiver", folder, receiver_actor,
        owner_limits(256U), protocol_limits(128U));

    const std::string missing_bytes = "payload-arrives-later";
    const auto missing = source.publish_file_without_payload(
        "missing/value.bin", missing_bytes);
    std::optional<anonsync::SyncReplicaOperation> earlier;
    std::optional<anonsync::SyncReplicaOperation> later;
    for (std::uint64_t index = 0U; index < 128U; ++index) {
        auto candidate = source.publish_tombstone(
            "missing/candidate-" + std::to_string(index));
        if (candidate.operation_id < missing.operation_id) {
            earlier = candidate;
        } else if (candidate.operation_id > missing.operation_id) {
            later = candidate;
        }
        if (earlier.has_value() && later.has_value()) break;
    }
    require(
        earlier.has_value() && later.has_value(),
        "test corpus could not bracket the missing payload in lexical evidence order");

    const auto receiver_channel =
        channel_to(source_actor, "missing-payload-session");
    const auto source_channel =
        channel_to(receiver_actor, "missing-payload-session");
    auto source_session = source.service_.make_serve_session_or_throw(
        source_channel);
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel);
    const auto response = source.service_.serve_request_or_throw(
        source_channel, request.request_frame, source_session);
    require(
        response.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::PayloadUnavailable &&
            response.response.blocked_operation_id ==
                std::optional<std::string>(missing.operation_id),
        "source did not stop at the exact file whose payload was unavailable");
    require(
        source_session.payload_targeted_access_births() == 1U &&
            source_session.payload_targeted_open_attempts() == 1U &&
            source_session.payload_targeted_opens() == 0U,
        "missing source payload did not use one exact current-name probe");
    require(
        std::none_of(
            response.response.operations.begin(),
            response.response.operations.end(),
            [&](const auto& operation) {
                return operation.operation_id >= missing.operation_id;
            }),
        "source response skipped over the missing payload operation");

    const auto applied = receiver.service_.apply_response_or_throw(
        receiver_channel, request.request, response.response_frame);
    require(
        applied.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::SourcePayloadUnavailable &&
            applied.blocked_operation_id ==
                std::optional<std::string>(missing.operation_id),
        "receiver did not retain typed source-payload backpressure");
    const auto receiver_stalled = receiver.owner_.snapshot_or_throw();
    require(
        std::none_of(
            receiver_stalled.durable.operations.begin(),
            receiver_stalled.durable.operations.end(),
            [&](const auto& operation) {
                return operation.operation_id >= missing.operation_id;
            }),
        "receiver admitted evidence after an unavailable payload boundary");

    const std::string evidence_before_payload =
        source.owner_.snapshot_or_throw().evidence_set_digest;
    const auto put = source.payload_store_.put_payload_or_throw(missing_bytes);
    require(
        put.content_sha256 == missing.content_sha256,
        "late payload did not match retained file evidence");
    require(
        source.owner_.snapshot_or_throw().evidence_set_digest ==
            evidence_before_payload,
        "payload availability incorrectly changed immutable evidence identity");

    const auto continuation = receiver.service_.make_request_or_throw(
        receiver_channel, applied.next_after_operation_id,
        applied.source_evidence_set_digest);
    const auto resumed = source.service_.serve_request_or_throw(
        source_channel, continuation.request_frame, source_session);
    require(
        resumed.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
            std::any_of(
                resumed.response.operations.begin(),
                resumed.response.operations.end(),
                [&](const auto& operation) {
                    return operation.operation_id == missing.operation_id;
                }),
        "same live serve session did not observe payload bytes that arrived without an evidence change");
    require(
        source_session.payload_targeted_access_births() == 2U &&
            source_session.payload_targeted_open_attempts() == 2U &&
            source_session.payload_targeted_opens() == 1U,
        "late payload availability rebuilt or bypassed the pass-scoped targeted source access");
    const auto resumed_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, continuation.request, resumed.response_frame);
    require(
        resumed_apply.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied,
        "resumed payload page was not applied");
    require(
        receiver.owner_.snapshot_or_throw().evidence_set_digest ==
            source.owner_.snapshot_or_throw().evidence_set_digest,
        "receiver did not converge after missing payload repair");
    require_payload_available(
        receiver.payload_store_, missing, missing_bytes,
        "repaired payload was not retained by receiver");
}

void test_targeted_source_serving_does_not_claim_namespace_health() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-targeted-source-nonclaim";
    const anonsync::SyncReplicaActor source_actor{
        "device-targeted-source-nonclaim-source", 6501U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-targeted-source-nonclaim-receiver", 6502U};
    ReplicaFixture source(
        temporary, "targeted-source-nonclaim-source", folder, source_actor,
        owner_limits(16U), protocol_limits(8U));
    ReplicaFixture receiver(
        temporary, "targeted-source-nonclaim-receiver", folder,
        receiver_actor, owner_limits(16U), protocol_limits(8U));

    const std::string bytes = "selected payload remains independently usable";
    const auto operation =
        source.publish_file("media/selected.bin", bytes);
    const fs::path unrelated =
        source.payload_root_ / "unrelated-invalid-payload-root-entry";
    {
        std::ofstream output(unrelated, std::ios::binary | std::ios::trunc);
        if (!output) fail("could not create unrelated invalid payload entry");
        output << "not a digest-named payload";
        if (!output) fail("could not write unrelated invalid payload entry");
    }
    if (::chmod(unrelated.c_str(), 0600) != 0) {
        fail("could not make unrelated invalid payload entry private");
    }

    const auto receiver_channel =
        channel_to(source_actor, "targeted-source-nonclaim-session");
    const auto source_channel =
        channel_to(receiver_actor, "targeted-source-nonclaim-session");
    auto source_session = source.service_.make_serve_session_or_throw(
        source_channel);
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel);
    const auto response = source.service_.serve_request_or_throw(
        source_channel, request.request_frame, source_session);
    require(
        response.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
            response.response.operations ==
                std::vector<anonsync::SyncReplicaOperation>{operation} &&
            response.response.payloads.size() == 1U &&
            source_session.payload_targeted_access_births() == 1U &&
            source_session.payload_targeted_open_attempts() == 1U &&
            source_session.payload_targeted_opens() == 1U,
        "bounded source serving enumerated or bypassed the exact selected payload");
    const auto applied = receiver.service_.apply_response_or_throw(
        receiver_channel, request.request, response.response_frame);
    require(
        applied.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            applied.inserted_payloads == 1U,
        "receiver did not admit the exactly selected payload");
    require_payload_available(
        receiver.payload_store_, operation, bytes,
        "receiver did not retain the exact targeted source bytes");

    require_error(
        [&] { (void)source.payload_store_.snapshot_or_throw(); },
        "refuses unexpected payload-root entry",
        "targeted source serving was incorrectly treated as namespace health authority");

    std::error_code remove_error;
    const bool removed = fs::remove(unrelated, remove_error);
    if (!removed || remove_error) {
        fail("could not remove unrelated invalid payload entry after nonclaim proof");
    }
    const auto complete = source.payload_store_.snapshot_or_throw();
    const auto live = anonsync::SyncReplicaFilePayloadStoreTestAccess::
        live_cutpoint_excluding_snapshot_or_throw(
            source.payload_store_, complete);
    require(
        live.targeted_access_count == 0U &&
            !live.all_current_payloads_may_be_reopened(),
        "source request returned while retaining a namespace-wide payload capability");
}

void test_targeted_whole_payload_hashes_before_source_advertisement() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-targeted-source-integrity";
    const anonsync::SyncReplicaActor source_actor{
        "device-targeted-source-integrity-source", 6751U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-targeted-source-integrity-receiver", 6752U};
    ReplicaFixture source(
        temporary, "targeted-source-integrity-source", folder, source_actor,
        owner_limits(16U), protocol_limits(8U));
    ReplicaFixture receiver(
        temporary, "targeted-source-integrity-receiver", folder,
        receiver_actor, owner_limits(16U), protocol_limits(8U));

    const std::string good = "whole targeted source content proof";
    const auto operation = source.publish_file("media/integrity.bin", good);
    std::string corrupt = good;
    corrupt.front() = corrupt.front() == 'x' ? 'y' : 'x';
    {
        std::ofstream output(
            source.payload_root_ / operation.content_sha256,
            std::ios::binary | std::ios::trunc);
        if (!output) fail("could not open targeted source corruption fixture");
        output.write(corrupt.data(), static_cast<std::streamsize>(corrupt.size()));
        if (!output) fail("could not write targeted source corruption fixture");
    }

    const auto receiver_channel =
        channel_to(source_actor, "targeted-source-integrity-session");
    const auto source_channel =
        channel_to(receiver_actor, "targeted-source-integrity-session");
    auto source_session = source.service_.make_serve_session_or_throw(
        source_channel);
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel);
    require_error(
        [&] {
            (void)source.service_.serve_request_or_throw(
                source_channel, request.request_frame, source_session);
        },
        "complete range discovered payload corruption",
        "whole targeted source bytes were advertised without an exact SHA-256 proof");
    require(
        source_session.payload_targeted_access_births() == 1U &&
            source_session.payload_targeted_open_attempts() == 1U &&
            source_session.payload_targeted_opens() == 1U,
        "whole targeted corruption bypassed the exact request-scoped source open");
    require(
        receiver.owner_.snapshot_or_throw().durable.operations.empty() &&
            receiver.payload_store_.snapshot_or_throw().entry_count() == 0U,
        "source-side targeted corruption changed receiver durable state");
}

void test_operation_ahead_crash_window_repairs_payload_idempotently() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-operation-ahead";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-operation-source", 14501U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-operation-receiver", 14502U};
    ReplicaFixture source(
        temporary, "operation-ahead-source", folder, source_actor,
        owner_limits(64U), protocol_limits(8U));
    ReplicaFixture receiver(
        temporary, "operation-ahead-receiver", folder, receiver_actor,
        owner_limits(64U), protocol_limits(8U));

    const std::string bytes = "payload-repaired-after-operation";
    const auto operation = source.publish_file(
        "repair/value.bin", bytes);
    require(
        receiver.owner_.accept_remote_or_throw(operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "operation-ahead fixture could not simulate the durable crash window");
    {
        auto before = receiver.payload_store_.snapshot_or_throw();
        require(
            !before.payload_size_or_none(operation.content_sha256).has_value(),
            "operation-ahead fixture unexpectedly already had payload bytes");
    }

    const auto receiver_channel =
        channel_to(source_actor, "operation-ahead-session");
    const auto source_channel =
        channel_to(receiver_actor, "operation-ahead-session");
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel);
    const auto response = source.service_.serve_request_or_throw(
        source_channel, request.request_frame);
    const auto applied = receiver.service_.apply_response_or_throw(
        receiver_channel, request.request, response.response_frame);
    require(
        applied.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            applied.duplicate_operations == 1U &&
            applied.inserted_payloads == 1U,
        "duplicate evidence did not repair its missing payload after restart");
    require_payload_available(
        receiver.payload_store_, operation, bytes,
        "operation-ahead retry did not materialize the missing payload");
    require(
        receiver.owner_.snapshot_or_throw().evidence_set_digest ==
            source.owner_.snapshot_or_throw().evidence_set_digest,
        "operation-ahead payload repair changed evidence convergence");
}


void test_large_payload_range_resume_survives_service_restart() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-range-restart";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-range-source", 11601U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-range-receiver", 11602U};
    auto ranged_wire = protocol_limits(1U);
    ranged_wire.max_single_payload_bytes = 4U;
    ranged_wire.max_payload_bytes_per_page = 8U;

    ReplicaFixture source(
        temporary, "range-source", folder, source_actor,
        owner_limits(64U), ranged_wire);
    auto receiver = std::make_unique<ReplicaFixture>(
        temporary, "range-receiver", folder, receiver_actor,
        owner_limits(64U), ranged_wire);
    const std::string bytes = "abcdefghij";
    const auto operation = source.publish_file("large/ranged.bin", bytes);
    const Channel receiver_channel =
        channel_to(source_actor, "range-restart-session");
    const Channel source_channel =
        channel_to(receiver_actor, "range-restart-session");

    auto source_session = source.service_.make_serve_session_or_throw(
        source_channel);

    const auto first_request = receiver->service_.make_request_or_throw(
        receiver_channel);
    const auto first_direct =
        source.service_.serve_request_frame_or_throw(
            source_channel, first_request.request_frame, source_session);
    require(
        first_direct.direct_frame_borrowed_manifest_count == 1U &&
            first_direct.direct_frame_borrowed_manifest_chunks == 1U &&
            first_direct.direct_frame_manifest_materialization_bytes == 0U &&
            first_direct.response.payloads.size() == 2U &&
            !first_direct.response.payloads[0].delta_manifest.has_value() &&
            !first_direct.response.payloads[1].delta_manifest.has_value(),
        "shipping service rebuilt an owning source manifest before direct framing");
    const anonsync::SyncReplicaReconciliationResponse first_response =
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            first_direct.response_frame, ranged_wire);
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        first_response, first_request.request, ranged_wire);
    require(
        first_response.operations.size() == 1U &&
            first_response.payloads.size() == 2U &&
            first_response.payloads[0].offset_bytes == 0U &&
            first_response.payloads[0].bytes == "abcd" &&
            first_response.payloads[0].delta_manifest.has_value() &&
            first_response.payloads[0].delta_manifest_digest.has_value() &&
            first_response.payloads[1].offset_bytes == 4U &&
            first_response.payloads[1].bytes == "efgh" &&
            !first_response.payloads[1].delta_manifest.has_value() &&
            first_response.payloads[1].delta_manifest_digest ==
                first_response.payloads[0].delta_manifest_digest &&
            first_response.payload_continuation.has_value() &&
            first_response.payload_continuation->next_offset_bytes == 8U &&
            !first_response.next_after_operation_id.has_value(),
        "initial large-payload page was not one bounded two-range window");
    const auto first_apply = receiver->service_.apply_response_or_throw(
        receiver_channel, first_request.request,
        first_direct.response_frame);
    require(
        first_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::
                    PayloadProgress &&
            first_apply.staged_payload_ranges == 2U &&
            first_apply.staged_payload_bytes == 8U &&
            first_apply.payload_continuation.has_value() &&
            first_apply.payload_continuation->next_offset_bytes == 8U &&
            first_apply.target_content_defined_manifest_publications == 1U &&
            first_apply.target_content_defined_manifest_reuses == 1U &&
            first_apply.inserted_active == 0U &&
            first_apply.duplicate_operations == 0U,
        "receiver did not retain one multi-range window without admitting incomplete evidence");
    require(
        source_session.ranged_payload_windows() == 1U &&
            source_session.ranged_payload_ranges() == 2U &&
            source_session.ranged_payload_bytes() == 8U,
        "source did not account for the exact first two-range window");
    require(
        receiver->owner_.snapshot_or_throw().durable.operations.empty(),
        "first durable multi-range window admitted operation metadata before whole-payload completion");

    const auto continued_request = receiver->service_.make_request_or_throw(
        receiver_channel, first_apply.next_after_operation_id,
        first_apply.source_evidence_set_digest,
        first_apply.payload_continuation);
    auto stale_manifest_request = continued_request.request;
    stale_manifest_request.cached_delta_manifest_digest =
        anonsync::sha256_hex("stale-source-manifest-reference");
    require_error(
        [&] {
            (void)source.service_.serve_request_or_throw(
                source_channel,
                anonsync::encode_sync_replica_reconciliation_request_or_throw(
                    stale_manifest_request, ranged_wire),
                source_session);
        },
        "requested content-defined manifest cache does not match current source bytes",
        "stale receiver manifest reference reached source range selection");
    require(
        source_session.content_defined_chunk_index_builds() == 1U &&
            source_session.content_defined_chunk_index_reuses() == 0U &&
            source_session.content_defined_chunk_index_lookups() == 1U &&
            source_session.ranged_payload_windows() == 1U &&
            source_session.ranged_payload_ranges() == 2U &&
            source_session.ranged_payload_bytes() == 8U,
        "stale receiver manifest reference consumed source index reuse or lookup work");
    {
        const auto staged = receiver->payload_store_.snapshot_or_throw();
        require(
            staged.entry_count() == 0U &&
                staged.transient_entry_count() == 1U &&
                staged.transient_bytes() == 8U,
            "two ranges in one response were not one durable prefix before service restart");
    }

    // Lose every in-memory cursor and reconstruct the database, payload store,
    // and reconciliation service from their durable roots. The source starts
    // from range zero again with the same two-range window. The receiver must
    // observe its longer durable prefix once, skip the second already-covered
    // range, and report offset eight without rewriting or abandoning bytes.
    receiver.reset();
    receiver = std::make_unique<ReplicaFixture>(
        temporary, "range-receiver", folder, receiver_actor,
        owner_limits(64U), ranged_wire);
    const auto replay_request = receiver->service_.make_request_or_throw(
        receiver_channel);
    const auto replay_response = source.service_.serve_request_or_throw(
        source_channel, replay_request.request_frame, source_session);
    const auto replay_apply = receiver->service_.apply_response_or_throw(
        receiver_channel, replay_request.request,
        replay_response.response_frame);
    require(
        !replay_request.request.cached_delta_manifest_digest.has_value() &&
            replay_response.response.payloads.size() == 2U &&
            replay_response.response.payloads[0]
                .delta_manifest.has_value() &&
            !replay_response.response.payloads[1]
                 .delta_manifest.has_value() &&
            replay_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::
                    PayloadProgress &&
            replay_apply.staged_payload_ranges == 1U &&
            replay_apply.staged_payload_bytes == 0U &&
            replay_apply.payload_continuation.has_value() &&
            replay_apply.payload_continuation->next_offset_bytes == 8U &&
            replay_apply.target_content_defined_manifest_publications == 1U &&
            replay_apply.target_content_defined_manifest_reuses == 1U &&
            replay_apply.inserted_active == 0U &&
            replay_apply.duplicate_operations == 0U,
        "fresh service lifetime did not recover and skip the durable two-range prefix");
    require(
        receiver->owner_.snapshot_or_throw().durable.operations.empty(),
        "fresh service lifetime admitted incomplete ranged evidence");

    const auto cache_before_terminal =
        source.service_.source_manifest_cache_status();
    require(
        cache_before_terminal.resident &&
            cache_before_terminal.operation_id == operation.operation_id &&
            cache_before_terminal.canonical_path == operation.canonical_path &&
            cache_before_terminal.content_sha256 == operation.content_sha256 &&
            cache_before_terminal.total_size_bytes == operation.size_bytes &&
            cache_before_terminal.chunk_count == 1U &&
            cache_before_terminal.retained_chunk_capacity_bytes > 0U &&
            cache_before_terminal.exact_complete_checkpoint_durable &&
            cache_before_terminal.complete_checkpoint_restorations == 0U &&
            cache_before_terminal.terminal_releases == 0U,
        "completed source manifest cache was not durably discardable before the terminal range");

    const auto final_request = receiver->service_.make_request_or_throw(
        receiver_channel, replay_apply.next_after_operation_id,
        replay_apply.source_evidence_set_digest,
        replay_apply.payload_continuation);
    const auto final_direct = source.service_.serve_request_frame_or_throw(
        source_channel, final_request.request_frame, source_session);
    const auto final_response =
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            final_direct.response_frame, ranged_wire);
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        final_response, final_request.request, ranged_wire);
    require(
        final_request.request.cached_delta_manifest_digest ==
                replay_response.response.payloads.front()
                    .delta_manifest_digest &&
            final_response.payloads.size() == 1U &&
            final_response.payloads.front().offset_bytes == 8U &&
            final_response.payloads.front().bytes == "ij" &&
            !final_response.payloads.front()
                 .delta_manifest.has_value() &&
            final_response.payload_continuation ==
                std::optional<anonsync::
                    SyncReplicaReconciliationPayloadContinuation>(
                    anonsync::SyncReplicaReconciliationPayloadContinuation{
                        operation.operation_id, operation.content_sha256,
                        operation.size_bytes, operation.size_bytes}) &&
            final_response.next_after_operation_id ==
                replay_apply.next_after_operation_id &&
            final_direct.source_manifest_cache_terminal_releases == 1U &&
            final_direct.source_manifest_cache_terminal_released_capacity_bytes ==
                cache_before_terminal.retained_chunk_capacity_bytes,
        "final source range did not hand off exact local terminal verification");
    const auto cache_after_terminal =
        source.service_.source_manifest_cache_status();
    require(
        !cache_after_terminal.resident &&
            cache_after_terminal.complete_checkpoint_restorations == 0U &&
            cache_after_terminal.terminal_releases == 1U &&
            cache_after_terminal.terminal_released_capacity_bytes ==
                cache_before_terminal.retained_chunk_capacity_bytes,
        "terminal source frame retained its dormant compact manifest");
    const auto final_apply = receiver->service_.apply_response_or_throw(
        receiver_channel, final_request.request,
        final_direct.response_frame);
    require(
        final_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            final_apply.inserted_payloads == 1U &&
            final_apply.inserted_active == 1U &&
            final_apply.duplicate_operations == 0U &&
            final_apply.staged_payload_ranges == 1U &&
            final_apply.staged_payload_bytes == 2U &&
            final_apply.target_content_defined_manifest_publications == 0U &&
            final_apply.target_content_defined_manifest_reuses == 1U &&
            !final_apply.payload_continuation.has_value() &&
            final_apply.next_after_operation_id ==
                std::optional<std::string>(operation.operation_id),
        "final range did not assemble one durable whole payload");
    require_payload_available(
        receiver->payload_store_, operation, bytes,
        "restarted ranged reconciliation did not retain exact whole bytes");
    {
        const auto completed = receiver->payload_store_.snapshot_or_throw();
        require(
            completed.transient_entry_count() == 0U &&
                completed.transient_bytes() == 0U,
            "completed ranged reconciliation left staging authority");
    }

    const auto duplicate_request = receiver->service_.make_request_or_throw(
        receiver_channel);
    const auto duplicate_response = source.service_.serve_request_or_throw(
        source_channel, duplicate_request.request_frame, source_session);
    const auto duplicate_apply = receiver->service_.apply_response_or_throw(
        receiver_channel, duplicate_request.request,
        duplicate_response.response_frame);
    require(
        duplicate_response.response.payloads.size() == 2U &&
            duplicate_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            duplicate_apply.existing_payloads == 1U &&
            duplicate_apply.duplicate_operations == 1U &&
            duplicate_apply.staged_payload_ranges == 1U &&
            duplicate_apply.staged_payload_bytes == 0U &&
            !duplicate_apply.payload_continuation.has_value() &&
            duplicate_apply.next_after_operation_id ==
                std::optional<std::string>(operation.operation_id),
        "completed large payload did not collapse a replayed multi-range window");
    const auto cache_after_replay =
        source.service_.source_manifest_cache_status();
    require(
        cache_after_replay.resident &&
            cache_after_replay.exact_complete_checkpoint_durable &&
            cache_after_replay.complete_checkpoint_restorations == 1U &&
            cache_after_replay.terminal_releases == 1U &&
            cache_after_replay.retained_chunk_capacity_bytes ==
                cache_before_terminal.retained_chunk_capacity_bytes,
        "lost-response replay did not rehydrate the exact durable manifest without source hashing");
    require(
        source_session.payload_targeted_access_births() == 5U &&
            source_session.payload_targeted_open_attempts() == 5U &&
            source_session.payload_targeted_opens() == 5U &&
            source_session.content_defined_manifest_scans() == 1U &&
            source_session.content_defined_manifest_reuses() == 3U &&
            source_session.content_defined_manifest_hashed_bytes() ==
                bytes.size() &&
            source_session.content_defined_manifest_publications() == 3U &&
            source_session.content_defined_manifest_references() == 4U &&
            source_session.content_defined_chunk_index_builds() == 1U &&
            source_session.content_defined_chunk_index_reuses() == 3U &&
            source_session.content_defined_chunk_index_lookups() == 4U &&
            source_session.ranged_payload_windows() == 4U &&
            source_session.ranged_payload_ranges() == 7U &&
            source_session.ranged_payload_bytes() == 26U,
        "one targeted source session did not batch contiguous ranges while retaining one exact cumulative chunk index across receiver cache states");
    const Channel other_source_channel =
        channel_to(receiver_actor, "range-restart-other-session");
    require_error(
        [&] {
            (void)source.service_.serve_request_or_throw(
                other_source_channel, first_request.request_frame,
                source_session);
        },
        "serve session does not bind",
        "payload snapshot session crossed its authenticated channel binding");
}

void test_terminal_verification_step_budget_yields_exact_continuation() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-terminal-verification-budget";
    const anonsync::SyncReplicaActor source_actor{
        "device-terminal-budget-source", 11631U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-terminal-budget-receiver", 11632U};
    const std::uint64_t frontier = anonsync::
        kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep;
    const std::uint64_t total_size = 2U * frontier + 4097U;

    auto store_limits = payload_limits();
    store_limits.max_payload_bytes = total_size + 4096U;
    store_limits.max_indexed_bytes = 2U * total_size + 4096U;
    store_limits.max_transient_bytes = total_size + 4096U;
    auto wire_limits = protocol_limits(1U);
    wire_limits.max_payload_extent_bytes = total_size + 4096U;

    ReplicaFixture source(
        temporary, "terminal-budget-source", folder, source_actor,
        owner_limits(16U), wire_limits, store_limits);
    ReplicaFixture receiver(
        temporary, "terminal-budget-receiver", folder, receiver_actor,
        owner_limits(16U), wire_limits, store_limits,
        anonsync::sync_replica_default_selective_sync_policy(),
        anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        anonsync::
            kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        1U);

    std::string bytes(static_cast<std::size_t>(total_size), '\0');
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
        bytes[index] = static_cast<char>(
            'a' + static_cast<char>((index * 17U + index / 101U) % 26U));
    }
    const std::string digest = anonsync::sha256_hex(bytes);
    const auto operation = source.owner_.publish_local_file_or_throw(
        "large/budgeted-terminal.bin", total_size, digest);
    const auto staged = receiver.payload_store_.stage_payload_prefix_or_throw(
        digest, total_size, 0U, digest, bytes);
    require(
        staged.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            staged.next_offset_bytes == total_size &&
            staged.terminal_verification_steps == 1U,
        "terminal-budget fixture did not retain its first exact checkpoint");
    bytes.clear();
    bytes.shrink_to_fit();

    const Channel receiver_channel =
        channel_to(source_actor, "terminal-budget-session");
    const Channel source_channel =
        channel_to(receiver_actor, "terminal-budget-session");
    const auto source_snapshot = source.owner_.snapshot_or_throw();
    const anonsync::SyncReplicaReconciliationPayloadContinuation continuation{
        operation.operation_id, operation.content_sha256,
        operation.size_bytes, operation.size_bytes};
    const auto first_request = receiver.service_.make_request_or_throw(
        receiver_channel, std::nullopt,
        source_snapshot.evidence_set_digest, continuation);
    const auto first_response = source.service_.serve_request_or_throw(
        source_channel, first_request.request_frame);
    require(
        first_response.response.payloads.empty() &&
            first_response.response.payload_continuation == continuation,
        "terminal-budget source response admitted payload bytes");
    const auto first_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, first_request.request,
        first_response.response_frame);
    require(
        first_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::
                    PayloadProgress &&
            first_apply.terminal_verification_steps == 1U &&
            first_apply.terminal_verification_local_continuation_steps == 1U &&
            first_apply.terminal_verification_step_budget_exhaustions == 1U &&
            first_apply.inserted_payloads == 0U &&
            first_apply.inserted_active == 0U &&
            first_apply.payload_continuation == continuation,
        "one-step terminal budget did not yield an exact payload-cold continuation");

    const auto second_request = receiver.service_.make_request_or_throw(
        receiver_channel, first_apply.next_after_operation_id,
        first_apply.source_evidence_set_digest,
        first_apply.payload_continuation);
    const auto second_response = source.service_.serve_request_or_throw(
        source_channel, second_request.request_frame);
    const auto second_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, second_request.request,
        second_response.response_frame);
    require(
        second_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            second_apply.terminal_verification_steps == 1U &&
            second_apply.terminal_verification_local_continuation_steps == 1U &&
            second_apply.terminal_verification_step_budget_exhaustions == 0U &&
            second_apply.inserted_payloads == 1U &&
            second_apply.inserted_active == 1U &&
            !second_apply.payload_continuation.has_value(),
        "second bounded terminal pulse did not publish and admit exact evidence");
    require(
        receiver.owner_.snapshot_or_throw().evidence_set_digest ==
            source_snapshot.evidence_set_digest,
        "bounded terminal pulses did not converge exact evidence");
}

void test_exhausted_byte_budget_stops_before_next_ranged_payload_open() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-zero-byte-frontier";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-zero-byte-source", 11651U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-zero-byte-receiver", 11652U};
    auto bounded_wire = protocol_limits(2U);
    bounded_wire.max_single_payload_bytes = 4U;
    bounded_wire.max_payload_bytes_per_page = 4U;

    ReplicaFixture source(
        temporary, "zero-byte-source", folder, source_actor,
        owner_limits(256U), bounded_wire);
    ReplicaFixture receiver(
        temporary, "zero-byte-receiver", folder, receiver_actor,
        owner_limits(256U), bounded_wire);

    std::vector<std::string> whole_operation_ids;
    std::vector<std::string> ranged_operation_ids;
    std::optional<std::size_t> adjacent_index;
    anonsync::SyncReplicaSqliteSnapshot source_snapshot;
    for (std::uint64_t index = 0U;
         index < 128U && !adjacent_index.has_value(); ++index) {
        const auto whole = source.publish_file(
            "budget/whole-" + std::to_string(index), "tiny");
        const auto ranged = source.publish_file(
            "budget/ranged-" + std::to_string(index), "abcdefghij");
        whole_operation_ids.push_back(whole.operation_id);
        ranged_operation_ids.push_back(ranged.operation_id);

        source_snapshot = source.owner_.snapshot_or_throw();
        const auto& operations = source_snapshot.durable.operations;
        for (std::size_t candidate = 0U;
             candidate + 1U < operations.size(); ++candidate) {
            const bool first_is_whole =
                std::find(
                    whole_operation_ids.begin(), whole_operation_ids.end(),
                    operations[candidate].operation_id) !=
                whole_operation_ids.end();
            const bool second_is_ranged =
                std::find(
                    ranged_operation_ids.begin(), ranged_operation_ids.end(),
                    operations[candidate + 1U].operation_id) !=
                ranged_operation_ids.end();
            if (first_is_whole && second_is_ranged) {
                adjacent_index = candidate;
                break;
            }
        }
    }
    require(
        adjacent_index.has_value(),
        "could not construct adjacent whole and ranged operations for the byte-frontier proof");

    const auto& operations = source_snapshot.durable.operations;
    const anonsync::SyncReplicaOperation& whole = operations[*adjacent_index];
    const anonsync::SyncReplicaOperation& ranged =
        operations[*adjacent_index + 1U];
    std::optional<std::string> after_operation_id;
    std::optional<std::string> expected_source_digest;
    if (*adjacent_index != 0U) {
        after_operation_id = operations[*adjacent_index - 1U].operation_id;
        expected_source_digest = source_snapshot.evidence_set_digest;
    }

    const Channel receiver_channel =
        channel_to(source_actor, "zero-byte-frontier-session");
    const Channel source_channel =
        channel_to(receiver_actor, "zero-byte-frontier-session");
    auto source_session = source.service_.make_serve_session_or_throw(
        source_channel);
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel, after_operation_id, expected_source_digest);
    const auto response = source.service_.serve_request_or_throw(
        source_channel, request.request_frame, source_session);

    require(
        whole.kind == anonsync::SyncReplicaValueKind::File &&
            whole.size_bytes == 4U &&
            ranged.kind == anonsync::SyncReplicaValueKind::File &&
            ranged.size_bytes > bounded_wire.max_single_payload_bytes &&
            response.response.operations ==
                std::vector<anonsync::SyncReplicaOperation>{whole} &&
            response.response.payloads.size() == 1U &&
            response.response.payloads.front().content_sha256 ==
                whole.content_sha256 &&
            response.response.payloads.front().bytes == "tiny" &&
            response.response.has_more &&
            response.response.next_after_operation_id ==
                std::optional<std::string>(whole.operation_id) &&
            !response.response.payload_continuation.has_value(),
        "whole payload did not consume the exact page byte frontier before the ranged successor");
    require(
        source_session.payload_targeted_access_births() == 1U &&
            source_session.payload_targeted_open_attempts() == 1U &&
            source_session.payload_targeted_opens() == 1U &&
            source_session.content_defined_manifest_scans() == 0U &&
            source_session.content_defined_manifest_hashed_bytes() == 0U &&
            source_session.content_defined_chunk_index_builds() == 0U &&
            source_session.content_defined_chunk_index_lookups() == 0U &&
            source_session.ranged_payload_windows() == 0U &&
            source_session.ranged_payload_ranges() == 0U &&
            source_session.ranged_payload_bytes() == 0U,
        "zero-byte frontier opened, hashed, indexed, or published the next ranged payload");
}

void test_payload_progress_preserves_completed_prefix_cursor() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-mixed-range";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-mixed-source", 11701U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-mixed-receiver", 11702U};
    auto ranged_wire = protocol_limits(64U);
    ranged_wire.model = owner_limits(64U).model;
    ranged_wire.max_single_payload_bytes = 4U;
    // This regression isolates operation-prefix cursor preservation. Keep one
    // range per response; multi-range windowing is proved independently by the
    // restart test above.
    ranged_wire.max_payload_bytes_per_page = 4U;

    ReplicaFixture source(
        temporary, "mixed-source", folder, source_actor,
        owner_limits(64U), ranged_wire);
    ReplicaFixture receiver(
        temporary, "mixed-receiver", folder, receiver_actor,
        owner_limits(64U), ranged_wire);
    const std::string bytes = "abcdefghij";
    const auto large = source.publish_file("large/mixed.bin", bytes);

    // Operation pages are canonical by operation ID rather than publication
    // time. Construct one independent tombstone whose ID sorts before the
    // ranged file, then admit only that chosen operation. This gives the page
    // a completed prefix followed by a partial payload without relying on a
    // particular hash ordering for two fixed examples.
    std::optional<anonsync::SyncReplicaOperation> prefix;
    for (std::uint64_t index = 0U; index < 4096U; ++index) {
        anonsync::SyncReplicaModel remote_model(
            folder,
            {"device-reconciliation-mixed-prefix-" +
                 std::to_string(index),
             11800U + index},
            owner_limits(64U).model);
        auto candidate = remote_model.create_local_tombstone_or_throw(
            "prefix/value-" + std::to_string(index));
        if (candidate.operation_id < large.operation_id) {
            prefix = std::move(candidate);
            break;
        }
    }
    require(
        prefix.has_value(),
        "could not construct a canonical operation prefix for mixed range test");
    require(
        source.owner_.accept_remote_or_throw(*prefix) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "mixed range fixture could not admit its canonical prefix");

    const Channel receiver_channel =
        channel_to(source_actor, "mixed-range-session");
    const Channel source_channel =
        channel_to(receiver_actor, "mixed-range-session");
    auto source_session = source.service_.make_serve_session_or_throw(
        source_channel);

    const auto first_request = receiver.service_.make_request_or_throw(
        receiver_channel);
    const auto first_response = source.service_.serve_request_or_throw(
        source_channel, first_request.request_frame, source_session);
    require(
        first_response.response.operations.size() == 2U &&
            first_response.response.operations.front().operation_id ==
                prefix->operation_id &&
            first_response.response.operations.back().operation_id ==
                large.operation_id &&
            first_response.response.next_after_operation_id ==
                std::optional<std::string>(prefix->operation_id) &&
            first_response.response.payload_continuation.has_value() &&
            first_response.response.payload_continuation->next_offset_bytes ==
                4U,
        "mixed page did not expose one completed prefix before its partial file");
    const auto first_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, first_request.request,
        first_response.response_frame);
    require(
        first_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::
                    PayloadProgress &&
            first_apply.inserted_active == 1U &&
            first_apply.next_after_operation_id ==
                first_response.response.next_after_operation_id &&
            first_apply.payload_continuation.has_value() &&
            first_apply.payload_continuation->operation_id ==
                large.operation_id,
        "receiver discarded the completed-prefix cursor at a partial payload");
    {
        const auto durable = receiver.owner_.snapshot_or_throw().durable;
        require(
            durable.operations.size() == 1U &&
                durable.operations.front().operation_id ==
                    prefix->operation_id,
            "mixed page admitted the partial file or lost its completed prefix");
    }

    const auto second_request = receiver.service_.make_request_or_throw(
        receiver_channel, first_apply.next_after_operation_id,
        first_apply.source_evidence_set_digest,
        first_apply.payload_continuation);
    const auto second_response = source.service_.serve_request_or_throw(
        source_channel, second_request.request_frame, source_session);
    require(
        second_response.response.operations.size() == 1U &&
            second_response.response.operations.front().operation_id ==
                large.operation_id &&
            second_response.response.payloads.size() == 1U &&
            second_response.response.payloads.front().offset_bytes == 4U &&
            second_response.response.payloads.front().bytes == "efgh",
        "mixed-page continuation replayed its prefix instead of the ranged file");
    const auto second_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, second_request.request,
        second_response.response_frame);
    require(
        second_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::
                    PayloadProgress &&
            second_apply.next_after_operation_id ==
                std::optional<std::string>(prefix->operation_id) &&
            second_apply.payload_continuation.has_value() &&
            second_apply.payload_continuation->next_offset_bytes == 8U,
        "second mixed-page range did not retain the completed-prefix cursor");

    const auto final_request = receiver.service_.make_request_or_throw(
        receiver_channel, second_apply.next_after_operation_id,
        second_apply.source_evidence_set_digest,
        second_apply.payload_continuation);
    const auto final_response = source.service_.serve_request_or_throw(
        source_channel, final_request.request_frame, source_session);
    const auto final_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, final_request.request,
        final_response.response_frame);
    require(
        final_response.response.payloads.size() == 1U &&
            final_response.response.payloads.front().offset_bytes == 8U &&
            final_response.response.payloads.front().bytes == "ij" &&
            final_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            final_apply.inserted_active == 1U &&
            !final_apply.payload_continuation.has_value() &&
            final_apply.next_after_operation_id ==
                std::optional<std::string>(large.operation_id),
        "mixed-page final range did not complete and advance past the file");
    require_payload_available(
        receiver.payload_store_, large, bytes,
        "mixed-page range continuation did not retain exact whole bytes");
    require(
        receiver.owner_.snapshot_or_throw().evidence_set_digest ==
            source.owner_.snapshot_or_throw().evidence_set_digest,
        "mixed-page range continuation did not converge evidence");
}

void test_content_defined_delta_reuses_shifted_predecessor_chunks() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-reconciliation-content-defined-delta";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-delta-source", 11901U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-delta-receiver", 11902U};
    constexpr std::uint64_t mebibyte = 1024U * 1024U;
    constexpr std::uint64_t old_size = 48U * mebibyte;
    constexpr std::uint64_t insertion_size = 256U * 1024U;
    constexpr std::uint64_t insertion_offset = 1U * mebibyte;
    constexpr std::uint64_t predecessor_projection_bytes_per_apply =
        anonsync::
            kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply;

    auto deterministic_bytes = [](
        std::uint64_t size_bytes, std::uint64_t seed) {
        std::string bytes(static_cast<std::size_t>(size_bytes), '\0');
        std::uint64_t state = seed;
        for (char& byte : bytes) {
            state ^= state >> 12U;
            state ^= state << 25U;
            state ^= state >> 27U;
            const std::uint64_t mixed =
                state * UINT64_C(2685821657736338717);
            byte = static_cast<char>(mixed >> 56U);
        }
        return bytes;
    };

    const std::string old_bytes =
        deterministic_bytes(old_size, UINT64_C(0x8f6d9a43b1c257e1));
    const std::string inserted = deterministic_bytes(
        insertion_size, UINT64_C(0x3be187f40629da5c));
    std::string new_bytes;
    new_bytes.reserve(old_bytes.size() + inserted.size());
    new_bytes.append(old_bytes.data(),
                     static_cast<std::size_t>(insertion_offset));
    new_bytes.append(inserted);
    new_bytes.append(
        old_bytes.data() + static_cast<std::size_t>(insertion_offset),
        old_bytes.size() - static_cast<std::size_t>(insertion_offset));
    const std::size_t distant_edit =
        static_cast<std::size_t>(28U * mebibyte + insertion_size);
    new_bytes[distant_edit] = static_cast<char>(
        static_cast<unsigned char>(new_bytes[distant_edit]) ^ 0x5aU);

    std::optional<std::string> selected_path;
    for (std::uint64_t suffix = 0U; suffix < 4096U; ++suffix) {
        const std::string path =
            "media/content-defined-" + std::to_string(suffix) + ".bin";
        anonsync::SyncReplicaModel probe(
            folder, source_actor, owner_limits(64U).model);
        const auto predecessor = probe.create_local_file_or_throw(
            path, old_bytes.size(), anonsync::sha256_hex(old_bytes));
        const auto successor = probe.create_local_file_or_throw(
            path, new_bytes.size(), anonsync::sha256_hex(new_bytes));
        if (predecessor.operation_id < successor.operation_id) {
            selected_path = path;
            break;
        }
    }
    require(
        selected_path.has_value(),
        "could not construct a canonical predecessor cursor for content-defined delta test");

    auto wire = protocol_limits(1U);
    wire.model = owner_limits(64U).model;
    wire.max_single_payload_bytes = 8U * mebibyte;
    wire.max_payload_bytes_per_page = 8U * mebibyte;
    wire.max_payload_extent_bytes = 96U * mebibyte;
    wire.max_response_frame_bytes = 16U * mebibyte;

    auto store = payload_limits();
    store.max_payload_bytes = 96U * mebibyte;
    store.max_indexed_bytes = 384U * mebibyte;
    store.max_transient_bytes = 128U * mebibyte;

    ReplicaFixture source(
        temporary, "delta-source", folder, source_actor,
        owner_limits(64U), wire, store);
    ReplicaFixture receiver(
        temporary, "delta-receiver", folder, receiver_actor,
        owner_limits(64U), wire, store,
        anonsync::sync_replica_default_selective_sync_policy(),
        anonsync::
            kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        predecessor_projection_bytes_per_apply);
    const auto predecessor = source.publish_file(*selected_path, old_bytes);
    const auto receiver_put =
        receiver.payload_store_.put_payload_or_throw(old_bytes);
    require(
        receiver_put.content_sha256 == predecessor.content_sha256 &&
            receiver.owner_.accept_remote_or_throw(predecessor) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
        "content-defined receiver did not retain the exact causal predecessor");
    const auto successor = source.publish_file(*selected_path, new_bytes);
    require(
        successor.predecessor_operation_ids ==
            std::vector<std::string>{predecessor.operation_id},
        "content-defined successor did not name its exact retained predecessor");

    const auto parameters =
        anonsync::sync_replica_reconciliation_content_defined_parameters_or_throw(
            successor.size_bytes);
    anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest
        predecessor_manifest;
    {
        auto snapshot = receiver.payload_store_.snapshot_or_throw();
        auto opened = snapshot.open_payload_for_operation_or_throw(
            predecessor, "content-defined predecessor fixture open");
        predecessor_manifest = opened.content_defined_manifest_or_throw(
            parameters, "content-defined predecessor fixture manifest");
    }
    anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest
        successor_manifest;
    {
        auto snapshot = source.payload_store_.snapshot_or_throw();
        auto opened = snapshot.open_payload_for_operation_or_throw(
            successor, "content-defined successor fixture open");
        successor_manifest = opened.content_defined_manifest_or_throw(
            parameters, "content-defined successor fixture manifest");
    }
    auto offsets_for = [](const auto& chunks) {
        std::vector<std::uint64_t> offsets;
        offsets.reserve(chunks.size());
        std::uint64_t offset = 0U;
        for (const auto& chunk : chunks) {
            offsets.push_back(offset);
            offset += chunk.size_bytes;
        }
        return offsets;
    };
    const auto predecessor_offsets = offsets_for(predecessor_manifest.chunks);
    const auto successor_offsets = offsets_for(successor_manifest.chunks);
    std::uint64_t shifted_matching_chunks = 0U;
    std::uint64_t shifted_matching_bytes = 0U;
    for (std::size_t target = 0U;
         target < successor_manifest.chunks.size(); ++target) {
        const auto& target_chunk = successor_manifest.chunks[target];
        for (std::size_t candidate = 0U;
             candidate < predecessor_manifest.chunks.size(); ++candidate) {
            const auto& candidate_chunk =
                predecessor_manifest.chunks[candidate];
            if (target_chunk.sha256 == candidate_chunk.sha256 &&
                target_chunk.size_bytes == candidate_chunk.size_bytes &&
                successor_offsets[target] != predecessor_offsets[candidate]) {
                ++shifted_matching_chunks;
                shifted_matching_bytes += target_chunk.size_bytes;
                break;
            }
        }
    }
    require(
        shifted_matching_chunks >= 4U &&
            shifted_matching_bytes >= 16U * mebibyte,
        "deterministic insertion fixture did not retain a useful shifted chunk frontier");

    const Channel receiver_channel =
        channel_to(source_actor, "content-defined-delta-session");
    const Channel source_channel =
        channel_to(receiver_actor, "content-defined-delta-session");
    auto source_session = source.service_.make_serve_session_or_throw(
        source_channel);
    const auto source_snapshot = source.owner_.snapshot_or_throw();
    ReplicaHistoryReadTrace source_history_trace;
    ReplicaHistoryReadTrace receiver_history_trace;
    require(
        sqlite3_trace_v2(
            source.db_.db.get(), SQLITE_TRACE_STMT,
            count_replica_history_reads, &source_history_trace) == SQLITE_OK &&
            sqlite3_trace_v2(
                receiver.db_.db.get(), SQLITE_TRACE_STMT,
                count_replica_history_reads,
                &receiver_history_trace) == SQLITE_OK,
        "content-defined fixture could not install bounded-history traces");

    std::optional<std::string> cursor = predecessor.operation_id;
    std::optional<std::string> source_digest =
        source_snapshot.evidence_set_digest;
    std::optional<anonsync::SyncReplicaReconciliationPayloadContinuation>
        continuation;
    std::uint64_t network_bytes = 0U;
    std::uint64_t staged_bytes = 0U;
    std::uint64_t reused_bytes = 0U;
    std::uint64_t reused_chunks = 0U;
    std::uint64_t predecessor_manifest_scans = 0U;
    std::uint64_t predecessor_manifest_reuses = 0U;
    std::uint64_t predecessor_manifest_hashed_bytes = 0U;
    std::uint64_t target_manifest_publications = 0U;
    std::uint64_t target_manifest_reuses = 0U;
    std::uint64_t predecessor_index_builds = 0U;
    std::uint64_t predecessor_index_reuses = 0U;
    std::uint64_t predecessor_projection_steps = 0U;
    std::uint64_t predecessor_incomplete_projection_steps = 0U;
    std::uint64_t wire_range_count = 0U;
    std::uint64_t source_payload_page_count = 0U;
    std::uint64_t source_manifest_preparation_page_count = 0U;
    std::uint64_t terminal_verification_page_count = 0U;
    std::uint64_t terminal_verification_steps = 0U;
    std::uint64_t terminal_verification_local_continuation_steps = 0U;
    std::uint64_t terminal_verification_step_budget_exhaustions = 0U;
    std::optional<std::string> target_manifest_digest;
    std::uint64_t page_count = 0U;
    bool completed = false;
    bool reused_before_predecessor_projection_completed = false;
    for (; page_count < 32U; ++page_count) {
        const auto outbound = receiver.service_.make_request_or_throw(
            receiver_channel, cursor, source_digest, continuation);
        const bool terminal_verification_request =
            outbound.request.payload_continuation.has_value() &&
            outbound.request.payload_continuation->next_offset_bytes ==
                outbound.request.payload_continuation->total_size_bytes;
        const std::uint64_t source_opens_before =
            source_session.payload_targeted_opens();
        const std::uint64_t source_windows_before =
            source_session.ranged_payload_windows();
        const std::uint64_t source_ranges_before =
            source_session.ranged_payload_ranges();
        const std::uint64_t source_bytes_before =
            source_session.ranged_payload_bytes();
        const auto inbound = source.service_.serve_request_or_throw(
            source_channel, outbound.request_frame, source_session);
        if (inbound.response.disposition ==
            anonsync::SyncReplicaReconciliationResponseDisposition::
                SourcePayloadPreparing) {
            ++source_manifest_preparation_page_count;
            require(
                !terminal_verification_request &&
                    inbound.response.operations.empty() &&
                    inbound.response.payloads.empty() &&
                    inbound.response.has_more &&
                    inbound.response.blocked_operation_id ==
                        std::optional<std::string>(successor.operation_id) &&
                    inbound.response.next_after_operation_id ==
                        outbound.request.after_operation_id &&
                    source_session.payload_targeted_opens() ==
                        source_opens_before + 1U &&
                    source_session.ranged_payload_windows() ==
                        source_windows_before &&
                    source_session.ranged_payload_ranges() ==
                        source_ranges_before &&
                    source_session.ranged_payload_bytes() ==
                        source_bytes_before,
                "bounded source manifest preparation did not yield at the exact blocked operation without framing payload bytes");
            const auto preparing = receiver.service_.apply_response_or_throw(
                receiver_channel, outbound.request, inbound.response_frame);
            require(
                preparing.disposition ==
                        anonsync::SyncReplicaReconciliationApplyDisposition::
                            SourcePayloadPreparing &&
                    preparing.inserted_active == 0U &&
                    preparing.inserted_pending == 0U &&
                    preparing.inserted_quarantined == 0U &&
                    preparing.staged_payload_bytes == 0U &&
                    preparing.blocked_operation_id ==
                        inbound.response.blocked_operation_id &&
                    preparing.next_after_operation_id ==
                        outbound.request.after_operation_id,
                "receiver did not preserve the bounded source-preparation continuation");
            cursor = preparing.next_after_operation_id;
            source_digest = preparing.source_evidence_set_digest;
            continuation = preparing.payload_continuation;
            continue;
        }
        if (terminal_verification_request) {
            ++terminal_verification_page_count;
            require(
                inbound.response.operations ==
                        std::vector<anonsync::SyncReplicaOperation>{successor} &&
                    inbound.response.payloads.empty() &&
                    inbound.response.payload_continuation ==
                        outbound.request.payload_continuation &&
                    inbound.response.next_after_operation_id ==
                        outbound.request.after_operation_id &&
                    source_session.payload_targeted_opens() ==
                        source_opens_before &&
                    source_session.ranged_payload_windows() ==
                        source_windows_before &&
                    source_session.ranged_payload_ranges() ==
                        source_ranges_before &&
                    source_session.ranged_payload_bytes() ==
                        source_bytes_before,
                "terminal payload verification turn touched source payload authority");
        } else {
            ++source_payload_page_count;
            require(
                inbound.response.operations ==
                        std::vector<anonsync::SyncReplicaOperation>{successor} &&
                    !inbound.response.payloads.empty() &&
                    std::all_of(
                        inbound.response.payloads.begin(),
                        inbound.response.payloads.end(),
                        [](const auto& payload) {
                            return payload.delta_manifest_digest.has_value();
                        }),
                "content-defined source page did not bind one ranged successor and a nonempty manifest-bound window");
            const auto& wire_payload = inbound.response.payloads.front();
            if (source_payload_page_count == 1U) {
                require(
                    !outbound.request.cached_delta_manifest_digest.has_value() &&
                        wire_payload.delta_manifest.has_value() &&
                        wire_payload.delta_manifest->parameters == parameters &&
                        wire_payload.delta_manifest->chunks.size() ==
                            successor_manifest.chunks.size(),
                    "initial content-defined range did not bootstrap the exact bounded target manifest");
                require(
                    std::all_of(
                        std::next(inbound.response.payloads.begin()),
                        inbound.response.payloads.end(),
                        [&](const auto& payload) {
                            return !payload.delta_manifest.has_value() &&
                                   payload.delta_manifest_digest ==
                                       wire_payload.delta_manifest_digest;
                        }),
                    "initial content-defined window repeated or changed its complete manifest after the first range");
                target_manifest_digest = wire_payload.delta_manifest_digest;
                auto forged = inbound.response;
                forged.payloads.front().bytes.assign(
                    forged.payloads.front().bytes.size(), 'Q');
                forged.payloads.front().chunk_sha256 =
                    anonsync::sha256_hex(forged.payloads.front().bytes);
                require_error(
                    [&] {
                        const std::string forged_frame =
                            anonsync::encode_sync_replica_reconciliation_response_or_throw(
                                forged, wire);
                        (void)receiver.service_.apply_response_or_throw(
                            receiver_channel, outbound.request, forged_frame);
                    },
                    "full chunk digest disagrees",
                    "receiver accepted a forged complete content-defined chunk");
                require(
                    receiver.payload_store_.snapshot_or_throw().transient_bytes() ==
                        0U,
                    "rejected content-defined chunk changed the durable prefix");
            } else {
                require(
                    outbound.request.cached_delta_manifest_digest ==
                            target_manifest_digest &&
                        std::all_of(
                            inbound.response.payloads.begin(),
                            inbound.response.payloads.end(),
                            [&](const auto& payload) {
                                return payload.delta_manifest_digest ==
                                           target_manifest_digest &&
                                       !payload.delta_manifest.has_value();
                            }),
                    "continued content-defined window copied or changed the complete manifest instead of using exact process-local references");
            }
            wire_range_count += static_cast<std::uint64_t>(
                inbound.response.payloads.size());
            for (const auto& payload : inbound.response.payloads) {
                network_bytes +=
                    static_cast<std::uint64_t>(payload.bytes.size());
            }
        }
        const auto applied = receiver.service_.apply_response_or_throw(
            receiver_channel, outbound.request, inbound.response_frame);
        staged_bytes += applied.staged_payload_bytes;
        reused_bytes += applied.reused_payload_bytes;
        reused_chunks += applied.reused_payload_chunks;
        terminal_verification_steps +=
            applied.terminal_verification_steps;
        terminal_verification_local_continuation_steps +=
            applied.terminal_verification_local_continuation_steps;
        terminal_verification_step_budget_exhaustions +=
            applied.terminal_verification_step_budget_exhaustions;
        predecessor_manifest_scans +=
            applied.delta_predecessor_manifest_scans;
        predecessor_manifest_reuses +=
            applied.delta_predecessor_manifest_reuses;
        predecessor_manifest_hashed_bytes +=
            applied.delta_predecessor_manifest_hashed_bytes;
        target_manifest_publications +=
            applied.target_content_defined_manifest_publications;
        target_manifest_reuses +=
            applied.target_content_defined_manifest_reuses;
        predecessor_index_builds +=
            applied.delta_predecessor_index_builds;
        predecessor_index_reuses +=
            applied.delta_predecessor_index_reuses;
        if (applied.delta_predecessor_manifest_hashed_bytes != 0U) {
            ++predecessor_projection_steps;
            require(
                applied.delta_predecessor_manifest_hashed_bytes <=
                    predecessor_projection_bytes_per_apply,
                "same-path predecessor projection crossed its configured per-apply byte frontier");
            if (applied.delta_predecessor_manifest_scans == 0U) {
                ++predecessor_incomplete_projection_steps;
                if (applied.reused_payload_bytes != 0U) {
                    reused_before_predecessor_projection_completed = true;
                }
            }
        }
        if (page_count == 0U) {
            require(
                source_history_trace.complete_operation_projection_read_count ==
                        0U &&
                    source_history_trace.complete_visible_projection_read_count ==
                        0U &&
                    receiver_history_trace.complete_operation_projection_read_count ==
                        0U &&
                    receiver_history_trace.complete_visible_projection_read_count ==
                        0U,
                "first bounded delta-progress turn reconstructed complete retained history");
        }
        if (applied.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied) {
            require(
                applied.inserted_active == 1U &&
                    !applied.payload_continuation.has_value(),
                "content-defined delta completion did not admit exactly one successor");
            completed = true;
            ++page_count;
            break;
        }
        require(
            applied.disposition ==
                    anonsync::SyncReplicaReconciliationApplyDisposition::
                        PayloadProgress &&
                applied.payload_continuation.has_value(),
            "content-defined delta did not return bounded payload progress");
        cursor = applied.next_after_operation_id;
        source_digest = applied.source_evidence_set_digest;
        continuation = applied.payload_continuation;
    }
    require(
        sqlite3_trace_v2(source.db_.db.get(), 0U, nullptr, nullptr) ==
                SQLITE_OK &&
            sqlite3_trace_v2(receiver.db_.db.get(), 0U, nullptr, nullptr) ==
                SQLITE_OK,
        "content-defined fixture could not remove bounded-history traces");
    require(completed && page_count >= 2U && page_count < 32U,
            "content-defined insertion delta did not settle through bounded referenced pages");
    require(
        source_history_trace.evidence_page_range_read_count == page_count &&
            source_history_trace.complete_operation_projection_read_count ==
                0U &&
            source_history_trace.complete_visible_projection_read_count ==
                0U,
        "bounded source windows reconstructed complete retained replica history");
    require(
        receiver_history_trace.evidence_page_range_read_count == 0U &&
            receiver_history_trace.complete_operation_projection_read_count <=
                2U &&
            receiver_history_trace.complete_visible_projection_read_count <=
                2U &&
            receiver_history_trace.exact_visible_path_read_count >=
                source_payload_page_count &&
            receiver_history_trace.exact_operation_read_count >=
                source_payload_page_count,
        "bounded receiver windows did not remain identity- and path-local: range=" +
            std::to_string(receiver_history_trace.evidence_page_range_read_count) +
            " complete_ops=" +
            std::to_string(receiver_history_trace.complete_operation_projection_read_count) +
            " complete_visible=" +
            std::to_string(receiver_history_trace.complete_visible_projection_read_count) +
            " exact_visible=" +
            std::to_string(receiver_history_trace.exact_visible_path_read_count) +
            " exact_ops=" +
            std::to_string(receiver_history_trace.exact_operation_read_count) +
            " pages=" + std::to_string(page_count));
    require(
        staged_bytes <= network_bytes &&
            staged_bytes + reused_bytes == new_bytes.size() &&
            reused_bytes >= shifted_matching_bytes &&
            reused_chunks >= shifted_matching_chunks &&
            network_bytes < new_bytes.size() / 2U,
        "content-defined delta did not reuse the shifted predecessor majority under a bounded multi-range window");
    require(
        predecessor_manifest_scans == 1U &&
            predecessor_manifest_hashed_bytes == old_bytes.size() &&
            predecessor_projection_steps ==
                (old_size + predecessor_projection_bytes_per_apply - 1U) /
                    predecessor_projection_bytes_per_apply &&
            predecessor_incomplete_projection_steps + 1U ==
                predecessor_projection_steps &&
            reused_before_predecessor_projection_completed &&
            target_manifest_publications == 1U &&
            target_manifest_reuses == wire_range_count - 1U &&
            predecessor_index_builds == 1U &&
            predecessor_manifest_reuses == predecessor_index_reuses,
        "receiver did not bound, incrementally index, and reuse the exact shifted predecessor before retaining its complete manifest: scans=" +
            std::to_string(predecessor_manifest_scans) +
            " reuses=" + std::to_string(predecessor_manifest_reuses) +
            " hashed=" + std::to_string(predecessor_manifest_hashed_bytes) +
            " steps=" + std::to_string(predecessor_projection_steps) +
            " incomplete=" +
            std::to_string(predecessor_incomplete_projection_steps) +
            " index_builds=" +
            std::to_string(predecessor_index_builds) +
            " index_reuses=" +
            std::to_string(predecessor_index_reuses));
    require(
        source_session.content_defined_manifest_scans() == 1U &&
            source_session.content_defined_manifest_reuses() ==
                source_payload_page_count - 1U &&
            source_session.content_defined_manifest_hashed_bytes() ==
                new_bytes.size() &&
            source_session.content_defined_manifest_projection_steps() ==
                (new_bytes.size() +
                     anonsync::kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest -
                     1U) /
                    anonsync::kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest &&
            source_session.content_defined_manifest_projection_restarts() == 0U &&
            source_session.source_payload_preparing_responses() ==
                source_manifest_preparation_page_count &&
            source_manifest_preparation_page_count + 1U ==
                source_session.content_defined_manifest_projection_steps() &&
            source_session.content_defined_manifest_publications() == 1U &&
            source_session.content_defined_manifest_references() ==
                wire_range_count - 1U &&
            source_session.content_defined_chunk_index_builds() == 1U &&
            source_session.content_defined_chunk_index_reuses() ==
                source_payload_page_count - 1U &&
            source_session.content_defined_chunk_index_lookups() ==
                source_payload_page_count &&
            terminal_verification_page_count == 0U &&
            terminal_verification_steps == 2U &&
            terminal_verification_local_continuation_steps == 1U &&
            terminal_verification_step_budget_exhaustions == 0U,
        "source manifest reuse or receiver-local terminal verification did not remain exact and payload-cold");
    require_payload_available(
        receiver.payload_store_, successor, new_bytes,
        "content-defined delta did not reconstruct exact insertion-shifted successor bytes");
    require(
        receiver.owner_.snapshot_or_throw().evidence_set_digest ==
            source_snapshot.evidence_set_digest,
        "content-defined delta did not converge the exact causal evidence set");
}


void test_source_manifest_projection_resumes_across_fresh_serve_sessions() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-reconciliation-source-projection-cross-session";
    const anonsync::SyncReplicaActor source_actor{
        "device-source-projection-cross-session-source", 11901U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-source-projection-cross-session-receiver", 11902U};
    constexpr std::uint64_t mebibyte = 1024U * 1024U;
    constexpr std::uint64_t source_step_bytes = mebibyte;

    auto wire = protocol_limits(1U);
    wire.max_single_payload_bytes = mebibyte;
    wire.max_payload_bytes_per_page = mebibyte;
    wire.max_response_frame_bytes = 8U * mebibyte;
    auto store = payload_limits();
    store.max_payload_bytes = 4U * mebibyte;
    store.max_indexed_bytes = 16U * mebibyte;
    store.max_transient_bytes = 8U * mebibyte;

    ReplicaFixture source(
        temporary, "source-projection-cross-session-source", folder,
        source_actor, owner_limits(256U), wire, store,
        anonsync::sync_replica_default_selective_sync_policy(),
        anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        anonsync::
            kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        anonsync::
            kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
        source_step_bytes);
    ReplicaFixture receiver(
        temporary, "source-projection-cross-session-receiver", folder,
        receiver_actor, owner_limits(256U), wire, store);

    std::string bytes(3U * mebibyte + 173U, '\0');
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
        bytes[index] = static_cast<char>(
            (index * 131U + index / 4093U + 17U) & 0xffU);
    }
    const auto operation = source.publish_file("media/large.bin", bytes);
    const Channel receiver_channel =
        channel_to(source_actor, "source-projection-cross-session");
    const Channel source_channel =
        channel_to(receiver_actor, "source-projection-cross-session");

    std::uint64_t preparing_responses = 0U;
    bool completed = false;
    for (std::uint64_t turn = 0U; turn < 8U; ++turn) {
        const auto outbound = receiver.service_.make_request_or_throw(
            receiver_channel);
        auto fresh_session = source.service_.make_serve_session_or_throw(
            source_channel);
        const auto inbound = source.service_.serve_request_or_throw(
            source_channel, outbound.request_frame, fresh_session);
        const auto applied = receiver.service_.apply_response_or_throw(
            receiver_channel, outbound.request, inbound.response_frame);

        require(
            fresh_session.content_defined_manifest_projection_steps() == 1U &&
                fresh_session.content_defined_manifest_hashed_bytes() > 0U &&
                fresh_session.content_defined_manifest_hashed_bytes() <=
                    source_step_bytes &&
                fresh_session.content_defined_manifest_projection_restarts() ==
                    0U,
            "one fresh serve session did not perform exactly one bounded source-manifest pulse");
        if (inbound.response.disposition ==
            anonsync::SyncReplicaReconciliationResponseDisposition::
                SourcePayloadPreparing) {
            ++preparing_responses;
            require(
                inbound.response.operations.empty() &&
                    inbound.response.payloads.empty() &&
                    inbound.response.has_more &&
                    inbound.response.blocked_operation_id ==
                        std::optional<std::string>(operation.operation_id) &&
                    applied.disposition ==
                        anonsync::SyncReplicaReconciliationApplyDisposition::
                            SourcePayloadPreparing &&
                    fresh_session.source_payload_preparing_responses() == 1U &&
                    fresh_session.content_defined_manifest_scans() == 0U &&
                    fresh_session.content_defined_chunk_index_builds() == 0U,
                "fresh-session source projection did not return one exact bounded preparing response");
            continue;
        }

        require(
            inbound.response.disposition ==
                    anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
                inbound.response.operations ==
                    std::vector<anonsync::SyncReplicaOperation>{operation} &&
                !inbound.response.payloads.empty() &&
                inbound.response.payloads.front().delta_manifest.has_value() &&
                applied.disposition ==
                    anonsync::SyncReplicaReconciliationApplyDisposition::
                        PayloadProgress &&
                fresh_session.source_payload_preparing_responses() == 0U &&
                fresh_session.content_defined_manifest_scans() == 1U &&
                fresh_session.content_defined_chunk_index_builds() == 1U &&
                fresh_session.content_defined_manifest_hashed_bytes() == 173U,
            "cross-session source projection did not complete once from retained bounded progress");
        completed = true;
        break;
    }
    require(
        completed && preparing_responses == 3U,
        "source manifest projection did not survive three fresh-session yields before exact completion");
}


void test_source_manifest_projection_advances_without_a_peer_after_discovery() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-reconciliation-source-projection-local-scheduler";
    const anonsync::SyncReplicaActor source_actor{
        "device-source-projection-local-scheduler-source", 11903U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-source-projection-local-scheduler-receiver", 11904U};
    constexpr std::uint64_t mebibyte = 1024U * 1024U;
    constexpr std::uint64_t source_step_bytes = mebibyte;

    auto wire = protocol_limits(1U);
    wire.max_single_payload_bytes = mebibyte;
    wire.max_payload_bytes_per_page = mebibyte;
    wire.max_response_frame_bytes = 8U * mebibyte;
    auto store = payload_limits();
    store.max_payload_bytes = 4U * mebibyte;
    store.max_indexed_bytes = 16U * mebibyte;
    store.max_transient_bytes = 8U * mebibyte;

    ReplicaFixture source(
        temporary, "source-projection-local-scheduler-source", folder,
        source_actor, owner_limits(256U), wire, store,
        anonsync::sync_replica_default_selective_sync_policy(),
        anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        anonsync::
            kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        anonsync::
            kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
        source_step_bytes);
    ReplicaFixture receiver(
        temporary, "source-projection-local-scheduler-receiver", folder,
        receiver_actor, owner_limits(256U), wire, store);

    std::string bytes(3U * mebibyte + 173U, '\0');
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
        bytes[index] = static_cast<char>(
            (index * 193U + index / 8191U + 29U) & 0xffU);
    }
    const auto operation = source.publish_file("media/local-large.bin", bytes);
    const Channel receiver_channel =
        channel_to(source_actor, "source-projection-local-scheduler");
    const Channel source_channel =
        channel_to(receiver_actor, "source-projection-local-scheduler");

    const auto outbound = receiver.service_.make_request_or_throw(
        receiver_channel);
    auto discovery_session = source.service_.make_serve_session_or_throw(
        source_channel);
    const auto discovery = source.service_.serve_request_or_throw(
        source_channel, outbound.request_frame, discovery_session);
    const auto discovery_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, outbound.request, discovery.response_frame);
    const auto discovered = source.service_.source_manifest_projection_status();
    require(
        discovery.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::
                    SourcePayloadPreparing &&
            discovery.response.operations.empty() &&
            discovery.response.payloads.empty() &&
            discovery.response.blocked_operation_id ==
                std::optional<std::string>(operation.operation_id) &&
            discovery_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::
                    SourcePayloadPreparing &&
            discovery_session.content_defined_manifest_projection_steps() ==
                1U &&
            discovery_session.content_defined_manifest_hashed_bytes() ==
                source_step_bytes &&
            discovered.pending &&
            discovered.operation_id == operation.operation_id &&
            discovered.content_sha256 == operation.content_sha256 &&
            discovered.total_size_bytes == bytes.size() &&
            discovered.next_offset_bytes == source_step_bytes,
        "one authenticated request did not discover exactly one bounded source-local manifest obligation");

    const auto first =
        source.service_.continue_source_manifest_projection_or_throw();
    const auto second =
        source.service_.continue_source_manifest_projection_or_throw();
    const auto final =
        source.service_.continue_source_manifest_projection_or_throw();
    require(
        first.disposition ==
                anonsync::
                    SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                        Progress &&
            first.before.next_offset_bytes == source_step_bytes &&
            first.after.next_offset_bytes == 2U * source_step_bytes &&
            first.hashed_bytes == source_step_bytes &&
            !first.projection_restarted &&
            second.disposition ==
                anonsync::
                    SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                        Progress &&
            second.before.next_offset_bytes == 2U * source_step_bytes &&
            second.after.next_offset_bytes == 3U * source_step_bytes &&
            second.hashed_bytes == source_step_bytes &&
            !second.projection_restarted &&
            final.disposition ==
                anonsync::
                    SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                        Completed &&
            final.before.next_offset_bytes == 3U * source_step_bytes &&
            !final.after.pending && final.hashed_bytes == 173U &&
            !final.projection_restarted,
        "three peer-independent source-local pulses did not finish the exact retained projection");

    const auto idle =
        source.service_.continue_source_manifest_projection_or_throw();
    require(
        idle.disposition ==
                anonsync::
                    SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                        NoPendingWork &&
            !idle.before.pending && !idle.after.pending &&
            idle.hashed_bytes == 0U &&
            idle.newly_completed_chunk_count == 0U &&
            !idle.projection_restarted,
        "idle source-local scheduling fabricated projection work");

    const auto replay_outbound = receiver.service_.make_request_or_throw(
        receiver_channel);
    auto replay_session = source.service_.make_serve_session_or_throw(
        source_channel);
    const auto replay = source.service_.serve_request_or_throw(
        source_channel, replay_outbound.request_frame, replay_session);
    const auto replay_apply = receiver.service_.apply_response_or_throw(
        receiver_channel, replay_outbound.request, replay.response_frame);
    require(
        replay.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
            replay.response.operations ==
                std::vector<anonsync::SyncReplicaOperation>{operation} &&
            !replay.response.payloads.empty() &&
            replay.response.payloads.front().delta_manifest.has_value() &&
            replay_apply.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::
                    PayloadProgress &&
            replay_session.content_defined_manifest_projection_steps() == 0U &&
            replay_session.content_defined_manifest_hashed_bytes() == 0U &&
            replay_session.content_defined_manifest_scans() == 0U &&
            replay_session.content_defined_manifest_reuses() == 1U &&
            replay_session.content_defined_chunk_index_builds() == 0U &&
            replay_session.content_defined_chunk_index_reuses() == 1U,
        "fresh authenticated session did not reuse the peer-independently completed source manifest");
}


void test_local_reuse_frontier_resumes_inside_one_adaptive_chunk() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-reconciliation-local-reuse-frontier";
    const anonsync::SyncReplicaActor source_actor{
        "device-local-reuse-frontier-source", 11911U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-local-reuse-frontier-receiver", 11912U};
    constexpr std::uint64_t mebibyte = 1024U * 1024U;
    constexpr std::uint64_t old_size = 24U * mebibyte;
    constexpr std::uint64_t insertion_size = 256U * 1024U;
    constexpr std::uint64_t insertion_offset = 1U * mebibyte;
    // Deliberately do not divide the local-copy frontier. The source frames
    // several ranges before apply begins, while one 1 MiB local copy advances
    // into the middle of a later 768 KiB range. The receiver must preserve the
    // authenticated suffix instead of discarding the rest of the page.
    constexpr std::uint64_t wire_range_bytes = 768U * 1024U;
    constexpr std::uint64_t local_reuse_bytes_per_apply = 1U * mebibyte;

    auto deterministic_bytes = [](
        std::uint64_t size_bytes, std::uint64_t seed) {
        std::string bytes(static_cast<std::size_t>(size_bytes), '\0');
        std::uint64_t state = seed;
        for (char& byte : bytes) {
            state ^= state >> 12U;
            state ^= state << 25U;
            state ^= state >> 27U;
            const std::uint64_t mixed =
                state * UINT64_C(2685821657736338717);
            byte = static_cast<char>(mixed >> 56U);
        }
        return bytes;
    };

    const std::string old_bytes = deterministic_bytes(
        old_size, UINT64_C(0x0c84e2b76195ad3f));
    const std::string inserted = deterministic_bytes(
        insertion_size, UINT64_C(0x99f2b0734d1e6a85));
    std::string new_bytes;
    new_bytes.reserve(old_bytes.size() + inserted.size());
    new_bytes.append(
        old_bytes.data(), static_cast<std::size_t>(insertion_offset));
    new_bytes.append(inserted);
    new_bytes.append(
        old_bytes.data() + static_cast<std::size_t>(insertion_offset),
        old_bytes.size() - static_cast<std::size_t>(insertion_offset));

    std::optional<std::string> selected_path;
    for (std::uint64_t suffix = 0U; suffix < 4096U; ++suffix) {
        const std::string path =
            "media/local-reuse-frontier-" + std::to_string(suffix) + ".bin";
        anonsync::SyncReplicaModel probe(
            folder, source_actor, owner_limits(64U).model);
        const auto predecessor = probe.create_local_file_or_throw(
            path, old_bytes.size(), anonsync::sha256_hex(old_bytes));
        const auto successor = probe.create_local_file_or_throw(
            path, new_bytes.size(), anonsync::sha256_hex(new_bytes));
        if (predecessor.operation_id < successor.operation_id) {
            selected_path = path;
            break;
        }
    }
    require(
        selected_path.has_value(),
        "could not construct a canonical predecessor cursor for local-reuse frontier test");

    auto wire = protocol_limits(1U);
    wire.model = owner_limits(64U).model;
    wire.max_single_payload_bytes = wire_range_bytes;
    wire.max_payload_bytes_per_page = 3U * wire_range_bytes;
    wire.max_payload_extent_bytes = 64U * mebibyte;
    wire.max_response_frame_bytes = 8U * mebibyte;

    auto store = payload_limits();
    store.max_payload_bytes = 64U * mebibyte;
    store.max_indexed_bytes = 256U * mebibyte;
    store.max_transient_bytes = 96U * mebibyte;

    ReplicaFixture source(
        temporary, "local-reuse-frontier-source", folder, source_actor,
        owner_limits(64U), wire, store);
    ReplicaFixture receiver(
        temporary, "local-reuse-frontier-receiver", folder, receiver_actor,
        owner_limits(64U), wire, store,
        anonsync::sync_replica_default_selective_sync_policy(),
        local_reuse_bytes_per_apply);
    const auto predecessor = source.publish_file(*selected_path, old_bytes);
    const auto receiver_put =
        receiver.payload_store_.put_payload_or_throw(old_bytes);
    require(
        receiver_put.content_sha256 == predecessor.content_sha256 &&
            receiver.owner_.accept_remote_or_throw(predecessor) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
        "local-reuse frontier receiver did not retain the exact predecessor");
    const auto successor = source.publish_file(*selected_path, new_bytes);

    const auto parameters =
        anonsync::sync_replica_reconciliation_content_defined_parameters_or_throw(
            successor.size_bytes);
    anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest
        predecessor_manifest;
    {
        auto snapshot = receiver.payload_store_.snapshot_or_throw();
        auto opened = snapshot.open_payload_for_operation_or_throw(
            predecessor, "local-reuse frontier predecessor open");
        predecessor_manifest = opened.content_defined_manifest_or_throw(
            parameters, "local-reuse frontier predecessor manifest");
    }
    anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest
        successor_manifest;
    {
        auto snapshot = source.payload_store_.snapshot_or_throw();
        auto opened = snapshot.open_payload_for_operation_or_throw(
            successor, "local-reuse frontier successor open");
        successor_manifest = opened.content_defined_manifest_or_throw(
            parameters, "local-reuse frontier successor manifest");
    }
    const bool has_large_matching_chunk = std::any_of(
        successor_manifest.chunks.begin(), successor_manifest.chunks.end(),
        [&](const auto& target_chunk) {
            return target_chunk.size_bytes > local_reuse_bytes_per_apply &&
                   std::any_of(
                       predecessor_manifest.chunks.begin(),
                       predecessor_manifest.chunks.end(),
                       [&](const auto& candidate_chunk) {
                           return candidate_chunk.sha256 == target_chunk.sha256 &&
                                  candidate_chunk.size_bytes ==
                                      target_chunk.size_bytes;
                       });
        });
    require(
        has_large_matching_chunk,
        "local-reuse deterministic fixture lacks a matching chunk larger than one copy turn");

    const Channel receiver_channel =
        channel_to(source_actor, "local-reuse-frontier-session");
    const Channel source_channel =
        channel_to(receiver_actor, "local-reuse-frontier-session");
    auto source_session =
        source.service_.make_serve_session_or_throw(source_channel);
    const auto source_snapshot = source.owner_.snapshot_or_throw();

    std::optional<std::string> cursor = predecessor.operation_id;
    std::optional<std::string> source_digest =
        source_snapshot.evidence_set_digest;
    std::optional<anonsync::SyncReplicaReconciliationPayloadContinuation>
        continuation;
    std::uint64_t network_bytes = 0U;
    std::uint64_t staged_bytes = 0U;
    std::uint64_t reused_bytes = 0U;
    std::uint64_t local_read_ranges = 0U;
    std::uint64_t local_read_bytes = 0U;
    std::uint64_t maximum_local_read_range_bytes = 0U;
    std::uint64_t budget_exhaustions = 0U;
    std::uint64_t interior_resumptions = 0U;
    std::uint64_t already_durable_wire_ranges = 0U;
    std::uint64_t already_durable_wire_bytes = 0U;
    std::uint64_t overlap_trimmed_wire_ranges = 0U;
    bool completed = false;
    bool restarted_after_exhaustion = false;
    std::unique_ptr<anonsync::SyncReplicaReconciliationService>
        restarted_receiver;
    anonsync::SyncReplicaReconciliationService* active_receiver =
        &receiver.service_;
    std::uint64_t turns = 0U;
    for (; turns < 128U; ++turns) {
        const auto outbound = active_receiver->make_request_or_throw(
            receiver_channel, cursor, source_digest, continuation);
        const auto inbound = source.service_.serve_request_or_throw(
            source_channel, outbound.request_frame, source_session);
        for (const auto& payload : inbound.response.payloads) {
            network_bytes +=
                static_cast<std::uint64_t>(payload.bytes.size());
        }
        const auto applied = active_receiver->apply_response_or_throw(
            receiver_channel, outbound.request, inbound.response_frame);
        staged_bytes += applied.staged_payload_bytes;
        reused_bytes += applied.reused_payload_bytes;
        local_read_ranges += applied.delta_local_reuse_read_ranges;
        local_read_bytes += applied.delta_local_reuse_read_bytes;
        maximum_local_read_range_bytes = std::max(
            maximum_local_read_range_bytes,
            applied.delta_local_reuse_maximum_read_range_bytes);
        budget_exhaustions +=
            applied.delta_local_reuse_budget_exhaustions;
        interior_resumptions +=
            applied.delta_local_reuse_interior_resumptions;
        already_durable_wire_ranges +=
            applied.delta_wire_already_durable_ranges;
        already_durable_wire_bytes +=
            applied.delta_wire_already_durable_bytes;
        overlap_trimmed_wire_ranges +=
            applied.delta_wire_overlap_trimmed_ranges;
        require(
            applied.delta_local_reuse_read_bytes <=
                    local_reuse_bytes_per_apply &&
                applied.delta_local_reuse_maximum_read_range_bytes <=
                    anonsync::
                        kSyncReplicaReconciliationMaximumLocalReuseRangeBytes &&
                applied.delta_local_reuse_maximum_read_range_bytes <=
                    applied.delta_local_reuse_read_bytes &&
                applied.delta_local_reuse_budget_exhaustions <= 1U &&
                applied.delta_local_reuse_interior_resumptions <= 1U &&
                applied.delta_wire_overlap_trimmed_ranges <=
                    applied.delta_wire_already_durable_ranges,
            "one reconciliation apply exceeded the shared local-copy frontier");
        if (applied.delta_local_reuse_budget_exhaustions != 0U) {
            require(
                applied.delta_local_reuse_read_bytes ==
                        local_reuse_bytes_per_apply &&
                    applied.disposition ==
                        anonsync::SyncReplicaReconciliationApplyDisposition::
                            PayloadProgress &&
                    applied.payload_continuation.has_value(),
                "local-copy exhaustion did not stop at an exact durable continuation");
            if (!restarted_after_exhaustion) {
                restarted_receiver = std::make_unique<
                    anonsync::SyncReplicaReconciliationService>(
                        receiver.owner_, receiver.payload_store_, wire,
                        "local-reuse frontier restarted receiver",
                        anonsync::sync_replica_default_selective_sync_policy(),
                        local_reuse_bytes_per_apply);
                active_receiver = restarted_receiver.get();
                restarted_after_exhaustion = true;
            }
        }
        if (applied.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied) {
            require(
                applied.inserted_active == 1U &&
                    !applied.payload_continuation.has_value(),
                "bounded local-copy completion did not admit exactly one successor");
            completed = true;
            ++turns;
            break;
        }
        require(
            applied.disposition ==
                    anonsync::SyncReplicaReconciliationApplyDisposition::
                        PayloadProgress &&
                applied.payload_continuation.has_value(),
            "bounded local-copy turn did not return exact payload progress");
        cursor = applied.next_after_operation_id;
        source_digest = applied.source_evidence_set_digest;
        continuation = applied.payload_continuation;
    }

    require(
        completed && restarted_after_exhaustion &&
            turns > 2U && turns < 128U &&
            budget_exhaustions >= 1U && interior_resumptions >= 1U &&
            maximum_local_read_range_bytes ==
                local_reuse_bytes_per_apply &&
            already_durable_wire_ranges != 0U &&
            already_durable_wire_bytes != 0U &&
            overlap_trimmed_wire_ranges != 0U &&
            local_read_bytes == reused_bytes &&
            maximum_local_read_range_bytes > wire_range_bytes &&
            reused_bytes > local_reuse_bytes_per_apply,
        "local reuse did not exhaust, resume inside, and complete across bounded turns: completed=" +
            std::to_string(completed) + ", restarted=" +
            std::to_string(restarted_after_exhaustion) + ", turns=" +
            std::to_string(turns) + ", exhaustions=" +
            std::to_string(budget_exhaustions) + ", resumptions=" +
            std::to_string(interior_resumptions) + ", max_read=" +
            std::to_string(maximum_local_read_range_bytes) +
            ", durable_ranges=" +
            std::to_string(already_durable_wire_ranges) +
            ", durable_bytes=" +
            std::to_string(already_durable_wire_bytes) +
            ", trimmed=" + std::to_string(overlap_trimmed_wire_ranges) +
            ", reads=" + std::to_string(local_read_bytes) +
            ", reused=" + std::to_string(reused_bytes) +
            ", ranges=" + std::to_string(local_read_ranges));
    require(
        staged_bytes <= network_bytes &&
            staged_bytes + reused_bytes == new_bytes.size() &&
            staged_bytes + already_durable_wire_bytes == network_bytes &&
            already_durable_wire_bytes <= reused_bytes &&
            network_bytes < new_bytes.size() &&
            new_bytes.size() - network_bytes ==
                reused_bytes - already_durable_wire_bytes &&
            new_bytes.size() - network_bytes > insertion_size,
        "bounded local-copy turns lost wire bytes, delta efficiency, or exact byte accounting: staged=" +
            std::to_string(staged_bytes) + ", network=" +
            std::to_string(network_bytes) + ", reused=" +
            std::to_string(reused_bytes) + ", already_durable=" +
            std::to_string(already_durable_wire_bytes) + ", target=" +
            std::to_string(new_bytes.size()) + ", local_read_ranges=" +
            std::to_string(local_read_ranges) + ", local_reads=" +
            std::to_string(local_read_bytes) + ", turns=" +
            std::to_string(turns));
    require_payload_available(
        receiver.payload_store_, successor, new_bytes,
        "bounded local-copy turns did not reconstruct exact successor bytes");
    require(
        receiver.owner_.snapshot_or_throw().evidence_set_digest ==
            source_snapshot.evidence_set_digest,
        "bounded local-copy turns did not converge exact causal evidence");
}


void test_cross_file_content_defined_delta_reuses_renamed_media_chunks() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-reconciliation-cross-file-content-defined-delta";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-cross-file-source", 15901U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-cross-file-receiver", 15902U};
    constexpr std::uint64_t mebibyte = 1024U * 1024U;
    constexpr std::uint64_t old_size = 48U * mebibyte;
    constexpr std::uint64_t insertion_size = 256U * 1024U;
    constexpr std::uint64_t insertion_offset = 1U * mebibyte;

    auto deterministic_bytes = [](
        std::uint64_t size_bytes, std::uint64_t seed) {
        std::string bytes(static_cast<std::size_t>(size_bytes), '\0');
        std::uint64_t state = seed;
        for (char& byte : bytes) {
            state ^= state >> 12U;
            state ^= state << 25U;
            state ^= state >> 27U;
            const std::uint64_t mixed =
                state * UINT64_C(2685821657736338717);
            byte = static_cast<char>(mixed >> 56U);
        }
        return bytes;
    };

    const std::string old_bytes = deterministic_bytes(
        old_size, UINT64_C(0x8f6d9a43b1c257e1));
    const std::string inserted = deterministic_bytes(
        insertion_size, UINT64_C(0x3be187f40629da5c));
    std::string new_bytes;
    new_bytes.reserve(old_bytes.size() + inserted.size());
    new_bytes.append(
        old_bytes.data(), static_cast<std::size_t>(insertion_offset));
    new_bytes.append(inserted);
    new_bytes.append(
        old_bytes.data() + static_cast<std::size_t>(insertion_offset),
        old_bytes.size() - static_cast<std::size_t>(insertion_offset));
    const std::size_t distant_edit =
        static_cast<std::size_t>(28U * mebibyte + insertion_size);
    new_bytes[distant_edit] = static_cast<char>(
        static_cast<unsigned char>(new_bytes[distant_edit]) ^ 0xa5U);

    auto wire = protocol_limits(1U);
    wire.model = owner_limits(64U).model;
    wire.max_single_payload_bytes = 4U * mebibyte;
    wire.max_payload_bytes_per_page = 4U * mebibyte;
    wire.max_payload_extent_bytes = 96U * mebibyte;
    wire.max_response_frame_bytes = 8U * mebibyte;

    auto store = payload_limits();
    store.max_payload_bytes = 96U * mebibyte;
    store.max_indexed_bytes = 384U * mebibyte;
    store.max_transient_bytes = 128U * mebibyte;

    ReplicaFixture source(
        temporary, "cross-file-source", folder, source_actor,
        owner_limits(64U), wire, store);
    ReplicaFixture receiver(
        temporary, "cross-file-receiver", folder, receiver_actor,
        owner_limits(64U), wire, store);
    const std::string decoy_bytes = deterministic_bytes(
        old_size, UINT64_C(0x71d2c4a58e963bf0));
    const auto candidate = receiver.publish_file_without_payload(
        "library/00-original-media.bin", old_bytes);
    const auto decoy = receiver.publish_file(
        "library/01-unrelated-media.bin", decoy_bytes);
    const auto target = source.publish_file(
        "incoming/renamed-media.bin", new_bytes);
    require(
        target.predecessor_operation_ids.empty() &&
            target.canonical_path != candidate.canonical_path &&
            target.content_sha256 != candidate.content_sha256,
        "cross-file delta fixture accidentally created same-path predecessor authority");

    const auto parameters =
        anonsync::sync_replica_reconciliation_content_defined_parameters_or_throw(
            target.size_bytes);
    anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest decoy_manifest;
    {
        auto snapshot = receiver.payload_store_.snapshot_or_throw();
        auto opened_decoy = snapshot.open_payload_for_operation_or_throw(
            decoy, "cross-file decoy fixture open");
        decoy_manifest = opened_decoy.content_defined_manifest_or_throw(
            parameters, "cross-file decoy fixture manifest");
    }
    anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest target_manifest;
    {
        auto snapshot = source.payload_store_.snapshot_or_throw();
        auto opened = snapshot.open_payload_for_operation_or_throw(
            target, "cross-file target fixture open");
        target_manifest = opened.content_defined_manifest_or_throw(
            parameters, "cross-file target fixture manifest");
    }
    const bool decoy_has_target_chunk = std::any_of(
        target_manifest.chunks.begin(), target_manifest.chunks.end(),
        [&](const auto& target_chunk) {
            return std::any_of(
                decoy_manifest.chunks.begin(), decoy_manifest.chunks.end(),
                [&](const auto& decoy_chunk) {
                    return decoy_chunk.sha256 == target_chunk.sha256 &&
                           decoy_chunk.size_bytes == target_chunk.size_bytes;
                });
        });
    require(
        !decoy_has_target_chunk,
        "cross-file deterministic fixture did not preserve one nonmatching available candidate");
    const std::string receiver_visible_state_before_late_payload =
        receiver.owner_.snapshot_or_throw().visible_state_digest;

    const Channel receiver_channel =
        channel_to(source_actor, "cross-file-delta-session");
    const Channel source_channel =
        channel_to(receiver_actor, "cross-file-delta-session");
    auto source_session =
        source.service_.make_serve_session_or_throw(source_channel);

    ReplicaHistoryReadTrace receiver_history_trace;
    require(
        sqlite3_trace_v2(
            receiver.db_.db.get(), SQLITE_TRACE_STMT,
            count_replica_history_reads, &receiver_history_trace) == SQLITE_OK,
        "cross-file delta fixture could not install receiver history trace");

    std::optional<std::string> cursor;
    std::optional<std::string> source_digest;
    std::optional<anonsync::SyncReplicaReconciliationPayloadContinuation>
        continuation;
    std::uint64_t network_bytes = 0U;
    std::uint64_t staged_bytes = 0U;
    std::uint64_t reused_bytes = 0U;
    std::uint64_t reused_chunks = 0U;
    std::uint64_t candidate_pages = 0U;
    std::uint64_t candidate_paths_scanned = 0U;
    std::uint64_t unavailable_candidates = 0U;
    std::uint64_t availability_generation_restarts = 0U;
    std::uint64_t cross_manifest_scan_steps = 0U;
    std::uint64_t cross_manifest_scans = 0U;
    std::uint64_t cross_manifest_reuses = 0U;
    std::uint64_t cross_manifest_hashed_bytes = 0U;
    std::uint64_t cross_candidate_matches = 0U;
    std::uint64_t cross_index_builds = 0U;
    std::uint64_t cross_index_reuses = 0U;
    std::uint64_t source_manifest_preparation_turns = 0U;
    bool partial_candidate_reuse_before_complete_manifest = false;
    bool late_candidate_payload_published = false;
    bool completed = false;
    std::uint64_t turns = 0U;
    for (; turns < 32U; ++turns) {
        const auto outbound = receiver.service_.make_request_or_throw(
            receiver_channel, cursor, source_digest, continuation);
        const auto inbound = source.service_.serve_request_or_throw(
            source_channel, outbound.request_frame, source_session);
        for (const auto& payload : inbound.response.payloads) {
            network_bytes +=
                static_cast<std::uint64_t>(payload.bytes.size());
        }
        const auto applied = receiver.service_.apply_response_or_throw(
            receiver_channel, outbound.request, inbound.response_frame);
        if (applied.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::
                SourcePayloadPreparing) {
            ++source_manifest_preparation_turns;
            require(
                inbound.response.operations.empty() &&
                    inbound.response.payloads.empty() &&
                    inbound.response.blocked_operation_id ==
                        std::optional<std::string>(target.operation_id) &&
                    applied.next_after_operation_id ==
                        outbound.request.after_operation_id &&
                    !applied.payload_continuation.has_value(),
                "cross-file target source-manifest preparation advanced payload or operation authority");
            cursor = applied.next_after_operation_id;
            source_digest = cursor.has_value()
                                ? std::optional<std::string>(
                                      applied.source_evidence_set_digest)
                                : std::nullopt;
            continuation.reset();
            continue;
        }
        staged_bytes += applied.staged_payload_bytes;
        reused_bytes += applied.reused_payload_bytes;
        reused_chunks += applied.reused_payload_chunks;
        candidate_pages += applied.delta_cross_file_candidate_pages;
        candidate_paths_scanned +=
            applied.delta_cross_file_candidate_paths_scanned;
        unavailable_candidates +=
            applied.delta_cross_file_unavailable_candidates;
        availability_generation_restarts +=
            applied.delta_cross_file_availability_generation_restarts;
        cross_manifest_scan_steps +=
            applied.delta_cross_file_manifest_scan_steps;
        cross_manifest_scans += applied.delta_cross_file_manifest_scans;
        cross_manifest_reuses += applied.delta_cross_file_manifest_reuses;
        cross_manifest_hashed_bytes +=
            applied.delta_cross_file_manifest_hashed_bytes;
        cross_candidate_matches +=
            applied.delta_cross_file_candidate_matches;
        cross_index_builds += applied.delta_cross_file_index_builds;
        cross_index_reuses += applied.delta_cross_file_index_reuses;
        require(
            applied.delta_cross_file_manifest_hashed_bytes <=
                anonsync::
                    kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply &&
                applied.delta_cross_file_manifest_scan_steps <= 1U,
            "cross-file candidate projection exceeded one bounded byte step in a reconciliation turn");
        if (applied.delta_cross_file_manifest_scan_steps == 1U &&
            applied.delta_cross_file_manifest_scans == 0U &&
            applied.reused_payload_bytes != 0U) {
            partial_candidate_reuse_before_complete_manifest = true;
        }
        require(
            applied.delta_predecessor_manifest_scans == 0U &&
                applied.delta_predecessor_manifest_reuses == 0U &&
                applied.delta_predecessor_manifest_hashed_bytes == 0U &&
                applied.delta_predecessor_index_builds == 0U &&
                applied.delta_predecessor_index_reuses == 0U,
            "cross-file delta silently fell back to same-path predecessor discovery");
        if (!late_candidate_payload_published &&
            cross_manifest_scans == 1U && unavailable_candidates == 1U) {
            require(
                applied.disposition ==
                        anonsync::SyncReplicaReconciliationApplyDisposition::
                            PayloadProgress &&
                    applied.payload_continuation.has_value() &&
                    candidate_pages == 1U &&
                    candidate_paths_scanned == 2U &&
                    unavailable_candidates == 1U &&
                    applied.delta_cross_file_candidate_pages == 0U &&
                    applied.delta_cross_file_candidate_paths_scanned == 0U &&
                    applied.delta_cross_file_unavailable_candidates == 0U &&
                    applied.delta_cross_file_availability_generation_restarts ==
                        0U &&
                    applied.delta_cross_file_manifest_scan_steps == 1U &&
                    applied.delta_cross_file_manifest_scans == 1U &&
                    applied.delta_cross_file_manifest_hashed_bytes ==
                        old_size - anonsync::
                            kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply &&
                    cross_manifest_scans == 1U &&
                    cross_manifest_scan_steps == 2U &&
                    applied.delta_cross_file_candidate_matches == 0U,
                "cross-file delta did not exhaust one bounded sweep while the useful candidate payload was absent: disposition=" +
                    std::to_string(static_cast<unsigned int>(applied.disposition)) +
                    ", continuation=" +
                    std::to_string(applied.payload_continuation.has_value()) +
                    ", cumulative_pages=" + std::to_string(candidate_pages) +
                    ", cumulative_paths=" +
                    std::to_string(candidate_paths_scanned) +
                    ", pages=" +
                    std::to_string(applied.delta_cross_file_candidate_pages) +
                    ", paths=" +
                    std::to_string(applied.delta_cross_file_candidate_paths_scanned) +
                    ", unavailable=" +
                    std::to_string(applied.delta_cross_file_unavailable_candidates) +
                    ", restarts=" +
                    std::to_string(applied.delta_cross_file_availability_generation_restarts) +
                    ", steps=" +
                    std::to_string(applied.delta_cross_file_manifest_scan_steps) +
                    ", bytes=" +
                    std::to_string(applied.delta_cross_file_manifest_hashed_bytes) +
                    ", cumulative_scans=" +
                    std::to_string(cross_manifest_scans) +
                    ", cumulative_steps=" +
                    std::to_string(cross_manifest_scan_steps) +
                    ", matches=" +
                    std::to_string(applied.delta_cross_file_candidate_matches));

            require(
                sqlite3_trace_v2(
                    receiver.db_.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
                "cross-file delta fixture could not pause receiver history trace");
            const auto late_put =
                receiver.payload_store_.put_payload_or_throw(old_bytes);
            const std::string receiver_visible_state_after_late_payload =
                receiver.owner_.snapshot_or_throw().visible_state_digest;
            require(
                sqlite3_trace_v2(
                    receiver.db_.db.get(), SQLITE_TRACE_STMT,
                    count_replica_history_reads,
                    &receiver_history_trace) == SQLITE_OK,
                "cross-file delta fixture could not resume receiver history trace");
            require(
                late_put.disposition ==
                        anonsync::SyncReplicaFilePayloadStorePutDisposition::
                            Inserted &&
                    late_put.content_sha256 == candidate.content_sha256 &&
                    late_put.size_bytes == candidate.size_bytes &&
                    receiver_visible_state_after_late_payload ==
                        receiver_visible_state_before_late_payload,
                "late candidate payload publication changed causal visible state or lost exact content identity");

            anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest
                candidate_manifest;
            {
                auto snapshot = receiver.payload_store_.snapshot_or_throw();
                auto opened_candidate =
                    snapshot.open_payload_for_operation_or_throw(
                        candidate,
                        "cross-file late candidate fixture open");
                candidate_manifest =
                    opened_candidate.content_defined_manifest_or_throw(
                        parameters,
                        "cross-file late candidate fixture manifest");
            }
            std::uint64_t shared_chunk_bytes = 0U;
            std::uint64_t shared_chunk_count = 0U;
            for (const auto& target_chunk : target_manifest.chunks) {
                const auto found = std::find_if(
                    candidate_manifest.chunks.begin(),
                    candidate_manifest.chunks.end(),
                    [&](const auto& source_chunk) {
                        return source_chunk.sha256 == target_chunk.sha256 &&
                               source_chunk.size_bytes ==
                                   target_chunk.size_bytes;
                    });
                if (found != candidate_manifest.chunks.end()) {
                    ++shared_chunk_count;
                    shared_chunk_bytes += target_chunk.size_bytes;
                }
            }
            require(
                shared_chunk_count >= 4U &&
                    shared_chunk_bytes >= 16U * mebibyte,
                "late cross-file candidate did not retain a useful shifted chunk majority");
            late_candidate_payload_published = true;
        }
        if (applied.disposition ==
            anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied) {
            require(
                applied.inserted_active == 1U &&
                    !applied.payload_continuation.has_value(),
                "cross-file delta completion did not admit exactly one target operation");
            completed = true;
            ++turns;
            break;
        }
        require(
            applied.disposition ==
                    anonsync::SyncReplicaReconciliationApplyDisposition::
                        PayloadProgress &&
                applied.payload_continuation.has_value(),
            "cross-file delta did not retain one exact bounded payload continuation");
        cursor = applied.next_after_operation_id;
        source_digest = applied.source_evidence_set_digest;
        continuation = applied.payload_continuation;
    }
    require(
        sqlite3_trace_v2(receiver.db_.db.get(), 0U, nullptr, nullptr) ==
            SQLITE_OK,
        "cross-file delta fixture could not remove receiver history trace");

    require(
        completed && turns >= 2U && turns < 32U &&
            source_manifest_preparation_turns == 1U,
        "cross-file delta did not settle through bounded source preparation and range windows");
    require(
        staged_bytes <= network_bytes &&
            staged_bytes + reused_bytes == new_bytes.size() &&
            reused_bytes >= 8U * mebibyte &&
            reused_chunks >= 2U &&
            network_bytes < new_bytes.size() * 3U / 4U,
        "cross-file delta did not reuse a substantial renamed-media chunk frontier");
    require(
        late_candidate_payload_published && candidate_pages == 2U &&
            candidate_paths_scanned == 4U &&
            unavailable_candidates == 1U &&
            availability_generation_restarts == 1U &&
            cross_manifest_scan_steps == 4U &&
            cross_manifest_scans == 2U &&
            cross_manifest_hashed_bytes == old_bytes.size() * 2U &&
            cross_candidate_matches == 1U && cross_index_builds == 2U &&
            partial_candidate_reuse_before_complete_manifest &&
            cross_manifest_reuses <= 1U && cross_index_reuses <= 1U,
        "cross-file delta did not reopen one exhausted bounded sweep after late payload publication");
    require(
        receiver_history_trace.visible_file_candidate_range_read_count == 2U &&
            receiver_history_trace.evidence_page_range_read_count == 0U &&
            receiver_history_trace.complete_operation_projection_read_count ==
                2U &&
            receiver_history_trace.complete_visible_projection_read_count ==
                2U,
        "cross-file candidate discovery reconstructed retained history or repeatedly scanned the visible tree: candidate=" +
            std::to_string(receiver_history_trace.visible_file_candidate_range_read_count) +
            ", evidence_page=" +
            std::to_string(receiver_history_trace.evidence_page_range_read_count) +
            ", complete_operations=" +
            std::to_string(receiver_history_trace.complete_operation_projection_read_count) +
            ", complete_visible=" +
            std::to_string(receiver_history_trace.complete_visible_projection_read_count));
    require_payload_available(
        receiver.payload_store_, target, new_bytes,
        "cross-file delta did not reconstruct exact renamed target bytes");
    const auto target_cutpoint =
        receiver.owner_.targeted_path_cutpoint_or_throw(
            target.canonical_path, target.operation_id);
    require(
        target_cutpoint.requested_retained_operation_or_none() != nullptr &&
            *target_cutpoint.requested_retained_operation_or_none() == target,
        "cross-file delta reused bytes without admitting the exact target operation");
}

void test_metadata_only_transfer_is_payload_cold_and_rehydrates_after_policy_change() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-selective";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-selective-source", 16001U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-selective-receiver", 16002U};
    const auto metadata_policy =
        anonsync::make_sync_replica_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize,
            {{"archive", anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}},
            7U);
    ReplicaFixture source(
        temporary, "selective-source", folder, source_actor,
        owner_limits(64U), protocol_limits(8U));
    ReplicaFixture receiver(
        temporary, "selective-receiver", folder, receiver_actor,
        owner_limits(64U), protocol_limits(8U), payload_limits(),
        metadata_policy);

    const std::string bytes = "large-media-payload-remains-source-only";
    const auto operation = source.publish_file("archive/movie.mkv", bytes);
    const auto receiver_channel =
        channel_to(source_actor, "selective-metadata-session");
    const auto source_channel =
        channel_to(receiver_actor, "selective-metadata-session");
    auto source_session =
        source.service_.make_serve_session_or_throw(source_channel);
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel);
    require(
        request.request.selective_sync_policy == metadata_policy,
        "metadata-only request did not carry the exact durable policy");
    const auto response = source.service_.serve_request_or_throw(
        source_channel, request.request_frame, source_session);
    require(
        response.response.operations.size() == 1U &&
            response.response.operations.front() == operation &&
            response.response.payloads.empty() &&
            response.response.metadata_only_file_operation_ids ==
                std::vector<std::string>{operation.operation_id} &&
            source_session.payload_targeted_access_births() == 0U &&
            source_session.payload_targeted_open_attempts() == 0U &&
            source_session.content_defined_manifest_scans() == 0U,
        "metadata-only source path observed or transferred payload bytes");
    const auto applied = receiver.service_.apply_response_or_throw(
        receiver_channel, request.request, response.response_frame);
    require(
        applied.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            applied.metadata_only_file_operations == 1U &&
            applied.inserted_active == 1U &&
            applied.inserted_payloads == 0U &&
            applied.existing_payloads == 0U,
        "metadata-only receiver did not admit exactly one payload-free file operation");
    {
        const auto receiver_payloads = receiver.payload_store_.snapshot_or_throw();
        require(
            !receiver_payloads.payload_size_or_none(
                 operation.content_sha256).has_value(),
            "metadata-only receiver unexpectedly retained payload bytes");
    }

    // Policy is process-start authority. Reopen only the reconciliation service
    // with the new all-materialize snapshot; the already admitted operation must
    // replay as duplicate evidence while its bytes are obtained exactly once.
    anonsync::SyncReplicaReconciliationService materializing_receiver(
        receiver.owner_, receiver.payload_store_, protocol_limits(8U),
        "selective materializing receiver",
        anonsync::sync_replica_default_selective_sync_policy());
    const auto materialize_channel =
        channel_to(source_actor, "selective-materialize-session");
    const auto materialize_source_channel =
        channel_to(receiver_actor, "selective-materialize-session");
    auto materialize_source_session =
        source.service_.make_serve_session_or_throw(materialize_source_channel);
    const auto materialize_request =
        materializing_receiver.make_request_or_throw(materialize_channel);
    const auto materialize_response = source.service_.serve_request_or_throw(
        materialize_source_channel, materialize_request.request_frame,
        materialize_source_session);
    require(
        materialize_response.response.metadata_only_file_operation_ids.empty() &&
            materialize_response.response.payloads.size() == 1U &&
            materialize_source_session.payload_targeted_access_births() == 1U &&
            materialize_source_session.payload_targeted_open_attempts() == 1U &&
            materialize_source_session.payload_targeted_opens() == 1U,
        "materialize policy did not obtain the formerly omitted payload");
    const auto materialized = materializing_receiver.apply_response_or_throw(
        materialize_channel, materialize_request.request,
        materialize_response.response_frame);
    require(
        materialized.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            materialized.duplicate_operations == 1U &&
            materialized.metadata_only_file_operations == 0U &&
            materialized.inserted_payloads == 1U,
        "policy change did not rehydrate duplicate file evidence exactly");
    require_payload_available(
        receiver.payload_store_, operation, bytes,
        "materialized policy did not retain exact rehydrated bytes");
}

void test_capacity_blocked_page_replays_exactly_after_policy_raise() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-reconciliation-capacity";
    const anonsync::SyncReplicaActor source_actor{
        "device-reconciliation-capacity-source", 15001U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-reconciliation-capacity-receiver", 15002U};
    ReplicaFixture source(
        temporary, "capacity-source", folder, source_actor,
        owner_limits(16U), protocol_limits(8U));
    ReplicaFixture receiver(
        temporary, "capacity-receiver", folder, receiver_actor,
        owner_limits(1U), protocol_limits(8U));
    for (std::uint64_t index = 0U; index < 3U; ++index) {
        anonsync::SyncReplicaModel remote_model(
            folder,
            {"device-capacity-origin-" + std::to_string(index),
             15100U + index},
            owner_limits(16U).model);
        const auto operation = remote_model.create_local_tombstone_or_throw(
            "capacity/value-" + std::to_string(index));
        const auto admission = source.owner_.accept_remote_or_throw(operation);
        require(
            admission == anonsync::SyncReplicaAdmission::InsertedActive,
            "capacity fixture could not admit independent source evidence");
    }

    const auto receiver_channel =
        channel_to(source_actor, "capacity-session");
    const auto source_channel =
        channel_to(receiver_actor, "capacity-session");
    const auto request = receiver.service_.make_request_or_throw(
        receiver_channel);
    const auto response = source.service_.serve_request_or_throw(
        source_channel, request.request_frame);
    const auto blocked = receiver.service_.apply_response_or_throw(
        receiver_channel, request.request, response.response_frame);
    require(
        blocked.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::ReceiverCapacityBlocked &&
            blocked.blocked_operation_id.has_value() &&
            blocked.next_after_operation_id == request.request.after_operation_id,
        "receiver capacity block incorrectly advanced the source cursor");
    require(
        receiver.owner_.snapshot_or_throw().durable.operations.size() == 1U,
        "capacity-bound receiver did not retain the exact admissible prefix");

    receiver.owner_.replace_limits_or_throw(owner_limits(16U));
    const auto retried = receiver.service_.apply_response_or_throw(
        receiver_channel, request.request, response.response_frame);
    require(
        retried.disposition ==
                anonsync::SyncReplicaReconciliationApplyDisposition::PageApplied &&
            retried.duplicate_operations == 1U &&
            retried.inserted_active + retried.inserted_pending +
                    retried.inserted_quarantined ==
                2U,
        "exact response replay did not settle duplicates then admit the blocked suffix");
    require(
        receiver.owner_.snapshot_or_throw().evidence_set_digest ==
            source.owner_.snapshot_or_throw().evidence_set_digest,
        "receiver did not converge after explicit capacity policy raise");

    std::string tampered = response.response_frame;
    tampered[tampered.size() / 2U] ^= 0x01;
    const auto before_tamper = receiver.owner_.snapshot_or_throw();
    require_error(
        [&] {
            (void)receiver.service_.apply_response_or_throw(
                receiver_channel, request.request, tampered);
        },
        "digest mismatch",
        "tampered reconciliation response reached receiver admission");
    require(
        receiver.owner_.snapshot_or_throw() == before_tamper,
        "tampered response mutated receiver durable state");
}

}  // namespace

int main() {
    try {
        test_range_and_page_ceiling_are_independent_from_complete_payload_ceiling();
        test_empty_share_is_one_bounded_noop_page();
        test_share_global_multi_page_convergence_and_reverse_flow();
        test_outbox_churn_does_not_break_cursor_but_evidence_change_does();
        test_missing_payload_stalls_exactly_and_recovers_without_evidence_change();
        test_targeted_source_serving_does_not_claim_namespace_health();
        test_targeted_whole_payload_hashes_before_source_advertisement();
        test_operation_ahead_crash_window_repairs_payload_idempotently();
        test_large_payload_range_resume_survives_service_restart();
        test_terminal_verification_step_budget_yields_exact_continuation();
        test_exhausted_byte_budget_stops_before_next_ranged_payload_open();
        test_payload_progress_preserves_completed_prefix_cursor();
        test_content_defined_delta_reuses_shifted_predecessor_chunks();
        test_source_manifest_projection_resumes_across_fresh_serve_sessions();
        test_source_manifest_projection_advances_without_a_peer_after_discovery();
        test_local_reuse_frontier_resumes_inside_one_adaptive_chunk();
        test_cross_file_content_defined_delta_reuses_renamed_media_chunks();
        test_metadata_only_transfer_is_payload_cold_and_rehydrates_after_policy_change();
        test_capacity_blocked_page_replays_exactly_after_policy_raise();
        std::cout << "sync replica reconciliation service tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica reconciliation service test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() {
    std::cout << "sync replica reconciliation service test skipped on Windows\n";
    return 0;
}

#endif
