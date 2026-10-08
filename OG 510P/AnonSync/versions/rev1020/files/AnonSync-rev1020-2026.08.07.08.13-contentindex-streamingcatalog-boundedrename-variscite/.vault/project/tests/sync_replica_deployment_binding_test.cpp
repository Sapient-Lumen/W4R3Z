#include "sync_replica_deployment_binding.hpp"

#include "sync_sqlite_support.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#include <sqlite3.h>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;

std::uint64_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#if !defined(_WIN32)
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        path_ = fs::temp_directory_path() /
            ("anonsync-deployment-binding-" + std::to_string(process) +
             "-" + std::to_string(tick));
        fs::create_directory(path_);
#if !defined(_WIN32)
        if (::chmod(path_.c_str(), 0700) != 0) {
            fail("could not make deployment-binding test root private");
        }
#endif
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

[[nodiscard]] anonsync::SyncSqliteDb open_database(
    const fs::path& path,
    bool create) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                SQLITE_OPEN_PRIVATECACHE;
    if (create) flags |= SQLITE_OPEN_CREATE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "deployment-binding test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "deployment-binding test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;"
        "PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;"
        "PRAGMA foreign_keys=ON;"
        "PRAGMA trusted_schema=OFF;",
        "deployment-binding test connection profile");
    return owner;
}

[[nodiscard]] anonsync::SyncSqliteDb open_detached_database() {
    anonsync::SyncSqliteDb owner;
    constexpr int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
        SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE | SQLITE_OPEN_MEMORY;
    const int result = sqlite3_open_v2(
        ":memory:", owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "deployment-binding detached test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "deployment-binding detached test busy timeout");
    return owner;
}

[[nodiscard]] anonsync::SyncSqliteDb open_anonymous_temporary_database() {
    anonsync::SyncSqliteDb owner;
    constexpr int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
        SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
    const int result = sqlite3_open_v2("", owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "deployment-binding anonymous temporary test open"));
    }
    return owner;
}

void copy_database_or_throw(
    anonsync::SyncSqliteDbHandleSlot& destination,
    anonsync::SyncSqliteDbHandleSlot& source) {
    auto destination_borrow = destination.borrow();
    auto source_borrow = source.borrow();
    sqlite3_backup* backup = sqlite3_backup_init(
        destination_borrow.get(), "main", source_borrow.get(), "main");
    if (backup == nullptr) {
        fail("could not initialize detached deployment-binding copy");
    }
    const int copied = sqlite3_backup_step(backup, -1);
    const int finished = sqlite3_backup_finish(backup);
    if (copied != SQLITE_DONE || finished != SQLITE_OK) {
        fail("could not finish detached deployment-binding copy");
    }
}

[[nodiscard]] anonsync::SyncReplicaDeploymentIdentity identity(
    const TemporaryDirectory& temporary,
    char deployment_byte = 'a',
    char digest_byte = 'b') {
    return {
        .deployment_id = std::string(64U, deployment_byte),
        .manifest_digest = std::string(64U, digest_byte),
        .manifest_path = temporary.path() / "deployment.json",
        .folder_id = "folder-alpha",
        .local_actor = {"device-alpha", 7U},
    };
}

[[nodiscard]] anonsync::SyncReplicaSqliteDeploymentBinding binding(
    const TemporaryDirectory& temporary,
    const fs::path& database_path,
    anonsync::SyncReplicaSqliteDeploymentRole role =
        anonsync::SyncReplicaSqliteDeploymentRole::Replica) {
    return {
        .deployment = identity(temporary),
        .role = role,
        .database_path = database_path,
    };
}

