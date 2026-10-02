#include "test_harness.hpp"

#include "iotox/command_store.hpp"
#include "iotox/protocol/command.hpp"
#include "iotox/protocol/frame.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"

#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-command-store-test-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        char *created = ::mkdtemp(bytes.data());
        if (created == nullptr) {
            throw std::runtime_error("mkdtemp failed");
        }
        path_ = created;
    }

    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    [[nodiscard]] const std::filesystem::path &path() const noexcept { return path_; }

  private:
    std::filesystem::path path_;
};

std::vector<std::uint8_t> encode_request(
    std::uint64_t epoch,
    std::uint64_t message_id,
    std::uint64_t expiry_unix_ms = 0U) {
    auto payload = iotox::protocol::encode_command_request(
        iotox::protocol::CommandRequest{
            iotox::protocol::CommandOperation::device_describe});
    IOTOX_CHECK(payload.ok());
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::command;
    frame.message_id = message_id;
    frame.sequence = epoch;
    frame.expiry_unix_ms = expiry_unix_ms;
    frame.payload.assign(payload.value().begin(), payload.value().end());
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    return std::move(encoded).value();
}

std::vector<std::uint8_t> encode_profile_status_request(
    std::uint64_t epoch,
    std::uint64_t message_id,
    std::uint64_t expiry_unix_ms) {
    auto payload = iotox::protocol::encode_command_request(
        iotox::protocol::CommandRequest{
            iotox::protocol::CommandOperation::profile_status_set,
            iotox::protocol::CommandRequest::ProfileStatus::busy});
    IOTOX_CHECK(payload.ok());
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::command;
    frame.message_id = message_id;
    frame.sequence = epoch;
    frame.expiry_unix_ms = expiry_unix_ms;
    frame.payload.assign(payload.value().begin(), payload.value().end());
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    return std::move(encoded).value();
}

std::vector<std::uint8_t> encode_update_stage_request(
    std::uint64_t epoch, std::uint64_t message_id,
    const iotox::protocol::UpdateHeadRecord &head) {
    iotox::protocol::CommandRequest request;
    request.operation = iotox::protocol::CommandOperation::update_stage;
    request.expected_update_head = head;
    auto payload = iotox::protocol::encode_command_request(request);
    IOTOX_CHECK(payload.ok());
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::command;
    frame.message_id = message_id;
    frame.sequence = epoch;
    frame.payload = std::move(payload).value();
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    return std::move(encoded).value();
}

std::vector<std::uint8_t> encode_update_stage_result(
    std::uint64_t epoch, std::uint64_t request_message_id,
    std::uint64_t result_message_id,
    const iotox::protocol::UpdateStageEvidence &evidence) {
    auto body = iotox::protocol::encode_update_stage_evidence(evidence);
    IOTOX_CHECK(body.ok());
    iotox::protocol::CommandResultPayload result;
    result.operation = iotox::protocol::CommandOperation::update_stage;
    result.outcome = iotox::protocol::CommandOutcome::succeeded;
    result.body.assign(body.value().begin(), body.value().end());
    auto payload = iotox::protocol::encode_command_result(result);
    IOTOX_CHECK(payload.ok());
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::command_result;
    frame.message_id = result_message_id;
    frame.correlation_id = request_message_id;
    frame.sequence = epoch;
    frame.payload = std::move(payload).value();
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    return std::move(encoded).value();
}

std::vector<std::uint8_t> encode_receipt(
    std::uint64_t epoch,
    std::uint64_t request_message_id,
    std::uint64_t receipt_message_id) {
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::acknowledgement;
    frame.message_id = receipt_message_id;
    frame.correlation_id = request_message_id;
    frame.sequence = epoch;
    auto receipt = iotox::protocol::encode_command_receipt(
        iotox::protocol::CommandReceipt{
            iotox::protocol::CommandReceiptStage::received});
    IOTOX_CHECK(receipt.ok());
    frame.payload.assign(receipt.value().begin(), receipt.value().end());
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    return std::move(encoded).value();
}

std::vector<std::uint8_t> encode_result(
    std::uint64_t epoch,
    std::uint64_t request_message_id,
    std::uint64_t result_message_id,
    iotox::protocol::CommandOutcome outcome) {
    iotox::protocol::CommandResultPayload result;
    result.operation = iotox::protocol::CommandOperation::device_describe;
    result.outcome = outcome;
    auto payload = iotox::protocol::encode_command_result(result);
    IOTOX_CHECK(payload.ok());
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::command_result;
    frame.message_id = result_message_id;
    frame.correlation_id = request_message_id;
    frame.sequence = epoch;
    frame.payload = std::move(payload).value();
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    return std::move(encoded).value();
}

std::vector<std::uint8_t> encode_operation_result(
    std::uint64_t epoch,
    std::uint64_t request_message_id,
    std::uint64_t result_message_id,
    iotox::protocol::CommandOperation operation,
    iotox::protocol::CommandOutcome outcome) {
    iotox::protocol::CommandResultPayload result;
    result.operation = operation;
    result.outcome = outcome;
    auto payload = iotox::protocol::encode_command_result(result);
    IOTOX_CHECK(payload.ok());
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::command_result;
    frame.message_id = result_message_id;
    frame.correlation_id = request_message_id;
    frame.sequence = epoch;
    frame.payload = std::move(payload).value();
    auto encoded = iotox::protocol::encode(frame);
    IOTOX_CHECK(encoded.ok());
    return std::move(encoded).value();
}

