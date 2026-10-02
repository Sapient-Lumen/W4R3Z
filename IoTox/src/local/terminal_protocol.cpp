#include "iotox/local/terminal_protocol.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <string>
#include <utility>

namespace iotox::local {
namespace {

// IoTox Terminal Transport Socket. This magic is local-only and distinct from
// both the public IoTox protocol and Ratox's toxcore packet ID.
constexpr std::array<std::uint8_t, 4U> kMagic{'I', 'T', 'T', 'S'};
constexpr std::size_t kOpenPayloadBytes = 56U;
constexpr std::size_t kOpenedPayloadBytes = 48U;
constexpr std::size_t kGapPayloadBytes = 16U;
constexpr std::size_t kExitPayloadBytes = 8U;

void write_u16(std::span<std::uint8_t> output, std::uint16_t value) {
    output[0U] = static_cast<std::uint8_t>(value >> 8U);
    output[1U] = static_cast<std::uint8_t>(value);
}

void write_u32(std::span<std::uint8_t> output, std::uint32_t value) {
    output[0U] = static_cast<std::uint8_t>(value >> 24U);
    output[1U] = static_cast<std::uint8_t>(value >> 16U);
    output[2U] = static_cast<std::uint8_t>(value >> 8U);
    output[3U] = static_cast<std::uint8_t>(value);
}

void write_u64(std::span<std::uint8_t> output, std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[index] = static_cast<std::uint8_t>(
            value >> static_cast<unsigned>((7U - index) * 8U));
    }
}

std::uint16_t read_u16(std::span<const std::uint8_t> input) {
    return static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(input[0U]) << 8U |
        static_cast<std::uint16_t>(input[1U]));
}

std::uint32_t read_u32(std::span<const std::uint8_t> input) {
    std::uint32_t value = 0U;
    for (const std::uint8_t byte : input.first(4U)) {
        value = (value << 8U) | byte;
    }
    return value;
}

std::uint64_t read_u64(std::span<const std::uint8_t> input) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : input.first(8U)) {
        value = (value << 8U) | byte;
    }
    return value;
}

