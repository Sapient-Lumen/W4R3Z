#include "iotox/command_store.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox {
namespace {

constexpr std::array<std::uint8_t, 8U> kStoreMagicV2 = {
    'I', 'O', 'T', 'X', 'C', 'M', 'D', '2'};
constexpr std::array<std::uint8_t, 8U> kStoreMagicV3 = {
    'I', 'O', 'T', 'X', 'C', 'M', 'D', '3'};
constexpr std::uint8_t kStoreFormatV2 = 2U;
constexpr std::uint8_t kStoreFormatV3 = 3U;
constexpr std::uint8_t kSignatureAlgorithmEd25519 = 1U;
constexpr std::size_t kStoreHeaderBytes = 176U;
constexpr std::size_t kUnsignedHeaderBytes = 112U;
constexpr std::size_t kStoreSignatureOffset = kUnsignedHeaderBytes;
constexpr std::size_t kStoreBodyOffset = kStoreHeaderBytes;
constexpr std::size_t kRecordHeaderBytesV2 = 168U;
constexpr std::size_t kRecordHeaderBytesV3 = 240U;
constexpr std::uint8_t kRecordFormatV2 = 2U;
constexpr std::uint8_t kRecordFormatV3 = 3U;
constexpr std::size_t kMaximumCanonicalFrameBytes = protocol::kToxMaxCustomPacketSize;

Status validate_snapshot_quotas(
    const std::vector<DurableCommandRecord> &records,
    const DurableCommandStore::Config &config);

Status file_status(std::string operation, const std::filesystem::path &path) {
    return Status{ErrorCode::io_error,
                  std::move(operation) + " '" + path.string() + "': " +
                      std::strerror(errno)};
}

void append_u16(std::vector<std::uint8_t> &out, std::uint16_t value) {
    out.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    out.push_back(static_cast<std::uint8_t>(value & 0xFFU));
}

void append_u32(std::vector<std::uint8_t> &out, std::uint32_t value) {
    out.push_back(static_cast<std::uint8_t>((value >> 24U) & 0xFFU));
    out.push_back(static_cast<std::uint8_t>((value >> 16U) & 0xFFU));
    out.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    out.push_back(static_cast<std::uint8_t>(value & 0xFFU));
}

void append_u64(std::vector<std::uint8_t> &out, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        out.push_back(static_cast<std::uint8_t>((value >> static_cast<unsigned>(shift)) & 0xFFU));
    }
}

std::uint16_t read_u16(std::span<const std::uint8_t> bytes, std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
        static_cast<std::uint16_t>(bytes[offset + 1U]));
}

std::uint32_t read_u32(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>(
            (value << 8U) | bytes[offset + index]);
    }
    return value;
}

std::uint64_t read_u64(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

bool valid_direction(CommandDirection value) noexcept {
    return value == CommandDirection::incoming || value == CommandDirection::outgoing;
}

bool valid_lifecycle(CommandLifecycle value) noexcept {
    return value >= CommandLifecycle::reserved &&
           value <= CommandLifecycle::timed_out_unconfirmed;
}

bool valid_delivery(CommandDeliveryState value) noexcept {
    return value >= CommandDeliveryState::none &&
           value <= CommandDeliveryState::observed;
}

bool valid_priority(CommandPriority value) noexcept {
    return value >= CommandPriority::low && value <= CommandPriority::high;
}

bool valid_clock_requirement(CommandClockRequirement value) noexcept {
    return value == CommandClockRequirement::none ||
           value == CommandClockRequirement::trusted_wall;
}

bool valid_operation(protocol::CommandOperation value) noexcept {
    return value == protocol::CommandOperation::unknown ||
           value == protocol::CommandOperation::device_describe ||
           value == protocol::CommandOperation::system_summary ||
           value == protocol::CommandOperation::profile_status_set ||
           value == protocol::CommandOperation::update_stage;
}

bool valid_outcome(protocol::CommandOutcome value) noexcept {
    return value >= protocol::CommandOutcome::succeeded &&
           value <= protocol::CommandOutcome::internal_error;
}

bool valid_error_code(ErrorCode code) noexcept {
    return code >= ErrorCode::ok && code <= ErrorCode::resource_exhausted;
}

Status validate_schedule(
    const CommandDeliverySchedule &schedule,
    std::uint64_t created_unix_ms,
    std::string_view label) {
    if (!valid_error_code(schedule.last_error_code)) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) + " contains an unknown error code"};
    }
    if (schedule.attempts == 0U) {
        if (schedule.last_attempt_unix_ms != 0U ||
            schedule.last_error_code != ErrorCode::ok) {
            return Status{ErrorCode::invalid_argument,
                          std::string(label) + " has attempt evidence without an attempt"};
        }
        return Status::success();
    }
    if (schedule.last_attempt_unix_ms < created_unix_ms ||
        schedule.next_attempt_unix_ms < schedule.last_attempt_unix_ms) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) + " timestamps are absent or move backwards"};
    }
    return Status::success();
}

Status validate_canonical_frame(
    std::span<const std::uint8_t> bytes,
    protocol::MessageType expected,
    std::string_view label,
    bool allow_empty) {
    if (bytes.empty()) {
        return allow_empty
            ? Status::success()
            : Status{ErrorCode::invalid_argument,
                     std::string(label) + " is required"};
    }
    if (bytes.size() > kMaximumCanonicalFrameBytes) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) + " exceeds the Tox custom-packet limit"};
    }
    auto decoded = protocol::decode(bytes);
    if (!decoded) {
        return Status{decoded.status().code(),
                      std::string(label) + " is not a canonical IoTox frame: " +
                          decoded.status().message()};
    }
    auto reencoded = protocol::encode(decoded.value());
    if (!reencoded || reencoded.value().size() != bytes.size() ||
        !std::equal(reencoded.value().begin(), reencoded.value().end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not canonical"};
    }
    if (decoded.value().type != expected) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " has the wrong IoTox message type"};
    }
    return Status::success();
}

