#include "iotox/local/control_socket.hpp"

#include "seqpacket_security.hpp"

#include <algorithm>
#include <array>
#include <climits>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <fcntl.h>
#include <exception>
#include <future>
#include <limits>
#include <mutex>
#include <poll.h>
#include <string>
#include <sys/eventfd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/un.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::local {
namespace {

class UniqueFd {
  public:
    UniqueFd() = default;
    explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd &) = delete;
    UniqueFd &operator=(const UniqueFd &) = delete;
    UniqueFd(UniqueFd &&other) noexcept : descriptor_(std::exchange(other.descriptor_, -1)) {}
    UniqueFd &operator=(UniqueFd &&other) noexcept {
        if (this != &other) {
            reset(std::exchange(other.descriptor_, -1));
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] explicit operator bool() const noexcept { return descriptor_ >= 0; }

    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) {
            static_cast<void>(::close(descriptor_));
        }
        descriptor_ = descriptor;
    }

  private:
    int descriptor_{-1};
};

struct SocketIdentity {
    dev_t device{0};
    ino_t inode{0};
    bool present{false};
};

Status system_status(ErrorCode code, std::string operation, const std::filesystem::path &path = {}) {
    std::string message = std::move(operation);
    if (!path.empty()) {
        message += " '" + path.string() + "'";
    }
    message += ": ";
    message += std::strerror(errno);
    return Status{code, std::move(message)};
}

Result<sockaddr_un> unix_address(const std::filesystem::path &socket_path) {
    if (!socket_path.is_absolute()) {
        return Status{ErrorCode::invalid_argument,
                      "local control socket path must be absolute"};
    }
    const std::string path = socket_path.string();
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    if (path.empty()) {
        return Status{ErrorCode::invalid_argument, "local control socket path is empty"};
    }
    if (path.size() >= sizeof(address.sun_path)) {
        return Status{ErrorCode::invalid_argument,
                      "local control socket path exceeds the Unix-domain limit"};
    }
    if (path.find('\0') != std::string::npos) {
        return Status{ErrorCode::invalid_argument,
                      "local control socket path contains an embedded NUL byte"};
    }
    std::memcpy(address.sun_path, path.c_str(), path.size() + 1U);
    return address;
}

Status inspect_private_parent(const std::filesystem::path &parent) {
    if (parent.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "local control socket must have an explicit parent directory"};
    }
    struct stat metadata {};
    if (::lstat(parent.c_str(), &metadata) != 0) {
        return system_status(
            ErrorCode::io_error,
            "unable to inspect local control parent directory", parent);
    }
    if (!S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "local control parent is not a real directory: " +
                          parent.string()};
    }
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "local control parent is owned by another user: " +
                          parent.string()};
    }
    if ((metadata.st_mode & 0077) != 0) {
        return Status{ErrorCode::io_error,
                      "local control parent must not grant group or other permissions: " +
                          parent.string()};
    }
    return Status::success();
}

Result<SocketIdentity> inspect_owned_socket_identity(
    const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        return system_status(
            ErrorCode::io_error,
            "unable to inspect local control socket", path);
    }
    if (!S_ISSOCK(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "local control path is not a socket owned by the daemon user: " +
                          path.string()};
    }
    return SocketIdentity{metadata.st_dev, metadata.st_ino, true};
}

void unlink_if_same_socket(
    const std::filesystem::path &path,
    const SocketIdentity &identity) noexcept {
    if (!identity.present || path.empty()) return;
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) == 0 &&
        S_ISSOCK(metadata.st_mode) && metadata.st_uid == ::geteuid() &&
        metadata.st_dev == identity.device && metadata.st_ino == identity.inode) {
        static_cast<void>(::unlink(path.c_str()));
    }
}

