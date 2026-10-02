#include "iotox/local/terminal_socket.hpp"
#include "test_harness.hpp"

#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <fstream>
#include <functional>
#include <poll.h>
#include <span>
#include <string>
#include <string_view>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

using namespace std::chrono_literals;
using iotox::ErrorCode;
using iotox::Status;
using iotox::local::TerminalConnection;
using iotox::local::TerminalOpenRequest;
using iotox::local::TerminalOpened;
using iotox::local::TerminalPacket;
using iotox::local::TerminalPacketType;
using iotox::local::TerminalServer;

std::filesystem::path terminal_socket_test_directory(std::string_view) {
    static std::atomic<unsigned int> sequence{0U};
    return std::filesystem::temp_directory_path() /
           ("it-" + std::to_string(static_cast<long long>(::getpid())) + "-" +
            std::to_string(sequence.fetch_add(1U)));
}

bool eventually(
    const std::function<bool()> &predicate,
    std::chrono::milliseconds timeout = 1000ms) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    do {
        if (predicate()) return true;
        std::this_thread::sleep_for(2ms);
    } while (std::chrono::steady_clock::now() < deadline);
    return predicate();
}

TerminalOpenRequest valid_open_request() {
    TerminalOpenRequest request;
    request.peer_public_key.front() = 0x42U;
    request.columns = 120U;
    request.rows = 40U;
    request.mode = iotox::local::TerminalOpenMode::new_session;
    return request;
}

TerminalPacket open_packet(std::uint64_t stream_id) {
    auto payload = iotox::local::encode_terminal_open(valid_open_request());
    IOTOX_CHECK_MSG(payload.ok(), payload.status().message());
    TerminalPacket packet;
    packet.type = TerminalPacketType::open;
    packet.stream_id = stream_id;
    packet.payload = std::move(payload.value());
    return packet;
}

TerminalPacket control_packet(
    TerminalPacketType type,
    std::uint64_t stream_id) {
    TerminalPacket packet;
    packet.type = type;
    packet.stream_id = stream_id;
    return packet;
}

TerminalPacket opened_packet() {
    TerminalOpened opened;
    opened.session_id.front() = 0x51U;
    opened.incarnation = 7U;
    opened.generation = 11U;
    opened.next_input_sequence = 1U;
    opened.next_output_sequence = 1U;
    auto payload = iotox::local::encode_terminal_opened(opened);
    IOTOX_CHECK_MSG(payload.ok(), payload.status().message());
    TerminalPacket packet;
    packet.type = TerminalPacketType::opened;
    packet.stream_id = 1U;  // Server replaces this with the attached stream ID.
    packet.payload = std::move(payload.value());
    return packet;
}

int bind_raw_seqpacket(
    const std::filesystem::path &path,
    bool listen_for_connections) {
    const std::string text = path.string();
    IOTOX_CHECK(text.size() < sizeof(sockaddr_un::sun_path));
    const int descriptor = ::socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
    IOTOX_CHECK(descriptor >= 0);
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    std::memcpy(address.sun_path, text.c_str(), text.size() + 1U);
    IOTOX_CHECK(::bind(
                    descriptor,
                    reinterpret_cast<const sockaddr *>(&address),
                    sizeof(address)) == 0);
    if (listen_for_connections) IOTOX_CHECK(::listen(descriptor, 4) == 0);
    return descriptor;
}

void prepare_private_directory(const std::filesystem::path &directory) {
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(::mkdir(directory.c_str(), 0700) == 0);
}

void remove_test_directory(const std::filesystem::path &directory) {
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
}

bool send_record_with_descriptor(
    int socket_descriptor,
    std::span<const std::uint8_t> payload,
    int passed_descriptor) {
    struct iovec vector {};
    vector.iov_base = const_cast<std::uint8_t *>(payload.data());
    vector.iov_len = payload.size();
    alignas(cmsghdr) std::array<std::byte, CMSG_SPACE(sizeof(int))> control{};
    struct msghdr message {};
    message.msg_iov = &vector;
    message.msg_iovlen = 1U;
    message.msg_control = control.data();
    message.msg_controllen = control.size();
    cmsghdr *header = CMSG_FIRSTHDR(&message);
    if (header == nullptr) return false;
    header->cmsg_level = SOL_SOCKET;
    header->cmsg_type = SCM_RIGHTS;
    header->cmsg_len = CMSG_LEN(sizeof(int));
    std::memcpy(CMSG_DATA(header), &passed_descriptor, sizeof(passed_descriptor));
    const ssize_t count = ::sendmsg(
        socket_descriptor, &message, MSG_NOSIGNAL);
    return count >= 0 && static_cast<std::size_t>(count) == payload.size();
}

int receive_passed_descriptor(int socket_descriptor, char &marker) {
    struct iovec vector {};
    vector.iov_base = &marker;
    vector.iov_len = sizeof(marker);
    alignas(cmsghdr) std::array<std::byte, CMSG_SPACE(sizeof(int))> control{};
    struct msghdr message {};
    message.msg_iov = &vector;
    message.msg_iovlen = 1U;
    message.msg_control = control.data();
    message.msg_controllen = control.size();
    const ssize_t count = ::recvmsg(
        socket_descriptor, &message, MSG_CMSG_CLOEXEC);
    if (count != 1 || (message.msg_flags & MSG_CTRUNC) != 0) return -1;
    for (cmsghdr *header = CMSG_FIRSTHDR(&message);
         header != nullptr;
         header = CMSG_NXTHDR(&message, header)) {
        if (header->cmsg_level == SOL_SOCKET &&
            header->cmsg_type == SCM_RIGHTS &&
            header->cmsg_len == CMSG_LEN(sizeof(int))) {
            int descriptor = -1;
            std::memcpy(&descriptor, CMSG_DATA(header), sizeof(descriptor));
            return descriptor;
        }
    }
    return -1;
}

bool descriptor_readable_within(
    int descriptor,
    std::chrono::milliseconds timeout) {
    struct pollfd poll_descriptor {descriptor, POLLIN, 0};
    int ready = -1;
    do {
        ready = ::poll(
            &poll_descriptor, 1U, static_cast<int>(timeout.count()));
    } while (ready < 0 && errno == EINTR);
    return ready > 0 &&
           (poll_descriptor.revents & (POLLIN | POLLHUP)) != 0;
}

bool runtime_has_pidfd_open() {
#if defined(SYS_pidfd_open)
    const long descriptor = ::syscall(SYS_pidfd_open, ::getpid(), 0U);
    if (descriptor >= 0) {
        static_cast<void>(::close(static_cast<int>(descriptor)));
        return true;
    }
    return errno != ENOSYS;
#else
    return false;
#endif
}

