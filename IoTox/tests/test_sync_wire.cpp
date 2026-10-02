#include "iotox/sync_content_wire.hpp"
#include "iotox/sync_wire.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <cstdint>
#include <limits>
#include <utility>

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

iotox::sync::SignedHead head() {
  iotox::sync::SignedHead result;
  result.namespace_id = "field-notes";
  result.writer.fill(0x11U);
  result.engine = iotox::sync::Engine::range_v1;
  result.generation = 1U;
  result.artifact = digest(0x22U);
  result.manifest = digest(0x33U);
  result.artifact_bytes = 4096U;
  result.manifest_bytes = 512U;
  result.signature.fill(0x44U);
  return result;
}

} // namespace

IOTOX_TEST(
    "sync wire HEAD request and signed result have exact canonical forms") {
  const iotox::sync::SyncHeadRequest request{"field-notes"};
  auto encoded_request = iotox::sync::encode_sync_head_request(request);
  IOTOX_CHECK(encoded_request.ok());
  IOTOX_CHECK(encoded_request.value().size() ==
              iotox::sync::kSyncHeadRequestBytes);
  auto decoded_request =
      iotox::sync::decode_sync_head_request(encoded_request.value());
  IOTOX_CHECK(decoded_request.ok() && decoded_request.value() == request);

  const iotox::sync::SyncHeadResult available{
      iotox::sync::SyncHeadResultStatus::available, head()};
  auto encoded_result = iotox::sync::encode_sync_head_result(available);
  IOTOX_CHECK(encoded_result.ok());
  IOTOX_CHECK(encoded_result.value().size() ==
              iotox::sync::kSyncHeadResultBytes);
  auto decoded_result =
      iotox::sync::decode_sync_head_result(encoded_result.value());
  IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == available);

  auto tree_head = head();
  tree_head.engine = iotox::sync::Engine::treepack_v1;
  const iotox::sync::SyncHeadResult tree_available{
      iotox::sync::SyncHeadResultStatus::available, tree_head};
  encoded_result = iotox::sync::encode_sync_head_result(tree_available);
  IOTOX_CHECK(encoded_result.ok());
  decoded_result = iotox::sync::decode_sync_head_result(encoded_result.value());
  IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == tree_available);

  const iotox::sync::SyncHeadResult absent{
      iotox::sync::SyncHeadResultStatus::absent, std::nullopt};
  encoded_result = iotox::sync::encode_sync_head_result(absent);
  IOTOX_CHECK(encoded_result.ok());
  decoded_result = iotox::sync::decode_sync_head_result(encoded_result.value());
  IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == absent);
}

IOTOX_TEST(
    "sync wire object request binds HEAD kind namespace and Tox file id") {
  const iotox::sync::SyncObjectRequest request{
      "field-notes", iotox::sync::SyncObjectKind::artifact, digest(0x51U),
      file_id(0x61U)};
  auto encoded_request = iotox::sync::encode_sync_object_request(request);
  IOTOX_CHECK(encoded_request.ok());
  IOTOX_CHECK(encoded_request.value().size() ==
              iotox::sync::kSyncObjectRequestBytes);
  auto decoded_request =
      iotox::sync::decode_sync_object_request(encoded_request.value());
  IOTOX_CHECK(decoded_request.ok() && decoded_request.value() == request);

  const iotox::sync::SyncObjectResult result{
      iotox::sync::SyncObjectResultStatus::offered, request.kind,
      request.head_record, request.transfer_id};
  auto encoded_result = iotox::sync::encode_sync_object_result(result);
  IOTOX_CHECK(encoded_result.ok());
  IOTOX_CHECK(encoded_result.value().size() ==
              iotox::sync::kSyncObjectResultBytes);
  auto decoded_result =
      iotox::sync::decode_sync_object_result(encoded_result.value());
  IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == result);
}

