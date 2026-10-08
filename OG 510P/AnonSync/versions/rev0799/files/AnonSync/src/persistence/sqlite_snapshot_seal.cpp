#include "sqlite_snapshot_seal.hpp"

#include <sqlite3.h>

#include <openssl/evp.h>

#include <array>
#include <cerrno>
#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync::persistence {
namespace {

namespace fs = std::filesystem;

constexpr std::array<const char*, 3> kSnapshotSidecarSuffixes{
    "-wal", "-shm", "-journal"};

std::vector<std::string> snapshot_sidecar_suffixes() {
    std::vector<std::string> out;
    out.reserve(kSnapshotSidecarSuffixes.size());
    for (const char* suffix : kSnapshotSidecarSuffixes) out.emplace_back(suffix);
    return out;
}

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
                              int error_number = errno) {
    throw std::runtime_error(label + " " + operation + " failed: " +
                             std::strerror(error_number));
}

bool source_stat_is_stable(const struct stat& before,
                           const struct stat& after) noexcept {
    return before.st_dev == after.st_dev && before.st_ino == after.st_ino &&
           before.st_mode == after.st_mode && before.st_nlink == after.st_nlink &&
           before.st_size == after.st_size &&
           before.st_mtim.tv_sec == after.st_mtim.tv_sec &&
           before.st_mtim.tv_nsec == after.st_mtim.tv_nsec &&
           before.st_ctim.tv_sec == after.st_ctim.tv_sec &&
           before.st_ctim.tv_nsec == after.st_ctim.tv_nsec;
}

template <typename Integer>
std::uint64_t unsigned_stat_value(Integer value) noexcept {
    return static_cast<std::uint64_t>(value);
}

template <typename Integer>
std::int64_t signed_time_value(Integer value) noexcept {
    return static_cast<std::int64_t>(value);
}

std::string digest_hex(const unsigned char* bytes, std::size_t count) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (std::size_t i = 0; i < count; ++i) {
        out << std::setw(2) << static_cast<unsigned int>(bytes[i]);
    }
    return out.str();
}


using DigestContext = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;

std::string sha256_descriptor_exact_or_throw(int fd,
                                             std::uint64_t expected_bytes,
                                             const std::string& label) {
    if (fd < 0) {
        throw std::runtime_error(label + " SHA-256 descriptor is invalid");
    }
    DigestContext digest(EVP_MD_CTX_new(), &EVP_MD_CTX_free);
    if (!digest || EVP_DigestInit_ex(digest.get(), EVP_sha256(), nullptr) != 1) {
        throw std::runtime_error(label + " SHA-256 initialization failed");
    }

    std::array<unsigned char, 64U * 1024U> buffer{};
    std::uint64_t consumed = 0;
    while (consumed < expected_bytes) {
        const std::uint64_t remaining = expected_bytes - consumed;
        const std::size_t request =
            remaining < static_cast<std::uint64_t>(buffer.size())
                ? static_cast<std::size_t>(remaining)
                : buffer.size();
        if (consumed > static_cast<std::uint64_t>(
                           std::numeric_limits<off_t>::max())) {
            throw std::runtime_error(label + " SHA-256 offset exceeds off_t");
        }
        const ssize_t rc = ::pread(fd, buffer.data(), request,
                                   static_cast<off_t>(consumed));
        if (rc < 0 && errno == EINTR) continue;
        if (rc < 0) throw_errno(label, "SHA-256 descriptor read");
        if (rc == 0) {
            throw std::runtime_error(
                label + " SHA-256 descriptor ended before the expected byte count");
        }
        const auto count = static_cast<std::size_t>(rc);
        if (count > request ||
            EVP_DigestUpdate(digest.get(), buffer.data(), count) != 1) {
            throw std::runtime_error(label + " SHA-256 update failed");
        }
        consumed += static_cast<std::uint64_t>(count);
    }

    std::array<unsigned char, EVP_MAX_MD_SIZE> digest_bytes{};
    unsigned int digest_count = 0;
    if (EVP_DigestFinal_ex(digest.get(), digest_bytes.data(), &digest_count) != 1 ||
        digest_count != 32U) {
        throw std::runtime_error(label + " SHA-256 finalization failed");
    }
    return digest_hex(digest_bytes.data(), digest_count);
}

