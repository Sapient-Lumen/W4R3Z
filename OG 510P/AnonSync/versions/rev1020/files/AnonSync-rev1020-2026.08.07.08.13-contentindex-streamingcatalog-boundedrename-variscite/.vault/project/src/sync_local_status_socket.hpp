#pragma once

#if !defined(_WIN32)

#include "sync_replica_historical_version_query.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint64_t kSyncLocalStatusSocketMaximumResponseBytes =
    1024U * 1024U;
inline constexpr std::uint64_t kSyncLocalStatusSocketDefaultTimeoutMilliseconds =
    2000U;
inline constexpr std::uint64_t kSyncLocalStatusSocketMaximumTimeoutMilliseconds =
    60000U;

void validate_sync_local_status_socket_path_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string_view label = "sync local status socket");

// Verifies the normalized socket path and its already-existing parent directory.
// The parent must be an effective-user-owned directory with exact mode 0700.
// This preflight owns no socket and is safe to run before a public listener is
// exposed; construction still repeats and re-proves the same boundary.
void preflight_sync_local_status_socket_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string_view label = "sync local status socket preflight");

enum class SyncLocalStatusSocketPayloadQuarantineOperation : std::uint8_t {
    Preserve = 1,
    Release = 2,
};

struct SyncLocalStatusSocketPayloadQuarantineRequest final {
    std::uint64_t request_generation = 0U;
    std::string expected_content_sha256;
    std::string observed_content_sha256;
    SyncLocalStatusSocketPayloadQuarantineOperation operation =
        SyncLocalStatusSocketPayloadQuarantineOperation::Preserve;

    bool operator==(
        const SyncLocalStatusSocketPayloadQuarantineRequest&) const = default;
};

enum class SyncLocalStatusSocketHistoricalVersionOperation : std::uint8_t {
    Inspect = 1,
    Restore = 2,
    Pin = 3,
    Unpin = 4,
    RetentionPlan = 5,
};

struct SyncLocalStatusSocketHistoricalVersionRequest final {
    std::uint64_t request_generation = 0U;
    SyncLocalStatusSocketHistoricalVersionOperation operation =
        SyncLocalStatusSocketHistoricalVersionOperation::Inspect;
    // Used only for inspection. A path scope and exact active predecessor
    // cursor make the bounded result fully browsable without making status
    // polling perform causal or filesystem work.
    SyncReplicaHistoricalVersionQuery query;
    // Used only for the deletion-free physical retention planner. It shares
    // the history action lane but has its own exact digest cursor and query
    // identity, so a pending history page cannot coalesce with a plan page.
    SyncReplicaRetentionPlanQuery retention_plan_query;
    // Empty for inspection. Restore retains one historical selection and,
    // for the exact rev0969 frame, the sole visible operation reviewed with it.
    SyncReplicaHistoricalVersionRestoreRequest restore_request;
    // Used only for pin/unpin. The ID names exact immutable replica evidence;
    // the socket worker receives no database or payload-store capability.
    std::string retention_operation_id;

    bool operator==(
        const SyncLocalStatusSocketHistoricalVersionRequest&) const = default;
};

// One mutex-linearized observation of the local control plane. The socket
// worker may advance the recheck generation, retain one exact payload-
// quarantine obligation, retain one bounded historical-version obligation, or
// latch drain. The service owner reads all actions together so every request
// accepted before drain is observed before shutdown.
struct SyncLocalStatusSocketActionSnapshot final {
    bool stop_requested = false;
    std::uint64_t recheck_request_generation = 0U;
    std::optional<SyncLocalStatusSocketPayloadQuarantineRequest>
        payload_quarantine_request;
    std::optional<SyncLocalStatusSocketHistoricalVersionRequest>
        historical_version_request;

    bool operator==(const SyncLocalStatusSocketActionSnapshot&) const = default;
};

