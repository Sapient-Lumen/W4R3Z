#include "sha256_digest.hpp"
#include "sqlite_path_security.hpp"
#include "sqlite_snapshot_seal.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_bootstrap_record.hpp"
#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_file_effect_sqlite_owner.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_file_tls_client.hpp"
#include "sync_replica_file_tls_server.hpp"
#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"
#include "sync_replica_tls_membership_anchored_owner.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"
#include "sync_replica_tls_transport.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/ssl.h>
#include <openssl/x509.h>
#include <sqlite3.h>

#ifdef __linux__
#include <arpa/inet.h>
#include <cerrno>
#include <cstring>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using SslContextOwner = std::unique_ptr<SSL_CTX, decltype(&SSL_CTX_free)>;
using BioOwner = std::unique_ptr<BIO, decltype(&BIO_free)>;
using CertificateOwner = std::unique_ptr<X509, decltype(&X509_free)>;

constexpr std::uint64_t kDefaultMaxPayloadBytes =
    4ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kMaximumCliPayloadBytes =
    64ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kDefaultTimeoutSeconds = 10U;
constexpr std::uint64_t kMaximumTimeoutSeconds = 3600U;
constexpr std::uint64_t kDefaultLeaseSeconds = 30U;
constexpr std::uint64_t kMaximumBootstrapSqliteImageBytes =
    64ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kMaximumBootstrapSqliteImagePages = 16384ULL;

[[nodiscard]] std::string openssl_errors() {
    std::string output;
    for (unsigned long code = ERR_get_error(); code != 0UL;
         code = ERR_get_error()) {
        char text[256]{};
        ERR_error_string_n(code, text, sizeof(text));
        if (!output.empty()) output += "; ";
        output += text;
    }
    return output.empty() ? "no OpenSSL detail" : output;
}

[[noreturn]] void throw_openssl(const std::string& message) {
    throw std::runtime_error(message + ": " + openssl_errors());
}

[[nodiscard]] std::string json_quote(std::string_view value) {
    std::ostringstream output;
    output << '"';
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2)
                           << std::setfill('0')
                           << static_cast<unsigned int>(byte)
                           << std::dec << std::setfill(' ');
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
    return output.str();
}

[[nodiscard]] const char* json_bool(bool value) noexcept {
    return value ? "true" : "false";
}

class Options final {
public:
    Options(int argc, char** argv, int first) {
        for (int index = first; index < argc; ++index) {
            std::string token = argv[index];
            if (!token.starts_with("--") || token.size() <= 2U) {
                throw std::invalid_argument(
                    "unexpected positional argument: " + token);
            }
            token.erase(0U, 2U);
            std::string key;
            std::string value;
            const std::size_t equals = token.find('=');
            if (equals != std::string::npos) {
                key = token.substr(0U, equals);
                value = token.substr(equals + 1U);
            } else {
                key = std::move(token);
                if (index + 1 >= argc ||
                    std::string_view(argv[index + 1]).starts_with("--")) {
                    throw std::invalid_argument(
                        "missing value for --" + key);
                }
                value = argv[++index];
            }
            if (key.empty()) {
                throw std::invalid_argument("empty option name");
            }
            values_[std::move(key)].push_back(std::move(value));
        }
    }

    void require_only(std::initializer_list<std::string_view> allowed) const {
        std::set<std::string_view> accepted(allowed.begin(), allowed.end());
        for (const auto& [key, ignored] : values_) {
            (void)ignored;
            if (!accepted.contains(key)) {
                throw std::invalid_argument("unknown option --" + key);
            }
        }
    }

    [[nodiscard]] bool has(std::string_view key) const {
        return values_.contains(std::string(key));
    }

    [[nodiscard]] const std::vector<std::string>& all(
        std::string_view key) const {
        static const std::vector<std::string> empty;
        const auto found = values_.find(std::string(key));
        return found == values_.end() ? empty : found->second;
    }

    [[nodiscard]] std::string one(std::string_view key) const {
        const auto& values = all(key);
        if (values.empty()) {
            throw std::invalid_argument(
                "required option --" + std::string(key) + " is missing");
        }
        if (values.size() != 1U) {
            throw std::invalid_argument(
                "option --" + std::string(key) +
                " must appear exactly once");
        }
        if (values.front().empty()) {
            throw std::invalid_argument(
                "option --" + std::string(key) + " must not be empty");
        }
        return values.front();
    }

    [[nodiscard]] std::string one_or(
        std::string_view key,
        std::string fallback) const {
        return has(key) ? one(key) : std::move(fallback);
    }

private:
    std::map<std::string, std::vector<std::string>> values_;
};

[[nodiscard]] std::uint64_t parse_uint64(
    std::string_view value,
    std::string_view label) {
    std::uint64_t parsed = 0U;
    const char* const begin = value.data();
    const char* const end = value.data() + value.size();
    const auto result = std::from_chars(begin, end, parsed, 10);
    if (result.ec != std::errc{} || result.ptr != end) {
        throw std::invalid_argument(
            std::string(label) + " is not an unsigned decimal integer");
    }
    return parsed;
}

[[nodiscard]] std::uint16_t parse_port(
    std::string_view value,
    std::string_view label) {
    const std::uint64_t parsed = parse_uint64(value, label);
    if (parsed == 0U || parsed > 65535U) {
        throw std::invalid_argument(
            std::string(label) + " must be in [1, 65535]");
    }
    return static_cast<std::uint16_t>(parsed);
}

[[nodiscard]] std::uint64_t option_uint64_or(
    const Options& options,
    std::string_view key,
    std::uint64_t fallback) {
    return options.has(key)
        ? parse_uint64(options.one(key), std::string("--") + std::string(key))
        : fallback;
}

[[nodiscard]] fs::path require_absolute_path(
    std::string value,
    std::string_view label) {
    fs::path path(std::move(value));
    if (!path.is_absolute()) {
        throw std::invalid_argument(
            std::string(label) + " must be an absolute path");
    }
    return path.lexically_normal();
}

[[nodiscard]] fs::path require_existing_directory(
    std::string value,
    std::string_view label) {
    fs::path path = require_absolute_path(std::move(value), label);
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (error || !fs::is_directory(status) || fs::is_symlink(status)) {
        throw std::invalid_argument(
            std::string(label) +
            " must name an existing non-symlink directory");
    }
    return path;
}

[[nodiscard]] fs::path require_database_path(
    std::string value,
    std::string_view label) {
    fs::path path = require_absolute_path(std::move(value), label);
    const fs::path parent = path.parent_path();
    if (parent.empty()) {
        throw std::invalid_argument(
            std::string(label) + " has no parent directory");
    }
    std::error_code error;
    const fs::file_status parent_status = fs::symlink_status(parent, error);
    if (error || !fs::is_directory(parent_status) ||
        fs::is_symlink(parent_status)) {
        throw std::invalid_argument(
            std::string(label) +
            " parent must be an existing non-symlink directory");
    }
    return path;
}

[[nodiscard]] fs::path require_existing_regular_file(
    std::string value,
    std::string_view label) {
    fs::path path = require_absolute_path(std::move(value), label);
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (error || !fs::is_regular_file(status) || fs::is_symlink(status)) {
        throw std::invalid_argument(
            std::string(label) +
            " must name an existing non-symlink regular file");
    }
    return path;
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    std::string_view bytes) noexcept {
    return {
        reinterpret_cast<const unsigned char*>(bytes.data()),
        bytes.size(),
    };
}

[[nodiscard]] fs::path append_ascii_path_suffix(
    const fs::path& path,
    std::string_view suffix) {
    fs::path::string_type native = path.native();
    for (const char byte : suffix) {
        native.push_back(static_cast<fs::path::value_type>(byte));
    }
    return fs::path(std::move(native));
}

[[nodiscard]] bool path_is_absent_or_throw(
    const fs::path& path,
    const std::string& label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (!error && status.type() == fs::file_type::not_found) return true;
    if (error == std::errc::no_such_file_or_directory) return true;
    if (error) {
        throw std::runtime_error(
            label + " could not prove path absence: " + error.message());
    }
    return false;
}

void require_path_absent_for_fresh_bootstrap_or_throw(
    const fs::path& path,
    const std::string& label) {
    if (path_is_absent_or_throw(path, label)) return;
    throw std::runtime_error(
        label + " must be absent for fresh bootstrap: " +
        path.generic_string());
}

void require_fresh_database_family_or_throw(
    const fs::path& database_path,
    const std::string& label) {
    require_path_absent_for_fresh_bootstrap_or_throw(
        database_path, label + " main database");
    for (const std::string_view suffix :
         {std::string_view("-journal"), std::string_view("-wal"),
          std::string_view("-shm")}) {
        require_path_absent_for_fresh_bootstrap_or_throw(
            append_ascii_path_suffix(database_path, suffix),
            label + " SQLite sidecar " + std::string(suffix));
    }
}

[[nodiscard]] bool directory_is_empty_or_throw(
    const fs::path& directory,
    const std::string& label) {
    std::error_code error;
    fs::directory_iterator cursor(directory, error);
    if (error) {
        throw std::runtime_error(
            label + " could not inspect directory: " + error.message());
    }
    return cursor == fs::directory_iterator{};
}

void require_empty_directory_for_fresh_bootstrap_or_throw(
    const fs::path& directory,
    const std::string& label) {
    if (!directory_is_empty_or_throw(directory, label)) {
        throw std::runtime_error(
            label + " must be empty for fresh bootstrap: " +
            directory.generic_string());
    }
}

[[nodiscard]] anonsync::SyncReplicaActor actor_from_options(
    const Options& options,
    std::string_view device_option,
    std::string_view epoch_option,
    std::string_view label) {
    anonsync::SyncReplicaActor actor{
        options.one(device_option),
        parse_uint64(options.one(epoch_option), epoch_option)};
    if (!anonsync::sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument(
            std::string(label) + " actor is invalid");
    }
    return actor;
}

[[nodiscard]] std::uint64_t max_payload_from_options(
    const Options& options) {
    const std::uint64_t maximum = option_uint64_or(
        options, "max-payload-bytes", kDefaultMaxPayloadBytes);
    if (maximum == 0U || maximum > kMaximumCliPayloadBytes) {
        throw std::invalid_argument(
            "--max-payload-bytes must be in [1, 67108864]");
    }
    return maximum;
}

[[nodiscard]] std::uint64_t timeout_from_options(const Options& options) {
    const std::uint64_t timeout = option_uint64_or(
        options, "timeout-seconds", kDefaultTimeoutSeconds);
    if (timeout == 0U || timeout > kMaximumTimeoutSeconds) {
        throw std::invalid_argument(
            "--timeout-seconds must be in [1, 3600]");
    }
    return timeout;
}

[[nodiscard]] std::unique_ptr<anonsync::SyncReplicaOutboxClockSource>
outbox_clock_source_from_options(const Options& options) {
    const bool has_authority = options.has("operator-clock-authority-id");
    const bool has_uncertainty =
        options.has("operator-clock-uncertainty-ns");
    if (has_authority != has_uncertainty) {
        throw std::invalid_argument(
            "--operator-clock-authority-id and "
            "--operator-clock-uncertainty-ns must be supplied together");
    }
    if (!has_authority) return {};
    return anonsync::
        make_operator_trusted_sync_replica_outbox_clock_source_or_throw(
            {options.one("operator-clock-authority-id"),
             parse_uint64(
                 options.one("operator-clock-uncertainty-ns"),
                 "--operator-clock-uncertainty-ns")});
}

[[nodiscard]] anonsync::SyncReplicaFileDeliveryServiceLimits
file_service_limits(std::uint64_t max_payload_bytes) {
    anonsync::SyncReplicaFileDeliveryServiceLimits limits;
    limits.max_payload_bytes = max_payload_bytes;

    // Preserve the protocol's reviewed default non-payload headroom instead
    // of guessing that a small fixed increment can contain the independently
    // bounded evidence request. The service constructor still validates the
    // complete relationship before any durable or network authority is spent.
    static_assert(
        anonsync::kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes >=
        anonsync::kSyncReplicaFileDeliveryDefaultMaxPayloadBytes);
    constexpr std::uint64_t kDefaultNonPayloadHeadroom =
        anonsync::kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes -
        anonsync::kSyncReplicaFileDeliveryDefaultMaxPayloadBytes;
    if (max_payload_bytes >
        std::numeric_limits<std::uint64_t>::max() -
            kDefaultNonPayloadHeadroom) {
        throw std::invalid_argument("payload request-frame ceiling overflow");
    }
    limits.max_request_frame_bytes =
        max_payload_bytes + kDefaultNonPayloadHeadroom;
    return limits;
}

[[nodiscard]] anonsync::SyncReplicaFilePayloadStoreLimits
payload_store_limits(std::uint64_t max_payload_bytes) {
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_payload_bytes = max_payload_bytes;
    return limits;
}

[[nodiscard]] anonsync::SyncReplicaFileEffectSqliteOwnerLimits
effect_owner_limits(std::uint64_t max_payload_bytes) {
    anonsync::SyncReplicaFileEffectSqliteOwnerLimits limits;
    limits.max_payload_bytes = max_payload_bytes;
    return limits;
}

enum class DatabaseOpenDisposition : std::uint8_t {
    ExistingOperational = 1U,
    ExistingBootstrapCandidate = 2U,
};

void validate_database_open_disposition_or_throw(
    DatabaseOpenDisposition disposition,
    const std::string& label) {
    switch (disposition) {
        case DatabaseOpenDisposition::ExistingOperational:
        case DatabaseOpenDisposition::ExistingBootstrapCandidate:
            return;
    }
    throw std::invalid_argument(
        label + " database open disposition is invalid");
}

class UnadoptedSqliteConnection final {
public:
    UnadoptedSqliteConnection() = default;
    ~UnadoptedSqliteConnection() noexcept {
        if (handle_ == nullptr) return;
        if (sqlite3_close(handle_) != SQLITE_OK) {
            // A fresh open candidate cannot legitimately own statements or
            // backups. close_v2 is only the no-throw last resort for an
            // exceptional SQLite implementation path during stack unwind.
            (void)sqlite3_close_v2(handle_);
        }
        handle_ = nullptr;
    }

