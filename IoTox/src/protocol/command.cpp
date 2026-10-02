#include "iotox/protocol/command.hpp"

#include "iotox/security/sodium.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <sstream>

namespace iotox::protocol {
namespace {

constexpr std::array<std::uint8_t, 4U> kCommandMagic{'I', 'C', 'Q', '1'};
constexpr std::array<std::uint8_t, 4U> kUpdateStageCommandMagic{
    'I', 'C', 'Q', '2'};
constexpr std::array<std::uint8_t, 4U> kResultMagic{'I', 'C', 'R', '1'};
constexpr std::array<std::uint8_t, 4U> kReceiptMagic{'I', 'C', 'A', '1'};
constexpr std::array<std::uint8_t, 4U> kDescriptionMagic{'I', 'D', 'D', '1'};
constexpr std::array<std::uint8_t, 4U> kSystemSummaryMagic{'I', 'S', 'S', '1'};
constexpr std::array<std::uint8_t, 4U> kProfileStatusEvidenceMagic{
    'I', 'P', 'S', '1'};
constexpr std::array<std::uint8_t, 4U> kUpdateStageEvidenceMagic{
    'I', 'U', 'S', '1'};

constexpr CommandOperationPolicy kDeviceDescribePolicy{
    CommandOperation::device_describe,
    "device.describe",
    kDeviceDescribeOperationBit,
    static_cast<std::uint64_t>(security::Capability::read_telemetry),
    CommandRestartPolicy::reexecute_read_only,
    true,
};
constexpr CommandOperationPolicy kSystemSummaryPolicy{
    CommandOperation::system_summary,
    "system.summary",
    kSystemSummaryOperationBit,
    static_cast<std::uint64_t>(security::Capability::read_telemetry),
    CommandRestartPolicy::reexecute_read_only,
    true,
};
constexpr CommandOperationPolicy kProfileStatusSetPolicy{
    CommandOperation::profile_status_set,
    "profile.status.set",
    kProfileStatusSetOperationBit,
    static_cast<std::uint64_t>(security::Capability::write_settings),
    CommandRestartPolicy::reexecute_idempotent_desired_state,
    false,
};
constexpr CommandOperationPolicy kUpdateStagePolicy{
    CommandOperation::update_stage,
    "update.stage",
    kUpdateStageOperationBit,
    static_cast<std::uint64_t>(security::Capability::install_firmware),
    CommandRestartPolicy::reexecute_idempotent_desired_state,
    false,
};

void write_u16(std::span<std::uint8_t> output, std::size_t offset,
               std::uint16_t value) {
    output[offset] = static_cast<std::uint8_t>((value >> 8U) & 0xffU);
    output[offset + 1U] = static_cast<std::uint8_t>(value & 0xffU);
}

void write_u32(std::span<std::uint8_t> output, std::size_t offset,
               std::uint32_t value) {
    for (std::size_t index = 0U; index < 4U; ++index) {
        const std::size_t shift = (3U - index) * 8U;
        output[offset + index] =
            static_cast<std::uint8_t>((value >> shift) & 0xffU);
    }
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        const std::size_t shift = (7U - index) * 8U;
        output[offset + index] =
            static_cast<std::uint8_t>((value >> shift) & 0xffU);
    }
}

std::uint16_t read_u16(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(input[offset]) << 8U) |
        static_cast<std::uint16_t>(input[offset + 1U]));
}

std::uint32_t read_u32(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>(
            (value << 8U) | static_cast<std::uint32_t>(input[offset + index]));
    }
    return value;
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) |
                static_cast<std::uint64_t>(input[offset + index]);
    }
    return value;
}

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t value) { return value == 0U; });
}

bool known_operation(std::uint8_t raw) {
    return raw == static_cast<std::uint8_t>(CommandOperation::device_describe) ||
           raw == static_cast<std::uint8_t>(CommandOperation::system_summary) ||
           raw == static_cast<std::uint8_t>(CommandOperation::profile_status_set) ||
           raw == static_cast<std::uint8_t>(CommandOperation::update_stage);
}

bool known_profile_status(std::uint8_t raw) {
    return raw <= static_cast<std::uint8_t>(
        CommandRequest::ProfileStatus::busy);
}

