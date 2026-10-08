#include "sync_replica_peer_service.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_replica_historical_version_inventory_json.hpp"
#include "sync_replica_i2p_ingress_worker.hpp"
#include "sync_replica_peer_service_integrity_evidence.hpp"
#include "sync_replica_reconciliation_tls_exchange.hpp"
#include "sync_replica_session_supervisor.hpp"

#include <algorithm>
#include <chrono>
#include <memory>
#include <limits>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace anonsync {
namespace {

using Clock = std::chrono::steady_clock;
using Milliseconds = std::chrono::milliseconds;

[[nodiscard]] Clock::time_point add_milliseconds_or_throw(
    Clock::time_point base,
    std::uint64_t amount,
    const std::string& label) {
    if (amount > static_cast<std::uint64_t>(
                     std::numeric_limits<Milliseconds::rep>::max())) {
        throw std::overflow_error(label + " duration overflows");
    }
    const Milliseconds duration(
        static_cast<Milliseconds::rep>(amount));
    if (duration.count() > 0 &&
        base > Clock::time_point::max() - duration) {
        throw std::overflow_error(label + " deadline overflows");
    }
    return base + duration;
}

[[nodiscard]] std::uint64_t retry_delay_milliseconds(
    const SyncReplicaPeerServiceLimits& limits,
    std::uint64_t consecutive_failures) noexcept {
    if (consecutive_failures == 0U) return 0U;
    std::uint64_t value = limits.retry_initial_milliseconds;
    for (std::uint64_t index = 1U;
         index < consecutive_failures &&
         value < limits.retry_maximum_milliseconds;
         ++index) {
        if (value > limits.retry_maximum_milliseconds / 2U) {
            value = limits.retry_maximum_milliseconds;
        } else {
            value *= 2U;
        }
    }
    return std::min(value, limits.retry_maximum_milliseconds);
}

[[nodiscard]] SyncReplicaI2pSamAcceptRoute i2p_accept_route_or_throw(
    const SyncReplicaPeerIngress& ingress,
    const std::string& label) {
    const auto* const selected =
        std::get_if<SyncReplicaI2pSamIngress>(&ingress);
    if (selected == nullptr) {
        throw std::logic_error(label + " is not an I2P SAM ingress");
    }
    SyncReplicaI2pSamAcceptRoute route{
        .bridge = selected->bridge,
        .session_id = selected->session_id,
        .session_destination = selected->session_destination,
        .inbound_quantity = selected->inbound_quantity,
        .outbound_quantity = selected->outbound_quantity};
    validate_sync_replica_i2p_sam_accept_route_or_throw(
        route, label + " accept route");
    return route;
}

[[nodiscard]] std::uint64_t remaining_milliseconds(
    Clock::time_point now,
    Clock::time_point deadline) noexcept {
    if (deadline <= now) return 0U;
    const auto exact = std::chrono::duration_cast<Milliseconds>(
        deadline - now);
    if (exact.count() <= 0) return 1U;
    return static_cast<std::uint64_t>(exact.count());
}

void increment_saturating(std::uint64_t& value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) ++value;
}

void add_saturating(
    std::uint64_t& value,
    std::uint64_t amount) noexcept {
    if (amount > std::numeric_limits<std::uint64_t>::max() - value) {
        value = std::numeric_limits<std::uint64_t>::max();
    } else {
        value += amount;
    }
}

[[nodiscard]] std::uint64_t elapsed_milliseconds(
    Clock::time_point now,
    Clock::time_point observed_at) noexcept {
    if (now <= observed_at) return 0U;
    const auto exact = std::chrono::duration_cast<Milliseconds>(
        now - observed_at);
    if (exact.count() <= 0) return 0U;
    return static_cast<std::uint64_t>(exact.count());
}

enum class PayloadAuthorityFailureContext : std::uint8_t {
    InitialRepair = 1U,
    IntegrityReproof = 2U,
    HealthyRepair = 3U,
    OutboundNetworkStep = 4U,
    InboundNetworkStep = 5U,
    OperatorRecheck = 6U,
    OperatorQuarantine = 7U,
    OperatorHistoricalVersion = 8U,
    TerminalVerification = 9U,
    SourceManifestProjection = 10U,
};

[[nodiscard]] bool network_outcome_is_unknown(
    PayloadAuthorityFailureContext context) noexcept {
    return context ==
               PayloadAuthorityFailureContext::OutboundNetworkStep ||
        context == PayloadAuthorityFailureContext::InboundNetworkStep;
}

[[nodiscard]] std::uint64_t successful_handoff_lease_milliseconds(
    const SyncReplicaPeerServiceLimits& limits) {
    if (limits.cycle_runtime_seconds >
        std::numeric_limits<std::uint64_t>::max() / 1000U) {
        throw std::overflow_error(
            "sync replica peer service cycle runtime overflows milliseconds");
    }
    // The peer may need its complete bounded scan/pull/apply horizon before it
    // can return the turn. An accept polling interval is merely responsiveness;
    // it must never become authority to reclaim a successfully handed-off turn.
    return std::max(
        limits.accept_window_milliseconds,
        limits.cycle_runtime_seconds * 1000U);
}

[[nodiscard]] bool exact_peer(
    const SyncReplicaTlsPeerPolicy& expected,
    const SyncReplicaPeerTlsServerResult& result) noexcept {
    return result.handshake_complete && result.peer_actor.has_value() &&
        result.peer_spki_sha256.has_value() &&
        *result.peer_actor == expected.actor &&
        *result.peer_spki_sha256 == expected.spki_sha256;
}

[[nodiscard]] bool inbound_handoff_complete(
    const SyncReplicaTlsPeerPolicy& expected,
    const SyncReplicaPeerTlsServerResult& result) noexcept {
    if (!exact_peer(expected, result) ||
        result.disposition !=
            SyncReplicaPeerTlsServerDisposition::ApplicationServed ||
        !result.application.has_value()) {
        return false;
    }
    const SyncReplicaPeerTlsServeResult& application = *result.application;
    if (application.disposition ==
            SyncReplicaPeerTlsServeDisposition::FileDelivery &&
        application.file_delivery.has_value()) {
        return application.file_delivery->disposition ==
            SyncReplicaFileTlsReceiveDisposition::ReceiptSent;
    }
    if (application.disposition ==
            SyncReplicaPeerTlsServeDisposition::Reconciliation &&
        application.reconciliation.has_value()) {
        return application.reconciliation->responses_written != 0U;
    }
    return false;
}

[[nodiscard]] bool outbound_handoff_complete(
    const SyncReplicaTlsPeerPolicy& expected,
    const SyncReplicaSyncOnceResult& result) noexcept {
    if (!result.reconciliation.has_value()) return false;
    const SyncReplicaReconciliationTlsClientResult& session =
        *result.reconciliation;
    return session.disposition ==
               SyncReplicaReconciliationTlsClientDisposition::PullCompleted &&
        session.peer_authenticated && session.peer_actor.has_value() &&
        session.peer_spki_sha256.has_value() &&
        *session.peer_actor == expected.actor &&
        *session.peer_spki_sha256 == expected.spki_sha256 &&
        session.pull.has_value() && session.pull->round_trips != 0U;
}

[[nodiscard]] SyncReplicaFileTlsServerDeadlines server_deadlines_or_throw(
    Clock::time_point started_at,
    Clock::time_point accept_deadline,
    std::uint64_t stage_timeout_seconds,
    const std::string& label) {
    // Reuse the canonical cumulative stage planner, then replace only the first
    // cutpoint with the shorter service accept window. Later stages retain the
    // full bounded session horizon from the step start.
    SyncReplicaSessionSupervisor supervisor(
        {1U, stage_timeout_seconds, std::nullopt}, started_at,
        label + " session deadline planner");
    const SyncReplicaSessionAuthorization authorization =
        supervisor.authorize_next_at_or_throw(started_at);
    if (authorization.disposition !=
            SyncReplicaSessionAuthorizationDisposition::Authorized ||
        !authorization.plan.has_value()) {
        throw std::logic_error(label + " could not authorize one session");
    }
    SyncReplicaFileTlsServerDeadlines deadlines =
        authorization.plan->server_deadlines();
    deadlines.accept = accept_deadline;
    return deadlines;
}

}  // namespace

std::string_view sync_replica_peer_ingress_kind_name(
    SyncReplicaPeerIngressKind kind) noexcept {
    switch (kind) {
        case SyncReplicaPeerIngressKind::DirectTcp:
            return "direct_tcp";
        case SyncReplicaPeerIngressKind::TorOnionService:
            return "tor_onion_service";
        case SyncReplicaPeerIngressKind::I2pSamAccept:
            return "i2p_sam_accept";
    }
    return "unknown";
}

SyncReplicaPeerIngressKind sync_replica_peer_ingress_kind(
    const SyncReplicaPeerIngress& ingress) noexcept {
    return std::visit(
        [](const auto& selected) noexcept {
            using Ingress = std::decay_t<decltype(selected)>;
            if constexpr (
                std::is_same_v<Ingress, SyncReplicaDirectTcpIngress>) {
                return SyncReplicaPeerIngressKind::DirectTcp;
            } else if constexpr (
                std::is_same_v<
                    Ingress, SyncReplicaTorOnionServiceIngress>) {
                return SyncReplicaPeerIngressKind::TorOnionService;
            } else {
                return SyncReplicaPeerIngressKind::I2pSamAccept;
            }
        },
        ingress);
}

void validate_sync_replica_peer_ingress_or_throw(
    const SyncReplicaPeerIngress& ingress,
    const SyncReplicaNumericStreamEndpoint& listen_endpoint,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica peer ingress label must not be empty");
    }
    std::visit(
        [&](const auto& selected) {
            using Ingress = std::decay_t<decltype(selected)>;
            if constexpr (
                std::is_same_v<Ingress, SyncReplicaDirectTcpIngress>) {
                // The numeric listener owner performs exact endpoint validation.
                (void)listen_endpoint;
            } else if constexpr (
                std::is_same_v<
                    Ingress, SyncReplicaTorOnionServiceIngress>) {
                if (!sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
                        listen_endpoint, label + " listener")) {
                    throw std::invalid_argument(
                        label +
                        " Tor onion forwarding requires a loopback listener");
                }
                if (selected.service_port == 0U) {
                    throw std::invalid_argument(
                        label + " Tor onion service port must be nonzero");
                }
                validate_sync_replica_tor_v3_onion_service_or_throw(
                    selected.onion_service, label + " Tor onion service");
            } else {
                // Native I2P ingress never binds or forwards through the numeric
                // endpoint. Schema v2 still carries that field for compatibility,
                // but it cannot become a second same-host application route.
                (void)listen_endpoint;
                (void)i2p_accept_route_or_throw(
                    ingress, label + " I2P SAM");
            }
        },
        ingress);
}

