#include "test_harness.hpp"

#include "iotox/interactive_service.hpp"

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <memory>
#include <optional>
#include <span>
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
using iotox::interactive::RatoxServiceEvent;
using iotox::interactive::RatoxServiceEventKind;
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

PrincipalId principal(std::uint8_t byte = 0x21U) {
    PrincipalId value{};
    value.front() = byte;
    return value;
}

SessionId session(std::uint8_t byte = 0x31U) {
    SessionId value{};
    value.front() = byte;
    return value;
}

AttachmentNonce nonce(std::uint8_t byte = 0x41U) {
    AttachmentNonce value{};
    value.front() = byte;
    return value;
}

RatoxPeerContext peer(
    std::uint32_t friend_number = 7U,
    std::uint64_t online_epoch = 11U,
    PrincipalId principal_id = principal()) {
    RatoxPeerContext context;
    context.friend_number = friend_number;
    context.online_epoch = online_epoch;
    context.principal_id = principal_id;
    context.transcript_confirmed = true;
    context.feature_negotiated = true;
    context.terminal_authorized = true;
    return context;
}

struct WriteStep {
    IoDisposition disposition{IoDisposition::progress};
    std::size_t bytes{0U};
    bool fail{false};
};

struct FakeState {
    std::deque<WriteStep> writes;
    std::vector<std::uint8_t> written;
    std::vector<std::uint8_t> output;
    std::size_t output_offset{0U};
    std::size_t maximum_read_chunk{static_cast<std::size_t>(-1)};
    bool output_closed{false};
    bool fail_read{false};
    bool fail_resize{false};
    bool fail_signal{false};
    bool fail_poll{false};
    std::vector<Dimensions> resizes;
    std::vector<ProcessSignal> signals;
    std::optional<ProcessSignal> exit_on_signal;
    std::optional<ProcessExit> exit;
    std::size_t destructions{0U};
};

class FakeProcess final : public PtyProcess {
  public:
    explicit FakeProcess(std::shared_ptr<FakeState> state)
        : state_(std::move(state)) {}

    ~FakeProcess() override { ++state_->destructions; }

    Result<WriteResult> write(std::span<const std::uint8_t> bytes) override {
        WriteStep step{IoDisposition::progress, bytes.size(), false};
        if (!state_->writes.empty()) {
            step = state_->writes.front();
            state_->writes.pop_front();
        }
        if (step.fail) {
            return Status{ErrorCode::io_error, "injected service write failure"};
        }
        if (step.disposition != IoDisposition::progress) {
            return WriteResult{step.disposition, 0U};
        }
        const std::size_t amount = std::min(step.bytes, bytes.size());
        state_->written.insert(
            state_->written.end(), bytes.begin(),
            bytes.begin() + static_cast<std::ptrdiff_t>(amount));
        return WriteResult{IoDisposition::progress, amount};
    }

    Result<ReadResult> read(std::size_t maximum_bytes) override {
        if (state_->fail_read) {
            return Status{ErrorCode::io_error, "injected service read failure"};
        }
        if (state_->output_offset < state_->output.size()) {
            const std::size_t amount = std::min({
                maximum_bytes, state_->maximum_read_chunk,
                state_->output.size() - state_->output_offset});
            std::vector<std::uint8_t> bytes(
                state_->output.begin() +
                    static_cast<std::ptrdiff_t>(state_->output_offset),
                state_->output.begin() + static_cast<std::ptrdiff_t>(
                    state_->output_offset + amount));
            state_->output_offset += amount;
            return ReadResult{IoDisposition::progress, std::move(bytes)};
        }
        return ReadResult{
            state_->output_closed
                ? IoDisposition::closed
                : IoDisposition::would_block,
            {}};
    }

    Status resize(const Dimensions &dimensions) override {
        if (state_->fail_resize) {
            return Status{ErrorCode::io_error, "injected service resize failure"};
        }
        state_->resizes.push_back(dimensions);
        return Status::success();
    }

    Status send_signal(ProcessSignal signal) override {
        if (state_->fail_signal) {
            return Status{ErrorCode::io_error, "injected service signal failure"};
        }
        state_->signals.push_back(signal);
        if (state_->exit_on_signal && *state_->exit_on_signal == signal) {
            state_->exit = ProcessExit{ExitKind::signaled, 1, false};
            state_->output_closed = true;
        }
        return Status::success();
    }

    Result<std::optional<ProcessExit>> poll_exit() override {
        if (state_->fail_poll) {
            return Status{ErrorCode::io_error, "injected service poll failure"};
        }
        return state_->exit;
    }

  private:
    std::shared_ptr<FakeState> state_;
};

class FakeFactory final : public PtyProcessFactory {
  public:
    std::vector<std::shared_ptr<FakeState>> states;
    std::size_t spawn_count{0U};
    bool fail_spawn{false};

    Result<std::unique_ptr<PtyProcess>> spawn(
        const ResolvedProfile &) override {
        ++spawn_count;
        if (fail_spawn) {
            return Status{ErrorCode::unavailable, "injected service spawn failure"};
        }
        auto state = std::make_shared<FakeState>();
        states.push_back(state);
        return std::unique_ptr<PtyProcess>(new FakeProcess(state));
    }

    FakeState &latest() const {
        if (states.empty() || !states.back()) {
            iotox::test::fail(
                "FakeFactory::latest", __FILE__, __LINE__,
                "fake PTY factory has no spawned process");
        }
        return *states.back();
    }
};

void populate_registry(
    ProfileRegistry &registry, PrincipalId principal_id = principal()) {
    Profile profile_record;
    profile_record.id = "service-fixture";
    profile_record.enabled = true;
    profile_record.arguments = {"/bin/echo", "fixed"};
    profile_record.working_directory = "/tmp";
    profile_record.environment = {
        EnvironmentEntry{"FIXED", "yes"},
    };
    Binding binding;
    binding.principal_id = principal_id;
    binding.profile_id = profile_record.id;
    binding.enabled = true;
    ProfileStoreData store;
    store.profiles.push_back(std::move(profile_record));
    store.bindings.push_back(std::move(binding));
    const Status replaced = registry.replace(std::move(store));
    if (!replaced.ok()) {
        iotox::test::fail(
            "ProfileRegistry::replace", __FILE__, __LINE__,
            replaced.message());
    }
}

void populate_registry_for_principals(
    ProfileRegistry &registry,
    std::span<const PrincipalId> principal_ids) {
    Profile profile_record;
    profile_record.id = "service-fixture";
    profile_record.enabled = true;
    profile_record.arguments = {"/bin/echo", "fixed"};
    profile_record.working_directory = "/tmp";
    profile_record.environment = {
        EnvironmentEntry{"FIXED", "yes"},
    };
    ProfileStoreData store;
    store.profiles.push_back(std::move(profile_record));
    for (const PrincipalId &principal_id : principal_ids) {
        Binding binding;
        binding.principal_id = principal_id;
        binding.profile_id = "service-fixture";
        binding.enabled = true;
        store.bindings.push_back(std::move(binding));
    }
    const Status replaced = registry.replace(std::move(store));
    if (!replaced.ok()) {
        iotox::test::fail(
            "ProfileRegistry::replace", __FILE__, __LINE__,
            replaced.message());
    }
}