std::array<unsigned char, kSqliteDatabaseHeaderBytes>
read_sqlite_header_exact_or_throw(int fd, const std::string& label) {
    if (fd < 0) {
        throw std::runtime_error(label + " SQLite header descriptor is invalid");
    }
    std::array<unsigned char, kSqliteDatabaseHeaderBytes> header{};
    std::size_t consumed = 0;
    while (consumed < header.size()) {
        const ssize_t rc = ::pread(
            fd, header.data() + consumed, header.size() - consumed,
            static_cast<off_t>(consumed));
        if (rc < 0 && errno == EINTR) continue;
        if (rc < 0) throw_errno(label, "SQLite header descriptor read");
        if (rc == 0) {
            throw std::runtime_error(
                label + " SQLite snapshot ended before its 100-byte header");
        }
        const auto count = static_cast<std::size_t>(rc);
        if (count > header.size() - consumed) {
            throw std::runtime_error(label + " SQLite header read overflow");
        }
        consumed += count;
    }
    return header;
}

std::string uri_encode_path(const fs::path& path) {
    const std::string bytes = path.string();
    static constexpr char kHex[] = "0123456789ABCDEF";
    std::string encoded;
    encoded.reserve(bytes.size() + 32U);
    for (const char byte : bytes) {
        const auto value = static_cast<unsigned char>(byte);
        const bool unreserved =
            (value >= static_cast<unsigned char>('a') &&
             value <= static_cast<unsigned char>('z')) ||
            (value >= static_cast<unsigned char>('A') &&
             value <= static_cast<unsigned char>('Z')) ||
            (value >= static_cast<unsigned char>('0') &&
             value <= static_cast<unsigned char>('9')) ||
            value == static_cast<unsigned char>('-') ||
            value == static_cast<unsigned char>('_') ||
            value == static_cast<unsigned char>('.') ||
            value == static_cast<unsigned char>('~') ||
            value == static_cast<unsigned char>('/');
        if (unreserved) {
            encoded.push_back(static_cast<char>(value));
        } else {
            encoded.push_back('%');
            encoded.push_back(kHex[(value >> 4U) & 0x0fU]);
            encoded.push_back(kHex[value & 0x0fU]);
        }
    }
    return encoded;
}

fs::path make_private_staging_directory_or_throw(const std::string& label) {
    std::string candidate =
        "/tmp/anonsync-sqlite-snapshot-seal-" +
        std::to_string(static_cast<long long>(::getpid())) + "-XXXXXX";
    std::vector<char> writable(candidate.begin(), candidate.end());
    writable.push_back('\0');
    char* created = ::mkdtemp(writable.data());
    if (created == nullptr) throw_errno(label, "private staging directory creation");
    const fs::path directory(created);
    if (::chmod(directory.c_str(), 0700) != 0) {
        const int chmod_error = errno;
        (void)::rmdir(directory.c_str());
        throw_errno(label, "private staging directory chmod", chmod_error);
    }
    struct stat status{};
    if (::lstat(directory.c_str(), &status) != 0) {
        const int stat_error = errno;
        (void)::rmdir(directory.c_str());
        throw_errno(label, "private staging directory inspection", stat_error);
    }
    if (!S_ISDIR(status.st_mode) || status.st_uid != ::geteuid() ||
        (status.st_mode & 0777) != 0700) {
        (void)::rmdir(directory.c_str());
        throw std::runtime_error(
            label + " private staging directory did not retain mode 0700 ownership");
    }
    return directory;
}

int destination_open_flags() noexcept {
    int flags = O_RDWR | O_CREAT | O_EXCL;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    return flags;
}

