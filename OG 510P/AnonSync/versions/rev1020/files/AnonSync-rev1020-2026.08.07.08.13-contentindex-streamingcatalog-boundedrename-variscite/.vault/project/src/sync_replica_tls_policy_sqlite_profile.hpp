#pragma once

#include "sqlite_path_security.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

// DurableNamed is the ordinary mutable policy-authority profile. The detached
// form is narrowly for constructing a complete namespace-free bootstrap image
// before that image is sealed and published create-new at its deployment-bound
// path. The forensic dispositions are observation-only: one for an already
// named database and one for a sealed filename-free detached image. No
// non-durable disposition may cross into operational mutable ownership.
enum class SyncReplicaTlsPolicySqliteBackendDisposition : std::uint8_t {
    DurableNamed = 1U,
    DetachedBootstrapImage = 2U,
    ForensicReadOnlyNamed = 3U,
    ForensicReadOnlyDetached = 4U,
};

// Exact process-local lifetime binding for one serialized SQLite connection
// generation used as TLS policy authority. The retained borrow prevents close
// or refill while an owner is live; explicit re-attestation also rejects a
// handle-slot move or retarget before authority is read or returned. Durable
// named backends additionally retain a SqlitePathFamilyGuard that binds the
// open main file and parent path, rejects symlink-family drift, and consults
// SQLITE_FCNTL_HAS_MOVED where the bundled SQLite/VFS supports it. Detached
// bootstrap images instead remain filename-free and are never treated as
// operational authority. ForensicReadOnlyNamed is deliberately rejected by
// this mutable-owner binding and is accepted only by the standalone observer
// profile/attestation functions below.
//
// This is one in-process handle generation plus, for named backends, live
// namespace observation. It is not media, controller, VFS-integrity,
// cross-process, or reboot provenance.
class SyncReplicaTlsPolicySqliteConnectionBinding final {
public:
    SyncReplicaTlsPolicySqliteConnectionBinding(
        SyncSqliteDbHandleSlot& database,
        std::string label,
        SyncReplicaTlsPolicySqliteBackendDisposition disposition =
            SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed);

    SyncReplicaTlsPolicySqliteConnectionBinding(
        const SyncReplicaTlsPolicySqliteConnectionBinding&) = delete;
    SyncReplicaTlsPolicySqliteConnectionBinding& operator=(
        const SyncReplicaTlsPolicySqliteConnectionBinding&) = delete;
    SyncReplicaTlsPolicySqliteConnectionBinding(
        SyncReplicaTlsPolicySqliteConnectionBinding&&) = delete;
    SyncReplicaTlsPolicySqliteConnectionBinding& operator=(
        SyncReplicaTlsPolicySqliteConnectionBinding&&) = delete;
    ~SyncReplicaTlsPolicySqliteConnectionBinding() noexcept = default;

    [[nodiscard]] SyncSqliteDbHandleSlot& database_or_throw(
        std::string_view operation_label);

    void require_current_or_throw(
        std::string_view operation_label);

    [[nodiscard]] const std::string& database_filename() const noexcept {
        return database_filename_;
    }

    [[nodiscard]] std::uint64_t database_generation() const noexcept {
        return database_generation_;
    }

private:
    SyncSqliteDbHandleSlot& database_;
    SyncSqliteSerializedDbBorrow retained_lifetime_;
    std::uint64_t database_generation_ = 0U;
    std::string database_filename_;
    SqlitePathFamilyGuard database_path_guard_;
    std::string label_;
    SyncReplicaTlsPolicySqliteBackendDisposition disposition_ =
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed;
};

// Shared writable connection profile for durable TLS policy databases and
// detached genesis images. This is a process-local SQLite capability profile,
// not a proof that the selected VFS, filesystem, controller, or storage medium honors
// persistence requests.
void configure_sync_replica_tls_policy_sqlite_connection_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label);

// Configures the same closed connection capability surface for a named
// read-only forensic observer, with query_only retained on. It grants no
// durable policy ownership and does not request a journal or sync transition.
void configure_sync_replica_tls_policy_sqlite_read_only_connection_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label);

// Re-attests the closed connection profile. DurableNamed requires a named,
// writable main database with WAL+FULL or rollback-journal+EXTRA settings;
// DetachedBootstrapImage requires an unnamed writable main image using MEMORY
// journaling; ForensicReadOnlyNamed requires a named read-only database with a
// persistent journal family but makes no mutable synchronous-policy claim;
// ForensicReadOnlyDetached requires an unnamed read-only MEMORY-journal image.
// The authority noun is diagnostic text such as "membership" or "membership
// anchor"; it must be nonempty.
void attest_sync_replica_tls_policy_sqlite_backend_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string_view authority_noun,
    const std::string& label,
    SyncReplicaTlsPolicySqliteBackendDisposition disposition =
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed);

// Returns SQLite's named main-database filename after the caller has selected a
// named backend disposition; an empty or anonymous name is invalid.
[[nodiscard]] std::string
sync_replica_tls_policy_sqlite_main_filename_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label);

// Fails closed unless two already-open named SQLite main databases can be
// proved to be different filesystem objects. This closes accidental same-file
// composition; it does not prove separate media, controllers, failure domains,
// administrative principals, or resistance to coordinated replacement.
void require_distinct_sync_replica_tls_policy_sqlite_databases_or_throw(
    std::string_view first_filename,
    std::string_view second_filename,
    const std::string& label);

}  // namespace anonsync