iotox::DurableCommandRecord received_record(
    const iotox::CommandPeerKey &peer,
    std::uint64_t epoch,
    std::uint64_t message_id,
    std::uint64_t now) {
    iotox::DurableCommandRecord record;
    record.key.direction = iotox::CommandDirection::incoming;
    record.key.peer_public_key = peer;
    record.key.sender_epoch = epoch;
    record.key.message_id = message_id;
    record.direction = iotox::CommandDirection::incoming;
    record.lifecycle = iotox::CommandLifecycle::received;
    record.operation = iotox::protocol::CommandOperation::device_describe;
    record.outcome = iotox::protocol::CommandOutcome::internal_error;
    record.receipt_delivery = iotox::CommandDeliveryState::pending;
    record.created_unix_ms = now;
    record.updated_unix_ms = now;
    record.canonical_request = encode_request(epoch, message_id);
    record.canonical_receipt = encode_receipt(epoch, message_id, message_id + 1U);
    return record;
}

iotox::DurableCommandRecord outgoing_record(
    const iotox::CommandPeerKey &peer,
    std::uint64_t epoch,
    std::uint64_t message_id,
    std::uint64_t now,
    iotox::CommandPriority priority = iotox::CommandPriority::normal) {
    iotox::DurableCommandRecord record;
    record.key.direction = iotox::CommandDirection::outgoing;
    record.key.peer_public_key = peer;
    record.key.sender_epoch = epoch;
    record.key.message_id = message_id;
    record.direction = iotox::CommandDirection::outgoing;
    record.lifecycle = iotox::CommandLifecycle::reserved;
    record.operation = iotox::protocol::CommandOperation::device_describe;
    record.outcome = iotox::protocol::CommandOutcome::internal_error;
    record.priority = priority;
    record.created_unix_ms = now;
    record.updated_unix_ms = now;
    record.request_schedule.next_attempt_unix_ms = now + 1000U;
    record.canonical_request = encode_request(epoch, message_id);
    return record;
}

void append_test_u16(std::vector<std::uint8_t> &bytes, std::uint16_t value) {
    bytes.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>(value & 0xFFU));
}