void write_all_or_throw(int fd,
                        const unsigned char* bytes,
                        std::size_t count,
                        const std::string& label) {
    std::size_t offset = 0;
    while (offset < count) {
        const ssize_t rc = ::write(fd, bytes + offset, count - offset);
        if (rc < 0 && errno == EINTR) continue;
        if (rc <= 0) {
            const int write_error = rc < 0 ? errno : EIO;
            throw_errno(label, "private snapshot write", write_error);
        }
        offset += static_cast<std::size_t>(rc);
    }
}

std::uint64_t checked_source_size_or_throw(const struct stat& status,
                                           const SqliteSnapshotSealPolicy& policy,
                                           const std::string& label) {
    if (!S_ISREG(status.st_mode) || status.st_nlink != 1) {
        throw std::runtime_error(label + " source is not one single-linked regular file");
    }
    if (status.st_size <= 0) {
        throw std::runtime_error(label + " source snapshot is empty");
    }
    if (policy.maximum_bytes == 0U || policy.maximum_pages == 0U) {
        throw std::runtime_error(
            label + " SQLite snapshot geometry policy has a zero ceiling");
    }
    if (policy.maximum_bytes > kMaximumUntrustedSqliteSnapshotBytes ||
        policy.maximum_pages > kMaximumUntrustedSqliteSnapshotPages) {
        throw std::runtime_error(
            label +
            " SQLite snapshot geometry policy may tighten but not widen the reviewed ceiling");
    }
    const auto bytes = static_cast<std::uint64_t>(status.st_size);
    if (bytes < kSqliteDatabaseHeaderBytes) {
        throw std::runtime_error(
            label + " SQLite snapshot is shorter than its 100-byte header");
    }
    if (bytes > policy.maximum_bytes) {
        throw std::runtime_error(label + " SQLite snapshot exceeds the byte ceiling");
    }
    return bytes;
}

}  // namespace

