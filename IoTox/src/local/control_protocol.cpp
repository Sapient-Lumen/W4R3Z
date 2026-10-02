#include "iotox/local/control_protocol.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <optional>
#include <string_view>
#include <utility>

namespace iotox::local {
namespace {

constexpr std::array<std::uint8_t, 4U> kMagic = {'I', 'T', 'L', 'C'};

void append_u16(std::vector<std::uint8_t> &output, std::uint16_t value) {
    output.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xFFU));
    output.push_back(static_cast<std::uint8_t>(value & 0xFFU));
}

void append_u32(std::vector<std::uint8_t> &output, std::uint32_t value) {
    for (int shift = 24; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>((value >> static_cast<unsigned int>(shift)) & 0xFFU));
    }
}

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>((value >> static_cast<unsigned int>(shift)) & 0xFFU));
    }
}

std::uint16_t read_u16(std::span<const std::uint8_t> bytes, std::size_t offset) {
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(bytes[offset]) << 8U) |
                                      static_cast<std::uint16_t>(bytes[offset + 1U]));
}

std::uint32_t read_u32(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>((value << 8U) | bytes[offset + index]);
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

bool valid_kind(std::uint8_t value) {
    return value == static_cast<std::uint8_t>(ControlKind::request) ||
           value == static_cast<std::uint8_t>(ControlKind::response);
}

bool valid_operation(std::uint8_t value) {
    switch (static_cast<ControlOperation>(value)) {
        case ControlOperation::ping:
        case ControlOperation::inspect:
        case ControlOperation::address:
        case ControlOperation::shutdown:
        case ControlOperation::self_profile:
        case ControlOperation::self_set_name:
        case ControlOperation::self_set_status_message:
        case ControlOperation::self_set_status:
        case ControlOperation::transport_peer_add:
        case ControlOperation::transport_send_lossless:
        case ControlOperation::transport_peer_request:
        case ControlOperation::transport_peer_remove:
        case ControlOperation::transport_peer_list:
        case ControlOperation::transport_send_message:
        case ControlOperation::transport_set_typing:
        case ControlOperation::transport_friend_request_list:
        case ControlOperation::transport_friend_request_reject:
        case ControlOperation::protocol_send_hello:
        case ControlOperation::protocol_session_list:
        case ControlOperation::protocol_session_show:
        case ControlOperation::transport_friend_request_accept:
        case ControlOperation::protocol_send_confirmation:
        case ControlOperation::transport_peer_remove_key:
        case ControlOperation::transport_message_probe:
        case ControlOperation::transport_file_send_path:
        case ControlOperation::transport_file_receive_path:
        case ControlOperation::transport_file_cancel:
        case ControlOperation::transport_file_list:
        case ControlOperation::transport_file_control:
        case ControlOperation::transport_packet_probe:
        case ControlOperation::transport_packet_probe_burst:
        case ControlOperation::transport_route_health:
        case ControlOperation::identity_show:
        case ControlOperation::authority_show:
        case ControlOperation::authority_principal_list:
        case ControlOperation::authority_prepare:
        case ControlOperation::authority_append:
        case ControlOperation::authority_session_list:
        case ControlOperation::authority_session_show:
        case ControlOperation::authority_challenge_send:
        case ControlOperation::authority_proof_prepare:
        case ControlOperation::authority_proof_send:
        case ControlOperation::authority_device_proof_send:
        case ControlOperation::protocol_device_describe:
        case ControlOperation::protocol_peer_description_show:
        case ControlOperation::command_store_show:
        case ControlOperation::command_record_show:
        case ControlOperation::command_issue:
        case ControlOperation::authority_remote_delegation_send:
        case ControlOperation::authority_remote_delegation_prepare:
        case ControlOperation::authority_remote_delegation_retry:
        case ControlOperation::authority_remote_delegation_show:
        case ControlOperation::authority_remote_revocation_prepare:
        case ControlOperation::authority_remote_successor_prepare:
        case ControlOperation::authority_remote_epoch_transition_prepare:
        case ControlOperation::command_cancel:
        case ControlOperation::authority_remote_migration_prepare:
        case ControlOperation::authority_remote_v3_migration_prepare:
        case ControlOperation::route_inventory_show:
        case ControlOperation::sync_namespace_list:
        case ControlOperation::sync_pull:
        case ControlOperation::sync_status:
        case ControlOperation::sync_publish:
        case ControlOperation::sync_activate:
        case ControlOperation::sync_namespace_install:
        case ControlOperation::sync_cancel:
        case ControlOperation::sync_namespace_update:
        case ControlOperation::sync_namespace_remove:
        case ControlOperation::sync_repair:
        case ControlOperation::sync_gc:
        case ControlOperation::transport_interactive_evidence:
        case ControlOperation::update_status:
        case ControlOperation::update_stage:
        case ControlOperation::update_apply:
        case ControlOperation::update_confirm:
        case ControlOperation::update_gc:
        case ControlOperation::transport_route_target_health:
        case ControlOperation::sync_pull_policy:
        case ControlOperation::sync_pull_route_policy:
        case ControlOperation::sync_content_source_add:
        case ControlOperation::sync_content_pull_multi:
        case ControlOperation::sync_content_replica_import:
        case ControlOperation::sync_content_pull_multi_route:
        case ControlOperation::sync_automation_list:
        case ControlOperation::sync_automation_publish:
        case ControlOperation::sync_automation_follow:
        case ControlOperation::sync_automation_remove:
        case ControlOperation::sync_create:
        case ControlOperation::sync_share_prepare:
        case ControlOperation::sync_share_commit:
        case ControlOperation::sync_share_read_write_prepare:
        case ControlOperation::sync_share_read_write_commit:
        case ControlOperation::sync_tree_checkpoint:
        case ControlOperation::sync_tree_pin:
        case ControlOperation::sync_tree_unpin:
        case ControlOperation::sync_tree_maintenance_show:
        case ControlOperation::sync_tree_restore:
        case ControlOperation::sync_tree_writer_cutoff:
        case ControlOperation::ratox_client_session_list:
        case ControlOperation::ratox_client_session_close:
        case ControlOperation::diagnostics_export:
        case ControlOperation::peer_alias_list:
        case ControlOperation::peer_alias_set:
        case ControlOperation::peer_alias_rename:
        case ControlOperation::peer_alias_remove:
        case ControlOperation::peer_alias_resolve:
        case ControlOperation::peer_invitation_create:
        case ControlOperation::sync_tree_history:
        case ControlOperation::sync_tree_diff:
        case ControlOperation::sync_tree_conflicts:
        case ControlOperation::sync_tree_restore_plan:
        case ControlOperation::sync_tree_restore_forward:
        case ControlOperation::sync_tree_interest:
        case ControlOperation::sync_tree_interest_clear:
        case ControlOperation::sync_namespace_health:
            return true;
    }
    return false;
}

bool valid_error_code(std::uint16_t value) {
    return value <= static_cast<std::uint16_t>(ErrorCode::resource_exhausted);
}

std::optional<PresenceStatus> decode_presence(std::uint8_t value) {
    switch (value) {
        case 0U:
            return PresenceStatus::available;
        case 1U:
            return PresenceStatus::away;
        case 2U:
            return PresenceStatus::busy;
        default:
            return std::nullopt;
    }
}

std::uint8_t encode_presence(PresenceStatus status) {
    switch (status) {
        case PresenceStatus::available:
            return 0U;
        case PresenceStatus::away:
            return 1U;
        case PresenceStatus::busy:
            return 2U;
    }
    return 0U;
}

bool can_read(
    std::span<const std::uint8_t> payload, std::size_t offset,
    std::size_t length) {
    return offset <= payload.size() && length <= payload.size() - offset;
}

Result<std::vector<std::uint8_t>> read_bounded_bytes(
    std::span<const std::uint8_t> payload, std::size_t &offset,
    std::size_t maximum, std::string_view label) {
    if (!can_read(payload, offset, 4U)) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " length is truncated"};
    }
    const std::uint32_t length = read_u32(payload, offset);
    offset += 4U;
    if (length > maximum) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " exceeds its protocol bound"};
    }
    if (!can_read(payload, offset, length)) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " bytes are truncated"};
    }
    std::vector<std::uint8_t> value(
        payload.begin() + static_cast<std::ptrdiff_t>(offset),
        payload.begin() + static_cast<std::ptrdiff_t>(offset + length));
    offset += length;
    return value;
}

}  // namespace

