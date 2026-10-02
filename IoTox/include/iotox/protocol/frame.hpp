#pragma once

#include "iotox/status.hpp"

#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <vector>

namespace iotox::protocol {

inline constexpr std::uint8_t kToxLosslessPacketId = 0xA0U;
inline constexpr std::uint8_t kProtocolMajor = 1U;
inline constexpr std::uint8_t kProtocolMinor = 0U;
inline constexpr std::size_t kToxMaxCustomPacketSize = 1373U;
inline constexpr std::size_t kHeaderSize = 41U;
inline constexpr std::size_t kMaxPayloadSize = kToxMaxCustomPacketSize - kHeaderSize;

enum class MessageType : std::uint8_t {
    hello = 1,
    capabilities = 2,
    command = 3,
    command_result = 4,
    state_snapshot = 5,
    state_event = 6,
    acknowledgement = 7,
    error = 8,
    pair_request = 9,
    pair_result = 10,
    revoke = 11,
    ota_manifest = 12,
    mutorr_head = 13,
    mutorr_inventory = 14,
    mutorr_want = 15,
    mutorr_object_offer = 16,
    authority_challenge = 17,
    authority_proof = 18,
    route_binding = 19,
    sync_head_request = 20,
    sync_head_result = 21,
    sync_object_request = 22,
    sync_object_result = 23,
    sync_range_request = 24,
    sync_range_result = 25,
    private_route_inventory = 26,
    private_route_member_binding = 27,
    sync_content_object_request = 28,
    sync_content_object_result = 29,
    sync_content_availability_request = 30,
    sync_content_availability_result = 31,
    sync_tree_inventory_request = 32,
    sync_tree_inventory_result = 33,
    sync_tree_object_request = 34,
    sync_tree_object_result = 35,
};

struct Frame {
    std::uint8_t major{kProtocolMajor};
    std::uint8_t minor{kProtocolMinor};
    MessageType type{MessageType::hello};
    std::uint8_t flags{0};
    std::uint64_t message_id{0};
    std::uint64_t correlation_id{0};
    std::uint64_t sequence{0};
    std::uint64_t expiry_unix_ms{0};
    std::vector<std::uint8_t> payload;
};

[[nodiscard]] Result<std::vector<std::uint8_t>> encode(const Frame &frame);
[[nodiscard]] Result<Frame> decode(std::span<const std::uint8_t> bytes);
[[nodiscard]] bool is_known_message_type(std::uint8_t value) noexcept;
[[nodiscard]] std::string to_string(MessageType type);

}  // namespace iotox::protocol
