#pragma once

#if !defined(_WIN32)

#include "sync_replica_folder_wake.hpp"
#include "sync_replica_peer_server_owner.hpp"
#include "sync_replica_sync_once.hpp"

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <variant>

namespace anonsync {

inline constexpr std::uint64_t
    kSyncReplicaPeerServiceMaximumAcceptWindowMilliseconds = 60000U;
inline constexpr std::uint64_t
    kSyncReplicaPeerServiceMaximumRepairIntervalMilliseconds = 3600000U;
inline constexpr std::uint64_t
    kSyncReplicaPeerServiceMaximumRetryDelayMilliseconds = 3600000U;
inline constexpr std::uint64_t
    kSyncReplicaPeerServiceMaximumIngressBackoffWaitMilliseconds = 250U;
inline constexpr std::uint64_t
    kSyncReplicaPeerServiceMaximumIntegrityBackoffWaitMilliseconds = 250U;
inline constexpr std::uint64_t
    kSyncReplicaPeerServiceMaximumPayloadStoreLeaseBackoffWaitMilliseconds =
        250U;
inline constexpr std::uint64_t
    kSyncReplicaPeerServiceMaximumFilesystemWakePollMilliseconds = 250U;
// The installed user service grants one hour for any already-started network
// owner step, plus a separate service-manager margin before forced termination.
// Durable linked-peer configurations must fit this horizon so SIGTERM can request
// a drain without pretending that systemd can interrupt SQLite/TLS work safely
// in the middle. Folder scans are bounded by configured inventory limits but are
// not yet wall-clock bounded; that remaining gap stays explicit. CMake supplies
// the same values to the installed unit; the fallbacks preserve direct builds.
#ifndef ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS
#define ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS 3600
#endif
#ifndef ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS
#define ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS 3660
#endif
inline constexpr std::uint64_t
    kSyncReplicaInstalledServiceMaximumNetworkStepSeconds =
        ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS;
inline constexpr std::uint64_t
    kSyncReplicaInstalledServiceStopTimeoutSeconds =
        ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS;

// Inbound publication is independent from the route used to dial the linked
// peer. Direct TCP owns only the retained numeric listener. Tor publication is
// external for now, but its exact onion identity is still bound to the service
// configuration and the local target must be loopback. I2P publication is
// native: a route-only worker owns retained SAM SESSION CREATE + STREAM ACCEPT
// authority and hands one exact accepted stream to this single TLS/application
// owner without exposing a same-host numeric ingress path.
enum class SyncReplicaPeerIngressKind : std::uint8_t {
    DirectTcp = 1U,
    TorOnionService = 2U,
    I2pSamAccept = 3U,
};

[[nodiscard]] std::string_view sync_replica_peer_ingress_kind_name(
    SyncReplicaPeerIngressKind kind) noexcept;

struct SyncReplicaDirectTcpIngress final {
    bool operator==(const SyncReplicaDirectTcpIngress&) const = default;
};

struct SyncReplicaTorOnionServiceIngress final {
    std::string onion_service;
    std::uint16_t service_port = 0U;

    bool operator==(
        const SyncReplicaTorOnionServiceIngress&) const = default;
};

struct SyncReplicaI2pSamIngress final {
    SyncReplicaNumericStreamEndpoint bridge;
    std::string session_id;
    std::string session_destination;
    std::uint32_t inbound_quantity = 2U;
    std::uint32_t outbound_quantity = 2U;

