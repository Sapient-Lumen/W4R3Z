#pragma once

#include <initializer_list>
#include <string>
#include <string_view>

namespace anonsync {

class Sha256DigestBuilder;

struct SecurityTupleFieldView final {
    std::string_view name;
    std::string_view value;
};

// Streams the exact byte format produced by length_prefixed_security_tuple()
// into an existing SHA-256 owner. This preserves every established v1 digest
// while avoiding a second, potentially large aggregate material string.
void update_sha256_with_length_prefixed_security_tuple(
    Sha256DigestBuilder& digest,
    std::string_view domain,
    std::initializer_list<SecurityTupleFieldView> fields);

[[nodiscard]] std::string sha256_length_prefixed_security_tuple(
    std::string_view domain,
    std::initializer_list<SecurityTupleFieldView> fields);

}  // namespace anonsync