void append_test_u32(std::vector<std::uint8_t> &bytes, std::uint32_t value) {
    bytes.push_back(static_cast<std::uint8_t>((value >> 24U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>((value >> 16U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    bytes.push_back(static_cast<std::uint8_t>(value & 0xFFU));
}

void append_test_u64(std::vector<std::uint8_t> &bytes, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        bytes.push_back(static_cast<std::uint8_t>(
            (value >> static_cast<unsigned>(shift)) & 0xFFU));
    }
}

std::vector<std::uint8_t> legacy_v2_store(
    const iotox::security::DeviceIdentity &identity,
    const iotox::DurableCommandRecord &record) {
    constexpr std::size_t kLegacyRecordHeaderBytes = 168U;
    constexpr std::size_t kUnsignedHeaderBytes = 112U;
    std::vector<std::uint8_t> body;
    const std::size_t record_bytes = kLegacyRecordHeaderBytes +
        record.canonical_request.size() + record.canonical_receipt.size() +
        record.canonical_result.size();
    body.reserve(record_bytes);
    append_test_u32(body, static_cast<std::uint32_t>(record_bytes));
    body.push_back(2U);
    body.push_back(static_cast<std::uint8_t>(record.direction));
    body.push_back(static_cast<std::uint8_t>(record.lifecycle));
    body.push_back(static_cast<std::uint8_t>(record.operation));
    body.push_back(static_cast<std::uint8_t>(record.outcome));
    body.push_back(static_cast<std::uint8_t>(record.receipt_delivery));
    body.push_back(static_cast<std::uint8_t>(record.result_delivery));
    body.push_back(0U);
    append_test_u16(body, static_cast<std::uint16_t>(iotox::ErrorCode::unavailable));
    append_test_u16(body, 0U);
    append_test_u32(body, 2U);
    body.insert(body.end(), record.key.peer_public_key.begin(),
                record.key.peer_public_key.end());
    body.insert(body.end(), record.peer_principal.begin(),
                record.peer_principal.end());
    append_test_u64(body, record.key.sender_epoch);
    append_test_u64(body, record.key.message_id);
    append_test_u64(body, record.correlation_id);
    append_test_u64(body, record.result_message_id);
    append_test_u64(body, record.ownership_epoch);
    append_test_u64(body, record.authority_sequence);
    append_test_u64(body, record.created_unix_ms);
    append_test_u64(body, record.updated_unix_ms);
    append_test_u32(body, static_cast<std::uint32_t>(record.canonical_request.size()));
    append_test_u32(body, static_cast<std::uint32_t>(record.canonical_receipt.size()));
    append_test_u32(body, static_cast<std::uint32_t>(record.canonical_result.size()));
    body.insert(body.end(), 8U, 0U);
    IOTOX_CHECK(body.size() >= kLegacyRecordHeaderBytes);
    body.insert(body.end(), record.canonical_request.begin(),
                record.canonical_request.end());
    body.insert(body.end(), record.canonical_receipt.begin(),
                record.canonical_receipt.end());
    body.insert(body.end(), record.canonical_result.begin(),
                record.canonical_result.end());

    constexpr std::array<std::uint8_t, 8U> kLegacyMagic{
        'I', 'O', 'T', 'X', 'C', 'M', 'D', '2'};
    std::vector<std::uint8_t> signed_bytes;
    signed_bytes.reserve(kUnsignedHeaderBytes + body.size());
    signed_bytes.insert(
        signed_bytes.end(), kLegacyMagic.begin(), kLegacyMagic.end());
    signed_bytes.push_back(2U);
    signed_bytes.push_back(1U);
    append_test_u16(signed_bytes, 176U);
    append_test_u32(signed_bytes, 1U);
    append_test_u64(signed_bytes, 7U);
    append_test_u64(signed_bytes, 55U);
    append_test_u32(signed_bytes, static_cast<std::uint32_t>(body.size()));
    append_test_u32(signed_bytes, 0U);
    signed_bytes.insert(signed_bytes.end(), identity.public_key().begin(),
                        identity.public_key().end());
    signed_bytes.insert(signed_bytes.end(), 40U, 0U);
    IOTOX_CHECK(signed_bytes.size() == kUnsignedHeaderBytes);
    signed_bytes.insert(signed_bytes.end(), body.begin(), body.end());
    auto signature = identity.sign(signed_bytes);
    IOTOX_CHECK(signature.ok());
    std::vector<std::uint8_t> file;
    file.reserve(176U + body.size());
    file.insert(
        file.end(), signed_bytes.begin(),
        signed_bytes.begin() + static_cast<std::ptrdiff_t>(kUnsignedHeaderBytes));
    file.insert(file.end(), signature.value().begin(), signature.value().end());
    file.insert(file.end(), body.begin(), body.end());
    return file;
}

}  // namespace

IOTOX_TEST("durable command store signs, reloads, deduplicates, and freezes terminal results") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    const auto identity_path = temporary.path() / "device.identity";
    auto identity = security::DeviceIdentity::load_or_create(
        identity_path, sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    auto store = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(store.ok(), store.status().message());
    const std::uint64_t local_epoch = store.value()->local_sender_epoch();
    IOTOX_CHECK(local_epoch != 0U);
    IOTOX_CHECK(store.value()->snapshot().generation == 1U);

    struct stat metadata {};
    IOTOX_CHECK(::stat(config.path.c_str(), &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & (S_IRWXG | S_IRWXO)) == 0);

    CommandPeerKey peer{};
    for (std::size_t index = 0U; index < peer.size(); ++index) {
        peer[index] = static_cast<std::uint8_t>(index + 1U);
    }
    DurableCommandRecord record = received_record(peer, 77U, 901U, 1000U);
    DurableCommandRecord expiring_mutation =
        received_record(peer, 77U, 900U, 1000U);
    expiring_mutation.key.message_id = 900U;
    expiring_mutation.operation =
        protocol::CommandOperation::profile_status_set;
    expiring_mutation.expiry_unix_ms = 2000U;
    expiring_mutation.clock_requirement =
        CommandClockRequirement::trusted_wall;
    expiring_mutation.canonical_request =
        encode_profile_status_request(77U, 900U, 2000U);
    IOTOX_CHECK(!store.value()->insert(expiring_mutation).ok());
    auto inserted = store.value()->insert(record);
    IOTOX_CHECK(inserted.ok());
    IOTOX_CHECK(inserted.value() == CommandInsertDisposition::inserted);
    auto duplicate = store.value()->insert(record);
    IOTOX_CHECK(duplicate.ok());
    IOTOX_CHECK(duplicate.value() == CommandInsertDisposition::exact_duplicate);

    DurableCommandRecord conflict = record;
    auto conflict_frame = protocol::decode(conflict.canonical_request);
    IOTOX_CHECK(conflict_frame.ok());
    conflict_frame.value().flags = 1U;
    auto conflict_request = protocol::encode(conflict_frame.value());
    IOTOX_CHECK(conflict_request.ok());
    conflict.canonical_request = std::move(conflict_request).value();
    auto conflicting = store.value()->insert(conflict);
    IOTOX_CHECK(conflicting.ok());
    IOTOX_CHECK(conflicting.value() == CommandInsertDisposition::conflicting_reuse);

    record.lifecycle = CommandLifecycle::admitted;
    record.ownership_epoch = 4U;
    record.authority_sequence = 12U;
    record.peer_principal.fill(0x44U);
    record.updated_unix_ms = 1001U;
    IOTOX_CHECK_MSG(store.value()->update(record).ok(), "admitted transition must persist");
    record.lifecycle = CommandLifecycle::started;
    record.updated_unix_ms = 1002U;
    IOTOX_CHECK_MSG(store.value()->update(record).ok(), "started transition must persist");
    record.lifecycle = CommandLifecycle::failed;
    record.outcome = protocol::CommandOutcome::denied;
    record.result_message_id = 902U;
    record.result_delivery = CommandDeliveryState::pending;
    record.canonical_result = encode_result(
        record.key.sender_epoch, record.key.message_id,
        record.result_message_id, record.outcome);
    record.updated_unix_ms = 1003U;
    IOTOX_CHECK_MSG(store.value()->update(record).ok(), "terminal transition must persist");
    IOTOX_CHECK(begin_command_delivery_attempt(
        record, CommandArtifact::receipt, 1004U).ok());
    IOTOX_CHECK(begin_command_delivery_attempt(
        record, CommandArtifact::result, 1004U).ok());
    record.receipt_delivery = CommandDeliveryState::queued;
    record.result_delivery = CommandDeliveryState::terminal_failure;
    record.result_schedule.last_error_code = ErrorCode::protocol_error;
    IOTOX_CHECK_MSG(
        store.value()->update(record).ok(),
        "terminal result provider failure must remain durable");
    IOTOX_CHECK(begin_command_delivery_attempt(
        record, CommandArtifact::result, 1005U, {}, true).ok());
    IOTOX_CHECK_MSG(
        store.value()->update(record).ok(),
        "explicit replay attempt must be committed before transport");
    record.result_delivery = CommandDeliveryState::queued;
    IOTOX_CHECK_MSG(
        store.value()->update(record).ok(),
        "explicit replay may recover a terminal provider failure");
    DurableCommandRecord delivery_rollback = record;
    delivery_rollback.result_delivery = CommandDeliveryState::pending;
    delivery_rollback.updated_unix_ms = 1006U;
    IOTOX_CHECK(!store.value()->update(delivery_rollback).ok());

    auto loaded = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value()->local_sender_epoch() == local_epoch);
    auto found = loaded.value()->find(record.key);
    IOTOX_CHECK(found.ok() && found.value().has_value());
    IOTOX_CHECK(found.value().value() == record);
    IOTOX_CHECK(loaded.value()->snapshot().generation == 8U);

    DurableCommandRecord rollback = record;
    rollback.lifecycle = CommandLifecycle::started;
    rollback.updated_unix_ms = 1007U;
    IOTOX_CHECK(!loaded.value()->update(rollback).ok());
}

IOTOX_TEST("durable command store binds update staging evidence to the exact HEAD") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    auto store = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(store.ok(), store.status().message());

    CommandPeerKey peer{};
    peer.fill(0x41U);
    protocol::UpdateHeadRecord head{};
    head.fill(0x52U);
    DurableCommandRecord record;
    record.key.direction = CommandDirection::incoming;
    record.key.peer_public_key = peer;
    record.key.sender_epoch = 17U;
    record.key.message_id = 19U;
    record.direction = CommandDirection::incoming;
    record.lifecycle = CommandLifecycle::received;
    record.operation = protocol::CommandOperation::update_stage;
    record.outcome = protocol::CommandOutcome::internal_error;
    record.receipt_delivery = CommandDeliveryState::pending;
    record.created_unix_ms = 100U;
    record.updated_unix_ms = 100U;
    record.canonical_request = encode_update_stage_request(
        record.key.sender_epoch, record.key.message_id, head);
    record.canonical_receipt = encode_receipt(
        record.key.sender_epoch, record.key.message_id, 20U);
    IOTOX_CHECK(store.value()->insert(record).ok());

    record.lifecycle = CommandLifecycle::admitted;
    record.peer_principal.fill(0x61U);
    record.ownership_epoch = 2U;
    record.authority_sequence = 3U;
    record.updated_unix_ms = 101U;
    IOTOX_CHECK(store.value()->update(record).ok());
    record.lifecycle = CommandLifecycle::started;
    record.updated_unix_ms = 102U;
    IOTOX_CHECK(store.value()->update(record).ok());

    protocol::UpdateStageEvidence evidence;
    evidence.release_sequence = 4U;
    evidence.accepted_head = head;
    evidence.manifest_record.fill(0x73U);
    record.lifecycle = CommandLifecycle::succeeded;
    record.outcome = protocol::CommandOutcome::succeeded;
    record.result_message_id = 21U;
    record.result_delivery = CommandDeliveryState::pending;
    record.correlation_id = record.key.message_id;
    record.canonical_result = encode_update_stage_result(
        record.key.sender_epoch, record.key.message_id,
        record.result_message_id, evidence);
    record.updated_unix_ms = 103U;
    IOTOX_CHECK_MSG(store.value()->update(record).ok(),
                    "exact update evidence must persist");

    auto mismatch = record;
    protocol::UpdateStageEvidence wrong = evidence;
    wrong.accepted_head.fill(0x53U);
    mismatch.canonical_result = encode_update_stage_result(
        record.key.sender_epoch, record.key.message_id,
        record.result_message_id, wrong);
    mismatch.updated_unix_ms = 104U;
    IOTOX_CHECK(!store.value()->update(mismatch).ok());

    auto loaded = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    auto found = loaded.value()->find(record.key);
    IOTOX_CHECK(found.ok() && found.value().has_value());
    IOTOX_CHECK(found.value().value() == record);
}

IOTOX_TEST("durable command store rejects tampering and a foreign device identity") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    auto store = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());

    auto foreign = security::DeviceIdentity::load_or_create(
        temporary.path() / "foreign.identity", sodium.value(), true);
    IOTOX_CHECK(foreign.ok());
    auto wrong_identity = DurableCommandStore::open(
        config, foreign.value(), sodium.value());
    IOTOX_CHECK(!wrong_identity.ok());
    IOTOX_CHECK(wrong_identity.status().code() == ErrorCode::protocol_error);

    std::fstream file(config.path, std::ios::binary | std::ios::in | std::ios::out);
    IOTOX_CHECK(file.good());
    file.seekg(24, std::ios::beg);
    char byte = 0;
    file.read(&byte, 1);
    IOTOX_CHECK(file.good());
    byte = static_cast<char>(static_cast<unsigned char>(byte) ^ 0x40U);
    file.seekp(24, std::ios::beg);
    file.write(&byte, 1);
    file.close();

    auto tampered = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(!tampered.ok());
    IOTOX_CHECK(tampered.status().code() == ErrorCode::protocol_error);
}

