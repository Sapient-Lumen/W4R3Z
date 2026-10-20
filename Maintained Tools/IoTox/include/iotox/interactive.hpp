#pragma once

#include "iotox/status.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <optional>
#include <span>
#include <vector>

namespace iotox::interactive {

// Fixed, unadvertised diagnostic echo packets used only to qualify candidate
// Ratox carriers. They are deliberately outside the IoTox 1.0 frame ID (0xA0)
// and carry no terminal data or authority.
inline constexpr std::uint8_t kLosslessProbePacketId = 0xA1U;
// 0xC0..0xC7 are reserved to ToxAV; c-toxcore's compatibility callback
// exposes the custom application range beginning at 0xC8.
inline constexpr std::uint8_t kLossyProbePacketId = 0xC8U;
inline constexpr std::size_t kProbePacketSize = 10U;
inline constexpr std::size_t kMaximumResearchProbePacketSize = 1200U;

enum class ProbeCarrier : std::uint8_t {
    lossless = 1U,
    lossy = 2U,
};

enum class ProbeKind : std::uint8_t {
    request = 1U,
    reply = 2U,
};

struct ProbePacket {
    ProbeCarrier carrier{ProbeCarrier::lossless};
    ProbeKind kind{ProbeKind::request};
    std::uint64_t nonce{0U};
};

[[nodiscard]] Result<std::array<std::uint8_t, kProbePacketSize>>
encode_probe(const ProbePacket &packet);
[[nodiscard]] Result<ProbePacket> decode_probe(
    std::span<const std::uint8_t> bytes, ProbeCarrier carrier);
// Sized probes preserve the fixed ten-byte header and add deterministic,
// nonce-bound padding. Replies have exactly the request size, so this remains
// a non-amplifying local research instrument while exercising realistic Ratox
// packet pressure.
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_sized_probe(
    const ProbePacket &packet, std::size_t packet_size);
[[nodiscard]] Result<ProbePacket> decode_sized_probe(
    std::span<const std::uint8_t> bytes, ProbeCarrier carrier);

using SessionId = std::array<std::uint8_t, 16U>;
using AttachmentNonce = std::array<std::uint8_t, 16U>;
using PrincipalId = std::array<std::uint8_t, 32U>;

struct AttachmentToken {
    SessionId session_id{};
    PrincipalId principal_id{};
    AttachmentNonce nonce{};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};

    [[nodiscard]] bool operator==(const AttachmentToken &) const = default;
};

// One terminal/session owner uses this object to fence delayed input from an
// older connection. It deliberately has no transport or wire-format knowledge.
// A successful attach advances the generation even for the same principal.
class AttachmentFence {
  public:
    AttachmentFence(
        SessionId session_id, std::uint64_t incarnation,
        std::uint64_t initial_generation = 0U);

    [[nodiscard]] Result<AttachmentToken> attach(
        PrincipalId principal_id, AttachmentNonce nonce);
    [[nodiscard]] Status validate(const AttachmentToken &token) const;
    [[nodiscard]] Status detach(const AttachmentToken &token);
    [[nodiscard]] Status replace_incarnation();
    void invalidate() noexcept;
    [[nodiscard]] const std::optional<AttachmentToken> &current() const noexcept;

    [[nodiscard]] bool attached() const noexcept;
    [[nodiscard]] std::uint64_t generation() const noexcept;
    [[nodiscard]] const SessionId &session_id() const noexcept;
    [[nodiscard]] std::uint64_t incarnation() const noexcept;

  private:
    SessionId session_id_{};
    std::uint64_t incarnation_{0U};
    std::uint64_t generation_{0U};
    std::optional<AttachmentToken> current_;
};

struct ReplaySlice {
    std::uint64_t first_sequence{0U};
    std::uint64_t next_sequence{0U};
    bool complete{false};
    std::vector<std::uint8_t> bytes;
};

struct ReplaySnapshot {
    std::uint64_t base_sequence{0U};
    std::uint64_t next_sequence{0U};
    std::size_t pending_bytes{0U};
    std::size_t maximum_bytes{0U};
};

// A cumulative byte sequence for latency-sensitive input and reconnect catchup.
// Acknowledged prefixes are released. Unacknowledged input is never evicted:
// append returns resource_exhausted instead of silently losing a keystroke.
class ByteReplayWindow {
  public:
    struct Config {
        std::size_t maximum_bytes{64U * 1024U};
        std::uint64_t initial_sequence{1U};
    };

    ByteReplayWindow();
    explicit ByteReplayWindow(Config config);
    ~ByteReplayWindow();

    ByteReplayWindow(const ByteReplayWindow &) = default;
    ByteReplayWindow &operator=(const ByteReplayWindow &other);
    ByteReplayWindow(ByteReplayWindow &&other) noexcept;
    ByteReplayWindow &operator=(ByteReplayWindow &&other) noexcept;

    [[nodiscard]] Result<std::uint64_t> append(
        std::span<const std::uint8_t> bytes);
    [[nodiscard]] Status acknowledge(std::uint64_t next_expected_sequence);
    [[nodiscard]] Result<ReplaySlice> replay_from(
        std::uint64_t next_expected_sequence, std::size_t maximum_bytes) const;
    [[nodiscard]] ReplaySnapshot snapshot() const noexcept;

  private:
    Config config_;
    std::uint64_t base_sequence_{0U};
    std::uint64_t next_sequence_{0U};
    std::deque<std::uint8_t> bytes_;
};

