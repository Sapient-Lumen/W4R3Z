#pragma once

#include "iotox/network.hpp"
#include "iotox/status.hpp"

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace iotox::routes {

// This is an auxiliary observation surface. None of these values may replace
// c-toxcore's authoritative connection state or advance a protocol session.
enum class LocalBoundaryHealth {
    not_applicable,
    reachable,
    refused,
    timed_out,
    unreachable,
    failed,
};

enum class UpstreamHealth {
    carrier_reported_online,
    blocked_by_local_boundary,
    unresolved,
};

enum class ApplicationHealth {
    not_sampled,
    responsive,
    unresponsive,
    unavailable,
};

// A separately requested SOCKS5 CONNECT probe to one numeric target already
// present in the frozen route configuration. The stage keeps local proxy
// failure separate from a proxy response about the configured target.
enum class TargetProbeStage {
    proxy_connect,
    method_negotiation,
    target_connect,
    complete,
};

enum class TargetHealth {
    reachable,
    refused,
    denied,
    timed_out,
    unreachable,
    failed,
};

struct RouteTargetHealthObservation {
    NetworkStack network{};
    std::string carrier_connection{"offline"};
    TargetProbeStage stage{TargetProbeStage::proxy_connect};
    TargetHealth target{TargetHealth::failed};
    std::uint64_t rtt_us{0U};
    std::optional<std::uint8_t> socks_reply_code;
};

struct RouteHealthObservation {
    NetworkStack network{};
    std::string carrier_connection{"offline"};
    LocalBoundaryHealth local_boundary{LocalBoundaryHealth::not_applicable};
    std::optional<std::uint64_t> local_boundary_rtt_us;
    UpstreamHealth upstream{UpstreamHealth::unresolved};
    ApplicationHealth application{ApplicationHealth::not_sampled};
    std::optional<std::uint64_t> application_rtt_us;
    std::optional<ErrorCode> application_error;
};

// Hysteresis is deliberately maintained independently for the local routing
// boundary and the remote application. A reachable SOCKS listener is not an
// application success, and an unavailable pre-send path is not fabricated
// into a remote timeout.
enum class PersistentHealthState {
    unknown,
    healthy,
    suspect,
    unavailable,
};

struct HealthLatchSnapshot {
    PersistentHealthState state{PersistentHealthState::unknown};
    std::uint32_t consecutive_successes{0U};
    std::uint32_t consecutive_failures{0U};
    std::uint64_t decisive_samples{0U};
    std::uint64_t inconclusive_samples{0U};
    std::uint64_t transitions{0U};
};

struct RouteHealthHysteresisSnapshot {
    bool configuration_valid{false};
    std::uint32_t failure_samples{0U};
    std::uint32_t recovery_samples{0U};
    std::uint64_t observations{0U};
    HealthLatchSnapshot local_boundary{};
    HealthLatchSnapshot application{};
};

class RouteHealthHysteresis {
  public:
    struct Config {
        std::uint32_t failure_samples{3U};
        std::uint32_t recovery_samples{2U};
    };

    RouteHealthHysteresis();
    explicit RouteHealthHysteresis(Config config);

    [[nodiscard]] Status observe(
        const RouteHealthObservation &observation) noexcept;
    [[nodiscard]] RouteHealthHysteresisSnapshot snapshot() const noexcept;
    void reset() noexcept;

  private:
    // nullopt is inconclusive; true/false are decisive success/failure.
    void apply(
        HealthLatchSnapshot &latch,
        std::optional<bool> success) noexcept;

    Config config_{};
    bool configuration_valid_{true};
    std::uint64_t observations_{0U};
    HealthLatchSnapshot local_boundary_{};
    HealthLatchSnapshot application_{};
};

// Opens and closes one numeric TCP connection to the configured local SOCKS5
// endpoint. It sends no SOCKS request and therefore says nothing by itself
// about the proxy's upstream route.
[[nodiscard]] Result<RouteHealthObservation> observe_route_health(
    NetworkStack network,
    const std::optional<Socks5ProxyEndpoint> &socks5_proxy,
    std::string carrier_connection,
    std::chrono::milliseconds local_boundary_timeout);

// Performs one complete no-auth SOCKS5 CONNECT to a numeric target selected
// by the Agent from its already validated explicit TCP-relay configuration.
// No application bytes are sent after a successful CONNECT.
[[nodiscard]] Result<RouteTargetHealthObservation>
observe_route_target_health(
    NetworkStack network,
    const std::optional<Socks5ProxyEndpoint> &socks5_proxy,
    const Socks5ProxyEndpoint &configured_target,
    std::string carrier_connection,
    std::chrono::milliseconds timeout);

void record_application_response(
    RouteHealthObservation &observation, std::uint64_t rtt_us) noexcept;
void record_application_failure(
    RouteHealthObservation &observation, ErrorCode error) noexcept;

[[nodiscard]] std::string render_route_health(
    const RouteHealthObservation &observation);
[[nodiscard]] Result<RouteHealthObservation> parse_route_health(
    std::string_view text);
[[nodiscard]] std::string render_route_health_hysteresis(
    const RouteHealthHysteresisSnapshot &snapshot);
[[nodiscard]] std::string render_route_target_health(
    const RouteTargetHealthObservation &observation);
[[nodiscard]] Result<RouteTargetHealthObservation> parse_route_target_health(
    std::string_view text);
[[nodiscard]] std::string to_string(LocalBoundaryHealth value);
[[nodiscard]] std::string to_string(UpstreamHealth value);
[[nodiscard]] std::string to_string(ApplicationHealth value);
[[nodiscard]] std::string to_string(PersistentHealthState value);
[[nodiscard]] std::string to_string(TargetProbeStage value);
[[nodiscard]] std::string to_string(TargetHealth value);

}  // namespace iotox::routes
