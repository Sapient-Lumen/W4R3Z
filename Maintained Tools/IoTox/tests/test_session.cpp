#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/security/random.hpp"
#include "iotox/version.hpp"
#include "test_harness.hpp"

#include <algorithm>
#include <array>
#include <charconv>
#include <cstdint>
#include <limits>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace {

iotox::protocol::SessionNonce nonce(std::uint8_t seed) {
    iotox::protocol::SessionNonce output{};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        output[index] = static_cast<std::uint8_t>(seed + index);
    }
    return output;
}

std::string public_key(char digit) { return std::string(64U, digit); }

[[nodiscard]] std::optional<std::array<std::uint16_t, 3U>>
parse_semantic_version(std::string_view text) {
    std::array<std::uint16_t, 3U> components{};
    std::size_t offset = 0U;
    for (std::size_t index = 0U; index < components.size(); ++index) {
        const std::size_t separator = text.find('.', offset);
        const std::size_t end = separator == std::string_view::npos
                                    ? text.size()
                                    : separator;
        if (end == offset) return std::nullopt;
        unsigned int value = 0U;
        const auto parsed = std::from_chars(
            text.data() + offset, text.data() + end, value);
        if (parsed.ec != std::errc{} || parsed.ptr != text.data() + end ||
            value > std::numeric_limits<std::uint16_t>::max()) {
            return std::nullopt;
        }
        components[index] = static_cast<std::uint16_t>(value);
        if (index + 1U < components.size()) {
            if (separator == std::string_view::npos) return std::nullopt;
            offset = separator + 1U;
        } else if (separator != std::string_view::npos) {
            return std::nullopt;
        }
    }
    return components;
}

[[nodiscard]] std::optional<std::uint16_t> parse_revision_number(
    std::string_view text) {
    constexpr std::string_view prefix = "rev";
    if (!text.starts_with(prefix) || text.size() == prefix.size()) {
        return std::nullopt;
    }
    unsigned int value = 0U;
    const auto parsed = std::from_chars(
        text.data() + prefix.size(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size() ||
        value > std::numeric_limits<std::uint16_t>::max()) {
        return std::nullopt;
    }
    return static_cast<std::uint16_t>(value);
}

iotox::protocol::Frame hello_frame(
    const iotox::protocol::HelloPayload &hello, std::uint64_t message_id) {
    auto payload = iotox::protocol::encode_hello_payload(hello);
    IOTOX_CHECK(payload);
    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::hello;
    frame.message_id = message_id;
    frame.sequence = 1U;
    frame.payload = std::move(payload).value();
    return frame;
}

iotox::protocol::Frame confirmation_frame(
    const std::string &sender_key,
    const std::string &other_key,
    const iotox::protocol::HelloPayload &sender_hello,
    const iotox::protocol::HelloPayload &other_hello,
    std::uint64_t message_id,
    std::uint64_t correlation_id) {
    auto confirmation = iotox::protocol::make_confirmation_payload(
        sender_key, other_key, sender_hello, other_hello);
    IOTOX_CHECK(confirmation);
    auto payload = iotox::protocol::encode_confirmation_payload(
        confirmation.value());
    IOTOX_CHECK(payload);
    iotox::protocol::Frame frame;
    frame.major = confirmation.value().negotiated.selected.major;
    frame.minor = confirmation.value().negotiated.selected.minor;
    frame.type = iotox::protocol::MessageType::capabilities;
    frame.message_id = message_id;
    frame.correlation_id = correlation_id;
    frame.sequence = 2U;
    frame.payload = std::move(payload).value();
    return frame;
}

}  // namespace

IOTOX_TEST("compiled identity keeps textual and protocol numerics coherent") {
    const auto version = parse_semantic_version(iotox::kVersion);
    IOTOX_CHECK(version.has_value());
    IOTOX_CHECK((*version)[0U] == iotox::kVersionMajor);
    IOTOX_CHECK((*version)[1U] == iotox::kVersionMinor);
    IOTOX_CHECK((*version)[2U] == iotox::kVersionPatch);

    const auto revision = parse_revision_number(iotox::kRevision);
    IOTOX_CHECK(revision.has_value());
    IOTOX_CHECK(*revision == iotox::kRevisionNumber);

    const auto hello =
        iotox::protocol::make_local_hello(1024U * 1024U, nonce(0U));
    IOTOX_CHECK(hello.implementation_major == iotox::kVersionMajor);
    IOTOX_CHECK(hello.implementation_minor == iotox::kVersionMinor);
    IOTOX_CHECK(hello.implementation_patch == iotox::kVersionPatch);
    IOTOX_CHECK(hello.build_revision == iotox::kRevisionNumber);
}

IOTOX_TEST("canonical IoTox HELLO has one exact bounded representation") {
    const auto original =
        iotox::protocol::make_local_hello(1024U * 1024U, nonce(1U));
    auto encoded = iotox::protocol::encode_hello_payload(original);
    IOTOX_CHECK(encoded);
    IOTOX_CHECK(encoded.value().size() ==
                iotox::protocol::kHelloPayloadSize);

    auto decoded = iotox::protocol::decode_hello_payload(encoded.value());
    IOTOX_CHECK(decoded);
    IOTOX_CHECK(decoded.value() == original);

    auto noncanonical = encoded.value();
    noncanonical.back() = 1U;
    IOTOX_CHECK(!iotox::protocol::decode_hello_payload(noncanonical));

    noncanonical = encoded.value();
    noncanonical.resize(noncanonical.size() - 1U);
    IOTOX_CHECK(!iotox::protocol::decode_hello_payload(noncanonical));
}

