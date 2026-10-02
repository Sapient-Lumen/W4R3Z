#pragma once

#include "iotox/interactive.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace iotox::interactive {

// A control message is admitted before its side effect. The reservation owns
// enough bounded result storage to make post-effect recording allocation-free.
struct MessageReplayReservation {
    std::uint64_t reservation_id{0U};
    std::uint64_t message_id{0U};
    std::size_t result_capacity{0U};

    [[nodiscard]] bool operator==(const MessageReplayReservation &) const = default;
};

enum class MessageReplayAdmissionKind : std::uint8_t {
    execute = 1U,
    replay = 2U,
};

struct MessageReplayAdmission {
    MessageReplayAdmissionKind kind{MessageReplayAdmissionKind::execute};
    MessageReplayReservation reservation{};
    std::vector<std::uint8_t> result;
};

struct MessageReplaySnapshot {
    std::size_t entries{0U};
    std::size_t pending_entries{0U};
    std::size_t retained_bytes{0U};
    std::size_t reserved_bytes{0U};
    std::size_t maximum_entries{0U};
    std::size_t maximum_bytes{0U};
    std::size_t maximum_result_bytes{0U};
    bool entry_bound_respected{false};
    bool byte_bound_respected{false};
};

// Exact, fail-closed duplicate-result retention. IDs are never evicted or
// reused inside one session: when the bounded cache fills, new controls are
// refused instead of risking duplicate side effects.
class MessageReplayCache {
  public:
    struct Config {
        std::size_t maximum_entries{128U};
        std::size_t maximum_bytes{256U * 1024U};
        std::size_t maximum_result_bytes{4096U};
    };

    MessageReplayCache();
    explicit MessageReplayCache(Config config);
    ~MessageReplayCache();

    MessageReplayCache(const MessageReplayCache &) = delete;
    MessageReplayCache &operator=(const MessageReplayCache &) = delete;
    MessageReplayCache(MessageReplayCache &&other) noexcept;
    MessageReplayCache &operator=(MessageReplayCache &&other) noexcept;

    [[nodiscard]] Result<MessageReplayAdmission> reserve(
        std::uint64_t message_id, std::span<const std::uint8_t> request,
        std::size_t result_capacity);
    [[nodiscard]] Status commit(
        const MessageReplayReservation &reservation,
        std::span<const std::uint8_t> result);
    [[nodiscard]] Status cancel(
        const MessageReplayReservation &reservation);
    [[nodiscard]] Result<std::vector<std::uint8_t>> lookup(
        std::uint64_t message_id,
        std::span<const std::uint8_t> request) const;
    [[nodiscard]] MessageReplaySnapshot snapshot() const noexcept;

  private:
    struct Entry {
        std::uint64_t message_id{0U};
        std::uint64_t reservation_id{0U};
        std::size_t result_capacity{0U};
        std::size_t budget_bytes{0U};
        bool pending{true};
        std::vector<std::uint8_t> request;
        std::vector<std::uint8_t> result;
    };

    [[nodiscard]] Status validate_config() const;
    [[nodiscard]] const Entry *find_message(std::uint64_t message_id) const;
    [[nodiscard]] Entry *find_reservation(
        const MessageReplayReservation &reservation);
    void wipe_entries() noexcept;

    Config config_;
    std::vector<Entry> entries_;
    std::size_t retained_bytes_{0U};
    std::size_t reserved_bytes_{0U};
    std::uint64_t next_reservation_id_{1U};
};

enum class SessionLifecycle : std::uint8_t {
    active = 1U,
    failed = 2U,
    closed = 3U,
};

// Values 0..4 are legal on a controller CLOSE. Values 5..6 are internal-only
// termination facts and can never be selected by a remote controller.
enum class SessionCloseReason : std::uint16_t {
    normal = 0U,
    controller_request = 1U,
    authority_revoked = 2U,
    protocol_violation = 3U,
    resource_exhaustion = 4U,
    process_failure = 5U,
    daemon_shutdown = 6U,
};

enum class SessionEventKind : std::uint8_t {
    opened = 1U,
    attached = 2U,
    resumed = 3U,
    detached = 4U,
    input_staged = 5U,
    input_pending = 6U,
    input_duplicate = 7U,
    input_gap = 8U,
    input_committed = 9U,
    input_failed = 10U,
    output_appended = 11U,
    output_acknowledged = 12U,
    incarnation_replaced = 13U,
    closed = 14U,
    terminated = 15U,
    control_committed = 16U,
    control_replayed = 17U,
    control_cancelled = 18U,
    control_denied = 19U,
    input_denied = 20U,
    attachment_denied = 21U,
};

