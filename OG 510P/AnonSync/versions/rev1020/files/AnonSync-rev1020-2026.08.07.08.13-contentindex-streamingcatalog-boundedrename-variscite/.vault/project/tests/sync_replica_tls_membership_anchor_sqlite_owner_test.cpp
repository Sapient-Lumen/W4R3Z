#include "sync_replica_tls_membership_anchor_sqlite_owner_test.hpp"

#include "sha256_digest.hpp"
#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"
#include "sync_replica_tls_membership_anchored_owner.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#include <array>
#include <barrier>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
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

static_assert(!std::is_copy_constructible_v<
              SyncReplicaTlsMembershipAnchorSqliteOwner>);
static_assert(!std::is_move_constructible_v<
              SyncReplicaTlsMembershipAnchorSqliteOwner>);
static_assert(!std::is_copy_constructible_v<
              SyncReplicaTlsMembershipAnchoredOwner>);
static_assert(!std::is_move_constructible_v<
              SyncReplicaTlsMembershipAnchoredOwner>);
static_assert(!std::is_constructible_v<
              SyncReplicaTlsAnchoredMembershipAuthority,
              SyncReplicaTlsMembershipAuthority>);

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

class TempAnchorWorkspace final {
public:
    explicit TempAnchorWorkspace(std::string_view stem) {
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

    ~TempAnchorWorkspace() {
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
    int busy_timeout_ms = 5000) {
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
            owner.db, "TLS membership anchor test open"));
    }
    sqlite_set_busy_timeout_or_throw(
        owner.db, busy_timeout_ms,
        "TLS membership anchor test busy timeout");
    sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "TLS membership anchor test durability profile");
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
            owner.db, "TLS membership anchor detached owner test open"));
    }
    sqlite_set_busy_timeout_or_throw(
        owner.db, 5000,
        "TLS membership anchor detached owner test busy timeout");
    return owner;
}

void checkpoint_or_throw(SyncSqliteDb& database) {
    sqlite_exec_or_throw(
        database.db, "PRAGMA wal_checkpoint(TRUNCATE);",
        "TLS membership anchor test checkpoint");
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
            "TLS membership anchor test could not clone database: " +
            error.message());
    }
}

[[nodiscard]] std::vector<SyncReplicaTlsMembershipEntry> entries_for(
    std::string_view generation_label,
    std::uint64_t epoch_base) {
    return {
        {sha256_hex(std::string(generation_label) + " pin a"),
         {"anchor-peer-a", epoch_base + 1U}},
        {sha256_hex(std::string(generation_label) + " pin b"),
         {"anchor-peer-b", epoch_base + 2U}},
    };
}