    bool operator==(const SyncReplicaI2pSamIngress&) const = default;
};

using SyncReplicaPeerIngress = std::variant<
    SyncReplicaDirectTcpIngress,
    SyncReplicaTorOnionServiceIngress,
    SyncReplicaI2pSamIngress>;

[[nodiscard]] SyncReplicaPeerIngressKind sync_replica_peer_ingress_kind(
    const SyncReplicaPeerIngress& ingress) noexcept;

void validate_sync_replica_peer_ingress_or_throw(
    const SyncReplicaPeerIngress& ingress,
    const SyncReplicaNumericStreamEndpoint& listen_endpoint,
    std::string_view label = "sync replica peer ingress");

// One peer service deliberately remains a single-threaded owner. The current
// operational SQLite profile is exclusive-owner oriented, so listener service,
// local scan/publication, reconciliation pull, and remote apply are serialized
// through the exact same configured-folder lifetime. The retained listener is
// still bound throughout every step and can accumulate a kernel backlog while a
// local pass or outbound session is active.
struct SyncReplicaPeerServiceLimits final {
    SyncReplicaFolderConvergencePassLimits folder_limits;
    std::uint64_t max_round_trips =
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips;
    std::uint64_t max_source_resets =
        kSyncReplicaReconciliationTlsDefaultMaxSourceResets;
    std::uint64_t stage_timeout_seconds = 10U;
    std::uint64_t cycle_runtime_seconds = 60U;
    std::uint64_t inbound_stage_timeout_seconds = 10U;
    std::uint64_t inbound_max_round_trips =
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips;
    std::uint64_t accept_window_milliseconds = 250U;
    std::uint64_t repair_interval_milliseconds = 1000U;
    std::uint64_t retry_initial_milliseconds = 100U;
    std::uint64_t retry_maximum_milliseconds = 5000U;
    std::uint64_t ingress_setup_timeout_seconds = 10U;

    bool operator==(const SyncReplicaPeerServiceLimits&) const = default;
};

void validate_sync_replica_peer_service_limits_or_throw(
    const SyncReplicaPeerServiceLimits& limits,
    std::string_view label = "sync replica peer service limits");

[[nodiscard]] std::uint64_t
sync_replica_peer_service_network_step_horizon_seconds_or_throw(
    const SyncReplicaPeerServiceLimits& limits,
    std::string_view label = "sync replica peer service network step horizon");

enum class SyncReplicaPeerServiceRole : std::uint8_t {
    OutboundPull = 1U,
    InboundServe = 2U,
};

[[nodiscard]] std::string_view sync_replica_peer_service_role_name(
    SyncReplicaPeerServiceRole role) noexcept;

enum class SyncReplicaPeerServiceStepDisposition : std::uint8_t {
    InitialRepairCompleted = 1U,
    PeriodicRepairCompleted = 2U,
    OutboundCycleCompleted = 3U,
    InboundAcceptWindowExpired = 4U,
    InboundSessionObserved = 5U,
    IngressPublicationConnected = 6U,
    IngressPublicationUnavailable = 7U,
    IngressPublicationLost = 8U,
    IngressPublicationBackoffPending = 9U,
    FilesystemWakeRepairCompleted = 10U,
    PayloadIntegrityFaultObserved = 11U,
    PayloadIntegrityReproofBackoffPending = 12U,
    PayloadIntegrityReproofCompleted = 13U,
    OutboundSessionIoFailed = 14U,
    InboundSessionIoFailed = 15U,
    PayloadStoreLeaseBusyDeferred = 16U,
    OperatorPayloadRecheckCompleted = 17U,
    OperatorPayloadQuarantineCompleted = 18U,
    OperatorHistoricalVersionCompleted = 19U,
    PayloadTerminalVerificationAdvanced = 20U,
    SourceManifestProjectionAdvanced = 21U,
};

[[nodiscard]] std::string_view sync_replica_peer_service_step_disposition_name(
    SyncReplicaPeerServiceStepDisposition disposition) noexcept;

// Immutable operator projection for the one active fail-closed payload alarm.
// Ages and retry delay are process-local monotonic observations. Durable fault
// evidence remains in the payload scrub record and is never replaced by this
// presentation object.
struct SyncReplicaPeerServicePayloadIntegrityFault final {
    std::string expected_content_sha256;
    std::string observed_content_sha256;
    // True only when durable evidence was published for the exact currently
    // reported expected/observed digest pair.
    bool failure_persisted = false;
    std::uint64_t detection_count = 0U;
    std::uint64_t observed_content_change_count = 0U;
    std::uint64_t active_age_milliseconds = 0U;
    std::uint64_t last_detection_age_milliseconds = 0U;
    std::uint64_t retry_delay_milliseconds = 0U;

