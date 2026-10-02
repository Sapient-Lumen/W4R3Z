#include "iotox/sync_wire.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <utility>

namespace iotox::sync {
namespace {

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

bool valid_kind(SyncObjectKind kind) noexcept {
  return kind == SyncObjectKind::artifact ||
         kind == SyncObjectKind::manifest;
}

bool valid_head_status(SyncHeadResultStatus status) noexcept {
  return status == SyncHeadResultStatus::available ||
         status == SyncHeadResultStatus::absent ||
         status == SyncHeadResultStatus::denied ||
         status == SyncHeadResultStatus::unavailable;
}

bool valid_object_status(SyncObjectResultStatus status) noexcept {
  return status == SyncObjectResultStatus::offered ||
         status == SyncObjectResultStatus::denied ||
         status == SyncObjectResultStatus::stale_head ||
         status == SyncObjectResultStatus::object_absent ||
         status == SyncObjectResultStatus::unavailable;
}

bool valid_range_status(SyncRangeResultStatus status) noexcept {
  return status == SyncRangeResultStatus::offered ||
         status == SyncRangeResultStatus::denied ||
         status == SyncRangeResultStatus::stale_head ||
         status == SyncRangeResultStatus::artifact_absent ||
         status == SyncRangeResultStatus::unavailable;
}

void write_u16(std::span<std::uint8_t> output, std::size_t offset,
               std::uint16_t value) {
  output[offset] = static_cast<std::uint8_t>(value >> 8U);
  output[offset + 1U] = static_cast<std::uint8_t>(value);
}

std::uint16_t read_u16(std::span<const std::uint8_t> input,
                       std::size_t offset) {
  return static_cast<std::uint16_t>(
      (static_cast<std::uint16_t>(input[offset]) << 8U) |
      static_cast<std::uint16_t>(input[offset + 1U]));
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output[offset + index] = static_cast<std::uint8_t>(
        value >> ((7U - index) * 8U));
  }
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
  std::uint64_t value = 0U;
  for (std::size_t index = 0U; index < 8U; ++index) {
    value = (value << 8U) | input[offset + index];
  }
  return value;
}

Status validate_ranges(std::span<const SyncRangeRecord> ranges) {
  if (ranges.empty() || ranges.size() > kSyncMaximumRanges) {
    return Status{ErrorCode::invalid_argument,
                  "sync range request count is invalid"};
  }
  std::uint64_t previous_end = 0U;
  bool first = true;
  std::uint64_t total = 0U;
  for (const SyncRangeRecord &range : ranges) {
    if (range.length == 0U ||
        range.length > std::numeric_limits<std::uint64_t>::max() -
                           range.offset ||
        (!first && range.offset <= previous_end) ||
        range.length > std::numeric_limits<std::uint64_t>::max() - total) {
      return Status{ErrorCode::invalid_argument,
                    "sync ranges are not canonical disjoint ranges"};
    }
    previous_end = range.offset + range.length;
    total += range.length;
    first = false;
  }
  return Status::success();
}

Status validate_head_shape(const SignedHead &head) {
  if (!valid_namespace_id(head.namespace_id) || all_zero(head.writer) ||
      (head.engine != Engine::range_v1 &&
       head.engine != Engine::content_v2 &&
       head.engine != Engine::treepack_v1) ||
      head.generation == 0U || all_zero(head.artifact) ||
      all_zero(head.manifest) || head.artifact_bytes == 0U ||
      head.manifest_bytes == 0U || all_zero(head.signature) ||
      (head.generation == 1U && !all_zero(head.parent)) ||
      (head.generation != 1U && all_zero(head.parent))) {
    return Status{ErrorCode::invalid_argument,
                  "sync wire HEAD has an invalid structural field"};
  }
  return Status::success();
}

Status encode_namespace(std::span<std::uint8_t> output, std::size_t offset,
                        std::string_view namespace_id) {
  if (!valid_namespace_id(namespace_id) ||
      namespace_id.size() > kSyncWireNamespaceBytes ||
      offset > output.size() ||
      output.size() - offset < kSyncWireNamespaceBytes) {
    return Status{ErrorCode::invalid_argument,
                  "sync wire namespace is invalid"};
  }
  std::copy(namespace_id.begin(), namespace_id.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset));
  return Status::success();
}