Status validate_record(const DurableCommandRecord &record) {
    if (all_zero(record.key.peer_public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "durable command peer public key is zero"};
    }
    if (record.key.sender_epoch == 0U || record.key.message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "durable command sender epoch and message id must be non-zero"};
    }
    if (!valid_direction(record.key.direction) ||
        !valid_direction(record.direction) ||
        record.key.direction != record.direction ||
        !valid_lifecycle(record.lifecycle) ||
        !valid_operation(record.operation) || !valid_outcome(record.outcome) ||
        !valid_delivery(record.receipt_delivery) ||
        !valid_delivery(record.result_delivery) ||
        !valid_priority(record.priority) ||
        !valid_clock_requirement(record.clock_requirement)) {
        return Status{ErrorCode::invalid_argument,
                      "durable command record contains an unknown enum value"};
    }
    if (record.created_unix_ms == 0U || record.updated_unix_ms == 0U ||
        record.updated_unix_ms < record.created_unix_ms) {
        return Status{ErrorCode::invalid_argument,
                      "durable command timestamps are absent or move backwards"};
    }
    for (const auto &[schedule, label] :
         std::array<std::pair<const CommandDeliverySchedule *, std::string_view>, 3U>{{
             {&record.request_schedule, "request delivery schedule"},
             {&record.receipt_schedule, "receipt delivery schedule"},
             {&record.result_schedule, "result delivery schedule"},
         }}) {
        const Status schedule_status = validate_schedule(
            *schedule, record.created_unix_ms, label);
        if (!schedule_status.ok()) {
            return schedule_status;
        }
    }
    const Status request_status = validate_canonical_frame(
        record.canonical_request, protocol::MessageType::command,
        "canonical command request", false);
    if (!request_status.ok()) {
        return request_status;
    }
    const Status receipt_status = validate_canonical_frame(
        record.canonical_receipt, protocol::MessageType::acknowledgement,
        "canonical command receipt", true);
    if (!receipt_status.ok()) {
        return receipt_status;
    }
    const Status result_status = validate_canonical_frame(
        record.canonical_result, protocol::MessageType::command_result,
        "canonical command result", true);
    if (!result_status.ok()) {
        return result_status;
    }

    auto request = protocol::decode(record.canonical_request);
    if (!request) {
        return request.status();
    }
    if (request.value().message_id != record.key.message_id ||
        request.value().sequence != record.key.sender_epoch ||
        request.value().correlation_id != 0U ||
        request.value().expiry_unix_ms != record.expiry_unix_ms) {
        return Status{ErrorCode::protocol_error,
                      "canonical command request does not match its durable key"};
    }
    const CommandClockRequirement expected_clock_requirement =
        record.expiry_unix_ms == 0U
        ? CommandClockRequirement::none
        : CommandClockRequirement::trusted_wall;
    if (record.clock_requirement != expected_clock_requirement) {
        return Status{ErrorCode::protocol_error,
                      "durable command clock requirement disagrees with its expiry"};
    }
    auto command = protocol::decode_command_request(request.value().payload);
    if (!command || command.value().operation != record.operation) {
        return Status{ErrorCode::protocol_error,
                      "canonical command request operation does not match its record"};
    }
    const auto operation_policy =
        protocol::command_operation_policy(record.operation);
    if (operation_policy.has_value() && !operation_policy->read_only &&
        record.expiry_unix_ms != 0U) {
        return Status{
            ErrorCode::protocol_error,
            "mutating durable command records must not contain an expiry"};
    }

    if (!record.canonical_receipt.empty()) {
        auto receipt = protocol::decode(record.canonical_receipt);
        if (!receipt || receipt.value().correlation_id != record.key.message_id ||
            receipt.value().sequence != record.key.sender_epoch) {
            return Status{ErrorCode::protocol_error,
                          "canonical receipt does not bind to its command key"};
        }
    }
    if (!record.canonical_result.empty()) {
        auto result = protocol::decode(record.canonical_result);
        if (!result || result.value().correlation_id != record.key.message_id ||
            result.value().sequence != record.key.sender_epoch ||
            result.value().message_id != record.result_message_id) {
            return Status{ErrorCode::protocol_error,
                          "canonical result does not bind to its command key"};
        }
        auto payload = protocol::decode_command_result(result.value().payload);
        if (!payload || payload.value().operation != record.operation ||
            payload.value().outcome != record.outcome) {
            return Status{ErrorCode::protocol_error,
                          "canonical result payload does not match its command record"};
        }
        if (record.operation ==
                protocol::CommandOperation::profile_status_set &&
            payload.value().outcome ==
                protocol::CommandOutcome::succeeded) {
            auto evidence = protocol::decode_profile_status_evidence(
                payload.value().body);
            if (!evidence ||
                !command.value().desired_profile_status.has_value() ||
                evidence.value().desired !=
                    *command.value().desired_profile_status ||
                evidence.value().observed !=
                    *command.value().desired_profile_status) {
                return Status{
                    ErrorCode::protocol_error,
                    "profile.status.set result does not prove the exact requested desired state"};
            }
        }
        if (record.operation == protocol::CommandOperation::update_stage &&
            payload.value().outcome ==
                protocol::CommandOutcome::succeeded) {
            auto evidence = protocol::decode_update_stage_evidence(
                payload.value().body);
            if (!evidence ||
                !command.value().expected_update_head.has_value() ||
                evidence.value().accepted_head !=
                    *command.value().expected_update_head) {
                return Status{
                    ErrorCode::protocol_error,
                    "update.stage result does not bind the exact requested accepted HEAD"};
            }
        }
    }

    const bool local_outgoing_terminal_without_result =
        record.direction == CommandDirection::outgoing &&
        (record.lifecycle == CommandLifecycle::cancelled ||
         record.lifecycle == CommandLifecycle::timed_out_unconfirmed ||
         (record.lifecycle == CommandLifecycle::expired &&
          record.request_schedule.attempts == 0U));
    if (command_lifecycle_terminal(record.lifecycle) &&
        record.canonical_result.empty() &&
        !local_outgoing_terminal_without_result) {
        return Status{ErrorCode::protocol_error,
                      "terminal durable command record has no frozen result"};
    }
    if (!record.canonical_result.empty() && record.result_message_id == 0U) {
        return Status{ErrorCode::protocol_error,
                      "durable command result is missing its message id"};
    }
    if (record.lifecycle == CommandLifecycle::cancelled &&
        (record.direction != CommandDirection::outgoing ||
         record.request_schedule.attempts != 0U ||
         !record.canonical_receipt.empty() ||
         !record.canonical_result.empty())) {
        return Status{ErrorCode::protocol_error,
                      "cancelled command contains evidence of peer-visible delivery"};
    }
    if (record.lifecycle == CommandLifecycle::timed_out_unconfirmed &&
        (record.direction != CommandDirection::outgoing ||
         record.request_schedule.attempts == 0U ||
         record.expiry_unix_ms == 0U ||
         !record.canonical_result.empty())) {
        return Status{ErrorCode::protocol_error,
                      "timed-out-unconfirmed command lacks an attempted expiring request"};
    }
    if (record.lifecycle == CommandLifecycle::expired &&
        record.direction == CommandDirection::outgoing &&
        record.canonical_result.empty() &&
        (record.request_schedule.attempts != 0U || record.expiry_unix_ms == 0U ||
         !record.canonical_receipt.empty())) {
        return Status{ErrorCode::protocol_error,
                      "locally expired command is not an unattempted expiring request"};
    }

    // Delivery state is directional. An outgoing record observes artifacts
    // received from its peer; an incoming record owns artifacts it may queue
    // back to that peer. Keeping those state spaces disjoint catches stale
    // cross-thread updates and prevents a local lane collision from being
    // mistaken for a valid protocol transition.
    if (record.direction == CommandDirection::outgoing) {
        if (record.receipt_schedule != CommandDeliverySchedule{} ||
            record.result_schedule != CommandDeliverySchedule{}) {
            return Status{ErrorCode::protocol_error,
                          "outgoing command owns a receiver-side delivery schedule"};
        }
        const bool receipt_valid =
            record.receipt_delivery == CommandDeliveryState::none ||
            record.receipt_delivery == CommandDeliveryState::observed;
        const bool result_valid =
            record.result_delivery == CommandDeliveryState::none ||
            record.result_delivery == CommandDeliveryState::observed;
        if (!receipt_valid || !result_valid) {
            return Status{ErrorCode::protocol_error,
                          "outgoing durable command has a sender-side delivery state"};
        }
        if ((!record.canonical_receipt.empty()) !=
                (record.receipt_delivery == CommandDeliveryState::observed) ||
            (!record.canonical_result.empty()) !=
                (record.result_delivery == CommandDeliveryState::observed)) {
            return Status{ErrorCode::protocol_error,
                          "outgoing durable command artifacts and observed states disagree"};
        }
    } else {
        if (record.request_schedule != CommandDeliverySchedule{}) {
            return Status{ErrorCode::protocol_error,
                          "incoming command owns a sender-side request schedule"};
        }
        const auto locally_owned = [](CommandDeliveryState state) {
            return state == CommandDeliveryState::pending ||
                   state == CommandDeliveryState::send_failed ||
                   state == CommandDeliveryState::queued ||
                   state == CommandDeliveryState::terminal_failure;
        };
        if (record.canonical_receipt.empty() ||
            !locally_owned(record.receipt_delivery) ||
            record.receipt_delivery == CommandDeliveryState::observed ||
            record.result_delivery == CommandDeliveryState::observed) {
            return Status{ErrorCode::protocol_error,
                          "incoming durable command receipt is not locally owned"};
        }
        if (record.canonical_result.empty()) {
            if (record.result_delivery != CommandDeliveryState::none) {
                return Status{ErrorCode::protocol_error,
                              "incoming durable command has result delivery without a result"};
            }
        } else if (!locally_owned(record.result_delivery)) {
            return Status{ErrorCode::protocol_error,
                          "incoming durable command result lacks a local delivery state"};
        }
    }
    return Status::success();
}

bool valid_delivery_transition(
    CommandDeliveryState before,
    CommandDeliveryState after) noexcept {
    if (before == after) {
        return true;
    }
    switch (before) {
        case CommandDeliveryState::none:
            return true;
        case CommandDeliveryState::pending:
            return after == CommandDeliveryState::send_failed ||
                   after == CommandDeliveryState::queued ||
                   after == CommandDeliveryState::terminal_failure ||
                   after == CommandDeliveryState::observed;
        case CommandDeliveryState::send_failed:
            return after == CommandDeliveryState::queued ||
                   after == CommandDeliveryState::terminal_failure;
        case CommandDeliveryState::queued:
        case CommandDeliveryState::observed:
            return false;
        case CommandDeliveryState::terminal_failure:
            // A non-retryable provider failure blocks automatic retry, but an
            // exact peer request replay is an explicit recovery trigger.
            return after == CommandDeliveryState::send_failed ||
                   after == CommandDeliveryState::queued;
    }
    return false;
}

