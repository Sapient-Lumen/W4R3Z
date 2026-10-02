#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "seqpacket_security.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <poll.h>
#include <string>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>

namespace iotox::local::detail {
namespace {

constexpr std::size_t kAncillaryBufferBytes = 4096U;

std::string surface_message(std::string_view surface, std::string detail) {
    std::string message(surface);
    if (!message.empty()) message += ' ';
    message += std::move(detail);
    return message;
}

Status system_status(
    ErrorCode code,
    std::string_view surface,
    std::string operation) {
    const int saved_errno = errno;
    std::string message = surface_message(surface, std::move(operation));
    message += ": ";
    message += std::strerror(saved_errno);
    return Status{code, std::move(message)};
}

void wipe_payload(std::vector<std::uint8_t> &payload) noexcept {
    std::fill(payload.begin(), payload.end(), 0U);
}

bool unsupported_socket_option_error(int error) noexcept {
    return error == ENOPROTOOPT || error == EINVAL || error == EOPNOTSUPP ||
           error == ENOTSUP;
}

void close_received_rights(const cmsghdr &header) noexcept {
    if (header.cmsg_len < CMSG_LEN(0U)) return;
    const std::size_t bytes = header.cmsg_len - CMSG_LEN(0U);
    const std::size_t count = bytes / sizeof(int);
    const auto *data = CMSG_DATA(const_cast<cmsghdr *>(&header));
    for (std::size_t index = 0U; index < count; ++index) {
        int descriptor = -1;
        std::memcpy(
            &descriptor,
            data + (index * sizeof(int)),
            sizeof(descriptor));
        if (descriptor >= 0) static_cast<void>(::close(descriptor));
    }
}

}  // namespace

OwnedDescriptor::OwnedDescriptor(int descriptor) noexcept
    : descriptor_(descriptor) {}
OwnedDescriptor::~OwnedDescriptor() { reset(); }
OwnedDescriptor::OwnedDescriptor(OwnedDescriptor &&other) noexcept
    : descriptor_(std::exchange(other.descriptor_, -1)) {}
OwnedDescriptor &OwnedDescriptor::operator=(OwnedDescriptor &&other) noexcept {
    if (this != &other) reset(std::exchange(other.descriptor_, -1));
    return *this;
}
int OwnedDescriptor::get() const noexcept { return descriptor_; }
OwnedDescriptor::operator bool() const noexcept { return descriptor_ >= 0; }
int OwnedDescriptor::release() noexcept {
    return std::exchange(descriptor_, -1);
}
void OwnedDescriptor::reset(int descriptor) noexcept {
    if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
    descriptor_ = descriptor;
}

Result<bool> enable_record_credentials(
    int descriptor,
    std::string_view surface) {
    const int enabled = 1;
    if (::setsockopt(
            descriptor, SOL_SOCKET, SO_PASSCRED,
            &enabled, static_cast<socklen_t>(sizeof(enabled))) != 0) {
        return system_status(
            ErrorCode::io_error, surface,
            "could not enable per-record sender credentials");
    }

#if defined(SO_PASSPIDFD) && defined(SCM_PIDFD)
    if (::setsockopt(
            descriptor, SOL_SOCKET, SO_PASSPIDFD,
            &enabled, static_cast<socklen_t>(sizeof(enabled))) == 0) {
        return true;
    }
    const int option_error = errno;
    if (!unsupported_socket_option_error(option_error)) {
        errno = option_error;
        return system_status(
            ErrorCode::io_error, surface,
            "could not enable per-record sender pidfds");
    }
#endif
    return false;
}

Status verify_record_credentials(
    int descriptor,
    bool require_pidfd,
    std::string_view surface) {
    int enabled = 0;
    socklen_t length = static_cast<socklen_t>(sizeof(enabled));
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_PASSCRED,
            &enabled, &length) != 0) {
        return system_status(
            ErrorCode::io_error, surface,
            "could not verify inherited sender credentials");
    }
    if (length != sizeof(enabled) || enabled != 1) {
        return Status{
            ErrorCode::protocol_error,
            surface_message(
                surface,
                "accepted socket did not inherit per-record sender credentials")};
    }

    if (!require_pidfd) return Status::success();
