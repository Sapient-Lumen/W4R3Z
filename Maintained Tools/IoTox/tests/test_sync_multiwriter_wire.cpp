#include "iotox/sync_multiwriter_wire.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <cstdint>

namespace {

iotox::sync::Digest digest(std::uint8_t value) {
    iotox::sync::Digest result{};
    result.fill(value);
    return result;
}

iotox::FileId file_id(std::uint8_t value) {
    iotox::FileId result{};
    result.fill(value);
    return result;
}

iotox::sync::TreeV2Observation observation(std::uint8_t writer,
                                           std::uint64_t generation) {
    return {digest(writer), generation,
            digest(static_cast<std::uint8_t>(writer + 0x40U))};
}

} // namespace

IOTOX_TEST("tree-v2 wire inventory is canonical bounded and frame-safe") {
    using namespace iotox::sync;
    TreeV2InventoryRequest request{"field-notes"};
    auto bytes = encode_tree_v2_inventory_request(request);
    IOTOX_CHECK(bytes.ok() &&
                bytes.value().size() == kTreeV2InventoryRequestBytes);
    auto decoded = decode_tree_v2_inventory_request(bytes.value());
    IOTOX_CHECK(decoded.ok() && decoded.value() == request);

    TreeV2InventoryResult result{
        TreeV2InventoryStatus::available,
        "field-notes",
        {observation(0x11U, 4U), observation(0x22U, 9U)}};
    auto result_bytes = encode_tree_v2_inventory_result(result);
    IOTOX_CHECK(result_bytes.ok());
    auto decoded_result = decode_tree_v2_inventory_result(result_bytes.value());
    IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == result);

    result.frontier.clear();
    IOTOX_CHECK(!encode_tree_v2_inventory_result(result).ok());
    result.status = TreeV2InventoryStatus::absent;
    IOTOX_CHECK(encode_tree_v2_inventory_result(result).ok());

    result.status = TreeV2InventoryStatus::available;
    for (std::uint8_t value = 1U; value <= kTreeV2WireMaximumWriters; ++value)
        result.frontier.push_back(observation(value, value));
    result_bytes = encode_tree_v2_inventory_result(result);
    IOTOX_CHECK(result_bytes.ok());
    IOTOX_CHECK(result_bytes.value().size() <=
                iotox::protocol::kMaxPayloadSize);
    result.frontier.push_back(observation(0x21U, 1U));
    IOTOX_CHECK(!encode_tree_v2_inventory_result(result).ok());
}

IOTOX_TEST("tree-v2 wire object protocol binds kind digest transfer and size") {
    using namespace iotox::sync;
    TreeV2ObjectRequest request{"field-notes", TreeV2ObjectKind::manifest,
                                digest(0x31U), file_id(0x41U)};
    auto bytes = encode_tree_v2_object_request(request);
    IOTOX_CHECK(bytes.ok() &&
                bytes.value().size() == kTreeV2ObjectRequestBytes);
    auto decoded = decode_tree_v2_object_request(bytes.value());
    IOTOX_CHECK(decoded.ok() && decoded.value() == request);

    TreeV2ObjectResult result{TreeV2ObjectStatus::offered, request.kind,
                              request.object, request.transfer_id, 912U};
    auto result_bytes = encode_tree_v2_object_result(result);
    IOTOX_CHECK(result_bytes.ok());
    auto decoded_result = decode_tree_v2_object_result(result_bytes.value());
    IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == result);

    result.kind = TreeV2ObjectKind::file;
    result.object_bytes = 0U;
    IOTOX_CHECK(encode_tree_v2_object_result(result).ok());
    result.kind = TreeV2ObjectKind::manifest;
    IOTOX_CHECK(!encode_tree_v2_object_result(result).ok());
    result.status = TreeV2ObjectStatus::absent;
    IOTOX_CHECK(encode_tree_v2_object_result(result).ok());
}

IOTOX_TEST(
    "tree-v2 wire rejects aliases and freezes request/result envelopes") {
    using namespace iotox::sync;
    auto inventory = make_tree_v2_inventory_request_frame({"field-notes"}, 11U);
    IOTOX_CHECK(inventory.ok());
    IOTOX_CHECK(
        validate_tree_v2_inventory_request_frame(inventory.value()).ok());
    auto inventory_result =
        make_tree_v2_inventory_result_frame({TreeV2InventoryStatus::available,
                                             "field-notes",
                                             {observation(0x11U, 1U)}},
                                            12U, 11U);
    IOTOX_CHECK(inventory_result.ok());
    IOTOX_CHECK(
        validate_tree_v2_inventory_result_frame(inventory_result.value()).ok());

    TreeV2ObjectRequest object{"field-notes", TreeV2ObjectKind::branch_record,
                               digest(0x51U), file_id(0x61U)};
    auto object_frame = make_tree_v2_object_request_frame(object, 21U);
    IOTOX_CHECK(object_frame.ok());
    IOTOX_CHECK(
        validate_tree_v2_object_request_frame(object_frame.value()).ok());
    auto offered = make_tree_v2_object_result_frame(
        {TreeV2ObjectStatus::offered, object.kind, object.object,
         object.transfer_id, 256U},
        22U, 21U);
    IOTOX_CHECK(offered.ok());
    IOTOX_CHECK(validate_tree_v2_object_result_frame(offered.value()).ok());
    auto packet = iotox::protocol::encode(offered.value());
    IOTOX_CHECK(packet.ok());
    auto frame = iotox::protocol::decode(packet.value());
    IOTOX_CHECK(frame.ok() &&
                frame.value().type ==
                    iotox::protocol::MessageType::sync_tree_object_result);

    auto request_bytes = encode_tree_v2_object_request(object);
    IOTOX_CHECK(request_bytes.ok());
    request_bytes.value()[136U] = 1U;
    IOTOX_CHECK(!decode_tree_v2_object_request(request_bytes.value()).ok());
    inventory.value().correlation_id = 1U;
    IOTOX_CHECK(
        !validate_tree_v2_inventory_request_frame(inventory.value()).ok());
    offered.value().correlation_id = 0U;
    IOTOX_CHECK(!validate_tree_v2_object_result_frame(offered.value()).ok());
}