bool valid_transition(
    const DurableCommandRecord &before,
    const DurableCommandRecord &after) noexcept {
    if (before.key != after.key || before.direction != after.direction ||
        before.operation != after.operation ||
        before.priority != after.priority ||
        before.clock_requirement != after.clock_requirement ||
        before.expiry_unix_ms != after.expiry_unix_ms ||
        before.canonical_request != after.canonical_request ||
        before.created_unix_ms != after.created_unix_ms) {
        return false;
    }
    if (!before.canonical_receipt.empty() &&
        before.canonical_receipt != after.canonical_receipt) {
        return false;
    }
    if (!before.canonical_result.empty() &&
        before.canonical_result != after.canonical_result) {
        return false;
    }
    if (!all_zero(before.peer_principal) &&
        before.peer_principal != after.peer_principal) {
        return false;
    }
    if (before.ownership_epoch != 0U &&
        before.ownership_epoch != after.ownership_epoch) {
        return false;
    }
    if (before.authority_sequence != 0U &&
        before.authority_sequence != after.authority_sequence) {
        return false;
    }
    if (before.result_message_id != 0U &&
        before.result_message_id != after.result_message_id) {
        return false;
    }
    if (before.correlation_id != 0U &&
        before.correlation_id != after.correlation_id) {
        return false;
    }
    const auto valid_schedule_transition = [](
        const CommandDeliverySchedule &old_schedule,
        const CommandDeliverySchedule &new_schedule) {
        if (new_schedule.attempts < old_schedule.attempts ||
            new_schedule.last_attempt_unix_ms < old_schedule.last_attempt_unix_ms ||
            new_schedule.next_attempt_unix_ms < old_schedule.next_attempt_unix_ms) {
            return false;
        }
        if (new_schedule.attempts == old_schedule.attempts &&
            new_schedule.last_attempt_unix_ms != old_schedule.last_attempt_unix_ms) {
            return false;
        }
        return true;
    };
    if (after.updated_unix_ms < before.updated_unix_ms ||
        !valid_schedule_transition(before.request_schedule, after.request_schedule) ||
        !valid_schedule_transition(before.receipt_schedule, after.receipt_schedule) ||
        !valid_schedule_transition(before.result_schedule, after.result_schedule) ||
        !valid_delivery_transition(
            before.receipt_delivery, after.receipt_delivery) ||
        !valid_delivery_transition(
            before.result_delivery, after.result_delivery)) {
        return false;
    }
    const bool resolves_uncertain_timeout =
        before.direction == CommandDirection::outgoing &&
        before.lifecycle == CommandLifecycle::timed_out_unconfirmed &&
        before.canonical_result.empty() &&
        !after.canonical_result.empty() &&
        after.result_delivery == CommandDeliveryState::observed &&
        (after.lifecycle == CommandLifecycle::succeeded ||
         after.lifecycle == CommandLifecycle::failed ||
         after.lifecycle == CommandLifecycle::expired);
    if (command_lifecycle_terminal(before.lifecycle) &&
        !resolves_uncertain_timeout &&
        (before.lifecycle != after.lifecycle || before.outcome != after.outcome)) {
        return false;
    }

    const auto rank = [](CommandLifecycle lifecycle) -> unsigned {
        switch (lifecycle) {
            case CommandLifecycle::reserved: return 1U;
            case CommandLifecycle::locally_queued: return 2U;
            case CommandLifecycle::received: return 3U;
            case CommandLifecycle::admitted: return 4U;
            case CommandLifecycle::started: return 5U;
            case CommandLifecycle::succeeded:
            case CommandLifecycle::failed:
            case CommandLifecycle::expired:
            case CommandLifecycle::cancelled:
            case CommandLifecycle::timed_out_unconfirmed:
                return 6U;
        }
        return 0U;
    };
    if (rank(after.lifecycle) < rank(before.lifecycle)) {
        return false;
    }
    if (before.direction == CommandDirection::incoming &&
        (after.lifecycle == CommandLifecycle::reserved ||
         after.lifecycle == CommandLifecycle::locally_queued)) {
        return false;
    }
    if (before.direction == CommandDirection::outgoing &&
        (after.lifecycle == CommandLifecycle::admitted ||
         after.lifecycle == CommandLifecycle::started)) {
        return false;
    }
    return true;
}

Result<std::vector<std::uint8_t>> encode_record(const DurableCommandRecord &record) {
    const Status valid = validate_record(record);
    if (!valid.ok()) {
        return valid;
    }
    const std::size_t total_size = kRecordHeaderBytesV3 +
        record.canonical_request.size() + record.canonical_receipt.size() +
        record.canonical_result.size();
    if (total_size > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command record is too large"};
    }

    std::vector<std::uint8_t> bytes;
    bytes.reserve(total_size);
    append_u32(bytes, static_cast<std::uint32_t>(total_size));
    bytes.push_back(kRecordFormatV3);
    bytes.push_back(static_cast<std::uint8_t>(record.direction));
    bytes.push_back(static_cast<std::uint8_t>(record.lifecycle));
    bytes.push_back(static_cast<std::uint8_t>(record.operation));
    bytes.push_back(static_cast<std::uint8_t>(record.outcome));
    bytes.push_back(static_cast<std::uint8_t>(record.receipt_delivery));
    bytes.push_back(static_cast<std::uint8_t>(record.result_delivery));
    bytes.push_back(static_cast<std::uint8_t>(record.priority));
    bytes.push_back(static_cast<std::uint8_t>(record.clock_requirement));
    bytes.insert(bytes.end(), 3U, 0U);
    bytes.insert(bytes.end(), record.key.peer_public_key.begin(),
                 record.key.peer_public_key.end());
    bytes.insert(bytes.end(), record.peer_principal.begin(),
                 record.peer_principal.end());
    append_u64(bytes, record.key.sender_epoch);
    append_u64(bytes, record.key.message_id);
    append_u64(bytes, record.correlation_id);
    append_u64(bytes, record.result_message_id);
    append_u64(bytes, record.ownership_epoch);
    append_u64(bytes, record.authority_sequence);
    append_u64(bytes, record.created_unix_ms);
    append_u64(bytes, record.updated_unix_ms);
    append_u64(bytes, record.expiry_unix_ms);
    const auto append_schedule = [&bytes](const CommandDeliverySchedule &schedule) {
        append_u32(bytes, schedule.attempts);
        append_u16(bytes, static_cast<std::uint16_t>(schedule.last_error_code));
        append_u16(bytes, 0U);
        append_u64(bytes, schedule.last_attempt_unix_ms);
        append_u64(bytes, schedule.next_attempt_unix_ms);
    };
    append_schedule(record.request_schedule);
    append_schedule(record.receipt_schedule);
    append_schedule(record.result_schedule);
    append_u32(bytes, static_cast<std::uint32_t>(record.canonical_request.size()));
    append_u32(bytes, static_cast<std::uint32_t>(record.canonical_receipt.size()));
    append_u32(bytes, static_cast<std::uint32_t>(record.canonical_result.size()));
    append_u32(bytes, 0U);
    if (bytes.size() != kRecordHeaderBytesV3) {
        return Status{ErrorCode::internal_error,
                      "durable command record header encoder drifted"};
    }
    bytes.insert(bytes.end(), record.canonical_request.begin(),
                 record.canonical_request.end());
    bytes.insert(bytes.end(), record.canonical_receipt.begin(),
                 record.canonical_receipt.end());
    bytes.insert(bytes.end(), record.canonical_result.begin(),
                 record.canonical_result.end());
    return bytes;
}

Result<DurableCommandRecord> decode_record_v3(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kRecordHeaderBytesV3 ||
        read_u32(bytes, 0U) != bytes.size() || bytes[4U] != kRecordFormatV3) {
        return Status{ErrorCode::protocol_error,
                      "durable command record header is malformed"};
    }
    if (!all_zero(bytes.subspan(13U, 3U)) ||
        read_u16(bytes, 158U) != 0U || read_u16(bytes, 182U) != 0U ||
        read_u16(bytes, 206U) != 0U || read_u32(bytes, 236U) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "durable command record reserved bytes are non-zero"};
    }
    DurableCommandRecord record;
    record.direction = static_cast<CommandDirection>(bytes[5U]);
    record.key.direction = record.direction;
    record.lifecycle = static_cast<CommandLifecycle>(bytes[6U]);
    record.operation = static_cast<protocol::CommandOperation>(bytes[7U]);
    record.outcome = static_cast<protocol::CommandOutcome>(bytes[8U]);
    record.receipt_delivery = static_cast<CommandDeliveryState>(bytes[9U]);
    record.result_delivery = static_cast<CommandDeliveryState>(bytes[10U]);
    record.priority = static_cast<CommandPriority>(bytes[11U]);
    record.clock_requirement = static_cast<CommandClockRequirement>(bytes[12U]);
    std::copy_n(bytes.begin() + 16U, record.key.peer_public_key.size(),
                record.key.peer_public_key.begin());
    std::copy_n(bytes.begin() + 48U, record.peer_principal.size(),
                record.peer_principal.begin());
    record.key.sender_epoch = read_u64(bytes, 80U);
    record.key.message_id = read_u64(bytes, 88U);
    record.correlation_id = read_u64(bytes, 96U);
    record.result_message_id = read_u64(bytes, 104U);
    record.ownership_epoch = read_u64(bytes, 112U);
    record.authority_sequence = read_u64(bytes, 120U);
    record.created_unix_ms = read_u64(bytes, 128U);
    record.updated_unix_ms = read_u64(bytes, 136U);
    record.expiry_unix_ms = read_u64(bytes, 144U);
    const auto read_schedule = [bytes](std::size_t offset) {
        CommandDeliverySchedule schedule;
        schedule.attempts = read_u32(bytes, offset);
        schedule.last_error_code = static_cast<ErrorCode>(read_u16(bytes, offset + 4U));
        schedule.last_attempt_unix_ms = read_u64(bytes, offset + 8U);
        schedule.next_attempt_unix_ms = read_u64(bytes, offset + 16U);
        return schedule;
    };
    record.request_schedule = read_schedule(152U);
    record.receipt_schedule = read_schedule(176U);
    record.result_schedule = read_schedule(200U);
    const std::size_t request_size = read_u32(bytes, 224U);
    const std::size_t receipt_size = read_u32(bytes, 228U);
    const std::size_t result_size = read_u32(bytes, 232U);
    if (request_size > kMaximumCanonicalFrameBytes ||
        receipt_size > kMaximumCanonicalFrameBytes ||
        result_size > kMaximumCanonicalFrameBytes ||
        kRecordHeaderBytesV3 + request_size + receipt_size + result_size != bytes.size()) {
        return Status{ErrorCode::protocol_error,
                      "durable command record frame lengths are invalid"};
    }
    std::size_t offset = kRecordHeaderBytesV3;
    record.canonical_request.assign(
        bytes.begin() + static_cast<std::ptrdiff_t>(offset),
        bytes.begin() + static_cast<std::ptrdiff_t>(offset + request_size));
    offset += request_size;
    record.canonical_receipt.assign(
        bytes.begin() + static_cast<std::ptrdiff_t>(offset),
        bytes.begin() + static_cast<std::ptrdiff_t>(offset + receipt_size));
    offset += receipt_size;
    record.canonical_result.assign(
        bytes.begin() + static_cast<std::ptrdiff_t>(offset), bytes.end());
    const Status valid = validate_record(record);
    if (!valid.ok()) {
        return Status{valid.code(),
                      "invalid durable command record: " + valid.message()};
    }
    return record;
}