Result<std::vector<std::uint8_t>> encode_control_packet(const ControlPacket &packet) {
    if (packet.payload.size() > kControlMaxPayloadSize) {
        return Status{ErrorCode::invalid_argument,
                      "local control payload exceeds " +
                          std::to_string(kControlMaxPayloadSize) + " bytes"};
    }
    if (packet.kind == ControlKind::request && packet.status != ErrorCode::ok) {
        return Status{ErrorCode::invalid_argument,
                      "local control requests must carry status=ok"};
    }
    if (packet.request_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "local control request id zero is reserved"};
    }
    if (packet.payload.size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::invalid_argument, "local control payload cannot be represented"};
    }

    std::vector<std::uint8_t> output;
    output.reserve(kControlHeaderSize + packet.payload.size());
    output.insert(output.end(), kMagic.begin(), kMagic.end());
    output.push_back(kControlProtocolMajor);
    output.push_back(kControlProtocolMinor);
    output.push_back(static_cast<std::uint8_t>(packet.kind));
    output.push_back(static_cast<std::uint8_t>(packet.operation));
    append_u64(output, packet.request_id);
    append_u16(output, static_cast<std::uint16_t>(packet.status));
    append_u16(output, 0U);  // reserved; must remain zero until assigned by an ADR.
    append_u32(output, static_cast<std::uint32_t>(packet.payload.size()));
    output.insert(output.end(), packet.payload.begin(), packet.payload.end());
    return output;
}