bool known_outcome(std::uint8_t raw) {
    return raw <= static_cast<std::uint8_t>(CommandOutcome::internal_error);
}

bool known_receipt_stage(std::uint8_t raw) {
    return raw >= static_cast<std::uint8_t>(CommandReceiptStage::received) &&
           raw <= static_cast<std::uint8_t>(CommandReceiptStage::started);
}

}  // namespace

Result<std::vector<std::uint8_t>> encode_command_request(
    const CommandRequest &request) {
    if (!command_operation_policy(request.operation).has_value()) {
        return Status{ErrorCode::invalid_argument,
                      "command operation must be a registered operation"};
    }
    if (request.operation == CommandOperation::update_stage) {
        if (!request.expected_update_head.has_value() ||
            all_zero(*request.expected_update_head) ||
            request.desired_profile_status.has_value()) {
            return Status{
                ErrorCode::invalid_argument,
                "update.stage requires one nonzero exact accepted HEAD"};
        }
        std::vector<std::uint8_t> output(
            kUpdateStageCommandRequestBytes, 0U);
        std::copy(kUpdateStageCommandMagic.begin(),
                  kUpdateStageCommandMagic.end(), output.begin());
        output[4U] = kUpdateStageCommandPayloadVersion;
        output[5U] = static_cast<std::uint8_t>(request.operation);
        std::copy(request.expected_update_head->begin(),
                  request.expected_update_head->end(), output.begin() + 8U);
        return output;
    }
    if (request.expected_update_head.has_value()) {
        return Status{ErrorCode::invalid_argument,
                      "only update.stage accepts an update HEAD"};
    }
    std::vector<std::uint8_t> output(kCommandRequestBytes, 0U);
    std::copy(kCommandMagic.begin(), kCommandMagic.end(), output.begin());
    output[4U] = kCommandPayloadVersion;
    output[5U] = static_cast<std::uint8_t>(request.operation);
    if (request.operation == CommandOperation::profile_status_set) {
        if (!request.desired_profile_status.has_value() ||
            !known_profile_status(static_cast<std::uint8_t>(
                *request.desired_profile_status))) {
            return Status{ErrorCode::invalid_argument,
                          "profile.status.set requires available, away, or busy"};
        }
        output[6U] = static_cast<std::uint8_t>(
            *request.desired_profile_status);
    } else if (request.desired_profile_status.has_value()) {
        return Status{ErrorCode::invalid_argument,
                      "read-only command operations do not accept an argument"};
    }
    return output;
}

Result<CommandRequest> decode_command_request(
    std::span<const std::uint8_t> payload) {
    if (payload.size() == kUpdateStageCommandRequestBytes &&
        std::equal(kUpdateStageCommandMagic.begin(),
                   kUpdateStageCommandMagic.end(), payload.begin())) {
        if (payload[4U] != kUpdateStageCommandPayloadVersion) {
            return Status{ErrorCode::unsupported,
                          "update.stage COMMAND payload version is unsupported"};
        }
        if (payload[5U] !=
                static_cast<std::uint8_t>(CommandOperation::update_stage) ||
            payload[6U] != 0U || payload[7U] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "update.stage operation or reserved bytes are invalid"};
        }
        CommandRequest request;
        request.operation = CommandOperation::update_stage;
        UpdateHeadRecord head{};
        std::copy_n(payload.begin() + 8U, head.size(), head.begin());
        if (all_zero(head)) {
            return Status{ErrorCode::protocol_error,
                          "update.stage accepted HEAD may not be zero"};
        }
        request.expected_update_head = head;
        return request;
    }
    if (payload.size() != kCommandRequestBytes) {
        return Status{ErrorCode::protocol_error,
                      "COMMAND payload has no supported fixed size"};
    }
    if (!std::equal(kCommandMagic.begin(), kCommandMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "COMMAND payload magic is invalid"};
    }
    if (payload[4U] != kCommandPayloadVersion) {
        return Status{ErrorCode::unsupported,
                      "COMMAND payload version is unsupported"};
    }
    if (!known_operation(payload[5U])) {
        return Status{ErrorCode::unsupported,
                      "COMMAND operation is unsupported"};
    }
    CommandRequest request;
    request.operation = static_cast<CommandOperation>(payload[5U]);
    if (request.operation == CommandOperation::update_stage) {
        return Status{ErrorCode::unsupported,
                      "update.stage requires the ICQ2 request form"};
    }
    if (request.operation == CommandOperation::profile_status_set) {
        if (!known_profile_status(payload[6U]) || payload[7U] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "profile.status.set argument or reserved byte is invalid"};
        }
        request.desired_profile_status =
            static_cast<CommandRequest::ProfileStatus>(payload[6U]);
    } else if (payload[6U] != 0U || payload[7U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "read-only COMMAND argument bytes must be zero"};
    }
    return request;
}

