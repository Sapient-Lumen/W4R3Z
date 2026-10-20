#pragma once

#include "iotox/status.hpp"
#include "iotox/transport.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <vector>

namespace iotox::local {

inline constexpr std::uint8_t kControlProtocolMajor = 1U;
inline constexpr std::uint8_t kControlProtocolMinor = 56U;
inline constexpr std::size_t kControlHeaderSize = 24U;
inline constexpr std::size_t kControlMaxPayloadSize = 60U * 1024U;
inline constexpr std::size_t kControlMaxPacketSize =
    kControlHeaderSize + kControlMaxPayloadSize;

enum class ControlKind : std::uint8_t {
    request = 1U,
    response = 2U,
};

enum class ControlOperation : std::uint8_t {
    ping = 1U,
    inspect = 2U,
    address = 3U,
    shutdown = 4U,
    self_profile = 5U,
    self_set_name = 6U,
    self_set_status_message = 7U,
    self_set_status = 8U,

    // These operations modify only the Tox transport relationship. They do not
    // create IoTox ownership, roles, capabilities, or application authority.
    transport_peer_add = 16U,
    transport_send_lossless = 17U,
    transport_peer_request = 18U,
    transport_peer_remove = 19U,
    transport_peer_list = 20U,
    transport_send_message = 21U,
    transport_set_typing = 22U,
    transport_friend_request_list = 23U,
    transport_friend_request_reject = 24U,
    protocol_send_hello = 25U,
    protocol_session_list = 26U,
    protocol_session_show = 27U,
    transport_friend_request_accept = 28U,
    protocol_send_confirmation = 29U,
    // Public-key-bound deletion. The legacy numeric operation remains decoded
    // for compatibility, but current clients use this operation so a reused
    // friend number cannot redirect a delayed removal request.
    transport_peer_remove_key = 30U,
    // Research/qualification seam for the ordinary Ratox text lane. The
    // daemon sends one normal message and measures monotonic time until its
    // c-toxcore read receipt. This is not a terminal wire protocol.
    transport_message_probe = 31U,

    // Finite regular-file operations. Paths are absolute paths interpreted by
    // the running iotox process. Incoming data stays paused until a private
    // temporary file has been acquired successfully.
    transport_file_send_path = 32U,
    transport_file_receive_path = 33U,
    transport_file_cancel = 34U,
    transport_file_list = 35U,
    // Generic two-sided c-toxcore file control. Payload: friend u32,
    // file u32, action byte (0=resume, 1=pause, 2=cancel). The older
    // cancel-only operation remains accepted as a local compatibility alias.
    transport_file_control = 36U,
    // Unadvertised research echo over c-toxcore custom packet carriers.
    // Payload: friend u32, timeout-ms u32, carrier byte (1=lossless, 2=lossy).
    transport_packet_probe = 37U,
    // Bounded research burst used to observe loss, duplication, and reorder.
    // Payload: friend u32, deadline-ms u32, carrier byte, count u16,
    // spacing-ms u16, packet-bytes u16 (10..1200; omitted by minor <=20
    // clients and interpreted as 10). Response: count u16, then count records
    // of ordinal u16, nonce u64, RTT-us u64 (UINT64_MAX=miss), arrival-rank u16
    // (zero=miss), copies u16, and local send ErrorCode u16. This is local
    // evidence, not a negotiated wire feature.
    transport_packet_probe_burst = 38U,
    // Content-free auxiliary route observation. Empty payload samples carrier
    // truth and the configured local route boundary. An 8-byte payload adds a
    // transcript-gated lossless application echo: friend u32, timeout-ms u32.
    // This operation cannot mutate carrier truth or a protocol session epoch.
    transport_route_health = 39U,

    // Stable IoTox application identity and the independent signed authority
    // ledger. These remain distinct from Tox friendship and session state.
    identity_show = 40U,
    authority_show = 41U,
    authority_principal_list = 42U,
    authority_prepare = 43U,
    authority_append = 44U,
    authority_session_list = 45U,
    authority_session_show = 46U,
    authority_challenge_send = 47U,
    authority_proof_prepare = 48U,
    authority_proof_send = 49U,
    authority_device_proof_send = 50U,

    // First bounded IoTox machine operation. The request is sent only after
    // the canonical session and local stable-principal proof are established.
    protocol_device_describe = 51U,
    protocol_peer_description_show = 52U,

    // Signed durable application-command journal. These operations are read
    // surfaces only; command creation still flows through a typed operation.
    command_store_show = 53U,
    command_record_show = 54U,