    UnadoptedSqliteConnection(const UnadoptedSqliteConnection&) = delete;
    UnadoptedSqliteConnection& operator=(
        const UnadoptedSqliteConnection&) = delete;
    UnadoptedSqliteConnection(UnadoptedSqliteConnection&&) = delete;
    UnadoptedSqliteConnection& operator=(
        UnadoptedSqliteConnection&&) = delete;

    [[nodiscard]] sqlite3** out() noexcept { return &handle_; }
    [[nodiscard]] sqlite3* get() const noexcept { return handle_; }

    [[nodiscard]] sqlite3* release() noexcept {
        sqlite3* released = handle_;
        handle_ = nullptr;
        return released;
    }

    [[nodiscard]] int close_noexcept() noexcept {
        if (handle_ == nullptr) return SQLITE_OK;
        const int result = sqlite3_close(handle_);
        if (result == SQLITE_OK) handle_ = nullptr;
        return result;
    }

private:
    sqlite3* handle_ = nullptr;
};


// Product file-backed SQLite authority. Declaration order is intentional:
// reverse destruction closes the exact connection before unregistering its
// private descriptor-rooted VFS, then releases the retained path guard.
class ProductSqliteDatabaseAuthority final {
private:
    anonsync::SqlitePathFamilyGuard path_guard_;
    std::unique_ptr<anonsync::SqliteDescriptorRootedVfs> rooted_vfs_;

public:
    anonsync::SyncSqliteDbHandleSlot db;

    ProductSqliteDatabaseAuthority() = default;
    ProductSqliteDatabaseAuthority(
        anonsync::SqlitePathFamilyGuard path_guard,
        std::unique_ptr<anonsync::SqliteDescriptorRootedVfs> rooted_vfs)
        : path_guard_(std::move(path_guard)),
          rooted_vfs_(std::move(rooted_vfs)) {
        if (!rooted_vfs_) {
            throw std::invalid_argument(
                "product SQLite authority requires a rooted VFS");
        }
    }
    ~ProductSqliteDatabaseAuthority() = default;
    ProductSqliteDatabaseAuthority(
        const ProductSqliteDatabaseAuthority&) = delete;
    ProductSqliteDatabaseAuthority& operator=(
        const ProductSqliteDatabaseAuthority&) = delete;
    ProductSqliteDatabaseAuthority(
        ProductSqliteDatabaseAuthority&& other) noexcept
        : path_guard_(std::move(other.path_guard_)),
          rooted_vfs_(std::move(other.rooted_vfs_)),
          db(std::move(other.db)) {}
    ProductSqliteDatabaseAuthority& operator=(
        ProductSqliteDatabaseAuthority&& other) noexcept {
        if (this == &other) return *this;

        // Move assignment is also an authority replacement boundary. Revoke
        // in reverse ownership order before acquiring the incoming family.
        db = anonsync::SyncSqliteDbHandleSlot{};
        rooted_vfs_.reset();
        path_guard_ = anonsync::SqlitePathFamilyGuard{};
        path_guard_ = std::move(other.path_guard_);
        rooted_vfs_ = std::move(other.rooted_vfs_);
        db = std::move(other.db);
        return *this;
    }

    [[nodiscard]] const char* vfs_name_or_throw(
        const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(label + " has no descriptor-rooted VFS");
        }
        return rooted_vfs_->name();
    }

    void verify_open_database_or_throw(const std::string& label) {
        if (!rooted_vfs_ || !db) {
            throw std::logic_error(
                label + " has no live product SQLite authority");
        }
        auto borrow = db.borrow();
        rooted_vfs_->verify_open_database_or_throw(
            borrow.get(), label + " descriptor-rooted connection proof");
        path_guard_.verify_open_database_or_throw(
            borrow.get(), label + " logical-path authority proof");
    }

    [[nodiscard]] std::string
    read_bounded_main_file_before_open_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(
                label + " has no descriptor-rooted SQLite VFS");
        }
        return rooted_vfs_->read_bounded_main_file_before_open_or_throw(
            maximum_bytes, label);
    }

    [[nodiscard]] std::string read_bounded_main_file_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label) const {
        if (!rooted_vfs_ || !db) {
            throw std::logic_error(
                label + " has no live product SQLite authority");
        }
        auto borrow = anonsync::borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " live main-file read");
        return rooted_vfs_->read_bounded_main_file_or_throw(
            borrow.get(), maximum_bytes, label);
    }

    void verify_sidecars_absent_or_throw(const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(
                label + " has no descriptor-rooted SQLite VFS");
        }
        rooted_vfs_->verify_sidecars_absent_or_throw(label);
    }

    void verify_sidecar_absent_or_throw(
        std::string_view suffix,
        const std::string& label) const {
        if (!rooted_vfs_) {
            throw std::logic_error(
                label + " has no descriptor-rooted SQLite VFS");
        }
        rooted_vfs_->verify_sidecar_absent_or_throw(suffix, label);
    }

    void sync_main_file_and_parent_directory_or_throw(
        const std::string& label) const {
        if (!rooted_vfs_ || !db) {
            throw std::logic_error(
                label + " has no live product SQLite authority");
        }
        auto borrow = anonsync::borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " live main-file sync");
        rooted_vfs_->sync_main_file_and_parent_directory_or_throw(
            borrow.get(), label);
    }
};

[[noreturn]] void reject_unadopted_database_handle_or_throw(
    UnadoptedSqliteConnection& candidate,
    std::string message) {
    // sqlite3_open_v2 usually returns a diagnostic handle even on failure.
    // Until writability has been proved, that handle has not crossed the
    // product's connection-authority frontier and must never enter the strict
    // SyncSqliteDbHandleSlot.
    if (candidate.close_noexcept() != SQLITE_OK) {
        message += "; unadopted SQLite handle could not be closed";
    }
    throw std::runtime_error(std::move(message));
}

[[nodiscard]] bool database_has_persistent_schema_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database,
        "SELECT 1 FROM main.sqlite_schema "
        "WHERE name NOT LIKE 'sqlite_%' LIMIT 1;",
        label + " persistent-schema probe");
    const int row = sqlite3_step(statement.stmt);
    if (row == SQLITE_DONE) return false;
    if (row != SQLITE_ROW) {
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " persistent-schema probe");
    }
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " persistent-schema probe returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " persistent-schema trailing-row probe");
    }
    return true;
}

[[nodiscard]] std::string database_journal_mode_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database, "PRAGMA main.journal_mode;",
        label + " journal-mode probe");
    const int row = sqlite3_step(statement.stmt);
    if (row == SQLITE_DONE) {
        throw std::runtime_error(
            label + " journal-mode probe returned no row");
    }
    if (row != SQLITE_ROW) {
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " journal-mode probe");
    }
    const std::string mode = anonsync::sqlite_column_text_or_throw(
        statement.stmt, 0, label + " journal-mode value");
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " journal-mode probe returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " journal-mode trailing-row probe");
    }
    return mode;
}

void require_wal_journal_mode_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    const std::string mode = database_journal_mode_or_throw(database, label);
    if (mode != "wal") {
        throw std::runtime_error(
            label + " journal mode is " + mode + ", expected wal");
    }
}

void require_sealed_rollback_sidecars_absent_or_throw(
    const ProductSqliteDatabaseAuthority& database,
    const std::string& label) {
    try {
        database.verify_sidecars_absent_or_throw(label);
    } catch (const std::runtime_error& error) {
        const std::string detail(error.what());
        if (detail.find("SQLite sidecar must be absent") ==
            std::string::npos) {
            throw;
        }
        throw std::runtime_error(
            label + " sealed rollback bootstrap candidate has sidecar: " +
            detail);
    }
}

void require_bootstrap_candidate_header_and_namespace_or_throw(
    const ProductSqliteDatabaseAuthority& database,
    const std::string& label) {
    constexpr std::string_view kSqliteHeader("SQLite format 3\0", 16U);
    constexpr std::size_t kMinimumDatabaseHeaderBytes = 100U;
    const std::string image =
        database.read_bounded_main_file_before_open_or_throw(
            kMaximumBootstrapSqliteImageBytes,
            label + " immutable main-file preflight");
    if (image.size() < kMinimumDatabaseHeaderBytes ||
        std::string_view(image.data(), kSqliteHeader.size()) != kSqliteHeader) {
        throw std::runtime_error(
            label + " main file is not a complete SQLite database image");
    }

    const auto write_version =
        static_cast<unsigned char>(image[18]);
    const auto read_version =
        static_cast<unsigned char>(image[19]);
    if (write_version == 1U && read_version == 1U) {
        // A sealed genesis image is a self-contained rollback-mode main file.
        // Reject every sidecar before SQLite gets an opportunity to interpret,
        // recover, delete, or otherwise mutate a contaminated namespace.
        require_sealed_rollback_sidecars_absent_or_throw(database, label);
        return;
    }
    if (write_version == 2U && read_version == 2U) {
        database.verify_sidecar_absent_or_throw(
            "-journal", label + " WAL bootstrap candidate");
        return;
    }
    throw std::runtime_error(
        label + " SQLite header has unsupported read/write journal versions " +
        std::to_string(read_version) + "/" +
        std::to_string(write_version));
}

void retain_exclusive_bootstrap_candidate_locking_mode_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database, "PRAGMA main.locking_mode=EXCLUSIVE;",
        label + " exclusive locking-mode prepare");
    const int row = sqlite3_step(statement.stmt);
    if (row != SQLITE_ROW) {
        if (row == SQLITE_DONE) {
            throw std::runtime_error(
                label + " exclusive locking-mode request returned no row");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " exclusive locking-mode request");
    }
    const std::string mode = anonsync::sqlite_column_text_or_throw(
        statement.stmt, 0, label + " exclusive locking-mode value");
    if (mode != "exclusive") {
        throw std::runtime_error(
            label + " could not retain exclusive SQLite locking mode");
    }
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " exclusive locking-mode request returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " exclusive locking-mode trailing step");
    }
}

void configure_operational_database_profile_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    require_wal_journal_mode_or_throw(database, label);
    anonsync::sqlite_exec_or_throw(
        database,
        "PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;"
        "PRAGMA temp_store=MEMORY;"
        "PRAGMA foreign_keys=ON;"
        "PRAGMA trusted_schema=OFF;",
        label + " durability profile");
}

[[nodiscard]] ProductSqliteDatabaseAuthority open_database_or_throw(
    const fs::path& path,
    const std::string& label,
    DatabaseOpenDisposition disposition) {
    validate_database_open_disposition_or_throw(disposition, label);

    anonsync::SqlitePathFamilyGuard path_guard =
        anonsync::guard_sqlite_path_family_or_throw(
            path, false, {"-journal", "-wal", "-shm"},
            label + " path authority");
    if (!path_guard.parent_exists() ||
        !path_guard.database_existed_at_preflight()) {
        throw std::runtime_error(
            label + " unable to open database file: requires an existing "
                    "guarded main database");
    }
    const fs::path logical_path = path_guard.database_path();

    auto rooted_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            path_guard, label + " descriptor-rooted VFS");
    ProductSqliteDatabaseAuthority database(
        std::move(path_guard), std::move(rooted_vfs));
    if (disposition ==
        DatabaseOpenDisposition::ExistingBootstrapCandidate) {
        // The retained parent descriptor and frozen main-file identity define
        // the exact namespace that both this preflight and every later SQLite
        // family operation will inspect. Ambient ancestor rebinding cannot
        // splice a different image or sidecar set between preflight and xOpen.
        require_bootstrap_candidate_header_and_namespace_or_throw(
            database, label + " bootstrap candidate pre-open");
    }

    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    UnadoptedSqliteConnection candidate;
    const int opened = sqlite3_open_v2(
        logical_path.string().c_str(), candidate.out(), flags,
        database.vfs_name_or_throw(label));
    if (opened != SQLITE_OK) {
        reject_unadopted_database_handle_or_throw(
            candidate,
            anonsync::sqlite_error_message(candidate.get(), label + " open"));
    }
    if (candidate.get() == nullptr) {
        throw std::runtime_error(label + " open returned no SQLite handle");
    }
    const int read_only = sqlite3_db_readonly(candidate.get(), "main");
    if (read_only != 0) {
        reject_unadopted_database_handle_or_throw(
            candidate,
            label + (read_only > 0
                ? " open fell back to a read-only main database"
                : " open could not prove main-database writability"));
    }

    {
        auto output = database.db.out();
        sqlite3** destination = output.get();
        *destination = candidate.release();
    }
    database.verify_open_database_or_throw(
        label + " post-open path attestation");
    anonsync::sqlite_set_busy_timeout_or_throw(
        database.db, 5000, label + " busy timeout");
    if (disposition ==
        DatabaseOpenDisposition::ExistingBootstrapCandidate) {
        // The first subsequent database read obtains and retains SQLite's file
        // lock for this exact connection. That closes the ordinary-writer gap
        // between set-wide identity proof, durability reconciliation, WAL
        // promotion, and role-state attestation. Descriptor-rooted sidecars
        // prevent a parent-path substitution from redirecting that lock family.
        retain_exclusive_bootstrap_candidate_locking_mode_or_throw(
            database.db, label + " bootstrap candidate");
    }
    const bool has_persistent_schema =
        database_has_persistent_schema_or_throw(database.db, label);
    if (!has_persistent_schema) {
        throw std::runtime_error(
            label + " has no persistent schema and requires explicit "
            "bootstrap");
    }
    if (disposition == DatabaseOpenDisposition::ExistingOperational) {
        // journal_mode is persistent. Operational commands observe the
        // reviewed profile instead of silently rewriting an unrelated or
        // incompletely initialized target before its exact owner attests it.
        configure_operational_database_profile_or_throw(database.db, label);
    } else {
        const std::string mode =
            database_journal_mode_or_throw(database.db, label);
        if (mode != "delete" && mode != "wal") {
            throw std::runtime_error(
                label + " bootstrap candidate journal mode is " + mode +
                ", expected delete or wal");
        }
    }
    database.verify_open_database_or_throw(
        label + " post-profile path attestation");
    return database;
}