Result<CommandReceiptBytes> encode_command_receipt(
    const CommandReceipt &receipt) {
    if (!known_receipt_stage(static_cast<std::uint8_t>(receipt.stage))) {
        return Status{ErrorCode::invalid_argument,
                      "command receipt stage must be assigned"};
    }
    CommandReceiptBytes output{};
    std::copy(kReceiptMagic.begin(), kReceiptMagic.end(), output.begin());
    output[4U] = kCommandReceiptPayloadVersion;
    output[5U] = static_cast<std::uint8_t>(receipt.stage);
    return output;
}

Result<CommandReceipt> decode_command_receipt(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kCommandReceiptBytes) {
        return Status{ErrorCode::protocol_error,
                      "ACKNOWLEDGEMENT payload must be exactly 8 bytes"};
    }
    if (!std::equal(kReceiptMagic.begin(), kReceiptMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "ACKNOWLEDGEMENT payload magic is invalid"};
    }
    if (payload[4U] != kCommandReceiptPayloadVersion) {
        return Status{ErrorCode::unsupported,
                      "ACKNOWLEDGEMENT payload version is unsupported"};
    }
    if (!known_receipt_stage(payload[5U])) {
        return Status{ErrorCode::protocol_error,
                      "ACKNOWLEDGEMENT stage is invalid"};
    }
    if (payload[6U] != 0U || payload[7U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "ACKNOWLEDGEMENT reserved bytes must be zero"};
    }
    return CommandReceipt{static_cast<CommandReceiptStage>(payload[5U])};
}

Result<std::vector<std::uint8_t>> encode_command_result(
    const CommandResultPayload &result) {
    if (result.operation == CommandOperation::unknown &&
        result.outcome == CommandOutcome::succeeded) {
        return Status{ErrorCode::invalid_argument,
                      "successful COMMAND_RESULT must name an operation"};
    }
    if (result.body.size() >
        kMaxPayloadSize - kCommandResultHeaderBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "COMMAND_RESULT body exceeds the frame payload limit"};
    }
    if (result.outcome != CommandOutcome::succeeded && !result.body.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "failed COMMAND_RESULT must have an empty body"};
    }
    if (result.operation == CommandOperation::device_describe &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kDeviceDescriptionBytes) {
        return Status{ErrorCode::invalid_argument,
                      "successful device.describe result requires 64-byte description"};
    }
    if (result.operation == CommandOperation::system_summary &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kSystemSummaryBytes) {
        return Status{ErrorCode::invalid_argument,
                      "successful system.summary result requires 40-byte summary"};
    }
    if (result.operation == CommandOperation::profile_status_set &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kProfileStatusEvidenceBytes) {
        return Status{ErrorCode::invalid_argument,
                      "successful profile.status.set result requires 8-byte evidence"};
    }
    if (result.operation == CommandOperation::update_stage &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kUpdateStageEvidenceBytes) {
        return Status{ErrorCode::invalid_argument,
                      "successful update.stage result requires 80-byte evidence"};
    }

    std::vector<std::uint8_t> output(
        kCommandResultHeaderBytes + result.body.size(), 0U);
    std::copy(kResultMagic.begin(), kResultMagic.end(), output.begin());
    output[4U] = kCommandResultPayloadVersion;
    output[5U] = static_cast<std::uint8_t>(result.operation);
    output[6U] = static_cast<std::uint8_t>(result.outcome);
    write_u32(output, 8U, static_cast<std::uint32_t>(result.body.size()));
    std::copy(result.body.begin(), result.body.end(),
              output.begin() + static_cast<std::ptrdiff_t>(kCommandResultHeaderBytes));
    return output;
}

