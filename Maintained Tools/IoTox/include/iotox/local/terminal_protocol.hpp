#pragma once

#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>
#include <vector>

namespace iotox::local {

inline constexpr std::uint8_t kTerminalProtocolMajor = 1U;
inline constexpr std::uint8_t kTerminalProtocolMinor = 0U;
inline constexpr std::size_t kTerminalHeaderSize = 32U;
inline constexpr std::size_t kTerminalMaxPayloadSize = 16U * 1024U;
inline constexpr std::size_t kTerminalMaxPacketSize =
    kTerminalHeaderSize + kTerminalMaxPayloadSize;
inline constexpr std::size_t kTerminalPeerPublicKeyBytes = 32U;
inline constexpr std::size_t kTerminalSessionIdBytes = 16U;

// The terminal socket is deliberately a separate, persistent, same-user
// streaming plane. These values are frozen for local protocol v1.
enum class TerminalPacketType : std::uint8_t {
    open = 1U,
    input = 2U,
    resize = 3U,
    detach = 4U,
    close = 5U,
    output_ack = 6U,
    ping = 7U,

    opened = 32U,
    output = 33U,
    output_gap = 34U,
    exit_status = 35U,
    detached = 36U,
    closed = 37U,
    error = 38U,
    pong = 39U,
};

enum class TerminalOpenMode : std::uint8_t {
    open_or_resume = 0U,
    new_session = 1U,
    resume_only = 2U,
};

struct TerminalPacket {
    TerminalPacketType type{TerminalPacketType::ping};
    std::uint8_t flags{0U};
    std::uint64_t stream_id{0U};
    // Cumulative byte position. INPUT and OUTPUT use the first byte position;
    // OUTPUT_ACK uses the next expected output position.
    std::uint64_t sequence{0U};
    ErrorCode status{ErrorCode::ok};
    std::vector<std::uint8_t> payload;

    [[nodiscard]] bool operator==(const TerminalPacket &) const = default;
};

struct TerminalOpenRequest {
    std::array<std::uint8_t, kTerminalPeerPublicKeyBytes> peer_public_key{};
    // Zero requests a new session. A nonzero value identifies the exact
    // detached session to resume; it is never inferred from a peer selector.
    std::array<std::uint8_t, kTerminalSessionIdBytes> session_id{};
    std::uint16_t columns{80U};
    std::uint16_t rows{24U};
    TerminalOpenMode mode{TerminalOpenMode::open_or_resume};

    [[nodiscard]] bool operator==(const TerminalOpenRequest &) const = default;
};

struct TerminalOpened {
    std::array<std::uint8_t, kTerminalSessionIdBytes> session_id{};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};
    std::uint64_t next_input_sequence{0U};
    std::uint64_t next_output_sequence{0U};

    [[nodiscard]] bool operator==(const TerminalOpened &) const = default;
};

struct TerminalOutputGap {
    std::uint64_t retained_base_sequence{0U};
    std::uint64_t produced_next_sequence{0U};

    [[nodiscard]] bool operator==(const TerminalOutputGap &) const = default;
};

struct TerminalExitStatus {
    std::uint8_t kind{0U};
    bool core_dumped{false};
    std::uint16_t signal{0U};
    std::uint32_t code{0U};

    [[nodiscard]] bool operator==(const TerminalExitStatus &) const = default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_terminal_packet(
    const TerminalPacket &packet);
[[nodiscard]] Result<TerminalPacket> decode_terminal_packet(
    std::span<const std::uint8_t> bytes);

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_terminal_open(
    const TerminalOpenRequest &request);
[[nodiscard]] Result<TerminalOpenRequest> decode_terminal_open(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_terminal_opened(
    const TerminalOpened &opened);
[[nodiscard]] Result<TerminalOpened> decode_terminal_opened(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_terminal_output_gap(
    const TerminalOutputGap &gap);
[[nodiscard]] Result<TerminalOutputGap> decode_terminal_output_gap(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_terminal_exit_status(
    const TerminalExitStatus &status);
[[nodiscard]] Result<TerminalExitStatus> decode_terminal_exit_status(
    std::span<const std::uint8_t> payload);

[[nodiscard]] std::string_view to_string(TerminalPacketType type) noexcept;

}  // namespace iotox::local