[[nodiscard]] anonsync::SyncSqliteDb
open_detached_bootstrap_database_or_throw(const std::string& label) {
    constexpr int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
        SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE | SQLITE_OPEN_MEMORY;
    UnadoptedSqliteConnection candidate;
    const int opened = sqlite3_open_v2(
        ":memory:", candidate.out(), flags, nullptr);
    if (opened != SQLITE_OK) {
        reject_unadopted_database_handle_or_throw(
            candidate,
            anonsync::sqlite_error_message(candidate.get(), label + " open"));
    }
    if (candidate.get() == nullptr) {
        throw std::runtime_error(
            label + " detached open returned no SQLite handle");
    }
    const char* const filename = sqlite3_db_filename(candidate.get(), "main");
    if (filename == nullptr || *filename != '\0') {
        reject_unadopted_database_handle_or_throw(
            candidate, label + " detached bootstrap database names a file");
    }

    anonsync::SyncSqliteDb database;
    {
        auto output = database.db.out();
        sqlite3** destination = output.get();
        *destination = candidate.release();
    }
    if (database_has_persistent_schema_or_throw(database.db, label)) {
        throw std::logic_error(
            label + " detached bootstrap database is not empty");
    }
    anonsync::sqlite_exec_or_throw(
        database.db,
        "PRAGMA temp_store=MEMORY;"
        "PRAGMA foreign_keys=ON;"
        "PRAGMA trusted_schema=OFF;",
        label + " detached profile");
    return database;
}

[[nodiscard]] anonsync::SyncReplicaSqliteDeploymentBinding
sqlite_deployment_binding_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    return anonsync::SyncReplicaSqliteDeploymentBinding{
        .deployment = anonsync::sync_replica_deployment_identity_or_throw(
            deployment, label + " deployment identity"),
        .role = role,
        .database_path = database_path,
    };
}

[[nodiscard]] ProductSqliteDatabaseAuthority
open_bound_operational_database_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    ProductSqliteDatabaseAuthority database = open_database_or_throw(
        database_path, label,
        DatabaseOpenDisposition::ExistingOperational);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db,
        sqlite_deployment_binding_or_throw(
            deployment, database_path, role, label),
        label + " store-set binding");
    return database;
}

[[nodiscard]] ProductSqliteDatabaseAuthority
open_bound_bootstrap_candidate_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    ProductSqliteDatabaseAuthority database = open_database_or_throw(
        database_path, label,
        DatabaseOpenDisposition::ExistingBootstrapCandidate);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db,
        sqlite_deployment_binding_or_throw(
            deployment, database_path, role, label),
        label + " store-set binding");
    return database;
}

void initialize_detached_sqlite_deployment_binding_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    anonsync::
        initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
            database,
            sqlite_deployment_binding_or_throw(
                deployment, database_path, role, label),
            label + " detached store-set binding");
}

void acquire_bootstrap_candidate_read_lock_or_throw(
    anonsync::SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        database,
        "SELECT id FROM main.anonsync_store_set_binding WHERE id=1;",
        label + " read-lock prepare");
    const int row = sqlite3_step(statement.stmt);
    if (row != SQLITE_ROW) {
        if (row == SQLITE_DONE) {
            throw std::runtime_error(
                label + " binding row disappeared before durability repair");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), row,
            label + " read-lock step");
    }
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " binding read-lock query returned excess rows");
        }
        anonsync::throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " read-lock trailing step");
    }
}

void promote_bound_bootstrap_candidate_to_operational_or_throw(
    ProductSqliteDatabaseAuthority& database,
    const anonsync::SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label) {
    const std::string mode = database_journal_mode_or_throw(database.db, label);
    if (mode == "delete") {
        require_sealed_rollback_sidecars_absent_or_throw(database, label);

        // Pin a rollback-mode read transaction while the exact main-file image
        // is read and flushed through SQLite's already-open main sqlite3_file.
        // This is essential on POSIX: opening and then closing an independent
        // descriptor for the same inode can release locks held by SQLite in the
        // process. The retained parent descriptor still prevents ambient
        // ancestor rebinding from substituting the bytes or directory.
        anonsync::SyncSqliteTransaction pin(
            database.db, label + " durability pin",
            anonsync::SyncSqliteTransactionMode::Deferred);
        acquire_bootstrap_candidate_read_lock_or_throw(
            database.db, label + " durability pin");
        const std::string exact_before =
            database.read_bounded_main_file_or_throw(
                kMaximumBootstrapSqliteImageBytes,
                label + " exact sealed image before durability flush");
        database.sync_main_file_and_parent_directory_or_throw(
            label + " sealed image durability flush");
        const std::string exact_after =
            database.read_bounded_main_file_or_throw(
                kMaximumBootstrapSqliteImageBytes,
                label + " exact sealed image after durability flush");
        if (exact_before != exact_after) {
            throw std::runtime_error(
                label + " sealed image changed across durability flush");
        }
        pin.commit();

        anonsync::sqlite_exec_or_throw(
            database.db, "PRAGMA main.journal_mode=WAL;",
            label + " WAL promotion");
        require_wal_journal_mode_or_throw(
            database.db, label + " WAL promotion");
    } else if (mode != "wal") {
        throw std::runtime_error(
            label + " bootstrap candidate journal mode is " + mode +
            ", expected delete or wal");
    }

    configure_operational_database_profile_or_throw(database.db, label);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db, binding, label + " post-promotion binding");
    database.verify_open_database_or_throw(
        label + " post-promotion path attestation");
}

template <typename InitializeAndVerifyRole>
void create_sealed_bootstrap_database_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role,
    const std::string& label,
    InitializeAndVerifyRole&& initialize_and_verify_role) {
    const anonsync::SyncReplicaSqliteDeploymentBinding binding =
        sqlite_deployment_binding_or_throw(
            deployment, database_path, role, label);
    anonsync::persistence::SealedSqliteSnapshot sealed = [&] {
        anonsync::SyncSqliteDb detached =
            open_detached_bootstrap_database_or_throw(
                label + " detached genesis image");
        initialize_detached_sqlite_deployment_binding_or_throw(
            detached.db, deployment, database_path, role,
            label + " detached genesis image");
        initialize_and_verify_role(detached.db);
        auto source = detached.db.borrow();
        return anonsync::persistence::SealedSqliteSnapshot::capture_database(
            source.get(),
            label + " sealed genesis image",
            anonsync::persistence::SqliteSnapshotSealPolicy{
                .maximum_bytes = kMaximumBootstrapSqliteImageBytes,
                .maximum_pages = kMaximumBootstrapSqliteImagePages,
            });
    }();
    // The earlier store-set inventory is only a planning observation. Reprove
    // the entire SQLite namespace family at the publication boundary so that
    // a late main file or sidecar cannot be silently adopted or combined with
    // this sealed genesis image. The create-new publisher independently makes
    // the final main-file transition no-replace atomic.
    require_fresh_database_family_or_throw(
        database_path, label + " prepublication namespace");
    sealed.publish_exact_copy_atomically_create_new_or_throw(
        database_path, label + " immutable genesis publication");

    ProductSqliteDatabaseAuthority published =
        open_bound_bootstrap_candidate_or_throw(
            deployment, database_path, role,
            label + " published genesis");
    promote_bound_bootstrap_candidate_to_operational_or_throw(
        published, binding, label + " published genesis");
}

[[nodiscard]] SslContextOwner load_tls_context_or_throw(
    const fs::path& certificate,
    const fs::path& private_key,
    const fs::path& ca_file,
    bool server,
    const std::string& label) {
    SslContextOwner context(SSL_CTX_new(TLS_method()), SSL_CTX_free);
    if (!context) throw_openssl(label + " could not allocate SSL_CTX");

    if (server) {
        anonsync::configure_sync_replica_tls13_server_context_or_throw(
            context.get(), label + " profile");
    } else {
        anonsync::configure_sync_replica_tls13_client_context_or_throw(
            context.get(), label + " profile");
    }

    ERR_clear_error();
    if (SSL_CTX_use_certificate_chain_file(
            context.get(), certificate.string().c_str()) != 1) {
        throw_openssl(label + " could not load certificate chain");
    }
    ERR_clear_error();
    if (SSL_CTX_use_PrivateKey_file(
            context.get(), private_key.string().c_str(),
            SSL_FILETYPE_PEM) != 1) {
        throw_openssl(label + " could not load private key");
    }
    ERR_clear_error();
    if (SSL_CTX_check_private_key(context.get()) != 1) {
        throw_openssl(label + " certificate/private key mismatch");
    }
    ERR_clear_error();
    if (SSL_CTX_load_verify_locations(
            context.get(), ca_file.string().c_str(), nullptr) != 1) {
        throw_openssl(label + " could not load CA trust file");
    }
    SSL_CTX_set_verify_depth(context.get(), 4);
    return context;
}

struct StagedDeadlines final {
    std::chrono::steady_clock::time_point first;
    std::chrono::steady_clock::time_point second;
    std::chrono::steady_clock::time_point third;
    std::chrono::steady_clock::time_point fourth;
    std::chrono::steady_clock::time_point fifth;
};

[[nodiscard]] StagedDeadlines staged_deadlines(std::uint64_t seconds) {
    const auto now = std::chrono::steady_clock::now();
    const auto budget = std::chrono::seconds(seconds);
    return {
        now + budget,
        now + budget * 2,
        now + budget * 3,
        now + budget * 4,
        now + budget * 5,
    };
}

[[nodiscard]] const char* payload_put_name(
    anonsync::SyncReplicaFilePayloadStorePutDisposition disposition) noexcept {
    switch (disposition) {
        case anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted:
            return "inserted";
        case anonsync::SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent:
            return "already_present";
    }
    return "unknown";
}

[[nodiscard]] const char* receipt_apply_name(
    anonsync::SyncReplicaFileDeliveryReceiptApplyResult result) noexcept {
    using Result = anonsync::SyncReplicaFileDeliveryReceiptApplyResult;
    switch (result) {
        case Result::EffectSettled: return "effect_settled";
        case Result::ReceiverEffectCapacityBlocked:
            return "receiver_effect_capacity_blocked";
        case Result::ReceiverEffectPathBlocked:
            return "receiver_effect_path_blocked";
        case Result::ReceiverEvidenceCapacityBlocked:
            return "receiver_evidence_capacity_blocked";
        case Result::ReceiverEvidencePending:
            return "receiver_evidence_pending";
        case Result::ReceiverEvidenceQuarantined:
            return "receiver_evidence_quarantined";
        case Result::ReceiverProjectionBlocked:
            return "receiver_projection_blocked";
        case Result::ReceiverDestinationConflict:
            return "receiver_destination_conflict";
        case Result::IntentMissing: return "intent_missing";
        case Result::StaleClaim: return "stale_claim";
        case Result::ExpiredClaim: return "expired_claim";
    }
    return "unknown";
}

[[nodiscard]] const char* server_disposition_name(
    anonsync::SyncReplicaFileTlsServerDisposition disposition) noexcept {
    using Disposition = anonsync::SyncReplicaFileTlsServerDisposition;
    switch (disposition) {
        case Disposition::AcceptDeadlineExpired:
            return "accept_deadline_expired";
        case Disposition::HandshakeDeadlineExpired:
            return "handshake_deadline_expired";
        case Disposition::HandshakeRejected: return "handshake_rejected";
        case Disposition::PeerUnauthorized: return "peer_unauthorized";
        case Disposition::PeerClosed: return "peer_closed";
        case Disposition::RequestDeadlineExpired:
            return "request_deadline_expired";
        case Disposition::ReceiptDeadlineExpired:
            return "receipt_deadline_expired";
        case Disposition::ReceiptSent: return "receipt_sent";
    }
    return "unknown";
}

[[nodiscard]] const char* server_shutdown_name(
    anonsync::SyncReplicaFileTlsServerShutdownDisposition disposition) noexcept {
    using Disposition =
        anonsync::SyncReplicaFileTlsServerShutdownDisposition;
    switch (disposition) {
        case Disposition::NotAttempted: return "not_attempted";
        case Disposition::CloseNotifySent: return "close_notify_sent";
        case Disposition::Complete: return "complete";
        case Disposition::DeadlineExpired: return "deadline_expired";
        case Disposition::Failed: return "failed";
    }
    return "unknown";
}

[[nodiscard]] const char* receive_disposition_name(
    anonsync::SyncReplicaFileTlsReceiveDisposition disposition) noexcept {
    using Disposition = anonsync::SyncReplicaFileTlsReceiveDisposition;
    switch (disposition) {
        case Disposition::PeerClosed: return "peer_closed";
        case Disposition::RequestDeadlineExpired:
            return "request_deadline_expired";
        case Disposition::ReceiptDeadlineExpired:
            return "receipt_deadline_expired";
        case Disposition::ReceiptSent: return "receipt_sent";
    }
    return "unknown";
}

[[nodiscard]] const char* file_receipt_disposition_name(
    anonsync::SyncReplicaFileDeliveryReceiptDisposition disposition) noexcept {
    using Disposition = anonsync::SyncReplicaFileDeliveryReceiptDisposition;
    switch (disposition) {
        case Disposition::Published: return "published";
        case Disposition::AlreadyPublished: return "already_published";
        case Disposition::EffectCapacityBlocked:
            return "effect_capacity_blocked";
        case Disposition::EvidenceCapacityBlocked:
            return "evidence_capacity_blocked";
        case Disposition::EvidencePending: return "evidence_pending";
        case Disposition::EvidenceQuarantined:
            return "evidence_quarantined";
        case Disposition::ProjectionBlocked: return "projection_blocked";
        case Disposition::DestinationConflict:
            return "destination_conflict";
        case Disposition::EffectPathBlocked: return "effect_path_blocked";
    }
    return "unknown";
}