    bool operator==(
        const SyncReplicaPeerServicePayloadIntegrityFault&) const = default;
};

// Immutable history for the most recently recovered payload-integrity alarm.
// Keeping the exact digests after authority is restored prevents a successful
// repair from erasing the only operator-visible explanation for the outage.
// This remains process-local presentation evidence; durable scrub state and
// current complete-byte reproof retain their existing authority boundaries.
struct SyncReplicaPeerServicePayloadIntegrityRecovery final {
    std::string expected_content_sha256;
    std::string observed_content_sha256;
    // True only when durable evidence was published for this retained exact
    // expected/observed digest pair, not merely for an older corrupt image.
    bool failure_persisted = false;
    std::uint64_t detection_count = 0U;
    std::uint64_t observed_content_change_count = 0U;
    std::uint64_t fault_duration_milliseconds = 0U;
    std::uint64_t recovery_age_milliseconds = 0U;

    bool operator==(
        const SyncReplicaPeerServicePayloadIntegrityRecovery&) const = default;
};

// Owner-thread projection of the explicit local current-byte recheck
// obligation. Generations come only from the owner-only local control socket.
// Multiple accepted requests may coalesce into one complete proof: completion
// through generation N means the exact forced-byte snapshot began only after
// every request through N had already been accepted. This is presentation and
// scheduler state, never durable payload authority.
struct SyncReplicaPeerServicePayloadRecheckStatus final {
    std::uint64_t requested_generation = 0U;
    std::uint64_t started_generation = 0U;
    std::uint64_t completed_generation = 0U;
    bool pending = false;
    std::uint64_t retry_delay_milliseconds = 0U;
    std::uint64_t last_hashed_entry_count = 0U;
    std::uint64_t last_hashed_bytes = 0U;
    std::uint64_t last_snapshot_handoff_count = 0U;
    std::uint64_t last_convergence_snapshot_observation_count = 0U;
    std::uint64_t last_convergence_mutation_full_scan_count = 0U;
    bool last_completion_recovered_integrity_fault = false;

    bool operator==(
        const SyncReplicaPeerServicePayloadRecheckStatus&) const = default;
};

// Owner-thread projection of one exact payload-quarantine request accepted by
// the local control socket. The pair remains an obligation until one bounded
// store attempt returns a typed terminal disposition; lease contention retains
// it. Quarantine preserves bytes outside authority and does not itself claim
// repair, restore, version history, or garbage collection.
struct SyncReplicaPeerServicePayloadQuarantineStatus final {
    std::uint64_t requested_generation = 0U;
    std::uint64_t started_generation = 0U;
    std::uint64_t completed_generation = 0U;
    bool pending = false;
    std::optional<SyncReplicaFilePayloadStoreQuarantineAction> action;
    std::string expected_content_sha256;
    std::string observed_content_sha256;
    std::uint64_t retry_delay_milliseconds = 0U;
    std::optional<SyncReplicaFilePayloadStoreQuarantineResult> last_result;
    // Independent of the last requested action: this is the store owner's most
    // recent complete leased view of every retained diagnostic image. A fresh
    // store owner begins unknown, but linked-peer service readiness is withheld
    // until initial repair has handed one complete store observation into
    // ordinary convergence.
    SyncReplicaFilePayloadStoreQuarantineInventoryStatus inventory;

