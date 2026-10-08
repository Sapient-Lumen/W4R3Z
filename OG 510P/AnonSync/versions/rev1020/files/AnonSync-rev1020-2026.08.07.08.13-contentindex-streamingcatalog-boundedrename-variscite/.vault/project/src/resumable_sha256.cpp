#include "resumable_sha256.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace {

constexpr std::array<std::uint32_t, 8U> kInitialHashWords = {
    0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
    0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U};

constexpr std::array<std::uint32_t, 64U> kRoundConstants = {
    0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
    0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
    0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
    0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
    0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
    0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
    0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
    0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
    0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
    0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
    0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
    0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
    0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
    0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
    0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
    0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U};

[[nodiscard]] constexpr std::uint32_t rotate_right(
    std::uint32_t value,
    unsigned count) noexcept {
    return (value >> count) | (value << (32U - count));
}

[[nodiscard]] constexpr std::uint32_t choose(
    std::uint32_t x,
    std::uint32_t y,
    std::uint32_t z) noexcept {
    return (x & y) ^ (~x & z);
}

[[nodiscard]] constexpr std::uint32_t majority(
    std::uint32_t x,
    std::uint32_t y,
    std::uint32_t z) noexcept {
    return (x & y) ^ (x & z) ^ (y & z);
}

[[nodiscard]] constexpr std::uint32_t big_sigma_zero(
    std::uint32_t value) noexcept {
    return rotate_right(value, 2U) ^ rotate_right(value, 13U) ^
           rotate_right(value, 22U);
}

[[nodiscard]] constexpr std::uint32_t big_sigma_one(
    std::uint32_t value) noexcept {
    return rotate_right(value, 6U) ^ rotate_right(value, 11U) ^
           rotate_right(value, 25U);
}

[[nodiscard]] constexpr std::uint32_t small_sigma_zero(
    std::uint32_t value) noexcept {
    return rotate_right(value, 7U) ^ rotate_right(value, 18U) ^
           (value >> 3U);
}

[[nodiscard]] constexpr std::uint32_t small_sigma_one(
    std::uint32_t value) noexcept {
    return rotate_right(value, 17U) ^ rotate_right(value, 19U) ^
           (value >> 10U);
}

[[nodiscard]] std::array<char, 64U> lowercase_hex_array(
    const std::array<std::uint8_t, 32U>& bytes) noexcept {
    static constexpr char kHex[] = "0123456789abcdef";
    std::array<char, 64U> output{};
    std::size_t position = 0U;
    for (const std::uint8_t byte : bytes) {
        output[position++] = kHex[(byte >> 4U) & 0x0fU];
        output[position++] = kHex[byte & 0x0fU];
    }
    return output;
}

[[noreturn]] void invalid_checkpoint(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " " + std::string(reason));
}

}  // namespace

void validate_resumable_sha256_checkpoint_or_throw(
    const ResumableSha256Checkpoint& checkpoint,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "resumable SHA-256 checkpoint label must not be empty");
    }
    if (checkpoint.total_bytes > kSha256MaximumMessageBytes) {
        invalid_checkpoint(label, "exceeds the SHA-256 message ceiling");
    }
    if (checkpoint.buffered_bytes >= checkpoint.buffered_block.size()) {
        invalid_checkpoint(label, "contains an invalid buffered-byte count");
    }
    if (checkpoint.total_bytes % checkpoint.buffered_block.size() !=
        checkpoint.buffered_bytes) {
        invalid_checkpoint(label, "byte count does not match its buffered tail");
    }
    const auto first_unused = checkpoint.buffered_block.begin() +
        static_cast<std::ptrdiff_t>(checkpoint.buffered_bytes);
    if (std::any_of(
            first_unused, checkpoint.buffered_block.end(),
            [](std::uint8_t byte) { return byte != 0U; })) {
        invalid_checkpoint(label, "contains noncanonical unused buffer bytes");
    }
}

ResumableSha256::ResumableSha256() {
    state_.hash_words = kInitialHashWords;
}

ResumableSha256::ResumableSha256(
    ResumableSha256Checkpoint checkpoint,
    std::string_view label)
    : state_(std::move(checkpoint)) {
    validate_resumable_sha256_checkpoint_or_throw(state_, label);
}

void ResumableSha256::require_updateable_or_throw() const {
    if (finished_) {
        throw std::logic_error("resumable SHA-256 builder is already finished");
    }
}

