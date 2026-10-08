#include "sync_replica_stream_connector.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <exception>
#include <functional>
#include <iostream>
#include <optional>
#include <poll.h>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

#ifdef __linux__
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace {

using namespace std::chrono_literals;
using Clock = std::chrono::steady_clock;

constexpr std::string_view kValidOnion =
    "pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion";
constexpr std::string_view kTorIsolationToken = "rev0908-batch-scope";
constexpr std::string_view kSamSessionId = "anonsync-rev0908-test";
constexpr std::string_view kI2pPeer = "peer-example.b32.i2p";
constexpr std::string_view kPersistedSamDestination =
    "persisted-private-destination-token";
constexpr auto kIoTimeout = 5s;

static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaConnectedStream>);
static_assert(std::is_move_constructible_v<
              anonsync::SyncReplicaConnectedStream>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaStreamConnector>);
static_assert(!std::is_move_constructible_v<
              anonsync::SyncReplicaStreamConnector>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaI2pSamForwarder>);
static_assert(!std::is_move_constructible_v<
              anonsync::SyncReplicaI2pSamForwarder>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaI2pSamAcceptor>);
static_assert(!std::is_move_constructible_v<
              anonsync::SyncReplicaI2pSamAcceptor>);

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

#ifdef __linux__
class DescriptorOwner final {
public:
    DescriptorOwner() noexcept = default;
    explicit DescriptorOwner(int descriptor) noexcept
        : descriptor_(descriptor) {}
    DescriptorOwner(const DescriptorOwner&) = delete;
    DescriptorOwner& operator=(const DescriptorOwner&) = delete;
    DescriptorOwner(DescriptorOwner&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    DescriptorOwner& operator=(DescriptorOwner&& other) noexcept {
        if (this != &other) {
            close_noexcept();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }
    ~DescriptorOwner() noexcept { close_noexcept(); }

    [[nodiscard]] int get() const noexcept { return descriptor_; }

    void close_noexcept() noexcept {
        if (descriptor_ >= 0) {
            const int descriptor = std::exchange(descriptor_, -1);
            (void)::close(descriptor);
        }
    }

private:
    int descriptor_ = -1;
};

struct LoopbackListener final {
    DescriptorOwner socket;
    std::uint16_t port = 0U;
};

[[nodiscard]] LoopbackListener make_loopback_listener() {
    errno = 0;
    const int raw = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (raw < 0) {
        throw std::runtime_error(
            "test listener socket failed (errno " +
            std::to_string(errno) + ")");
    }
    DescriptorOwner owner(raw);
    int reuse = 1;
    if (::setsockopt(raw, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) !=
        0) {
        throw std::runtime_error("test listener SO_REUSEADDR failed");
    }
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = 0U;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (::bind(
            raw, reinterpret_cast<const sockaddr*>(&address),
            sizeof(address)) != 0) {
        throw std::runtime_error(
            "test listener bind failed (errno " +
            std::to_string(errno) + ")");
    }
    if (::listen(raw, 8) != 0) {
        throw std::runtime_error("test listener listen failed");
    }
    sockaddr_in bound{};
    socklen_t bytes = sizeof(bound);
    if (::getsockname(
            raw, reinterpret_cast<sockaddr*>(&bound), &bytes) != 0 ||
        bytes != sizeof(bound)) {
        throw std::runtime_error("test listener getsockname failed");
    }
    return {std::move(owner), ntohs(bound.sin_port)};
}

void wait_descriptor_or_throw(
    int descriptor,
    short events,
    std::string_view label) {
    pollfd item{};
    item.fd = descriptor;
    item.events = events;
    const auto deadline = Clock::now() + kIoTimeout;
    for (;;) {
        const auto now = Clock::now();
        if (now >= deadline) {
            throw std::runtime_error(std::string(label) + " timed out");
        }
        const auto remaining = std::chrono::duration_cast<
            std::chrono::milliseconds>(deadline - now);
        const int milliseconds = static_cast<int>(
            std::max<std::int64_t>(1, remaining.count()));
        errno = 0;
        const int result = ::poll(&item, 1U, milliseconds);
        const int poll_errno = errno;
        if (result > 0) {
            if ((item.revents & POLLNVAL) != 0) {
                throw std::runtime_error(
                    std::string(label) + " observed POLLNVAL");
            }
            return;
        }
        if (result == 0) continue;
        if (poll_errno == EINTR) continue;
        throw std::runtime_error(
            std::string(label) + " poll failed (errno " +
            std::to_string(poll_errno) + ")");
    }
}

[[nodiscard]] DescriptorOwner accept_one_or_throw(
    int listener,
    std::string_view label) {
    wait_descriptor_or_throw(listener, POLLIN, label);
    for (;;) {
        errno = 0;
        const int accepted = ::accept4(listener, nullptr, nullptr, SOCK_CLOEXEC);
        const int accept_errno = errno;
        if (accepted >= 0) return DescriptorOwner(accepted);
        if (accept_errno == EINTR) continue;
        throw std::runtime_error(
            std::string(label) + " accept failed (errno " +
            std::to_string(accept_errno) + ")");
    }
}

// Closing one TCP connection before writing a marker on another does not
// establish cross-connection receive order. This oracle half-closes the SAM
// control stream and waits until Linux reports FIN_WAIT2, which means the peer
// kernel acknowledged the FIN. Only then may the data stream release the
// application marker that lets the connector begin its reuse check.
void shutdown_write_and_wait_for_fin_ack_or_throw(
    int descriptor,
    std::string_view label) {
    errno = 0;
    if (::shutdown(descriptor, SHUT_WR) != 0) {
        throw std::runtime_error(
            std::string(label) + " shutdown failed (errno " +
            std::to_string(errno) + ")");
    }

    const auto deadline = Clock::now() + kIoTimeout;
    for (;;) {
        tcp_info info{};
        socklen_t bytes = sizeof(info);
        errno = 0;
        if (::getsockopt(
                descriptor, IPPROTO_TCP, TCP_INFO, &info, &bytes) != 0) {
            throw std::runtime_error(
                std::string(label) + " TCP_INFO failed (errno " +
                std::to_string(errno) + ")");
        }
        if (bytes < sizeof(info.tcpi_state)) {
            throw std::runtime_error(
                std::string(label) + " TCP_INFO state was truncated");
        }
        if (info.tcpi_state == TCP_FIN_WAIT2) return;
        if (info.tcpi_state != TCP_FIN_WAIT1 &&
            info.tcpi_state != TCP_ESTABLISHED) {
            throw std::runtime_error(
                std::string(label) + " entered unexpected TCP state " +
                std::to_string(info.tcpi_state));
        }
        if (Clock::now() >= deadline) {
            throw std::runtime_error(
                std::string(label) + " FIN acknowledgement timed out");
        }
        std::this_thread::sleep_for(1ms);
    }
}

void write_all_or_throw(
    int descriptor,
    std::span<const unsigned char> bytes,
    std::string_view label) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        wait_descriptor_or_throw(descriptor, POLLOUT, label);
        errno = 0;
        const ssize_t written = ::send(
            descriptor, bytes.data() + offset, bytes.size() - offset,
            MSG_NOSIGNAL);
        const int send_errno = errno;
        if (written > 0) {
            offset += static_cast<std::size_t>(written);
            continue;
        }
        if (written < 0 && send_errno == EINTR) continue;
        if (written < 0 &&
            (send_errno == EAGAIN || send_errno == EWOULDBLOCK)) {
            continue;
        }
        throw std::runtime_error(
            std::string(label) + " send failed (errno " +
            std::to_string(send_errno) + ")");
    }
}

