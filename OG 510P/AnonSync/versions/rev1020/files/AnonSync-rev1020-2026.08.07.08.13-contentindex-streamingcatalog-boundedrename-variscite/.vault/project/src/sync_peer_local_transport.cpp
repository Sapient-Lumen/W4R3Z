#include "anonsync_core.hpp"
#include "anonsync_core_internal.hpp"
#include "sync_peer_ingress_wire.hpp"
#include "sync_peer_transport_digest_bound_frame.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <poll.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

SyncValidationResult local_socket_ok() {
    return {true, ""};
}

SyncValidationResult local_socket_fail(const std::string& reason) {
    return {false, reason};
}

std::uint64_t sum_chunk_bytes_or_throw(const std::vector<std::string>& chunk_bytes,
                                       const std::string& label) {
    std::uint64_t total = 0;
    for (const auto& chunk : chunk_bytes) {
        if (chunk.size() > static_cast<std::size_t>(
                std::numeric_limits<std::uint64_t>::max() - total)) {
            throw std::runtime_error(label + " chunk bytes exceed uint64 range");
        }
        total += static_cast<std::uint64_t>(chunk.size());
    }
    return total;
}

template <typename SubmitOptions, typename SubmitResult>
SyncValidationResult decode_check_and_enqueue_received_transport_frame(
    const SubmitOptions& options,
    const std::string& encoded_frame_digest,
    std::string received_frame,
    SubmitResult& out) {
    SyncPeerTransportDigestBoundFrame digest_bound_frame =
        SyncPeerTransportDigestBoundFrame::bind(
            encoded_frame_digest,
            std::move(received_frame),
            options.max_frame_bytes);
    out.socket_frame_digest = digest_bound_frame.observed_sha256();
    out.frame_digest_checked = true;

    PeerTransportIngressWireLimits limits;
    limits.max_frame_bytes = options.max_frame_bytes;
    limits.max_chunk_count = options.max_chunk_count;
    PeerTransportIngressWirePayload decoded;
    SyncValidationResult decoded_result = decode_peer_transport_ingress_wire_frame(
        limits, digest_bound_frame.bytes(), decoded);
    if (!decoded_result.ok) {
        return local_socket_fail(
            "local transport rejected received canonical ingress frame: " + decoded_result.reason);
    }

    // From here onward all admission material came from the received frame.
    // The sender-side envelope supplied to the fixture is no longer ambient
    // receiver authority. The digest-bound frame above is the only point that
    // can promote socket bytes to checked transport integrity evidence.
    out.canonical_frame_checked = true;
    out.wire_envelope_decoded = true;
    out.payload_bytes_received = true;
    out.transport_envelope_idempotency_key =
        decoded.transport_envelope.transport_envelope_idempotency_key;
    out.payload_digest = decoded.payload_digest;
    out.chunk_count_received = static_cast<std::uint64_t>(decoded.chunk_bytes.size());
    out.chunk_bytes_received = decoded.transport_envelope.peer_batch_envelope.total_bytes;

    SyncPeerTransportIngressEnqueueOptions enqueue_options;
    enqueue_options.sqlite_path = options.sqlite_path;
    enqueue_options.session_id = options.session_id;
    enqueue_options.enqueue_now_epoch = options.submit_now_epoch;
    enqueue_options.max_attempts = options.max_attempts;
    enqueue_options.retry_backoff_seconds = options.retry_backoff_seconds;
    enqueue_options.max_open_rows = options.max_open_rows;
    enqueue_options.max_open_bytes = options.max_open_bytes;
    enqueue_options.max_peer_open_rows = options.max_peer_open_rows;
    enqueue_options.max_peer_open_bytes = options.max_peer_open_bytes;
    enqueue_options.max_open_frame_bytes = options.max_open_frame_bytes;
    enqueue_options.max_peer_open_frame_bytes = options.max_peer_open_frame_bytes;
    enqueue_options.max_frame_bytes = options.max_frame_bytes;
    enqueue_options.max_chunk_count = options.max_chunk_count;
    enqueue_options.require_authority_gate = options.require_authority_gate;
    enqueue_options.sqlite_busy_timeout_ms = options.sqlite_busy_timeout_ms;

    SyncPeerTransportIngressEnqueueResult enqueue_result;
    SyncValidationResult enqueued = enqueue_sync_peer_transport_ingress_envelope(
        enqueue_options,
        decoded.transport_envelope,
        decoded.chunk_bytes,
        enqueue_result);
    out.enqueue = enqueue_result;
    out.row_inserted = enqueue_result.row_inserted;
    out.row_already_present = enqueue_result.row_already_present;
    out.authority_decision = enqueue_result.authority_decision;
    if (!enqueue_result.payload_digest.empty()) out.payload_digest = enqueue_result.payload_digest;
    return enqueued;
}

