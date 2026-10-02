#pragma once

#include "iotox/file_transfer.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/route_binding.hpp"
#include "iotox/route_inventory.hpp"
#include "iotox/transport.hpp"

#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <optional>
#include <span>
#include <vector>

namespace iotox::routes {

// Local egress policy for one exact auxiliary identity. The stable-device-
// signed route set already authenticates the member key and its TCP/UDP
// class; this mapping selects the host's transport context without adding a
// proxy or rendezvous endpoints to the shared signed inventory.
struct WorkerNetworkOverride {
    ToxPublicKey tox_public_key{};
    NetworkStack network{};
    std::optional<Socks5ProxyEndpoint> socks5_proxy;
    // Nonempty lists replace, rather than extend, the primary transport
    // template for this exact auxiliary identity. Empty preserves inheritance.
    // This keeps deployment-local rendezvous records out of the signed route
    // inventory while allowing native and privacy-routed workers to use
    // independently reachable Tox infrastructure.
    std::vector<toxcore::BootstrapEndpoint> bootstrap_nodes;
    std::vector<toxcore::BootstrapEndpoint> tcp_relays;

    [[nodiscard]] bool operator==(
        const WorkerNetworkOverride &) const = default;
};

// Resolve one exact worker's deployment-local transport context from the
// primary template. Endpoint lists are inherited when empty and replaced when
// explicitly populated. Keep CLI preflight and runtime worker construction on
// this single transformation so strict-route validation sees the topology that
// will actually be launched.
[[nodiscard]] ToxTransport::Config apply_worker_network_override(
    ToxTransport::Config transport_config,
    const WorkerNetworkOverride &network_override);

struct WorkerSessionSnapshot {
    MemberPolicy policy;
    NetworkStack network{};
    std::uint64_t worker_id{0U};
    bool transport_running{false};
    bool qualification_held{false};
    bool unique_peer{false};
    bool application_ready{false};
    bool hello_sent{false};
    bool hello_received{false};
    bool confirmation_sent{false};
    bool confirmation_received{false};
    std::uint32_t hello_send_attempts{0U};
    std::uint32_t confirmation_send_attempts{0U};
    bool local_binding_sent{false};
    bool remote_binding_authenticated{false};
    std::uint64_t local_binding_message_id{0U};
    std::uint64_t remote_binding_message_id{0U};
    std::uint64_t remote_route_generation{0U};
    security::SigningPublicKey remote_stable_principal{};
    ToxPublicKey remote_coordinator_route_key{};
    std::uint64_t primary_authority_online_epoch{0U};
    std::size_t sync_frame_events_queued{0U};
    std::uint64_t sync_frames_received{0U};
    std::uint64_t sync_frames_rejected{0U};
    bool range_transfer_negotiated{false};
    bool content_transfer_negotiated{false};
    std::uint64_t online_epoch{0U};
    std::uint32_t friend_number{0U};
    Failure last_failure{Failure::none};
};

struct WorkerTransferSnapshot {
    ToxPublicKey route_key{};
    std::uint64_t worker_id{0U};
    FileTransferRecord transfer;
};

enum class WorkerTransferOutcome : std::uint8_t {
    completed = 1U,
    cancelled = 2U,
    failed = 3U,
};

struct WorkerTransferTerminalEvent {
    ToxPublicKey route_key{};
    std::uint64_t worker_id{0U};
    FileTransferRecord transfer;
    WorkerTransferOutcome outcome{WorkerTransferOutcome::failed};
    ErrorCode failure{ErrorCode::ok};

    [[nodiscard]] bool operator==(
        const WorkerTransferTerminalEvent &) const = default;
};

// An auxiliary worker may carry only immutable-object, bounded-range, and
// content-v2 object/availability negotiation records. Authority and signed
// HEAD records remain on the parent Agent's primary session.
// The parent must revalidate this complete incarnation fence before applying
// the record to scheduler or publisher state.
struct WorkerSyncFrameEvent {
    ToxPublicKey route_key{};
    std::uint64_t worker_id{0U};
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    std::uint64_t remote_route_generation{0U};
    security::SigningPublicKey remote_stable_principal{};
    ToxPublicKey remote_coordinator_route_key{};
    std::uint64_t primary_authority_online_epoch{0U};
    protocol::Frame frame;
};

// Owns auxiliary Tox instances only. The authority ledger, device signer,
// route inventory, scheduling decisions, and application effects stay in the
// parent Agent. This first live slice progresses canonical application
// sessions but cannot declare a route authenticated until the parent verifies
// route-binding-v1.
class WorkerSupervisor {
  public:
    using BindingFrameFactory = std::function<Result<protocol::Frame>(
        const MemberPolicy &, const protocol::PeerSessionSnapshot &,
        std::uint64_t)>;
    using PrivateBindingFrameFactory =
        std::function<Result<protocol::Frame>(
            const MemberPolicy &, const PrivateRoutePrimaryContext &,
            const protocol::PeerSessionSnapshot &, std::uint64_t)>;