Result<std::string> decode_namespace(std::span<const std::uint8_t> input,
                                     std::size_t offset,
                                     std::size_t length) {
  if (length == 0U || length > kSyncWireNamespaceBytes ||
      offset > input.size() ||
      input.size() - offset < kSyncWireNamespaceBytes ||
      !all_zero(input.subspan(offset + length,
                              kSyncWireNamespaceBytes - length))) {
    return Status{ErrorCode::protocol_error,
                  "sync wire namespace slot is invalid"};
  }
  std::string value(
      reinterpret_cast<const char *>(input.data() + offset), length);
  if (!valid_namespace_id(value)) {
    return Status{ErrorCode::protocol_error,
                  "sync wire namespace grammar is invalid"};
  }
  return value;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> output, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
  std::copy(value.begin(), value.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> input, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
  std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset), Size,
              value.begin());
}

Status validate_request_envelope(const protocol::Frame &frame,
                                 protocol::MessageType expected) {
  if (frame.type != expected || frame.major != protocol::kProtocolMajor ||
      frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
      frame.message_id == 0U || frame.correlation_id != 0U ||
      frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync request frame envelope is invalid"};
  }
  return Status::success();
}

Status validate_result_envelope(const protocol::Frame &frame,
                                protocol::MessageType expected) {
  if (frame.type != expected || frame.major != protocol::kProtocolMajor ||
      frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
      frame.message_id == 0U || frame.correlation_id == 0U ||
      frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync result frame envelope is invalid"};
  }
  return Status::success();
}

protocol::Frame request_frame(protocol::MessageType type,
                              std::uint64_t message_id,
                              std::vector<std::uint8_t> payload) {
  protocol::Frame frame;
  frame.type = type;
  frame.message_id = message_id;
  frame.payload = std::move(payload);
  return frame;
}

protocol::Frame result_frame(protocol::MessageType type,
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
encode_sync_head_request(const SyncHeadRequest &request) {
  std::vector<std::uint8_t> output(kSyncHeadRequestBytes, 0U);
  output[0U] = kSyncWireVersion;
  output[1U] = static_cast<std::uint8_t>(request.namespace_id.size());
  const Status encoded = encode_namespace(output, 8U, request.namespace_id);
  if (!encoded.ok()) return encoded;
  return output;
}

Result<SyncHeadRequest>
decode_sync_head_request(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncHeadRequestBytes ||
      bytes[0U] != kSyncWireVersion || !all_zero(bytes.subspan(2U, 6U))) {
    return Status{ErrorCode::protocol_error,
                  "sync HEAD request is not canonical"};
  }
  auto namespace_id = decode_namespace(bytes, 8U, bytes[1U]);
  if (!namespace_id) return namespace_id.status();
  return SyncHeadRequest{std::move(namespace_id).value()};
}

Result<std::vector<std::uint8_t>>
encode_sync_head_result(const SyncHeadResult &result) {
  if (!valid_head_status(result.status) ||
      ((result.status == SyncHeadResultStatus::available) !=
       result.head.has_value())) {
    return Status{ErrorCode::invalid_argument,
                  "sync HEAD result status and body disagree"};
  }
  std::vector<std::uint8_t> output(kSyncHeadResultBytes, 0U);
  output[0U] = kSyncWireVersion;
  output[1U] = static_cast<std::uint8_t>(result.status);
  if (result.head) {
    const Status valid = validate_head_shape(*result.head);
    if (!valid.ok()) return valid;
    auto encoded = encode_signed_head(*result.head);
    if (!encoded) return encoded.status();
    std::copy(encoded.value().begin(), encoded.value().end(),
              output.begin() + 8);
  }
  return output;
}

