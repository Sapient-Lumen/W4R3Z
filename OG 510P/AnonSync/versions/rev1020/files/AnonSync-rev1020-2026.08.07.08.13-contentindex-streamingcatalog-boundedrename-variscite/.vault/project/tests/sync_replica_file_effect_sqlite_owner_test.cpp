#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_file_effect_sqlite_owner.hpp"
#include "sync_replica_model.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

#if !defined(_WIN32)
#include <sys/statvfs.h>
#include <unistd.h>
#endif

namespace {

std::size_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(Callable&& callable,
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

struct TempWorkspace final {
    std::filesystem::path root;
    std::filesystem::path database;

    explicit TempWorkspace(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __linux__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        root = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick));
        std::filesystem::create_directories(root / "files" / "nested");
        database = root / "effects.sqlite3";
    }

    ~TempWorkspace() {
        std::error_code ignored;
        std::filesystem::remove_all(root, ignored);
    }
};

anonsync::SyncSqliteDb open_database(const std::filesystem::path& path) {
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
            owner.db, "file-effect owner test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "file-effect owner test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "file-effect owner test durability profile");
    return owner;
}

anonsync::SyncReplicaFileEffectSqliteOwnerLimits effect_limits(
    std::uint64_t max_effects = 16U,
    std::uint64_t retained_payload = 1024U * 1024U) {
    anonsync::SyncReplicaFileEffectSqliteOwnerLimits limits;
    limits.model.max_operations = 64U;
    limits.model.max_context_entries = 64U;
    limits.model.max_predecessor_ids = 64U;
    limits.model.max_canonical_operation_bytes = 256U * 1024U;
    limits.model.max_retained_canonical_bytes = 4U * 1024U * 1024U;
    limits.model.max_retained_context_entries = 4096U;
    limits.model.max_retained_predecessor_ids = 4096U;
    limits.max_effects = max_effects;
    limits.max_payload_bytes = 256U * 1024U;
    limits.max_retained_payload_bytes = retained_payload;
    limits.max_effects_per_device = max_effects;
    limits.max_retained_payload_bytes_per_device = retained_payload;
    return limits;
}

constexpr std::string_view kLegacyEffectMetaSchemaSql =
    "CREATE TABLE main.sync_replica_file_effect_meta("
    "id INTEGER PRIMARY KEY CHECK(id=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=2),"
    "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
    "root_path TEXT NOT NULL CHECK(length(root_path) BETWEEN 1 AND 32768),"
    "root_authority_digest TEXT NOT NULL CHECK(length(root_authority_digest)=64),"
    "max_operations INTEGER NOT NULL CHECK(max_operations>0),"
    "max_context_entries INTEGER NOT NULL CHECK(max_context_entries>0),"
    "max_predecessor_ids INTEGER NOT NULL CHECK(max_predecessor_ids>0),"
    "max_canonical_operation_bytes INTEGER NOT NULL CHECK(max_canonical_operation_bytes>0),"
    "max_retained_canonical_bytes INTEGER NOT NULL CHECK(max_retained_canonical_bytes>0),"
    "max_retained_context_entries INTEGER NOT NULL CHECK(max_retained_context_entries>0),"
    "max_retained_predecessor_ids INTEGER NOT NULL CHECK(max_retained_predecessor_ids>0),"
    "max_effects INTEGER NOT NULL CHECK(max_effects>0),"
    "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
    "max_retained_payload_bytes INTEGER NOT NULL CHECK(max_retained_payload_bytes>0),"
    "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
    "effect_count INTEGER NOT NULL CHECK(effect_count>=0),"
    "published_count INTEGER NOT NULL CHECK(published_count>=0),"
    "retained_payload_bytes INTEGER NOT NULL CHECK(retained_payload_bytes>=0),"
    "effect_set_digest TEXT NOT NULL CHECK(length(effect_set_digest)=64),"
    "cutpoint_digest TEXT NOT NULL CHECK(length(cutpoint_digest)=64)) STRICT;";

std::array<char, 8U> big_endian_u64(std::uint64_t value) {
    std::array<char, 8U> result{};
    for (std::size_t index = result.size(); index != 0U; --index) {
        result[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return result;
}

void digest_u64(anonsync::Sha256DigestBuilder& digest,
                std::uint64_t value) {
    const auto encoded = big_endian_u64(value);
    digest.update(std::string_view(encoded.data(), encoded.size()));
}

void digest_field(anonsync::Sha256DigestBuilder& digest,
                  std::string_view value) {
    digest_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

std::uint64_t published_effect_count(
    const anonsync::SyncReplicaFileEffectSqliteSnapshot& snapshot) {
    return static_cast<std::uint64_t>(std::count_if(
        snapshot.effects.begin(), snapshot.effects.end(),
        [](const anonsync::SyncReplicaFileEffectRecord& effect) {
            return effect.state ==
                   anonsync::SyncReplicaFileEffectState::Published;
        }));
}

std::string legacy_cutpoint_digest(
    const anonsync::SyncReplicaFileEffectSqliteSnapshot& snapshot) {
    const auto& limits = snapshot.limits;
    anonsync::Sha256DigestBuilder digest;
    digest.update("anonsync-replica-file-effect-cutpoint-v2");
    digest_u64(digest, 2U);
    digest_field(digest, snapshot.folder_id);
    digest_field(digest, snapshot.root_path.generic_string());
    digest_field(digest, snapshot.root_authority_digest);
    digest_u64(digest, limits.model.max_operations);
    digest_u64(digest, limits.model.max_context_entries);
    digest_u64(digest, limits.model.max_predecessor_ids);
    digest_u64(digest, limits.model.max_canonical_operation_bytes);
    digest_u64(digest, limits.model.max_retained_canonical_bytes);
    digest_u64(digest, limits.model.max_retained_context_entries);
    digest_u64(digest, limits.model.max_retained_predecessor_ids);
    digest_u64(digest, limits.max_effects);
    digest_u64(digest, limits.max_payload_bytes);
    digest_u64(digest, limits.max_retained_payload_bytes);
    digest_u64(digest, snapshot.state_generation);
    digest_u64(
        digest, static_cast<std::uint64_t>(snapshot.effects.size()));
    digest_u64(digest, published_effect_count(snapshot));
    digest_u64(digest, snapshot.retained_payload_bytes);
    digest_field(digest, snapshot.effect_set_digest);
    return digest.finish_hex();
}

void downgrade_effect_meta_to_v2_or_throw(
    anonsync::SyncSqliteDbHandleSlot& db,
    const anonsync::SyncReplicaFileEffectSqliteSnapshot& snapshot) {
    const std::string label = "file-effect test v2 downgrade";
    anonsync::SyncSqliteTransaction transaction(
        db, label, anonsync::SyncSqliteTransactionMode::Immediate);
    anonsync::sqlite_exec_or_throw(
        db, "DROP TABLE main.sync_replica_file_effect_meta;",
        label + " drop v3 metadata");
    anonsync::sqlite_exec_or_throw(
        db, std::string(kLegacyEffectMetaSchemaSql),
        label + " create v2 metadata");
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_replica_file_effect_meta("
        "id,schema_version,folder_id,root_path,root_authority_digest,"
        "max_operations,max_context_entries,max_predecessor_ids,"
        "max_canonical_operation_bytes,max_retained_canonical_bytes,"
        "max_retained_context_entries,max_retained_predecessor_ids,"
        "max_effects,max_payload_bytes,max_retained_payload_bytes,"
        "state_generation,effect_count,published_count,"
        "retained_payload_bytes,effect_set_digest,cutpoint_digest)"
        "VALUES(1,2,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
        label + " insert prepare");
    const auto& limits = snapshot.limits;
    const std::string root_path = snapshot.root_path.generic_string();
    anonsync::sqlite_bind_text_or_throw(
        statement.stmt, 1, snapshot.folder_id, label);
    anonsync::sqlite_bind_text_or_throw(
        statement.stmt, 2, root_path, label);
    anonsync::sqlite_bind_text_or_throw(
        statement.stmt, 3, snapshot.root_authority_digest, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 4, limits.model.max_operations, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 5, limits.model.max_context_entries, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 6, limits.model.max_predecessor_ids, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 7,
        limits.model.max_canonical_operation_bytes, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 8,
        limits.model.max_retained_canonical_bytes, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 9,
        limits.model.max_retained_context_entries, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 10,
        limits.model.max_retained_predecessor_ids, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 11, limits.max_effects, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 12, limits.max_payload_bytes, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 13, limits.max_retained_payload_bytes, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 14, snapshot.state_generation, label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 15,
        static_cast<std::uint64_t>(snapshot.effects.size()), label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 16, published_effect_count(snapshot), label);
    anonsync::sqlite_bind_u64_or_throw(
        statement.stmt, 17, snapshot.retained_payload_bytes, label);
    anonsync::sqlite_bind_text_or_throw(
        statement.stmt, 18, snapshot.effect_set_digest, label);
    const std::string cutpoint = legacy_cutpoint_digest(snapshot);
    anonsync::sqlite_bind_text_or_throw(
        statement.stmt, 19, cutpoint, label);
    anonsync::sqlite_step_done_or_throw(
        statement.stmt, label + " insert");
    transaction.commit();
}

std::uint64_t effect_schema_version_or_throw(
    anonsync::SyncSqliteDbHandleSlot& db) {
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        db,
        "SELECT schema_version FROM main.sync_replica_file_effect_meta "
        "WHERE id=1 LIMIT 2;",
        "file-effect test schema version prepare");
    const int first = sqlite3_step(statement.stmt);
    if (first != SQLITE_ROW) {
        fail("file-effect test schema version row is missing");
    }
    const std::uint64_t version = anonsync::sqlite_column_u64_or_throw(
        statement.stmt, 0, "file-effect test schema version");
    if (sqlite3_step(statement.stmt) != SQLITE_DONE) {
        fail("file-effect test schema version returned extra rows");
    }
    return version;
}

void update_meta_text_or_throw(anonsync::SyncSqliteDbHandleSlot& db,
                               std::string_view column,
                               const std::string& value) {
    if (column != "cutpoint_digest" &&
        column != "device_usage_digest") {
        fail("file-effect test rejected an unsafe metadata column");
    }
    const std::string sql =
        "UPDATE main.sync_replica_file_effect_meta SET " +
        std::string(column) + "=? WHERE id=1;";
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        db, sql, "file-effect test metadata update prepare");
    anonsync::sqlite_bind_text_or_throw(
        statement.stmt, 1, value, "file-effect test metadata update");
    anonsync::sqlite_step_done_or_throw(
        statement.stmt, "file-effect test metadata update");
}

int deny_effect_meta_insert_authorizer(void*,
                                       int action,
                                       const char* first,
                                       const char*,
                                       const char*,
                                       const char*) noexcept {
    if (action == SQLITE_INSERT && first != nullptr &&
        std::strcmp(first, "sync_replica_file_effect_meta") == 0) {
        return SQLITE_DENY;
    }
    return SQLITE_OK;
}

std::span<const unsigned char> bytes(const std::string& value) {
    return {reinterpret_cast<const unsigned char*>(value.data()), value.size()};
}

std::string read_binary(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) fail("could not read materialized file");
    return {std::istreambuf_iterator<char>(input),
            std::istreambuf_iterator<char>()};
}