IOTOX_TEST("canonical HELLO rejects every assigned structural ambiguity") {
    const auto hello = iotox::protocol::make_local_hello(4096U, nonce(3U));
    auto encoded_result = iotox::protocol::encode_hello_payload(hello);
    IOTOX_CHECK(encoded_result);
    const auto encoded = encoded_result.value();

    const auto rejected = [&encoded](std::size_t offset, std::uint8_t value) {
        auto malformed = encoded;
        malformed[offset] = value;
        return !iotox::protocol::decode_hello_payload(malformed).ok();
    };
    IOTOX_CHECK(rejected(0U, 'X'));   // magic
    IOTOX_CHECK(rejected(4U, 2U));    // payload version
    IOTOX_CHECK(rejected(5U, 1U));    // flags
    IOTOX_CHECK(rejected(60U, 1U));   // reserved

    auto reversed = hello;
    reversed.minimum_protocol = {2U, 0U};
    reversed.maximum_protocol = {1U, 0U};
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(reversed));

    auto impossible_frame = hello;
    impossible_frame.maximum_frame_payload_size =
        static_cast<std::uint16_t>(
            iotox::protocol::kConfirmationPayloadSize - 1U);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(impossible_frame));

    auto unsupported_requirement = hello;
    unsupported_requirement.required_features |=
        iotox::protocol::feature_bit(
            iotox::protocol::Feature::state_sync_v1);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(
        unsupported_requirement));

    auto missing_session_requirement = hello;
    missing_session_requirement.required_features = 0U;
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(
        missing_session_requirement));

    auto inconsistent_file_feature = hello;
    inconsistent_file_feature.supported_features &=
        ~iotox::protocol::feature_bit(
            iotox::protocol::Feature::finite_file_transfer_v1);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(
        inconsistent_file_feature));

    auto zero_nonce = hello;
    zero_nonce.session_nonce.fill(0U);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(zero_nonce));

    auto orphan_v3 = hello;
    orphan_v3.supported_features &= ~iotox::protocol::feature_bit(
        iotox::protocol::Feature::authorization_ledger_v2);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(orphan_v3));

    auto orphan_ranges = hello;
    orphan_ranges.supported_features |= iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_ranges_v1);
    orphan_ranges.supported_features &= ~iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_v1);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(orphan_ranges));

    auto orphan_content = hello;
    orphan_content.supported_features |= iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_content_v2);
    orphan_content.supported_features &= ~iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_v1);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(orphan_content));
    orphan_content.supported_features |= iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_v1);
    IOTOX_CHECK(iotox::protocol::encode_hello_payload(orphan_content));

    auto orphan_tree = hello;
    orphan_tree.supported_features |= iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_tree_v2);
    orphan_tree.supported_features &=
        ~iotox::protocol::feature_bit(iotox::protocol::Feature::state_sync_v1);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(orphan_tree));
    orphan_tree.supported_features |=
        iotox::protocol::feature_bit(iotox::protocol::Feature::state_sync_v1);
    IOTOX_CHECK(iotox::protocol::encode_hello_payload(orphan_tree));

    auto orphan_checkpoint = hello;
    orphan_checkpoint.supported_features |= iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_tree_checkpoint_v2);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(orphan_checkpoint));
    orphan_checkpoint.supported_features |=
        iotox::protocol::feature_bit(iotox::protocol::Feature::state_sync_v1) |
        iotox::protocol::feature_bit(
            iotox::protocol::Feature::state_sync_tree_v2);
    IOTOX_CHECK(iotox::protocol::encode_hello_payload(orphan_checkpoint));

    auto orphan_ota = hello;
    orphan_ota.supported_features |= iotox::protocol::feature_bit(
        iotox::protocol::Feature::signed_ota_v1);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(orphan_ota));

    auto complete_ota = hello;
    complete_ota.supported_features |=
        iotox::protocol::feature_bit(
            iotox::protocol::Feature::state_sync_v1) |
        iotox::protocol::feature_bit(
            iotox::protocol::Feature::state_sync_ranges_v1) |
        iotox::protocol::feature_bit(
            iotox::protocol::Feature::signed_ota_v1);
    IOTOX_CHECK(iotox::protocol::encode_hello_payload(complete_ota));

    auto orphan_private_routes = hello;
    orphan_private_routes.supported_features |=
        iotox::protocol::feature_bit(
            iotox::protocol::Feature::private_route_binding_v2);
    IOTOX_CHECK(!iotox::protocol::encode_hello_payload(
        orphan_private_routes));
    orphan_private_routes.supported_features |=
        iotox::protocol::feature_bit(
            iotox::protocol::Feature::route_binding_v1);
    IOTOX_CHECK(iotox::protocol::encode_hello_payload(
        orphan_private_routes));

    auto frame = hello_frame(hello, 77U);
    IOTOX_CHECK(iotox::protocol::validate_hello_frame(frame).ok());
    frame.flags = 1U;
    IOTOX_CHECK(!iotox::protocol::validate_hello_frame(frame).ok());
    frame.flags = 0U;
    frame.correlation_id = 1U;
    IOTOX_CHECK(!iotox::protocol::validate_hello_frame(frame).ok());
    frame.correlation_id = 0U;
    frame.sequence = 2U;
    IOTOX_CHECK(!iotox::protocol::validate_hello_frame(frame).ok());
    frame.sequence = 1U;
    frame.expiry_unix_ms = 1U;
    IOTOX_CHECK(!iotox::protocol::validate_hello_frame(frame).ok());
}

