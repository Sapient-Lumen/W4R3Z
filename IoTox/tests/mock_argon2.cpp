#include "iotox/security/argon2_abi.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <string_view>

#if defined(__GNUC__) || defined(__clang__)
#define IOTOX_MOCK_EXPORT __attribute__((visibility("default")))
#else
#define IOTOX_MOCK_EXPORT
#endif

namespace {
constexpr std::array<std::uint8_t, 16> kExpectedSalt = {
    'I', 'o', 'T', 'o', 'x', 'R', 'e', 'c', 'a', 'l', 'l', 'R', 'o', 'o', 't', '1'};
constexpr std::string_view kExpectedPhrase =
    "abacus abdomen abdominal abide abiding ability ablaze able";
constexpr std::string_view kSuccessorFixturePhrase =
    "absentee absently absinthe absolute absolve abstain abstract absurd";
}  // namespace

extern "C" IOTOX_MOCK_EXPORT int argon2id_ctx(argon2_context *context) {
    if (context == nullptr || context->out == nullptr || context->pwd == nullptr ||
        context->salt == nullptr) {
        return -25;
    }
    if (context->outlen != 32U || context->t_cost != 3U || context->m_cost != 65'536U ||
        context->lanes != 4U || context->threads != 4U || context->version != 0x13U ||
        context->saltlen != kExpectedSalt.size() ||
        context->secret != nullptr || context->secretlen != 0U || context->ad != nullptr ||
        context->adlen != 0U || context->allocate_cbk != nullptr || context->free_cbk != nullptr ||
        (context->flags & 1U) == 0U) {
        return -25;
    }
    const bool known_answer =
        context->pwdlen == kExpectedPhrase.size() &&
        std::memcmp(context->pwd, kExpectedPhrase.data(), kExpectedPhrase.size()) == 0;
    const bool successor_fixture =
        context->pwdlen == kSuccessorFixturePhrase.size() &&
        std::memcmp(context->pwd, kSuccessorFixturePhrase.data(),
                    kSuccessorFixturePhrase.size()) == 0;
    if (!std::equal(kExpectedSalt.begin(), kExpectedSalt.end(), context->salt) ||
        (!known_answer && !successor_fixture)) {
        return -25;
    }

    for (std::uint32_t index = 0U; index < context->outlen; ++index) {
        const std::uint8_t base = known_answer ? 0xA0U : 0x40U;
        context->out[index] = static_cast<std::uint8_t>(base + index);
    }
    if ((context->flags & 1U) != 0U) {
        std::fill_n(context->pwd, context->pwdlen, std::uint8_t{0});
    }
    return 0;
}

extern "C" IOTOX_MOCK_EXPORT const char *argon2_error_message(int error_code) {
    return error_code == 0 ? "OK" : "mock Argon2 contract mismatch";
}
