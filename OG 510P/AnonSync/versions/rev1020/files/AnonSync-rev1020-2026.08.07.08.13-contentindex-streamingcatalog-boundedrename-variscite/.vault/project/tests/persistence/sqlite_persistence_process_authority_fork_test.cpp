#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif
#include "sqlite_busy_handler_owner.hpp"
#include "sqlite_path_security.hpp"
#include "sqlite_snapshot_seal.hpp"
#include "sqlite_verification_budget.hpp"
#include "sync_process_incarnation.hpp"

#include <sqlite3.h>

#include <array>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <new>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#if defined(__linux__)
#include <sched.h>
#include <sys/mount.h>
#endif
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;
using anonsync::SqlitePathFamilyGuard;
using anonsync::SyncSqliteDbHandleSlot;
using anonsync::borrow_sync_sqlite_serialized_db_or_throw;
using anonsync::guard_sqlite_path_family_or_throw;
using anonsync::kSyncProcessCapabilityViolationExitCode;
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_or_throw;
#endif
using anonsync::persistence::SealedSqliteSnapshot;
using anonsync::persistence::SqliteBusyHandlerOwner;
using anonsync::persistence::SqliteVerificationBudget;
using anonsync::persistence::SqliteVerificationBudgetPolicy;

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
            return;
        }
        ++failed;
        std::cerr << "FAIL: " << label << "\n";
    }
};

void sqlite_or_throw(int rc, sqlite3* database, const std::string& operation) {
    if (rc == SQLITE_OK) return;
    const std::string detail =
        database == nullptr ? "SQLite handle unavailable" : sqlite3_errmsg(database);
    const int extended = database == nullptr ? rc : sqlite3_extended_errcode(database);
    throw std::runtime_error(
        operation + ": " + detail + " (rc=" + std::to_string(rc) +
        ", extended=" + std::to_string(extended) + ")");
}

void create_fixture(const fs::path& path) {
    sqlite3* database = nullptr;
    sqlite_or_throw(sqlite3_open_v2(
                        path.c_str(), &database,
                        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                            SQLITE_OPEN_FULLMUTEX,
                        nullptr),
                    database, "fixture open");
    try {
        sqlite_or_throw(sqlite3_exec(
                            database,
                            "CREATE TABLE evidence(value TEXT NOT NULL);"
                            "INSERT INTO evidence(value) VALUES('parent');",
                            nullptr, nullptr, nullptr),
                        database, "fixture schema");
        sqlite_or_throw(sqlite3_close(database), database, "fixture close");
        database = nullptr;
    } catch (...) {
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw;
    }
}

void write_exact_file(const fs::path& path, std::string_view bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error(
            "could not create byte fixture: " + path.generic_string());
    }
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!output) {
        throw std::runtime_error(
            "could not write byte fixture: " + path.generic_string());
    }
}

std::string read_exact_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error(
            "could not open byte fixture: " + path.generic_string());
    }
    input.seekg(0, std::ios::end);
    const std::streamoff size = input.tellg();
    if (size < 0) {
        throw std::runtime_error(
            "could not size byte fixture: " + path.generic_string());
    }
    input.seekg(0, std::ios::beg);
    std::string output(static_cast<std::size_t>(size), '\0');
    input.read(output.data(), static_cast<std::streamsize>(output.size()));
    if (!input && !output.empty()) {
        throw std::runtime_error(
            "could not read byte fixture: " + path.generic_string());
    }
    return output;
}