IOTOX_TEST("HELLO negotiation is symmetric and fails closed on requirements") {
    const std::uint64_t ratox_feature = iotox::protocol::feature_bit(
        iotox::protocol::Feature::ratox_interactive_v1);
    IOTOX_CHECK((iotox::protocol::kNamedFeatureMask & ratox_feature) != 0U);
    IOTOX_CHECK((iotox::protocol::kImplementedFeatureMask & ratox_feature) == 0U);
    auto local = iotox::protocol::make_local_hello(
        16U * 1024U, nonce(11U));
    auto peer = iotox::protocol::make_local_hello(
        8U * 1024U, nonce(31U));
    local.minimum_protocol = {1U, 0U};
    local.maximum_protocol = {1U, 4U};
    peer.minimum_protocol = {1U, 2U};
    peer.maximum_protocol = {1U, 3U};

    const auto compatible = iotox::protocol::negotiate_protocol(local, peer);
    const auto reverse = iotox::protocol::negotiate_protocol(peer, local);
    IOTOX_CHECK(compatible.compatible);
    IOTOX_CHECK(reverse.compatible);
    IOTOX_CHECK(compatible.selected == reverse.selected);
    const iotox::protocol::ProtocolVersion expected_version{1U, 3U};
    IOTOX_CHECK(compatible.selected == expected_version);
    IOTOX_CHECK(compatible.shared_features == reverse.shared_features);
    IOTOX_CHECK(compatible.maximum_frame_payload_size ==
                reverse.maximum_frame_payload_size);
    IOTOX_CHECK(compatible.maximum_finite_file_bytes == 8U * 1024U);

    // HELLOs may advertise extension bits that this build does not implement.
    // Requiring one is structurally valid, but negotiation must fail unless the
    // other endpoint advertises it too.
    const std::uint64_t future_feature = iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_v1);
    local.supported_features |= future_feature;
    local.required_features |= future_feature;
    const auto missing = iotox::protocol::negotiate_protocol(local, peer);
    IOTOX_CHECK(!missing.compatible);
    IOTOX_CHECK(
        missing.failure ==
        iotox::protocol::NegotiationFailure::local_required_feature_missing);

    local.supported_features &= ~future_feature;
    local.required_features &= ~future_feature;
    peer = iotox::protocol::make_local_hello(8U * 1024U, nonce(41U));
    peer.minimum_protocol = {2U, 0U};
    peer.maximum_protocol = {2U, 0U};
    const auto version = iotox::protocol::negotiate_protocol(local, peer);
    IOTOX_CHECK(!version.compatible);
    IOTOX_CHECK(
        version.failure ==
        iotox::protocol::NegotiationFailure::no_common_version);
}

IOTOX_TEST("CAPABILITIES canonically binds both keys HELLOs and negotiation") {
    const std::string lower_key = public_key('A');
    const std::string higher_key = public_key('B');
    auto lower_hello =
        iotox::protocol::make_local_hello(8192U, nonce(21U));
    auto higher_hello =
        iotox::protocol::make_local_hello(4096U, nonce(51U));

    auto higher_confirmation = iotox::protocol::make_confirmation_payload(
        higher_key, lower_key, higher_hello, lower_hello);
    IOTOX_CHECK(higher_confirmation);
    IOTOX_CHECK(
        higher_confirmation.value().sender_role ==
        iotox::protocol::SessionRole::higher_transport_key);
    IOTOX_CHECK(
        iotox::protocol::public_key_hex(
            higher_confirmation.value().lower_public_key) == lower_key);
    IOTOX_CHECK(
        iotox::protocol::public_key_hex(
            higher_confirmation.value().higher_public_key) == higher_key);
    IOTOX_CHECK(
        higher_confirmation.value().negotiated.maximum_finite_file_bytes ==
        4096U);

    auto encoded = iotox::protocol::encode_confirmation_payload(
        higher_confirmation.value());
    IOTOX_CHECK(encoded);
    IOTOX_CHECK(encoded.value().size() ==
                iotox::protocol::kConfirmationPayloadSize);
    auto decoded =
        iotox::protocol::decode_confirmation_payload(encoded.value());
    IOTOX_CHECK(decoded);
    IOTOX_CHECK(decoded.value() == higher_confirmation.value());

    auto lower_confirmation = iotox::protocol::make_confirmation_payload(
        lower_key, higher_key, lower_hello, higher_hello);
    IOTOX_CHECK(lower_confirmation);
    auto lower_encoded = iotox::protocol::encode_confirmation_payload(
        lower_confirmation.value());
    IOTOX_CHECK(lower_encoded);
    IOTOX_CHECK(lower_encoded.value().at(6U) == 0U);
    IOTOX_CHECK(encoded.value().at(6U) == 1U);
    auto without_role = encoded.value();
    without_role.at(6U) = 0U;
    IOTOX_CHECK(without_role == lower_encoded.value());

    const auto rejects_mutation = [&encoded](std::size_t offset,
                                              std::uint8_t value) {
        auto malformed = encoded.value();
        malformed.at(offset) ^= value;
        return !iotox::protocol::decode_confirmation_payload(malformed).ok();
    };
    IOTOX_CHECK(rejects_mutation(0U, 'X'));      // magic
    IOTOX_CHECK(rejects_mutation(4U, 2U));       // version
    IOTOX_CHECK(rejects_mutation(5U, 1U));       // flags
    IOTOX_CHECK(rejects_mutation(7U, 1U));       // reserved
    IOTOX_CHECK(rejects_mutation(8U, 2U));       // selected version
    IOTOX_CHECK(rejects_mutation(12U, 1U));      // negotiated features
    IOTOX_CHECK(rejects_mutation(124U, 'X'));    // lower HELLO magic
    IOTOX_CHECK(rejects_mutation(252U, 1U));     // tail reserved

    auto frame = confirmation_frame(
        higher_key, lower_key, higher_hello, lower_hello, 44U, 33U);
    IOTOX_CHECK(iotox::protocol::validate_confirmation_frame(frame).ok());
    frame.flags = 1U;
    IOTOX_CHECK(!iotox::protocol::validate_confirmation_frame(frame).ok());
    frame.flags = 0U;
    frame.correlation_id = 0U;
    IOTOX_CHECK(!iotox::protocol::validate_confirmation_frame(frame).ok());
    frame.correlation_id = 33U;
    frame.sequence = 3U;
    IOTOX_CHECK(!iotox::protocol::validate_confirmation_frame(frame).ok());
    frame.sequence = 2U;
    frame.major = 2U;
    IOTOX_CHECK(!iotox::protocol::validate_confirmation_frame(frame).ok());
}