void test_generation_and_role_classifier() {
    const std::string first =
        anonsync::generate_sync_replica_deployment_id_or_throw(
            "deployment-binding first ID");
    const std::string second =
        anonsync::generate_sync_replica_deployment_id_or_throw(
            "deployment-binding second ID");
    require(anonsync::sync_replica_deployment_id_is_valid(first) &&
                anonsync::sync_replica_deployment_id_is_valid(second),
            "generated deployment IDs are lowercase 256-bit values");
    require(first != second,
            "two deployment-ID generations did not repeat in the fixture");
    using Role = anonsync::SyncReplicaSqliteDeploymentRole;
    constexpr std::array<Role, 5> roles{
        Role::Replica, Role::FileEffect, Role::TlsMembership,
        Role::TlsMembershipAnchor, Role::FolderCatalog};
    constexpr std::array<std::string_view, 5> names{
        "replica", "file-effect", "tls-membership",
        "tls-membership-anchor", "folder-catalog"};
    for (std::size_t index = 0U; index < roles.size(); ++index) {
        require(
            std::string_view(
                anonsync::sync_replica_sqlite_deployment_role_name(
                    roles[index])) == names[index],
            "role name is exact");
    }
    for (std::size_t left = 0U; left < roles.size(); ++left) {
        for (std::size_t right = left + 1U; right < roles.size(); ++right) {
            require(
                anonsync::sync_replica_sqlite_application_id(roles[left]) !=
                    anonsync::sync_replica_sqlite_application_id(roles[right]),
                "role-specific SQLite application IDs are pairwise distinct");
        }
    }
}

void test_exact_round_trip_and_reinitialization_rejection() {
    TemporaryDirectory temporary;
    const fs::path path = temporary.path() / "replica.sqlite";
    auto database = open_database(path, true);
    const auto exact = binding(temporary, path);

    anonsync::initialize_sync_replica_sqlite_deployment_binding_or_throw(
        database.db, exact, "deployment-binding exact fixture");
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.db, exact, "deployment-binding exact fixture restart");

    anonsync::sqlite_exec_or_throw(
        database.db, "BEGIN DEFERRED;",
        "deployment-binding state attestation transaction");
    anonsync::attest_sync_replica_sqlite_deployment_binding_state_or_throw(
        database.db, exact,
        "deployment-binding state attestation inside owner transaction");
    anonsync::sqlite_exec_or_throw(
        database.db, "ROLLBACK;",
        "deployment-binding state attestation rollback");

    require_error(
        [&] {
            anonsync::initialize_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, exact,
                "deployment-binding duplicate initialization");
        },
        "namespace is already occupied",
        "a committed binding could be initialized twice");
}

void test_detached_image_initialization_and_named_readback() {
    TemporaryDirectory temporary;
    const fs::path path = temporary.path() / "detached-published.sqlite";
    const auto exact = binding(
        temporary, path,
        anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership);
    auto detached = open_detached_database();

    anonsync::
        initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
            detached.db, exact, "deployment-binding detached fixture");
    anonsync::sqlite_exec_or_throw(
        detached.db, "BEGIN DEFERRED;",
        "deployment-binding detached state transaction");
    anonsync::
        attest_sync_replica_sqlite_deployment_binding_state_in_detached_image_or_throw(
            detached.db, exact,
            "deployment-binding detached state inside owner transaction");
    anonsync::sqlite_exec_or_throw(
        detached.db, "ROLLBACK;",
        "deployment-binding detached state rollback");
    {
        auto borrow = detached.db.borrow();
        const char* const filename = sqlite3_db_filename(borrow.get(), "main");
        require(filename != nullptr && filename[0] == '\0',
                "detached binding image unexpectedly acquired a filename");
    }
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                detached.db, exact,
                "deployment-binding detached ordinary attestation");
        },
        "could not prove the opened main-database filename",
        "a detached image crossed the ordinary named authority gate");

    auto published = open_database(path, true);
    copy_database_or_throw(published.db, detached.db);
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        published.db, exact,
        "deployment-binding detached image named readback");

    require_error(
        [&] {
            anonsync::
                initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
                    published.db, exact,
                    "deployment-binding named detached initialization");
        },
        "unexpectedly names a file",
        "a named database was accepted as a detached bootstrap image");
}

