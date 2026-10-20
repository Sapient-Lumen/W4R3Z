#include "iotox/sync_content_wire.hpp"

#include "iotox/sync_namespace.hpp"

#include <algorithm>
#include <array>
#include <utility>

namespace iotox::sync {
namespace {

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

bool valid_object_kind(SyncContentObjectKind kind) noexcept {
  return kind == SyncContentObjectKind::manifest_page ||
         kind == SyncContentObjectKind::artifact_chunk ||
         kind == SyncContentObjectKind::root_manifest;
}

bool valid_availability_kind(SyncContentObjectKind kind) noexcept {
  return kind == SyncContentObjectKind::manifest_page ||
         kind == SyncContentObjectKind::artifact_chunk;
}

bool valid_status(SyncContentObjectResultStatus status) noexcept {
  return status == SyncContentObjectResultStatus::offered ||
         status == SyncContentObjectResultStatus::denied ||
         status == SyncContentObjectResultStatus::stale_head ||
         status == SyncContentObjectResultStatus::object_absent ||
         status == SyncContentObjectResultStatus::unavailable;
}

bool valid_status(SyncContentAvailabilityResultStatus status) noexcept {
  return status == SyncContentAvailabilityResultStatus::available ||
         status == SyncContentAvailabilityResultStatus::denied ||
         status == SyncContentAvailabilityResultStatus::stale_head ||
         status == SyncContentAvailabilityResultStatus::unavailable;
}

void write_u32(std::span<std::uint8_t> output, std::size_t offset,
               std::uint32_t value) {
  for (std::size_t index = 0U; index < 4U; ++index) {
    output[offset + index] =
        static_cast<std::uint8_t>(value >> ((3U - index) * 8U));
  }
}

std::uint32_t read_u32(std::span<const std::uint8_t> input,
                       std::size_t offset) {
  std::uint32_t value = 0U;
  for (std::size_t index = 0U; index < 4U; ++index) {
    value = static_cast<std::uint32_t>((value << 8U) | input[offset + index]);
  }
  return value;
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output[offset + index] =
        static_cast<std::uint8_t>(value >> ((7U - index) * 8U));
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

Status encode_namespace(std::span<std::uint8_t> output,
                        std::string_view namespace_id, std::size_t offset) {
  if (!valid_namespace_id(namespace_id) || namespace_id.size() > 64U) {
    return Status{ErrorCode::invalid_argument,
                  "sync content namespace is invalid"};
  }
  if (offset > output.size() || output.size() - offset < 64U) {
    return Status{ErrorCode::invalid_argument,
                  "sync content namespace output is truncated"};
  }
  std::copy(namespace_id.begin(), namespace_id.end(),
            output.begin() + static_cast<std::ptrdiff_t>(offset));
  return Status::success();
}

Result<std::string> decode_namespace(std::span<const std::uint8_t> input,
                                     std::size_t length, std::size_t offset) {
  if (length == 0U || length > 64U || offset > input.size() ||
      input.size() - offset < 64U ||
      !all_zero(input.subspan(offset + length, 64U - length))) {
    return Status{ErrorCode::protocol_error,
                  "sync content namespace slot is invalid"};
  }
  std::string value(reinterpret_cast<const char *>(input.data() + offset),
                    length);
  if (!valid_namespace_id(value)) {
    return Status{ErrorCode::protocol_error,
                  "sync content namespace grammar is invalid"};
  }
  return value;
}

Status validate_identity(SyncContentObjectKind kind, const Digest &head_record,
                         const Digest &object, const FileId &transfer_id,
                         std::uint64_t object_bytes) {
  if (!valid_object_kind(kind) || all_zero(head_record) || all_zero(object) ||
      all_zero(transfer_id) || object_bytes == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync content object identity is invalid"};
  }
  return Status::success();
}

Status validate_request_envelope(const protocol::Frame &frame) {
  if (frame.type != protocol::MessageType::sync_content_object_request ||
      frame.major != protocol::kProtocolMajor ||
      frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
      frame.message_id == 0U || frame.correlation_id != 0U ||
      frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync content request frame envelope is invalid"};
  }
  return Status::success();
}

Status validate_result_envelope(const protocol::Frame &frame) {
  if (frame.type != protocol::MessageType::sync_content_object_result ||
      frame.major != protocol::kProtocolMajor ||
      frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
      frame.message_id == 0U || frame.correlation_id == 0U ||
      frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync content result frame envelope is invalid"};
  }
  return Status::success();
}

Status validate_availability_request_envelope(const protocol::Frame &frame) {
  if (frame.type != protocol::MessageType::sync_content_availability_request ||
      frame.major != protocol::kProtocolMajor ||
      frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
      frame.message_id == 0U || frame.correlation_id != 0U ||
      frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
    return Status{
        ErrorCode::protocol_error,
        "sync content availability request frame envelope is invalid"};
  }
  return Status::success();
}

Status validate_availability_result_envelope(const protocol::Frame &frame) {
  if (frame.type != protocol::MessageType::sync_content_availability_result ||
      frame.major != protocol::kProtocolMajor ||
      frame.minor != protocol::kProtocolMinor || frame.flags != 0U ||
      frame.message_id == 0U || frame.correlation_id == 0U ||
      frame.sequence != 0U || frame.expiry_unix_ms != 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync content availability result frame envelope is invalid"};
  }
  return Status::success();
}

Status validate_availability_identity(SyncContentObjectKind kind,
                                      const Digest &head_record,
                                      std::uint32_t object_count) {
  if (!valid_availability_kind(kind) || all_zero(head_record) ||
      object_count == 0U ||
      object_count > kSyncContentMaximumAvailabilityObjects) {
    return Status{ErrorCode::invalid_argument,
                  "sync content availability identity is invalid"};
  }
  return Status::success();
}

std::size_t availability_bytes(std::uint32_t object_count) {
  return (static_cast<std::size_t>(object_count) + 7U) / 8U;
}

bool canonical_availability(std::span<const std::uint8_t> bits,
                            std::uint32_t object_count) {
  const std::size_t expected = availability_bytes(object_count);
  if (bits.size() != expected)
    return false;
  const std::uint32_t remainder = object_count % 8U;
  if (remainder == 0U)
    return true;
  const std::uint8_t allowed = static_cast<std::uint8_t>(
      (std::uint32_t{1U} << remainder) - std::uint32_t{1U});
  return (bits.back() & static_cast<std::uint8_t>(~allowed)) == 0U;
}

} // namespace

Result<std::vector<std::uint8_t>>
encode_sync_content_object_request(const SyncContentObjectRequest &request) {
  const Status valid =
      validate_identity(request.kind, request.head_record, request.object,
                        request.transfer_id, request.object_bytes);
  if (!valid.ok())
    return valid;
  std::vector<std::uint8_t> output(kSyncContentObjectRequestBytes, 0U);
  output[0U] = kSyncContentWireVersion;
  output[1U] = static_cast<std::uint8_t>(request.kind);
  output[2U] = static_cast<std::uint8_t>(request.namespace_id.size());
  write_array(output, 8U, request.head_record);
  write_array(output, 40U, request.object);
  write_array(output, 72U, request.transfer_id);
  write_u64(output, 104U, request.logical_index);
  write_u64(output, 112U, request.object_bytes);
  const Status encoded = encode_namespace(output, request.namespace_id, 120U);
  if (!encoded.ok())
    return encoded;
  return output;
}

Result<SyncContentObjectRequest>
decode_sync_content_object_request(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncContentObjectRequestBytes ||
      bytes[0U] != kSyncContentWireVersion ||
      !all_zero(bytes.subspan(3U, 5U))) {
    return Status{ErrorCode::protocol_error,
                  "sync content object request is not canonical"};
  }
  SyncContentObjectRequest request;
  request.kind = static_cast<SyncContentObjectKind>(bytes[1U]);
  auto namespace_id = decode_namespace(bytes, bytes[2U], 120U);
  if (!namespace_id)
    return namespace_id.status();
  request.namespace_id = std::move(namespace_id).value();
  read_array(bytes, 8U, request.head_record);
  read_array(bytes, 40U, request.object);
  read_array(bytes, 72U, request.transfer_id);
  request.logical_index = read_u64(bytes, 104U);
  request.object_bytes = read_u64(bytes, 112U);
  const Status valid =
      validate_identity(request.kind, request.head_record, request.object,
                        request.transfer_id, request.object_bytes);
  return valid.ok() ? Result<SyncContentObjectRequest>{std::move(request)}
                    : Result<SyncContentObjectRequest>{
                          Status{ErrorCode::protocol_error, valid.message()}};
}

Result<std::vector<std::uint8_t>>
encode_sync_content_object_result(const SyncContentObjectResult &result) {
  const Status valid =
      validate_identity(result.kind, result.head_record, result.object,
                        result.transfer_id, result.object_bytes);
  if (!valid_status(result.status) || !valid.ok()) {
    return Status{ErrorCode::invalid_argument,
                  "sync content object result is invalid"};
  }
  std::vector<std::uint8_t> output(kSyncContentObjectResultBytes, 0U);
  output[0U] = kSyncContentWireVersion;
  output[1U] = static_cast<std::uint8_t>(result.status);
  output[2U] = static_cast<std::uint8_t>(result.kind);
  write_array(output, 8U, result.head_record);
  write_array(output, 40U, result.object);
  write_array(output, 72U, result.transfer_id);
  write_u64(output, 104U, result.logical_index);
  write_u64(output, 112U, result.object_bytes);
  return output;
}

Result<SyncContentObjectResult>
decode_sync_content_object_result(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncContentObjectResultBytes ||
      bytes[0U] != kSyncContentWireVersion ||
      !all_zero(bytes.subspan(3U, 5U))) {
    return Status{ErrorCode::protocol_error,
                  "sync content object result is not canonical"};
  }
  SyncContentObjectResult result;
  result.status = static_cast<SyncContentObjectResultStatus>(bytes[1U]);
  result.kind = static_cast<SyncContentObjectKind>(bytes[2U]);
  read_array(bytes, 8U, result.head_record);
  read_array(bytes, 40U, result.object);
  read_array(bytes, 72U, result.transfer_id);
  result.logical_index = read_u64(bytes, 104U);
  result.object_bytes = read_u64(bytes, 112U);
  const Status valid =
      validate_identity(result.kind, result.head_record, result.object,
                        result.transfer_id, result.object_bytes);
  if (!valid_status(result.status) || !valid.ok()) {
    return Status{ErrorCode::protocol_error,
                  "sync content object result is invalid"};
  }
  return result;
}

