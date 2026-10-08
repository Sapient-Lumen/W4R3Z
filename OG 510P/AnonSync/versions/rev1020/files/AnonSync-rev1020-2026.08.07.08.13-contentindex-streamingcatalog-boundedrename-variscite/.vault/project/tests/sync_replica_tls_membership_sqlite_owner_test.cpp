#include "sync_replica_tls_membership_sqlite_owner_test.hpp"

#include "sha256_digest.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#include <array>
#include <barrier>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

#include <sqlite3.h>

#ifdef __unix__
#include <unistd.h>
#endif

namespace anonsync::test {
namespace {

static_assert(!std::is_default_constructible_v<
              SyncReplicaTlsMembershipAuthority>);
static_assert(!std::is_copy_constructible_v<
              SyncReplicaTlsMembershipAuthority>);
static_assert(!std::is_copy_assignable_v<
              SyncReplicaTlsMembershipAuthority>);
static_assert(std::is_nothrow_move_constructible_v<
              SyncReplicaTlsMembershipAuthority>);
static_assert(std::is_nothrow_move_assignable_v<
              SyncReplicaTlsMembershipAuthority>);
static_assert(!std::is_copy_constructible_v<
              SyncReplicaTlsMembershipSqliteOwner>);
static_assert(!std::is_move_constructible_v<
              SyncReplicaTlsMembershipSqliteOwner>);

class Checks final {
public:
    void require(bool condition, const std::string& message) {
        ++count_;
        if (!condition) throw std::runtime_error(message);
    }

    template <typename Callable>
    void require_error(Callable&& callable,
                       std::string_view expected,
                       const std::string& message) {
        ++count_;
        try {
            std::forward<Callable>(callable)();
        } catch (const std::exception& error) {
            if (std::string_view(error.what()).find(expected) !=
                std::string_view::npos) {
                return;
            }
            throw std::runtime_error(
                message + ": unexpected error: " + error.what());
        }
        throw std::runtime_error(message + ": no error was thrown");
    }

    [[nodiscard]] std::size_t count() const noexcept { return count_; }

private:
    std::size_t count_ = 0U;
};

class TempMembershipWorkspace final {
public:
    explicit TempMembershipWorkspace(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __unix__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0L;
#endif
        root_ = std::filesystem::temp_directory_path() /
                (std::string(stem) + "-" + std::to_string(process) + "-" +
                 std::to_string(tick));
        std::filesystem::create_directories(root_);
    }

    ~TempMembershipWorkspace() {
        std::error_code ignored;
        std::filesystem::remove_all(root_, ignored);
    }

    [[nodiscard]] std::filesystem::path path(std::string_view name) const {
        return root_ / std::string(name);
    }

private:
    std::filesystem::path root_;
};

[[nodiscard]] SyncSqliteDb open_database(
    const std::filesystem::path& path,
    bool use_wal = true) {
    SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            owner.db, "TLS membership owner test open"));
    }
    sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "TLS membership owner test busy timeout");
    if (use_wal) {
        sqlite_exec_or_throw(
            owner.db,
            "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
            "PRAGMA wal_autocheckpoint=1;",
            "TLS membership owner test durability profile");
    } else {
        sqlite_exec_or_throw(
            owner.db, "PRAGMA synchronous=EXTRA;",
            "TLS membership owner test rollback-journal profile");
    }
    return owner;
}

[[nodiscard]] SyncSqliteDb open_detached_database() {
    SyncSqliteDb owner;
    constexpr int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
        SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE | SQLITE_OPEN_MEMORY;
    const int result = sqlite3_open_v2(
        ":memory:", owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            owner.db, "TLS membership detached owner test open"));
    }
    sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "TLS membership detached owner test busy timeout");
    return owner;
}

