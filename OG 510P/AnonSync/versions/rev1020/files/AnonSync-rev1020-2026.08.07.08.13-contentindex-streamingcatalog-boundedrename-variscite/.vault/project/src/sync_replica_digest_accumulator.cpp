#include "sync_replica_digest_accumulator.hpp"

#include "sha256_digest.hpp"

#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <string_view>

namespace anonsync {
namespace {

using Words = std::array<std::uint64_t, 4U>;

[[nodiscard]] unsigned hex_nibble_or_throw(char value) {
    if (value >= '0' && value <= '9') {
        return static_cast<unsigned>(value - '0');
    }
    if (value >= 'a' && value <= 'f') {
        return static_cast<unsigned>(value - 'a' + 10);
    }
    throw std::invalid_argument(
        "sync replica digest accumulator input is not lowercase SHA-256");
}

[[nodiscard]] Words parse_words_or_throw(std::string_view digest) {
    if (!is_lowercase_sha256_hex(digest)) {
        throw std::invalid_argument(
            "sync replica digest accumulator input is not lowercase SHA-256");
    }
    Words words{};
    for (std::size_t word = 0U; word < words.size(); ++word) {
        std::uint64_t value = 0U;
        for (std::size_t nibble = 0U; nibble < 16U; ++nibble) {
            value = (value << 4U) |
                    static_cast<std::uint64_t>(hex_nibble_or_throw(
                        digest[word * 16U + nibble]));
        }
        words[word] = value;
    }
    return words;
}

[[nodiscard]] std::string encode_words(const Words& words) {
    constexpr char kHex[] = "0123456789abcdef";
    std::string result(64U, '0');
    for (std::size_t word = 0U; word < words.size(); ++word) {
        std::uint64_t value = words[word];
        for (std::size_t nibble = 0U; nibble < 16U; ++nibble) {
            const std::size_t output = word * 16U + (15U - nibble);
            result[output] = kHex[value & 0x0fU];
            value >>= 4U;
        }
    }
    return result;
}

[[nodiscard]] Words add_words(Words left, const Words& right) noexcept {
    std::uint64_t carry = 0U;
    for (std::size_t index = left.size(); index-- > 0U;) {
        const std::uint64_t with_right = left[index] + right[index];
        const std::uint64_t carry_from_right =
            with_right < left[index] ? 1U : 0U;
        const std::uint64_t with_carry = with_right + carry;
        const std::uint64_t carry_from_carry =
            with_carry < with_right ? 1U : 0U;
        left[index] = with_carry;
        carry = carry_from_right | carry_from_carry;
    }
    return left;
}

[[nodiscard]] Words subtract_words(Words left, const Words& right) noexcept {
    std::uint64_t borrow = 0U;
    for (std::size_t index = left.size(); index-- > 0U;) {
        const std::uint64_t with_right = left[index] - right[index];
        const std::uint64_t borrow_from_right =
            left[index] < right[index] ? 1U : 0U;
        const std::uint64_t with_borrow = with_right - borrow;
        const std::uint64_t borrow_from_borrow =
            with_right < borrow ? 1U : 0U;
        left[index] = with_borrow;
        borrow = borrow_from_right | borrow_from_borrow;
    }
    return left;
}

}  // namespace

std::string sync_replica_digest_accumulator_zero() {
    return std::string(64U, '0');
}

std::string sync_replica_digest_accumulator_add_or_throw(
    std::string_view accumulator_sha256,
    std::string_view element_sha256) {
    return encode_words(add_words(
        parse_words_or_throw(accumulator_sha256),
        parse_words_or_throw(element_sha256)));
}

std::string sync_replica_digest_accumulator_subtract_or_throw(
    std::string_view accumulator_sha256,
    std::string_view element_sha256) {
    return encode_words(subtract_words(
        parse_words_or_throw(accumulator_sha256),
        parse_words_or_throw(element_sha256)));
}

}  // namespace anonsync
