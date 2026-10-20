#include "iotox/route_health.hpp"

#include <algorithm>
#include <arpa/inet.h>
#include <array>
#include <cerrno>
#include <charconv>
#include <chrono>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <poll.h>
#include <span>
#include <sstream>
#include <sys/socket.h>
#include <unistd.h>
#include <vector>

namespace iotox::routes {
namespace {

constexpr std::uint32_t kMaximumHysteresisSamples = 64U;

class Descriptor {
  public:
    explicit Descriptor(int value) noexcept : value_(value) {}
    ~Descriptor() {
        if (value_ >= 0) {
            static_cast<void>(::close(value_));
        }
    }

    Descriptor(const Descriptor &) = delete;
    Descriptor &operator=(const Descriptor &) = delete;

    [[nodiscard]] int get() const noexcept { return value_; }

  private:
    int value_{-1};
};

struct NumericAddress {
    sockaddr_storage storage{};
    socklen_t length{0U};
    int family{AF_UNSPEC};
};

Result<NumericAddress> numeric_address(const Socks5ProxyEndpoint &endpoint) {
    NumericAddress output;
    sockaddr_in ipv4{};
    ipv4.sin_family = AF_INET;
    ipv4.sin_port = htons(endpoint.port);
    if (::inet_pton(AF_INET, endpoint.host.c_str(), &ipv4.sin_addr) == 1) {
        std::memcpy(&output.storage, &ipv4, sizeof(ipv4));
        output.length = sizeof(ipv4);
        output.family = AF_INET;
        return output;
    }

    sockaddr_in6 ipv6{};
    ipv6.sin6_family = AF_INET6;
    ipv6.sin6_port = htons(endpoint.port);
    if (::inet_pton(AF_INET6, endpoint.host.c_str(), &ipv6.sin6_addr) == 1) {
        std::memcpy(&output.storage, &ipv6, sizeof(ipv6));
        output.length = sizeof(ipv6);
        output.family = AF_INET6;
        return output;
    }
    return Status{ErrorCode::invalid_argument,
                  "route health requires a numeric SOCKS5 endpoint"};
}

LocalBoundaryHealth classify_connect_error(int error) noexcept {
    switch (error) {
        case ECONNREFUSED:
            return LocalBoundaryHealth::refused;
        case ETIMEDOUT:
            return LocalBoundaryHealth::timed_out;
        case ENETUNREACH:
        case EHOSTUNREACH:
            return LocalBoundaryHealth::unreachable;
        default:
            return LocalBoundaryHealth::failed;
    }
}

std::uint64_t elapsed_us(
    std::chrono::steady_clock::time_point started) noexcept {
    const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::steady_clock::now() - started);
    return elapsed.count() <= 0
        ? 0U
        : static_cast<std::uint64_t>(elapsed.count());
}

void classify_upstream(RouteHealthObservation &observation) noexcept {
    if (observation.carrier_connection != "offline") {
        observation.upstream = UpstreamHealth::carrier_reported_online;
        return;
    }
    switch (observation.local_boundary) {
        case LocalBoundaryHealth::refused:
        case LocalBoundaryHealth::timed_out:
        case LocalBoundaryHealth::unreachable:
            observation.upstream = UpstreamHealth::blocked_by_local_boundary;
            return;
        case LocalBoundaryHealth::not_applicable:
        case LocalBoundaryHealth::reachable:
        case LocalBoundaryHealth::failed:
            observation.upstream = UpstreamHealth::unresolved;
            return;
    }
}

Result<std::uint64_t> parse_u64(std::string_view text, std::string_view field) {
    if (text.empty()) {
        return Status{ErrorCode::protocol_error,
                      "route health " + std::string(field) + " is empty"};
    }
    std::uint64_t value = 0U;
    const auto parsed = std::from_chars(
        text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size()) {
        return Status{ErrorCode::protocol_error,
                      "route health " + std::string(field) + " is not canonical decimal"};
    }
    return value;
}

Result<std::string_view> consume_field(
    std::string_view &input, std::string_view name) {
    const std::string prefix = std::string(name) + '=';
    if (!input.starts_with(prefix)) {
        return Status{ErrorCode::protocol_error,
                      "route health report is missing ordered field " +
                          std::string(name)};
    }
    const std::size_t newline = input.find('\n');
    if (newline == std::string_view::npos) {
        return Status{ErrorCode::protocol_error,
                      "route health report has an unterminated field"};
    }
    const std::string_view value = input.substr(prefix.size(), newline - prefix.size());
    input.remove_prefix(newline + 1U);
    return value;
}

std::optional<bool> boundary_sample(LocalBoundaryHealth value) {
    switch (value) {
        case LocalBoundaryHealth::reachable:
            return true;
        case LocalBoundaryHealth::refused:
        case LocalBoundaryHealth::timed_out:
        case LocalBoundaryHealth::unreachable:
            return false;
        case LocalBoundaryHealth::not_applicable:
        case LocalBoundaryHealth::failed:
            return std::nullopt;
    }
    return std::nullopt;
}

std::optional<bool> application_sample(ApplicationHealth value) {
    switch (value) {
        case ApplicationHealth::responsive:
            return true;
        case ApplicationHealth::unresponsive:
            return false;
        case ApplicationHealth::not_sampled:
        case ApplicationHealth::unavailable:
            return std::nullopt;
    }
    return std::nullopt;
}

Status wait_ready(
    int descriptor, short events,
    std::chrono::steady_clock::time_point deadline) noexcept {
    for (;;) {
        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) {
            return Status{ErrorCode::timeout,
                          "SOCKS5 target probe deadline expired"};
        }
        const auto remaining_us = std::chrono::duration_cast<
            std::chrono::microseconds>(deadline - now).count();
        const auto rounded_ms = (remaining_us + 999LL) / 1000LL;
        const int timeout_ms = rounded_ms > 2147483647LL
            ? 2147483647
            : static_cast<int>(rounded_ms);
        pollfd event{descriptor, events, 0};
        const int ready = ::poll(&event, 1U, timeout_ms);
        if (ready > 0) {
            if ((event.revents & POLLNVAL) != 0) {
                return Status{ErrorCode::io_error,
                              "SOCKS5 target probe descriptor is invalid"};
            }
            return Status::success();
        }
        if (ready == 0) {
            return Status{ErrorCode::timeout,
                          "SOCKS5 target probe deadline expired"};
        }
        if (errno != EINTR) {
            return Status{ErrorCode::io_error,
                          "SOCKS5 target probe poll failed"};
        }
    }
}

