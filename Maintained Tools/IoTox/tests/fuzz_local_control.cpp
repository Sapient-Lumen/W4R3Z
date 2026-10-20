#include "iotox/local/control_protocol.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data, std::size_t size) {
    const auto decoded = iotox::local::decode_control_packet(std::span<const std::uint8_t>(data, size));
    if (decoded) {
        const auto encoded = iotox::local::encode_control_packet(decoded.value());
        if (!encoded) {
            __builtin_trap();
        }
        const auto round_trip = iotox::local::decode_control_packet(encoded.value());
        if (!round_trip || !(round_trip.value() == decoded.value())) {
            __builtin_trap();
        }
    }
    return 0;
}