IOTOX_TEST("peer session feature advertisement is explicit and immutable after "
           "admission") {
    const auto ratox = iotox::protocol::feature_bit(
        iotox::protocol::Feature::ratox_interactive_v1);
    const auto private_routes = iotox::protocol::feature_bit(
        iotox::protocol::Feature::private_route_binding_v2);
    const auto baseline = iotox::protocol::make_local_hello(4096U, nonce(7U));
    IOTOX_CHECK((baseline.supported_features & ratox) == 0U);
    IOTOX_CHECK((iotox::protocol::kNamedFeatureMask & private_routes) != 0U);
    IOTOX_CHECK((iotox::protocol::kImplementedFeatureMask & private_routes) ==
                0U);

    iotox::protocol::PeerSessionRegistry sessions(4096U);
    IOTOX_CHECK(sessions.set_supported_features(
                    iotox::protocol::kImplementedFeatureMask | ratox)
                    .ok());
    IOTOX_CHECK(sessions.set_local_public_key(public_key('B')).ok());
    IOTOX_CHECK(sessions.ensure_offline_peer(
                    77U, public_key('A'), 1U)
                    .ok());
    auto online = sessions.peer_online(
        77U, public_key('A'), 1, nonce(8U), 2U);
    IOTOX_CHECK(online);
    IOTOX_CHECK((online.value().local.supported_features & ratox) != 0U);
    IOTOX_CHECK(!sessions.set_supported_features(
                     iotox::protocol::kImplementedFeatureMask)
                     .ok());

    iotox::protocol::PeerSessionRegistry unnamed(4096U);
    IOTOX_CHECK(!unnamed.set_supported_features(1ULL << 63U).ok());
    iotox::protocol::PeerSessionRegistry missing_required(4096U);
    IOTOX_CHECK(!missing_required.set_supported_features(ratox).ok());
    iotox::protocol::PeerSessionRegistry orphan_v3(4096U);
    const auto v2 = iotox::protocol::feature_bit(
        iotox::protocol::Feature::authorization_ledger_v2);
    IOTOX_CHECK(!orphan_v3
                     .set_supported_features(
                         iotox::protocol::kImplementedFeatureMask & ~v2)
                     .ok());
    iotox::protocol::PeerSessionRegistry orphan_ranges(4096U);
    const auto ranges = iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_ranges_v1);
    IOTOX_CHECK(!orphan_ranges
                     .set_supported_features(
                         iotox::protocol::kImplementedFeatureMask | ranges)
                     .ok());
    const auto content = iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_content_v2);
    iotox::protocol::PeerSessionRegistry orphan_content(4096U);
    IOTOX_CHECK(!orphan_content
                     .set_supported_features(
                         iotox::protocol::kImplementedFeatureMask | content)
                     .ok());
    iotox::protocol::PeerSessionRegistry complete_content(4096U);
    IOTOX_CHECK(complete_content
                    .set_supported_features(
                        iotox::protocol::kImplementedFeatureMask |
                        iotox::protocol::feature_bit(
                            iotox::protocol::Feature::state_sync_v1) |
                        content)
                    .ok());
    const auto tree = iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_tree_v2);
    iotox::protocol::PeerSessionRegistry orphan_tree(4096U);
    IOTOX_CHECK(!orphan_tree
                     .set_supported_features(
                         iotox::protocol::kImplementedFeatureMask | tree)
                     .ok());
    iotox::protocol::PeerSessionRegistry complete_tree(4096U);
    IOTOX_CHECK(complete_tree
                    .set_supported_features(
                        iotox::protocol::kImplementedFeatureMask |
                        iotox::protocol::feature_bit(
                            iotox::protocol::Feature::state_sync_v1) |
                        tree)
                    .ok());
    const auto checkpoint = iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_tree_checkpoint_v2);
    iotox::protocol::PeerSessionRegistry orphan_checkpoint(4096U);
    IOTOX_CHECK(!orphan_checkpoint
                     .set_supported_features(
                         iotox::protocol::kImplementedFeatureMask |
                         checkpoint)
                     .ok());
    iotox::protocol::PeerSessionRegistry complete_checkpoint(4096U);
    IOTOX_CHECK(complete_checkpoint
                    .set_supported_features(
                        iotox::protocol::kImplementedFeatureMask |
                        iotox::protocol::feature_bit(
                            iotox::protocol::Feature::state_sync_v1) |
                        tree | checkpoint)
                    .ok());
    IOTOX_CHECK(iotox::protocol::render_feature_mask(checkpoint).find(
                    "state-sync-tree-checkpoint-v2") != std::string::npos);
    iotox::protocol::PeerSessionRegistry orphan_ota(4096U);
    const auto ota = iotox::protocol::feature_bit(
        iotox::protocol::Feature::signed_ota_v1);
    IOTOX_CHECK(!orphan_ota
                     .set_supported_features(
                         iotox::protocol::kImplementedFeatureMask | ota)
                     .ok());
    iotox::protocol::PeerSessionRegistry complete_ota(4096U);
    const auto sync = iotox::protocol::feature_bit(
        iotox::protocol::Feature::state_sync_v1);
    IOTOX_CHECK(complete_ota
                    .set_supported_features(
                        iotox::protocol::kImplementedFeatureMask | sync |
                        ranges | ota)
                    .ok());
    iotox::protocol::PeerSessionRegistry orphan_private_routes(4096U);
    IOTOX_CHECK(!orphan_private_routes
                     .set_supported_features(
                         iotox::protocol::kImplementedFeatureMask |
                         private_routes)
                     .ok());
    iotox::protocol::PeerSessionRegistry complete_private_routes(4096U);
    IOTOX_CHECK(complete_private_routes
                    .set_supported_features(
                        iotox::protocol::kImplementedFeatureMask |
                        iotox::protocol::feature_bit(
                            iotox::protocol::Feature::route_binding_v1) |
                        private_routes)
                    .ok());
}

