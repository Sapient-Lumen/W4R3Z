#include "toxsync/hash.hpp"

#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <cstring>
#include <fstream>
#include <stdexcept>
#include <vector>

namespace toxsync {
namespace {

constexpr std::array<std::uint32_t, 64> kSha256K{
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
    0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U,
};

[[nodiscard]] constexpr std::uint32_t rotr(std::uint32_t value, unsigned count) noexcept {
    return std::rotr(value, static_cast<int>(count));
}

[[nodiscard]] std::uint32_t load_be32(const std::byte* bytes) noexcept {
    return (std::to_integer<std::uint32_t>(bytes[0]) << 24U) |
           (std::to_integer<std::uint32_t>(bytes[1]) << 16U) |
           (std::to_integer<std::uint32_t>(bytes[2]) << 8U) |
           std::to_integer<std::uint32_t>(bytes[3]);
}

void store_be32(std::byte* out, std::uint32_t value) noexcept {
    out[0] = static_cast<std::byte>(value >> 24U);
    out[1] = static_cast<std::byte>(value >> 16U);
    out[2] = static_cast<std::byte>(value >> 8U);
    out[3] = static_cast<std::byte>(value);
}

[[nodiscard]] std::uint64_t load_le64(const std::byte* data) noexcept {
    std::uint64_t value{};
    std::memcpy(&value, data, sizeof(value));
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    value = __builtin_bswap64(value);
#endif
    return value;
}

[[nodiscard]] constexpr std::uint64_t avalanche(std::uint64_t value) noexcept {
    value ^= value >> 29U;
    value *= 0x165667919E3779F9ULL;
    value ^= value >> 32U;
    value *= 0x9FB21C651E98DF25ULL;
    return value ^ (value >> 28U);
}

[[nodiscard]] std::uint64_t mum(std::uint64_t a, std::uint64_t b) noexcept {
#if defined(__SIZEOF_INT128__)
    __extension__ using WideProduct = unsigned __int128;
    const auto product = static_cast<WideProduct>(a) * static_cast<WideProduct>(b);
    return static_cast<std::uint64_t>(product) ^ static_cast<std::uint64_t>(product >> 64U);
#else
    const std::uint64_t a_lo = static_cast<std::uint32_t>(a);
    const std::uint64_t a_hi = a >> 32U;
    const std::uint64_t b_lo = static_cast<std::uint32_t>(b);
    const std::uint64_t b_hi = b >> 32U;
    const std::uint64_t lo = a_lo * b_lo;
    const std::uint64_t mid1 = a_hi * b_lo;
    const std::uint64_t mid2 = a_lo * b_hi;
    const std::uint64_t hi = a_hi * b_hi;
    return lo ^ std::rotl(mid1, 17) ^ std::rotl(mid2, 31) ^ hi;
#endif
}

[[nodiscard]] unsigned hex_nibble(char value) {
    if (value >= '0' && value <= '9') return static_cast<unsigned>(value - '0');
    if (value >= 'a' && value <= 'f') return static_cast<unsigned>(value - 'a' + 10);
    if (value >= 'A' && value <= 'F') return static_cast<unsigned>(value - 'A' + 10);
    throw std::invalid_argument("invalid hexadecimal digest");
}

} // namespace

std::string Digest256::hex() const {
    static constexpr char kHex[] = "0123456789abcdef";
    std::string output;
    output.resize(bytes.size() * 2U);
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        const auto value = std::to_integer<unsigned>(bytes[i]);
        output[i * 2U] = kHex[value >> 4U];
        output[i * 2U + 1U] = kHex[value & 0x0fU];
    }
    return output;
}

Digest256 Digest256::from_hex(const std::string& text) {
    if (text.size() != 64U) throw std::invalid_argument("SHA-256 text must contain 64 hexadecimal characters");
    Digest256 digest;
    for (std::size_t i = 0; i < digest.bytes.size(); ++i) {
        digest.bytes[i] = static_cast<std::byte>((hex_nibble(text[i * 2U]) << 4U) |
                                                 hex_nibble(text[i * 2U + 1U]));
    }
    return digest;
}

