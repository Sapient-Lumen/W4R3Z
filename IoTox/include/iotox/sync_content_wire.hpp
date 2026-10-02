#pragma once

#include "iotox/protocol/frame.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/transport.hpp"

#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <vector>

namespace iotox::sync {

inline constexpr std::uint8_t kSyncContentWireVersion = 1U;
inline constexpr std::size_t kSyncContentObjectRequestBytes = 184U;
inline constexpr std::size_t kSyncContentObjectResultBytes = 120U;
inline constexpr std::size_t kSyncContentAvailabilityRequestBytes = 120U;
inline constexpr std::size_t kSyncContentAvailabilityResultBaseBytes = 56U;
inline constexpr std::uint32_t kSyncContentMaximumAvailabilityObjects = 8192U;

enum class SyncContentObjectKind : std::uint8_t {
  manifest_page = 1U,
  artifact_chunk = 2U,
  root_manifest = 3U,
};

enum class SyncContentObjectResultStatus : std::uint8_t {
  offered = 1U,
  denied = 2U,
  stale_head = 3U,
  object_absent = 4U,
  unavailable = 5U,
};

enum class SyncContentAvailabilityResultStatus : std::uint8_t {
  available = 1U,
  denied = 2U,
  stale_head = 3U,
  unavailable = 4U,
};

struct SyncContentObjectRequest {
  std::string namespace_id;
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  Digest head_record{};
  Digest object{};
  FileId transfer_id{};
  std::uint64_t logical_index{0U};
  std::uint64_t object_bytes{0U};

  [[nodiscard]] bool
  operator==(const SyncContentObjectRequest &) const = default;
};

struct SyncContentObjectResult {
  SyncContentObjectResultStatus status{
      SyncContentObjectResultStatus::unavailable};
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  Digest head_record{};
  Digest object{};
  FileId transfer_id{};
  std::uint64_t logical_index{0U};
  std::uint64_t object_bytes{0U};

  [[nodiscard]] bool
  operator==(const SyncContentObjectResult &) const = default;
};

struct SyncContentAvailabilityRequest {
  std::string namespace_id;
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  Digest head_record{};
  std::uint64_t first_object{0U};
  std::uint32_t object_count{0U};

  [[nodiscard]] bool
  operator==(const SyncContentAvailabilityRequest &) const = default;
};

struct SyncContentAvailabilityResult {
  SyncContentAvailabilityResultStatus status{
      SyncContentAvailabilityResultStatus::unavailable};
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  Digest head_record{};
  std::uint64_t first_object{0U};
  std::uint32_t object_count{0U};
  // Little-endian bits: bit zero of byte zero describes first_object.
  std::vector<std::uint8_t> availability;

  [[nodiscard]] bool
  operator==(const SyncContentAvailabilityResult &) const = default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_content_object_request(const SyncContentObjectRequest &request);
[[nodiscard]] Result<SyncContentObjectRequest>
decode_sync_content_object_request(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_content_object_result(const SyncContentObjectResult &result);
[[nodiscard]] Result<SyncContentObjectResult>
decode_sync_content_object_result(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_content_availability_request(
    const SyncContentAvailabilityRequest &request);
[[nodiscard]] Result<SyncContentAvailabilityRequest>
decode_sync_content_availability_request(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_content_availability_result(
    const SyncContentAvailabilityResult &result);
[[nodiscard]] Result<SyncContentAvailabilityResult>
decode_sync_content_availability_result(std::span<const std::uint8_t> bytes);

[[nodiscard]] Result<protocol::Frame>
make_sync_content_object_request_frame(const SyncContentObjectRequest &request,
                                       std::uint64_t message_id);
[[nodiscard]] Result<protocol::Frame>
make_sync_content_object_result_frame(const SyncContentObjectResult &result,
                                      std::uint64_t message_id,
                                      std::uint64_t correlation_id);
[[nodiscard]] Result<protocol::Frame>
make_sync_content_availability_request_frame(
    const SyncContentAvailabilityRequest &request, std::uint64_t message_id);
[[nodiscard]] Result<protocol::Frame>
make_sync_content_availability_result_frame(
    const SyncContentAvailabilityResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id);
[[nodiscard]] Status
validate_sync_content_object_request_frame(const protocol::Frame &frame);
[[nodiscard]] Status
validate_sync_content_object_result_frame(const protocol::Frame &frame);
[[nodiscard]] Status
validate_sync_content_availability_request_frame(const protocol::Frame &frame);
[[nodiscard]] Status
validate_sync_content_availability_result_frame(const protocol::Frame &frame);

} // namespace iotox::sync
