#include "iotox/local/terminal_protocol.hpp"
#include "iotox/local/terminal_socket.hpp"
#include "iotox/status.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <deque>
#include <filesystem>
#include <fcntl.h>
#include <iostream>
#include <mutex>
#include <spawn.h>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

extern char **environ;

namespace {

using namespace std::chrono_literals;
using iotox::ErrorCode;
using iotox::Status;
using iotox::local::TerminalOpenMode;
using iotox::local::TerminalOpenRequest;
using iotox::local::TerminalOpened;
using iotox::local::TerminalPacket;
using iotox::local::TerminalPacketType;
using iotox::local::TerminalServer;

void require(bool condition, std::string_view message) {
    if (!condition) throw std::runtime_error(std::string(message));
}

void require_ok(const Status &status, std::string_view context) {
    if (!status.ok()) {
        throw std::runtime_error(
            std::string(context) + ": " + status.message());
    }
}

template <typename Predicate>
bool eventually(
    Predicate predicate,
    std::chrono::milliseconds timeout = 3000ms) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    do {
        if (predicate()) return true;
        std::this_thread::sleep_for(2ms);
    } while (std::chrono::steady_clock::now() < deadline);
    return predicate();
}

class TempDirectory {
  public:
    TempDirectory() {
        std::array<char, 64U> pattern{};
        constexpr std::string_view value =
            "/tmp/iotox-terminal-controller-process-XXXXXX";
        std::copy(value.begin(), value.end(), pattern.begin());
        char *created = ::mkdtemp(pattern.data());
        if (created == nullptr) {
            throw std::runtime_error(
                "mkdtemp failed: " + std::string(std::strerror(errno)));
        }
        path_ = created;
        if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0) {
            throw std::runtime_error(
                "chmod temp directory failed: " +
                std::string(std::strerror(errno)));
        }
    }

    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    TempDirectory(const TempDirectory &) = delete;
    TempDirectory &operator=(const TempDirectory &) = delete;

    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

class SpawnFileActions {
  public:
    SpawnFileActions() : error_(::posix_spawn_file_actions_init(&actions_)) {}
    ~SpawnFileActions() {
        if (error_ == 0) {
            static_cast<void>(::posix_spawn_file_actions_destroy(&actions_));
        }
    }
    SpawnFileActions(const SpawnFileActions &) = delete;
    SpawnFileActions &operator=(const SpawnFileActions &) = delete;

    [[nodiscard]] int error() const noexcept { return error_; }
    [[nodiscard]] posix_spawn_file_actions_t *get() noexcept { return &actions_; }

  private:
    posix_spawn_file_actions_t actions_{};
    int error_{0};
};

struct ProcessResult {
    int exit_code{128};
    std::string output;
};

class ChildProcess {
  public:
    ChildProcess() = default;
    ChildProcess(pid_t process, int input, int output)
        : process_(process), input_(input), output_(output) {}
    ~ChildProcess() { cleanup(); }

    ChildProcess(const ChildProcess &) = delete;
    ChildProcess &operator=(const ChildProcess &) = delete;
    ChildProcess(ChildProcess &&other) noexcept
        : process_(std::exchange(other.process_, -1)),
          input_(std::exchange(other.input_, -1)),
          output_(std::exchange(other.output_, -1)) {}
    ChildProcess &operator=(ChildProcess &&other) noexcept {
        if (this == &other) return *this;
        cleanup();
        process_ = std::exchange(other.process_, -1);
        input_ = std::exchange(other.input_, -1);
        output_ = std::exchange(other.output_, -1);
        return *this;
    }

    [[nodiscard]] pid_t process() const noexcept { return process_; }

    void close_input() noexcept {
        if (input_ >= 0) {
            static_cast<void>(::close(input_));
            input_ = -1;
        }
    }

