#include "iotox/local/terminal_socket.hpp"

#include "iotox/security/sodium.hpp"
#include "seqpacket_security.hpp"

#include <algorithm>
#include <array>
#include <climits>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
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

namespace iotox::local {
namespace {


class SensitiveVectorGuard {
  public:
    explicit SensitiveVectorGuard(std::vector<std::uint8_t> &bytes) noexcept
        : bytes_(&bytes) {}
    ~SensitiveVectorGuard() {
        if (bytes_ != nullptr) security::secure_wipe(*bytes_);
    }
    SensitiveVectorGuard(const SensitiveVectorGuard &) = delete;
    SensitiveVectorGuard &operator=(const SensitiveVectorGuard &) = delete;
    void dismiss() noexcept { bytes_ = nullptr; }
  private:
    std::vector<std::uint8_t> *bytes_;
};

class SensitivePacketGuard {
  public:
    explicit SensitivePacketGuard(TerminalPacket &packet) noexcept
        : packet_(&packet) {}
    ~SensitivePacketGuard() {
        if (packet_ != nullptr) security::secure_wipe(packet_->payload);
    }
    SensitivePacketGuard(const SensitivePacketGuard &) = delete;
    SensitivePacketGuard &operator=(const SensitivePacketGuard &) = delete;
    void dismiss() noexcept { packet_ = nullptr; }
  private:
    TerminalPacket *packet_;
};

class UniqueFd {
  public:
    UniqueFd() = default;
    explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
    ~UniqueFd() { reset(); }
    UniqueFd(const UniqueFd &) = delete;
    UniqueFd &operator=(const UniqueFd &) = delete;
    UniqueFd(UniqueFd &&other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    UniqueFd &operator=(UniqueFd &&other) noexcept {
        if (this != &other) reset(std::exchange(other.descriptor_, -1));
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] explicit operator bool() const noexcept { return descriptor_ >= 0; }
    int release() noexcept { return std::exchange(descriptor_, -1); }
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
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

Status system_status(
    ErrorCode code,
    std::string operation,
    const std::filesystem::path &path = {}) {
    const int saved_errno = errno;
    if (!path.empty()) operation += " '" + path.string() + "'";
    operation += ": ";
    operation += std::strerror(saved_errno);
    return Status{code, std::move(operation)};
}

Result<sockaddr_un> unix_address(const std::filesystem::path &socket_path) {
    if (!socket_path.is_absolute()) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal socket path must be absolute"};
    }
    const std::string path = socket_path.string();
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    if (path.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal socket path is empty"};
    }
    if (path.size() >= sizeof(address.sun_path)) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal socket path exceeds the Unix-domain limit"};
    }
    if (path.find('\0') != std::string::npos) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal socket path contains an embedded NUL byte"};
    }
    std::memcpy(address.sun_path, path.c_str(), path.size() + 1U);
    return address;
}

Status inspect_private_parent(const std::filesystem::path &parent) {
    if (parent.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal socket must have an explicit parent directory"};
    }
    struct stat metadata {};
    if (::lstat(parent.c_str(), &metadata) != 0) {
        return system_status(
            ErrorCode::io_error,
            "unable to inspect local terminal parent directory", parent);
    }
    if (!S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "local terminal parent is not a real directory: " +
                          parent.string()};
    }
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "local terminal parent is owned by another user: " +
                          parent.string()};
    }
    if ((metadata.st_mode & 0077) != 0) {
        return Status{ErrorCode::io_error,
                      "local terminal parent must not grant group or other permissions: " +
                          parent.string()};
    }
    return Status::success();
}

Result<SocketIdentity> inspect_owned_socket_identity(
    const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        return system_status(ErrorCode::io_error,
                             "unable to inspect local terminal socket", path);
    }
    if (!S_ISSOCK(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "local terminal path is not a socket owned by the daemon user: " +
                          path.string()};
    }
    SocketIdentity identity;
    identity.device = metadata.st_dev;
    identity.inode = metadata.st_ino;
    identity.present = true;
    return identity;
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
        return errno == ENOENT
            ? Status::success()
            : system_status(ErrorCode::io_error,
                            "unable to inspect local terminal socket", path);
    }
    if (!S_ISSOCK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "refusing to replace non-socket local terminal path '" +
                          path.string() + "'"};
    }
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "refusing to remove local terminal socket owned by another user: " +
                          path.string()};
    }

    auto address = unix_address(path);
    if (!address) return address.status();
    UniqueFd probe(::socket(
        AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0));
    if (!probe) {
        return system_status(ErrorCode::io_error,
                             "unable to probe existing local terminal socket");
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
                      "another IoTox terminal server is already listening at '" +
                          path.string() + "'"};
    }
    if (errno != ECONNREFUSED && errno != ENOENT) {
        return system_status(ErrorCode::io_error,
                             "unable to probe existing local terminal socket", path);
    }

    // Re-check the inode after the probe so a replacement path is never
    // unlinked on the strength of stale metadata.
    struct stat current {};
    if (::lstat(path.c_str(), &current) != 0) {
        return errno == ENOENT
            ? Status::success()
            : system_status(ErrorCode::io_error,
                            "unable to re-inspect local terminal socket", path);
    }
    if (!S_ISSOCK(current.st_mode) || current.st_uid != ::geteuid() ||
        current.st_dev != metadata.st_dev || current.st_ino != metadata.st_ino) {
        return Status{ErrorCode::unavailable,
                      "local terminal socket changed while stale ownership was checked"};
    }
    if (::unlink(path.c_str()) != 0) {
        return system_status(ErrorCode::io_error,
                             "unable to remove stale local terminal socket", path);
    }
    return Status::success();
}

Result<PeerCredentials> peer_credentials(int descriptor) {
    return detail::connected_peer_credentials(descriptor, "local terminal");
}

