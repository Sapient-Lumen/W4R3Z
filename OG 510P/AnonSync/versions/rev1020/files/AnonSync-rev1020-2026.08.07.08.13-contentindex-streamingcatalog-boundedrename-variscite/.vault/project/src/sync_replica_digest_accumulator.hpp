#pragma once

#include <string>
#include <string_view>

namespace anonsync {

// Canonical 256-bit commutative accumulator used only with separately bound
// set cardinality. Each element first receives a domain-separated SHA-256
// digest; digests are then added modulo 2^256. The resulting set witness is
// deterministic under insertion order and supports exact O(1) add/remove
// updates without retaining the complete set in memory.
// It is an unkeyed structural witness, not authentication authority.
[[nodiscard]] std::string sync_replica_digest_accumulator_zero();
[[nodiscard]] std::string sync_replica_digest_accumulator_add_or_throw(
    std::string_view accumulator_sha256,
    std::string_view element_sha256);
[[nodiscard]] std::string sync_replica_digest_accumulator_subtract_or_throw(
    std::string_view accumulator_sha256,
    std::string_view element_sha256);

}  // namespace anonsync
