#include "iotox/interactive_client.hpp"

#include "iotox/security/sodium.hpp"

#include <algorithm>
#include <limits>
#include <memory>
#include <optional>
#include <utility>

namespace iotox::interactive {
namespace {

using protocol::ratox::Frame;
using protocol::ratox::FrameType;

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

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

std::uint32_t read_u32(std::span<const std::uint8_t> input) {
    std::uint32_t value = 0U;
    for (const std::uint8_t byte : input.first(4U)) value = (value << 8U) | byte;
    return value;
}

std::uint64_t read_u64(std::span<const std::uint8_t> input) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : input.first(8U)) value = (value << 8U) | byte;
    return value;
}

ErrorCode error_for_result(std::uint16_t result) {
    switch (result) {
        case 0U: return ErrorCode::ok;
        case 1U:
        case 3U:
        case 7U:
            return ErrorCode::unavailable;
        case 2U: return ErrorCode::unsupported;
        case 4U: return ErrorCode::not_found;
        case 5U: return ErrorCode::invalid_argument;
        case 6U: return ErrorCode::resource_exhausted;
        case 8U: return ErrorCode::internal_error;
    }
    return ErrorCode::protocol_error;
}

std::string result_detail(std::uint16_t result) {
    switch (result) {
        case 1U: return "remote terminal authority denied the request";
        case 2U: return "remote terminal service does not support the request";
        case 3U: return "remote terminal service is busy";
        case 4U: return "remote terminal session was not found";
        case 5U: return "remote terminal service rejected invalid state";
        case 6U: return "remote terminal service exhausted a configured bound";
        case 7U: return "remote terminal session is unavailable";
        case 8U: return "remote terminal service reported an internal failure";
        default: return "remote terminal service returned an unknown result";
    }
}

bool valid_route(const RatoxClientRoute &route) {
    return route.online_epoch != 0U && !all_zero(route.principal_id) &&
           route.transcript_confirmed && route.feature_negotiated &&
           route.claimant_authenticated;
}

}  // namespace

class RatoxClient::Impl {
  public:
    explicit Impl(Config config) : config_(config) {
        configuration_status_ = validate_config();
        initialize_windows(1U, 1U);
        next_message_id_ = config_.initial_message_id;
        events_.reserve(config_.maximum_events);
    }

    ~Impl() {
        clear_outbound();
        security::secure_wipe(principal_id_);
        security::secure_wipe(session_id_);
        security::secure_wipe(attachment_nonce_);
    }

