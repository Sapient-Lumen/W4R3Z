#include "sqlite_snapshot_seal.hpp"

#include <sqlite3.h>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <type_traits>

#include <sys/stat.h>
#include <unistd.h>

namespace fs = std::filesystem;
using anonsync::persistence::SealedSqliteSnapshot;

namespace {
bool g_armed = false;
unsigned long long g_unlink_calls = 0;
unsigned long long g_rmdir_calls = 0;
}

extern "C" int __real_unlink(const char*);
extern "C" int __wrap_unlink(const char* path) {
    if (g_armed) ++g_unlink_calls;
    return __real_unlink(path);
}
extern "C" int __real_rmdir(const char*);
extern "C" int __wrap_rmdir(const char* path) {
    if (g_armed) ++g_rmdir_calls;
    return __real_rmdir(path);
}

void write_bytes(const fs::path& path, const std::string& bytes, mode_t mode) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("open failed: " + path.string());
    out.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    out.close();
    if (!out || ::chmod(path.c_str(), mode) != 0) {
        throw std::runtime_error("write/chmod failed: " + path.string());
    }
}

std::string read_bytes(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return {};
    return std::string(std::istreambuf_iterator<char>(in), {});
}

template <typename Seal>
concept ExposesStagedPath = requires(const Seal& seal) {
    { seal.staged_path() } -> std::same_as<const fs::path&>;
};

template <typename Seal>
fs::path cleanup_target(Seal& seal, const fs::path& source) {
    if constexpr (ExposesStagedPath<Seal>) {
        return seal.staged_path();
    } else {
        return source;
    }
}

int main() {
    const fs::path root = fs::path("/tmp") /
        ("anonsync_snapshot_cleanup_authority_" + std::to_string(::getpid()));
    std::error_code ignored;
    fs::remove_all(root, ignored);
    fs::create_directory(root);
    const fs::path source = root / "source.sqlite";

    sqlite3* db = nullptr;
    if (sqlite3_open_v2(source.c_str(), &db,
                        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE,
                        nullptr) != SQLITE_OK) {
        throw std::runtime_error("source SQLite open failed");
    }
    if (sqlite3_exec(db,
                     "PRAGMA journal_mode=DELETE;"
                     "CREATE TABLE evidence(value TEXT NOT NULL);"
                     "INSERT INTO evidence VALUES('sealed');",
                     nullptr, nullptr, nullptr) != SQLITE_OK) {
        const std::string reason = sqlite3_errmsg(db);
        sqlite3_close(db);
        throw std::runtime_error(reason);
    }
    sqlite3_close(db);

    auto seal = std::make_unique<SealedSqliteSnapshot>(
        SealedSqliteSnapshot::capture(source, "cleanup authority differential"));
    const fs::path target = cleanup_target(*seal, source);
    const fs::path displaced = target.parent_path() / "writer-owned-displaced.sqlite";
    const fs::path wal = fs::path(target.string() + "-wal");
    const fs::path shm = fs::path(target.string() + "-shm");
    const fs::path journal = fs::path(target.string() + "-journal");

    fs::rename(target, displaced);
    write_bytes(target, "FOREIGN_REPLACEMENT", 0644);
    write_bytes(wal, "FOREIGN_WAL", 0644);
    write_bytes(shm, "FOREIGN_SHM", 0644);
    write_bytes(journal, "FOREIGN_JOURNAL", 0644);

    g_armed = true;
    seal.reset();
    g_armed = false;

    const bool replacement_exact = fs::exists(target) &&
        read_bytes(target) == "FOREIGN_REPLACEMENT";
    const bool wal_exact = fs::exists(wal) && read_bytes(wal) == "FOREIGN_WAL";
    const bool shm_exact = fs::exists(shm) && read_bytes(shm) == "FOREIGN_SHM";
    const bool journal_exact = fs::exists(journal) &&
        read_bytes(journal) == "FOREIGN_JOURNAL";
    const bool displaced_exists = fs::exists(displaced);
    const bool vulnerable = !replacement_exact || !wal_exact || !shm_exact ||
                            !journal_exact;

    std::cout << "{\n"
              << "  \"api_exposes_staged_path\": "
              << (ExposesStagedPath<SealedSqliteSnapshot> ? "true" : "false") << ",\n"
              << "  \"unlink_calls_during_destruction\": " << g_unlink_calls << ",\n"
              << "  \"rmdir_calls_during_destruction\": " << g_rmdir_calls << ",\n"
              << "  \"foreign_replacement_exact\": " << (replacement_exact ? "true" : "false") << ",\n"
              << "  \"foreign_wal_exact\": " << (wal_exact ? "true" : "false") << ",\n"
              << "  \"foreign_shm_exact\": " << (shm_exact ? "true" : "false") << ",\n"
              << "  \"foreign_journal_exact\": " << (journal_exact ? "true" : "false") << ",\n"
              << "  \"displaced_writer_inode_exists\": " << (displaced_exists ? "true" : "false") << ",\n"
              << "  \"vulnerable\": " << (vulnerable ? "true" : "false") << "\n"
              << "}\n";
    fs::remove_all(root, ignored);
    return 0;
}