void test_writable_detached_image_cannot_masquerade_as_read_only() {
    TemporaryDirectory temporary;
    const fs::path path = temporary.path() / "detached-writable.sqlite";
    const auto exact = binding(
        temporary, path,
        anonsync::SyncReplicaSqliteDeploymentRole::Replica);
    auto detached = open_detached_database();

    anonsync::
        initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
            detached.db, exact,
            "deployment-binding writable detached probe fixture");
    anonsync::sqlite_exec_or_throw(
        detached.db, "PRAGMA query_only=ON;",
        "deployment-binding writable detached query-only profile");

    anonsync::SyncSqliteTransaction transaction(
        detached.db,
        "deployment-binding writable detached outer transaction",
        anonsync::SyncSqliteTransactionMode::Deferred);
    const auto transaction_authority = transaction.authority();
    require_error(
        [&] {
            anonsync::
                attest_sync_replica_sqlite_deployment_binding_state_in_read_only_detached_image_or_throw(
                    detached.db, exact, transaction_authority,
                    "deployment-binding writable detached read-only rejection");
        },
        "accepted a main-database write",
        "a writable detached image masqueraded as sealed read-only");

    require(
        transaction.active(),
        "the writable-image denial probe ended its exact outer transaction");
    require(
        !anonsync::sqlite_table_exists_or_throw(
            detached.db, "anonsync_detached_read_only_probe_rev0982",
            "deployment-binding writable detached probe cleanup"),
        "the writable-image denial probe retained its test table");
    {
        anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
            detached.db, "PRAGMA query_only;",
            "deployment-binding writable detached query-only reproof");
        const int first = sqlite3_step(statement.stmt);
        require(
            first == SQLITE_ROW &&
                anonsync::sqlite_column_u64_or_throw(
                    statement.stmt, 0,
                    "deployment-binding writable detached query-only value") ==
                    1U,
            "the writable-image denial probe did not restore query_only");
        require(
            sqlite3_step(statement.stmt) == SQLITE_DONE,
            "the writable-image query_only reproof returned excess rows");
    }
    anonsync::
        attest_sync_replica_sqlite_deployment_binding_state_in_detached_image_or_throw(
            detached.db, exact,
            "deployment-binding writable detached post-probe state");
    require(
        transaction.active(),
        "post-probe binding reproof ended the exact outer transaction");
    transaction.commit();
}

void test_detached_image_profile_rejections() {
    TemporaryDirectory temporary;
    const fs::path path = temporary.path() / "detached-profile.sqlite";
    const auto exact = binding(
        temporary, path,
        anonsync::SyncReplicaSqliteDeploymentRole::Replica);

    auto anonymous_temporary = open_anonymous_temporary_database();
    {
        auto borrow = anonymous_temporary.db.borrow();
        const char* const filename = sqlite3_db_filename(borrow.get(), "main");
        require(filename != nullptr && filename[0] == '\0',
                "anonymous temporary fixture unexpectedly exposed a filename");
    }
    require_error(
        [&] {
            anonsync::
                initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
                    anonymous_temporary.db, exact,
                    "deployment-binding anonymous temporary rejection");
        },
        "expected memory",
        "an anonymous disk-backed temporary database was accepted as a "
        "detached bootstrap image");

    auto prepopulated = open_detached_database();
    anonsync::sqlite_exec_or_throw(
        prepopulated.db,
        "CREATE TABLE main.preexisting_authority(id INTEGER PRIMARY KEY);",
        "deployment-binding prepopulated detached fixture");
    require_error(
        [&] {
            anonsync::
                initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
                    prepopulated.db, exact,
                    "deployment-binding prepopulated detached rejection");
        },
        "must be schema-empty",
        "a prepopulated detached database was allowed to acquire bootstrap "
        "deployment identity");
}

