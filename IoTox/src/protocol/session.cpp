#include "iotox/protocol/session.hpp"

#include "iotox/version.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <iomanip>
#include <limits>
#include <sstream>
#include <utility>

namespace iotox::protocol {
namespace {

constexpr std::array<std::uint8_t, 4U> kHelloMagic{'I', 'H', 'L', '1'};
constexpr std::size_t kHelloOffsetPayloadVersion = 4U;
constexpr std::size_t kHelloOffsetFlags = 5U;
constexpr std::size_t kHelloOffsetMinimumMajor = 6U;
constexpr std::size_t kHelloOffsetMinimumMinor = 7U;
constexpr std::size_t kHelloOffsetMaximumMajor = 8U;
constexpr std::size_t kHelloOffsetMaximumMinor = 9U;
constexpr std::size_t kHelloOffsetImplementationMajor = 10U;
constexpr std::size_t kHelloOffsetImplementationMinor = 12U;
constexpr std::size_t kHelloOffsetImplementationPatch = 14U;
constexpr std::size_t kHelloOffsetBuildRevision = 16U;
constexpr std::size_t kHelloOffsetMaximumFramePayload = 18U;
constexpr std::size_t kHelloOffsetSupportedFeatures = 20U;
constexpr std::size_t kHelloOffsetRequiredFeatures = 28U;
constexpr std::size_t kHelloOffsetMaximumFiniteFileBytes = 36U;
constexpr std::size_t kHelloOffsetSessionNonce = 44U;
constexpr std::size_t kHelloOffsetReserved = 60U;

constexpr std::array<std::uint8_t, 4U> kConfirmationMagic{'I', 'C', 'F', '1'};
constexpr std::size_t kConfirmationOffsetPayloadVersion = 4U;
constexpr std::size_t kConfirmationOffsetFlags = 5U;
constexpr std::size_t kConfirmationOffsetSenderRole = 6U;
constexpr std::size_t kConfirmationOffsetReserved0 = 7U;
constexpr std::size_t kConfirmationOffsetSelectedMajor = 8U;
constexpr std::size_t kConfirmationOffsetSelectedMinor = 9U;
constexpr std::size_t kConfirmationOffsetMaximumFramePayload = 10U;
constexpr std::size_t kConfirmationOffsetSharedFeatures = 12U;
constexpr std::size_t kConfirmationOffsetMaximumFiniteFileBytes = 20U;
constexpr std::size_t kConfirmationOffsetLowerPublicKey = 28U;
constexpr std::size_t kConfirmationOffsetHigherPublicKey = 60U;
constexpr std::size_t kConfirmationOffsetLowerNonce = 92U;
constexpr std::size_t kConfirmationOffsetHigherNonce = 108U;
constexpr std::size_t kConfirmationOffsetLowerHello = 124U;
constexpr std::size_t kConfirmationOffsetHigherHello = 188U;
constexpr std::size_t kConfirmationOffsetReservedTail = 252U;

void write_u16(std::span<std::uint8_t> output, std::size_t offset,
               std::uint16_t value) {
    output[offset] = static_cast<std::uint8_t>((value >> 8U) & 0xFFU);
    output[offset + 1U] = static_cast<std::uint8_t>(value & 0xFFU);
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        const unsigned int shift = static_cast<unsigned int>((7U - index) * 8U);
        output[offset + index] =
            static_cast<std::uint8_t>((value >> shift) & 0xFFU);
    }
}

std::uint16_t read_u16(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(input[offset]) << 8U) |
        static_cast<std::uint16_t>(input[offset + 1U]));
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | input[offset + index];
    }
    return value;
}

int compare_version(ProtocolVersion left, ProtocolVersion right) noexcept {
    if (left.major != right.major) {
        return left.major < right.major ? -1 : 1;
    }
    if (left.minor != right.minor) {
        return left.minor < right.minor ? -1 : 1;
    }
    return 0;
}

ProtocolVersion minimum_version(ProtocolVersion left,
                                ProtocolVersion right) noexcept {
    return compare_version(left, right) <= 0 ? left : right;
}

ProtocolVersion maximum_version(ProtocolVersion left,
                                ProtocolVersion right) noexcept {
    return compare_version(left, right) >= 0 ? left : right;
}

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t value) {
        return value == 0U;
    });
}

std::string_view error_code_text(ErrorCode code) noexcept {
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

std::string version_text(ProtocolVersion version) {
    return std::to_string(static_cast<unsigned int>(version.major)) + "." +
           std::to_string(static_cast<unsigned int>(version.minor));
}

Status validate_hello(const HelloPayload &hello) {
    if (hello.minimum_protocol.major == 0U ||
        hello.maximum_protocol.major == 0U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO protocol major version zero is reserved"};
    }
    if (compare_version(hello.maximum_protocol,
                        hello.minimum_protocol) < 0) {
        return Status{ErrorCode::protocol_error,
                      "HELLO protocol range is reversed"};
    }
    if (hello.maximum_frame_payload_size < kConfirmationPayloadSize ||
        hello.maximum_frame_payload_size > kMaxPayloadSize) {
        return Status{ErrorCode::protocol_error,
                      "HELLO maximum frame payload cannot carry the v1 "
                      "confirmation or exceeds Tox bounds"};
    }
    if ((hello.required_features & ~hello.supported_features) != 0U) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO requires a feature it does not advertise as supported"};
    }
    if ((hello.required_features &
         feature_bit(Feature::capability_session_v1)) == 0U) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO must require capability-session-v1"};
    }
    if ((hello.supported_features &
         feature_bit(Feature::authorization_ledger_v3)) != 0U &&
        (hello.supported_features &
         feature_bit(Feature::authorization_ledger_v2)) == 0U) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO authority-ledger-v3 requires the v2 lineage feature"};
    }
    if ((hello.supported_features &
         feature_bit(Feature::state_sync_ranges_v1)) != 0U &&
        (hello.supported_features &
         feature_bit(Feature::state_sync_v1)) == 0U) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO state-sync-ranges-v1 requires state-sync-v1"};
    }
    if ((hello.supported_features &
         feature_bit(Feature::state_sync_content_v2)) != 0U &&
        (hello.supported_features &
         feature_bit(Feature::state_sync_v1)) == 0U) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO state-sync-content-v2 requires state-sync-v1"};
    }
    if ((hello.supported_features & feature_bit(Feature::state_sync_tree_v2)) !=
            0U &&
        (hello.supported_features & feature_bit(Feature::state_sync_v1)) ==
            0U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO state-sync-tree-v2 requires state-sync-v1"};
    }
    if ((hello.supported_features & feature_bit(
             Feature::state_sync_tree_checkpoint_v2)) != 0U &&
        (hello.supported_features & feature_bit(Feature::state_sync_tree_v2)) ==
            0U) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO state-sync-tree-checkpoint-v2 requires state-sync-tree-v2"};
    }
    const std::uint64_t ota_dependencies =
        feature_bit(Feature::durable_commands_v1) |
        feature_bit(Feature::state_sync_v1) |
        feature_bit(Feature::state_sync_ranges_v1);
    if ((hello.supported_features &
         feature_bit(Feature::signed_ota_v1)) != 0U &&
        (hello.supported_features & ota_dependencies) != ota_dependencies) {
        return Status{ErrorCode::protocol_error,
                      "HELLO signed-ota-v1 requires durable commands and range "
                      "synchronization"};
    }
    if ((hello.supported_features & feature_bit(
             Feature::application_epoch_restart_v1)) != 0U &&
        (session_incarnation(hello.session_nonce) == 0U ||
         session_connection_epoch(hello.session_nonce) == 0U)) {
        return Status{ErrorCode::protocol_error,
                      "HELLO application-epoch-restart-v1 requires a nonzero "
                      "durable incarnation and connection epoch"};
    }
    const std::uint64_t private_route_dependencies =
        feature_bit(Feature::authorization_ledger_v1) |
        feature_bit(Feature::route_binding_v1);
    if ((hello.supported_features & feature_bit(
             Feature::private_route_binding_v2)) != 0U &&
        (hello.supported_features & private_route_dependencies) !=
            private_route_dependencies) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO private-route-binding-v2 requires authority-ledger-v1 "
            "and route-binding-v1"};
    }
    const bool finite_file_feature =
        (hello.supported_features &
         feature_bit(Feature::finite_file_transfer_v1)) != 0U;
    if (finite_file_feature != (hello.maximum_finite_file_bytes != 0U)) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO finite-file feature and byte limit disagree"};
    }
    if (all_zero(hello.session_nonce)) {
        return Status{ErrorCode::protocol_error,
                      "HELLO session nonce may not be all zero"};
    }
    return Status::success();
}

std::string hexadecimal(std::uint64_t value) {
    std::ostringstream output;
    output << "0x" << std::hex << std::uppercase << std::setfill('0')
           << std::setw(16) << value;
    return output.str();
}

void append_feature(std::ostringstream &output, bool &first,
                    std::string_view name) {
    if (!first) {
        output << ',';
    }
    output << name;
    first = false;
}

PeerSessionState state_for_negotiation(
    const NegotiatedProtocol &negotiated) noexcept {
    if (negotiated.compatible) {
        return PeerSessionState::awaiting_confirmation;
    }
    switch (negotiated.failure) {
        case NegotiationFailure::no_common_version:
            return PeerSessionState::incompatible_version;
        case NegotiationFailure::local_required_feature_missing:
        case NegotiationFailure::peer_required_feature_missing:
            return PeerSessionState::incompatible_features;
        case NegotiationFailure::none:
            return PeerSessionState::malformed_hello;
    }
    return PeerSessionState::malformed_hello;
}

