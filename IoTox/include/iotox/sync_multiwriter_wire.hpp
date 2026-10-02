#pragma once

#include "iotox/file_transfer.hpp"
#include "iotox/protocol/frame.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_multiwriter.hpp"

#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <vector>

namespace iotox::sync {

inline constexpr std::uint8_t kTreeV2WireVersion = 1U;
inline constexpr std::size_t kTreeV2WireNamespaceBytes = 64U;
inline constexpr std::size_t kTreeV2WireMaximumWriters = 16U;
inline constexpr std::size_t kTreeV2InventoryRequestBytes = 72U;
inline constexpr std::size_t kTreeV2InventoryResultBaseBytes = 72U;
inline constexpr std::size_t kTreeV2InventoryRecordBytes = 72U;
inline constexpr std::size_t kTreeV2ObjectRequestBytes = 144U;
inline constexpr std::size_t kTreeV2ObjectResultBytes = 88U;

enum class TreeV2InventoryStatus : std::uint8_t {
    available = 1U,
    absent = 2U,
    denied = 3U,
    unavailable = 4U,
};

enum class TreeV2ObjectKind : std::uint8_t {
    branch_record = 1U,
    manifest = 2U,
    file = 3U,
};

enum class TreeV2ObjectStatus : std::uint8_t {
    offered = 1U,
    denied = 2U,
    absent = 3U,
    unavailable = 4U,
};

struct TreeV2InventoryRequest {
    std::string namespace_id;

    [[nodiscard]] bool
    operator==(const TreeV2InventoryRequest &) const = default;
};

struct TreeV2InventoryResult {
    TreeV2InventoryStatus status{TreeV2InventoryStatus::unavailable};
    std::string namespace_id;
    std::vector<TreeV2Observation> frontier;

    [[nodiscard]] bool
    operator==(const TreeV2InventoryResult &) const = default;
};

struct TreeV2ObjectRequest {
    std::string namespace_id;
    TreeV2ObjectKind kind{TreeV2ObjectKind::file};
    Digest object{};
    FileId transfer_id{};

    [[nodiscard]] bool operator==(const TreeV2ObjectRequest &) const = default;
};

struct TreeV2ObjectResult {
    TreeV2ObjectStatus status{TreeV2ObjectStatus::unavailable};
    TreeV2ObjectKind kind{TreeV2ObjectKind::file};
    Digest object{};
    FileId transfer_id{};
    std::uint64_t object_bytes{0U};

    [[nodiscard]] bool operator==(const TreeV2ObjectResult &) const = default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_inventory_request(const TreeV2InventoryRequest &request);
[[nodiscard]] Result<TreeV2InventoryRequest>
decode_tree_v2_inventory_request(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_inventory_result(const TreeV2InventoryResult &result);
[[nodiscard]] Result<TreeV2InventoryResult>
decode_tree_v2_inventory_result(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_object_request(const TreeV2ObjectRequest &request);
[[nodiscard]] Result<TreeV2ObjectRequest>
decode_tree_v2_object_request(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_object_result(const TreeV2ObjectResult &result);
[[nodiscard]] Result<TreeV2ObjectResult>
decode_tree_v2_object_result(std::span<const std::uint8_t> bytes);

[[nodiscard]] Result<protocol::Frame>
make_tree_v2_inventory_request_frame(const TreeV2InventoryRequest &request,
                                     std::uint64_t message_id);
[[nodiscard]] Result<protocol::Frame>
make_tree_v2_inventory_result_frame(const TreeV2InventoryResult &result,
                                    std::uint64_t message_id,
                                    std::uint64_t correlation_id);
[[nodiscard]] Result<protocol::Frame>
make_tree_v2_object_request_frame(const TreeV2ObjectRequest &request,
                                  std::uint64_t message_id);
[[nodiscard]] Result<protocol::Frame>
make_tree_v2_object_result_frame(const TreeV2ObjectResult &result,
                                 std::uint64_t message_id,
                                 std::uint64_t correlation_id);

[[nodiscard]] Status
validate_tree_v2_inventory_request_frame(const protocol::Frame &frame);
[[nodiscard]] Status
validate_tree_v2_inventory_result_frame(const protocol::Frame &frame);
[[nodiscard]] Status
validate_tree_v2_object_request_frame(const protocol::Frame &frame);
[[nodiscard]] Status
validate_tree_v2_object_result_frame(const protocol::Frame &frame);

} // namespace iotox::sync
