#pragma once

#if !defined(_WIN32)

#include "sync_replica_file_tls_client.hpp"
#include "sync_replica_folder_process.hpp"
#include "sync_replica_reconciliation_service.hpp"
#include "sync_replica_session_supervisor.hpp"
#include "sync_replica_stream_connector.hpp"

#include <chrono>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

// Compact product-visible cutpoint for one configured folder. Catalog content,
// authenticated scan continuation, and replica values are observed in
// sequence, not as one cross-database atomic snapshot. This is deliberate:
// sync-once owns a bounded process composition, while each SQLite owner remains
// the authority for its own durable image. Scan continuation is included
// because it can make real crash-surviving progress without changing a catalog
// entry or replica operation. The remote-apply cursor is included for the
// same reason: advancing it or extending/resetting its cutpoint-bound inspection
// sweep is durable fairness/settlement progress even when every selected
// idempotent apply resolves to an exact no-op.
struct SyncReplicaSyncOnceCutpoint final {
    std::uint64_t catalog_generation = 0U;
    std::uint64_t catalog_entries = 0U;
    std::string catalog_digest;
    std::uint64_t local_scan_epoch = 0U;
    std::uint64_t local_scan_seen_path_count = 0U;
    std::uint64_t local_scan_seen_path_bytes = 0U;
    std::string local_scan_resume_after_path;
    std::string local_scan_seen_chain_digest;
    std::string remote_apply_resume_after_path;
    std::string remote_inspection_sweep_basis_digest;
    std::string remote_inspection_sweep_started_after_path;
    std::uint64_t remote_inspection_sweep_seen_path_count = 0U;
    bool remote_inspection_sweep_had_unresolved_paths = false;
    std::uint64_t replica_generation = 0U;
    std::string replica_cutpoint_digest;
    std::string replica_evidence_set_digest;
    std::string replica_visible_state_digest;

    bool operator==(const SyncReplicaSyncOnceCutpoint&) const = default;
};

struct SyncReplicaSyncOnceOptions final {
    SyncReplicaFolderConvergencePassLimits folder_limits;
    std::uint64_t max_round_trips =
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips;
    std::uint64_t max_source_resets =
        kSyncReplicaReconciliationTlsDefaultMaxSourceResets;
    std::uint64_t stage_timeout_seconds = 10U;
    std::uint64_t maximum_runtime_seconds = 60U;
    std::chrono::steady_clock::time_point command_started_at =
        std::chrono::steady_clock::now();

    bool operator==(const SyncReplicaSyncOnceOptions&) const = default;
};

enum class SyncReplicaSyncOnceDisposition : std::uint8_t {
    CompleteNoOp = 1U,
    CompleteChanged = 2U,
    CompleteWithUnresolvedPaths = 3U,
    CommandDeadlineReachedBeforeLocalPass = 4U,
    CommandDeadlineReachedBeforePull = 5U,
    CommandDeadlineReachedBeforeRemoteApply = 6U,
    ConnectDeadlineExpired = 7U,
    ConnectFailed = 8U,
    RouteDeadlineExpired = 9U,
    RouteRejected = 10U,
    HandshakeDeadlineExpired = 11U,
    HandshakeRejected = 12U,
    PeerUnauthorized = 13U,
    ReconciliationRoundTripLimitReached = 14U,
    ReconciliationSourceChangedLimitReached = 15U,
    ReconciliationSourcePayloadUnavailable = 16U,
    ReconciliationReceiverCapacityBlocked = 17U,
    ReconciliationRequestDeadlineExpired = 18U,
    ReconciliationResponseDeadlineExpired = 19U,
    ReconciliationPeerClosed = 20U,
    ReconciliationSourcePayloadPreparing = 21U,
};

[[nodiscard]] std::string_view sync_replica_sync_once_disposition_name(
    SyncReplicaSyncOnceDisposition disposition) noexcept;
[[nodiscard]] bool sync_replica_sync_once_is_complete(
    SyncReplicaSyncOnceDisposition disposition) noexcept;
[[nodiscard]] bool sync_replica_sync_once_is_settled(
    SyncReplicaSyncOnceDisposition disposition) noexcept;
[[nodiscard]] bool sync_replica_sync_once_is_bounded_progress(
    SyncReplicaSyncOnceDisposition disposition) noexcept;

struct SyncReplicaSyncOnceResult final {
    SyncReplicaSyncOnceDisposition disposition =
        SyncReplicaSyncOnceDisposition::CommandDeadlineReachedBeforeLocalPass;
    SyncReplicaSyncOnceCutpoint before;
    SyncReplicaSyncOnceCutpoint after_local_pass;
    SyncReplicaSyncOnceCutpoint after_pull;
    SyncReplicaSyncOnceCutpoint after;
    std::optional<SyncReplicaFolderConvergencePassReport> local_pass;
    std::optional<SyncReplicaReconciliationTlsClientResult> reconciliation;
    std::optional<SyncReplicaFolderConvergencePassReport> remote_apply_pass;
    bool pull_attempted = false;
    bool remote_apply_attempted = false;
    bool command_deadline_reached_after_completion = false;