    Status begin_open(
        const RatoxClientRoute &route,
        const SessionId &session_id,
        const AttachmentNonce &attachment_nonce,
        std::uint16_t columns,
        std::uint16_t rows) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (!valid_route(route)) {
            return Status{ErrorCode::unavailable,
                          "Ratox client route is not transcript-confirmed, negotiated, and authenticated"};
        }
        if (all_zero(session_id) || all_zero(attachment_nonce)) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox OPEN requires nonzero session and attachment identifiers"};
        }
        if (!valid_dimensions(columns, rows)) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox terminal dimensions must be in 1..1000"};
        }
        if (state_ != RatoxClientState::idle &&
            state_ != RatoxClientState::exited &&
            state_ != RatoxClientState::failed) {
            return Status{ErrorCode::unavailable,
                          "Ratox client already owns a live or recoverable session"};
        }
        if (next_message_id_ == 0U) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox client exhausted its message identifier space"};
        }

        clear_outbound();
        events_.clear();
        dropped_events_ = 0U;
        detach_when_attached_ = false;
        initialize_windows(1U, 1U);
        security::secure_wipe(principal_id_);
        security::secure_wipe(session_id_);
        security::secure_wipe(attachment_nonce_);
        route_ = route;
        peer_friend_number_ = route.friend_number;
        principal_id_ = route.principal_id;
        session_id_ = session_id;
        attachment_nonce_ = attachment_nonce;
        incarnation_ = 0U;
        generation_ = 0U;
        input_send_cursor_ = 1U;
        requested_resume_output_ = 1U;
        pending_request_message_id_ = 0U;
        heartbeat_message_id_ = 0U;

        Frame frame = base_frame(FrameType::open);
        frame.incarnation = 0U;
        frame.generation = 0U;
        frame.payload.resize(12U, 0U);
        frame.payload[0U] = 1U;
        write_u16(std::span<std::uint8_t>{frame.payload}.subspan(2U, 2U), columns);
        write_u16(std::span<std::uint8_t>{frame.payload}.subspan(4U, 2U), rows);
        const Status queued = queue_frame(frame);
        if (!queued.ok()) {
            clear_outbound();
            route_.reset();
            peer_friend_number_.reset();
            security::secure_wipe(principal_id_);
            security::secure_wipe(session_id_);
            security::secure_wipe(attachment_nonce_);
            incarnation_ = 0U;
            generation_ = 0U;
            pending_request_message_id_ = 0U;
            state_ = RatoxClientState::failed;
            return queued;
        }
        pending_request_message_id_ = frame.message_id;
        state_ = RatoxClientState::opening;
        return Status::success();
    }

    Status begin_resume(
        const RatoxClientRoute &route,
        const AttachmentNonce &attachment_nonce) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (state_ != RatoxClientState::detached) {
            return Status{ErrorCode::unavailable,
                          "Ratox RESUME requires a detached session"};
        }
        if (!valid_route(route) || all_zero(attachment_nonce)) {
            return Status{ErrorCode::unavailable,
                          "Ratox RESUME route or attachment nonce is invalid"};
        }
        if (!peer_friend_number_ ||
            *peer_friend_number_ != route.friend_number ||
            principal_id_ != route.principal_id) {
            return Status{ErrorCode::unavailable,
                          "Ratox RESUME cannot change peer or durable principal"};
        }
        if (incarnation_ == 0U || generation_ == 0U || all_zero(session_id_)) {
            return Status{ErrorCode::internal_error,
                          "Ratox detached state has no resumable identity"};
        }

        const ReplaySnapshot input = input_.snapshot();
        const ReplaySnapshot output = output_.snapshot();
        if (outbound_capacity_exhausted(16U)) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox client outbound queue reached its configured bound"};
        }
        if (next_message_id_ == 0U) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox client exhausted its message identifier space"};
        }

        // Build and retain the RESUME against the proposed route before
        // publishing any new attachment identity. A saturated queue or message
        // ID exhaustion therefore leaves the detached session exactly intact.
        Frame frame;
        frame.type = FrameType::resume;
        frame.session_id = session_id_;
        frame.principal_id = principal_id_;
        frame.attachment_nonce = attachment_nonce;
        frame.incarnation = incarnation_;
        frame.generation = generation_;
        frame.payload.resize(16U, 0U);
        write_u64(std::span<std::uint8_t>{frame.payload}.first(8U),
                  input.base_sequence);
        write_u64(std::span<std::uint8_t>{frame.payload}.subspan(8U, 8U),
                  output.base_sequence);
        const Status queued = queue_frame_on_route(frame, route);
        if (!queued.ok()) return queued;

        route_ = route;
        security::secure_wipe(attachment_nonce_);
        attachment_nonce_ = attachment_nonce;
        requested_resume_output_ = output.base_sequence;
        input_send_cursor_ = input.base_sequence;
        pending_request_message_id_ = frame.message_id;
        heartbeat_message_id_ = 0U;
        state_ = RatoxClientState::resuming;
        return Status::success();
    }

    Status enqueue_input(std::span<const std::uint8_t> bytes) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (state_ != RatoxClientState::attached) {
            return Status{ErrorCode::unavailable,
                          "Ratox input requires an attached session"};
        }
        if (bytes.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox input cannot be empty"};
        }
        auto appended = input_.append(bytes);
        if (!appended) return appended.status();
        return stage_input();
    }

    Status acknowledge_output(std::uint64_t next_expected_sequence) {
        if (!configuration_status_.ok()) return configuration_status_;
        const ReplaySnapshot snapshot = output_.snapshot();
        if (next_expected_sequence == 0U ||
            next_expected_sequence > snapshot.next_sequence) {
            return Status{ErrorCode::protocol_error,
                          "Ratox output acknowledgement advances beyond retained output"};
        }
        if (next_expected_sequence <= snapshot.base_sequence) {
            return Status::success();
        }
        if (state_ != RatoxClientState::attached &&
            state_ != RatoxClientState::closing) {
            return output_.acknowledge(next_expected_sequence);
        }
        Frame frame = base_frame(FrameType::output_ack);
        frame.incarnation = incarnation_;
        frame.generation = generation_;
        frame.acknowledgement = next_expected_sequence;
        // Reserve (or monotonically coalesce) the exact remote acknowledgement
        // before releasing the local replay prefix. Queue saturation therefore
        // cannot make locally rendered bytes disappear without a deliverable
        // cumulative ACK, and a fast terminal cannot flood the control queue
        // with obsolete intermediate ACK positions.
        const Status queued = queue_cumulative_output_ack(frame);
        if (!queued.ok()) return queued;
        return output_.acknowledge(next_expected_sequence);
    }

    Status resize(std::uint16_t columns, std::uint16_t rows) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (state_ != RatoxClientState::attached) {
            return Status{ErrorCode::unavailable,
                          "Ratox resize requires an attached session"};
        }
        if (!valid_dimensions(columns, rows)) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox terminal dimensions must be in 1..1000"};
        }
        Frame frame = base_frame(FrameType::resize);
        frame.incarnation = incarnation_;
        frame.generation = generation_;
        frame.payload.resize(4U, 0U);
        write_u16(std::span<std::uint8_t>{frame.payload}.first(2U), columns);
        write_u16(std::span<std::uint8_t>{frame.payload}.subspan(2U, 2U), rows);
        return queue_latest_resize(frame);
    }

    Status ping() {
        if (!configuration_status_.ok()) return configuration_status_;
        if (state_ != RatoxClientState::attached) {
            return Status{ErrorCode::unavailable,
                          "Ratox PING requires an attached session"};
        }

        Frame frame = base_frame(FrameType::ping);
        frame.incarnation = incarnation_;
        frame.generation = generation_;
        if (heartbeat_message_id_ == 0U) {
            const Status queued = queue_frame(frame);
            if (queued.ok()) heartbeat_message_id_ = frame.message_id;
            return queued;
        }

        frame.message_id = heartbeat_message_id_;
        for (const RatoxClientOutboundPacket &packet : outbound_) {
            if (packet.type == FrameType::ping &&
                packet.message_id == heartbeat_message_id_ &&
                same_attachment(packet, frame)) {
                // Coalesce callers while the exact heartbeat is still waiting
                // for local transport acceptance.
                return Status::success();
            }
        }
        if (!route_) {
            return Status{ErrorCode::unavailable,
                          "Ratox client has no current transport route"};
        }
        return queue_assigned_frame_on_route(frame, *route_);
    }

    Status detach() {
        if (!configuration_status_.ok()) return configuration_status_;
        if (state_ == RatoxClientState::opening ||
            state_ == RatoxClientState::resuming) {
            detach_when_attached_ = true;
            return Status::success();
        }
        if (state_ != RatoxClientState::attached &&
            state_ != RatoxClientState::closing) {
            return state_ == RatoxClientState::detached
                ? Status::success()
                : Status{ErrorCode::unavailable,
                         "Ratox detach requires an attached session"};
        }
        const Status queued = queue_detach_now();
        if (queued.ok()) return queued;
        if (queued.code() == ErrorCode::resource_exhausted &&
            outbound_capacity_exhausted(0U)) {
            // A disconnected local terminal must not leave a remote writer
            // attached merely because the retained transport queue is full.
            // Service retries DETACH before staging any more input.
            detach_when_attached_ = true;
            return Status::success();
        }
        return fail(
            "Ratox DETACH could not be retained: " + queued.message(),
            queued.code());
    }

    Status close(std::uint16_t reason) {
        if (!configuration_status_.ok()) return configuration_status_;
        if (state_ != RatoxClientState::attached) {
            return Status{ErrorCode::unavailable,
                          "Ratox close requires an attached session"};
        }
        if (reason > 4U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox close reason must be in 0..4"};
        }
        Frame frame = base_frame(FrameType::close);
        frame.incarnation = incarnation_;
        frame.generation = generation_;
        frame.payload.resize(2U, 0U);
        write_u16(frame.payload, reason);
        const Status queued = queue_frame(frame);
        if (!queued.ok()) return queued;
        state_ = RatoxClientState::closing;
        return Status::success();
    }

    Status receive(
        const RatoxClientRoute &route,
        std::span<const std::uint8_t> packet) {
        if (!configuration_status_.ok()) return configuration_status_;
        auto decoded = protocol::ratox::decode(packet);
        if (!decoded) return decoded.status();
        const Frame &frame = decoded.value();
        if (!is_ratox_client_inbound(frame.type)) {
            return Status{ErrorCode::protocol_error,
                          "Ratox client received a controller-request frame"};
        }
        if (!route_ || route != *route_ || !valid_route(route)) {
            return Status{ErrorCode::unavailable,
                          "Ratox client packet route is stale or unauthenticated"};
        }
        if (frame.session_id != session_id_ ||
            frame.principal_id != principal_id_ ||
            frame.attachment_nonce != attachment_nonce_) {
            // A delayed packet from an older session or attachment is rejected
            // without allowing it to destroy the current controller state.
            return Status{ErrorCode::protocol_error,
                          "Ratox client packet identity does not match the active attachment"};
        }

        switch (frame.type) {
            case FrameType::open_result:
                return receive_open_result(frame);
            case FrameType::resume_result:
                return receive_resume_result(frame);
            case FrameType::attach_result:
                return fail("Ratox client did not issue ATTACH",
                            ErrorCode::protocol_error);
            case FrameType::input_ack:
                return receive_input_ack(frame);
            case FrameType::output:
                return receive_output(frame);
            case FrameType::output_gap:
                return receive_output_gap(frame);
            case FrameType::pong:
                if ((state_ != RatoxClientState::attached &&
                     state_ != RatoxClientState::closing) ||
                    !attached_identity(frame)) {
                    return Status{ErrorCode::protocol_error,
                                  "Ratox PONG attachment identity is stale"};
                }
                if (heartbeat_message_id_ == 0U ||
                    frame.correlation_id != heartbeat_message_id_) {
                    return Status{ErrorCode::protocol_error,
                                  "Ratox PONG does not correlate to the attachment heartbeat"};
                }
                drop_outbound_message_id(heartbeat_message_id_);
                append_event(RatoxClientEventKind::pong);
                return Status::success();
            case FrameType::exit_status:
                return receive_exit(frame);
            case FrameType::open:
            case FrameType::attach:
            case FrameType::detach:
            case FrameType::input:
            case FrameType::output_ack:
            case FrameType::resize:
            case FrameType::ping:
            case FrameType::close:
            case FrameType::resume:
                break;
        }
        return fail("Ratox client received an impossible frame type",
                    ErrorCode::protocol_error);
    }

    Status peer_offline(
        std::uint32_t friend_number,
        std::uint64_t online_epoch) {
        if (!route_ || route_->friend_number != friend_number ||
            route_->online_epoch != online_epoch) {
            return Status{ErrorCode::not_found,
                          "Ratox client route does not match the offline epoch"};
        }
        drop_outbound_route(friend_number, online_epoch);
        route_.reset();
        pending_request_message_id_ = 0U;
        heartbeat_message_id_ = 0U;
        detach_when_attached_ = false;
        if (state_ == RatoxClientState::opening && incarnation_ == 0U) {
            state_ = RatoxClientState::failed;
            append_event(
                RatoxClientEventKind::route_lost,
                ErrorCode::unavailable,
                "Ratox peer went offline before OPEN completed; the unknown remote outcome cannot be resumed safely");
        } else if (state_ != RatoxClientState::idle &&
                   state_ != RatoxClientState::exited &&
                   state_ != RatoxClientState::failed) {
            state_ = RatoxClientState::detached;
            append_event(
                RatoxClientEventKind::route_lost,
                ErrorCode::unavailable,
                "Ratox peer went offline; the session may be resumed after a new authenticated epoch");
        }
        return Status::success();
    }

    Status service() {
        if (!configuration_status_.ok()) return configuration_status_;
        if (detach_when_attached_ &&
            (state_ == RatoxClientState::attached ||
             state_ == RatoxClientState::closing)) {
            const Status detached = queue_detach_now();
            if (!detached.ok()) {
                if (detached.code() == ErrorCode::resource_exhausted &&
                    outbound_capacity_exhausted(0U)) {
                    return Status::success();
                }
                return fail(
                    "Ratox deferred DETACH could not be retained: " +
                        detached.message(),
                    detached.code());
            }
            return Status::success();
        }
        return state_ == RatoxClientState::attached
            ? stage_input()
            : Status::success();
    }

    const RatoxClientOutboundPacket *peek_outbound() const noexcept {
        return outbound_.empty() ? nullptr : &outbound_.front();
    }

    Status pop_outbound() {
        if (outbound_.empty()) {
            return Status{ErrorCode::not_found,
                          "Ratox client outbound queue is empty"};
        }
        outbound_bytes_ -= outbound_.front().size;
        wipe_outbound_packet(outbound_.front());
        outbound_.pop_front();
        return Status::success();
    }

    Result<ReplaySlice> read_output(
        std::uint64_t next_expected_sequence,
        std::size_t maximum_bytes) const {
        return output_.replay_from(next_expected_sequence, maximum_bytes);
    }

    RatoxClientSnapshot snapshot() const noexcept {
        RatoxClientSnapshot snapshot;
        snapshot.state = state_;
        snapshot.route_present = route_.has_value();
        if (route_) snapshot.route = *route_;
        snapshot.peer_present = peer_friend_number_.has_value();
        if (peer_friend_number_) {
            snapshot.peer_friend_number = *peer_friend_number_;
            snapshot.principal_id = principal_id_;
        }
        snapshot.session_id = session_id_;
        snapshot.attachment_nonce = attachment_nonce_;
        snapshot.incarnation = incarnation_;
        snapshot.generation = generation_;
        snapshot.input = input_.snapshot();
        snapshot.output = output_.snapshot();
        snapshot.input_send_cursor = input_send_cursor_;
        snapshot.heartbeat_message_id = heartbeat_message_id_;
        snapshot.heartbeat_queued = std::any_of(
            outbound_.begin(), outbound_.end(), [this](const auto &packet) {
                return heartbeat_message_id_ != 0U &&
                       packet.type == FrameType::ping &&
                       packet.message_id == heartbeat_message_id_;
            });
        snapshot.outbound_packets = outbound_.size();
        snapshot.outbound_bytes = outbound_bytes_;
        snapshot.retained_events = events_.size();
        snapshot.dropped_events = dropped_events_;
        return snapshot;
    }

    std::vector<RatoxClientEvent> drain_events() {
        std::vector<RatoxClientEvent> drained;
        drained.swap(events_);
        events_.reserve(config_.maximum_events);
        return drained;
    }

    void reset() noexcept {
        clear_outbound();
        events_.clear();
        initialize_windows(1U, 1U);
        state_ = RatoxClientState::idle;
        route_.reset();
        peer_friend_number_.reset();
        security::secure_wipe(principal_id_);
        security::secure_wipe(session_id_);
        security::secure_wipe(attachment_nonce_);
        incarnation_ = 0U;
        generation_ = 0U;
        input_send_cursor_ = 1U;
        requested_resume_output_ = 1U;
        pending_request_message_id_ = 0U;
        heartbeat_message_id_ = 0U;
        detach_when_attached_ = false;
        next_message_id_ = config_.initial_message_id;
        dropped_events_ = 0U;
    }

  private:
    Status validate_config() const {
        if (config_.maximum_input_bytes == 0U ||
            config_.maximum_output_bytes == 0U ||
            config_.maximum_outbound_packets == 0U ||
            config_.maximum_outbound_bytes < protocol::ratox::kMaximumPacketBytes ||
            config_.maximum_events == 0U ||
            config_.initial_message_id == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox client bounds and initial message ID must be positive"};
        }
        if (config_.maximum_input_bytes > 64U * 1024U * 1024U ||
            config_.maximum_output_bytes > 64U * 1024U * 1024U ||
            config_.maximum_outbound_packets > 4096U ||
            config_.maximum_outbound_bytes > 64U * 1024U * 1024U ||
            config_.maximum_events > 4096U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox client configured bounds exceed hard safety ceilings"};
        }
        return Status::success();
    }

    static bool valid_dimensions(std::uint16_t columns, std::uint16_t rows) {
        return columns >= 1U && columns <= 1000U && rows >= 1U && rows <= 1000U;
    }

    void initialize_windows(
        std::uint64_t input_sequence,
        std::uint64_t output_sequence) {
        input_ = ByteReplayWindow(ByteReplayWindow::Config{
            config_.maximum_input_bytes, input_sequence});
        output_ = ByteReplayWindow(ByteReplayWindow::Config{
            config_.maximum_output_bytes, output_sequence});
    }

    static void wipe_outbound_packet(
        RatoxClientOutboundPacket &packet) noexcept {
        security::secure_wipe(packet.principal_id);
        security::secure_wipe(packet.session_id);
        security::secure_wipe(packet.attachment_nonce);
        security::secure_wipe(packet.storage);
        packet.incarnation = 0U;
        packet.generation = 0U;
        packet.message_id = 0U;
        packet.acknowledgement = 0U;
        packet.size = 0U;
    }

    void clear_outbound() noexcept {
        for (RatoxClientOutboundPacket &packet : outbound_) {
            wipe_outbound_packet(packet);
        }
        outbound_.clear();
        outbound_bytes_ = 0U;
    }

    Result<std::uint64_t> allocate_message_id() {
        if (next_message_id_ == 0U) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox client exhausted its message identifier space"};
        }
        const std::uint64_t allocated = next_message_id_;
        ++next_message_id_;
        if (next_message_id_ == 0U) {
            // The allocated maximum value remains legal; the following
            // allocation fails instead of wrapping to the reserved zero ID.
        }
        return allocated;
    }

    Frame base_frame(FrameType type) const {
        Frame frame;
        frame.type = type;
        frame.session_id = session_id_;
        frame.principal_id = principal_id_;
        frame.attachment_nonce = attachment_nonce_;
        return frame;
    }

    [[nodiscard]] bool outbound_capacity_exhausted(
        std::size_t payload_bytes) const noexcept {
        const std::size_t packet_bytes =
            protocol::ratox::kHeaderBytes + payload_bytes;
        return outbound_.size() >= config_.maximum_outbound_packets ||
               packet_bytes > config_.maximum_outbound_bytes - outbound_bytes_;
    }

    Status queue_frame(Frame &frame) {
        if (!route_) {
            return Status{ErrorCode::unavailable,
                          "Ratox client has no current transport route"};
        }
        return queue_frame_on_route(frame, *route_);
    }

    Status queue_assigned_frame_on_route(
        const Frame &frame,
        const RatoxClientRoute &route) {
        if (!valid_route(route)) {
            return Status{ErrorCode::unavailable,
                          "Ratox client outbound route is not authenticated"};
        }
        if (outbound_capacity_exhausted(frame.payload.size())) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox client outbound queue reached its configured bound"};
        }
        if (frame.message_id == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox assigned outbound frame has a zero message ID"};
        }
        auto encoded = protocol::ratox::encode(frame);
        if (!encoded) return encoded.status();

        RatoxClientOutboundPacket packet;
        packet.friend_number = route.friend_number;
        packet.online_epoch = route.online_epoch;
        packet.principal_id = route.principal_id;
        packet.session_id = frame.session_id;
        packet.attachment_nonce = frame.attachment_nonce;
        packet.incarnation = frame.incarnation;
        packet.generation = frame.generation;
        packet.message_id = frame.message_id;
        packet.acknowledgement = frame.acknowledgement;
        packet.type = frame.type;
        packet.size = encoded.value().size();
        std::copy(encoded.value().begin(), encoded.value().end(), packet.storage.begin());
        outbound_bytes_ += packet.size;
        outbound_.push_back(std::move(packet));
        security::secure_wipe(encoded.value());
        return Status::success();
    }

    Status queue_frame_on_route(
        Frame &frame,
        const RatoxClientRoute &route) {
        if (!valid_route(route)) {
            return Status{ErrorCode::unavailable,
                          "Ratox client outbound route is not authenticated"};
        }
        if (outbound_capacity_exhausted(frame.payload.size())) {
            return Status{ErrorCode::resource_exhausted,
                          "Ratox client outbound queue reached its configured bound"};
        }
        auto message = allocate_message_id();
        if (!message) return message.status();
        frame.message_id = message.value();
        return queue_assigned_frame_on_route(frame, route);
    }

    bool same_attachment(
        const RatoxClientOutboundPacket &packet,
        const Frame &frame) const noexcept {
        return route_ && packet.friend_number == route_->friend_number &&
               packet.online_epoch == route_->online_epoch &&
               packet.principal_id == frame.principal_id &&
               packet.session_id == frame.session_id &&
               packet.attachment_nonce == frame.attachment_nonce &&
               packet.incarnation == frame.incarnation &&
               packet.generation == frame.generation;
    }

    Status replace_retained_frame(
        RatoxClientOutboundPacket &packet,
        Frame &frame) {
        frame.message_id = packet.message_id;
        auto encoded = protocol::ratox::encode(frame);
        if (!encoded) return encoded.status();
        if (encoded.value().size() != packet.size) {
            security::secure_wipe(encoded.value());
            return Status{ErrorCode::internal_error,
                          "Ratox retained control-frame replacement changed packet size"};
        }
        std::fill(packet.storage.begin(), packet.storage.end(), 0U);
        std::copy(encoded.value().begin(), encoded.value().end(), packet.storage.begin());
        packet.acknowledgement = frame.acknowledgement;
        security::secure_wipe(encoded.value());
        return Status::success();
    }

    Status queue_cumulative_output_ack(Frame &frame) {
        for (auto iterator = outbound_.rbegin(); iterator != outbound_.rend();
             ++iterator) {
            if (iterator->type == FrameType::output_ack &&
                same_attachment(*iterator, frame)) {
                if (frame.acknowledgement <= iterator->acknowledgement) {
                    return Status::success();
                }
                return replace_retained_frame(*iterator, frame);
            }
        }
        return queue_frame(frame);
    }

    Status queue_latest_resize(Frame &frame) {
        for (auto iterator = outbound_.rbegin(); iterator != outbound_.rend();
             ++iterator) {
            if (iterator->type == FrameType::resize &&
                same_attachment(*iterator, frame)) {
                return replace_retained_frame(*iterator, frame);
            }
        }
        return queue_frame(frame);
    }

    Status queue_detach_now() {
        Frame frame = base_frame(FrameType::detach);
        frame.incarnation = incarnation_;
        frame.generation = generation_;
        const Status queued = queue_frame(frame);
        if (!queued.ok()) return queued;
        heartbeat_message_id_ = 0U;
        detach_when_attached_ = false;
        state_ = RatoxClientState::detached;
        append_event(RatoxClientEventKind::detached);
        return Status::success();
    }

    Status stage_input() {
        if (state_ != RatoxClientState::attached) return Status::success();
        constexpr std::size_t kMaximumFramesPerService = 32U;
        std::size_t frames = 0U;
        while (frames < kMaximumFramesPerService) {
            const ReplaySnapshot snapshot = input_.snapshot();
            if (input_send_cursor_ < snapshot.base_sequence ||
                input_send_cursor_ > snapshot.next_sequence) {
                return fail("Ratox input send cursor left the retained replay window",
                            ErrorCode::internal_error);
            }
            if (input_send_cursor_ == snapshot.next_sequence) break;
            auto replay = input_.replay_from(
                input_send_cursor_, protocol::ratox::kMaximumPayloadBytes);
            if (!replay) return replay.status();
            if (replay.value().bytes.empty()) break;

            Frame frame = base_frame(FrameType::input);
            frame.incarnation = incarnation_;
            frame.generation = generation_;
            frame.sequence = replay.value().first_sequence;
            frame.payload = replay.value().bytes;
            const Status queued = queue_frame(frame);
            if (!queued.ok()) {
                if (queued.code() == ErrorCode::resource_exhausted &&
                    outbound_capacity_exhausted(frame.payload.size())) {
                    return Status::success();
                }
                return fail(
                    "Ratox INPUT could not be retained: " + queued.message(),
                    queued.code());
            }
            input_send_cursor_ = replay.value().next_sequence;
            ++frames;
        }
        return Status::success();
    }

    bool attached_identity(const Frame &frame) const {
        return frame.incarnation == incarnation_ &&
               frame.generation == generation_;
    }

    Status receive_open_result(const Frame &frame) {
        if (state_ != RatoxClientState::opening ||
            frame.correlation_id != pending_request_message_id_) {
            return Status{ErrorCode::protocol_error,
                          "Ratox OPEN_RESULT correlation is stale"};
        }
        const std::uint16_t result = read_u16(frame.payload);
        drop_outbound_message_id(pending_request_message_id_);
        pending_request_message_id_ = 0U;
        if (result != 0U) {
            state_ = RatoxClientState::failed;
            route_.reset();
            peer_friend_number_.reset();
            security::secure_wipe(principal_id_);
            security::secure_wipe(session_id_);
            security::secure_wipe(attachment_nonce_);
            incarnation_ = 0U;
            generation_ = 0U;
            detach_when_attached_ = false;
            const ErrorCode code = error_for_result(result);
            append_event(RatoxClientEventKind::error, code, result_detail(result));
            return Status{code, result_detail(result)};
        }
        incarnation_ = frame.incarnation;
        generation_ = frame.generation;
        input_send_cursor_ = 1U;
        state_ = RatoxClientState::attached;
        RatoxClientEvent event;
        event.kind = RatoxClientEventKind::opened;
        event.sequence = 1U;
        event.acknowledgement = 1U;
        append_event(std::move(event));
        if (detach_when_attached_) {
            detach_when_attached_ = false;
            return detach();
        }
        return Status::success();
    }

    Status receive_resume_result(const Frame &frame) {
        if (state_ != RatoxClientState::resuming ||
            frame.correlation_id != pending_request_message_id_ ||
            frame.incarnation != incarnation_) {
            return Status{ErrorCode::protocol_error,
                          "Ratox RESUME_RESULT correlation or incarnation is stale"};
        }
        const std::uint16_t result = read_u16(frame.payload);
        drop_outbound_message_id(pending_request_message_id_);
        pending_request_message_id_ = 0U;
        if (result != 0U) {
            state_ = RatoxClientState::detached;
            const ErrorCode code = error_for_result(result);
            append_event(RatoxClientEventKind::error, code, result_detail(result));
            return Status{code, result_detail(result)};
        }

        if (frame.generation <= generation_) {
            return fail("Ratox RESUME_RESULT did not advance the attachment generation",
                        ErrorCode::protocol_error);
        }
        const std::uint64_t next_input = read_u64(
            std::span<const std::uint8_t>{frame.payload}.subspan(4U, 8U));
        const std::uint64_t output_base = read_u64(
            std::span<const std::uint8_t>{frame.payload}.subspan(12U, 8U));
        const std::uint64_t output_next = read_u64(
            std::span<const std::uint8_t>{frame.payload}.subspan(20U, 8U));
        const ReplaySnapshot input = input_.snapshot();
        if (next_input < input.base_sequence || next_input > input.next_sequence) {
            return fail("Ratox RESUME_RESULT input position is outside retained input",
                        ErrorCode::protocol_error);
        }
        const ReplaySnapshot output = output_.snapshot();
        if (output_base < requested_resume_output_ ||
            output_base > output_next || output.next_sequence > output_next) {
            return fail(
                "Ratox RESUME_RESULT output bounds contradict retained controller output",
                ErrorCode::protocol_error);
        }

        // Validate every peer-controlled replay coordinate before releasing
        // any locally retained byte. A malformed output claim must not be able
        // to acknowledge input as a side effect of a response that ultimately
        // fails closed.
        const Status input_acknowledged = input_.acknowledge(next_input);
        if (!input_acknowledged.ok()) return fail(
            input_acknowledged.message(), input_acknowledged.code());
        input_send_cursor_ = next_input;

        // Preserve every locally retained byte the remote no longer has. Only
        // an actual hole beyond our local next sequence requires a window
        // reset and an explicit gap. If the remote retained base lies inside
        // our local replay, overlapping retransmissions are validated below.
        const bool local_gap = output_base > output.next_sequence;
        if (local_gap) {
            output_ = ByteReplayWindow(ByteReplayWindow::Config{
                config_.maximum_output_bytes, output_base});
        }
        generation_ = frame.generation;
        state_ = RatoxClientState::attached;
        RatoxClientEvent event;
        event.kind = RatoxClientEventKind::resumed;
        event.sequence = next_input;
        event.acknowledgement = output_.snapshot().base_sequence;
        append_event(std::move(event));
        if (local_gap) {
            RatoxClientEvent gap;
            gap.kind = RatoxClientEventKind::output_gap;
            gap.sequence = output_base;
            gap.acknowledgement = output_next;
            gap.detail =
                "remote output history advanced beyond locally retained output";
            append_event(std::move(gap));
        }
        const Status staged = stage_input();
        if (!staged.ok()) return staged;
        if (detach_when_attached_) {
            detach_when_attached_ = false;
            return detach();
        }
        return Status::success();
    }

    Status receive_input_ack(const Frame &frame) {
        if (state_ != RatoxClientState::attached &&
            state_ != RatoxClientState::closing) {
            return fail("Ratox INPUT_ACK arrived while not attached",
                        ErrorCode::protocol_error);
        }
        if (!attached_identity(frame)) {
            return fail("Ratox INPUT_ACK attachment identity is stale",
                        ErrorCode::protocol_error);
        }
        const ReplaySnapshot snapshot = input_.snapshot();
        if (frame.acknowledgement < snapshot.base_sequence ||
            frame.acknowledgement > snapshot.next_sequence ||
            frame.acknowledgement > input_send_cursor_) {
            return fail("Ratox INPUT_ACK is outside sent retained input",
                        ErrorCode::protocol_error);
        }
        const Status acknowledged = input_.acknowledge(frame.acknowledgement);
        if (!acknowledged.ok()) return fail(acknowledged.message(), acknowledged.code());
        return stage_input();
    }

    Status receive_output(const Frame &frame) {
        if (state_ != RatoxClientState::attached &&
            state_ != RatoxClientState::closing) {
            return fail("Ratox OUTPUT arrived while not attached",
                        ErrorCode::protocol_error);
        }
        if (!attached_identity(frame)) {
            return fail("Ratox OUTPUT attachment identity is stale",
                        ErrorCode::protocol_error);
        }
        const ReplaySnapshot snapshot = output_.snapshot();
        if (frame.payload.size() >
            std::numeric_limits<std::uint64_t>::max() - frame.sequence) {
            return fail("Ratox OUTPUT sequence overflows",
                        ErrorCode::protocol_error);
        }
        const std::uint64_t frame_next =
            frame.sequence + static_cast<std::uint64_t>(frame.payload.size());
        if (frame_next <= snapshot.base_sequence) {
            // This complete prefix was already rendered and acknowledged. Its
            // bytes have been wiped, so a wholly old retransmission is benign.
            return Status::success();
        }
        if (frame.sequence > snapshot.next_sequence) {
            return fail("Ratox OUTPUT introduced a sequence gap",
                        ErrorCode::protocol_error);
        }

        // Lossless transport retries and resume catch-up may overlap an
        // acknowledged prefix, retained bytes, and a fresh suffix in one
        // frame. Compare every byte we still retain before extending the
        // replay window; conflicting duplicates fail closed.
        const std::uint64_t overlap_begin =
            std::max(frame.sequence, snapshot.base_sequence);
        const std::uint64_t overlap_end =
            std::min(frame_next, snapshot.next_sequence);
        if (overlap_begin < overlap_end) {
            const std::size_t overlap_size = static_cast<std::size_t>(
                overlap_end - overlap_begin);
            auto retained = output_.replay_from(overlap_begin, overlap_size);
            const std::size_t frame_offset = static_cast<std::size_t>(
                overlap_begin - frame.sequence);
            if (!retained || retained.value().bytes.size() != overlap_size ||
                !std::equal(
                    retained.value().bytes.begin(), retained.value().bytes.end(),
                    frame.payload.begin() +
                        static_cast<std::ptrdiff_t>(frame_offset))) {
                return fail(
                    "Ratox OUTPUT replay reused retained positions with different bytes",
                    ErrorCode::protocol_error);
            }
        }
        if (frame_next <= snapshot.next_sequence) return Status::success();

        const std::size_t suffix_offset = static_cast<std::size_t>(
            snapshot.next_sequence - frame.sequence);
        auto appended = output_.append(
            std::span<const std::uint8_t>{frame.payload}.subspan(suffix_offset));
        if (!appended) {
            return fail(
                "Ratox local output replay reached its configured bound before acknowledgement",
                appended.status().code());
        }
        RatoxClientEvent event;
        event.kind = RatoxClientEventKind::output_available;
        event.sequence = snapshot.next_sequence;
        event.acknowledgement = frame_next;
        append_event(std::move(event));
        return Status::success();
    }

    Status receive_output_gap(const Frame &frame) {
        if (state_ != RatoxClientState::attached &&
            state_ != RatoxClientState::closing) {
            return fail("Ratox OUTPUT_GAP arrived while not attached",
                        ErrorCode::protocol_error);
        }
        if (!attached_identity(frame)) {
            return fail("Ratox OUTPUT_GAP attachment identity is stale",
                        ErrorCode::protocol_error);
        }
        const ReplaySnapshot snapshot = output_.snapshot();
        if (frame.acknowledgement < snapshot.next_sequence) {
            // A wholly stale duplicate cannot invalidate output already
            // retained or acknowledged locally.
            if (frame.sequence <= snapshot.base_sequence) {
                return Status::success();
            }
            return fail(
                "Ratox OUTPUT_GAP produced-next position moved behind received output",
                ErrorCode::protocol_error);
        }
        if (frame.sequence <= snapshot.next_sequence) {
            // The remote may have evicted bytes that are still retained
            // locally. Keep them and validate its overlapping retransmission
            // instead of manufacturing data loss on the controller.
            return Status::success();
        }
        if (snapshot.pending_bytes != 0U) {
            return fail(
                "Ratox OUTPUT_GAP begins after locally retained output; refusing to discard the retained prefix",
                ErrorCode::protocol_error);
        }
        output_ = ByteReplayWindow(ByteReplayWindow::Config{
            config_.maximum_output_bytes, frame.sequence});
        RatoxClientEvent event;
        event.kind = RatoxClientEventKind::output_gap;
        event.sequence = frame.sequence;
        event.acknowledgement = frame.acknowledgement;
        event.detail = "remote output history reported an explicit retained-prefix gap";
        append_event(std::move(event));
        return Status::success();
    }

    Status receive_exit(const Frame &frame) {
        if (frame.incarnation != incarnation_ || frame.generation != generation_) {
            return Status{ErrorCode::protocol_error,
                          "Ratox EXIT_STATUS attachment identity is stale"};
        }
        if (state_ == RatoxClientState::exited) {
            return Status::success();
        }
        if (state_ != RatoxClientState::attached &&
            state_ != RatoxClientState::closing &&
            state_ != RatoxClientState::detached) {
            return Status{ErrorCode::protocol_error,
                          "Ratox EXIT_STATUS arrived outside a live session"};
        }
        RatoxClientEvent event;
        event.kind = RatoxClientEventKind::exit_status;
        event.exit_kind = frame.payload[0U];
        event.core_dumped = frame.payload[1U] != 0U;
        event.signal = read_u16(
            std::span<const std::uint8_t>{frame.payload}.subspan(2U, 2U));
        event.exit_code = read_u32(
            std::span<const std::uint8_t>{frame.payload}.subspan(4U, 4U));
        append_event(std::move(event));
        state_ = RatoxClientState::exited;
        heartbeat_message_id_ = 0U;
        detach_when_attached_ = false;
        if (route_) {
            drop_outbound_route(route_->friend_number, route_->online_epoch);
        }
        route_.reset();
        return Status::success();
    }

    Status fail(std::string detail, ErrorCode code) {
        state_ = RatoxClientState::failed;
        pending_request_message_id_ = 0U;
        heartbeat_message_id_ = 0U;
        detach_when_attached_ = false;
        if (route_) {
            drop_outbound_route(route_->friend_number, route_->online_epoch);
        }
        route_.reset();
        append_event(RatoxClientEventKind::error, code, detail);
        return Status{code, std::move(detail)};
    }

    void append_event(
        RatoxClientEventKind kind,
        ErrorCode code = ErrorCode::ok,
        std::string detail = {}) {
        RatoxClientEvent event;
        event.kind = kind;
        event.error_code = code;
        event.detail = std::move(detail);
        append_event(std::move(event));
    }

    void append_event(RatoxClientEvent event) {
        if (!events_.empty() && event.kind == RatoxClientEventKind::output_available &&
            events_.back().kind == RatoxClientEventKind::output_available) {
            events_.back().sequence = std::min(
                events_.back().sequence, event.sequence);
            events_.back().acknowledgement = std::max(
                events_.back().acknowledgement, event.acknowledgement);
            return;
        }
        if (!events_.empty() && event.kind == RatoxClientEventKind::pong &&
            events_.back().kind == RatoxClientEventKind::pong) {
            return;
        }
        if (events_.size() >= config_.maximum_events) {
            const auto disposable = std::find_if(
                events_.begin(), events_.end(), [](const RatoxClientEvent &entry) {
                    return entry.kind == RatoxClientEventKind::output_available ||
                           entry.kind == RatoxClientEventKind::pong;
                });
            events_.erase(disposable != events_.end() ? disposable : events_.begin());
            ++dropped_events_;
        }
        events_.push_back(std::move(event));
    }

    void drop_outbound_message_id(std::uint64_t message_id) noexcept {
        if (message_id == 0U) return;
        for (auto iterator = outbound_.begin(); iterator != outbound_.end(); ++iterator) {
            if (iterator->message_id != message_id) continue;
            outbound_bytes_ -= iterator->size;
            wipe_outbound_packet(*iterator);
            outbound_.erase(iterator);
            return;
        }
    }

    void drop_outbound_route(
        std::uint32_t friend_number,
        std::uint64_t online_epoch) noexcept {
        std::deque<RatoxClientOutboundPacket> retained;
        std::size_t retained_bytes = 0U;
        while (!outbound_.empty()) {
            RatoxClientOutboundPacket packet = std::move(outbound_.front());
            outbound_.pop_front();
            if (packet.friend_number == friend_number &&
                packet.online_epoch == online_epoch) {
                wipe_outbound_packet(packet);
                continue;
            }
            retained_bytes += packet.size;
            retained.push_back(std::move(packet));
        }
        outbound_.swap(retained);
        outbound_bytes_ = retained_bytes;
    }

    Config config_;
    Status configuration_status_{};
    RatoxClientState state_{RatoxClientState::idle};
    std::optional<RatoxClientRoute> route_;
    std::optional<std::uint32_t> peer_friend_number_;
    PrincipalId principal_id_{};
    SessionId session_id_{};
    AttachmentNonce attachment_nonce_{};
    std::uint64_t incarnation_{0U};
    std::uint64_t generation_{0U};
    ByteReplayWindow input_;
    ByteReplayWindow output_;
    std::uint64_t input_send_cursor_{1U};
    std::uint64_t requested_resume_output_{1U};
    std::uint64_t pending_request_message_id_{0U};
    std::uint64_t heartbeat_message_id_{0U};
    bool detach_when_attached_{false};
    std::uint64_t next_message_id_{1U};
    std::deque<RatoxClientOutboundPacket> outbound_;
    std::size_t outbound_bytes_{0U};
    std::vector<RatoxClientEvent> events_;
    std::size_t dropped_events_{0U};
};

