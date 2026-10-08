#include "sqlite_path_security.hpp"
#include "sync_posix_directory_resolution.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"
#include "sync_posix_mount_namespace_authority.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <limits>
#include <mutex>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

class ScopedFd final {
public:
    ScopedFd() noexcept = default;
    explicit ScopedFd(int fd) noexcept : fd_(fd) {}
    ~ScopedFd() { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : fd_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    int get() const noexcept { return fd_; }
    int release() noexcept {
        const int out = fd_;
        fd_ = -1;
        return out;
    }
    void reset(int fd = -1) noexcept {
        if (fd_ >= 0) (void)::close(fd_);
        fd_ = fd;
    }

private:
    int fd_ = -1;
};

[[noreturn]] void throw_errno(const std::string& label,
                              const std::string& operation,
                              const fs::path& path,
                              int error_number = errno) {
    throw std::runtime_error(label + " " + operation + " failed for " +
                             path.generic_string() + ": " +
                             std::strerror(error_number));
}

bool same_identity(const struct stat& left, const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

bool same_stable_regular_file_observation(
    const struct stat& left,
    const struct stat& right) noexcept {
    if (!same_identity(left, right) || !S_ISREG(left.st_mode) ||
        !S_ISREG(right.st_mode) || left.st_nlink != 1 ||
        right.st_nlink != 1 || left.st_size != right.st_size ||
        left.st_blocks != right.st_blocks ||
        (left.st_mode & 07777) != (right.st_mode & 07777) ||
        left.st_uid != right.st_uid || left.st_gid != right.st_gid) {
        return false;
    }
#if defined(__linux__)
    return left.st_mtim.tv_sec == right.st_mtim.tv_sec &&
        left.st_mtim.tv_nsec == right.st_mtim.tv_nsec &&
        left.st_ctim.tv_sec == right.st_ctim.tv_sec &&
        left.st_ctim.tv_nsec == right.st_ctim.tv_nsec;
#else
    return true;
#endif
}

unsigned long long device_value(const struct stat& value) noexcept {
    return static_cast<unsigned long long>(value.st_dev);
}

unsigned long long inode_value(const struct stat& value) noexcept {
    return static_cast<unsigned long long>(value.st_ino);
}

fs::path absolute_normal_path_or_throw(const fs::path& raw_path,
                                       const std::string& label) {
    if (raw_path.empty()) throw std::runtime_error(label + " database path is required");
    std::error_code ec;
    fs::path absolute = fs::absolute(raw_path, ec);
    if (ec) {
        throw std::runtime_error(label + " database path could not be made absolute: " +
                                 ec.message());
    }
    absolute = absolute.lexically_normal();
    if (!absolute.is_absolute() || absolute.filename().empty() ||
        absolute.filename() == "." || absolute.filename() == "..") {
        throw std::runtime_error(label + " database path must name a file");
    }
    const std::string filename = absolute.filename().string();
    if (filename.find('\0') != std::string::npos) {
        throw std::runtime_error(label + " database filename contains a NUL byte");
    }
    return absolute;
}

void validate_suffixes_or_throw(const std::vector<std::string>& suffixes,
                                const std::string& label) {
    for (const std::string& suffix : suffixes) {
        if (suffix.empty() || suffix.find('/') != std::string::npos ||
            suffix.find('\0') != std::string::npos || suffix == "." || suffix == "..") {
            throw std::runtime_error(label + " contains an invalid SQLite family suffix");
        }
    }
}

int directory_open_flags() noexcept {
    int flags = O_RDONLY | O_DIRECTORY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    return flags;
}

struct DirectoryTraversalResult {
    ScopedFd fd;
    struct stat identity{};
    bool exists = false;
};

DirectoryTraversalResult traverse_directory_chain_or_throw(
    const fs::path& absolute_directory,
    bool create_missing,
    const std::string& label) {
    if (!absolute_directory.is_absolute()) {
        throw std::runtime_error(label + " internal directory traversal requires an absolute path");
    }

    ScopedFd current(::open("/", directory_open_flags()));
    if (current.get() < 0) throw_errno(label, "root directory open", "/");

    struct stat current_identity{};
    if (::fstat(current.get(), &current_identity) != 0) {
        throw_errno(label, "root directory fstat", "/");
    }
    if (!S_ISDIR(current_identity.st_mode)) {
        throw std::runtime_error(label + " root path is not a directory");
    }

    fs::path walked = "/";
    for (const fs::path& component_path : absolute_directory.relative_path()) {
        const std::string component = component_path.string();
        if (component.empty() || component == ".") continue;
        if (component == ".." || component.find('/') != std::string::npos ||
            component.find('\0') != std::string::npos) {
            throw std::runtime_error(label + " contains an unsafe parent path component");
        }
        walked /= component_path;

        struct stat before{};
        if (::fstatat(current.get(), component.c_str(), &before, AT_SYMLINK_NOFOLLOW) != 0) {
            const int status_error = errno;
            if (status_error != ENOENT) {
                throw_errno(label, "parent component inspection", walked, status_error);
            }
            if (!create_missing) return {};
            if (::mkdirat(current.get(), component.c_str(), 0700) != 0 && errno != EEXIST) {
                throw_errno(label, "parent component creation", walked);
            }
            if (::fstatat(current.get(), component.c_str(), &before, AT_SYMLINK_NOFOLLOW) != 0) {
                throw_errno(label, "created parent component inspection", walked);
            }
        }

        if (S_ISLNK(before.st_mode)) {
            throw std::runtime_error(label + " refuses symbolic-link parent component: " +
                                     walked.generic_string());
        }
        if (!S_ISDIR(before.st_mode)) {
            throw std::runtime_error(label + " parent component is not a directory: " +
                                     walked.generic_string());
        }

        ScopedFd next(::openat(current.get(), component.c_str(), directory_open_flags()));
        if (next.get() < 0) throw_errno(label, "parent component open", walked);
        struct stat after{};
        if (::fstat(next.get(), &after) != 0) {
            throw_errno(label, "parent component fstat", walked);
        }
        if (!S_ISDIR(after.st_mode) || !same_identity(before, after)) {
            throw std::runtime_error(label + " parent component changed during secure traversal: " +
                                     walked.generic_string());
        }
        current = std::move(next);
        current_identity = after;
    }

    DirectoryTraversalResult out;
    out.fd = std::move(current);
    out.identity = current_identity;
    out.exists = true;
    return out;
}

struct FamilyMemberIdentity {
    bool exists = false;
    struct stat status{};
};

FamilyMemberIdentity inspect_family_member_or_throw(int parent_fd,
                                                    const std::string& name,
                                                    const fs::path& display_path,
                                                    const std::string& label) {
    struct stat status{};
    if (::fstatat(parent_fd, name.c_str(), &status, AT_SYMLINK_NOFOLLOW) != 0) {
        const int status_error = errno;
        if (status_error == ENOENT) return {};
        throw_errno(label, "SQLite family member inspection", display_path, status_error);
    }
    if (S_ISLNK(status.st_mode)) {
        throw std::runtime_error(label + " refuses symbolic-link SQLite family member: " +
                                 display_path.generic_string());
    }
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label + " refuses non-regular SQLite family member: " +
                                 display_path.generic_string());
    }
    if (status.st_nlink != 1) {
        throw std::runtime_error(label + " refuses multiply-linked SQLite family member: " +
                                 display_path.generic_string());
    }
    FamilyMemberIdentity out;
    out.exists = true;
    out.status = status;
    return out;
}


}  // namespace

SqlitePathFamilyGuard::~SqlitePathFamilyGuard() {
    require_current_process_noexcept();
    if (parent_fd_ >= 0) (void)::close(parent_fd_);
}

SqlitePathFamilyGuard::SqlitePathFamilyGuard(
    SqlitePathFamilyGuard&& other) noexcept {
    other.require_current_process_noexcept();
    transfer_from_noexcept(other);
}

SqlitePathFamilyGuard& SqlitePathFamilyGuard::operator=(
    SqlitePathFamilyGuard&& other) noexcept {
    require_current_process_noexcept();
    other.require_current_process_noexcept();
    if (this == &other) return *this;
    if (parent_fd_ >= 0) (void)::close(parent_fd_);
    transfer_from_noexcept(other);
    return *this;
}

void SqlitePathFamilyGuard::transfer_from_noexcept(
    SqlitePathFamilyGuard& other) noexcept {
    process_id_ = other.process_id_;
    database_path_ = std::move(other.database_path_);
    parent_path_ = std::move(other.parent_path_);
    basename_ = std::move(other.basename_);
    sidecar_suffixes_ = std::move(other.sidecar_suffixes_);
    parent_fd_ = other.parent_fd_;
    parent_device_ = other.parent_device_;
    parent_inode_ = other.parent_inode_;
    parent_exists_ = other.parent_exists_;
    database_existed_at_preflight_ = other.database_existed_at_preflight_;
    database_identity_bound_ = other.database_identity_bound_;
    database_device_ = other.database_device_;
    database_inode_ = other.database_inode_;
    other.clear_moved_from_noexcept();
}

void SqlitePathFamilyGuard::clear_moved_from_noexcept() noexcept {
    process_id_ = {};
    parent_fd_ = -1;
    parent_device_ = 0;
    parent_inode_ = 0;
    parent_exists_ = false;
    database_existed_at_preflight_ = false;
    database_identity_bound_ = false;
    database_device_ = 0;
    database_inode_ = 0;
    database_path_.clear();
    parent_path_.clear();
    basename_.clear();
    sidecar_suffixes_.clear();
}

