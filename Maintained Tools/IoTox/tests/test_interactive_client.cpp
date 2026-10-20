#include "test_harness.hpp"

#include "iotox/interactive_client.hpp"
#include "iotox/protocol/ratox.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using iotox::interactive::AttachmentNonce;
using iotox::interactive::PrincipalId;
using iotox::interactive::RatoxClient;
using iotox::interactive::RatoxClientRoute;
using iotox::interactive::RatoxClientState;
using iotox::interactive::SessionId;
using iotox::protocol::ratox::Frame;
using iotox::protocol::ratox::FrameType;

void write_u16(std::span<std::uint8_t> output, std::uint16_t value) {
    output[0U] = static_cast<std::uint8_t>(value >> 8U);
    output[1U] = static_cast<std::uint8_t>(value);
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

std::uint64_t read_u64(std::span<const std::uint8_t> input) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : input.first(8U)) value = (value << 8U) | byte;
    return value;
}

template <typename Identifier>
Identifier identifier(std::uint8_t value) {
    Identifier result{};
    result.front() = value;
    result.back() = static_cast<std::uint8_t>(value ^ 0xA5U);
    return result;
}

RatoxClientRoute route(
    std::uint64_t epoch = 7U,
    PrincipalId principal = identifier<PrincipalId>(0x31U)) {
    RatoxClientRoute result;
    result.friend_number = 11U;
    result.online_epoch = epoch;
    result.principal_id = principal;
    result.transcript_confirmed = true;
    result.feature_negotiated = true;
    result.claimant_authenticated = true;
    return result;
}

Frame decode_outbound(const RatoxClient &client) {
    const auto *packet = client.peek_outbound();
    if (packet == nullptr) throw std::runtime_error("Ratox outbound queue is empty");
    auto decoded = iotox::protocol::ratox::decode(packet->bytes());
    if (!decoded) throw std::runtime_error(decoded.status().message());
    return decoded.value();
}

Frame take_outbound(RatoxClient &client) {
    Frame frame = decode_outbound(client);
    const iotox::Status popped = client.pop_outbound();
    if (!popped.ok()) throw std::runtime_error(popped.message());
    return frame;
}

std::vector<std::uint8_t> encode_frame(const Frame &frame) {
    auto encoded = iotox::protocol::ratox::encode(frame);
    if (!encoded) throw std::runtime_error(encoded.status().message());
    return encoded.value();
}

Frame open_result(
    const Frame &request,
    std::uint16_t result = 0U,
    std::uint64_t incarnation = 19U,
    std::uint64_t generation = 1U) {
    Frame frame;
    frame.type = FrameType::open_result;
    frame.message_id = 9001U;
    frame.correlation_id = request.message_id;
    frame.session_id = request.session_id;
    frame.principal_id = request.principal_id;
    frame.attachment_nonce = request.attachment_nonce;
    frame.incarnation = result == 0U ? incarnation : 0U;
    frame.generation = result == 0U ? generation : 0U;
    frame.payload.resize(12U, 0U);
    write_u16(frame.payload, result);
    if (result == 0U) {
        frame.payload[2U] = 1U;
        write_u16(std::span<std::uint8_t>{frame.payload}.subspan(4U, 2U), 80U);
        write_u16(std::span<std::uint8_t>{frame.payload}.subspan(6U, 2U), 24U);
    }
    return frame;
}

Frame resume_result(
    const Frame &request,
    std::uint64_t generation,
    std::uint64_t next_input,
    std::uint64_t output_base,
    std::uint64_t output_next,
    std::uint16_t result = 0U) {
    Frame frame;
    frame.type = FrameType::resume_result;
    frame.message_id = 9002U;
    frame.correlation_id = request.message_id;
    frame.session_id = request.session_id;
    frame.principal_id = request.principal_id;
    frame.attachment_nonce = request.attachment_nonce;
    frame.incarnation = request.incarnation;
    frame.generation = generation;
    frame.payload.resize(28U, 0U);
    write_u16(frame.payload, result);
    if (result == 0U) {
        write_u64(std::span<std::uint8_t>{frame.payload}.subspan(4U, 8U), next_input);
        write_u64(std::span<std::uint8_t>{frame.payload}.subspan(12U, 8U), output_base);
        write_u64(std::span<std::uint8_t>{frame.payload}.subspan(20U, 8U), output_next);
    }
    return frame;
}

