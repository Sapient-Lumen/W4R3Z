#include "iotox/sync_multiwriter_wire.hpp"

#include <algorithm>

namespace iotox::sync {
namespace {

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

[[nodiscard]] bool
valid_inventory_status(TreeV2InventoryStatus status) noexcept {
    return status == TreeV2InventoryStatus::available ||
           status == TreeV2InventoryStatus::absent ||
           status == TreeV2InventoryStatus::denied ||
           status == TreeV2InventoryStatus::unavailable;
}

[[nodiscard]] bool valid_object_kind(TreeV2ObjectKind kind) noexcept {
    return kind == TreeV2ObjectKind::branch_record ||
           kind == TreeV2ObjectKind::manifest || kind == TreeV2ObjectKind::file;
}

[[nodiscard]] bool valid_object_status(TreeV2ObjectStatus status) noexcept {
    return status == TreeV2ObjectStatus::offered ||
           status == TreeV2ObjectStatus::denied ||
           status == TreeV2ObjectStatus::absent ||
           status == TreeV2ObjectStatus::unavailable;
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index)
        bytes[offset + index] =
            static_cast<std::uint8_t>(value >> ((7U - index) * 8U));
}

[[nodiscard]] std::uint64_t read_u64(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index)
        value = (value << 8U) | bytes[offset + index];
    return value;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> bytes, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
    std::copy(value.begin(), value.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> bytes, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset), Size,
                value.begin());
}

[[nodiscard]] Status write_namespace(std::span<std::uint8_t> bytes,
                                     std::size_t offset,
                                     std::string_view namespace_id) {
    if (!valid_namespace_id(namespace_id) ||
        namespace_id.size() > kTreeV2WireNamespaceBytes ||
        offset > bytes.size() ||
        bytes.size() - offset < kTreeV2WireNamespaceBytes) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 wire namespace is invalid"};
    }
    std::copy(namespace_id.begin(), namespace_id.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));
    return Status::success();
}

[[nodiscard]] Result<std::string>
read_namespace(std::span<const std::uint8_t> bytes, std::size_t offset,
               std::size_t length) {
    if (length == 0U || length > kTreeV2WireNamespaceBytes ||
        offset > bytes.size() ||
        bytes.size() - offset < kTreeV2WireNamespaceBytes ||
        !all_zero(bytes.subspan(offset + length,
                                kTreeV2WireNamespaceBytes - length))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 wire namespace slot is invalid"};
    }
    std::string result(reinterpret_cast<const char *>(bytes.data() + offset),
                       length);
    if (!valid_namespace_id(result)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 wire namespace grammar is invalid"};
    }
    return result;
}

[[nodiscard]] Status validate_request_frame(const protocol::Frame &frame,
                                            protocol::MessageType type) {
    if (frame.type != type || frame.major != protocol::kProtocolMajor ||
        frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
        frame.message_id == 0U || frame.correlation_id != 0U ||
        frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 request frame envelope is invalid"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_result_frame(const protocol::Frame &frame,
                                           protocol::MessageType type) {
    if (frame.type != type || frame.major != protocol::kProtocolMajor ||
        frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
        frame.message_id == 0U || frame.correlation_id == 0U ||
        frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 result frame envelope is invalid"};
    }
    return Status::success();
}

[[nodiscard]] protocol::Frame request_frame(protocol::MessageType type,
                                            std::uint64_t message_id,
                                            std::vector<std::uint8_t> payload) {
    protocol::Frame frame;
    frame.type = type;
    frame.message_id = message_id;
    frame.payload = std::move(payload);
    return frame;
}

[[nodiscard]] protocol::Frame result_frame(protocol::MessageType type,
                                           std::uint64_t message_id,
                                           std::uint64_t correlation_id,
                                           std::vector<std::uint8_t> payload) {
    protocol::Frame frame;
    frame.type = type;
    frame.message_id = message_id;
    frame.correlation_id = correlation_id;
    frame.payload = std::move(payload);
    return frame;
}

} // namespace

Result<std::vector<std::uint8_t>>
encode_tree_v2_inventory_request(const TreeV2InventoryRequest &request) {
    std::vector<std::uint8_t> bytes(kTreeV2InventoryRequestBytes, 0U);
    bytes[0U] = kTreeV2WireVersion;
    bytes[1U] = static_cast<std::uint8_t>(request.namespace_id.size());
    const Status encoded = write_namespace(bytes, 8U, request.namespace_id);
    if (!encoded.ok()) return encoded;
    return bytes;
}

Result<TreeV2InventoryRequest>
decode_tree_v2_inventory_request(std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kTreeV2InventoryRequestBytes ||
        bytes[0U] != kTreeV2WireVersion || !all_zero(bytes.subspan(2U, 6U))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 inventory request is not canonical"};
    }
    auto namespace_id = read_namespace(bytes, 8U, bytes[1U]);
    if (!namespace_id) return namespace_id.status();
    return TreeV2InventoryRequest{std::move(namespace_id).value()};
}