void write_direct(const std::filesystem::path& path,
                  const std::string& payload) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) fail("could not create conflicting file");
    output.write(payload.data(), static_cast<std::streamsize>(payload.size()));
    if (!output) fail("could not write conflicting file");
}

anonsync::SyncReplicaOperation make_file(
    anonsync::SyncReplicaModel& model,
    std::string path,
    const std::string& payload) {
    return model.create_local_file_or_throw(
        std::move(path), static_cast<std::uint64_t>(payload.size()),
        anonsync::sha256_hex(payload));
}

anonsync::SyncReplicaFileEffectActorUsage actor_usage_or_fail(
    const anonsync::SyncReplicaFileEffectSqliteSnapshot& snapshot,
    const anonsync::SyncReplicaActor& actor,
    const std::string& message) {
    const auto found = std::find_if(
        snapshot.actor_usage.begin(), snapshot.actor_usage.end(),
        [&](const anonsync::SyncReplicaFileEffectActorUsage& usage) {
            return usage.actor == actor;
        });
    require(found != snapshot.actor_usage.end(), message);
    return *found;
}

anonsync::SyncReplicaFileEffectDeviceUsage device_usage_or_fail(
    const anonsync::SyncReplicaFileEffectSqliteSnapshot& snapshot,
    std::string_view device_id,
    const std::string& message) {
    const auto found = std::find_if(
        snapshot.device_usage.begin(), snapshot.device_usage.end(),
        [&](const anonsync::SyncReplicaFileEffectDeviceUsage& usage) {
            return usage.device_id == device_id;
        });
    require(found != snapshot.device_usage.end(), message);
    return *found;
}

#if !defined(_WIN32)
std::uint64_t observed_component_byte_limit(
    const std::filesystem::path& directory) {
    struct statvfs filesystem {};
    if (::statvfs(directory.c_str(), &filesystem) != 0) {
        fail("could not observe filesystem filename limit");
    }
    std::uint64_t limit = static_cast<std::uint64_t>(filesystem.f_namemax);
    errno = 0;
    const long path_limit = ::pathconf(directory.c_str(), _PC_NAME_MAX);
    if (path_limit < 0 && errno != 0) {
        fail("could not observe path filename limit");
    }
    if (path_limit > 0) {
        const auto converted = static_cast<std::uint64_t>(path_limit);
        limit = limit == 0U ? converted : std::min(limit, converted);
    }
    if (limit == 0U) fail("filesystem reported no usable filename limit");
    return limit;
}
#endif