IOTOX_TEST("durable command store prunes only fully delivered terminal history at its record bound") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    config.maximum_records = 2U;
    auto store = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());

    CommandPeerKey peer{};
    peer.fill(0x33U);
    DurableCommandRecord first = received_record(peer, 1U, 11U, 100U);
    first.lifecycle = CommandLifecycle::failed;
    first.outcome = protocol::CommandOutcome::denied;
    first.result_message_id = 12U;
    first.result_delivery = CommandDeliveryState::pending;
    first.canonical_result = encode_result(1U, 11U, 12U, first.outcome);
    IOTOX_CHECK(store.value()->insert(first).ok());

    DurableCommandRecord second = received_record(peer, 1U, 21U, 200U);
    IOTOX_CHECK(store.value()->insert(second).ok());
    DurableCommandRecord third = received_record(peer, 1U, 31U, 300U);
    auto delivery_pending = store.value()->insert(third);
    IOTOX_CHECK(!delivery_pending.ok());
    IOTOX_CHECK(delivery_pending.status().code() == ErrorCode::resource_exhausted);
    IOTOX_CHECK(begin_command_delivery_attempt(
        first, CommandArtifact::receipt, 301U).ok());
    IOTOX_CHECK(begin_command_delivery_attempt(
        first, CommandArtifact::result, 301U).ok());
    first.receipt_delivery = CommandDeliveryState::queued;
    first.result_delivery = CommandDeliveryState::queued;
    IOTOX_CHECK(store.value()->update(first).ok());
    IOTOX_CHECK(store.value()->insert(third).ok());
    IOTOX_CHECK(store.value()->snapshot().records.size() == 2U);
    auto old = store.value()->find(first.key);
    IOTOX_CHECK(old.ok() && !old.value().has_value());

    DurableCommandRecord fourth = received_record(peer, 1U, 41U, 400U);
    auto exhausted = store.value()->insert(fourth);
    IOTOX_CHECK(!exhausted.ok());
    IOTOX_CHECK(exhausted.status().code() == ErrorCode::resource_exhausted);
}