Result<std::vector<std::uint8_t>>
encode_tree_v2_inventory_result(const TreeV2InventoryResult &result) {
    const bool available = result.status == TreeV2InventoryStatus::available;
    if (!valid_inventory_status(result.status) ||
        result.frontier.size() > kTreeV2WireMaximumWriters ||
        (available != !result.frontier.empty())) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 inventory status and frontier disagree"};
    }
    for (std::size_t index = 0U; index < result.frontier.size(); ++index) {
        const TreeV2Observation &observation = result.frontier[index];
        if (all_zero(observation.writer) || observation.generation == 0U ||
            all_zero(observation.record) ||
            (index != 0U &&
             !(result.frontier[index - 1U].writer < observation.writer))) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 inventory frontier is not canonical"};
        }
    }
    std::vector<std::uint8_t> bytes(kTreeV2InventoryResultBaseBytes +
                                        result.frontier.size() *
                                            kTreeV2InventoryRecordBytes,
                                    0U);
    bytes[0U] = kTreeV2WireVersion;
    bytes[1U] = static_cast<std::uint8_t>(result.status);
    bytes[2U] = static_cast<std::uint8_t>(result.namespace_id.size());
    bytes[3U] = static_cast<std::uint8_t>(result.frontier.size());
    const Status encoded = write_namespace(bytes, 8U, result.namespace_id);
    if (!encoded.ok()) return encoded;
    std::size_t offset = kTreeV2InventoryResultBaseBytes;
    for (const TreeV2Observation &observation : result.frontier) {
        write_array(bytes, offset, observation.writer);
        write_u64(bytes, offset + 32U, observation.generation);
        write_array(bytes, offset + 40U, observation.record);
        offset += kTreeV2InventoryRecordBytes;
    }
    return bytes;
}

Result<TreeV2InventoryResult>
decode_tree_v2_inventory_result(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kTreeV2InventoryResultBaseBytes ||
        bytes[0U] != kTreeV2WireVersion || !all_zero(bytes.subspan(4U, 4U))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 inventory result header is invalid"};
    }
    const std::size_t count = bytes[3U];
    if (count > kTreeV2WireMaximumWriters ||
        bytes.size() != kTreeV2InventoryResultBaseBytes +
                            count * kTreeV2InventoryRecordBytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 inventory result length is invalid"};
    }
    TreeV2InventoryResult result;
    result.status = static_cast<TreeV2InventoryStatus>(bytes[1U]);
    auto namespace_id = read_namespace(bytes, 8U, bytes[2U]);
    if (!namespace_id) return namespace_id.status();
    result.namespace_id = std::move(namespace_id).value();
    result.frontier.reserve(count);
    std::size_t offset = kTreeV2InventoryResultBaseBytes;
    for (std::size_t index = 0U; index < count; ++index) {
        TreeV2Observation observation;
        read_array(bytes, offset, observation.writer);
        observation.generation = read_u64(bytes, offset + 32U);
        read_array(bytes, offset + 40U, observation.record);
        result.frontier.push_back(observation);
        offset += kTreeV2InventoryRecordBytes;
    }
    auto canonical = encode_tree_v2_inventory_result(result);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 inventory result is not canonical"};
    }
    return result;
}

Result<std::vector<std::uint8_t>>
encode_tree_v2_object_request(const TreeV2ObjectRequest &request) {
    if (!valid_object_kind(request.kind) || all_zero(request.object) ||
        all_zero(request.transfer_id)) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 object request identity is invalid"};
    }
    std::vector<std::uint8_t> bytes(kTreeV2ObjectRequestBytes, 0U);
    bytes[0U] = kTreeV2WireVersion;
    bytes[1U] = static_cast<std::uint8_t>(request.kind);
    bytes[2U] = static_cast<std::uint8_t>(request.namespace_id.size());
    write_array(bytes, 8U, request.object);
    write_array(bytes, 40U, request.transfer_id);
    const Status encoded = write_namespace(bytes, 72U, request.namespace_id);
    if (!encoded.ok()) return encoded;
    return bytes;
}

Result<TreeV2ObjectRequest>
decode_tree_v2_object_request(std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kTreeV2ObjectRequestBytes ||
        bytes[0U] != kTreeV2WireVersion || !all_zero(bytes.subspan(3U, 5U)) ||
        !all_zero(bytes.subspan(136U, 8U))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object request is not canonical"};
    }
    TreeV2ObjectRequest request;
    request.kind = static_cast<TreeV2ObjectKind>(bytes[1U]);
    auto namespace_id = read_namespace(bytes, 72U, bytes[2U]);
    if (!namespace_id) return namespace_id.status();
    request.namespace_id = std::move(namespace_id).value();
    read_array(bytes, 8U, request.object);
    read_array(bytes, 40U, request.transfer_id);
    if (!valid_object_kind(request.kind) || all_zero(request.object) ||
        all_zero(request.transfer_id)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object request identity is invalid"};
    }
    return request;
}

