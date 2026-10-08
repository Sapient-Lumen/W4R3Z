#pragma once

#include "anonsync_sync_checkpoint_owner_fence.hpp"
#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <string>

struct sqlite3;

namespace anonsync::sync_checkpoint_owner_fence_internal {

// The sticky mode row deliberately has no foreign key to the checkpoint root.
// It is the durable memory that ownership once existed, so release and
// checkpoint replacement cannot silently return the session to unowned mode.
void ensure_checkpoint_owner_mode_schema_or_throw(
    sqlite3* db,
    const std::string& context);

struct MintedDaemonOwnerLockRecord final {
    std::string daemon_id;
    std::string worker_id;
    std::string owner_lock_id;
    std::uint64_t owner_lock_epoch = 0;
    std::uint64_t acquired_at_epoch = 0;
    std::uint64_t expires_at_epoch = 0;
    bool acquired = false;
    bool reclaimed_expired = false;
};

[[nodiscard]] std::string owner_lock_id_or_throw(
    const std::string& session_id,
    const std::string& daemon_id,
    const std::string& worker_id,
    std::uint64_t owner_lock_epoch);

// The caller owns the write transaction and its commit boundary. This function
// interprets the durable row, asks the pure policy to mint the next generation,
// performs compare-and-replace, and reloads the exact evidence before return.
[[nodiscard]] MintedDaemonOwnerLockRecord
acquire_owner_generation_in_write_transaction_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& daemon_id,
    const std::string& worker_id,
    std::uint64_t acquired_at_epoch,
    std::uint64_t owner_lock_seconds,
    const std::string& context);

// Release is itself a recipient-fenced state transition. The exact live
// generation must still authorize this write transaction before it is retired.
void release_owner_generation_in_write_transaction_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const SyncSessionCheckpointDaemonOwnerCapability& capability,
    std::uint64_t released_at_epoch,
    const std::string& context);

// Must be called after the recipient has entered the write transaction that
// will contain the guarded mutation. The owner row and capability are compared
// on that same SQLite snapshot; a preflight observation is never authority.
void require_recipient_write_authority_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const SyncSessionCheckpointDaemonOwnerCapability& capability,
    std::uint64_t observed_at_epoch,
    const std::string& context);

// A root reset is destructive and its foreign-key cascade retires the current
// owner row.  The permit is constructible only after the exact recipient fence
// has run on a live typed write-transaction generation.  The delete consumes
// that permit and advances the independent sticky-mode timestamp before the
// checkpoint root can be repopulated by the caller.
class CheckpointRootResetPermit final {
public:
    CheckpointRootResetPermit(const CheckpointRootResetPermit&) = delete;
    CheckpointRootResetPermit& operator=(const CheckpointRootResetPermit&) =
        delete;
    CheckpointRootResetPermit(CheckpointRootResetPermit&&) = delete;
    CheckpointRootResetPermit& operator=(CheckpointRootResetPermit&&) = delete;

private:
    CheckpointRootResetPermit(
        SyncSqliteTransactionAuthority transaction_authority,
        sqlite3* db,
        std::string session_id,
        bool owner_mode_present,
        std::string ownership_mode,
        std::uint64_t latest_owner_lock_epoch,
        std::uint64_t previous_mode_updated_at_epoch,
        std::string administrative_disable_evidence_id,
        std::uint64_t reset_at_epoch);

    SyncSqliteTransactionAuthority transaction_authority_;
    sqlite3* db_ = nullptr;
    std::string session_id_;
    bool owner_mode_present_ = false;
    std::string ownership_mode_;
    std::uint64_t latest_owner_lock_epoch_ = 0;
    std::uint64_t previous_mode_updated_at_epoch_ = 0;
    std::string administrative_disable_evidence_id_;
    std::uint64_t reset_at_epoch_ = 0;
    bool consumed_ = false;

    friend CheckpointRootResetPermit
    authorize_checkpoint_root_reset_in_write_transaction_or_throw(
        sqlite3*,
        const SyncSqliteTransactionAuthority&,
        const std::string&,
        const SyncSessionCheckpointDaemonOwnerCapability&,
        std::uint64_t,
        const std::string&);
    friend void delete_checkpoint_root_with_permit_in_write_transaction_or_throw(
        sqlite3*,
        CheckpointRootResetPermit&,
        const std::string&);
};

[[nodiscard]] CheckpointRootResetPermit
authorize_checkpoint_root_reset_in_write_transaction_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionAuthority& transaction_authority,
    const std::string& session_id,
    const SyncSessionCheckpointDaemonOwnerCapability& capability,
    std::uint64_t reset_at_epoch,
    const std::string& context);

void delete_checkpoint_root_with_permit_in_write_transaction_or_throw(
    sqlite3* db,
    CheckpointRootResetPermit& permit,
    const std::string& context);

}  // namespace anonsync::sync_checkpoint_owner_fence_internal