    // Generic durable operation entrance. The payload identifies a friend,
    // one registered CommandOperation, scheduling policy, and (when required)
    // one registry-defined bounded argument byte.
    command_issue = 55U,
    authority_remote_delegation_send = 56U,
    authority_remote_delegation_prepare = 57U,
    authority_remote_delegation_retry = 58U,
    authority_remote_delegation_show = 59U,
    authority_remote_revocation_prepare = 60U,
    authority_remote_successor_prepare = 61U,
    authority_remote_epoch_transition_prepare = 62U,
    command_cancel = 63U,
    authority_remote_migration_prepare = 64U,
    authority_remote_v3_migration_prepare = 65U,
    route_inventory_show = 66U,
    sync_namespace_list = 67U,
    sync_pull = 68U,
    sync_status = 69U,
    sync_publish = 70U,
    sync_activate = 71U,
    sync_namespace_install = 72U,
    sync_cancel = 73U,
    sync_namespace_update = 74U,
    sync_namespace_remove = 75U,
    sync_repair = 76U,
    // Payload: mode byte (0=dry-run, 1=quarantine), then one namespace id.
    // Quarantine is descriptor-pinned and never unlinks; no purge operation is
    // present in this protocol generation.
    sync_gc = 77U,
    // Qualification seam: a fixed 16-byte response containing the live
    // interactive owner-command execution count and cumulative queue wait.
    // Unlike inspect/status, this does not render the complete Agent snapshot.
    transport_interactive_evidence = 78U,
    // Owner-local M7 construction controls. Staging binds one exact accepted
    // sync HEAD; apply returns a one-use health token for a later incarnation.
    update_status = 79U,
    update_stage = 80U,
    update_apply = 81U,
    update_confirm = 82U,
    // Payload byte: 0=dry-run, 1=recoverable quarantine. No purge operation
    // exists in this protocol generation.
    update_gc = 83U,
    // One-shot SOCKS5 CONNECT to the first explicit numeric TCP relay in the
    // frozen Tox/Tor route. Payload: timeout-ms u32. The response is
    // content-free and cannot change provider or session truth.
    transport_route_target_health = 84U,
    // Versioned sync-pull entrance. Payload: failover byte
    // (1=available, 2=fail-closed), friend u32, namespace bytes 1..64.
    // Operation 68 remains the compatibility entrance and captures the
    // running Agent's configured default at job creation.
    sync_pull_policy = 85U,
    // Route-constrained sync pull. Payload: route-class byte, failover byte,
    // friend u32, namespace bytes 1..64. Named route classes require an
    // exact authenticated auxiliary worker; they never fall back to primary.
    sync_pull_route_policy = 86U,
    // Add one currently authenticated primary peer as an immutable-object
    // source for an existing content-v2 or tree-v2 job. Payload: job id u64,
    // friend u32. The primary signed HEAD/frontier remains authoritative and
    // cannot be replaced. The historical operation name/value stay frozen.
    sync_content_source_add = 87U,
    // Atomically create one content-v2 or tree-v2 pull with every
    // authenticated source registered before the primary HEAD/frontier
    // request can leave the daemon. Tree-v2 uses primary carriers only.
    // Payload: auxiliary-count u8 (1..15), primary friend u32, that many
    // auxiliary friend u32 values, then namespace bytes 1..64.
    sync_content_pull_multi = 88U,
    // Admit one exact foreign-writer content-v2 HEAD as an owner-local,
    // device-authenticated availability replica. Payload: namespace-length
    // u8, namespace bytes 1..64, then one canonical SignedHead record.
    sync_content_replica_import = 89U,
    // Atomically create a content-v2 pull whose source-path records each bind
    // to one distinct ready auxiliary carrier in the same named owner-local
    // route class before the primary HEAD request is released. A primary
    // friend may repeat: every occurrence retains the same independently
    // proven principal/authority session but requires another exact carrier.
    // Payload: route-class u8, auxiliary-count u8, primary friend u32,
    // auxiliary friend u32 values, then namespace bytes 1..64. Carrier loss
    // is fail-closed; authority and HEAD remain on the primary sessions.
    sync_content_pull_multi_route = 90U,
    // Durable, stable-device-signed one-writer synchronization automation.
    // These are owner-local controls; they do not extend the peer wire.
    sync_automation_list = 91U,
    // Payload: interval-ms u32, namespace-length u8, namespace, absolute path.
    sync_automation_publish = 92U,
    // Payload: interval-ms u32, activation byte (1=pull, 2=verified),
    // friend u32, then namespace bytes 1..64. The friend is resolved to its
    // authenticated stable principal before anything is persisted.
    sync_automation_follow = 93U,
    // Payload: namespace bytes 1..64. Removal commits a signed tombstone.
    sync_automation_remove = 94U,
    // Owner-local everyday-sync convenience entrance. Payload: interval-ms
    // u32, namespace-length u8, namespace, absolute source path. The Agent
    // infers regular-file content-v2 or directory treepack-v1, installs a
    // private managed namespace, and enables automatic publication.
    sync_create = 95U,
    // Read-only share preparation. Payload: friend u32, owner signing key,
    // namespace bytes 1..64. Response: grant-required u8, exact stable peer
    // principal, and an optional authority record body for RecallRoot signing.
    sync_share_prepare = 96U,
    // Read-only share commit. Payload: friend u32, namespace-length u8,
    // namespace, exact prepared peer principal, then zero or one complete
    // signed authority record. Commit preserves every existing writer and
    // adds only subscriber membership after any required grant is durable.
    sync_share_commit = 97U,
    // Read-write counterparts preserve the frozen read-only payloads while
    // granting both sync capabilities and both namespace memberships.
    sync_share_read_write_prepare = 98U,
    sync_share_read_write_commit = 99U,
    // Owner-local tree-v2 maintenance. These do not extend the peer frame.
    sync_tree_checkpoint = 100U,
    sync_tree_pin = 101U,
    sync_tree_unpin = 102U,
    sync_tree_maintenance_show = 103U,
    sync_tree_restore = 104U,
    sync_tree_writer_cutoff = 105U,
    // Owner-local Ratox controller lifecycle. LIST accepts zero or one
    // 32-byte peer key and returns content-free text. CLOSE accepts one
    // 16-byte session ID and an optional 32-byte peer key; a detached session
    // first traverses the existing authenticated RESUME path.
    ratox_client_session_list = 106U,
    ratox_client_session_close = 107U,
    // Returns only the locally signature-verified, closed-field diagnostic
    // recorder tail plus a current redacted observation. The device public
    // key, signature, paths, content, and raw configuration never cross this
    // response. Empty request payload.
    diagnostics_export = 108U,
    // Stable-device-signed owner-local alias registry. List has an empty
    // payload; set/rename/remove/resolve use peer_alias canonical codecs.
    peer_alias_list = 109U,
    peer_alias_set = 110U,
    peer_alias_rename = 111U,
    peer_alias_remove = 112U,
    peer_alias_resolve = 113U,
    // Creates one stable-device-signed invitation for this Agent's exact
    // current Tox address. Payload and response use peer_invitation codecs;
    // this operation creates neither friendship nor authority.
    peer_invitation_create = 114U,
    // Owner-local tree-v2 time machine. History, diff, conflicts, and plan are
    // read-only. Forward restore requires the exact plan ID and creates one
    // higher local writer generation; operation 104 remains quarantine repair.
    sync_tree_history = 115U,
    sync_tree_diff = 116U,
    sync_tree_conflicts = 117U,
    sync_tree_restore_plan = 118U,
    sync_tree_restore_forward = 119U,
    // Recipient-local tree-v2 selection and content-custody policy. INTEREST
    // uses namespace/count/rule framing; zero rules is read-only inspection.
    // CLEAR restores complete projection/custody intent. Neither extends the
    // peer wire or lets a remote peer choose paths.
    sync_tree_interest = 120U,
    sync_tree_interest_clear = 121U,
    // Signed, content-free tree-v2 namespace health. Payload: mode byte
    // (0=load cached, 1=refresh), then namespace bytes 1..64. Refresh verifies
    // current selected custody and stores one local-device-signed observation.
    sync_namespace_health = 122U,
};

struct ControlPacket {
    ControlKind kind{ControlKind::request};
    ControlOperation operation{ControlOperation::ping};
    std::uint64_t request_id{0U};
    ErrorCode status{ErrorCode::ok};
    std::vector<std::uint8_t> payload;

