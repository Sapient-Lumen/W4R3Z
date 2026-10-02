#include "iotox/terminal_profile.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(
    const std::uint8_t *data, std::size_t size) {
    const std::span<const std::uint8_t> bytes{data, size};

    auto profile = iotox::terminal::decode_profile_record(bytes);
    if (profile.ok()) {
        // The public encoder intentionally migrates canonical v1-v4 records to
        // v5, so byte length is not an invariant across the first encode. The
        // semantic profile and the canonical v4 re-encoding are the invariants.
        auto encoded = iotox::terminal::encode_profile_record(profile.value());
        if (!encoded.ok()) {
            __builtin_trap();
        }
        auto decoded = iotox::terminal::decode_profile_record(encoded.value());
        if (!decoded.ok() || decoded.value() != profile.value()) {
            __builtin_trap();
        }
        auto reencoded =
            iotox::terminal::encode_profile_record(decoded.value());
        if (!reencoded.ok() || reencoded.value() != encoded.value()) {
            __builtin_trap();
        }
    }

    auto binding = iotox::terminal::decode_binding_record(bytes);
    if (binding.ok()) {
        auto encoded = iotox::terminal::encode_binding_record(binding.value());
        if (!encoded.ok() || encoded.value().size() != bytes.size()) {
            __builtin_trap();
        }
        auto decoded = iotox::terminal::decode_binding_record(encoded.value());
        if (!decoded.ok() || decoded.value() != binding.value()) {
            __builtin_trap();
        }
    }
    return 0;
}
