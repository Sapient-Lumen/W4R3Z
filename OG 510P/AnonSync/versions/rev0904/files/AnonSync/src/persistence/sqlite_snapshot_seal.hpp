#pragma once

#include "sqlite_snapshot_geometry.hpp"
#include "sync_atomic_file_publication_internal.hpp"
#include "sync_process_incarnation.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <string>
#include <string_view>

struct sqlite3;
struct sqlite3_vfs;

namespace anonsync::persistence {

// The seal and the pure geometry verifier share one monotone policy. Callers
// may reduce reviewed byte/page authority for narrower deployments and tests;
// they cannot enlarge it.
using SqliteSnapshotSealPolicy = SqliteSnapshotGeometryPolicy;

// A process-local, namespace-free capability for one byte-exact, sidecar-free
// SQLite snapshot.
//
// Capture opens the source through a retained no-symlink parent-directory
// guard, rejects WAL/SHM/journal siblings, verifies exact SQLite geometry, and
// copies the exact bytes into private process memory while hashing that same
// stream. SQLite consumers receive independent read-only deserializations of
// those captured bytes. No staging pathname, journal pathname, unlink, rename,
// or cleanup directory exists after capture.
//
// The minting fork-lineage token is retained so a child cannot inspect, move,
// free, deserialize, or otherwise reuse its parent's inherited capability.
class SealedSqliteSnapshot final {
public:
    static SealedSqliteSnapshot capture(
        const std::filesystem::path& source_path,
        const std::string& label,
        const SqliteSnapshotSealPolicy& policy = {});

    // Capture one transactionally consistent image from an already-open
    // database without creating or deleting a filesystem pathname. The source
    // connection must be in autocommit mode and full-mutex protected. SQLite's
    // page geometry is checked against policy before any private destination
    // is opened. A separately owned backup boundary then pins one read
    // transaction, rechecks exact geometry inside that snapshot, copies only
    // fixed-size page batches with a derived step ceiling, and verifies the
    // completed private in-memory destination;
    // temp_store=MEMORY plus VACUUM canonicalizes the serialized image to the
    // standalone rollback-journal 1/1 file format before resident authority is
    // minted. The caller remains responsible for proving that source_database
    // is its current-process capability.
    static SealedSqliteSnapshot capture_database(
        sqlite3* source_database,
        const std::string& label,
        const SqliteSnapshotSealPolicy& policy = {});

    SealedSqliteSnapshot() = default;
    ~SealedSqliteSnapshot();
    SealedSqliteSnapshot(const SealedSqliteSnapshot&) = delete;
    SealedSqliteSnapshot& operator=(const SealedSqliteSnapshot&) = delete;
    SealedSqliteSnapshot(SealedSqliteSnapshot&& other) noexcept;
    SealedSqliteSnapshot& operator=(SealedSqliteSnapshot&& other) noexcept;

    const std::filesystem::path& source_path() const noexcept;
    const std::string& sha256_hex() const noexcept;
    std::uint64_t byte_count() const noexcept;
    std::uint32_t page_size() const noexcept;
    std::uint32_t page_count() const noexcept;
    const SqliteSnapshotGeometry& geometry() const noexcept;

    // Re-establish that the process-owned bytes still have the captured size,
    // digest, and exact SQLite geometry, and that the capture-time VFS object
    // remains registered under the same name.
    void verify_unchanged_or_throw(const std::string& label);

    // Create an independent private in-memory database and deserialize a fresh
    // SQLite-owned copy using SQLITE_DESERIALIZE_READONLY. Prefer the typed
    // owner form: it binds every later borrow and close to one exact serialized
    // connection generation. The raw compatibility form transfers ownership to
    // the caller and remains valid after this seal is destroyed.
    sqlite3* open_database_or_throw(const std::string& label);
    SyncSqliteDbHandleSlot open_database_owner_or_throw(
        const std::string& label);

    // Publish the exact resident bytes through the capability-bound atomic
    // file owner. This does not reopen the source pathname and does not create
    // a SQLite staging database or sidecar family. The resident image is
    // reverified immediately before and after synchronous publication.
    void publish_exact_copy_atomically_or_throw(
        const std::filesystem::path& destination_path,
        const std::string& label);

    // Immutable publication variant. The exact resident snapshot is linked at
    // destination_path only when that final entry is absent; an existing entry
    // is never replaced. This is the bootstrap/genesis boundary for callers
    // that must not expose an empty or partially initialized SQLite main file.
    void publish_exact_copy_atomically_create_new_or_throw(
        const std::filesystem::path& destination_path,
        const std::string& label);

    // Deterministic-observer form used by the restore crash-frontier model.
    // Production callers normally use the wrapper above.
    void publish_exact_copy_atomically_with_observer_or_throw(
        const std::filesystem::path& destination_path,
        const std::string& label,
        atomic_file_publication_detail::AtomicFilePublicationObserver observer,
        void* observer_context);

    void publish_exact_copy_atomically_create_new_with_observer_or_throw(
        const std::filesystem::path& destination_path,
        const std::string& label,
        atomic_file_publication_detail::AtomicFilePublicationObserver observer,
        void* observer_context);

private:
    struct SqliteBufferDeleter {
        void operator()(unsigned char* bytes) const noexcept;
    };

    void require_current_process_noexcept() const noexcept;
    void require_current_process_or_throw(std::string_view label) const;
    void initialize_process_and_vfs_or_throw(const std::string& label);
    void finalize_resident_bytes_or_throw(const std::string& label);
    void transfer_from_noexcept(SealedSqliteSnapshot& other) noexcept;
    void clear_moved_from_noexcept() noexcept;
    void verify_pinned_vfs_registration_or_throw(const std::string& label) const;
    void open_database_into_or_throw(sqlite3** output,
                                     const std::string& label);
    void cleanup_noexcept() noexcept;

    SyncProcessIncarnation process_id_;
    std::filesystem::path source_path_;
    std::string sha256_hex_;
    std::string pinned_vfs_name_;
    std::uint64_t byte_count_ = 0;
    SqliteSnapshotGeometry geometry_{};
    SqliteSnapshotGeometryPolicy geometry_policy_{};
    std::unique_ptr<unsigned char, SqliteBufferDeleter> serialized_bytes_;
    sqlite3_vfs* pinned_vfs_ = nullptr;
};

}  // namespace anonsync::persistence
