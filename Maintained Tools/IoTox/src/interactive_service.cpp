#include "iotox/interactive_service.hpp"
#include "iotox/security/sodium.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <string_view>
#include <utility>

namespace iotox::interactive {
namespace {

using protocol::ratox::Frame;
using protocol::ratox::FrameType;

constexpr std::uint16_t kResultSuccess = 0U;
constexpr std::uint16_t kResultDenied = 1U;
constexpr std::uint16_t kResultUnsupported = 2U;
constexpr std::uint16_t kResultBusy = 3U;
constexpr std::uint16_t kResultNotFound = 4U;
constexpr std::uint16_t kResultInvalid = 5U;
constexpr std::uint16_t kResultResourceExhausted = 6U;
constexpr std::uint16_t kResultUnavailable = 7U;
constexpr std::uint16_t kResultInternalFailure = 8U;

constexpr std::size_t kOpenResultPacketBytes =
    protocol::ratox::kHeaderBytes + 12U;
constexpr std::size_t kAttachResultPacketBytes =
    protocol::ratox::kHeaderBytes + 28U;
constexpr std::size_t kControlPacketBytes = protocol::ratox::kHeaderBytes;
constexpr std::size_t kExitPacketBytes =
    protocol::ratox::kHeaderBytes + 8U;
constexpr std::size_t kMaximumAdmissionRequestPacketBytes =
    protocol::ratox::kHeaderBytes + 16U;
constexpr std::size_t kMaximumAdmissionReservationBytes =
    kMaximumAdmissionRequestPacketBytes +
    protocol::ratox::kMaximumPacketBytes;
constexpr std::size_t kControlReplayRoutePrefixBytes = 16U;
constexpr std::array<std::uint8_t, 4U> kControlReplayRouteDomain{
    'I', '4', 'R', 'P'};

class ScopedByteWipe {
  public:
    explicit ScopedByteWipe(std::vector<std::uint8_t> &bytes) noexcept
        : bytes_(&bytes) {}
    ~ScopedByteWipe() {
        security::secure_wipe(*bytes_);
        bytes_->clear();
    }

    ScopedByteWipe(const ScopedByteWipe &) = delete;
    ScopedByteWipe &operator=(const ScopedByteWipe &) = delete;

  private:
    std::vector<std::uint8_t> *bytes_;
};

void clear_packet(RatoxOutboundPacket &packet) noexcept {
    security::secure_wipe(packet.storage);
    packet = RatoxOutboundPacket{};
}

bool all_zero(const PrincipalId &value) {
    return std::all_of(value.begin(), value.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

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

std::uint64_t read_u64(std::span<const std::uint8_t> input) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : input) value = (value << 8U) | byte;
    return value;
}

std::uint16_t result_for_status(const Status &status) {
    switch (status.code()) {
        case ErrorCode::ok: return kResultSuccess;
        case ErrorCode::invalid_argument:
        case ErrorCode::protocol_error:
            return kResultInvalid;
        case ErrorCode::not_found: return kResultNotFound;
        case ErrorCode::unsupported: return kResultUnsupported;
        case ErrorCode::resource_exhausted: return kResultResourceExhausted;
        case ErrorCode::unavailable:
        case ErrorCode::timeout:
        case ErrorCode::io_error:
            return kResultUnavailable;
        case ErrorCode::library_error:
        case ErrorCode::internal_error:
            return kResultInternalFailure;
    }
    return kResultInternalFailure;
}

ErrorCode error_for_result(std::uint16_t result) {
    switch (result) {
        case kResultSuccess: return ErrorCode::ok;
        case kResultDenied:
        case kResultBusy:
        case kResultUnavailable:
            return ErrorCode::unavailable;
        case kResultUnsupported: return ErrorCode::unsupported;
        case kResultNotFound: return ErrorCode::not_found;
        case kResultInvalid: return ErrorCode::invalid_argument;
        case kResultResourceExhausted: return ErrorCode::resource_exhausted;
        case kResultInternalFailure: return ErrorCode::internal_error;
    }
    return ErrorCode::internal_error;
}

bool controller_request_type(FrameType type) {
    switch (type) {
        case FrameType::open:
        case FrameType::attach:
        case FrameType::detach:
        case FrameType::input:
        case FrameType::output_ack:
        case FrameType::resize:
        case FrameType::ping:
        case FrameType::close:
        case FrameType::resume:
            return true;
        case FrameType::open_result:
        case FrameType::attach_result:
        case FrameType::input_ack:
        case FrameType::output:
        case FrameType::pong:
        case FrameType::exit_status:
        case FrameType::resume_result:
        case FrameType::output_gap:
            return false;
    }
    return false;
}

SessionCloseReason close_reason_from_wire(std::uint16_t value) {
    return static_cast<SessionCloseReason>(value);
}

terminal::CloseReason terminal_close_reason(SessionCloseReason reason) {
    switch (reason) {
        case SessionCloseReason::authority_revoked:
            return terminal::CloseReason::authority_revoked;
        case SessionCloseReason::daemon_shutdown:
            return terminal::CloseReason::daemon_shutdown;
        case SessionCloseReason::process_failure:
        case SessionCloseReason::protocol_violation:
        case SessionCloseReason::resource_exhaustion:
            return terminal::CloseReason::process_failure;
        case SessionCloseReason::normal:
        case SessionCloseReason::controller_request:
            return terminal::CloseReason::controller_request;
    }
    return terminal::CloseReason::process_failure;
}

std::uint16_t wire_close_reason(SessionCloseReason reason) {
    const auto value = static_cast<std::uint16_t>(reason);
    return std::min<std::uint16_t>(value, 4U);
}

RatoxTrafficClass traffic_for(FrameType type) {
    switch (type) {
        case FrameType::input_ack:
        case FrameType::output:
            return RatoxTrafficClass::interactive;
        default:
            return RatoxTrafficClass::control;
    }
}

}  // namespace

class RatoxService::Impl {
  public:
    Impl(
        terminal::ProfileRegistry &profiles,
        terminal::PtyProcessFactory &processes,
        Config config,
        std::vector<terminal::EnvironmentEntry> ambient_environment)
        : profiles_(&profiles),
          processes_(&processes),
          config_(config),
          ambient_environment_(std::move(ambient_environment)),
          next_message_id_(config.initial_outbound_message_id) {
        configuration_status_ = validate_config();
        if (!configuration_status_.ok()) return;

        directory_ = std::make_unique<SessionDirectory>(config_.directory);
        sessions_.reserve(
            config_.directory.maximum_sessions_per_device +
            config_.maximum_session_tombstones);
        replay_.reserve(config_.maximum_admission_replay_entries);
        events_.reserve(config_.maximum_events);
        outbound_slots_.resize(config_.maximum_outbound_packets);
        outbound_scratch_.resize(config_.maximum_outbound_packets);
    }

    ~Impl() {
        for (RatoxOutboundPacket &packet : outbound_slots_) {
            clear_packet(packet);
        }
        for (RatoxOutboundPacket &packet : outbound_scratch_) {
            clear_packet(packet);
        }
        for (ReplayEntry &entry : replay_) wipe_replay_entry(entry);
    }

    [[nodiscard]] Status receive(
        const RatoxPeerContext &peer,
        std::span<const std::uint8_t> packet,
        TimePoint now) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (!config_.enabled) {
            return Status{ErrorCode::unsupported,
                          "Ratox service is disabled by the local activation gate"};
        }
        if (peer.online_epoch == 0U || all_zero(peer.principal_id)) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox peer context has no online epoch or principal"};
        }
        if (!peer.transcript_confirmed) {
            return Status{ErrorCode::unavailable,
                          "Ratox packet is outside a confirmed IoTox transcript"};
        }
        if (config_.require_feature_negotiation && !peer.feature_negotiated) {
            return Status{ErrorCode::unsupported,
                          "Ratox feature is not negotiated for this online epoch"};
        }

        auto decoded = protocol::ratox::decode(packet);
        if (!decoded.ok()) {
            append_event(
                RatoxServiceEventKind::packet_rejected,
                decoded.status().code(), peer, nullptr, FrameType::open);
            return decoded.status();
        }
        Frame &frame = decoded.value();
        ScopedByteWipe frame_payload_wipe{frame.payload};
        if (frame.principal_id != peer.principal_id) {
            const Status mismatch{
                ErrorCode::protocol_error,
                "Ratox frame principal does not match the authenticated peer context"};
            append_event(
                RatoxServiceEventKind::packet_rejected,
                mismatch.code(), peer, nullptr, frame.type);
            return mismatch;
        }
        if (!controller_request_type(frame.type)) {
            const Status direction{
                ErrorCode::protocol_error,
                "Ratox terminal host received a frame assigned to the controller direction"};
            append_event(
                RatoxServiceEventKind::packet_rejected,
                direction.code(), peer, nullptr, frame.type);
            return direction;
        }

        if (frame.type == FrameType::open) {
            return handle_open(peer, frame, packet, now);
        }

        ActiveSession *active = find_session(frame.session_id);
        if (active == nullptr) {
            if (frame.type == FrameType::attach ||
                frame.type == FrameType::resume) {
                return handle_absent_attach(
                    peer, frame, packet,
                    peer.terminal_authorized
                        ? kResultNotFound
                        : kResultDenied);
            }
            const Status absent{
                ErrorCode::not_found,
                "Ratox session is not present on this device"};
            append_event(
                RatoxServiceEventKind::packet_rejected,
                absent.code(), peer, nullptr, frame.type);
            return absent;
        }
        if (active->state->snapshot().principal_id != peer.principal_id) {
            const Status mismatch{
                ErrorCode::protocol_error,
                "Ratox session principal does not match the authenticated context"};
            append_event(
                RatoxServiceEventKind::packet_rejected,
                mismatch.code(), peer, active, frame.type);
            return mismatch;
        }

        if (!peer.terminal_authorized) {
            // A stale or absent exact-head proof fences only the authenticated
            // transport epoch. A separate principal_revoked() reconciliation
            // handles an actual durable-ledger revocation, including detached
            // sessions. Keeping the two transitions distinct avoids killing a
            // still-authorized detached session merely because one route is
            // waiting for a refreshed proof at a new ledger head.
            if (!active->authority_revoked) {
                static_cast<void>(authority_revoked(
                    peer.friend_number, peer.online_epoch,
                    peer.principal_id, now));
            }
            if (frame.type == FrameType::attach ||
                frame.type == FrameType::resume) {
                return handle_absent_attach(
                    peer, frame, packet, kResultDenied);
            }
            const Status denied{
                ErrorCode::unavailable,
                "Ratox authority is absent at the current exact ledger head"};
            append_event(
                RatoxServiceEventKind::packet_rejected,
                denied.code(), peer, active, frame.type);
            return denied;
        }