#if defined(SO_PASSPIDFD) && defined(SCM_PIDFD)
    enabled = 0;
    length = static_cast<socklen_t>(sizeof(enabled));
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_PASSPIDFD,
            &enabled, &length) != 0) {
        return system_status(
            ErrorCode::io_error, surface,
            "could not verify inherited sender pidfds");
    }
    if (length != sizeof(enabled) || enabled != 1) {
        return Status{
            ErrorCode::protocol_error,
            surface_message(
                surface,
                "accepted socket did not inherit per-record sender pidfds")};
    }
    return Status::success();
#else
    return Status{
        ErrorCode::unsupported,
        surface_message(
            surface,
            "sender pidfds were required but are unavailable in the build headers")};
#endif
}

Result<PeerCredentials> connected_peer_credentials(
    int descriptor,
    std::string_view surface) {
    struct ucred credentials {};
    socklen_t length = static_cast<socklen_t>(sizeof(credentials));
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_PEERCRED,
            &credentials, &length) != 0) {
        return system_status(
            ErrorCode::io_error, surface,
            "could not read connection-time peer credentials");
    }
    if (length != sizeof(credentials) || credentials.pid <= 0) {
        return Status{
            ErrorCode::protocol_error,
            surface_message(
                surface,
                "connection-time peer credentials were malformed")};
    }
    PeerCredentials result;
    result.process_id = static_cast<std::int64_t>(credentials.pid);
    result.user_id = static_cast<std::uint64_t>(credentials.uid);
    result.group_id = static_cast<std::uint64_t>(credentials.gid);
    return result;
}

Result<OwnedDescriptor> connected_peer_pidfd(
    int descriptor,
    std::string_view surface) {
#if defined(SO_PEERPIDFD)
    int pidfd = -1;
    socklen_t length = static_cast<socklen_t>(sizeof(pidfd));
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_PEERPIDFD,
            &pidfd, &length) != 0) {
        const int option_error = errno;
        if (unsupported_socket_option_error(option_error)) {
            return OwnedDescriptor{};
        }
        if (option_error == ENODATA || option_error == ESRCH) {
            return Status{
                ErrorCode::unavailable,
                surface_message(
                    surface,
                    option_error == ESRCH
                        ? "connection peer exited before its identity was pinned"
                        : "connection peer process identity is unavailable")};
        }
        errno = option_error;
        return system_status(
            ErrorCode::io_error, surface,
            "could not obtain the connection peer pidfd");
    }
    if (length != sizeof(pidfd) || pidfd < 0) {
        if (pidfd >= 0) static_cast<void>(::close(pidfd));
        return Status{
            ErrorCode::protocol_error,
            surface_message(surface, "connection peer pidfd was malformed")};
    }

    const int flags = ::fcntl(pidfd, F_GETFD);
    if (flags < 0 || ::fcntl(pidfd, F_SETFD, flags | FD_CLOEXEC) != 0) {
        const Status failed = system_status(
            ErrorCode::io_error, surface,
            "could not seal the connection peer pidfd close-on-exec");
        static_cast<void>(::close(pidfd));
        return failed;
    }
    return OwnedDescriptor(pidfd);
#else
    static_cast<void>(descriptor);
    static_cast<void>(surface);
    return OwnedDescriptor{};
#endif
}