[[nodiscard]] const char* outbox_clock_health_name(
    anonsync::SyncReplicaOutboxClockHealth health) noexcept {
    switch (health) {
        case anonsync::SyncReplicaOutboxClockHealth::Uninitialized:
            return "uninitialized";
        case anonsync::SyncReplicaOutboxClockHealth::Healthy:
            return "healthy";
        case anonsync::SyncReplicaOutboxClockHealth::Quarantined:
            return "quarantined";
    }
    return "unknown";
}

[[nodiscard]] const char* outbox_clock_observation_outcome_name(
    anonsync::SyncReplicaOutboxClockObservationOutcome outcome) noexcept {
    using Outcome = anonsync::SyncReplicaOutboxClockObservationOutcome;
    switch (outcome) {
        case Outcome::Accepted: return "accepted";
        case Outcome::Quarantined: return "quarantined";
        case Outcome::AlreadyQuarantined: return "already_quarantined";
    }
    return "unknown";
}

[[nodiscard]] const char* clock_profile_name(bool operator_trusted) noexcept {
    return operator_trusted ? "operator-trusted" : "system";
}

void append_outbox_clock_state_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaOutboxClockState& state) {
    output
        << ",\"clock_health\":"
        << json_quote(outbox_clock_health_name(state.health))
        << ",\"clock_anomaly\":"
        << json_quote(anonsync::sync_replica_outbox_clock_anomaly_name(
               state.anomaly))
        << ",\"clock_high_water_epoch\":" << state.high_water_epoch
        << ",\"clock_observation_generation\":"
        << state.observation_generation
        << ",\"clock_recovery_generation\":"
        << state.recovery_generation
        << ",\"clock_accepted_observation_present\":"
        << json_bool(state.accepted.has_value())
        << ",\"clock_rejected_observation_present\":"
        << json_bool(state.rejected.has_value());
}

struct ProductStatusOutboxCounts final {
    std::uint64_t intents = 0U;
    std::uint64_t unclaimed = 0U;
    std::uint64_t claimable_at_high_water = 0U;
    std::uint64_t claimed_live_at_high_water = 0U;
    std::uint64_t expired_at_high_water = 0U;
    std::uint64_t retry_waiting_at_high_water = 0U;
    std::uint64_t dispatch_attempts = 0U;
};

[[nodiscard]] ProductStatusOutboxCounts summarize_outbox_at_high_water_or_throw(
    const std::vector<anonsync::SyncReplicaSqliteOutboxIntent>& outbox,
    std::uint64_t high_water_epoch) {
    ProductStatusOutboxCounts counts;
    counts.intents = static_cast<std::uint64_t>(outbox.size());
    for (const auto& intent : outbox) {
        const auto& lease = intent.lease;
        counts.dispatch_attempts += lease.dispatch_attempts;
        const bool claimable = high_water_epoch != 0U &&
            anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                lease, high_water_epoch, "anonsync_replica status outbox");
        if (claimable) ++counts.claimable_at_high_water;
        if (lease.claim_id.empty()) {
            if (lease.retry_not_before_epoch != 0U &&
                (high_water_epoch == 0U ||
                 lease.retry_not_before_epoch > high_water_epoch)) {
                ++counts.retry_waiting_at_high_water;
            } else {
                ++counts.unclaimed;
            }
            continue;
        }
        if (lease.lease_expires_at_epoch <= high_water_epoch) {
            ++counts.expired_at_high_water;
        } else {
            ++counts.claimed_live_at_high_water;
        }
    }
    return counts;
}

struct ProductStatusEffectCounts final {
    std::uint64_t staged = 0U;
    std::uint64_t published = 0U;
};

[[nodiscard]] ProductStatusEffectCounts summarize_effects(
    const std::vector<anonsync::SyncReplicaFileEffectRecord>& effects) {
    ProductStatusEffectCounts counts;
    for (const auto& effect : effects) {
        switch (effect.state) {
            case anonsync::SyncReplicaFileEffectState::Staged:
                ++counts.staged;
                break;
            case anonsync::SyncReplicaFileEffectState::Published:
                ++counts.published;
                break;
        }
    }
    return counts;
}

void require_paired_options(
    const Options& options,
    std::string_view first,
    std::string_view second) {
    if (options.has(first) != options.has(second)) {
        throw std::invalid_argument(
            "--" + std::string(first) + " and --" + std::string(second) +
            " must be supplied together");
    }
}

[[nodiscard]] anonsync::SyncReplicaDeploymentManifest
load_operational_deployment_manifest_or_throw(
    const Options& options,
    std::string_view command) {
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    return anonsync::read_sync_replica_deployment_manifest_or_throw(
        manifest_path,
        "anonsync_replica " + std::string(command) + " deployment manifest");
}


void append_deployment_authority_json_fields(
    std::ostream& output,
    const anonsync::SyncReplicaDeploymentManifest& deployment) {
    output
        << ",\"deployment_id\":"
        << json_quote(deployment.deployment_id)
        << ",\"deployment_manifest_digest\":"
        << json_quote(deployment.manifest_digest);
}

[[nodiscard]] const fs::path& require_payload_root(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    std::string_view command) {
    if (!deployment.payload_root.has_value()) {
        throw std::invalid_argument(
            "anonsync_replica " + std::string(command) +
            " requires a payload_root in the deployment manifest");
    }
    return *deployment.payload_root;
}

void require_effect_store(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    std::string_view command) {
    if (!deployment.effect_db.has_value() ||
        !deployment.files_root.has_value()) {
        throw std::invalid_argument(
            "anonsync_replica " + std::string(command) +
            " requires effect_db and files_root in the deployment manifest");
    }
}

void require_membership_store(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    std::string_view command) {
    if (!deployment.membership_db.has_value() ||
        !deployment.anchor_db.has_value()) {
        throw std::invalid_argument(
            "anonsync_replica " + std::string(command) +
            " requires membership_db and anchor_db in the deployment manifest");
    }
}

[[nodiscard]] anonsync::SyncReplicaTlsMembershipEntry parse_peer_entry(
    std::string_view encoded) {
    const std::size_t first = encoded.find(':');
    const std::size_t second = first == std::string_view::npos
        ? std::string_view::npos
        : encoded.find(':', first + 1U);
    if (first == std::string_view::npos ||
        second == std::string_view::npos ||
        encoded.find(':', second + 1U) != std::string_view::npos) {
        throw std::invalid_argument(
            "--peer must be DEVICE_ID:EPOCH:LOWERCASE_SPKI_SHA256");
    }
    anonsync::SyncReplicaTlsMembershipEntry entry;
    entry.actor.device_id = std::string(encoded.substr(0U, first));
    entry.actor.epoch = parse_uint64(
        encoded.substr(first + 1U, second - first - 1U), "peer epoch");
    entry.spki_sha256 = std::string(encoded.substr(second + 1U));
    if (!anonsync::sync_id_is_valid(entry.actor.device_id) ||
        entry.actor.epoch == 0U ||
        !anonsync::is_lowercase_sha256_hex(entry.spki_sha256)) {
        throw std::invalid_argument("--peer contains invalid actor or SPKI");
    }
    return entry;
}

#ifdef __linux__
class FileDescriptor final {
public:
    explicit FileDescriptor(int value = -1) noexcept : value_(value) {}
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept
        : value_(std::exchange(other.value_, -1)) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            close_noexcept();
            value_ = std::exchange(other.value_, -1);
        }
        return *this;
    }
    ~FileDescriptor() noexcept { close_noexcept(); }

    [[nodiscard]] int get() const noexcept { return value_; }

private:
    void close_noexcept() noexcept {
        if (value_ >= 0) {
            const int owned = std::exchange(value_, -1);
            (void)::close(owned);
        }
    }

    int value_ = -1;
};

struct ListenerSocket final {
    FileDescriptor descriptor;
};

[[nodiscard]] ListenerSocket make_listener_or_throw(
    std::string_view numeric_address,
    std::uint16_t port,
    const std::string& label) {
    sockaddr_storage storage{};
    socklen_t bytes = 0U;
    int family = AF_UNSPEC;

    sockaddr_in ipv4{};
    ipv4.sin_family = AF_INET;
    ipv4.sin_port = htons(port);
    if (::inet_pton(
            AF_INET, std::string(numeric_address).c_str(),
            &ipv4.sin_addr) == 1) {
        family = AF_INET;
        std::memcpy(&storage, &ipv4, sizeof(ipv4));
        bytes = sizeof(ipv4);
    } else {
        sockaddr_in6 ipv6{};
        ipv6.sin6_family = AF_INET6;
        ipv6.sin6_port = htons(port);
        if (::inet_pton(
                AF_INET6, std::string(numeric_address).c_str(),
                &ipv6.sin6_addr) != 1) {
            throw std::invalid_argument(
                label +
                " bind address is not numeric IPv4 or unscoped IPv6");
        }
        family = AF_INET6;
        std::memcpy(&storage, &ipv6, sizeof(ipv6));
        bytes = sizeof(ipv6);
    }

    const int raw = ::socket(
        family, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (raw < 0) {
        throw std::runtime_error(
            label + " socket failed (errno " + std::to_string(errno) + ")");
    }
    ListenerSocket listener{FileDescriptor(raw)};
    int one = 1;
    if (::setsockopt(
            raw, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)) != 0) {
        throw std::runtime_error(
            label + " SO_REUSEADDR failed (errno " +
            std::to_string(errno) + ")");
    }
    if (family == AF_INET6 &&
        ::setsockopt(
            raw, IPPROTO_IPV6, IPV6_V6ONLY, &one, sizeof(one)) != 0) {
        throw std::runtime_error(
            label + " IPV6_V6ONLY failed (errno " +
            std::to_string(errno) + ")");
    }
    if (::bind(
            raw, reinterpret_cast<const sockaddr*>(&storage), bytes) != 0) {
        throw std::runtime_error(
            label + " bind failed (errno " + std::to_string(errno) + ")");
    }
    if (::listen(raw, 16) != 0) {
        throw std::runtime_error(
            label + " listen failed (errno " + std::to_string(errno) + ")");
    }
    return listener;
}
#endif

struct BootstrapResourceInventory final {
    bool replica_database_present = false;
    bool payload_store_present = false;
    bool effect_database_present = false;
    bool membership_database_present = false;
    bool anchor_database_present = false;
    bool files_root_empty = true;

    [[nodiscard]] std::uint64_t missing_store_count(
        const anonsync::SyncReplicaDeploymentManifest& deployment) const
        noexcept {
        std::uint64_t missing = replica_database_present ? 0U : 1U;
        if (deployment.payload_root.has_value() && !payload_store_present) {
            ++missing;
        }
        if (deployment.effect_db.has_value() && !effect_database_present) {
            ++missing;
        }
        if (deployment.membership_db.has_value()) {
            if (!membership_database_present) ++missing;
            if (!anchor_database_present) ++missing;
        }
        return missing;
    }
};

struct BootstrapExistingSqliteAuthorities final {
    std::optional<ProductSqliteDatabaseAuthority> replica;
    std::optional<ProductSqliteDatabaseAuthority> effect;
    std::optional<ProductSqliteDatabaseAuthority> membership;
    std::optional<ProductSqliteDatabaseAuthority> anchor;
};

[[nodiscard]] bool database_main_is_present_for_resume_or_throw(
    const fs::path& database_path,
    const std::string& label) {
    if (path_is_absent_or_throw(database_path, label + " main database")) {
        for (const std::string_view suffix :
             {std::string_view("-journal"), std::string_view("-wal"),
              std::string_view("-shm")}) {
            const fs::path sidecar_path =
                append_ascii_path_suffix(database_path, suffix);
            if (!path_is_absent_or_throw(
                    sidecar_path,
                    label + " orphan SQLite sidecar " + std::string(suffix))) {
                throw std::runtime_error(
                    label + " orphan SQLite sidecar " + std::string(suffix) +
                    " must be absent when the main database is absent: " +
                    sidecar_path.generic_string());
            }
        }
        return false;
    }

    std::error_code error;
    const fs::file_status status = fs::symlink_status(database_path, error);
    if (error || fs::is_symlink(status) || !fs::is_regular_file(status)) {
        throw std::runtime_error(
            label + " main database must be a non-symlink regular file: " +
            database_path.generic_string());
    }
    return true;
}

void require_existing_deployment_directory_or_throw(
    const fs::path& directory,
    const std::string& label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(directory, error);
    if (error || fs::is_symlink(status) || !fs::is_directory(status)) {
        throw std::runtime_error(
            label + " must be an existing non-symlink directory: " +
            directory.generic_string());
    }
}

[[nodiscard]] BootstrapResourceInventory
inspect_bootstrap_resource_inventory_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    BootstrapResourceInventory inventory;
    inventory.replica_database_present =
        database_main_is_present_for_resume_or_throw(
            deployment.replica_db, label + " replica database");

    if (deployment.payload_root.has_value()) {
        require_existing_deployment_directory_or_throw(
            *deployment.payload_root, label + " payload root");
        inventory.payload_store_present = !directory_is_empty_or_throw(
            *deployment.payload_root, label + " payload root");
    }
    if (deployment.effect_db.has_value()) {
        require_existing_deployment_directory_or_throw(
            *deployment.files_root, label + " files root");
        inventory.effect_database_present =
            database_main_is_present_for_resume_or_throw(
                *deployment.effect_db, label + " effect database");
        inventory.files_root_empty = directory_is_empty_or_throw(
            *deployment.files_root, label + " files root");
    }
    if (deployment.membership_db.has_value()) {
        inventory.membership_database_present =
            database_main_is_present_for_resume_or_throw(
                *deployment.membership_db,
                label + " membership database");
        inventory.anchor_database_present =
            database_main_is_present_for_resume_or_throw(
                *deployment.anchor_db,
                label + " membership anchor database");
    }
    return inventory;
}