void update_progress(PeerSessionSnapshot &snapshot) {
    snapshot.application_ready = false;
    if (!snapshot.connected) {
        snapshot.state = PeerSessionState::offline;
        snapshot.detail = "transport peer is offline";
        return;
    }
    if (snapshot.hello_received && !snapshot.negotiated.compatible) {
        snapshot.state = state_for_negotiation(snapshot.negotiated);
        snapshot.detail = snapshot.negotiated.detail;
        return;
    }
    if (!snapshot.hello_sent || !snapshot.hello_received) {
        snapshot.state = PeerSessionState::awaiting_hello;
        if (!snapshot.hello_sent && !snapshot.hello_received) {
            snapshot.detail = "transport online; canonical HELLO exchange pending";
        } else if (!snapshot.hello_sent) {
            snapshot.detail = "peer HELLO accepted; local HELLO is not yet queued";
        } else {
            snapshot.detail = "canonical HELLO sent; awaiting peer HELLO";
        }
        return;
    }
    if (!snapshot.confirmation_sent || !snapshot.confirmation_received) {
        snapshot.state = PeerSessionState::awaiting_confirmation;
        if (!snapshot.confirmation_sent && !snapshot.confirmation_received) {
            snapshot.detail =
                "HELLO negotiation is compatible; transcript confirmations pending";
        } else if (!snapshot.confirmation_sent) {
            snapshot.detail =
                "peer confirmed the transcript; local confirmation is not yet queued";
        } else {
            snapshot.detail =
                "local transcript confirmation sent; awaiting peer confirmation";
        }
        return;
    }
    snapshot.state = PeerSessionState::confirmed;
    snapshot.application_ready = true;
    snapshot.detail =
        "online-epoch transcript confirmed; application gate open; "
        "authorization still required";
}

int hex_nibble(char character) noexcept {
    if (character >= '0' && character <= '9') {
        return character - '0';
    }
    if (character >= 'A' && character <= 'F') {
        return 10 + character - 'A';
    }
    return -1;
}

Result<ToxPublicKey> parse_public_key(std::string_view public_key) {
    if (public_key.size() != kToxPublicKeySize * 2U) {
        return Status{ErrorCode::invalid_argument,
                      "Tox public key must contain 64 uppercase hexadecimal characters"};
    }
    ToxPublicKey bytes{};
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
        const int high = hex_nibble(public_key[index * 2U]);
        const int low = hex_nibble(public_key[index * 2U + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::invalid_argument,
                          "Tox public key must use uppercase hexadecimal"};
        }
        bytes[index] = static_cast<std::uint8_t>((high << 4U) | low);
    }
    if (all_zero(bytes)) {
        return Status{ErrorCode::invalid_argument,
                      "all-zero Tox public key is reserved"};
    }
    return bytes;
}

bool key_less(const ToxPublicKey &left, const ToxPublicKey &right) noexcept {
    return std::lexicographical_compare(
        left.begin(), left.end(), right.begin(), right.end());
}

bool same_negotiation_values(const NegotiatedProtocol &left,
                             const NegotiatedProtocol &right) noexcept {
    return left.compatible == right.compatible &&
           left.failure == right.failure &&
           left.selected == right.selected &&
           left.shared_features == right.shared_features &&
           left.maximum_frame_payload_size ==
               right.maximum_frame_payload_size &&
           left.maximum_finite_file_bytes ==
               right.maximum_finite_file_bytes;
}

Status validate_confirmation(const ConfirmationPayload &confirmation) {
    if (!key_less(confirmation.lower_public_key,
                  confirmation.higher_public_key)) {
        return Status{
            ErrorCode::protocol_error,
            "confirmation transport keys are not in strict canonical order"};
    }
    if (all_zero(confirmation.lower_nonce) ||
        all_zero(confirmation.higher_nonce)) {
        return Status{ErrorCode::protocol_error,
                      "confirmation session nonces may not be all zero"};
    }

    auto lower = decode_hello_payload(confirmation.lower_hello);
    if (!lower) {
        return Status{ErrorCode::protocol_error,
                      "confirmation lower HELLO is invalid: " +
                          lower.status().message()};
    }
    auto higher = decode_hello_payload(confirmation.higher_hello);
    if (!higher) {
        return Status{ErrorCode::protocol_error,
                      "confirmation higher HELLO is invalid: " +
                          higher.status().message()};
    }
    if (lower.value().session_nonce != confirmation.lower_nonce ||
        higher.value().session_nonce != confirmation.higher_nonce) {
        return Status{ErrorCode::protocol_error,
                      "confirmation nonce fields do not match the embedded HELLOs"};
    }

    const NegotiatedProtocol expected =
        negotiate_protocol(lower.value(), higher.value());
    if (!expected.compatible) {
        return Status{ErrorCode::protocol_error,
                      "confirmation embeds an incompatible HELLO transcript: " +
                          expected.detail};
    }
    if (!same_negotiation_values(confirmation.negotiated, expected)) {
        return Status{ErrorCode::protocol_error,
                      "confirmation negotiation result does not match the embedded HELLOs"};
    }
    if ((confirmation.negotiated.shared_features &
         feature_bit(Feature::capability_session_v1)) == 0U) {
        return Status{ErrorCode::protocol_error,
                      "confirmation did not negotiate capability-session-v1"};
    }
    if (confirmation.negotiated.maximum_frame_payload_size <
        kConfirmationPayloadSize) {
        return Status{ErrorCode::protocol_error,
                      "confirmation negotiated a frame limit smaller than itself"};
    }
    return Status::success();
}

}  // namespace

SessionNonce bind_session_generation(
    SessionNonce entropy, std::uint64_t incarnation,
    std::uint32_t connection_epoch) noexcept {
    for (std::size_t index = 0U; index < 8U; ++index) {
        const unsigned int shift =
            static_cast<unsigned int>((7U - index) * 8U);
        entropy[index] =
            static_cast<std::uint8_t>((incarnation >> shift) & 0xffU);
    }
    for (std::size_t index = 0U; index < 4U; ++index) {
        const unsigned int shift =
            static_cast<unsigned int>((3U - index) * 8U);
        entropy[8U + index] = static_cast<std::uint8_t>(
            (connection_epoch >> shift) & 0xffU);
    }
    return entropy;
}

std::uint64_t session_incarnation(const SessionNonce &nonce) noexcept {
    std::uint64_t incarnation = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        incarnation = (incarnation << 8U) |
            static_cast<std::uint64_t>(nonce[index]);
    }
    return incarnation;
}

std::uint32_t session_connection_epoch(
    const SessionNonce &nonce) noexcept {
    std::uint32_t connection_epoch = 0U;
    for (std::size_t index = 8U; index < 12U; ++index) {
        connection_epoch = (connection_epoch << 8U) |
            static_cast<std::uint32_t>(nonce[index]);
    }
    return connection_epoch;
}

HelloPayload make_local_hello(std::uint64_t maximum_finite_file_bytes,
                              const SessionNonce &session_nonce,
                              std::uint64_t supported_features) {
    HelloPayload hello;
    hello.implementation_major = kVersionMajor;
    hello.implementation_minor = kVersionMinor;
    hello.implementation_patch = kVersionPatch;
    hello.build_revision = kRevisionNumber;
    hello.maximum_frame_payload_size =
        static_cast<std::uint16_t>(kMaxPayloadSize);
    hello.supported_features = supported_features;
    hello.required_features = kRequiredFeatureMask;
    hello.maximum_finite_file_bytes = maximum_finite_file_bytes;
    if (maximum_finite_file_bytes == 0U) {
        hello.supported_features &=
            ~feature_bit(Feature::finite_file_transfer_v1);
    }
    hello.session_nonce = session_nonce;
    return hello;
}

Result<std::vector<std::uint8_t>> encode_hello_payload(
    const HelloPayload &hello) {
    const Status valid = validate_hello(hello);
    if (!valid.ok()) {
        return valid;
    }

    std::vector<std::uint8_t> output(kHelloPayloadSize, 0U);
    std::copy(kHelloMagic.begin(), kHelloMagic.end(), output.begin());
    output[kHelloOffsetPayloadVersion] = kHelloPayloadVersion;
    output[kHelloOffsetFlags] = 0U;
    output[kHelloOffsetMinimumMajor] = hello.minimum_protocol.major;
    output[kHelloOffsetMinimumMinor] = hello.minimum_protocol.minor;
    output[kHelloOffsetMaximumMajor] = hello.maximum_protocol.major;
    output[kHelloOffsetMaximumMinor] = hello.maximum_protocol.minor;
    write_u16(output, kHelloOffsetImplementationMajor,
              hello.implementation_major);
    write_u16(output, kHelloOffsetImplementationMinor,
              hello.implementation_minor);
    write_u16(output, kHelloOffsetImplementationPatch,
              hello.implementation_patch);
    write_u16(output, kHelloOffsetBuildRevision, hello.build_revision);
    write_u16(output, kHelloOffsetMaximumFramePayload,
              hello.maximum_frame_payload_size);
    write_u64(output, kHelloOffsetSupportedFeatures, hello.supported_features);
    write_u64(output, kHelloOffsetRequiredFeatures, hello.required_features);
    write_u64(output, kHelloOffsetMaximumFiniteFileBytes,
              hello.maximum_finite_file_bytes);
    std::copy(hello.session_nonce.begin(), hello.session_nonce.end(),
              output.begin() +
                  static_cast<std::ptrdiff_t>(kHelloOffsetSessionNonce));
    return output;
}