    ProcessResult wait(std::chrono::milliseconds timeout) {
        require(process_ > 0, "attempted to wait for an inactive child");
        const auto deadline = std::chrono::steady_clock::now() + timeout;
        int status = 0;
        for (;;) {
            const pid_t waited = ::waitpid(process_, &status, WNOHANG);
            if (waited == process_) break;
            if (waited < 0 && errno != EINTR) {
                throw std::runtime_error(
                    "waitpid failed: " + std::string(std::strerror(errno)));
            }
            if (std::chrono::steady_clock::now() >= deadline) {
                static_cast<void>(::kill(process_, SIGKILL));
                while (::waitpid(process_, &status, 0) < 0 && errno == EINTR) {}
                process_ = -1;
                close_input();
                const std::string output = read_output();
                throw std::runtime_error(
                    "child process deadline elapsed; output=" + output);
            }
            std::this_thread::sleep_for(2ms);
        }
        process_ = -1;
        close_input();
        ProcessResult result;
        if (WIFEXITED(status)) {
            result.exit_code = WEXITSTATUS(status);
        } else if (WIFSIGNALED(status)) {
            result.exit_code = 128 + WTERMSIG(status);
        }
        result.output = read_output();
        return result;
    }

    ProcessResult signal_and_wait(
        int signal_number, std::chrono::milliseconds timeout) {
        require(process_ > 0, "attempted to signal an inactive child");
        if (::kill(process_, signal_number) != 0) {
            throw std::runtime_error(
                "kill failed: " + std::string(std::strerror(errno)));
        }
        return wait(timeout);
    }

  private:
    std::string read_output() noexcept {
        std::string output;
        if (output_ < 0) return output;
        std::array<char, 4096U> buffer{};
        for (;;) {
            const ssize_t count = ::read(output_, buffer.data(), buffer.size());
            if (count > 0) {
                output.append(buffer.data(), static_cast<std::size_t>(count));
                continue;
            }
            if (count < 0 && errno == EINTR) continue;
            break;
        }
        static_cast<void>(::close(output_));
        output_ = -1;
        return output;
    }

    void cleanup() noexcept {
        close_input();
        if (process_ > 0) {
            static_cast<void>(::kill(process_, SIGKILL));
            int status = 0;
            while (::waitpid(process_, &status, 0) < 0 && errno == EINTR) {}
            process_ = -1;
        }
        static_cast<void>(read_output());
    }

    pid_t process_{-1};
    int input_{-1};
    int output_{-1};
};

std::vector<char *> argv_for(std::vector<std::string> &arguments) {
    std::vector<char *> argv;
    argv.reserve(arguments.size() + 1U);
    for (std::string &argument : arguments) argv.push_back(argument.data());
    argv.push_back(nullptr);
    return argv;
}

ChildProcess spawn_iotox(
    const std::filesystem::path &iotox,
    const std::filesystem::path &runtime,
    std::vector<std::string> command,
    bool close_input) {
    int input_pipe[2]{};
    int output_pipe[2]{};
    if (::pipe2(input_pipe, O_CLOEXEC) != 0 ||
        ::pipe2(output_pipe, O_CLOEXEC) != 0) {
        const int saved_errno = errno;
        for (const int descriptor : input_pipe) {
            if (descriptor > 0) static_cast<void>(::close(descriptor));
        }
        for (const int descriptor : output_pipe) {
            if (descriptor > 0) static_cast<void>(::close(descriptor));
        }
        throw std::runtime_error(
            "pipe2 failed: " + std::string(std::strerror(saved_errno)));
    }

    SpawnFileActions actions;
    require(actions.error() == 0, "posix_spawn file actions initialization failed");
    const auto add_action = [](int error, std::string_view operation) {
        if (error != 0) {
            throw std::runtime_error(
                std::string(operation) + ": " + std::string(std::strerror(error)));
        }
    };
    add_action(
        ::posix_spawn_file_actions_adddup2(actions.get(), input_pipe[0], STDIN_FILENO),
        "posix_spawn stdin dup2 failed");
    add_action(
        ::posix_spawn_file_actions_adddup2(actions.get(), output_pipe[1], STDOUT_FILENO),
        "posix_spawn stdout dup2 failed");
    add_action(
        ::posix_spawn_file_actions_adddup2(actions.get(), output_pipe[1], STDERR_FILENO),
        "posix_spawn stderr dup2 failed");
    for (const int descriptor : {input_pipe[0], input_pipe[1],
                                 output_pipe[0], output_pipe[1]}) {
        add_action(
            ::posix_spawn_file_actions_addclose(actions.get(), descriptor),
            "posix_spawn close action failed");
    }

    std::vector<std::string> arguments{
        iotox.string(), "--runtime", runtime.string(),
        "--timeout-ms", "3000"};
    arguments.insert(
        arguments.end(),
        std::make_move_iterator(command.begin()),
        std::make_move_iterator(command.end()));
    std::vector<char *> argv = argv_for(arguments);

    pid_t child = -1;
    const int spawned = ::posix_spawn(
        &child, iotox.c_str(), actions.get(), nullptr, argv.data(), environ);
    static_cast<void>(::close(input_pipe[0]));
    static_cast<void>(::close(output_pipe[1]));
    if (spawned != 0) {
        static_cast<void>(::close(input_pipe[1]));
        static_cast<void>(::close(output_pipe[0]));
        throw std::runtime_error(
            "posix_spawn failed: " + std::string(std::strerror(spawned)));
    }

    ChildProcess process(child, input_pipe[1], output_pipe[0]);
    if (close_input) process.close_input();
    return process;
}