Status remove_owned_stale_socket(const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return system_status(ErrorCode::io_error, "unable to inspect local control socket", path);
    }
    if (!S_ISSOCK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "refusing to replace non-socket local control path '" + path.string() + "'"};
    }
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "refusing to remove local control socket owned by another user: " + path.string()};
    }

    auto address = unix_address(path);
    if (!address) return address.status();
    UniqueFd probe(::socket(
        AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0));
    if (!probe) {
        return system_status(
            ErrorCode::io_error,
            "unable to probe existing local control socket");
    }
    int connected = -1;
    do {
        connected = ::connect(
            probe.get(), reinterpret_cast<const sockaddr *>(&address.value()),
            sizeof(sockaddr_un));
    } while (connected != 0 && errno == EINTR);
    if (connected == 0 || errno == EINPROGRESS || errno == EAGAIN ||
        errno == EWOULDBLOCK) {
        return Status{ErrorCode::resource_exhausted,
                      "another IoTox control server is already listening at '" +
                          path.string() + "'"};
    }
    if (errno != ECONNREFUSED && errno != ENOENT) {
        return system_status(
            ErrorCode::io_error,
            "unable to probe existing local control socket", path);
    }

    struct stat current {};
    if (::lstat(path.c_str(), &current) != 0) {
        return errno == ENOENT
            ? Status::success()
            : system_status(
                  ErrorCode::io_error,
                  "unable to re-inspect local control socket", path);
    }
    if (!S_ISSOCK(current.st_mode) || current.st_uid != ::geteuid() ||
        current.st_dev != metadata.st_dev || current.st_ino != metadata.st_ino) {
        return Status{ErrorCode::unavailable,
                      "local control socket changed while stale ownership was checked"};
    }
    if (::unlink(path.c_str()) != 0) {
        return system_status(ErrorCode::io_error, "unable to remove stale local control socket", path);
    }
    return Status::success();
}

Result<PeerCredentials> peer_credentials(int descriptor) {
    return detail::connected_peer_credentials(descriptor, "local control");
}

ControlPacket error_response(
    std::uint64_t request_id,
    ControlOperation operation,
    ErrorCode code,
    std::string message) {
    ControlPacket response;
    response.kind = ControlKind::response;
    response.operation = operation;
    response.request_id = request_id == 0U ? 1U : request_id;
    response.status = code;
    response.payload = text_payload(std::move(message));
    return response;
}

Status send_packet(int descriptor, const ControlPacket &packet) {
    auto encoded = encode_control_packet(packet);
    if (!encoded) {
        return encoded.status();
    }
    ssize_t count = -1;
    do {
        count = ::send(descriptor, encoded.value().data(), encoded.value().size(), MSG_NOSIGNAL);
    } while (count < 0 && errno == EINTR);
    if (count < 0) {
        return system_status(ErrorCode::io_error, "unable to send local control packet");
    }
    if (static_cast<std::size_t>(count) != encoded.value().size()) {
        return Status{ErrorCode::io_error,
                      "local control seqpacket send was unexpectedly partial"};
    }
    return Status::success();
}

Result<detail::ReceivedSeqpacket> receive_authenticated_datagram(
    int descriptor,
    bool require_pidfd,
    int receive_flags = 0) {
    return detail::receive_seqpacket(
        descriptor, kControlMaxPacketSize, true, require_pidfd,
        receive_flags, "local control");
}

Status configure_timeout(int descriptor, std::chrono::milliseconds timeout) {
    if (timeout <= std::chrono::milliseconds::zero()) {
        return Status{ErrorCode::invalid_argument, "local control timeout must be positive"};
    }
    const auto seconds = std::chrono::duration_cast<std::chrono::seconds>(timeout);
    const auto remainder = timeout - seconds;
    struct timeval value {};
    value.tv_sec = static_cast<time_t>(seconds.count());
    value.tv_usec = static_cast<suseconds_t>(
        std::chrono::duration_cast<std::chrono::microseconds>(remainder).count());
    if (::setsockopt(descriptor, SOL_SOCKET, SO_RCVTIMEO, &value, sizeof(value)) != 0 ||
        ::setsockopt(descriptor, SOL_SOCKET, SO_SNDTIMEO, &value, sizeof(value)) != 0) {
        return system_status(ErrorCode::io_error, "unable to configure local control timeout");
    }
    return Status::success();
}