    bool operator==(
        const SyncReplicaPeerServicePayloadQuarantineStatus&) const = default;
};

enum class SyncReplicaPeerServiceHistoricalVersionAction : std::uint8_t {
    Inspect = 1U,
    Restore = 2U,
    Pin = 3U,
    Unpin = 4U,
    RetentionPlan = 5U,
};

[[nodiscard]] std::string_view
sync_replica_peer_service_historical_version_action_name(
    SyncReplicaPeerServiceHistoricalVersionAction action) noexcept;

enum class SyncReplicaPeerServiceHistoricalVersionFailureClass
    : std::uint8_t {
    OperationFailed = 1U,
    SourceChanged = 2U,
};

[[nodiscard]] std::string_view
sync_replica_peer_service_historical_version_failure_class_name(
    SyncReplicaPeerServiceHistoricalVersionFailureClass failure_class)
    noexcept;

// One owner-thread projection of the bounded historical-version action lane.
// Inspection reports active superseded file evidence whose exact payload bytes
// are still retained. Restore publishes the selected bytes through the rooted
// folder owner and mints a new causal successor. This is not retention policy,
// wall-clock chronology, conflict resolution, or a second synchronization
// engine.
struct SyncReplicaPeerServiceHistoricalVersionStatus final {
    std::uint64_t requested_generation = 0U;
    std::uint64_t started_generation = 0U;
    std::uint64_t completed_generation = 0U;
    bool pending = false;
    std::optional<SyncReplicaPeerServiceHistoricalVersionAction> action;
    // Meaningful only for inspection. It is retained while pending and after
    // completion so an operator can bind the result/failure to the exact page.
    SyncReplicaHistoricalVersionQuery query;
    SyncReplicaRetentionPlanQuery retention_plan_query;
    SyncReplicaHistoricalVersionRestoreRequest restore_request;
    // Meaningful only for pin/unpin. A retention root names one exact
    // immutable File operation; it never names a mutable path or payload file.
    std::string retention_operation_id;
    std::uint64_t retry_delay_milliseconds = 0U;
    std::optional<SyncReplicaHistoricalVersionInventory> last_inventory;
    std::optional<SyncReplicaRetentionPlan> last_retention_plan;
    std::optional<SyncReplicaHistoricalVersionRestoreResult> last_restore;
    std::optional<SyncReplicaSqliteHistoricalVersionPinResult>
        last_pin_update;
    std::optional<SyncReplicaPeerServiceHistoricalVersionFailureClass>
        last_failure_class;
    std::optional<SyncReplicaHistoricalVersionSourceChangeStage>
        last_source_change_stage;
    std::optional<std::string> last_failure;

    bool operator==(
        const SyncReplicaPeerServiceHistoricalVersionStatus&) const = default;
};

struct SyncReplicaPeerServiceStepResult final {
    SyncReplicaPeerServiceStepDisposition disposition =
        SyncReplicaPeerServiceStepDisposition::InitialRepairCompleted;
    SyncReplicaPeerServiceRole role_before =
        SyncReplicaPeerServiceRole::InboundServe;
    SyncReplicaPeerServiceRole role_after =
        SyncReplicaPeerServiceRole::InboundServe;
    bool initial_repair = false;
    bool exact_peer_observed = false;
    bool network_turn_handed_off = false;
    // False only when a typed payload-authority failure interrupted a network
    // step after its externally visible cutpoint could no longer be recovered
    // from the stack. In that state both booleans above are deliberately
    // non-authoritative and the service applies the conservative turn fence.
    bool network_outcome_known = true;
    // Distinguishes a newly observed nonblocking flock conflict from a cheap
    // clock-only backoff step carrying the same operator disposition.
    bool payload_store_lease_conflict_observed = false;
    bool filesystem_wake_observed = false;
    bool filesystem_wake_overflow = false;
    bool filesystem_watch_rebuilt = false;
    std::uint64_t filesystem_wake_event_count = 0U;
    bool ingress_ready = false;
    std::uint64_t consecutive_outbound_failures = 0U;
    std::uint64_t retry_delay_milliseconds = 0U;
    std::uint64_t consecutive_ingress_failures = 0U;
    std::uint64_t ingress_retry_delay_milliseconds = 0U;
    std::uint64_t payload_integrity_retry_delay_milliseconds = 0U;
    std::uint64_t payload_store_lease_retry_delay_milliseconds = 0U;
    std::uint64_t payload_recheck_generation = 0U;
    std::uint64_t payload_recheck_hashed_entry_count = 0U;
    std::uint64_t payload_recheck_hashed_bytes = 0U;
    std::uint64_t payload_recheck_snapshot_handoff_count = 0U;
    std::uint64_t
        payload_recheck_convergence_snapshot_observation_count = 0U;
    std::uint64_t payload_recheck_convergence_mutation_full_scan_count = 0U;
    bool payload_recheck_recovered_integrity_fault = false;
    std::uint64_t payload_quarantine_generation = 0U;
    std::optional<SyncReplicaFilePayloadStoreQuarantineResult>
        payload_quarantine_result;
    std::uint64_t historical_version_generation = 0U;
    std::optional<SyncReplicaPeerServiceHistoricalVersionAction>
        historical_version_action;
    std::optional<SyncReplicaHistoricalVersionRestoreRequest>
        historical_version_restore_request;
    std::string historical_version_retention_operation_id;
    std::optional<SyncReplicaHistoricalVersionInventory>
        historical_version_inventory;
    std::optional<SyncReplicaRetentionPlan> historical_version_retention_plan;
    std::optional<SyncReplicaHistoricalVersionRestoreResult>
        historical_version_restore;
    std::optional<SyncReplicaSqliteHistoricalVersionPinResult>
        historical_version_pin_update;
    std::optional<SyncReplicaPeerServiceHistoricalVersionFailureClass>
        historical_version_failure_class;
    std::optional<SyncReplicaHistoricalVersionSourceChangeStage>
        historical_version_source_change_stage;
    std::optional<std::string> historical_version_failure;
    std::optional<
        SyncReplicaFilePayloadStoreTerminalVerificationStepResult>
        payload_terminal_verification;
    std::optional<
        SyncReplicaReconciliationSourceManifestProjectionStepResult>
        source_manifest_projection;
    std::optional<SyncReplicaStreamConnectReport> ingress_report;
    std::optional<std::string> ingress_error;
    std::optional<std::string> session_io_error;
    std::optional<SyncReplicaFolderConvergencePassReport> repair;
    std::optional<SyncReplicaSyncOnceResult> outbound;
    std::optional<SyncReplicaPeerTlsServerResult> inbound;

