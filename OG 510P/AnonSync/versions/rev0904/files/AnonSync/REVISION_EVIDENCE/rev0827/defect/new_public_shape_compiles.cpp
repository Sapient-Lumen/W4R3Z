#include "sync_process_incarnation.hpp"

#include <cstdint>
#include <type_traits>

static_assert(!std::is_constructible_v<anonsync::SyncProcessIncarnation,
                                       std::uint64_t>);
static_assert(!std::is_convertible_v<std::uint64_t,
                                     anonsync::SyncProcessIncarnation>);
static_assert(!std::is_trivially_copyable_v<
              anonsync::SyncProcessIncarnation>);
static_assert(std::is_standard_layout_v<anonsync::SyncProcessIncarnation>);

int main() {
    anonsync::SyncProcessIncarnation empty;
    return empty.valid() ? 1 : 0;
}