Result<std::vector<std::uint8_t>>
encode_tree_v2_object_result(const TreeV2ObjectResult &result) {
    if (!valid_object_status(result.status) ||
        !valid_object_kind(result.kind) || all_zero(result.object) ||
        all_zero(result.transfer_id) ||
        (result.status != TreeV2ObjectStatus::offered &&
         result.object_bytes != 0U) ||
        (result.status == TreeV2ObjectStatus::offered &&
         result.kind != TreeV2ObjectKind::file && result.object_bytes == 0U)) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 object result identity or size is invalid"};
    }
    std::vector<std::uint8_t> bytes(kTreeV2ObjectResultBytes, 0U);
    bytes[0U] = kTreeV2WireVersion;
    bytes[1U] = static_cast<std::uint8_t>(result.status);
    bytes[2U] = static_cast<std::uint8_t>(result.kind);
    write_array(bytes, 8U, result.object);
    write_array(bytes, 40U, result.transfer_id);
    write_u64(bytes, 72U, result.object_bytes);
    return bytes;
}

Result<TreeV2ObjectResult>
decode_tree_v2_object_result(std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kTreeV2ObjectResultBytes ||
        bytes[0U] != kTreeV2WireVersion || !all_zero(bytes.subspan(3U, 5U)) ||
        !all_zero(bytes.subspan(80U, 8U))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object result is not canonical"};
    }
    TreeV2ObjectResult result;
    result.status = static_cast<TreeV2ObjectStatus>(bytes[1U]);
    result.kind = static_cast<TreeV2ObjectKind>(bytes[2U]);
    read_array(bytes, 8U, result.object);
    read_array(bytes, 40U, result.transfer_id);
    result.object_bytes = read_u64(bytes, 72U);
    auto canonical = encode_tree_v2_object_result(result);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object result is not canonical"};
    }
    return result;
}

Result<protocol::Frame>
make_tree_v2_inventory_request_frame(const TreeV2InventoryRequest &request,
                                     std::uint64_t message_id) {
    if (message_id == 0U)
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 message id is zero"};
    auto payload = encode_tree_v2_inventory_request(request);
    if (!payload) return payload.status();
    return request_frame(protocol::MessageType::sync_tree_inventory_request,
                         message_id, std::move(payload).value());
}

Result<protocol::Frame>
make_tree_v2_inventory_result_frame(const TreeV2InventoryResult &result,
                                    std::uint64_t message_id,
                                    std::uint64_t correlation_id) {
    if (message_id == 0U || correlation_id == 0U)
        return Status{ErrorCode::invalid_argument, "tree-v2 frame id is zero"};
    auto payload = encode_tree_v2_inventory_result(result);
    if (!payload) return payload.status();
    return result_frame(protocol::MessageType::sync_tree_inventory_result,
                        message_id, correlation_id, std::move(payload).value());
}

Result<protocol::Frame>
make_tree_v2_object_request_frame(const TreeV2ObjectRequest &request,
                                  std::uint64_t message_id) {
    if (message_id == 0U)
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 message id is zero"};
    auto payload = encode_tree_v2_object_request(request);
    if (!payload) return payload.status();
    return request_frame(protocol::MessageType::sync_tree_object_request,
                         message_id, std::move(payload).value());
}

Result<protocol::Frame>
make_tree_v2_object_result_frame(const TreeV2ObjectResult &result,
                                 std::uint64_t message_id,
                                 std::uint64_t correlation_id) {
    if (message_id == 0U || correlation_id == 0U)
        return Status{ErrorCode::invalid_argument, "tree-v2 frame id is zero"};
    auto payload = encode_tree_v2_object_result(result);
    if (!payload) return payload.status();
    return result_frame(protocol::MessageType::sync_tree_object_result,
                        message_id, correlation_id, std::move(payload).value());
}

Status validate_tree_v2_inventory_request_frame(const protocol::Frame &frame) {
    const Status envelope = validate_request_frame(
        frame, protocol::MessageType::sync_tree_inventory_request);
    if (!envelope.ok()) return envelope;
    auto decoded = decode_tree_v2_inventory_request(frame.payload);
    return decoded ? Status::success() : decoded.status();
}

Status validate_tree_v2_inventory_result_frame(const protocol::Frame &frame) {
    const Status envelope = validate_result_frame(
        frame, protocol::MessageType::sync_tree_inventory_result);
    if (!envelope.ok()) return envelope;
    auto decoded = decode_tree_v2_inventory_result(frame.payload);
    return decoded ? Status::success() : decoded.status();
}

Status validate_tree_v2_object_request_frame(const protocol::Frame &frame) {
    const Status envelope = validate_request_frame(
        frame, protocol::MessageType::sync_tree_object_request);
    if (!envelope.ok()) return envelope;
    auto decoded = decode_tree_v2_object_request(frame.payload);
    return decoded ? Status::success() : decoded.status();
}

Status validate_tree_v2_object_result_frame(const protocol::Frame &frame) {
    const Status envelope = validate_result_frame(
        frame, protocol::MessageType::sync_tree_object_result);
    if (!envelope.ok()) return envelope;
    auto decoded = decode_tree_v2_object_result(frame.payload);
    return decoded ? Status::success() : decoded.status();
}

} // namespace iotox::sync