int poll_timeout_until(
    std::chrono::steady_clock::time_point deadline) noexcept {
    const auto now = std::chrono::steady_clock::now();
    if (deadline <= now) return 0;
    const auto remaining = std::chrono::ceil<std::chrono::milliseconds>(
        deadline - now);
    if (remaining.count() >=
        static_cast<std::chrono::milliseconds::rep>(
            std::numeric_limits<int>::max())) {
        return std::numeric_limits<int>::max();
    }
    return static_cast<int>(remaining.count());
}

Status wait_for_response(
    int descriptor,
    const detail::OwnedDescriptor &server_pidfd,
    std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    for (;;) {
        std::array<struct pollfd, 2U> descriptors{{
            {descriptor, POLLIN, 0},
            {server_pidfd ? server_pidfd.get() : -1, POLLIN, 0},
        }};
        int ready = -1;
        do {
            ready = ::poll(
                descriptors.data(), descriptors.size(),
                poll_timeout_until(deadline));
        } while (ready < 0 && errno == EINTR);
        if (ready < 0) {
            return system_status(
                ErrorCode::io_error,
                "unable to poll the IoTox control response");
        }
        if (ready == 0) {
            return Status{
                ErrorCode::timeout,
                "IoTox control response deadline elapsed"};
        }

        const short socket_events = descriptors[0U].revents;
        // A complete record sent immediately before server exit remains a
        // valid response. Preserve record ordering when socket and pidfd become
        // ready in the same poll cycle.
        if ((socket_events & POLLIN) != 0) return Status::success();
        if ((socket_events & POLLNVAL) != 0) {
            return Status{
                ErrorCode::io_error,
                "IoTox control response socket became invalid"};
        }
        if ((socket_events & (POLLERR | POLLHUP)) != 0) {
            return Status{
                ErrorCode::unavailable,
                "IoTox control server closed without a response"};
        }
        if ((descriptors[1U].revents &
             (POLLIN | POLLHUP | POLLERR | POLLNVAL)) != 0) {
            return Status{
                ErrorCode::unavailable,
                "IoTox control server process exited before responding"};
        }
    }
}

}  // namespace

class ControlServer::Impl {
  public:
    Impl(Config config, Handler handler)
        : config_(std::move(config)), handler_(std::move(handler)) {}

    ~Impl() { stop(); }

