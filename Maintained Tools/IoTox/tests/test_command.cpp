#include "iotox/protocol/command.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/security/authority.hpp"
#include "test_harness.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>

IOTOX_TEST("device.describe command request has one canonical eight-byte form") {
    iotox::protocol::CommandRequest request;
    request.operation = iotox::protocol::CommandOperation::device_describe;
    auto encoded = iotox::protocol::encode_command_request(request);
    IOTOX_CHECK(encoded);
    IOTOX_CHECK(encoded.value().size() ==
                iotox::protocol::kCommandRequestBytes);
    auto decoded = iotox::protocol::decode_command_request(encoded.value());
    IOTOX_CHECK(decoded);
    IOTOX_CHECK(decoded.value() == request);

    auto malformed = encoded.value();
    malformed[7U] = 1U;
    IOTOX_CHECK(!iotox::protocol::decode_command_request(malformed));
    malformed = encoded.value();
    malformed[5U] = 0xffU;
    IOTOX_CHECK(!iotox::protocol::decode_command_request(malformed));
}

IOTOX_TEST("profile.status.set freezes one bounded desired-state byte") {
    using namespace iotox::protocol;
    CommandRequest request;
    request.operation = CommandOperation::profile_status_set;
    request.desired_profile_status = CommandRequest::ProfileStatus::busy;
    auto encoded = encode_command_request(request);
    IOTOX_CHECK(encoded.ok());
    IOTOX_CHECK(encoded.value()[5U] == 3U);
    IOTOX_CHECK(encoded.value()[6U] == 2U);
    IOTOX_CHECK(encoded.value()[7U] == 0U);
    auto decoded = decode_command_request(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == request);

    auto invalid = encoded.value();
    invalid[6U] = 3U;
    IOTOX_CHECK(!decode_command_request(invalid));
    invalid = encoded.value();
    invalid[7U] = 1U;
    IOTOX_CHECK(!decode_command_request(invalid));

    request.desired_profile_status.reset();
    IOTOX_CHECK(!encode_command_request(request));
    request.operation = CommandOperation::system_summary;
    request.desired_profile_status = CommandRequest::ProfileStatus::away;
    IOTOX_CHECK(!encode_command_request(request));
}

IOTOX_TEST("profile status completion evidence proves exact convergence") {
    using namespace iotox::protocol;
    ProfileStatusEvidence evidence;
    evidence.desired = CommandRequest::ProfileStatus::away;
    evidence.observed = CommandRequest::ProfileStatus::away;
    auto encoded = encode_profile_status_evidence(evidence);
    IOTOX_CHECK(encoded.ok());
    IOTOX_CHECK(encoded.value()[0U] == 'I');
    IOTOX_CHECK(encoded.value()[3U] == '1');
    auto decoded = decode_profile_status_evidence(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == evidence);

    evidence.observed = CommandRequest::ProfileStatus::busy;
    IOTOX_CHECK(!encode_profile_status_evidence(evidence));
    auto noncanonical = encoded.value();
    noncanonical[6U] = 2U;
    IOTOX_CHECK(!decode_profile_status_evidence(noncanonical));
}

IOTOX_TEST("update.stage freezes one exact accepted HEAD and bounded evidence") {
    using namespace iotox::protocol;
    CommandRequest request;
    request.operation = CommandOperation::update_stage;
    UpdateHeadRecord head{};
    for (std::size_t index = 0U; index < head.size(); ++index) {
        head[index] = static_cast<std::uint8_t>(index + 1U);
    }
    request.expected_update_head = head;
    auto encoded = encode_command_request(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() == kUpdateStageCommandRequestBytes);
    IOTOX_CHECK(encoded.value()[3U] == '2');
    IOTOX_CHECK(encoded.value()[4U] == kUpdateStageCommandPayloadVersion);
    auto decoded = decode_command_request(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == request);

    auto reserved = encoded.value();
    reserved[6U] = 1U;
    IOTOX_CHECK(!decode_command_request(reserved));
    auto zero = request;
    zero.expected_update_head->fill(0U);
    IOTOX_CHECK(!encode_command_request(zero));
    request.expected_update_head.reset();
    IOTOX_CHECK(!encode_command_request(request));

    UpdateStageEvidence evidence;
    evidence.duplicate = true;
    evidence.release_sequence = 7U;
    evidence.accepted_head = head;
    evidence.manifest_record.fill(0xa5U);
    auto evidence_bytes = encode_update_stage_evidence(evidence);
    IOTOX_CHECK_MSG(evidence_bytes.ok(), evidence_bytes.status().message());
    IOTOX_CHECK(evidence_bytes.value().size() == kUpdateStageEvidenceBytes);
    auto decoded_evidence = decode_update_stage_evidence(
        evidence_bytes.value());
    IOTOX_CHECK_MSG(decoded_evidence.ok(),
                    decoded_evidence.status().message());
    IOTOX_CHECK(decoded_evidence.value() == evidence);
    auto malformed_evidence = evidence_bytes.value();
    malformed_evidence[7U] = 1U;
    IOTOX_CHECK(!decode_update_stage_evidence(malformed_evidence));
}


