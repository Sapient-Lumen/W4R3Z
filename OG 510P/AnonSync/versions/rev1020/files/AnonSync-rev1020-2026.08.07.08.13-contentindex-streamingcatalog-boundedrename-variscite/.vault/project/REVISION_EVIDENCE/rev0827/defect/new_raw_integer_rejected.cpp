#include "sync_process_incarnation.hpp"

#include <cstdint>

int main() {
    const std::uint64_t row_or_wire_value = 0x000000010000002aULL;
    const anonsync::SyncProcessIncarnation forged = row_or_wire_value;
    return forged.valid() ? 0 : 1;
}