RatoxClient::RatoxClient() : RatoxClient(Config{}) {}
RatoxClient::RatoxClient(Config config) : impl_(new Impl(config)) {}
RatoxClient::~RatoxClient() { delete impl_; }
RatoxClient::RatoxClient(RatoxClient &&other) noexcept
    : impl_(std::exchange(other.impl_, nullptr)) {}
RatoxClient &RatoxClient::operator=(RatoxClient &&other) noexcept {
    if (this != &other) {
        delete impl_;
        impl_ = std::exchange(other.impl_, nullptr);
    }
    return *this;
}

Status RatoxClient::begin_open(
    const RatoxClientRoute &route,
    const SessionId &session_id,
    const AttachmentNonce &attachment_nonce,
    std::uint16_t columns,
    std::uint16_t rows) {
    return impl_->begin_open(route, session_id, attachment_nonce, columns, rows);
}
Status RatoxClient::begin_resume(
    const RatoxClientRoute &route,
    const AttachmentNonce &attachment_nonce) {
    return impl_->begin_resume(route, attachment_nonce);
}
Status RatoxClient::enqueue_input(std::span<const std::uint8_t> bytes) {
    return impl_->enqueue_input(bytes);
}
Status RatoxClient::acknowledge_output(std::uint64_t next_expected_sequence) {
    return impl_->acknowledge_output(next_expected_sequence);
}
Status RatoxClient::resize(std::uint16_t columns, std::uint16_t rows) {
    return impl_->resize(columns, rows);
}
Status RatoxClient::ping() { return impl_->ping(); }
Status RatoxClient::detach() { return impl_->detach(); }
Status RatoxClient::close(std::uint16_t reason) { return impl_->close(reason); }
Status RatoxClient::receive(
    const RatoxClientRoute &route,
    std::span<const std::uint8_t> packet) {
    return impl_->receive(route, packet);
}
Status RatoxClient::peer_offline(
    std::uint32_t friend_number,
    std::uint64_t online_epoch) {
    return impl_->peer_offline(friend_number, online_epoch);
}
Status RatoxClient::service() { return impl_->service(); }
const RatoxClientOutboundPacket *RatoxClient::peek_outbound() const noexcept {
    return impl_->peek_outbound();
}
Status RatoxClient::pop_outbound() { return impl_->pop_outbound(); }
Result<ReplaySlice> RatoxClient::read_output(
    std::uint64_t next_expected_sequence,
    std::size_t maximum_bytes) const {
    return impl_->read_output(next_expected_sequence, maximum_bytes);
}
RatoxClientSnapshot RatoxClient::snapshot() const noexcept {
    return impl_->snapshot();
}
std::vector<RatoxClientEvent> RatoxClient::drain_events() {
    return impl_->drain_events();
}
void RatoxClient::reset() { impl_->reset(); }