#if defined(__unix__) || defined(__APPLE__)
struct LocalSocketFd {
    int fd = -1;
    ~LocalSocketFd() { if (fd >= 0) ::close(fd); }
    LocalSocketFd() = default;
    explicit LocalSocketFd(int value) : fd(value) {}
    LocalSocketFd(const LocalSocketFd&) = delete;
    LocalSocketFd& operator=(const LocalSocketFd&) = delete;
    LocalSocketFd(LocalSocketFd&& other) noexcept : fd(other.fd) { other.fd = -1; }
    LocalSocketFd& operator=(LocalSocketFd&& other) noexcept {
        if (this != &other) {
            if (fd >= 0) ::close(fd);
            fd = other.fd;
            other.fd = -1;
        }
        return *this;
    }
};

bool set_nonblocking(int fd, std::string& reason) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) {
        reason = std::string("fcntl(F_GETFL) failed: ") + std::strerror(errno);
        return false;
    }
    if (::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        reason = std::string("fcntl(F_SETFL O_NONBLOCK) failed: ") + std::strerror(errno);
        return false;
    }
    return true;
}

SyncValidationResult transmit_frame_over_socketpair(const std::string& frame,
                                                    std::uint64_t max_frame_bytes,
                                                    SyncPeerTransportLocalSocketIngressSubmitResult& out,
                                                    std::string& received_frame) {
    received_frame.clear();
    if (frame.empty()) return local_socket_fail("local socket transport frame is empty");
    if (frame.size() > max_frame_bytes) return local_socket_fail("local socket transport frame exceeds max_frame_bytes");

    std::array<int, 2> raw_fds{-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, raw_fds.data()) != 0) {
        return local_socket_fail(std::string("local socketpair creation failed: ") + std::strerror(errno));
    }
    LocalSocketFd writer(raw_fds[0]);
    LocalSocketFd reader(raw_fds[1]);
    out.socket_pair_created = true;

    std::string reason;
    if (!set_nonblocking(writer.fd, reason) || !set_nonblocking(reader.fd, reason)) return local_socket_fail(reason);

    std::size_t write_offset = 0;
    bool writer_shutdown = false;
    bool reader_eof = false;
    std::uint64_t idle_polls = 0;
    while (!reader_eof) {
        std::array<pollfd, 2> fds{};
        fds[0].fd = writer.fd;
        fds[0].events = (!writer_shutdown && write_offset < frame.size()) ? POLLOUT : 0;
        fds[1].fd = reader.fd;
        fds[1].events = POLLIN;
        const int rc = ::poll(fds.data(), fds.size(), 1000);
        if (rc < 0) {
            if (errno == EINTR) continue;
            return local_socket_fail(std::string("local socket poll failed: ") + std::strerror(errno));
        }
        if (rc == 0) {
            if (++idle_polls > 5) return local_socket_fail("local socket transport timed out moving frame");
            continue;
        }
        idle_polls = 0;
        if (fds[0].revents & (POLLERR | POLLNVAL)) return local_socket_fail("local socket writer reported an error");
        if (fds[1].revents & (POLLERR | POLLNVAL)) return local_socket_fail("local socket reader reported an error");

        if (!writer_shutdown && (fds[0].revents & POLLOUT) && write_offset < frame.size()) {
            const std::size_t remaining = frame.size() - write_offset;
            const std::size_t requested = remaining > 8192 ? 8192 : remaining;
            const ssize_t written = ::write(writer.fd, frame.data() + write_offset, requested);
            if (written < 0) {
                if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
                    return local_socket_fail(std::string("local socket write failed: ") + std::strerror(errno));
                }
            } else if (written > 0) {
                write_offset += static_cast<std::size_t>(written);
                out.frame_bytes_written += static_cast<std::uint64_t>(written);
                out.frame_sent = write_offset == frame.size();
            }
        }
        if (!writer_shutdown && write_offset == frame.size()) {
            if (::shutdown(writer.fd, SHUT_WR) != 0) {
                return local_socket_fail(std::string("local socket writer shutdown failed: ") + std::strerror(errno));
            }
            writer_shutdown = true;
        }

        if (fds[1].revents & (POLLIN | POLLHUP)) {
            while (true) {
                char buffer[8192];
                const ssize_t read_count = ::read(reader.fd, buffer, sizeof(buffer));
                if (read_count < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) break;
                    return local_socket_fail(std::string("local socket read failed: ") + std::strerror(errno));
                }
                if (read_count == 0) {
                    reader_eof = true;
                    break;
                }
                const std::uint64_t read_bytes = static_cast<std::uint64_t>(read_count);
                if (read_bytes > max_frame_bytes ||
                    static_cast<std::uint64_t>(received_frame.size()) >
                        max_frame_bytes - read_bytes) {
                    return local_socket_fail("local socket transport read exceeded max_frame_bytes");
                }
                received_frame.append(buffer, static_cast<std::size_t>(read_count));
                out.frame_bytes_read += static_cast<std::uint64_t>(read_count);
                out.frame_received = true;
            }
        }
    }
    if (out.frame_bytes_written != static_cast<std::uint64_t>(frame.size())) return local_socket_fail("local socket transport did not write the full frame");
    if (received_frame.size() != frame.size()) return local_socket_fail("local socket transport did not read the full frame");
    return local_socket_ok();
}


