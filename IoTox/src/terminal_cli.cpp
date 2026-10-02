#include "iotox/terminal_cli.hpp"

#include "iotox/cli_registry.hpp"
#include "iotox/local/runtime_tree.hpp"
#include "iotox/local/control_protocol.hpp"
#include "iotox/local/control_socket.hpp"
#include "iotox/local/terminal_protocol.hpp"
#include "iotox/local/terminal_socket.hpp"
#include "iotox/peer_alias.hpp"
#include "iotox/security/random.hpp"
#include "iotox/security/sodium.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <climits>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <limits>
#include <optional>
#include <poll.h>
#include <span>
#include <string>
#include <string_view>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox {
namespace {

volatile std::sig_atomic_t g_terminal_signal = 0;
volatile std::sig_atomic_t g_terminal_resize = 0;

extern "C" void handle_terminal_signal(int signal_number) {
    if (signal_number == SIGWINCH) {
        g_terminal_resize = 1;
    } else {
        g_terminal_signal = signal_number;
    }
}

class SensitiveVectorGuard {
  public:
    explicit SensitiveVectorGuard(std::vector<std::uint8_t> &bytes) noexcept
        : bytes_(&bytes) {}
    ~SensitiveVectorGuard() {
        if (bytes_ != nullptr) security::secure_wipe(*bytes_);
    }
    SensitiveVectorGuard(const SensitiveVectorGuard &) = delete;
    SensitiveVectorGuard &operator=(const SensitiveVectorGuard &) = delete;
  private:
    std::vector<std::uint8_t> *bytes_;
};

template <std::size_t Size>
class SensitiveArrayGuard {
  public:
    explicit SensitiveArrayGuard(std::array<std::uint8_t, Size> &bytes) noexcept
        : bytes_(&bytes) {}
    ~SensitiveArrayGuard() {
        if (bytes_ != nullptr) security::secure_wipe(*bytes_);
    }
    SensitiveArrayGuard(const SensitiveArrayGuard &) = delete;
    SensitiveArrayGuard &operator=(const SensitiveArrayGuard &) = delete;
  private:
    std::array<std::uint8_t, Size> *bytes_;
};

struct TerminalArguments {
    enum class Mode : std::uint8_t { open, resume, sessions, close };

    std::filesystem::path runtime{local::default_runtime_root()};
    std::chrono::milliseconds timeout{5000};
    Mode mode{Mode::open};
    bool batch{false};
    bool reconnect{false};
    std::array<std::uint8_t, local::kTerminalPeerPublicKeyBytes> peer{};
    std::string peer_selector;
    std::array<std::uint8_t, local::kTerminalSessionIdBytes> session{};
};

bool option_takes_value(std::string_view option) noexcept {
    return option == "--runtime" || option == "--timeout-ms";
}

Result<std::uint64_t> parse_unsigned(
    std::string_view text, std::string_view label) {
    if (text.empty() || text.front() == '-') {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) + " must be a non-negative integer"};
    }
    std::uint64_t value = 0U;
    for (const char character : text) {
        if (character < '0' || character > '9') {
            return Status{ErrorCode::invalid_argument,
                          std::string(label) + " must contain decimal digits"};
        }
        const std::uint64_t digit =
            static_cast<std::uint64_t>(character - '0');
        if (value > (std::numeric_limits<std::uint64_t>::max() - digit) / 10U) {
            return Status{ErrorCode::invalid_argument,
                          std::string(label) + " is too large"};
        }
        value = value * 10U + digit;
    }
    return value;
}

template <std::size_t Size>
Result<std::array<std::uint8_t, Size>> parse_hex_array(
    std::string_view text, std::string_view label) {
    auto decoded = security::decode_hex_exact(text, Size, label);
    if (!decoded) return decoded.status();
    std::array<std::uint8_t, Size> result{};
    std::copy(decoded.value().begin(), decoded.value().end(), result.begin());
    return result;
}

