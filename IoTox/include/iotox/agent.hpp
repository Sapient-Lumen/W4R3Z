#pragma once

#include "iotox/command_store.hpp"
#include "iotox/diagnostics.hpp"
#include "iotox/file_transfer.hpp"
#include "iotox/interactive_service.hpp"
#include "iotox/interactive_client.hpp"
#include "iotox/peer_alias.hpp"
#include "iotox/rollback_witness.hpp"
#include "iotox/rollback_witness_service.hpp"
#include "iotox/local/runtime_tree.hpp"
#include "iotox/route_worker.hpp"
#include "iotox/status.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/sync_route_selector.hpp"
#include "iotox/sync_service.hpp"
#include "iotox/terminal_posix.hpp"
#include "iotox/transport.hpp"
#include "iotox/update_state.hpp"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace iotox {

class Agent {
  public:
    struct ProtectedStateConfig {
        // Default-off deployment boundary. When selected, every durable path
        // controlled by this Agent must live below one externally unlocked
        // fscrypt v2 policy root. IoTox never accepts the data key itself.
        bool require_fscrypt_v2{false};
        std::filesystem::path root;
        // Canonical 16-byte fscrypt-v2 master-key identifier. It is
        // not a secret; pinning it prevents an unintended encrypted root from
        // satisfying the deployment boundary.
        std::string policy_identifier;
        // The exact owner-private record used to materialize this process.
        // CLI construction fills this automatically for --config; embedding
        // callers may name their equivalent deployment-policy record.
        std::filesystem::path deployment_config_path;
    };

    struct SecurityConfig {
        std::filesystem::path sodium_library;
        std::filesystem::path device_identity_path;
        std::filesystem::path authority_ledger_path;
        // Optional embedding/deployment injection for the authenticated
        // authority freshness witness. No unauthenticated CLI endpoint is
        // exposed; production backends must report independent control.
        std::shared_ptr<rollback_witness::Backend> authority_rollback_witness;
        // Production-selectable authenticated service transport. The service
        // key is public and pinned; the existing device identity signs each
        // request. Physical/admin independence remains a deployment property.
        std::optional<rollback_witness::RemoteBackendConfig>
            authority_rollback_witness_service;
        rollback_witness::DomainId authority_rollback_witness_domain{};
        std::uint64_t authority_rollback_witness_epoch{0U};
        std::filesystem::path authority_rollback_witness_intent_path;
        // Optional additional startup-freshness lanes reuse the same pinned
        // service/domain/epoch but require distinct service enrollment and
        // same-directory signed intents.
        bool witness_application_incarnation{false};
        bool witness_ratox_incarnation{false};
        bool witness_route_generation{false};
        bool witness_terminal_policy{false};
        bool witness_command_effects{false};
        bool witness_sync_policy{false};
        bool witness_update_lifecycle{false};
        // Anchors each non-tree-v2 namespace's signed published, accepted,
        // activated, and retained roots in an independently keyed witness
        // record. The complete sync-policy lane is a mandatory prerequisite.
        bool witness_sync_guarded_state{false};
        std::filesystem::path application_incarnation_witness_intent_path;
        std::filesystem::path ratox_incarnation_witness_intent_path;
        std::filesystem::path route_generation_witness_intent_path;
        std::filesystem::path terminal_policy_witness_checkpoint_path;
        std::filesystem::path terminal_policy_witness_intent_path;
        std::filesystem::path command_effect_witness_checkpoint_path;
        std::filesystem::path command_effect_witness_intent_path;
        std::filesystem::path sync_policy_witness_checkpoint_path;
        std::filesystem::path sync_policy_witness_intent_path;
        std::filesystem::path update_lifecycle_witness_intent_path;
        bool allow_non_independent_witness_for_testing{false};
        std::filesystem::path command_store_path;
        // Stable-device-signed content-free operational tail. Empty selects
        // a savedata-scoped private path during normalization.
        std::filesystem::path diagnostics_store_path;
        // Stable-device-signed owner-local names for Tox public keys. Empty
        // selects a savedata-scoped private path during normalization.
        std::filesystem::path peer_alias_store_path;
        std::filesystem::path route_set_path;
        std::filesystem::path route_generation_state_path;
        // Device-signed process incarnation for application-session restart
        // fencing. Empty selects a private per-savedata subdirectory lane.
        std::filesystem::path protocol_incarnation_state_path;
        bool route_workers_enabled{false};
        // Default-off privacy upgrade. Full route inventories cross only the
        // authority-authenticated primary; auxiliary workers exchange fixed
        // member proofs after that primary admission exists.
        bool private_route_bindings_enabled{false};
        std::filesystem::path route_worker_state_root;
        std::vector<routes::WorkerNetworkOverride>
            route_worker_network_overrides;
        // Default-off route-readiness qualification. Both values must be
        // present together; normal worker scheduling remains canonical.
        std::optional<routes::ToxPublicKey>
            qualification_first_route_worker;
        std::chrono::milliseconds qualification_other_route_worker_delay{0};
        std::size_t maximum_authority_records{
            security::kDefaultMaximumAuthorityRecords};
        std::size_t maximum_command_records{
            kDefaultMaximumCommandRecords};
        std::size_t maximum_command_store_bytes{
            kDefaultMaximumCommandStoreBytes};
        std::size_t maximum_pending_command_records{
            kDefaultMaximumPendingCommandRecords};
        std::size_t maximum_pending_commands_per_peer{
            kDefaultMaximumPendingCommandsPerPeer};
        std::size_t maximum_command_bytes_per_peer{
            kDefaultMaximumCommandBytesPerPeer};
        std::size_t maximum_diagnostics_records{
            diagnostics::kDefaultMaximumRecords};
        bool trust_wall_clock{false};
        std::uint64_t clock_rollback_tolerance_ms{5U * 60U * 1000U};
    };