    [[nodiscard]] bool operator==(const ControlPacket &) const = default;
};

struct InteractiveTransportEvidence {
    std::uint64_t executed_commands{0U};
    std::uint64_t total_queue_wait_us{0U};

    [[nodiscard]] bool operator==(
        const InteractiveTransportEvidence &) const = default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_control_packet(
    const ControlPacket &packet);
[[nodiscard]] Result<ControlPacket> decode_control_packet(std::span<const std::uint8_t> bytes);
[[nodiscard]] std::vector<std::uint8_t> encode_interactive_transport_evidence(
    const InteractiveTransportEvidence &evidence);
[[nodiscard]] Result<InteractiveTransportEvidence>
decode_interactive_transport_evidence(std::span<const std::uint8_t> payload);

[[nodiscard]] std::string to_string(ControlKind kind);
[[nodiscard]] std::string to_string(ControlOperation operation);
[[nodiscard]] std::string to_string(ErrorCode code);


struct FriendRequestRecord {
    std::array<std::uint8_t, toxcore::abi::kPublicKeySize> public_key{};
    std::uint64_t received_unix_ms{0U};
    std::vector<std::uint8_t> message;

    [[nodiscard]] bool operator==(const FriendRequestRecord &) const = default;
};

// Binary response records used by the single iotox executable. These helpers
// keep the daemon and client sides on one bounded, byte-preserving contract.
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_self_profile(
    const SelfProfile &profile);
[[nodiscard]] Result<SelfProfile> decode_self_profile(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_peer_list(
    std::span<const TransportPeer> peers);
[[nodiscard]] Result<std::vector<TransportPeer>> decode_peer_list(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_friend_request_list(
    std::span<const FriendRequestRecord> requests);
[[nodiscard]] Result<std::vector<FriendRequestRecord>> decode_friend_request_list(
    std::span<const std::uint8_t> payload);

[[nodiscard]] std::vector<std::uint8_t> text_payload(std::string text);
[[nodiscard]] std::string payload_text(std::span<const std::uint8_t> payload);

}  // namespace iotox::local
