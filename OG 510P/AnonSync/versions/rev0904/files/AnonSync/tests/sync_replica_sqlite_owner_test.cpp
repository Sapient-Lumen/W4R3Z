#include "sha256_digest.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#include <array>
#include <barrier>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <exception>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

#include <sqlite3.h>

#ifdef __linux__
#include "self_exec_test_process.hpp"

#include <unistd.h>
#endif

namespace {

using anonsync::SyncReplicaActor;
using anonsync::SyncReplicaAdmission;
using anonsync::SyncReplicaEvidenceState;
using anonsync::SyncReplicaOperation;
using anonsync::SyncReplicaSqliteOwnerLimits;
using anonsync::SyncReplicaSqliteOutboxReceiptResult;
using anonsync::SyncReplicaSqliteSnapshot;
using anonsync::SyncSqliteDb;

thread_local anonsync::SyncReplicaOutboxClockObservation test_clock_observation{
    "test-boottime-realtime-v1",
    "01234567-89ab-cdef-0123-456789abcdef",
    std::string(64U, 'a'),
    100U * anonsync::kSyncReplicaNanosecondsPerSecond,
    100U * anonsync::kSyncReplicaNanosecondsPerSecond,
    1U,
    anonsync::SyncReplicaOutboxClockSynchronization::Synchronized};

void set_test_clock_epoch(std::uint64_t epoch) {
    if (epoch == 0U ||
        epoch > std::numeric_limits<std::uint64_t>::max() /
                    anonsync::kSyncReplicaNanosecondsPerSecond) {
        throw std::invalid_argument("test clock epoch is invalid");
    }
    const std::uint64_t nanoseconds =
        epoch * anonsync::kSyncReplicaNanosecondsPerSecond;
    test_clock_observation.realtime_ns = nanoseconds;
    test_clock_observation.boottime_ns = nanoseconds;
    test_clock_observation.uncertainty_ns = 1U;
    test_clock_observation.synchronization =
        anonsync::SyncReplicaOutboxClockSynchronization::Synchronized;
}

class TestOutboxClockSource final
    : public anonsync::SyncReplicaOutboxClockSource {
public:
    [[nodiscard]] anonsync::SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string&) override {
        return test_clock_observation;
    }
};

[[nodiscard]] std::unique_ptr<anonsync::SyncReplicaOutboxClockSource>
make_test_outbox_clock_source() {
    return std::make_unique<TestOutboxClockSource>();
}

struct WriterLockClockProbeState final {
    std::filesystem::path database_path;
    std::size_t observations = 0U;
    bool competing_writer_was_blocked = false;
};

class WriterLockClockProbeSource final
    : public anonsync::SyncReplicaOutboxClockSource {
public:
    explicit WriterLockClockProbeSource(
        std::shared_ptr<WriterLockClockProbeState> state)
        : state_(std::move(state)) {}

    [[nodiscard]] anonsync::SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string& label) override {
        ++state_->observations;
        sqlite3* probe = nullptr;
        int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                    SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        const int open_result = sqlite3_open_v2(
            state_->database_path.string().c_str(), &probe, flags, nullptr);
        if (open_result != SQLITE_OK) {
            const std::string detail = probe != nullptr
                ? sqlite3_errmsg(probe)
                : sqlite3_errstr(open_result);
            if (probe != nullptr) (void)sqlite3_close(probe);
            throw std::runtime_error(
                label + " writer-lock probe open failed: " + detail);
        }
        (void)sqlite3_busy_timeout(probe, 0);
        char* error = nullptr;
        const int begin_result = sqlite3_exec(
            probe, "BEGIN IMMEDIATE;", nullptr, nullptr, &error);
        const int primary_result = begin_result & 0xff;
        if (begin_result == SQLITE_OK) {
            (void)sqlite3_exec(probe, "ROLLBACK;", nullptr, nullptr, nullptr);
            (void)sqlite3_close(probe);
            throw std::runtime_error(
                label + " was sampled before SQLite writer authority");
        }
        const std::string detail = error != nullptr
            ? std::string(error)
            : std::string(sqlite3_errstr(begin_result));
        sqlite3_free(error);
        const int close_result = sqlite3_close(probe);
        if (primary_result != SQLITE_BUSY && primary_result != SQLITE_LOCKED) {
            throw std::runtime_error(
                label + " writer-lock probe failed unexpectedly: " + detail);
        }
        if (close_result != SQLITE_OK) {
            throw std::runtime_error(
                label + " writer-lock probe close failed");
        }
        state_->competing_writer_was_blocked = true;
        return {"test-writer-lock-clock-v1",
                "01234567-89ab-cdef-0123-456789abcdef",
                std::string(64U, 'b'),
                200U * anonsync::kSyncReplicaNanosecondsPerSecond,
                200U * anonsync::kSyncReplicaNanosecondsPerSecond,
                1U,
                anonsync::SyncReplicaOutboxClockSynchronization::Synchronized};
    }

private:
    std::shared_ptr<WriterLockClockProbeState> state_;
};

// Preserve the rev0873 test vocabulary while exercising the rev0874 production
// surface.  The wrapper converts each old explicit epoch into an observation
// owned by an injected clock source; no caller-time overload exists in the
// production owner.
class SyncReplicaSqliteOwner final {
public:
    SyncReplicaSqliteOwner(
        anonsync::SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        anonsync::SyncReplicaActor local_actor,
        anonsync::SyncReplicaSqliteOwnerLimits initial_limits = {},
        std::string label = "sync replica SQLite owner test")
        : owner_(db, std::move(folder_id), std::move(local_actor),
                 initial_limits, std::move(label),
                 make_test_outbox_clock_source()) {}

    [[nodiscard]] anonsync::SyncReplicaSqliteSnapshot snapshot_or_throw() {
        return owner_.snapshot_or_throw();
    }
    [[nodiscard]] anonsync::SyncReplicaOperation create_local_file_or_throw(
        std::string canonical_path,
        std::uint64_t size_bytes,
        std::string content_sha256,
        std::span<const std::string> destination_device_ids = {}) {
        return owner_.create_local_file_or_throw(
            std::move(canonical_path), size_bytes, std::move(content_sha256),
            destination_device_ids);
    }
    [[nodiscard]] anonsync::SyncReplicaOperation create_local_tombstone_or_throw(
        std::string canonical_path,
        std::span<const std::string> destination_device_ids = {}) {
        return owner_.create_local_tombstone_or_throw(
            std::move(canonical_path), destination_device_ids);
    }
    [[nodiscard]] anonsync::SyncReplicaAdmission accept_remote_or_throw(
        const anonsync::SyncReplicaOperation& operation) {
        return owner_.accept_remote_or_throw(operation);
    }
    [[nodiscard]] std::optional<anonsync::SyncReplicaSqliteOutboxClaim>
    claim_next_outbox_or_throw(
        std::string worker_id,
        std::uint64_t now_epoch,
        std::uint64_t lease_seconds,
        std::optional<std::string> destination_device_id = std::nullopt) {
        set_test_clock_epoch(now_epoch);
        return owner_.claim_next_outbox_or_throw(
            std::move(worker_id), lease_seconds,
            std::move(destination_device_id));
    }
    [[nodiscard]] std::optional<anonsync::SyncReplicaSqliteOutboxClaim>
    claim_next_outbox_for_delivery_or_throw(
        std::string worker_id,
        std::uint64_t now_epoch,
        std::uint64_t lease_seconds,
        const anonsync::SyncReplicaModelLimits& delivery_operation_limits,
        std::optional<std::string> destination_device_id,
        std::optional<anonsync::SyncReplicaValueKind> operation_kind,
        std::optional<std::uint64_t> max_file_payload_bytes,
        std::optional<anonsync::SyncReplicaFileContentInventory>
            available_file_content) {
        set_test_clock_epoch(now_epoch);
        return owner_.claim_next_outbox_for_delivery_or_throw(
            std::move(worker_id), lease_seconds, delivery_operation_limits,
            std::move(destination_device_id), operation_kind,
            max_file_payload_bytes, std::move(available_file_content));
    }
    [[nodiscard]] anonsync::SyncReplicaSqliteOutboxReceiptResult
    settle_outbox_or_throw(
        const std::string& destination_device_id,
        const std::string& operation_id,
        const std::string& claim_id,
        std::uint64_t now_epoch) {
        set_test_clock_epoch(now_epoch);
        return owner_.settle_outbox_or_throw(
            destination_device_id, operation_id, claim_id);
    }
    [[nodiscard]] anonsync::SyncReplicaSqliteOutboxReceiptResult
    renew_outbox_lease_or_throw(
        const std::string& destination_device_id,
        const std::string& operation_id,
        const std::string& claim_id,
        std::uint64_t now_epoch,
        std::uint64_t lease_seconds) {
        set_test_clock_epoch(now_epoch);
        return owner_.renew_outbox_lease_or_throw(
            destination_device_id, operation_id, claim_id, lease_seconds);
    }
    [[nodiscard]] anonsync::SyncReplicaSqliteOutboxDispatchGuardResult
    guard_outbox_claim_for_dispatch_or_throw(
        const anonsync::SyncReplicaSqliteOutboxClaim& expected_claim,
        std::uint64_t now_epoch) {
        set_test_clock_epoch(now_epoch);
        return owner_.guard_outbox_claim_for_dispatch_or_throw(expected_claim);
    }
    [[nodiscard]] anonsync::SyncReplicaSqliteOutboxReceiptResult
    release_outbox_for_retry_or_throw(
        const std::string& destination_device_id,
        const std::string& operation_id,
        const std::string& claim_id,
        std::uint64_t now_epoch,
        std::uint64_t retry_delay_seconds) {
        set_test_clock_epoch(now_epoch);
        return owner_.release_outbox_for_retry_or_throw(
            destination_device_id, operation_id, claim_id,
            retry_delay_seconds);
    }
    [[nodiscard]] anonsync::SyncReplicaOutboxClockObservationResult
    observe_outbox_clock_or_throw(std::uint64_t now_epoch) {
        set_test_clock_epoch(now_epoch);
        return owner_.observe_outbox_clock_or_throw();
    }
    [[nodiscard]] anonsync::SyncReplicaOutboxClockState
    recover_outbox_clock_or_throw(
        std::uint64_t expected_observation_generation,
        std::uint64_t now_epoch) {
        set_test_clock_epoch(now_epoch);
        return owner_.recover_outbox_clock_or_throw(
            expected_observation_generation);
    }
    void replace_limits_or_throw(
        const anonsync::SyncReplicaSqliteOwnerLimits& replacement) {
        owner_.replace_limits_or_throw(replacement);
    }

private:
    anonsync::SyncReplicaSqliteOwner owner_;
};

std::size_t checks = 0;

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
        if (std::string_view(error.what()).find(expected_fragment) ==
            std::string_view::npos) {
            fail(message + " returned unexpected error: " + error.what());
        }
        return;
    }
    fail(message + " did not reject");
}

struct TempDatabasePath final {
    std::filesystem::path path;

    explicit TempDatabasePath(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __linux__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        path = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick) + ".sqlite3");
    }

    ~TempDatabasePath() {
        std::error_code ignored;
        std::filesystem::remove(path, ignored);
        std::filesystem::remove(path.string() + "-wal", ignored);
        std::filesystem::remove(path.string() + "-shm", ignored);
        std::filesystem::remove(path.string() + "-journal", ignored);
    }
};

SyncSqliteDb open_database(const std::filesystem::path& path) {
    SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "replica SQLite owner test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "replica SQLite owner test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "replica SQLite owner test durability profile");
    return owner;
}

void exec(SyncSqliteDb& db, const std::string& sql) {
    anonsync::sqlite_exec_or_throw(
        db.db, sql, "replica SQLite owner test SQL");
}

std::uint64_t scalar_count(
    SyncSqliteDb& db,
    const std::string& table_name) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        db.db,
        "SELECT count(*) FROM main." + table_name + ";",
        "replica SQLite owner test count prepare");
    const int row = sqlite3_step(statement.stmt);
    if (row != SQLITE_ROW) {
        fail("replica SQLite owner test count query did not return a row");
    }
    const std::uint64_t value = anonsync::sqlite_column_u64_or_throw(
        statement.stmt, 0, "replica SQLite owner test count");
    if (sqlite3_step(statement.stmt) != SQLITE_DONE) {
        fail("replica SQLite owner test count query returned extra rows");
    }
    return value;
}

std::uint64_t scalar_u64_query(
    SyncSqliteDb& db,
    const std::string& sql,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        db.db, sql, label + " prepare");
    const int row = sqlite3_step(statement.stmt);
    if (row != SQLITE_ROW) {
        fail(label + " did not return a row");
    }
    const std::uint64_t value = anonsync::sqlite_column_u64_or_throw(
        statement.stmt, 0, label);
    if (sqlite3_step(statement.stmt) != SQLITE_DONE) {
        fail(label + " returned extra rows");
    }
    return value;
}

std::string scalar_text_query(
    SyncSqliteDb& db,
    const std::string& sql,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        db.db, sql, label + " prepare");
    const int row = sqlite3_step(statement.stmt);
    if (row != SQLITE_ROW) {
        fail(label + " did not return a row");
    }
    std::string value = anonsync::sqlite_column_text_or_throw(
        statement.stmt, 0, 1024U * 1024U, label);
    if (sqlite3_step(statement.stmt) != SQLITE_DONE) {
        fail(label + " returned extra rows");
    }
    return value;
}

SyncReplicaActor actor(std::string device_id, std::uint64_t epoch) {
    return {std::move(device_id), epoch};
}

SyncReplicaSqliteOwnerLimits limits(
    std::uint64_t max_operations,
    std::uint64_t max_outbox_intents = 64U,
    std::uint64_t max_outbox_destination_bytes = 4096U) {
    SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = max_operations;
    value.model.max_context_entries = 64U;
    value.model.max_predecessor_ids = 64U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 16U * 1024U * 1024U;
    value.model.max_retained_context_entries = 4096U;
    value.model.max_retained_predecessor_ids = 4096U;
    value.max_outbox_intents = max_outbox_intents;
    value.max_outbox_destination_bytes = max_outbox_destination_bytes;
    return value;
}