IOTOX_TEST("command effect frontier is stable across result churn and retains its identities") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    config.maximum_records = 2U;
    config.retain_mutating_effect_history = true;
    auto store = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());
    auto empty = command_effect_frontier_digest(
        store.value()->snapshot(), sodium.value());
    IOTOX_CHECK(empty.ok());

    CommandPeerKey peer{};
    peer.fill(0x35U);
    DurableCommandRecord effect = received_record(peer, 3U, 51U, 500U);
    effect.operation = protocol::CommandOperation::profile_status_set;
    effect.canonical_request = encode_profile_status_request(3U, 51U, 0U);
    IOTOX_CHECK(store.value()->insert(effect).ok());
    auto received = command_effect_frontier_digest(
        store.value()->snapshot(), sodium.value());
    IOTOX_CHECK(received.ok() && received.value() == empty.value());
    effect.lifecycle = CommandLifecycle::admitted;
    effect.peer_principal.fill(0x45U);
    effect.ownership_epoch = 2U;
    effect.authority_sequence = 7U;
    effect.updated_unix_ms = 501U;
    IOTOX_CHECK(store.value()->update(effect).ok());
    effect.lifecycle = CommandLifecycle::started;
    effect.updated_unix_ms = 502U;
    IOTOX_CHECK(store.value()->update(effect).ok());
    auto started = command_effect_frontier_digest(
        store.value()->snapshot(), sodium.value());
    IOTOX_CHECK(started.ok() && started.value() != empty.value());

    IOTOX_CHECK(begin_command_delivery_attempt(
        effect, CommandArtifact::receipt, 503U).ok());
    effect.receipt_delivery = CommandDeliveryState::queued;
    effect.lifecycle = CommandLifecycle::failed;
    effect.outcome = protocol::CommandOutcome::internal_error;
    effect.result_message_id = 52U;
    effect.correlation_id = effect.key.message_id;
    effect.result_delivery = CommandDeliveryState::pending;
    effect.canonical_result = encode_operation_result(
        effect.key.sender_epoch, effect.key.message_id,
        effect.result_message_id, effect.operation, effect.outcome);
    IOTOX_CHECK(begin_command_delivery_attempt(
        effect, CommandArtifact::result, 503U).ok());
    effect.result_delivery = CommandDeliveryState::queued;
    effect.updated_unix_ms = 503U;
    IOTOX_CHECK_MSG(store.value()->update(effect).ok(),
                    "terminal effect identity must persist");
    auto settled = command_effect_frontier_digest(
        store.value()->snapshot(), sodium.value());
    IOTOX_CHECK(settled.ok() && settled.value() == started.value());
    IOTOX_CHECK(command_record_has_effect_identity(effect));

    DurableCommandRecord read_only = received_record(peer, 3U, 61U, 600U);
    read_only.lifecycle = CommandLifecycle::failed;
    read_only.outcome = protocol::CommandOutcome::denied;
    read_only.result_message_id = 62U;
    read_only.correlation_id = read_only.key.message_id;
    read_only.result_delivery = CommandDeliveryState::pending;
    read_only.canonical_result = encode_result(
        3U, 61U, 62U, read_only.outcome);
    IOTOX_CHECK(begin_command_delivery_attempt(
        read_only, CommandArtifact::receipt, 601U).ok());
    IOTOX_CHECK(begin_command_delivery_attempt(
        read_only, CommandArtifact::result, 601U).ok());
    read_only.receipt_delivery = CommandDeliveryState::queued;
    read_only.result_delivery = CommandDeliveryState::queued;
    IOTOX_CHECK(store.value()->insert(read_only).ok());
    DurableCommandRecord replacement =
        received_record(peer, 3U, 71U, 700U);
    IOTOX_CHECK(store.value()->insert(replacement).ok());
    auto retained = store.value()->find(effect.key);
    auto pruned = store.value()->find(read_only.key);
    IOTOX_CHECK(retained.ok() && retained.value().has_value());
    IOTOX_CHECK(pruned.ok() && !pruned.value().has_value());
}

