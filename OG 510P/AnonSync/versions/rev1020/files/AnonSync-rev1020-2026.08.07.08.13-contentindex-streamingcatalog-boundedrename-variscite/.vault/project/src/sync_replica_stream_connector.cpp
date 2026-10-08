#include "sync_replica_stream_connector.hpp"

#include "sync_stream_socket_deadline_poll.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
#include <optional>
#include <span>
#include <stop_token>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

#include <openssl/evp.h>
#include <openssl/rand.h>

#ifdef __linux__
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

constexpr std::string_view kTorSocksFormatZeroUsername = "<torS0X>0";
constexpr std::size_t kMaximumSamLineBytes = 4096U;
constexpr std::size_t kMaximumI2pPeerDestinationBytes = 2048U;
constexpr std::size_t kMaximumI2pSessionDestinationBytes = 8192U;
constexpr std::size_t kMaximumI2pSamSessionIdBytes = 64U;
constexpr std::size_t kI2pSamRuntimeRandomBytes = 8U;
constexpr std::size_t kI2pSamRuntimeSequenceBytes = 8U;
constexpr std::size_t kI2pSamRuntimeSuffixHexBytes =
    (kI2pSamRuntimeRandomBytes + kI2pSamRuntimeSequenceBytes) * 2U;
constexpr std::uint32_t kMaximumI2pTunnelQuantity = 16U;
constexpr std::size_t kTorV3OnionLabelBytes = 56U;
constexpr std::size_t kTorV3DecodedBytes = 35U;
constexpr std::size_t kTorV3PublicKeyBytes = 32U;
constexpr std::string_view kTorV3ChecksumDomain = ".onion checksum";
constexpr unsigned char kTorV3Version = 0x03U;

static_assert(
    kI2pSamRuntimeSuffixHexBytes + 2U <=
    kMaximumI2pSamSessionIdBytes);

std::atomic<std::uint64_t> next_i2p_sam_session_sequence{0U};

[[nodiscard]] std::uint64_t claim_i2p_sam_session_sequence_or_throw(
    std::string_view label) {
    std::uint64_t observed =
        next_i2p_sam_session_sequence.load(std::memory_order_relaxed);
    for (;;) {
        if (observed == std::numeric_limits<std::uint64_t>::max()) {
            throw std::runtime_error(
                std::string(label) +
                " exhausted process-local SAM session identity space");
        }
        if (next_i2p_sam_session_sequence.compare_exchange_weak(
                observed, observed + 1U, std::memory_order_relaxed,
                std::memory_order_relaxed)) {
            return observed;
        }
    }
}

[[nodiscard]] std::string runtime_i2p_sam_session_id_or_throw(
    std::string_view configured_base,
    std::string_view label) {
    // SAM session IDs are global within one bridge. A literal configured ID is
    // therefore unsafe once one AnonSync process owns several shares, or when
    // several AnonSync processes use the same router. Keep a recognizable,
    // bounded prefix while adding per-owner entropy and a process-local
    // sequence. The sequence gives deterministic uniqueness inside this
    // process; RAND_bytes keeps independent processes from sharing a suffix.
    std::array<unsigned char, kI2pSamRuntimeRandomBytes> random{};
    if (RAND_bytes(random.data(), static_cast<int>(random.size())) != 1) {
        throw std::runtime_error(
            std::string(label) +
            " could not generate a runtime SAM session identity");
    }
    const std::uint64_t sequence =
        claim_i2p_sam_session_sequence_or_throw(label);

    constexpr std::string_view hex = "0123456789abcdef";
    constexpr std::size_t maximum_base_bytes =
        kMaximumI2pSamSessionIdBytes - 1U -
        kI2pSamRuntimeSuffixHexBytes;
    std::string runtime_id(configured_base.substr(0U, maximum_base_bytes));
    runtime_id.push_back('.');
    runtime_id.reserve(kMaximumI2pSamSessionIdBytes);
    for (const unsigned char byte : random) {
        runtime_id.push_back(hex[byte >> 4U]);
        runtime_id.push_back(hex[byte & 0x0fU]);
    }
    for (std::size_t index = 0U;
         index < kI2pSamRuntimeSequenceBytes; ++index) {
        const unsigned int shift = static_cast<unsigned int>(
            (kI2pSamRuntimeSequenceBytes - 1U - index) * 8U);
        const auto byte = static_cast<unsigned char>(
            (sequence >> shift) & 0xffU);
        runtime_id.push_back(hex[byte >> 4U]);
        runtime_id.push_back(hex[byte & 0x0fU]);
    }
    if (runtime_id.empty() ||
        runtime_id.size() > kMaximumI2pSamSessionIdBytes) {
        throw std::logic_error(
            std::string(label) +
            " produced an invalid runtime SAM session identity");
    }
    return runtime_id;
}

#ifdef __linux__
struct ReleasedSocket final {
    int descriptor = -1;
    SyncSocketLifetimeIdentity identity;
};

class SocketOwner final {
public:
    SocketOwner() noexcept = default;
    SocketOwner(int descriptor, SyncSocketLifetimeIdentity identity) noexcept
        : descriptor_(descriptor), identity_(std::move(identity)) {}
    SocketOwner(const SocketOwner&) = delete;
    SocketOwner& operator=(const SocketOwner&) = delete;
    SocketOwner(SocketOwner&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)),
          identity_(std::move(other.identity_)) {
        other.identity_.reset();
    }
    SocketOwner& operator=(SocketOwner&& other) noexcept {
        if (this != &other) {
            close_noexcept();
            descriptor_ = std::exchange(other.descriptor_, -1);
            identity_ = std::move(other.identity_);
            other.identity_.reset();
        }
        return *this;
    }
    ~SocketOwner() noexcept { close_noexcept(); }

    [[nodiscard]] int descriptor() const noexcept { return descriptor_; }
    [[nodiscard]] const SyncSocketLifetimeIdentity& identity_or_throw(
        std::string_view label) const {
        if (descriptor_ < 0 || !identity_.has_value()) {
            throw std::logic_error(
                std::string(label) + " socket ownership is absent");
        }
        return *identity_;
    }

    [[nodiscard]] ReleasedSocket release_or_throw(
        std::string_view label) {
        if (descriptor_ < 0 || !identity_.has_value()) {
            throw std::logic_error(
                std::string(label) + " connected socket ownership is absent");
        }
        ReleasedSocket released{
            std::exchange(descriptor_, -1), std::move(*identity_)};
        identity_.reset();
        return released;
    }

private:
    void close_noexcept() noexcept {
        if (descriptor_ >= 0) {
            const int descriptor = std::exchange(descriptor_, -1);
            identity_.reset();
            // The descriptor lifetime ends after one close call. Retrying an
            // EINTR result can close a different descriptor after reuse.
            (void)::close(descriptor);
        }
    }

    int descriptor_ = -1;
    std::optional<SyncSocketLifetimeIdentity> identity_;
};

struct ParsedNumericEndpoint final {
    int family = AF_UNSPEC;
    sockaddr_storage address{};
    socklen_t address_bytes = 0U;
};

[[nodiscard]] bool parsed_numeric_endpoint_is_loopback(
    const ParsedNumericEndpoint& endpoint) noexcept {
    if (endpoint.family == AF_INET &&
        endpoint.address_bytes == sizeof(sockaddr_in)) {
        sockaddr_in address{};
        std::memcpy(&address, &endpoint.address, sizeof(address));
        return (ntohl(address.sin_addr.s_addr) & 0xff000000U) ==
            0x7f000000U;
    }
    if (endpoint.family == AF_INET6 &&
        endpoint.address_bytes == sizeof(sockaddr_in6)) {
        sockaddr_in6 address{};
        std::memcpy(&address, &endpoint.address, sizeof(address));
        return IN6_IS_ADDR_LOOPBACK(&address.sin6_addr) != 0;
    }
    return false;
}

[[nodiscard]] ParsedNumericEndpoint parse_numeric_endpoint_or_throw(
    const SyncReplicaNumericStreamEndpoint& endpoint,
    std::string_view label) {
    if (endpoint.numeric_address.empty()) {
        throw std::invalid_argument(
            std::string(label) + " numeric address is empty");
    }
    if (endpoint.port == 0U) {
        throw std::invalid_argument(
            std::string(label) + " port must be nonzero");
    }

    ParsedNumericEndpoint parsed;
    sockaddr_in ipv4{};
    ipv4.sin_family = AF_INET;
    ipv4.sin_port = htons(endpoint.port);
    errno = 0;
    const int ipv4_result = ::inet_pton(
        AF_INET, endpoint.numeric_address.c_str(), &ipv4.sin_addr);
    if (ipv4_result == 1) {
        parsed.family = AF_INET;
        std::memcpy(&parsed.address, &ipv4, sizeof(ipv4));
        parsed.address_bytes = sizeof(ipv4);
        return parsed;
    }
    if (ipv4_result < 0) {
        throw std::runtime_error(
            std::string(label) + " could not parse IPv4 address (errno " +
            std::to_string(errno) + ")");
    }

    sockaddr_in6 ipv6{};
    ipv6.sin6_family = AF_INET6;
    ipv6.sin6_port = htons(endpoint.port);
    errno = 0;
    const int ipv6_result = ::inet_pton(
        AF_INET6, endpoint.numeric_address.c_str(), &ipv6.sin6_addr);
    if (ipv6_result == 1) {
        parsed.family = AF_INET6;
        std::memcpy(&parsed.address, &ipv6, sizeof(ipv6));
        parsed.address_bytes = sizeof(ipv6);
        return parsed;
    }
    if (ipv6_result < 0) {
        throw std::runtime_error(
            std::string(label) + " could not parse IPv6 address (errno " +
            std::to_string(errno) + ")");
    }

    throw std::invalid_argument(
        std::string(label) +
        " is not a numeric IPv4 or unscoped IPv6 endpoint");
}

[[nodiscard]] bool connect_in_progress_error(int error) noexcept {
    return error == EINPROGRESS || error == EALREADY ||
           error == EWOULDBLOCK || error == EINTR;
}

enum class RoutePollDisposition {
    Ready,
    DeadlineExpired,
    Cancelled,
};

// Long SAM SESSION CREATE waits are legitimate while I2P builds tunnels. Poll
// in short monotonic slices only when a stop token exists so service shutdown
// can cancel the exact attempt without imposing short protocol timeouts or
// abandoning and retrying a still-live tunnel build during ordinary operation.
[[nodiscard]] RoutePollDisposition poll_route_socket_until_or_throw(
    const SyncSocketLifetimeIdentity& identity,
    SyncStreamSocketPollReadiness readiness,
    std::chrono::steady_clock::time_point deadline,
    std::stop_token cancellation,
    std::string_view label) {
    if (!cancellation.stop_possible()) {
        const auto result = poll_sync_stream_socket_until_or_throw(
            identity, readiness, deadline, label);
        return result == SyncStreamSocketDeadlinePollResult::Ready
            ? RoutePollDisposition::Ready
            : RoutePollDisposition::DeadlineExpired;
    }
    constexpr auto kCancellationPollSlice = std::chrono::milliseconds(100);
    for (;;) {
        if (cancellation.stop_requested()) {
            return RoutePollDisposition::Cancelled;
        }
        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) {
            return RoutePollDisposition::DeadlineExpired;
        }
        const auto slice_deadline = std::min(deadline, now + kCancellationPollSlice);
        const auto result = poll_sync_stream_socket_until_or_throw(
            identity, readiness, slice_deadline, label);
        if (result == SyncStreamSocketDeadlinePollResult::Ready) {
            return cancellation.stop_requested()
                ? RoutePollDisposition::Cancelled
                : RoutePollDisposition::Ready;
        }
    }
}