std::string test_u64_be(std::uint64_t value) {
    std::string out(8U, '\0');
    for (std::size_t index = 0; index < 8U; ++index) {
        out[7U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

void test_append_framed(
    anonsync::Sha256DigestBuilder& digest,
    std::string_view bytes) {
    digest.update(test_u64_be(static_cast<std::uint64_t>(bytes.size())));
    digest.update(bytes);
}

struct LegacyV1Meta final {
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t last_local_counter = 0U;
    std::uint64_t state_generation = 0U;
    std::uint64_t policy_generation = 0U;
    SyncReplicaSqliteOwnerLimits limits;
    std::uint64_t evidence_count = 0U;
    std::uint64_t active_count = 0U;
    std::uint64_t retained_canonical_bytes = 0U;
    std::uint64_t retained_context_entries = 0U;
    std::uint64_t retained_predecessor_ids = 0U;
    std::uint64_t outbox_intent_count = 0U;
    std::uint64_t outbox_destination_bytes = 0U;
    bool local_actor_compromised = false;
    std::string local_operation_digest;
    std::string operation_set_digest;
    std::string evidence_set_digest;
    std::string visible_state_digest;
    std::string outbox_digest;
    std::string cutpoint_digest;
};

std::string legacy_v1_local_operation_digest(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    const std::vector<std::string>& operation_ids) {
    anonsync::Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-local-authority-v1");
    test_append_framed(digest, folder_id);
    test_append_framed(digest, local_actor.device_id);
    digest.update(test_u64_be(local_actor.epoch));
    digest.update(test_u64_be(
        static_cast<std::uint64_t>(operation_ids.size())));
    for (const std::string& operation_id : operation_ids) {
        test_append_framed(digest, operation_id);
    }
    return digest.finish_hex();
}

std::string legacy_v1_outbox_digest(
    const std::string& folder_id,
    const std::vector<anonsync::SyncReplicaSqliteOutboxIntent>& outbox) {
    anonsync::Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-outbox-v1");
    test_append_framed(digest, folder_id);
    digest.update(test_u64_be(static_cast<std::uint64_t>(outbox.size())));
    for (const auto& intent : outbox) {
        test_append_framed(digest, intent.destination_device_id);
        test_append_framed(digest, intent.operation_id);
        digest.update(test_u64_be(intent.enqueued_generation));
    }
    return digest.finish_hex();
}

std::string previous_v2_outbox_digest(
    const std::string& folder_id,
    const std::vector<anonsync::SyncReplicaSqliteOutboxIntent>& outbox) {
    anonsync::Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-outbox-v2");
    test_append_framed(digest, folder_id);
    digest.update(test_u64_be(static_cast<std::uint64_t>(outbox.size())));
    for (const auto& intent : outbox) {
        test_append_framed(digest, intent.destination_device_id);
        test_append_framed(digest, intent.operation_id);
        digest.update(test_u64_be(intent.enqueued_generation));
        digest.update(test_u64_be(intent.lease.dispatch_attempts));
        test_append_framed(digest, intent.lease.claim_id);
        test_append_framed(digest, intent.lease.worker_id);
        digest.update(test_u64_be(intent.lease.claimed_at_epoch));
        digest.update(test_u64_be(intent.lease.lease_expires_at_epoch));
        digest.update(test_u64_be(intent.lease.retry_not_before_epoch));
    }
    return digest.finish_hex();
}

std::string retry_v4_outbox_digest(
    const std::string& folder_id,
    const std::vector<anonsync::SyncReplicaSqliteOutboxIntent>& outbox) {
    anonsync::Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-outbox-v3");
    test_append_framed(digest, folder_id);
    digest.update(test_u64_be(static_cast<std::uint64_t>(outbox.size())));
    for (const auto& intent : outbox) {
        test_append_framed(digest, intent.destination_device_id);
        test_append_framed(digest, intent.operation_id);
        digest.update(test_u64_be(intent.enqueued_generation));
        digest.update(test_u64_be(intent.lease.dispatch_attempts));
        test_append_framed(digest, intent.lease.claim_id);
        test_append_framed(digest, intent.lease.worker_id);
        digest.update(test_u64_be(intent.lease.claimed_at_epoch));
        digest.update(test_u64_be(intent.lease.lease_expires_at_epoch));
        digest.update(test_u64_be(intent.lease.retry_not_before_epoch));
        digest.update(test_u64_be(intent.lease.retry_released_at_epoch));
        digest.update(test_u64_be(static_cast<std::uint64_t>(
            intent.lease.retry_release_provenance)));
    }
    return digest.finish_hex();
}

void append_test_cutpoint_authority(
    anonsync::Sha256DigestBuilder& digest,
    const LegacyV1Meta& meta) {
    test_append_framed(digest, meta.folder_id);
    test_append_framed(digest, meta.local_actor.device_id);
    digest.update(test_u64_be(meta.local_actor.epoch));
    digest.update(test_u64_be(meta.last_local_counter));
    digest.update(test_u64_be(meta.state_generation));
    digest.update(test_u64_be(meta.policy_generation));
    digest.update(test_u64_be(meta.limits.model.max_operations));
    digest.update(test_u64_be(meta.limits.model.max_context_entries));
    digest.update(test_u64_be(meta.limits.model.max_predecessor_ids));
    digest.update(test_u64_be(
        meta.limits.model.max_canonical_operation_bytes));
    digest.update(test_u64_be(
        meta.limits.model.max_retained_canonical_bytes));
    digest.update(test_u64_be(
        meta.limits.model.max_retained_context_entries));
    digest.update(test_u64_be(
        meta.limits.model.max_retained_predecessor_ids));
    digest.update(test_u64_be(meta.limits.max_outbox_intents));
    digest.update(test_u64_be(meta.limits.max_outbox_destination_bytes));
    digest.update(test_u64_be(meta.evidence_count));
    digest.update(test_u64_be(meta.active_count));
    digest.update(test_u64_be(meta.retained_canonical_bytes));
    digest.update(test_u64_be(meta.retained_context_entries));
    digest.update(test_u64_be(meta.retained_predecessor_ids));
    digest.update(test_u64_be(meta.outbox_intent_count));
    digest.update(test_u64_be(meta.outbox_destination_bytes));
    digest.update(meta.local_actor_compromised ? std::string_view("1")
                                               : std::string_view("0"));
    test_append_framed(digest, meta.local_operation_digest);
    test_append_framed(digest, meta.operation_set_digest);
    test_append_framed(digest, meta.evidence_set_digest);
    test_append_framed(digest, meta.visible_state_digest);
    test_append_framed(digest, meta.outbox_digest);
}

std::string legacy_v1_cutpoint_digest(const LegacyV1Meta& meta) {
    anonsync::Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-sqlite-cutpoint-v1");
    append_test_cutpoint_authority(digest, meta);
    return digest.finish_hex();
}

std::string versioned_test_cutpoint_digest(
    const LegacyV1Meta& meta,
    std::uint64_t schema_version,
    std::string_view domain) {
    anonsync::Sha256DigestBuilder digest;
    digest.update(domain);
    digest.update(test_u64_be(schema_version));
    append_test_cutpoint_authority(digest, meta);
    return digest.finish_hex();
}

std::string previous_v2_cutpoint_digest(const LegacyV1Meta& meta) {
    return versioned_test_cutpoint_digest(
        meta, 2U, "anonsync-sync-replica-sqlite-cutpoint-v2");
}

std::string clock_v3_cutpoint_digest(const LegacyV1Meta& meta) {
    return versioned_test_cutpoint_digest(
        meta, 3U, "anonsync-sync-replica-sqlite-cutpoint-v3");
}

std::string retry_v4_cutpoint_digest(const LegacyV1Meta& meta) {
    return versioned_test_cutpoint_digest(
        meta, 4U, "anonsync-sync-replica-sqlite-cutpoint-v4");
}

std::string test_outbox_clock_digest(
    const std::string& folder_id,
    const SyncReplicaActor& local_actor,
    std::uint64_t high_water_epoch) {
    anonsync::Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-outbox-clock-v1");
    test_append_framed(digest, folder_id);
    test_append_framed(digest, local_actor.device_id);
    digest.update(test_u64_be(local_actor.epoch));
    digest.update(test_u64_be(high_water_epoch));
    return digest.finish_hex();
}

void bind_test_u64_be(
    sqlite3_stmt* statement,
    int index,
    std::uint64_t value,
    const std::string& label) {
    anonsync::sqlite_bind_blob_or_throw(
        statement, index, test_u64_be(value), label);
}

SyncReplicaOperation create_legacy_v1_fixture(
    SyncSqliteDb& db,
    const std::string& folder,
    const SyncReplicaActor& local,
    const SyncReplicaSqliteOwnerLimits& fixture_limits,
    const std::string& destination) {
    exec(db, "PRAGMA foreign_keys=ON;PRAGMA trusted_schema=OFF;");
    exec(db, R"LEGACY(
CREATE TABLE main.sync_replica_meta(id INTEGER PRIMARY KEY CHECK(id=1),schema_version INTEGER NOT NULL CHECK(schema_version=1),folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT;
CREATE TABLE main.sync_replica_operations(operation_id TEXT PRIMARY KEY CHECK(length(operation_id)=64),canonical_bytes BLOB NOT NULL,canonical_size_be BLOB NOT NULL CHECK(length(canonical_size_be)=8),context_count_be BLOB NOT NULL CHECK(length(context_count_be)=8),predecessor_count_be BLOB NOT NULL CHECK(length(predecessor_count_be)=8),evidence_state TEXT NOT NULL CHECK(evidence_state IN ('active','pending_missing_dependency','quarantined_dot_fork','quarantined_dependency','quarantined_causal_envelope','quarantined_dependency_cycle'))) STRICT;
CREATE TABLE main.sync_replica_parent_edges(child_operation_id TEXT NOT NULL,parent_ordinal INTEGER NOT NULL CHECK(parent_ordinal>=0),parent_operation_id TEXT NOT NULL CHECK(length(parent_operation_id)=64),PRIMARY KEY(child_operation_id,parent_ordinal),UNIQUE(child_operation_id,parent_operation_id),FOREIGN KEY(child_operation_id) REFERENCES sync_replica_operations(operation_id) ON DELETE CASCADE) STRICT;
CREATE TABLE main.sync_replica_local_operations(counter_be BLOB PRIMARY KEY CHECK(length(counter_be)=8),operation_id TEXT NOT NULL UNIQUE,FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT;
CREATE TABLE main.sync_replica_heads(operation_id TEXT PRIMARY KEY,FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT;
CREATE TABLE main.sync_replica_visible(canonical_path TEXT NOT NULL CHECK(length(canonical_path) BETWEEN 1 AND 4096),visible_ordinal INTEGER NOT NULL CHECK(visible_ordinal>=0),operation_id TEXT NOT NULL,is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)),preserve_file INTEGER NOT NULL CHECK(preserve_file IN (0,1)),PRIMARY KEY(canonical_path,visible_ordinal),UNIQUE(canonical_path,operation_id),FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT;
CREATE TABLE main.sync_replica_outbox(destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),operation_id TEXT NOT NULL,enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),PRIMARY KEY(destination_device_id,operation_id),FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT;
CREATE INDEX main.sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id);
)LEGACY");

    anonsync::SyncReplicaModel model(folder, local, fixture_limits.model);
    const SyncReplicaOperation operation = model.create_local_file_or_throw(
        "legacy/file.bin", 6U, anonsync::sha256_hex("legacy"));
    const std::vector<anonsync::SyncReplicaSqliteOutboxIntent> outbox{{
        destination, operation.operation_id, 2U, {}}};

    LegacyV1Meta meta;
    meta.folder_id = folder;
    meta.local_actor = local;
    meta.last_local_counter = model.last_local_counter();
    meta.state_generation = 2U;
    meta.policy_generation = 1U;
    meta.limits = fixture_limits;
    meta.evidence_count = static_cast<std::uint64_t>(model.evidence_count());
    meta.active_count = static_cast<std::uint64_t>(model.operation_count());
    meta.retained_canonical_bytes = model.retained_canonical_bytes();
    meta.retained_context_entries = model.retained_context_entry_count();
    meta.retained_predecessor_ids = model.retained_predecessor_id_count();
    meta.outbox_intent_count = 1U;
    meta.outbox_destination_bytes =
        static_cast<std::uint64_t>(destination.size());
    meta.local_actor_compromised = model.local_actor_compromised();
    meta.local_operation_digest = legacy_v1_local_operation_digest(
        folder, local, model.local_operation_ids());
    meta.operation_set_digest = model.operation_set_digest();
    meta.evidence_set_digest = model.evidence_set_digest();
    meta.visible_state_digest = model.visible_state_digest();
    meta.outbox_digest = legacy_v1_outbox_digest(folder, outbox);
    meta.cutpoint_digest = legacy_v1_cutpoint_digest(meta);

    anonsync::SyncSqliteStmt meta_insert = anonsync::sqlite_prepare_or_throw(
        db.db,
        "INSERT INTO main.sync_replica_meta("
        "id,schema_version,folder_id,local_device_id,local_epoch_be,"
        "last_local_counter_be,state_generation_be,policy_generation_be,"
        "max_operations_be,max_context_entries_be,max_predecessor_ids_be,"
        "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
        "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
        "max_outbox_intents_be,max_outbox_destination_bytes_be,"
        "evidence_count_be,active_count_be,retained_canonical_bytes_be,"
        "retained_context_entries_be,retained_predecessor_ids_be,"
        "outbox_intent_count_be,outbox_destination_bytes_be,"
        "local_actor_compromised,local_operation_digest,operation_set_digest,"
        "evidence_set_digest,visible_state_digest,outbox_digest,cutpoint_digest)"
        "VALUES(1,1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
        "legacy v1 fixture meta prepare");
    int index = 1;
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.folder_id, "legacy bind folder");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.local_actor.device_id,
        "legacy bind actor");
    bind_test_u64_be(meta_insert.stmt, index++, meta.local_actor.epoch,
                     "legacy bind epoch");
    bind_test_u64_be(meta_insert.stmt, index++, meta.last_local_counter,
                     "legacy bind counter");
    bind_test_u64_be(meta_insert.stmt, index++, meta.state_generation,
                     "legacy bind generation");
    bind_test_u64_be(meta_insert.stmt, index++, meta.policy_generation,
                     "legacy bind policy generation");
    bind_test_u64_be(meta_insert.stmt, index++, meta.limits.model.max_operations,
                     "legacy bind max operations");
    bind_test_u64_be(meta_insert.stmt, index++,
                     meta.limits.model.max_context_entries,
                     "legacy bind max context");
    bind_test_u64_be(meta_insert.stmt, index++,
                     meta.limits.model.max_predecessor_ids,
                     "legacy bind max predecessors");
    bind_test_u64_be(meta_insert.stmt, index++,
                     meta.limits.model.max_canonical_operation_bytes,
                     "legacy bind max canonical");
    bind_test_u64_be(meta_insert.stmt, index++,
                     meta.limits.model.max_retained_canonical_bytes,
                     "legacy bind retained bytes limit");
    bind_test_u64_be(meta_insert.stmt, index++,
                     meta.limits.model.max_retained_context_entries,
                     "legacy bind retained context limit");
    bind_test_u64_be(meta_insert.stmt, index++,
                     meta.limits.model.max_retained_predecessor_ids,
                     "legacy bind retained predecessor limit");
    bind_test_u64_be(meta_insert.stmt, index++, meta.limits.max_outbox_intents,
                     "legacy bind outbox limit");
    bind_test_u64_be(meta_insert.stmt, index++,
                     meta.limits.max_outbox_destination_bytes,
                     "legacy bind outbox byte limit");
    bind_test_u64_be(meta_insert.stmt, index++, meta.evidence_count,
                     "legacy bind evidence count");
    bind_test_u64_be(meta_insert.stmt, index++, meta.active_count,
                     "legacy bind active count");
    bind_test_u64_be(meta_insert.stmt, index++, meta.retained_canonical_bytes,
                     "legacy bind retained bytes");
    bind_test_u64_be(meta_insert.stmt, index++, meta.retained_context_entries,
                     "legacy bind retained context");
    bind_test_u64_be(meta_insert.stmt, index++, meta.retained_predecessor_ids,
                     "legacy bind retained predecessors");
    bind_test_u64_be(meta_insert.stmt, index++, meta.outbox_intent_count,
                     "legacy bind outbox count");
    bind_test_u64_be(meta_insert.stmt, index++, meta.outbox_destination_bytes,
                     "legacy bind outbox bytes");
    anonsync::sqlite_bind_bool_or_throw(
        meta_insert.stmt, index++, meta.local_actor_compromised,
        "legacy bind compromise");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.local_operation_digest,
        "legacy bind local digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.operation_set_digest,
        "legacy bind operation digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.evidence_set_digest,
        "legacy bind evidence digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.visible_state_digest,
        "legacy bind visible digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.outbox_digest,
        "legacy bind outbox digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, index++, meta.cutpoint_digest,
        "legacy bind cutpoint digest");
    anonsync::sqlite_step_done_or_throw(
        meta_insert.stmt, "legacy v1 fixture meta insert");

    const std::string canonical =
        anonsync::encode_sync_replica_operation_canonical_or_throw(
            operation, fixture_limits.model);
    anonsync::SyncSqliteStmt operation_insert =
        anonsync::sqlite_prepare_or_throw(
            db.db,
            "INSERT INTO main.sync_replica_operations("
            "operation_id,canonical_bytes,canonical_size_be,context_count_be,"
            "predecessor_count_be,evidence_state) VALUES(?,?,?,?,?,?);",
            "legacy v1 operation prepare");
    anonsync::sqlite_bind_text_or_throw(
        operation_insert.stmt, 1, operation.operation_id,
        "legacy bind operation id");
    anonsync::sqlite_bind_blob_or_throw(
        operation_insert.stmt, 2, canonical, "legacy bind canonical");
    bind_test_u64_be(operation_insert.stmt, 3,
                     static_cast<std::uint64_t>(canonical.size()),
                     "legacy bind canonical size");
    bind_test_u64_be(operation_insert.stmt, 4, 0U,
                     "legacy bind context count");
    bind_test_u64_be(operation_insert.stmt, 5, 0U,
                     "legacy bind predecessor count");
    anonsync::sqlite_bind_text_or_throw(
        operation_insert.stmt, 6, "active", "legacy bind evidence state");
    anonsync::sqlite_step_done_or_throw(
        operation_insert.stmt, "legacy v1 operation insert");

    anonsync::SyncSqliteStmt local_insert = anonsync::sqlite_prepare_or_throw(
        db.db,
        "INSERT INTO main.sync_replica_local_operations(counter_be,operation_id)"
        "VALUES(?,?);",
        "legacy v1 local operation prepare");
    bind_test_u64_be(local_insert.stmt, 1, 1U, "legacy bind local counter");
    anonsync::sqlite_bind_text_or_throw(
        local_insert.stmt, 2, operation.operation_id,
        "legacy bind local operation");
    anonsync::sqlite_step_done_or_throw(
        local_insert.stmt, "legacy v1 local operation insert");

    exec(db,
         "INSERT INTO main.sync_replica_heads(operation_id) VALUES('" +
             operation.operation_id + "');");
    const auto views = model.visible_paths();
    if (views.size() != 1U || views.front().visible_operation_ids.size() != 1U) {
        fail("legacy v1 fixture did not derive one visible row");
    }
    anonsync::SyncSqliteStmt visible_insert =
        anonsync::sqlite_prepare_or_throw(
            db.db,
            "INSERT INTO main.sync_replica_visible("
            "canonical_path,visible_ordinal,operation_id,is_primary,preserve_file)"
            "VALUES(?,?,?,?,?);",
            "legacy v1 visible prepare");
    anonsync::sqlite_bind_text_or_throw(
        visible_insert.stmt, 1, views.front().canonical_path,
        "legacy bind visible path");
    anonsync::sqlite_bind_u64_or_throw(
        visible_insert.stmt, 2, 0U, "legacy bind visible ordinal");
    anonsync::sqlite_bind_text_or_throw(
        visible_insert.stmt, 3, operation.operation_id,
        "legacy bind visible operation");
    anonsync::sqlite_bind_bool_or_throw(
        visible_insert.stmt, 4,
        views.front().primary_operation_id == operation.operation_id,
        "legacy bind primary");
    anonsync::sqlite_bind_bool_or_throw(
        visible_insert.stmt, 5,
        !views.front().preserved_file_operation_ids.empty(),
        "legacy bind preserved");
    anonsync::sqlite_step_done_or_throw(
        visible_insert.stmt, "legacy v1 visible insert");

    anonsync::SyncSqliteStmt outbox_insert =
        anonsync::sqlite_prepare_or_throw(
            db.db,
            "INSERT INTO main.sync_replica_outbox("
            "destination_device_id,operation_id,enqueued_generation_be)"
            "VALUES(?,?,?);",
            "legacy v1 outbox prepare");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 1, destination, "legacy bind destination");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 2, operation.operation_id,
        "legacy bind outbox operation");
    bind_test_u64_be(outbox_insert.stmt, 3, 2U,
                     "legacy bind outbox generation");
    anonsync::sqlite_step_done_or_throw(
        outbox_insert.stmt, "legacy v1 outbox insert");
    return operation;
}


struct PreviousV2Fixture final {
    SyncReplicaOperation operation;
    anonsync::SyncReplicaSqliteOutboxIntent intent;
    LegacyV1Meta meta;
};

PreviousV2Fixture create_previous_v2_fixture(
    SyncSqliteDb& db,
    const std::string& folder,
    const SyncReplicaActor& local,
    const SyncReplicaSqliteOwnerLimits& fixture_limits,
    const std::string& destination) {
    const SyncReplicaOperation operation = create_legacy_v1_fixture(
        db, folder, local, fixture_limits, destination);

    anonsync::SyncReplicaModel model(folder, local, fixture_limits.model);
    const SyncReplicaOperation rebuilt = model.create_local_file_or_throw(
        "legacy/file.bin", 6U, anonsync::sha256_hex("legacy"));
    if (rebuilt != operation) {
        fail("previous-v2 fixture did not reconstruct its canonical operation");
    }

    anonsync::SyncReplicaOutboxLeaseState lease;
    lease.dispatch_attempts = 1U;
    lease.claim_id = anonsync::sha256_hex("previous-v2-live-claim");
    lease.worker_id = "worker-previous-v2";
    lease.claimed_at_epoch = 100U;
    lease.lease_expires_at_epoch = 120U;
    const anonsync::SyncReplicaSqliteOutboxIntent intent{
        destination, operation.operation_id, 2U, lease};
    const std::vector<anonsync::SyncReplicaSqliteOutboxIntent> outbox{intent};

    LegacyV1Meta meta;
    meta.folder_id = folder;
    meta.local_actor = local;
    meta.last_local_counter = model.last_local_counter();
    meta.state_generation = 3U;
    meta.policy_generation = 1U;
    meta.limits = fixture_limits;
    meta.evidence_count = static_cast<std::uint64_t>(model.evidence_count());
    meta.active_count = static_cast<std::uint64_t>(model.operation_count());
    meta.retained_canonical_bytes = model.retained_canonical_bytes();
    meta.retained_context_entries = model.retained_context_entry_count();
    meta.retained_predecessor_ids = model.retained_predecessor_id_count();
    meta.outbox_intent_count = 1U;
    meta.outbox_destination_bytes =
        static_cast<std::uint64_t>(destination.size());
    meta.local_actor_compromised = model.local_actor_compromised();
    meta.local_operation_digest = legacy_v1_local_operation_digest(
        folder, local, model.local_operation_ids());
    meta.operation_set_digest = model.operation_set_digest();
    meta.evidence_set_digest = model.evidence_set_digest();
    meta.visible_state_digest = model.visible_state_digest();
    meta.outbox_digest = previous_v2_outbox_digest(folder, outbox);
    meta.cutpoint_digest = previous_v2_cutpoint_digest(meta);

    exec(db, R"PREVIOUS_V2(
CREATE TEMP TABLE sync_replica_previous_meta AS
SELECT * FROM main.sync_replica_meta WHERE id=1;
DROP INDEX main.sync_replica_outbox_operation;
DROP TABLE main.sync_replica_outbox;
DROP TABLE main.sync_replica_meta;
CREATE TABLE main.sync_replica_meta(id INTEGER PRIMARY KEY CHECK(id=1),schema_version INTEGER NOT NULL CHECK(schema_version=2),folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),local_device_id TEXT NOT NULL CHECK(length(local_device_id) BETWEEN 1 AND 128),local_epoch_be BLOB NOT NULL CHECK(length(local_epoch_be)=8),last_local_counter_be BLOB NOT NULL CHECK(length(last_local_counter_be)=8),state_generation_be BLOB NOT NULL CHECK(length(state_generation_be)=8),policy_generation_be BLOB NOT NULL CHECK(length(policy_generation_be)=8),max_operations_be BLOB NOT NULL CHECK(length(max_operations_be)=8),max_context_entries_be BLOB NOT NULL CHECK(length(max_context_entries_be)=8),max_predecessor_ids_be BLOB NOT NULL CHECK(length(max_predecessor_ids_be)=8),max_canonical_operation_bytes_be BLOB NOT NULL CHECK(length(max_canonical_operation_bytes_be)=8),max_retained_canonical_bytes_be BLOB NOT NULL CHECK(length(max_retained_canonical_bytes_be)=8),max_retained_context_entries_be BLOB NOT NULL CHECK(length(max_retained_context_entries_be)=8),max_retained_predecessor_ids_be BLOB NOT NULL CHECK(length(max_retained_predecessor_ids_be)=8),max_outbox_intents_be BLOB NOT NULL CHECK(length(max_outbox_intents_be)=8),max_outbox_destination_bytes_be BLOB NOT NULL CHECK(length(max_outbox_destination_bytes_be)=8),evidence_count_be BLOB NOT NULL CHECK(length(evidence_count_be)=8),active_count_be BLOB NOT NULL CHECK(length(active_count_be)=8),retained_canonical_bytes_be BLOB NOT NULL CHECK(length(retained_canonical_bytes_be)=8),retained_context_entries_be BLOB NOT NULL CHECK(length(retained_context_entries_be)=8),retained_predecessor_ids_be BLOB NOT NULL CHECK(length(retained_predecessor_ids_be)=8),outbox_intent_count_be BLOB NOT NULL CHECK(length(outbox_intent_count_be)=8),outbox_destination_bytes_be BLOB NOT NULL CHECK(length(outbox_destination_bytes_be)=8),local_actor_compromised INTEGER NOT NULL CHECK(local_actor_compromised IN (0,1)),local_operation_digest TEXT NOT NULL CHECK(length(local_operation_digest)=64),operation_set_digest TEXT NOT NULL CHECK(length(operation_set_digest)=64),evidence_set_digest TEXT NOT NULL CHECK(length(evidence_set_digest)=64),visible_state_digest TEXT NOT NULL CHECK(length(visible_state_digest)=64),outbox_digest TEXT NOT NULL CHECK(length(outbox_digest)=64),cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT;
CREATE TABLE main.sync_replica_outbox(destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),operation_id TEXT NOT NULL,enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),PRIMARY KEY(destination_device_id,operation_id),FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT;
CREATE INDEX main.sync_replica_outbox_operation ON sync_replica_outbox(operation_id,destination_device_id);
CREATE INDEX main.sync_replica_outbox_schedule ON sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id);
)PREVIOUS_V2");

    anonsync::SyncSqliteStmt meta_insert = anonsync::sqlite_prepare_or_throw(
        db.db,
        "INSERT INTO main.sync_replica_meta("
        "id,schema_version,folder_id,local_device_id,local_epoch_be,"
        "last_local_counter_be,state_generation_be,policy_generation_be,"
        "max_operations_be,max_context_entries_be,max_predecessor_ids_be,"
        "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
        "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
        "max_outbox_intents_be,max_outbox_destination_bytes_be,"
        "evidence_count_be,active_count_be,retained_canonical_bytes_be,"
        "retained_context_entries_be,retained_predecessor_ids_be,"
        "outbox_intent_count_be,outbox_destination_bytes_be,"
        "local_actor_compromised,local_operation_digest,operation_set_digest,"
        "evidence_set_digest,visible_state_digest,outbox_digest,cutpoint_digest) "
        "SELECT id,2,folder_id,local_device_id,local_epoch_be,"
        "last_local_counter_be,?,policy_generation_be,max_operations_be,"
        "max_context_entries_be,max_predecessor_ids_be,"
        "max_canonical_operation_bytes_be,max_retained_canonical_bytes_be,"
        "max_retained_context_entries_be,max_retained_predecessor_ids_be,"
        "max_outbox_intents_be,max_outbox_destination_bytes_be,"
        "evidence_count_be,active_count_be,retained_canonical_bytes_be,"
        "retained_context_entries_be,retained_predecessor_ids_be,"
        "outbox_intent_count_be,outbox_destination_bytes_be,"
        "local_actor_compromised,local_operation_digest,operation_set_digest,"
        "evidence_set_digest,visible_state_digest,?,? "
        "FROM temp.sync_replica_previous_meta WHERE id=1;",
        "previous v2 meta prepare");
    bind_test_u64_be(
        meta_insert.stmt, 1, meta.state_generation,
        "previous v2 bind state generation");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, 2, meta.outbox_digest,
        "previous v2 bind outbox digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_insert.stmt, 3, meta.cutpoint_digest,
        "previous v2 bind cutpoint digest");
    anonsync::sqlite_step_done_or_throw(
        meta_insert.stmt, "previous v2 meta insert");

    anonsync::SyncSqliteStmt outbox_insert =
        anonsync::sqlite_prepare_or_throw(
            db.db,
            "INSERT INTO main.sync_replica_outbox("
            "destination_device_id,operation_id,enqueued_generation_be,"
            "dispatch_attempts_be,claim_id,worker_id,claimed_at_epoch_be,"
            "lease_expires_at_epoch_be,retry_not_before_epoch_be)"
            "VALUES(?,?,?,?,?,?,?,?,?);",
            "previous v2 outbox prepare");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 1, intent.destination_device_id,
        "previous v2 bind destination");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 2, intent.operation_id,
        "previous v2 bind operation");
    bind_test_u64_be(
        outbox_insert.stmt, 3, intent.enqueued_generation,
        "previous v2 bind enqueued generation");
    bind_test_u64_be(
        outbox_insert.stmt, 4, intent.lease.dispatch_attempts,
        "previous v2 bind dispatch attempts");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 5, intent.lease.claim_id,
        "previous v2 bind claim id");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 6, intent.lease.worker_id,
        "previous v2 bind worker id");
    bind_test_u64_be(
        outbox_insert.stmt, 7, intent.lease.claimed_at_epoch,
        "previous v2 bind claimed at");
    bind_test_u64_be(
        outbox_insert.stmt, 8, intent.lease.lease_expires_at_epoch,
        "previous v2 bind lease expiry");
    bind_test_u64_be(
        outbox_insert.stmt, 9, intent.lease.retry_not_before_epoch,
        "previous v2 bind retry not before");
    anonsync::sqlite_step_done_or_throw(
        outbox_insert.stmt, "previous v2 outbox insert");
    exec(db, "DROP TABLE temp.sync_replica_previous_meta;");
    return {operation, intent, meta};
}