void write_all_or_throw(
    int descriptor,
    std::string_view bytes,
    std::string_view label) {
    write_all_or_throw(
        descriptor,
        std::span<const unsigned char>(
            reinterpret_cast<const unsigned char*>(bytes.data()),
            bytes.size()),
        label);
}

template <std::size_t Size>
void write_all_or_throw(
    int descriptor,
    const std::array<unsigned char, Size>& bytes,
    std::string_view label) {
    write_all_or_throw(
        descriptor, std::span<const unsigned char>(bytes), label);
}

[[nodiscard]] std::vector<unsigned char> read_exact_or_throw(
    int descriptor,
    std::size_t byte_count,
    std::string_view label) {
    std::vector<unsigned char> bytes(byte_count);
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        wait_descriptor_or_throw(descriptor, POLLIN, label);
        errno = 0;
        const ssize_t received = ::recv(
            descriptor, bytes.data() + offset, bytes.size() - offset, 0);
        const int receive_errno = errno;
        if (received > 0) {
            offset += static_cast<std::size_t>(received);
            continue;
        }
        if (received == 0) {
            throw std::runtime_error(
                std::string(label) + " peer closed early");
        }
        if (receive_errno == EINTR || receive_errno == EAGAIN ||
            receive_errno == EWOULDBLOCK) {
            continue;
        }
        throw std::runtime_error(
            std::string(label) + " receive failed (errno " +
            std::to_string(receive_errno) + ")");
    }
    return bytes;
}

[[nodiscard]] std::string read_line_or_throw(
    int descriptor,
    std::string_view label) {
    std::string line;
    line.reserve(128U);
    while (line.size() < 16384U) {
        const auto byte = read_exact_or_throw(descriptor, 1U, label);
        if (byte[0] == static_cast<unsigned char>('\n')) return line;
        if (byte[0] == 0U) {
            throw std::runtime_error(std::string(label) + " contains NUL");
        }
        line.push_back(static_cast<char>(byte[0]));
    }
    throw std::runtime_error(std::string(label) + " line is oversized");
}

void exchange_marker_server_or_throw(
    int descriptor,
    unsigned char expected,
    unsigned char response,
    std::string_view label) {
    const auto marker = read_exact_or_throw(descriptor, 1U, label);
    if (marker[0] != expected) {
        throw std::runtime_error(std::string(label) + " marker mismatch");
    }
    const std::array<unsigned char, 1U> reply{response};
    write_all_or_throw(descriptor, reply, label);
}

void exchange_marker_client_or_throw(
    const anonsync::SyncReplicaConnectedStream& stream,
    unsigned char marker,
    unsigned char expected,
    std::string_view label) {
    const std::array<unsigned char, 1U> request{marker};
    write_all_or_throw(stream.descriptor(), request, label);
    const auto response = read_exact_or_throw(stream.descriptor(), 1U, label);
    require(response[0] == expected, "routed marker response mismatch");
}

class ServerThread final {
public:
    explicit ServerThread(std::function<void()> function)
        : thread_([this, function = std::move(function)]() mutable {
              try {
                  function();
              } catch (...) {
                  error_ = std::current_exception();
              }
          }) {}
    ServerThread(const ServerThread&) = delete;
    ServerThread& operator=(const ServerThread&) = delete;
    ~ServerThread() {
        if (thread_.joinable()) thread_.join();
    }

    void join_and_rethrow() {
        if (thread_.joinable()) thread_.join();
        if (error_) std::rethrow_exception(error_);
    }

private:
    std::thread thread_;
    std::exception_ptr error_;
};

[[nodiscard]] anonsync::SyncReplicaNumericStreamEndpoint endpoint_for(
    const LoopbackListener& listener) {
    return {"127.0.0.1", listener.port};
}

[[nodiscard]] DescriptorOwner connect_loopback_or_throw(
    std::uint16_t port,
    std::string_view label) {
    errno = 0;
    const int raw = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (raw < 0) {
        throw std::runtime_error(
            std::string(label) + " socket failed (errno " +
            std::to_string(errno) + ")");
    }
    DescriptorOwner owner(raw);
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    for (;;) {
        errno = 0;
        if (::connect(
                raw, reinterpret_cast<const sockaddr*>(&address),
                sizeof(address)) == 0) {
            return owner;
        }
        const int connect_errno = errno;
        if (connect_errno == EINTR) continue;
        throw std::runtime_error(
            std::string(label) + " connect failed (errno " +
            std::to_string(connect_errno) + ")");
    }
}

void expect_peer_close_or_throw(int descriptor, std::string_view label) {
    wait_descriptor_or_throw(descriptor, POLLIN | POLLHUP, label);
    std::array<unsigned char, 1U> byte{};
    for (;;) {
        errno = 0;
        const ssize_t received = ::recv(descriptor, byte.data(), byte.size(), 0);
        const int receive_errno = errno;
        if (received == 0) return;
        if (received > 0) {
            throw std::runtime_error(
                std::string(label) + " received unexpected bytes before close");
        }
        if (receive_errno == EINTR) continue;
        if (receive_errno == EAGAIN || receive_errno == EWOULDBLOCK) {
            wait_descriptor_or_throw(descriptor, POLLIN | POLLHUP, label);
            continue;
        }
        throw std::runtime_error(
            std::string(label) + " close observation failed (errno " +
            std::to_string(receive_errno) + ")");
    }
}

