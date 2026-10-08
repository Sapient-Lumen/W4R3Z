#include "persistence/peer_ingress_connection_profile.hpp"

#include <sqlite3.h>

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <string>
#include <utility>

namespace {

int checks = 0;

bool check(bool condition, const char* expression, int line) {
    ++checks;
    if (!condition) {
        std::cerr << "check failed at line " << line << ": "
                  << expression << '\n';
        return false;
    }
    return true;
}

#define CHECK(expr) \
    do { \
        if (!check((expr), #expr, __LINE__)) return 1; \
    } while (false)

std::filesystem::path unique_database_path(const std::string& label) {
    static std::uint64_t sequence = 0;
    const auto ticks = std::chrono::steady_clock::now()
                           .time_since_epoch()
                           .count();
    ++sequence;
    return std::filesystem::temp_directory_path() /
        ("anonsync-rev0788-" + label + "-" + std::to_string(ticks) +
         "-" + std::to_string(sequence) + ".sqlite");
}

void remove_database_family(const std::filesystem::path& path) noexcept {
    std::error_code ignored;
    std::filesystem::remove(path, ignored);
    std::filesystem::remove(path.string() + "-wal", ignored);
    std::filesystem::remove(path.string() + "-shm", ignored);
    std::filesystem::remove(path.string() + "-journal", ignored);
}

int primary_code(int result) noexcept {
    return result & 0xff;
}

class RegisteredAliasVfs final {
public:
    explicit RegisteredAliasVfs(std::string name)
        : name_(std::move(name)) {
        sqlite3_vfs* const base = sqlite3_vfs_find(nullptr);
        if (base == nullptr) {
            return;
        }
        alias_ = *base;
        alias_.zName = name_.c_str();
        alias_.pNext = nullptr;
        registered_ = sqlite3_vfs_register(&alias_, 0) == SQLITE_OK;
    }

    ~RegisteredAliasVfs() {
        if (registered_) {
            (void)sqlite3_vfs_unregister(&alias_);
        }
    }

    RegisteredAliasVfs(const RegisteredAliasVfs&) = delete;
    RegisteredAliasVfs& operator=(const RegisteredAliasVfs&) = delete;

    [[nodiscard]] bool registered() const noexcept { return registered_; }
    [[nodiscard]] const char* name() const noexcept { return name_.c_str(); }

private:
    std::string name_;
    sqlite3_vfs alias_{};
    bool registered_{false};
};

}  // namespace

int main() {
    using anonsync::persistence::SqliteConnectionEvidence;
    using anonsync::persistence::open_verified_sqlite_database;

    const int writable_flags =
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
    const int readonly_flags =
        SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;

    const std::filesystem::path path = unique_database_path("main");
    const std::filesystem::path mode_text_path =
        unique_database_path("literal-mode=memory");
    const std::filesystem::path alias_path = unique_database_path("alias");
    remove_database_family(path);
    remove_database_family(mode_text_path);
    remove_database_family(alias_path);

    sqlite3* database = reinterpret_cast<sqlite3*>(
        static_cast<std::uintptr_t>(1));
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), nullptr, writable_flags, nullptr) ==
          SQLITE_MISUSE);

    SqliteConnectionEvidence rejected_evidence;
    rejected_evidence.requested_flags = 99;
    rejected_evidence.pinned_vfs_name = "stale";
    CHECK(open_verified_sqlite_database(
              nullptr, &database, writable_flags, nullptr,
              &rejected_evidence) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(rejected_evidence.requested_flags == 0);
    CHECK(rejected_evidence.pinned_vfs_name.empty());

    CHECK(open_verified_sqlite_database(
              "", &database, writable_flags, nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              ":memory:", &database, writable_flags, nullptr) ==
          SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              ":future-special", &database, writable_flags, nullptr) ==
          SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              "file:authority.sqlite?mode=memory", &database,
              writable_flags, nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              "FILE:authority.sqlite?nolock=1", &database,
              writable_flags, nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);

    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              SQLITE_OPEN_READONLY | SQLITE_OPEN_READWRITE |
                  SQLITE_OPEN_FULLMUTEX,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              SQLITE_OPEN_READONLY | SQLITE_OPEN_CREATE |
                  SQLITE_OPEN_FULLMUTEX,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              writable_flags | SQLITE_OPEN_NOMUTEX,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              writable_flags | SQLITE_OPEN_URI,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              writable_flags | SQLITE_OPEN_MEMORY,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              writable_flags | SQLITE_OPEN_SHAREDCACHE,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database,
              writable_flags | SQLITE_OPEN_DELETEONCLOSE,
              nullptr) == SQLITE_MISUSE);
    CHECK(database == nullptr);
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database, writable_flags,
              "missing-anonsync-vfs") == SQLITE_CANTOPEN);
    CHECK(database == nullptr);

    SqliteConnectionEvidence writable_evidence;
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database, writable_flags,
              nullptr, &writable_evidence) == SQLITE_OK);
    CHECK(database != nullptr);
    CHECK(writable_evidence.requested_flags == writable_flags);
    CHECK((writable_evidence.effective_flags &
           SQLITE_OPEN_PRIVATECACHE) != 0);
    CHECK(!writable_evidence.requested_vfs_was_explicit);
    CHECK(writable_evidence.file_backing_verified);
    CHECK(writable_evidence.access_mode_verified);
    CHECK(writable_evidence.serialized_mutex_verified);
    CHECK(writable_evidence.vfs_identity_verified);
    CHECK(writable_evidence.observed_read_only == 0);
    CHECK(!writable_evidence.pinned_vfs_name.empty());
    CHECK(!writable_evidence.observed_main_filename.empty());
    CHECK(std::filesystem::path(
              writable_evidence.observed_main_filename).is_absolute());
    CHECK(sqlite3_db_mutex(database) != nullptr);
    if (writable_evidence.vfs_name_diagnostic_available) {
        CHECK(!writable_evidence.observed_vfs_stack.empty());
    }
    CHECK(sqlite3_exec(database,
                       "CREATE TABLE authority(value INTEGER);",
                       nullptr, nullptr, nullptr) == SQLITE_OK);
    CHECK(sqlite3_close(database) == SQLITE_OK);
    database = nullptr;
    CHECK(std::filesystem::is_regular_file(path));

    // A literal ordinary filename containing mode=memory is still durable. The
    // rev0787 substring classifier incorrectly treated this as in-memory.
    CHECK(open_verified_sqlite_database(
              mode_text_path.string().c_str(), &database, writable_flags,
              nullptr) == SQLITE_OK);
    CHECK(database != nullptr);
    CHECK(sqlite3_close(database) == SQLITE_OK);
    database = nullptr;
    CHECK(std::filesystem::is_regular_file(mode_text_path));

    SqliteConnectionEvidence readonly_evidence;
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database, readonly_flags,
              nullptr, &readonly_evidence) == SQLITE_OK);
    CHECK(database != nullptr);
    CHECK(readonly_evidence.observed_read_only == 1);
    CHECK(readonly_evidence.file_backing_verified);
    CHECK(readonly_evidence.serialized_mutex_verified);
    CHECK(readonly_evidence.vfs_identity_verified);
    CHECK(primary_code(sqlite3_exec(
              database, "INSERT INTO authority VALUES(1);",
              nullptr, nullptr, nullptr)) == SQLITE_READONLY);
    CHECK(sqlite3_close(database) == SQLITE_OK);
    database = nullptr;

    sqlite3_vfs* const default_vfs = sqlite3_vfs_find(nullptr);
    CHECK(default_vfs != nullptr);
    CHECK(default_vfs->zName != nullptr);
    SqliteConnectionEvidence explicit_default_evidence;
    CHECK(open_verified_sqlite_database(
              path.string().c_str(), &database, readonly_flags,
              default_vfs->zName, &explicit_default_evidence) == SQLITE_OK);
    CHECK(database != nullptr);
    CHECK(explicit_default_evidence.requested_vfs_was_explicit);
    CHECK(explicit_default_evidence.vfs_identity_verified);
    CHECK(explicit_default_evidence.pinned_vfs_name == default_vfs->zName);
    CHECK(sqlite3_close(database) == SQLITE_OK);
    database = nullptr;

    RegisteredAliasVfs alias("anonsync-rev0788-alias-vfs");
    CHECK(alias.registered());
    SqliteConnectionEvidence alias_evidence;
    CHECK(open_verified_sqlite_database(
              alias_path.string().c_str(), &database, writable_flags,
              alias.name(), &alias_evidence) == SQLITE_OK);
    CHECK(database != nullptr);
    CHECK(alias_evidence.requested_vfs_was_explicit);
    CHECK(alias_evidence.vfs_identity_verified);
    CHECK(alias_evidence.pinned_vfs_name == alias.name());
    CHECK(sqlite3_close(database) == SQLITE_OK);
    database = nullptr;

    const std::filesystem::path missing_parent =
        unique_database_path("missing-parent").parent_path() /
        ("anonsync-rev0788-missing-parent-" +
         std::to_string(std::chrono::steady_clock::now()
                            .time_since_epoch().count())) /
        "db.sqlite";
    SqliteConnectionEvidence failed_open_evidence;
    const int failed_open_result = open_verified_sqlite_database(
        missing_parent.string().c_str(), &database, writable_flags,
        nullptr, &failed_open_evidence);
    CHECK(failed_open_result != SQLITE_OK);
    CHECK(!failed_open_evidence.file_backing_verified);
    CHECK(!failed_open_evidence.access_mode_verified);
    CHECK(!failed_open_evidence.serialized_mutex_verified);
    CHECK(!failed_open_evidence.vfs_identity_verified);
    if (database != nullptr) {
        CHECK(sqlite3_errmsg(database) != nullptr);
        CHECK(sqlite3_close(database) == SQLITE_OK);
        database = nullptr;
    }

    remove_database_family(path);
    remove_database_family(mode_text_path);
    remove_database_family(alias_path);

    std::cout << "peer ingress durable connection profile: "
              << checks << " checks passed\n";
    return 0;
}
