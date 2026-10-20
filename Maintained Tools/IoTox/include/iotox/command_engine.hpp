#pragma once

#include "iotox/protocol/command.hpp"
#include "iotox/status.hpp"

#include <cstdint>
#include <optional>

namespace iotox {

// CommandExecutionContext is the complete, immutable product context an
// operation executor may inspect. It deliberately contains no transport,
// filesystem, journal, or authorization handles: admission and durability are
// the Agent's responsibility, while execution is a typed deterministic step.
struct CommandExecutionContext {
    std::uint16_t revision_number{0U};
    std::uint16_t version_major{0U};
    std::uint16_t version_minor{0U};
    std::uint16_t version_patch{0U};
    protocol::ProtocolVersion protocol{};
    security::SigningPublicKey device_principal{};
    std::uint64_t supported_features{0U};
    std::uint64_t offered_operations{0U};
    std::optional<protocol::SystemSummary> system_summary;
    std::optional<protocol::CommandRequest::ProfileStatus>
        observed_profile_status;
    std::optional<protocol::UpdateStageEvidence> update_stage_evidence;
};

// Execute one already-decoded, already-authorized operation. Unsupported
// operations produce an ordinary COMMAND_RESULT outcome; malformed executor
// context is reported as a local Status because the caller cannot safely claim
// that the operation ran.
[[nodiscard]] Result<protocol::CommandResultPayload> execute_command(
    const protocol::CommandRequest &request,
    const CommandExecutionContext &context);

}  // namespace iotox
