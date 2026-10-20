#include "iotox/interactive_service.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <limits>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <utility>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::Result;
using iotox::Status;
using iotox::interactive::AttachmentNonce;
using iotox::interactive::PrincipalId;
using iotox::interactive::RatoxOutboundPacket;
using iotox::interactive::RatoxPeerContext;
using iotox::interactive::RatoxService;
using iotox::interactive::SessionId;
using iotox::protocol::ratox::Frame;
using iotox::protocol::ratox::FrameType;
using iotox::terminal::Binding;
using iotox::terminal::Dimensions;
using iotox::terminal::EnvironmentEntry;
using iotox::terminal::ExitKind;
using iotox::terminal::IoDisposition;
using iotox::terminal::ProcessExit;
using iotox::terminal::ProcessSignal;
using iotox::terminal::Profile;
using iotox::terminal::ProfileRegistry;
using iotox::terminal::ProfileStoreData;
using iotox::terminal::PtyProcess;
using iotox::terminal::PtyProcessFactory;
using iotox::terminal::ReadResult;
using iotox::terminal::ResolvedProfile;
using iotox::terminal::WriteResult;

constexpr std::size_t kModelSessions = 4U;
constexpr std::size_t kModelPrincipals = 3U;
constexpr std::size_t kMaximumRetainedProcessBytes = 512U;

class Cursor {
  public:
    Cursor(const std::uint8_t *data, std::size_t size)
        : data_(data), size_(size) {}

    [[nodiscard]] bool empty() const noexcept { return offset_ >= size_; }
    [[nodiscard]] std::size_t remaining() const noexcept {
        return size_ - std::min(offset_, size_);
    }

    [[nodiscard]] std::uint8_t take() noexcept {
        return empty() ? 0U : data_[offset_++];
    }

    [[nodiscard]] std::uint16_t take_u16() noexcept {
        const std::uint16_t high = take();
        return static_cast<std::uint16_t>((high << 8U) | take());
    }

    [[nodiscard]] std::uint64_t take_u64() noexcept {
        std::uint64_t value = 0U;
        for (std::size_t index = 0U; index < 8U; ++index) {
            value = (value << 8U) | take();
        }
        return value;
    }

    [[nodiscard]] std::span<const std::uint8_t> take_bytes(
        std::size_t maximum) noexcept {
        if (maximum == 0U || empty()) return {};
        const std::size_t count = std::min(remaining(), maximum);
        const auto bytes = std::span<const std::uint8_t>{data_ + offset_, count};
        offset_ += count;
        return bytes;
    }

  private:
    const std::uint8_t *data_{nullptr};
    std::size_t size_{0U};
    std::size_t offset_{0U};
};

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
    for (const std::uint8_t byte : input) value = (value << 8U) | byte;
    return value;
}

