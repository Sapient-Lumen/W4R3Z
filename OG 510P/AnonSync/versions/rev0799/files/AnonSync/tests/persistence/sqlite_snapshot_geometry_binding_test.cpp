#include "sqlite_snapshot_seal.hpp"

#include <sqlite3.h>

#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using anonsync::persistence::SealedSqliteSnapshot;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void cleanup_sqlite_family(const fs::path& path) {
    for (const std::string_view suffix : {"", "-wal", "-shm", "-journal"}) {
        std::error_code ignored;
        fs::remove(fs::path(path.string() + std::string(suffix)), ignored);
    }
}

class Database final {
public:
    Database(const fs::path& path, int flags) {
        if (sqlite3_open_v2(path.c_str(), &database_, flags, nullptr) != SQLITE_OK) {
            const std::string reason = database_ != nullptr
                                           ? sqlite3_errmsg(database_)
                                           : "SQLite open failed";
            if (database_ != nullptr) (void)sqlite3_close_v2(database_);
            database_ = nullptr;
            throw std::runtime_error(reason);
        }
    }

    explicit Database(sqlite3* database) : database_(database) {
        if (database_ == nullptr) throw std::runtime_error("null SQLite handle");
    }

    ~Database() {
        if (database_ != nullptr) (void)sqlite3_close_v2(database_);
    }

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    sqlite3* get() const noexcept { return database_; }

    void exec(const std::string& sql) const {
        const int rc = sqlite3_exec(database_, sql.c_str(), nullptr, nullptr, nullptr);
        if (rc != SQLITE_OK) throw std::runtime_error(sqlite3_errmsg(database_));
    }

    std::int64_t integer(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(database_, sql.c_str(), -1, &statement, nullptr) !=
            SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database_));
        }
        const int rc = sqlite3_step(statement);
        if (rc != SQLITE_ROW || sqlite3_column_type(statement, 0) != SQLITE_INTEGER) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("integer query returned no exact row");
        }
        const std::int64_t value = sqlite3_column_int64(statement, 0);
        (void)sqlite3_finalize(statement);
        return value;
    }

    std::string text(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(database_, sql.c_str(), -1, &statement, nullptr) !=
            SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database_));
        }
        const int rc = sqlite3_step(statement);
        if (rc != SQLITE_ROW || sqlite3_column_type(statement, 0) != SQLITE_TEXT) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("text query returned no exact row");
        }
        const unsigned char* bytes = sqlite3_column_text(statement, 0);
        const int count = sqlite3_column_bytes(statement, 0);
        if (bytes == nullptr || count < 0) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("text query returned invalid bytes");
        }
        std::string value(reinterpret_cast<const char*>(bytes),
                          static_cast<std::size_t>(count));
        (void)sqlite3_finalize(statement);
        return value;
    }

private:
    sqlite3* database_ = nullptr;
};

void create_database(const fs::path& path) {
    cleanup_sqlite_family(path);
    Database database(path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
    database.exec("PRAGMA journal_mode=DELETE;");
    database.exec("CREATE TABLE evidence(value TEXT NOT NULL);");
    database.exec("INSERT INTO evidence(value) VALUES('canonical');");
}

std::array<unsigned char, 100> read_header(const fs::path& path) {
    std::array<unsigned char, 100> header{};
    std::ifstream input(path, std::ios::binary);
    input.read(reinterpret_cast<char*>(header.data()),
               static_cast<std::streamsize>(header.size()));
    if (input.gcount() != static_cast<std::streamsize>(header.size())) {
        throw std::runtime_error("could not read SQLite header fixture");
    }
    return header;
}

std::uint32_t read_be32(const std::array<unsigned char, 100>& bytes,
                        std::size_t offset) {
    return (static_cast<std::uint32_t>(bytes[offset]) << 24U) |
           (static_cast<std::uint32_t>(bytes[offset + 1U]) << 16U) |
           (static_cast<std::uint32_t>(bytes[offset + 2U]) << 8U) |
           static_cast<std::uint32_t>(bytes[offset + 3U]);
}

std::uint32_t header_page_size(const std::array<unsigned char, 100>& header) {
    const std::uint16_t encoded = static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(header[16]) << 8U) |
        static_cast<std::uint16_t>(header[17]));
    return encoded == 1U ? 65536U : static_cast<std::uint32_t>(encoded);
}

void append_ignored_page(const fs::path& path, std::uint32_t page_size) {
    std::ofstream output(path, std::ios::binary | std::ios::app);
    if (!output) throw std::runtime_error("could not open padded snapshot fixture");
    std::vector<char> bytes(page_size, static_cast<char>(0x5a));
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!output) throw std::runtime_error("could not append ignored snapshot page");
}