bool peer_pidfd_supported() {
#if defined(SO_PEERPIDFD)
    int descriptors[2]{-1, -1};
    if (::socketpair(
            AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC,
            0, descriptors) != 0) {
        return false;
    }
    int pidfd = -1;
    socklen_t length = static_cast<socklen_t>(sizeof(pidfd));
    const bool supported = ::getsockopt(
        descriptors[0], SOL_SOCKET, SO_PEERPIDFD,
        &pidfd, &length) == 0 &&
        length == sizeof(pidfd) && pidfd >= 0;
    if (pidfd >= 0) static_cast<void>(::close(pidfd));
    static_cast<void>(::close(descriptors[0]));
    static_cast<void>(::close(descriptors[1]));
    return supported;
#else
    return false;
#endif
}

}  // namespace

IOTOX_TEST("terminal seqpacket server authenticates and streams one local client") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("roundtrip");
    prepare_private_directory(directory);

    std::atomic<bool> opened_pending{false};
    std::atomic<bool> pong_pending{false};
    std::atomic<bool> trailing_output_pending{false};
    std::atomic<bool> detached_pending{false};
    std::atomic<bool> observed_credentials{false};
    std::atomic<std::uint64_t> acknowledged_output{0U};
    std::atomic<unsigned int> disconnects{0U};
    constexpr std::string_view trailing_output = "late-output\n";

    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &credentials) {
            observed_credentials.store(
                credentials.process_id > 0 &&
                credentials.user_id == static_cast<std::uint64_t>(::geteuid()) &&
                credentials.group_id == static_cast<std::uint64_t>(::getegid()));
            switch (packet.type) {
                case TerminalPacketType::open: {
                    auto request = iotox::local::decode_terminal_open(packet.payload);
                    if (!request) return request.status();
                    opened_pending.store(true);
                    return Status::success();
                }
                case TerminalPacketType::ping:
                    pong_pending.store(true);
                    return Status::success();
                case TerminalPacketType::detach:
                    trailing_output_pending.store(true);
                    detached_pending.store(true);
                    return Status::success();
                case TerminalPacketType::output_ack:
                    acknowledged_output.store(packet.sequence);
                    return Status::success();
                default:
                    return Status{ErrorCode::protocol_error,
                                  "unexpected packet in terminal socket test"};
            }
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            if (pong_pending.exchange(false)) {
                packets.push_back(control_packet(TerminalPacketType::pong, 1U));
            }
            if (trailing_output_pending.exchange(false)) {
                TerminalPacket output;
                output.type = TerminalPacketType::output;
                output.stream_id = 1U;
                output.sequence = 1U;
                output.payload.assign(
                    trailing_output.begin(), trailing_output.end());
                packets.push_back(std::move(output));
            }
            if (detached_pending.exchange(false)) {
                packets.push_back(control_packet(TerminalPacketType::detached, 1U));
            }
            IOTOX_CHECK(packets.size() <= maximum_packets);
            return packets;
        },
        [&](std::uint64_t stream_id,
            const iotox::local::PeerCredentials &credentials) {
            if (stream_id == 0x1234U &&
                credentials.user_id == static_cast<std::uint64_t>(::geteuid())) {
                disconnects.fetch_add(1U);
            }
        });

    const Status started = server.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    IOTOX_CHECK(server.running());

    struct stat metadata {};
    IOTOX_CHECK(::lstat(config.socket_path.c_str(), &metadata) == 0);
    IOTOX_CHECK(S_ISSOCK(metadata.st_mode));
    IOTOX_CHECK(metadata.st_uid == ::geteuid());
    IOTOX_CHECK((metadata.st_mode & 0777) == 0600);

    auto connection = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    IOTOX_CHECK(connection.value().valid());
    const Status negative_timeout = connection.value().send(
        open_packet(0x1234U), std::chrono::milliseconds(-1));
    IOTOX_CHECK(!negative_timeout.ok());
    IOTOX_CHECK(negative_timeout.code() == ErrorCode::invalid_argument);
    IOTOX_CHECK_MSG(
        connection.value().send(open_packet(0x1234U), 500ms).ok(),
        "unable to send local terminal OPEN");

    auto opened = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().type == TerminalPacketType::opened);
    IOTOX_CHECK(opened.value().stream_id == 0x1234U);
    auto identity = iotox::local::decode_terminal_opened(opened.value().payload);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    IOTOX_CHECK(identity.value().incarnation == 7U);
    IOTOX_CHECK(observed_credentials.load());

    IOTOX_CHECK(connection.value()
                    .send(control_packet(TerminalPacketType::ping, 0x1234U), 500ms)
                    .ok());
    auto pong = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(pong.ok(), pong.status().message());
    IOTOX_CHECK(pong.value().type == TerminalPacketType::pong);
    IOTOX_CHECK(pong.value().stream_id == 0x1234U);

    IOTOX_CHECK(connection.value()
                    .send(control_packet(TerminalPacketType::detach, 0x1234U), 500ms)
                    .ok());
    auto trailing = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(trailing.ok(), trailing.status().message());
    IOTOX_CHECK(trailing.value().type == TerminalPacketType::output);
    IOTOX_CHECK(trailing.value().sequence == 1U);
    IOTOX_CHECK(std::string(
        trailing.value().payload.begin(), trailing.value().payload.end()) ==
        trailing_output);
    TerminalPacket acknowledgement;
    acknowledgement.type = TerminalPacketType::output_ack;
    acknowledgement.stream_id = 0x1234U;
    acknowledgement.sequence =
        1U + static_cast<std::uint64_t>(trailing_output.size());
    IOTOX_CHECK(connection.value().send(acknowledgement, 500ms).ok());

    auto detached = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(detached.ok(), detached.status().message());
    IOTOX_CHECK(detached.value().type == TerminalPacketType::detached);
    connection.value().close();
    IOTOX_CHECK(eventually([&] {
        return acknowledged_output.load() == acknowledgement.sequence &&
               disconnects.load() == 1U;
    }));
    server.stop();
    IOTOX_CHECK(!server.running());
    IOTOX_CHECK(!std::filesystem::exists(config.socket_path));
    remove_test_directory(directory);
}

