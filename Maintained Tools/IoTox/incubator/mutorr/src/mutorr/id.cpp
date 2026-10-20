#include "iotox/mutorr/id.hpp"

#include <algorithm>
#include <array>
#include <charconv>

namespace iotox::mutorr {
namespace {

std::uint64_t mix64(std::uint64_t value) noexcept {
    value += 0x9E3779B97F4A7C15ULL;
    value = (value ^ (value >> 30U)) * 0xBF58476D1CE4E5B9ULL;
    value = (value ^ (value >> 27U)) * 0x94D049BB133111EBULL;
    return value ^ (value >> 31U);
}

int hex_value(char value) noexcept {
    if (value >= '0' && value <= '9') {
        return value - '0';
    }
    if (value >= 'a' && value <= 'f') {
        return value - 'a' + 10;
    }
    if (value >= 'A' && value <= 'F') {
        return value - 'A' + 10;
    }
    return -1;
}

}  // namespace

bool Id256::is_zero() const noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t value) { return value == 0U; });
}

std::string Id256::hex() const {
    static constexpr std::array<char, 16> digits{
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};

    std::string output;
    output.resize(bytes.size() * 2U);
    for (std::size_t index = 0; index < bytes.size(); ++index) {
        output[index * 2U] = digits[bytes[index] >> 4U];
        output[index * 2U + 1U] = digits[bytes[index] & 0x0FU];
    }
    return output;
}

Result<Id256> Id256::from_hex(std::string_view text) {
    if (text.size() != kIdSize * 2U) {
        return Status{ErrorCode::invalid_argument, "256-bit identifier must contain exactly 64 hex characters"};
    }

    Id256 identifier;
    for (std::size_t index = 0; index < identifier.bytes.size(); ++index) {
        const int high = hex_value(text[index * 2U]);
        const int low = hex_value(text[index * 2U + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::invalid_argument, "256-bit identifier contains a non-hex character"};
        }
        identifier.bytes[index] = static_cast<std::uint8_t>((high << 4) | low);
    }
    return identifier;
}

Id256 synthetic_id(std::uint64_t value, std::uint64_t domain) noexcept {
    Id256 output;
    std::uint64_t state = mix64(value ^ (domain + 0xD6E8FEB86659FD93ULL));
    for (std::size_t lane = 0; lane < output.bytes.size() / 8U; ++lane) {
        state = mix64(state ^ value ^ (domain + static_cast<std::uint64_t>(lane)));
        for (std::size_t byte = 0; byte < 8U; ++byte) {
            output.bytes[lane * 8U + byte] =
                static_cast<std::uint8_t>((state >> static_cast<unsigned>(56U - byte * 8U)) & 0xFFU);
        }
    }
    return output;
}

}  // namespace iotox::mutorr
