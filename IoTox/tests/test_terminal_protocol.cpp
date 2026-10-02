#include "iotox/local/terminal_protocol.hpp"
#include "test_harness.hpp"

#include <array>
#include <cstdint>
#include <limits>
#include <string_view>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::local::TerminalExitStatus;
using iotox::local::TerminalOpenMode;
using iotox::local::TerminalOpened;
using iotox::local::TerminalOpenRequest;
using iotox::local::TerminalOutputGap;
using iotox::local::TerminalPacket;
using iotox::local::TerminalPacketType;

TerminalOpenRequest new_request() {
    TerminalOpenRequest request;
    request.peer_public_key.front() = 0x31U;
    request.columns = 132U;
    request.rows = 43U;
    request.mode = TerminalOpenMode::new_session;
    return request;
}

}  // namespace

IOTOX_TEST("local terminal OPEN payload round-trips new and resume identities") {
    const TerminalOpenRequest created = new_request();
    auto encoded = iotox::local::encode_terminal_open(created);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() == 56U);
    auto decoded = iotox::local::decode_terminal_open(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == created);

    TerminalOpenRequest resumed;
    resumed.session_id.front() = 0x52U;
    resumed.columns = 80U;
    resumed.rows = 24U;
    resumed.mode = TerminalOpenMode::resume_only;
    auto resume_bytes = iotox::local::encode_terminal_open(resumed);
    IOTOX_CHECK_MSG(resume_bytes.ok(), resume_bytes.status().message());
    auto resume_decoded = iotox::local::decode_terminal_open(resume_bytes.value());
    IOTOX_CHECK_MSG(resume_decoded.ok(), resume_decoded.status().message());
    IOTOX_CHECK(resume_decoded.value() == resumed);
}

IOTOX_TEST("local terminal packet framing is canonical and bounded") {
    TerminalPacket packet;
    packet.type = TerminalPacketType::output;
    packet.stream_id = 0x1122334455667788ULL;
    packet.sequence = 9U;
    packet.payload = {0x00U, 0x7fU, 0x80U, 0xffU};

    auto encoded = iotox::local::encode_terminal_packet(packet);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() ==
                iotox::local::kTerminalHeaderSize + packet.payload.size());
    auto decoded = iotox::local::decode_terminal_packet(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == packet);

    TerminalPacket too_large = packet;
    too_large.payload.assign(iotox::local::kTerminalMaxPayloadSize + 1U, 0x41U);
    auto rejected = iotox::local::encode_terminal_packet(too_large);
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.status().code() == ErrorCode::invalid_argument);
}

IOTOX_TEST("local terminal v1 header has one exact frozen wire image") {
    TerminalPacket packet;
    packet.type = TerminalPacketType::output;
    packet.stream_id = 0x1122334455667788ULL;
    packet.sequence = 9U;
    packet.payload = {0x00U, 0x7fU, 0x80U, 0xffU};

    const std::vector<std::uint8_t> expected{
        0x49U, 0x54U, 0x54U, 0x53U, 0x01U, 0x00U, 0x21U, 0x00U,
        0x11U, 0x22U, 0x33U, 0x44U, 0x55U, 0x66U, 0x77U, 0x88U,
        0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x09U,
        0x00U, 0x00U, 0x00U, 0x04U, 0x00U, 0x00U, 0x00U, 0x00U,
        0x00U, 0x7fU, 0x80U, 0xffU,
    };

    auto encoded = iotox::local::encode_terminal_packet(packet);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value() == expected);

    auto decoded = iotox::local::decode_terminal_packet(expected);
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == packet);
}

IOTOX_TEST("local terminal framing rejects noncanonical headers and type fields") {
    TerminalPacket packet;
    packet.type = TerminalPacketType::ping;
    packet.stream_id = 7U;
    auto encoded = iotox::local::encode_terminal_packet(packet);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    std::vector<std::uint8_t> corrupted = encoded.value();
    corrupted[28U] = 1U;
    auto reserved = iotox::local::decode_terminal_packet(corrupted);
    IOTOX_CHECK(!reserved.ok());
    IOTOX_CHECK(reserved.status().code() == ErrorCode::protocol_error);

    corrupted = encoded.value();
    corrupted[6U] = 0xffU;
    auto unknown = iotox::local::decode_terminal_packet(corrupted);
    IOTOX_CHECK(!unknown.ok());
    IOTOX_CHECK(unknown.status().code() == ErrorCode::protocol_error);

    corrupted = encoded.value();
    corrupted[4U] = static_cast<std::uint8_t>(
        iotox::local::kTerminalProtocolMajor + 1U);
    auto major = iotox::local::decode_terminal_packet(corrupted);
    IOTOX_CHECK(!major.ok());
    IOTOX_CHECK(major.status().code() == ErrorCode::unsupported);

    TerminalPacket malformed_ack;
    malformed_ack.type = TerminalPacketType::output_ack;
    malformed_ack.stream_id = 8U;
    malformed_ack.sequence = 0U;
    auto ack = iotox::local::encode_terminal_packet(malformed_ack);
    IOTOX_CHECK(!ack.ok());
}