std::string hex(std::span<const std::uint8_t> bytes) {
    constexpr std::array<char, 16U> digits{
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
    std::string result;
    result.reserve(bytes.size() * 2U);
    for (const std::uint8_t byte : bytes) {
        result.push_back(digits[byte >> 4U]);
        result.push_back(digits[byte & 0x0FU]);
    }
    return result;
}

TerminalPacket opened_packet(
    const std::array<std::uint8_t, iotox::local::kTerminalSessionIdBytes> &session,
    std::uint64_t generation) {
    TerminalOpened opened;
    opened.session_id = session;
    opened.incarnation = 9U;
    opened.generation = generation;
    opened.next_input_sequence = 1U;
    opened.next_output_sequence = 1U;
    auto payload = iotox::local::encode_terminal_opened(opened);
    require(payload.ok(), payload.status().message());
    TerminalPacket packet;
    packet.type = TerminalPacketType::opened;
    packet.stream_id = 1U;
    packet.payload = std::move(payload).value();
    return packet;
}

struct FixtureState {
    std::mutex mutex;
    std::deque<TerminalPacket> outbound;
    std::array<std::uint8_t, iotox::local::kTerminalSessionIdBytes> session{};
    bool session_exists{false};
    bool attached{false};
    std::uint64_t generation{0U};
    std::uint64_t output_ack{0U};
    unsigned int opens{0U};
    unsigned int resumes{0U};
    unsigned int resume_attempts{0U};
    unsigned int resume_denials_remaining{0U};
    unsigned int disconnects{0U};
    unsigned int pings{0U};
    bool reply_to_pings{true};
    unsigned int detach_at_ping{0U};
    unsigned int route_loss_at_ping{0U};
    bool batch_exit_on_eot{false};
};

Status handle_packet(FixtureState &state, const TerminalPacket &packet) {
    std::scoped_lock lock(state.mutex);
    switch (packet.type) {
        case TerminalPacketType::open: {
            auto request = iotox::local::decode_terminal_open(packet.payload);
            if (!request) return request.status();
            if (request.value().mode == TerminalOpenMode::new_session) {
                if (state.session_exists) {
                    return Status{ErrorCode::resource_exhausted,
                                  "test session already exists"};
                }
                state.session_exists = true;
                state.attached = true;
                state.generation = 1U;
                ++state.opens;
                state.outbound.push_back(opened_packet(
                    state.session, state.generation));
                return Status::success();
            }
            if (request.value().mode != TerminalOpenMode::resume_only ||
                request.value().session_id != state.session ||
                !state.session_exists) {
                return Status{ErrorCode::not_found,
                              "terminal session is not available"};
            }
            if (state.attached) {
                return Status{ErrorCode::resource_exhausted,
                              "terminal session already has a controller"};
            }
            ++state.resume_attempts;
            if (state.resume_denials_remaining > 0U) {
                --state.resume_denials_remaining;
                return Status{ErrorCode::unavailable,
                              "higher authenticated epoch is not ready"};
            }
            state.attached = true;
            ++state.generation;
            ++state.resumes;
            state.outbound.push_back(opened_packet(
                state.session, state.generation));
            TerminalPacket output;
            output.type = TerminalPacketType::output;
            output.stream_id = 1U;
            output.sequence = 1U;
            constexpr std::string_view replay = "resumed-output\n";
            output.payload.assign(replay.begin(), replay.end());
            state.outbound.push_back(std::move(output));
            return Status::success();
        }
        case TerminalPacketType::resize:
            return Status::success();
        case TerminalPacketType::output_ack:
            state.output_ack = packet.sequence;
            return Status::success();
        case TerminalPacketType::detach: {
            state.attached = false;
            TerminalPacket detached;
            detached.type = TerminalPacketType::detached;
            detached.stream_id = 1U;
            state.outbound.push_back(std::move(detached));
            return Status::success();
        }
        case TerminalPacketType::close: {
            state.attached = false;
            state.session_exists = false;
            TerminalPacket closed;
            closed.type = TerminalPacketType::closed;
            closed.stream_id = 1U;
            state.outbound.push_back(std::move(closed));
            return Status::success();
        }
        case TerminalPacketType::ping: {
            ++state.pings;
            if (state.route_loss_at_ping != 0U &&
                state.pings >= state.route_loss_at_ping) {
                state.route_loss_at_ping = 0U;
                state.attached = false;
                TerminalPacket lost;
                lost.type = TerminalPacketType::error;
                lost.stream_id = 1U;
                lost.status = ErrorCode::unavailable;
                constexpr std::string_view detail =
                    "authoritative route loss retained the session";
                lost.payload.assign(detail.begin(), detail.end());
                state.outbound.push_back(std::move(lost));
                return Status::success();
            }
            if (state.detach_at_ping != 0U &&
                state.pings >= state.detach_at_ping) {
                state.attached = false;
                TerminalPacket detached;
                detached.type = TerminalPacketType::detached;
                detached.stream_id = 1U;
                state.outbound.push_back(std::move(detached));
                return Status::success();
            }
            if (!state.reply_to_pings) return Status::success();
            TerminalPacket pong;
            pong.type = TerminalPacketType::pong;
            pong.stream_id = 1U;
            state.outbound.push_back(std::move(pong));
            return Status::success();
        }
        case TerminalPacketType::input:
            if (state.batch_exit_on_eot && packet.payload.size() == 1U &&
                packet.payload.front() == 0x04U) {
                TerminalPacket output;
                output.type = TerminalPacketType::output;
                output.stream_id = 1U;
                output.sequence = 1U;
                constexpr std::string_view text = "batch-output\n";
                output.payload.assign(text.begin(), text.end());
                state.outbound.push_back(std::move(output));
                iotox::local::TerminalExitStatus status;
                status.kind = 0U;
                status.code = 7U;
                auto encoded = iotox::local::encode_terminal_exit_status(status);
                if (!encoded) return encoded.status();
                TerminalPacket exited;
                exited.type = TerminalPacketType::exit_status;
                exited.stream_id = 1U;
                exited.payload = std::move(encoded).value();
                state.outbound.push_back(std::move(exited));
            }
            return Status::success();
        case TerminalPacketType::opened:
        case TerminalPacketType::output:
        case TerminalPacketType::output_gap:
        case TerminalPacketType::exit_status:
        case TerminalPacketType::detached:
        case TerminalPacketType::closed:
        case TerminalPacketType::error:
        case TerminalPacketType::pong:
            return Status{ErrorCode::protocol_error,
                          "client sent a server-only packet"};
    }
    return Status{ErrorCode::protocol_error, "impossible terminal packet"};
}

std::vector<TerminalPacket> drain_packets(
    FixtureState &state, std::size_t maximum_packets);
void mark_disconnected(FixtureState &state);

void test_exact_session_reconnect_waits_for_higher_epoch(
    const std::filesystem::path &iotox) {
    TempDirectory runtime;
    FixtureState state;
    state.session.fill(0x61U);
    state.route_loss_at_ping = 1U;
    state.resume_denials_remaining = 2U;

    TerminalServer::Config config;
    config.socket_path = runtime.path() / "terminal.sock";
    config.poll_interval = 2ms;
    config.open_timeout = 500ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            return handle_packet(state, packet);
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            return drain_packets(state, maximum_packets);
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            mark_disconnected(state);
        });
    require_ok(server.start(), "start reconnect fixture server");

    std::array<std::uint8_t, iotox::local::kTerminalPeerPublicKeyBytes> peer{};
    peer.fill(0x82U);
    ChildProcess client = spawn_iotox(
        iotox, runtime.path(), {"--reconnect", "terminal", hex(peer)}, false);
    require(eventually([&] {
        std::scoped_lock lock(state.mutex);
        return state.opens == 1U && state.resume_attempts >= 3U &&
               state.resumes == 1U && state.generation == 2U &&
               state.attached;
    }, 7000ms), "terminal client did not wait through higher-epoch denial and resume exactly");
    client.close_input();
    const ProcessResult result = client.wait(5000ms);
    require(result.exit_code == 0,
            "reconnected terminal client did not detach cleanly");
    require(result.output.find(
                "Ratox reconnect: waiting for the exact retained session") !=
                std::string::npos,
            "reconnected terminal client did not expose its wait state; output=" +
                result.output);
    require(result.output.find(
                "Ratox reconnect: resumed exact session generation=2") !=
                std::string::npos,
            "reconnected terminal client did not expose exact resume; output=" +
                result.output);
    require(result.output.find("resumed-output\n") != std::string::npos,
            "reconnected terminal client did not render retained output");
    {
        std::scoped_lock lock(state.mutex);
        require(state.opens == 1U,
                "reconnect opened a replacement terminal session");
        require(state.resume_attempts == 3U && state.resumes == 1U,
                "reconnect did not preserve exact denied/successful attempt accounting");
        require(!state.attached,
                "reconnected terminal remained attached after stdin close");
    }
    server.stop();
}