Result<DurableCommandRecord> decode_record_v2(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kRecordHeaderBytesV2 ||
        read_u32(bytes, 0U) != bytes.size() || bytes[4U] != kRecordFormatV2 ||
        bytes[11U] != 0U || read_u16(bytes, 14U) != 0U ||
        !all_zero(bytes.subspan(160U, 8U))) {
        return Status{ErrorCode::protocol_error,
                      "legacy durable command record header is malformed"};
    }
    DurableCommandRecord record;
    record.direction = static_cast<CommandDirection>(bytes[5U]);
    record.key.direction = record.direction;
    record.lifecycle = static_cast<CommandLifecycle>(bytes[6U]);
    if (record.lifecycle > CommandLifecycle::expired) {
        return Status{ErrorCode::protocol_error,
                      "legacy durable command lifecycle is unknown"};
    }
    record.operation = static_cast<protocol::CommandOperation>(bytes[7U]);
    record.outcome = static_cast<protocol::CommandOutcome>(bytes[8U]);
    record.receipt_delivery = static_cast<CommandDeliveryState>(bytes[9U]);
    record.result_delivery = static_cast<CommandDeliveryState>(bytes[10U]);
    const ErrorCode legacy_error = static_cast<ErrorCode>(read_u16(bytes, 12U));
    const std::uint32_t legacy_attempts = read_u32(bytes, 16U);
    if (!valid_error_code(legacy_error)) {
        return Status{ErrorCode::protocol_error,
                      "legacy durable command send error is unknown"};
    }
    std::copy_n(bytes.begin() + 20U, record.key.peer_public_key.size(),
                record.key.peer_public_key.begin());
    std::copy_n(bytes.begin() + 52U, record.peer_principal.size(),
                record.peer_principal.begin());
    record.key.sender_epoch = read_u64(bytes, 84U);
    record.key.message_id = read_u64(bytes, 92U);
    record.correlation_id = read_u64(bytes, 100U);
    record.result_message_id = read_u64(bytes, 108U);
    record.ownership_epoch = read_u64(bytes, 116U);
    record.authority_sequence = read_u64(bytes, 124U);
    record.created_unix_ms = read_u64(bytes, 132U);
    record.updated_unix_ms = read_u64(bytes, 140U);
    const std::size_t request_size = read_u32(bytes, 148U);
    const std::size_t receipt_size = read_u32(bytes, 152U);
    const std::size_t result_size = read_u32(bytes, 156U);
    if (request_size > kMaximumCanonicalFrameBytes ||
        receipt_size > kMaximumCanonicalFrameBytes ||
        result_size > kMaximumCanonicalFrameBytes ||
        kRecordHeaderBytesV2 + request_size + receipt_size + result_size != bytes.size()) {
        return Status{ErrorCode::protocol_error,
                      "legacy durable command frame lengths are invalid"};
    }
    std::size_t offset = kRecordHeaderBytesV2;
    record.canonical_request.assign(
        bytes.begin() + static_cast<std::ptrdiff_t>(offset),
        bytes.begin() + static_cast<std::ptrdiff_t>(offset + request_size));
    offset += request_size;
    record.canonical_receipt.assign(
        bytes.begin() + static_cast<std::ptrdiff_t>(offset),
        bytes.begin() + static_cast<std::ptrdiff_t>(offset + receipt_size));
    offset += receipt_size;
    record.canonical_result.assign(
        bytes.begin() + static_cast<std::ptrdiff_t>(offset), bytes.end());

    auto request = protocol::decode(record.canonical_request);
    if (!request) {
        return request.status();
    }
    record.expiry_unix_ms = request.value().expiry_unix_ms;
    record.clock_requirement = record.expiry_unix_ms == 0U
        ? CommandClockRequirement::none
        : CommandClockRequirement::trusted_wall;
    const auto migrate_attempts = [&](CommandDeliverySchedule &schedule) {
        schedule.attempts = legacy_attempts;
        if (legacy_attempts != 0U) {
            schedule.last_error_code = legacy_error;
            schedule.last_attempt_unix_ms = record.updated_unix_ms;
        }
        schedule.next_attempt_unix_ms = record.updated_unix_ms;
    };
    if (record.direction == CommandDirection::outgoing) {
        migrate_attempts(record.request_schedule);
    } else if (record.direction == CommandDirection::incoming) {
        migrate_attempts(record.receipt_schedule);
        if (!record.canonical_result.empty() &&
            (record.result_delivery == CommandDeliveryState::pending ||
             record.result_delivery == CommandDeliveryState::send_failed)) {
            record.result_schedule.next_attempt_unix_ms = record.updated_unix_ms;
        }
    }
    const Status valid = validate_record(record);
    if (!valid.ok()) {
        return Status{valid.code(),
                      "invalid migrated durable command record: " + valid.message()};
    }
    return record;
}

Result<std::vector<std::uint8_t>> read_private_file(
    const std::filesystem::path &path,
    std::size_t maximum_file_bytes) {
    int descriptor = -1;
    do {
        descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        if (errno == ENOENT) {
            return Status{ErrorCode::not_found,
                          "durable command store does not exist: " + path.string()};
        }
        return file_status("unable to open durable command store", path);
    }

    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        const Status status = file_status("unable to inspect durable command store", path);
        (void)::close(descriptor);
        return status;
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      "durable command store must be a regular file owned by the running user: " +
                          path.string()};
    }
    if ((metadata.st_mode & (S_IRWXG | S_IRWXO)) != 0) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      "durable command store permissions must be 0600: " + path.string()};
    }
    if (metadata.st_size < static_cast<off_t>(kStoreHeaderBytes) ||
        static_cast<std::uintmax_t>(metadata.st_size) > maximum_file_bytes) {
        (void)::close(descriptor);
        return Status{ErrorCode::resource_exhausted,
                      "durable command store size is outside configured bounds"};
    }

    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(metadata.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            descriptor, bytes.data() + static_cast<std::ptrdiff_t>(offset),
            bytes.size() - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count < 0) {
            const Status status = file_status("unable to read durable command store", path);
            (void)::close(descriptor);
            return status;
        }
        if (count == 0) {
            (void)::close(descriptor);
            return Status{ErrorCode::io_error,
                          "durable command store ended before its recorded size"};
        }
        offset += static_cast<std::size_t>(count);
    }
    if (::close(descriptor) != 0) {
        return file_status("unable to close durable command store", path);
    }
    return bytes;
}

Result<std::vector<std::uint8_t>> encode_snapshot(
    const DurableCommandSnapshot &snapshot,
    const security::DeviceIdentity &identity) {
    if (snapshot.generation == 0U || snapshot.local_sender_epoch == 0U ||
        snapshot.records.size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::invalid_argument,
                      "durable command snapshot metadata is invalid"};
    }

    std::vector<std::uint8_t> body;
    for (const DurableCommandRecord &record : snapshot.records) {
        auto encoded = encode_record(record);
        if (!encoded) {
            return encoded.status();
        }
        body.insert(body.end(), encoded.value().begin(), encoded.value().end());
    }
    if (body.size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command store body is too large"};
    }

    std::vector<std::uint8_t> unsigned_message;
    unsigned_message.reserve(kUnsignedHeaderBytes + body.size());
    unsigned_message.insert(unsigned_message.end(), kStoreMagicV3.begin(), kStoreMagicV3.end());
    unsigned_message.push_back(kStoreFormatV3);
    unsigned_message.push_back(kSignatureAlgorithmEd25519);
    append_u16(unsigned_message, static_cast<std::uint16_t>(kStoreHeaderBytes));
    append_u32(unsigned_message, static_cast<std::uint32_t>(snapshot.records.size()));
    append_u64(unsigned_message, snapshot.generation);
    append_u64(unsigned_message, snapshot.local_sender_epoch);
    append_u32(unsigned_message, static_cast<std::uint32_t>(body.size()));
    append_u32(unsigned_message, 0U);
    unsigned_message.insert(unsigned_message.end(), identity.public_key().begin(),
                            identity.public_key().end());
    append_u64(unsigned_message, snapshot.clock_high_water_unix_ms);
    unsigned_message.insert(unsigned_message.end(), 32U, 0U);
    if (unsigned_message.size() != kUnsignedHeaderBytes) {
        return Status{ErrorCode::internal_error,
                      "durable command store header encoder drifted"};
    }
    unsigned_message.insert(unsigned_message.end(), body.begin(), body.end());

    auto signature = identity.sign(unsigned_message);
    if (!signature) {
        return signature.status();
    }
    std::vector<std::uint8_t> file;
    file.reserve(kStoreHeaderBytes + body.size());
    file.insert(file.end(), unsigned_message.begin(),
                unsigned_message.begin() + static_cast<std::ptrdiff_t>(kUnsignedHeaderBytes));
    file.insert(file.end(), signature.value().begin(), signature.value().end());
    file.insert(file.end(), body.begin(), body.end());
    return file;
}