Status write_exact(
    int descriptor, std::span<const std::uint8_t> bytes,
    std::chrono::steady_clock::time_point deadline) noexcept {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const Status ready = wait_ready(descriptor, POLLOUT, deadline);
        if (!ready.ok()) return ready;
        const ssize_t written = ::send(
            descriptor, bytes.data() + offset, bytes.size() - offset,
            MSG_NOSIGNAL);
        if (written > 0) {
            offset += static_cast<std::size_t>(written);
            continue;
        }
        if (written < 0 && (errno == EINTR || errno == EAGAIN ||
                            errno == EWOULDBLOCK)) {
            continue;
        }
        return Status{ErrorCode::io_error,
                      "SOCKS5 target probe write failed"};
    }
    return Status::success();
}

Status read_exact(
    int descriptor, std::span<std::uint8_t> bytes,
    std::chrono::steady_clock::time_point deadline) noexcept {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const Status ready = wait_ready(descriptor, POLLIN, deadline);
        if (!ready.ok()) return ready;
        const ssize_t received = ::recv(
            descriptor, bytes.data() + offset, bytes.size() - offset, 0);
        if (received > 0) {
            offset += static_cast<std::size_t>(received);
            continue;
        }
        if (received < 0 && (errno == EINTR || errno == EAGAIN ||
                             errno == EWOULDBLOCK)) {
            continue;
        }
        return Status{ErrorCode::io_error,
                      "SOCKS5 target probe read failed"};
    }
    return Status::success();
}

TargetHealth target_health_from_error(int error) noexcept {
    switch (error) {
        case ECONNREFUSED:
            return TargetHealth::refused;
        case ETIMEDOUT:
            return TargetHealth::timed_out;
        case ENETUNREACH:
        case EHOSTUNREACH:
            return TargetHealth::unreachable;
        default:
            return TargetHealth::failed;
    }
}

TargetHealth target_health_from_status(const Status &status) noexcept {
    return status.code() == ErrorCode::timeout
        ? TargetHealth::timed_out
        : TargetHealth::failed;
}

TargetHealth target_health_from_socks_reply(std::uint8_t reply) noexcept {
    switch (reply) {
        case 0U:
            return TargetHealth::reachable;
        case 2U:
        case 7U:
        case 8U:
            return TargetHealth::denied;
        case 3U:
        case 4U:
            return TargetHealth::unreachable;
        case 5U:
            return TargetHealth::refused;
        case 6U:
            return TargetHealth::timed_out;
        default:
            return TargetHealth::failed;
    }
}

}  // namespace

RouteHealthHysteresis::RouteHealthHysteresis()
    : RouteHealthHysteresis(Config{}) {}

RouteHealthHysteresis::RouteHealthHysteresis(Config config)
    : config_(config),
      configuration_valid_(
          config.failure_samples >= 1U &&
          config.failure_samples <= kMaximumHysteresisSamples &&
          config.recovery_samples >= 1U &&
          config.recovery_samples <= kMaximumHysteresisSamples) {}

