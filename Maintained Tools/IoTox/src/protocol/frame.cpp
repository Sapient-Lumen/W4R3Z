#include "iotox/protocol/frame.hpp"

#include <array>
#include <limits>

namespace iotox::protocol {
namespace {

void append_u32_be(std::vector<std::uint8_t> &out, std::uint32_t value) {
    for (int shift = 24; shift >= 0; shift -= 8) {
        out.push_back(static_cast<std::uint8_t>((value >> static_cast<unsigned>(shift)) & 0xFFU));
    }
}

void append_u64_be(std::vector<std::uint8_t> &out, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        out.push_back(static_cast<std::uint8_t>((value >> static_cast<unsigned>(shift)) & 0xFFU));
    }
}

std::uint32_t read_u32_be(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint32_t value = 0;
    for (std::size_t index = 0; index < 4; ++index) {
        value = static_cast<std::uint32_t>((value << 8U) | bytes[offset + index]);
    }
    return value;
}

std::uint64_t read_u64_be(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint64_t value = 0;
    for (std::size_t index = 0; index < 8; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

}  // namespace

Result<std::vector<std::uint8_t>> encode(const Frame &frame) {
    if (frame.payload.size() > kMaxPayloadSize) {
        return Status{ErrorCode::protocol_error, "IoTox frame payload exceeds Tox custom-packet capacity"};
    }
    if (!is_known_message_type(static_cast<std::uint8_t>(frame.type))) {
        return Status{ErrorCode::protocol_error, "IoTox frame has an unknown message type"};
    }
    if (frame.payload.size() > static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
        return Status{ErrorCode::protocol_error, "IoTox frame payload length cannot be encoded"};
    }

    std::vector<std::uint8_t> bytes;
    bytes.reserve(kHeaderSize + frame.payload.size());
    bytes.push_back(kToxLosslessPacketId);
    bytes.push_back(frame.major);
    bytes.push_back(frame.minor);
    bytes.push_back(static_cast<std::uint8_t>(frame.type));
    bytes.push_back(frame.flags);
    append_u32_be(bytes, static_cast<std::uint32_t>(frame.payload.size()));
    append_u64_be(bytes, frame.message_id);
    append_u64_be(bytes, frame.correlation_id);
    append_u64_be(bytes, frame.sequence);
    append_u64_be(bytes, frame.expiry_unix_ms);
    bytes.insert(bytes.end(), frame.payload.begin(), frame.payload.end());
    return bytes;
}

Result<Frame> decode(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kHeaderSize) {
        return Status{ErrorCode::protocol_error, "IoTox frame is truncated"};
    }
    if (bytes.size() > kToxMaxCustomPacketSize) {
        return Status{ErrorCode::protocol_error, "IoTox frame exceeds the Tox custom-packet limit"};
    }
    if (bytes[0] != kToxLosslessPacketId) {
        return Status{ErrorCode::protocol_error, "packet is not in the IoTox lossless packet lane"};
    }
    if (!is_known_message_type(bytes[3])) {
        return Status{ErrorCode::protocol_error, "IoTox frame has an unknown message type"};
    }

    const std::uint32_t payload_size = read_u32_be(bytes, 5);
    if (static_cast<std::size_t>(payload_size) != bytes.size() - kHeaderSize) {
        return Status{ErrorCode::protocol_error, "IoTox frame payload length does not match packet length"};
    }

    Frame frame;
    frame.major = bytes[1];
    frame.minor = bytes[2];
    frame.type = static_cast<MessageType>(bytes[3]);
    frame.flags = bytes[4];
    frame.message_id = read_u64_be(bytes, 9);
    frame.correlation_id = read_u64_be(bytes, 17);
    frame.sequence = read_u64_be(bytes, 25);
    frame.expiry_unix_ms = read_u64_be(bytes, 33);
    frame.payload.assign(bytes.begin() + static_cast<std::ptrdiff_t>(kHeaderSize), bytes.end());
    return frame;
}

bool is_known_message_type(std::uint8_t value) noexcept {
    return value >= static_cast<std::uint8_t>(MessageType::hello) &&
           value <=
               static_cast<std::uint8_t>(MessageType::sync_tree_object_result);
}

std::string to_string(MessageType type) {
    switch (type) {
        case MessageType::hello: return "hello";
        case MessageType::capabilities: return "capabilities";
        case MessageType::command: return "command";
        case MessageType::command_result: return "command-result";
        case MessageType::state_snapshot: return "state-snapshot";
        case MessageType::state_event: return "state-event";
        case MessageType::acknowledgement: return "acknowledgement";
        case MessageType::error: return "error";
        case MessageType::pair_request: return "pair-request";
        case MessageType::pair_result: return "pair-result";
        case MessageType::revoke: return "revoke";
        case MessageType::ota_manifest: return "ota-manifest";
        case MessageType::mutorr_head: return "mutorr-head";
        case MessageType::mutorr_inventory: return "mutorr-inventory";
        case MessageType::mutorr_want: return "mutorr-want";
        case MessageType::mutorr_object_offer: return "mutorr-object-offer";
        case MessageType::authority_challenge: return "authority-challenge";
        case MessageType::authority_proof: return "authority-proof";
        case MessageType::route_binding: return "route-binding";
        case MessageType::sync_head_request: return "sync-head-request";
        case MessageType::sync_head_result: return "sync-head-result";
        case MessageType::sync_object_request: return "sync-object-request";
        case MessageType::sync_object_result: return "sync-object-result";
        case MessageType::sync_range_request: return "sync-range-request";
        case MessageType::sync_range_result: return "sync-range-result";
        case MessageType::private_route_inventory:
            return "private-route-inventory";
        case MessageType::private_route_member_binding:
            return "private-route-member-binding";
        case MessageType::sync_content_object_request:
            return "sync-content-object-request";
        case MessageType::sync_content_object_result:
            return "sync-content-object-result";
        case MessageType::sync_content_availability_request:
            return "sync-content-availability-request";
        case MessageType::sync_content_availability_result:
            return "sync-content-availability-result";
        case MessageType::sync_tree_inventory_request:
            return "sync-tree-inventory-request";
        case MessageType::sync_tree_inventory_result:
            return "sync-tree-inventory-result";
        case MessageType::sync_tree_object_request:
            return "sync-tree-object-request";
        case MessageType::sync_tree_object_result:
            return "sync-tree-object-result";
    }
    return "unknown";
}

}  // namespace iotox::protocol
