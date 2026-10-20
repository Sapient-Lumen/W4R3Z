#include "toxsync/rolling_checksum.hpp"

#include <cstddef>
#include <cstdint>

#if !defined(TOXSYNC_DISABLE_SIMD) && (defined(__x86_64__) || defined(_M_X64))
#include <emmintrin.h>
#define TOXSYNC_ROLLING_SSE2 1
#elif !defined(TOXSYNC_DISABLE_SIMD) && defined(__aarch64__)
#include <arm_neon.h>
#define TOXSYNC_ROLLING_NEON 1
#endif

namespace toxsync {

RollingChecksum RollingChecksum::compute(std::span<const std::byte> bytes) noexcept {
    // For a group x[0..n), the rsync checksum recurrence is equivalent to:
    //   next_a = a + sum(x)
    //   next_b = b + n*a + sum((n-i)*x[i])
    // This breaks the byte-by-byte dependency and gives SIMD backends two
    // independent reductions. The 16 MiB format limit keeps 64-bit totals safe.
    std::uint64_t a{};
    std::uint64_t b{};
    const auto* input = bytes.data();
    std::size_t remaining = bytes.size();

#if defined(TOXSYNC_ROLLING_SSE2)
    const auto zero = _mm_setzero_si128();
    const auto weights_lo = _mm_setr_epi16(16, 15, 14, 13, 12, 11, 10, 9);
    const auto weights_hi = _mm_setr_epi16(8, 7, 6, 5, 4, 3, 2, 1);
    while (remaining >= 16U) {
        const auto packed = _mm_loadu_si128(reinterpret_cast<const __m128i*>(input));
        const auto sad = _mm_sad_epu8(packed, zero);
        const auto sum = static_cast<std::uint64_t>(_mm_cvtsi128_si64(sad)) +
                         static_cast<std::uint64_t>(_mm_cvtsi128_si64(_mm_unpackhi_epi64(sad, sad)));
        auto weighted = _mm_add_epi32(
            _mm_madd_epi16(_mm_unpacklo_epi8(packed, zero), weights_lo),
            _mm_madd_epi16(_mm_unpackhi_epi8(packed, zero), weights_hi));
        weighted = _mm_add_epi32(weighted,
                                 _mm_shuffle_epi32(weighted, _MM_SHUFFLE(1, 0, 3, 2)));
        weighted = _mm_add_epi32(weighted,
                                 _mm_shuffle_epi32(weighted, _MM_SHUFFLE(2, 3, 0, 1)));
        b += 16U * a + static_cast<std::uint32_t>(_mm_cvtsi128_si32(weighted));
        a += sum;
        input += 16U;
        remaining -= 16U;
    }
#elif defined(TOXSYNC_ROLLING_NEON)
    static constexpr std::uint8_t kWeights[16]{
        16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    };
    const auto weights = vld1q_u8(kWeights);
    while (remaining >= 16U) {
        const auto packed = vld1q_u8(reinterpret_cast<const std::uint8_t*>(input));
        const auto sum = static_cast<std::uint64_t>(vaddlvq_u8(packed));
        const auto products_lo = vmull_u8(vget_low_u8(packed), vget_low_u8(weights));
        const auto products_hi = vmull_u8(vget_high_u8(packed), vget_high_u8(weights));
        const auto weighted = static_cast<std::uint64_t>(vaddlvq_u16(products_lo)) +
                              static_cast<std::uint64_t>(vaddlvq_u16(products_hi));
        b += 16U * a + weighted;
        a += sum;
        input += 16U;
        remaining -= 16U;
    }
#else
    while (remaining >= 16U) {
        const auto x0 = std::to_integer<std::uint64_t>(input[0]);
        const auto x1 = std::to_integer<std::uint64_t>(input[1]);
        const auto x2 = std::to_integer<std::uint64_t>(input[2]);
        const auto x3 = std::to_integer<std::uint64_t>(input[3]);
        const auto x4 = std::to_integer<std::uint64_t>(input[4]);
        const auto x5 = std::to_integer<std::uint64_t>(input[5]);
        const auto x6 = std::to_integer<std::uint64_t>(input[6]);
        const auto x7 = std::to_integer<std::uint64_t>(input[7]);
        const auto x8 = std::to_integer<std::uint64_t>(input[8]);
        const auto x9 = std::to_integer<std::uint64_t>(input[9]);
        const auto xa = std::to_integer<std::uint64_t>(input[10]);
        const auto xb = std::to_integer<std::uint64_t>(input[11]);
        const auto xc = std::to_integer<std::uint64_t>(input[12]);
        const auto xd = std::to_integer<std::uint64_t>(input[13]);
        const auto xe = std::to_integer<std::uint64_t>(input[14]);
        const auto xf = std::to_integer<std::uint64_t>(input[15]);
        const auto sum = x0 + x1 + x2 + x3 + x4 + x5 + x6 + x7 +
                         x8 + x9 + xa + xb + xc + xd + xe + xf;
        const auto weighted = 16U * x0 + 15U * x1 + 14U * x2 + 13U * x3 +
                              12U * x4 + 11U * x5 + 10U * x6 + 9U * x7 +
                               8U * x8 +  7U * x9 +  6U * xa + 5U * xb +
                               4U * xc +  3U * xd +  2U * xe +      xf;
        b += 16U * a + weighted;
        a += sum;
        input += 16U;
        remaining -= 16U;
    }
#endif

    while (remaining != 0U) {
        a += std::to_integer<std::uint64_t>(*input++);
        b += a;
        --remaining;
    }
    return RollingChecksum{
        .a = static_cast<std::uint32_t>(a) & 0xffffU,
        .b = static_cast<std::uint32_t>(b) & 0xffffU,
        .window = static_cast<std::uint32_t>(bytes.size()),
    };
}

std::string_view rolling_checksum_backend_name() noexcept {
#if defined(TOXSYNC_ROLLING_SSE2)
    return "sse2";
#elif defined(TOXSYNC_ROLLING_NEON)
    return "aarch64-neon";
#else
    return "scalar-unrolled";
#endif
}

} // namespace toxsync

#if defined(TOXSYNC_ROLLING_SSE2)
#undef TOXSYNC_ROLLING_SSE2
#elif defined(TOXSYNC_ROLLING_NEON)
#undef TOXSYNC_ROLLING_NEON
#endif
