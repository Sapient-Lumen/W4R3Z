#pragma once

#include "iotox/protocol/frame.hpp"
#include "iotox/sync_job.hpp"
#include "iotox/sync_publication.hpp"
#include "iotox/transport.hpp"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace iotox::sync {

inline constexpr std::uint8_t kSyncWireVersion = 1U;
inline constexpr std::size_t kSyncWireNamespaceBytes = 64U;
inline constexpr std::size_t kSyncHeadRequestBytes = 72U;
inline constexpr std::size_t kSyncHeadResultBytes = 304U;
inline constexpr std::size_t kSyncObjectRequestBytes = 136U;
inline constexpr std::size_t kSyncObjectResultBytes = 72U;
inline constexpr std::size_t kSyncRangeRequestBaseBytes = 136U;
inline constexpr std::size_t kSyncRangeResultBytes = 72U;
inline constexpr std::size_t kSyncRangeRecordBytes = 16U;
inline constexpr std::size_t kSyncMaximumRanges = 64U;

enum class SyncHeadResultStatus : std::uint8_t {
  available = 1U,
  absent = 2U,
  denied = 3U,
  unavailable = 4U,
};

enum class SyncObjectResultStatus : std::uint8_t {
  offered = 1U,
  denied = 2U,
  stale_head = 3U,
  object_absent = 4U,
  unavailable = 5U,
};

enum class SyncRangeResultStatus : std::uint8_t {
  offered = 1U,
  denied = 2U,
  stale_head = 3U,
  artifact_absent = 4U,
  unavailable = 5U,
};

struct SyncHeadRequest {
  std::string namespace_id;

  [[nodiscard]] bool operator==(const SyncHeadRequest &) const = default;
};

struct SyncHeadResult {
  SyncHeadResultStatus status{SyncHeadResultStatus::unavailable};
  std::optional<SignedHead> head;

  [[nodiscard]] bool operator==(const SyncHeadResult &) const = default;
};

struct SyncObjectRequest {
  std::string namespace_id;
  SyncObjectKind kind{SyncObjectKind::artifact};
  Digest head_record{};
  FileId transfer_id{};

  [[nodiscard]] bool operator==(const SyncObjectRequest &) const = default;
};

struct SyncObjectResult {
  SyncObjectResultStatus status{SyncObjectResultStatus::unavailable};
  SyncObjectKind kind{SyncObjectKind::artifact};
  Digest head_record{};
  FileId transfer_id{};

  [[nodiscard]] bool operator==(const SyncObjectResult &) const = default;
};

struct SyncRangeRecord {
  std::uint64_t offset{0U};
  std::uint64_t length{0U};

  [[nodiscard]] bool operator==(const SyncRangeRecord &) const = default;
};

struct SyncRangeRequest {
  std::string namespace_id;
  Digest head_record{};
  FileId transfer_id{};
  std::vector<SyncRangeRecord> ranges;

  [[nodiscard]] bool operator==(const SyncRangeRequest &) const = default;
};

struct SyncRangeResult {
  SyncRangeResultStatus status{SyncRangeResultStatus::unavailable};
  Digest head_record{};
  FileId transfer_id{};

  [[nodiscard]] bool operator==(const SyncRangeResult &) const = default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_head_request(const SyncHeadRequest &request);
[[nodiscard]] Result<SyncHeadRequest>
decode_sync_head_request(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_head_result(const SyncHeadResult &result);
[[nodiscard]] Result<SyncHeadResult>
decode_sync_head_result(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_object_request(const SyncObjectRequest &request);
[[nodiscard]] Result<SyncObjectRequest>
decode_sync_object_request(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_object_result(const SyncObjectResult &result);
[[nodiscard]] Result<SyncObjectResult>
decode_sync_object_result(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_range_request(const SyncRangeRequest &request);
[[nodiscard]] Result<SyncRangeRequest>
decode_sync_range_request(std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_range_result(const SyncRangeResult &result);
[[nodiscard]] Result<SyncRangeResult>
decode_sync_range_result(std::span<const std::uint8_t> bytes);

[[nodiscard]] Result<protocol::Frame> make_sync_head_request_frame(
    const SyncHeadRequest &request, std::uint64_t message_id);
[[nodiscard]] Result<protocol::Frame> make_sync_head_result_frame(
    const SyncHeadResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id);
[[nodiscard]] Result<protocol::Frame> make_sync_object_request_frame(
    const SyncObjectRequest &request, std::uint64_t message_id);
[[nodiscard]] Result<protocol::Frame> make_sync_object_result_frame(
    const SyncObjectResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id);
[[nodiscard]] Result<protocol::Frame> make_sync_range_request_frame(
    const SyncRangeRequest &request, std::uint64_t message_id);
[[nodiscard]] Result<protocol::Frame> make_sync_range_result_frame(
    const SyncRangeResult &result, std::uint64_t message_id,
    std::uint64_t correlation_id);

[[nodiscard]] Status validate_sync_head_request_frame(
    const protocol::Frame &frame);
[[nodiscard]] Status validate_sync_head_result_frame(
    const protocol::Frame &frame);
[[nodiscard]] Status validate_sync_object_request_frame(
    const protocol::Frame &frame);
[[nodiscard]] Status validate_sync_object_result_frame(
    const protocol::Frame &frame);
[[nodiscard]] Status validate_sync_range_request_frame(
    const protocol::Frame &frame);
[[nodiscard]] Status validate_sync_range_result_frame(
    const protocol::Frame &frame);

} // namespace iotox::sync
