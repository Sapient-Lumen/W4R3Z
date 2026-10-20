#pragma once

#include "iotox/protocol/frame.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

namespace iotox::protocol {

// The first application exchange on every online Tox friendship is a compact,
// canonical HELLO. It is deliberately fixed-size: a peer can reject malformed
// capability traffic before allocating a richer application codec.
inline constexpr std::uint8_t kHelloPayloadVersion = 1U;
inline constexpr std::size_t kHelloPayloadSize = 64U;
inline constexpr std::uint8_t kHelloFrameMajor = 1U;
inline constexpr std::uint8_t kHelloFrameMinor = 0U;

// CAPABILITIES confirms the exact two-HELLO transcript and the deterministic
// negotiation result. It is not owner authorization and it is not an
// application signature. It is the fail-closed barrier between an online Tox
// friendship and an IoTox machine session that may carry later application
// traffic.
inline constexpr std::uint8_t kConfirmationPayloadVersion = 1U;
inline constexpr std::size_t kConfirmationPayloadSize = 256U;
inline constexpr std::size_t kToxPublicKeySize = 32U;
inline constexpr std::uint8_t kCanonicalSessionTranscriptVersion = 1U;
inline constexpr std::size_t kCanonicalSessionTranscriptSize = 296U;

using SessionNonce = std::array<std::uint8_t, 16U>;
using ToxPublicKey = std::array<std::uint8_t, kToxPublicKeySize>;
using CanonicalHello = std::array<std::uint8_t, kHelloPayloadSize>;
using CanonicalSessionTranscript =
    std::array<std::uint8_t, kCanonicalSessionTranscriptSize>;

enum class Feature : std::uint64_t {
    capability_session_v1 = 1ULL << 0U,
    tox_text_lane = 1ULL << 1U,
    finite_file_transfer_v1 = 1ULL << 2U,

    // Reserved, named product directions. They are not advertised until the
    // corresponding runtime semantics exist and are exercised.
    authorization_ledger_v1 = 1ULL << 16U,
    durable_commands_v1 = 1ULL << 17U,
    state_sync_v1 = 1ULL << 18U,
    recall_reentry_v1 = 1ULL << 19U,
    signed_ota_v1 = 1ULL << 20U,
    route_binding_v1 = 1ULL << 21U,
    mutorr_namespaces_v1 = 1ULL << 22U,
    ratox_interactive_v1 = 1ULL << 23U,
    authorization_ledger_v2 = 1ULL << 24U,
    authorization_ledger_v3 = 1ULL << 25U,
    state_sync_ranges_v1 = 1ULL << 26U,
    application_epoch_restart_v1 = 1ULL << 27U,
    private_route_binding_v2 = 1ULL << 28U,
    state_sync_content_v2 = 1ULL << 29U,
    state_sync_tree_v2 = 1ULL << 30U,
    state_sync_tree_checkpoint_v2 = 1ULL << 31U,
};

[[nodiscard]] constexpr std::uint64_t feature_bit(Feature feature) noexcept {
    return static_cast<std::uint64_t>(feature);
}

inline constexpr std::uint64_t kImplementedFeatureMask =
    feature_bit(Feature::capability_session_v1) |
    feature_bit(Feature::tox_text_lane) |
    feature_bit(Feature::finite_file_transfer_v1) |
    feature_bit(Feature::authorization_ledger_v1) |
    feature_bit(Feature::authorization_ledger_v2) |
    feature_bit(Feature::authorization_ledger_v3) |
    feature_bit(Feature::durable_commands_v1);
inline constexpr std::uint64_t kRequiredFeatureMask =
    feature_bit(Feature::capability_session_v1);
inline constexpr std::uint64_t kNamedFeatureMask =
    kImplementedFeatureMask | feature_bit(Feature::authorization_ledger_v1) |
    feature_bit(Feature::durable_commands_v1) |
    feature_bit(Feature::state_sync_v1) |
    feature_bit(Feature::recall_reentry_v1) |
    feature_bit(Feature::signed_ota_v1) |
    feature_bit(Feature::route_binding_v1) |
    feature_bit(Feature::mutorr_namespaces_v1) |
    feature_bit(Feature::ratox_interactive_v1) |
    feature_bit(Feature::state_sync_ranges_v1) |
    feature_bit(Feature::application_epoch_restart_v1) |
    feature_bit(Feature::private_route_binding_v2) |
    feature_bit(Feature::state_sync_content_v2) |
    feature_bit(Feature::state_sync_tree_v2) |
    feature_bit(Feature::state_sync_tree_checkpoint_v2);

struct ProtocolVersion {
    std::uint8_t major{0U};
    std::uint8_t minor{0U};