[[nodiscard]] BootstrapExistingSqliteAuthorities
attest_existing_bootstrap_resource_identities_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    DatabaseOpenDisposition disposition,
    const std::string& label) {
    BootstrapExistingSqliteAuthorities authorities;
    const auto open_bound = [&](
                                const fs::path& path,
                                anonsync::SyncReplicaSqliteDeploymentRole role,
                                const std::string& resource_label) {
        if (disposition == DatabaseOpenDisposition::ExistingOperational) {
            return open_bound_operational_database_or_throw(
                deployment, path, role, resource_label);
        }
        return open_bound_bootstrap_candidate_or_throw(
            deployment, path, role, resource_label);
    };

    // Identity is the first phase. Every existing SQLite main file must prove
    // the exact record-selected deployment, role, and pathname before any role
    // owner or WAL promotion is allowed to mutate another resource. Handles
    // remain retained so the role-state phase cannot accidentally reopen a
    // different pathname object after identity attestation.
    if (inventory.replica_database_present) {
        authorities.replica.emplace(open_bound(
            deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            label + " replica database"));
    }
    if (inventory.effect_database_present) {
        authorities.effect.emplace(open_bound(
            *deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            label + " effect database"));
    }
    if (inventory.membership_database_present) {
        authorities.membership.emplace(open_bound(
            *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database"));
    }
    if (inventory.anchor_database_present) {
        authorities.anchor.emplace(open_bound(
            *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database"));
    }
    if (inventory.payload_store_present) {
        anonsync::SyncReplicaFilePayloadStore payload_store(
            anonsync::sync_replica_deployment_identity_or_throw(
                deployment, label + " payload identity"),
            *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            payload_store_limits(deployment.max_payload_bytes),
            label + " payload store");
        (void)payload_store.snapshot_or_throw();
    }
    return authorities;
}

void promote_existing_bootstrap_sqlite_authorities_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    BootstrapExistingSqliteAuthorities& authorities,
    const std::string& label) {
    const auto promote = [&](
                             std::optional<ProductSqliteDatabaseAuthority>& database,
                             const fs::path& path,
                             anonsync::SyncReplicaSqliteDeploymentRole role,
                             const std::string& resource_label) {
        if (!database.has_value()) return;
        promote_bound_bootstrap_candidate_to_operational_or_throw(
            *database,
            sqlite_deployment_binding_or_throw(
                deployment, path, role, resource_label),
            resource_label);
    };
    promote(
        authorities.replica, deployment.replica_db,
        anonsync::SyncReplicaSqliteDeploymentRole::Replica,
        label + " replica database");
    if (deployment.effect_db.has_value()) {
        promote(
            authorities.effect, *deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            label + " effect database");
    }
    if (deployment.membership_db.has_value()) {
        promote(
            authorities.membership, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database");
    }
    if (deployment.anchor_db.has_value()) {
        promote(
            authorities.anchor, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database");
    }
}

[[nodiscard]] bool replica_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaSqliteSnapshot& snapshot) noexcept {
    return snapshot.state_generation == 1U &&
        snapshot.policy_generation == 1U &&
        snapshot.durable.last_local_counter == 0U &&
        snapshot.durable.local_operation_ids.empty() &&
        snapshot.durable.operations.empty() && snapshot.outbox.empty() &&
        snapshot.outbox_clock_state == anonsync::SyncReplicaOutboxClockState{};
}

[[nodiscard]] bool payload_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaFilePayloadStoreSnapshot& snapshot) {
    return snapshot.entry_count() == 0U && snapshot.indexed_bytes() == 0U &&
        snapshot.transient_entry_count() == 0U &&
        snapshot.transient_bytes() == 0U;
}

[[nodiscard]] bool effect_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaFileEffectSqliteSnapshot& snapshot) noexcept {
    return snapshot.state_generation == 0U &&
        snapshot.retained_payload_bytes == 0U && snapshot.effects.empty() &&
        snapshot.actor_usage.empty() && snapshot.device_usage.empty();
}

[[nodiscard]] bool membership_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaTlsMembershipSqliteSnapshot& snapshot) noexcept {
    return snapshot.state_generation == 0U &&
        snapshot.current_policy_epoch == 0U &&
        snapshot.current_entry_count == 0U && snapshot.history.empty() &&
        !snapshot.current_authority.has_value();
}

[[nodiscard]] bool membership_anchor_snapshot_is_bootstrap_genesis(
    const anonsync::SyncReplicaTlsMembershipAnchorSqliteSnapshot& snapshot,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    return snapshot.transition_sequence == 0U && snapshot.history.empty() &&
        snapshot.current_anchor ==
            anonsync::sync_replica_tls_membership_genesis_anchor_or_throw(
                deployment.folder_id, deployment.local_actor,
                label + " expected genesis");
}

struct BootstrapPresentResourceAttestation final {
    bool all_present_resources_are_genesis = true;
};

[[nodiscard]] BootstrapPresentResourceAttestation
attest_existing_bootstrap_role_state_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    BootstrapExistingSqliteAuthorities& authorities,
    const std::string& label) {
    BootstrapPresentResourceAttestation result;

    if (inventory.replica_database_present) {
        if (!authorities.replica.has_value()) {
            throw std::logic_error(
                label + " retained replica authority is absent");
        }
        anonsync::SyncReplicaSqliteOwner owner(
            authorities.replica->db, deployment.folder_id,
            deployment.local_actor, {},
            label + " replica owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            replica_snapshot_is_bootstrap_genesis(owner.snapshot_or_throw());
    }

    if (inventory.payload_store_present) {
        anonsync::SyncReplicaFilePayloadStore store(
            anonsync::sync_replica_deployment_identity_or_throw(
                deployment, label + " payload identity"),
            *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            payload_store_limits(deployment.max_payload_bytes),
            label + " payload store");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            payload_snapshot_is_bootstrap_genesis(store.snapshot_or_throw());
    }

    if (inventory.effect_database_present) {
        if (!authorities.effect.has_value()) {
            throw std::logic_error(
                label + " retained effect authority is absent");
        }
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            authorities.effect->db, deployment.folder_id,
            *deployment.files_root,
            effect_owner_limits(deployment.max_payload_bytes),
            label + " effect owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            effect_snapshot_is_bootstrap_genesis(owner.snapshot_or_throw());
    }
    if (deployment.effect_db.has_value() && !inventory.files_root_empty) {
        result.all_present_resources_are_genesis = false;
    }

    if (inventory.membership_database_present) {
        if (!authorities.membership.has_value()) {
            throw std::logic_error(
                label + " retained membership authority is absent");
        }
        anonsync::SyncReplicaTlsMembershipSqliteOwner owner(
            authorities.membership->db, deployment.folder_id,
            deployment.local_actor,
            label + " membership owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            membership_snapshot_is_bootstrap_genesis(
                owner.snapshot_or_throw());
    }

    if (inventory.anchor_database_present) {
        if (!authorities.anchor.has_value()) {
            throw std::logic_error(
                label + " retained membership-anchor authority is absent");
        }
        anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner owner(
            authorities.anchor->db, deployment.folder_id,
            deployment.local_actor,
            label + " membership anchor owner");
        result.all_present_resources_are_genesis =
            result.all_present_resources_are_genesis &&
            membership_anchor_snapshot_is_bootstrap_genesis(
                owner.snapshot_or_throw(), deployment,
                label + " membership anchor");
    }
    return result;
}

void create_missing_bootstrap_resources_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    const std::string& label) {
    const anonsync::SyncReplicaDeploymentIdentity deployment_identity =
        anonsync::sync_replica_deployment_identity_or_throw(
            deployment, label + " deployment identity");

    if (!inventory.replica_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            label + " replica database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaSqliteOwner owner(
                    database, deployment.folder_id, deployment.local_actor, {},
                    label + " replica owner");
                if (!replica_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw())) {
                    throw std::logic_error(
                        label +
                        " newly created replica database is not at genesis");
                }
            });
    }

    if (deployment.payload_root.has_value() &&
        !inventory.payload_store_present) {
        anonsync::SyncReplicaFilePayloadStore store(
            deployment_identity, *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            payload_store_limits(deployment.max_payload_bytes),
            label + " payload store");
        if (!payload_snapshot_is_bootstrap_genesis(store.snapshot_or_throw())) {
            throw std::logic_error(
                label + " newly created payload store is not at genesis");
        }
    }

    if (deployment.effect_db.has_value() &&
        !inventory.effect_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, *deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            label + " effect database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaFileEffectSqliteOwner owner(
                    database, deployment.folder_id, *deployment.files_root,
                    effect_owner_limits(deployment.max_payload_bytes),
                    label + " effect owner");
                if (!effect_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw())) {
                    throw std::logic_error(
                        label +
                        " newly created effect database is not at genesis");
                }
            });
    }

    if (deployment.membership_db.has_value() &&
        !inventory.membership_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaTlsMembershipSqliteOwner owner(
                    database, deployment.folder_id, deployment.local_actor,
                    anonsync::SyncReplicaTlsPolicySqliteBackendDisposition::
                        DetachedBootstrapImage,
                    label + " membership owner");
                if (!membership_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw())) {
                    throw std::logic_error(
                        label +
                        " newly created membership database is not at genesis");
                }
            });
    }

    if (deployment.anchor_db.has_value() &&
        !inventory.anchor_database_present) {
        create_sealed_bootstrap_database_or_throw(
            deployment, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database",
            [&](anonsync::SyncSqliteDbHandleSlot& database) {
                anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner owner(
                    database, deployment.folder_id, deployment.local_actor,
                    anonsync::SyncReplicaTlsPolicySqliteBackendDisposition::
                        DetachedBootstrapImage,
                    label + " membership anchor owner");
                if (!membership_anchor_snapshot_is_bootstrap_genesis(
                        owner.snapshot_or_throw(), deployment,
                        label + " membership anchor")) {
                    throw std::logic_error(
                        label + " newly created membership anchor database "
                                "is not at genesis");
                }
            });
    }
}

void reconcile_complete_bootstrap_membership_pair_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    if (!deployment.membership_db.has_value()) return;
    ProductSqliteDatabaseAuthority membership_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database");
    ProductSqliteDatabaseAuthority anchor_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database");
    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, deployment.folder_id, deployment.local_actor,
        label + " membership owner");
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.db, deployment.folder_id, deployment.local_actor,
        label + " membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner coordinator(
        membership_owner, anchor_owner, label + " anchored coordinator");
    (void)coordinator.reconcile_or_throw();
}

struct CompleteBootstrapStoreAuthorities final {
    BootstrapResourceInventory inventory;
    BootstrapExistingSqliteAuthorities sqlite;
};

[[nodiscard]] CompleteBootstrapStoreAuthorities
attest_complete_bootstrap_store_identities_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    const BootstrapResourceInventory inventory =
        inspect_bootstrap_resource_inventory_or_throw(deployment, label);
    const std::uint64_t missing = inventory.missing_store_count(deployment);
    if (missing != 0U) {
        throw std::runtime_error(
            label + " selected store set remains incomplete after bootstrap: " +
            std::to_string(missing) + " store(s) missing");
    }
    BootstrapExistingSqliteAuthorities authorities =
        attest_existing_bootstrap_resource_identities_or_throw(
            deployment, inventory,
            DatabaseOpenDisposition::ExistingOperational,
            label + " identity attestation");
    return CompleteBootstrapStoreAuthorities{
        .inventory = inventory,
        .sqlite = std::move(authorities),
    };
}

void attest_complete_bootstrap_store_set_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    CompleteBootstrapStoreAuthorities authorities =
        attest_complete_bootstrap_store_identities_or_throw(
            deployment, label);
    (void)attest_existing_bootstrap_role_state_or_throw(
        deployment, authorities.inventory, authorities.sqlite,
        label + " role-state attestation");
    reconcile_complete_bootstrap_membership_pair_or_throw(
        deployment, label + " membership reconciliation");
}

void require_fresh_inventory_after_bootstrap_record_or_throw(
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const BootstrapResourceInventory& inventory,
    const std::string& label) {
    if (inventory.replica_database_present || inventory.payload_store_present ||
        inventory.effect_database_present ||
        inventory.membership_database_present ||
        inventory.anchor_database_present || !inventory.files_root_empty) {
        throw std::runtime_error(
            label +
            " selected namespace changed after the durable bootstrap record "
            "was published; use init-resume to attest the exact recorded "
            "deployment instead of adopting observed resources");
    }
    if (inventory.missing_store_count(deployment) == 0U) {
        throw std::logic_error(
            label + " fresh inventory unexpectedly selects no creatable store");
    }
}

void attest_committed_manifest_matches_bootstrap_record_or_throw(
    const anonsync::SyncReplicaBootstrapRecord& record,
    const std::string& label) {
    const std::string exact =
        anonsync::read_sync_bounded_regular_file_no_symlink_or_throw(
            record.deployment.manifest_path,
            anonsync::kSyncReplicaDeploymentManifestMaxBytes,
            label + " exact final manifest");
    const anonsync::SyncReplicaDeploymentManifest committed =
        anonsync::decode_sync_replica_deployment_manifest_or_throw(
            exact, record.deployment.manifest_path,
            label + " final manifest bytes");
    if (exact != record.exact_manifest_bytes ||
        committed != record.deployment) {
        throw std::runtime_error(
            label +
            " final deployment manifest conflicts with the immutable "
            "bootstrap record");
    }
    const anonsync::SyncImmutableFileReconciliationOutcome durability =
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            record.deployment.manifest_path, byte_span(exact),
            label + " durability reconciliation");
    if (durability != anonsync::SyncImmutableFileReconciliationOutcome::
                          ExactAndDirectorySynced) {
        throw std::runtime_error(
            label + " final deployment manifest could not be reconciled as "
            "exact and directory-synced: " +
            anonsync::sync_immutable_file_reconciliation_outcome_name(
                durability));
    }
}

