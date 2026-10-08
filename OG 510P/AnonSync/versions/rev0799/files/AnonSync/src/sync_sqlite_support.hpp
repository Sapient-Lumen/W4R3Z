#pragma once

#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>

#include <sqlite3.h>

#include "sync_sqlite_handle_slot.hpp"
#include "sync_sqlite_runtime.hpp"

namespace anonsync {

class SyncSqliteException final : public std::runtime_error {
public:
    SyncSqliteException(std::string message,
                        std::string operation,
                        int primary_result_code,
                        int extended_result_code);

    const std::string& operation() const noexcept;
    int primary_result_code() const noexcept;
    int extended_result_code() const noexcept;

private:
    std::string operation_;
    int primary_result_code_ = SQLITE_ERROR;
    int extended_result_code_ = SQLITE_ERROR;
};

struct SyncSqliteDb final {
    SyncSqliteDbHandleSlot db;

    SyncSqliteDb() = default;
    ~SyncSqliteDb() = default;
    SyncSqliteDb(const SyncSqliteDb&) = delete;
    SyncSqliteDb& operator=(const SyncSqliteDb&) = delete;
    SyncSqliteDb(SyncSqliteDb&&) noexcept = default;
    SyncSqliteDb& operator=(SyncSqliteDb&&) noexcept = default;
};

struct SyncSqliteStmt final {
public:
    // Public use is intentionally a non-owning view. Callers retain the
    // familiar `statement.stmt` spelling for SQLite C APIs, but cannot move,
    // reset, or refill the underlying owner slot independently of the
    // database-generation pin.
    class HandleView final {
    public:
        HandleView(const HandleView&) = delete;
        HandleView& operator=(const HandleView&) = delete;
        HandleView(HandleView&&) = delete;
        HandleView& operator=(HandleView&&) = delete;

        [[nodiscard]] sqlite3_stmt* get() const noexcept;
        [[nodiscard]] bool empty() const noexcept { return get() == nullptr; }
        [[nodiscard]] explicit operator bool() const noexcept {
            return get() != nullptr;
        }
        operator sqlite3_stmt*() const noexcept { return get(); }

    private:
        friend struct SyncSqliteStmt;
        explicit HandleView(SyncSqliteStmt& owner) noexcept
            : owner_(std::addressof(owner)) {}

        SyncSqliteStmt* owner_ = nullptr;
    };

private:
    // Declaration order is authority order. Reverse destruction finalizes the
    // SQLite statement owner before releasing the exact database-generation
    // pin. The public HandleView is declared last and owns nothing.
    SyncSqliteSerializedDbBorrow owner_borrow_;
    SyncSqliteStmtHandleSlot statement_owner_;

    explicit SyncSqliteStmt(SyncSqliteSerializedDbBorrow owner_borrow) noexcept;
    void prepare_or_throw(sqlite3* db,
                          const std::string& sql,
                          const std::string& label);

    friend SyncSqliteStmt sqlite_prepare_or_throw(
        sqlite3* db,
        const std::string& sql,
        const std::string& label);
    friend SyncSqliteStmt sqlite_prepare_or_throw(
        SyncSqliteDbHandleSlot& db,
        const std::string& sql,
        const std::string& label);

public:
    HandleView stmt;

    SyncSqliteStmt() noexcept;
    ~SyncSqliteStmt() = default;
    SyncSqliteStmt(const SyncSqliteStmt&) = delete;
    SyncSqliteStmt& operator=(const SyncSqliteStmt&) = delete;
    SyncSqliteStmt(SyncSqliteStmt&& other) noexcept;
    SyncSqliteStmt& operator=(SyncSqliteStmt&& other) noexcept;

    // Finalize first, then revoke the owner-generation capability.
    void reset() noexcept;
    [[nodiscard]] std::uint64_t owner_generation() const noexcept;
    [[nodiscard]] SyncSqliteConnectionMutexMode owner_connection_mutex_mode()
        const noexcept;
};

enum class SyncSqliteTransactionMode {
    Deferred,
    Immediate,
    Exclusive
};

struct SyncSqliteTransactionAuthorityState;
struct SyncSqliteTransactionBoundaryProof;

// A non-owning, guard-generation lease issued by SyncSqliteTransaction. It
// fails closed once that exact guard commits, rolls back, or leaves scope;
// pointer equality alone is deliberately insufficient because one SQLite
// handle can host many successive transactions and snapshots.
//
// On an AnonSync-authorized connection, the owned SQLite authorizer
// mechanically denies raw BEGIN/COMMIT/ROLLBACK and every SAVEPOINT operation.
// One single-use permit is issued only by the typed guard and is bound to the
// exact connection incarnation, authorizer generation, and transaction
// generation. Unowned utility connections retain observation-based fallback
// semantics for compatibility.
class SyncSqliteTransactionAuthority final {
public:
    SyncSqliteTransactionAuthority() = default;

    [[nodiscard]] bool authorizes(sqlite3* db) const noexcept;
    [[nodiscard]] bool authorizes_snapshot(sqlite3* db) const noexcept;
    [[nodiscard]] bool authorizes_write(sqlite3* db) const noexcept;

private:
    SyncSqliteProcessId process_id_ = 0;
    std::weak_ptr<SyncSqliteTransactionAuthorityState> state_;

    explicit SyncSqliteTransactionAuthority(
        SyncSqliteProcessId process_id,
        const std::shared_ptr<SyncSqliteTransactionAuthorityState>& state) noexcept
        : process_id_(process_id), state_(state) {}