IOTOX_TEST("sync wire frames freeze request and correlated result envelopes") {
  auto head_request =
      iotox::sync::make_sync_head_request_frame({"field-notes"}, 101U);
  IOTOX_CHECK(head_request.ok());
  IOTOX_CHECK(
      iotox::sync::validate_sync_head_request_frame(head_request.value()).ok());
  auto head_result = iotox::sync::make_sync_head_result_frame(
      {iotox::sync::SyncHeadResultStatus::available, head()}, 102U,
      head_request.value().message_id);
  IOTOX_CHECK(head_result.ok());
  IOTOX_CHECK(
      iotox::sync::validate_sync_head_result_frame(head_result.value()).ok());

  const iotox::sync::SyncObjectRequest object_request{
      "field-notes", iotox::sync::SyncObjectKind::manifest, digest(0x71U),
      file_id(0x81U)};
  auto request_frame =
      iotox::sync::make_sync_object_request_frame(object_request, 201U);
  IOTOX_CHECK(request_frame.ok());
  IOTOX_CHECK(
      iotox::sync::validate_sync_object_request_frame(request_frame.value())
          .ok());
  auto result_frame = iotox::sync::make_sync_object_result_frame(
      {iotox::sync::SyncObjectResultStatus::offered, object_request.kind,
       object_request.head_record, object_request.transfer_id},
      202U, request_frame.value().message_id);
  IOTOX_CHECK(result_frame.ok());
  IOTOX_CHECK(
      iotox::sync::validate_sync_object_result_frame(result_frame.value())
          .ok());
  auto packet = iotox::protocol::encode(result_frame.value());
  IOTOX_CHECK(packet.ok());
  auto decoded = iotox::protocol::decode(packet.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value().type ==
              iotox::protocol::MessageType::sync_object_result);
}

IOTOX_TEST("sync range wire binds one canonical bounded range set to HEAD and "
           "FileId") {
  const iotox::sync::SyncRangeRequest request{
      "field-notes",
      digest(0x92U),
      file_id(0xA2U),
      {{0U, 4096U}, {8192U, 2048U}, {16384U, 512U}}};
  auto encoded = iotox::sync::encode_sync_range_request(request);
  IOTOX_CHECK(encoded.ok());
  IOTOX_CHECK(encoded.value().size() ==
              iotox::sync::kSyncRangeRequestBaseBytes +
                  3U * iotox::sync::kSyncRangeRecordBytes);
  auto decoded = iotox::sync::decode_sync_range_request(encoded.value());
  IOTOX_CHECK(decoded.ok() && decoded.value() == request);
  auto frame = iotox::sync::make_sync_range_request_frame(request, 401U);
  IOTOX_CHECK(frame.ok());
  IOTOX_CHECK(
      iotox::sync::validate_sync_range_request_frame(frame.value()).ok());

  const iotox::sync::SyncRangeResult result{
      iotox::sync::SyncRangeResultStatus::offered, request.head_record,
      request.transfer_id};
  auto result_bytes = iotox::sync::encode_sync_range_result(result);
  IOTOX_CHECK(result_bytes.ok());
  IOTOX_CHECK(result_bytes.value().size() ==
              iotox::sync::kSyncRangeResultBytes);
  auto decoded_result =
      iotox::sync::decode_sync_range_result(result_bytes.value());
  IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == result);
  auto result_frame = iotox::sync::make_sync_range_result_frame(
      result, 402U, frame.value().message_id);
  IOTOX_CHECK(result_frame.ok());
  IOTOX_CHECK(
      iotox::sync::validate_sync_range_result_frame(result_frame.value()).ok());
  auto packet = iotox::protocol::encode(result_frame.value());
  IOTOX_CHECK(packet.ok());
  auto decoded_frame = iotox::protocol::decode(packet.value());
  IOTOX_CHECK(decoded_frame.ok());
  IOTOX_CHECK(decoded_frame.value().type ==
              iotox::protocol::MessageType::sync_range_result);
}