int command_init(const Options& options) {
    options.require_only({
        "manifest", "replica-db", "payload-root", "effect-db",
        "files-root", "membership-db", "anchor-db", "folder",
        "local-device", "local-epoch", "max-payload-bytes"});
    require_paired_options(options, "effect-db", "files-root");
    require_paired_options(options, "membership-db", "anchor-db");

    anonsync::SyncReplicaDeploymentManifest deployment;
    deployment.deployment_id =
        anonsync::generate_sync_replica_deployment_id_or_throw(
            "anonsync_replica init");
    deployment.manifest_path = require_database_path(
        options.one("manifest"), "--manifest");
    deployment.replica_db = require_database_path(
        options.one("replica-db"), "--replica-db");
    if (options.has("payload-root")) {
        deployment.payload_root = require_existing_directory(
            options.one("payload-root"), "--payload-root");
    }
    if (options.has("effect-db")) {
        deployment.effect_db = require_database_path(
            options.one("effect-db"), "--effect-db");
        deployment.files_root = require_existing_directory(
            options.one("files-root"), "--files-root");
    }
    if (options.has("membership-db")) {
        deployment.membership_db = require_database_path(
            options.one("membership-db"), "--membership-db");
        deployment.anchor_db = require_database_path(
            options.one("anchor-db"), "--anchor-db");
    }
    deployment.folder_id = options.one("folder");
    if (!anonsync::sync_id_is_valid(deployment.folder_id)) {
        throw std::invalid_argument(
            "--folder is not a lowercase portable sync ID");
    }
    deployment.local_actor = actor_from_options(
        options, "local-device", "local-epoch", "local");
    deployment.max_payload_bytes = max_payload_from_options(options);
    deployment.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            deployment, "anonsync_replica init deployment manifest");
    anonsync::validate_sync_replica_bootstrap_record_namespace_or_throw(
        deployment, "anonsync_replica init bootstrap record");

    // Fresh init has no adoption semantics. Prove the complete selected
    // namespace clean before preparing either immutable publication.
    require_path_absent_for_fresh_bootstrap_or_throw(
        deployment.manifest_path,
        "anonsync_replica init deployment manifest");
    const fs::path record_path =
        anonsync::sync_replica_bootstrap_record_path_or_throw(
            deployment.manifest_path,
            "anonsync_replica init bootstrap record");
    require_path_absent_for_fresh_bootstrap_or_throw(
        record_path, "anonsync_replica init bootstrap record");
    require_fresh_database_family_or_throw(
        deployment.replica_db,
        "anonsync_replica init replica database");
    if (deployment.effect_db.has_value()) {
        require_fresh_database_family_or_throw(
            *deployment.effect_db,
            "anonsync_replica init effect database");
    }
    if (deployment.membership_db.has_value()) {
        require_fresh_database_family_or_throw(
            *deployment.membership_db,
            "anonsync_replica init membership database");
        require_fresh_database_family_or_throw(
            *deployment.anchor_db,
            "anonsync_replica init membership anchor database");
    }
    if (deployment.payload_root.has_value()) {
        require_empty_directory_for_fresh_bootstrap_or_throw(
            *deployment.payload_root,
            "anonsync_replica init payload root");
    }
    if (deployment.files_root.has_value()) {
        require_empty_directory_for_fresh_bootstrap_or_throw(
            *deployment.files_root,
            "anonsync_replica init files root");
    }

    // Prepare the final create-new cutpoint before the first durable mutation.
    // The immutable record is then published first and carries the exact future
    // manifest bytes, making a later restart's authority explicit rather than
    // inferred from path presence or from partially materialized stores.
    const std::string exact_manifest =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            deployment, "anonsync_replica init deployment manifest");
    auto manifest_publication =
        anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
            deployment.manifest_path, exact_manifest,
            "anonsync_replica deployment manifest");
    const anonsync::SyncReplicaBootstrapRecord record =
        anonsync::create_sync_replica_bootstrap_record_or_throw(
            deployment, "anonsync_replica init bootstrap record");
    if (record.deployment != deployment ||
        record.exact_manifest_bytes != exact_manifest) {
        throw std::logic_error(
            "anonsync_replica init bootstrap record readback conflicts with "
            "the prepared deployment");
    }

    const BootstrapResourceInventory inventory =
        inspect_bootstrap_resource_inventory_or_throw(
            deployment, "anonsync_replica init post-record inventory");
    require_fresh_inventory_after_bootstrap_record_or_throw(
        deployment, inventory, "anonsync_replica init");
    create_missing_bootstrap_resources_or_throw(
        deployment, inventory, "anonsync_replica init store creation");
    attest_complete_bootstrap_store_set_or_throw(
        deployment, "anonsync_replica init complete-store attestation");
    anonsync::attest_sync_replica_bootstrap_record_unchanged_or_throw(
        record, "anonsync_replica init pre-commit record attestation");
    manifest_publication.publish_or_throw();
    std::cout << exact_manifest;
    return 0;
}

int command_init_resume(const Options& options) {
    options.require_only({"manifest"});
    const fs::path manifest_path = require_database_path(
        options.one("manifest"), "--manifest");
    const anonsync::SyncReplicaBootstrapRecord record =
        anonsync::read_sync_replica_bootstrap_record_or_throw(
            manifest_path, "anonsync_replica init-resume bootstrap record");
    const anonsync::SyncReplicaDeploymentManifest& deployment =
        record.deployment;

    if (!path_is_absent_or_throw(
            manifest_path,
            "anonsync_replica init-resume deployment manifest")) {
        // A committed deployment is not repaired by creating a missing
        // authority store, initializing role schema, or reconciling membership.
        // Idempotence requires exact final bytes plus a complete identity-bound
        // store set; ordinary operational commands own later role-state work.
        attest_committed_manifest_matches_bootstrap_record_or_throw(
            record, "anonsync_replica init-resume committed deployment");
        (void)attest_complete_bootstrap_store_identities_or_throw(
            deployment,
            "anonsync_replica init-resume committed store-set attestation");
        anonsync::attest_sync_replica_bootstrap_record_unchanged_or_throw(
            record,
            "anonsync_replica init-resume committed record attestation");
        std::cout << record.exact_manifest_bytes;
        return 0;
    }

    // Retain the exact final publication authority before any recovery-time
    // schema initialization or missing-store creation. The record bytes—not
    // observed resource names—select the deployment being resumed.
    auto manifest_publication =
        anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
            deployment.manifest_path, record.exact_manifest_bytes,
            "anonsync_replica init-resume deployment manifest");
    const BootstrapResourceInventory inventory =
        inspect_bootstrap_resource_inventory_or_throw(
            deployment, "anonsync_replica init-resume inventory");

    // Three phases are deliberate: every present resource first proves exact
    // record-selected identity without application-level writes. Rollback-mode
    // candidates are namespace-preflighted before SQLite reads; after the whole
    // set passes, sealed images may be durability-reconciled and promoted to
    // WAL. Role owners then inspect those same retained handles.
    BootstrapExistingSqliteAuthorities existing =
        attest_existing_bootstrap_resource_identities_or_throw(
            deployment, inventory,
            DatabaseOpenDisposition::ExistingBootstrapCandidate,
            "anonsync_replica init-resume identity phase");
    promote_existing_bootstrap_sqlite_authorities_or_throw(
        deployment, existing,
        "anonsync_replica init-resume WAL-promotion phase");
    const BootstrapPresentResourceAttestation present_state =
        attest_existing_bootstrap_role_state_or_throw(
            deployment, inventory, existing,
            "anonsync_replica init-resume role-state phase");
    const std::uint64_t missing = inventory.missing_store_count(deployment);
    if (missing != 0U &&
        !present_state.all_present_resources_are_genesis) {
        throw std::runtime_error(
            "anonsync_replica init-resume refuses to create " +
            std::to_string(missing) +
            " missing store(s) because at least one present resource or the "
            "files root has advanced beyond bootstrap genesis");
    }

    // Bootstrap-candidate handles deliberately retain EXCLUSIVE locking mode
    // across identity, promotion, and role-state proof. Release those exact
    // handles only after the recomposition decision is final, before opening a
    // second operational authority set for complete-store attestation.
    existing = BootstrapExistingSqliteAuthorities{};

    create_missing_bootstrap_resources_or_throw(
        deployment, inventory,
        "anonsync_replica init-resume missing-store creation");
    attest_complete_bootstrap_store_set_or_throw(
        deployment,
        "anonsync_replica init-resume complete-store attestation");
    anonsync::attest_sync_replica_bootstrap_record_unchanged_or_throw(
        record, "anonsync_replica init-resume pre-commit record attestation");
    manifest_publication.publish_or_throw();
    std::cout << record.exact_manifest_bytes;
    return 0;
}

int command_status(const Options& options) {
    options.require_only({"manifest"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "status");

    ProductSqliteDatabaseAuthority replica_database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica status replica database");
    anonsync::SyncReplicaSqliteOwner replica_owner(
        replica_database.db, deployment.folder_id,
        deployment.local_actor, {},
        "anonsync_replica status replica owner");
    const anonsync::SyncReplicaSqliteSnapshot replica =
        replica_owner.snapshot_or_throw();
    const anonsync::SyncReplicaModel model =
        anonsync::SyncReplicaModel::restore_or_throw(
            replica.durable, replica.limits.model);
    const ProductStatusOutboxCounts outbox =
        summarize_outbox_at_high_water_or_throw(
            replica.outbox, replica.outbox_time_high_water_epoch);
    const std::vector<anonsync::SyncReplicaPathView> visible_paths =
        model.visible_paths();
    const std::vector<std::string> causal_heads =
        model.causal_head_operation_ids();
    const std::vector<std::string> missing_predecessors =
        model.missing_predecessor_operation_ids();

    bool payload_present = false;
    std::uint64_t payload_entries = 0U;
    std::uint64_t payload_indexed_bytes = 0U;
    std::uint64_t payload_transient_entries = 0U;
    std::uint64_t payload_transient_bytes = 0U;
    std::string payload_snapshot_digest;
    if (deployment.payload_root.has_value()) {
        anonsync::SyncReplicaFilePayloadStore payload_store(
            anonsync::sync_replica_deployment_identity_or_throw(
                deployment, "anonsync_replica status payload identity"),
            *deployment.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            payload_store_limits(deployment.max_payload_bytes),
            "anonsync_replica status payload store");
        const anonsync::SyncReplicaFilePayloadStoreSnapshot payload =
            payload_store.snapshot_or_throw();
        payload_present = true;
        payload_entries = payload.entry_count();
        payload_indexed_bytes = payload.indexed_bytes();
        payload_transient_entries = payload.transient_entry_count();
        payload_transient_bytes = payload.transient_bytes();
        payload_snapshot_digest = payload.snapshot_digest();
    }

    bool effect_present = false;
    std::uint64_t effect_state_generation = 0U;
    std::uint64_t effect_total = 0U;
    std::uint64_t effect_staged = 0U;
    std::uint64_t effect_published = 0U;
    std::uint64_t effect_retained_payload_bytes = 0U;
    std::string effect_cutpoint_digest;
    if (deployment.effect_db.has_value()) {
        ProductSqliteDatabaseAuthority effect_database =
            open_bound_operational_database_or_throw(
                deployment, *deployment.effect_db,
                anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
                "anonsync_replica status effect database");
        anonsync::SyncReplicaFileEffectSqliteOwner effect_owner(
            effect_database.db, deployment.folder_id,
            *deployment.files_root,
            effect_owner_limits(deployment.max_payload_bytes),
            "anonsync_replica status effect owner");
        const anonsync::SyncReplicaFileEffectSqliteSnapshot effect =
            effect_owner.snapshot_or_throw();
        const ProductStatusEffectCounts effect_counts =
            summarize_effects(effect.effects);
        effect_present = true;
        effect_state_generation = effect.state_generation;
        effect_total = static_cast<std::uint64_t>(effect.effects.size());
        effect_staged = effect_counts.staged;
        effect_published = effect_counts.published;
        effect_retained_payload_bytes = effect.retained_payload_bytes;
        effect_cutpoint_digest = effect.cutpoint_digest;
    }

    bool membership_present = false;
    std::uint64_t membership_state_generation = 0U;
    std::uint64_t membership_policy_epoch = 0U;
    std::uint64_t membership_entry_count = 0U;
    std::string membership_chain_digest;
    std::uint64_t membership_anchor_generation = 0U;
    std::uint64_t membership_anchor_transition_sequence = 0U;
    bool membership_anchor_matches_current = false;
    if (deployment.membership_db.has_value()) {
        ProductSqliteDatabaseAuthority membership_database =
            open_bound_operational_database_or_throw(
                deployment, *deployment.membership_db,
                anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
                "anonsync_replica status membership database");
        ProductSqliteDatabaseAuthority anchor_database =
            open_bound_operational_database_or_throw(
                deployment, *deployment.anchor_db,
                anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
                "anonsync_replica status membership anchor database");
        anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
            membership_database.db, deployment.folder_id,
            deployment.local_actor,
            "anonsync_replica status membership owner");
        anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
            anchor_database.db, deployment.folder_id,
            deployment.local_actor,
            "anonsync_replica status membership anchor owner");
        const auto anchor = anchor_owner.snapshot_or_throw();
        const auto membership = membership_owner.snapshot_or_throw(
            anchor.current_anchor);
        membership_present = true;
        membership_state_generation = membership.state_generation;
        membership_policy_epoch = membership.current_policy_epoch;
        membership_entry_count = membership.current_entry_count;
        membership_chain_digest = membership.current_chain_digest;
        membership_anchor_generation = anchor.current_anchor.state_generation;
        membership_anchor_transition_sequence = anchor.transition_sequence;
        membership_anchor_matches_current =
            anchor.current_anchor == membership.anchor();
    }

    std::cout << "{\"command\":\"status\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"replica_state_generation\":" << replica.state_generation
        << ",\"replica_policy_generation\":" << replica.policy_generation
        << ",\"replica_evidence_operations\":" << model.evidence_count()
        << ",\"replica_active_operations\":" << model.operation_count()
        << ",\"replica_pending_operations\":" << model.pending_operation_count()
        << ",\"replica_quarantined_operations\":" << model.quarantined_operation_count()
        << ",\"replica_visible_paths\":" << visible_paths.size()
        << ",\"replica_causal_heads\":" << causal_heads.size()
        << ",\"replica_missing_predecessors\":" << missing_predecessors.size()
        << ",\"replica_local_counter\":" << model.last_local_counter()
        << ",\"replica_local_actor_compromised\":"
        << json_bool(model.local_actor_compromised())
        << ",\"replica_retained_canonical_bytes\":"
        << model.retained_canonical_bytes()
        << ",\"replica_outbox_intents\":" << outbox.intents
        << ",\"replica_outbox_unclaimed\":" << outbox.unclaimed
        << ",\"replica_outbox_claimable_at_high_water\":"
        << outbox.claimable_at_high_water
        << ",\"replica_outbox_claimed_live_at_high_water\":"
        << outbox.claimed_live_at_high_water
        << ",\"replica_outbox_expired_at_high_water\":"
        << outbox.expired_at_high_water
        << ",\"replica_outbox_retry_waiting_at_high_water\":"
        << outbox.retry_waiting_at_high_water
        << ",\"replica_outbox_dispatch_attempts\":"
        << outbox.dispatch_attempts
        << ",\"replica_outbox_time_high_water_epoch\":"
        << replica.outbox_time_high_water_epoch
        << ",\"replica_outbox_clock_health\":"
        << json_quote(outbox_clock_health_name(
               replica.outbox_clock_state.health))
        << ",\"replica_outbox_clock_anomaly\":"
        << json_quote(anonsync::sync_replica_outbox_clock_anomaly_name(
               replica.outbox_clock_state.anomaly))
        << ",\"replica_outbox_clock_observation_generation\":"
        << replica.outbox_clock_state.observation_generation
        << ",\"replica_outbox_clock_recovery_generation\":"
        << replica.outbox_clock_state.recovery_generation
        << ",\"replica_operation_set_digest\":"
        << json_quote(replica.operation_set_digest)
        << ",\"replica_evidence_set_digest\":"
        << json_quote(replica.evidence_set_digest)
        << ",\"replica_visible_state_digest\":"
        << json_quote(replica.visible_state_digest)
        << ",\"replica_cutpoint_digest\":"
        << json_quote(replica.cutpoint_digest)
        << ",\"payload_status_present\":" << json_bool(payload_present)
        << ",\"payload_entries\":" << payload_entries
        << ",\"payload_indexed_bytes\":" << payload_indexed_bytes
        << ",\"payload_transient_entries\":" << payload_transient_entries
        << ",\"payload_transient_bytes\":" << payload_transient_bytes
        << ",\"payload_snapshot_digest\":"
        << json_quote(payload_snapshot_digest)
        << ",\"effect_status_present\":" << json_bool(effect_present)
        << ",\"effect_state_generation\":" << effect_state_generation
        << ",\"effect_total\":" << effect_total
        << ",\"effect_staged\":" << effect_staged
        << ",\"effect_published\":" << effect_published
        << ",\"effect_retained_payload_bytes\":"
        << effect_retained_payload_bytes
        << ",\"effect_cutpoint_digest\":"
        << json_quote(effect_cutpoint_digest)
        << ",\"membership_status_present\":"
        << json_bool(membership_present)
        << ",\"membership_state_generation\":"
        << membership_state_generation
        << ",\"membership_policy_epoch\":" << membership_policy_epoch
        << ",\"membership_entry_count\":" << membership_entry_count
        << ",\"membership_chain_digest\":"
        << json_quote(membership_chain_digest)
        << ",\"membership_anchor_generation\":"
        << membership_anchor_generation
        << ",\"membership_anchor_transition_sequence\":"
        << membership_anchor_transition_sequence
        << ",\"membership_anchor_matches_current\":"
        << json_bool(membership_anchor_matches_current)
        << "}\n";
    return 0;
}