enum class InputDisposition : std::uint8_t {
    staged = 1U,
    pending = 2U,
    duplicate = 3U,
    future_gap = 4U,
};

struct InputOfferResult {
    InputDisposition disposition{InputDisposition::staged};
    std::uint64_t acknowledgement{0U};
};

struct InputConsumeResult {
    std::uint64_t acknowledgement{0U};
    std::size_t remaining_bytes{0U};
    bool committed{false};
};

struct InputReceiverSnapshot {
    std::uint64_t next_expected_sequence{0U};
    std::uint64_t staged_sequence{0U};
    std::size_t staged_bytes{0U};
    std::size_t consumed_bytes{0U};
    std::size_t maximum_frame_bytes{0U};
    bool terminal_failure{false};
};

// Receiver-side at-most-once byte commitment. One exact-next frame is staged
// while a nonblocking sink consumes it. The cumulative acknowledgement moves
// only after whole-frame completion; a sink failure makes this incarnation
// terminal so uncertain partial bytes cannot be replayed into a replacement.
class InputReceiver {
  public:
    struct Config {
        std::size_t maximum_frame_bytes{1076U};
        std::uint64_t initial_sequence{1U};
    };

    InputReceiver();
    explicit InputReceiver(Config config);
    ~InputReceiver();

    InputReceiver(const InputReceiver &) = default;
    InputReceiver &operator=(const InputReceiver &other);
    InputReceiver(InputReceiver &&other) noexcept;
    InputReceiver &operator=(InputReceiver &&other) noexcept;

    [[nodiscard]] Result<InputOfferResult> offer(
        std::uint64_t sequence, std::span<const std::uint8_t> bytes);
    [[nodiscard]] Result<std::vector<std::uint8_t>> pending_bytes() const;
    [[nodiscard]] Result<InputConsumeResult> consume_staged(std::size_t bytes);
    [[nodiscard]] Status fail_staged();
    [[nodiscard]] InputReceiverSnapshot snapshot() const noexcept;

  private:
    [[nodiscard]] Status validate_config() const;

    Config config_;
    std::uint64_t next_expected_sequence_{0U};
    std::uint64_t staged_sequence_{0U};
    std::vector<std::uint8_t> staged_bytes_;
    std::size_t consumed_bytes_{0U};
    bool terminal_failure_{false};
};

enum class OutputReadKind : std::uint8_t {
    data = 1U,
    gap = 2U,
};

struct OutputReadResult {
    OutputReadKind kind{OutputReadKind::data};
    std::uint64_t requested_sequence{0U};
    std::uint64_t first_sequence{0U};
    std::uint64_t next_sequence{0U};
    std::uint64_t produced_next_sequence{0U};
    bool complete{false};
    std::vector<std::uint8_t> bytes;
};

struct OutputHistorySnapshot {
    std::uint64_t base_sequence{0U};
    std::uint64_t next_sequence{0U};
    std::size_t retained_bytes{0U};
    std::size_t maximum_bytes{0U};
};

// Receiver-side PTY output history. New output is always sequenced; excess
// history evicts the oldest prefix. A reader asking before the retained base
// receives an explicit gap with both retained-base and produced-next bounds.
class OutputHistory {
  public:
    struct Config {
        std::size_t maximum_bytes{1024U * 1024U};
        std::uint64_t initial_sequence{1U};
    };

    OutputHistory();
    explicit OutputHistory(Config config);
    ~OutputHistory();

    OutputHistory(const OutputHistory &) = default;
    OutputHistory &operator=(const OutputHistory &other);
    OutputHistory(OutputHistory &&other) noexcept;
    OutputHistory &operator=(OutputHistory &&other) noexcept;

    [[nodiscard]] Result<std::uint64_t> append(
        std::span<const std::uint8_t> bytes);
    [[nodiscard]] Status acknowledge(std::uint64_t next_expected_sequence);
    [[nodiscard]] Result<OutputReadResult> read_from(
        std::uint64_t next_expected_sequence, std::size_t maximum_bytes) const;
    [[nodiscard]] OutputHistorySnapshot snapshot() const noexcept;

  private:
    [[nodiscard]] Status validate_config() const;

    Config config_;
    std::uint64_t base_sequence_{0U};
    std::uint64_t next_sequence_{0U};
    std::deque<std::uint8_t> bytes_;
};

struct RttSnapshot {
    std::uint64_t sample_count{0U};
    std::uint64_t latest_us{0U};
    std::uint64_t minimum_us{0U};
    std::uint64_t smoothed_us{0U};
    std::uint64_t variation_us{0U};
    std::uint64_t retransmission_timeout_us{0U};
};

// Monotonic round-trip estimator. It uses the familiar 1/8 SRTT and 1/4
// variation gains, but makes no wall-clock or transport-retransmission claim.
class RttEstimator {
  public:
    struct Config {
        std::chrono::microseconds minimum_rto{std::chrono::milliseconds(50)};
        std::chrono::microseconds maximum_rto{std::chrono::seconds(5)};
    };

    RttEstimator();
    explicit RttEstimator(Config config);

    [[nodiscard]] Status observe(std::chrono::microseconds round_trip);
    [[nodiscard]] RttSnapshot snapshot() const noexcept;

  private:
    Config config_;
    RttSnapshot snapshot_{};
};

}  // namespace iotox::interactive
