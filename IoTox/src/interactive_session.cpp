#include "iotox/interactive_session.hpp"

#include <algorithm>
#include <limits>
#include <utility>

namespace iotox::interactive {
namespace {

void wipe_vector(std::vector<std::uint8_t> &bytes) noexcept {
    for (std::uint8_t &byte : bytes) {
        volatile std::uint8_t *slot = &byte;
        *slot = 0U;
    }
    bytes.clear();
}

template <std::size_t Size>
bool all_zero(const std::array<std::uint8_t, Size> &value) {
    return std::all_of(value.begin(), value.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

bool bytes_equal(
    std::span<const std::uint8_t> left,
    const std::vector<std::uint8_t> &right) {
    return left.size() == right.size() &&
        std::equal(left.begin(), left.end(), right.begin());
}

Result<std::size_t> checked_budget(
    std::size_t request_bytes, std::size_t result_bytes) {
    if (result_bytes >
        std::numeric_limits<std::size_t>::max() - request_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "message replay byte budget overflows size_t"};
    }
    return request_bytes + result_bytes;
}

SessionDenialReason reason_for_status(const Status &status) {
    switch (status.code()) {
        case ErrorCode::invalid_argument:
            return SessionDenialReason::invalid_request;
        case ErrorCode::protocol_error:
            return SessionDenialReason::protocol_violation;
        case ErrorCode::resource_exhausted:
            return SessionDenialReason::resource_limit;
        case ErrorCode::unavailable:
            return SessionDenialReason::unavailable;
        default:
            return SessionDenialReason::unavailable;
    }
}

SessionDenialReason reason_for_lifecycle(SessionLifecycle lifecycle) {
    switch (lifecycle) {
        case SessionLifecycle::active:
            return SessionDenialReason::none;
        case SessionLifecycle::failed:
            return SessionDenialReason::terminal_incarnation;
        case SessionLifecycle::closed:
            return SessionDenialReason::closed;
    }
    return SessionDenialReason::unavailable;
}

bool controller_close_reason(SessionCloseReason reason) {
    return static_cast<std::uint16_t>(reason) <=
        static_cast<std::uint16_t>(SessionCloseReason::resource_exhaustion);
}

bool internal_close_reason(SessionCloseReason reason) {
    return static_cast<std::uint16_t>(reason) <=
        static_cast<std::uint16_t>(SessionCloseReason::daemon_shutdown);
}

}  // namespace

MessageReplayCache::MessageReplayCache() : MessageReplayCache(Config{}) {}

MessageReplayCache::MessageReplayCache(Config config) : config_(config) {
    entries_.reserve(config_.maximum_entries);
}

MessageReplayCache::~MessageReplayCache() { wipe_entries(); }

MessageReplayCache::MessageReplayCache(MessageReplayCache &&other) noexcept
    : config_(other.config_),
      entries_(std::move(other.entries_)),
      retained_bytes_(other.retained_bytes_),
      reserved_bytes_(other.reserved_bytes_),
      next_reservation_id_(other.next_reservation_id_) {
    other.wipe_entries();
    other.retained_bytes_ = 0U;
    other.reserved_bytes_ = 0U;
    other.next_reservation_id_ = 1U;
}

MessageReplayCache &MessageReplayCache::operator=(
    MessageReplayCache &&other) noexcept {
    if (this == &other) return *this;
    wipe_entries();
    config_ = other.config_;
    entries_ = std::move(other.entries_);
    retained_bytes_ = other.retained_bytes_;
    reserved_bytes_ = other.reserved_bytes_;
    next_reservation_id_ = other.next_reservation_id_;
    other.wipe_entries();
    other.retained_bytes_ = 0U;
    other.reserved_bytes_ = 0U;
    other.next_reservation_id_ = 1U;
    return *this;
}

void MessageReplayCache::wipe_entries() noexcept {
    for (Entry &entry : entries_) {
        wipe_vector(entry.request);
        wipe_vector(entry.result);
        entry = Entry{};
    }
    entries_.clear();
}

Status MessageReplayCache::validate_config() const {
    if (config_.maximum_entries == 0U || config_.maximum_bytes == 0U ||
        config_.maximum_result_bytes == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "message replay cache requires nonzero bounds"};
    }
    return Status::success();
}

const MessageReplayCache::Entry *MessageReplayCache::find_message(
    std::uint64_t message_id) const {
    const auto found = std::find_if(
        entries_.begin(), entries_.end(),
        [message_id](const Entry &entry) {
            return entry.message_id == message_id;
        });
    return found == entries_.end() ? nullptr : &*found;
}

MessageReplayCache::Entry *MessageReplayCache::find_reservation(
    const MessageReplayReservation &reservation) {
    const auto found = std::find_if(
        entries_.begin(), entries_.end(),
        [&reservation](const Entry &entry) {
            return entry.pending &&
                entry.reservation_id == reservation.reservation_id &&
                entry.message_id == reservation.message_id &&
                entry.result_capacity == reservation.result_capacity;
        });
    return found == entries_.end() ? nullptr : &*found;
}

Result<MessageReplayAdmission> MessageReplayCache::reserve(
    std::uint64_t message_id, std::span<const std::uint8_t> request,
    std::size_t result_capacity) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "message replay ID zero is reserved"};
    }
    if (const Entry *existing = find_message(message_id); existing != nullptr) {
        if (!bytes_equal(request, existing->request)) {
            return Status{ErrorCode::protocol_error,
                          "message replay ID was reused with different request bytes"};
        }
        if (existing->pending) {
            return Status{ErrorCode::unavailable,
                          "message replay result is still in progress"};
        }
        MessageReplayAdmission replay;
        replay.kind = MessageReplayAdmissionKind::replay;
        replay.result = existing->result;
        return replay;
    }

    // A completed exact duplicate cannot execute again, so its newly supplied
    // capacity is irrelevant. Validate capacity only for a genuinely fresh
    // control that could acquire an execution reservation.
    if (result_capacity > config_.maximum_result_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "message replay result reservation exceeds its bound"};
    }

    if (entries_.size() >= config_.maximum_entries) {
        return Status{ErrorCode::resource_exhausted,
                      "message replay entry bound is exhausted"};
    }
    auto budget = checked_budget(request.size(), result_capacity);
    if (!budget.ok()) return budget.status();
    const std::size_t total_bytes = retained_bytes_ + reserved_bytes_;
    if (total_bytes > config_.maximum_bytes ||
        budget.value() > config_.maximum_bytes - total_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "message replay byte bound is exhausted"};
    }
    if (next_reservation_id_ == 0U ||
        next_reservation_id_ == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "message replay reservation IDs are exhausted"};
    }

    Entry candidate;
    candidate.message_id = message_id;
    candidate.reservation_id = next_reservation_id_;
    candidate.result_capacity = result_capacity;
    candidate.budget_bytes = budget.value();
    candidate.pending = true;
    candidate.request.assign(request.begin(), request.end());
    candidate.result.reserve(result_capacity);

    entries_.push_back(std::move(candidate));
    wipe_vector(candidate.request);
    wipe_vector(candidate.result);
    reserved_bytes_ += budget.value();
    const MessageReplayReservation reservation{
        next_reservation_id_, message_id, result_capacity};
    ++next_reservation_id_;

    MessageReplayAdmission admission;
    admission.kind = MessageReplayAdmissionKind::execute;
    admission.reservation = reservation;
    return admission;
}

