#include "sync_socket_readiness_identity.hpp"

#include <cerrno>
#include <stdexcept>
#include <string>
#include <type_traits>

#ifdef __linux__
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

[[nodiscard]] std::string diagnostic_prefix(
    std::string_view label,
    int descriptor) {
    return std::string(label) + " descriptor " + std::to_string(descriptor);
}

#ifdef __linux__
[[nodiscard]] std::uint64_t unsigned_stat_component_or_throw(
    auto value,
    std::string_view label,
    int descriptor,
    std::string_view component) {
    using Value = decltype(value);
    if constexpr (std::is_signed_v<Value>) {
        if (value < 0) {
            throw std::runtime_error(
                diagnostic_prefix(label, descriptor) + " exposed a negative " +
                std::string(component));
        }
    }
    using UnsignedValue = std::make_unsigned_t<Value>;
    const auto converted = static_cast<UnsignedValue>(value);
    if constexpr (sizeof(UnsignedValue) > sizeof(std::uint64_t)) {
        if (converted > static_cast<UnsignedValue>(UINT64_MAX)) {
            throw std::overflow_error(
                diagnostic_prefix(label, descriptor) + " " +
                std::string(component) + " does not fit uint64_t");
        }
    }
    return static_cast<std::uint64_t>(converted);
}

[[nodiscard]] bool same_file_identity(
    const struct stat& left,
    const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino &&
           left.st_mode == right.st_mode;
}

[[nodiscard]] int observe_socket_type_or_throw(
    int descriptor,
    std::string_view label) {
    int socket_type = 0;
    socklen_t socket_type_bytes = sizeof(socket_type);
    errno = 0;
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_TYPE,
            &socket_type, &socket_type_bytes) != 0 ||
        socket_type_bytes != sizeof(socket_type)) {
        throw std::runtime_error(
            diagnostic_prefix(label, descriptor) +
            " could not prove SO_TYPE (errno " + std::to_string(errno) + ")");
    }
    if (socket_type != SOCK_STREAM) {
        throw std::invalid_argument(
            diagnostic_prefix(label, descriptor) +
            " is not a SOCK_STREAM socket");
    }
    return socket_type;
}

[[nodiscard]] std::uint64_t observe_socket_cookie_or_throw(
    int descriptor,
    std::string_view label) {
#ifndef SO_COOKIE
#error "Linux socket lifetime reproof requires SO_COOKIE"
#endif
    std::uint64_t cookie = 0U;
    socklen_t cookie_bytes = sizeof(cookie);
    errno = 0;
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_COOKIE,
            &cookie, &cookie_bytes) != 0 ||
        cookie_bytes != sizeof(cookie) || cookie == 0U) {
        throw std::runtime_error(
            diagnostic_prefix(label, descriptor) +
            " could not bind a nonzero Linux SO_COOKIE (errno " +
            std::to_string(errno) + ")");
    }
    return cookie;
}
#endif

}  // namespace

