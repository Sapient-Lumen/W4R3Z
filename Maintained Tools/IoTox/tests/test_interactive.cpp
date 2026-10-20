#include "test_harness.hpp"

#include "iotox/interactive.hpp"
#include "iotox/interactive_session.hpp"
#include "iotox/protocol/ratox.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <limits>
#include <vector>

namespace {

iotox::protocol::ratox::Frame attached_ratox_frame(
    iotox::protocol::ratox::FrameType type) {
    iotox::protocol::ratox::Frame frame;
    frame.type = type;
    frame.message_id = 0x0102030405060708ULL;
    frame.session_id.front() = 0x11U;
    frame.principal_id.front() = 0x22U;
    frame.attachment_nonce.front() = 0x33U;
    frame.incarnation = 7U;
    frame.generation = 9U;
    return frame;
}

iotox::interactive::SessionId test_session_id(std::uint8_t value) {
    iotox::interactive::SessionId result{};
    result.front() = value;
    return result;
}

iotox::interactive::PrincipalId test_principal_id(std::uint8_t value) {
    iotox::interactive::PrincipalId result{};
    result.front() = value;
    return result;
}

iotox::interactive::AttachmentNonce test_attachment_nonce(std::uint8_t value) {
    iotox::interactive::AttachmentNonce result{};
    result.front() = value;
    return result;
}

void exercise_two_packet_split_range(
    std::size_t first_begin, std::size_t first_end) {
    using namespace iotox::interactive;
    constexpr std::size_t maximum = 1076U;
    const std::vector<std::uint8_t> payload(maximum, 0xA5U);
    const std::vector<std::uint8_t> overlap{0x5AU, 0x5BU};
    const std::vector<std::uint8_t> one{0xCCU};

    IOTOX_CHECK(first_begin >= 1U);
    IOTOX_CHECK(first_begin <= first_end);
    IOTOX_CHECK(first_end <= maximum);
    for (std::size_t first_size = first_begin;
         first_size <= first_end; ++first_size) {
        for (std::size_t second_size = 1U;
             second_size <= maximum; ++second_size) {
            const std::size_t total = first_size + second_size;
            InputReceiver receiver({maximum, 1U});
            IOTOX_CHECK(receiver.offer(
                1U, std::span<const std::uint8_t>{
                    payload.data(), first_size}).ok());
            IOTOX_CHECK(receiver.consume_staged(first_size).value().committed);
            IOTOX_CHECK(receiver.offer(
                1U + first_size, std::span<const std::uint8_t>{
                    payload.data(), second_size}).ok());
            IOTOX_CHECK(receiver.consume_staged(second_size).value().committed);
            IOTOX_CHECK(receiver.snapshot().next_expected_sequence == total + 1U);

            auto duplicate = receiver.offer(
                1U, std::span<const std::uint8_t>{payload.data(), first_size});
            IOTOX_CHECK(duplicate.ok());
            IOTOX_CHECK(duplicate.value().disposition ==
                        InputDisposition::duplicate);
            auto future = receiver.offer(total + 2U, one);
            IOTOX_CHECK(future.ok());
            IOTOX_CHECK(future.value().disposition ==
                        InputDisposition::future_gap);
            auto partial_overlap = receiver.offer(total, overlap);
            IOTOX_CHECK(!partial_overlap.ok());
            IOTOX_CHECK(partial_overlap.status().code() ==
                        iotox::ErrorCode::protocol_error);
        }
    }
}

}  // namespace

IOTOX_TEST("interactive diagnostic probes are fixed and carrier separated") {
    using namespace iotox::interactive;
    const ProbePacket original{
        ProbeCarrier::lossy, ProbeKind::reply, 0x0102030405060708ULL};
    auto encoded = encode_probe(original);
    IOTOX_CHECK(encoded.ok());
    IOTOX_CHECK(encoded.value()[0] == kLossyProbePacketId);
    IOTOX_CHECK(encoded.value().size() == kProbePacketSize);
    auto decoded = decode_probe(encoded.value(), ProbeCarrier::lossy);
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value().carrier == ProbeCarrier::lossy);
    IOTOX_CHECK(decoded.value().kind == ProbeKind::reply);
    IOTOX_CHECK(decoded.value().nonce == original.nonce);
    IOTOX_CHECK(!decode_probe(encoded.value(), ProbeCarrier::lossless).ok());
    IOTOX_CHECK(!encode_probe(
        ProbePacket{ProbeCarrier::lossless, ProbeKind::request, 0U}).ok());
    IOTOX_CHECK(!encode_probe(ProbePacket{
        static_cast<ProbeCarrier>(99U), ProbeKind::request, 1U}).ok());
    IOTOX_CHECK(!decode_probe(
        encoded.value(), static_cast<ProbeCarrier>(99U)).ok());

    auto sized = encode_sized_probe(original, 1200U);
    IOTOX_CHECK(sized.ok());
    IOTOX_CHECK(sized.value().size() == 1200U);
    auto sized_decoded = decode_sized_probe(
        sized.value(), ProbeCarrier::lossy);
    IOTOX_CHECK(sized_decoded.ok());
    IOTOX_CHECK(sized_decoded.value().nonce == original.nonce);
    sized.value().back() ^= 1U;
    IOTOX_CHECK(!decode_sized_probe(
        sized.value(), ProbeCarrier::lossy).ok());
    IOTOX_CHECK(!encode_sized_probe(original, 9U).ok());
    IOTOX_CHECK(!encode_sized_probe(original, 1201U).ok());
}

IOTOX_TEST("interactive attachment generations fence stale controllers") {
    iotox::interactive::SessionId session{};
    session.front() = 1U;
    iotox::interactive::AttachmentFence fence(session, 7U);

    iotox::interactive::PrincipalId principal{};
    principal.front() = 2U;
    iotox::interactive::AttachmentNonce first_nonce{};
    first_nonce.front() = 3U;
    auto first = fence.attach(principal, first_nonce);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(first.value().generation == 1U);
    IOTOX_CHECK(fence.validate(first.value()).ok());

    iotox::interactive::AttachmentNonce second_nonce{};
    second_nonce.front() = 4U;
    auto second = fence.attach(principal, second_nonce);
    IOTOX_CHECK(second.ok());
    IOTOX_CHECK(second.value().generation == 2U);
    IOTOX_CHECK(!fence.validate(first.value()).ok());
    IOTOX_CHECK(fence.validate(second.value()).ok());
    IOTOX_CHECK(!fence.detach(first.value()).ok());
    IOTOX_CHECK(fence.detach(second.value()).ok());
    IOTOX_CHECK(!fence.attached());
}