void ResumableSha256::process_block(const std::uint8_t* block) {
    std::array<std::uint32_t, 64U> schedule{};
    for (std::size_t index = 0U; index < 16U; ++index) {
        const std::size_t offset = index * 4U;
        schedule[index] =
            (static_cast<std::uint32_t>(block[offset]) << 24U) |
            (static_cast<std::uint32_t>(block[offset + 1U]) << 16U) |
            (static_cast<std::uint32_t>(block[offset + 2U]) << 8U) |
            static_cast<std::uint32_t>(block[offset + 3U]);
    }
    for (std::size_t index = 16U; index < schedule.size(); ++index) {
        schedule[index] = small_sigma_one(schedule[index - 2U]) +
            schedule[index - 7U] +
            small_sigma_zero(schedule[index - 15U]) +
            schedule[index - 16U];
    }

    std::uint32_t a = state_.hash_words[0U];
    std::uint32_t b = state_.hash_words[1U];
    std::uint32_t c = state_.hash_words[2U];
    std::uint32_t d = state_.hash_words[3U];
    std::uint32_t e = state_.hash_words[4U];
    std::uint32_t f = state_.hash_words[5U];
    std::uint32_t g = state_.hash_words[6U];
    std::uint32_t h = state_.hash_words[7U];

    for (std::size_t index = 0U; index < schedule.size(); ++index) {
        const std::uint32_t first = h + big_sigma_one(e) +
            choose(e, f, g) + kRoundConstants[index] + schedule[index];
        const std::uint32_t second = big_sigma_zero(a) + majority(a, b, c);
        h = g;
        g = f;
        f = e;
        e = d + first;
        d = c;
        c = b;
        b = a;
        a = first + second;
    }

    state_.hash_words[0U] += a;
    state_.hash_words[1U] += b;
    state_.hash_words[2U] += c;
    state_.hash_words[3U] += d;
    state_.hash_words[4U] += e;
    state_.hash_words[5U] += f;
    state_.hash_words[6U] += g;
    state_.hash_words[7U] += h;
}

void ResumableSha256::update(std::string_view bytes) {
    require_updateable_or_throw();
    const std::uint64_t byte_count =
        static_cast<std::uint64_t>(bytes.size());
    if (byte_count > kSha256MaximumMessageBytes - state_.total_bytes) {
        throw std::length_error(
            "resumable SHA-256 message exceeds the standard byte ceiling");
    }

    std::size_t input_position = 0U;
    if (state_.buffered_bytes != 0U) {
        const std::size_t available = state_.buffered_block.size() -
            static_cast<std::size_t>(state_.buffered_bytes);
        const std::size_t copied = std::min(available, bytes.size());
        if (copied != 0U) {
            std::copy_n(
                reinterpret_cast<const std::uint8_t*>(bytes.data()), copied,
                state_.buffered_block.begin() +
                    static_cast<std::ptrdiff_t>(state_.buffered_bytes));
        }
        state_.buffered_bytes += static_cast<std::uint32_t>(copied);
        input_position += copied;
        if (state_.buffered_bytes == state_.buffered_block.size()) {
            process_block(state_.buffered_block.data());
            state_.buffered_block.fill(0U);
            state_.buffered_bytes = 0U;
        }
    }

    while (bytes.size() - input_position >= state_.buffered_block.size()) {
        process_block(reinterpret_cast<const std::uint8_t*>(
            bytes.data() + input_position));
        input_position += state_.buffered_block.size();
    }

    const std::size_t tail = bytes.size() - input_position;
    if (tail != 0U) {
        std::copy_n(
            reinterpret_cast<const std::uint8_t*>(
                bytes.data() + input_position),
            tail, state_.buffered_block.begin());
        state_.buffered_bytes = static_cast<std::uint32_t>(tail);
    }
    state_.total_bytes += byte_count;
}

ResumableSha256Checkpoint ResumableSha256::checkpoint() const {
    require_updateable_or_throw();
    validate_resumable_sha256_checkpoint_or_throw(
        state_, "resumable SHA-256 live checkpoint");
    return state_;
}

std::array<std::uint8_t, 32U> ResumableSha256::finish_binary_array() {
    require_updateable_or_throw();
    finished_ = true;

    std::array<std::uint8_t, 128U> terminal{};
    const std::size_t buffered =
        static_cast<std::size_t>(state_.buffered_bytes);
    std::copy_n(state_.buffered_block.begin(), buffered, terminal.begin());
    terminal[buffered] = 0x80U;
    const std::size_t terminal_bytes =
        buffered + 1U + 8U <= 64U ? 64U : 128U;
    const std::uint64_t bit_count = state_.total_bytes * 8U;
    for (unsigned index = 0U; index < 8U; ++index) {
        terminal[terminal_bytes - 1U - index] =
            static_cast<std::uint8_t>(bit_count >> (index * 8U));
    }
    process_block(terminal.data());
    if (terminal_bytes == 128U) {
        process_block(terminal.data() + 64U);
    }
    std::array<std::uint8_t, 32U> output{};
    std::size_t position = 0U;
    for (const std::uint32_t word : state_.hash_words) {
        for (unsigned shift : {24U, 16U, 8U, 0U}) {
            output[position++] =
                static_cast<std::uint8_t>((word >> shift) & 0xffU);
        }
    }
    return output;
}

std::array<char, 64U> ResumableSha256::finish_hex_array() {
    return lowercase_hex_array(finish_binary_array());
}

std::string ResumableSha256::finish_hex() {
    const std::array<char, 64U> output = finish_hex_array();
    return {output.data(), output.size()};
}

}  // namespace anonsync