Frame attached_frame(
    const RatoxClient &client,
    FrameType type,
    std::uint64_t message_id = 9100U) {
    const auto snapshot = client.snapshot();
    Frame frame;
    frame.type = type;
    frame.message_id = message_id;
    frame.session_id = snapshot.session_id;
    frame.principal_id = snapshot.principal_id;
    frame.attachment_nonce = snapshot.attachment_nonce;
    frame.incarnation = snapshot.incarnation;
    frame.generation = snapshot.generation;
    return frame;
}

struct AttachedClient {
    SessionId session;
    AttachmentNonce nonce;
    Frame open;
};

AttachedClient attach(
    RatoxClient &client,
    const RatoxClientRoute &active_route,
    bool drain_opened = true) {
    AttachedClient result;
    result.session = identifier<SessionId>(0x41U);
    result.nonce = identifier<AttachmentNonce>(0x51U);
    const iotox::Status begun = client.begin_open(
        active_route, result.session, result.nonce, 80U, 24U);
    if (!begun.ok()) throw std::runtime_error(begun.message());
    result.open = take_outbound(client);
    const auto response = encode_frame(open_result(result.open));
    const iotox::Status received = client.receive(active_route, response);
    if (!received.ok()) throw std::runtime_error(received.message());
    if (drain_opened) static_cast<void>(client.drain_events());
    return result;
}

void deliver(
    RatoxClient &client,
    const RatoxClientRoute &active_route,
    const Frame &frame) {
    const iotox::Status received = client.receive(active_route, encode_frame(frame));
    if (!received.ok()) throw std::runtime_error(received.message());
}

}  // namespace

IOTOX_TEST("Ratox client validates OPEN and binds the exact authenticated route") {
    RatoxClient client;
    const SessionId session = identifier<SessionId>(1U);
    const AttachmentNonce nonce = identifier<AttachmentNonce>(2U);

    RatoxClientRoute invalid = route();
    invalid.claimant_authenticated = false;
    IOTOX_CHECK(!client.begin_open(invalid, session, nonce, 80U, 24U).ok());
    IOTOX_CHECK(!client.begin_open(route(), SessionId{}, nonce, 80U, 24U).ok());
    IOTOX_CHECK(!client.begin_open(route(), session, nonce, 0U, 24U).ok());

    IOTOX_CHECK(client.begin_open(route(), session, nonce, 80U, 24U).ok());
    const auto snapshot = client.snapshot();
    IOTOX_CHECK(snapshot.state == RatoxClientState::opening);
    IOTOX_CHECK(snapshot.route_present);
    IOTOX_CHECK(snapshot.peer_present);
    IOTOX_CHECK(snapshot.outbound_packets == 1U);

    const Frame open = decode_outbound(client);
    IOTOX_CHECK(open.type == FrameType::open);
    IOTOX_CHECK(open.session_id == session);
    IOTOX_CHECK(open.principal_id == route().principal_id);
    IOTOX_CHECK(open.attachment_nonce == nonce);
    IOTOX_CHECK(open.payload.size() == 12U);
    IOTOX_CHECK(read_u16(std::span<const std::uint8_t>{open.payload}.subspan(2U, 2U)) == 80U);
    IOTOX_CHECK(read_u16(std::span<const std::uint8_t>{open.payload}.subspan(4U, 2U)) == 24U);
}

IOTOX_TEST("Ratox client rejects stale identities without destroying a live OPEN") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    const SessionId session = identifier<SessionId>(3U);
    const AttachmentNonce nonce = identifier<AttachmentNonce>(4U);
    IOTOX_CHECK(client.begin_open(active_route, session, nonce, 80U, 24U).ok());
    const Frame open = take_outbound(client);

    Frame stale = open_result(open);
    stale.attachment_nonce = identifier<AttachmentNonce>(0xEEU);
    auto rejected = client.receive(active_route, encode_frame(stale));
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::opening);
    IOTOX_CHECK(client.snapshot().route_present);

    Frame wrong_correlation = open_result(open);
    ++wrong_correlation.correlation_id;
    rejected = client.receive(active_route, encode_frame(wrong_correlation));
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::opening);

    deliver(client, active_route, open_result(open));
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);

    // A duplicate result is stale but cannot tear down the established stream.
    rejected = client.receive(active_route, encode_frame(open_result(open)));
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);
    IOTOX_CHECK(client.snapshot().route_present);
}

