#include "sha256_digest.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

#if !defined(_WIN32)
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;

class TestState final {
public:
    void require(bool condition, const std::string& message) {
        if (condition) {
            ++passed;
            return;
        }
        ++failed;
        std::cerr << "FAIL: " << message << "\n";
    }

    template <typename Callable>
    void require_throws(
        Callable&& callable,
        std::string_view expected_fragment,
        const std::string& message) {
        try {
            std::forward<Callable>(callable)();
        } catch (const std::exception& error) {
            const std::string_view observed(error.what());
            require(
                observed.find(expected_fragment) != std::string_view::npos,
                message + " (unexpected error: " + error.what() + ")");
            return;
        }
        require(false, message + " (did not reject)");
    }

    std::size_t passed = 0;
    std::size_t failed = 0;
};

class TemporaryDatabase final {
public:
    explicit TemporaryDatabase(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#if !defined(_WIN32)
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        path_ = fs::temp_directory_path() /
                (std::string(stem) + "-" + std::to_string(process) + "-" +
                 std::to_string(tick) + ".sqlite3");
    }

    ~TemporaryDatabase() {
        std::error_code ignored;
        fs::remove(path_, ignored);
        fs::remove(path_.string() + "-wal", ignored);
        fs::remove(path_.string() + "-shm", ignored);
        fs::remove(path_.string() + "-journal", ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

[[nodiscard]] anonsync::SyncSqliteDb open_database(const fs::path& path) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "prepared publication test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "prepared publication test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "prepared publication test durability profile");
    return owner;
}

struct TargetedLocalPublicationTrace final {
    std::uint64_t targeted_path_history_rows = 0U;
    std::uint64_t causal_head_rows = 0U;
    std::uint64_t complete_operation_projection_rows = 0U;
    std::uint64_t complete_visible_projection_rows = 0U;
    std::uint64_t complete_operation_projection_statements = 0U;
};

int trace_targeted_local_publication(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (context == nullptr || statement_pointer == nullptr ||
        (trace_kind != SQLITE_TRACE_STMT && trace_kind != SQLITE_TRACE_ROW)) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr) return 0;
    auto& trace = *static_cast<TargetedLocalPublicationTrace*>(context);
    const std::string_view text(sql);
    const bool complete_operations =
        text.find("FROM main.sync_replica_operations ORDER BY operation_id") !=
        std::string_view::npos;
    if (trace_kind == SQLITE_TRACE_STMT) {
        if (complete_operations) {
            ++trace.complete_operation_projection_statements;
        }
        return 0;
    }
    if (text.find("FROM main.sync_replica_operation_paths AS p") !=
            std::string_view::npos &&
        text.find("WHERE p.canonical_path=?") != std::string_view::npos) {
        ++trace.targeted_path_history_rows;
    }
    if (text.find("FROM main.sync_replica_heads AS h") !=
        std::string_view::npos) {
        ++trace.causal_head_rows;
    }
    if (complete_operations) {
        ++trace.complete_operation_projection_rows;
    }
    if (text.find("FROM main.sync_replica_visible ") !=
            std::string_view::npos &&
        text.find("ORDER BY canonical_path,visible_ordinal") !=
            std::string_view::npos) {
        ++trace.complete_visible_projection_rows;
    }
    return 0;
}

[[nodiscard]] std::vector<std::string> visible_heads(
    const anonsync::SyncReplicaSqliteSnapshot& snapshot,
    const std::string& canonical_path) {
    anonsync::SyncReplicaModel model =
        anonsync::SyncReplicaModel::restore_or_throw(
            snapshot.durable, snapshot.limits.model);
    const auto view = model.visible_path(canonical_path);
    return view.has_value() ? view->visible_operation_ids
                            : std::vector<std::string>{};
}