Status MessageReplayCache::commit(
    const MessageReplayReservation &reservation,
    std::span<const std::uint8_t> result) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (reservation.reservation_id == 0U || reservation.message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "message replay reservation is invalid"};
    }
    Entry *entry = find_reservation(reservation);
    if (entry == nullptr) {
        return Status{ErrorCode::not_found,
                      "message replay reservation is absent or already completed"};
    }
    if (result.size() > entry->result_capacity) {
        return Status{ErrorCode::resource_exhausted,
                      "message replay result exceeds its pre-effect reservation"};
    }

    const std::size_t reserved_budget = entry->budget_bytes;
    const std::size_t retained_budget = entry->request.size() + result.size();
    entry->result.assign(result.begin(), result.end());
    entry->budget_bytes = retained_budget;
    entry->pending = false;
    reserved_bytes_ -= reserved_budget;
    retained_bytes_ += retained_budget;
    return Status::success();
}

Status MessageReplayCache::cancel(
    const MessageReplayReservation &reservation) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (reservation.reservation_id == 0U || reservation.message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "message replay reservation is invalid"};
    }
    const auto found = std::find_if(
        entries_.begin(), entries_.end(),
        [&reservation](const Entry &entry) {
            return entry.pending &&
                entry.reservation_id == reservation.reservation_id &&
                entry.message_id == reservation.message_id &&
                entry.result_capacity == reservation.result_capacity;
        });
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "message replay reservation is absent or already completed"};
    }
    reserved_bytes_ -= found->budget_bytes;
    wipe_vector(found->request);
    wipe_vector(found->result);
    entries_.erase(found);
    return Status::success();
}