    bool operator==(const SyncReplicaPeerServiceStepResult&) const = default;
};

struct SyncReplicaPeerServiceCounters final {
    std::uint64_t steps = 0U;
    std::uint64_t initial_repairs = 0U;
    std::uint64_t initial_repair_payload_snapshot_handoffs = 0U;
    std::uint64_t initial_repair_payload_snapshot_handoff_entries = 0U;
    std::uint64_t initial_repair_convergence_snapshot_observations = 0U;
    std::uint64_t initial_repair_convergence_mutation_full_scans = 0U;
    std::uint64_t periodic_repairs = 0U;
    std::uint64_t filesystem_wake_repairs = 0U;
    std::uint64_t filesystem_wakes_consumed_by_outbound = 0U;
    std::uint64_t outbound_cycles = 0U;
    std::uint64_t outbound_handoffs = 0U;
    std::uint64_t outbound_failures = 0U;
    std::uint64_t outbound_session_io_failures = 0U;
    std::uint64_t inbound_accept_windows_expired = 0U;
    std::uint64_t inbound_sessions = 0U;
    std::uint64_t inbound_session_io_failures = 0U;
    std::uint64_t inbound_exact_peer_sessions = 0U;
    std::uint64_t inbound_handoffs = 0U;
    std::uint64_t ingress_setup_attempts = 0U;
    std::uint64_t ingress_setup_successes = 0U;
    std::uint64_t ingress_setup_failures = 0U;
    std::uint64_t ingress_losses = 0U;
    std::uint64_t ingress_backoff_deferrals = 0U;
    std::uint64_t payload_integrity_faults_observed = 0U;
    std::uint64_t payload_integrity_reproof_attempts = 0U;
    std::uint64_t payload_integrity_reproof_recoveries = 0U;
    std::uint64_t payload_integrity_reproof_snapshot_handoffs = 0U;
    std::uint64_t
        payload_integrity_reproof_convergence_snapshot_observations = 0U;
    std::uint64_t
        payload_integrity_reproof_convergence_mutation_full_scans = 0U;
    std::uint64_t payload_integrity_backoff_deferrals = 0U;
    std::uint64_t payload_store_lease_busy_deferrals = 0U;
    std::uint64_t payload_store_lease_backoff_deferrals = 0U;
    std::uint64_t payload_authority_network_outcome_uncertain_steps = 0U;
    std::uint64_t payload_terminal_verification_scheduler_steps = 0U;
    std::uint64_t payload_terminal_verification_progress_steps = 0U;
    std::uint64_t payload_terminal_verification_completions = 0U;
    std::uint64_t payload_terminal_verification_insertions = 0U;
    std::uint64_t payload_terminal_verification_reconciliations = 0U;
    std::uint64_t payload_terminal_verification_hashed_bytes = 0U;
    std::uint64_t payload_terminal_verification_ordinary_turn_yields = 0U;
    std::uint64_t source_manifest_projection_scheduler_steps = 0U;
    std::uint64_t source_manifest_projection_progress_steps = 0U;
    std::uint64_t source_manifest_projection_completions = 0U;
    std::uint64_t source_manifest_projection_payload_unavailable = 0U;
    std::uint64_t source_manifest_projection_restarts = 0U;
    std::uint64_t source_manifest_projection_hashed_bytes = 0U;
    std::uint64_t source_manifest_projection_ordinary_turn_yields = 0U;
    std::uint64_t payload_recheck_requests_observed = 0U;
    std::uint64_t payload_recheck_requests_coalesced = 0U;
    std::uint64_t payload_recheck_attempts = 0U;
    std::uint64_t payload_recheck_completions = 0U;
    std::uint64_t payload_recheck_integrity_recoveries = 0U;
    std::uint64_t payload_recheck_snapshot_handoffs = 0U;
    std::uint64_t
        payload_recheck_convergence_snapshot_observations = 0U;
    std::uint64_t payload_recheck_convergence_mutation_full_scans = 0U;
    std::uint64_t payload_quarantine_requests_observed = 0U;
    std::uint64_t payload_quarantine_requests_coalesced = 0U;
    std::uint64_t payload_quarantine_attempts = 0U;
    std::uint64_t payload_quarantine_completions = 0U;
    std::uint64_t payload_quarantine_images_preserved = 0U;
    std::uint64_t payload_quarantine_images_released = 0U;
    std::uint64_t payload_quarantine_observed_content_changes = 0U;
    std::uint64_t historical_version_requests_observed = 0U;
    std::uint64_t historical_version_requests_coalesced = 0U;
    std::uint64_t historical_version_attempts = 0U;
    std::uint64_t historical_version_completions = 0U;
    std::uint64_t historical_version_inspections = 0U;
    std::uint64_t historical_version_retention_plans = 0U;
    std::uint64_t historical_version_restores = 0U;
    std::uint64_t historical_version_pins = 0U;
    std::uint64_t historical_version_unpins = 0U;
    std::uint64_t historical_version_failures = 0U;