void validate_sync_replica_peer_service_limits_or_throw(
    const SyncReplicaPeerServiceLimits& limits,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica peer service limits label must not be empty");
    }
    SyncReplicaSyncOnceOptions cycle;
    cycle.folder_limits = limits.folder_limits;
    cycle.max_round_trips = limits.max_round_trips;
    cycle.max_source_resets = limits.max_source_resets;
    cycle.stage_timeout_seconds = limits.stage_timeout_seconds;
    cycle.maximum_runtime_seconds = limits.cycle_runtime_seconds;
    validate_sync_replica_sync_once_options_or_throw(
        cycle, label + " outbound cycle");
    if (limits.folder_limits.maximum_regular_files >
        kSyncReplicaFilePayloadStoreProductionMaxEntries) {
        throw std::invalid_argument(
            label +
            " folder maximum_regular_files exceeds the production durable capacity");
    }
    if (limits.folder_limits.maximum_remote_paths >
        kSyncReplicaFilePayloadStoreProductionMaxEntries) {
        throw std::invalid_argument(
            label +
            " folder maximum_remote_paths exceeds the production durable capacity");
    }
    if (limits.folder_limits.maximum_remote_inspection_paths >
        kSyncReplicaFilePayloadStoreProductionMaxEntries) {
        throw std::invalid_argument(
            label +
            " folder maximum_remote_inspection_paths exceeds the production durable capacity");
    }
    if (limits.inbound_stage_timeout_seconds == 0U ||
        limits.inbound_stage_timeout_seconds >
            kSyncReplicaSessionSupervisorMaximumStageTimeoutSeconds) {
        throw std::invalid_argument(
            label + " inbound_stage_timeout_seconds must be in [1, 3600]");
    }
    if (limits.inbound_max_round_trips == 0U ||
        limits.inbound_max_round_trips >
            kSyncReplicaReconciliationTlsMaximumRoundTrips) {
        throw std::invalid_argument(
            label + " inbound_max_round_trips must be in [1, 4096]");
    }
    if (limits.accept_window_milliseconds == 0U ||
        limits.accept_window_milliseconds >
            kSyncReplicaPeerServiceMaximumAcceptWindowMilliseconds) {
        throw std::invalid_argument(
            label + " accept_window_milliseconds must be in [1, 60000]");
    }
    if (limits.repair_interval_milliseconds == 0U ||
        limits.repair_interval_milliseconds >
            kSyncReplicaPeerServiceMaximumRepairIntervalMilliseconds) {
        throw std::invalid_argument(
            label + " repair_interval_milliseconds must be in [1, 3600000]");
    }
    if (limits.retry_initial_milliseconds == 0U ||
        limits.retry_initial_milliseconds >
            kSyncReplicaPeerServiceMaximumRetryDelayMilliseconds) {
        throw std::invalid_argument(
            label + " retry_initial_milliseconds must be in [1, 3600000]");
    }
    if (limits.retry_maximum_milliseconds == 0U ||
        limits.retry_maximum_milliseconds >
            kSyncReplicaPeerServiceMaximumRetryDelayMilliseconds ||
        limits.retry_maximum_milliseconds <
            limits.retry_initial_milliseconds) {
        throw std::invalid_argument(
            label + " retry_maximum_milliseconds must be in "
                    "[retry_initial_milliseconds, 3600000]");
    }
    if (limits.ingress_setup_timeout_seconds == 0U ||
        limits.ingress_setup_timeout_seconds >
            kSyncReplicaSessionSupervisorMaximumStageTimeoutSeconds) {
        throw std::invalid_argument(
            label + " ingress_setup_timeout_seconds must be in [1, 3600]");
    }
}

std::uint64_t
sync_replica_peer_service_network_step_horizon_seconds_or_throw(
    const SyncReplicaPeerServiceLimits& limits,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica peer service network horizon label is empty");
    }
    validate_sync_replica_peer_service_limits_or_throw(
        limits, label + " limits");
    if (limits.inbound_stage_timeout_seconds >
        std::numeric_limits<std::uint64_t>::max() /
            kSyncReplicaSessionSupervisorStageCount) {
        throw std::overflow_error(label + " inbound horizon overflows");
    }
    const std::uint64_t inbound_session_horizon =
        limits.inbound_stage_timeout_seconds *
        kSyncReplicaSessionSupervisorStageCount;
    const std::uint64_t accept_horizon =
        (limits.accept_window_milliseconds + 999U) / 1000U;
    return std::max(
        limits.cycle_runtime_seconds,
        std::max(
            inbound_session_horizon,
            std::max(
                accept_horizon,
                limits.ingress_setup_timeout_seconds)));
}

std::string_view sync_replica_peer_service_role_name(
    SyncReplicaPeerServiceRole role) noexcept {
    switch (role) {
        case SyncReplicaPeerServiceRole::OutboundPull:
            return "outbound_pull";
        case SyncReplicaPeerServiceRole::InboundServe:
            return "inbound_serve";
    }
    return "unknown";
}

std::string_view
sync_replica_peer_service_historical_version_action_name(
    SyncReplicaPeerServiceHistoricalVersionAction action) noexcept {
    switch (action) {
        case SyncReplicaPeerServiceHistoricalVersionAction::Inspect:
            return "inspect";
        case SyncReplicaPeerServiceHistoricalVersionAction::Restore:
            return "restore";
        case SyncReplicaPeerServiceHistoricalVersionAction::Pin:
            return "pin";
        case SyncReplicaPeerServiceHistoricalVersionAction::Unpin:
            return "unpin";
        case SyncReplicaPeerServiceHistoricalVersionAction::RetentionPlan:
            return "retention_plan";
    }
    return "unknown";
}

std::string_view
sync_replica_peer_service_historical_version_failure_class_name(
    SyncReplicaPeerServiceHistoricalVersionFailureClass failure_class)
    noexcept {
    switch (failure_class) {
        case SyncReplicaPeerServiceHistoricalVersionFailureClass::
                OperationFailed:
            return "operation_failed";
        case SyncReplicaPeerServiceHistoricalVersionFailureClass::
                SourceChanged:
            return "source_changed";
    }
    return "unknown";
}

std::string_view sync_replica_peer_service_step_disposition_name(
    SyncReplicaPeerServiceStepDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaPeerServiceStepDisposition::InitialRepairCompleted:
            return "initial_repair_completed";
        case SyncReplicaPeerServiceStepDisposition::PeriodicRepairCompleted:
            return "periodic_repair_completed";
        case SyncReplicaPeerServiceStepDisposition::OutboundCycleCompleted:
            return "outbound_cycle_completed";
        case SyncReplicaPeerServiceStepDisposition::
                InboundAcceptWindowExpired:
            return "inbound_accept_window_expired";
        case SyncReplicaPeerServiceStepDisposition::InboundSessionObserved:
            return "inbound_session_observed";
        case SyncReplicaPeerServiceStepDisposition::
                IngressPublicationConnected:
            return "ingress_publication_connected";
        case SyncReplicaPeerServiceStepDisposition::
                IngressPublicationUnavailable:
            return "ingress_publication_unavailable";
        case SyncReplicaPeerServiceStepDisposition::IngressPublicationLost:
            return "ingress_publication_lost";
        case SyncReplicaPeerServiceStepDisposition::
                IngressPublicationBackoffPending:
            return "ingress_publication_backoff_pending";
        case SyncReplicaPeerServiceStepDisposition::
                FilesystemWakeRepairCompleted:
            return "filesystem_wake_repair_completed";
        case SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityFaultObserved:
            return "payload_integrity_fault_observed";
        case SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityReproofBackoffPending:
            return "payload_integrity_reproof_backoff_pending";
        case SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityReproofCompleted:
            return "payload_integrity_reproof_completed";
        case SyncReplicaPeerServiceStepDisposition::OutboundSessionIoFailed:
            return "outbound_session_io_failed";
        case SyncReplicaPeerServiceStepDisposition::InboundSessionIoFailed:
            return "inbound_session_io_failed";
        case SyncReplicaPeerServiceStepDisposition::
                PayloadStoreLeaseBusyDeferred:
            return "payload_store_lease_busy_deferred";
        case SyncReplicaPeerServiceStepDisposition::
                OperatorPayloadRecheckCompleted:
            return "operator_payload_recheck_completed";
        case SyncReplicaPeerServiceStepDisposition::
                OperatorPayloadQuarantineCompleted:
            return "operator_payload_quarantine_completed";
        case SyncReplicaPeerServiceStepDisposition::
                OperatorHistoricalVersionCompleted:
            return "operator_historical_version_completed";
        case SyncReplicaPeerServiceStepDisposition::
                PayloadTerminalVerificationAdvanced:
            return "payload_terminal_verification_advanced";
        case SyncReplicaPeerServiceStepDisposition::
                SourceManifestProjectionAdvanced:
            return "source_manifest_projection_advanced";
    }
    return "unknown";
}

struct SyncReplicaPeerServiceOwner::State final {
    enum class LocalPayloadWorkKind : std::uint8_t {
        TerminalVerification = 1U,
        SourceManifestProjection = 2U,
    };

    struct ActivePayloadIntegrityFault final {
        SyncReplicaPeerServicePayloadIntegrityEvidence evidence;
        Clock::time_point first_detected_at = Clock::time_point::min();
        Clock::time_point last_detected_at = Clock::time_point::min();
    };

    struct RecoveredPayloadIntegrityFault final {
        ActivePayloadIntegrityFault fault;
        Clock::time_point recovered_at = Clock::time_point::min();
    };

    SyncReplicaPeerServiceLimits limits;
    SyncReplicaFolderProcessOwner folder_process;
    SyncReplicaFolderWakeOwner folder_wake;
    SyncReplicaSyncCycleOwner outbound_cycle;
    std::unique_ptr<SyncReplicaPeerServerOwner> inbound_server;
    SyncReplicaPeerIngress ingress;
    SyncReplicaNumericStreamEndpoint configured_listen_endpoint;
    SyncReplicaTlsPeerPolicy expected_peer;
    SyncReplicaPeerServiceRole role;
    bool local_recovery_initiator = false;
    bool initial_repair_done = false;
    Clock::time_point next_repair_at = Clock::time_point::min();
    Clock::time_point next_outbound_at = Clock::time_point::min();
    std::uint64_t consecutive_outbound_failures = 0U;
    std::optional<ActivePayloadIntegrityFault> payload_integrity_fault;
    std::optional<RecoveredPayloadIntegrityFault>
        most_recent_payload_integrity_recovery;
    Clock::time_point next_payload_integrity_reproof_at =
        Clock::time_point::min();
    // A failed nonblocking identity-anchor lease acquisition is retried only
    // after this cutpoint. Healthy established services may still accept peer
    // work while local repair is gated; initial repair and integrity recovery
    // remain fail-closed and return clock-only deferral steps.
    Clock::time_point next_payload_store_lease_retry_at =
        Clock::time_point::min();
    std::uint64_t payload_recheck_requested_generation = 0U;
    std::uint64_t payload_recheck_started_generation = 0U;
    std::uint64_t payload_recheck_completed_generation = 0U;
    std::uint64_t payload_recheck_last_hashed_entry_count = 0U;
    std::uint64_t payload_recheck_last_hashed_bytes = 0U;
    std::uint64_t payload_recheck_last_snapshot_handoff_count = 0U;
    std::uint64_t
        payload_recheck_last_convergence_snapshot_observation_count = 0U;
    std::uint64_t
        payload_recheck_last_convergence_mutation_full_scan_count = 0U;
    bool payload_recheck_last_completion_recovered_integrity_fault = false;
    std::uint64_t payload_quarantine_requested_generation = 0U;
    std::uint64_t payload_quarantine_started_generation = 0U;
    std::uint64_t payload_quarantine_completed_generation = 0U;
    std::optional<SyncReplicaFilePayloadStoreQuarantineAction>
        payload_quarantine_action;
    std::string payload_quarantine_expected_content_sha256;
    std::string payload_quarantine_observed_content_sha256;
    std::optional<SyncReplicaFilePayloadStoreQuarantineResult>
        payload_quarantine_last_result;
    std::uint64_t historical_version_requested_generation = 0U;
    std::uint64_t historical_version_started_generation = 0U;
    std::uint64_t historical_version_completed_generation = 0U;
    std::optional<SyncReplicaPeerServiceHistoricalVersionAction>
        historical_version_action;
    SyncReplicaHistoricalVersionQuery historical_version_query;
    SyncReplicaRetentionPlanQuery historical_version_retention_plan_query;
    SyncReplicaHistoricalVersionRestoreRequest
        historical_version_restore_request;
    std::string historical_version_retention_operation_id;
    std::optional<SyncReplicaHistoricalVersionInventory>
        historical_version_last_inventory;
    std::optional<SyncReplicaRetentionPlan>
        historical_version_last_retention_plan;
    std::optional<SyncReplicaHistoricalVersionRestoreResult>
        historical_version_last_restore;
    std::optional<SyncReplicaSqliteHistoricalVersionPinResult>
        historical_version_last_pin_update;
    std::optional<SyncReplicaPeerServiceHistoricalVersionFailureClass>
        historical_version_last_failure_class;
    std::optional<SyncReplicaHistoricalVersionSourceChangeStage>
        historical_version_last_source_change_stage;
    std::optional<std::string> historical_version_last_failure;
    bool ingress_is_ready = false;
    bool ingress_setup_in_progress = false;
    Clock::time_point next_ingress_attempt_at = Clock::time_point::min();
    std::uint64_t consecutive_ingress_failures = 0U;
    std::uint64_t observed_ingress_event_generation = 0U;
    bool filesystem_wake_pending = false;
    bool filesystem_wake_overflow = false;
    bool filesystem_watch_rebuilt = false;
    std::uint64_t filesystem_wake_event_count = 0U;
    // Every bounded local payload hash pulse yields at least one ordinary
    // owner turn before another local pulse. When both receiver terminal
    // verification and source-manifest preparation are pending, selection
    // alternates so neither multi-terabyte obligation can starve the other.
    std::optional<LocalPayloadWorkKind> local_payload_work_ordinary_turn_due;
    LocalPayloadWorkKind next_local_payload_work =
        LocalPayloadWorkKind::TerminalVerification;
    SyncReplicaPeerServiceCounters counters;
    std::string label;