IOTOX_TEST("peer session freezes and confirms one transcript per online epoch") {
    constexpr std::uint32_t friend_number = 7U;
    const std::string local_key = public_key('B');
    const std::string peer_key = public_key('A');
    iotox::protocol::PeerSessionRegistry sessions(4096U);

    IOTOX_CHECK(sessions.set_local_public_key(local_key).ok());
    IOTOX_CHECK(sessions.ensure_offline_peer(
                    friend_number, peer_key, 100U)
                    .ok());
    auto online = sessions.peer_online(
        friend_number, peer_key, 1, nonce(1U), 101U);
    IOTOX_CHECK(online);
    IOTOX_CHECK(online.value().state ==
                iotox::protocol::PeerSessionState::awaiting_hello);
    IOTOX_CHECK(online.value().online_epoch == 1U);
    IOTOX_CHECK(online.value().local_role ==
                iotox::protocol::SessionRole::higher_transport_key);

    auto local_frame = sessions.make_hello_frame(friend_number, 1001U);
    IOTOX_CHECK(local_frame);
    IOTOX_CHECK(
        iotox::protocol::validate_hello_frame(local_frame.value()).ok());
    IOTOX_CHECK(sessions.mark_hello_send_failed(
                    friend_number, iotox::ErrorCode::resource_exhausted,
                    "synthetic SENDQ", 102U)
                    .ok());
    auto failed_hello = sessions.get(friend_number);
    IOTOX_CHECK(failed_hello);
    IOTOX_CHECK(failed_hello.value().local_hello_message_id == 1001U);
    IOTOX_CHECK(failed_hello.value().hello_send_attempts == 1U);
    // The first constructed HELLO id is the correlation anchor even before a
    // successful enqueue. A retry cannot silently replace it after SENDQ.
    IOTOX_CHECK(!sessions.make_hello_frame(friend_number, 1002U).ok());
    auto local_hello_retry = sessions.make_hello_frame(friend_number, 1001U);
    IOTOX_CHECK(local_hello_retry);
    IOTOX_CHECK(local_hello_retry.value().message_id == 1001U);
    IOTOX_CHECK(
        sessions.mark_hello_sent(friend_number, 1001U, 103U).ok());
    IOTOX_CHECK(!sessions.mark_hello_sent(
                    friend_number, 1002U, 104U)
                    .ok());

    const auto peer_hello =
        iotox::protocol::make_local_hello(2048U, nonce(61U));
    const auto incoming = hello_frame(peer_hello, 2001U);
    IOTOX_CHECK(sessions.receive_hello(
                    friend_number, peer_key, incoming, 104U)
                    .ok());

    auto compatible = sessions.get(friend_number);
    IOTOX_CHECK(compatible);
    IOTOX_CHECK(compatible.value().state ==
                iotox::protocol::PeerSessionState::awaiting_confirmation);
    IOTOX_CHECK(compatible.value().hello_sent);
    IOTOX_CHECK(compatible.value().hello_received);
    IOTOX_CHECK(compatible.value().local_hello_message_id == 1001U);
    IOTOX_CHECK(
        compatible.value().negotiated.maximum_finite_file_bytes == 2048U);
    IOTOX_CHECK(!iotox::protocol::is_application_ready(compatible.value()));

    auto local_confirmation =
        sessions.make_confirmation_frame(friend_number, 3001U);
    IOTOX_CHECK(local_confirmation);
    IOTOX_CHECK(local_confirmation.value().correlation_id == 2001U);
    IOTOX_CHECK(sessions.mark_confirmation_send_failed(
                    friend_number, iotox::ErrorCode::resource_exhausted,
                    "synthetic SENDQ", 105U)
                    .ok());
    auto failed_confirmation = sessions.get(friend_number);
    IOTOX_CHECK(failed_confirmation);
    IOTOX_CHECK(
        failed_confirmation.value().local_confirmation_message_id == 3001U);
    IOTOX_CHECK(failed_confirmation.value().confirmation_send_attempts == 1U);
    IOTOX_CHECK(!sessions.make_confirmation_frame(
                    friend_number, 3002U)
                    .ok());
    auto confirmation_retry =
        sessions.make_confirmation_frame(friend_number, 3001U);
    IOTOX_CHECK(confirmation_retry);
    IOTOX_CHECK(confirmation_retry.value().message_id == 3001U);
    IOTOX_CHECK(sessions.mark_confirmation_sent(
                    friend_number, 3001U, 106U)
                    .ok());
    IOTOX_CHECK(!sessions.mark_confirmation_sent(
                    friend_number, 3002U, 106U)
                    .ok());

    const auto peer_confirmation = confirmation_frame(
        peer_key, local_key, peer_hello, compatible.value().local,
        4001U, 1001U);
    IOTOX_CHECK(sessions.receive_confirmation(
                    friend_number, peer_key, peer_confirmation, 106U)
                    .ok());
    auto established = sessions.get(friend_number);
    IOTOX_CHECK(established);
    IOTOX_CHECK(established.value().state ==
                iotox::protocol::PeerSessionState::confirmed);
    IOTOX_CHECK(iotox::protocol::is_application_ready(established.value()));
    IOTOX_CHECK(established.value().confirmation_sent);
    IOTOX_CHECK(established.value().confirmation_received);

    // Byte-identical retries are idempotent even when the outer message id is
    // fresh. The first peer confirmation remains the audit identifier.
    auto retry = peer_confirmation;
    retry.message_id = 4002U;
    IOTOX_CHECK(sessions.receive_confirmation(
                    friend_number, peer_key, retry, 107U)
                    .ok());
    auto after_retry = sessions.get(friend_number);
    IOTOX_CHECK(after_retry);
    IOTOX_CHECK(after_retry.value().peer_confirmation_message_id == 4001U);

    auto conflicting_confirmation = peer_confirmation;
    conflicting_confirmation.message_id = 4003U;
    conflicting_confirmation.payload[6U] = 1U;
    const auto confirmation_conflict = sessions.receive_confirmation(
        friend_number, peer_key, conflicting_confirmation, 108U);
    IOTOX_CHECK(!confirmation_conflict.ok());
    auto conflicted = sessions.get(friend_number);
    IOTOX_CHECK(conflicted);
    IOTOX_CHECK(conflicted.value().state ==
                iotox::protocol::PeerSessionState::conflicting_confirmation);
    IOTOX_CHECK(!iotox::protocol::is_application_ready(conflicted.value()));

    // A byte-identical HELLO retry is idempotent. Changed canonical material is
    // a conflict even after the confirmation gate had once opened.
    auto hello_retry = incoming;
    hello_retry.message_id = 2002U;
    IOTOX_CHECK(sessions.receive_hello(
                    friend_number, peer_key, hello_retry, 109U)
                    .ok());
    auto changed_peer = peer_hello;
    changed_peer.session_nonce = nonce(81U);
    const auto conflicting_hello = hello_frame(changed_peer, 2003U);
    const auto hello_conflict = sessions.receive_hello(
        friend_number, peer_key, conflicting_hello, 110U);
    IOTOX_CHECK(!hello_conflict.ok());
    conflicted = sessions.get(friend_number);
    IOTOX_CHECK(conflicted);
    IOTOX_CHECK(conflicted.value().state ==
                iotox::protocol::PeerSessionState::conflicting_hello);

    IOTOX_CHECK(sessions.peer_offline(friend_number, 111U).ok());
    auto offline = sessions.get(friend_number);
    IOTOX_CHECK(offline);
    IOTOX_CHECK(!offline.value().connected);
    IOTOX_CHECK(offline.value().online_epoch == 1U);

    auto second_epoch = sessions.peer_online(
        friend_number, peer_key, 2, nonce(101U), 112U);
    IOTOX_CHECK(second_epoch);
    IOTOX_CHECK(second_epoch.value().online_epoch == 2U);
    IOTOX_CHECK(!second_epoch.value().hello_received);
    IOTOX_CHECK(!second_epoch.value().confirmation_received);
}