Result<std::vector<std::uint8_t>> encode_sync_content_availability_request(
    const SyncContentAvailabilityRequest &request) {
  const Status valid = validate_availability_identity(
      request.kind, request.head_record, request.object_count);
  if (!valid.ok())
    return valid;
  std::vector<std::uint8_t> output(kSyncContentAvailabilityRequestBytes, 0U);
  output[0U] = kSyncContentWireVersion;
  output[1U] = static_cast<std::uint8_t>(request.kind);
  output[2U] = static_cast<std::uint8_t>(request.namespace_id.size());
  write_u32(output, 4U, request.object_count);
  write_array(output, 8U, request.head_record);
  write_u64(output, 40U, request.first_object);
  const Status encoded = encode_namespace(output, request.namespace_id, 56U);
  if (!encoded.ok())
    return encoded;
  return output;
}

Result<SyncContentAvailabilityRequest>
decode_sync_content_availability_request(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kSyncContentAvailabilityRequestBytes ||
      bytes[0U] != kSyncContentWireVersion || bytes[3U] != 0U ||
      !all_zero(bytes.subspan(48U, 8U))) {
    return Status{ErrorCode::protocol_error,
                  "sync content availability request is not canonical"};
  }
  SyncContentAvailabilityRequest request;
  request.kind = static_cast<SyncContentObjectKind>(bytes[1U]);
  auto namespace_id = decode_namespace(bytes, bytes[2U], 56U);
  if (!namespace_id)
    return namespace_id.status();
  request.namespace_id = std::move(namespace_id).value();
  request.object_count = read_u32(bytes, 4U);
  read_array(bytes, 8U, request.head_record);
  request.first_object = read_u64(bytes, 40U);
  const Status valid = validate_availability_identity(
      request.kind, request.head_record, request.object_count);
  return valid.ok() ? Result<SyncContentAvailabilityRequest>{std::move(request)}
                    : Result<SyncContentAvailabilityRequest>{
                          Status{ErrorCode::protocol_error, valid.message()}};
}