Result<CommandResultPayload> decode_command_result(
    std::span<const std::uint8_t> payload) {
    if (payload.size() < kCommandResultHeaderBytes) {
        return Status{ErrorCode::protocol_error,
                      "COMMAND_RESULT payload is truncated"};
    }
    if (!std::equal(kResultMagic.begin(), kResultMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "COMMAND_RESULT payload magic is invalid"};
    }
    if (payload[4U] != kCommandResultPayloadVersion) {
        return Status{ErrorCode::unsupported,
                      "COMMAND_RESULT payload version is unsupported"};
    }
    if (payload[7U] != 0U || !all_zero(payload.subspan(12U, 4U))) {
        return Status{ErrorCode::protocol_error,
                      "COMMAND_RESULT reserved bytes must be zero"};
    }
    if (payload[5U] != 0U && !known_operation(payload[5U])) {
        return Status{ErrorCode::unsupported,
                      "COMMAND_RESULT operation is unsupported"};
    }
    if (!known_outcome(payload[6U])) {
        return Status{ErrorCode::protocol_error,
                      "COMMAND_RESULT outcome is invalid"};
    }
    const std::uint32_t body_size = read_u32(payload, 8U);
    if (body_size != payload.size() - kCommandResultHeaderBytes) {
        return Status{ErrorCode::protocol_error,
                      "COMMAND_RESULT body length does not match payload"};
    }

    CommandResultPayload result;
    result.operation = static_cast<CommandOperation>(payload[5U]);
    result.outcome = static_cast<CommandOutcome>(payload[6U]);
    result.body.assign(
        payload.begin() + static_cast<std::ptrdiff_t>(kCommandResultHeaderBytes),
        payload.end());
    if (result.outcome != CommandOutcome::succeeded && !result.body.empty()) {
        return Status{ErrorCode::protocol_error,
                      "failed COMMAND_RESULT contains an unexpected body"};
    }
    if (result.operation == CommandOperation::device_describe &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kDeviceDescriptionBytes) {
        return Status{ErrorCode::protocol_error,
                      "device.describe result has the wrong body size"};
    }
    if (result.operation == CommandOperation::system_summary &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kSystemSummaryBytes) {
        return Status{ErrorCode::protocol_error,
                      "system.summary result has the wrong body size"};
    }
    if (result.operation == CommandOperation::profile_status_set &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kProfileStatusEvidenceBytes) {
        return Status{ErrorCode::protocol_error,
                      "profile.status.set result has the wrong body size"};
    }
    if (result.operation == CommandOperation::update_stage &&
        result.outcome == CommandOutcome::succeeded &&
        result.body.size() != kUpdateStageEvidenceBytes) {
        return Status{ErrorCode::protocol_error,
                      "update.stage result has the wrong body size"};
    }
    return result;
}

Result<SystemSummaryBytes> encode_system_summary(const SystemSummary &summary) {
    const auto health = static_cast<std::uint8_t>(summary.health);
    if (health > static_cast<std::uint8_t>(SystemHealth::degraded) ||
        (summary.flags & ~kSystemSummaryKnownFlags) != 0U ||
        summary.memory_available_64mib > summary.memory_total_64mib ||
        summary.load_milli > 1000000U || summary.process_count > 10000000U ||
        summary.load_milli % 100U != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "system summary violates its bounded schema"};
    }
    SystemSummaryBytes output{};
    std::copy(kSystemSummaryMagic.begin(), kSystemSummaryMagic.end(), output.begin());
    output[4U] = kSystemSummaryVersion;
    output[5U] = health;
    write_u16(output, 6U, summary.flags);
    write_u32(output, 8U, summary.uptime_minutes);
    write_u32(output, 12U, summary.memory_total_64mib);
    write_u32(output, 16U, summary.memory_available_64mib);
    write_u32(output, 20U, summary.load_milli);
    write_u32(output, 24U, summary.process_count);
    return output;
}