void test_exact_session_reconnect_survives_repeated_loss(
    const std::filesystem::path &iotox) {
    TempDirectory runtime;
    FixtureState state;
    state.session.fill(0x62U);
    state.route_loss_at_ping = 1U;

    TerminalServer::Config config;
    config.socket_path = runtime.path() / "terminal.sock";
    config.poll_interval = 2ms;
    config.open_timeout = 500ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            return handle_packet(state, packet);
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            return drain_packets(state, maximum_packets);
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            mark_disconnected(state);
        });
    require_ok(server.start(), "start repeated reconnect fixture server");

    std::array<std::uint8_t, iotox::local::kTerminalPeerPublicKeyBytes> peer{};
    peer.fill(0x83U);
    ChildProcess client = spawn_iotox(
        iotox, runtime.path(), {"--reconnect", "terminal", hex(peer)}, false);
    const pid_t client_pid = client.process();
    require(eventually([&] {
        std::scoped_lock lock(state.mutex);
        return state.opens == 1U && state.resumes == 1U &&
               state.generation == 2U && state.attached;
    }, 7000ms), "terminal client did not complete its first exact reconnect");

    {
        std::scoped_lock lock(state.mutex);
        state.route_loss_at_ping = state.pings + 1U;
        state.resume_denials_remaining = 1U;
    }
    require(eventually([&] {
        std::scoped_lock lock(state.mutex);
        return state.opens == 1U && state.resumes == 2U &&
               state.generation == 3U && state.attached;
    }, 7000ms), "same terminal client did not complete its second exact reconnect");
    require(client.process() == client_pid,
            "repeated reconnect replaced the production CLI process");

    client.close_input();
    const ProcessResult result = client.wait(5000ms);
    require(result.exit_code == 0,
            "repeatedly reconnected terminal client did not detach cleanly");
    require(result.output.find(
                "Ratox reconnect: resumed exact session generation=2") !=
                std::string::npos,
            "first repeated reconnect marker is absent; output=" +
                result.output);
    require(result.output.find(
                "Ratox reconnect: resumed exact session generation=3") !=
                std::string::npos,
            "second repeated reconnect marker is absent; output=" +
                result.output);
    require(std::count(result.output.begin(), result.output.end(), '\n') >= 4,
            "repeated reconnect output capture is unexpectedly short");
    {
        std::scoped_lock lock(state.mutex);
        require(state.opens == 1U,
                "repeated reconnect opened a replacement terminal session");
        require(state.resumes == 2U && state.resume_attempts == 3U,
                "repeated reconnect attempt accounting is not exact");
        require(state.generation == 3U,
                "repeated reconnect did not advance each attachment generation");
        require(!state.attached,
                "repeatedly reconnected terminal remained attached after EOF");
    }
    server.stop();
}