struct ClockV3Fixture final {
    SyncReplicaOperation operation;
    anonsync::SyncReplicaSqliteOutboxIntent intent;
    LegacyV1Meta meta;
    std::uint64_t outbox_time_high_water_epoch = 0U;
};

ClockV3Fixture create_clock_v3_released_fixture(
    SyncSqliteDb& db,
    const std::string& folder,
    const SyncReplicaActor& local,
    const SyncReplicaSqliteOwnerLimits& fixture_limits,
    const std::string& destination) {
    PreviousV2Fixture prior = create_previous_v2_fixture(
        db, folder, local, fixture_limits, destination);

    anonsync::SyncReplicaSqliteOutboxIntent released = prior.intent;
    released.lease.claim_id.clear();
    released.lease.worker_id.clear();
    released.lease.claimed_at_epoch = 0U;
    released.lease.lease_expires_at_epoch = 0U;
    released.lease.retry_not_before_epoch = 130U;
    released.lease.retry_released_at_epoch = 0U;
    released.lease.retry_release_provenance =
        anonsync::SyncReplicaOutboxRetryReleaseProvenance::LegacyUnproven;

    prior.meta.state_generation = 4U;
    prior.meta.outbox_digest = previous_v2_outbox_digest(folder, {released});
    prior.meta.cutpoint_digest = clock_v3_cutpoint_digest(prior.meta);
    constexpr std::uint64_t kHighWaterEpoch = 105U;
    const std::string clock_digest = test_outbox_clock_digest(
        folder, local, kHighWaterEpoch);

    const std::string v2_meta_sql = scalar_text_query(
        db,
        "SELECT sql FROM main.sqlite_schema "
        "WHERE type='table' AND name='sync_replica_meta';",
        "clock-v3 source meta SQL");
    std::string v3_meta_sql = v2_meta_sql;
    const std::string old_check = "schema_version=2";
    const std::string new_check = "schema_version=3";
    const std::size_t check_at = v3_meta_sql.find(old_check);
    if (check_at == std::string::npos ||
        v3_meta_sql.find(old_check, check_at + old_check.size()) !=
            std::string::npos) {
        fail("clock-v3 fixture could not identify one schema-version check");
    }
    v3_meta_sql.replace(check_at, old_check.size(), new_check);

    anonsync::SyncSqliteStmt outbox_update =
        anonsync::sqlite_prepare_or_throw(
            db.db,
            "UPDATE main.sync_replica_outbox SET "
            "dispatch_attempts_be=?,claim_id='',worker_id='',"
            "claimed_at_epoch_be=zeroblob(8),"
            "lease_expires_at_epoch_be=zeroblob(8),"
            "retry_not_before_epoch_be=? "
            "WHERE destination_device_id=? AND operation_id=?;",
            "clock-v3 released outbox prepare");
    bind_test_u64_be(
        outbox_update.stmt, 1, released.lease.dispatch_attempts,
        "clock-v3 bind dispatch attempts");
    bind_test_u64_be(
        outbox_update.stmt, 2, released.lease.retry_not_before_epoch,
        "clock-v3 bind retry deadline");
    anonsync::sqlite_bind_text_or_throw(
        outbox_update.stmt, 3, released.destination_device_id,
        "clock-v3 bind destination");
    anonsync::sqlite_bind_text_or_throw(
        outbox_update.stmt, 4, released.operation_id,
        "clock-v3 bind operation");
    anonsync::sqlite_step_done_or_throw(
        outbox_update.stmt, "clock-v3 released outbox update");

    anonsync::SyncSqliteStmt meta_update = anonsync::sqlite_prepare_or_throw(
        db.db,
        "UPDATE main.sync_replica_meta SET state_generation_be=?,"
        "outbox_digest=?,cutpoint_digest=? WHERE id=1;",
        "clock-v3 meta prepare");
    bind_test_u64_be(
        meta_update.stmt, 1, prior.meta.state_generation,
        "clock-v3 bind state generation");
    anonsync::sqlite_bind_text_or_throw(
        meta_update.stmt, 2, prior.meta.outbox_digest,
        "clock-v3 bind outbox digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_update.stmt, 3, prior.meta.cutpoint_digest,
        "clock-v3 bind cutpoint digest");
    anonsync::sqlite_step_done_or_throw(
        meta_update.stmt, "clock-v3 meta update");

    exec(db,
         "CREATE TEMP TABLE sync_replica_clock_v3_meta AS "
         "SELECT * FROM main.sync_replica_meta WHERE id=1;"
         "UPDATE temp.sync_replica_clock_v3_meta SET schema_version=3;"
         "DROP TABLE main.sync_replica_meta;");
    exec(db, v3_meta_sql + ";");
    exec(db,
         "INSERT INTO main.sync_replica_meta "
         "SELECT * FROM temp.sync_replica_clock_v3_meta;"
         "DROP TABLE temp.sync_replica_clock_v3_meta;"
         "CREATE TABLE main.sync_replica_outbox_clock("
         "id INTEGER PRIMARY KEY CHECK(id=1),"
         "high_water_epoch_be BLOB NOT NULL CHECK(length(high_water_epoch_be)=8),"
         "clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)) STRICT;");
    anonsync::SyncSqliteStmt clock_insert = anonsync::sqlite_prepare_or_throw(
        db.db,
        "INSERT INTO main.sync_replica_outbox_clock("
        "id,high_water_epoch_be,clock_digest) VALUES(1,?,?);",
        "clock-v3 clock prepare");
    bind_test_u64_be(
        clock_insert.stmt, 1, kHighWaterEpoch,
        "clock-v3 bind high water");
    anonsync::sqlite_bind_text_or_throw(
        clock_insert.stmt, 2, clock_digest,
        "clock-v3 bind clock digest");
    anonsync::sqlite_step_done_or_throw(
        clock_insert.stmt, "clock-v3 clock insert");

    return {prior.operation, released, prior.meta, kHighWaterEpoch};
}

struct RetryV4Fixture final {
    SyncReplicaOperation operation;
    anonsync::SyncReplicaSqliteOutboxIntent intent;
    LegacyV1Meta meta;
    std::uint64_t outbox_time_high_water_epoch = 0U;
};

RetryV4Fixture create_retry_v4_released_fixture(
    SyncSqliteDb& db,
    const std::string& folder,
    const SyncReplicaActor& local,
    const SyncReplicaSqliteOwnerLimits& fixture_limits,
    const std::string& destination) {
    ClockV3Fixture prior = create_clock_v3_released_fixture(
        db, folder, local, fixture_limits, destination);

    anonsync::SyncReplicaSqliteOutboxIntent exact = prior.intent;
    exact.lease.retry_released_at_epoch = prior.outbox_time_high_water_epoch;
    exact.lease.retry_release_provenance =
        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact;
    prior.meta.state_generation = 5U;
    prior.meta.outbox_digest = retry_v4_outbox_digest(folder, {exact});
    prior.meta.cutpoint_digest = retry_v4_cutpoint_digest(prior.meta);

    const std::string v3_meta_sql = scalar_text_query(
        db,
        "SELECT sql FROM main.sqlite_schema "
        "WHERE type='table' AND name='sync_replica_meta';",
        "retry-v4 source meta SQL");
    std::string v4_meta_sql = v3_meta_sql;
    const std::string old_check = "schema_version=3";
    const std::string new_check = "schema_version=4";
    const std::size_t check_at = v4_meta_sql.find(old_check);
    if (check_at == std::string::npos ||
        v4_meta_sql.find(old_check, check_at + old_check.size()) !=
            std::string::npos) {
        fail("retry-v4 fixture could not identify one schema-version check");
    }
    v4_meta_sql.replace(check_at, old_check.size(), new_check);

    exec(db, "BEGIN IMMEDIATE;");
    anonsync::SyncSqliteStmt meta_update = anonsync::sqlite_prepare_or_throw(
        db.db,
        "UPDATE main.sync_replica_meta SET state_generation_be=?,"
        "outbox_digest=?,cutpoint_digest=? WHERE id=1;",
        "retry-v4 meta prepare");
    bind_test_u64_be(
        meta_update.stmt, 1, prior.meta.state_generation,
        "retry-v4 bind state generation");
    anonsync::sqlite_bind_text_or_throw(
        meta_update.stmt, 2, prior.meta.outbox_digest,
        "retry-v4 bind outbox digest");
    anonsync::sqlite_bind_text_or_throw(
        meta_update.stmt, 3, prior.meta.cutpoint_digest,
        "retry-v4 bind cutpoint digest");
    anonsync::sqlite_step_done_or_throw(
        meta_update.stmt, "retry-v4 meta update");

    exec(db,
         "CREATE TEMP TABLE sync_replica_retry_v4_meta AS "
         "SELECT * FROM main.sync_replica_meta WHERE id=1;"
         "UPDATE temp.sync_replica_retry_v4_meta SET schema_version=4;"
         "DROP INDEX main.sync_replica_outbox_schedule;"
         "DROP INDEX main.sync_replica_outbox_operation;"
         "DROP TABLE main.sync_replica_outbox;"
         "DROP TABLE main.sync_replica_meta;");
    exec(db, v4_meta_sql + ";");
    exec(db,
         "INSERT INTO main.sync_replica_meta "
         "SELECT * FROM temp.sync_replica_retry_v4_meta;"
         "DROP TABLE temp.sync_replica_retry_v4_meta;"
         "CREATE TABLE main.sync_replica_outbox("
         "destination_device_id TEXT NOT NULL CHECK(length(destination_device_id) BETWEEN 1 AND 128),"
         "operation_id TEXT NOT NULL,"
         "enqueued_generation_be BLOB NOT NULL CHECK(length(enqueued_generation_be)=8),"
         "dispatch_attempts_be BLOB NOT NULL CHECK(length(dispatch_attempts_be)=8),"
         "claim_id TEXT NOT NULL CHECK(length(claim_id) IN (0,64)),"
         "worker_id TEXT NOT NULL CHECK(length(worker_id) BETWEEN 0 AND 128),"
         "claimed_at_epoch_be BLOB NOT NULL CHECK(length(claimed_at_epoch_be)=8),"
         "lease_expires_at_epoch_be BLOB NOT NULL CHECK(length(lease_expires_at_epoch_be)=8),"
         "retry_not_before_epoch_be BLOB NOT NULL CHECK(length(retry_not_before_epoch_be)=8),"
         "retry_released_at_epoch_be BLOB NOT NULL CHECK(length(retry_released_at_epoch_be)=8),"
         "retry_release_provenance INTEGER NOT NULL CHECK(retry_release_provenance BETWEEN 0 AND 2),"
         "PRIMARY KEY(destination_device_id,operation_id),"
         "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)) STRICT;"
         "CREATE INDEX main.sync_replica_outbox_operation ON "
         "sync_replica_outbox(operation_id,destination_device_id);"
         "CREATE INDEX main.sync_replica_outbox_schedule ON "
         "sync_replica_outbox(retry_not_before_epoch_be,lease_expires_at_epoch_be,destination_device_id,operation_id);");

    anonsync::SyncSqliteStmt outbox_insert =
        anonsync::sqlite_prepare_or_throw(
            db.db,
            "INSERT INTO main.sync_replica_outbox("
            "destination_device_id,operation_id,enqueued_generation_be,"
            "dispatch_attempts_be,claim_id,worker_id,claimed_at_epoch_be,"
            "lease_expires_at_epoch_be,retry_not_before_epoch_be,"
            "retry_released_at_epoch_be,retry_release_provenance)"
            "VALUES(?,?,?,?,?,?,?,?,?,?,?);",
            "retry-v4 outbox prepare");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 1, exact.destination_device_id,
        "retry-v4 bind destination");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 2, exact.operation_id,
        "retry-v4 bind operation");
    bind_test_u64_be(
        outbox_insert.stmt, 3, exact.enqueued_generation,
        "retry-v4 bind enqueued generation");
    bind_test_u64_be(
        outbox_insert.stmt, 4, exact.lease.dispatch_attempts,
        "retry-v4 bind dispatch attempts");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 5, exact.lease.claim_id,
        "retry-v4 bind claim id");
    anonsync::sqlite_bind_text_or_throw(
        outbox_insert.stmt, 6, exact.lease.worker_id,
        "retry-v4 bind worker id");
    bind_test_u64_be(
        outbox_insert.stmt, 7, exact.lease.claimed_at_epoch,
        "retry-v4 bind claimed at");
    bind_test_u64_be(
        outbox_insert.stmt, 8, exact.lease.lease_expires_at_epoch,
        "retry-v4 bind lease expiry");
    bind_test_u64_be(
        outbox_insert.stmt, 9, exact.lease.retry_not_before_epoch,
        "retry-v4 bind retry deadline");
    bind_test_u64_be(
        outbox_insert.stmt, 10, exact.lease.retry_released_at_epoch,
        "retry-v4 bind retry release");
    anonsync::sqlite_bind_u64_or_throw(
        outbox_insert.stmt, 11,
        static_cast<std::uint64_t>(exact.lease.retry_release_provenance),
        "retry-v4 bind retry provenance");
    anonsync::sqlite_step_done_or_throw(
        outbox_insert.stmt, "retry-v4 outbox insert");
    exec(db, "COMMIT;");

    return {prior.operation, exact, prior.meta,
            prior.outbox_time_high_water_epoch};
}


void test_exact_v1_migration_preserves_evidence_and_outbox() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-v1-migration");
    const std::string folder = "folder-sqlite-v1-migration";
    const SyncReplicaActor local = actor("device-sqlite-v1-migration", 901U);
    const std::string destination = "device-sqlite-v1-peer";
    const SyncReplicaSqliteOwnerLimits fixture_limits = limits(16U, 8U, 256U);
    SyncReplicaOperation operation;

    {
        SyncSqliteDb db = open_database(file.path);
        operation = create_legacy_v1_fixture(
            db, folder, local, fixture_limits, destination);
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "legacy schema version") == 1U &&
                    scalar_count(db, "sync_replica_operations") == 1U &&
                    scalar_count(db, "sync_replica_outbox") == 1U,
                "legacy fixture did not expose one exact rev0869 cutpoint");
    }

    SyncReplicaSqliteSnapshot claimed;
    {
        SyncSqliteDb db = open_database(file.path);
        // Migration must retain the durable v1 policy rather than replacing it
        // with the caller's initialization defaults.
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(999U, 999U, 9999U),
            "exact v1 migration owner");
        const SyncReplicaSqliteSnapshot migrated = owner.snapshot_or_throw();
        require(migrated.state_generation == 3U &&
                    migrated.policy_generation == 1U &&
                    migrated.limits == fixture_limits &&
                    migrated.durable.last_local_counter == 1U &&
                    migrated.durable.operations ==
                        std::vector<SyncReplicaOperation>{operation} &&
                    migrated.durable.local_operation_ids ==
                        std::vector<std::string>{operation.operation_id},
                "v1 migration changed canonical evidence, mint authority, or policy");
        require(migrated.outbox ==
                    std::vector<anonsync::SyncReplicaSqliteOutboxIntent>{{
                        destination, operation.operation_id, 2U, {}}},
                "v1 migration did not preserve the unsettled intent with an empty lease");
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "migrated schema version") == 5U &&
                    scalar_u64_query(
                        db,
                        "SELECT count(*) FROM main.sqlite_schema "
                        "WHERE type='index' AND name='sync_replica_outbox_schedule';",
                        "migrated schedule index count") == 1U &&
                    scalar_count(db, "sync_replica_outbox_clock") == 1U &&
                    migrated.outbox_time_high_water_epoch == 0U &&
                    anonsync::is_lowercase_sha256_hex(
                        migrated.outbox_clock_digest),
                "v1 migration did not publish the exact schema-v5 surface");

        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-v1-migration", 100U, 20U, destination);
        require(claim.has_value() && claim->operation == operation &&
                    claim->intent.enqueued_generation == 2U &&
                    claim->intent.lease.dispatch_attempts == 1U &&
                    claim->intent.lease.claimed_at_epoch == 100U &&
                    claim->intent.lease.lease_expires_at_epoch == 120U &&
                    anonsync::is_lowercase_sha256_hex(
                        claim->intent.lease.claim_id),
                "migrated v1 intent was not immediately claimable under v5 authority");
        claimed = owner.snapshot_or_throw();
        require(claimed.state_generation == 4U &&
                    claimed.outbox.size() == 1U &&
                    claimed.outbox_time_high_water_epoch == 100U &&
                    claimed.outbox.front() == claim->intent,
                "claim after migration did not publish one exact v5 lease cutpoint");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(1U), "v1 migration restart owner");
        require(owner.snapshot_or_throw() == claimed,
                "restart lost the exact receipt authority minted after migration");
        const auto& intent = claimed.outbox.front();
        require(owner.settle_outbox_or_throw(
                    destination, operation.operation_id,
                    intent.lease.claim_id, 110U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied &&
                    owner.snapshot_or_throw().outbox.empty(),
                "current migrated receipt did not settle after restart");
    }
}

void test_malformed_v1_is_not_laundered_into_v5() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-v1-malformed");
    const std::string folder = "folder-sqlite-v1-malformed";
    const SyncReplicaActor local = actor("device-sqlite-v1-malformed", 907U);
    SyncSqliteDb db = open_database(file.path);
    (void)create_legacy_v1_fixture(
        db, folder, local, limits(16U), "device-sqlite-v1-malformed-peer");
    exec(db,
         "UPDATE main.sync_replica_outbox SET enqueued_generation_be=zeroblob(8);");

    require_error(
        [&] {
            SyncReplicaSqliteOwner owner(
                db.db, folder, local, limits(16U),
                "malformed v1 migration owner");
        },
        "outbox intent is invalid",
        "malformed v1 evidence was accepted by migration");
    require(scalar_u64_query(
                db,
                "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                "failed migration schema version") == 1U &&
                scalar_u64_query(
                    db,
                    "SELECT count(*) FROM main.sqlite_schema "
                    "WHERE type='index' AND name='sync_replica_outbox_schedule';",
                    "failed migration schedule index count") == 0U,
            "failed v1 attestation partially published schema v5");
}


SyncReplicaOperation root_operation(
    const std::string& folder,
    const SyncReplicaActor& operation_actor,
    const std::string& path,
    const std::string& payload) {
    SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = path;
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = static_cast<std::uint64_t>(payload.size());
    operation.content_sha256 = anonsync::sha256_hex(payload);
    operation.dot = {operation_actor, 1U};
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

SyncReplicaOperation child_operation(
    const SyncReplicaOperation& parent,
    const SyncReplicaActor& child_actor,
    const std::string& payload) {
    SyncReplicaOperation operation;
    operation.folder_id = parent.folder_id;
    operation.canonical_path = parent.canonical_path;
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = static_cast<std::uint64_t>(payload.size());
    operation.content_sha256 = anonsync::sha256_hex(payload);
    operation.dot = {child_actor, 1U};
    operation.causal_context = {{parent.dot.actor, parent.dot.counter}};
    operation.predecessor_operation_ids = {parent.operation_id};
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

void test_exact_v2_migration_preserves_live_receipt_and_seeds_clock() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-v2-migration");
    const std::string folder = "folder-sqlite-v2-migration";
    const SyncReplicaActor local = actor("device-sqlite-v2-migration", 911U);
    const std::string destination = "device-sqlite-v2-peer";
    const SyncReplicaSqliteOwnerLimits fixture_limits = limits(16U, 8U, 256U);
    PreviousV2Fixture fixture;

    {
        SyncSqliteDb db = open_database(file.path);
        fixture = create_previous_v2_fixture(
            db, folder, local, fixture_limits, destination);
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "previous schema version") == 2U &&
                    scalar_count(db, "sync_replica_operations") == 1U &&
                    scalar_count(db, "sync_replica_outbox") == 1U &&
                    scalar_u64_query(
                        db,
                        "SELECT count(*) FROM main.sqlite_schema "
                        "WHERE type='table' AND "
                        "name='sync_replica_outbox_clock';",
                        "previous clock table count") == 0U,
                "previous fixture did not expose one exact rev0871 cutpoint");
    }

    SyncReplicaSqliteSnapshot migrated;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(999U, 999U, 9999U),
            "exact v2 migration owner");
        migrated = owner.snapshot_or_throw();
        require(migrated.state_generation == 4U &&
                    migrated.policy_generation == 1U &&
                    migrated.limits == fixture_limits &&
                    migrated.durable.operations ==
                        std::vector<SyncReplicaOperation>{fixture.operation} &&
                    migrated.outbox ==
                        std::vector<anonsync::SyncReplicaSqliteOutboxIntent>{
                            fixture.intent},
                "v2 migration changed evidence, policy, or live receipt authority");
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "v2 migrated schema version") == 5U &&
                    scalar_count(db, "sync_replica_outbox_clock") == 1U &&
                    migrated.outbox_time_high_water_epoch ==
                        fixture.intent.lease.claimed_at_epoch &&
                    anonsync::is_lowercase_sha256_hex(
                        migrated.outbox_clock_digest),
                "v2 migration did not seed one canonical conservative time fence");
        require(
            migrated.outbox_clock_state.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
                migrated.outbox_clock_state.anomaly ==
                    anonsync::SyncReplicaOutboxClockAnomaly::LegacyUnbound &&
                !migrated.outbox_clock_state.accepted.has_value(),
            "v2 migration must not relabel a caller epoch as trusted host time");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(1U), "v2 migration restart owner");
        require(owner.snapshot_or_throw() == migrated,
                "restart lost exact v2 receipt authority after v5 migration");
        const auto recovered = owner.recover_outbox_clock_or_throw(
            migrated.outbox_clock_state.observation_generation,
            migrated.outbox_time_high_water_epoch);
        require(
            recovered.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Healthy &&
                recovered.recovery_generation == 1U &&
                recovered.high_water_epoch ==
                    migrated.outbox_time_high_water_epoch,
            "explicit recovery did not bind migrated v2 time to the owned clock");
        require(owner.settle_outbox_or_throw(
                    destination, fixture.operation.operation_id,
                    fixture.intent.lease.claim_id, 110U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "live receipt imported from v2 could not settle after restart");
        const SyncReplicaSqliteSnapshot settled = owner.snapshot_or_throw();
        require(settled.state_generation == migrated.state_generation + 1U &&
                    settled.outbox.empty() &&
                    settled.outbox_time_high_water_epoch == 110U,
                "v2 receipt settlement did not publish one exact v5 cutpoint");
    }
}

