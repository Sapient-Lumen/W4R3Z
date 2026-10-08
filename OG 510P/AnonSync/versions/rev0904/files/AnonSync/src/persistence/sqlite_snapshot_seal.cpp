#include "sqlite_snapshot_seal.hpp"

#include "sqlite_exact_value.hpp"
#include "sqlite_live_backup.hpp"
#include "sqlite_path_security.hpp"

#include <sqlite3.h>

#include <openssl/evp.h>

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <iomanip>
#include <limits>
#include <memory>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

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
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
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

std::string digest_hex(const unsigned char* bytes, std::size_t count) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (std::size_t i = 0; i < count; ++i) {
        out << std::setw(2) << static_cast<unsigned int>(bytes[i]);
    }
    return out.str();
}

using DigestContext = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;

DigestContext new_sha256_context_or_throw(const std::string& label) {
    DigestContext digest(EVP_MD_CTX_new(), &EVP_MD_CTX_free);
    if (!digest || EVP_DigestInit_ex(digest.get(), EVP_sha256(), nullptr) != 1) {
        throw std::runtime_error(label + " SHA-256 initialization failed");
    }
    return digest;
}

std::string finish_sha256_or_throw(DigestContext& digest,
                                   const std::string& label) {
    std::array<unsigned char, EVP_MAX_MD_SIZE> digest_bytes{};
    unsigned int digest_count = 0;
    if (EVP_DigestFinal_ex(digest.get(), digest_bytes.data(), &digest_count) != 1 ||
        digest_count != 32U) {
        throw std::runtime_error(label + " SHA-256 finalization failed");
    }
    return digest_hex(digest_bytes.data(), digest_count);
}

std::string sha256_bytes_or_throw(std::span<const unsigned char> bytes,
                                  const std::string& label) {
    DigestContext digest = new_sha256_context_or_throw(label);
    if (!bytes.empty() &&
        EVP_DigestUpdate(digest.get(), bytes.data(), bytes.size()) != 1) {
        throw std::runtime_error(label + " SHA-256 update failed");
    }
    return finish_sha256_or_throw(digest, label);
}