struct NumericConnectOutcome final {
    SyncReplicaStreamConnectDisposition disposition =
        SyncReplicaStreamConnectDisposition::NumericConnectFailed;
    bool socket_created = false;
    bool socket_policy_verified = false;
    std::uint64_t attempts = 0U;
    std::optional<int> error;
    std::optional<SocketOwner> socket;
};

[[nodiscard]] NumericConnectOutcome connect_numeric_until_or_throw(
    const SyncReplicaNumericStreamEndpoint& endpoint,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label,
    std::stop_token cancellation = {}) {
    NumericConnectOutcome outcome;
    const ParsedNumericEndpoint parsed =
        parse_numeric_endpoint_or_throw(endpoint, label);
    if (cancellation.stop_requested()) {
        outcome.disposition = SyncReplicaStreamConnectDisposition::Cancelled;
        return outcome;
    }
    if (std::chrono::steady_clock::now() >= deadline) {
        outcome.disposition =
            SyncReplicaStreamConnectDisposition::DeadlineExpired;
        return outcome;
    }

    errno = 0;
    const int raw_socket = ::socket(
        parsed.family, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (raw_socket < 0) {
        throw std::runtime_error(
            std::string(label) + " could not create stream socket (errno " +
            std::to_string(errno) + ")");
    }
    outcome.socket_created = true;
    SyncSocketLifetimeIdentity identity =
        observe_sync_stream_socket_lifetime_or_throw(
            raw_socket, std::string(label) + " socket");
    SocketOwner socket(raw_socket, identity);
    require_sync_stream_socket_nonblocking_or_throw(
        identity, std::string(label) + " socket");
    require_sync_stream_socket_close_on_exec_or_throw(
        identity, std::string(label) + " socket");
    outcome.socket_policy_verified = true;

    ++outcome.attempts;
    errno = 0;
    const int connected = ::connect(
        raw_socket,
        reinterpret_cast<const sockaddr*>(&parsed.address),
        parsed.address_bytes);
    const int connect_errno = errno;
    if (connected == 0 ||
        (connected < 0 && connect_errno == EISCONN)) {
        require_sync_stream_socket_nonblocking_or_throw(identity, label);
        require_sync_stream_socket_close_on_exec_or_throw(identity, label);
        outcome.disposition = SyncReplicaStreamConnectDisposition::Connected;
        outcome.socket.emplace(std::move(socket));
        return outcome;
    }
    if (!connect_in_progress_error(connect_errno)) {
        outcome.disposition =
            SyncReplicaStreamConnectDisposition::NumericConnectFailed;
        outcome.error = connect_errno;
        return outcome;
    }

    const auto readiness = poll_route_socket_until_or_throw(
        identity, SyncStreamSocketPollReadiness::Writable, deadline,
        cancellation, std::string(label) + " readiness");
    if (readiness == RoutePollDisposition::Cancelled) {
        outcome.disposition = SyncReplicaStreamConnectDisposition::Cancelled;
        return outcome;
    }
    if (readiness == RoutePollDisposition::DeadlineExpired) {
        outcome.disposition =
            SyncReplicaStreamConnectDisposition::DeadlineExpired;
        return outcome;
    }

    int socket_error = 0;
    socklen_t socket_error_bytes = sizeof(socket_error);
    errno = 0;
    if (::getsockopt(
            raw_socket, SOL_SOCKET, SO_ERROR,
            &socket_error, &socket_error_bytes) != 0 ||
        socket_error_bytes != sizeof(socket_error)) {
        throw std::runtime_error(
            std::string(label) + " could not observe SO_ERROR (errno " +
            std::to_string(errno) + ")");
    }
    require_sync_stream_socket_nonblocking_or_throw(identity, label);
    require_sync_stream_socket_close_on_exec_or_throw(identity, label);
    if (socket_error == 0 || socket_error == EISCONN) {
        outcome.disposition = SyncReplicaStreamConnectDisposition::Connected;
        outcome.socket.emplace(std::move(socket));
    } else {
        outcome.disposition =
            SyncReplicaStreamConnectDisposition::NumericConnectFailed;
        outcome.error = socket_error;
    }
    return outcome;
}

enum class RouteIoDisposition {
    Complete,
    DeadlineExpired,
    PeerClosed,
    Cancelled,
};

[[nodiscard]] bool terminal_socket_error(int error) noexcept {
    return error == ECONNRESET || error == ECONNABORTED || error == EPIPE ||
           error == ENOTCONN || error == ETIMEDOUT;
}

// A SAM STREAM session exists only while its control socket exists. Before a
// later batch delivery reuses the session, observe the retained socket without
// consuming protocol bytes. SAM 3.1 has no unsolicited control traffic after
// SESSION STATUS; queued bytes therefore make this specific retained session
// unsafe to reuse just as surely as EOF does.
[[nodiscard]] bool sam_control_session_is_reusable_or_throw(
    const SocketOwner& socket,
    std::string_view label) {
    const auto& identity = socket.identity_or_throw(label);
    require_sync_stream_socket_nonblocking_or_throw(identity, label);
    require_sync_stream_socket_close_on_exec_or_throw(identity, label);
    for (;;) {
        std::array<unsigned char, 1U> byte{};
        errno = 0;
        const ssize_t observed = ::recv(
            socket.descriptor(), byte.data(), byte.size(),
            MSG_PEEK | MSG_DONTWAIT);
        const int receive_errno = errno;
        if (observed == 0) return false;
        if (observed > 0) return false;
        if (receive_errno == EINTR) continue;
        if (receive_errno == EAGAIN || receive_errno == EWOULDBLOCK) {
            return true;
        }
        if (terminal_socket_error(receive_errno)) return false;
        throw std::runtime_error(
            std::string(label) +
            " could not inspect retained SAM control socket (errno " +
            std::to_string(receive_errno) + ")");
    }
}

// A pending STREAM ACCEPT socket legitimately becomes readable when a remote
// destination or the first application bytes are ready. Readability is liveness
// here, unlike on the quiescent control socket; only EOF or a terminal socket
// error proves that the armed accept was lost.
[[nodiscard]] bool sam_pending_accept_is_live_or_throw(
    const SocketOwner& socket,
    std::string_view label) {
    const auto& identity = socket.identity_or_throw(label);
    require_sync_stream_socket_nonblocking_or_throw(identity, label);
    require_sync_stream_socket_close_on_exec_or_throw(identity, label);
    for (;;) {
        std::array<unsigned char, 1U> byte{};
        errno = 0;
        const ssize_t observed = ::recv(
            socket.descriptor(), byte.data(), byte.size(),
            MSG_PEEK | MSG_DONTWAIT);
        const int receive_errno = errno;
        if (observed > 0) return true;
        if (observed == 0) return false;
        if (receive_errno == EINTR) continue;
        if (receive_errno == EAGAIN || receive_errno == EWOULDBLOCK) {
            return true;
        }
        if (terminal_socket_error(receive_errno)) return false;
        throw std::runtime_error(
            std::string(label) +
            " could not inspect pending SAM accept socket (errno " +
            std::to_string(receive_errno) + ")");
    }
}

[[nodiscard]] RouteIoDisposition write_all_until_or_throw(
    const SocketOwner& socket,
    std::span<const unsigned char> bytes,
    std::chrono::steady_clock::time_point deadline,
    std::uint64_t& written_total,
    std::string_view label,
    std::stop_token cancellation = {}) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        if (cancellation.stop_requested()) {
            return RouteIoDisposition::Cancelled;
        }
        const auto& identity = socket.identity_or_throw(label);
        require_sync_stream_socket_nonblocking_or_throw(identity, label);
        require_sync_stream_socket_close_on_exec_or_throw(identity, label);
        if (std::chrono::steady_clock::now() >= deadline) {
            return RouteIoDisposition::DeadlineExpired;
        }

        errno = 0;
        const ssize_t written = ::send(
            socket.descriptor(), bytes.data() + offset,
            bytes.size() - offset, MSG_NOSIGNAL);
        const int send_errno = errno;
        if (written > 0) {
            const auto count = static_cast<std::size_t>(written);
            offset += count;
            written_total += static_cast<std::uint64_t>(count);
            continue;
        }
        if (written == 0) return RouteIoDisposition::PeerClosed;
        if (send_errno == EINTR) continue;
        if (send_errno == EAGAIN || send_errno == EWOULDBLOCK) {
            const auto readiness = poll_route_socket_until_or_throw(
                identity, SyncStreamSocketPollReadiness::Writable, deadline,
                cancellation, std::string(label) + " write readiness");
            if (readiness == RoutePollDisposition::Cancelled) {
                return RouteIoDisposition::Cancelled;
            }
            if (readiness == RoutePollDisposition::DeadlineExpired) {
                return RouteIoDisposition::DeadlineExpired;
            }
            continue;
        }
        if (terminal_socket_error(send_errno)) {
            return RouteIoDisposition::PeerClosed;
        }
        throw std::runtime_error(
            std::string(label) + " send failed (errno " +
            std::to_string(send_errno) + ")");
    }
    return RouteIoDisposition::Complete;
}

[[nodiscard]] RouteIoDisposition read_exact_until_or_throw(
    const SocketOwner& socket,
    std::span<unsigned char> bytes,
    std::chrono::steady_clock::time_point deadline,
    std::uint64_t& received_total,
    std::string_view label,
    std::stop_token cancellation = {}) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        if (cancellation.stop_requested()) {
            return RouteIoDisposition::Cancelled;
        }
        const auto& identity = socket.identity_or_throw(label);
        require_sync_stream_socket_nonblocking_or_throw(identity, label);
        require_sync_stream_socket_close_on_exec_or_throw(identity, label);
        if (std::chrono::steady_clock::now() >= deadline) {
            return RouteIoDisposition::DeadlineExpired;
        }

        errno = 0;
        const ssize_t received = ::recv(
            socket.descriptor(), bytes.data() + offset,
            bytes.size() - offset, 0);
        const int receive_errno = errno;
        if (received > 0) {
            const auto count = static_cast<std::size_t>(received);
            offset += count;
            received_total += static_cast<std::uint64_t>(count);
            continue;
        }
        if (received == 0) return RouteIoDisposition::PeerClosed;
        if (receive_errno == EINTR) continue;
        if (receive_errno == EAGAIN || receive_errno == EWOULDBLOCK) {
            const auto readiness = poll_route_socket_until_or_throw(
                identity, SyncStreamSocketPollReadiness::Readable, deadline,
                cancellation, std::string(label) + " read readiness");
            if (readiness == RoutePollDisposition::Cancelled) {
                return RouteIoDisposition::Cancelled;
            }
            if (readiness == RoutePollDisposition::DeadlineExpired) {
                return RouteIoDisposition::DeadlineExpired;
            }
            continue;
        }
        if (terminal_socket_error(receive_errno)) {
            return RouteIoDisposition::PeerClosed;
        }
        throw std::runtime_error(
            std::string(label) + " receive failed (errno " +
            std::to_string(receive_errno) + ")");
    }
    return RouteIoDisposition::Complete;
}

