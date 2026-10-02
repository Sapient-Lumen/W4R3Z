#pragma once

#include "iotox/interactive_session.hpp"
#include "iotox/protocol/ratox.hpp"
#include "iotox/terminal_process.hpp"
#include "iotox/terminal_profile.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace iotox::interactive {

// The Agent supplies this context from one transcript-confirmed online epoch
// and one exact-head authority decision. Friend numbers are routing handles,
// never durable identity.
struct RatoxPeerContext {
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    PrincipalId principal_id{};
    bool transcript_confirmed{false};
    bool feature_negotiated{false};
    bool terminal_authorized{false};
};

enum class RatoxTrafficClass : std::uint8_t {
    interactive = 1U,
    control = 2U,
};

// Fixed packet storage lets a control reserve its complete outbound result
// before a PTY, attachment, resize, or shutdown side effect is admitted.
struct RatoxOutboundPacket {
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    SessionId session_id{};
    PrincipalId principal_id{};
    // True for every packet whose creation depended on live interactive-
    // terminal authority. The Agent revalidates this fence immediately before
    // transport admission. Explicit DENIED admission replies are false so an
    // authenticated but unauthorized peer can receive a bounded rejection.
    bool terminal_authority_required{true};
    std::uint64_t generation{0U};
    protocol::ratox::FrameType type{protocol::ratox::FrameType::open_result};
    RatoxTrafficClass traffic_class{RatoxTrafficClass::control};
    std::uint64_t sequence{0U};
    std::uint64_t next_sequence{0U};
    std::size_t size{0U};
    std::array<std::uint8_t, protocol::ratox::kMaximumPacketBytes> storage{};

    [[nodiscard]] std::span<const std::uint8_t> bytes() const noexcept {
        return std::span<const std::uint8_t>{storage}.first(size);
    }
};

enum class RatoxServiceEventKind : std::uint8_t {
    packet_rejected = 1U,
    open_denied = 2U,
    opened = 3U,
    attached = 4U,
    resumed = 5U,
    detached = 6U,
    input_staged = 7U,
    input_committed = 8U,
    input_rejected = 9U,
    output_appended = 10U,
    output_gap = 11U,
    resize_applied = 12U,
    peer_detached = 13U,
    authority_revoked = 14U,
    close_started = 15U,
    process_exited = 16U,
    process_failed = 17U,
    session_finalized = 18U,
    replayed = 19U,
    outbound_backpressure = 20U,
    shutdown_started = 21U,
};

// Audit records deliberately contain no terminal bytes, argv, environment,
// profile ID, cwd, or error string. They expose only bounded lifecycle facts.
struct RatoxServiceEvent {
    std::uint64_t ordinal{0U};
    // Monotonic microseconds since this service instance was constructed.
    // Zero is reserved as an unavailable sentinel; values are clamped so the
    // bounded journal never moves backwards even when multiple events land in
    // the same steady-clock tick.
    std::uint64_t steady_time_us{0U};
    RatoxServiceEventKind kind{RatoxServiceEventKind::packet_rejected};
    ErrorCode error_code{ErrorCode::ok};
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    SessionId session_id{};
    PrincipalId principal_id{};
    protocol::ratox::FrameType frame_type{protocol::ratox::FrameType::open};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};
    // Event-specific protocol coordinates. These fields deliberately retain
    // positions and sizes only; terminal bytes remain absent. For INPUT they
    // identify the exact admitted or committed frame span. For OUTPUT they
    // identify the exact PTY append span. A zero message ID is the sentinel
    // for events that are not correlated to one inbound Ratox frame.
    std::uint64_t message_id{0U};
    std::uint64_t sequence{0U};
    std::uint64_t next_sequence{0U};
    std::uint64_t event_bytes{0U};
    std::uint64_t next_input_sequence{0U};
    std::uint64_t output_base_sequence{0U};
    std::uint64_t output_next_sequence{0U};
};

struct RatoxServiceSnapshot {
    bool enabled{false};
    bool configuration_valid{false};
    std::size_t sessions{0U};
    std::size_t live_sessions{0U};
    std::size_t retained_session_tombstones{0U};
    std::size_t running_processes{0U};
    std::size_t attached_sessions{0U};
    std::size_t closing_sessions{0U};
    std::size_t retained_admission_results{0U};
    std::size_t pending_admission_results{0U};
    std::size_t admission_replay_bytes{0U};
    std::size_t outbound_packets{0U};
    std::size_t outbound_bytes{0U};
    std::size_t retained_events{0U};
    std::size_t dropped_events{0U};
    std::size_t maximum_sessions{0U};
    std::size_t maximum_session_tombstones{0U};
    std::size_t maximum_admission_replay_entries{0U};
    std::size_t maximum_admission_replay_bytes{0U};
    std::size_t maximum_outbound_packets{0U};
    std::size_t maximum_outbound_bytes{0U};
    bool session_bound_respected{false};
    bool tombstone_bound_respected{false};
    bool admission_replay_entry_bound_respected{false};
    bool admission_replay_byte_bound_respected{false};
    bool outbound_packet_bound_respected{false};
    bool outbound_byte_bound_respected{false};
};