Result<HelloPayload> decode_hello_payload(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kHelloPayloadSize) {
        return Status{ErrorCode::protocol_error,
                      "HELLO payload must contain exactly 64 bytes"};
    }
    if (!std::equal(kHelloMagic.begin(), kHelloMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "HELLO payload magic is invalid"};
    }
    if (payload[kHelloOffsetPayloadVersion] != kHelloPayloadVersion) {
        return Status{ErrorCode::protocol_error,
                      "HELLO payload version is unsupported"};
    }
    if (payload[kHelloOffsetFlags] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO payload flags must be zero"};
    }
    if (!all_zero(payload.subspan(kHelloOffsetReserved))) {
        return Status{ErrorCode::protocol_error,
                      "HELLO reserved bytes must be zero"};
    }

    HelloPayload hello;
    hello.minimum_protocol = {
        payload[kHelloOffsetMinimumMajor], payload[kHelloOffsetMinimumMinor]};
    hello.maximum_protocol = {
        payload[kHelloOffsetMaximumMajor], payload[kHelloOffsetMaximumMinor]};
    hello.implementation_major =
        read_u16(payload, kHelloOffsetImplementationMajor);
    hello.implementation_minor =
        read_u16(payload, kHelloOffsetImplementationMinor);
    hello.implementation_patch =
        read_u16(payload, kHelloOffsetImplementationPatch);
    hello.build_revision = read_u16(payload, kHelloOffsetBuildRevision);
    hello.maximum_frame_payload_size =
        read_u16(payload, kHelloOffsetMaximumFramePayload);
    hello.supported_features =
        read_u64(payload, kHelloOffsetSupportedFeatures);
    hello.required_features =
        read_u64(payload, kHelloOffsetRequiredFeatures);
    hello.maximum_finite_file_bytes =
        read_u64(payload, kHelloOffsetMaximumFiniteFileBytes);
    std::copy_n(payload.begin() +
                    static_cast<std::ptrdiff_t>(kHelloOffsetSessionNonce),
                hello.session_nonce.size(), hello.session_nonce.begin());

    const Status valid = validate_hello(hello);
    if (!valid.ok()) {
        return valid;
    }
    return hello;
}

NegotiatedProtocol negotiate_protocol(const HelloPayload &local,
                                       const HelloPayload &peer) {
    NegotiatedProtocol result;

    const Status local_valid = validate_hello(local);
    if (!local_valid.ok()) {
        result.detail = "local HELLO is invalid: " + local_valid.message();
        return result;
    }
    const Status peer_valid = validate_hello(peer);
    if (!peer_valid.ok()) {
        result.detail = "peer HELLO is invalid: " + peer_valid.message();
        return result;
    }

    const ProtocolVersion lower = maximum_version(
        local.minimum_protocol, peer.minimum_protocol);
    const ProtocolVersion upper = minimum_version(
        local.maximum_protocol, peer.maximum_protocol);
    if (compare_version(upper, lower) < 0) {
        result.failure = NegotiationFailure::no_common_version;
        result.detail =
            "no common IoTox protocol version: local=" +
            version_text(local.minimum_protocol) + ".." +
            version_text(local.maximum_protocol) + ", peer=" +
            version_text(peer.minimum_protocol) + ".." +
            version_text(peer.maximum_protocol);
        return result;
    }

    const std::uint64_t local_missing =
        local.required_features & ~peer.supported_features;
    if (local_missing != 0U) {
        result.failure =
            NegotiationFailure::local_required_feature_missing;
        result.detail = "peer lacks locally required features " +
                        render_feature_mask(local_missing);
        return result;
    }

    const std::uint64_t peer_missing =
        peer.required_features & ~local.supported_features;
    if (peer_missing != 0U) {
        result.failure = NegotiationFailure::peer_required_feature_missing;
        result.detail = "local implementation lacks peer-required features " +
                        render_feature_mask(peer_missing);
        return result;
    }

    result.compatible = true;
    result.failure = NegotiationFailure::none;
    result.selected = upper;
    result.shared_features =
        local.supported_features & peer.supported_features;
    result.maximum_frame_payload_size = std::min(
        local.maximum_frame_payload_size,
        peer.maximum_frame_payload_size);
    if ((result.shared_features &
         feature_bit(Feature::finite_file_transfer_v1)) != 0U) {
        result.maximum_finite_file_bytes = std::min(
            local.maximum_finite_file_bytes,
            peer.maximum_finite_file_bytes);
    }
    result.detail = "compatible IoTox session " +
                    version_text(result.selected) + "; shared=" +
                    render_feature_mask(result.shared_features);
    return result;
}

Status validate_hello_frame(const Frame &frame) {
    if (frame.type != MessageType::hello) {
        return Status{ErrorCode::protocol_error,
                      "session frame is not an IoTox HELLO"};
    }
    if (frame.major != kHelloFrameMajor ||
        frame.minor != kHelloFrameMinor) {
        return Status{ErrorCode::protocol_error,
                      "HELLO outer frame version must be 1.0"};
    }
    if (frame.flags != 0U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO frame flags must be zero"};
    }
    if (frame.message_id == 0U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO message identifier zero is reserved"};
    }
    if (frame.correlation_id != 0U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO correlation identifier must be zero"};
    }
    if (frame.sequence != 1U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO sequence must be one"};
    }
    if (frame.expiry_unix_ms != 0U) {
        return Status{ErrorCode::protocol_error,
                      "HELLO expiry must be zero"};
    }
    auto decoded = decode_hello_payload(frame.payload);
    return decoded ? Status::success() : decoded.status();
}

Result<ConfirmationPayload> make_confirmation_payload(
    std::string_view sender_public_key,
    std::string_view other_public_key,
    const HelloPayload &sender_hello,
    const HelloPayload &other_hello) {
    auto sender_key = parse_public_key(sender_public_key);
    if (!sender_key) {
        return sender_key.status();
    }
    auto other_key = parse_public_key(other_public_key);
    if (!other_key) {
        return other_key.status();
    }
    if (sender_key.value() == other_key.value()) {
        return Status{ErrorCode::protocol_error,
                      "confirmation requires two distinct transport keys"};
    }

    auto sender_encoded = encode_hello_payload(sender_hello);
    if (!sender_encoded) {
        return sender_encoded.status();
    }
    auto other_encoded = encode_hello_payload(other_hello);
    if (!other_encoded) {
        return other_encoded.status();
    }

    ConfirmationPayload confirmation;
    const bool sender_is_lower = key_less(sender_key.value(), other_key.value());
    confirmation.sender_role = sender_is_lower
        ? SessionRole::lower_transport_key
        : SessionRole::higher_transport_key;

    const HelloPayload &lower_hello =
        sender_is_lower ? sender_hello : other_hello;
    const HelloPayload &higher_hello =
        sender_is_lower ? other_hello : sender_hello;
    confirmation.lower_public_key =
        sender_is_lower ? sender_key.value() : other_key.value();
    confirmation.higher_public_key =
        sender_is_lower ? other_key.value() : sender_key.value();
    confirmation.lower_nonce = lower_hello.session_nonce;
    confirmation.higher_nonce = higher_hello.session_nonce;

    const std::vector<std::uint8_t> &lower_encoded =
        sender_is_lower ? sender_encoded.value() : other_encoded.value();
    const std::vector<std::uint8_t> &higher_encoded =
        sender_is_lower ? other_encoded.value() : sender_encoded.value();
    std::copy_n(lower_encoded.begin(), confirmation.lower_hello.size(),
                confirmation.lower_hello.begin());
    std::copy_n(higher_encoded.begin(), confirmation.higher_hello.size(),
                confirmation.higher_hello.begin());
    confirmation.negotiated = negotiate_protocol(lower_hello, higher_hello);
    if (!confirmation.negotiated.compatible) {
        return Status{ErrorCode::unsupported,
                      "cannot confirm an incompatible HELLO transcript: " +
                          confirmation.negotiated.detail};
    }

    const Status valid = validate_confirmation(confirmation);
    if (!valid.ok()) {
        return valid;
    }
    return confirmation;
}

Result<std::vector<std::uint8_t>> encode_confirmation_payload(
    const ConfirmationPayload &confirmation) {
    const Status valid = validate_confirmation(confirmation);
    if (!valid.ok()) {
        return valid;
    }

    std::vector<std::uint8_t> output(kConfirmationPayloadSize, 0U);
    std::copy(kConfirmationMagic.begin(), kConfirmationMagic.end(),
              output.begin());
    output[kConfirmationOffsetPayloadVersion] = kConfirmationPayloadVersion;
    output[kConfirmationOffsetFlags] = 0U;
    output[kConfirmationOffsetSenderRole] =
        static_cast<std::uint8_t>(confirmation.sender_role);
    output[kConfirmationOffsetReserved0] = 0U;
    output[kConfirmationOffsetSelectedMajor] =
        confirmation.negotiated.selected.major;
    output[kConfirmationOffsetSelectedMinor] =
        confirmation.negotiated.selected.minor;
    write_u16(output, kConfirmationOffsetMaximumFramePayload,
              confirmation.negotiated.maximum_frame_payload_size);
    write_u64(output, kConfirmationOffsetSharedFeatures,
              confirmation.negotiated.shared_features);
    write_u64(output, kConfirmationOffsetMaximumFiniteFileBytes,
              confirmation.negotiated.maximum_finite_file_bytes);
    std::copy(confirmation.lower_public_key.begin(),
              confirmation.lower_public_key.end(),
              output.begin() + static_cast<std::ptrdiff_t>(
                                   kConfirmationOffsetLowerPublicKey));
    std::copy(confirmation.higher_public_key.begin(),
              confirmation.higher_public_key.end(),
              output.begin() + static_cast<std::ptrdiff_t>(
                                   kConfirmationOffsetHigherPublicKey));
    std::copy(confirmation.lower_nonce.begin(), confirmation.lower_nonce.end(),
              output.begin() + static_cast<std::ptrdiff_t>(
                                   kConfirmationOffsetLowerNonce));
    std::copy(confirmation.higher_nonce.begin(), confirmation.higher_nonce.end(),
              output.begin() + static_cast<std::ptrdiff_t>(
                                   kConfirmationOffsetHigherNonce));
    std::copy(confirmation.lower_hello.begin(), confirmation.lower_hello.end(),
              output.begin() + static_cast<std::ptrdiff_t>(
                                   kConfirmationOffsetLowerHello));
    std::copy(confirmation.higher_hello.begin(), confirmation.higher_hello.end(),
              output.begin() + static_cast<std::ptrdiff_t>(
                                   kConfirmationOffsetHigherHello));
    return output;
}