void test_unreachable_v2_lease_is_not_laundered_into_v5() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-v2-unreachable");
    const std::string folder = "folder-sqlite-v2-unreachable";
    const SyncReplicaActor local = actor("device-sqlite-v2-unreachable", 919U);
    SyncSqliteDb db = open_database(file.path);
    (void)create_previous_v2_fixture(
        db, folder, local, limits(16U),
        "device-sqlite-v2-unreachable-peer");
    exec(db,
         "UPDATE main.sync_replica_outbox SET "
         "claim_id='',worker_id='',claimed_at_epoch_be=zeroblob(8),"
         "lease_expires_at_epoch_be=zeroblob(8),"
         "retry_not_before_epoch_be=zeroblob(8);");

    require_error(
        [&] {
            SyncReplicaSqliteOwner owner(
                db.db, folder, local, limits(16U),
                "unreachable v2 migration owner");
        },
        "without active or retry authority",
        "unreachable v2 lease state was laundered into schema v5");
    require(scalar_u64_query(
                db,
                "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                "failed v2 migration schema version") == 2U &&
                scalar_u64_query(
                    db,
                    "SELECT count(*) FROM main.sqlite_schema "
                    "WHERE type='table' AND name='sync_replica_outbox_clock';",
                    "failed v2 migration clock table count") == 0U,
            "failed v2 attestation partially published schema v5");
}

void test_exact_v3_migration_preserves_clock_and_marks_retry_gap() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-v3-migration");
    const std::string folder = "folder-sqlite-v3-migration";
    const SyncReplicaActor local = actor("device-sqlite-v3-migration", 929U);
    const std::string destination = "device-sqlite-v3-peer";
    const SyncReplicaSqliteOwnerLimits fixture_limits = limits(16U, 8U, 256U);
    ClockV3Fixture fixture;

    {
        SyncSqliteDb db = open_database(file.path);
        fixture = create_clock_v3_released_fixture(
            db, folder, local, fixture_limits, destination);
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "clock-v3 schema version") == 3U &&
                    scalar_count(db, "sync_replica_outbox_clock") == 1U &&
                    scalar_u64_query(
                        db,
                        "SELECT count(*) FROM pragma_table_info("
                        "'sync_replica_outbox') WHERE name IN ("
                        "'retry_released_at_epoch_be',"
                        "'retry_release_provenance');",
                        "clock-v3 provenance column count") == 0U,
                "clock-v3 fixture was not the exact rev0872 protocol surface");
    }

    SyncReplicaSqliteSnapshot migrated;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(999U, 999U, 9999U),
            "exact v3 migration owner");
        migrated = owner.snapshot_or_throw();
        require(migrated.state_generation ==
                        fixture.meta.state_generation + 1U &&
                    migrated.policy_generation == fixture.meta.policy_generation &&
                    migrated.limits == fixture_limits &&
                    migrated.durable.operations ==
                        std::vector<SyncReplicaOperation>{fixture.operation} &&
                    migrated.outbox ==
                        std::vector<anonsync::SyncReplicaSqliteOutboxIntent>{
                            fixture.intent},
                "v3 migration changed evidence, policy, or retry authority");
        require(migrated.outbox_time_high_water_epoch ==
                        fixture.outbox_time_high_water_epoch &&
                    migrated.outbox.front().lease.retry_released_at_epoch == 0U &&
                    migrated.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::
                            LegacyUnproven,
                "v3 migration fabricated or discarded retry-release knowledge");
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "v3 migrated schema version") == 5U &&
                    scalar_u64_query(
                        db,
                        "SELECT retry_release_provenance "
                        "FROM main.sync_replica_outbox;",
                        "v3 migrated retry provenance") == 2U &&
                    scalar_u64_query(
                        db,
                        "SELECT count(*) FROM pragma_table_info("
                        "'sync_replica_outbox') WHERE name IN ("
                        "'retry_released_at_epoch_be',"
                        "'retry_release_provenance');",
                        "v3 migrated provenance column count") == 2U,
                "v3 migration did not publish the exact schema-v5 surface");
    }

    SyncReplicaSqliteSnapshot exact_release;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(1U), "v3 migration restart owner");
        require(owner.snapshot_or_throw() == migrated,
                "restart changed the explicit legacy-unproven retry row");
        require(
            migrated.outbox_clock_state.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
                migrated.outbox_clock_state.anomaly ==
                    anonsync::SyncReplicaOutboxClockAnomaly::LegacyUnbound &&
                !migrated.outbox_clock_state.accepted.has_value(),
            "v3 migration must quarantine its caller-supplied legacy epoch");
        const auto recovered = owner.recover_outbox_clock_or_throw(
            migrated.outbox_clock_state.observation_generation,
            migrated.outbox_time_high_water_epoch);
        require(
            recovered.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Healthy &&
                recovered.recovery_generation == 1U &&
                recovered.high_water_epoch ==
                    migrated.outbox_time_high_water_epoch,
            "explicit recovery did not bind migrated v3 retry time to the owned clock");
        require(owner.snapshot_or_throw().outbox_clock_state == recovered,
                "v3 recovered clock state was not durably published");
        require(!owner.claim_next_outbox_or_throw(
                     "worker-v3-before-deadline", 129U, 10U, destination)
                     .has_value(),
                "legacy-unproven retry deadline was bypassed");
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-v3-at-deadline", 130U, 10U, destination);
        require(claim.has_value() &&
                    claim->intent.lease.dispatch_attempts == 2U &&
                    claim->intent.lease.retry_not_before_epoch == 0U &&
                    claim->intent.lease.retry_released_at_epoch == 0U &&
                    claim->intent.lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::None,
                "new claim did not clear inherited legacy retry provenance");
        require(owner.release_outbox_for_retry_or_throw(
                    destination, fixture.operation.operation_id,
                    claim->intent.lease.claim_id, 135U, 7U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "post-migration release did not mint exact retry provenance");
        exact_release = owner.snapshot_or_throw();
        require(exact_release.outbox.size() == 1U &&
                    exact_release.outbox.front().lease.retry_not_before_epoch ==
                        142U &&
                    exact_release.outbox.front().lease.retry_released_at_epoch ==
                        135U &&
                    exact_release.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
                "post-migration release did not bind deadline to its observation");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(1U),
            "v3 migration exact provenance restart owner");
        require(owner.snapshot_or_throw() == exact_release,
                "restart lost exact post-migration retry provenance");
    }
}

void test_exact_v4_migration_preserves_retry_provenance_and_quarantines_clock() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-v4-migration");
    const std::string folder = "folder-sqlite-v4-migration";
    const SyncReplicaActor local = actor("device-sqlite-v4-migration", 939U);
    const std::string destination = "device-sqlite-v4-peer";
    const SyncReplicaSqliteOwnerLimits fixture_limits = limits(16U, 8U, 256U);
    RetryV4Fixture fixture;

    {
        SyncSqliteDb db = open_database(file.path);
        fixture = create_retry_v4_released_fixture(
            db, folder, local, fixture_limits, destination);
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "retry-v4 schema version") == 4U &&
                    scalar_count(db, "sync_replica_outbox_clock") == 1U &&
                    scalar_u64_query(
                        db,
                        "SELECT count(*) FROM pragma_table_info("
                        "'sync_replica_outbox') WHERE name IN ("
                        "'retry_released_at_epoch_be',"
                        "'retry_release_provenance');",
                        "retry-v4 provenance column count") == 2U &&
                    scalar_u64_query(
                        db,
                        "SELECT retry_release_provenance "
                        "FROM main.sync_replica_outbox;",
                        "retry-v4 exact provenance") == 1U,
                "retry-v4 fixture was not the exact rev0873 protocol surface");
    }

    SyncReplicaSqliteSnapshot migrated;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(999U, 999U, 9999U),
            "exact v4 migration owner");
        migrated = owner.snapshot_or_throw();
        require(migrated.state_generation ==
                        fixture.meta.state_generation + 1U &&
                    migrated.policy_generation == fixture.meta.policy_generation &&
                    migrated.limits == fixture_limits &&
                    migrated.durable.operations ==
                        std::vector<SyncReplicaOperation>{fixture.operation} &&
                    migrated.outbox ==
                        std::vector<anonsync::SyncReplicaSqliteOutboxIntent>{
                            fixture.intent},
                "v4 migration changed evidence, policy, or exact retry authority");
        require(migrated.outbox_time_high_water_epoch ==
                        fixture.outbox_time_high_water_epoch &&
                    migrated.outbox.front().lease.retry_not_before_epoch ==
                        130U &&
                    migrated.outbox.front().lease.retry_released_at_epoch ==
                        fixture.outbox_time_high_water_epoch &&
                    migrated.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
                "v4 migration discarded exact retry-release provenance");
        require(migrated.outbox_clock_state.health ==
                        anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
                    migrated.outbox_clock_state.anomaly ==
                        anonsync::SyncReplicaOutboxClockAnomaly::LegacyUnbound &&
                    !migrated.outbox_clock_state.accepted.has_value() &&
                    migrated.outbox_clock_state.high_water_epoch ==
                        fixture.outbox_time_high_water_epoch,
                "v4 migration trusted an unbound legacy clock observation");
        require(scalar_u64_query(
                    db,
                    "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                    "v4 migrated schema version") == 5U &&
                    scalar_u64_query(
                        db,
                        "SELECT count(*) FROM pragma_table_info("
                        "'sync_replica_outbox_clock') "
                        "WHERE name='clock_state_bytes';",
                        "v4 migrated clock state column count") == 1U &&
                    scalar_u64_query(
                        db,
                        "SELECT retry_release_provenance "
                        "FROM main.sync_replica_outbox;",
                        "v4 migrated retry provenance") == 1U,
                "v4 migration did not publish the exact schema-v5 surface");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(1U), "v4 migration restart owner");
        require(owner.snapshot_or_throw() == migrated,
                "restart changed migrated v4 retry or clock evidence");
        require_error(
            [&] {
                (void)owner.claim_next_outbox_or_throw(
                    "worker-v4-before-recovery", 130U, 10U, destination);
            },
            "clock is quarantined",
            "migrated v4 caller-time clock minted authority before recovery");
        const SyncReplicaSqliteSnapshot still_quarantined =
            owner.snapshot_or_throw();
        require(still_quarantined == migrated,
                "sticky legacy quarantine was overwritten by a later observation");
        const auto recovered = owner.recover_outbox_clock_or_throw(
            still_quarantined.outbox_clock_state.observation_generation,
            fixture.outbox_time_high_water_epoch);
        require(recovered.health ==
                        anonsync::SyncReplicaOutboxClockHealth::Healthy &&
                    recovered.recovery_generation == 1U &&
                    recovered.high_water_epoch ==
                        fixture.outbox_time_high_water_epoch &&
                    recovered.anchor.has_value() &&
                    recovered.accepted.has_value(),
                "explicit recovery did not bind migrated v4 time to an observation");
        require(!owner.claim_next_outbox_or_throw(
                     "worker-v4-before-deadline", 129U, 10U, destination)
                     .has_value(),
                "exact v4 retry deadline was bypassed after migration");
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-v4-at-deadline", 130U, 10U, destination);
        require(claim.has_value() &&
                    claim->intent.lease.dispatch_attempts == 2U &&
                    claim->intent.lease.retry_not_before_epoch == 0U &&
                    claim->intent.lease.retry_released_at_epoch == 0U &&
                    claim->intent.lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::None,
                "v4 deadline claim did not consume exact retry provenance");
    }
}

void test_malformed_v4_provenance_is_not_laundered_into_v5() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-v4-malformed");
    const std::string folder = "folder-sqlite-v4-malformed";
    const SyncReplicaActor local = actor("device-sqlite-v4-malformed", 949U);
    SyncSqliteDb db = open_database(file.path);
    (void)create_retry_v4_released_fixture(
        db, folder, local, limits(16U), "device-sqlite-v4-malformed-peer");
    exec(db,
         "UPDATE main.sync_replica_outbox SET "
         "retry_released_at_epoch_be=zeroblob(8),"
         "retry_release_provenance=2;");

    require_error(
        [&] {
            SyncReplicaSqliteOwner owner(
                db.db, folder, local, limits(16U),
                "malformed v4 migration owner");
        },
        "outbox attestation mismatch",
        "tampered v4 retry provenance was laundered into schema v5");
    require(scalar_u64_query(
                db,
                "SELECT schema_version FROM main.sync_replica_meta WHERE id=1;",
                "failed v4 migration schema version") == 4U &&
                scalar_u64_query(
                    db,
                    "SELECT count(*) FROM pragma_table_info("
                    "'sync_replica_outbox_clock') "
                    "WHERE name='high_water_epoch_be';",
                    "failed v4 migration clock column count") == 1U,
            "failed v4 attestation partially published schema v5");
}


void test_atomic_local_publication_and_single_copy_outbox() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-local");
    const std::string folder = "folder-sqlite-local";
    const SyncReplicaActor local = actor("device-sqlite-local", 1001U);
    SyncReplicaSqliteSnapshot settled;
    SyncReplicaOperation operation;

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "local publication owner");
        const SyncReplicaSqliteSnapshot empty = owner.snapshot_or_throw();
        require(empty.state_generation == 1U &&
                    empty.policy_generation == 1U &&
                    empty.durable.operations.empty() && empty.outbox.empty(),
                "fresh SQLite owner did not publish its exact empty generation");

        const std::vector<std::string> destinations{
            "device-sqlite-peer-b", "device-sqlite-peer-c"};
        operation = owner.create_local_file_or_throw(
            "docs/report.bin", 7U, anonsync::sha256_hex("payload"),
            destinations);
        const SyncReplicaSqliteSnapshot committed = owner.snapshot_or_throw();
        require(committed.state_generation == 2U &&
                    committed.policy_generation == 1U &&
                    committed.durable.last_local_counter == 1U &&
                    committed.durable.operations.size() == 1U &&
                    committed.outbox.size() == 2U,
                "local publication did not atomically advance evidence, counter, and fanout");
        require(committed.outbox[0].operation_id == operation.operation_id &&
                    committed.outbox[1].operation_id == operation.operation_id &&
                    committed.outbox[0].enqueued_generation == 2U &&
                    committed.outbox[1].enqueued_generation == 2U &&
                    committed.outbox[0].lease ==
                        anonsync::SyncReplicaOutboxLeaseState{} &&
                    committed.outbox[1].lease ==
                        anonsync::SyncReplicaOutboxLeaseState{},
                "fanout intents did not bind one operation and start unsettled");
        require(scalar_count(db, "sync_replica_operations") == 1U &&
                    scalar_count(db, "sync_replica_outbox") == 2U,
                "fanout cloned canonical operation rows instead of lightweight intents");

        const auto claim_b = owner.claim_next_outbox_or_throw(
            "worker-local-b", 100U, 10U, "device-sqlite-peer-b");
        require(claim_b.has_value() && claim_b->operation == operation &&
                    claim_b->intent.destination_device_id ==
                        "device-sqlite-peer-b" &&
                    claim_b->intent.lease.dispatch_attempts == 1U &&
                    anonsync::is_lowercase_sha256_hex(
                        claim_b->intent.lease.claim_id),
                "outbox claim did not resolve one intent through its canonical owner");
        const SyncReplicaSqliteSnapshot claimed = owner.snapshot_or_throw();
        require(claimed.state_generation == 3U &&
                    claimed.durable == committed.durable &&
                    claimed.outbox.size() == 2U,
                "claim did not atomically publish lease authority only");

        exec(db,
             "CREATE TEMP TABLE sync_replica_meta(id INTEGER,folder_id TEXT);"
             "INSERT INTO temp.sync_replica_meta VALUES(1,'attacker-folder');"
             "CREATE TEMP TABLE sync_replica_operations(operation_id TEXT);"
             "INSERT INTO temp.sync_replica_operations VALUES('attacker');"
             "CREATE TEMP TABLE sync_replica_outbox(destination_device_id TEXT);"
             "INSERT INTO temp.sync_replica_outbox VALUES('attacker');");
        require(owner.snapshot_or_throw() == claimed,
                "TEMP shadows redirected main-bound durable replica reads");

        require(owner.settle_outbox_or_throw(
                    "device-sqlite-peer-b", operation.operation_id,
                    claim_b->intent.lease.claim_id, 105U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "exact current receipt did not settle its intent");
        settled = owner.snapshot_or_throw();
        require(settled.state_generation == 4U &&
                    settled.durable == committed.durable &&
                    settled.outbox.size() == 1U &&
                    settled.outbox.front().destination_device_id ==
                        "device-sqlite-peer-c",
                "settlement changed evidence or retired the wrong destination");
        require(owner.settle_outbox_or_throw(
                    "device-sqlite-peer-b", operation.operation_id,
                    claim_b->intent.lease.claim_id, 105U) ==
                    SyncReplicaSqliteOutboxReceiptResult::IntentMissing &&
                    owner.snapshot_or_throw() == settled,
                "missing-intent settlement advanced durable generation");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        // Existing durable policy is authoritative; this argument is only the
        // initialization policy for a database with no replica schema.
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(999U), "local restart owner");
        require(owner.snapshot_or_throw() == settled,
                "restart did not restore the exact settled cutpoint");
        const auto remaining = owner.claim_next_outbox_or_throw(
            "worker-local-c", 106U, 10U, "device-sqlite-peer-c");
        require(remaining.has_value() && remaining->operation == operation,
                "restart lost the canonical payload behind an unsettled intent");
    }
}

void test_delivery_payload_inventory_validation_precedes_claim_authority() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-payload-inventory");
    const std::string folder = "folder-sqlite-payload-inventory";
    const SyncReplicaActor local =
        actor("device-sqlite-payload-inventory", 1021U);
    const std::string destination = "device-sqlite-payload-inventory-peer";
    const std::string payload = "payload-inventory-authority";
    const auto owner_policy = limits(16U);

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, owner_policy, "payload inventory owner");
    const SyncReplicaOperation operation = owner.create_local_file_or_throw(
        "payload/inventory.bin", payload.size(), anonsync::sha256_hex(payload),
        std::vector<std::string>{destination});
    const SyncReplicaSqliteSnapshot before = owner.snapshot_or_throw();

    require_error(
        [&] {
            (void)anonsync::SyncReplicaFileContentInventory(
                folder, {"not-a-content-digest"},
                "malformed payload inventory");
        },
        "contains an invalid content digest",
        "malformed payload inventory became immutable authority");
    require(owner.snapshot_or_throw() == before,
            "malformed payload inventory sampled time or changed durable authority");

    const std::string digest_a = anonsync::sha256_hex("inventory-a");
    require_error(
        [&] {
            (void)anonsync::SyncReplicaFileContentInventory(
                folder, {digest_a, digest_a},
                "duplicate payload inventory");
        },
        "contains duplicate content authority",
        "duplicate payload inventory became immutable authority");
    require(owner.snapshot_or_throw() == before,
            "duplicate payload inventory sampled time or changed durable authority");

    require_error(
        [&] {
            (void)anonsync::SyncReplicaFileContentInventory(
                folder,
                std::vector<std::string>(
                    static_cast<std::size_t>(
                        anonsync::kSyncReplicaFileContentInventoryMaxEntries + 1U),
                    digest_a),
                "oversized payload inventory");
        },
        "entry count exceeds its hard ceiling",
        "oversized payload inventory became immutable authority");
    require(owner.snapshot_or_throw() == before,
            "oversized payload inventory sampled time or changed durable authority");

    std::vector<std::string> caller_digests{
        anonsync::sha256_hex("unavailable-content"),
        operation.content_sha256};
    anonsync::SyncReplicaFileContentInventory inventory(
        folder, caller_digests, "owned payload inventory");
    caller_digests[0].assign(64U, 'f');
    caller_digests[1].assign(64U, '0');
    const auto retained = inventory.content_sha256s();
    require(retained.size() == 2U &&
                std::is_sorted(retained.begin(), retained.end()) &&
                std::binary_search(
                    retained.begin(), retained.end(), operation.content_sha256),
            "payload inventory borrowed or failed to canonicalize caller storage");

    anonsync::SyncReplicaFileContentInventory wrong_folder_inventory(
        "folder-sqlite-payload-inventory-wrong",
        {operation.content_sha256}, "wrong-folder payload inventory");
    require_error(
        [&] {
            (void)owner.claim_next_outbox_for_delivery_or_throw(
                "worker-payload-inventory-folder", 100U, 10U,
                owner_policy.model, destination,
                anonsync::SyncReplicaValueKind::File, 1024U,
                wrong_folder_inventory);
        },
        "does not match owner folder identity",
        "cross-folder payload inventory reached claim authority");
    require(owner.snapshot_or_throw() == before,
            "cross-folder payload inventory sampled time or changed durable authority");

    anonsync::SyncReplicaFileContentInventory moved_inventory(
        folder, {operation.content_sha256}, "movable payload inventory");
    anonsync::SyncReplicaFileContentInventory retained_inventory =
        std::move(moved_inventory);
    require_error(
        [&] {
            (void)owner.claim_next_outbox_for_delivery_or_throw(
                "worker-payload-inventory-inactive", 100U, 10U,
                owner_policy.model, destination,
                anonsync::SyncReplicaValueKind::File, 1024U,
                moved_inventory);
        },
        "file content inventory is inactive",
        "moved-from payload inventory reached claim authority");
    require(owner.snapshot_or_throw() == before,
            "inactive payload inventory sampled time or changed durable authority");

    require_error(
        [&] {
            (void)owner.claim_next_outbox_for_delivery_or_throw(
                "worker-payload-inventory-kind", 100U, 10U,
                owner_policy.model, destination, std::nullopt, std::nullopt,
                retained_inventory);
        },
        "payload inventory requires File operation kind",
        "payload inventory was accepted without file-only claim scope");
    require(owner.snapshot_or_throw() == before,
            "mis-scoped payload inventory sampled time or changed durable authority");

    const auto claim = owner.claim_next_outbox_for_delivery_or_throw(
        "worker-payload-inventory-valid", 100U, 10U,
        owner_policy.model, destination,
        anonsync::SyncReplicaValueKind::File, 1024U,
        inventory);
    require(claim.has_value() && claim->operation == operation &&
                claim->intent.lease.dispatch_attempts == 1U,
            "immutable payload inventory did not authorize its exact operation");
}