    struct InteractiveConfig {
        // A separate outer gate prevents a populated profile path or a custom
        // service limit from accidentally advertising Ratox terminal support.
        // Host-side gate: permits authenticated peers to open bounded PTYs.
        bool enabled{false};
        // Controller-side gate: creates the private terminal.sock streaming
        // surface without requiring this device to host a PTY profile.
        bool client_enabled{false};
        std::filesystem::path profile_store_root;
        // Durable signed host-incarnation ledger. Empty selects a private
        // savedata-sibling lane before any Ratox feature is advertised.
        std::filesystem::path incarnation_state_path;
        std::optional<std::uint32_t> expected_profile_owner_uid;
        std::filesystem::path helper_executable;
        std::chrono::milliseconds helper_startup_timeout{3000};
        // Optional cgroup-v2 delegation used only by the production PTY
        // factory. Empty retains pidfd/procfs session supervision.
        std::filesystem::path delegated_cgroup_root;
        // Administrator-owned host ceiling. Profile v3 may tighten or add
        // limits; exact monotone composition occurs at activation and spawn.
        terminal::CgroupResourceLimits cgroup_resource_limits;
        // Host-wide exact reservation ceiling across all live production PTY
        // sessions. Configured dimensions require finite effective
        // per-session cgroup maxima and therefore also require delegation.
        terminal::CgroupAggregateLimits cgroup_aggregate_limits;
        // Host-local PSI load-shedding gate for new PTY admissions. The
        // delegated root is sampled before reservation or process mutation.
        terminal::CgroupPressureAdmissionLimits cgroup_pressure_admission_limits;
        interactive::RatoxService::Config service{};
        interactive::RatoxClient::Config client{};
        // An attached terminal needs bounded PTY progress and inbound toxcore
        // receive cadence. These limits apply only while a host attachment or
        // local controller transition is live; the transport's ordinary
        // maximum iteration interval is restored while Ratox is idle.
        std::chrono::milliseconds active_service_interval{5};
        std::chrono::milliseconds active_transport_iteration_interval{5};
        std::vector<terminal::EnvironmentEntry> ambient_environment;

        // Dependency injection is useful for deterministic process-boundary
        // tests and alternate platform implementations. Production callers
        // normally leave this empty and configure helper_executable instead.
        std::shared_ptr<terminal::PtyProcessFactory> process_factory;
    };