Result<TerminalArguments> parse_terminal_arguments(
    std::span<const std::string_view> arguments) {
    TerminalArguments parsed;
    std::vector<std::string_view> positional;
    positional.reserve(arguments.size());

    for (std::size_t index = 0U; index < arguments.size(); ++index) {
        const std::string_view argument = arguments[index];
        if (option_takes_value(argument)) {
            if (index + 1U >= arguments.size()) {
                return Status{ErrorCode::invalid_argument,
                              std::string(argument) + " requires a value"};
            }
            const std::string_view value = arguments[++index];
            if (argument == "--runtime") {
                parsed.runtime = value;
            } else {
                auto milliseconds = parse_unsigned(value, "terminal timeout");
                if (!milliseconds || milliseconds.value() == 0U ||
                    milliseconds.value() > 60000U) {
                    return Status{ErrorCode::invalid_argument,
                                  "--timeout-ms must be in 1..60000"};
                }
                parsed.timeout =
                    std::chrono::milliseconds(milliseconds.value());
            }
            continue;
        }
        if (argument == "--batch") {
            parsed.batch = true;
            continue;
        }
        if (argument == "--reconnect") {
            if (parsed.reconnect) {
                return Status{ErrorCode::invalid_argument,
                              "--reconnect may be specified only once"};
            }
            parsed.reconnect = true;
            continue;
        }
        if (argument.starts_with("--")) {
            return Status{ErrorCode::invalid_argument,
                          "unknown terminal option: " + std::string(argument)};
        }
        positional.push_back(argument);
    }

    if (positional.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal command is missing"};
    }
    if (positional.front() == "terminal") {
        if (positional.size() != 2U) {
            return Status{ErrorCode::invalid_argument,
                          "terminal requires one PEER selector"};
        }
        parsed.mode = TerminalArguments::Mode::open;
        parsed.peer_selector = positional[1U];
    } else if (positional.front() == "terminal-resume") {
        if (positional.size() < 2U || positional.size() > 3U) {
            return Status{
                ErrorCode::invalid_argument,
                "terminal-resume requires SESSION_ID_HEX and optional PEER"};
        }
        auto session = parse_hex_array<local::kTerminalSessionIdBytes>(
            positional[1U], "terminal session ID");
        if (!session) return session.status();
        parsed.mode = TerminalArguments::Mode::resume;
        parsed.session = session.value();
        if (positional.size() == 3U) {
            parsed.peer_selector = positional[2U];
        }
    } else if (positional.front() == "terminal-sessions") {
        if (positional.size() > 2U) {
            return Status{ErrorCode::invalid_argument,
                          "terminal-sessions accepts an optional PEER"};
        }
        parsed.mode = TerminalArguments::Mode::sessions;
        if (positional.size() == 2U) {
            parsed.peer_selector = positional[1U];
        }
    } else if (positional.front() == "terminal-close") {
        if (positional.size() < 2U || positional.size() > 3U) {
            return Status{ErrorCode::invalid_argument,
                          "terminal-close requires SESSION_ID_HEX and optional PEER"};
        }
        parsed.mode = TerminalArguments::Mode::close;
        auto session = parse_hex_array<local::kTerminalSessionIdBytes>(
            positional[1U], "terminal session ID");
        if (!session) return session.status();
        parsed.session = session.value();
        if (positional.size() == 3U) {
            parsed.peer_selector = positional[2U];
        }
    } else {
        return Status{ErrorCode::invalid_argument,
                      "unknown terminal command: " +
                          std::string(positional.front())};
    }
    if (parsed.batch && parsed.mode != TerminalArguments::Mode::open &&
        parsed.mode != TerminalArguments::Mode::resume) {
        return Status{ErrorCode::invalid_argument,
                      "--batch is valid only with terminal or terminal-resume"};
    }
    if (parsed.reconnect && parsed.mode != TerminalArguments::Mode::open) {
        return Status{ErrorCode::invalid_argument,
                      "--reconnect is valid only with terminal PEER"};
    }
    if (parsed.reconnect && parsed.batch) {
        return Status{ErrorCode::invalid_argument,
                      "--reconnect is not valid with --batch"};
    }
    return parsed;
}

std::string safe_metadata(std::span<const std::uint8_t> bytes) {
    std::string text;
    text.reserve(bytes.size());
    for (const std::uint8_t byte : bytes) {
        if ((byte >= 0x20U && byte <= 0x7EU) || byte == '\t') {
            text.push_back(static_cast<char>(byte));
        } else {
            text.push_back('?');
        }
    }
    return text;
}

std::string safe_metadata_record(std::span<const std::uint8_t> bytes) {
    const bool terminated = !bytes.empty() && bytes.back() == '\n';
    if (terminated) bytes = bytes.first(bytes.size() - 1U);
    std::string text = safe_metadata(bytes);
    if (terminated) text.push_back('\n');
    return text;
}

Status write_all(
    int descriptor, std::span<const std::uint8_t> bytes,
    std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::write(
            descriptor,
            bytes.data() + static_cast<std::ptrdiff_t>(offset),
            bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count == 0) {
            return Status{ErrorCode::io_error,
                          "terminal output descriptor accepted zero bytes"};
        }
        if (count < 0 && errno == EINTR) continue;
        if (count < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            const auto now = std::chrono::steady_clock::now();
            if (now >= deadline) {
                return Status{ErrorCode::timeout,
                              "local terminal output deadline elapsed"};
            }
            const auto remaining =
                std::chrono::duration_cast<std::chrono::milliseconds>(
                    deadline - now);
            struct pollfd descriptor_state {descriptor, POLLOUT, 0};
            int ready = -1;
            do {
                ready = ::poll(
                    &descriptor_state, 1U,
                    static_cast<int>(std::min<std::int64_t>(
                        remaining.count(), INT_MAX)));
            } while (ready < 0 && errno == EINTR);
            if (ready > 0 &&
                (descriptor_state.revents & POLLOUT) != 0) {
                continue;
            }
            if (ready == 0) {
                return Status{ErrorCode::timeout,
                              "local terminal output deadline elapsed"};
            }
        }
        return Status{ErrorCode::io_error,
                      "unable to write terminal output: " +
                          std::string(std::strerror(errno))};
    }
    return Status::success();
}