void test_receipt_bound_reclaim_backoff_and_restart() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-receipts");
    const std::string folder = "folder-sqlite-receipts";
    const SyncReplicaActor local = actor("device-sqlite-receipts", 1051U);
    const std::string destination = "device-sqlite-receipts-peer";
    SyncReplicaOperation operation;
    SyncReplicaSqliteSnapshot renewed_snapshot;
    std::string first_claim_id;

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "receipt seed owner");
        operation = owner.create_local_file_or_throw(
            "receipts/file.bin", 8U, anonsync::sha256_hex("receipts"),
            std::vector<std::string>{destination});
        const auto first = owner.claim_next_outbox_or_throw(
            "worker-receipt-a", 100U, 10U, destination);
        require(first.has_value() &&
                    first->intent.lease.dispatch_attempts == 1U &&
                    first->intent.lease.claimed_at_epoch == 100U &&
                    first->intent.lease.lease_expires_at_epoch == 110U,
                "first durable dispatch attempt was not claimed exactly");
        first_claim_id = first->intent.lease.claim_id;
        const SyncReplicaSqliteSnapshot first_claim_snapshot =
            owner.snapshot_or_throw();
        require(first_claim_snapshot.outbox_time_high_water_epoch == 100U,
                "first claim did not publish its durable time observation");

        require(owner.renew_outbox_lease_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    105U, 10U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "exact live receipt did not renew its durable deadline");
        const SyncReplicaSqliteSnapshot extended_snapshot =
            owner.snapshot_or_throw();
        require(extended_snapshot.state_generation ==
                    first_claim_snapshot.state_generation + 1U &&
                    extended_snapshot.outbox_time_high_water_epoch == 105U &&
                    extended_snapshot.outbox.size() == 1U &&
                    extended_snapshot.outbox.front().lease.claim_id ==
                        first_claim_id &&
                    extended_snapshot.outbox.front().lease.worker_id ==
                        "worker-receipt-a" &&
                    extended_snapshot.outbox.front().lease.dispatch_attempts ==
                        1U &&
                    extended_snapshot.outbox.front().lease.claimed_at_epoch ==
                        100U &&
                    extended_snapshot.outbox.front().lease
                            .lease_expires_at_epoch == 115U,
                "heartbeat changed attempt identity or failed to extend the deadline");
        require(owner.renew_outbox_lease_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    106U, 5U) ==
                    SyncReplicaSqliteOutboxReceiptResult::LeaseAlreadyCovered,
                "covered heartbeat did not preserve its current lease");
        const SyncReplicaSqliteSnapshot covered_snapshot =
            owner.snapshot_or_throw();
        require(covered_snapshot.state_generation ==
                    extended_snapshot.state_generation &&
                    covered_snapshot.outbox == extended_snapshot.outbox &&
                    covered_snapshot.outbox_time_high_water_epoch == 106U &&
                    covered_snapshot.outbox_clock_digest !=
                        extended_snapshot.outbox_clock_digest,
                "covered heartbeat failed to publish only its clock observation");
        require_error(
            [&] {
                (void)owner.renew_outbox_lease_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    106U,
                    anonsync::kSyncReplicaOutboxMaxLeaseSeconds + 1U);
            },
            "1..86400",
            "owner accepted an overlong heartbeat duration");
        require(owner.snapshot_or_throw() == covered_snapshot,
                "invalid heartbeat changed the durable cutpoint");
        require_error(
            [&] {
                (void)owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    106U,
                    anonsync::kSyncReplicaOutboxMaxRetryDelaySeconds + 1U);
            },
            "fixed retry budget",
            "owner accepted an unbounded retry delay");
        require(owner.snapshot_or_throw() == covered_snapshot,
                "invalid retry release changed the durable cutpoint");
        require_error(
            [&] {
                (void)owner.settle_outbox_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    99U);
            },
            "boottime-rollback",
            "owner did not quarantine an observed host-clock rollback");
        const SyncReplicaSqliteSnapshot quarantined_snapshot =
            owner.snapshot_or_throw();
        require(
            quarantined_snapshot.state_generation ==
                    covered_snapshot.state_generation &&
                quarantined_snapshot.outbox == covered_snapshot.outbox &&
                quarantined_snapshot.outbox_time_high_water_epoch == 106U &&
                quarantined_snapshot.outbox_clock_state.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
                quarantined_snapshot.outbox_clock_state.anomaly ==
                    anonsync::SyncReplicaOutboxClockAnomaly::BoottimeRollback &&
                quarantined_snapshot.outbox_clock_digest !=
                    covered_snapshot.outbox_clock_digest,
            "clock rollback was not durably isolated from receipt authority");
        const auto recovered_clock = owner.recover_outbox_clock_or_throw(
            quarantined_snapshot.outbox_clock_state.observation_generation,
            106U);
        require(
            recovered_clock.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Healthy &&
                recovered_clock.high_water_epoch == 106U &&
                recovered_clock.recovery_generation == 1U,
            "explicit recovery did not restore clock authority after rollback");
        const SyncReplicaSqliteSnapshot recovered_snapshot =
            owner.snapshot_or_throw();
        require(!owner.claim_next_outbox_or_throw(
                     "worker-receipt-b", 114U, 10U, destination)
                     .has_value(),
                "renewed lease was stolen before its exact deadline");
        renewed_snapshot = owner.snapshot_or_throw();
        require(renewed_snapshot.state_generation ==
                    recovered_snapshot.state_generation &&
                    renewed_snapshot.outbox == recovered_snapshot.outbox &&
                    renewed_snapshot.outbox_time_high_water_epoch == 114U,
                "no-ready claim changed history or failed to advance durable time");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(999U), "receipt restart owner");
        require(owner.snapshot_or_throw() == renewed_snapshot,
                "restart forgot renewed receipt authority");

        require(owner.settle_outbox_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    115U) ==
                    SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim,
                "expired receipt retained settlement authority at its deadline");
        const SyncReplicaSqliteSnapshot expired_snapshot =
            owner.snapshot_or_throw();
        require(expired_snapshot.state_generation ==
                    renewed_snapshot.state_generation &&
                    expired_snapshot.outbox == renewed_snapshot.outbox &&
                    expired_snapshot.outbox_time_high_water_epoch == 115U,
                "expiry did not durably publish revocation without changing history");
        require(owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    115U, 15U) ==
                    SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim &&
                    owner.snapshot_or_throw() == expired_snapshot,
                "expired receipt retained retry-release authority");
        require(owner.renew_outbox_lease_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    115U, 10U) ==
                    SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim &&
                    owner.snapshot_or_throw() == expired_snapshot,
                "expired receipt was revived by a heartbeat");
        require_error(
            [&] {
                (void)owner.settle_outbox_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    114U);
            },
            "boottime-rollback",
            "clock rollback did not quarantine receipt processing after expiry");
        const SyncReplicaSqliteSnapshot expiry_rollback_quarantine =
            owner.snapshot_or_throw();
        require(
            expiry_rollback_quarantine.state_generation ==
                    expired_snapshot.state_generation &&
                expiry_rollback_quarantine.outbox == expired_snapshot.outbox &&
                expiry_rollback_quarantine.outbox_time_high_water_epoch == 115U &&
                expiry_rollback_quarantine.outbox_clock_state.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
                expiry_rollback_quarantine.outbox_clock_state.anomaly ==
                    anonsync::SyncReplicaOutboxClockAnomaly::BoottimeRollback,
            "post-expiry rollback changed evidence instead of isolating clock authority");
        const auto expiry_rollback_recovered =
            owner.recover_outbox_clock_or_throw(
                expiry_rollback_quarantine.outbox_clock_state
                    .observation_generation,
                115U);
        require(
            expiry_rollback_recovered.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Healthy &&
                expiry_rollback_recovered.high_water_epoch == 115U &&
                expiry_rollback_recovered.recovery_generation == 2U,
            "second explicit clock recovery did not preserve durable expiry");

        const auto replacement = owner.claim_next_outbox_or_throw(
            "worker-receipt-b", 115U, 10U, destination);
        require(replacement.has_value() &&
                    replacement->operation == operation &&
                    replacement->intent.lease.dispatch_attempts == 2U &&
                    replacement->intent.lease.claim_id != first_claim_id &&
                    replacement->intent.lease.claimed_at_epoch == 115U &&
                    replacement->intent.lease.lease_expires_at_epoch == 125U,
                "exact renewed expiry did not mint a fresh replacement receipt");
        const SyncReplicaSqliteSnapshot replacement_snapshot =
            owner.snapshot_or_throw();
        require(owner.settle_outbox_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    120U) ==
                    SyncReplicaSqliteOutboxReceiptResult::StaleClaim &&
                    owner.snapshot_or_throw() == replacement_snapshot,
                "stale receipt settled a replacement attempt");
        require(owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id, first_claim_id,
                    120U, 10U) ==
                    SyncReplicaSqliteOutboxReceiptResult::StaleClaim &&
                    owner.snapshot_or_throw() == replacement_snapshot,
                "stale receipt released a replacement attempt");

        require(owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id,
                    replacement->intent.lease.claim_id, 120U, 10U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "current receipt did not release its attempt");
        const SyncReplicaSqliteSnapshot released = owner.snapshot_or_throw();
        require(released.state_generation ==
                    replacement_snapshot.state_generation + 1U &&
                    released.outbox.size() == 1U &&
                    released.outbox.front().lease.dispatch_attempts == 2U &&
                    released.outbox.front().lease.claim_id.empty() &&
                    released.outbox.front().lease.retry_not_before_epoch == 130U &&
                    released.outbox.front().lease.retry_released_at_epoch == 120U &&
                    released.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
                "release did not preserve attempt history and durable backoff");
        {
            SyncSqliteDb restart_db = open_database(file.path);
            SyncReplicaSqliteOwner restart_owner(
                restart_db.db, folder, local, limits(1U),
                "exact retry provenance restart owner");
            require(restart_owner.snapshot_or_throw() == released,
                    "restart lost the observation that minted retry backoff");
        }
        require(!owner.claim_next_outbox_or_throw(
                     "worker-receipt-c", 129U, 10U, destination)
                     .has_value(),
                "retry backoff was bypassed");
        const SyncReplicaSqliteSnapshot backoff_observed =
            owner.snapshot_or_throw();
        require(backoff_observed.state_generation ==
                    released.state_generation &&
                    backoff_observed.outbox == released.outbox &&
                    backoff_observed.outbox_time_high_water_epoch == 129U,
                "backoff observation changed history or failed to advance time");

        const auto third = owner.claim_next_outbox_or_throw(
            "worker-receipt-c", 130U, 10U, destination);
        require(third.has_value() &&
                    third->intent.lease.dispatch_attempts == 3U &&
                    third->intent.lease.retry_not_before_epoch == 0U &&
                    third->intent.lease.retry_released_at_epoch == 0U &&
                    third->intent.lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::None,
                "retry-not-before boundary did not mint attempt three");
        require(owner.settle_outbox_or_throw(
                    destination, operation.operation_id,
                    third->intent.lease.claim_id, 135U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "current third receipt did not settle");
        const SyncReplicaSqliteSnapshot final = owner.snapshot_or_throw();
        require(final.outbox.empty() &&
                    final.durable.operations ==
                        std::vector<SyncReplicaOperation>{operation},
                "settlement removed canonical evidence with its sender intent");
        require(owner.settle_outbox_or_throw(
                    destination, operation.operation_id,
                    third->intent.lease.claim_id, 135U) ==
                    SyncReplicaSqliteOutboxReceiptResult::IntentMissing &&
                    owner.snapshot_or_throw() == final,
                "missing receipt replay changed the settled cutpoint");
    }
}

void test_claim_precommit_reattestation_and_lease_tamper() {
    TempDatabasePath trigger_file(
        "anonsync-replica-sqlite-owner-claim-trigger");
    const std::string folder = "folder-sqlite-claim-trigger";
    const SyncReplicaActor local =
        actor("device-sqlite-claim-trigger", 1061U);
    const std::string destination = "device-sqlite-claim-trigger-peer";
    {
        SyncSqliteDb db = open_database(trigger_file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "claim trigger owner");
        const SyncReplicaOperation operation =
            owner.create_local_file_or_throw(
                "claim-trigger/file.bin", 4U,
                anonsync::sha256_hex("claim-trigger"),
                std::vector<std::string>{destination});
        const SyncReplicaSqliteSnapshot baseline = owner.snapshot_or_throw();
        exec(db,
             "CREATE TEMP TRIGGER silent_claim_worker_mutation "
             "AFTER UPDATE OF claim_id ON main.sync_replica_outbox "
             "WHEN NEW.claim_id<>'' "
             "BEGIN UPDATE main.sync_replica_outbox "
             "SET worker_id='worker-trigger-mutated' "
             "WHERE destination_device_id=NEW.destination_device_id "
             "AND operation_id=NEW.operation_id; END;");
        require_error(
            [&] {
                (void)owner.claim_next_outbox_or_throw(
                    "worker-trigger-intended", 100U, 10U, destination);
            },
            "outbox attestation mismatch",
            "valid-looking TEMP-trigger claim mutation escaped re-attestation");
        require(owner.snapshot_or_throw() == baseline,
                "failed claim re-attestation left a durable lease prefix");
        exec(db, "DROP TRIGGER temp.silent_claim_worker_mutation;");
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-trigger-intended", 100U, 10U, destination);
        require(claim.has_value() && claim->operation == operation,
                "claim path did not recover after rollback of trigger mutation");
        const SyncReplicaSqliteSnapshot claimed = owner.snapshot_or_throw();
        exec(db,
             "CREATE TEMP TRIGGER silent_renew_worker_mutation "
             "AFTER UPDATE OF lease_expires_at_epoch_be "
             "ON main.sync_replica_outbox "
             "BEGIN UPDATE main.sync_replica_outbox "
             "SET worker_id='worker-renew-trigger-mutated' "
             "WHERE destination_device_id=NEW.destination_device_id "
             "AND operation_id=NEW.operation_id; END;");
        require_error(
            [&] {
                (void)owner.renew_outbox_lease_or_throw(
                    destination, operation.operation_id,
                    claim->intent.lease.claim_id, 105U, 10U);
            },
            "outbox attestation mismatch",
            "valid-looking TEMP-trigger heartbeat mutation escaped re-attestation");
        require(owner.snapshot_or_throw() == claimed,
                "failed heartbeat re-attestation left a durable lease prefix");
        exec(db, "DROP TRIGGER temp.silent_renew_worker_mutation;");
        require(owner.renew_outbox_lease_or_throw(
                    destination, operation.operation_id,
                    claim->intent.lease.claim_id, 105U, 10U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "heartbeat path did not recover after trigger rollback");
        const SyncReplicaSqliteSnapshot renewed = owner.snapshot_or_throw();
        require(renewed.state_generation == claimed.state_generation + 1U &&
                    renewed.outbox.size() == 1U &&
                    renewed.outbox.front().lease.claim_id ==
                        claim->intent.lease.claim_id &&
                    renewed.outbox.front().lease.worker_id ==
                        "worker-trigger-intended" &&
                    renewed.outbox.front().lease.lease_expires_at_epoch == 115U,
                "successful heartbeat changed receipt identity or deadline");
    }

    TempDatabasePath tamper_file(
        "anonsync-replica-sqlite-owner-lease-tamper");
    {
        SyncSqliteDb db = open_database(tamper_file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "lease tamper owner");
        const SyncReplicaOperation operation =
            owner.create_local_file_or_throw(
                "lease-tamper/file.bin", 4U,
                anonsync::sha256_hex("lease-tamper"),
                std::vector<std::string>{destination});
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-tamper", 100U, 10U, destination);
        require(claim.has_value(), "lease tamper fixture did not claim");
        exec(db,
             "UPDATE main.sync_replica_outbox SET claim_id='' "
             "WHERE operation_id='" + operation.operation_id + "';");
        require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "partial lease authority",
            "partial durable claim metadata survived restore validation");
    }
}

void test_concurrent_claimers_mint_one_receipt() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-claim-race");
    const std::string folder = "folder-sqlite-claim-race";
    const SyncReplicaActor local = actor("device-sqlite-claim-race", 1071U);
    const std::string destination = "device-sqlite-claim-race-peer";
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "claim race seed owner");
        (void)owner.create_local_file_or_throw(
            "claim-race/file.bin", 4U, anonsync::sha256_hex("race"),
            std::vector<std::string>{destination});
    }

    std::barrier start(2);
    std::array<bool, 2> claimed{false, false};
    std::array<std::string, 2> claim_ids;
    std::array<std::exception_ptr, 2> errors;
    std::array<std::thread, 2> workers;
    for (std::size_t index = 0; index < workers.size(); ++index) {
        workers[index] = std::thread([&, index] {
            try {
                SyncSqliteDb db = open_database(file.path);
                SyncReplicaSqliteOwner owner(
                    db.db, folder, local, limits(16U),
                    "claim race worker owner");
                start.arrive_and_wait();
                const auto claim = owner.claim_next_outbox_or_throw(
                    "worker-claim-race-" + std::to_string(index),
                    100U, 100U, destination);
                claimed[index] = claim.has_value();
                if (claim.has_value()) {
                    claim_ids[index] = claim->intent.lease.claim_id;
                }
            } catch (...) {
                errors[index] = std::current_exception();
            }
        });
    }
    for (std::thread& worker : workers) worker.join();
    for (const std::exception_ptr& error : errors) {
        if (error) std::rethrow_exception(error);
    }
    const std::size_t claim_count =
        static_cast<std::size_t>(claimed[0]) +
        static_cast<std::size_t>(claimed[1]);
    require(claim_count == 1U,
            "serialized competing workers minted more or fewer than one receipt");

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "claim race recovery owner");
    const SyncReplicaSqliteSnapshot snapshot = owner.snapshot_or_throw();
    require(snapshot.state_generation == 3U &&
                snapshot.outbox.size() == 1U &&
                snapshot.outbox.front().lease.dispatch_attempts == 1U &&
                !snapshot.outbox.front().lease.claim_id.empty() &&
                (snapshot.outbox.front().lease.claim_id == claim_ids[0] ||
                 snapshot.outbox.front().lease.claim_id == claim_ids[1]),
            "claim race did not publish one complete durable authority transition");
}

void test_durable_capacity_policy_and_retry() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-capacity");
    const std::string folder = "folder-sqlite-capacity";
    const SyncReplicaActor local = actor("device-sqlite-capacity", 1101U);
    const SyncReplicaOperation first = root_operation(
        folder, actor("device-sqlite-remote-a", 1102U),
        "remote/first.bin", "first");
    const SyncReplicaOperation second = root_operation(
        folder, actor("device-sqlite-remote-b", 1103U),
        "remote/second.bin", "second");
    SyncReplicaSqliteSnapshot blocked_baseline;

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(1U), "capacity owner");
        require(owner.accept_remote_or_throw(first) ==
                    SyncReplicaAdmission::InsertedActive,
                "capacity fixture did not admit its first valid envelope");
        blocked_baseline = owner.snapshot_or_throw();
        require(owner.accept_remote_or_throw(second) ==
                    SyncReplicaAdmission::CapacityBlocked &&
                    owner.snapshot_or_throw() == blocked_baseline,
                "capacity-blocked remote evidence mutated durable state");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(99U), "capacity restart owner");
        require(owner.accept_remote_or_throw(second) ==
                    SyncReplicaAdmission::CapacityBlocked &&
                    owner.snapshot_or_throw() == blocked_baseline,
                "restart forgot the durable policy that caused backpressure");

        SyncReplicaSqliteOwnerLimits expanded = blocked_baseline.limits;
        expanded.model.max_operations = 2U;
        owner.replace_limits_or_throw(expanded);
        const SyncReplicaSqliteSnapshot policy_changed = owner.snapshot_or_throw();
        require(policy_changed.state_generation ==
                    blocked_baseline.state_generation + 1U &&
                    policy_changed.policy_generation ==
                    blocked_baseline.policy_generation + 1U &&
                    policy_changed.durable == blocked_baseline.durable,
                "explicit policy replacement did not preserve exact evidence");
        require(owner.accept_remote_or_throw(second) ==
                    SyncReplicaAdmission::InsertedActive,
                "same exact valid envelope was not admissible after capacity expansion");
        const SyncReplicaSqliteSnapshot admitted = owner.snapshot_or_throw();
        require(admitted.durable.operations.size() == 2U &&
                    admitted.state_generation ==
                        policy_changed.state_generation + 1U,
                "post-policy retry did not publish one atomic evidence generation");
        require(owner.accept_remote_or_throw(second) ==
                    SyncReplicaAdmission::Duplicate &&
                    owner.snapshot_or_throw() == admitted,
                "exact duplicate rewrote durable state or advanced generation");

        SyncReplicaSqliteOwnerLimits too_small = admitted.limits;
        too_small.model.max_operations = 1U;
        require_error(
            [&] { owner.replace_limits_or_throw(too_small); },
            "exceeds configured operation limit",
            "policy shrink below retained evidence was not rejected atomically");
        require(owner.snapshot_or_throw() == admitted,
                "failed policy shrink mutated durable policy or evidence");
    }
}

