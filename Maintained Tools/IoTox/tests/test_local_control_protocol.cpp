#include "iotox/local/control_protocol.hpp"
#include "test_harness.hpp"

#include <array>
#include <cstdint>
#include <vector>

IOTOX_TEST("local control protocol round-trips bounded correlated packets") {
    iotox::local::ControlPacket request;
    request.kind = iotox::local::ControlKind::request;
    request.operation = iotox::local::ControlOperation::transport_send_lossless;
    request.request_id = 0x0102030405060708ULL;
    request.payload = {0U, 0U, 0U, 7U, 69U, 'I', 'o', 'T', 'o', 'x'};

    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() ==
                iotox::local::kControlHeaderSize + request.payload.size());

    auto decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == request);

    iotox::local::ControlPacket response = request;
    response.kind = iotox::local::ControlKind::response;
    response.status = iotox::ErrorCode::unavailable;
    response.payload = iotox::local::text_payload("peer offline");
    auto response_encoded = iotox::local::encode_control_packet(response);
    IOTOX_CHECK(response_encoded.ok());
    auto response_decoded = iotox::local::decode_control_packet(response_encoded.value());
    IOTOX_CHECK(response_decoded.ok());
    IOTOX_CHECK(response_decoded.value() == response);
}

IOTOX_TEST("local control protocol rejects ambiguity and unsupported versions") {
    iotox::local::ControlPacket request;
    request.request_id = 44U;
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK(encoded.ok());

    std::vector<std::uint8_t> truncated(encoded.value().begin(), encoded.value().begin() + 7);
    IOTOX_CHECK(!iotox::local::decode_control_packet(truncated).ok());

    auto bad_magic = encoded.value();
    bad_magic[0U] = 'X';
    IOTOX_CHECK(!iotox::local::decode_control_packet(bad_magic).ok());

    auto future_major = encoded.value();
    future_major[4U] = static_cast<std::uint8_t>(iotox::local::kControlProtocolMajor + 1U);
    auto future_result = iotox::local::decode_control_packet(future_major);
    IOTOX_CHECK(!future_result.ok());
    IOTOX_CHECK(future_result.status().code() == iotox::ErrorCode::unsupported);

    auto unknown_operation = encoded.value();
    unknown_operation[7U] = 255U;
    IOTOX_CHECK(!iotox::local::decode_control_packet(unknown_operation).ok());

    auto reserved = encoded.value();
    reserved[19U] = 1U;
    IOTOX_CHECK(!iotox::local::decode_control_packet(reserved).ok());

    auto wrong_length = encoded.value();
    wrong_length[23U] = 1U;
    IOTOX_CHECK(!iotox::local::decode_control_packet(wrong_length).ok());

    request.request_id = 0U;
    IOTOX_CHECK(!iotox::local::encode_control_packet(request).ok());

    request.request_id = 7U;
    request.status = iotox::ErrorCode::timeout;
    IOTOX_CHECK(!iotox::local::encode_control_packet(request).ok());
}