void SqlitePathFamilyGuard::require_current_process_noexcept() const noexcept {
    if (process_id_.valid() && !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
}

void SqlitePathFamilyGuard::require_current_process_or_throw(
    std::string_view label) const {
    if (!process_id_.valid()) {
        throw std::logic_error(std::string(label) +
                               " SQLite path guard is not initialized");
    }
    require_sync_process_incarnation_or_fail_stop(process_id_, label);
}

const fs::path& SqlitePathFamilyGuard::database_path() const noexcept {
    require_current_process_noexcept();
    return database_path_;
}

bool SqlitePathFamilyGuard::parent_exists() const noexcept {
    require_current_process_noexcept();
    return parent_exists_;
}

bool SqlitePathFamilyGuard::database_existed_at_preflight() const noexcept {
    require_current_process_noexcept();
    return database_existed_at_preflight_;
}

SqlitePathIdentity SqlitePathFamilyGuard::bound_path_identity_or_throw(
    const std::string& label) const {
    require_current_process_or_throw(label);
    if (!parent_exists_ || parent_fd_ < 0 || !database_identity_bound_) {
        throw std::runtime_error(
            label + " requires a bound existing SQLite namespace identity");
    }
    verify_family_or_throw(label + " namespace recheck");
    const FamilyMemberIdentity current = inspect_family_member_or_throw(
        parent_fd_, basename_, database_path_, label + " main identity recheck");
    if (!current.exists || device_value(current.status) != database_device_ ||
        inode_value(current.status) != database_inode_) {
        throw std::runtime_error(
            label + " SQLite main database identity changed: " +
            database_path_.generic_string());
    }
    return SqlitePathIdentity{
        static_cast<std::uint64_t>(parent_device_),
        static_cast<std::uint64_t>(parent_inode_),
        static_cast<std::uint64_t>(database_device_),
        static_cast<std::uint64_t>(database_inode_)};
}

void SqlitePathFamilyGuard::verify_family_or_throw(const std::string& label) const {
    require_current_process_or_throw(label);
    if (!parent_exists_ || parent_fd_ < 0) {
        throw std::runtime_error(label + " SQLite parent directory was not established");
    }

    DirectoryTraversalResult current = traverse_directory_chain_or_throw(parent_path_, false, label);
    if (!current.exists || device_value(current.identity) != parent_device_ ||
        inode_value(current.identity) != parent_inode_) {
        throw std::runtime_error(label + " SQLite parent directory identity changed: " +
                                 parent_path_.generic_string());
    }

    (void)inspect_family_member_or_throw(parent_fd_, basename_, database_path_, label);
    for (const std::string& suffix : sidecar_suffixes_) {
        (void)inspect_family_member_or_throw(parent_fd_, basename_ + suffix,
                                             fs::path(database_path_.string() + suffix), label);
    }
}

void SqlitePathFamilyGuard::verify_sidecars_absent_or_throw(
    const std::string& label) const {
    verify_family_or_throw(label);
    for (const std::string& suffix : sidecar_suffixes_) {
        const FamilyMemberIdentity member = inspect_family_member_or_throw(
            parent_fd_, basename_ + suffix,
            fs::path(database_path_.string() + suffix), label);
        if (member.exists) {
            throw std::runtime_error(
                label + " refuses SQLite snapshot sidecar " + suffix);
        }
    }
}

void SqlitePathFamilyGuard::verify_open_file_descriptor_or_throw(
    int fd,
    const std::string& label) {
    require_current_process_or_throw(label);
    if (fd < 0) throw std::runtime_error(label + " file descriptor is invalid");
    verify_family_or_throw(label);
    const FamilyMemberIdentity expected = inspect_family_member_or_throw(
        parent_fd_, basename_, database_path_, label);
    if (!expected.exists) {
        throw std::runtime_error(label + " approved file does not exist: " +
                                 database_path_.generic_string());
    }
    if (database_identity_bound_) {
        if (device_value(expected.status) != database_device_ ||
            inode_value(expected.status) != database_inode_) {
            throw std::runtime_error(label + " approved file identity changed before descriptor binding: " +
                                     database_path_.generic_string());
        }
    } else {
        database_device_ = device_value(expected.status);
        database_inode_ = inode_value(expected.status);
        database_identity_bound_ = true;
    }
    struct stat opened_status{};
    if (::fstat(fd, &opened_status) != 0) {
        throw_errno(label, "opened file descriptor fstat", database_path_);
    }
    if (!S_ISREG(opened_status.st_mode) || opened_status.st_nlink != 1 ||
        !same_identity(expected.status, opened_status)) {
        throw std::runtime_error(label + " opened file descriptor is outside the approved path identity");
    }
}

int SqlitePathFamilyGuard::open_readonly_file_or_throw(
    const std::string& label) {
    require_current_process_or_throw(label);
    if (!parent_exists_ || parent_fd_ < 0) {
        throw std::runtime_error(label + " parent directory was not established");
    }
    verify_family_or_throw(label);

    int flags = O_RDONLY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    ScopedFd opened(::openat(parent_fd_, basename_.c_str(), flags));
    if (opened.get() < 0) {
        throw_errno(label, "read-only file open", database_path_);
    }
    verify_open_file_descriptor_or_throw(opened.get(), label);
    return opened.release();
}

int SqlitePathFamilyGuard::open_private_lock_file_or_throw(
    const std::string& label) {
    require_current_process_or_throw(label);
    if (!parent_exists_ || parent_fd_ < 0) {
        throw std::runtime_error(label + " parent directory was not established");
    }
    verify_family_or_throw(label);

    int flags = O_RDWR | O_CREAT;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    ScopedFd opened(::openat(parent_fd_, basename_.c_str(), flags, 0600));
    if (opened.get() < 0) {
        throw_errno(label, "private lock open", database_path_);
    }

    verify_open_file_descriptor_or_throw(opened.get(), label);
    struct stat status{};
    if (::fstat(opened.get(), &status) != 0) {
        throw_errno(label, "private lock fstat", database_path_);
    }
    if (status.st_uid != ::geteuid()) {
        throw std::runtime_error(label + " refuses lock file owned by another user: " +
                                 database_path_.generic_string());
    }
    if (::fchmod(opened.get(), 0600) != 0) {
        throw_errno(label, "private lock chmod", database_path_);
    }
    verify_open_file_descriptor_or_throw(opened.get(), label);
    return opened.release();
}

void SqlitePathFamilyGuard::verify_open_database_or_throw(sqlite3* db,
                                                          const std::string& label) {
    require_current_process_or_throw(label);
    if (db == nullptr) throw std::runtime_error(label + " SQLite database handle is null");
    verify_family_or_throw(label);

    const FamilyMemberIdentity expected = inspect_family_member_or_throw(
        parent_fd_, basename_, database_path_, label);
    if (!expected.exists) {
        throw std::runtime_error(label + " SQLite main database was not created or opened: " +
                                 database_path_.generic_string());
    }

    if (database_identity_bound_) {
        if (device_value(expected.status) != database_device_ ||
            inode_value(expected.status) != database_inode_) {
            throw std::runtime_error(label + " SQLite main database identity changed while open: " +
                                     database_path_.generic_string());
        }
    } else {
        database_device_ = device_value(expected.status);
        database_inode_ = inode_value(expected.status);
        database_identity_bound_ = true;
    }

    const char* opened_name = sqlite3_db_filename(db, "main");
    if (opened_name == nullptr || *opened_name == '\0') {
        throw std::runtime_error(label + " SQLite did not expose a main database filename");
    }
    struct stat opened_status{};
    if (::stat(opened_name, &opened_status) != 0) {
        throw_errno(label, "opened SQLite database stat", opened_name);
    }
    if (!S_ISREG(opened_status.st_mode) || !same_identity(expected.status, opened_status)) {
        throw std::runtime_error(label + " SQLite opened a database outside the approved path identity");
    }

#ifdef SQLITE_FCNTL_HAS_MOVED
    int moved = 0;
    const int moved_rc = sqlite3_file_control(db, "main", SQLITE_FCNTL_HAS_MOVED, &moved);
    if (moved_rc == SQLITE_OK && moved != 0) {
        throw std::runtime_error(label + " SQLite reports that the main database moved after open");
    }
#endif
}

struct SqliteDescriptorRootedVfs::State final {
    enum class FamilyMember : std::uint8_t {
        Main = 1U,
        RollbackJournal = 2U,
        Wal = 3U,
        SharedMemory = 4U,
    };

    struct WrappedFile final {
        sqlite3_file public_file{};
        State* state = nullptr;
        const sqlite3_io_methods* base_methods = nullptr;
        const char* retained_path = nullptr;
        FamilyMember member = FamilyMember::Main;
    };

    sqlite3_vfs vfs{};
    sqlite3_vfs* base = nullptr;
    SyncProcessIncarnation process_id;
    SyncPosixMountNamespaceAuthority mount_namespace_authority;
    SyncPosixDirectoryResolutionCapability directory_resolution_capability =
        SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
    SyncPosixMountIdentity retained_parent_mount;
    mutable std::mutex mount_namespace_mutex;
    mutable std::mutex file_lifecycle_mutex;
    int parent_fd = -1;
    unsigned long long parent_device = 0;
    unsigned long long parent_inode = 0;
    unsigned long long main_device = 0;
    unsigned long long main_inode = 0;
    std::string logical_main_path;
    std::string basename;
    std::vector<std::string> sidecar_suffixes;
    std::string descriptor_prefix;
    std::array<std::string, 4U> family_basenames;
    std::array<std::string, 4U> logical_family_paths;
    std::array<std::string, 4U> descriptor_family_paths;
    std::string vfs_name;
    std::size_t base_file_offset = 0U;
    std::atomic<std::uint64_t> open_files{0U};
    bool registered = false;

    ~State() {
        // State destruction also runs while registration is being assembled.
        // A failed namespace capture must be allowed to unwind an otherwise
        // empty state; every initialized authority is re-proved before any
        // descriptor or registration can be released.
        require_current_process_noexcept();
        if (mount_namespace_authority.initialized()) {
            try {
                const std::lock_guard<std::mutex> lock(mount_namespace_mutex);
                mount_namespace_authority.verify_or_throw(
                    "descriptor-rooted SQLite VFS destruction");
            } catch (...) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
        } else if (registered || open_files.load(std::memory_order_acquire) != 0U ||
                   parent_fd >= 0) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        if (open_files.load(std::memory_order_acquire) != 0U) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        if (registered) {
            if (sqlite3_vfs_unregister(&vfs) != SQLITE_OK) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            registered = false;
        }
        if (parent_fd >= 0) {
            (void)::close(parent_fd);
            parent_fd = -1;
        }
    }

    [[nodiscard]] static State& from(sqlite3_vfs* vfs_pointer) noexcept {
        if (vfs_pointer == nullptr || vfs_pointer->pAppData == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return *static_cast<State*>(vfs_pointer->pAppData);
    }

    [[nodiscard]] static WrappedFile& from(sqlite3_file* file) noexcept {
        if (file == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        auto& wrapped = *reinterpret_cast<WrappedFile*>(file);
        if (wrapped.state == nullptr || wrapped.base_methods == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        // Most sqlite3_io_methods operate only on an already-open descriptor.
        // Re-opening and fstat'ing /proc/thread-self/ns/mnt for every page read,
        // write, lock, or sync is both unnecessary for descriptor authority and
        // prohibitively expensive. Path-resolving callbacks use from_context().
        wrapped.state->require_current_process_noexcept();
        wrapped.state->clear_local_error_noexcept();
        return wrapped;
    }

    [[nodiscard]] static WrappedFile& from_context(
        sqlite3_file* file) noexcept {
        WrappedFile& wrapped = from(file);
        wrapped.state->require_current_context_noexcept();
        return wrapped;
    }

    [[nodiscard]] static sqlite3_file* base_file(
        WrappedFile& wrapped) noexcept {
        auto* const bytes = reinterpret_cast<unsigned char*>(&wrapped);
        return reinterpret_cast<sqlite3_file*>(
            bytes + wrapped.state->base_file_offset);
    }

    struct LocalErrorSlot final {
        const State* owner = nullptr;
        std::array<char, 512> buffer{};
    };

    [[nodiscard]] static LocalErrorSlot& local_error_slot_noexcept() noexcept {
        // SQLite asks xGetLastError on the same thread that observed the VFS
        // failure. A thread-local, registration-tagged slot keeps independent
        // connections from racing or leaking diagnostics into one another while
        // avoiding locks and allocation inside noexcept VFS callbacks.
        static thread_local LocalErrorSlot slot{};
        return slot;
    }

    void clear_local_error_noexcept() const noexcept {
        auto& slot = local_error_slot_noexcept();
        slot.owner = this;
        slot.buffer[0] = '\0';
    }

    void set_local_error_noexcept(
        std::string_view operation,
        std::string_view detail) const noexcept {
        auto& slot = local_error_slot_noexcept();
        slot.owner = this;
        auto& buffer = slot.buffer;
        constexpr std::size_t kMaximumPrintable =
            static_cast<std::size_t>(std::numeric_limits<int>::max());
        const int operation_bytes = static_cast<int>(
            std::min(operation.size(), kMaximumPrintable));
        const int detail_bytes = static_cast<int>(
            std::min(detail.size(), kMaximumPrintable));
        (void)std::snprintf(
            buffer.data(), buffer.size(), "%.*s: %.*s",
            operation_bytes, operation.data(), detail_bytes, detail.data());
        buffer.back() = '\0';
    }

    void require_current_process_noexcept() const noexcept {
        if (!process_id.valid() ||
            !sync_process_incarnation_is_current(process_id)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
    }

    [[nodiscard]] bool retained_parent_bridge_is_current_noexcept()
        const noexcept {
        if (parent_fd < 0 || descriptor_prefix.empty()) return false;

        struct stat retained {};
        if (::fstat(parent_fd, &retained) != 0 ||
            !S_ISDIR(retained.st_mode) ||
            device_value(retained) != parent_device ||
            inode_value(retained) != parent_inode) {
            return false;
        }

        // The delegated Unix VFS resolves paths through this procfs bridge.
        // Mount-namespace identity alone does not prove that /proc has not
        // been overmounted inside the same namespace, and a process-global
        // descriptor table permits accidental close/reuse. Re-prove both the
        // retained descriptor and the bridge target at every path frontier.
        struct stat bridged {};
        if (::stat(descriptor_prefix.c_str(), &bridged) != 0 ||
            !S_ISDIR(bridged.st_mode) ||
            device_value(bridged) != parent_device ||
            inode_value(bridged) != parent_inode) {
            return false;
        }

        try {
            return sync_posix_capture_mount_identity_or_throw(
                       parent_fd, directory_resolution_capability,
                       "descriptor-rooted SQLite retained parent mount") ==
                retained_parent_mount;
        } catch (...) {
            return false;
        }
    }

    void require_current_context_or_throw(
        std::string_view label) const {
        require_current_process_noexcept();
        const std::lock_guard<std::mutex> lock(mount_namespace_mutex);
        mount_namespace_authority.verify_or_throw(label);
        if (!retained_parent_bridge_is_current_noexcept()) {
            throw std::runtime_error(
                std::string(label) +
                " retained parent descriptor or procfs bridge changed");
        }
    }

    void require_current_context_noexcept() const noexcept {
        require_current_process_noexcept();
        try {
            const std::lock_guard<std::mutex> lock(mount_namespace_mutex);
            mount_namespace_authority.verify_or_throw(
                "descriptor-rooted SQLite VFS callback");
            if (!retained_parent_bridge_is_current_noexcept()) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
        } catch (...) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
    }

    [[nodiscard]] FamilyMemberIdentity retained_main_observation_or_throw(
        const std::string& label) const {
        require_current_context_or_throw(label);
        const FamilyMemberIdentity named_main = inspect_family_member_or_throw(
            parent_fd, basename, fs::path(logical_main_path), label);
        if (!named_main.exists || named_main.status.st_nlink != 1 ||
            device_value(named_main.status) != main_device ||
            inode_value(named_main.status) != main_inode) {
            throw std::runtime_error(
                label +
                " SQLite main pathname no longer names the retained file");
        }
        const SyncPosixRelativeMountObservation mount =
            sync_posix_observe_relative_mount_noexcept(
                parent_fd, basename.c_str(),
                directory_resolution_capability, retained_parent_mount);
        if (mount.disposition !=
            SyncPosixRelativeMountDisposition::RetainedMount) {
            throw std::runtime_error(
                label +
                " SQLite main pathname crossed the retained parent mount");
        }
        return named_main;
    }

    void verify_retained_namespace_or_throw(
        const std::string& label) const {
        (void)retained_main_observation_or_throw(label);
    }

    [[nodiscard]] bool suffix_is_configured(
        std::string_view suffix) const noexcept {
        return std::any_of(
            sidecar_suffixes.begin(), sidecar_suffixes.end(),
            [suffix](const std::string& configured) {
                return suffix == configured;
            });
    }

    void verify_sidecar_absent_or_throw(
        std::string_view suffix,
        const std::string& label) const {
        verify_retained_namespace_or_throw(label);
        if (!suffix_is_configured(suffix)) {
            throw std::invalid_argument(
                label + " requested an unconfigured SQLite sidecar suffix");
        }
        const std::string member = basename + std::string(suffix);
        const fs::path display(logical_main_path + std::string(suffix));
        const FamilyMemberIdentity observed = inspect_family_member_or_throw(
            parent_fd, member, display, label);
        if (observed.exists) {
            throw std::runtime_error(
                label + " SQLite sidecar must be absent: " +
                display.generic_string());
        }
    }

    [[nodiscard]] static std::string read_file_through_sqlite_or_throw(
        sqlite3_file* file,
        std::uint64_t maximum_bytes,
        const std::string& label) {
        if (file == nullptr || file->pMethods == nullptr ||
            file->pMethods->xFileSize == nullptr ||
            file->pMethods->xRead == nullptr) {
            throw std::runtime_error(
                label + " SQLite file object has no readable I/O methods");
        }

        sqlite3_int64 signed_size = -1;
        const int size_result = file->pMethods->xFileSize(file, &signed_size);
        if (size_result != SQLITE_OK) {
            throw std::runtime_error(
                label + " SQLite xFileSize failed with code " +
                std::to_string(size_result));
        }
        if (signed_size < 0) {
            throw std::runtime_error(
                label + " retained SQLite main file has negative size");
        }
        const std::uint64_t bytes = static_cast<std::uint64_t>(signed_size);
        if (bytes > maximum_bytes ||
            bytes > static_cast<std::uint64_t>(
                        std::numeric_limits<std::size_t>::max())) {
            throw std::runtime_error(
                label + " retained SQLite main file exceeds the byte limit");
        }

        std::string output(static_cast<std::size_t>(bytes), '\0');
        std::size_t offset = 0U;
        while (offset < output.size()) {
            const std::size_t request = std::min<std::size_t>(
                output.size() - offset,
                static_cast<std::size_t>(std::numeric_limits<int>::max()));
            const int read_result = file->pMethods->xRead(
                file, output.data() + offset, static_cast<int>(request),
                static_cast<sqlite3_int64>(offset));
            if (read_result != SQLITE_OK) {
                throw std::runtime_error(
                    label + " SQLite xRead failed with code " +
                    std::to_string(read_result));
            }
            offset += request;
        }

        sqlite3_int64 signed_size_after = -1;
        const int size_after_result =
            file->pMethods->xFileSize(file, &signed_size_after);
        if (size_after_result != SQLITE_OK) {
            throw std::runtime_error(
                label + " post-read SQLite xFileSize failed with code " +
                std::to_string(size_after_result));
        }
        if (signed_size_after != signed_size) {
            throw std::runtime_error(
                label + " retained SQLite main file changed size during read");
        }
        return output;
    }

    [[nodiscard]] std::string
    read_bounded_main_file_before_open_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label) const {
        require_current_context_or_throw(label);
        const std::lock_guard<std::mutex> lifecycle_lock(file_lifecycle_mutex);
        if (open_files.load(std::memory_order_acquire) != 0U) {
            throw std::logic_error(
                label + " pre-open SQLite inspection requires no live files");
        }
        if (base == nullptr || base->xOpen == nullptr || base->szOsFile <= 0) {
            throw std::logic_error(
                label + " delegated Unix SQLite VFS is unavailable");
        }

        const FamilyMemberIdentity before =
            retained_main_observation_or_throw(label + " pre-read identity");
        const std::string& mapped = descriptor_family_paths[0U];
        auto* const file = static_cast<sqlite3_file*>(sqlite3_malloc64(
            static_cast<sqlite3_uint64>(base->szOsFile)));
        if (file == nullptr) {
            throw std::bad_alloc();
        }
        std::memset(file, 0, static_cast<std::size_t>(base->szOsFile));

        bool opened = false;
        const auto close_noexcept = [&]() noexcept {
            if (opened && file->pMethods != nullptr &&
                file->pMethods->xClose != nullptr) {
                (void)file->pMethods->xClose(file);
            }
            opened = false;
        };

        try {
            int output_flags = 0;
            const int open_result = base->xOpen(
                base, mapped.c_str(), file,
                SQLITE_OPEN_READONLY | SQLITE_OPEN_MAIN_DB |
                    SQLITE_OPEN_NOFOLLOW,
                &output_flags);
            opened = file->pMethods != nullptr;
            if (open_result != SQLITE_OK || !opened) {
                throw std::runtime_error(
                    label + " delegated Unix VFS read-only open failed with code " +
                    std::to_string(open_result));
            }
            if ((output_flags & SQLITE_OPEN_READONLY) == 0 ||
                (output_flags & SQLITE_OPEN_READWRITE) != 0) {
                throw std::runtime_error(
                    label + " delegated Unix VFS did not preserve read-only authority");
            }
            if (!opened_member_matches_retained_name_noexcept(
                    FamilyMember::Main, file)) {
                throw std::runtime_error(
                    label + " pre-open SQLite file no longer occupies the retained name");
            }

            std::string output = read_file_through_sqlite_or_throw(
                file, maximum_bytes, label);
            const FamilyMemberIdentity after =
                retained_main_observation_or_throw(label + " post-read identity");
            if (!same_stable_regular_file_observation(
                    before.status, after.status)) {
                throw std::runtime_error(
                    label + " retained SQLite main file changed during read");
            }

            const int close_result = file->pMethods->xClose(file);
            opened = false;
            file->pMethods = nullptr;
            if (close_result != SQLITE_OK) {
                throw std::runtime_error(
                    label + " delegated Unix VFS close failed with code " +
                    std::to_string(close_result));
            }
            sqlite3_free(file);
            return output;
        } catch (...) {
            close_noexcept();
            sqlite3_free(file);
            throw;
        }
    }

    [[nodiscard]] sqlite3_file* main_file_for_database_or_throw(
        sqlite3* database,
        const std::string& label) const {
        verify_retained_namespace_or_throw(label);

        const char* const opened_name = sqlite3_db_filename(database, "main");
        if (opened_name == nullptr ||
            std::string_view(opened_name) != logical_main_path) {
            throw std::runtime_error(
                label +
                " SQLite connection does not name the authorized logical path");
        }

        sqlite3_vfs* opened_vfs = nullptr;
        const int vfs_result = sqlite3_file_control(
            database, "main", SQLITE_FCNTL_VFS_POINTER, &opened_vfs);
        if (vfs_result != SQLITE_OK || opened_vfs != &vfs) {
            throw std::runtime_error(
                label +
                " SQLite connection was not opened through this exact private VFS");
        }

        sqlite3_file* opened_file = nullptr;
        const int file_result = sqlite3_file_control(
            database, "main", SQLITE_FCNTL_FILE_POINTER, &opened_file);
        if (file_result != SQLITE_OK || opened_file == nullptr ||
            opened_file->pMethods == nullptr) {
            throw std::runtime_error(
                label + " SQLite connection exposes no live main-file handle");
        }

        // VFS_POINTER was proved before interpreting the top-level sqlite3_file
        // as our wrapper. This binds the connection to this registration's exact
        // state and retained descriptor family.
        auto* const wrapped = reinterpret_cast<WrappedFile*>(opened_file);
        if (wrapped->state != this || wrapped->base_methods == nullptr ||
            wrapped->retained_path == nullptr ||
            wrapped->member != FamilyMember::Main ||
            open_files.load(std::memory_order_acquire) == 0U) {
            throw std::runtime_error(
                label +
                " SQLite main handle is outside this VFS registration state");
        }
        const sqlite3_io_methods* const expected_methods = methods_for_version(
            supported_methods_version(*wrapped->base_methods));
        if (expected_methods == nullptr ||
            opened_file->pMethods != expected_methods) {
            throw std::runtime_error(
                label +
                " SQLite main handle does not expose this VFS wrapper's I/O methods");
        }
        if (std::string_view(wrapped->retained_path) !=
            descriptor_family_paths[0U]) {
            throw std::runtime_error(
                label +
                " SQLite main handle does not retain the approved descriptor path");
        }

        sqlite3_file* const underlying = base_file(*wrapped);
        if (!opened_member_matches_retained_name_noexcept(
                FamilyMember::Main, underlying)) {
            throw std::runtime_error(
                label +
                " SQLite main handle no longer occupies the retained family name");
        }
        return opened_file;
    }

    [[nodiscard]] std::string read_bounded_main_file_or_throw(
        sqlite3* database,
        std::uint64_t maximum_bytes,
        const std::string& label) const {
        sqlite3_file* const file =
            main_file_for_database_or_throw(database, label);
        const FamilyMemberIdentity before =
            retained_main_observation_or_throw(label + " pre-read identity");
        std::string output = read_file_through_sqlite_or_throw(
            file, maximum_bytes, label);
        const FamilyMemberIdentity after =
            retained_main_observation_or_throw(label + " post-read identity");
        if (!same_stable_regular_file_observation(
                before.status, after.status)) {
            throw std::runtime_error(
                label + " retained SQLite main file changed during read");
        }
        auto* const wrapped = reinterpret_cast<WrappedFile*>(file);
        if (!opened_member_matches_retained_name_noexcept(
                FamilyMember::Main, base_file(*wrapped))) {
            throw std::runtime_error(
                label + " SQLite main handle moved during read");
        }
        return output;
    }

    void sync_main_file_and_parent_directory_or_throw(
        sqlite3* database,
        const std::string& label) const {
        sqlite3_file* const file =
            main_file_for_database_or_throw(database, label);
        const FamilyMemberIdentity before =
            retained_main_observation_or_throw(label + " pre-sync identity");
        if (file->pMethods == nullptr || file->pMethods->xSync == nullptr) {
            throw std::runtime_error(
                label + " SQLite main file exposes no sync method");
        }
        const int sync_result =
            file->pMethods->xSync(file, SQLITE_SYNC_FULL);
        if (sync_result != SQLITE_OK) {
            throw std::runtime_error(
                label + " SQLite main xSync failed with code " +
                std::to_string(sync_result));
        }
        for (;;) {
            if (::fsync(parent_fd) == 0) break;
            if (errno == EINTR) continue;
            throw_errno(
                label, "retained parent directory fsync",
                fs::path(logical_main_path).parent_path());
        }
        const FamilyMemberIdentity after =
            retained_main_observation_or_throw(label + " post-sync identity");
        if (!same_identity(before.status, after.status)) {
            throw std::runtime_error(
                label + " retained SQLite main identity changed during sync");
        }
        auto* const wrapped = reinterpret_cast<WrappedFile*>(file);
        if (!opened_member_matches_retained_name_noexcept(
                FamilyMember::Main, base_file(*wrapped))) {
            throw std::runtime_error(
                label + " SQLite main handle moved during sync");
        }
    }

    [[nodiscard]] static std::string_view suffix_for_member(
        FamilyMember member) noexcept {
        switch (member) {
            case FamilyMember::Main:
                return {};
            case FamilyMember::RollbackJournal:
                return "-journal";
            case FamilyMember::Wal:
                return "-wal";
            case FamilyMember::SharedMemory:
                return "-shm";
        }
        return {};
    }

    [[nodiscard]] static std::size_t family_member_index_noexcept(
        FamilyMember member) noexcept {
        switch (member) {
            case FamilyMember::Main:
                return 0U;
            case FamilyMember::RollbackJournal:
                return 1U;
            case FamilyMember::Wal:
                return 2U;
            case FamilyMember::SharedMemory:
                return 3U;
        }
        fail_stop_on_sync_process_capability_violation_noexcept();
    }

    [[nodiscard]] bool current_member_is_safe_noexcept(
        FamilyMember member,
        bool allow_absent) const noexcept {
        const std::string_view suffix = suffix_for_member(member);
        if (member != FamilyMember::Main && !suffix_is_configured(suffix)) {
            return false;
        }
        const std::string& filename =
            family_basenames[family_member_index_noexcept(member)];

        struct stat observed {};
        if (::fstatat(
                parent_fd, filename.c_str(), &observed,
                AT_SYMLINK_NOFOLLOW) != 0) {
            return allow_absent && errno == ENOENT;
        }
        if (!S_ISREG(observed.st_mode) || observed.st_nlink != 1) {
            return false;
        }
        const SyncPosixRelativeMountObservation mount =
            sync_posix_observe_relative_mount_noexcept(
                parent_fd, filename.c_str(),
                directory_resolution_capability, retained_parent_mount);
        if (mount.disposition !=
            SyncPosixRelativeMountDisposition::RetainedMount) {
            return false;
        }
        if (member == FamilyMember::Main) {
            return device_value(observed) == main_device &&
                inode_value(observed) == main_inode;
        }
        return true;
    }

    [[nodiscard]] bool current_main_path_matches_retained_identity_noexcept()
        const noexcept {
        return current_member_is_safe_noexcept(FamilyMember::Main, false);
    }

    [[nodiscard]] bool opened_member_matches_retained_name_noexcept(
        FamilyMember member,
        sqlite3_file* underlying) const noexcept {
        if (!current_member_is_safe_noexcept(member, false) ||
            underlying == nullptr || underlying->pMethods == nullptr ||
            underlying->pMethods->xFileControl == nullptr) {
            return false;
        }
#ifdef SQLITE_FCNTL_HAS_MOVED
        int moved = 0;
        return underlying->pMethods->xFileControl(
                   underlying, SQLITE_FCNTL_HAS_MOVED, &moved) == SQLITE_OK &&
            moved == 0;
#else
        (void)member;
        return false;
#endif
    }

    [[nodiscard]] bool map_path_noexcept(
        const char* raw_path,
        const std::string*& mapped,
        FamilyMember& member) const noexcept {
        mapped = nullptr;
        if (raw_path == nullptr || *raw_path == '\0') return false;
        const std::string_view observed(raw_path);
        constexpr std::array<FamilyMember, 4U> kMembers{
            FamilyMember::Main,
            FamilyMember::RollbackJournal,
            FamilyMember::Wal,
            FamilyMember::SharedMemory,
        };
        for (const FamilyMember candidate : kMembers) {
            const std::size_t index = family_member_index_noexcept(candidate);
            if (observed == logical_family_paths[index]) {
                member = candidate;
                mapped = &descriptor_family_paths[index];
                return mapped->size() + 1U <=
                    static_cast<std::size_t>(base->mxPathname);
            }
        }
        return false;
    }

    [[nodiscard]] static bool open_role_matches_member(
        FamilyMember member,
        int flags) noexcept {
        constexpr int kRoleMask =
            SQLITE_OPEN_MAIN_DB | SQLITE_OPEN_TEMP_DB |
            SQLITE_OPEN_TRANSIENT_DB | SQLITE_OPEN_MAIN_JOURNAL |
            SQLITE_OPEN_TEMP_JOURNAL | SQLITE_OPEN_SUBJOURNAL |
            SQLITE_OPEN_SUPER_JOURNAL | SQLITE_OPEN_WAL;
        const int role = flags & kRoleMask;
        switch (member) {
            case FamilyMember::Main:
                return role == SQLITE_OPEN_MAIN_DB;
            case FamilyMember::RollbackJournal:
                return role == SQLITE_OPEN_MAIN_JOURNAL;
            case FamilyMember::Wal:
                return role == SQLITE_OPEN_WAL;
            case FamilyMember::SharedMemory:
                // The Unix VFS reaches shared memory through xShmMap on the
                // exact main handle. A named xOpen of -shm is unexpected.
                return false;
        }
        return false;
    }

    [[nodiscard]] static const sqlite3_io_methods* methods_for_version(
        int version) noexcept {
        static const sqlite3_io_methods version_one{
            1,
            &close,
            &read,
            &write,
            &truncate,
            &sync,
            &file_size,
            &lock,
            &unlock,
            &check_reserved_lock,
            &file_control,
            &sector_size,
            &device_characteristics,
            nullptr,
            nullptr,
            nullptr,
            nullptr,
            nullptr,
            nullptr,
        };
        static const sqlite3_io_methods version_two{
            2,
            &close,
            &read,
            &write,
            &truncate,
            &sync,
            &file_size,
            &lock,
            &unlock,
            &check_reserved_lock,
            &file_control,
            &sector_size,
            &device_characteristics,
            &shm_map,
            &shm_lock,
            &shm_barrier,
            &shm_unmap,
            nullptr,
            nullptr,
        };
        static const sqlite3_io_methods version_three{
            3,
            &close,
            &read,
            &write,
            &truncate,
            &sync,
            &file_size,
            &lock,
            &unlock,
            &check_reserved_lock,
            &file_control,
            &sector_size,
            &device_characteristics,
            &shm_map,
            &shm_lock,
            &shm_barrier,
            &shm_unmap,
            &fetch,
            &unfetch,
        };
        if (version >= 3) return &version_three;
        if (version == 2) return &version_two;
        if (version == 1) return &version_one;
        return nullptr;
    }

    [[nodiscard]] static int supported_methods_version(
        const sqlite3_io_methods& methods) noexcept {
        if (methods.iVersion < 1 || methods.xClose == nullptr ||
            methods.xRead == nullptr || methods.xWrite == nullptr ||
            methods.xTruncate == nullptr || methods.xSync == nullptr ||
            methods.xFileSize == nullptr || methods.xLock == nullptr ||
            methods.xUnlock == nullptr ||
            methods.xCheckReservedLock == nullptr ||
            methods.xFileControl == nullptr || methods.xSectorSize == nullptr ||
            methods.xDeviceCharacteristics == nullptr) {
            return 0;
        }
        int version = 1;
        if (methods.iVersion >= 2 && methods.xShmMap != nullptr &&
            methods.xShmLock != nullptr && methods.xShmBarrier != nullptr &&
            methods.xShmUnmap != nullptr) {
            version = 2;
        }
        if (version == 2 && methods.iVersion >= 3 &&
            methods.xFetch != nullptr && methods.xUnfetch != nullptr) {
            version = 3;
        }
        return version;
    }

    static int open(sqlite3_vfs* wrapper,
                    sqlite3_filename name,
                    sqlite3_file* file,
                    int flags,
                    int* output_flags) noexcept {
        State& state = from(wrapper);
        state.require_current_context_noexcept();
        const std::lock_guard<std::mutex> lifecycle_lock(
            state.file_lifecycle_mutex);
        state.clear_local_error_noexcept();
        if (file == nullptr) {
            state.set_local_error_noexcept(
                "xOpen", "SQLite supplied no file storage");
            return SQLITE_MISUSE;
        }

        auto* const wrapped = ::new (file) WrappedFile{};
        wrapped->state = &state;
        sqlite3_file* const underlying = base_file(*wrapped);
        std::memset(
            underlying, 0,
            static_cast<std::size_t>(state.base->szOsFile));

        const auto reject_unopened_file = [&](int result) noexcept {
            wrapped->retained_path = nullptr;
            wrapped->base_methods = nullptr;
            wrapped->state = nullptr;
            wrapped->public_file.pMethods = nullptr;
            return result;
        };

        if (name == nullptr || *name == '\0') {
            state.set_local_error_noexcept(
                "xOpen",
                "anonymous SQLite disk files are outside descriptor-rooted "
                "authority");
            return reject_unopened_file(SQLITE_CANTOPEN);
        }
        if ((flags & SQLITE_OPEN_URI) != 0) {
            state.set_local_error_noexcept(
                "xOpen",
                "URI filenames are outside descriptor-rooted authority");
            return reject_unopened_file(SQLITE_CANTOPEN);
        }
        if ((flags & SQLITE_OPEN_DELETEONCLOSE) != 0) {
            // SQLite normally reserves DELETEONCLOSE for anonymous/temp,
            // transient, and subjournal files. None of those roles belongs to
            // this exact main/journal/WAL family. Reject the bit independently
            // so even a malformed direct VFS caller cannot turn an otherwise
            // reviewed family member into pathname deletion during xClose.
            state.set_local_error_noexcept(
                "xOpen",
                "delete-on-close files are outside descriptor-rooted authority");
            return reject_unopened_file(SQLITE_CANTOPEN);
        }

        const std::string* mapped = nullptr;
        FamilyMember member = FamilyMember::Main;
        if (!state.map_path_noexcept(name, mapped, member)) {
            state.set_local_error_noexcept(
                "xOpen", "filename is outside the reviewed SQLite family");
            return reject_unopened_file(SQLITE_CANTOPEN);
        }
        if (!open_role_matches_member(member, flags)) {
            state.set_local_error_noexcept(
                "xOpen",
                "SQLite file role does not match the reviewed family member");
            return reject_unopened_file(SQLITE_CANTOPEN);
        }
        wrapped->member = member;

        const bool is_main_database = member == FamilyMember::Main;
        if (is_main_database &&
            ((flags & SQLITE_OPEN_CREATE) != 0 ||
             (flags & SQLITE_OPEN_READWRITE) == 0 ||
             (flags & SQLITE_OPEN_NOFOLLOW) == 0)) {
            state.set_local_error_noexcept(
                "xOpen",
                "main database requires existing writable no-follow authority");
            return reject_unopened_file(SQLITE_CANTOPEN);
        }
        // O_NOFOLLOW rejects a final symlink but accepts hard links. Bind every
        // existing family member to a regular, single-linked name before the
        // delegated Unix VFS can open it. Sidecars may be absent because SQLite
        // creates them lazily; the exact main inode must already be present.
        if (!state.current_member_is_safe_noexcept(
                member, !is_main_database)) {
            state.set_local_error_noexcept(
                "xOpen",
                is_main_database
                    ? "logical main path no longer names the retained inode "
                      "before open"
                    : "SQLite sidecar is neither absent nor a single-linked "
                      "regular file before open");
            return reject_unopened_file(SQLITE_CANTOPEN);
        }

        // State owns immutable exact paths for the lifetime of every open
        // wrapper file. Reuse that storage rather than allocating one filename
        // per xOpen; the Unix VFS retains but does not own this pointer.
        wrapped->retained_path = mapped->c_str();

        // The wrapper, not SQLite's propagation choices, owns final-member
        // no-follow policy for the main, rollback journal, WAL, and SHM family.
        const int delegated_flags = flags | SQLITE_OPEN_NOFOLLOW;
        const int result = state.base->xOpen(
            state.base, wrapped->retained_path, underlying, delegated_flags,
            output_flags);
        if (result != SQLITE_OK || underlying->pMethods == nullptr) {
            if (underlying->pMethods != nullptr &&
                underlying->pMethods->xClose != nullptr) {
                (void)underlying->pMethods->xClose(underlying);
            }
            if (result == SQLITE_OK) {
                state.set_local_error_noexcept(
                    "xOpen", "delegated VFS returned no I/O methods");
            }
            return reject_unopened_file(
                result == SQLITE_OK ? SQLITE_IOERR : result);
        }

        const auto reject_opened_file = [&](std::string_view detail) noexcept {
            state.set_local_error_noexcept("xOpen", detail);
            if (underlying->pMethods != nullptr &&
                underlying->pMethods->xClose != nullptr) {
                (void)underlying->pMethods->xClose(underlying);
            }
            return reject_unopened_file(SQLITE_CANTOPEN);
        };

        if (!state.opened_member_matches_retained_name_noexcept(
                member, underlying)) {
            return reject_opened_file(
                is_main_database
                    ? "Unix VFS could not prove the opened main file still "
                      "occupies the approved path"
                    : "Unix VFS could not prove the opened sidecar still "
                      "occupies a single-linked regular family name");
        }

        wrapped->base_methods = underlying->pMethods;
        wrapped->public_file.pMethods = methods_for_version(
            supported_methods_version(*wrapped->base_methods));
        if (wrapped->public_file.pMethods == nullptr) {
            state.set_local_error_noexcept(
                "xOpen", "delegated VFS exposed incomplete I/O methods");
            (void)wrapped->base_methods->xClose(underlying);
            return reject_unopened_file(SQLITE_IOERR);
        }
        state.open_files.fetch_add(1U, std::memory_order_release);
        return SQLITE_OK;
    }

    static int remove(sqlite3_vfs* wrapper,
                      const char* name,
                      int sync_directory) noexcept {
        State& state = from(wrapper);
        state.require_current_context_noexcept();
        state.clear_local_error_noexcept();
        const std::string* mapped = nullptr;
        FamilyMember member = FamilyMember::Main;
        if (!state.map_path_noexcept(name, mapped, member)) {
            state.set_local_error_noexcept(
                "xDelete", "filename is outside the reviewed SQLite family");
            return SQLITE_IOERR_DELETE;
        }
        if (member == FamilyMember::Main) {
            // The private VFS may retire SQLite sidecars but never the exact
            // retained main database object.
            state.set_local_error_noexcept(
                "xDelete",
                "deleting the descriptor-rooted main database is forbidden");
            return SQLITE_IOERR_DELETE;
        }
        if (!state.current_member_is_safe_noexcept(member, true)) {
            state.set_local_error_noexcept(
                "xDelete",
                "refusing to delete an unsafe SQLite sidecar name");
            return SQLITE_IOERR_DELETE;
        }
        const int delete_result = state.base->xDelete(
            state.base, mapped->c_str(), sync_directory);
        if (delete_result == SQLITE_OK &&
            !state.current_member_is_safe_noexcept(member, true)) {
            state.set_local_error_noexcept(
                "xDelete",
                "SQLite sidecar became unsafe while deletion was delegated");
            return SQLITE_IOERR_DELETE;
        }
        return delete_result;
    }

    static int access(sqlite3_vfs* wrapper,
                      const char* name,
                      int flags,
                      int* result) noexcept {
        State& state = from(wrapper);
        state.require_current_context_noexcept();
        state.clear_local_error_noexcept();
        const std::string* mapped = nullptr;
        FamilyMember member = FamilyMember::Main;
        if (!state.map_path_noexcept(name, mapped, member)) {
            state.set_local_error_noexcept(
                "xAccess", "filename is outside the reviewed SQLite family");
            if (result != nullptr) *result = 0;
            return SQLITE_IOERR_ACCESS;
        }
        if (!state.current_member_is_safe_noexcept(
                member, member != FamilyMember::Main)) {
            state.set_local_error_noexcept(
                "xAccess",
                "SQLite family name is neither absent nor a single-linked "
                "regular file");
            if (result != nullptr) *result = 0;
            return SQLITE_IOERR_ACCESS;
        }
        const int access_result = state.base->xAccess(
            state.base, mapped->c_str(), flags, result);
        if (access_result == SQLITE_OK && result != nullptr && *result != 0 &&
            !state.current_member_is_safe_noexcept(member, false)) {
            *result = 0;
            state.set_local_error_noexcept(
                "xAccess",
                "SQLite family name became unsafe while access was delegated");
            return SQLITE_IOERR_ACCESS;
        }
        return access_result;
    }

    static int full_pathname(sqlite3_vfs* wrapper,
                             const char* name,
                             int output_size,
                             char* output) noexcept {
        State& state = from(wrapper);
        state.require_current_context_noexcept();
        state.clear_local_error_noexcept();
        if (name == nullptr || output == nullptr || output_size <= 0 ||
            std::string_view(name) != state.logical_main_path) {
            state.set_local_error_noexcept(
                "xFullPathname",
                "only the exact logical main path is authorized");
            return SQLITE_CANTOPEN;
        }
        if (state.logical_main_path.size() + 1U >
            static_cast<std::size_t>(output_size)) {
            state.set_local_error_noexcept(
                "xFullPathname",
                "logical main path exceeds the SQLite output buffer");
            return SQLITE_CANTOPEN;
        }
        std::memcpy(
            output, state.logical_main_path.c_str(),
            state.logical_main_path.size() + 1U);
        return SQLITE_OK;
    }

    static int close(sqlite3_file* file) noexcept {
        // Unix close may retire a shared-memory pathname, so preserve the
        // namespace proof at this release boundary.
        WrappedFile& wrapped = from_context(file);
        State& state = *wrapped.state;
        const std::lock_guard<std::mutex> lifecycle_lock(
            state.file_lifecycle_mutex);
        if (wrapped.member == FamilyMember::Main &&
            (!state.current_main_path_matches_retained_identity_noexcept() ||
             !state.current_member_is_safe_noexcept(
                 FamilyMember::SharedMemory, true))) {
            // xClose cannot safely return without releasing SQLite locks, yet
            // delegating may unlink a hostile replacement at the -shm name.
            // A reviewed-family violation here is therefore process-fatal:
            // kernel teardown closes descriptors without running the Unix VFS
            // pathname cleanup against an untrusted family entry.
            state.set_local_error_noexcept(
                "xClose",
                "main or shared-memory name is outside descriptor-rooted "
                "authority before close");
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        sqlite3_file* const underlying = base_file(wrapped);
        const sqlite3_io_methods* const methods = wrapped.base_methods;
        State* const owner = wrapped.state;
        const int result = methods->xClose(underlying);
        wrapped.retained_path = nullptr;
        wrapped.base_methods = nullptr;
        wrapped.state = nullptr;
        wrapped.public_file.pMethods = nullptr;
        const std::uint64_t previous =
            owner->open_files.fetch_sub(1U, std::memory_order_acq_rel);
        if (previous == 0U) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return result;
    }

    static int read(sqlite3_file* file,
                    void* output,
                    int bytes,
                    sqlite3_int64 offset) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xRead(
            base_file(wrapped), output, bytes, offset);
    }

    static int write(sqlite3_file* file,
                     const void* input,
                     int bytes,
                     sqlite3_int64 offset) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xWrite(
            base_file(wrapped), input, bytes, offset);
    }

    static int truncate(sqlite3_file* file, sqlite3_int64 size) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xTruncate(base_file(wrapped), size);
    }

    static int sync(sqlite3_file* file, int flags) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xSync(base_file(wrapped), flags);
    }

    static int file_size(sqlite3_file* file, sqlite3_int64* size) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xFileSize(base_file(wrapped), size);
    }

    static int lock(sqlite3_file* file, int level) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xLock(base_file(wrapped), level);
    }

    static int unlock(sqlite3_file* file, int level) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xUnlock(base_file(wrapped), level);
    }

    static int check_reserved_lock(sqlite3_file* file, int* result) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xCheckReservedLock(
            base_file(wrapped), result);
    }

    [[nodiscard]] static bool delegated_file_control_requires_argument(
        int operation) noexcept {
        // The retained Unix VFS dereferences pArg for each control below. The
        // public sqlite3_file_control API does not validate that pointer before
        // invoking xFileControl, and malformed direct sqlite3_io_methods callers
        // can reach this boundary too. Reject the malformed call here rather
        // than converting application misuse into a process crash inside the
        // delegated VFS. Keep this list scoped to controls actually handled by
        // the Unix VFS (plus the two controls owned by this wrapper); controls
        // whose documented contract permits a null argument continue to pass.
        switch (operation) {
#ifdef SQLITE_FCNTL_LOCKSTATE
            case SQLITE_FCNTL_LOCKSTATE:
#endif
#ifdef SQLITE_FCNTL_LAST_ERRNO
            case SQLITE_FCNTL_LAST_ERRNO:
#endif
#ifdef SQLITE_FCNTL_SIZE_HINT
            case SQLITE_FCNTL_SIZE_HINT:
#endif
#ifdef SQLITE_FCNTL_CHUNK_SIZE
            case SQLITE_FCNTL_CHUNK_SIZE:
#endif
#ifdef SQLITE_FCNTL_PERSIST_WAL
            case SQLITE_FCNTL_PERSIST_WAL:
#endif
#ifdef SQLITE_FCNTL_VFSNAME
            case SQLITE_FCNTL_VFSNAME:
#endif
#ifdef SQLITE_FCNTL_POWERSAFE_OVERWRITE
            case SQLITE_FCNTL_POWERSAFE_OVERWRITE:
#endif
#ifdef SQLITE_FCNTL_MMAP_SIZE
            case SQLITE_FCNTL_MMAP_SIZE:
#endif
#ifdef SQLITE_FCNTL_HAS_MOVED
            case SQLITE_FCNTL_HAS_MOVED:
#endif
#ifdef SQLITE_FCNTL_VFS_POINTER
            case SQLITE_FCNTL_VFS_POINTER:
#endif
#ifdef SQLITE_FCNTL_LOCK_TIMEOUT
            case SQLITE_FCNTL_LOCK_TIMEOUT:
#endif
#ifdef SQLITE_FCNTL_EXTERNAL_READER
            case SQLITE_FCNTL_EXTERNAL_READER:
#endif
#ifdef SQLITE_FCNTL_BLOCK_ON_CONNECT
            case SQLITE_FCNTL_BLOCK_ON_CONNECT:
#endif
#ifdef SQLITE_FCNTL_FILESTAT
            case SQLITE_FCNTL_FILESTAT:
#endif
                return true;
            default:
                return false;
        }
    }

    static int file_control(sqlite3_file* file,
                            int operation,
                            void* argument) noexcept {
        // SQLITE_FCNTL_HAS_MOVED and other delegated controls may resolve the
        // retained zPath; treat the generic file-control boundary as pathful.
        WrappedFile& wrapped = from_context(file);
        State& state = *wrapped.state;

        // These controls exceed the exact database-family capability. The Unix
        // implementation of TEMPFILENAME invents an ambient filesystem path,
        // NULL_IO closes the already-attested descriptor behind this wrapper,
        // and lock-proxy controls can redirect locking to another pathname on
        // platforms that support them. Unsupported is the normal xFileControl
        // result and avoids granting any part of those capabilities.
#ifdef SQLITE_FCNTL_TEMPFILENAME
        if (operation == SQLITE_FCNTL_TEMPFILENAME) {
            state.set_local_error_noexcept(
                "xFileControl",
                "temporary filename generation is outside descriptor-rooted "
                "authority");
            return SQLITE_NOTFOUND;
        }
#endif
#ifdef SQLITE_FCNTL_NULL_IO
        if (operation == SQLITE_FCNTL_NULL_IO) {
            state.set_local_error_noexcept(
                "xFileControl",
                "descriptor invalidation is outside descriptor-rooted authority");
            return SQLITE_NOTFOUND;
        }
#endif
#ifdef SQLITE_FCNTL_SET_LOCKPROXYFILE
        if (operation == SQLITE_FCNTL_SET_LOCKPROXYFILE) {
            state.set_local_error_noexcept(
                "xFileControl",
                "lock-proxy path selection is outside descriptor-rooted authority");
            return SQLITE_NOTFOUND;
        }
#endif
#ifdef SQLITE_FCNTL_GET_LOCKPROXYFILE
        if (operation == SQLITE_FCNTL_GET_LOCKPROXYFILE) {
            state.set_local_error_noexcept(
                "xFileControl",
                "lock-proxy paths are outside descriptor-rooted authority");
            return SQLITE_NOTFOUND;
        }
#endif

        if (argument == nullptr &&
            delegated_file_control_requires_argument(operation)) {
            state.set_local_error_noexcept(
                "xFileControl",
                "file-control operation requires a non-null argument");
            return SQLITE_MISUSE;
        }
#ifdef SQLITE_FCNTL_VFS_POINTER
        if (operation == SQLITE_FCNTL_VFS_POINTER) {
            *static_cast<sqlite3_vfs**>(argument) = &wrapped.state->vfs;
            return SQLITE_OK;
        }
#endif
#ifdef SQLITE_FCNTL_VFSNAME
        if (operation == SQLITE_FCNTL_VFSNAME) {
            auto** const output = static_cast<char**>(argument);
            *output = sqlite3_mprintf(
                "%s/%s", wrapped.state->vfs_name.c_str(),
                wrapped.state->base->zName);
            return *output == nullptr ? SQLITE_NOMEM : SQLITE_OK;
        }
#endif
        return wrapped.base_methods->xFileControl(
            base_file(wrapped), operation, argument);
    }

    static int sector_size(sqlite3_file* file) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xSectorSize(base_file(wrapped));
    }

    static int device_characteristics(sqlite3_file* file) noexcept {
        WrappedFile& wrapped = from(file);
        return wrapped.base_methods->xDeviceCharacteristics(
            base_file(wrapped));
    }

    static int shm_map(sqlite3_file* file,
                       int page,
                       int page_size,
                       int extend,
                       void volatile** output) noexcept {
        WrappedFile& wrapped = from_context(file);
        if (wrapped.base_methods->iVersion < 2 ||
            wrapped.base_methods->xShmMap == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        State& state = *wrapped.state;
        if (output != nullptr) *output = nullptr;
        if (wrapped.member != FamilyMember::Main ||
            !state.current_main_path_matches_retained_identity_noexcept() ||
            !state.current_member_is_safe_noexcept(
                FamilyMember::SharedMemory, true)) {
            state.set_local_error_noexcept(
                "xShmMap",
                "main or shared-memory name is outside descriptor-rooted "
                "authority before mapping");
            return SQLITE_IOERR_SHMOPEN;
        }

        sqlite3_file* const underlying = base_file(wrapped);
        const int result = wrapped.base_methods->xShmMap(
            underlying, page, page_size, extend, output);
        if (result != SQLITE_OK) return result;
        if (!state.current_main_path_matches_retained_identity_noexcept() ||
            !state.current_member_is_safe_noexcept(
                FamilyMember::SharedMemory, false)) {
            state.set_local_error_noexcept(
                "xShmMap",
                "Unix VFS could not prove the retained main and a "
                "single-linked regular shared-memory family name after "
                "mapping");
            if (wrapped.base_methods->xShmUnmap != nullptr) {
                (void)wrapped.base_methods->xShmUnmap(underlying, 0);
            }
            if (output != nullptr) *output = nullptr;
            return SQLITE_IOERR_SHMOPEN;
        }
        return SQLITE_OK;
    }

    static int shm_lock(sqlite3_file* file,
                        int offset,
                        int count,
                        int flags) noexcept {
        WrappedFile& wrapped = from(file);
        if (wrapped.base_methods->iVersion < 2 ||
            wrapped.base_methods->xShmLock == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return wrapped.base_methods->xShmLock(
            base_file(wrapped), offset, count, flags);
    }

    static void shm_barrier(sqlite3_file* file) noexcept {
        WrappedFile& wrapped = from(file);
        if (wrapped.base_methods->iVersion < 2 ||
            wrapped.base_methods->xShmBarrier == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        wrapped.base_methods->xShmBarrier(base_file(wrapped));
    }

    static int shm_unmap(sqlite3_file* file, int delete_flag) noexcept {
        WrappedFile& wrapped = from_context(file);
        if (wrapped.base_methods->iVersion < 2 ||
            wrapped.base_methods->xShmUnmap == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        State& state = *wrapped.state;
        if (wrapped.member != FamilyMember::Main ||
            !state.current_main_path_matches_retained_identity_noexcept() ||
            !state.current_member_is_safe_noexcept(
                FamilyMember::SharedMemory, true)) {
            wrapped.state->set_local_error_noexcept(
                "xShmUnmap",
                "main or shared-memory name is outside descriptor-rooted "
                "authority before unmapping");
            return SQLITE_IOERR_SHMOPEN;
        }
        const int result = wrapped.base_methods->xShmUnmap(
            base_file(wrapped), delete_flag);
        if (result == SQLITE_OK &&
            !state.current_member_is_safe_noexcept(
                FamilyMember::SharedMemory, true)) {
            state.set_local_error_noexcept(
                "xShmUnmap",
                "shared-memory family name became unsafe while unmapping was "
                "delegated");
            return SQLITE_IOERR_SHMOPEN;
        }
        return result;
    }

    static int fetch(sqlite3_file* file,
                     sqlite3_int64 offset,
                     int bytes,
                     void** output) noexcept {
        WrappedFile& wrapped = from(file);
        if (wrapped.base_methods->iVersion < 3 ||
            wrapped.base_methods->xFetch == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return wrapped.base_methods->xFetch(
            base_file(wrapped), offset, bytes, output);
    }

    static int unfetch(sqlite3_file* file,
                       sqlite3_int64 offset,
                       void* pointer) noexcept {
        WrappedFile& wrapped = from(file);
        if (wrapped.base_methods->iVersion < 3 ||
            wrapped.base_methods->xUnfetch == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return wrapped.base_methods->xUnfetch(
            base_file(wrapped), offset, pointer);
    }

    static void* dynamic_open(sqlite3_vfs* wrapper,
                              const char* filename) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        state.clear_local_error_noexcept();
        (void)filename;
        state.set_local_error_noexcept(
            "xDlOpen",
            "dynamic extension loading is outside descriptor-rooted authority");
        return nullptr;
    }

    static void dynamic_error(sqlite3_vfs* wrapper,
                              int bytes,
                              char* output) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        auto& slot = local_error_slot_noexcept();
        if (bytes <= 0 || output == nullptr) return;
        const char* detail =
            slot.owner == &state && slot.buffer[0] != '\0'
                ? slot.buffer.data()
                : "dynamic extension loading is outside descriptor-rooted authority";
        const std::size_t count = std::min<std::size_t>(
            static_cast<std::size_t>(bytes - 1), std::strlen(detail));
        std::memcpy(output, detail, count);
        output[count] = '\0';
    }

    static void (*dynamic_symbol(sqlite3_vfs* wrapper,
                                 void* handle,
                                 const char* symbol))(void) {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        (void)handle;
        (void)symbol;
        state.set_local_error_noexcept(
            "xDlSym",
            "dynamic extension loading is outside descriptor-rooted authority");
        return nullptr;
    }

    static void dynamic_close(sqlite3_vfs* wrapper,
                              void* handle) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        (void)handle;
        state.set_local_error_noexcept(
            "xDlClose",
            "dynamic extension loading is outside descriptor-rooted authority");
    }

    static int randomness(sqlite3_vfs* wrapper,
                          int bytes,
                          char* output) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        state.clear_local_error_noexcept();
        return state.base->xRandomness(state.base, bytes, output);
    }

    static int sleep(sqlite3_vfs* wrapper, int microseconds) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        state.clear_local_error_noexcept();
        return state.base->xSleep(state.base, microseconds);
    }

    static int current_time(sqlite3_vfs* wrapper, double* output) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        state.clear_local_error_noexcept();
        return state.base->xCurrentTime(state.base, output);
    }

    static int last_error(sqlite3_vfs* wrapper,
                          int bytes,
                          char* output) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        auto& slot = local_error_slot_noexcept();
        if (slot.owner == &state && bytes > 0 && output != nullptr &&
            slot.buffer[0] != '\0') {
            const std::size_t count = std::min<std::size_t>(
                static_cast<std::size_t>(bytes - 1),
                std::strlen(slot.buffer.data()));
            std::memcpy(output, slot.buffer.data(), count);
            output[count] = '\0';
            slot.buffer[0] = '\0';
            return 0;
        }
        return state.base->xGetLastError(state.base, bytes, output);
    }

    static int current_time_int64(
        sqlite3_vfs* wrapper,
        sqlite3_int64* output) noexcept {
        State& state = from(wrapper);
        state.require_current_process_noexcept();
        state.clear_local_error_noexcept();
        return state.base->xCurrentTimeInt64(state.base, output);
    }

};
SqliteDescriptorRootedVfs::SqliteDescriptorRootedVfs(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}