class SignalScope {
  public:
    Status install() noexcept {
        struct sigaction action {};
        action.sa_handler = handle_terminal_signal;
        ::sigemptyset(&action.sa_mask);
        action.sa_flags = 0;
        if (::sigaction(SIGINT, &action, &old_interrupt_) != 0) {
            return failure("SIGINT");
        }
        interrupt_installed_ = true;
        if (::sigaction(SIGTERM, &action, &old_terminate_) != 0) {
            return failure("SIGTERM");
        }
        terminate_installed_ = true;
        if (::sigaction(SIGWINCH, &action, &old_resize_) != 0) {
            return failure("SIGWINCH");
        }
        resize_installed_ = true;
        g_terminal_signal = 0;
        g_terminal_resize = 1;
        return Status::success();
    }

    ~SignalScope() { restore(); }
    SignalScope(const SignalScope &) = delete;
    SignalScope &operator=(const SignalScope &) = delete;
    SignalScope() = default;

  private:
    static Status failure(std::string_view name) noexcept {
        return Status{ErrorCode::io_error,
                      "unable to install " + std::string(name) +
                          " handler: " + std::string(std::strerror(errno))};
    }

    void restore() noexcept {
        if (resize_installed_) {
            static_cast<void>(::sigaction(SIGWINCH, &old_resize_, nullptr));
        }
        if (terminate_installed_) {
            static_cast<void>(::sigaction(SIGTERM, &old_terminate_, nullptr));
        }
        if (interrupt_installed_) {
            static_cast<void>(::sigaction(SIGINT, &old_interrupt_, nullptr));
        }
    }

    struct sigaction old_interrupt_ {};
    struct sigaction old_terminate_ {};
    struct sigaction old_resize_ {};
    bool interrupt_installed_{false};
    bool terminate_installed_{false};
    bool resize_installed_{false};
};

class RawTerminalScope {
  public:
    Status enable() noexcept {
        if (::isatty(STDIN_FILENO) != 1 || ::isatty(STDOUT_FILENO) != 1) {
            return Status::success();
        }
        if (::tcgetattr(STDIN_FILENO, &saved_) != 0) {
            return Status{ErrorCode::io_error,
                          "unable to read local terminal attributes: " +
                              std::string(std::strerror(errno))};
        }
        struct termios raw = saved_;
        ::cfmakeraw(&raw);
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;
        if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) != 0) {
            return Status{ErrorCode::io_error,
                          "unable to enter local raw terminal mode: " +
                              std::string(std::strerror(errno))};
        }
        active_ = true;
        return Status::success();
    }

    ~RawTerminalScope() { restore(); }
    RawTerminalScope() = default;
    RawTerminalScope(const RawTerminalScope &) = delete;
    RawTerminalScope &operator=(const RawTerminalScope &) = delete;

    [[nodiscard]] bool active() const noexcept { return active_; }

  private:
    void restore() noexcept {
        if (!active_) return;
        for (;;) {
            if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &saved_) == 0) break;
            if (errno != EINTR) break;
        }
        active_ = false;
    }

    struct termios saved_ {};
    bool active_{false};
};

std::pair<std::uint16_t, std::uint16_t> terminal_dimensions() noexcept {
    struct winsize size {};
    int result = ::ioctl(STDIN_FILENO, TIOCGWINSZ, &size);
    if (result != 0) result = ::ioctl(STDOUT_FILENO, TIOCGWINSZ, &size);
    if (result != 0 || size.ws_col == 0U || size.ws_row == 0U ||
        size.ws_col > 1000U || size.ws_row > 1000U) {
        return {80U, 24U};
    }
    return {size.ws_col, size.ws_row};
}

Status send_resize(
    local::TerminalConnection &connection, std::uint64_t stream_id,
    std::chrono::milliseconds timeout) {
    const auto [columns, rows] = terminal_dimensions();
    local::TerminalPacket packet;
    packet.type = local::TerminalPacketType::resize;
    packet.stream_id = stream_id;
    packet.payload = {
        static_cast<std::uint8_t>(columns >> 8U),
        static_cast<std::uint8_t>(columns),
        static_cast<std::uint8_t>(rows >> 8U),
        static_cast<std::uint8_t>(rows),
    };
    return connection.send(packet, timeout);
}

Status send_control(
    local::TerminalConnection &connection, std::uint64_t stream_id,
    local::TerminalPacketType type, std::chrono::milliseconds timeout) {
    local::TerminalPacket packet;
    packet.type = type;
    packet.stream_id = stream_id;
    return connection.send(packet, timeout);
}

struct OpenResult {
    local::TerminalOpened opened;
    std::optional<local::TerminalOutputGap> initial_gap;
};