Result<ConfirmationPayload> decode_confirmation_payload(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kConfirmationPayloadSize) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation must contain exactly 256 bytes"};
    }
    if (!std::equal(kConfirmationMagic.begin(), kConfirmationMagic.end(),
                    payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation magic is invalid"};
    }
    if (payload[kConfirmationOffsetPayloadVersion] !=
        kConfirmationPayloadVersion) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation version is unsupported"};
    }
    if (payload[kConfirmationOffsetFlags] != 0U ||
        payload[kConfirmationOffsetReserved0] != 0U ||
        !all_zero(payload.subspan(kConfirmationOffsetReservedTail))) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation flags and reserved bytes must be zero"};
    }
    if (payload[kConfirmationOffsetSenderRole] >
        static_cast<std::uint8_t>(SessionRole::higher_transport_key)) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation sender role is invalid"};
    }

    ConfirmationPayload confirmation;
    confirmation.sender_role = static_cast<SessionRole>(
        payload[kConfirmationOffsetSenderRole]);
    confirmation.negotiated.compatible = true;
    confirmation.negotiated.failure = NegotiationFailure::none;
    confirmation.negotiated.selected = {
        payload[kConfirmationOffsetSelectedMajor],
        payload[kConfirmationOffsetSelectedMinor]};
    confirmation.negotiated.maximum_frame_payload_size =
        read_u16(payload, kConfirmationOffsetMaximumFramePayload);
    confirmation.negotiated.shared_features =
        read_u64(payload, kConfirmationOffsetSharedFeatures);
    confirmation.negotiated.maximum_finite_file_bytes =
        read_u64(payload, kConfirmationOffsetMaximumFiniteFileBytes);

    std::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(
                                      kConfirmationOffsetLowerPublicKey),
                confirmation.lower_public_key.size(),
                confirmation.lower_public_key.begin());
    std::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(
                                      kConfirmationOffsetHigherPublicKey),
                confirmation.higher_public_key.size(),
                confirmation.higher_public_key.begin());
    std::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(
                                      kConfirmationOffsetLowerNonce),
                confirmation.lower_nonce.size(),
                confirmation.lower_nonce.begin());
    std::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(
                                      kConfirmationOffsetHigherNonce),
                confirmation.higher_nonce.size(),
                confirmation.higher_nonce.begin());
    std::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(
                                      kConfirmationOffsetLowerHello),
                confirmation.lower_hello.size(),
                confirmation.lower_hello.begin());
    std::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(
                                      kConfirmationOffsetHigherHello),
                confirmation.higher_hello.size(),
                confirmation.higher_hello.begin());

    const Status valid = validate_confirmation(confirmation);
    if (!valid.ok()) {
        return valid;
    }
    // `detail` is diagnostic text, not a wire field. Reconstruct it only after
    // every received negotiated value has been checked against the embedded
    // canonical HELLO transcript; doing this earlier would mask tampering.
    auto lower = decode_hello_payload(confirmation.lower_hello);
    auto higher = decode_hello_payload(confirmation.higher_hello);
    if (lower && higher) {
        confirmation.negotiated.detail =
            negotiate_protocol(lower.value(), higher.value()).detail;
    }
    return confirmation;
}

Status validate_confirmation_frame(const Frame &frame) {
    if (frame.type != MessageType::capabilities) {
        return Status{ErrorCode::protocol_error,
                      "session frame is not an IoTox CAPABILITIES confirmation"};
    }
    if (frame.flags != 0U) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation frame flags must be zero"};
    }
    if (frame.message_id == 0U) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation message identifier zero is reserved"};
    }
    if (frame.correlation_id == 0U) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation must correlate to the peer HELLO"};
    }
    if (frame.sequence != 2U) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation sequence must be two"};
    }
    if (frame.expiry_unix_ms != 0U) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES confirmation expiry must be zero"};
    }
    auto decoded = decode_confirmation_payload(frame.payload);
    if (!decoded) {
        return decoded.status();
    }
    if (frame.major != decoded.value().negotiated.selected.major ||
        frame.minor != decoded.value().negotiated.selected.minor) {
        return Status{ErrorCode::protocol_error,
                      "CAPABILITIES outer version does not match the confirmed negotiation"};
    }
    return Status::success();
}

std::string to_string(PeerSessionState state) {
    switch (state) {
        case PeerSessionState::offline:
            return "offline";
        case PeerSessionState::awaiting_hello:
            return "awaiting-hello";
        case PeerSessionState::awaiting_confirmation:
            return "awaiting-confirmation";
        case PeerSessionState::confirmed:
            return "confirmed";
        case PeerSessionState::incompatible_version:
            return "incompatible-version";
        case PeerSessionState::incompatible_features:
            return "incompatible-features";
        case PeerSessionState::malformed_frame:
            return "malformed-frame";
        case PeerSessionState::malformed_hello:
            return "malformed-hello";
        case PeerSessionState::conflicting_hello:
            return "conflicting-hello";
        case PeerSessionState::hello_send_failed:
            return "hello-send-failed";
        case PeerSessionState::malformed_confirmation:
            return "malformed-confirmation";
        case PeerSessionState::conflicting_confirmation:
            return "conflicting-confirmation";
        case PeerSessionState::confirmation_send_failed:
            return "confirmation-send-failed";
    }
    return "unknown";
}

std::string to_string(NegotiationFailure failure) {
    switch (failure) {
        case NegotiationFailure::none:
            return "none";
        case NegotiationFailure::no_common_version:
            return "no-common-version";
        case NegotiationFailure::local_required_feature_missing:
            return "local-required-feature-missing";
        case NegotiationFailure::peer_required_feature_missing:
            return "peer-required-feature-missing";
    }
    return "unknown";
}

std::string to_string(SessionRole role) {
    switch (role) {
        case SessionRole::lower_transport_key:
            return "lower-transport-key";
        case SessionRole::higher_transport_key:
            return "higher-transport-key";
    }
    return "unknown";
}

std::string render_feature_mask(std::uint64_t feature_mask) {
    std::ostringstream output;
    output << hexadecimal(feature_mask) << '[';
    bool first = true;
    if ((feature_mask & feature_bit(Feature::capability_session_v1)) != 0U) {
        append_feature(output, first, "capability-session-v1");
    }
    if ((feature_mask & feature_bit(Feature::tox_text_lane)) != 0U) {
        append_feature(output, first, "tox-text-lane");
    }
    if ((feature_mask & feature_bit(Feature::finite_file_transfer_v1)) != 0U) {
        append_feature(output, first, "finite-file-transfer-v1");
    }
    if ((feature_mask & feature_bit(Feature::authorization_ledger_v1)) != 0U) {
        append_feature(output, first, "authorization-ledger-v1");
    }
    if ((feature_mask & feature_bit(Feature::authorization_ledger_v2)) != 0U) {
        append_feature(output, first, "authorization-ledger-v2");
    }
    if ((feature_mask & feature_bit(Feature::authorization_ledger_v3)) != 0U) {
        append_feature(output, first, "authorization-ledger-v3");
    }
    if ((feature_mask & feature_bit(Feature::durable_commands_v1)) != 0U) {
        append_feature(output, first, "durable-commands-v1");
    }
    if ((feature_mask & feature_bit(Feature::state_sync_v1)) != 0U) {
        append_feature(output, first, "state-sync-v1");
    }
    if ((feature_mask & feature_bit(Feature::state_sync_ranges_v1)) != 0U) {
        append_feature(output, first, "state-sync-ranges-v1");
    }
    if ((feature_mask & feature_bit(Feature::recall_reentry_v1)) != 0U) {
        append_feature(output, first, "recall-reentry-v1");
    }
    if ((feature_mask & feature_bit(Feature::signed_ota_v1)) != 0U) {
        append_feature(output, first, "signed-ota-v1");
    }
    if ((feature_mask & feature_bit(Feature::route_binding_v1)) != 0U) {
        append_feature(output, first, "route-binding-v1");
    }
    if ((feature_mask & feature_bit(Feature::mutorr_namespaces_v1)) != 0U) {
        append_feature(output, first, "mutorr-namespaces-v1");
    }
    if ((feature_mask & feature_bit(Feature::ratox_interactive_v1)) != 0U) {
        append_feature(output, first, "ratox-interactive-v1");
    }
    if ((feature_mask & feature_bit(
             Feature::application_epoch_restart_v1)) != 0U) {
        append_feature(output, first, "application-epoch-restart-v1");
    }
    if ((feature_mask & feature_bit(
             Feature::private_route_binding_v2)) != 0U) {
        append_feature(output, first, "private-route-binding-v2");
    }
    if ((feature_mask & feature_bit(
             Feature::state_sync_content_v2)) != 0U) {
        append_feature(output, first, "state-sync-content-v2");
    }
    if ((feature_mask & feature_bit(Feature::state_sync_tree_v2)) != 0U) {
        append_feature(output, first, "state-sync-tree-v2");
    }
    if ((feature_mask & feature_bit(
             Feature::state_sync_tree_checkpoint_v2)) != 0U) {
        append_feature(output, first, "state-sync-tree-checkpoint-v2");
    }
    const std::uint64_t unknown = feature_mask & ~kNamedFeatureMask;
    if (unknown != 0U) {
        append_feature(output, first, "unknown=" + hexadecimal(unknown));
    }
    if (first) {
        output << "none";
    }
    output << ']';
    return output.str();
}