Status RouteHealthHysteresis::observe(
    const RouteHealthObservation &observation) noexcept {
    if (!configuration_valid_) {
        return Status{ErrorCode::invalid_argument,
                      "route health hysteresis thresholds must be in 1..64"};
    }
    if (observations_ != std::numeric_limits<std::uint64_t>::max()) {
        ++observations_;
    }
    apply(local_boundary_, boundary_sample(observation.local_boundary));
    apply(application_, application_sample(observation.application));
    return Status::success();
}

RouteHealthHysteresisSnapshot RouteHealthHysteresis::snapshot() const noexcept {
    RouteHealthHysteresisSnapshot output;
    output.configuration_valid = configuration_valid_;
    output.failure_samples = config_.failure_samples;
    output.recovery_samples = config_.recovery_samples;
    output.observations = observations_;
    output.local_boundary = local_boundary_;
    output.application = application_;
    return output;
}

void RouteHealthHysteresis::reset() noexcept {
    observations_ = 0U;
    local_boundary_ = {};
    application_ = {};
}

void RouteHealthHysteresis::apply(
    HealthLatchSnapshot &latch, std::optional<bool> success) noexcept {
    const auto increment = [](std::uint64_t &value) noexcept {
        if (value != std::numeric_limits<std::uint64_t>::max()) {
            ++value;
        }
    };
    if (!success.has_value()) {
        increment(latch.inconclusive_samples);
        latch.consecutive_successes = 0U;
        latch.consecutive_failures = 0U;
        return;
    }
    increment(latch.decisive_samples);
    PersistentHealthState next = latch.state;
    if (*success) {
        latch.consecutive_failures = 0U;
        latch.consecutive_successes = std::min(
            config_.recovery_samples,
            latch.consecutive_successes + 1U);
        if (latch.state == PersistentHealthState::healthy ||
            latch.consecutive_successes >= config_.recovery_samples) {
            next = PersistentHealthState::healthy;
        }
    } else {
        latch.consecutive_successes = 0U;
        latch.consecutive_failures = std::min(
            config_.failure_samples,
            latch.consecutive_failures + 1U);
        if (latch.consecutive_failures >= config_.failure_samples) {
            next = PersistentHealthState::unavailable;
        } else if (latch.state == PersistentHealthState::unknown ||
                   latch.state == PersistentHealthState::healthy) {
            next = PersistentHealthState::suspect;
        }
    }
    if (next != latch.state) {
        latch.state = next;
        increment(latch.transitions);
    }
}

Result<RouteHealthObservation> observe_route_health(
    NetworkStack network,
    const std::optional<Socks5ProxyEndpoint> &socks5_proxy,
    std::string carrier_connection,
    std::chrono::milliseconds local_boundary_timeout) {
    if (!network.implemented()) {
        return Status{ErrorCode::unsupported,
                      "route health requires an implemented network stack"};
    }
    if (carrier_connection != "offline" && carrier_connection != "tcp" &&
        carrier_connection != "udp") {
        return Status{ErrorCode::invalid_argument,
                      "route health carrier connection is invalid"};
    }
    if (local_boundary_timeout <= std::chrono::milliseconds::zero()) {
        return Status{ErrorCode::invalid_argument,
                      "route health local-boundary timeout must be positive"};
    }

    RouteHealthObservation observation;
    observation.network = network;
    observation.carrier_connection = std::move(carrier_connection);
    if (network.tox_route == ToxRoute::native) {
        classify_upstream(observation);
        return observation;
    }
    if (!is_strict_socks_tox_route(network.tox_route) ||
        !socks5_proxy.has_value()) {
        return Status{ErrorCode::invalid_argument,
                      "routed route health requires one configured SOCKS5 endpoint"};
    }

    auto address = numeric_address(*socks5_proxy);
    if (!address) {
        return address.status();
    }
    const Descriptor descriptor(::socket(
        address.value().family, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0));
    if (descriptor.get() < 0) {
        observation.local_boundary = LocalBoundaryHealth::failed;
        observation.local_boundary_rtt_us = 0U;
        classify_upstream(observation);
        return observation;
    }

    const auto started = std::chrono::steady_clock::now();
    if (::connect(
            descriptor.get(),
            reinterpret_cast<const sockaddr *>(&address.value().storage),
            address.value().length) == 0) {
        observation.local_boundary = LocalBoundaryHealth::reachable;
        observation.local_boundary_rtt_us = elapsed_us(started);
        classify_upstream(observation);
        return observation;
    }
    if (errno != EINPROGRESS) {
        observation.local_boundary = classify_connect_error(errno);
        observation.local_boundary_rtt_us = elapsed_us(started);
        classify_upstream(observation);
        return observation;
    }

    pollfd event{descriptor.get(), POLLOUT, 0};
    const int timeout_ms = local_boundary_timeout.count() > 2147483647LL
        ? 2147483647
        : static_cast<int>(local_boundary_timeout.count());
    const auto deadline = started + local_boundary_timeout;
    int poll_result = 0;
    int remaining_ms = timeout_ms;
    do {
        poll_result = ::poll(&event, 1U, remaining_ms);
        if (poll_result < 0 && errno == EINTR) {
            const auto remaining = std::chrono::duration_cast<
                std::chrono::milliseconds>(
                deadline - std::chrono::steady_clock::now());
            remaining_ms = remaining.count() <= 0
                ? 0
                : static_cast<int>(remaining.count());
        }
    } while (poll_result < 0 && errno == EINTR && remaining_ms > 0);
    if (poll_result < 0 && errno == EINTR && remaining_ms == 0) {
        poll_result = 0;
    }
    if (poll_result == 0) {
        observation.local_boundary = LocalBoundaryHealth::timed_out;
    } else if (poll_result < 0) {
        observation.local_boundary = LocalBoundaryHealth::failed;
    } else {
        int error = 0;
        socklen_t error_length = sizeof(error);
        if (::getsockopt(
                descriptor.get(), SOL_SOCKET, SO_ERROR, &error,
                &error_length) != 0) {
            observation.local_boundary = LocalBoundaryHealth::failed;
        } else if (error == 0) {
            observation.local_boundary = LocalBoundaryHealth::reachable;
        } else {
            observation.local_boundary = classify_connect_error(error);
        }
    }
    observation.local_boundary_rtt_us = elapsed_us(started);
    classify_upstream(observation);
    return observation;
}