IOTOX_TEST("local terminal structured server payloads enforce semantic bounds") {
    TerminalOpened opened;
    opened.session_id.front() = 0x10U;
    opened.incarnation = 2U;
    opened.generation = 3U;
    opened.next_input_sequence = 4U;
    opened.next_output_sequence = 5U;
    auto opened_bytes = iotox::local::encode_terminal_opened(opened);
    IOTOX_CHECK_MSG(opened_bytes.ok(), opened_bytes.status().message());
    auto opened_again = iotox::local::decode_terminal_opened(opened_bytes.value());
    IOTOX_CHECK_MSG(opened_again.ok(), opened_again.status().message());
    IOTOX_CHECK(opened_again.value() == opened);

    TerminalOutputGap gap{11U, 19U};
    auto gap_bytes = iotox::local::encode_terminal_output_gap(gap);
    IOTOX_CHECK_MSG(gap_bytes.ok(), gap_bytes.status().message());
    auto gap_again = iotox::local::decode_terminal_output_gap(gap_bytes.value());
    IOTOX_CHECK_MSG(gap_again.ok(), gap_again.status().message());
    IOTOX_CHECK(gap_again.value() == gap);

    TerminalOutputGap backwards{20U, 19U};
    IOTOX_CHECK(!iotox::local::encode_terminal_output_gap(backwards).ok());

    TerminalExitStatus signaled;
    signaled.kind = 1U;
    signaled.core_dumped = true;
    signaled.signal = 11U;
    auto exit_bytes = iotox::local::encode_terminal_exit_status(signaled);
    IOTOX_CHECK_MSG(exit_bytes.ok(), exit_bytes.status().message());
    auto exit_again = iotox::local::decode_terminal_exit_status(exit_bytes.value());
    IOTOX_CHECK_MSG(exit_again.ok(), exit_again.status().message());
    IOTOX_CHECK(exit_again.value() == signaled);

    TerminalExitStatus inconsistent;
    inconsistent.kind = 0U;
    inconsistent.signal = 9U;
    IOTOX_CHECK(!iotox::local::encode_terminal_exit_status(inconsistent).ok());
}

IOTOX_TEST("local terminal protocol freezes every v1 packet type") {
    using iotox::local::TerminalPacketType;
    const std::array types{
        TerminalPacketType::open,
        TerminalPacketType::input,
        TerminalPacketType::resize,
        TerminalPacketType::detach,
        TerminalPacketType::close,
        TerminalPacketType::output_ack,
        TerminalPacketType::ping,
        TerminalPacketType::opened,
        TerminalPacketType::output,
        TerminalPacketType::output_gap,
        TerminalPacketType::exit_status,
        TerminalPacketType::detached,
        TerminalPacketType::closed,
        TerminalPacketType::error,
        TerminalPacketType::pong,
    };
    const std::array<std::uint8_t, 15U> values{
        1U, 2U, 3U, 4U, 5U, 6U, 7U,
        32U, 33U, 34U, 35U, 36U, 37U, 38U, 39U,
    };
    const std::array<std::string_view, 15U> names{
        "OPEN", "INPUT", "RESIZE", "DETACH", "CLOSE", "OUTPUT_ACK", "PING",
        "OPENED", "OUTPUT", "OUTPUT_GAP", "EXIT_STATUS", "DETACHED", "CLOSED",
        "ERROR", "PONG",
    };
    for (std::size_t index = 0U; index < types.size(); ++index) {
        IOTOX_CHECK(static_cast<std::uint8_t>(types[index]) == values[index]);
        IOTOX_CHECK(iotox::local::to_string(types[index]) == names[index]);
    }
    IOTOX_CHECK(iotox::local::to_string(
                    static_cast<TerminalPacketType>(0xffU)) == "UNKNOWN");
}