RatoxService::Config service_config() {
    RatoxService::Config config;
    config.enabled = true;
    config.session_incarnation = 1U;
    config.maximum_outbound_packets = 32U;
    config.maximum_outbound_bytes = 32U * 1200U;
    config.maximum_input_write_operations = 8U;
    config.maximum_output_read_operations = 8U;
    config.maximum_output_frames = 8U;
    config.terminal_read_bytes = 4096U;
    return config;
}

Frame open_frame(
    const RatoxPeerContext &context,
    SessionId session_id = session(),
    AttachmentNonce attachment_nonce = nonce(),
    std::uint64_t message_id = 101U) {
    Frame frame;
    frame.type = FrameType::open;
    frame.message_id = message_id;
    frame.session_id = session_id;
    frame.principal_id = context.principal_id;
    frame.attachment_nonce = attachment_nonce;
    frame.payload.resize(12U, 0U);
    frame.payload[0U] = 1U;
    write_u16(std::span<std::uint8_t>{frame.payload}.subspan(2U, 2U), 80U);
    write_u16(std::span<std::uint8_t>{frame.payload}.subspan(4U, 2U), 24U);
    return frame;
}

std::vector<std::uint8_t> encode_frame(const Frame &frame) {
    auto encoded = iotox::protocol::ratox::encode(frame);
    if (!encoded.ok()) {
        iotox::test::fail(
            "ratox::encode", __FILE__, __LINE__, encoded.status().message());
    }
    return std::move(encoded.value());
}

Frame take_frame(RatoxService &service) {
    const auto *outbound = service.peek_outbound();
    if (outbound == nullptr) {
        iotox::test::fail(
            "RatoxService::peek_outbound", __FILE__, __LINE__,
            "expected one retained outbound packet");
    }
    auto decoded = iotox::protocol::ratox::decode(outbound->bytes());
    if (!decoded.ok()) {
        iotox::test::fail(
            "ratox::decode", __FILE__, __LINE__,
            decoded.status().message());
    }
    const Status popped = service.pop_outbound();
    IOTOX_CHECK(popped.ok());
    return std::move(decoded.value());
}

const RatoxOutboundPacket &require_front(const RatoxService &service) {
    const auto *outbound = service.peek_outbound();
    if (outbound == nullptr) {
        iotox::test::fail(
            "RatoxService::peek_outbound", __FILE__, __LINE__,
            "expected one retained outbound packet");
    }
    return *outbound;
}

std::vector<std::uint8_t> copy_front_bytes(RatoxService &service) {
    const auto &outbound = require_front(service);
    return std::vector<std::uint8_t>(
        outbound.bytes().begin(), outbound.bytes().end());
}

struct Opened {
    Frame response;
    Frame attached;
};

Opened open_service(
    RatoxService &service, const RatoxPeerContext &context,
    RatoxService::TimePoint now = RatoxService::Clock::time_point{}) {
    const Frame request = open_frame(context);
    const Status received = service.receive(context, encode_frame(request), now);
    IOTOX_CHECK_MSG(received.ok(), received.message());
    Frame response = take_frame(service);
    IOTOX_CHECK(response.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(response.payload) == 0U);
    Frame attached = request;
    attached.incarnation = response.incarnation;
    attached.generation = response.generation;
    return Opened{std::move(response), std::move(attached)};
}

Frame attached_request(
    FrameType type, const Frame &base, std::uint64_t message_id) {
    Frame frame;
    frame.type = type;
    frame.message_id = message_id;
    frame.session_id = base.session_id;
    frame.principal_id = base.principal_id;
    frame.attachment_nonce = base.attachment_nonce;
    frame.incarnation = base.incarnation;
    frame.generation = base.generation;
    return frame;
}

}  // namespace

IOTOX_TEST("Ratox service is disabled by default and rejects unconfirmed epochs") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService disabled(registry, factory);
    const RatoxPeerContext context = peer();
    const auto packet = encode_frame(open_frame(context));
    const Status gate = disabled.receive(
        context, packet, RatoxService::Clock::time_point{});
    IOTOX_CHECK(!gate.ok());
    IOTOX_CHECK(gate.code() == ErrorCode::unsupported);
    IOTOX_CHECK(factory.spawn_count == 0U);

    RatoxService service(registry, factory, service_config());
    RatoxPeerContext unconfirmed = context;
    unconfirmed.transcript_confirmed = false;
    const Status transcript = service.receive(
        unconfirmed, packet, RatoxService::Clock::time_point{});
    IOTOX_CHECK(!transcript.ok());
    IOTOX_CHECK(transcript.code() == ErrorCode::unavailable);
    IOTOX_CHECK(factory.spawn_count == 0U);
}

IOTOX_TEST("Ratox outbound authority fences survive exact admission replay") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const auto now = RatoxService::Clock::time_point{};

    RatoxPeerContext unauthorized = peer();
    unauthorized.terminal_authorized = false;
    const std::vector<std::uint8_t> denied_request =
        encode_frame(open_frame(unauthorized));
    IOTOX_CHECK(service.receive(unauthorized, denied_request, now).ok());
    const auto &denied = require_front(service);
    IOTOX_CHECK(!denied.terminal_authority_required);
    const std::vector<std::uint8_t> frozen_denial(
        denied.bytes().begin(), denied.bytes().end());
    IOTOX_CHECK(service.pop_outbound().ok());

    IOTOX_CHECK(service.receive(unauthorized, denied_request, now).ok());
    const auto &replayed_denial = require_front(service);
    IOTOX_CHECK(!replayed_denial.terminal_authority_required);
    IOTOX_CHECK(std::equal(
        frozen_denial.begin(), frozen_denial.end(),
        replayed_denial.bytes().begin(), replayed_denial.bytes().end()));
    IOTOX_CHECK(service.pop_outbound().ok());

    const RatoxPeerContext authorized = peer(8U, 12U);
    const Frame accepted_request = open_frame(
        authorized, session(0x32U), nonce(0x42U), 102U);
    IOTOX_CHECK(service.receive(
        authorized, encode_frame(accepted_request), now).ok());
    const auto &accepted = require_front(service);
    IOTOX_CHECK(accepted.terminal_authority_required);
    const Frame accepted_result = take_frame(service);
    IOTOX_CHECK(accepted_result.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(accepted_result.payload) == 0U);
    IOTOX_CHECK(factory.spawn_count == 1U);
}