IOTOX_TEST("Ratox client retains input and fences exact duplicate output bytes") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));

    const std::vector<std::uint8_t> input(
        iotox::protocol::ratox::kMaximumPayloadBytes + 13U, 0xA5U);
    IOTOX_CHECK(client.enqueue_input(input).ok());
    IOTOX_CHECK(client.snapshot().input.pending_bytes == input.size());
    IOTOX_CHECK(client.snapshot().outbound_packets == 2U);

    const Frame first = take_outbound(client);
    IOTOX_CHECK(first.type == FrameType::input);
    IOTOX_CHECK(first.sequence == 1U);
    IOTOX_CHECK(first.payload.size() == iotox::protocol::ratox::kMaximumPayloadBytes);
    const Frame second = take_outbound(client);
    IOTOX_CHECK(second.type == FrameType::input);
    IOTOX_CHECK(second.sequence == 1U + first.payload.size());
    IOTOX_CHECK(second.payload.size() == 13U);

    Frame acknowledgement = attached_frame(client, FrameType::input_ack);
    acknowledgement.acknowledgement = 1U + input.size();
    deliver(client, active_route, acknowledgement);
    IOTOX_CHECK(client.snapshot().input.pending_bytes == 0U);

    Frame output = attached_frame(client, FrameType::output, 9200U);
    output.sequence = 1U;
    output.payload = {'o', 'k'};
    deliver(client, active_route, output);
    deliver(client, active_route, output);
    auto replay = client.read_output(1U, 16U);
    IOTOX_CHECK(replay.ok());
    IOTOX_CHECK(replay.value().bytes == output.payload);

    Frame conflict = output;
    conflict.message_id = 9201U;
    conflict.payload.back() ^= 1U;
    auto rejected = client.receive(active_route, encode_frame(conflict));
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::failed);
    IOTOX_CHECK(!client.snapshot().route_present);
    IOTOX_CHECK(client.snapshot().outbound_packets == 0U);
}

IOTOX_TEST("Ratox client validates overlapping output before appending its suffix") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));

    Frame first = attached_frame(client, FrameType::output, 9250U);
    first.sequence = 1U;
    first.payload = {'a', 'b', 'c'};
    deliver(client, active_route, first);

    Frame overlap = attached_frame(client, FrameType::output, 9251U);
    overlap.sequence = 2U;
    overlap.payload = {'b', 'c', 'd', 'e'};
    deliver(client, active_route, overlap);

    auto replay = client.read_output(1U, 16U);
    IOTOX_CHECK(replay.ok());
    IOTOX_CHECK(
        replay.value().bytes ==
        std::vector<std::uint8_t>({'a', 'b', 'c', 'd', 'e'}));

    const auto events = client.drain_events();
    IOTOX_CHECK(events.size() == 1U);
    IOTOX_CHECK(events.front().kind ==
                iotox::interactive::RatoxClientEventKind::output_available);
    IOTOX_CHECK(events.front().sequence == 1U);
    IOTOX_CHECK(events.front().acknowledgement == 6U);
}

IOTOX_TEST("Ratox client output ACK is atomic with outbound queue capacity") {
    RatoxClient::Config config;
    config.maximum_outbound_packets = 1U;
    config.maximum_outbound_bytes =
        2U * iotox::protocol::ratox::kMaximumPacketBytes;
    RatoxClient client(config);
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));

    Frame output = attached_frame(client, FrameType::output, 9260U);
    output.sequence = 1U;
    output.payload = {'x', 'y'};
    deliver(client, active_route, output);
    IOTOX_CHECK(client.resize(120U, 40U).ok());

    const iotox::Status saturated = client.acknowledge_output(3U);
    IOTOX_CHECK(!saturated.ok());
    IOTOX_CHECK(saturated.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);
    IOTOX_CHECK(client.snapshot().output.base_sequence == 1U);
    IOTOX_CHECK(client.snapshot().output.pending_bytes == 2U);

    IOTOX_CHECK(take_outbound(client).type == FrameType::resize);
    IOTOX_CHECK(client.acknowledge_output(3U).ok());
    IOTOX_CHECK(client.snapshot().output.base_sequence == 3U);
    IOTOX_CHECK(client.snapshot().output.pending_bytes == 0U);
    const Frame acknowledgement = take_outbound(client);
    IOTOX_CHECK(acknowledgement.type == FrameType::output_ack);
    IOTOX_CHECK(acknowledgement.acknowledgement == 3U);
}