IOTOX_TEST("command receipts have one canonical bounded representation") {
    iotox::protocol::CommandReceipt receipt;
    receipt.stage = iotox::protocol::CommandReceiptStage::received;
    auto encoded = iotox::protocol::encode_command_receipt(receipt);
    IOTOX_CHECK(encoded.ok());
    IOTOX_CHECK(encoded.value().size() == iotox::protocol::kCommandReceiptBytes);
    auto decoded = iotox::protocol::decode_command_receipt(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == receipt);

    auto malformed = encoded.value();
    malformed[6U] = 1U;
    IOTOX_CHECK(!iotox::protocol::decode_command_receipt(malformed));
    receipt.stage = iotox::protocol::CommandReceiptStage::none;
    IOTOX_CHECK(!iotox::protocol::encode_command_receipt(receipt));
}

IOTOX_TEST("device description is fixed bounded and carries stable principal") {
    iotox::protocol::DeviceDescription description;
    description.revision_number = 9U;
    description.version_major = 0U;
    description.version_minor = 9U;
    description.version_patch = 0U;
    description.protocol = {1U, 0U};
    std::fill(description.device_principal.begin(),
              description.device_principal.end(), 0x42U);
    description.supported_features =
        iotox::protocol::kImplementedFeatureMask;
    description.offered_operations =
        iotox::protocol::implemented_operation_mask();

    auto encoded = iotox::protocol::encode_device_description(description);
    IOTOX_CHECK(encoded);
    IOTOX_CHECK(encoded.value().size() ==
                iotox::protocol::kDeviceDescriptionBytes);
    auto decoded =
        iotox::protocol::decode_device_description(encoded.value());
    IOTOX_CHECK(decoded);
    IOTOX_CHECK(decoded.value() == description);
    IOTOX_CHECK(iotox::protocol::render_device_description(decoded.value())
                    .find("offered-operations=device.describe") !=
                std::string::npos);

    auto zero_principal = description;
    zero_principal.device_principal.fill(0U);
    IOTOX_CHECK(!iotox::protocol::encode_device_description(zero_principal));
}

IOTOX_TEST("command results reject ambiguous bodies and preserve description") {
    iotox::protocol::DeviceDescription description;
    description.revision_number = 9U;
    description.version_minor = 9U;
    description.protocol = {1U, 0U};
    std::fill(description.device_principal.begin(),
              description.device_principal.end(), 0x24U);
    description.supported_features =
        iotox::protocol::kImplementedFeatureMask;
    description.offered_operations =
        iotox::protocol::implemented_operation_mask();
    auto body = iotox::protocol::encode_device_description(description);
    IOTOX_CHECK(body);

    iotox::protocol::CommandResultPayload result;
    result.operation = iotox::protocol::CommandOperation::device_describe;
    result.outcome = iotox::protocol::CommandOutcome::succeeded;
    result.body.assign(body.value().begin(), body.value().end());
    auto encoded = iotox::protocol::encode_command_result(result);
    IOTOX_CHECK(encoded);
    auto decoded = iotox::protocol::decode_command_result(encoded.value());
    IOTOX_CHECK(decoded);
    IOTOX_CHECK(decoded.value() == result);

    auto mismatch = encoded.value();
    IOTOX_CHECK(mismatch.size() > 11U);
    mismatch.at(11U) = 63U;
    IOTOX_CHECK(!iotox::protocol::decode_command_result(mismatch));

    result.outcome = iotox::protocol::CommandOutcome::denied;
    IOTOX_CHECK(!iotox::protocol::encode_command_result(result));
    result.body.clear();
    IOTOX_CHECK(iotox::protocol::encode_command_result(result));
}