void open_typed_database_or_throw(SyncSqliteDbHandleSlot& owner,
                                  const fs::path& path,
                                  const std::string& label) {
    const int result = sqlite3_open_v2(
        path.c_str(),
        owner.out(),
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    sqlite_or_throw(result, owner.get(), label);
}

#if defined(__unix__) || defined(__APPLE__)

inline constexpr int kHostileTerminateExitCode = 87;
inline constexpr int kHostileAtExitCode = 88;
inline constexpr int kUnexpectedReturnExitCode = 89;
inline constexpr int kUnexpectedExceptionExitCode = 90;

[[noreturn]] void hostile_terminate_handler() noexcept {
    std::_Exit(kHostileTerminateExitCode);
}

void hostile_atexit_handler() noexcept {
    std::_Exit(kHostileAtExitCode);
}

template <typename Function>
void require_child_fail_stop(TestState& test,
                             Function&& function,
                             const std::string& label) {
    auto child = spawn_inherited_test_process_or_throw(
        [&]() -> int {
            std::set_terminate(hostile_terminate_handler);
            if (std::atexit(hostile_atexit_handler) != 0) {
                return kUnexpectedExceptionExitCode;
            }
            try {
                function();
                return kUnexpectedReturnExitCode;
            } catch (...) {
                return kUnexpectedExceptionExitCode;
            }
        },
        label);
    const int status = child.wait_for_exit(5s, label);
    test.require(WIFEXITED(status) &&
                     WEXITSTATUS(status) == kSyncProcessCapabilityViolationExitCode,
                 label + " fail-stopped before inherited authority was used");
}

template <typename Function>
void require_child_success(TestState& test,
                           Function&& function,
                           const std::string& label) {
    auto child = spawn_inherited_test_process_or_throw(
        [&]() -> int {
            try {
                function();
                return 0;
            } catch (...) {
                return kUnexpectedExceptionExitCode;
            }
        },
        label);
    const int status = child.wait_for_exit(5s, label);
    test.require(WIFEXITED(status) && WEXITSTATUS(status) == 0,
                 label + " completed with child-local authority");
}

void test_path_guard_process_authority(const fs::path& source,
                                       TestState& test) {
    SqlitePathFamilyGuard guard = guard_sqlite_path_family_or_throw(
        source, false, {"-wal", "-shm", "-journal"},
        "process-bound path guard");
    guard.verify_family_or_throw("parent path guard pre-fork");

    require_child_fail_stop(
        test,
        [&] { (void)guard.database_path(); },
        "child cannot inspect an inherited path guard");
    require_child_fail_stop(
        test,
        [&] { guard.verify_family_or_throw("inherited path guard"); },
        "child cannot verify through an inherited path guard");
    require_child_fail_stop(
        test,
        [&] {
            auto* moved = new SqlitePathFamilyGuard(std::move(guard));
            (void)moved;
        },
        "child cannot move an inherited path guard");

    auto* heap_guard = new SqlitePathFamilyGuard(
        guard_sqlite_path_family_or_throw(
            source, false, {}, "heap process-bound path guard"));
    require_child_fail_stop(
        test,
        [&] { delete heap_guard; },
        "child destructor cannot close an inherited path guard owner");
    delete heap_guard;

    guard.verify_family_or_throw("parent path guard post-fork");
    const int descriptor = guard.open_readonly_file_or_throw(
        "parent path guard post-fork descriptor");
    test.require(descriptor >= 0,
                 "parent path guard remains usable after hostile children");
    if (descriptor >= 0) (void)::close(descriptor);
}

void test_descriptor_rooted_sqlite_open(const fs::path& root,
                                        TestState& test) {
#if defined(__linux__)
    const fs::path selected_parent = root / "descriptor-selected";
    const fs::path retained_parent = root / "descriptor-retained";
    const fs::path selected_database = selected_parent / "authority.sqlite";
    fs::create_directories(selected_parent);
    create_fixture(selected_database);

    SqlitePathFamilyGuard guard = guard_sqlite_path_family_or_throw(
        selected_database, false, {"-wal", "-shm", "-journal"},
        "descriptor-rooted SQLite guard");
    auto rooted_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            guard, "descriptor-rooted SQLite VFS");

    const std::string retained_fixture =
        rooted_vfs->read_bounded_main_file_before_open_or_throw(
            16U * 1024U * 1024U,
            "descriptor-rooted retained fixture read");
    test.require(
        retained_fixture.size() >= 100U &&
            std::string_view(retained_fixture.data(), 16U) ==
                std::string_view("SQLite format 3\0", 16U),
        "descriptor-rooted VFS retains a bounded exact SQLite main image");
    rooted_vfs->verify_sidecars_absent_or_throw(
        "descriptor-rooted initial sidecar proof");

    require_child_fail_stop(
        test,
        [&] { (void)rooted_vfs->name(); },
        "child cannot inspect an inherited descriptor-rooted VFS");
    require_child_fail_stop(
        test,
        [&] { rooted_vfs.reset(); },
        "child destructor cannot unregister an inherited descriptor-rooted VFS");

    // SQLite documents a null xOpen name as authority for the VFS to invent a
    // temporary disk pathname. This private VFS must reject that escape hatch;
    // product connections explicitly retain temporary state in memory.
    sqlite3_vfs* const registered_vfs = sqlite3_vfs_find(rooted_vfs->name());
    test.require(
        registered_vfs != nullptr && registered_vfs->xOpen != nullptr &&
            registered_vfs->szOsFile >=
                static_cast<int>(sizeof(sqlite3_file)),
        "descriptor-rooted SQLite VFS is registered for direct policy proof");
    test.require(
        registered_vfs != nullptr && registered_vfs->xDlOpen != nullptr &&
            registered_vfs->xDlError != nullptr &&
            registered_vfs->xDlSym != nullptr &&
            registered_vfs->xDlClose != nullptr &&
            registered_vfs->xSetSystemCall == nullptr &&
            registered_vfs->xGetSystemCall == nullptr &&
            registered_vfs->xNextSystemCall == nullptr,
        "descriptor-rooted VFS narrows dynamic loading and syscall replacement capabilities");
    if (registered_vfs != nullptr && registered_vfs->xDlOpen != nullptr &&
        registered_vfs->xDlError != nullptr) {
        void* const extension = registered_vfs->xDlOpen(
            registered_vfs, "/tmp/anonsync-forbidden-extension.so");
        std::array<char, 256> extension_error{};
        registered_vfs->xDlError(
            registered_vfs, static_cast<int>(extension_error.size()),
            extension_error.data());
        test.require(
            extension == nullptr &&
                std::string_view(extension_error.data()).find(
                    "outside descriptor-rooted authority") !=
                    std::string_view::npos,
            "descriptor-rooted VFS rejects extension loading locally without delegation");
    }
    if (registered_vfs != nullptr && registered_vfs->xOpen != nullptr &&
        registered_vfs->szOsFile >= static_cast<int>(sizeof(sqlite3_file))) {
        void* const storage = ::operator new(
            static_cast<std::size_t>(registered_vfs->szOsFile));
        std::memset(
            storage, 0, static_cast<std::size_t>(registered_vfs->szOsFile));
        auto* const temporary = static_cast<sqlite3_file*>(storage);
        int output_flags = 0;
        const int temporary_result = registered_vfs->xOpen(
            registered_vfs, nullptr, temporary,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_DELETEONCLOSE | SQLITE_OPEN_TEMP_DB,
            &output_flags);
        test.require(
            temporary_result != SQLITE_OK && temporary->pMethods == nullptr,
            "descriptor-rooted SQLite VFS rejects anonymous temporary disk files");
        if (temporary->pMethods != nullptr &&
            temporary->pMethods->xClose != nullptr) {
            (void)temporary->pMethods->xClose(temporary);
        }
        ::operator delete(storage);

        // A named reviewed member must not be allowed to smuggle unlink
        // authority into xClose. SQLite documents DELETEONCLOSE for temp,
        // transient, and subjournal roles, none of which this VFS admits.
        void* const delete_storage = ::operator new(
            static_cast<std::size_t>(registered_vfs->szOsFile));
        std::memset(
            delete_storage, 0,
            static_cast<std::size_t>(registered_vfs->szOsFile));
        auto* const delete_on_close =
            static_cast<sqlite3_file*>(delete_storage);
        output_flags = 0;
        const fs::path journal_path =
            fs::path(selected_database.string() + "-journal");
        const int delete_on_close_result = registered_vfs->xOpen(
            registered_vfs, journal_path.c_str(), delete_on_close,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_DELETEONCLOSE | SQLITE_OPEN_MAIN_JOURNAL,
            &output_flags);
        test.require(
            delete_on_close_result != SQLITE_OK &&
                delete_on_close->pMethods == nullptr &&
                !fs::exists(journal_path),
            "descriptor-rooted SQLite VFS rejects named delete-on-close authority");
        if (delete_on_close->pMethods != nullptr &&
            delete_on_close->pMethods->xClose != nullptr) {
            (void)delete_on_close->pMethods->xClose(delete_on_close);
        }
        ::operator delete(delete_storage);
    }

    // Model the exact preflight/open race the product must close: after the
    // authority has retained and duplicated the selected parent directory,
    // replace its pathname spelling before SQLite consumes the logical name.
    fs::rename(selected_parent, retained_parent);
    fs::create_directories(selected_parent);

    test.require(
        rooted_vfs->read_bounded_main_file_before_open_or_throw(
            16U * 1024U * 1024U,
            "descriptor-rooted post-rename fixture read") == retained_fixture,
        "descriptor-rooted retained read ignores ambient parent rebinding");
    rooted_vfs->verify_sidecars_absent_or_throw(
        "descriptor-rooted post-rename sidecar proof");

    // A same-spelled logical path is not sufficient authority. Prove that a
    // decoy connection opened through the default VFS is rejected by this
    // registration's exact VFS-pointer and wrapper-state attestation.
    create_fixture(selected_database);
    sqlite3* wrong_vfs_database = nullptr;
    sqlite_or_throw(
        sqlite3_open_v2(
            selected_database.c_str(), &wrong_vfs_database,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                SQLITE_OPEN_NOFOLLOW,
            nullptr),
        wrong_vfs_database, "same-path wrong-VFS fixture open");
    bool wrong_vfs_rejected = false;
    try {
        rooted_vfs->verify_open_database_or_throw(
            wrong_vfs_database, "same-path wrong-VFS attestation");
    } catch (const std::runtime_error& error) {
        wrong_vfs_rejected =
            std::string(error.what()).find("exact private VFS") !=
            std::string::npos;
    }
    test.require(
        wrong_vfs_rejected,
        "descriptor-rooted attestation rejects a same-path default-VFS connection");
    sqlite_or_throw(
        sqlite3_close(wrong_vfs_database), wrong_vfs_database,
        "same-path wrong-VFS fixture close");
    wrong_vfs_database = nullptr;
    fs::remove(selected_database);

    sqlite3* database = nullptr;
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                      SQLITE_OPEN_NOFOLLOW;
    const int open_result = sqlite3_open_v2(
        selected_database.c_str(), &database, flags, rooted_vfs->name());
    sqlite_or_throw(
        open_result, database, "descriptor-rooted SQLite open");
    try {
        rooted_vfs->verify_open_database_or_throw(
            database, "descriptor-rooted exact VFS attestation");
        test.require(
            true,
            "descriptor-rooted attestation binds the live connection to its exact private VFS");
        const char* const logical_filename =
            sqlite3_db_filename(database, "main");
        test.require(
            logical_filename != nullptr &&
                std::string_view(logical_filename) ==
                    selected_database.generic_string(),
            "descriptor-rooted VFS preserves the deployment logical pathname");

        char* ambient_temporary_filename = nullptr;
        const int temporary_filename_control = sqlite3_file_control(
            database, "main", SQLITE_FCNTL_TEMPFILENAME,
            &ambient_temporary_filename);
        test.require(
            temporary_filename_control == SQLITE_NOTFOUND &&
                ambient_temporary_filename == nullptr,
            "descriptor-rooted xFileControl denies ambient temporary-filename generation");
        if (ambient_temporary_filename != nullptr) {
            sqlite3_free(ambient_temporary_filename);
            ambient_temporary_filename = nullptr;
        }

        const int null_io_control = sqlite3_file_control(
            database, "main", SQLITE_FCNTL_NULL_IO, nullptr);
        test.require(
            null_io_control == SQLITE_NOTFOUND,
            "descriptor-rooted xFileControl denies delegated NULL_IO descriptor invalidation");

        constexpr char kForbiddenLockProxy[] =
            "/tmp/anonsync-forbidden-lock-proxy";
        const int lock_proxy_control = sqlite3_file_control(
            database, "main", SQLITE_FCNTL_SET_LOCKPROXYFILE,
            const_cast<char*>(kForbiddenLockProxy));
        test.require(
            lock_proxy_control == SQLITE_NOTFOUND &&
                !fs::exists(kForbiddenLockProxy),
            "descriptor-rooted xFileControl denies lock-proxy pathname authority");

        sqlite3_file* rooted_main_file = nullptr;
        sqlite_or_throw(
            sqlite3_file_control(
                database, "main", SQLITE_FCNTL_FILE_POINTER,
                &rooted_main_file),
            database, "descriptor-rooted malformed file-control fixture");
        test.require(
            rooted_main_file != nullptr && rooted_main_file->pMethods != nullptr &&
                rooted_main_file->pMethods->xFileControl != nullptr,
            "descriptor-rooted main handle exposes the reviewed file-control boundary");
        if (rooted_main_file != nullptr &&
            rooted_main_file->pMethods != nullptr &&
            rooted_main_file->pMethods->xFileControl != nullptr) {
            const int malformed_control =
                rooted_main_file->pMethods->xFileControl(
                    rooted_main_file, SQLITE_FCNTL_LOCKSTATE, nullptr);
            test.require(
                malformed_control == SQLITE_MISUSE,
                "descriptor-rooted xFileControl rejects malformed null arguments before Unix VFS delegation");
        }

        sqlite_or_throw(
            sqlite3_exec(
                database, "SELECT count(*) FROM evidence;", nullptr, nullptr,
                nullptr),
            database, "descriptor-rooted post-NULL_IO usability proof");
        test.require(
            true,
            "denied NULL_IO leaves the attested SQLite descriptor usable");

        sqlite3_stmt* statement = nullptr;
        sqlite_or_throw(
            sqlite3_prepare_v2(
                database, "SELECT value FROM evidence ORDER BY rowid;", -1,
                &statement, nullptr),
            database, "descriptor-rooted SQLite query prepare");
        const int row = sqlite3_step(statement);
        if (row != SQLITE_ROW) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error(
                "descriptor-rooted SQLite query returned no row");
        }
        const unsigned char* const text = sqlite3_column_text(statement, 0);
        const std::string value =
            text == nullptr ? std::string() :
                              reinterpret_cast<const char*>(text);
        sqlite_or_throw(
            sqlite3_finalize(statement), database,
            "descriptor-rooted SQLite query finalize");
        if (value != "parent") {
            throw std::runtime_error(
                "descriptor-rooted SQLite open reached the wrong database");
        }

        // Force a rollback-journal family member through xOpen/xAccess/xDelete.
        // The commit must mutate only the retained directory object, never the
        // fresh replacement now occupying the approved pathname spelling.
        sqlite_or_throw(
            sqlite3_exec(
                database,
                "BEGIN IMMEDIATE;"
                "INSERT INTO evidence(value) VALUES('retained-write');"
                "COMMIT;",
                nullptr, nullptr, nullptr),
            database, "descriptor-rooted SQLite journaled write");

        // Exercise exact-image evidence while SQLite retains a rollback-mode
        // read lock. The read and sync use SQLite's existing main file object;
        // no independent same-inode descriptor is opened or closed at this
        // boundary, preserving POSIX process-lock semantics.
        sqlite_or_throw(
            sqlite3_exec(
                database,
                "BEGIN; SELECT count(*) FROM evidence;",
                nullptr, nullptr, nullptr),
            database, "descriptor-rooted SQLite durability read pin");
        const std::string pinned_image =
            rooted_vfs->read_bounded_main_file_or_throw(
                database, 16U * 1024U * 1024U,
                "descriptor-rooted pinned main read");
        test.require(
            pinned_image.size() >= retained_fixture.size(),
            "descriptor-rooted live SQLite file remains readable under SQLite lock");
        rooted_vfs->sync_main_file_and_parent_directory_or_throw(
            database, "descriptor-rooted pinned durability flush");
        sqlite_or_throw(
            sqlite3_exec(database, "COMMIT;", nullptr, nullptr, nullptr),
            database, "descriptor-rooted SQLite durability read release");

        test.require(
            !fs::exists(selected_database),
            "descriptor-rooted SQLite open created nothing in replacement parent");
        test.require(
            !fs::exists(fs::path(selected_database.string() + "-journal")),
            "descriptor-rooted SQLite journal never entered replacement parent");
        test.require(
            fs::exists(retained_parent / "authority.sqlite"),
            "descriptor-rooted SQLite open retained the approved parent object");

        // Move the already-retained directory again after the connection is
        // live, then install a same-named decoy. WAL and shared-memory activity
        // must continue through the directory descriptor rather than either
        // ambient spelling.
        const fs::path retained_again = root / "descriptor-retained-again";
        fs::rename(retained_parent, retained_again);
        fs::create_directories(retained_parent);
        create_fixture(retained_parent / "authority.sqlite");
        sqlite_or_throw(
            sqlite3_exec(
                database,
                "PRAGMA main.journal_mode=WAL;"
                "BEGIN IMMEDIATE;"
                "INSERT INTO evidence(value) VALUES('descriptor-wal');"
                "COMMIT;",
                nullptr, nullptr, nullptr),
            database, "descriptor-rooted SQLite WAL write");
        test.require(
            fs::exists(retained_again / "authority.sqlite-wal"),
            "descriptor-rooted WAL remains in the twice-renamed parent object");
        test.require(
            fs::exists(retained_again / "authority.sqlite-shm"),
            "descriptor-rooted shared memory remains in the retained parent object");
        test.require(
            !fs::exists(retained_parent / "authority.sqlite-wal") &&
                !fs::exists(retained_parent / "authority.sqlite-shm"),
            "descriptor-rooted WAL family never enters a same-named decoy parent");
        test.require(
            !fs::exists(fs::path(selected_database.string() + "-wal")) &&
                !fs::exists(fs::path(selected_database.string() + "-shm")),
            "descriptor-rooted WAL family never enters the logical-path replacement");

        test.require(
            rooted_vfs->read_bounded_main_file_or_throw(
                database, 16U * 1024U * 1024U,
                "descriptor-rooted twice-renamed main read").size() >= 100U,
            "descriptor-rooted retained main survives repeated ancestor renames");
        rooted_vfs->verify_open_database_or_throw(
            database, "descriptor-rooted twice-renamed VFS attestation");
        test.require(
            true,
            "exact private-VFS attestation survives ambient ancestor rebinding");

        bool replacement_detected = false;
        try {
            guard.verify_open_database_or_throw(
                database,
                "descriptor-rooted SQLite post-replacement attestation");
        } catch (const std::runtime_error& error) {
            replacement_detected =
                std::string(error.what()).find(
                    "parent directory identity changed") != std::string::npos;
        }
        test.require(
            replacement_detected,
            "descriptor-rooted open is safe but later pathname replacement revokes authority");

        sqlite_or_throw(
            sqlite3_close(database), database,
            "descriptor-rooted SQLite close");
        database = nullptr;
    } catch (...) {
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw;
    }

    // The wrapper still delegates SQLITE_OPEN_NOFOLLOW to the Unix VFS for
    // every final family member. Replacing the bound main file with a symlink
    // must therefore fail closed instead of following it through procfs.
    const fs::path symlink_parent = root / "descriptor-symlink";
    const fs::path symlink_database = symlink_parent / "authority.sqlite";
    const fs::path external_database = root / "descriptor-external.sqlite";
    fs::create_directories(symlink_parent);
    create_fixture(symlink_database);
    create_fixture(external_database);
    SqlitePathFamilyGuard symlink_guard = guard_sqlite_path_family_or_throw(
        symlink_database, false, {"-wal", "-shm", "-journal"},
        "descriptor-rooted final-symlink guard");
    auto symlink_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            symlink_guard, "descriptor-rooted final-symlink VFS");
    fs::rename(symlink_database, symlink_parent / "approved.sqlite");
    fs::create_symlink(external_database, symlink_database);

    sqlite3* rejected = nullptr;
    const int rejected_result = sqlite3_open_v2(
        symlink_database.c_str(), &rejected, flags, symlink_vfs->name());
    test.require(
        rejected_result != SQLITE_OK,
        "descriptor-rooted SQLite VFS rejects a replaced main-file symlink");
    if (rejected != nullptr) (void)sqlite3_close_v2(rejected);

    // O_NOFOLLOW alone does not reject a same-directory regular-file swap.
    // The retained main inode and HAS_MOVED attestation must prevent SQLite
    // from opening a different regular database under the approved spelling.
    const fs::path regular_parent = root / "descriptor-regular-replacement";
    const fs::path regular_database = regular_parent / "authority.sqlite";
    fs::create_directories(regular_parent);
    create_fixture(regular_database);
    SqlitePathFamilyGuard regular_guard = guard_sqlite_path_family_or_throw(
        regular_database, false, {"-wal", "-shm", "-journal"},
        "descriptor-rooted regular-replacement guard");
    auto regular_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            regular_guard, "descriptor-rooted regular-replacement VFS");
    const fs::path approved_database = regular_parent / "approved.sqlite";
    fs::rename(regular_database, approved_database);
    create_fixture(regular_database);

    sqlite3* regular_rejected = nullptr;
    const int regular_rejected_result = sqlite3_open_v2(
        regular_database.c_str(), &regular_rejected, flags,
        regular_vfs->name());
    test.require(
        regular_rejected_result != SQLITE_OK,
        "descriptor-rooted SQLite VFS rejects a replaced regular main file");
    if (regular_rejected != nullptr) {
        (void)sqlite3_close_v2(regular_rejected);
    }
    test.require(
        fs::exists(approved_database),
        "regular-file replacement rejection preserves the approved main inode");

    // The guard rejects multiply-linked members at registration, but a family
    // name can be replaced afterward. O_NOFOLLOW does not reject hard links,
    // so every VFS callback must independently fail closed before delegation.
    const fs::path hardlink_parent = root / "descriptor-hardlink-family";
    const fs::path hardlink_database = hardlink_parent / "authority.sqlite";
    fs::create_directories(hardlink_parent);
    create_fixture(hardlink_database);
    SqlitePathFamilyGuard hardlink_guard = guard_sqlite_path_family_or_throw(
        hardlink_database, false, {"-wal", "-shm", "-journal"},
        "descriptor-rooted hardlink guard");
    auto hardlink_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            hardlink_guard, "descriptor-rooted hardlink VFS");
    sqlite3_vfs* const hardlink_registered =
        sqlite3_vfs_find(hardlink_vfs->name());
    test.require(
        hardlink_registered != nullptr &&
            hardlink_registered->xOpen != nullptr &&
            hardlink_registered->xAccess != nullptr &&
            hardlink_registered->xDelete != nullptr,
        "hardlink adversary reaches the registered descriptor-rooted callbacks");

    constexpr std::string_view kForeignJournalBytes =
        "foreign-journal-target-must-remain-byte-exact";
    const fs::path foreign_journal = root / "foreign-journal-target.bin";
    const fs::path journal_name =
        fs::path(hardlink_database.string() + "-journal");
    write_exact_file(foreign_journal, kForeignJournalBytes);
    fs::create_hard_link(foreign_journal, journal_name);
    if (hardlink_registered != nullptr &&
        hardlink_registered->xOpen != nullptr) {
        void* const storage = ::operator new(
            static_cast<std::size_t>(hardlink_registered->szOsFile));
        std::memset(
            storage, 0,
            static_cast<std::size_t>(hardlink_registered->szOsFile));
        auto* const journal = static_cast<sqlite3_file*>(storage);
        int output_flags = 0;
        const int journal_result = hardlink_registered->xOpen(
            hardlink_registered, journal_name.c_str(), journal,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_MAIN_JOURNAL,
            &output_flags);
        test.require(
            journal_result != SQLITE_OK && journal->pMethods == nullptr,
            "descriptor-rooted xOpen rejects a multiply-linked rollback journal");
        if (journal->pMethods != nullptr &&
            journal->pMethods->xClose != nullptr) {
            (void)journal->pMethods->xClose(journal);
        }
        ::operator delete(storage);
    }
    int access_result = 1;
    const int access_code = hardlink_registered == nullptr
        ? SQLITE_ERROR
        : hardlink_registered->xAccess(
              hardlink_registered, journal_name.c_str(), SQLITE_ACCESS_EXISTS,
              &access_result);
    test.require(
        access_code != SQLITE_OK && access_result == 0,
        "descriptor-rooted xAccess refuses a multiply-linked family member");
    const int delete_code = hardlink_registered == nullptr
        ? SQLITE_ERROR
        : hardlink_registered->xDelete(
              hardlink_registered, journal_name.c_str(), 0);
    test.require(
        delete_code != SQLITE_OK && fs::exists(journal_name),
        "descriptor-rooted xDelete preserves a multiply-linked foreign target");
    test.require(
        read_exact_file(foreign_journal) == kForeignJournalBytes,
        "journal hardlink rejection leaves foreign bytes unchanged");
    fs::remove(journal_name);

    sqlite3* hardlink_database_handle = nullptr;
    sqlite_or_throw(
        sqlite3_open_v2(
            hardlink_database.c_str(), &hardlink_database_handle, flags,
            hardlink_vfs->name()),
        hardlink_database_handle, "hardlink shared-memory main open");
    hardlink_vfs->verify_open_database_or_throw(
        hardlink_database_handle, "hardlink shared-memory main attestation");
    constexpr std::string_view kForeignShmBytes =
        "foreign-shm-target-must-remain-byte-exact";
    const fs::path foreign_shm = root / "foreign-shm-target.bin";
    const fs::path shm_name = fs::path(hardlink_database.string() + "-shm");
    write_exact_file(foreign_shm, kForeignShmBytes);
    fs::create_hard_link(foreign_shm, shm_name);
    sqlite3_file* main_file = nullptr;
    sqlite_or_throw(
        sqlite3_file_control(
            hardlink_database_handle, "main", SQLITE_FCNTL_FILE_POINTER,
            &main_file),
        hardlink_database_handle, "hardlink shared-memory main pointer");
    void volatile* mapping = reinterpret_cast<void volatile*>(1U);
    const int shm_result =
        main_file == nullptr || main_file->pMethods == nullptr ||
                main_file->pMethods->xShmMap == nullptr
            ? SQLITE_ERROR
            : main_file->pMethods->xShmMap(
                  main_file, 0, 32768, 1, &mapping);
    test.require(
        shm_result == SQLITE_IOERR_SHMOPEN && mapping == nullptr,
        "descriptor-rooted xShmMap rejects multiply-linked shared memory before Unix open");
    test.require(
        read_exact_file(foreign_shm) == kForeignShmBytes,
        "shared-memory hardlink rejection leaves foreign bytes unchanged");
    fs::remove(shm_name);
    sqlite_or_throw(
        sqlite3_close(hardlink_database_handle), hardlink_database_handle,
        "hardlink shared-memory main close");
    hardlink_database_handle = nullptr;

    // xClose in the delegated Unix VFS may retire a -shm pathname. A hostile
    // hard-link replacement after the last ordinary operation must therefore
    // fail-stop before xClose can unlink the reviewed family name or mutate an
    // unrelated target. The child proves that process teardown, rather than a
    // pathname-capable SQLite callback, releases the remaining descriptors.
    constexpr std::string_view kForeignCloseShmBytes =
        "foreign-close-shm-target-must-remain-byte-exact";
    const fs::path close_parent = root / "descriptor-close-hardlink";
    const fs::path close_database = close_parent / "authority.sqlite";
    const fs::path close_shm =
        fs::path(close_database.string() + "-shm");
    const fs::path foreign_close_shm =
        root / "foreign-close-shm-target.bin";
    write_exact_file(foreign_close_shm, kForeignCloseShmBytes);
    require_child_fail_stop(
        test,
        [&] {
            fs::create_directories(close_parent);
            create_fixture(close_database);
            SqlitePathFamilyGuard close_guard =
                guard_sqlite_path_family_or_throw(
                    close_database, false, {"-wal", "-shm", "-journal"},
                    "descriptor-rooted close hardlink guard");
            auto close_vfs =
                anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
                    close_guard, "descriptor-rooted close hardlink VFS");
            sqlite3* close_handle = nullptr;
            sqlite_or_throw(
                sqlite3_open_v2(
                    close_database.c_str(), &close_handle, flags,
                    close_vfs->name()),
                close_handle, "descriptor-rooted close hardlink main open");
            close_vfs->verify_open_database_or_throw(
                close_handle,
                "descriptor-rooted close hardlink main attestation");
            fs::create_hard_link(foreign_close_shm, close_shm);
            (void)sqlite3_close(close_handle);
        },
        "descriptor-rooted xClose rejects unsafe shared-memory replacement");
    test.require(
        fs::exists(close_shm),
        "descriptor-rooted xClose fail-stop preserves the hostile shared-memory name");
    test.require(
        read_exact_file(foreign_close_shm) == kForeignCloseShmBytes,
        "descriptor-rooted xClose fail-stop leaves foreign bytes unchanged");
    fs::remove(close_shm);