enum class SessionDenialReason : std::uint8_t {
    none = 0U,
    invalid_identity = 1U,
    stale_attachment = 2U,
    protocol_violation = 3U,
    output_gap = 4U,
    resource_limit = 5U,
    replay_in_progress = 6U,
    terminal_incarnation = 7U,
    closed = 8U,
    unavailable = 9U,
    invalid_request = 10U,
};

struct SessionEvent {
    std::uint64_t ordinal{0U};
    SessionEventKind kind{SessionEventKind::opened};
    SessionDenialReason denial_reason{SessionDenialReason::none};
    SessionCloseReason close_reason{SessionCloseReason::normal};
    bool has_close_reason{false};
    SessionId session_id{};
    PrincipalId principal_id{};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};
    std::uint64_t next_input_sequence{0U};
    std::uint64_t output_base_sequence{0U};
    std::uint64_t output_next_sequence{0U};
};

struct SessionAttachmentResult {
    AttachmentToken token{};
    std::uint64_t next_input_sequence{0U};
    std::uint64_t output_base_sequence{0U};
    std::uint64_t output_next_sequence{0U};
    bool output_gap{false};
};

struct InteractiveSessionSnapshot {
    SessionId session_id{};
    PrincipalId principal_id{};
    SessionLifecycle lifecycle{SessionLifecycle::active};
    std::uint64_t incarnation{0U};
    std::uint64_t generation{0U};
    std::optional<AttachmentToken> current_attachment;
    InputReceiverSnapshot input{};
    OutputHistorySnapshot output{};
    MessageReplaySnapshot control_replay{};
    std::size_t remembered_attachment_nonces{0U};
    std::size_t maximum_attachment_nonces{0U};
    std::size_t retained_events{0U};
    std::size_t dropped_events{0U};
    std::size_t maximum_events{0U};
};

// Pure Ratox R1 state. This class has no toxcore, wall clock, filesystem, PTY,
// process, or authority dependency. Its caller supplies authenticated identity,
// opaque bytes, and explicit lifecycle actions.
class InteractiveSession {
  public:
    struct Config {
        InputReceiver::Config input{};
        OutputHistory::Config output{};
        MessageReplayCache::Config control_replay{};
        std::size_t maximum_attachment_nonces{64U};
        std::size_t maximum_events{128U};
        std::uint64_t initial_generation{0U};
    };

    InteractiveSession(
        SessionId session_id, PrincipalId principal_id,
        std::uint64_t incarnation = 1U);
    InteractiveSession(
        SessionId session_id, PrincipalId principal_id,
        std::uint64_t incarnation, Config config);

    InteractiveSession(const InteractiveSession &) = delete;
    InteractiveSession &operator=(const InteractiveSession &) = delete;
    InteractiveSession(InteractiveSession &&) noexcept = default;
    InteractiveSession &operator=(InteractiveSession &&) noexcept = default;

    [[nodiscard]] Result<SessionAttachmentResult> attach(
        PrincipalId principal_id, AttachmentNonce nonce,
        std::uint64_t controller_next_input,
        std::uint64_t controller_next_output);
    [[nodiscard]] Result<SessionAttachmentResult> resume(
        PrincipalId principal_id, AttachmentNonce nonce,
        std::uint64_t controller_next_input,
        std::uint64_t controller_next_output);
    [[nodiscard]] Status validate_attachment(
        const AttachmentToken &token) const;
    [[nodiscard]] Status detach(const AttachmentToken &token);

    [[nodiscard]] Result<InputOfferResult> offer_input(
        const AttachmentToken &token, std::uint64_t sequence,
        std::span<const std::uint8_t> bytes);
    [[nodiscard]] Result<std::vector<std::uint8_t>> pending_input() const;
    [[nodiscard]] Result<InputConsumeResult> consume_input(std::size_t bytes);
    [[nodiscard]] Status fail_input();

    [[nodiscard]] Result<std::uint64_t> append_output(
        std::span<const std::uint8_t> bytes);
    [[nodiscard]] Result<OutputReadResult> read_output(
        const AttachmentToken &token, std::uint64_t sequence,
        std::size_t maximum_bytes) const;
    [[nodiscard]] Status acknowledge_output(
        const AttachmentToken &token,
        std::uint64_t next_expected_sequence);