void test_projection_and_redundant_attestation() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-fork");
    const std::string folder = "folder-sqlite-fork";
    const SyncReplicaActor local = actor("device-sqlite-fork-local", 1201U);
    const SyncReplicaActor fork_actor = actor("device-sqlite-fork-remote", 1202U);
    const SyncReplicaOperation fork_a = root_operation(
        folder, fork_actor, "fork/a.bin", "fork-a");
    const SyncReplicaOperation fork_b = root_operation(
        folder, fork_actor, "fork/b.bin", "fork-b");

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(8U), "fork projection owner");
    require(owner.accept_remote_or_throw(fork_a) ==
                SyncReplicaAdmission::InsertedActive &&
                owner.accept_remote_or_throw(fork_b) ==
                SyncReplicaAdmission::InsertedQuarantined,
            "same-dot fork fixture did not produce deterministic quarantine");
    const SyncReplicaSqliteSnapshot snapshot = owner.snapshot_or_throw();
    anonsync::SyncReplicaModel restored =
        anonsync::SyncReplicaModel::restore_or_throw(
            snapshot.durable, snapshot.limits.model);
    require(restored.evidence_state(fork_a.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDotFork &&
                restored.evidence_state(fork_b.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDotFork &&
                restored.operation_count() == 0U,
            "durable fork projection selected an arrival-order winner");

    exec(db,
         "UPDATE main.sync_replica_operations SET evidence_state='active' "
         "WHERE operation_id='" + fork_a.operation_id + "';");
    require_error(
        [&] { (void)owner.snapshot_or_throw(); },
        "stored evidence projection mismatch",
        "tampered evidence-state cache was trusted over exact reprojection");
}

void test_transaction_failure_rolls_back_entire_cutpoint() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-rollback");
    const std::string folder = "folder-sqlite-rollback";
    const SyncReplicaActor local = actor("device-sqlite-rollback", 1301U);
    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "rollback owner");
    const SyncReplicaSqliteSnapshot empty = owner.snapshot_or_throw();
    const std::vector<std::string> destinations{"device-sqlite-rollback-peer"};

    exec(db,
         "CREATE TEMP TRIGGER fail_outbox_insert "
         "BEFORE INSERT ON main.sync_replica_outbox "
         "BEGIN SELECT RAISE(ABORT,'injected outbox failure'); END;");
    require_error(
        [&] {
            (void)owner.create_local_file_or_throw(
                "rollback/one.bin", 3U, anonsync::sha256_hex("one"),
                destinations);
        },
        "injected outbox failure",
        "outbox-stage SQL failure did not abort local publication");
    require(owner.snapshot_or_throw() == empty &&
                scalar_count(db, "sync_replica_operations") == 0U &&
                scalar_count(db, "sync_replica_outbox") == 0U,
            "outbox-stage failure left a counter, operation, projection, or intent prefix");
    exec(db, "DROP TRIGGER temp.fail_outbox_insert;");

    const SyncReplicaOperation committed = owner.create_local_file_or_throw(
        "rollback/one.bin", 3U, anonsync::sha256_hex("one"), destinations);
    const SyncReplicaSqliteSnapshot baseline = owner.snapshot_or_throw();
    exec(db,
         "CREATE TEMP TRIGGER fail_meta_update "
         "BEFORE UPDATE ON main.sync_replica_meta "
         "BEGIN SELECT RAISE(ABORT,'injected meta failure'); END;");
    require_error(
        [&] {
            (void)owner.create_local_tombstone_or_throw(
                "rollback/one.bin", destinations);
        },
        "injected meta failure",
        "final metadata-stage SQL failure did not abort local publication");
    require(owner.snapshot_or_throw() == baseline &&
                scalar_count(db, "sync_replica_operations") == 1U &&
                scalar_count(db, "sync_replica_outbox") == 1U &&
                owner.snapshot_or_throw().outbox.front().operation_id ==
                    committed.operation_id,
            "metadata-stage failure exposed a partially committed tombstone cutpoint");
}

void test_schema_contract_and_outbox_tamper_detection() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-tamper");
    const std::string folder = "folder-sqlite-tamper";
    const SyncReplicaActor local = actor("device-sqlite-tamper", 1401U);
    SyncReplicaOperation operation;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "tamper seed owner");
        const std::vector<std::string> destinations{"device-sqlite-tamper-peer"};
        operation = owner.create_local_file_or_throw(
            "tamper/file.bin", 4U, anonsync::sha256_hex("file"),
            destinations);
        exec(db,
             "UPDATE main.sync_replica_outbox SET enqueued_generation_be=x'0000000000000000' "
             "WHERE operation_id='" + operation.operation_id + "';");
        require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "outbox intent is invalid",
            "tampered outbox generation survived restore attestation");
    }

    TempDatabasePath policy_file("anonsync-replica-sqlite-owner-policy-seal");
    {
        SyncSqliteDb db = open_database(policy_file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "policy seal seed owner");
        exec(db,
             "UPDATE main.sync_replica_meta SET "
             "max_operations_be=x'0000000000000011' WHERE id=1;");
        require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "cutpoint digest mismatch",
            "casual durable-policy edit bypassed the structural cutpoint seal");
    }

    TempDatabasePath schema_file("anonsync-replica-sqlite-owner-schema");
    {
        SyncSqliteDb db = open_database(schema_file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "schema seed owner");
        exec(db, "DROP INDEX main.sync_replica_outbox_operation;");
    }
    {
        SyncSqliteDb db = open_database(schema_file.path);
        require_error(
            [&] {
                SyncReplicaSqliteOwner owner(
                    db.db, folder, local, limits(16U),
                    "schema reopen owner");
            },
            "does not match schema v5",
            "partial durable schema was silently repaired or accepted");
    }
}

void test_retry_release_provenance_tamper_and_precommit_guard() {
    const std::string folder = "folder-sqlite-retry-provenance";
    const SyncReplicaActor local = actor(
        "device-sqlite-retry-provenance", 1411U);
    const std::string destination = "device-sqlite-retry-provenance-peer";

    TempDatabasePath release_time_file(
        "anonsync-replica-sqlite-retry-release-time-tamper");
    {
        SyncSqliteDb db = open_database(release_time_file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U),
            "retry release-time tamper owner");
        const SyncReplicaOperation operation = owner.create_local_file_or_throw(
            "retry/tamper-time.bin", 4U, anonsync::sha256_hex("time"),
            std::vector<std::string>{destination});
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-retry-time", 100U, 20U, destination);
        require(claim.has_value(),
                "retry release-time tamper fixture did not mint a claim");
        require(owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id,
                    claim->intent.lease.claim_id, 105U, 10U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "retry release-time tamper fixture did not release exactly");
        exec(db,
             "UPDATE main.sync_replica_outbox SET "
             "retry_released_at_epoch_be=zeroblob(8);");
        require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "invalid exact retry release provenance",
            "zeroed release observation survived exact-state validation");
    }

    TempDatabasePath provenance_file(
        "anonsync-replica-sqlite-retry-provenance-tamper");
    {
        SyncSqliteDb db = open_database(provenance_file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U),
            "retry provenance tamper owner");
        const SyncReplicaOperation operation = owner.create_local_file_or_throw(
            "retry/tamper-provenance.bin", 10U,
            anonsync::sha256_hex("provenance"),
            std::vector<std::string>{destination});
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-retry-provenance", 200U, 20U, destination);
        require(claim.has_value(),
                "retry provenance tamper fixture did not mint a claim");
        require(owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id,
                    claim->intent.lease.claim_id, 205U, 10U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "retry provenance tamper fixture did not release exactly");
        exec(db,
             "UPDATE main.sync_replica_outbox SET "
             "retry_release_provenance=2;");
        require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "fabricates an exact legacy retry release epoch",
            "provenance downgrade laundered an exact observation into legacy state");
    }

    TempDatabasePath trigger_file(
        "anonsync-replica-sqlite-retry-provenance-trigger");
    {
        SyncSqliteDb db = open_database(trigger_file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U),
            "retry provenance trigger owner");
        const SyncReplicaOperation operation = owner.create_local_file_or_throw(
            "retry/trigger.bin", 7U, anonsync::sha256_hex("trigger"),
            std::vector<std::string>{destination});
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-retry-trigger", 300U, 20U, destination);
        require(claim.has_value(),
                "retry provenance trigger fixture did not mint a claim");
        const SyncReplicaSqliteSnapshot baseline = owner.snapshot_or_throw();
        exec(db,
             "CREATE TEMP TRIGGER mutate_retry_provenance "
             "AFTER UPDATE OF retry_release_provenance "
             "ON main.sync_replica_outbox "
             "WHEN NEW.retry_release_provenance=1 "
             "BEGIN UPDATE main.sync_replica_outbox "
             "SET retry_release_provenance=2 "
             "WHERE destination_device_id=NEW.destination_device_id "
             "AND operation_id=NEW.operation_id; END;");
        require_error(
            [&] {
                (void)owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id,
                    claim->intent.lease.claim_id, 305U, 10U);
            },
            "fabricates an exact legacy retry release epoch",
            "post-update provenance mutation escaped staged re-attestation");
        require(owner.snapshot_or_throw() == baseline,
                "failed provenance re-attestation committed a row or clock prefix");
    }
}

void test_exact_schema_attachment_and_precommit_reattestation() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-trigger-guard");
    const std::string folder = "folder-sqlite-trigger-guard";
    const SyncReplicaActor local = actor("device-sqlite-trigger-guard", 1421U);
    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "trigger guard owner");
    const SyncReplicaSqliteSnapshot baseline = owner.snapshot_or_throw();

    // An object's own name is not sufficient schema evidence: an unrelated
    // trigger name can still attach executable behavior to a replica table.
    exec(db,
         "CREATE TRIGGER main.unrelated_audit_trigger "
         "AFTER INSERT ON sync_replica_operations BEGIN SELECT 1; END;");
    require_error(
        [&] { (void)owner.snapshot_or_throw(); },
        "exact sqlite_schema contract mismatch",
        "main trigger attached under an unrelated name escaped schema attestation");
    exec(db, "DROP TRIGGER main.unrelated_audit_trigger;");
    require(owner.snapshot_or_throw() == baseline,
            "rejected attached trigger changed the durable cutpoint");

    // TEMP objects are connection-local and intentionally remain available for
    // fault injection. A successful AFTER trigger must nevertheless be caught
    // by the full staged reload before COMMIT, then rolled back with its writes.
    exec(db,
         "CREATE TEMP TRIGGER silent_outbox_mutation "
         "AFTER INSERT ON main.sync_replica_outbox "
         "BEGIN UPDATE main.sync_replica_outbox "
         "SET enqueued_generation_be=x'0000000000000000' "
         "WHERE destination_device_id=NEW.destination_device_id "
         "AND operation_id=NEW.operation_id; END;");
    const std::vector<std::string> destinations{
        "device-sqlite-trigger-peer"};
    require_error(
        [&] {
            (void)owner.create_local_file_or_throw(
                "trigger/file.bin", 4U, anonsync::sha256_hex("file"),
                destinations);
        },
        "outbox intent is invalid",
        "silent TEMP-trigger mutation was committed as a successful publication");
    require(owner.snapshot_or_throw() == baseline &&
                scalar_count(db, "sync_replica_operations") == 0U &&
                scalar_count(db, "sync_replica_outbox") == 0U,
            "pre-commit re-attestation failure left a durable transaction prefix");
    exec(db, "DROP TRIGGER temp.silent_outbox_mutation;");

    const SyncReplicaOperation committed = owner.create_local_file_or_throw(
        "trigger/file.bin", 4U, anonsync::sha256_hex("file"), destinations);
    const auto recovered_claim = owner.claim_next_outbox_or_throw(
        "worker-trigger-recovery", 100U, 10U, destinations.front());
    require(recovered_claim.has_value() &&
                recovered_claim->operation == committed,
            "owner did not recover after rolling back a silently mutated stage");
}


void test_unknown_clock_capability_is_durably_quarantined() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-clock-unknown");
    const std::string folder = "folder-sqlite-clock-unknown";
    const SyncReplicaActor local = actor("device-sqlite-clock-unknown", 1429U);
    const std::string destination = "device-clock-unknown-peer";
    SyncReplicaSqliteSnapshot quarantined;

    {
        SyncSqliteDb db = open_database(file.path);
        set_test_clock_epoch(200U);
        anonsync::SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "unknown clock owner",
            make_test_outbox_clock_source());
        const SyncReplicaOperation operation = owner.create_local_file_or_throw(
            "clock/unknown.txt", 7U,
            anonsync::sha256_hex("unknown-clock-payload"),
            std::array<std::string, 1>{destination});
        const SyncReplicaSqliteSnapshot before = owner.snapshot_or_throw();

        test_clock_observation.source_id =
            "linux-boottime-adjtimex-timens-unavailable-v1";
        test_clock_observation.time_namespace_id = anonsync::sha256_hex(
            "time-namespace-identity-unavailable");
        test_clock_observation.synchronization =
            anonsync::SyncReplicaOutboxClockSynchronization::Unknown;
        require_error(
            [&] {
                (void)owner.claim_next_outbox_or_throw(
                    "worker-clock-unknown", 30U, destination);
            },
            "synchronization-unknown",
            "unknown time-namespace capability was not published as an exact quarantine");

        quarantined = owner.snapshot_or_throw();
        require(
            quarantined.state_generation == before.state_generation &&
                quarantined.durable == before.durable &&
                quarantined.outbox == before.outbox &&
                quarantined.outbox.size() == 1U &&
                quarantined.outbox.front().operation_id == operation.operation_id &&
                quarantined.outbox_clock_state.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
                quarantined.outbox_clock_state.anomaly ==
                    anonsync::SyncReplicaOutboxClockAnomaly::SynchronizationUnknown &&
                quarantined.outbox_clock_state.rejected == test_clock_observation &&
                quarantined.outbox_clock_digest != before.outbox_clock_digest,
            "unknown capability quarantine changed replica authority or failed to persist exact rejected evidence");
    }

    // Reopening through a fresh connection proves this was a committed cutpoint,
    // not merely an exception-local state transition.
    {
        SyncSqliteDb reopened = open_database(file.path);
        anonsync::SyncReplicaSqliteOwner restored(
            reopened.db, folder, local, limits(999U),
            "unknown clock restart owner", make_test_outbox_clock_source());
        require(
            restored.snapshot_or_throw() == quarantined,
            "restart forgot the synchronization-unknown quarantine cutpoint");
        require_error(
            [&] {
                (void)restored.claim_next_outbox_or_throw(
                    "worker-clock-unknown-restart", 30U, destination);
            },
            "synchronization-unknown",
            "sticky unknown-capability quarantine minted liveness authority after restart");
    }

    // Restore deterministic defaults for every later test in this process.
    test_clock_observation.source_id = "test-boottime-realtime-v1";
    test_clock_observation.time_namespace_id = std::string(64U, 'a');
    set_test_clock_epoch(200U);
}

void test_outbox_clock_precommit_reattestation_and_tamper() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-clock-guard");
    const std::string folder = "folder-sqlite-clock-guard";
    const SyncReplicaActor local = actor("device-sqlite-clock-guard", 1431U);
    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "clock guard owner");
    const SyncReplicaSqliteSnapshot baseline = owner.snapshot_or_throw();
    require(baseline.outbox_time_high_water_epoch == 0U &&
                anonsync::is_lowercase_sha256_hex(
                    baseline.outbox_clock_digest),
            "fresh owner did not expose one canonical zero clock fence");

    exec(db,
         "CREATE TEMP TABLE sync_replica_outbox_clock("
         "id INTEGER PRIMARY KEY,clock_state_bytes BLOB,clock_digest TEXT);"
         "INSERT INTO temp.sync_replica_outbox_clock VALUES("
         "1,x'ff',"
         "'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff');");
    require(owner.snapshot_or_throw() == baseline,
            "TEMP clock shadow displaced main clock authority");

    exec(db,
         "CREATE TEMP TRIGGER silent_clock_digest_mutation "
         "AFTER UPDATE ON main.sync_replica_outbox_clock "
         "BEGIN UPDATE main.sync_replica_outbox_clock "
         "SET clock_digest='0000000000000000000000000000000000000000000000000000000000000000' "
         "WHERE id=NEW.id; END;");
    require_error(
        [&] {
            (void)owner.claim_next_outbox_or_throw(
                "worker-clock-guard", 100U, 10U);
        },
        "outbox clock attestation mismatch",
        "TEMP-trigger clock mutation escaped staged re-attestation");
    require(owner.snapshot_or_throw() == baseline,
            "failed clock-only publication escaped transaction rollback");
    exec(db, "DROP TRIGGER temp.silent_clock_digest_mutation;");

    require(!owner.claim_next_outbox_or_throw(
                 "worker-clock-guard", 100U, 10U)
                 .has_value(),
            "empty outbox unexpectedly returned a claim");
    const SyncReplicaSqliteSnapshot observed = owner.snapshot_or_throw();
    require(observed.state_generation == baseline.state_generation &&
                observed.policy_generation == baseline.policy_generation &&
                observed.durable == baseline.durable &&
                observed.outbox == baseline.outbox &&
                observed.outbox_time_high_water_epoch == 100U &&
                observed.outbox_clock_digest != baseline.outbox_clock_digest,
            "clock-only publication changed evidence or failed to advance time");
    require_error(
        [&] {
            (void)owner.claim_next_outbox_or_throw(
                "worker-clock-guard", 99U, 10U);
        },
        "boottime-rollback",
        "no-ready scheduler path did not quarantine a host-clock rollback");
    const SyncReplicaSqliteSnapshot quarantined = owner.snapshot_or_throw();
    require(
        quarantined.state_generation == observed.state_generation &&
            quarantined.policy_generation == observed.policy_generation &&
            quarantined.durable == observed.durable &&
            quarantined.outbox == observed.outbox &&
            quarantined.outbox_time_high_water_epoch == 100U &&
            quarantined.outbox_clock_state.health ==
                anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
            quarantined.outbox_clock_state.anomaly ==
                anonsync::SyncReplicaOutboxClockAnomaly::BoottimeRollback,
        "scheduler rollback changed evidence instead of isolating clock authority");
    const auto recovered = owner.recover_outbox_clock_or_throw(
        quarantined.outbox_clock_state.observation_generation, 100U);
    require(
        recovered.health == anonsync::SyncReplicaOutboxClockHealth::Healthy &&
            recovered.high_water_epoch == 100U &&
            recovered.recovery_generation == 1U,
        "clock guard recovery did not preserve the durable time floor");

    exec(db,
         "UPDATE main.sync_replica_outbox_clock "
         "SET clock_digest='ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' "
         "WHERE id=1;");
    require_error(
        [&] { (void)owner.snapshot_or_throw(); },
        "outbox clock attestation mismatch",
        "direct durable clock tamper escaped digest attestation");
}

void test_explicit_clock_observation_and_recovery_preserve_replica_authority() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-clock-observe-api");
    const std::string folder = "folder-sqlite-clock-observe-api";
    const SyncReplicaActor local = actor(
        "device-sqlite-clock-observe-api", 1433U);
    const std::string destination = "device-clock-observe-api-peer";

    test_clock_observation.source_id = "test-boottime-realtime-v1";
    test_clock_observation.boot_id =
        "01234567-89ab-cdef-0123-456789abcdef";
    test_clock_observation.time_namespace_id = std::string(64U, 'a');
    test_clock_observation.synchronization =
        anonsync::SyncReplicaOutboxClockSynchronization::Synchronized;

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "clock observe API owner");
    (void)owner.create_local_file_or_throw(
        "clock/observe-api.bin", 11U,
        anonsync::sha256_hex("clock-observe-api"),
        std::vector<std::string>{destination});
    const SyncReplicaSqliteSnapshot baseline = owner.snapshot_or_throw();

    const auto require_nonclock_authority_unchanged = [&baseline](
        const SyncReplicaSqliteSnapshot& observed,
        const std::string& label) {
        require(
            observed.durable == baseline.durable &&
                observed.limits == baseline.limits &&
                observed.state_generation == baseline.state_generation &&
                observed.policy_generation == baseline.policy_generation &&
                observed.outbox == baseline.outbox &&
                observed.local_operation_digest ==
                    baseline.local_operation_digest &&
                observed.operation_set_digest ==
                    baseline.operation_set_digest &&
                observed.evidence_set_digest ==
                    baseline.evidence_set_digest &&
                observed.visible_state_digest ==
                    baseline.visible_state_digest &&
                observed.outbox_digest == baseline.outbox_digest,
            label + " changed replica evidence, policy, or outbox authority");
    };

    const auto accepted = owner.observe_outbox_clock_or_throw(200U);
    const SyncReplicaSqliteSnapshot accepted_snapshot =
        owner.snapshot_or_throw();
    require(
        accepted.outcome ==
                anonsync::SyncReplicaOutboxClockObservationOutcome::Accepted &&
            accepted.changed && accepted.usable_epoch == 200U &&
            accepted.state == accepted_snapshot.outbox_clock_state &&
            accepted.state.health ==
                anonsync::SyncReplicaOutboxClockHealth::Healthy &&
            accepted.state.high_water_epoch == 200U &&
            accepted.state.observation_generation == 1U &&
            accepted.state.recovery_generation == 0U &&
            accepted_snapshot.outbox_clock_digest !=
                baseline.outbox_clock_digest,
        "explicit clock observation did not publish one exact healthy cutpoint");
    require_nonclock_authority_unchanged(
        accepted_snapshot, "explicit clock observation");

    const auto identical = owner.observe_outbox_clock_or_throw(200U);
    require(
        identical.outcome ==
                anonsync::SyncReplicaOutboxClockObservationOutcome::Accepted &&
            !identical.changed && identical.usable_epoch == 200U &&
            owner.snapshot_or_throw() == accepted_snapshot,
        "identical explicit observation rewrote the durable clock cutpoint");

    const auto quarantined = owner.observe_outbox_clock_or_throw(199U);
    const SyncReplicaSqliteSnapshot quarantined_snapshot =
        owner.snapshot_or_throw();
    require(
        quarantined.outcome ==
                anonsync::SyncReplicaOutboxClockObservationOutcome::Quarantined &&
            quarantined.changed && quarantined.usable_epoch == 0U &&
            quarantined.state == quarantined_snapshot.outbox_clock_state &&
            quarantined.state.health ==
                anonsync::SyncReplicaOutboxClockHealth::Quarantined &&
            quarantined.state.anomaly ==
                anonsync::SyncReplicaOutboxClockAnomaly::BoottimeRollback &&
            quarantined.state.high_water_epoch == 200U &&
            quarantined.state.observation_generation == 2U &&
            quarantined.state.recovery_generation == 0U,
        "explicit rollback observation was not durably quarantined");
    require_nonclock_authority_unchanged(
        quarantined_snapshot, "explicit clock quarantine");

    const auto sticky = owner.observe_outbox_clock_or_throw(201U);
    require(
        sticky.outcome == anonsync::
                SyncReplicaOutboxClockObservationOutcome::AlreadyQuarantined &&
            !sticky.changed && sticky.usable_epoch == 0U &&
            sticky.state == quarantined.state &&
            owner.snapshot_or_throw() == quarantined_snapshot,
        "explicit observation bypassed sticky clock quarantine");
    require_error(
        [&]() { (void)owner.recover_outbox_clock_or_throw(1U, 201U); },
        "recovery generation does not name current quarantine",
        "stale recovery generation changed quarantined clock authority");
    require(owner.snapshot_or_throw() == quarantined_snapshot,
            "stale recovery generation changed the durable cutpoint");

    const auto recovered = owner.recover_outbox_clock_or_throw(2U, 201U);
    const SyncReplicaSqliteSnapshot recovered_snapshot =
        owner.snapshot_or_throw();
    require(
        recovered == recovered_snapshot.outbox_clock_state &&
            recovered.health ==
                anonsync::SyncReplicaOutboxClockHealth::Healthy &&
            recovered.anomaly ==
                anonsync::SyncReplicaOutboxClockAnomaly::None &&
            recovered.high_water_epoch == 201U &&
            recovered.observation_generation == 3U &&
            recovered.recovery_generation == 1U &&
            recovered.accepted.has_value() && !recovered.rejected.has_value(),
        "exact explicit recovery did not publish one fresh healthy anchor");
    require_nonclock_authority_unchanged(
        recovered_snapshot, "explicit clock recovery");
    require_error(
        [&]() { (void)owner.recover_outbox_clock_or_throw(3U, 202U); },
        "clock is not quarantined",
        "repeated recovery changed healthy clock authority");
    require(owner.snapshot_or_throw() == recovered_snapshot,
            "repeated recovery changed the durable cutpoint");
}

