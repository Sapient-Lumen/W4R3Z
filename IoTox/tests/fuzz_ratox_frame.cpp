#include "iotox/protocol/ratox.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(
    const std::uint8_t *data, std::size_t size) {
    auto decoded = iotox::protocol::ratox::decode(
        std::span<const std::uint8_t>{data, size});
    if (decoded) {
        auto encoded = iotox::protocol::ratox::encode(decoded.value());
        if (!encoded || encoded.value().size() != size) {
            __builtin_trap();
        }
    }
    return 0;
}