// R4's transport-independent coordinator. It joins the pure R1 session model,
// locally resolved R3 profiles, and the PTY controller. It does not own
// toxcore, authority state, feature negotiation, wall clock, or a network
// thread. The Agent must supply a fresh RatoxPeerContext for every packet.
class RatoxService {
  public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    struct Config {
        // Deliberately false in default construction. The Agent may set this
        // only after explicit pre-network construction activation; R8 remains
        // the production-support gate.
        bool enabled{false};
        bool require_feature_negotiation{true};
        // Reserved before transport startup and persisted across daemon
        // restarts. Zero is the fail-closed, unreserved protocol sentinel and
        // is never admitted; every enabled caller must inject a lease value.
        std::uint64_t session_incarnation{0U};
        SessionDirectory::Config directory{};
        // Closed sessions retain exact control outcomes only until the owning
        // online epoch ends. This bound must cover every simultaneously live
        // session so shutdown/failure can always publish a tombstone without
        // allocating or dropping replay state.
        std::size_t maximum_session_tombstones{64U};
        std::size_t maximum_admission_replay_entries{64U};
        // One admission retains at most a 140-byte ATTACH/RESUME request plus
        // one complete 1200-byte result reservation. Keep the byte ceiling
        // coherent with the entry ceiling instead of implying unusable slack.
        std::size_t maximum_admission_replay_bytes{
            64U * (protocol::ratox::kHeaderBytes + 16U +
                   protocol::ratox::kMaximumPacketBytes)};
        std::size_t maximum_outbound_packets{256U};
        std::size_t maximum_outbound_bytes{256U * 1024U};
        std::size_t maximum_events{256U};
        std::size_t maximum_input_write_operations{32U};
        std::size_t maximum_output_read_operations{32U};
        std::size_t maximum_output_frames{32U};
        std::size_t terminal_read_bytes{64U * 1024U};
        std::chrono::milliseconds exit_output_drain_timeout{2000};
        std::uint64_t initial_outbound_message_id{1U};
    };

    RatoxService(
        terminal::ProfileRegistry &profiles,
        terminal::PtyProcessFactory &processes);
    RatoxService(
        terminal::ProfileRegistry &profiles,
        terminal::PtyProcessFactory &processes,
        Config config,
        std::vector<terminal::EnvironmentEntry> ambient_environment = {});
    ~RatoxService();

    RatoxService(const RatoxService &) = delete;
    RatoxService &operator=(const RatoxService &) = delete;
    RatoxService(RatoxService &&) = delete;
    RatoxService &operator=(RatoxService &&) = delete;

    // Decode, authenticate the supplied routing context, reserve replay state,
    // and apply at most one inbound frame. Accepted PTY input remains staged;
    // service() alone performs nonblocking process I/O.
    [[nodiscard]] Status receive(
        const RatoxPeerContext &peer,
        std::span<const std::uint8_t> packet,
        TimePoint now);

    // Bounded, nonblocking progress. Outbound packets remain retained until the
    // caller reports transport acceptance by pop_outbound(). SENDQ rejection
    // therefore requires no state rollback and loses no packet.
    [[nodiscard]] Status service(TimePoint now);

    [[nodiscard]] const RatoxOutboundPacket *peek_outbound() const noexcept;
    [[nodiscard]] Status pop_outbound();

    // An online-epoch loss fences only the attachment routed through that
    // epoch; its PTY remains alive for a future ATTACH/RESUME.
    [[nodiscard]] Status peer_offline(
        std::uint32_t friend_number,
        std::uint64_t online_epoch,
        TimePoint now);

    // Exact authority loss starts a fail-closed process shutdown and fences new
    // input before another PTY write. Other principals and epochs are untouched.
    [[nodiscard]] Status authority_revoked(
        std::uint32_t friend_number,
        std::uint64_t online_epoch,
        const PrincipalId &principal_id,
        TimePoint now);

    // Revokes every still-live session owned by one durable principal,
    // including sessions detached from a transport epoch. Retained packets
    // and admission replay state for that principal are discarded before
    // process shutdown starts, so a later regrant cannot replay pre-revocation
    // terminal authority or terminal bytes.
    [[nodiscard]] Status principal_revoked(
        const PrincipalId &principal_id,
        TimePoint now);

    // Metadata-only ownership view used by the Agent to reconcile detached
    // sessions against a newly committed authority head. Principal IDs are
    // unique in the returned vector; terminal bytes and session IDs are never
    // exposed by this method.
    [[nodiscard]] std::vector<PrincipalId> live_principals() const;

    // Starts bounded HUP/TERM/KILL shutdown for every live process. This method
    // is idempotent; callers continue service() until running_processes is zero.
    [[nodiscard]] Status shutdown(TimePoint now);

    [[nodiscard]] RatoxServiceSnapshot snapshot() const noexcept;
    [[nodiscard]] std::span<const RatoxServiceEvent> events() const noexcept;
    [[nodiscard]] std::vector<RatoxServiceEvent> drain_events();

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

[[nodiscard]] std::string_view to_string(RatoxServiceEventKind value) noexcept;

}  // namespace iotox::interactive
