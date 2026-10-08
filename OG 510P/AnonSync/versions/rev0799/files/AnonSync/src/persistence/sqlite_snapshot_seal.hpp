#pragma once

#include "sqlite_path_security.hpp"
#include "sqlite_snapshot_geometry.hpp"

#include <cstdint>
#include <filesystem>
#include <string>

struct sqlite3;
struct sqlite3_vfs;

namespace anonsync::persistence {

// The seal and the pure geometry verifier share one monotone policy.  Callers
// may reduce reviewed byte/page authority for narrower deployments and tests;
// they cannot enlarge it.
using SqliteSnapshotSealPolicy = SqliteSnapshotGeometryPolicy;

// A process-local capability for one byte-exact, sidecar-free SQLite snapshot.
//
// Capture opens the source through a retained, no-symlink parent-directory
// guard, rejects WAL/SHM/journal siblings, copies and hashes the exact bytes
// into a private 0700 directory, and retains an O_RDONLY descriptor for the
// staged inode.  SQLite is then opened only through an immutable, read-only URI
// naming that private copy.  The original pathname is never used after capture.
class SealedSqliteSnapshot final {
public:
    static SealedSqliteSnapshot capture(
        const std::filesystem::path& source_path,
        const std::string& label,
        const SqliteSnapshotSealPolicy& policy = {});

    SealedSqliteSnapshot() = default;
    ~SealedSqliteSnapshot();
    SealedSqliteSnapshot(const SealedSqliteSnapshot&) = delete;
    SealedSqliteSnapshot& operator=(const SealedSqliteSnapshot&) = delete;
    SealedSqliteSnapshot(SealedSqliteSnapshot&& other) noexcept;
    SealedSqliteSnapshot& operator=(SealedSqliteSnapshot&& other) noexcept;

    const std::filesystem::path& source_path() const noexcept;
    const std::filesystem::path& staged_path() const noexcept;
    const std::string& immutable_uri() const noexcept;
    const std::string& sha256_hex() const noexcept;
    std::uint64_t byte_count() const noexcept;
    std::uint32_t page_size() const noexcept;
    std::uint32_t page_count() const noexcept;
    const SqliteSnapshotGeometry& geometry() const noexcept;

    // Re-establish that the retained descriptor, staged pathname, and absent
    // sidecars still describe the same private snapshot captured above.
    void verify_unchanged_or_throw(const std::string& label);

    // Open the private copy with mode=ro, cache=private, immutable=1, URI and
    // no-follow flags.  The returned handle is owned by the caller.
    sqlite3* open_database_or_throw(const std::string& label);

private:
    void verify_pinned_vfs_registration_or_throw(const std::string& label) const;
    void cleanup_noexcept() noexcept;

    std::filesystem::path source_path_;
    std::filesystem::path staging_directory_;
    std::filesystem::path staged_path_;
    std::string immutable_uri_;
    std::string sha256_hex_;
    std::string pinned_vfs_name_;
    std::uint64_t byte_count_ = 0;
    SqliteSnapshotGeometry geometry_{};
    SqliteSnapshotGeometryPolicy geometry_policy_{};
    SqlitePathFamilyGuard staged_guard_;
    int staged_fd_ = -1;
    sqlite3_vfs* pinned_vfs_ = nullptr;
    std::uint64_t staged_device_ = 0;
    std::uint64_t staged_inode_ = 0;
    std::int64_t staged_mtime_seconds_ = 0;
    std::int64_t staged_mtime_nanoseconds_ = 0;
    std::int64_t staged_ctime_seconds_ = 0;
    std::int64_t staged_ctime_nanoseconds_ = 0;
};

}  // namespace anonsync::persistence
