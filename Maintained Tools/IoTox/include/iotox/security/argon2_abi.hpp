#pragma once

#include <cstddef>
#include <cstdint>
#include <type_traits>

#if __has_include(<argon2.h>) && !defined(IOTOX_FORCE_BUILTIN_ARGON2_ABI)
#include <argon2.h>
#define IOTOX_HAS_OFFICIAL_ARGON2_HEADER 1
#else
extern "C" {

using allocate_fptr = int (*)(std::uint8_t **memory, std::size_t bytes_to_allocate);
using deallocate_fptr = void (*)(std::uint8_t *memory, std::size_t bytes_to_allocate);

// Exact public ABI layout from the Argon2 reference implementation's
// include/argon2.h. This fallback is isolated so ordinary IoTox code never
// needs to reproduce or depend on the external C header.
typedef struct Argon2_Context {
    std::uint8_t *out;
    std::uint32_t outlen;
    std::uint8_t *pwd;
    std::uint32_t pwdlen;
    std::uint8_t *salt;
    std::uint32_t saltlen;
    std::uint8_t *secret;
    std::uint32_t secretlen;
    std::uint8_t *ad;
    std::uint32_t adlen;
    std::uint32_t t_cost;
    std::uint32_t m_cost;
    std::uint32_t lanes;
    std::uint32_t threads;
    std::uint32_t version;
    allocate_fptr allocate_cbk;
    deallocate_fptr free_cbk;
    std::uint32_t flags;
} argon2_context;

int argon2id_ctx(argon2_context *context);
const char *argon2_error_message(int error_code);

}  // extern "C"
#define IOTOX_HAS_OFFICIAL_ARGON2_HEADER 0
#endif

namespace iotox::security::argon2_abi {

using Context = ::argon2_context;
using IdContext = decltype(&::argon2id_ctx);
using ErrorMessage = decltype(&::argon2_error_message);

inline constexpr std::uint32_t kVersion13 = 0x13U;
inline constexpr std::uint32_t kFlagClearPassword = 1U << 0U;
inline constexpr int kOk = 0;

struct Api {
    IdContext id_context{nullptr};
    ErrorMessage error_message{nullptr};
};

static_assert(std::is_pointer_v<IdContext>);
static_assert(std::is_pointer_v<ErrorMessage>);
static_assert(std::is_standard_layout_v<Context>);

}  // namespace iotox::security::argon2_abi
