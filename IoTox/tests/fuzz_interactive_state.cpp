#include "iotox/interactive.hpp"
#include "iotox/interactive_session.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <span>
#include <vector>

namespace {

std::uint64_t nearby_sequence(
    std::uint64_t base, std::uint8_t selector) {
    const std::int64_t delta = static_cast<std::int64_t>(selector % 9U) - 4;
    if (delta < 0) {
        const std::uint64_t magnitude = static_cast<std::uint64_t>(-delta);
        return base > magnitude ? base - magnitude : 1U;
    }
    const std::uint64_t magnitude = static_cast<std::uint64_t>(delta);
    return base <= std::numeric_limits<std::uint64_t>::max() - magnitude
        ? base + magnitude
        : std::numeric_limits<std::uint64_t>::max();
}

void check_input(const iotox::interactive::InputReceiverSnapshot &snapshot) {
    if (snapshot.next_expected_sequence == 0U ||
        snapshot.maximum_frame_bytes == 0U ||
        snapshot.staged_bytes > snapshot.maximum_frame_bytes ||
        snapshot.consumed_bytes > snapshot.staged_bytes) {
        __builtin_trap();
    }
    if (snapshot.terminal_failure &&
        (snapshot.staged_sequence != 0U || snapshot.staged_bytes != 0U ||
         snapshot.consumed_bytes != 0U)) {
        __builtin_trap();
    }
    if ((snapshot.staged_bytes == 0U) !=
        (snapshot.staged_sequence == 0U && snapshot.consumed_bytes == 0U)) {
        __builtin_trap();
    }
    if (snapshot.staged_bytes != 0U &&
        snapshot.staged_sequence != snapshot.next_expected_sequence) {
        __builtin_trap();
    }
}

void check_output(const iotox::interactive::OutputHistorySnapshot &snapshot) {
    if (snapshot.base_sequence == 0U ||
        snapshot.base_sequence > snapshot.next_sequence ||
        snapshot.maximum_bytes == 0U ||
        snapshot.retained_bytes > snapshot.maximum_bytes ||
        snapshot.next_sequence - snapshot.base_sequence !=
            snapshot.retained_bytes) {
        __builtin_trap();
    }
}

iotox::interactive::AttachmentNonce fuzz_nonce(
    std::uint8_t value, std::size_t cursor) {
    iotox::interactive::AttachmentNonce nonce{};
    nonce[0] = static_cast<std::uint8_t>(value | 1U);
    nonce[1] = static_cast<std::uint8_t>((cursor & 0xFFU) | 1U);
    nonce[2] = static_cast<std::uint8_t>(((cursor >> 8U) & 0xFFU) | 1U);
    return nonce;
}

iotox::interactive::SessionId fuzz_session_id(std::uint8_t value) {
    iotox::interactive::SessionId session_id{};
    session_id[0] = static_cast<std::uint8_t>(1U + value % 6U);
    session_id[1] = 0xD1U;
    return session_id;
}

iotox::interactive::PrincipalId fuzz_principal_id(std::uint8_t value) {
    iotox::interactive::PrincipalId principal_id{};
    principal_id[0] = static_cast<std::uint8_t>(1U + value % 3U);
    principal_id[1] = 0xD2U;
    return principal_id;
}

void check_directory(
    const iotox::interactive::SessionDirectory &directory) {
    const iotox::interactive::SessionDirectorySnapshot snapshot =
        directory.snapshot();
    if (snapshot.sessions > snapshot.maximum_sessions_per_device ||
        snapshot.maximum_observed_sessions_per_principal >
            snapshot.maximum_sessions_per_principal ||
        !snapshot.principal_bound_respected ||
        !snapshot.device_bound_respected) {
        __builtin_trap();
    }
}

void check_session(
    iotox::interactive::InteractiveSession &session,
    const iotox::interactive::SessionId &expected_session,
    const iotox::interactive::PrincipalId &expected_principal) {
    using namespace iotox::interactive;
    const InteractiveSessionSnapshot snapshot = session.snapshot();
    if (snapshot.session_id != expected_session ||
        snapshot.principal_id != expected_principal ||
        snapshot.incarnation == 0U ||
        snapshot.remembered_attachment_nonces >
            snapshot.maximum_attachment_nonces ||
        snapshot.retained_events > snapshot.maximum_events ||
        snapshot.control_replay.entries +
                snapshot.control_replay.pending_entries >
            snapshot.control_replay.maximum_entries ||
        snapshot.control_replay.retained_bytes +
                snapshot.control_replay.reserved_bytes >
            snapshot.control_replay.maximum_bytes ||
        !snapshot.control_replay.entry_bound_respected ||
        !snapshot.control_replay.byte_bound_respected) {
        __builtin_trap();
    }
    check_input(snapshot.input);
    check_output(snapshot.output);

    if (snapshot.lifecycle != SessionLifecycle::active &&
        snapshot.current_attachment.has_value()) {
        __builtin_trap();
    }
    if (snapshot.current_attachment) {
        const AttachmentToken &token = *snapshot.current_attachment;
        if (token.session_id != expected_session ||
            token.principal_id != expected_principal ||
            token.incarnation != snapshot.incarnation ||
            token.generation != snapshot.generation ||
            !session.validate_attachment(token).ok()) {
            __builtin_trap();
        }
    }

    std::uint64_t ordinal = 0U;
    for (const SessionEvent &event : session.events()) {
        if (event.ordinal <= ordinal || event.session_id != expected_session ||
            event.principal_id != expected_principal ||
            event.incarnation == 0U ||
            event.output_base_sequence == 0U ||
            event.output_base_sequence > event.output_next_sequence ||
            event.next_input_sequence == 0U) {
            __builtin_trap();
        }
        ordinal = event.ordinal;
    }
}

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(
    const std::uint8_t *data, std::size_t size) {
    if (size < 4U) return 0;
    using namespace iotox::interactive;

    const std::size_t input_limit = 1U + data[0U] % 64U;
    const std::size_t output_limit = 1U + data[1U] % 128U;
    InputReceiver input({input_limit, 1U});
    OutputHistory output({output_limit, 1U});

    SessionId session_id{};
    session_id.front() = 1U;
    PrincipalId principal{};
    principal.front() = 2U;
    InteractiveSession::Config config;
    config.input = {input_limit, 1U};
    config.output = {output_limit, 1U};
    config.control_replay = {8U, 256U, 32U};
    config.maximum_attachment_nonces = 8U;
    config.maximum_events = 24U;
    InteractiveSession session(session_id, principal, 1U, config);

    SessionDirectory::Config directory_config;
    directory_config.maximum_sessions_per_principal = 2U;
    directory_config.maximum_sessions_per_device = 4U;
    directory_config.session = config;
    directory_config.session.maximum_attachment_nonces = 4U;
    directory_config.session.maximum_events = 8U;
    SessionDirectory directory(directory_config);

    std::vector<AttachmentToken> stale_tokens;
    stale_tokens.reserve(16U);
    std::vector<MessageReplayReservation> reservations;
    reservations.reserve(8U);

    std::size_t cursor = 2U;
    while (cursor < size) {
        const std::uint8_t operation = data[cursor++];
        const InputReceiverSnapshot input_snapshot = input.snapshot();
        const OutputHistorySnapshot output_snapshot = output.snapshot();

        // Keep exercising the low-level receiver/history state independently.
        switch (operation % 7U) {
            case 0U:
            case 1U: {
                if (cursor >= size) break;
                const std::uint64_t sequence = nearby_sequence(
                    input_snapshot.next_expected_sequence, data[cursor++]);
                const std::size_t available = size - cursor;
                const std::size_t count = std::min(
                    available, 1U + static_cast<std::size_t>(operation) %
                        (input_limit + 1U));
                if (count != 0U) {
                    static_cast<void>(input.offer(
                        sequence,
                        std::span<const std::uint8_t>{data + cursor, count}));
                    cursor += count;
                }
                break;
            }
            case 2U: {
                if (input_snapshot.staged_bytes != 0U) {
                    const std::size_t remaining = input_snapshot.staged_bytes -
                        input_snapshot.consumed_bytes;
                    const std::size_t count = 1U + operation % remaining;
                    static_cast<void>(input.consume_staged(count));
                } else {
                    static_cast<void>(input.consume_staged(1U));
                }
                break;
            }
            case 3U:
                static_cast<void>(input.fail_staged());
                break;
            case 4U: {
                if (cursor >= size) break;
                const std::size_t available = size - cursor;
                const std::size_t count = std::min(
                    available, 1U + static_cast<std::size_t>(data[cursor]) %
                        (output_limit + 1U));
                if (count != 0U) {
                    static_cast<void>(output.append(
                        std::span<const std::uint8_t>{data + cursor, count}));
                    cursor += count;
                }
                break;
            }
            case 5U:
                if (cursor < size) {
                    static_cast<void>(output.acknowledge(nearby_sequence(
                        output_snapshot.base_sequence, data[cursor++])));
                }
                break;
            case 6U:
                if (cursor < size) {
                    const std::uint64_t requested = nearby_sequence(
                        output_snapshot.base_sequence, data[cursor++]);
                    auto read = output.read_from(
                        requested, 1U + operation % 64U);
                    if (read && read.value().produced_next_sequence !=
                                    output.snapshot().next_sequence) {
                        __builtin_trap();
                    }
                }
                break;
        }
        check_input(input.snapshot());
        check_output(output.snapshot());

        const InteractiveSessionSnapshot before = session.snapshot();
        const std::optional<AttachmentToken> current =
            before.current_attachment;
        switch (operation % 14U) {
            case 0U:
            case 1U: {
                if (cursor + 1U >= size) break;
                const std::uint64_t input_position = nearby_sequence(
                    before.input.next_expected_sequence, data[cursor++]);
                const std::uint64_t output_position = nearby_sequence(
                    before.output.base_sequence, data[cursor++]);
                const AttachmentNonce nonce =
                    fuzz_nonce(operation, cursor);
                auto attached = operation % 14U == 0U
                    ? session.attach(
                          principal, nonce, input_position, output_position)
                    : session.resume(
                          principal, nonce, input_position, output_position);
                if (attached) {
                    if (current && stale_tokens.size() < stale_tokens.capacity()) {
                        stale_tokens.push_back(*current);
                    }
                    if (!session.validate_attachment(
                            attached.value().token).ok()) {
                        __builtin_trap();
                    }
                }
                break;
            }
            case 2U: {
                if (!current || cursor >= size) break;
                const std::uint64_t sequence = nearby_sequence(
                    before.input.next_expected_sequence, data[cursor++]);
                const std::size_t count = std::min(
                    size - cursor,
                    1U + static_cast<std::size_t>(operation) % input_limit);
                if (count != 0U) {
                    static_cast<void>(session.offer_input(
                        *current, sequence,
                        std::span<const std::uint8_t>{data + cursor, count}));
                    cursor += count;
                }
                break;
            }
            case 3U:
                if (before.input.staged_bytes != 0U) {
                    const std::size_t remaining = before.input.staged_bytes -
                        before.input.consumed_bytes;
                    static_cast<void>(session.consume_input(
                        1U + operation % remaining));
                } else {
                    static_cast<void>(session.consume_input(1U));
                }
                break;
            case 4U:
                static_cast<void>(session.fail_input());
                break;
            case 5U: {
                const std::size_t count = std::min(
                    size - cursor,
                    1U + static_cast<std::size_t>(operation) % output_limit);
                if (count != 0U) {
                    static_cast<void>(session.append_output(
                        std::span<const std::uint8_t>{data + cursor, count}));
                    cursor += count;
                }
                break;
            }
            case 6U:
                if (current && cursor < size) {
                    static_cast<void>(session.acknowledge_output(
                        *current, nearby_sequence(
                            before.output.base_sequence, data[cursor++])));
                }
                break;
            case 7U:
                if (current && cursor < size) {
                    static_cast<void>(session.read_output(
                        *current,
                        nearby_sequence(
                            before.output.base_sequence, data[cursor++]),
                        1U + operation % 64U));
                }
                break;
            case 8U:
                if (current) static_cast<void>(session.detach(*current));
                break;
            case 9U:
                static_cast<void>(session.replace_incarnation());
                break;
            case 10U:
                if (current) {
                    static_cast<void>(session.close(
                        *current, static_cast<SessionCloseReason>(
                            operation % 9U)));
                }
                break;
            case 11U:
                static_cast<void>(session.terminate(
                    static_cast<SessionCloseReason>(operation % 9U)));
                break;
            case 12U: {
                if (cursor >= size) break;
                const std::uint64_t message_id =
                    1U + static_cast<std::uint64_t>(data[cursor++]);
                const std::size_t request_size =
                    std::min<std::size_t>(size - cursor, operation % 9U);
                const std::span<const std::uint8_t> request{
                    data + cursor, request_size};
                cursor += request_size;
                const std::size_t result_capacity = operation % 17U;
                auto admission = session.begin_control(
                    message_id, request, result_capacity);
                if (admission &&
                    admission.value().kind ==
                        MessageReplayAdmissionKind::execute &&
                    reservations.size() < reservations.capacity()) {
                    reservations.push_back(admission.value().reservation);
                }
                break;
            }
            case 13U:
                if (!reservations.empty()) {
                    const std::size_t index = operation % reservations.size();
                    const MessageReplayReservation reservation =
                        reservations[index];
                    if ((operation & 0x80U) != 0U) {
                        static_cast<void>(session.cancel_control(reservation));
                    } else {
                        const std::size_t result_size = std::min(
                            reservation.result_capacity, size - cursor);
                        static_cast<void>(session.complete_control(
                            reservation,
                            std::span<const std::uint8_t>{
                                data + cursor, result_size}));
                        cursor += result_size;
                    }
                    reservations.erase(
                        reservations.begin() +
                        static_cast<std::ptrdiff_t>(index));
                } else {
                    static_cast<void>(session.drain_events());
                }
                break;
        }

        for (const AttachmentToken &stale : stale_tokens) {
            if (session.snapshot().current_attachment &&
                stale != *session.snapshot().current_attachment &&
                session.validate_attachment(stale).ok()) {
                __builtin_trap();
            }
        }
        check_session(session, session_id, principal);

        const SessionId directory_session = fuzz_session_id(operation);
        const PrincipalId directory_principal =
            fuzz_principal_id(static_cast<std::uint8_t>(operation >> 2U));
        switch ((operation >> 6U) & 0x03U) {
            case 0U:
                static_cast<void>(directory.open(
                    directory_session, directory_principal,
                    fuzz_nonce(
                        static_cast<std::uint8_t>(operation ^ 0xA5U),
                        cursor),
                    1U + static_cast<std::uint64_t>(operation % 3U)));
                break;
            case 1U: {
                auto found = directory.find(directory_session);
                if (!found) break;
                InteractiveSession *directory_entry = found.value();
                const InteractiveSessionSnapshot entry_snapshot =
                    directory_entry->snapshot();
                if (entry_snapshot.lifecycle == SessionLifecycle::active) {
                    if (entry_snapshot.current_attachment) {
                        static_cast<void>(directory_entry->close(
                            *entry_snapshot.current_attachment,
                            SessionCloseReason::normal));
                    } else {
                        static_cast<void>(directory_entry->terminate(
                            SessionCloseReason::daemon_shutdown));
                    }
                } else if (
                    entry_snapshot.lifecycle == SessionLifecycle::failed) {
                    static_cast<void>(directory_entry->terminate(
                        SessionCloseReason::process_failure));
                }
                break;
            }
            case 2U:
                static_cast<void>(directory.erase_closed(directory_session));
                break;
            case 3U:
                static_cast<void>(directory.find(directory_session));
                break;
        }
        check_directory(directory);
    }
    return 0;
}