int command_clock_observe(const Options& options) {
    options.require_only({
        "manifest", "operator-clock-authority-id",
        "operator-clock-uncertainty-ns"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "clock-observe");
    const bool operator_trusted_clock =
        options.has("operator-clock-authority-id");
    auto clock_source = outbox_clock_source_from_options(options);

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica clock observation database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica clock observation owner", std::move(clock_source));
    const anonsync::SyncReplicaOutboxClockObservationResult observed =
        owner.observe_outbox_clock_or_throw();

    std::cout << "{\"command\":\"clock-observe\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"clock_profile\":"
        << json_quote(clock_profile_name(operator_trusted_clock))
        << ",\"outcome\":"
        << json_quote(outbox_clock_observation_outcome_name(observed.outcome))
        << ",\"changed\":" << json_bool(observed.changed);
    append_outbox_clock_state_json_fields(std::cout, observed.state);
    std::cout << "}\n";
    return 0;
}

int command_clock_recover(const Options& options) {
    options.require_only({
        "manifest", "expected-observation-generation",
        "operator-clock-authority-id", "operator-clock-uncertainty-ns"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "clock-recover");
    const std::uint64_t expected_generation = parse_uint64(
        options.one("expected-observation-generation"),
        "--expected-observation-generation");
    if (expected_generation == 0U) {
        throw std::invalid_argument(
            "--expected-observation-generation must be nonzero");
    }
    const bool operator_trusted_clock =
        options.has("operator-clock-authority-id");
    auto clock_source = outbox_clock_source_from_options(options);

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica clock recovery database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica clock recovery owner", std::move(clock_source));
    const anonsync::SyncReplicaOutboxClockState recovered =
        owner.recover_outbox_clock_or_throw(expected_generation);

    std::cout << "{\"command\":\"clock-recover\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"clock_profile\":"
        << json_quote(clock_profile_name(operator_trusted_clock))
        << ",\"expected_observation_generation\":"
        << expected_generation;
    append_outbox_clock_state_json_fields(std::cout, recovered);
    std::cout << "}\n";
    return 0;
}

int command_enqueue_file(const Options& options) {
    options.require_only({
        "manifest", "destination-device", "canonical-path", "source-file"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "enqueue-file");
    const fs::path& payload_root =
        require_payload_root(deployment, "enqueue-file");
    const fs::path source_file = require_existing_regular_file(
        options.one("source-file"), "--source-file");
    const auto& destination_values = options.all("destination-device");
    if (destination_values.empty()) {
        throw std::invalid_argument(
            "at least one --destination-device is required");
    }
    std::vector<std::string> destinations = destination_values;
    for (const std::string& destination : destinations) {
        if (!anonsync::sync_id_is_valid(destination)) {
            throw std::invalid_argument(
                "--destination-device contains an invalid sync ID");
        }
    }

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica replica database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica SQLite owner");

    // Prove the exact replica identity before spending payload-directory
    // mutation authority. A mistyped or wrong-role database must not leave an
    // unreferenced content object in an otherwise valid payload store.
    std::string payload =
        anonsync::read_sync_bounded_regular_file_no_symlink_or_throw(
            source_file, deployment.max_payload_bytes,
            "anonsync_replica source payload");
    anonsync::SyncReplicaFilePayloadStore payload_store(
        anonsync::sync_replica_deployment_identity_or_throw(
            deployment, "anonsync_replica enqueue payload identity"),
        payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        payload_store_limits(deployment.max_payload_bytes),
        "anonsync_replica payload store");
    const auto put = payload_store.put_payload_or_throw(std::move(payload));

    const anonsync::SyncReplicaOperation operation =
        owner.create_local_file_or_throw(
            options.one("canonical-path"), put.size_bytes,
            put.content_sha256, destinations);

    std::cout
        << "{\"command\":\"enqueue-file\",\"operation_id\":"
        << json_quote(operation.operation_id)
        << ",\"folder_id\":" << json_quote(operation.folder_id)
        << ",\"canonical_path\":" << json_quote(operation.canonical_path)
        << ",\"content_sha256\":" << json_quote(operation.content_sha256)
        << ",\"size_bytes\":" << operation.size_bytes
        << ",\"destinations\":" << destinations.size();
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"payload_store_disposition\":"
        << json_quote(payload_put_name(put.disposition)) << "}\n";
    return 0;
}

int command_membership_publish(const Options& options) {
    options.require_only({"manifest", "policy-epoch", "peer"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(
            options, "membership-publish");
    require_membership_store(deployment, "membership-publish");
    const std::uint64_t policy_epoch = parse_uint64(
        options.one("policy-epoch"), "--policy-epoch");
    if (policy_epoch == 0U) {
        throw std::invalid_argument("--policy-epoch must be nonzero");
    }
    std::vector<anonsync::SyncReplicaTlsMembershipEntry> entries;
    entries.reserve(options.all("peer").size());
    for (const std::string& peer : options.all("peer")) {
        entries.push_back(parse_peer_entry(peer));
    }

    ProductSqliteDatabaseAuthority membership_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            "anonsync_replica membership database");
    ProductSqliteDatabaseAuthority anchor_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            "anonsync_replica membership anchor database");
    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, deployment.folder_id,
        deployment.local_actor,
        "anonsync_replica membership owner");
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.db, deployment.folder_id,
        deployment.local_actor,
        "anonsync_replica membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner coordinator(
        membership_owner, anchor_owner,
        "anonsync_replica anchored membership coordinator");
    // Explicit init leaves a durable generation-zero membership/anchor pair
    // without published peer authority. Reconciliation exposes that exact
    // chain cutpoint without manufacturing authorization, so this operational
    // command supports both the first and subsequent CAS publications.
    const auto reconciled = coordinator.reconcile_or_throw();
    const auto published = coordinator.publish_or_throw(
        reconciled.target, policy_epoch, std::move(entries));

    std::cout
        << "{\"command\":\"membership-publish\",\"state_generation\":"
        << published.state_generation()
        << ",\"policy_epoch\":" << published.snapshot().policy_epoch()
        << ",\"entry_count\":" << published.snapshot().entry_count()
        << ",\"snapshot_digest\":"
        << json_quote(published.snapshot().snapshot_digest())
        << ",\"chain_digest\":" << json_quote(published.chain_digest())
        << ",\"durable_anchor_generation\":"
        << published.durable_anchor().state_generation
        << ",\"durable_anchor_chain_digest\":"
        << json_quote(published.durable_anchor().chain_digest);
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout << "}\n";
    return 0;
}

int command_send_one(const Options& options) {
    options.require_only({
        "manifest", "remote-device", "remote-epoch", "remote-spki",
        "address", "port", "certificate", "private-key", "ca-file",
        "worker", "lease-seconds", "timeout-seconds",
        "operator-clock-authority-id", "operator-clock-uncertainty-ns"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "send-one");
    const fs::path& payload_root = require_payload_root(deployment, "send-one");
    const fs::path certificate = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    const fs::path private_key = require_existing_regular_file(
        options.one("private-key"), "--private-key");
    const fs::path ca_file = require_existing_regular_file(
        options.one("ca-file"), "--ca-file");
    const anonsync::SyncReplicaActor remote_actor = actor_from_options(
        options, "remote-device", "remote-epoch", "remote");
    const std::string remote_spki = options.one("remote-spki");
    if (!anonsync::is_lowercase_sha256_hex(remote_spki)) {
        throw std::invalid_argument(
            "--remote-spki must be lowercase SHA-256");
    }
    const std::uint16_t port = parse_port(options.one("port"), "--port");
    const std::uint64_t lease_seconds = option_uint64_or(
        options, "lease-seconds", kDefaultLeaseSeconds);
    const std::uint64_t timeout_seconds = timeout_from_options(options);
    const std::string worker =
        options.one_or("worker", "anonsync-replica-worker");
    const bool operator_trusted_clock =
        options.has("operator-clock-authority-id");
    auto clock_source = outbox_clock_source_from_options(options);

    ProductSqliteDatabaseAuthority database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica sender database");
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, deployment.folder_id, deployment.local_actor, {},
        "anonsync_replica sender owner", std::move(clock_source));
    anonsync::SyncReplicaFileDeliveryService service(
        owner, nullptr, file_service_limits(deployment.max_payload_bytes),
        "anonsync_replica sender service");
    anonsync::SyncReplicaFilePayloadStore payload_store(
        anonsync::sync_replica_deployment_identity_or_throw(
            deployment, "anonsync_replica sender payload identity"),
        payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        payload_store_limits(deployment.max_payload_bytes),
        "anonsync_replica sender payload store");
    auto payload_snapshot = payload_store.snapshot_or_throw();
    SslContextOwner context = load_tls_context_or_throw(
        certificate, private_key, ca_file, false,
        "anonsync_replica client TLS context");
    const StagedDeadlines staged = staged_deadlines(timeout_seconds);
    const auto result =
        anonsync::send_one_sync_replica_file_delivery_tls_session_or_throw(
            service, payload_snapshot,
            anonsync::retain_sync_replica_file_tls_client_context_or_throw(
                context.get(), "anonsync_replica retained client context"),
            {options.one("address"), port},
            {remote_actor, remote_spki}, worker, lease_seconds,
            {staged.first, staged.second, staged.third,
             staged.fourth, staged.fifth},
            "anonsync_replica send-one session");

    std::cout << "{\"command\":\"send-one\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"clock_profile\":"
        << json_quote(clock_profile_name(operator_trusted_clock))
        << ",\"disposition\":"
        << json_quote(anonsync::sync_replica_file_tls_client_disposition_name(
               result.disposition))
        << ",\"shutdown_disposition\":"
        << json_quote(
               anonsync::
                   sync_replica_file_tls_client_shutdown_disposition_name(
                       result.shutdown_disposition))
        << ",\"connected\":" << (result.connected ? "true" : "false")
        << ",\"handshake_complete\":"
        << (result.handshake_complete ? "true" : "false")
        << ",\"peer_authenticated\":"
        << (result.peer_authenticated ? "true" : "false")
        << ",\"connect_attempts\":" << result.connect_attempts
        << ",\"handshake_attempts\":" << result.handshake_attempts
        << ",\"request_frame_bytes\":" << result.request_frame_bytes
        << ",\"request_body_bytes_written\":"
        << result.request_body_bytes_written
        << ",\"receipt_frame_bytes\":" << result.receipt_frame_bytes;
    if (result.operation_id.has_value()) {
        std::cout << ",\"operation_id\":"
                  << json_quote(*result.operation_id);
    }
    if (result.claim_id.has_value()) {
        std::cout << ",\"claim_id\":" << json_quote(*result.claim_id);
    }
    if (result.peer_spki_sha256.has_value()) {
        std::cout << ",\"peer_spki_sha256\":"
                  << json_quote(*result.peer_spki_sha256);
    }
    if (result.receipt_apply_result.has_value()) {
        std::cout << ",\"receipt_apply_result\":"
                  << json_quote(receipt_apply_name(
                         *result.receipt_apply_result));
    }
    if (result.connect_error.has_value()) {
        std::cout << ",\"connect_error\":" << *result.connect_error;
    }
    std::cout << "}\n";

    if (result.disposition ==
        anonsync::SyncReplicaFileTlsClientDisposition::NoReadyDelivery) {
        return 0;
    }
    return result.disposition ==
                   anonsync::SyncReplicaFileTlsClientDisposition::
                       ReceiptApplied &&
               result.receipt_apply_result == anonsync::
                   SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled
        ? 0
        : 2;
}

int command_serve_one(const Options& options) {
    options.require_only({
        "manifest", "bind-address", "port", "certificate", "private-key",
        "ca-file", "timeout-seconds"});
    const anonsync::SyncReplicaDeploymentManifest deployment =
        load_operational_deployment_manifest_or_throw(options, "serve-one");
    require_effect_store(deployment, "serve-one");
    require_membership_store(deployment, "serve-one");
    const fs::path certificate = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    const fs::path private_key = require_existing_regular_file(
        options.one("private-key"), "--private-key");
    const fs::path ca_file = require_existing_regular_file(
        options.one("ca-file"), "--ca-file");
    const std::uint16_t port = parse_port(options.one("port"), "--port");
    const std::uint64_t timeout_seconds = timeout_from_options(options);

#ifndef __linux__
    (void)certificate;
    (void)private_key;
    (void)ca_file;
    (void)port;
    (void)timeout_seconds;
    throw std::runtime_error("serve-one requires Linux");
#else
    // Prove every prerequisite without bootstrap authority. A bad TLS
    // identity, occupied listener, or any selected-store typo must not leave a
    // new database family or authorize a different receiver/effect pair.
    SslContextOwner context = load_tls_context_or_throw(
        certificate, private_key, ca_file, true,
        "anonsync_replica server TLS context");
    ListenerSocket listener_socket = make_listener_or_throw(
        options.one("bind-address"), port,
        "anonsync_replica listener");
    auto listener =
        anonsync::observe_sync_replica_file_tls_server_listener_or_throw(
            listener_socket.descriptor.get(),
            "anonsync_replica listener capability");
    ProductSqliteDatabaseAuthority membership_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.membership_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership,
            "anonsync_replica membership database");
    ProductSqliteDatabaseAuthority anchor_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.anchor_db,
            anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            "anonsync_replica membership anchor database");

    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, deployment.folder_id,
        deployment.local_actor,
        "anonsync_replica membership owner");
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.db, deployment.folder_id,
        deployment.local_actor,
        "anonsync_replica membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner coordinator(
        membership_owner, anchor_owner,
        "anonsync_replica anchored membership coordinator");
    auto membership = coordinator.current_authority_or_throw();

    ProductSqliteDatabaseAuthority replica_database =
        open_bound_operational_database_or_throw(
            deployment, deployment.replica_db,
            anonsync::SyncReplicaSqliteDeploymentRole::Replica,
            "anonsync_replica receiver database");
    ProductSqliteDatabaseAuthority effect_database =
        open_bound_operational_database_or_throw(
            deployment, *deployment.effect_db,
            anonsync::SyncReplicaSqliteDeploymentRole::FileEffect,
            "anonsync_replica effect database");
    anonsync::SyncReplicaSqliteOwner owner(
        replica_database.db, deployment.folder_id,
        deployment.local_actor, {},
        "anonsync_replica receiver owner");
    anonsync::SyncReplicaFileEffectSqliteOwner effect_owner(
        effect_database.db, deployment.folder_id,
        *deployment.files_root,
        effect_owner_limits(deployment.max_payload_bytes),
        "anonsync_replica receiver effect owner");
    anonsync::SyncReplicaFileDeliveryService service(
        owner, &effect_owner, file_service_limits(deployment.max_payload_bytes),
        "anonsync_replica receiver service");
    const StagedDeadlines staged = staged_deadlines(timeout_seconds);
    const auto result =
        anonsync::serve_one_sync_replica_file_delivery_tls_session_or_throw(
            service, listener,
            anonsync::retain_sync_replica_file_tls_server_context_or_throw(
                context.get(), "anonsync_replica retained server context"),
            std::move(membership),
            {staged.first, staged.second, staged.third,
             staged.fourth, staged.fifth},
            "anonsync_replica serve-one session");

    std::cout << "{\"command\":\"serve-one\"";
    append_deployment_authority_json_fields(std::cout, deployment);
    std::cout
        << ",\"disposition\":"
        << json_quote(server_disposition_name(result.disposition))
        << ",\"shutdown_disposition\":"
        << json_quote(server_shutdown_name(result.shutdown_disposition))
        << ",\"accepted\":" << (result.accepted ? "true" : "false")
        << ",\"handshake_complete\":"
        << (result.handshake_complete ? "true" : "false")
        << ",\"accept_attempts\":" << result.accept_attempts
        << ",\"handshake_attempts\":" << result.handshake_attempts
        << ",\"membership_state_generation\":"
        << result.membership_state_generation
        << ",\"membership_policy_epoch\":"
        << result.membership_policy_epoch;
    if (result.peer_spki_sha256.has_value()) {
        std::cout << ",\"peer_spki_sha256\":"
                  << json_quote(*result.peer_spki_sha256);
    }
    if (result.peer_actor.has_value()) {
        std::cout << ",\"peer_device_id\":"
                  << json_quote(result.peer_actor->device_id)
                  << ",\"peer_epoch\":" << result.peer_actor->epoch;
    }
    if (result.receive.has_value()) {
        std::cout << ",\"receive_disposition\":"
                  << json_quote(receive_disposition_name(
                         result.receive->disposition))
                  << ",\"request_frame_bytes\":"
                  << result.receive->request_frame_bytes
                  << ",\"receipt_frame_bytes\":"
                  << result.receive->receipt_frame_bytes;
        if (result.receive->inbound.has_value()) {
            std::cout << ",\"receipt_disposition\":"
                      << json_quote(file_receipt_disposition_name(
                             result.receive->inbound->receipt.disposition))
                      << ",\"operation_id\":"
                      << json_quote(
                             result.receive->inbound->request.evidence_request
                                 .operation.operation_id);
        }
    }
    std::cout << "}\n";

    return result.disposition ==
                   anonsync::SyncReplicaFileTlsServerDisposition::ReceiptSent ||
               result.disposition == anonsync::
                   SyncReplicaFileTlsServerDisposition::AcceptDeadlineExpired
        ? 0
        : 2;
