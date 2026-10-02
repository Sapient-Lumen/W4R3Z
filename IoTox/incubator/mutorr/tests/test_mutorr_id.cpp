#include "test_harness.hpp"

#include "iotox/mutorr/id.hpp"

IOTOX_TEST("mutorr identifiers round trip through canonical lowercase hex") {
    const iotox::mutorr::Id256 original = iotox::mutorr::synthetic_id(42U, 7U);
    const std::string text = original.hex();
    IOTOX_CHECK(text.size() == 64U);

    auto parsed = iotox::mutorr::Id256::from_hex(text);
    IOTOX_CHECK(parsed);
    IOTOX_CHECK(parsed.value() == original);

    auto uppercase = iotox::mutorr::Id256::from_hex(
        "ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789");
    IOTOX_CHECK(uppercase);
    IOTOX_CHECK(uppercase.value().hex() ==
                "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789");
}

IOTOX_TEST("mutorr identifiers reject malformed hex") {
    IOTOX_CHECK(!iotox::mutorr::Id256::from_hex("abcd"));
    IOTOX_CHECK(!iotox::mutorr::Id256::from_hex(
        "zbcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"));
}
