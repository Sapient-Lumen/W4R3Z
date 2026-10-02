#pragma once

#include "iotox/status.hpp"

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace iotox {

// The application transport and the route used by that transport are separate
// concepts. This distinction keeps "Tox over Tor" separate from a future
// direct Tor transport that does not use Tox at all.
enum class TransportKind {
    tox,
    i2p_direct_reserved,
    tor_direct_reserved,
};

enum class ToxRoute {
    native,
    i2p,
    i2p_construction,
    tor,
};

// Strict routed-Tox construction deliberately accepts only a numeric SOCKS5
// endpoint. c-toxcore resolves the proxy host before opening it, so accepting
// a hostname while claiming native-DNS containment would be a leak-prone
// contract.
struct Socks5ProxyEndpoint {
    std::string host;
    std::uint16_t port{0U};

    [[nodiscard]] bool operator==(const Socks5ProxyEndpoint &) const = default;
};

struct NetworkStack {
    TransportKind transport{TransportKind::tox};
    ToxRoute tox_route{ToxRoute::native};

    [[nodiscard]] bool operator==(const NetworkStack &) const = default;
    [[nodiscard]] bool implemented() const noexcept;
    [[nodiscard]] std::string name() const;
};

struct NetworkCapability {
    NetworkStack stack;
    std::string status;
    std::string intent;
};

[[nodiscard]] std::vector<NetworkCapability> network_capabilities();
[[nodiscard]] Result<NetworkStack> parse_network_stack(std::string_view text);
// Text form is IPv4:PORT or [IPv6]:PORT. Hostnames, scope identifiers, zero,
// whitespace, trailing records, and unbracketed IPv6 fail closed.
[[nodiscard]] Result<Socks5ProxyEndpoint> parse_socks5_proxy_endpoint(
    std::string_view text);
[[nodiscard]] bool is_strict_socks_tox_route(ToxRoute route) noexcept;
[[nodiscard]] bool is_numeric_ip_address(std::string_view text) noexcept;
[[nodiscard]] std::string format_socks5_proxy_endpoint(
    const Socks5ProxyEndpoint &endpoint);
[[nodiscard]] std::string to_string(TransportKind value);
[[nodiscard]] std::string to_string(ToxRoute value);

}  // namespace iotox
