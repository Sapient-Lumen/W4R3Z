#pragma once

#if !defined(_WIN32)

#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_file_tls_server.hpp"
#include "sync_replica_folder_process.hpp"
#include "sync_replica_numeric_listener.hpp"

#include <cstdint>
#include <memory>
#include <string>

namespace anonsync {

// Existing-only inbound owner for one configured combined peer deployment.
// It always retains immutable TLS context, membership/anchor owners,
// replica/effect owners, payload store, and the existing file and reconciliation
// application services. Direct/Tor-target construction also retains one numeric
// listener; native-overlay construction accepts an already-owned connected
// stream instead. Bootstrap and retry/lifetime policy stay outside this class.
// Construction and every serve call must occur on one thread because the SQLite
// owners (and the optional listener) are thread-bound capabilities.
class SyncReplicaPeerServerOwner final {
public:
    // Replica and payload authority are borrowed from the exact configured-
    // folder process so a long-running peer cannot accidentally open a
    // competing connection to the same exclusive operational database. There
    // is deliberately no second owning constructor: standalone serve commands
    // retain their existing preflight order until they can delegate the whole
    // operation rather than only part of it.
    SyncReplicaPeerServerOwner(
        SyncReplicaFolderProcessOwner& folder_process,
        SyncReplicaFileTlsServerContext server_context,
        SyncReplicaNumericStreamEndpoint listen_endpoint,
        std::string label = "sync replica borrowed peer server owner");

    // Application/TLS authority without a numeric listener. Native overlay
    // owners feed their exact accepted stream through serve_connected_or_throw,
    // avoiding a second same-host ingress path.
    SyncReplicaPeerServerOwner(
        SyncReplicaFolderProcessOwner& folder_process,
        SyncReplicaFileTlsServerContext server_context,
        std::string label);
    ~SyncReplicaPeerServerOwner() noexcept;

    SyncReplicaPeerServerOwner(const SyncReplicaPeerServerOwner&) = delete;
    SyncReplicaPeerServerOwner& operator=(
        const SyncReplicaPeerServerOwner&) = delete;
    SyncReplicaPeerServerOwner(SyncReplicaPeerServerOwner&&) = delete;
    SyncReplicaPeerServerOwner& operator=(
        SyncReplicaPeerServerOwner&&) = delete;

    [[nodiscard]] const SyncReplicaDeploymentManifest& deployment()
        const noexcept;
    [[nodiscard]] bool has_listener() const noexcept;

    // Source-manifest acceleration owned by the exact inbound reconciliation
    // service. Status is filesystem-cold. Explicit discovery may restore one
    // checksum-framed durable acceleration record after restart; every later
    // pulse still reopens only the selected digest-named payload and releases
    // all payload authority before returning. The surrounding peer-service
    // owner remains responsible for ordinary-turn fairness.
    [[nodiscard]]
    SyncReplicaReconciliationSourceManifestProjectionStatus
    source_manifest_projection_status() const;

    [[nodiscard]]
    SyncReplicaReconciliationSourceManifestProjectionStatus
    discover_source_manifest_projection_or_throw();

    [[nodiscard]]
    SyncReplicaReconciliationSourceManifestProjectionStepResult
    continue_source_manifest_projection_or_throw();

    [[nodiscard]] SyncReplicaPeerTlsServerResult serve_one_or_throw(
        const SyncReplicaFileTlsServerDeadlines& deadlines,
        std::uint64_t reconciliation_max_round_trips =
            kSyncReplicaReconciliationTlsDefaultMaxRoundTrips,
        const std::string& session_label =
            "sync replica peer server session");

    [[nodiscard]] SyncReplicaPeerTlsServerResult serve_connected_or_throw(
        SyncReplicaConnectedStream stream,
        const SyncReplicaFileTlsServerDeadlines& deadlines,
        std::uint64_t reconciliation_max_round_trips =
            kSyncReplicaReconciliationTlsDefaultMaxRoundTrips,
        const std::string& session_label =
            "sync replica peer connected-stream session");

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
