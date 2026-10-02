#pragma once

#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <string_view>
#include <optional>
#include <vector>

namespace iotox::protocol {

// COMMAND v1 has one fixed operation byte and two operation-specific bytes.
// Read-only operations require both argument bytes to be zero. The first
// mutable operation uses one byte for a bounded desired value and remains
// forbidden on the legacy, non-durable command path.
inline constexpr std::uint8_t kCommandPayloadVersion = 1U;
inline constexpr std::size_t kCommandRequestBytes = 8U;
inline constexpr std::uint8_t kUpdateStageCommandPayloadVersion = 2U;
inline constexpr std::size_t kUpdateStageCommandRequestBytes = 40U;
inline constexpr std::uint8_t kCommandResultPayloadVersion = 1U;
inline constexpr std::size_t kCommandResultHeaderBytes = 16U;
inline constexpr std::uint8_t kCommandReceiptPayloadVersion = 1U;
inline constexpr std::size_t kCommandReceiptBytes = 8U;
inline constexpr std::uint8_t kDeviceDescriptionVersion = 1U;
inline constexpr std::size_t kDeviceDescriptionBytes = 64U;
inline constexpr std::uint8_t kSystemSummaryVersion = 1U;
inline constexpr std::size_t kSystemSummaryBytes = 40U;
inline constexpr std::uint8_t kProfileStatusEvidenceVersion = 1U;
inline constexpr std::size_t kProfileStatusEvidenceBytes = 8U;
inline constexpr std::uint8_t kUpdateStageEvidenceVersion = 1U;
inline constexpr std::size_t kUpdateHeadRecordBytes = 32U;
inline constexpr std::size_t kUpdateStageEvidenceBytes = 80U;
inline constexpr std::uint64_t kDeviceDescribeOperationBit = 1ULL << 0U;
inline constexpr std::uint64_t kSystemSummaryOperationBit = 1ULL << 1U;
inline constexpr std::uint64_t kProfileStatusSetOperationBit = 1ULL << 2U;
inline constexpr std::uint64_t kUpdateStageOperationBit = 1ULL << 3U;

using CommandRequestBytes = std::array<std::uint8_t, kCommandRequestBytes>;
using CommandReceiptBytes = std::array<std::uint8_t, kCommandReceiptBytes>;
using DeviceDescriptionBytes =
    std::array<std::uint8_t, kDeviceDescriptionBytes>;
using SystemSummaryBytes = std::array<std::uint8_t, kSystemSummaryBytes>;
using ProfileStatusEvidenceBytes =
    std::array<std::uint8_t, kProfileStatusEvidenceBytes>;
using UpdateHeadRecord = std::array<std::uint8_t, kUpdateHeadRecordBytes>;
using UpdateStageEvidenceBytes =
    std::array<std::uint8_t, kUpdateStageEvidenceBytes>;

enum class CommandOperation : std::uint8_t {
    unknown = 0U,
    device_describe = 1U,
    system_summary = 2U,
    profile_status_set = 3U,
    update_stage = 4U,
};

enum class CommandRestartPolicy : std::uint8_t {
    never_reexecute = 0U,
    reexecute_read_only = 1U,
    reexecute_idempotent_desired_state = 2U,
};

// The operation table is the constitutional bridge between the generic
// durable command engine and operation-specific code. A new operation is not
// admitted merely by assigning an enum value: its wire name, capability,
// advertised bit, and crash/restart policy must be declared together.
struct CommandOperationPolicy {
    CommandOperation operation{CommandOperation::unknown};
    std::string_view name;
    std::uint64_t advertised_bit{0U};
    std::uint64_t required_capabilities{0U};
    CommandRestartPolicy restart_policy{
        CommandRestartPolicy::never_reexecute};
    bool read_only{false};

    [[nodiscard]] bool operator==(const CommandOperationPolicy &) const = default;
};

enum class CommandReceiptStage : std::uint8_t {
    none = 0U,
    received = 1U,
    admitted = 2U,
    started = 3U,
};

struct CommandReceipt {
    CommandReceiptStage stage{CommandReceiptStage::none};

    [[nodiscard]] bool operator==(const CommandReceipt &) const = default;
};

enum class CommandOutcome : std::uint8_t {
    succeeded = 0U,
    denied = 1U,
    malformed = 2U,
    unsupported = 3U,
    expired = 4U,
    conflict = 5U,
    internal_error = 6U,
};

struct CommandRequest {
    CommandOperation operation{CommandOperation::unknown};
    enum class ProfileStatus : std::uint8_t {
        available = 0U,
        away = 1U,
        busy = 2U,
    };
    std::optional<ProfileStatus> desired_profile_status;
    std::optional<UpdateHeadRecord> expected_update_head;

    CommandRequest() = default;
    CommandRequest(CommandOperation requested_operation)
        : operation(requested_operation) {}
    CommandRequest(CommandOperation requested_operation,
                   ProfileStatus desired_status)
        : operation(requested_operation),
          desired_profile_status(desired_status) {}

    [[nodiscard]] bool operator==(const CommandRequest &) const = default;
};

struct ProfileStatusEvidence {
    CommandRequest::ProfileStatus desired{
        CommandRequest::ProfileStatus::available};
    CommandRequest::ProfileStatus observed{
        CommandRequest::ProfileStatus::available};

    [[nodiscard]] bool operator==(const ProfileStatusEvidence &) const = default;
};

// A successful remote update-stage result binds the sender's exact accepted
// sync HEAD to the independently verified release manifest and sequence that
// entered the device's immutable inactive-slot state. It grants no apply,
// restart, health-confirmation, or execution authority.
struct UpdateStageEvidence {
    bool duplicate{false};
    std::uint64_t release_sequence{0U};
    UpdateHeadRecord accepted_head{};
    UpdateHeadRecord manifest_record{};

