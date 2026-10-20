#include "iotox/command_engine.hpp"

#include <algorithm>

namespace iotox {
namespace {

bool all_zero(const security::SigningPublicKey &key) noexcept {
    return std::all_of(key.begin(), key.end(),
                       [](std::uint8_t value) { return value == 0U; });
}

}  // namespace

Result<protocol::CommandResultPayload> execute_command(
    const protocol::CommandRequest &request,
    const CommandExecutionContext &context) {
    protocol::CommandResultPayload result;
    result.operation = request.operation;

    if (request.operation == protocol::CommandOperation::unknown) {
        result.outcome = protocol::CommandOutcome::unsupported;
        return result;
    }

    if (request.operation == protocol::CommandOperation::system_summary) {
        if (!context.system_summary.has_value()) {
            return Status{ErrorCode::internal_error,
                          "system.summary executor context is incomplete"};
        }
        auto encoded = protocol::encode_system_summary(*context.system_summary);
        if (!encoded) {
            return encoded.status();
        }
        result.outcome = protocol::CommandOutcome::succeeded;
        result.body.assign(encoded.value().begin(), encoded.value().end());
        return result;
    }

    if (request.operation == protocol::CommandOperation::profile_status_set) {
        if (!request.desired_profile_status.has_value() ||
            !context.observed_profile_status.has_value()) {
            return Status{ErrorCode::internal_error,
                          "profile.status.set executor context is incomplete"};
        }
        protocol::ProfileStatusEvidence evidence;
        evidence.desired = *request.desired_profile_status;
        evidence.observed = *context.observed_profile_status;
        auto encoded = protocol::encode_profile_status_evidence(evidence);
        if (!encoded) {
            return encoded.status();
        }
        result.outcome = protocol::CommandOutcome::succeeded;
        result.body.assign(encoded.value().begin(), encoded.value().end());
        return result;
    }

    if (request.operation == protocol::CommandOperation::update_stage) {
        if (!request.expected_update_head.has_value() ||
            !context.update_stage_evidence.has_value() ||
            context.update_stage_evidence->accepted_head !=
                *request.expected_update_head) {
            return Status{ErrorCode::internal_error,
                          "update.stage executor context is incomplete or does not bind the request"};
        }
        auto encoded = protocol::encode_update_stage_evidence(
            *context.update_stage_evidence);
        if (!encoded) {
            return encoded.status();
        }
        result.outcome = protocol::CommandOutcome::succeeded;
        result.body.assign(encoded.value().begin(), encoded.value().end());
        return result;
    }

    if (request.operation != protocol::CommandOperation::device_describe) {
        result.outcome = protocol::CommandOutcome::unsupported;
        return result;
    }

    if (context.revision_number == 0U ||
        context.protocol.major == 0U ||
        all_zero(context.device_principal)) {
        return Status{ErrorCode::internal_error,
                      "device.describe executor context is incomplete"};
    }

    protocol::DeviceDescription description;
    description.revision_number = context.revision_number;
    description.version_major = context.version_major;
    description.version_minor = context.version_minor;
    description.version_patch = context.version_patch;
    description.protocol = context.protocol;
    description.device_principal = context.device_principal;
    description.supported_features = context.supported_features;
    description.offered_operations = context.offered_operations;

    auto encoded = protocol::encode_device_description(description);
    if (!encoded) {
        return encoded.status();
    }
    result.outcome = protocol::CommandOutcome::succeeded;
    result.body.assign(encoded.value().begin(), encoded.value().end());
    return result;
}

}  // namespace iotox