void test_stage_materialize_restart_and_ambiguous_recovery() {
    TempWorkspace workspace("anonsync-file-effect-owner");
    const std::string folder = "folder-file-effect-owner";
    const auto limits = effect_limits();
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-source", 9101U}, limits.model);
    const std::string payload{"first\0payload\xff", 15U};
    const auto operation = make_file(model, "nested/first.bin", payload);

    anonsync::SyncSqliteDb database = open_database(workspace.database);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, workspace.root / "files", limits,
            "file-effect primary owner");
        const auto empty = owner.snapshot_or_throw();
        require(empty.effects.empty() && empty.state_generation == 0U,
                "new effect owner must begin at an attested empty cutpoint");
        require(empty.root_authority_digest.size() == 64U,
                "the durable cutpoint must bind one exact root authority digest");
        require(
            owner.stage_or_throw(operation, bytes(payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted,
            "first exact payload must be durably staged");
        const auto staged = owner.snapshot_or_throw();
        require(staged.effects.size() == 1U &&
                    staged.effects.front().state ==
                        anonsync::SyncReplicaFileEffectState::Staged &&
                    staged.state_generation == 1U &&
                    staged.retained_payload_bytes == payload.size(),
                "staging must advance one generation without claiming publication");
        require(!std::filesystem::exists(
                    workspace.root / "files" / "nested" / "first.bin"),
                "staging alone must not create a visible file");
        require(
            owner.stage_or_throw(operation, bytes(payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Duplicate,
            "an exact staged duplicate must be idempotent");
        require(owner.snapshot_or_throw().state_generation == 1U,
                "an exact duplicate must not advance durable authority");

        require(
            owner.materialize_or_throw(operation.operation_id) ==
                anonsync::SyncReplicaFileEffectMaterializeResult::Published,
            "staged payload must publish and mark one terminal effect");
        require(read_binary(workspace.root / "files" / "nested" /
                            "first.bin") == payload,
                "materialization must preserve exact payload bytes");
        const auto published = owner.snapshot_or_throw();
        require(published.state_generation == 2U &&
                    published.effects.front().state ==
                        anonsync::SyncReplicaFileEffectState::Published &&
                    !published.effects.front().publication_digest.empty(),
                "published state must have a fresh generation and exact seal");
        require(
            owner.materialize_or_throw(operation.operation_id) ==
                anonsync::SyncReplicaFileEffectMaterializeResult::
                    AlreadyPublished,
            "repeated materialization must reconcile without rewriting");
        require(owner.snapshot_or_throw().state_generation == 2U,
                "already-published reconciliation must be a database no-op");
    }

    // Caller defaults are not restart authority; the exact persisted policy is.
    auto different_defaults = limits;
    different_defaults.max_effects = 32U;
    {
        anonsync::SyncReplicaFileEffectSqliteOwner restarted(
            database.db, folder, workspace.root / "files", different_defaults,
            "file-effect restarted owner");
        const auto snapshot = restarted.snapshot_or_throw();
        require(snapshot.limits == limits && snapshot.state_generation == 2U,
                "restart must restore persisted limits and publication state");

        const std::string second_payload = "staged-across-restart";
        const auto second = make_file(
            model, "nested/second.bin", second_payload);
        require(
            restarted.stage_or_throw(second, bytes(second_payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted,
            "a second payload must stage independently");
    }
    {
        anonsync::SyncReplicaFileEffectSqliteOwner restarted_again(
            database.db, folder, workspace.root / "files", limits,
            "file-effect second restart");
        const auto snapshot = restarted_again.snapshot_or_throw();
        const auto found = std::find_if(
            snapshot.effects.begin(), snapshot.effects.end(),
            [](const anonsync::SyncReplicaFileEffectRecord& record) {
                return record.operation.canonical_path ==
                       "nested/second.bin";
            });
        require(found != snapshot.effects.end(),
                "the staged second effect must survive reconstruction");
        require(
            restarted_again.materialize_or_throw(
                found->operation.operation_id) ==
                anonsync::SyncReplicaFileEffectMaterializeResult::Published,
            "a staged payload must remain publishable after owner reconstruction");
    }

    const std::string ambiguous_payload = "renamed-before-database-mark";
    const auto ambiguous = make_file(
        model, "nested/ambiguous.bin", ambiguous_payload);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, workspace.root / "files", limits,
            "file-effect ambiguous owner");
        require(
            owner.stage_or_throw(ambiguous, bytes(ambiguous_payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted,
            "ambiguous effect must first own durable staged bytes");
    }
    const auto ambiguous_path =
        workspace.root / "files" / "nested" / "ambiguous.bin";
    anonsync::write_sync_file_atomically_create_new_no_symlink_or_throw(
        ambiguous_path, bytes(ambiguous_payload),
        "simulated pre-mark effect publication");
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, workspace.root / "files", limits,
            "file-effect ambiguous recovery");
        require(
            owner.materialize_or_throw(ambiguous.operation_id) ==
                anonsync::SyncReplicaFileEffectMaterializeResult::Published,
            "exact preexisting bytes must recover the post-rename/pre-mark crash window");
        require(read_binary(ambiguous_path) == ambiguous_payload,
                "ambiguous recovery must not replace exact bytes");
    }
}

void test_exact_usage_and_capacity_diagnostics() {
    TempWorkspace usage_workspace("anonsync-file-effect-usage");
    const std::string folder = "folder-file-effect-usage";
    auto limits = effect_limits(16U, 64U);
    limits.max_payload_bytes = 64U;
    const anonsync::SyncReplicaActor first_epoch{
        "device-file-effect-usage-a", 9301U};
    const anonsync::SyncReplicaActor second_epoch{
        "device-file-effect-usage-a", 9302U};
    const anonsync::SyncReplicaActor other_device{
        "device-file-effect-usage-b", 9303U};
    anonsync::SyncReplicaModel first_model(folder, first_epoch, limits.model);
    anonsync::SyncReplicaModel second_model(folder, second_epoch, limits.model);
    anonsync::SyncReplicaModel other_model(folder, other_device, limits.model);
    const std::string first_payload = "aaa";
    const std::string second_payload = "bb";
    const std::string other_payload = "cccc";
    const auto first = make_file(
        first_model, "nested/usage-first", first_payload);
    const auto second = make_file(
        second_model, "nested/usage-second", second_payload);
    const auto other = make_file(
        other_model, "nested/usage-other", other_payload);
    anonsync::SyncSqliteDb usage_db = open_database(usage_workspace.database);
    anonsync::SyncReplicaFileEffectSqliteSnapshot before_restart;
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            usage_db.db, folder, usage_workspace.root / "files", limits,
            "file-effect usage owner");
        require(
            owner.stage_with_diagnostics_or_throw(
                     first, bytes(first_payload)) ==
                anonsync::SyncReplicaFileEffectStageOutcome{
                    anonsync::SyncReplicaFileEffectStageResult::Inserted,
                    std::nullopt},
            "first actor usage effect did not stage without a capacity diagnostic");
        require(
            owner.stage_or_throw(second, bytes(second_payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted &&
                owner.stage_or_throw(other, bytes(other_payload)) ==
                    anonsync::SyncReplicaFileEffectStageResult::Inserted,
            "multi-actor usage effects did not stage");
        require(
            owner.materialize_or_throw(first.operation_id) ==
                anonsync::SyncReplicaFileEffectMaterializeResult::Published,
            "usage fixture did not publish its first actor effect");
        before_restart = owner.snapshot_or_throw();
    }

    require(before_restart.effects.size() == 3U &&
                before_restart.actor_usage.size() == 3U &&
                before_restart.device_usage.size() == 2U &&
                before_restart.retained_payload_bytes == 9U &&
                before_restart.device_usage_digest.size() == 64U,
            "usage snapshot did not expose the exact retained partition");
    const auto first_usage = actor_usage_or_fail(
        before_restart, first_epoch,
        "first actor epoch was absent from exact usage accounting");
    require(first_usage.retained_effects == 1U &&
                first_usage.staged_effects == 0U &&
                first_usage.published_effects == 1U &&
                first_usage.retained_payload_bytes == first_payload.size(),
            "published actor usage did not match its exact retained row");
    const auto second_usage = actor_usage_or_fail(
        before_restart, second_epoch,
        "second actor epoch was absent from exact usage accounting");
    require(second_usage.retained_effects == 1U &&
                second_usage.staged_effects == 1U &&
                second_usage.published_effects == 0U &&
                second_usage.retained_payload_bytes == second_payload.size(),
            "staged actor usage did not match its exact retained row");
    const auto first_device_usage = device_usage_or_fail(
        before_restart, first_epoch.device_id,
        "multi-epoch device was absent from exact usage accounting");
    require(first_device_usage.actor_epochs == 2U &&
                first_device_usage.retained_effects == 2U &&
                first_device_usage.staged_effects == 1U &&
                first_device_usage.published_effects == 1U &&
                first_device_usage.retained_payload_bytes == 5U,
            "device usage did not aggregate exact actor epochs without merging their authority");
    const auto other_usage = device_usage_or_fail(
        before_restart, other_device.device_id,
        "other device was absent from exact usage accounting");
    require(other_usage.actor_epochs == 1U &&
                other_usage.retained_effects == 1U &&
                other_usage.staged_effects == 1U &&
                other_usage.published_effects == 0U &&
                other_usage.retained_payload_bytes == other_payload.size(),
            "other-device usage did not remain independently attributable");

    {
        anonsync::SyncReplicaFileEffectSqliteOwner restarted(
            usage_db.db, folder, usage_workspace.root / "files", limits,
            "file-effect usage restart");
        require(restarted.snapshot_or_throw() == before_restart,
                "restart did not re-derive byte-for-byte identical usage summaries");
    }

    TempWorkspace count_workspace("anonsync-file-effect-count-block");
    auto count_limits = effect_limits(1U, 64U);
    count_limits.max_payload_bytes = 64U;
    const anonsync::SyncReplicaActor count_first_actor{
        "device-file-effect-count", 9311U};
    const anonsync::SyncReplicaActor count_next_actor{
        "device-file-effect-count", 9312U};
    anonsync::SyncReplicaModel count_first_model(
        folder, count_first_actor, count_limits.model);
    anonsync::SyncReplicaModel count_next_model(
        folder, count_next_actor, count_limits.model);
    const std::string count_first_payload = "one";
    const std::string count_next_payload = "two";
    const auto count_first = make_file(
        count_first_model, "nested/count-first", count_first_payload);
    const auto count_next = make_file(
        count_next_model, "nested/count-next", count_next_payload);
    anonsync::SyncSqliteDb count_db = open_database(count_workspace.database);
    anonsync::SyncReplicaFileEffectSqliteOwner count_owner(
        count_db.db, folder, count_workspace.root / "files", count_limits,
        "file-effect count diagnostics");
    require(count_owner.stage_or_throw(
                count_first, bytes(count_first_payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted,
            "count diagnostic fixture did not stage its retained effect");
    const auto count_before = count_owner.snapshot_or_throw();
    const auto duplicate = count_owner.stage_with_diagnostics_or_throw(
        count_first, bytes(count_first_payload));
    require(duplicate.result ==
                    anonsync::SyncReplicaFileEffectStageResult::Duplicate &&
                !duplicate.capacity_block.has_value() &&
                count_owner.snapshot_or_throw() == count_before,
            "an exact duplicate at full capacity was not admitted without mutation");
    const auto count_block = count_owner.stage_with_diagnostics_or_throw(
        count_next, bytes(count_next_payload));
    require(count_block.result ==
                    anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked &&
                count_block.capacity_block.has_value(),
            "count exhaustion did not return a typed local diagnostic");
    const auto& count_detail = *count_block.capacity_block;
    require(count_detail.constraint ==
                    anonsync::SyncReplicaFileEffectCapacityConstraint::
                        FolderEffectCount &&
                count_detail.state_generation == count_before.state_generation &&
                count_detail.cutpoint_digest == count_before.cutpoint_digest &&
                count_detail.effects == anonsync::SyncReplicaResourceBudget{
                    1U, 1U, 1U} &&
                count_detail.effects.would_exceed() &&
                count_detail.retained_payload_bytes ==
                    anonsync::SyncReplicaResourceBudget{3U, 3U, 64U} &&
                !count_detail.retained_payload_bytes.would_exceed() &&
                count_detail.device_effects ==
                    anonsync::SyncReplicaResourceBudget{1U, 1U, 1U} &&
                count_detail.device_effects.would_exceed() &&
                count_detail.device_retained_payload_bytes ==
                    anonsync::SyncReplicaResourceBudget{3U, 3U, 64U} &&
                !count_detail.device_retained_payload_bytes.would_exceed(),
            "count diagnostic was not bound to the exact inspected cutpoint and budgets");
    require(count_detail.actor_usage.actor == count_next_actor &&
                count_detail.actor_usage.retained_effects == 0U &&
                count_detail.device_usage.device_id ==
                    count_next_actor.device_id &&
                count_detail.device_usage.actor_epochs == 1U &&
                count_detail.device_usage.retained_effects == 1U &&
                count_detail.device_usage.retained_payload_bytes == 3U,
            "count diagnostic did not distinguish a fresh epoch from its existing device usage");
    require(count_owner.snapshot_or_throw() == count_before,
            "count capacity diagnostic advanced or rewrote durable effect authority");

    TempWorkspace byte_workspace("anonsync-file-effect-byte-block");
    auto byte_limits = effect_limits(8U, 5U);
    byte_limits.max_payload_bytes = 5U;
    const anonsync::SyncReplicaActor byte_actor{
        "device-file-effect-byte", 9321U};
    anonsync::SyncReplicaModel byte_model(folder, byte_actor, byte_limits.model);
    const std::string byte_first_payload = "abc";
    const std::string byte_next_payload = "def";
    const auto byte_first = make_file(
        byte_model, "nested/byte-first", byte_first_payload);
    const auto byte_next = make_file(
        byte_model, "nested/byte-next", byte_next_payload);
    anonsync::SyncSqliteDb byte_db = open_database(byte_workspace.database);
    anonsync::SyncReplicaFileEffectSqliteOwner byte_owner(
        byte_db.db, folder, byte_workspace.root / "files", byte_limits,
        "file-effect byte diagnostics");
    require(byte_owner.stage_or_throw(byte_first, bytes(byte_first_payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted,
            "byte diagnostic fixture did not stage its retained effect");
    const auto byte_before = byte_owner.snapshot_or_throw();
    const auto byte_block = byte_owner.stage_with_diagnostics_or_throw(
        byte_next, bytes(byte_next_payload));
    require(byte_block.result ==
                    anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked &&
                byte_block.capacity_block.has_value() &&
                byte_block.capacity_block->constraint ==
                    anonsync::SyncReplicaFileEffectCapacityConstraint::
                        FolderRetainedPayloadBytes &&
                !byte_block.capacity_block->effects.would_exceed() &&
                byte_block.capacity_block->retained_payload_bytes ==
                    anonsync::SyncReplicaResourceBudget{3U, 3U, 5U} &&
                byte_block.capacity_block->retained_payload_bytes.would_exceed() &&
                !byte_block.capacity_block->device_effects.would_exceed() &&
                byte_block.capacity_block->device_retained_payload_bytes ==
                    anonsync::SyncReplicaResourceBudget{3U, 3U, 5U} &&
                byte_block.capacity_block->device_retained_payload_bytes.would_exceed(),
            "retained-byte exhaustion did not remain distinct from effect-count exhaustion");
    require(byte_block.capacity_block->actor_usage.retained_effects == 1U &&
                byte_block.capacity_block->actor_usage.staged_effects == 1U &&
                byte_block.capacity_block->actor_usage.retained_payload_bytes ==
                    byte_first_payload.size() &&
                byte_owner.snapshot_or_throw() == byte_before,
            "byte diagnostic did not attribute current actor usage without mutation");
}

void test_device_isolation_schema_migration_and_restart() {
    TempWorkspace workspace("anonsync-file-effect-device-migration");
    const std::string folder = "folder-file-effect-device-migration";
    auto legacy_limits = effect_limits(8U, 64U);
    legacy_limits.max_payload_bytes = 64U;
    const anonsync::SyncReplicaActor first_epoch{
        "device-file-effect-isolated-a", 9401U};
    const anonsync::SyncReplicaActor second_epoch{
        "device-file-effect-isolated-a", 9402U};
    const anonsync::SyncReplicaActor other_device{
        "device-file-effect-isolated-b", 9403U};
    const anonsync::SyncReplicaActor third_epoch{
        "device-file-effect-isolated-a", 9404U};
    const anonsync::SyncReplicaActor independent_device{
        "device-file-effect-isolated-c", 9405U};
    anonsync::SyncReplicaModel first_model(
        folder, first_epoch, legacy_limits.model);
    anonsync::SyncReplicaModel second_model(
        folder, second_epoch, legacy_limits.model);
    anonsync::SyncReplicaModel other_model(
        folder, other_device, legacy_limits.model);
    anonsync::SyncReplicaModel third_epoch_model(
        folder, third_epoch, legacy_limits.model);
    anonsync::SyncReplicaModel independent_model(
        folder, independent_device, legacy_limits.model);
    const std::string first_payload = "aaa";
    const std::string second_payload = "bb";
    const std::string other_payload = "cccc";
    const auto first = make_file(
        first_model, "nested/migration-first", first_payload);
    const auto second = make_file(
        second_model, "nested/migration-second", second_payload);
    const auto other = make_file(
        other_model, "nested/migration-other", other_payload);

    anonsync::SyncSqliteDb database = open_database(workspace.database);
    anonsync::SyncReplicaFileEffectSqliteSnapshot legacy_snapshot;
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, workspace.root / "files", legacy_limits,
            "file-effect migration fixture");
        require(owner.stage_or_throw(first, bytes(first_payload)) ==
                        anonsync::SyncReplicaFileEffectStageResult::Inserted &&
                    owner.stage_or_throw(second, bytes(second_payload)) ==
                        anonsync::SyncReplicaFileEffectStageResult::Inserted &&
                    owner.stage_or_throw(other, bytes(other_payload)) ==
                        anonsync::SyncReplicaFileEffectStageResult::Inserted,
                "migration fixture did not stage its exact retained closure");
        require(owner.materialize_or_throw(first.operation_id) ==
                    anonsync::SyncReplicaFileEffectMaterializeResult::Published,
                "migration fixture did not preserve a mixed staged/published closure");
        legacy_snapshot = owner.snapshot_or_throw();
    }
    require(legacy_snapshot.effects.size() == 3U &&
                legacy_snapshot.state_generation == 4U &&
                legacy_snapshot.retained_payload_bytes == 9U,
            "migration fixture did not own the expected exact cutpoint");

    downgrade_effect_meta_to_v2_or_throw(database.db, legacy_snapshot);
    require(effect_schema_version_or_throw(database.db) == 2U,
            "test downgrade did not produce the exact legacy schema");

    // Only the two new device-isolation fields are migration input. Deliberate
    // incompatible values in every legacy field prove that v2 durable policy,
    // rather than caller defaults, remains authoritative.
    auto migration_policy = effect_limits(1U, 1U);
    migration_policy.max_payload_bytes = 1U;
    migration_policy.max_effects_per_device = 2U;
    migration_policy.max_retained_payload_bytes_per_device = 5U;
    auto expected_limits = legacy_limits;
    expected_limits.max_effects_per_device = 2U;
    expected_limits.max_retained_payload_bytes_per_device = 5U;

    anonsync::SyncReplicaFileEffectSqliteSnapshot migrated_snapshot;
    anonsync::SyncReplicaFileEffectSqliteSnapshot after_independent_insert;
    {
        anonsync::SyncReplicaFileEffectSqliteOwner migrated(
            database.db, folder, workspace.root / "files", migration_policy,
            "file-effect v2-to-v3 migration");
        migrated_snapshot = migrated.snapshot_or_throw();
        require(effect_schema_version_or_throw(database.db) == 3U &&
                    migrated_snapshot.limits == expected_limits &&
                    migrated_snapshot.effects == legacy_snapshot.effects &&
                    migrated_snapshot.actor_usage ==
                        legacy_snapshot.actor_usage &&
                    migrated_snapshot.device_usage ==
                        legacy_snapshot.device_usage &&
                    migrated_snapshot.state_generation ==
                        legacy_snapshot.state_generation &&
                    migrated_snapshot.retained_payload_bytes ==
                        legacy_snapshot.retained_payload_bytes &&
                    migrated_snapshot.effect_set_digest ==
                        legacy_snapshot.effect_set_digest &&
                    migrated_snapshot.device_usage_digest ==
                        legacy_snapshot.device_usage_digest &&
                    migrated_snapshot.cutpoint_digest !=
                        legacy_snapshot.cutpoint_digest,
                "v2-to-v3 migration changed retained authority or imported legacy caller defaults");

        require(migrated.stage_or_throw(first, bytes(first_payload)) ==
                    anonsync::SyncReplicaFileEffectStageResult::Duplicate,
                "exact duplicate reconciliation must survive a newly saturated device policy");

        const std::string count_payload = "z";
        const auto count_candidate = make_file(
            third_epoch_model, "nested/device-count-block", count_payload);
        const auto count_block = migrated.stage_with_diagnostics_or_throw(
            count_candidate, bytes(count_payload));
        require(count_block.result ==
                        anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked &&
                    count_block.capacity_block.has_value() &&
                    count_block.capacity_block->constraint ==
                        anonsync::SyncReplicaFileEffectCapacityConstraint::
                            DeviceEffectCount &&
                    count_block.capacity_block->effects ==
                        anonsync::SyncReplicaResourceBudget{3U, 1U, 8U} &&
                    !count_block.capacity_block->effects.would_exceed() &&
                    count_block.capacity_block->device_effects ==
                        anonsync::SyncReplicaResourceBudget{2U, 1U, 2U} &&
                    count_block.capacity_block->device_effects.would_exceed() &&
                    count_block.capacity_block->device_retained_payload_bytes ==
                        anonsync::SyncReplicaResourceBudget{5U, 1U, 5U} &&
                    count_block.capacity_block->device_retained_payload_bytes.would_exceed() &&
                    count_block.capacity_block->actor_usage.actor ==
                        third_epoch &&
                    count_block.capacity_block->actor_usage.retained_effects == 0U &&
                    count_block.capacity_block->device_usage.actor_epochs == 2U &&
                    count_block.capacity_block->device_usage.retained_effects == 2U,
                "device-count isolation did not aggregate actor epochs at the exact pre-mutation cutpoint");
        require(migrated.snapshot_or_throw() == migrated_snapshot,
                "device-count rejection mutated durable effect authority");

        const std::string byte_payload = "dd";
        const auto byte_candidate = make_file(
            other_model, "nested/device-byte-block", byte_payload);
        const auto byte_block = migrated.stage_with_diagnostics_or_throw(
            byte_candidate, bytes(byte_payload));
        require(byte_block.result ==
                        anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked &&
                    byte_block.capacity_block.has_value() &&
                    byte_block.capacity_block->constraint ==
                        anonsync::SyncReplicaFileEffectCapacityConstraint::
                            DeviceRetainedPayloadBytes &&
                    byte_block.capacity_block->device_effects ==
                        anonsync::SyncReplicaResourceBudget{1U, 1U, 2U} &&
                    !byte_block.capacity_block->device_effects.would_exceed() &&
                    byte_block.capacity_block->device_retained_payload_bytes ==
                        anonsync::SyncReplicaResourceBudget{4U, 2U, 5U} &&
                    byte_block.capacity_block->device_retained_payload_bytes.would_exceed(),
                "device-byte isolation did not remain distinct from count and folder limits");
        require(migrated.snapshot_or_throw() == migrated_snapshot,
                "device-byte rejection mutated durable effect authority");

        const std::string independent_payload = "q";
        const auto independent = make_file(
            independent_model, "nested/independent-device", independent_payload);
        require(migrated.stage_or_throw(
                    independent, bytes(independent_payload)) ==
                    anonsync::SyncReplicaFileEffectStageResult::Inserted,
                "one saturated device incorrectly consumed another device's retained reserve");
        after_independent_insert = migrated.snapshot_or_throw();
        require(after_independent_insert.state_generation ==
                        migrated_snapshot.state_generation + 1U &&
                    after_independent_insert.effects.size() == 4U &&
                    after_independent_insert.retained_payload_bytes == 10U,
                "independent device admission did not advance exactly one transition");
    }

    auto ignored_restart_defaults = effect_limits(1U, 1U);
    ignored_restart_defaults.max_payload_bytes = 1U;
    ignored_restart_defaults.max_effects_per_device = 1U;
    ignored_restart_defaults.max_retained_payload_bytes_per_device = 1U;
    {
        anonsync::SyncReplicaFileEffectSqliteOwner restarted(
            database.db, folder, workspace.root / "files",
            ignored_restart_defaults,
            "file-effect device-policy restart");
        const auto snapshot = restarted.snapshot_or_throw();
        require(snapshot == after_independent_insert &&
                    snapshot.limits == expected_limits,
                "restart replaced persisted device policy with caller defaults");
    }
}

void test_v2_migration_fail_closed_and_rolls_back_ddl() {
    TempWorkspace workspace("anonsync-file-effect-migration-rollback");
    const std::string folder = "folder-file-effect-migration-rollback";
    auto limits = effect_limits(4U, 32U);
    limits.max_payload_bytes = 32U;
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-migration-rollback", 9411U},
        limits.model);
    const std::string payload = "rollback";
    const auto operation = make_file(
        model, "nested/rollback", payload);
    anonsync::SyncSqliteDb database = open_database(workspace.database);
    anonsync::SyncReplicaFileEffectSqliteSnapshot legacy_snapshot;
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, workspace.root / "files", limits,
            "file-effect rollback fixture");
        require(owner.stage_or_throw(operation, bytes(payload)) ==
                    anonsync::SyncReplicaFileEffectStageResult::Inserted,
                "rollback fixture did not stage its exact effect");
        legacy_snapshot = owner.snapshot_or_throw();
    }
    downgrade_effect_meta_to_v2_or_throw(database.db, legacy_snapshot);

    auto invalid_policy = limits;
    invalid_policy.max_effects_per_device = 0U;
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner owner(
                database.db, folder, workspace.root / "files",
                invalid_policy, "file-effect invalid migration policy");
        },
        "device effect limits must be positive",
        "invalid device policy must fail before legacy DDL mutation");
    require(effect_schema_version_or_throw(database.db) == 2U,
            "invalid migration policy changed the legacy schema");

    update_meta_text_or_throw(
        database.db, "cutpoint_digest", std::string(64U, '0'));
    auto migration_policy = limits;
    migration_policy.max_effects_per_device = 1U;
    migration_policy.max_retained_payload_bytes_per_device = payload.size();
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner owner(
                database.db, folder, workspace.root / "files",
                migration_policy, "file-effect tampered legacy migration");
        },
        "durable legacy cutpoint attestation mismatch",
        "tampered v2 authority must fail before migration");
    require(effect_schema_version_or_throw(database.db) == 2U,
            "tampered v2 rejection changed the legacy schema");
    update_meta_text_or_throw(
        database.db, "cutpoint_digest",
        legacy_cutpoint_digest(legacy_snapshot));

    require(sqlite3_set_authorizer(
                database.db.get(), deny_effect_meta_insert_authorizer,
                nullptr) == SQLITE_OK,
            "could not install migration rollback fault injection");
    try {
        require_error(
            [&] {
                anonsync::SyncReplicaFileEffectSqliteOwner owner(
                    database.db, folder, workspace.root / "files",
                    migration_policy, "file-effect injected migration failure");
            },
            "not authorized",
            "post-DDL metadata failure did not abort migration");
    } catch (...) {
        (void)sqlite3_set_authorizer(database.db.get(), nullptr, nullptr);
        throw;
    }
    require(sqlite3_set_authorizer(
                database.db.get(), nullptr, nullptr) == SQLITE_OK,
            "could not clear migration rollback fault injection");
    require(effect_schema_version_or_throw(database.db) == 2U,
            "failed v3 metadata insertion did not roll back legacy DDL atomically");

    anonsync::SyncReplicaFileEffectSqliteSnapshot migrated_snapshot;
    {
        anonsync::SyncReplicaFileEffectSqliteOwner migrated(
            database.db, folder, workspace.root / "files",
            migration_policy, "file-effect migration after rollback");
        migrated_snapshot = migrated.snapshot_or_throw();
        require(migrated_snapshot.effects == legacy_snapshot.effects &&
                    migrated_snapshot.effect_set_digest ==
                        legacy_snapshot.effect_set_digest &&
                    migrated_snapshot.state_generation ==
                        legacy_snapshot.state_generation &&
                    migrated_snapshot.limits.max_effects_per_device == 1U &&
                    migrated_snapshot.limits.
                            max_retained_payload_bytes_per_device ==
                        payload.size(),
                "retry after rolled-back migration did not preserve exact legacy authority");
    }
    require(effect_schema_version_or_throw(database.db) == 3U,
            "successful retry did not commit the exact v3 schema");

    update_meta_text_or_throw(
        database.db, "device_usage_digest", std::string(64U, 'f'));
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner owner(
                database.db, folder, workspace.root / "files",
                migration_policy, "file-effect device digest tamper");
        },
        "durable cutpoint attestation mismatch",
        "device-usage metadata tamper was not rejected on restart");
}