void test_route_validation_and_tor_checksum() {
    anonsync::validate_sync_replica_stream_route_or_throw(
        anonsync::SyncReplicaDirectTcpRoute{{"127.0.0.1", 1U}},
        "valid direct route");
    anonsync::validate_sync_replica_stream_route_or_throw(
        anonsync::SyncReplicaTorSocks5Route{
            {"127.0.0.1", 9050U}, std::string(kValidOnion), 443U,
            std::string(kTorIsolationToken)},
        "valid Tor route");
    anonsync::validate_sync_replica_tor_v3_onion_service_or_throw(
        kValidOnion, "valid standalone Tor onion service");
    anonsync::validate_sync_replica_stream_route_or_throw(
        anonsync::SyncReplicaI2pSamRoute{
            {"127.0.0.1", 7656U}, std::string(kSamSessionId),
            std::string(kI2pPeer)},
        "valid I2P route");

    require(
        anonsync::sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
            {"127.63.18.9", 1U}, "IPv4 loopback probe"),
        "127/8 endpoint was not recognized as loopback");
    require(
        anonsync::sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
            {"::1", 1U}, "IPv6 loopback probe"),
        "IPv6 ::1 endpoint was not recognized as loopback");
    require(
        !anonsync::sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
            {"192.0.2.1", 1U}, "non-loopback probe"),
        "documentation address was falsely recognized as loopback");

    anonsync::validate_sync_replica_i2p_sam_forward_route_or_throw(
        anonsync::SyncReplicaI2pSamForwardRoute{
            {"127.0.0.1", 7656U}, std::string(kSamSessionId),
            std::string(kPersistedSamDestination), {"127.0.0.1", 4433U},
            2U, 2U},
        "valid I2P SAM forward route");

    require_throws(
        [] {
            anonsync::SyncReplicaStreamConnector connector(
                anonsync::SyncReplicaDirectTcpRoute{{"localhost", 1U}},
                "DNS-forbidden direct route");
            (void)connector;
        },
        "direct route accepted a process-global DNS name");
    require_throws(
        [] {
            std::string invalid(kValidOnion);
            invalid[0U] = invalid[0U] == 'p' ? 'q' : 'p';
            anonsync::SyncReplicaStreamConnector connector(
                anonsync::SyncReplicaTorSocks5Route{
                    {"127.0.0.1", 9050U}, std::move(invalid), 443U,
                    std::string(kTorIsolationToken)},
                "bad-checksum Tor route");
            (void)connector;
        },
        "Tor route accepted a syntactic v3 address with a bad checksum");
    require_throws(
        [] {
            anonsync::SyncReplicaStreamConnector connector(
                anonsync::SyncReplicaTorSocks5Route{
                    {"127.0.0.1", 9050U}, std::string(kValidOnion), 443U,
                    "token with spaces"},
                "unsafe isolation route");
            (void)connector;
        },
        "Tor route accepted an ambiguous isolation token");
    require_throws(
        [] {
            anonsync::SyncReplicaStreamConnector connector(
                anonsync::SyncReplicaI2pSamRoute{
                    {"127.0.0.1", 7656U}, "bad session id!",
                    std::string(kI2pPeer)},
                "unsafe SAM session route");
            (void)connector;
        },
        "I2P route accepted command-injecting session syntax");

    require_throws(
        [] {
            anonsync::SyncReplicaStreamConnector connector(
                anonsync::SyncReplicaTorSocks5Route{
                    {"192.0.2.1", 9050U}, std::string(kValidOnion), 443U,
                    std::string(kTorIsolationToken)},
                "remote plaintext Tor proxy route");
            (void)connector;
        },
        "Tor route accepted a non-loopback plaintext SOCKS proxy");
    require_throws(
        [] {
            anonsync::SyncReplicaStreamConnector connector(
                anonsync::SyncReplicaI2pSamRoute{
                    {"192.0.2.1", 7656U}, std::string(kSamSessionId),
                    std::string(kI2pPeer)},
                "remote plaintext SAM route");
            (void)connector;
        },
        "I2P route accepted a non-loopback plaintext SAM bridge");
    require_throws(
        [] {
            anonsync::validate_sync_replica_i2p_sam_forward_route_or_throw(
                anonsync::SyncReplicaI2pSamForwardRoute{
                    {"127.0.0.1", 7656U}, std::string(kSamSessionId),
                    std::string(kPersistedSamDestination),
                    {"192.0.2.1", 4433U}, 2U, 2U},
                "remote I2P forward target");
        },
        "I2P SAM forward route accepted a non-loopback target");
    require_throws(
        [] {
            anonsync::validate_sync_replica_i2p_sam_forward_route_or_throw(
                anonsync::SyncReplicaI2pSamForwardRoute{
                    {"127.0.0.1", 7656U}, std::string(kSamSessionId),
                    "TRANSIENT", {"127.0.0.1", 4433U}, 2U, 2U},
                "transient I2P forward identity");
        },
        "I2P SAM forward route accepted a transient inbound identity");

    require(
        anonsync::sync_replica_stream_route_kind_name(
            anonsync::SyncReplicaStreamRouteKind::DirectTcp) == "direct_tcp",
        "direct route-kind name changed");
    require(
        anonsync::sync_replica_i2p_sam_result_name(
            anonsync::SyncReplicaI2pSamResult::DuplicateDestination) ==
            "duplicate_destination",
        "SAM duplicate-destination result name changed");
    require(
        anonsync::sync_replica_i2p_sam_result_name(
            anonsync::SyncReplicaI2pSamResult::LeaseSetNotFound) ==
            "leaseset_not_found",
        "SAM leaseset-not-found result name changed");
}

void test_deadline_precedes_socket_authority() {
    anonsync::SyncReplicaStreamConnector direct(
        anonsync::SyncReplicaDirectTcpRoute{{"127.0.0.1", 1U}},
        "expired direct connector");
    auto outcome = direct.connect_until_or_throw(Clock::now() - 1ms);
    require(
        outcome.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::DeadlineExpired,
        "expired connector did not return deadline disposition");
    require(
        outcome.report.terminal_stage ==
            anonsync::SyncReplicaStreamRouteStage::NumericConnect,
        "expired connector reported the wrong stage");
    require(!outcome.report.data_socket_created,
            "expired connector created a socket");
    require(!outcome.stream.has_value(),
            "expired connector returned stream authority");
}

void test_direct_stream() {
    LoopbackListener listener = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner peer =
            accept_one_or_throw(listener.socket.get(), "direct server");
        exchange_marker_server_or_throw(
            peer.get(), 0x41U, 0x42U, "direct server");
    });

    anonsync::SyncReplicaStreamConnector connector(
        anonsync::SyncReplicaDirectTcpRoute{endpoint_for(listener)},
        "direct connector");
    auto outcome = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        outcome.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::Connected,
        "direct route did not connect");
    require(
        outcome.report.terminal_stage ==
            anonsync::SyncReplicaStreamRouteStage::Complete,
        "direct route did not reach complete stage");
    require(outcome.report.route_negotiated,
            "direct route did not mark route negotiation complete");
    require(outcome.report.data_socket_created,
            "direct route omitted socket creation report");
    require(outcome.report.data_socket_policy_verified,
            "direct route omitted socket-policy report");
    require(outcome.report.numeric_connect_attempts == 1U,
            "direct route attempted numeric connect more than once");
    require(outcome.report.route_bytes_written == 0U &&
                outcome.report.route_bytes_received == 0U,
            "direct route unexpectedly emitted proxy protocol bytes");
    require(outcome.stream.has_value(),
            "direct route omitted stream ownership");
    exchange_marker_client_or_throw(
        *outcome.stream, 0x41U, 0x42U, "direct client");
    server.join_and_rethrow();
}