void clone_database_file_or_throw(
    const std::filesystem::path& source,
    const std::filesystem::path& destination) {
    std::error_code error;
    std::filesystem::copy_file(
        source, destination,
        std::filesystem::copy_options::overwrite_existing, error);
    if (error) {
        throw std::runtime_error(
            "TLS membership owner test could not clone database: " +
            error.message());
    }
}

void checkpoint_or_throw(SyncSqliteDb& database) {
    sqlite_exec_or_throw(
        database.db, "PRAGMA wal_checkpoint(TRUNCATE);",
        "TLS membership owner test checkpoint");
}

[[nodiscard]] std::uint64_t query_scalar_u64_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string_view sql,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, std::string(sql), label + " prepare");
    const int first = sqlite3_step(statement.stmt);
    if (first != SQLITE_ROW) {
        throw std::runtime_error(sqlite_error_message(db, label + " step"));
    }
    const std::uint64_t value = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " value");
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        throw std::runtime_error(
            sqlite_error_message(db, label + " trailing step"));
    }
    return value;
}

[[nodiscard]] int query_db_config_or_throw(
    SyncSqliteDbHandleSlot& db,
    int option,
    const std::string& label) {
    int observed = -1;
    const int result = sqlite3_db_config(db.get(), option, -1, &observed);
    if (result != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(db, label));
    }
    return observed;
}

[[nodiscard]] std::vector<SyncReplicaTlsMembershipEntry> first_entries(
    const SyncReplicaActor& peer_a,
    const SyncReplicaActor& peer_b) {
    return {
        {sha256_hex("membership durable peer b"), peer_b},
        {sha256_hex("membership durable peer a"), peer_a},
    };
}

void test_serialized_first_open(Checks& checks) {
    TempMembershipWorkspace workspace("anonsync-membership-first-open");
    const auto database_path = workspace.path("membership.sqlite3");
    const SyncReplicaActor local{"membership-race-local", 7001U};
    std::barrier start(2);
    std::array<std::exception_ptr, 2U> errors{};
    std::array<std::uint64_t, 2U> generations{};

    auto run = [&](std::size_t index) {
        try {
            SyncSqliteDb database = open_database(database_path, false);
            start.arrive_and_wait();
            SyncReplicaTlsMembershipSqliteOwner owner(
                database.db, "membership-race-folder", local,
                "TLS membership concurrent first-open owner");
            generations[index] = owner.snapshot_or_throw().state_generation;
        } catch (...) {
            errors[index] = std::current_exception();
        }
    };

    std::thread left(run, 0U);
    std::thread right(run, 1U);
    left.join();
    right.join();
    if (errors[0]) std::rethrow_exception(errors[0]);
    if (errors[1]) std::rethrow_exception(errors[1]);
    checks.require(
        generations[0] == 0U && generations[1] == 0U,
        "concurrent membership owners disagreed on serialized genesis state");

    SyncSqliteDb database = open_database(database_path, false);
    SyncReplicaTlsMembershipSqliteOwner owner(
        database.db, "membership-race-folder", local,
        "TLS membership concurrent first-open restart");
    const auto snapshot = owner.snapshot_or_throw();
    checks.require(
        snapshot.history.empty() && snapshot.state_generation == 0U &&
            is_lowercase_sha256_hex(snapshot.current_chain_digest),
        "concurrent membership schema initialization left partial authority");
}