void test_anchor_owner_cas_restart_and_tamper(Checks& checks) {
    TempAnchorWorkspace workspace("anonsync-membership-anchor-owner");
    const auto membership_path = workspace.path("membership.sqlite3");
    const auto anchor_path = workspace.path("anchor.sqlite3");
    const auto tamper_path = workspace.path("anchor-tamper.sqlite3");
    const std::string folder = "anchor-owner-folder";
    const SyncReplicaActor local{"anchor-owner-local", 8101U};

    SyncReplicaTlsMembershipAnchor generation_one;
    SyncReplicaTlsMembershipAnchor generation_two;
    {
        SyncSqliteDb database = open_database(membership_path);
        SyncReplicaTlsMembershipSqliteOwner owner(
            database.db, folder, local,
            "TLS membership anchor fixture membership owner");
        const auto genesis = owner.snapshot_or_throw().anchor();
        generation_one = owner.publish_or_throw(
            genesis, 100U, entries_for("anchor generation one", 8200U))
                             .anchor();
        generation_two = owner.publish_or_throw(
            generation_one, 200U,
            entries_for("anchor generation two", 8300U))
                             .anchor();
        checkpoint_or_throw(database);
    }

    const SyncReplicaTlsMembershipAnchor genesis =
        sync_replica_tls_membership_genesis_anchor_or_throw(
            folder, local, "TLS anchor test genesis");
    {
        SyncSqliteDb database = open_database(anchor_path);
        SyncReplicaTlsMembershipAnchorSqliteOwner owner(
            database.db, folder, local,
            "TLS independent membership anchor owner");
        const auto initial = owner.snapshot_or_throw();
        checks.require(
            initial.current_anchor == genesis && initial.history.empty() &&
                initial.transition_sequence == 0U &&
                is_lowercase_sha256_hex(initial.current_transition_digest),
            "membership anchor store did not begin at canonical genesis");

        const auto first = owner.advance_or_throw(genesis, generation_one);
        checks.require(
            first.disposition ==
                    SyncReplicaTlsMembershipAnchorAdvanceDisposition::Advanced &&
                first.observed_before == genesis &&
                first.durable_after == generation_one &&
                first.transition_sequence == 1U &&
                is_lowercase_sha256_hex(first.transition_digest),
            "membership anchor did not advance exact genesis CAS");
        const auto retry = owner.advance_or_throw(genesis, generation_one);
        checks.require(
            retry.disposition ==
                    SyncReplicaTlsMembershipAnchorAdvanceDisposition::
                        AlreadyCurrent &&
                retry.durable_after == generation_one &&
                retry.transition_sequence == 1U,
            "membership anchor did not make an ambiguous exact retry idempotent");
        const auto stale = owner.advance_or_throw(genesis, generation_two);
        checks.require(
            stale.disposition ==
                    SyncReplicaTlsMembershipAnchorAdvanceDisposition::
                        StaleExpected &&
                stale.observed_before == generation_one &&
                stale.durable_after == generation_one,
            "membership anchor stale CAS mutated or concealed current state");
        const auto second =
            owner.advance_or_throw(generation_one, generation_two);
        checks.require(
            second.disposition ==
                    SyncReplicaTlsMembershipAnchorAdvanceDisposition::Advanced &&
                second.transition_sequence == 2U &&
                second.durable_after == generation_two,
            "membership anchor did not append its second exact transition");
        checks.require_error(
            [&] {
                (void)owner.advance_or_throw(
                    generation_two, generation_two);
            },
            "advance generation strictly",
            "membership anchor accepted a non-monotonic transition");
        checkpoint_or_throw(database);
    }

    {
        SyncSqliteDb database = open_database(anchor_path);
        SyncReplicaTlsMembershipAnchorSqliteOwner owner(
            database.db, folder, local,
            "TLS membership anchor restart owner");
        const auto snapshot = owner.snapshot_or_throw();
        checks.require(
            snapshot.current_anchor == generation_two &&
                snapshot.transition_sequence == 2U &&
                snapshot.history.size() == 2U &&
                snapshot.history[0].previous_anchor == genesis &&
                snapshot.history[0].current_anchor == generation_one &&
                snapshot.history[1].previous_anchor == generation_one &&
                snapshot.history[1].current_anchor == generation_two &&
                snapshot.history[1].previous_transition_digest ==
                    snapshot.history[0].transition_digest,
            "membership anchor restart did not reconstruct its digest chain");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipAnchorSqliteOwner wrong(
                    database.db, "anchor-wrong-folder", local,
                    "TLS membership anchor wrong-folder owner");
            },
            "identity does not match owner",
            "membership anchor crossed folder identity");
        checkpoint_or_throw(database);
    }

    clone_database_file_or_throw(anchor_path, tamper_path);
    {
        SyncSqliteDb database = open_database(tamper_path);
        sqlite_exec_or_throw(
            database.db,
            "UPDATE sync_replica_tls_membership_anchor_updates "
            "SET transition_digest='" +
                sha256_hex("rewritten anchor transition") +
                "' WHERE transition_sequence=2;"
                "UPDATE sync_replica_tls_membership_anchor_meta "
                "SET current_transition_digest='" +
                sha256_hex("rewritten anchor transition") + "';",
            "TLS membership anchor transition tamper");
    }
    {
        SyncSqliteDb database = open_database(tamper_path);
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipAnchorSqliteOwner owner(
                    database.db, folder, local,
                    "TLS membership anchor tamper owner");
            },
            "transition digest mismatch",
            "membership anchor trusted a rewritten transition digest");
    }

    {
        SyncSqliteDb database = open_database(anchor_path);
        SyncReplicaTlsMembershipAnchorSqliteOwner owner(
            database.db, folder, local,
            "TLS membership anchor mutable-profile owner");
        sqlite_exec_or_throw(
            database.db, "PRAGMA query_only=ON;",
            "TLS membership anchor query-only mutation");
        checks.require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "mutable connection pragma escaped",
            "membership anchor did not re-attest its SQLite connection profile");
    }
}