Result<DurableCommandSnapshot> decode_snapshot(
    std::span<const std::uint8_t> bytes,
    const DurableCommandStore::Config &config,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    bool *migrated_legacy) {
    if (migrated_legacy != nullptr) {
        *migrated_legacy = false;
    }
    if (bytes.size() < kStoreHeaderBytes) {
        return Status{ErrorCode::protocol_error,
                      "durable command store header is unsupported"};
    }
    const bool is_v2 =
        std::equal(kStoreMagicV2.begin(), kStoreMagicV2.end(), bytes.begin()) &&
        bytes[8U] == kStoreFormatV2;
    const bool is_v3 =
        std::equal(kStoreMagicV3.begin(), kStoreMagicV3.end(), bytes.begin()) &&
        bytes[8U] == kStoreFormatV3;
    if ((!is_v2 && !is_v3) ||
        bytes[9U] != kSignatureAlgorithmEd25519 ||
        read_u16(bytes, 10U) != kStoreHeaderBytes) {
        return Status{ErrorCode::protocol_error,
                      "durable command store header is unsupported"};
    }
    const std::size_t record_count = read_u32(bytes, 12U);
    const std::uint64_t generation = read_u64(bytes, 16U);
    const std::uint64_t sender_epoch = read_u64(bytes, 24U);
    const std::size_t body_bytes = read_u32(bytes, 32U);
    const bool reserved_header_valid = read_u32(bytes, 36U) == 0U &&
        (is_v2
             ? all_zero(bytes.subspan(72U, 40U))
             : all_zero(bytes.subspan(80U, 32U)));
    if (!reserved_header_valid) {
        return Status{ErrorCode::protocol_error,
                      "durable command store reserved header bytes are non-zero"};
    }
    if (record_count > config.maximum_records || generation == 0U ||
        sender_epoch == 0U || body_bytes != bytes.size() - kStoreBodyOffset) {
        return Status{ErrorCode::protocol_error,
                      "durable command store counts or epochs are invalid"};
    }
    security::SigningPublicKey stored_device{};
    std::copy_n(bytes.begin() + 40U, stored_device.size(), stored_device.begin());
    if (stored_device != identity.public_key()) {
        return Status{ErrorCode::protocol_error,
                      "durable command store belongs to a different device identity"};
    }
    security::Signature signature{};
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(kStoreSignatureOffset),
                signature.size(), signature.begin());
    std::vector<std::uint8_t> signed_message;
    signed_message.reserve(kUnsignedHeaderBytes + body_bytes);
    signed_message.insert(signed_message.end(), bytes.begin(),
                          bytes.begin() + static_cast<std::ptrdiff_t>(kUnsignedHeaderBytes));
    signed_message.insert(signed_message.end(),
                          bytes.begin() + static_cast<std::ptrdiff_t>(kStoreBodyOffset),
                          bytes.end());
    const Status verified = sodium.verify_detached(
        signature, signed_message, identity.public_key());
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "durable command store signature is invalid"};
    }

    DurableCommandSnapshot snapshot;
    snapshot.generation = generation;
    snapshot.local_sender_epoch = sender_epoch;
    snapshot.clock_high_water_unix_ms = is_v3 ? read_u64(bytes, 72U) : 0U;
    const std::uint64_t encoded_clock_high_water =
        snapshot.clock_high_water_unix_ms;
    std::uint64_t record_clock_high_water = 0U;
    snapshot.records.reserve(record_count);
    std::size_t offset = kStoreBodyOffset;
    for (std::size_t index = 0U; index < record_count; ++index) {
        const std::size_t record_header_bytes =
            is_v2 ? kRecordHeaderBytesV2 : kRecordHeaderBytesV3;
        if (bytes.size() - offset < record_header_bytes) {
            return Status{ErrorCode::protocol_error,
                          "durable command store ended inside a record header"};
        }
        const std::size_t record_bytes = read_u32(bytes, offset);
        if (record_bytes < record_header_bytes || record_bytes > bytes.size() - offset) {
            return Status{ErrorCode::protocol_error,
                          "durable command store record length is invalid"};
        }
        auto record = is_v2
            ? decode_record_v2(bytes.subspan(offset, record_bytes))
            : decode_record_v3(bytes.subspan(offset, record_bytes));
        if (!record) {
            return record.status();
        }
        snapshot.records.push_back(std::move(record).value());
        record_clock_high_water = std::max(
            record_clock_high_water,
            std::max(snapshot.records.back().created_unix_ms,
                     snapshot.records.back().updated_unix_ms));
        offset += record_bytes;
    }
    if (offset != bytes.size()) {
        return Status{ErrorCode::protocol_error,
                      "durable command store contains unclaimed trailing bytes"};
    }
    if (!std::is_sorted(
            snapshot.records.begin(), snapshot.records.end(),
            [](const DurableCommandRecord &left, const DurableCommandRecord &right) {
                return left.key < right.key;
            })) {
        return Status{ErrorCode::protocol_error,
                      "durable command store records are not in canonical key order"};
    }
    for (std::size_t index = 1U; index < snapshot.records.size(); ++index) {
        if (snapshot.records[index - 1U].key == snapshot.records[index].key) {
            return Status{ErrorCode::protocol_error,
                          "durable command store contains a duplicate key"};
        }
    }
    const Status quotas = validate_snapshot_quotas(snapshot.records, config);
    if (!quotas.ok()) {
        return quotas;
    }
    if (is_v3 && encoded_clock_high_water < record_clock_high_water) {
        return Status{ErrorCode::protocol_error,
                      "durable command clock high-water mark trails record history"};
    }
    if (is_v2) {
        snapshot.clock_high_water_unix_ms = record_clock_high_water;
    }
    if (migrated_legacy != nullptr) {
        *migrated_legacy = is_v2;
    }
    return snapshot;
}

void sort_records(std::vector<DurableCommandRecord> &records) {
    std::sort(records.begin(), records.end(),
              [](const DurableCommandRecord &left, const DurableCommandRecord &right) {
                  return left.key < right.key;
              });
}

std::vector<DurableCommandRecord>::iterator find_record(
    std::vector<DurableCommandRecord> &records,
    const DurableCommandKey &key) {
    return std::lower_bound(
        records.begin(), records.end(), key,
        [](const DurableCommandRecord &record, const DurableCommandKey &candidate) {
            return record.key < candidate;
        });
}

std::vector<DurableCommandRecord>::const_iterator find_record(
    const std::vector<DurableCommandRecord> &records,
    const DurableCommandKey &key) {
    return std::lower_bound(
        records.begin(), records.end(), key,
        [](const DurableCommandRecord &record, const DurableCommandKey &candidate) {
            return record.key < candidate;
        });
}

bool prune_oldest_terminal(std::vector<DurableCommandRecord> &records,
                           bool retain_mutating_effect_history) {
    auto oldest = records.end();
    for (auto current = records.begin(); current != records.end(); ++current) {
        if (command_record_unfinished(*current)) {
            continue;
        }
        if (retain_mutating_effect_history &&
            command_record_has_effect_identity(*current)) {
            continue;
        }
        if (oldest == records.end() ||
            current->updated_unix_ms < oldest->updated_unix_ms) {
            oldest = current;
        }
    }
    if (oldest == records.end()) {
        return false;
    }
    records.erase(oldest);
    return true;
}

Status validate_pending_quotas(
    const std::vector<DurableCommandRecord> &records,
    const DurableCommandRecord &addition,
    const DurableCommandStore::Config &config) {
    if (!command_record_unfinished(addition)) {
        return Status::success();
    }
    std::size_t pending_total = 0U;
    std::size_t pending_for_peer = 0U;
    std::size_t bytes_for_peer = 0U;
    for (const DurableCommandRecord &record : records) {
        if (!command_record_unfinished(record)) {
            continue;
        }
        ++pending_total;
        if (record.key.peer_public_key == addition.key.peer_public_key &&
            record.direction == addition.direction) {
            ++pending_for_peer;
            bytes_for_peer += command_record_canonical_bytes(record);
        }
    }
    if (pending_total >= config.maximum_pending_records) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command unfinished-record quota is exhausted"};
    }
    if (pending_for_peer >= config.maximum_pending_per_peer) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command per-peer unfinished-record quota is exhausted"};
    }
    const std::size_t addition_bytes = command_record_canonical_bytes(addition);
    if (addition_bytes > config.maximum_bytes_per_peer ||
        bytes_for_peer > config.maximum_bytes_per_peer - addition_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command per-peer canonical-byte quota is exhausted"};
    }
    return Status::success();
}

Status validate_snapshot_quotas(
    const std::vector<DurableCommandRecord> &records,
    const DurableCommandStore::Config &config) {
    std::vector<DurableCommandRecord> accepted;
    accepted.reserve(records.size());
    for (const DurableCommandRecord &record : records) {
        const Status valid = validate_pending_quotas(accepted, record, config);
        if (!valid.ok()) {
            return Status{
                valid.code(),
                "durable command store exceeds configured unfinished-work quotas: " +
                    valid.message()};
        }
        accepted.push_back(record);
    }
    return Status::success();
}

}  // namespace

Result<std::unique_ptr<DurableCommandStore>> DurableCommandStore::open(
    Config config,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (config.path.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "durable command store path is empty"};
    }
    if (config.maximum_records == 0U ||
        config.maximum_records > kDefaultMaximumCommandRecords ||
        config.maximum_file_bytes < kStoreHeaderBytes ||
        config.maximum_file_bytes > kDefaultMaximumCommandStoreBytes ||
        config.maximum_pending_records == 0U ||
        config.maximum_pending_records > kDefaultMaximumCommandRecords ||
        config.maximum_pending_per_peer == 0U ||
        config.maximum_pending_per_peer > kDefaultMaximumCommandRecords ||
        config.maximum_bytes_per_peer == 0U ||
        config.maximum_bytes_per_peer > config.maximum_file_bytes) {
        return Status{ErrorCode::invalid_argument,
                      "durable command store limits are outside supported bounds"};
    }
    auto store = std::unique_ptr<DurableCommandStore>(
        new DurableCommandStore(std::move(config), identity, sodium));
    const Status loaded = store->load_or_create();
    if (!loaded.ok()) {
        return loaded;
    }
    return store;
}

