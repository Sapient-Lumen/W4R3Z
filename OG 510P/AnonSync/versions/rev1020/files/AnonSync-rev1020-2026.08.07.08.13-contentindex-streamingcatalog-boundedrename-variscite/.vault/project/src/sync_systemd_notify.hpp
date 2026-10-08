#pragma once

#if !defined(_WIN32)

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::size_t kSyncSystemdNotifyMaximumStatusBytes = 2048U;

struct SyncSystemdNotifySnapshot final {
    bool configured = false;
    bool ready_announced = false;
    bool stopping_announced = false;
    std::uint64_t datagrams_attempted = 0U;
    std::uint64_t datagrams_sent = 0U;
    std::uint64_t datagrams_failed = 0U;
    std::optional<std::string> last_status;
    std::optional<std::string> last_error;

    bool operator==(const SyncSystemdNotifySnapshot&) const = default;
};

// Minimal native implementation of the systemd notification datagram protocol.
// The service remains a normal foreground process and takes no libsystemd
// dependency. Before READY=1, a configured-but-unreachable notification socket
// is a startup failure: otherwise Type=notify would wait until its own timeout.
// After READY=1, status publication is diagnostic-only and cannot stop folder
// synchronization merely because the service manager disappeared or restarted.
class SyncSystemdNotifier final {
public:
    static SyncSystemdNotifier from_environment_or_throw(
        std::string label = "systemd notifier");

    SyncSystemdNotifier(
        std::optional<std::string> notify_socket,
        std::string label = "systemd notifier");

    SyncSystemdNotifier(const SyncSystemdNotifier&) = delete;
    SyncSystemdNotifier& operator=(const SyncSystemdNotifier&) = delete;
    SyncSystemdNotifier(SyncSystemdNotifier&&) = delete;
    SyncSystemdNotifier& operator=(SyncSystemdNotifier&&) = delete;

    [[nodiscard]] bool configured() const noexcept;
    [[nodiscard]] bool ready_announced() const noexcept;
    [[nodiscard]] SyncSystemdNotifySnapshot snapshot() const;

    void publish_startup_status_or_throw(std::string_view status);
    void announce_ready_or_throw(std::string_view status);
    void publish_runtime_status(std::string_view status) noexcept;
    void announce_stopping(std::string_view status) noexcept;

private:
    void validate_status_or_throw(std::string_view status) const;
    void send_or_throw(std::string_view payload);
    void send_runtime_noexcept(
        std::string_view payload,
        std::string_view status,
        bool stopping) noexcept;

    std::optional<std::string> notify_socket_;
    std::string label_;
    SyncSystemdNotifySnapshot snapshot_;
};

}  // namespace anonsync

#endif