void test_detached_bootstrap_image_profile(Checks& checks) {
    const std::string folder = "anchor-detached-folder";
    const SyncReplicaActor local{"anchor-detached-local", 8091U};
    SyncSqliteDb database = open_detached_database();
    SyncReplicaTlsMembershipAnchorSqliteOwner owner(
        database.db, folder, local,
        SyncReplicaTlsPolicySqliteBackendDisposition::DetachedBootstrapImage,
        "TLS membership anchor detached bootstrap owner");
    const auto genesis = owner.snapshot_or_throw();
    checks.require(
        owner.database_filename().empty() && genesis.history.empty() &&
            genesis.transition_sequence == 0U &&
            genesis.current_anchor.state_generation == 0U,
        "detached membership-anchor owner did not expose exact genesis");
    const SyncReplicaTlsMembershipAnchor next{
        1U, sha256_hex("detached membership anchor forbidden advance")};
    checks.require_error(
        [&] {
            (void)owner.advance_or_throw(genesis.current_anchor, next);
        },
        "detached bootstrap image cannot advance membership anchor",
        "detached membership-anchor owner crossed into durable advancement");

    SyncSqliteDb ordinary_rejection = open_detached_database();
    checks.require_error(
        [&] {
            SyncReplicaTlsMembershipAnchorSqliteOwner named_owner(
                ordinary_rejection.db, folder, local,
                "TLS membership anchor detached ordinary-owner rejection");
        },
        "has no durable main filename",
        "ordinary membership-anchor owner admitted anonymous SQLite authority");

    SyncSqliteDb forensic_owner_rejection = open_detached_database();
    checks.require_error(
        [&] {
            SyncReplicaTlsMembershipAnchorSqliteOwner forbidden_owner(
                forensic_owner_rejection.db, folder, local,
                SyncReplicaTlsPolicySqliteBackendDisposition::
                    ForensicReadOnlyNamed,
                "TLS membership anchor forensic owner rejection");
        },
        "forensic read-only disposition cannot own mutable TLS policy authority",
        "membership-anchor owner admitted forensic observation as mutable authority");
}

void test_policy_connection_binding_and_path_alias(Checks& checks) {
    TempAnchorWorkspace workspace("anonsync-membership-policy-binding");
    const std::string folder = "anchor-binding-folder";
    const SyncReplicaActor local{"anchor-binding-local", 8701U};

    const auto membership_path = workspace.path("membership.sqlite3");
    SyncSqliteDb moved_membership_database;
    {
        SyncSqliteDb membership_database = open_database(membership_path);
        SyncReplicaTlsMembershipSqliteOwner owner(
            membership_database.db, folder, local,
            "TLS exact-generation membership history owner");
        moved_membership_database = std::move(membership_database);
        checks.require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "exact SQLite handle-slot generation changed",
            "membership owner silently followed a moved/refilled handle slot");
    }

    const auto renamed_membership_path =
        workspace.path("renamed-membership.sqlite3");
    const auto displaced_membership_path =
        workspace.path("renamed-membership.displaced.sqlite3");
    {
        SyncSqliteDb database = open_database(renamed_membership_path);
        SyncReplicaTlsMembershipSqliteOwner owner(
            database.db, folder, local,
            "TLS renamed-path membership history owner");
        std::filesystem::rename(
            renamed_membership_path, displaced_membership_path);
        std::string rejection;
        try {
            (void)owner.snapshot_or_throw();
        } catch (const std::exception& error) {
            rejection = error.what();
        }
        std::filesystem::rename(
            displaced_membership_path, renamed_membership_path);
        checks.require(
            rejection.find("was not created or opened") != std::string::npos ||
                rejection.find("moved after open") != std::string::npos ||
                rejection.find("identity changed") != std::string::npos,
            "membership owner continued after its live main database path moved: " +
                rejection);
    }

    const auto anchor_path = workspace.path("anchor.sqlite3");
    SyncSqliteDb moved_anchor_database;
    {
        SyncSqliteDb anchor_database = open_database(anchor_path);
        SyncReplicaTlsMembershipAnchorSqliteOwner owner(
            anchor_database.db, folder, local,
            "TLS exact-generation membership anchor owner");
        moved_anchor_database = std::move(anchor_database);
        checks.require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "exact SQLite handle-slot generation changed",
            "membership anchor owner silently followed a moved/refilled handle slot");
    }

    const auto shared_path = workspace.path("shared.sqlite3");
    {
        SyncSqliteDb shared_database = open_database(shared_path);
        checkpoint_or_throw(shared_database);
    }
    const auto alias_directory = workspace.path("alias-hop");
    std::filesystem::create_directories(alias_directory);
    const auto aliased_path =
        alias_directory / ".." / shared_path.filename();
    checks.require_error(
        [&] {
            require_distinct_sync_replica_tls_policy_sqlite_databases_or_throw(
                shared_path.string(), aliased_path.string(),
                "TLS policy database alias preflight");
        },
        "alias the same filesystem object",
        "distinct-database preflight accepted a lexical alias of one file");
}