IOTOX_TEST("Ratox service rejects incoherent replay and work-loop bounds") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    const std::size_t admission_reservation =
        iotox::protocol::ratox::kHeaderBytes + 16U +
        iotox::protocol::ratox::kMaximumPacketBytes;

    RatoxService::Config zero_incarnation = service_config();
    zero_incarnation.session_incarnation = 0U;
    RatoxService zero_service(registry, factory, zero_incarnation);
    IOTOX_CHECK(!zero_service.snapshot().configuration_valid);

    RatoxService::Config too_small = service_config();
    too_small.maximum_admission_replay_bytes = admission_reservation - 1U;
    RatoxService small_service(registry, factory, too_small);
    IOTOX_CHECK(!small_service.snapshot().configuration_valid);
    const Status small_status = small_service.service(
        RatoxService::Clock::time_point{});
    IOTOX_CHECK(!small_status.ok());
    IOTOX_CHECK(small_status.code() == ErrorCode::invalid_argument);

    RatoxService::Config impossible_slack = service_config();
    impossible_slack.maximum_admission_replay_entries = 1U;
    impossible_slack.maximum_admission_replay_bytes =
        admission_reservation + 1U;
    RatoxService slack_service(registry, factory, impossible_slack);
    IOTOX_CHECK(!slack_service.snapshot().configuration_valid);

    RatoxService::Config unbounded_work = service_config();
    unbounded_work.maximum_output_frames = 4097U;
    RatoxService work_service(registry, factory, unbounded_work);
    IOTOX_CHECK(!work_service.snapshot().configuration_valid);
    IOTOX_CHECK(factory.spawn_count == 0U);
}

IOTOX_TEST("Ratox OPEN atomically spawns once and replays the exact result") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService::Config config = service_config();
    config.session_incarnation = 99U;
    RatoxService service(registry, factory, config);
    const RatoxPeerContext context = peer();
    const auto request = encode_frame(open_frame(context));

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(factory.spawn_count == 1U);
    const auto first = copy_front_bytes(service);
    const Frame first_frame = take_frame(service);
    IOTOX_CHECK(first_frame.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(first_frame.payload) == 0U);
    IOTOX_CHECK(first_frame.incarnation == 99U);
    IOTOX_CHECK(first_frame.generation == 1U);

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(factory.spawn_count == 1U);
    const auto replay = copy_front_bytes(service);
    IOTOX_CHECK(replay == first);
    static_cast<void>(take_frame(service));

    const auto snapshot = service.snapshot();
    IOTOX_CHECK(snapshot.sessions == 1U);
    IOTOX_CHECK(snapshot.running_processes == 1U);
    IOTOX_CHECK(snapshot.retained_admission_results == 1U);
    IOTOX_CHECK(snapshot.pending_admission_results == 0U);
}

IOTOX_TEST("Ratox unauthorized OPEN is a retained denial with no profile effect") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    RatoxPeerContext context = peer();
    context.terminal_authorized = false;
    const auto request = encode_frame(open_frame(context));

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    const auto first = copy_front_bytes(service);
    const Frame denial = take_frame(service);
    IOTOX_CHECK(denial.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(denial.payload) == 1U);
    IOTOX_CHECK(denial.incarnation == 0U);
    IOTOX_CHECK(denial.generation == 0U);
    IOTOX_CHECK(factory.spawn_count == 0U);

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == first);
    IOTOX_CHECK(factory.spawn_count == 0U);
}

IOTOX_TEST("Ratox revoked RESUME receives one replayable authority-free denial") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext authorized = peer();
    Opened opened = open_service(service, authorized);
    auto &process = factory.latest();

    RatoxPeerContext revoked = authorized;
    revoked.terminal_authorized = false;
    Frame resume = attached_request(
        FrameType::resume, opened.attached, 153U);
    resume.payload.resize(16U, 0U);
    write_u64(std::span<std::uint8_t>{resume.payload}.first(8U), 1U);
    write_u64(
        std::span<std::uint8_t>{resume.payload}.subspan(8U, 8U), 1U);
    const auto packet = encode_frame(resume);

    IOTOX_CHECK(service.receive(
        revoked, packet, RatoxService::Clock::time_point{}).ok());
    const auto first = copy_front_bytes(service);
    const auto *outbound = service.peek_outbound();
    IOTOX_CHECK(outbound != nullptr);
    IOTOX_CHECK(!outbound->terminal_authority_required);
    const Frame denied = take_frame(service);
    IOTOX_CHECK(denied.type == FrameType::resume_result);
    IOTOX_CHECK(read_u16(denied.payload) == 1U);
    IOTOX_CHECK(process.signals ==
                std::vector<ProcessSignal>({ProcessSignal::hangup}));

    IOTOX_CHECK(service.receive(
        revoked, packet, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == first);
    const auto *replayed = service.peek_outbound();
    IOTOX_CHECK(replayed != nullptr);
    IOTOX_CHECK(!replayed->terminal_authority_required);
}

IOTOX_TEST("Ratox failed PTY spawn is retained exactly and never retried") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    factory.fail_spawn = true;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    const auto request = encode_frame(open_frame(context));

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    const auto first = copy_front_bytes(service);
    const Frame denial = take_frame(service);
    IOTOX_CHECK(denial.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(denial.payload) == 7U);
    IOTOX_CHECK(factory.spawn_count == 1U);
    IOTOX_CHECK(service.snapshot().live_sessions == 0U);

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == first);
    IOTOX_CHECK(factory.spawn_count == 1U);
}