Result<std::vector<std::uint8_t>> encode_sync_content_availability_result(
    const SyncContentAvailabilityResult &result) {
  const Status valid = validate_availability_identity(
      result.kind, result.head_record, result.object_count);
  if (!valid_status(result.status) || !valid.ok() ||
      !canonical_availability(result.availability, result.object_count)) {
    return Status{ErrorCode::invalid_argument,
                  "sync content availability result is invalid"};
  }
  std::vector<std::uint8_t> output(
      kSyncContentAvailabilityResultBaseBytes + result.availability.size(), 0U);
  output[0U] = kSyncContentWireVersion;
  output[1U] = static_cast<std::uint8_t>(result.status);
  output[2U] = static_cast<std::uint8_t>(result.kind);
  write_u32(output, 4U, result.object_count);
  write_array(output, 8U, result.head_record);
  write_u64(output, 40U, result.first_object);
  write_u32(output, 48U,
            static_cast<std::uint32_t>(result.availability.size()));
  std::copy(result.availability.begin(), result.availability.end(),
            output.begin() + static_cast<std::ptrdiff_t>(
                                 kSyncContentAvailabilityResultBaseBytes));
  return output;
}

Result<SyncContentAvailabilityResult>
decode_sync_content_availability_result(std::span<const std::uint8_t> bytes) {
  if (bytes.size() < kSyncContentAvailabilityResultBaseBytes ||
      bytes[0U] != kSyncContentWireVersion || bytes[3U] != 0U ||
      !all_zero(bytes.subspan(52U, 4U))) {
    return Status{ErrorCode::protocol_error,
                  "sync content availability result is not canonical"};
  }
  SyncContentAvailabilityResult result;
  result.status = static_cast<SyncContentAvailabilityResultStatus>(bytes[1U]);
  result.kind = static_cast<SyncContentObjectKind>(bytes[2U]);
  result.object_count = read_u32(bytes, 4U);
  read_array(bytes, 8U, result.head_record);
  result.first_object = read_u64(bytes, 40U);
  const std::uint32_t encoded_bytes = read_u32(bytes, 48U);
  const Status valid = validate_availability_identity(
      result.kind, result.head_record, result.object_count);
  if (!valid_status(result.status) || !valid.ok() ||
      encoded_bytes != availability_bytes(result.object_count) ||
      bytes.size() != kSyncContentAvailabilityResultBaseBytes + encoded_bytes) {
    return Status{ErrorCode::protocol_error,
                  "sync content availability result is invalid"};
  }
  result.availability.assign(
      bytes.begin() +
          static_cast<std::ptrdiff_t>(kSyncContentAvailabilityResultBaseBytes),
      bytes.end());
  if (!canonical_availability(result.availability, result.object_count)) {
    return Status{ErrorCode::protocol_error,
                  "sync content availability bitmap is not canonical"};
  }
  auto canonical = encode_sync_content_availability_result(result);
  if (!canonical || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "sync content availability result is not canonical"};
  }
  return result;
}

