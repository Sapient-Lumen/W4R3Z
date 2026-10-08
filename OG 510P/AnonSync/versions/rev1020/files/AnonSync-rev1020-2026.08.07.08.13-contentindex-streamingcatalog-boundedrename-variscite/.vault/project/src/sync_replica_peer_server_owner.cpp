#include "sync_replica_peer_server_owner.hpp"

#if !defined(_WIN32)

#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_deployment_identity.hpp"
#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_file_effect_sqlite_owner.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_operational_database.hpp"
#include "sync_replica_reconciliation_protocol.hpp"
#include "sync_replica_reconciliation_service.hpp"
#include "sync_replica_stream_connector.hpp"
#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"
#include "sync_replica_tls_membership_anchored_owner.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"

#include <limits>
#include <optional>
#include <stdexcept>
#include <utility>

namespace anonsync {
namespace {

void validate_combined_deployment_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    validate_sync_replica_deployment_manifest_or_throw(
        deployment, label + " manifest");
    if (!deployment.payload_root.has_value() ||
        !deployment.effect_db.has_value() ||
        !deployment.files_root.has_value() ||
        !deployment.membership_db.has_value() ||
        !deployment.anchor_db.has_value()) {
        throw std::invalid_argument(
            label +
            " requires payload_root, effect_db, files_root, membership_db, and anchor_db");
    }
}

[[nodiscard]] SyncReplicaSqliteDeploymentBinding binding_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::filesystem::path& path,
    SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    SyncReplicaSqliteDeploymentBinding binding{
        .deployment = sync_replica_deployment_identity_or_throw(
            deployment, label + " identity"),
        .role = role,
        .database_path = path,
    };
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        binding, label + " binding");
    return binding;
}

[[nodiscard]] SyncReplicaOperationalDatabase open_bound_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::filesystem::path& path,
    SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    SyncReplicaOperationalDatabase database =
        SyncReplicaOperationalDatabase::open_or_throw(
            path,
            SyncReplicaOperationalDatabaseOpenDisposition::ExistingOperational,
            label);
    attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.handle(), binding_or_throw(deployment, path, role, label),
        label + " store-set binding");
    return database;
}

[[nodiscard]] SyncReplicaFileDeliveryServiceLimits file_service_limits(
    std::uint64_t max_payload_bytes) {
    SyncReplicaFileDeliveryServiceLimits limits;
    // File-delivery v2 is the retained small-file compatibility protocol: it
    // owns one complete payload in one request frame. Larger configured files
    // must use bounded reconciliation ranges instead of silently expanding an
    // authenticated peer's one-frame memory authority to the folder ceiling.
    const std::uint64_t bounded_payload_bytes =
        sync_replica_file_delivery_single_frame_payload_limit(
            max_payload_bytes);
    limits.max_payload_bytes = bounded_payload_bytes;
    static_assert(
        kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes >=
        kSyncReplicaFileDeliveryDefaultMaxPayloadBytes);
    constexpr std::uint64_t kDefaultNonPayloadHeadroom =
        kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes -
        kSyncReplicaFileDeliveryDefaultMaxPayloadBytes;
    if (bounded_payload_bytes >
        std::numeric_limits<std::uint64_t>::max() -
            kDefaultNonPayloadHeadroom) {
        throw std::invalid_argument(
            "peer server payload request-frame ceiling overflow");
    }
    limits.max_request_frame_bytes =
        bounded_payload_bytes + kDefaultNonPayloadHeadroom;
    return limits;
}

[[nodiscard]] SyncReplicaReconciliationProtocolLimits reconciliation_limits(
    std::uint64_t max_payload_bytes) {
    SyncReplicaReconciliationProtocolLimits limits;
    limits.max_single_payload_bytes =
        sync_replica_reconciliation_single_payload_limit(
            max_payload_bytes);
    limits.max_payload_bytes_per_page =
        kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage;
    limits.max_payload_extent_bytes = max_payload_bytes;
    validate_sync_replica_reconciliation_protocol_limits_or_throw(limits);
    return limits;
}

[[nodiscard]] SyncReplicaFileEffectSqliteOwnerLimits effect_limits(
    std::uint64_t max_payload_bytes) {
    SyncReplicaFileEffectSqliteOwnerLimits limits;
    // The durable effect owner belongs only to the legacy one-frame delivery
    // path. Resumable reconciliation owns larger configured file extents, so
    // widening this whole-payload store would add memory authority without a
    // shipping caller that can use it.
    limits.max_payload_bytes =
        sync_replica_file_delivery_single_frame_payload_limit(
            max_payload_bytes);
    return limits;
}

}  // namespace