Result<SyncHeadResult>
decode_sync_head_result(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncHeadResultBytes ||
      bytes[0U] != kSyncWireVersion || !all_zero(bytes.subspan(2U, 6U))) {
    return Status{ErrorCode::protocol_error,
                  "sync HEAD result is not canonical"};
  }
  SyncHeadResult result;
  result.status = static_cast<SyncHeadResultStatus>(bytes[1U]);
  if (!valid_head_status(result.status)) {
    return Status{ErrorCode::protocol_error,
                  "sync HEAD result status is unknown"};
  }
  const auto head_bytes = bytes.subspan(8U, kSignedHeadBytes);
  if (result.status == SyncHeadResultStatus::available) {
    auto head = decode_signed_head(head_bytes);
    if (!head) return head.status();
    const Status valid = validate_head_shape(head.value());
    if (!valid.ok()) {
      return Status{ErrorCode::protocol_error, valid.message()};
    }
    result.head.emplace(std::move(head).value());
  } else if (!all_zero(head_bytes)) {
    return Status{ErrorCode::protocol_error,
                  "sync HEAD denial carries unexpected content"};
  }
  return result;
}

Result<std::vector<std::uint8_t>>
encode_sync_object_request(const SyncObjectRequest &request) {
  if (!valid_namespace_id(request.namespace_id) ||
      !valid_kind(request.kind) || all_zero(request.head_record) ||
      all_zero(request.transfer_id)) {
    return Status{ErrorCode::invalid_argument,
                  "sync object request identity is invalid"};
  }
  std::vector<std::uint8_t> output(kSyncObjectRequestBytes, 0U);
  output[0U] = kSyncWireVersion;
  output[1U] = static_cast<std::uint8_t>(request.kind);
  output[2U] = static_cast<std::uint8_t>(request.namespace_id.size());
  write_array(output, 8U, request.head_record);
  write_array(output, 40U, request.transfer_id);
  const Status encoded = encode_namespace(output, 72U, request.namespace_id);
  if (!encoded.ok()) return encoded;
  return output;
}

Result<SyncObjectRequest>
decode_sync_object_request(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncObjectRequestBytes ||
      bytes[0U] != kSyncWireVersion || !all_zero(bytes.subspan(3U, 5U))) {
    return Status{ErrorCode::protocol_error,
                  "sync object request is not canonical"};
  }
  SyncObjectRequest request;
  request.kind = static_cast<SyncObjectKind>(bytes[1U]);
  auto namespace_id = decode_namespace(bytes, 72U, bytes[2U]);
  if (!namespace_id) return namespace_id.status();
  request.namespace_id = std::move(namespace_id).value();
  read_array(bytes, 8U, request.head_record);
  read_array(bytes, 40U, request.transfer_id);
  if (!valid_kind(request.kind) || all_zero(request.head_record) ||
      all_zero(request.transfer_id)) {
    return Status{ErrorCode::protocol_error,
                  "sync object request identity is invalid"};
  }
  return request;
}

Result<std::vector<std::uint8_t>>
encode_sync_object_result(const SyncObjectResult &result) {
  if (!valid_object_status(result.status) || !valid_kind(result.kind) ||
      all_zero(result.head_record) || all_zero(result.transfer_id)) {
    return Status{ErrorCode::invalid_argument,
                  "sync object result identity is invalid"};
  }
  std::vector<std::uint8_t> output(kSyncObjectResultBytes, 0U);
  output[0U] = kSyncWireVersion;
  output[1U] = static_cast<std::uint8_t>(result.status);
  output[2U] = static_cast<std::uint8_t>(result.kind);
  write_array(output, 8U, result.head_record);
  write_array(output, 40U, result.transfer_id);
  return output;
}

Result<SyncObjectResult>
decode_sync_object_result(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncObjectResultBytes ||
      bytes[0U] != kSyncWireVersion || !all_zero(bytes.subspan(3U, 5U))) {
    return Status{ErrorCode::protocol_error,
                  "sync object result is not canonical"};
  }
  SyncObjectResult result;
  result.status = static_cast<SyncObjectResultStatus>(bytes[1U]);
  result.kind = static_cast<SyncObjectKind>(bytes[2U]);
  read_array(bytes, 8U, result.head_record);
  read_array(bytes, 40U, result.transfer_id);
  if (!valid_object_status(result.status) || !valid_kind(result.kind) ||
      all_zero(result.head_record) || all_zero(result.transfer_id)) {
    return Status{ErrorCode::protocol_error,
                  "sync object result identity is invalid"};
  }
  return result;
}