IOTOX_TEST("system summary has one privacy-bounded canonical wire form") {
    using namespace iotox::protocol;
    SystemSummary summary;
    summary.health = SystemHealth::healthy;
    summary.flags = kSystemSummaryKnownFlags;
    summary.uptime_minutes = 1234U;
    summary.memory_total_64mib = 128U;
    summary.memory_available_64mib = 48U;
    summary.load_milli = 700U;
    summary.process_count = 91U;

    auto encoded = encode_system_summary(summary);
    IOTOX_CHECK(encoded.ok());
    IOTOX_CHECK(encoded.value().size() == kSystemSummaryBytes);
    IOTOX_CHECK(encoded.value()[0U] == 'I');
    IOTOX_CHECK(encoded.value()[3U] == '1');
    auto decoded = decode_system_summary(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == summary);
    const auto rendered = render_system_summary(summary);
    IOTOX_CHECK(rendered.find("uptime-minutes=1234") != std::string::npos);
    IOTOX_CHECK(rendered.find("hostname") == std::string::npos);

    auto reserved = encoded.value();
    reserved[39U] = 1U;
    IOTOX_CHECK(!decode_system_summary(reserved));
    auto invalid = summary;
    invalid.memory_available_64mib = 129U;
    IOTOX_CHECK(!encode_system_summary(invalid));
    invalid = summary;
    invalid.load_milli = 701U;
    IOTOX_CHECK(!encode_system_summary(invalid));
}

IOTOX_TEST("device.describe requires only read telemetry authority") {
    IOTOX_CHECK(iotox::protocol::required_capabilities(
                    iotox::protocol::CommandOperation::device_describe) ==
                static_cast<std::uint64_t>(
                    iotox::security::Capability::read_telemetry));
    IOTOX_CHECK(iotox::protocol::required_capabilities(
                    iotox::protocol::CommandOperation::unknown) == 0U);
}

IOTOX_TEST("command operation registry freezes name capability bit and restart policy") {
    using namespace iotox;
    using namespace iotox::protocol;

    const auto parsed = parse_command_operation("device.describe");
    IOTOX_CHECK(parsed.has_value());
    IOTOX_CHECK(*parsed == CommandOperation::device_describe);
    IOTOX_CHECK(!parse_command_operation("device.reset").has_value());
    const auto summary = parse_command_operation("system.summary");
    IOTOX_CHECK(summary.has_value());
    IOTOX_CHECK(*summary == CommandOperation::system_summary);
    const auto summary_policy = command_operation_policy(*summary);
    IOTOX_CHECK(summary_policy.has_value());
    IOTOX_CHECK(summary_policy->advertised_bit == kSystemSummaryOperationBit);
    IOTOX_CHECK(summary_policy->required_capabilities ==
                static_cast<std::uint64_t>(
                    security::Capability::read_telemetry));
    IOTOX_CHECK(command_restart_safe(*summary));
    const auto mutation = parse_command_operation("profile.status.set");
    IOTOX_CHECK(mutation.has_value());
    IOTOX_CHECK(*mutation == CommandOperation::profile_status_set);
    const auto mutation_policy = command_operation_policy(*mutation);
    IOTOX_CHECK(mutation_policy.has_value());
    IOTOX_CHECK(!mutation_policy->read_only);
    IOTOX_CHECK(mutation_policy->required_capabilities ==
                static_cast<std::uint64_t>(
                    security::Capability::write_settings));
    IOTOX_CHECK(mutation_policy->restart_policy ==
                CommandRestartPolicy::reexecute_idempotent_desired_state);
    IOTOX_CHECK(command_restart_safe(*mutation));
    const auto update = parse_command_operation("update.stage");
    IOTOX_CHECK(update.has_value());
    IOTOX_CHECK(*update == CommandOperation::update_stage);
    const auto update_policy = command_operation_policy(*update);
    IOTOX_CHECK(update_policy.has_value());
    IOTOX_CHECK(!update_policy->read_only);
    IOTOX_CHECK(update_policy->required_capabilities ==
                static_cast<std::uint64_t>(
                    security::Capability::install_firmware));
    IOTOX_CHECK(update_policy->restart_policy ==
                CommandRestartPolicy::reexecute_idempotent_desired_state);
    IOTOX_CHECK(command_restart_safe(*update));

    const auto policy = command_operation_policy(*parsed);
    IOTOX_CHECK(policy.has_value());
    IOTOX_CHECK(policy->name == "device.describe");
    IOTOX_CHECK(policy->advertised_bit == kDeviceDescribeOperationBit);
    IOTOX_CHECK(policy->required_capabilities ==
                static_cast<std::uint64_t>(
                    security::Capability::read_telemetry));
    IOTOX_CHECK(policy->read_only);
    IOTOX_CHECK(policy->restart_policy ==
                CommandRestartPolicy::reexecute_read_only);
    IOTOX_CHECK(command_restart_safe(*parsed));
    IOTOX_CHECK(!command_restart_safe(CommandOperation::unknown));
    IOTOX_CHECK(implemented_operation_mask() ==
                (kDeviceDescribeOperationBit | kSystemSummaryOperationBit |
                 kProfileStatusSetOperationBit | kUpdateStageOperationBit));
}