        if (active->authority_revoked) {
            const Status denied{
                ErrorCode::unavailable,
                "Ratox session authority was revoked and cannot be replayed or reattached"};
            append_event(
                RatoxServiceEventKind::packet_rejected,
                denied.code(), peer, active, frame.type);
            return denied;
        }

        // The pure session replay cache is intentionally transport agnostic.
        // Scope every live-session control to its authenticated friend/epoch
        // before consulting that cache so a delayed or parallel route cannot
        // replay, conflict with, or permanently reserve another route's
        // message IDs. OPEN and absent ATTACH/RESUME use the separate
        // route-keyed admission cache above.
        std::array<
            std::uint8_t,
            kControlReplayRoutePrefixBytes +
                protocol::ratox::kMaximumPacketBytes> scoped_request{};
        std::copy(
            kControlReplayRouteDomain.begin(),
            kControlReplayRouteDomain.end(), scoped_request.begin());
        write_u32(
            std::span<std::uint8_t>{scoped_request}.subspan(4U, 4U),
            peer.friend_number);
        write_u64(
            std::span<std::uint8_t>{scoped_request}.subspan(8U, 8U),
            peer.online_epoch);
        std::copy(
            packet.begin(), packet.end(),
            scoped_request.begin() +
                static_cast<std::ptrdiff_t>(kControlReplayRoutePrefixBytes));
        const auto replay_request =
            std::span<const std::uint8_t>{scoped_request}.first(
                kControlReplayRoutePrefixBytes + packet.size());