Result<std::vector<std::uint8_t>>
encode_sync_range_request(const SyncRangeRequest &request) {
  const Status ranges = validate_ranges(request.ranges);
  if (!valid_namespace_id(request.namespace_id) ||
      all_zero(request.head_record) || all_zero(request.transfer_id) ||
      !ranges.ok()) {
    return Status{ErrorCode::invalid_argument,
                  "sync range request identity or ranges are invalid"};
  }
  const std::size_t bytes = kSyncRangeRequestBaseBytes +
      request.ranges.size() * kSyncRangeRecordBytes;
  if (bytes > protocol::kMaxPayloadSize) {
    return Status{ErrorCode::resource_exhausted,
                  "sync range request exceeds frame capacity"};
  }
  std::vector<std::uint8_t> output(bytes, 0U);
  output[0U] = kSyncWireVersion;
  output[1U] = static_cast<std::uint8_t>(request.namespace_id.size());
  write_u16(output, 2U, static_cast<std::uint16_t>(request.ranges.size()));
  write_array(output, 8U, request.head_record);
  write_array(output, 40U, request.transfer_id);
  const Status encoded = encode_namespace(output, 72U, request.namespace_id);
  if (!encoded.ok()) return encoded;
  std::size_t offset = kSyncRangeRequestBaseBytes;
  for (const SyncRangeRecord &range : request.ranges) {
    write_u64(output, offset, range.offset);
    write_u64(output, offset + 8U, range.length);
    offset += kSyncRangeRecordBytes;
  }
  return output;
}

Result<SyncRangeRequest>
decode_sync_range_request(std::span<const std::uint8_t> bytes) {
  if (bytes.size() < kSyncRangeRequestBaseBytes ||
      bytes[0U] != kSyncWireVersion || !all_zero(bytes.subspan(4U, 4U))) {
    return Status{ErrorCode::protocol_error,
                  "sync range request is not canonical"};
  }
  const std::size_t count = read_u16(bytes, 2U);
  if (count == 0U || count > kSyncMaximumRanges ||
      bytes.size() !=
          kSyncRangeRequestBaseBytes + count * kSyncRangeRecordBytes) {
    return Status{ErrorCode::protocol_error,
                  "sync range request length or count is invalid"};
  }
  SyncRangeRequest request;
  auto namespace_id = decode_namespace(bytes, 72U, bytes[1U]);
  if (!namespace_id) return namespace_id.status();
  request.namespace_id = std::move(namespace_id).value();
  read_array(bytes, 8U, request.head_record);
  read_array(bytes, 40U, request.transfer_id);
  request.ranges.reserve(count);
  std::size_t offset = kSyncRangeRequestBaseBytes;
  for (std::size_t index = 0U; index < count; ++index) {
    request.ranges.push_back(
        {read_u64(bytes, offset), read_u64(bytes, offset + 8U)});
    offset += kSyncRangeRecordBytes;
  }
  const Status ranges = validate_ranges(request.ranges);
  if (all_zero(request.head_record) || all_zero(request.transfer_id) ||
      !ranges.ok()) {
    return Status{ErrorCode::protocol_error,
                  "sync range request identity or ranges are invalid"};
  }
  return request;
}

Result<std::vector<std::uint8_t>>
encode_sync_range_result(const SyncRangeResult &result) {
  if (!valid_range_status(result.status) || all_zero(result.head_record) ||
      all_zero(result.transfer_id)) {
    return Status{ErrorCode::invalid_argument,
                  "sync range result identity is invalid"};
  }
  std::vector<std::uint8_t> output(kSyncRangeResultBytes, 0U);
  output[0U] = kSyncWireVersion;
  output[1U] = static_cast<std::uint8_t>(result.status);
  write_array(output, 8U, result.head_record);
  write_array(output, 40U, result.transfer_id);
  return output;
}

Result<SyncRangeResult>
decode_sync_range_result(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncRangeResultBytes ||
      bytes[0U] != kSyncWireVersion || !all_zero(bytes.subspan(2U, 6U))) {
    return Status{ErrorCode::protocol_error,
                  "sync range result is not canonical"};
  }
  SyncRangeResult result;
  result.status = static_cast<SyncRangeResultStatus>(bytes[1U]);
  read_array(bytes, 8U, result.head_record);
  read_array(bytes, 40U, result.transfer_id);
  if (!valid_range_status(result.status) || all_zero(result.head_record) ||
      all_zero(result.transfer_id)) {
    return Status{ErrorCode::protocol_error,
                  "sync range result identity is invalid"};
  }
  return result;
}