#else
    (void)root;
    test.require(
        true,
        "descriptor-rooted SQLite open proof requires Linux procfs");
#endif
}


struct ExactFileObservation final {
    std::string bytes;
    std::uint64_t device = 0U;
    std::uint64_t inode = 0U;
    std::uint64_t size = 0U;
    std::uint64_t links = 0U;
    std::uint32_t mode = 0U;
    std::int64_t modified_seconds = 0;
    std::int64_t modified_nanoseconds = 0;
    std::int64_t changed_seconds = 0;
    std::int64_t changed_nanoseconds = 0;

    [[nodiscard]] bool operator==(
        const ExactFileObservation&) const noexcept = default;
};

[[nodiscard]] ExactFileObservation observe_exact_file_or_throw(
    const fs::path& path,
    const std::string& label) {
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0) {
        throw std::runtime_error(
            label + " lstat failed: " + std::strerror(errno));
    }
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label + " is not a regular file");
    }
    ExactFileObservation observed;
    observed.bytes = read_exact_file(path);
    observed.device = static_cast<std::uint64_t>(status.st_dev);
    observed.inode = static_cast<std::uint64_t>(status.st_ino);
    observed.size = static_cast<std::uint64_t>(status.st_size);
    observed.links = static_cast<std::uint64_t>(status.st_nlink);
    observed.mode = static_cast<std::uint32_t>(status.st_mode);
