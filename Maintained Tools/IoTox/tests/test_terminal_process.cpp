#include "test_harness.hpp"

#include "iotox/terminal_process.hpp"

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <span>
#include <utility>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::Result;
using iotox::Status;
using iotox::terminal::CloseReason;
using iotox::terminal::ControllerPhase;
using iotox::terminal::Dimensions;
using iotox::terminal::EnvironmentEntry;
using iotox::terminal::ExitKind;
using iotox::terminal::IoDisposition;
using iotox::terminal::ProcessExit;
using iotox::terminal::ProcessSignal;
using iotox::terminal::PtyProcess;
using iotox::terminal::PtyProcessFactory;
using iotox::terminal::ReadResult;
using iotox::terminal::ResolvedProfile;
using iotox::terminal::TerminalController;
using iotox::terminal::WriteResult;

struct FakeState {
    std::size_t maximum_write{static_cast<std::size_t>(-1)};
    IoDisposition write_disposition{IoDisposition::progress};
    std::vector<std::uint8_t> output;
    std::size_t output_offset{0U};
    bool output_closed{false};
    std::size_t maximum_read_requested{0U};
    std::vector<Dimensions> resizes;
    std::vector<ProcessSignal> signals;
    std::optional<ProcessSignal> exit_on_signal;
    std::optional<ProcessExit> exit;
    bool fail_write{false};
    bool fail_read{false};
    bool fail_resize{false};
    bool fail_signal{false};
    bool fail_poll{false};
};

class FakeProcess final : public PtyProcess {
  public:
    explicit FakeProcess(std::shared_ptr<FakeState> state)
        : state_(std::move(state)) {}

    Result<WriteResult> write(std::span<const std::uint8_t> bytes) override {
        if (state_->fail_write) {
            return Status{ErrorCode::io_error, "injected write failure"};
        }
        if (state_->write_disposition != IoDisposition::progress) {
            return WriteResult{state_->write_disposition, 0U};
        }
        return WriteResult{
            IoDisposition::progress,
            std::min(bytes.size(), state_->maximum_write)};
    }

    Result<ReadResult> read(std::size_t maximum_bytes) override {
        state_->maximum_read_requested =
            std::max(state_->maximum_read_requested, maximum_bytes);
        if (state_->fail_read) {
            return Status{ErrorCode::io_error, "injected read failure"};
        }
        if (state_->output_offset < state_->output.size()) {
            const std::size_t amount = std::min(
                maximum_bytes, state_->output.size() - state_->output_offset);
            std::vector<std::uint8_t> bytes(
                state_->output.begin() +
                    static_cast<std::ptrdiff_t>(state_->output_offset),
                state_->output.begin() + static_cast<std::ptrdiff_t>(
                    state_->output_offset + amount));
            state_->output_offset += amount;
            return ReadResult{IoDisposition::progress, std::move(bytes)};
        }
        return ReadResult{
            state_->output_closed ? IoDisposition::closed
                                  : IoDisposition::would_block,
            {}};
    }

    Status resize(const Dimensions &dimensions) override {
        if (state_->fail_resize) {
            return Status{ErrorCode::io_error, "injected resize failure"};
        }
        state_->resizes.push_back(dimensions);
        return Status::success();
    }

    Status send_signal(ProcessSignal signal) override {
        if (state_->fail_signal) {
            return Status{ErrorCode::io_error, "injected signal failure"};
        }
        state_->signals.push_back(signal);
        if (state_->exit_on_signal && *state_->exit_on_signal == signal) {
            int value = 0;
            switch (signal) {
                case ProcessSignal::hangup:
                    value = 1;
                    break;
                case ProcessSignal::terminate:
                    value = 15;
                    break;
                case ProcessSignal::kill:
                    value = 9;
                    break;
            }
            state_->exit = ProcessExit{ExitKind::signaled, value, false};
        }
        return Status::success();
    }