void test_conflict_capacity_and_published_contradiction() {
    TempWorkspace conflict_workspace("anonsync-file-effect-conflict");
    const std::string folder = "folder-file-effect-conflict";
    const auto limits = effect_limits();
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-conflict", 9201U}, limits.model);
    anonsync::SyncSqliteDb database = open_database(conflict_workspace.database);
    anonsync::SyncReplicaFileEffectSqliteOwner owner(
        database.db, folder, conflict_workspace.root / "files", limits,
        "file-effect conflict owner");

    const std::string payload = "authorized-payload";
    const auto operation = make_file(model, "nested/conflict.bin", payload);
    require(
        owner.stage_or_throw(operation, bytes(payload)) ==
            anonsync::SyncReplicaFileEffectStageResult::Inserted,
        "conflict test payload must stage");
    write_direct(conflict_workspace.root / "files" / "nested" /
                     "conflict.bin",
                 std::string(payload.size(), 'x'));
    require(
        owner.materialize_or_throw(operation.operation_id) ==
            anonsync::SyncReplicaFileEffectMaterializeResult::
                DestinationConflict,
        "different destination bytes must block immutable publication");
    require(owner.snapshot_or_throw().effects.front().state ==
                anonsync::SyncReplicaFileEffectState::Staged,
            "destination conflict must not fabricate a published database mark");

    TempWorkspace capacity_workspace("anonsync-file-effect-capacity");
    const auto tiny_limits = effect_limits(1U, 256U * 1024U);
    anonsync::SyncReplicaModel tiny_model(
        folder, {"device-file-effect-capacity", 9202U}, tiny_limits.model);
    const std::string one_payload = "one";
    const std::string two_payload = "two";
    const auto one = make_file(tiny_model, "nested/one", one_payload);
    const auto two = make_file(tiny_model, "nested/two", two_payload);
    anonsync::SyncSqliteDb capacity_db =
        open_database(capacity_workspace.database);
    anonsync::SyncReplicaFileEffectSqliteOwner capacity_owner(
        capacity_db.db, folder, capacity_workspace.root / "files",
        tiny_limits, "file-effect capacity owner");
    require(
        capacity_owner.stage_or_throw(one, bytes(one_payload)) ==
            anonsync::SyncReplicaFileEffectStageResult::Inserted,
        "first effect must fit the exact effect-count budget");
    require(
        capacity_owner.stage_or_throw(two, bytes(two_payload)) ==
            anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked,
        "second effect must be explicitly capacity-blocked");
    require(capacity_owner.snapshot_or_throw().state_generation == 1U,
            "capacity rejection must not advance the durable cutpoint");

    TempWorkspace missing_workspace("anonsync-file-effect-missing");
    anonsync::SyncSqliteDb missing_db = open_database(missing_workspace.database);
    anonsync::SyncReplicaModel missing_model(
        folder, {"device-file-effect-missing", 9203U}, limits.model);
    const std::string missing_payload = "published-then-removed";
    const auto missing = make_file(
        missing_model, "nested/missing", missing_payload);
    anonsync::SyncReplicaFileEffectSqliteOwner missing_owner(
        missing_db.db, folder, missing_workspace.root / "files", limits,
        "file-effect missing owner");
    (void)missing_owner.stage_or_throw(missing, bytes(missing_payload));
    (void)missing_owner.materialize_or_throw(missing.operation_id);
    std::filesystem::remove(
        missing_workspace.root / "files" / "nested" / "missing");
    require_error(
        [&] { (void)missing_owner.materialize_or_throw(missing.operation_id); },
        "published state has no final file",
        "durable publication must fail closed when its final effect disappears");
}