    [[nodiscard]] bool operator==(const ProtocolVersion &) const = default;
};

struct HelloPayload {
    ProtocolVersion minimum_protocol{kProtocolMajor, kProtocolMinor};
    ProtocolVersion maximum_protocol{kProtocolMajor, kProtocolMinor};
    std::uint16_t implementation_major{0U};
    std::uint16_t implementation_minor{0U};
    std::uint16_t implementation_patch{0U};
    std::uint16_t build_revision{0U};
    std::uint16_t maximum_frame_payload_size{
        static_cast<std::uint16_t>(kMaxPayloadSize)};
    std::uint64_t supported_features{kImplementedFeatureMask};
    std::uint64_t required_features{kRequiredFeatureMask};
    std::uint64_t maximum_finite_file_bytes{0U};
    SessionNonce session_nonce{};

    [[nodiscard]] bool operator==(const HelloPayload &) const = default;
};

enum class NegotiationFailure : std::uint8_t {
    none = 0U,
    no_common_version = 1U,
    local_required_feature_missing = 2U,
    peer_required_feature_missing = 3U,
};

struct NegotiatedProtocol {
    bool compatible{false};
    NegotiationFailure failure{NegotiationFailure::none};
    ProtocolVersion selected{};
    std::uint64_t shared_features{0U};
    std::uint16_t maximum_frame_payload_size{0U};
    std::uint64_t maximum_finite_file_bytes{0U};
    std::string detail;

    [[nodiscard]] bool operator==(const NegotiatedProtocol &) const = default;
};

enum class SessionRole : std::uint8_t {
    lower_transport_key = 0U,
    higher_transport_key = 1U,
};

struct ConfirmationPayload {
    SessionRole sender_role{SessionRole::lower_transport_key};
    NegotiatedProtocol negotiated{};
    ToxPublicKey lower_public_key{};
    ToxPublicKey higher_public_key{};
    SessionNonce lower_nonce{};
    SessionNonce higher_nonce{};
    CanonicalHello lower_hello{};
    CanonicalHello higher_hello{};

    [[nodiscard]] bool operator==(const ConfirmationPayload &) const = default;
};

enum class PeerSessionState : std::uint8_t {
    offline = 0U,
    awaiting_hello = 1U,
    awaiting_confirmation = 2U,
    confirmed = 3U,
    incompatible_version = 4U,
    incompatible_features = 5U,
    malformed_frame = 6U,
    malformed_hello = 7U,
    conflicting_hello = 8U,
    hello_send_failed = 9U,
    malformed_confirmation = 10U,
    conflicting_confirmation = 11U,
    confirmation_send_failed = 12U,
};

struct PeerSessionSnapshot {
    std::uint32_t friend_number{0U};
    std::string public_key;
    std::string local_public_key;
    int connection_status{0};
    PeerSessionState state{PeerSessionState::offline};
    bool connected{false};
    bool hello_sent{false};
    bool hello_received{false};
    bool confirmation_sent{false};
    bool confirmation_received{false};
    bool application_ready{false};
    bool local_role_known{false};
    SessionRole local_role{SessionRole::lower_transport_key};
    std::uint64_t online_epoch{0U};
    std::uint64_t local_hello_message_id{0U};
    std::uint64_t peer_hello_message_id{0U};
    std::uint64_t local_confirmation_message_id{0U};
    std::uint64_t peer_confirmation_message_id{0U};
    std::uint64_t updated_unix_ms{0U};
    HelloPayload local{};
    HelloPayload peer{};
    NegotiatedProtocol negotiated{};
    std::string detail{"offline"};
    std::uint32_t hello_send_attempts{0U};
    std::uint32_t confirmation_send_attempts{0U};
    ErrorCode last_hello_send_error_code{ErrorCode::ok};
    ErrorCode last_confirmation_send_error_code{ErrorCode::ok};
    std::string last_hello_send_error;
    std::string last_confirmation_send_error;