IOTOX_TEST("sync range wire rejects overlap adjacency overflow count and "
           "padding aliases") {
  iotox::sync::SyncRangeRequest request{"field-notes",
                                        digest(0x93U),
                                        file_id(0xA3U),
                                        {{0U, 4096U}, {4096U, 2048U}}};
  IOTOX_CHECK(!iotox::sync::encode_sync_range_request(request).ok());
  request.ranges = {{1U, 4096U}, {4095U, 2048U}};
  IOTOX_CHECK(!iotox::sync::encode_sync_range_request(request).ok());
  request.ranges = {{std::numeric_limits<std::uint64_t>::max(), 1U}};
  IOTOX_CHECK(!iotox::sync::encode_sync_range_request(request).ok());
  request.ranges.assign(iotox::sync::kSyncMaximumRanges + 1U, {1U, 1U});
  IOTOX_CHECK(!iotox::sync::encode_sync_range_request(request).ok());

  request.ranges = {{0U, 128U}};
  auto encoded = iotox::sync::encode_sync_range_request(request);
  IOTOX_CHECK(encoded.ok());
  encoded.value()[4U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_sync_range_request(encoded.value()).ok());
  auto result = iotox::sync::encode_sync_range_result(
      {iotox::sync::SyncRangeResultStatus::denied, request.head_record,
       request.transfer_id});
  IOTOX_CHECK(result.ok());
  result.value()[7U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_sync_range_result(result.value()).ok());
}

IOTOX_TEST("sync wire rejects padding unknown status zero identity and "
           "envelope aliases") {
  auto request = iotox::sync::encode_sync_head_request({"field-notes"});
  IOTOX_CHECK(request.ok());
  request.value()[2U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_sync_head_request(request.value()).ok());

  auto denied = iotox::sync::encode_sync_head_result(
      {iotox::sync::SyncHeadResultStatus::denied, std::nullopt});
  IOTOX_CHECK(denied.ok());
  denied.value()[8U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_sync_head_result(denied.value()).ok());

  iotox::sync::SyncObjectRequest object{"field-notes",
                                        iotox::sync::SyncObjectKind::artifact,
                                        digest(0x91U), file_id(0xa1U)};
  auto object_bytes = iotox::sync::encode_sync_object_request(object);
  IOTOX_CHECK(object_bytes.ok());
  object_bytes.value()[40U] = 0U;
  std::fill(object_bytes.value().begin() + 41,
            object_bytes.value().begin() + 72, 0U);
  IOTOX_CHECK(
      !iotox::sync::decode_sync_object_request(object_bytes.value()).ok());

  auto frame = iotox::sync::make_sync_object_request_frame(object, 301U);
  IOTOX_CHECK(frame.ok());
  frame.value().correlation_id = 1U;
  IOTOX_CHECK(
      !iotox::sync::validate_sync_object_request_frame(frame.value()).ok());
  IOTOX_CHECK(
      !iotox::sync::make_sync_head_request_frame({"field-notes"}, 0U).ok());
}