std::vector<TerminalPacket> drain_packets(
    FixtureState &state, std::size_t maximum_packets) {
    std::scoped_lock lock(state.mutex);
    std::vector<TerminalPacket> result;
    result.reserve(std::min(maximum_packets, state.outbound.size()));
    while (!state.outbound.empty() && result.size() < maximum_packets) {
        result.push_back(std::move(state.outbound.front()));
        state.outbound.pop_front();
    }
    return result;
}

void mark_disconnected(FixtureState &state) {
    std::scoped_lock lock(state.mutex);
    state.attached = false;
    ++state.disconnects;
}

void test_controller_replacement_and_restart(
    const std::filesystem::path &iotox) {
    TempDirectory runtime;
    FixtureState state;
    state.session.fill(0x31U);

    TerminalServer::Config config;
    config.socket_path = runtime.path() / "terminal.sock";
    config.poll_interval = 2ms;
    config.open_timeout = 500ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            return handle_packet(state, packet);
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            return drain_packets(state, maximum_packets);
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            mark_disconnected(state);
        });
    require_ok(server.start(), "start terminal fixture server");

    std::array<std::uint8_t, iotox::local::kTerminalPeerPublicKeyBytes> peer{};
    peer.fill(0x52U);
    ChildProcess winner = spawn_iotox(
        iotox, runtime.path(), {"terminal", hex(peer)}, false);
    require(eventually([&] {
        std::scoped_lock lock(state.mutex);
        return state.opens == 1U && state.attached && server.client_connected();
    }), "first controller did not attach");
    require(eventually([&] {
        std::scoped_lock lock(state.mutex);
        return state.pings >= 1U;
    }), "attached terminal client did not issue its end-to-end heartbeat");

    ChildProcess loser = spawn_iotox(
        iotox, runtime.path(), {"terminal", hex(peer)}, true);
    const ProcessResult denied = loser.wait(5000ms);
    require(denied.exit_code == 3,
            "competing terminal client used the wrong exit code");
    require(
        denied.output.find(
            "another local terminal client is already attached") !=
            std::string::npos,
        "competing terminal client lost the typed busy reason; output=" +
            denied.output);
    require(
        denied.output.find("changed the stream ID") == std::string::npos,
        "competing terminal client misreported busy as stream corruption");

    const ProcessResult killed = winner.signal_and_wait(SIGKILL, 5000ms);
    require(killed.exit_code == 128 + SIGKILL,
            "first terminal controller was not killed as requested");
    require(eventually([&] {
        std::scoped_lock lock(state.mutex);
        return !state.attached && state.disconnects >= 1U &&
               !server.client_connected();
    }), "controller death did not detach the session");

    ChildProcess successor = spawn_iotox(
        iotox, runtime.path(),
        {"terminal-resume", hex(state.session), hex(peer)}, true);
    const ProcessResult resumed = successor.wait(5000ms);
    require(resumed.exit_code == 0,
            "replacement controller did not detach cleanly");
    require(resumed.output.find("resumed-output\n") != std::string::npos,
            "replacement controller did not render retained output");
    constexpr std::string_view replay = "resumed-output\n";
    require(eventually([&] {
        std::scoped_lock lock(state.mutex);
        return state.resumes == 1U && state.generation == 2U &&
               state.output_ack == 1U + replay.size() && !state.attached;
    }), "replacement controller did not acknowledge exact replay output");

    server.stop();

    TerminalServer restarted(
        config,
        [](const TerminalPacket &packet,
           const iotox::local::PeerCredentials &) {
            if (packet.type != TerminalPacketType::open) {
                return Status{ErrorCode::protocol_error,
                              "restart fixture expected OPEN"};
            }
            return Status{
                ErrorCode::not_found,
                "terminal session was lost when the Agent restarted"};
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    require_ok(restarted.start(), "restart terminal fixture server");
    ChildProcess stale_resume = spawn_iotox(
        iotox, runtime.path(),
        {"terminal-resume", hex(state.session), hex(peer)}, true);
    const ProcessResult absent = stale_resume.wait(5000ms);
    require(absent.exit_code == 3,
            "post-restart resume used the wrong exit code");
    require(
        absent.output.find(
            "terminal session was lost when the Agent restarted") !=
            std::string::npos,
        "post-restart resume did not expose explicit not-found semantics");
    restarted.stop();
}

void test_heartbeat_warning_without_session_mutation(
    const std::filesystem::path &iotox) {
    TempDirectory runtime;
    FixtureState state;
    state.session.fill(0x41U);
    state.reply_to_pings = false;
    state.detach_at_ping = 4U;

    TerminalServer::Config config;
    config.socket_path = runtime.path() / "terminal.sock";
    config.poll_interval = 2ms;
    config.open_timeout = 500ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            return handle_packet(state, packet);
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            return drain_packets(state, maximum_packets);
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            mark_disconnected(state);
        });
    require_ok(server.start(), "start heartbeat fixture server");

    std::array<std::uint8_t, iotox::local::kTerminalPeerPublicKeyBytes> peer{};
    peer.fill(0x62U);
    ChildProcess client = spawn_iotox(
        iotox, runtime.path(), {"terminal", hex(peer)}, false);
    const ProcessResult result = client.wait(7000ms);
    require(result.exit_code == 0,
            "heartbeat warning fixture did not finish through explicit DETACHED");
    require(
        result.output.find(
            "Ratox heartbeat: remote attachment is unresponsive; session retained") !=
            std::string::npos,
        "terminal client did not expose the three-miss heartbeat warning; output=" +
            result.output);
    {
        std::scoped_lock lock(state.mutex);
        require(state.pings == 4U,
                "terminal heartbeat did not use the frozen one-second/three-miss policy");
        require(!state.attached,
                "fixture DETACHED did not release the terminal attachment");
    }
    server.stop();
}