void test_clock_sampling_is_inside_writer_transaction() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-clock-linearization");
    const std::string folder = "folder-sqlite-clock-linearization";
    const SyncReplicaActor local = actor(
        "device-sqlite-clock-linearization", 1437U);
    SyncSqliteDb db = open_database(file.path);
    auto probe = std::make_shared<WriterLockClockProbeState>();
    probe->database_path = file.path;
    anonsync::SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U),
        "clock linearization owner",
        std::make_unique<WriterLockClockProbeSource>(probe));

    require(!owner.claim_next_outbox_or_throw("worker-clock-linearization", 10U)
                 .has_value(),
            "empty outbox returned a claim during clock linearization probe");
    require(probe->observations == 1U &&
                probe->competing_writer_was_blocked,
            "clock observation was not taken under exact SQLite writer authority");
    const SyncReplicaSqliteSnapshot snapshot = owner.snapshot_or_throw();
    require(snapshot.outbox_time_high_water_epoch == 200U &&
                snapshot.outbox_clock_state.health ==
                    anonsync::SyncReplicaOutboxClockHealth::Healthy,
            "writer-linearized observation was not durably published");
}

void test_local_authority_mapping_digest() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-local-authority");
    const std::string folder = "folder-sqlite-local-authority";
    const SyncReplicaActor local = actor("device-sqlite-local-authority", 1431U);
    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "local authority owner");
    const SyncReplicaOperation authorized = owner.create_local_file_or_throw(
        "authority/file.bin", 10U, anonsync::sha256_hex("authorized"));
    SyncReplicaOperation fork = authorized;
    fork.content_sha256 = anonsync::sha256_hex("forged-fork");
    fork.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(fork);
    require(owner.accept_remote_or_throw(fork) ==
                SyncReplicaAdmission::InsertedQuarantined,
            "local-authority fixture did not retain its same-dot fork");
    const SyncReplicaSqliteSnapshot compromised = owner.snapshot_or_throw();
    require(compromised.durable.local_operation_ids ==
                    std::vector<std::string>{authorized.operation_id} &&
                compromised.durable.operations.size() == 2U &&
                compromised.local_operation_digest.size() == 64U,
            "local authority mapping was not exposed as exact digest-bound state");

    // Either fork is structurally capable of occupying counter 1. Operation and
    // evidence set digests are identical under this swap, so the dedicated
    // authority-map digest is what makes the corruption observable.
    exec(db,
         "UPDATE main.sync_replica_local_operations SET operation_id='" +
             fork.operation_id +
             "' WHERE counter_be=x'0000000000000001';");
    require_error(
        [&] { (void)owner.snapshot_or_throw(); },
        "local operation authority digest mismatch",
        "same-dot fork substitution rewrote local mint authority undetected");
    exec(db,
         "UPDATE main.sync_replica_local_operations SET operation_id='" +
             authorized.operation_id +
             "' WHERE counter_be=x'0000000000000001';");
    require(owner.snapshot_or_throw() == compromised,
            "restoring the exact local authority mapping did not restore the cutpoint");
}

void test_pending_dependency_restart_and_activation() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-pending");
    const std::string folder = "folder-sqlite-pending";
    const SyncReplicaActor local = actor("device-sqlite-pending-local", 1441U);
    const SyncReplicaOperation parent = root_operation(
        folder, actor("device-sqlite-pending-parent", 1442U),
        "pending/file.bin", "parent");
    const SyncReplicaOperation child = child_operation(
        parent, actor("device-sqlite-pending-child", 1443U), "child");
    SyncReplicaSqliteSnapshot pending;

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "pending child owner");
        require(owner.accept_remote_or_throw(child) ==
                    SyncReplicaAdmission::InsertedPending,
                "child-first admission did not persist exact pending evidence");
        pending = owner.snapshot_or_throw();
        const anonsync::SyncReplicaModel model =
            anonsync::SyncReplicaModel::restore_or_throw(
                pending.durable, pending.limits.model);
        require(model.evidence_state(child.operation_id) ==
                    SyncReplicaEvidenceState::PendingMissingDependency &&
                    model.missing_predecessor_operation_ids() ==
                        std::vector<std::string>{parent.operation_id} &&
                    scalar_count(db, "sync_replica_parent_edges") == 1U,
                "pending cutpoint lost its exact parent edge or fetch request");
    }

    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(99U), "pending restart owner");
        require(owner.snapshot_or_throw() == pending,
                "restart changed a pending evidence cutpoint");
        require(owner.accept_remote_or_throw(parent) ==
                    SyncReplicaAdmission::InsertedActive,
                "late exact parent was not admitted after pending restart");
        const SyncReplicaSqliteSnapshot activated = owner.snapshot_or_throw();
        const anonsync::SyncReplicaModel model =
            anonsync::SyncReplicaModel::restore_or_throw(
                activated.durable, activated.limits.model);
        const auto visible = model.visible_path("pending/file.bin");
        require(model.evidence_state(parent.operation_id) ==
                    SyncReplicaEvidenceState::Active &&
                    model.evidence_state(child.operation_id) ==
                    SyncReplicaEvidenceState::Active &&
                    model.missing_predecessor_operation_ids().empty() &&
                    model.causal_head_operation_ids() ==
                        std::vector<std::string>{child.operation_id} &&
                    visible.has_value() &&
                    visible->primary_operation_id == child.operation_id,
                "late parent did not atomically reproject the persisted child active");
        require(activated.state_generation == pending.state_generation + 1U &&
                    scalar_count(db, "sync_replica_operations") == 2U &&
                    scalar_count(db, "sync_replica_parent_edges") == 1U,
                "dependency activation rewrote evidence rows or advanced multiple generations");
    }
}

void test_outbox_budget_precedes_local_mint() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-outbox-budget");
    const std::string folder = "folder-sqlite-outbox-budget";
    const SyncReplicaActor local = actor("device-sqlite-outbox-budget", 1447U);
    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U, 1U, 128U),
        "outbox budget owner");
    const SyncReplicaSqliteSnapshot empty = owner.snapshot_or_throw();
    const std::vector<std::string> two_destinations{
        "device-sqlite-budget-a", "device-sqlite-budget-b"};
    require_error(
        [&] {
            (void)owner.create_local_file_or_throw(
                "budget/blocked.bin", 1U, anonsync::sha256_hex("x"),
                two_destinations);
        },
        "outbox intent capacity",
        "fanout over outbox capacity consumed local mint authority");
    require(owner.snapshot_or_throw() == empty,
            "outbox preflight denial changed evidence, counter, or generation");

    const std::vector<std::string> duplicate_destinations{
        "device-sqlite-budget-a", "device-sqlite-budget-a"};
    require_error(
        [&] {
            (void)owner.create_local_tombstone_or_throw(
                "budget/duplicate.bin", duplicate_destinations);
        },
        "contains a duplicate",
        "duplicate destination list reached durable publication");
    const std::vector<std::string> self_destination{local.device_id};
    require_error(
        [&] {
            (void)owner.create_local_tombstone_or_throw(
                "budget/self.bin", self_destination);
        },
        "self-directed",
        "self-directed outbox intent reached durable publication");
    require(owner.snapshot_or_throw() == empty,
            "invalid destination preflights changed the empty cutpoint");

    const std::vector<std::string> one_destination{
        "device-sqlite-budget-a"};
    (void)owner.create_local_file_or_throw(
        "budget/one.bin", 1U, anonsync::sha256_hex("one"), one_destination);
    const SyncReplicaSqliteSnapshot full = owner.snapshot_or_throw();
    require_error(
        [&] {
            (void)owner.create_local_file_or_throw(
                "budget/two.bin", 1U, anonsync::sha256_hex("two"),
                one_destination);
        },
        "outbox intent capacity",
        "full sender outbox consumed a second local counter before denial");
    require(owner.snapshot_or_throw() == full &&
                full.durable.last_local_counter == 1U &&
                full.durable.operations.size() == 1U &&
                full.outbox.size() == 1U,
            "full sender outbox denial left a local operation prefix");
}

void test_projection_guard_serializes_external_effect_cutpoint() {
    TempDatabasePath file(
        "anonsync-replica-sqlite-owner-projection-guard");
    const std::string folder = "folder-sqlite-projection-guard";
    const SyncReplicaActor local =
        actor("device-sqlite-projection-guard", 1441U);
    const SyncReplicaOperation parent = root_operation(
        folder, actor("device-projection-guard-parent", 1442U),
        "guarded/file.bin", "parent-bytes");
    const SyncReplicaOperation child = child_operation(
        parent, actor("device-projection-guard-child", 1443U),
        "child-bytes");

    SyncSqliteDb guarded_db = open_database(file.path);
    anonsync::SyncReplicaSqliteOwner guarded_owner(
        guarded_db.db, folder, local, limits(16U),
        "projection guard owner", make_test_outbox_clock_source());
    const anonsync::SyncReplicaSqliteRemoteAdmissionResult admission =
        guarded_owner.accept_remote_with_cutpoint_or_throw(parent);
    require(admission.admission == SyncReplicaAdmission::InsertedActive &&
                admission.evidence_state == SyncReplicaEvidenceState::Active &&
                admission.state_generation != 0U &&
                !admission.cutpoint_digest.empty(),
            "projection guard fixture did not publish one active cutpoint");

    // Construct a fully independent owner before acquiring the guard. Its next
    // BEGIN IMMEDIATE must fail quickly while the guarded cutpoint is live, then
    // succeed unchanged after release. This models the causal writer that could
    // otherwise race a filesystem publication between snapshot and effect.
    SyncSqliteDb competing_db = open_database(file.path);
    anonsync::SyncReplicaSqliteOwner competing_owner(
        competing_db.db, folder, local, limits(16U),
        "projection guard competing owner", make_test_outbox_clock_source());
    anonsync::sqlite_set_busy_timeout_or_throw(
        competing_db.db, 0, "projection guard zero busy timeout");

    std::unique_ptr<anonsync::SyncReplicaSqliteProjectionGuard> guard =
        guarded_owner.guard_unambiguous_file_primary_at_cutpoint_or_throw(
            parent, admission.state_generation, admission.cutpoint_digest);
    require(guard != nullptr && guard->active() &&
                guard->snapshot().state_generation ==
                    admission.state_generation &&
                guard->snapshot().cutpoint_digest ==
                    admission.cutpoint_digest,
            "projection guard did not retain the exact evidence cutpoint");
    require_error(
        [&] { (void)competing_owner.accept_remote_or_throw(child); },
        "database is locked",
        "independent causal writer crossed a live projection guard");
    require(guard->active() &&
                guard->snapshot().cutpoint_digest ==
                    admission.cutpoint_digest,
            "blocked writer revoked or changed projection guard authority");

    guard->commit_or_throw();
    require(!guard->active(),
            "committed projection guard remained authoritative");
    require(competing_owner.accept_remote_or_throw(child) ==
                SyncReplicaAdmission::InsertedActive,
            "causal writer did not resume after projection guard release");

    const SyncReplicaSqliteSnapshot advanced =
        guarded_owner.snapshot_or_throw();
    const auto view = anonsync::SyncReplicaModel::restore_or_throw(
        advanced.durable, advanced.limits.model)
                          .visible_path(parent.canonical_path);
    require(advanced.state_generation == admission.state_generation + 1U &&
                view.has_value() &&
                view->primary_operation_id == child.operation_id,
            "post-guard causal writer did not publish the superseding projection");

    const SyncReplicaSqliteSnapshot before_stale =
        guarded_owner.snapshot_or_throw();
    const auto stale =
        guarded_owner.guard_unambiguous_file_primary_at_cutpoint_or_throw(
            parent, admission.state_generation, admission.cutpoint_digest);
    require(stale == nullptr &&
                guarded_owner.snapshot_or_throw() == before_stale,
            "stale projection cutpoint minted authority or changed durable state");
}


void test_outbox_dispatch_guard_reattests_and_serializes_claim() {
    static_assert(!std::is_copy_constructible_v<
                  anonsync::SyncReplicaSqliteOutboxDispatchGuard>);
    static_assert(!std::is_copy_assignable_v<
                  anonsync::SyncReplicaSqliteOutboxDispatchGuard>);
    static_assert(!std::is_move_constructible_v<
                  anonsync::SyncReplicaSqliteOutboxDispatchGuard>);
    static_assert(!std::is_move_assignable_v<
                  anonsync::SyncReplicaSqliteOutboxDispatchGuard>);

    {
        TempDatabasePath file("anonsync-replica-sqlite-owner-dispatch-guard");
        const std::string folder = "folder-sqlite-dispatch-guard";
        const SyncReplicaActor local =
            actor("device-sqlite-dispatch-guard", 1441U);
        const std::string destination =
            "device-sqlite-dispatch-guard-peer";
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "dispatch guard owner");
        SyncSqliteDb competing_db = open_database(file.path);
        anonsync::sqlite_set_busy_timeout_or_throw(
            competing_db.db, 0, "dispatch guard competing busy timeout");
        SyncReplicaSqliteOwner competing_owner(
            competing_db.db, folder, local, limits(16U),
            "dispatch guard competing owner");

        const std::vector<std::string> destinations{destination};
        const SyncReplicaOperation operation = owner.create_local_file_or_throw(
            "dispatch/file.bin", 8U, anonsync::sha256_hex("dispatch"),
            destinations);
        const auto first = owner.claim_next_outbox_or_throw(
            "dispatch-worker-1", 100U, 10U, destination);
        require(first.has_value() && first->operation == operation &&
                    first->intent.lease.lease_expires_at_epoch == 110U,
                "dispatch guard fixture did not mint its first exact claim");
        require(owner.renew_outbox_lease_or_throw(
                    destination, operation.operation_id,
                    first->intent.lease.claim_id, 101U, 20U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "dispatch guard fixture could not renew its exact claim");
        const SyncReplicaSqliteSnapshot renewed = owner.snapshot_or_throw();
        require(renewed.outbox.size() == 1U &&
                    renewed.outbox.front().lease.claim_id ==
                        first->intent.lease.claim_id &&
                    renewed.outbox.front().lease.lease_expires_at_epoch == 121U,
                "dispatch guard fixture did not retain one bounded renewal");

        auto acquired = owner.guard_outbox_claim_for_dispatch_or_throw(
            *first, 102U);
        require(acquired.disposition ==
                    anonsync::SyncReplicaSqliteOutboxDispatchGuardDisposition::Acquired &&
                    acquired.guard != nullptr && acquired.guard->active() &&
                    acquired.guard->observed_epoch() == 102U &&
                    acquired.guard->claim().operation == operation &&
                    acquired.guard->claim().intent == renewed.outbox.front(),
                "dispatch guard did not re-attest the renewed exact claim");
        require_error(
            [&] {
                (void)competing_owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id,
                    first->intent.lease.claim_id, 102U, 1U);
            },
            "locked",
            "competing writer crossed live dispatch claim authority");
        require(acquired.guard->active() &&
                    acquired.guard->claim().intent.lease.claim_id ==
                        first->intent.lease.claim_id,
                "blocked writer revoked or changed live dispatch authority");

        acquired.guard->commit_or_throw();
        require(!acquired.guard->active(),
                "committed dispatch guard remained authoritative");
        require_error(
            [&] { acquired.guard->commit_or_throw(); },
            "is not active",
            "inactive dispatch guard committed a second time");
        const SyncReplicaSqliteSnapshot guarded = owner.snapshot_or_throw();
        require(guarded.outbox == renewed.outbox &&
                    guarded.outbox_time_high_water_epoch == 102U,
                "dispatch guard commit changed claim authority or lost its clock fence");

        require(competing_owner.release_outbox_for_retry_or_throw(
                    destination, operation.operation_id,
                    first->intent.lease.claim_id, 102U, 1U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "writer did not resume after dispatch guard release");
        const SyncReplicaSqliteSnapshot released = owner.snapshot_or_throw();
        auto stale = owner.guard_outbox_claim_for_dispatch_or_throw(
            *first, 103U);
        require(stale.disposition ==
                    anonsync::SyncReplicaSqliteOutboxDispatchGuardDisposition::StaleClaim &&
                    stale.guard == nullptr &&
                    owner.snapshot_or_throw() == released &&
                    released.outbox_time_high_water_epoch == 102U,
                "stale dispatch identity sampled time or changed durable authority");

        const auto second = owner.claim_next_outbox_or_throw(
            "dispatch-worker-2", 103U, 2U, destination);
        require(second.has_value() &&
                    second->intent.lease.dispatch_attempts == 2U &&
                    second->intent.lease.lease_expires_at_epoch == 105U,
                "released dispatch attempt did not mint one fresh claim");
        const SyncReplicaSqliteSnapshot before_expiry = owner.snapshot_or_throw();
        auto expired = owner.guard_outbox_claim_for_dispatch_or_throw(
            *second, 105U);
        const SyncReplicaSqliteSnapshot after_expiry = owner.snapshot_or_throw();
        require(expired.disposition ==
                    anonsync::SyncReplicaSqliteOutboxDispatchGuardDisposition::ExpiredClaim &&
                    expired.guard == nullptr &&
                    after_expiry.state_generation ==
                        before_expiry.state_generation &&
                    after_expiry.durable == before_expiry.durable &&
                    after_expiry.outbox == before_expiry.outbox &&
                    after_expiry.outbox_time_high_water_epoch == 105U &&
                    after_expiry.outbox_clock_digest !=
                        before_expiry.outbox_clock_digest,
                "expired dispatch claim was not revoked by one durable clock-only cutpoint");

        const auto third = owner.claim_next_outbox_or_throw(
            "dispatch-worker-3", 105U, 10U, destination);
        require(third.has_value() &&
                    third->intent.lease.dispatch_attempts == 3U,
                "expired dispatch attempt did not require a third identity");
        require(owner.settle_outbox_or_throw(
                    destination, operation.operation_id,
                    third->intent.lease.claim_id, 106U) ==
                    SyncReplicaSqliteOutboxReceiptResult::Applied,
                "dispatch guard fixture could not settle its third claim");
        const SyncReplicaSqliteSnapshot settled = owner.snapshot_or_throw();
        auto missing = owner.guard_outbox_claim_for_dispatch_or_throw(
            *third, 107U);
        require(missing.disposition ==
                    anonsync::SyncReplicaSqliteOutboxDispatchGuardDisposition::IntentMissing &&
                    missing.guard == nullptr &&
                    owner.snapshot_or_throw() == settled &&
                    settled.outbox_time_high_water_epoch == 106U,
                "missing dispatch intent sampled time or recreated durable state");
    }

    {
        TempDatabasePath file(
            "anonsync-replica-sqlite-owner-dispatch-trigger-guard");
        const std::string folder =
            "folder-sqlite-dispatch-trigger-guard";
        const SyncReplicaActor local =
            actor("device-sqlite-dispatch-trigger-guard", 1442U);
        const std::string destination =
            "device-sqlite-dispatch-trigger-peer";
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U),
            "dispatch trigger guard owner");
        const std::vector<std::string> destinations{destination};
        const SyncReplicaOperation operation = owner.create_local_file_or_throw(
            "dispatch/trigger.bin", 7U, anonsync::sha256_hex("trigger"),
            destinations);
        const auto claim = owner.claim_next_outbox_or_throw(
            "dispatch-trigger-worker", 200U, 10U, destination);
        require(claim.has_value(),
                "dispatch trigger fixture did not mint a claim");
        const SyncReplicaSqliteSnapshot baseline = owner.snapshot_or_throw();

        exec(db,
             "CREATE TEMP TRIGGER silent_dispatch_clock_digest_mutation "
             "AFTER UPDATE ON main.sync_replica_outbox_clock "
             "BEGIN UPDATE main.sync_replica_outbox_clock "
             "SET clock_digest="
             "'0000000000000000000000000000000000000000000000000000000000000000' "
             "WHERE id=NEW.id; END;");
        require_error(
            [&] {
                (void)owner.guard_outbox_claim_for_dispatch_or_throw(
                    *claim, 201U);
            },
            "outbox clock attestation mismatch",
            "TEMP-trigger mutation escaped dispatch staged re-attestation");
        require(owner.snapshot_or_throw() == baseline,
                "failed dispatch re-attestation escaped transaction rollback");
        exec(db, "DROP TRIGGER temp.silent_dispatch_clock_digest_mutation;");

        auto recovered = owner.guard_outbox_claim_for_dispatch_or_throw(
            *claim, 201U);
        require(recovered.disposition ==
                    anonsync::SyncReplicaSqliteOutboxDispatchGuardDisposition::Acquired &&
                    recovered.guard != nullptr && recovered.guard->active() &&
                    recovered.guard->claim().operation == operation,
                "dispatch guard did not recover after removing trigger fault");
        recovered.guard->commit_or_throw();
        const SyncReplicaSqliteSnapshot committed = owner.snapshot_or_throw();
        require(committed.outbox == baseline.outbox &&
                    committed.outbox_time_high_water_epoch == 201U,
                "recovered dispatch guard did not publish only its owned clock fence");
    }
}

