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
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using anonsync::SyncSqliteDbHandleSlot;
using anonsync::SyncSqliteSerializedDbBorrow;
using anonsync::borrow_sync_sqlite_serialized_db_or_throw;
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

std::int64_t query_integer_nonowning(sqlite3* database,
                                        const std::string& sql) {
    if (database == nullptr) {
        throw std::runtime_error("non-owning integer query requires a database");
    }
    sqlite3_stmt* statement = nullptr;
    if (sqlite3_prepare_v2(database, sql.c_str(), -1, &statement, nullptr) !=
        SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(database));
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

std::string query_text_nonowning(sqlite3* database, const std::string& sql) {
    if (database == nullptr) {
        throw std::runtime_error("non-owning text query requires a database");
    }
    sqlite3_stmt* statement = nullptr;
    if (sqlite3_prepare_v2(database, sql.c_str(), -1, &statement, nullptr) !=
        SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(database));
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
        return query_integer_nonowning(database_, sql);
    }

    std::string text(const std::string& sql) const {
        return query_text_nonowning(database_, sql);
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
    std::uint64_t non_memory_open_calls() const noexcept {
        return non_memory_open_calls_;
    }
    std::uint64_t named_open_calls() const noexcept { return named_open_calls_; }

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
        if ((flags & SQLITE_OPEN_MEMORY) == 0) {
            ++active_->non_memory_open_calls_;
        }
        if (filename != nullptr && filename[0] != '\0') {
            ++active_->named_open_calls_;
        }
        return active_->base_->xOpen(
            active_->base_, filename, file, flags, output_flags);
    }

    inline static RegisteredDefaultAliasVfs* active_ = nullptr;
    std::string name_;
    sqlite3_vfs* base_ = nullptr;
    sqlite3_vfs alias_{};
    std::uint64_t open_calls_ = 0;
    std::uint64_t non_memory_open_calls_ = 0;
    std::uint64_t named_open_calls_ = 0;
    bool registered_ = false;
};

struct PreflightGrowthTrace {
    sqlite3* writer = nullptr;
    bool armed = false;
    bool fired = false;
    int sqlite_result = SQLITE_OK;
};

int grow_after_source_page_count_profile(unsigned trace_event,
                                         void* context,
                                         void* statement_pointer,
                                         void*) noexcept {
    auto& state = *static_cast<PreflightGrowthTrace*>(context);
    if (trace_event != SQLITE_TRACE_PROFILE || !state.armed ||
        statement_pointer == nullptr) {
        return 0;
    }
    const char* const sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr || std::string_view(sql) != "PRAGMA main.page_count;") {
        return 0;
    }
    state.armed = false;
    state.fired = true;
    state.sqlite_result = sqlite3_exec(
        state.writer,
        "INSERT INTO evidence(value) VALUES(zeroblob(4194304));",
        nullptr, nullptr, nullptr);
    return 0;
}

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