Result<SystemSummary> decode_system_summary(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kSystemSummaryBytes) {
        return Status{ErrorCode::protocol_error,
                      "system summary must be exactly 40 bytes"};
    }
    if (!std::equal(kSystemSummaryMagic.begin(), kSystemSummaryMagic.end(),
                    payload.begin())) {
        return Status{ErrorCode::protocol_error, "system summary magic is invalid"};
    }
    if (payload[4U] != kSystemSummaryVersion) {
        return Status{ErrorCode::unsupported,
                      "system summary version is unsupported"};
    }
    if (!all_zero(payload.subspan(28U, 12U))) {
        return Status{ErrorCode::protocol_error,
                      "system summary reserved bytes must be zero"};
    }
    SystemSummary summary;
    summary.health = static_cast<SystemHealth>(payload[5U]);
    summary.flags = read_u16(payload, 6U);
    summary.uptime_minutes = read_u32(payload, 8U);
    summary.memory_total_64mib = read_u32(payload, 12U);
    summary.memory_available_64mib = read_u32(payload, 16U);
    summary.load_milli = read_u32(payload, 20U);
    summary.process_count = read_u32(payload, 24U);
    auto canonical = encode_system_summary(summary);
    if (!canonical) {
        return Status{ErrorCode::protocol_error, canonical.status().message()};
    }
    return summary;
}

Result<ProfileStatusEvidenceBytes> encode_profile_status_evidence(
    const ProfileStatusEvidence &evidence) {
    const auto desired = static_cast<std::uint8_t>(evidence.desired);
    const auto observed = static_cast<std::uint8_t>(evidence.observed);
    if (!known_profile_status(desired) || !known_profile_status(observed) ||
        desired != observed) {
        return Status{ErrorCode::invalid_argument,
                      "profile status evidence requires equal bounded desired and observed values"};
    }
    ProfileStatusEvidenceBytes output{};
    std::copy(kProfileStatusEvidenceMagic.begin(),
              kProfileStatusEvidenceMagic.end(), output.begin());
    output[4U] = kProfileStatusEvidenceVersion;
    output[5U] = desired;
    output[6U] = observed;
    return output;
}

Result<ProfileStatusEvidence> decode_profile_status_evidence(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kProfileStatusEvidenceBytes) {
        return Status{ErrorCode::protocol_error,
                      "profile status evidence must be exactly 8 bytes"};
    }
    if (!std::equal(kProfileStatusEvidenceMagic.begin(),
                    kProfileStatusEvidenceMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "profile status evidence magic is invalid"};
    }
    if (payload[4U] != kProfileStatusEvidenceVersion) {
        return Status{ErrorCode::unsupported,
                      "profile status evidence version is unsupported"};
    }
    if (!known_profile_status(payload[5U]) ||
        !known_profile_status(payload[6U]) || payload[7U] != 0U ||
        payload[5U] != payload[6U]) {
        return Status{ErrorCode::protocol_error,
                      "profile status evidence is non-canonical or does not prove convergence"};
    }
    ProfileStatusEvidence evidence;
    evidence.desired =
        static_cast<CommandRequest::ProfileStatus>(payload[5U]);
    evidence.observed =
        static_cast<CommandRequest::ProfileStatus>(payload[6U]);
    return evidence;
}

Result<UpdateStageEvidenceBytes> encode_update_stage_evidence(
    const UpdateStageEvidence &evidence) {
    if (evidence.release_sequence == 0U || all_zero(evidence.accepted_head) ||
        all_zero(evidence.manifest_record)) {
        return Status{
            ErrorCode::invalid_argument,
            "update stage evidence requires a sequence, accepted HEAD, and manifest record"};
    }
    UpdateStageEvidenceBytes output{};
    std::copy(kUpdateStageEvidenceMagic.begin(),
              kUpdateStageEvidenceMagic.end(), output.begin());
    output[4U] = kUpdateStageEvidenceVersion;
    output[5U] = evidence.duplicate ? 1U : 0U;
    write_u64(output, 8U, evidence.release_sequence);
    std::copy(evidence.accepted_head.begin(), evidence.accepted_head.end(),
              output.begin() + 16U);
    std::copy(evidence.manifest_record.begin(),
              evidence.manifest_record.end(), output.begin() + 48U);
    return output;
}