Result<OpenResult> await_opened(
    local::TerminalConnection &connection, std::uint64_t stream_id,
    std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    OpenResult result;
    for (;;) {
        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) {
            return Status{ErrorCode::timeout,
                          "Ratox terminal OPEN deadline elapsed"};
        }
        auto packet = connection.receive(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                deadline - now));
        if (!packet) return packet.status();
        SensitiveVectorGuard wipe_packet(packet.value().payload);
        // Before OPEN commits, the single-client server may reject a queued
        // contender or expire a silent handshake without reading the
        // contender's random stream ID. Such terminal ERROR packets are
        // connection-scoped and authenticated by the private Unix socket and
        // peer credentials. Every successful/progress packet remains bound to
        // the exact requested stream ID.
        if (packet.value().type == local::TerminalPacketType::error) {
            return Status{
                packet.value().status,
                safe_metadata(packet.value().payload)};
        }
        if (packet.value().stream_id != stream_id) {
            return Status{ErrorCode::protocol_error,
                          "local terminal server changed the stream ID"};
        }
        switch (packet.value().type) {
            case local::TerminalPacketType::opened: {
                auto opened = local::decode_terminal_opened(
                    packet.value().payload);
                if (!opened) return opened.status();
                if (result.initial_gap &&
                    result.initial_gap->retained_base_sequence !=
                        opened.value().next_output_sequence) {
                    return Status{
                        ErrorCode::protocol_error,
                        "local terminal OPENED output cursor contradicts the preceding OUTPUT_GAP"};
                }
                result.opened = opened.value();
                return result;
            }
            case local::TerminalPacketType::output_gap: {
                if (result.initial_gap) {
                    return Status{
                        ErrorCode::protocol_error,
                        "local terminal server repeated OUTPUT_GAP before OPENED"};
                }
                auto gap = local::decode_terminal_output_gap(
                    packet.value().payload);
                if (!gap) return gap.status();
                result.initial_gap = gap.value();
                break;
            }
            case local::TerminalPacketType::error:
                // Handled before stream-ID validation above.
                return Status{ErrorCode::internal_error,
                              "unreachable local terminal error branch"};
            case local::TerminalPacketType::pong:
                break;
            case local::TerminalPacketType::open:
            case local::TerminalPacketType::input:
            case local::TerminalPacketType::resize:
            case local::TerminalPacketType::detach:
            case local::TerminalPacketType::close:
            case local::TerminalPacketType::output_ack:
            case local::TerminalPacketType::ping:
            case local::TerminalPacketType::output:
            case local::TerminalPacketType::exit_status:
            case local::TerminalPacketType::detached:
            case local::TerminalPacketType::closed:
                return Status{ErrorCode::protocol_error,
                              "local terminal server replied before OPENED with an invalid packet"};
        }
    }
}

enum class EscapeAction : std::uint8_t { none, detach, close };

struct FilteredInput {
    std::vector<std::uint8_t> bytes;
    EscapeAction action{EscapeAction::none};
    bool help{false};
};

class EscapeFilter {
  public:
    FilteredInput process(std::span<const std::uint8_t> input) {
        FilteredInput result;
        result.bytes.reserve(input.size() + (pending_tilde_ ? 1U : 0U));
        for (const std::uint8_t byte : input) {
            if (pending_tilde_) {
                pending_tilde_ = false;
                if (byte == static_cast<std::uint8_t>('.')) {
                    result.action = EscapeAction::close;
                    return result;
                }
                if (byte == static_cast<std::uint8_t>('d') ||
                    byte == static_cast<std::uint8_t>('D')) {
                    result.action = EscapeAction::detach;
                    return result;
                }
                if (byte == static_cast<std::uint8_t>('?')) {
                    result.help = true;
                    line_start_ = true;
                    continue;
                }
                result.bytes.push_back(static_cast<std::uint8_t>('~'));
                if (byte == static_cast<std::uint8_t>('~')) {
                    line_start_ = false;
                    continue;
                }
                result.bytes.push_back(byte);
                line_start_ = byte == static_cast<std::uint8_t>('\n') ||
                              byte == static_cast<std::uint8_t>('\r');
                continue;
            }
            if (line_start_ && byte == static_cast<std::uint8_t>('~')) {
                pending_tilde_ = true;
                continue;
            }
            result.bytes.push_back(byte);
            line_start_ = byte == static_cast<std::uint8_t>('\n') ||
                          byte == static_cast<std::uint8_t>('\r');
        }
        return result;
    }

  private:
    bool line_start_{true};
    bool pending_tilde_{false};
};

Status send_input(
    local::TerminalConnection &connection, std::uint64_t stream_id,
    std::uint64_t &sequence, std::span<const std::uint8_t> bytes,
    std::chrono::milliseconds timeout) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const std::size_t count = std::min(
            local::kTerminalMaxPayloadSize, bytes.size() - offset);
        if (count > std::numeric_limits<std::uint64_t>::max() - sequence) {
            return Status{ErrorCode::resource_exhausted,
                          "local terminal input sequence exhausted"};
        }
        local::TerminalPacket packet;
        packet.type = local::TerminalPacketType::input;
        packet.stream_id = stream_id;
        packet.sequence = sequence;
        packet.payload.assign(
            bytes.begin() + static_cast<std::ptrdiff_t>(offset),
            bytes.begin() + static_cast<std::ptrdiff_t>(offset + count));
        SensitiveVectorGuard wipe_packet(packet.payload);
        const Status sent = connection.send(packet, timeout);
        if (!sent.ok()) return sent;
        sequence += static_cast<std::uint64_t>(count);
        offset += count;
    }
    return Status::success();
}

Status acknowledge_output(
    local::TerminalConnection &connection, std::uint64_t stream_id,
    std::uint64_t sequence, std::chrono::milliseconds timeout) {
    local::TerminalPacket packet;
    packet.type = local::TerminalPacketType::output_ack;
    packet.stream_id = stream_id;
    packet.sequence = sequence;
    return connection.send(packet, timeout);
}