void serve_tor_success_or_throw(
    int listener,
    std::string_view expected_token,
    unsigned char request_marker,
    unsigned char response_marker) {
    DescriptorOwner peer = accept_one_or_throw(listener, "Tor SOCKS server");
    require(
        read_exact_or_throw(peer.get(), 3U, "Tor method request") ==
            std::vector<unsigned char>({0x05U, 0x01U, 0x02U}),
        "Tor connector did not require username/password method");
    write_all_or_throw(
        peer.get(), std::array<unsigned char, 2U>{0x05U, 0x02U},
        "Tor method response");

    const auto auth_prefix =
        read_exact_or_throw(peer.get(), 2U, "Tor auth prefix");
    require(auth_prefix[0U] == 0x01U,
            "Tor connector used the wrong auth version");
    const auto username = read_exact_or_throw(
        peer.get(), auth_prefix[1U], "Tor auth username");
    require(
        std::string(username.begin(), username.end()) == "<torS0X>0",
        "Tor connector did not use format-zero isolation username");
    const auto password_length =
        read_exact_or_throw(peer.get(), 1U, "Tor auth password length");
    const auto password = read_exact_or_throw(
        peer.get(), password_length[0U], "Tor auth password");
    require(
        std::string(password.begin(), password.end()) == expected_token,
        "Tor connector changed the isolation token");
    write_all_or_throw(
        peer.get(), std::array<unsigned char, 2U>{0x01U, 0x00U},
        "Tor auth response");

    const auto connect_prefix =
        read_exact_or_throw(peer.get(), 5U, "Tor connect prefix");
    require(
        connect_prefix[0U] == 0x05U && connect_prefix[1U] == 0x01U &&
            connect_prefix[2U] == 0x00U && connect_prefix[3U] == 0x03U,
        "Tor connector did not request a SOCKS5 domain connect");
    const auto domain = read_exact_or_throw(
        peer.get(), connect_prefix[4U], "Tor onion domain");
    require(
        std::string(domain.begin(), domain.end()) == kValidOnion,
        "Tor connector did not pass the exact onion address to Tor");
    const auto port = read_exact_or_throw(peer.get(), 2U, "Tor service port");
    require(port == std::vector<unsigned char>({0x01U, 0xbbU}),
            "Tor connector changed the onion service port");
    write_all_or_throw(
        peer.get(),
        std::array<unsigned char, 10U>{
            0x05U, 0x00U, 0x00U, 0x01U, 127U, 0U, 0U, 1U, 0U, 0U},
        "Tor connect response");

    exchange_marker_server_or_throw(
        peer.get(), request_marker, response_marker, "Tor routed stream");
}

void test_tor_socks5_stream_and_isolation() {
    LoopbackListener listener = make_loopback_listener();
    ServerThread server([&] {
        serve_tor_success_or_throw(
            listener.socket.get(), kTorIsolationToken, 0x51U, 0x52U);
    });

    anonsync::SyncReplicaStreamConnector connector(
        anonsync::SyncReplicaTorSocks5Route{
            endpoint_for(listener), std::string(kValidOnion), 443U,
            std::string(kTorIsolationToken)},
        "Tor connector");
    auto outcome = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        outcome.report.route_kind ==
            anonsync::SyncReplicaStreamRouteKind::TorSocks5,
        "Tor connector reported the wrong route kind");
    require(
        outcome.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::Connected,
        "Tor connector did not connect");
    require(outcome.report.socks5_reply == 0U,
            "Tor connector did not preserve the SOCKS5 reply");
    require(outcome.report.route_bytes_written > 0U &&
                outcome.report.route_bytes_received > 0U,
            "Tor connector omitted route byte accounting");
    require(outcome.report.numeric_connect_attempts == 1U,
            "Tor connector attempted its proxy more than once");
    require(outcome.stream.has_value(),
            "Tor connector omitted routed stream ownership");
    exchange_marker_client_or_throw(
        *outcome.stream, 0x51U, 0x52U, "Tor client stream");
    server.join_and_rethrow();
}

void test_tor_route_rejection_is_typed() {
    LoopbackListener listener = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner peer =
            accept_one_or_throw(listener.socket.get(), "rejecting Tor server");
        (void)read_exact_or_throw(peer.get(), 3U, "Tor reject method");
        write_all_or_throw(
            peer.get(), std::array<unsigned char, 2U>{0x05U, 0xffU},
            "Tor reject response");
    });

    anonsync::SyncReplicaStreamConnector connector(
        anonsync::SyncReplicaTorSocks5Route{
            endpoint_for(listener), std::string(kValidOnion), 443U,
            std::string(kTorIsolationToken)},
        "rejecting Tor connector");
    auto outcome = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        outcome.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::RouteRejected,
        "SOCKS method rejection was not typed as route rejection");
    require(
        outcome.report.terminal_stage ==
            anonsync::SyncReplicaStreamRouteStage::TorMethodNegotiation,
        "SOCKS method rejection reported the wrong stage");
    require(!outcome.stream.has_value(),
            "rejected Tor route returned stream authority");
    server.join_and_rethrow();
}

void expect_sam_hello_or_throw(
    int descriptor,
    std::string_view label,
    std::string_view selected_version = "3.1") {
    require(
        read_line_or_throw(descriptor, label) ==
            "HELLO VERSION MIN=3.1 MAX=3.2",
        "SAM connector did not advertise its supported 3.1..3.2 range");
    require(selected_version == "3.1" || selected_version == "3.2",
            "test selected an unsupported SAM version");
    write_all_or_throw(
        descriptor,
        "HELLO REPLY RESULT=OK VERSION=" + std::string(selected_version) +
            "\n",
        label);
}

[[nodiscard]] std::string runtime_sam_session_id_or_throw(
    std::string_view command,
    std::string_view label) {
    const std::size_t marker = command.find("ID=");
    require(
        marker != std::string_view::npos &&
            (marker == 0U || command[marker - 1U] == ' '),
        "SAM command omitted a token-bounded session ID");
    const std::size_t begin = marker + 3U;
    const std::size_t end = command.find(' ', begin);
    const std::string session_id(command.substr(
        begin, end == std::string_view::npos
            ? command.size() - begin
            : end - begin));
    constexpr std::size_t kRuntimeSuffixHexBytes = 32U;
    constexpr std::size_t kMaximumSessionIdBytes = 64U;
    constexpr std::size_t kMaximumBaseBytes =
        kMaximumSessionIdBytes - 1U - kRuntimeSuffixHexBytes;
    const std::string expected_prefix =
        std::string(kSamSessionId.substr(0U, kMaximumBaseBytes)) + ".";
    require(session_id.starts_with(expected_prefix),
            "SAM runtime session ID lost its configured base");
    require(session_id != kSamSessionId,
            "SAM connector reused the literal configured session ID");
    require(session_id.size() ==
                expected_prefix.size() + kRuntimeSuffixHexBytes,
            "SAM runtime session ID has the wrong suffix width");
    require(session_id.size() <= kMaximumSessionIdBytes,
            "SAM runtime session ID exceeds the protocol bound");
    require(
        std::all_of(
            session_id.begin() + expected_prefix.size(),
            session_id.end(), [](char value) {
                return (value >= '0' && value <= '9') ||
                       (value >= 'a' && value <= 'f');
            }),
        "SAM runtime session ID suffix is not lowercase hexadecimal");
    (void)label;
    return session_id;
}

