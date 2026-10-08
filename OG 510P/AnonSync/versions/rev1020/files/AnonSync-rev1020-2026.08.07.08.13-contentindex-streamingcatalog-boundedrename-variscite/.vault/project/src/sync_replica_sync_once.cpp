#include "sync_replica_sync_once.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_reconciliation_protocol.hpp"

#include <chrono>
#include <stdexcept>
#include <utility>

namespace anonsync {
namespace {

[[nodiscard]] SyncReplicaSyncOnceCutpoint observe_cutpoint_or_throw(
    SyncReplicaFolderProcessOwner& folder_process) {
    const SyncReplicaFolderCatalogSnapshot catalog =
        folder_process.catalog_snapshot_or_throw();
    const SyncReplicaFolderScanProgressSnapshot scan_progress =
        folder_process.scan_progress_snapshot_or_throw();
    const SyncReplicaSqliteSnapshot replica =
        folder_process.replica_snapshot_or_throw();
    return {
        .catalog_generation = catalog.state_generation,
        .catalog_entries =
            static_cast<std::uint64_t>(catalog.entries.size()),
        .catalog_digest = catalog.catalog_digest,
        .local_scan_epoch = scan_progress.scan_epoch,
        .local_scan_seen_path_count = scan_progress.seen_path_count,
        .local_scan_seen_path_bytes = scan_progress.seen_path_bytes,
        .local_scan_resume_after_path = scan_progress.resume_after_path,
        .local_scan_seen_chain_digest = scan_progress.seen_chain_digest,
        .remote_apply_resume_after_path =
            scan_progress.remote_apply_resume_after_path,
        .remote_inspection_sweep_basis_digest =
            scan_progress.remote_inspection_sweep_basis_digest,
        .remote_inspection_sweep_started_after_path =
            scan_progress.remote_inspection_sweep_started_after_path,
        .remote_inspection_sweep_seen_path_count =
            scan_progress.remote_inspection_sweep_seen_path_count,
        .remote_inspection_sweep_had_unresolved_paths =
            scan_progress.remote_inspection_sweep_had_unresolved_paths,
        .replica_generation = replica.state_generation,
        .replica_cutpoint_digest = replica.cutpoint_digest,
        .replica_evidence_set_digest = replica.evidence_set_digest,
        .replica_visible_state_digest = replica.visible_state_digest,
    };
}

[[nodiscard]] bool pass_observed_unresolved_paths(
    const std::optional<SyncReplicaFolderConvergencePassReport>& pass) {
    return pass.has_value() &&
        (pass->skipped_conflicted_remote_path_count != 0U ||
         pass->skipped_tombstone_remote_path_count != 0U);
}

[[nodiscard]] bool final_pass_does_not_settle_cutpoint(
    const std::optional<SyncReplicaFolderConvergencePassReport>& pass,
    const SyncReplicaSyncOnceCutpoint& cutpoint) {
    // classify_complete is reached only after the post-pull folder pass, but
    // keep settlement fail-closed rather than silently accepting an older
    // terminal observation. Earlier-pass scheduling remainder is deliberately
    // not consulted: the final pass may have advanced and completed that exact
    // durable scan/apply suffix during the same sync-once cycle.
    return !pass.has_value() ||
        !sync_replica_sync_once_final_pass_settles_cutpoint(
            *pass, cutpoint);
}

[[nodiscard]] SyncReplicaSyncOnceDisposition classify_complete(
    const SyncReplicaSyncOnceResult& result) {
    if (pass_observed_unresolved_paths(result.local_pass) ||
        pass_observed_unresolved_paths(result.remote_apply_pass) ||
        final_pass_does_not_settle_cutpoint(
            result.remote_apply_pass, result.after)) {
        return SyncReplicaSyncOnceDisposition::CompleteWithUnresolvedPaths;
    }
    return result.before == result.after
        ? SyncReplicaSyncOnceDisposition::CompleteNoOp
        : SyncReplicaSyncOnceDisposition::CompleteChanged;
}

[[nodiscard]] SyncReplicaSyncOnceDisposition map_client_disposition(
    SyncReplicaReconciliationTlsClientDisposition disposition) {
    switch (disposition) {
        case SyncReplicaReconciliationTlsClientDisposition::
                ConnectDeadlineExpired:
            return SyncReplicaSyncOnceDisposition::ConnectDeadlineExpired;
        case SyncReplicaReconciliationTlsClientDisposition::ConnectFailed:
            return SyncReplicaSyncOnceDisposition::ConnectFailed;
        case SyncReplicaReconciliationTlsClientDisposition::
                RouteDeadlineExpired:
            return SyncReplicaSyncOnceDisposition::RouteDeadlineExpired;
        case SyncReplicaReconciliationTlsClientDisposition::RouteRejected:
            return SyncReplicaSyncOnceDisposition::RouteRejected;
        case SyncReplicaReconciliationTlsClientDisposition::
                HandshakeDeadlineExpired:
            return SyncReplicaSyncOnceDisposition::HandshakeDeadlineExpired;
        case SyncReplicaReconciliationTlsClientDisposition::HandshakeRejected:
            return SyncReplicaSyncOnceDisposition::HandshakeRejected;
        case SyncReplicaReconciliationTlsClientDisposition::PeerUnauthorized:
            return SyncReplicaSyncOnceDisposition::PeerUnauthorized;
        case SyncReplicaReconciliationTlsClientDisposition::PullCompleted:
            break;
    }
    throw std::logic_error(
        "sync replica sync-once client completed without pull classification");
}

[[nodiscard]] SyncReplicaSyncOnceDisposition map_pull_disposition(
    SyncReplicaReconciliationTlsPullDisposition disposition) {
    switch (disposition) {
        case SyncReplicaReconciliationTlsPullDisposition::Complete:
            break;
        case SyncReplicaReconciliationTlsPullDisposition::
                RoundTripLimitReached:
            return SyncReplicaSyncOnceDisposition::
                ReconciliationRoundTripLimitReached;
        case SyncReplicaReconciliationTlsPullDisposition::
                SourceChangedLimitReached:
            return SyncReplicaSyncOnceDisposition::
                ReconciliationSourceChangedLimitReached;
        case SyncReplicaReconciliationTlsPullDisposition::
                SourcePayloadUnavailable:
            return SyncReplicaSyncOnceDisposition::
                ReconciliationSourcePayloadUnavailable;
        case SyncReplicaReconciliationTlsPullDisposition::
                SourcePayloadPreparing:
            return SyncReplicaSyncOnceDisposition::
                ReconciliationSourcePayloadPreparing;
        case SyncReplicaReconciliationTlsPullDisposition::
                ReceiverCapacityBlocked:
            return SyncReplicaSyncOnceDisposition::
                ReconciliationReceiverCapacityBlocked;
        case SyncReplicaReconciliationTlsPullDisposition::
                RequestDeadlineExpired:
            return SyncReplicaSyncOnceDisposition::
                ReconciliationRequestDeadlineExpired;
        case SyncReplicaReconciliationTlsPullDisposition::
                ResponseDeadlineExpired:
            return SyncReplicaSyncOnceDisposition::
                ReconciliationResponseDeadlineExpired;
        case SyncReplicaReconciliationTlsPullDisposition::PeerClosed:
            return SyncReplicaSyncOnceDisposition::ReconciliationPeerClosed;
    }
    throw std::logic_error(
        "sync replica sync-once complete pull requires final classification");
}

[[nodiscard]] SyncReplicaReconciliationProtocolLimits protocol_limits(
    std::uint64_t maximum_payload_bytes) {
    SyncReplicaReconciliationProtocolLimits limits;
    limits.max_single_payload_bytes =
        sync_replica_reconciliation_single_payload_limit(
            maximum_payload_bytes);
    limits.max_payload_bytes_per_page =
        kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage;
    limits.max_payload_extent_bytes = maximum_payload_bytes;
    validate_sync_replica_reconciliation_protocol_limits_or_throw(limits);
    return limits;
}

}  // namespace

std::string_view sync_replica_sync_once_disposition_name(
    SyncReplicaSyncOnceDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaSyncOnceDisposition::CompleteNoOp:
            return "complete_no_op";
        case SyncReplicaSyncOnceDisposition::CompleteChanged:
            return "complete_changed";
        case SyncReplicaSyncOnceDisposition::CompleteWithUnresolvedPaths:
            return "complete_with_unresolved_paths";
        case SyncReplicaSyncOnceDisposition::
                CommandDeadlineReachedBeforeLocalPass:
            return "command_deadline_before_local_pass";
        case SyncReplicaSyncOnceDisposition::CommandDeadlineReachedBeforePull:
            return "command_deadline_before_pull";
        case SyncReplicaSyncOnceDisposition::
                CommandDeadlineReachedBeforeRemoteApply:
            return "command_deadline_before_remote_apply";
        case SyncReplicaSyncOnceDisposition::ConnectDeadlineExpired:
            return "connect_deadline_expired";
        case SyncReplicaSyncOnceDisposition::ConnectFailed:
            return "connect_failed";
        case SyncReplicaSyncOnceDisposition::RouteDeadlineExpired:
            return "route_deadline_expired";
        case SyncReplicaSyncOnceDisposition::RouteRejected:
            return "route_rejected";
        case SyncReplicaSyncOnceDisposition::HandshakeDeadlineExpired:
            return "handshake_deadline_expired";
        case SyncReplicaSyncOnceDisposition::HandshakeRejected:
            return "handshake_rejected";
        case SyncReplicaSyncOnceDisposition::PeerUnauthorized:
            return "peer_unauthorized";
        case SyncReplicaSyncOnceDisposition::
                ReconciliationRoundTripLimitReached:
            return "reconciliation_round_trip_limit_reached";
        case SyncReplicaSyncOnceDisposition::
                ReconciliationSourceChangedLimitReached:
            return "reconciliation_source_changed_limit_reached";
        case SyncReplicaSyncOnceDisposition::
                ReconciliationSourcePayloadUnavailable:
            return "reconciliation_source_payload_unavailable";
        case SyncReplicaSyncOnceDisposition::
                ReconciliationSourcePayloadPreparing:
            return "reconciliation_source_payload_preparing";
        case SyncReplicaSyncOnceDisposition::
                ReconciliationReceiverCapacityBlocked:
            return "reconciliation_receiver_capacity_blocked";
        case SyncReplicaSyncOnceDisposition::
                ReconciliationRequestDeadlineExpired:
            return "reconciliation_request_deadline_expired";
        case SyncReplicaSyncOnceDisposition::
                ReconciliationResponseDeadlineExpired:
            return "reconciliation_response_deadline_expired";
        case SyncReplicaSyncOnceDisposition::ReconciliationPeerClosed:
            return "reconciliation_peer_closed";
    }
    return "unknown";
}