IOTOX_TEST("durable incarnation advances an application epoch without "
           "weakening conflicts") {
    constexpr std::uint32_t friend_number = 17U;
    constexpr std::uint64_t local_incarnation = 40U;
    constexpr std::uint64_t first_peer_incarnation = 90U;
    constexpr std::uint64_t next_peer_incarnation = 91U;
    const std::string local_key = public_key('B');
    const std::string peer_key = public_key('A');
    const std::uint64_t restart_feature = iotox::protocol::feature_bit(
        iotox::protocol::Feature::application_epoch_restart_v1);
    const std::uint64_t restart_features =
        iotox::protocol::kImplementedFeatureMask | restart_feature;
    iotox::protocol::PeerSessionRegistry sessions(4096U);

    IOTOX_CHECK(sessions.set_supported_features(restart_features).ok());
    IOTOX_CHECK(sessions.set_local_incarnation(local_incarnation).ok());
    IOTOX_CHECK(sessions.set_local_public_key(local_key).ok());
    IOTOX_CHECK(sessions.ensure_offline_peer(
                    friend_number, peer_key, 100U)
                    .ok());
    auto online = sessions.peer_online(
        friend_number, peer_key, 1, nonce(1U), 101U);
    IOTOX_CHECK(online);
    IOTOX_CHECK(iotox::protocol::session_incarnation(
                    online.value().local.session_nonce) ==
                local_incarnation);
    IOTOX_CHECK(iotox::protocol::session_connection_epoch(
                    online.value().local.session_nonce) == 1U);
    auto local_hello = sessions.make_hello_frame(friend_number, 1001U);
    IOTOX_CHECK(local_hello);
    IOTOX_CHECK(sessions.mark_hello_sent(
                    friend_number, local_hello.value().message_id, 102U)
                    .ok());

    auto first_peer = iotox::protocol::make_local_hello(
        2048U,
        iotox::protocol::bind_session_generation(
            nonce(61U), first_peer_incarnation, 1U),
        restart_features);
    IOTOX_CHECK(sessions.receive_hello(
                    friend_number, peer_key,
                    hello_frame(first_peer, 2001U), 103U)
                    .ok());
    auto first = sessions.get(friend_number);
    IOTOX_CHECK(first);
    IOTOX_CHECK(first.value().online_epoch == 1U);
    IOTOX_CHECK(first.value().hello_sent);

    // The peer can reconnect asymmetrically while its process and the local
    // Tox transport epoch remain alive. Its process-local generation still
    // orders the fresh HELLO.
    auto reconnected_peer = iotox::protocol::make_local_hello(
        2048U,
        iotox::protocol::bind_session_generation(
            nonce(81U), first_peer_incarnation, 2U),
        restart_features);
    IOTOX_CHECK(sessions.receive_hello(
                    friend_number, peer_key,
                    hello_frame(reconnected_peer, 2002U), 104U)
                    .ok());
    auto reconnected = sessions.get(friend_number);
    IOTOX_CHECK(reconnected);
    IOTOX_CHECK(reconnected.value().online_epoch == 2U);
    IOTOX_CHECK(!reconnected.value().hello_sent);
    IOTOX_CHECK(reconnected.value().hello_received);
    IOTOX_CHECK(reconnected.value().local_hello_message_id == 1001U);
    IOTOX_CHECK(reconnected.value().peer_hello_message_id == 2002U);
    IOTOX_CHECK(iotox::protocol::session_incarnation(
                    reconnected.value().peer.session_nonce) ==
                first_peer_incarnation);
    IOTOX_CHECK(iotox::protocol::session_connection_epoch(
                    reconnected.value().peer.session_nonce) == 2U);
    IOTOX_CHECK(!reconnected.value().confirmation_sent);
    IOTOX_CHECK(!reconnected.value().confirmation_received);

    // A durable process restart resets the local connection counter but its
    // greater incarnation still makes the tuple newer.
    auto restarted_peer = iotox::protocol::make_local_hello(
        2048U,
        iotox::protocol::bind_session_generation(
            nonce(91U), next_peer_incarnation, 1U),
        restart_features);
    IOTOX_CHECK(sessions.receive_hello(
                    friend_number, peer_key,
                    hello_frame(restarted_peer, 2003U), 105U)
                    .ok());
    auto restarted = sessions.get(friend_number);
    IOTOX_CHECK(restarted);
    IOTOX_CHECK(restarted.value().online_epoch == 3U);
    IOTOX_CHECK(iotox::protocol::session_incarnation(
                    restarted.value().peer.session_nonce) ==
                next_peer_incarnation);
    IOTOX_CHECK(iotox::protocol::session_connection_epoch(
                    restarted.value().peer.session_nonce) == 1U);

    // A reordered prior generation cannot roll back or poison the accepted
    // fresh state. It remains available for the exact local-HELLO resend.
    IOTOX_CHECK(!sessions.receive_hello(
                     friend_number, peer_key,
                     hello_frame(reconnected_peer, 2004U), 106U)
                     .ok());
    auto after_stale = sessions.get(friend_number);
    IOTOX_CHECK(after_stale);
    IOTOX_CHECK(after_stale.value().online_epoch == 3U);
    IOTOX_CHECK(after_stale.value().state !=
                iotox::protocol::PeerSessionState::conflicting_hello);
    IOTOX_CHECK(iotox::protocol::session_incarnation(
                    after_stale.value().peer.session_nonce) ==
                next_peer_incarnation);

    // A different nonce inside the exact same claimed generation retains the
    // original fail-closed conflict rule.
    auto conflicting_peer = restarted_peer;
    conflicting_peer.session_nonce =
        iotox::protocol::bind_session_generation(
            nonce(101U), next_peer_incarnation, 1U);
    IOTOX_CHECK(!sessions.receive_hello(
                     friend_number, peer_key,
                     hello_frame(conflicting_peer, 2005U), 107U)
                     .ok());
    auto conflicted = sessions.get(friend_number);
    IOTOX_CHECK(conflicted);
    IOTOX_CHECK(conflicted.value().online_epoch == 3U);
    IOTOX_CHECK(conflicted.value().state ==
                iotox::protocol::PeerSessionState::conflicting_hello);
}