struct LineReadOutcome final {
    RouteIoDisposition disposition = RouteIoDisposition::PeerClosed;
    std::string line;
};

// Resumable SAM line reader for a retained STREAM ACCEPT socket. Ordinary SAM
// command replies are setup transactions and may be discarded with their socket
// on timeout. The remote destination line is different: it can arrive in pieces
// while the application deliberately uses short idle accept windows, so the
// already-consumed prefix must remain attached to the exact pending socket.
[[nodiscard]] RouteIoDisposition read_line_incrementally_until_or_throw(
    const SocketOwner& socket,
    std::string& line,
    std::chrono::steady_clock::time_point deadline,
    std::uint64_t& received_total,
    std::string_view label,
    std::stop_token cancellation = {}) {
    for (;;) {
        if (line.size() >= kMaximumSamLineBytes) {
            return RouteIoDisposition::PeerClosed;
        }
        std::array<unsigned char, 1U> byte{};
        const RouteIoDisposition disposition = read_exact_until_or_throw(
            socket, byte, deadline, received_total, label, cancellation);
        if (disposition != RouteIoDisposition::Complete) {
            return disposition;
        }
        if (byte[0] == static_cast<unsigned char>('\n')) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            return RouteIoDisposition::Complete;
        }
        if (byte[0] == 0U) return RouteIoDisposition::PeerClosed;
        line.push_back(static_cast<char>(byte[0]));
    }
}

[[nodiscard]] LineReadOutcome read_line_until_or_throw(
    const SocketOwner& socket,
    std::chrono::steady_clock::time_point deadline,
    std::uint64_t& received_total,
    std::string_view label,
    std::stop_token cancellation = {}) {
    LineReadOutcome outcome;
    outcome.line.reserve(128U);
    for (;;) {
        if (outcome.line.size() >= kMaximumSamLineBytes) {
            outcome.disposition = RouteIoDisposition::PeerClosed;
            return outcome;
        }
        std::array<unsigned char, 1U> byte{};
        const RouteIoDisposition disposition = read_exact_until_or_throw(
            socket, byte, deadline, received_total, label, cancellation);
        if (disposition != RouteIoDisposition::Complete) {
            outcome.disposition = disposition;
            return outcome;
        }
        if (byte[0] == static_cast<unsigned char>('\n')) {
            if (!outcome.line.empty() && outcome.line.back() == '\r') {
                outcome.line.pop_back();
            }
            outcome.disposition = RouteIoDisposition::Complete;
            return outcome;
        }
        if (byte[0] == 0U) {
            outcome.disposition = RouteIoDisposition::PeerClosed;
            return outcome;
        }
        outcome.line.push_back(static_cast<char>(byte[0]));
    }
}

[[nodiscard]] std::optional<std::string_view> sam_token_value(
    std::string_view line,
    std::string_view key) noexcept {
    std::size_t position = 0U;
    while (position < line.size()) {
        while (position < line.size() && line[position] == ' ') ++position;
        if (position >= line.size()) break;
        const std::size_t end = line.find(' ', position);
        const std::size_t token_end =
            end == std::string_view::npos ? line.size() : end;
        const std::string_view token = line.substr(position, token_end - position);
        if (token.size() > key.size() + 1U &&
            token.starts_with(key) && token[key.size()] == '=') {
            return token.substr(key.size() + 1U);
        }
        position = token_end + (end == std::string_view::npos ? 0U : 1U);
    }
    return std::nullopt;
}

[[nodiscard]] SyncReplicaI2pSamResult sam_result_from_token(
    std::string_view value) noexcept {
    if (value == "OK") return SyncReplicaI2pSamResult::Ok;
    if (value == "NOVERSION") return SyncReplicaI2pSamResult::NoVersion;
    if (value == "DUPLICATED_ID") {
        return SyncReplicaI2pSamResult::DuplicateId;
    }
    if (value == "DUPLICATED_DEST") {
        return SyncReplicaI2pSamResult::DuplicateDestination;
    }
    if (value == "INVALID_KEY") return SyncReplicaI2pSamResult::InvalidKey;
    if (value == "INVALID_ID") return SyncReplicaI2pSamResult::InvalidId;
    if (value == "CANT_REACH_PEER") {
        return SyncReplicaI2pSamResult::CantReachPeer;
    }
    if (value == "KEY_NOT_FOUND") {
        return SyncReplicaI2pSamResult::KeyNotFound;
    }
    if (value == "PEER_NOT_FOUND") {
        return SyncReplicaI2pSamResult::PeerNotFound;
    }
    if (value == "LEASESET_NOT_FOUND") {
        return SyncReplicaI2pSamResult::LeaseSetNotFound;
    }
    if (value == "TIMEOUT") return SyncReplicaI2pSamResult::Timeout;
    if (value == "I2P_ERROR") return SyncReplicaI2pSamResult::I2pError;
    return SyncReplicaI2pSamResult::Unknown;
}

[[nodiscard]] bool sam_response_prefix_matches(
    std::string_view line,
    std::string_view prefix) noexcept {
    return line.size() > prefix.size() && line.starts_with(prefix) &&
           line[prefix.size()] == ' ';
}

[[nodiscard]] RouteIoDisposition send_sam_command_until_or_throw(
    const SocketOwner& socket,
    std::string_view command,
    std::chrono::steady_clock::time_point deadline,
    SyncReplicaStreamConnectReport& report,
    std::string_view label,
    std::stop_token cancellation = {}) {
    if (command.empty() || command.back() != '\n') {
        throw std::logic_error(
            std::string(label) + " SAM command lacks line terminator");
    }
    return write_all_until_or_throw(
        socket,
        std::span<const unsigned char>(
            reinterpret_cast<const unsigned char*>(command.data()),
            command.size()),
        deadline, report.route_bytes_written, label, cancellation);
}

[[nodiscard]] RouteIoDisposition sam_hello_until_or_throw(
    const SocketOwner& socket,
    std::chrono::steady_clock::time_point deadline,
    SyncReplicaStreamConnectReport& report,
    std::string_view label,
    std::stop_token cancellation = {}) {
    const RouteIoDisposition write = send_sam_command_until_or_throw(
        socket, "HELLO VERSION MIN=3.1 MAX=3.2\n", deadline, report,
        std::string(label) + " request", cancellation);
    if (write != RouteIoDisposition::Complete) return write;
    LineReadOutcome response = read_line_until_or_throw(
        socket, deadline, report.route_bytes_received,
        std::string(label) + " response", cancellation);
    if (response.disposition != RouteIoDisposition::Complete) {
        return response.disposition;
    }
    if (!sam_response_prefix_matches(response.line, "HELLO REPLY")) {
        report.sam_result = SyncReplicaI2pSamResult::Unknown;
        return RouteIoDisposition::PeerClosed;
    }
    const auto result = sam_token_value(response.line, "RESULT");
    report.sam_result = result.has_value()
        ? sam_result_from_token(*result)
        : SyncReplicaI2pSamResult::Unknown;
    if (report.sam_result != SyncReplicaI2pSamResult::Ok) {
        return RouteIoDisposition::PeerClosed;
    }
    const auto version = sam_token_value(response.line, "VERSION");
    if (!version.has_value() || (*version != "3.1" && *version != "3.2")) {
        report.sam_result = SyncReplicaI2pSamResult::NoVersion;
        return RouteIoDisposition::PeerClosed;
    }
    return RouteIoDisposition::Complete;
}

template <typename SamRoute>
[[nodiscard]] RouteIoDisposition sam_session_create_until_or_throw(
    const SocketOwner& socket,
    const SamRoute& route,
    std::chrono::steady_clock::time_point deadline,
    SyncReplicaStreamConnectReport& report,
    std::string_view label,
    std::stop_token cancellation = {}) {
    std::string command =
        "SESSION CREATE STYLE=STREAM ID=" + route.session_id +
        " DESTINATION=" + route.session_destination;
    // SAM 3.1 permits SIGNATURE_TYPE only when the bridge is generating a
    // transient destination. A supplied private destination already embeds its
    // signing-key type; appending this option there is invalid on strict SAM
    // implementations and can make persistent I2P identity unusable.
    if (route.session_destination == "TRANSIENT") {
        command += " SIGNATURE_TYPE=7";
    }
    command +=
        " i2cp.leaseSetEncType=4 inbound.quantity=" +
        std::to_string(route.inbound_quantity) + " outbound.quantity=" +
        std::to_string(route.outbound_quantity) + "\n";
    const RouteIoDisposition write = send_sam_command_until_or_throw(
        socket, command, deadline, report,
        std::string(label) + " request", cancellation);
    if (write != RouteIoDisposition::Complete) return write;
    LineReadOutcome response = read_line_until_or_throw(
        socket, deadline, report.route_bytes_received,
        std::string(label) + " response", cancellation);
    if (response.disposition != RouteIoDisposition::Complete) {
        return response.disposition;
    }
    if (!sam_response_prefix_matches(response.line, "SESSION STATUS")) {
        report.sam_result = SyncReplicaI2pSamResult::Unknown;
        return RouteIoDisposition::PeerClosed;
    }
    const auto result = sam_token_value(response.line, "RESULT");
    report.sam_result = result.has_value()
        ? sam_result_from_token(*result)
        : SyncReplicaI2pSamResult::Unknown;
    return report.sam_result == SyncReplicaI2pSamResult::Ok
        ? RouteIoDisposition::Complete
        : RouteIoDisposition::PeerClosed;
}

[[nodiscard]] RouteIoDisposition sam_stream_connect_until_or_throw(
    const SocketOwner& socket,
    const SyncReplicaI2pSamRoute& route,
    std::chrono::steady_clock::time_point deadline,
    SyncReplicaStreamConnectReport& report,
    std::string_view label) {
    const std::string command =
        "STREAM CONNECT ID=" + route.session_id + " DESTINATION=" +
        route.peer_destination + " SILENT=false\n";
    const RouteIoDisposition write = send_sam_command_until_or_throw(
        socket, command, deadline, report,
        std::string(label) + " request");
    if (write != RouteIoDisposition::Complete) return write;
    LineReadOutcome response = read_line_until_or_throw(
        socket, deadline, report.route_bytes_received,
        std::string(label) + " response");
    if (response.disposition != RouteIoDisposition::Complete) {
        return response.disposition;
    }
    if (!sam_response_prefix_matches(response.line, "STREAM STATUS")) {
        report.sam_result = SyncReplicaI2pSamResult::Unknown;
        return RouteIoDisposition::PeerClosed;
    }
    const auto result = sam_token_value(response.line, "RESULT");
    report.sam_result = result.has_value()
        ? sam_result_from_token(*result)
        : SyncReplicaI2pSamResult::Unknown;
    return report.sam_result == SyncReplicaI2pSamResult::Ok
        ? RouteIoDisposition::Complete
        : RouteIoDisposition::PeerClosed;
}