IOTOX_TEST("Ratox client coalesces cumulative output ACKs and latest resize") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));

    IOTOX_CHECK(client.resize(80U, 24U).ok());
    const std::uint64_t resize_message = decode_outbound(client).message_id;
    IOTOX_CHECK(client.resize(120U, 40U).ok());
    IOTOX_CHECK(client.snapshot().outbound_packets == 1U);
    Frame resized = decode_outbound(client);
    IOTOX_CHECK(resized.type == FrameType::resize);
    IOTOX_CHECK(resized.message_id == resize_message);
    IOTOX_CHECK(read_u16(resized.payload) == 120U);
    IOTOX_CHECK(read_u16(std::span<const std::uint8_t>{resized.payload}.subspan(2U, 2U)) == 40U);
    IOTOX_CHECK(client.pop_outbound().ok());

    for (std::uint64_t sequence = 1U; sequence <= 32U; ++sequence) {
        Frame output = attached_frame(client, FrameType::output, 9300U + sequence);
        output.sequence = sequence;
        output.payload = {static_cast<std::uint8_t>(sequence)};
        deliver(client, active_route, output);
        IOTOX_CHECK(client.acknowledge_output(sequence + 1U).ok());
    }
    IOTOX_CHECK(client.snapshot().outbound_packets == 1U);
    const Frame ack = decode_outbound(client);
    IOTOX_CHECK(ack.type == FrameType::output_ack);
    IOTOX_CHECK(ack.acknowledgement == 33U);
    IOTOX_CHECK(client.snapshot().output.base_sequence == 33U);
    IOTOX_CHECK(client.snapshot().output.pending_bytes == 0U);

    const auto events = client.drain_events();
    IOTOX_CHECK(events.size() == 1U);
    IOTOX_CHECK(events.front().kind ==
                iotox::interactive::RatoxClientEventKind::output_available);
    IOTOX_CHECK(events.front().sequence == 1U);
    IOTOX_CHECK(events.front().acknowledgement == 33U);
}

IOTOX_TEST("Ratox client reuses one exact heartbeat for an attachment") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    IOTOX_CHECK(!client.ping().ok());
    static_cast<void>(attach(client, active_route));

    IOTOX_CHECK(client.ping().ok());
    const auto first_snapshot = client.snapshot();
    IOTOX_CHECK(first_snapshot.heartbeat_message_id != 0U);
    IOTOX_CHECK(first_snapshot.heartbeat_queued);
    IOTOX_CHECK(first_snapshot.outbound_packets == 1U);
    const Frame first = decode_outbound(client);
    const std::vector<std::uint8_t> canonical = encode_frame(first);
    IOTOX_CHECK(first.type == FrameType::ping);
    IOTOX_CHECK(first.payload.empty());
    IOTOX_CHECK(first.message_id == first_snapshot.heartbeat_message_id);

    // Multiple local samplers coalesce while the retained transport head has
    // not yet been accepted.
    IOTOX_CHECK(client.ping().ok());
    IOTOX_CHECK(client.snapshot().outbound_packets == 1U);
    IOTOX_CHECK(encode_frame(take_outbound(client)) == canonical);
    IOTOX_CHECK(!client.snapshot().heartbeat_queued);

    // A timeout retry is the byte-identical request, not a fresh permanent
    // exact-control replay entry at the service.
    IOTOX_CHECK(client.ping().ok());
    IOTOX_CHECK(encode_frame(take_outbound(client)) == canonical);

    Frame wrong = attached_frame(client, FrameType::pong, 9600U);
    wrong.correlation_id = first.message_id + 1U;
    const iotox::Status rejected = client.receive(
        active_route, encode_frame(wrong));
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);

    Frame pong = wrong;
    pong.correlation_id = first.message_id;
    deliver(client, active_route, pong);
    auto events = client.drain_events();
    IOTOX_CHECK(events.size() == 1U);
    IOTOX_CHECK(events.front().kind ==
                iotox::interactive::RatoxClientEventKind::pong);

    // Thousands of completed samples retain the same request ID and bytes.
    // The next unrelated control proves no heartbeat iteration allocated an
    // additional message ID.
    for (std::size_t sample = 0U; sample < 2048U; ++sample) {
        IOTOX_CHECK(client.ping().ok());
        IOTOX_CHECK(encode_frame(take_outbound(client)) == canonical);
        deliver(client, active_route, pong);
        events = client.drain_events();
        IOTOX_CHECK(events.size() == 1U);
        IOTOX_CHECK(events.front().kind ==
                    iotox::interactive::RatoxClientEventKind::pong);
    }
    IOTOX_CHECK(client.resize(100U, 30U).ok());
    const Frame resize = take_outbound(client);
    IOTOX_CHECK(resize.type == FrameType::resize);
    IOTOX_CHECK(resize.message_id == first.message_id + 1U);
}