#if defined(__APPLE__)
    observed.modified_seconds = status.st_mtimespec.tv_sec;
    observed.modified_nanoseconds = status.st_mtimespec.tv_nsec;
    observed.changed_seconds = status.st_ctimespec.tv_sec;
    observed.changed_nanoseconds = status.st_ctimespec.tv_nsec;
#else
    observed.modified_seconds = status.st_mtim.tv_sec;
    observed.modified_nanoseconds = status.st_mtim.tv_nsec;
    observed.changed_seconds = status.st_ctim.tv_sec;
    observed.changed_nanoseconds = status.st_ctim.tv_nsec;
#endif
    if (observed.size != observed.bytes.size()) {
        throw std::runtime_error(label + " changed while it was observed");
    }
    return observed;
}

struct SqliteFamilyObservation final {
    std::array<std::optional<ExactFileObservation>, 4U> members;

    [[nodiscard]] bool operator==(
        const SqliteFamilyObservation&) const noexcept = default;
};

[[nodiscard]] SqliteFamilyObservation observe_sqlite_family_or_throw(
    const fs::path& main_path,
    const std::string& label) {
    const std::array<fs::path, 4U> paths{{
        main_path,
        fs::path(main_path.string() + "-journal"),
        fs::path(main_path.string() + "-wal"),
        fs::path(main_path.string() + "-shm"),
    }};
    SqliteFamilyObservation observation;
    for (std::size_t index = 0U; index < paths.size(); ++index) {
        struct stat status {};
        if (::lstat(paths[index].c_str(), &status) != 0) {
            if (errno == ENOENT) continue;
            throw std::runtime_error(
                label + " could not inspect " + paths[index].generic_string() +
                ": " + std::strerror(errno));
        }
        observation.members[index] = observe_exact_file_or_throw(
            paths[index], label + " member " + std::to_string(index));
    }
    return observation;
}

void create_persistent_wal_fixture(const fs::path& path) {
    sqlite3* database = nullptr;
    sqlite_or_throw(
        sqlite3_open_v2(
            path.c_str(), &database,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX,
            nullptr),
        database, "forensic WAL fixture open");
    try {
        sqlite_or_throw(
            sqlite3_exec(
                database,
                "PRAGMA journal_mode=WAL;"
                "PRAGMA wal_autocheckpoint=0;"
                "CREATE TABLE evidence(value TEXT NOT NULL);"
                "INSERT INTO evidence(value) VALUES('main-and-wal');"
                "INSERT INTO evidence(value) VALUES('retained-wal');",
                nullptr, nullptr, nullptr),
            database, "forensic WAL fixture populate");
#ifdef SQLITE_FCNTL_PERSIST_WAL
        int persist_wal = 1;
        sqlite_or_throw(
            sqlite3_file_control(
                database, "main", SQLITE_FCNTL_PERSIST_WAL, &persist_wal),
            database, "forensic WAL fixture persistence control");
#endif
        sqlite_or_throw(
            sqlite3_close(database), database,
            "forensic WAL fixture close");
        database = nullptr;
    } catch (...) {
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw;
    }
    if (!fs::exists(fs::path(path.string() + "-wal"))) {
        throw std::runtime_error(
            "forensic WAL fixture did not retain a WAL sidecar");
    }
}

