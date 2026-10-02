#include "iotox/terminal_process.hpp"

#include <limits>
#include <utility>

namespace iotox::terminal {
namespace {

[[nodiscard]] Status validate_exit(const ProcessExit &exit) {
    if (exit.kind == ExitKind::exited) {
        if (exit.value < 0 || exit.value > 255 || exit.core_dumped) {
            return Status{ErrorCode::internal_error,
                          "PTY backend returned an invalid exit status"};
        }
        return Status::success();
    }
    if (exit.kind == ExitKind::signaled) {
        if (exit.value <= 0 || exit.value > 255) {
            return Status{ErrorCode::internal_error,
                          "PTY backend returned an invalid signal status"};
        }
        return Status::success();
    }
    return Status{ErrorCode::internal_error,
                  "PTY backend returned an unassigned exit kind"};
}


void saturating_increment(std::uint64_t &value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) ++value;
}
}  // namespace

Result<std::unique_ptr<TerminalController>> TerminalController::start(
    PtyProcessFactory &factory, ResolvedProfile profile) {
    const Status valid_profile = validate_resolved_profile(profile);
    if (!valid_profile.ok()) return valid_profile;
    auto process = factory.spawn(profile);
    if (!process.ok()) return process.status();
    if (!process.value()) {
        return Status{ErrorCode::internal_error,
                      "PTY process factory returned a null process"};
    }
    return std::unique_ptr<TerminalController>(new TerminalController(
        std::move(process.value()), std::move(profile)));
}

TerminalController::TerminalController(
    std::unique_ptr<PtyProcess> process, ResolvedProfile profile)
    : process_(std::move(process)),
      profile_(std::move(profile)),
      dimensions_(profile_.accepted_dimensions) {}

void TerminalController::account_input(std::size_t bytes) noexcept {
    const std::uint64_t amount = static_cast<std::uint64_t>(bytes);
    input_bytes_ = amount > std::numeric_limits<std::uint64_t>::max() - input_bytes_
                       ? std::numeric_limits<std::uint64_t>::max()
                       : input_bytes_ + amount;
}

void TerminalController::account_output(std::size_t bytes) noexcept {
    const std::uint64_t amount = static_cast<std::uint64_t>(bytes);
    output_bytes_ = amount > std::numeric_limits<std::uint64_t>::max() - output_bytes_
                        ? std::numeric_limits<std::uint64_t>::max()
                        : output_bytes_ + amount;
}

Status TerminalController::fail(Status status, CloseReason reason) {
    if (status.ok()) {
        status = Status{ErrorCode::internal_error,
                        "terminal controller entered failure without an error"};
    }
    if (phase_ != ControllerPhase::failed) {
        failure_ = status;
        phase_ = ControllerPhase::failed;
        deadline_.reset();
        if (!close_reason_) close_reason_ = reason;
    }
    return failure_;
}

Status TerminalController::observe_exit() {
    if (phase_ == ControllerPhase::exited) return Status::success();
    if (phase_ == ControllerPhase::failed) return failure_;
    auto observed = process_->poll_exit();
    if (!observed.ok()) {
        return fail(observed.status(), CloseReason::process_failure);
    }
    if (!observed.value()) return Status::success();
    const Status valid = validate_exit(*observed.value());
    if (!valid.ok()) return fail(valid, CloseReason::process_failure);
    exit_ = *observed.value();
    phase_ = ControllerPhase::exited;
    deadline_.reset();
    return Status::success();
}

Result<WriteResult> TerminalController::write_input(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() > kMaximumTerminalIoChunk) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal input exceeds the per-call byte bound"};
    }
    if (phase_ != ControllerPhase::running) {
        return Status{ErrorCode::unavailable,
                      "terminal input is closed once shutdown begins"};
    }
    saturating_increment(write_calls_);
    auto written = process_->write(bytes);
    if (!written.ok()) {
        return fail(written.status(), CloseReason::process_failure);
    }
    if (written.value().bytes > bytes.size()) {
        return fail(
            Status{ErrorCode::internal_error,
                   "PTY backend reported writing more bytes than supplied"},
            CloseReason::process_failure);
    }
    if (written.value().disposition == IoDisposition::progress &&
        !bytes.empty() && written.value().bytes == 0U) {
        return fail(
            Status{ErrorCode::internal_error,
                   "PTY backend reported zero-byte write progress"},
            CloseReason::process_failure);
    }
    if (written.value().disposition != IoDisposition::progress &&
        written.value().bytes != 0U) {
        return fail(
            Status{ErrorCode::internal_error,
                   "PTY backend attached bytes to a non-progress write"},
            CloseReason::process_failure);
    }
    if (written.value().disposition == IoDisposition::closed) {
        return fail(
            Status{ErrorCode::io_error, "terminal input side is closed"},
            CloseReason::process_failure);
    }
    account_input(written.value().bytes);
    return written.value();
}

