#include "sync_systemd_notify.hpp"

#if !defined(_WIN32)

#include <cerrno>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <string>
#include <system_error>
#include <utility>

#if defined(__linux__)
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

[[nodiscard]] std::string errno_message(
    int error,
    std::string_view operation) {
    return std::string(operation) + ": " +
        std::error_code(error, std::generic_category()).message();
}

void validate_endpoint_or_throw(
    const std::optional<std::string>& endpoint,
    std::string_view label) {
    if (!endpoint.has_value()) return;
    if (endpoint->empty()) {
        throw std::invalid_argument(
            std::string(label) + " NOTIFY_SOCKET is empty");
    }
#if defined(__linux__)
    const bool abstract = endpoint->front() == '@';
    if (!abstract && endpoint->front() != '/') {
        throw std::invalid_argument(
            std::string(label) +
            " NOTIFY_SOCKET must be absolute or begin with @");
    }
    const std::size_t payload_size = abstract
        ? endpoint->size() - 1U
        : endpoint->size();
    if (payload_size == 0U ||
        payload_size >= sizeof(((sockaddr_un*)nullptr)->sun_path)) {
        throw std::invalid_argument(
            std::string(label) + " NOTIFY_SOCKET is too long or empty");
    }
    if (endpoint->find('\0') != std::string::npos) {
        throw std::invalid_argument(
            std::string(label) + " NOTIFY_SOCKET contains NUL");
    }
#else
    throw std::invalid_argument(
        std::string(label) +
        " NOTIFY_SOCKET is configured on a non-Linux platform");
#endif
}

}  // namespace

SyncSystemdNotifier SyncSystemdNotifier::from_environment_or_throw(
    std::string label) {
    const char* const raw = std::getenv("NOTIFY_SOCKET");
    std::optional<std::string> endpoint;
    if (raw != nullptr && raw[0] != '\0') endpoint = std::string(raw);
    return SyncSystemdNotifier(std::move(endpoint), std::move(label));
}

SyncSystemdNotifier::SyncSystemdNotifier(
    std::optional<std::string> notify_socket,
    std::string label)
    : notify_socket_(std::move(notify_socket)), label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument("systemd notifier label must not be empty");
    }
    validate_endpoint_or_throw(notify_socket_, label_);
    snapshot_.configured = notify_socket_.has_value();
}

bool SyncSystemdNotifier::configured() const noexcept {
    return snapshot_.configured;
}

bool SyncSystemdNotifier::ready_announced() const noexcept {
    return snapshot_.ready_announced;
}

SyncSystemdNotifySnapshot SyncSystemdNotifier::snapshot() const {
    return snapshot_;
}

void SyncSystemdNotifier::validate_status_or_throw(
    std::string_view status) const {
    if (status.empty() ||
        status.size() > kSyncSystemdNotifyMaximumStatusBytes) {
        throw std::invalid_argument(
            label_ + " status must contain 1..2048 bytes");
    }
    if (status.find('\0') != std::string_view::npos ||
        status.find('\n') != std::string_view::npos ||
        status.find('\r') != std::string_view::npos) {
        throw std::invalid_argument(
            label_ + " status contains a protocol delimiter");
    }
}