Status DurableCommandStore::load_or_create() {
    auto bytes = read_private_file(config_.path, config_.maximum_file_bytes);
    if (!bytes && bytes.status().code() != ErrorCode::not_found) {
        return bytes.status();
    }
    if (bytes) {
        bool migrated_legacy = false;
        auto decoded = decode_snapshot(
            bytes.value(), config_, *identity_, *sodium_, &migrated_legacy);
        if (!decoded) {
            return decoded.status();
        }
        DurableCommandSnapshot candidate = std::move(decoded).value();
        if (migrated_legacy) {
            ++candidate.generation;
            if (candidate.generation == 0U) {
                return Status{ErrorCode::resource_exhausted,
                              "durable command store generation exhausted during migration"};
            }
            const Status stored = persist(candidate);
            if (!stored.ok()) {
                return Status{stored.code(),
                              "unable to commit durable command store v3 migration: " +
                                  stored.message()};
            }
        }
        snapshot_ = std::move(candidate);
        return Status::success();
    }

    auto epoch = security::random_u64_nonzero();
    if (!epoch) {
        return epoch.status();
    }
    DurableCommandSnapshot candidate;
    candidate.generation = 1U;
    candidate.local_sender_epoch = epoch.value();
    const Status stored = persist(candidate);
    if (!stored.ok()) {
        return stored;
    }
    snapshot_ = std::move(candidate);
    return Status::success();
}

Status DurableCommandStore::persist(
    const DurableCommandSnapshot &candidate) const {
    auto encoded = encode_snapshot(candidate, *identity_);
    if (!encoded) {
        return encoded.status();
    }
    if (encoded.value().size() > config_.maximum_file_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command store exceeds its configured file bound"};
    }
    return StateStore::write_atomic(config_.path, encoded.value());
}

DurableCommandSnapshot DurableCommandStore::snapshot() const {
    std::scoped_lock lock(mutex_);
    return snapshot_;
}

std::uint64_t DurableCommandStore::local_sender_epoch() const {
    std::scoped_lock lock(mutex_);
    return snapshot_.local_sender_epoch;
}

std::uint64_t DurableCommandStore::clock_high_water_unix_ms() const {
    std::scoped_lock lock(mutex_);
    return snapshot_.clock_high_water_unix_ms;
}

Result<std::optional<DurableCommandRecord>> DurableCommandStore::find(
    const DurableCommandKey &key) const {
    if (!valid_direction(key.direction) || all_zero(key.peer_public_key) ||
        key.sender_epoch == 0U ||
        key.message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "durable command lookup key is incomplete"};
    }
    std::scoped_lock lock(mutex_);
    const auto found = find_record(snapshot_.records, key);
    if (found == snapshot_.records.end() || found->key != key) {
        return std::optional<DurableCommandRecord>{};
    }
    return std::optional<DurableCommandRecord>{*found};
}

std::vector<DurableCommandRecord> DurableCommandStore::records_for_peer(
    const CommandPeerKey &peer_public_key,
    CommandDirection direction) const {
    std::vector<DurableCommandRecord> records;
    std::scoped_lock lock(mutex_);
    for (const DurableCommandRecord &record : snapshot_.records) {
        if (record.key.peer_public_key == peer_public_key &&
            record.key.direction == direction) {
            records.push_back(record);
        }
    }
    std::sort(records.begin(), records.end(),
              [](const DurableCommandRecord &left, const DurableCommandRecord &right) {
                  if (left.updated_unix_ms != right.updated_unix_ms) {
                      return left.updated_unix_ms > right.updated_unix_ms;
                  }
                  return left.key.message_id > right.key.message_id;
              });
    return records;
}

Result<CommandInsertDisposition> DurableCommandStore::insert(
    const DurableCommandRecord &record) {
    const Status valid = validate_record(record);
    if (!valid.ok()) {
        return valid;
    }
    std::scoped_lock lock(mutex_);
    const auto found = find_record(snapshot_.records, record.key);
    if (found != snapshot_.records.end() && found->key == record.key) {
        return found->canonical_request == record.canonical_request
            ? CommandInsertDisposition::exact_duplicate
            : CommandInsertDisposition::conflicting_reuse;
    }

    const Status quota_status = validate_pending_quotas(
        snapshot_.records, record, config_);
    if (!quota_status.ok()) {
        return quota_status;
    }

    DurableCommandSnapshot candidate = snapshot_;
    while (candidate.records.size() >= config_.maximum_records) {
        if (!prune_oldest_terminal(
                candidate.records,
                config_.retain_mutating_effect_history)) {
            return Status{ErrorCode::resource_exhausted,
                          "durable command store contains no prunable terminal record"};
        }
    }
    candidate.records.push_back(record);
    sort_records(candidate.records);
    candidate.clock_high_water_unix_ms = std::max(
        candidate.clock_high_water_unix_ms,
        std::max(record.created_unix_ms, record.updated_unix_ms));
    ++candidate.generation;
    if (candidate.generation == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command store generation exhausted"};
    }
    const Status stored = persist(candidate);
    if (!stored.ok()) {
        return stored;
    }
    snapshot_ = std::move(candidate);
    return CommandInsertDisposition::inserted;
}

Status DurableCommandStore::update(const DurableCommandRecord &record) {
    const Status valid = validate_record(record);
    if (!valid.ok()) {
        return valid;
    }
    std::scoped_lock lock(mutex_);
    const auto found = find_record(snapshot_.records, record.key);
    if (found == snapshot_.records.end() || found->key != record.key) {
        return Status{ErrorCode::not_found,
                      "durable command update key does not exist"};
    }
    if (!valid_transition(*found, record)) {
        return Status{ErrorCode::protocol_error,
                      "durable command update violates immutable fields or lifecycle order"};
    }
    if (*found == record) {
        return Status::success();
    }

    std::vector<DurableCommandRecord> quota_records = snapshot_.records;
    const auto quota_existing = find_record(quota_records, record.key);
    quota_records.erase(quota_existing);
    const Status quota_status = validate_pending_quotas(
        quota_records, record, config_);
    if (!quota_status.ok()) {
        return quota_status;
    }

    DurableCommandSnapshot candidate = snapshot_;
    auto replacement = find_record(candidate.records, record.key);
    *replacement = record;
    candidate.clock_high_water_unix_ms = std::max(
        candidate.clock_high_water_unix_ms,
        std::max(record.created_unix_ms, record.updated_unix_ms));
    ++candidate.generation;
    if (candidate.generation == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command store generation exhausted"};
    }
    const Status stored = persist(candidate);
    if (!stored.ok()) {
        return stored;
    }
    snapshot_ = std::move(candidate);
    return Status::success();
}

Status DurableCommandStore::checkpoint_clock_high_water(
    std::uint64_t now_unix_ms) {
    if (now_unix_ms == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "durable command clock checkpoint is zero"};
    }
    std::scoped_lock lock(mutex_);
    if (now_unix_ms <= snapshot_.clock_high_water_unix_ms) {
        return Status::success();
    }
    DurableCommandSnapshot candidate = snapshot_;
    candidate.clock_high_water_unix_ms = now_unix_ms;
    ++candidate.generation;
    if (candidate.generation == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command store generation exhausted"};
    }
    const Status stored = persist(candidate);
    if (!stored.ok()) {
        return stored;
    }
    snapshot_ = std::move(candidate);
    return Status::success();
}

Result<DurableCommandRecord> DurableCommandStore::cancel_before_start(
    const DurableCommandKey &key,
    std::uint64_t now_unix_ms) {
    if (now_unix_ms == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "command cancellation timestamp is zero"};
    }
    std::scoped_lock lock(mutex_);
    const auto found = find_record(snapshot_.records, key);
    if (found == snapshot_.records.end() || found->key != key) {
        return Status{ErrorCode::not_found,
                      "durable command cancellation key does not exist"};
    }
    if (found->direction != CommandDirection::outgoing ||
        found->lifecycle != CommandLifecycle::reserved ||
        found->request_schedule.attempts != 0U) {
        return Status{ErrorCode::unavailable,
                      "command cancellation is only safe before its first committed attempt"};
    }

    DurableCommandSnapshot candidate = snapshot_;
    auto replacement = find_record(candidate.records, key);
    replacement->lifecycle = CommandLifecycle::cancelled;
    replacement->updated_unix_ms = std::max(now_unix_ms, replacement->updated_unix_ms);
    candidate.clock_high_water_unix_ms = std::max(
        candidate.clock_high_water_unix_ms, replacement->updated_unix_ms);
    const Status valid = validate_record(*replacement);
    if (!valid.ok() || !valid_transition(*found, *replacement)) {
        return valid.ok()
            ? Status{ErrorCode::protocol_error,
                     "command cancellation violates lifecycle invariants"}
            : valid;
    }
    ++candidate.generation;
    if (candidate.generation == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "durable command store generation exhausted"};
    }
    const Status stored = persist(candidate);
    if (!stored.ok()) {
        return stored;
    }
    DurableCommandRecord cancelled = *replacement;
    snapshot_ = std::move(candidate);
    return cancelled;
}

