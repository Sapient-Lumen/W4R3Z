#include "iotox/network.hpp"

#include <algorithm>
#include <arpa/inet.h>
#include <cctype>
#include <limits>

namespace iotox {
namespace {

std::string lowercase(std::string_view input) {
    std::string output(input);
    std::transform(output.begin(), output.end(), output.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return output;
}

}  // namespace

bool NetworkStack::implemented() const noexcept {
    return transport == TransportKind::tox &&
           (tox_route == ToxRoute::native ||
            is_strict_socks_tox_route(tox_route));
}

std::string NetworkStack::name() const {
    if (transport == TransportKind::tox) {
        return "Tox/" + to_string(tox_route);
    }
    return to_string(transport);
}

std::vector<NetworkCapability> network_capabilities() {
    return {
        {{TransportKind::tox, ToxRoute::native}, "adapter-verified",
         "Current build target: c-toxcore through an isolated C++ runtime adapter."},
        {{TransportKind::tox, ToxRoute::i2p}, "vm-qualified",
         "Strict TCP-only Tox through an owner-controlled numeric SOCKS-to-SAM I2P boundary; no native fallback."},
        {{TransportKind::tox, ToxRoute::i2p_construction}, "compatibility-alias",
         "Deprecated laboratory spelling for reproducing pre-promotion Tox/I2P evidence."},
        {{TransportKind::tox, ToxRoute::tor}, "construction-enabled",
         "Strict TCP-only Tox through one explicit numeric SOCKS5 endpoint and numeric bootstrap/relay records."},
        {{TransportKind::i2p_direct_reserved, ToxRoute::native}, "out-of-scope",
         "Separate future peer transport using I2P directly, without Tox semantics."},
        {{TransportKind::tor_direct_reserved, ToxRoute::native}, "out-of-scope",
         "Separate future peer transport using Tor directly, without Tox semantics."},
    };
}

Result<NetworkStack> parse_network_stack(std::string_view text) {
    const std::string value = lowercase(text);
    if (value == "tox" || value == "tox/native" || value == "native") {
        return NetworkStack{TransportKind::tox, ToxRoute::native};
    }
    if (value == "tox/i2p" || value == "tox-over-i2p") {
        return NetworkStack{TransportKind::tox, ToxRoute::i2p};
    }
    if (value == "tox/i2p-construction") {
        return NetworkStack{TransportKind::tox, ToxRoute::i2p_construction};
    }
    if (value == "tox/tor" || value == "tox-over-tor") {
        return NetworkStack{TransportKind::tox, ToxRoute::tor};
    }
    if (value == "i2p" || value == "i2p-direct") {
        return NetworkStack{TransportKind::i2p_direct_reserved, ToxRoute::native};
    }
    if (value == "tor" || value == "tor-direct") {
        return NetworkStack{TransportKind::tor_direct_reserved, ToxRoute::native};
    }
    return Status{ErrorCode::invalid_argument, "unknown network stack: " + std::string(text)};
}

bool is_strict_socks_tox_route(ToxRoute route) noexcept {
    return route == ToxRoute::tor || route == ToxRoute::i2p ||
           route == ToxRoute::i2p_construction;
}

bool is_numeric_ip_address(std::string_view text) noexcept {
    if (text.empty() || text.size() > INET6_ADDRSTRLEN - 1U ||
        text.find('\0') != std::string_view::npos) {
        return false;
    }
    const std::string candidate(text);
    in_addr ipv4{};
    in6_addr ipv6{};
    return ::inet_pton(AF_INET, candidate.c_str(), &ipv4) == 1 ||
           ::inet_pton(AF_INET6, candidate.c_str(), &ipv6) == 1;
}

Result<Socks5ProxyEndpoint> parse_socks5_proxy_endpoint(
    std::string_view text) {
    std::string_view host;
    std::string_view port_text;
    if (!text.empty() && text.front() == '[') {
        const std::size_t closing = text.find(']');
        if (closing == std::string_view::npos || closing == 1U ||
            closing + 2U > text.size() || text[closing + 1U] != ':' ||
            text.find('[', 1U) != std::string_view::npos ||
            text.find(']', closing + 1U) != std::string_view::npos) {
            return Status{ErrorCode::invalid_argument,
                          "SOCKS5 proxy must use [IPv6]:PORT"};
        }
        host = text.substr(1U, closing - 1U);
        port_text = text.substr(closing + 2U);
    } else {
        const std::size_t separator = text.find(':');
        if (separator == std::string_view::npos ||
            text.find(':', separator + 1U) != std::string_view::npos) {
            return Status{ErrorCode::invalid_argument,
                          "SOCKS5 proxy must use IPv4:PORT or [IPv6]:PORT"};
        }
        host = text.substr(0U, separator);
        port_text = text.substr(separator + 1U);
    }
    if (!is_numeric_ip_address(host)) {
        return Status{ErrorCode::invalid_argument,
                      "SOCKS5 proxy host must be a numeric IP address"};
    }
    if (port_text.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "SOCKS5 proxy port is empty"};
    }
    std::uint32_t port = 0U;
    for (const char character : port_text) {
        if (character < '0' || character > '9') {
            return Status{ErrorCode::invalid_argument,
                          "SOCKS5 proxy port must be decimal"};
        }
        const std::uint32_t digit =
            static_cast<std::uint32_t>(character - '0');
        if (port >
            (std::numeric_limits<std::uint16_t>::max() - digit) / 10U) {
            return Status{ErrorCode::invalid_argument,
                          "SOCKS5 proxy port exceeds 65535"};
        }
        port = port * 10U + digit;
    }
    if (port == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "SOCKS5 proxy port zero is invalid"};
    }
    return Socks5ProxyEndpoint{
        std::string(host), static_cast<std::uint16_t>(port)};
}

std::string format_socks5_proxy_endpoint(
    const Socks5ProxyEndpoint &endpoint) {
    if (endpoint.host.find(':') != std::string::npos) {
        return '[' + endpoint.host + "]:" + std::to_string(endpoint.port);
    }
    return endpoint.host + ':' + std::to_string(endpoint.port);
}

std::string to_string(TransportKind value) {
    switch (value) {
        case TransportKind::tox:
            return "Tox";
        case TransportKind::i2p_direct_reserved:
            return "I2P-direct";
        case TransportKind::tor_direct_reserved:
            return "Tor-direct";
    }
    return "unknown";
}

std::string to_string(ToxRoute value) {
    switch (value) {
        case ToxRoute::native:
            return "native";
        case ToxRoute::i2p:
            return "I2P";
        case ToxRoute::i2p_construction:
            return "I2P-construction";
        case ToxRoute::tor:
            return "Tor";
    }
    return "unknown";
}

}  // namespace iotox