void SyncSystemdNotifier::send_or_throw(std::string_view payload) {
    if (!notify_socket_.has_value()) return;
    ++snapshot_.datagrams_attempted;
#if defined(__linux__)
    const int descriptor = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) {
        const int error = errno;
        ++snapshot_.datagrams_failed;
        snapshot_.last_error = errno_message(error, "socket");
        throw std::runtime_error(label_ + " " + *snapshot_.last_error);
    }

    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    socklen_t address_length = 0;
    if (notify_socket_->front() == '@') {
        const std::string_view name(*notify_socket_);
        address.sun_path[0] = '\0';
        std::memcpy(
            address.sun_path + 1,
            name.data() + 1,
            name.size() - 1U);
        address_length = static_cast<socklen_t>(
            offsetof(sockaddr_un, sun_path) + name.size());
    } else {
        std::memcpy(
            address.sun_path,
            notify_socket_->data(),
            notify_socket_->size());
        address.sun_path[notify_socket_->size()] = '\0';
        address_length = static_cast<socklen_t>(
            offsetof(sockaddr_un, sun_path) + notify_socket_->size() + 1U);
    }

    const ssize_t sent = ::sendto(
        descriptor,
        payload.data(),
        payload.size(),
        MSG_NOSIGNAL,
        reinterpret_cast<const sockaddr*>(&address),
        address_length);
    const int send_error = sent < 0 ? errno : 0;
    const int close_result = ::close(descriptor);
    const int close_error = close_result != 0 ? errno : 0;
    if (sent < 0) {
        ++snapshot_.datagrams_failed;
        snapshot_.last_error = errno_message(send_error, "sendto");
        throw std::runtime_error(label_ + " " + *snapshot_.last_error);
    }
    if (static_cast<std::size_t>(sent) != payload.size()) {
        ++snapshot_.datagrams_failed;
        snapshot_.last_error = "sendto wrote a partial datagram";
        throw std::runtime_error(label_ + " " + *snapshot_.last_error);
    }
    if (close_result != 0) {
        ++snapshot_.datagrams_failed;
        snapshot_.last_error = errno_message(close_error, "close");
        throw std::runtime_error(label_ + " " + *snapshot_.last_error);
    }
    ++snapshot_.datagrams_sent;
    snapshot_.last_error.reset();
#else
    (void)payload;
    ++snapshot_.datagrams_failed;
    snapshot_.last_error = "systemd notification is unavailable";
    throw std::runtime_error(label_ + " " + *snapshot_.last_error);
#endif
}

void SyncSystemdNotifier::publish_startup_status_or_throw(
    std::string_view status) {
    validate_status_or_throw(status);
    if (!configured()) return;
    if (snapshot_.ready_announced) {
        throw std::logic_error(
            label_ + " startup status followed READY=1");
    }
    if (snapshot_.last_status.has_value() &&
        *snapshot_.last_status == status) {
        return;
    }
    const std::string payload = "STATUS=" + std::string(status);
    send_or_throw(payload);
    snapshot_.last_status = std::string(status);
}

void SyncSystemdNotifier::announce_ready_or_throw(std::string_view status) {
    validate_status_or_throw(status);
    if (!configured()) {
        snapshot_.ready_announced = true;
        snapshot_.last_status = std::string(status);
        return;
    }
    if (snapshot_.ready_announced) {
        if (!snapshot_.last_status.has_value() ||
            *snapshot_.last_status != status) {
            publish_runtime_status(status);
        }
        return;
    }
    const std::string payload =
        "READY=1\nSTATUS=" + std::string(status);
    send_or_throw(payload);
    snapshot_.ready_announced = true;
    snapshot_.last_status = std::string(status);
}

void SyncSystemdNotifier::send_runtime_noexcept(
    std::string_view payload,
    std::string_view status,
    bool stopping) noexcept {
    try {
        send_or_throw(payload);
        snapshot_.last_status = std::string(status);
        if (stopping) snapshot_.stopping_announced = true;
    } catch (const std::exception&) {
        // A service-manager outage after readiness must not become sync
        // authority. send_or_throw already retained the diagnostic.
    }
}

void SyncSystemdNotifier::publish_runtime_status(
    std::string_view status) noexcept {
    try {
        validate_status_or_throw(status);
        if (snapshot_.last_status.has_value() &&
            *snapshot_.last_status == status) {
            return;
        }
        if (!configured()) {
            snapshot_.last_status = std::string(status);
            return;
        }
        const std::string payload = "STATUS=" + std::string(status);
        send_runtime_noexcept(payload, status, false);
    } catch (const std::exception& error) {
        ++snapshot_.datagrams_failed;
        snapshot_.last_error = error.what();
    }
}

void SyncSystemdNotifier::announce_stopping(
    std::string_view status) noexcept {
    if (snapshot_.stopping_announced) return;
    try {
        validate_status_or_throw(status);
        if (!configured()) {
            snapshot_.stopping_announced = true;
            snapshot_.last_status = std::string(status);
            return;
        }
        const std::string payload =
            "STOPPING=1\nSTATUS=" + std::string(status);
        send_runtime_noexcept(payload, status, true);
    } catch (const std::exception& error) {
        ++snapshot_.datagrams_failed;
        snapshot_.last_error = error.what();
    }
}

}  // namespace anonsync

#endif
