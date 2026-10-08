#include "sqlite_path_security.hpp"

#include <sqlite3.h>

#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <string>
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
    if (parent_fd_ >= 0) (void)::close(parent_fd_);
}

SqlitePathFamilyGuard::SqlitePathFamilyGuard(SqlitePathFamilyGuard&& other) noexcept
    : database_path_(std::move(other.database_path_)),
      parent_path_(std::move(other.parent_path_)),
      basename_(std::move(other.basename_)),
      sidecar_suffixes_(std::move(other.sidecar_suffixes_)),
      parent_fd_(other.parent_fd_),
      parent_device_(other.parent_device_),
      parent_inode_(other.parent_inode_),
      parent_exists_(other.parent_exists_),
      database_existed_at_preflight_(other.database_existed_at_preflight_),
      database_identity_bound_(other.database_identity_bound_),
      database_device_(other.database_device_),
      database_inode_(other.database_inode_) {
    other.parent_fd_ = -1;
    other.parent_exists_ = false;
    other.database_existed_at_preflight_ = false;
    other.database_identity_bound_ = false;
}

SqlitePathFamilyGuard& SqlitePathFamilyGuard::operator=(SqlitePathFamilyGuard&& other) noexcept {
    if (this == &other) return *this;
    if (parent_fd_ >= 0) (void)::close(parent_fd_);
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
    other.parent_fd_ = -1;
    other.parent_exists_ = false;
    other.database_existed_at_preflight_ = false;
    other.database_identity_bound_ = false;
    return *this;
}

const fs::path& SqlitePathFamilyGuard::database_path() const noexcept {
    return database_path_;
}

bool SqlitePathFamilyGuard::parent_exists() const noexcept {
    return parent_exists_;
}

bool SqlitePathFamilyGuard::database_existed_at_preflight() const noexcept {
    return database_existed_at_preflight_;
}

void SqlitePathFamilyGuard::verify_family_or_throw(const std::string& label) const {
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

void SqlitePathFamilyGuard::verify_private_parent_directory_or_throw(
    const std::string& label) const {
    verify_family_or_throw(label);
    struct stat status{};
    if (::fstat(parent_fd_, &status) != 0) {
        throw_errno(label, "private SQLite parent directory fstat", parent_path_);
    }
    if (!S_ISDIR(status.st_mode) || status.st_uid != ::geteuid() ||
        (status.st_mode & 0777) != 0700) {
        throw std::runtime_error(
            label + " private SQLite parent directory is not owned mode 0700: " +
            parent_path_.generic_string());
    }
}

void SqlitePathFamilyGuard::verify_open_file_descriptor_or_throw(
    int fd,
    const std::string& label) {
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

SqlitePathFamilyGuard guard_sqlite_path_family_or_throw(
    const fs::path& database_path,
    bool create_parent_directories,
    const std::vector<std::string>& sidecar_suffixes,
    const std::string& label) {
    validate_suffixes_or_throw(sidecar_suffixes, label);
    SqlitePathFamilyGuard out;
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