bool is_ratox_client_inbound(FrameType type) noexcept {
    switch (type) {
        case FrameType::open_result:
        case FrameType::attach_result:
        case FrameType::input_ack:
        case FrameType::output:
        case FrameType::pong:
        case FrameType::exit_status:
        case FrameType::resume_result:
        case FrameType::output_gap:
            return true;
        case FrameType::open:
        case FrameType::attach:
        case FrameType::detach:
        case FrameType::input:
        case FrameType::output_ack:
        case FrameType::resize:
        case FrameType::ping:
        case FrameType::close:
        case FrameType::resume:
            return false;
    }
    return false;
}

std::string_view to_string(RatoxClientState state) noexcept {
    switch (state) {
        case RatoxClientState::idle: return "idle";
        case RatoxClientState::opening: return "opening";
        case RatoxClientState::attached: return "attached";
        case RatoxClientState::detached: return "detached";
        case RatoxClientState::resuming: return "resuming";
        case RatoxClientState::closing: return "closing";
        case RatoxClientState::exited: return "exited";
        case RatoxClientState::failed: return "failed";
    }
    return "unknown";
}

std::string_view to_string(RatoxClientEventKind kind) noexcept {
    switch (kind) {
        case RatoxClientEventKind::opened: return "opened";
        case RatoxClientEventKind::resumed: return "resumed";
        case RatoxClientEventKind::output_available: return "output-available";
        case RatoxClientEventKind::output_gap: return "output-gap";
        case RatoxClientEventKind::detached: return "detached";
        case RatoxClientEventKind::route_lost: return "route-lost";
        case RatoxClientEventKind::exit_status: return "exit-status";
        case RatoxClientEventKind::closed: return "closed";
        case RatoxClientEventKind::error: return "error";
        case RatoxClientEventKind::pong: return "pong";
    }
    return "unknown";
}

}  // namespace iotox::interactive