void test_detached_bootstrap_image_profile(Checks& checks) {
    const std::string folder = "membership-detached-folder";
    const SyncReplicaActor local{"membership-detached-local", 6991U};
    SyncSqliteDb database = open_detached_database();
    SyncReplicaTlsMembershipSqliteOwner owner(
        database.db, folder, local,
        SyncReplicaTlsPolicySqliteBackendDisposition::DetachedBootstrapImage,
        "TLS membership detached bootstrap owner");
    const auto genesis = owner.snapshot_or_throw();
    checks.require(
        owner.database_filename().empty() && genesis.history.empty() &&
            genesis.state_generation == 0U &&
            genesis.current_policy_epoch == 0U &&
            genesis.current_entry_count == 0U,
        "detached membership bootstrap owner did not expose exact genesis");
    checks.require_error(
        [&] {
            (void)owner.publish_or_throw(genesis.anchor(), 1U, {});
        },
        "detached bootstrap image cannot publish membership authority",
        "detached membership bootstrap owner crossed into durable publication");

    SyncSqliteDb ordinary_rejection = open_detached_database();
    checks.require_error(
        [&] {
            SyncReplicaTlsMembershipSqliteOwner named_owner(
                ordinary_rejection.db, folder, local,
                "TLS membership detached ordinary-owner rejection");
        },
        "has no durable main filename",
        "ordinary membership owner admitted anonymous SQLite authority");

    SyncSqliteDb forensic_owner_rejection = open_detached_database();
    checks.require_error(
        [&] {
            SyncReplicaTlsMembershipSqliteOwner forbidden_owner(
                forensic_owner_rejection.db, folder, local,
                SyncReplicaTlsPolicySqliteBackendDisposition::
                    ForensicReadOnlyNamed,
                "TLS membership forensic owner rejection");
        },
        "forensic read-only disposition cannot own mutable TLS policy authority",
        "membership owner admitted forensic observation as mutable authority");

    SyncSqliteDb invalid_rejection = open_detached_database();
    checks.require_error(
        [&] {
            SyncReplicaTlsMembershipSqliteOwner invalid_owner(
                invalid_rejection.db, folder, local,
                static_cast<SyncReplicaTlsPolicySqliteBackendDisposition>(0U),
                "TLS membership invalid backend disposition");
        },
        "backend disposition is invalid",
        "membership owner admitted an invalid backend disposition");
}