void test_transition_generation_tamper_fail_closed() {
    const std::string folder = "folder-file-effect-generation-tamper";
    const auto limits = effect_limits();

    TempWorkspace duplicate_workspace(
        "anonsync-file-effect-generation-duplicate");
    anonsync::SyncReplicaModel duplicate_model(
        folder, {"device-file-effect-generation-duplicate", 9251U},
        limits.model);
    const std::string first_payload = "generation-one";
    const std::string second_payload = "generation-two";
    const auto first = make_file(
        duplicate_model, "nested/generation-one", first_payload);
    const auto second = make_file(
        duplicate_model, "nested/generation-two", second_payload);
    anonsync::SyncSqliteDb duplicate_db =
        open_database(duplicate_workspace.database);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            duplicate_db.db, folder,
            duplicate_workspace.root / "files", limits,
            "file-effect duplicate-generation owner");
        (void)owner.stage_or_throw(first, bytes(first_payload));
        (void)owner.stage_or_throw(second, bytes(second_payload));
    }
    anonsync::sqlite_exec_or_throw(
        duplicate_db.db,
        "UPDATE main.sync_replica_file_effects SET staged_generation=1 "
        "WHERE operation_id='" + second.operation_id + "';",
        "file-effect duplicate generation tamper");
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner corrupted(
                duplicate_db.db, folder,
                duplicate_workspace.root / "files", limits,
                "file-effect duplicate-generation corrupted owner");
        },
        "transition generations are not the exact gap-free sequence",
        "duplicate transition generations must fail before restored authority escapes");

    TempWorkspace ordering_workspace(
        "anonsync-file-effect-generation-ordering");
    anonsync::SyncReplicaModel ordering_model(
        folder, {"device-file-effect-generation-ordering", 9252U},
        limits.model);
    const std::string published_payload = "published-generation";
    const auto published = make_file(
        ordering_model, "nested/published-generation", published_payload);
    anonsync::SyncSqliteDb ordering_db =
        open_database(ordering_workspace.database);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            ordering_db.db, folder,
            ordering_workspace.root / "files", limits,
            "file-effect publication-generation owner");
        (void)owner.stage_or_throw(published, bytes(published_payload));
        (void)owner.materialize_or_throw(published.operation_id);
    }
    anonsync::sqlite_exec_or_throw(
        ordering_db.db,
        "UPDATE main.sync_replica_file_effects SET published_generation="
        "staged_generation WHERE operation_id='" +
            published.operation_id + "';",
        "file-effect publication generation tamper");
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner corrupted(
                ordering_db.db, folder,
                ordering_workspace.root / "files", limits,
                "file-effect publication-generation corrupted owner");
        },
        "published generation is invalid",
        "publication generation must be strictly later than staging");
}