IOTOX_TEST("durable command journal keeps incoming and outgoing wire identities in separate lanes") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    auto store = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(store.ok(), store.status().message());

    CommandPeerKey peer{};
    peer.fill(0xA5U);
    constexpr std::uint64_t epoch = 0x1122334455667788ULL;
    constexpr std::uint64_t message = 0x8877665544332211ULL;

    DurableCommandRecord incoming = received_record(peer, epoch, message, 500U);
    IOTOX_CHECK(store.value()->insert(incoming).ok());

    DurableCommandRecord outgoing;
    outgoing.key.direction = CommandDirection::outgoing;
    outgoing.key.peer_public_key = peer;
    outgoing.key.sender_epoch = epoch;
    outgoing.key.message_id = message;
    outgoing.direction = CommandDirection::outgoing;
    outgoing.lifecycle = CommandLifecycle::reserved;
    outgoing.operation = protocol::CommandOperation::device_describe;
    outgoing.outcome = protocol::CommandOutcome::internal_error;
    outgoing.created_unix_ms = 501U;
    outgoing.updated_unix_ms = 501U;
    outgoing.canonical_request = encode_request(epoch, message);
    auto inserted = store.value()->insert(outgoing);
    IOTOX_CHECK_MSG(inserted.ok(), inserted.status().message());
    IOTOX_CHECK(inserted.value() == CommandInsertDisposition::inserted);

    auto incoming_found = store.value()->find(incoming.key);
    auto outgoing_found = store.value()->find(outgoing.key);
    IOTOX_CHECK(incoming_found.ok() && incoming_found.value().has_value());
    IOTOX_CHECK(outgoing_found.ok() && outgoing_found.value().has_value());
    IOTOX_CHECK(incoming_found.value()->direction == CommandDirection::incoming);
    IOTOX_CHECK(outgoing_found.value()->direction == CommandDirection::outgoing);
    IOTOX_CHECK(store.value()->snapshot().records.size() == 2U);

    DurableCommandRecord malformed = outgoing;
    malformed.direction = CommandDirection::incoming;
    auto rejected = store.value()->insert(malformed);
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.status().code() == ErrorCode::invalid_argument);
}

IOTOX_TEST("durable outbox persists cancellation boundary and deterministic retry schedule") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    auto store = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());

    CommandPeerKey peer{};
    peer.fill(0x52U);
    DurableCommandRecord cancellable = outgoing_record(peer, 9U, 10U, 1000U);
    IOTOX_CHECK(store.value()->insert(cancellable).ok());
    auto cancelled = store.value()->cancel_before_start(
        cancellable.key, 1500U);
    IOTOX_CHECK_MSG(cancelled.ok(), cancelled.status().message());
    IOTOX_CHECK(cancelled.value().lifecycle == CommandLifecycle::cancelled);
    IOTOX_CHECK(cancelled.value().request_schedule.attempts == 0U);

    DurableCommandRecord attempted = outgoing_record(peer, 9U, 20U, 2000U);
    IOTOX_CHECK(store.value()->insert(attempted).ok());
    DurableCommandRecord repeated = attempted;
    IOTOX_CHECK(begin_command_delivery_attempt(
        attempted, CommandArtifact::request, 3000U,
        CommandRetryPolicy{100U, 800U}).ok());
    IOTOX_CHECK(begin_command_delivery_attempt(
        repeated, CommandArtifact::request, 3000U,
        CommandRetryPolicy{100U, 800U}).ok());
    IOTOX_CHECK(attempted.request_schedule == repeated.request_schedule);
    IOTOX_CHECK(attempted.lifecycle == CommandLifecycle::locally_queued);
    IOTOX_CHECK(attempted.request_schedule.next_attempt_unix_ms >= 3100U);
    IOTOX_CHECK(attempted.request_schedule.next_attempt_unix_ms <= 3125U);
    IOTOX_CHECK(store.value()->update(attempted).ok());
    auto unsafe_cancel = store.value()->cancel_before_start(
        attempted.key, 3100U);
    IOTOX_CHECK(!unsafe_cancel.ok());
    IOTOX_CHECK(unsafe_cancel.status().code() == ErrorCode::unavailable);

    auto loaded = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(loaded.ok());
    auto persisted_cancel = loaded.value()->find(cancellable.key);
    auto persisted_attempt = loaded.value()->find(attempted.key);
    IOTOX_CHECK(persisted_cancel.ok() && persisted_cancel.value().has_value());
    IOTOX_CHECK(persisted_attempt.ok() && persisted_attempt.value().has_value());
    IOTOX_CHECK(persisted_cancel.value()->lifecycle == CommandLifecycle::cancelled);
    IOTOX_CHECK(persisted_attempt.value()->request_schedule ==
                attempted.request_schedule);

    DurableCommandRecord incoming = received_record(peer, 10U, 30U, 4000U);
    const CommandRetryPolicy saturated{4U, 4U};
    IOTOX_CHECK(begin_command_delivery_attempt(
        incoming, CommandArtifact::receipt, 4000U, saturated).ok());
    incoming.receipt_delivery = CommandDeliveryState::queued;
    std::uint64_t previous_next =
        incoming.receipt_schedule.next_attempt_unix_ms;
    for (unsigned replay = 0U; replay < 16U; ++replay) {
        IOTOX_CHECK(begin_command_delivery_attempt(
            incoming, CommandArtifact::receipt, 4000U,
            saturated, true).ok());
        IOTOX_CHECK(
            incoming.receipt_schedule.next_attempt_unix_ms >= previous_next);
        previous_next = incoming.receipt_schedule.next_attempt_unix_ms;
    }
}