    bool operator==(const SyncReplicaPeerServiceCounters&) const = default;
};

// Restartable two-peer product service for one already-bootstrapped combined
// deployment. It composes, rather than duplicates, the configured-folder owner,
// sync-cycle owner, and retained peer-server owner. The lower canonical actor is
// the deterministic recovery initiator. After any failed outbound attempt it
// serves first; after an idle inbound window only that lower actor may initiate
// a new pull. A successful exact-peer request/response hands the network turn to
// the other side. This asymmetry breaks same-role recovery lockstep without
// clocks, discovery, background threads, or a second wire protocol.
//
// run_next_or_throw() performs exactly one bounded step and owns no sleep or
// signal handling. Construction and every call must remain on one thread. The
// native I2P route worker is the only exception: it receives no sync authority
// and exists solely so a minutes-long SAM tunnel build cannot freeze that owner.
class SyncReplicaPeerServiceOwner final {
public:
    SyncReplicaPeerServiceOwner(
        SyncReplicaDeploymentManifest deployment,
        SyncReplicaFileTlsClientContext client_context,
        SyncReplicaFileTlsServerContext server_context,
        SyncReplicaStreamRoute route,
        SyncReplicaPeerIngress ingress,
        SyncReplicaTlsPeerPolicy expected_peer,
        SyncReplicaNumericStreamEndpoint listen_endpoint,
        SyncReplicaPeerServiceLimits limits = {},
        std::string label = "sync replica peer service owner");
    ~SyncReplicaPeerServiceOwner() noexcept;

    SyncReplicaPeerServiceOwner(const SyncReplicaPeerServiceOwner&) = delete;
    SyncReplicaPeerServiceOwner& operator=(
        const SyncReplicaPeerServiceOwner&) = delete;
    SyncReplicaPeerServiceOwner(SyncReplicaPeerServiceOwner&&) = delete;
    SyncReplicaPeerServiceOwner& operator=(
        SyncReplicaPeerServiceOwner&&) = delete;

