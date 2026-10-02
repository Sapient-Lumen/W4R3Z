#pragma once

#include "iotox/local/control_protocol.hpp"
#include "iotox/status.hpp"

#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>

namespace iotox::local {

struct PeerCredentials {
    std::int64_t process_id{-1};
    std::uint64_t user_id{0U};
    std::uint64_t group_id{0U};
};

class ControlServer {
  public:
    using Handler = std::function<ControlPacket(const ControlPacket &, const PeerCredentials &)>;

    struct Config {
        std::filesystem::path socket_path;
        unsigned int socket_mode{0600U};
        int backlog{16};
        bool same_user_only{true};
        // A silent same-user connection must not monopolize the single
        // request lane indefinitely. This is a complete-record deadline.
        std::chrono::milliseconds request_timeout{5000};
        // Accepted clients are polled together, so a silent peer cannot
        // serialize ready requests behind its lease. These limits bound the
        // descriptor set, per-process hoarding, and accept work per refill.
        std::size_t maximum_pending_clients{32U};
        std::size_t maximum_pending_clients_per_process{4U};
        std::size_t maximum_accepts_per_interval{8U};
        std::size_t maximum_requests_per_cycle{8U};
        std::chrono::milliseconds admission_interval{1};
    };

    ControlServer(Config config, Handler handler);
    ~ControlServer();

    ControlServer(const ControlServer &) = delete;
    ControlServer &operator=(const ControlServer &) = delete;
    ControlServer(ControlServer &&) = delete;
    ControlServer &operator=(ControlServer &&) = delete;

    [[nodiscard]] Status start();
    void stop();

    [[nodiscard]] bool running() const noexcept;
    [[nodiscard]] const std::filesystem::path &socket_path() const noexcept;

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

[[nodiscard]] Result<ControlPacket> control_request(
    const std::filesystem::path &socket_path,
    const ControlPacket &request,
    std::chrono::milliseconds timeout = std::chrono::seconds(5));

}  // namespace iotox::local