    [[nodiscard]] bool operator==(const PeerSessionSnapshot &) const = default;
};

[[nodiscard]] HelloPayload make_local_hello(
    std::uint64_t maximum_finite_file_bytes, const SessionNonce &session_nonce,
    std::uint64_t supported_features = kImplementedFeatureMask);
// application-epoch-restart-v1 orders a nonce by one durable, monotonically
// increasing process incarnation followed by one process-local connection
// epoch. The final four bytes retain entropy so the nonce remains unique.
// Zero in either ordered field is the legacy unstructured nonce form and may
// never authorize an in-transport restart.
[[nodiscard]] SessionNonce bind_session_generation(
    SessionNonce entropy, std::uint64_t incarnation,
    std::uint32_t connection_epoch) noexcept;
[[nodiscard]] std::uint64_t session_incarnation(
    const SessionNonce &nonce) noexcept;
[[nodiscard]] std::uint32_t session_connection_epoch(
    const SessionNonce &nonce) noexcept;
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_hello_payload(
    const HelloPayload &hello);
[[nodiscard]] Result<HelloPayload> decode_hello_payload(
    std::span<const std::uint8_t> payload);
[[nodiscard]] NegotiatedProtocol negotiate_protocol(
    const HelloPayload &local, const HelloPayload &peer);
[[nodiscard]] Status validate_hello_frame(const Frame &frame);

[[nodiscard]] Result<ConfirmationPayload> make_confirmation_payload(
    std::string_view sender_public_key,
    std::string_view other_public_key,
    const HelloPayload &sender_hello,
    const HelloPayload &other_hello);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_confirmation_payload(
    const ConfirmationPayload &confirmation);
[[nodiscard]] Result<ConfirmationPayload> decode_confirmation_payload(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Status validate_confirmation_frame(const Frame &frame);

[[nodiscard]] std::string to_string(PeerSessionState state);
[[nodiscard]] std::string to_string(NegotiationFailure failure);
[[nodiscard]] std::string to_string(SessionRole role);
[[nodiscard]] std::string render_feature_mask(std::uint64_t feature_mask);
[[nodiscard]] std::string nonce_hex(const SessionNonce &nonce);
[[nodiscard]] std::string public_key_hex(const ToxPublicKey &public_key);
[[nodiscard]] bool is_application_ready(
    const PeerSessionSnapshot &snapshot) noexcept;
[[nodiscard]] Status validate_application_frame_for_session(
    const PeerSessionSnapshot &snapshot, const Frame &frame);
[[nodiscard]] Result<CanonicalSessionTranscript>
encode_canonical_session_transcript(const PeerSessionSnapshot &snapshot);

// Thread-safe, per-friend online-epoch state. The first valid remote HELLO and
// confirmation payload are frozen for the epoch. Byte-identical retries are
// idempotent; changed transcript material is a protocol conflict rather than a
// mid-session renegotiation or downgrade.
[[nodiscard]] std::string render_session_snapshot(
    const PeerSessionSnapshot &snapshot);

class PeerSessionRegistry {
  public:
    explicit PeerSessionRegistry(std::uint64_t maximum_finite_file_bytes);

    // Runtime-gated features must be selected before any peer is admitted.
    // This lets the Agent keep experimental semantics unadvertised by default
    // while still freezing one exact feature mask into every online epoch.
    [[nodiscard]] Status set_supported_features(
        std::uint64_t supported_features);
    [[nodiscard]] Status set_local_incarnation(std::uint64_t incarnation);

    // The local key is the first 32 bytes of the current Tox address. It is set
    // once after toxcore starts and anchors deterministic transcript ordering.
    [[nodiscard]] Status set_local_public_key(std::string public_key);

    [[nodiscard]] Status ensure_offline_peer(
        std::uint32_t friend_number, std::string public_key,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Result<PeerSessionSnapshot> peer_online(
        std::uint32_t friend_number, std::string public_key,
        int connection_status, const SessionNonce &nonce,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status peer_offline(
        std::uint32_t friend_number, std::uint64_t now_unix_ms);
    void erase(std::uint32_t friend_number);

    // Constructing the first frame reserves its message identifier before any
    // transport enqueue. A rejected enqueue must therefore retry the exact
    // same logical record rather than generate another identifier.
    [[nodiscard]] Result<Frame> make_hello_frame(
        std::uint32_t friend_number, std::uint64_t message_id);
    [[nodiscard]] Status mark_hello_sent(
        std::uint32_t friend_number, std::uint64_t message_id,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_hello_send_failed(
        std::uint32_t friend_number, ErrorCode error_code,
        std::string error, std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_malformed_frame(
        std::uint32_t friend_number, std::string error,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_malformed_hello(
        std::uint32_t friend_number, std::string error,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status receive_hello(
        std::uint32_t friend_number, std::string_view public_key,
        const Frame &frame, std::uint64_t now_unix_ms);

    [[nodiscard]] Result<Frame> make_confirmation_frame(
        std::uint32_t friend_number, std::uint64_t message_id);
    [[nodiscard]] Status mark_confirmation_sent(
        std::uint32_t friend_number, std::uint64_t message_id,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_confirmation_send_failed(
        std::uint32_t friend_number, ErrorCode error_code,
        std::string error, std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_malformed_confirmation(
        std::uint32_t friend_number, std::string error,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status receive_confirmation(
        std::uint32_t friend_number, std::string_view public_key,
        const Frame &frame, std::uint64_t now_unix_ms);

    [[nodiscard]] Result<PeerSessionSnapshot> get(
        std::uint32_t friend_number) const;
    [[nodiscard]] std::vector<PeerSessionSnapshot> list() const;

  private:
    struct Entry {
        PeerSessionSnapshot snapshot;
        std::vector<std::uint8_t> frozen_peer_hello_payload;
        std::vector<std::uint8_t> frozen_peer_confirmation_payload;
    };

    [[nodiscard]] static Status validate_public_key(
        std::string_view public_key);

    std::uint64_t maximum_finite_file_bytes_{0U};
    std::uint64_t supported_features_{kImplementedFeatureMask};
    std::uint64_t local_incarnation_{0U};
    std::string local_public_key_;
    mutable std::mutex mutex_;
    std::unordered_map<std::uint32_t, Entry> entries_;
};

}  // namespace iotox::protocol
