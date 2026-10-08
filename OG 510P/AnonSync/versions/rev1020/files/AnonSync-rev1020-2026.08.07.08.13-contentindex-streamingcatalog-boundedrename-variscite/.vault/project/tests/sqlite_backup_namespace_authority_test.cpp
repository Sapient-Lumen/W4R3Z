#include "anonsync_core_internal.hpp"
#include "persistence/sqlite_snapshot_seal.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <cstdio>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void write_binary(const fs::path& path, const std::string& bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("could not create fixture: " + path.string());
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!output) throw std::runtime_error("could not write fixture: " + path.string());
}

std::string read_binary(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("could not read fixture: " + path.string());
    return std::string(std::istreambuf_iterator<char>(input),
                       std::istreambuf_iterator<char>());
}

std::string sqlite_text_scalar(const fs::path& path, const char* sql) {
    sqlite3* database = nullptr;
    sqlite3_stmt* statement = nullptr;
    try {
        const int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX |
                          SQLITE_OPEN_PRIVATECACHE;
        if (sqlite3_open_v2(path.c_str(), &database, flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(
                database != nullptr ? sqlite3_errmsg(database)
                                    : "could not open SQLite scalar fixture");
        }
        sqlite3_busy_timeout(database, 2000);
        if (sqlite3_prepare_v2(database, sql, -1, &statement, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database));
        }
        if (sqlite3_step(statement) != SQLITE_ROW ||
            sqlite3_column_type(statement, 0) != SQLITE_TEXT) {
            throw std::runtime_error("SQLite scalar fixture returned no exact text row");
        }
        const unsigned char* bytes = sqlite3_column_text(statement, 0);
        const int count = sqlite3_column_bytes(statement, 0);
        if (bytes == nullptr || count < 0) {
            throw std::runtime_error("SQLite scalar fixture returned invalid text bytes");
        }
        std::string value(reinterpret_cast<const char*>(bytes),
                          static_cast<std::size_t>(count));
        if (sqlite3_step(statement) != SQLITE_DONE) {
            throw std::runtime_error("SQLite scalar fixture returned extra rows");
        }
        if (sqlite3_finalize(statement) != SQLITE_OK) {
            statement = nullptr;
            throw std::runtime_error("could not finalize SQLite scalar fixture");
        }
        statement = nullptr;
        if (sqlite3_close_v2(database) != SQLITE_OK) {
            database = nullptr;
            throw std::runtime_error("could not close SQLite scalar fixture");
        }
        database = nullptr;
        return value;
    } catch (...) {
        if (statement != nullptr) (void)sqlite3_finalize(statement);
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw;
    }
}

void replace_ledger_instance_id(const fs::path& path,
                                const std::string& replacement) {
    sqlite3* database = nullptr;
    sqlite3_stmt* statement = nullptr;
    try {
        const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                          SQLITE_OPEN_PRIVATECACHE;
        if (sqlite3_open_v2(path.c_str(), &database, flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(
                database != nullptr ? sqlite3_errmsg(database)
                                    : "could not open identity substitution fixture");
        }
        sqlite3_busy_timeout(database, 2000);
        if (sqlite3_prepare_v2(
                database,
                "UPDATE ledger_identity SET ledger_instance_id=? WHERE id=1;",
                -1, &statement, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database));
        }
        if (sqlite3_bind_text(statement, 1, replacement.data(),
                              static_cast<int>(replacement.size()),
                              SQLITE_TRANSIENT) != SQLITE_OK ||
            sqlite3_step(statement) != SQLITE_DONE) {
            throw std::runtime_error(sqlite3_errmsg(database));
        }
        if (sqlite3_changes(database) != 1) {
            throw std::runtime_error(
                "identity substitution fixture did not update exactly one row");
        }
        if (sqlite3_finalize(statement) != SQLITE_OK) {
            statement = nullptr;
            throw std::runtime_error(
                "could not finalize identity substitution fixture");
        }
        statement = nullptr;
        if (sqlite3_close_v2(database) != SQLITE_OK) {
            database = nullptr;
            throw std::runtime_error(
                "could not close identity substitution fixture");
        }
        database = nullptr;
    } catch (...) {
        if (statement != nullptr) (void)sqlite3_finalize(statement);
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw;
    }
}

void cleanup_sqlite_family(const fs::path& path) {
    for (const std::string_view suffix : {
             "", "-wal", "-shm", "-journal", ".restore.lock", ".write.lock"}) {
        std::error_code ignored;
        fs::remove(fs::path(path.string() + std::string(suffix)), ignored);
    }
}

anonsync::Json make_case(const std::string& case_id) {
    anonsync::Json value;
    value.type = anonsync::Json::Type::Object;
    value.o["case_id"] = anonsync::json_string_value(case_id);
    value.o["kind"] = anonsync::json_string_value("openapi");
    value.o["operation_id"] =
        anonsync::json_string_value("backupNamespaceAuthority");
    value.o["contract_digest_sha256"] =
        anonsync::json_string_value("backup-namespace-authority-contract");
    value.o["cloud_event_source"] = anonsync::json_string_value("");
    value.o["cloud_event_id"] = anonsync::json_string_value("");
    return value;
}