std::filesystem::path default_command_store_path(
    const std::filesystem::path &tox_savedata_path) {
    if (tox_savedata_path.empty()) {
        return {};
    }
    const std::filesystem::path parent = tox_savedata_path.has_parent_path()
        ? tox_savedata_path.parent_path()
        : std::filesystem::path{"."};
    return parent / "commands.store";
}

bool command_lifecycle_terminal(CommandLifecycle lifecycle) noexcept {
    return lifecycle == CommandLifecycle::succeeded ||
           lifecycle == CommandLifecycle::failed ||
           lifecycle == CommandLifecycle::expired ||
           lifecycle == CommandLifecycle::cancelled ||
           lifecycle == CommandLifecycle::timed_out_unconfirmed;
}

bool command_lifecycle_locally_terminal(CommandLifecycle lifecycle) noexcept {
    return lifecycle == CommandLifecycle::cancelled ||
           lifecycle == CommandLifecycle::timed_out_unconfirmed;
}

bool command_record_unfinished(
    const DurableCommandRecord &record) noexcept {
    if (!command_lifecycle_terminal(record.lifecycle)) {
        return true;
    }
    if (record.direction == CommandDirection::outgoing) {
        return false;
    }
    return record.receipt_delivery != CommandDeliveryState::queued ||
           record.result_delivery != CommandDeliveryState::queued;
}

bool command_record_has_effect_identity(
    const DurableCommandRecord &record) noexcept {
    if (record.direction != CommandDirection::incoming ||
        record.key.direction != CommandDirection::incoming) {
        return false;
    }
    const auto policy =
        protocol::command_operation_policy(record.operation);
    if (!policy || policy->read_only) return false;
    if (record.lifecycle == CommandLifecycle::started) return true;
    return command_lifecycle_terminal(record.lifecycle) &&
        !std::all_of(record.peer_principal.begin(),
                     record.peer_principal.end(),
                     [](std::uint8_t byte) { return byte == 0U; }) &&
        record.ownership_epoch != 0U && record.authority_sequence != 0U;
}

Result<security::Digest> command_effect_frontier_digest(
    const DurableCommandSnapshot &snapshot,
    const security::Sodium &sodium) {
    std::vector<const DurableCommandRecord *> effects;
    effects.reserve(snapshot.records.size());
    for (const DurableCommandRecord &record : snapshot.records) {
        if (!command_record_has_effect_identity(record)) continue;
        const Status valid = validate_record(record);
        if (!valid.ok()) return valid;
        effects.push_back(&record);
    }
    std::sort(effects.begin(), effects.end(),
              [](const DurableCommandRecord *left,
                 const DurableCommandRecord *right) {
                  return left->key < right->key;
              });
    if (effects.size() >
        static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
        return Status{ErrorCode::resource_exhausted,
                      "command effect frontier contains too many identities"};
    }
    std::vector<std::uint8_t> material;
    constexpr std::string_view header{"iotox-command-effect-frontier-v1\n"};
    material.insert(material.end(), header.begin(), header.end());
    const auto append_u32 = [&material](std::uint32_t value) {
        material.push_back(static_cast<std::uint8_t>(value >> 24U));
        material.push_back(static_cast<std::uint8_t>(value >> 16U));
        material.push_back(static_cast<std::uint8_t>(value >> 8U));
        material.push_back(static_cast<std::uint8_t>(value));
    };
    const auto append_u64 = [&material](std::uint64_t value) {
        for (std::size_t index = 0U; index < 8U; ++index) {
            material.push_back(static_cast<std::uint8_t>(
                value >> ((7U - index) * 8U)));
        }
    };
    append_u32(static_cast<std::uint32_t>(effects.size()));
    for (const DurableCommandRecord *record : effects) {
        material.insert(material.end(), record->key.peer_public_key.begin(),
                        record->key.peer_public_key.end());
        append_u64(record->key.sender_epoch);
        append_u64(record->key.message_id);
        material.push_back(static_cast<std::uint8_t>(record->operation));
        material.insert(material.end(), record->peer_principal.begin(),
                        record->peer_principal.end());
        append_u64(record->ownership_epoch);
        append_u64(record->authority_sequence);
        if (record->canonical_request.size() >
            static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
            return Status{ErrorCode::resource_exhausted,
                          "command effect request is too large to commit"};
        }
        append_u32(static_cast<std::uint32_t>(
            record->canonical_request.size()));
        material.insert(material.end(), record->canonical_request.begin(),
                        record->canonical_request.end());
    }
    return sodium.hash("iotox-command-effect-frontier-v1", material);
}

bool command_clock_within_rollback_tolerance(
    std::uint64_t high_water_unix_ms,
    std::uint64_t now_unix_ms,
    std::uint64_t tolerance_ms) noexcept {
    return high_water_unix_ms <= now_unix_ms ||
           high_water_unix_ms - now_unix_ms <= tolerance_ms;
}

CommandDeliverySchedule &command_delivery_schedule(
    DurableCommandRecord &record,
    CommandArtifact artifact) {
    switch (artifact) {
        case CommandArtifact::request: return record.request_schedule;
        case CommandArtifact::receipt: return record.receipt_schedule;
        case CommandArtifact::result: return record.result_schedule;
    }
    return record.request_schedule;
}

const CommandDeliverySchedule &command_delivery_schedule(
    const DurableCommandRecord &record,
    CommandArtifact artifact) {
    switch (artifact) {
        case CommandArtifact::request: return record.request_schedule;
        case CommandArtifact::receipt: return record.receipt_schedule;
        case CommandArtifact::result: return record.result_schedule;
    }
    return record.request_schedule;
}

std::size_t command_record_canonical_bytes(
    const DurableCommandRecord &record) noexcept {
    return record.canonical_request.size() + record.canonical_receipt.size() +
           record.canonical_result.size();
}

bool command_artifact_due(
    const DurableCommandRecord &record,
    CommandArtifact artifact,
    std::uint64_t now_unix_ms) noexcept {
    const CommandDeliverySchedule &schedule =
        command_delivery_schedule(record, artifact);
    const bool schedule_due = schedule.next_attempt_unix_ms == 0U ||
        schedule.next_attempt_unix_ms <= now_unix_ms;
    if (!schedule_due) {
        return false;
    }
    switch (artifact) {
        case CommandArtifact::request:
            return record.direction == CommandDirection::outgoing &&
                   !command_lifecycle_terminal(record.lifecycle) &&
                   record.receipt_delivery != CommandDeliveryState::observed &&
                   record.result_delivery != CommandDeliveryState::observed;
        case CommandArtifact::receipt:
            return record.direction == CommandDirection::incoming &&
                (record.receipt_delivery == CommandDeliveryState::pending ||
                 record.receipt_delivery == CommandDeliveryState::send_failed);
        case CommandArtifact::result:
            return record.direction == CommandDirection::incoming &&
                   !record.canonical_result.empty() &&
                (record.result_delivery == CommandDeliveryState::pending ||
                 record.result_delivery == CommandDeliveryState::send_failed);
    }
    return false;
}

Status begin_command_delivery_attempt(
    DurableCommandRecord &record,
    CommandArtifact artifact,
    std::uint64_t now_unix_ms,
    const CommandRetryPolicy &policy,
    bool force_replay) {
    if (now_unix_ms == 0U || now_unix_ms < record.created_unix_ms ||
        policy.base_delay_ms == 0U ||
        policy.maximum_delay_ms < policy.base_delay_ms) {
        return Status{ErrorCode::invalid_argument,
                      "command delivery attempt timing policy is invalid"};
    }
    const auto explicitly_replayable = [](CommandDeliveryState state) {
        return state == CommandDeliveryState::pending ||
               state == CommandDeliveryState::send_failed ||
               state == CommandDeliveryState::queued ||
               state == CommandDeliveryState::terminal_failure;
    };
    const bool replayable_owned_artifact = force_replay &&
        record.direction == CommandDirection::incoming &&
        ((artifact == CommandArtifact::receipt &&
          explicitly_replayable(record.receipt_delivery)) ||
         (artifact == CommandArtifact::result &&
          explicitly_replayable(record.result_delivery)));
    if (!command_artifact_due(record, artifact, now_unix_ms) &&
        !replayable_owned_artifact) {
        return Status{ErrorCode::unavailable,
                      "command artifact is not due for delivery"};
    }
    CommandDeliverySchedule &schedule =
        command_delivery_schedule(record, artifact);
    const std::uint64_t previous_next_attempt_unix_ms =
        schedule.next_attempt_unix_ms;
    if (schedule.attempts == std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "command delivery attempt counter is exhausted"};
    }
    ++schedule.attempts;
    schedule.last_error_code = ErrorCode::ok;
    schedule.last_attempt_unix_ms = now_unix_ms;

    std::uint64_t delay = policy.base_delay_ms;
    for (std::uint32_t index = 1U;
         index < schedule.attempts && delay < policy.maximum_delay_ms;
         ++index) {
        delay = delay > policy.maximum_delay_ms / 2U
            ? policy.maximum_delay_ms
            : std::min(policy.maximum_delay_ms, delay * 2U);
    }
    std::uint64_t hash = 1469598103934665603ULL;
    const auto mix = [&hash](std::uint8_t byte) {
        hash ^= byte;
        hash *= 1099511628211ULL;
    };
    for (const std::uint8_t byte : record.key.peer_public_key) {
        mix(byte);
    }
    for (unsigned shift = 0U; shift < 64U; shift += 8U) {
        mix(static_cast<std::uint8_t>((record.key.sender_epoch >> shift) & 0xFFU));
        mix(static_cast<std::uint8_t>((record.key.message_id >> shift) & 0xFFU));
    }
    mix(static_cast<std::uint8_t>(artifact));
    for (unsigned shift = 0U; shift < 32U; shift += 8U) {
        mix(static_cast<std::uint8_t>((schedule.attempts >> shift) & 0xFFU));
    }
    const std::uint64_t jitter_bound = delay / 4U;
    const std::uint64_t jitter = jitter_bound == 0U
        ? 0U
        : hash % (jitter_bound + 1U);
    const std::uint64_t total_delay =
        delay > std::numeric_limits<std::uint64_t>::max() - jitter
        ? std::numeric_limits<std::uint64_t>::max()
        : delay + jitter;
    const std::uint64_t computed_next_attempt_unix_ms =
        now_unix_ms > std::numeric_limits<std::uint64_t>::max() - total_delay
        ? std::numeric_limits<std::uint64_t>::max()
        : now_unix_ms + total_delay;
    schedule.next_attempt_unix_ms = std::max(
        previous_next_attempt_unix_ms, computed_next_attempt_unix_ms);
    record.updated_unix_ms = std::max(record.updated_unix_ms, now_unix_ms);
    if (artifact == CommandArtifact::request &&
        record.lifecycle == CommandLifecycle::reserved) {
        record.lifecycle = CommandLifecycle::locally_queued;
    }
    return Status::success();
}