[[nodiscard]] std::string expect_sam_session_create_or_throw(
    int descriptor,
    std::string_view label) {
    const std::string line = read_line_or_throw(descriptor, label);
    require(line.starts_with("SESSION CREATE STYLE=STREAM ID="),
            "SAM connector omitted STREAM session create");
    const std::string session_id =
        runtime_sam_session_id_or_throw(line, label);
    require(line.find("DESTINATION=TRANSIENT") != std::string::npos,
            "SAM connector did not request a transient outbound identity");
    require(line.find("SIGNATURE_TYPE=7") != std::string::npos,
            "SAM connector omitted transient Ed25519 signature type");
    require(line.find("i2cp.leaseSetEncType=4") != std::string::npos,
            "SAM connector omitted ECIES-X25519 lease-set encryption");
    require(line.find("inbound.quantity=2") != std::string::npos &&
                line.find("outbound.quantity=2") != std::string::npos,
            "SAM connector omitted explicit tunnel quantities");
    write_all_or_throw(
        descriptor, "SESSION STATUS RESULT=OK DESTINATION=fake-private-key\n",
        label);
    return session_id;
}

[[nodiscard]] std::string expect_persisted_sam_session_create_or_throw(
    int descriptor,
    std::string_view label) {
    const std::string line = read_line_or_throw(descriptor, label);
    require(line.starts_with("SESSION CREATE STYLE=STREAM ID="),
            "persisted SAM connector omitted STREAM session create");
    const std::string session_id =
        runtime_sam_session_id_or_throw(line, label);
    require(
        line.find(
            "DESTINATION=" + std::string(kPersistedSamDestination)) !=
            std::string::npos,
        "persisted SAM connector changed the private destination");
    require(line.find("SIGNATURE_TYPE=") == std::string::npos,
            "persisted SAM connector sent TRANSIENT-only SIGNATURE_TYPE");
    require(line.find("i2cp.leaseSetEncType=4") != std::string::npos,
            "persisted SAM connector omitted lease-set encryption");
    require(line.find("inbound.quantity=2") != std::string::npos &&
                line.find("outbound.quantity=2") != std::string::npos,
            "persisted SAM connector omitted explicit tunnel quantities");
    write_all_or_throw(
        descriptor,
        "SESSION STATUS RESULT=OK DESTINATION=persisted-public-destination\n",
        label);
    return session_id;
}

void expect_sam_stream_connect_or_throw(
    int descriptor,
    std::string_view expected_session_id,
    std::string_view label) {
    expect_sam_hello_or_throw(descriptor, label);
    const std::string line = read_line_or_throw(descriptor, label);
    require(line.starts_with("STREAM CONNECT "),
            "SAM connector omitted STREAM CONNECT");
    require(line.find("ID=" + std::string(expected_session_id)) !=
                std::string::npos,
            "SAM stream changed the session ID");
    require(line.find("DESTINATION=" + std::string(kI2pPeer)) !=
                std::string::npos,
            "SAM stream changed the I2P peer destination");
    require(line.find("SILENT=false") != std::string::npos,
            "SAM stream omitted explicit result reporting");
    write_all_or_throw(descriptor, "STREAM STATUS RESULT=OK\n", label);
}

void expect_sam_stream_forward_or_throw(
    int descriptor,
    const LoopbackListener& local_receiver,
    std::string_view expected_session_id,
    std::string_view label) {
    expect_sam_hello_or_throw(descriptor, label);
    const std::string line = read_line_or_throw(descriptor, label);
    require(line.starts_with("STREAM FORWARD "),
            "SAM forwarder omitted STREAM FORWARD");
    require(line.find("ID=" + std::string(expected_session_id)) !=
                std::string::npos,
            "SAM forwarder changed the session ID");
    require(line.find("HOST=127.0.0.1") != std::string::npos,
            "SAM forwarder changed the loopback host");
    require(
        line.find("PORT=" + std::to_string(local_receiver.port)) !=
            std::string::npos,
        "SAM forwarder changed the local receiver port");
    require(line.find("SILENT=true") != std::string::npos,
            "SAM forwarder did not suppress destination-line injection");
    require(line.find("SILENT=false") == std::string::npos,
            "SAM forwarder enabled destination-line injection");
    write_all_or_throw(descriptor, "STREAM STATUS RESULT=OK\n", label);
}

void expect_sam_stream_accept_or_throw(
    int descriptor,
    std::string_view expected_session_id,
    std::string_view label) {
    expect_sam_hello_or_throw(descriptor, label, "3.2");
    const std::string line = read_line_or_throw(descriptor, label);
    require(line.starts_with("STREAM ACCEPT "),
            "SAM acceptor omitted STREAM ACCEPT");
    require(line.find("ID=" + std::string(expected_session_id)) !=
                std::string::npos,
            "SAM acceptor changed the session ID");
    require(line.find("SILENT=false") != std::string::npos,
            "SAM acceptor suppressed its peer destination line");
    require(line.find("HOST=") == std::string::npos &&
                line.find("PORT=") == std::string::npos,
            "SAM acceptor introduced a local forwarding endpoint");
    write_all_or_throw(descriptor, "STREAM STATUS RESULT=OK\n", label);
}

[[nodiscard]] std::string full_i2p_peer_destination() {
    // SAM STREAM ACCEPT reports the full base64 destination, not a b32 name.
    return std::string(516U, 'A');
}

[[nodiscard]] anonsync::SyncReplicaI2pSamRoute i2p_route_for(
    const LoopbackListener& listener) {
    return {
        endpoint_for(listener), std::string(kSamSessionId),
        std::string(kI2pPeer), "TRANSIENT", 2U, 2U};
}

void test_i2p_runtime_session_ids_are_owner_unique() {
    const anonsync::SyncReplicaI2pSamRoute configured{
        {"127.0.0.1", 1U}, std::string(kSamSessionId),
        std::string(kI2pPeer), "TRANSIENT", 2U, 2U};
    anonsync::SyncReplicaStreamConnector first(
        configured, "first runtime-ID connector");
    anonsync::SyncReplicaStreamConnector second(
        configured, "second runtime-ID connector");
    const auto& first_route =
        std::get<anonsync::SyncReplicaI2pSamRoute>(first.route());
    const auto& second_route =
        std::get<anonsync::SyncReplicaI2pSamRoute>(second.route());
    require(
        runtime_sam_session_id_or_throw(
            "ID=" + first_route.session_id, "first runtime ID") ==
            first_route.session_id,
        "first connector did not expose its materialized runtime ID");
    require(
        runtime_sam_session_id_or_throw(
            "ID=" + second_route.session_id, "second runtime ID") ==
            second_route.session_id,
        "second connector did not expose its materialized runtime ID");
    require(first_route.session_id != second_route.session_id,
            "independent connectors reused one bridge-global SAM session ID");

    anonsync::SyncReplicaI2pSamForwarder forwarder(
        anonsync::SyncReplicaI2pSamForwardRoute{
            {"127.0.0.1", 1U}, std::string(kSamSessionId),
            std::string(kPersistedSamDestination), {"127.0.0.1", 2U},
            2U, 2U},
        "runtime-ID forwarder");
    const std::string& forward_id = forwarder.route().session_id;
    require(
        runtime_sam_session_id_or_throw(
            "ID=" + forward_id, "forwarder runtime ID") == forward_id,
        "forwarder did not expose its materialized runtime ID");
    require(forward_id != first_route.session_id &&
                forward_id != second_route.session_id,
            "inbound and outbound owners reused one bridge-global SAM ID");
}

