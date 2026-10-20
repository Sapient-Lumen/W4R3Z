#pragma once

#include "iotox/interactive.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <chrono>
#include <cstdint>
#include <deque>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace iotox::protocol::ratox {

// Ratox v1 occupies a distinct c-toxcore custom-lossless packet ID. The
// diagnostic probe remains on 0xA1 and the ordinary IoTox protocol on 0xA0.
inline constexpr std::uint8_t kPacketId = 0xA2U;
inline constexpr std::uint8_t kMajor = 1U;
inline constexpr std::uint8_t kMinor = 0U;
inline constexpr std::size_t kHeaderBytes = 124U;
inline constexpr std::size_t kMaximumPacketBytes = 1200U;
inline constexpr std::size_t kMaximumPayloadBytes =
    kMaximumPacketBytes - kHeaderBytes;
// Reserved for authority-ledger v2. Authority v1 deliberately rejects this
// bit, so framing can be reviewed without accidentally granting remote PTY
// power before an explicit signed-ledger migration exists.
inline constexpr std::uint64_t kTerminalAuthorityCapabilityBit = 1ULL << 7U;

enum class FrameType : std::uint8_t {
    open = 1U,
    open_result = 2U,
    attach = 3U,
    attach_result = 4U,
    detach = 5U,
    input = 6U,
    input_ack = 7U,
    output = 8U,
    output_ack = 9U,
    resize = 10U,
    ping = 11U,
    pong = 12U,
    close = 13U,
    exit_status = 14U,
    resume = 15U,
    resume_result = 16U,
    output_gap = 17U,
};

struct Frame {
    FrameType type{FrameType::open};
    std::uint64_t message_id{0U};
    std::uint64_t correlation_id{0U};
    interactive::SessionId session_id{};
    interactive::PrincipalId principal_id{};
    interactive::AttachmentNonce attachment_nonce{};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};
    std::uint64_t sequence{0U};
    std::uint64_t acknowledgement{0U};
    std::vector<std::uint8_t> payload;

    [[nodiscard]] bool operator==(const Frame &) const = default;
};

[[nodiscard]] Result<std::size_t> encode_into(
    const Frame &frame, std::span<std::uint8_t> output);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode(const Frame &frame);
[[nodiscard]] Result<Frame> decode(std::span<const std::uint8_t> bytes);
[[nodiscard]] std::string_view to_string(FrameType type) noexcept;

struct PacingSnapshot {
    std::size_t buffered_bytes{0U};
    std::size_t offered_bytes{0U};
    std::uint64_t interval_us{0U};
    std::uint32_t consecutive_accepts{0U};
};

// Transport-independent admission pacer. Bytes remain owned until one whole
// offered packet is accepted; SENDQ rejection backs off without advancing or
// discarding input. Every packet coalesces for the current interval, including
// a full packet, so input cannot accidentally recreate an unpaced burst.
class AdmissionPacer {
  public:
    using Clock = std::chrono::steady_clock;
    struct Config {
        std::chrono::microseconds base_interval{std::chrono::milliseconds(20)};
        std::chrono::microseconds maximum_interval{std::chrono::milliseconds(320)};
        std::size_t maximum_packet_bytes{kMaximumPayloadBytes};
        std::size_t maximum_buffered_bytes{64U * 1024U};
        std::uint32_t recovery_accepts{8U};
    };

    AdmissionPacer();
    explicit AdmissionPacer(Config config);

    [[nodiscard]] Status enqueue(
        std::span<const std::uint8_t> bytes, Clock::time_point now);
    [[nodiscard]] Result<std::vector<std::uint8_t>> ready(
        Clock::time_point now);
    [[nodiscard]] Status accepted(
        std::size_t bytes, Clock::time_point now);
    [[nodiscard]] Status rejected(Clock::time_point now);
    [[nodiscard]] PacingSnapshot snapshot() const noexcept;

  private:
    [[nodiscard]] Status validate_config() const;

    Config config_;
    std::deque<std::uint8_t> bytes_;
    std::optional<Clock::time_point> next_ready_;
    std::size_t offered_bytes_{0U};
    std::chrono::microseconds interval_{};
    std::uint32_t consecutive_accepts_{0U};
};

}  // namespace iotox::protocol::ratox
