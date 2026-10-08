#pragma once

#if !defined(_WIN32)

#include "sync_replica_deployment_identity.hpp"
#include "sync_replica_file_content_inventory.hpp"
#include "sync_replica_model.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaFilePayloadStoreMaxEntries =
    kSyncReplicaFileContentInventoryMaxEntries;
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadStoreMaxTransientEntries = 65536U;

struct SyncReplicaFilePayloadStoreLimits final {
    std::uint64_t max_entries = 4096U;
    std::uint64_t max_payload_bytes = 4ULL * 1024ULL * 1024ULL;
    std::uint64_t max_indexed_bytes = 64ULL * 1024ULL * 1024ULL * 1024ULL;
    std::uint64_t max_transient_entries = 4096U;
    std::uint64_t max_transient_bytes = 64ULL * 1024ULL * 1024ULL;

    bool operator==(const SyncReplicaFilePayloadStoreLimits&) const = default;
};

void validate_sync_replica_file_payload_store_limits_or_throw(
    const SyncReplicaFilePayloadStoreLimits& limits);

enum class SyncReplicaFilePayloadStorePutDisposition : std::uint8_t {
    Inserted = 1,
    AlreadyPresent = 2,
};

// Separates observation/mutation authority from bootstrap authority. An
// ExistingOnly store may use an exact durable identity marker but can never
// adopt an unbound directory or mint that marker. CreateIfMissing is reserved
// for explicit bootstrap and still validates the complete pre-existing
// namespace before publishing the immutable folder binding.
enum class SyncReplicaFilePayloadStoreOpenDisposition : std::uint8_t {
    ExistingOnly = 1,
    CreateIfMissing = 2,
};

struct SyncReplicaFilePayloadStorePutResult final {
    SyncReplicaFilePayloadStorePutDisposition disposition =
        SyncReplicaFilePayloadStorePutDisposition::Inserted;
    std::string content_sha256;
    std::uint64_t size_bytes = 0U;

    bool operator==(const SyncReplicaFilePayloadStorePutResult&) const =
        default;
};

// Stable classification for the cooperative lease frontier. This is local
// availability evidence, not operation, attempt, or effect authority.
enum class SyncReplicaFilePayloadStoreLeaseMode : std::uint8_t {
    SharedObservation = 1,
    ExclusiveMutation = 2,
};

// Typed local availability result for a cooperative shared/exclusive lease
// conflict. No payload, attempt, or effect authority has been consumed when
// this exception is raised; callers may retry from a fresh observation
// cutpoint without parsing diagnostic text.
class SyncReplicaFilePayloadStoreLeaseBusyError final
    : public std::runtime_error {
public:
    SyncReplicaFilePayloadStoreLeaseBusyError(
        SyncReplicaFilePayloadStoreLeaseMode mode,
        const std::string& message)
        : std::runtime_error(message), mode_(mode) {}

    [[nodiscard]] SyncReplicaFilePayloadStoreLeaseMode mode() const noexcept {
        return mode_;
    }

private:
    SyncReplicaFilePayloadStoreLeaseMode mode_ =
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation;
};

class SyncReplicaFilePayloadStore;

// Move-only, thread-affine read authority for one bounded observation of a
// durable content directory. Construction acquires a fail-fast shared advisory
// lease on the exact folder-identity marker, passes that move-only witness into
// a dedicated private-root scan, rejects unexpected namespace entries, hashes
// each immutable digest-named regular file without retaining the working set,
// synchronizes file and directory state, re-proves that the marker name still
// identifies the exact locked inode, and freezes a canonical digest/size index.
// The scan is not hostile-writer-exclusive: noncooperating same-UID/privileged
// writers and
// filesystems that cannot prove independent-open flock exclusion remain outside
// this authority. Lease contention fails rather than blocking an event loop.
//
// The snapshot may be reused synchronously across multiple claim attempts. It
// reopens the selected digest relative to its retained root descriptor and
// rechecks exact size and SHA-256 after a claim is minted. External deletion or
// replacement therefore becomes an exact local preparation failure that the
// file-delivery service releases onto its bounded retry schedule; it cannot
// manufacture a request for different bytes.
class SyncReplicaFilePayloadStoreSnapshot final {
public:
    SyncReplicaFilePayloadStoreSnapshot() noexcept = default;
    SyncReplicaFilePayloadStoreSnapshot(
        const SyncReplicaFilePayloadStoreSnapshot&) = delete;
    SyncReplicaFilePayloadStoreSnapshot& operator=(
        const SyncReplicaFilePayloadStoreSnapshot&) = delete;
    SyncReplicaFilePayloadStoreSnapshot(
        SyncReplicaFilePayloadStoreSnapshot&&) noexcept;
    SyncReplicaFilePayloadStoreSnapshot& operator=(
        SyncReplicaFilePayloadStoreSnapshot&&) noexcept;
    ~SyncReplicaFilePayloadStoreSnapshot() noexcept;