bool all_zero(std::span<const std::uint8_t> input) {
    return std::all_of(input.begin(), input.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

bool known_type(TerminalPacketType type) {
    switch (type) {
        case TerminalPacketType::open:
        case TerminalPacketType::input:
        case TerminalPacketType::resize:
        case TerminalPacketType::detach:
        case TerminalPacketType::close:
        case TerminalPacketType::output_ack:
        case TerminalPacketType::ping:
        case TerminalPacketType::opened:
        case TerminalPacketType::output:
        case TerminalPacketType::output_gap:
        case TerminalPacketType::exit_status:
        case TerminalPacketType::detached:
        case TerminalPacketType::closed:
        case TerminalPacketType::error:
        case TerminalPacketType::pong:
            return true;
    }
    return false;
}

Status validate_packet(const TerminalPacket &packet, ErrorCode code) {
    const auto reject = [code](std::string message) {
        return Status{code, std::move(message)};
    };
    if (!known_type(packet.type)) {
        return reject("local terminal packet type is unknown");
    }
    if (packet.stream_id == 0U) {
        return reject("local terminal packet requires a nonzero stream ID");
    }
    if (packet.flags != 0U) {
        return reject("local terminal packet has unsupported flags");
    }
    if (packet.payload.size() > kTerminalMaxPayloadSize) {
        return reject("local terminal packet exceeds the payload ceiling");
    }
    const auto status_value = static_cast<unsigned int>(packet.status);
    if (status_value > static_cast<unsigned int>(ErrorCode::resource_exhausted)) {
        return reject("local terminal packet status is unknown");
    }
    if (packet.type == TerminalPacketType::error) {
        if (packet.status == ErrorCode::ok) {
            return reject("local terminal ERROR requires a failure status");
        }
        if (packet.payload.empty() || packet.payload.size() > 1024U) {
            return reject("local terminal ERROR text must be in 1..1024 bytes");
        }
    } else if (packet.status != ErrorCode::ok) {
        return reject("only local terminal ERROR may carry a failure status");
    }

    switch (packet.type) {
        case TerminalPacketType::input:
        case TerminalPacketType::output:
            if (packet.sequence == 0U || packet.payload.empty()) {
                return reject("local terminal byte packet requires sequence and payload");
            }
            if (packet.payload.size() >
                std::numeric_limits<std::uint64_t>::max() - packet.sequence) {
                return reject("local terminal byte sequence overflows");
            }
            break;
        case TerminalPacketType::output_ack:
            if (packet.sequence == 0U || !packet.payload.empty()) {
                return reject("local terminal OUTPUT_ACK is malformed");
            }
            break;
        case TerminalPacketType::open:
            if (packet.sequence != 0U || packet.payload.size() != kOpenPayloadBytes) {
                return reject("local terminal OPEN payload must be 56 bytes");
            }
            if (!decode_terminal_open(packet.payload)) {
                return reject("local terminal OPEN payload is not canonical");
            }
            break;
        case TerminalPacketType::resize:
            if (packet.sequence != 0U || packet.payload.size() != 4U) {
                return reject("local terminal RESIZE payload must be 4 bytes");
            }
            if (read_u16(std::span<const std::uint8_t>{packet.payload}.first(2U)) < 1U ||
                read_u16(std::span<const std::uint8_t>{packet.payload}.first(2U)) > 1000U ||
                read_u16(std::span<const std::uint8_t>{packet.payload}.subspan(2U, 2U)) < 1U ||
                read_u16(std::span<const std::uint8_t>{packet.payload}.subspan(2U, 2U)) > 1000U) {
                return reject("local terminal RESIZE dimensions must be in 1..1000");
            }
            break;
        case TerminalPacketType::opened:
            if (packet.sequence != 0U || packet.payload.size() != kOpenedPayloadBytes) {
                return reject("local terminal OPENED payload must be 48 bytes");
            }
            if (!decode_terminal_opened(packet.payload)) {
                return reject("local terminal OPENED payload is not canonical");
            }
            break;
        case TerminalPacketType::output_gap:
            if (packet.sequence != 0U || packet.payload.size() != kGapPayloadBytes) {
                return reject("local terminal OUTPUT_GAP payload must be 16 bytes");
            }
            if (!decode_terminal_output_gap(packet.payload)) {
                return reject("local terminal OUTPUT_GAP payload is not canonical");
            }
            break;
        case TerminalPacketType::exit_status:
            if (packet.sequence != 0U || packet.payload.size() != kExitPayloadBytes) {
                return reject("local terminal EXIT_STATUS payload must be 8 bytes");
            }
            if (!decode_terminal_exit_status(packet.payload)) {
                return reject("local terminal EXIT_STATUS payload is not canonical");
            }
            break;
        case TerminalPacketType::error:
            if (packet.sequence != 0U) {
                return reject("local terminal ERROR cannot carry a byte sequence");
            }
            break;
        case TerminalPacketType::detach:
        case TerminalPacketType::close:
        case TerminalPacketType::ping:
        case TerminalPacketType::detached:
        case TerminalPacketType::closed:
        case TerminalPacketType::pong:
            if (packet.sequence != 0U || !packet.payload.empty()) {
                return reject("local terminal control packet must have an empty payload");
            }
            break;
    }
    return Status::success();
}

}  // namespace

Result<std::vector<std::uint8_t>> encode_terminal_packet(
    const TerminalPacket &packet) {
    const Status valid = validate_packet(packet, ErrorCode::invalid_argument);
    if (!valid.ok()) return valid;

    std::array<std::uint8_t, kTerminalHeaderSize> header{};
    std::copy(kMagic.begin(), kMagic.end(), header.begin());
    header[4U] = kTerminalProtocolMajor;
    header[5U] = kTerminalProtocolMinor;
    header[6U] = static_cast<std::uint8_t>(packet.type);
    header[7U] = packet.flags;
    write_u64(std::span<std::uint8_t>{header}.subspan(8U, 8U), packet.stream_id);
    write_u64(std::span<std::uint8_t>{header}.subspan(16U, 8U), packet.sequence);
    write_u16(
        std::span<std::uint8_t>{header}.subspan(24U, 2U),
        static_cast<std::uint16_t>(packet.status));
    write_u16(
        std::span<std::uint8_t>{header}.subspan(26U, 2U),
        static_cast<std::uint16_t>(packet.payload.size()));

    std::vector<std::uint8_t> bytes;
    bytes.reserve(kTerminalHeaderSize + packet.payload.size());
    bytes.insert(bytes.end(), header.begin(), header.end());
    bytes.insert(bytes.end(), packet.payload.begin(), packet.payload.end());
    return bytes;
}

Result<TerminalPacket> decode_terminal_packet(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kTerminalHeaderSize || bytes.size() > kTerminalMaxPacketSize) {
        return Status{ErrorCode::protocol_error,
                      "local terminal packet size is outside the protocol bounds"};
    }
    if (!std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
        bytes[4U] != kTerminalProtocolMajor) {
        return Status{ErrorCode::unsupported,
                      "local terminal protocol magic or major version is unsupported"};
    }
    if (bytes[5U] != kTerminalProtocolMinor ||
        !all_zero(bytes.subspan(28U, 4U))) {
        return Status{ErrorCode::protocol_error,
                      "local terminal minor version or reserved bytes are invalid"};
    }
    const std::size_t payload_size = read_u16(bytes.subspan(26U, 2U));
    if (bytes.size() != kTerminalHeaderSize + payload_size) {
        return Status{ErrorCode::protocol_error,
                      "local terminal payload length does not match packet size"};
    }

    TerminalPacket packet;
    packet.type = static_cast<TerminalPacketType>(bytes[6U]);
    packet.flags = bytes[7U];
    packet.stream_id = read_u64(bytes.subspan(8U, 8U));
    packet.sequence = read_u64(bytes.subspan(16U, 8U));
    packet.status = static_cast<ErrorCode>(read_u16(bytes.subspan(24U, 2U)));
    packet.payload.assign(bytes.begin() + static_cast<std::ptrdiff_t>(kTerminalHeaderSize),
                          bytes.end());
    const Status valid = validate_packet(packet, ErrorCode::protocol_error);
    if (!valid.ok()) return valid;
    return packet;
}