anonsync::Json make_claims(const std::string& jti) {
    anonsync::Json value;
    value.type = anonsync::Json::Type::Object;
    value.o["operation_id"] =
        anonsync::json_string_value("backupNamespaceAuthority");
    value.o["contract_digest_sha256"] = anonsync::json_string_value(
        anonsync::sha256_hex("backup-namespace-authority-contract"));
    value.o["jti"] = anonsync::json_string_value(jti);
    return value;
}

std::uint64_t fnv1a_64(const std::string& value) {
    std::uint64_t digest = 14695981039346656037ULL;
    for (const unsigned char byte : value) {
        digest ^= static_cast<std::uint64_t>(byte);
        digest *= 1099511628211ULL;
    }
    return digest;
}

std::string hex_u64(std::uint64_t value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(16) << value;
    return out.str();
}

fs::path first_atomic_temp_name(const fs::path& destination) {
    return destination.parent_path() /
           (".anonsync-publish-v1-" +
            hex_u64(fnv1a_64(destination.filename().string())) + "-" +
            hex_u64(static_cast<std::uint64_t>(::getpid())) +
            "-0000000000000000.tmp");
}

std::vector<fs::path> atomic_temp_names(const fs::path& root) {
    std::vector<fs::path> out;
    for (const auto& entry : fs::directory_iterator(root)) {
        const std::string name = entry.path().filename().string();
        if (name.rfind(".anonsync-publish-v1-", 0) == 0) {
            out.push_back(entry.path());
        }
    }
    return out;
}

long long sealed_entry_count(const fs::path& snapshot) {
    anonsync::persistence::SealedSqliteSnapshot seal =
        anonsync::persistence::SealedSqliteSnapshot::capture(
            snapshot, "backup namespace authority published snapshot");
    sqlite3* database = seal.open_database_or_throw(
        "backup namespace authority count open");
    sqlite3_stmt* statement = nullptr;
    try {
        if (sqlite3_prepare_v2(database,
                               "SELECT COUNT(*) FROM ledger_entries;",
                               -1, &statement, nullptr) != SQLITE_OK) {
            throw std::runtime_error("could not prepare published snapshot count");
        }
        if (sqlite3_step(statement) != SQLITE_ROW) {
            throw std::runtime_error("could not read published snapshot count");
        }
        const long long count = sqlite3_column_int64(statement, 0);
        if (sqlite3_step(statement) != SQLITE_DONE) {
            throw std::runtime_error("published snapshot count returned extra rows");
        }
        if (sqlite3_finalize(statement) != SQLITE_OK) {
            statement = nullptr;
            throw std::runtime_error("could not finalize published snapshot count");
        }
        statement = nullptr;
        if (sqlite3_close_v2(database) != SQLITE_OK) {
            database = nullptr;
            throw std::runtime_error("could not close published snapshot count database");
        }
        database = nullptr;
        seal.verify_unchanged_or_throw(
            "backup namespace authority post-count seal");
        return count;
    } catch (...) {
        if (statement != nullptr) (void)sqlite3_finalize(statement);
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw;
    }
}