Result<UpdateStageEvidence> decode_update_stage_evidence(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kUpdateStageEvidenceBytes) {
        return Status{ErrorCode::protocol_error,
                      "update stage evidence must be exactly 80 bytes"};
    }
    if (!std::equal(kUpdateStageEvidenceMagic.begin(),
                    kUpdateStageEvidenceMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "update stage evidence magic is invalid"};
    }
    if (payload[4U] != kUpdateStageEvidenceVersion) {
        return Status{ErrorCode::unsupported,
                      "update stage evidence version is unsupported"};
    }
    if (payload[5U] > 1U || payload[6U] != 0U || payload[7U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "update stage evidence flags or reserved bytes are invalid"};
    }
    UpdateStageEvidence evidence;
    evidence.duplicate = payload[5U] != 0U;
    evidence.release_sequence = read_u64(payload, 8U);
    std::copy_n(payload.begin() + 16U, evidence.accepted_head.size(),
                evidence.accepted_head.begin());
    std::copy_n(payload.begin() + 48U, evidence.manifest_record.size(),
                evidence.manifest_record.begin());
    auto canonical = encode_update_stage_evidence(evidence);
    if (!canonical) {
        return Status{ErrorCode::protocol_error,
                      canonical.status().message()};
    }
    return evidence;
}

Result<DeviceDescriptionBytes> encode_device_description(
    const DeviceDescription &description) {
    if (description.protocol.major == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "device description protocol version must be assigned"};
    }
    if (all_zero(description.device_principal)) {
        return Status{ErrorCode::invalid_argument,
                      "device description principal must be nonzero"};
    }
    if ((description.offered_operations & kDeviceDescribeOperationBit) == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "device description must advertise device.describe"};
    }

    DeviceDescriptionBytes output{};
    std::copy(kDescriptionMagic.begin(), kDescriptionMagic.end(), output.begin());
    output[4U] = kDeviceDescriptionVersion;
    output[5U] = 0U;
    write_u16(output, 6U, description.revision_number);
    write_u16(output, 8U, description.version_major);
    write_u16(output, 10U, description.version_minor);
    write_u16(output, 12U, description.version_patch);
    output[14U] = description.protocol.major;
    output[15U] = description.protocol.minor;
    std::copy(description.device_principal.begin(),
              description.device_principal.end(), output.begin() + 16);
    write_u64(output, 48U, description.supported_features);
    write_u64(output, 56U, description.offered_operations);
    return output;
}

Result<DeviceDescription> decode_device_description(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kDeviceDescriptionBytes) {
        return Status{ErrorCode::protocol_error,
                      "device description must be exactly 64 bytes"};
    }
    if (!std::equal(kDescriptionMagic.begin(), kDescriptionMagic.end(),
                    payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "device description magic is invalid"};
    }
    if (payload[4U] != kDeviceDescriptionVersion) {
        return Status{ErrorCode::unsupported,
                      "device description version is unsupported"};
    }
    if (payload[5U] != 0U || payload[14U] == 0U) {
        return Status{ErrorCode::protocol_error,
                      "device description flags/version are invalid"};
    }

    DeviceDescription description;
    description.revision_number = read_u16(payload, 6U);
    description.version_major = read_u16(payload, 8U);
    description.version_minor = read_u16(payload, 10U);
    description.version_patch = read_u16(payload, 12U);
    description.protocol = {payload[14U], payload[15U]};
    std::copy(payload.begin() + 16, payload.begin() + 48,
              description.device_principal.begin());
    description.supported_features = read_u64(payload, 48U);
    description.offered_operations = read_u64(payload, 56U);
    if (all_zero(description.device_principal)) {
        return Status{ErrorCode::protocol_error,
                      "device description principal is zero"};
    }
    if ((description.offered_operations & kDeviceDescribeOperationBit) == 0U) {
        return Status{ErrorCode::protocol_error,
                      "device description does not advertise device.describe"};
    }
    return description;
}