bool sync_replica_sync_once_is_complete(
    SyncReplicaSyncOnceDisposition disposition) noexcept {
    return disposition == SyncReplicaSyncOnceDisposition::CompleteNoOp ||
        disposition == SyncReplicaSyncOnceDisposition::CompleteChanged ||
        disposition == SyncReplicaSyncOnceDisposition::CompleteWithUnresolvedPaths;
}

bool sync_replica_sync_once_is_settled(
    SyncReplicaSyncOnceDisposition disposition) noexcept {
    return disposition == SyncReplicaSyncOnceDisposition::CompleteNoOp ||
        disposition == SyncReplicaSyncOnceDisposition::CompleteChanged;
}

bool sync_replica_sync_once_is_bounded_progress(
    SyncReplicaSyncOnceDisposition disposition) noexcept {
    return sync_replica_sync_once_is_complete(disposition) ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationRoundTripLimitReached ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationSourceChangedLimitReached ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationSourcePayloadUnavailable ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationSourcePayloadPreparing ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationReceiverCapacityBlocked ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationRequestDeadlineExpired ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationResponseDeadlineExpired ||
        disposition == SyncReplicaSyncOnceDisposition::
            ReconciliationPeerClosed ||
        disposition == SyncReplicaSyncOnceDisposition::
            CommandDeadlineReachedBeforePull ||
        disposition == SyncReplicaSyncOnceDisposition::
            CommandDeadlineReachedBeforeRemoteApply;
}

