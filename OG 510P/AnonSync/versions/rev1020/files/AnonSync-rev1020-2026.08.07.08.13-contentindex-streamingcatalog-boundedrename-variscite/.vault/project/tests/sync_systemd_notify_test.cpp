#include "sync_systemd_notify.hpp"

#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <type_traits>
#include <utility>
#include <vector>

#include <poll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

static_assert(!std::is_copy_constructible_v<anonsync::SyncSystemdNotifier>);
static_assert(!std::is_move_constructible_v<anonsync::SyncSystemdNotifier>);

std::size_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_throws(Function&& function, std::string_view message) {
    ++checks;
    try {
        std::forward<Function>(function)();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(std::string(message));
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/anonsync-systemd-notify-test-XXXXXX";
        std::vector<char> writable(pattern.begin(), pattern.end());
        writable.push_back('\0');
        char* selected = ::mkdtemp(writable.data());
        if (selected == nullptr) throw std::runtime_error("mkdtemp failed");
        path_ = selected;
    }

    ~TemporaryDirectory() noexcept {
        std::error_code error;
        fs::remove_all(path_, error);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

class DatagramReceiver final {
public:
    explicit DatagramReceiver(std::string endpoint)
        : endpoint_(std::move(endpoint)) {
        descriptor_ = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
        if (descriptor_ < 0) throw std::runtime_error("socket failed");
        sockaddr_un address{};
        address.sun_family = AF_UNIX;
        socklen_t length = 0;
        if (endpoint_.starts_with('@')) {
            if (endpoint_.size() <= 1U ||
                endpoint_.size() >= sizeof(address.sun_path)) {
                throw std::runtime_error("abstract endpoint invalid");
            }
            address.sun_path[0] = '\0';
            std::memcpy(
                address.sun_path + 1,
                endpoint_.data() + 1,
                endpoint_.size() - 1U);
            length = static_cast<socklen_t>(
                offsetof(sockaddr_un, sun_path) + endpoint_.size());
        } else {
            if (endpoint_.size() >= sizeof(address.sun_path)) {
                throw std::runtime_error("filesystem endpoint too long");
            }
            std::memcpy(
                address.sun_path, endpoint_.data(), endpoint_.size());
            address.sun_path[endpoint_.size()] = '\0';
            length = static_cast<socklen_t>(
                offsetof(sockaddr_un, sun_path) + endpoint_.size() + 1U);
        }
        if (::bind(
                descriptor_,
                reinterpret_cast<const sockaddr*>(&address),
                length) != 0) {
            const int error = errno;
            throw std::runtime_error(
                "bind failed: " +
                std::error_code(error, std::generic_category()).message());
        }
    }

    ~DatagramReceiver() noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        if (!endpoint_.starts_with('@')) (void)::unlink(endpoint_.c_str());
    }

    DatagramReceiver(const DatagramReceiver&) = delete;
    DatagramReceiver& operator=(const DatagramReceiver&) = delete;

    [[nodiscard]] std::string receive() {
        pollfd poll_descriptor{descriptor_, POLLIN, 0};
        const int ready = ::poll(&poll_descriptor, 1U, 1000);
        if (ready != 1 || (poll_descriptor.revents & POLLIN) == 0) {
            throw std::runtime_error("notification datagram did not arrive");
        }
        char bytes[4096]{};
        const ssize_t count = ::recv(descriptor_, bytes, sizeof(bytes), 0);
        if (count < 0) throw std::runtime_error("recv failed");
        return std::string(bytes, static_cast<std::size_t>(count));
    }

    void close_receiver() noexcept {
        if (descriptor_ >= 0) {
            (void)::close(descriptor_);
            descriptor_ = -1;
        }
        if (!endpoint_.starts_with('@')) (void)::unlink(endpoint_.c_str());
    }

private:
    std::string endpoint_;
    int descriptor_ = -1;
};

void exercise_endpoint(const std::string& endpoint) {
    DatagramReceiver receiver(endpoint);
    anonsync::SyncSystemdNotifier notifier(endpoint, "notify test");
    require(notifier.configured(), "endpoint must configure notifier");
    require(!notifier.ready_announced(), "new notifier must not be ready");

    notifier.publish_startup_status_or_throw("Starting: folder repair");
    require(
        receiver.receive() == "STATUS=Starting: folder repair",
        "startup status datagram mismatch");
    notifier.publish_startup_status_or_throw("Starting: folder repair");

    notifier.announce_ready_or_throw("Running: service ready");
    require(
        receiver.receive() == "READY=1\nSTATUS=Running: service ready",
        "ready datagram mismatch");
    require(notifier.ready_announced(), "ready state must latch");

    notifier.publish_runtime_status("Degraded: ingress unavailable");
    require(
        receiver.receive() == "STATUS=Degraded: ingress unavailable",
        "runtime status datagram mismatch");
    notifier.publish_runtime_status("Degraded: ingress unavailable");

    notifier.announce_stopping("Stopping: local request");
    require(
        receiver.receive() == "STOPPING=1\nSTATUS=Stopping: local request",
        "stopping datagram mismatch");

    const auto snapshot = notifier.snapshot();
    require(snapshot.configured, "snapshot must report configured");
    require(snapshot.ready_announced, "snapshot must report ready");
    require(snapshot.stopping_announced, "snapshot must report stopping");
    require(snapshot.datagrams_attempted == 4U,
            "duplicate statuses must not emit datagrams");
    require(snapshot.datagrams_sent == 4U,
            "all expected datagrams must be sent");
    require(snapshot.datagrams_failed == 0U,
            "healthy receiver must not record failures");
}

}  // namespace