Status wait_fd(int descriptor, short events, std::chrono::milliseconds timeout) {
    if (timeout < std::chrono::milliseconds::zero()) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal I/O timeout cannot be negative"};
    }
    struct pollfd poll_descriptor {descriptor, events, 0};
    int ready = -1;
    do {
        ready = ::poll(&poll_descriptor, 1U,
                       static_cast<int>(std::min<std::int64_t>(
                           timeout.count(), static_cast<std::int64_t>(INT_MAX))));
    } while (ready < 0 && errno == EINTR);
    if (ready < 0) {
        return system_status(ErrorCode::io_error,
                             "unable to poll local terminal descriptor");
    }
    if (ready == 0) {
        return Status{ErrorCode::timeout,
                      "local terminal I/O deadline elapsed"};
    }
    if ((poll_descriptor.revents & (POLLERR | POLLNVAL)) != 0) {
        return Status{ErrorCode::io_error,
                      "local terminal descriptor reported an I/O error"};
    }
    if ((poll_descriptor.revents & POLLHUP) != 0 &&
        (poll_descriptor.revents & events) == 0) {
        return Status{ErrorCode::unavailable,
                      "local terminal peer closed the connection"};
    }
    if ((poll_descriptor.revents & events) == 0) {
        return Status{ErrorCode::io_error,
                      "local terminal descriptor did not report the requested readiness"};
    }
    return Status::success();
}

Status send_bytes(
    int descriptor,
    std::span<const std::uint8_t> bytes,
    std::chrono::milliseconds timeout) {
    if (timeout < std::chrono::milliseconds::zero()) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal I/O timeout cannot be negative"};
    }
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    for (;;) {
        const ssize_t count = ::send(
            descriptor, bytes.data(), bytes.size(), MSG_NOSIGNAL | MSG_DONTWAIT);
        if (count >= 0) {
            return static_cast<std::size_t>(count) == bytes.size()
                ? Status::success()
                : Status{ErrorCode::io_error,
                         "local terminal seqpacket send was unexpectedly partial"};
        }
        if (errno == EINTR) continue;
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            return system_status(ErrorCode::io_error,
                                 "unable to send local terminal packet");
        }
        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) {
            return Status{ErrorCode::timeout,
                          "local terminal send deadline elapsed"};
        }
        const Status writable = wait_fd(
            descriptor, POLLOUT,
            std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now));
        if (!writable.ok()) return writable;
    }
}

Result<detail::ReceivedSeqpacket> receive_authenticated_bytes(
    int descriptor,
    std::chrono::milliseconds timeout,
    bool require_pidfd) {
    const Status readable = wait_fd(descriptor, POLLIN, timeout);
    if (!readable.ok()) return readable;
    return detail::receive_seqpacket(
        descriptor, kTerminalMaxPacketSize, true, require_pidfd,
        MSG_DONTWAIT, "local terminal");
}

TerminalPacket error_packet(
    std::uint64_t stream_id,
    ErrorCode code,
    std::string detail) {
    TerminalPacket packet;
    packet.type = TerminalPacketType::error;
    packet.stream_id = stream_id == 0U ? 1U : stream_id;
    packet.status = code == ErrorCode::ok ? ErrorCode::internal_error : code;
    if (detail.empty()) detail = "local terminal request failed";
    if (detail.size() > 1024U) detail.resize(1024U);
    packet.payload.assign(detail.begin(), detail.end());
    return packet;
}

Status send_packet(
    int descriptor,
    const TerminalPacket &packet,
    std::chrono::milliseconds timeout) {
    auto encoded = encode_terminal_packet(packet);
    if (!encoded) return encoded.status();
    SensitiveVectorGuard wipe_encoded(encoded.value());
    return send_bytes(descriptor, encoded.value(), timeout);
}

Status send_error_packet(
    int descriptor,
    std::uint64_t stream_id,
    ErrorCode code,
    std::string detail,
    std::chrono::milliseconds timeout) {
    TerminalPacket packet = error_packet(stream_id, code, std::move(detail));
    SensitivePacketGuard wipe_packet(packet);
    return send_packet(descriptor, packet, timeout);
}

std::chrono::milliseconds bounded_remaining_timeout(
    std::chrono::steady_clock::time_point deadline,
    std::chrono::milliseconds ceiling) {
    if (deadline == std::chrono::steady_clock::time_point::max()) {
        return ceiling;
    }
    const auto now = std::chrono::steady_clock::now();
    if (now >= deadline) return std::chrono::milliseconds::zero();
    auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(
        deadline - now);
    // duration_cast floors. Preserve one final finite syscall budget rather
    // than turning a positive sub-millisecond remainder into an early close.
    if (remaining <= std::chrono::milliseconds::zero()) {
        remaining = std::chrono::milliseconds(1);
    }
    return std::min(ceiling, remaining);
}

}  // namespace

class TerminalServer::Impl {
  public:
    Impl(
        Config config,
        PacketHandler packet_handler,
        DrainHandler drain_handler,
        DisconnectHandler disconnect_handler)
        : config_(std::move(config)),
          packet_handler_(std::move(packet_handler)),
          drain_handler_(std::move(drain_handler)),
          disconnect_handler_(std::move(disconnect_handler)) {}

    ~Impl() { stop(); }