    Status start() {
        std::scoped_lock lifecycle_lock(lifecycle_mutex_);
        bool expected = false;
        if (!start_called_.compare_exchange_strong(expected, true)) {
            return Status{ErrorCode::invalid_argument,
                          "local control server start() may only be called once"};
        }
        if (!handler_) {
            return Status{ErrorCode::invalid_argument,
                          "local control server handler is empty"};
        }
        if (config_.backlog < 1 || config_.backlog > 1024 ||
            config_.request_timeout <= std::chrono::milliseconds::zero() ||
            config_.request_timeout > std::chrono::seconds(60) ||
            config_.maximum_pending_clients == 0U ||
            config_.maximum_pending_clients > 256U ||
            config_.maximum_pending_clients_per_process == 0U ||
            config_.maximum_pending_clients_per_process >
                config_.maximum_pending_clients ||
            config_.maximum_accepts_per_interval == 0U ||
            config_.maximum_accepts_per_interval > 256U ||
            config_.maximum_requests_per_cycle == 0U ||
            config_.maximum_requests_per_cycle > 256U ||
            config_.admission_interval <=
                std::chrono::milliseconds::zero() ||
            config_.admission_interval > std::chrono::seconds(1) ||
            (config_.socket_mode & ~0777U) != 0U ||
            (config_.socket_mode & 0077U) != 0U ||
            (config_.socket_mode & 0600U) != 0600U) {
            return Status{ErrorCode::invalid_argument,
                          "local control server limits or permissions are invalid"};
        }

        auto address = unix_address(config_.socket_path);
        if (!address) return address.status();
        const Status parent = inspect_private_parent(
            config_.socket_path.parent_path());
        if (!parent.ok()) return parent;
        const Status stale = remove_owned_stale_socket(config_.socket_path);
        if (!stale.ok()) return stale;

        UniqueFd listener(::socket(
            AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0));
        if (!listener) {
            return system_status(
                ErrorCode::io_error,
                "unable to create local control socket");
        }
        auto pidfd_delivery = detail::enable_record_credentials(
            listener.get(), "local control");
        if (!pidfd_delivery) return pidfd_delivery.status();
        if (::bind(
                listener.get(),
                reinterpret_cast<const sockaddr *>(&address.value()),
                sizeof(sockaddr_un)) != 0) {
            return system_status(
                ErrorCode::io_error,
                "unable to bind local control socket", config_.socket_path);
        }
        auto identity = inspect_owned_socket_identity(config_.socket_path);
        if (!identity) {
            static_cast<void>(::unlink(config_.socket_path.c_str()));
            return identity.status();
        }
        const SocketIdentity bound_identity = identity.value();
        if (::chmod(
                config_.socket_path.c_str(),
                static_cast<mode_t>(config_.socket_mode)) != 0) {
            const Status failed = system_status(
                ErrorCode::io_error,
                "unable to set local control socket permissions",
                config_.socket_path);
            unlink_if_same_socket(config_.socket_path, bound_identity);
            return failed;
        }
        if (::listen(listener.get(), config_.backlog) != 0) {
            const Status failed = system_status(
                ErrorCode::io_error,
                "unable to listen on local control socket",
                config_.socket_path);
            unlink_if_same_socket(config_.socket_path, bound_identity);
            return failed;
        }

        UniqueFd wake(::eventfd(0U, EFD_CLOEXEC | EFD_NONBLOCK));
        if (!wake) {
            const Status failed = system_status(
                ErrorCode::io_error,
                "unable to create local control wake event");
            unlink_if_same_socket(config_.socket_path, bound_identity);
            return failed;
        }

        listener_ = std::move(listener);
        pass_pidfd_enabled_ = pidfd_delivery.value();
        {
            std::scoped_lock wake_lock(wake_mutex_);
            wake_ = std::move(wake);
        }
        bound_identity_ = bound_identity;
        stop_requested_.store(false);
        running_.store(true);
        try {
            worker_ = std::thread([this] { worker_main(); });
            worker_id_ = worker_.get_id();
        } catch (const std::exception &exception) {
            running_.store(false);
            listener_.reset();
            pass_pidfd_enabled_ = false;
            {
                std::scoped_lock wake_lock(wake_mutex_);
                wake_.reset();
            }
            unlink_if_same_socket(config_.socket_path, bound_identity_);
            bound_identity_ = {};
            return Status{
                ErrorCode::resource_exhausted,
                "unable to start local control worker: " +
                    std::string(exception.what())};
        }
        return Status::success();
    }

    void stop() {
        bool called_from_worker = false;
        {
            std::scoped_lock lifecycle_lock(lifecycle_mutex_);
            stop_requested_.store(true);
            called_from_worker =
                worker_id_ != std::thread::id{} &&
                worker_id_ == std::this_thread::get_id();
        }
        notify();
        if (called_from_worker) return;

        {
            std::scoped_lock join_lock(join_mutex_);
            if (worker_.joinable()) worker_.join();
        }
        {
            std::scoped_lock lifecycle_lock(lifecycle_mutex_);
            running_.store(false);
            listener_.reset();
            pass_pidfd_enabled_ = false;
            {
                std::scoped_lock wake_lock(wake_mutex_);
                wake_.reset();
            }
            unlink_if_same_socket(config_.socket_path, bound_identity_);
            bound_identity_ = {};
            worker_id_ = {};
        }
    }

    [[nodiscard]] bool running() const noexcept { return running_.load(); }
    [[nodiscard]] const std::filesystem::path &socket_path() const noexcept {
        return config_.socket_path;
    }

  private:
    void notify() noexcept {
        std::scoped_lock wake_lock(wake_mutex_);
        if (!wake_) return;
        const std::uint64_t one = 1U;
        const ssize_t ignored = ::write(wake_.get(), &one, sizeof(one));
        static_cast<void>(ignored);
    }

    void drain_wake() noexcept {
        std::uint64_t value = 0U;
        while (::read(wake_.get(), &value, sizeof(value)) > 0) {}
    }

    struct PendingClient {
        UniqueFd descriptor;
        PeerCredentials connection_credentials;
        detail::OwnedDescriptor peer_pidfd;
        std::chrono::steady_clock::time_point deadline;
        bool remove{false};
    };