IOTOX_TEST("local control protocol enforces its payload ceiling") {
    iotox::local::ControlPacket packet;
    packet.request_id = 99U;
    packet.payload.resize(iotox::local::kControlMaxPayloadSize + 1U, 0xA5U);
    auto encoded = iotox::local::encode_control_packet(packet);
    IOTOX_CHECK(!encoded.ok());
    IOTOX_CHECK(encoded.status().code() == iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST("local control profile and peer records preserve bounded transport bytes") {
    iotox::SelfProfile profile;
    profile.name = {'I', 'o', 0U, 'T', 'o', 'x'};
    profile.status_message = {'j', 'u', 's', 't', '\n', 'w', 'e', 'r', 'x'};
    profile.status = iotox::PresenceStatus::busy;

    auto encoded_profile = iotox::local::encode_self_profile(profile);
    IOTOX_CHECK_MSG(encoded_profile.ok(), encoded_profile.status().message());
    auto decoded_profile = iotox::local::decode_self_profile(encoded_profile.value());
    IOTOX_CHECK_MSG(decoded_profile.ok(), decoded_profile.status().message());
    IOTOX_CHECK(decoded_profile.value() == profile);

    iotox::TransportPeer first;
    first.friend_number = 7U;
    first.public_key.fill(0xA5U);
    first.connection_status = 2;
    first.name = {'p', 'e', 'e', 'r', 0U, '7'};
    first.status_message = {'w', 'o', 'r', 'k', 's'};
    first.status = iotox::PresenceStatus::away;
    first.typing = true;

    iotox::TransportPeer second;
    second.friend_number = 9U;
    second.public_key.fill(0x5AU);
    second.connection_status = 0;
    second.status = iotox::PresenceStatus::available;

    const std::array peers{first, second};
    auto encoded_peers = iotox::local::encode_peer_list(peers);
    IOTOX_CHECK_MSG(encoded_peers.ok(), encoded_peers.status().message());
    auto decoded_peers = iotox::local::decode_peer_list(encoded_peers.value());
    IOTOX_CHECK_MSG(decoded_peers.ok(), decoded_peers.status().message());
    IOTOX_CHECK(decoded_peers.value().size() == peers.size());
    IOTOX_CHECK(decoded_peers.value()[0] == first);
    IOTOX_CHECK(decoded_peers.value()[1] == second);
}

IOTOX_TEST("local control profile and peer decoders reject malformed variable "
           "records") {
    iotox::SelfProfile profile;
    auto encoded_profile = iotox::local::encode_self_profile(profile);
    IOTOX_CHECK(encoded_profile.ok());

    auto invalid_presence = encoded_profile.value();
    invalid_presence.back() = 0xFFU;
    IOTOX_CHECK(!iotox::local::decode_self_profile(invalid_presence).ok());

    auto trailing_profile = encoded_profile.value();
    trailing_profile.push_back(0U);
    IOTOX_CHECK(!iotox::local::decode_self_profile(trailing_profile).ok());

    const std::vector<std::uint8_t> impossible_count{0U, 0U, 0U, 1U};
    auto impossible = iotox::local::decode_peer_list(impossible_count);
    IOTOX_CHECK(!impossible.ok());
    IOTOX_CHECK(impossible.status().code() == iotox::ErrorCode::protocol_error);

    iotox::TransportPeer peer;
    peer.public_key.fill(0x11U);
    const std::array peers{peer};
    auto encoded_peer = iotox::local::encode_peer_list(peers);
    IOTOX_CHECK(encoded_peer.ok());

    auto bad_reserved = encoded_peer.value();
    bad_reserved[11U] = 1U;
    IOTOX_CHECK(!iotox::local::decode_peer_list(bad_reserved).ok());

    auto truncated = encoded_peer.value();
    truncated.pop_back();
    IOTOX_CHECK(!iotox::local::decode_peer_list(truncated).ok());
}

IOTOX_TEST("local control friend request records preserve keys timestamps and "
           "arbitrary bytes") {
    iotox::local::FriendRequestRecord first;
    first.public_key.fill(0xA7U);
    first.received_unix_ms = 0x0102030405060708ULL;
    first.message = {'h', 'i', 0U, '\n', 0xFFU};

    iotox::local::FriendRequestRecord second;
    second.public_key.fill(0x42U);
    second.received_unix_ms = 99U;

    const std::array requests{first, second};
    auto encoded = iotox::local::encode_friend_request_list(requests);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto decoded = iotox::local::decode_friend_request_list(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value().size() == requests.size());
    IOTOX_CHECK(decoded.value()[0] == first);
    IOTOX_CHECK(decoded.value()[1] == second);

    auto trailing = encoded.value();
    trailing.push_back(0U);
    IOTOX_CHECK(!iotox::local::decode_friend_request_list(trailing).ok());

    auto truncated = encoded.value();
    truncated.pop_back();
    IOTOX_CHECK(!iotox::local::decode_friend_request_list(truncated).ok());

    const std::vector<std::uint8_t> impossible_count{0U, 0U, 0U, 1U};
    auto impossible =
        iotox::local::decode_friend_request_list(impossible_count);
    IOTOX_CHECK(!impossible.ok());
    IOTOX_CHECK(impossible.status().code() == iotox::ErrorCode::protocol_error);

    first.message.resize(iotox::toxcore::abi::kMaxFriendRequestLength + 1U, 0U);
    const std::array oversized{first};
    IOTOX_CHECK(!iotox::local::encode_friend_request_list(oversized).ok());
}

IOTOX_TEST("local control protocol freezes the public capability-session operations") {
    using iotox::local::ControlOperation;
    const std::array operations{
        ControlOperation::protocol_send_hello,
        ControlOperation::protocol_session_list,
        ControlOperation::protocol_session_show,
        ControlOperation::protocol_send_confirmation,
    };
    const std::array<const char *, 4U> names{
        "protocol-send-hello",
        "protocol-session-list",
        "protocol-session-show",
        "protocol-send-confirmation",
    };
    const std::array<std::uint8_t, 4U> wire_values{25U, 26U, 27U, 29U};

    for (std::size_t index = 0U; index < operations.size(); ++index) {
        IOTOX_CHECK(static_cast<std::uint8_t>(operations[index]) == wire_values[index]);
        IOTOX_CHECK(iotox::local::to_string(operations[index]) == names[index]);

        iotox::local::ControlPacket request;
        request.operation = operations[index];
        request.request_id = 700U + index;
        auto encoded = iotox::local::encode_control_packet(request);
        IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
        auto decoded = iotox::local::decode_control_packet(encoded.value());
        IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
        IOTOX_CHECK(decoded.value().operation == operations[index]);
    }
}

IOTOX_TEST("local control protocol freezes public-key-bound friend removal") {
    using iotox::local::ControlOperation;
    IOTOX_CHECK(
        static_cast<std::uint8_t>(
            ControlOperation::transport_peer_remove_key) == 30U);
    IOTOX_CHECK(
        iotox::local::to_string(
            ControlOperation::transport_peer_remove_key) ==
        "transport-peer-remove-key");

    iotox::local::ControlPacket request;
    request.operation = ControlOperation::transport_peer_remove_key;
    request.request_id = 730U;
    request.payload.resize(iotox::toxcore::abi::kPublicKeySize, 0x42U);
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == request);
}

IOTOX_TEST("local control protocol freezes explicit friend request acceptance") {
    using iotox::local::ControlOperation;
    IOTOX_CHECK(
        static_cast<std::uint8_t>(
            ControlOperation::transport_friend_request_accept) == 28U);
    IOTOX_CHECK(
        iotox::local::to_string(
            ControlOperation::transport_friend_request_accept) ==
        "transport-friend-request-accept");

    iotox::local::ControlPacket request;
    request.operation =
        ControlOperation::transport_friend_request_accept;
    request.request_id = 728U;
    request.payload.resize(iotox::toxcore::abi::kPublicKeySize, 0xA7U);
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == request);
}

