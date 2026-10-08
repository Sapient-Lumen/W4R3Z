#include "sync_sqlite_sidecar_claimed_path_snapshot.hpp"

#include "sync_manifest_validation.hpp"

#include <limits>
#include <stdexcept>
#include <utility>

#include <sqlite3.h>

namespace anonsync {
namespace {

inline constexpr std::uint64_t kSidecarLookupKeyMaxBytes = 256U;

persistence::SqliteVerificationBudgetPolicy execution_policy_or_throw(
    const SyncSqliteSidecarSnapshotExecutionLimits& limits) {
    persistence::SqliteVerificationBudgetPolicy policy;
    policy.maximum_progress_callbacks = limits.maximum_progress_callbacks;
    policy.progress_opcode_interval = limits.progress_opcode_interval;
    policy.maximum_elapsed_milliseconds =
        limits.maximum_elapsed_milliseconds;
    return policy;
}

void reset_and_clear_or_throw(sqlite3_stmt* stmt, const std::string& label) {
    const int reset_rc = sqlite3_reset(stmt);
    if (reset_rc != SQLITE_OK) {
        throw_sqlite_exception(
            sqlite3_db_handle(stmt), reset_rc, label + " reset");
    }
    const int clear_rc = sqlite3_clear_bindings(stmt);
    if (clear_rc != SQLITE_OK) {
        throw_sqlite_exception(
            sqlite3_db_handle(stmt), clear_rc, label + " clear bindings");
    }
}

void reset_and_clear_noexcept(sqlite3_stmt* stmt) noexcept {
    if (stmt == nullptr) return;
    (void)sqlite3_reset(stmt);
    (void)sqlite3_clear_bindings(stmt);
}

void require_bounded_lookup_key(
    const std::string& value,
    const std::string& field,
    const std::string& label) {
    if (value.empty()) {
        throw std::runtime_error(label + " " + field + " is required");
    }
    if (value.size() > kSidecarLookupKeyMaxBytes) {
        throw std::runtime_error(
            label + " " + field + " exceeds its byte limit");
    }
}

void validate_limits_or_throw(
    const SyncSqliteSidecarClaimedPathLimits& limits,
    const std::string& label) {
    if (limits.max_paths == 0 || limits.max_total_path_bytes == 0) {
        throw std::runtime_error(
            label + " claimed-path limits must be positive");
    }
    constexpr std::uint64_t sqlite_i64_max =
        static_cast<std::uint64_t>(
            std::numeric_limits<sqlite3_int64>::max());
    if (limits.max_paths >= sqlite_i64_max) {
        throw std::runtime_error(
            label + " claimed-path row limit cannot form a SQLite sentinel");
    }
}

}  // namespace

SyncSqliteSidecarLockWaitBudgetException::
SyncSqliteSidecarLockWaitBudgetException(
    const std::string& label,
    const persistence::SqliteBusyHandlerSnapshot& snapshot,
    std::uint64_t limit)
    : std::runtime_error(
          label +
          " sqlite_sidecar_lock_wait_budget[lock_wait_limit] exhausted: " +
          std::to_string(snapshot.invocations) + " busy callbacks, " +
          std::to_string(snapshot.authorized_sleep_milliseconds) +
          " authorized sleep milliseconds, " +
          std::to_string(snapshot.sleep_milliseconds) +
          " observed sleep milliseconds, limit " + std::to_string(limit)),
      invocations_(snapshot.invocations),
      authorized_sleep_milliseconds_(
          snapshot.authorized_sleep_milliseconds),
      observed_sleep_milliseconds_(snapshot.sleep_milliseconds),
      limit_(limit) {}

std::uint64_t SyncSqliteSidecarLockWaitBudgetException::invocations() const
    noexcept {
    return invocations_;
}

std::uint64_t
SyncSqliteSidecarLockWaitBudgetException::authorized_sleep_milliseconds() const
    noexcept {
    return authorized_sleep_milliseconds_;
}

std::uint64_t
SyncSqliteSidecarLockWaitBudgetException::observed_sleep_milliseconds() const
    noexcept {
    return observed_sleep_milliseconds_;
}

std::uint64_t SyncSqliteSidecarLockWaitBudgetException::limit() const noexcept {
    return limit_;
}

SyncSqliteSidecarLockWaitBudget::SyncSqliteSidecarLockWaitBudget(
    SyncSqliteDbHandleSlot& db,
    const SyncSqliteSidecarLockWaitLimits& limits,
    const std::string& label)
    : SyncSqliteSidecarLockWaitBudget(
          borrow_sync_sqlite_serialized_db_or_throw(
              db, label + " exact lock-wait database generation"),
          limits,
          label,
          FrozenBorrowTag{}) {}

SyncSqliteSidecarLockWaitBudget::SyncSqliteSidecarLockWaitBudget(
    SyncSqliteSerializedDbBorrow database_borrow,
    const SyncSqliteSidecarLockWaitLimits& limits,
    const std::string& label,
    FrozenBorrowTag)
    : database_(database_borrow.get()),
      database_owner_generation_(database_borrow.generation()),
      maximum_lock_wait_milliseconds_(
          limits.maximum_lock_wait_milliseconds),
      label_(label),
      budget_(std::move(database_borrow),
              limits.maximum_lock_wait_milliseconds,
              label) {
    if (database_ == nullptr || database_owner_generation_ == 0) {
        throw std::logic_error(
            label + " could not freeze an exact SQLite lock-wait generation");
    }
}

void SyncSqliteSidecarLockWaitBudget::require_authorizes_or_throw(
    sqlite3* database,
    std::uint64_t database_owner_generation,
    const std::string& label) {
    // snapshot() is also the process-incarnation fence before ordinary adapter
    // state is observed.
    (void)budget_.snapshot();
    if (!attached_) {
        throw std::runtime_error(
            label + " sidecar lock-wait budget is detached");
    }
    if (database == nullptr || database != database_ ||
        database_owner_generation == 0 ||
        database_owner_generation != database_owner_generation_) {
        throw std::runtime_error(
            label + " requires the exact sidecar lock-wait generation");
    }
}

void SyncSqliteSidecarLockWaitBudget::throw_if_exhausted() const {
    const persistence::SqliteBusyHandlerSnapshot observed = budget_.snapshot();
    if (observed.timeout_exhausted) {
        throw SyncSqliteSidecarLockWaitBudgetException(
            label_, observed, maximum_lock_wait_milliseconds_);
    }
}

void SyncSqliteSidecarLockWaitBudget::detach() noexcept {
    budget_.detach();
    attached_ = false;
}

std::uint64_t SyncSqliteSidecarLockWaitBudget::owner_generation() const
    noexcept {
    (void)budget_.snapshot();
    return database_owner_generation_;
}

persistence::SqliteBusyHandlerSnapshot
SyncSqliteSidecarLockWaitBudget::snapshot() const noexcept {
    return budget_.snapshot();
}

SyncSqliteSidecarSnapshotExecutionBudget::
SyncSqliteSidecarSnapshotExecutionBudget(
    SyncSqliteDbHandleSlot& db,
    const SyncSqliteSidecarSnapshotExecutionLimits& limits,
    const std::string& label)
    : SyncSqliteSidecarSnapshotExecutionBudget(
          borrow_sync_sqlite_serialized_db_or_throw(
              db, label + " exact database generation"),
          limits,
          label,
          FrozenBorrowTag{}) {}

SyncSqliteSidecarSnapshotExecutionBudget::
SyncSqliteSidecarSnapshotExecutionBudget(
    SyncSqliteSerializedDbBorrow database_borrow,
    const SyncSqliteSidecarSnapshotExecutionLimits& limits,
    const std::string& label,
    FrozenBorrowTag)
    : database_(database_borrow.get()),
      database_owner_generation_(database_borrow.generation()),
      budget_(std::move(database_borrow),
              label,
              execution_policy_or_throw(limits)) {
    if (database_ == nullptr || database_owner_generation_ == 0) {
        throw std::logic_error(
            label + " could not freeze an exact SQLite database generation");
    }
}

void SyncSqliteSidecarSnapshotExecutionBudget::require_authorizes_or_throw(
    sqlite3* database,
    std::uint64_t database_owner_generation,
    const std::string& label) {
    // Fence process/thread authority before reading the adapter's ordinary
    // state. Detachment is a one-way revocation: retaining the frozen pointer
    // and generation for diagnostics must never authorize callback-free work.
    (void)budget_.progress_callbacks();
    if (!attached_) {
        throw std::runtime_error(
            label + " sidecar snapshot execution budget is detached");
    }
    budget_.checkpoint();
    if (database == nullptr || database != database_ ||
        database_owner_generation == 0 ||
        database_owner_generation != database_owner_generation_) {
        throw std::runtime_error(
            label +
            " requires the exact sidecar snapshot execution-budget generation");
    }
}

void SyncSqliteSidecarSnapshotExecutionBudget::checkpoint() {
    (void)budget_.progress_callbacks();
    if (!attached_) {
        throw std::runtime_error(
            "sidecar snapshot execution budget is detached");
    }
    budget_.checkpoint();
}

void SyncSqliteSidecarSnapshotExecutionBudget::throw_if_exhausted() const {
    budget_.throw_if_exhausted();
}

void SyncSqliteSidecarSnapshotExecutionBudget::detach() noexcept {
    budget_.detach();
    attached_ = false;
}

std::uint64_t
SyncSqliteSidecarSnapshotExecutionBudget::owner_generation() const noexcept {
    (void)budget_.progress_callbacks();
    return database_owner_generation_;
}

std::uint64_t
SyncSqliteSidecarSnapshotExecutionBudget::progress_callbacks() const noexcept {
    return budget_.progress_callbacks();
}

SyncSqliteSidecarClaimedPathSnapshotReader::
SyncSqliteSidecarClaimedPathSnapshotReader(
    SyncSqliteDbHandleSlot& db,
    const std::string& label)
    : claimed_path_query_(sqlite_prepare_or_throw(
          db,
          "SELECT DISTINCT path COLLATE BINARY "
          "FROM main.sync_session_resume_transfer_workorders "
          "WHERE session_id COLLATE BINARY=? "
          "AND worker_id COLLATE BINARY=? "
          "AND worker_lease_id COLLATE BINARY=? "
          "AND work_state COLLATE BINARY='claimed' "
          "ORDER BY path COLLATE BINARY LIMIT ?;",
          label + " claimed-path snapshot prepare")) {}

SyncSqliteSidecarClaimedPathSnapshot
SyncSqliteSidecarClaimedPathSnapshotReader::load_or_throw(
    const SyncSqliteTransactionAuthority& transaction_authority,
    SyncSqliteSidecarSnapshotExecutionBudget& execution_budget,
    const std::string& session_id,
    const std::string& worker_id,
    const std::string& worker_lease_id,
    const SyncSqliteSidecarClaimedPathLimits& limits,
    const std::string& label) {
    validate_limits_or_throw(limits, label);
    if (!sync_id_is_valid(session_id)) {
        throw std::runtime_error(label + " session id is invalid");
    }
    require_bounded_lookup_key(worker_id, "worker id", label);
    require_bounded_lookup_key(worker_lease_id, "worker lease id", label);

    sqlite3_stmt* const statement = claimed_path_query_.stmt.get();
    sqlite3* const database = sqlite3_db_handle(statement);
    if (database == nullptr ||
        !transaction_authority.authorizes(database)) {
        throw std::runtime_error(
            label + " requires the exact live SQLite transaction authority");
    }
    execution_budget.require_authorizes_or_throw(
        database, owner_generation(), label);

    SyncSqliteSidecarClaimedPathSnapshot snapshot;
    snapshot.database_owner_generation = owner_generation();
    const std::uint64_t sql_row_sentinel = limits.max_paths + 1U;

    try {
        sqlite_bind_text_or_throw(
            statement, 1, session_id, label + " session id");
        sqlite_bind_text_or_throw(
            statement, 2, worker_id, label + " worker id");
        sqlite_bind_text_or_throw(
            statement, 3, worker_lease_id, label + " worker lease id");
        sqlite_bind_u64_or_throw(
            statement, 4, sql_row_sentinel, label + " row sentinel");

        while (true) {
            const int rc = sqlite3_step(statement);
            if (rc != SQLITE_DONE && rc != SQLITE_ROW) {
                execution_budget.throw_if_exhausted();
                throw_sqlite_exception(
                    database, rc, label + " claimed-path snapshot step");
            }
            execution_budget.checkpoint();
            if (rc == SQLITE_DONE) break;
            if (snapshot.path_count == limits.max_paths) {
                throw std::runtime_error(
                    label + " claimed-path row count exceeds its limit");
            }

            std::string raw_path = sqlite_column_text_or_throw(
                statement,
                0,
                kSyncManifestRelativePathMaxBytes,
                label + " claimed path");
            NormalizedSyncPath normalized;
            const SyncValidationResult path_result =
                normalize_sync_relative_path(raw_path, normalized);
            if (!path_result.ok) {
                throw std::runtime_error(
                    label + " stored claimed path is invalid: " +
                    path_result.reason);
            }
            if (!snapshot.paths.empty() &&
                normalized.value.compare(snapshot.paths.back().value) <= 0) {
                throw std::runtime_error(
                    label +
                    " claimed paths are not unique and strictly ordered");
            }
            if (normalized.value.size() >
                std::numeric_limits<std::uint64_t>::max() -
                    snapshot.total_path_bytes) {
                throw std::runtime_error(
                    label + " claimed-path bytes overflow uint64");
            }
            snapshot.total_path_bytes +=
                static_cast<std::uint64_t>(normalized.value.size());
            if (snapshot.total_path_bytes >
                limits.max_total_path_bytes) {
                throw std::runtime_error(
                    label + " claimed-path bytes exceed their limit");
            }

            snapshot.paths.push_back(std::move(normalized));
            ++snapshot.path_count;
        }

        execution_budget.require_authorizes_or_throw(
            database, owner_generation(), label);
        if (!transaction_authority.authorizes_snapshot(database)) {
            throw std::runtime_error(
                label +
                " claimed-path query did not establish the authorized main snapshot");
        }
        if (snapshot.path_count !=
            static_cast<std::uint64_t>(snapshot.paths.size())) {
            throw std::logic_error(
                label + " claimed-path snapshot accounting mismatch");
        }
        reset_and_clear_or_throw(statement, label + " claimed-path snapshot");
        return snapshot;
    } catch (...) {
        reset_and_clear_noexcept(statement);
        throw;
    }
}

std::uint64_t
SyncSqliteSidecarClaimedPathSnapshotReader::owner_generation() const noexcept {
    return claimed_path_query_.owner_generation();
}

}  // namespace anonsync