SqliteDescriptorRootedVfs::~SqliteDescriptorRootedVfs() {
    if (!state_) return;
    state_->require_current_context_noexcept();
    state_.reset();
}

const char* SqliteDescriptorRootedVfs::name() const noexcept {
    if (!state_) return "";
    state_->require_current_context_noexcept();
    return state_->vfs_name.c_str();
}

void SqliteDescriptorRootedVfs::verify_open_database_or_throw(
    sqlite3* database,
    const std::string& label) const {
    if (!state_) {
        throw std::logic_error(
            label + " descriptor-rooted SQLite VFS is unavailable");
    }
    const SyncSqliteDatabaseMutexGuard database_lock(database, label);
    (void)state_->main_file_for_database_or_throw(database, label);
}

std::string
SqliteDescriptorRootedVfs::read_bounded_main_file_before_open_or_throw(
    std::uint64_t maximum_bytes,
    const std::string& label) const {
    if (!state_) {
        throw std::logic_error(
            label + " descriptor-rooted SQLite VFS is unavailable");
    }
    return state_->read_bounded_main_file_before_open_or_throw(
        maximum_bytes, label);
}

std::string SqliteDescriptorRootedVfs::read_bounded_main_file_or_throw(
    sqlite3* database,
    std::uint64_t maximum_bytes,
    const std::string& label) const {
    if (!state_) {
        throw std::logic_error(
            label + " descriptor-rooted SQLite VFS is unavailable");
    }
    const SyncSqliteDatabaseMutexGuard database_lock(database, label);
    return state_->read_bounded_main_file_or_throw(
        database, maximum_bytes, label);
}