IOTOX_TEST("first structurally valid wrong confirmation freezes the online epoch") {
    constexpr std::uint32_t friend_number = 8U;
    const std::string local_key = public_key('B');
    const std::string peer_key = public_key('A');
    iotox::protocol::PeerSessionRegistry sessions(4096U);

    IOTOX_CHECK(sessions.set_local_public_key(local_key).ok());
    IOTOX_CHECK(sessions.ensure_offline_peer(
                    friend_number, peer_key, 200U)
                    .ok());
    IOTOX_CHECK(sessions.peer_online(
                    friend_number, peer_key, 1, nonce(111U), 201U));
    IOTOX_CHECK(sessions.mark_hello_sent(
                    friend_number, 5001U, 202U)
                    .ok());
    const auto peer_hello =
        iotox::protocol::make_local_hello(2048U, nonce(131U));
    const auto incoming_hello = hello_frame(peer_hello, 6001U);
    IOTOX_CHECK(sessions.receive_hello(
                    friend_number, peer_key, incoming_hello, 203U)
                    .ok());

    const auto snapshot = sessions.get(friend_number);
    IOTOX_CHECK(snapshot);

    // This is a valid confirmation object, but it claims the local endpoint was
    // the sender. The receiver must freeze and reject it, not let the peer probe
    // with one transcript and repair it inside the same online epoch.
    const auto wrong_sender = confirmation_frame(
        local_key, peer_key, snapshot.value().local, peer_hello,
        7001U, 5001U);
    const auto rejected = sessions.receive_confirmation(
        friend_number, peer_key, wrong_sender, 204U);
    IOTOX_CHECK(!rejected.ok());
    auto malformed = sessions.get(friend_number);
    IOTOX_CHECK(malformed);
    IOTOX_CHECK(
        malformed.value().state ==
        iotox::protocol::PeerSessionState::malformed_confirmation);
    IOTOX_CHECK(!iotox::protocol::is_application_ready(malformed.value()));

    // Byte identity is not semantic rehabilitation. Retrying the same wrong
    // confirmation must remain a rejection, even though it remains the frozen
    // first confirmation for this online epoch.
    auto same_wrong_sender = wrong_sender;
    same_wrong_sender.message_id = 7002U;
    const auto repeated_wrong = sessions.receive_confirmation(
        friend_number, peer_key, same_wrong_sender, 205U);
    IOTOX_CHECK(!repeated_wrong.ok());
    malformed = sessions.get(friend_number);
    IOTOX_CHECK(malformed);
    IOTOX_CHECK(
        malformed.value().state ==
        iotox::protocol::PeerSessionState::malformed_confirmation);

    const auto correct_sender = confirmation_frame(
        peer_key, local_key, peer_hello, snapshot.value().local,
        7003U, 5001U);
    const auto changed = sessions.receive_confirmation(
        friend_number, peer_key, correct_sender, 206U);
    IOTOX_CHECK(!changed.ok());
    auto conflict = sessions.get(friend_number);
    IOTOX_CHECK(conflict);
    IOTOX_CHECK(
        conflict.value().state ==
        iotox::protocol::PeerSessionState::conflicting_confirmation);

    IOTOX_CHECK(sessions.peer_offline(friend_number, 207U).ok());
    IOTOX_CHECK(sessions.peer_online(
                    friend_number, peer_key, 1, nonce(151U), 208U));
}