std::string nonce_hex(const SessionNonce &nonce) {
    std::ostringstream output;
    output << std::hex << std::uppercase << std::setfill('0');
    for (const std::uint8_t byte : nonce) {
        output << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return output.str();
}

std::string public_key_hex(const ToxPublicKey &public_key) {
    std::ostringstream output;
    output << std::hex << std::uppercase << std::setfill('0');
    for (const std::uint8_t byte : public_key) {
        output << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return output.str();
}

bool is_application_ready(const PeerSessionSnapshot &snapshot) noexcept {
    return snapshot.connected && snapshot.negotiated.compatible &&
           snapshot.confirmation_sent && snapshot.confirmation_received &&
           snapshot.application_ready &&
           snapshot.state == PeerSessionState::confirmed;
}

Status validate_application_frame_for_session(
    const PeerSessionSnapshot &snapshot, const Frame &frame) {
    if (frame.type == MessageType::hello ||
        frame.type == MessageType::capabilities) {
        return Status{ErrorCode::unsupported,
                      "HELLO and CAPABILITIES are reserved "
                      "to the canonical session machinery"};
    }
    if (!is_application_ready(snapshot)) {
        return Status{
            ErrorCode::unavailable,
            "IoTox application traffic requires a transcript-confirmed "
            "online session"};
    }
    if (frame.major != snapshot.negotiated.selected.major ||
        frame.minor != snapshot.negotiated.selected.minor) {
        return Status{
            ErrorCode::unsupported,
            "IoTox application frame version differs from the confirmed session"};
    }
    if (frame.message_id == 0U) {
        return Status{ErrorCode::protocol_error,
                      "IoTox application message identifier zero is reserved"};
    }
    if (frame.payload.size() >
        snapshot.negotiated.maximum_frame_payload_size) {
        return Status{
            ErrorCode::protocol_error,
            "IoTox application payload exceeds the confirmed peer limit"};
    }
    return Status::success();
}


Result<CanonicalSessionTranscript> encode_canonical_session_transcript(
    const PeerSessionSnapshot &snapshot) {
    if (!is_application_ready(snapshot)) {
        return Status{ErrorCode::unavailable,
                      "canonical session transcript requires a confirmed IoTox session"};
    }
    if (!snapshot.local_role_known || snapshot.local_public_key.empty() ||
        snapshot.local_hello_message_id == 0U ||
        snapshot.peer_hello_message_id == 0U ||
        snapshot.local_confirmation_message_id == 0U ||
        snapshot.peer_confirmation_message_id == 0U) {
        return Status{ErrorCode::protocol_error,
                      "confirmed session lacks canonical transcript identifiers"};
    }

    auto canonical = make_confirmation_payload(
        snapshot.local_public_key, snapshot.public_key,
        snapshot.local, snapshot.peer);
    if (!canonical) {
        return canonical.status();
    }
    canonical.value().sender_role = SessionRole::lower_transport_key;
    auto confirmation_bytes = encode_confirmation_payload(canonical.value());
    if (!confirmation_bytes) {
        return confirmation_bytes.status();
    }
    if (confirmation_bytes.value().size() != kConfirmationPayloadSize) {
        return Status{ErrorCode::internal_error,
                      "canonical confirmation encoder returned an unexpected length"};
    }

    const bool local_is_lower =
        snapshot.local_role == SessionRole::lower_transport_key;
    const std::uint64_t lower_hello_id = local_is_lower
        ? snapshot.local_hello_message_id
        : snapshot.peer_hello_message_id;
    const std::uint64_t higher_hello_id = local_is_lower
        ? snapshot.peer_hello_message_id
        : snapshot.local_hello_message_id;
    const std::uint64_t lower_confirmation_id = local_is_lower
        ? snapshot.local_confirmation_message_id
        : snapshot.peer_confirmation_message_id;
    const std::uint64_t higher_confirmation_id = local_is_lower
        ? snapshot.peer_confirmation_message_id
        : snapshot.local_confirmation_message_id;

    CanonicalSessionTranscript output{};
    output[0U] = 'I';
    output[1U] = 'T';
    output[2U] = 'S';
    output[3U] = '1';
    output[4U] = kCanonicalSessionTranscriptVersion;
    std::copy(
        confirmation_bytes.value().begin(), confirmation_bytes.value().end(),
        output.begin() + 8U);
    write_u64(output, 264U, lower_hello_id);
    write_u64(output, 272U, higher_hello_id);
    write_u64(output, 280U, lower_confirmation_id);
    write_u64(output, 288U, higher_confirmation_id);
    return output;
}

PeerSessionRegistry::PeerSessionRegistry(
    std::uint64_t maximum_finite_file_bytes)
    : maximum_finite_file_bytes_(maximum_finite_file_bytes) {}

Status PeerSessionRegistry::set_supported_features(
    std::uint64_t supported_features) {
    if ((supported_features & ~kNamedFeatureMask) != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session feature mask contains unnamed bits"};
    }
    if ((supported_features & kRequiredFeatureMask) !=
        kRequiredFeatureMask) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session feature mask omits a required feature"};
    }
    if ((supported_features & feature_bit(Feature::authorization_ledger_v3)) !=
            0U &&
        (supported_features & feature_bit(Feature::authorization_ledger_v2)) ==
            0U) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session authority-ledger-v3 requires the v2 lineage feature"};
    }
    if ((supported_features & feature_bit(Feature::state_sync_ranges_v1)) !=
            0U &&
        (supported_features & feature_bit(Feature::state_sync_v1)) == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session state-sync-ranges-v1 requires state-sync-v1"};
    }
    if ((supported_features & feature_bit(
             Feature::state_sync_content_v2)) != 0U &&
        (supported_features & feature_bit(Feature::state_sync_v1)) == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session state-sync-content-v2 requires state-sync-v1"};
    }
    if ((supported_features & feature_bit(Feature::state_sync_tree_v2)) != 0U &&
        (supported_features & feature_bit(Feature::state_sync_v1)) == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session state-sync-tree-v2 requires state-sync-v1"};
    }
    if ((supported_features & feature_bit(
             Feature::state_sync_tree_checkpoint_v2)) != 0U &&
        (supported_features & feature_bit(Feature::state_sync_tree_v2)) == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session tree checkpoint v2 requires state-sync-tree-v2"};
    }
    const std::uint64_t ota_dependencies =
        feature_bit(Feature::durable_commands_v1) |
        feature_bit(Feature::state_sync_v1) |
        feature_bit(Feature::state_sync_ranges_v1);
    if ((supported_features & feature_bit(Feature::signed_ota_v1)) != 0U &&
        (supported_features & ota_dependencies) != ota_dependencies) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session signed-ota-v1 requires durable commands and "
            "range synchronization"};
    }
    const std::uint64_t private_route_dependencies =
        feature_bit(Feature::authorization_ledger_v1) |
        feature_bit(Feature::route_binding_v1);
    if ((supported_features & feature_bit(
             Feature::private_route_binding_v2)) != 0U &&
        (supported_features & private_route_dependencies) !=
            private_route_dependencies) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session private-route-binding-v2 requires "
                      "authority-ledger-v1 and route-binding-v1"};
    }
    std::scoped_lock lock(mutex_);
    if (!entries_.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session feature mask is immutable after peer admission"};
    }
    supported_features_ = supported_features;
    return Status::success();
}

Status PeerSessionRegistry::set_local_incarnation(
    std::uint64_t incarnation) {
    if (incarnation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session local incarnation must be nonzero"};
    }
    std::scoped_lock lock(mutex_);
    if (!entries_.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session local incarnation is immutable after peer admission"};
    }
    if (local_incarnation_ != 0U && local_incarnation_ != incarnation) {
        return Status{
            ErrorCode::invalid_argument,
            "peer-session local incarnation is immutable after initialization"};
    }
    local_incarnation_ = incarnation;
    return Status::success();
}

Status PeerSessionRegistry::validate_public_key(std::string_view public_key) {
    auto parsed = parse_public_key(public_key);
    return parsed ? Status::success() : parsed.status();
}

Status PeerSessionRegistry::set_local_public_key(std::string public_key) {
    const Status valid = validate_public_key(public_key);
    if (!valid.ok()) {
        return valid;
    }
    std::scoped_lock lock(mutex_);
    if (!local_public_key_.empty() && local_public_key_ != public_key) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session local Tox public key is immutable after initialization"};
    }
    for (const auto &[friend_number, entry] : entries_) {
        static_cast<void>(friend_number);
        if (entry.snapshot.public_key == public_key) {
            return Status{ErrorCode::protocol_error,
                          "local Tox public key cannot also identify a friend session"};
        }
    }
    local_public_key_ = std::move(public_key);
    for (auto &[friend_number, entry] : entries_) {
        static_cast<void>(friend_number);
        entry.snapshot.local_public_key = local_public_key_;
    }
    return Status::success();
}