    struct Config {
        ToxTransport::Config transport_template;
        // Empty preserves exact template inheritance. Overrides are bounded,
        // unique, auxiliary-only, and completely route-validated before the
        // first worker transport starts.
        std::vector<WorkerNetworkOverride> network_overrides;
        std::filesystem::path state_root;
        RouteSet route_set;
        std::uint64_t maximum_finite_file_bytes{0U};
        std::size_t maximum_transfer_terminal_events{1024U};
        std::size_t maximum_sync_frame_events{1024U};
        // Device-signed process incarnation shared by the parent and all
        // auxiliary Tox identities for this Agent start. A strict increase
        // permits application re-handshake when a TCP relay coalesces the
        // underlying Tox online callback across process restart.
        std::uint64_t session_incarnation{0U};
        // Default-off laboratory seam. The selected exact auxiliary identity
        // advances first. Every other worker remains below the application
        // protocol until the selected worker is ready and reciprocally bound,
        // followed by this bounded hold. Transport construction and canonical
        // route-set ordering are unchanged.
        std::optional<ToxPublicKey> qualification_first_worker;
        std::chrono::milliseconds qualification_other_worker_delay{0};
        // Construction gate: disabled workers neither advertise state-sync
        // nor accept/send its application records.
        bool sync_frames_enabled{false};
        // Content-v2 is a narrower construction gate. It may be advertised
        // only when the parent has constructed both content services; HEAD
        // records are still excluded from this worker protocol.
        bool sync_content_frames_enabled{false};
        // A narrow parent-owned signing capability. An absent factory keeps
        // route-binding-v1 unadvertised and preserves the construction-only
        // worker behavior.
        BindingFrameFactory make_binding_frame;
        // Mutually exclusive privacy-preserving v2 factory. Its presence
        // advertises v1+v2 dependencies but sends no auxiliary proof until
        // replace_private_route_contexts supplies an exact, live primary
        // inventory containing that auxiliary peer.
        PrivateBindingFrameFactory make_private_binding_frame;
        const security::Sodium *sodium{nullptr};
    };

    explicit WorkerSupervisor(Config config);
    ~WorkerSupervisor();

    WorkerSupervisor(const WorkerSupervisor &) = delete;
    WorkerSupervisor &operator=(const WorkerSupervisor &) = delete;
    WorkerSupervisor(WorkerSupervisor &&) = delete;
    WorkerSupervisor &operator=(WorkerSupervisor &&) = delete;

    // Finalize the narrow content construction gate after the parent has
    // loaded namespace policy and constructed both content services. This is
    // valid only before start(); negotiated worker capability is immutable.
    [[nodiscard]] Status set_sync_content_frames_enabled(bool enabled);
    [[nodiscard]] Status start();
    void stop();
    [[nodiscard]] bool running() const noexcept;
    [[nodiscard]] std::vector<WorkerSessionSnapshot> snapshot() const;
    [[nodiscard]] Status replace_remote_trust(
        std::vector<RemoteRouteTrust> trust);
    [[nodiscard]] Status replace_private_route_contexts(
        std::vector<PrivateRoutePrimaryContext> contexts);
    [[nodiscard]] std::vector<WorkerTransferSnapshot> transfers() const;
    [[nodiscard]] Result<FileTransferRecord> receive_to_path(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        std::uint32_t file_number,
        const std::filesystem::path &destination);
    [[nodiscard]] Result<FileTransferRecord> receive_to_path_from_offset(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        std::uint32_t file_number,
        const std::filesystem::path &destination,
        std::uint64_t resume_offset);
    [[nodiscard]] Result<FileTransferRecord> send_path_with_file_id(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        const std::filesystem::path &source, const FileId &file_id);
    [[nodiscard]] Result<FileTransferRecord> send_path_ranges_with_file_id(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        const std::filesystem::path &source,
        std::span<const FileByteRange> ranges, const FileId &file_id);
    [[nodiscard]] Status cancel_transfer(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        std::uint32_t file_number);
    // Retire only the local receive resource on an exact worker incarnation.
    // Unlike cancel_transfer(), this remains valid after authentication loss
    // and never tries to send control through the dead carrier.
    [[nodiscard]] Status retire_incoming_transfer(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        std::uint32_t file_number);
    [[nodiscard]] Result<std::vector<WorkerTransferTerminalEvent>>
    take_transfer_terminal_events(std::size_t maximum_events);
    [[nodiscard]] Status send_sync_frame(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        const protocol::Frame &frame);
    [[nodiscard]] Result<std::vector<WorkerSyncFrameEvent>>
    take_sync_frame_events(std::size_t maximum_events);
    // Qualification-only fault boundary used by the genuine two-guest lab.
    // It cannot select the protected parent transport and permanently stops
    // only the named exact auxiliary incarnation.
    [[nodiscard]] Status stop_worker_for_qualification(
        const ToxPublicKey &route_key, std::uint64_t worker_id);
    // Reconstruct the exact stopped identity from savedata with a fresh
    // incarnation. The parent owns signed restart accounting and must move
    // the coordinator through recovering before accepting the returned ID.
    [[nodiscard]] Result<std::uint64_t> restart_worker_for_qualification(
        const ToxPublicKey &route_key, std::uint64_t worker_id);

    [[nodiscard]] static std::filesystem::path state_path_for(
        const std::filesystem::path &root, const ToxPublicKey &key);

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace iotox::routes