IOTOX_TEST("Ratox client eventually queues DETACH behind saturated retained input") {
    RatoxClient::Config config;
    config.maximum_outbound_packets = 2U;
    config.maximum_outbound_bytes = 8U * iotox::protocol::ratox::kMaximumPacketBytes;
    RatoxClient client(config);
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));

    const std::vector<std::uint8_t> input(
        3U * iotox::protocol::ratox::kMaximumPayloadBytes, 0x5AU);
    IOTOX_CHECK(client.enqueue_input(input).ok());
    IOTOX_CHECK(client.snapshot().outbound_packets == 2U);

    IOTOX_CHECK(client.detach().ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);
    IOTOX_CHECK(client.pop_outbound().ok());
    IOTOX_CHECK(client.service().ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::detached);
    IOTOX_CHECK(client.snapshot().outbound_packets == 2U);

    IOTOX_CHECK(take_outbound(client).type == FrameType::input);
    IOTOX_CHECK(take_outbound(client).type == FrameType::detach);
    const auto events = client.drain_events();
    IOTOX_CHECK(events.size() == 1U);
    IOTOX_CHECK(events.front().kind ==
                iotox::interactive::RatoxClientEventKind::detached);
}

IOTOX_TEST("Ratox client fails closed when message IDs are exhausted") {
    RatoxClient::Config config;
    config.initial_message_id = std::numeric_limits<std::uint64_t>::max();
    RatoxClient client(config);
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));

    const std::vector<std::uint8_t> input{'x'};
    const iotox::Status queued = client.enqueue_input(input);
    IOTOX_CHECK(!queued.ok());
    IOTOX_CHECK(queued.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::failed);
    IOTOX_CHECK(!client.snapshot().route_present);
    IOTOX_CHECK(client.snapshot().outbound_packets == 0U);
    IOTOX_CHECK(client.snapshot().input.pending_bytes == 1U);
}

IOTOX_TEST("Ratox client route loss preserves only safely resumable state") {
    RatoxClient opening;
    const RatoxClientRoute first_route = route(20U);
    IOTOX_CHECK(opening.begin_open(
        first_route, identifier<SessionId>(9U),
        identifier<AttachmentNonce>(10U), 80U, 24U).ok());
    IOTOX_CHECK(opening.peer_offline(
        first_route.friend_number, first_route.online_epoch).ok());
    IOTOX_CHECK(opening.snapshot().state == RatoxClientState::failed);
    IOTOX_CHECK(!opening.snapshot().route_present);
    IOTOX_CHECK(opening.snapshot().outbound_packets == 0U);

    RatoxClient client;
    static_cast<void>(attach(client, first_route));
    IOTOX_CHECK(client.enqueue_input(
        std::vector<std::uint8_t>{'a', 'b', 'c'}).ok());
    while (client.peek_outbound() != nullptr) IOTOX_CHECK(client.pop_outbound().ok());

    Frame output = attached_frame(client, FrameType::output);
    output.sequence = 1U;
    output.payload = {'x', 'y', 'z'};
    deliver(client, first_route, output);
    IOTOX_CHECK(client.acknowledge_output(2U).ok());
    IOTOX_CHECK(client.peer_offline(
        first_route.friend_number, first_route.online_epoch).ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::detached);
    IOTOX_CHECK(client.snapshot().peer_present);
    IOTOX_CHECK(!client.snapshot().route_present);
    IOTOX_CHECK(client.snapshot().input.pending_bytes == 3U);
    IOTOX_CHECK(client.snapshot().output.base_sequence == 2U);
    IOTOX_CHECK(client.snapshot().output.pending_bytes == 2U);
    static_cast<void>(client.drain_events());

    RatoxClientRoute resumed_route = first_route;
    resumed_route.online_epoch = 21U;
    const AttachmentNonce resumed_nonce = identifier<AttachmentNonce>(0x77U);
    IOTOX_CHECK(client.begin_resume(resumed_route, resumed_nonce).ok());
    const Frame resume = take_outbound(client);
    IOTOX_CHECK(resume.type == FrameType::resume);
    IOTOX_CHECK(resume.incarnation == 19U);
    IOTOX_CHECK(resume.generation == 1U);
    IOTOX_CHECK(read_u64(resume.payload) == 1U);
    IOTOX_CHECK(read_u64(std::span<const std::uint8_t>{resume.payload}.subspan(8U, 8U)) == 2U);

    deliver(client, resumed_route, resume_result(
        resume, 2U, 2U, 3U, 5U));
    const auto snapshot = client.snapshot();
    IOTOX_CHECK(snapshot.state == RatoxClientState::attached);
    IOTOX_CHECK(snapshot.generation == 2U);
    IOTOX_CHECK(snapshot.input.base_sequence == 2U);
    IOTOX_CHECK(snapshot.input.pending_bytes == 2U);
    // The remote has evicted byte 2, but that byte and the overlap at 3
    // remain locally retained. Resume preserves them instead of manufacturing
    // a local gap; the remote suffix will be overlap-validated.
    IOTOX_CHECK(snapshot.output.base_sequence == 2U);
    IOTOX_CHECK(snapshot.output.next_sequence == 4U);
    IOTOX_CHECK(snapshot.output.pending_bytes == 2U);

    const auto events = client.drain_events();
    IOTOX_CHECK(events.size() == 1U);
    IOTOX_CHECK(events[0U].kind ==
                iotox::interactive::RatoxClientEventKind::resumed);
    IOTOX_CHECK(events[0U].acknowledgement == 2U);

    Frame resumed_output = attached_frame(client, FrameType::output, 9350U);
    resumed_output.sequence = 3U;
    resumed_output.payload = {'z', 'w'};
    deliver(client, resumed_route, resumed_output);
    auto retained_output = client.read_output(2U, 8U);
    IOTOX_CHECK(retained_output.ok());
    IOTOX_CHECK(retained_output.value().bytes ==
                std::vector<std::uint8_t>({'y', 'z', 'w'}));

    const Frame replay = decode_outbound(client);
    IOTOX_CHECK(replay.type == FrameType::input);
    IOTOX_CHECK(replay.sequence == 2U);
    IOTOX_CHECK(replay.payload == std::vector<std::uint8_t>({'b', 'c'}));
}