    // Declared last so its jthread stops and joins before the application/TLS,
    // folder, or database owners can begin destruction.
    std::unique_ptr<SyncReplicaI2pIngressWorker> i2p_ingress_worker;

    State(
        SyncReplicaDeploymentManifest deployment,
        SyncReplicaFileTlsClientContext client_context,
        SyncReplicaFileTlsServerContext server_context,
        SyncReplicaStreamRoute route,
        SyncReplicaPeerIngress selected_ingress,
        SyncReplicaTlsPeerPolicy peer,
        SyncReplicaNumericStreamEndpoint listen_endpoint,
        SyncReplicaPeerServiceLimits selected_limits,
        std::string owner_label)
        : limits(std::move(selected_limits)),
          folder_process(
              std::move(deployment), owner_label + " folder process"),
          folder_wake(
              *folder_process.deployment().files_root,
              SyncReplicaFolderWakeLimits{},
              owner_label + " folder wake"),
          outbound_cycle(
              folder_process, std::move(client_context), std::move(route),
              peer, owner_label + " outbound cycle"),
          ingress(std::move(selected_ingress)),
          configured_listen_endpoint(std::move(listen_endpoint)),
          expected_peer(std::move(peer)),
          role(folder_process.deployment().local_actor < expected_peer.actor
                   ? SyncReplicaPeerServiceRole::OutboundPull
                   : SyncReplicaPeerServiceRole::InboundServe),
          local_recovery_initiator(
              folder_process.deployment().local_actor < expected_peer.actor),
          label(std::move(owner_label)) {
        if (native_i2p_ingress()) {
            inbound_server = std::make_unique<SyncReplicaPeerServerOwner>(
                folder_process, std::move(server_context),
                label + " inbound overlay application");
            i2p_ingress_worker =
                std::make_unique<SyncReplicaI2pIngressWorker>(
                    i2p_accept_route_or_throw(ingress, label + " ingress"),
                    limits.ingress_setup_timeout_seconds,
                    limits.retry_initial_milliseconds,
                    limits.retry_maximum_milliseconds,
                    label + " native I2P ingress");
        } else {
            inbound_server = std::make_unique<SyncReplicaPeerServerOwner>(
                folder_process, std::move(server_context),
                configured_listen_endpoint,
                label + " inbound server");
            ingress_is_ready = true;
        }
    }

    [[nodiscard]] bool native_i2p_ingress() const noexcept {
        return sync_replica_peer_ingress_kind(ingress) ==
            SyncReplicaPeerIngressKind::I2pSamAccept;
    }

    void update_ingress_retry_delay(
        SyncReplicaPeerServiceStepResult& result) const {
        if (ingress_is_ready) return;
        if (next_ingress_attempt_at != Clock::time_point::min()) {
            result.ingress_retry_delay_milliseconds =
                remaining_milliseconds(
                    Clock::now(), next_ingress_attempt_at);
        }
        if (result.ingress_retry_delay_milliseconds == 0U &&
            ingress_setup_in_progress) {
            result.ingress_retry_delay_milliseconds = std::min(
                limits.accept_window_milliseconds,
                kSyncReplicaPeerServiceMaximumIngressBackoffWaitMilliseconds);
        }
        if (result.ingress_retry_delay_milliseconds == 0U) {
            result.ingress_retry_delay_milliseconds = 1U;
        }
    }

    void finish_ingress_step(SyncReplicaPeerServiceStepResult& result) {
        result.role_after = role;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        update_ingress_retry_delay(result);
        ++counters.steps;
    }