Result<ControlPacket> decode_control_packet(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kControlHeaderSize) {
        return Status{ErrorCode::protocol_error, "local control packet is truncated"};
    }
    if (bytes.size() > kControlMaxPacketSize) {
        return Status{ErrorCode::protocol_error, "local control packet exceeds the protocol limit"};
    }
    for (std::size_t index = 0U; index < kMagic.size(); ++index) {
        if (bytes[index] != kMagic[index]) {
            return Status{ErrorCode::protocol_error, "local control packet magic is invalid"};
        }
    }
    if (bytes[4U] != kControlProtocolMajor) {
        return Status{ErrorCode::unsupported,
                      "unsupported local control protocol major " +
                          std::to_string(bytes[4U])};
    }
    if (bytes[5U] > kControlProtocolMinor) {
        return Status{ErrorCode::unsupported,
                      "unsupported local control protocol minor " +
                          std::to_string(bytes[5U])};
    }
    if (!valid_kind(bytes[6U])) {
        return Status{ErrorCode::protocol_error, "local control packet kind is invalid"};
    }
    if (!valid_operation(bytes[7U])) {
        return Status{ErrorCode::unsupported, "local control operation is not defined"};
    }

    const std::uint64_t request_id = read_u64(bytes, 8U);
    if (request_id == 0U) {
        return Status{ErrorCode::protocol_error, "local control request id zero is reserved"};
    }

    const std::uint16_t raw_status = read_u16(bytes, 16U);
    if (!valid_error_code(raw_status)) {
        return Status{ErrorCode::protocol_error, "local control status code is invalid"};
    }
    if (read_u16(bytes, 18U) != 0U) {
        return Status{ErrorCode::unsupported,
                      "local control reserved header bits are nonzero"};
    }

    const std::uint32_t payload_size = read_u32(bytes, 20U);
    if (payload_size > kControlMaxPayloadSize) {
        return Status{ErrorCode::protocol_error, "local control payload length exceeds the limit"};
    }
    if (bytes.size() != kControlHeaderSize + static_cast<std::size_t>(payload_size)) {
        return Status{ErrorCode::protocol_error,
                      "local control payload length does not match the packet"};
    }

    ControlPacket packet;
    packet.kind = static_cast<ControlKind>(bytes[6U]);
    packet.operation = static_cast<ControlOperation>(bytes[7U]);
    packet.request_id = request_id;
    packet.status = static_cast<ErrorCode>(raw_status);
    packet.payload.assign(bytes.begin() + static_cast<std::ptrdiff_t>(kControlHeaderSize), bytes.end());

    if (packet.kind == ControlKind::request && packet.status != ErrorCode::ok) {
        return Status{ErrorCode::protocol_error,
                      "local control request carries a non-success status"};
    }
    return packet;
}