struct SyncReplicaPeerServerOwner::State final {
    SyncReplicaDeploymentManifest deployment;
    SyncReplicaFileTlsServerContext server_context;
    std::unique_ptr<SyncReplicaNumericListener> listener;
    SyncReplicaOperationalDatabase membership_database;
    SyncReplicaOperationalDatabase anchor_database;
    SyncReplicaOperationalDatabase effect_database;
    std::unique_ptr<SyncReplicaTlsMembershipSqliteOwner> membership_owner;
    std::unique_ptr<SyncReplicaTlsMembershipAnchorSqliteOwner> anchor_owner;
    std::unique_ptr<SyncReplicaTlsMembershipAnchoredOwner>
        membership_coordinator;
    SyncReplicaSqliteOwner* replica_owner = nullptr;
    std::unique_ptr<SyncReplicaFileEffectSqliteOwner> effect_owner;
    std::unique_ptr<SyncReplicaFileDeliveryService> file_service;
    SyncReplicaFilePayloadStore* payload_store = nullptr;
    SyncReplicaSelectiveSyncPolicy selective_sync_policy =
        sync_replica_default_selective_sync_policy();
    std::unique_ptr<SyncReplicaReconciliationService>
        reconciliation_service;
    std::string label;

    State(
        SyncReplicaDeploymentManifest selected_deployment,
        SyncReplicaFileTlsServerContext context,
        std::string owner_label)
        : deployment(std::move(selected_deployment)),
          server_context(std::move(context)),
          label(std::move(owner_label)) {
        if (label.empty()) {
            throw std::invalid_argument(
                "sync replica peer server owner label must not be empty");
        }
        if (!server_context.active()) {
            throw std::invalid_argument(
                label + " TLS server context is inactive");
        }
        validate_combined_deployment_or_throw(deployment, label);
    }

    void initialize_common_or_throw(
        std::optional<SyncReplicaNumericStreamEndpoint> listen_endpoint) {
        // A numeric/Tor target binds first so an occupied endpoint fails before
        // the complete operational store set is opened. Native overlay ingress
        // deliberately omits this capability and enters through a SAM-owned
        // connected stream instead.
        if (listen_endpoint.has_value()) {
            listener = std::make_unique<SyncReplicaNumericListener>(
                std::move(*listen_endpoint), label + " listener");
        }

        membership_database = open_bound_or_throw(
            deployment, *deployment.membership_db,
            SyncReplicaSqliteDeploymentRole::TlsMembership,
            label + " membership database");
        anchor_database = open_bound_or_throw(
            deployment, *deployment.anchor_db,
            SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            label + " membership anchor database");
        effect_database = open_bound_or_throw(
            deployment, *deployment.effect_db,
            SyncReplicaSqliteDeploymentRole::FileEffect,
            label + " effect database");

        membership_owner =
            std::make_unique<SyncReplicaTlsMembershipSqliteOwner>(
                membership_database.handle(), deployment.folder_id,
                deployment.local_actor, label + " membership owner");
        anchor_owner =
            std::make_unique<SyncReplicaTlsMembershipAnchorSqliteOwner>(
                anchor_database.handle(), deployment.folder_id,
                deployment.local_actor,
                label + " membership anchor owner");
        membership_coordinator =
            std::make_unique<SyncReplicaTlsMembershipAnchoredOwner>(
                *membership_owner, *anchor_owner,
                label + " anchored membership coordinator");

        if (replica_owner == nullptr || payload_store == nullptr) {
            throw std::logic_error(
                label + " omitted replica or payload ownership");
        }
        effect_owner =
            std::make_unique<SyncReplicaFileEffectSqliteOwner>(
                effect_database.handle(), deployment.folder_id,
                *deployment.files_root,
                effect_limits(deployment.max_payload_bytes),
                label + " effect owner");
        file_service = std::make_unique<SyncReplicaFileDeliveryService>(
            *replica_owner, effect_owner.get(),
            file_service_limits(deployment.max_payload_bytes),
            label + " file service");
        reconciliation_service =
            std::make_unique<SyncReplicaReconciliationService>(
                *replica_owner, *payload_store,
                reconciliation_limits(deployment.max_payload_bytes),
                label + " reconciliation service", selective_sync_policy);

        // Surface malformed membership/anchor state before the caller reports
        // a live endpoint. Every session refreshes the exact authority again.
        (void)membership_coordinator->current_authority_or_throw();
    }
};