IOTOX_TEST("Ratox client rejects nonadvancing resume generations fail closed") {
    RatoxClient client;
    RatoxClientRoute first_route = route(30U);
    static_cast<void>(attach(client, first_route));
    IOTOX_CHECK(client.peer_offline(
        first_route.friend_number, first_route.online_epoch).ok());
    static_cast<void>(client.drain_events());

    RatoxClientRoute next_route = first_route;
    next_route.online_epoch = 31U;
    IOTOX_CHECK(client.begin_resume(
        next_route, identifier<AttachmentNonce>(0x88U)).ok());
    const Frame resume = take_outbound(client);
    auto rejected = client.receive(
        next_route, encode_frame(resume_result(resume, 1U, 1U, 1U, 1U)));
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::failed);
    IOTOX_CHECK(!client.snapshot().route_present);
}

IOTOX_TEST("Ratox client validates complete resume coordinates before releasing replay") {
    RatoxClient client;
    RatoxClientRoute first_route = route(40U);
    static_cast<void>(attach(client, first_route));

    IOTOX_CHECK(client.enqueue_input(
        std::vector<std::uint8_t>{'a', 'b', 'c'}).ok());
    while (client.peek_outbound() != nullptr) {
        IOTOX_CHECK(client.pop_outbound().ok());
    }

    Frame output = attached_frame(client, FrameType::output, 9360U);
    output.sequence = 1U;
    output.payload = {'x', 'y', 'z'};
    deliver(client, first_route, output);
    IOTOX_CHECK(client.peer_offline(
        first_route.friend_number, first_route.online_epoch).ok());
    static_cast<void>(client.drain_events());

    RatoxClientRoute resumed_route = first_route;
    resumed_route.online_epoch = 41U;
    IOTOX_CHECK(client.begin_resume(
        resumed_route, identifier<AttachmentNonce>(0x89U)).ok());
    const Frame resume = take_outbound(client);
    const auto before = client.snapshot();
    IOTOX_CHECK(before.state == RatoxClientState::resuming);
    IOTOX_CHECK(before.input.base_sequence == 1U);
    IOTOX_CHECK(before.input.next_sequence == 4U);
    IOTOX_CHECK(before.input_send_cursor == 1U);
    IOTOX_CHECK(before.output.next_sequence == 4U);

    // The input acknowledgement is individually valid, but output_next lies
    // behind already retained output. The entire response must be rejected
    // without committing the earlier input coordinate.
    const iotox::Status rejected = client.receive(
        resumed_route,
        encode_frame(resume_result(resume, 2U, 2U, 1U, 3U)));
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.code() == iotox::ErrorCode::protocol_error);

    const auto after = client.snapshot();
    IOTOX_CHECK(after.state == RatoxClientState::failed);
    IOTOX_CHECK(!after.route_present);
    IOTOX_CHECK(after.generation == before.generation);
    IOTOX_CHECK(after.input.base_sequence == before.input.base_sequence);
    IOTOX_CHECK(after.input.next_sequence == before.input.next_sequence);
    IOTOX_CHECK(after.input.pending_bytes == before.input.pending_bytes);
    IOTOX_CHECK(after.input_send_cursor == before.input_send_cursor);
    IOTOX_CHECK(after.output.base_sequence == before.output.base_sequence);
    IOTOX_CHECK(after.output.next_sequence == before.output.next_sequence);
    IOTOX_CHECK(after.output.pending_bytes == before.output.pending_bytes);
}