SealedSqliteSnapshot SealedSqliteSnapshot::capture(
    const fs::path& source_path,
    const std::string& label,
    const SqliteSnapshotSealPolicy& policy) {
    if (label.empty()) {
        throw std::runtime_error("SQLite snapshot seal requires a nonempty diagnostic label");
    }

    SealedSqliteSnapshot out;
    out.pinned_vfs_ = sqlite3_vfs_find(nullptr);
    if (out.pinned_vfs_ == nullptr || out.pinned_vfs_->zName == nullptr ||
        out.pinned_vfs_->zName[0] == '\0') {
        throw std::runtime_error(label + " could not pin the default SQLite VFS");
    }
    out.pinned_vfs_name_ = out.pinned_vfs_->zName;

    SqlitePathFamilyGuard source_guard = guard_sqlite_path_family_or_throw(
        source_path, false, snapshot_sidecar_suffixes(), label);
    if (!source_guard.parent_exists()) {
        throw std::runtime_error(label + " source parent directory does not exist");
    }
    source_guard.verify_sidecars_absent_or_throw(label);
    ScopedFd source(source_guard.open_readonly_file_or_throw(label));
    source_guard.verify_sidecars_absent_or_throw(label);

    struct stat source_before{};
    if (::fstat(source.get(), &source_before) != 0) {
        throw_errno(label, "source descriptor inspection");
    }
    const std::uint64_t expected_bytes =
        checked_source_size_or_throw(source_before, policy, label);
    out.geometry_policy_ = policy;
    out.geometry_ = verify_sqlite_snapshot_geometry_or_throw(
        read_sqlite_header_exact_or_throw(source.get(), label + " source"),
        expected_bytes, label + " source", out.geometry_policy_);
    out.byte_count_ = out.geometry_.byte_count;

    // Geometry is established before creating a private staging directory, so
    // malformed or padded input cannot mint staging-allocation authority.
    out.source_path_ = source_guard.database_path();
    out.staging_directory_ = make_private_staging_directory_or_throw(label);
    out.staged_path_ = out.staging_directory_ / "snapshot.sqlite";

    try {
        ScopedFd destination(::open(out.staged_path_.c_str(),
                                    destination_open_flags(), 0600));
        if (destination.get() < 0) {
            throw_errno(label, "private snapshot creation");
        }

        DigestContext digest(EVP_MD_CTX_new(), &EVP_MD_CTX_free);
        if (!digest || EVP_DigestInit_ex(digest.get(), EVP_sha256(), nullptr) != 1) {
            throw std::runtime_error(label + " SHA-256 initialization failed");
        }

        std::array<unsigned char, 64U * 1024U> buffer{};
        std::uint64_t copied = 0;
        while (true) {
            const ssize_t rc = ::read(source.get(), buffer.data(), buffer.size());
            if (rc < 0 && errno == EINTR) continue;
            if (rc < 0) throw_errno(label, "source snapshot read");
            if (rc == 0) break;
            const auto count = static_cast<std::size_t>(rc);
            const auto count_u64 = static_cast<std::uint64_t>(count);
            if (count_u64 > policy.maximum_bytes ||
                copied > policy.maximum_bytes - count_u64) {
                throw std::runtime_error(
                    label +
                    " source snapshot exceeded the byte ceiling while copying");
            }
            if (EVP_DigestUpdate(digest.get(), buffer.data(), count) != 1) {
                throw std::runtime_error(label + " SHA-256 update failed");
            }
            write_all_or_throw(destination.get(), buffer.data(), count, label);
            copied += count_u64;
        }
        if (copied != expected_bytes) {
            throw std::runtime_error(label + " source snapshot size changed while copying");
        }

        struct stat source_after{};
        if (::fstat(source.get(), &source_after) != 0) {
            throw_errno(label, "source descriptor post-copy inspection");
        }
        if (!source_stat_is_stable(source_before, source_after)) {
            throw std::runtime_error(label + " source snapshot changed while being sealed");
        }
        source_guard.verify_open_file_descriptor_or_throw(source.get(), label);
        source_guard.verify_sidecars_absent_or_throw(label);

        if (::fsync(destination.get()) != 0) {
            throw_errno(label, "private snapshot fsync");
        }
        if (::fchmod(destination.get(), 0400) != 0) {
            throw_errno(label, "private snapshot chmod");
        }
        struct stat staged_status{};
        if (::fstat(destination.get(), &staged_status) != 0) {
            throw_errno(label, "private snapshot inspection");
        }
        if (!S_ISREG(staged_status.st_mode) || staged_status.st_nlink != 1 ||
            staged_status.st_uid != ::geteuid() ||
            (staged_status.st_mode & 0777) != 0400 ||
            staged_status.st_size != source_before.st_size) {
            throw std::runtime_error(label + " private snapshot identity or mode mismatch");
        }
        const SqliteSnapshotGeometry staged_geometry =
            verify_sqlite_snapshot_geometry_or_throw(
                read_sqlite_header_exact_or_throw(
                    destination.get(), label + " private snapshot"),
                static_cast<std::uint64_t>(staged_status.st_size),
                label + " private snapshot", out.geometry_policy_);
        if (staged_geometry != out.geometry_) {
            throw std::runtime_error(
                label + " private snapshot geometry changed while copying");
        }

        std::array<unsigned char, EVP_MAX_MD_SIZE> digest_bytes{};
        unsigned int digest_count = 0;
        if (EVP_DigestFinal_ex(digest.get(), digest_bytes.data(), &digest_count) != 1 ||
            digest_count != 32U) {
            throw std::runtime_error(label + " SHA-256 finalization failed");
        }

        destination.reset();
        out.sha256_hex_ = digest_hex(digest_bytes.data(), digest_count);
        if (copied != out.geometry_.byte_count) {
            throw std::runtime_error(
                label + " private snapshot byte count diverged from verified geometry");
        }
        out.immutable_uri_ =
            "file:" + uri_encode_path(out.staged_path_) +
            "?mode=ro&immutable=1&cache=private";
        out.staged_guard_ = guard_sqlite_path_family_or_throw(
            out.staged_path_, false, snapshot_sidecar_suffixes(), label);
        out.staged_guard_.verify_private_parent_directory_or_throw(label);
        out.staged_guard_.verify_sidecars_absent_or_throw(label);
        out.staged_fd_ = out.staged_guard_.open_readonly_file_or_throw(label);
        const std::string staged_sha256 = sha256_descriptor_exact_or_throw(
            out.staged_fd_, out.byte_count_, label + " private snapshot");
        if (staged_sha256 != out.sha256_hex_) {
            throw std::runtime_error(
                label + " private snapshot digest does not match captured source bytes");
        }

        struct stat retained_status{};
        if (::fstat(out.staged_fd_, &retained_status) != 0) {
            throw_errno(label, "retained private snapshot inspection");
        }
        if (retained_status.st_size < 0) {
            throw std::runtime_error(
                label + " retained private snapshot has a negative byte count");
        }
        const SqliteSnapshotGeometry retained_geometry =
            verify_sqlite_snapshot_geometry_or_throw(
                read_sqlite_header_exact_or_throw(
                    out.staged_fd_, label + " retained private snapshot"),
                static_cast<std::uint64_t>(retained_status.st_size),
                label + " retained private snapshot", out.geometry_policy_);
        if (retained_geometry != out.geometry_) {
            throw std::runtime_error(
                label + " retained private snapshot geometry mismatch");
        }
        out.staged_device_ = unsigned_stat_value(retained_status.st_dev);
        out.staged_inode_ = unsigned_stat_value(retained_status.st_ino);
        out.staged_mtime_seconds_ = signed_time_value(retained_status.st_mtim.tv_sec);
        out.staged_mtime_nanoseconds_ =
            static_cast<std::int64_t>(retained_status.st_mtim.tv_nsec);
        out.staged_ctime_seconds_ = signed_time_value(retained_status.st_ctim.tv_sec);
        out.staged_ctime_nanoseconds_ =
            static_cast<std::int64_t>(retained_status.st_ctim.tv_nsec);
        out.verify_unchanged_or_throw(label);
        return out;
    } catch (...) {
        out.cleanup_noexcept();
        throw;
    }
}