Result<RouteTargetHealthObservation> observe_route_target_health(
    NetworkStack network,
    const std::optional<Socks5ProxyEndpoint> &socks5_proxy,
    const Socks5ProxyEndpoint &configured_target,
    std::string carrier_connection,
    std::chrono::milliseconds timeout) {
    if (!network.implemented() ||
        !is_strict_socks_tox_route(network.tox_route) ||
        !socks5_proxy.has_value()) {
        return Status{
            ErrorCode::unsupported,
            "route target health requires one configured strict routed-Tox SOCKS5 route"};
    }
    if (carrier_connection != "offline" && carrier_connection != "tcp" &&
        carrier_connection != "udp") {
        return Status{ErrorCode::invalid_argument,
                      "route target health carrier connection is invalid"};
    }
    if (timeout <= std::chrono::milliseconds::zero() ||
        timeout > std::chrono::seconds(5) || socks5_proxy->port == 0U ||
        configured_target.port == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "route target health requires a 1..5000 ms timeout and nonzero ports"};
    }
    auto proxy_address = numeric_address(*socks5_proxy);
    if (!proxy_address) return proxy_address.status();
    auto target_address = numeric_address(configured_target);
    if (!target_address) {
        return Status{ErrorCode::invalid_argument,
                      "route target health requires a numeric configured target"};
    }

    RouteTargetHealthObservation observation;
    observation.network = network;
    observation.carrier_connection = std::move(carrier_connection);
    const auto started = std::chrono::steady_clock::now();
    const auto deadline = started + timeout;
    const auto finish = [&observation, started](
        TargetProbeStage stage, TargetHealth target,
        std::optional<std::uint8_t> reply = std::nullopt) {
        observation.stage = stage;
        observation.target = target;
        observation.socks_reply_code = reply;
        observation.rtt_us = elapsed_us(started);
        return observation;
    };

    const Descriptor descriptor(::socket(
        proxy_address.value().family,
        SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0));
    if (descriptor.get() < 0) {
        return finish(TargetProbeStage::proxy_connect, TargetHealth::failed);
    }
    if (::connect(
            descriptor.get(),
            reinterpret_cast<const sockaddr *>(
                &proxy_address.value().storage),
            proxy_address.value().length) != 0) {
        if (errno != EINPROGRESS) {
            return finish(
                TargetProbeStage::proxy_connect,
                target_health_from_error(errno));
        }
        const Status ready = wait_ready(descriptor.get(), POLLOUT, deadline);
        if (!ready.ok()) {
            return finish(
                TargetProbeStage::proxy_connect,
                target_health_from_status(ready));
        }
        int error = 0;
        socklen_t error_size = sizeof(error);
        if (::getsockopt(
                descriptor.get(), SOL_SOCKET, SO_ERROR, &error,
                &error_size) != 0) {
            return finish(
                TargetProbeStage::proxy_connect, TargetHealth::failed);
        }
        if (error != 0) {
            return finish(
                TargetProbeStage::proxy_connect,
                target_health_from_error(error));
        }
    }

    constexpr std::array<std::uint8_t, 3U> greeting{5U, 1U, 0U};
    Status transferred = write_exact(descriptor.get(), greeting, deadline);
    if (!transferred.ok()) {
        return finish(
            TargetProbeStage::method_negotiation,
            target_health_from_status(transferred));
    }
    std::array<std::uint8_t, 2U> method{};
    transferred = read_exact(descriptor.get(), method, deadline);
    if (!transferred.ok()) {
        return finish(
            TargetProbeStage::method_negotiation,
            target_health_from_status(transferred));
    }
    if (method != std::array<std::uint8_t, 2U>{5U, 0U}) {
        return finish(
            TargetProbeStage::method_negotiation, TargetHealth::failed);
    }

    std::vector<std::uint8_t> request{5U, 1U, 0U};
    if (target_address.value().family == AF_INET) {
        request.push_back(1U);
        const auto *target = reinterpret_cast<const sockaddr_in *>(
            &target_address.value().storage);
        const auto *bytes = reinterpret_cast<const std::uint8_t *>(
            &target->sin_addr);
        request.insert(request.end(), bytes, bytes + 4U);
    } else {
        request.push_back(4U);
        const auto *target = reinterpret_cast<const sockaddr_in6 *>(
            &target_address.value().storage);
        const auto *bytes = reinterpret_cast<const std::uint8_t *>(
            &target->sin6_addr);
        request.insert(request.end(), bytes, bytes + 16U);
    }
    request.push_back(
        static_cast<std::uint8_t>(configured_target.port >> 8U));
    request.push_back(
        static_cast<std::uint8_t>(configured_target.port & 0xFFU));
    transferred = write_exact(descriptor.get(), request, deadline);
    if (!transferred.ok()) {
        return finish(
            TargetProbeStage::target_connect,
            target_health_from_status(transferred));
    }

    std::array<std::uint8_t, 4U> reply_header{};
    transferred = read_exact(descriptor.get(), reply_header, deadline);
    if (!transferred.ok()) {
        return finish(
            TargetProbeStage::target_connect,
            target_health_from_status(transferred));
    }
    if (reply_header[0U] != 5U || reply_header[2U] != 0U) {
        return finish(
            TargetProbeStage::target_connect, TargetHealth::failed);
    }
    const std::uint8_t reply_code = reply_header[1U];
    std::size_t address_bytes = 0U;
    if (reply_header[3U] == 1U) {
        address_bytes = 4U;
    } else if (reply_header[3U] == 4U) {
        address_bytes = 16U;
    } else if (reply_header[3U] == 3U) {
        std::array<std::uint8_t, 1U> length{};
        transferred = read_exact(descriptor.get(), length, deadline);
        if (!transferred.ok()) {
            return finish(
                TargetProbeStage::target_connect,
                target_health_from_status(transferred));
        }
        address_bytes = length[0U];
    } else {
        return finish(
            TargetProbeStage::target_connect, TargetHealth::failed);
    }
    std::array<std::uint8_t, 257U> reply_tail{};
    transferred = read_exact(
        descriptor.get(),
        std::span<std::uint8_t>{reply_tail}.first(address_bytes + 2U),
        deadline);
    if (!transferred.ok()) {
        return finish(
            TargetProbeStage::target_connect,
            target_health_from_status(transferred));
    }
    const TargetHealth target = target_health_from_socks_reply(reply_code);
    return finish(
        target == TargetHealth::reachable ? TargetProbeStage::complete
                                          : TargetProbeStage::target_connect,
        target, reply_code);
}