    [[nodiscard]] const SyncReplicaDeploymentManifest& deployment()
        const noexcept;
    [[nodiscard]] const SyncReplicaTlsPeerPolicy& expected_peer()
        const noexcept;
    // Returns the configured numeric endpoint. It is an active listener for
    // direct/Tor ingress and a schema-v2 compatibility placeholder for native
    // I2P ingress. has_numeric_listener() is the operational truth.
    [[nodiscard]] const SyncReplicaNumericStreamEndpoint& listen_endpoint()
        const noexcept;
    [[nodiscard]] bool has_numeric_listener() const noexcept;
    [[nodiscard]] SyncReplicaStreamRouteKind route_kind() const noexcept;
    [[nodiscard]] SyncReplicaPeerIngressKind ingress_kind() const noexcept;
    [[nodiscard]] bool ingress_ready() const noexcept;
    // Readiness is an owner-thread query. Besides ingress, initial repair, and
    // integrity health, it requires a complete cached diagnostic-quarantine
    // observation; the query itself performs no filesystem I/O.
    [[nodiscard]] bool ready() const;
    [[nodiscard]] const SyncReplicaPeerServiceLimits& limits() const noexcept;
    [[nodiscard]] SyncReplicaPeerServiceRole role() const noexcept;
    [[nodiscard]] bool local_is_recovery_initiator() const noexcept;
    [[nodiscard]] bool initial_repair_complete() const noexcept;
    [[nodiscard]] const SyncReplicaFolderWakeSnapshot&
    folder_wake_snapshot() const noexcept;
    [[nodiscard]] const SyncReplicaPeerServiceCounters& counters()
        const noexcept;
    [[nodiscard]] SyncReplicaFilePayloadStoreScrubStatus payload_scrub_status()
        const;
    [[nodiscard]] SyncReplicaFilePayloadStoreTerminalVerificationStatus
    payload_terminal_verification_status() const;
    [[nodiscard]]
    SyncReplicaReconciliationSourceManifestProjectionStatus
    source_manifest_projection_status() const;
    [[nodiscard]] bool payload_integrity_fault_active() const noexcept;
    [[nodiscard]] std::optional<SyncReplicaPeerServicePayloadIntegrityFault>
    payload_integrity_fault() const;
    [[nodiscard]]
    std::optional<SyncReplicaPeerServicePayloadIntegrityRecovery>
    most_recent_payload_integrity_recovery() const;
    [[nodiscard]] SyncReplicaPeerServicePayloadRecheckStatus
    payload_recheck_status() const noexcept;
    [[nodiscard]] SyncReplicaPeerServicePayloadQuarantineStatus
    payload_quarantine_status() const;
    [[nodiscard]] SyncReplicaPeerServiceHistoricalVersionStatus
    historical_version_status() const;

    // Observe the exact monotonically increasing generation accepted by the
    // owner-only local socket. A new pending obligation may bypass one existing
    // automatic retry delay so explicit operator work starts promptly. Further
    // generations coalesce without clearing active integrity/lease backoff.
    void observe_payload_recheck_request_generation_or_throw(
        std::uint64_t generation);

    // Accepts the exact generation/pair observed in the combined local action
    // snapshot. Same-pair generations coalesce; a changed pair while pending is
    // rejected as a control-plane invariant violation.
    void observe_payload_quarantine_request_or_throw(
        std::uint64_t generation,
        SyncReplicaFilePayloadStoreQuarantineAction action,
        std::string expected_content_sha256,
        std::string observed_content_sha256);

    // Accepts one exact inspection or restore request from the owner-only local
    // socket. Same requests may coalesce by generation; a changed request while
    // pending is a control-plane invariant violation.
    void observe_historical_version_request_or_throw(
        std::uint64_t generation,
        SyncReplicaPeerServiceHistoricalVersionAction action,
        SyncReplicaHistoricalVersionRestoreRequest restore_request = {},
        SyncReplicaHistoricalVersionQuery query = {},
        SyncReplicaRetentionPlanQuery retention_plan_query = {},
        std::string retention_operation_id = {});

    [[nodiscard]] SyncReplicaPeerServiceStepResult run_next_or_throw();

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