IOTOX_TEST("local terminal protocol round-trips every canonical packet shape") {
    std::vector<TerminalPacket> packets;

    TerminalPacket open;
    open.type = TerminalPacketType::open;
    open.stream_id = 1U;
    auto open_payload = iotox::local::encode_terminal_open(new_request());
    IOTOX_CHECK_MSG(open_payload.ok(), open_payload.status().message());
    open.payload = open_payload.value();
    packets.push_back(open);

    TerminalPacket input;
    input.type = TerminalPacketType::input;
    input.stream_id = 2U;
    input.sequence = 1U;
    input.payload = {0x00U, 0x7fU, 0x80U, 0xffU};
    packets.push_back(input);

    TerminalPacket resize;
    resize.type = TerminalPacketType::resize;
    resize.stream_id = 3U;
    resize.payload = {0U, 120U, 0U, 40U};
    packets.push_back(resize);

    for (const TerminalPacketType type : {
             TerminalPacketType::detach,
             TerminalPacketType::close,
             TerminalPacketType::ping,
             TerminalPacketType::detached,
             TerminalPacketType::closed,
             TerminalPacketType::pong}) {
        TerminalPacket control;
        control.type = type;
        control.stream_id = 4U + packets.size();
        packets.push_back(control);
    }

    TerminalPacket acknowledgement;
    acknowledgement.type = TerminalPacketType::output_ack;
    acknowledgement.stream_id = 20U;
    acknowledgement.sequence = 9U;
    packets.push_back(acknowledgement);

    TerminalOpened opened;
    opened.session_id.front() = 0x21U;
    opened.incarnation = 2U;
    opened.generation = 3U;
    opened.next_input_sequence = 4U;
    opened.next_output_sequence = 5U;
    auto opened_payload = iotox::local::encode_terminal_opened(opened);
    IOTOX_CHECK_MSG(opened_payload.ok(), opened_payload.status().message());
    TerminalPacket opened_packet;
    opened_packet.type = TerminalPacketType::opened;
    opened_packet.stream_id = 21U;
    opened_packet.payload = opened_payload.value();
    packets.push_back(opened_packet);

    TerminalPacket output;
    output.type = TerminalPacketType::output;
    output.stream_id = 22U;
    output.sequence = 5U;
    output.payload = {'o', 'u', 't'};
    packets.push_back(output);

    auto gap_payload = iotox::local::encode_terminal_output_gap({8U, 13U});
    IOTOX_CHECK_MSG(gap_payload.ok(), gap_payload.status().message());
    TerminalPacket gap;
    gap.type = TerminalPacketType::output_gap;
    gap.stream_id = 23U;
    gap.payload = gap_payload.value();
    packets.push_back(gap);

    TerminalExitStatus exit;
    exit.kind = 0U;
    exit.code = 17U;
    auto exit_payload = iotox::local::encode_terminal_exit_status(exit);
    IOTOX_CHECK_MSG(exit_payload.ok(), exit_payload.status().message());
    TerminalPacket exit_packet;
    exit_packet.type = TerminalPacketType::exit_status;
    exit_packet.stream_id = 24U;
    exit_packet.payload = exit_payload.value();
    packets.push_back(exit_packet);

    TerminalPacket error;
    error.type = TerminalPacketType::error;
    error.stream_id = 25U;
    error.status = ErrorCode::unavailable;
    error.payload = {'n', 'o', 't', ' ', 'o', 'n', 'l', 'i', 'n', 'e'};
    packets.push_back(error);

    for (const TerminalPacket &packet : packets) {
        auto encoded = iotox::local::encode_terminal_packet(packet);
        IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
        auto decoded = iotox::local::decode_terminal_packet(encoded.value());
        IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
        IOTOX_CHECK(decoded.value() == packet);
    }
}

IOTOX_TEST("local terminal decoder rejects header length status and sequence ambiguity") {
    TerminalPacket packet;
    packet.type = TerminalPacketType::ping;
    packet.stream_id = 7U;
    auto encoded = iotox::local::encode_terminal_packet(packet);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    auto bad_magic = encoded.value();
    bad_magic[0U] = 'X';
    auto magic = iotox::local::decode_terminal_packet(bad_magic);
    IOTOX_CHECK(!magic.ok());
    IOTOX_CHECK(magic.status().code() == ErrorCode::unsupported);

    auto bad_minor = encoded.value();
    bad_minor[5U] = 1U;
    auto minor = iotox::local::decode_terminal_packet(bad_minor);
    IOTOX_CHECK(!minor.ok());
    IOTOX_CHECK(minor.status().code() == ErrorCode::protocol_error);

    auto bad_flags = encoded.value();
    bad_flags[7U] = 1U;
    IOTOX_CHECK(!iotox::local::decode_terminal_packet(bad_flags).ok());

    auto zero_stream = encoded.value();
    for (std::size_t index = 8U; index < 16U; ++index) {
        zero_stream.at(index) = 0U;
    }
    IOTOX_CHECK(!iotox::local::decode_terminal_packet(zero_stream).ok());

    auto unknown_status = encoded.value();
    unknown_status[24U] = 0xffU;
    unknown_status[25U] = 0xffU;
    IOTOX_CHECK(!iotox::local::decode_terminal_packet(unknown_status).ok());

    auto wrong_length = encoded.value();
    wrong_length[27U] = 1U;
    IOTOX_CHECK(!iotox::local::decode_terminal_packet(wrong_length).ok());

    auto trailing = encoded.value();
    trailing.push_back(0U);
    IOTOX_CHECK(!iotox::local::decode_terminal_packet(trailing).ok());

    const std::vector<std::uint8_t> truncated(
        encoded.value().begin(), encoded.value().begin() + 31);
    IOTOX_CHECK(!iotox::local::decode_terminal_packet(truncated).ok());

    TerminalPacket overflow;
    overflow.type = TerminalPacketType::input;
    overflow.stream_id = 8U;
    overflow.sequence = std::numeric_limits<std::uint64_t>::max();
    overflow.payload = {0x41U};
    IOTOX_CHECK(!iotox::local::encode_terminal_packet(overflow).ok());
}