void test_concurrent_writers_serialize_local_counter_authority() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-concurrent");
    const std::string folder = "folder-sqlite-concurrent";
    const SyncReplicaActor local = actor("device-sqlite-concurrent", 1451U);
    {
        // Freeze the database profile before the two owner connections race to
        // initialize/use the replica schema.
        SyncSqliteDb profile = open_database(file.path);
    }

    std::barrier start(2);
    std::array<std::exception_ptr, 2> errors{};
    std::array<SyncReplicaOperation, 2> operations{};
    std::array<std::thread, 2> writers;
    for (std::size_t index = 0; index < writers.size(); ++index) {
        writers[index] = std::thread([&, index] {
            try {
                SyncSqliteDb db = open_database(file.path);
                start.arrive_and_wait();
                SyncReplicaSqliteOwner owner(
                    db.db, folder, local, limits(16U),
                    "concurrent writer owner");
                const std::vector<std::string> destinations{
                    "device-sqlite-concurrent-peer-" +
                    std::to_string(index)};
                operations[index] = owner.create_local_file_or_throw(
                    "concurrent/file-" + std::to_string(index) + ".bin",
                    1U, anonsync::sha256_hex(std::to_string(index)),
                    destinations);
            } catch (...) {
                errors[index] = std::current_exception();
            }
        });
    }
    for (std::thread& writer : writers) writer.join();
    for (const std::exception_ptr& error : errors) {
        if (error) std::rethrow_exception(error);
    }

    require(operations[0].operation_id != operations[1].operation_id &&
                operations[0].dot.actor == local &&
                operations[1].dot.actor == local &&
                ((operations[0].dot.counter == 1U &&
                  operations[1].dot.counter == 2U) ||
                 (operations[0].dot.counter == 2U &&
                  operations[1].dot.counter == 1U)),
            "concurrent writers reused or skipped local dot authority");
    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "concurrent recovery owner");
    const SyncReplicaSqliteSnapshot snapshot = owner.snapshot_or_throw();
    require(snapshot.durable.last_local_counter == 2U &&
                snapshot.durable.local_operation_ids.size() == 2U &&
                snapshot.durable.operations.size() == 2U &&
                snapshot.outbox.size() == 2U,
            "serialized concurrent writers did not publish two complete cutpoints");
}

#ifdef __linux__
constexpr std::string_view kReplicaCrashHelper =
    "--anonsync-replica-sqlite-owner-crash-helper-v1";
constexpr std::string_view kReplicaClaimCrashHelper =
    "--anonsync-replica-sqlite-owner-claim-crash-helper-v2";
constexpr std::string_view kReplicaRenewCrashHelper =
    "--anonsync-replica-sqlite-owner-renew-crash-helper-v1";
constexpr std::string_view kReplicaClockCrashHelper =
    "--anonsync-replica-sqlite-owner-clock-crash-helper-v1";
constexpr std::string_view kReplicaCrashFolder = "folder-sqlite-crash";
constexpr std::string_view kReplicaCrashDevice = "device-sqlite-crash";
constexpr std::uint64_t kReplicaCrashEpoch = 1501U;
constexpr std::string_view kReplicaClaimCrashFolder =
    "folder-sqlite-claim-crash";
constexpr std::string_view kReplicaClaimCrashDevice =
    "device-sqlite-claim-crash";
constexpr std::string_view kReplicaClaimCrashDestination =
    "device-sqlite-claim-crash-peer";
constexpr std::uint64_t kReplicaClaimCrashEpoch = 1511U;
constexpr std::string_view kReplicaRenewCrashFolder =
    "folder-sqlite-renew-crash";
constexpr std::string_view kReplicaRenewCrashDevice =
    "device-sqlite-renew-crash";
constexpr std::string_view kReplicaRenewCrashDestination =
    "device-sqlite-renew-crash-peer";
constexpr std::uint64_t kReplicaRenewCrashEpoch = 1521U;
constexpr std::string_view kReplicaClockCrashFolder =
    "folder-sqlite-clock-crash";
constexpr std::string_view kReplicaClockCrashDevice =
    "device-sqlite-clock-crash";
constexpr std::uint64_t kReplicaClockCrashEpoch = 1531U;

void crash_after_outbox_insert(
    void*, int operation, const char*, const char* table_name,
    sqlite3_int64) {
    if (operation == SQLITE_INSERT && table_name != nullptr &&
        std::strcmp(table_name, "sync_replica_outbox") == 0) {
        ::_exit(73);
    }
}

int run_replica_crash_helper(int argc, char** argv) {
    try {
        anonsync::test::verify_self_exec_child_boundary_or_throw();
        if (argc != 3 || argv == nullptr || argv[1] == nullptr ||
            argv[2] == nullptr || std::string_view(argv[1]) != kReplicaCrashHelper) {
            throw std::runtime_error(
                "invalid replica SQLite crash helper instruction");
        }
        const std::filesystem::path database_path(argv[2]);
        const std::string filename = database_path.filename().string();
        if (!database_path.is_absolute() ||
            database_path != database_path.lexically_normal() ||
            database_path.extension() != ".sqlite3" ||
            filename.rfind("anonsync-replica-sqlite-owner-crash-", 0) != 0) {
            throw std::runtime_error(
                "replica SQLite crash helper path binding failed");
        }

        SyncSqliteDb db = open_database(database_path);
        SyncReplicaSqliteOwner owner(
            db.db, std::string(kReplicaCrashFolder),
            actor(std::string(kReplicaCrashDevice), kReplicaCrashEpoch),
            limits(16U), "crash self-exec owner");
        auto borrow = db.db.borrow();
        sqlite3_update_hook(
            borrow.get(), &crash_after_outbox_insert, nullptr);
        const std::vector<std::string> destinations{
            "device-sqlite-crash-peer"};
        (void)owner.create_local_file_or_throw(
            "crash/file.bin", 5U, anonsync::sha256_hex("crash"),
            destinations);
        return 75;
    } catch (const std::exception& error) {
        std::cerr << "replica SQLite crash helper failed: "
                  << error.what() << '\n';
        return 74;
    }
}


void crash_after_outbox_lease_update(
    void*, int operation, const char*, const char* table_name,
    sqlite3_int64) {
    if (operation == SQLITE_UPDATE && table_name != nullptr &&
        std::strcmp(table_name, "sync_replica_outbox") == 0) {
        ::_exit(76);
    }
}

int run_replica_claim_crash_helper(int argc, char** argv) {
    try {
        anonsync::test::verify_self_exec_child_boundary_or_throw();
        if (argc != 3 || argv == nullptr || argv[1] == nullptr ||
            argv[2] == nullptr ||
            std::string_view(argv[1]) != kReplicaClaimCrashHelper) {
            throw std::runtime_error(
                "invalid replica SQLite claim crash helper instruction");
        }
        const std::filesystem::path database_path(argv[2]);
        const std::string filename = database_path.filename().string();
        if (!database_path.is_absolute() ||
            database_path != database_path.lexically_normal() ||
            database_path.extension() != ".sqlite3" ||
            filename.rfind("anonsync-replica-sqlite-owner-crash-", 0) != 0) {
            throw std::runtime_error(
                "replica SQLite claim crash helper path binding failed");
        }

        SyncSqliteDb db = open_database(database_path);
        SyncReplicaSqliteOwner owner(
            db.db, std::string(kReplicaClaimCrashFolder),
            actor(std::string(kReplicaClaimCrashDevice),
                  kReplicaClaimCrashEpoch),
            limits(16U), "claim crash self-exec owner");
        auto borrow = db.db.borrow();
        sqlite3_update_hook(
            borrow.get(), &crash_after_outbox_lease_update, nullptr);
        (void)owner.claim_next_outbox_or_throw(
            "worker-claim-crash", 500U, 30U,
            std::string(kReplicaClaimCrashDestination));
        return 78;
    } catch (const std::exception& error) {
        std::cerr << "replica SQLite claim crash helper failed: "
                  << error.what() << '\n';
        return 77;
    }
}

int run_replica_renew_crash_helper(int argc, char** argv) {
    try {
        anonsync::test::verify_self_exec_child_boundary_or_throw();
        if (argc != 3 || argv == nullptr || argv[1] == nullptr ||
            argv[2] == nullptr ||
            std::string_view(argv[1]) != kReplicaRenewCrashHelper) {
            throw std::runtime_error(
                "invalid replica SQLite renewal crash helper instruction");
        }
        const std::filesystem::path database_path(argv[2]);
        const std::string filename = database_path.filename().string();
        if (!database_path.is_absolute() ||
            database_path != database_path.lexically_normal() ||
            database_path.extension() != ".sqlite3" ||
            filename.rfind("anonsync-replica-sqlite-owner-crash-", 0) != 0) {
            throw std::runtime_error(
                "replica SQLite renewal crash helper path binding failed");
        }

        SyncSqliteDb db = open_database(database_path);
        SyncReplicaSqliteOwner owner(
            db.db, std::string(kReplicaRenewCrashFolder),
            actor(std::string(kReplicaRenewCrashDevice),
                  kReplicaRenewCrashEpoch),
            limits(16U), "renewal crash self-exec owner");
        const SyncReplicaSqliteSnapshot snapshot = owner.snapshot_or_throw();
        if (snapshot.outbox.size() != 1U ||
            snapshot.outbox.front().destination_device_id !=
                kReplicaRenewCrashDestination ||
            snapshot.outbox.front().lease.claim_id.empty()) {
            throw std::runtime_error(
                "replica SQLite renewal crash fixture is not one active claim");
        }
        auto borrow = db.db.borrow();
        sqlite3_update_hook(
            borrow.get(), &crash_after_outbox_lease_update, nullptr);
        (void)owner.renew_outbox_lease_or_throw(
            std::string(kReplicaRenewCrashDestination),
            snapshot.outbox.front().operation_id,
            snapshot.outbox.front().lease.claim_id, 505U, 30U);
        return 80;
    } catch (const std::exception& error) {
        std::cerr << "replica SQLite renewal crash helper failed: "
                  << error.what() << '\n';
        return 79;
    }
}


void crash_after_outbox_clock_update(
    void*, int operation, const char*, const char* table_name,
    sqlite3_int64) {
    if (operation == SQLITE_UPDATE && table_name != nullptr &&
        std::strcmp(table_name, "sync_replica_outbox_clock") == 0) {
        ::_exit(82);
    }
}

int run_replica_clock_crash_helper(int argc, char** argv) {
    try {
        anonsync::test::verify_self_exec_child_boundary_or_throw();
        if (argc != 3 || argv == nullptr || argv[1] == nullptr ||
            argv[2] == nullptr ||
            std::string_view(argv[1]) != kReplicaClockCrashHelper) {
            throw std::runtime_error(
                "invalid replica SQLite clock crash helper instruction");
        }
        const std::filesystem::path database_path(argv[2]);
        const std::string filename = database_path.filename().string();
        if (!database_path.is_absolute() ||
            database_path != database_path.lexically_normal() ||
            database_path.extension() != ".sqlite3" ||
            filename.rfind("anonsync-replica-sqlite-owner-crash-", 0) != 0) {
            throw std::runtime_error(
                "replica SQLite clock crash helper path binding failed");
        }

        SyncSqliteDb db = open_database(database_path);
        SyncReplicaSqliteOwner owner(
            db.db, std::string(kReplicaClockCrashFolder),
            actor(std::string(kReplicaClockCrashDevice),
                  kReplicaClockCrashEpoch),
            limits(16U), "clock crash self-exec owner");
        auto borrow = db.db.borrow();
        sqlite3_update_hook(
            borrow.get(), &crash_after_outbox_clock_update, nullptr);
        (void)owner.claim_next_outbox_or_throw(
            "worker-clock-crash", 500U, 30U);
        return 84;
    } catch (const std::exception& error) {
        std::cerr << "replica SQLite clock crash helper failed: "
                  << error.what() << '\n';
        return 83;
    }
}

void test_process_crash_before_commit_recovers_old_generation() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-crash");
    const std::string folder(kReplicaCrashFolder);
    const SyncReplicaActor local =
        actor(std::string(kReplicaCrashDevice), kReplicaCrashEpoch);
    SyncReplicaSqliteSnapshot baseline;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "crash seed owner");
        baseline = owner.snapshot_or_throw();
    }

    anonsync::test::SelfExecTestProcess child =
        anonsync::test::spawn_self_exec_test_process_or_throw(
            anonsync::test::current_self_executable_or_throw(),
            {std::string(kReplicaCrashHelper), file.path.string()});
    child.wait_for_exact_exit(
        73, std::chrono::seconds(10),
        "replica SQLite post-outbox pre-commit crash helper");
    require(true,
            "child crashed at the intended post-outbox/pre-commit frontier");

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "crash recovery owner");
    require(owner.snapshot_or_throw() == baseline &&
                scalar_count(db, "sync_replica_operations") == 0U &&
                scalar_count(db, "sync_replica_outbox") == 0U,
            "SQLite recovery exposed a transaction prefix after process death");

}

void test_process_crash_during_claim_recovers_unclaimed_cutpoint() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-crash-claim");
    const std::string folder(kReplicaClaimCrashFolder);
    const SyncReplicaActor local = actor(
        std::string(kReplicaClaimCrashDevice), kReplicaClaimCrashEpoch);
    const std::string destination(kReplicaClaimCrashDestination);
    SyncReplicaSqliteSnapshot baseline;
    SyncReplicaOperation operation;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "claim crash seed owner");
        operation = owner.create_local_file_or_throw(
            "crash/claim.bin", 6U, anonsync::sha256_hex("claim-crash"),
            std::vector<std::string>{destination});
        baseline = owner.snapshot_or_throw();
        require(baseline.state_generation == 2U &&
                    baseline.outbox.size() == 1U &&
                    baseline.outbox.front().lease ==
                        anonsync::SyncReplicaOutboxLeaseState{},
                "claim crash seed did not publish one unclaimed intent");
    }

    anonsync::test::SelfExecTestProcess child =
        anonsync::test::spawn_self_exec_test_process_or_throw(
            anonsync::test::current_self_executable_or_throw(),
            {std::string(kReplicaClaimCrashHelper), file.path.string()});
    child.wait_for_exact_exit(
        76, std::chrono::seconds(10),
        "replica SQLite post-lease-update pre-commit crash helper");
    require(true,
            "child crashed at the intended post-lease-update/pre-commit frontier");

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "claim crash recovery owner");
    require(owner.snapshot_or_throw() == baseline &&
                scalar_count(db, "sync_replica_operations") == 1U &&
                scalar_count(db, "sync_replica_outbox") == 1U,
            "SQLite recovery exposed a partial receipt after process death");
    const auto recovered_claim = owner.claim_next_outbox_or_throw(
        "worker-claim-recovery", 500U, 30U, destination);
    require(recovered_claim.has_value() &&
                recovered_claim->operation == operation &&
                recovered_claim->intent.lease.dispatch_attempts == 1U,
            "rolled-back claim consumed attempt authority or stranded the intent");
}
void test_process_crash_during_clock_only_publication_recovers_old_fence() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-crash-clock");
    const std::string folder(kReplicaClockCrashFolder);
    const SyncReplicaActor local = actor(
        std::string(kReplicaClockCrashDevice), kReplicaClockCrashEpoch);
    SyncReplicaSqliteSnapshot baseline;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "clock crash seed owner");
        baseline = owner.snapshot_or_throw();
        require(baseline.state_generation == 1U &&
                    baseline.outbox.empty() &&
                    baseline.outbox_time_high_water_epoch == 0U,
                "clock crash seed was not one empty zero-fence cutpoint");
    }

    anonsync::test::SelfExecTestProcess child =
        anonsync::test::spawn_self_exec_test_process_or_throw(
            anonsync::test::current_self_executable_or_throw(),
            {std::string(kReplicaClockCrashHelper), file.path.string()});
    child.wait_for_exact_exit(
        82, std::chrono::seconds(10),
        "replica SQLite post-clock-update pre-commit crash helper");
    require(true,
            "child crashed at the intended post-clock-update/pre-commit frontier");

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "clock crash recovery owner");
    require(owner.snapshot_or_throw() == baseline,
            "SQLite recovery exposed a partial durable clock observation");
    require(!owner.claim_next_outbox_or_throw(
                 "worker-clock-recovery", 500U, 30U)
                 .has_value(),
            "empty recovered outbox unexpectedly returned a claim");
    const SyncReplicaSqliteSnapshot observed = owner.snapshot_or_throw();
    require(observed.state_generation == baseline.state_generation &&
                observed.outbox.empty() &&
                observed.outbox_time_high_water_epoch == 500U,
            "recovered clock-only publication did not retry atomically");
}

void test_process_crash_during_renewal_recovers_prior_deadline() {
    TempDatabasePath file("anonsync-replica-sqlite-owner-crash-renew");
    const std::string folder(kReplicaRenewCrashFolder);
    const SyncReplicaActor local = actor(
        std::string(kReplicaRenewCrashDevice), kReplicaRenewCrashEpoch);
    const std::string destination(kReplicaRenewCrashDestination);
    SyncReplicaSqliteSnapshot baseline;
    SyncReplicaOperation operation;
    {
        SyncSqliteDb db = open_database(file.path);
        SyncReplicaSqliteOwner owner(
            db.db, folder, local, limits(16U), "renewal crash seed owner");
        operation = owner.create_local_file_or_throw(
            "crash/renew.bin", 7U, anonsync::sha256_hex("renew-crash"),
            std::vector<std::string>{destination});
        const auto claim = owner.claim_next_outbox_or_throw(
            "worker-renew-crash", 500U, 10U, destination);
        require(claim.has_value() &&
                    claim->intent.lease.lease_expires_at_epoch == 510U,
                "renewal crash seed did not publish one active claim");
        baseline = owner.snapshot_or_throw();
    }

    anonsync::test::SelfExecTestProcess child =
        anonsync::test::spawn_self_exec_test_process_or_throw(
            anonsync::test::current_self_executable_or_throw(),
            {std::string(kReplicaRenewCrashHelper), file.path.string()});
    child.wait_for_exact_exit(
        76, std::chrono::seconds(10),
        "replica SQLite post-heartbeat-update pre-commit crash helper");
    require(true,
            "child crashed at the intended post-heartbeat-update/pre-commit frontier");

    SyncSqliteDb db = open_database(file.path);
    SyncReplicaSqliteOwner owner(
        db.db, folder, local, limits(16U), "renewal crash recovery owner");
    require(owner.snapshot_or_throw() == baseline,
            "SQLite recovery exposed a partial renewed deadline");
    const auto& intent = baseline.outbox.front();
    require(owner.renew_outbox_lease_or_throw(
                destination, operation.operation_id,
                intent.lease.claim_id, 505U, 30U) ==
                SyncReplicaSqliteOutboxReceiptResult::Applied,
            "rolled-back heartbeat stranded live renewal authority");
    const SyncReplicaSqliteSnapshot renewed = owner.snapshot_or_throw();
    require(renewed.state_generation == baseline.state_generation + 1U &&
                renewed.outbox.size() == 1U &&
                renewed.outbox.front().lease.claim_id ==
                    intent.lease.claim_id &&
                renewed.outbox.front().lease.lease_expires_at_epoch == 535U,
            "recovered heartbeat did not publish one exact renewed cutpoint");
}

#endif

}  // namespace

int main(int argc, char** argv) {
#ifdef __linux__
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr &&
        std::string_view(argv[1]) == kReplicaCrashHelper) {
        return run_replica_crash_helper(argc, argv);
    }
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr &&
        std::string_view(argv[1]) == kReplicaClaimCrashHelper) {
        return run_replica_claim_crash_helper(argc, argv);
    }
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr &&
        std::string_view(argv[1]) == kReplicaRenewCrashHelper) {
        return run_replica_renew_crash_helper(argc, argv);
    }
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr &&
        std::string_view(argv[1]) == kReplicaClockCrashHelper) {
        return run_replica_clock_crash_helper(argc, argv);
    }
#endif
    try {
        if (argc != 1) {
            throw std::runtime_error(
                "unexpected sync replica SQLite owner test arguments");
        }
        test_exact_v1_migration_preserves_evidence_and_outbox();
        test_malformed_v1_is_not_laundered_into_v5();
        test_exact_v2_migration_preserves_live_receipt_and_seeds_clock();
        test_unreachable_v2_lease_is_not_laundered_into_v5();
        test_exact_v3_migration_preserves_clock_and_marks_retry_gap();
        test_exact_v4_migration_preserves_retry_provenance_and_quarantines_clock();
        test_malformed_v4_provenance_is_not_laundered_into_v5();
        test_atomic_local_publication_and_single_copy_outbox();
        test_delivery_payload_inventory_validation_precedes_claim_authority();
        test_receipt_bound_reclaim_backoff_and_restart();
        test_claim_precommit_reattestation_and_lease_tamper();
        test_concurrent_claimers_mint_one_receipt();
        test_durable_capacity_policy_and_retry();
        test_projection_and_redundant_attestation();
        test_transaction_failure_rolls_back_entire_cutpoint();
        test_schema_contract_and_outbox_tamper_detection();
        test_retry_release_provenance_tamper_and_precommit_guard();
        test_exact_schema_attachment_and_precommit_reattestation();
        test_unknown_clock_capability_is_durably_quarantined();
        test_outbox_clock_precommit_reattestation_and_tamper();
        test_explicit_clock_observation_and_recovery_preserve_replica_authority();
        test_clock_sampling_is_inside_writer_transaction();
        test_local_authority_mapping_digest();
        test_pending_dependency_restart_and_activation();
        test_outbox_budget_precedes_local_mint();
        test_projection_guard_serializes_external_effect_cutpoint();
        test_outbox_dispatch_guard_reattests_and_serializes_claim();
        test_concurrent_writers_serialize_local_counter_authority();
#ifdef __linux__
        test_process_crash_before_commit_recovers_old_generation();
        test_process_crash_during_claim_recovers_unclaimed_cutpoint();
        test_process_crash_during_clock_only_publication_recovers_old_fence();
        test_process_crash_during_renewal_recovers_prior_deadline();
#endif
        std::cout << "sync replica SQLite owner tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica SQLite owner tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