SealedSqliteSnapshot::~SealedSqliteSnapshot() {
    cleanup_noexcept();
}

SealedSqliteSnapshot::SealedSqliteSnapshot(SealedSqliteSnapshot&& other) noexcept
    : source_path_(std::move(other.source_path_)),
      staging_directory_(std::move(other.staging_directory_)),
      staged_path_(std::move(other.staged_path_)),
      immutable_uri_(std::move(other.immutable_uri_)),
      sha256_hex_(std::move(other.sha256_hex_)),
      pinned_vfs_name_(std::move(other.pinned_vfs_name_)),
      byte_count_(other.byte_count_),
      geometry_(other.geometry_),
      geometry_policy_(other.geometry_policy_),
      staged_guard_(std::move(other.staged_guard_)),
      staged_fd_(other.staged_fd_),
      pinned_vfs_(other.pinned_vfs_),
      staged_device_(other.staged_device_),
      staged_inode_(other.staged_inode_),
      staged_mtime_seconds_(other.staged_mtime_seconds_),
      staged_mtime_nanoseconds_(other.staged_mtime_nanoseconds_),
      staged_ctime_seconds_(other.staged_ctime_seconds_),
      staged_ctime_nanoseconds_(other.staged_ctime_nanoseconds_) {
    other.byte_count_ = 0;
    other.geometry_ = {};
    other.geometry_policy_ = {};
    other.staged_fd_ = -1;
    other.pinned_vfs_ = nullptr;
    other.staged_device_ = 0;
    other.staged_inode_ = 0;
    other.staged_mtime_seconds_ = 0;
    other.staged_mtime_nanoseconds_ = 0;
    other.staged_ctime_seconds_ = 0;
    other.staged_ctime_nanoseconds_ = 0;
    other.staging_directory_.clear();
    other.staged_path_.clear();
}