bool sync_replica_sync_once_made_durable_progress(
    const SyncReplicaSyncOnceResult& result) noexcept {
    return result.before != result.after;
}

bool sync_replica_sync_once_final_pass_settles_cutpoint(
    const SyncReplicaFolderConvergencePassReport& pass,
    const SyncReplicaSyncOnceCutpoint& cutpoint) noexcept {
    return pass.completed_local_scan_epoch &&
        pass.deferred_remote_payload_candidate_count == 0U &&
        pass.deferred_remote_apply_candidate_count == 0U &&
        pass.deferred_unadjudicated_local_absence_remote_file_count == 0U &&
        pass.completed_remote_inspection_sweep &&
        pass.deferred_remote_inspection_path_count == 0U &&
        !pass.remote_inspection_sweep_had_unresolved_paths &&
        pass.remote_apply_stop_reason ==
            SyncReplicaFolderRemoteApplyStopReason::EndOfProjection &&
        pass.remote_inspection_terminal_cutpoint_reproved &&
        pass.remote_inspection_terminal_catalog_digest ==
            cutpoint.catalog_digest &&
        pass.remote_inspection_terminal_visible_state_digest ==
            cutpoint.replica_visible_state_digest &&
        pass.remote_apply_resume_after_path ==
            cutpoint.remote_apply_resume_after_path &&
        cutpoint.local_scan_seen_path_count == 0U &&
        cutpoint.local_scan_seen_path_bytes == 0U &&
        cutpoint.local_scan_resume_after_path.empty() &&
        cutpoint.remote_inspection_sweep_basis_digest.empty() &&
        cutpoint.remote_inspection_sweep_started_after_path.empty() &&
        cutpoint.remote_inspection_sweep_seen_path_count == 0U &&
        !cutpoint.remote_inspection_sweep_had_unresolved_paths;
}