void test_coordinator_rejects_same_database_file(Checks& checks) {
    TempAnchorWorkspace workspace("anonsync-membership-anchor-same-file");
    const auto shared_path = workspace.path("shared.sqlite3");
    const auto alias_source_path = workspace.path("alias-source.sqlite3");
    const auto alias_path = workspace.path("alias.sqlite3");
    const std::string folder = "anchor-same-file-folder";
    const SyncReplicaActor local{"anchor-same-file-local", 8901U};

    SyncSqliteDb membership_database = open_database(shared_path);
    SyncSqliteDb anchor_database = open_database(shared_path);
    SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, folder, local,
        "TLS same-file membership history owner");
    SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.db, folder, local,
        "TLS same-file membership anchor owner");
    checks.require_error(
        [&] {
            SyncReplicaTlsMembershipAnchoredOwner coordinator(
                membership_owner, anchor_owner,
                "TLS same-file anchored membership coordinator");
        },
        "same main database file",
        "membership and rollback anchor silently shared one failure domain");

    {
        SyncSqliteDb alias_source = open_database(alias_source_path);
        checkpoint_or_throw(alias_source);
    }
    std::error_code alias_error;
    std::filesystem::create_hard_link(
        alias_source_path, alias_path, alias_error);
    if (alias_error) {
        throw std::runtime_error(
            "TLS membership anchor test could not create hard-link alias: " +
            alias_error.message());
    }
    checks.require_error(
        [&] {
            require_distinct_sync_replica_tls_policy_sqlite_databases_or_throw(
                alias_source_path.string(), alias_path.string(),
                "TLS hard-link alias preflight");
        },
        "alias the same filesystem object",
        "membership and rollback anchor accepted different names for one filesystem object");
}