    [[nodiscard]] std::size_t pending_for_process(
        const std::vector<PendingClient> &pending,
        const PeerCredentials &credentials) const noexcept {
        return static_cast<std::size_t>(std::count_if(
            pending.begin(), pending.end(),
            [&](const PendingClient &client) {
                return detail::same_peer_credentials(
                    client.connection_credentials, credentials);
            }));
    }

    [[nodiscard]] int poll_timeout(
        const std::vector<PendingClient> &pending,
        std::chrono::steady_clock::time_point next_admission,
        bool admission_suppressed) const noexcept {
        auto deadline = std::chrono::steady_clock::time_point::max();
        for (const PendingClient &client : pending) {
            deadline = std::min(deadline, client.deadline);
        }
        if (admission_suppressed) {
            deadline = std::min(deadline, next_admission);
        }
        if (deadline == std::chrono::steady_clock::time_point::max()) return -1;

        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) return 0;
        auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(
            deadline - now);
        // duration_cast floors; retain a finite wait instead of spinning during
        // the final sub-millisecond portion of a lease/refill interval.
        if (remaining <= std::chrono::milliseconds::zero()) {
            remaining = std::chrono::milliseconds(1);
        }
        return static_cast<int>(std::min<std::int64_t>(
            remaining.count(), static_cast<std::int64_t>(INT_MAX)));
    }

    void send_admission_error(
        int descriptor,
        const PeerCredentials *connection_credentials,
        ErrorCode code,
        std::string message) {
        std::uint64_t request_id = 1U;
        ControlOperation operation = ControlOperation::ping;

        // Never wait for an overloaded peer. If its complete request is
        // already queued, authenticate and decode only enough to correlate the
        // rejection. Otherwise the generic response is best effort and the
        // connection is closed immediately.
        auto record = receive_authenticated_datagram(
            descriptor, pass_pidfd_enabled_, MSG_DONTWAIT);
        if (record && connection_credentials != nullptr &&
            detail::same_peer_credentials(
                record.value().credentials, *connection_credentials)) {
            auto request = decode_control_packet(record.value().payload);
            if (request && request.value().kind == ControlKind::request) {
                request_id = request.value().request_id;
                operation = request.value().operation;
            }
        }
        static_cast<void>(send_packet(
            descriptor,
            error_response(request_id, operation, code, std::move(message))));
    }

    void accept_clients(std::vector<PendingClient> &pending) {
        std::size_t attempts = 0U;
        while (attempts < config_.maximum_accepts_per_interval) {
            UniqueFd client(::accept4(
                listener_.get(), nullptr, nullptr,
                SOCK_CLOEXEC | SOCK_NONBLOCK));
            if (!client) {
                if (errno == EINTR) continue;
                break;
            }
            ++attempts;

            const Status inherited = detail::verify_record_credentials(
                client.get(), pass_pidfd_enabled_, "local control");
            if (!inherited.ok()) {
                send_admission_error(
                    client.get(), nullptr,
                    inherited.code(), inherited.message());
                continue;
            }
            auto credentials = peer_credentials(client.get());
            if (!credentials) {
                send_admission_error(
                    client.get(), nullptr,
                    credentials.status().code(), credentials.status().message());
                continue;
            }
            if (config_.same_user_only &&
                credentials.value().user_id !=
                    static_cast<std::uint64_t>(::geteuid())) {
                send_admission_error(
                    client.get(), &credentials.value(), ErrorCode::unavailable,
                    "local control peer is not the daemon user");
                continue;
            }
            if (pending.size() >= config_.maximum_pending_clients) {
                send_admission_error(
                    client.get(), &credentials.value(),
                    ErrorCode::resource_exhausted,
                    "local control pending-client limit is full");
                continue;
            }
            if (pending_for_process(
                    pending, credentials.value()) >=
                config_.maximum_pending_clients_per_process) {
                send_admission_error(
                    client.get(), &credentials.value(),
                    ErrorCode::resource_exhausted,
                    "local control per-process pending-client limit is full");
                continue;
            }

            auto peer_pidfd = detail::connected_peer_pidfd(
                client.get(), "local control");
            if (!peer_pidfd) {
                send_admission_error(
                    client.get(), &credentials.value(),
                    peer_pidfd.status().code(), peer_pidfd.status().message());
                continue;
            }

            PendingClient admitted;
            admitted.descriptor = std::move(client);
            admitted.connection_credentials = credentials.value();
            admitted.peer_pidfd = std::move(peer_pidfd.value());
            admitted.deadline = std::chrono::steady_clock::now() +
                config_.request_timeout;
            pending.push_back(std::move(admitted));
        }
    }

    void handle_ready_client(PendingClient &client) noexcept {
        try {
            auto record = receive_authenticated_datagram(
                client.descriptor.get(), pass_pidfd_enabled_, MSG_DONTWAIT);
            if (!record) {
                static_cast<void>(send_packet(
                    client.descriptor.get(),
                    error_response(
                        1U, ControlOperation::ping,
                        record.status().code(), record.status().message())));
                return;
            }
            if (!detail::same_peer_credentials(
                    record.value().credentials,
                    client.connection_credentials)) {
                static_cast<void>(send_packet(
                    client.descriptor.get(),
                    error_response(
                        1U, ControlOperation::ping,
                        ErrorCode::unavailable,
                        "local control record came from a different process")));
                return;
            }

            auto request = decode_control_packet(record.value().payload);
            if (!request) {
                static_cast<void>(send_packet(
                    client.descriptor.get(),
                    error_response(
                        1U, ControlOperation::ping,
                        request.status().code(), request.status().message())));
                return;
            }
            if (request.value().kind != ControlKind::request) {
                static_cast<void>(send_packet(
                    client.descriptor.get(),
                    error_response(
                        request.value().request_id,
                        request.value().operation,
                        ErrorCode::protocol_error,
                        "local control server accepts request packets only")));
                return;
            }

            ControlPacket response = handler_(
                request.value(), record.value().credentials);
            response.kind = ControlKind::response;
            response.operation = request.value().operation;
            response.request_id = request.value().request_id;
            static_cast<void>(send_packet(client.descriptor.get(), response));
        } catch (const std::exception &exception) {
            static_cast<void>(send_packet(
                client.descriptor.get(),
                error_response(
                    1U, ControlOperation::ping,
                    ErrorCode::internal_error,
                    "local control handler failed: " +
                        std::string(exception.what()))));
        } catch (...) {
            static_cast<void>(send_packet(
                client.descriptor.get(),
                error_response(
                    1U, ControlOperation::ping,
                    ErrorCode::internal_error,
                    "local control handler failed unexpectedly")));
        }
    }

    void worker_main() noexcept {
        try {
            std::vector<PendingClient> pending;
            pending.reserve(config_.maximum_pending_clients);
            std::vector<struct pollfd> descriptors;
            descriptors.reserve((config_.maximum_pending_clients * 2U) + 2U);
            std::vector<std::size_t> socket_indices;
            socket_indices.reserve(config_.maximum_pending_clients);
            std::vector<std::size_t> pidfd_indices;
            pidfd_indices.reserve(config_.maximum_pending_clients);
            constexpr std::size_t kInvalidIndex =
                std::numeric_limits<std::size_t>::max();
            auto next_admission = std::chrono::steady_clock::time_point::min();

            while (!stop_requested_.load()) {
                const auto before_poll = std::chrono::steady_clock::now();
                const bool admission_suppressed = before_poll < next_admission;

                descriptors.clear();
                descriptors.push_back(pollfd{
                    admission_suppressed ? -1 : listener_.get(), POLLIN, 0});
                descriptors.push_back(pollfd{wake_.get(), POLLIN, 0});
                socket_indices.clear();
                pidfd_indices.clear();
                for (const PendingClient &client : pending) {
                    socket_indices.push_back(descriptors.size());
                    descriptors.push_back(
                        pollfd{client.descriptor.get(), POLLIN, 0});
                    if (client.peer_pidfd) {
                        pidfd_indices.push_back(descriptors.size());
                        descriptors.push_back(
                            pollfd{client.peer_pidfd.get(), POLLIN, 0});
                    } else {
                        pidfd_indices.push_back(kInvalidIndex);
                    }
                }

                int ready = -1;
                do {
                    ready = ::poll(
                        descriptors.data(), descriptors.size(),
                        poll_timeout(
                            pending, next_admission, admission_suppressed));
                } while (ready < 0 && errno == EINTR);
                if (ready < 0) break;

                if ((descriptors[1U].revents & POLLIN) != 0) {
                    drain_wake();
                    if (stop_requested_.load()) break;
                }

                for (PendingClient &client : pending) client.remove = false;
                std::size_t handled = 0U;
                for (std::size_t index = 0U; index < pending.size(); ++index) {
                    const short socket_events =
                        descriptors[socket_indices[index]].revents;
                    const short pidfd_events =
                        pidfd_indices[index] == kInvalidIndex
                        ? 0
                        : descriptors[pidfd_indices[index]].revents;
                    if ((socket_events & POLLIN) != 0 &&
                        handled < config_.maximum_requests_per_cycle) {
                        handle_ready_client(pending[index]);
                        pending[index].remove = true;
                        ++handled;
                    } else if ((socket_events &
                                (POLLERR | POLLHUP | POLLNVAL)) != 0 &&
                               (socket_events & POLLIN) == 0) {
                        pending[index].remove = true;
                    } else if ((socket_events & POLLIN) == 0 &&
                               (pidfd_events &
                                (POLLIN | POLLHUP | POLLERR | POLLNVAL)) != 0) {
                        // A descriptor inherited or passed to another process
                        // cannot extend the connection-time peer's admission
                        // lease after that exact process exits.
                        pending[index].remove = true;
                    }
                }

                // A record observed ready in this cycle is never expired merely
                // because the per-cycle handler budget was reached. The next
                // zero-latency poll services it before lease cleanup.
                const auto after_ready = std::chrono::steady_clock::now();
                for (std::size_t index = 0U; index < pending.size(); ++index) {
                    if (pending[index].remove) continue;
                    const short socket_events =
                        descriptors[socket_indices[index]].revents;
                    if ((socket_events & POLLIN) != 0) continue;
                    if (after_ready >= pending[index].deadline) {
                        static_cast<void>(send_packet(
                            pending[index].descriptor.get(),
                            error_response(
                                1U, ControlOperation::ping,
                                ErrorCode::timeout,
                                "local control request deadline elapsed before a complete record")));
                        pending[index].remove = true;
                    }
                }
                // Compact once without allocating. A hostile ready/close burst
                // therefore cannot turn bounded admission into quadratic erase
                // work or a per-cycle heap-allocation failure boundary.
                std::erase_if(
                    pending, [](const PendingClient &client) {
                        return client.remove;
                    });

                const auto now = std::chrono::steady_clock::now();
                if ((descriptors[0U].revents & POLLIN) != 0 &&
                    now >= next_admission) {
                    accept_clients(pending);
                    next_admission = now + config_.admission_interval;
                }
            }
        } catch (...) {
            // The public server boundary is noexcept. Unexpected allocation or
            // callback failures stop the server instead of terminating IoTox.
        }
        running_.store(false);
    }

    Config config_;
    Handler handler_;
    std::atomic<bool> start_called_{false};
    std::atomic<bool> stop_requested_{false};
    std::atomic<bool> running_{false};
    UniqueFd listener_;
    bool pass_pidfd_enabled_{false};
    UniqueFd wake_;
    mutable std::mutex wake_mutex_;
    std::mutex lifecycle_mutex_;
    std::mutex join_mutex_;
    SocketIdentity bound_identity_{};
    std::thread::id worker_id_{};
    std::thread worker_;
};