IOTOX_TEST("interactive replay retains every unacknowledged input byte") {
    iotox::interactive::ByteReplayWindow replay({6U, 10U});
    const std::vector<std::uint8_t> first{'a', 'b', 'c'};
    const std::vector<std::uint8_t> second{'d', 'e', 'f'};
    IOTOX_CHECK(replay.append(first).value() == 10U);
    IOTOX_CHECK(replay.append(second).value() == 13U);

    const std::vector<std::uint8_t> overflow{'g'};
    auto refused = replay.append(overflow);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::resource_exhausted);

    auto partial = replay.replay_from(12U, 3U);
    IOTOX_CHECK(partial.ok());
    IOTOX_CHECK(partial.value().first_sequence == 12U);
    IOTOX_CHECK(partial.value().next_sequence == 15U);
    IOTOX_CHECK(!partial.value().complete);
    IOTOX_CHECK(partial.value().bytes ==
                std::vector<std::uint8_t>({'c', 'd', 'e'}));

    IOTOX_CHECK(replay.acknowledge(13U).ok());
    IOTOX_CHECK(replay.snapshot().pending_bytes == 3U);
    IOTOX_CHECK(replay.append(overflow).ok());
    auto gap = replay.replay_from(12U, 8U);
    IOTOX_CHECK(!gap.ok());
    IOTOX_CHECK(gap.status().code() == iotox::ErrorCode::not_found);
    IOTOX_CHECK(!replay.acknowledge(99U).ok());
}

IOTOX_TEST("interactive input receiver stages commits and classifies replay") {
    using namespace iotox::interactive;
    InputReceiver receiver({4U, 10U});
    const std::vector<std::uint8_t> first{'a', 'b', 'c'};
    auto staged = receiver.offer(10U, first);
    IOTOX_CHECK(staged.ok());
    IOTOX_CHECK(staged.value().disposition == InputDisposition::staged);
    IOTOX_CHECK(staged.value().acknowledgement == 10U);

    auto pending = receiver.offer(10U, first);
    IOTOX_CHECK(pending.ok());
    IOTOX_CHECK(pending.value().disposition == InputDisposition::pending);
    const std::vector<std::uint8_t> changed{'a', 'b', 'd'};
    IOTOX_CHECK(!receiver.offer(10U, changed).ok());
    const std::vector<std::uint8_t> future{'d'};
    auto gap = receiver.offer(13U, future);
    IOTOX_CHECK(gap.ok());
    IOTOX_CHECK(gap.value().disposition == InputDisposition::future_gap);

    auto partial = receiver.consume_staged(1U);
    IOTOX_CHECK(partial.ok());
    IOTOX_CHECK(!partial.value().committed);
    IOTOX_CHECK(partial.value().acknowledgement == 10U);
    IOTOX_CHECK(partial.value().remaining_bytes == 2U);
    IOTOX_CHECK(receiver.pending_bytes().value() ==
                std::vector<std::uint8_t>({'b', 'c'}));
    IOTOX_CHECK(!receiver.consume_staged(3U).ok());

    auto committed = receiver.consume_staged(2U);
    IOTOX_CHECK(committed.ok());
    IOTOX_CHECK(committed.value().committed);
    IOTOX_CHECK(committed.value().acknowledgement == 13U);
    IOTOX_CHECK(!receiver.pending_bytes().ok());

    auto duplicate = receiver.offer(10U, first);
    IOTOX_CHECK(duplicate.ok());
    IOTOX_CHECK(duplicate.value().disposition == InputDisposition::duplicate);
    const std::vector<std::uint8_t> overlap{'c', 'd'};
    auto rejected_overlap = receiver.offer(12U, overlap);
    IOTOX_CHECK(!rejected_overlap.ok());
    IOTOX_CHECK(rejected_overlap.status().code() ==
                iotox::ErrorCode::protocol_error);
    auto future_gap = receiver.offer(14U, future);
    IOTOX_CHECK(future_gap.ok());
    IOTOX_CHECK(future_gap.value().disposition ==
                InputDisposition::future_gap);
    IOTOX_CHECK(receiver.offer(13U, future).ok());
    IOTOX_CHECK(receiver.consume_staged(1U).value().acknowledgement == 14U);

    const std::vector<std::uint8_t> empty;
    const std::vector<std::uint8_t> oversized(5U, 0U);
    IOTOX_CHECK(!receiver.offer(14U, empty).ok());
    IOTOX_CHECK(!receiver.offer(14U, oversized).ok());
    IOTOX_CHECK(!receiver.consume_staged(1U).ok());
    IOTOX_CHECK(!receiver.fail_staged().ok());
}

IOTOX_TEST("interactive input receiver covers every v1 frame and sink boundary") {
    using namespace iotox::interactive;
    constexpr std::size_t maximum = 1076U;
    for (std::size_t size = 1U; size <= maximum; ++size) {
        InputReceiver receiver({maximum, 1U});
        const std::vector<std::uint8_t> payload(size, 0xA5U);
        IOTOX_CHECK(receiver.offer(1U, payload).ok());
        auto committed = receiver.consume_staged(size);
        IOTOX_CHECK(committed.ok());
        IOTOX_CHECK(committed.value().committed);
        IOTOX_CHECK(committed.value().acknowledgement == size + 1U);
    }

    const std::vector<std::uint8_t> maximum_payload(maximum, 0x5AU);
    for (std::size_t first_write = 0U;
         first_write <= maximum; ++first_write) {
        InputReceiver receiver({maximum, 1U});
        IOTOX_CHECK(receiver.offer(1U, maximum_payload).ok());
        if (first_write != 0U) {
            auto first = receiver.consume_staged(first_write);
            IOTOX_CHECK(first.ok());
            IOTOX_CHECK(first.value().committed ==
                        (first_write == maximum));
        }
        if (first_write < maximum) {
            auto second = receiver.consume_staged(maximum - first_write);
            IOTOX_CHECK(second.ok());
            IOTOX_CHECK(second.value().committed);
        }
        IOTOX_CHECK(receiver.snapshot().next_expected_sequence ==
                    maximum + 1U);
    }
}