Result<protocol::Frame>
make_sync_content_object_request_frame(const SyncContentObjectRequest &request,
                                       std::uint64_t message_id) {
  if (message_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync content request message identifier is zero"};
  }
  auto payload = encode_sync_content_object_request(request);
  if (!payload)
    return payload.status();
  protocol::Frame frame;
  frame.type = protocol::MessageType::sync_content_object_request;
  frame.message_id = message_id;
  frame.payload = std::move(payload).value();
  return frame;
}

Result<protocol::Frame>
make_sync_content_object_result_frame(const SyncContentObjectResult &result,
                                      std::uint64_t message_id,
                                      std::uint64_t correlation_id) {
  if (message_id == 0U || correlation_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync content result identifier is zero"};
  }
  auto payload = encode_sync_content_object_result(result);
  if (!payload)
    return payload.status();
  protocol::Frame frame;
  frame.type = protocol::MessageType::sync_content_object_result;
  frame.message_id = message_id;
  frame.correlation_id = correlation_id;
  frame.payload = std::move(payload).value();
  return frame;
}

Result<protocol::Frame> make_sync_content_availability_request_frame(
    const SyncContentAvailabilityRequest &request, std::uint64_t message_id) {
  if (message_id == 0U) {
    return Status{
        ErrorCode::invalid_argument,
        "sync content availability request message identifier is zero"};
  }
  auto payload = encode_sync_content_availability_request(request);
  if (!payload)
    return payload.status();
  protocol::Frame frame;
  frame.type = protocol::MessageType::sync_content_availability_request;
  frame.message_id = message_id;
  frame.payload = std::move(payload).value();
  return frame;
}

Result<protocol::Frame> make_sync_content_availability_result_frame(
    const SyncContentAvailabilityResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id) {
  if (message_id == 0U || correlation_id == 0U) {
    return Status{ErrorCode::invalid_argument,
                  "sync content availability result identifier is zero"};
  }
  auto payload = encode_sync_content_availability_result(result);
  if (!payload)
    return payload.status();
  protocol::Frame frame;
  frame.type = protocol::MessageType::sync_content_availability_result;
  frame.message_id = message_id;
  frame.correlation_id = correlation_id;
  frame.payload = std::move(payload).value();
  return frame;
}

Status
validate_sync_content_object_request_frame(const protocol::Frame &frame) {
  const Status envelope = validate_request_envelope(frame);
  if (!envelope.ok())
    return envelope;
  auto decoded = decode_sync_content_object_request(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status validate_sync_content_object_result_frame(const protocol::Frame &frame) {
  const Status envelope = validate_result_envelope(frame);
  if (!envelope.ok())
    return envelope;
  auto decoded = decode_sync_content_object_result(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status
validate_sync_content_availability_request_frame(const protocol::Frame &frame) {
  const Status envelope = validate_availability_request_envelope(frame);
  if (!envelope.ok())
    return envelope;
  auto decoded = decode_sync_content_availability_request(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

Status
validate_sync_content_availability_result_frame(const protocol::Frame &frame) {
  const Status envelope = validate_availability_result_envelope(frame);
  if (!envelope.ok())
    return envelope;
  auto decoded = decode_sync_content_availability_result(frame.payload);
  return decoded ? Status::success() : decoded.status();
}

} // namespace iotox::sync