Result<std::vector<std::uint8_t>> MessageReplayCache::lookup(
    std::uint64_t message_id,
    std::span<const std::uint8_t> request) const {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "message replay ID zero is reserved"};
    }
    const Entry *entry = find_message(message_id);
    if (entry == nullptr) {
        return Status{ErrorCode::not_found,
                      "message replay ID is not retained"};
    }
    if (!bytes_equal(request, entry->request)) {
        return Status{ErrorCode::protocol_error,
                      "message replay ID was reused with different request bytes"};
    }
    if (entry->pending) {
        return Status{ErrorCode::unavailable,
                      "message replay result is still in progress"};
    }
    return entry->result;
}

MessageReplaySnapshot MessageReplayCache::snapshot() const noexcept {
    std::size_t committed = 0U;
    std::size_t pending = 0U;
    for (const Entry &entry : entries_) {
        if (entry.pending) {
            ++pending;
        } else {
            ++committed;
        }
    }
    const std::size_t total_bytes = retained_bytes_ + reserved_bytes_;
    return MessageReplaySnapshot{
        committed,
        pending,
        retained_bytes_,
        reserved_bytes_,
        config_.maximum_entries,
        config_.maximum_bytes,
        config_.maximum_result_bytes,
        entries_.size() <= config_.maximum_entries,
        retained_bytes_ <= total_bytes && total_bytes <= config_.maximum_bytes};
}

InteractiveSession::InteractiveSession(
    SessionId session_id, PrincipalId principal_id,
    std::uint64_t incarnation)
    : InteractiveSession(
          session_id, principal_id, incarnation, Config{}) {}

InteractiveSession::InteractiveSession(
    SessionId session_id, PrincipalId principal_id,
    std::uint64_t incarnation, Config config)
    : config_(config),
      session_id_(session_id),
      principal_id_(principal_id),
      fence_(session_id, incarnation, config.initial_generation),
      input_(config.input),
      output_(config.output),
      control_replay_(config.control_replay) {
    seen_nonces_.reserve(config_.maximum_attachment_nonces);
    events_.reserve(config_.maximum_events);
    if (validate_config().ok()) {
        append_event(SessionEventKind::opened);
    }
}

Status InteractiveSession::validate_config() const {
    if (all_zero(session_id_) || all_zero(principal_id_) ||
        fence_.incarnation() == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "interactive session identity must be nonzero"};
    }
    if (config_.input.maximum_frame_bytes == 0U ||
        config_.input.initial_sequence == 0U ||
        config_.output.maximum_bytes == 0U ||
        config_.output.initial_sequence == 0U ||
        config_.maximum_attachment_nonces == 0U ||
        config_.maximum_events == 0U ||
        config_.control_replay.maximum_entries == 0U ||
        config_.control_replay.maximum_bytes == 0U ||
        config_.control_replay.maximum_result_bytes == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "interactive session requires nonzero resource bounds"};
    }
    return Status::success();
}

Status InteractiveSession::require_active() const {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (lifecycle_ == SessionLifecycle::closed) {
        return Status{ErrorCode::unavailable,
                      "interactive session is closed"};
    }
    if (lifecycle_ == SessionLifecycle::failed) {
        return Status{ErrorCode::unavailable,
                      "interactive session incarnation is terminal"};
    }
    return Status::success();
}

bool InteractiveSession::nonce_seen(const AttachmentNonce &nonce) const {
    return std::find(seen_nonces_.begin(), seen_nonces_.end(), nonce) !=
        seen_nonces_.end();
}

Result<SessionAttachmentResult> InteractiveSession::attach(
    PrincipalId principal_id, AttachmentNonce nonce,
    std::uint64_t controller_next_input,
    std::uint64_t controller_next_output) {
    return attach_impl(
        AttachKind::attach, principal_id, nonce,
        controller_next_input, controller_next_output);
}

Result<SessionAttachmentResult> InteractiveSession::resume(
    PrincipalId principal_id, AttachmentNonce nonce,
    std::uint64_t controller_next_input,
    std::uint64_t controller_next_output) {
    return attach_impl(
        AttachKind::resume, principal_id, nonce,
        controller_next_input, controller_next_output);
}