int exit_code_for(const local::TerminalExitStatus &status) noexcept {
    if (status.kind == 0U) {
        return static_cast<int>(std::min<std::uint32_t>(status.code, 255U));
    }
    if (status.kind == 1U) {
        return static_cast<int>(std::min<std::uint32_t>(
            128U + static_cast<std::uint32_t>(status.signal), 255U));
    }
    return 255;
}

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

Status resolve_terminal_peer(TerminalArguments &arguments) {
    if (arguments.peer_selector.empty()) return Status::success();
    auto selector = peer_alias::parse_selector(arguments.peer_selector);
    if (!selector) return selector.status();
    if (selector.value().kind == peer_alias::SelectorKind::public_key) {
        arguments.peer = selector.value().public_key;
        return Status::success();
    }

    local::ControlPacket request;
    request.kind = local::ControlKind::request;
    auto request_id = security::random_u64_nonzero();
    if (!request_id) return request_id.status();
    request.request_id = request_id.value();
    if (selector.value().kind == peer_alias::SelectorKind::alias) {
        auto payload = peer_alias::encode_name_request(
            selector.value().alias);
        if (!payload) return payload.status();
        request.operation = local::ControlOperation::peer_alias_resolve;
        request.payload = std::move(payload).value();
    } else {
        request.operation = local::ControlOperation::transport_peer_list;
    }
    auto response = local::control_request(
        arguments.runtime / "control.sock", request, arguments.timeout);
    if (!response) return response.status();
    SensitiveVectorGuard wipe_response(response.value().payload);
    if (response.value().status != ErrorCode::ok) {
        return Status{response.value().status,
                      safe_metadata(response.value().payload)};
    }
    if (selector.value().kind == peer_alias::SelectorKind::alias) {
        if (response.value().payload.size() != arguments.peer.size()) {
            return Status{ErrorCode::protocol_error,
                          "peer alias resolve returned a malformed key"};
        }
        std::copy(response.value().payload.begin(),
                  response.value().payload.end(), arguments.peer.begin());
        return Status::success();
    }
    auto peers = local::decode_peer_list(response.value().payload);
    if (!peers) return peers.status();
    const auto found = std::find_if(
        peers.value().begin(), peers.value().end(),
        [&selector](const TransportPeer &peer) {
            return peer.friend_number == selector.value().friend_number;
        });
    if (found == peers.value().end()) {
        return Status{ErrorCode::not_found,
                      "no Tox friend matches the selected friend number"};
    }
    std::copy(found->public_key.begin(), found->public_key.end(),
              arguments.peer.begin());
    return Status::success();
}

int run_lifecycle_control(const TerminalArguments &arguments) {
    local::ControlPacket request;
    request.kind = local::ControlKind::request;
    auto request_id = security::random_u64_nonzero();
    if (!request_id) {
        std::cerr << request_id.status().message() << '\n';
        return 3;
    }
    request.request_id = request_id.value();
    if (arguments.mode == TerminalArguments::Mode::sessions) {
        request.operation = local::ControlOperation::ratox_client_session_list;
        if (!all_zero(arguments.peer)) {
            request.payload.assign(arguments.peer.begin(), arguments.peer.end());
        }
    } else {
        request.operation = local::ControlOperation::ratox_client_session_close;
        request.payload.assign(arguments.session.begin(), arguments.session.end());
        if (!all_zero(arguments.peer)) {
            request.payload.insert(
                request.payload.end(), arguments.peer.begin(),
                arguments.peer.end());
        }
    }
    auto response = local::control_request(
        arguments.runtime / "control.sock", request, arguments.timeout);
    if (!response) {
        std::cerr << response.status().message() << '\n';
        return 3;
    }
    SensitiveVectorGuard wipe_response(response.value().payload);
    if (response.value().status != ErrorCode::ok) {
        std::cerr << "error=" << local::to_string(response.value().status)
                  << " message="
                  << safe_metadata(response.value().payload) << '\n';
        return 4;
    }
    std::cout << safe_metadata_record(response.value().payload);
    return 0;
}

