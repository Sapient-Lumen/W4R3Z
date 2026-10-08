#pragma once

#include "anonsync_core.hpp"
#include "persistence/sqlite_busy_handler_owner.hpp"
#include "sqlite_verification_budget.hpp"
#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace anonsync {

struct SyncSqliteSidecarClaimedPathLimits final {
    std::uint64_t max_paths = 0;
    std::uint64_t max_total_path_bytes = 0;
};

// Cooperative execution authority for one sidecar snapshot transaction.
// SQLite invokes the progress callback after approximately
// progress_opcode_interval virtual-machine instructions. The callback count
// and monotonic elapsed ceiling are independent so a caller may tighten either
// dimension without widening the reviewed generic verifier ceilings.
struct SyncSqliteSidecarSnapshotExecutionLimits final {
    std::uint64_t maximum_progress_callbacks = 0;
    std::uint32_t progress_opcode_interval = 0;
    std::uint64_t maximum_elapsed_milliseconds = 0;
};

// Lock waiting is deliberately separate from cooperative SQLite VM execution:
// a blocked connection does not invoke the progress handler. This value caps
// cumulative sqlite3_sleep() requests rather than wall-clock scheduler delay.
// Zero is valid and means fail fast on the first lock conflict.
struct SyncSqliteSidecarLockWaitLimits final {
    std::uint64_t maximum_lock_wait_milliseconds = 0;
};

class SyncSqliteSidecarLockWaitBudgetException final
    : public std::runtime_error {
public:
    SyncSqliteSidecarLockWaitBudgetException(
        const std::string& label,
        const persistence::SqliteBusyHandlerSnapshot& snapshot,
        std::uint64_t limit);

    [[nodiscard]] std::uint64_t invocations() const noexcept;
    [[nodiscard]] std::uint64_t authorized_sleep_milliseconds() const noexcept;
    [[nodiscard]] std::uint64_t observed_sleep_milliseconds() const noexcept;
    [[nodiscard]] std::uint64_t limit() const noexcept;

private:
    std::uint64_t invocations_ = 0;
    std::uint64_t authorized_sleep_milliseconds_ = 0;
    std::uint64_t observed_sleep_milliseconds_ = 0;
    std::uint64_t limit_ = 0;
};

// Purpose-specific exact-generation owner for one complete sidecar read
// transaction. It must be declared before the transaction guard so its busy
// callback remains live through begin, every statement, commit, and any
// failure-path rollback. The younger progress owner still detaches before
// transaction cleanup. Every locking event consumes the same lifetime budget.
class SyncSqliteSidecarLockWaitBudget final {
public:
    SyncSqliteSidecarLockWaitBudget(
        SyncSqliteDbHandleSlot& db,
        const SyncSqliteSidecarLockWaitLimits& limits,
        const std::string& label);
    ~SyncSqliteSidecarLockWaitBudget() = default;

    SyncSqliteSidecarLockWaitBudget(
        const SyncSqliteSidecarLockWaitBudget&) = delete;
    SyncSqliteSidecarLockWaitBudget& operator=(
        const SyncSqliteSidecarLockWaitBudget&) = delete;
    SyncSqliteSidecarLockWaitBudget(
        SyncSqliteSidecarLockWaitBudget&&) = delete;
    SyncSqliteSidecarLockWaitBudget& operator=(
        SyncSqliteSidecarLockWaitBudget&&) = delete;

    void require_authorizes_or_throw(
        sqlite3* database,
        std::uint64_t database_owner_generation,
        const std::string& label);
    void throw_if_exhausted() const;
    void detach() noexcept;

    [[nodiscard]] std::uint64_t owner_generation() const noexcept;
    [[nodiscard]] persistence::SqliteBusyHandlerSnapshot snapshot() const
        noexcept;

private:
    struct FrozenBorrowTag final {};

    SyncSqliteSidecarLockWaitBudget(
        SyncSqliteSerializedDbBorrow database_borrow,
        const SyncSqliteSidecarLockWaitLimits& limits,
        const std::string& label,
        FrozenBorrowTag);

    sqlite3* database_ = nullptr;
    std::uint64_t database_owner_generation_ = 0;
    std::uint64_t maximum_lock_wait_milliseconds_ = 0;
    std::string label_;
    persistence::SqliteBusyHandlerOwner budget_;
    bool attached_ = true;
};