void test_identity_role_path_and_header_mismatch_rejections() {
    TemporaryDirectory temporary;
    const fs::path path = temporary.path() / "effect.sqlite";
    auto database = open_database(path, true);
    const auto exact = binding(
        temporary, path,
        anonsync::SyncReplicaSqliteDeploymentRole::FileEffect);
    anonsync::initialize_sync_replica_sqlite_deployment_binding_or_throw(
        database.db, exact, "deployment-binding mismatch fixture");

    auto wrong_deployment = exact;
    wrong_deployment.deployment.deployment_id = std::string(64U, 'c');
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, wrong_deployment,
                "deployment-binding wrong deployment");
        },
        "does not match the selected manifest",
        "a database from another deployment was accepted");

    auto wrong_digest = exact;
    wrong_digest.deployment.manifest_digest = std::string(64U, 'd');
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, wrong_digest,
                "deployment-binding wrong manifest digest");
        },
        "does not match the selected manifest",
        "a database bound to another manifest was accepted");

    auto wrong_role = exact;
    wrong_role.role = anonsync::SyncReplicaSqliteDeploymentRole::Replica;
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, wrong_role, "deployment-binding wrong role");
        },
        "application_id conflicts with the store role",
        "a database with another role was accepted");

    auto wrong_path = exact;
    wrong_path.database_path = temporary.path() / "copied.sqlite";
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, wrong_path, "deployment-binding wrong path");
        },
        "opened main-database filename conflicts",
        "a database opened under another pathname was accepted");

    anonsync::sqlite_exec_or_throw(
        database.db, "PRAGMA main.application_id=0;",
        "deployment-binding application-id tamper");
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, exact,
                "deployment-binding application-id tamper proof");
        },
        "application_id conflicts with the store role",
        "a tampered SQLite application ID was accepted");
}

void test_schema_shadow_and_row_tamper_rejections() {
    TemporaryDirectory temporary;
    const fs::path path = temporary.path() / "membership.sqlite";
    auto database = open_database(path, true);
    const auto exact = binding(
        temporary, path,
        anonsync::SyncReplicaSqliteDeploymentRole::TlsMembership);
    anonsync::initialize_sync_replica_sqlite_deployment_binding_or_throw(
        database.db, exact, "deployment-binding tamper fixture");

    anonsync::sqlite_exec_or_throw(
        database.db,
        "CREATE TEMP TABLE anonsync_store_set_binding(shadow INTEGER);",
        "deployment-binding temp shadow creation");
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, exact,
                "deployment-binding temp shadow proof");
        },
        "temporary deployment-binding shadow is forbidden",
        "a temporary name shadow bypassed exact binding attestation");
    anonsync::sqlite_exec_or_throw(
        database.db, "DROP TABLE temp.anonsync_store_set_binding;",
        "deployment-binding temp shadow cleanup");

    anonsync::sqlite_exec_or_throw(
        database.db,
        "UPDATE main.anonsync_store_set_binding "
        "SET deployment_id='cccccccccccccccccccccccccccccccc"
        "cccccccccccccccccccccccccccccccc';",
        "deployment-binding row tamper");
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                database.db, exact,
                "deployment-binding row tamper proof");
        },
        "does not match the selected manifest",
        "a tampered deployment-binding row was accepted");
}

void test_copied_database_cannot_rebind_path() {
    TemporaryDirectory temporary;
    const fs::path source = temporary.path() / "anchor.sqlite";
    const fs::path copied = temporary.path() / "anchor-copy.sqlite";
    const auto exact = binding(
        temporary, source,
        anonsync::SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor);
    {
        auto database = open_database(source, true);
        anonsync::initialize_sync_replica_sqlite_deployment_binding_or_throw(
            database.db, exact, "deployment-binding copy source");
        anonsync::sqlite_exec_or_throw(
            database.db, "PRAGMA wal_checkpoint(TRUNCATE);",
            "deployment-binding copy checkpoint");
    }
    fs::copy_file(source, copied);
    auto copied_database = open_database(copied, false);
    auto copied_binding = exact;
    copied_binding.database_path = copied;
    require_error(
        [&] {
            anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
                copied_database.db, copied_binding,
                "deployment-binding copied database proof");
        },
        "does not match the selected manifest",
        "copying a database file minted authority at a new pathname");
}

}  // namespace

int main() {
    try {
        test_generation_and_role_classifier();
        test_exact_round_trip_and_reinitialization_rejection();
        test_detached_image_initialization_and_named_readback();
        test_writable_detached_image_cannot_masquerade_as_read_only();
        test_detached_image_profile_rejections();
        test_identity_role_path_and_header_mismatch_rejections();
        test_schema_shadow_and_row_tamper_rejections();
        test_copied_database_cannot_rebind_path();
        std::cout << "sync replica deployment-binding tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica deployment-binding tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