        const Status dispatched = [&]() -> Status {
            switch (frame.type) {
                case FrameType::attach:
                    return handle_attach(
                        peer, *active, frame, replay_request, false, now);
                case FrameType::resume:
                    return handle_attach(
                        peer, *active, frame, replay_request, true, now);
                case FrameType::detach:
                    return handle_detach(
                        peer, *active, frame, replay_request, now);
                case FrameType::input:
                    return handle_input(peer, *active, frame, now);
                case FrameType::output_ack:
                    return handle_output_ack(
                        peer, *active, frame, replay_request);
                case FrameType::resize:
                    return handle_resize(
                        peer, *active, frame, replay_request);
                case FrameType::ping:
                    return handle_ping(
                        peer, *active, frame, replay_request);
                case FrameType::close:
                    return handle_close(
                        peer, *active, frame, replay_request, now);
                case FrameType::open:
                case FrameType::open_result:
                case FrameType::attach_result:
                case FrameType::input_ack:
                case FrameType::output:
                case FrameType::pong:
                case FrameType::exit_status:
                case FrameType::resume_result:
                case FrameType::output_gap:
                    break;
            }
            return Status{
                ErrorCode::internal_error,
                "Ratox dispatcher reached an unassigned frame branch"};
        }();
        security::secure_wipe(scoped_request);
        return dispatched;
    }

    [[nodiscard]] Status service(TimePoint now) {
        if (!configuration_status_.ok()) return configuration_status_;
        Status first_failure = Status::success();

        std::size_t remaining_writes = config_.maximum_input_write_operations;
        std::size_t remaining_reads = config_.maximum_output_read_operations;
        std::size_t remaining_frames = config_.maximum_output_frames;

        const std::size_t session_count = sessions_.size();
        if (session_count == 0U) {
            service_cursor_ = 0U;
            return first_failure;
        }
        const std::size_t start = service_cursor_ % session_count;
        for (std::size_t offset = 0U; offset < session_count; ++offset) {
            ActiveSession &active = sessions_[(start + offset) % session_count];
            if (active.finalized) continue;

            if (active.controller != nullptr && !active.terminal_done) {
                service_process(active, now, remaining_writes, remaining_reads,
                                first_failure);
            }
            if (active.route && !active.finalized) {
                emit_pending_input_ack(active);
                emit_output(active, remaining_frames);
            }
            if (active.terminal_done && !active.finalized) {
                finalize_terminal(active, now, remaining_frames, first_failure);
            }
        }
        // Global operation ceilings are shared by all sessions. Rotating the
        // first serviced slot prevents a continuously writable/readable PTY at
        // a low vector index from monopolizing every bounded cycle.
        service_cursor_ = (start + 1U) % session_count;
        return first_failure;
    }

    [[nodiscard]] const RatoxOutboundPacket *peek_outbound() const noexcept {
        if (outbound_count_ == 0U || outbound_slots_.empty()) return nullptr;
        return &outbound_slots_[outbound_head_];
    }

    [[nodiscard]] Status pop_outbound() {
        if (outbound_count_ == 0U || outbound_slots_.empty()) {
            return Status{ErrorCode::not_found,
                          "Ratox outbound queue is empty"};
        }
        RatoxOutboundPacket &packet = outbound_slots_[outbound_head_];
        outbound_bytes_ -= packet.size;
        clear_packet(packet);
        outbound_head_ = (outbound_head_ + 1U) % outbound_slots_.size();
        --outbound_count_;
        return Status::success();
    }

    [[nodiscard]] Status peer_offline(
        std::uint32_t friend_number,
        std::uint64_t online_epoch,
        TimePoint now) {
        (void)now;
        if (!configuration_status_.ok()) return configuration_status_;
        if (online_epoch == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox offline transition requires an online epoch"};
        }
        bool changed = false;
        const std::size_t outbound_before = outbound_count_;
        drop_outbound_route(friend_number, online_epoch);
        changed = outbound_count_ != outbound_before;
        for (ActiveSession &active : sessions_) {
            if (!active.route ||
                active.route->friend_number != friend_number ||
                active.route->online_epoch != online_epoch) {
                continue;
            }
            const RatoxPeerContext peer = peer_for(active);
            const AttachmentToken token = active.route->token;
            const Status detached = active.state->detach(token);
            if (!detached.ok() &&
                detached.code() != ErrorCode::unavailable) {
                return detached;
            }
            active.route.reset();
            append_event(
                RatoxServiceEventKind::peer_detached,
                ErrorCode::ok, peer, &active, FrameType::detach);
            changed = true;
        }

        const std::size_t replay_before = replay_.size();
        std::size_t released_replay_bytes = 0U;
        for (auto entry = replay_.begin(); entry != replay_.end();) {
            if (entry->friend_number != friend_number ||
                entry->online_epoch != online_epoch) {
                ++entry;
                continue;
            }
            released_replay_bytes += entry->budget_bytes;
            wipe_replay_entry(*entry);
            entry = replay_.erase(entry);
        }
        replay_bytes_ -= released_replay_bytes;
        changed = changed || replay_.size() != replay_before;

        const std::size_t sessions_before = sessions_.size();
        sessions_.erase(
            std::remove_if(
                sessions_.begin(), sessions_.end(),
                [friend_number, online_epoch](const ActiveSession &active) {
                    return active.finalized &&
                           active.authority_friend_number == friend_number &&
                           active.authority_online_epoch == online_epoch;
                }),
            sessions_.end());
        changed = changed || sessions_.size() != sessions_before;
        return changed
            ? Status::success()
            : Status{ErrorCode::not_found,
                     "Ratox online epoch has no attached session"};
    }

    [[nodiscard]] Status authority_revoked(
        std::uint32_t friend_number,
        std::uint64_t online_epoch,
        const PrincipalId &principal_id,
        TimePoint now) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (online_epoch == 0U || all_zero(principal_id)) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox authority revocation context is incomplete"};
        }
        bool changed = purge_replay_route(
            friend_number, online_epoch, principal_id);
        const std::size_t outbound_before = outbound_count_;
        drop_outbound_route(friend_number, online_epoch);
        changed = changed || outbound_count_ != outbound_before;
        Status first_failure = Status::success();
        for (ActiveSession &active : sessions_) {
            const auto snapshot = active.state->snapshot();
            if (snapshot.principal_id != principal_id || active.finalized ||
                active.authority_revoked ||
                active.authority_friend_number != friend_number ||
                active.authority_online_epoch != online_epoch) {
                continue;
            }
            const Status closing = revoke_session(
                active, friend_number, online_epoch, now);
            if (!closing.ok() && first_failure.ok()) first_failure = closing;
            changed = true;
        }
        if (!changed) {
            return Status{ErrorCode::not_found,
                          "Ratox authority context has no live session"};
        }
        return first_failure;
    }

    [[nodiscard]] Status principal_revoked(
        const PrincipalId &principal_id,
        TimePoint now) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (all_zero(principal_id)) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox principal revocation requires a durable principal"};
        }

        bool changed = purge_replay_principal(principal_id);
        const std::size_t outbound_before = outbound_count_;
        drop_outbound_principal(principal_id);
        changed = changed || outbound_count_ != outbound_before;
        Status first_failure = Status::success();
        for (ActiveSession &active : sessions_) {
            if (active.finalized || active.authority_revoked ||
                active.state->snapshot().principal_id != principal_id) {
                continue;
            }
            const RatoxPeerContext peer = peer_for(active);
            const Status closing = revoke_session(
                active, peer.friend_number, peer.online_epoch, now);
            if (!closing.ok() && first_failure.ok()) first_failure = closing;
            changed = true;
        }
        if (!changed) {
            return Status{ErrorCode::not_found,
                          "Ratox principal has no live session"};
        }
        return first_failure;
    }

    [[nodiscard]] std::vector<PrincipalId> live_principals() const {
        std::vector<PrincipalId> principals;
        principals.reserve(std::min(
            sessions_.size(),
            config_.directory.maximum_sessions_per_device));
        for (const ActiveSession &active : sessions_) {
            if (active.finalized || active.authority_revoked ||
                active.state == nullptr) {
                continue;
            }
            const PrincipalId principal_id =
                active.state->snapshot().principal_id;
            if (all_zero(principal_id) ||
                std::find(principals.begin(), principals.end(), principal_id) !=
                    principals.end()) {
                continue;
            }
            principals.push_back(principal_id);
        }
        return principals;
    }

    [[nodiscard]] Status shutdown(TimePoint now) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (!shutdown_started_) {
            shutdown_started_ = true;
            RatoxPeerContext peer;
            append_event(
                RatoxServiceEventKind::shutdown_started,
                ErrorCode::ok, peer, nullptr, FrameType::close);
        }
        Status first_failure = Status::success();
        for (ActiveSession &active : sessions_) {
            if (active.finalized || active.controller == nullptr) continue;
            const Status closing = start_closing(
                active, SessionCloseReason::daemon_shutdown,
                0U, now, false);
            if (!closing.ok() && first_failure.ok()) first_failure = closing;
        }
        return first_failure;
    }

    [[nodiscard]] RatoxServiceSnapshot snapshot() const noexcept {
        std::size_t running = 0U;
        std::size_t attached = 0U;
        std::size_t closing = 0U;
        std::size_t tombstones = 0U;
        for (const ActiveSession &active : sessions_) {
            if (active.controller != nullptr) ++running;
            if (active.route) ++attached;
            if (active.closing && !active.finalized) ++closing;
            if (active.finalized) ++tombstones;
        }
        std::size_t committed_replay = 0U;
        std::size_t pending_replay = 0U;
        for (const ReplayEntry &entry : replay_) {
            if (entry.pending) {
                ++pending_replay;
            } else {
                ++committed_replay;
            }
        }
        return RatoxServiceSnapshot{
            config_.enabled,
            configuration_status_.ok(),
            sessions_.size(),
            sessions_.size() - tombstones,
            tombstones,
            running,
            attached,
            closing,
            committed_replay,
            pending_replay,
            replay_bytes_,
            outbound_count_,
            outbound_bytes_,
            events_.size(),
            dropped_events_,
            config_.directory.maximum_sessions_per_device,
            config_.maximum_session_tombstones,
            config_.maximum_admission_replay_entries,
            config_.maximum_admission_replay_bytes,
            config_.maximum_outbound_packets,
            config_.maximum_outbound_bytes,
            sessions_.size() - tombstones <=
                config_.directory.maximum_sessions_per_device,
            tombstones <= config_.maximum_session_tombstones,
            replay_.size() <= config_.maximum_admission_replay_entries,
            replay_bytes_ <= config_.maximum_admission_replay_bytes,
            outbound_count_ <= config_.maximum_outbound_packets,
            outbound_bytes_ <= config_.maximum_outbound_bytes};
    }

    [[nodiscard]] std::span<const RatoxServiceEvent> events() const noexcept {
        return events_;
    }

    [[nodiscard]] std::vector<RatoxServiceEvent> drain_events() {
        std::vector<RatoxServiceEvent> drained;
        drained.swap(events_);
        if (configuration_status_.ok()) events_.reserve(config_.maximum_events);
        return drained;
    }

  private:
    struct Route {
        std::uint32_t friend_number{0U};
        std::uint64_t online_epoch{0U};
        AttachmentToken token{};
        std::uint64_t output_cursor{1U};
        bool input_ack_pending{false};
        // OUTPUT_ACK is cumulative and OutputHistory::acknowledge is
        // idempotent. Retain one exact high-water fence instead of consuming
        // the session's never-evicted control replay cache once per rendered
        // output. Tox lossless ordering plus the attachment generation makes
        // every older ACK stale; an exact repeat of the newest ACK is safe.
        std::uint64_t output_ack_message_id{0U};
        std::uint64_t output_acknowledgement{0U};
    };

    struct ActiveSession {
        SessionId session_id{};
        InteractiveSession *state{nullptr};
        std::unique_ptr<InteractiveSession> retained_state;
        std::unique_ptr<terminal::TerminalController> controller;
        std::optional<Route> route;
        std::uint32_t authority_friend_number{0U};
        std::uint64_t authority_online_epoch{0U};
        bool closing{false};
        bool close_signal_started{false};
        SessionCloseReason close_reason{SessionCloseReason::normal};
        std::uint64_t exit_correlation_id{0U};
        bool terminal_done{false};
        bool terminal_failed{false};
        std::optional<terminal::ProcessExit> final_exit;
        std::optional<TimePoint> exit_observed_at;
        bool exit_packet_queued{false};
        bool finalized{false};
        bool authority_revoked{false};
        // The receiver intentionally retains only one staged INPUT frame.
        // Preserve its protocol message ID alongside that frame so the later
        // whole-frame PTY commit event can be joined to the exact admission.
        std::uint64_t staged_input_message_id{0U};
    };

    struct ReplayEntry {
        std::uint32_t friend_number{0U};
        std::uint64_t online_epoch{0U};
        PrincipalId principal_id{};
        std::uint64_t message_id{0U};
        FrameType request_type{FrameType::open};
        std::size_t budget_bytes{0U};
        bool terminal_authority_required{true};
        bool pending{true};
        std::vector<std::uint8_t> request;
        std::vector<std::uint8_t> result;
    };

    static void wipe_replay_entry(ReplayEntry &entry) noexcept {
        security::secure_wipe(entry.request);
        security::secure_wipe(entry.result);
        entry.request.clear();
        entry.result.clear();
        entry = ReplayEntry{};
    }

    enum class ReplayAdmissionKind : std::uint8_t {
        execute,
        replay,
    };

    struct ReplayAdmission {
        ReplayAdmissionKind kind{ReplayAdmissionKind::execute};
        ReplayEntry *entry{nullptr};
    };

    [[nodiscard]] Status validate_config() const {
        if (config_.enabled && config_.session_incarnation == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox session incarnation zero is reserved"};
        }
        if (config_.directory.maximum_sessions_per_principal == 0U ||
            config_.directory.maximum_sessions_per_device == 0U ||
            config_.directory.maximum_sessions_per_principal >
                config_.directory.maximum_sessions_per_device ||
            config_.directory.maximum_sessions_per_device > 1024U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox session-directory bounds are invalid"};
        }
        if (config_.maximum_session_tombstones <
                config_.directory.maximum_sessions_per_device ||
            config_.maximum_session_tombstones > 4096U ||
            config_.directory.maximum_sessions_per_device >
                std::numeric_limits<std::size_t>::max() -
                    config_.maximum_session_tombstones) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox session tombstone bounds are invalid"};
        }
        if (config_.maximum_admission_replay_entries == 0U ||
            config_.maximum_admission_replay_entries > 4096U ||
            config_.maximum_admission_replay_bytes <
                kMaximumAdmissionReservationBytes ||
            config_.maximum_admission_replay_entries >
                std::numeric_limits<std::size_t>::max() /
                    kMaximumAdmissionReservationBytes ||
            config_.maximum_admission_replay_bytes >
                config_.maximum_admission_replay_entries *
                    kMaximumAdmissionReservationBytes ||
            config_.maximum_outbound_packets == 0U ||
            config_.maximum_outbound_packets > 4096U ||
            config_.maximum_outbound_bytes < kControlPacketBytes ||
            config_.maximum_outbound_bytes >
                config_.maximum_outbound_packets *
                    protocol::ratox::kMaximumPacketBytes ||
            config_.maximum_events == 0U ||
            config_.maximum_events > 4096U ||
            config_.maximum_input_write_operations == 0U ||
            config_.maximum_input_write_operations > 4096U ||
            config_.maximum_output_read_operations == 0U ||
            config_.maximum_output_read_operations > 4096U ||
            config_.maximum_output_frames == 0U ||
            config_.maximum_output_frames > 4096U ||
            config_.terminal_read_bytes == 0U ||
            config_.terminal_read_bytes > terminal::kMaximumTerminalIoChunk ||
            config_.exit_output_drain_timeout.count() <= 0 ||
            config_.exit_output_drain_timeout > std::chrono::seconds{30} ||
            config_.initial_outbound_message_id == 0U ||
            config_.initial_outbound_message_id ==
                std::numeric_limits<std::uint64_t>::max()) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox service resource or clock bounds are invalid"};
        }
        return Status::success();
    }

    [[nodiscard]] ActiveSession *find_session(const SessionId &session_id) {
        const auto found = std::find_if(
            sessions_.begin(), sessions_.end(),
            [&session_id](const ActiveSession &active) {
                return active.session_id == session_id;
            });
        return found == sessions_.end() ? nullptr : &*found;
    }

    [[nodiscard]] RatoxPeerContext peer_for(
        const ActiveSession &active) const {
        RatoxPeerContext peer;
        peer.friend_number = active.route
            ? active.route->friend_number
            : active.authority_friend_number;
        peer.online_epoch = active.route
            ? active.route->online_epoch
            : active.authority_online_epoch;
        peer.principal_id = active.state->snapshot().principal_id;
        peer.transcript_confirmed = true;
        peer.feature_negotiated = true;
        peer.terminal_authorized = true;
        return peer;
    }

    [[nodiscard]] Result<std::uint64_t> allocate_message_id() {
        if (next_message_id_ == 0U ||
            next_message_id_ == std::numeric_limits<std::uint64_t>::max()) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox outbound message IDs are exhausted"};
        }
        const std::uint64_t value = next_message_id_;
        ++next_message_id_;
        return value;
    }

    [[nodiscard]] bool can_queue(std::size_t size) const noexcept {
        return size >= protocol::ratox::kHeaderBytes &&
               size <= protocol::ratox::kMaximumPacketBytes &&
               outbound_count_ < outbound_slots_.size() &&
               outbound_bytes_ <= config_.maximum_outbound_bytes &&
               size <= config_.maximum_outbound_bytes - outbound_bytes_;
    }

    [[nodiscard]] Status enqueue_packet(RatoxOutboundPacket &&packet) {
        if (!can_queue(packet.size)) {
            clear_packet(packet);
            return Status{ErrorCode::resource_exhausted,
                          "Ratox outbound queue is backpressured"};
        }
        const std::size_t index =
            (outbound_head_ + outbound_count_) % outbound_slots_.size();
        outbound_slots_[index] = packet;
        outbound_bytes_ += outbound_slots_[index].size;
        ++outbound_count_;
        clear_packet(packet);
        return Status::success();
    }

    [[nodiscard]] Result<RatoxOutboundPacket> encode_packet(
        const RatoxPeerContext &peer, const Frame &frame,
        RatoxTrafficClass traffic_class,
        bool terminal_authority_required = true) const {
        RatoxOutboundPacket packet;
        packet.friend_number = peer.friend_number;
        packet.online_epoch = peer.online_epoch;
        packet.session_id = frame.session_id;
        packet.principal_id = frame.principal_id;
        packet.terminal_authority_required =
            terminal_authority_required;
        packet.generation = frame.generation;
        packet.type = frame.type;
        packet.traffic_class = traffic_class;
        packet.sequence = frame.sequence;
        packet.next_sequence = frame.type == FrameType::output
            ? frame.sequence + static_cast<std::uint64_t>(frame.payload.size())
            : frame.acknowledgement;
        auto encoded = protocol::ratox::encode_into(frame, packet.storage);
        if (!encoded.ok()) return encoded.status();
        packet.size = encoded.value();
        return packet;
    }

    [[nodiscard]] Status enqueue_frame(
        const RatoxPeerContext &peer, Frame &&frame,
        RatoxTrafficClass traffic_class) {
        const SessionId session_id = frame.session_id;
        const FrameType type = frame.type;
        auto packet = encode_packet(peer, frame, traffic_class);
        security::secure_wipe(frame.payload);
        frame.payload.clear();
        if (!packet.ok()) return packet.status();
        const Status queued = enqueue_packet(std::move(packet.value()));
        if (!queued.ok()) {
            append_event(
                RatoxServiceEventKind::outbound_backpressure,
                queued.code(), peer, find_session(session_id), type);
        }
        return queued;
    }

    [[nodiscard]] Status enqueue_encoded(
        const RatoxPeerContext &peer,
        std::span<const std::uint8_t> bytes,
        bool terminal_authority_required = true) {
        if (bytes.size() < protocol::ratox::kHeaderBytes ||
            bytes.size() > protocol::ratox::kMaximumPacketBytes) {
            return Status{ErrorCode::internal_error,
                          "retained Ratox result has an invalid size"};
        }
        RatoxOutboundPacket packet;
        packet.friend_number = peer.friend_number;
        packet.online_epoch = peer.online_epoch;
        packet.terminal_authority_required =
            terminal_authority_required;
        packet.type = static_cast<FrameType>(bytes[3U]);
        packet.traffic_class = traffic_for(packet.type);
        packet.size = bytes.size();
        std::copy_n(bytes.begin(), bytes.size(), packet.storage.begin());
        std::copy_n(bytes.begin() + 24U, packet.session_id.size(),
                    packet.session_id.begin());
        std::copy_n(bytes.begin() + 40U, packet.principal_id.size(),
                    packet.principal_id.begin());
        packet.generation = read_u64(bytes.subspan(96U, 8U));
        packet.sequence = read_u64(bytes.subspan(104U, 8U));
        const std::uint64_t ack = read_u64(bytes.subspan(112U, 8U));
        packet.next_sequence = packet.type == FrameType::output
            ? packet.sequence + static_cast<std::uint64_t>(
                  bytes.size() - protocol::ratox::kHeaderBytes)
            : ack;
        const SessionId session_id = packet.session_id;
        const FrameType type = packet.type;
        const Status queued = enqueue_packet(std::move(packet));
        if (!queued.ok()) {
            append_event(
                RatoxServiceEventKind::outbound_backpressure,
                queued.code(), peer, find_session(session_id), type);
        }
        return queued;
    }

    template <typename Predicate>
    void drop_outbound(Predicate predicate) {
        if (outbound_count_ == 0U) return;
        std::size_t kept = 0U;
        std::size_t kept_bytes = 0U;
        for (std::size_t offset = 0U; offset < outbound_count_; ++offset) {
            const std::size_t index =
                (outbound_head_ + offset) % outbound_slots_.size();
            RatoxOutboundPacket &packet = outbound_slots_[index];
            if (!predicate(packet)) {
                outbound_scratch_[kept] = packet;
                kept_bytes += packet.size;
                ++kept;
            }
            clear_packet(packet);
        }
        outbound_slots_.swap(outbound_scratch_);
        outbound_head_ = 0U;
        outbound_count_ = kept;
        outbound_bytes_ = kept_bytes;
        // The scratch vector now owns the old ring. Wipe every slot, not only
        // the previously active range, so queue compaction cannot retain
        // terminal bytes in inactive capacity until the service is destroyed.
        for (RatoxOutboundPacket &discarded : outbound_scratch_) {
            clear_packet(discarded);
        }
    }

    void drop_outbound_route(
        std::uint32_t friend_number, std::uint64_t online_epoch) {
        drop_outbound(
            [friend_number, online_epoch](const RatoxOutboundPacket &packet) {
                return packet.friend_number == friend_number &&
                       packet.online_epoch == online_epoch;
            });
    }

    void drop_outbound_session(const SessionId &session_id) {
        drop_outbound(
            [&session_id](const RatoxOutboundPacket &packet) {
                return packet.session_id == session_id;
            });
    }

    void drop_outbound_principal(const PrincipalId &principal_id) {
        drop_outbound(
            [&principal_id](const RatoxOutboundPacket &packet) {
                return packet.principal_id == principal_id;
            });
    }

    [[nodiscard]] bool purge_replay_route(
        std::uint32_t friend_number,
        std::uint64_t online_epoch,
        const PrincipalId &principal_id) {
        const std::size_t before = replay_.size();
        std::size_t released_bytes = 0U;
        for (auto entry = replay_.begin(); entry != replay_.end();) {
            if (entry->friend_number != friend_number ||
                entry->online_epoch != online_epoch ||
                entry->principal_id != principal_id) {
                ++entry;
                continue;
            }
            released_bytes += entry->budget_bytes;
            wipe_replay_entry(*entry);
            entry = replay_.erase(entry);
        }
        replay_bytes_ -= released_bytes;
        return replay_.size() != before;
    }

    [[nodiscard]] bool purge_replay_principal(
        const PrincipalId &principal_id) {
        const std::size_t before = replay_.size();
        std::size_t released_bytes = 0U;
        for (auto entry = replay_.begin(); entry != replay_.end();) {
            if (entry->principal_id != principal_id) {
                ++entry;
                continue;
            }
            released_bytes += entry->budget_bytes;
            wipe_replay_entry(*entry);
            entry = replay_.erase(entry);
        }
        replay_bytes_ -= released_bytes;
        return replay_.size() != before;
    }

    [[nodiscard]] Status revoke_session(
        ActiveSession &active,
        std::uint32_t friend_number,
        std::uint64_t online_epoch,
        TimePoint now) {
        RatoxPeerContext peer = peer_for(active);
        peer.friend_number = friend_number;
        peer.online_epoch = online_epoch;
        append_event(
            RatoxServiceEventKind::authority_revoked,
            ErrorCode::ok, peer, &active, FrameType::close);

        // Revocation is not a graceful transport close. Remove every retained
        // packet first, invalidate the routing handle, and only then begin the
        // local process shutdown. This prevents queued OUTPUT/INPUT_ACK bytes
        // or exact admission results from crossing the authority boundary.
        drop_outbound_session(active.session_id);
        active.route.reset();
        active.authority_revoked = true;
        active.closing = true;
        active.close_reason = SessionCloseReason::authority_revoked;
        active.exit_correlation_id = 0U;
        return start_closing(
            active, SessionCloseReason::authority_revoked,
            0U, now, false);
    }

    [[nodiscard]] Result<ReplayAdmission> reserve_replay(
        const RatoxPeerContext &peer, const Frame &frame,
        std::span<const std::uint8_t> request,
        std::size_t result_capacity) {
        const auto found = std::find_if(
            replay_.begin(), replay_.end(),
            [&peer, &frame](const ReplayEntry &entry) {
                return entry.friend_number == peer.friend_number &&
                       entry.online_epoch == peer.online_epoch &&
                       entry.message_id == frame.message_id;
            });
        if (found != replay_.end()) {
            if (found->request_type != frame.type ||
                found->request.size() != request.size() ||
                !std::equal(request.begin(), request.end(),
                            found->request.begin())) {
                return Status{ErrorCode::protocol_error,
                              "Ratox admission message ID was reused with different bytes"};
            }
            if (found->pending) {
                return Status{ErrorCode::unavailable,
                              "Ratox admission result is still in progress"};
            }
            return ReplayAdmission{ReplayAdmissionKind::replay, &*found};
        }
        if (replay_.size() >= config_.maximum_admission_replay_entries ||
            result_capacity > protocol::ratox::kMaximumPacketBytes) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox admission replay entry bound is exhausted"};
        }
        if (request.size() >
                std::numeric_limits<std::size_t>::max() - result_capacity) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox admission replay budget overflows"};
        }
        const std::size_t budget = request.size() + result_capacity;
        if (replay_bytes_ > config_.maximum_admission_replay_bytes ||
            budget > config_.maximum_admission_replay_bytes - replay_bytes_) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox admission replay byte bound is exhausted"};
        }

        ReplayEntry entry;
        entry.friend_number = peer.friend_number;
        entry.online_epoch = peer.online_epoch;
        entry.principal_id = peer.principal_id;
        entry.message_id = frame.message_id;
        entry.request_type = frame.type;
        entry.budget_bytes = budget;
        entry.request.assign(request.begin(), request.end());
        entry.result.reserve(result_capacity);
        replay_.push_back(std::move(entry));
        wipe_replay_entry(entry);
        replay_bytes_ += budget;
        return ReplayAdmission{
            ReplayAdmissionKind::execute, &replay_.back()};
    }

    [[nodiscard]] Status commit_replay(
        ReplayEntry &entry, std::span<const std::uint8_t> result,
        bool terminal_authority_required) {
        if (!entry.pending || result.size() > entry.result.capacity()) {
            return Status{ErrorCode::internal_error,
                          "Ratox admission replay reservation is invalid"};
        }
        const std::size_t retained = entry.request.size() + result.size();
        replay_bytes_ -= entry.budget_bytes;
        entry.result.assign(result.begin(), result.end());
        entry.budget_bytes = retained;
        entry.terminal_authority_required =
            terminal_authority_required;
        entry.pending = false;
        replay_bytes_ += retained;
        return Status::success();
    }

    void cancel_replay(ReplayEntry *entry) {
        if (entry == nullptr) return;
        const auto found = std::find_if(
            replay_.begin(), replay_.end(),
            [entry](const ReplayEntry &candidate) {
                return &candidate == entry;
            });
        if (found == replay_.end()) return;
        replay_bytes_ -= found->budget_bytes;
        wipe_replay_entry(*found);
        replay_.erase(found);
    }

    [[nodiscard]] Status handle_open(
        const RatoxPeerContext &peer, const Frame &request,
        std::span<const std::uint8_t> canonical, TimePoint now) {
        auto admission = reserve_replay(
            peer, request, canonical,
            protocol::ratox::kMaximumPacketBytes);
        if (!admission.ok()) {
            append_event(
                RatoxServiceEventKind::open_denied,
                admission.status().code(), peer, nullptr, request.type);
            return admission.status();
        }
        if (admission.value().kind == ReplayAdmissionKind::replay) {
            append_event(
                RatoxServiceEventKind::replayed,
                ErrorCode::ok, peer, find_session(request.session_id),
                request.type);
            return enqueue_encoded(
                peer, admission.value().entry->result,
                admission.value().entry->terminal_authority_required);
        }
        ReplayEntry &replay = *admission.value().entry;

        auto response_message = allocate_message_id();
        if (!response_message.ok()) {
            cancel_replay(&replay);
            return response_message.status();
        }
        Frame response;
        response.type = FrameType::open_result;
        response.message_id = response_message.value();
        response.correlation_id = request.message_id;
        response.session_id = request.session_id;
        response.principal_id = request.principal_id;
        response.attachment_nonce = request.attachment_nonce;
        response.payload.resize(12U, 0U);  // allocation precedes every effect

        std::uint16_t result = kResultSuccess;
        terminal::Dimensions accepted{
            read_u16(std::span<const std::uint8_t>{request.payload}.subspan(2U, 2U)),
            read_u16(std::span<const std::uint8_t>{request.payload}.subspan(4U, 2U))};
        InteractiveSession *opened_state = nullptr;
        std::unique_ptr<terminal::TerminalController> controller;
        SessionAttachmentResult attachment;

        if (!peer.terminal_authorized) {
            result = kResultDenied;
        } else if (!can_queue(kOpenResultPacketBytes)) {
            result = kResultResourceExhausted;
        } else if (find_session(request.session_id) != nullptr) {
            result = kResultInvalid;
        } else if (static_cast<std::size_t>(std::count_if(
                       sessions_.begin(), sessions_.end(),
                       [](const ActiveSession &active) {
                           return active.finalized;
                       })) >= config_.maximum_session_tombstones ||
                   sessions_.size() >=
                       config_.directory.maximum_sessions_per_device +
                           config_.maximum_session_tombstones) {
            result = kResultResourceExhausted;
        } else {
            auto profile = profiles_->resolve(
                peer.principal_id, accepted, ambient_environment_);
            if (!profile.ok()) {
                result = result_for_status(profile.status());
            } else {
                accepted = profile.value().accepted_dimensions;
                auto opened = directory_->open(
                    request.session_id, peer.principal_id,
                    request.attachment_nonce,
                    config_.session_incarnation);
                if (!opened.ok()) {
                    result = result_for_status(opened.status());
                } else {
                    opened_state = opened.value().session;
                    attachment = opened.value().attachment;
                    auto started = terminal::TerminalController::start(
                        *processes_, std::move(profile.value()));
                    if (!started.ok()) {
                        result = result_for_status(started.status());
                        static_cast<void>(opened_state->terminate(
                            SessionCloseReason::process_failure));
                        static_cast<void>(directory_->erase_closed(
                            request.session_id));
                        opened_state = nullptr;
                    } else {
                        controller = std::move(started.value());
                    }
                }
            }
        }

        write_u16(response.payload, result);
        if (result == kResultSuccess) {
            response.incarnation = attachment.token.incarnation;
            response.generation = attachment.token.generation;
            response.payload[2U] = 1U;
            response.payload[3U] = 0U;
            write_u16(
                std::span<std::uint8_t>{response.payload}.subspan(4U, 2U),
                accepted.columns);
            write_u16(
                std::span<std::uint8_t>{response.payload}.subspan(6U, 2U),
                accepted.rows);
        }

        auto packet = encode_packet(
            peer, response, RatoxTrafficClass::control,
            peer.terminal_authorized);
        if (!packet.ok()) {
            if (controller != nullptr && opened_state != nullptr) {
                controller.reset();
                static_cast<void>(opened_state->terminate(
                    SessionCloseReason::process_failure));
                static_cast<void>(directory_->erase_closed(request.session_id));
            }
            cancel_replay(&replay);
            return packet.status();
        }

        if (result == kResultSuccess) {
            ActiveSession active;
            active.session_id = request.session_id;
            active.state = opened_state;
            active.controller = std::move(controller);
            active.route = Route{
                peer.friend_number,
                peer.online_epoch,
                attachment.token,
                attachment.output_base_sequence,
                false,
                0U,
                0U};
            active.authority_friend_number = peer.friend_number;
            active.authority_online_epoch = peer.online_epoch;
            sessions_.push_back(std::move(active));
        }

        const Status committed = commit_replay(
            replay, packet.value().bytes(),
            packet.value().terminal_authority_required);
        if (!committed.ok()) {
            if (result == kResultSuccess) {
                ActiveSession &active = sessions_.back();
                active.controller.reset();
                static_cast<void>(active.state->terminate(
                    SessionCloseReason::process_failure));
                static_cast<void>(directory_->erase_closed(active.session_id));
                sessions_.pop_back();
            }
            return committed;
        }
        const Status queued = enqueue_packet(std::move(packet.value()));
        if (!queued.ok()) {
            append_event(
                RatoxServiceEventKind::outbound_backpressure,
                queued.code(), peer, find_session(request.session_id),
                response.type);
        }
        if (result == kResultSuccess) {
            append_event(
                RatoxServiceEventKind::opened,
                ErrorCode::ok, peer, find_session(request.session_id),
                request.type);
        } else {
            append_event(
                RatoxServiceEventKind::open_denied,
                error_for_result(result),
                peer, nullptr, request.type);
        }
        (void)now;
        return queued;
    }

    [[nodiscard]] Status handle_absent_attach(
        const RatoxPeerContext &peer, const Frame &request,
        std::span<const std::uint8_t> canonical,
        std::uint16_t result) {
        auto admission = reserve_replay(
            peer, request, canonical,
            protocol::ratox::kMaximumPacketBytes);
        if (!admission.ok()) {
            append_event(
                RatoxServiceEventKind::packet_rejected,
                admission.status().code(), peer, nullptr, request.type);
            return admission.status();
        }
        if (admission.value().kind == ReplayAdmissionKind::replay) {
            append_event(
                RatoxServiceEventKind::replayed,
                ErrorCode::ok, peer, nullptr, request.type);
            return enqueue_encoded(
                peer, admission.value().entry->result,
                admission.value().entry->terminal_authority_required);
        }
        ReplayEntry &replay = *admission.value().entry;

        auto response_message = allocate_message_id();
        if (!response_message.ok()) {
            cancel_replay(&replay);
            return response_message.status();
        }
        Frame response;
        response.type = request.type == FrameType::resume
            ? FrameType::resume_result
            : FrameType::attach_result;
        response.message_id = response_message.value();
        response.correlation_id = request.message_id;
        response.session_id = request.session_id;
        response.principal_id = request.principal_id;
        response.attachment_nonce = request.attachment_nonce;
        response.incarnation = request.incarnation;
        if (request.type == FrameType::resume) {
            response.generation = request.generation;
        }
        response.payload.resize(28U, 0U);
        write_u16(response.payload, result);

        auto packet = encode_packet(
            peer, response, RatoxTrafficClass::control,
            peer.terminal_authorized);
        if (!packet.ok()) {
            cancel_replay(&replay);
            return packet.status();
        }
        const Status committed = commit_replay(
            replay, packet.value().bytes(),
            packet.value().terminal_authority_required);
        if (!committed.ok()) return committed;
        const Status queued = enqueue_packet(std::move(packet.value()));
        if (!queued.ok()) {
            append_event(
                RatoxServiceEventKind::outbound_backpressure,
                queued.code(), peer, nullptr, response.type);
        }
        append_event(
            RatoxServiceEventKind::packet_rejected,
            error_for_result(result), peer, nullptr, request.type);
        return queued;
    }

    [[nodiscard]] Status handle_attach(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, std::span<const std::uint8_t> canonical,
        bool resume, TimePoint now) {
        auto admission = active.state->begin_control(
            request.message_id, canonical,
            protocol::ratox::kMaximumPacketBytes);
        if (!admission.ok()) return admission.status();
        if (admission.value().kind == MessageReplayAdmissionKind::replay) {
            append_event(
                RatoxServiceEventKind::replayed,
                ErrorCode::ok, peer, &active, request.type);
            return enqueue_encoded(peer, admission.value().result);
        }
        const MessageReplayReservation reservation =
            admission.value().reservation;

        auto response_message = allocate_message_id();
        if (!response_message.ok()) {
            static_cast<void>(active.state->cancel_control(reservation));
            return response_message.status();
        }
        Frame response;
        response.type = resume
            ? FrameType::resume_result
            : FrameType::attach_result;
        response.message_id = response_message.value();
        response.correlation_id = request.message_id;
        response.session_id = request.session_id;
        response.principal_id = request.principal_id;
        response.attachment_nonce = request.attachment_nonce;
        response.incarnation = request.incarnation;
        // RESUME is sent from a previously assigned generation, and even a
        // denied RESUME_RESULT remains attached to that generation. A success
        // replaces it below with the newly assigned generation.
        if (resume) response.generation = request.generation;
        response.payload.resize(28U, 0U);

        const auto snapshot = active.state->snapshot();
        const std::uint64_t controller_next_input =
            read_u64(std::span<const std::uint8_t>{request.payload}.first(8U));
        const std::uint64_t controller_next_output =
            read_u64(std::span<const std::uint8_t>{request.payload}.subspan(8U, 8U));
        std::uint16_t result = kResultSuccess;
        std::optional<SessionAttachmentResult> attached;

        if (!can_queue(kAttachResultPacketBytes)) {
            result = kResultResourceExhausted;
        } else if (active.controller == nullptr || active.terminal_done ||
                   active.closing || snapshot.lifecycle != SessionLifecycle::active) {
            result = kResultUnavailable;
        } else if (request.incarnation != snapshot.incarnation) {
            result = kResultNotFound;
        } else {
            auto attempted = resume
                ? active.state->resume(
                      peer.principal_id, request.attachment_nonce,
                      controller_next_input, controller_next_output)
                : active.state->attach(
                      peer.principal_id, request.attachment_nonce,
                      controller_next_input, controller_next_output);
            if (!attempted.ok()) {
                result = result_for_status(attempted.status());
            } else {
                attached = attempted.value();
            }
        }

        write_u16(response.payload, result);
        if (attached) {
            response.generation = attached->token.generation;
            write_u64(
                std::span<std::uint8_t>{response.payload}.subspan(4U, 8U),
                attached->next_input_sequence);
            write_u64(
                std::span<std::uint8_t>{response.payload}.subspan(12U, 8U),
                attached->output_base_sequence);
            write_u64(
                std::span<std::uint8_t>{response.payload}.subspan(20U, 8U),
                attached->output_next_sequence);
        }

        auto packet = encode_packet(peer, response, RatoxTrafficClass::control);
        if (!packet.ok()) {
            static_cast<void>(active.state->cancel_control(reservation));
            if (attached) {
                static_cast<void>(start_closing(
                    active, SessionCloseReason::process_failure,
                    0U, now, false));
            }
            return packet.status();
        }
        const Status committed = active.state->complete_control(
            reservation, packet.value().bytes());
        if (!committed.ok()) {
            if (attached) {
                static_cast<void>(start_closing(
                    active, SessionCloseReason::process_failure,
                    0U, now, false));
            }
            return committed;
        }

        if (attached) {
            drop_outbound_session(active.session_id);
            active.route = Route{
                peer.friend_number,
                peer.online_epoch,
                attached->token,
                attached->output_gap
                    ? attached->output_base_sequence
                    : controller_next_output,
                false,
                0U,
                0U};
            active.authority_friend_number = peer.friend_number;
            active.authority_online_epoch = peer.online_epoch;
        }
        const Status queued = enqueue_packet(std::move(packet.value()));
        if (!queued.ok()) return queued;
        append_event(
            attached
                ? (resume ? RatoxServiceEventKind::resumed
                          : RatoxServiceEventKind::attached)
                : RatoxServiceEventKind::packet_rejected,
            attached ? ErrorCode::ok : ErrorCode::unavailable,
            peer, &active, request.type);
        return Status::success();
    }

    [[nodiscard]] Result<MessageReplayAdmission> begin_empty_control(
        ActiveSession &active, const Frame &request,
        std::span<const std::uint8_t> canonical) {
        return active.state->begin_control(
            request.message_id, canonical, 0U);
    }

    [[nodiscard]] Status replay_empty_or_continue(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, const MessageReplayAdmission &admission) {
        if (admission.kind != MessageReplayAdmissionKind::replay) {
            return Status{ErrorCode::internal_error,
                          "Ratox empty-control replay helper received an execution admission"};
        }
        if (!admission.result.empty()) {
            return enqueue_encoded(peer, admission.result);
        }
        append_event(
            RatoxServiceEventKind::replayed,
            ErrorCode::ok, peer, &active, request.type);
        return Status::success();
    }

    [[nodiscard]] Status validate_route(
        const RatoxPeerContext &peer, const ActiveSession &active,
        const Frame &frame) const {
        if (!active.route) {
            return Status{ErrorCode::unavailable,
                          "Ratox session has no attached controller"};
        }
        const Route &route = *active.route;
        if (route.friend_number != peer.friend_number ||
            route.online_epoch != peer.online_epoch ||
            route.token.session_id != frame.session_id ||
            route.token.principal_id != frame.principal_id ||
            route.token.nonce != frame.attachment_nonce ||
            route.token.incarnation != frame.incarnation ||
            route.token.generation != frame.generation) {
            return Status{ErrorCode::protocol_error,
                          "Ratox frame is fenced by attachment routing identity"};
        }
        return active.state->validate_attachment(route.token);
    }

    [[nodiscard]] Status handle_detach(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, std::span<const std::uint8_t> canonical,
        TimePoint now) {
        auto admission = begin_empty_control(active, request, canonical);
        if (!admission.ok()) return admission.status();
        if (admission.value().kind == MessageReplayAdmissionKind::replay) {
            return replay_empty_or_continue(
                peer, active, request, admission.value());
        }
        const Status route = validate_route(peer, active, request);
        if (!route.ok()) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return route;
        }
        const AttachmentToken token = active.route->token;
        const Status detached = active.state->detach(token);
        if (!detached.ok()) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return detached;
        }
        const Status committed = active.state->complete_control(
            admission.value().reservation, {});
        if (!committed.ok()) {
            return start_closing(
                active, SessionCloseReason::process_failure,
                0U, now, false);
        }
        drop_outbound_route(peer.friend_number, peer.online_epoch);
        active.route.reset();
        append_event(
            RatoxServiceEventKind::detached,
            ErrorCode::ok, peer, &active, request.type);
        return Status::success();
    }

    [[nodiscard]] Status handle_output_ack(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, std::span<const std::uint8_t> canonical) {
        const Status route = validate_route(peer, active, request);
        if (!route.ok()) return route;

        // Preserve message-ID conflict detection against retained exact
        // controls. OUTPUT_ACK itself is stream-coordinate state, like INPUT,
        // and therefore uses the constant-space route fence below instead of
        // the finite never-evicted side-effect replay cache.
        auto retained = active.state->lookup_control_result(
            request.message_id, canonical);
        if (retained.ok()) {
            return Status{ErrorCode::protocol_error,
                          "Ratox OUTPUT_ACK reused an exact-control message ID"};
        }
        if (retained.status().code() != ErrorCode::not_found) {
            return retained.status();
        }

        Route &current = *active.route;
        if (current.output_ack_message_id != 0U) {
            if (request.message_id == current.output_ack_message_id) {
                return request.acknowledgement ==
                        current.output_acknowledgement
                    ? Status::success()
                    : Status{ErrorCode::protocol_error,
                             "Ratox OUTPUT_ACK message ID was reused with a different acknowledgement"};
            }
            if (request.message_id < current.output_ack_message_id) {
                return Status{ErrorCode::protocol_error,
                              "Ratox OUTPUT_ACK message ID moved backwards"};
            }
            if (request.acknowledgement <=
                current.output_acknowledgement) {
                return Status{ErrorCode::protocol_error,
                              "Ratox OUTPUT_ACK high-water mark did not advance"};
            }
        }
        const Status acknowledged = acknowledge_output(
            active, request.acknowledgement);
        if (!acknowledged.ok()) return acknowledged;
        current.output_ack_message_id = request.message_id;
        current.output_acknowledgement = request.acknowledgement;
        return Status::success();
    }

    [[nodiscard]] Status acknowledge_output(
        ActiveSession &active, std::uint64_t acknowledgment) {
        if (!active.route) {
            return Status{ErrorCode::unavailable,
                          "Ratox output acknowledgement has no attachment"};
        }
        const Status acknowledged = active.state->acknowledge_output(
            active.route->token, acknowledgment);
        if (!acknowledged.ok()) return acknowledged;
        drop_outbound(
            [&active, acknowledgment](const RatoxOutboundPacket &packet) {
                const bool output_record =
                    packet.type == FrameType::output ||
                    packet.type == FrameType::output_gap;
                return packet.session_id == active.session_id &&
                       output_record && packet.next_sequence != 0U &&
                       packet.next_sequence <= acknowledgment;
            });
        return Status::success();
    }

    [[nodiscard]] Status handle_resize(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, std::span<const std::uint8_t> canonical) {
        auto admission = begin_empty_control(active, request, canonical);
        if (!admission.ok()) return admission.status();
        if (admission.value().kind == MessageReplayAdmissionKind::replay) {
            return replay_empty_or_continue(
                peer, active, request, admission.value());
        }
        const Status route = validate_route(peer, active, request);
        if (!route.ok() || active.closing || active.controller == nullptr) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return route.ok()
                ? Status{ErrorCode::unavailable,
                         "Ratox terminal is closing"}
                : route;
        }
        terminal::Dimensions dimensions{
            read_u16(std::span<const std::uint8_t>{request.payload}.first(2U)),
            read_u16(std::span<const std::uint8_t>{request.payload}.subspan(2U, 2U))};
        auto resized = active.controller->resize(dimensions);
        if (!resized.ok()) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return resized.status();
        }
        const Status committed = active.state->complete_control(
            admission.value().reservation, {});
        if (!committed.ok()) return committed;
        append_event(
            RatoxServiceEventKind::resize_applied,
            ErrorCode::ok, peer, &active, request.type);
        return Status::success();
    }

    [[nodiscard]] Status handle_ping(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, std::span<const std::uint8_t> canonical) {
        auto admission = active.state->begin_control(
            request.message_id, canonical,
            protocol::ratox::kMaximumPacketBytes);
        if (!admission.ok()) return admission.status();
        if (admission.value().kind == MessageReplayAdmissionKind::replay) {
            return enqueue_encoded(peer, admission.value().result);
        }
        const Status route = validate_route(peer, active, request);
        if (!route.ok()) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return route;
        }
        auto message_id = allocate_message_id();
        if (!message_id.ok()) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return message_id.status();
        }
        Frame response;
        response.type = FrameType::pong;
        response.message_id = message_id.value();
        response.correlation_id = request.message_id;
        response.session_id = request.session_id;
        response.principal_id = request.principal_id;
        response.attachment_nonce = request.attachment_nonce;
        response.incarnation = request.incarnation;
        response.generation = request.generation;
        auto packet = encode_packet(peer, response, RatoxTrafficClass::control);
        if (!packet.ok()) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return packet.status();
        }
        const Status committed = active.state->complete_control(
            admission.value().reservation, packet.value().bytes());
        if (!committed.ok()) return committed;
        return enqueue_packet(std::move(packet.value()));
    }

    [[nodiscard]] Status handle_close(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, std::span<const std::uint8_t> canonical,
        TimePoint now) {
        auto admission = begin_empty_control(active, request, canonical);
        if (!admission.ok()) return admission.status();
        if (admission.value().kind == MessageReplayAdmissionKind::replay) {
            return replay_empty_or_continue(
                peer, active, request, admission.value());
        }
        const Status route = validate_route(peer, active, request);
        if (!route.ok()) {
            static_cast<void>(active.state->cancel_control(
                admission.value().reservation));
            return route;
        }
        const SessionCloseReason reason = close_reason_from_wire(
            read_u16(request.payload));
        const Status closing = start_closing(
            active, reason, request.message_id, now, true);
        const Status committed = active.state->complete_control(
            admission.value().reservation, {});
        if (!committed.ok()) return committed;
        append_event(
            RatoxServiceEventKind::close_started,
            closing.code(), peer, &active, request.type);
        return closing;
    }

    [[nodiscard]] Status handle_input(
        const RatoxPeerContext &peer, ActiveSession &active,
        const Frame &request, TimePoint now) {
        const Status route = validate_route(peer, active, request);
        if (!route.ok()) {
            append_event(
                RatoxServiceEventKind::input_rejected,
                route.code(), peer, &active, request.type,
                request.message_id, request.sequence,
                frame_next_sequence(request),
                request.payload.size());
            return route;
        }
        if (active.closing || active.controller == nullptr ||
            active.terminal_done) {
            const Status unavailable{
                ErrorCode::unavailable,
                "Ratox input is fenced once terminal shutdown begins"};
            append_event(
                RatoxServiceEventKind::input_rejected,
                unavailable.code(), peer, &active, request.type,
                request.message_id, request.sequence,
                frame_next_sequence(request),
                request.payload.size());
            return unavailable;
        }
        if (request.acknowledgement != 0U) {
            const Status acknowledged = acknowledge_output(
                active, request.acknowledgement);
            if (!acknowledged.ok()) return acknowledged;
        }
        auto offered = active.state->offer_input(
            active.route->token, request.sequence, request.payload);
        if (!offered.ok()) {
            append_event(
                RatoxServiceEventKind::input_rejected,
                offered.status().code(), peer, &active, request.type,
                request.message_id, request.sequence,
                frame_next_sequence(request),
                request.payload.size());
            if (offered.status().code() == ErrorCode::protocol_error) {
                queue_close_notice(
                    active, SessionCloseReason::protocol_violation);
                static_cast<void>(start_closing(
                    active, SessionCloseReason::protocol_violation,
                    0U, now, false));
            }
            return offered.status();
        }
        if (offered.value().disposition == InputDisposition::staged) {
            active.staged_input_message_id = request.message_id;
            append_event(
                RatoxServiceEventKind::input_staged,
                ErrorCode::ok, peer, &active, request.type,
                request.message_id, request.sequence,
                frame_next_sequence(request),
                request.payload.size());
        } else {
            active.route->input_ack_pending = true;
        }
        return Status::success();
    }

    [[nodiscard]] Status start_closing(
        ActiveSession &active, SessionCloseReason reason,
        std::uint64_t correlation_id, TimePoint now,
        bool drain_admitted_input) {
        if (active.finalized) return Status::success();
        if (!active.closing) {
            active.closing = true;
            active.close_reason = reason;
            active.exit_correlation_id = correlation_id;
        }
        if (active.controller == nullptr || active.terminal_done) {
            return Status::success();
        }
        const auto input = active.state->snapshot().input;
        if (input.staged_bytes != 0U && !drain_admitted_input) {
            static_cast<void>(active.state->fail_input());
            active.terminal_failed = true;
            active.terminal_done = true;
            active.controller.reset();
            return Status{ErrorCode::unavailable,
                          "Ratox staged input was fenced by terminal shutdown"};
        }
        if (input.staged_bytes != 0U) {
            return Status::success();
        }
        return ensure_close_signal(active, now);
    }

    [[nodiscard]] Status ensure_close_signal(
        ActiveSession &active, TimePoint now) {
        if (!active.closing || active.close_signal_started ||
            active.controller == nullptr || active.terminal_done) {
            return Status::success();
        }
        const Status closed = active.controller->request_close(
            terminal_close_reason(active.close_reason), now);
        active.close_signal_started = closed.ok();
        return closed;
    }

    void queue_close_notice(
        ActiveSession &active, SessionCloseReason reason) {
        if (!active.route || !can_queue(
                protocol::ratox::kHeaderBytes + 2U)) {
            return;
        }
        auto message_id = allocate_message_id();
        if (!message_id.ok()) return;
        Frame frame = attached_frame(active, FrameType::close);
        frame.message_id = message_id.value();
        const std::uint16_t encoded_reason = wire_close_reason(reason);
        frame.payload = {
            static_cast<std::uint8_t>(encoded_reason & 0xffU),
            static_cast<std::uint8_t>((encoded_reason >> 8U) & 0xffU),
        };
        const RatoxPeerContext peer = peer_for(active);
        static_cast<void>(enqueue_frame(
            peer, std::move(frame), RatoxTrafficClass::control));
    }

    [[nodiscard]] Frame attached_frame(
        const ActiveSession &active, FrameType type) const {
        Frame frame;
        frame.type = type;
        frame.session_id = active.session_id;
        if (active.route) {
            frame.principal_id = active.route->token.principal_id;
            frame.attachment_nonce = active.route->token.nonce;
            frame.incarnation = active.route->token.incarnation;
            frame.generation = active.route->token.generation;
        } else {
            const auto snapshot = active.state->snapshot();
            frame.principal_id = snapshot.principal_id;
        }
        return frame;
    }

    void service_process(
        ActiveSession &active, TimePoint now,
        std::size_t &remaining_writes,
        std::size_t &remaining_reads,
        Status &first_failure) {
        if (active.controller == nullptr) return;

        while (remaining_writes != 0U) {
            const auto input_before = active.state->snapshot().input;
            auto pending = active.state->pending_input();
            if (!pending.ok() || pending.value().empty()) break;
            ScopedByteWipe pending_wipe{pending.value()};
            --remaining_writes;
            auto written = active.controller->write_input(pending.value());
            if (!written.ok()) {
                static_cast<void>(active.state->fail_input());
                mark_terminal_failure(active, written.status());
                if (first_failure.ok()) first_failure = written.status();
                break;
            }
            if (written.value().disposition == terminal::IoDisposition::would_block) {
                break;
            }
            auto consumed = active.state->consume_input(written.value().bytes);
            if (!consumed.ok()) {
                mark_terminal_failure(active, consumed.status());
                if (first_failure.ok()) first_failure = consumed.status();
                break;
            }
            if (consumed.value().committed) {
                if (active.route) active.route->input_ack_pending = true;
                append_event(
                    RatoxServiceEventKind::input_committed,
                    ErrorCode::ok, peer_for(active), &active,
                    FrameType::input, active.staged_input_message_id,
                    input_before.staged_sequence,
                    consumed.value().acknowledgement,
                    input_before.staged_bytes);
                active.staged_input_message_id = 0U;
                if (active.closing) {
                    const Status signaled = ensure_close_signal(active, now);
                    if (!signaled.ok() && first_failure.ok()) {
                        first_failure = signaled;
                    }
                }
            }
        }

        if (active.controller == nullptr || active.terminal_done) return;
        const Status polled = active.controller->poll(now);
        if (!polled.ok()) {
            mark_terminal_failure(active, polled);
            if (first_failure.ok()) first_failure = polled;
            return;
        }

        while (remaining_reads != 0U && active.controller != nullptr) {
            --remaining_reads;
            auto read = active.controller->read_output(
                config_.terminal_read_bytes);
            if (!read.ok()) {
                mark_terminal_failure(active, read.status());
                if (first_failure.ok()) first_failure = read.status();
                return;
            }
            ScopedByteWipe read_wipe{read.value().bytes};
            if (read.value().disposition == terminal::IoDisposition::would_block) {
                break;
            }
            if (read.value().disposition == terminal::IoDisposition::closed) {
                break;
            }
            auto appended = active.state->append_output(read.value().bytes);
            if (!appended.ok()) {
                mark_terminal_failure(active, appended.status());
                if (first_failure.ok()) first_failure = appended.status();
                return;
            }
            const auto output_after = active.state->snapshot().output;
            append_event(
                RatoxServiceEventKind::output_appended,
                ErrorCode::ok, peer_for(active), &active,
                FrameType::output, 0U, appended.value(),
                output_after.next_sequence,
                static_cast<std::uint64_t>(read.value().bytes.size()));
        }

        if (active.controller == nullptr || active.terminal_done) return;
        const auto snapshot = active.controller->snapshot();
        if (snapshot.phase == terminal::ControllerPhase::failed) {
            const Status failed{
                snapshot.error_code,
                snapshot.error_message.empty()
                    ? "Ratox terminal controller failed"
                    : snapshot.error_message};
            mark_terminal_failure(active, failed);
            if (first_failure.ok()) first_failure = failed;
            return;
        }
        if (snapshot.phase == terminal::ControllerPhase::exited) {
            if (!active.closing) {
                active.closing = true;
                active.close_reason = SessionCloseReason::normal;
            }
            if (!active.exit_observed_at) active.exit_observed_at = now;
            if (snapshot.output_closed ||
                now - *active.exit_observed_at >=
                    config_.exit_output_drain_timeout) {
                active.final_exit = snapshot.exit;
                active.terminal_done = true;
                active.controller.reset();
                append_event(
                    RatoxServiceEventKind::process_exited,
                    ErrorCode::ok, peer_for(active), &active,
                    FrameType::exit_status);
            }
        }
    }

    void mark_terminal_failure(
        ActiveSession &active, const Status &failure) {
        active.terminal_failed = true;
        active.terminal_done = true;
        active.closing = true;
        active.close_reason = SessionCloseReason::process_failure;
        active.controller.reset();
        append_event(
            RatoxServiceEventKind::process_failed,
            failure.code(), peer_for(active), &active,
            FrameType::exit_status);
    }

    void emit_pending_input_ack(ActiveSession &active) {
        if (!active.route || !active.route->input_ack_pending ||
            !can_queue(kControlPacketBytes)) {
            return;
        }
        auto message_id = allocate_message_id();
        if (!message_id.ok()) return;
        Frame ack = attached_frame(active, FrameType::input_ack);
        ack.message_id = message_id.value();
        ack.acknowledgement =
            active.state->snapshot().input.next_expected_sequence;
        const Status queued = enqueue_frame(
            peer_for(active), std::move(ack), RatoxTrafficClass::interactive);
        if (queued.ok()) active.route->input_ack_pending = false;
    }

    void emit_output(
        ActiveSession &active, std::size_t &remaining_frames) {
        if (!active.route || remaining_frames == 0U) return;
        while (remaining_frames != 0U && active.route) {
            auto output = active.state->read_output(
                active.route->token, active.route->output_cursor,
                protocol::ratox::kMaximumPayloadBytes);
            if (!output.ok()) return;
            if (output.value().kind == OutputReadKind::gap) {
                if (!can_queue(kControlPacketBytes)) return;
                auto message_id = allocate_message_id();
                if (!message_id.ok()) return;
                Frame gap = attached_frame(active, FrameType::output_gap);
                gap.message_id = message_id.value();
                gap.sequence = output.value().first_sequence;
                gap.acknowledgement = output.value().produced_next_sequence;
                const Status queued = enqueue_frame(
                    peer_for(active), std::move(gap),
                    RatoxTrafficClass::control);
                if (!queued.ok()) return;
                active.route->output_cursor = output.value().first_sequence;
                --remaining_frames;
                append_event(
                    RatoxServiceEventKind::output_gap,
                    ErrorCode::ok, peer_for(active), &active,
                    FrameType::output_gap);
                continue;
            }
            if (output.value().bytes.empty()) return;
            const std::size_t packet_bytes =
                protocol::ratox::kHeaderBytes + output.value().bytes.size();
            if (!can_queue(packet_bytes)) return;
            auto message_id = allocate_message_id();
            if (!message_id.ok()) return;
            Frame frame = attached_frame(active, FrameType::output);
            frame.message_id = message_id.value();
            frame.sequence = output.value().first_sequence;
            frame.acknowledgement =
                active.state->snapshot().input.next_expected_sequence;
            frame.payload = std::move(output.value().bytes);
            const Status queued = enqueue_frame(
                peer_for(active), std::move(frame),
                RatoxTrafficClass::interactive);
            if (!queued.ok()) return;
            active.route->output_cursor = output.value().next_sequence;
            --remaining_frames;
        }
    }

    void finalize_terminal(
        ActiveSession &active, TimePoint now,
        std::size_t &remaining_frames,
        Status &first_failure) {
        (void)now;
        if (active.route) {
            emit_output(active, remaining_frames);
            const auto output = active.state->snapshot().output;
            if (active.route->output_cursor < output.next_sequence) return;
            if (!active.exit_packet_queued) {
                if (!can_queue(kExitPacketBytes)) return;
                auto message_id = allocate_message_id();
                if (!message_id.ok()) {
                    if (first_failure.ok()) first_failure = message_id.status();
                    return;
                }
                Frame exit = attached_frame(active, FrameType::exit_status);
                exit.message_id = message_id.value();
                exit.correlation_id = active.exit_correlation_id;
                exit.payload.resize(8U, 0U);
                if (active.final_exit) {
                    if (active.final_exit->kind == terminal::ExitKind::exited) {
                        exit.payload[0U] = 0U;
                        write_u32(
                            std::span<std::uint8_t>{exit.payload}.subspan(4U, 4U),
                            static_cast<std::uint32_t>(active.final_exit->value));
                    } else {
                        exit.payload[0U] = 1U;
                        exit.payload[1U] = active.final_exit->core_dumped ? 1U : 0U;
                        write_u16(
                            std::span<std::uint8_t>{exit.payload}.subspan(2U, 2U),
                            static_cast<std::uint16_t>(active.final_exit->value));
                    }
                } else {
                    exit.payload[0U] = 2U;
                }
                const Status queued = enqueue_frame(
                    peer_for(active), std::move(exit),
                    RatoxTrafficClass::control);
                if (!queued.ok()) {
                    if (first_failure.ok()) first_failure = queued;
                    return;
                }
                active.exit_packet_queued = true;
            }
        }

        Status closed = Status::success();
        const auto lifecycle = active.state->snapshot().lifecycle;
        if (lifecycle != SessionLifecycle::closed) {
            if (active.route && lifecycle == SessionLifecycle::active &&
                static_cast<std::uint16_t>(active.close_reason) <= 4U) {
                closed = active.state->close(
                    active.route->token, active.close_reason);
            } else {
                closed = active.state->terminate(active.close_reason);
            }
        }
        if (!closed.ok() && closed.code() != ErrorCode::unavailable &&
            first_failure.ok()) {
            first_failure = closed;
        }
        active.route.reset();
        auto retained = directory_->release_closed(active.session_id);
        if (!retained.ok()) {
            if (first_failure.ok()) first_failure = retained.status();
        } else {
            active.retained_state = std::move(retained.value());
            active.state = active.retained_state.get();
        }
        active.finalized = true;
        append_event(
            RatoxServiceEventKind::session_finalized,
            closed.ok() ? ErrorCode::ok : closed.code(),
            peer_for(active), &active, FrameType::exit_status);
    }

    void append_event(
        RatoxServiceEventKind kind, ErrorCode error_code,
        const RatoxPeerContext &peer, const ActiveSession *active,
        FrameType frame_type, std::uint64_t message_id = 0U,
        std::uint64_t sequence = 0U,
        std::uint64_t next_sequence = 0U,
        std::uint64_t event_bytes = 0U) {
        if (config_.maximum_events == 0U || next_event_ordinal_ == 0U) return;
        RatoxServiceEvent event;
        event.ordinal = next_event_ordinal_;
        const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
            Clock::now() - event_clock_origin_).count();
        const auto candidate = elapsed < 0
            ? 1U
            : static_cast<std::uint64_t>(elapsed) + 1U;
        event.steady_time_us = std::max(candidate, last_event_steady_time_us_);
        last_event_steady_time_us_ = event.steady_time_us;
        event.kind = kind;
        event.error_code = error_code;
        event.friend_number = peer.friend_number;
        event.online_epoch = peer.online_epoch;
        event.principal_id = peer.principal_id;
        event.frame_type = frame_type;
        event.message_id = message_id;
        event.sequence = sequence;
        event.next_sequence = next_sequence;
        event.event_bytes = event_bytes;
        if (active != nullptr && active->state != nullptr) {
            const auto snapshot = active->state->snapshot();
            event.session_id = snapshot.session_id;
            event.principal_id = snapshot.principal_id;
            event.incarnation = snapshot.incarnation;
            event.generation = snapshot.generation;
            event.next_input_sequence = snapshot.input.next_expected_sequence;
            event.output_base_sequence = snapshot.output.base_sequence;
            event.output_next_sequence = snapshot.output.next_sequence;
        }
        if (events_.size() == config_.maximum_events) {
            std::move(events_.begin() + 1, events_.end(), events_.begin());
            events_.back() = event;
            if (dropped_events_ != std::numeric_limits<std::size_t>::max()) {
                ++dropped_events_;
            }
        } else {
            events_.push_back(event);
        }
        if (next_event_ordinal_ == std::numeric_limits<std::uint64_t>::max()) {
            next_event_ordinal_ = 0U;
        } else {
            ++next_event_ordinal_;
        }
    }

    [[nodiscard]] static std::uint64_t frame_next_sequence(
        const Frame &frame) noexcept {
        const auto bytes = static_cast<std::uint64_t>(frame.payload.size());
        if (bytes > std::numeric_limits<std::uint64_t>::max() - frame.sequence) {
            return 0U;
        }
        return frame.sequence + bytes;
    }

    terminal::ProfileRegistry *profiles_{nullptr};
    terminal::PtyProcessFactory *processes_{nullptr};
    Config config_;
    std::vector<terminal::EnvironmentEntry> ambient_environment_;
    Status configuration_status_{};
    std::unique_ptr<SessionDirectory> directory_;
    std::vector<ActiveSession> sessions_;
    std::size_t service_cursor_{0U};
    std::vector<ReplayEntry> replay_;
    std::size_t replay_bytes_{0U};
    std::vector<RatoxOutboundPacket> outbound_slots_;
    std::vector<RatoxOutboundPacket> outbound_scratch_;
    std::size_t outbound_head_{0U};
    std::size_t outbound_count_{0U};
    std::size_t outbound_bytes_{0U};
    std::vector<RatoxServiceEvent> events_;
    std::size_t dropped_events_{0U};
    std::uint64_t next_event_ordinal_{1U};
    TimePoint event_clock_origin_{Clock::now()};
    std::uint64_t last_event_steady_time_us_{0U};
    std::uint64_t next_message_id_{1U};
    bool shutdown_started_{false};
};