    [[nodiscard]] Status replace_incarnation();
    [[nodiscard]] Status close(
        const AttachmentToken &token, SessionCloseReason reason);
    [[nodiscard]] Status terminate(SessionCloseReason reason);

    [[nodiscard]] Result<MessageReplayAdmission> begin_control(
        std::uint64_t message_id, std::span<const std::uint8_t> request,
        std::size_t result_capacity);
    [[nodiscard]] Status complete_control(
        const MessageReplayReservation &reservation,
        std::span<const std::uint8_t> result);
    [[nodiscard]] Status cancel_control(
        const MessageReplayReservation &reservation);
    [[nodiscard]] Result<std::vector<std::uint8_t>> lookup_control_result(
        std::uint64_t message_id,
        std::span<const std::uint8_t> request) const;

    [[nodiscard]] InteractiveSessionSnapshot snapshot() const noexcept;
    [[nodiscard]] std::span<const SessionEvent> events() const noexcept;
    [[nodiscard]] std::vector<SessionEvent> drain_events();

  private:
    enum class AttachKind : std::uint8_t {
        attach,
        resume,
    };

    [[nodiscard]] Status validate_config() const;
    [[nodiscard]] Status require_active() const;
    [[nodiscard]] Result<SessionAttachmentResult> attach_impl(
        AttachKind kind, PrincipalId principal_id, AttachmentNonce nonce,
        std::uint64_t controller_next_input,
        std::uint64_t controller_next_output);
    [[nodiscard]] bool nonce_seen(const AttachmentNonce &nonce) const;
    void append_event(
        SessionEventKind kind,
        SessionDenialReason denial_reason = SessionDenialReason::none,
        std::optional<SessionCloseReason> close_reason = std::nullopt);
    void wipe_stream_state();

    Config config_;
    SessionId session_id_{};
    PrincipalId principal_id_{};
    SessionLifecycle lifecycle_{SessionLifecycle::active};
    AttachmentFence fence_;
    InputReceiver input_;
    OutputHistory output_;
    MessageReplayCache control_replay_;
    std::vector<AttachmentNonce> seen_nonces_;
    std::vector<SessionEvent> events_;
    std::size_t dropped_events_{0U};
    std::uint64_t next_event_ordinal_{1U};
};

struct SessionDirectorySnapshot {
    std::size_t sessions{0U};
    std::size_t maximum_observed_sessions_per_principal{0U};
    std::size_t maximum_sessions_per_principal{0U};
    std::size_t maximum_sessions_per_device{0U};
    bool principal_bound_respected{false};
    bool device_bound_respected{false};
};

struct SessionOpenResult {
    InteractiveSession *session{nullptr};
    SessionAttachmentResult attachment{};
};

// One directory represents one local device. It applies the frozen R1 limits
// atomically before publishing a new session pointer.
class SessionDirectory {
  public:
    struct Config {
        std::size_t maximum_sessions_per_principal{2U};
        std::size_t maximum_sessions_per_device{8U};
        InteractiveSession::Config session{};
    };

    SessionDirectory();
    explicit SessionDirectory(Config config);

    [[nodiscard]] Result<SessionOpenResult> open(
        SessionId session_id, PrincipalId principal_id,
        AttachmentNonce nonce, std::uint64_t incarnation = 1U);
    [[nodiscard]] Result<InteractiveSession *> find(
        const SessionId &session_id);
    [[nodiscard]] Result<const InteractiveSession *> find(
        const SessionId &session_id) const;
    // Transfers a closed session to its caller without discarding the exact
    // control-replay record. This releases live principal/device quota while
    // allowing an outer transport epoch to retain a bounded tombstone.
    [[nodiscard]] Result<std::unique_ptr<InteractiveSession>> release_closed(
        const SessionId &session_id);
    [[nodiscard]] Status erase_closed(const SessionId &session_id);
    [[nodiscard]] SessionDirectorySnapshot snapshot() const noexcept;

  private:
    [[nodiscard]] Status validate_config() const;
    [[nodiscard]] std::size_t count_principal(
        const PrincipalId &principal_id) const noexcept;

    Config config_;
    std::vector<std::unique_ptr<InteractiveSession>> sessions_;
};

[[nodiscard]] std::string_view to_string(SessionLifecycle value) noexcept;
[[nodiscard]] std::string_view to_string(SessionEventKind value) noexcept;
[[nodiscard]] std::string_view to_string(SessionDenialReason value) noexcept;
[[nodiscard]] std::string_view to_string(SessionCloseReason value) noexcept;

}  // namespace iotox::interactive