Result<SessionAttachmentResult> InteractiveSession::attach_impl(
    AttachKind kind, PrincipalId principal_id, AttachmentNonce nonce,
    std::uint64_t controller_next_input,
    std::uint64_t controller_next_output) {
    const Status active = require_active();
    if (!active.ok()) {
        if (validate_config().ok()) {
            append_event(
                SessionEventKind::attachment_denied,
                reason_for_lifecycle(lifecycle_));
        }
        return active;
    }
    if (principal_id != principal_id_ || all_zero(principal_id) ||
        all_zero(nonce)) {
        append_event(
            SessionEventKind::attachment_denied,
            SessionDenialReason::invalid_identity);
        return Status{
            ErrorCode::invalid_argument,
            "attachment identity does not match the session"};
    }
    if (controller_next_input == 0U || controller_next_output == 0U) {
        append_event(
            SessionEventKind::attachment_denied,
            SessionDenialReason::invalid_request);
        return Status{
            ErrorCode::invalid_argument,
            "attachment byte positions must be nonzero"};
    }
    if (nonce_seen(nonce)) {
        append_event(
            SessionEventKind::attachment_denied,
            SessionDenialReason::protocol_violation);
        return Status{
            ErrorCode::protocol_error,
            "attachment nonce was already used in this session"};
    }
    if (seen_nonces_.size() >= config_.maximum_attachment_nonces) {
        append_event(
            SessionEventKind::attachment_denied,
            SessionDenialReason::resource_limit);
        return Status{
            ErrorCode::resource_exhausted,
            "attachment nonce retention is exhausted"};
    }

    const InputReceiverSnapshot input_snapshot = input_.snapshot();
    const OutputHistorySnapshot output_snapshot = output_.snapshot();
    if (controller_next_input > input_snapshot.next_expected_sequence) {
        append_event(
            SessionEventKind::attachment_denied,
            SessionDenialReason::protocol_violation);
        return Status{
            ErrorCode::protocol_error,
            "attachment input position advances beyond committed input"};
    }
    if (controller_next_output > output_snapshot.next_sequence) {
        append_event(
            SessionEventKind::attachment_denied,
            SessionDenialReason::protocol_violation);
        return Status{
            ErrorCode::protocol_error,
            "attachment output position advances beyond produced output"};
    }

    OutputHistory output_candidate = output_;
    const bool gap = controller_next_output < output_snapshot.base_sequence;
    if (!gap) {
        const Status acknowledged =
            output_candidate.acknowledge(controller_next_output);
        if (!acknowledged.ok()) {
            append_event(
                SessionEventKind::attachment_denied,
                reason_for_status(acknowledged));
            return acknowledged;
        }
    }

    AttachmentFence fence_candidate = fence_;
    auto token = fence_candidate.attach(principal_id, nonce);
    if (!token.ok()) {
        append_event(
            SessionEventKind::attachment_denied,
            reason_for_status(token.status()));
        return token.status();
    }

    // Capacity was reserved at construction, so no bounded state is published
    // until every potentially failing validation and history copy succeeds.
    seen_nonces_.push_back(nonce);
    output_ = std::move(output_candidate);
    fence_ = std::move(fence_candidate);

    const OutputHistorySnapshot accepted_output = output_.snapshot();
    append_event(
        kind == AttachKind::attach
            ? SessionEventKind::attached
            : SessionEventKind::resumed,
        gap ? SessionDenialReason::output_gap
            : SessionDenialReason::none);
    return SessionAttachmentResult{
        token.value(), input_snapshot.next_expected_sequence,
        accepted_output.base_sequence, accepted_output.next_sequence, gap};
}

Status InteractiveSession::validate_attachment(
    const AttachmentToken &token) const {
    const Status active = require_active();
    if (!active.ok()) return active;
    return fence_.validate(token);
}

Status InteractiveSession::detach(const AttachmentToken &token) {
    const Status active = require_active();
    if (!active.ok()) return active;
    const Status detached = fence_.detach(token);
    if (!detached.ok()) return detached;
    append_event(SessionEventKind::detached);
    return Status::success();
}

Result<InputOfferResult> InteractiveSession::offer_input(
    const AttachmentToken &token, std::uint64_t sequence,
    std::span<const std::uint8_t> bytes) {
    const Status accepted = validate_attachment(token);
    if (!accepted.ok()) {
        if (validate_config().ok()) {
            SessionDenialReason reason = reason_for_status(accepted);
            if (lifecycle_ != SessionLifecycle::active) {
                reason = reason_for_lifecycle(lifecycle_);
            } else if (accepted.code() == ErrorCode::protocol_error ||
                       accepted.code() == ErrorCode::unavailable) {
                reason = SessionDenialReason::stale_attachment;
            }
            append_event(SessionEventKind::input_denied, reason);
        }
        return accepted;
    }
    auto offered = input_.offer(sequence, bytes);
    if (!offered.ok()) {
        append_event(
            SessionEventKind::input_denied,
            reason_for_status(offered.status()));
        return offered.status();
    }
    SessionEventKind kind = SessionEventKind::input_staged;
    switch (offered.value().disposition) {
        case InputDisposition::staged:
            kind = SessionEventKind::input_staged;
            break;
        case InputDisposition::pending:
            kind = SessionEventKind::input_pending;
            break;
        case InputDisposition::duplicate:
            kind = SessionEventKind::input_duplicate;
            break;
        case InputDisposition::future_gap:
            kind = SessionEventKind::input_gap;
            break;
    }
    append_event(kind);
    return offered;
}

