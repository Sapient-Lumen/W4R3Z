#pragma once

#include "sync_replica_model.hpp"
#include "sync_sqlite_support.hpp"

#if !defined(_WIN32)
#include "sync_directory_authority.hpp"
#endif

#include <cstdint>
#include <filesystem>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace anonsync {

// Durable receiver-side policy for exact file effects. The operation limits are
// persisted because canonical operation bytes must remain decodable after a
// restart even if caller defaults change. Payload and aggregate limits are
// independent of the causal evidence owner's retention policy.
struct SyncReplicaFileEffectSqliteOwnerLimits final {
    SyncReplicaModelLimits model;
    std::uint64_t max_effects = 10000U;
    std::uint64_t max_payload_bytes = 4U * 1024U * 1024U;
    std::uint64_t max_retained_payload_bytes =
        256ULL * 1024ULL * 1024ULL;
    // A device quota spans every retained actor epoch with the same durable
    // device_id. It is intentionally not described as a user/account quota:
    // actor enrollment and membership authority live above this owner.
    std::uint64_t max_effects_per_device = 2500U;
    std::uint64_t max_retained_payload_bytes_per_device =
        64ULL * 1024ULL * 1024ULL;

    bool operator==(
        const SyncReplicaFileEffectSqliteOwnerLimits&) const = default;
};

enum class SyncReplicaFileEffectState {
    Staged,
    Published,
};

enum class SyncReplicaFileEffectStageResult {
    Inserted,
    Duplicate,
    CapacityBlocked,
    // The canonical identity is valid, but at least one path component is
    // provably outside the retained destination filesystem's byte ceiling.
    // No effect row or payload authority is created for this result.
    DestinationPathBlocked,
};

// Deterministic first violated admission boundary. Folder limits remain the
// final aggregate safety cap. Device limits isolate unrelated durable device
// identities from one another across actor-epoch rotation.
enum class SyncReplicaFileEffectCapacityConstraint {
    None,
    FolderEffectCount,
    FolderRetainedPayloadBytes,
    DeviceEffectCount,
    DeviceRetainedPayloadBytes,
};

// Exact, re-derived accounting for one event-minting actor namespace. These
// summaries are diagnostics/acceleration only: the canonical operation and
// payload rows remain authority, and every owner load reconstructs the
// summaries from that complete retained set.
struct SyncReplicaFileEffectActorUsage final {
    SyncReplicaActor actor;
    std::uint64_t retained_effects = 0U;
    std::uint64_t staged_effects = 0U;
    std::uint64_t published_effects = 0U;
    std::uint64_t retained_payload_bytes = 0U;

    bool operator==(const SyncReplicaFileEffectActorUsage&) const = default;
};

// Device aggregation deliberately does not claim that device_id is a human,
// account, or membership principal. It is the stable identifier already
// committed by retained actor epochs and gives later quota/fairness work an
// exact observable baseline without manufacturing new identity authority.
struct SyncReplicaFileEffectDeviceUsage final {
    std::string device_id;
    std::uint64_t actor_epochs = 0U;
    std::uint64_t retained_effects = 0U;
    std::uint64_t staged_effects = 0U;
    std::uint64_t published_effects = 0U;
    std::uint64_t retained_payload_bytes = 0U;

    bool operator==(const SyncReplicaFileEffectDeviceUsage&) const = default;
};

// Local explanation of one exact capacity rejection. The global budgets use
// the same subtraction-safe resource shape as causal evidence admission. The
// cutpoint fields bind the explanation to the complete effect state inspected
// inside the stage transaction; they are intentionally not serialized into a
// peer-controlled wire receipt.
struct SyncReplicaFileEffectCapacityBlock final {
    std::uint64_t state_generation = 0U;
    std::string cutpoint_digest;
    SyncReplicaFileEffectCapacityConstraint constraint =
        SyncReplicaFileEffectCapacityConstraint::None;
    SyncReplicaResourceBudget effects;
    SyncReplicaResourceBudget retained_payload_bytes;
    SyncReplicaResourceBudget device_effects;
    SyncReplicaResourceBudget device_retained_payload_bytes;
    SyncReplicaFileEffectActorUsage actor_usage;
    SyncReplicaFileEffectDeviceUsage device_usage;

    bool operator==(const SyncReplicaFileEffectCapacityBlock&) const = default;
};

struct SyncReplicaFileEffectStageOutcome final {
    SyncReplicaFileEffectStageResult result =
        SyncReplicaFileEffectStageResult::CapacityBlocked;
    std::optional<SyncReplicaFileEffectCapacityBlock> capacity_block;

    bool operator==(const SyncReplicaFileEffectStageOutcome&) const = default;
};

enum class SyncReplicaFileEffectMaterializeResult {
    Published,
    AlreadyPublished,
    DestinationConflict,
};

struct SyncReplicaFileEffectRecord final {
    std::string effect_id;
    SyncReplicaOperation operation;
    SyncReplicaFileEffectState state = SyncReplicaFileEffectState::Staged;
    std::uint64_t staged_generation = 0;
    std::uint64_t published_generation = 0;
    std::string publication_digest;

    bool operator==(const SyncReplicaFileEffectRecord&) const = default;
};

// Bounded current owner identity and persisted policy. Constructor-time full
// reconstruction remains the cold authority for retained effects; this
// cutpoint re-attests only the exact schema, root binding, immutable limits,
// and current generation. It never loads canonical operations or payloads.
struct SyncReplicaFileEffectSqliteIdentityCutpoint final {
    std::string folder_id;
    std::filesystem::path root_path;
    std::string root_authority_digest;
    SyncReplicaFileEffectSqliteOwnerLimits limits;
    std::uint64_t state_generation = 0U;