std::string to_string(ControlKind kind) {
    switch (kind) {
        case ControlKind::request:
            return "request";
        case ControlKind::response:
            return "response";
    }
    return "unknown";
}

std::string to_string(ControlOperation operation) {
    switch (operation) {
        case ControlOperation::ping:
            return "ping";
        case ControlOperation::inspect:
            return "inspect";
        case ControlOperation::address:
            return "address";
        case ControlOperation::shutdown:
            return "shutdown";
        case ControlOperation::self_profile:
            return "self-profile";
        case ControlOperation::self_set_name:
            return "self-set-name";
        case ControlOperation::self_set_status_message:
            return "self-set-status-message";
        case ControlOperation::self_set_status:
            return "self-set-status";
        case ControlOperation::transport_peer_add:
            return "transport-peer-add";
        case ControlOperation::transport_send_lossless:
            return "transport-send-lossless";
        case ControlOperation::transport_peer_request:
            return "transport-peer-request";
        case ControlOperation::transport_peer_remove:
            return "transport-peer-remove";
        case ControlOperation::transport_peer_list:
            return "transport-peer-list";
        case ControlOperation::transport_send_message:
            return "transport-send-message";
        case ControlOperation::transport_set_typing:
            return "transport-set-typing";
        case ControlOperation::transport_friend_request_list:
            return "transport-friend-request-list";
        case ControlOperation::transport_friend_request_reject:
            return "transport-friend-request-reject";
        case ControlOperation::protocol_send_hello:
            return "protocol-send-hello";
        case ControlOperation::protocol_session_list:
            return "protocol-session-list";
        case ControlOperation::protocol_session_show:
            return "protocol-session-show";
        case ControlOperation::transport_friend_request_accept:
            return "transport-friend-request-accept";
        case ControlOperation::protocol_send_confirmation:
            return "protocol-send-confirmation";
        case ControlOperation::transport_peer_remove_key:
            return "transport-peer-remove-key";
        case ControlOperation::transport_message_probe:
            return "transport-message-probe";
        case ControlOperation::transport_file_send_path:
            return "transport-file-send-path";
        case ControlOperation::transport_file_receive_path:
            return "transport-file-receive-path";
        case ControlOperation::transport_file_cancel:
            return "transport-file-cancel";
        case ControlOperation::transport_file_list:
            return "transport-file-list";
        case ControlOperation::transport_file_control:
            return "transport-file-control";
        case ControlOperation::transport_packet_probe:
            return "transport-packet-probe";
        case ControlOperation::transport_packet_probe_burst:
            return "transport-packet-probe-burst";
        case ControlOperation::transport_route_health:
            return "transport-route-health";
        case ControlOperation::identity_show:
            return "identity-show";
        case ControlOperation::authority_show:
            return "authority-show";
        case ControlOperation::authority_principal_list:
            return "authority-principal-list";
        case ControlOperation::authority_prepare:
            return "authority-prepare";
        case ControlOperation::authority_append:
            return "authority-append";
        case ControlOperation::authority_session_list:
            return "authority-session-list";
        case ControlOperation::authority_session_show:
            return "authority-session-show";
        case ControlOperation::authority_challenge_send:
            return "authority-challenge-send";
        case ControlOperation::authority_proof_prepare:
            return "authority-proof-prepare";
        case ControlOperation::authority_proof_send:
            return "authority-proof-send";
        case ControlOperation::authority_device_proof_send:
            return "authority-device-proof-send";
        case ControlOperation::protocol_device_describe:
            return "protocol-device-describe";
        case ControlOperation::protocol_peer_description_show:
            return "protocol-peer-description-show";
        case ControlOperation::command_store_show:
            return "command-store-show";
        case ControlOperation::command_record_show:
            return "command-record-show";
        case ControlOperation::command_issue:
            return "command-issue";
        case ControlOperation::authority_remote_delegation_send:
            return "authority-remote-delegation-send";
        case ControlOperation::authority_remote_delegation_prepare:
            return "authority-remote-delegation-prepare";
        case ControlOperation::authority_remote_delegation_retry:
            return "authority-remote-delegation-retry";
        case ControlOperation::authority_remote_delegation_show:
            return "authority-remote-delegation-show";
        case ControlOperation::authority_remote_revocation_prepare:
            return "authority-remote-revocation-prepare";
        case ControlOperation::authority_remote_successor_prepare:
            return "authority-remote-successor-prepare";
        case ControlOperation::authority_remote_epoch_transition_prepare:
            return "authority-remote-epoch-transition-prepare";
        case ControlOperation::command_cancel:
            return "command-cancel";
        case ControlOperation::authority_remote_migration_prepare:
            return "authority-remote-migration-prepare";
        case ControlOperation::authority_remote_v3_migration_prepare:
            return "authority-remote-v3-migration-prepare";
        case ControlOperation::route_inventory_show:
            return "route-inventory-show";
        case ControlOperation::sync_namespace_list:
            return "sync-namespace-list";
        case ControlOperation::sync_pull:
            return "sync-pull";
        case ControlOperation::sync_status:
            return "sync-status";
        case ControlOperation::sync_publish:
            return "sync-publish";
        case ControlOperation::sync_activate:
            return "sync-activate";
        case ControlOperation::sync_namespace_install:
            return "sync-namespace-install";
        case ControlOperation::sync_cancel:
            return "sync-cancel";
        case ControlOperation::sync_namespace_update:
            return "sync-namespace-update";
        case ControlOperation::sync_namespace_remove:
            return "sync-namespace-remove";
        case ControlOperation::sync_repair:
            return "sync-repair";
        case ControlOperation::sync_gc:
            return "sync-gc";
        case ControlOperation::transport_interactive_evidence:
            return "transport-interactive-evidence";
        case ControlOperation::update_status:
            return "update-status";
        case ControlOperation::update_stage:
            return "update-stage";
        case ControlOperation::update_apply:
            return "update-apply";
        case ControlOperation::update_confirm:
            return "update-confirm";
        case ControlOperation::update_gc:
            return "update-gc";
        case ControlOperation::transport_route_target_health:
            return "transport-route-target-health";
        case ControlOperation::sync_pull_policy:
            return "sync-pull-policy";
        case ControlOperation::sync_pull_route_policy:
            return "sync-pull-route-policy";
        case ControlOperation::sync_content_source_add:
            return "sync-content-source-add";
        case ControlOperation::sync_content_pull_multi:
            return "sync-content-pull-multi";
        case ControlOperation::sync_content_replica_import:
            return "sync-content-replica-import";
        case ControlOperation::sync_content_pull_multi_route:
            return "sync-content-pull-multi-route";
        case ControlOperation::sync_automation_list:
            return "sync-automation-list";
        case ControlOperation::sync_automation_publish:
            return "sync-automation-publish";
        case ControlOperation::sync_automation_follow:
            return "sync-automation-follow";
        case ControlOperation::sync_automation_remove:
            return "sync-automation-remove";
        case ControlOperation::sync_create:
            return "sync-create";
        case ControlOperation::sync_share_prepare:
            return "sync-share-prepare";
        case ControlOperation::sync_share_commit:
            return "sync-share-commit";
        case ControlOperation::sync_share_read_write_prepare:
            return "sync-share-read-write-prepare";
        case ControlOperation::sync_share_read_write_commit:
            return "sync-share-read-write-commit";
        case ControlOperation::sync_tree_checkpoint:
            return "sync-tree-checkpoint";
        case ControlOperation::sync_tree_pin:
            return "sync-tree-pin";
        case ControlOperation::sync_tree_unpin:
            return "sync-tree-unpin";
        case ControlOperation::sync_tree_maintenance_show:
            return "sync-tree-maintenance-show";
        case ControlOperation::sync_tree_restore:
            return "sync-tree-restore";
        case ControlOperation::sync_tree_writer_cutoff:
            return "sync-tree-writer-cutoff";
        case ControlOperation::ratox_client_session_list:
            return "ratox-client-session-list";
        case ControlOperation::ratox_client_session_close:
            return "ratox-client-session-close";
        case ControlOperation::diagnostics_export:
            return "diagnostics-export";
        case ControlOperation::peer_alias_list:
            return "peer-alias-list";
        case ControlOperation::peer_alias_set:
            return "peer-alias-set";
        case ControlOperation::peer_alias_rename:
            return "peer-alias-rename";
        case ControlOperation::peer_alias_remove:
            return "peer-alias-remove";
        case ControlOperation::peer_alias_resolve:
            return "peer-alias-resolve";
        case ControlOperation::peer_invitation_create:
            return "peer-invitation-create";
        case ControlOperation::sync_tree_history:
            return "sync-tree-history";
        case ControlOperation::sync_tree_diff:
            return "sync-tree-diff";
        case ControlOperation::sync_tree_conflicts:
            return "sync-tree-conflicts";
        case ControlOperation::sync_tree_restore_plan:
            return "sync-tree-restore-plan";
        case ControlOperation::sync_tree_restore_forward:
            return "sync-tree-restore-forward";
        case ControlOperation::sync_tree_interest:
            return "sync-tree-interest";
        case ControlOperation::sync_tree_interest_clear:
            return "sync-tree-interest-clear";
        case ControlOperation::sync_namespace_health:
            return "sync-namespace-health";
    }
    return "unknown";
}