SealedSqliteSnapshot& SealedSqliteSnapshot::operator=(
    SealedSqliteSnapshot&& other) noexcept {
    if (this == &other) return *this;
    cleanup_noexcept();
    source_path_ = std::move(other.source_path_);
    staging_directory_ = std::move(other.staging_directory_);
    staged_path_ = std::move(other.staged_path_);
    immutable_uri_ = std::move(other.immutable_uri_);
    sha256_hex_ = std::move(other.sha256_hex_);
    pinned_vfs_name_ = std::move(other.pinned_vfs_name_);
    byte_count_ = other.byte_count_;
    geometry_ = other.geometry_;
    geometry_policy_ = other.geometry_policy_;
    staged_guard_ = std::move(other.staged_guard_);
    staged_fd_ = other.staged_fd_;
    pinned_vfs_ = other.pinned_vfs_;
    staged_device_ = other.staged_device_;
    staged_inode_ = other.staged_inode_;
    staged_mtime_seconds_ = other.staged_mtime_seconds_;
    staged_mtime_nanoseconds_ = other.staged_mtime_nanoseconds_;
    staged_ctime_seconds_ = other.staged_ctime_seconds_;
    staged_ctime_nanoseconds_ = other.staged_ctime_nanoseconds_;
    other.byte_count_ = 0;
    other.geometry_ = {};
    other.geometry_policy_ = {};
    other.staged_fd_ = -1;
    other.pinned_vfs_ = nullptr;
    other.staged_device_ = 0;
    other.staged_inode_ = 0;
    other.staged_mtime_seconds_ = 0;
    other.staged_mtime_nanoseconds_ = 0;
    other.staged_ctime_seconds_ = 0;
    other.staged_ctime_nanoseconds_ = 0;
    other.staging_directory_.clear();
    other.staged_path_.clear();
    return *this;
}

const fs::path& SealedSqliteSnapshot::source_path() const noexcept {
    return source_path_;
}

const fs::path& SealedSqliteSnapshot::staged_path() const noexcept {
    return staged_path_;
}

const std::string& SealedSqliteSnapshot::immutable_uri() const noexcept {
    return immutable_uri_;
}

const std::string& SealedSqliteSnapshot::sha256_hex() const noexcept {
    return sha256_hex_;
}

std::uint64_t SealedSqliteSnapshot::byte_count() const noexcept {
    return byte_count_;
}

std::uint32_t SealedSqliteSnapshot::page_size() const noexcept {
    return geometry_.page_size;
}

std::uint32_t SealedSqliteSnapshot::page_count() const noexcept {
    return geometry_.page_count;
}

const SqliteSnapshotGeometry& SealedSqliteSnapshot::geometry() const noexcept {
    return geometry_;
}

void SealedSqliteSnapshot::verify_pinned_vfs_registration_or_throw(
    const std::string& label) const {
    if (pinned_vfs_ == nullptr || pinned_vfs_name_.empty()) {
        throw std::runtime_error(label + " sealed SQLite VFS identity is absent");
    }
    sqlite3_vfs* const registered = sqlite3_vfs_find(pinned_vfs_name_.c_str());
    if (registered != pinned_vfs_) {
        throw std::runtime_error(
            label + " sealed SQLite VFS registration changed after capture");
    }
    if (registered->zName == nullptr || pinned_vfs_name_ != registered->zName) {
        throw std::runtime_error(
            label + " sealed SQLite VFS name changed after capture");
    }
}