std::optional<CommandOperationPolicy> command_operation_policy(
    CommandOperation operation) noexcept {
    switch (operation) {
        case CommandOperation::device_describe:
            return kDeviceDescribePolicy;
        case CommandOperation::system_summary:
            return kSystemSummaryPolicy;
        case CommandOperation::profile_status_set:
            return kProfileStatusSetPolicy;
        case CommandOperation::update_stage:
            return kUpdateStagePolicy;
        case CommandOperation::unknown:
            return std::nullopt;
    }
    return std::nullopt;
}

std::optional<CommandOperation> parse_command_operation(
    std::string_view name) noexcept {
    if (name == kDeviceDescribePolicy.name) {
        return kDeviceDescribePolicy.operation;
    }
    if (name == kSystemSummaryPolicy.name) {
        return kSystemSummaryPolicy.operation;
    }
    if (name == kProfileStatusSetPolicy.name) {
        return kProfileStatusSetPolicy.operation;
    }
    if (name == kUpdateStagePolicy.name) {
        return kUpdateStagePolicy.operation;
    }
    return std::nullopt;
}

std::uint64_t implemented_operation_mask() noexcept {
    return kDeviceDescribePolicy.advertised_bit |
           kSystemSummaryPolicy.advertised_bit |
           kProfileStatusSetPolicy.advertised_bit |
           kUpdateStagePolicy.advertised_bit;
}

std::uint64_t required_capabilities(CommandOperation operation) noexcept {
    const auto policy = command_operation_policy(operation);
    return policy.has_value() ? policy->required_capabilities : 0U;
}

bool command_restart_safe(CommandOperation operation) noexcept {
    const auto policy = command_operation_policy(operation);
    return policy.has_value() &&
           ((policy->read_only && policy->restart_policy ==
                CommandRestartPolicy::reexecute_read_only) ||
            (!policy->read_only && policy->restart_policy ==
                CommandRestartPolicy::reexecute_idempotent_desired_state));
}

std::string to_string(CommandOperation operation) {
    const auto policy = command_operation_policy(operation);
    return policy.has_value() ? std::string(policy->name) : "unknown";
}

std::string to_string(CommandRequest::ProfileStatus status) {
    switch (status) {
        case CommandRequest::ProfileStatus::available: return "available";
        case CommandRequest::ProfileStatus::away: return "away";
        case CommandRequest::ProfileStatus::busy: return "busy";
    }
    return "unknown";
}

std::string to_string(CommandOutcome outcome) {
    switch (outcome) {
        case CommandOutcome::succeeded: return "succeeded";
        case CommandOutcome::denied: return "denied";
        case CommandOutcome::malformed: return "malformed";
        case CommandOutcome::unsupported: return "unsupported";
        case CommandOutcome::expired: return "expired";
        case CommandOutcome::conflict: return "conflict";
        case CommandOutcome::internal_error: return "internal-error";
    }
    return "unknown";
}

std::string to_string(CommandReceiptStage stage) {
    switch (stage) {
        case CommandReceiptStage::none: return "none";
        case CommandReceiptStage::received: return "received";
        case CommandReceiptStage::admitted: return "admitted";
        case CommandReceiptStage::started: return "started";
    }
    return "unknown";
}

std::string to_string(PeerDescriptionState state) {
    switch (state) {
        case PeerDescriptionState::none: return "none";
        case PeerDescriptionState::send_failed: return "send-failed";
        case PeerDescriptionState::awaiting_result: return "awaiting-result";
        case PeerDescriptionState::succeeded: return "succeeded";
        case PeerDescriptionState::denied: return "denied";
        case PeerDescriptionState::malformed: return "malformed";
        case PeerDescriptionState::unsupported: return "unsupported";
        case PeerDescriptionState::expired: return "expired";
        case PeerDescriptionState::conflict: return "conflict";
        case PeerDescriptionState::internal_error: return "internal-error";
    }
    return "unknown";
}