Status PeerSessionRegistry::ensure_offline_peer(
    std::uint32_t friend_number, std::string public_key,
    std::uint64_t now_unix_ms) {
    const Status valid_key = validate_public_key(public_key);
    if (!valid_key.ok()) {
        return valid_key;
    }
    std::scoped_lock lock(mutex_);
    if (!local_public_key_.empty() && local_public_key_ == public_key) {
        return Status{ErrorCode::protocol_error,
                      "friend session public key equals the local Tox public key"};
    }
    auto found = entries_.find(friend_number);
    if (found != entries_.end()) {
        if (found->second.snapshot.public_key != public_key) {
            return Status{
                ErrorCode::protocol_error,
                "transport friend number changed public key without removal"};
        }
        found->second.snapshot.local_public_key = local_public_key_;
        found->second.snapshot.updated_unix_ms = now_unix_ms;
        return Status::success();
    }

    Entry entry;
    entry.snapshot.friend_number = friend_number;
    entry.snapshot.public_key = std::move(public_key);
    entry.snapshot.local_public_key = local_public_key_;
    entry.snapshot.updated_unix_ms = now_unix_ms;
    entry.snapshot.detail = "transport friend exists; awaiting connection";
    entries_.emplace(friend_number, std::move(entry));
    return Status::success();
}

Result<PeerSessionSnapshot> PeerSessionRegistry::peer_online(
    std::uint32_t friend_number, std::string public_key,
    int connection_status, const SessionNonce &nonce,
    std::uint64_t now_unix_ms) {
    const Status valid_key = validate_public_key(public_key);
    if (!valid_key.ok()) {
        return valid_key;
    }
    if (connection_status == 0) {
        return Status{ErrorCode::invalid_argument,
                      "peer_online requires a nonzero Tox connection status"};
    }
    if (all_zero(nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "peer_online requires a nonzero session nonce"};
    }

    std::scoped_lock lock(mutex_);
    if (local_public_key_.empty()) {
        return Status{ErrorCode::unavailable,
                      "local Tox public key must be set before opening a peer session"};
    }
    if (local_public_key_ == public_key) {
        return Status{ErrorCode::protocol_error,
                      "friend session public key equals the local Tox public key"};
    }
    Entry &entry = entries_[friend_number];
    if (!entry.snapshot.public_key.empty() &&
        entry.snapshot.public_key != public_key) {
        return Status{
            ErrorCode::protocol_error,
            "transport friend number changed public key without removal"};
    }
    entry.snapshot.friend_number = friend_number;
    entry.snapshot.public_key = public_key;
    entry.snapshot.local_public_key = local_public_key_;
    entry.snapshot.connection_status = connection_status;
    entry.snapshot.updated_unix_ms = now_unix_ms;
    if (entry.snapshot.connected) {
        return entry.snapshot;
    }

    const std::uint64_t next_epoch = entry.snapshot.online_epoch + 1U;
    SessionNonce local_nonce = nonce;
    if ((supported_features_ & feature_bit(
             Feature::application_epoch_restart_v1)) != 0U) {
        if (local_incarnation_ == 0U) {
            return Status{
                ErrorCode::unavailable,
                "application-epoch restart was advertised without a local "
                "incarnation"};
        }
        if (next_epoch >
            static_cast<std::uint64_t>(
                std::numeric_limits<std::uint32_t>::max())) {
            return Status{
                ErrorCode::resource_exhausted,
                "local application connection epoch is exhausted"};
        }
        local_nonce = bind_session_generation(
            local_nonce, local_incarnation_,
            static_cast<std::uint32_t>(next_epoch));
    }
    auto local_key = parse_public_key(local_public_key_);
    auto peer_key = parse_public_key(public_key);
    if (!local_key || !peer_key) {
        return Status{ErrorCode::internal_error,
                      "validated session public key could not be decoded"};
    }

    Entry fresh_entry;
    entry = std::move(fresh_entry);
    entry.snapshot.friend_number = friend_number;
    entry.snapshot.public_key = std::move(public_key);
    entry.snapshot.local_public_key = local_public_key_;
    entry.snapshot.connection_status = connection_status;
    entry.snapshot.state = PeerSessionState::awaiting_hello;
    entry.snapshot.connected = true;
    entry.snapshot.local_role_known = true;
    entry.snapshot.local_role = key_less(local_key.value(), peer_key.value())
        ? SessionRole::lower_transport_key
        : SessionRole::higher_transport_key;
    entry.snapshot.online_epoch = next_epoch;
    entry.snapshot.updated_unix_ms = now_unix_ms;
    entry.snapshot.local = make_local_hello(
        maximum_finite_file_bytes_, local_nonce, supported_features_);
    update_progress(entry.snapshot);
    return entry.snapshot;
}

Status PeerSessionRegistry::peer_offline(std::uint32_t friend_number,
                                         std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "cannot mark an unknown peer session offline"};
    }
    Entry &entry = found->second;
    const std::uint64_t epoch = entry.snapshot.online_epoch;
    const std::string key = entry.snapshot.public_key;
    Entry fresh_entry;
    entry = std::move(fresh_entry);
    entry.snapshot.friend_number = friend_number;
    entry.snapshot.public_key = key;
    entry.snapshot.local_public_key = local_public_key_;
    entry.snapshot.online_epoch = epoch;
    entry.snapshot.updated_unix_ms = now_unix_ms;
    update_progress(entry.snapshot);
    return Status::success();
}

void PeerSessionRegistry::erase(std::uint32_t friend_number) {
    std::scoped_lock lock(mutex_);
    entries_.erase(friend_number);
}

Result<Frame> PeerSessionRegistry::make_hello_frame(
    std::uint32_t friend_number, std::uint64_t message_id) {
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "HELLO message identifier zero is reserved"};
    }
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "cannot create HELLO for an offline or unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    if (snapshot.local_hello_message_id != 0U &&
        snapshot.local_hello_message_id != message_id) {
        return Status{ErrorCode::protocol_error,
                      "HELLO retry must reuse the first message identifier for "
                      "this online epoch"};
    }
    auto payload = encode_hello_payload(snapshot.local);
    if (!payload) {
        return payload.status();
    }
    // Reserve the logical record before the caller attempts toxcore enqueue.
    // A SENDQ/offline rejection must not permit a new message id on retry.
    if (snapshot.local_hello_message_id == 0U) {
        snapshot.local_hello_message_id = message_id;
    }
    Frame frame;
    frame.major = kHelloFrameMajor;
    frame.minor = kHelloFrameMinor;
    frame.type = MessageType::hello;
    frame.message_id = snapshot.local_hello_message_id;
    frame.sequence = 1U;
    frame.payload = std::move(payload).value();
    return frame;
}

Status PeerSessionRegistry::mark_hello_sent(
    std::uint32_t friend_number, std::uint64_t message_id,
    std::uint64_t now_unix_ms) {
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "HELLO message identifier zero is reserved"};
    }
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "cannot mark HELLO sent for an offline or unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    if (snapshot.local_hello_message_id != 0U &&
        snapshot.local_hello_message_id != message_id) {
        return Status{
            ErrorCode::protocol_error,
            "HELLO retry changed the first message identifier for this "
            "online epoch"};
    }
    ++snapshot.hello_send_attempts;
    snapshot.hello_sent = true;
    if (snapshot.local_hello_message_id == 0U) {
        snapshot.local_hello_message_id = message_id;
    }
    snapshot.updated_unix_ms = now_unix_ms;
    snapshot.last_hello_send_error_code = ErrorCode::ok;
    snapshot.last_hello_send_error.clear();
    update_progress(snapshot);
    return Status::success();
}

Status PeerSessionRegistry::mark_hello_send_failed(
    std::uint32_t friend_number, ErrorCode error_code,
    std::string error, std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "cannot mark HELLO failure for an offline or unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    ++snapshot.hello_send_attempts;
    snapshot.updated_unix_ms = now_unix_ms;
    snapshot.last_hello_send_error_code = error_code;
    snapshot.last_hello_send_error = std::move(error);
    if (!snapshot.hello_sent) {
        snapshot.state = PeerSessionState::hello_send_failed;
        snapshot.application_ready = false;
        snapshot.detail = "canonical HELLO could not be queued to toxcore";
    }
    return Status::success();
}

Status PeerSessionRegistry::mark_malformed_frame(
    std::uint32_t friend_number, std::string error,
    std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "cannot record a malformed frame for an unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    snapshot.state = PeerSessionState::malformed_frame;
    snapshot.application_ready = false;
    snapshot.updated_unix_ms = now_unix_ms;
    snapshot.detail = std::move(error);
    return Status::success();
}

Status PeerSessionRegistry::mark_malformed_hello(
    std::uint32_t friend_number, std::string error,
    std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "cannot record malformed HELLO for an unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    snapshot.state = PeerSessionState::malformed_hello;
    snapshot.application_ready = false;
    snapshot.updated_unix_ms = now_unix_ms;
    snapshot.detail = std::move(error);
    return Status::success();
}