Hash128 fast_hash128(std::span<const std::byte> bytes) noexcept {
    constexpr std::uint64_t k0 = 0xa0761d6478bd642fULL;
    constexpr std::uint64_t k1 = 0xe7037ed1a0b428dbULL;
    constexpr std::uint64_t k2 = 0x8ebc6af09c88c6e3ULL;
    constexpr std::uint64_t k3 = 0x589965cc75374cc3ULL;

    std::uint64_t h1 = k0 ^ static_cast<std::uint64_t>(bytes.size());
    std::uint64_t h2 = k1 + static_cast<std::uint64_t>(bytes.size()) * k2;
    std::size_t offset{};
    while (offset + 32U <= bytes.size()) {
        const auto a0 = load_le64(bytes.data() + offset);
        const auto b0 = load_le64(bytes.data() + offset + 8U);
        const auto a1 = load_le64(bytes.data() + offset + 16U);
        const auto b1 = load_le64(bytes.data() + offset + 24U);
        h1 = mum(a0 ^ k1, h1 ^ b0 ^ k2);
        h2 = mum(b0 ^ k3, h2 ^ a0 ^ k0);
        h1 = mum(a1 ^ k1, h1 ^ b1 ^ k2);
        h2 = mum(b1 ^ k3, h2 ^ a1 ^ k0);
        offset += 32U;
    }
    if (offset + 16U <= bytes.size()) {
        const auto a = load_le64(bytes.data() + offset);
        const auto b = load_le64(bytes.data() + offset + 8U);
        h1 = mum(a ^ k1, h1 ^ b ^ k2);
        h2 = mum(b ^ k3, h2 ^ a ^ k0);
        offset += 16U;
    }

    std::array<std::byte, 16> tail{};
    const auto remaining = bytes.size() - offset;
    if (remaining != 0U) {
        std::memcpy(tail.data(), bytes.data() + offset, remaining);
    }
    const auto a = load_le64(tail.data());
    const auto b = load_le64(tail.data() + 8U);
    h1 = mum(a ^ k2, h1 ^ b ^ k3);
    h2 = mum(b ^ k0, h2 ^ a ^ k1);
    return {avalanche(h1 ^ std::rotl(h2, 23)), avalanche(h2 ^ std::rotl(h1, 41))};
}

Sha256::Sha256() noexcept
    : state_{0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
             0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U} {}

void Sha256::transform(const std::byte* block) noexcept {
    std::array<std::uint32_t, 64> words{};
    for (std::size_t i = 0; i < 16U; ++i) words[i] = load_be32(block + i * 4U);
    for (std::size_t i = 16U; i < words.size(); ++i) {
        const auto s0 = rotr(words[i - 15U], 7U) ^ rotr(words[i - 15U], 18U) ^ (words[i - 15U] >> 3U);
        const auto s1 = rotr(words[i - 2U], 17U) ^ rotr(words[i - 2U], 19U) ^ (words[i - 2U] >> 10U);
        words[i] = words[i - 16U] + s0 + words[i - 7U] + s1;
    }

    auto a = state_[0]; auto b = state_[1]; auto c = state_[2]; auto d = state_[3];
    auto e = state_[4]; auto f = state_[5]; auto g = state_[6]; auto h = state_[7];
    for (std::size_t i = 0; i < words.size(); ++i) {
        const auto s1 = rotr(e, 6U) ^ rotr(e, 11U) ^ rotr(e, 25U);
        const auto ch = (e & f) ^ ((~e) & g);
        const auto temp1 = h + s1 + ch + kSha256K[i] + words[i];
        const auto s0 = rotr(a, 2U) ^ rotr(a, 13U) ^ rotr(a, 22U);
        const auto maj = (a & b) ^ (a & c) ^ (b & c);
        const auto temp2 = s0 + maj;
        h = g; g = f; f = e; e = d + temp1;
        d = c; c = b; b = a; a = temp1 + temp2;
    }
    state_[0] += a; state_[1] += b; state_[2] += c; state_[3] += d;
    state_[4] += e; state_[5] += f; state_[6] += g; state_[7] += h;
}

void Sha256::update(std::span<const std::byte> bytes) noexcept {
    if (finished_ || bytes.empty()) return;
    total_bytes_ += bytes.size();
    std::size_t offset{};
    if (buffered_ != 0U) {
        const auto take = std::min(buffer_.size() - buffered_, bytes.size());
        std::memcpy(buffer_.data() + buffered_, bytes.data(), take);
        buffered_ += take;
        offset += take;
        if (buffered_ == buffer_.size()) {
            transform(buffer_.data());
            buffered_ = 0U;
        }
    }
    while (offset + buffer_.size() <= bytes.size()) {
        transform(bytes.data() + offset);
        offset += buffer_.size();
    }
    if (offset < bytes.size()) {
        buffered_ = bytes.size() - offset;
        std::memcpy(buffer_.data(), bytes.data() + offset, buffered_);
    }
}

Digest256 Sha256::finish() noexcept {
    if (!finished_) {
        const auto bit_length = total_bytes_ * 8ULL;
        buffer_[buffered_++] = std::byte{0x80};
        if (buffered_ > 56U) {
            std::fill(buffer_.begin() + static_cast<std::ptrdiff_t>(buffered_), buffer_.end(), std::byte{});
            transform(buffer_.data());
            buffered_ = 0U;
        }
        std::fill(buffer_.begin() + static_cast<std::ptrdiff_t>(buffered_), buffer_.begin() + 56, std::byte{});
        for (unsigned i = 0; i < 8U; ++i) {
            buffer_[63U - i] = static_cast<std::byte>(bit_length >> (i * 8U));
        }
        transform(buffer_.data());
        buffered_ = 0U;
        finished_ = true;
    }
    Digest256 digest;
    for (std::size_t i = 0; i < state_.size(); ++i) store_be32(digest.bytes.data() + i * 4U, state_[i]);
    return digest;
}


} // namespace toxsync
