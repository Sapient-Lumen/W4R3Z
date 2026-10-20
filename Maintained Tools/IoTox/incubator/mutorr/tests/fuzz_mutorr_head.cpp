#include "iotox/mutorr/head.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data, std::size_t size) {
    static_cast<void>(iotox::mutorr::decode_head(std::span<const std::uint8_t>(data, size)));
    return 0;
}