void test_i2p_persisted_destination_omits_transient_signature_option() {
    LoopbackListener listener = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner control = accept_one_or_throw(
            listener.socket.get(), "persisted SAM control");
        expect_sam_hello_or_throw(
            control.get(), "persisted SAM control hello");
        const std::string session_id =
            expect_persisted_sam_session_create_or_throw(
            control.get(), "persisted SAM session create");

        DescriptorOwner data = accept_one_or_throw(
            listener.socket.get(), "persisted SAM stream");
        expect_sam_stream_connect_or_throw(
            data.get(), session_id, "persisted SAM stream");
        exchange_marker_server_or_throw(
            data.get(), 0x59U, 0x5aU, "persisted SAM stream");
    });

    anonsync::SyncReplicaI2pSamRoute route = i2p_route_for(listener);
    route.session_destination = std::string(kPersistedSamDestination);
    anonsync::SyncReplicaStreamConnector connector(
        std::move(route), "persisted-destination I2P connector");
    auto outcome = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        outcome.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::Connected,
        "persisted-destination SAM stream did not connect");
    require(outcome.report.control_session_created,
            "persisted-destination SAM session was not created");
    require(outcome.stream.has_value(),
            "persisted-destination SAM stream omitted authority");
    exchange_marker_client_or_throw(
        *outcome.stream, 0x59U, 0x5aU, "persisted SAM client stream");
    server.join_and_rethrow();
}

void test_i2p_sam_session_reuse() {
    LoopbackListener listener = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner control =
            accept_one_or_throw(listener.socket.get(), "SAM control");
        expect_sam_hello_or_throw(control.get(), "SAM control hello");
        const std::string session_id = expect_sam_session_create_or_throw(
            control.get(), "SAM session create");

        DescriptorOwner first =
            accept_one_or_throw(listener.socket.get(), "SAM first stream");
        expect_sam_stream_connect_or_throw(
            first.get(), session_id, "SAM first stream");
        exchange_marker_server_or_throw(
            first.get(), 0x61U, 0x62U, "SAM first stream");

        DescriptorOwner second =
            accept_one_or_throw(listener.socket.get(), "SAM second stream");
        expect_sam_stream_connect_or_throw(
            second.get(), session_id, "SAM second stream");
        exchange_marker_server_or_throw(
            second.get(), 0x63U, 0x64U, "SAM second stream");
    });

    anonsync::SyncReplicaStreamConnector connector(
        i2p_route_for(listener), "I2P SAM connector");
    auto first = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        first.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::Connected,
        "first SAM stream did not connect");
    require(first.report.control_session_created,
            "first SAM stream did not create a control session");
    require(!first.report.control_session_reused,
            "first SAM stream falsely reported control reuse");
    require(first.report.numeric_connect_attempts == 2U,
            "first SAM stream did not account for control plus data connects");
    require(first.report.sam_result == anonsync::SyncReplicaI2pSamResult::Ok,
            "first SAM stream did not preserve SAM OK status");
    require(first.stream.has_value(),
            "first SAM stream omitted stream authority");
    exchange_marker_client_or_throw(
        *first.stream, 0x61U, 0x62U, "first I2P client stream");
    first.stream.reset();

    auto second = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        second.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::Connected,
        "second SAM stream did not connect");
    require(!second.report.control_session_created,
            "second SAM stream created a duplicate control session");
    require(second.report.control_session_reused,
            "second SAM stream did not reuse the retained control session");
    require(!second.report.control_session_stale_detected,
            "healthy SAM control was reported stale");
    require(second.report.numeric_connect_attempts == 1U,
            "reused SAM stream attempted more than one numeric connect");
    require(second.stream.has_value(),
            "second SAM stream omitted stream authority");
    exchange_marker_client_or_throw(
        *second.stream, 0x63U, 0x64U, "second I2P client stream");
    server.join_and_rethrow();
}

void test_i2p_stale_control_is_recovered_between_sessions() {
    LoopbackListener listener = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner control =
            accept_one_or_throw(listener.socket.get(), "stale SAM control");
        expect_sam_hello_or_throw(control.get(), "stale SAM control hello");
        const std::string session_id = expect_sam_session_create_or_throw(
            control.get(), "stale SAM session create");
        DescriptorOwner first =
            accept_one_or_throw(listener.socket.get(), "stale SAM first data");
        expect_sam_stream_connect_or_throw(
            first.get(), session_id, "stale SAM first data");
        const auto marker =
            read_exact_or_throw(first.get(), 1U, "stale SAM first marker");
        require(marker[0U] == 0x71U, "stale SAM first marker changed");

        // The SAM specification binds session lifetime to this control socket.
        // A close before a write on another TCP connection is not itself an
        // ordered peer observation. Prove the connector kernel acknowledged the
        // control FIN before releasing the data marker that permits its next
        // session attempt.
        shutdown_write_and_wait_for_fin_ack_or_throw(
            control.get(), "stale SAM control close");
        write_all_or_throw(
            first.get(), std::array<unsigned char, 1U>{0x72U},
            "stale SAM first response");

        DescriptorOwner replacement_control = accept_one_or_throw(
            listener.socket.get(), "replacement SAM control");
        expect_sam_hello_or_throw(
            replacement_control.get(), "replacement SAM control hello");
        const std::string replacement_session_id =
            expect_sam_session_create_or_throw(
            replacement_control.get(), "replacement SAM session create");
        require(replacement_session_id == session_id,
                "replacement control changed the connector runtime session ID");
        DescriptorOwner second = accept_one_or_throw(
            listener.socket.get(), "replacement SAM data");
        expect_sam_stream_connect_or_throw(
            second.get(), session_id, "replacement SAM data");
        exchange_marker_server_or_throw(
            second.get(), 0x73U, 0x74U, "replacement SAM data");
    });

    anonsync::SyncReplicaStreamConnector connector(
        i2p_route_for(listener), "recovering I2P SAM connector");
    auto first = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(first.stream.has_value(),
            "stale-control first stream did not connect");
    exchange_marker_client_or_throw(
        *first.stream, 0x71U, 0x72U, "stale-control first client");
    first.stream.reset();

    auto second = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        second.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::Connected,
        "replacement SAM stream did not connect");
    require(second.report.control_session_stale_detected,
            "dead retained SAM control was not detected");
    require(second.report.control_session_created,
            "dead retained SAM control was not replaced");
    require(second.report.control_session_recovered,
            "replacement SAM session was not reported as recovery");
    require(!second.report.control_session_reused,
            "dead SAM control was falsely reported reused");
    require(second.report.numeric_connect_attempts == 2U,
            "SAM recovery did not account for replacement control and data");
    require(second.stream.has_value(),
            "replacement SAM stream omitted authority");
    exchange_marker_client_or_throw(
        *second.stream, 0x73U, 0x74U, "replacement I2P client");
    server.join_and_rethrow();
}