    [[nodiscard]] bool operator==(const UpdateStageEvidence &) const = default;
};

struct CommandResultPayload {
    CommandOperation operation{CommandOperation::unknown};
    CommandOutcome outcome{CommandOutcome::internal_error};
    std::vector<std::uint8_t> body;

    [[nodiscard]] bool operator==(const CommandResultPayload &) const = default;
};

enum class PeerDescriptionState : std::uint8_t {
    none = 0U,
    send_failed = 1U,
    awaiting_result = 2U,
    succeeded = 3U,
    denied = 4U,
    malformed = 5U,
    unsupported = 6U,
    expired = 7U,
    conflict = 8U,
    internal_error = 9U,
};

struct DeviceDescription {
    std::uint16_t revision_number{0U};
    std::uint16_t version_major{0U};
    std::uint16_t version_minor{0U};
    std::uint16_t version_patch{0U};
    ProtocolVersion protocol{};
    security::SigningPublicKey device_principal{};
    std::uint64_t supported_features{0U};
    std::uint64_t offered_operations{0U};

    [[nodiscard]] bool operator==(const DeviceDescription &) const = default;
};

enum class SystemHealth : std::uint8_t {
    unknown = 0U,
    healthy = 1U,
    degraded = 2U,
};

inline constexpr std::uint16_t kSystemSummaryMemoryValid = 1U << 0U;
inline constexpr std::uint16_t kSystemSummaryLoadValid = 1U << 1U;
inline constexpr std::uint16_t kSystemSummaryProcessCountValid = 1U << 2U;
inline constexpr std::uint16_t kSystemSummaryKnownFlags =
    kSystemSummaryMemoryValid | kSystemSummaryLoadValid |
    kSystemSummaryProcessCountValid;

// Deliberately coarse and identifier-free. Uptime is in whole minutes,
// memory in 64 MiB buckets, and load in tenths (100 milli-load units).
struct SystemSummary {
    SystemHealth health{SystemHealth::unknown};
    std::uint16_t flags{0U};
    std::uint32_t uptime_minutes{0U};
    std::uint32_t memory_total_64mib{0U};
    std::uint32_t memory_available_64mib{0U};
    std::uint32_t load_milli{0U};
    std::uint32_t process_count{0U};

    [[nodiscard]] bool operator==(const SystemSummary &) const = default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_command_request(
    const CommandRequest &request);
[[nodiscard]] Result<CommandRequest> decode_command_request(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<CommandReceiptBytes> encode_command_receipt(
    const CommandReceipt &receipt);
[[nodiscard]] Result<CommandReceipt> decode_command_receipt(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_command_result(
    const CommandResultPayload &result);
[[nodiscard]] Result<CommandResultPayload> decode_command_result(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<DeviceDescriptionBytes> encode_device_description(
    const DeviceDescription &description);
[[nodiscard]] Result<DeviceDescription> decode_device_description(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<SystemSummaryBytes> encode_system_summary(
    const SystemSummary &summary);
[[nodiscard]] Result<SystemSummary> decode_system_summary(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<ProfileStatusEvidenceBytes> encode_profile_status_evidence(
    const ProfileStatusEvidence &evidence);
[[nodiscard]] Result<ProfileStatusEvidence> decode_profile_status_evidence(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<UpdateStageEvidenceBytes> encode_update_stage_evidence(
    const UpdateStageEvidence &evidence);
[[nodiscard]] Result<UpdateStageEvidence> decode_update_stage_evidence(
    std::span<const std::uint8_t> payload);

struct PeerDescriptionSnapshot {
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    PeerDescriptionState state{PeerDescriptionState::none};
    std::uint64_t sender_epoch{0U};
    std::uint64_t request_message_id{0U};
    std::uint64_t receipt_message_id{0U};
    CommandReceiptStage receipt_stage{CommandReceiptStage::none};
    std::uint64_t result_message_id{0U};
    CommandOutcome outcome{CommandOutcome::internal_error};
    std::optional<DeviceDescription> description;
    std::uint32_t send_attempts{0U};
    ErrorCode last_send_error_code{ErrorCode::ok};
    std::string last_send_error;
    std::string detail{"none"};
    std::uint64_t updated_unix_ms{0U};

    [[nodiscard]] bool operator==(const PeerDescriptionSnapshot &) const = default;
};

[[nodiscard]] std::optional<CommandOperationPolicy> command_operation_policy(
    CommandOperation operation) noexcept;
[[nodiscard]] std::optional<CommandOperation> parse_command_operation(
    std::string_view name) noexcept;
[[nodiscard]] std::uint64_t implemented_operation_mask() noexcept;
[[nodiscard]] std::uint64_t required_capabilities(
    CommandOperation operation) noexcept;
[[nodiscard]] bool command_restart_safe(CommandOperation operation) noexcept;
[[nodiscard]] std::string to_string(CommandOperation operation);
[[nodiscard]] std::string to_string(CommandRequest::ProfileStatus status);
[[nodiscard]] std::string to_string(CommandOutcome outcome);
[[nodiscard]] std::string to_string(CommandReceiptStage stage);
[[nodiscard]] std::string to_string(PeerDescriptionState state);
[[nodiscard]] std::string render_device_description(
    const DeviceDescription &description);
[[nodiscard]] std::string render_system_summary(const SystemSummary &summary);
[[nodiscard]] std::string render_profile_status_evidence(
    const ProfileStatusEvidence &evidence);
[[nodiscard]] std::string render_update_stage_evidence(
    const UpdateStageEvidence &evidence);
[[nodiscard]] std::string render_peer_description(
    const PeerDescriptionSnapshot &snapshot);

}  // namespace iotox::protocol
