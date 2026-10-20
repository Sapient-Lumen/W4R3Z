#pragma once

#include "iotox/local/control_socket.hpp"
#include "iotox/local/terminal_protocol.hpp"
#include "iotox/status.hpp"

#include <atomic>
#include <chrono>
#include <cstddef>
#include <filesystem>
#include <functional>
#include <memory>
#include <vector>

namespace iotox::local {

class TerminalServer {
  public:
    using PacketHandler = std::function<Status(
        const TerminalPacket &, const PeerCredentials &)>;
    using DrainHandler = std::function<std::vector<TerminalPacket>(
        std::uint64_t stream_id, std::size_t maximum_packets)>;
    using DisconnectHandler = std::function<void(
        std::uint64_t stream_id, const PeerCredentials &)>;

    struct Config {
        std::filesystem::path socket_path;
        unsigned int socket_mode{0600U};
        int backlog{4};
        bool same_user_only{true};
        std::chrono::milliseconds poll_interval{10};
        // A connected process must commit its first OPEN promptly. Without
        // this lease, a silent same-user client could reserve the sole
        // controller slot indefinitely and starve every legitimate terminal.
        std::chrono::milliseconds open_timeout{5000};
        // DETACH is a two-phase local close. After the terminal result is
        // drained, keep the socket alive briefly so cumulative OUTPUT_ACK
        // records sent before the CLI closes are committed. The lease keeps a
        // detached but nonclosing same-user process from reserving the slot.
        std::chrono::milliseconds detach_drain_timeout{250};
        std::size_t maximum_packets_per_cycle{32U};
        // A second connection is never allowed to enter the controller state
        // machine while a stream is active. Keep only a bounded set long
        // enough to recover the attempted stream ID for a correlated BUSY
        // response, and service those contenders without blocking the active
        // stream's poll loop.
        std::chrono::milliseconds contender_open_timeout{20};
        std::chrono::milliseconds contender_admission_interval{1};
        std::size_t maximum_pending_contenders{16U};
        std::size_t maximum_pending_contenders_per_process{4U};
        std::size_t maximum_contender_accepts_per_interval{4U};
        std::size_t maximum_contender_records_per_cycle{8U};
    };

    TerminalServer(
        Config config,
        PacketHandler packet_handler,
        DrainHandler drain_handler,
        DisconnectHandler disconnect_handler = {});
    ~TerminalServer();

    TerminalServer(const TerminalServer &) = delete;
    TerminalServer &operator=(const TerminalServer &) = delete;
    TerminalServer(TerminalServer &&) = delete;
    TerminalServer &operator=(TerminalServer &&) = delete;

    [[nodiscard]] Status start();
    void stop();
    void notify() noexcept;

    [[nodiscard]] bool running() const noexcept;
    [[nodiscard]] bool client_connected() const noexcept;
    [[nodiscard]] const std::filesystem::path &socket_path() const noexcept;

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

class TerminalConnection {
  public:
    TerminalConnection();
    ~TerminalConnection();

    TerminalConnection(const TerminalConnection &) = delete;
    TerminalConnection &operator=(const TerminalConnection &) = delete;
    TerminalConnection(TerminalConnection &&) noexcept;
    TerminalConnection &operator=(TerminalConnection &&) noexcept;

    [[nodiscard]] static Result<TerminalConnection> connect(
        const std::filesystem::path &socket_path,
        std::chrono::milliseconds timeout = std::chrono::seconds(5));

    [[nodiscard]] Status send(
        const TerminalPacket &packet,
        std::chrono::milliseconds timeout = std::chrono::seconds(5));
    [[nodiscard]] Result<TerminalPacket> receive(
        std::chrono::milliseconds timeout = std::chrono::seconds(5));

    [[nodiscard]] int native_handle() const noexcept;
    [[nodiscard]] bool valid() const noexcept;
    void close() noexcept;

  private:
    explicit TerminalConnection(
        int descriptor,
        PeerCredentials server_credentials,
        bool require_server_pidfd) noexcept;
    int descriptor_{-1};
    PeerCredentials server_credentials_{};
    bool require_server_pidfd_{false};
};

}  // namespace iotox::local