template <std::size_t Size>
bool all_zero(const std::array<std::uint8_t, Size> &value) {
    return std::all_of(value.begin(), value.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

PrincipalId principal_id(std::size_t index) {
    PrincipalId value{};
    value[0U] = static_cast<std::uint8_t>(1U + index % kModelPrincipals);
    value[1U] = 0xD2U;
    return value;
}

SessionId session_id(std::size_t index) {
    SessionId value{};
    value[0U] = static_cast<std::uint8_t>(1U + index % kModelSessions);
    value[1U] = 0xD1U;
    return value;
}

AttachmentNonce attachment_nonce(std::size_t index, std::uint8_t salt) {
    AttachmentNonce value{};
    value[0U] = static_cast<std::uint8_t>(1U + index % kModelSessions);
    value[1U] = static_cast<std::uint8_t>(salt | 1U);
    value[2U] = 0xD3U;
    return value;
}

struct ProcessState {
    std::uint8_t write_mode{0U};
    std::uint8_t read_mode{0U};
    std::uint8_t poll_mode{0U};
    bool fail_resize{false};
    bool fail_signal{false};
    bool exit_on_signal{false};
    std::deque<std::uint8_t> output;
    std::vector<std::uint8_t> written;
    std::size_t signals{0U};
    std::size_t resizes{0U};
};

class FuzzProcess final : public PtyProcess {
  public:
    explicit FuzzProcess(std::shared_ptr<ProcessState> state)
        : state_(std::move(state)) {}

    Result<WriteResult> write(std::span<const std::uint8_t> bytes) override {
        switch (state_->write_mode % 7U) {
            case 0U:
                return record(bytes, bytes.size());
            case 1U:
                return record(bytes, std::min<std::size_t>(1U, bytes.size()));
            case 2U:
                return WriteResult{IoDisposition::would_block, 0U};
            case 3U:
                return Status{ErrorCode::io_error,
                              "fuzz PTY write failure"};
            case 4U:
                return WriteResult{IoDisposition::closed, 0U};
            case 5U:
                return WriteResult{IoDisposition::progress, 0U};
            case 6U:
                return WriteResult{IoDisposition::progress, bytes.size() + 1U};
        }
        __builtin_trap();
    }

    Result<ReadResult> read(std::size_t maximum_bytes) override {
        switch (state_->read_mode % 7U) {
            case 0U:
            case 1U: {
                if (state_->output.empty()) {
                    return ReadResult{IoDisposition::would_block, {}};
                }
                const std::size_t chunk = state_->read_mode % 7U == 0U
                    ? maximum_bytes
                    : std::min<std::size_t>(maximum_bytes, 1U);
                const std::size_t count = std::min(chunk, state_->output.size());
                std::vector<std::uint8_t> bytes;
                bytes.reserve(count);
                for (std::size_t index = 0U; index < count; ++index) {
                    bytes.push_back(state_->output.front());
                    state_->output.pop_front();
                }
                return ReadResult{IoDisposition::progress, std::move(bytes)};
            }
            case 2U:
                return ReadResult{IoDisposition::would_block, {}};
            case 3U:
                return ReadResult{IoDisposition::closed, {}};
            case 4U:
                return Status{ErrorCode::io_error,
                              "fuzz PTY read failure"};
            case 5U:
                return ReadResult{IoDisposition::progress, {}};
            case 6U:
                return ReadResult{
                    IoDisposition::progress,
                    std::vector<std::uint8_t>(maximum_bytes + 1U, 0xA5U)};
        }
        __builtin_trap();
    }

    Status resize(const Dimensions &) override {
        ++state_->resizes;
        return state_->fail_resize
            ? Status{ErrorCode::io_error, "fuzz PTY resize failure"}
            : Status::success();
    }

    Status send_signal(ProcessSignal) override {
        ++state_->signals;
        if (state_->fail_signal) {
            return Status{ErrorCode::io_error, "fuzz PTY signal failure"};
        }
        if (state_->exit_on_signal) {
            state_->poll_mode = 1U;
            state_->read_mode = 3U;
        }
        return Status::success();
    }

    Result<std::optional<ProcessExit>> poll_exit() override {
        switch (state_->poll_mode % 5U) {
            case 0U:
                return std::optional<ProcessExit>{};
            case 1U:
                return std::optional<ProcessExit>{
                    ProcessExit{ExitKind::exited, 0, false}};
            case 2U:
                return Status{ErrorCode::io_error,
                              "fuzz PTY poll failure"};
            case 3U:
                return std::optional<ProcessExit>{
                    ProcessExit{ExitKind::exited, 999, false}};
            case 4U:
                return std::optional<ProcessExit>{
                    ProcessExit{ExitKind::signaled, 9, false}};
        }
        __builtin_trap();
    }

  private:
    Result<WriteResult> record(
        std::span<const std::uint8_t> bytes, std::size_t count) {
        const std::size_t room = kMaximumRetainedProcessBytes -
            std::min(state_->written.size(), kMaximumRetainedProcessBytes);
        const std::size_t retained = std::min(count, room);
        state_->written.insert(
            state_->written.end(), bytes.begin(),
            bytes.begin() + static_cast<std::ptrdiff_t>(retained));
        return WriteResult{IoDisposition::progress, count};
    }

    std::shared_ptr<ProcessState> state_;
};

class FuzzFactory final : public PtyProcessFactory {
  public:
    bool fail_spawn{false};
    bool null_spawn{false};
    std::uint8_t next_write_mode{0U};
    std::uint8_t next_read_mode{0U};
    std::uint8_t next_poll_mode{0U};
    std::vector<std::shared_ptr<ProcessState>> states;

    Result<std::unique_ptr<PtyProcess>> spawn(
        const ResolvedProfile &) override {
        if (fail_spawn) {
            return Status{ErrorCode::unavailable, "fuzz PTY spawn failure"};
        }
        if (null_spawn) return std::unique_ptr<PtyProcess>{};
        auto state = std::make_shared<ProcessState>();
        state->write_mode = next_write_mode;
        state->read_mode = next_read_mode;
        state->poll_mode = next_poll_mode;
        states.push_back(state);
        return std::unique_ptr<PtyProcess>(new FuzzProcess(std::move(state)));
    }
};

void populate_registry(ProfileRegistry &registry) {
    Profile profile;
    profile.id = "interactive-service-fuzz";
    profile.enabled = true;
    profile.arguments = {"/bin/echo", "fixed"};
    profile.working_directory = "/tmp";
    profile.environment = {EnvironmentEntry{"IOTOX_FUZZ", "1"}};
    profile.hangup_grace = std::chrono::milliseconds{1};
    profile.terminate_grace = std::chrono::milliseconds{1};
    profile.kill_reap_grace = std::chrono::milliseconds{1};

    ProfileStoreData store;
    store.profiles.push_back(std::move(profile));
    for (std::size_t index = 0U; index < kModelPrincipals; ++index) {
        Binding binding;
        binding.principal_id = principal_id(index);
        binding.profile_id = "interactive-service-fuzz";
        binding.enabled = true;
        store.bindings.push_back(std::move(binding));
    }
    if (!registry.replace(std::move(store)).ok()) __builtin_trap();
}

RatoxService::Config service_config(bool exhaust_message_ids) {
    RatoxService::Config config;
    config.enabled = true;
    config.session_incarnation = 1U;
    config.directory.maximum_sessions_per_principal = 2U;
    config.directory.maximum_sessions_per_device = kModelSessions;
    config.directory.session.input.maximum_frame_bytes = 64U;
    config.directory.session.output.maximum_bytes = 128U;
    config.directory.session.control_replay.maximum_entries = 8U;
    config.directory.session.control_replay.maximum_bytes = 20U * 1024U;
    config.directory.session.control_replay.maximum_result_bytes =
        iotox::protocol::ratox::kMaximumPacketBytes;
    config.directory.session.maximum_attachment_nonces = 8U;
    config.directory.session.maximum_events = 32U;
    config.maximum_session_tombstones = kModelSessions;
    config.maximum_admission_replay_entries = 8U;
    config.maximum_admission_replay_bytes =
        8U * (iotox::protocol::ratox::kHeaderBytes + 16U +
              iotox::protocol::ratox::kMaximumPacketBytes);
    config.maximum_outbound_packets = 8U;
    config.maximum_outbound_bytes =
        8U * iotox::protocol::ratox::kMaximumPacketBytes;
    config.maximum_events = 32U;
    config.maximum_input_write_operations = 4U;
    config.maximum_output_read_operations = 4U;
    config.maximum_output_frames = 4U;
    config.terminal_read_bytes = 64U;
    config.exit_output_drain_timeout = std::chrono::milliseconds{3};
    config.initial_outbound_message_id = exhaust_message_ids
        ? std::numeric_limits<std::uint64_t>::max() - 4U
        : 1U;
    return config;
}

struct SessionModel {
    bool known{false};
    SessionId session{};
    PrincipalId principal{};
    AttachmentNonce nonce{};
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    std::uint64_t incarnation{1U};
    std::uint64_t generation{1U};
    std::uint64_t next_input{1U};
    std::uint64_t next_output{1U};
};

std::size_t model_index(
    const std::array<SessionModel, kModelSessions> &models,
    const SessionId &session) {
    for (std::size_t index = 0U; index < models.size(); ++index) {
        if (models[index].session == session) return index;
    }
    return models.size();
}

std::uint64_t request_message_id(std::uint8_t selector) {
    return 1U + static_cast<std::uint64_t>(selector % 24U);
}

RatoxPeerContext selected_peer(
    const SessionModel &model, std::size_t principal_index,
    std::uint8_t selector, bool prefer_model) {
    RatoxPeerContext peer;
    if (prefer_model && model.known) {
        peer.friend_number = model.friend_number;
        peer.online_epoch = model.online_epoch;
        peer.principal_id = model.principal;
    } else {
        peer.friend_number = 1U + static_cast<std::uint32_t>(selector % 4U);
        peer.online_epoch = 1U + static_cast<std::uint64_t>((selector >> 2U) % 4U);
        peer.principal_id = principal_id(principal_index);
    }
    const std::uint8_t route_fault = selector & 0x0FU;
    if (route_fault == 1U) ++peer.friend_number;
    if (route_fault == 2U) ++peer.online_epoch;
    if (route_fault == 3U) {
        peer.principal_id = principal_id(principal_index + 1U);
    }
    const std::uint8_t gate_fault = selector & 0xE0U;
    peer.transcript_confirmed = gate_fault != 0x20U;
    peer.feature_negotiated = gate_fault != 0x40U;
    peer.terminal_authorized = gate_fault != 0x80U;
    return peer;
}

Frame open_frame(
    const SessionModel &model, const RatoxPeerContext &peer,
    std::uint8_t nonce_salt, std::uint8_t message_selector,
    std::uint16_t columns, std::uint16_t rows) {
    Frame frame;
    frame.type = FrameType::open;
    frame.message_id = request_message_id(message_selector);
    frame.session_id = model.session;
    frame.principal_id = peer.principal_id;
    frame.attachment_nonce = attachment_nonce(model.session[0U], nonce_salt);
    frame.payload.resize(12U, 0U);
    frame.payload[0U] = 1U;
    write_u16(
        std::span<std::uint8_t>{frame.payload}.subspan(2U, 2U),
        static_cast<std::uint16_t>(1U + columns % 512U));
    write_u16(
        std::span<std::uint8_t>{frame.payload}.subspan(4U, 2U),
        static_cast<std::uint16_t>(1U + rows % 256U));
    return frame;
}

Frame attached_frame(
    FrameType type, const SessionModel &model,
    std::uint8_t message_selector, std::uint8_t stale_selector) {
    Frame frame;
    frame.type = type;
    frame.message_id = request_message_id(message_selector);
    frame.session_id = model.session;
    frame.principal_id = model.known
        ? model.principal
        : principal_id(model.session[0U]);
    frame.attachment_nonce = model.known
        ? model.nonce
        : attachment_nonce(model.session[0U], 1U);
    frame.incarnation = model.known ? model.incarnation : 1U;
    frame.generation = model.known ? model.generation : 1U;
    if ((stale_selector & 0x01U) != 0U) ++frame.generation;
    if ((stale_selector & 0x02U) != 0U) {
        frame.attachment_nonce[3U] ^= 0x5AU;
    }
    return frame;
}

void remember_outbound(
    const RatoxOutboundPacket &packet, const Frame &frame,
    std::array<SessionModel, kModelSessions> &models) {
    const std::size_t index = model_index(models, frame.session_id);
    if (index == models.size()) return;
    SessionModel &model = models[index];
    const bool success = frame.payload.size() >= 2U &&
        read_u16(frame.payload) == 0U;
    if (frame.type == FrameType::open_result && success) {
        model.known = true;
        model.principal = frame.principal_id;
        model.nonce = frame.attachment_nonce;
        model.friend_number = packet.friend_number;
        model.online_epoch = packet.online_epoch;
        model.incarnation = frame.incarnation;
        model.generation = frame.generation;
        model.next_input = 1U;
        model.next_output = 1U;
    } else if ((frame.type == FrameType::attach_result ||
                frame.type == FrameType::resume_result) && success) {
        model.known = true;
        model.principal = frame.principal_id;
        model.nonce = frame.attachment_nonce;
        model.friend_number = packet.friend_number;
        model.online_epoch = packet.online_epoch;
        model.incarnation = frame.incarnation;
        model.generation = frame.generation;
        model.next_input = read_u64(
            std::span<const std::uint8_t>{frame.payload}.subspan(4U, 8U));
        model.next_output = read_u64(
            std::span<const std::uint8_t>{frame.payload}.subspan(20U, 8U));
    } else if (frame.type == FrameType::input_ack) {
        model.next_input = frame.acknowledgement;
    } else if (frame.type == FrameType::output) {
        model.next_output = frame.sequence + frame.payload.size();
    } else if (frame.type == FrameType::output_gap) {
        model.next_output = frame.acknowledgement;
    } else if (frame.type == FrameType::exit_status) {
        model.known = false;
    }
}

Frame check_outbound(const RatoxOutboundPacket &packet) {
    if (packet.size < iotox::protocol::ratox::kHeaderBytes ||
        packet.size > iotox::protocol::ratox::kMaximumPacketBytes ||
        packet.bytes().size() != packet.size ||
        packet.bytes().front() != iotox::protocol::ratox::kPacketId ||
        all_zero(packet.session_id) || all_zero(packet.principal_id)) {
        __builtin_trap();
    }
    auto decoded = iotox::protocol::ratox::decode(packet.bytes());
    if (!decoded.ok()) __builtin_trap();
    const Frame &frame = decoded.value();
    if (frame.session_id != packet.session_id ||
        frame.principal_id != packet.principal_id ||
        frame.type != packet.type ||
        frame.generation != packet.generation ||
        frame.message_id == 0U) {
        __builtin_trap();
    }
    const std::uint64_t expected_next = frame.type == FrameType::output
        ? frame.sequence + static_cast<std::uint64_t>(frame.payload.size())
        : frame.acknowledgement;
    if (packet.sequence != frame.sequence ||
        packet.next_sequence != expected_next) {
        __builtin_trap();
    }
    return frame;
}

void check_service(
    const RatoxService &service, const RatoxService::Config &config) {
    const auto snapshot = service.snapshot();
    if (!snapshot.enabled || !snapshot.configuration_valid ||
        snapshot.sessions !=
            snapshot.live_sessions + snapshot.retained_session_tombstones ||
        snapshot.running_processes > snapshot.live_sessions ||
        snapshot.attached_sessions > snapshot.live_sessions ||
        snapshot.closing_sessions > snapshot.live_sessions ||
        snapshot.retained_admission_results +
                snapshot.pending_admission_results >
            snapshot.maximum_admission_replay_entries ||
        snapshot.retained_events > config.maximum_events ||
        !snapshot.session_bound_respected ||
        !snapshot.tombstone_bound_respected ||
        !snapshot.admission_replay_entry_bound_respected ||
        !snapshot.admission_replay_byte_bound_respected ||
        !snapshot.outbound_packet_bound_respected ||
        !snapshot.outbound_byte_bound_respected) {
        __builtin_trap();
    }

    const auto events = service.events();
    if (events.size() != snapshot.retained_events) __builtin_trap();
    std::uint64_t prior_ordinal = 0U;
    for (const auto &event : events) {
        if (event.ordinal == 0U || event.ordinal <= prior_ordinal ||
            event.output_base_sequence > event.output_next_sequence) {
            __builtin_trap();
        }
        prior_ordinal = event.ordinal;
    }

    const auto principals = service.live_principals();
    if (principals.size() > config.directory.maximum_sessions_per_device) {
        __builtin_trap();
    }
    for (std::size_t index = 0U; index < principals.size(); ++index) {
        if (all_zero(principals[index]) ||
            std::find(
                principals.begin() + static_cast<std::ptrdiff_t>(index + 1U),
                principals.end(), principals[index]) != principals.end()) {
            __builtin_trap();
        }
    }

    if (const RatoxOutboundPacket *packet = service.peek_outbound()) {
        static_cast<void>(check_outbound(*packet));
    } else if (snapshot.outbound_packets != 0U || snapshot.outbound_bytes != 0U) {
        __builtin_trap();
    }
}

bool send_frame(
    RatoxService &service, const RatoxPeerContext &peer, Frame frame,
    RatoxService::TimePoint now, std::vector<std::uint8_t> &last_packet,
    RatoxPeerContext &last_peer) {
    auto encoded = iotox::protocol::ratox::encode(frame);
    if (!encoded.ok()) return false;
    last_packet = encoded.value();
    last_peer = peer;
    static_cast<void>(service.receive(peer, last_packet, now));
    return true;
}

void mutate_process(FuzzFactory &factory, Cursor &cursor) {
    factory.fail_spawn = (cursor.take() & 0x01U) != 0U;
    factory.null_spawn = (cursor.take() & 0x01U) != 0U;
    factory.next_write_mode = cursor.take();
    factory.next_read_mode = cursor.take();
    factory.next_poll_mode = cursor.take();
    if (factory.states.empty()) return;
    auto &state = *factory.states[cursor.take() % factory.states.size()];
    state.write_mode = cursor.take();
    state.read_mode = cursor.take();
    state.poll_mode = cursor.take();
    const std::uint8_t flags = cursor.take();
    state.fail_resize = (flags & 0x01U) != 0U;
    state.fail_signal = (flags & 0x02U) != 0U;
    state.exit_on_signal = (flags & 0x04U) != 0U;
}

void append_process_output(FuzzFactory &factory, Cursor &cursor) {
    if (factory.states.empty()) return;
    auto &state = *factory.states[cursor.take() % factory.states.size()];
    const std::size_t available =
        kMaximumRetainedProcessBytes -
        std::min(state.output.size(), kMaximumRetainedProcessBytes);
    const std::size_t requested = 1U + cursor.take() % 32U;
    const std::size_t count = std::min({available, requested, cursor.remaining()});
    const auto bytes = cursor.take_bytes(count);
    if (bytes.empty() && available != 0U) {
        state.output.push_back(0xA5U);
    } else {
        state.output.insert(state.output.end(), bytes.begin(), bytes.end());
    }
}

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(
    const std::uint8_t *data, std::size_t size) {
    if (size == 0U) return 0;

    Cursor cursor(data, size);
    const bool exhaust_message_ids = (cursor.take() & 0x01U) != 0U;
    ProfileRegistry registry;
    populate_registry(registry);
    FuzzFactory factory;
    const RatoxService::Config config = service_config(exhaust_message_ids);
    RatoxService service(registry, factory, config);

    std::array<SessionModel, kModelSessions> models{};
    for (std::size_t index = 0U; index < models.size(); ++index) {
        models[index].session = session_id(index);
        models[index].principal = principal_id(index);
        models[index].nonce = attachment_nonce(index, 1U);
        models[index].friend_number = 1U + static_cast<std::uint32_t>(index);
        models[index].online_epoch = 1U + index;
    }

    std::vector<std::uint8_t> last_packet;
    RatoxPeerContext last_peer;
    std::uint64_t tick = 0U;
    std::size_t operations = 0U;
    while (!cursor.empty() && operations++ < 160U) {
        const std::uint8_t operation = cursor.take();
        const std::size_t index = cursor.take() % models.size();
        SessionModel &model = models[index];
        const std::size_t principal = cursor.take() % kModelPrincipals;
        const std::uint8_t peer_selector = cursor.take();
        RatoxPeerContext peer = selected_peer(
            model, principal, peer_selector, true);
        tick += 1U + static_cast<std::uint64_t>(cursor.take() % 7U);
        const auto now = RatoxService::Clock::time_point{} +
            std::chrono::milliseconds{tick};

        switch (operation % 25U) {
            case 0U: {
                const std::size_t count = std::min<std::size_t>(
                    cursor.remaining(), 1U + cursor.take() % 96U);
                static_cast<void>(service.receive(
                    peer, cursor.take_bytes(count), now));
                break;
            }
            case 1U: {
                peer = selected_peer(model, principal, peer_selector, false);
                Frame frame = open_frame(
                    model, peer, cursor.take(), cursor.take(),
                    cursor.take_u16(), cursor.take_u16());
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 2U: {
                Frame frame = attached_frame(
                    FrameType::input, model, cursor.take(), cursor.take());
                const std::uint8_t sequence_selector = cursor.take();
                frame.sequence = model.next_input;
                if ((sequence_selector & 0x01U) != 0U && frame.sequence > 1U) {
                    --frame.sequence;
                }
                if ((sequence_selector & 0x02U) != 0U &&
                    frame.sequence != std::numeric_limits<std::uint64_t>::max()) {
                    ++frame.sequence;
                }
                if ((sequence_selector & 0x04U) != 0U) {
                    frame.acknowledgement = model.next_output;
                }
                const std::size_t count = std::min<std::size_t>(
                    cursor.remaining(), 1U + cursor.take() % 32U);
                const auto bytes = cursor.take_bytes(count);
                frame.payload.assign(bytes.begin(), bytes.end());
                if (frame.payload.empty()) frame.payload.push_back(operation);
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 3U: {
                Frame frame = attached_frame(
                    FrameType::ping, model, cursor.take(), cursor.take());
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 4U: {
                Frame frame = attached_frame(
                    FrameType::resize, model, cursor.take(), cursor.take());
                frame.payload.resize(4U, 0U);
                write_u16(
                    std::span<std::uint8_t>{frame.payload}.first(2U),
                    static_cast<std::uint16_t>(1U + cursor.take_u16() % 512U));
                write_u16(
                    std::span<std::uint8_t>{frame.payload}.subspan(2U, 2U),
                    static_cast<std::uint16_t>(1U + cursor.take_u16() % 256U));
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 5U: {
                Frame frame = attached_frame(
                    FrameType::output_ack, model, cursor.take(), cursor.take());
                frame.acknowledgement = std::max<std::uint64_t>(
                    1U, model.next_output + cursor.take() % 3U);
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 6U: {
                Frame frame = attached_frame(
                    FrameType::detach, model, cursor.take(), cursor.take());
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 7U:
            case 8U: {
                const bool resume = operation % 25U == 8U;
                Frame frame = attached_frame(
                    resume ? FrameType::resume : FrameType::attach,
                    model, cursor.take(), 0U);
                frame.attachment_nonce = attachment_nonce(index, cursor.take());
                if (!resume) frame.generation = 0U;
                frame.payload.resize(16U, 0U);
                write_u64(
                    std::span<std::uint8_t>{frame.payload}.first(8U),
                    std::max<std::uint64_t>(1U, model.next_input));
                write_u64(
                    std::span<std::uint8_t>{frame.payload}.subspan(8U, 8U),
                    std::max<std::uint64_t>(1U, model.next_output));
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 9U: {
                Frame frame = attached_frame(
                    FrameType::close, model, cursor.take(), cursor.take());
                frame.payload.resize(2U, 0U);
                write_u16(frame.payload, cursor.take() % 5U);
                static_cast<void>(send_frame(
                    service, peer, std::move(frame), now,
                    last_packet, last_peer));
                break;
            }
            case 10U:
                static_cast<void>(service.service(now));
                break;
            case 11U:
                if (const RatoxOutboundPacket *packet = service.peek_outbound()) {
                    const Frame frame = check_outbound(*packet);
                    remember_outbound(*packet, frame, models);
                    if (!service.pop_outbound().ok()) __builtin_trap();
                } else if (service.pop_outbound().ok()) {
                    __builtin_trap();
                }
                break;
            case 12U:
                static_cast<void>(service.peer_offline(
                    peer.friend_number, peer.online_epoch, now));
                break;
            case 13U:
                static_cast<void>(service.authority_revoked(
                    peer.friend_number, peer.online_epoch,
                    peer.principal_id, now));
                break;
            case 14U:
                static_cast<void>(service.principal_revoked(
                    peer.principal_id, now));
                break;
            case 15U:
                static_cast<void>(service.shutdown(now));
                break;
            case 16U:
                mutate_process(factory, cursor);
                break;
            case 17U:
                append_process_output(factory, cursor);
                break;
            case 18U:
                static_cast<void>(service.drain_events());
                break;
            case 19U:
                if (!last_packet.empty()) {
                    static_cast<void>(service.receive(last_peer, last_packet, now));
                }
                break;
            case 20U:
                if (!last_packet.empty()) {
                    RatoxPeerContext altered = last_peer;
                    ++altered.online_epoch;
                    if ((cursor.take() & 1U) != 0U) {
                        altered.principal_id = principal_id(principal + 1U);
                    }
                    static_cast<void>(service.receive(altered, last_packet, now));
                }
                break;
            case 21U:
                for (std::size_t cycle = 0U;
                     cycle < 1U + cursor.take() % 4U; ++cycle) {
                    tick += 2U;
                    static_cast<void>(service.service(
                        RatoxService::Clock::time_point{} +
                        std::chrono::milliseconds{tick}));
                }
                break;
            case 22U:
                if (!factory.states.empty()) {
                    auto &state = *factory.states[
                        cursor.take() % factory.states.size()];
                    state.poll_mode = 1U + cursor.take() % 4U;
                    state.read_mode = cursor.take();
                }
                break;
            case 23U: {
                Frame frame = attached_frame(
                    FrameType::input, model, cursor.take(), cursor.take());
                frame.sequence = std::numeric_limits<std::uint64_t>::max() - 1U;
                frame.payload = {1U, 2U, 3U};
                auto encoded = iotox::protocol::ratox::encode(frame);
                if (encoded.ok()) __builtin_trap();
                break;
            }
            case 24U: {
                peer.transcript_confirmed = false;
                const auto bytes = cursor.take_bytes(
                    std::min<std::size_t>(cursor.remaining(), 1200U));
                static_cast<void>(service.receive(peer, bytes, now));
                break;
            }
        }
        check_service(service, config);
    }

    for (std::size_t cycle = 0U; cycle < 8U; ++cycle) {
        tick += 4U;
        static_cast<void>(service.service(
            RatoxService::Clock::time_point{} +
            std::chrono::milliseconds{tick}));
        if (const RatoxOutboundPacket *packet = service.peek_outbound()) {
            const Frame frame = check_outbound(*packet);
            remember_outbound(*packet, frame, models);
            if (!service.pop_outbound().ok()) __builtin_trap();
        }
        check_service(service, config);
    }
    return 0;
}