void test_descriptor_rooted_forensic_read_only_authority(
    const fs::path& root,
    TestState& test) {
#if defined(__linux__)
    const fs::path parent = root / "descriptor-forensic";
    const fs::path database_path = parent / "authority.sqlite";
    fs::create_directories(parent);
    create_persistent_wal_fixture(database_path);
    constexpr std::string_view kRetainedSharedMemorySentinel =
        "retained-shm-path-must-remain-byte-exact";
    write_exact_file(
        fs::path(database_path.string() + "-shm"),
        kRetainedSharedMemorySentinel);

    const SqliteFamilyObservation before = observe_sqlite_family_or_throw(
        database_path, "forensic family before observation");
    test.require(
        before.members[0U].has_value() && before.members[2U].has_value() &&
            before.members[3U].has_value(),
        "forensic fixture retains main, WAL, and an independently preserved shared-memory name");

    SqlitePathFamilyGuard guard = guard_sqlite_path_family_or_throw(
        database_path, false, {"-journal", "-wal", "-shm"},
        "forensic descriptor-rooted guard");
    auto rooted_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            guard,
            anonsync::SqliteDescriptorRootedVfsAccess::ReadOnlyExisting,
            "forensic descriptor-rooted VFS");

    sqlite3_vfs* const registered = sqlite3_vfs_find(rooted_vfs->name());
    test.require(
        registered != nullptr && registered->xAccess != nullptr &&
            registered->xDelete != nullptr,
        "forensic VFS exposes its reviewed access and deletion boundaries");
    if (registered != nullptr && registered->xAccess != nullptr) {
        int writable = 1;
        const int access_result = registered->xAccess(
            registered, database_path.c_str(), SQLITE_ACCESS_READWRITE,
            &writable);
        test.require(
            access_result == SQLITE_OK && writable == 0,
            "forensic VFS never advertises writable deployment authority");
    }
    if (registered != nullptr && registered->xDelete != nullptr) {
        const int delete_result = registered->xDelete(
            registered, database_path.c_str(), 1);
        test.require(
            delete_result == SQLITE_READONLY && fs::exists(database_path),
            "forensic VFS denies main-database deletion");
    }

    sqlite3* database = nullptr;
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX |
                SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    sqlite_or_throw(
        sqlite3_open_v2(
            database_path.c_str(), &database, flags, rooted_vfs->name()),
        database, "forensic descriptor-rooted open");
    try {
        rooted_vfs->verify_open_database_or_throw(
            database, "forensic exact private-VFS attestation");
        test.require(
            sqlite3_db_readonly(database, "main") == 1,
            "forensic connection remains logically read-only despite its lock-capable main descriptor");

        sqlite_or_throw(
            sqlite3_exec(
                database,
                "PRAGMA locking_mode=EXCLUSIVE;"
                "PRAGMA query_only=ON;"
                "PRAGMA temp_store=MEMORY;"
                "PRAGMA trusted_schema=OFF;",
                nullptr, nullptr, nullptr),
            database, "forensic connection profile");

        sqlite3_stmt* statement = nullptr;
        sqlite_or_throw(
            sqlite3_prepare_v2(
                database,
                "SELECT count(*), max(value) FROM evidence;", -1,
                &statement, nullptr),
            database, "forensic WAL replay prepare");
        const int row = sqlite3_step(statement);
        if (row != SQLITE_ROW) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error(
                "forensic WAL replay query returned no row");
        }
        const std::uint64_t count = static_cast<std::uint64_t>(
            sqlite3_column_int64(statement, 0));
        const unsigned char* const maximum_text =
            sqlite3_column_text(statement, 1);
        const std::string maximum = maximum_text == nullptr
            ? std::string()
            : reinterpret_cast<const char*>(maximum_text);
        sqlite_or_throw(
            sqlite3_finalize(statement), database,
            "forensic WAL replay finalize");
        test.require(
            count == 2U && maximum == "retained-wal",
            "forensic observer replays committed WAL bytes from its anonymous private snapshot");

        sqlite3_file* main_file = nullptr;
        sqlite_or_throw(
            sqlite3_file_control(
                database, "main", SQLITE_FCNTL_FILE_POINTER, &main_file),
            database, "forensic main-file pointer");
        test.require(
            main_file != nullptr && main_file->pMethods != nullptr &&
                main_file->pMethods->iVersion == 1 &&
                main_file->pMethods->xShmMap == nullptr &&
                main_file->pMethods->xFetch == nullptr,
            "forensic main handle structurally exposes neither shared-memory nor mmap authority");
        if (main_file != nullptr && main_file->pMethods != nullptr) {
            const char hostile = 'X';
            test.require(
                main_file->pMethods->xWrite(
                    main_file, &hostile, 1, 0) == SQLITE_READONLY,
                "forensic main handle denies direct byte writes");
            test.require(
                main_file->pMethods->xTruncate(main_file, 0) ==
                    SQLITE_READONLY,
                "forensic main handle denies direct truncation");
            test.require(
                main_file->pMethods->xSync(
                    main_file, SQLITE_SYNC_FULL) == SQLITE_OK,
                "forensic main sync is a non-synchronizing no-op");
#ifdef SQLITE_FCNTL_SIZE_HINT
            sqlite3_int64 size_hint = 0;
            test.require(
                main_file->pMethods->xFileControl(
                    main_file, SQLITE_FCNTL_SIZE_HINT, &size_hint) ==
                    SQLITE_NOTFOUND,
                "forensic file-control allowlist denies mutating size hints");
#endif
        }

        char* error_message = nullptr;
        const int write_result = sqlite3_exec(
            database,
            "INSERT INTO evidence(value) VALUES('forbidden');",
            nullptr, nullptr, &error_message);
        sqlite3_free(error_message);
        test.require(
            write_result == SQLITE_READONLY,
            "forensic SQL connection rejects mutation before any deployment write");

        sqlite_or_throw(
            sqlite3_close(database), database,
            "forensic descriptor-rooted close");
        database = nullptr;
    } catch (...) {
        if (database != nullptr) (void)sqlite3_close_v2(database);
        throw;
    }
    rooted_vfs.reset();

    const SqliteFamilyObservation after = observe_sqlite_family_or_throw(
        database_path, "forensic family after observation");
    test.require(
        after == before,
        "forensic WAL observation preserves exact family bytes, identities, links, modes, sizes, mtimes, and ctimes");
#else
    (void)root;
    test.require(
        true,
        "descriptor-rooted forensic read-only proof unavailable on this platform");
#endif
}

void test_descriptor_rooted_auxiliary_close_preserves_locks(
    const fs::path& root,
    TestState& test) {
#if defined(__linux__)
    const fs::path parent = root / "descriptor-auxiliary-close-lock";
    const fs::path database_path = parent / "authority.sqlite";
    fs::create_directories(parent);
    create_fixture(database_path);

    SqlitePathFamilyGuard primary_guard = guard_sqlite_path_family_or_throw(
        database_path, false, {"-wal", "-shm", "-journal"},
        "primary lock-preservation guard");
    auto primary_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            primary_guard, "primary lock-preservation VFS");

    SqlitePathFamilyGuard auxiliary_guard = guard_sqlite_path_family_or_throw(
        database_path, false, {"-wal", "-shm", "-journal"},
        "auxiliary lock-preservation guard");
    auto auxiliary_vfs =
        anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
            auxiliary_guard, "auxiliary lock-preservation VFS");

    sqlite3* database = nullptr;
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                      SQLITE_OPEN_NOFOLLOW;
    sqlite_or_throw(
        sqlite3_open_v2(
            database_path.c_str(), &database, flags, primary_vfs->name()),
        database, "primary lock-preservation open");
    try {
        primary_vfs->verify_open_database_or_throw(
            database, "primary lock-preservation attestation");
        sqlite_or_throw(
            sqlite3_exec(
                database, "BEGIN IMMEDIATE;", nullptr, nullptr, nullptr),
            database, "primary reserved-lock acquisition");

        // SQLite's rollback-mode RESERVED lock is the one-byte POSIX lock at
        // PENDING_BYTE+1. F_GETLK from a fork child observes the kernel state
        // without running SQLite or destructing inherited C++ authority.
        constexpr off_t kSqliteReservedByte =
            static_cast<off_t>(0x40000000ULL + 1ULL);
        const auto require_reserved_lock_state =
            [&](bool expected_locked, const std::string& label) {
                require_child_success(
                    test,
                    [&] {
                        int open_flags = O_RDWR;
#ifdef O_CLOEXEC
                        open_flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
                        open_flags |= O_NOFOLLOW;
#endif
                        const int descriptor =
                            ::open(database_path.c_str(), open_flags);
                        if (descriptor < 0) {
                            throw std::runtime_error(
                                "reserved-lock probe could not open database");
                        }
                        struct flock requested {};
                        requested.l_type = F_WRLCK;
                        requested.l_whence = SEEK_SET;
                        requested.l_start = kSqliteReservedByte;
                        requested.l_len = 1;
                        const int result =
                            ::fcntl(descriptor, F_GETLK, &requested);
                        const int saved_errno = errno;
                        (void)::close(descriptor);
                        if (result != 0) {
                            throw std::runtime_error(
                                "reserved-lock F_GETLK failed: " +
                                std::string(std::strerror(saved_errno)));
                        }
                        const bool observed_locked =
                            requested.l_type != F_UNLCK;
                        if (observed_locked != expected_locked) {
                            throw std::runtime_error(
                                expected_locked
                                    ? "SQLite RESERVED lock disappeared from the kernel"
                                    : "SQLite RESERVED lock remained after rollback and close");
                        }
                    },
                    label);
            };

        require_reserved_lock_state(
            true,
            "primary SQLite RESERVED lock is present before auxiliary inspection");

        // The only safe pre-open image read is another Unix-VFS file object:
        // unixClose defers its descriptor close while any same-inode POSIX lock
        // remains in this process. A raw open/read/close sequence would revoke
        // the primary connection's RESERVED lock.
        test.require(
            auxiliary_vfs->read_bounded_main_file_before_open_or_throw(
                16U * 1024U * 1024U,
                "auxiliary lock-preserving pre-open read").size() >= 100U,
            "auxiliary VFS pre-open read uses SQLite lock-aware close semantics");
        require_reserved_lock_state(
            true,
            "auxiliary pre-open read preserves the primary SQLite RESERVED lock");

        bool bounded_read_rejected = false;
        try {
            (void)auxiliary_vfs->read_bounded_main_file_before_open_or_throw(
                1U, "auxiliary lock-preserving rejected pre-open read");
        } catch (const std::runtime_error& error) {
            bounded_read_rejected =
                std::string(error.what()).find("exceeds the byte limit") !=
                std::string::npos;
        }
        test.require(
            bounded_read_rejected,
            "auxiliary VFS rejects an undersized pre-open read limit");
        require_reserved_lock_state(
            true,
            "failed auxiliary pre-open read cleanup preserves the primary SQLite RESERVED lock");

        // A private VFS with no connection must own no main-database descriptor.
        // On POSIX, closing any independent descriptor for this inode here would
        // discard the primary connection's process-scoped SQLite locks.
        auxiliary_vfs.reset();

        require_reserved_lock_state(
            true,
            "auxiliary VFS teardown preserves the primary SQLite RESERVED lock");
        sqlite_or_throw(
            sqlite3_exec(database, "ROLLBACK;", nullptr, nullptr, nullptr),
            database, "primary reserved-lock release");
        sqlite_or_throw(
            sqlite3_close(database), database,
            "primary lock-preservation close");
        database = nullptr;
        require_reserved_lock_state(
            false,
            "rollback and primary close release the SQLite RESERVED lock");
    } catch (...) {
        if (database != nullptr) {
            (void)sqlite3_exec(
                database, "ROLLBACK;", nullptr, nullptr, nullptr);
            (void)sqlite3_close_v2(database);
        }
        throw;
    }