void test_payload_schema_and_cutpoint_tamper_fail_closed() {
    TempWorkspace workspace("anonsync-file-effect-tamper");
    const std::string folder = "folder-file-effect-tamper";
    const auto limits = effect_limits();
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-tamper", 9301U}, limits.model);
    const std::string payload = "tamper-evidence";
    const auto operation = make_file(model, "nested/value", payload);
    anonsync::SyncSqliteDb database = open_database(workspace.database);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, workspace.root / "files", limits,
            "file-effect tamper owner");
        (void)owner.stage_or_throw(operation, bytes(payload));
    }
    anonsync::sqlite_exec_or_throw(
        database.db,
        "UPDATE main.sync_replica_file_effects SET payload=X'00' "
        "WHERE operation_id='" + operation.operation_id + "';",
        "file-effect payload tamper");
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner corrupted(
                database.db, folder, workspace.root / "files", limits,
                "file-effect corrupted payload owner");
        },
        "payload size does not match operation",
        "payload mutation must be detected before restored authority escapes");

    TempWorkspace schema_workspace("anonsync-file-effect-schema-tamper");
    anonsync::SyncSqliteDb schema_db = open_database(schema_workspace.database);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            schema_db.db, folder, schema_workspace.root / "files", limits,
            "file-effect schema owner");
    }
    anonsync::sqlite_exec_or_throw(
        schema_db.db,
        "CREATE TABLE main.unowned_extra(value TEXT) STRICT;",
        "file-effect schema injection");
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner corrupted(
                schema_db.db, folder, schema_workspace.root / "files", limits,
                "file-effect extra-schema owner");
        },
        "does not match exact file-effect schema",
        "an unowned durable schema object must prevent reconstruction");

    TempWorkspace cutpoint_workspace("anonsync-file-effect-cutpoint-tamper");
    anonsync::SyncSqliteDb cutpoint_db =
        open_database(cutpoint_workspace.database);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            cutpoint_db.db, folder, cutpoint_workspace.root / "files", limits,
            "file-effect cutpoint owner");
    }
    anonsync::sqlite_exec_or_throw(
        cutpoint_db.db,
        "UPDATE main.sync_replica_file_effect_meta SET state_generation=1 "
        "WHERE id=1;",
        "file-effect cutpoint tamper");
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner corrupted(
                cutpoint_db.db, folder,
                cutpoint_workspace.root / "files", limits,
                "file-effect cutpoint-corrupted owner");
        },
        "state generation does not equal the retained transition count",
        "generation-only edits must be rejected as impossible transition history");

    TempWorkspace digest_workspace("anonsync-file-effect-digest-tamper");
    anonsync::SyncSqliteDb digest_db =
        open_database(digest_workspace.database);
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            digest_db.db, folder, digest_workspace.root / "files", limits,
            "file-effect digest owner");
    }
    anonsync::sqlite_exec_or_throw(
        digest_db.db,
        "UPDATE main.sync_replica_file_effect_meta SET cutpoint_digest='"
        "0000000000000000000000000000000000000000000000000000000000000000' "
        "WHERE id=1;",
        "file-effect digest tamper");
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner corrupted(
                digest_db.db, folder,
                digest_workspace.root / "files", limits,
                "file-effect digest-corrupted owner");
        },
        "durable cutpoint attestation mismatch",
        "cutpoint digest edits must be detected independently of generation history");
}