void backup_logical_database(const fs::path& source, const fs::path& destination) {
    cleanup_sqlite_family(destination);
    Database src(source, SQLITE_OPEN_READONLY);
    Database dst(destination, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
    sqlite3_backup* backup = sqlite3_backup_init(dst.get(), "main", src.get(), "main");
    if (backup == nullptr) throw std::runtime_error(sqlite3_errmsg(dst.get()));
    const int step_rc = sqlite3_backup_step(backup, -1);
    const int finish_rc = sqlite3_backup_finish(backup);
    if (step_rc != SQLITE_DONE || finish_rc != SQLITE_OK) {
        throw std::runtime_error("SQLite logical backup failed");
    }
}

std::set<std::string> staging_directories() {
    std::set<std::string> names;
    std::error_code error;
    for (const auto& entry : fs::directory_iterator("/tmp", error)) {
        if (error) break;
        const std::string name = entry.path().filename().string();
        const std::string process_prefix =
            "anonsync-sqlite-snapshot-seal-" +
            std::to_string(static_cast<long long>(::getpid())) + "-";
        if (name.rfind(process_prefix, 0) == 0) {
            names.insert(name);
        }
    }
    return names;
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const fs::path root = fs::path("/tmp") /
                          ("anonsync_rev0798_geometry_binding_" +
                           std::to_string(::getpid()));
    const fs::path canonical = root / "canonical.sqlite";
    const fs::path padded = root / "padded.sqlite";
    const fs::path restored = root / "restored.sqlite";
    std::error_code ignored;
    fs::remove_all(root, ignored);
    fs::create_directory(root);
    try {
        create_database(canonical);
        fs::copy_file(canonical, padded, fs::copy_options::overwrite_existing);
        const auto header = read_header(padded);
        const std::uint32_t page_size = header_page_size(header);
        const std::uint32_t page_count = read_be32(header, 28U);
        const std::uint64_t logical_bytes =
            static_cast<std::uint64_t>(page_size) * page_count;
        require(fs::file_size(padded) == logical_bytes,
                "canonical fixture did not have exact SQLite geometry", checks);

        append_ignored_page(padded, page_size);
        require(fs::file_size(padded) == logical_bytes + page_size,
                "padding fixture did not append one exact page", checks);

        {
            Database ordinary(padded, SQLITE_OPEN_READONLY);
            require(ordinary.text("SELECT value FROM evidence") == "canonical",
                    "ordinary SQLite did not accept the padded database", checks);
            require(ordinary.integer("PRAGMA page_count;") == page_count,
                    "ordinary SQLite promoted the ignored suffix into page authority",
                    checks);
        }

        backup_logical_database(padded, restored);
        require(fs::file_size(restored) == logical_bytes,
                "SQLite backup did not discard the authenticated trailing page",
                checks);
        require(fs::file_size(restored) != fs::file_size(padded),
                "padded source bytes unexpectedly survived logical restore", checks);
        {
            Database restored_database(restored, SQLITE_OPEN_READONLY);
            require(restored_database.text("SELECT value FROM evidence") ==
                        "canonical",
                    "logical restore changed the visible database row", checks);
        }

        const auto staging_before = staging_directories();
        bool rejected = false;
        std::string reason;
        try {
            (void)SealedSqliteSnapshot::capture(
                padded, "trailing-page authority exploit proof");
        } catch (const std::exception& error) {
            rejected = true;
            reason = error.what();
        }
        require(rejected, "AnonSync accepted a padded SQLite snapshot", checks);
        require(reason.find("header page count does not match exact file bytes") !=
                    std::string::npos,
                "AnonSync rejected padding for an unexpected reason: " + reason,
                checks);
        require(staging_directories() == staging_before,
                "geometry rejection minted a private staging directory", checks);

        {
            SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture(
                canonical, "canonical geometry acceptance proof");
            require(seal.page_size() == page_size,
                    "sealed page-size evidence mismatch", checks);
            require(seal.page_count() == page_count,
                    "sealed page-count evidence mismatch", checks);
            require(seal.geometry().byte_count == logical_bytes,
                    "sealed geometry byte count mismatch", checks);
        }

        fs::remove_all(root, ignored);
        std::cout << "anonsync sqlite snapshot geometry binding checks=" << checks
                  << "\n";
        return 0;
    } catch (const std::exception& error) {
        fs::remove_all(root, ignored);
        std::cerr << "anonsync sqlite snapshot geometry binding failed after "
                  << checks << " checks: " << error.what() << "\n";
        return 1;
    }
}