[[nodiscard]] RouteIoDisposition sam_stream_forward_until_or_throw(
    const SocketOwner& socket,
    const SyncReplicaI2pSamForwardRoute& route,
    std::chrono::steady_clock::time_point deadline,
    SyncReplicaStreamConnectReport& report,
    std::string_view label,
    std::stop_token cancellation = {}) {
    const std::string command =
        "STREAM FORWARD ID=" + route.session_id + " HOST=" +
        route.forward_endpoint.numeric_address + " PORT=" +
        std::to_string(route.forward_endpoint.port) + " SILENT=true\n";
    const RouteIoDisposition write = send_sam_command_until_or_throw(
        socket, command, deadline, report,
        std::string(label) + " request", cancellation);
    if (write != RouteIoDisposition::Complete) return write;
    LineReadOutcome response = read_line_until_or_throw(
        socket, deadline, report.route_bytes_received,
        std::string(label) + " response", cancellation);
    if (response.disposition != RouteIoDisposition::Complete) {
        return response.disposition;
    }
    if (!sam_response_prefix_matches(response.line, "STREAM STATUS")) {
        report.sam_result = SyncReplicaI2pSamResult::Unknown;
        return RouteIoDisposition::PeerClosed;
    }
    const auto result = sam_token_value(response.line, "RESULT");
    report.sam_result = result.has_value()
        ? sam_result_from_token(*result)
        : SyncReplicaI2pSamResult::Unknown;
    return report.sam_result == SyncReplicaI2pSamResult::Ok
        ? RouteIoDisposition::Complete
        : RouteIoDisposition::PeerClosed;
}

[[nodiscard]] RouteIoDisposition sam_stream_accept_until_or_throw(
    const SocketOwner& socket,
    const SyncReplicaI2pSamAcceptRoute& route,
    std::chrono::steady_clock::time_point deadline,
    SyncReplicaStreamConnectReport& report,
    std::string_view label,
    std::stop_token cancellation = {}) {
    const std::string command =
        "STREAM ACCEPT ID=" + route.session_id + " SILENT=false\n";
    const RouteIoDisposition write = send_sam_command_until_or_throw(
        socket, command, deadline, report,
        std::string(label) + " request", cancellation);
    if (write != RouteIoDisposition::Complete) return write;
    LineReadOutcome response = read_line_until_or_throw(
        socket, deadline, report.route_bytes_received,
        std::string(label) + " response", cancellation);
    if (response.disposition != RouteIoDisposition::Complete) {
        return response.disposition;
    }
    if (!sam_response_prefix_matches(response.line, "STREAM STATUS")) {
        report.sam_result = SyncReplicaI2pSamResult::Unknown;
        return RouteIoDisposition::PeerClosed;
    }
    const auto result = sam_token_value(response.line, "RESULT");
    report.sam_result = result.has_value()
        ? sam_result_from_token(*result)
        : SyncReplicaI2pSamResult::Unknown;
    return report.sam_result == SyncReplicaI2pSamResult::Ok
        ? RouteIoDisposition::Complete
        : RouteIoDisposition::PeerClosed;
}
#endif

[[nodiscard]] bool visible_nonspace_ascii(std::string_view value) noexcept {
    return std::all_of(value.begin(), value.end(), [](unsigned char byte) {
        return byte >= 0x21U && byte <= 0x7eU;
    });
}

[[nodiscard]] unsigned char tor_base32_value_or_throw(
    char character,
    std::string_view label) {
    if (character >= 'a' && character <= 'z') {
        return static_cast<unsigned char>(character - 'a');
    }
    if (character >= '2' && character <= '7') {
        return static_cast<unsigned char>(26 + character - '2');
    }
    throw std::invalid_argument(
        std::string(label) + " onion service label is not lowercase base32");
}

[[nodiscard]] std::array<unsigned char, kTorV3DecodedBytes>
decode_tor_v3_onion_label_or_throw(
    std::string_view label_bytes,
    std::string_view label) {
    if (label_bytes.size() != kTorV3OnionLabelBytes) {
        throw std::invalid_argument(
            std::string(label) + " onion service label has the wrong length");
    }

    std::array<unsigned char, kTorV3DecodedBytes> decoded{};
    std::uint32_t accumulator = 0U;
    unsigned int accumulated_bits = 0U;
    std::size_t output_index = 0U;
    for (const char character : label_bytes) {
        accumulator = static_cast<std::uint32_t>(
            (accumulator << 5U) |
            tor_base32_value_or_throw(character, label));
        accumulated_bits += 5U;
        while (accumulated_bits >= 8U) {
            accumulated_bits -= 8U;
            if (output_index >= decoded.size()) {
                throw std::logic_error(
                    std::string(label) + " Tor base32 decoder overflowed");
            }
            decoded[output_index++] = static_cast<unsigned char>(
                (accumulator >> accumulated_bits) & 0xffU);
            if (accumulated_bits == 0U) {
                accumulator = 0U;
            } else {
                accumulator &=
                    (static_cast<std::uint32_t>(1U) << accumulated_bits) - 1U;
            }
        }
    }
    if (output_index != decoded.size() || accumulated_bits != 0U ||
        accumulator != 0U) {
        throw std::invalid_argument(
            std::string(label) + " onion service label is not canonical base32");
    }
    return decoded;
}

void validate_tor_v3_onion_checksum_or_throw(
    std::string_view onion_label,
    std::string_view label) {
    const auto decoded =
        decode_tor_v3_onion_label_or_throw(onion_label, label);
    if (decoded.back() != kTorV3Version) {
        throw std::invalid_argument(
            std::string(label) + " onion service version is not Tor v3");
    }

    std::array<unsigned char, EVP_MAX_MD_SIZE> digest{};
    unsigned int digest_bytes = 0U;
    EVP_MD_CTX* const raw_context = EVP_MD_CTX_new();
    if (raw_context == nullptr) {
        throw std::runtime_error(
            std::string(label) + " could not allocate SHA3-256 context");
    }
    const auto free_context = [](EVP_MD_CTX* context) noexcept {
        EVP_MD_CTX_free(context);
    };
    std::unique_ptr<EVP_MD_CTX, decltype(free_context)> context(
        raw_context, free_context);
    if (EVP_DigestInit_ex(context.get(), EVP_sha3_256(), nullptr) != 1 ||
        EVP_DigestUpdate(
            context.get(), kTorV3ChecksumDomain.data(),
            kTorV3ChecksumDomain.size()) != 1 ||
        EVP_DigestUpdate(
            context.get(), decoded.data(), kTorV3PublicKeyBytes) != 1 ||
        EVP_DigestUpdate(
            context.get(), &decoded.back(), 1U) != 1 ||
        EVP_DigestFinal_ex(context.get(), digest.data(), &digest_bytes) != 1 ||
        digest_bytes < 2U) {
        throw std::runtime_error(
            std::string(label) + " could not compute Tor v3 address checksum");
    }
    if (decoded[kTorV3PublicKeyBytes] != digest[0U] ||
        decoded[kTorV3PublicKeyBytes + 1U] != digest[1U]) {
        throw std::invalid_argument(
            std::string(label) + " onion service checksum is invalid");
    }
}

void validate_numeric_endpoint_or_throw(
    const SyncReplicaNumericStreamEndpoint& endpoint,
    std::string_view label) {
#ifdef __linux__
    (void)parse_numeric_endpoint_or_throw(endpoint, label);
#else
    if (endpoint.numeric_address.empty() || endpoint.port == 0U) {
        throw std::invalid_argument(
            std::string(label) + " numeric endpoint is incomplete");
    }
#endif
}

void validate_tor_route_or_throw(
    const SyncReplicaTorSocks5Route& route,
    std::string_view label) {
    validate_numeric_endpoint_or_throw(
        route.proxy, std::string(label) + " proxy");
    if (!sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
            route.proxy, std::string(label) + " proxy")) {
        throw std::invalid_argument(
            std::string(label) +
            " Tor SOCKS proxy must be loopback until authenticated remote-proxy transport exists");
    }
    if (route.service_port == 0U) {
        throw std::invalid_argument(
            std::string(label) + " service port must be nonzero");
    }
    validate_sync_replica_tor_v3_onion_service_or_throw(
        route.onion_service, label);
    if (route.isolation_token.empty() ||
        route.isolation_token.size() > 255U ||
        !visible_nonspace_ascii(route.isolation_token)) {
        throw std::invalid_argument(
            std::string(label) +
            " isolation token must contain 1..255 visible non-space ASCII bytes");
    }
}

void validate_sam_value_or_throw(
    std::string_view value,
    std::size_t maximum_bytes,
    std::string_view label) {
    if (value.empty() || value.size() > maximum_bytes ||
        !visible_nonspace_ascii(value) || value.find('"') != std::string_view::npos ||
        value.find('\\') != std::string_view::npos) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a bounded visible SAM token without quotes or backslashes");
    }
}

[[nodiscard]] std::uint16_t parse_sam_port_or_throw(
    std::string_view value,
    std::string_view label) {
    if (value.empty()) {
        throw std::invalid_argument(std::string(label) + " is empty");
    }
    std::uint32_t parsed = 0U;
    const auto conversion = std::from_chars(
        value.data(), value.data() + value.size(), parsed, 10);
    if (conversion.ec != std::errc{} ||
        conversion.ptr != value.data() + value.size() ||
        parsed > std::numeric_limits<std::uint16_t>::max()) {
        throw std::invalid_argument(
            std::string(label) + " must be a decimal port in 0..65535");
    }
    return static_cast<std::uint16_t>(parsed);
}