struct LoopbackTcpConnection {
    LocalSocketFd listener;
    LocalSocketFd client;
    LocalSocketFd server;
    std::uint16_t port = 0;
};

SyncValidationResult establish_loopback_tcp_connection(SyncPeerTransportLoopbackIngressSubmitResult& out,
                                                       LoopbackTcpConnection& conn) {
    const int listen_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) return local_socket_fail(std::string("loopback transport listener socket failed: ") + std::strerror(errno));
    conn.listener = LocalSocketFd(listen_fd);
    out.listener_created = true;

    int one = 1;
    if (::setsockopt(conn.listener.fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)) != 0) {
        return local_socket_fail(std::string("loopback transport setsockopt(SO_REUSEADDR) failed: ") + std::strerror(errno));
    }

    sockaddr_in listen_addr{};
    listen_addr.sin_family = AF_INET;
    listen_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    listen_addr.sin_port = htons(0);
    if (::bind(conn.listener.fd, reinterpret_cast<sockaddr*>(&listen_addr), sizeof(listen_addr)) != 0) {
        return local_socket_fail(std::string("loopback transport bind failed: ") + std::strerror(errno));
    }
    if (::listen(conn.listener.fd, 1) != 0) {
        return local_socket_fail(std::string("loopback transport listen failed: ") + std::strerror(errno));
    }

    sockaddr_in bound_addr{};
    socklen_t bound_len = sizeof(bound_addr);
    if (::getsockname(conn.listener.fd, reinterpret_cast<sockaddr*>(&bound_addr), &bound_len) != 0) {
        return local_socket_fail(std::string("loopback transport getsockname failed: ") + std::strerror(errno));
    }
    conn.port = ntohs(bound_addr.sin_port);
    out.loopback_address = "127.0.0.1";
    out.loopback_port = conn.port;

    std::string reason;
    if (!set_nonblocking(conn.listener.fd, reason)) return local_socket_fail(reason);

    const int client_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (client_fd < 0) return local_socket_fail(std::string("loopback transport client socket failed: ") + std::strerror(errno));
    conn.client = LocalSocketFd(client_fd);
    out.client_socket_created = true;
    if (!set_nonblocking(conn.client.fd, reason)) return local_socket_fail(reason);

    sockaddr_in connect_addr{};
    connect_addr.sin_family = AF_INET;
    connect_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    connect_addr.sin_port = htons(conn.port);
    const int connect_rc = ::connect(conn.client.fd, reinterpret_cast<sockaddr*>(&connect_addr), sizeof(connect_addr));
    out.client_connect_initiated = true;
    if (connect_rc == 0) {
        out.client_connected = true;
    } else if (errno != EINPROGRESS && errno != EALREADY && errno != EWOULDBLOCK) {
        return local_socket_fail(std::string("loopback transport connect failed: ") + std::strerror(errno));
    }

    std::uint64_t idle_polls = 0;
    while (!out.client_connected || !out.server_accepted) {
        std::array<pollfd, 2> fds{};
        fds[0].fd = out.server_accepted ? -1 : conn.listener.fd;
        fds[0].events = out.server_accepted ? 0 : POLLIN;
        fds[1].fd = out.client_connected ? -1 : conn.client.fd;
        fds[1].events = out.client_connected ? 0 : POLLOUT;
        const int poll_rc = ::poll(fds.data(), fds.size(), 100);
        if (poll_rc < 0) {
            if (errno == EINTR) continue;
            return local_socket_fail(std::string("loopback transport connection poll failed: ") + std::strerror(errno));
        }
        if (poll_rc == 0) {
            if (++idle_polls > 50) return local_socket_fail("loopback transport timed out establishing client/server sockets");
            continue;
        }
        idle_polls = 0;
        if (!out.client_connected && (fds[1].revents & (POLLOUT | POLLERR | POLLHUP))) {
            int so_error = 0;
            socklen_t so_error_len = sizeof(so_error);
            if (::getsockopt(conn.client.fd, SOL_SOCKET, SO_ERROR, &so_error, &so_error_len) != 0) {
                return local_socket_fail(std::string("loopback transport getsockopt(SO_ERROR) failed: ") + std::strerror(errno));
            }
            if (so_error != 0) return local_socket_fail(std::string("loopback transport async connect failed: ") + std::strerror(so_error));
            out.client_connected = true;
        }
        if (!out.server_accepted && (fds[0].revents & (POLLIN | POLLERR | POLLHUP))) {
            sockaddr_in peer_addr{};
            socklen_t peer_len = sizeof(peer_addr);
            const int server_fd = ::accept(conn.listener.fd, reinterpret_cast<sockaddr*>(&peer_addr), &peer_len);
            if (server_fd < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
                return local_socket_fail(std::string("loopback transport accept failed: ") + std::strerror(errno));
            }
            conn.server = LocalSocketFd(server_fd);
            if (!set_nonblocking(conn.server.fd, reason)) return local_socket_fail(reason);
            out.server_accepted = true;
        }
    }
    return local_socket_ok();
}

