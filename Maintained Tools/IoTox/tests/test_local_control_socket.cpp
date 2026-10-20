#include "iotox/local/control_socket.hpp"
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
#include <sys/un.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

std::filesystem::path socket_test_directory(std::string_view) {
    static std::atomic<unsigned int> sequence{0U};
    return std::filesystem::temp_directory_path() /
           ("ic-" + std::to_string(static_cast<long long>(::getpid())) + "-" +
            std::to_string(sequence.fetch_add(1U)));
}

bool eventually(
    const std::function<bool()> &predicate,
    std::chrono::milliseconds timeout = std::chrono::milliseconds(1000)) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    do {
        if (predicate()) return true;
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    } while (std::chrono::steady_clock::now() < deadline);
    return predicate();
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

int connect_raw_seqpacket(const std::filesystem::path &path) {
    const std::string text = path.string();
    IOTOX_CHECK(text.size() < sizeof(sockaddr_un::sun_path));
    const int descriptor = ::socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
    IOTOX_CHECK(descriptor >= 0);
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    std::memcpy(address.sun_path, text.c_str(), text.size() + 1U);
    IOTOX_CHECK(::connect(
                    descriptor,
                    reinterpret_cast<const sockaddr *>(&address),
                    sizeof(address)) == 0);
    return descriptor;
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

iotox::local::ControlPacket receive_control_packet(
    int descriptor,
    std::chrono::milliseconds timeout = std::chrono::milliseconds(500)) {
    struct pollfd poll_descriptor {descriptor, POLLIN, 0};
    int ready = -1;
    do {
        ready = ::poll(
            &poll_descriptor, 1U, static_cast<int>(timeout.count()));
    } while (ready < 0 && errno == EINTR);
    IOTOX_CHECK(ready > 0);
    IOTOX_CHECK(
        (poll_descriptor.revents & (POLLIN | POLLHUP)) != 0);
    std::vector<std::uint8_t> bytes(iotox::local::kControlMaxPacketSize + 1U);
    const ssize_t count = ::recv(
        descriptor, bytes.data(), bytes.size(), 0);
    IOTOX_CHECK(count > 0);
    IOTOX_CHECK(
        static_cast<std::size_t>(count) <= iotox::local::kControlMaxPacketSize);
    bytes.resize(static_cast<std::size_t>(count));
    auto packet = iotox::local::decode_control_packet(bytes);
    IOTOX_CHECK_MSG(packet.ok(), packet.status().message());
    return std::move(packet.value());
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

int receive_passed_descriptor(int socket_descriptor) {
    std::uint8_t payload = 0U;
    struct iovec vector {};
    vector.iov_base = &payload;
    vector.iov_len = sizeof(payload);
    alignas(cmsghdr) std::array<std::byte, CMSG_SPACE(sizeof(int))> control{};
    struct msghdr message {};
    message.msg_iov = &vector;
    message.msg_iovlen = 1U;
    message.msg_control = control.data();
    message.msg_controllen = control.size();
    const ssize_t count = ::recvmsg(
        socket_descriptor, &message, MSG_CMSG_CLOEXEC);
    IOTOX_CHECK(count == static_cast<ssize_t>(sizeof(payload)));
    IOTOX_CHECK((message.msg_flags & (MSG_CTRUNC | MSG_TRUNC)) == 0);
    const cmsghdr *header = CMSG_FIRSTHDR(&message);
    IOTOX_CHECK(header != nullptr);
    IOTOX_CHECK(header->cmsg_level == SOL_SOCKET);
    IOTOX_CHECK(header->cmsg_type == SCM_RIGHTS);
    IOTOX_CHECK(header->cmsg_len == CMSG_LEN(sizeof(int)));
    int descriptor = -1;
    std::memcpy(
        &descriptor, CMSG_DATA(const_cast<cmsghdr *>(header)),
        sizeof(descriptor));
    IOTOX_CHECK(descriptor >= 0);
    return descriptor;
}

void send_control_packet(
    int descriptor,
    const iotox::local::ControlPacket &packet) {
    auto encoded = iotox::local::encode_control_packet(packet);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    const ssize_t sent = ::send(
        descriptor, encoded.value().data(), encoded.value().size(),
        MSG_NOSIGNAL);
    IOTOX_CHECK(sent >= 0);
    IOTOX_CHECK(
        static_cast<std::size_t>(sent) == encoded.value().size());
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

IOTOX_TEST("same-user seqpacket control server correlates one request and response") {
    const std::filesystem::path directory = socket_test_directory("roundtrip");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(::mkdir(directory.c_str(), 0700) == 0);

    std::atomic<bool> observed_credentials{false};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    iotox::local::ControlServer server(
        config,
        [&observed_credentials](const iotox::local::ControlPacket &request,
                                const iotox::local::PeerCredentials &credentials) {
            observed_credentials.store(
                credentials.process_id > 0 && credentials.user_id ==
                                                   static_cast<std::uint64_t>(::geteuid()));
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            response.payload = iotox::local::text_payload("just-werx\n");
            return response;
        });
    const iotox::Status started = server.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    IOTOX_CHECK(server.running());

    struct stat metadata {};
    IOTOX_CHECK(::lstat(config.socket_path.c_str(), &metadata) == 0);
    IOTOX_CHECK(S_ISSOCK(metadata.st_mode));
    IOTOX_CHECK((metadata.st_mode & 0777) == 0600);

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 1234U;
    auto response = iotox::local::control_request(config.socket_path, request);
    IOTOX_CHECK_MSG(response.ok(), response.status().message());
    IOTOX_CHECK(response.value().request_id == request.request_id);
    IOTOX_CHECK(response.value().operation == request.operation);
    IOTOX_CHECK(response.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(iotox::local::payload_text(response.value().payload) == "just-werx\n");
    IOTOX_CHECK(observed_credentials.load());

    server.stop();
    IOTOX_CHECK(!std::filesystem::exists(config.socket_path));
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("control server refuses to unlink a non-socket occupant") {
    const std::filesystem::path directory = socket_test_directory("occupant");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(::mkdir(directory.c_str(), 0700) == 0);
    const std::filesystem::path occupied = directory / "control.sock";
    {
        std::ofstream output(occupied);
        output << "do-not-replace\n";
    }

    iotox::local::ControlServer::Config config;
    config.socket_path = occupied;
    iotox::local::ControlServer server(
        config, [](const auto &request, const auto &) { return request; });
    const iotox::Status started = server.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(std::filesystem::is_regular_file(occupied));

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("control client reports an absent daemon as unavailable") {
    const std::filesystem::path directory = socket_test_directory("absent");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(::mkdir(directory.c_str(), 0700) == 0);

    iotox::local::ControlPacket request;
    request.request_id = 77U;
    auto response = iotox::local::control_request(
        directory / "control.sock", request, std::chrono::milliseconds(100));
    IOTOX_CHECK(!response.ok());
    IOTOX_CHECK(response.status().code() == iotox::ErrorCode::unavailable);

    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("control server rejects a request sent through a fork-inherited socket") {
    const std::filesystem::path directory =
        socket_test_directory("fork-inherited-sender");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    config.request_timeout = std::chrono::milliseconds(500);
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &credentials) {
            IOTOX_CHECK(
                credentials.process_id ==
                static_cast<std::int64_t>(::getpid()));
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    const int descriptor = connect_raw_seqpacket(config.socket_path);
    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4101U;
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    int release_child[2]{-1, -1};
    IOTOX_CHECK(::pipe2(release_child, O_CLOEXEC) == 0);
    const pid_t child = ::fork();
    IOTOX_CHECK(child >= 0);
    if (child == 0) {
        static_cast<void>(::close(release_child[1]));
        const ssize_t count = ::send(
            descriptor, encoded.value().data(), encoded.value().size(),
            MSG_NOSIGNAL);
        std::uint8_t release = 0U;
        const ssize_t released = count >= 0 &&
                static_cast<std::size_t>(count) == encoded.value().size()
            ? ::read(release_child[0], &release, sizeof(release))
            : -1;
        ::_exit(
            released == static_cast<ssize_t>(sizeof(release))
                ? 0
                : 1);
    }
    IOTOX_CHECK(::close(release_child[0]) == 0);
    release_child[0] = -1;

    // Keep the actual record sender alive until recvmsg has captured its
    // SCM_PIDFD. Reaping it first races the valid credential-mismatch branch
    // against the kernel's fail-closed ancillary-truncation branch.
    const auto denied = receive_control_packet(descriptor);
    const std::uint8_t release = 1U;
    IOTOX_CHECK(::write(
                    release_child[1], &release, sizeof(release)) ==
                static_cast<ssize_t>(sizeof(release)));
    IOTOX_CHECK(::close(release_child[1]) == 0);
    release_child[1] = -1;
    int child_status = 0;
    IOTOX_CHECK(::waitpid(child, &child_status, 0) == child);
    IOTOX_CHECK(WIFEXITED(child_status));
    IOTOX_CHECK(WEXITSTATUS(child_status) == 0);

    IOTOX_CHECK(denied.kind == iotox::local::ControlKind::response);
    IOTOX_CHECK_MSG(
        denied.status == iotox::ErrorCode::unavailable,
        "unexpected status=" + iotox::local::to_string(denied.status) +
            " payload=" + iotox::local::payload_text(denied.payload));
    IOTOX_CHECK(handled.load() == 0U);
    IOTOX_CHECK(::close(descriptor) == 0);

    auto accepted = iotox::local::control_request(
        config.socket_path, request, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(handled.load() == 1U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("control server closes injected rights and rejects their request") {
    const std::filesystem::path directory =
        socket_test_directory("ancillary-rights");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    const int descriptor = connect_raw_seqpacket(config.socket_path);
    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4201U;
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    int pipe_descriptors[2]{-1, -1};
    IOTOX_CHECK(::pipe2(pipe_descriptors, O_CLOEXEC | O_NONBLOCK) == 0);
    IOTOX_CHECK(send_record_with_descriptor(
        descriptor, encoded.value(), pipe_descriptors[1]));
    IOTOX_CHECK(::close(pipe_descriptors[1]) == 0);
    pipe_descriptors[1] = -1;

    const auto denied = receive_control_packet(descriptor);
    IOTOX_CHECK(denied.status == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(handled.load() == 0U);
    IOTOX_CHECK(eventually([&] {
        std::uint8_t byte = 0U;
        const ssize_t count = ::read(pipe_descriptors[0], &byte, sizeof(byte));
        return count == 0;
    }));

    IOTOX_CHECK(::close(pipe_descriptors[0]) == 0);
    IOTOX_CHECK(::close(descriptor) == 0);
    auto accepted = iotox::local::control_request(
        config.socket_path, request, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(handled.load() == 1U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("control server expires a silent request lease and admits a successor") {
    const std::filesystem::path directory =
        socket_test_directory("silent-request-lease");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    config.request_timeout = std::chrono::milliseconds(30);
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    const int silent = connect_raw_seqpacket(config.socket_path);
    const auto timed_out = receive_control_packet(
        silent, std::chrono::milliseconds(500));
    IOTOX_CHECK(timed_out.status == iotox::ErrorCode::timeout);
    IOTOX_CHECK(handled.load() == 0U);
    IOTOX_CHECK(::close(silent) == 0);

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4301U;
    auto accepted = iotox::local::control_request(
        config.socket_path, request, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(handled.load() == 1U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("silent control peers do not serialize ready requests behind their leases") {
    const std::filesystem::path directory =
        socket_test_directory("concurrent-silent-request");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    config.request_timeout = std::chrono::milliseconds(400);
    config.maximum_pending_clients = 8U;
    config.maximum_pending_clients_per_process = 4U;
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    const int silent = connect_raw_seqpacket(config.socket_path);
    std::this_thread::sleep_for(std::chrono::milliseconds(20));

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4351U;
    const auto begin = std::chrono::steady_clock::now();
    auto response = iotox::local::control_request(
        config.socket_path, request, std::chrono::milliseconds(200));
    const auto elapsed = std::chrono::steady_clock::now() - begin;
    IOTOX_CHECK_MSG(response.ok(), response.status().message());
    IOTOX_CHECK(response.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(elapsed < std::chrono::milliseconds(200));
    IOTOX_CHECK(handled.load() == 1U);

    const auto timed_out = receive_control_packet(
        silent, std::chrono::milliseconds(800));
    IOTOX_CHECK(timed_out.status == iotox::ErrorCode::timeout);
    IOTOX_CHECK(::close(silent) == 0);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("control admission bounds silent connections from one process") {
    const std::filesystem::path directory =
        socket_test_directory("per-process-admission-bound");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    config.request_timeout = std::chrono::milliseconds(300);
    config.maximum_pending_clients = 4U;
    config.maximum_pending_clients_per_process = 1U;
    config.maximum_accepts_per_interval = 4U;
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    const int first = connect_raw_seqpacket(config.socket_path);
    const int second = connect_raw_seqpacket(config.socket_path);
    const auto rejected = receive_control_packet(
        second, std::chrono::milliseconds(500));
    IOTOX_CHECK(rejected.status == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(iotox::local::payload_text(rejected.payload) ==
                "local control per-process pending-client limit is full");
    IOTOX_CHECK(handled.load() == 0U);
    IOTOX_CHECK(::close(second) == 0);

    IOTOX_CHECK(::close(first) == 0);
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4352U;
    auto accepted = iotox::local::control_request(
        config.socket_path, request, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(handled.load() == 1U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("control server expires admitted silent leases concurrently") {
    const std::filesystem::path directory =
        socket_test_directory("concurrent-silent-expiry");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    config.request_timeout = std::chrono::milliseconds(300);
    config.maximum_pending_clients = 4U;
    config.maximum_pending_clients_per_process = 4U;
    config.maximum_accepts_per_interval = 4U;
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    const auto begin = std::chrono::steady_clock::now();
    std::array<int, 4U> silent{{
        connect_raw_seqpacket(config.socket_path),
        connect_raw_seqpacket(config.socket_path),
        connect_raw_seqpacket(config.socket_path),
        connect_raw_seqpacket(config.socket_path),
    }};
    for (const int descriptor : silent) {
        const auto timed_out = receive_control_packet(
            descriptor, std::chrono::milliseconds(1200));
        IOTOX_CHECK(timed_out.status == iotox::ErrorCode::timeout);
    }
    const auto elapsed = std::chrono::steady_clock::now() - begin;
    // A serial four-client worker would consume roughly four complete leases.
    // Independent admission deadlines expire in one shared poll horizon.
    IOTOX_CHECK(elapsed < std::chrono::milliseconds(900));
    IOTOX_CHECK(handled.load() == 0U);
    for (const int descriptor : silent) {
        IOTOX_CHECK(::close(descriptor) == 0);
    }

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4353U;
    auto successor = iotox::local::control_request(
        config.socket_path, request, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(handled.load() == 1U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("control server enforces the global pending admission ceiling") {
    const std::filesystem::path directory =
        socket_test_directory("global-admission-bound");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    config.request_timeout = std::chrono::milliseconds(800);
    config.maximum_pending_clients = 2U;
    config.maximum_pending_clients_per_process = 2U;
    config.maximum_accepts_per_interval = 4U;
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    const int first = connect_raw_seqpacket(config.socket_path);
    const int second = connect_raw_seqpacket(config.socket_path);
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    const int excess = connect_raw_seqpacket(config.socket_path);
    const auto rejected = receive_control_packet(
        excess, std::chrono::milliseconds(500));
    IOTOX_CHECK(rejected.status == iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(iotox::local::payload_text(rejected.payload) ==
                "local control pending-client limit is full");
    IOTOX_CHECK(::close(excess) == 0);

    iotox::local::ControlPacket first_request;
    first_request.operation = iotox::local::ControlOperation::ping;
    first_request.request_id = 4354U;
    send_control_packet(first, first_request);
    const auto first_response = receive_control_packet(first);
    IOTOX_CHECK(first_response.request_id == first_request.request_id);
    IOTOX_CHECK(first_response.status == iotox::ErrorCode::ok);

    iotox::local::ControlPacket second_request;
    second_request.operation = iotox::local::ControlOperation::ping;
    second_request.request_id = 4355U;
    send_control_packet(second, second_request);
    const auto second_response = receive_control_packet(second);
    IOTOX_CHECK(second_response.request_id == second_request.request_id);
    IOTOX_CHECK(second_response.status == iotox::ErrorCode::ok);
    IOTOX_CHECK(handled.load() == 2U);
    IOTOX_CHECK(::close(first) == 0);
    IOTOX_CHECK(::close(second) == 0);

    iotox::local::ControlPacket successor_request;
    successor_request.operation = iotox::local::ControlOperation::ping;
    successor_request.request_id = 4356U;
    auto successor = iotox::local::control_request(
        config.socket_path, successor_request,
        std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(handled.load() == 3U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("control server releases a silent socket when its pinned peer exits") {
    if (!peer_pidfd_supported()) return;

    const std::filesystem::path directory =
        socket_test_directory("pinned-peer-exit");
    prepare_private_directory(directory);

    std::atomic<unsigned int> handled{0U};
    iotox::local::ControlServer::Config config;
    config.socket_path = directory / "control.sock";
    config.request_timeout = std::chrono::milliseconds(2000);
    config.maximum_pending_clients = 1U;
    config.maximum_pending_clients_per_process = 1U;
    iotox::local::ControlServer server(
        config,
        [&](const iotox::local::ControlPacket &request,
            const iotox::local::PeerCredentials &) {
            handled.fetch_add(1U);
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(server.start().ok(), "control server did not start");

    int transfer[2]{-1, -1};
    IOTOX_CHECK(::socketpair(
                    AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC,
                    0, transfer) == 0);
    const pid_t connector = ::fork();
    IOTOX_CHECK(connector >= 0);
    if (connector == 0) {
        static_cast<void>(::close(transfer[0]));
        const std::string text = config.socket_path.string();
        const int descriptor = ::socket(
            AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
        if (descriptor < 0 || text.size() >= sizeof(sockaddr_un::sun_path)) {
            ::_exit(10);
        }
        sockaddr_un address{};
        address.sun_family = AF_UNIX;
        std::memcpy(address.sun_path, text.c_str(), text.size() + 1U);
        if (::connect(
                descriptor,
                reinterpret_cast<const sockaddr *>(&address),
                sizeof(address)) != 0) {
            ::_exit(11);
        }
        const std::array<std::uint8_t, 1U> marker{{0xA5U}};
        if (!send_record_with_descriptor(
                transfer[1], marker, descriptor)) {
            ::_exit(12);
        }
        std::uint8_t release = 0U;
        if (::recv(
                transfer[1], &release, sizeof(release), 0) !=
            static_cast<ssize_t>(sizeof(release))) {
            ::_exit(13);
        }
        static_cast<void>(::close(descriptor));
        static_cast<void>(::close(transfer[1]));
        ::_exit(release == 0x5AU ? 0 : 14);
    }
    IOTOX_CHECK(::close(transfer[1]) == 0);
    transfer[1] = -1;
    const int surviving_descriptor = receive_passed_descriptor(transfer[0]);

    // Keep the connection-time process alive until the server has had an
    // uncontended admission window, then exit while this process retains the
    // same open file description.
    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    const std::uint8_t release = 0x5AU;
    IOTOX_CHECK(
        ::send(
            transfer[0], &release, sizeof(release), MSG_NOSIGNAL) ==
        static_cast<ssize_t>(sizeof(release)));
    IOTOX_CHECK(::close(transfer[0]) == 0);
    transfer[0] = -1;

    int connector_status = 0;
    IOTOX_CHECK(
        ::waitpid(connector, &connector_status, 0) == connector);
    IOTOX_CHECK(WIFEXITED(connector_status));
    IOTOX_CHECK(WEXITSTATUS(connector_status) == 0);

    struct pollfd released {surviving_descriptor, POLLIN, 0};
    int release_ready = -1;
    do {
        release_ready = ::poll(&released, 1U, 750);
    } while (release_ready < 0 && errno == EINTR);
    IOTOX_CHECK(release_ready > 0);
    IOTOX_CHECK(
        (released.revents & (POLLIN | POLLHUP | POLLERR)) != 0);
    IOTOX_CHECK(::close(surviving_descriptor) == 0);

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4357U;
    auto successor = iotox::local::control_request(
        config.socket_path, request, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(successor.value().status == iotox::ErrorCode::ok);
    IOTOX_CHECK(handled.load() == 1U);

    server.stop();
    remove_test_directory(directory);
}

IOTOX_TEST("control client abandons a socket retained after its pinned server exits") {
    if (!peer_pidfd_supported()) return;

    const std::filesystem::path directory =
        socket_test_directory("pinned-server-exit");
    prepare_private_directory(directory);
    const std::filesystem::path socket_path = directory / "control.sock";

    int transfer[2]{-1, -1};
    IOTOX_CHECK(::socketpair(
                    AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC,
                    0, transfer) == 0);
    const pid_t server_process = ::fork();
    IOTOX_CHECK(server_process >= 0);
    if (server_process == 0) {
        static_cast<void>(::close(transfer[0]));
        const std::string text = socket_path.string();
        const int listener = ::socket(
            AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
        if (listener < 0 || text.size() >= sizeof(sockaddr_un::sun_path)) {
            ::_exit(20);
        }
        sockaddr_un address{};
        address.sun_family = AF_UNIX;
        std::memcpy(address.sun_path, text.c_str(), text.size() + 1U);
        if (::bind(
                listener,
                reinterpret_cast<const sockaddr *>(&address),
                sizeof(address)) != 0 ||
            ::chmod(socket_path.c_str(), 0600) != 0 ||
            ::listen(listener, 1) != 0) {
            ::_exit(21);
        }
        const std::uint8_t ready = 0x5AU;
        if (::send(
                transfer[1], &ready, sizeof(ready), MSG_NOSIGNAL) !=
            static_cast<ssize_t>(sizeof(ready))) {
            ::_exit(22);
        }
        const int accepted = ::accept4(
            listener, nullptr, nullptr, SOCK_CLOEXEC);
        if (accepted < 0) ::_exit(23);

        std::array<std::uint8_t, iotox::local::kControlMaxPacketSize + 1U>
            request{};
        const ssize_t received = ::recv(
            accepted, request.data(), request.size(), 0);
        if (received <= 0) ::_exit(24);

        const std::array<std::uint8_t, 1U> marker{{0xA6U}};
        if (!send_record_with_descriptor(
                transfer[1], marker, accepted)) {
            ::_exit(25);
        }
        static_cast<void>(::close(accepted));
        static_cast<void>(::close(listener));
        static_cast<void>(::close(transfer[1]));
        ::_exit(0);
    }

    IOTOX_CHECK(::close(transfer[1]) == 0);
    transfer[1] = -1;
    std::uint8_t ready = 0U;
    IOTOX_CHECK(
        ::recv(transfer[0], &ready, sizeof(ready), 0) ==
        static_cast<ssize_t>(sizeof(ready)));
    IOTOX_CHECK(ready == 0x5AU);

    std::atomic<bool> request_succeeded{true};
    std::atomic<int> request_code{
        static_cast<int>(iotox::ErrorCode::internal_error)};
    std::atomic<std::int64_t> elapsed_milliseconds{0};
    std::jthread requester([&] {
        iotox::local::ControlPacket request;
        request.operation = iotox::local::ControlOperation::ping;
        request.request_id = 4358U;
        const auto started = std::chrono::steady_clock::now();
        auto result = iotox::local::control_request(
            socket_path, request, std::chrono::milliseconds(2500));
        elapsed_milliseconds.store(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now() - started)
                .count());
        request_succeeded.store(result.ok());
        request_code.store(static_cast<int>(
            result.ok() ? iotox::ErrorCode::ok : result.status().code()));
    });

    const int surviving_server_descriptor =
        receive_passed_descriptor(transfer[0]);
    IOTOX_CHECK(::close(transfer[0]) == 0);
    transfer[0] = -1;

    int server_status = 0;
    IOTOX_CHECK(
        ::waitpid(server_process, &server_status, 0) == server_process);
    IOTOX_CHECK(WIFEXITED(server_status));
    IOTOX_CHECK(WEXITSTATUS(server_status) == 0);
    requester.join();

    IOTOX_CHECK(!request_succeeded.load());
    IOTOX_CHECK(
        request_code.load() ==
        static_cast<int>(iotox::ErrorCode::unavailable));
    IOTOX_CHECK(elapsed_milliseconds.load() < 1500);
    IOTOX_CHECK(::close(surviving_server_descriptor) == 0);

    remove_test_directory(directory);
}

IOTOX_TEST("control server preserves active and replacement socket inodes") {
    const std::filesystem::path directory =
        socket_test_directory("inode-ownership");
    prepare_private_directory(directory);
    const std::filesystem::path socket_path = directory / "control.sock";

    iotox::local::ControlServer::Config config;
    config.socket_path = socket_path;
    iotox::local::ControlServer first(
        config,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) {
            iotox::local::ControlPacket response;
            response.operation = request.operation;
            response.request_id = request.request_id;
            response.status = iotox::ErrorCode::ok;
            return response;
        });
    IOTOX_CHECK_MSG(first.start().ok(), "first control server did not start");

    struct stat original {};
    IOTOX_CHECK(::lstat(socket_path.c_str(), &original) == 0);
    iotox::local::ControlServer second(
        config,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status second_start = second.start();
    IOTOX_CHECK(!second_start.ok());
    IOTOX_CHECK(second_start.code() == iotox::ErrorCode::resource_exhausted);

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4401U;
    auto response = iotox::local::control_request(
        socket_path, request, std::chrono::milliseconds(500));
    IOTOX_CHECK_MSG(response.ok(), response.status().message());
    IOTOX_CHECK(response.value().status == iotox::ErrorCode::ok);

    IOTOX_CHECK(::unlink(socket_path.c_str()) == 0);
    const int replacement = bind_raw_seqpacket(socket_path, true);
    struct stat replacement_metadata {};
    IOTOX_CHECK(::lstat(socket_path.c_str(), &replacement_metadata) == 0);
    IOTOX_CHECK(original.st_ino != replacement_metadata.st_ino);

    first.stop();
    struct stat after_stop {};
    IOTOX_CHECK(::lstat(socket_path.c_str(), &after_stop) == 0);
    IOTOX_CHECK(after_stop.st_dev == replacement_metadata.st_dev);
    IOTOX_CHECK(after_stop.st_ino == replacement_metadata.st_ino);

    IOTOX_CHECK(::close(replacement) == 0);
    IOTOX_CHECK(::unlink(socket_path.c_str()) == 0);
    remove_test_directory(directory);
}

IOTOX_TEST("control client and server reject unsafe paths and request leases") {
    const std::filesystem::path directory =
        socket_test_directory("configuration-hardening");
    prepare_private_directory(directory);

    iotox::local::ControlServer::Config no_lease;
    no_lease.socket_path = directory / "no-lease.sock";
    no_lease.request_timeout = std::chrono::milliseconds::zero();
    iotox::local::ControlServer no_lease_server(
        no_lease,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status no_lease_start = no_lease_server.start();
    IOTOX_CHECK(!no_lease_start.ok());
    IOTOX_CHECK(no_lease_start.code() == iotox::ErrorCode::invalid_argument);

    iotox::local::ControlServer::Config no_pending;
    no_pending.socket_path = directory / "no-pending.sock";
    no_pending.maximum_pending_clients = 0U;
    iotox::local::ControlServer no_pending_server(
        no_pending,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status no_pending_start = no_pending_server.start();
    IOTOX_CHECK(!no_pending_start.ok());
    IOTOX_CHECK(no_pending_start.code() == iotox::ErrorCode::invalid_argument);

    iotox::local::ControlServer::Config excessive_pending;
    excessive_pending.socket_path = directory / "excessive-pending.sock";
    excessive_pending.maximum_pending_clients = 257U;
    excessive_pending.maximum_pending_clients_per_process = 1U;
    iotox::local::ControlServer excessive_pending_server(
        excessive_pending,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status excessive_pending_start =
        excessive_pending_server.start();
    IOTOX_CHECK(!excessive_pending_start.ok());
    IOTOX_CHECK(
        excessive_pending_start.code() ==
        iotox::ErrorCode::invalid_argument);

    iotox::local::ControlServer::Config bad_process_limit;
    bad_process_limit.socket_path = directory / "bad-process-limit.sock";
    bad_process_limit.maximum_pending_clients = 2U;
    bad_process_limit.maximum_pending_clients_per_process = 3U;
    iotox::local::ControlServer bad_process_limit_server(
        bad_process_limit,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status bad_process_limit_start =
        bad_process_limit_server.start();
    IOTOX_CHECK(!bad_process_limit_start.ok());
    IOTOX_CHECK(
        bad_process_limit_start.code() == iotox::ErrorCode::invalid_argument);

    iotox::local::ControlServer::Config no_accept_budget;
    no_accept_budget.socket_path = directory / "no-accept-budget.sock";
    no_accept_budget.maximum_accepts_per_interval = 0U;
    iotox::local::ControlServer no_accept_budget_server(
        no_accept_budget,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status no_accept_budget_start =
        no_accept_budget_server.start();
    IOTOX_CHECK(!no_accept_budget_start.ok());
    IOTOX_CHECK(
        no_accept_budget_start.code() ==
        iotox::ErrorCode::invalid_argument);

    iotox::local::ControlServer::Config no_request_budget;
    no_request_budget.socket_path = directory / "no-request-budget.sock";
    no_request_budget.maximum_requests_per_cycle = 0U;
    iotox::local::ControlServer no_request_budget_server(
        no_request_budget,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status no_request_budget_start =
        no_request_budget_server.start();
    IOTOX_CHECK(!no_request_budget_start.ok());
    IOTOX_CHECK(
        no_request_budget_start.code() ==
        iotox::ErrorCode::invalid_argument);

    iotox::local::ControlServer::Config no_admission_interval;
    no_admission_interval.socket_path = directory / "no-admission-interval.sock";
    no_admission_interval.admission_interval =
        std::chrono::milliseconds::zero();
    iotox::local::ControlServer no_admission_interval_server(
        no_admission_interval,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status no_admission_interval_start =
        no_admission_interval_server.start();
    IOTOX_CHECK(!no_admission_interval_start.ok());
    IOTOX_CHECK(
        no_admission_interval_start.code() ==
        iotox::ErrorCode::invalid_argument);

    iotox::local::ControlServer::Config public_mode;
    public_mode.socket_path = directory / "public.sock";
    public_mode.socket_mode = 0660U;
    iotox::local::ControlServer public_mode_server(
        public_mode,
        [](const iotox::local::ControlPacket &request,
           const iotox::local::PeerCredentials &) { return request; });
    const iotox::Status public_mode_start = public_mode_server.start();
    IOTOX_CHECK(!public_mode_start.ok());
    IOTOX_CHECK(public_mode_start.code() == iotox::ErrorCode::invalid_argument);

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4501U;
    auto relative = iotox::local::control_request(
        "relative-control.sock", request, std::chrono::milliseconds(50));
    IOTOX_CHECK(!relative.ok());
    IOTOX_CHECK(relative.status().code() == iotox::ErrorCode::invalid_argument);

    IOTOX_CHECK(::chmod(directory.c_str(), 0755) == 0);
    auto public_parent = iotox::local::control_request(
        directory / "absent.sock", request, std::chrono::milliseconds(50));
    IOTOX_CHECK(!public_parent.ok());
    IOTOX_CHECK(public_parent.status().code() == iotox::ErrorCode::io_error);

    remove_test_directory(directory);
}

IOTOX_TEST("control client rejects a response sent through a fork-inherited server socket") {
    const std::filesystem::path directory =
        socket_test_directory("fork-inherited-response");
    prepare_private_directory(directory);
    const std::filesystem::path socket_path = directory / "control.sock";
    const int listener = bind_raw_seqpacket(socket_path, true);
    IOTOX_CHECK(::chmod(socket_path.c_str(), 0600) == 0);

    std::atomic<int> child_exit{-1};
    std::jthread responder([&] {
        const int accepted = ::accept4(listener, nullptr, nullptr, SOCK_CLOEXEC);
        IOTOX_CHECK(accepted >= 0);
        std::array<std::uint8_t, iotox::local::kControlMaxPacketSize + 1U> bytes{};
        const ssize_t received = ::recv(accepted, bytes.data(), bytes.size(), 0);
        IOTOX_CHECK(received > 0);

        iotox::local::ControlPacket response;
        response.kind = iotox::local::ControlKind::response;
        response.operation = iotox::local::ControlOperation::ping;
        response.request_id = 4601U;
        response.status = iotox::ErrorCode::ok;
        auto encoded = iotox::local::encode_control_packet(response);
        IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

        const pid_t child = ::fork();
        IOTOX_CHECK(child >= 0);
        if (child == 0) {
            const ssize_t sent = ::send(
                accepted, encoded.value().data(), encoded.value().size(),
                MSG_NOSIGNAL);
            ::_exit(
                sent >= 0 &&
                        static_cast<std::size_t>(sent) == encoded.value().size()
                    ? 0
                    : 1);
        }
        int status = 0;
        IOTOX_CHECK(::waitpid(child, &status, 0) == child);
        IOTOX_CHECK(WIFEXITED(status));
        child_exit.store(WEXITSTATUS(status));
        IOTOX_CHECK(::close(accepted) == 0);
    });

    iotox::local::ControlPacket request;
    request.operation = iotox::local::ControlOperation::ping;
    request.request_id = 4601U;
    auto denied = iotox::local::control_request(
        socket_path, request, std::chrono::milliseconds(1000));
    IOTOX_CHECK(!denied.ok());
    IOTOX_CHECK(denied.status().code() == iotox::ErrorCode::unavailable);

    responder.join();
    IOTOX_CHECK(child_exit.load() == 0);
    IOTOX_CHECK(::close(listener) == 0);
    IOTOX_CHECK(::unlink(socket_path.c_str()) == 0);
    remove_test_directory(directory);
}
