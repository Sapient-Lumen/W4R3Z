#include "test_harness.hpp"
#include "test_support.hpp"
#include "toxsync/hash.hpp"
#include "toxsync/rolling_checksum.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <string_view>

TOXSYNC_TEST(sha256_known_vectors) {
    const std::string_view empty;
    REQUIRE(toxsync::sha256(std::as_bytes(std::span(empty))).hex() ==
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    const std::string_view abc = "abc";
    REQUIRE(toxsync::sha256(std::as_bytes(std::span(abc))).hex() ==
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
}

TOXSYNC_TEST(sha256_streaming_matches_one_shot) {
    const auto bytes = test::pattern(100003U, 0x12345678U);
    toxsync::Sha256 stream;
    stream.update(std::span<const std::byte>(bytes.data(), 17U));
    stream.update(std::span<const std::byte>(bytes.data() + 17U, 8192U));
    stream.update(std::span<const std::byte>(bytes.data() + 8209U, bytes.size() - 8209U));
    REQUIRE(stream.finish() == toxsync::sha256(bytes));
}

TOXSYNC_TEST(digest_hex_round_trip) {
    const auto digest = toxsync::sha256(test::pattern(99U, 44U));
    REQUIRE(toxsync::Digest256::from_hex(digest.hex()) == digest);
    REQUIRE_THROWS(toxsync::Digest256::from_hex("bad"));
}

TOXSYNC_TEST(rolling_checksum_roll_matches_recompute) {
    const auto bytes = test::pattern(2049U, 88U);
    constexpr std::size_t window = 128U;
    auto rolling = toxsync::RollingChecksum::compute(std::span<const std::byte>(bytes.data(), window));
    for (std::size_t offset = 1U; offset + window <= bytes.size(); ++offset) {
        rolling.roll(bytes[offset - 1U], bytes[offset + window - 1U]);
        const auto recomputed = toxsync::RollingChecksum::compute(
            std::span<const std::byte>(bytes.data() + offset, window));
        REQUIRE(rolling.value() == recomputed.value());
    }
}

TOXSYNC_TEST(fast_hash_is_stable_and_sensitive) {
    auto left = test::pattern(4096U, 7U);
    auto right = left;
    right[2048] ^= std::byte{0x80};
    REQUIRE(toxsync::fast_hash128(left) == toxsync::fast_hash128(left));
    REQUIRE(!(toxsync::fast_hash128(left) == toxsync::fast_hash128(right)));
}


TOXSYNC_TEST(rolling_checksum_matches_scalar_definition_for_varied_windows) {
    const auto bytes = test::pattern(513U, 0xdeadbeefU);
    for (std::size_t length = 0U; length <= bytes.size(); ++length) {
        std::uint64_t a{};
        std::uint64_t b{};
        for (std::size_t i = 0U; i < length; ++i) {
            a += std::to_integer<std::uint64_t>(bytes[i]);
            b += static_cast<std::uint64_t>(length - i) *
                 std::to_integer<std::uint64_t>(bytes[i]);
        }
        const auto expected = static_cast<std::uint32_t>(a & 0xffffU) |
                              (static_cast<std::uint32_t>(b & 0xffffU) << 16U);
        REQUIRE(toxsync::RollingChecksum::compute(
                    std::span<const std::byte>(bytes.data(), length)).value() == expected);
    }
}

TOXSYNC_TEST(selected_sha256_backend_matches_portable_streaming_core) {
    const auto bytes = test::pattern(2U * 1024U * 1024U + 17U, 0x77112233U);
    toxsync::Sha256 portable;
    for (std::size_t offset = 0U; offset < bytes.size();) {
        const auto count = std::min<std::size_t>(7919U, bytes.size() - offset);
        portable.update(std::span<const std::byte>(bytes.data() + offset, count));
        offset += count;
    }
    REQUIRE(toxsync::sha256(bytes) == portable.finish());
    REQUIRE(!toxsync::sha256_backend_name().empty());
}

TOXSYNC_TEST(fast_hash_v1_regression_vectors) {
    struct Vector {
        std::size_t size;
        std::uint64_t lo;
        std::uint64_t hi;
    };
    constexpr std::array vectors{
        Vector{0U,    0x90aac663dc1fa2aeULL, 0x1c19fb926bb5c3fcULL},
        Vector{1U,    0x1c11d941c3aeb1e2ULL, 0x94579706f2dac349ULL},
        Vector{15U,   0x809407d3e1161eefULL, 0xcfb0fbea70f8b1bfULL},
        Vector{16U,   0xb349e09f47f8eec7ULL, 0x430c01ed7bd768b2ULL},
        Vector{17U,   0xf48598e9f8a28eb3ULL, 0xd8b3b4e62d4fe240ULL},
        Vector{31U,   0x599cda1d267e6128ULL, 0x1294ef30a4265fe7ULL},
        Vector{32U,   0x7e49c4e9e3c4f034ULL, 0x71fd179c17c14153ULL},
        Vector{33U,   0xb7074ba8a5ff326eULL, 0x4a39a0b09b4d35fcULL},
        Vector{4096U, 0x51c2d1f00351f959ULL, 0xf40d5edb1d9640eeULL},
    };
    for (const auto& vector : vectors) {
        const auto actual = toxsync::fast_hash128(test::pattern(vector.size, 7U));
        REQUIRE(actual == (toxsync::Hash128{vector.lo, vector.hi}));
    }
    REQUIRE(!toxsync::rolling_checksum_backend_name().empty());
}