Result<std::vector<std::uint8_t>> encode_terminal_open(
    const TerminalOpenRequest &request) {
    const bool peer_is_zero = all_zero(request.peer_public_key);
    const bool session_is_zero = all_zero(request.session_id);
    if (request.columns < 1U || request.columns > 1000U ||
        request.rows < 1U || request.rows > 1000U) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal dimensions must be in 1..1000"};
    }
    if (static_cast<std::uint8_t>(request.mode) >
        static_cast<std::uint8_t>(TerminalOpenMode::resume_only)) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal OPEN mode is unknown"};
    }
    if (request.mode == TerminalOpenMode::new_session &&
        (peer_is_zero || !session_is_zero)) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal new-session OPEN requires a peer and a zero session ID"};
    }
    if (request.mode == TerminalOpenMode::resume_only && session_is_zero) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal resume-only OPEN requires a nonzero session ID"};
    }
    if (request.mode == TerminalOpenMode::open_or_resume &&
        session_is_zero && peer_is_zero) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal OPEN requires a peer when creating a session"};
    }
    std::vector<std::uint8_t> payload(kOpenPayloadBytes, 0U);
    std::copy(request.peer_public_key.begin(), request.peer_public_key.end(),
              payload.begin());
    std::copy(request.session_id.begin(), request.session_id.end(),
              payload.begin() + 32U);
    write_u16(std::span<std::uint8_t>{payload}.subspan(48U, 2U), request.columns);
    write_u16(std::span<std::uint8_t>{payload}.subspan(50U, 2U), request.rows);
    payload[52U] = static_cast<std::uint8_t>(request.mode);
    return payload;
}

Result<TerminalOpenRequest> decode_terminal_open(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kOpenPayloadBytes) {
        return Status{ErrorCode::protocol_error,
                      "local terminal OPEN payload must be 56 bytes"};
    }
    if (!all_zero(payload.subspan(53U, 3U))) {
        return Status{ErrorCode::protocol_error,
                      "local terminal OPEN reserved bytes are nonzero"};
    }
    TerminalOpenRequest request;
    std::copy_n(payload.begin(), request.peer_public_key.size(),
                request.peer_public_key.begin());
    std::copy_n(payload.begin() + 32U, request.session_id.size(),
                request.session_id.begin());
    request.columns = read_u16(payload.subspan(48U, 2U));
    request.rows = read_u16(payload.subspan(50U, 2U));
    request.mode = static_cast<TerminalOpenMode>(payload[52U]);
    auto canonical = encode_terminal_open(request);
    if (!canonical) {
        return Status{ErrorCode::protocol_error, canonical.status().message()};
    }
    return request;
}

Result<std::vector<std::uint8_t>> encode_terminal_opened(
    const TerminalOpened &opened) {
    if (all_zero(opened.session_id) || opened.incarnation == 0U ||
        opened.generation == 0U || opened.next_input_sequence == 0U ||
        opened.next_output_sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal OPENED identity and positions must be nonzero"};
    }
    std::vector<std::uint8_t> payload(kOpenedPayloadBytes, 0U);
    std::copy(opened.session_id.begin(), opened.session_id.end(), payload.begin());
    write_u64(std::span<std::uint8_t>{payload}.subspan(16U, 8U), opened.incarnation);
    write_u64(std::span<std::uint8_t>{payload}.subspan(24U, 8U), opened.generation);
    write_u64(std::span<std::uint8_t>{payload}.subspan(32U, 8U),
              opened.next_input_sequence);
    write_u64(std::span<std::uint8_t>{payload}.subspan(40U, 8U),
              opened.next_output_sequence);
    return payload;
}