    Result<std::optional<ProcessExit>> poll_exit() override {
        if (state_->fail_poll) {
            return Status{ErrorCode::io_error, "injected poll failure"};
        }
        return state_->exit;
    }

  private:
    std::shared_ptr<FakeState> state_;
};

class FakeFactory final : public PtyProcessFactory {
  public:
    std::shared_ptr<FakeState> state{std::make_shared<FakeState>()};
    bool fail{false};
    bool return_null{false};
    std::optional<ResolvedProfile> received;

    Result<std::unique_ptr<PtyProcess>> spawn(
        const ResolvedProfile &profile) override {
        received = profile;
        if (fail) {
            return Status{ErrorCode::unavailable, "injected spawn failure"};
        }
        if (return_null) return std::unique_ptr<PtyProcess>{};
        return std::unique_ptr<PtyProcess>(new FakeProcess(state));
    }
};

ResolvedProfile sample_resolved_profile() {
    ResolvedProfile resolved;
    resolved.profile.id = "deterministic-fixture";
    resolved.profile.enabled = true;
    resolved.profile.arguments = {"/bin/echo", "fixed"};
    resolved.profile.working_directory = "/tmp";
    resolved.profile.dimensions.minimum = Dimensions{20U, 5U};
    resolved.profile.dimensions.initial = Dimensions{80U, 24U};
    resolved.profile.dimensions.maximum = Dimensions{200U, 60U};
    resolved.profile.hangup_grace = std::chrono::milliseconds{20};
    resolved.profile.terminate_grace = std::chrono::milliseconds{40};
    resolved.profile.kill_reap_grace = std::chrono::milliseconds{60};
    resolved.environment = {
        EnvironmentEntry{"TERM", "xterm-256color"},
    };
    resolved.accepted_dimensions = Dimensions{80U, 24U};
    resolved.policy_generation = 7U;
    return resolved;
}

std::unique_ptr<TerminalController> start_controller(FakeFactory &factory) {
    auto started = TerminalController::start(factory, sample_resolved_profile());
    if (!started.ok()) {
        iotox::test::fail(
            "TerminalController::start", __FILE__, __LINE__,
            started.status().message());
    }
    return std::move(started.value());
}

}  // namespace

IOTOX_TEST("terminal controller streams bounded nonblocking IO and clamps resize") {
    FakeFactory factory;
    factory.state->maximum_write = 3U;
    factory.state->output = {1U, 2U, 3U, 4U, 5U};
    auto controller = start_controller(factory);

    const std::vector<std::uint8_t> input{9U, 8U, 7U, 6U};
    auto written = controller->write_input(input);
    IOTOX_CHECK(written.ok());
    IOTOX_CHECK((written.value() == WriteResult{IoDisposition::progress, 3U}));

    auto first = controller->read_output(2U);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK((first.value() ==
                 ReadResult{IoDisposition::progress, {1U, 2U}}));
    auto second = controller->read_output(8U);
    IOTOX_CHECK(second.ok());
    IOTOX_CHECK((second.value() ==
                 ReadResult{IoDisposition::progress, {3U, 4U, 5U}}));
    auto empty = controller->read_output(8U);
    IOTOX_CHECK(empty.ok());
    IOTOX_CHECK(empty.value().disposition == IoDisposition::would_block);

    auto resized = controller->resize(Dimensions{1000U, 1U});
    IOTOX_CHECK(resized.ok());
    IOTOX_CHECK((resized.value() == Dimensions{200U, 5U}));
    IOTOX_CHECK(factory.state->resizes.size() == 1U);
    IOTOX_CHECK((factory.state->resizes.front() == Dimensions{200U, 5U}));

    const auto snapshot = controller->snapshot();
    IOTOX_CHECK(snapshot.phase == ControllerPhase::running);
    IOTOX_CHECK(snapshot.policy_generation == 7U);
    IOTOX_CHECK(snapshot.input_bytes == 3U);
    IOTOX_CHECK(snapshot.output_bytes == 5U);
    IOTOX_CHECK(snapshot.write_calls == 1U);
    IOTOX_CHECK(snapshot.read_calls == 3U);
    IOTOX_CHECK(snapshot.resize_calls == 1U);
    IOTOX_CHECK(factory.state->maximum_read_requested == 8U);
}