int main() {
    try {
        TemporaryDirectory temporary;
        exercise_endpoint((temporary.path() / "notify.sock").string());
        exercise_endpoint(
            "@anonsync-systemd-notify-" +
            std::to_string(static_cast<long long>(::getpid())));

        anonsync::SyncSystemdNotifier absent(std::nullopt, "absent notify");
        absent.publish_startup_status_or_throw("Starting: no manager");
        absent.announce_ready_or_throw("Running: no manager");
        absent.publish_runtime_status("Running: still no manager");
        absent.announce_stopping("Stopping: no manager");
        const auto absent_snapshot = absent.snapshot();
        require(!absent_snapshot.configured,
                "absent endpoint must remain unconfigured");
        require(absent_snapshot.ready_announced,
                "no-manager readiness must still latch locally");
        require(absent_snapshot.stopping_announced,
                "no-manager stopping must still latch locally");
        require(absent_snapshot.datagrams_attempted == 0U,
                "no-manager mode must attempt no datagrams");

        const std::string missing =
            (temporary.path() / "missing.sock").string();
        anonsync::SyncSystemdNotifier startup_failure(
            missing, "startup failure");
        require_throws(
            [&] {
                startup_failure.publish_startup_status_or_throw(
                    "Starting: manager required");
            },
            "missing manager before readiness must fail startup");
        require(startup_failure.snapshot().datagrams_failed == 1U,
                "startup failure must be retained diagnostically");

        const std::string disappearing =
            (temporary.path() / "disappearing.sock").string();
        DatagramReceiver receiver(disappearing);
        anonsync::SyncSystemdNotifier runtime_failure(
            disappearing, "runtime failure");
        runtime_failure.announce_ready_or_throw("Running: before outage");
        require(
            receiver.receive() == "READY=1\nSTATUS=Running: before outage",
            "runtime failure fixture did not receive readiness");
        receiver.close_receiver();
        runtime_failure.publish_runtime_status("Degraded: manager lost");
        runtime_failure.announce_stopping("Stopping: manager lost");
        const auto runtime_snapshot = runtime_failure.snapshot();
        require(runtime_snapshot.ready_announced,
                "manager loss must not revoke readiness");
        require(runtime_snapshot.datagrams_failed >= 1U,
                "manager loss must remain diagnostic");

        require_throws(
            [] {
                anonsync::SyncSystemdNotifier invalid(
                    std::string("relative.sock"), "invalid endpoint");
            },
            "relative manager endpoint must be rejected");
        require_throws(
            [] {
                anonsync::SyncSystemdNotifier notifier(
                    std::nullopt, "invalid status");
                notifier.publish_startup_status_or_throw("bad\nstatus");
            },
            "status delimiters must be rejected");

        const char* prior = std::getenv("NOTIFY_SOCKET");
        const std::optional<std::string> saved =
            prior == nullptr ? std::nullopt
                             : std::optional<std::string>(prior);
        require(::setenv("NOTIFY_SOCKET", missing.c_str(), 1) == 0,
                "setenv must succeed");
        auto from_environment =
            anonsync::SyncSystemdNotifier::from_environment_or_throw(
                "environment notify");
        require(from_environment.configured(),
                "environment endpoint must configure notifier");
        if (saved.has_value()) {
            require(::setenv("NOTIFY_SOCKET", saved->c_str(), 1) == 0,
                    "environment restore must succeed");
        } else {
            require(::unsetenv("NOTIFY_SOCKET") == 0,
                    "environment clear must succeed");
        }

        std::cout << "sync_systemd_notify_test: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync_systemd_notify_test failure after " << checks
                  << " checks: " << error.what() << '\n';
        return 1;
    }
}