void SealedSqliteSnapshot::verify_unchanged_or_throw(
    const std::string& label) {
    if (staged_fd_ < 0 || staged_path_.empty() || staging_directory_.empty()) {
        throw std::runtime_error(label + " sealed SQLite snapshot is not initialized");
    }
    verify_pinned_vfs_registration_or_throw(label);
    staged_guard_.verify_private_parent_directory_or_throw(label);
    staged_guard_.verify_sidecars_absent_or_throw(label);
    staged_guard_.verify_open_file_descriptor_or_throw(staged_fd_, label);
    struct stat status{};
    if (::fstat(staged_fd_, &status) != 0) {
        throw_errno(label, "sealed snapshot descriptor inspection");
    }
    if (!S_ISREG(status.st_mode) || status.st_nlink != 1 ||
        status.st_uid != ::geteuid() || (status.st_mode & 0777) != 0400 ||
        status.st_size < 0 ||
        static_cast<std::uint64_t>(status.st_size) != byte_count_ ||
        unsigned_stat_value(status.st_dev) != staged_device_ ||
        unsigned_stat_value(status.st_ino) != staged_inode_ ||
        signed_time_value(status.st_mtim.tv_sec) != staged_mtime_seconds_ ||
        static_cast<std::int64_t>(status.st_mtim.tv_nsec) !=
            staged_mtime_nanoseconds_ ||
        signed_time_value(status.st_ctim.tv_sec) != staged_ctime_seconds_ ||
        static_cast<std::int64_t>(status.st_ctim.tv_nsec) !=
            staged_ctime_nanoseconds_) {
        throw std::runtime_error(label + " sealed SQLite snapshot changed after capture");
    }
    const SqliteSnapshotGeometry current_geometry =
        verify_sqlite_snapshot_geometry_or_throw(
            read_sqlite_header_exact_or_throw(
                staged_fd_, label + " sealed snapshot"),
            static_cast<std::uint64_t>(status.st_size),
            label + " sealed snapshot", geometry_policy_);
    if (current_geometry != geometry_) {
        throw std::runtime_error(
            label + " sealed SQLite snapshot geometry changed after capture");
    }
}

sqlite3* SealedSqliteSnapshot::open_database_or_throw(
    const std::string& label) {
    verify_unchanged_or_throw(label);
    sqlite3* database = nullptr;
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_URI |
                SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int rc = sqlite3_open_v2(
        immutable_uri_.c_str(), &database, flags, pinned_vfs_name_.c_str());
    if (rc != SQLITE_OK) {
        const std::string message =
            database != nullptr ? sqlite3_errmsg(database) : "SQLite open failed";
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw std::runtime_error(label + " immutable SQLite open failed: " + message);
    }
    try {
        staged_guard_.verify_open_database_or_throw(database, label);
        if (sqlite3_db_readonly(database, "main") != 1) {
            throw std::runtime_error(label + " immutable SQLite handle is not read-only");
        }
        if (sqlite3_db_mutex(database) == nullptr) {
            throw std::runtime_error(
                label + " immutable SQLite handle lacks its requested full mutex");
        }
        sqlite3_vfs* observed_vfs = nullptr;
        const int vfs_rc = sqlite3_file_control(
            database, "main", SQLITE_FCNTL_VFS_POINTER, &observed_vfs);
        if (vfs_rc != SQLITE_OK || observed_vfs != pinned_vfs_) {
            throw std::runtime_error(
                label + " immutable SQLite open used an unpinned VFS object");
        }
        verify_unchanged_or_throw(label);
        return database;
    } catch (...) {
        (void)sqlite3_close_v2(database);
        throw;
    }
}

void SealedSqliteSnapshot::cleanup_noexcept() noexcept {
    if (staged_fd_ >= 0) {
        (void)::close(staged_fd_);
        staged_fd_ = -1;
    }
    if (!staged_path_.empty()) {
        (void)::unlink((staged_path_.string() + "-wal").c_str());
        (void)::unlink((staged_path_.string() + "-shm").c_str());
        (void)::unlink((staged_path_.string() + "-journal").c_str());
        (void)::unlink(staged_path_.c_str());
    }
    if (!staging_directory_.empty()) {
        (void)::rmdir(staging_directory_.c_str());
    }
    staging_directory_.clear();
    staged_path_.clear();
    immutable_uri_.clear();
    sha256_hex_.clear();
    pinned_vfs_name_.clear();
    byte_count_ = 0;
    geometry_ = {};
    geometry_policy_ = {};
    pinned_vfs_ = nullptr;
    staged_device_ = 0;
    staged_inode_ = 0;
    staged_mtime_seconds_ = 0;
    staged_mtime_nanoseconds_ = 0;
    staged_ctime_seconds_ = 0;
    staged_ctime_nanoseconds_ = 0;
}

}  // namespace anonsync::persistence