void validate_sync_replica_sync_once_options_or_throw(
    const SyncReplicaSyncOnceOptions& options,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica sync-once options label must not be empty");
    }
    validate_sync_replica_session_supervisor_limits_or_throw(
        {1U, options.stage_timeout_seconds,
         options.maximum_runtime_seconds},
        std::string(label) + " session limits");
    if (options.max_round_trips == 0U ||
        options.max_round_trips >
            kSyncReplicaReconciliationTlsMaximumRoundTrips) {
        throw std::invalid_argument(
            std::string(label) + " max_round_trips must be in [1, 4096]");
    }
    if (options.max_source_resets >
        kSyncReplicaReconciliationTlsMaximumRoundTrips) {
        throw std::invalid_argument(
            std::string(label) + " max_source_resets must be in [0, 4096]");
    }
}

struct SyncReplicaSyncCycleOwner::State final {
    SyncReplicaFolderProcessOwner* folder_process = nullptr;
    SyncReplicaFileTlsClientContext client_context;
    SyncReplicaStreamConnector connector;
    SyncReplicaTlsPeerPolicy expected_peer;
    std::unique_ptr<SyncReplicaReconciliationService> reconciliation_service;
    std::string label;

    State(
        SyncReplicaFolderProcessOwner& process,
        SyncReplicaFileTlsClientContext context,
        SyncReplicaStreamRoute route,
        SyncReplicaTlsPeerPolicy peer,
        std::string owner_label)
        : folder_process(&process),
          client_context(std::move(context)),
          connector(std::move(route), owner_label + " route connector"),
          expected_peer(std::move(peer)),
          label(std::move(owner_label)) {
        reconciliation_service =
            std::make_unique<SyncReplicaReconciliationService>(
                folder_process->replica_owner_or_throw(),
                folder_process->payload_store_or_throw(),
                protocol_limits(
                    folder_process->deployment().max_payload_bytes),
                label + " reconciliation service",
                folder_process->folder_owner_or_throw()
                    .selective_sync_policy_snapshot_or_throw());
    }
};

