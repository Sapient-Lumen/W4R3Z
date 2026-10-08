#pragma once

#include "sync_process_incarnation.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

struct sqlite3;

namespace anonsync {

class SqliteDescriptorRootedVfs;

// Capability granted to one private descriptor-rooted registration. The
// read-only form is not merely an sqlite3_open_v2 flag: the wrapper removes
// CREATE/READWRITE authority from every delegated family open and rejects
// write, truncate, delete, and shared-memory creation callbacks. It is intended
// for forensic observation where an unexpected SQLite recovery path must fail
// rather than repair the selected deployment.
enum class SqliteDescriptorRootedVfsAccess : std::uint8_t {
    ReadWriteExisting = 1U,
    ReadOnlyExisting = 2U,
};

// Stable identity of one approved SQLite namespace object. Numeric device and
// inode values are evidence about the exact retained parent and database file,
// not portable identifiers. They are intentionally exposed so an
// administrative request can refuse a byte-identical replacement at the same
// pathname.
struct SqlitePathIdentity final {
    std::uint64_t parent_device = 0;
    std::uint64_t parent_inode = 0;
    std::uint64_t database_device = 0;
    std::uint64_t database_inode = 0;

    [[nodiscard]] bool operator==(
        const SqlitePathIdentity&) const noexcept = default;
};

// Scope-bound, process-bound proof that a SQLite database path is rooted in a
// directory chain containing no symbolic-link components. The parent directory
// descriptor is kept open so later checks can compare the pathname's current
// identity with the directory that was approved before SQLite was opened. A
// fork child may neither inspect nor destroy an inherited guard.
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

    // Return the exact retained parent and bound main-file identity after
    // rechecking the namespace. Existing-database administrative requests use
    // this token to reject path replacement between inspection and mutation.
    [[nodiscard]] SqlitePathIdentity bound_path_identity_or_throw(
        const std::string& label) const;

    // Re-check the parent directory identity and every configured family
    // member. Existing members must be regular files and never symlinks.
    void verify_family_or_throw(const std::string& label) const;

    // A portable SQLite snapshot is exactly one main database file.  WAL,
    // shared-memory, rollback-journal, and other configured sidecars are not
    // part of that byte identity and therefore must be absent before the main
    // file can be promoted as sealed snapshot evidence.
    void verify_sidecars_absent_or_throw(const std::string& label) const;

    // Bind a normal open file descriptor (for example an adjacent lock file)
    // to the approved main path identity.
    void verify_open_file_descriptor_or_throw(int fd, const std::string& label);

    // Open the approved main file relative to the retained parent directory.
    // The returned descriptor is O_RDONLY, O_CLOEXEC, O_NOFOLLOW, regular, and
    // single-linked. It is already bound to the path identity approved by the
    // guard. The caller owns the returned descriptor. This offline primitive
    // must not be used while any SQLite connection in this process may hold a
    // POSIX record lock on the same inode: closing any independently opened
    // descriptor can release every process-associated lock on that file. Live
    // database owners must use SqliteDescriptorRootedVfs evidence methods.
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
    friend class SqliteDescriptorRootedVfs;
    friend std::unique_ptr<SqliteDescriptorRootedVfs>
    register_sqlite_descriptor_rooted_vfs_or_throw(
        const SqlitePathFamilyGuard&,
        SqliteDescriptorRootedVfsAccess,
        const std::string&);
    friend std::unique_ptr<SqliteDescriptorRootedVfs>
    register_sqlite_descriptor_rooted_vfs_or_throw(
        const SqlitePathFamilyGuard&,
        const std::string&);

    void require_current_process_noexcept() const noexcept;
    void require_current_process_or_throw(std::string_view label) const;
    void transfer_from_noexcept(SqlitePathFamilyGuard& other) noexcept;
    void clear_moved_from_noexcept() noexcept;

