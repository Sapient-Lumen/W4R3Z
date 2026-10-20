#pragma once

#include "iotox/interactive.hpp"
#include "iotox/protocol/ratox.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::interactive {

struct RatoxClientRoute {
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    PrincipalId principal_id{};
    bool transcript_confirmed{false};
    bool feature_negotiated{false};
    bool claimant_authenticated{false};

    [[nodiscard]] bool operator==(const RatoxClientRoute &) const = default;
};

enum class RatoxClientState : std::uint8_t {
    idle = 0U,
    opening = 1U,
    attached = 2U,
    detached = 3U,
    resuming = 4U,
    closing = 5U,
    exited = 6U,
    failed = 7U,
};

enum class RatoxClientEventKind : std::uint8_t {
    opened = 1U,
    resumed = 2U,
    output_available = 3U,
    output_gap = 4U,
    detached = 5U,
    route_lost = 6U,
    exit_status = 7U,
    closed = 8U,
    error = 9U,
    pong = 10U,
};

struct RatoxClientEvent {
    RatoxClientEventKind kind{RatoxClientEventKind::error};
    ErrorCode error_code{ErrorCode::ok};
    std::uint64_t sequence{0U};
    std::uint64_t acknowledgement{0U};
    std::uint8_t exit_kind{0U};
    bool core_dumped{false};
    std::uint16_t signal{0U};
    std::uint32_t exit_code{0U};
    std::string detail;
};

struct RatoxClientOutboundPacket {
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    PrincipalId principal_id{};
    SessionId session_id{};
    AttachmentNonce attachment_nonce{};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};
    std::uint64_t message_id{0U};
    std::uint64_t acknowledgement{0U};
    protocol::ratox::FrameType type{protocol::ratox::FrameType::open};
    std::size_t size{0U};
    std::array<std::uint8_t, protocol::ratox::kMaximumPacketBytes> storage{};

    [[nodiscard]] std::span<const std::uint8_t> bytes() const noexcept {
        return std::span<const std::uint8_t>{storage}.first(size);
    }
};

struct RatoxClientSnapshot {
    RatoxClientState state{RatoxClientState::idle};
    bool route_present{false};
    RatoxClientRoute route{};
    // Durable peer identity survives route loss so a detached session can be
    // resumed only on a fresh authenticated epoch for the same controller.
    bool peer_present{false};
    std::uint32_t peer_friend_number{0U};
    PrincipalId principal_id{};
    SessionId session_id{};
    AttachmentNonce attachment_nonce{};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};
    ReplaySnapshot input{};
    ReplaySnapshot output{};
    std::uint64_t input_send_cursor{0U};
    // One exact PING identity is reused for the lifetime of an attachment.
    // This bounds the remote never-evicted exact-control replay cost to one
    // entry even when an operator samples the attachment repeatedly.
    std::uint64_t heartbeat_message_id{0U};
    bool heartbeat_queued{false};
    std::size_t outbound_packets{0U};
    std::size_t outbound_bytes{0U};
    std::size_t retained_events{0U};
    std::size_t dropped_events{0U};
};

// Controller-side Ratox R1 state. Like RatoxService, this object owns no
// toxcore, socket, terminal, authority ledger, or wall clock. It retains every
// outbound packet until transport acceptance, every unacknowledged input byte,
// and every output byte until the local terminal acknowledges it.
class RatoxClient {
  public:
    struct Config {
        std::size_t maximum_input_bytes{64U * 1024U};
        std::size_t maximum_output_bytes{1024U * 1024U};
        std::size_t maximum_outbound_packets{256U};
        std::size_t maximum_outbound_bytes{256U * 1024U};
        std::size_t maximum_events{256U};
        std::uint64_t initial_message_id{1U};
    };

    RatoxClient();
    explicit RatoxClient(Config config);
    ~RatoxClient();

    RatoxClient(const RatoxClient &) = delete;
    RatoxClient &operator=(const RatoxClient &) = delete;
    RatoxClient(RatoxClient &&) noexcept;
    RatoxClient &operator=(RatoxClient &&) noexcept;

    [[nodiscard]] Status begin_open(
        const RatoxClientRoute &route,
        const SessionId &session_id,
        const AttachmentNonce &attachment_nonce,
        std::uint16_t columns,
        std::uint16_t rows);
    [[nodiscard]] Status begin_resume(
        const RatoxClientRoute &route,
        const AttachmentNonce &attachment_nonce);
    [[nodiscard]] Status enqueue_input(std::span<const std::uint8_t> bytes);
    [[nodiscard]] Status acknowledge_output(
        std::uint64_t next_expected_sequence);
    [[nodiscard]] Status resize(std::uint16_t columns, std::uint16_t rows);
    // Queue (or coalesce) the attachment's stable exact PING. Repeated calls
    // retransmit the byte-identical request rather than allocate new message
    // IDs, allowing the service to return its exact cached PONG without
    // growing the permanent control replay ledger.
    [[nodiscard]] Status ping();
    [[nodiscard]] Status detach();
    [[nodiscard]] Status close(std::uint16_t reason = 1U);

    [[nodiscard]] Status receive(
        const RatoxClientRoute &route,
        std::span<const std::uint8_t> packet);
    [[nodiscard]] Status peer_offline(
        std::uint32_t friend_number,
        std::uint64_t online_epoch);
    [[nodiscard]] Status service();

    [[nodiscard]] const RatoxClientOutboundPacket *peek_outbound() const noexcept;
    [[nodiscard]] Status pop_outbound();

    [[nodiscard]] Result<ReplaySlice> read_output(
        std::uint64_t next_expected_sequence,
        std::size_t maximum_bytes) const;
    [[nodiscard]] RatoxClientSnapshot snapshot() const noexcept;
    [[nodiscard]] std::vector<RatoxClientEvent> drain_events();

    void reset();

  private:
    class Impl;
    Impl *impl_{nullptr};
};

[[nodiscard]] bool is_ratox_client_inbound(
    protocol::ratox::FrameType type) noexcept;
[[nodiscard]] std::string_view to_string(RatoxClientState state) noexcept;
[[nodiscard]] std::string_view to_string(RatoxClientEventKind kind) noexcept;

}  // namespace iotox::interactive