std::vector<std::uint8_t> encode_interactive_transport_evidence(
    const InteractiveTransportEvidence &evidence) {
    std::vector<std::uint8_t> output;
    output.reserve(16U);
    append_u64(output, evidence.executed_commands);
    append_u64(output, evidence.total_queue_wait_us);
    return output;
}

Result<InteractiveTransportEvidence>
decode_interactive_transport_evidence(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != 16U) {
        return Status{
            ErrorCode::protocol_error,
            "interactive transport evidence must be exactly 16 bytes"};
    }
    return InteractiveTransportEvidence{
        read_u64(payload, 0U), read_u64(payload, 8U)};
}

Result<std::vector<std::uint8_t>> encode_self_profile(
    const SelfProfile &profile) {
    if (profile.name.size() > toxcore::abi::kMaxNameLength ||
        profile.status_message.size() > toxcore::abi::kMaxStatusMessageLength) {
        return Status{ErrorCode::invalid_argument,
                      "self profile exceeds c-toxcore bounds"};
    }
    std::vector<std::uint8_t> output;
    output.reserve(
        4U + profile.name.size() + 4U + profile.status_message.size() + 1U);
    append_u32(output, static_cast<std::uint32_t>(profile.name.size()));
    output.insert(output.end(), profile.name.begin(), profile.name.end());
    append_u32(
        output, static_cast<std::uint32_t>(profile.status_message.size()));
    output.insert(
        output.end(), profile.status_message.begin(), profile.status_message.end());
    output.push_back(encode_presence(profile.status));
    return output;
}