Status PeerSessionRegistry::receive_hello(
    std::uint32_t friend_number, std::string_view public_key,
    const Frame &frame, std::uint64_t now_unix_ms) {
    const Status valid_key = validate_public_key(public_key);
    if (!valid_key.ok()) {
        return valid_key;
    }
    const Status valid_frame = validate_hello_frame(frame);
    if (!valid_frame.ok()) {
        const Status marked = mark_malformed_hello(
            friend_number, "rejected HELLO: " + valid_frame.message(),
            now_unix_ms);
        return marked.ok() ? valid_frame : marked;
    }
    auto peer_hello = decode_hello_payload(frame.payload);
    if (!peer_hello) {
        return peer_hello.status();
    }

    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "HELLO arrived without an online peer session"};
    }
    Entry &entry = found->second;
    if (entry.snapshot.public_key != public_key) {
        return Status{ErrorCode::protocol_error,
                      "HELLO public key does not match the friend session"};
    }

    if (!entry.frozen_peer_hello_payload.empty()) {
        if (entry.frozen_peer_hello_payload != frame.payload) {
            const std::uint64_t restart_feature = feature_bit(
                Feature::application_epoch_restart_v1);
            const bool incumbent_restart_capable =
                (entry.snapshot.local.supported_features & restart_feature) !=
                    0U &&
                (entry.snapshot.peer.supported_features & restart_feature) !=
                    0U;
            const bool candidate_restart_capable =
                (peer_hello.value().supported_features & restart_feature) !=
                0U;
            if (incumbent_restart_capable && candidate_restart_capable) {
                const std::uint64_t incumbent_incarnation =
                    session_incarnation(
                        entry.snapshot.peer.session_nonce);
                const std::uint64_t candidate_incarnation =
                    session_incarnation(
                        peer_hello.value().session_nonce);
                const std::uint32_t incumbent_connection_epoch =
                    session_connection_epoch(
                        entry.snapshot.peer.session_nonce);
                const std::uint32_t candidate_connection_epoch =
                    session_connection_epoch(
                        peer_hello.value().session_nonce);
                const bool candidate_is_stale =
                    candidate_incarnation < incumbent_incarnation ||
                    (candidate_incarnation == incumbent_incarnation &&
                     candidate_connection_epoch <
                         incumbent_connection_epoch);
                const bool candidate_is_newer =
                    candidate_incarnation > incumbent_incarnation ||
                    (candidate_incarnation == incumbent_incarnation &&
                     candidate_connection_epoch >
                         incumbent_connection_epoch);
                if (candidate_is_stale) {
                    entry.snapshot.updated_unix_ms = now_unix_ms;
                    return Status{
                        ErrorCode::protocol_error,
                        "stale application-epoch HELLO generation was ignored"};
                }
                if (candidate_is_newer) {
                    if (entry.snapshot.online_epoch ==
                        std::numeric_limits<std::uint64_t>::max()) {
                        return Status{
                            ErrorCode::resource_exhausted,
                            "peer application online-epoch counter is exhausted"};
                    }
                    const PeerSessionSnapshot previous = entry.snapshot;
                    PeerSessionSnapshot restarted;
                    restarted.friend_number = previous.friend_number;
                    restarted.public_key = previous.public_key;
                    restarted.local_public_key = previous.local_public_key;
                    restarted.connection_status =
                        previous.connection_status;
                    restarted.state = PeerSessionState::awaiting_hello;
                    restarted.connected = true;
                    // The canonical local HELLO bytes and message identifier
                    // remain frozen to the continuous transport epoch, but a
                    // fresh enqueue is required before confirming the new
                    // application epoch. A transient enqueue failure can then
                    // follow the ordinary exact-record retry path.
                    restarted.hello_sent = false;
                    restarted.hello_received = true;
                    restarted.local_role_known =
                        previous.local_role_known;
                    restarted.local_role = previous.local_role;
                    restarted.online_epoch = previous.online_epoch + 1U;
                    restarted.local_hello_message_id =
                        previous.local_hello_message_id;
                    restarted.peer_hello_message_id = frame.message_id;
                    restarted.updated_unix_ms = now_unix_ms;
                    restarted.local = previous.local;
                    restarted.peer = peer_hello.value();
                    restarted.negotiated = negotiate_protocol(
                        restarted.local, restarted.peer);
                    entry.snapshot = std::move(restarted);
                    entry.frozen_peer_hello_payload = frame.payload;
                    entry.frozen_peer_confirmation_payload.clear();
                    update_progress(entry.snapshot);
                    return entry.snapshot.negotiated.compatible
                               ? Status::success()
                               : Status{
                                     ErrorCode::unsupported,
                                     entry.snapshot.negotiated.detail};
                }
            }
            entry.snapshot.state = PeerSessionState::conflicting_hello;
            entry.snapshot.application_ready = false;
            entry.snapshot.updated_unix_ms = now_unix_ms;
            entry.snapshot.detail =
                "peer changed its canonical HELLO within one online epoch";
            return Status{ErrorCode::protocol_error,
                          entry.snapshot.detail};
        }
        entry.snapshot.updated_unix_ms = now_unix_ms;
        // An exact retransmission is idempotent, but it cannot transform a
        // previously incompatible HELLO into a successful negotiation. Keep
        // the first semantic result as well as the first canonical bytes.
        return entry.snapshot.negotiated.compatible
                   ? Status::success()
                   : Status{ErrorCode::unsupported,
                            entry.snapshot.negotiated.detail};
    }

    entry.frozen_peer_hello_payload = frame.payload;
    entry.snapshot.hello_received = true;
    entry.snapshot.peer_hello_message_id = frame.message_id;
    entry.snapshot.peer = peer_hello.value();
    entry.snapshot.negotiated =
        negotiate_protocol(entry.snapshot.local, entry.snapshot.peer);
    entry.snapshot.updated_unix_ms = now_unix_ms;
    update_progress(entry.snapshot);
    return entry.snapshot.negotiated.compatible
               ? Status::success()
               : Status{ErrorCode::unsupported,
                        entry.snapshot.negotiated.detail};
}

Result<Frame> PeerSessionRegistry::make_confirmation_frame(
    std::uint32_t friend_number, std::uint64_t message_id) {
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "confirmation message identifier zero is reserved"};
    }
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "cannot create confirmation for an offline or unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    if (snapshot.local_confirmation_message_id != 0U &&
        snapshot.local_confirmation_message_id != message_id) {
        return Status{
            ErrorCode::protocol_error,
            "confirmation retry must reuse the first message identifier "
            "for this online epoch"};
    }
    if (!snapshot.hello_sent || !snapshot.hello_received ||
        !snapshot.negotiated.compatible ||
        snapshot.peer_hello_message_id == 0U) {
        return Status{ErrorCode::unavailable,
                      "confirmation requires a complete compatible HELLO exchange"};
    }
    auto confirmation = make_confirmation_payload(
        local_public_key_, snapshot.public_key,
        snapshot.local, snapshot.peer);
    if (!confirmation) {
        return confirmation.status();
    }
    auto payload = encode_confirmation_payload(confirmation.value());
    if (!payload) {
        return payload.status();
    }

    // Reserve the confirmation id before the transport call for the same
    // reason as HELLO: only an exact unsent record may cross a transient retry.
    if (snapshot.local_confirmation_message_id == 0U) {
        snapshot.local_confirmation_message_id = message_id;
    }
    Frame frame;
    frame.major = snapshot.negotiated.selected.major;
    frame.minor = snapshot.negotiated.selected.minor;
    frame.type = MessageType::capabilities;
    frame.message_id = snapshot.local_confirmation_message_id;
    frame.correlation_id = snapshot.peer_hello_message_id;
    frame.sequence = 2U;
    frame.payload = std::move(payload).value();
    return frame;
}

Status PeerSessionRegistry::mark_confirmation_sent(
    std::uint32_t friend_number, std::uint64_t message_id,
    std::uint64_t now_unix_ms) {
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "confirmation message identifier zero is reserved"};
    }
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "cannot mark confirmation sent for an offline or unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    if (snapshot.local_confirmation_message_id != 0U &&
        snapshot.local_confirmation_message_id != message_id) {
        return Status{
            ErrorCode::protocol_error,
            "confirmation retry changed the first message identifier for "
            "this online epoch"};
    }
    if (!snapshot.hello_sent || !snapshot.hello_received ||
        !snapshot.negotiated.compatible) {
        return Status{ErrorCode::unavailable,
                      "cannot mark confirmation before compatible HELLO exchange"};
    }
    ++snapshot.confirmation_send_attempts;
    snapshot.confirmation_sent = true;
    if (snapshot.local_confirmation_message_id == 0U) {
        snapshot.local_confirmation_message_id = message_id;
    }
    snapshot.updated_unix_ms = now_unix_ms;
    snapshot.last_confirmation_send_error_code = ErrorCode::ok;
    snapshot.last_confirmation_send_error.clear();
    update_progress(snapshot);
    return Status::success();
}

Status PeerSessionRegistry::mark_confirmation_send_failed(
    std::uint32_t friend_number, ErrorCode error_code,
    std::string error, std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "cannot mark confirmation failure for an offline or unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    ++snapshot.confirmation_send_attempts;
    snapshot.updated_unix_ms = now_unix_ms;
    snapshot.last_confirmation_send_error_code = error_code;
    snapshot.last_confirmation_send_error = std::move(error);
    if (!snapshot.confirmation_sent) {
        snapshot.state = PeerSessionState::confirmation_send_failed;
        snapshot.application_ready = false;
        snapshot.detail =
            "transcript confirmation could not be queued to toxcore";
    }
    return Status::success();
}

Status PeerSessionRegistry::mark_malformed_confirmation(
    std::uint32_t friend_number, std::string error,
    std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "cannot record malformed confirmation for an unknown peer"};
    }
    PeerSessionSnapshot &snapshot = found->second.snapshot;
    snapshot.state = PeerSessionState::malformed_confirmation;
    snapshot.application_ready = false;
    snapshot.updated_unix_ms = now_unix_ms;
    snapshot.detail = std::move(error);
    return Status::success();
}