SyncReplicaPeerServerOwner::SyncReplicaPeerServerOwner(
    SyncReplicaFolderProcessOwner& folder_process,
    SyncReplicaFileTlsServerContext server_context,
    SyncReplicaNumericStreamEndpoint listen_endpoint,
    std::string label) {
    auto state = std::make_unique<State>(
        folder_process.deployment(), std::move(server_context),
        std::move(label));
    state->replica_owner = &folder_process.replica_owner_or_throw();
    state->payload_store = &folder_process.payload_store_or_throw();
    state->selective_sync_policy = folder_process.folder_owner_or_throw()
        .selective_sync_policy_snapshot_or_throw();
    state->initialize_common_or_throw(std::move(listen_endpoint));
    state_ = std::move(state);
}

SyncReplicaPeerServerOwner::SyncReplicaPeerServerOwner(
    SyncReplicaFolderProcessOwner& folder_process,
    SyncReplicaFileTlsServerContext server_context,
    std::string label) {
    auto state = std::make_unique<State>(
        folder_process.deployment(), std::move(server_context),
        std::move(label));
    state->replica_owner = &folder_process.replica_owner_or_throw();
    state->payload_store = &folder_process.payload_store_or_throw();
    state->selective_sync_policy = folder_process.folder_owner_or_throw()
        .selective_sync_policy_snapshot_or_throw();
    state->initialize_common_or_throw(std::nullopt);
    state_ = std::move(state);
}

SyncReplicaPeerServerOwner::~SyncReplicaPeerServerOwner() noexcept = default;

const SyncReplicaDeploymentManifest&
SyncReplicaPeerServerOwner::deployment() const noexcept {
    return state_->deployment;
}

bool SyncReplicaPeerServerOwner::has_listener() const noexcept {
    return state_ && state_->listener != nullptr;
}

SyncReplicaReconciliationSourceManifestProjectionStatus
SyncReplicaPeerServerOwner::source_manifest_projection_status() const {
    if (!state_ || !state_->reconciliation_service) {
        throw std::logic_error(
            "sync replica peer server owner is inactive");
    }
    return state_->reconciliation_service->source_manifest_projection_status();
}

SyncReplicaReconciliationSourceManifestProjectionStatus
SyncReplicaPeerServerOwner::discover_source_manifest_projection_or_throw() {
    if (!state_ || !state_->reconciliation_service) {
        throw std::logic_error(
            "sync replica peer server owner is inactive");
    }
    return state_->reconciliation_service
        ->discover_source_manifest_projection_or_throw();
}

SyncReplicaReconciliationSourceManifestProjectionStepResult
SyncReplicaPeerServerOwner::continue_source_manifest_projection_or_throw() {
    if (!state_ || !state_->reconciliation_service) {
        throw std::logic_error(
            "sync replica peer server owner is inactive");
    }
    return state_->reconciliation_service
        ->continue_source_manifest_projection_or_throw();
}

SyncReplicaPeerTlsServerResult
SyncReplicaPeerServerOwner::serve_one_or_throw(
    const SyncReplicaFileTlsServerDeadlines& deadlines,
    std::uint64_t reconciliation_max_round_trips,
    const std::string& session_label) {
    if (session_label.empty()) {
        throw std::invalid_argument(
            "sync replica peer server session label must not be empty");
    }
    if (!state_ || !state_->server_context.active() || !state_->listener ||
        !state_->membership_coordinator || !state_->file_service ||
        !state_->reconciliation_service) {
        throw std::logic_error("sync replica peer server owner is inactive");
    }
    auto membership =
        state_->membership_coordinator->current_authority_or_throw();
    return serve_one_sync_replica_peer_tls_session_or_throw(
        *state_->file_service, *state_->reconciliation_service,
        state_->listener->listener_or_throw(),
        state_->server_context.retain_another_or_throw(
            state_->label + " retained server context"),
        std::move(membership), deadlines, reconciliation_max_round_trips,
        session_label);
}

SyncReplicaPeerTlsServerResult
SyncReplicaPeerServerOwner::serve_connected_or_throw(
    SyncReplicaConnectedStream stream,
    const SyncReplicaFileTlsServerDeadlines& deadlines,
    std::uint64_t reconciliation_max_round_trips,
    const std::string& session_label) {
    if (session_label.empty()) {
        throw std::invalid_argument(
            "sync replica peer connected-stream session label must not be empty");
    }
    if (!state_ || !state_->server_context.active() ||
        !state_->membership_coordinator || !state_->file_service ||
        !state_->reconciliation_service) {
        throw std::logic_error("sync replica peer server owner is inactive");
    }
    auto membership =
        state_->membership_coordinator->current_authority_or_throw();
    return serve_one_sync_replica_peer_tls_connected_stream_or_throw(
        *state_->file_service, *state_->reconciliation_service,
        std::move(stream),
        state_->server_context.retain_another_or_throw(
            state_->label + " retained server context"),
        std::move(membership), deadlines, reconciliation_max_round_trips,
        session_label);
}

}  // namespace anonsync

#endif