Result<int> run_stream(
    local::TerminalConnection &connection, std::uint64_t stream_id,
    const OpenResult &opened, std::chrono::milliseconds timeout,
    bool batch) {
    RawTerminalScope raw_terminal;
    if (!batch) {
        const Status raw = raw_terminal.enable();
        if (!raw.ok()) return raw;
    }

    if (!batch) {
        std::cerr << "Ratox session=" << security::hex(opened.opened.session_id)
                  << " escape=~. close, ~d detach, ~~ literal, ~? help\r\n";
    }
    if (opened.initial_gap) {
        if (!batch) {
            std::cerr << "Ratox output-gap retained-base="
                      << opened.initial_gap->retained_base_sequence
                      << " produced-next="
                      << opened.initial_gap->produced_next_sequence << "\r\n";
        }
    }
    std::cerr.flush();

    std::uint64_t input_sequence = opened.opened.next_input_sequence;
    std::uint64_t output_sequence = opened.opened.next_output_sequence;
    if (opened.initial_gap) {
        output_sequence = opened.initial_gap->retained_base_sequence;
    }
    EscapeFilter filter;
    bool input_closed = false;
    constexpr auto kHeartbeatInterval = std::chrono::seconds(1);
    constexpr std::uint32_t kHeartbeatFailureSamples = 3U;
    auto next_heartbeat =
        std::chrono::steady_clock::now() + kHeartbeatInterval;
    bool heartbeat_outstanding = false;
    std::uint32_t heartbeat_failures = 0U;
    bool heartbeat_warning = false;

    while (true) {
        if (g_terminal_signal != 0) {
            const int signal_number = g_terminal_signal;
            static_cast<void>(send_control(
                connection, stream_id, local::TerminalPacketType::detach,
                std::chrono::milliseconds{100}));
            return 128 + signal_number;
        }
        if (g_terminal_resize != 0) {
            g_terminal_resize = 0;
            const Status resized = send_resize(connection, stream_id, timeout);
            if (!resized.ok()) return resized;
        }
        const auto heartbeat_now = std::chrono::steady_clock::now();
        if (!input_closed && heartbeat_now >= next_heartbeat) {
            if (heartbeat_outstanding) {
                heartbeat_failures = std::min(
                    kHeartbeatFailureSamples,
                    heartbeat_failures + 1U);
                if (heartbeat_failures >= kHeartbeatFailureSamples &&
                    !heartbeat_warning) {
                    std::cerr << "\r\nRatox heartbeat: remote attachment is unresponsive; session retained for authoritative route loss or manual detach\r\n";
                    std::cerr.flush();
                    heartbeat_warning = true;
                }
            }
            const Status pinged = send_control(
                connection, stream_id, local::TerminalPacketType::ping,
                timeout);
            if (!pinged.ok()) return pinged;
            heartbeat_outstanding = true;
            next_heartbeat = heartbeat_now + kHeartbeatInterval;
        }

        std::array<struct pollfd, 2U> descriptors{{
            {connection.native_handle(), POLLIN, 0},
            {STDIN_FILENO, static_cast<short>(input_closed ? 0 : POLLIN), 0},
        }};
        int ready = -1;
        do {
            ready = ::poll(descriptors.data(), descriptors.size(), 100);
        } while (ready < 0 && errno == EINTR &&
                 g_terminal_signal == 0 && g_terminal_resize == 0);
        if (ready < 0) {
            return Status{ErrorCode::io_error,
                          "unable to poll terminal streams: " +
                              std::string(std::strerror(errno))};
        }
        if (ready == 0) continue;

        if ((descriptors[0U].revents & POLLIN) != 0) {
            for (;;) {
                auto packet = connection.receive(std::chrono::milliseconds::zero());
                if (!packet) {
                    if (packet.status().code() == ErrorCode::timeout) break;
                    return packet.status();
                }
                SensitiveVectorGuard wipe_packet(packet.value().payload);
                if (packet.value().stream_id != stream_id) {
                    return Status{ErrorCode::protocol_error,
                                  "local terminal server changed the stream ID"};
                }
                switch (packet.value().type) {
                    case local::TerminalPacketType::output: {
                        const std::uint64_t sequence = packet.value().sequence;
                        if (packet.value().payload.size() >
                            std::numeric_limits<std::uint64_t>::max() - sequence) {
                            return Status{ErrorCode::protocol_error,
                                          "local terminal output sequence overflowed"};
                        }
                        const std::uint64_t next = sequence +
                            static_cast<std::uint64_t>(packet.value().payload.size());
                        if (sequence != output_sequence) {
                            return Status{ErrorCode::protocol_error,
                                          "local terminal output did not begin at the exact next byte"};
                        }
                        const Status written = write_all(
                            STDOUT_FILENO, packet.value().payload, timeout);
                        if (!written.ok()) return written;
                        output_sequence = next;
                        const Status acknowledged = acknowledge_output(
                            connection, stream_id, output_sequence, timeout);
                        if (!acknowledged.ok()) return acknowledged;
                        break;
                    }
                    case local::TerminalPacketType::output_gap: {
                        auto gap = local::decode_terminal_output_gap(
                            packet.value().payload);
                        if (!gap) return gap.status();
                        if (gap.value().retained_base_sequence < output_sequence) {
                            return Status{
                                ErrorCode::protocol_error,
                                "local terminal output gap moved behind rendered output"};
                        }
                        output_sequence = gap.value().retained_base_sequence;
                        if (!batch) {
                            std::cerr << "\r\nRatox output-gap retained-base="
                                      << gap.value().retained_base_sequence
                                      << " produced-next="
                                      << gap.value().produced_next_sequence
                                      << "\r\n";
                            std::cerr.flush();
                        }
                        break;
                    }
                    case local::TerminalPacketType::exit_status: {
                        auto status = local::decode_terminal_exit_status(
                            packet.value().payload);
                        if (!status) return status.status();
                        return exit_code_for(status.value());
                    }
                    case local::TerminalPacketType::detached:
                        return 0;
                    case local::TerminalPacketType::closed:
                        return 0;
                    case local::TerminalPacketType::error:
                        return Status{
                            packet.value().status,
                            safe_metadata(packet.value().payload)};
                    case local::TerminalPacketType::pong:
                        heartbeat_outstanding = false;
                        heartbeat_failures = 0U;
                        if (heartbeat_warning) {
                            std::cerr << "\r\nRatox heartbeat: remote attachment responsive\r\n";
                            std::cerr.flush();
                            heartbeat_warning = false;
                        }
                        break;
                    case local::TerminalPacketType::opened:
                        return Status{ErrorCode::protocol_error,
                                      "local terminal server repeated OPENED after attachment"};
                    case local::TerminalPacketType::open:
                    case local::TerminalPacketType::input:
                    case local::TerminalPacketType::resize:
                    case local::TerminalPacketType::detach:
                    case local::TerminalPacketType::close:
                    case local::TerminalPacketType::output_ack:
                    case local::TerminalPacketType::ping:
                        return Status{ErrorCode::protocol_error,
                                      "local terminal server sent a client-only packet"};
                }
            }
        }

        if (!input_closed && (descriptors[1U].revents & POLLIN) != 0) {
            std::array<std::uint8_t, local::kTerminalMaxPayloadSize> input{};
            SensitiveArrayGuard wipe_input(input);
            const ssize_t count = ::read(STDIN_FILENO, input.data(), input.size());
            if (count > 0) {
                const auto bytes = std::span<const std::uint8_t>{input}.first(
                    static_cast<std::size_t>(count));
                FilteredInput filtered;
                if (raw_terminal.active()) {
                    filtered = filter.process(bytes);
                } else {
                    filtered.bytes.assign(bytes.begin(), bytes.end());
                }
                SensitiveVectorGuard wipe_filtered(filtered.bytes);
                if (filtered.help) {
                    std::cerr << "\r\n~. close remote process; ~d detach; ~~ send ~; ~? help\r\n";
                    std::cerr.flush();
                }
                const Status sent = send_input(
                    connection, stream_id, input_sequence,
                    filtered.bytes, timeout);
                if (!sent.ok()) return sent;
                if (filtered.action != EscapeAction::none) {
                    const auto type = filtered.action == EscapeAction::close
                        ? local::TerminalPacketType::close
                        : local::TerminalPacketType::detach;
                    const Status controlled = send_control(
                        connection, stream_id, type, timeout);
                    if (!controlled.ok()) return controlled;
                    input_closed = true;
                }
            } else if (count == 0) {
                if (batch) {
                    // A PTY has no half-close operation. Inject its canonical
                    // end-of-input character and retain the attachment so a
                    // fixed profile can finish and return its exit status.
                    const std::array<std::uint8_t, 1U> end_of_input{0x04U};
                    const Status sent = send_input(
                        connection, stream_id, input_sequence,
                        end_of_input, timeout);
                    if (!sent.ok()) return sent;
                } else {
                    const Status detached = send_control(
                        connection, stream_id,
                        local::TerminalPacketType::detach, timeout);
                    if (!detached.ok()) return detached;
                }
                input_closed = true;
            } else if (errno != EINTR && errno != EAGAIN && errno != EWOULDBLOCK) {
                return Status{ErrorCode::io_error,
                              "unable to read terminal input: " +
                                  std::string(std::strerror(errno))};
            }
        }

        if (!input_closed &&
            (descriptors[1U].revents & (POLLHUP | POLLERR | POLLNVAL)) != 0 &&
            (descriptors[1U].revents & POLLIN) == 0) {
            if (batch) {
                const std::array<std::uint8_t, 1U> end_of_input{0x04U};
                const Status sent = send_input(
                    connection, stream_id, input_sequence,
                    end_of_input, timeout);
                if (!sent.ok()) return sent;
            } else {
                const Status detached = send_control(
                    connection, stream_id, local::TerminalPacketType::detach,
                    timeout);
                if (!detached.ok()) return detached;
            }
            input_closed = true;
        }
        if ((descriptors[0U].revents & (POLLHUP | POLLERR | POLLNVAL)) != 0 &&
            (descriptors[0U].revents & POLLIN) == 0) {
            return Status{ErrorCode::unavailable,
                          "local terminal server closed the stream"};
        }
    }
}