SyncValidationResult transmit_frame_over_loopback_tcp(const std::string& frame,
                                                      std::uint64_t max_frame_bytes,
                                                      std::uint64_t max_write_chunk_bytes,
                                                      std::uint64_t max_read_chunk_bytes,
                                                      SyncPeerTransportLoopbackIngressSubmitResult& out,
                                                      std::string& received_frame) {
    received_frame.clear();
    if (frame.empty()) return local_socket_fail("loopback transport frame is empty");
    if (frame.size() > max_frame_bytes) return local_socket_fail("loopback transport frame exceeds max_frame_bytes");
    if (max_write_chunk_bytes == 0) return local_socket_fail("loopback transport max_write_chunk_bytes must be positive");
    if (max_read_chunk_bytes == 0) return local_socket_fail("loopback transport max_read_chunk_bytes must be positive");

    LoopbackTcpConnection conn;
    SyncValidationResult connected = establish_loopback_tcp_connection(out, conn);
    if (!connected.ok) return connected;

    std::size_t write_offset = 0;
    bool client_shutdown = false;
    bool server_eof = false;
    std::uint64_t idle_polls = 0;
    const std::size_t write_cap = static_cast<std::size_t>(std::min<std::uint64_t>(max_write_chunk_bytes, 8192));
    const std::size_t read_cap = static_cast<std::size_t>(std::min<std::uint64_t>(max_read_chunk_bytes, 8192));
    std::vector<char> read_buffer(read_cap);

    while (!server_eof) {
        std::array<pollfd, 2> fds{};
        fds[0].fd = conn.client.fd;
        fds[0].events = (!client_shutdown && write_offset < frame.size()) ? POLLOUT : 0;
        fds[1].fd = conn.server.fd;
        fds[1].events = POLLIN;
        const int rc = ::poll(fds.data(), fds.size(), 1000);
        if (rc < 0) {
            if (errno == EINTR) continue;
            return local_socket_fail(std::string("loopback transport poll failed: ") + std::strerror(errno));
        }
        if (rc == 0) {
            if (++idle_polls > 5) return local_socket_fail("loopback transport timed out moving frame");
            continue;
        }
        idle_polls = 0;
        if (fds[0].revents & (POLLERR | POLLNVAL)) return local_socket_fail("loopback transport client writer reported an error");
        if (fds[1].revents & (POLLERR | POLLNVAL)) return local_socket_fail("loopback transport server reader reported an error");

        if (!client_shutdown && (fds[0].revents & POLLOUT) && write_offset < frame.size()) {
            const std::size_t remaining = frame.size() - write_offset;
            const std::size_t requested = std::min(remaining, write_cap);
            const ssize_t written = ::write(conn.client.fd, frame.data() + write_offset, requested);
            if (written < 0) {
                if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
                    return local_socket_fail(std::string("loopback transport write failed: ") + std::strerror(errno));
                }
            } else if (written > 0) {
                ++out.write_call_count;
                write_offset += static_cast<std::size_t>(written);
                out.frame_bytes_written += static_cast<std::uint64_t>(written);
                if (write_offset < frame.size() || static_cast<std::size_t>(written) < remaining) ++out.partial_write_count;
                out.frame_sent = write_offset == frame.size();
            }
        }
        if (!client_shutdown && write_offset == frame.size()) {
            if (::shutdown(conn.client.fd, SHUT_WR) != 0) {
                return local_socket_fail(std::string("loopback transport client shutdown failed: ") + std::strerror(errno));
            }
            client_shutdown = true;
        }

        if (fds[1].revents & (POLLIN | POLLHUP)) {
            while (true) {
                const ssize_t read_count = ::read(conn.server.fd, read_buffer.data(), read_buffer.size());
                if (read_count < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) break;
                    return local_socket_fail(std::string("loopback transport read failed: ") + std::strerror(errno));
                }
                if (read_count == 0) {
                    server_eof = true;
                    break;
                }
                ++out.read_call_count;
                const std::uint64_t read_bytes = static_cast<std::uint64_t>(read_count);
                if (read_bytes > max_frame_bytes ||
                    static_cast<std::uint64_t>(received_frame.size()) >
                        max_frame_bytes - read_bytes) {
                    return local_socket_fail("loopback transport read exceeded max_frame_bytes");
                }
                received_frame.append(read_buffer.data(), static_cast<std::size_t>(read_count));
                out.frame_bytes_read += static_cast<std::uint64_t>(read_count);
                if (received_frame.size() < frame.size()) ++out.partial_read_count;
                out.frame_received = true;
            }
        }
    }
    if (out.frame_bytes_written != static_cast<std::uint64_t>(frame.size())) return local_socket_fail("loopback transport did not write the full frame");
    if (received_frame.size() != frame.size()) return local_socket_fail("loopback transport did not read the full frame");
    return local_socket_ok();
}
#endif

}  // namespace

