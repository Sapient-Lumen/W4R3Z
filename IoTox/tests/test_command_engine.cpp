#include "iotox/command_engine.hpp"
#include "iotox/protocol/command.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/system_summary.hpp"
#include "test_harness.hpp"

#include <algorithm>

IOTOX_TEST("command executor renders device.describe without transport or storage") {
    iotox::CommandExecutionContext context;
    context.revision_number = 11U;
    context.version_major = 0U;
    context.version_minor = 11U;
    context.version_patch = 0U;
    context.protocol = {1U, 0U};
    std::fill(context.device_principal.begin(),
              context.device_principal.end(), 0x5AU);
    context.supported_features = iotox::protocol::kImplementedFeatureMask;
    context.offered_operations =
        iotox::protocol::implemented_operation_mask();

    auto result = iotox::execute_command(
        {iotox::protocol::CommandOperation::device_describe}, context);
    IOTOX_CHECK_MSG(result.ok(), result.status().message());
    IOTOX_CHECK(result.value().outcome ==
                iotox::protocol::CommandOutcome::succeeded);
    IOTOX_CHECK(result.value().body.size() ==
                iotox::protocol::kDeviceDescriptionBytes);

    auto decoded = iotox::protocol::decode_device_description(
        result.value().body);
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value().revision_number == 11U);
    IOTOX_CHECK(decoded.value().version_minor == 11U);
    const iotox::protocol::ProtocolVersion expected_protocol{1U, 0U};
    IOTOX_CHECK(decoded.value().protocol == expected_protocol);
    IOTOX_CHECK(decoded.value().device_principal ==
                context.device_principal);
}

IOTOX_TEST("command executor fails closed on incomplete identity context") {
    iotox::CommandExecutionContext context;
    context.revision_number = 11U;
    context.version_minor = 11U;
    context.protocol = {1U, 0U};

    auto incomplete = iotox::execute_command(
        {iotox::protocol::CommandOperation::device_describe}, context);
    IOTOX_CHECK(!incomplete.ok());
    IOTOX_CHECK(incomplete.status().code() ==
                iotox::ErrorCode::internal_error);

    auto unsupported = iotox::execute_command(
        {iotox::protocol::CommandOperation::unknown}, context);
    IOTOX_CHECK(unsupported.ok());
    IOTOX_CHECK(unsupported.value().outcome ==
                iotox::protocol::CommandOutcome::unsupported);
    IOTOX_CHECK(unsupported.value().body.empty());
}

IOTOX_TEST("command executor emits only the injected system summary") {
    iotox::CommandExecutionContext context;
    iotox::protocol::SystemSummary summary;
    summary.health = iotox::protocol::SystemHealth::degraded;
    summary.flags = iotox::protocol::kSystemSummaryLoadValid;
    summary.uptime_minutes = 60U;
    summary.load_milli = 1200U;
    context.system_summary = summary;

    auto result = iotox::execute_command(
        {iotox::protocol::CommandOperation::system_summary}, context);
    IOTOX_CHECK_MSG(result.ok(), result.status().message());
    IOTOX_CHECK(result.value().outcome ==
                iotox::protocol::CommandOutcome::succeeded);
    auto decoded = iotox::protocol::decode_system_summary(result.value().body);
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == summary);

    context.system_summary.reset();
    auto absent = iotox::execute_command(
        {iotox::protocol::CommandOperation::system_summary}, context);
    IOTOX_CHECK(!absent.ok());
}

IOTOX_TEST("command executor binds desired and observed profile status") {
    using namespace iotox;
    protocol::CommandRequest request;
    request.operation = protocol::CommandOperation::profile_status_set;
    request.desired_profile_status =
        protocol::CommandRequest::ProfileStatus::busy;
    CommandExecutionContext context;
    context.observed_profile_status =
        protocol::CommandRequest::ProfileStatus::busy;

    auto result = execute_command(request, context);
    IOTOX_CHECK_MSG(result.ok(), result.status().message());
    IOTOX_CHECK(result.value().outcome ==
                protocol::CommandOutcome::succeeded);
    auto evidence = protocol::decode_profile_status_evidence(
        result.value().body);
    IOTOX_CHECK_MSG(evidence.ok(), evidence.status().message());
    IOTOX_CHECK(evidence.value().desired ==
                protocol::CommandRequest::ProfileStatus::busy);
    IOTOX_CHECK(evidence.value().observed ==
                protocol::CommandRequest::ProfileStatus::busy);

    context.observed_profile_status =
        protocol::CommandRequest::ProfileStatus::away;
    IOTOX_CHECK(!execute_command(request, context));
    context.observed_profile_status.reset();
    IOTOX_CHECK(!execute_command(request, context));
}

IOTOX_TEST("command executor binds remote update staging to the exact accepted HEAD") {
    using namespace iotox;
    protocol::CommandRequest request;
    request.operation = protocol::CommandOperation::update_stage;
    protocol::UpdateHeadRecord head{};
    head.fill(0x31U);
    request.expected_update_head = head;

    CommandExecutionContext context;
    protocol::UpdateStageEvidence evidence;
    evidence.release_sequence = 9U;
    evidence.accepted_head = head;
    evidence.manifest_record.fill(0x72U);
    context.update_stage_evidence = evidence;
    auto result = execute_command(request, context);
    IOTOX_CHECK_MSG(result.ok(), result.status().message());
    IOTOX_CHECK(result.value().outcome ==
                protocol::CommandOutcome::succeeded);
    auto decoded = protocol::decode_update_stage_evidence(
        result.value().body);
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == evidence);

    context.update_stage_evidence->accepted_head.fill(0x32U);
    IOTOX_CHECK(!execute_command(request, context));
    context.update_stage_evidence.reset();
    IOTOX_CHECK(!execute_command(request, context));
}

IOTOX_TEST("linux system summary collector honors coarse public bounds") {
    auto summary = iotox::collect_system_summary();
    IOTOX_CHECK_MSG(summary.ok(), summary.status().message());
    IOTOX_CHECK(summary.value().memory_available_64mib <=
                summary.value().memory_total_64mib);
    IOTOX_CHECK(summary.value().load_milli % 100U == 0U);
    IOTOX_CHECK(summary.value().flags ==
                iotox::protocol::kSystemSummaryKnownFlags);
    auto encoded = iotox::protocol::encode_system_summary(summary.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
}