void SqliteDescriptorRootedVfs::verify_sidecars_absent_or_throw(
    const std::string& label) const {
    if (!state_) {
        throw std::logic_error(
            label + " descriptor-rooted SQLite VFS is unavailable");
    }
    state_->verify_retained_namespace_or_throw(label);
    for (const std::string& suffix : state_->sidecar_suffixes) {
        state_->verify_sidecar_absent_or_throw(suffix, label);
    }
}

void SqliteDescriptorRootedVfs::verify_sidecar_absent_or_throw(
    std::string_view suffix,
    const std::string& label) const {
    if (!state_) {
        throw std::logic_error(
            label + " descriptor-rooted SQLite VFS is unavailable");
    }
    state_->verify_sidecar_absent_or_throw(suffix, label);
}

void SqliteDescriptorRootedVfs::
sync_main_file_and_parent_directory_or_throw(
    sqlite3* database,
    const std::string& label) const {
    if (!state_) {
        throw std::logic_error(
            label + " descriptor-rooted SQLite VFS is unavailable");
    }
    const SyncSqliteDatabaseMutexGuard database_lock(database, label);
    state_->sync_main_file_and_parent_directory_or_throw(database, label);
}

std::unique_ptr<SqliteDescriptorRootedVfs>
register_sqlite_descriptor_rooted_vfs_or_throw(
    const SqlitePathFamilyGuard& guard,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "descriptor-rooted SQLite VFS label must not be empty");
    }
    guard.require_current_process_or_throw(label);
    if (!guard.parent_exists_ || guard.parent_fd_ < 0) {
        throw std::runtime_error(
            label + " SQLite parent directory was not established");
    }
    guard.verify_family_or_throw(label + " retained family");