IOTOX_TEST("terminal detach drain accepts only cumulative output acknowledgements") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("detach-ack-only");
    prepare_private_directory(directory);

    std::atomic<bool> opened_pending{false};
    std::atomic<bool> detached_pending{false};
    std::atomic<unsigned int> dispatched_pings{0U};
    std::atomic<unsigned int> disconnects{0U};

    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 1ms;
    config.detach_drain_timeout = 500ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            switch (packet.type) {
                case TerminalPacketType::open:
                    opened_pending.store(true);
                    return Status::success();
                case TerminalPacketType::detach:
                    detached_pending.store(true);
                    return Status::success();
                case TerminalPacketType::ping:
                    dispatched_pings.fetch_add(1U);
                    return Status::success();
                default:
                    return Status{ErrorCode::protocol_error,
                                  "unexpected packet in ACK-only drain test"};
            }
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            if (detached_pending.exchange(false)) {
                packets.push_back(
                    control_packet(TerminalPacketType::detached, 1U));
            }
            IOTOX_CHECK(packets.size() <= maximum_packets);
            return packets;
        },
        [&](std::uint64_t,
            const iotox::local::PeerCredentials &) {
            disconnects.fetch_add(1U);
        });

    IOTOX_CHECK_MSG(server.start().ok(), "unable to start ACK-only drain server");
    auto connection = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    IOTOX_CHECK(connection.value().send(open_packet(0x8822U), 500ms).ok());
    auto opened = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().type == TerminalPacketType::opened);

    IOTOX_CHECK(connection.value()
                    .send(control_packet(TerminalPacketType::detach, 0x8822U), 500ms)
                    .ok());
    // SOCK_SEQPACKET ordering guarantees this record follows DETACH. The
    // server must classify it inside the post-detach gate, not dispatch it to
    // the Agent handler as a fresh effect.
    IOTOX_CHECK(connection.value()
                    .send(control_packet(TerminalPacketType::ping, 0x8822U), 500ms)
                    .ok());

    auto detached = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(detached.ok(), detached.status().message());
    IOTOX_CHECK(detached.value().type == TerminalPacketType::detached);
    auto rejected = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(rejected.ok(), rejected.status().message());
    IOTOX_CHECK(rejected.value().type == TerminalPacketType::error);
    IOTOX_CHECK(rejected.value().status == ErrorCode::protocol_error);
    IOTOX_CHECK(dispatched_pings.load() == 0U);
    IOTOX_CHECK(eventually([&] { return disconnects.load() == 1U; }));

    connection.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server requires OPEN as the first packet") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("first-open");
    prepare_private_directory(directory);
    std::atomic<unsigned int> handled{0U};

    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto connection = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    IOTOX_CHECK(connection.value()
                    .send(control_packet(TerminalPacketType::ping, 99U), 500ms)
                    .ok());
    auto response = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(response.ok(), response.status().message());
    IOTOX_CHECK(response.value().type == TerminalPacketType::error);
    IOTOX_CHECK(response.value().status == ErrorCode::protocol_error);
    IOTOX_CHECK(handled.load() == 0U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server does not publish or disconnect a rejected OPEN") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("rejected-open");
    prepare_private_directory(directory);
    std::atomic<unsigned int> disconnects{0U};

    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [](const TerminalPacket &packet,
           const iotox::local::PeerCredentials &) {
            IOTOX_CHECK(packet.type == TerminalPacketType::open);
            return Status{ErrorCode::unavailable,
                          "test policy rejected local terminal OPEN"};
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            disconnects.fetch_add(1U);
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto connection = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    IOTOX_CHECK(connection.value().send(open_packet(100U), 500ms).ok());
    auto response = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(response.ok(), response.status().message());
    IOTOX_CHECK(response.value().type == TerminalPacketType::error);
    IOTOX_CHECK(response.value().status == ErrorCode::unavailable);
    IOTOX_CHECK(eventually([&] { return !server.client_connected(); }));
    IOTOX_CHECK(disconnects.load() == 0U);

    connection.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server rejects concurrent local attachments") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("one-client");
    prepare_private_directory(directory);
    std::atomic<bool> opened_pending{false};
    std::atomic<unsigned int> dispatched_opens{0U};

    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet, const iotox::local::PeerCredentials &) {
            if (packet.type == TerminalPacketType::open) {
                dispatched_opens.fetch_add(1U);
                opened_pending.store(true);
                return Status::success();
            }
            return Status::success();
        },
        [&](std::uint64_t, std::size_t) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            return packets;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto first = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    IOTOX_CHECK(first.value().send(open_packet(501U), 500ms).ok());
    auto opened = first.value().receive(500ms);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(eventually([&] { return server.client_connected(); }));

    auto second = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    IOTOX_CHECK(second.value().send(open_packet(777U), 500ms).ok());
    auto rejected = second.value().receive(500ms);
    IOTOX_CHECK_MSG(rejected.ok(), rejected.status().message());
    IOTOX_CHECK(rejected.value().type == TerminalPacketType::error);
    IOTOX_CHECK(rejected.value().stream_id == 777U);
    IOTOX_CHECK(rejected.value().status == ErrorCode::resource_exhausted);
    IOTOX_CHECK(std::string(
        rejected.value().payload.begin(), rejected.value().payload.end()) ==
        "another local terminal client is already attached");
    IOTOX_CHECK(dispatched_opens.load() == 1U);

    first.value().close();
    second.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("silent terminal contenders cannot delay an active stream") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("nonblocking-contender");
    prepare_private_directory(directory);

    std::atomic<bool> opened_pending{false};
    std::atomic<bool> pong_pending{false};
    std::atomic<unsigned int> dispatched{0U};
    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    config.contender_open_timeout = 400ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            dispatched.fetch_add(1U);
            if (packet.type == TerminalPacketType::open) {
                opened_pending.store(true);
                return Status::success();
            }
            if (packet.type == TerminalPacketType::ping) {
                pong_pending.store(true);
                return Status::success();
            }
            return Status{ErrorCode::protocol_error,
                          "unexpected packet in contender latency test"};
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            if (pong_pending.exchange(false)) {
                packets.push_back(control_packet(TerminalPacketType::pong, 1U));
            }
            IOTOX_CHECK(packets.size() <= maximum_packets);
            return packets;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto active = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(active.ok(), active.status().message());
    IOTOX_CHECK(active.value().send(open_packet(8501U), 500ms).ok());
    auto opened = active.value().receive(500ms);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().type == TerminalPacketType::opened);

    auto silent = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(silent.ok(), silent.status().message());
    std::this_thread::sleep_for(30ms);

    const auto begin = std::chrono::steady_clock::now();
    IOTOX_CHECK(active.value().send(
        control_packet(TerminalPacketType::ping, 8501U), 500ms).ok());
    auto pong = active.value().receive(200ms);
    const auto elapsed = std::chrono::steady_clock::now() - begin;
    IOTOX_CHECK_MSG(pong.ok(), pong.status().message());
    IOTOX_CHECK(pong.value().type == TerminalPacketType::pong);
    IOTOX_CHECK(pong.value().stream_id == 8501U);
    IOTOX_CHECK(elapsed < 200ms);
    IOTOX_CHECK(dispatched.load() == 2U);

    auto rejected = silent.value().receive(800ms);
    IOTOX_CHECK_MSG(rejected.ok(), rejected.status().message());
    IOTOX_CHECK(rejected.value().type == TerminalPacketType::error);
    IOTOX_CHECK(rejected.value().status == ErrorCode::resource_exhausted);
    IOTOX_CHECK(std::string(
        rejected.value().payload.begin(), rejected.value().payload.end()) ==
        "another local terminal client is already attached");
    IOTOX_CHECK(dispatched.load() == 2U);

    active.value().close();
    silent.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal contender admission is bounded per process") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("contender-process-bound");
    prepare_private_directory(directory);

    std::atomic<bool> opened_pending{false};
    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    config.contender_open_timeout = 300ms;
    config.maximum_pending_contenders = 4U;
    config.maximum_pending_contenders_per_process = 1U;
    config.maximum_contender_accepts_per_interval = 4U;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            if (packet.type == TerminalPacketType::open) {
                opened_pending.store(true);
                return Status::success();
            }
            return Status::success();
        },
        [&](std::uint64_t, std::size_t) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            return packets;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto active = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(active.ok(), active.status().message());
    IOTOX_CHECK(active.value().send(open_packet(8601U), 500ms).ok());
    auto opened = active.value().receive(500ms);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().type == TerminalPacketType::opened);

    auto first = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    std::this_thread::sleep_for(20ms);
    auto second = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    auto quota = second.value().receive(500ms);
    IOTOX_CHECK_MSG(quota.ok(), quota.status().message());
    IOTOX_CHECK(quota.value().type == TerminalPacketType::error);
    IOTOX_CHECK(quota.value().status == ErrorCode::resource_exhausted);
    IOTOX_CHECK(std::string(
        quota.value().payload.begin(), quota.value().payload.end()) ==
        "local terminal per-process contender limit is full");

    auto first_rejected = first.value().receive(700ms);
    IOTOX_CHECK_MSG(first_rejected.ok(), first_rejected.status().message());
    IOTOX_CHECK(first_rejected.value().status == ErrorCode::resource_exhausted);

    active.value().close();
    first.value().close();
    second.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server admits a queued successor after active client death") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("queued-successor");
    prepare_private_directory(directory);

    std::atomic<unsigned int> opens{0U};
    std::atomic<unsigned int> disconnects{0U};
    std::atomic<bool> opened_pending{false};
    std::atomic<bool> ping_handler_entered{false};
    std::atomic<bool> release_ping_handler{false};

    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            if (packet.type == TerminalPacketType::open) {
                opens.fetch_add(1U);
                opened_pending.store(true);
                return Status::success();
            }
            if (packet.type == TerminalPacketType::ping) {
                ping_handler_entered.store(true);
                while (!release_ping_handler.load()) {
                    std::this_thread::yield();
                }
            }
            return Status::success();
        },
        [&](std::uint64_t, std::size_t) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            return packets;
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            disconnects.fetch_add(1U);
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto active = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(active.ok(), active.status().message());
    IOTOX_CHECK(active.value().send(open_packet(801U), 500ms).ok());
    auto first_opened = active.value().receive(500ms);
    IOTOX_CHECK_MSG(first_opened.ok(), first_opened.status().message());
    IOTOX_CHECK(first_opened.value().type == TerminalPacketType::opened);
    IOTOX_CHECK(first_opened.value().stream_id == 801U);

    IOTOX_CHECK(active.value().send(
        control_packet(TerminalPacketType::ping, 801U), 500ms).ok());
    IOTOX_CHECK(eventually([&] { return ping_handler_entered.load(); }));

    auto successor = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().send(open_packet(802U), 500ms).ok());
    active.value().close();
    release_ping_handler.store(true);

    auto replacement_opened = successor.value().receive(1000ms);
    IOTOX_CHECK_MSG(
        replacement_opened.ok(), replacement_opened.status().message());
    IOTOX_CHECK(replacement_opened.value().type == TerminalPacketType::opened);
    IOTOX_CHECK(replacement_opened.value().stream_id == 802U);
    IOTOX_CHECK(opens.load() == 2U);
    IOTOX_CHECK(eventually([&] { return disconnects.load() >= 1U; }));

    successor.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server expires a silent OPEN lease and accepts a successor") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("open-timeout");
    prepare_private_directory(directory);

    std::atomic<unsigned int> opens{0U};
    std::atomic<unsigned int> disconnects{0U};
    std::atomic<bool> opened_pending{false};
    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    config.open_timeout = 40ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            IOTOX_CHECK(packet.type == TerminalPacketType::open);
            opens.fetch_add(1U);
            opened_pending.store(true);
            return Status::success();
        },
        [&](std::uint64_t, std::size_t) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            return packets;
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            disconnects.fetch_add(1U);
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto silent = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(silent.ok(), silent.status().message());
    auto expired = silent.value().receive(500ms);
    IOTOX_CHECK_MSG(expired.ok(), expired.status().message());
    IOTOX_CHECK(expired.value().type == TerminalPacketType::error);
    IOTOX_CHECK(expired.value().status == ErrorCode::timeout);
    IOTOX_CHECK(std::string(
        expired.value().payload.begin(), expired.value().payload.end()) ==
        "local terminal OPEN deadline elapsed before the first packet");
    IOTOX_CHECK(eventually([&] { return !server.client_connected(); }));
    IOTOX_CHECK(opens.load() == 0U);
    IOTOX_CHECK(disconnects.load() == 0U);
    silent.value().close();

    auto successor = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().send(open_packet(601U), 500ms).ok());
    auto opened = successor.value().receive(500ms);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().type == TerminalPacketType::opened);
    IOTOX_CHECK(opened.value().stream_id == 601U);
    IOTOX_CHECK(opens.load() == 1U);

    successor.value().close();
    IOTOX_CHECK(eventually([&] { return disconnects.load() == 1U; }));
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server cannot steal an active socket path") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("active-owner");
    prepare_private_directory(directory);

    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    const auto packet_handler = [](const TerminalPacket &,
                                   const iotox::local::PeerCredentials &) {
        return Status::success();
    };
    const auto drain_handler = [](std::uint64_t, std::size_t) {
        return std::vector<TerminalPacket>{};
    };
    TerminalServer first(config, packet_handler, drain_handler);
    IOTOX_CHECK_MSG(first.start().ok(), "first terminal server did not start");

    struct stat before {};
    IOTOX_CHECK(::lstat(config.socket_path.c_str(), &before) == 0);
    TerminalServer second(config, packet_handler, drain_handler);
    const Status second_start = second.start();
    IOTOX_CHECK(!second_start.ok());
    IOTOX_CHECK(second_start.code() == ErrorCode::resource_exhausted);

    struct stat after {};
    IOTOX_CHECK(::lstat(config.socket_path.c_str(), &after) == 0);
    IOTOX_CHECK(before.st_dev == after.st_dev);
    IOTOX_CHECK(before.st_ino == after.st_ino);
    IOTOX_CHECK(first.running());

    first.stop();
    IOTOX_CHECK(!std::filesystem::exists(config.socket_path));
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server reclaims a stale owned seqpacket path") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("stale");
    prepare_private_directory(directory);
    const std::filesystem::path socket_path = directory / "terminal.sock";
    const int stale = bind_raw_seqpacket(socket_path, false);
    IOTOX_CHECK(::chmod(socket_path.c_str(), 0700) == 0);
    IOTOX_CHECK(::close(stale) == 0);

    TerminalServer::Config config;
    config.socket_path = socket_path;
    TerminalServer server(
        config,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    const Status started = server.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());

    struct stat live_metadata {};
    IOTOX_CHECK(::lstat(socket_path.c_str(), &live_metadata) == 0);
    IOTOX_CHECK(S_ISSOCK(live_metadata.st_mode));
    IOTOX_CHECK((live_metadata.st_mode & 0777) == 0600);
    auto connection = TerminalConnection::connect(socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    connection.value().close();

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server refuses a non-socket occupant and public parent") {
    const std::filesystem::path occupied_directory =
        terminal_socket_test_directory("occupied");
    prepare_private_directory(occupied_directory);
    const std::filesystem::path occupied = occupied_directory / "terminal.sock";
    {
        std::ofstream output(occupied);
        output << "do-not-replace\n";
    }

    TerminalServer::Config occupied_config;
    occupied_config.socket_path = occupied;
    TerminalServer occupied_server(
        occupied_config,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    const Status occupied_start = occupied_server.start();
    IOTOX_CHECK(!occupied_start.ok());
    IOTOX_CHECK(std::filesystem::is_regular_file(occupied));
    remove_test_directory(occupied_directory);

    const std::filesystem::path public_directory =
        terminal_socket_test_directory("public-parent");
    prepare_private_directory(public_directory);
    IOTOX_CHECK(::chmod(public_directory.c_str(), 0755) == 0);
    TerminalServer::Config public_config;
    public_config.socket_path = public_directory / "terminal.sock";
    TerminalServer public_server(
        public_config,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    const Status public_start = public_server.start();
    IOTOX_CHECK(!public_start.ok());
    IOTOX_CHECK(public_start.code() == ErrorCode::io_error);
    auto public_connect = TerminalConnection::connect(public_config.socket_path, 50ms);
    IOTOX_CHECK(!public_connect.ok());
    IOTOX_CHECK(public_connect.status().code() == ErrorCode::io_error);
    remove_test_directory(public_directory);
}

IOTOX_TEST("terminal server stop preserves a replacement socket inode") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("replacement");
    prepare_private_directory(directory);
    const std::filesystem::path socket_path = directory / "terminal.sock";

    TerminalServer::Config config;
    config.socket_path = socket_path;
    TerminalServer server(
        config,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    struct stat original {};
    IOTOX_CHECK(::lstat(socket_path.c_str(), &original) == 0);
    IOTOX_CHECK(::unlink(socket_path.c_str()) == 0);
    const int replacement = bind_raw_seqpacket(socket_path, true);
    struct stat replacement_metadata {};
    IOTOX_CHECK(::lstat(socket_path.c_str(), &replacement_metadata) == 0);
    IOTOX_CHECK(original.st_ino != replacement_metadata.st_ino);

    server.stop();
    struct stat after_stop {};
    IOTOX_CHECK(::lstat(socket_path.c_str(), &after_stop) == 0);
    IOTOX_CHECK(after_stop.st_dev == replacement_metadata.st_dev);
    IOTOX_CHECK(after_stop.st_ino == replacement_metadata.st_ino);

    IOTOX_CHECK(::close(replacement) == 0);
    IOTOX_CHECK(::unlink(socket_path.c_str()) == 0);
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server rejects unusable socket modes and repeated start") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("configuration");
    prepare_private_directory(directory);

    TerminalServer::Config invalid;
    invalid.socket_path = directory / "invalid.sock";
    invalid.socket_mode = 0400U;
    TerminalServer invalid_server(
        invalid,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    const Status invalid_start = invalid_server.start();
    IOTOX_CHECK(!invalid_start.ok());
    IOTOX_CHECK(invalid_start.code() == ErrorCode::invalid_argument);

    TerminalServer::Config no_open_lease;
    no_open_lease.socket_path = directory / "no-open-lease.sock";
    no_open_lease.open_timeout = 0ms;
    TerminalServer no_open_lease_server(
        no_open_lease,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    const Status no_open_lease_start = no_open_lease_server.start();
    IOTOX_CHECK(!no_open_lease_start.ok());
    IOTOX_CHECK(no_open_lease_start.code() == ErrorCode::invalid_argument);

    TerminalServer::Config no_detach_drain;
    no_detach_drain.socket_path = directory / "no-detach-drain.sock";
    no_detach_drain.detach_drain_timeout = 0ms;
    TerminalServer no_detach_drain_server(
        no_detach_drain,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    const Status no_detach_drain_start = no_detach_drain_server.start();
    IOTOX_CHECK(!no_detach_drain_start.ok());
    IOTOX_CHECK(no_detach_drain_start.code() == ErrorCode::invalid_argument);

    TerminalServer::Config excessive_detach_drain;
    excessive_detach_drain.socket_path =
        directory / "excessive-detach-drain.sock";
    excessive_detach_drain.detach_drain_timeout = 5001ms;
    TerminalServer excessive_detach_drain_server(
        excessive_detach_drain,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    const Status excessive_detach_drain_start =
        excessive_detach_drain_server.start();
    IOTOX_CHECK(!excessive_detach_drain_start.ok());
    IOTOX_CHECK(
        excessive_detach_drain_start.code() == ErrorCode::invalid_argument);

    TerminalServer::Config excessive_open_lease;
    excessive_open_lease.socket_path = directory / "excessive-open-lease.sock";
    excessive_open_lease.open_timeout = 60001ms;
    TerminalServer excessive_open_lease_server(
        excessive_open_lease,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    const Status excessive_open_lease_start = excessive_open_lease_server.start();
    IOTOX_CHECK(!excessive_open_lease_start.ok());
    IOTOX_CHECK(
        excessive_open_lease_start.code() == ErrorCode::invalid_argument);

    TerminalServer::Config no_contender_lease;
    no_contender_lease.socket_path = directory / "no-contender-lease.sock";
    no_contender_lease.contender_open_timeout = 0ms;
    TerminalServer no_contender_lease_server(
        no_contender_lease,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    const Status no_contender_lease_start = no_contender_lease_server.start();
    IOTOX_CHECK(!no_contender_lease_start.ok());
    IOTOX_CHECK(
        no_contender_lease_start.code() == ErrorCode::invalid_argument);

    TerminalServer::Config bad_contender_process_limit;
    bad_contender_process_limit.socket_path =
        directory / "bad-contender-process-limit.sock";
    bad_contender_process_limit.maximum_pending_contenders = 2U;
    bad_contender_process_limit.maximum_pending_contenders_per_process = 3U;
    TerminalServer bad_contender_process_limit_server(
        bad_contender_process_limit,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    const Status bad_contender_process_limit_start =
        bad_contender_process_limit_server.start();
    IOTOX_CHECK(!bad_contender_process_limit_start.ok());
    IOTOX_CHECK(
        bad_contender_process_limit_start.code() ==
        ErrorCode::invalid_argument);

    TerminalServer::Config no_contender_admission_interval;
    no_contender_admission_interval.socket_path =
        directory / "no-contender-admission-interval.sock";
    no_contender_admission_interval.contender_admission_interval = 0ms;
    TerminalServer no_contender_admission_interval_server(
        no_contender_admission_interval,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    const Status no_contender_admission_interval_start =
        no_contender_admission_interval_server.start();
    IOTOX_CHECK(!no_contender_admission_interval_start.ok());
    IOTOX_CHECK(
        no_contender_admission_interval_start.code() ==
        ErrorCode::invalid_argument);

    TerminalServer::Config relative;
    relative.socket_path = "relative-terminal.sock";
    TerminalServer relative_server(
        relative,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    const Status relative_start = relative_server.start();
    IOTOX_CHECK(!relative_start.ok());
    IOTOX_CHECK(relative_start.code() == ErrorCode::invalid_argument);
    IOTOX_CHECK(!std::filesystem::exists(relative.socket_path));

    auto relative_connect = TerminalConnection::connect(
        relative.socket_path, 50ms);
    IOTOX_CHECK(!relative_connect.ok());
    IOTOX_CHECK(relative_connect.status().code() == ErrorCode::invalid_argument);

    const std::string embedded_nul_text(
        "/tmp/iotox-terminal\0hidden.sock", 31U);
    auto embedded_nul = TerminalConnection::connect(
        std::filesystem::path{embedded_nul_text}, 50ms);
    IOTOX_CHECK(!embedded_nul.ok());
    IOTOX_CHECK(embedded_nul.status().code() == ErrorCode::invalid_argument);

    TerminalServer::Config valid;
    valid.socket_path = directory / "valid.sock";
    TerminalServer server(
        valid,
        [](const TerminalPacket &, const iotox::local::PeerCredentials &) {
            return Status::success();
        },
        [](std::uint64_t, std::size_t) { return std::vector<TerminalPacket>{}; });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");
    const Status repeated = server.start();
    IOTOX_CHECK(!repeated.ok());
    IOTOX_CHECK(repeated.code() == ErrorCode::invalid_argument);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server callback stop and concurrent cleanup are deadlock free") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("callback-stop");
    prepare_private_directory(directory);

    std::atomic<bool> callback_entered{false};
    std::atomic<bool> callback_returned{false};
    TerminalServer *server_address = nullptr;
    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            IOTOX_CHECK(packet.type == TerminalPacketType::open);
            callback_entered.store(true);
            IOTOX_CHECK(server_address != nullptr);
            server_address->stop();
            callback_returned.store(true);
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    server_address = &server;
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto connection = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    IOTOX_CHECK(connection.value().send(open_packet(7001U), 500ms).ok());
    IOTOX_CHECK(eventually([&] { return callback_entered.load(); }));
    IOTOX_CHECK(eventually([&] { return callback_returned.load(); }));
    IOTOX_CHECK(eventually([&] { return !server.running(); }));

    std::atomic<bool> keep_notifying{true};
    std::thread notifier([&] {
        while (keep_notifying.load()) {
            server.notify();
            std::this_thread::yield();
        }
    });
    std::array<std::thread, 4U> stoppers{
        std::thread([&] { server.stop(); }),
        std::thread([&] { server.stop(); }),
        std::thread([&] { server.stop(); }),
        std::thread([&] { server.stop(); }),
    };
    for (std::thread &stopper : stoppers) stopper.join();
    keep_notifying.store(false);
    notifier.join();

    connection.value().close();
    IOTOX_CHECK(!server.running());
    IOTOX_CHECK(!server.client_connected());
    IOTOX_CHECK(!std::filesystem::exists(config.socket_path));
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server rejects records sent through a fork-inherited controller socket") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("fork-inherited-sender");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    std::atomic<unsigned int> disconnects{0U};
    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &credentials) {
            IOTOX_CHECK(
                credentials.process_id ==
                static_cast<std::int64_t>(::getpid()));
            IOTOX_CHECK(
                packet.type == TerminalPacketType::open ||
                packet.type == TerminalPacketType::ping);
            handled.fetch_add(1U);
            return Status::success();
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &) {
            disconnects.fetch_add(1U);
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto connection = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    IOTOX_CHECK(connection.value().send(open_packet(8101U), 500ms).ok());
    IOTOX_CHECK(eventually([&] { return handled.load() == 1U; }));

    auto encoded_ping = iotox::local::encode_terminal_packet(
        control_packet(TerminalPacketType::ping, 8101U));
    IOTOX_CHECK_MSG(encoded_ping.ok(), encoded_ping.status().message());
    int release_gate[2]{-1, -1};
    IOTOX_CHECK(::pipe2(release_gate, O_CLOEXEC) == 0);
    const pid_t child = ::fork();
    IOTOX_CHECK(child >= 0);
    if (child == 0) {
        static_cast<void>(::close(release_gate[1]));
        const ssize_t count = ::send(
            connection.value().native_handle(),
            encoded_ping.value().data(), encoded_ping.value().size(),
            MSG_NOSIGNAL);
        if (count < 0 ||
            static_cast<std::size_t>(count) != encoded_ping.value().size()) {
            ::_exit(1);
        }
        char release = '\0';
        const ssize_t release_count = ::read(
            release_gate[0], &release, sizeof(release));
        ::_exit(release_count == 1 && release == 'x' ? 0 : 2);
    }
    IOTOX_CHECK(::close(release_gate[0]) == 0);
    release_gate[0] = -1;

    auto denial = connection.value().receive(500ms);
    IOTOX_CHECK(::write(release_gate[1], "x", 1U) == 1);
    IOTOX_CHECK(::close(release_gate[1]) == 0);
    release_gate[1] = -1;
    int child_status = 0;
    IOTOX_CHECK(::waitpid(child, &child_status, 0) == child);
    IOTOX_CHECK(WIFEXITED(child_status));
    IOTOX_CHECK(WEXITSTATUS(child_status) == 0);

    IOTOX_CHECK_MSG(denial.ok(), denial.status().message());
    IOTOX_CHECK(denial.value().type == TerminalPacketType::error);
    IOTOX_CHECK_MSG(
        denial.value().status == ErrorCode::unavailable,
        "status=" +
            std::to_string(static_cast<int>(denial.value().status)) +
            " detail=" + std::string(
                denial.value().payload.begin(), denial.value().payload.end()));
    IOTOX_CHECK(handled.load() == 1U);
    IOTOX_CHECK(eventually([&] {
        return !server.client_connected() && disconnects.load() == 1U;
    }));

    auto successor = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().send(open_packet(8102U), 500ms).ok());
    IOTOX_CHECK(eventually([&] { return handled.load() == 2U; }));
    successor.value().close();
    connection.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server closes injected rights and never dispatches their record") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("ancillary-rights");
    prepare_private_directory(directory);

    std::atomic<unsigned int> opens{0U};
    std::atomic<unsigned int> pings{0U};
    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            if (packet.type == TerminalPacketType::open) {
                opens.fetch_add(1U);
                return Status::success();
            }
            if (packet.type == TerminalPacketType::ping) {
                pings.fetch_add(1U);
                return Status::success();
            }
            return Status{ErrorCode::protocol_error, "unexpected test packet"};
        },
        [](std::uint64_t, std::size_t) {
            return std::vector<TerminalPacket>{};
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    auto connection = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    IOTOX_CHECK(connection.value().send(open_packet(8201U), 500ms).ok());
    IOTOX_CHECK(eventually([&] { return opens.load() == 1U; }));

    int pipe_descriptors[2]{-1, -1};
    IOTOX_CHECK(::pipe2(pipe_descriptors, O_CLOEXEC | O_NONBLOCK) == 0);
    auto encoded_ping = iotox::local::encode_terminal_packet(
        control_packet(TerminalPacketType::ping, 8201U));
    IOTOX_CHECK_MSG(encoded_ping.ok(), encoded_ping.status().message());
    IOTOX_CHECK(send_record_with_descriptor(
        connection.value().native_handle(), encoded_ping.value(),
        pipe_descriptors[1]));
    IOTOX_CHECK(::close(pipe_descriptors[1]) == 0);
    pipe_descriptors[1] = -1;

    auto denial = connection.value().receive(500ms);
    IOTOX_CHECK_MSG(denial.ok(), denial.status().message());
    IOTOX_CHECK(denial.value().type == TerminalPacketType::error);
    IOTOX_CHECK(denial.value().status == ErrorCode::protocol_error);
    IOTOX_CHECK(pings.load() == 0U);
    IOTOX_CHECK(eventually([&] {
        std::uint8_t byte = 0U;
        const ssize_t count = ::read(pipe_descriptors[0], &byte, sizeof(byte));
        return count == 0;
    }));

    IOTOX_CHECK(::close(pipe_descriptors[0]) == 0);
    connection.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server releases a silent inherited socket when its connector exits") {
    if (!peer_pidfd_supported()) return;

    const std::filesystem::path directory =
        terminal_socket_test_directory("connection-pidfd-exit");
    prepare_private_directory(directory);

    std::atomic<unsigned int> opens{0U};
    std::atomic<bool> opened_pending{false};
    TerminalServer::Config config;
    config.socket_path = directory / "terminal.sock";
    config.poll_interval = 2ms;
    config.open_timeout = 2000ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &) {
            if (packet.type != TerminalPacketType::open) {
                return Status{
                    ErrorCode::protocol_error,
                    "unexpected packet in connection pidfd test"};
            }
            opens.fetch_add(1U);
            opened_pending.store(true);
            return Status::success();
        },
        [&](std::uint64_t, std::size_t) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) {
                packets.push_back(opened_packet());
            }
            return packets;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");

    int transfer[2]{-1, -1};
    int release_gate[2]{-1, -1};
    IOTOX_CHECK(::socketpair(
                    AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC,
                    0, transfer) == 0);
    IOTOX_CHECK(::pipe2(release_gate, O_CLOEXEC) == 0);

    const pid_t connector = ::fork();
    IOTOX_CHECK(connector >= 0);
    if (connector == 0) {
        static_cast<void>(::close(transfer[0]));
        static_cast<void>(::close(release_gate[1]));
        auto connection = TerminalConnection::connect(config.socket_path, 500ms);
        if (!connection) ::_exit(10);
        const std::array<std::uint8_t, 1U> marker{{0xA7U}};
        if (!send_record_with_descriptor(
                transfer[1], marker,
                connection.value().native_handle())) {
            ::_exit(11);
        }
        char release = '\0';
        const ssize_t count = ::read(
            release_gate[0], &release, sizeof(release));
        ::_exit(count == 1 && release == 'x' ? 0 : 12);
    }

    IOTOX_CHECK(::close(transfer[1]) == 0);
    transfer[1] = -1;
    IOTOX_CHECK(::close(release_gate[0]) == 0);
    release_gate[0] = -1;
    char marker = '\0';
    const int inherited = receive_passed_descriptor(transfer[0], marker);
    IOTOX_CHECK(inherited >= 0);
    IOTOX_CHECK(static_cast<unsigned char>(marker) == 0xA7U);
    IOTOX_CHECK(eventually([&] { return server.client_connected(); }, 500ms));
    IOTOX_CHECK(opens.load() == 0U);

    const auto exited_at = std::chrono::steady_clock::now();
    IOTOX_CHECK(::write(release_gate[1], "x", 1U) == 1);
    IOTOX_CHECK(::close(release_gate[1]) == 0);
    release_gate[1] = -1;
    int connector_status = 0;
    IOTOX_CHECK(::waitpid(connector, &connector_status, 0) == connector);
    IOTOX_CHECK(WIFEXITED(connector_status));
    IOTOX_CHECK(WEXITSTATUS(connector_status) == 0);

    IOTOX_CHECK(descriptor_readable_within(inherited, 750ms));
    IOTOX_CHECK(eventually(
        [&] { return !server.client_connected(); }, 750ms));
    IOTOX_CHECK(
        std::chrono::steady_clock::now() - exited_at < 1500ms);
    IOTOX_CHECK(opens.load() == 0U);
    IOTOX_CHECK(::close(inherited) == 0);
    IOTOX_CHECK(::close(transfer[0]) == 0);

    auto successor = TerminalConnection::connect(config.socket_path, 500ms);
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().send(open_packet(8251U), 500ms).ok());
    auto opened = successor.value().receive(500ms);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().type == TerminalPacketType::opened);
    IOTOX_CHECK(opened.value().stream_id == 8251U);
    IOTOX_CHECK(opens.load() == 1U);

    successor.value().close();
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal server releases a passed socket when its bound process exits") {
    if (!runtime_has_pidfd_open()) return;

    const std::filesystem::path directory =
        terminal_socket_test_directory("owner-pidfd-exit");
    prepare_private_directory(directory);
    const std::filesystem::path socket_path = directory / "terminal.sock";
    const TerminalPacket child_open = open_packet(8301U);

    int transfer[2]{-1, -1};
    int start_gate[2]{-1, -1};
    IOTOX_CHECK(::socketpair(
                    AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC,
                    0, transfer) == 0);
    IOTOX_CHECK(::pipe2(start_gate, O_CLOEXEC) == 0);

    const pid_t child = ::fork();
    IOTOX_CHECK(child >= 0);
    if (child == 0) {
        static_cast<void>(::close(transfer[0]));
        static_cast<void>(::close(start_gate[1]));
        char start = '\0';
        if (::read(start_gate[0], &start, sizeof(start)) != 1) ::_exit(10);
        auto connection = TerminalConnection::connect(socket_path, 1000ms);
        if (!connection) {
            const char marker = 'E';
            static_cast<void>(::send(transfer[1], &marker, 1U, MSG_NOSIGNAL));
            ::_exit(11);
        }
        if (!connection.value().send(child_open, 1000ms).ok()) {
            const char marker = 'E';
            static_cast<void>(::send(transfer[1], &marker, 1U, MSG_NOSIGNAL));
            ::_exit(12);
        }
        auto opened = connection.value().receive(1000ms);
        if (!opened || opened.value().type != TerminalPacketType::opened) {
            const char marker = 'E';
            static_cast<void>(::send(transfer[1], &marker, 1U, MSG_NOSIGNAL));
            ::_exit(13);
        }
        const std::array<std::uint8_t, 1U> marker{{'F'}};
        if (!send_record_with_descriptor(
                transfer[1], marker, connection.value().native_handle())) {
            ::_exit(14);
        }
        ::_exit(0);
    }

    static_cast<void>(::close(transfer[1]));
    transfer[1] = -1;
    static_cast<void>(::close(start_gate[0]));
    start_gate[0] = -1;

    std::atomic<unsigned int> opens{0U};
    std::atomic<unsigned int> disconnects{0U};
    std::atomic<bool> opened_pending{false};
    TerminalServer::Config config;
    config.socket_path = socket_path;
    config.poll_interval = 2ms;
    TerminalServer server(
        config,
        [&](const TerminalPacket &packet,
            const iotox::local::PeerCredentials &credentials) {
            IOTOX_CHECK(packet.type == TerminalPacketType::open);
            const unsigned int prior_opens = opens.load();
            IOTOX_CHECK(
                credentials.process_id ==
                (prior_opens == 0U
                     ? static_cast<std::int64_t>(child)
                     : static_cast<std::int64_t>(::getpid())));
            opens.fetch_add(1U);
            opened_pending.store(true);
            return Status::success();
        },
        [&](std::uint64_t, std::size_t maximum_packets) {
            std::vector<TerminalPacket> packets;
            if (opened_pending.exchange(false)) packets.push_back(opened_packet());
            IOTOX_CHECK(packets.size() <= maximum_packets);
            return packets;
        },
        [&](std::uint64_t, const iotox::local::PeerCredentials &credentials) {
            if (credentials.process_id == static_cast<std::int64_t>(child)) {
                disconnects.fetch_add(1U);
            }
        });
    IOTOX_CHECK_MSG(server.start().ok(), "terminal server did not start");
    const char start = 'S';
    IOTOX_CHECK(::write(start_gate[1], &start, sizeof(start)) == 1);
    IOTOX_CHECK(::close(start_gate[1]) == 0);
    start_gate[1] = -1;

    IOTOX_CHECK(descriptor_readable_within(transfer[0], 2000ms));
    char marker = '\0';
    const int held_socket = receive_passed_descriptor(transfer[0], marker);
    IOTOX_CHECK(marker == 'F');
    IOTOX_CHECK(held_socket >= 0);

    int child_status = 0;
    IOTOX_CHECK(::waitpid(child, &child_status, 0) == child);
    IOTOX_CHECK(WIFEXITED(child_status));
    IOTOX_CHECK(WEXITSTATUS(child_status) == 0);
    IOTOX_CHECK(eventually([&] { return opens.load() == 1U; }));
    IOTOX_CHECK(eventually(
        [&] {
            return disconnects.load() == 1U && !server.client_connected();
        },
        1500ms));

    auto successor = TerminalConnection::connect(socket_path, 500ms);
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().send(open_packet(8302U), 500ms).ok());
    IOTOX_CHECK(eventually([&] { return opens.load() == 2U; }));

    successor.value().close();
    IOTOX_CHECK(::close(held_socket) == 0);
    IOTOX_CHECK(::close(transfer[0]) == 0);
    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("terminal client closes injected response rights and rejects the record") {
    const std::filesystem::path directory =
        terminal_socket_test_directory("response-ancillary-rights");
    prepare_private_directory(directory);
    const std::filesystem::path socket_path = directory / "terminal.sock";
    const int listener = bind_raw_seqpacket(socket_path, true);
    IOTOX_CHECK(::chmod(socket_path.c_str(), 0600) == 0);

    int pipe_descriptors[2]{-1, -1};
    IOTOX_CHECK(::pipe2(pipe_descriptors, O_CLOEXEC | O_NONBLOCK) == 0);
    std::atomic<bool> sent{false};
    std::thread responder([&] {
        const int accepted = ::accept4(listener, nullptr, nullptr, SOCK_CLOEXEC);
        IOTOX_CHECK(accepted >= 0);
        TerminalPacket response = opened_packet();
        response.stream_id = 4701U;
        auto encoded = iotox::local::encode_terminal_packet(response);
        IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
        IOTOX_CHECK(send_record_with_descriptor(
            accepted, encoded.value(), pipe_descriptors[1]));
        sent.store(true);
        IOTOX_CHECK(::close(pipe_descriptors[1]) == 0);
        pipe_descriptors[1] = -1;
        IOTOX_CHECK(::close(accepted) == 0);
    });

    auto connection = TerminalConnection::connect(socket_path, 1000ms);
    IOTOX_CHECK_MSG(connection.ok(), connection.status().message());
    auto denied = connection.value().receive(1000ms);
    IOTOX_CHECK(!denied.ok());
    IOTOX_CHECK(denied.status().code() == ErrorCode::protocol_error);

    responder.join();
    IOTOX_CHECK(sent.load());
    IOTOX_CHECK(eventually([&] {
        std::uint8_t byte = 0U;
        const ssize_t count = ::read(pipe_descriptors[0], &byte, sizeof(byte));
        return count == 0;
    }));

    IOTOX_CHECK(::close(pipe_descriptors[0]) == 0);
    connection.value().close();
    IOTOX_CHECK(::close(listener) == 0);
    IOTOX_CHECK(::unlink(socket_path.c_str()) == 0);
    remove_test_directory(directory);
}