Result<ReadResult> TerminalController::read_output(std::size_t maximum_bytes) {
    if (maximum_bytes == 0U || maximum_bytes > kMaximumTerminalIoChunk) {
        return Status{ErrorCode::invalid_argument,
                      "terminal output read bound is outside the per-call limit"};
    }
    if (phase_ == ControllerPhase::failed) return failure_;
    saturating_increment(read_calls_);
    auto read = process_->read(maximum_bytes);
    if (!read.ok()) {
        return fail(read.status(), CloseReason::process_failure);
    }
    if (read.value().bytes.size() > maximum_bytes) {
        return fail(
            Status{ErrorCode::internal_error,
                   "PTY backend returned more output than requested"},
            CloseReason::process_failure);
    }
    if (read.value().disposition == IoDisposition::progress &&
        read.value().bytes.empty()) {
        return fail(
            Status{ErrorCode::internal_error,
                   "PTY backend reported empty output progress"},
            CloseReason::process_failure);
    }
    if (read.value().disposition != IoDisposition::progress &&
        !read.value().bytes.empty()) {
        return fail(
            Status{ErrorCode::internal_error,
                   "PTY backend attached bytes to a non-progress read"},
            CloseReason::process_failure);
    }
    if (read.value().disposition == IoDisposition::closed) {
        output_closed_ = true;
    }
    account_output(read.value().bytes.size());
    return read.value();
}

Result<Dimensions> TerminalController::resize(const Dimensions &requested) {
    if (phase_ != ControllerPhase::running) {
        return Status{ErrorCode::unavailable,
                      "terminal resize is closed once shutdown begins"};
    }
    if (!profile_.profile.dimensions.allow_resize) {
        return Status{ErrorCode::unsupported,
                      "terminal profile does not permit resize"};
    }
    auto accepted = accept_dimensions(profile_.profile.dimensions, requested);
    if (!accepted.ok()) return accepted.status();
    const Status resized = process_->resize(accepted.value());
    if (!resized.ok()) {
        return fail(resized, CloseReason::process_failure);
    }
    dimensions_ = accepted.value();
    saturating_increment(resize_calls_);
    return dimensions_;
}

Status TerminalController::issue_signal(ProcessSignal signal, TimePoint now) {
    const Status sent = process_->send_signal(signal);
    if (!sent.ok()) return fail(sent, CloseReason::process_failure);
    switch (signal) {
        case ProcessSignal::hangup:
            saturating_increment(hangup_signals_);
            phase_ = ControllerPhase::hangup_grace;
            deadline_ = now + profile_.profile.hangup_grace;
            break;
        case ProcessSignal::terminate:
            saturating_increment(terminate_signals_);
            phase_ = ControllerPhase::terminate_grace;
            deadline_ = now + profile_.profile.terminate_grace;
            break;
        case ProcessSignal::kill:
            saturating_increment(kill_signals_);
            phase_ = ControllerPhase::kill_reap_grace;
            deadline_ = now + profile_.profile.kill_reap_grace;
            break;
        default:
            return fail(
                Status{ErrorCode::internal_error,
                       "terminal controller selected an unassigned signal"},
                CloseReason::process_failure);
    }
    return Status::success();
}

Status TerminalController::request_close(CloseReason reason, TimePoint now) {
    if (phase_ == ControllerPhase::failed) return failure_;
    if (phase_ == ControllerPhase::exited) return Status::success();
    if (phase_ != ControllerPhase::running) return Status::success();
    const Status observed = observe_exit();
    if (!observed.ok() || phase_ == ControllerPhase::exited) return observed;
    close_reason_ = reason;
    return issue_signal(ProcessSignal::hangup, now);
}

Status TerminalController::poll(TimePoint now) {
    if (phase_ == ControllerPhase::failed) return failure_;
    if (phase_ == ControllerPhase::exited) return Status::success();
    const Status observed = observe_exit();
    if (!observed.ok() || phase_ == ControllerPhase::exited) return observed;
    if (phase_ == ControllerPhase::running || !deadline_ || now < *deadline_) {
        return Status::success();
    }
    switch (phase_) {
        case ControllerPhase::hangup_grace:
            return issue_signal(ProcessSignal::terminate, now);
        case ControllerPhase::terminate_grace:
            return issue_signal(ProcessSignal::kill, now);
        case ControllerPhase::kill_reap_grace:
            return fail(
                Status{ErrorCode::timeout,
                       "terminal process was not reaped after SIGKILL"},
                CloseReason::process_failure);
        case ControllerPhase::running:
        case ControllerPhase::exited:
        case ControllerPhase::failed:
            break;
    }
    return fail(
        Status{ErrorCode::internal_error,
               "terminal controller reached an unassigned lifecycle phase"},
        CloseReason::process_failure);
}

ControllerSnapshot TerminalController::snapshot() const {
    ControllerSnapshot snapshot;
    snapshot.phase = phase_;
    snapshot.profile_id = profile_.profile.id;
    snapshot.policy_generation = profile_.policy_generation;
    snapshot.dimensions = dimensions_;
    snapshot.close_reason = close_reason_;
    snapshot.exit = exit_;
    snapshot.output_closed = output_closed_;
    snapshot.input_bytes = input_bytes_;
    snapshot.output_bytes = output_bytes_;
    snapshot.write_calls = write_calls_;
    snapshot.read_calls = read_calls_;
    snapshot.resize_calls = resize_calls_;
    snapshot.hangup_signals = hangup_signals_;
    snapshot.terminate_signals = terminate_signals_;
    snapshot.kill_signals = kill_signals_;
    if (phase_ == ControllerPhase::failed) {
        snapshot.error_code = failure_.code();
        snapshot.error_message = failure_.message();
    }
    return snapshot;
}

}  // namespace iotox::terminal
