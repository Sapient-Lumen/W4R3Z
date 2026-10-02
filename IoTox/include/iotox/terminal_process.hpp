#pragma once

#include "iotox/status.hpp"
#include "iotox/terminal_profile.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace iotox::terminal {

inline constexpr std::size_t kMaximumTerminalIoChunk = 64U * 1024U;

enum class IoDisposition : std::uint8_t {
    progress = 1U,
    would_block = 2U,
    closed = 3U,
};

struct WriteResult {
    IoDisposition disposition{IoDisposition::would_block};
    std::size_t bytes{0U};

    [[nodiscard]] bool operator==(const WriteResult &) const = default;
};

struct ReadResult {
    IoDisposition disposition{IoDisposition::would_block};
    std::vector<std::uint8_t> bytes;

    [[nodiscard]] bool operator==(const ReadResult &) const = default;
};

enum class ProcessSignal : std::uint8_t {
    hangup = 1U,
    terminate = 2U,
    kill = 3U,
};

enum class ExitKind : std::uint8_t {
    exited = 1U,
    signaled = 2U,
};

struct ProcessExit {
    ExitKind kind{ExitKind::exited};
    // Exit status when kind=exited; signal number when kind=signaled.
    int value{0};
    bool core_dumped{false};

    [[nodiscard]] bool operator==(const ProcessExit &) const = default;
};

class PtyProcess {
  public:
    virtual ~PtyProcess() = default;

    // Implementations are nonblocking and never retain caller-owned input.
    [[nodiscard]] virtual Result<WriteResult> write(
        std::span<const std::uint8_t> bytes) = 0;
    [[nodiscard]] virtual Result<ReadResult> read(std::size_t maximum_bytes) = 0;
    [[nodiscard]] virtual Status resize(const Dimensions &dimensions) = 0;
    [[nodiscard]] virtual Status send_signal(ProcessSignal signal) = 0;
    // Idempotent: after exit is observed, every later call returns the same value.
    [[nodiscard]] virtual Result<std::optional<ProcessExit>> poll_exit() = 0;
};

class PtyProcessFactory {
  public:
    virtual ~PtyProcessFactory() = default;
    [[nodiscard]] virtual Result<std::unique_ptr<PtyProcess>> spawn(
        const ResolvedProfile &profile) = 0;
};

enum class ControllerPhase : std::uint8_t {
    running = 1U,
    hangup_grace = 2U,
    terminate_grace = 3U,
    kill_reap_grace = 4U,
    exited = 5U,
    failed = 6U,
};

enum class CloseReason : std::uint8_t {
    controller_request = 1U,
    authority_revoked = 2U,
    daemon_shutdown = 3U,
    process_failure = 4U,
};

struct ControllerSnapshot {
    ControllerPhase phase{ControllerPhase::failed};
    std::string profile_id;
    std::uint64_t policy_generation{0U};
    Dimensions dimensions{};
    std::optional<CloseReason> close_reason;
    std::optional<ProcessExit> exit;
    bool output_closed{false};
    std::uint64_t input_bytes{0U};
    std::uint64_t output_bytes{0U};
    std::uint64_t write_calls{0U};
    std::uint64_t read_calls{0U};
    std::uint64_t resize_calls{0U};
    std::uint64_t hangup_signals{0U};
    std::uint64_t terminate_signals{0U};
    std::uint64_t kill_signals{0U};
    ErrorCode error_code{ErrorCode::ok};
    std::string error_message;
};

class TerminalController {
  public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    [[nodiscard]] static Result<std::unique_ptr<TerminalController>> start(
        PtyProcessFactory &factory, ResolvedProfile profile);

    TerminalController(const TerminalController &) = delete;
    TerminalController &operator=(const TerminalController &) = delete;
    TerminalController(TerminalController &&) = delete;
    TerminalController &operator=(TerminalController &&) = delete;
    ~TerminalController() = default;

    [[nodiscard]] Result<WriteResult> write_input(
        std::span<const std::uint8_t> bytes);
    [[nodiscard]] Result<ReadResult> read_output(std::size_t maximum_bytes);
    [[nodiscard]] Result<Dimensions> resize(const Dimensions &requested);
    [[nodiscard]] Status request_close(CloseReason reason, TimePoint now);
    [[nodiscard]] Status poll(TimePoint now);
    [[nodiscard]] ControllerSnapshot snapshot() const;

  private:
    TerminalController(
        std::unique_ptr<PtyProcess> process, ResolvedProfile profile);

    [[nodiscard]] Status observe_exit();
    [[nodiscard]] Status issue_signal(ProcessSignal signal, TimePoint now);
    [[nodiscard]] Status fail(Status status, CloseReason reason);
    void account_input(std::size_t bytes) noexcept;
    void account_output(std::size_t bytes) noexcept;

    std::unique_ptr<PtyProcess> process_;
    ResolvedProfile profile_;
    ControllerPhase phase_{ControllerPhase::running};
    Dimensions dimensions_{};
    std::optional<CloseReason> close_reason_;
    std::optional<ProcessExit> exit_;
    std::optional<TimePoint> deadline_;
    bool output_closed_{false};
    std::uint64_t input_bytes_{0U};
    std::uint64_t output_bytes_{0U};
    std::uint64_t write_calls_{0U};
    std::uint64_t read_calls_{0U};
    std::uint64_t resize_calls_{0U};
    std::uint64_t hangup_signals_{0U};
    std::uint64_t terminate_signals_{0U};
    std::uint64_t kill_signals_{0U};
    Status failure_{};
};

}  // namespace iotox::terminal