#if !defined(__linux__)
    throw std::runtime_error(
        label + " descriptor-rooted SQLite VFS requires Linux procfs");
#else
    auto state = std::make_unique<SqliteDescriptorRootedVfs::State>();
    state->process_id = current_sync_process_incarnation_noexcept();
    state->mount_namespace_authority =
        SyncPosixMountNamespaceAuthority::capture_or_throw(
            label + " mount namespace");
    state->mount_namespace_authority.verify_or_throw(
        label + " mount namespace before descriptor capture");
    state->parent_device = guard.parent_device_;
    state->parent_inode = guard.parent_inode_;
    state->logical_main_path = guard.database_path_.generic_string();
    state->basename = guard.basename_;
    state->sidecar_suffixes = guard.sidecar_suffixes_;
    const auto has_exact_suffix = [&](std::string_view suffix) {
        return std::count(
                   state->sidecar_suffixes.begin(),
                   state->sidecar_suffixes.end(), suffix) == 1;
    };
    if (state->sidecar_suffixes.size() != 3U ||
        !has_exact_suffix("-journal") || !has_exact_suffix("-wal") ||
        !has_exact_suffix("-shm")) {
        throw std::runtime_error(
            label + " descriptor-rooted SQLite VFS requires exactly the "
                    "-journal, -wal, and -shm family");
    }