    SyncProcessIncarnation process_id_;
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

// One private SQLite VFS registration rooted at a duplicated parent-directory
// descriptor from SqlitePathFamilyGuard. xFullPathname preserves the exact
// logical deployment pathname used by database bindings, while xOpen, xAccess,
// and xDelete translate the main file and its reviewed SQLite sidecars through
// /proc/self/fd/<dirfd>. Registration precomputes immutable exact logical,
// basename, and descriptor-rooted paths for all four family members. The
// registration also owns one sqlite3_create_filename() family for the mapped
// main, rollback-journal, and WAL names. Each delegated Unix sqlite3_file
// borrows the corresponding stable view until xClose; this is required because
// SQLite's Unix VFS later interprets the retained pointer with sqlite3_uri_*()
// and sqlite3_filename_*(), whose hidden layout cannot be replaced by an
// ordinary NUL-terminated std::string. No callback rebuilds or heap-retains a
// path. The delegated Unix VFS applies O_NOFOLLOW to each final member. The
// wrapper also
// requires every opened, accessed, deleted, or mapped family name to be absent
// or a regular single-link entry as appropriate, then applies HAS_MOVED to each
// xOpen result. This closes the symlink and pre-existing hard-link forms of
// redirection for the main file, rollback journal, WAL, and shared-memory
// family inside the retained directory. Registration additionally requires
// Linux statx mount identity, freezes the retained parent mount, and requires
// every existing main, journal, WAL, or SHM name to remain on that exact mount.
// This rejects same-namespace bind-mount substitution even when st_dev is
// unchanged, without opening an auxiliary descriptor that could disturb
// SQLite's process-associated POSIX locks.
// Anonymous xOpen requests are rejected rather than delegated, so temporary
// SQLite files cannot spill outside that authority; product connections use
// temp_store=MEMORY. DELETEONCLOSE is rejected for every named member so a
// malformed direct caller cannot defer family-name deletion to xClose.
// xFileControl likewise denies ambient temporary-name generation, NULL_IO
// descriptor invalidation, and lock-proxy pathname selection. Pointer-bearing
// controls handled by the retained Unix VFS are rejected with SQLITE_MISUSE
// when malformed callers supply no argument rather than being allowed to
// dereference null below the authority boundary.
// Mount-namespace identity is re-proved at pathname-resolution frontiers:
// open, access, delete, full-path, file-control, shared-memory map/unmap, and
// close. These boundaries also re-prove the exact retained parent descriptor
// and its /proc/self/fd bridge. Descriptor-only page I/O, locking, syncing, and
// already-open mappings pay only the process-incarnation check. Main-handle
// close fail-stops rather than delegate if the retained main or shared-memory
// family name has become unsafe, because Unix cleanup may unlink the SHM name.
// Main-database xOpen additionally requires the current logical entry to match
// the exact retained inode both before and after the delegated Unix open, then
// requires SQLITE_FCNTL_HAS_MOVED to report that the delegated file still
// occupies that entry before SQLite recovery can begin.
// Dynamic extension loading and Unix VFS syscall-table replacement are denied
// rather than delegated because neither belongs to database-family authority.
// This is a namespace binding, not protection against a same-UID adversary who
// can mutate link counts after an already-open handle has passed attestation.
//
// The object is process-bound, non-movable, and must outlive every SQLite
// connection opened with name(). Destruction unregisters the VFS; callers must
// close the connection first.
class SqliteDescriptorRootedVfs final {
public:
    ~SqliteDescriptorRootedVfs();
    SqliteDescriptorRootedVfs(const SqliteDescriptorRootedVfs&) = delete;
    SqliteDescriptorRootedVfs& operator=(
        const SqliteDescriptorRootedVfs&) = delete;
    SqliteDescriptorRootedVfs(SqliteDescriptorRootedVfs&&) = delete;
    SqliteDescriptorRootedVfs& operator=(
        SqliteDescriptorRootedVfs&&) = delete;

    [[nodiscard]] const char* name() const noexcept;

    // Prove that one live connection was opened through this exact private VFS,
    // still names the manifest-selected logical path, and still has the exact
    // retained main inode at the descriptor-rooted family name. This proof is
    // intentionally independent of ambient ancestor-path revalidation; product
    // owners apply both so a renamed-but-retained family is physically safe yet
    // no longer authorized for normal logical-path operation.
    void verify_open_database_or_throw(
        sqlite3* database,
        const std::string& label) const;

    // Read the exact retained main-file object before a connection is opened.
    // The delegated Unix VFS owns the temporary read-only sqlite3_file and its
    // close, so same-process SQLite lock bookkeeping is preserved even when a
    // different connection already has this inode open. This method refuses to
    // run while this private VFS has any live file objects.
    [[nodiscard]] std::string read_bounded_main_file_before_open_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label) const;

    // Read through the exact main sqlite3_file already owned by one live
    // connection. The connection mutex is held across handle attestation,
    // xFileSize, and xRead. No auxiliary POSIX descriptor is opened or closed.
    [[nodiscard]] std::string read_bounded_main_file_or_throw(
        sqlite3* database,
        std::uint64_t maximum_bytes,
        const std::string& label) const;

    // Inspect sidecars relative to the retained parent directory object, not
    // through the ambient pathname. The single-suffix form requires a suffix
    // that was included when the path family guard was created.
    void verify_sidecars_absent_or_throw(const std::string& label) const;
    void verify_sidecar_absent_or_throw(
        std::string_view suffix,
        const std::string& label) const;

    // Flush the exact live main sqlite3_file under the connection mutex, then
    // flush the retained parent directory descriptor. No same-inode POSIX file
    // descriptor is independently opened or closed while SQLite owns locks.
    void sync_main_file_and_parent_directory_or_throw(
        sqlite3* database,
        const std::string& label) const;

private:
    struct State;
    explicit SqliteDescriptorRootedVfs(std::unique_ptr<State> state) noexcept;

    std::unique_ptr<State> state_;

    friend std::unique_ptr<SqliteDescriptorRootedVfs>
    register_sqlite_descriptor_rooted_vfs_or_throw(
        const SqlitePathFamilyGuard&,
        SqliteDescriptorRootedVfsAccess,
        const std::string&);
    friend std::unique_ptr<SqliteDescriptorRootedVfs>
    register_sqlite_descriptor_rooted_vfs_or_throw(
        const SqlitePathFamilyGuard&,
        const std::string&);
};

[[nodiscard]] std::unique_ptr<SqliteDescriptorRootedVfs>
register_sqlite_descriptor_rooted_vfs_or_throw(
    const SqlitePathFamilyGuard& guard,
    SqliteDescriptorRootedVfsAccess access,
    const std::string& label);

// Compatibility surface for existing operational callers. New observation
// lanes should select access explicitly rather than inheriting write authority.
[[nodiscard]] std::unique_ptr<SqliteDescriptorRootedVfs>
register_sqlite_descriptor_rooted_vfs_or_throw(
    const SqlitePathFamilyGuard& guard,
    const std::string& label);

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