std::string render_device_description(
    const DeviceDescription &description) {
    std::ostringstream output;
    output << "device-principal=" << security::hex(description.device_principal)
           << '\n'
           << "product=IoTox\n"
           << "version=" << description.version_major << '.'
           << description.version_minor << '.' << description.version_patch
           << '\n'
           << "revision=rev";
    output.width(4);
    output.fill('0');
    output << description.revision_number << '\n'
           << "protocol=" << static_cast<unsigned>(description.protocol.major)
           << '.' << static_cast<unsigned>(description.protocol.minor) << '\n'
           << "supported-features="
           << render_feature_mask(description.supported_features) << '\n'
           << "offered-operations=";
    bool first = true;
    for (const CommandOperationPolicy policy :
         std::array<CommandOperationPolicy, 4U>{
             kDeviceDescribePolicy, kSystemSummaryPolicy,
             kProfileStatusSetPolicy, kUpdateStagePolicy}) {
        if ((description.offered_operations & policy.advertised_bit) == 0U) {
            continue;
        }
        if (!first) output << ',';
        output << policy.name;
        first = false;
    }
    output << '\n';
    return output.str();
}

std::string render_system_summary(const SystemSummary &summary) {
    std::ostringstream output;
    output << "health=";
    switch (summary.health) {
        case SystemHealth::unknown: output << "unknown"; break;
        case SystemHealth::healthy: output << "healthy"; break;
        case SystemHealth::degraded: output << "degraded"; break;
    }
    output << '\n' << "uptime-minutes=" << summary.uptime_minutes << '\n';
    if ((summary.flags & kSystemSummaryMemoryValid) != 0U) {
        output << "memory-total-64mib=" << summary.memory_total_64mib << '\n'
               << "memory-available-64mib="
               << summary.memory_available_64mib << '\n';
    }
    if ((summary.flags & kSystemSummaryLoadValid) != 0U) {
        output << "load-milli=" << summary.load_milli << '\n';
    }
    if ((summary.flags & kSystemSummaryProcessCountValid) != 0U) {
        output << "process-count=" << summary.process_count << '\n';
    }
    return output.str();
}

std::string render_profile_status_evidence(
    const ProfileStatusEvidence &evidence) {
    std::ostringstream output;
    output << "desired-status=" << to_string(evidence.desired) << '\n'
           << "observed-status=" << to_string(evidence.observed) << '\n'
           << "converged=" << (evidence.desired == evidence.observed ? 1 : 0)
           << '\n';
    return output.str();
}

std::string render_update_stage_evidence(
    const UpdateStageEvidence &evidence) {
    std::ostringstream output;
    output << "update-staged=1\n"
           << "update-duplicate=" << (evidence.duplicate ? 1 : 0) << '\n'
           << "update-sequence=" << evidence.release_sequence << '\n'
           << "update-accepted-head="
           << security::hex(evidence.accepted_head) << '\n'
           << "update-manifest-record="
           << security::hex(evidence.manifest_record) << '\n';
    return output.str();
}

std::string render_peer_description(
    const PeerDescriptionSnapshot &snapshot) {
    std::ostringstream output;
    output << "friend-number=" << snapshot.friend_number << '\n'
           << "online-epoch=" << snapshot.online_epoch << '\n'
           << "sender-epoch=" << snapshot.sender_epoch << '\n'
           << "state=" << to_string(snapshot.state) << '\n'
           << "request-message-id=" << snapshot.request_message_id << '\n'
           << "receipt-message-id=" << snapshot.receipt_message_id << '\n'
           << "receipt-stage=" << to_string(snapshot.receipt_stage) << '\n'
           << "result-message-id=" << snapshot.result_message_id << '\n'
           << "outcome=" << to_string(snapshot.outcome) << '\n'
           << "send-attempts=" << snapshot.send_attempts << '\n'
           << "last-send-error-code="
           << static_cast<unsigned>(snapshot.last_send_error_code) << '\n'
           << "last-send-error=" << snapshot.last_send_error << '\n'
           << "detail=" << snapshot.detail << '\n'
           << "updated-unix-ms=" << snapshot.updated_unix_ms << '\n';
    if (snapshot.description) {
        output << render_device_description(*snapshot.description);
    }
    return output.str();
}

}  // namespace iotox::protocol