    Status start() {
        std::scoped_lock lifecycle_lock(lifecycle_mutex_);
        bool expected = false;
        if (!start_called_.compare_exchange_strong(expected, true)) {
            return Status{ErrorCode::invalid_argument,
                          "local terminal server start() may only be called once"};
        }
        if (!packet_handler_ || !drain_handler_) {
            return Status{ErrorCode::invalid_argument,
                          "local terminal server handlers are incomplete"};
        }
        if (config_.backlog < 1 || config_.backlog > 128 ||
            config_.poll_interval <= std::chrono::milliseconds::zero() ||
            config_.poll_interval > std::chrono::seconds(1) ||
            config_.open_timeout <= std::chrono::milliseconds::zero() ||
            config_.open_timeout > std::chrono::seconds(60) ||
            config_.detach_drain_timeout <=
                std::chrono::milliseconds::zero() ||
            config_.detach_drain_timeout > std::chrono::seconds(5) ||
            config_.maximum_packets_per_cycle == 0U ||
            config_.maximum_packets_per_cycle > 1024U ||
            config_.contender_open_timeout <=
                std::chrono::milliseconds::zero() ||
            config_.contender_open_timeout > std::chrono::seconds(5) ||
            config_.contender_admission_interval <=
                std::chrono::milliseconds::zero() ||
            config_.contender_admission_interval >
                std::chrono::seconds(1) ||
            config_.maximum_pending_contenders == 0U ||
            config_.maximum_pending_contenders > 256U ||
            config_.maximum_pending_contenders_per_process == 0U ||
            config_.maximum_pending_contenders_per_process >
                config_.maximum_pending_contenders ||
            config_.maximum_contender_accepts_per_interval == 0U ||
            config_.maximum_contender_accepts_per_interval > 256U ||
            config_.maximum_contender_records_per_cycle == 0U ||
            config_.maximum_contender_records_per_cycle > 256U ||
            (config_.socket_mode & ~0777U) != 0U ||
            (config_.socket_mode & 0077U) != 0U ||
            (config_.socket_mode & 0600U) != 0600U) {
            return Status{ErrorCode::invalid_argument,
                          "local terminal server limits or permissions are invalid"};
        }
        auto address = unix_address(config_.socket_path);
        if (!address) return address.status();
        const Status parent = inspect_private_parent(config_.socket_path.parent_path());
        if (!parent.ok()) return parent;
        const Status stale = remove_owned_stale_socket(config_.socket_path);
        if (!stale.ok()) return stale;

        UniqueFd listener(::socket(
            AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0));
        if (!listener) {
            return system_status(ErrorCode::io_error,
                                 "unable to create local terminal socket");
        }
        auto pidfd_delivery = detail::enable_record_credentials(
            listener.get(), "local terminal");
        if (!pidfd_delivery) return pidfd_delivery.status();
        if (::bind(listener.get(),
                   reinterpret_cast<const sockaddr *>(&address.value()),
                   sizeof(sockaddr_un)) != 0) {
            return system_status(ErrorCode::io_error,
                                 "unable to bind local terminal socket",
                                 config_.socket_path);
        }
        auto identity = inspect_owned_socket_identity(config_.socket_path);
        if (!identity) {
            static_cast<void>(::unlink(config_.socket_path.c_str()));
            return identity.status();
        }
        const SocketIdentity bound_identity = identity.value();
        if (::chmod(config_.socket_path.c_str(),
                    static_cast<mode_t>(config_.socket_mode)) != 0) {
            const Status failed = system_status(
                ErrorCode::io_error,
                "unable to set local terminal socket permissions",
                config_.socket_path);
            unlink_if_same_socket(config_.socket_path, bound_identity);
            return failed;
        }
        if (::listen(listener.get(), config_.backlog) != 0) {
            const Status failed = system_status(
                ErrorCode::io_error,
                "unable to listen on local terminal socket",
                config_.socket_path);
            unlink_if_same_socket(config_.socket_path, bound_identity);
            return failed;
        }
        UniqueFd wake(::eventfd(0U, EFD_CLOEXEC | EFD_NONBLOCK));
        if (!wake) {
            const Status failed = system_status(
                ErrorCode::io_error,
                "unable to create local terminal wake event");
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
            {
                std::scoped_lock wake_lock(wake_mutex_);
                wake_.reset();
            }
            unlink_if_same_socket(config_.socket_path, bound_identity_);
            bound_identity_ = {};
            return Status{ErrorCode::resource_exhausted,
                          "unable to start local terminal worker: " +
                              std::string(exception.what())};
        }
        return Status::success();
    }

