#include "sync_process_incarnation.hpp"

#include <bit>
#include <cstdint>

int main() {
    const std::uint64_t raw = 0x0000000100000001ULL;
    const auto forged =
        std::bit_cast<anonsync::SyncProcessIncarnation>(raw);
    return forged.valid() ? 0 : 1;
}