Result<std::vector<std::uint8_t>> InteractiveSession::pending_input() const {
    const Status active = require_active();
    if (!active.ok()) return active;
    return input_.pending_bytes();
}

Result<InputConsumeResult> InteractiveSession::consume_input(
    std::size_t bytes) {
    const Status active = require_active();
    if (!active.ok()) return active;
    auto consumed = input_.consume_staged(bytes);
    if (!consumed.ok()) return consumed.status();
    if (consumed.value().committed) {
        append_event(SessionEventKind::input_committed);
    }
    return consumed;
}

Status InteractiveSession::fail_input() {
    const Status active = require_active();
    if (!active.ok()) return active;
    const Status failed = input_.fail_staged();
    if (!failed.ok()) return failed;
    lifecycle_ = SessionLifecycle::failed;
    fence_.invalidate();
    append_event(
        SessionEventKind::input_failed,
        SessionDenialReason::terminal_incarnation);
    return Status::success();
}

Result<std::uint64_t> InteractiveSession::append_output(
    std::span<const std::uint8_t> bytes) {
    const Status active = require_active();
    if (!active.ok()) return active;
    auto appended = output_.append(bytes);
    if (!appended.ok()) return appended.status();
    append_event(SessionEventKind::output_appended);
    return appended;
}

Result<OutputReadResult> InteractiveSession::read_output(
    const AttachmentToken &token, std::uint64_t sequence,
    std::size_t maximum_bytes) const {
    const Status accepted = validate_attachment(token);
    if (!accepted.ok()) return accepted;
    return output_.read_from(sequence, maximum_bytes);
}

Status InteractiveSession::acknowledge_output(
    const AttachmentToken &token,
    std::uint64_t next_expected_sequence) {
    const Status accepted = validate_attachment(token);
    if (!accepted.ok()) return accepted;
    const Status acknowledged = output_.acknowledge(next_expected_sequence);
    if (!acknowledged.ok()) return acknowledged;
    append_event(SessionEventKind::output_acknowledged);
    return Status::success();
}

Status InteractiveSession::replace_incarnation() {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (lifecycle_ == SessionLifecycle::closed) {
        return Status{ErrorCode::unavailable,
                      "closed interactive session cannot replace its process"};
    }

    AttachmentFence fence_candidate = fence_;
    const Status replaced = fence_candidate.replace_incarnation();
    if (!replaced.ok()) return replaced;
    InputReceiver input_candidate(config_.input);
    OutputHistory output_candidate(config_.output);

    fence_ = std::move(fence_candidate);
    input_ = std::move(input_candidate);
    output_ = std::move(output_candidate);
    lifecycle_ = SessionLifecycle::active;
    append_event(SessionEventKind::incarnation_replaced);
    return Status::success();
}

Status InteractiveSession::close(
    const AttachmentToken &token, SessionCloseReason reason) {
    const Status active = require_active();
    if (!active.ok()) return active;
    if (!controller_close_reason(reason)) {
        return Status{ErrorCode::protocol_error,
                      "controller selected an internal-only close reason"};
    }
    const Status accepted = fence_.validate(token);
    if (!accepted.ok()) return accepted;

    lifecycle_ = SessionLifecycle::closed;
    fence_.invalidate();
    append_event(SessionEventKind::closed, SessionDenialReason::none, reason);
    wipe_stream_state();
    return Status::success();
}

Status InteractiveSession::terminate(SessionCloseReason reason) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (!internal_close_reason(reason)) {
        return Status{ErrorCode::invalid_argument,
                      "interactive termination reason is unassigned"};
    }
    if (lifecycle_ == SessionLifecycle::closed) {
        return Status{ErrorCode::unavailable,
                      "interactive session is already closed"};
    }

    lifecycle_ = SessionLifecycle::closed;
    fence_.invalidate();
    append_event(
        SessionEventKind::terminated, SessionDenialReason::none, reason);
    wipe_stream_state();
    return Status::success();
}