SyncReplicaSyncCycleOwner::SyncReplicaSyncCycleOwner(
    SyncReplicaFolderProcessOwner& folder_process,
    SyncReplicaFileTlsClientContext client_context,
    SyncReplicaStreamRoute route,
    SyncReplicaTlsPeerPolicy expected_peer,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica sync-cycle owner label must not be empty");
    }
    if (!client_context.active()) {
        throw std::invalid_argument(
            label + " TLS client context is inactive");
    }
    validate_sync_replica_stream_route_or_throw(route, label + " route");
    if (!sync_id_is_valid(expected_peer.actor.device_id) ||
        expected_peer.actor.epoch == 0U) {
        throw std::invalid_argument(
            label + " expected peer actor identity is invalid");
    }
    if (!is_lowercase_sha256_hex(expected_peer.spki_sha256)) {
        throw std::invalid_argument(
            label + " expected peer SPKI must be lowercase SHA-256");
    }
    if (folder_process.deployment().local_actor == expected_peer.actor) {
        throw std::invalid_argument(
            label + " expected peer must differ from the local actor");
    }
    state_ = std::make_unique<State>(
        folder_process, std::move(client_context), std::move(route),
        std::move(expected_peer), std::move(label));
}

SyncReplicaSyncCycleOwner::~SyncReplicaSyncCycleOwner() noexcept = default;

const SyncReplicaDeploymentManifest&
SyncReplicaSyncCycleOwner::deployment() const noexcept {
    return state_->folder_process->deployment();
}

const SyncReplicaTlsPeerPolicy&
SyncReplicaSyncCycleOwner::expected_peer() const noexcept {
    return state_->expected_peer;
}

const SyncReplicaStreamRoute& SyncReplicaSyncCycleOwner::route() const noexcept {
    return state_->connector.route();
}

SyncReplicaStreamRouteKind SyncReplicaSyncCycleOwner::route_kind()
    const noexcept {
    return state_->connector.route_kind();
}

SyncReplicaSyncOnceResult SyncReplicaSyncCycleOwner::run_once_or_throw(
    SyncReplicaSyncOnceOptions options) {
    validate_sync_replica_sync_once_options_or_throw(
        options, state_->label + " run");
    SyncReplicaSessionSupervisor supervisor(
        {1U, options.stage_timeout_seconds,
         options.maximum_runtime_seconds},
        options.command_started_at, state_->label + " supervisor");

    SyncReplicaFolderProcessOwner& folder_process = *state_->folder_process;
    SyncReplicaSyncOnceResult result;
    result.before = observe_cutpoint_or_throw(folder_process);
    result.after_local_pass = result.before;
    result.after_pull = result.before;
    result.after = result.before;

    if (supervisor.command_deadline_reached_at(
            std::chrono::steady_clock::now())) {
        result.disposition = SyncReplicaSyncOnceDisposition::
            CommandDeadlineReachedBeforeLocalPass;
        return result;
    }

    result.local_pass.emplace(
        folder_process.run_convergence_pass_or_throw(options.folder_limits));
    result.after_local_pass = observe_cutpoint_or_throw(folder_process);
    result.after_pull = result.after_local_pass;
    result.after = result.after_local_pass;

    const SyncReplicaSessionAuthorization authorization =
        supervisor.authorize_next_or_throw();
    if (authorization.disposition ==
            SyncReplicaSessionAuthorizationDisposition::
                CommandDeadlineReached) {
        result.disposition = SyncReplicaSyncOnceDisposition::
            CommandDeadlineReachedBeforePull;
        return result;
    }
    if (authorization.disposition !=
            SyncReplicaSessionAuthorizationDisposition::Authorized ||
        !authorization.plan.has_value()) {
        throw std::logic_error(
            state_->label +
            " one-shot supervisor did not authorize its only session");
    }

    const SyncReplicaFileTlsClientDeadlines staged =
        authorization.plan->client_deadlines();
    const SyncReplicaReconciliationTlsClientDeadlines deadlines{
        staged.connect,
        staged.handshake,
        staged.receipt,
        staged.shutdown,
    };
    SyncReplicaReconciliationTlsPullOptions pull_options;
    pull_options.max_round_trips = options.max_round_trips;
    pull_options.max_source_resets = options.max_source_resets;

    result.pull_attempted = true;
    result.reconciliation.emplace(
        pull_sync_replica_reconciliation_tls_session_or_throw(
            *state_->reconciliation_service,
            state_->client_context.retain_another_or_throw(
                state_->label + " retained client context"),
            state_->connector, state_->expected_peer,
            std::move(pull_options), deadlines,
            state_->label + " reconciliation session"));
    result.after_pull = observe_cutpoint_or_throw(folder_process);
    result.after = result.after_pull;

    if (result.reconciliation->disposition !=
        SyncReplicaReconciliationTlsClientDisposition::PullCompleted) {
        result.disposition = map_client_disposition(
            result.reconciliation->disposition);
        return result;
    }
    if (!result.reconciliation->pull.has_value()) {
        throw std::logic_error(
            state_->label + " completed reconciliation lacks pull result");
    }

    const SyncReplicaReconciliationTlsPullDisposition pull_disposition =
        result.reconciliation->pull->disposition;
    const bool pull_complete = pull_disposition ==
        SyncReplicaReconciliationTlsPullDisposition::Complete;
    const SyncReplicaSyncOnceDisposition partial_disposition = pull_complete
        ? SyncReplicaSyncOnceDisposition::CompleteNoOp
        : map_pull_disposition(pull_disposition);

    if (supervisor.command_deadline_reached_at(
            std::chrono::steady_clock::now())) {
        result.disposition = pull_complete
            ? SyncReplicaSyncOnceDisposition::
                CommandDeadlineReachedBeforeRemoteApply
            : partial_disposition;
        return result;
    }

    result.remote_apply_attempted = true;
    result.remote_apply_pass.emplace(
        folder_process.run_convergence_pass_or_throw(options.folder_limits));
    result.after = observe_cutpoint_or_throw(folder_process);
    result.command_deadline_reached_after_completion =
        supervisor.command_deadline_reached_at(
            std::chrono::steady_clock::now());

    result.disposition = pull_complete
        ? classify_complete(result)
        : partial_disposition;
    return result;
}