void test_connection_profile_and_retention_admission(Checks& checks) {
    checks.require(
        sync_replica_tls_membership_append_fits_hard_limits(0U, 0U, 0U),
        "empty membership append did not fit empty hard ceilings");
    checks.require(
        sync_replica_tls_membership_append_fits_hard_limits(
            kSyncReplicaTlsMembershipMaxHistoryRecords - 1U,
            kSyncReplicaTlsMembershipMaxRetainedEntryRows, 0U),
        "last empty membership history append was rejected at its exact boundary");
    checks.require(
        !sync_replica_tls_membership_append_fits_hard_limits(
            kSyncReplicaTlsMembershipMaxHistoryRecords, 0U, 0U),
        "membership history admitted one record beyond its hard ceiling");
    checks.require(
        !sync_replica_tls_membership_append_fits_hard_limits(
            0U, kSyncReplicaTlsMembershipMaxRetainedEntryRows, 1U),
        "membership retention admitted one entry beyond its hard ceiling");
    checks.require(
        !sync_replica_tls_membership_append_fits_hard_limits(
            0U, kSyncReplicaTlsMembershipMaxRetainedEntryRows + 1U, 0U),
        "membership retention accepted an already-overflowed retained count");
    checks.require(
        !sync_replica_tls_membership_append_fits_hard_limits(
            0U, 0U, kSyncReplicaTlsMembershipMaxEntries + 1U),
        "membership append planning bypassed the per-snapshot entry ceiling");

    TempMembershipWorkspace workspace("anonsync-membership-connection-profile");
    {
        SyncSqliteDb database =
            open_database(workspace.path("profile.sqlite3"));
        sqlite_exec_or_throw(
            database.db,
            "PRAGMA trusted_schema=ON;"
            "PRAGMA read_uncommitted=ON;"
            "PRAGMA ignore_check_constraints=ON;",
            "TLS membership mutable connection profile fixture");
        SyncReplicaTlsMembershipSqliteOwner owner(
            database.db, "membership-profile-owned-folder",
            {"membership-profile-owned-local", 7061U},
            "TLS membership hardened connection owner");
        checks.require(
            query_scalar_u64_or_throw(
                database.db, "PRAGMA trusted_schema;",
                "TLS membership trusted-schema observation") == 0U &&
                query_scalar_u64_or_throw(
                    database.db, "PRAGMA query_only;",
                    "TLS membership query-only observation") == 0U &&
                query_scalar_u64_or_throw(
                    database.db, "PRAGMA read_uncommitted;",
                    "TLS membership read-uncommitted observation") == 0U &&
                query_scalar_u64_or_throw(
                    database.db, "PRAGMA ignore_check_constraints;",
                    "TLS membership check-constraint observation") == 0U,
            "membership owner did not install its exact safe pragma profile");
#ifdef SQLITE_DBCONFIG_DEFENSIVE
        checks.require(
            query_db_config_or_throw(
                database.db, SQLITE_DBCONFIG_DEFENSIVE,
                "TLS membership defensive-mode observation") == 1,
            "membership owner did not retain SQLite defensive mode");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_TRIGGER
        checks.require(
            query_db_config_or_throw(
                database.db, SQLITE_DBCONFIG_ENABLE_TRIGGER,
                "TLS membership trigger-mode observation") == 0,
            "membership owner left schema triggers enabled");
        int changed = -1;
        const int result = sqlite3_db_config(
            database.db.get(), SQLITE_DBCONFIG_ENABLE_TRIGGER, 1, &changed);
        if (result != SQLITE_OK || changed != 1) {
            throw std::runtime_error(
                "TLS membership test could not mutate trigger profile");
        }
        checks.require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "connection profile changed after owner configuration",
            "membership owner reused authority after connection-profile mutation");
        const int restored = sqlite3_db_config(
            database.db.get(), SQLITE_DBCONFIG_ENABLE_TRIGGER, 0, &changed);
        if (restored != SQLITE_OK || changed != 0) {
            throw std::runtime_error(
                "TLS membership test could not restore trigger profile");
        }
#endif
    }

    {
        SyncSqliteDb database =
            open_database(workspace.path("attached.sqlite3"));
        sqlite_exec_or_throw(
            database.db, "ATTACH DATABASE ':memory:' AS injected;",
            "TLS membership attached-database fixture");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, "membership-profile-owned-folder",
                    {"membership-profile-owned-local", 7061U},
                    "TLS membership attached-database owner");
            },
            "attached database outside owner authority",
            "membership owner admitted an attached schema on its authority connection");
    }
}

void test_durable_backend_profile(Checks& checks) {
    TempMembershipWorkspace workspace("anonsync-membership-backend-profile");

    {
        SyncSqliteDb database =
            open_database(workspace.path("synchronous-off.sqlite3"), false);
        sqlite_exec_or_throw(
            database.db, "PRAGMA synchronous=OFF;",
            "TLS membership synchronous-off fixture");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, "membership-profile-folder",
                    {"membership-profile-local", 7051U},
                    "TLS membership synchronous-off owner");
            },
            "rollback-journal synchronous mode is below EXTRA",
            "membership owner minted durable authority with synchronous OFF");
    }

    {
        SyncSqliteDb database =
            open_database(workspace.path("rollback-full.sqlite3"), false);
        sqlite_exec_or_throw(
            database.db, "PRAGMA synchronous=FULL;",
            "TLS membership rollback FULL fixture");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, "membership-profile-folder",
                    {"membership-profile-local", 7051U},
                    "TLS membership rollback FULL owner");
            },
            "rollback-journal synchronous mode is below EXTRA",
            "membership owner overstated rollback-journal FULL durability");
    }

    {
        SyncSqliteDb database =
            open_database(workspace.path("wal-normal.sqlite3"));
        sqlite_exec_or_throw(
            database.db, "PRAGMA synchronous=NORMAL;",
            "TLS membership WAL NORMAL fixture");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, "membership-profile-folder",
                    {"membership-profile-local", 7051U},
                    "TLS membership WAL NORMAL owner");
            },
            "WAL synchronous mode is below FULL",
            "membership owner overstated WAL NORMAL durability");
    }

    {
        SyncSqliteDb database =
            open_database(workspace.path("memory-journal.sqlite3"), false);
        sqlite_exec_or_throw(
            database.db,
            "PRAGMA journal_mode=MEMORY;PRAGMA synchronous=FULL;",
            "TLS membership memory-journal fixture");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, "membership-profile-folder",
                    {"membership-profile-local", 7051U},
                    "TLS membership memory-journal owner");
            },
            "journal mode is not durable",
            "membership owner minted durable authority in memory journal mode");
    }

    {
        SyncSqliteDb database;
        const int result = sqlite3_open_v2(
            ":memory:", database.db.out(),
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE,
            nullptr);
        if (result != SQLITE_OK) {
            throw std::runtime_error(sqlite_error_message(
                database.db, "TLS membership memory database open"));
        }
        sqlite_set_busy_timeout_or_throw(
            database.db, 5000, "TLS membership memory database timeout");
        sqlite_exec_or_throw(
            database.db, "PRAGMA synchronous=FULL;",
            "TLS membership memory database profile");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, "membership-profile-folder",
                    {"membership-profile-local", 7051U},
                    "TLS membership memory database owner");
            },
            "no durable main filename",
            "membership owner minted durable authority in an in-memory database");
    }
}