// SAM 3.2 appends optional FROM_PORT and TO_PORT tokens to the full remote
// destination delivered after a successful SILENT=false STREAM ACCEPT. Consume
// and validate that entire control line before handing the remaining socket to
// TLS. This prevents SAM metadata from becoming a bogus TLS record while still
// accepting both the original destination-only grammar and the 3.2 grammar.
[[nodiscard]] std::optional<std::string>
parse_sam_stream_accept_peer_line_or_throw(
    std::string_view line,
    SyncReplicaStreamConnectReport& report,
    std::string_view label) {
    if (sam_response_prefix_matches(line, "STREAM STATUS")) {
        const auto result = sam_token_value(line, "RESULT");
        report.sam_result = result.has_value()
            ? sam_result_from_token(*result)
            : SyncReplicaI2pSamResult::Unknown;
        return std::nullopt;
    }

    const std::size_t destination_end = line.find(' ');
    const std::string_view destination = line.substr(0U, destination_end);
    validate_sam_value_or_throw(
        destination, kMaximumI2pPeerDestinationBytes,
        std::string(label) + " remote I2P destination");
    if (destination.size() < 516U) {
        throw std::invalid_argument(
            std::string(label) +
            " remote I2P destination is not a full base64 destination");
    }

    bool saw_from_port = false;
    bool saw_to_port = false;
    std::size_t position = destination_end;
    while (position != std::string_view::npos && position < line.size()) {
        while (position < line.size() && line[position] == ' ') ++position;
        if (position >= line.size()) break;
        const std::size_t end = line.find(' ', position);
        const std::size_t token_end =
            end == std::string_view::npos ? line.size() : end;
        const std::string_view token = line.substr(position, token_end - position);
        const std::size_t separator = token.find('=');
        if (separator == std::string_view::npos || separator == 0U ||
            separator + 1U >= token.size()) {
            throw std::invalid_argument(
                std::string(label) + " contains malformed SAM peer metadata");
        }
        const std::string_view key = token.substr(0U, separator);
        const std::string_view value = token.substr(separator + 1U);
        if (key == "FROM_PORT") {
            if (saw_from_port) {
                throw std::invalid_argument(
                    std::string(label) + " repeats FROM_PORT");
            }
            (void)parse_sam_port_or_throw(
                value, std::string(label) + " FROM_PORT");
            saw_from_port = true;
        } else if (key == "TO_PORT") {
            if (saw_to_port) {
                throw std::invalid_argument(
                    std::string(label) + " repeats TO_PORT");
            }
            (void)parse_sam_port_or_throw(
                value, std::string(label) + " TO_PORT");
            saw_to_port = true;
        } else {
            throw std::invalid_argument(
                std::string(label) + " contains unsupported SAM peer metadata");
        }
        position = end;
    }
    return std::string(destination);
}

template <typename SamRoute>
void validate_i2p_session_route_or_throw(
    const SamRoute& route,
    std::string_view label) {
    validate_numeric_endpoint_or_throw(
        route.bridge, std::string(label) + " bridge");
    if (!sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
            route.bridge, std::string(label) + " bridge")) {
        throw std::invalid_argument(
            std::string(label) +
            " SAM bridge must be loopback until authenticated remote-SAM transport exists");
    }
    if (route.session_id.empty() ||
        route.session_id.size() > kMaximumI2pSamSessionIdBytes ||
        !std::all_of(
            route.session_id.begin(), route.session_id.end(), [](char value) {
                return (value >= 'a' && value <= 'z') ||
                       (value >= 'A' && value <= 'Z') ||
                       (value >= '0' && value <= '9') || value == '-' ||
                       value == '_' || value == '.';
            })) {
        throw std::invalid_argument(
            std::string(label) +
            " session ID must contain 1..64 ASCII letters, digits, '.', '_', or '-'");
    }
    validate_sam_value_or_throw(
        route.session_destination, kMaximumI2pSessionDestinationBytes,
        std::string(label) + " session destination");
    if (route.inbound_quantity == 0U ||
        route.inbound_quantity > kMaximumI2pTunnelQuantity ||
        route.outbound_quantity == 0U ||
        route.outbound_quantity > kMaximumI2pTunnelQuantity) {
        throw std::invalid_argument(
            std::string(label) + " tunnel quantities must be in 1..16");
    }
}

void validate_i2p_route_or_throw(
    const SyncReplicaI2pSamRoute& route,
    std::string_view label) {
    validate_i2p_session_route_or_throw(route, label);
    validate_sam_value_or_throw(
        route.peer_destination, kMaximumI2pPeerDestinationBytes,
        std::string(label) + " peer destination");
    if (!route.peer_destination.ends_with(".i2p") &&
        route.peer_destination.size() < 516U) {
        throw std::invalid_argument(
            std::string(label) +
            " peer destination must be an .i2p name/b32 address or a full base64 destination");
    }
}

void validate_i2p_forward_route_or_throw(
    const SyncReplicaI2pSamForwardRoute& route,
    std::string_view label) {
    validate_i2p_session_route_or_throw(route, label);
    if (route.session_destination == "TRANSIENT") {
        throw std::invalid_argument(
            std::string(label) +
            " native inbound publication requires a persisted private destination");
    }
    validate_numeric_endpoint_or_throw(
        route.forward_endpoint, std::string(label) + " forward endpoint");
    if (!sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
            route.forward_endpoint,
            std::string(label) + " forward endpoint")) {
        throw std::invalid_argument(
            std::string(label) +
            " local forward endpoint must be loopback");
    }
}

void validate_i2p_accept_route_or_throw(
    const SyncReplicaI2pSamAcceptRoute& route,
    std::string_view label) {
    validate_i2p_session_route_or_throw(route, label);
    if (route.session_destination == "TRANSIENT") {
        throw std::invalid_argument(
            std::string(label) +
            " native inbound acceptance requires a persisted private destination");
    }
}

[[nodiscard]] SyncReplicaStreamConnectOutcome failed_outcome(
    SyncReplicaStreamConnectReport report,
    SyncReplicaStreamConnectDisposition disposition,
    SyncReplicaStreamRouteStage stage) {
    report.disposition = disposition;
    report.terminal_stage = stage;
    SyncReplicaStreamConnectOutcome outcome;
    outcome.report = std::move(report);
    return outcome;
}

#ifdef __linux__
[[nodiscard]] SyncReplicaStreamConnectOutcome route_io_failure(
    SyncReplicaStreamConnectReport report,
    RouteIoDisposition disposition,
    SyncReplicaStreamRouteStage stage) {
    return failed_outcome(
        std::move(report),
        disposition == RouteIoDisposition::DeadlineExpired
            ? SyncReplicaStreamConnectDisposition::DeadlineExpired
            : disposition == RouteIoDisposition::Cancelled
                ? SyncReplicaStreamConnectDisposition::Cancelled
                : SyncReplicaStreamConnectDisposition::RouteRejected,
        stage);
}

[[nodiscard]] SyncReplicaStreamConnectReport route_io_failure_report(
    SyncReplicaStreamConnectReport report,
    RouteIoDisposition disposition,
    SyncReplicaStreamRouteStage stage) {
    report.disposition =
        disposition == RouteIoDisposition::DeadlineExpired
        ? SyncReplicaStreamConnectDisposition::DeadlineExpired
        : disposition == RouteIoDisposition::Cancelled
            ? SyncReplicaStreamConnectDisposition::Cancelled
            : SyncReplicaStreamConnectDisposition::RouteRejected;
    report.terminal_stage = stage;
    return report;
}
#endif

}  // namespace

struct SyncReplicaI2pSamForwarder::Implementation final {
#ifdef __linux__
    // Declaration order makes the forwarding socket close before the control
    // socket during reverse-order destruction.
    std::optional<SocketOwner> sam_control;
    std::optional<SocketOwner> sam_forward;
#endif
    bool start_attempted = false;
    bool forwarding_ready = false;
};

struct SyncReplicaI2pSamAcceptor::Implementation final {
#ifdef __linux__
    // A pending accept is subordinate to the control session and therefore
    // closes first during reverse-order destruction.
    std::optional<SocketOwner> sam_control;
    std::optional<SocketOwner> sam_accept;
    std::string peer_destination_prefix;
#endif
    bool start_attempted = false;
    bool session_ready = false;
};

struct SyncReplicaStreamConnector::Implementation final {
#ifdef __linux__
    std::optional<SocketOwner> sam_control;
#endif
    bool sam_session_ready = false;
};

void validate_sync_replica_tor_v3_onion_service_or_throw(
    std::string_view onion_service,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica Tor v3 onion service label is empty");
    }
    constexpr std::string_view suffix = ".onion";
    if (onion_service.size() != kTorV3OnionLabelBytes + suffix.size() ||
        !onion_service.ends_with(suffix)) {
        throw std::invalid_argument(
            std::string(label) +
            " requires one lowercase Tor v3 56-character service label plus .onion");
    }
    validate_tor_v3_onion_checksum_or_throw(
        onion_service.substr(0U, kTorV3OnionLabelBytes), label);
}

bool sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
    const SyncReplicaNumericStreamEndpoint& endpoint,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica numeric stream endpoint label is empty");
    }
#ifdef __linux__
    return parsed_numeric_endpoint_is_loopback(
        parse_numeric_endpoint_or_throw(endpoint, label));
#else
    validate_numeric_endpoint_or_throw(endpoint, label);
    return endpoint.numeric_address == "127.0.0.1" ||
        endpoint.numeric_address == "::1";
#endif
}

void validate_sync_replica_i2p_sam_forward_route_or_throw(
    const SyncReplicaI2pSamForwardRoute& route,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica I2P SAM forward route label is empty");
    }
    validate_i2p_forward_route_or_throw(route, label);
}

void validate_sync_replica_i2p_sam_accept_route_or_throw(
    const SyncReplicaI2pSamAcceptRoute& route,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica I2P SAM accept route label is empty");
    }
    validate_i2p_accept_route_or_throw(route, label);
}

std::string_view sync_replica_stream_route_kind_name(
    SyncReplicaStreamRouteKind kind) noexcept {
    switch (kind) {
        case SyncReplicaStreamRouteKind::DirectTcp:
            return "direct_tcp";
        case SyncReplicaStreamRouteKind::TorSocks5:
            return "tor_socks5";
        case SyncReplicaStreamRouteKind::I2pSam:
            return "i2p_sam";
    }
    return "unknown";
}

SyncReplicaStreamRouteKind sync_replica_stream_route_kind(
    const SyncReplicaStreamRoute& route) noexcept {
    return std::visit(
        [](const auto& selected) noexcept {
            using Route = std::decay_t<decltype(selected)>;
            if constexpr (std::is_same_v<Route, SyncReplicaDirectTcpRoute>) {
                return SyncReplicaStreamRouteKind::DirectTcp;
            } else if constexpr (
                std::is_same_v<Route, SyncReplicaTorSocks5Route>) {
                return SyncReplicaStreamRouteKind::TorSocks5;
            } else {
                return SyncReplicaStreamRouteKind::I2pSam;
            }
        },
        route);
}

void validate_sync_replica_stream_route_or_throw(
    const SyncReplicaStreamRoute& route,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument("sync replica stream route label is empty");
    }
    std::visit(
        [&](const auto& selected) {
            using Route = std::decay_t<decltype(selected)>;
            if constexpr (std::is_same_v<Route, SyncReplicaDirectTcpRoute>) {
                validate_numeric_endpoint_or_throw(
                    selected.endpoint, std::string(label) + " direct");
            } else if constexpr (
                std::is_same_v<Route, SyncReplicaTorSocks5Route>) {
                validate_tor_route_or_throw(selected, label);
            } else {
                validate_i2p_route_or_throw(selected, label);
            }
        },
        route);
}

std::string_view sync_replica_stream_connect_disposition_name(
    SyncReplicaStreamConnectDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaStreamConnectDisposition::Connected:
            return "connected";
        case SyncReplicaStreamConnectDisposition::DeadlineExpired:
            return "deadline_expired";
        case SyncReplicaStreamConnectDisposition::NumericConnectFailed:
            return "numeric_connect_failed";
        case SyncReplicaStreamConnectDisposition::RouteRejected:
            return "route_rejected";
        case SyncReplicaStreamConnectDisposition::Cancelled:
            return "cancelled";
    }
    return "unknown";
}