Status PeerSessionRegistry::receive_confirmation(
    std::uint32_t friend_number, std::string_view public_key,
    const Frame &frame, std::uint64_t now_unix_ms) {
    const Status valid_key = validate_public_key(public_key);
    if (!valid_key.ok()) {
        return valid_key;
    }
    const Status valid_frame = validate_confirmation_frame(frame);
    if (!valid_frame.ok()) {
        const Status marked = mark_malformed_confirmation(
            friend_number,
            "rejected CAPABILITIES confirmation: " + valid_frame.message(),
            now_unix_ms);
        return marked.ok() ? valid_frame : marked;
    }

    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || !found->second.snapshot.connected) {
        return Status{ErrorCode::unavailable,
                      "confirmation arrived without an online peer session"};
    }
    Entry &entry = found->second;
    PeerSessionSnapshot &snapshot = entry.snapshot;
    if (snapshot.public_key != public_key) {
        return Status{ErrorCode::protocol_error,
                      "confirmation public key does not match the friend session"};
    }
    if (!snapshot.hello_sent || !snapshot.hello_received ||
        !snapshot.negotiated.compatible ||
        snapshot.local_hello_message_id == 0U) {
        snapshot.state = PeerSessionState::malformed_confirmation;
        snapshot.application_ready = false;
        snapshot.updated_unix_ms = now_unix_ms;
        snapshot.detail =
            "peer confirmation arrived before the compatible HELLO "
            "exchange completed";
        return Status{ErrorCode::protocol_error, snapshot.detail};
    }
    if (frame.correlation_id != snapshot.local_hello_message_id) {
        snapshot.state = PeerSessionState::malformed_confirmation;
        snapshot.application_ready = false;
        snapshot.updated_unix_ms = now_unix_ms;
        snapshot.detail = "peer confirmation does not correlate to the first "
                          "accepted local HELLO";
        return Status{ErrorCode::protocol_error, snapshot.detail};
    }

    auto expected_confirmation = make_confirmation_payload(
        snapshot.public_key, local_public_key_,
        snapshot.peer, snapshot.local);
    if (!expected_confirmation) {
        snapshot.state = PeerSessionState::malformed_confirmation;
        snapshot.application_ready = false;
        snapshot.updated_unix_ms = now_unix_ms;
        snapshot.detail = "unable to construct the expected peer confirmation: " +
                          expected_confirmation.status().message();
        return Status{ErrorCode::protocol_error, snapshot.detail};
    }
    auto expected_payload =
        encode_confirmation_payload(expected_confirmation.value());
    if (!expected_payload) {
        snapshot.state = PeerSessionState::malformed_confirmation;
        snapshot.application_ready = false;
        snapshot.updated_unix_ms = now_unix_ms;
        snapshot.detail = "unable to encode the expected peer confirmation: " +
                          expected_payload.status().message();
        return Status{ErrorCode::protocol_error, snapshot.detail};
    }

    if (!entry.frozen_peer_confirmation_payload.empty()) {
        if (entry.frozen_peer_confirmation_payload != frame.payload) {
            snapshot.state = PeerSessionState::conflicting_confirmation;
            snapshot.application_ready = false;
            snapshot.updated_unix_ms = now_unix_ms;
            snapshot.detail =
                "peer changed its canonical confirmation within one online epoch";
            return Status{ErrorCode::protocol_error, snapshot.detail};
        }
        snapshot.updated_unix_ms = now_unix_ms;
        // Only a confirmation that passed the local transcript comparison is
        // an idempotent success. Repeating the exact bytes of a confirmation
        // that was frozen and rejected must remain a rejection.
        if (snapshot.confirmation_received &&
            snapshot.state != PeerSessionState::conflicting_confirmation) {
            return Status::success();
        }
        return Status{
            ErrorCode::protocol_error,
            snapshot.detail.empty()
                ? "frozen peer confirmation was not accepted for this online epoch"
                : snapshot.detail};
    }
    // Freeze the first structurally valid confirmation for this online epoch
    // before comparing it with our reconstruction. A peer cannot probe with a
    // mismatching transcript and then replace it with a corrected one without
    // disconnecting and creating a fresh epoch.
    entry.frozen_peer_confirmation_payload = frame.payload;
    if (frame.payload != expected_payload.value()) {
        snapshot.state = PeerSessionState::malformed_confirmation;
        snapshot.application_ready = false;
        snapshot.updated_unix_ms = now_unix_ms;
        snapshot.detail =
            "peer confirmation does not equal the locally reconstructed transcript";
        return Status{ErrorCode::protocol_error, snapshot.detail};
    }

    snapshot.confirmation_received = true;
    snapshot.peer_confirmation_message_id = frame.message_id;
    snapshot.updated_unix_ms = now_unix_ms;
    update_progress(snapshot);
    return Status::success();
}

Result<PeerSessionSnapshot> PeerSessionRegistry::get(
    std::uint32_t friend_number) const {
    std::scoped_lock lock(mutex_);
    const auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "peer protocol session does not exist"};
    }
    return found->second.snapshot;
}

std::vector<PeerSessionSnapshot> PeerSessionRegistry::list() const {
    std::scoped_lock lock(mutex_);
    std::vector<PeerSessionSnapshot> output;
    output.reserve(entries_.size());
    for (const auto &[friend_number, entry] : entries_) {
        static_cast<void>(friend_number);
        output.push_back(entry.snapshot);
    }
    std::sort(output.begin(), output.end(),
              [](const PeerSessionSnapshot &left,
                 const PeerSessionSnapshot &right) {
                  return left.friend_number < right.friend_number;
              });
    return output;
}

std::string render_session_snapshot(const PeerSessionSnapshot &snapshot) {
    std::ostringstream output;
    output << "friend-number=" << snapshot.friend_number << '\n'
           << "public-key=" << snapshot.public_key << '\n'
           << "local-public-key=" << snapshot.local_public_key << '\n'
           << "connection-status=" << snapshot.connection_status << '\n'
           << "connected=" << (snapshot.connected ? 1 : 0) << '\n'
           << "state=" << to_string(snapshot.state) << '\n'
           << "application-ready=" << (is_application_ready(snapshot) ? 1 : 0)
           << '\n'
           << "online-epoch=" << snapshot.online_epoch << '\n'
           << "local-role="
           << (snapshot.local_role_known
                   ? to_string(snapshot.local_role)
                   : std::string("unknown"))
           << '\n'
           << "hello-sent=" << (snapshot.hello_sent ? 1 : 0) << '\n'
           << "hello-received=" << (snapshot.hello_received ? 1 : 0) << '\n'
           << "hello-send-attempts=" << snapshot.hello_send_attempts << '\n'
           << "confirmation-sent=" << (snapshot.confirmation_sent ? 1 : 0)
           << '\n'
           << "confirmation-received="
           << (snapshot.confirmation_received ? 1 : 0) << '\n'
           << "confirmation-send-attempts="
           << snapshot.confirmation_send_attempts << '\n'
           << "local-hello-message-id=" << snapshot.local_hello_message_id << '\n'
           << "peer-hello-message-id=" << snapshot.peer_hello_message_id << '\n'
           << "local-confirmation-message-id="
           << snapshot.local_confirmation_message_id << '\n'
           << "peer-confirmation-message-id="
           << snapshot.peer_confirmation_message_id << '\n'
           << "updated-unix-ms=" << snapshot.updated_unix_ms << '\n'
           << "compatible=" << (snapshot.negotiated.compatible ? 1 : 0) << '\n'
           << "negotiation-failure="
           << to_string(snapshot.negotiated.failure) << '\n'
           << "selected-protocol=";
    if (snapshot.negotiated.compatible) {
        output << static_cast<unsigned int>(snapshot.negotiated.selected.major)
               << '.'
               << static_cast<unsigned int>(snapshot.negotiated.selected.minor);
    } else {
        output << "none";
    }
    output << '\n'
           << "local-supported-features="
           << render_feature_mask(snapshot.local.supported_features) << '\n'
           << "local-required-features="
           << render_feature_mask(snapshot.local.required_features) << '\n'
           << "peer-supported-features="
           << render_feature_mask(snapshot.peer.supported_features) << '\n'
           << "peer-required-features="
           << render_feature_mask(snapshot.peer.required_features) << '\n'
           << "shared-features="
           << render_feature_mask(snapshot.negotiated.shared_features) << '\n'
           << "maximum-frame-payload-size="
           << snapshot.negotiated.maximum_frame_payload_size << '\n'
           << "maximum-finite-file-bytes="
           << snapshot.negotiated.maximum_finite_file_bytes << '\n'
           << "local-implementation="
           << snapshot.local.implementation_major << '.'
           << snapshot.local.implementation_minor << '.'
           << snapshot.local.implementation_patch << " rev"
           << snapshot.local.build_revision << '\n'
           << "local-session-nonce="
           << nonce_hex(snapshot.local.session_nonce) << '\n'
           << "peer-implementation="
           << snapshot.peer.implementation_major << '.'
           << snapshot.peer.implementation_minor << '.'
           << snapshot.peer.implementation_patch << " rev"
           << snapshot.peer.build_revision << '\n'
           << "peer-session-nonce="
           << nonce_hex(snapshot.peer.session_nonce) << '\n'
           << "authorization=separate-authority-session\n"
           << "detail=" << snapshot.detail << '\n';
    if (!snapshot.last_hello_send_error.empty()) {
        output << "last-hello-send-error-code="
               << error_code_text(snapshot.last_hello_send_error_code) << '\n'
               << "last-hello-send-error="
               << snapshot.last_hello_send_error << '\n';
    }
    if (!snapshot.last_confirmation_send_error.empty()) {
        output << "last-confirmation-send-error-code="
               << error_code_text(snapshot.last_confirmation_send_error_code) << '\n'
               << "last-confirmation-send-error="
               << snapshot.last_confirmation_send_error << '\n';
    }
    return output.str();
}

}  // namespace iotox::protocol