void test_i2p_native_forwarder_publishes_loopback_tls_listener() {
    LoopbackListener sam_bridge = make_loopback_listener();
    LoopbackListener local_receiver = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner control = accept_one_or_throw(
            sam_bridge.socket.get(), "I2P forward control");
        expect_sam_hello_or_throw(control.get(), "I2P forward control hello");
        const std::string session_id =
            expect_persisted_sam_session_create_or_throw(
            control.get(), "I2P forward session create");

        DescriptorOwner forward = accept_one_or_throw(
            sam_bridge.socket.get(), "I2P forwarding socket");
        expect_sam_stream_forward_or_throw(
            forward.get(), local_receiver, session_id,
            "I2P STREAM FORWARD");

        // Model the bridge opening one SILENT forwarding child to the existing
        // TLS listener. No I2P destination preamble is injected.
        DescriptorOwner child = connect_loopback_or_throw(
            local_receiver.port, "I2P forwarded child");
        write_all_or_throw(
            child.get(), std::array<unsigned char, 1U>{0x91U},
            "I2P forwarded child request");
        const auto response = read_exact_or_throw(
            child.get(), 1U, "I2P forwarded child response");
        require(response[0U] == 0x92U,
                "I2P forwarded child response changed");
        expect_peer_close_or_throw(
            forward.get(), "I2P forwarding capability close");
    });

    {
        anonsync::SyncReplicaI2pSamForwarder forwarder(
            anonsync::SyncReplicaI2pSamForwardRoute{
                endpoint_for(sam_bridge), std::string(kSamSessionId),
                std::string(kPersistedSamDestination),
                endpoint_for(local_receiver), 2U, 2U},
            "native inbound I2P forwarder");
        const auto report =
            forwarder.start_until_or_throw(Clock::now() + kIoTimeout);
        require(
            report.disposition ==
                anonsync::SyncReplicaStreamConnectDisposition::Connected,
            "native I2P forwarder did not connect");
        require(
            report.terminal_stage ==
                anonsync::SyncReplicaStreamRouteStage::Complete,
            "native I2P forwarder did not reach complete stage");
        require(report.route_negotiated,
                "native I2P forwarder omitted route negotiation evidence");
        require(report.control_session_created,
                "native I2P forwarder omitted SAM session creation evidence");
        require(report.data_socket_created &&
                    report.data_socket_policy_verified,
                "native I2P forwarder omitted forwarding-socket evidence");
        require(report.numeric_connect_attempts == 2U,
                "native I2P forwarder did not account for two SAM sockets");
        require(report.sam_result == anonsync::SyncReplicaI2pSamResult::Ok,
                "native I2P forwarder did not preserve SAM OK status");
        require(report.route_bytes_written > 0U &&
                    report.route_bytes_received > 0U,
                "native I2P forwarder omitted route byte accounting");
        require(forwarder.active(),
                "native I2P forwarder was inactive after setup");
        forwarder.require_active_or_throw("live native I2P forwarder");

        DescriptorOwner child = accept_one_or_throw(
            local_receiver.socket.get(), "local receiver forwarded child");
        exchange_marker_server_or_throw(
            child.get(), 0x91U, 0x92U, "local receiver forwarded child");
        require_throws(
            [&] {
                (void)forwarder.start_until_or_throw(
                    Clock::now() + kIoTimeout);
            },
            "native I2P forwarder allowed a second setup attempt");
    }
    server.join_and_rethrow();
}

void test_i2p_native_forwarder_expired_setup_is_terminal() {
    anonsync::SyncReplicaI2pSamForwarder forwarder(
        anonsync::SyncReplicaI2pSamForwardRoute{
            {"127.0.0.1", 1U}, std::string(kSamSessionId),
            std::string(kPersistedSamDestination), {"127.0.0.1", 4433U},
            2U, 2U},
        "expired native inbound I2P forwarder");
    const auto report =
        forwarder.start_until_or_throw(Clock::now() - 1ms);
    require(
        report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::DeadlineExpired,
        "expired native I2P forwarder did not preserve deadline disposition");
    require(report.numeric_connect_attempts == 0U,
            "expired native I2P forwarder attempted a numeric connect");
    require(!forwarder.active(),
            "expired native I2P forwarder retained authority");
    require_throws(
        [&] {
            (void)forwarder.start_until_or_throw(Clock::now() + kIoTimeout);
        },
        "expired native I2P forwarder allowed a hidden retry");
}

void test_i2p_native_acceptor_hands_off_sam32_stream() {
    LoopbackListener sam_bridge = make_loopback_listener();
    const std::string peer_destination = full_i2p_peer_destination();
    ServerThread server([&] {
        DescriptorOwner control = accept_one_or_throw(
            sam_bridge.socket.get(), "I2P accept control");
        expect_sam_hello_or_throw(
            control.get(), "I2P accept control hello", "3.2");
        const std::string session_id =
            expect_persisted_sam_session_create_or_throw(
                control.get(), "I2P accept session create");

        DescriptorOwner accepted = accept_one_or_throw(
            sam_bridge.socket.get(), "I2P accept socket");
        expect_sam_stream_accept_or_throw(
            accepted.get(), session_id, "I2P STREAM ACCEPT");
        write_all_or_throw(
            accepted.get(),
            peer_destination + " FROM_PORT=12345 TO_PORT=443\n",
            "I2P SAM 3.2 peer line");
        exchange_marker_server_or_throw(
            accepted.get(), 0xa1U, 0xa2U, "I2P accepted application stream");
    });

    {
        anonsync::SyncReplicaI2pSamAcceptor acceptor(
            anonsync::SyncReplicaI2pSamAcceptRoute{
                endpoint_for(sam_bridge), std::string(kSamSessionId),
                std::string(kPersistedSamDestination), 2U, 2U},
            "native inbound I2P acceptor");
        const auto setup =
            acceptor.start_until_or_throw(Clock::now() + kIoTimeout);
        require(
            setup.disposition ==
                anonsync::SyncReplicaStreamConnectDisposition::Connected,
            "native I2P acceptor did not establish its retained session");
        require(setup.route_negotiated && setup.control_session_created,
                "native I2P acceptor omitted setup evidence");
        require(acceptor.active() && acceptor.accept_armed(),
                "native I2P acceptor did not retain an armed accept");

        auto outcome = acceptor.accept_until_or_throw(
            Clock::now() + kIoTimeout, Clock::now() + kIoTimeout);
        require(
            outcome.report.disposition ==
                anonsync::SyncReplicaStreamConnectDisposition::Connected,
            "native I2P acceptor did not hand off the application stream");
        require(
            outcome.report.terminal_stage ==
                anonsync::SyncReplicaStreamRouteStage::Complete,
            "native I2P acceptor did not reach the complete stage");
        require(outcome.report.sam_peer_destination == peer_destination,
                "SAM 3.2 peer metadata leaked into the peer destination");
        require(outcome.stream.has_value(),
                "native I2P acceptor omitted stream authority");
        exchange_marker_client_or_throw(
            *outcome.stream, 0xa1U, 0xa2U,
            "native I2P accepted application stream");
    }
    server.join_and_rethrow();
}