SyncSocketLifetimeIdentity observe_sync_stream_socket_lifetime_or_throw(
    int descriptor,
    std::string_view label) {
#ifdef __linux__
    if (descriptor < 0) {
        throw std::invalid_argument(
            diagnostic_prefix(label, descriptor) + " is invalid");
    }

    struct stat before {};
    errno = 0;
    if (::fstat(descriptor, &before) != 0) {
        throw std::runtime_error(
            diagnostic_prefix(label, descriptor) +
            " could not be statted (errno " + std::to_string(errno) + ")");
    }
    if (!S_ISSOCK(before.st_mode)) {
        throw std::invalid_argument(
            diagnostic_prefix(label, descriptor) +
            " is not a socket-backed descriptor");
    }

    const int socket_type = observe_socket_type_or_throw(descriptor, label);
    const std::uint64_t cookie =
        observe_socket_cookie_or_throw(descriptor, label);

    struct stat after {};
    errno = 0;
    if (::fstat(descriptor, &after) != 0) {
        throw std::runtime_error(
            diagnostic_prefix(label, descriptor) +
            " could not be restatted (errno " + std::to_string(errno) + ")");
    }
    if (!same_file_identity(before, after)) {
        throw std::runtime_error(
            diagnostic_prefix(label, descriptor) +
            " changed identity while its lifetime was observed");
    }
    const int socket_type_after =
        observe_socket_type_or_throw(descriptor, label);
    if (socket_type_after != socket_type) {
        throw std::runtime_error(
            diagnostic_prefix(label, descriptor) +
            " changed SO_TYPE while its lifetime was observed");
    }
    const std::uint64_t cookie_after =
        observe_socket_cookie_or_throw(descriptor, label);
    if (cookie_after != cookie) {
        throw std::runtime_error(
            diagnostic_prefix(label, descriptor) +
            " changed Linux SO_COOKIE while its lifetime was observed");
    }

    return SyncSocketLifetimeIdentity(
        descriptor,
        socket_type,
        unsigned_stat_component_or_throw(
            before.st_dev, label, descriptor, "device identity"),
        unsigned_stat_component_or_throw(
            before.st_ino, label, descriptor, "inode identity"),
        cookie);
#else
    (void)descriptor;
    throw std::runtime_error(
        std::string(label) +
        " cannot prove an exact stream-socket lifetime on this platform");
#endif
}

void reprove_sync_stream_socket_lifetime_or_throw(
    const SyncSocketLifetimeIdentity& expected,
    std::string_view label) {
    const SyncSocketLifetimeIdentity observed =
        observe_sync_stream_socket_lifetime_or_throw(
            expected.descriptor(), label);
    if (observed != expected) {
        throw std::runtime_error(
            diagnostic_prefix(label, expected.descriptor()) +
            " no longer names the exact observed socket lifetime");
    }
}

void require_sync_stream_socket_nonblocking_or_throw(
    const SyncSocketLifetimeIdentity& expected,
    std::string_view label) {
#ifdef __linux__
    // The lifetime checks on both sides prevent close/dup2 substitution from
    // lending an unrelated descriptor's flags to the expected socket. Raw
    // descriptor and F_SETFL mutation must still be externally serialized.
    reprove_sync_stream_socket_lifetime_or_throw(expected, label);
    errno = 0;
    const int flags = ::fcntl(expected.descriptor(), F_GETFL, 0);
    if (flags < 0) {
        throw std::runtime_error(
            diagnostic_prefix(label, expected.descriptor()) +
            " could not expose file-status flags (errno " +
            std::to_string(errno) + ")");
    }
    reprove_sync_stream_socket_lifetime_or_throw(expected, label);
    if ((flags & O_NONBLOCK) == 0) {
        throw std::invalid_argument(
            diagnostic_prefix(label, expected.descriptor()) +
            " is not nonblocking");
    }
#else
    reprove_sync_stream_socket_lifetime_or_throw(expected, label);
#endif
}

void require_sync_stream_socket_close_on_exec_or_throw(
    const SyncSocketLifetimeIdentity& expected,
    std::string_view label) {
#ifdef __linux__
    reprove_sync_stream_socket_lifetime_or_throw(expected, label);
    errno = 0;
    const int flags = ::fcntl(expected.descriptor(), F_GETFD, 0);
    if (flags < 0) {
        throw std::runtime_error(
            diagnostic_prefix(label, expected.descriptor()) +
            " could not expose descriptor flags (errno " +
            std::to_string(errno) + ")");
    }
    reprove_sync_stream_socket_lifetime_or_throw(expected, label);
    if ((flags & FD_CLOEXEC) == 0) {
        throw std::invalid_argument(
            diagnostic_prefix(label, expected.descriptor()) +
            " is inheritable across exec");
    }
#else
    reprove_sync_stream_socket_lifetime_or_throw(expected, label);
    throw std::runtime_error(
        std::string(label) +
        " cannot prove close-on-exec socket policy on this platform");
#endif
}

}  // namespace anonsync