Result<SelfProfile> decode_self_profile(
    std::span<const std::uint8_t> payload) {
    std::size_t offset = 0U;
    auto name = read_bounded_bytes(
        payload, offset, toxcore::abi::kMaxNameLength, "self name");
    if (!name) {
        return name.status();
    }
    auto status_message = read_bounded_bytes(
        payload, offset, toxcore::abi::kMaxStatusMessageLength,
        "self status message");
    if (!status_message) {
        return status_message.status();
    }
    if (!can_read(payload, offset, 1U) || offset + 1U != payload.size()) {
        return Status{ErrorCode::protocol_error,
                      "self profile status byte is missing or has trailing data"};
    }
    const auto status = decode_presence(payload[offset]);
    if (!status) {
        return Status{ErrorCode::protocol_error,
                      "self profile presence status is invalid"};
    }
    SelfProfile profile;
    profile.name = std::move(name).value();
    profile.status_message = std::move(status_message).value();
    profile.status = *status;
    return profile;
}

Result<std::vector<std::uint8_t>> encode_peer_list(
    std::span<const TransportPeer> peers) {
    if (peers.size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::invalid_argument,
                      "peer count cannot be represented by local protocol"};
    }
    std::vector<std::uint8_t> output;
    append_u32(output, static_cast<std::uint32_t>(peers.size()));
    for (const TransportPeer &peer : peers) {
        if (peer.name.size() > toxcore::abi::kMaxNameLength ||
            peer.status_message.size() > toxcore::abi::kMaxStatusMessageLength ||
            peer.connection_status < 0 || peer.connection_status > 255) {
            return Status{ErrorCode::invalid_argument,
                          "peer record exceeds local protocol bounds"};
        }
        append_u32(output, peer.friend_number);
        output.push_back(static_cast<std::uint8_t>(peer.connection_status));
        output.push_back(encode_presence(peer.status));
        output.push_back(peer.typing ? 1U : 0U);
        output.push_back(0U);
        output.insert(
            output.end(), peer.public_key.begin(), peer.public_key.end());
        append_u32(output, static_cast<std::uint32_t>(peer.name.size()));
        output.insert(output.end(), peer.name.begin(), peer.name.end());
        append_u32(
            output, static_cast<std::uint32_t>(peer.status_message.size()));
        output.insert(
            output.end(), peer.status_message.begin(), peer.status_message.end());
        if (output.size() > kControlMaxPayloadSize) {
            return Status{ErrorCode::resource_exhausted,
                          "encoded peer list exceeds local control payload limit"};
        }
    }
    return output;
}