    [[nodiscard]] std::optional<SyncReplicaPeerServiceStepResult>
    refresh_ingress_worker(bool observe_event) {
        if (!native_i2p_ingress()) return std::nullopt;
        if (!i2p_ingress_worker) {
            throw std::logic_error(
                label + " omitted its native I2P ingress worker");
        }
        const SyncReplicaI2pIngressWorkerSnapshot snapshot =
            i2p_ingress_worker->snapshot();
        ingress_is_ready = snapshot.ready;
        ingress_setup_in_progress = snapshot.setup_in_progress;
        next_ingress_attempt_at = snapshot.retry_at;
        consecutive_ingress_failures = snapshot.consecutive_failures;
        counters.ingress_setup_attempts = snapshot.setup_attempts;
        counters.ingress_setup_successes = snapshot.setup_successes;
        counters.ingress_setup_failures = snapshot.setup_failures;
        counters.ingress_losses = snapshot.losses;

        if (!observe_event ||
            snapshot.event_generation == observed_ingress_event_generation) {
            return std::nullopt;
        }
        observed_ingress_event_generation = snapshot.event_generation;
        if (snapshot.event == SyncReplicaI2pIngressWorkerEvent::None) {
            return std::nullopt;
        }

        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        result.ingress_report = snapshot.report;
        result.ingress_error = snapshot.diagnostic;
        switch (snapshot.event) {
            case SyncReplicaI2pIngressWorkerEvent::PublicationConnected:
                result.disposition = SyncReplicaPeerServiceStepDisposition::
                    IngressPublicationConnected;
                break;
            case SyncReplicaI2pIngressWorkerEvent::PublicationUnavailable:
                result.disposition = SyncReplicaPeerServiceStepDisposition::
                    IngressPublicationUnavailable;
                break;
            case SyncReplicaI2pIngressWorkerEvent::PublicationLost:
                result.disposition = SyncReplicaPeerServiceStepDisposition::
                    IngressPublicationLost;
                break;
            case SyncReplicaI2pIngressWorkerEvent::None:
                throw std::logic_error(
                    label + " observed an empty I2P ingress event");
        }
        finish_ingress_step(result);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult ingress_backoff_step() {
        const Clock::time_point now = Clock::now();
        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        result.disposition = SyncReplicaPeerServiceStepDisposition::
            IngressPublicationBackoffPending;
        if (local_recovery_initiator &&
            next_outbound_at != Clock::time_point::min() &&
            now >= next_outbound_at) {
            role = SyncReplicaPeerServiceRole::OutboundPull;
        }
        ++counters.ingress_backoff_deferrals;
        finish_ingress_step(result);
        return result;
    }

    void observe_folder_wake_or_throw() {
        const SyncReplicaFolderWakeObservation observation =
            folder_wake.observe_or_throw();
        if (!observation.wake_observed) return;
        filesystem_wake_pending = true;
        filesystem_wake_overflow = filesystem_wake_overflow ||
            observation.kernel_queue_overflow ||
            observation.observation_budget_exhausted;
        filesystem_watch_rebuilt = filesystem_watch_rebuilt ||
            observation.watch_set_rebuilt;
        if (observation.event_count >
            std::numeric_limits<std::uint64_t>::max() -
                filesystem_wake_event_count) {
            filesystem_wake_event_count =
                std::numeric_limits<std::uint64_t>::max();
        } else {
            filesystem_wake_event_count += observation.event_count;
        }
    }

    void attach_folder_wake(
        SyncReplicaPeerServiceStepResult& result) const noexcept {
        if (!filesystem_wake_pending) return;
        result.filesystem_wake_observed = true;
        result.filesystem_wake_overflow = filesystem_wake_overflow;
        result.filesystem_watch_rebuilt = filesystem_watch_rebuilt;
        result.filesystem_wake_event_count =
            filesystem_wake_event_count;
    }

    void consume_folder_wake() noexcept {
        filesystem_wake_pending = false;
        filesystem_wake_overflow = false;
        filesystem_watch_rebuilt = false;
        filesystem_wake_event_count = 0U;
    }

    void schedule_next_repair(Clock::time_point completed_at) {
        next_repair_at = add_milliseconds_or_throw(
            completed_at, limits.repair_interval_milliseconds,
            label + " next repair");
    }

    [[nodiscard]] std::optional<SyncReplicaPeerServicePayloadIntegrityFault>
    payload_integrity_status() const {
        if (!payload_integrity_fault.has_value()) return std::nullopt;
        const Clock::time_point now = Clock::now();
        const ActivePayloadIntegrityFault& active = *payload_integrity_fault;
        SyncReplicaPeerServicePayloadIntegrityFault status;
        status.expected_content_sha256 =
            active.evidence.expected_content_sha256;
        status.observed_content_sha256 =
            active.evidence.observed_content_sha256;
        status.failure_persisted = active.evidence.failure_persisted;
        status.detection_count = active.evidence.detection_count;
        status.observed_content_change_count =
            active.evidence.observed_content_change_count;
        status.active_age_milliseconds =
            elapsed_milliseconds(now, active.first_detected_at);
        status.last_detection_age_milliseconds =
            elapsed_milliseconds(now, active.last_detected_at);
        status.retry_delay_milliseconds = remaining_milliseconds(
            now, next_payload_integrity_reproof_at);
        return status;
    }

    [[nodiscard]]
    std::optional<SyncReplicaPeerServicePayloadIntegrityRecovery>
    payload_integrity_recovery_status() const {
        if (!most_recent_payload_integrity_recovery.has_value()) {
            return std::nullopt;
        }
        const Clock::time_point now = Clock::now();
        const RecoveredPayloadIntegrityFault& recovered =
            *most_recent_payload_integrity_recovery;
        SyncReplicaPeerServicePayloadIntegrityRecovery status;
        status.expected_content_sha256 =
            recovered.fault.evidence.expected_content_sha256;
        status.observed_content_sha256 =
            recovered.fault.evidence.observed_content_sha256;
        status.failure_persisted =
            recovered.fault.evidence.failure_persisted;
        status.detection_count = recovered.fault.evidence.detection_count;
        status.observed_content_change_count =
            recovered.fault.evidence.observed_content_change_count;
        status.fault_duration_milliseconds = elapsed_milliseconds(
            recovered.recovered_at, recovered.fault.first_detected_at);
        status.recovery_age_milliseconds = elapsed_milliseconds(
            now, recovered.recovered_at);
        return status;
    }

    [[nodiscard]] bool payload_recheck_pending() const noexcept {
        return payload_recheck_requested_generation >
            payload_recheck_completed_generation;
    }

    [[nodiscard]] SyncReplicaPeerServicePayloadRecheckStatus
    payload_recheck_status() const noexcept {
        SyncReplicaPeerServicePayloadRecheckStatus status;
        status.requested_generation = payload_recheck_requested_generation;
        status.started_generation = payload_recheck_started_generation;
        status.completed_generation = payload_recheck_completed_generation;
        status.pending = payload_recheck_pending();
        const Clock::time_point now = Clock::now();
        status.retry_delay_milliseconds = std::max(
            remaining_milliseconds(
                now, next_payload_integrity_reproof_at),
            remaining_milliseconds(
                now, next_payload_store_lease_retry_at));
        status.last_hashed_entry_count =
            payload_recheck_last_hashed_entry_count;
        status.last_hashed_bytes = payload_recheck_last_hashed_bytes;
        status.last_snapshot_handoff_count =
            payload_recheck_last_snapshot_handoff_count;
        status.last_convergence_snapshot_observation_count =
            payload_recheck_last_convergence_snapshot_observation_count;
        status.last_convergence_mutation_full_scan_count =
            payload_recheck_last_convergence_mutation_full_scan_count;
        status.last_completion_recovered_integrity_fault =
            payload_recheck_last_completion_recovered_integrity_fault;
        return status;
    }

    void observe_payload_recheck_request_generation_or_throw(
        std::uint64_t generation) {
        if (generation < payload_recheck_requested_generation) {
            throw std::invalid_argument(
                label +
                " payload recheck request generation regressed from " +
                std::to_string(payload_recheck_requested_generation) +
                " to " + std::to_string(generation));
        }
        if (generation == payload_recheck_requested_generation) return;

        const bool pending_before = payload_recheck_pending();
        const std::uint64_t delta =
            generation - payload_recheck_requested_generation;
        add_saturating(counters.payload_recheck_requests_observed, delta);
        const std::uint64_t coalesced = pending_before ? delta : delta - 1U;
        add_saturating(
            counters.payload_recheck_requests_coalesced, coalesced);
        payload_recheck_requested_generation = generation;

        if (!pending_before) {
            // One newly pending explicit owner obligation may bypass an old
            // automatic cutpoint. Once an attempt establishes fresh integrity
            // or lease backoff, later accepted generations coalesce without
            // clearing it, so a request storm cannot turn bounded retry into a
            // busy loop.
            next_payload_integrity_reproof_at = Clock::time_point::min();
            next_payload_store_lease_retry_at = Clock::time_point::min();
        }
    }

    [[nodiscard]] bool payload_quarantine_pending() const noexcept {
        return payload_quarantine_requested_generation >
            payload_quarantine_completed_generation;
    }

    [[nodiscard]] SyncReplicaPeerServicePayloadQuarantineStatus
    payload_quarantine_status() const {
        SyncReplicaPeerServicePayloadQuarantineStatus status;
        status.requested_generation = payload_quarantine_requested_generation;
        status.started_generation = payload_quarantine_started_generation;
        status.completed_generation = payload_quarantine_completed_generation;
        status.pending = payload_quarantine_pending();
        status.action = payload_quarantine_action;
        status.expected_content_sha256 =
            payload_quarantine_expected_content_sha256;
        status.observed_content_sha256 =
            payload_quarantine_observed_content_sha256;
        status.retry_delay_milliseconds = remaining_milliseconds(
            Clock::now(), next_payload_store_lease_retry_at);
        status.last_result = payload_quarantine_last_result;
        return status;
    }

    void observe_payload_quarantine_request_or_throw(
        std::uint64_t generation,
        SyncReplicaFilePayloadStoreQuarantineAction action,
        std::string expected_content_sha256,
        std::string observed_content_sha256) {
        if ((action != SyncReplicaFilePayloadStoreQuarantineAction::Preserve &&
             action != SyncReplicaFilePayloadStoreQuarantineAction::Release) ||
            generation == 0U ||
            !is_lowercase_sha256_hex(expected_content_sha256) ||
            !is_lowercase_sha256_hex(observed_content_sha256) ||
            expected_content_sha256 == observed_content_sha256) {
            throw std::invalid_argument(
                label + " payload quarantine request is not canonical");
        }
        if (generation < payload_quarantine_requested_generation) {
            throw std::invalid_argument(
                label +
                " payload quarantine request generation regressed from " +
                std::to_string(payload_quarantine_requested_generation) +
                " to " + std::to_string(generation));
        }
        if (generation == payload_quarantine_requested_generation) {
            if (!payload_quarantine_action.has_value() ||
                *payload_quarantine_action != action ||
                payload_quarantine_expected_content_sha256 !=
                    expected_content_sha256 ||
                payload_quarantine_observed_content_sha256 !=
                    observed_content_sha256) {
                throw std::invalid_argument(
                    label +
                    " payload quarantine pair changed at one generation");
            }
            return;
        }

        const bool pending_before = payload_quarantine_pending();
        if (pending_before &&
            (!payload_quarantine_action.has_value() ||
             *payload_quarantine_action != action ||
             payload_quarantine_expected_content_sha256 !=
                 expected_content_sha256 ||
             payload_quarantine_observed_content_sha256 !=
                 observed_content_sha256)) {
            throw std::invalid_argument(
                label +
                " payload quarantine pair changed while an older generation "
                "remains pending");
        }
        const std::uint64_t delta =
            generation - payload_quarantine_requested_generation;
        add_saturating(
            counters.payload_quarantine_requests_observed, delta);
        const std::uint64_t coalesced = pending_before ? delta : delta - 1U;
        add_saturating(
            counters.payload_quarantine_requests_coalesced, coalesced);
        payload_quarantine_requested_generation = generation;
        payload_quarantine_action = action;
        payload_quarantine_expected_content_sha256 =
            std::move(expected_content_sha256);
        payload_quarantine_observed_content_sha256 =
            std::move(observed_content_sha256);
        if (!pending_before) {
            next_payload_store_lease_retry_at = Clock::time_point::min();
        }
    }

    [[nodiscard]] bool historical_version_pending() const noexcept {
        return historical_version_requested_generation >
            historical_version_completed_generation;
    }

    [[nodiscard]] SyncReplicaPeerServiceHistoricalVersionStatus
    historical_version_status() const {
        SyncReplicaPeerServiceHistoricalVersionStatus status;
        status.requested_generation = historical_version_requested_generation;
        status.started_generation = historical_version_started_generation;
        status.completed_generation = historical_version_completed_generation;
        status.pending = historical_version_pending();
        status.action = historical_version_action;
        status.query = historical_version_query;
        status.retention_plan_query =
            historical_version_retention_plan_query;
        status.restore_request = historical_version_restore_request;
        status.retention_operation_id =
            historical_version_retention_operation_id;
        status.retry_delay_milliseconds = remaining_milliseconds(
            Clock::now(), next_payload_store_lease_retry_at);
        status.last_inventory = historical_version_last_inventory;
        status.last_retention_plan = historical_version_last_retention_plan;
        status.last_restore = historical_version_last_restore;
        status.last_pin_update = historical_version_last_pin_update;
        status.last_failure_class = historical_version_last_failure_class;
        status.last_source_change_stage =
            historical_version_last_source_change_stage;
        status.last_failure = historical_version_last_failure;
        return status;
    }

    void observe_historical_version_request_or_throw(
        std::uint64_t generation,
        SyncReplicaPeerServiceHistoricalVersionAction action,
        SyncReplicaHistoricalVersionRestoreRequest restore_request,
        SyncReplicaHistoricalVersionQuery query,
        SyncReplicaRetentionPlanQuery retention_plan_query,
        std::string retention_operation_id) {
        const bool inspecting =
            action == SyncReplicaPeerServiceHistoricalVersionAction::Inspect;
        const bool restoring =
            action == SyncReplicaPeerServiceHistoricalVersionAction::Restore;
        const bool pinning =
            action == SyncReplicaPeerServiceHistoricalVersionAction::Pin;
        const bool unpinning =
            action == SyncReplicaPeerServiceHistoricalVersionAction::Unpin;
        const bool planning =
            action ==
            SyncReplicaPeerServiceHistoricalVersionAction::RetentionPlan;
        const bool retention_update = pinning || unpinning;
        if ((!inspecting && !restoring && !retention_update && !planning) ||
            generation == 0U ||
            (inspecting &&
             (restore_request != SyncReplicaHistoricalVersionRestoreRequest{} ||
              retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
              !retention_operation_id.empty())) ||
            (planning &&
             (query != SyncReplicaHistoricalVersionQuery{} ||
              restore_request != SyncReplicaHistoricalVersionRestoreRequest{} ||
              !retention_operation_id.empty())) ||
            (restoring &&
             (query != SyncReplicaHistoricalVersionQuery{} ||
              retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
              !retention_operation_id.empty())) ||
            (retention_update &&
             (query != SyncReplicaHistoricalVersionQuery{} ||
              retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
              restore_request != SyncReplicaHistoricalVersionRestoreRequest{} ||
              !is_lowercase_sha256_hex(retention_operation_id)))) {
            throw std::invalid_argument(
                label + " historical-version request is not canonical");
        }
        if (inspecting) {
            validate_sync_replica_historical_version_query_or_throw(
                query, label + " historical-version request");
        } else if (planning) {
            validate_sync_replica_retention_plan_query_or_throw(
                retention_plan_query, label + " retention-plan request");
        } else if (restoring) {
            validate_sync_replica_historical_version_restore_request_or_throw(
                restore_request, label + " historical-version request");
        }
        if (generation < historical_version_requested_generation) {
            throw std::invalid_argument(
                label +
                " historical-version request generation regressed from " +
                std::to_string(historical_version_requested_generation) +
                " to " + std::to_string(generation));
        }
        if (generation == historical_version_requested_generation) {
            if (!historical_version_action.has_value() ||
                *historical_version_action != action ||
                historical_version_query != query ||
                historical_version_retention_plan_query !=
                    retention_plan_query ||
                historical_version_restore_request != restore_request ||
                historical_version_retention_operation_id !=
                    retention_operation_id) {
                throw std::invalid_argument(
                    label +
                    " historical-version request changed at one generation");
            }
            return;
        }

        const bool pending_before = historical_version_pending();
        if (pending_before &&
            (!historical_version_action.has_value() ||
             *historical_version_action != action ||
             historical_version_query != query ||
             historical_version_retention_plan_query !=
                 retention_plan_query ||
             historical_version_restore_request != restore_request ||
             historical_version_retention_operation_id !=
                 retention_operation_id)) {
            throw std::invalid_argument(
                label +
                " historical-version request changed while an older generation remains pending");
        }
        const std::uint64_t delta =
            generation - historical_version_requested_generation;
        add_saturating(counters.historical_version_requests_observed, delta);
        const std::uint64_t coalesced = pending_before ? delta : delta - 1U;
        add_saturating(
            counters.historical_version_requests_coalesced, coalesced);
        historical_version_requested_generation = generation;
        historical_version_action = action;
        historical_version_query = std::move(query);
        historical_version_retention_plan_query =
            std::move(retention_plan_query);
        historical_version_restore_request = std::move(restore_request);
        historical_version_retention_operation_id =
            std::move(retention_operation_id);
        if (!pending_before) {
            next_payload_store_lease_retry_at = Clock::time_point::min();
        }
    }

    void record_payload_integrity_evidence_or_throw(
        std::string_view expected_content_sha256,
        std::string_view observed_content_sha256,
        bool failure_persisted) {

        const Clock::time_point now = Clock::now();
        if (!payload_integrity_fault.has_value()) {
            ActivePayloadIntegrityFault active;
            const auto update =
                merge_sync_replica_peer_service_payload_integrity_evidence(
                    active.evidence, expected_content_sha256,
                    observed_content_sha256, failure_persisted);
            if (update !=
                SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate::
                    NewExpectedContent) {
                throw std::logic_error(
                    label +
                    " initial payload integrity evidence was not new");
            }
            active.first_detected_at = now;
            active.last_detected_at = now;
            payload_integrity_fault = std::move(active);
        } else {
            const auto update =
                merge_sync_replica_peer_service_payload_integrity_evidence(
                    payload_integrity_fault->evidence,
                    expected_content_sha256, observed_content_sha256,
                    failure_persisted);
            if (update ==
                SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate::
                    NewExpectedContent) {
                payload_integrity_fault->first_detected_at = now;
            }
            payload_integrity_fault->last_detected_at = now;
        }
        increment_saturating(counters.payload_integrity_faults_observed);
        const std::uint64_t retry_delay = retry_delay_milliseconds(
            limits, payload_integrity_fault->evidence.detection_count);
        next_payload_integrity_reproof_at = add_milliseconds_or_throw(
            now, retry_delay, label + " payload integrity reproof");
    }

    void record_payload_integrity_fault_or_throw(
        const SyncReplicaFilePayloadStoreIntegrityError& error) {
        record_payload_integrity_evidence_or_throw(
            error.expected_content_sha256(),
            error.observed_content_sha256(), error.failure_persisted());
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    state_preserving_deferral_step(
        SyncReplicaPeerServiceStepDisposition disposition) const noexcept {
        SyncReplicaPeerServiceStepResult result;
        result.disposition = disposition;
        result.role_before = role;
        result.role_after = role;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        return result;
    }

    void apply_unknown_network_outcome_fence_or_throw(
        SyncReplicaPeerServiceStepResult& result,
        PayloadAuthorityFailureContext context,
        Clock::time_point now) {
        if (!network_outcome_is_unknown(context)) return;

        result.network_outcome_known = false;
        increment_saturating(
            counters.payload_authority_network_outcome_uncertain_steps);
        if (context ==
            PayloadAuthorityFailureContext::OutboundNetworkStep) {
            if (role != SyncReplicaPeerServiceRole::OutboundPull) {
                throw std::logic_error(
                    label +
                    " outbound payload-authority failure lacks outbound role");
            }
            attach_folder_wake(result);
            const std::uint64_t conservative_turn_lease =
                successful_handoff_lease_milliseconds(limits);
            next_outbound_at = add_milliseconds_or_throw(
                now, conservative_turn_lease,
                label + " unknown outbound outcome turn fence");
            result.retry_delay_milliseconds = conservative_turn_lease;
            // The peer may already have observed a valid request/response even
            // though the local stack lost the completed result. Never redial
            // from that ambiguity. Yield exactly as after a proven handoff and
            // let actor asymmetry recover after the full cycle horizon.
            role = SyncReplicaPeerServiceRole::InboundServe;
        }
        result.role_after = role;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    payload_integrity_fault_step_or_throw(
        const SyncReplicaFilePayloadStoreIntegrityError& error,
        PayloadAuthorityFailureContext context) {
        record_payload_integrity_fault_or_throw(error);
        next_payload_store_lease_retry_at = Clock::time_point::min();
        SyncReplicaPeerServiceStepResult result =
            state_preserving_deferral_step(
                SyncReplicaPeerServiceStepDisposition::
                    PayloadIntegrityFaultObserved);
        const Clock::time_point now = Clock::now();
        apply_unknown_network_outcome_fence_or_throw(result, context, now);
        result.payload_integrity_retry_delay_milliseconds =
            remaining_milliseconds(
                now, next_payload_integrity_reproof_at);
        increment_saturating(counters.steps);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    payload_integrity_backoff_step() {
        SyncReplicaPeerServiceStepResult result =
            state_preserving_deferral_step(
                SyncReplicaPeerServiceStepDisposition::
                    PayloadIntegrityReproofBackoffPending);
        result.payload_integrity_retry_delay_milliseconds =
            remaining_milliseconds(
                Clock::now(), next_payload_integrity_reproof_at);
        increment_saturating(counters.steps);
        increment_saturating(
            counters.payload_integrity_backoff_deferrals);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    payload_store_lease_busy_step(
        const SyncReplicaFilePayloadStoreLeaseBusyError&,
        PayloadAuthorityFailureContext context) {
        const Clock::time_point now = Clock::now();
        next_payload_store_lease_retry_at = add_milliseconds_or_throw(
            now, limits.retry_initial_milliseconds,
            label + " payload-store lease retry");
        // One exact retry cutpoint serves both directions. It moves an overdue
        // repair forward so a held cooperative lease cannot win every scheduler
        // turn, and it moves a distant periodic repair earlier after an
        // interrupted network session so separately committed catalog/replica
        // progress receives bounded convergence. Until the cutpoint, an
        // established healthy service may accept network work instead of
        // probing flock four times per second.
        if (initial_repair_done) {
            next_repair_at = next_payload_store_lease_retry_at;
        }

        SyncReplicaPeerServiceStepResult result =
            state_preserving_deferral_step(
                SyncReplicaPeerServiceStepDisposition::
                    PayloadStoreLeaseBusyDeferred);
        result.payload_store_lease_conflict_observed = true;
        apply_unknown_network_outcome_fence_or_throw(result, context, now);
        result.payload_store_lease_retry_delay_milliseconds =
            remaining_milliseconds(
                now, next_payload_store_lease_retry_at);
        increment_saturating(counters.steps);
        increment_saturating(counters.payload_store_lease_busy_deferrals);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    payload_store_lease_backoff_step() {
        SyncReplicaPeerServiceStepResult result =
            state_preserving_deferral_step(
                SyncReplicaPeerServiceStepDisposition::
                    PayloadStoreLeaseBusyDeferred);
        result.payload_store_lease_retry_delay_milliseconds =
            remaining_milliseconds(
                Clock::now(), next_payload_store_lease_retry_at);
        increment_saturating(counters.steps);
        increment_saturating(
            counters.payload_store_lease_backoff_deferrals);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    payload_terminal_verification_step_or_throw() {
        const auto before =
            folder_process.payload_store_or_throw()
                .terminal_verification_status();
        if (!before.observation_known || before.pending_entry_count == 0U ||
            !before.next_work.has_value()) {
            throw std::logic_error(
                label +
                " terminal-verification scheduler lacks known pending work");
        }

        // Publish the fairness obligation before entering the store. Even a
        // typed lease conflict must yield one ordinary owner turn before this
        // local scheduler probes again.
        local_payload_work_ordinary_turn_due =
            LocalPayloadWorkKind::TerminalVerification;
        next_local_payload_work =
            LocalPayloadWorkKind::SourceManifestProjection;
        const auto advanced =
            folder_process.payload_store_or_throw()
                .continue_one_pending_terminal_verification_or_throw();
        if (advanced.disposition ==
                SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    ObservationUnknown ||
            advanced.disposition ==
                SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    NoPendingWork ||
            !advanced.work_before.has_value()) {
            throw std::logic_error(
                label +
                " terminal-verification scheduler lost its selected obligation");
        }

        SyncReplicaPeerServiceStepResult result =
            state_preserving_deferral_step(
                SyncReplicaPeerServiceStepDisposition::
                    PayloadTerminalVerificationAdvanced);
        result.payload_terminal_verification = advanced;
        increment_saturating(counters.steps);
        increment_saturating(
            counters.payload_terminal_verification_scheduler_steps);
        add_saturating(
            counters.payload_terminal_verification_hashed_bytes,
            advanced.hashed_bytes);
        switch (advanced.disposition) {
            case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    Progress:
                increment_saturating(
                    counters.payload_terminal_verification_progress_steps);
                break;
            case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    CompletedInserted:
                increment_saturating(
                    counters.payload_terminal_verification_completions);
                increment_saturating(
                    counters.payload_terminal_verification_insertions);
                break;
            case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    CompletedAlreadyPresent:
                increment_saturating(
                    counters.payload_terminal_verification_completions);
                increment_saturating(
                    counters.payload_terminal_verification_reconciliations);
                break;
            case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    ObservationUnknown:
            case SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                    NoPendingWork:
                throw std::logic_error(
                    label +
                    " terminal-verification scheduler returned an idle disposition");
        }
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    source_manifest_projection_step_or_throw() {
        const auto before =
            inbound_server->source_manifest_projection_status();
        if (!before.pending) {
            throw std::logic_error(
                label +
                " source-manifest scheduler lacks pending projection work");
        }

        // Publish the fairness obligation before entering targeted payload
        // access. A typed lease conflict still consumes this local-work turn.
        local_payload_work_ordinary_turn_due =
            LocalPayloadWorkKind::SourceManifestProjection;
        next_local_payload_work =
            LocalPayloadWorkKind::TerminalVerification;
        const auto advanced =
            inbound_server->continue_source_manifest_projection_or_throw();
        if (advanced.disposition ==
                SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                    NoPendingWork ||
            !advanced.before.pending) {
            throw std::logic_error(
                label +
                " source-manifest scheduler lost its selected obligation");
        }

        SyncReplicaPeerServiceStepResult result =
            state_preserving_deferral_step(
                SyncReplicaPeerServiceStepDisposition::
                    SourceManifestProjectionAdvanced);
        result.source_manifest_projection = advanced;
        increment_saturating(counters.steps);
        increment_saturating(
            counters.source_manifest_projection_scheduler_steps);
        add_saturating(
            counters.source_manifest_projection_hashed_bytes,
            advanced.hashed_bytes);
        if (advanced.projection_restarted) {
            increment_saturating(
                counters.source_manifest_projection_restarts);
        }
        switch (advanced.disposition) {
            case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                    Progress:
                increment_saturating(
                    counters.source_manifest_projection_progress_steps);
                break;
            case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                    Completed:
                increment_saturating(
                    counters.source_manifest_projection_completions);
                break;
            case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                    PayloadUnavailable:
                increment_saturating(
                    counters.source_manifest_projection_payload_unavailable);
                break;
            case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                    NoPendingWork:
                throw std::logic_error(
                    label +
                    " source-manifest scheduler returned an idle disposition");
        }
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    complete_payload_snapshot_convergence_or_throw(
        SyncReplicaFilePayloadStoreSnapshot payload_snapshot,
        SyncReplicaPeerServiceStepDisposition disposition,
        std::uint64_t payload_recheck_generation = 0U,
        std::uint64_t payload_recheck_hashed_entry_count = 0U,
        std::uint64_t payload_recheck_hashed_bytes = 0U) {
        const bool operator_recheck =
            disposition == SyncReplicaPeerServiceStepDisposition::
                OperatorPayloadRecheckCompleted;
        const bool automatic_reproof =
            disposition == SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityReproofCompleted;
        if (operator_recheck == automatic_reproof) {
            throw std::logic_error(
                label + " payload snapshot convergence disposition is invalid");
        }
        if (operator_recheck) {
            if (payload_recheck_generation == 0U ||
                payload_recheck_generation >
                    payload_recheck_requested_generation ||
                payload_recheck_generation <=
                    payload_recheck_completed_generation) {
                throw std::logic_error(
                    label + " payload recheck completion generation is invalid");
            }
        } else if (payload_recheck_generation != 0U ||
                   !payload_integrity_fault.has_value()) {
            throw std::logic_error(
                label + " automatic payload reproof lacks exact fault state");
        }

        const bool initial = !initial_repair_done;
        const bool recovered_integrity_fault =
            payload_integrity_fault.has_value();
        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        result.initial_repair = initial;
        result.repair.emplace(
            folder_process
                .run_convergence_pass_with_payload_snapshot_or_throw(
                    std::move(payload_snapshot), limits.folder_limits));

        if (operator_recheck) {
            result.payload_recheck_generation = payload_recheck_generation;
            result.payload_recheck_hashed_entry_count =
                payload_recheck_hashed_entry_count;
            result.payload_recheck_hashed_bytes =
                payload_recheck_hashed_bytes;
            result.payload_recheck_snapshot_handoff_count =
                result.repair->payload_snapshot_handoff_count;
            result.payload_recheck_convergence_snapshot_observation_count =
                result.repair->payload_snapshot_observation_count;
            result.payload_recheck_convergence_mutation_full_scan_count =
                result.repair->payload_mutation_full_scan_count;
            result.payload_recheck_recovered_integrity_fault =
                recovered_integrity_fault;
            add_saturating(
                counters.payload_recheck_snapshot_handoffs,
                result.payload_recheck_snapshot_handoff_count);
            add_saturating(
                counters.payload_recheck_convergence_snapshot_observations,
                result
                    .payload_recheck_convergence_snapshot_observation_count);
            add_saturating(
                counters.payload_recheck_convergence_mutation_full_scans,
                result
                    .payload_recheck_convergence_mutation_full_scan_count);
        } else {
            add_saturating(
                counters.payload_integrity_reproof_snapshot_handoffs,
                result.repair->payload_snapshot_handoff_count);
            add_saturating(
                counters
                    .payload_integrity_reproof_convergence_snapshot_observations,
                result.repair->payload_snapshot_observation_count);
            add_saturating(
                counters
                    .payload_integrity_reproof_convergence_mutation_full_scans,
                result.repair->payload_mutation_full_scan_count);
        }

        // Native I2P publication continues on its capability-free worker while
        // the owner performs the potentially long byte proof and convergence
        // pass. Refresh at the authority-restoration cutpoint so readiness can
        // never be restored from a stale pre-proof ingress snapshot.
        (void)refresh_ingress_worker(false);
        initial_repair_done = true;
        const Clock::time_point completed_at = Clock::now();
        schedule_next_repair(completed_at);
        if (recovered_integrity_fault) {
            RecoveredPayloadIntegrityFault recovered;
            recovered.fault = std::move(*payload_integrity_fault);
            recovered.recovered_at = completed_at;
            most_recent_payload_integrity_recovery = std::move(recovered);
            payload_integrity_fault.reset();
        }
        next_payload_integrity_reproof_at = Clock::time_point::min();
        next_payload_store_lease_retry_at = Clock::time_point::min();

        if (operator_recheck) {
            payload_recheck_completed_generation = payload_recheck_generation;
            payload_recheck_last_hashed_entry_count =
                payload_recheck_hashed_entry_count;
            payload_recheck_last_hashed_bytes =
                payload_recheck_hashed_bytes;
            payload_recheck_last_snapshot_handoff_count =
                result.payload_recheck_snapshot_handoff_count;
            payload_recheck_last_convergence_snapshot_observation_count =
                result
                    .payload_recheck_convergence_snapshot_observation_count;
            payload_recheck_last_convergence_mutation_full_scan_count =
                result
                    .payload_recheck_convergence_mutation_full_scan_count;
            payload_recheck_last_completion_recovered_integrity_fault =
                recovered_integrity_fault;
            increment_saturating(counters.payload_recheck_completions);
            if (recovered_integrity_fault) {
                increment_saturating(
                    counters.payload_recheck_integrity_recoveries);
            }
        } else {
            increment_saturating(
                counters.payload_integrity_reproof_recoveries);
        }

        result.role_after = role;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        result.disposition = disposition;
        increment_saturating(counters.steps);
        if (initial) {
            increment_saturating(counters.initial_repairs);
        } else {
            increment_saturating(counters.periodic_repairs);
        }
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    payload_integrity_reproof_step_or_throw() {
        if (!payload_integrity_fault.has_value()) {
            throw std::logic_error(
                label + " payload integrity reproof lacks an active fault");
        }
        increment_saturating(counters.payload_integrity_reproof_attempts);

        // The complete leased payload snapshot is the sole authority that can
        // clear the process-local fail-closed witness after current bytes or
        // absence are proved. Other unchanged payloads may retain exact verified
        // metadata reuse; the faulted identity itself cannot.
        SyncReplicaFilePayloadStoreSnapshot payload_reproof =
            folder_process.payload_store_or_throw().snapshot_or_throw();
        return complete_payload_snapshot_convergence_or_throw(
            std::move(payload_reproof),
            SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityReproofCompleted);
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    operator_payload_recheck_step_or_throw() {
        if (!payload_recheck_pending()) {
            throw std::logic_error(
                label + " operator payload recheck lacks pending generation");
        }
        const std::uint64_t target_generation =
            payload_recheck_requested_generation;
        payload_recheck_started_generation = target_generation;
        increment_saturating(counters.payload_recheck_attempts);

        // Unlike automatic fault recovery, explicit owner recheck disables all
        // process and durable digest reuse. Capture the proof work before moving
        // the exact snapshot into ordinary convergence.
        SyncReplicaFilePayloadStoreSnapshot payload_reproof =
            folder_process.payload_store_or_throw()
                .snapshot_rechecking_current_bytes_or_throw();
        const std::uint64_t hashed_entry_count =
            payload_reproof.scan_hashed_entry_count();
        const std::uint64_t hashed_bytes =
            payload_reproof.scan_hashed_bytes();
        return complete_payload_snapshot_convergence_or_throw(
            std::move(payload_reproof),
            SyncReplicaPeerServiceStepDisposition::
                OperatorPayloadRecheckCompleted,
            target_generation, hashed_entry_count, hashed_bytes);
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    operator_historical_version_step_or_throw() {
        if (!historical_version_pending()) {
            throw std::logic_error(
                label +
                " operator historical-version action lacks a pending generation");
        }
        if (!historical_version_action.has_value()) {
            throw std::logic_error(
                label + " operator historical-version action is absent");
        }
        const std::uint64_t target_generation =
            historical_version_requested_generation;
        const SyncReplicaPeerServiceHistoricalVersionAction action =
            *historical_version_action;
        historical_version_started_generation = target_generation;
        increment_saturating(counters.historical_version_attempts);

        SyncReplicaPeerServiceStepResult result = state_preserving_deferral_step(
            SyncReplicaPeerServiceStepDisposition::
                OperatorHistoricalVersionCompleted);
        result.historical_version_generation = target_generation;
        result.historical_version_action = action;
        if (action == SyncReplicaPeerServiceHistoricalVersionAction::Restore) {
            result.historical_version_restore_request =
                historical_version_restore_request;
        } else if (
            action == SyncReplicaPeerServiceHistoricalVersionAction::Pin ||
            action == SyncReplicaPeerServiceHistoricalVersionAction::Unpin) {
            result.historical_version_retention_operation_id =
                historical_version_retention_operation_id;
        }
        historical_version_last_failure_class.reset();
        historical_version_last_source_change_stage.reset();
        historical_version_last_failure.reset();
        try {
            if (action ==
                SyncReplicaPeerServiceHistoricalVersionAction::Inspect) {
                SyncReplicaHistoricalVersionInventory inventory =
                    folder_process.folder_owner_or_throw()
                        .inspect_historical_versions_or_throw(
                            historical_version_query);
                // The folder owner returns a causally complete count-bounded
                // page. Before retaining it in the fixed local-status
                // transport, apply one deterministic encoded-byte prefix.
                // The exact source cutpoint and operation-ID cursor preserve
                // reachability of every omitted successor page.
                bound_sync_replica_historical_version_inventory_for_status_or_throw(
                    inventory);
                historical_version_last_inventory = inventory;
                historical_version_last_retention_plan.reset();
                historical_version_last_restore.reset();
                historical_version_last_pin_update.reset();
                result.historical_version_inventory = std::move(inventory);
                increment_saturating(
                    counters.historical_version_inspections);
            } else if (
                action == SyncReplicaPeerServiceHistoricalVersionAction::
                    RetentionPlan) {
                SyncReplicaRetentionPlan plan =
                    folder_process.folder_owner_or_throw()
                        .plan_payload_retention_or_throw(
                            historical_version_retention_plan_query);
                bound_sync_replica_retention_plan_for_status_or_throw(plan);
                historical_version_last_inventory.reset();
                historical_version_last_retention_plan = plan;
                historical_version_last_restore.reset();
                historical_version_last_pin_update.reset();
                result.historical_version_retention_plan = std::move(plan);
                increment_saturating(
                    counters.historical_version_retention_plans);
            } else if (
                action ==
                SyncReplicaPeerServiceHistoricalVersionAction::Restore) {
                SyncReplicaHistoricalVersionRestoreResult restored =
                    folder_process.folder_owner_or_throw()
                        .restore_historical_version_or_throw(
                            historical_version_restore_request);
                historical_version_last_inventory.reset();
                historical_version_last_retention_plan.reset();
                historical_version_last_restore = restored;
                historical_version_last_pin_update.reset();
                result.historical_version_restore = std::move(restored);
                increment_saturating(counters.historical_version_restores);
            } else {
                SyncReplicaSqliteHistoricalVersionPinResult updated =
                    action == SyncReplicaPeerServiceHistoricalVersionAction::Pin
                    ? folder_process.folder_owner_or_throw()
                          .pin_historical_version_or_throw(
                              historical_version_retention_operation_id)
                    : folder_process.folder_owner_or_throw()
                          .unpin_historical_version_or_throw(
                              historical_version_retention_operation_id);
                historical_version_last_inventory.reset();
                historical_version_last_retention_plan.reset();
                historical_version_last_restore.reset();
                historical_version_last_pin_update = updated;
                result.historical_version_pin_update = std::move(updated);
                if (action ==
                    SyncReplicaPeerServiceHistoricalVersionAction::Pin) {
                    increment_saturating(counters.historical_version_pins);
                } else {
                    increment_saturating(counters.historical_version_unpins);
                }
            }
        } catch (const SyncReplicaFilePayloadStoreIntegrityError&) {
            throw;
        } catch (const SyncReplicaFilePayloadStoreLeaseBusyError&) {
            throw;
        } catch (const SyncReplicaHistoricalVersionSourceChangedError& error) {
            historical_version_last_inventory.reset();
            historical_version_last_retention_plan.reset();
            historical_version_last_restore.reset();
            historical_version_last_pin_update.reset();
            historical_version_last_failure_class =
                SyncReplicaPeerServiceHistoricalVersionFailureClass::
                    SourceChanged;
            historical_version_last_source_change_stage = error.stage();
            historical_version_last_failure = error.what();
            result.historical_version_failure_class =
                historical_version_last_failure_class;
            result.historical_version_source_change_stage =
                historical_version_last_source_change_stage;
            result.historical_version_failure = error.what();
            increment_saturating(counters.historical_version_failures);
        } catch (const std::runtime_error& error) {
            historical_version_last_inventory.reset();
            historical_version_last_retention_plan.reset();
            historical_version_last_restore.reset();
            historical_version_last_pin_update.reset();
            historical_version_last_failure_class =
                SyncReplicaPeerServiceHistoricalVersionFailureClass::
                    OperationFailed;
            historical_version_last_source_change_stage.reset();
            historical_version_last_failure = error.what();
            result.historical_version_failure_class =
                historical_version_last_failure_class;
            result.historical_version_source_change_stage.reset();
            result.historical_version_failure = error.what();
            increment_saturating(counters.historical_version_failures);
        }

        historical_version_completed_generation = target_generation;
        next_payload_store_lease_retry_at = Clock::time_point::min();
        increment_saturating(counters.historical_version_completions);
        increment_saturating(counters.steps);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    operator_payload_quarantine_step_or_throw() {
        if (!payload_quarantine_pending()) {
            throw std::logic_error(
                label +
                " operator payload quarantine lacks a pending generation");
        }
        const std::uint64_t target_generation =
            payload_quarantine_requested_generation;
        payload_quarantine_started_generation = target_generation;
        increment_saturating(counters.payload_quarantine_attempts);

        if (!payload_quarantine_action.has_value()) {
            throw std::logic_error(
                label + " operator payload quarantine lacks an action");
        }
        SyncReplicaFilePayloadStoreQuarantineResult quarantine =
            *payload_quarantine_action ==
                    SyncReplicaFilePayloadStoreQuarantineAction::Preserve
                ? folder_process.payload_store_or_throw()
                      .quarantine_corrupt_payload_or_throw(
                          payload_quarantine_expected_content_sha256,
                          payload_quarantine_observed_content_sha256)
                : folder_process.payload_store_or_throw()
                      .release_quarantined_payload_or_throw(
                          payload_quarantine_expected_content_sha256,
                          payload_quarantine_observed_content_sha256);
        if (quarantine.action ==
                SyncReplicaFilePayloadStoreQuarantineAction::Preserve &&
            quarantine.disposition ==
                SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ObservedDigestChanged) {
            record_payload_integrity_evidence_or_throw(
                quarantine.expected_content_sha256,
                quarantine.current_observed_content_sha256, false);
            increment_saturating(
                counters.payload_quarantine_observed_content_changes);
        } else if (
            quarantine.action ==
                SyncReplicaFilePayloadStoreQuarantineAction::Preserve &&
            (quarantine.disposition ==
                SyncReplicaFilePayloadStoreQuarantineDisposition::Quarantined ||
            quarantine.disposition ==
                SyncReplicaFilePayloadStoreQuarantineDisposition::PayloadAbsent ||
            quarantine.disposition ==
                SyncReplicaFilePayloadStoreQuarantineDisposition::
                    PayloadAlreadyRepaired ||
            quarantine.disposition ==
                SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ExactQuarantineAlreadyPresent)) {
            // The operator action changed or proved the faulted namespace. Let
            // the next ordinary complete convergence step establish whether
            // authority can be restored without waiting behind an old alarm
            // retry cutpoint.
            next_payload_integrity_reproof_at = Clock::time_point::min();
        }

        payload_quarantine_completed_generation = target_generation;
        payload_quarantine_last_result = quarantine;
        next_payload_store_lease_retry_at = Clock::time_point::min();
        increment_saturating(counters.payload_quarantine_completions);
        if (quarantine.disposition ==
            SyncReplicaFilePayloadStoreQuarantineDisposition::Quarantined) {
            increment_saturating(
                counters.payload_quarantine_images_preserved);
        } else if (
            quarantine.disposition ==
            SyncReplicaFilePayloadStoreQuarantineDisposition::Released) {
            increment_saturating(
                counters.payload_quarantine_images_released);
        }

        SyncReplicaPeerServiceStepResult result =
            state_preserving_deferral_step(
                SyncReplicaPeerServiceStepDisposition::
                    OperatorPayloadQuarantineCompleted);
        result.payload_quarantine_generation = target_generation;
        result.payload_quarantine_result = std::move(quarantine);
        increment_saturating(counters.steps);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult repair_step_or_throw(
        bool initial,
        bool filesystem_wake = false) {
        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        result.initial_repair = initial;
        if (filesystem_wake) attach_folder_wake(result);
        if (initial) {
            // Service readiness promises more than an empty catalog/root
            // reconciliation. A fresh payload-store owner starts with an
            // unknown diagnostic-quarantine projection, while the ordinary
            // convergence idle fast path deliberately keeps its payload
            // snapshot lazy for an actually empty folder. Take exactly one
            // complete payload-root observation at the initial-repair
            // boundary and move that cutpoint into the ordinary convergence
            // algorithm. This makes every ready process able to report the
            // complete bounded quarantine set without adding a second scan or
            // a query-time filesystem owner.
            SyncReplicaFilePayloadStoreSnapshot payload_snapshot =
                folder_process.payload_store_or_throw().snapshot_or_throw();
            result.repair.emplace(
                folder_process
                    .run_convergence_pass_with_payload_snapshot_or_throw(
                        std::move(payload_snapshot), limits.folder_limits));
            add_saturating(
                counters.initial_repair_payload_snapshot_handoffs,
                result.repair->payload_snapshot_handoff_count);
            add_saturating(
                counters.initial_repair_payload_snapshot_handoff_entries,
                result.repair->payload_snapshot_handoff_entry_count);
            add_saturating(
                counters.initial_repair_convergence_snapshot_observations,
                result.repair->payload_snapshot_observation_count);
            add_saturating(
                counters.initial_repair_convergence_mutation_full_scans,
                result.repair->payload_mutation_full_scan_count);
            if (result.repair->payload_snapshot_handoff_count != 1U ||
                result.repair->payload_snapshot_observation_count != 0U ||
                !folder_process.payload_store_or_throw()
                     .quarantine_inventory_observation_known()) {
                throw std::logic_error(
                    label +
                    " initial repair did not retain its exact complete "
                    "payload-store observation");
            }
        } else {
            result.repair.emplace(
                folder_process.run_convergence_pass_or_throw(
                    limits.folder_limits));
        }
        if (filesystem_wake) consume_folder_wake();
        initial_repair_done = true;
        next_payload_store_lease_retry_at = Clock::time_point::min();
        schedule_next_repair(Clock::now());
        result.role_after = role;
        result.disposition = initial
            ? SyncReplicaPeerServiceStepDisposition::InitialRepairCompleted
            : (filesystem_wake
                   ? SyncReplicaPeerServiceStepDisposition::
                         FilesystemWakeRepairCompleted
                   : SyncReplicaPeerServiceStepDisposition::
                         PeriodicRepairCompleted);
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        ++counters.steps;
        if (initial) {
            ++counters.initial_repairs;
        } else if (filesystem_wake) {
            ++counters.filesystem_wake_repairs;
        } else {
            ++counters.periodic_repairs;
        }
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    outbound_session_io_failure_step(
        const SyncReplicaTlsSessionIoError& error) {
        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        attach_folder_wake(result);
        result.disposition = SyncReplicaPeerServiceStepDisposition::
            OutboundSessionIoFailed;
        result.session_io_error = error.what();

        increment_saturating(consecutive_outbound_failures);
        const std::uint64_t retry = retry_delay_milliseconds(
            limits, consecutive_outbound_failures);
        next_outbound_at = add_milliseconds_or_throw(
            Clock::now(), retry, label + " outbound session-I/O retry");
        result.retry_delay_milliseconds = retry;

        // Match every bounded non-handoff result: yield to inbound service so
        // two peers cannot enter a reconnect spin after one broken session.
        role = SyncReplicaPeerServiceRole::InboundServe;
        result.role_after = role;
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        increment_saturating(counters.steps);
        increment_saturating(counters.outbound_cycles);
        increment_saturating(counters.outbound_failures);
        increment_saturating(counters.outbound_session_io_failures);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult
    inbound_session_io_failure_step(
        const SyncReplicaTlsSessionIoError& error) {
        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        result.disposition = SyncReplicaPeerServiceStepDisposition::
            InboundSessionIoFailed;
        result.session_io_error = error.what();
        if (local_recovery_initiator &&
            next_outbound_at != Clock::time_point::min() &&
            Clock::now() >= next_outbound_at) {
            role = SyncReplicaPeerServiceRole::OutboundPull;
        }
        result.role_after = role;
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        increment_saturating(counters.steps);
        increment_saturating(counters.inbound_session_io_failures);
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult outbound_step_or_throw() {
        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        attach_folder_wake(result);
        SyncReplicaSyncOnceOptions options;
        options.folder_limits = limits.folder_limits;
        options.max_round_trips = limits.max_round_trips;
        options.max_source_resets = limits.max_source_resets;
        options.stage_timeout_seconds = limits.stage_timeout_seconds;
        options.maximum_runtime_seconds = limits.cycle_runtime_seconds;
        options.command_started_at = Clock::now();
        result.outbound.emplace(
            outbound_cycle.run_once_or_throw(std::move(options)));
        if (filesystem_wake_pending) {
            consume_folder_wake();
            ++counters.filesystem_wakes_consumed_by_outbound;
        }
        const Clock::time_point completed_at = Clock::now();
        next_payload_store_lease_retry_at = Clock::time_point::min();
        schedule_next_repair(completed_at);
        result.exact_peer_observed =
            result.outbound->reconciliation.has_value() &&
            result.outbound->reconciliation->peer_authenticated &&
            result.outbound->reconciliation->peer_actor.has_value() &&
            result.outbound->reconciliation->peer_spki_sha256.has_value() &&
            *result.outbound->reconciliation->peer_actor ==
                expected_peer.actor &&
            *result.outbound->reconciliation->peer_spki_sha256 ==
                expected_peer.spki_sha256;
        result.network_turn_handed_off =
            outbound_handoff_complete(expected_peer, *result.outbound);
        if (result.network_turn_handed_off) {
            consecutive_outbound_failures = 0U;
            // A successful pull transfers the turn to the peer. The peer may
            // need its complete bounded scan/pull/apply horizon before it can
            // return the turn; accept polling cadence is not a turn lease.
            next_outbound_at = add_milliseconds_or_throw(
                completed_at, successful_handoff_lease_milliseconds(limits),
                label + " successful handoff turn lease");
            ++counters.outbound_handoffs;
        } else {
            if (consecutive_outbound_failures !=
                std::numeric_limits<std::uint64_t>::max()) {
                ++consecutive_outbound_failures;
            }
            const std::uint64_t retry = retry_delay_milliseconds(
                limits, consecutive_outbound_failures);
            next_outbound_at = add_milliseconds_or_throw(
                completed_at, retry, label + " outbound retry");
            result.retry_delay_milliseconds = retry;
            ++counters.outbound_failures;
        }
        // Every outbound attempt yields to inbound service. If the peer did not
        // observe the attempt, an idle window plus actor asymmetry recovers the
        // turn without a simultaneous redial loop.
        role = SyncReplicaPeerServiceRole::InboundServe;
        result.role_after = role;
        result.disposition =
            SyncReplicaPeerServiceStepDisposition::OutboundCycleCompleted;
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        ++counters.steps;
        ++counters.outbound_cycles;
        return result;
    }

    [[nodiscard]] SyncReplicaPeerServiceStepResult inbound_step_or_throw() {
        const Clock::time_point started_at = Clock::now();
        Clock::time_point accept_deadline = add_milliseconds_or_throw(
            started_at, limits.accept_window_milliseconds,
            label + " accept window");
        // The inotify descriptor deliberately stays on this single owner
        // thread instead of creating a watcher thread or second scheduler. A
        // configured long network poll must therefore be capped while Linux
        // wake hints are supported, or local changes could remain invisible
        // for the full accept window despite a healthy watch set. The cap also
        // gives an unavailable watcher bounded opportunities to retry.
        if (folder_wake.snapshot().platform_supported) {
            accept_deadline = std::min(
                accept_deadline,
                add_milliseconds_or_throw(
                    started_at,
                    kSyncReplicaPeerServiceMaximumFilesystemWakePollMilliseconds,
                    label + " filesystem wake poll"));
        }
        if (next_repair_at != Clock::time_point::min()) {
            accept_deadline = std::min(accept_deadline, next_repair_at);
        }
        if (local_recovery_initiator &&
            next_outbound_at != Clock::time_point::min()) {
            accept_deadline = std::min(
                accept_deadline,
                std::max(started_at, next_outbound_at));
        }

        if (!inbound_server) {
            throw std::logic_error(label + " omitted its inbound server owner");
        }
        const SyncReplicaFileTlsServerDeadlines deadlines =
            server_deadlines_or_throw(
                started_at, accept_deadline,
                limits.inbound_stage_timeout_seconds,
                label + " inbound");

        SyncReplicaPeerServiceStepResult result;
        result.role_before = role;
        if (native_i2p_ingress()) {
            if (inbound_server->has_listener()) {
                throw std::logic_error(
                    label + " native I2P ingress exposed a numeric listener");
            }
            if (!i2p_ingress_worker) {
                throw std::logic_error(
                    label + " native I2P ingress omitted its worker");
            }
            SyncReplicaI2pIngressStreamHandoff handoff =
                i2p_ingress_worker->take_stream_until_or_throw(
                    accept_deadline, label + " inbound I2P stream");
            (void)refresh_ingress_worker(false);
            if (handoff.stream.has_value()) {
                result.inbound.emplace(
                    inbound_server->serve_connected_or_throw(
                        std::move(*handoff.stream), deadlines,
                        limits.inbound_max_round_trips,
                        label + " inbound I2P session"));
            } else {
                result.inbound.emplace();
            }
        } else {
            if (!inbound_server->has_listener()) {
                throw std::logic_error(
                    label + " numeric ingress omitted its listener");
            }
            result.inbound.emplace(inbound_server->serve_one_or_throw(
                deadlines, limits.inbound_max_round_trips,
                label + " inbound session"));
        }

        const Clock::time_point completed_at = Clock::now();
        result.exact_peer_observed = exact_peer(
            expected_peer, *result.inbound);
        result.network_turn_handed_off = inbound_handoff_complete(
            expected_peer, *result.inbound);
        ++counters.steps;
        if (result.inbound->disposition ==
            SyncReplicaPeerTlsServerDisposition::AcceptDeadlineExpired) {
            result.disposition = SyncReplicaPeerServiceStepDisposition::
                InboundAcceptWindowExpired;
            ++counters.inbound_accept_windows_expired;
            if (local_recovery_initiator &&
                completed_at >= next_outbound_at) {
                role = SyncReplicaPeerServiceRole::OutboundPull;
            }
        } else {
            result.disposition =
                SyncReplicaPeerServiceStepDisposition::InboundSessionObserved;
            ++counters.inbound_sessions;
            if (result.exact_peer_observed) {
                ++counters.inbound_exact_peer_sessions;
            }
            if (result.network_turn_handed_off) {
                role = SyncReplicaPeerServiceRole::OutboundPull;
                consecutive_outbound_failures = 0U;
                next_outbound_at = completed_at;
                ++counters.inbound_handoffs;
            }
        }
        result.role_after = role;
        result.consecutive_outbound_failures =
            consecutive_outbound_failures;
        result.ingress_ready = ingress_is_ready;
        result.consecutive_ingress_failures =
            consecutive_ingress_failures;
        return result;
    }
};
SyncReplicaPeerServiceOwner::SyncReplicaPeerServiceOwner(
    SyncReplicaDeploymentManifest deployment,
    SyncReplicaFileTlsClientContext client_context,
    SyncReplicaFileTlsServerContext server_context,
    SyncReplicaStreamRoute route,
    SyncReplicaPeerIngress ingress,
    SyncReplicaTlsPeerPolicy expected_peer,
    SyncReplicaNumericStreamEndpoint listen_endpoint,
    SyncReplicaPeerServiceLimits limits,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica peer service owner label must not be empty");
    }
    validate_sync_replica_peer_service_limits_or_throw(
        limits, label + " limits");
    validate_sync_replica_peer_ingress_or_throw(
        ingress, listen_endpoint, label + " ingress");
    state_ = std::make_unique<State>(
        std::move(deployment), std::move(client_context),
        std::move(server_context), std::move(route),
        std::move(ingress), std::move(expected_peer),
        std::move(listen_endpoint),
        std::move(limits), std::move(label));
}

SyncReplicaPeerServiceOwner::~SyncReplicaPeerServiceOwner() noexcept = default;

const SyncReplicaDeploymentManifest&
SyncReplicaPeerServiceOwner::deployment() const noexcept {
    return state_->folder_process.deployment();
}

const SyncReplicaTlsPeerPolicy&
SyncReplicaPeerServiceOwner::expected_peer() const noexcept {
    return state_->expected_peer;
}

const SyncReplicaNumericStreamEndpoint&
SyncReplicaPeerServiceOwner::listen_endpoint() const noexcept {
    return state_->configured_listen_endpoint;
}

bool SyncReplicaPeerServiceOwner::has_numeric_listener() const noexcept {
    return state_->inbound_server && state_->inbound_server->has_listener();
}

SyncReplicaStreamRouteKind SyncReplicaPeerServiceOwner::route_kind()
    const noexcept {
    return state_->outbound_cycle.route_kind();
}

SyncReplicaPeerIngressKind SyncReplicaPeerServiceOwner::ingress_kind()
    const noexcept {
    return sync_replica_peer_ingress_kind(state_->ingress);
}

bool SyncReplicaPeerServiceOwner::ingress_ready() const noexcept {
    return state_->ingress_is_ready;
}

bool SyncReplicaPeerServiceOwner::ready() const {
    // Initial repair takes one complete payload-store observation and hands it
    // into ordinary convergence. Preserve/release mutation paths may revoke a
    // stale projection before their final cutpoint, so readiness also checks
    // the live allocation-free cache predicate rather than relying only on the
    // historical initial-repair bit. The predicate performs no filesystem I/O.
    return state_->initial_repair_done && state_->ingress_is_ready &&
        !state_->payload_integrity_fault.has_value() &&
        state_->folder_process.payload_store_or_throw()
            .quarantine_inventory_observation_known();
}

const SyncReplicaPeerServiceLimits& SyncReplicaPeerServiceOwner::limits()
    const noexcept {
    return state_->limits;
}

SyncReplicaPeerServiceRole SyncReplicaPeerServiceOwner::role() const noexcept {
    return state_->role;
}

bool SyncReplicaPeerServiceOwner::local_is_recovery_initiator()
    const noexcept {
    return state_->local_recovery_initiator;
}

bool SyncReplicaPeerServiceOwner::initial_repair_complete() const noexcept {
    return state_->initial_repair_done;
}

const SyncReplicaFolderWakeSnapshot&
SyncReplicaPeerServiceOwner::folder_wake_snapshot() const noexcept {
    return state_->folder_wake.snapshot();
}

const SyncReplicaPeerServiceCounters&
SyncReplicaPeerServiceOwner::counters() const noexcept {
    return state_->counters;
}

SyncReplicaFilePayloadStoreScrubStatus
SyncReplicaPeerServiceOwner::payload_scrub_status() const {
    return state_->folder_process.payload_store_or_throw().scrub_status();
}

SyncReplicaFilePayloadStoreTerminalVerificationStatus
SyncReplicaPeerServiceOwner::payload_terminal_verification_status() const {
    return state_->folder_process.payload_store_or_throw()
        .terminal_verification_status();
}

SyncReplicaReconciliationSourceManifestProjectionStatus
SyncReplicaPeerServiceOwner::source_manifest_projection_status() const {
    return state_->inbound_server->source_manifest_projection_status();
}

bool SyncReplicaPeerServiceOwner::payload_integrity_fault_active()
    const noexcept {
    return state_->payload_integrity_fault.has_value();
}

std::optional<SyncReplicaPeerServicePayloadIntegrityFault>
SyncReplicaPeerServiceOwner::payload_integrity_fault() const {
    return state_->payload_integrity_status();
}

std::optional<SyncReplicaPeerServicePayloadIntegrityRecovery>
SyncReplicaPeerServiceOwner::most_recent_payload_integrity_recovery() const {
    return state_->payload_integrity_recovery_status();
}

SyncReplicaPeerServicePayloadRecheckStatus
SyncReplicaPeerServiceOwner::payload_recheck_status() const noexcept {
    return state_->payload_recheck_status();
}

void SyncReplicaPeerServiceOwner::
observe_payload_recheck_request_generation_or_throw(
    std::uint64_t generation) {
    state_->observe_payload_recheck_request_generation_or_throw(generation);
}

SyncReplicaPeerServicePayloadQuarantineStatus
SyncReplicaPeerServiceOwner::payload_quarantine_status() const {
    SyncReplicaPeerServicePayloadQuarantineStatus status =
        state_->payload_quarantine_status();
    status.inventory =
        state_->folder_process.payload_store_or_throw()
            .quarantine_inventory_status();
    return status;
}

void SyncReplicaPeerServiceOwner::
observe_payload_quarantine_request_or_throw(
    std::uint64_t generation,
    SyncReplicaFilePayloadStoreQuarantineAction action,
    std::string expected_content_sha256,
    std::string observed_content_sha256) {
    state_->observe_payload_quarantine_request_or_throw(
        generation, action, std::move(expected_content_sha256),
        std::move(observed_content_sha256));
}

SyncReplicaPeerServiceHistoricalVersionStatus
SyncReplicaPeerServiceOwner::historical_version_status() const {
    return state_->historical_version_status();
}

void SyncReplicaPeerServiceOwner::
observe_historical_version_request_or_throw(
    std::uint64_t generation,
    SyncReplicaPeerServiceHistoricalVersionAction action,
    SyncReplicaHistoricalVersionRestoreRequest restore_request,
    SyncReplicaHistoricalVersionQuery query,
    SyncReplicaRetentionPlanQuery retention_plan_query,
    std::string retention_operation_id) {
    state_->observe_historical_version_request_or_throw(
        generation, action, std::move(restore_request), std::move(query),
        std::move(retention_plan_query),
        std::move(retention_operation_id));
}

SyncReplicaPeerServiceStepResult
SyncReplicaPeerServiceOwner::run_next_or_throw() {
    const bool operator_quarantine_pending =
        state_->payload_quarantine_pending();
    const bool operator_recheck_pending = state_->payload_recheck_pending();
    const bool operator_historical_version_pending =
        state_->historical_version_pending();
    if (state_->payload_integrity_fault.has_value() ||
        operator_recheck_pending || operator_quarantine_pending ||
        operator_historical_version_pending) {
        // Fault mode suppresses ordinary ingress events, but native I2P
        // publication still changes asynchronously. Keep its readiness and
        // retry counters current without allowing an event to preempt the
        // fail-closed backoff/reproof state machine. A healthy explicit owner
        // recheck is also scheduler-priority work: it must not wait behind an
        // ordinary network turn after the local socket accepted its generation.
        if (state_->payload_integrity_fault.has_value()) {
            (void)state_->refresh_ingress_worker(false);
        }
        const Clock::time_point now = Clock::now();
        if (!operator_quarantine_pending &&
            !operator_historical_version_pending &&
            state_->payload_integrity_fault.has_value() &&
            now < state_->next_payload_integrity_reproof_at) {
            return state_->payload_integrity_backoff_step();
        }
        if (now < state_->next_payload_store_lease_retry_at) {
            return state_->payload_store_lease_backoff_step();
        }
        const PayloadAuthorityFailureContext context =
            operator_quarantine_pending
                ? PayloadAuthorityFailureContext::OperatorQuarantine
                : (operator_historical_version_pending
                       ? PayloadAuthorityFailureContext::
                             OperatorHistoricalVersion
                       : (operator_recheck_pending
                              ? PayloadAuthorityFailureContext::OperatorRecheck
                              : PayloadAuthorityFailureContext::IntegrityReproof));
        try {
            if (operator_quarantine_pending) {
                return state_->operator_payload_quarantine_step_or_throw();
            }
            if (operator_historical_version_pending) {
                return state_->operator_historical_version_step_or_throw();
            }
            if (operator_recheck_pending) {
                return state_->operator_payload_recheck_step_or_throw();
            }
            return state_->payload_integrity_reproof_step_or_throw();
        } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
            return state_->payload_integrity_fault_step_or_throw(
                error, context);
        } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
            return state_->payload_store_lease_busy_step(error, context);
        }
    }
    if (!state_->initial_repair_done) {
        const Clock::time_point now = Clock::now();
        if (now < state_->next_payload_store_lease_retry_at) {
            return state_->payload_store_lease_backoff_step();
        }
        try {
            return state_->repair_step_or_throw(true);
        } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
            return state_->payload_integrity_fault_step_or_throw(
                error, PayloadAuthorityFailureContext::InitialRepair);
        } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
            return state_->payload_store_lease_busy_step(
                error, PayloadAuthorityFailureContext::InitialRepair);
        }
    }
    bool local_payload_scheduler_may_run = true;
    if (state_->local_payload_work_ordinary_turn_due.has_value()) {
        // The previous owner call advanced one bounded local hash frontier.
        // This call is reserved for ordinary ingress/network/watcher/repair
        // work, even when no such work is ultimately available, so neither
        // source preparation nor terminal verification can monopolize the
        // single-threaded service owner.
        switch (*state_->local_payload_work_ordinary_turn_due) {
            case State::LocalPayloadWorkKind::TerminalVerification:
                increment_saturating(
                    state_->counters
                        .payload_terminal_verification_ordinary_turn_yields);
                break;
            case State::LocalPayloadWorkKind::SourceManifestProjection:
                increment_saturating(
                    state_->counters
                        .source_manifest_projection_ordinary_turn_yields);
                break;
        }
        state_->local_payload_work_ordinary_turn_due.reset();
        local_payload_scheduler_may_run = false;
    }
    state_->observe_folder_wake_or_throw();
    if (auto event = state_->refresh_ingress_worker(true);
        event.has_value()) {
        return std::move(*event);
    }
    const Clock::time_point now = Clock::now();
    if (local_payload_scheduler_may_run &&
        now >= state_->next_payload_store_lease_retry_at) {
        const auto terminal_pending =
            state_->folder_process.payload_store_or_throw()
                .terminal_verification_status();
        const auto source_pending =
            state_->inbound_server
                ->discover_source_manifest_projection_or_throw();
        const bool terminal_available =
            terminal_pending.observation_known &&
            terminal_pending.pending_entry_count != 0U;
        const bool source_available = source_pending.pending;
        const bool select_source =
            source_available &&
            (!terminal_available ||
             state_->next_local_payload_work ==
                 State::LocalPayloadWorkKind::SourceManifestProjection);
        if (select_source) {
            try {
                return state_->source_manifest_projection_step_or_throw();
            } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
                return state_->payload_integrity_fault_step_or_throw(
                    error,
                    PayloadAuthorityFailureContext::SourceManifestProjection);
            } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
                return state_->payload_store_lease_busy_step(
                    error,
                    PayloadAuthorityFailureContext::SourceManifestProjection);
            }
        }
        if (terminal_available) {
            try {
                return state_->payload_terminal_verification_step_or_throw();
            } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
                return state_->payload_integrity_fault_step_or_throw(
                    error,
                    PayloadAuthorityFailureContext::TerminalVerification);
            } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
                return state_->payload_store_lease_busy_step(
                    error,
                    PayloadAuthorityFailureContext::TerminalVerification);
            }
        }
    }
    // A handed-off outbound turn must run before a periodic repair. The
    // bounded outbound cycle already performs its own local pass and
    // post-pull apply; inserting another full repair first duplicates work
    // and can consume the peer's turn lease on a large tree. I2P setup
    // continues independently. Payload-authority failures are caught here, not
    // by one outer state-preserving catch: the session may already have crossed
    // an externally visible turn boundary.
    if (state_->role == SyncReplicaPeerServiceRole::OutboundPull) {
        try {
            return state_->outbound_step_or_throw();
        } catch (const SyncReplicaTlsSessionIoError& error) {
            return state_->outbound_session_io_failure_step(error);
        } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
            return state_->payload_integrity_fault_step_or_throw(
                error,
                PayloadAuthorityFailureContext::OutboundNetworkStep);
        } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
            return state_->payload_store_lease_busy_step(
                error,
                PayloadAuthorityFailureContext::OutboundNetworkStep);
        }
    }
    const bool local_payload_retry_pending =
        now < state_->next_payload_store_lease_retry_at;
    if (!local_payload_retry_pending && state_->filesystem_wake_pending) {
        try {
            return state_->repair_step_or_throw(false, true);
        } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
            return state_->payload_integrity_fault_step_or_throw(
                error, PayloadAuthorityFailureContext::HealthyRepair);
        } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
            return state_->payload_store_lease_busy_step(
                error, PayloadAuthorityFailureContext::HealthyRepair);
        }
    }
    if (!local_payload_retry_pending && now >= state_->next_repair_at) {
        try {
            return state_->repair_step_or_throw(false);
        } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
            return state_->payload_integrity_fault_step_or_throw(
                error, PayloadAuthorityFailureContext::HealthyRepair);
        } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
            return state_->payload_store_lease_busy_step(
                error, PayloadAuthorityFailureContext::HealthyRepair);
        }
    }
    if (state_->native_i2p_ingress() && !state_->ingress_is_ready) {
        return state_->ingress_backoff_step();
    }
    try {
        return state_->inbound_step_or_throw();
    } catch (const SyncReplicaTlsSessionIoError& error) {
        return state_->inbound_session_io_failure_step(error);
    } catch (const SyncReplicaFilePayloadStoreIntegrityError& error) {
        return state_->payload_integrity_fault_step_or_throw(
            error, PayloadAuthorityFailureContext::InboundNetworkStep);
    } catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error) {
        return state_->payload_store_lease_busy_step(
            error, PayloadAuthorityFailureContext::InboundNetworkStep);
    }
}


}  // namespace anonsync

#endif