#ifdef F_DUPFD_CLOEXEC
    state->parent_fd = ::fcntl(guard.parent_fd_, F_DUPFD_CLOEXEC, 3);
#else
    state->parent_fd = ::dup(guard.parent_fd_);
    if (state->parent_fd >= 0) {
        (void)::fcntl(state->parent_fd, F_SETFD, FD_CLOEXEC);
    }
#endif
    if (state->parent_fd < 0) {
        throw_errno(
            label, "retained parent descriptor duplication",
            guard.parent_path_);
    }

    struct stat duplicated_status {};
    if (::fstat(state->parent_fd, &duplicated_status) != 0) {
        throw_errno(
            label, "duplicated parent descriptor fstat",
            guard.parent_path_);
    }
    if (!S_ISDIR(duplicated_status.st_mode) ||
        device_value(duplicated_status) != state->parent_device ||
        inode_value(duplicated_status) != state->parent_inode) {
        throw std::runtime_error(
            label + " duplicated descriptor changed SQLite parent identity");
    }
    state->directory_resolution_capability =
        sync_posix_probe_directory_resolution_capability_or_throw(
            state->parent_fd, label + " directory-resolution capability");
    if (!sync_posix_directory_resolution_uses_statx_mount_id(
            state->directory_resolution_capability)) {
        throw std::runtime_error(
            label + " descriptor-rooted SQLite VFS requires Linux statx "
                    "mount identity");
    }
    state->retained_parent_mount =
        sync_posix_capture_mount_identity_or_throw(
            state->parent_fd, state->directory_resolution_capability,
            label + " retained parent mount identity");
    if (!state->retained_parent_mount.available) {
        throw std::runtime_error(
            label + " retained SQLite parent mount identity is absent");
    }
    if (!guard.database_identity_bound_ ||
        !guard.database_existed_at_preflight_) {
        throw std::runtime_error(
            label + " descriptor-rooted SQLite VFS requires an existing main file");
    }

    // Bind the exact approved main identity without retaining a second
    // same-inode descriptor beside SQLite. POSIX close semantics make such an
    // auxiliary descriptor unsafe: closing it can discard locks held through
    // another connection in this process. Pre-open inspection is delegated to
    // the Unix VFS; live evidence uses SQLite's existing main file object.
    const FamilyMemberIdentity main = inspect_family_member_or_throw(
        state->parent_fd, state->basename, guard.database_path_, label);
    if (!main.exists || main.status.st_nlink != 1 ||
        device_value(main.status) != guard.database_device_ ||
        inode_value(main.status) != guard.database_inode_) {
        throw std::runtime_error(
            label + " retained main pathname changed approved identity");
    }
    state->main_device = device_value(main.status);
    state->main_inode = inode_value(main.status);
    const SyncPosixRelativeMountObservation main_mount =
        sync_posix_observe_relative_mount_noexcept(
            state->parent_fd, state->basename.c_str(),
            state->directory_resolution_capability,
            state->retained_parent_mount);
    if (main_mount.disposition !=
        SyncPosixRelativeMountDisposition::RetainedMount) {
        throw std::runtime_error(
            label + " SQLite main file crosses the retained parent mount");
    }

    state->descriptor_prefix =
        "/proc/self/fd/" + std::to_string(state->parent_fd) + "/";
    state->family_basenames = {
        state->basename,
        state->basename + "-journal",
        state->basename + "-wal",
        state->basename + "-shm",
    };
    state->logical_family_paths = {
        state->logical_main_path,
        state->logical_main_path + "-journal",
        state->logical_main_path + "-wal",
        state->logical_main_path + "-shm",
    };
    for (std::size_t index = 0U;
         index < state->descriptor_family_paths.size(); ++index) {
        state->descriptor_family_paths[index] =
            state->descriptor_prefix + state->family_basenames[index];
    }
    const std::string descriptor_directory =
        state->descriptor_prefix.substr(
            0U, state->descriptor_prefix.size() - 1U);
    struct stat procfs_status {};
    if (::stat(descriptor_directory.c_str(), &procfs_status) != 0) {
        throw_errno(
            label, "retained descriptor procfs resolution",
            descriptor_directory);
    }
    if (!S_ISDIR(procfs_status.st_mode) ||
        device_value(procfs_status) != state->parent_device ||
        inode_value(procfs_status) != state->parent_inode) {
        throw std::runtime_error(
            label +
            " /proc/self/fd does not resolve the retained SQLite parent "
            "directory");
    }
    state->mount_namespace_authority.verify_or_throw(
        label + " mount namespace after procfs descriptor proof");

    const int initialized = sqlite3_initialize();
    if (initialized != SQLITE_OK) {
        throw std::runtime_error(
            label + " SQLite initialization failed with code " +
            std::to_string(initialized));
    }
    state->base = sqlite3_vfs_find("unix");
    if (state->base == nullptr || state->base->xOpen == nullptr ||
        state->base->xDelete == nullptr || state->base->xAccess == nullptr ||
        state->base->xFullPathname == nullptr ||
        state->base->xRandomness == nullptr ||
        state->base->xSleep == nullptr ||
        state->base->xCurrentTime == nullptr ||
        state->base->xGetLastError == nullptr) {
        throw std::runtime_error(
            label + " bundled Unix SQLite VFS is unavailable or incomplete");
    }
    if (state->base->iVersion < 1 || state->base->iVersion > 3 ||
        state->base->szOsFile <= 0 || state->base->mxPathname <= 0) {
        throw std::runtime_error(
            label + " bundled Unix SQLite VFS geometry or version is invalid");
    }
    if (state->base->iVersion >= 2 &&
        state->base->xCurrentTimeInt64 == nullptr) {
        throw std::runtime_error(
            label + " bundled Unix SQLite VFS lacks its version-2 time callback");
    }

    std::size_t maximum_suffix_bytes = 0U;
    for (const std::string& suffix : state->sidecar_suffixes) {
        maximum_suffix_bytes = std::max(maximum_suffix_bytes, suffix.size());
    }
    const auto path_fits = [&](std::size_t prefix_bytes) {
        const std::size_t ceiling =
            static_cast<std::size_t>(state->base->mxPathname);
        return prefix_bytes <= ceiling &&
               maximum_suffix_bytes <= ceiling - prefix_bytes &&
               prefix_bytes + maximum_suffix_bytes + 1U <= ceiling;
    };
    if (!path_fits(state->logical_main_path.size()) ||
        !path_fits(state->descriptor_prefix.size() + state->basename.size())) {
        throw std::runtime_error(
            label + " SQLite family path exceeds the Unix VFS ceiling");
    }

    constexpr std::size_t kFileAlignment = alignof(std::max_align_t);
    static_assert((kFileAlignment & (kFileAlignment - 1U)) == 0U);
    state->base_file_offset =
        (sizeof(SqliteDescriptorRootedVfs::State::WrappedFile) +
         kFileAlignment - 1U) & ~(kFileAlignment - 1U);
    const std::size_t base_file_bytes =
        static_cast<std::size_t>(state->base->szOsFile);
    if (state->base_file_offset >
            static_cast<std::size_t>(std::numeric_limits<int>::max()) ||
        base_file_bytes >
            static_cast<std::size_t>(std::numeric_limits<int>::max()) -
                state->base_file_offset) {
        throw std::runtime_error(
            label + " SQLite wrapped file geometry exceeds int capacity");
    }

    static std::atomic<std::uint64_t> next_registration{1U};
    const std::uint64_t registration =
        next_registration.fetch_add(1U, std::memory_order_relaxed);
    state->vfs_name =
        "anonsync-dirfd-" + std::to_string(static_cast<long long>(::getpid())) +
        "-" + std::to_string(registration);
    if (sqlite3_vfs_find(state->vfs_name.c_str()) != nullptr) {
        throw std::runtime_error(
            label + " generated SQLite VFS name is already registered");
    }

    state->vfs = *state->base;
    state->vfs.pNext = nullptr;
    state->vfs.szOsFile = static_cast<int>(
        state->base_file_offset +
        static_cast<std::size_t>(state->base->szOsFile));
    state->vfs.zName = state->vfs_name.c_str();
    state->vfs.pAppData = state.get();
    state->vfs.xOpen = &SqliteDescriptorRootedVfs::State::open;
    state->vfs.xDelete = &SqliteDescriptorRootedVfs::State::remove;
    state->vfs.xAccess = &SqliteDescriptorRootedVfs::State::access;
    state->vfs.xFullPathname =
        &SqliteDescriptorRootedVfs::State::full_pathname;

    // Never leave a copied base callback reachable with this wrapper's
    // pAppData or zName. Dynamic loading is denied locally rather than
    // delegated, which keeps the private VFS safe even in builds where SQLite
    // was not compiled with SQLITE_OMIT_LOAD_EXTENSION.
    state->vfs.xDlOpen =
        &SqliteDescriptorRootedVfs::State::dynamic_open;
    state->vfs.xDlError =
        &SqliteDescriptorRootedVfs::State::dynamic_error;
    state->vfs.xDlSym =
        &SqliteDescriptorRootedVfs::State::dynamic_symbol;
    state->vfs.xDlClose =
        &SqliteDescriptorRootedVfs::State::dynamic_close;
    state->vfs.xRandomness =
        &SqliteDescriptorRootedVfs::State::randomness;
    state->vfs.xSleep = &SqliteDescriptorRootedVfs::State::sleep;
    state->vfs.xCurrentTime =
        &SqliteDescriptorRootedVfs::State::current_time;
    state->vfs.xGetLastError =
        &SqliteDescriptorRootedVfs::State::last_error;

    state->vfs.xCurrentTimeInt64 = nullptr;
    if (state->base->iVersion >= 2) {
        state->vfs.xCurrentTimeInt64 =
            &SqliteDescriptorRootedVfs::State::current_time_int64;
    }
    // SQLite core does not use these optional process-global syscall
    // replacement hooks. A deployment-rooted VFS must not inherit testing
    // authority capable of rewriting the Unix VFS syscall table.
    state->vfs.xSetSystemCall = nullptr;
    state->vfs.xGetSystemCall = nullptr;
    state->vfs.xNextSystemCall = nullptr;

    auto owner = std::unique_ptr<SqliteDescriptorRootedVfs>(
        new SqliteDescriptorRootedVfs(std::move(state)));
    const int registered = sqlite3_vfs_register(&owner->state_->vfs, 0);
    if (registered != SQLITE_OK) {
        throw std::runtime_error(
            label + " SQLite VFS registration failed with code " +
            std::to_string(registered));
    }
    owner->state_->registered = true;
    return owner;