Result<MessageReplayAdmission> InteractiveSession::begin_control(
    std::uint64_t message_id, std::span<const std::uint8_t> request,
    std::size_t result_capacity) {
    // Completed duplicates and pending/conflicting IDs must remain observable
    // after close so a lost CLOSE result can be replayed safely. A fresh ID,
    // however, must never acquire an execution reservation in a terminal
    // session.
    auto retained = control_replay_.lookup(message_id, request);
    if (retained.ok()) {
        MessageReplayAdmission replay;
        replay.kind = MessageReplayAdmissionKind::replay;
        replay.result = std::move(retained.value());
        append_event(SessionEventKind::control_replayed);
        return replay;
    }
    if (retained.status().code() != ErrorCode::not_found) {
        SessionDenialReason reason = reason_for_status(retained.status());
        if (retained.status().code() == ErrorCode::unavailable) {
            reason = SessionDenialReason::replay_in_progress;
        }
        append_event(SessionEventKind::control_denied, reason);
        return retained.status();
    }

    const Status active = require_active();
    if (!active.ok()) {
        append_event(
            SessionEventKind::control_denied,
            validate_config().ok()
                ? reason_for_lifecycle(lifecycle_)
                : reason_for_status(active));
        return active;
    }

    auto admission =
        control_replay_.reserve(message_id, request, result_capacity);
    if (!admission.ok()) {
        SessionDenialReason reason = reason_for_status(admission.status());
        if (admission.status().code() == ErrorCode::unavailable) {
            reason = SessionDenialReason::replay_in_progress;
        }
        append_event(SessionEventKind::control_denied, reason);
        return admission.status();
    }
    return admission;
}

Status InteractiveSession::complete_control(
    const MessageReplayReservation &reservation,
    std::span<const std::uint8_t> result) {
    const Status committed = control_replay_.commit(reservation, result);
    if (committed.ok()) {
        append_event(SessionEventKind::control_committed);
    } else {
        append_event(
            SessionEventKind::control_denied,
            reason_for_status(committed));
    }
    return committed;
}

Status InteractiveSession::cancel_control(
    const MessageReplayReservation &reservation) {
    const Status cancelled = control_replay_.cancel(reservation);
    if (cancelled.ok()) {
        append_event(SessionEventKind::control_cancelled);
    }
    return cancelled;
}

Result<std::vector<std::uint8_t>>
InteractiveSession::lookup_control_result(
    std::uint64_t message_id,
    std::span<const std::uint8_t> request) const {
    return control_replay_.lookup(message_id, request);
}

InteractiveSessionSnapshot InteractiveSession::snapshot() const noexcept {
    std::optional<AttachmentToken> current;
    if (fence_.current()) current = *fence_.current();
    return InteractiveSessionSnapshot{
        session_id_,
        principal_id_,
        lifecycle_,
        fence_.incarnation(),
        fence_.generation(),
        std::move(current),
        input_.snapshot(),
        output_.snapshot(),
        control_replay_.snapshot(),
        seen_nonces_.size(),
        config_.maximum_attachment_nonces,
        events_.size(),
        dropped_events_,
        config_.maximum_events};
}

std::span<const SessionEvent> InteractiveSession::events() const noexcept {
    return events_;
}

std::vector<SessionEvent> InteractiveSession::drain_events() {
    std::vector<SessionEvent> drained;
    drained.swap(events_);
    events_.reserve(config_.maximum_events);
    return drained;
}

void InteractiveSession::append_event(
    SessionEventKind kind, SessionDenialReason denial_reason,
    std::optional<SessionCloseReason> close_reason) {
    if (config_.maximum_events == 0U || next_event_ordinal_ == 0U) return;
    const InputReceiverSnapshot input_snapshot = input_.snapshot();
    const OutputHistorySnapshot output_snapshot = output_.snapshot();
    SessionEvent event;
    event.ordinal = next_event_ordinal_;
    event.kind = kind;
    event.denial_reason = denial_reason;
    if (close_reason) {
        event.close_reason = *close_reason;
        event.has_close_reason = true;
    }
    event.session_id = session_id_;
    event.principal_id = principal_id_;
    event.incarnation = fence_.incarnation();
    event.generation = fence_.generation();
    event.next_input_sequence = input_snapshot.next_expected_sequence;
    event.output_base_sequence = output_snapshot.base_sequence;
    event.output_next_sequence = output_snapshot.next_sequence;

    if (events_.size() == config_.maximum_events) {
        std::move(events_.begin() + 1, events_.end(), events_.begin());
        events_.back() = event;
        if (dropped_events_ != std::numeric_limits<std::size_t>::max()) {
            ++dropped_events_;
        }
    } else {
        events_.push_back(event);
    }
    if (next_event_ordinal_ != std::numeric_limits<std::uint64_t>::max()) {
        ++next_event_ordinal_;
    } else {
        next_event_ordinal_ = 0U;
    }
}