SyncValidationResult submit_sync_peer_transport_local_socket_ingress_fixture(
    const SyncPeerTransportLocalSocketIngressSubmitOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportLocalSocketIngressSubmitResult& out) {
    out = SyncPeerTransportLocalSocketIngressSubmitResult{};
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.transport_envelope_idempotency_key = transport_envelope.transport_envelope_idempotency_key;
    if (options.max_frame_bytes == 0) return local_socket_fail("local socket transport max_frame_bytes must be positive");
    if (options.max_chunk_count == 0) return local_socket_fail("local socket transport max_chunk_count must be positive");
    if (chunk_bytes.empty()) return local_socket_fail("local socket transport requires at least one chunk payload");
    if (chunk_bytes.size() > options.max_chunk_count) return local_socket_fail("local socket transport chunk count exceeds max_chunk_count");

    try {
        const std::uint64_t input_chunk_total = sum_chunk_bytes_or_throw(chunk_bytes, "local socket transport submit");
        if (input_chunk_total > options.max_frame_bytes) return local_socket_fail("local socket transport chunk bytes exceed max_frame_bytes");
        PeerTransportIngressWireLimits limits;
        limits.max_frame_bytes = options.max_frame_bytes;
        limits.max_chunk_count = options.max_chunk_count;
        std::string frame;
        std::string payload_digest;
        SyncValidationResult encoded = encode_peer_transport_ingress_wire_frame(
            limits, transport_envelope, chunk_bytes, frame, payload_digest);
        if (!encoded.ok) return encoded;
        out.payload_digest = payload_digest;
        out.encoded_frame_digest = sha256_hex(frame);

#if defined(__unix__) || defined(__APPLE__)
        std::string received_frame;
        SyncValidationResult moved = transmit_frame_over_socketpair(frame, options.max_frame_bytes, out, received_frame);
        if (!moved.ok) return moved;
        return decode_check_and_enqueue_received_transport_frame(
            options,
            out.encoded_frame_digest,
            std::move(received_frame),
            out);
#else
        (void)frame;
        return local_socket_fail("local socket transport fixture requires POSIX AF_UNIX socketpair support");
#endif
    } catch (const std::exception& e) {
        return local_socket_fail(std::string("local socket transport submit failed: ") + e.what());
    }
}

