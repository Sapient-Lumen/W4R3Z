#include "sync_replica_numeric_listener.hpp"

#if !defined(_WIN32)

#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <utility>

#ifdef __linux__
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace anonsync {

SyncReplicaNumericListener::SyncReplicaNumericListener(
    SyncReplicaNumericStreamEndpoint endpoint,
    std::string label)
    : endpoint_(std::move(endpoint)), label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica numeric listener label must not be empty");
    }
    // This function performs the shared numeric/port validation. Loopback is a
    // property returned to route-policy callers, not a requirement for a direct
    // listener, so the boolean is intentionally ignored here.
    (void)sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
        endpoint_, label_ + " endpoint");

#ifdef __linux__
    sockaddr_storage storage{};
    socklen_t bytes = 0U;
    int family = AF_UNSPEC;

    sockaddr_in ipv4{};
    ipv4.sin_family = AF_INET;
    ipv4.sin_port = htons(endpoint_.port);
    if (::inet_pton(
            AF_INET, endpoint_.numeric_address.c_str(), &ipv4.sin_addr) == 1) {
        family = AF_INET;
        std::memcpy(&storage, &ipv4, sizeof(ipv4));
        bytes = sizeof(ipv4);
    } else {
        sockaddr_in6 ipv6{};
        ipv6.sin6_family = AF_INET6;
        ipv6.sin6_port = htons(endpoint_.port);
        if (::inet_pton(
                AF_INET6, endpoint_.numeric_address.c_str(),
                &ipv6.sin6_addr) != 1) {
            throw std::invalid_argument(
                label_ +
                " address is not numeric IPv4 or unscoped IPv6");
        }
        family = AF_INET6;
        std::memcpy(&storage, &ipv6, sizeof(ipv6));
        bytes = sizeof(ipv6);
    }

    descriptor_ = ::socket(
        family, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (descriptor_ < 0) {
        throw std::runtime_error(
            label_ + " socket failed (errno " + std::to_string(errno) + ")");
    }

    try {
        int one = 1;
        if (::setsockopt(
                descriptor_, SOL_SOCKET, SO_REUSEADDR, &one,
                sizeof(one)) != 0) {
            throw std::runtime_error(
                label_ + " SO_REUSEADDR failed (errno " +
                std::to_string(errno) + ")");
        }
        if (family == AF_INET6 &&
            ::setsockopt(
                descriptor_, IPPROTO_IPV6, IPV6_V6ONLY, &one,
                sizeof(one)) != 0) {
            throw std::runtime_error(
                label_ + " IPV6_V6ONLY failed (errno " +
                std::to_string(errno) + ")");
        }
        if (::bind(
                descriptor_, reinterpret_cast<const sockaddr*>(&storage),
                bytes) != 0) {
            throw std::runtime_error(
                label_ + " bind failed (errno " +
                std::to_string(errno) + ")");
        }
        if (::listen(descriptor_, 16) != 0) {
            throw std::runtime_error(
                label_ + " listen failed (errno " +
                std::to_string(errno) + ")");
        }
        listener_ = std::make_unique<SyncReplicaFileTlsServerListener>(
            observe_sync_replica_file_tls_server_listener_or_throw(
                descriptor_, label_ + " capability"));
    } catch (...) {
        close_noexcept();
        throw;
    }
#else
    throw std::runtime_error(
        label_ + " cannot create a numeric listener on this platform");
#endif
}

SyncReplicaNumericListener::~SyncReplicaNumericListener() noexcept {
    close_noexcept();
}

SyncReplicaFileTlsServerListener&
SyncReplicaNumericListener::listener_or_throw() {
    if (descriptor_ < 0 || !listener_ || !listener_->active()) {
        throw std::logic_error(label_ + " listener owner is inactive");
    }
    return *listener_;
}

void SyncReplicaNumericListener::close_noexcept() noexcept {
    listener_.reset();
#ifdef __linux__
    if (descriptor_ >= 0) {
        const int owned = std::exchange(descriptor_, -1);
        // Linux may recycle the descriptor after EINTR; one close attempt ends
        // ownership and must not be retried.
        (void)::close(owned);
    }
#else
    descriptor_ = -1;
#endif
}

}  // namespace anonsync

#endif