void record_application_response(
    RouteHealthObservation &observation, std::uint64_t rtt_us) noexcept {
    observation.application = ApplicationHealth::responsive;
    observation.application_rtt_us = rtt_us;
    observation.application_error.reset();
}

void record_application_failure(
    RouteHealthObservation &observation, ErrorCode error) noexcept {
    observation.application = error == ErrorCode::timeout
        ? ApplicationHealth::unresponsive
        : ApplicationHealth::unavailable;
    observation.application_rtt_us.reset();
    observation.application_error = error;
}

std::string render_route_health(const RouteHealthObservation &observation) {
    std::ostringstream output;
    output << "network=" << observation.network.name() << '\n'
           << "carrier-connection=" << observation.carrier_connection << '\n'
           << "local-boundary=" << to_string(observation.local_boundary) << '\n'
           << "local-boundary-rtt-us=";
    if (observation.local_boundary_rtt_us.has_value()) {
        output << *observation.local_boundary_rtt_us;
    } else {
        output << "not-sampled";
    }
    output << '\n'
           << "upstream=" << to_string(observation.upstream) << '\n'
           << "application=" << to_string(observation.application) << '\n'
           << "application-rtt-us=";
    if (observation.application_rtt_us.has_value()) {
        output << *observation.application_rtt_us;
    } else {
        output << "not-sampled";
    }
    output << '\n' << "application-error=";
    if (observation.application_error.has_value()) {
        output << static_cast<unsigned int>(*observation.application_error);
    } else {
        output << "none";
    }
    output << '\n'
           << "semantics=auxiliary-only-no-carrier-or-session-epoch-mutation\n";
    return output.str();
}