// Narrow owner-only local service front end. The worker thread owns only the
// Unix socket, immutable JSON bytes, one drain latch, monotonic action
// generations, and at most one exact payload-quarantine digest pair, all copied
// or changed under one mutex. It never sees SQLite owners, TLS contexts, folder
// roots, or mutable service state. "resources\n" performs one explicit Linux
// process-resource observation without entering the service owner. "stop\n"
// begins drain; "recheck\n" accepts
// a current-byte proof obligation; "quarantine EXPECTED OBSERVED\n" preserves
// one exact corrupt image; "quarantine-release EXPECTED OBSERVED\n"
// releases one exact recovered diagnostic image; "versions\n" requests the
// default bounded exact-payload causal-history projection; "versions-query
// MODE LIMIT PATH_HEX CURSOR SOURCE_CUTPOINT_OR_DASH\n" requests one exact
// query identity. MODE is exact_payload_availability or causal_metadata_only;
// the rev0967/0968 three- and four-field forms remain accepted as exact mode.
// "restore
// OPERATION_ID\n" retains the rev0966 unbound compatibility frame; and
// "restore-exact OPERATION_ID EXPECTED_CURRENT_OPERATION_ID\n" binds the
// selected value to the sole current head reviewed by the operator. Quarantine
// operations share one lane and history operations—including "version-pin
// OPERATION_ID\n", "version-unpin OPERATION_ID\n", and "retention-plan
// LIMIT CURSOR_OR_DASH SOURCE_CUTPOINT_OR_DASH\n"—share another. This is not
// a generic command dispatcher.
class SyncLocalStatusSocketServer final {
public:
    SyncLocalStatusSocketServer(
        std::filesystem::path absolute_socket_path,
        std::string initial_status_json,
        std::string label = "sync local status socket server");
    ~SyncLocalStatusSocketServer() noexcept;

    SyncLocalStatusSocketServer(const SyncLocalStatusSocketServer&) = delete;
    SyncLocalStatusSocketServer& operator=(
        const SyncLocalStatusSocketServer&) = delete;
    SyncLocalStatusSocketServer(SyncLocalStatusSocketServer&&) = delete;
    SyncLocalStatusSocketServer& operator=(
        SyncLocalStatusSocketServer&&) = delete;

    [[nodiscard]] const std::filesystem::path& path() const noexcept;
    void publish_or_throw(std::string status_json);
    void require_healthy_or_throw() const;

    // This is the sole owner-thread action observation. Keeping drain and
    // recheck generation inseparable prevents a future caller from recreating
    // the split-read shutdown race through convenience getters.
    [[nodiscard]] SyncLocalStatusSocketActionSnapshot action_snapshot() const;

    // Atomically closes action admission for owner shutdown and returns the
    // terminal action cutpoint. Every recheck linearized before this call is
    // included in the returned generation; every later recheck is rejected.
    // Status reads remain available until destruction.
    [[nodiscard]] SyncLocalStatusSocketActionSnapshot
    seal_actions_for_owner_shutdown();

    // Marks one owner-observed quarantine generation complete. A newer
    // coalesced request for the same pair remains pending; future or regressed
    // completions are rejected. This method never mutates payload bytes.
    void complete_payload_quarantine_request_or_throw(
        std::uint64_t completed_generation);

    // Marks one owner-observed historical-version generation complete. A newer
    // coalesced request for the same operation remains pending; a changed
    // request cannot occupy the lane until completion.
    void complete_historical_version_request_or_throw(
        std::uint64_t completed_generation);

    // Waits for drain or for an action newer than the caller's exact combined
    // observation. Future recheck or quarantine baselines are rejected rather
    // than turning an owner-generation bug into fallback sleep latency.
    [[nodiscard]] bool wait_for_action_request_or_timeout(
        const SyncLocalStatusSocketActionSnapshot& observed_actions,
        std::uint64_t timeout_milliseconds);

private:
    struct State;
    std::unique_ptr<State> state_;
};

// Sends the exact read-only request "status\n", reads one bounded JSON line,
// verifies it is an object, and returns the JSON bytes without the terminal
// newline. On Linux, when the object contains a numeric pid, that pid must
// match the process actually serving the connected Unix socket.
[[nodiscard]] std::string query_sync_local_status_socket_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local status query");