IOTOX_TEST("durable outbox distinguishes unattempted expiry from uncertain timeout") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    auto store = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());

    CommandPeerKey peer{};
    peer.fill(0x5AU);
    DurableCommandRecord expired = outgoing_record(peer, 4U, 10U, 1000U);
    expired.expiry_unix_ms = 1500U;
    expired.clock_requirement = CommandClockRequirement::trusted_wall;
    expired.canonical_request = encode_request(4U, 10U, 1500U);
    IOTOX_CHECK(store.value()->insert(expired).ok());
    expired.lifecycle = CommandLifecycle::expired;
    expired.outcome = protocol::CommandOutcome::expired;
    expired.updated_unix_ms = 1500U;
    IOTOX_CHECK(store.value()->update(expired).ok());

    DurableCommandRecord uncertain = outgoing_record(peer, 4U, 20U, 2000U);
    uncertain.expiry_unix_ms = 4000U;
    uncertain.clock_requirement = CommandClockRequirement::trusted_wall;
    uncertain.canonical_request = encode_request(4U, 20U, 4000U);
    IOTOX_CHECK(store.value()->insert(uncertain).ok());
    IOTOX_CHECK(begin_command_delivery_attempt(
        uncertain, CommandArtifact::request, 3000U).ok());
    IOTOX_CHECK(store.value()->update(uncertain).ok());
    uncertain.lifecycle = CommandLifecycle::timed_out_unconfirmed;
    uncertain.outcome = protocol::CommandOutcome::expired;
    uncertain.updated_unix_ms = 4000U;
    IOTOX_CHECK(store.value()->update(uncertain).ok());
    IOTOX_CHECK(uncertain.canonical_result.empty());

    DurableCommandRecord resolved = uncertain;
    resolved.lifecycle = CommandLifecycle::failed;
    resolved.outcome = protocol::CommandOutcome::denied;
    resolved.result_message_id = 21U;
    resolved.correlation_id = uncertain.key.message_id;
    resolved.result_delivery = CommandDeliveryState::observed;
    resolved.canonical_result = encode_result(
        resolved.key.sender_epoch, resolved.key.message_id,
        resolved.result_message_id, resolved.outcome);
    resolved.updated_unix_ms = 4001U;
    IOTOX_CHECK_MSG(
        store.value()->update(resolved).ok(),
        "an exact late result must resolve a retained uncertain timeout");

    DurableCommandRecord fabricated = expired;
    fabricated.canonical_receipt = encode_receipt(4U, 10U, 11U);
    fabricated.receipt_delivery = CommandDeliveryState::observed;
    fabricated.updated_unix_ms = 1600U;
    IOTOX_CHECK(!store.value()->update(fabricated).ok());
}

IOTOX_TEST("durable outbox orders priority and enforces unfinished peer quotas") {
    using namespace iotox;
    CommandPeerKey first_peer{};
    first_peer.fill(0x61U);
    CommandPeerKey second_peer{};
    second_peer.fill(0x62U);
    DurableCommandRecord low = outgoing_record(
        first_peer, 1U, 1U, 100U, CommandPriority::low);
    DurableCommandRecord high = outgoing_record(
        second_peer, 1U, 2U, 200U, CommandPriority::high);
    DurableCommandRecord normal = outgoing_record(
        second_peer, 1U, 3U, 50U, CommandPriority::normal);
    auto ordered = order_command_outbox({low, high, normal});
    IOTOX_CHECK(ordered.size() == 3U);
    IOTOX_CHECK(ordered[0U].priority == CommandPriority::high);
    IOTOX_CHECK(ordered[1U].priority == CommandPriority::normal);
    IOTOX_CHECK(ordered[2U].priority == CommandPriority::low);

    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    config.maximum_pending_records = 2U;
    config.maximum_pending_per_peer = 1U;
    auto store = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());
    IOTOX_CHECK(store.value()->insert(low).ok());
    DurableCommandRecord same_peer = outgoing_record(
        first_peer, 1U, 4U, 300U);
    auto peer_exhausted = store.value()->insert(same_peer);
    IOTOX_CHECK(!peer_exhausted.ok());
    IOTOX_CHECK(peer_exhausted.status().code() == ErrorCode::resource_exhausted);
    IOTOX_CHECK(store.value()->insert(high).ok());
    DurableCommandRecord total = outgoing_record(
        second_peer, 1U, 5U, 400U);
    total.key.peer_public_key.fill(0x63U);
    total.canonical_request = encode_request(
        total.key.sender_epoch, total.key.message_id);
    auto total_exhausted = store.value()->insert(total);
    IOTOX_CHECK(!total_exhausted.ok());
    IOTOX_CHECK(total_exhausted.status().code() == ErrorCode::resource_exhausted);

    store.value().reset();
    config.maximum_pending_records = 1U;
    auto below_persisted_work = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(!below_persisted_work.ok());
    IOTOX_CHECK(
        below_persisted_work.status().code() == ErrorCode::resource_exhausted);
}