RatoxService::RatoxService(
    terminal::ProfileRegistry &profiles,
    terminal::PtyProcessFactory &processes)
    : RatoxService(profiles, processes, Config{}, {}) {}

RatoxService::RatoxService(
    terminal::ProfileRegistry &profiles,
    terminal::PtyProcessFactory &processes,
    Config config,
    std::vector<terminal::EnvironmentEntry> ambient_environment)
    : impl_(std::make_unique<Impl>(
          profiles, processes, config, std::move(ambient_environment))) {}

RatoxService::~RatoxService() = default;

Status RatoxService::receive(
    const RatoxPeerContext &peer,
    std::span<const std::uint8_t> packet,
    TimePoint now) {
    return impl_->receive(peer, packet, now);
}

Status RatoxService::service(TimePoint now) {
    return impl_->service(now);
}

const RatoxOutboundPacket *RatoxService::peek_outbound() const noexcept {
    return impl_->peek_outbound();
}

Status RatoxService::pop_outbound() {
    return impl_->pop_outbound();
}

Status RatoxService::peer_offline(
    std::uint32_t friend_number,
    std::uint64_t online_epoch,
    TimePoint now) {
    return impl_->peer_offline(friend_number, online_epoch, now);
}

Status RatoxService::authority_revoked(
    std::uint32_t friend_number,
    std::uint64_t online_epoch,
    const PrincipalId &principal_id,
    TimePoint now) {
    return impl_->authority_revoked(
        friend_number, online_epoch, principal_id, now);
}