#if !defined(_WIN32)
void test_destination_component_limit_precedes_durable_stage() {
    TempWorkspace workspace("anonsync-file-effect-name-limit");
    const std::string folder = "folder-file-effect-name-limit";
    const auto limits = effect_limits();
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-name-limit", 9251U}, limits.model);
    anonsync::SyncSqliteDb database = open_database(workspace.database);
    anonsync::SyncReplicaFileEffectSqliteOwner owner(
        database.db, folder, workspace.root / "files", limits,
        "file-effect name-limit owner");

    const std::uint64_t component_limit =
        observed_component_byte_limit(workspace.root / "files");
    require(component_limit + 1U <=
                anonsync::kSyncManifestRelativePathMaxBytes,
            "test filesystem filename limit exceeds the canonical path corpus");
    const std::string payload = "name-limit-payload";
    const std::string blocked_component(
        static_cast<std::size_t>(component_limit + 1U), 'b');
    const auto blocked_operation =
        make_file(model, blocked_component, payload);
    const auto before = owner.snapshot_or_throw();
    require(
        owner.stage_or_throw(blocked_operation, bytes(payload)) ==
            anonsync::SyncReplicaFileEffectStageResult::DestinationPathBlocked,
        "one byte beyond the observed local filename ceiling must be typed before staging");
    require(owner.snapshot_or_throw() == before,
            "path-policy denial must not consume payload bytes, effect rows, or generation authority");
    std::error_code blocked_status_error;
    const bool blocked_exists = std::filesystem::exists(
        workspace.root / "files" / blocked_component,
        blocked_status_error);
    require(!blocked_exists &&
                (!blocked_status_error ||
                 blocked_status_error == std::errc::filename_too_long),
            "path-policy denial must not attempt filesystem publication");

    const std::string boundary_component(
        static_cast<std::size_t>(component_limit), 'a');
    const auto boundary_operation =
        make_file(model, boundary_component, payload);
    require(
        owner.stage_or_throw(boundary_operation, bytes(payload)) ==
            anonsync::SyncReplicaFileEffectStageResult::Inserted,
        "the exact observed local filename ceiling must remain inclusive");
    const auto after = owner.snapshot_or_throw();
    require(after.state_generation == 1U && after.effects.size() == 1U &&
                after.effects.front().operation == boundary_operation &&
                after.retained_payload_bytes == payload.size(),
            "only the locally representable boundary operation may acquire durable effect authority");
}

void test_live_root_rebind_sticky_revocation() {
    TempWorkspace workspace("anonsync-file-effect-live-root-rebind");
    const std::string folder = "folder-file-effect-live-root-rebind";
    const auto limits = effect_limits();
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-live-root-rebind", 9351U},
        limits.model);
    const std::string retained_payload = "retained-root-payload";
    const std::string rejected_payload = "replacement-root-payload";
    const auto retained = make_file(
        model, "nested/retained.bin", retained_payload);
    const auto rejected = make_file(
        model, "nested/rejected.bin", rejected_payload);
    anonsync::SyncSqliteDb database = open_database(workspace.database);

    const std::filesystem::path configured_root = workspace.root / "files";
    const std::filesystem::path displaced_root =
        workspace.root / "files-retained-identity";
    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, configured_root, limits,
            "file-effect live-root-rebind owner");
        require(
            owner.stage_or_throw(retained, bytes(retained_payload)) ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted,
            "the retained-root effect must be staged before namespace replacement");

        std::filesystem::rename(configured_root, displaced_root);
        std::filesystem::create_directories(configured_root / "nested");

        require_error(
            [&] {
                (void)owner.stage_or_throw(rejected, bytes(rejected_payload));
            },
            "path no longer names the retained directory",
            "same-path root replacement must be detected before stage mutation");
        require_error(
            [&] {
                (void)owner.materialize_or_throw(
                    retained.operation_id);
            },
            "directory authority is revoked",
            "a revoked root must block materialization before replacement-tree publication");
        require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "directory authority is revoked",
            "all later owner observations must fail after root revocation");
        require(!std::filesystem::exists(
                    configured_root / "nested" / "retained.bin") &&
                    !std::filesystem::exists(
                        configured_root / "nested" / "rejected.bin"),
                "the replacement tree must receive neither staged nor materialized bytes");

        std::filesystem::remove_all(configured_root);
        std::filesystem::rename(displaced_root, configured_root);
        require_error(
            [&] { (void)owner.snapshot_or_throw(); },
            "directory authority is revoked",
            "restoring the original pathname must not resurrect an authority after an unobserved interval");
    }

    anonsync::SyncReplicaFileEffectSqliteOwner restarted(
        database.db, folder, configured_root, limits,
        "file-effect post-rebind restarted owner");
    const auto snapshot = restarted.snapshot_or_throw();
    require(snapshot.state_generation == 1U &&
                snapshot.effects.size() == 1U &&
                snapshot.effects.front().operation.operation_id ==
                    retained.operation_id,
            "a failed rebind-stage attempt must leave the durable effect cutpoint unchanged");
    require(
        restarted.materialize_or_throw(retained.operation_id) ==
            anonsync::SyncReplicaFileEffectMaterializeResult::Published,
        "a fresh owner may resume against the restored exact root identity");
    require(read_binary(configured_root / "nested" / "retained.bin") ==
                retained_payload,
            "post-rebind recovery must publish only beneath the restored retained root");
}