struct SyncReplicaSyncOnceOwner::State final {
    SyncReplicaFolderProcessOwner folder_process;
    SyncReplicaSyncCycleOwner cycle;

    State(
        SyncReplicaDeploymentManifest deployment,
        SyncReplicaFileTlsClientContext client_context,
        SyncReplicaStreamRoute route,
        SyncReplicaTlsPeerPolicy expected_peer,
        std::string label)
        : folder_process(
              std::move(deployment), label + " folder process"),
          cycle(
              folder_process, std::move(client_context), std::move(route),
              std::move(expected_peer), label + " cycle") {}
};

SyncReplicaSyncOnceOwner::SyncReplicaSyncOnceOwner(
    SyncReplicaDeploymentManifest deployment,
    SyncReplicaFileTlsClientContext client_context,
    SyncReplicaStreamRoute route,
    SyncReplicaTlsPeerPolicy expected_peer,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica sync-once owner label must not be empty");
    }
    state_ = std::make_unique<State>(
        std::move(deployment), std::move(client_context), std::move(route),
        std::move(expected_peer), std::move(label));
}

SyncReplicaSyncOnceOwner::~SyncReplicaSyncOnceOwner() noexcept = default;

const SyncReplicaDeploymentManifest&
SyncReplicaSyncOnceOwner::deployment() const noexcept {
    return state_->cycle.deployment();
}

const SyncReplicaTlsPeerPolicy&
SyncReplicaSyncOnceOwner::expected_peer() const noexcept {
    return state_->cycle.expected_peer();
}

const SyncReplicaStreamRoute& SyncReplicaSyncOnceOwner::route() const noexcept {
    return state_->cycle.route();
}

SyncReplicaStreamRouteKind SyncReplicaSyncOnceOwner::route_kind()
    const noexcept {
    return state_->cycle.route_kind();
}

SyncReplicaSyncOnceResult SyncReplicaSyncOnceOwner::run_once_or_throw(
    SyncReplicaSyncOnceOptions options) {
    return state_->cycle.run_once_or_throw(std::move(options));
}

}  // namespace anonsync

#endif