#endif
}

SqlitePathFamilyGuard guard_sqlite_path_family_or_throw(
    const fs::path& database_path,
    bool create_parent_directories,
    const std::vector<std::string>& sidecar_suffixes,
    const std::string& label) {
    validate_suffixes_or_throw(sidecar_suffixes, label);
    SqlitePathFamilyGuard out;
    out.process_id_ = current_sync_process_incarnation_noexcept();
    out.database_path_ = absolute_normal_path_or_throw(database_path, label);
    out.parent_path_ = out.database_path_.parent_path();
    if (out.parent_path_.empty()) out.parent_path_ = "/";
    out.basename_ = out.database_path_.filename().string();
    out.sidecar_suffixes_ = sidecar_suffixes;

    DirectoryTraversalResult parent = traverse_directory_chain_or_throw(
        out.parent_path_, create_parent_directories, label);
    if (!parent.exists) return out;

    out.parent_fd_ = parent.fd.release();
    out.parent_device_ = device_value(parent.identity);
    out.parent_inode_ = inode_value(parent.identity);
    out.parent_exists_ = true;

    const FamilyMemberIdentity main = inspect_family_member_or_throw(
        out.parent_fd_, out.basename_, out.database_path_, label);
    out.database_existed_at_preflight_ = main.exists;
    if (main.exists) {
        out.database_identity_bound_ = true;
        out.database_device_ = device_value(main.status);
        out.database_inode_ = inode_value(main.status);
    }
    for (const std::string& suffix : out.sidecar_suffixes_) {
        (void)inspect_family_member_or_throw(out.parent_fd_, out.basename_ + suffix,
                                             fs::path(out.database_path_.string() + suffix), label);
    }
    return out;
}

void reject_unsafe_sqlite_path_family_or_throw(
    const fs::path& database_path,
    const std::vector<std::string>& sidecar_suffixes,
    const std::string& label) {
    SqlitePathFamilyGuard guard = guard_sqlite_path_family_or_throw(
        database_path, false, sidecar_suffixes, label);
    if (guard.parent_exists()) guard.verify_family_or_throw(label);
}

}  // namespace anonsync