IOTOX_TEST("session rendering keeps establishment separate from authorization") {
    iotox::protocol::PeerSessionSnapshot snapshot;
    snapshot.friend_number = 9U;
    snapshot.public_key = public_key('B');
    snapshot.state = iotox::protocol::PeerSessionState::confirmed;
    snapshot.connected = true;
    snapshot.hello_sent = true;
    snapshot.hello_received = true;
    snapshot.confirmation_sent = true;
    snapshot.confirmation_received = true;
    snapshot.application_ready = true;
    snapshot.online_epoch = 3U;
    snapshot.negotiated.compatible = true;
    snapshot.negotiated.selected = {1U, 0U};
    const auto ratox = iotox::protocol::feature_bit(
        iotox::protocol::Feature::ratox_interactive_v1);
    snapshot.local.supported_features =
        iotox::protocol::kImplementedFeatureMask | ratox;
    snapshot.local.required_features =
        iotox::protocol::kRequiredFeatureMask;
    snapshot.peer.supported_features =
        iotox::protocol::kImplementedFeatureMask;
    snapshot.peer.required_features =
        iotox::protocol::kRequiredFeatureMask;
    snapshot.negotiated.shared_features =
        iotox::protocol::kImplementedFeatureMask;
    snapshot.detail = "confirmed test session";
    const std::string rendered =
        iotox::protocol::render_session_snapshot(snapshot);
    IOTOX_CHECK(rendered.find("state=confirmed") != std::string::npos);
    IOTOX_CHECK(rendered.find("application-ready=1") != std::string::npos);
    IOTOX_CHECK(rendered.find("selected-protocol=1.0") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("local-supported-features=0x") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("ratox-interactive-v1") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("peer-supported-features=0x") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find("shared-features=0x") !=
                std::string::npos);
    IOTOX_CHECK(rendered.find(
                    "authorization=separate-authority-session") !=
                std::string::npos);
}

IOTOX_TEST("protocol nonces and message identifiers come from the operating system") {
    auto identifier = iotox::security::random_u64_nonzero();
    IOTOX_CHECK(identifier);
    IOTOX_CHECK(identifier.value() != 0U);
    auto generated_nonce = iotox::security::random_nonce_128();
    IOTOX_CHECK(generated_nonce);
    IOTOX_CHECK(std::any_of(
        generated_nonce.value().begin(), generated_nonce.value().end(),
        [](std::uint8_t value) { return value != 0U; }));
}

IOTOX_TEST("application frames remain closed until the transcript is confirmed") {
    iotox::protocol::PeerSessionSnapshot snapshot;
    snapshot.state =
        iotox::protocol::PeerSessionState::awaiting_confirmation;
    snapshot.connected = true;
    snapshot.hello_sent = true;
    snapshot.hello_received = true;
    snapshot.negotiated.compatible = true;
    snapshot.negotiated.selected = {1U, 0U};
    snapshot.negotiated.maximum_frame_payload_size = 512U;

    iotox::protocol::Frame command;
    command.type = iotox::protocol::MessageType::command;
    command.message_id = 99U;
    command.payload = {'p', 'i', 'n', 'g'};
    IOTOX_CHECK(!iotox::protocol::validate_application_frame_for_session(
                     snapshot, command)
                     .ok());

    snapshot.state = iotox::protocol::PeerSessionState::confirmed;
    snapshot.confirmation_sent = true;
    snapshot.confirmation_received = true;
    snapshot.application_ready = true;
    IOTOX_CHECK(iotox::protocol::validate_application_frame_for_session(
                    snapshot, command)
                    .ok());

    auto wrong_version = command;
    wrong_version.minor = 1U;
    IOTOX_CHECK(!iotox::protocol::validate_application_frame_for_session(
                     snapshot, wrong_version)
                     .ok());

    auto missing_id = command;
    missing_id.message_id = 0U;
    IOTOX_CHECK(!iotox::protocol::validate_application_frame_for_session(
                     snapshot, missing_id)
                     .ok());

    auto oversized = command;
    oversized.payload.resize(513U, 0U);
    IOTOX_CHECK(!iotox::protocol::validate_application_frame_for_session(
                     snapshot, oversized)
                     .ok());

    auto session_frame = command;
    session_frame.type = iotox::protocol::MessageType::hello;
    IOTOX_CHECK(!iotox::protocol::validate_application_frame_for_session(
                     snapshot, session_frame)
                     .ok());
}