Result<std::vector<TransportPeer>> decode_peer_list(
    std::span<const std::uint8_t> payload) {
    if (!can_read(payload, 0U, 4U)) {
        return Status{ErrorCode::protocol_error,
                      "peer list count is truncated"};
    }
    std::size_t offset = 4U;
    const std::uint32_t count = read_u32(payload, 0U);
    constexpr std::size_t kMinimumRecord =
        4U + 4U + toxcore::abi::kPublicKeySize + 4U + 4U;
    if (count != 0U && count > (payload.size() - offset) / kMinimumRecord) {
        return Status{ErrorCode::protocol_error,
                      "peer list count is impossible for payload size"};
    }
    std::vector<TransportPeer> peers;
    peers.reserve(count);
    for (std::uint32_t index = 0U; index < count; ++index) {
        if (!can_read(payload, offset, 4U + 4U + toxcore::abi::kPublicKeySize)) {
            return Status{ErrorCode::protocol_error,
                          "peer record header is truncated"};
        }
        TransportPeer peer;
        peer.friend_number = read_u32(payload, offset);
        offset += 4U;
        peer.connection_status = static_cast<int>(payload[offset++]);
        const auto presence = decode_presence(payload[offset++]);
        if (!presence) {
            return Status{ErrorCode::protocol_error,
                          "peer presence status is invalid"};
        }
        peer.status = *presence;
        const std::uint8_t typing = payload[offset++];
        if (typing > 1U || payload[offset++] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "peer typing or reserved field is invalid"};
        }
        peer.typing = typing != 0U;
        std::copy_n(
            payload.begin() + static_cast<std::ptrdiff_t>(offset),
            peer.public_key.size(), peer.public_key.begin());
        offset += peer.public_key.size();
        auto name = read_bounded_bytes(
            payload, offset, toxcore::abi::kMaxNameLength, "peer name");
        if (!name) {
            return name.status();
        }
        auto status_message = read_bounded_bytes(
            payload, offset, toxcore::abi::kMaxStatusMessageLength,
            "peer status message");
        if (!status_message) {
            return status_message.status();
        }
        peer.name = std::move(name).value();
        peer.status_message = std::move(status_message).value();
        peers.push_back(std::move(peer));
    }
    if (offset != payload.size()) {
        return Status{ErrorCode::protocol_error,
                      "peer list contains trailing bytes"};
    }
    return peers;
}