IOTOX_TEST("Ratox absent ATTACH and RESUME denials are admission replay safe") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();

    Frame attach;
    attach.type = FrameType::attach;
    attach.message_id = 150U;
    attach.session_id = session(0x71U);
    attach.principal_id = context.principal_id;
    attach.attachment_nonce = nonce(0x72U);
    attach.incarnation = 1U;
    attach.payload.resize(16U, 0U);
    write_u64(std::span<std::uint8_t>{attach.payload}.first(8U), 1U);
    write_u64(std::span<std::uint8_t>{attach.payload}.subspan(8U, 8U), 1U);
    const auto attach_packet = encode_frame(attach);

    IOTOX_CHECK(service.receive(
        context, attach_packet, RatoxService::Clock::time_point{}).ok());
    const auto first = copy_front_bytes(service);
    const Frame denied = take_frame(service);
    IOTOX_CHECK(denied.type == FrameType::attach_result);
    IOTOX_CHECK(read_u16(denied.payload) == 4U);

    IOTOX_CHECK(service.receive(
        context, attach_packet, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == first);
    static_cast<void>(take_frame(service));

    Frame conflicting = attach;
    conflicting.attachment_nonce = nonce(0x73U);
    const Status conflict = service.receive(
        context, encode_frame(conflicting),
        RatoxService::Clock::time_point{});
    IOTOX_CHECK(!conflict.ok());
    IOTOX_CHECK(conflict.code() == ErrorCode::protocol_error);

    Frame resume = attach;
    resume.type = FrameType::resume;
    resume.message_id = 151U;
    resume.generation = 9U;
    const auto resume_packet = encode_frame(resume);
    IOTOX_CHECK(service.receive(
        context, resume_packet, RatoxService::Clock::time_point{}).ok());
    const auto resume_first = copy_front_bytes(service);
    const Frame resume_denied = take_frame(service);
    IOTOX_CHECK(resume_denied.type == FrameType::resume_result);
    IOTOX_CHECK(read_u16(resume_denied.payload) == 4U);
    IOTOX_CHECK(resume_denied.generation == resume.generation);
    IOTOX_CHECK(service.receive(
        context, resume_packet, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == resume_first);
    static_cast<void>(take_frame(service));
    IOTOX_CHECK(service.snapshot().retained_admission_results == 2U);

    RatoxPeerContext unauthorized = context;
    unauthorized.terminal_authorized = false;
    Frame unauthorized_attach = attach;
    unauthorized_attach.message_id = 152U;
    unauthorized_attach.session_id = session(0x74U);
    unauthorized_attach.attachment_nonce = nonce(0x75U);
    const auto unauthorized_packet = encode_frame(unauthorized_attach);
    IOTOX_CHECK(service.receive(
        unauthorized, unauthorized_packet,
        RatoxService::Clock::time_point{}).ok());
    const auto unauthorized_first = copy_front_bytes(service);
    const Frame unauthorized_denied = take_frame(service);
    IOTOX_CHECK(unauthorized_denied.type == FrameType::attach_result);
    IOTOX_CHECK(read_u16(unauthorized_denied.payload) == 1U);
    IOTOX_CHECK(service.receive(
        unauthorized, unauthorized_packet,
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == unauthorized_first);
    IOTOX_CHECK(factory.spawn_count == 0U);
}

IOTOX_TEST("Ratox queue saturation denies OPEN before spawn and replays later") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService::Config config = service_config();
    config.maximum_outbound_packets = 1U;
    config.maximum_outbound_bytes =
        iotox::protocol::ratox::kMaximumPacketBytes;
    RatoxService service(registry, factory, config);

    RatoxPeerContext denied_context = peer();
    denied_context.terminal_authorized = false;
    IOTOX_CHECK(service.receive(
        denied_context,
        encode_frame(open_frame(
            denied_context, session(0x61U), nonce(0x61U), 161U)),
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 1U);

    const RatoxPeerContext context = peer();
    const auto request = encode_frame(open_frame(
        context, session(0x62U), nonce(0x62U), 162U));
    const Status saturated = service.receive(
        context, request, RatoxService::Clock::time_point{});
    IOTOX_CHECK(!saturated.ok());
    IOTOX_CHECK(saturated.code() == ErrorCode::resource_exhausted);
    IOTOX_CHECK(factory.spawn_count == 0U);

    static_cast<void>(take_frame(service));
    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    const Frame replayed = take_frame(service);
    IOTOX_CHECK(replayed.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(replayed.payload) == 6U);
    IOTOX_CHECK(factory.spawn_count == 0U);
}

IOTOX_TEST("Ratox staged input ACK advances only after whole PTY commitment") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &state = factory.latest();
    state.writes.push_back(WriteStep{IoDisposition::progress, 2U, false});
    state.writes.push_back(WriteStep{IoDisposition::would_block, 0U, false});
    state.writes.push_back(WriteStep{IoDisposition::progress, 2U, false});

    Frame input = attached_request(FrameType::input, opened.attached, 102U);
    input.sequence = 1U;
    input.payload = {0x10U, 0x20U, 0x30U, 0x40U};
    IOTOX_CHECK(service.receive(
        context, encode_frame(input), RatoxService::Clock::time_point{}).ok());

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(state.written == std::vector<std::uint8_t>({0x10U, 0x20U}));
    IOTOX_CHECK(service.peek_outbound() == nullptr);

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(state.written == input.payload);
    const Frame ack = take_frame(service);
    IOTOX_CHECK(ack.type == FrameType::input_ack);
    IOTOX_CHECK(ack.acknowledgement == 5U);

    const auto events = service.events();
    const auto staged = std::find_if(
        events.begin(), events.end(), [](const RatoxServiceEvent &event) {
            return event.kind == RatoxServiceEventKind::input_staged;
        });
    const auto committed = std::find_if(
        events.begin(), events.end(), [](const RatoxServiceEvent &event) {
            return event.kind == RatoxServiceEventKind::input_committed;
        });
    IOTOX_CHECK(staged != events.end());
    IOTOX_CHECK(committed != events.end());
    IOTOX_CHECK(staged->message_id == input.message_id);
    IOTOX_CHECK(committed->message_id == input.message_id);
    IOTOX_CHECK(staged->sequence == 1U);
    IOTOX_CHECK(staged->next_sequence == 5U);
    IOTOX_CHECK(staged->event_bytes == 4U);
    IOTOX_CHECK(committed->sequence == 1U);
    IOTOX_CHECK(committed->next_sequence == 5U);
    IOTOX_CHECK(committed->event_bytes == 4U);

    IOTOX_CHECK(service.receive(
        context, encode_frame(input), RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    const Frame duplicate_ack = take_frame(service);
    IOTOX_CHECK(duplicate_ack.type == FrameType::input_ack);
    IOTOX_CHECK(duplicate_ack.acknowledgement == 5U);
    IOTOX_CHECK(state.written == input.payload);
}

IOTOX_TEST("Ratox partial PTY write failure never acknowledges uncertain input") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &state = factory.latest();
    state.writes.push_back(WriteStep{IoDisposition::progress, 2U, false});
    state.writes.push_back(WriteStep{IoDisposition::progress, 0U, true});

    Frame input = attached_request(FrameType::input, opened.attached, 103U);
    input.sequence = 1U;
    input.payload = {0x10U, 0x20U, 0x30U, 0x40U};
    IOTOX_CHECK(service.receive(
        context, encode_frame(input), RatoxService::Clock::time_point{}).ok());

    const Status failed = service.service(RatoxService::Clock::time_point{});
    IOTOX_CHECK(!failed.ok());
    IOTOX_CHECK(failed.code() == ErrorCode::io_error);
    IOTOX_CHECK(state.written == std::vector<std::uint8_t>({0x10U, 0x20U}));

    bool saw_ack = false;
    bool saw_exit = false;
    while (service.peek_outbound() != nullptr) {
        const Frame frame = take_frame(service);
        saw_ack = saw_ack || frame.type == FrameType::input_ack;
        saw_exit = saw_exit || frame.type == FrameType::exit_status;
    }
    IOTOX_CHECK(!saw_ack);
    IOTOX_CHECK(saw_exit);

    const auto snapshot = service.snapshot();
    IOTOX_CHECK(snapshot.running_processes == 0U);
    IOTOX_CHECK(snapshot.live_sessions == 0U);
    IOTOX_CHECK(snapshot.retained_session_tombstones == 1U);
    IOTOX_CHECK(snapshot.pending_admission_results == 0U);
}

IOTOX_TEST("Ratox ATTACH advances generation and fences delayed controller input") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    const Frame old_attachment = opened.attached;

    Frame attach;
    attach.type = FrameType::attach;
    attach.message_id = 201U;
    attach.session_id = old_attachment.session_id;
    attach.principal_id = old_attachment.principal_id;
    attach.attachment_nonce = nonce(0x42U);
    attach.incarnation = old_attachment.incarnation;
    attach.payload.resize(16U, 0U);
    write_u64(std::span<std::uint8_t>{attach.payload}.first(8U), 1U);
    write_u64(std::span<std::uint8_t>{attach.payload}.subspan(8U, 8U), 1U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(attach), RatoxService::Clock::time_point{}).ok());
    const Frame attached = take_frame(service);
    IOTOX_CHECK(attached.type == FrameType::attach_result);
    IOTOX_CHECK(read_u16(attached.payload) == 0U);
    IOTOX_CHECK(attached.generation == old_attachment.generation + 1U);

    Frame stale = attached_request(FrameType::input, old_attachment, 202U);
    stale.sequence = 1U;
    stale.payload = {0xAAU};
    const Status rejected = service.receive(
        context, encode_frame(stale), RatoxService::Clock::time_point{});
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.code() == ErrorCode::protocol_error);
    IOTOX_CHECK(factory.latest().written.empty());

    Frame current = stale;
    current.message_id = 203U;
    current.attachment_nonce = attach.attachment_nonce;
    current.generation = attached.generation;
    IOTOX_CHECK(service.receive(
        context, encode_frame(current), RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    const Frame ack = take_frame(service);
    IOTOX_CHECK(ack.type == FrameType::input_ack);
    IOTOX_CHECK(factory.latest().written == current.payload);
}

IOTOX_TEST("Ratox peer offline detaches routing while preserving the PTY for resume") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    RatoxPeerContext first_peer = peer(7U, 11U);
    Opened opened = open_service(service, first_peer);
    auto &process = factory.latest();
    process.output = {1U, 2U, 3U};

    IOTOX_CHECK(service.peer_offline(
        first_peer.friend_number, first_peer.online_epoch,
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().running_processes == 1U);
    IOTOX_CHECK(service.snapshot().attached_sessions == 0U);
    IOTOX_CHECK(process.destructions == 0U);
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.peek_outbound() == nullptr);

    RatoxPeerContext second_peer = peer(7U, 12U);
    Frame resume;
    resume.type = FrameType::resume;
    resume.message_id = 301U;
    resume.session_id = opened.attached.session_id;
    resume.principal_id = opened.attached.principal_id;
    resume.attachment_nonce = nonce(0x44U);
    resume.incarnation = opened.attached.incarnation;
    resume.generation = opened.attached.generation;
    resume.payload.resize(16U, 0U);
    write_u64(std::span<std::uint8_t>{resume.payload}.first(8U), 1U);
    write_u64(std::span<std::uint8_t>{resume.payload}.subspan(8U, 8U), 1U);
    IOTOX_CHECK(service.receive(
        second_peer, encode_frame(resume),
        RatoxService::Clock::time_point{}).ok());
    const Frame resumed = take_frame(service);
    IOTOX_CHECK(resumed.type == FrameType::resume_result);
    IOTOX_CHECK(read_u16(resumed.payload) == 0U);
    IOTOX_CHECK(resumed.generation == opened.attached.generation + 1U);

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    const Frame output = take_frame(service);
    IOTOX_CHECK(output.type == FrameType::output);
    IOTOX_CHECK(output.payload == process.output);
}