std::set<std::string> snapshot_staging_entries() {
    std::set<std::string> entries;
    std::error_code error;
    for (const auto& entry : fs::directory_iterator("/tmp", error)) {
        if (error) break;
        const std::string name = entry.path().filename().string();
        if (name.rfind("anonsync-sqlite-snapshot-seal-", 0) == 0) {
            entries.insert(name);
        }
    }
    if (error) throw std::runtime_error("could not inventory /tmp snapshot staging entries");
    return entries;
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

std::array<unsigned char, 2> sqlite_file_format_versions(
    const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("could not open SQLite header fixture");
    input.seekg(18, std::ios::beg);
    std::array<unsigned char, 2> versions{};
    input.read(reinterpret_cast<char*>(versions.data()),
               static_cast<std::streamsize>(versions.size()));
    if (input.gcount() != static_cast<std::streamsize>(versions.size())) {
        throw std::runtime_error("could not read SQLite file-format versions");
    }
    return versions;
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
    const fs::path published = root / "published exact copy.sqlite";
    const fs::path immutable_published =
        root / "published immutable exact copy.sqlite";
    create_database(source, "alpha");
    cleanup_sqlite_family(immutable_published);
    const std::string source_digest = sha256_file(source);
    const auto namespace_before = snapshot_staging_entries();

    sqlite3* surviving_database = nullptr;
    {
        SealedSqliteSnapshot seal =
            SealedSqliteSnapshot::capture(source, "focused snapshot seal");
        require(snapshot_staging_entries() == namespace_before,
                "snapshot capture minted a staging pathname", checks);
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

        seal.publish_exact_copy_atomically_or_throw(
            published, "focused sealed snapshot exact publication");
        require(sha256_file(published) == seal.sha256_hex(),
                "sealed publication changed the exact resident bytes", checks);
        require(sqlite_file_format_versions(published) ==
                    std::array<unsigned char, 2>{1U, 1U},
                "sealed publication did not preserve portable 1/1 format", checks);
        require(Database(published, SQLITE_OPEN_READONLY)
                    .text("SELECT value FROM evidence") == "alpha",
                "sealed publication did not preserve logical snapshot state",
                checks);
        require(!fs::exists(fs::path(published.string() + "-wal")) &&
                    !fs::exists(fs::path(published.string() + "-shm")) &&
                    !fs::exists(fs::path(published.string() + "-journal")),
                "sealed publication manufactured a SQLite sidecar family",
                checks);

        seal.publish_exact_copy_atomically_create_new_or_throw(
            immutable_published,
            "focused sealed snapshot immutable publication");
        const std::string immutable_digest = sha256_file(immutable_published);
        require(immutable_digest == seal.sha256_hex(),
                "immutable sealed publication changed resident bytes", checks);
        expect_rejection(
            [&] {
                seal.publish_exact_copy_atomically_create_new_or_throw(
                    immutable_published,
                    "focused sealed snapshot immutable republish");
            },
            "already exists", checks);
        require(sha256_file(immutable_published) == immutable_digest,
                "failed immutable republish replaced the existing image",
                checks);

        sqlite3_vfs* const captured_default_vfs = sqlite3_vfs_find(nullptr);
        require(captured_default_vfs != nullptr,
                "SQLite did not expose a default VFS before substitution", checks);
        {
            RegisteredDefaultAliasVfs replacement_default(
                "anonsync-rev0820-replacement-default-vfs-" +
                std::to_string(::getpid()));
            require(replacement_default.registered() &&
                        sqlite3_vfs_find(nullptr) == replacement_default.pointer(),
                    "replacement VFS did not become process default", checks);
            {
                SyncSqliteDbHandleSlot database_owner =
                    seal.open_database_owner_or_throw(
                        "focused pinned-VFS deserialize");
                const std::uint64_t owner_generation =
                    database_owner.generation();
                require(owner_generation != 0U &&
                            database_owner.active_borrows() == 0U,
                        "typed deserialization did not mint one idle generation",
                        checks);
                SyncSqliteSerializedDbBorrow database_borrow =
                    borrow_sync_sqlite_serialized_db_or_throw(
                        database_owner,
                        "focused pinned-VFS deserialize generation");
                sqlite3* const database = database_borrow.get();
                require(database_borrow.generation() == owner_generation &&
                            database_owner.active_borrows() == 1U,
                        "typed deserialization borrow lost exact generation",
                        checks);
                require(query_text_nonowning(
                            database, "SELECT value FROM evidence") == "alpha",
                        "deserialized SQLite view did not match captured bytes", checks);
                const char* const filename = sqlite3_db_filename(database, "main");
                require(filename != nullptr && filename[0] == '\0',
                        "deserialized SQLite view unexpectedly names a file", checks);
                expect_rejection(
                    [&] {
                        char* error = nullptr;
                        const int rc = sqlite3_exec(
                            database, "INSERT INTO evidence VALUES('write');",
                            nullptr, nullptr, &error);
                        const std::string reason =
                            error != nullptr ? error : sqlite3_errmsg(database);
                        sqlite3_free(error);
                        if (rc != SQLITE_OK) throw std::runtime_error(reason);
                    },
                    "readonly", checks);
                database_borrow.reset();
                require(database_owner.active_borrows() == 0U &&
                            database_owner.generation() == owner_generation,
                        "typed deserialization borrow did not release cleanly",
                        checks);
                database_owner.reset();
            }
            require(replacement_default.open_calls() == 0,
                    "deserialized open inherited a replacement process-default VFS",
                    checks);
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
                    (void)seal.open_database_owner_or_throw(
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
            SyncSqliteDbHandleSlot database_owner =
                seal.open_database_owner_or_throw(
                    "focused post-replace deserialize");
            require(query_text_nonowning(
                        database_owner.get(), "SELECT value FROM evidence") ==
                        "alpha",
                    "sealed snapshot followed a replaced source pathname", checks);
        }
        require(Database(source, SQLITE_OPEN_READONLY)
                    .text("SELECT value FROM evidence") == "beta",
                "source replacement fixture did not take effect", checks);
        surviving_database = seal.open_database_or_throw(
            "focused handle-outlives-seal deserialize");
    }
    require(snapshot_staging_entries() == namespace_before,
            "snapshot destruction changed the staging namespace", checks);
    {
        Database database(surviving_database);
        surviving_database = nullptr;
        require(database.text("SELECT value FROM evidence") == "alpha",
                "deserialized handle depended on seal lifetime", checks);
    }
    cleanup_sqlite_family(source);
    cleanup_sqlite_family(replacement);
    cleanup_sqlite_family(published);
    cleanup_sqlite_family(immutable_published);
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

void test_quiescent_wal_format_rejected(const fs::path& root,
                                        std::uint64_t& checks) {
    const fs::path source = root / "quiescent-wal-format.sqlite";
    cleanup_sqlite_family(source);
    {
        Database writer(source, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
        writer.exec("PRAGMA journal_mode=WAL;");
        writer.exec("CREATE TABLE evidence(value TEXT NOT NULL);");
        writer.exec("INSERT INTO evidence(value) VALUES('checkpointed');");
        writer.exec("PRAGMA wal_checkpoint(TRUNCATE);");
    }

    require(!fs::exists(fs::path(source.string() + "-wal")) &&
                !fs::exists(fs::path(source.string() + "-shm")),
            "clean WAL close retained a sidecar in the format-version fixture",
            checks);
    const auto versions = sqlite_file_format_versions(source);
    require(versions[0] == 2U && versions[1] == 2U,
            "clean WAL fixture did not retain file-format versions 2/2", checks);
    const auto namespace_before = snapshot_staging_entries();
    expect_rejection(
        [&] {
            (void)SealedSqliteSnapshot::capture(
                source, "quiescent WAL format deserialization proof");
        },
        "rollback-journal file format versions 1/1", checks);
    require(snapshot_staging_entries() == namespace_before,
            "quiescent WAL format rejection changed the staging namespace",
            checks);
    require(Database(source, SQLITE_OPEN_READONLY)
                .text("SELECT value FROM evidence") == "checkpointed",
            "ordinary SQLite could not read the quiescent WAL-format main file",
            checks);
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

void test_live_database_capture(const fs::path& root,
                                std::uint64_t& checks) {
    const fs::path source_path = root / "live-capture-source.sqlite";
    const fs::path published_path = root / "live-capture-published.sqlite";
    const fs::path no_mutex_path = root / "live-capture-no-mutex.sqlite";
    cleanup_sqlite_family(source_path);
    cleanup_sqlite_family(published_path);
    cleanup_sqlite_family(no_mutex_path);

    RegisteredDefaultAliasVfs observed_vfs(
        "anonsync-rev0823-live-capture-vfs-" + std::to_string(::getpid()));
    require(observed_vfs.registered() &&
                sqlite3_vfs_find(nullptr) == observed_vfs.pointer(),
            "live-capture observer VFS did not become the process default", checks);

    {
        Database source(
            source_path,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX |
                SQLITE_OPEN_PRIVATECACHE);
        source.exec("PRAGMA journal_mode=WAL;");
        source.exec("PRAGMA wal_autocheckpoint=0;");
        source.exec("CREATE TABLE evidence(id INTEGER PRIMARY KEY, value TEXT NOT NULL);");
        source.exec("INSERT INTO evidence(value) VALUES('before-capture');");
        require(source.integer("SELECT count(*) FROM evidence;") == 1,
                "live source fixture did not commit its first row", checks);

        const auto namespace_before = snapshot_staging_entries();
        const std::uint64_t non_memory_opens_before =
            observed_vfs.non_memory_open_calls();
        const std::uint64_t named_opens_before = observed_vfs.named_open_calls();
        SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture_database(
            source.get(), "focused live-database snapshot seal");
        require(seal.source_path().empty(),
                "live-database seal retained a filesystem source pathname", checks);
        require(observed_vfs.non_memory_open_calls() == non_memory_opens_before &&
                    observed_vfs.named_open_calls() == named_opens_before,
                "live-database capture opened a non-memory or named VFS file", checks);
        require(snapshot_staging_entries() == namespace_before,
                "live-database capture minted a filesystem staging namespace", checks);
        seal.verify_unchanged_or_throw("focused live-database resident proof");

        source.exec("INSERT INTO evidence(value) VALUES('after-capture');");
        require(source.integer("SELECT count(*) FROM evidence;") == 2,
                "source connection stopped accepting commits after live capture", checks);
        {
            SyncSqliteDbHandleSlot captured =
                seal.open_database_owner_or_throw(
                    "focused live-database independent deserialize");
            require(query_integer_nonowning(
                        captured.get(), "SELECT count(*) FROM evidence;") == 1,
                    "resident live capture followed later source mutations", checks);
            require(query_text_nonowning(
                        captured.get(),
                        "SELECT value FROM evidence WHERE id=1;") ==
                        "before-capture",
                    "resident live capture changed committed source content", checks);
        }

        seal.publish_exact_copy_atomically_or_throw(
            published_path, "focused live-database exact publication");
        require(sqlite_file_format_versions(published_path) ==
                    std::array<unsigned char, 2>{1U, 1U},
                "live-database publication is not standalone format 1/1", checks);
        require(Database(published_path, SQLITE_OPEN_READONLY)
                    .integer("SELECT count(*) FROM evidence;") == 1,
                "live-database publication did not preserve capture-time state", checks);
        require(!fs::exists(fs::path(published_path.string() + "-wal")) &&
                    !fs::exists(fs::path(published_path.string() + "-shm")) &&
                    !fs::exists(fs::path(published_path.string() + "-journal")),
                "live-database publication manufactured a SQLite sidecar", checks);

        source.exec("BEGIN IMMEDIATE;");
        expect_rejection(
            [&] {
                (void)SealedSqliteSnapshot::capture_database(
                    source.get(), "active-transaction live capture proof");
            },
            "active transaction", checks);
        source.exec("ROLLBACK;");

        const std::uint64_t opens_before_tight_policy = observed_vfs.open_calls();
        const auto namespace_before_tight_policy = snapshot_staging_entries();
        expect_rejection(
            [&] {
                SqliteSnapshotSealPolicy policy;
                policy.maximum_bytes = 1024U;
                (void)SealedSqliteSnapshot::capture_database(
                    source.get(), "live-capture byte ceiling proof", policy);
            },
            "exceeds the byte ceiling", checks);
        require(observed_vfs.open_calls() == opens_before_tight_policy,
                "oversized live capture opened a private destination before source geometry rejection",
                checks);
        require(snapshot_staging_entries() == namespace_before_tight_policy,
                "oversized live capture changed the staging namespace before source geometry rejection",
                checks);

        Database writer(
            source_path,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                SQLITE_OPEN_PRIVATECACHE);
        writer.exec("PRAGMA journal_mode=WAL;");
        writer.exec("PRAGMA wal_autocheckpoint=0;");
        const std::uint64_t pre_race_page_size = static_cast<std::uint64_t>(
            source.integer("PRAGMA main.page_size;"));
        const std::uint64_t pre_race_pages = static_cast<std::uint64_t>(
            source.integer("PRAGMA main.page_count;"));
        SqliteSnapshotSealPolicy exact_pre_race_policy;
        exact_pre_race_policy.maximum_pages = pre_race_pages;
        exact_pre_race_policy.maximum_bytes =
            pre_race_page_size * pre_race_pages;
        PreflightGrowthTrace growth_trace{writer.get(), true, false, SQLITE_OK};
        if (sqlite3_trace_v2(source.get(), SQLITE_TRACE_PROFILE,
                             &grow_after_source_page_count_profile,
                             &growth_trace) != SQLITE_OK) {
            throw std::runtime_error(
                "could not install preflight-to-pin growth trace");
        }
        expect_rejection(
            [&] {
                (void)SealedSqliteSnapshot::capture_database(
                    source.get(), "preflight-to-pin growth race proof",
                    exact_pre_race_policy);
            },
            "exceeds the page ceiling", checks);
        (void)sqlite3_trace_v2(source.get(), 0U, nullptr, nullptr);
        require(growth_trace.fired &&
                    growth_trace.sqlite_result == SQLITE_OK,
                "preflight-to-pin growth trace did not commit after early page-count observation",
                checks);
        require(static_cast<std::uint64_t>(
                    writer.integer("PRAGMA main.page_count;")) > pre_race_pages,
                "preflight-to-pin growth race did not exceed the early policy evidence",
                checks);
        require(source.integer("SELECT count(*) FROM evidence;") == 3,
                "source did not retain the commit rejected by the pinned geometry proof",
                checks);
        expect_rejection(
            [&] {
                (void)SealedSqliteSnapshot::capture_database(
                    nullptr, "null live capture proof");
            },
            "handle is null", checks);
    }

    {
        Database no_mutex(
            no_mutex_path,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_NOMUTEX |
                SQLITE_OPEN_PRIVATECACHE);
        require(sqlite3_db_mutex(no_mutex.get()) == nullptr,
                "no-mutex source fixture unexpectedly exposes a database mutex", checks);
        expect_rejection(
            [&] {
                (void)SealedSqliteSnapshot::capture_database(
                    no_mutex.get(), "no-mutex live capture proof");
            },
            "lacks full-mutex protection", checks);
    }

    cleanup_sqlite_family(source_path);
    cleanup_sqlite_family(published_path);
    cleanup_sqlite_family(no_mutex_path);
}

void test_budget_and_resident_deserialization(const fs::path& root,
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

    const auto namespace_before = snapshot_staging_entries();
    {
        SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture(
            source, "resident deserialize proof");
        seal.verify_unchanged_or_throw("resident byte proof");
        require(snapshot_staging_entries() == namespace_before,
                "resident seal created a filesystem staging artifact", checks);

        SyncSqliteDbHandleSlot first = seal.open_database_owner_or_throw(
            "first independent deserialize proof");
        SyncSqliteDbHandleSlot second = seal.open_database_owner_or_throw(
            "second independent deserialize proof");
        require(query_text_nonowning(
                    first.get(), "SELECT value FROM evidence") == "value" &&
                    query_text_nonowning(
                        second.get(), "SELECT value FROM evidence") == "value",
                "independent deserializations disagreed with captured bytes", checks);
        expect_rejection(
            [&] {
                char* error = nullptr;
                const int rc = sqlite3_exec(
                    first.get(), "CREATE TABLE forbidden(value TEXT);",
                    nullptr, nullptr, &error);
                const std::string reason =
                    error != nullptr ? error : sqlite3_errmsg(first.get());
                sqlite3_free(error);
                if (rc != SQLITE_OK) throw std::runtime_error(reason);
            },
            "readonly", checks);
        require(query_text_nonowning(
                    second.get(), "SELECT value FROM evidence") == "value",
                "failed write contaminated another deserialized connection", checks);
    }
    require(snapshot_staging_entries() == namespace_before,
            "resident seal cleanup mutated /tmp staging state", checks);

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
        ("anonsync_rev0823_snapshot_seal_" + std::to_string(::getpid()));
    std::error_code ignored;
    fs::remove_all(root, ignored);
    fs::create_directory(root);
    try {
        test_exact_capture_and_path_independence(root, checks);
        test_wal_laundering_rejected(root, checks);
        test_quiescent_wal_format_rejected(root, checks);
        test_other_sidecars_and_link_aliases_rejected(root, checks);
        test_live_database_capture(root, checks);
        test_budget_and_resident_deserialization(root, checks);
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