    friend class SyncSqliteTransaction;
};

// Scope-bound, thread-affine transaction guard. A live transaction is rolled
// back without throwing on scope exit; commit/rollback preserve the SQLite
// error code when an explicit operation fails. The guard retains the
// serialized connection mutex for the full live generation, preventing other
// users of the same handle from interleaving between BEGIN, evidence checks,
// mutations, and the final boundary. Other SQLite connections remain free.
// The issued authority lease binds downstream capabilities to this exact guard
// lifetime, not merely to its connection. The retained mutex capability is
// bound to one exact process-local thread incarnation: foreign-thread queries
// fail closed, explicit finalization throws before touching SQLite, and an
// unsafe foreign-thread destructor fails stopped.
class SyncSqliteTransaction final {
public:
    SyncSqliteTransaction(SyncSqliteDbHandleSlot& db,
                          std::string label,
                          SyncSqliteTransactionMode mode =
                              SyncSqliteTransactionMode::Immediate);
    SyncSqliteTransaction(sqlite3* db,
                          std::string label,
                          SyncSqliteTransactionMode mode =
                              SyncSqliteTransactionMode::Immediate);
    ~SyncSqliteTransaction();
    SyncSqliteTransaction(const SyncSqliteTransaction&) = delete;
    SyncSqliteTransaction& operator=(const SyncSqliteTransaction&) = delete;
    SyncSqliteTransaction(SyncSqliteTransaction&&) = delete;
    SyncSqliteTransaction& operator=(SyncSqliteTransaction&&) = delete;

    void commit();
    void rollback();
    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] bool authorizes(sqlite3* db) const noexcept;
    [[nodiscard]] bool authorizes_snapshot(sqlite3* db) const noexcept;
    [[nodiscard]] bool authorizes_write(sqlite3* db) const noexcept;
    [[nodiscard]] SyncSqliteTransactionAuthority authority() const noexcept;

private:
    void begin_or_throw(SyncSqliteTransactionMode mode);
    void revoke_authority() noexcept;

    // Declared first so it is destroyed last. An active typed transaction
    // pins the exact connection-owner generation through rollback/commit and
    // retained-mutex release.
    SyncSqliteSerializedDbBorrow owner_borrow_;
    sqlite3* db_ = nullptr;
    SyncSqliteProcessId process_id_ = 0;
    std::string label_;
    bool active_ = false;
    std::shared_ptr<SyncSqliteTransactionAuthorityState> authority_state_;
    std::unique_ptr<SyncSqliteTransactionBoundaryProof> boundary_proof_;
};

std::string sqlite_error_message(sqlite3* db, const std::string& prefix);
std::string sqlite_result_code_name(int result_code);
[[noreturn]] void throw_sqlite_exception(sqlite3* db,
                                         int result_code,
                                         const std::string& operation,
                                         const std::string& detail = "");
void sqlite_exec_or_throw(sqlite3* db, const std::string& sql, const std::string& label);
void sqlite_exec_or_throw(SyncSqliteDbHandleSlot& db,
                          const std::string& sql,
                          const std::string& label);
SyncSqliteStmt sqlite_prepare_or_throw(sqlite3* db,
                                      const std::string& sql,
                                      const std::string& label);
SyncSqliteStmt sqlite_prepare_or_throw(SyncSqliteDbHandleSlot& db,
                                      const std::string& sql,
                                      const std::string& label);
void sqlite_bind_text_or_throw(sqlite3_stmt* stmt, int index, const std::string& value, const std::string& label);
void sqlite_bind_blob_or_throw(sqlite3_stmt* stmt, int index, const std::string& value, const std::string& label);
void sqlite_bind_bool_or_throw(sqlite3_stmt* stmt, int index, bool value, const std::string& label);
sqlite3_int64 u64_to_sqlite_i64_or_throw(std::uint64_t value, const std::string& label);
void sqlite_bind_u64_or_throw(sqlite3_stmt* stmt, int index, std::uint64_t value, const std::string& label);
void sqlite_step_done_or_throw(sqlite3_stmt* stmt, const std::string& label);
std::string sqlite_column_text_or_throw(sqlite3_stmt* stmt, int column, const std::string& label);
std::string sqlite_column_blob_or_throw(sqlite3_stmt* stmt,
                                        int column,
                                        std::uint64_t max_bytes,
                                        const std::string& label);
std::int64_t sqlite_column_i64_or_throw(sqlite3_stmt* stmt,
                                        int column,
                                        const std::string& label);
std::uint64_t sqlite_column_u64_or_throw(sqlite3_stmt* stmt, int column, const std::string& label);
bool sqlite_column_bool_or_throw(sqlite3_stmt* stmt, int column, const std::string& label);
std::uint64_t sqlite_count_for_session_or_throw(sqlite3* db,
                                                const std::string& sql,
                                                const std::string& session_id,
                                                const std::string& label);
std::uint64_t sqlite_count_for_session_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& sql,
    const std::string& session_id,
    const std::string& label);
bool sqlite_table_exists_or_throw(sqlite3* db,
                                  const std::string& table_name,
                                  const std::string& label);
bool sqlite_table_exists_or_throw(SyncSqliteDbHandleSlot& db,
                                  const std::string& table_name,
                                  const std::string& label);
bool sqlite_simple_identifier_ok(const std::string& identifier);
// Persistent schema probes are deliberately bound to main. TEMP-first name
// resolution must not redirect a durability or migration decision.
bool sqlite_table_column_exists_or_throw(sqlite3* db,
                                         const std::string& table_name,
                                         const std::string& column_name,
                                         const std::string& label);
bool sqlite_table_column_exists_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& table_name,
    const std::string& column_name,
    const std::string& label);

}  // namespace anonsync