IOTOX_TEST("Ratox output eviction emits an explicit gap before the retained suffix") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService::Config config = service_config();
    config.directory.session.output.maximum_bytes = 4U;
    RatoxService service(registry, factory, config);
    const RatoxPeerContext context = peer();
    static_cast<void>(open_service(service, context));
    auto &process = factory.latest();
    process.output = {1U, 2U, 3U, 4U, 5U, 6U};
    process.output_closed = false;

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    const Frame gap = take_frame(service);
    IOTOX_CHECK(gap.type == FrameType::output_gap);
    IOTOX_CHECK(gap.sequence == 3U);
    IOTOX_CHECK(gap.acknowledgement == 7U);
    const Frame output = take_frame(service);
    IOTOX_CHECK(output.type == FrameType::output);
    IOTOX_CHECK(output.sequence == 3U);
    IOTOX_CHECK(output.payload == std::vector<std::uint8_t>({3U, 4U, 5U, 6U}));
}

IOTOX_TEST("Ratox PING replay is byte exact and does not repeat a side effect") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    Frame ping = attached_request(FrameType::ping, opened.attached, 401U);
    const auto request = encode_frame(ping);

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    const auto first = copy_front_bytes(service);
    const Frame pong = take_frame(service);
    IOTOX_CHECK(pong.type == FrameType::pong);
    IOTOX_CHECK(pong.correlation_id == ping.message_id);

    IOTOX_CHECK(service.receive(
        context, request, RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == first);
}