    [[nodiscard]] bool active() const noexcept {
        return static_cast<bool>(state_);
    }

    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] const std::filesystem::path& root_path() const;
    [[nodiscard]] std::uint64_t entry_count() const;
    [[nodiscard]] std::uint64_t indexed_bytes() const;
    [[nodiscard]] std::uint64_t transient_entry_count() const;
    [[nodiscard]] std::uint64_t transient_bytes() const;
    [[nodiscard]] const std::string& root_attestation_digest() const;
    [[nodiscard]] const std::string& snapshot_digest() const;
    [[nodiscard]] const SyncReplicaFilePayloadStoreLimits& limits() const;

    [[nodiscard]] SyncReplicaFileContentInventory content_inventory() const;
    [[nodiscard]] std::optional<std::uint64_t> payload_size_or_none(
        std::string_view content_sha256) const;

    [[nodiscard]] std::string copy_payload_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label =
            "sync replica durable file payload lookup") const;

    void require_folder_or_throw(
        std::string_view folder_id,
        std::string_view label) const;

    // Pure pre-claim authority reproof. No payload bytes are read and no
    // durable sender state is touched.
    void preflight_or_throw(std::string_view label) const;

private:
    struct State;

    explicit SyncReplicaFilePayloadStoreSnapshot(
        std::unique_ptr<State> state) noexcept;

    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::unique_ptr<State> state_;

    friend class SyncReplicaFilePayloadStore;
};

// Durable content-addressed directory owner. Payload bytes are published under
// their full lowercase SHA-256 name through the existing descriptor-relative,
// create-new, file-sync, no-replace rename, and directory-sync owner. A put holds
// a fail-fast exclusive advisory lease on the exact immutable folder marker from
// full-store capacity preflight through publication/reconciliation. The scan
// requires that exact lease witness and re-proves the locked anchor after
// traversal. Cooperative processes using this owner therefore cannot
// independently spend the same
// aggregate budget. The root must already exist as a dedicated private
// directory; this class never guesses directory creation, cleanup, garbage
// collection, or hostile-writer authority.
class SyncReplicaFilePayloadStore final {
public:
    SyncReplicaFilePayloadStore(
        std::string folder_id,
        std::filesystem::path absolute_root_directory,
        SyncReplicaFilePayloadStoreOpenDisposition disposition,
        SyncReplicaFilePayloadStoreLimits limits = {},
        std::string label = "sync replica file payload store");

    // Product-bound form. The immutable v3 identity/lease anchor commits the
    // deployment ID, exact manifest digest/path, folder, and local actor. It is
    // intentionally incompatible with the standalone v2 folder-only marker so
    // an independently initialized payload directory cannot be recomposed into
    // a committed product deployment.
    SyncReplicaFilePayloadStore(
        SyncReplicaDeploymentIdentity deployment_identity,
        std::filesystem::path absolute_root_directory,
        SyncReplicaFilePayloadStoreOpenDisposition disposition,
        SyncReplicaFilePayloadStoreLimits limits = {},
        std::string label = "sync replica product-bound file payload store");

    SyncReplicaFilePayloadStore(
        const SyncReplicaFilePayloadStore&) = delete;
    SyncReplicaFilePayloadStore& operator=(
        const SyncReplicaFilePayloadStore&) = delete;
    SyncReplicaFilePayloadStore(
        SyncReplicaFilePayloadStore&&) = delete;
    SyncReplicaFilePayloadStore& operator=(
        SyncReplicaFilePayloadStore&&) = delete;
    ~SyncReplicaFilePayloadStore() noexcept;

    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] const std::filesystem::path& root_path() const;
    [[nodiscard]] const SyncReplicaFilePayloadStoreLimits& limits() const;

    [[nodiscard]] SyncReplicaFilePayloadStorePutResult put_payload_or_throw(
        std::string payload);

    [[nodiscard]] SyncReplicaFilePayloadStoreSnapshot snapshot_or_throw() const;

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
