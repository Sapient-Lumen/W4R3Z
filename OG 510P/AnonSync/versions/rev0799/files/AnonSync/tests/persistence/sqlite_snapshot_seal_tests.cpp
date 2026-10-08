#include "sqlite_snapshot_seal.hpp"

#include <sqlite3.h>

#include <openssl/evp.h>

#include <array>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using anonsync::persistence::SealedSqliteSnapshot;
using anonsync::persistence::SqliteSnapshotSealPolicy;
using anonsync::persistence::kMaximumUntrustedSqliteSnapshotBytes;
using anonsync::persistence::kMaximumUntrustedSqliteSnapshotPages;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void cleanup_sqlite_family(const fs::path& path) {
    for (const std::string_view suffix : {
             "", "-wal", "-shm", "-journal", ".write.lock", ".restore.lock"}) {
        std::error_code ignored;
        fs::remove(fs::path(path.string() + std::string(suffix)), ignored);
    }
}

class Database final {
public:
    Database(const fs::path& path, int flags) {
        if (sqlite3_open_v2(path.c_str(), &database_, flags, nullptr) != SQLITE_OK) {
            const std::string reason =
                database_ != nullptr ? sqlite3_errmsg(database_) : "SQLite open failed";
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
        char* error = nullptr;
        const int rc = sqlite3_exec(database_, sql.c_str(), nullptr, nullptr, &error);
        if (rc != SQLITE_OK) {
            const std::string reason =
                error != nullptr ? error : sqlite3_errmsg(database_);
            sqlite3_free(error);
            throw std::runtime_error(reason);
        }
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
            throw std::runtime_error("integer query returned no exact integer row");
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
            throw std::runtime_error("text query returned no exact text row");
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

class TemporarilyUnregisteredVfs final {
public:
    explicit TemporarilyUnregisteredVfs(sqlite3_vfs* vfs) : vfs_(vfs) {
        if (vfs_ != nullptr) unregistered_ = sqlite3_vfs_unregister(vfs_) == SQLITE_OK;
    }

    ~TemporarilyUnregisteredVfs() {
        if (unregistered_) (void)sqlite3_vfs_register(vfs_, 1);
    }

    TemporarilyUnregisteredVfs(const TemporarilyUnregisteredVfs&) = delete;
    TemporarilyUnregisteredVfs& operator=(const TemporarilyUnregisteredVfs&) = delete;

    bool unregistered() const noexcept { return unregistered_; }

private:
    sqlite3_vfs* vfs_ = nullptr;
    bool unregistered_ = false;
};

class RegisteredDefaultAliasVfs final {
public:
    explicit RegisteredDefaultAliasVfs(std::string name)
        : name_(std::move(name)), base_(sqlite3_vfs_find(nullptr)) {
        if (base_ == nullptr || active_ != nullptr) return;
        alias_ = *base_;
        alias_.zName = name_.c_str();
        alias_.pNext = nullptr;
        alias_.xOpen = &RegisteredDefaultAliasVfs::open;
        active_ = this;
        registered_ = sqlite3_vfs_register(&alias_, 1) == SQLITE_OK;
        if (!registered_) active_ = nullptr;
    }

    ~RegisteredDefaultAliasVfs() {
        if (registered_) (void)sqlite3_vfs_unregister(&alias_);
        if (active_ == this) active_ = nullptr;
    }

    RegisteredDefaultAliasVfs(const RegisteredDefaultAliasVfs&) = delete;
    RegisteredDefaultAliasVfs& operator=(const RegisteredDefaultAliasVfs&) = delete;

    bool registered() const noexcept { return registered_; }
    sqlite3_vfs* pointer() noexcept { return &alias_; }
    std::uint64_t open_calls() const noexcept { return open_calls_; }

private:
    static int open(sqlite3_vfs* vfs,
                    sqlite3_filename filename,
                    sqlite3_file* file,
                    int flags,
                    int* output_flags) {
        if (active_ == nullptr || vfs != &active_->alias_ ||
            active_->base_ == nullptr || active_->base_->xOpen == nullptr) {
            return SQLITE_CANTOPEN;
        }
        ++active_->open_calls_;
        return active_->base_->xOpen(
            active_->base_, filename, file, flags, output_flags);
    }

    inline static RegisteredDefaultAliasVfs* active_ = nullptr;
    std::string name_;
    sqlite3_vfs* base_ = nullptr;
    sqlite3_vfs alias_{};
    std::uint64_t open_calls_ = 0;
    bool registered_ = false;
};

void create_database(const fs::path& path, const std::string& value) {
    cleanup_sqlite_family(path);
    Database database(path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
    database.exec("PRAGMA journal_mode=DELETE;");
    database.exec("CREATE TABLE evidence(value TEXT NOT NULL);");
    sqlite3_stmt* statement = nullptr;
    if (sqlite3_prepare_v2(database.get(),
                          "INSERT INTO evidence(value) VALUES(?);", -1,
                          &statement, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(database.get()));
    }
    if (sqlite3_bind_text(statement, 1, value.data(),
                          static_cast<int>(value.size()), SQLITE_TRANSIENT) !=
            SQLITE_OK ||
        sqlite3_step(statement) != SQLITE_DONE) {
        const std::string reason = sqlite3_errmsg(database.get());
        (void)sqlite3_finalize(statement);
        throw std::runtime_error(reason);
    }
    (void)sqlite3_finalize(statement);
}

std::string sha256_file(const fs::path& path) {
    using DigestContext = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;
    DigestContext digest(EVP_MD_CTX_new(), &EVP_MD_CTX_free);
    if (!digest || EVP_DigestInit_ex(digest.get(), EVP_sha256(), nullptr) != 1) {
        throw std::runtime_error("SHA-256 initialization failed");
    }
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("could not open file for hashing");
    std::array<char, 64U * 1024U> buffer{};
    while (input) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = input.gcount();
        if (count > 0 &&
            EVP_DigestUpdate(digest.get(), buffer.data(),
                             static_cast<std::size_t>(count)) != 1) {
            throw std::runtime_error("SHA-256 update failed");
        }
    }
    if (!input.eof()) throw std::runtime_error("file hash read failed");
    std::array<unsigned char, EVP_MAX_MD_SIZE> bytes{};
    unsigned int count = 0;
    if (EVP_DigestFinal_ex(digest.get(), bytes.data(), &count) != 1 || count != 32U) {
        throw std::runtime_error("SHA-256 finalization failed");
    }
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < count; ++i) {
        output << std::setw(2) << static_cast<unsigned int>(bytes[i]);
    }
    return output.str();
}

template <typename Callable>
std::string expect_rejection(Callable&& callable,
                             const std::string& expected_fragment,
                             std::uint64_t& checks) {
    bool rejected = false;
    std::string reason;
    try {
        callable();
    } catch (const std::exception& error) {
        rejected = true;
        reason = error.what();
    }
    require(rejected, "expected rejection did not occur", checks);
    require(reason.find(expected_fragment) != std::string::npos,
            "rejection reason mismatch: " + reason, checks);
    return reason;
}

void test_exact_capture_and_path_independence(const fs::path& root,
                                              std::uint64_t& checks) {
    const fs::path source = root / "snapshot with ? hash# percent%.sqlite";
    const fs::path replacement = root / "replacement.sqlite";
    create_database(source, "alpha");
    const std::string source_digest = sha256_file(source);

    fs::path staged;
    fs::path staging_directory;
    {
        SealedSqliteSnapshot seal =
            SealedSqliteSnapshot::capture(source, "focused snapshot seal");
        staged = seal.staged_path();
        staging_directory = staged.parent_path();
        require(seal.sha256_hex() == source_digest,
                "sealed digest did not bind copied source bytes", checks);
        require(seal.byte_count() == fs::file_size(source),
                "sealed byte count mismatch", checks);
        require(seal.page_size() >= 512U && seal.page_size() <= 65536U,
                "sealed page-size evidence is outside SQLite bounds", checks);
        require(seal.page_count() > 0U,
                "sealed page-count evidence is absent", checks);
        require(static_cast<std::uint64_t>(seal.page_size()) *
                        static_cast<std::uint64_t>(seal.page_count()) ==
                    seal.byte_count(),
                "sealed page geometry does not bind exact bytes", checks);
        require(seal.geometry().byte_count == seal.byte_count(),
                "sealed geometry capability lost its byte count", checks);
        require(seal.immutable_uri().find("immutable=1") != std::string::npos,
                "immutable URI parameter is absent", checks);
        require(seal.immutable_uri().find("mode=ro") != std::string::npos,
                "read-only URI parameter is absent", checks);
        require(seal.immutable_uri().find("cache=private") != std::string::npos,
                "private-cache URI parameter is absent", checks);
        require(seal.immutable_uri().rfind("file:/tmp/", 0) == 0,
                "immutable URI does not name the private staging tree", checks);

        struct stat directory_status{};
        struct stat staged_status{};
        require(::lstat(staging_directory.c_str(), &directory_status) == 0 &&
                    S_ISDIR(directory_status.st_mode) &&
                    (directory_status.st_mode & 0777) == 0700,
                "staging directory is not private mode 0700", checks);
        require(::lstat(staged.c_str(), &staged_status) == 0 &&
                    S_ISREG(staged_status.st_mode) &&
                    (staged_status.st_mode & 0777) == 0400,
                "staged snapshot is not regular mode 0400", checks);

        sqlite3_vfs* const captured_default_vfs = sqlite3_vfs_find(nullptr);
        require(captured_default_vfs != nullptr,
                "SQLite did not expose a default VFS before substitution", checks);
        {
            RegisteredDefaultAliasVfs replacement_default(
                "anonsync-rev0796-replacement-default-vfs-" +
                std::to_string(::getpid()));
            require(replacement_default.registered() &&
                        sqlite3_vfs_find(nullptr) == replacement_default.pointer(),
                    "replacement VFS did not become process default", checks);
            {
                Database database(
                    seal.open_database_or_throw("focused pinned-VFS immutable open"));
                require(database.text("SELECT value FROM evidence") == "alpha",
                        "sealed SQLite view did not match captured bytes", checks);
            }
            require(replacement_default.open_calls() == 0,
                    "sealed open inherited a replacement process-default VFS", checks);
            {
                Database ordinary(source, SQLITE_OPEN_READONLY);
                require(ordinary.text("SELECT value FROM evidence") == "alpha" &&
                            replacement_default.open_calls() > 0,
                        "replacement default VFS probe did not observe an ordinary open",
                        checks);
            }
        }
        require(sqlite3_vfs_find(nullptr) == captured_default_vfs,
                "default VFS did not return to its captured object", checks);
        {
            TemporarilyUnregisteredVfs missing_registration(captured_default_vfs);
            require(missing_registration.unregistered(),
                    "could not unregister captured VFS for registry proof", checks);
            expect_rejection(
                [&] {
                    (void)seal.open_database_or_throw(
                        "focused missing pinned-VFS registration open");
                },
                "sealed SQLite VFS registration changed after capture", checks);
        }
        require(sqlite3_vfs_find(nullptr) == captured_default_vfs,
                "captured VFS was not restored after registry proof", checks);
        seal.verify_unchanged_or_throw("focused post-query seal check");

        create_database(replacement, "beta");
        fs::rename(replacement, source);
        {
            Database database(seal.open_database_or_throw("focused post-replace open"));
            require(database.text("SELECT value FROM evidence") == "alpha",
                    "sealed snapshot followed a replaced source pathname", checks);
        }
        require(Database(source, SQLITE_OPEN_READONLY)
                    .text("SELECT value FROM evidence") == "beta",
                "source replacement fixture did not take effect", checks);
    }
    require(!fs::exists(staged), "sealed snapshot staging file leaked", checks);
    require(!fs::exists(staging_directory),
            "sealed snapshot staging directory leaked", checks);
    cleanup_sqlite_family(source);
    cleanup_sqlite_family(replacement);
}

void test_wal_laundering_rejected(const fs::path& root,
                                  std::uint64_t& checks) {
    const fs::path source = root / "wal-laundering.sqlite";
    cleanup_sqlite_family(source);
    {
        Database writer(source, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
        writer.exec("PRAGMA journal_mode=WAL;");
        writer.exec("PRAGMA wal_autocheckpoint=0;");
        writer.exec("CREATE TABLE evidence(value TEXT NOT NULL);");
        writer.exec("INSERT INTO evidence(value) VALUES('main');");
        writer.exec("PRAGMA wal_checkpoint(TRUNCATE);");
        const std::string main_digest_before = sha256_file(source);
        writer.exec("INSERT INTO evidence(value) VALUES('wal-only');");
        const std::string main_digest_after = sha256_file(source);

        require(main_digest_after == main_digest_before,
                "WAL exploit fixture changed signed main-file bytes", checks);
        require(fs::exists(fs::path(source.string() + "-wal")),
                "WAL exploit fixture did not create a WAL sidecar", checks);
        {
            Database ordinary_reader(source, SQLITE_OPEN_READONLY);
            require(ordinary_reader.integer("SELECT count(*) FROM evidence") == 2,
                    "ordinary read-only SQLite did not merge unsigned WAL state",
                    checks);
        }
        expect_rejection(
            [&] {
                (void)SealedSqliteSnapshot::capture(source,
                                                    "WAL laundering proof");
            },
            "snapshot sidecar -wal", checks);
    }
    cleanup_sqlite_family(source);
}

void test_other_sidecars_and_link_aliases_rejected(const fs::path& root,
                                                    std::uint64_t& checks) {
    const fs::path source = root / "sidecar.sqlite";
    create_database(source, "value");
    for (const std::string_view suffix : {"-shm", "-journal"}) {
        const fs::path sidecar(source.string() + std::string(suffix));
        {
            std::ofstream output(sidecar, std::ios::binary);
            output << "attacker-controlled sidecar";
        }
        expect_rejection(
            [&] {
                (void)SealedSqliteSnapshot::capture(source, "sidecar absence proof");
            },
            "snapshot sidecar " + std::string(suffix), checks);
        fs::remove(sidecar);
    }

    const fs::path symlink_path = root / "source-symlink.sqlite";
    fs::create_symlink(source.filename(), symlink_path);
    expect_rejection(
        [&] {
            (void)SealedSqliteSnapshot::capture(symlink_path, "symlink proof");
        },
        "symbolic-link SQLite family member", checks);
    fs::remove(symlink_path);

    const fs::path hardlink_path = root / "source-hardlink.sqlite";
    fs::create_hard_link(source, hardlink_path);
    expect_rejection(
        [&] {
            (void)SealedSqliteSnapshot::capture(source, "hardlink proof");
        },
        "multiply-linked SQLite family member", checks);
    fs::remove(hardlink_path);
    cleanup_sqlite_family(source);
}

void test_budget_and_staged_tamper_detection(const fs::path& root,
                                             std::uint64_t& checks) {
    const fs::path source = root / "budget.sqlite";
    create_database(source, "value");
    expect_rejection(
        [&] {
            SqliteSnapshotSealPolicy policy;
            policy.maximum_bytes = 1024;
            (void)SealedSqliteSnapshot::capture(source, "byte ceiling proof", policy);
        },
        "exceeds the byte ceiling", checks);
    expect_rejection(
        [&] {
            SqliteSnapshotSealPolicy policy;
            policy.maximum_bytes = 0;
            (void)SealedSqliteSnapshot::capture(source, "zero ceiling proof", policy);
        },
        "zero ceiling", checks);
    expect_rejection(
        [&] {
            SqliteSnapshotSealPolicy policy;
            policy.maximum_pages = 0;
            (void)SealedSqliteSnapshot::capture(source, "zero page ceiling proof", policy);
        },
        "zero ceiling", checks);
    expect_rejection(
        [&] {
            SqliteSnapshotSealPolicy policy;
            policy.maximum_bytes = kMaximumUntrustedSqliteSnapshotBytes + 1U;
            (void)SealedSqliteSnapshot::capture(source, "byte authority widening proof", policy);
        },
        "may tighten but not widen", checks);
    expect_rejection(
        [&] {
            SqliteSnapshotSealPolicy policy;
            policy.maximum_pages = kMaximumUntrustedSqliteSnapshotPages + 1U;
            (void)SealedSqliteSnapshot::capture(source, "page authority widening proof", policy);
        },
        "may tighten but not widen", checks);
    expect_rejection(
        [&] {
            SqliteSnapshotSealPolicy policy;
            policy.maximum_pages = 1U;
            (void)SealedSqliteSnapshot::capture(source, "tight page ceiling proof", policy);
        },
        "exceeds the page ceiling", checks);

    {
        SealedSqliteSnapshot seal =
            SealedSqliteSnapshot::capture(source, "staged tamper proof");
        const fs::path malicious_sidecar(seal.staged_path().string() + "-wal");
        {
            std::ofstream output(malicious_sidecar, std::ios::binary);
            output << "late sidecar";
        }
        expect_rejection(
            [&] { seal.verify_unchanged_or_throw("late sidecar proof"); },
            "snapshot sidecar -wal", checks);
        fs::remove(malicious_sidecar);
        require(::chmod(seal.staged_path().c_str(), 0600) == 0,
                "could not modify staged mode for tamper proof", checks);
        expect_rejection(
            [&] { seal.verify_unchanged_or_throw("staged mode proof"); },
            "changed after capture", checks);
    }

    {
        SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture(
            source, "staging directory permission proof");
        const fs::path staging_directory = seal.staged_path().parent_path();
        require(::chmod(staging_directory.c_str(), 0755) == 0,
                "could not weaken staging directory mode for tamper proof",
                checks);
        expect_rejection(
            [&] {
                seal.verify_unchanged_or_throw(
                    "staging directory permission downgrade proof");
            },
            "private SQLite parent directory is not owned mode 0700", checks);
        require(::chmod(staging_directory.c_str(), 0700) == 0,
                "could not restore staging directory mode after tamper proof",
                checks);
    }

    {
        SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture(
            source, "same-size staged tamper proof");
        require(::chmod(seal.staged_path().c_str(), 0600) == 0,
                "could not make staged file writable for same-size tamper proof",
                checks);
        {
            std::fstream file(seal.staged_path(),
                              std::ios::in | std::ios::out | std::ios::binary);
            require(static_cast<bool>(file),
                    "could not open staged file for same-size tamper proof",
                    checks);
            const char replacement = 'X';
            file.write(&replacement, 1);
            file.flush();
            require(static_cast<bool>(file),
                    "same-size staged tamper write failed", checks);
        }
        require(::chmod(seal.staged_path().c_str(), 0400) == 0,
                "could not restore staged mode after same-size tamper", checks);
        expect_rejection(
            [&] {
                seal.verify_unchanged_or_throw(
                    "same-size staged byte tamper proof");
            },
            "changed after capture", checks);
    }

    const fs::path empty = root / "empty.sqlite";
    {
        std::ofstream output(empty, std::ios::binary);
    }
    expect_rejection(
        [&] { (void)SealedSqliteSnapshot::capture(empty, "empty proof"); },
        "source snapshot is empty", checks);
    fs::remove(empty);
    cleanup_sqlite_family(source);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const fs::path root =
        fs::path("/tmp") /
        ("anonsync_rev0798_snapshot_seal_" + std::to_string(::getpid()));
    std::error_code ignored;
    fs::remove_all(root, ignored);
    fs::create_directory(root);
    try {
        test_exact_capture_and_path_independence(root, checks);
        test_wal_laundering_rejected(root, checks);
        test_other_sidecars_and_link_aliases_rejected(root, checks);
        test_budget_and_staged_tamper_detection(root, checks);
        fs::remove_all(root, ignored);
        std::cout << "anonsync sqlite snapshot seal tests checks=" << checks
                  << "\n";
        return 0;
    } catch (const std::exception& error) {
        fs::remove_all(root, ignored);
        std::cerr << "anonsync sqlite snapshot seal test failed after " << checks
                  << " checks: " << error.what() << "\n";
        return 1;
    }
}
