#pragma once

#include "iotox/status.hpp"

#include <array>
#include <cstdint>
#include <string>
#include <string_view>

namespace iotox::toxcore {

struct BootstrapEndpoint {
    std::string host;
    std::uint16_t port{0U};
    std::array<std::uint8_t, 32U> public_key{};

    [[nodiscard]] bool operator==(const BootstrapEndpoint &) const = default;
};

// Text form:
//   hostname:port:64_HEX_DIGITS
//   IPv4:port:64_HEX_DIGITS
//   [IPv6]:port:64_HEX_DIGITS
[[nodiscard]] Result<BootstrapEndpoint> parse_bootstrap_endpoint(std::string_view text);
[[nodiscard]] std::string format_bootstrap_endpoint(const BootstrapEndpoint &endpoint);

}  // namespace iotox::toxcore