    bool operator==(
        const SyncReplicaFileEffectSqliteIdentityCutpoint&) const = default;
};

struct SyncReplicaFileEffectSqliteSnapshot final {
    std::string folder_id;
    std::filesystem::path root_path;
    std::string root_authority_digest;
    SyncReplicaFileEffectSqliteOwnerLimits limits;
    std::uint64_t state_generation = 0;
    std::uint64_t retained_payload_bytes = 0;
    std::vector<SyncReplicaFileEffectRecord> effects;
    std::vector<SyncReplicaFileEffectActorUsage> actor_usage;
    std::vector<SyncReplicaFileEffectDeviceUsage> device_usage;
    std::string effect_set_digest;
    std::string device_usage_digest;
    std::string cutpoint_digest;

    bool operator==(const SyncReplicaFileEffectSqliteSnapshot&) const = default;
};

// Read-only exact-schema observation. The selected filesystem root is opened
// and re-attested, but no schema initialization, migration, effect publication,
// or filesystem synchronization is attempted.
[[nodiscard]] SyncReplicaFileEffectSqliteSnapshot
inspect_sync_replica_file_effect_sqlite_snapshot_read_only_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    std::filesystem::path root_path,
    std::string label =
        "sync replica file-effect read-only SQLite inspection");

// Offline artifact counterpart. The exact database binding is attested by the
// caller before this function. It validates the persisted root pathname and
// authority digest without opening the selected files root, then restores and
// re-proves the complete current-schema effect state in one deferred read-only
// transaction. This is inspection authority only: it cannot initialize,
// migrate, publish, or synchronize filesystem effects.
[[nodiscard]] SyncReplicaFileEffectSqliteSnapshot
inspect_sync_replica_file_effect_sqlite_snapshot_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    std::filesystem::path expected_root_path,
    std::string label =
        "sync replica file-effect offline SQLite inspection");

[[nodiscard]] SyncReplicaFileEffectSqliteSnapshot
inspect_sync_replica_file_effect_sqlite_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    std::filesystem::path expected_root_path,
    std::string label =
        "sync replica detached file-effect offline SQLite inspection");

// A separate database owner for receiver payload/effect authority. stage() is
// committed before causal admission. materialize() first reconciles the exact
// immutable destination, publishes with create-new semantics only when absent,
// and marks Published only after file and parent-directory durability are
// established. A crash after namespace publication but before the database
// mark is recovered by exact-byte reconciliation; no sender settlement is
// implied by this class. Every public operation restores and re-attests the
// complete retained set. This is intentionally an O(history) correctness
// oracle for migration, repair, and differential testing, not a scalable
// production index.
class SyncReplicaFileEffectSqliteOwner final {
public:
    SyncReplicaFileEffectSqliteOwner(
        SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        std::filesystem::path root_path,
        SyncReplicaFileEffectSqliteOwnerLimits initial_limits = {},
        std::string label = "sync replica file-effect SQLite owner");

    SyncReplicaFileEffectSqliteOwner(
        const SyncReplicaFileEffectSqliteOwner&) = delete;
    SyncReplicaFileEffectSqliteOwner& operator=(
        const SyncReplicaFileEffectSqliteOwner&) = delete;
    SyncReplicaFileEffectSqliteOwner(
        SyncReplicaFileEffectSqliteOwner&&) = delete;
    SyncReplicaFileEffectSqliteOwner& operator=(
        SyncReplicaFileEffectSqliteOwner&&) = delete;

    [[nodiscard]] SyncReplicaFileEffectSqliteSnapshot snapshot_or_throw();

    // Bounded service-composition reproof. The exact trigger-free schema,
    // root authority, folder identity, durable limits, and state generation
    // are read in one deferred transaction without touching retained effect
    // rows or payload blobs.
    [[nodiscard]] SyncReplicaFileEffectSqliteIdentityCutpoint
    identity_cutpoint_or_throw();

    [[nodiscard]] SyncReplicaFileEffectStageOutcome
    stage_with_diagnostics_or_throw(
        const SyncReplicaOperation& operation,
        std::span<const unsigned char> payload);

    // Compatibility projection for callers that need only the durable stage
    // classification. New receiver composition should retain the diagnostic
    // outcome so a capacity block remains attributable to its exact cutpoint.
    [[nodiscard]] SyncReplicaFileEffectStageResult stage_or_throw(
        const SyncReplicaOperation& operation,
        std::span<const unsigned char> payload);

    [[nodiscard]] SyncReplicaFileEffectMaterializeResult
    materialize_or_throw(const std::string& operation_id);

private:
    SyncSqliteDbHandleSlot& db_;
    std::string folder_id_;
    std::filesystem::path root_path_;
    std::string root_path_text_;
#if !defined(_WIN32)
    SyncDirectoryAuthority root_authority_;
#endif
    std::string root_authority_digest_;
    std::string label_;
};

[[nodiscard]] const char* sync_replica_file_effect_state_name(
    SyncReplicaFileEffectState state) noexcept;
[[nodiscard]] const char* sync_replica_file_effect_stage_result_name(
    SyncReplicaFileEffectStageResult result) noexcept;
[[nodiscard]] const char* sync_replica_file_effect_capacity_constraint_name(
    SyncReplicaFileEffectCapacityConstraint constraint) noexcept;
[[nodiscard]] const char* sync_replica_file_effect_materialize_result_name(
    SyncReplicaFileEffectMaterializeResult result) noexcept;

}  // namespace anonsync