#endif
}

int command_certificate_spki(const Options& options) {
    options.require_only({"certificate"});
    const fs::path certificate_path = require_existing_regular_file(
        options.one("certificate"), "--certificate");
    ERR_clear_error();
    BioOwner input(
        BIO_new_file(certificate_path.string().c_str(), "rb"), BIO_free);
    if (!input) throw_openssl("could not open certificate");
    CertificateOwner certificate(
        PEM_read_bio_X509(input.get(), nullptr, nullptr, nullptr), X509_free);
    if (!certificate) throw_openssl("could not parse PEM certificate");
    X509_PUBKEY* public_key = X509_get_X509_PUBKEY(certificate.get());
    if (public_key == nullptr) {
        throw std::runtime_error("certificate has no SubjectPublicKeyInfo");
    }
    const int encoded_bytes = i2d_X509_PUBKEY(public_key, nullptr);
    if (encoded_bytes <= 0) {
        throw_openssl("could not size certificate SubjectPublicKeyInfo");
    }
    std::string encoded(static_cast<std::size_t>(encoded_bytes), '\0');
    unsigned char* output =
        reinterpret_cast<unsigned char*>(encoded.data());
    if (i2d_X509_PUBKEY(public_key, &output) != encoded_bytes) {
        throw_openssl("could not encode certificate SubjectPublicKeyInfo");
    }
    std::cout
        << "{\"command\":\"certificate-spki\",\"spki_sha256\":"
        << json_quote(anonsync::sha256_hex(encoded)) << "}\n";
    return 0;
}

void print_usage(std::ostream& output) {
    output <<
        "AnonSync bounded causal replica product spine\n\n"
        "Commands:\n"
        "  anonsync_replica init --manifest ABSOLUTE_JSON "
        "--replica-db ABSOLUTE_DB --folder ID --local-device ID "
        "--local-epoch N [--max-payload-bytes N] "
        "[--payload-root ABSOLUTE_DIR] "
        "[--effect-db ABSOLUTE_DB --files-root ABSOLUTE_DIR] "
        "[--membership-db ABSOLUTE_DB --anchor-db ABSOLUTE_DB]\n"
        "  anonsync_replica init-resume --manifest ABSOLUTE_JSON\n"
        "  anonsync_replica certificate-spki --certificate ABSOLUTE_PEM\n"
        "  anonsync_replica status --manifest ABSOLUTE_JSON\n"
        "  anonsync_replica clock-observe --manifest ABSOLUTE_JSON "
        "[--operator-clock-authority-id ID "
        "--operator-clock-uncertainty-ns N]\n"
        "  anonsync_replica clock-recover --manifest ABSOLUTE_JSON "
        "--expected-observation-generation N "
        "[--operator-clock-authority-id ID "
        "--operator-clock-uncertainty-ns N]\n"
        "  anonsync_replica enqueue-file --manifest ABSOLUTE_JSON "
        "--destination-device ID [--destination-device ID...] "
        "--canonical-path PATH --source-file ABSOLUTE_FILE\n"
        "  anonsync_replica membership-publish --manifest ABSOLUTE_JSON "
        "--policy-epoch N [--peer DEVICE:EPOCH:SPKI_SHA256 ...]\n"
        "  anonsync_replica send-one --manifest ABSOLUTE_JSON "
        "--remote-device ID --remote-epoch N --remote-spki SHA256 "
        "--address NUMERIC_IP --port N --certificate ABSOLUTE_PEM "
        "--private-key ABSOLUTE_PEM --ca-file ABSOLUTE_PEM "
        "[--worker ID] [--lease-seconds N] [--timeout-seconds N] "
        "[--operator-clock-authority-id ID "
        "--operator-clock-uncertainty-ns N]\n"
        "  anonsync_replica serve-one --manifest ABSOLUTE_JSON "
        "--bind-address NUMERIC_IP --port N "
        "--certificate ABSOLUTE_PEM --private-key ABSOLUTE_PEM "
        "--ca-file ABSOLUTE_PEM [--timeout-seconds N]\n\n"
        "All paths must be absolute. init is the sole fresh product-spine "
        "bootstrap authority: it proves a clean namespace, durably publishes "
        "an immutable record containing the exact future manifest, initializes "
        "the selected stores, and publishes the manifest last. init-resume can "
        "only resume that exact recorded deployment after two-phase identity "
        "and role-state attestation; it never adopts path-selected stores. The "
        "selected resources are individually durable but are not one "
        "cross-resource atomic transaction. Absence of the manifest means the "
        "deployment has not reached its committed operational cutpoint. Every "
        "operational "
        "command loads one bounded, no-symlink, canonical, self-digested "
        "manifest before opening a store and derives every store path, local "
        "identity, folder, and payload ceiling from it. Missing, copied, "
        "tampered, noncanonical, or policy-incompatible manifests fail closed. "
        "Operational database and payload opens are existing-only and cannot "
        "mint a database, payload identity marker, or alternate store set. "
        "status emits a bounded attested condition report. clock-observe "
        "samples and publishes clock health without claiming work; "
        "clock-recover requires the exact current quarantine generation. "
        "send-one and serve-one each own exactly one bounded TLS conversation "
        "and are intentionally not a background daemon. send-one defaults to "
        "the fail-closed kernel clock source; paired operator-clock options are "
        "an explicit deployment assertion for externally owned synchronization "
        "evidence. JSON is written to stdout and diagnostics to stderr.\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 2 || std::string_view(argv[1]) == "--help" ||
            std::string_view(argv[1]) == "help") {
            print_usage(std::cout);
            return argc < 2 ? 2 : 0;
        }
        const std::string command = argv[1];
        const Options options(argc, argv, 2);
        if (command == "init") {
            return command_init(options);
        }
        if (command == "init-resume") {
            return command_init_resume(options);
        }
        if (command == "status") {
            return command_status(options);
        }
        if (command == "clock-observe") {
            return command_clock_observe(options);
        }
        if (command == "clock-recover") {
            return command_clock_recover(options);
        }
        if (command == "enqueue-file") {
            return command_enqueue_file(options);
        }
        if (command == "membership-publish") {
            return command_membership_publish(options);
        }
        if (command == "send-one") {
            return command_send_one(options);
        }
        if (command == "serve-one") {
            return command_serve_one(options);
        }
        if (command == "certificate-spki") {
            return command_certificate_spki(options);
        }
        throw std::invalid_argument("unknown command: " + command);
    } catch (const std::exception& error) {
        std::cerr << "anonsync_replica: " << error.what() << '\n';
        return 1;
    }
}