IOTOX_TEST("Ratox client never discards retained output on remote GAP reports") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));

    Frame output = attached_frame(client, FrameType::output);
    output.sequence = 1U;
    output.payload = {'a', 'b', 'c'};
    deliver(client, active_route, output);
    static_cast<void>(client.drain_events());

    Frame stale_gap = attached_frame(client, FrameType::output_gap, 9400U);
    stale_gap.sequence = 1U;
    stale_gap.acknowledgement = 4U;
    deliver(client, active_route, stale_gap);
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);
    IOTOX_CHECK(client.snapshot().output.pending_bytes == 3U);

    Frame overlapping_gap = stale_gap;
    overlapping_gap.message_id = 9401U;
    overlapping_gap.sequence = 2U;
    overlapping_gap.acknowledgement = 8U;
    deliver(client, active_route, overlapping_gap);
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);
    IOTOX_CHECK(client.snapshot().output.pending_bytes == 3U);

    Frame destructive_gap = stale_gap;
    destructive_gap.message_id = 9402U;
    destructive_gap.sequence = 5U;
    destructive_gap.acknowledgement = 8U;
    auto rejected = client.receive(active_route, encode_frame(destructive_gap));
    IOTOX_CHECK_MSG(
        !rejected.ok(),
        "state=" + std::string(iotox::interactive::to_string(client.snapshot().state)) +
            " base=" + std::to_string(client.snapshot().output.base_sequence) +
            " next=" + std::to_string(client.snapshot().output.next_sequence));
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::failed);
    auto replay = client.read_output(1U, 8U);
    IOTOX_CHECK(replay.ok());
    IOTOX_CHECK(replay.value().bytes == output.payload);
}

IOTOX_TEST("Ratox client accepts one EXIT event and drops queued effects") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    static_cast<void>(attach(client, active_route));
    IOTOX_CHECK(client.enqueue_input(
        std::vector<std::uint8_t>{'q'}).ok());
    IOTOX_CHECK(client.snapshot().outbound_packets == 1U);

    Frame exit = attached_frame(client, FrameType::exit_status, 9500U);
    exit.payload.resize(8U, 0U);
    exit.payload[0U] = 0U;
    exit.payload[4U] = 0U;
    exit.payload[5U] = 0U;
    exit.payload[6U] = 0U;
    exit.payload[7U] = 17U;
    deliver(client, active_route, exit);
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::exited);
    IOTOX_CHECK(!client.snapshot().route_present);
    IOTOX_CHECK(client.snapshot().outbound_packets == 0U);

    const auto first_events = client.drain_events();
    IOTOX_CHECK(first_events.size() == 1U);
    IOTOX_CHECK(first_events.front().kind ==
                iotox::interactive::RatoxClientEventKind::exit_status);
    IOTOX_CHECK(first_events.front().exit_code == 17U);

    // Exact duplicate completion evidence is idempotent.
    const iotox::Status duplicate = client.receive(active_route, encode_frame(exit));
    IOTOX_CHECK(!duplicate.ok());
    IOTOX_CHECK(client.drain_events().empty());
}

IOTOX_TEST("Ratox client retains correlated requests only until result evidence") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    const SessionId session = identifier<SessionId>(0x61U);
    const AttachmentNonce nonce = identifier<AttachmentNonce>(0x62U);
    IOTOX_CHECK(client.begin_open(active_route, session, nonce, 80U, 24U).ok());
    const Frame request = decode_outbound(client);
    IOTOX_CHECK(client.snapshot().outbound_packets == 1U);

    deliver(client, active_route, open_result(request));
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::attached);
    IOTOX_CHECK(client.snapshot().outbound_packets == 0U);
}