std::string_view sync_replica_stream_route_stage_name(
    SyncReplicaStreamRouteStage stage) noexcept {
    switch (stage) {
        case SyncReplicaStreamRouteStage::NumericConnect:
            return "numeric_connect";
        case SyncReplicaStreamRouteStage::TorMethodNegotiation:
            return "tor_method_negotiation";
        case SyncReplicaStreamRouteStage::TorAuthentication:
            return "tor_authentication";
        case SyncReplicaStreamRouteStage::TorConnect:
            return "tor_connect";
        case SyncReplicaStreamRouteStage::I2pControlHello:
            return "i2p_control_hello";
        case SyncReplicaStreamRouteStage::I2pSessionCreate:
            return "i2p_session_create";
        case SyncReplicaStreamRouteStage::I2pStreamHello:
            return "i2p_stream_hello";
        case SyncReplicaStreamRouteStage::I2pStreamConnect:
            return "i2p_stream_connect";
        case SyncReplicaStreamRouteStage::I2pStreamForward:
            return "i2p_stream_forward";
        case SyncReplicaStreamRouteStage::I2pStreamAccept:
            return "i2p_stream_accept";
        case SyncReplicaStreamRouteStage::I2pStreamPeerDestination:
            return "i2p_stream_peer_destination";
        case SyncReplicaStreamRouteStage::Complete:
            return "complete";
    }
    return "unknown";
}

std::string_view sync_replica_i2p_sam_result_name(
    SyncReplicaI2pSamResult result) noexcept {
    switch (result) {
        case SyncReplicaI2pSamResult::Ok:
            return "ok";
        case SyncReplicaI2pSamResult::NoVersion:
            return "no_version";
        case SyncReplicaI2pSamResult::DuplicateId:
            return "duplicate_id";
        case SyncReplicaI2pSamResult::DuplicateDestination:
            return "duplicate_destination";
        case SyncReplicaI2pSamResult::InvalidKey:
            return "invalid_key";
        case SyncReplicaI2pSamResult::InvalidId:
            return "invalid_id";
        case SyncReplicaI2pSamResult::CantReachPeer:
            return "cant_reach_peer";
        case SyncReplicaI2pSamResult::KeyNotFound:
            return "key_not_found";
        case SyncReplicaI2pSamResult::PeerNotFound:
            return "peer_not_found";
        case SyncReplicaI2pSamResult::LeaseSetNotFound:
            return "leaseset_not_found";
        case SyncReplicaI2pSamResult::Timeout:
            return "timeout";
        case SyncReplicaI2pSamResult::I2pError:
            return "i2p_error";
        case SyncReplicaI2pSamResult::Unknown:
            return "unknown";
    }
    return "unknown";
}

SyncReplicaI2pSamForwarder::SyncReplicaI2pSamForwarder(
    SyncReplicaI2pSamForwardRoute route,
    std::string label)
    : route_(std::move(route)),
      label_(std::move(label)),
      implementation_(std::make_unique<Implementation>()) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica I2P SAM forwarder label is empty");
    }
    validate_sync_replica_i2p_sam_forward_route_or_throw(
        route_, label_ + " route");
    route_.session_id = runtime_i2p_sam_session_id_or_throw(
        route_.session_id, label_);
}

SyncReplicaI2pSamForwarder::~SyncReplicaI2pSamForwarder() noexcept = default;

bool SyncReplicaI2pSamForwarder::active() const noexcept {
#ifdef __linux__
    return implementation_->forwarding_ready &&
        implementation_->sam_control.has_value() &&
        implementation_->sam_forward.has_value();
#else
    return false;
#endif
}

void SyncReplicaI2pSamForwarder::require_active_or_throw(
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica I2P SAM forwarding capability label is empty");
    }
#ifdef __linux__
    if (!active()) {
        throw std::logic_error(
            std::string(label) + " is inactive");
    }
    const bool control_live = sam_control_session_is_reusable_or_throw(
        *implementation_->sam_control,
        std::string(label) + " control socket");
    const bool forward_live = sam_control_session_is_reusable_or_throw(
        *implementation_->sam_forward,
        std::string(label) + " forwarding socket");
    if (!control_live || !forward_live) {
        implementation_->sam_forward.reset();
        implementation_->sam_control.reset();
        implementation_->forwarding_ready = false;
        throw std::runtime_error(
            std::string(label) + " lost retained SAM forwarding authority");
    }
#else
    throw std::runtime_error(
        std::string(label) + " requires Linux exact socket authority");
#endif
}

SyncReplicaStreamConnectReport
SyncReplicaI2pSamForwarder::start_until_or_throw(
    std::chrono::steady_clock::time_point deadline) {
    return start_until_or_throw(deadline, {});
}

SyncReplicaStreamConnectReport
SyncReplicaI2pSamForwarder::start_until_or_throw(
    std::chrono::steady_clock::time_point deadline,
    std::stop_token cancellation) {
    if (implementation_->start_attempted) {
        throw std::logic_error(
            label_ + " setup was already attempted");
    }
    implementation_->start_attempted = true;
    SyncReplicaStreamConnectReport report;
    report.route_kind = SyncReplicaStreamRouteKind::I2pSam;
    if (cancellation.stop_requested()) {
        report.disposition = SyncReplicaStreamConnectDisposition::Cancelled;
        return report;
    }
    if (std::chrono::steady_clock::now() >= deadline) {
        report.disposition =
            SyncReplicaStreamConnectDisposition::DeadlineExpired;
        return report;
    }
#ifdef __linux__
    NumericConnectOutcome control = connect_numeric_until_or_throw(
        route_.bridge, deadline, label_ + " SAM control connect", cancellation);
    report.numeric_connect_attempts += control.attempts;
    report.numeric_connect_error = control.error;
    if (control.disposition != SyncReplicaStreamConnectDisposition::Connected) {
        report.disposition = control.disposition;
        report.terminal_stage = SyncReplicaStreamRouteStage::NumericConnect;
        return report;
    }
    SocketOwner control_socket = std::move(*control.socket);

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pControlHello;
    RouteIoDisposition io = sam_hello_until_or_throw(
        control_socket, deadline, report, label_ + " SAM control HELLO",
        cancellation);
    if (io != RouteIoDisposition::Complete) {
        return route_io_failure_report(report, io, report.terminal_stage);
    }

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pSessionCreate;
    io = sam_session_create_until_or_throw(
        control_socket, route_, deadline, report,
        label_ + " SAM session create", cancellation);
    if (io != RouteIoDisposition::Complete) {
        return route_io_failure_report(report, io, report.terminal_stage);
    }
    report.control_session_created = true;

    NumericConnectOutcome forward = connect_numeric_until_or_throw(
        route_.bridge, deadline, label_ + " SAM forwarding connect", cancellation);
    report.data_socket_created = forward.socket_created;
    report.data_socket_policy_verified = forward.socket_policy_verified;
    report.numeric_connect_attempts += forward.attempts;
    report.numeric_connect_error = forward.error;
    if (forward.disposition != SyncReplicaStreamConnectDisposition::Connected) {
        report.disposition = forward.disposition;
        report.terminal_stage = SyncReplicaStreamRouteStage::NumericConnect;
        return report;
    }
    SocketOwner forward_socket = std::move(*forward.socket);

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pStreamHello;
    io = sam_hello_until_or_throw(
        forward_socket, deadline, report, label_ + " SAM forwarding HELLO",
        cancellation);
    if (io != RouteIoDisposition::Complete) {
        return route_io_failure_report(report, io, report.terminal_stage);
    }

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pStreamForward;
    io = sam_stream_forward_until_or_throw(
        forward_socket, route_, deadline, report,
        label_ + " SAM STREAM FORWARD", cancellation);
    if (io != RouteIoDisposition::Complete) {
        return route_io_failure_report(report, io, report.terminal_stage);
    }

    implementation_->sam_control.emplace(std::move(control_socket));
    implementation_->sam_forward.emplace(std::move(forward_socket));
    implementation_->forwarding_ready = true;
    report.disposition = SyncReplicaStreamConnectDisposition::Connected;
    report.terminal_stage = SyncReplicaStreamRouteStage::Complete;
    report.route_negotiated = true;
    return report;
#else
    (void)deadline;
    (void)cancellation;
    throw std::runtime_error(
        label_ + " requires Linux exact nonblocking socket authority");
#endif
}

namespace {

#ifdef __linux__
[[nodiscard]] std::optional<SocketOwner> arm_i2p_sam_accept_until_or_throw(
    const SyncReplicaI2pSamAcceptRoute& route,
    std::chrono::steady_clock::time_point deadline,
    SyncReplicaStreamConnectReport& report,
    const std::string& label,
    std::stop_token cancellation = {}) {
    NumericConnectOutcome accepted = connect_numeric_until_or_throw(
        route.bridge, deadline, label + " SAM accept connect", cancellation);
    report.data_socket_created = accepted.socket_created;
    report.data_socket_policy_verified = accepted.socket_policy_verified;
    report.numeric_connect_attempts += accepted.attempts;
    report.numeric_connect_error = accepted.error;
    if (accepted.disposition != SyncReplicaStreamConnectDisposition::Connected) {
        report.disposition = accepted.disposition;
        report.terminal_stage = SyncReplicaStreamRouteStage::NumericConnect;
        return std::nullopt;
    }
    SocketOwner accept_socket = std::move(*accepted.socket);

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pStreamHello;
    RouteIoDisposition io = sam_hello_until_or_throw(
        accept_socket, deadline, report, label + " SAM accept HELLO",
        cancellation);
    if (io != RouteIoDisposition::Complete) {
        report = route_io_failure_report(report, io, report.terminal_stage);
        return std::nullopt;
    }

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pStreamAccept;
    io = sam_stream_accept_until_or_throw(
        accept_socket, route, deadline, report,
        label + " SAM STREAM ACCEPT", cancellation);
    if (io != RouteIoDisposition::Complete) {
        report = route_io_failure_report(report, io, report.terminal_stage);
        return std::nullopt;
    }
    return accept_socket;
}
#endif

}  // namespace

SyncReplicaI2pSamAcceptor::SyncReplicaI2pSamAcceptor(
    SyncReplicaI2pSamAcceptRoute route,
    std::string label)
    : route_(std::move(route)),
      label_(std::move(label)),
      implementation_(std::make_unique<Implementation>()) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica I2P SAM acceptor label is empty");
    }
    validate_sync_replica_i2p_sam_accept_route_or_throw(
        route_, label_ + " route");
    route_.session_id = runtime_i2p_sam_session_id_or_throw(
        route_.session_id, label_);
}

SyncReplicaI2pSamAcceptor::~SyncReplicaI2pSamAcceptor() noexcept = default;

bool SyncReplicaI2pSamAcceptor::active() const noexcept {
#ifdef __linux__
    return implementation_->session_ready &&
        implementation_->sam_control.has_value();
#else
    return false;
#endif
}

bool SyncReplicaI2pSamAcceptor::accept_armed() const noexcept {
#ifdef __linux__
    return active() && implementation_->sam_accept.has_value();
#else
    return false;
#endif
}