#else
    (void)root;
    test.require(
        true,
        "auxiliary VFS lock-preservation proof requires Linux POSIX locks");
#endif
}

void test_descriptor_rooted_mount_namespace_authority(
    const fs::path& root,
    TestState& test) {
#if defined(__linux__)
    auto child = spawn_inherited_test_process_or_throw(
        [&]() -> int {
            try {
                const fs::path parent = root / "descriptor-mount-namespace";
                const fs::path database = parent / "authority.sqlite";
                fs::create_directories(parent);
                create_fixture(database);
                SqlitePathFamilyGuard guard =
                    guard_sqlite_path_family_or_throw(
                        database, false, {"-wal", "-shm", "-journal"},
                        "mount-namespace descriptor-rooted guard");
                auto rooted_vfs =
                    anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
                        guard, "mount-namespace descriptor-rooted VFS");
                if (::unshare(CLONE_NEWUSER | CLONE_NEWNS) != 0) {
                    if (errno == EPERM || errno == EINVAL || errno == ENOSYS) {
                        return 77;
                    }
                    return 78;
                }
                // name() is noexcept because inherited-VFS misuse is a
                // capability violation. A mount-namespace transition is the
                // same class of context escape and must fail-stop here.
                (void)rooted_vfs->name();
                return kUnexpectedReturnExitCode;
            } catch (...) {
                return kUnexpectedExceptionExitCode;
            }
        },
        "descriptor-rooted mount namespace transition");
    const int status = child.wait_for_exit(
        10s, "descriptor-rooted mount namespace transition");
    if (WIFEXITED(status) && WEXITSTATUS(status) == 77) {
        std::cout <<
            "SKIP: host denies descriptor-rooted mount namespace witness\n";
        test.require(
            true,
            "host denies descriptor-rooted mount namespace witness");
        return;
    }
    test.require(
        WIFEXITED(status) &&
            WEXITSTATUS(status) == kSyncProcessCapabilityViolationExitCode,
        "descriptor-rooted VFS fail-stops after a mount namespace transition");
#else
    (void)root;
    test.require(
        true,
        "descriptor-rooted mount namespace proof is not applicable");
#endif
}

void test_descriptor_rooted_same_namespace_mount_family_authority(
    const fs::path& root,
    TestState& test) {
#if defined(__linux__)
    const fs::path parent = root / "descriptor-same-namespace-bind-mount";
    const fs::path database = parent / "authority.sqlite";
    const fs::path wal = fs::path(database.string() + "-wal");
    const fs::path foreign = parent / "foreign-wal-bytes";
    fs::create_directories(parent);
    create_fixture(database);
    write_exact_file(wal, "approved-local-wal-target");
    write_exact_file(foreign, "foreign-bind-mounted-wal-bytes");
    const std::string foreign_before = read_exact_file(foreign);

    auto child = spawn_inherited_test_process_or_throw(
        [&]() -> int {
            if (::unshare(CLONE_NEWUSER | CLONE_NEWNS) != 0) {
                if (errno == EPERM || errno == EINVAL || errno == ENOSYS) {
                    return 77;
                }
                return 101;
            }
            if (::mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) !=
                0) {
                if (errno == EPERM || errno == EINVAL || errno == ENOSYS) {
                    return 77;
                }
                return 102;
            }

            struct stat namespace_before {};
            if (::stat("/proc/thread-self/ns/mnt", &namespace_before) != 0) {
                return 103;
            }

            bool mounted = false;
            fs::path mounted_target;
            const auto finish = [&](int code) -> int {
                if (mounted &&
                    ::umount2(mounted_target.c_str(), MNT_DETACH) != 0) {
                    return 118;
                }
                mounted = false;
                return code;
            };

            try {
                SqlitePathFamilyGuard guard =
                    guard_sqlite_path_family_or_throw(
                        database, false, {"-wal", "-shm", "-journal"},
                        "same-namespace bind-mount guard");
                auto rooted_vfs =
                    anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
                        guard, "same-namespace bind-mount VFS");
                sqlite3_vfs* const registered =
                    sqlite3_vfs_find(rooted_vfs->name());
                if (registered == nullptr || registered->xAccess == nullptr ||
                    registered->xOpen == nullptr ||
                    registered->szOsFile <
                        static_cast<int>(sizeof(sqlite3_file))) {
                    return 104;
                }

                if (::mount(
                        foreign.c_str(), wal.c_str(), nullptr, MS_BIND,
                        nullptr) != 0) {
                    if (errno == EPERM || errno == EINVAL ||
                        errno == ENOSYS) {
                        return 77;
                    }
                    return 105;
                }
                mounted_target = wal;
                mounted = true;

                struct stat namespace_after {};
                if (::stat("/proc/thread-self/ns/mnt", &namespace_after) != 0) {
                    return finish(106);
                }
                if (namespace_before.st_dev != namespace_after.st_dev ||
                    namespace_before.st_ino != namespace_after.st_ino) {
                    return finish(107);
                }
                if (read_exact_file(wal) != foreign_before) {
                    return finish(108);
                }

                int access_result = 1;
                const int access_code = registered->xAccess(
                    registered, wal.c_str(), SQLITE_ACCESS_EXISTS,
                    &access_result);
                if (access_code == SQLITE_OK || access_result != 0) {
                    return finish(109);
                }

                void* const storage = ::operator new(
                    static_cast<std::size_t>(registered->szOsFile));
                std::memset(
                    storage, 0,
                    static_cast<std::size_t>(registered->szOsFile));
                auto* const opened = static_cast<sqlite3_file*>(storage);
                int output_flags = 0;
                const int open_code = registered->xOpen(
                    registered, wal.c_str(), opened,
                    SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                        SQLITE_OPEN_WAL,
                    &output_flags);
                const bool rejected =
                    open_code != SQLITE_OK && opened->pMethods == nullptr;
                if (opened->pMethods != nullptr &&
                    opened->pMethods->xClose != nullptr) {
                    (void)opened->pMethods->xClose(opened);
                }
                ::operator delete(storage);
                if (!rejected) return finish(110);
                if (read_exact_file(foreign) != foreign_before) {
                    return finish(111);
                }

                if (::umount2(mounted_target.c_str(), MNT_DETACH) != 0) {
                    return 113;
                }
                mounted = false;

                // A bind mount of the approved main file onto its own pathname
                // preserves st_dev, st_ino, bytes, and mount-namespace inode.
                // Only the frozen statx mount identity distinguishes the
                // substituted mount object. Namespace-only public proofs must
                // reject it even before any SQLite connection is opened.
                if (::mount(
                        database.c_str(), database.c_str(), nullptr, MS_BIND,
                        nullptr) != 0) {
                    return 114;
                }
                mounted_target = database;
                mounted = true;
                bool exact_main_mount_rejected = false;
                try {
                    rooted_vfs->verify_sidecars_absent_or_throw(
                        "same-inode main bind-mount namespace proof");
                } catch (...) {
                    exact_main_mount_rejected = true;
                }
                if (!exact_main_mount_rejected) return finish(115);

                const int cleanup = finish(0);
                rooted_vfs.reset();
                return cleanup;
            } catch (...) {
                return finish(112);
            }
        },
        "descriptor-rooted same-namespace bind-mount family witness");

    const int status = child.wait_for_exit(
        10s, "descriptor-rooted same-namespace bind-mount family witness");
    if (WIFEXITED(status) && WEXITSTATUS(status) == 77) {
        std::cout
            << "SKIP: host denies same-namespace bind-mount family witness\n";
        test.require(
            true, "host denies same-namespace bind-mount family witness");
        return;
    }
    test.require(
        WIFEXITED(status) && WEXITSTATUS(status) == 0,
        "descriptor-rooted authority rejects same-namespace bind-mounted WAL and exact-inode main names");
    test.require(
        read_exact_file(foreign) == foreign_before,
        "same-namespace bind-mount rejection preserves foreign bytes");