void test_prepare_commit_restart_and_stale(TestState& test) {
    TemporaryDatabase database("anonsync-prepared-publication");
    const std::string folder_id = "prepared-folder";
    const anonsync::SyncReplicaActor local_actor{"local-device", 7U};
    anonsync::SyncReplicaSqlitePreparedLocalFilePublication prepared_v2;
    anonsync::SyncReplicaSqliteSnapshot committed_v2;

    {
        auto db = open_database(database.path());
        anonsync::SyncReplicaSqliteOwner owner(
            db.db, folder_id, local_actor, {}, "prepared publication owner");
        const auto empty = owner.snapshot_or_throw();
        const auto prepared_v1 =
            owner.prepare_local_file_from_observed_heads_or_throw(
                "notes.txt", {}, 5U, anonsync::sha256_hex("alpha"));
        test.require(
            owner.snapshot_or_throw() == empty,
            "preparation is a complete durable no-op");
        test.require(
            prepared_v1.observed_state_generation == empty.state_generation &&
                prepared_v1.expected_publication_cutpoint_digest.size() == 64U &&
                prepared_v1.observed_visible_operation_ids.empty(),
            "preparation binds the exact pinned empty cutpoint");
        test.require(
            prepared_v1.operation.canonical_path == "notes.txt" &&
                prepared_v1.operation.content_sha256 ==
                    anonsync::sha256_hex("alpha") &&
                prepared_v1.operation.dot.actor == local_actor &&
                prepared_v1.operation.dot.counter == 1U,
            "preparation derives the exact next local canonical operation");

        const auto published =
            owner.commit_prepared_local_file_or_throw(prepared_v1);
        const auto after_v1 = owner.snapshot_or_throw();
        test.require(
            published.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        Published &&
                published.state_generation == after_v1.state_generation &&
                published.cutpoint_digest == after_v1.cutpoint_digest,
            "the first exact commit publishes one transaction-bound cutpoint");
        test.require(
            after_v1.durable.local_operation_ids ==
                std::vector<std::string>{prepared_v1.operation.operation_id} &&
                after_v1.outbox.empty(),
            "prepared publication retains share evidence without courier intents");

        const auto before_repeat = owner.snapshot_or_throw();
        const auto repeated =
            owner.commit_prepared_local_file_or_throw(prepared_v1);
        test.require(
            repeated.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        AlreadyPublished &&
                owner.snapshot_or_throw() == before_repeat,
            "an exact repeated commit is a generation-stable durable no-op");

        const std::vector<std::string> heads_v1 =
            visible_heads(after_v1, "notes.txt");
        prepared_v2 = owner.prepare_local_file_from_observed_heads_or_throw(
            "notes.txt", heads_v1, 4U, anonsync::sha256_hex("beta"));
        test.require(
            prepared_v2.observed_visible_operation_ids == heads_v1 &&
                prepared_v2.operation.dot.counter == 2U,
            "preparation carries the exact nonempty path-head observation");
        const auto before_outbox = owner.snapshot_or_throw();
        const std::vector<std::string> destination{"peer-device"};
        const auto enqueued = owner.enqueue_operation_for_destinations_or_throw(
            prepared_v1.operation.operation_id, destination);
        const auto after_outbox = owner.snapshot_or_throw();
        test.require(
            enqueued.added_intent_count == 1U &&
                after_outbox.state_generation > before_outbox.state_generation &&
                after_outbox.durable == before_outbox.durable,
            "destination scheduling advances liveness without changing evidence");

        anonsync::SyncReplicaModel unrelated_remote(
            folder_id, {"remote-unrelated", 21U});
        const auto unrelated_remote_operation =
            unrelated_remote.create_local_file_or_throw(
                "remote-only.txt", 6U, anonsync::sha256_hex("remote"));
        test.require(
            owner.accept_remote_or_throw(unrelated_remote_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "the unrelated-remote fixture did not advance retained evidence");
        const auto v2_result =
            owner.commit_prepared_local_file_or_throw(prepared_v2);
        committed_v2 = owner.snapshot_or_throw();
        test.require(
            v2_result.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        Published &&
                visible_heads(committed_v2, "notes.txt") ==
                    std::vector<std::string>{
                        prepared_v2.operation.operation_id},
            "a prepared successor survives unrelated outbox and remote-path activity while replacing the exact observed path head");

        const auto target_stale =
            owner.prepare_local_file_from_observed_heads_or_throw(
                "target-race.txt", {}, 5U, anonsync::sha256_hex("local"));
        anonsync::SyncReplicaModel target_remote(
            folder_id, {"remote-target", 22U});
        const auto target_remote_operation =
            target_remote.create_local_file_or_throw(
                "target-race.txt", 6U, anonsync::sha256_hex("remote"));
        test.require(
            owner.accept_remote_or_throw(target_remote_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "the target-path fixture did not advance the visible frontier");
        const auto before_target_stale = owner.snapshot_or_throw();
        const auto target_stale_result =
            owner.commit_prepared_local_file_or_throw(target_stale);
        test.require(
            target_stale_result.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        StaleCutpoint &&
                owner.snapshot_or_throw() == before_target_stale,
            "a target-path frontier change was not reported as a durable no-op stale preparation");

        const auto stale =
            owner.prepare_local_file_from_observed_heads_or_throw(
                "later.txt", {}, 5U, anonsync::sha256_hex("later"));
        (void)owner.publish_local_file_or_throw(
            "unrelated.txt", 7U, anonsync::sha256_hex("advance"));
        const auto before_stale_commit = owner.snapshot_or_throw();
        const auto stale_result =
            owner.commit_prepared_local_file_or_throw(stale);
        test.require(
            stale_result.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        StaleCutpoint &&
                stale_result.state_generation ==
                    before_stale_commit.state_generation &&
                stale_result.cutpoint_digest ==
                    before_stale_commit.cutpoint_digest &&
                owner.snapshot_or_throw() == before_stale_commit,
            "an intervening local mint changes operation identity and makes a preparation stale without writing");
    }

    {
        auto db = open_database(database.path());
        anonsync::SyncReplicaSqliteOwner restarted(
            db.db, folder_id, local_actor, {},
            "restarted prepared publication owner");
        const auto before = restarted.snapshot_or_throw();
        const auto recovered =
            restarted.commit_prepared_local_file_or_throw(prepared_v2);
        test.require(
            recovered.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        AlreadyPublished &&
                restarted.snapshot_or_throw() == before,
            "a catalog can repeat an exact prepared commit after process restart");
        test.require(
            before.durable.local_operation_ids.size() == 3U &&
                before.durable.local_operation_ids[1] ==
                    prepared_v2.operation.operation_id,
            "restart preserves the exact local counter-to-operation binding");
        test.require(
            before.state_generation > committed_v2.state_generation,
            "the restart fixture retained the unrelated cutpoint advance");
    }
}

void test_tamper_and_conflict_rejection(TestState& test) {
    TemporaryDatabase database("anonsync-prepared-rejection");
    auto db = open_database(database.path());
    const std::string folder_id = "prepared-rejection-folder";
    const anonsync::SyncReplicaActor local_actor{"local-device", 11U};
    anonsync::SyncReplicaSqliteOwner owner(
        db.db, folder_id, local_actor, {}, "prepared rejection owner");

    const auto prepared = owner.prepare_local_file_from_observed_heads_or_throw(
        "safe.txt", {}, 4U, anonsync::sha256_hex("safe"));
    auto tampered = prepared;
    tampered.operation.size_bytes += 1U;
    const auto before_tamper = owner.snapshot_or_throw();
    test.require_throws(
        [&] { (void)owner.commit_prepared_local_file_or_throw(tampered); },
        "operation",
        "a caller cannot alter prepared canonical bytes while retaining the ID");
    test.require(
        owner.snapshot_or_throw() == before_tamper,
        "tampered prepared evidence leaves the durable cutpoint unchanged");

    auto canonically_changed = prepared;
    canonically_changed.operation.size_bytes = 5U;
    canonically_changed.operation.content_sha256 =
        anonsync::sha256_hex("other");
    canonically_changed.operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(
            canonically_changed.operation);
    const auto before_canonical_change = owner.snapshot_or_throw();
    const auto canonical_change_result =
        owner.commit_prepared_local_file_or_throw(canonically_changed);
    test.require(
        canonical_change_result.disposition ==
                anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                    StaleCutpoint &&
            owner.snapshot_or_throw() == before_canonical_change,
        "the prepared cutpoint seal did not bind exact canonical operation bytes");

    auto changed_heads = prepared;
    changed_heads.observed_visible_operation_ids = {std::string(64U, 'a')};
    const auto before_changed_heads = owner.snapshot_or_throw();
    const auto changed_heads_result =
        owner.commit_prepared_local_file_or_throw(changed_heads);
    test.require(
        changed_heads_result.disposition ==
                anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                    StaleCutpoint &&
            owner.snapshot_or_throw() == before_changed_heads,
        "the prepared cutpoint seal did not bind the supplied path-head set");

    auto stale_tampered =
        owner.prepare_local_file_from_observed_heads_or_throw(
            "stale-tamper.txt", {}, 5U, anonsync::sha256_hex("stale"));
    (void)owner.publish_local_file_or_throw(
        "advance-before-tamper.txt", 7U, anonsync::sha256_hex("advance"));
    stale_tampered.operation.size_bytes += 1U;
    const auto before_stale_tamper = owner.snapshot_or_throw();
    test.require_throws(
        [&] {
            (void)owner.commit_prepared_local_file_or_throw(stale_tampered);
        },
        "operation",
        "malformed prepared evidence is rejected even after its cutpoint becomes stale");
    test.require(
        owner.snapshot_or_throw() == before_stale_tamper,
        "stale malformed prepared evidence leaves the durable cutpoint unchanged");

    auto invalid_heads = prepared;
    invalid_heads.observed_visible_operation_ids = {
        std::string(64U, 'a'), std::string(64U, 'a')};
    test.require_throws(
        [&] {
            (void)owner.commit_prepared_local_file_or_throw(invalid_heads);
        },
        "strictly sorted and unique",
        "prepared path-head sets reject duplicate identities before mutation");

    anonsync::SyncReplicaModel remote_a(
        folder_id, {"remote-a", 1U});
    anonsync::SyncReplicaModel remote_b(
        folder_id, {"remote-b", 1U});
    const auto a = remote_a.create_local_file_or_throw(
        "conflict.txt", 1U, anonsync::sha256_hex("a"));
    const auto b = remote_b.create_local_file_or_throw(
        "conflict.txt", 1U, anonsync::sha256_hex("b"));
    (void)owner.accept_remote_or_throw(a);
    (void)owner.accept_remote_or_throw(b);
    const auto conflicted = owner.snapshot_or_throw();
    const std::vector<std::string> conflict_heads =
        visible_heads(conflicted, "conflict.txt");
    test.require(
        conflict_heads.size() == 2U,
        "the rejection fixture has two concurrent visible file heads");
    test.require_throws(
        [&] {
            (void)owner.prepare_local_file_from_observed_heads_or_throw(
                "conflict.txt", conflict_heads, 1U,
                anonsync::sha256_hex("winner"));
        },
        "explicit resolution",
        "ordinary prepared publication cannot collapse a visible conflict");
    test.require(
        owner.snapshot_or_throw() == conflicted,
        "rejected conflict preparation is a complete durable no-op");
}

void test_path_local_scale_and_statement_shape(TestState& test) {
    TemporaryDatabase database("anonsync-prepared-path-local-scale");
    auto db = open_database(database.path());
    const std::string folder_id = "prepared-path-local-scale-folder";
    const anonsync::SyncReplicaActor local_actor{"local-scale", 31U};
    anonsync::SyncReplicaSqliteOwnerLimits owner_limits;
    owner_limits.model.max_operations = 512U;
    owner_limits.model.max_context_entries = 64U;
    owner_limits.model.max_predecessor_ids = 64U;
    owner_limits.model.max_retained_canonical_bytes = 64U * 1024U * 1024U;
    owner_limits.model.max_retained_context_entries = 4096U;
    owner_limits.model.max_retained_predecessor_ids = 4096U;
    anonsync::SyncReplicaSqliteOwner owner(
        db.db, folder_id, local_actor, owner_limits,
        "prepared path-local scale owner");

    // A long unrelated causal chain leaves one bounded active head while
    // retaining far more operation history than the target path. The prepared
    // path must not decode that history merely to mint or commit one local file.
    anonsync::SyncReplicaModel remote(
        folder_id, {"remote-scale", 41U}, owner_limits.model);
    constexpr std::size_t kUnrelatedHistory = 192U;
    for (std::size_t index = 0U; index < kUnrelatedHistory; ++index) {
        const auto operation = remote.create_local_file_or_throw(
            "unrelated/archive.bin", static_cast<std::uint64_t>(index + 1U),
            anonsync::sha256_hex("remote-scale-" + std::to_string(index)));
        test.require(
            owner.accept_remote_or_throw(operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "the scale fixture could not retain its unrelated causal chain");
    }

    const auto baseline = owner.snapshot_or_throw();
    anonsync::SyncReplicaModel reference =
        anonsync::SyncReplicaModel::restore_or_throw(
            baseline.durable, baseline.limits.model);
    const auto expected = reference.create_local_file_from_observed_heads_or_throw(
        "selected/movie.mkv", {}, 17U, anonsync::sha256_hex("selected"));

    TargetedLocalPublicationTrace prepare_trace;
    test.require(
        sqlite3_trace_v2(
            db.db.get(), SQLITE_TRACE_STMT | SQLITE_TRACE_ROW,
            trace_targeted_local_publication, &prepare_trace) == SQLITE_OK,
        "the scale fixture could not install its prepare trace");
    const auto prepared = owner.prepare_local_file_from_observed_heads_or_throw(
        "selected/movie.mkv", {}, 17U, anonsync::sha256_hex("selected"));
    test.require(
        sqlite3_trace_v2(db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "the scale fixture could not remove its prepare trace");
    test.require(
        prepared.operation == expected,
        "path-local preparation diverged from the complete public causal-model definition");
    test.require(
        prepare_trace.targeted_path_history_rows == 0U &&
            prepare_trace.causal_head_rows == 1U &&
            prepare_trace.complete_operation_projection_rows == 0U &&
            prepare_trace.complete_visible_projection_rows == 0U &&
            prepare_trace.complete_operation_projection_statements == 0U,
        "path-local preparation decoded unrelated retained history or a complete projection");

    TargetedLocalPublicationTrace commit_trace;
    test.require(
        sqlite3_trace_v2(
            db.db.get(), SQLITE_TRACE_STMT | SQLITE_TRACE_ROW,
            trace_targeted_local_publication, &commit_trace) == SQLITE_OK,
        "the scale fixture could not install its commit trace");
    const auto committed = owner.commit_prepared_local_file_or_throw(prepared);
    test.require(
        sqlite3_trace_v2(db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "the scale fixture could not remove its commit trace");
    test.require(
        committed.disposition ==
            anonsync::SyncReplicaSqlitePreparedPublicationDisposition::Published,
        "the path-local scale commit did not publish its exact operation");
    test.require(
        commit_trace.targeted_path_history_rows == 1U &&
            commit_trace.causal_head_rows == 0U &&
            commit_trace.complete_operation_projection_rows == 0U &&
            commit_trace.complete_visible_projection_rows == 0U &&
            commit_trace.complete_operation_projection_statements == 0U,
        "path-local commit decoded unrelated retained history or a complete projection");
    const auto after = owner.snapshot_or_throw();
    test.require(
        after.durable.operations.size() == kUnrelatedHistory + 1U &&
            visible_heads(after, "selected/movie.mkv") ==
                std::vector<std::string>{prepared.operation.operation_id},
        "path-local commit did not preserve unrelated history and publish one target value");
}

void test_nonvisible_same_path_drift_and_dependency_fallback(TestState& test) {
    {
        TemporaryDatabase database("anonsync-prepared-pending-path-drift");
        auto db = open_database(database.path());
        const std::string folder_id = "prepared-pending-path-drift-folder";
        const anonsync::SyncReplicaActor local_actor{"local-pending", 51U};
        anonsync::SyncReplicaSqliteOwner owner(
            db.db, folder_id, local_actor, {},
            "prepared pending-path drift owner");
        const auto prepared = owner.prepare_local_file_from_observed_heads_or_throw(
            "same/path.bin", {}, 5U, anonsync::sha256_hex("local"));

        anonsync::SyncReplicaOperation pending;
        pending.folder_id = folder_id;
        pending.canonical_path = "same/path.bin";
        pending.kind = anonsync::SyncReplicaValueKind::File;
        pending.size_bytes = 7U;
        pending.content_sha256 = anonsync::sha256_hex("pending");
        pending.dot = {{"remote-pending", 52U}, 1U};
        pending.predecessor_operation_ids = {anonsync::sha256_hex("missing")};
        pending.operation_id =
            anonsync::make_sync_replica_operation_id_or_throw(pending);
        test.require(
            owner.accept_remote_or_throw(pending) ==
                anonsync::SyncReplicaAdmission::InsertedPending,
            "the same-path drift fixture did not retain nonvisible evidence");
        const auto before = owner.snapshot_or_throw();
        const auto result = owner.commit_prepared_local_file_or_throw(prepared);
        test.require(
            result.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        StaleCutpoint &&
                owner.snapshot_or_throw() == before,
            "nonvisible same-path history drift did not reject before effects");
    }

    {
        TemporaryDatabase database("anonsync-prepared-dependency-fallback");
        auto db = open_database(database.path());
        const std::string folder_id = "prepared-dependency-fallback-folder";
        const anonsync::SyncReplicaActor local_actor{"local-fallback", 61U};
        anonsync::SyncReplicaSqliteOwner owner(
            db.db, folder_id, local_actor, {},
            "prepared dependency fallback owner");
        const auto prepared = owner.prepare_local_file_from_observed_heads_or_throw(
            "target/file.bin", {}, 6U, anonsync::sha256_hex("target"));

        anonsync::SyncReplicaOperation child;
        child.folder_id = folder_id;
        child.canonical_path = "unrelated/dependent.bin";
        child.kind = anonsync::SyncReplicaValueKind::File;
        child.size_bytes = 9U;
        child.content_sha256 = anonsync::sha256_hex("dependent");
        child.dot = {{"remote-fallback", 62U}, 1U};
        child.causal_context = {{local_actor, prepared.operation.dot.counter}};
        child.predecessor_operation_ids = {prepared.operation.operation_id};
        child.operation_id =
            anonsync::make_sync_replica_operation_id_or_throw(child);
        test.require(
            owner.accept_remote_or_throw(child) ==
                anonsync::SyncReplicaAdmission::InsertedPending,
            "the reverse-dependency fixture did not retain its pending child");

        const auto result = owner.commit_prepared_local_file_or_throw(prepared);
        const auto after = owner.snapshot_or_throw();
        const auto model = anonsync::SyncReplicaModel::restore_or_throw(
            after.durable, after.limits.model);
        test.require(
            result.disposition ==
                    anonsync::SyncReplicaSqlitePreparedPublicationDisposition::
                        Published &&
                model.evidence_state(prepared.operation.operation_id) ==
                    anonsync::SyncReplicaEvidenceState::Active &&
                model.evidence_state(child.operation_id) ==
                    anonsync::SyncReplicaEvidenceState::Active,
            "the indexed reverse-dependency fallback did not preserve complete-model activation semantics");
    }
}

void test_quarantined_local_retry_fails_closed(TestState& test) {
    TemporaryDatabase database("anonsync-prepared-compromised-retry");
    auto db = open_database(database.path());
    const std::string folder_id = "prepared-compromised-retry-folder";
    const anonsync::SyncReplicaActor local_actor{
        "local-compromised-retry", 66U};
    anonsync::SyncReplicaSqliteOwner owner(
        db.db, folder_id, local_actor, {},
        "prepared compromised retry owner");

    const auto prepared = owner.prepare_local_file_from_observed_heads_or_throw(
        "important/file.bin", {}, 8U, anonsync::sha256_hex("trusted"));
    const auto published = owner.commit_prepared_local_file_or_throw(prepared);
    test.require(
        published.disposition ==
            anonsync::SyncReplicaSqlitePreparedPublicationDisposition::Published,
        "the compromised-retry fixture did not publish its local operation");

    anonsync::SyncReplicaOperation fork = prepared.operation;
    fork.size_bytes = 9U;
    fork.content_sha256 = anonsync::sha256_hex("same-dot-fork");
    fork.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(fork);
    test.require(
        owner.accept_remote_or_throw(fork) ==
            anonsync::SyncReplicaAdmission::InsertedQuarantined,
        "the compromised-retry fixture did not retain its same-dot fork");

    const auto compromised = owner.snapshot_or_throw();
    const auto compromised_model =
        anonsync::SyncReplicaModel::restore_or_throw(
            compromised.durable, compromised.limits.model);
    test.require(
        compromised_model.local_actor_compromised() &&
            compromised_model.evidence_state(
                prepared.operation.operation_id) ==
                anonsync::SyncReplicaEvidenceState::QuarantinedDotFork &&
            compromised_model.evidence_state(fork.operation_id) ==
                anonsync::SyncReplicaEvidenceState::QuarantinedDotFork,
        "the same-dot fork did not revoke active local minting authority");

    test.require_throws(
        [&] { (void)owner.commit_prepared_local_file_or_throw(prepared); },
        "no longer carries active local minting authority",
        "an exact retry falsely reported already-published after quarantine");
    test.require(
        owner.snapshot_or_throw() == compromised,
        "the rejected compromised retry changed durable replica authority");
}

void test_temporary_trigger_fence_precedes_effects(TestState& test) {
    TemporaryDatabase database("anonsync-prepared-temp-trigger-fence");
    auto db = open_database(database.path());
    const std::string folder_id = "prepared-temp-trigger-folder";
    const anonsync::SyncReplicaActor local_actor{"local-temp-trigger", 71U};
    anonsync::SyncReplicaSqliteOwner owner(
        db.db, folder_id, local_actor, {},
        "prepared TEMP-trigger owner");
    const auto prepared = owner.prepare_local_file_from_observed_heads_or_throw(
        "safe/file.bin", {}, 4U, anonsync::sha256_hex("safe"));
    const auto baseline = owner.snapshot_or_throw();

    anonsync::sqlite_exec_or_throw(
        db.db,
        "CREATE TEMP TRIGGER anonsync_test_targeted_publication_trigger "
        "BEFORE INSERT ON main.sync_replica_operations BEGIN "
        "SELECT RAISE(ABORT,'targeted trigger executed'); END;",
        "prepared TEMP-trigger fixture create");
    test.require_throws(
        [&] { (void)owner.commit_prepared_local_file_or_throw(prepared); },
        "TEMP triggers exist",
        "targeted publication did not reject executable TEMP schema before effects");
    anonsync::sqlite_exec_or_throw(
        db.db,
        "DROP TRIGGER temp.anonsync_test_targeted_publication_trigger;",
        "prepared TEMP-trigger fixture drop");
    test.require(
        owner.snapshot_or_throw() == baseline,
        "rejected TEMP-trigger publication changed durable replica authority");
}

}  // namespace

int main() {
    try {
        TestState test;
        test_prepare_commit_restart_and_stale(test);
        test_tamper_and_conflict_rejection(test);
        test_path_local_scale_and_statement_shape(test);
        test_nonvisible_same_path_drift_and_dependency_fallback(test);
        test_quarantined_local_retry_fails_closed(test);
        test_temporary_trigger_fence_precedes_effects(test);
        std::cout << "sync replica prepared publication checks: "
                  << test.passed << "/" << (test.passed + test.failed)
                  << "\n";
        return test.failed == 0U ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
}