IOTOX_TEST("interactive input sink failure permanently closes its incarnation") {
    using namespace iotox::interactive;
    const std::vector<std::uint8_t> payload(32U, 0xCCU);
    for (std::size_t consumed = 0U; consumed < payload.size(); ++consumed) {
        InputReceiver receiver({payload.size(), 9U});
        IOTOX_CHECK(receiver.offer(9U, payload).ok());
        if (consumed != 0U) {
            auto partial = receiver.consume_staged(consumed);
            IOTOX_CHECK(partial.ok());
            IOTOX_CHECK(!partial.value().committed);
        }
        IOTOX_CHECK(receiver.fail_staged().ok());
        const auto snapshot = receiver.snapshot();
        IOTOX_CHECK(snapshot.terminal_failure);
        IOTOX_CHECK(snapshot.next_expected_sequence == 9U);
        IOTOX_CHECK(snapshot.staged_bytes == 0U);
        IOTOX_CHECK(!receiver.offer(9U, payload).ok());
        IOTOX_CHECK(!receiver.pending_bytes().ok());
        IOTOX_CHECK(!receiver.consume_staged(1U).ok());
        IOTOX_CHECK(!receiver.fail_staged().ok());
    }

    InputReceiver invalid({0U, 0U});
    IOTOX_CHECK(!invalid.offer(1U, payload).ok());
}

IOTOX_TEST("interactive output history returns exact suffixes and explicit gaps") {
    using namespace iotox::interactive;
    OutputHistory history({6U, 10U});
    const std::vector<std::uint8_t> first{'a', 'b', 'c'};
    const std::vector<std::uint8_t> second{'d', 'e', 'f', 'g'};
    IOTOX_CHECK(history.append(first).value() == 10U);
    auto prefix = history.read_from(10U, 2U);
    IOTOX_CHECK(prefix.ok());
    IOTOX_CHECK(prefix.value().kind == OutputReadKind::data);
    IOTOX_CHECK(prefix.value().bytes ==
                std::vector<std::uint8_t>({'a', 'b'}));
    IOTOX_CHECK(!prefix.value().complete);
    IOTOX_CHECK(prefix.value().next_sequence == 12U);

    IOTOX_CHECK(history.append(second).value() == 13U);
    auto snapshot = history.snapshot();
    IOTOX_CHECK(snapshot.base_sequence == 11U);
    IOTOX_CHECK(snapshot.next_sequence == 17U);
    IOTOX_CHECK(snapshot.retained_bytes == 6U);
    auto gap = history.read_from(10U, 6U);
    IOTOX_CHECK(gap.ok());
    IOTOX_CHECK(gap.value().kind == OutputReadKind::gap);
    IOTOX_CHECK(gap.value().first_sequence == 11U);
    IOTOX_CHECK(gap.value().produced_next_sequence == 17U);
    IOTOX_CHECK(gap.value().bytes.empty());

    auto retained = history.read_from(11U, 6U);
    IOTOX_CHECK(retained.ok());
    IOTOX_CHECK(retained.value().bytes ==
                std::vector<std::uint8_t>({'b', 'c', 'd', 'e', 'f', 'g'}));
    IOTOX_CHECK(retained.value().complete);
    IOTOX_CHECK(history.acknowledge(14U).ok());
    IOTOX_CHECK(history.acknowledge(12U).ok());
    IOTOX_CHECK(history.snapshot().base_sequence == 14U);

    const std::vector<std::uint8_t> large{
        'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p'};
    IOTOX_CHECK(history.append(large).value() == 17U);
    snapshot = history.snapshot();
    IOTOX_CHECK(snapshot.base_sequence == 20U);
    IOTOX_CHECK(snapshot.next_sequence == 26U);
    auto tail = history.read_from(20U, 6U);
    IOTOX_CHECK(tail.ok());
    IOTOX_CHECK(tail.value().bytes ==
                std::vector<std::uint8_t>({'k', 'l', 'm', 'n', 'o', 'p'}));
    IOTOX_CHECK(tail.value().complete);
    auto at_end = history.read_from(26U, 1U);
    IOTOX_CHECK(at_end.ok());
    IOTOX_CHECK(at_end.value().bytes.empty());
    IOTOX_CHECK(at_end.value().complete);

    IOTOX_CHECK(!history.acknowledge(27U).ok());
    IOTOX_CHECK(!history.read_from(27U, 1U).ok());
    IOTOX_CHECK(!history.read_from(20U, 0U).ok());
    const std::vector<std::uint8_t> empty;
    IOTOX_CHECK(!history.append(empty).ok());

    OutputHistory exhausted({6U,
        std::numeric_limits<std::uint64_t>::max() - 2U});
    const std::vector<std::uint8_t> three{'x', 'y', 'z'};
    IOTOX_CHECK(!exhausted.append(three).ok());
    IOTOX_CHECK(exhausted.snapshot().retained_bytes == 0U);
    OutputHistory invalid({0U, 0U});
    IOTOX_CHECK(!invalid.append(first).ok());
}

IOTOX_TEST("interactive RTT estimator is monotonic-clock bounded") {
    using namespace std::chrono_literals;
    iotox::interactive::RttEstimator estimator;
    IOTOX_CHECK(estimator.observe(100ms).ok());
    auto first = estimator.snapshot();
    IOTOX_CHECK(first.sample_count == 1U);
    IOTOX_CHECK(first.smoothed_us == 100000U);
    IOTOX_CHECK(first.variation_us == 50000U);
    IOTOX_CHECK(first.retransmission_timeout_us == 300000U);

    IOTOX_CHECK(estimator.observe(60ms).ok());
    auto second = estimator.snapshot();
    IOTOX_CHECK(second.sample_count == 2U);
    IOTOX_CHECK(second.minimum_us == 60000U);
    IOTOX_CHECK(second.smoothed_us == 95000U);
    IOTOX_CHECK(second.variation_us == 47500U);
    IOTOX_CHECK(second.retransmission_timeout_us == 285000U);
    IOTOX_CHECK(estimator.observe(
        std::chrono::microseconds::max()).ok());
    const auto extreme = estimator.snapshot();
    IOTOX_CHECK(extreme.sample_count == 3U);
    IOTOX_CHECK(extreme.smoothed_us >= second.smoothed_us);
    IOTOX_CHECK(extreme.retransmission_timeout_us == 5000000U);
    IOTOX_CHECK(!estimator.observe(0us).ok());
}

IOTOX_TEST("Ratox v1 input frame freezes its complete attachment envelope") {
    using namespace iotox::protocol::ratox;
    IOTOX_CHECK(kTerminalAuthorityCapabilityBit == (1ULL << 7U));
    Frame frame = attached_ratox_frame(FrameType::input);
    frame.sequence = 42U;
    frame.acknowledgement = 77U;
    frame.payload = {'a', 'b', 'c'};
    auto encoded = encode(frame);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() == kHeaderBytes + 3U);
    IOTOX_CHECK(encoded.value()[0U] == kPacketId);
    IOTOX_CHECK(encoded.value()[1U] == kMajor);
    IOTOX_CHECK(encoded.value()[2U] == kMinor);
    IOTOX_CHECK(encoded.value()[3U] == 6U);
    IOTOX_CHECK(encoded.value()[4U] == 0U);
    IOTOX_CHECK(encoded.value()[5U] == kHeaderBytes);
    IOTOX_CHECK(encoded.value()[6U] == 0U);
    IOTOX_CHECK(encoded.value()[7U] == 3U);
    IOTOX_CHECK(encoded.value()[24U] == 0x11U);
    IOTOX_CHECK(encoded.value()[40U] == 0x22U);
    IOTOX_CHECK(encoded.value()[72U] == 0x33U);
    IOTOX_CHECK(encoded.value()[111U] == 42U);
    IOTOX_CHECK(encoded.value()[119U] == 77U);
    auto decoded = decode(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == frame);
}