    struct SyncConfig {
        // Construction gate for the synchronization protocol. Disabled is the
        // default; a path alone never activates remote service semantics.
        bool enabled{false};
        std::filesystem::path policy_store_root;
        std::size_t maximum_publisher_replays{256U};
        std::size_t maximum_subscriber_jobs{8U};
        std::size_t maximum_worker_queue{64U};
        // Content-v2 page/chunk concurrency per pull. One preserves the
        // conservative serial default; signed namespace quotas only tighten
        // this process ceiling.
        std::size_t maximum_content_lanes{1U};
        // Tree-v2 exact-object concurrency per pull. Four matches the default
        // namespace lane quota and materially reduces small-file head-of-line
        // blocking while preserving exact per-object framing.
        std::size_t maximum_tree_lanes{4U};
        // Adaptive selects only at admission or mandatory reassignment by
        // exact load/budget ratio. Fixed remains an explicit diagnostic mode.
        sync::SyncRouteSelectionPolicy route_selection_policy{
            sync::SyncRouteSelectionPolicy::adaptive};
        // Available preserves existing whole-object reassignment. Fail-closed
        // fences lost work without selecting a replacement carrier.
        sync::SyncRouteFailoverPolicy route_failover_policy{
            sync::SyncRouteFailoverPolicy::available};
        // Default-off laboratory fault seam. A nonzero value stops the first
        // exact auxiliary receive incarnation only after observing at least
        // this many but fewer than all object bytes.
        std::uint64_t qualification_stop_after_receive_bytes{0U};
        // Bounded number of sequential receive incarnations stopped by the
        // byte-threshold seam. The ordinary one-shot behavior is the default;
        // two and three exist only for repeated-loss laboratory qualification.
        // Between faults, reassigned object/range requests remain held until the
        // exact stopped identity is ready again, so the next fault begins
        // from a genuine two-carrier topology rather than winning a timer
        // race against successor completion.
        std::size_t qualification_stop_count{1U};
        // Optional exact file-size selector for the byte-threshold seam. Zero
        // preserves the historical first-eligible-receive behavior.
        std::uint64_t qualification_receive_file_bytes{0U};
        // Optional exact route-key selector for the byte-threshold seam. This
        // is laboratory targeting only: the key must name a signed auxiliary
        // bulk member, and no production scheduling rule reads it.
        std::optional<routes::ToxPublicKey>
            qualification_receive_route_key;
        // Optional bounded arm-to-stop delay for the progress-first seam.
        // This exists only to qualify cancel/loss interleavings from one
        // shared observable arm edge; zero preserves immediate faulting.
        std::chrono::milliseconds qualification_route_fault_delay{0};
        // Separate default-off ordering seam. Stop the exact carrier retained
        // by the first settled cancelled auxiliary pull, so cancellation is
        // causally complete before route loss is introduced.
        bool qualification_stop_after_cancelled_pull{false};
    };

    struct UpdateConfig {
        // Local construction gate. Delivery still uses an exact accepted sync
        // HEAD, while release intent is independently authorized by POLICY.
        bool enabled{false};
        std::filesystem::path policy_path;
        // Named Linux service deployment adapter. This must match an exact
        // linux-service-v1 policy; opaque slots can never be reinterpreted.
        bool linux_service_enabled{false};
        std::filesystem::path service_helper_executable;
        std::chrono::milliseconds service_helper_startup_timeout{3000};
        std::chrono::milliseconds service_shutdown_timeout{3000};
    };

    struct Config {
        ToxTransport::Config transport;
        FileTransferManager::Config file_transfers;
        local::RuntimeTree::Config runtime;
        SecurityConfig security;
        InteractiveConfig interactive;
        SyncConfig sync;
        UpdateConfig update;
        ProtectedStateConfig protected_state;
    };

    // Applies every side-effect-free derived path used by construction. CLI
    // preflight and the live Agent call this same normalization boundary.
    static void normalize_config(Config &config);

    explicit Agent(Config config);
    ~Agent();

    Agent(const Agent &) = delete;
    Agent &operator=(const Agent &) = delete;
    Agent(Agent &&) = delete;
    Agent &operator=(Agent &&) = delete;

    [[nodiscard]] Status start();
    void stop();

    [[nodiscard]] bool running() const noexcept;
    [[nodiscard]] bool shutdown_requested() const noexcept;
    [[nodiscard]] local::RuntimeSnapshot snapshot() const;
    [[nodiscard]] const std::filesystem::path &runtime_root() const noexcept;

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace iotox