void InteractiveSession::wipe_stream_state() {
    input_ = InputReceiver(config_.input);
    output_ = OutputHistory(config_.output);
}

SessionDirectory::SessionDirectory() : SessionDirectory(Config{}) {}

SessionDirectory::SessionDirectory(Config config) : config_(config) {
    sessions_.reserve(config_.maximum_sessions_per_device);
}

Status SessionDirectory::validate_config() const {
    if (config_.maximum_sessions_per_principal == 0U ||
        config_.maximum_sessions_per_device == 0U ||
        config_.maximum_sessions_per_principal >
            config_.maximum_sessions_per_device) {
        return Status{ErrorCode::invalid_argument,
                      "interactive session directory bounds are invalid"};
    }
    return Status::success();
}

std::size_t SessionDirectory::count_principal(
    const PrincipalId &principal_id) const noexcept {
    return static_cast<std::size_t>(std::count_if(
        sessions_.begin(), sessions_.end(),
        [&principal_id](const std::unique_ptr<InteractiveSession> &session) {
            return session->snapshot().principal_id == principal_id;
        }));
}

Result<SessionOpenResult> SessionDirectory::open(
    SessionId session_id, PrincipalId principal_id,
    AttachmentNonce nonce, std::uint64_t incarnation) {
    // Validate identity before duplicate and quota checks so malformed callers
    // cannot use denial ordering to probe live directory occupancy.
    if (all_zero(session_id) || all_zero(principal_id) || all_zero(nonce) ||
        incarnation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "session open identity must be nonzero"};
    }
    const Status configured = validate_config();
    if (!configured.ok()) return configured;

    for (const auto &session : sessions_) {
        if (session->snapshot().session_id == session_id) {
            return Status{ErrorCode::protocol_error,
                          "session ID is already live on this device"};
        }
    }
    if (sessions_.size() >= config_.maximum_sessions_per_device) {
        return Status{ErrorCode::resource_exhausted,
                      "device interactive-session quota is exhausted"};
    }
    if (count_principal(principal_id) >=
        config_.maximum_sessions_per_principal) {
        return Status{ErrorCode::resource_exhausted,
                      "principal interactive-session quota is exhausted"};
    }

    auto candidate = std::make_unique<InteractiveSession>(
        session_id, principal_id, incarnation, config_.session);
    const InteractiveSessionSnapshot initial = candidate->snapshot();
    auto attached = candidate->attach(
        principal_id, nonce, initial.input.next_expected_sequence,
        initial.output.next_sequence);
    if (!attached.ok()) return attached.status();
    InteractiveSession *published = candidate.get();
    sessions_.push_back(std::move(candidate));
    return SessionOpenResult{published, attached.value()};
}

Result<InteractiveSession *> SessionDirectory::find(
    const SessionId &session_id) {
    if (all_zero(session_id)) {
        return Status{ErrorCode::invalid_argument,
                      "session lookup ID may not be all zero"};
    }
    const auto found = std::find_if(
        sessions_.begin(), sessions_.end(),
        [&session_id](const std::unique_ptr<InteractiveSession> &session) {
            return session->snapshot().session_id == session_id;
        });
    if (found == sessions_.end()) {
        return Status{ErrorCode::not_found,
                      "interactive session is not present"};
    }
    return found->get();
}

Result<const InteractiveSession *> SessionDirectory::find(
    const SessionId &session_id) const {
    if (all_zero(session_id)) {
        return Status{ErrorCode::invalid_argument,
                      "session lookup ID may not be all zero"};
    }
    const auto found = std::find_if(
        sessions_.begin(), sessions_.end(),
        [&session_id](const std::unique_ptr<InteractiveSession> &session) {
            return session->snapshot().session_id == session_id;
        });
    if (found == sessions_.end()) {
        return Status{ErrorCode::not_found,
                      "interactive session is not present"};
    }
    return found->get();
}

Status SessionDirectory::erase_closed(const SessionId &session_id) {
    auto released = release_closed(session_id);
    if (!released.ok()) return released.status();
    return Status::success();
}