Result<RouteHealthObservation> parse_route_health(std::string_view text) {
    const std::string_view original = text;
    RouteHealthObservation observation;

    auto network = consume_field(text, "network");
    if (!network) return network.status();
    auto parsed_network = parse_network_stack(network.value());
    if (!parsed_network || !parsed_network.value().implemented()) {
        return Status{ErrorCode::protocol_error,
                      "route health report names an unsupported network"};
    }
    observation.network = parsed_network.value();

    auto carrier = consume_field(text, "carrier-connection");
    if (!carrier) return carrier.status();
    if (carrier.value() != "offline" && carrier.value() != "tcp" &&
        carrier.value() != "udp") {
        return Status{ErrorCode::protocol_error,
                      "route health report has an invalid carrier"};
    }
    observation.carrier_connection = std::string(carrier.value());

    auto boundary = consume_field(text, "local-boundary");
    if (!boundary) return boundary.status();
    if (boundary.value() == "not-applicable") {
        observation.local_boundary = LocalBoundaryHealth::not_applicable;
    } else if (boundary.value() == "reachable") {
        observation.local_boundary = LocalBoundaryHealth::reachable;
    } else if (boundary.value() == "refused") {
        observation.local_boundary = LocalBoundaryHealth::refused;
    } else if (boundary.value() == "timed-out") {
        observation.local_boundary = LocalBoundaryHealth::timed_out;
    } else if (boundary.value() == "unreachable") {
        observation.local_boundary = LocalBoundaryHealth::unreachable;
    } else if (boundary.value() == "failed") {
        observation.local_boundary = LocalBoundaryHealth::failed;
    } else {
        return Status{ErrorCode::protocol_error,
                      "route health report has an invalid local boundary"};
    }

    auto boundary_rtt = consume_field(text, "local-boundary-rtt-us");
    if (!boundary_rtt) return boundary_rtt.status();
    if (boundary_rtt.value() != "not-sampled") {
        auto parsed = parse_u64(boundary_rtt.value(), "local-boundary-rtt-us");
        if (!parsed) return parsed.status();
        observation.local_boundary_rtt_us = parsed.value();
    }

    auto upstream = consume_field(text, "upstream");
    if (!upstream) return upstream.status();
    if (upstream.value() == "carrier-reported-online") {
        observation.upstream = UpstreamHealth::carrier_reported_online;
    } else if (upstream.value() == "blocked-by-local-boundary") {
        observation.upstream = UpstreamHealth::blocked_by_local_boundary;
    } else if (upstream.value() == "unresolved") {
        observation.upstream = UpstreamHealth::unresolved;
    } else {
        return Status{ErrorCode::protocol_error,
                      "route health report has an invalid upstream state"};
    }

    auto application = consume_field(text, "application");
    if (!application) return application.status();
    if (application.value() == "not-sampled") {
        observation.application = ApplicationHealth::not_sampled;
    } else if (application.value() == "responsive") {
        observation.application = ApplicationHealth::responsive;
    } else if (application.value() == "unresponsive") {
        observation.application = ApplicationHealth::unresponsive;
    } else if (application.value() == "unavailable") {
        observation.application = ApplicationHealth::unavailable;
    } else {
        return Status{ErrorCode::protocol_error,
                      "route health report has an invalid application state"};
    }

    auto application_rtt = consume_field(text, "application-rtt-us");
    if (!application_rtt) return application_rtt.status();
    if (application_rtt.value() != "not-sampled") {
        auto parsed = parse_u64(application_rtt.value(), "application-rtt-us");
        if (!parsed) return parsed.status();
        observation.application_rtt_us = parsed.value();
    }

    auto application_error = consume_field(text, "application-error");
    if (!application_error) return application_error.status();
    if (application_error.value() != "none") {
        auto parsed = parse_u64(application_error.value(), "application-error");
        if (!parsed || parsed.value() >
                           static_cast<std::uint64_t>(ErrorCode::resource_exhausted)) {
            return Status{ErrorCode::protocol_error,
                          "route health report has an invalid application error"};
        }
        observation.application_error =
            static_cast<ErrorCode>(parsed.value());
    }

    auto semantics = consume_field(text, "semantics");
    if (!semantics) return semantics.status();
    RouteHealthObservation expected_upstream = observation;
    classify_upstream(expected_upstream);
    const bool boundary_coherent =
        observation.network.tox_route == ToxRoute::native
            ? observation.local_boundary ==
                      LocalBoundaryHealth::not_applicable &&
                  !observation.local_boundary_rtt_us.has_value()
            : observation.local_boundary !=
                      LocalBoundaryHealth::not_applicable &&
                  observation.local_boundary_rtt_us.has_value();
    const bool application_coherent =
        (observation.application == ApplicationHealth::not_sampled &&
         !observation.application_rtt_us.has_value() &&
         !observation.application_error.has_value()) ||
        (observation.application == ApplicationHealth::responsive &&
         observation.application_rtt_us.has_value() &&
         !observation.application_error.has_value()) ||
        ((observation.application == ApplicationHealth::unresponsive ||
          observation.application == ApplicationHealth::unavailable) &&
         !observation.application_rtt_us.has_value() &&
         observation.application_error.has_value() &&
         *observation.application_error != ErrorCode::ok);
    if (semantics.value() !=
        "auxiliary-only-no-carrier-or-session-epoch-mutation" ||
        !text.empty() || !boundary_coherent || !application_coherent ||
        observation.upstream != expected_upstream.upstream ||
        render_route_health(observation) != original) {
        return Status{ErrorCode::protocol_error,
                      "route health report is noncanonical"};
    }
    return observation;
}