#else
    (void)root;
    test.require(
        true,
        "descriptor-rooted same-namespace mount-family proof is not applicable");
#endif
}

void test_descriptor_rooted_descriptor_bridge_authority(
    const fs::path& root,
    TestState& test) {
#if defined(__linux__)
    auto bridge_child = spawn_inherited_test_process_or_throw(
        [&]() -> int {
            try {
                const fs::path parent = root / "descriptor-bridge-reuse";
                const fs::path database = parent / "authority.sqlite";
                fs::create_directories(parent);
                create_fixture(database);

                struct stat expected {};
                if (::stat(parent.c_str(), &expected) != 0) return 91;
                SqlitePathFamilyGuard guard =
                    guard_sqlite_path_family_or_throw(
                        database, false, {"-wal", "-shm", "-journal"},
                        "descriptor bridge guard");
                auto rooted_vfs =
                    anonsync::register_sqlite_descriptor_rooted_vfs_or_throw(
                        guard, "descriptor bridge VFS");

                std::vector<int> matching_descriptors;
                {
                    for (const fs::directory_entry& entry :
                         fs::directory_iterator("/proc/self/fd")) {
                        const std::string name =
                            entry.path().filename().string();
                        char* end = nullptr;
                        errno = 0;
                        const long parsed = std::strtol(
                            name.c_str(), &end, 10);
                        if (errno != 0 || end == name.c_str() ||
                            *end != '\0' || parsed < 0 ||
                            parsed > std::numeric_limits<int>::max()) {
                            continue;
                        }
                        struct stat observed {};
                        const int descriptor = static_cast<int>(parsed);
                        if (::fstat(descriptor, &observed) == 0 &&
                            S_ISDIR(observed.st_mode) &&
                            observed.st_dev == expected.st_dev &&
                            observed.st_ino == expected.st_ino) {
                            matching_descriptors.push_back(descriptor);
                        }
                    }
                }
                if (matching_descriptors.size() < 2U) return 92;
                for (const int descriptor : matching_descriptors) {
                    (void)::close(descriptor);
                }

                // name() is noexcept and therefore must fail-stop rather than
                // return a VFS whose /proc/self/fd bridge can now be reused.
                (void)rooted_vfs->name();
                return kUnexpectedReturnExitCode;
            } catch (...) {
                return kUnexpectedExceptionExitCode;
            }
        },
        "descriptor-rooted parent descriptor bridge loss");
    const int bridge_status = bridge_child.wait_for_exit(
        10s, "descriptor-rooted parent descriptor bridge loss");
    test.require(
        WIFEXITED(bridge_status) &&
            WEXITSTATUS(bridge_status) ==
                kSyncProcessCapabilityViolationExitCode,
        "descriptor-rooted VFS fail-stops after retained parent descriptor loss");

#else
    (void)root;
    test.require(
        true,
        "descriptor-rooted descriptor-bridge proof is not applicable");
#endif
}

void test_seal_process_authority(const fs::path& source,
                                 TestState& test) {
    std::string first_digest;
    {
        SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture(
            source, "process-bound sealed snapshot");
        first_digest = seal.sha256_hex();

        require_child_fail_stop(
            test,
            [&] { (void)seal.sha256_hex(); },
            "child cannot inspect an inherited sealed snapshot");
        require_child_fail_stop(
            test,
            [&] { seal.verify_unchanged_or_throw("inherited seal verify"); },
            "child cannot verify through an inherited sealed snapshot");
        require_child_fail_stop(
            test,
            [&] {
                auto* moved = new SealedSqliteSnapshot(std::move(seal));
                (void)moved;
            },
            "child cannot move an inherited sealed snapshot");
        require_child_fail_stop(
            test,
            [&] { seal = SealedSqliteSnapshot{}; },
            "child move-assignment cannot free parent resident snapshot bytes");

        test.require(seal.sha256_hex() == first_digest,
                     "hostile child cleanup changed parent resident snapshot evidence");
        seal.verify_unchanged_or_throw("parent seal post-fork verification");
        sqlite3* database = seal.open_database_or_throw(
            "parent seal post-fork deserialize");
        sqlite_or_throw(sqlite3_close(database), database,
                        "parent seal post-fork close");
        test.require(true,
                     "parent seal remains verifiable and openable after hostile children");
    }
    test.require(!first_digest.empty(),
                 "parent seal destructor completed after process-fenced use");

    auto* heap_seal = new SealedSqliteSnapshot(
        SealedSqliteSnapshot::capture(source, "heap process-bound seal"));
    const std::string heap_digest = heap_seal->sha256_hex();
    require_child_fail_stop(
        test,
        [&] { delete heap_seal; },
        "child destructor cannot free an inherited sealed snapshot");
    test.require(heap_seal->sha256_hex() == heap_digest,
                 "child seal destructor changed parent resident snapshot");
    delete heap_seal;
    test.require(true,
                 "parent seal destructor released resident snapshot authority");
}
void test_child_local_persistence_authority(const fs::path& source,
                                            TestState& test) {
    require_child_success(
        test,
        [&] {
            SqlitePathFamilyGuard guard = guard_sqlite_path_family_or_throw(
                source, false, {"-wal", "-shm", "-journal"},
                "child-local path guard");
            guard.verify_family_or_throw("child-local path guard verification");

            SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture(
                source, "child-local sealed snapshot");
            SyncSqliteDbHandleSlot database_owner =
                seal.open_database_owner_or_throw(
                    "child-local immutable open");
            sqlite3* const database = database_owner.get();
            SqliteVerificationBudgetPolicy policy;
            policy.progress_opcode_interval = 1U;
            SqliteVerificationBudget budget(
                borrow_sync_sqlite_serialized_db_or_throw(
                    database_owner,
                    "child-local verification budget generation"),
                "child-local verification budget", policy);
            char* error = nullptr;
            const int query_rc = sqlite3_exec(
                database,
                "SELECT length(value) FROM evidence;",
                nullptr, nullptr, &error);
            const std::string detail = error == nullptr ? std::string() : error;
            sqlite3_free(error);
            sqlite_or_throw(query_rc, database,
                            "child-local immutable query" +
                                (detail.empty() ? std::string() : ": " + detail));
            budget.consume_row();
            budget.detach();
            database_owner.reset();
            seal.verify_unchanged_or_throw(
                "child-local post-close seal verification");
        },
        "child can mint fresh persistence authority after fork");
}

void test_busy_handler_process_authority(const fs::path& path,
                                         TestState& test) {
    SyncSqliteDbHandleSlot writer;
    SyncSqliteDbHandleSlot contender;
    open_typed_database_or_throw(writer, path, "busy-owner writer open");
    open_typed_database_or_throw(contender, path, "busy-owner contender open");
    sqlite_or_throw(sqlite3_exec(
                        writer.get(),
                        "CREATE TABLE IF NOT EXISTS busy_evidence(value INTEGER);",
                        nullptr, nullptr, nullptr),
                    writer.get(), "busy-owner fixture schema");
    sqlite_or_throw(sqlite3_exec(writer.get(), "BEGIN IMMEDIATE;",
                                 nullptr, nullptr, nullptr),
                    writer.get(), "busy-owner parent writer lock");

    auto* owner = new SqliteBusyHandlerOwner(
        borrow_sync_sqlite_serialized_db_or_throw(
            contender, "process-bound busy-handler generation"),
        2'000U,
        "process-bound busy handler");
    sqlite3* const inherited_contender = contender.get();

    require_child_fail_stop(
        test,
        [&] { (void)owner->snapshot(); },
        "child cannot inspect an inherited busy-handler owner");
    require_child_fail_stop(
        test,
        [&] { owner->detach(); },
        "child cannot detach an inherited busy callback");
    require_child_fail_stop(
        test,
        [&] { delete owner; },
        "child destructor cannot detach an inherited busy-handler owner");
    require_child_fail_stop(
        test,
        [&] {
            char* error = nullptr;
            (void)sqlite3_exec(inherited_contender,
                               "BEGIN IMMEDIATE;",
                               nullptr, nullptr, &error);
            sqlite3_free(error);
        },
        "inherited SQLite contention reaches the process-bound busy callback");
    require_child_fail_stop(
        test,
        [&] { (void)sqlite3_close(inherited_contender); },
        "child raw close cannot destroy an inherited busy-handler claim");

    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteDbHandleSlot child_database;
            open_typed_database_or_throw(
                child_database, ":memory:", "child-local premature close open");
            auto* child_owner = new SqliteBusyHandlerOwner(
                borrow_sync_sqlite_serialized_db_or_throw(
                    child_database, "child-local premature close generation"),
                10U,
                "child-local premature close busy handler");
            (void)child_owner;
            (void)sqlite3_close(child_database.get());
        },
        "raw close cannot destroy a live child-local busy-handler claim");
    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteDbHandleSlot child_database;
            open_typed_database_or_throw(
                child_database, ":memory:", "child-local replacement open");
            auto* child_owner = new SqliteBusyHandlerOwner(
                borrow_sync_sqlite_serialized_db_or_throw(
                    child_database, "child-local replacement generation"),
                10U,
                "child-local replacement busy handler");
            (void)child_owner;
            (void)sqlite3_set_clientdata(
                child_database.get(),
                "anonsync.sqlite-busy-handler-owner.v1",
                nullptr,
                nullptr);
        },
        "client-data replacement cannot destroy a live child-local busy-handler claim");

    test.require(contender.active_borrows() == 1U &&
                     owner->snapshot().invocations == 0U,
                 "parent busy-handler generation survives hostile children");
    sqlite_or_throw(sqlite3_exec(writer.get(), "ROLLBACK;",
                                 nullptr, nullptr, nullptr),
                    writer.get(), "busy-owner parent writer unlock");
    owner->detach();
    test.require(contender.active_borrows() == 0U,
                 "parent busy-handler detach releases its exact generation");
    delete owner;

    require_child_success(
        test,
        [&] {
            SyncSqliteDbHandleSlot child_database;
            open_typed_database_or_throw(
                child_database, ":memory:", "child-local busy-owner open");
            SqliteBusyHandlerOwner child_owner(
                borrow_sync_sqlite_serialized_db_or_throw(
                    child_database, "child-local busy-owner generation"),
                10U,
                "child-local busy handler");
            if (child_owner.snapshot().invocations != 0U) {
                throw std::runtime_error(
                    "fresh child-local busy owner had nonempty diagnostics");
            }
            child_owner.detach();
        },
        "child can mint and detach fresh busy-handler authority after fork");
}