Result<protocol::Frame> make_sync_head_request_frame(
    const SyncHeadRequest &request, std::uint64_t message_id) {
  if (message_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync HEAD request message identifier is zero"};
  }
  auto payload = encode_sync_head_request(request);
  if (!payload) return payload.status();
  return request_frame(protocol::MessageType::sync_head_request, message_id,
                       std::move(payload).value());
}

Result<protocol::Frame> make_sync_head_result_frame(
    const SyncHeadResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id) {
  if (message_id == 0U || correlation_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync HEAD result identifier is zero"};
  }
  auto payload = encode_sync_head_result(result);
  if (!payload) return payload.status();
  return result_frame(protocol::MessageType::sync_head_result, message_id,
                      correlation_id, std::move(payload).value());
}

Result<protocol::Frame> make_sync_object_request_frame(
    const SyncObjectRequest &request, std::uint64_t message_id) {
  if (message_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync object request message identifier is zero"};
  }
  auto payload = encode_sync_object_request(request);
  if (!payload) return payload.status();
  return request_frame(protocol::MessageType::sync_object_request, message_id,
                       std::move(payload).value());
}

Result<protocol::Frame> make_sync_object_result_frame(
    const SyncObjectResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id) {
  if (message_id == 0U || correlation_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync object result identifier is zero"};
  }
  auto payload = encode_sync_object_result(result);
  if (!payload) return payload.status();
  return result_frame(protocol::MessageType::sync_object_result, message_id,
                      correlation_id, std::move(payload).value());
}

Result<protocol::Frame> make_sync_range_request_frame(
    const SyncRangeRequest &request, std::uint64_t message_id) {
  if (message_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync range request message identifier is zero"};
  }
  auto payload = encode_sync_range_request(request);
  if (!payload) return payload.status();
  return request_frame(protocol::MessageType::sync_range_request, message_id,
                       std::move(payload).value());
}

Result<protocol::Frame> make_sync_range_result_frame(
    const SyncRangeResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id) {
  if (message_id == 0U || correlation_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync range result identifier is zero"};
  }
  auto payload = encode_sync_range_result(result);
  if (!payload) return payload.status();
  return result_frame(protocol::MessageType::sync_range_result, message_id,
                      correlation_id, std::move(payload).value());
}

Status validate_sync_head_request_frame(const protocol::Frame &frame) {
  const Status envelope = validate_request_envelope(
      frame, protocol::MessageType::sync_head_request);
  if (!envelope.ok()) return envelope;
  auto decoded = decode_sync_head_request(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status validate_sync_head_result_frame(const protocol::Frame &frame) {
  const Status envelope = validate_result_envelope(
      frame, protocol::MessageType::sync_head_result);
  if (!envelope.ok()) return envelope;
  auto decoded = decode_sync_head_result(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status validate_sync_object_request_frame(const protocol::Frame &frame) {
  const Status envelope = validate_request_envelope(
      frame, protocol::MessageType::sync_object_request);
  if (!envelope.ok()) return envelope;
  auto decoded = decode_sync_object_request(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status validate_sync_object_result_frame(const protocol::Frame &frame) {
  const Status envelope = validate_result_envelope(
      frame, protocol::MessageType::sync_object_result);
  if (!envelope.ok()) return envelope;
  auto decoded = decode_sync_object_result(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status validate_sync_range_request_frame(const protocol::Frame &frame) {
  const Status envelope = validate_request_envelope(
      frame, protocol::MessageType::sync_range_request);
  if (!envelope.ok()) return envelope;
  auto decoded = decode_sync_range_request(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status validate_sync_range_result_frame(const protocol::Frame &frame) {
  const Status envelope = validate_result_envelope(
      frame, protocol::MessageType::sync_range_result);
  if (!envelope.ok()) return envelope;
  auto decoded = decode_sync_range_result(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

} // namespace iotox::sync