Result<ReceivedSeqpacket> receive_seqpacket(
    int descriptor,
    std::size_t maximum_payload,
    bool require_credentials,
    bool require_pidfd,
    int receive_flags,
    std::string_view surface) {
    if (maximum_payload == 0U ||
        maximum_payload == std::numeric_limits<std::size_t>::max()) {
        return Status{
            ErrorCode::invalid_argument,
            surface_message(surface, "receive limit is invalid")};
    }

    ReceivedSeqpacket record;
    record.payload.resize(maximum_payload + 1U);
    struct iovec vector {};
    vector.iov_base = record.payload.data();
    vector.iov_len = record.payload.size();

    alignas(cmsghdr) std::array<std::byte, kAncillaryBufferBytes> control{};
    struct msghdr message {};
    message.msg_iov = &vector;
    message.msg_iovlen = 1U;
    message.msg_control = control.data();
    message.msg_controllen = control.size();

    ssize_t count = -1;
    do {
        count = ::recvmsg(
            descriptor, &message,
            receive_flags | MSG_CMSG_CLOEXEC);
    } while (count < 0 && errno == EINTR);
    if (count < 0) {
        wipe_payload(record.payload);
        return (errno == EAGAIN || errno == EWOULDBLOCK)
            ? Status{
                  ErrorCode::timeout,
                  surface_message(surface, "record was not ready")}
            : system_status(
                  ErrorCode::io_error, surface,
                  "could not receive record");
    }
    if (count == 0) {
        wipe_payload(record.payload);
        return Status{
            ErrorCode::unavailable,
            surface_message(surface, "peer closed without a record")};
    }

    bool malformed_control = false;
    bool unexpected_control = false;
    bool duplicate_credentials = false;
    bool duplicate_pidfd = false;
    for (cmsghdr *header = CMSG_FIRSTHDR(&message);
         header != nullptr;
         header = CMSG_NXTHDR(&message, header)) {
        if (header->cmsg_len < CMSG_LEN(0U)) {
            malformed_control = true;
            continue;
        }
        const std::size_t data_bytes = header->cmsg_len - CMSG_LEN(0U);
        if (header->cmsg_level != SOL_SOCKET) {
            unexpected_control = true;
            continue;
        }
        if (header->cmsg_type == SCM_RIGHTS) {
            close_received_rights(*header);
            if (data_bytes == 0U || (data_bytes % sizeof(int)) != 0U) {
                malformed_control = true;
            }
            unexpected_control = true;
            continue;
        }
        if (header->cmsg_type == SCM_CREDENTIALS) {
            if (record.credentials_present) duplicate_credentials = true;
            if (header->cmsg_len != CMSG_LEN(sizeof(struct ucred))) {
                malformed_control = true;
                continue;
            }
            struct ucred credentials {};
            std::memcpy(
                &credentials, CMSG_DATA(header), sizeof(credentials));
            if (credentials.pid <= 0) {
                malformed_control = true;
                continue;
            }
            record.credentials.process_id =
                static_cast<std::int64_t>(credentials.pid);
            record.credentials.user_id =
                static_cast<std::uint64_t>(credentials.uid);
            record.credentials.group_id =
                static_cast<std::uint64_t>(credentials.gid);
            record.credentials_present = true;
            continue;
        }
#if defined(SCM_PIDFD)
        if (header->cmsg_type == SCM_PIDFD) {
            if (record.sender_pidfd) duplicate_pidfd = true;
            if (header->cmsg_len != CMSG_LEN(sizeof(int))) {
                malformed_control = true;
                continue;
            }
            int pidfd = -1;
            std::memcpy(&pidfd, CMSG_DATA(header), sizeof(pidfd));
            if (pidfd < 0) {
                malformed_control = true;
                continue;
            }
            if (!record.sender_pidfd) {
                record.sender_pidfd.reset(pidfd);
            } else {
                static_cast<void>(::close(pidfd));
            }
            continue;
        }
#endif
        unexpected_control = true;
    }

    if ((message.msg_flags & MSG_CTRUNC) != 0) {
        malformed_control = true;
    }
    if ((message.msg_flags & MSG_TRUNC) != 0 ||
        static_cast<std::size_t>(count) > maximum_payload) {
        wipe_payload(record.payload);
        return Status{
            ErrorCode::protocol_error,
            surface_message(surface, "record exceeds the receive ceiling")};
    }
    if (malformed_control || duplicate_credentials || duplicate_pidfd) {
        wipe_payload(record.payload);
        return Status{
            ErrorCode::protocol_error,
            surface_message(surface, "record ancillary data is malformed or truncated")};
    }
    if (unexpected_control) {
        wipe_payload(record.payload);
        return Status{
            ErrorCode::protocol_error,
            surface_message(surface, "record carried forbidden ancillary data")};
    }
    if (require_credentials != record.credentials_present) {
        wipe_payload(record.payload);
        return Status{
            ErrorCode::protocol_error,
            surface_message(
                surface,
                require_credentials
                    ? "record omitted kernel sender credentials"
                    : "record unexpectedly carried sender credentials")};
    }
    if (require_pidfd != static_cast<bool>(record.sender_pidfd)) {
        wipe_payload(record.payload);
        return Status{
            ErrorCode::protocol_error,
            surface_message(
                surface,
                require_pidfd
                    ? "record omitted the kernel sender pidfd"
                    : "record unexpectedly carried a sender pidfd")};
    }

    record.payload.resize(static_cast<std::size_t>(count));
    return record;
}