void SyncReplicaI2pSamAcceptor::require_active_or_throw(
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica I2P SAM accept capability label is empty");
    }
#ifdef __linux__
    if (!active()) {
        throw std::logic_error(std::string(label) + " is inactive");
    }
    const bool control_live = sam_control_session_is_reusable_or_throw(
        *implementation_->sam_control,
        std::string(label) + " control socket");
    const bool accept_live = !implementation_->sam_accept.has_value() ||
        sam_pending_accept_is_live_or_throw(
            *implementation_->sam_accept,
            std::string(label) + " pending accept socket");
    if (!control_live || !accept_live) {
        implementation_->sam_accept.reset();
        implementation_->sam_control.reset();
        implementation_->peer_destination_prefix.clear();
        implementation_->session_ready = false;
        throw std::runtime_error(
            std::string(label) + " lost retained SAM accept authority");
    }
#else
    throw std::runtime_error(
        std::string(label) + " requires Linux exact socket authority");
#endif
}

SyncReplicaStreamConnectReport
SyncReplicaI2pSamAcceptor::start_until_or_throw(
    std::chrono::steady_clock::time_point deadline) {
    return start_until_or_throw(deadline, {});
}

SyncReplicaStreamConnectReport
SyncReplicaI2pSamAcceptor::start_until_or_throw(
    std::chrono::steady_clock::time_point deadline,
    std::stop_token cancellation) {
    if (implementation_->start_attempted) {
        throw std::logic_error(label_ + " setup was already attempted");
    }
    implementation_->start_attempted = true;
    SyncReplicaStreamConnectReport report;
    report.route_kind = SyncReplicaStreamRouteKind::I2pSam;
    if (cancellation.stop_requested()) {
        report.disposition = SyncReplicaStreamConnectDisposition::Cancelled;
        return report;
    }
    if (std::chrono::steady_clock::now() >= deadline) {
        report.disposition =
            SyncReplicaStreamConnectDisposition::DeadlineExpired;
        return report;
    }
#ifdef __linux__
    NumericConnectOutcome control = connect_numeric_until_or_throw(
        route_.bridge, deadline, label_ + " SAM control connect", cancellation);
    report.numeric_connect_attempts += control.attempts;
    report.numeric_connect_error = control.error;
    if (control.disposition != SyncReplicaStreamConnectDisposition::Connected) {
        report.disposition = control.disposition;
        report.terminal_stage = SyncReplicaStreamRouteStage::NumericConnect;
        return report;
    }
    SocketOwner control_socket = std::move(*control.socket);

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pControlHello;
    RouteIoDisposition io = sam_hello_until_or_throw(
        control_socket, deadline, report, label_ + " SAM control HELLO",
        cancellation);
    if (io != RouteIoDisposition::Complete) {
        return route_io_failure_report(report, io, report.terminal_stage);
    }

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pSessionCreate;
    io = sam_session_create_until_or_throw(
        control_socket, route_, deadline, report,
        label_ + " SAM session create", cancellation);
    if (io != RouteIoDisposition::Complete) {
        return route_io_failure_report(report, io, report.terminal_stage);
    }
    report.control_session_created = true;

    std::optional<SocketOwner> accept_socket =
        arm_i2p_sam_accept_until_or_throw(
            route_, deadline, report, label_, cancellation);
    if (!accept_socket.has_value()) return report;

    implementation_->sam_control.emplace(std::move(control_socket));
    implementation_->sam_accept.emplace(std::move(*accept_socket));
    implementation_->peer_destination_prefix.clear();
    implementation_->session_ready = true;
    report.disposition = SyncReplicaStreamConnectDisposition::Connected;
    report.terminal_stage = SyncReplicaStreamRouteStage::Complete;
    report.route_negotiated = true;
    return report;
#else
    (void)deadline;
    (void)cancellation;
    throw std::runtime_error(
        label_ + " requires Linux exact nonblocking socket authority");
#endif
}

SyncReplicaI2pSamAcceptOutcome
SyncReplicaI2pSamAcceptor::accept_until_or_throw(
    std::chrono::steady_clock::time_point setup_deadline,
    std::chrono::steady_clock::time_point peer_deadline) {
    return accept_until_or_throw(setup_deadline, peer_deadline, {});
}

SyncReplicaI2pSamAcceptOutcome
SyncReplicaI2pSamAcceptor::accept_until_or_throw(
    std::chrono::steady_clock::time_point setup_deadline,
    std::chrono::steady_clock::time_point peer_deadline,
    std::stop_token cancellation) {
    SyncReplicaI2pSamAcceptOutcome outcome;
    outcome.report.route_kind = SyncReplicaStreamRouteKind::I2pSam;
    outcome.report.control_session_reused = true;
    if (cancellation.stop_requested()) {
        outcome.report.disposition =
            SyncReplicaStreamConnectDisposition::Cancelled;
        return outcome;
    }
#ifdef __linux__
    // Once STREAM ACCEPT has returned its initial OK, that exact socket may
    // carry either the remote destination or a more specific asynchronous SAM
    // failure. Consume it before inspecting the control socket: the bridge may
    // close both descriptors together, and checking control first would erase
    // the queued per-accept result behind a generic "authority lost" error.
    if (!active()) {
        throw std::logic_error(label_ + " accept is inactive");
    }
    if (!implementation_->sam_accept.has_value()) {
        require_active_or_throw(label_ + " accept setup");
        implementation_->peer_destination_prefix.clear();
        std::optional<SocketOwner> accept_socket =
            arm_i2p_sam_accept_until_or_throw(
                route_, setup_deadline, outcome.report, label_, cancellation);
        if (!accept_socket.has_value()) return outcome;
        implementation_->sam_accept.emplace(std::move(*accept_socket));
    }

    outcome.report.terminal_stage =
        SyncReplicaStreamRouteStage::I2pStreamPeerDestination;
    const RouteIoDisposition read = read_line_incrementally_until_or_throw(
        *implementation_->sam_accept,
        implementation_->peer_destination_prefix,
        peer_deadline,
        outcome.report.route_bytes_received,
        label_ + " SAM remote destination", cancellation);
    if (read == RouteIoDisposition::DeadlineExpired ||
        read == RouteIoDisposition::Cancelled) {
        if (read == RouteIoDisposition::DeadlineExpired &&
            !sam_control_session_is_reusable_or_throw(
                *implementation_->sam_control,
                label_ + " SAM control while accept is pending")) {
            implementation_->sam_accept.reset();
            implementation_->sam_control.reset();
            implementation_->peer_destination_prefix.clear();
            implementation_->session_ready = false;
            throw std::runtime_error(
                label_ + " lost retained SAM accept authority");
        }
        outcome.report.disposition =
            read == RouteIoDisposition::Cancelled
            ? SyncReplicaStreamConnectDisposition::Cancelled
            : SyncReplicaStreamConnectDisposition::DeadlineExpired;
        outcome.report.route_negotiated = true;
        return outcome;
    }
    if (read != RouteIoDisposition::Complete) {
        implementation_->sam_accept.reset();
        implementation_->peer_destination_prefix.clear();
        outcome.report.disposition =
            SyncReplicaStreamConnectDisposition::RouteRejected;
        return outcome;
    }

    try {
        outcome.report.sam_peer_destination =
            parse_sam_stream_accept_peer_line_or_throw(
                implementation_->peer_destination_prefix,
                outcome.report, label_);
    } catch (const std::invalid_argument&) {
        implementation_->sam_accept.reset();
        implementation_->peer_destination_prefix.clear();
        outcome.report.disposition =
            SyncReplicaStreamConnectDisposition::RouteRejected;
        return outcome;
    }
    if (!outcome.report.sam_peer_destination.has_value()) {
        implementation_->sam_accept.reset();
        implementation_->peer_destination_prefix.clear();
        outcome.report.disposition =
            SyncReplicaStreamConnectDisposition::RouteRejected;
        return outcome;
    }

    ReleasedSocket released =
        implementation_->sam_accept->release_or_throw(
            label_ + " accepted I2P stream");
    implementation_->sam_accept.reset();
    implementation_->peer_destination_prefix.clear();
    outcome.stream.emplace(SyncReplicaConnectedStream(
        released.descriptor, std::move(released.identity)));
    outcome.report.data_socket_policy_verified = true;
    outcome.report.disposition = SyncReplicaStreamConnectDisposition::Connected;
    outcome.report.terminal_stage = SyncReplicaStreamRouteStage::Complete;
    outcome.report.route_negotiated = true;
    return outcome;
#else
    (void)setup_deadline;
    (void)peer_deadline;
    (void)cancellation;
    throw std::runtime_error(
        label_ + " requires Linux exact nonblocking socket authority");
#endif
}

SyncReplicaConnectedStream::SyncReplicaConnectedStream(
    int descriptor,
    SyncSocketLifetimeIdentity identity) noexcept
    : descriptor_(descriptor), identity_(std::move(identity)) {}

SyncReplicaConnectedStream::SyncReplicaConnectedStream(
    SyncReplicaConnectedStream&& other) noexcept
    : descriptor_(std::exchange(other.descriptor_, -1)),
      identity_(std::move(other.identity_)) {
    other.identity_.reset();
}

SyncReplicaConnectedStream& SyncReplicaConnectedStream::operator=(
    SyncReplicaConnectedStream&& other) noexcept {
    if (this != &other) {
        close_noexcept();
        descriptor_ = std::exchange(other.descriptor_, -1);
        identity_ = std::move(other.identity_);
        other.identity_.reset();
    }
    return *this;
}

SyncReplicaConnectedStream::~SyncReplicaConnectedStream() noexcept {
    close_noexcept();
}

int SyncReplicaConnectedStream::descriptor() const noexcept {
    return descriptor_;
}

const SyncSocketLifetimeIdentity&
SyncReplicaConnectedStream::socket_identity_or_throw(
    std::string_view label) const {
    if (descriptor_ < 0 || !identity_.has_value()) {
        throw std::logic_error(
            std::string(label) + " socket ownership is absent");
    }
    return *identity_;
}

void SyncReplicaConnectedStream::close_noexcept() noexcept {
#ifdef __linux__
    if (descriptor_ >= 0) {
        const int descriptor = std::exchange(descriptor_, -1);
        identity_.reset();
        (void)::close(descriptor);
    }
#else
    descriptor_ = -1;
    identity_.reset();
#endif
}

SyncReplicaStreamConnector::SyncReplicaStreamConnector(
    SyncReplicaStreamRoute route,
    std::string label)
    : route_(std::move(route)),
      label_(std::move(label)),
      implementation_(std::make_unique<Implementation>()) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica stream connector label is empty");
    }
    validate_sync_replica_stream_route_or_throw(route_, label_ + " route");
    if (auto* sam = std::get_if<SyncReplicaI2pSamRoute>(&route_)) {
        sam->session_id = runtime_i2p_sam_session_id_or_throw(
            sam->session_id, label_);
    }
}

SyncReplicaStreamConnector::~SyncReplicaStreamConnector() noexcept = default;