void test_i2p_native_acceptor_preserves_post_ok_error() {
    LoopbackListener sam_bridge = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner control = accept_one_or_throw(
            sam_bridge.socket.get(), "I2P failed-accept control");
        expect_sam_hello_or_throw(
            control.get(), "I2P failed-accept control hello", "3.2");
        const std::string session_id =
            expect_persisted_sam_session_create_or_throw(
                control.get(), "I2P failed-accept session create");
        DescriptorOwner accepted = accept_one_or_throw(
            sam_bridge.socket.get(), "I2P failed-accept socket");
        expect_sam_stream_accept_or_throw(
            accepted.get(), session_id, "I2P failed STREAM ACCEPT");
        write_all_or_throw(
            accepted.get(),
            "STREAM STATUS RESULT=I2P_ERROR MESSAGE=peer-failed\n",
            "I2P post-OK accept error");
        expect_peer_close_or_throw(
            control.get(), "post-OK-error SAM control close");
    });

    {
        anonsync::SyncReplicaI2pSamAcceptor acceptor(
            anonsync::SyncReplicaI2pSamAcceptRoute{
                endpoint_for(sam_bridge), std::string(kSamSessionId),
                std::string(kPersistedSamDestination), 2U, 2U},
            "post-OK-error I2P acceptor");
        const auto setup =
            acceptor.start_until_or_throw(Clock::now() + kIoTimeout);
        require(
            setup.disposition ==
                anonsync::SyncReplicaStreamConnectDisposition::Connected,
            "post-OK-error I2P acceptor setup failed");
        auto outcome = acceptor.accept_until_or_throw(
            Clock::now() + kIoTimeout, Clock::now() + kIoTimeout);
        require(
            outcome.report.disposition ==
                anonsync::SyncReplicaStreamConnectDisposition::RouteRejected,
            "post-OK SAM accept failure was not typed as route rejection");
        require(
            outcome.report.terminal_stage ==
                anonsync::SyncReplicaStreamRouteStage::I2pStreamPeerDestination,
            "post-OK SAM accept failure reported the wrong stage");
        require(
            outcome.report.sam_result ==
                anonsync::SyncReplicaI2pSamResult::I2pError,
            "post-OK SAM accept failure lost its SAM result");
        require(!outcome.stream.has_value(),
                "post-OK SAM accept failure returned stream authority");
    }
    server.join_and_rethrow();
}

void test_i2p_invalid_id_invalidates_future_reuse_without_hidden_retry() {
    LoopbackListener listener = make_loopback_listener();
    ServerThread server([&] {
        DescriptorOwner control =
            accept_one_or_throw(listener.socket.get(), "invalid-ID control");
        expect_sam_hello_or_throw(control.get(), "invalid-ID control hello");
        const std::string session_id = expect_sam_session_create_or_throw(
            control.get(), "invalid-ID session create");
        DescriptorOwner data =
            accept_one_or_throw(listener.socket.get(), "invalid-ID data");
        expect_sam_hello_or_throw(data.get(), "invalid-ID stream hello");
        (void)read_line_or_throw(data.get(), "invalid-ID connect command");
        write_all_or_throw(
            data.get(), "STREAM STATUS RESULT=INVALID_ID\n",
            "invalid-ID response");

        // A second caller-authorized session creates a replacement. The first
        // connect must not hide an immediate retry after INVALID_ID.
        DescriptorOwner replacement_control = accept_one_or_throw(
            listener.socket.get(), "post-invalid-ID control");
        expect_sam_hello_or_throw(
            replacement_control.get(), "post-invalid-ID control hello");
        const std::string replacement_session_id =
            expect_sam_session_create_or_throw(
            replacement_control.get(), "post-invalid-ID session create");
        require(replacement_session_id == session_id,
                "post-invalid-ID control changed the connector runtime session ID");
        DescriptorOwner replacement_data = accept_one_or_throw(
            listener.socket.get(), "post-invalid-ID data");
        expect_sam_stream_connect_or_throw(
            replacement_data.get(), session_id, "post-invalid-ID data");
        exchange_marker_server_or_throw(
            replacement_data.get(), 0x81U, 0x82U, "post-invalid-ID data");
    });

    anonsync::SyncReplicaStreamConnector connector(
        i2p_route_for(listener), "invalid-ID I2P connector");
    auto rejected = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(
        rejected.report.disposition ==
            anonsync::SyncReplicaStreamConnectDisposition::RouteRejected,
        "SAM INVALID_ID was not typed as route rejection");
    require(
        rejected.report.terminal_stage ==
            anonsync::SyncReplicaStreamRouteStage::I2pStreamConnect,
        "SAM INVALID_ID reported the wrong stage");
    require(
        rejected.report.sam_result ==
            anonsync::SyncReplicaI2pSamResult::InvalidId,
        "SAM INVALID_ID result was not preserved");
    require(rejected.report.control_session_stale_detected,
            "SAM INVALID_ID did not invalidate retained session state");
    require(rejected.report.numeric_connect_attempts == 2U,
            "SAM INVALID_ID path performed a hidden numeric retry");
    require(!rejected.stream.has_value(),
            "SAM INVALID_ID returned stream authority");

    auto recovered = connector.connect_until_or_throw(Clock::now() + kIoTimeout);
    require(recovered.report.control_session_created,
            "post-INVALID_ID session did not recreate control authority");
    require(!recovered.report.control_session_reused,
            "post-INVALID_ID session reused invalid control authority");
    require(recovered.stream.has_value(),
            "post-INVALID_ID session did not connect");
    exchange_marker_client_or_throw(
        *recovered.stream, 0x81U, 0x82U, "post-invalid-ID client");
    server.join_and_rethrow();
}
#endif

}  // namespace

int main() {
    try {
#ifdef __linux__
        test_route_validation_and_tor_checksum();
        test_deadline_precedes_socket_authority();
        test_direct_stream();
        test_tor_socks5_stream_and_isolation();
        test_tor_route_rejection_is_typed();
        test_i2p_runtime_session_ids_are_owner_unique();
        test_i2p_persisted_destination_omits_transient_signature_option();
        test_i2p_sam_session_reuse();
        test_i2p_stale_control_is_recovered_between_sessions();
        test_i2p_native_forwarder_publishes_loopback_tls_listener();
        test_i2p_native_forwarder_expired_setup_is_terminal();
        test_i2p_native_acceptor_hands_off_sam32_stream();
        test_i2p_native_acceptor_preserves_post_ok_error();
        test_i2p_invalid_id_invalidates_future_reuse_without_hidden_retry();
#else
        require_throws(
            [] {
                anonsync::SyncReplicaStreamConnector connector(
                    anonsync::SyncReplicaDirectTcpRoute{{"127.0.0.1", 1U}},
                    "non-Linux connector");
                (void)connector.connect_until_or_throw(Clock::now() + 1s);
            },
            "non-Linux connector did not fail closed");
#endif
        std::cout << "sync replica stream connector tests passed: " << checks
                  << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica stream connector test failure after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