void test_descendant_directory_policy_blocks_uncontrolled_publication() {
    TempWorkspace workspace("anonsync-file-effect-descendant-policy");
    const std::string folder = "folder-file-effect-descendant-policy";
    const auto limits = effect_limits();
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-descendant-policy", 9353U},
        limits.model);
    const std::string payload = "descendant-policy-payload";
    const auto operation = make_file(
        model, "nested/policy.bin", payload);
    anonsync::SyncSqliteDb database = open_database(workspace.database);
    anonsync::SyncReplicaFileEffectSqliteOwner owner(
        database.db, folder, workspace.root / "files", limits,
        "file-effect descendant-policy owner");
    (void)owner.stage_or_throw(operation, bytes(payload));

    const std::filesystem::path nested =
        workspace.root / "files" / "nested";
    std::filesystem::permissions(
        nested,
        std::filesystem::perms::owner_all |
            std::filesystem::perms::group_all,
        std::filesystem::perm_options::replace);
    require_error(
        [&] { (void)owner.materialize_or_throw(operation.operation_id); },
        "group/other-writable descendant directory",
        "publication must reject a descendant parent writable by another mode class");
    require(!std::filesystem::exists(nested / "policy.bin"),
            "a rejected descendant directory must receive no temporary or final effect entry");
    const auto staged = owner.snapshot_or_throw();
    require(staged.state_generation == 1U &&
                staged.effects.size() == 1U &&
                staged.effects.front().state ==
                    anonsync::SyncReplicaFileEffectState::Staged,
            "descendant-policy rejection must not fabricate terminal database authority");

    std::filesystem::permissions(
        nested,
        std::filesystem::perms::owner_all |
            std::filesystem::perms::group_read |
            std::filesystem::perms::group_exec |
            std::filesystem::perms::others_read |
            std::filesystem::perms::others_exec,
        std::filesystem::perm_options::replace);
    require(
        owner.materialize_or_throw(operation.operation_id) ==
            anonsync::SyncReplicaFileEffectMaterializeResult::Published,
        "restoring an owner-controlled descendant permits a fresh bounded publication attempt");
    require(read_binary(nested / "policy.bin") == payload,
            "the accepted descendant publication must preserve exact bytes");
}

void test_restart_rejects_same_path_replacement_root() {
    TempWorkspace workspace("anonsync-file-effect-restart-root-rebind");
    const std::string folder = "folder-file-effect-restart-root-rebind";
    const auto limits = effect_limits();
    anonsync::SyncReplicaModel model(
        folder, {"device-file-effect-restart-root-rebind", 9352U},
        limits.model);
    const std::string payload = "restart-root-identity";
    const auto operation = make_file(
        model, "nested/restart.bin", payload);
    anonsync::SyncSqliteDb database = open_database(workspace.database);
    const std::filesystem::path configured_root = workspace.root / "files";
    const std::filesystem::path displaced_root =
        workspace.root / "files-original-identity";
    std::string original_authority_digest;

    {
        anonsync::SyncReplicaFileEffectSqliteOwner owner(
            database.db, folder, configured_root, limits,
            "file-effect restart-root baseline owner");
        (void)owner.stage_or_throw(operation, bytes(payload));
        original_authority_digest =
            owner.snapshot_or_throw().root_authority_digest;
    }

    std::filesystem::rename(configured_root, displaced_root);
    std::filesystem::create_directories(configured_root / "nested");
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner replacement_owner(
                database.db, folder, configured_root, limits,
                "file-effect replacement-root owner");
        },
        "root directory authority identity mismatch",
        "restart must reject a different directory inode at the configured root path");
    require(std::filesystem::is_empty(configured_root / "nested"),
            "restart rejection must not create an effect in the replacement tree");

    std::filesystem::remove_all(configured_root);
    std::filesystem::rename(displaced_root, configured_root);
    anonsync::SyncReplicaFileEffectSqliteOwner restored(
        database.db, folder, configured_root, limits,
        "file-effect restored-root owner");
    const auto snapshot = restored.snapshot_or_throw();
    require(snapshot.root_authority_digest == original_authority_digest &&
                snapshot.state_generation == 1U &&
                snapshot.effects.size() == 1U &&
                snapshot.effects.front().state ==
                    anonsync::SyncReplicaFileEffectState::Staged,
            "replacement-root rejection must leave the original durable cutpoint exact");
}
#endif

void test_validation_and_names() {
    require(std::string(anonsync::sync_replica_file_effect_state_name(
                anonsync::SyncReplicaFileEffectState::Published)) ==
                "published",
            "effect state names must be stable");
    require(std::string(anonsync::sync_replica_file_effect_stage_result_name(
                anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked)) ==
                "capacity_blocked",
            "stage result names must be stable");
    require(std::string(anonsync::sync_replica_file_effect_stage_result_name(
                anonsync::SyncReplicaFileEffectStageResult::
                    DestinationPathBlocked)) == "destination_path_blocked",
            "path-policy stage result name must be stable");
    require(std::string(
                anonsync::sync_replica_file_effect_capacity_constraint_name(
                    anonsync::SyncReplicaFileEffectCapacityConstraint::
                        DeviceRetainedPayloadBytes)) ==
                "device_retained_payload_bytes",
            "device capacity constraint names must be stable");
    require(std::string(
                anonsync::sync_replica_file_effect_materialize_result_name(
                    anonsync::SyncReplicaFileEffectMaterializeResult::
                        DestinationConflict)) == "destination_conflict",
            "materialization result names must be stable");

    TempWorkspace workspace("anonsync-file-effect-validation");
    anonsync::SyncSqliteDb database = open_database(workspace.database);
    auto invalid_limits = effect_limits();
    invalid_limits.max_payload_bytes =
        invalid_limits.max_retained_payload_bytes + 1U;
    require_error(
        [&] {
            anonsync::SyncReplicaFileEffectSqliteOwner owner(
                database.db, "folder-validation",
                workspace.root / "files", invalid_limits,
                "file-effect invalid limits");
        },
        "per-payload limit exceeds retained-payload limit",
        "internally inconsistent payload limits must fail before schema creation");
}

}  // namespace

int main() {
    try {
        test_stage_materialize_restart_and_ambiguous_recovery();
        test_exact_usage_and_capacity_diagnostics();
        test_device_isolation_schema_migration_and_restart();
        test_v2_migration_fail_closed_and_rolls_back_ddl();
        test_conflict_capacity_and_published_contradiction();
        test_transition_generation_tamper_fail_closed();
        test_payload_schema_and_cutpoint_tamper_fail_closed();
#if !defined(_WIN32)
        test_destination_component_limit_precedes_durable_stage();
        test_live_root_rebind_sticky_revocation();
        test_descendant_directory_policy_blocks_uncontrolled_publication();
        test_restart_rejects_same_path_replacement_root();
#endif
        test_validation_and_names();
        std::cout << "sync replica file-effect SQLite owner tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica file-effect SQLite owner test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