IOTOX_TEST("content v2 wire binds an exact immutable object to HEAD index and "
           "FileId") {
  const iotox::sync::SyncContentObjectRequest request{
      "field-notes",  iotox::sync::SyncContentObjectKind::artifact_chunk,
      digest(0xb1U),  digest(0xb2U),
      file_id(0xb3U), 17U,
      65536U};
  auto encoded = iotox::sync::encode_sync_content_object_request(request);
  IOTOX_CHECK(encoded.ok());
  IOTOX_CHECK(encoded.value().size() ==
              iotox::sync::kSyncContentObjectRequestBytes);
  auto decoded =
      iotox::sync::decode_sync_content_object_request(encoded.value());
  IOTOX_CHECK(decoded.ok() && decoded.value() == request);

  auto frame =
      iotox::sync::make_sync_content_object_request_frame(request, 501U);
  IOTOX_CHECK(frame.ok());
  IOTOX_CHECK(
      iotox::sync::validate_sync_content_object_request_frame(frame.value())
          .ok());

  const iotox::sync::SyncContentObjectResult result{
      iotox::sync::SyncContentObjectResultStatus::offered,
      request.kind,
      request.head_record,
      request.object,
      request.transfer_id,
      request.logical_index,
      request.object_bytes};
  auto result_bytes = iotox::sync::encode_sync_content_object_result(result);
  IOTOX_CHECK(result_bytes.ok());
  IOTOX_CHECK(result_bytes.value().size() ==
              iotox::sync::kSyncContentObjectResultBytes);
  auto decoded_result =
      iotox::sync::decode_sync_content_object_result(result_bytes.value());
  IOTOX_CHECK(decoded_result.ok() && decoded_result.value() == result);
  auto result_frame = iotox::sync::make_sync_content_object_result_frame(
      result, 502U, frame.value().message_id);
  IOTOX_CHECK(result_frame.ok());
  IOTOX_CHECK(iotox::sync::validate_sync_content_object_result_frame(
                  result_frame.value())
                  .ok());
  auto packet = iotox::protocol::encode(result_frame.value());
  IOTOX_CHECK(packet.ok());
  auto decoded_frame = iotox::protocol::decode(packet.value());
  IOTOX_CHECK(decoded_frame.ok());
  IOTOX_CHECK(decoded_frame.value().type ==
              iotox::protocol::MessageType::sync_content_object_result);
}

IOTOX_TEST("content v2 wire rejects aliases and incomplete identities") {
  iotox::sync::SyncContentObjectRequest request{
      "field-notes",  iotox::sync::SyncContentObjectKind::manifest_page,
      digest(0xc1U),  digest(0xc2U),
      file_id(0xc3U), 0U,
      4096U};
  auto encoded = iotox::sync::encode_sync_content_object_request(request);
  IOTOX_CHECK(encoded.ok());
  encoded.value()[3U] = 1U;
  IOTOX_CHECK(
      !iotox::sync::decode_sync_content_object_request(encoded.value()).ok());

  request.object = {};
  IOTOX_CHECK(!iotox::sync::encode_sync_content_object_request(request).ok());
  request.object = digest(0xc2U);
  request.object_bytes = 0U;
  IOTOX_CHECK(!iotox::sync::encode_sync_content_object_request(request).ok());
  request.object_bytes = 4096U;
  auto frame =
      iotox::sync::make_sync_content_object_request_frame(request, 503U);
  IOTOX_CHECK(frame.ok());
  frame.value().correlation_id = 1U;
  IOTOX_CHECK(
      !iotox::sync::validate_sync_content_object_request_frame(frame.value())
           .ok());

  iotox::sync::SyncContentObjectResult result{
      static_cast<iotox::sync::SyncContentObjectResultStatus>(255U),
      request.kind,
      request.head_record,
      request.object,
      request.transfer_id,
      request.logical_index,
      request.object_bytes};
  IOTOX_CHECK(!iotox::sync::encode_sync_content_object_result(result).ok());
}

IOTOX_TEST(
    "content v2 root manifest keeps frozen framing and has no sparse window") {
  const iotox::sync::SyncContentObjectRequest root{
      "field-notes",  iotox::sync::SyncContentObjectKind::root_manifest,
      digest(0xc4U),  digest(0xc5U),
      file_id(0xc6U), 0U,
      4096U};
  auto encoded = iotox::sync::encode_sync_content_object_request(root);
  IOTOX_CHECK(encoded.ok());
  IOTOX_CHECK(encoded.value().size() ==
              iotox::sync::kSyncContentObjectRequestBytes);
  auto decoded =
      iotox::sync::decode_sync_content_object_request(encoded.value());
  IOTOX_CHECK(decoded.ok() && decoded.value() == root);

  const iotox::sync::SyncContentAvailabilityRequest unavailable{
      "field-notes", iotox::sync::SyncContentObjectKind::root_manifest,
      root.head_record, 0U, 1U};
  IOTOX_CHECK(
      !iotox::sync::encode_sync_content_availability_request(unavailable).ok());
}