void test_coordinator_commit_gap_recovery_and_race(Checks& checks) {
    TempAnchorWorkspace workspace("anonsync-membership-anchor-coordinator");
    const auto membership_path = workspace.path("membership.sqlite3");
    const auto anchor_path = workspace.path("anchor.sqlite3");
    const std::string folder = "anchored-membership-folder";
    const SyncReplicaActor local{"anchored-membership-local", 9101U};

    SyncReplicaTlsMembershipAnchor generation_one;
    {
        SyncSqliteDb membership_database = open_database(membership_path);
        SyncSqliteDb anchor_database = open_database(anchor_path, 50);
        SyncReplicaTlsMembershipSqliteOwner membership_owner(
            membership_database.db, folder, local,
            "TLS anchored membership primary history owner");
        SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
            anchor_database.db, folder, local,
            "TLS anchored membership primary anchor owner");
        SyncReplicaTlsMembershipAnchoredOwner coordinator(
            membership_owner, anchor_owner,
            "TLS anchored membership primary coordinator");

        const auto genesis = membership_owner.snapshot_or_throw().anchor();

        // Hold an independent anchor writer lock. WAL readers remain available,
        // so coordinator preflight succeeds and the membership transaction can
        // commit; only the post-commit anchor advance fails. This deterministically
        // exercises the unavoidable two-database crash/failure gap.
        SyncSqliteDb lock_database = open_database(anchor_path);
        sqlite_exec_or_throw(
            lock_database.db, "BEGIN IMMEDIATE;",
            "TLS membership anchor gap writer lock");
        checks.require_error(
            [&] {
                (void)coordinator.publish_or_throw(
                    genesis, 100U,
                    entries_for("coordinator generation one", 9200U));
            },
            "locked",
            "anchored membership unexpectedly emitted authority while anchor commit was blocked");

        const auto committed_membership = membership_owner.snapshot_or_throw();
        const auto retained_anchor = anchor_owner.snapshot_or_throw();
        checks.require(
            committed_membership.state_generation == 1U &&
                retained_anchor.current_anchor == genesis,
            "two-store failure fixture did not leave membership ahead of anchor");
        generation_one = committed_membership.anchor();
        sqlite_exec_or_throw(
            lock_database.db, "ROLLBACK;",
            "TLS membership anchor release gap writer lock");

        auto recovered = coordinator.current_authority_or_throw();
        checks.require(
            recovered.anchor() == generation_one &&
                recovered.durable_anchor() == generation_one &&
                anchor_owner.snapshot_or_throw().current_anchor == generation_one,
            "restart-style reconciliation did not close membership/anchor gap before authority emission");

        // Advance membership twice without using the coordinator, modeling two
        // committed generations before recovery. Reconciliation may safely jump
        // the external anchor directly because it proves both endpoints on the
        // complete retained membership chain.
        auto generation_two_authority = membership_owner.publish_or_throw(
            generation_one, 200U,
            entries_for("coordinator generation two", 9300U));
        const auto generation_two = generation_two_authority.anchor();
        auto generation_three_authority = membership_owner.publish_or_throw(
            generation_two, 300U,
            entries_for("coordinator generation three", 9400U));
        const auto generation_three = generation_three_authority.anchor();
        checks.require(
            anchor_owner.snapshot_or_throw().current_anchor == generation_one,
            "direct membership fixture accidentally advanced independent anchor");
        checkpoint_or_throw(membership_database);
        checkpoint_or_throw(anchor_database);

        (void)generation_three;
    }

    std::barrier start(2);
    std::array<std::exception_ptr, 2U> errors{};
    std::array<SyncReplicaTlsMembershipAnchor, 2U> authorities{};
    auto reconcile = [&](std::size_t index) {
        try {
            SyncSqliteDb membership_database = open_database(membership_path);
            SyncSqliteDb anchor_database = open_database(anchor_path);
            SyncReplicaTlsMembershipSqliteOwner membership_owner(
                membership_database.db, folder, local,
                "TLS anchored membership racing history owner");
            SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
                anchor_database.db, folder, local,
                "TLS anchored membership racing anchor owner");
            SyncReplicaTlsMembershipAnchoredOwner coordinator(
                membership_owner, anchor_owner,
                "TLS anchored membership racing coordinator");
            start.arrive_and_wait();
            authorities[index] =
                coordinator.current_authority_or_throw().anchor();
        } catch (...) {
            errors[index] = std::current_exception();
        }
    };

    std::thread left(reconcile, 0U);
    std::thread right(reconcile, 1U);
    left.join();
    right.join();
    if (errors[0]) std::rethrow_exception(errors[0]);
    if (errors[1]) std::rethrow_exception(errors[1]);
    checks.require(
        authorities[0] == authorities[1] &&
            authorities[0].state_generation == 3U,
        "concurrent anchor reconciliation did not converge on exact current authority");

    {
        SyncSqliteDb membership_database = open_database(membership_path);
        SyncSqliteDb anchor_database = open_database(anchor_path);
        SyncReplicaTlsMembershipSqliteOwner membership_owner(
            membership_database.db, folder, local,
            "TLS anchored membership converged history owner");
        SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
            anchor_database.db, folder, local,
            "TLS anchored membership converged anchor owner");
        const auto membership = membership_owner.snapshot_or_throw();
        const auto anchor = anchor_owner.snapshot_or_throw();
        checks.require(
            anchor.current_anchor == membership.anchor() &&
                anchor.transition_sequence == 2U &&
                anchor.history.size() == 2U &&
                anchor.history[0].current_anchor == generation_one &&
                anchor.history[1].previous_anchor == generation_one &&
                anchor.history[1].current_anchor == membership.anchor(),
            "anchor reconciliation did not retain one exact crash recovery jump");
    }
}

