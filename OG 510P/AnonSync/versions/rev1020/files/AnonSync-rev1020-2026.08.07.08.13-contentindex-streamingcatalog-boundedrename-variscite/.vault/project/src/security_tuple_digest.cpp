#include "security_tuple_digest.hpp"

#include "sha256_digest.hpp"

#include <array>
#include <charconv>
#include <stdexcept>
#include <system_error>

namespace anonsync {
namespace {

constexpr std::string_view kTuplePrefix =
    "anonsync-length-prefixed-tuple-v1";

void update_framed_component(
    Sha256DigestBuilder& digest,
    std::string_view component) {
    std::array<char, 32> decimal{};
    const auto converted = std::to_chars(
        decimal.data(), decimal.data() + decimal.size(), component.size());
    if (converted.ec != std::errc{}) {
        throw std::runtime_error(
            "security tuple digest component length formatting failed");
    }
    digest.update(std::string_view(
        decimal.data(),
        static_cast<std::size_t>(converted.ptr - decimal.data())));
    digest.update(":");
    digest.update(component);
}

}  // namespace

void update_sha256_with_length_prefixed_security_tuple(
    Sha256DigestBuilder& digest,
    std::string_view domain,
    std::initializer_list<SecurityTupleFieldView> fields) {
    digest.update(kTuplePrefix);
    update_framed_component(digest, domain);
    for (const SecurityTupleFieldView& field : fields) {
        update_framed_component(digest, field.name);
        update_framed_component(digest, field.value);
    }
}

std::string sha256_length_prefixed_security_tuple(
    std::string_view domain,
    std::initializer_list<SecurityTupleFieldView> fields) {
    Sha256DigestBuilder digest;
    update_sha256_with_length_prefixed_security_tuple(digest, domain, fields);
    return digest.finish_hex();
}

}  // namespace anonsync