// Sends the exact read-only request "resources\n". The socket worker performs
// one bounded Linux smaps_rollup/rusage/fd/thread observation and returns a
// strictly validated PID-bound JSON object. Ordinary status publication stays
// free of procfs traversal and measurement cost.
[[nodiscard]] std::string query_sync_local_process_resources_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local process resources query");

// Sends the only mutating local request, "stop\n". The server atomically latches
// a graceful drain request and returns one strictly validated JSON response.
// Repeated requests are idempotent and report first_request=false.
[[nodiscard]] std::string request_sync_local_status_stop_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local stop request");

// Sends "recheck\n" and validates the PID-bound structured response. An
// accepted response advances one monotonic generation; a request serialized
// after drain is rejected without advancing it. Acceptance is not completion.
[[nodiscard]] std::string request_sync_local_status_recheck_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local recheck request");

// Sends one exact digest-pair request. Only one pair may remain pending; repeat
// requests for that pair coalesce by generation, while a different pair is
// rejected until the owner reports completion. Acceptance preserves bytes but
// is not itself quarantine completion.
[[nodiscard]] std::string request_sync_local_status_payload_quarantine_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string expected_content_sha256,
    std::string observed_content_sha256,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local payload quarantine request");

// Sends the exact release operation for one retained diagnostic pair. The
// response is only owner-thread admission; status reports the typed terminal
// store result. Release shares the same single pending quarantine-action lane.
[[nodiscard]] std::string
request_sync_local_status_payload_quarantine_release_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string expected_content_sha256,
    std::string observed_content_sha256,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local payload quarantine release request");

// Requests one bounded inspection of retained active file predecessors. The
// response acknowledges admission only; status reports the resulting inventory.
[[nodiscard]] std::string
request_sync_local_status_historical_versions_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local historical versions request");

// Path-scoped/cursor-paginated form. The exact query participates in request
// coalescing, so a different page cannot overwrite one already accepted. The
// legacy no-query helper above remains the default 64-entry global request.
[[nodiscard]] std::string
request_sync_local_status_historical_versions_query_or_throw(
    const std::filesystem::path& absolute_socket_path,
    SyncReplicaHistoricalVersionQuery query,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local historical versions query");

// Retains the rev0966 unbound restore request for local protocol
// compatibility. New product callers should use the exact-current helper.
[[nodiscard]] std::string
request_sync_local_status_historical_version_restore_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string operation_id,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local historical version restore request");

// Requests restoration of one exact active non-visible file operation only if
// the path still has the exact sole current operation returned by inspection.
// The response acknowledges admission only; the owner re-proves and publishes.
[[nodiscard]] std::string
request_sync_local_status_historical_version_restore_exact_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string operation_id,
    std::string expected_current_operation_id,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label =
        "sync local exact historical version restore request");

// Requests one durable local retention-root transition over exact immutable
// File evidence. Admission is not completion; peer-service status reports the
// typed SQLite-owner result and resulting canonical pin-set digest.
// Requests one exact, deletion-free physical payload plan page. Admission is
// not completion; peer-service status carries the bounded result and exact v4
// source cutpoint. The operation has no quota, grace, quarantine, or unlink
// authority.
[[nodiscard]] std::string
request_sync_local_status_retention_plan_or_throw(
    const std::filesystem::path& absolute_socket_path,
    SyncReplicaRetentionPlanQuery query = {},
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local retention plan request");

[[nodiscard]] std::string
request_sync_local_status_historical_version_pin_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string operation_id,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local historical version pin request");

[[nodiscard]] std::string
request_sync_local_status_historical_version_unpin_or_throw(
    const std::filesystem::path& absolute_socket_path,
    std::string operation_id,
    std::uint64_t timeout_milliseconds =
        kSyncLocalStatusSocketDefaultTimeoutMilliseconds,
    std::string_view label = "sync local historical version unpin request");

}  // namespace anonsync

#endif