IOTOX_TEST("durable command persistence failure leaves memory and disk generation unchanged") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    config.maximum_file_bytes = 400U;
    config.maximum_bytes_per_peer = 400U;
    auto store = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());
    const std::uint64_t generation = store.value()->snapshot().generation;
    CommandPeerKey peer{};
    peer.fill(0x71U);
    auto failed = store.value()->insert(received_record(peer, 2U, 3U, 100U));
    IOTOX_CHECK(!failed.ok());
    IOTOX_CHECK(failed.status().code() == ErrorCode::resource_exhausted);
    IOTOX_CHECK(store.value()->snapshot().generation == generation);
    IOTOX_CHECK(store.value()->snapshot().records.empty());
    auto reopened = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(reopened.value()->snapshot().generation == generation);
    IOTOX_CHECK(reopened.value()->snapshot().records.empty());
}

IOTOX_TEST("durable command clock checkpoints are signed monotonic restart state") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    DurableCommandStore::Config config;
    config.path = temporary.path() / "commands.store";
    auto store = DurableCommandStore::open(config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());
    const std::uint64_t initial_generation =
        store.value()->snapshot().generation;
    IOTOX_CHECK(store.value()->clock_high_water_unix_ms() == 0U);
    IOTOX_CHECK(store.value()->checkpoint_clock_high_water(5000U).ok());
    IOTOX_CHECK(store.value()->clock_high_water_unix_ms() == 5000U);
    IOTOX_CHECK(store.value()->snapshot().clock_high_water_unix_ms == 5000U);
    IOTOX_CHECK(
        store.value()->snapshot().generation == initial_generation + 1U);
    IOTOX_CHECK(store.value()->checkpoint_clock_high_water(4999U).ok());
    IOTOX_CHECK(
        store.value()->snapshot().generation == initial_generation + 1U);
    IOTOX_CHECK(command_clock_within_rollback_tolerance(5000U, 4900U, 100U));
    IOTOX_CHECK(!command_clock_within_rollback_tolerance(5000U, 4899U, 100U));

    auto reopened = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(reopened.value()->clock_high_water_unix_ms() == 5000U);
    IOTOX_CHECK(reopened.value()->snapshot().clock_high_water_unix_ms == 5000U);
    IOTOX_CHECK(
        reopened.value()->snapshot().generation == initial_generation + 1U);
}

IOTOX_TEST("signed v2 command journal migrates atomically to scheduled v3") {
    using namespace iotox;
    TemporaryDirectory temporary;
    auto sodium = security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = security::DeviceIdentity::load_or_create(
        temporary.path() / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    CommandPeerKey peer{};
    peer.fill(0x81U);
    DurableCommandRecord legacy = received_record(peer, 8U, 9U, 1000U);
    const std::vector<std::uint8_t> fixture = legacy_v2_store(
        identity.value(), legacy);
    const std::filesystem::path path = temporary.path() / "commands.store";
    {
        std::ofstream output(path, std::ios::binary | std::ios::trunc);
        IOTOX_CHECK(output.good());
        output.write(
            reinterpret_cast<const char *>(fixture.data()),
            static_cast<std::streamsize>(fixture.size()));
        IOTOX_CHECK(output.good());
    }
    IOTOX_CHECK(::chmod(path.c_str(), S_IRUSR | S_IWUSR) == 0);

    DurableCommandStore::Config config;
    config.path = path;
    auto migrated = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(migrated.ok(), migrated.status().message());
    IOTOX_CHECK(migrated.value()->snapshot().generation == 8U);
    IOTOX_CHECK(migrated.value()->snapshot().clock_high_water_unix_ms == 1000U);
    auto found = migrated.value()->find(legacy.key);
    IOTOX_CHECK(found.ok() && found.value().has_value());
    IOTOX_CHECK(found.value()->receipt_schedule.attempts == 2U);
    IOTOX_CHECK(found.value()->receipt_schedule.last_error_code ==
                ErrorCode::unavailable);
    std::ifstream input(path, std::ios::binary);
    std::array<char, 8U> magic{};
    input.read(magic.data(), static_cast<std::streamsize>(magic.size()));
    IOTOX_CHECK(std::string(magic.data(), magic.size()) == "IOTXCMD3");
    auto reopened = DurableCommandStore::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(reopened.value()->snapshot().generation == 8U);

    const std::filesystem::path failure_path =
        temporary.path() / "commands-migration-failure.store";
    {
        std::ofstream output(failure_path, std::ios::binary | std::ios::trunc);
        IOTOX_CHECK(output.good());
        output.write(
            reinterpret_cast<const char *>(fixture.data()),
            static_cast<std::streamsize>(fixture.size()));
        IOTOX_CHECK(output.good());
    }
    IOTOX_CHECK(::chmod(failure_path.c_str(), S_IRUSR | S_IWUSR) == 0);
    DurableCommandStore::Config failure_config;
    failure_config.path = failure_path;
    failure_config.maximum_file_bytes = fixture.size();
    failure_config.maximum_bytes_per_peer = fixture.size();
    auto migration_refused = DurableCommandStore::open(
        failure_config, identity.value(), sodium.value());
    IOTOX_CHECK(!migration_refused.ok());
    IOTOX_CHECK(
        migration_refused.status().code() == ErrorCode::resource_exhausted);
    std::vector<std::uint8_t> unchanged(fixture.size());
    {
        std::ifstream unchanged_input(failure_path, std::ios::binary);
        IOTOX_CHECK(unchanged_input.good());
        unchanged_input.read(
            reinterpret_cast<char *>(unchanged.data()),
            static_cast<std::streamsize>(unchanged.size()));
        IOTOX_CHECK(unchanged_input.good());
    }
    IOTOX_CHECK(unchanged == fixture);
}