Result<std::unique_ptr<InteractiveSession>> SessionDirectory::release_closed(
    const SessionId &session_id) {
    if (all_zero(session_id)) {
        return Status{ErrorCode::invalid_argument,
                      "session release ID may not be all zero"};
    }
    auto found = std::find_if(
        sessions_.begin(), sessions_.end(),
        [&session_id](const std::unique_ptr<InteractiveSession> &session) {
            return session->snapshot().session_id == session_id;
        });
    if (found == sessions_.end()) {
        return Status{ErrorCode::not_found,
                      "interactive session is not present"};
    }
    if ((*found)->snapshot().lifecycle != SessionLifecycle::closed) {
        return Status{ErrorCode::unavailable,
                      "only a closed interactive session may be released"};
    }
    std::unique_ptr<InteractiveSession> released = std::move(*found);
    sessions_.erase(found);
    return released;
}

SessionDirectorySnapshot SessionDirectory::snapshot() const noexcept {
    std::size_t maximum_observed = 0U;
    for (const auto &session : sessions_) {
        maximum_observed = std::max(
            maximum_observed,
            count_principal(session->snapshot().principal_id));
    }
    return SessionDirectorySnapshot{
        sessions_.size(),
        maximum_observed,
        config_.maximum_sessions_per_principal,
        config_.maximum_sessions_per_device,
        maximum_observed <= config_.maximum_sessions_per_principal,
        sessions_.size() <= config_.maximum_sessions_per_device};
}

std::string_view to_string(SessionLifecycle value) noexcept {
    switch (value) {
        case SessionLifecycle::active: return "active";
        case SessionLifecycle::failed: return "failed";
        case SessionLifecycle::closed: return "closed";
    }
    return "unknown";
}

std::string_view to_string(SessionEventKind value) noexcept {
    switch (value) {
        case SessionEventKind::opened: return "opened";
        case SessionEventKind::attached: return "attached";
        case SessionEventKind::resumed: return "resumed";
        case SessionEventKind::detached: return "detached";
        case SessionEventKind::input_staged: return "input-staged";
        case SessionEventKind::input_pending: return "input-pending";
        case SessionEventKind::input_duplicate: return "input-duplicate";
        case SessionEventKind::input_gap: return "input-gap";
        case SessionEventKind::input_committed: return "input-committed";
        case SessionEventKind::input_failed: return "input-failed";
        case SessionEventKind::output_appended: return "output-appended";
        case SessionEventKind::output_acknowledged: return "output-acknowledged";
        case SessionEventKind::incarnation_replaced: return "incarnation-replaced";
        case SessionEventKind::closed: return "closed";
        case SessionEventKind::terminated: return "terminated";
        case SessionEventKind::control_committed: return "control-committed";
        case SessionEventKind::control_replayed: return "control-replayed";
        case SessionEventKind::control_cancelled: return "control-cancelled";
        case SessionEventKind::control_denied: return "control-denied";
        case SessionEventKind::input_denied: return "input-denied";
        case SessionEventKind::attachment_denied: return "attachment-denied";
    }
    return "unknown";
}

std::string_view to_string(SessionDenialReason value) noexcept {
    switch (value) {
        case SessionDenialReason::none: return "none";
        case SessionDenialReason::invalid_identity: return "invalid-identity";
        case SessionDenialReason::stale_attachment: return "stale-attachment";
        case SessionDenialReason::protocol_violation: return "protocol-violation";
        case SessionDenialReason::output_gap: return "output-gap";
        case SessionDenialReason::resource_limit: return "resource-limit";
        case SessionDenialReason::replay_in_progress: return "replay-in-progress";
        case SessionDenialReason::terminal_incarnation: return "terminal-incarnation";
        case SessionDenialReason::closed: return "closed";
        case SessionDenialReason::unavailable: return "unavailable";
        case SessionDenialReason::invalid_request: return "invalid-request";
    }
    return "unknown";
}

std::string_view to_string(SessionCloseReason value) noexcept {
    switch (value) {
        case SessionCloseReason::normal: return "normal";
        case SessionCloseReason::controller_request: return "controller-request";
        case SessionCloseReason::authority_revoked: return "authority-revoked";
        case SessionCloseReason::protocol_violation: return "protocol-violation";
        case SessionCloseReason::resource_exhaustion: return "resource-exhaustion";
        case SessionCloseReason::process_failure: return "process-failure";
        case SessionCloseReason::daemon_shutdown: return "daemon-shutdown";
    }
    return "unknown";
}

}  // namespace iotox::interactive
