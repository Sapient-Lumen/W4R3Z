#include "test_harness.hpp"

#include "iotox/network.hpp"
#include "iotox/route_health.hpp"

#include <arpa/inet.h>
#include <chrono>
#include <sys/socket.h>
#include <unistd.h>

IOTOX_TEST("network model keeps Tox routes separate from direct overlays") {
    auto native = iotox::parse_network_stack("tox/native");
    IOTOX_CHECK(native);
    IOTOX_CHECK(native.value().implemented());
    IOTOX_CHECK(native.value().transport == iotox::TransportKind::tox);
    IOTOX_CHECK(native.value().tox_route == iotox::ToxRoute::native);

    auto tox_tor = iotox::parse_network_stack("tox-over-tor");
    IOTOX_CHECK(tox_tor);
    IOTOX_CHECK(tox_tor.value().implemented());
    IOTOX_CHECK(tox_tor.value().transport == iotox::TransportKind::tox);
    IOTOX_CHECK(tox_tor.value().tox_route == iotox::ToxRoute::tor);

    auto direct_tor = iotox::parse_network_stack("tor-direct");
    IOTOX_CHECK(direct_tor);
    IOTOX_CHECK(direct_tor.value().transport == iotox::TransportKind::tor_direct_reserved);
    IOTOX_CHECK(direct_tor.value().tox_route == iotox::ToxRoute::native);

    auto tox_i2p = iotox::parse_network_stack("TOX/I2P");
    IOTOX_CHECK(tox_i2p);
    IOTOX_CHECK(tox_i2p.value().name() == "Tox/I2P");
    IOTOX_CHECK(tox_i2p.value().implemented());
    IOTOX_CHECK(tox_i2p.value().tox_route == iotox::ToxRoute::i2p);
    IOTOX_CHECK(iotox::is_strict_socks_tox_route(
        tox_i2p.value().tox_route));

    auto tox_i2p_construction =
        iotox::parse_network_stack("tox/i2p-construction");
    IOTOX_CHECK(tox_i2p_construction);
    IOTOX_CHECK(tox_i2p_construction.value().implemented());
    IOTOX_CHECK(tox_i2p_construction.value().name() ==
                "Tox/I2P-construction");
    IOTOX_CHECK(iotox::is_strict_socks_tox_route(
        tox_i2p_construction.value().tox_route));

    auto direct_i2p = iotox::parse_network_stack("i2p-direct");
    IOTOX_CHECK(direct_i2p);
    IOTOX_CHECK(direct_i2p.value().name() == "I2P-direct");
    IOTOX_CHECK(direct_tor.value().name() == "Tor-direct");

    const auto capabilities = iotox::network_capabilities();
    IOTOX_CHECK(capabilities.size() == 6U);
    IOTOX_CHECK(capabilities.front().stack.name() == native.value().name());
    IOTOX_CHECK(capabilities.front().status == "adapter-verified");
    IOTOX_CHECK(capabilities[1U].stack.name() == tox_i2p.value().name());
    IOTOX_CHECK(capabilities[2U].stack.name() ==
                tox_i2p_construction.value().name());
    IOTOX_CHECK(capabilities[1U].status == "vm-qualified");
    IOTOX_CHECK(capabilities[2U].status == "compatibility-alias");
    IOTOX_CHECK(capabilities[3U].stack.name() == tox_tor.value().name());
    IOTOX_CHECK(capabilities[3U].status == "construction-enabled");
    IOTOX_CHECK(capabilities[4U].stack.name() == direct_i2p.value().name());
    IOTOX_CHECK(capabilities[5U].stack.name() == direct_tor.value().name());

    IOTOX_CHECK(iotox::to_string(static_cast<iotox::TransportKind>(255U)) == "unknown");
    IOTOX_CHECK(iotox::to_string(static_cast<iotox::ToxRoute>(255U)) == "unknown");
}