SyncReplicaStreamConnectOutcome
SyncReplicaStreamConnector::connect_until_or_throw(
    std::chrono::steady_clock::time_point deadline) {
    SyncReplicaStreamConnectReport report;
    report.route_kind = route_kind();
#ifdef __linux__
    const auto make_connected_outcome = [&](
        SyncReplicaStreamConnectReport completed_report,
        SocketOwner socket) {
        completed_report.disposition =
            SyncReplicaStreamConnectDisposition::Connected;
        completed_report.terminal_stage =
            SyncReplicaStreamRouteStage::Complete;
        completed_report.route_negotiated = true;
        ReleasedSocket released = socket.release_or_throw(label_);
        SyncReplicaStreamConnectOutcome outcome;
        outcome.report = std::move(completed_report);
        outcome.stream.emplace(
            SyncReplicaConnectedStream(
                released.descriptor, std::move(released.identity)));
        return outcome;
    };
#endif
    if (std::chrono::steady_clock::now() >= deadline) {
        return failed_outcome(
            std::move(report),
            SyncReplicaStreamConnectDisposition::DeadlineExpired,
            SyncReplicaStreamRouteStage::NumericConnect);
    }

#ifdef __linux__
    if (const auto* direct = std::get_if<SyncReplicaDirectTcpRoute>(&route_)) {
        NumericConnectOutcome connected = connect_numeric_until_or_throw(
            direct->endpoint, deadline, label_ + " direct connect");
        report.data_socket_created = connected.socket_created;
        report.data_socket_policy_verified = connected.socket_policy_verified;
        report.numeric_connect_attempts = connected.attempts;
        report.numeric_connect_error = connected.error;
        if (connected.disposition !=
            SyncReplicaStreamConnectDisposition::Connected) {
            return failed_outcome(
                std::move(report), connected.disposition,
                SyncReplicaStreamRouteStage::NumericConnect);
        }
        return make_connected_outcome(
            std::move(report), std::move(*connected.socket));
    }

    if (const auto* tor = std::get_if<SyncReplicaTorSocks5Route>(&route_)) {
        NumericConnectOutcome connected = connect_numeric_until_or_throw(
            tor->proxy, deadline, label_ + " Tor SOCKS proxy connect");
        report.data_socket_created = connected.socket_created;
        report.data_socket_policy_verified = connected.socket_policy_verified;
        report.numeric_connect_attempts = connected.attempts;
        report.numeric_connect_error = connected.error;
        if (connected.disposition !=
            SyncReplicaStreamConnectDisposition::Connected) {
            return failed_outcome(
                std::move(report), connected.disposition,
                SyncReplicaStreamRouteStage::NumericConnect);
        }
        SocketOwner socket = std::move(*connected.socket);

        report.terminal_stage =
            SyncReplicaStreamRouteStage::TorMethodNegotiation;
        const std::array<unsigned char, 3U> method_request{0x05U, 0x01U, 0x02U};
        RouteIoDisposition io = write_all_until_or_throw(
            socket, method_request, deadline, report.route_bytes_written,
            label_ + " Tor SOCKS method request");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }
        std::array<unsigned char, 2U> method_response{};
        io = read_exact_until_or_throw(
            socket, method_response, deadline, report.route_bytes_received,
            label_ + " Tor SOCKS method response");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }
        if (method_response != std::array<unsigned char, 2U>{0x05U, 0x02U}) {
            return failed_outcome(
                std::move(report),
                SyncReplicaStreamConnectDisposition::RouteRejected,
                SyncReplicaStreamRouteStage::TorMethodNegotiation);
        }

        report.terminal_stage = SyncReplicaStreamRouteStage::TorAuthentication;
        std::vector<unsigned char> auth_request;
        auth_request.reserve(
            3U + kTorSocksFormatZeroUsername.size() +
            tor->isolation_token.size());
        auth_request.push_back(0x01U);
        auth_request.push_back(static_cast<unsigned char>(
            kTorSocksFormatZeroUsername.size()));
        auth_request.insert(
            auth_request.end(), kTorSocksFormatZeroUsername.begin(),
            kTorSocksFormatZeroUsername.end());
        auth_request.push_back(static_cast<unsigned char>(
            tor->isolation_token.size()));
        auth_request.insert(
            auth_request.end(), tor->isolation_token.begin(),
            tor->isolation_token.end());
        io = write_all_until_or_throw(
            socket, auth_request, deadline, report.route_bytes_written,
            label_ + " Tor SOCKS isolation authentication request");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }
        std::array<unsigned char, 2U> auth_response{};
        io = read_exact_until_or_throw(
            socket, auth_response, deadline, report.route_bytes_received,
            label_ + " Tor SOCKS isolation authentication response");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }
        if (auth_response != std::array<unsigned char, 2U>{0x01U, 0x00U}) {
            return failed_outcome(
                std::move(report),
                SyncReplicaStreamConnectDisposition::RouteRejected,
                SyncReplicaStreamRouteStage::TorAuthentication);
        }

        report.terminal_stage = SyncReplicaStreamRouteStage::TorConnect;
        std::vector<unsigned char> connect_request;
        connect_request.reserve(7U + tor->onion_service.size());
        connect_request.insert(
            connect_request.end(), {0x05U, 0x01U, 0x00U, 0x03U});
        connect_request.push_back(
            static_cast<unsigned char>(tor->onion_service.size()));
        connect_request.insert(
            connect_request.end(), tor->onion_service.begin(),
            tor->onion_service.end());
        connect_request.push_back(
            static_cast<unsigned char>(tor->service_port >> 8U));
        connect_request.push_back(
            static_cast<unsigned char>(tor->service_port & 0xffU));
        io = write_all_until_or_throw(
            socket, connect_request, deadline, report.route_bytes_written,
            label_ + " Tor SOCKS connect request");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }

        std::array<unsigned char, 4U> connect_response{};
        io = read_exact_until_or_throw(
            socket, connect_response, deadline, report.route_bytes_received,
            label_ + " Tor SOCKS connect response");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }
        report.socks5_reply = connect_response[1U];
        if (connect_response[0U] != 0x05U || connect_response[1U] != 0x00U ||
            connect_response[2U] != 0x00U) {
            return failed_outcome(
                std::move(report),
                SyncReplicaStreamConnectDisposition::RouteRejected,
                SyncReplicaStreamRouteStage::TorConnect);
        }

        std::size_t address_bytes = 0U;
        if (connect_response[3U] == 0x01U) {
            address_bytes = 4U;
        } else if (connect_response[3U] == 0x04U) {
            address_bytes = 16U;
        } else if (connect_response[3U] == 0x03U) {
            std::array<unsigned char, 1U> length{};
            io = read_exact_until_or_throw(
                socket, length, deadline, report.route_bytes_received,
                label_ + " Tor SOCKS bound-name length");
            if (io != RouteIoDisposition::Complete) {
                return route_io_failure(
                    std::move(report), io, report.terminal_stage);
            }
            address_bytes = length[0U];
        } else {
            return failed_outcome(
                std::move(report),
                SyncReplicaStreamConnectDisposition::RouteRejected,
                SyncReplicaStreamRouteStage::TorConnect);
        }
        std::vector<unsigned char> bound_address(address_bytes + 2U);
        io = read_exact_until_or_throw(
            socket, bound_address, deadline, report.route_bytes_received,
            label_ + " Tor SOCKS bound endpoint");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }
        return make_connected_outcome(
            std::move(report), std::move(socket));
    }

    const auto& sam = std::get<SyncReplicaI2pSamRoute>(route_);
    bool replacing_stale_control = false;
    if (implementation_->sam_session_ready) {
        if (!implementation_->sam_control.has_value()) {
            throw std::logic_error(
                label_ + " SAM session-ready state omitted control socket");
        }
        if (!sam_control_session_is_reusable_or_throw(
                *implementation_->sam_control,
                label_ + " retained I2P SAM control session")) {
            implementation_->sam_control.reset();
            implementation_->sam_session_ready = false;
            report.control_session_stale_detected = true;
            replacing_stale_control = true;
        }
    }
    report.control_session_reused = implementation_->sam_session_ready;
    if (!implementation_->sam_session_ready) {
        NumericConnectOutcome control = connect_numeric_until_or_throw(
            sam.bridge, deadline, label_ + " I2P SAM control connect");
        report.numeric_connect_attempts += control.attempts;
        report.numeric_connect_error = control.error;
        if (control.disposition !=
            SyncReplicaStreamConnectDisposition::Connected) {
            return failed_outcome(
                std::move(report), control.disposition,
                SyncReplicaStreamRouteStage::NumericConnect);
        }
        SocketOwner control_socket = std::move(*control.socket);

        report.terminal_stage = SyncReplicaStreamRouteStage::I2pControlHello;
        RouteIoDisposition io = sam_hello_until_or_throw(
            control_socket, deadline, report,
            label_ + " I2P SAM control HELLO");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }

        report.terminal_stage = SyncReplicaStreamRouteStage::I2pSessionCreate;
        io = sam_session_create_until_or_throw(
            control_socket, sam, deadline, report,
            label_ + " I2P SAM session create");
        if (io != RouteIoDisposition::Complete) {
            return route_io_failure(report, io, report.terminal_stage);
        }
        implementation_->sam_control.emplace(std::move(control_socket));
        implementation_->sam_session_ready = true;
        report.control_session_created = true;
        report.control_session_reused = false;
        report.control_session_recovered = replacing_stale_control;
    }

    NumericConnectOutcome data = connect_numeric_until_or_throw(
        sam.bridge, deadline, label_ + " I2P SAM stream connect");
    report.data_socket_created = data.socket_created;
    report.data_socket_policy_verified = data.socket_policy_verified;
    report.numeric_connect_attempts += data.attempts;
    report.numeric_connect_error = data.error;
    if (data.disposition != SyncReplicaStreamConnectDisposition::Connected) {
        return failed_outcome(
            std::move(report), data.disposition,
            SyncReplicaStreamRouteStage::NumericConnect);
    }
    SocketOwner data_socket = std::move(*data.socket);

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pStreamHello;
    RouteIoDisposition io = sam_hello_until_or_throw(
        data_socket, deadline, report,
        label_ + " I2P SAM stream HELLO");
    if (io != RouteIoDisposition::Complete) {
        return route_io_failure(report, io, report.terminal_stage);
    }

    report.terminal_stage = SyncReplicaStreamRouteStage::I2pStreamConnect;
    io = sam_stream_connect_until_or_throw(
        data_socket, sam, deadline, report,
        label_ + " I2P SAM STREAM CONNECT");
    if (io != RouteIoDisposition::Complete) {
        if (report.sam_result == SyncReplicaI2pSamResult::InvalidId ||
            report.sam_result == SyncReplicaI2pSamResult::I2pError) {
            implementation_->sam_control.reset();
            implementation_->sam_session_ready = false;
            report.control_session_stale_detected = true;
        }
        return route_io_failure(report, io, report.terminal_stage);
    }
    return make_connected_outcome(
        std::move(report), std::move(data_socket));
#else
    (void)deadline;
    throw std::runtime_error(
        label_ + " requires Linux exact nonblocking socket authority");
#endif
}

}  // namespace anonsync