void test_batch_mode_preserves_output_and_exit_status(
    const std::filesystem::path &iotox) {
    TempDirectory runtime;
    FixtureState state;
    state.session.fill(0x51U);
    state.batch_exit_on_eot = true;

    TerminalServer::Config config;
    config.socket_path = runtime.path() / "terminal.sock";
    config.poll_interval = 2ms;
    config.open_timeout = 500ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            return handle_packet(state, packet);
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            return drain_packets(state, maximum_packets);
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            mark_disconnected(state);
        });
    require_ok(server.start(), "start batch terminal fixture server");

    std::array<std::uint8_t, iotox::local::kTerminalPeerPublicKeyBytes> peer{};
    peer.fill(0x72U);
    ChildProcess client = spawn_iotox(
        iotox, runtime.path(), {"--batch", "terminal", hex(peer)}, true);
    const ProcessResult result = client.wait(5000ms);
    require(result.exit_code == 7,
            "batch terminal did not preserve the remote exit status");
    require(result.output == "batch-output\n",
            "batch terminal polluted or lost the remote byte stream; output=" +
                result.output);
    server.stop();
}

}  // namespace

int main(int argc, char **argv) {
    try {
        if (argc != 2) {
            throw std::runtime_error(
                "usage: iotox_terminal_controller_process_tests IOTOX");
        }
        const std::filesystem::path iotox = argv[1];
        require(std::filesystem::is_regular_file(iotox),
                "IoTox executable is missing");
        test_controller_replacement_and_restart(iotox);
        test_exact_session_reconnect_waits_for_higher_epoch(iotox);
        test_exact_session_reconnect_survives_repeated_loss(iotox);
        test_heartbeat_warning_without_session_mutation(iotox);
        test_batch_mode_preserves_output_and_exit_status(iotox);
        std::cout << "terminal-controller-process: passed\n";
        return 0;
    } catch (const std::exception &exception) {
        std::cerr << "terminal-controller-process: failed: "
                  << exception.what() << '\n';
        return 1;
    }
}
