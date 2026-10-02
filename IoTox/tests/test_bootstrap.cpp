#include "test_harness.hpp"

#include "iotox/toxcore/bootstrap.hpp"
#include "iotox/toxcore/default_nodes.hpp"

#include <array>
#include <string>

namespace {

constexpr const char *kKey =
    "000102030405060708090A0B0C0D0E0F"
    "101112131415161718191A1B1C1D1E1F";

}  // namespace

IOTOX_TEST("bootstrap endpoint syntax is strict and round-trippable") {
    auto hostname = iotox::toxcore::parse_bootstrap_endpoint(
        std::string("node.example:33445:") + kKey);
    IOTOX_CHECK_MSG(hostname.ok(), hostname.status().message());
    IOTOX_CHECK(hostname.value().host == "node.example");
    IOTOX_CHECK(hostname.value().port == 33445U);
    IOTOX_CHECK(hostname.value().public_key.front() == 0x00U);
    IOTOX_CHECK(hostname.value().public_key.back() == 0x1FU);
    IOTOX_CHECK(iotox::toxcore::format_bootstrap_endpoint(hostname.value()) ==
                std::string("node.example:33445:") + kKey);

    auto ipv6 = iotox::toxcore::parse_bootstrap_endpoint(
        std::string("[2001:db8::7]:443:") + kKey);
    IOTOX_CHECK_MSG(ipv6.ok(), ipv6.status().message());
    IOTOX_CHECK(ipv6.value().host == "2001:db8::7");
    IOTOX_CHECK(ipv6.value().port == 443U);
    IOTOX_CHECK(iotox::toxcore::format_bootstrap_endpoint(ipv6.value()) ==
                std::string("[2001:db8::7]:443:") + kKey);
}

IOTOX_TEST("bootstrap endpoint parser rejects ambiguous or weak forms") {
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint("").ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint("node.example:33445").ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint(
                     std::string("node example:33445:") + kKey)
                     .ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint(
                     std::string("node.example:0:") + kKey)
                     .ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint(
                     std::string("node.example:65536:") + kKey)
                     .ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint(
                     std::string("2001:db8::7:443:") + kKey)
                     .ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint(
                     std::string("[2001:db8::7:443:") + kKey)
                     .ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint(
                     std::string("node.example:33445:") +
                     "000102030405060708090A0B0C0D0E0F")
                     .ok());
    IOTOX_CHECK(!iotox::toxcore::parse_bootstrap_endpoint(
                     std::string("node.example:33445:") +
                     "Z00102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F")
                     .ok());
}


IOTOX_TEST("frozen default Tox node catalog is small explicit and parseable") {
    using namespace iotox::toxcore;
    IOTOX_CHECK(kDefaultNodeSnapshotDate == "2026-08-13");
    IOTOX_CHECK(kDefaultNodeSource == "https://nodes.tox.chat/");

    const auto catalog = default_node_catalog();
    IOTOX_CHECK(catalog.size() == 10U);
    std::size_t bootstrap_count = 0U;
    std::size_t relay_count = 0U;
    for (const DefaultNodeRecord &record : catalog) {
        IOTOX_CHECK(!record.endpoint.host.empty());
        IOTOX_CHECK(record.endpoint.port != 0U);
        IOTOX_CHECK(!record.location.empty());
        bool nonzero_key = false;
        for (const std::uint8_t byte : record.endpoint.public_key) {
            nonzero_key = nonzero_key || byte != 0U;
        }
        IOTOX_CHECK(nonzero_key);
        if (record.role == DefaultNodeRole::bootstrap) {
            ++bootstrap_count;
        } else if (record.role == DefaultNodeRole::tcp_relay) {
            ++relay_count;
        }
    }
    IOTOX_CHECK(bootstrap_count == 6U);
    IOTOX_CHECK(relay_count == 4U);
    IOTOX_CHECK(default_bootstrap_nodes().size() == bootstrap_count);
    IOTOX_CHECK(default_tcp_relays().size() == relay_count);
}