Result<TerminalOpened> decode_terminal_opened(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kOpenedPayloadBytes) {
        return Status{ErrorCode::protocol_error,
                      "local terminal OPENED payload must be 48 bytes"};
    }
    TerminalOpened opened;
    std::copy_n(payload.begin(), opened.session_id.size(), opened.session_id.begin());
    opened.incarnation = read_u64(payload.subspan(16U, 8U));
    opened.generation = read_u64(payload.subspan(24U, 8U));
    opened.next_input_sequence = read_u64(payload.subspan(32U, 8U));
    opened.next_output_sequence = read_u64(payload.subspan(40U, 8U));
    auto canonical = encode_terminal_opened(opened);
    if (!canonical) {
        return Status{ErrorCode::protocol_error, canonical.status().message()};
    }
    return opened;
}

Result<std::vector<std::uint8_t>> encode_terminal_output_gap(
    const TerminalOutputGap &gap) {
    if (gap.retained_base_sequence == 0U || gap.produced_next_sequence == 0U ||
        gap.retained_base_sequence > gap.produced_next_sequence) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal output gap bounds are invalid"};
    }
    std::vector<std::uint8_t> payload(kGapPayloadBytes, 0U);
    write_u64(std::span<std::uint8_t>{payload}.first(8U),
              gap.retained_base_sequence);
    write_u64(std::span<std::uint8_t>{payload}.subspan(8U, 8U),
              gap.produced_next_sequence);
    return payload;
}

Result<TerminalOutputGap> decode_terminal_output_gap(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kGapPayloadBytes) {
        return Status{ErrorCode::protocol_error,
                      "local terminal OUTPUT_GAP payload must be 16 bytes"};
    }
    TerminalOutputGap gap{
        read_u64(payload.first(8U)), read_u64(payload.subspan(8U, 8U))};
    auto canonical = encode_terminal_output_gap(gap);
    if (!canonical) {
        return Status{ErrorCode::protocol_error, canonical.status().message()};
    }
    return gap;
}

Result<std::vector<std::uint8_t>> encode_terminal_exit_status(
    const TerminalExitStatus &status) {
    if (status.kind > 2U ||
        (status.kind == 0U && (status.core_dumped || status.signal != 0U)) ||
        (status.kind == 1U && status.signal == 0U) ||
        (status.kind == 2U &&
         (status.core_dumped || status.signal != 0U || status.code != 0U))) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal exit status fields are inconsistent"};
    }
    std::vector<std::uint8_t> payload(kExitPayloadBytes, 0U);
    payload[0U] = status.kind;
    payload[1U] = status.core_dumped ? 1U : 0U;
    write_u16(std::span<std::uint8_t>{payload}.subspan(2U, 2U), status.signal);
    write_u32(std::span<std::uint8_t>{payload}.subspan(4U, 4U), status.code);
    return payload;
}

Result<TerminalExitStatus> decode_terminal_exit_status(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kExitPayloadBytes) {
        return Status{ErrorCode::protocol_error,
                      "local terminal EXIT_STATUS payload must be 8 bytes"};
    }
    if (payload[1U] > 1U) {
        return Status{ErrorCode::protocol_error,
                      "local terminal core-dump flag is invalid"};
    }
    TerminalExitStatus status;
    status.kind = payload[0U];
    status.core_dumped = payload[1U] != 0U;
    status.signal = read_u16(payload.subspan(2U, 2U));
    status.code = read_u32(payload.subspan(4U, 4U));
    auto canonical = encode_terminal_exit_status(status);
    if (!canonical) {
        return Status{ErrorCode::protocol_error, canonical.status().message()};
    }
    return status;
}

std::string_view to_string(TerminalPacketType type) noexcept {
    switch (type) {
        case TerminalPacketType::open: return "OPEN";
        case TerminalPacketType::input: return "INPUT";
        case TerminalPacketType::resize: return "RESIZE";
        case TerminalPacketType::detach: return "DETACH";
        case TerminalPacketType::close: return "CLOSE";
        case TerminalPacketType::output_ack: return "OUTPUT_ACK";
        case TerminalPacketType::ping: return "PING";
        case TerminalPacketType::opened: return "OPENED";
        case TerminalPacketType::output: return "OUTPUT";
        case TerminalPacketType::output_gap: return "OUTPUT_GAP";
        case TerminalPacketType::exit_status: return "EXIT_STATUS";
        case TerminalPacketType::detached: return "DETACHED";
        case TerminalPacketType::closed: return "CLOSED";
        case TerminalPacketType::error: return "ERROR";
        case TerminalPacketType::pong: return "PONG";
    }
    return "UNKNOWN";
}

}  // namespace iotox::local