void require_no_snapshot_sidecars(const fs::path& snapshot,
                                  std::uint64_t& checks) {
    require(!fs::exists(fs::path(snapshot.string() + "-wal")) &&
                !fs::exists(fs::path(snapshot.string() + "-shm")) &&
                !fs::exists(fs::path(snapshot.string() + "-journal")),
            "backup manufactured a destination SQLite sidecar", checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const fs::path root = fs::path("/tmp") /
        ("anonsync-r0822-backup-namespace-" +
         std::to_string(static_cast<long long>(::getpid())) + "-" +
         std::to_string(static_cast<long long>(std::time(nullptr))));
    const fs::path ledger = root / "ledger.sqlite";
    const fs::path snapshot = root / "snapshot.sqlite";

    try {
        fs::create_directory(root);
        if (::chmod(root.c_str(), 0700) != 0) {
            throw std::runtime_error("could not make test directory private");
        }

        std::string reason;
        auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
        backend->load(ledger.string(), "batch");
        require(backend->stage(make_case("backup-authority-1"),
                               make_claims("backup-authority-jti-1"),
                               "allow", reason),
                "could not stage first backup fixture: " + reason, checks);
        require(backend->commit(reason),
                "could not commit first backup fixture: " + reason, checks);

        const fs::path foreign_atomic_temp = first_atomic_temp_name(snapshot);
        const std::string foreign_temp_bytes =
            std::string("foreign-publisher-collision\0tail", 32);
        write_binary(foreign_atomic_temp, foreign_temp_bytes);
        const std::string prior_main =
            std::string("prior-snapshot-main\0not-sqlite", 30);
        write_binary(snapshot, prior_main);

        require(backend->backup_snapshot(snapshot.string(), reason),
                "valid backup failed: " + reason, checks);
        require(read_binary(snapshot) != prior_main,
                "backup did not replace the prior regular main entry", checks);
        require(fs::exists(foreign_atomic_temp) &&
                    read_binary(foreign_atomic_temp) == foreign_temp_bytes,
                "backup consumed or changed a foreign publisher collision", checks);
        const std::vector<fs::path> temps_after_first = atomic_temp_names(root);
        require(temps_after_first.size() == 1U &&
                    temps_after_first.front() == foreign_atomic_temp,
                "backup left an owned atomic publication temp", checks);
        require_no_snapshot_sidecars(snapshot, checks);
        require(sealed_entry_count(snapshot) == 1,
                "first published snapshot has the wrong ledger count", checks);
        const std::string first_snapshot_bytes = read_binary(snapshot);
        require(first_snapshot_bytes.size() >= 100U &&
                    static_cast<unsigned char>(first_snapshot_bytes[18]) == 1U &&
                    static_cast<unsigned char>(first_snapshot_bytes[19]) == 1U,
                "published backup is not canonical SQLite file format 1/1", checks);

        require(backend->stage(make_case("backup-authority-2"),
                               make_claims("backup-authority-jti-2"),
                               "allow", reason),
                "source ledger stopped accepting rows after live capture: " + reason,
                checks);
        require(backend->commit(reason),
                "source ledger stopped committing after live capture: " + reason,
                checks);
        require(backend->backup_snapshot(snapshot.string(), reason),
                "second valid backup failed: " + reason, checks);
        require(sealed_entry_count(snapshot) == 2,
                "second published snapshot has the wrong ledger count", checks);
        require_no_snapshot_sidecars(snapshot, checks);
        const std::string current_snapshot_bytes = read_binary(snapshot);

        const std::string original_instance_id = sqlite_text_scalar(
            ledger, "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;");
        require(original_instance_id.size() == 64U,
                "live ledger identity fixture is not a SHA-256-sized token", checks);
        const std::string substituted_instance_id(
            64U, original_instance_id.front() == 'a' ? 'b' : 'a');
        replace_ledger_instance_id(ledger, substituted_instance_id);
        require(sqlite_text_scalar(
                    ledger,
                    "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;") ==
                    substituted_instance_id,
                "identity substitution fixture was not visible to SQLite", checks);

        const fs::path invalid_parent = root / "identity-mismatch-parent";
        const fs::path invalid_destination = invalid_parent / "snapshot.sqlite";
        std::error_code ignored;
        fs::remove_all(invalid_parent, ignored);
        std::string identity_reason;
        require(!backend->backup_snapshot(invalid_destination.string(),
                                          identity_reason),
                "backup accepted a substituted durable ledger identity", checks);
        require(identity_reason.find("identity") != std::string::npos,
                "identity substitution rejection reason mismatch: " +
                    identity_reason,
                checks);
        require(!fs::exists(invalid_parent) && !fs::exists(invalid_destination),
                "invalid source evidence created a destination directory or file",
                checks);

        replace_ledger_instance_id(ledger, original_instance_id);
        require(backend->backup_snapshot(snapshot.string(), reason),
                "backup did not recover after durable identity restoration: " +
                    reason,
                checks);
        require(sealed_entry_count(snapshot) == 2,
                "post-restoration backup has the wrong ledger count", checks);

        for (const std::string_view suffix : {"-wal", "-shm", "-journal"}) {
            write_binary(snapshot, current_snapshot_bytes);
            const fs::path sidecar(snapshot.string() + std::string(suffix));
            const std::string foreign_sidecar =
                "foreign-backup-sidecar:" + std::string(suffix) +
                std::string("\0tail", 5);
            write_binary(sidecar, foreign_sidecar);

            std::string rejected_reason;
            const bool accepted =
                backend->backup_snapshot(snapshot.string(), rejected_reason);
            require(!accepted,
                    "backup accepted an authority-free destination sidecar " +
                        std::string(suffix),
                    checks);
            require(rejected_reason.find("sidecar " + std::string(suffix)) !=
                        std::string::npos,
                    "backup sidecar rejection reason mismatch: " + rejected_reason,
                    checks);
            require(fs::exists(snapshot) &&
                        read_binary(snapshot) == current_snapshot_bytes,
                    "backup changed the prior main file while rejecting " +
                        std::string(suffix),
                    checks);
            require(fs::exists(sidecar) &&
                        read_binary(sidecar) == foreign_sidecar,
                    "backup deleted or changed foreign sidecar " +
                        std::string(suffix),
                    checks);
            const std::vector<fs::path> temps_after_rejection =
                atomic_temp_names(root);
            require(temps_after_rejection.size() == 1U &&
                        temps_after_rejection.front() == foreign_atomic_temp,
                    "sidecar rejection left an owned atomic publication temp", checks);
            std::error_code ignored;
            fs::remove(sidecar, ignored);
        }

        backend->close();
        cleanup_sqlite_family(ledger);
        cleanup_sqlite_family(snapshot);
        fs::remove(foreign_atomic_temp, ignored);
        fs::remove_all(root, ignored);
        std::cout << "anonsync sqlite backup namespace authority test passed="
                  << checks << " failed=0\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << '\n';
        std::error_code ignored;
        fs::remove_all(root, ignored);
        return 2;
    }
}