IOTOX_TEST("Ratox authority revocation fences staged bytes before another PTY write") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &process = factory.latest();
    process.writes.push_back(WriteStep{IoDisposition::would_block, 0U, false});

    Frame input = attached_request(FrameType::input, opened.attached, 501U);
    input.sequence = 1U;
    input.payload = {9U, 8U, 7U};
    IOTOX_CHECK(service.receive(
        context, encode_frame(input), RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(process.written.empty());

    const Status revoked = service.authority_revoked(
        context.friend_number, context.online_epoch,
        context.principal_id, RatoxService::Clock::time_point{});
    IOTOX_CHECK(!revoked.ok());
    IOTOX_CHECK(revoked.code() == ErrorCode::unavailable);
    IOTOX_CHECK(process.destructions == 1U);
    IOTOX_CHECK(service.snapshot().running_processes == 0U);
    IOTOX_CHECK(process.written.empty());
}

IOTOX_TEST("Ratox authority revocation drops retained bytes and blocks later replay") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &process = factory.latest();
    process.output = {0xA1U, 0xA2U, 0xA3U};
    process.exit_on_signal = ProcessSignal::hangup;

    IOTOX_CHECK(service.service(
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.peek_outbound() != nullptr);
    IOTOX_CHECK(service.snapshot().retained_admission_results == 1U);

    const Status revoked = service.authority_revoked(
        context.friend_number, context.online_epoch,
        context.principal_id, RatoxService::Clock::time_point{});
    IOTOX_CHECK_MSG(revoked.ok(), revoked.message());
    IOTOX_CHECK(service.peek_outbound() == nullptr);
    IOTOX_CHECK(service.snapshot().retained_admission_results == 0U);
    IOTOX_CHECK(service.live_principals().empty());
    IOTOX_CHECK(process.signals ==
                std::vector<ProcessSignal>({ProcessSignal::hangup}));

    Frame ping = attached_request(FrameType::ping, opened.attached, 502U);
    const Status replay = service.receive(
        context, encode_frame(ping), RatoxService::Clock::time_point{});
    IOTOX_CHECK(!replay.ok());
    IOTOX_CHECK(replay.code() == ErrorCode::unavailable);
    IOTOX_CHECK(service.peek_outbound() == nullptr);

    IOTOX_CHECK(service.service(
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().running_processes == 0U);
    IOTOX_CHECK(service.peek_outbound() == nullptr);
}

IOTOX_TEST("Ratox exact-route authority loss preserves same-principal sessions on other epochs") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const PrincipalId shared_principal = principal();
    const RatoxPeerContext first_peer = peer(7U, 11U, shared_principal);
    const RatoxPeerContext second_peer = peer(8U, 12U, shared_principal);

    Opened first = open_service(service, first_peer);
    auto &first_process = factory.latest();

    const Frame second_open = open_frame(
        second_peer, session(0x32U), nonce(0x42U), 102U);
    IOTOX_CHECK(service.receive(
        second_peer, encode_frame(second_open),
        RatoxService::Clock::time_point{}).ok());
    const Frame second_result = take_frame(service);
    IOTOX_CHECK(second_result.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(second_result.payload) == 0U);
    auto &second_process = factory.latest();

    Frame second_attached = second_open;
    second_attached.incarnation = second_result.incarnation;
    second_attached.generation = second_result.generation;
    Frame second_ping = attached_request(
        FrameType::ping, second_attached, 503U);
    IOTOX_CHECK(service.receive(
        second_peer, encode_frame(second_ping),
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 1U);
    IOTOX_CHECK(service.snapshot().retained_admission_results == 2U);

    RatoxPeerContext unauthorized_first = first_peer;
    unauthorized_first.terminal_authorized = false;
    Frame first_ping = attached_request(
        FrameType::ping, first.attached, 504U);
    const Status denied = service.receive(
        unauthorized_first, encode_frame(first_ping),
        RatoxService::Clock::time_point{});
    IOTOX_CHECK(!denied.ok());
    IOTOX_CHECK(denied.code() == ErrorCode::unavailable);

    IOTOX_CHECK(first_process.signals ==
                std::vector<ProcessSignal>({ProcessSignal::hangup}));
    IOTOX_CHECK(second_process.signals.empty());
    const auto snapshot = service.snapshot();
    IOTOX_CHECK(snapshot.running_processes == 2U);
    IOTOX_CHECK(snapshot.live_sessions == 2U);
    IOTOX_CHECK(snapshot.retained_admission_results == 1U);
    IOTOX_CHECK(snapshot.outbound_packets == 1U);
    const auto &remaining = require_front(service);
    IOTOX_CHECK(remaining.friend_number == second_peer.friend_number);
    IOTOX_CHECK(remaining.online_epoch == second_peer.online_epoch);
    IOTOX_CHECK(remaining.principal_id == shared_principal);
    const auto live = service.live_principals();
    IOTOX_CHECK(live.size() == 1U);
    IOTOX_CHECK(live.front() == shared_principal);
}

IOTOX_TEST("Ratox stale routes cannot replay controls retarget authority or poison reservations") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const PrincipalId shared_principal = principal();
    const RatoxPeerContext owner_route = peer(7U, 11U, shared_principal);
    const RatoxPeerContext stale_route = peer(8U, 12U, shared_principal);
    Opened opened = open_service(service, owner_route);
    auto &process = factory.latest();
    process.exit_on_signal = ProcessSignal::hangup;

    Frame ping = attached_request(FrameType::ping, opened.attached, 505U);
    const auto ping_packet = encode_frame(ping);
    IOTOX_CHECK(service.receive(
        owner_route, ping_packet,
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(take_frame(service).type == FrameType::pong);

    const Status cross_route_replay = service.receive(
        stale_route, ping_packet,
        RatoxService::Clock::time_point{});
    IOTOX_CHECK(!cross_route_replay.ok());
    IOTOX_CHECK(cross_route_replay.code() == ErrorCode::protocol_error);
    IOTOX_CHECK(service.peek_outbound() == nullptr);

    Frame resize = attached_request(
        FrameType::resize, opened.attached, 506U);
    resize.payload.resize(4U, 0U);
    write_u16(std::span<std::uint8_t>{resize.payload}.first(2U), 100U);
    write_u16(
        std::span<std::uint8_t>{resize.payload}.subspan(2U, 2U), 40U);
    const auto resize_packet = encode_frame(resize);
    for (std::size_t attempt = 0U; attempt < 2U; ++attempt) {
        const Status rejected = service.receive(
            stale_route, resize_packet,
            RatoxService::Clock::time_point{});
        IOTOX_CHECK(!rejected.ok());
        IOTOX_CHECK(rejected.code() == ErrorCode::protocol_error);
    }
    IOTOX_CHECK(process.resizes.empty());

    const Status wrong_route = service.authority_revoked(
        stale_route.friend_number, stale_route.online_epoch,
        shared_principal, RatoxService::Clock::time_point{});
    IOTOX_CHECK(!wrong_route.ok());
    IOTOX_CHECK(wrong_route.code() == ErrorCode::not_found);
    IOTOX_CHECK(process.signals.empty());

    const Status owning_route = service.authority_revoked(
        owner_route.friend_number, owner_route.online_epoch,
        shared_principal, RatoxService::Clock::time_point{});
    IOTOX_CHECK_MSG(owning_route.ok(), owning_route.message());
    IOTOX_CHECK(process.signals ==
                std::vector<ProcessSignal>({ProcessSignal::hangup}));
}

IOTOX_TEST("Ratox principal revocation closes detached sessions without touching peers") {
    ProfileRegistry registry;
    const std::array<PrincipalId, 2U> principals{
        principal(0x21U), principal(0x22U)};
    populate_registry_for_principals(registry, principals);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext first_peer = peer(7U, 11U, principals[0U]);
    const RatoxPeerContext second_peer = peer(8U, 12U, principals[1U]);

    static_cast<void>(open_service(service, first_peer));
    auto &first_process = factory.latest();

    const Frame second_open = open_frame(
        second_peer, session(0x32U), nonce(0x42U), 102U);
    IOTOX_CHECK(service.receive(
        second_peer, encode_frame(second_open),
        RatoxService::Clock::time_point{}).ok());
    const Frame second_result = take_frame(service);
    IOTOX_CHECK(second_result.type == FrameType::open_result);
    IOTOX_CHECK(read_u16(second_result.payload) == 0U);
    auto &second_process = factory.latest();

    IOTOX_CHECK(service.peer_offline(
        first_peer.friend_number, first_peer.online_epoch,
        RatoxService::Clock::time_point{}).ok());
    const auto live_before = service.live_principals();
    IOTOX_CHECK(live_before.size() == 2U);
    IOTOX_CHECK(std::find(
        live_before.begin(), live_before.end(), principals[0U]) !=
        live_before.end());
    IOTOX_CHECK(std::find(
        live_before.begin(), live_before.end(), principals[1U]) !=
        live_before.end());

    first_process.exit_on_signal = ProcessSignal::hangup;
    const Status revoked = service.principal_revoked(
        principals[0U], RatoxService::Clock::time_point{});
    IOTOX_CHECK_MSG(revoked.ok(), revoked.message());
    IOTOX_CHECK(first_process.signals ==
                std::vector<ProcessSignal>({ProcessSignal::hangup}));
    IOTOX_CHECK(second_process.signals.empty());

    const auto live_after = service.live_principals();
    IOTOX_CHECK(live_after.size() == 1U);
    IOTOX_CHECK(live_after.front() == principals[1U]);
    IOTOX_CHECK(service.service(
        RatoxService::Clock::time_point{}).ok());
    const auto snapshot = service.snapshot();
    IOTOX_CHECK(snapshot.running_processes == 1U);
    IOTOX_CHECK(snapshot.live_sessions == 1U);
    IOTOX_CHECK(snapshot.retained_session_tombstones == 1U);

    const Status duplicate = service.principal_revoked(
        principals[0U], RatoxService::Clock::time_point{});
    IOTOX_CHECK(!duplicate.ok());
    IOTOX_CHECK(duplicate.code() == ErrorCode::not_found);
}

IOTOX_TEST("Ratox controller CLOSE drains admitted input before signaling HUP") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &process = factory.latest();
    process.writes.push_back(WriteStep{IoDisposition::would_block, 0U, false});
    process.writes.push_back(WriteStep{IoDisposition::progress, 3U, false});
    process.exit_on_signal = ProcessSignal::hangup;

    Frame input = attached_request(FrameType::input, opened.attached, 601U);
    input.sequence = 1U;
    input.payload = {1U, 2U, 3U};
    IOTOX_CHECK(service.receive(
        context, encode_frame(input), RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(process.written.empty());

    Frame close = attached_request(FrameType::close, opened.attached, 602U);
    close.payload.resize(2U, 0U);
    write_u16(close.payload, 1U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(close), RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(process.signals.empty());

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(process.written == input.payload);
    IOTOX_CHECK(!process.signals.empty());
    IOTOX_CHECK(process.signals.front() == ProcessSignal::hangup);

    bool saw_ack = false;
    bool saw_exit = false;
    while (service.peek_outbound() != nullptr) {
        const Frame frame = take_frame(service);
        saw_ack = saw_ack || frame.type == FrameType::input_ack;
        saw_exit = saw_exit || frame.type == FrameType::exit_status;
    }
    IOTOX_CHECK(saw_ack);
    IOTOX_CHECK(saw_exit);
    IOTOX_CHECK(service.snapshot().running_processes == 0U);
}

IOTOX_TEST("Ratox outbound packets remain retained until explicit transport acceptance") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &process = factory.latest();
    process.output = {0xA1U, 0xA2U};
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());

    const auto first = copy_front_bytes(service);
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(copy_front_bytes(service) == first);
    const Frame output = take_frame(service);
    IOTOX_CHECK(output.type == FrameType::output);
    IOTOX_CHECK(output.payload == process.output);

    Frame ack = attached_request(FrameType::output_ack, opened.attached, 701U);
    ack.acknowledgement = 3U;
    IOTOX_CHECK(service.receive(
        context, encode_frame(ack), RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 0U);
}

IOTOX_TEST("Ratox OUTPUT_ACK compacts only fully acknowledged queued frames") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &process = factory.latest();
    process.output.resize(
        iotox::protocol::ratox::kMaximumPayloadBytes + 9U, 0x5AU);

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 2U);
    const auto &first = require_front(service);
    IOTOX_CHECK(first.type == FrameType::output);
    IOTOX_CHECK(first.sequence == 1U);
    const std::uint64_t first_next = first.next_sequence;
    IOTOX_CHECK(first_next ==
                1U + iotox::protocol::ratox::kMaximumPayloadBytes);

    Frame ack = attached_request(
        FrameType::output_ack, opened.attached, 702U);
    ack.acknowledgement = first_next;
    IOTOX_CHECK(service.receive(
        context, encode_frame(ack),
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 1U);
    const auto &remaining = require_front(service);
    IOTOX_CHECK(remaining.type == FrameType::output);
    IOTOX_CHECK(remaining.sequence == first_next);
    IOTOX_CHECK(remaining.next_sequence == first_next + 9U);
}

IOTOX_TEST("Ratox cumulative OUTPUT_ACK remains bounded through long sessions") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService::Config config = service_config();
    config.directory.session.control_replay.maximum_entries = 1U;
    RatoxService service(registry, factory, config);
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &process = factory.latest();
    process.output.resize(1001U, 0x5AU);
    process.exit_on_signal = ProcessSignal::hangup;

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 1U);
    const Frame output = take_frame(service);
    IOTOX_CHECK(output.type == FrameType::output);
    IOTOX_CHECK(output.sequence == 1U);
    IOTOX_CHECK(output.payload.size() == 1001U);

    Frame latest;
    for (std::uint64_t index = 0U; index < 1001U; ++index) {
        latest = attached_request(
            FrameType::output_ack, opened.attached, 1000U + index);
        latest.acknowledgement = 2U + index;
        IOTOX_CHECK(service.receive(
            context, encode_frame(latest),
            RatoxService::Clock::time_point{}).ok());
    }
    IOTOX_CHECK(service.snapshot().outbound_packets == 0U);

    IOTOX_CHECK(service.receive(
        context, encode_frame(latest),
        RatoxService::Clock::time_point{}).ok());
    Frame conflicting = latest;
    --conflicting.acknowledgement;
    const Status conflict = service.receive(
        context, encode_frame(conflicting),
        RatoxService::Clock::time_point{});
    IOTOX_CHECK(!conflict.ok());
    IOTOX_CHECK(conflict.code() == ErrorCode::protocol_error);
    Frame stale = latest;
    --stale.message_id;
    const Status stale_result = service.receive(
        context, encode_frame(stale),
        RatoxService::Clock::time_point{});
    IOTOX_CHECK(!stale_result.ok());
    IOTOX_CHECK(stale_result.code() == ErrorCode::protocol_error);

    Frame close = attached_request(
        FrameType::close, opened.attached, 3000U);
    close.payload.resize(2U, 0U);
    write_u16(close.payload, 1U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(close),
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    bool saw_exit = false;
    while (service.peek_outbound() != nullptr) {
        saw_exit = saw_exit || take_frame(service).type == FrameType::exit_status;
    }
    IOTOX_CHECK(saw_exit);
    IOTOX_CHECK(service.snapshot().running_processes == 0U);
}

IOTOX_TEST("Ratox INPUT piggyback ACK compacts retained output and gap notices") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService::Config config = service_config();
    config.directory.session.output.maximum_bytes = 4U;
    RatoxService service(registry, factory, config);
    const RatoxPeerContext context = peer();
    Opened opened = open_service(service, context);
    auto &process = factory.latest();
    process.output = {1U, 2U, 3U, 4U, 5U, 6U};

    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 2U);
    IOTOX_CHECK(require_front(service).type == FrameType::output_gap);

    Frame input = attached_request(FrameType::input, opened.attached, 703U);
    input.sequence = 1U;
    input.acknowledgement = 7U;
    input.payload = {0x42U};
    IOTOX_CHECK(service.receive(
        context, encode_frame(input),
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.snapshot().outbound_packets == 0U);
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    const Frame input_ack = take_frame(service);
    IOTOX_CHECK(input_ack.type == FrameType::input_ack);
    IOTOX_CHECK(input_ack.acknowledgement == 2U);
}

IOTOX_TEST("Ratox closed sessions release live quota into bounded epoch tombstones") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService::Config config = service_config();
    config.directory.maximum_sessions_per_principal = 1U;
    config.directory.maximum_sessions_per_device = 1U;
    config.maximum_session_tombstones = 2U;
    RatoxService service(registry, factory, config);
    const RatoxPeerContext context = peer();
    Opened first = open_service(service, context);
    auto &first_process = factory.latest();
    first_process.exit_on_signal = ProcessSignal::hangup;

    Frame close = attached_request(FrameType::close, first.attached, 801U);
    close.payload.resize(2U, 0U);
    write_u16(close.payload, 1U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(close),
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(service.service(RatoxService::Clock::time_point{}).ok());
    while (service.peek_outbound() != nullptr) {
        static_cast<void>(take_frame(service));
    }

    auto closed = service.snapshot();
    IOTOX_CHECK(closed.live_sessions == 0U);
    IOTOX_CHECK(closed.retained_session_tombstones == 1U);
    IOTOX_CHECK(closed.tombstone_bound_respected);

    const Frame second_request = open_frame(
        context, session(0x52U), nonce(0x52U), 802U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(second_request),
        RatoxService::Clock::time_point{}).ok());
    const Frame second_result = take_frame(service);
    IOTOX_CHECK(read_u16(second_result.payload) == 0U);
    IOTOX_CHECK(factory.spawn_count == 2U);
    IOTOX_CHECK(service.snapshot().live_sessions == 1U);

    const Frame reused_request = open_frame(
        context, first.attached.session_id, nonce(0x53U), 803U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(reused_request),
        RatoxService::Clock::time_point{}).ok());
    const Frame reused_result = take_frame(service);
    IOTOX_CHECK(read_u16(reused_result.payload) == 5U);
    IOTOX_CHECK(factory.spawn_count == 2U);

    IOTOX_CHECK(service.peer_offline(
        context.friend_number, context.online_epoch,
        RatoxService::Clock::time_point{}).ok());
    const auto released = service.snapshot();
    IOTOX_CHECK(released.retained_session_tombstones == 0U);
    IOTOX_CHECK(released.retained_admission_results == 0U);
    IOTOX_CHECK(released.live_sessions == 1U);
    IOTOX_CHECK(released.attached_sessions == 0U);
}