bool same_peer_credentials(
    const PeerCredentials &left,
    const PeerCredentials &right) noexcept {
    return left.process_id == right.process_id &&
           left.user_id == right.user_id &&
           left.group_id == right.group_id;
}

Result<OwnedDescriptor> open_process_pidfd(
    std::int64_t process_id,
    std::string_view surface) {
    if (process_id <= 0 ||
        process_id > static_cast<std::int64_t>(
            std::numeric_limits<pid_t>::max())) {
        return Status{
            ErrorCode::protocol_error,
            surface_message(surface, "sender process ID is outside pid_t")};
    }
#if defined(SYS_pidfd_open)
    errno = 0;
    const long result = ::syscall(
        SYS_pidfd_open, static_cast<pid_t>(process_id), 0U);
    if (result >= 0) {
        if (result > static_cast<long>(std::numeric_limits<int>::max())) {
            static_cast<void>(::close(static_cast<int>(result)));
            return Status{
                ErrorCode::io_error,
                surface_message(surface, "pidfd_open returned an invalid descriptor")};
        }
        const int descriptor = static_cast<int>(result);
        const int flags = ::fcntl(descriptor, F_GETFD);
        if (flags < 0 ||
            ::fcntl(descriptor, F_SETFD, flags | FD_CLOEXEC) != 0) {
            const Status failed = system_status(
                ErrorCode::io_error, surface,
                "could not seal sender pidfd close-on-exec");
            static_cast<void>(::close(descriptor));
            return failed;
        }
        return OwnedDescriptor(descriptor);
    }
    if (errno == ENOSYS) return OwnedDescriptor{};
    if (errno == ESRCH) {
        return Status{
            ErrorCode::unavailable,
            surface_message(surface, "record sender exited before its identity was pinned")};
    }
    return system_status(
        ErrorCode::io_error, surface,
        "could not open sender pidfd");
#else
    static_cast<void>(surface);
    return OwnedDescriptor{};
#endif
}

Result<bool> pidfd_has_exited(
    int descriptor,
    std::string_view surface) {
    if (descriptor < 0) {
        return Status{
            ErrorCode::invalid_argument,
            surface_message(surface, "pidfd is invalid")};
    }
    struct pollfd poll_descriptor {descriptor, POLLIN, 0};
    int ready = -1;
    do {
        ready = ::poll(&poll_descriptor, 1U, 0);
    } while (ready < 0 && errno == EINTR);
    if (ready < 0) {
        return system_status(
            ErrorCode::io_error, surface,
            "could not inspect sender pidfd");
    }
    if (ready == 0) return false;
    return (poll_descriptor.revents &
            (POLLIN | POLLHUP | POLLERR | POLLNVAL)) != 0;
}

}  // namespace iotox::local::detail
