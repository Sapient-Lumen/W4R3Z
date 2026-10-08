#include "sync_sqlite_support.hpp"

#include "sync_sqlite_connection_authority_internal.hpp"
#include "sync_sqlite_mutex_capability.hpp"

#include <atomic>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace {

const char* transaction_begin_sql_or_throw(SyncSqliteTransactionMode mode) {
    switch (mode) {
        case SyncSqliteTransactionMode::Deferred: return "BEGIN;";
        case SyncSqliteTransactionMode::Immediate: return "BEGIN IMMEDIATE;";
        case SyncSqliteTransactionMode::Exclusive: return "BEGIN EXCLUSIVE;";
    }
    throw std::invalid_argument("SQLite transaction mode is invalid");
}

}  // namespace

struct SyncSqliteTransactionAuthorityState final {
    sqlite3* db = nullptr;
    SyncSqliteTransactionBoundaryProof boundary;
    std::atomic<bool> active{false};
};

bool SyncSqliteTransactionAuthority::authorizes(sqlite3* db) const noexcept {
    if (!sync_sqlite_process_id_is_current(process_id_)) return false;
    const std::shared_ptr<SyncSqliteTransactionAuthorityState> state = state_.lock();
    if (state == nullptr ||
        !state->active.load(std::memory_order_acquire) ||
        state->db == nullptr || state->db != db) {
        return false;
    }
    // Foreign-thread observation is unusable there, but must not revoke the
    // still-current owner-thread generation.
    if (!sync_sqlite_thread_incarnation_is_current(
            state->boundary.owner_thread_incarnation)) {
        return false;
    }
    if (!sync_sqlite_transaction_boundary_authorizes_noexcept(
            db, state->boundary)) {
        // Autocommit restoration, generation supersession, or authorizer
        // replacement permanently revokes this guard generation. It can never
        // authorize a later transaction on a reused SQLite handle.
        state->active.store(false, std::memory_order_release);
        return false;
    }
    return true;
}

bool SyncSqliteTransactionAuthority::authorizes_snapshot(sqlite3* db) const noexcept {
    if (!authorizes(db)) return false;
    const int state = sqlite3_txn_state(db, "main");
    return state == SQLITE_TXN_READ || state == SQLITE_TXN_WRITE;
}

bool SyncSqliteTransactionAuthority::authorizes_write(sqlite3* db) const noexcept {
    return authorizes(db) && sqlite3_txn_state(db, "main") == SQLITE_TXN_WRITE;
}

SyncSqliteTransaction::SyncSqliteTransaction(
    SyncSqliteDbHandleSlot& db,
    std::string label,
    SyncSqliteTransactionMode mode)
    : owner_borrow_(borrow_sync_sqlite_serialized_db_or_throw(
          db, label + " typed transaction owner")),
      db_(owner_borrow_.get()),
      process_id_(current_sync_sqlite_process_id_noexcept()),
      label_(std::move(label)),
      authority_state_(std::make_shared<SyncSqliteTransactionAuthorityState>()),
      boundary_proof_(std::make_unique<SyncSqliteTransactionBoundaryProof>()) {
    begin_or_throw(mode);
}

SyncSqliteTransaction::SyncSqliteTransaction(sqlite3* db,
                                             std::string label,
                                             SyncSqliteTransactionMode mode)
    : db_(db),
      process_id_(current_sync_sqlite_process_id_noexcept()),
      label_(std::move(label)),
      authority_state_(std::make_shared<SyncSqliteTransactionAuthorityState>()),
      boundary_proof_(std::make_unique<SyncSqliteTransactionBoundaryProof>()) {
    begin_or_throw(mode);
}

void SyncSqliteTransaction::begin_or_throw(SyncSqliteTransactionMode mode) {
    if (db_ == nullptr) {
        throw std::invalid_argument(label_ + " database handle is null");
    }
    const char* const begin_sql = transaction_begin_sql_or_throw(mode);
    *boundary_proof_ = begin_sync_sqlite_transaction_boundary_or_throw(
        db_, begin_sql, label_ + " begin");

    active_ = true;
    authority_state_->db = db_;
    authority_state_->boundary = *boundary_proof_;
    authority_state_->boundary.retained_connection_mutex = nullptr;
    // The copied authority keeps a non-owning view of the lifetime sentinel so
    // use-time checks can prove that the owning guard still pins the mutex.
    // Only boundary_proof_ owns the recursive mutex entry and decrements the
    // sentinel during revocation.
    authority_state_->active.store(true, std::memory_order_release);
}