IOTOX_TEST("Ratox v1 encode_into is exact bounded and nonmutating on refusal") {
    using namespace iotox::protocol::ratox;
    Frame frame = attached_ratox_frame(FrameType::output);
    frame.sequence = 0x1122334455667788ULL;
    frame.acknowledgement = 0x0102030405060708ULL;
    frame.payload = {0x00U, 0x7FU, 0x80U, 0xFFU};

    auto allocated = encode(frame);
    IOTOX_CHECK_MSG(allocated.ok(), allocated.status().message());

    std::array<std::uint8_t, kMaximumPacketBytes> storage{};
    storage.fill(0xA5U);
    auto fixed = encode_into(frame, storage);
    IOTOX_CHECK_MSG(fixed.ok(), fixed.status().message());
    IOTOX_CHECK(fixed.value() == allocated.value().size());
    IOTOX_CHECK(std::equal(
        allocated.value().begin(), allocated.value().end(), storage.begin()));
    IOTOX_CHECK(storage[fixed.value()] == 0xA5U);

    std::vector<std::uint8_t> undersized(
        allocated.value().size() - 1U, 0xC3U);
    const auto before = undersized;
    auto refused = encode_into(frame, undersized);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() ==
                iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(undersized == before);
}

IOTOX_TEST("Ratox v1 frame decoder rejects structural ambiguity") {
    using namespace iotox::protocol::ratox;
    Frame frame = attached_ratox_frame(FrameType::resize);
    frame.payload = {0U, 80U, 0U, 24U};
    auto encoded = encode(frame);
    IOTOX_CHECK(encoded.ok());

    for (const std::size_t offset : {0U, 1U, 2U, 4U, 5U, 120U}) {
        auto malformed = encoded.value();
        malformed[offset] ^= 1U;
        IOTOX_CHECK(!decode(malformed).ok());
    }
    auto unknown_type = encoded.value();
    unknown_type[3U] = 18U;
    IOTOX_CHECK(!decode(unknown_type).ok());
    auto wrong_length = encoded.value();
    wrong_length[7U] = 3U;
    IOTOX_CHECK(!decode(wrong_length).ok());
    auto trailing = encoded.value();
    trailing.push_back(0U);
    IOTOX_CHECK(!decode(trailing).ok());
}

IOTOX_TEST("Ratox v1 types enforce attachment sequence and payload roles") {
    using namespace iotox::protocol::ratox;
    Frame open = attached_ratox_frame(FrameType::open);
    open.incarnation = 0U;
    open.generation = 0U;
    open.payload.resize(12U);
    open.payload[0U] = 1U;
    open.payload[3U] = 80U;
    open.payload[5U] = 24U;
    IOTOX_CHECK(encode(open).ok());
    open.generation = 1U;
    IOTOX_CHECK(!encode(open).ok());

    Frame ack = attached_ratox_frame(FrameType::input_ack);
    ack.acknowledgement = 100U;
    IOTOX_CHECK(encode(ack).ok());
    ack.payload.push_back(0U);
    IOTOX_CHECK(!encode(ack).ok());

    Frame result = attached_ratox_frame(FrameType::resume_result);
    result.correlation_id = 88U;
    result.payload.resize(28U);
    result.payload[1U] = 1U;
    IOTOX_CHECK(encode(result).ok());
    result.correlation_id = 0U;
    IOTOX_CHECK(!encode(result).ok());

    Frame gap = attached_ratox_frame(FrameType::output_gap);
    gap.sequence = 500U;
    gap.acknowledgement = 700U;
    IOTOX_CHECK(encode(gap).ok());
    gap.sequence = 701U;
    IOTOX_CHECK(!encode(gap).ok());

    Frame maximum = attached_ratox_frame(FrameType::output);
    maximum.sequence = 1U;
    maximum.payload.resize(kMaximumPayloadBytes, 0xA5U);
    auto maximum_encoded = encode(maximum);
    IOTOX_CHECK(maximum_encoded.ok());
    IOTOX_CHECK(maximum_encoded.value().size() == kMaximumPacketBytes);
    maximum.payload.push_back(0U);
    IOTOX_CHECK(!encode(maximum).ok());
}

IOTOX_TEST("Ratox admission pacer coalesces and never loses a rejected offer") {
    using namespace std::chrono_literals;
    using iotox::protocol::ratox::AdmissionPacer;
    AdmissionPacer pacer({5ms, 40ms, 4U, 8U, 2U});
    const auto start = AdmissionPacer::Clock::time_point{};
    const std::vector<std::uint8_t> first{'a', 'b'};
    IOTOX_CHECK(pacer.enqueue(first, start).ok());
    IOTOX_CHECK(!pacer.ready(start + 4ms).ok());
    auto offered = pacer.ready(start + 5ms);
    IOTOX_CHECK(offered.ok());
    IOTOX_CHECK(offered.value() == first);
    IOTOX_CHECK(pacer.rejected(start + 5ms).ok());
    IOTOX_CHECK(pacer.snapshot().buffered_bytes == 2U);
    IOTOX_CHECK(pacer.snapshot().interval_us == 10000U);
    IOTOX_CHECK(!pacer.ready(start + 14ms).ok());
    auto retry = pacer.ready(start + 15ms);
    IOTOX_CHECK(retry.ok());
    IOTOX_CHECK(retry.value() == first);
    IOTOX_CHECK(pacer.accepted(2U, start + 15ms).ok());
    IOTOX_CHECK(pacer.snapshot().buffered_bytes == 0U);
    IOTOX_CHECK(pacer.snapshot().interval_us == 5000U);

    const std::vector<std::uint8_t> full{'c', 'd', 'e', 'f'};
    IOTOX_CHECK(pacer.enqueue(full, start + 20ms).ok());
    IOTOX_CHECK(!pacer.ready(start + 24ms).ok());
    auto coalesced = pacer.ready(start + 25ms);
    IOTOX_CHECK(coalesced.ok());
    IOTOX_CHECK(coalesced.value() == full);
    IOTOX_CHECK(!pacer.accepted(3U, start + 25ms).ok());
    IOTOX_CHECK(pacer.snapshot().buffered_bytes == 4U);
    IOTOX_CHECK(pacer.accepted(4U, start + 25ms).ok());
    const std::vector<std::uint8_t> overflow(9U, 0U);
    IOTOX_CHECK(!pacer.enqueue(overflow, start).ok());
}