IOTOX_TEST("local terminal packet layer rejects noncanonical structured payloads") {
    TerminalPacket open;
    open.type = TerminalPacketType::open;
    open.stream_id = 51U;
    auto open_payload = iotox::local::encode_terminal_open(new_request());
    IOTOX_CHECK_MSG(open_payload.ok(), open_payload.status().message());
    open.payload = open_payload.value();
    open.payload[55U] = 1U;
    IOTOX_CHECK(!iotox::local::encode_terminal_packet(open).ok());

    open.payload = open_payload.value();
    auto encoded_open = iotox::local::encode_terminal_packet(open);
    IOTOX_CHECK_MSG(encoded_open.ok(), encoded_open.status().message());
    encoded_open.value().back() = 1U;
    IOTOX_CHECK(!iotox::local::decode_terminal_packet(encoded_open.value()).ok());

    TerminalPacket resize;
    resize.type = TerminalPacketType::resize;
    resize.stream_id = 52U;
    resize.payload = {0U, 0U, 0U, 24U};
    IOTOX_CHECK(!iotox::local::encode_terminal_packet(resize).ok());
    resize.payload = {0x03U, 0xe9U, 0U, 24U};
    IOTOX_CHECK(!iotox::local::encode_terminal_packet(resize).ok());

    TerminalPacket opened;
    opened.type = TerminalPacketType::opened;
    opened.stream_id = 53U;
    opened.payload.assign(48U, 0U);
    IOTOX_CHECK(!iotox::local::encode_terminal_packet(opened).ok());

    TerminalPacket gap;
    gap.type = TerminalPacketType::output_gap;
    gap.stream_id = 54U;
    gap.payload.assign(16U, 0U);
    IOTOX_CHECK(!iotox::local::encode_terminal_packet(gap).ok());

    TerminalPacket exit;
    exit.type = TerminalPacketType::exit_status;
    exit.stream_id = 55U;
    exit.payload = {1U, 0U, 0U, 0U, 0U, 0U, 0U, 0U};
    IOTOX_CHECK(!iotox::local::encode_terminal_packet(exit).ok());
}

IOTOX_TEST("local terminal OPEN modes and exit variants are exact") {
    TerminalOpenRequest open_or_resume;
    open_or_resume.peer_public_key.front() = 0x31U;
    open_or_resume.columns = 1U;
    open_or_resume.rows = 1000U;
    open_or_resume.mode = TerminalOpenMode::open_or_resume;
    IOTOX_CHECK(iotox::local::encode_terminal_open(open_or_resume).ok());

    open_or_resume.session_id.front() = 0x51U;
    IOTOX_CHECK(iotox::local::encode_terminal_open(open_or_resume).ok());

    TerminalOpenRequest invalid_new = new_request();
    invalid_new.session_id.front() = 1U;
    IOTOX_CHECK(!iotox::local::encode_terminal_open(invalid_new).ok());
    invalid_new = new_request();
    invalid_new.peer_public_key.fill(0U);
    IOTOX_CHECK(!iotox::local::encode_terminal_open(invalid_new).ok());

    TerminalOpenRequest invalid_resume;
    invalid_resume.mode = TerminalOpenMode::resume_only;
    IOTOX_CHECK(!iotox::local::encode_terminal_open(invalid_resume).ok());
    invalid_resume.session_id.front() = 1U;
    invalid_resume.columns = 0U;
    IOTOX_CHECK(!iotox::local::encode_terminal_open(invalid_resume).ok());

    TerminalExitStatus exited;
    exited.kind = 0U;
    exited.code = 255U;
    IOTOX_CHECK(iotox::local::encode_terminal_exit_status(exited).ok());

    TerminalExitStatus signaled;
    signaled.kind = 1U;
    signaled.signal = 9U;
    signaled.core_dumped = true;
    IOTOX_CHECK(iotox::local::encode_terminal_exit_status(signaled).ok());

    TerminalExitStatus unknown;
    unknown.kind = 2U;
    IOTOX_CHECK(iotox::local::encode_terminal_exit_status(unknown).ok());
    unknown.code = 1U;
    IOTOX_CHECK(!iotox::local::encode_terminal_exit_status(unknown).ok());
}