std::string render_route_health_hysteresis(
    const RouteHealthHysteresisSnapshot &snapshot) {
    std::ostringstream output;
    const auto render_latch = [&output](
        std::string_view prefix, const HealthLatchSnapshot &latch) {
        output << prefix << "-state=" << to_string(latch.state) << '\n'
               << prefix << "-success-streak=" << latch.consecutive_successes << '\n'
               << prefix << "-failure-streak=" << latch.consecutive_failures << '\n'
               << prefix << "-decisive-samples=" << latch.decisive_samples << '\n'
               << prefix << "-inconclusive-samples=" << latch.inconclusive_samples << '\n'
               << prefix << "-transitions=" << latch.transitions << '\n';
    };
    output << "monitor-observations=" << snapshot.observations << '\n'
           << "monitor-failure-samples=" << snapshot.failure_samples << '\n'
           << "monitor-recovery-samples=" << snapshot.recovery_samples << '\n';
    render_latch("monitor-local-boundary", snapshot.local_boundary);
    render_latch("monitor-application", snapshot.application);
    output << "monitor-semantics=observation-only-independent-latches-no-carrier-or-session-mutation\n";
    return output.str();
}

std::string render_route_target_health(
    const RouteTargetHealthObservation &observation) {
    std::ostringstream output;
    output << "network=" << observation.network.name() << '\n'
           << "carrier-connection=" << observation.carrier_connection << '\n'
           << "target-source=configured-tcp-relay-0\n"
           << "probe-stage=" << to_string(observation.stage) << '\n'
           << "target-health=" << to_string(observation.target) << '\n'
           << "target-rtt-us=" << observation.rtt_us << '\n'
           << "socks-reply-code=";
    if (observation.socks_reply_code.has_value()) {
        output << static_cast<unsigned int>(*observation.socks_reply_code);
    } else {
        output << "none";
    }
    output << '\n'
           << "semantics=auxiliary-only-explicit-numeric-relay-no-carrier-or-session-epoch-mutation\n";
    return output.str();
}