IOTOX_TEST("content v2 availability wire freezes an exact sparse window") {
  const iotox::sync::SyncContentAvailabilityRequest request{
      "field-notes", iotox::sync::SyncContentObjectKind::artifact_chunk,
      digest(0xd1U), 4096U, 13U};
  auto encoded = iotox::sync::encode_sync_content_availability_request(request);
  IOTOX_CHECK(encoded.ok());
  IOTOX_CHECK(encoded.value().size() ==
              iotox::sync::kSyncContentAvailabilityRequestBytes);
  auto decoded =
      iotox::sync::decode_sync_content_availability_request(encoded.value());
  IOTOX_CHECK(decoded.ok() && decoded.value() == request);
  auto frame =
      iotox::sync::make_sync_content_availability_request_frame(request, 601U);
  IOTOX_CHECK(frame.ok());
  IOTOX_CHECK(iotox::sync::validate_sync_content_availability_request_frame(
                  frame.value())
                  .ok());

  const iotox::sync::SyncContentAvailabilityResult result{
      iotox::sync::SyncContentAvailabilityResultStatus::available,
      request.kind,
      request.head_record,
      request.first_object,
      request.object_count,
      {0x55U, 0x15U}};
  auto result_bytes =
      iotox::sync::encode_sync_content_availability_result(result);
  IOTOX_CHECK(result_bytes.ok());
  IOTOX_CHECK(result_bytes.value().size() ==
              iotox::sync::kSyncContentAvailabilityResultBaseBytes + 2U);
  auto result_decoded = iotox::sync::decode_sync_content_availability_result(
      result_bytes.value());
  IOTOX_CHECK(result_decoded.ok() && result_decoded.value() == result);
  auto result_frame = iotox::sync::make_sync_content_availability_result_frame(
      result, 602U, frame.value().message_id);
  IOTOX_CHECK(result_frame.ok());
  IOTOX_CHECK(iotox::sync::validate_sync_content_availability_result_frame(
                  result_frame.value())
                  .ok());
  auto packet = iotox::protocol::encode(result_frame.value());
  IOTOX_CHECK(packet.ok());
  auto decoded_frame = iotox::protocol::decode(packet.value());
  IOTOX_CHECK(decoded_frame.ok());
  IOTOX_CHECK(decoded_frame.value().type ==
              iotox::protocol::MessageType::sync_content_availability_result);
}

IOTOX_TEST("content v2 availability rejects tail size and envelope aliases") {
  iotox::sync::SyncContentAvailabilityResult result{
      iotox::sync::SyncContentAvailabilityResultStatus::available,
      iotox::sync::SyncContentObjectKind::manifest_page,
      digest(0xe1U),
      0U,
      9U,
      {0xffU, 0x01U}};
  auto encoded = iotox::sync::encode_sync_content_availability_result(result);
  IOTOX_CHECK(encoded.ok());
  encoded.value().back() = 0x81U;
  IOTOX_CHECK(
      !iotox::sync::decode_sync_content_availability_result(encoded.value())
           .ok());
  result.availability.back() = 0x81U;
  IOTOX_CHECK(
      !iotox::sync::encode_sync_content_availability_result(result).ok());
  result.availability.back() = 0x01U;
  result.object_count =
      iotox::sync::kSyncContentMaximumAvailabilityObjects + 1U;
  IOTOX_CHECK(
      !iotox::sync::encode_sync_content_availability_result(result).ok());

  iotox::sync::SyncContentAvailabilityRequest request{
      "field-notes", iotox::sync::SyncContentObjectKind::artifact_chunk,
      digest(0xe2U), 0U, 8U};
  auto frame =
      iotox::sync::make_sync_content_availability_request_frame(request, 603U);
  IOTOX_CHECK(frame.ok());
  frame.value().correlation_id = 1U;
  IOTOX_CHECK(!iotox::sync::validate_sync_content_availability_request_frame(
                   frame.value())
                   .ok());
}