IOTOX_TEST("local control protocol freezes finite file operations including "
           "two-sided control") {
    using iotox::local::ControlOperation;
    const std::array operations{
        ControlOperation::transport_file_send_path,
        ControlOperation::transport_file_receive_path,
        ControlOperation::transport_file_cancel,
        ControlOperation::transport_file_list,
        ControlOperation::transport_file_control,
    };
    const std::array<const char *, 5U> names{
        "transport-file-send-path",
        "transport-file-receive-path",
        "transport-file-cancel",
        "transport-file-list",
        "transport-file-control",
    };
    const std::array<std::uint8_t, 5U> wire_values{32U, 33U, 34U, 35U, 36U};

    for (std::size_t index = 0U; index < operations.size(); ++index) {
        IOTOX_CHECK(static_cast<std::uint8_t>(operations[index]) == wire_values[index]);
        IOTOX_CHECK(iotox::local::to_string(operations[index]) == names[index]);
        iotox::local::ControlPacket request;
        request.operation = operations[index];
        request.request_id = 700U + index;
        auto encoded = iotox::local::encode_control_packet(request);
        IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
        auto decoded = iotox::local::decode_control_packet(encoded.value());
        IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
        IOTOX_CHECK(decoded.value().operation == operations[index]);
    }
}

IOTOX_TEST("local control protocol freezes stable identity and authority operations") {
    using iotox::local::ControlOperation;
    const std::array operations{
        ControlOperation::identity_show,
        ControlOperation::authority_show,
        ControlOperation::authority_principal_list,
        ControlOperation::authority_prepare,
        ControlOperation::authority_append,
        ControlOperation::authority_session_list,
        ControlOperation::authority_session_show,
        ControlOperation::authority_challenge_send,
        ControlOperation::authority_proof_prepare,
        ControlOperation::authority_proof_send,
        ControlOperation::authority_device_proof_send,
        ControlOperation::protocol_device_describe,
        ControlOperation::protocol_peer_description_show,
        ControlOperation::command_store_show,
        ControlOperation::command_record_show,
        ControlOperation::command_issue,
        ControlOperation::authority_remote_delegation_send,
        ControlOperation::authority_remote_delegation_prepare,
        ControlOperation::authority_remote_delegation_retry,
        ControlOperation::authority_remote_delegation_show,
        ControlOperation::authority_remote_revocation_prepare,
        ControlOperation::authority_remote_successor_prepare,
        ControlOperation::authority_remote_epoch_transition_prepare,
        ControlOperation::command_cancel,
        ControlOperation::authority_remote_migration_prepare,
        ControlOperation::authority_remote_v3_migration_prepare,
        ControlOperation::route_inventory_show,
        ControlOperation::sync_namespace_list,
        ControlOperation::sync_pull,
        ControlOperation::sync_status,
        ControlOperation::sync_publish,
        ControlOperation::sync_activate,
        ControlOperation::sync_namespace_install,
        ControlOperation::sync_cancel,
        ControlOperation::sync_namespace_update,
        ControlOperation::sync_namespace_remove,
        ControlOperation::sync_repair,
        ControlOperation::sync_gc,
        ControlOperation::transport_interactive_evidence,
        ControlOperation::update_status,
        ControlOperation::update_stage,
        ControlOperation::update_apply,
        ControlOperation::update_confirm,
        ControlOperation::update_gc,
        ControlOperation::transport_route_target_health,
        ControlOperation::sync_pull_policy,
        ControlOperation::sync_pull_route_policy,
        ControlOperation::sync_content_source_add,
        ControlOperation::sync_content_pull_multi,
        ControlOperation::sync_content_replica_import,
        ControlOperation::sync_content_pull_multi_route,
        ControlOperation::sync_automation_list,
        ControlOperation::sync_automation_publish,
        ControlOperation::sync_automation_follow,
        ControlOperation::sync_automation_remove,
        ControlOperation::sync_create,
        ControlOperation::sync_share_prepare,
        ControlOperation::sync_share_commit,
        ControlOperation::sync_share_read_write_prepare,
        ControlOperation::sync_share_read_write_commit,
        ControlOperation::sync_tree_checkpoint,
        ControlOperation::sync_tree_pin,
        ControlOperation::sync_tree_unpin,
        ControlOperation::sync_tree_maintenance_show,
        ControlOperation::sync_tree_restore,
        ControlOperation::sync_tree_writer_cutoff,
        ControlOperation::ratox_client_session_list,
        ControlOperation::ratox_client_session_close,
        ControlOperation::diagnostics_export,
        ControlOperation::peer_alias_list,
        ControlOperation::peer_alias_set,
        ControlOperation::peer_alias_rename,
        ControlOperation::peer_alias_remove,
        ControlOperation::peer_alias_resolve,
        ControlOperation::peer_invitation_create,
        ControlOperation::sync_tree_history,
        ControlOperation::sync_tree_diff,
        ControlOperation::sync_tree_conflicts,
        ControlOperation::sync_tree_restore_plan,
        ControlOperation::sync_tree_restore_forward,
        ControlOperation::sync_tree_interest,
        ControlOperation::sync_tree_interest_clear,
        ControlOperation::sync_namespace_health,
    };
    const std::array<const char *, 83U> names{
        "identity-show",
        "authority-show",
        "authority-principal-list",
        "authority-prepare",
        "authority-append",
        "authority-session-list",
        "authority-session-show",
        "authority-challenge-send",
        "authority-proof-prepare",
        "authority-proof-send",
        "authority-device-proof-send",
        "protocol-device-describe",
        "protocol-peer-description-show",
        "command-store-show",
        "command-record-show",
        "command-issue",
        "authority-remote-delegation-send",
        "authority-remote-delegation-prepare",
        "authority-remote-delegation-retry",
        "authority-remote-delegation-show",
        "authority-remote-revocation-prepare",
        "authority-remote-successor-prepare",
        "authority-remote-epoch-transition-prepare",
        "command-cancel",
        "authority-remote-migration-prepare",
        "authority-remote-v3-migration-prepare",
        "route-inventory-show",
        "sync-namespace-list",
        "sync-pull",
        "sync-status",
        "sync-publish",
        "sync-activate",
        "sync-namespace-install",
        "sync-cancel",
        "sync-namespace-update",
        "sync-namespace-remove",
        "sync-repair",
        "sync-gc",
        "transport-interactive-evidence",
        "update-status",
        "update-stage",
        "update-apply",
        "update-confirm",
        "update-gc",
        "transport-route-target-health",
        "sync-pull-policy",
        "sync-pull-route-policy",
        "sync-content-source-add",
        "sync-content-pull-multi",
        "sync-content-replica-import",
        "sync-content-pull-multi-route",
        "sync-automation-list",
        "sync-automation-publish",
        "sync-automation-follow",
        "sync-automation-remove",
        "sync-create",
        "sync-share-prepare",
        "sync-share-commit",
        "sync-share-read-write-prepare",
        "sync-share-read-write-commit",
        "sync-tree-checkpoint",
        "sync-tree-pin",
        "sync-tree-unpin",
        "sync-tree-maintenance-show",
        "sync-tree-restore",
        "sync-tree-writer-cutoff",
        "ratox-client-session-list",
        "ratox-client-session-close",
        "diagnostics-export",
        "peer-alias-list",
        "peer-alias-set",
        "peer-alias-rename",
        "peer-alias-remove",
        "peer-alias-resolve",
        "peer-invitation-create",
        "sync-tree-history",
        "sync-tree-diff",
        "sync-tree-conflicts",
        "sync-tree-restore-plan",
        "sync-tree-restore-forward",
        "sync-tree-interest",
        "sync-tree-interest-clear",
        "sync-namespace-health",
    };
    const std::array<std::uint8_t, 83U> wire_values{
        40U, 41U, 42U, 43U, 44U, 45U, 46U, 47U, 48U, 49U, 50U, 51U,
        52U, 53U, 54U, 55U, 56U, 57U, 58U, 59U, 60U, 61U, 62U, 63U,
        64U, 65U, 66U, 67U, 68U, 69U, 70U, 71U, 72U, 73U, 74U, 75U,
        76U, 77U, 78U, 79U, 80U, 81U, 82U, 83U, 84U, 85U, 86U, 87U,
        88U, 89U, 90U, 91U, 92U, 93U, 94U, 95U, 96U, 97U, 98U, 99U,
        100U, 101U, 102U, 103U, 104U, 105U, 106U, 107U, 108U, 109U,
        110U, 111U, 112U, 113U, 114U, 115U, 116U, 117U, 118U, 119U,
        120U, 121U, 122U};

    IOTOX_CHECK(iotox::local::kControlProtocolMajor == 1U);
    IOTOX_CHECK(iotox::local::kControlProtocolMinor == 56U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_pull_policy) == 85U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_pull_route_policy) == 86U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_content_source_add) == 87U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_content_pull_multi) == 88U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_content_replica_import) == 89U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_content_pull_multi_route) == 90U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_automation_remove) == 94U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_share_commit) == 97U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_share_read_write_prepare) == 98U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_share_read_write_commit) == 99U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_tree_writer_cutoff) == 105U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::ratox_client_session_list) == 106U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::ratox_client_session_close) == 107U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::diagnostics_export) == 108U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::peer_alias_resolve) == 113U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::peer_invitation_create) == 114U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_tree_restore_forward) == 119U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_tree_interest_clear) == 121U);
    IOTOX_CHECK(static_cast<std::uint8_t>(
                    ControlOperation::sync_namespace_health) == 122U);
    for (std::size_t index = 0U; index < operations.size(); ++index) {
        IOTOX_CHECK(static_cast<std::uint8_t>(operations[index]) == wire_values[index]);
        IOTOX_CHECK(iotox::local::to_string(operations[index]) == names[index]);

        iotox::local::ControlPacket request;
        request.operation = operations[index];
        request.request_id = 900U + index;
        auto encoded = iotox::local::encode_control_packet(request);
        IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
        auto decoded = iotox::local::decode_control_packet(encoded.value());
        IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
        IOTOX_CHECK(decoded.value().operation == operations[index]);
    }
}