void test_history_cas_and_external_anchor(Checks& checks) {
    TempMembershipWorkspace workspace("anonsync-membership-history");
    const auto current_path = workspace.path("membership.sqlite3");
    const auto rollback_path = workspace.path("membership-rollback.sqlite3");
    const auto entry_tamper_path = workspace.path("membership-entry-tamper.sqlite3");
    const auto chain_tamper_path = workspace.path("membership-chain-tamper.sqlite3");
    const auto orphan_path = workspace.path("membership-orphan.sqlite3");
    const auto schema_tamper_path = workspace.path("membership-schema-tamper.sqlite3");
    const auto temp_trigger_path = workspace.path("membership-temp-trigger.sqlite3");

    const std::string folder = "membership-durable-folder";
    const SyncReplicaActor local{"membership-durable-local", 7101U};
    const SyncReplicaActor peer_a{"membership-durable-peer-a", 7102U};
    const SyncReplicaActor peer_b{"membership-durable-peer-b", 7103U};
    const SyncReplicaActor peer_c{"membership-durable-peer-c", 7104U};
    const std::string peer_a_pin = sha256_hex("membership durable peer a");
    const std::string peer_b_pin = sha256_hex("membership durable peer b");
    const std::string peer_c_pin = sha256_hex("membership durable peer c");

    SyncReplicaTlsMembershipAnchor genesis_anchor;
    SyncReplicaTlsMembershipAnchor generation_one_anchor;
    SyncReplicaTlsMembershipAnchor generation_two_anchor;
    std::string generation_one_snapshot_digest;
    std::string generation_two_snapshot_digest;

    {
        SyncSqliteDb database = open_database(current_path);
        SyncReplicaTlsMembershipSqliteOwner owner(
            database.db, folder, local,
            "TLS membership durable owner generation one");
        const auto empty = owner.snapshot_or_throw();
        genesis_anchor = empty.anchor();
        checks.require(
            empty.folder_id == folder && empty.local_actor == local &&
                empty.state_generation == 0U &&
                empty.current_policy_epoch == 0U &&
                empty.current_entry_count == 0U && empty.history.empty() &&
                !empty.current_authority.has_value() &&
                is_lowercase_sha256_hex(genesis_anchor.chain_digest),
            "new membership database did not expose exact genesis authority");
        checks.require_error(
            [&] { (void)owner.current_authority_or_throw(); },
            "no published membership authority",
            "empty membership history minted accepted-session authority");
        checks.require_error(
            [&] {
                (void)owner.publish_or_throw(
                    genesis_anchor, 99U,
                    {{sha256_hex("membership oversized actor epoch"),
                      {"membership-oversized-peer",
                       std::numeric_limits<std::uint64_t>::max()}}});
            },
            "member actor epoch exceeds SQLite integer range",
            "membership owner entered its write cutpoint with an unpersistable actor epoch");
        checks.require(
            owner.snapshot_or_throw().anchor() == genesis_anchor,
            "rejected unpersistable actor epoch mutated membership authority");

        auto authority = owner.publish_or_throw(
            genesis_anchor, 100U, first_entries(peer_a, peer_b));
        generation_one_anchor = authority.anchor();
        generation_one_snapshot_digest = authority.snapshot().snapshot_digest();
        checks.require(
            authority.active() && authority.state_generation() == 1U &&
                authority.previous_chain_digest() == genesis_anchor.chain_digest &&
                authority.chain_digest() == generation_one_anchor.chain_digest &&
                authority.snapshot().policy_epoch() == 100U &&
                authority.snapshot().entry_count() == 2U &&
                authority.snapshot().entries()[0].spki_sha256 <
                    authority.snapshot().entries()[1].spki_sha256 &&
                authority.snapshot().resolve_peer_or_throw(peer_a_pin) == peer_a &&
                authority.snapshot().resolve_peer_or_throw(peer_b_pin) == peer_b,
            "committed membership authority lost canonical policy evidence");

        auto moved = std::move(authority);
        checks.require(
            !authority.active() && moved.active() &&
                moved.anchor() == generation_one_anchor,
            "move-only membership authority duplicated or lost one session capability");
        checks.require_error(
            [&] { (void)authority.snapshot(); }, "inactive",
            "moved-from membership authority remained usable");

        const auto restored = owner.snapshot_or_throw(genesis_anchor);
        checks.require(
            restored.state_generation == 1U && restored.history.size() == 1U &&
                restored.current_authority.has_value() &&
                restored.current_snapshot_digest == generation_one_snapshot_digest &&
                restored.current_authority->anchor() == generation_one_anchor,
            "membership owner did not reconstruct generation one from exact rows");

        const auto before_stale = owner.snapshot_or_throw();
        checks.require_error(
            [&] {
                (void)owner.publish_or_throw(
                    genesis_anchor, 101U, {{peer_c_pin, peer_c}});
            },
            "expected-current anchor is stale",
            "membership publication accepted a stale compare-and-swap anchor");
        checks.require(
            owner.snapshot_or_throw().anchor() == before_stale.anchor(),
            "stale membership compare-and-swap mutated durable authority");
        checks.require_error(
            [&] {
                (void)owner.publish_or_throw(
                    generation_one_anchor, 100U, {{peer_c_pin, peer_c}});
            },
            "policy epoch must advance monotonically",
            "membership publication reused a committed policy epoch");
        checks.require(
            owner.snapshot_or_throw().anchor() == generation_one_anchor,
            "nonmonotonic membership policy epoch mutated durable authority");
        checkpoint_or_throw(database);
    }
    clone_database_file_or_throw(current_path, rollback_path);

    {
        SyncSqliteDb first_database = open_database(current_path);
        SyncSqliteDb stale_database = open_database(current_path);
        SyncReplicaTlsMembershipSqliteOwner first_owner(
            first_database.db, folder, local,
            "TLS membership generation two publisher");
        SyncReplicaTlsMembershipSqliteOwner stale_owner(
            stale_database.db, folder, local,
            "TLS membership stale concurrent publisher");
        const auto stale_cutpoint = stale_owner.snapshot_or_throw().anchor();
        auto authority = first_owner.publish_or_throw(
            generation_one_anchor, 200U,
            {{peer_c_pin, peer_c}, {peer_a_pin, peer_a}});
        generation_two_anchor = authority.anchor();
        generation_two_snapshot_digest = authority.snapshot().snapshot_digest();
        checks.require(
            authority.state_generation() == 2U &&
                authority.previous_chain_digest() ==
                    generation_one_anchor.chain_digest &&
                authority.snapshot().policy_epoch() == 200U &&
                authority.snapshot().resolve_peer_or_throw(peer_a_pin) == peer_a &&
                authority.snapshot().resolve_peer_or_throw(peer_c_pin) == peer_c &&
                !authority.snapshot().resolve_peer_or_throw(peer_b_pin).has_value(),
            "membership rotation did not replace the exact prior snapshot");
        checks.require_error(
            [&] {
                (void)stale_owner.publish_or_throw(
                    stale_cutpoint, 201U, {{peer_b_pin, peer_b}});
            },
            "expected-current anchor is stale",
            "second SQLite connection overwrote a newer membership generation");
        const auto observed = stale_owner.snapshot_or_throw(generation_one_anchor);
        checks.require(
            observed.anchor() == generation_two_anchor &&
                observed.history.size() == 2U,
            "stale membership owner did not reconstruct the winning generation");
        checkpoint_or_throw(first_database);
    }

    {
        SyncSqliteDb database = open_database(current_path);
        SyncReplicaTlsMembershipSqliteOwner owner(
            database.db, folder, local,
            "TLS membership restart reconstruction");
        const auto snapshot = owner.snapshot_or_throw(generation_one_anchor);
        checks.require(
            snapshot.state_generation == 2U && snapshot.history.size() == 2U &&
                snapshot.history[0].chain_digest ==
                    generation_one_anchor.chain_digest &&
                snapshot.history[1].previous_chain_digest ==
                    generation_one_anchor.chain_digest &&
                snapshot.current_snapshot_digest == generation_two_snapshot_digest &&
                snapshot.anchor() == generation_two_anchor,
            "membership restart lost append-only chain continuity");
        auto current = owner.current_authority_or_throw(generation_two_anchor);
        checks.require(
            current.anchor() == generation_two_anchor &&
                current.snapshot().snapshot_digest() ==
                    generation_two_snapshot_digest,
            "membership restart did not remint exact current authority");

        SyncReplicaTlsMembershipAnchor divergent = generation_one_anchor;
        divergent.chain_digest = sha256_hex("membership divergent anchor");
        checks.require_error(
            [&] { (void)owner.snapshot_or_throw(divergent); },
            "diverges from trusted anchor",
            "membership owner accepted a fork through a retained generation");
        const SyncReplicaTlsMembershipAnchor future{
            generation_two_anchor.state_generation + 1U,
            sha256_hex("membership future anchor")};
        checks.require_error(
            [&] { (void)owner.snapshot_or_throw(future); },
            "rolled back below trusted generation",
            "membership owner accepted a database older than trusted state");
        checkpoint_or_throw(database);
    }

    {
        SyncSqliteDb database = open_database(rollback_path);
        SyncReplicaTlsMembershipSqliteOwner owner(
            database.db, folder, local,
            "TLS membership rolled-back database");
        checks.require(
            owner.snapshot_or_throw().anchor() == generation_one_anchor,
            "unanchored rollback fixture was not internally valid generation one");
        checks.require_error(
            [&] { (void)owner.snapshot_or_throw(generation_two_anchor); },
            "rolled back below trusted generation",
            "external membership anchor did not detect whole-database rollback");
    }

    {
        SyncSqliteDb database = open_database(current_path);
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner wrong_folder(
                    database.db, "membership-wrong-folder", local,
                    "TLS membership wrong-folder owner");
            },
            "identity does not match owner",
            "membership database crossed folder identity");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner wrong_local(
                    database.db, folder,
                    {"membership-wrong-local", local.epoch},
                    "TLS membership wrong-local owner");
            },
            "identity does not match owner",
            "membership database crossed local actor identity");
    }

    clone_database_file_or_throw(current_path, entry_tamper_path);
    clone_database_file_or_throw(current_path, chain_tamper_path);
    clone_database_file_or_throw(current_path, orphan_path);
    clone_database_file_or_throw(current_path, schema_tamper_path);
    clone_database_file_or_throw(current_path, temp_trigger_path);

    {
        SyncSqliteDb database = open_database(entry_tamper_path);
        sqlite_exec_or_throw(
            database.db,
            "UPDATE sync_replica_tls_membership_entries "
            "SET actor_epoch=actor_epoch+1 WHERE state_generation=1 "
            "AND spki_sha256=(SELECT min(spki_sha256) FROM "
            "sync_replica_tls_membership_entries WHERE state_generation=1);",
            "TLS membership entry tamper");
    }
    {
        SyncSqliteDb database = open_database(entry_tamper_path);
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, folder, local,
                    "TLS membership entry-tamper owner");
            },
            "snapshot digest mismatch",
            "membership owner trusted rows that no longer match snapshot digest");
    }

    {
        SyncSqliteDb database = open_database(chain_tamper_path);
        const std::string replacement = sha256_hex("membership chain tamper");
        sqlite_exec_or_throw(
            database.db,
            "UPDATE sync_replica_tls_membership_updates SET chain_digest='" +
                replacement + "' WHERE state_generation=2;"
                "UPDATE sync_replica_tls_membership_meta SET "
                "current_chain_digest='" + replacement + "';",
            "TLS membership chain tamper");
    }
    {
        SyncSqliteDb database = open_database(chain_tamper_path);
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, folder, local,
                    "TLS membership chain-tamper owner");
            },
            "chain digest mismatch",
            "membership owner trusted a rewritten append-only chain digest");
    }

    {
        SyncSqliteDb database = open_database(orphan_path);
        sqlite_exec_or_throw(
            database.db,
            "INSERT INTO sync_replica_tls_membership_entries("
            "state_generation,spki_sha256,actor_device_id,actor_epoch) VALUES("
            "99,'" + sha256_hex("membership orphan row") +
                "','membership-orphan-peer',7999);",
            "TLS membership orphan insertion");
    }
    {
        SyncSqliteDb database = open_database(orphan_path);
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, folder, local,
                    "TLS membership orphan-row owner");
            },
            "orphan rows",
            "membership owner ignored unowned retained entry rows");
    }

    {
        SyncSqliteDb database = open_database(schema_tamper_path);
        sqlite_exec_or_throw(
            database.db,
            "CREATE INDEX unowned_membership_index ON "
            "sync_replica_tls_membership_entries(actor_device_id);",
            "TLS membership schema tamper");
    }
    {
        SyncSqliteDb database = open_database(schema_tamper_path);
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, folder, local,
                    "TLS membership schema-tamper owner");
            },
            "schema object count mismatch",
            "membership owner admitted an unowned schema object");
    }


    {
        SyncSqliteDb database = open_database(temp_trigger_path);
        sqlite_exec_or_throw(
            database.db,
            "CREATE TEMP TRIGGER unowned_membership_temp_trigger "
            "AFTER INSERT ON main.sync_replica_tls_membership_entries "
            "BEGIN SELECT 1; END;",
            "TLS membership temp trigger fixture");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipSqliteOwner owner(
                    database.db, folder, local,
                    "TLS membership temp-trigger owner");
            },
            "unowned temp schema attachments",
            "membership owner admitted a connection-local trigger on its tables");
    }

    checks.require(
        generation_one_anchor != generation_two_anchor &&
            generation_one_snapshot_digest != generation_two_snapshot_digest,
        "membership history fixture failed to rotate durable authority");
}

}  // namespace

std::size_t run_sync_replica_tls_membership_sqlite_owner_tests() {
    Checks checks;
    test_serialized_first_open(checks);
    test_detached_bootstrap_image_profile(checks);
    test_connection_profile_and_retention_admission(checks);
    test_durable_backend_profile(checks);
    test_history_cas_and_external_anchor(checks);
    return checks.count();
}

}  // namespace anonsync::test