void test_budget_process_authority(TestState& test) {
    SyncSqliteDbHandleSlot database_owner;
    open_typed_database_or_throw(
        database_owner, ":memory:", "budget fixture open");
    sqlite3* const database = database_owner.get();
    sqlite_or_throw(sqlite3_exec(
                        database,
                        "CREATE TABLE numbers(value INTEGER NOT NULL);"
                        "WITH RECURSIVE values_cte(value) AS ("
                        "SELECT 1 UNION ALL SELECT value + 1 FROM values_cte "
                        "WHERE value < 1000) "
                        "INSERT INTO numbers SELECT value FROM values_cte;",
                        nullptr, nullptr, nullptr),
                    database, "budget fixture populate");

    SqliteVerificationBudgetPolicy policy;
    policy.progress_opcode_interval = 1U;
    SqliteVerificationBudget budget(
        borrow_sync_sqlite_serialized_db_or_throw(
            database_owner, "process-bound budget generation"),
        "process-bound budget", policy);

    require_child_fail_stop(
        test,
        [&] { budget.consume_row(); },
        "child cannot consume inherited verification budget");
    require_child_fail_stop(
        test,
        [&] { budget.detach(); },
        "child cannot detach a parent progress callback");
    require_child_fail_stop(
        test,
        [&] {
            char* error = nullptr;
            (void)sqlite3_exec(database,
                               "SELECT sum(value) FROM numbers;",
                               nullptr, nullptr, &error);
            sqlite3_free(error);
        },
        "inherited SQLite execution reaches the process-bound callback");
    require_child_fail_stop(
        test,
        [&] { (void)sqlite3_close(database); },
        "child raw close cannot destroy an inherited verification claim");

    auto* heap_database_owner = new SyncSqliteDbHandleSlot();
    open_typed_database_or_throw(
        *heap_database_owner, ":memory:", "heap budget fixture open");
    auto* heap_budget = new SqliteVerificationBudget(
        borrow_sync_sqlite_serialized_db_or_throw(
            *heap_database_owner, "heap process-bound budget generation"),
        "heap process-bound budget", policy);
    require_child_fail_stop(
        test,
        [&] { delete heap_budget; },
        "child destructor cannot detach an inherited verification budget");
    delete heap_budget;
    heap_database_owner->reset();
    delete heap_database_owner;

    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteDbHandleSlot child_database;
            open_typed_database_or_throw(
                child_database, ":memory:",
                "child-local verification premature close open");
            auto* child_budget = new SqliteVerificationBudget(
                borrow_sync_sqlite_serialized_db_or_throw(
                    child_database,
                    "child-local verification premature close generation"),
                "child-local verification premature close", policy);
            (void)child_budget;
            (void)sqlite3_close(child_database.get());
        },
        "raw close cannot destroy a live child-local verification claim");
    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteDbHandleSlot child_database;
            open_typed_database_or_throw(
                child_database, ":memory:",
                "child-local verification deferred close_v2 open");
            sqlite3_stmt* statement = nullptr;
            sqlite_or_throw(sqlite3_prepare_v2(
                                child_database.get(), "SELECT 1;", -1,
                                &statement, nullptr),
                            child_database.get(),
                            "child-local verification deferred statement");
            auto* child_budget = new SqliteVerificationBudget(
                borrow_sync_sqlite_serialized_db_or_throw(
                    child_database,
                    "child-local verification deferred close_v2 generation"),
                "child-local verification deferred close_v2", policy);
            (void)child_budget;
            sqlite_or_throw(sqlite3_close_v2(child_database.get()),
                            child_database.get(),
                            "child-local verification deferred close_v2");
            (void)sqlite3_finalize(statement);
        },
        "deferred close_v2 destruction cannot outlive a live verification claim");
    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteDbHandleSlot child_database;
            open_typed_database_or_throw(
                child_database, ":memory:",
                "child-local verification replacement open");
            auto* child_budget = new SqliteVerificationBudget(
                borrow_sync_sqlite_serialized_db_or_throw(
                    child_database,
                    "child-local verification replacement generation"),
                "child-local verification replacement", policy);
            (void)child_budget;
            (void)sqlite3_set_clientdata(
                child_database.get(),
                "anonsync.sqlite-verification-budget.v1",
                nullptr,
                nullptr);
        },
        "client-data replacement cannot destroy a live child-local verification claim");

    // Prove the parent still owns both accounting and callback detachment.
    test.require(database_owner.active_borrows() == 1U,
                 "parent verification generation survives hostile children");
    budget.consume_row();
    budget.checkpoint();
    test.require(budget.rows() == 1U,
                 "parent budget remains usable after hostile children");
    budget.detach();
    test.require(database_owner.active_borrows() == 0U,
                 "parent verification detach releases its exact generation");
    database_owner.reset();
}

#else

void test_path_guard_process_authority(const fs::path&, TestState& test) {
    test.require(true, "path-guard fork proof unavailable on this platform");
}
void test_descriptor_rooted_sqlite_open(const fs::path&, TestState& test) {
    test.require(
        true,
        "descriptor-rooted SQLite open proof unavailable on this platform");
}
void test_descriptor_rooted_forensic_read_only_authority(
    const fs::path&,
    TestState& test) {
    test.require(
        true,
        "descriptor-rooted forensic read-only proof unavailable on this platform");
}
void test_descriptor_rooted_auxiliary_close_preserves_locks(
    const fs::path&,
    TestState& test) {
    test.require(
        true,
        "auxiliary VFS lock-preservation proof unavailable on this platform");
}
void test_descriptor_rooted_mount_namespace_authority(
    const fs::path&,
    TestState& test) {
    test.require(
        true,
        "descriptor-rooted mount namespace proof unavailable on this platform");
}
void test_descriptor_rooted_same_namespace_mount_family_authority(
    const fs::path&,
    TestState& test) {
    test.require(
        true,
        "descriptor-rooted same-namespace mount-family proof unavailable on this platform");
}
void test_descriptor_rooted_descriptor_bridge_authority(
    const fs::path&,
    TestState& test) {
    test.require(
        true,
        "descriptor-rooted descriptor-bridge proof unavailable on this platform");
}
void test_seal_process_authority(const fs::path&, TestState& test) {
    test.require(true, "seal fork proof unavailable on this platform");
}
void test_child_local_persistence_authority(const fs::path&, TestState& test) {
    test.require(true, "child-local persistence fork proof unavailable on this platform");
}
void test_busy_handler_process_authority(const fs::path&, TestState& test) {
    test.require(true, "busy-handler fork proof unavailable on this platform");
}
void test_budget_process_authority(TestState& test) {
    test.require(true, "budget fork proof unavailable on this platform");
}

#endif

}  // namespace

int main() {
    TestState test;
    const fs::path root = fs::temp_directory_path() /
        ("anonsync_rev0905_persistence_process_authority_" +
#if defined(__unix__) || defined(__APPLE__)
         std::to_string(static_cast<long long>(::getpid()))
#else
         std::to_string(std::rand())
#endif
        );
    const fs::path source = root / "source.sqlite";
    std::error_code ignored;
    fs::remove_all(root, ignored);
    try {
        fs::create_directories(root);
        create_fixture(source);
        test_path_guard_process_authority(source, test);
        test_descriptor_rooted_sqlite_open(root, test);
        test_descriptor_rooted_forensic_read_only_authority(root, test);
        test_descriptor_rooted_auxiliary_close_preserves_locks(root, test);
        test_descriptor_rooted_mount_namespace_authority(root, test);
        test_descriptor_rooted_same_namespace_mount_family_authority(root, test);
        test_descriptor_rooted_descriptor_bridge_authority(root, test);
        test_seal_process_authority(source, test);
        test_child_local_persistence_authority(source, test);
        test_busy_handler_process_authority(root / "busy-owner.sqlite", test);
        test_budget_process_authority(test);
    } catch (const std::exception& error) {
        ++test.failed;
        std::cerr << "FAIL: unexpected exception: " << error.what() << "\n";
    }
    fs::remove_all(root, ignored);
    std::cout << "anonsync sqlite persistence process authority fork tests checks="
              << test.passed << " failed=" << test.failed << "\n";
    return test.failed == 0U ? EXIT_SUCCESS : EXIT_FAILURE;
}