std::array<unsigned char, kSqliteDatabaseHeaderBytes>
header_from_bytes_or_throw(std::span<const unsigned char> bytes,
                           const std::string& label) {
    if (bytes.size() < kSqliteDatabaseHeaderBytes) {
        throw std::runtime_error(
            label + " SQLite snapshot ended before its 100-byte header");
    }
    std::array<unsigned char, kSqliteDatabaseHeaderBytes> header{};
    std::copy_n(bytes.begin(), header.size(), header.begin());
    return header;
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

void verify_deserializable_file_format_or_throw(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    const std::string& label) {
    // sqlite3_deserialize() cannot use an image whose file-format read/write
    // versions advertise WAL mode. A cleanly closed WAL database commonly has
    // no -wal or -shm sibling while retaining 2/2 at offsets 18/19, so sidecar
    // absence alone is not sufficient evidence. Do not rewrite authenticated
    // bytes to 1/1: require the producer to supply a canonical rollback-mode
    // snapshot instead.
    if (header[18] != 1U || header[19] != 1U) {
        throw std::runtime_error(
            label +
            " SQLite snapshot must use rollback-journal file format versions 1/1 for read-only deserialization");
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
    if (bytes > static_cast<std::uint64_t>(
                    std::numeric_limits<std::size_t>::max())) {
        throw std::runtime_error(label + " SQLite snapshot exceeds process addressability");
    }
    if (bytes > static_cast<std::uint64_t>(
                    std::numeric_limits<sqlite3_int64>::max())) {
        throw std::runtime_error(label + " SQLite snapshot exceeds SQLite addressability");
    }
    return bytes;
}

using SqliteAllocatedBytes =
    std::unique_ptr<unsigned char, decltype(&sqlite3_free)>;

SqliteAllocatedBytes copy_source_exact_or_throw(
    int fd,
    std::uint64_t expected_bytes,
    std::string& stream_sha256,
    const std::string& label) {
    if (fd < 0) {
        throw std::runtime_error(label + " source descriptor is invalid");
    }
    SqliteAllocatedBytes bytes(
        static_cast<unsigned char*>(sqlite3_malloc64(expected_bytes)),
        &sqlite3_free);
    if (!bytes) {
        throw std::runtime_error(
            label + " could not allocate resident SQLite snapshot bytes");
    }
    DigestContext digest = new_sha256_context_or_throw(label);

    std::uint64_t copied = 0;
    while (copied < expected_bytes) {
        const std::uint64_t remaining = expected_bytes - copied;
        const std::size_t request =
            remaining < 64U * 1024U
                ? static_cast<std::size_t>(remaining)
                : 64U * 1024U;
        const ssize_t rc = ::pread(
            fd, bytes.get() + static_cast<std::size_t>(copied), request,
            static_cast<off_t>(copied));
        if (rc < 0 && errno == EINTR) continue;
        if (rc < 0) throw_errno(label, "source snapshot read");
        if (rc == 0) {
            throw std::runtime_error(
                label + " source snapshot ended before its captured byte count");
        }
        const auto count = static_cast<std::size_t>(rc);
        if (count > request ||
            EVP_DigestUpdate(
                digest.get(),
                bytes.get() + static_cast<std::size_t>(copied), count) != 1) {
            throw std::runtime_error(label + " SHA-256 update failed");
        }
        copied += static_cast<std::uint64_t>(count);
    }

    unsigned char extra = 0;
    while (true) {
        const ssize_t rc = ::pread(
            fd, &extra, 1U, static_cast<off_t>(expected_bytes));
        if (rc < 0 && errno == EINTR) continue;
        if (rc < 0) throw_errno(label, "source snapshot terminal read");
        if (rc != 0) {
            throw std::runtime_error(
                label + " source snapshot grew beyond its captured byte count");
        }
        break;
    }

    stream_sha256 = finish_sha256_or_throw(digest, label);
    return bytes;
}

std::string sqlite_error_text(sqlite3* database) {
    return database != nullptr ? sqlite3_errmsg(database)
                               : "SQLite database handle is null";
}

void sqlite_exec_or_throw(sqlite3* database,
                          const char* sql,
                          const std::string& label) {
    char* error = nullptr;
    const int rc = sqlite3_exec(database, sql, nullptr, nullptr, &error);
    if (rc == SQLITE_OK) return;
    std::string message = error != nullptr ? error : sqlite_error_text(database);
    sqlite3_free(error);
    throw std::runtime_error(label + ": " + message);
}

class ScopedStatement final {
public:
    ScopedStatement(sqlite3* database,
                    const char* sql,
                    const std::string& label)
        : database_(database), label_(label) {
        if (database_ == nullptr ||
            sqlite3_prepare_v2(database_, sql, -1, &statement_, nullptr) !=
                SQLITE_OK) {
            throw std::runtime_error(label_ + ": " + sqlite_error_text(database_));
        }
    }

    ~ScopedStatement() {
        if (statement_ != nullptr) (void)sqlite3_finalize(statement_);
    }

    ScopedStatement(const ScopedStatement&) = delete;
    ScopedStatement& operator=(const ScopedStatement&) = delete;

    sqlite3_stmt* get() const noexcept { return statement_; }

    void finalize_or_throw() {
        if (statement_ == nullptr) return;
        sqlite3_stmt* const statement = std::exchange(statement_, nullptr);
        const int rc = sqlite3_finalize(statement);
        if (rc != SQLITE_OK) {
            throw std::runtime_error(label_ + " finalize failed: " +
                                     sqlite_error_text(database_));
        }
    }

private:
    sqlite3* database_ = nullptr;
    sqlite3_stmt* statement_ = nullptr;
    std::string label_;
};

std::uint64_t sqlite_query_exact_u64_or_throw(sqlite3* database,
                                              const char* sql,
                                              const std::string& label) {
    ScopedStatement statement(database, sql, label + " prepare failed");
    if (sqlite3_step(statement.get()) != SQLITE_ROW) {
        throw std::runtime_error(label + " query failed: " +
                                 sqlite_error_text(database));
    }
    const std::uint64_t value = sqlite_exact_u64_or_throw(
        statement.get(), 0, label + " exact integer projection");
    if (sqlite3_step(statement.get()) != SQLITE_DONE) {
        throw std::runtime_error(label + " returned more than one row");
    }
    statement.finalize_or_throw();
    return value;
}

void close_database_or_throw(sqlite3*& database, const std::string& label) {
    if (database == nullptr) return;
    const int rc = sqlite3_close_v2(database);
    if (rc != SQLITE_OK) {
        throw std::runtime_error(label + ": " + sqlite3_errstr(rc));
    }
    database = nullptr;
}

void close_database_best_effort(sqlite3*& database) noexcept {
    if (database == nullptr) return;
    sqlite3* const owned = std::exchange(database, nullptr);
    (void)sqlite3_close_v2(owned);
}

std::uint64_t checked_serialized_geometry_bytes_or_throw(
    sqlite3* database,
    const SqliteSnapshotSealPolicy& policy,
    const std::string& label) {
    const std::uint64_t page_size = sqlite_query_exact_u64_or_throw(
        database, "PRAGMA main.page_size;", label + " page-size");
    const std::uint64_t page_count = sqlite_query_exact_u64_or_throw(
        database, "PRAGMA main.page_count;", label + " page-count");
    const SqliteSnapshotGeometry geometry =
        verify_sqlite_snapshot_page_geometry_or_throw(
            page_size, page_count, label, policy);
    if (geometry.byte_count > static_cast<std::uint64_t>(
                                  std::numeric_limits<sqlite3_int64>::max())) {
        throw std::runtime_error(label + " exceeds SQLite addressability");
    }
    return geometry.byte_count;
}

}  // namespace

SealedSqliteSnapshot SealedSqliteSnapshot::capture(
    const fs::path& source_path,
    const std::string& label,
    const SqliteSnapshotSealPolicy& policy) {
    if (label.empty()) {
        throw std::runtime_error("SQLite snapshot seal requires a nonempty diagnostic label");
    }

    validate_sqlite_snapshot_geometry_policy_or_throw(policy, label);
    SealedSqliteSnapshot out;
    out.geometry_policy_ = policy;
    out.initialize_process_and_vfs_or_throw(label);

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
    const auto source_header =
        read_sqlite_header_exact_or_throw(source.get(), label + " source");
    verify_deserializable_file_format_or_throw(source_header, label + " source");
    out.geometry_ = verify_sqlite_snapshot_geometry_or_throw(
        source_header, expected_bytes, label + " source", out.geometry_policy_);
    out.byte_count_ = out.geometry_.byte_count;

    // Geometry is established before allocating resident snapshot authority, so
    // malformed or padded input cannot mint a large process-memory capability.
    std::string stream_sha256;
    SqliteAllocatedBytes captured = copy_source_exact_or_throw(
        source.get(), expected_bytes, stream_sha256, label);

    struct stat source_after{};
    if (::fstat(source.get(), &source_after) != 0) {
        throw_errno(label, "source descriptor post-copy inspection");
    }
    if (!source_stat_is_stable(source_before, source_after)) {
        throw std::runtime_error(label + " source snapshot changed while being sealed");
    }
    source_guard.verify_open_file_descriptor_or_throw(source.get(), label);
    source_guard.verify_sidecars_absent_or_throw(label);

    out.source_path_ = source_guard.database_path();
    out.byte_count_ = expected_bytes;
    out.serialized_bytes_.reset(captured.release());
    out.finalize_resident_bytes_or_throw(label + " captured bytes");
    if (out.geometry_ != verify_sqlite_snapshot_geometry_or_throw(
                             source_header, expected_bytes,
                             label + " source", out.geometry_policy_)) {
        throw std::runtime_error(
            label + " resident snapshot geometry changed while copying");
    }
    if (out.sha256_hex_ != stream_sha256) {
        throw std::runtime_error(
            label + " resident snapshot digest does not match captured source bytes");
    }
    return out;
}

SealedSqliteSnapshot SealedSqliteSnapshot::capture_database(
    sqlite3* source_database,
    const std::string& label,
    const SqliteSnapshotSealPolicy& policy) {
    if (label.empty()) {
        throw std::runtime_error(
            "SQLite live snapshot seal requires a nonempty diagnostic label");
    }
    validate_sqlite_snapshot_geometry_policy_or_throw(policy, label);
    if (source_database == nullptr) {
        throw std::runtime_error(label + " source database handle is null");
    }
    if (sqlite3_db_mutex(source_database) == nullptr) {
        throw std::runtime_error(
            label + " source database lacks full-mutex protection");
    }
    if (sqlite3_get_autocommit(source_database) == 0) {
        throw std::runtime_error(
            label + " refuses a source database with an active transaction");
    }

    // Refuse oversized source geometry before SQLite allocates a private copy
    // or VACUUM workspace. The bounded backup owner establishes a read snapshot
    // and repeats this proof inside that snapshot, so a commit between this
    // early rejection gate and the pin cannot enlarge the copied image.
    (void)checked_serialized_geometry_bytes_or_throw(
        source_database, policy, label + " source preflight geometry");

    SealedSqliteSnapshot out;
    out.geometry_policy_ = policy;
    out.initialize_process_and_vfs_or_throw(label);

    sqlite3* resident_database = nullptr;
    try {
        const int open_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                               SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE |
                               SQLITE_OPEN_MEMORY;
        const int open_rc = sqlite3_open_v2(
            ":memory:", &resident_database, open_flags,
            out.pinned_vfs_name_.c_str());
        if (open_rc != SQLITE_OK) {
            throw std::runtime_error(
                label + " private in-memory destination open failed: " +
                sqlite_error_text(resident_database));
        }
        if (sqlite3_db_mutex(resident_database) == nullptr) {
            throw std::runtime_error(
                label + " private in-memory destination lacks its requested full mutex");
        }

#ifdef SQLITE_DBCONFIG_TRUSTED_SCHEMA
        int trusted_schema_out = 0;
        if (sqlite3_db_config(resident_database, SQLITE_DBCONFIG_TRUSTED_SCHEMA,
                              0, &trusted_schema_out) != SQLITE_OK) {
            throw std::runtime_error(
                label + " could not disable trusted_schema on private destination");
        }
#endif
        sqlite_exec_or_throw(
            resident_database, "PRAGMA trusted_schema=OFF;",
            label + " private destination trusted_schema pragma failed");
        if (sqlite_query_exact_u64_or_throw(
                resident_database, "PRAGMA trusted_schema;",
                label + " private destination trusted_schema readback") != 0U) {
            throw std::runtime_error(
                label + " private destination did not retain trusted_schema=OFF");
        }
        sqlite_exec_or_throw(
            resident_database, "PRAGMA temp_store=MEMORY;",
            label + " private destination temp_store pragma failed");
        if (sqlite_query_exact_u64_or_throw(
                resident_database, "PRAGMA temp_store;",
                label + " private destination temp_store readback") != 2U) {
            throw std::runtime_error(
                label + " private destination did not retain temp_store=MEMORY");
        }

        const SqliteLiveBackupEvidence live_backup =
            copy_sqlite_live_snapshot_bounded_or_throw(
                resident_database, source_database,
                label + " bounded private live backup", policy);
        if (live_backup.source_geometry.byte_count == 0U ||
            live_backup.step_calls == 0U ||
            live_backup.maximum_reported_page_count !=
                live_backup.source_geometry.page_count) {
            throw std::runtime_error(
                label + " bounded private live backup returned incomplete evidence");
        }

        // sqlite3_backup preserves page-1 WAL read/write versions 2/2. A
        // private in-memory VACUUM, with its temporary store forced to memory,
        // rebuilds the complete logical image. The resident header is still
        // independently required to prove canonical 1/1 before promotion.
        sqlite_exec_or_throw(
            resident_database, "VACUUM;",
            label + " private rollback-format canonicalization failed");

        const std::uint64_t expected_bytes =
            checked_serialized_geometry_bytes_or_throw(
                resident_database, policy,
                label + " private serialized geometry");
        sqlite3_int64 reported_size = 0;
        (void)sqlite3_serialize(
            resident_database, "main", &reported_size,
            SQLITE_SERIALIZE_NOCOPY);
        if (reported_size <= 0 ||
            static_cast<std::uint64_t>(reported_size) != expected_bytes) {
            throw std::runtime_error(
                label + " private serialization size does not match page geometry");
        }

        sqlite3_int64 serialized_size = 0;
        unsigned char* serialized = sqlite3_serialize(
            resident_database, "main", &serialized_size, 0);
        if (serialized == nullptr) {
            throw std::runtime_error(
                label + " could not allocate the private serialized image");
        }
        out.serialized_bytes_.reset(serialized);
        if (serialized_size <= 0 ||
            static_cast<std::uint64_t>(serialized_size) != expected_bytes) {
            throw std::runtime_error(
                label + " allocated serialization size changed after preflight");
        }
        out.byte_count_ = expected_bytes;
        out.finalize_resident_bytes_or_throw(label + " private serialized image");
        close_database_or_throw(
            resident_database, label + " private in-memory destination close failed");
        out.verify_unchanged_or_throw(label + " post-close resident image");
        return out;
    } catch (...) {
        close_database_best_effort(resident_database);
        throw;
    }
}

SealedSqliteSnapshot::~SealedSqliteSnapshot() {
    cleanup_noexcept();
}

void SealedSqliteSnapshot::SqliteBufferDeleter::operator()(
    unsigned char* bytes) const noexcept {
    sqlite3_free(bytes);
}

SealedSqliteSnapshot::SealedSqliteSnapshot(
    SealedSqliteSnapshot&& other) noexcept {
    other.require_current_process_noexcept();
    transfer_from_noexcept(other);
}

SealedSqliteSnapshot& SealedSqliteSnapshot::operator=(
    SealedSqliteSnapshot&& other) noexcept {
    require_current_process_noexcept();
    other.require_current_process_noexcept();
    if (this == &other) return *this;
    cleanup_noexcept();
    transfer_from_noexcept(other);
    return *this;
}

void SealedSqliteSnapshot::transfer_from_noexcept(
    SealedSqliteSnapshot& other) noexcept {
    process_id_ = other.process_id_;
    source_path_ = std::move(other.source_path_);
    sha256_hex_ = std::move(other.sha256_hex_);
    pinned_vfs_name_ = std::move(other.pinned_vfs_name_);
    byte_count_ = other.byte_count_;
    geometry_ = other.geometry_;
    geometry_policy_ = other.geometry_policy_;
    serialized_bytes_ = std::move(other.serialized_bytes_);
    pinned_vfs_ = other.pinned_vfs_;
    other.clear_moved_from_noexcept();
}

void SealedSqliteSnapshot::clear_moved_from_noexcept() noexcept {
    process_id_ = {};
    source_path_.clear();
    sha256_hex_.clear();
    pinned_vfs_name_.clear();
    byte_count_ = 0;
    geometry_ = {};
    geometry_policy_ = {};
    serialized_bytes_.reset();
    pinned_vfs_ = nullptr;
}

void SealedSqliteSnapshot::require_current_process_noexcept() const noexcept {
    if (process_id_.valid() && !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
}

void SealedSqliteSnapshot::require_current_process_or_throw(
    std::string_view label) const {
    if (!process_id_.valid()) {
        throw std::logic_error(std::string(label) +
                               " sealed SQLite snapshot is not initialized");
    }
    require_sync_process_incarnation_or_fail_stop(process_id_, label);
}

void SealedSqliteSnapshot::initialize_process_and_vfs_or_throw(
    const std::string& label) {
    process_id_ = current_sync_process_incarnation_noexcept();
    pinned_vfs_ = sqlite3_vfs_find(nullptr);
    if (pinned_vfs_ == nullptr || pinned_vfs_->zName == nullptr ||
        pinned_vfs_->zName[0] == '\0') {
        throw std::runtime_error(label + " could not pin the default SQLite VFS");
    }
    pinned_vfs_name_ = pinned_vfs_->zName;
}

void SealedSqliteSnapshot::finalize_resident_bytes_or_throw(
    const std::string& label) {
    require_current_process_or_throw(label);
    if (!serialized_bytes_ || byte_count_ == 0U ||
        byte_count_ > static_cast<std::uint64_t>(
                          std::numeric_limits<std::size_t>::max())) {
        throw std::runtime_error(label + " resident SQLite snapshot is not initialized");
    }
    const std::span<const unsigned char> bytes(
        serialized_bytes_.get(), static_cast<std::size_t>(byte_count_));
    const auto header = header_from_bytes_or_throw(bytes, label);
    verify_deserializable_file_format_or_throw(header, label);
    geometry_ = verify_sqlite_snapshot_geometry_or_throw(
        header, byte_count_, label, geometry_policy_);
    sha256_hex_ = sha256_bytes_or_throw(bytes, label);
    verify_unchanged_or_throw(label);
}

const fs::path& SealedSqliteSnapshot::source_path() const noexcept {
    require_current_process_noexcept();
    return source_path_;
}

const std::string& SealedSqliteSnapshot::sha256_hex() const noexcept {
    require_current_process_noexcept();
    return sha256_hex_;
}

std::uint64_t SealedSqliteSnapshot::byte_count() const noexcept {
    require_current_process_noexcept();
    return byte_count_;
}

std::uint32_t SealedSqliteSnapshot::page_size() const noexcept {
    require_current_process_noexcept();
    return geometry_.page_size;
}

std::uint32_t SealedSqliteSnapshot::page_count() const noexcept {
    require_current_process_noexcept();
    return geometry_.page_count;
}

const SqliteSnapshotGeometry& SealedSqliteSnapshot::geometry() const noexcept {
    require_current_process_noexcept();
    return geometry_;
}

void SealedSqliteSnapshot::verify_pinned_vfs_registration_or_throw(
    const std::string& label) const {
    require_current_process_or_throw(label);
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
    require_current_process_or_throw(label);
    if (!serialized_bytes_ || byte_count_ == 0U ||
        byte_count_ > static_cast<std::uint64_t>(
                          std::numeric_limits<std::size_t>::max())) {
        throw std::runtime_error(label + " sealed SQLite snapshot is not initialized");
    }
    verify_pinned_vfs_registration_or_throw(label);

    const std::span<const unsigned char> bytes(
        serialized_bytes_.get(), static_cast<std::size_t>(byte_count_));

    const auto resident_header = header_from_bytes_or_throw(
        bytes, label + " resident snapshot");
    verify_deserializable_file_format_or_throw(
        resident_header, label + " resident snapshot");
    const SqliteSnapshotGeometry current_geometry =
        verify_sqlite_snapshot_geometry_or_throw(
            resident_header, byte_count_,
            label + " resident snapshot", geometry_policy_);
    if (current_geometry != geometry_) {
        throw std::runtime_error(
            label + " sealed SQLite snapshot geometry changed after capture");
    }
    if (sha256_bytes_or_throw(bytes, label + " resident snapshot") !=
        sha256_hex_) {
        throw std::runtime_error(
            label + " sealed SQLite snapshot bytes changed after capture");
    }
}

sqlite3* SealedSqliteSnapshot::open_database_or_throw(
    const std::string& label) {
    sqlite3* database = nullptr;
    open_database_into_or_throw(&database, label);
    return database;
}

SyncSqliteDbHandleSlot SealedSqliteSnapshot::open_database_owner_or_throw(
    const std::string& label) {
    SyncSqliteDbHandleSlot owner;
    {
        auto output = owner.out();
        open_database_into_or_throw(output.get(), label);
    }
    return owner;
}

void SealedSqliteSnapshot::open_database_into_or_throw(
    sqlite3** output,
    const std::string& label) {
    if (output == nullptr || *output != nullptr) {
        throw std::logic_error(
            label + " SQLite snapshot output requires an empty handle slot");
    }
    require_current_process_or_throw(label);
    verify_unchanged_or_throw(label);

    auto* copy = static_cast<unsigned char*>(sqlite3_malloc64(byte_count_));
    if (copy == nullptr) {
        throw std::runtime_error(
            label + " could not allocate an independent SQLite snapshot image");
    }
    std::memcpy(copy, serialized_bytes_.get(),
                static_cast<std::size_t>(byte_count_));

    sqlite3* database = nullptr;
    const int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX |
                      SQLITE_OPEN_PRIVATECACHE | SQLITE_OPEN_MEMORY;
    const int open_rc = sqlite3_open_v2(
        ":memory:", &database, flags, pinned_vfs_name_.c_str());
    if (open_rc != SQLITE_OK) {
        const std::string message =
            database != nullptr ? sqlite3_errmsg(database) : "SQLite open failed";
        sqlite3_free(copy);
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw std::runtime_error(label + " private in-memory SQLite open failed: " +
                                 message);
    }

    const int deserialize_rc = sqlite3_deserialize(
        database, "main", copy,
        static_cast<sqlite3_int64>(byte_count_),
        static_cast<sqlite3_int64>(byte_count_),
        SQLITE_DESERIALIZE_FREEONCLOSE | SQLITE_DESERIALIZE_READONLY);
    // FREEONCLOSE transfers or releases copy even when deserialization fails.
    copy = nullptr;
    if (deserialize_rc != SQLITE_OK) {
        const std::string message = sqlite3_errmsg(database);
        (void)sqlite3_close_v2(database);
        throw std::runtime_error(label + " read-only SQLite deserialize failed: " +
                                 message);
    }

    try {
        verify_pinned_vfs_registration_or_throw(label);
        if (sqlite3_db_mutex(database) == nullptr) {
            throw std::runtime_error(
                label + " deserialized SQLite handle lacks its requested full mutex");
        }
        const char* const filename = sqlite3_db_filename(database, "main");
        if (filename == nullptr || filename[0] != '\0') {
            throw std::runtime_error(
                label + " deserialized SQLite handle unexpectedly names a file");
        }
        verify_unchanged_or_throw(label);
        *output = database;
    } catch (...) {
        (void)sqlite3_close_v2(database);
        throw;
    }
}

void SealedSqliteSnapshot::publish_exact_copy_atomically_or_throw(
    const fs::path& destination_path,
    const std::string& label) {
    publish_exact_copy_atomically_with_observer_or_throw(
        destination_path, label, nullptr, nullptr);
}

void SealedSqliteSnapshot::publish_exact_copy_atomically_create_new_or_throw(
    const fs::path& destination_path,
    const std::string& label) {
    publish_exact_copy_atomically_create_new_with_observer_or_throw(
        destination_path, label, nullptr, nullptr);
}

void SealedSqliteSnapshot::publish_exact_copy_atomically_with_observer_or_throw(
    const fs::path& destination_path,
    const std::string& label,
    atomic_file_publication_detail::AtomicFilePublicationObserver observer,
    void* observer_context) {
    require_current_process_or_throw(label);
    verify_unchanged_or_throw(label + " prepublication");
    atomic_file_publication_detail::
        write_sync_file_atomically_with_observer_or_throw(
            destination_path,
            std::span<const unsigned char>(
                serialized_bytes_.get(), static_cast<std::size_t>(byte_count_)),
            label,
            observer,
            observer_context);
    verify_unchanged_or_throw(label + " postpublication");
}

void SealedSqliteSnapshot::
publish_exact_copy_atomically_create_new_with_observer_or_throw(
    const fs::path& destination_path,
    const std::string& label,
    atomic_file_publication_detail::AtomicFilePublicationObserver observer,
    void* observer_context) {
    require_current_process_or_throw(label);
    verify_unchanged_or_throw(label + " prepublication");
    atomic_file_publication_detail::
        write_sync_file_atomically_create_new_with_observer_or_throw(
            destination_path,
            std::span<const unsigned char>(
                serialized_bytes_.get(), static_cast<std::size_t>(byte_count_)),
            label,
            observer,
            observer_context);
    verify_unchanged_or_throw(label + " postpublication");
}

void SealedSqliteSnapshot::cleanup_noexcept() noexcept {
    require_current_process_noexcept();
    serialized_bytes_.reset();
    source_path_.clear();
    sha256_hex_.clear();
    pinned_vfs_name_.clear();
    byte_count_ = 0;
    geometry_ = {};
    geometry_policy_ = {};
    pinned_vfs_ = nullptr;
    process_id_ = {};
}

}  // namespace anonsync::persistence
