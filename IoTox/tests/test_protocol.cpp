#include "test_harness.hpp"

#include "iotox/protocol/frame.hpp"

#include <algorithm>
#include <cstdint>
#include <vector>

IOTOX_TEST("IoTox frame round trips through the Tox lossless lane") {
    iotox::protocol::Frame original;
    original.type = iotox::protocol::MessageType::command;
    original.flags = 3;
    original.message_id = 0x0102030405060708ULL;
    original.correlation_id = 99;
    original.sequence = 7;
    original.expiry_unix_ms = 1234567890;
    original.payload = {0, 1, 2, 3, 255};

    auto encoded = iotox::protocol::encode(original);
    IOTOX_CHECK(encoded);
    IOTOX_CHECK(encoded.value().front() == iotox::protocol::kToxLosslessPacketId);
    IOTOX_CHECK(encoded.value().size() == iotox::protocol::kHeaderSize + original.payload.size());

    auto decoded = iotox::protocol::decode(encoded.value());
    IOTOX_CHECK(decoded);
    IOTOX_CHECK(decoded.value().type == original.type);
    IOTOX_CHECK(decoded.value().flags == original.flags);
    IOTOX_CHECK(decoded.value().message_id == original.message_id);
    IOTOX_CHECK(decoded.value().correlation_id == original.correlation_id);
    IOTOX_CHECK(decoded.value().sequence == original.sequence);
    IOTOX_CHECK(decoded.value().expiry_unix_ms == original.expiry_unix_ms);
    IOTOX_CHECK(decoded.value().payload == original.payload);
}

IOTOX_TEST("IoTox frame decoder rejects malformed packets") {
    std::vector<std::uint8_t> short_packet(4, 0);
    IOTOX_CHECK(!iotox::protocol::decode(short_packet));

    iotox::protocol::Frame frame;
    frame.payload = {'o', 'k'};
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded);

    encoded.value()[0] = 0x01U;
    IOTOX_CHECK(!iotox::protocol::decode(encoded.value()));
}

IOTOX_TEST("IoTox frame encoder enforces custom-packet capacity") {
    iotox::protocol::Frame frame;
    frame.payload.resize(iotox::protocol::kMaxPayloadSize + 1U);
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(!encoded);
}

IOTOX_TEST("private route frame allocations are named and round trip") {
    using iotox::protocol::MessageType;
    IOTOX_CHECK(iotox::protocol::is_known_message_type(
        static_cast<std::uint8_t>(MessageType::private_route_inventory)));
    IOTOX_CHECK(iotox::protocol::to_string(
                    MessageType::private_route_inventory) ==
                "private-route-inventory");
    IOTOX_CHECK(iotox::protocol::to_string(
                    MessageType::private_route_member_binding) ==
                "private-route-member-binding");
    iotox::protocol::Frame frame;
    frame.type = MessageType::private_route_member_binding;
    frame.message_id = 7U;
    frame.sequence = 7U;
    frame.payload = {1U, 2U, 3U};
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    auto decoded = iotox::protocol::decode(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value().type == frame.type);
}