SyncSqliteTransaction::~SyncSqliteTransaction() {
    if (active_ && db_ != nullptr && boundary_proof_ != nullptr) {
        if (!sync_sqlite_process_id_is_current(process_id_)) {
            fail_stop_on_sync_sqlite_capability_violation_noexcept();
        }
        if (!sync_sqlite_thread_incarnation_is_current(
                boundary_proof_->owner_thread_incarnation)) {
            fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
        }
        rollback_sync_sqlite_transaction_boundary_noexcept(db_, *boundary_proof_);
    }
    revoke_authority();
}

void SyncSqliteTransaction::commit() {
    if (!active_) throw std::logic_error(label_ + " transaction is not active");
    require_sync_sqlite_process_id_or_fail_stop(process_id_, label_ + " commit");
    require_sync_sqlite_thread_incarnation_or_throw(
        boundary_proof_->owner_thread_incarnation, label_ + " commit");
    if (!authority().authorizes(db_)) {
        revoke_authority();
        throw std::logic_error(
            label_ + " transaction boundary is no longer owned by this guard");
    }
    try {
        end_sync_sqlite_transaction_boundary_or_throw(
            db_,
            *boundary_proof_,
            SyncSqliteTransactionBoundaryEnd::Commit,
            label_ + " commit");
    } catch (...) {
        // SQLITE_BUSY can leave COMMIT retryable. Preserve authority only when
        // the exact bridge and transaction generation are still current.
        if (!sync_sqlite_transaction_boundary_authorizes_noexcept(
                db_, *boundary_proof_)) {
            revoke_authority();
        }
        throw;
    }
    revoke_authority();
}

void SyncSqliteTransaction::rollback() {
    if (!active_) return;
    require_sync_sqlite_process_id_or_fail_stop(process_id_, label_ + " rollback");
    require_sync_sqlite_thread_incarnation_or_throw(
        boundary_proof_->owner_thread_incarnation, label_ + " rollback");
    if (!authority().authorizes(db_)) {
        const bool already_ended = sqlite3_get_autocommit(db_) != 0;
        revoke_authority();
        if (already_ended) return;
        throw std::logic_error(
            label_ +
            " transaction boundary is no longer owned; rollback was not executed");
    }
    try {
        end_sync_sqlite_transaction_boundary_or_throw(
            db_,
            *boundary_proof_,
            SyncSqliteTransactionBoundaryEnd::Rollback,
            label_ + " rollback");
    } catch (...) {
        if (!sync_sqlite_transaction_boundary_authorizes_noexcept(
                db_, *boundary_proof_)) {
            revoke_authority();
        }
        throw;
    }
    revoke_authority();
}

bool SyncSqliteTransaction::active() const noexcept {
    return active_ && boundary_proof_ != nullptr &&
           sync_sqlite_process_id_is_current(process_id_) &&
           sync_sqlite_thread_incarnation_is_current(
               boundary_proof_->owner_thread_incarnation) &&
           authority().authorizes(db_);
}

bool SyncSqliteTransaction::authorizes(sqlite3* db) const noexcept {
    return authority().authorizes(db);
}

bool SyncSqliteTransaction::authorizes_snapshot(sqlite3* db) const noexcept {
    return authority().authorizes_snapshot(db);
}

bool SyncSqliteTransaction::authorizes_write(sqlite3* db) const noexcept {
    return authority().authorizes_write(db);
}

SyncSqliteTransactionAuthority SyncSqliteTransaction::authority() const noexcept {
    if (!sync_sqlite_process_id_is_current(process_id_)) return {};
    return SyncSqliteTransactionAuthority(process_id_, authority_state_);
}

void SyncSqliteTransaction::revoke_authority() noexcept {
    active_ = false;
    if (authority_state_ != nullptr) {
        authority_state_->active.store(false, std::memory_order_release);
    }
    if (boundary_proof_ != nullptr) {
        release_sync_sqlite_transaction_mutex_noexcept(*boundary_proof_);
    }
    // The SQLite mutex and transaction-generation evidence must be released
    // before the owner pin. A committed/rolled-back guard no longer prevents
    // an explicit strict close even if the inert C++ guard remains in scope.
    owner_borrow_.reset();
}

}  // namespace anonsync