void test_coordinator_rollback_and_fork_rejection(Checks& checks) {
    TempAnchorWorkspace workspace("anonsync-membership-anchor-rollback");
    const auto primary_membership_path = workspace.path("primary-membership.sqlite3");
    const auto primary_anchor_path = workspace.path("primary-anchor.sqlite3");
    const auto rollback_membership_path = workspace.path("rollback-membership.sqlite3");
    const auto fork_membership_path = workspace.path("fork-membership.sqlite3");
    const auto fork_anchor_path = workspace.path("fork-anchor.sqlite3");
    const std::string folder = "anchor-rollback-folder";
    const SyncReplicaActor local{"anchor-rollback-local", 10101U};

    SyncReplicaTlsMembershipAnchor generation_one;
    SyncReplicaTlsMembershipAnchor generation_two;
    {
        SyncSqliteDb membership_database = open_database(primary_membership_path);
        SyncSqliteDb anchor_database = open_database(primary_anchor_path);
        SyncReplicaTlsMembershipSqliteOwner membership_owner(
            membership_database.db, folder, local,
            "TLS rollback primary history owner");
        SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
            anchor_database.db, folder, local,
            "TLS rollback primary anchor owner");
        SyncReplicaTlsMembershipAnchoredOwner coordinator(
            membership_owner, anchor_owner,
            "TLS rollback primary coordinator");
        const auto genesis = membership_owner.snapshot_or_throw().anchor();
        generation_one = coordinator.publish_or_throw(
            genesis, 100U, entries_for("rollback generation one", 10200U))
                             .anchor();
        checkpoint_or_throw(membership_database);
        clone_database_file_or_throw(
            primary_membership_path, rollback_membership_path);
        generation_two = coordinator.publish_or_throw(
            generation_one, 200U,
            entries_for("rollback generation two", 10300U))
                             .anchor();
        checkpoint_or_throw(membership_database);
        checkpoint_or_throw(anchor_database);
    }

    {
        SyncSqliteDb rollback_database = open_database(rollback_membership_path);
        SyncSqliteDb anchor_database = open_database(primary_anchor_path);
        SyncReplicaTlsMembershipSqliteOwner rollback_owner(
            rollback_database.db, folder, local,
            "TLS rolled-back history owner");
        SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
            anchor_database.db, folder, local,
            "TLS rollback retained anchor owner");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipAnchoredOwner coordinator(
                    rollback_owner, anchor_owner,
                    "TLS rollback rejecting coordinator");
            },
            "rolled back below trusted generation",
            "anchored membership accepted whole-file rollback below retained anchor");
    }

    {
        SyncSqliteDb fork_membership_database = open_database(fork_membership_path);
        SyncSqliteDb fork_anchor_database = open_database(fork_anchor_path);
        SyncReplicaTlsMembershipSqliteOwner fork_membership_owner(
            fork_membership_database.db, folder, local,
            "TLS fork history owner");
        SyncReplicaTlsMembershipAnchorSqliteOwner fork_anchor_owner(
            fork_anchor_database.db, folder, local,
            "TLS fork anchor owner");
        SyncReplicaTlsMembershipAnchoredOwner fork_coordinator(
            fork_membership_owner, fork_anchor_owner,
            "TLS fork coordinator");
        const auto genesis = fork_membership_owner.snapshot_or_throw().anchor();
        const auto fork_generation_one = fork_coordinator.publish_or_throw(
            genesis, 111U, entries_for("divergent fork", 10400U))
                                             .anchor();
        checks.require(
            fork_generation_one.state_generation ==
                    generation_one.state_generation &&
                fork_generation_one != generation_one,
            "fork fixture did not create a divergent same-generation chain");
        checkpoint_or_throw(fork_membership_database);
        checkpoint_or_throw(fork_anchor_database);
    }

    {
        SyncSqliteDb primary_membership_database =
            open_database(primary_membership_path);
        SyncSqliteDb fork_anchor_database = open_database(fork_anchor_path);
        SyncReplicaTlsMembershipSqliteOwner primary_membership_owner(
            primary_membership_database.db, folder, local,
            "TLS primary history paired with fork anchor");
        SyncReplicaTlsMembershipAnchorSqliteOwner fork_anchor_owner(
            fork_anchor_database.db, folder, local,
            "TLS divergent retained anchor owner");
        checks.require_error(
            [&] {
                SyncReplicaTlsMembershipAnchoredOwner coordinator(
                    primary_membership_owner, fork_anchor_owner,
                    "TLS fork rejecting coordinator");
            },
            "diverges from trusted anchor",
            "anchored membership accepted a divergent retained checkpoint");
        checks.require(
            primary_membership_owner.snapshot_or_throw().anchor() ==
                generation_two,
            "fork rejection mutated valid primary membership authority");
    }
}

}  // namespace

std::size_t run_sync_replica_tls_membership_anchor_sqlite_owner_tests() {
    Checks checks;
    test_anchor_owner_cas_restart_and_tamper(checks);
    test_detached_bootstrap_image_profile(checks);
    test_policy_connection_binding_and_path_alias(checks);
    test_coordinator_rejects_same_database_file(checks);
    test_coordinator_commit_gap_recovery_and_race(checks);
    test_coordinator_rollback_and_fork_rejection(checks);
    return checks.count();
}

}  // namespace anonsync::test