Result<std::vector<std::uint8_t>> encode_friend_request_list(
    std::span<const FriendRequestRecord> requests) {
    if (requests.size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::invalid_argument,
                      "friend request count cannot be represented by local protocol"};
    }
    std::vector<std::uint8_t> output;
    append_u32(output, static_cast<std::uint32_t>(requests.size()));
    for (const FriendRequestRecord &request : requests) {
        if (request.message.size() > toxcore::abi::kMaxFriendRequestLength) {
            return Status{ErrorCode::invalid_argument,
                          "friend request message exceeds c-toxcore bounds"};
        }
        output.insert(
            output.end(), request.public_key.begin(), request.public_key.end());
        append_u64(output, request.received_unix_ms);
        append_u32(output, static_cast<std::uint32_t>(request.message.size()));
        output.insert(output.end(), request.message.begin(), request.message.end());
        if (output.size() > kControlMaxPayloadSize) {
            return Status{ErrorCode::resource_exhausted,
                          "encoded friend request list exceeds local control payload limit"};
        }
    }
    return output;
}

Result<std::vector<FriendRequestRecord>> decode_friend_request_list(
    std::span<const std::uint8_t> payload) {
    if (!can_read(payload, 0U, 4U)) {
        return Status{ErrorCode::protocol_error,
                      "friend request list count is truncated"};
    }
    const std::uint32_t count = read_u32(payload, 0U);
    std::size_t offset = 4U;
    constexpr std::size_t kMinimumRecord =
        toxcore::abi::kPublicKeySize + 8U + 4U;
    if (count != 0U && count > (payload.size() - offset) / kMinimumRecord) {
        return Status{ErrorCode::protocol_error,
                      "friend request list count is impossible for payload size"};
    }

    std::vector<FriendRequestRecord> requests;
    requests.reserve(count);
    for (std::uint32_t index = 0U; index < count; ++index) {
        if (!can_read(payload, offset, kMinimumRecord)) {
            return Status{ErrorCode::protocol_error,
                          "friend request record is truncated"};
        }
        FriendRequestRecord request;
        std::copy_n(
            payload.begin() + static_cast<std::ptrdiff_t>(offset),
            request.public_key.size(), request.public_key.begin());
        offset += request.public_key.size();
        request.received_unix_ms = read_u64(payload, offset);
        offset += 8U;
        auto message = read_bounded_bytes(
            payload, offset, toxcore::abi::kMaxFriendRequestLength,
            "friend request message");
        if (!message) {
            return message.status();
        }
        request.message = std::move(message).value();
        requests.push_back(std::move(request));
    }
    if (offset != payload.size()) {
        return Status{ErrorCode::protocol_error,
                      "friend request list contains trailing bytes"};
    }
    return requests;
}

std::string to_string(ErrorCode code) {
    switch (code) {
        case ErrorCode::ok:
            return "ok";
        case ErrorCode::invalid_argument:
            return "invalid-argument";
        case ErrorCode::not_found:
            return "not-found";
        case ErrorCode::unsupported:
            return "unsupported";
        case ErrorCode::unavailable:
            return "unavailable";
        case ErrorCode::io_error:
            return "io-error";
        case ErrorCode::library_error:
            return "library-error";
        case ErrorCode::protocol_error:
            return "protocol-error";
        case ErrorCode::timeout:
            return "timeout";
        case ErrorCode::internal_error:
            return "internal-error";
        case ErrorCode::resource_exhausted:
            return "resource-exhausted";
    }
    return "unknown";
}

std::vector<std::uint8_t> text_payload(std::string text) {
    return {text.begin(), text.end()};
}

std::string payload_text(std::span<const std::uint8_t> payload) {
    return {payload.begin(), payload.end()};
}

}  // namespace iotox::local