IOTOX_TEST("Ratox bounded service cycles rotate fairly across live PTYs") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService::Config config = service_config();
    config.maximum_input_write_operations = 1U;
    config.maximum_output_read_operations = 1U;
    config.maximum_output_frames = 8U;
    RatoxService service(registry, factory, config);
    const RatoxPeerContext context = peer();

    const Frame first_open = open_frame(
        context, session(0x81U), nonce(0x81U), 901U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(first_open),
        RatoxService::Clock::time_point{}).ok());
    const Frame first_result = take_frame(service);
    IOTOX_CHECK(read_u16(first_result.payload) == 0U);
    Frame first_attached = first_open;
    first_attached.incarnation = first_result.incarnation;
    first_attached.generation = first_result.generation;

    const Frame second_open = open_frame(
        context, session(0x82U), nonce(0x82U), 902U);
    IOTOX_CHECK(service.receive(
        context, encode_frame(second_open),
        RatoxService::Clock::time_point{}).ok());
    const Frame second_result = take_frame(service);
    IOTOX_CHECK(read_u16(second_result.payload) == 0U);
    Frame second_attached = second_open;
    second_attached.incarnation = second_result.incarnation;
    second_attached.generation = second_result.generation;

    IOTOX_CHECK(factory.states.size() == 2U);
    factory.states[0U]->writes = {
        WriteStep{IoDisposition::progress, 1U, false},
        WriteStep{IoDisposition::progress, 1U, false},
        WriteStep{IoDisposition::progress, 1U, false},
        WriteStep{IoDisposition::progress, 1U, false},
    };

    Frame first_input = attached_request(
        FrameType::input, first_attached, 903U);
    first_input.sequence = 1U;
    first_input.payload = {1U, 2U, 3U, 4U};
    IOTOX_CHECK(service.receive(
        context, encode_frame(first_input),
        RatoxService::Clock::time_point{}).ok());

    Frame second_input = attached_request(
        FrameType::input, second_attached, 904U);
    second_input.sequence = 1U;
    second_input.payload = {9U};
    IOTOX_CHECK(service.receive(
        context, encode_frame(second_input),
        RatoxService::Clock::time_point{}).ok());

    IOTOX_CHECK(service.service(
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(factory.states[0U]->written ==
                std::vector<std::uint8_t>({1U}));
    IOTOX_CHECK(factory.states[1U]->written.empty());

    IOTOX_CHECK(service.service(
        RatoxService::Clock::time_point{}).ok());
    IOTOX_CHECK(factory.states[0U]->written ==
                std::vector<std::uint8_t>({1U}));
    IOTOX_CHECK(factory.states[1U]->written ==
                std::vector<std::uint8_t>({9U}));
}

IOTOX_TEST("Ratox shutdown escalates HUP TERM KILL on caller supplied time") {
    using namespace std::chrono_literals;
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    static_cast<void>(open_service(service, context));
    auto &process = factory.latest();
    const auto start = RatoxService::Clock::time_point{};

    IOTOX_CHECK(service.shutdown(start).ok());
    IOTOX_CHECK(process.signals ==
                std::vector<ProcessSignal>({ProcessSignal::hangup}));
    IOTOX_CHECK(service.service(start + 499ms).ok());
    IOTOX_CHECK(process.signals.size() == 1U);
    IOTOX_CHECK(service.service(start + 500ms).ok());
    IOTOX_CHECK(process.signals.back() == ProcessSignal::terminate);
    IOTOX_CHECK(service.service(start + 1999ms).ok());
    IOTOX_CHECK(process.signals.size() == 2U);
    IOTOX_CHECK(service.service(start + 2000ms).ok());
    IOTOX_CHECK(process.signals.back() == ProcessSignal::kill);
    const Status timed_out = service.service(start + 3000ms);
    IOTOX_CHECK(!timed_out.ok());
    IOTOX_CHECK(timed_out.code() == ErrorCode::timeout);
    IOTOX_CHECK(service.snapshot().running_processes == 0U);
}

IOTOX_TEST("Ratox lifecycle events carry nonzero monotonic service time") {
    ProfileRegistry registry;
    populate_registry(registry);
    FakeFactory factory;
    RatoxService service(registry, factory, service_config());
    const RatoxPeerContext context = peer();
    static_cast<void>(open_service(service, context));

    const auto events = service.events();
    IOTOX_CHECK(!events.empty());
    std::uint64_t previous = 0U;
    for (const auto &event : events) {
        IOTOX_CHECK(event.steady_time_us != 0U);
        IOTOX_CHECK(event.steady_time_us >= previous);
        previous = event.steady_time_us;
    }
}