std::vector<DurableCommandRecord> order_command_outbox(
    std::vector<DurableCommandRecord> records) {
    const auto next_due = [](const DurableCommandRecord &record) {
        std::uint64_t next = std::numeric_limits<std::uint64_t>::max();
        const auto consider = [&next](
            bool active, const CommandDeliverySchedule &schedule) {
            if (active) {
                next = std::min(next, schedule.next_attempt_unix_ms);
            }
        };
        consider(record.direction == CommandDirection::outgoing &&
                     !command_lifecycle_terminal(record.lifecycle) &&
                     record.receipt_delivery != CommandDeliveryState::observed &&
                     record.result_delivery != CommandDeliveryState::observed,
                 record.request_schedule);
        consider(record.direction == CommandDirection::incoming &&
                     (record.receipt_delivery == CommandDeliveryState::pending ||
                      record.receipt_delivery == CommandDeliveryState::send_failed),
                 record.receipt_schedule);
        consider(record.direction == CommandDirection::incoming &&
                     !record.canonical_result.empty() &&
                     (record.result_delivery == CommandDeliveryState::pending ||
                      record.result_delivery == CommandDeliveryState::send_failed),
                 record.result_schedule);
        return next;
    };
    std::sort(records.begin(), records.end(), [&](
        const DurableCommandRecord &left,
        const DurableCommandRecord &right) {
        if (left.priority != right.priority) {
            return left.priority > right.priority;
        }
        const std::uint64_t left_due = next_due(left);
        const std::uint64_t right_due = next_due(right);
        if (left_due != right_due) {
            return left_due < right_due;
        }
        if (left.created_unix_ms != right.created_unix_ms) {
            return left.created_unix_ms < right.created_unix_ms;
        }
        return left.key < right.key;
    });
    return records;
}

std::string to_string(CommandDirection direction) {
    switch (direction) {
        case CommandDirection::incoming: return "incoming";
        case CommandDirection::outgoing: return "outgoing";
    }
    return "unknown";
}

std::string to_string(CommandLifecycle lifecycle) {
    switch (lifecycle) {
        case CommandLifecycle::reserved: return "reserved";
        case CommandLifecycle::locally_queued: return "locally-queued";
        case CommandLifecycle::received: return "received";
        case CommandLifecycle::admitted: return "admitted";
        case CommandLifecycle::started: return "started";
        case CommandLifecycle::succeeded: return "succeeded";
        case CommandLifecycle::failed: return "failed";
        case CommandLifecycle::expired: return "expired";
        case CommandLifecycle::cancelled: return "cancelled";
        case CommandLifecycle::timed_out_unconfirmed: return "timed-out-unconfirmed";
    }
    return "unknown";
}

std::string to_string(CommandPriority priority) {
    switch (priority) {
        case CommandPriority::low: return "low";
        case CommandPriority::normal: return "normal";
        case CommandPriority::high: return "high";
    }
    return "unknown";
}

std::string to_string(CommandClockRequirement requirement) {
    switch (requirement) {
        case CommandClockRequirement::none: return "none";
        case CommandClockRequirement::trusted_wall: return "trusted-wall";
    }
    return "unknown";
}

std::string to_string(CommandArtifact artifact) {
    switch (artifact) {
        case CommandArtifact::request: return "request";
        case CommandArtifact::receipt: return "receipt";
        case CommandArtifact::result: return "result";
    }
    return "unknown";
}

std::string to_string(CommandDeliveryState state) {
    switch (state) {
        case CommandDeliveryState::none: return "none";
        case CommandDeliveryState::pending: return "pending";
        case CommandDeliveryState::send_failed: return "send-failed";
        case CommandDeliveryState::queued: return "queued";
        case CommandDeliveryState::terminal_failure: return "terminal-failure";
        case CommandDeliveryState::observed: return "observed";
    }
    return "unknown";
}

std::string render_command_record(const DurableCommandRecord &record) {
    std::ostringstream output;
    output << "direction=" << to_string(record.key.direction) << '\n'
           << "peer=" << security::hex(record.key.peer_public_key) << '\n'
           << "sender-epoch=" << record.key.sender_epoch << '\n'
           << "message-id=" << record.key.message_id << '\n'
           << "lifecycle=" << to_string(record.lifecycle) << '\n'
           << "operation=" << protocol::to_string(record.operation) << '\n'
           << "outcome=" << protocol::to_string(record.outcome) << '\n'
           << "peer-principal=" << security::hex(record.peer_principal) << '\n'
           << "ownership-epoch=" << record.ownership_epoch << '\n'
           << "authority-sequence=" << record.authority_sequence << '\n'
           << "correlation-id=" << record.correlation_id << '\n'
           << "result-message-id=" << record.result_message_id << '\n'
           << "receipt-delivery=" << to_string(record.receipt_delivery) << '\n'
           << "result-delivery=" << to_string(record.result_delivery) << '\n'
           << "priority=" << to_string(record.priority) << '\n'
           << "clock-requirement=" << to_string(record.clock_requirement) << '\n'
           << "expiry-unix-ms=" << record.expiry_unix_ms << '\n';
    auto request_frame = protocol::decode(record.canonical_request);
    if (request_frame) {
        auto request = protocol::decode_command_request(
            request_frame.value().payload);
        if (request && request.value().desired_profile_status.has_value()) {
            output << "desired-status=" << protocol::to_string(
                *request.value().desired_profile_status) << '\n';
        }
        if (request && request.value().expected_update_head.has_value()) {
            output << "expected-update-head=" << security::hex(
                *request.value().expected_update_head) << '\n';
        }
    }
    if (!record.canonical_result.empty()) {
        auto result_frame = protocol::decode(record.canonical_result);
        if (result_frame) {
            auto result = protocol::decode_command_result(
                result_frame.value().payload);
            if (result && result.value().outcome ==
                              protocol::CommandOutcome::succeeded &&
                result.value().operation ==
                    protocol::CommandOperation::profile_status_set) {
                auto evidence = protocol::decode_profile_status_evidence(
                    result.value().body);
                if (evidence) {
                    output << protocol::render_profile_status_evidence(
                        evidence.value());
                }
            }
            if (result && result.value().outcome ==
                              protocol::CommandOutcome::succeeded &&
                result.value().operation ==
                    protocol::CommandOperation::update_stage) {
                auto evidence = protocol::decode_update_stage_evidence(
                    result.value().body);
                if (evidence) {
                    output << protocol::render_update_stage_evidence(
                        evidence.value());
                }
            }
        }
    }
    const auto render_schedule = [&output](
        std::string_view prefix,
        const CommandDeliverySchedule &schedule) {
        output << prefix << "-attempts=" << schedule.attempts << '\n'
               << prefix << "-last-error="
               << static_cast<unsigned>(schedule.last_error_code) << '\n'
               << prefix << "-last-attempt-unix-ms="
               << schedule.last_attempt_unix_ms << '\n'
               << prefix << "-next-attempt-unix-ms="
               << schedule.next_attempt_unix_ms << '\n';
    };
    render_schedule("request", record.request_schedule);
    render_schedule("receipt", record.receipt_schedule);
    render_schedule("result", record.result_schedule);
    output
           << "request-bytes=" << record.canonical_request.size() << '\n'
           << "receipt-bytes=" << record.canonical_receipt.size() << '\n'
           << "result-bytes=" << record.canonical_result.size() << '\n'
           << "created-unix-ms=" << record.created_unix_ms << '\n'
           << "updated-unix-ms=" << record.updated_unix_ms << '\n';
    return output.str();
}

std::string render_command_snapshot(const DurableCommandSnapshot &snapshot) {
    std::ostringstream output;
    output << "format=IoTox-Durable-Commands-v3\n"
           << "generation=" << snapshot.generation << '\n'
           << "local-sender-epoch=" << snapshot.local_sender_epoch << '\n'
           << "clock-high-water-unix-ms=" << snapshot.clock_high_water_unix_ms << '\n'
           << "record-count=" << snapshot.records.size() << '\n';
    for (const DurableCommandRecord &record : snapshot.records) {
        output << "---\n" << render_command_record(record);
    }
    return output.str();
}

}  // namespace iotox