IOTOX_TEST("terminal controller performs HUP TERM KILL escalation with fresh grace windows") {
    FakeFactory factory;
    factory.state->exit_on_signal = ProcessSignal::kill;
    auto controller = start_controller(factory);
    const auto start = TerminalController::TimePoint{};

    IOTOX_CHECK(controller->request_close(
        CloseReason::authority_revoked, start).ok());
    IOTOX_CHECK(factory.state->signals ==
                std::vector<ProcessSignal>{ProcessSignal::hangup});
    IOTOX_CHECK(controller->snapshot().phase == ControllerPhase::hangup_grace);

    IOTOX_CHECK(controller->poll(start + std::chrono::milliseconds{19}).ok());
    IOTOX_CHECK(factory.state->signals.size() == 1U);
    IOTOX_CHECK(controller->poll(start + std::chrono::milliseconds{20}).ok());
    IOTOX_CHECK(factory.state->signals ==
                std::vector<ProcessSignal>({
                    ProcessSignal::hangup,
                    ProcessSignal::terminate,
                }));

    IOTOX_CHECK(controller->poll(start + std::chrono::milliseconds{59}).ok());
    IOTOX_CHECK(factory.state->signals.size() == 2U);
    IOTOX_CHECK(controller->poll(start + std::chrono::milliseconds{60}).ok());
    IOTOX_CHECK(factory.state->signals ==
                std::vector<ProcessSignal>({
                    ProcessSignal::hangup,
                    ProcessSignal::terminate,
                    ProcessSignal::kill,
                }));
    IOTOX_CHECK(controller->snapshot().phase == ControllerPhase::kill_reap_grace);

    IOTOX_CHECK(controller->poll(start + std::chrono::milliseconds{61}).ok());
    const auto snapshot = controller->snapshot();
    IOTOX_CHECK(snapshot.phase == ControllerPhase::exited);
    IOTOX_CHECK(snapshot.close_reason == CloseReason::authority_revoked);
    IOTOX_CHECK((snapshot.exit ==
                 ProcessExit{ExitKind::signaled, 9, false}));
    IOTOX_CHECK(snapshot.hangup_signals == 1U);
    IOTOX_CHECK(snapshot.terminate_signals == 1U);
    IOTOX_CHECK(snapshot.kill_signals == 1U);
}

IOTOX_TEST("terminal close observes an already-exited process before signaling") {
    FakeFactory factory;
    factory.state->exit = ProcessExit{ExitKind::exited, 23, false};
    auto controller = start_controller(factory);
    IOTOX_CHECK(controller->request_close(
        CloseReason::controller_request, TerminalController::TimePoint{}).ok());
    IOTOX_CHECK(factory.state->signals.empty());
    IOTOX_CHECK(controller->snapshot().phase == ControllerPhase::exited);
    IOTOX_CHECK((controller->snapshot().exit ==
                 ProcessExit{ExitKind::exited, 23, false}));
}

IOTOX_TEST("terminal controller fails closed when SIGKILL is not reaped") {
    FakeFactory factory;
    auto controller = start_controller(factory);
    const auto start = TerminalController::TimePoint{};
    IOTOX_CHECK(controller->request_close(
        CloseReason::daemon_shutdown, start).ok());
    IOTOX_CHECK(controller->poll(start + std::chrono::milliseconds{20}).ok());
    IOTOX_CHECK(controller->poll(start + std::chrono::milliseconds{60}).ok());
    const Status timed_out =
        controller->poll(start + std::chrono::milliseconds{120});
    IOTOX_CHECK(!timed_out.ok());
    IOTOX_CHECK(timed_out.code() == ErrorCode::timeout);
    const auto snapshot = controller->snapshot();
    IOTOX_CHECK(snapshot.phase == ControllerPhase::failed);
    IOTOX_CHECK(snapshot.close_reason == CloseReason::daemon_shutdown);
    IOTOX_CHECK(snapshot.error_code == ErrorCode::timeout);
}

