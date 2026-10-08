#pragma once

#if !defined(_WIN32)

#include "sync_replica_peer_service.hpp"

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::string_view kSyncReplicaPeerServiceStatusSchema =
    "anonsync.peer-service.status.v26";

// Read-only accounting derived from completed bounded service steps. This is
// presentation state, never scheduling or durable authority.
struct SyncReplicaPeerServiceLoopSummary final {
    std::uint64_t cycles_complete = 0U;
    std::uint64_t cycles_settled = 0U;
    std::uint64_t cycles_changed = 0U;
    std::uint64_t cycles_with_unresolved_paths = 0U;
    std::uint64_t cycles_partial_progress = 0U;
    std::uint64_t cycles_failed = 0U;
    std::uint64_t cycles_with_durable_progress = 0U;
    std::uint64_t accepted_sessions = 0U;
    std::uint64_t completed_handshakes = 0U;
    std::uint64_t rejected_handshakes = 0U;
    std::uint64_t unauthorized_peers = 0U;
    std::uint64_t applications_served = 0U;
    std::uint64_t file_delivery_sessions = 0U;
    std::uint64_t reconciliation_sessions = 0U;
    std::uint64_t unsupported_application_sessions = 0U;
    std::uint64_t peer_closed_sessions = 0U;
    std::uint64_t application_deadline_expirations = 0U;
    std::optional<SyncReplicaSyncOnceResult> last_cycle;
    std::optional<SyncReplicaPeerTlsServerResult> last_inbound;
    // Retains the last meaningful publication transition across ordinary
    // backoff/repair/network steps so a degraded operator status does not lose
    // the SAM stage/result that caused it. Backoff-pending steps intentionally
    // do not overwrite this event.
    std::optional<SyncReplicaPeerServiceStepResult> last_ingress_event;
    std::optional<SyncReplicaPeerServiceStepResult> last_step;
};

void account_sync_replica_peer_service_step(
    SyncReplicaPeerServiceLoopSummary& summary,
    const SyncReplicaPeerServiceStepResult& step);

// One canonical projection is shared by the live status socket and terminal
// service report. Keeping it here prevents those two operator surfaces from
// silently assigning different names or meanings to watcher health.
[[nodiscard]] std::string render_sync_replica_folder_wake_status_json(
    const SyncReplicaFolderWakeSnapshot& snapshot);

// Canonical operator projection for the generation-tracked current-byte
// recheck obligation. The live status object and terminal service report both
// embed these exact bytes so field names and completion semantics cannot drift
// between the two shipping surfaces.
// Canonical filesystem-cold projection of bounded receiver-local terminal
// SHA-256 work discovered by the last complete payload-store observation.
[[nodiscard]] std::string
render_sync_replica_file_payload_store_terminal_verification_status_json(
    const SyncReplicaFilePayloadStoreTerminalVerificationStatus& status);

// Canonical filesystem-cold projection of the process-local source manifest
// scheduler. Unlike terminal verification this state is not durable: restart
// loss is reported by absence rather than hidden behind a recovered cursor.
[[nodiscard]] std::string
render_sync_replica_source_manifest_projection_status_json(
    const SyncReplicaReconciliationSourceManifestProjectionStatus& status);

[[nodiscard]] std::string
render_sync_replica_peer_service_payload_recheck_status_json(
    const SyncReplicaPeerServicePayloadRecheckStatus& status);

// Canonical operator projection for one exact quarantine preserve-or-release
// obligation and its typed terminal store result. Retained bytes remain non-
// authoritative; this object reports explicit evidence lifecycle, not repair,
// restore, automatic retention, or garbage-collection authority.
[[nodiscard]] std::string
render_sync_replica_peer_service_payload_quarantine_status_json(
    const SyncReplicaPeerServicePayloadQuarantineStatus& status);

// Canonical live/terminal projection for the explicit bounded causal-history
// action lane and its most recent inventory, restore, or terminal refusal.
[[nodiscard]] std::string
render_sync_replica_peer_service_historical_version_status_json(
    const SyncReplicaPeerServiceHistoricalVersionStatus& status);

[[nodiscard]] std::string
render_sync_replica_file_payload_store_quarantine_result_json(
    const SyncReplicaFilePayloadStoreQuarantineResult& result);

// Produces one immutable, secret-free status snapshot. The caller may hand the
// resulting bytes to another thread; the renderer itself remains on the exact
// service-owner thread and never exports an owner or database capability.
[[nodiscard]] std::string render_sync_replica_peer_service_status_json(
    const SyncReplicaPeerServiceOwner& owner,
    const SyncReplicaPeerServiceLoopSummary& summary,
    std::uint64_t generation,
    std::chrono::steady_clock::time_point service_started_at,
    std::string_view service_state,
    std::string_view activity,
    const std::optional<std::filesystem::path>& configuration_path,
    const std::optional<std::filesystem::path>& status_socket_path,
    std::optional<std::string_view> stop_reason = std::nullopt);

}  // namespace anonsync

#endif