IOTOX_TEST("interactive message replay cache is exact bounded and fail closed") {
    using namespace iotox::interactive;
    MessageReplayCache cache({2U, 16U, 8U});
    const std::vector<std::uint8_t> request_one{1U, 2U, 3U};
    const std::vector<std::uint8_t> result_one{4U, 5U};
    auto first = cache.reserve(11U, request_one, result_one.size());
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(first.value().kind == MessageReplayAdmissionKind::execute);
    IOTOX_CHECK(cache.commit(first.value().reservation, result_one).ok());
    IOTOX_CHECK(cache.lookup(11U, request_one).value() == result_one);

    const std::vector<std::uint8_t> conflict{1U, 2U, 4U};
    auto conflicting = cache.lookup(11U, conflict);
    IOTOX_CHECK(!conflicting.ok());
    IOTOX_CHECK(conflicting.status().code() == iotox::ErrorCode::protocol_error);

    const std::vector<std::uint8_t> request_two{6U, 7U, 8U, 9U};
    const std::vector<std::uint8_t> result_two{10U, 11U, 12U};
    auto second = cache.reserve(12U, request_two, result_two.size());
    IOTOX_CHECK(second.ok());
    IOTOX_CHECK(cache.commit(second.value().reservation, result_two).ok());
    const std::vector<std::uint8_t> request_three{13U};
    auto full = cache.reserve(13U, request_three, result_one.size());
    IOTOX_CHECK(!full.ok());
    IOTOX_CHECK(full.status().code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(cache.lookup(11U, request_one).value() == result_one);

    const auto snapshot = cache.snapshot();
    IOTOX_CHECK(snapshot.entries == 2U);
    IOTOX_CHECK(snapshot.pending_entries == 0U);
    IOTOX_CHECK(snapshot.retained_bytes == 12U);
    IOTOX_CHECK(snapshot.reserved_bytes == 0U);
    IOTOX_CHECK(snapshot.entry_bound_respected);
    IOTOX_CHECK(snapshot.byte_bound_respected);
}

IOTOX_TEST("interactive replay reservations close the cache-full after-side-effect window") {
    using namespace iotox::interactive;
    MessageReplayCache cache({2U, 12U, 6U});
    const std::vector<std::uint8_t> request{1U, 2U};
    auto first = cache.reserve(21U, request, 4U);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(first.value().kind == MessageReplayAdmissionKind::execute);
    IOTOX_CHECK(cache.snapshot().pending_entries == 1U);
    IOTOX_CHECK(cache.snapshot().reserved_bytes == 6U);

    auto in_progress = cache.reserve(21U, request, 4U);
    IOTOX_CHECK(!in_progress.ok());
    IOTOX_CHECK(in_progress.status().code() == iotox::ErrorCode::unavailable);
    const std::vector<std::uint8_t> changed{1U, 3U};
    auto conflict = cache.reserve(21U, changed, 4U);
    IOTOX_CHECK(!conflict.ok());
    IOTOX_CHECK(conflict.status().code() == iotox::ErrorCode::protocol_error);

    const std::vector<std::uint8_t> oversized(5U, 0xA0U);
    auto oversized_commit =
        cache.commit(first.value().reservation, oversized);
    IOTOX_CHECK(!oversized_commit.ok());
    IOTOX_CHECK(oversized_commit.code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(cache.snapshot().pending_entries == 1U);

    const std::vector<std::uint8_t> result{9U, 8U, 7U, 6U};
    IOTOX_CHECK(cache.commit(first.value().reservation, result).ok());
    auto replay = cache.reserve(21U, request, 4U);
    IOTOX_CHECK(replay.ok());
    IOTOX_CHECK(replay.value().kind == MessageReplayAdmissionKind::replay);
    IOTOX_CHECK(replay.value().result == result);
    auto replay_with_irrelevant_capacity = cache.reserve(21U, request, 999U);
    IOTOX_CHECK(replay_with_irrelevant_capacity.ok());
    IOTOX_CHECK(replay_with_irrelevant_capacity.value().kind ==
                MessageReplayAdmissionKind::replay);
    IOTOX_CHECK(replay_with_irrelevant_capacity.value().result == result);

    const std::vector<std::uint8_t> second_request{3U, 4U};
    auto second = cache.reserve(22U, second_request, 4U);
    IOTOX_CHECK(second.ok());
    auto byte_full = cache.reserve(23U, std::span<const std::uint8_t>{}, 1U);
    IOTOX_CHECK(!byte_full.ok());
    IOTOX_CHECK(byte_full.status().code() == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(cache.cancel(second.value().reservation).ok());
    IOTOX_CHECK(cache.snapshot().pending_entries == 0U);
    IOTOX_CHECK(cache.snapshot().reserved_bytes == 0U);

    MessageReplayCache releases_unused_capacity({2U, 10U, 6U});
    auto reserved = releases_unused_capacity.reserve(31U, request, 6U);
    IOTOX_CHECK(reserved.ok());
    const std::vector<std::uint8_t> short_result{0xA1U};
    IOTOX_CHECK(releases_unused_capacity.commit(
        reserved.value().reservation, short_result).ok());
    IOTOX_CHECK(releases_unused_capacity.snapshot().retained_bytes == 3U);
    auto reclaimed = releases_unused_capacity.reserve(
        32U, second_request, 5U);
    IOTOX_CHECK(reclaimed.ok());
    IOTOX_CHECK(releases_unused_capacity.snapshot().reserved_bytes == 7U);
}

IOTOX_TEST("interactive session attaches resumes and atomically applies output position") {
    using namespace iotox::interactive;
    InteractiveSession::Config config;
    config.input = {8U, 1U};
    config.output = {6U, 1U};
    config.maximum_attachment_nonces = 8U;
    config.maximum_events = 32U;
    InteractiveSession session(
        test_session_id(1U), test_principal_id(2U), 1U, config);

    const std::vector<std::uint8_t> output{'a', 'b', 'c', 'd', 'e', 'f', 'g'};
    IOTOX_CHECK(session.append_output(output).ok());
    IOTOX_CHECK(session.snapshot().output.base_sequence == 2U);
    IOTOX_CHECK(session.snapshot().output.next_sequence == 8U);

    auto attached = session.attach(
        test_principal_id(2U), test_attachment_nonce(3U), 1U, 1U);
    IOTOX_CHECK(attached.ok());
    IOTOX_CHECK(attached.value().output_gap);
    IOTOX_CHECK(attached.value().token.generation == 1U);
    auto gap = session.read_output(attached.value().token, 1U, 8U);
    IOTOX_CHECK(gap.ok());
    IOTOX_CHECK(gap.value().kind == OutputReadKind::gap);

    const auto before_invalid = session.snapshot();
    auto invalid = session.resume(
        test_principal_id(2U), test_attachment_nonce(4U), 1U, 9U);
    IOTOX_CHECK(!invalid.ok());
    const auto after_invalid = session.snapshot();
    IOTOX_CHECK(after_invalid.generation == before_invalid.generation);
    IOTOX_CHECK(after_invalid.output.base_sequence ==
                before_invalid.output.base_sequence);
    IOTOX_CHECK(after_invalid.remembered_attachment_nonces ==
                before_invalid.remembered_attachment_nonces);
    IOTOX_CHECK(session.validate_attachment(attached.value().token).ok());
    IOTOX_CHECK(session.events().back().kind ==
                SessionEventKind::attachment_denied);
    IOTOX_CHECK(session.events().back().denial_reason ==
                SessionDenialReason::protocol_violation);

    auto resumed = session.resume(
        test_principal_id(2U), test_attachment_nonce(4U), 1U, 4U);
    IOTOX_CHECK(resumed.ok());
    IOTOX_CHECK(!resumed.value().output_gap);
    IOTOX_CHECK(resumed.value().token.generation == 2U);
    IOTOX_CHECK(resumed.value().output_base_sequence == 4U);
    IOTOX_CHECK(session.snapshot().output.base_sequence == 4U);
    IOTOX_CHECK(!session.validate_attachment(attached.value().token).ok());
    IOTOX_CHECK(session.validate_attachment(resumed.value().token).ok());
}

IOTOX_TEST("interactive session preserves staged input across fencing and fails uncertain incarnations") {
    using namespace iotox::interactive;
    InteractiveSession::Config config;
    config.input = {8U, 1U};
    config.output = {16U, 1U};
    config.maximum_attachment_nonces = 8U;
    config.maximum_events = 32U;
    InteractiveSession session(
        test_session_id(11U), test_principal_id(12U), 1U, config);

    auto first = session.attach(
        test_principal_id(12U), test_attachment_nonce(13U), 1U, 1U);
    IOTOX_CHECK(first.ok());
    const std::vector<std::uint8_t> bytes{'a', 'b', 'c'};
    IOTOX_CHECK(session.offer_input(first.value().token, 1U, bytes).ok());
    auto partial = session.consume_input(1U);
    IOTOX_CHECK(partial.ok());
    IOTOX_CHECK(!partial.value().committed);

    auto second = session.attach(
        test_principal_id(12U), test_attachment_nonce(14U), 1U, 1U);
    IOTOX_CHECK(second.ok());
    IOTOX_CHECK(!session.validate_attachment(first.value().token).ok());
    auto stale_offer = session.offer_input(first.value().token, 1U, bytes);
    IOTOX_CHECK(!stale_offer.ok());
    IOTOX_CHECK(session.events().back().kind == SessionEventKind::input_denied);
    IOTOX_CHECK(session.events().back().denial_reason ==
                SessionDenialReason::stale_attachment);
    IOTOX_CHECK(session.pending_input().value() ==
                std::vector<std::uint8_t>({'b', 'c'}));

    IOTOX_CHECK(session.fail_input().ok());
    IOTOX_CHECK(session.snapshot().lifecycle == SessionLifecycle::failed);
    IOTOX_CHECK(!session.validate_attachment(second.value().token).ok());
    IOTOX_CHECK(!session.pending_input().ok());

    IOTOX_CHECK(session.replace_incarnation().ok());
    const auto replaced = session.snapshot();
    IOTOX_CHECK(replaced.lifecycle == SessionLifecycle::active);
    IOTOX_CHECK(replaced.incarnation == 2U);
    IOTOX_CHECK(replaced.generation == 2U);
    IOTOX_CHECK(replaced.input.next_expected_sequence == 1U);
    IOTOX_CHECK(replaced.output.next_sequence == 1U);
    auto third = session.attach(
        test_principal_id(12U), test_attachment_nonce(15U), 1U, 1U);
    IOTOX_CHECK(third.ok());
    IOTOX_CHECK(third.value().token.incarnation == 2U);
    IOTOX_CHECK(third.value().token.generation == 3U);
}

IOTOX_TEST("interactive close retains final audit positions then wipes stream content") {
    using namespace iotox::interactive;
    InteractiveSession session(
        test_session_id(21U), test_principal_id(22U), 1U);
    auto attached = session.attach(
        test_principal_id(22U), test_attachment_nonce(23U), 1U, 1U);
    IOTOX_CHECK(attached.ok());
    const std::vector<std::uint8_t> input{'i', 'n', 'p', 't'};
    IOTOX_CHECK(session.offer_input(
        attached.value().token, 1U, input).ok());
    IOTOX_CHECK(session.consume_input(input.size()).value().committed);
    const std::vector<std::uint8_t> output{'o', 'u', 't'};
    IOTOX_CHECK(session.append_output(output).ok());

    auto internal_reason = session.close(
        attached.value().token, SessionCloseReason::process_failure);
    IOTOX_CHECK(!internal_reason.ok());
    IOTOX_CHECK(internal_reason.code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(session.snapshot().lifecycle == SessionLifecycle::active);

    IOTOX_CHECK(session.close(
        attached.value().token,
        SessionCloseReason::controller_request).ok());
    const auto snapshot = session.snapshot();
    IOTOX_CHECK(snapshot.lifecycle == SessionLifecycle::closed);
    IOTOX_CHECK(!snapshot.current_attachment.has_value());
    IOTOX_CHECK(snapshot.input.next_expected_sequence == 1U);
    IOTOX_CHECK(snapshot.input.staged_bytes == 0U);
    IOTOX_CHECK(snapshot.output.next_sequence == 1U);
    IOTOX_CHECK(snapshot.output.retained_bytes == 0U);

    bool found_close = false;
    for (const SessionEvent &event : session.events()) {
        if (event.kind == SessionEventKind::closed) {
            found_close = true;
            IOTOX_CHECK(event.has_close_reason);
            IOTOX_CHECK(event.close_reason ==
                        SessionCloseReason::controller_request);
            IOTOX_CHECK(event.next_input_sequence == 5U);
            IOTOX_CHECK(event.output_next_sequence == 4U);
        }
    }
    IOTOX_CHECK(found_close);
}

IOTOX_TEST("interactive session refuses generation incarnation and nonce exhaustion without mutation") {
    using namespace iotox::interactive;
    const SessionId session_id = test_session_id(31U);
    const PrincipalId principal = test_principal_id(32U);

    AttachmentFence generation_exhausted(
        session_id, 1U, std::numeric_limits<std::uint64_t>::max());
    auto generation_failure = generation_exhausted.attach(
        principal, test_attachment_nonce(33U));
    IOTOX_CHECK(!generation_failure.ok());
    IOTOX_CHECK(generation_failure.status().code() ==
                iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(!generation_exhausted.attached());
    IOTOX_CHECK(generation_exhausted.generation() ==
                std::numeric_limits<std::uint64_t>::max());

    AttachmentFence incarnation_exhausted(
        session_id, std::numeric_limits<std::uint64_t>::max(), 7U);
    auto current = incarnation_exhausted.attach(
        principal, test_attachment_nonce(34U));
    IOTOX_CHECK(current.ok());
    auto replace_failure = incarnation_exhausted.replace_incarnation();
    IOTOX_CHECK(!replace_failure.ok());
    IOTOX_CHECK(incarnation_exhausted.incarnation() ==
                std::numeric_limits<std::uint64_t>::max());
    IOTOX_CHECK(incarnation_exhausted.validate(current.value()).ok());

    InteractiveSession::Config nonce_config;
    nonce_config.maximum_attachment_nonces = 1U;
    nonce_config.maximum_events = 16U;
    InteractiveSession nonce_limited(
        test_session_id(35U), principal, 1U, nonce_config);
    auto first = nonce_limited.attach(
        principal, test_attachment_nonce(36U), 1U, 1U);
    IOTOX_CHECK(first.ok());
    const auto before = nonce_limited.snapshot();
    auto second = nonce_limited.attach(
        principal, test_attachment_nonce(37U), 1U, 1U);
    IOTOX_CHECK(!second.ok());
    IOTOX_CHECK(second.status().code() == iotox::ErrorCode::resource_exhausted);
    const auto after = nonce_limited.snapshot();
    IOTOX_CHECK(after.generation == before.generation);
    IOTOX_CHECK(after.remembered_attachment_nonces ==
                before.remembered_attachment_nonces);
    IOTOX_CHECK(nonce_limited.validate_attachment(first.value().token).ok());

    InteractiveSession max_incarnation(
        test_session_id(38U), principal,
        std::numeric_limits<std::uint64_t>::max());
    auto attached = max_incarnation.attach(
        principal, test_attachment_nonce(39U), 1U, 1U);
    IOTOX_CHECK(attached.ok());
    IOTOX_CHECK(!max_incarnation.replace_incarnation().ok());
    IOTOX_CHECK(max_incarnation.validate_attachment(
        attached.value().token).ok());
}

IOTOX_TEST("interactive directory enforces atomic principal and device quotas") {
    using namespace iotox::interactive;
    SessionDirectory::Config config;
    config.maximum_sessions_per_principal = 1U;
    config.maximum_sessions_per_device = 2U;
    config.session.input.initial_sequence = 9U;
    config.session.output.initial_sequence = 17U;
    config.session.maximum_events = 16U;
    SessionDirectory directory(config);

    auto first = directory.open(
        test_session_id(41U), test_principal_id(51U),
        test_attachment_nonce(61U));
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(first.value().attachment.next_input_sequence == 9U);
    IOTOX_CHECK(first.value().attachment.output_base_sequence == 17U);
    IOTOX_CHECK(first.value().attachment.output_next_sequence == 17U);
    IOTOX_CHECK(!first.value().attachment.output_gap);
    auto principal_full = directory.open(
        test_session_id(42U), test_principal_id(51U),
        test_attachment_nonce(62U));
    IOTOX_CHECK(!principal_full.ok());
    IOTOX_CHECK(principal_full.status().code() ==
                iotox::ErrorCode::resource_exhausted);

    auto second = directory.open(
        test_session_id(42U), test_principal_id(52U),
        test_attachment_nonce(63U));
    IOTOX_CHECK(second.ok());
    auto device_full = directory.open(
        test_session_id(43U), test_principal_id(53U),
        test_attachment_nonce(64U));
    IOTOX_CHECK(!device_full.ok());
    IOTOX_CHECK(device_full.status().code() ==
                iotox::ErrorCode::resource_exhausted);
    auto duplicate = directory.open(
        test_session_id(41U), test_principal_id(53U),
        test_attachment_nonce(65U));
    IOTOX_CHECK(!duplicate.ok());
    IOTOX_CHECK(duplicate.status().code() == iotox::ErrorCode::protocol_error);

    SessionId invalid{};
    auto malformed = directory.open(
        invalid, test_principal_id(53U), test_attachment_nonce(66U));
    IOTOX_CHECK(!malformed.ok());
    IOTOX_CHECK(malformed.status().code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(directory.erase_closed(invalid).code() ==
                iotox::ErrorCode::invalid_argument);

    IOTOX_CHECK(first.value().session->close(
        first.value().attachment.token, SessionCloseReason::normal).ok());
    IOTOX_CHECK(directory.erase_closed(test_session_id(41U)).ok());
    auto replacement = directory.open(
        test_session_id(43U), test_principal_id(53U),
        test_attachment_nonce(67U));
    IOTOX_CHECK(replacement.ok());
    IOTOX_CHECK(directory.snapshot().sessions == 2U);
    IOTOX_CHECK(directory.snapshot().maximum_observed_sessions_per_principal ==
                1U);
    IOTOX_CHECK(directory.snapshot().principal_bound_respected);
    IOTOX_CHECK(directory.snapshot().device_bound_respected);
}

IOTOX_TEST("interactive control replay survives close for exact duplicate results") {
    using namespace iotox::interactive;
    InteractiveSession session(
        test_session_id(71U), test_principal_id(72U), 1U);
    auto attached = session.attach(
        test_principal_id(72U), test_attachment_nonce(73U), 1U, 1U);
    IOTOX_CHECK(attached.ok());
    const std::vector<std::uint8_t> request{0x0DU, 0x01U};
    const std::vector<std::uint8_t> result{0U, 0U};
    auto admission = session.begin_control(1001U, request, result.size());
    IOTOX_CHECK(admission.ok());
    IOTOX_CHECK(admission.value().kind == MessageReplayAdmissionKind::execute);

    IOTOX_CHECK(session.close(
        attached.value().token,
        SessionCloseReason::controller_request).ok());
    IOTOX_CHECK(session.complete_control(
        admission.value().reservation, result).ok());
    IOTOX_CHECK(session.snapshot().lifecycle == SessionLifecycle::closed);

    auto replay = session.begin_control(1001U, request, result.size());
    IOTOX_CHECK(replay.ok());
    IOTOX_CHECK(replay.value().kind == MessageReplayAdmissionKind::replay);
    IOTOX_CHECK(replay.value().result == result);
    const std::vector<std::uint8_t> conflict{0x0DU, 0x02U};
    auto conflicting = session.begin_control(1001U, conflict, result.size());
    IOTOX_CHECK(!conflicting.ok());
    IOTOX_CHECK(conflicting.status().code() ==
                iotox::ErrorCode::protocol_error);

    const MessageReplaySnapshot before_fresh =
        session.snapshot().control_replay;
    auto fresh = session.begin_control(1002U, request, result.size());
    IOTOX_CHECK(!fresh.ok());
    IOTOX_CHECK(fresh.status().code() == iotox::ErrorCode::unavailable);
    const MessageReplaySnapshot after_fresh =
        session.snapshot().control_replay;
    IOTOX_CHECK(after_fresh.entries == before_fresh.entries);
    IOTOX_CHECK(after_fresh.pending_entries == before_fresh.pending_entries);
    IOTOX_CHECK(after_fresh.retained_bytes == before_fresh.retained_bytes);
    IOTOX_CHECK(after_fresh.reserved_bytes == before_fresh.reserved_bytes);
    bool saw_closed_denial = false;
    for (const SessionEvent &event : session.events()) {
        if (event.kind == SessionEventKind::control_denied &&
            event.denial_reason == SessionDenialReason::closed) {
            saw_closed_denial = true;
        }
    }
    IOTOX_CHECK(saw_closed_denial);
}

IOTOX_TEST("interactive control reservations expose content-free denial facts") {
    using namespace iotox::interactive;
    InteractiveSession::Config config;
    config.control_replay = {1U, 6U, 4U};
    config.input = {2U, 1U};
    config.maximum_events = 16U;
    InteractiveSession session(
        test_session_id(81U), test_principal_id(82U), 1U, config);
    auto attached = session.attach(
        test_principal_id(82U), test_attachment_nonce(83U), 1U, 1U);
    IOTOX_CHECK(attached.ok());
    const std::vector<std::uint8_t> request{1U, 2U};
    auto first = session.begin_control(2001U, request, 4U);
    IOTOX_CHECK(first.ok());
    auto pending = session.begin_control(2001U, request, 4U);
    IOTOX_CHECK(!pending.ok());
    auto full = session.begin_control(2002U, request, 1U);
    IOTOX_CHECK(!full.ok());
    IOTOX_CHECK(session.cancel_control(first.value().reservation).ok());
    const std::vector<std::uint8_t> oversized_input{1U, 2U, 3U};
    auto denied_input = session.offer_input(
        attached.value().token, 1U, oversized_input);
    IOTOX_CHECK(!denied_input.ok());
    IOTOX_CHECK(denied_input.status().code() ==
                iotox::ErrorCode::resource_exhausted);

    bool saw_pending = false;
    bool saw_limit = false;
    bool saw_input_limit = false;
    std::uint64_t previous = 0U;
    for (const SessionEvent &event : session.events()) {
        IOTOX_CHECK(event.session_id == test_session_id(81U));
        IOTOX_CHECK(event.principal_id == test_principal_id(82U));
        IOTOX_CHECK(event.ordinal > previous);
        previous = event.ordinal;
        if (event.kind == SessionEventKind::control_denied &&
            event.denial_reason == SessionDenialReason::replay_in_progress) {
            saw_pending = true;
        }
        if (event.kind == SessionEventKind::control_denied &&
            event.denial_reason == SessionDenialReason::resource_limit) {
            saw_limit = true;
        }
        if (event.kind == SessionEventKind::input_denied &&
            event.denial_reason == SessionDenialReason::resource_limit) {
            saw_input_limit = true;
        }
    }
    IOTOX_CHECK(saw_pending);
    IOTOX_CHECK(saw_limit);
    IOTOX_CHECK(saw_input_limit);
    auto drained = session.drain_events();
    IOTOX_CHECK(!drained.empty());
    IOTOX_CHECK(session.events().empty());
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 1 through 135") {
    exercise_two_packet_split_range(1U, 135U);
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 136 through 270") {
    exercise_two_packet_split_range(136U, 270U);
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 271 through 405") {
    exercise_two_packet_split_range(271U, 405U);
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 406 through 540") {
    exercise_two_packet_split_range(406U, 540U);
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 541 through 675") {
    exercise_two_packet_split_range(541U, 675U);
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 676 through 810") {
    exercise_two_packet_split_range(676U, 810U);
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 811 through 945") {
    exercise_two_packet_split_range(811U, 945U);
}

IOTOX_TEST("interactive receiver exhaustively crosses two-packet v1 splits 946 through 1076") {
    exercise_two_packet_split_range(946U, 1076U);
}

IOTOX_TEST("interactive default byte windows cross exact Ratox resource limits") {
    using namespace iotox::interactive;
    ByteReplayWindow input;
    const std::vector<std::uint8_t> input_limit(64U * 1024U, 0x11U);
    IOTOX_CHECK(input.append(input_limit).ok());
    const std::vector<std::uint8_t> one{0x22U};
    auto input_full = input.append(one);
    IOTOX_CHECK(!input_full.ok());
    IOTOX_CHECK(input_full.status().code() ==
                iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(input.acknowledge(32769U).ok());
    const std::vector<std::uint8_t> refill(32U * 1024U, 0x33U);
    IOTOX_CHECK(input.append(refill).ok());
    IOTOX_CHECK(input.snapshot().pending_bytes == 64U * 1024U);

    OutputHistory output;
    const std::vector<std::uint8_t> output_limit(1024U * 1024U, 0x44U);
    IOTOX_CHECK(output.append(output_limit).ok());
    IOTOX_CHECK(output.snapshot().base_sequence == 1U);
    IOTOX_CHECK(output.snapshot().next_sequence == output_limit.size() + 1U);
    IOTOX_CHECK(output.append(one).ok());
    IOTOX_CHECK(output.snapshot().base_sequence == 2U);
    IOTOX_CHECK(output.snapshot().retained_bytes == 1024U * 1024U);
    auto gap = output.read_from(1U, 16U);
    IOTOX_CHECK(gap.ok());
    IOTOX_CHECK(gap.value().kind == OutputReadKind::gap);
    IOTOX_CHECK(output.acknowledge(1026U).ok());
    IOTOX_CHECK(output.snapshot().base_sequence == 1026U);
}