IOTOX_TEST("terminal controller denies new effects after close while allowing output drain") {
    FakeFactory factory;
    factory.state->output = {42U, 43U};
    factory.state->output_closed = true;
    auto controller = start_controller(factory);
    const auto start = TerminalController::TimePoint{};
    IOTOX_CHECK(controller->request_close(
        CloseReason::controller_request, start).ok());

    const std::vector<std::uint8_t> byte{1U};
    auto denied_write = controller->write_input(byte);
    IOTOX_CHECK(!denied_write.ok());
    IOTOX_CHECK(denied_write.status().code() == ErrorCode::unavailable);
    auto denied_resize = controller->resize(Dimensions{100U, 30U});
    IOTOX_CHECK(!denied_resize.ok());
    IOTOX_CHECK(denied_resize.status().code() == ErrorCode::unavailable);

    auto drained = controller->read_output(8U);
    IOTOX_CHECK(drained.ok());
    IOTOX_CHECK(drained.value().bytes == std::vector<std::uint8_t>({42U, 43U}));
    auto closed = controller->read_output(8U);
    IOTOX_CHECK(closed.ok());
    IOTOX_CHECK(closed.value().disposition == IoDisposition::closed);
    IOTOX_CHECK(controller->snapshot().output_closed);
}

IOTOX_TEST("terminal controller converts backend contract violations into terminal failure") {
    FakeFactory factory;
    factory.state->write_disposition = IoDisposition::would_block;
    auto controller = start_controller(factory);
    const std::vector<std::uint8_t> input{1U, 2U};
    auto would_block = controller->write_input(input);
    IOTOX_CHECK(would_block.ok());
    IOTOX_CHECK(would_block.value().disposition == IoDisposition::would_block);

    factory.state->fail_poll = true;
    const Status failed = controller->poll(TerminalController::TimePoint{});
    IOTOX_CHECK(!failed.ok());
    IOTOX_CHECK(failed.code() == ErrorCode::io_error);
    IOTOX_CHECK(controller->snapshot().phase == ControllerPhase::failed);
    auto read_after_failure = controller->read_output(1U);
    IOTOX_CHECK(!read_after_failure.ok());
}

IOTOX_TEST("terminal controller enforces profile resize and factory gates") {
    FakeFactory factory;
    ResolvedProfile profile = sample_resolved_profile();
    profile.profile.dimensions.allow_resize = false;
    auto started = TerminalController::start(factory, profile);
    IOTOX_CHECK(started.ok());
    auto resize = started.value()->resize(Dimensions{100U, 30U});
    IOTOX_CHECK(!resize.ok());
    IOTOX_CHECK(resize.status().code() == ErrorCode::unsupported);
    IOTOX_CHECK(factory.state->resizes.empty());

    FakeFactory failed_factory;
    failed_factory.fail = true;
    auto failed = TerminalController::start(
        failed_factory, sample_resolved_profile());
    IOTOX_CHECK(!failed.ok());
    IOTOX_CHECK(failed.status().code() == ErrorCode::unavailable);

    FakeFactory null_factory;
    null_factory.return_null = true;
    auto null_process = TerminalController::start(
        null_factory, sample_resolved_profile());
    IOTOX_CHECK(!null_process.ok());
    IOTOX_CHECK(null_process.status().code() == ErrorCode::internal_error);

    FakeFactory invalid_factory;
    ResolvedProfile invalid = sample_resolved_profile();
    invalid.policy_generation = 0U;
    auto invalid_start = TerminalController::start(invalid_factory, invalid);
    IOTOX_CHECK(!invalid_start.ok());
    IOTOX_CHECK(invalid_factory.received == std::nullopt);
}