Result<RouteTargetHealthObservation> parse_route_target_health(
    std::string_view text) {
    const std::string_view original = text;
    RouteTargetHealthObservation observation;
    auto network = consume_field(text, "network");
    if (!network) return network.status();
    auto parsed_network = parse_network_stack(network.value());
    if (!parsed_network ||
        parsed_network.value().transport != TransportKind::tox ||
        !is_strict_socks_tox_route(parsed_network.value().tox_route)) {
        return Status{ErrorCode::protocol_error,
                      "route target report requires strict routed Tox"};
    }
    observation.network = parsed_network.value();

    auto carrier = consume_field(text, "carrier-connection");
    if (!carrier) return carrier.status();
    if (carrier.value() != "offline" && carrier.value() != "tcp" &&
        carrier.value() != "udp") {
        return Status{ErrorCode::protocol_error,
                      "route target report has an invalid carrier"};
    }
    observation.carrier_connection = std::string(carrier.value());

    auto source = consume_field(text, "target-source");
    if (!source || source.value() != "configured-tcp-relay-0") {
        return Status{ErrorCode::protocol_error,
                      "route target report has an invalid target source"};
    }
    auto stage = consume_field(text, "probe-stage");
    if (!stage) return stage.status();
    if (stage.value() == "proxy-connect") {
        observation.stage = TargetProbeStage::proxy_connect;
    } else if (stage.value() == "method-negotiation") {
        observation.stage = TargetProbeStage::method_negotiation;
    } else if (stage.value() == "target-connect") {
        observation.stage = TargetProbeStage::target_connect;
    } else if (stage.value() == "complete") {
        observation.stage = TargetProbeStage::complete;
    } else {
        return Status{ErrorCode::protocol_error,
                      "route target report has an invalid probe stage"};
    }

    auto target = consume_field(text, "target-health");
    if (!target) return target.status();
    if (target.value() == "reachable") {
        observation.target = TargetHealth::reachable;
    } else if (target.value() == "refused") {
        observation.target = TargetHealth::refused;
    } else if (target.value() == "denied") {
        observation.target = TargetHealth::denied;
    } else if (target.value() == "timed-out") {
        observation.target = TargetHealth::timed_out;
    } else if (target.value() == "unreachable") {
        observation.target = TargetHealth::unreachable;
    } else if (target.value() == "failed") {
        observation.target = TargetHealth::failed;
    } else {
        return Status{ErrorCode::protocol_error,
                      "route target report has an invalid health state"};
    }

    auto rtt = consume_field(text, "target-rtt-us");
    if (!rtt) return rtt.status();
    auto parsed_rtt = parse_u64(rtt.value(), "target-rtt-us");
    if (!parsed_rtt) return parsed_rtt.status();
    observation.rtt_us = parsed_rtt.value();

    auto reply = consume_field(text, "socks-reply-code");
    if (!reply) return reply.status();
    if (reply.value() != "none") {
        auto parsed_reply = parse_u64(reply.value(), "socks-reply-code");
        if (!parsed_reply || parsed_reply.value() > 255U) {
            return Status{ErrorCode::protocol_error,
                          "route target report has an invalid SOCKS reply code"};
        }
        observation.socks_reply_code =
            static_cast<std::uint8_t>(parsed_reply.value());
    }

    auto semantics = consume_field(text, "semantics");
    if (!semantics) return semantics.status();
    const bool complete = observation.stage == TargetProbeStage::complete &&
        observation.target == TargetHealth::reachable &&
        observation.socks_reply_code == 0U;
    const bool coherent_proxy_failure =
        observation.stage == TargetProbeStage::proxy_connect &&
        !observation.socks_reply_code.has_value() &&
        observation.target != TargetHealth::reachable &&
        observation.target != TargetHealth::denied;
    const bool coherent_method_failure =
        observation.stage == TargetProbeStage::method_negotiation &&
        !observation.socks_reply_code.has_value() &&
        (observation.target == TargetHealth::timed_out ||
         observation.target == TargetHealth::failed);
    const bool coherent_target_failure =
        observation.stage == TargetProbeStage::target_connect &&
        observation.target != TargetHealth::reachable &&
        ((!observation.socks_reply_code.has_value() &&
          (observation.target == TargetHealth::timed_out ||
           observation.target == TargetHealth::failed)) ||
         (observation.socks_reply_code.has_value() &&
          target_health_from_socks_reply(*observation.socks_reply_code) ==
              observation.target));
    if (semantics.value() !=
            "auxiliary-only-explicit-numeric-relay-no-carrier-or-session-epoch-mutation" ||
        !text.empty() ||
        (!complete && !coherent_proxy_failure &&
         !coherent_method_failure && !coherent_target_failure) ||
        render_route_target_health(observation) != original) {
        return Status{ErrorCode::protocol_error,
                      "route target report is noncanonical"};
    }
    return observation;
}

std::string to_string(LocalBoundaryHealth value) {
    switch (value) {
        case LocalBoundaryHealth::not_applicable:
            return "not-applicable";
        case LocalBoundaryHealth::reachable:
            return "reachable";
        case LocalBoundaryHealth::refused:
            return "refused";
        case LocalBoundaryHealth::timed_out:
            return "timed-out";
        case LocalBoundaryHealth::unreachable:
            return "unreachable";
        case LocalBoundaryHealth::failed:
            return "failed";
    }
    return "unknown";
}

std::string to_string(UpstreamHealth value) {
    switch (value) {
        case UpstreamHealth::carrier_reported_online:
            return "carrier-reported-online";
        case UpstreamHealth::blocked_by_local_boundary:
            return "blocked-by-local-boundary";
        case UpstreamHealth::unresolved:
            return "unresolved";
    }
    return "unknown";
}

std::string to_string(ApplicationHealth value) {
    switch (value) {
        case ApplicationHealth::not_sampled:
            return "not-sampled";
        case ApplicationHealth::responsive:
            return "responsive";
        case ApplicationHealth::unresponsive:
            return "unresponsive";
        case ApplicationHealth::unavailable:
            return "unavailable";
    }
    return "unknown";
}

std::string to_string(PersistentHealthState value) {
    switch (value) {
        case PersistentHealthState::unknown:
            return "unknown";
        case PersistentHealthState::healthy:
            return "healthy";
        case PersistentHealthState::suspect:
            return "suspect";
        case PersistentHealthState::unavailable:
            return "unavailable";
    }
    return "unknown";
}

std::string to_string(TargetProbeStage value) {
    switch (value) {
        case TargetProbeStage::proxy_connect:
            return "proxy-connect";
        case TargetProbeStage::method_negotiation:
            return "method-negotiation";
        case TargetProbeStage::target_connect:
            return "target-connect";
        case TargetProbeStage::complete:
            return "complete";
    }
    return "unknown";
}

std::string to_string(TargetHealth value) {
    switch (value) {
        case TargetHealth::reachable:
            return "reachable";
        case TargetHealth::refused:
            return "refused";
        case TargetHealth::denied:
            return "denied";
        case TargetHealth::timed_out:
            return "timed-out";
        case TargetHealth::unreachable:
            return "unreachable";
        case TargetHealth::failed:
            return "failed";
    }
    return "unknown";
}

}  // namespace iotox::routes