SyncValidationResult submit_sync_peer_transport_loopback_ingress_harness(
    const SyncPeerTransportLoopbackIngressSubmitOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportLoopbackIngressSubmitResult& out) {
    out = SyncPeerTransportLoopbackIngressSubmitResult{};
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.transport_envelope_idempotency_key = transport_envelope.transport_envelope_idempotency_key;
    if (options.max_frame_bytes == 0) return local_socket_fail("loopback transport max_frame_bytes must be positive");
    if (options.max_chunk_count == 0) return local_socket_fail("loopback transport max_chunk_count must be positive");
    if (options.max_write_chunk_bytes == 0) return local_socket_fail("loopback transport max_write_chunk_bytes must be positive");
    if (options.max_read_chunk_bytes == 0) return local_socket_fail("loopback transport max_read_chunk_bytes must be positive");
    if (chunk_bytes.empty()) return local_socket_fail("loopback transport requires at least one chunk payload");
    if (chunk_bytes.size() > options.max_chunk_count) return local_socket_fail("loopback transport chunk count exceeds max_chunk_count");

    try {
        const std::uint64_t input_chunk_total = sum_chunk_bytes_or_throw(chunk_bytes, "loopback transport submit");
        if (input_chunk_total > options.max_frame_bytes) return local_socket_fail("loopback transport chunk bytes exceed max_frame_bytes");
        PeerTransportIngressWireLimits limits;
        limits.max_frame_bytes = options.max_frame_bytes;
        limits.max_chunk_count = options.max_chunk_count;
        std::string frame;
        std::string payload_digest;
        SyncValidationResult encoded = encode_peer_transport_ingress_wire_frame(
            limits, transport_envelope, chunk_bytes, frame, payload_digest);
        if (!encoded.ok) return encoded;
        out.payload_digest = payload_digest;
        out.encoded_frame_digest = sha256_hex(frame);

#if defined(__unix__) || defined(__APPLE__)
        std::string received_frame;
        SyncValidationResult moved = transmit_frame_over_loopback_tcp(frame,
                                                                      options.max_frame_bytes,
                                                                      options.max_write_chunk_bytes,
                                                                      options.max_read_chunk_bytes,
                                                                      out,
                                                                      received_frame);
        if (!moved.ok) return moved;
        return decode_check_and_enqueue_received_transport_frame(
            options,
            out.encoded_frame_digest,
            std::move(received_frame),
            out);
#else
        (void)frame;
        return local_socket_fail("loopback transport harness requires POSIX IPv4 loopback socket support");
#endif
    } catch (const std::exception& e) {
        return local_socket_fail(std::string("loopback transport submit failed: ") + e.what());
    }
}

}  // namespace anonsync