IOTOX_TEST("Ratox client RESUME preflight is transactional under backpressure") {
    RatoxClient::Config config;
    config.maximum_outbound_packets = 1U;
    config.maximum_outbound_bytes =
        2U * iotox::protocol::ratox::kMaximumPacketBytes;
    RatoxClient client(config);
    const RatoxClientRoute active_route = route(70U);
    const AttachedClient attached = attach(client, active_route);

    IOTOX_CHECK(client.detach().ok());
    const auto before = client.snapshot();
    IOTOX_CHECK(before.state == RatoxClientState::detached);
    IOTOX_CHECK(before.outbound_packets == 1U);
    IOTOX_CHECK(decode_outbound(client).type == FrameType::detach);

    const AttachmentNonce replacement = identifier<AttachmentNonce>(0x91U);
    const iotox::Status blocked = client.begin_resume(active_route, replacement);
    IOTOX_CHECK(!blocked.ok());
    IOTOX_CHECK(blocked.code() == iotox::ErrorCode::resource_exhausted);
    const auto after = client.snapshot();
    IOTOX_CHECK(after.state == RatoxClientState::detached);
    IOTOX_CHECK(after.route_present == before.route_present);
    IOTOX_CHECK(after.route == before.route);
    IOTOX_CHECK(after.session_id == attached.session);
    IOTOX_CHECK(after.attachment_nonce == attached.nonce);
    IOTOX_CHECK(after.input_send_cursor == before.input_send_cursor);
    IOTOX_CHECK(after.outbound_packets == 1U);
    IOTOX_CHECK(decode_outbound(client).type == FrameType::detach);

    IOTOX_CHECK(client.pop_outbound().ok());
    IOTOX_CHECK(client.begin_resume(active_route, replacement).ok());
    IOTOX_CHECK(client.snapshot().state == RatoxClientState::resuming);
    IOTOX_CHECK(client.snapshot().attachment_nonce == replacement);
}

IOTOX_TEST("Ratox client OPEN exhaustion preserves the completed prior state") {
    RatoxClient::Config config;
    config.initial_message_id = std::numeric_limits<std::uint64_t>::max();
    RatoxClient client(config);
    const RatoxClientRoute active_route = route();
    const AttachedClient attached = attach(client, active_route);

    Frame exit = attached_frame(client, FrameType::exit_status, 9800U);
    exit.payload.resize(8U, 0U);
    deliver(client, active_route, exit);
    static_cast<void>(client.drain_events());
    const auto before = client.snapshot();
    IOTOX_CHECK(before.state == RatoxClientState::exited);

    const iotox::Status exhausted = client.begin_open(
        active_route, identifier<SessionId>(0xA1U),
        identifier<AttachmentNonce>(0xA2U), 100U, 30U);
    IOTOX_CHECK(!exhausted.ok());
    IOTOX_CHECK(exhausted.code() == iotox::ErrorCode::resource_exhausted);
    const auto after = client.snapshot();
    IOTOX_CHECK(after.state == RatoxClientState::exited);
    IOTOX_CHECK(after.session_id == attached.session);
    IOTOX_CHECK(after.attachment_nonce == attached.nonce);
    IOTOX_CHECK(after.outbound_packets == 0U);
}

IOTOX_TEST("Ratox client wipes nonresumable identity after OPEN denial") {
    RatoxClient client;
    const RatoxClientRoute active_route = route();
    IOTOX_CHECK(client.begin_open(
        active_route, identifier<SessionId>(0xB1U),
        identifier<AttachmentNonce>(0xB2U), 80U, 24U).ok());
    const Frame request = decode_outbound(client);
    const iotox::Status denied = client.receive(
        active_route, encode_frame(open_result(request, 1U)));
    IOTOX_CHECK(!denied.ok());
    const auto snapshot = client.snapshot();
    IOTOX_CHECK(snapshot.state == RatoxClientState::failed);
    IOTOX_CHECK(!snapshot.route_present);
    IOTOX_CHECK(!snapshot.peer_present);
    IOTOX_CHECK(std::all_of(
        snapshot.principal_id.begin(), snapshot.principal_id.end(),
        [](std::uint8_t byte) { return byte == 0U; }));
    IOTOX_CHECK(std::all_of(
        snapshot.session_id.begin(), snapshot.session_id.end(),
        [](std::uint8_t byte) { return byte == 0U; }));
    IOTOX_CHECK(std::all_of(
        snapshot.attachment_nonce.begin(), snapshot.attachment_nonce.end(),
        [](std::uint8_t byte) { return byte == 0U; }));
    IOTOX_CHECK(snapshot.outbound_packets == 0U);
}
