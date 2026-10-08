#include "sync_sqlite_process_incarnation.hpp"

#include <cstdint>

int main() {
    const std::uint64_t row_or_wire_value = 0x000000010000002aULL;
    const anonsync::SyncSqliteProcessId forged = row_or_wire_value;
    return forged == row_or_wire_value ? 0 : 1;
}
