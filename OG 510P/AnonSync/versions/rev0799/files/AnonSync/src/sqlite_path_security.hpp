#pragma once

#include <filesystem>
#include <string>
#include <vector>

struct sqlite3;

namespace anonsync {

// Scope-bound proof that a SQLite database path is rooted in a directory chain
// containing no symbolic-link components. The parent directory descriptor is
// kept open so later checks can compare the pathname's current identity with
// the directory that was approved before SQLite was opened.
class SqlitePathFamilyGuard final {
public:
    SqlitePathFamilyGuard() = default;
    ~SqlitePathFamilyGuard();
    SqlitePathFamilyGuard(const SqlitePathFamilyGuard&) = delete;
    SqlitePathFamilyGuard& operator=(const SqlitePathFamilyGuard&) = delete;
    SqlitePathFamilyGuard(SqlitePathFamilyGuard&& other) noexcept;
    SqlitePathFamilyGuard& operator=(SqlitePathFamilyGuard&& other) noexcept;

    const std::filesystem::path& database_path() const noexcept;
    bool parent_exists() const noexcept;
    bool database_existed_at_preflight() const noexcept;

    // Re-check the parent directory identity and every configured family
    // member. Existing members must be regular files and never symlinks.
    void verify_family_or_throw(const std::string& label) const;

    // A portable SQLite snapshot is exactly one main database file.  WAL,
    // shared-memory, rollback-journal, and other configured sidecars are not
    // part of that byte identity and therefore must be absent before the main
    // file can be promoted as sealed snapshot evidence.
    void verify_sidecars_absent_or_throw(const std::string& label) const;

    // Reassert that the retained parent directory remains owned by this
    // effective user and mode 0700.  Private staging capabilities must not
    // continue after their namespace becomes searchable or writable by others.
    void verify_private_parent_directory_or_throw(const std::string& label) const;

    // Bind a normal open file descriptor (for example an adjacent lock file)
    // to the approved main path identity.
    void verify_open_file_descriptor_or_throw(int fd, const std::string& label);

    // Open the approved main file relative to the retained parent directory.
    // The returned descriptor is O_RDONLY, O_CLOEXEC, O_NOFOLLOW, regular, and
    // single-linked.  It is already bound to the path identity approved by the
    // guard.  The caller owns the returned descriptor.
    int open_readonly_file_or_throw(const std::string& label);

    // Open the approved path as a private lock file relative to the retained
    // parent directory descriptor. The returned descriptor is O_RDWR,
    // O_CLOEXEC, O_NOFOLLOW, owned by the effective user, mode 0600, regular,
    // and single-linked. The caller owns the returned descriptor.
    int open_private_lock_file_or_throw(const std::string& label);

    // Bind the opened SQLite connection to the approved main database object.
    // This also checks SQLITE_FCNTL_HAS_MOVED where the SQLite build supports
    // it. Calling it again detects later main-file replacement or parent-path
    // rebinding while the guard is alive.
    void verify_open_database_or_throw(sqlite3* db, const std::string& label);

private:
    friend SqlitePathFamilyGuard guard_sqlite_path_family_or_throw(
        const std::filesystem::path&,
        bool,
        const std::vector<std::string>&,
        const std::string&);

    std::filesystem::path database_path_;
    std::filesystem::path parent_path_;
    std::string basename_;
    std::vector<std::string> sidecar_suffixes_;
    int parent_fd_ = -1;
    unsigned long long parent_device_ = 0;
    unsigned long long parent_inode_ = 0;
    bool parent_exists_ = false;
    bool database_existed_at_preflight_ = false;
    bool database_identity_bound_ = false;
    unsigned long long database_device_ = 0;
    unsigned long long database_inode_ = 0;
};

// The input is converted to an absolute, lexically-normal path. Existing
// components are traversed with fstatat/openat and O_NOFOLLOW. When requested,
// missing parent directories are created one component at a time with mode
// 0700 and then opened without following links. Family suffixes are relative
// to the database basename (for example "-wal", "-shm", and "-journal").
SqlitePathFamilyGuard guard_sqlite_path_family_or_throw(
    const std::filesystem::path& database_path,
    bool create_parent_directories,
    const std::vector<std::string>& sidecar_suffixes,
    const std::string& label);

// Convenience preflight for callers that do not need to retain directory
// identity. It still rejects symlinked/non-regular family members and symlinked
// parent components before returning.
void reject_unsafe_sqlite_path_family_or_throw(
    const std::filesystem::path& database_path,
    const std::vector<std::string>& sidecar_suffixes,
    const std::string& label);

}  // namespace anonsync
