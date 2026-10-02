#include "iotox/toxcore/bootstrap.hpp"

#include <cctype>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>

namespace iotox::toxcore {
namespace {

int hex_nibble(char value) {
    if (value >= '0' && value <= '9') {
        return value - '0';
    }
    if (value >= 'a' && value <= 'f') {
        return 10 + value - 'a';
    }
    if (value >= 'A' && value <= 'F') {
        return 10 + value - 'A';
    }
    return -1;
}

Result<std::uint16_t> parse_port(std::string_view text) {
    if (text.empty()) {
        return Status{ErrorCode::invalid_argument, "bootstrap port is empty"};
    }
    std::uint32_t value = 0U;
    for (const char character : text) {
        if (character < '0' || character > '9') {
            return Status{ErrorCode::invalid_argument,
                          "bootstrap port contains a non-decimal character"};
        }
        value = value * 10U + static_cast<std::uint32_t>(character - '0');
        if (value > std::numeric_limits<std::uint16_t>::max()) {
            return Status{ErrorCode::invalid_argument, "bootstrap port exceeds 65535"};
        }
    }
    if (value == 0U) {
        return Status{ErrorCode::invalid_argument, "bootstrap port zero is invalid"};
    }
    return static_cast<std::uint16_t>(value);
}

Result<std::array<std::uint8_t, 32U>> parse_public_key(std::string_view text) {
    if (text.size() != 64U) {
        return Status{ErrorCode::invalid_argument,
                      "bootstrap public key must contain exactly 64 hexadecimal characters"};
    }
    std::array<std::uint8_t, 32U> key{};
    for (std::size_t index = 0U; index < key.size(); ++index) {
        const int high = hex_nibble(text[index * 2U]);
        const int low = hex_nibble(text[index * 2U + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::invalid_argument,
                          "bootstrap public key contains a non-hexadecimal character"};
        }
        key[index] = static_cast<std::uint8_t>((high << 4) | low);
    }
    return key;
}

bool valid_host(std::string_view host) {
    if (host.empty() || host.size() > 255U) {
        return false;
    }
    for (const char character : host) {
        const auto value = static_cast<unsigned char>(character);
        if (value == 0U || std::isspace(value) != 0) {
            return false;
        }
    }
    return true;
}

}  // namespace

Result<BootstrapEndpoint> parse_bootstrap_endpoint(std::string_view text) {
    std::string_view host;
    std::string_view remainder;
    if (!text.empty() && text.front() == '[') {
        const std::size_t closing = text.find(']');
        if (closing == std::string_view::npos || closing == 1U ||
            closing + 1U >= text.size() || text[closing + 1U] != ':') {
            return Status{ErrorCode::invalid_argument,
                          "bracketed bootstrap host must use [host]:port:key"};
        }
        host = text.substr(1U, closing - 1U);
        remainder = text.substr(closing + 2U);
    } else {
        const std::size_t separator = text.find(':');
        if (separator == std::string_view::npos) {
            return Status{ErrorCode::invalid_argument,
                          "bootstrap endpoint must use host:port:key"};
        }
        host = text.substr(0U, separator);
        remainder = text.substr(separator + 1U);
    }

    const std::size_t key_separator = remainder.find(':');
    if (key_separator == std::string_view::npos ||
        remainder.find(':', key_separator + 1U) != std::string_view::npos) {
        return Status{ErrorCode::invalid_argument,
                      "bootstrap endpoint must contain one port and one public key"};
    }
    const std::string_view port_text = remainder.substr(0U, key_separator);
    const std::string_view key_text = remainder.substr(key_separator + 1U);

    if (!valid_host(host)) {
        return Status{ErrorCode::invalid_argument,
                      "bootstrap host is empty, too long, or contains whitespace"};
    }
    auto port = parse_port(port_text);
    if (!port) {
        return port.status();
    }
    auto key = parse_public_key(key_text);
    if (!key) {
        return key.status();
    }

    BootstrapEndpoint endpoint;
    endpoint.host = std::string(host);
    endpoint.port = port.value();
    endpoint.public_key = key.value();
    return endpoint;
}

std::string format_bootstrap_endpoint(const BootstrapEndpoint &endpoint) {
    std::ostringstream output;
    const bool bracket = endpoint.host.find(':') != std::string::npos;
    if (bracket) {
        output << '[' << endpoint.host << ']';
    } else {
        output << endpoint.host;
    }
    output << ':' << endpoint.port << ':' << std::hex << std::uppercase << std::setfill('0');
    for (const std::uint8_t byte : endpoint.public_key) {
        output << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return output.str();
}

}  // namespace iotox::toxcore