ControlServer::ControlServer(Config config, Handler handler)
    : impl_(std::make_unique<Impl>(std::move(config), std::move(handler))) {}
ControlServer::~ControlServer() = default;
Status ControlServer::start() { return impl_->start(); }
void ControlServer::stop() { impl_->stop(); }
bool ControlServer::running() const noexcept { return impl_->running(); }
const std::filesystem::path &ControlServer::socket_path() const noexcept {
    return impl_->socket_path();
}

Result<ControlPacket> control_request(
    const std::filesystem::path &socket_path,
    const ControlPacket &request,
    std::chrono::milliseconds timeout) {
    if (request.kind != ControlKind::request) {
        return Status{ErrorCode::invalid_argument,
                      "control_request requires a request packet"};
    }
    auto address = unix_address(socket_path);
    if (!address) return address.status();
    const Status parent = inspect_private_parent(socket_path.parent_path());
    if (!parent.ok()) return parent;

    struct stat metadata {};
    if (::lstat(socket_path.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status{ErrorCode::unavailable,
                          "IoTox control socket is unavailable: " +
                              socket_path.string()};
        }
        return system_status(
            ErrorCode::io_error,
            "unable to inspect IoTox control socket", socket_path);
    }
    if (!S_ISSOCK(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & 0077) != 0 ||
        (metadata.st_mode & 0600) != 0600) {
        return Status{ErrorCode::unavailable,
                      "IoTox control socket is not an owner-private socket"};
    }
    const SocketIdentity expected_identity{
        metadata.st_dev, metadata.st_ino, true};

    auto encoded = encode_control_packet(request);
    if (!encoded) {
        return encoded.status();
    }

    UniqueFd descriptor(::socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0));
    if (!descriptor) {
        return system_status(ErrorCode::io_error, "unable to create local control client socket");
    }
    auto pidfd_delivery = detail::enable_record_credentials(
        descriptor.get(), "local control client");
    if (!pidfd_delivery) return pidfd_delivery.status();
    const Status timeout_status = configure_timeout(descriptor.get(), timeout);
    if (!timeout_status.ok()) {
        return timeout_status;
    }
    if (::connect(descriptor.get(), reinterpret_cast<const sockaddr *>(&address.value()),
                  sizeof(sockaddr_un)) != 0) {
        if (errno == ENOENT || errno == ECONNREFUSED) {
            return Status{ErrorCode::unavailable,
                          "IoTox control socket is unavailable: " + socket_path.string()};
        }
        return system_status(ErrorCode::io_error, "unable to connect to IoTox control socket",
                             socket_path);
    }
    auto server_credentials = peer_credentials(descriptor.get());
    if (!server_credentials) return server_credentials.status();
    if (server_credentials.value().user_id !=
        static_cast<std::uint64_t>(::geteuid())) {
        return Status{ErrorCode::unavailable,
                      "IoTox control server is owned by another user"};
    }
    auto server_pidfd = detail::connected_peer_pidfd(
        descriptor.get(), "local control client");
    if (!server_pidfd) return server_pidfd.status();

    struct stat current {};
    if (::lstat(socket_path.c_str(), &current) != 0 ||
        !S_ISSOCK(current.st_mode) || current.st_uid != ::geteuid() ||
        (current.st_mode & 0077) != 0 || (current.st_mode & 0600) != 0600 ||
        current.st_dev != expected_identity.device ||
        current.st_ino != expected_identity.inode) {
        return Status{ErrorCode::unavailable,
                      "IoTox control socket changed while the connection was established"};
    }

    const Status sent = send_packet(descriptor.get(), request);
    if (!sent.ok()) {
        return sent;
    }
    const Status response_ready = wait_for_response(
        descriptor.get(), server_pidfd.value(), timeout);
    if (!response_ready.ok()) return response_ready;
    auto datagram = receive_authenticated_datagram(
        descriptor.get(), pidfd_delivery.value(), MSG_DONTWAIT);
    if (!datagram) {
        return datagram.status();
    }
    if (!detail::same_peer_credentials(
            datagram.value().credentials, server_credentials.value())) {
        return Status{
            ErrorCode::unavailable,
            "IoTox control response came from a different server process"};
    }
    auto response = decode_control_packet(datagram.value().payload);
    if (!response) {
        return response.status();
    }
    if (response.value().kind != ControlKind::response) {
        return Status{ErrorCode::protocol_error, "IoTox control peer returned a non-response packet"};
    }
    if (response.value().request_id != request.request_id ||
        response.value().operation != request.operation) {
        return Status{ErrorCode::protocol_error,
                      "IoTox control response does not match its request"};
    }
    return response;
}

}  // namespace iotox::local