    bool operator==(const SyncReplicaSyncOnceResult&) const = default;
};

[[nodiscard]] bool sync_replica_sync_once_made_durable_progress(
    const SyncReplicaSyncOnceResult& result) noexcept;

// True only when one final convergence report settles the exact cutpoint
// observed after that pass. The folder owner must have completed both bounded
// scheduling domains, established its writer-serialized terminal
// catalog/visible-projection fence, and left no authenticated scan or remote
// inspection continuation at the reported cutpoint. Its published remote
// fairness cursor must also equal the final durable cursor, so scheduling-only
// movement cannot be mistaken for the same terminal observation. This public
// pure predicate keeps process-level settlement classification independently
// testable.
[[nodiscard]] bool sync_replica_sync_once_final_pass_settles_cutpoint(
    const SyncReplicaFolderConvergencePassReport& pass,
    const SyncReplicaSyncOnceCutpoint& cutpoint) noexcept;

void validate_sync_replica_sync_once_options_or_throw(
    const SyncReplicaSyncOnceOptions& options,
    std::string_view label = "sync replica sync-once options");

// Borrowing cycle owner for higher-level product composition. The configured
// folder process remains the sole replica/catalog/payload owner; this class
// retains only the client TLS context, route connector, expected peer, and
// reconciliation service that operate on that exact folder lifetime. Calls are
// synchronous and must remain on the folder owner's construction thread. It
// owns no sleep, retry, listener, discovery, or daemon lifetime.
class SyncReplicaSyncCycleOwner final {
public:
    SyncReplicaSyncCycleOwner(
        SyncReplicaFolderProcessOwner& folder_process,
        SyncReplicaFileTlsClientContext client_context,
        SyncReplicaStreamRoute route,
        SyncReplicaTlsPeerPolicy expected_peer,
        std::string label = "sync replica sync-cycle owner");
    ~SyncReplicaSyncCycleOwner() noexcept;

    SyncReplicaSyncCycleOwner(const SyncReplicaSyncCycleOwner&) = delete;
    SyncReplicaSyncCycleOwner& operator=(
        const SyncReplicaSyncCycleOwner&) = delete;
    SyncReplicaSyncCycleOwner(SyncReplicaSyncCycleOwner&&) = delete;
    SyncReplicaSyncCycleOwner& operator=(
        SyncReplicaSyncCycleOwner&&) = delete;

    [[nodiscard]] const SyncReplicaDeploymentManifest& deployment()
        const noexcept;
    [[nodiscard]] const SyncReplicaTlsPeerPolicy& expected_peer()
        const noexcept;
    [[nodiscard]] const SyncReplicaStreamRoute& route() const noexcept;
    [[nodiscard]] SyncReplicaStreamRouteKind route_kind() const noexcept;

    [[nodiscard]] SyncReplicaSyncOnceResult run_once_or_throw(
        SyncReplicaSyncOnceOptions options = {});

private:
    struct State;
    std::unique_ptr<State> state_;
};

// Owning convenience wrapper used by the one-shot CLI. It creates one existing-
// only configured folder process and delegates the exact operation to the
// borrowing cycle owner above. The split prevents a long-running peer service
// from opening a second replica database merely to reuse sync-once semantics.
class SyncReplicaSyncOnceOwner final {
public:
    SyncReplicaSyncOnceOwner(
        SyncReplicaDeploymentManifest deployment,
        SyncReplicaFileTlsClientContext client_context,
        SyncReplicaStreamRoute route,
        SyncReplicaTlsPeerPolicy expected_peer,
        std::string label = "sync replica sync-once owner");
    ~SyncReplicaSyncOnceOwner() noexcept;

    SyncReplicaSyncOnceOwner(const SyncReplicaSyncOnceOwner&) = delete;
    SyncReplicaSyncOnceOwner& operator=(
        const SyncReplicaSyncOnceOwner&) = delete;
    SyncReplicaSyncOnceOwner(SyncReplicaSyncOnceOwner&&) = delete;
    SyncReplicaSyncOnceOwner& operator=(SyncReplicaSyncOnceOwner&&) = delete;

    [[nodiscard]] const SyncReplicaDeploymentManifest& deployment()
        const noexcept;
    [[nodiscard]] const SyncReplicaTlsPeerPolicy& expected_peer()
        const noexcept;
    [[nodiscard]] const SyncReplicaStreamRoute& route() const noexcept;
    [[nodiscard]] SyncReplicaStreamRouteKind route_kind() const noexcept;

    [[nodiscard]] SyncReplicaSyncOnceResult run_once_or_throw(
        SyncReplicaSyncOnceOptions options = {});

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