IOTOX_TEST("local control protocol binds compact interactive transport evidence") {
    const iotox::local::InteractiveTransportEvidence evidence{
        0x0102030405060708ULL, 0x1112131415161718ULL};
    const std::vector<std::uint8_t> encoded =
        iotox::local::encode_interactive_transport_evidence(evidence);
    IOTOX_CHECK(encoded.size() == 16U);
    auto decoded =
        iotox::local::decode_interactive_transport_evidence(encoded);
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == evidence);
    IOTOX_CHECK(!iotox::local::decode_interactive_transport_evidence(
                     std::span<const std::uint8_t>{encoded}.first(15U))
                     .ok());
}

IOTOX_TEST("local control protocol exposes the bounded Ratox message probe seam") {
    using iotox::local::ControlOperation;
    IOTOX_CHECK(
        static_cast<std::uint8_t>(
            ControlOperation::transport_message_probe) == 31U);
    IOTOX_CHECK(
        iotox::local::to_string(
            ControlOperation::transport_message_probe) ==
        "transport-message-probe");
    iotox::local::ControlPacket request;
    request.operation = ControlOperation::transport_message_probe;
    request.request_id = 3100U;
    request.payload = {0U, 0U, 0U, 1U, 0U, 0U, 3U, 0xE8U, 'x'};
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK(encoded.ok());
    auto decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == request);

    IOTOX_CHECK(
        static_cast<std::uint8_t>(
            ControlOperation::transport_route_target_health) == 84U);
    IOTOX_CHECK(
        iotox::local::to_string(
            ControlOperation::transport_route_target_health) ==
        "transport-route-target-health");
    request.operation = ControlOperation::transport_route_target_health;
    request.request_id = 8400U;
    request.payload = {0U, 0U, 3U, 0xE8U};
    encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK(encoded.ok());
    decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == request);
}