[[nodiscard]] bool reconnect_retryable(const Status &status) noexcept {
    return status.code() == ErrorCode::unavailable ||
           status.code() == ErrorCode::timeout;
}

[[nodiscard]] bool wait_for_reconnect_retry() noexcept {
    constexpr int kSliceMilliseconds = 100;
    constexpr int kSlices = 5;
    for (int slice = 0; slice < kSlices; ++slice) {
        if (g_terminal_signal != 0) return false;
        int result = -1;
        do {
            result = ::poll(nullptr, 0U, kSliceMilliseconds);
        } while (result < 0 && errno == EINTR && g_terminal_signal == 0);
        if (result < 0 && errno != EINTR) return false;
    }
    return g_terminal_signal == 0;
}

}  // namespace

bool is_terminal_cli_invocation(
    std::span<const std::string_view> arguments) noexcept {
    for (std::size_t index = 0U; index < arguments.size(); ++index) {
        if (option_takes_value(arguments[index])) {
            ++index;
            continue;
        }
        if (arguments[index] == "--batch" ||
            arguments[index] == "--reconnect") continue;
        if (arguments[index].starts_with("--")) return false;
        return is_cli_command_kind(
            arguments[index], CliCommandKind::terminal);
    }
    return false;
}

int run_terminal_cli(std::span<const std::string_view> arguments) {
    auto parsed = parse_terminal_arguments(arguments);
    if (!parsed) {
        std::cerr << parsed.status().message() << '\n';
        return 2;
    }

    const Status peer_resolved = resolve_terminal_peer(parsed.value());
    if (!peer_resolved.ok()) {
        std::cerr << peer_resolved.message() << '\n';
        return peer_resolved.code() == ErrorCode::invalid_argument ? 2 : 3;
    }

    if (parsed.value().mode == TerminalArguments::Mode::sessions ||
        parsed.value().mode == TerminalArguments::Mode::close) {
        return run_lifecycle_control(parsed.value());
    }

    SignalScope signals;
    const Status signal_status = signals.install();
    if (!signal_status.ok()) {
        std::cerr << signal_status.message() << '\n';
        return 3;
    }

    std::optional<local::TerminalOpened> retained;
    bool resume_only = parsed.value().mode == TerminalArguments::Mode::resume;
    std::uint64_t retry_attempts = 0U;
    bool waiting_announced = false;
    for (;;) {
        auto connection = local::TerminalConnection::connect(
            parsed.value().runtime / "terminal.sock", parsed.value().timeout);
        if (!connection) {
            if (parsed.value().reconnect && retained &&
                reconnect_retryable(connection.status())) {
                ++retry_attempts;
                if (!waiting_announced) {
                    std::cerr << "\r\nRatox reconnect: waiting for the exact retained session on a higher authenticated epoch\r\n";
                    std::cerr.flush();
                    waiting_announced = true;
                }
                if (wait_for_reconnect_retry()) continue;
                return g_terminal_signal == 0 ? 3 : 128 + g_terminal_signal;
            }
            std::cerr << connection.status().message() << '\n';
            return 3;
        }
        auto stream_id = security::random_u64_nonzero();
        if (!stream_id) {
            std::cerr << stream_id.status().message() << '\n';
            return 3;
        }

        const auto [columns, rows] = terminal_dimensions();
        local::TerminalOpenRequest request;
        request.peer_public_key = parsed.value().peer;
        request.session_id = retained ? retained->session_id
                                      : parsed.value().session;
        request.columns = columns;
        request.rows = rows;
        request.mode = resume_only
            ? local::TerminalOpenMode::resume_only
            : local::TerminalOpenMode::new_session;
        auto payload = local::encode_terminal_open(request);
        if (!payload) {
            std::cerr << payload.status().message() << '\n';
            return 2;
        }
        SensitiveVectorGuard wipe_open_payload(payload.value());
        local::TerminalPacket open;
        open.type = local::TerminalPacketType::open;
        open.stream_id = stream_id.value();
        open.payload = std::move(payload).value();
        SensitiveVectorGuard wipe_open_packet(open.payload);
        const Status sent = connection.value().send(
            open, parsed.value().timeout);
        if (!sent.ok()) {
            if (parsed.value().reconnect && retained &&
                reconnect_retryable(sent)) {
                ++retry_attempts;
                if (!waiting_announced) {
                    std::cerr << "\r\nRatox reconnect: waiting for the exact retained session on a higher authenticated epoch\r\n";
                    std::cerr.flush();
                    waiting_announced = true;
                }
                if (wait_for_reconnect_retry()) continue;
                return g_terminal_signal == 0 ? 3 : 128 + g_terminal_signal;
            }
            std::cerr << sent.message() << '\n';
            return 3;
        }
        auto opened = await_opened(
            connection.value(), stream_id.value(), parsed.value().timeout);
        if (!opened) {
            if (parsed.value().reconnect && retained &&
                reconnect_retryable(opened.status())) {
                ++retry_attempts;
                if (!waiting_announced) {
                    std::cerr << "\r\nRatox reconnect: waiting for the exact retained session on a higher authenticated epoch\r\n";
                    std::cerr.flush();
                    waiting_announced = true;
                }
                if (wait_for_reconnect_retry()) continue;
                return g_terminal_signal == 0 ? 3 : 128 + g_terminal_signal;
            }
            std::cerr << opened.status().message() << '\n';
            return 3;
        }
        if (retained &&
            (opened.value().opened.session_id != retained->session_id ||
             opened.value().opened.incarnation != retained->incarnation ||
             opened.value().opened.generation <= retained->generation)) {
            std::cerr << "Ratox reconnect changed the retained session, incarnation, or generation\n";
            return 3;
        }
        retained = opened.value().opened;
        if (waiting_announced) {
            std::cerr << "Ratox reconnect: resumed exact session generation="
                      << retained->generation << " attempts="
                      << retry_attempts << "\r\n";
            std::cerr.flush();
            waiting_announced = false;
            retry_attempts = 0U;
        }
        auto result = run_stream(
            connection.value(), stream_id.value(), opened.value(),
            parsed.value().timeout, parsed.value().batch);
        if (result) return result.value();
        if (!parsed.value().reconnect || !retained ||
            result.status().code() != ErrorCode::unavailable) {
            std::cerr << "\r\n" << result.status().message() << '\n';
            return 3;
        }
        resume_only = true;
        ++retry_attempts;
        if (!waiting_announced) {
            std::cerr << "\r\nRatox reconnect: waiting for the exact retained session on a higher authenticated epoch\r\n";
            std::cerr.flush();
            waiting_announced = true;
        }
        if (!wait_for_reconnect_retry()) {
            return g_terminal_signal == 0 ? 3 : 128 + g_terminal_signal;
        }
    }
}

}  // namespace iotox
