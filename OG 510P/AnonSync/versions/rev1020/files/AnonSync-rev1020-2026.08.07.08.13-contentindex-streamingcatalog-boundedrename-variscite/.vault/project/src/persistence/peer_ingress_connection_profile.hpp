#pragma once

#include <string>

struct sqlite3;

namespace anonsync {
namespace persistence {

// Process-local evidence captured only after an unpublished candidate has
// passed the complete durable-file connection profile. Requested flags are not
// authority: file backing, access mode, connection serialization, and the exact
// top-level sqlite3_vfs object are observed before a successful handle is
// published.
struct SqliteConnectionEvidence {
    int requested_flags{0};
    int effective_flags{0};
    int observed_read_only{-1};
    bool requested_vfs_was_explicit{false};
    bool file_backing_verified{false};
    bool access_mode_verified{false};
    bool serialized_mutex_verified{false};
    bool vfs_identity_verified{false};
    bool vfs_name_diagnostic_available{false};
    std::string pinned_vfs_name;
    std::string observed_vfs_stack;
    std::string observed_main_filename;
};

// Opens only durable, file-backed, serialized SQLite connections. This is a
// deliberately smaller contract than sqlite3_open_v2():
//
//   * one canonical access tuple: RO, RW, or RW|CREATE;
//   * SQLITE_OPEN_FULLMUTEX is mandatory;
//   * URI, MEMORY, NOMUTEX, and SHAREDCACHE control planes are rejected;
//   * only explicitly allow-listed application flags are accepted;
//   * PRIVATECACHE is imposed on the effective open profile;
//   * the opened main database must report a concrete backing filename;
//   * SQLITE_FCNTL_VFS_POINTER must report the exact preselected VFS object.
//
// SQLITE_FCNTL_VFSNAME is retained only as optional diagnostics because SQLite
// documents that file-control as diagnostic-only and not guaranteed to act.
// On successful return, *published_database is non-null and verified. On input
// or post-open verification failure it is null. SQLite may still return a
// failed diagnostic handle for an ordinary open failure; that handle is
// published solely for sqlite3_errmsg() compatibility and carries no verified
// connection evidence.
[[nodiscard]] int open_verified_sqlite_database(
    const char* filename,
    sqlite3** published_database,
    int flags,
    const char* requested_vfs) noexcept;

[[nodiscard]] int open_verified_sqlite_database(
    const char* filename,
    sqlite3** published_database,
    int flags,
    const char* requested_vfs,
    SqliteConnectionEvidence* evidence) noexcept;

}  // namespace persistence
}  // namespace anonsync