// Purpose-specific adapter around the shared retained progress-handler owner.
// It freezes one exact serialized database generation, exposes only the
// execution operations required by sidecar hydration, and must be declared
// after the transaction guard so an exhausted callback is detached before a
// failure-path rollback executes. Detachment is one-way revocation: the frozen
// identity remains available only for diagnostics and can never authorize
// callback-free SQLite execution.
class SyncSqliteSidecarSnapshotExecutionBudget final {
public:
    SyncSqliteSidecarSnapshotExecutionBudget(
        SyncSqliteDbHandleSlot& db,
        const SyncSqliteSidecarSnapshotExecutionLimits& limits,
        const std::string& label);
    ~SyncSqliteSidecarSnapshotExecutionBudget() = default;

    SyncSqliteSidecarSnapshotExecutionBudget(
        const SyncSqliteSidecarSnapshotExecutionBudget&) = delete;
    SyncSqliteSidecarSnapshotExecutionBudget& operator=(
        const SyncSqliteSidecarSnapshotExecutionBudget&) = delete;
    SyncSqliteSidecarSnapshotExecutionBudget(
        SyncSqliteSidecarSnapshotExecutionBudget&&) = delete;
    SyncSqliteSidecarSnapshotExecutionBudget& operator=(
        SyncSqliteSidecarSnapshotExecutionBudget&&) = delete;

    void require_authorizes_or_throw(
        sqlite3* database,
        std::uint64_t database_owner_generation,
        const std::string& label);
    void checkpoint();
    void throw_if_exhausted() const;
    void detach() noexcept;

    [[nodiscard]] std::uint64_t owner_generation() const noexcept;
    [[nodiscard]] std::uint64_t progress_callbacks() const noexcept;

private:
    struct FrozenBorrowTag final {};

    SyncSqliteSidecarSnapshotExecutionBudget(
        SyncSqliteSerializedDbBorrow database_borrow,
        const SyncSqliteSidecarSnapshotExecutionLimits& limits,
        const std::string& label,
        FrozenBorrowTag);

    sqlite3* database_ = nullptr;
    std::uint64_t database_owner_generation_ = 0;
    persistence::SqliteVerificationBudget budget_;
    bool attached_ = true;
};

struct SyncSqliteSidecarClaimedPathSnapshot final {
    std::vector<NormalizedSyncPath> paths;
    std::uint64_t path_count = 0;
    std::uint64_t total_path_bytes = 0;
    std::uint64_t database_owner_generation = 0;
    bool sqlite_lock_contention_observed = false;
    std::uint64_t sqlite_lock_wait_invocations = 0;
    std::uint64_t sqlite_lock_wait_authorized_sleep_milliseconds = 0;
    std::uint64_t sqlite_lock_wait_observed_sleep_milliseconds = 0;
};

// Exact-generation reader for the claimed-path frontier used by sidecar
// recovery. load_or_throw requires one typed transaction on this exact
// connection. The bounded query itself establishes the main-database read
// snapshot; every later evidence query must retain that transaction authority.
// A max_paths+1 SQL sentinel detects truncation without materializing an
// attacker-sized suffix, all path bytes are admitted before vector growth, and
// the exact-generation execution budget bounds SQLite VM work and cooperative
// elapsed time before any result is returned.
class SyncSqliteSidecarClaimedPathSnapshotReader final {
public:
    explicit SyncSqliteSidecarClaimedPathSnapshotReader(
        SyncSqliteDbHandleSlot& db,
        const std::string& label);
    ~SyncSqliteSidecarClaimedPathSnapshotReader() = default;

    SyncSqliteSidecarClaimedPathSnapshotReader(
        const SyncSqliteSidecarClaimedPathSnapshotReader&) = delete;
    SyncSqliteSidecarClaimedPathSnapshotReader& operator=(
        const SyncSqliteSidecarClaimedPathSnapshotReader&) = delete;
    SyncSqliteSidecarClaimedPathSnapshotReader(
        SyncSqliteSidecarClaimedPathSnapshotReader&&) = delete;
    SyncSqliteSidecarClaimedPathSnapshotReader& operator=(
        SyncSqliteSidecarClaimedPathSnapshotReader&&) = delete;

    [[nodiscard]] SyncSqliteSidecarClaimedPathSnapshot load_or_throw(
        const SyncSqliteTransactionAuthority& transaction_authority,
        SyncSqliteSidecarSnapshotExecutionBudget& execution_budget,
        const std::string& session_id,
        const std::string& worker_id,
        const std::string& worker_lease_id,
        const SyncSqliteSidecarClaimedPathLimits& limits,
        const std::string& label);

    [[nodiscard]] std::uint64_t owner_generation() const noexcept;

private:
    SyncSqliteStmt claimed_path_query_;
};

}  // namespace anonsync