    void stop() {
        bool called_from_worker = false;
        {
            // Serialize against start() so stop cannot observe a partially
            // published listener/wake/thread tuple. Do not retain this lock
            // while joining: a packet or disconnect callback is permitted to
            // request stop from the worker thread itself.
            std::scoped_lock lifecycle_lock(lifecycle_mutex_);
            stop_requested_.store(true);
            called_from_worker =
                worker_id_ != std::thread::id{} &&
                worker_id_ == std::this_thread::get_id();
        }
        notify();
        if (called_from_worker) return;

        {
            // Only one external caller may inspect or join std::thread at a
            // time. A worker callback returns above, avoiding the classic
            // join-lock cycle where an owner waits for a worker that is itself
            // waiting to enter stop().
            std::scoped_lock join_lock(join_mutex_);
            if (worker_.joinable()) worker_.join();
        }
        {
            std::scoped_lock lifecycle_lock(lifecycle_mutex_);
            client_connected_.store(false);
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

    void notify() noexcept {
        std::scoped_lock wake_lock(wake_mutex_);
        if (!wake_) return;
        const std::uint64_t one = 1U;
        const ssize_t ignored = ::write(wake_.get(), &one, sizeof(one));
        static_cast<void>(ignored);
    }

    bool running() const noexcept { return running_.load(); }
    bool client_connected() const noexcept { return client_connected_.load(); }
    const std::filesystem::path &socket_path() const noexcept {
        return config_.socket_path;
    }

  private:
    void drain_wake() noexcept {
        std::uint64_t value = 0U;
        while (::read(wake_.get(), &value, sizeof(value)) > 0) {}
    }

    struct PendingContender {
        UniqueFd descriptor;
        PeerCredentials connection_credentials;
        std::chrono::steady_clock::time_point deadline;
        bool remove{false};
    };

    struct AcceptedClient {
        UniqueFd descriptor;
        PeerCredentials connection_credentials;
        detail::OwnedDescriptor peer_pidfd;
    };

    [[nodiscard]] std::size_t contenders_for_process(
        const std::vector<PendingContender> &contenders,
        const PeerCredentials &credentials) const noexcept {
        return static_cast<std::size_t>(std::count_if(
            contenders.begin(), contenders.end(),
            [&](const PendingContender &contender) {
                return detail::same_peer_credentials(
                    contender.connection_credentials, credentials);
            }));
    }

    void send_contender_error(
        int descriptor,
        const PeerCredentials *connection_credentials,
        ErrorCode code,
        std::string message) {
        std::uint64_t stream_id = 1U;

        // Never wait for a contender and never dispatch its record. A complete
        // first packet that is already queued is authenticated and decoded only
        // to correlate the bounded rejection with the attempted stream.
        auto record = receive_authenticated_bytes(
            descriptor, std::chrono::milliseconds::zero(),
            pass_pidfd_enabled_);
        if (record && connection_credentials != nullptr &&
            detail::same_peer_credentials(
                record.value().credentials, *connection_credentials)) {
            SensitiveVectorGuard wipe_received(record.value().payload);
            auto packet = decode_terminal_packet(record.value().payload);
            if (packet) {
                SensitivePacketGuard wipe_packet(packet.value());
                stream_id = packet.value().stream_id;
            }
        }
        static_cast<void>(send_error_packet(
            descriptor, stream_id, code, std::move(message),
            std::chrono::milliseconds::zero()));
    }

    void accept_contenders(
        std::vector<PendingContender> &contenders) {
        std::size_t attempts = 0U;
        while (attempts < config_.maximum_contender_accepts_per_interval) {
            UniqueFd contender(::accept4(
                listener_.get(), nullptr, nullptr,
                SOCK_CLOEXEC | SOCK_NONBLOCK));
            if (!contender) {
                if (errno == EINTR) continue;
                break;
            }
            ++attempts;

            const Status inherited = detail::verify_record_credentials(
                contender.get(), pass_pidfd_enabled_, "local terminal");
            if (!inherited.ok()) {
                send_contender_error(
                    contender.get(), nullptr,
                    inherited.code(), inherited.message());
                continue;
            }
            auto credentials = peer_credentials(contender.get());
            if (!credentials) {
                send_contender_error(
                    contender.get(), nullptr,
                    credentials.status().code(), credentials.status().message());
                continue;
            }
            if (config_.same_user_only &&
                credentials.value().user_id !=
                    static_cast<std::uint64_t>(::geteuid())) {
                send_contender_error(
                    contender.get(), &credentials.value(),
                    ErrorCode::unavailable,
                    "local terminal peer is not the daemon user");
                continue;
            }
            if (contenders.size() >= config_.maximum_pending_contenders) {
                send_contender_error(
                    contender.get(), &credentials.value(),
                    ErrorCode::resource_exhausted,
                    "local terminal pending-contender limit is full");
                continue;
            }
            if (contenders_for_process(
                    contenders, credentials.value()) >=
                config_.maximum_pending_contenders_per_process) {
                send_contender_error(
                    contender.get(), &credentials.value(),
                    ErrorCode::resource_exhausted,
                    "local terminal per-process contender limit is full");
                continue;
            }

            PendingContender admitted;
            admitted.descriptor = std::move(contender);
            admitted.connection_credentials = credentials.value();
            admitted.deadline = std::chrono::steady_clock::now() +
                config_.contender_open_timeout;
            contenders.push_back(std::move(admitted));
        }
    }

    void process_contenders(
        std::vector<PendingContender> &contenders,
        const std::vector<struct pollfd> &descriptors,
        std::size_t descriptor_offset) {
        for (PendingContender &contender : contenders) {
            contender.remove = false;
        }
        std::size_t handled = 0U;
        for (std::size_t index = 0U; index < contenders.size(); ++index) {
            const short events = descriptors[descriptor_offset + index].revents;
            if ((events & POLLIN) != 0 &&
                handled < config_.maximum_contender_records_per_cycle) {
                send_contender_error(
                    contenders[index].descriptor.get(),
                    &contenders[index].connection_credentials,
                    ErrorCode::resource_exhausted,
                    "another local terminal client is already attached");
                contenders[index].remove = true;
                ++handled;
            } else if ((events & (POLLERR | POLLHUP | POLLNVAL)) != 0 &&
                       (events & POLLIN) == 0) {
                contenders[index].remove = true;
            }
        }

        // Preserve a ready record when this cycle's bounded decode budget is
        // exhausted. It is serviced by the next zero-latency poll instead of
        // being replaced by a generic deadline response.
        const auto now = std::chrono::steady_clock::now();
        for (std::size_t index = 0U; index < contenders.size(); ++index) {
            if (contenders[index].remove) continue;
            const short events = descriptors[descriptor_offset + index].revents;
            if ((events & POLLIN) != 0) continue;
            if (now >= contenders[index].deadline) {
                send_contender_error(
                    contenders[index].descriptor.get(),
                    &contenders[index].connection_credentials,
                    ErrorCode::resource_exhausted,
                    "another local terminal client is already attached");
                contenders[index].remove = true;
            }
        }
        // Compact once without allocating. A hostile contender burst cannot
        // amplify bounded admission into quadratic descriptor movement or a
        // per-cycle heap-allocation failure boundary.
        std::erase_if(
            contenders, [](const PendingContender &contender) {
                return contender.remove;
            });
    }

    Result<AcceptedClient> accept_client() {
        for (;;) {
            UniqueFd client(::accept4(
                listener_.get(), nullptr, nullptr,
                SOCK_CLOEXEC | SOCK_NONBLOCK));
            if (!client) {
                if (errno == EINTR) continue;
                return system_status(ErrorCode::io_error,
                                     "unable to accept local terminal client");
            }
            const Status inherited = detail::verify_record_credentials(
                client.get(), pass_pidfd_enabled_, "local terminal");
            if (!inherited.ok()) {
                static_cast<void>(send_error_packet(
                    client.get(), 1U, inherited.code(), inherited.message(),
                    std::chrono::milliseconds(20)));
                continue;
            }
            auto credentials = peer_credentials(client.get());
            if (!credentials) return credentials.status();
            if (config_.same_user_only &&
                credentials.value().user_id !=
                    static_cast<std::uint64_t>(::geteuid())) {
                static_cast<void>(send_error_packet(
                    client.get(), 1U, ErrorCode::unavailable,
                    "local terminal peer is not the daemon user",
                    std::chrono::milliseconds(20)));
                continue;
            }
            auto peer_pidfd = detail::connected_peer_pidfd(
                client.get(), "local terminal");
            if (!peer_pidfd) {
                static_cast<void>(send_error_packet(
                    client.get(), 1U,
                    peer_pidfd.status().code(), peer_pidfd.status().message(),
                    std::chrono::milliseconds(20)));
                continue;
            }
            return AcceptedClient{
                std::move(client), credentials.value(),
                std::move(peer_pidfd.value())};
        }
    }

    bool drain_outbound(
        int descriptor,
        std::uint64_t stream_id,
        std::chrono::steady_clock::time_point deadline) noexcept {
        try {
            std::vector<TerminalPacket> packets = drain_handler_(
                stream_id, config_.maximum_packets_per_cycle);
            if (packets.size() > config_.maximum_packets_per_cycle) {
                static_cast<void>(send_error_packet(
                    descriptor, stream_id, ErrorCode::internal_error,
                    "local terminal drain handler exceeded its packet bound",
                    std::chrono::milliseconds(20)));
                return false;
            }
            for (std::size_t index = 0U; index < packets.size(); ++index) {
                TerminalPacket &packet = packets[index];
                packet.stream_id = stream_id;
                const std::chrono::milliseconds send_timeout =
                    bounded_remaining_timeout(
                        deadline, std::chrono::milliseconds(100));
                if (send_timeout <= std::chrono::milliseconds::zero()) {
                    for (std::size_t remaining = index;
                         remaining < packets.size(); ++remaining) {
                        security::secure_wipe(packets[remaining].payload);
                    }
                    return false;
                }
                const Status sent = send_packet(
                    descriptor, packet, send_timeout);
                security::secure_wipe(packet.payload);
                if (!sent.ok()) {
                    for (std::size_t remaining = index + 1U;
                         remaining < packets.size(); ++remaining) {
                        security::secure_wipe(packets[remaining].payload);
                    }
                    return false;
                }
            }
            return true;
        } catch (...) {
            static_cast<void>(send_error_packet(
                descriptor, stream_id, ErrorCode::internal_error,
                "local terminal drain handler failed unexpectedly",
                std::chrono::milliseconds(20)));
            return false;
        }
    }

    void serve_client(
        UniqueFd client,
        const PeerCredentials &connection_credentials,
        detail::OwnedDescriptor connection_pidfd) noexcept {
        client_connected_.store(true);
        std::uint64_t stream_id = 0U;
        bool opened = false;
        bool detaching = false;
        bool owner_bound = false;
        PeerCredentials owner_credentials = connection_credentials;
        detail::OwnedDescriptor owner_pidfd = std::move(connection_pidfd);
        std::chrono::steady_clock::time_point detach_deadline{};
        const auto open_deadline =
            std::chrono::steady_clock::now() + config_.open_timeout;
        auto next_contender_admission =
            std::chrono::steady_clock::time_point::min();
        std::vector<PendingContender> contenders;
        std::vector<struct pollfd> descriptors;
        try {
            contenders.reserve(config_.maximum_pending_contenders);
            descriptors.reserve(config_.maximum_pending_contenders + 4U);
            while (!stop_requested_.load()) {
                const auto before_poll = std::chrono::steady_clock::now();
                std::chrono::milliseconds poll_timeout = config_.poll_interval;
                if (detaching) {
                    if (before_poll >= detach_deadline) break;
                    auto remaining =
                        std::chrono::duration_cast<std::chrono::milliseconds>(
                            detach_deadline - before_poll);
                    if (remaining <= std::chrono::milliseconds::zero()) {
                        remaining = std::chrono::milliseconds(1);
                    }
                    poll_timeout = std::min(poll_timeout, remaining);
                } else if (!opened) {
                    if (before_poll >= open_deadline) {
                        static_cast<void>(send_error_packet(
                            client.get(), 1U, ErrorCode::timeout,
                            "local terminal OPEN deadline elapsed before the first packet",
                            std::chrono::milliseconds(100)));
                        break;
                    }
                    auto remaining =
                        std::chrono::duration_cast<std::chrono::milliseconds>(
                            open_deadline - before_poll);
                    // duration_cast floors. Preserve a finite wait instead of
                    // spinning when less than one millisecond remains.
                    if (remaining <= std::chrono::milliseconds::zero()) {
                        remaining = std::chrono::milliseconds(1);
                    }
                    poll_timeout = std::min(poll_timeout, remaining);
                }

                const auto tighten_poll_timeout =
                    [&](std::chrono::steady_clock::time_point deadline) {
                        if (before_poll >= deadline) {
                            poll_timeout = std::chrono::milliseconds::zero();
                            return;
                        }
                        auto remaining =
                            std::chrono::duration_cast<std::chrono::milliseconds>(
                                deadline - before_poll);
                        if (remaining <= std::chrono::milliseconds::zero()) {
                            remaining = std::chrono::milliseconds(1);
                        }
                        poll_timeout = std::min(poll_timeout, remaining);
                    };
                for (const PendingContender &contender : contenders) {
                    tighten_poll_timeout(contender.deadline);
                }
                const bool admission_suppressed =
                    !detaching && before_poll < next_contender_admission;
                if (admission_suppressed) {
                    tighten_poll_timeout(next_contender_admission);
                }

                descriptors.clear();
                descriptors.push_back(pollfd{
                    // Once DETACH commits, leave successors queued in the
                    // kernel backlog until the bounded ACK drain releases the
                    // old stream. Polling a readable listener without
                    // accepting it would otherwise create a busy loop. Active
                    // streams also rate-limit contender admission so a local
                    // connect flood cannot monopolize this worker.
                    detaching || admission_suppressed ? -1 : listener_.get(),
                    POLLIN, 0});
                descriptors.push_back(pollfd{wake_.get(), POLLIN, 0});
                descriptors.push_back(pollfd{client.get(), POLLIN, 0});
                descriptors.push_back(pollfd{
                    owner_pidfd ? owner_pidfd.get() : -1, POLLIN, 0});
                for (const PendingContender &contender : contenders) {
                    descriptors.push_back(pollfd{
                        contender.descriptor.get(), POLLIN, 0});
                }
                int ready = -1;
                do {
                    ready = ::poll(
                        descriptors.data(), descriptors.size(),
                        static_cast<int>(poll_timeout.count()));
                } while (ready < 0 && errno == EINTR);
                if (ready < 0) break;
                if ((descriptors[1U].revents & POLLIN) != 0) drain_wake();
                if (stop_requested_.load()) break;
                if ((descriptors[3U].revents &
                     (POLLIN | POLLHUP | POLLERR | POLLNVAL)) != 0) {
                    static_cast<void>(send_error_packet(
                        client.get(), stream_id, ErrorCode::unavailable,
                        "local terminal controller process exited",
                        std::chrono::milliseconds(20)));
                    break;
                }
                const short client_events = descriptors[2U].revents;
                const bool client_terminal_event =
                    (client_events & (POLLERR | POLLHUP | POLLNVAL)) != 0;
                if (client_terminal_event && (client_events & POLLIN) == 0) {
                    // Release a dead controller before touching queued
                    // contenders. A replacement that arrived in the same
                    // poll cycle must not be denied on behalf of a peer that
                    // is already gone.
                    break;
                }
                if ((client_events & POLLIN) != 0) {
                    auto record = receive_authenticated_bytes(
                        client.get(), std::chrono::milliseconds::zero(),
                        pass_pidfd_enabled_);
                    if (!record) {
                        if (record.status().code() != ErrorCode::timeout) {
                            static_cast<void>(send_error_packet(
                                client.get(), stream_id,
                                record.status().code(), record.status().message(),
                                std::chrono::milliseconds(100)));
                            break;
                        }
                    } else {
                        SensitiveVectorGuard wipe_received(
                            record.value().payload);
                        if (!detail::same_peer_credentials(
                                record.value().credentials,
                                connection_credentials) ||
                            (owner_bound && !detail::same_peer_credentials(
                                record.value().credentials,
                                owner_credentials))) {
                            static_cast<void>(send_error_packet(
                                client.get(), stream_id,
                                ErrorCode::unavailable,
                                "local terminal record came from a different process",
                                std::chrono::milliseconds(100)));
                            break;
                        }
                        if (!owner_bound) {
                            owner_credentials = record.value().credentials;
                            if (!owner_pidfd && record.value().sender_pidfd) {
                                owner_pidfd = std::move(
                                    record.value().sender_pidfd);
                            } else if (!owner_pidfd) {
                                auto fallback_pidfd = detail::open_process_pidfd(
                                    owner_credentials.process_id,
                                    "local terminal");
                                if (!fallback_pidfd) {
                                    static_cast<void>(send_error_packet(
                                        client.get(), stream_id,
                                        fallback_pidfd.status().code(),
                                        fallback_pidfd.status().message(),
                                        std::chrono::milliseconds(100)));
                                    break;
                                }
                                owner_pidfd = std::move(fallback_pidfd.value());
                            }
                            owner_bound = true;
                        }
                        if (owner_pidfd) {
                            auto exited = detail::pidfd_has_exited(
                                owner_pidfd.get(), "local terminal");
                            if (!exited || exited.value()) {
                                static_cast<void>(send_error_packet(
                                    client.get(), stream_id,
                                    exited ? ErrorCode::unavailable
                                           : exited.status().code(),
                                    exited
                                        ? "local terminal controller process exited"
                                        : exited.status().message(),
                                    std::chrono::milliseconds(100)));
                                break;
                            }
                        }
                        auto packet = decode_terminal_packet(
                            record.value().payload);
                        if (!packet) {
                            static_cast<void>(send_error_packet(
                                client.get(), stream_id,
                                packet.status().code(), packet.status().message(),
                                std::chrono::milliseconds(100)));
                            break;
                        }
                        SensitivePacketGuard wipe_packet(packet.value());
                        const bool first_packet = !opened;
                        if (first_packet) {
                            stream_id = packet.value().stream_id;
                            if (packet.value().type != TerminalPacketType::open) {
                                static_cast<void>(send_error_packet(
                                    client.get(), stream_id,
                                    ErrorCode::protocol_error,
                                    "first local terminal packet must be OPEN",
                                    std::chrono::milliseconds(100)));
                                break;
                            }
                        } else if (packet.value().stream_id != stream_id ||
                                   packet.value().type == TerminalPacketType::open) {
                            static_cast<void>(send_error_packet(
                                client.get(), stream_id,
                                ErrorCode::protocol_error,
                                "local terminal stream ID changed or OPEN was repeated",
                                std::chrono::milliseconds(100)));
                            break;
                        }
                        if (detaching &&
                            packet.value().type !=
                                TerminalPacketType::output_ack) {
                            const std::chrono::milliseconds error_timeout =
                                bounded_remaining_timeout(
                                    detach_deadline,
                                    std::chrono::milliseconds(100));
                            if (error_timeout >
                                std::chrono::milliseconds::zero()) {
                                static_cast<void>(send_error_packet(
                                    client.get(), stream_id,
                                    ErrorCode::protocol_error,
                                    "only OUTPUT_ACK is valid after local DETACH",
                                    error_timeout));
                            }
                            break;
                        }
                        const Status handled = packet_handler_(
                            packet.value(), owner_credentials);
                        if (!handled.ok()) {
                            static_cast<void>(send_error_packet(
                                client.get(), stream_id,
                                handled.code(), handled.message(),
                                std::chrono::milliseconds(100)));
                            break;
                        }
                        // The stream becomes externally visible only after its
                        // OPEN handler commits successfully. Rejected OPENs do
                        // not trigger attachment-disconnect cleanup for state
                        // that was never published.
                        if (first_packet) opened = true;
                        if (packet.value().type ==
                            TerminalPacketType::detach) {
                            detaching = true;
                            detach_deadline = std::chrono::steady_clock::now() +
                                config_.detach_drain_timeout;
                        }
                    }
                }
                const auto outbound_deadline = detaching
                    ? detach_deadline
                    : std::chrono::steady_clock::time_point::max();
                if (opened &&
                    !drain_outbound(
                        client.get(), stream_id, outbound_deadline)) {
                    break;
                }
                // A client can render OUTPUT staged immediately before
                // DETACHED, send its cumulative ACK, and then close. When
                // POLLIN and HUP arrive together, keep consuming one ordered
                // record per cycle until the ACK queue is empty. The next poll
                // observes HUP without POLLIN and releases the stream.
                if (client_terminal_event && !detaching) break;
                process_contenders(contenders, descriptors, 4U);
                const auto after_cycle = std::chrono::steady_clock::now();
                if (!detaching &&
                    (descriptors[0U].revents & POLLIN) != 0 &&
                    after_cycle >= next_contender_admission) {
                    accept_contenders(contenders);
                    next_contender_admission = after_cycle +
                        config_.contender_admission_interval;
                }
            }
        } catch (const std::exception &exception) {
            if (stream_id != 0U) {
                static_cast<void>(send_error_packet(
                    client.get(), stream_id, ErrorCode::internal_error,
                    "local terminal server failed: " +
                        std::string(exception.what()),
                    std::chrono::milliseconds(20)));
            }
        } catch (...) {}

        if (opened && disconnect_handler_) {
            try {
                disconnect_handler_(
                    stream_id,
                    owner_bound ? owner_credentials : connection_credentials);
            } catch (...) {}
        }
        client_connected_.store(false);
    }

    void worker_main() noexcept {
        try {
            while (!stop_requested_.load()) {
                std::array<struct pollfd, 2U> descriptors{{
                    {listener_.get(), POLLIN, 0},
                    {wake_.get(), POLLIN, 0},
                }};
                int ready = -1;
                do {
                    ready = ::poll(descriptors.data(), descriptors.size(), -1);
                } while (ready < 0 && errno == EINTR);
                if (ready < 0) break;
                if ((descriptors[1U].revents & POLLIN) != 0) {
                    drain_wake();
                    if (stop_requested_.load()) break;
                }
                if ((descriptors[0U].revents & POLLIN) == 0) continue;
                auto accepted = accept_client();
                if (!accepted) continue;
                serve_client(
                    std::move(accepted.value().descriptor),
                    accepted.value().connection_credentials,
                    std::move(accepted.value().peer_pidfd));
            }
        } catch (...) {}
        client_connected_.store(false);
        running_.store(false);
    }

    Config config_;
    PacketHandler packet_handler_;
    DrainHandler drain_handler_;
    DisconnectHandler disconnect_handler_;
    std::atomic<bool> start_called_{false};
    std::atomic<bool> stop_requested_{false};
    std::atomic<bool> running_{false};
    std::atomic<bool> client_connected_{false};
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

TerminalServer::TerminalServer(
    Config config,
    PacketHandler packet_handler,
    DrainHandler drain_handler,
    DisconnectHandler disconnect_handler)
    : impl_(std::make_unique<Impl>(
          std::move(config), std::move(packet_handler),
          std::move(drain_handler), std::move(disconnect_handler))) {}
TerminalServer::~TerminalServer() = default;
Status TerminalServer::start() { return impl_->start(); }
void TerminalServer::stop() { impl_->stop(); }
void TerminalServer::notify() noexcept { impl_->notify(); }
bool TerminalServer::running() const noexcept { return impl_->running(); }
bool TerminalServer::client_connected() const noexcept {
    return impl_->client_connected();
}
const std::filesystem::path &TerminalServer::socket_path() const noexcept {
    return impl_->socket_path();
}

TerminalConnection::TerminalConnection() = default;
TerminalConnection::TerminalConnection(
    int descriptor,
    PeerCredentials server_credentials,
    bool require_server_pidfd) noexcept
    : descriptor_(descriptor),
      server_credentials_(server_credentials),
      require_server_pidfd_(require_server_pidfd) {}
TerminalConnection::~TerminalConnection() { close(); }
TerminalConnection::TerminalConnection(TerminalConnection &&other) noexcept
    : descriptor_(std::exchange(other.descriptor_, -1)),
      server_credentials_(other.server_credentials_),
      require_server_pidfd_(std::exchange(other.require_server_pidfd_, false)) {
    other.server_credentials_ = {};
}
TerminalConnection &TerminalConnection::operator=(TerminalConnection &&other) noexcept {
    if (this != &other) {
        close();
        descriptor_ = std::exchange(other.descriptor_, -1);
        server_credentials_ = other.server_credentials_;
        require_server_pidfd_ =
            std::exchange(other.require_server_pidfd_, false);
        other.server_credentials_ = {};
    }
    return *this;
}

Result<TerminalConnection> TerminalConnection::connect(
    const std::filesystem::path &socket_path,
    std::chrono::milliseconds timeout) {
    if (timeout <= std::chrono::milliseconds::zero()) {
        return Status{ErrorCode::invalid_argument,
                      "local terminal connect timeout must be positive"};
    }
    auto address = unix_address(socket_path);
    if (!address) return address.status();
    const Status parent = inspect_private_parent(socket_path.parent_path());
    if (!parent.ok()) return parent;

    struct stat metadata {};
    if (::lstat(socket_path.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status{ErrorCode::unavailable,
                          "IoTox terminal socket is unavailable: " +
                              socket_path.string()};
        }
        return system_status(ErrorCode::io_error,
                             "unable to inspect IoTox terminal socket", socket_path);
    }
    if (!S_ISSOCK(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & 0077) != 0 ||
        (metadata.st_mode & 0600) != 0600) {
        return Status{ErrorCode::unavailable,
                      "IoTox terminal socket is not an owner-private socket"};
    }
    const SocketIdentity expected_identity{
        metadata.st_dev, metadata.st_ino, true};

    UniqueFd descriptor(::socket(
        AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0));
    if (!descriptor) {
        return system_status(ErrorCode::io_error,
                             "unable to create local terminal client socket");
    }
    auto pidfd_delivery = detail::enable_record_credentials(
        descriptor.get(), "local terminal client");
    if (!pidfd_delivery) return pidfd_delivery.status();
    int result = -1;
    do {
        result = ::connect(
            descriptor.get(), reinterpret_cast<const sockaddr *>(&address.value()),
            sizeof(sockaddr_un));
    } while (result != 0 && errno == EINTR);
    if (result != 0 && errno != EINPROGRESS && errno != EAGAIN) {
        if (errno == ENOENT || errno == ECONNREFUSED) {
            return Status{ErrorCode::unavailable,
                          "IoTox terminal socket is unavailable: " +
                              socket_path.string()};
        }
        return system_status(ErrorCode::io_error,
                             "unable to connect to IoTox terminal socket", socket_path);
    }
    if (result != 0) {
        const Status writable = wait_fd(descriptor.get(), POLLOUT, timeout);
        if (!writable.ok()) return writable;
        int socket_error = 0;
        socklen_t length = sizeof(socket_error);
        if (::getsockopt(descriptor.get(), SOL_SOCKET, SO_ERROR,
                         &socket_error, &length) != 0) {
            return system_status(ErrorCode::io_error,
                                 "unable to finish local terminal connection");
        }
        if (socket_error != 0) {
            errno = socket_error;
            return system_status(ErrorCode::unavailable,
                                 "unable to connect to IoTox terminal socket",
                                 socket_path);
        }
    }
    auto credentials = peer_credentials(descriptor.get());
    if (!credentials) return credentials.status();
    if (credentials.value().user_id != static_cast<std::uint64_t>(::geteuid())) {
        return Status{ErrorCode::unavailable,
                      "IoTox terminal server is owned by another user"};
    }

    // The pathname is inspected both before and after connect. This does not
    // turn a same-UID process into a hostile security boundary, but it prevents
    // a connection from being accepted on the strength of metadata belonging
    // to a socket pathname that was replaced during the handshake.
    struct stat current {};
    if (::lstat(socket_path.c_str(), &current) != 0 ||
        !S_ISSOCK(current.st_mode) || current.st_uid != ::geteuid() ||
        (current.st_mode & 0077) != 0 || (current.st_mode & 0600) != 0600 ||
        current.st_dev != expected_identity.device ||
        current.st_ino != expected_identity.inode) {
        return Status{ErrorCode::unavailable,
                      "IoTox terminal socket changed while the connection was established"};
    }
    return TerminalConnection(
        descriptor.release(), credentials.value(), pidfd_delivery.value());
}

Status TerminalConnection::send(
    const TerminalPacket &packet,
    std::chrono::milliseconds timeout) {
    if (!valid()) {
        return Status{ErrorCode::unavailable,
                      "local terminal connection is closed"};
    }
    return send_packet(descriptor_, packet, timeout);
}

Result<TerminalPacket> TerminalConnection::receive(
    std::chrono::milliseconds timeout) {
    if (!valid()) {
        return Status{ErrorCode::unavailable,
                      "local terminal connection is closed"};
    }
    auto record = receive_authenticated_bytes(
        descriptor_, timeout, require_server_pidfd_);
    if (!record) return record.status();
    SensitiveVectorGuard wipe_received(record.value().payload);
    if (!detail::same_peer_credentials(
            record.value().credentials, server_credentials_)) {
        return Status{
            ErrorCode::unavailable,
            "local terminal response came from a different server process"};
    }
    return decode_terminal_packet(record.value().payload);
}

int TerminalConnection::native_handle() const noexcept { return descriptor_; }
bool TerminalConnection::valid() const noexcept { return descriptor_ >= 0; }
void TerminalConnection::close() noexcept {
    if (descriptor_ >= 0) {
        static_cast<void>(::close(descriptor_));
        descriptor_ = -1;
    }
    server_credentials_ = {};
    require_server_pidfd_ = false;
}

}  // namespace iotox::local