IOTOX_TEST("SOCKS5 proxy endpoints are numeric and unambiguous") {
    auto ipv4 = iotox::parse_socks5_proxy_endpoint("127.0.0.1:9050");
    IOTOX_CHECK(ipv4);
    IOTOX_CHECK(ipv4.value().host == "127.0.0.1");
    IOTOX_CHECK(ipv4.value().port == 9050U);
    IOTOX_CHECK(iotox::format_socks5_proxy_endpoint(ipv4.value()) ==
                "127.0.0.1:9050");

    auto ipv6 = iotox::parse_socks5_proxy_endpoint("[::1]:65535");
    IOTOX_CHECK(ipv6);
    IOTOX_CHECK(ipv6.value().host == "::1");
    IOTOX_CHECK(iotox::format_socks5_proxy_endpoint(ipv6.value()) ==
                "[::1]:65535");

    IOTOX_CHECK(iotox::is_numeric_ip_address("192.0.2.1"));
    IOTOX_CHECK(iotox::is_numeric_ip_address("2001:db8::1"));
    IOTOX_CHECK(!iotox::is_numeric_ip_address("relay.example"));
    for (std::string_view rejected : {
             "localhost:9050", "127.0.0.1:0", "127.0.0.1:65536",
             "127.0.0.1:99999999999999999999999999999999999999999999",
             "127.0.0.1:-1", "127.0.0.1:", "::1:9050",
             "[::1]9050", "[fe80::1%lo]:9050", " 127.0.0.1:9050",
             "127.0.0.1:9050:extra"}) {
        IOTOX_CHECK(!iotox::parse_socks5_proxy_endpoint(rejected));
    }

    const int listener = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    IOTOX_CHECK(listener >= 0);
    sockaddr_in listen_address{};
    listen_address.sin_family = AF_INET;
    listen_address.sin_port = 0U;
    IOTOX_CHECK(
        ::inet_pton(AF_INET, "127.0.0.1", &listen_address.sin_addr) == 1);
    IOTOX_CHECK(::bind(
                    listener,
                    reinterpret_cast<const sockaddr *>(&listen_address),
                    sizeof(listen_address)) == 0);
    IOTOX_CHECK(::listen(listener, 1) == 0);
    socklen_t address_length = sizeof(listen_address);
    IOTOX_CHECK(::getsockname(
                    listener,
                    reinterpret_cast<sockaddr *>(&listen_address),
                    &address_length) == 0);
    const iotox::Socks5ProxyEndpoint local_proxy{
        "127.0.0.1", ntohs(listen_address.sin_port)};
    const iotox::NetworkStack tor{
        iotox::TransportKind::tox, iotox::ToxRoute::tor};
    auto reachable = iotox::routes::observe_route_health(
        tor, local_proxy, "offline", std::chrono::milliseconds(250));
    IOTOX_CHECK_MSG(reachable.ok(), reachable.status().message());
    IOTOX_CHECK(
        reachable.value().local_boundary ==
        iotox::routes::LocalBoundaryHealth::reachable);
    IOTOX_CHECK(reachable.value().local_boundary_rtt_us.has_value());
    IOTOX_CHECK(
        reachable.value().upstream ==
        iotox::routes::UpstreamHealth::unresolved);

    auto carrier_online = iotox::routes::observe_route_health(
        tor, local_proxy, "tcp", std::chrono::milliseconds(250));
    IOTOX_CHECK(carrier_online);
    IOTOX_CHECK(
        carrier_online.value().upstream ==
        iotox::routes::UpstreamHealth::carrier_reported_online);
    iotox::routes::record_application_response(
        carrier_online.value(), 1234U);
    const std::string rendered =
        iotox::routes::render_route_health(carrier_online.value());
    auto parsed_rendered = iotox::routes::parse_route_health(rendered);
    IOTOX_CHECK_MSG(parsed_rendered.ok(), parsed_rendered.status().message());
    IOTOX_CHECK(iotox::routes::render_route_health(parsed_rendered.value()) ==
                rendered);
    IOTOX_CHECK(rendered.find("network=Tox/Tor\n") != std::string::npos);
    IOTOX_CHECK(rendered.find("application=responsive\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("application-rtt-us=1234\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find(
                    "semantics=auxiliary-only-no-carrier-or-session-epoch-mutation\n") !=
                std::string::npos);
    iotox::routes::record_application_failure(
        carrier_online.value(), iotox::ErrorCode::timeout);
    const std::string failed_application =
        iotox::routes::render_route_health(carrier_online.value());
    IOTOX_CHECK(failed_application.find("application=unresponsive\n") !=
                std::string::npos);
    IOTOX_CHECK(failed_application.find(
                    "application-rtt-us=not-sampled\n") !=
                std::string::npos);
    IOTOX_CHECK(failed_application.find(
                    "application-error=" +
                    std::to_string(static_cast<unsigned int>(
                        iotox::ErrorCode::timeout)) +
                    "\n") != std::string::npos);
    iotox::routes::record_application_failure(
        carrier_online.value(), iotox::ErrorCode::unavailable);
    IOTOX_CHECK(
        iotox::routes::render_route_health(carrier_online.value()).find(
            "application=unavailable\n") != std::string::npos);

    IOTOX_CHECK(::close(listener) == 0);
    auto refused = iotox::routes::observe_route_health(
        tor, local_proxy, "offline", std::chrono::milliseconds(250));
    IOTOX_CHECK(refused);
    IOTOX_CHECK(
        refused.value().local_boundary ==
        iotox::routes::LocalBoundaryHealth::refused);
    IOTOX_CHECK(
        refused.value().upstream ==
        iotox::routes::UpstreamHealth::blocked_by_local_boundary);

    auto native_health = iotox::routes::observe_route_health(
        iotox::NetworkStack{}, std::nullopt, "offline",
        std::chrono::milliseconds(250));
    IOTOX_CHECK(native_health);
    IOTOX_CHECK(
        native_health.value().local_boundary ==
        iotox::routes::LocalBoundaryHealth::not_applicable);
    IOTOX_CHECK(!native_health.value().local_boundary_rtt_us.has_value());
    IOTOX_CHECK(!iotox::routes::observe_route_health(
        tor, std::nullopt, "offline", std::chrono::milliseconds(250)));

    std::string noncanonical = rendered;
    noncanonical.replace(
        noncanonical.find("application-rtt-us=1234"),
        std::string("application-rtt-us=1234").size(),
        "application-rtt-us=01234");
    IOTOX_CHECK(!iotox::routes::parse_route_health(noncanonical));
    std::string contradictory = rendered;
    contradictory.replace(
        contradictory.find("local-boundary=reachable"),
        std::string("local-boundary=reachable").size(),
        "local-boundary=not-applicable");
    IOTOX_CHECK(!iotox::routes::parse_route_health(contradictory));
}

IOTOX_TEST("route health hysteresis separates boundary and application truth") {
    using iotox::routes::ApplicationHealth;
    using iotox::routes::LocalBoundaryHealth;
    using iotox::routes::PersistentHealthState;
    using iotox::routes::RouteHealthHysteresis;
    using iotox::routes::RouteHealthObservation;

    RouteHealthHysteresis monitor({3U, 2U});
    RouteHealthObservation sample;
    sample.network = {
        iotox::TransportKind::tox, iotox::ToxRoute::tor};
    sample.local_boundary = LocalBoundaryHealth::reachable;
    sample.application = ApplicationHealth::unavailable;

    IOTOX_CHECK(monitor.observe(sample).ok());
    auto snapshot = monitor.snapshot();
    IOTOX_CHECK(snapshot.observations == 1U);
    IOTOX_CHECK(snapshot.local_boundary.state ==
                PersistentHealthState::unknown);
    IOTOX_CHECK(snapshot.application.state ==
                PersistentHealthState::unknown);
    IOTOX_CHECK(snapshot.application.inconclusive_samples == 1U);

    IOTOX_CHECK(monitor.observe(sample).ok());
    snapshot = monitor.snapshot();
    IOTOX_CHECK(snapshot.local_boundary.state ==
                PersistentHealthState::healthy);
    IOTOX_CHECK(snapshot.application.state ==
                PersistentHealthState::unknown);

    sample.local_boundary = LocalBoundaryHealth::refused;
    sample.application = ApplicationHealth::unresponsive;
    IOTOX_CHECK(monitor.observe(sample).ok());
    snapshot = monitor.snapshot();
    IOTOX_CHECK(snapshot.local_boundary.state ==
                PersistentHealthState::suspect);
    IOTOX_CHECK(snapshot.application.state ==
                PersistentHealthState::suspect);
    IOTOX_CHECK(monitor.observe(sample).ok());
    IOTOX_CHECK(monitor.observe(sample).ok());
    snapshot = monitor.snapshot();
    IOTOX_CHECK(snapshot.local_boundary.state ==
                PersistentHealthState::unavailable);
    IOTOX_CHECK(snapshot.application.state ==
                PersistentHealthState::unavailable);

    sample.local_boundary = LocalBoundaryHealth::reachable;
    sample.application = ApplicationHealth::responsive;
    IOTOX_CHECK(monitor.observe(sample).ok());
    snapshot = monitor.snapshot();
    IOTOX_CHECK(snapshot.local_boundary.state ==
                PersistentHealthState::unavailable);
    IOTOX_CHECK(monitor.observe(sample).ok());
    snapshot = monitor.snapshot();
    IOTOX_CHECK(snapshot.local_boundary.state ==
                PersistentHealthState::healthy);
    IOTOX_CHECK(snapshot.application.state ==
                PersistentHealthState::healthy);
    IOTOX_CHECK(snapshot.local_boundary.transitions == 4U);
    IOTOX_CHECK(snapshot.application.transitions == 3U);

    const std::string rendered =
        iotox::routes::render_route_health_hysteresis(snapshot);
    IOTOX_CHECK(rendered.find("monitor-local-boundary-state=healthy\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("monitor-application-state=healthy\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find(
                    "monitor-semantics=observation-only-independent-latches-no-carrier-or-session-mutation\n") !=
                std::string::npos);

    RouteHealthHysteresis invalid({0U, 65U});
    IOTOX_CHECK(!invalid.snapshot().configuration_valid);
    IOTOX_CHECK(!invalid.observe(sample).ok());
}

IOTOX_TEST("route target health report binds configured SOCKS result semantics") {
    iotox::routes::RouteTargetHealthObservation observation;
    observation.network = {
        iotox::TransportKind::tox, iotox::ToxRoute::tor};
    observation.carrier_connection = "tcp";
    observation.stage = iotox::routes::TargetProbeStage::complete;
    observation.target = iotox::routes::TargetHealth::reachable;
    observation.rtt_us = 1234U;
    observation.socks_reply_code = 0U;

    const std::string rendered =
        iotox::routes::render_route_target_health(observation);
    auto parsed = iotox::routes::parse_route_target_health(rendered);
    IOTOX_CHECK_MSG(parsed.ok(), parsed.status().message());
    IOTOX_CHECK(
        iotox::routes::render_route_target_health(parsed.value()) == rendered);
    IOTOX_CHECK(rendered.find("target-source=configured-tcp-relay-0\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("probe-stage=complete\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("target-health=reachable\n") !=
                std::string::npos);

    std::string contradictory = rendered;
    contradictory.replace(
        contradictory.find("probe-stage=complete"),
        std::string("probe-stage=complete").size(),
        "probe-stage=proxy-connect");
    IOTOX_CHECK(!iotox::routes::parse_route_target_health(contradictory));

    std::string endpoint_leak = rendered;
    endpoint_leak.replace(
        endpoint_leak.find("configured-tcp-relay-0"),
        std::string("configured-tcp-relay-0").size(),
        "127.0.0.1:33445");
    IOTOX_CHECK(!iotox::routes::parse_route_target_health(endpoint_leak));

    observation.network = {
        iotox::TransportKind::tox,
        iotox::ToxRoute::i2p};
    const std::string i2p_rendered =
        iotox::routes::render_route_target_health(observation);
    auto i2p_parsed =
        iotox::routes::parse_route_target_health(i2p_rendered);
    IOTOX_CHECK_MSG(i2p_parsed.ok(), i2p_parsed.status().message());
    IOTOX_CHECK(i2p_rendered.find("network=Tox/I2P\n") !=
                std::string::npos);
}

IOTOX_TEST("unknown network names fail closed") {
    auto parsed = iotox::parse_network_stack("carrier-pigeon");
    IOTOX_CHECK(!parsed);
    IOTOX_CHECK(parsed.status().code() == iotox::ErrorCode::invalid_argument);
}