Status RatoxService::principal_revoked(
    const PrincipalId &principal_id,
    TimePoint now) {
    return impl_->principal_revoked(principal_id, now);
}

std::vector<PrincipalId> RatoxService::live_principals() const {
    return impl_->live_principals();
}

Status RatoxService::shutdown(TimePoint now) {
    return impl_->shutdown(now);
}

RatoxServiceSnapshot RatoxService::snapshot() const noexcept {
    return impl_->snapshot();
}

std::span<const RatoxServiceEvent> RatoxService::events() const noexcept {
    return impl_->events();
}

std::vector<RatoxServiceEvent> RatoxService::drain_events() {
    return impl_->drain_events();
}

std::string_view to_string(RatoxServiceEventKind value) noexcept {
    switch (value) {
        case RatoxServiceEventKind::packet_rejected: return "packet-rejected";
        case RatoxServiceEventKind::open_denied: return "open-denied";
        case RatoxServiceEventKind::opened: return "opened";
        case RatoxServiceEventKind::attached: return "attached";
        case RatoxServiceEventKind::resumed: return "resumed";
        case RatoxServiceEventKind::detached: return "detached";
        case RatoxServiceEventKind::input_staged: return "input-staged";
        case RatoxServiceEventKind::input_committed: return "input-committed";
        case RatoxServiceEventKind::input_rejected: return "input-rejected";
        case RatoxServiceEventKind::output_appended: return "output-appended";
        case RatoxServiceEventKind::output_gap: return "output-gap";
        case RatoxServiceEventKind::resize_applied: return "resize-applied";
        case RatoxServiceEventKind::peer_detached: return "peer-detached";
        case RatoxServiceEventKind::authority_revoked: return "authority-revoked";
        case RatoxServiceEventKind::close_started: return "close-started";
        case RatoxServiceEventKind::process_exited: return "process-exited";
        case RatoxServiceEventKind::process_failed: return "process-failed";
        case RatoxServiceEventKind::session_finalized: return "session-finalized";
        case RatoxServiceEventKind::replayed: return "replayed";
        case RatoxServiceEventKind::outbound_backpressure: return "outbound-backpressure";
        case RatoxServiceEventKind::shutdown_started: return "shutdown-started";
    }
    return "unknown";
}

}  // namespace iotox::interactive