IOTOX_TEST("local control protocol exposes separated custom packet probes") {
    using iotox::local::ControlOperation;
    IOTOX_CHECK(
        static_cast<std::uint8_t>(ControlOperation::transport_packet_probe) ==
        37U);
    IOTOX_CHECK(
        iotox::local::to_string(ControlOperation::transport_packet_probe) ==
        "transport-packet-probe");
    iotox::local::ControlPacket request;
    request.operation = ControlOperation::transport_packet_probe;
    request.request_id = 3700U;
    request.payload = {0U, 0U, 0U, 1U, 0U, 0U, 3U, 0xE8U, 2U};
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK(encoded.ok());
    auto decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == request);

    IOTOX_CHECK(
        static_cast<std::uint8_t>(
            ControlOperation::transport_route_health) == 39U);
    IOTOX_CHECK(
        iotox::local::to_string(
            ControlOperation::transport_route_health) ==
        "transport-route-health");
    request.operation = ControlOperation::transport_route_health;
    request.request_id = 3900U;
    request.payload = {0U, 0U, 0U, 1U, 0U, 0U, 3U, 0xE8U};
    encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK(encoded.ok());
    decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == request);
}

IOTOX_TEST("local control protocol exposes bounded impairment burst probes") {
    using iotox::local::ControlOperation;
    IOTOX_CHECK(
        static_cast<std::uint8_t>(
            ControlOperation::transport_packet_probe_burst) == 38U);
    IOTOX_CHECK(
        iotox::local::to_string(
            ControlOperation::transport_packet_probe_burst) ==
        "transport-packet-probe-burst");
    iotox::local::ControlPacket request;
    request.operation = ControlOperation::transport_packet_probe_burst;
    request.request_id = 3800U;
    request.payload = {
        0U, 0U, 0U, 1U, 0U, 0U, 3U, 0xE8U, 2U,
        0U, 32U, 0U, 1U, 4U, 0xB0U};
    auto encoded = iotox::local::encode_control_packet(request);
    IOTOX_CHECK(encoded.ok());
    auto decoded = iotox::local::decode_control_packet(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == request);
}
