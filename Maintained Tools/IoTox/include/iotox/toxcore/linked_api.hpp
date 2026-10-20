#pragma once

#include "iotox/toxcore/abi.hpp"

namespace iotox::toxcore {

// Returns the exact function table for a c-toxcore library linked into the
// process. This is populated only in IOTOX_LINKED_TOXCORE builds.
[[nodiscard]] abi::Api linked_toxcore_api() noexcept;

}  // namespace iotox::toxcore
