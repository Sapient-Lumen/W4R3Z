#include "iotox/route_binding.hpp"

#include "iotox/security/authority_session.hpp"

#include <algorithm>
#include <array>
#include <string_view>
#include <vector>

namespace iotox::routes {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {
    'I', 'O', 'T', 'O', 'X', 'R', 'B', '1'};
constexpr std::array<std::uint8_t, 8U> kPrivateMemberMagic = {
    'I', 'O', 'T', 'O', 'X', 'R', 'B', '2'};
constexpr std::string_view kSignatureDomain =
    "IOTOX-ROUTE-BINDING-SIGNATURE-V1";
constexpr std::string_view kPrivateMemberSignatureDomain =
    "IOTOX-PRIVATE-ROUTE-MEMBER-BINDING-SIGNATURE-V2";

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output[offset++] = static_cast<std::uint8_t>(
            (value >> static_cast<unsigned>(shift)) & 0xffU);
    }
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | input[offset + index];
    }
    return value;
}

Result<ToxPublicKey> parse_transport_key(std::string_view text) {
    if (text.size() != 64U) {
        return Status{ErrorCode::protocol_error,
                      "session transport public key has an invalid length"};
    }
    const auto nibble = [](char value) -> int {
        if (value >= '0' && value <= '9') return value - '0';
        if (value >= 'a' && value <= 'f') return value - 'a' + 10;
        if (value >= 'A' && value <= 'F') return value - 'A' + 10;
        return -1;
    };
    ToxPublicKey key{};
    for (std::size_t index = 0U; index < key.size(); ++index) {
        const int high = nibble(text[index * 2U]);
        const int low = nibble(text[index * 2U + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::protocol_error,
                          "session transport public key is not hexadecimal"};
        }
        key[index] = static_cast<std::uint8_t>((high << 4) | low);
    }
    return key;
}

const MemberPolicy *find_member(const RouteSet &route_set,
                                const ToxPublicKey &key) {
    const auto found = std::find_if(
        route_set.members.begin(), route_set.members.end(),
        [&key](const MemberPolicy &member) {
            return member.tox_public_key == key;
        });
    return found == route_set.members.end() ? nullptr : &*found;
}

std::vector<std::uint8_t> signature_message(
    std::span<const std::uint8_t, kRouteBindingBodyBytes> body) {
    std::vector<std::uint8_t> message;
    message.reserve(kSignatureDomain.size() + body.size());
    message.insert(message.end(), kSignatureDomain.begin(),
                   kSignatureDomain.end());
    message.insert(message.end(), body.begin(), body.end());
    return message;
}

std::vector<std::uint8_t> private_member_signature_message(
    std::span<const std::uint8_t,
              kPrivateRouteMemberBindingBodyBytes> body) {
    std::vector<std::uint8_t> message;
    message.reserve(kPrivateMemberSignatureDomain.size() + body.size());
    message.insert(message.end(), kPrivateMemberSignatureDomain.begin(),
                   kPrivateMemberSignatureDomain.end());
    message.insert(message.end(), body.begin(), body.end());
    return message;
}

Status validate_route_set_shape(const RouteSet &route_set) {
    if (route_set.generation == 0U ||
        (route_set.format_version != kRouteSetFormatVersion &&
         route_set.format_version != kRouteSetFormatVersionV2) ||
        route_set.minimum_route_protocol != kRouteProtocolVersion ||
        all_zero(route_set.stable_device_principal) ||
        all_zero(route_set.coordinator_tox_public_key)) {
        return Status{ErrorCode::protocol_error,
                      "route binding received an invalid route-set context"};
    }
    return Status::success();
}

Status require_negotiated_route_binding(
    const protocol::PeerSessionSnapshot &session) {
    if (!protocol::is_application_ready(session) ||
        (session.negotiated.shared_features &
         protocol::feature_bit(protocol::Feature::route_binding_v1)) == 0U) {
        return Status{
            ErrorCode::unavailable,
            "route binding requires a confirmed session that negotiated route-binding-v1"};
    }
    return Status::success();
}

Status require_private_route_feature(
    const protocol::PeerSessionSnapshot &session) {
    if (!protocol::is_application_ready(session) ||
        (session.negotiated.shared_features & protocol::feature_bit(
             protocol::Feature::private_route_binding_v2)) == 0U) {
        return Status{
            ErrorCode::unavailable,
            "private route binding requires a confirmed session that negotiated private-route-binding-v2"};
    }
    return Status::success();
}

Status validate_primary_authority(
    const protocol::PeerSessionSnapshot &session,
    const security::PeerAuthoritySnapshot &authority,
    const security::Sodium &sodium) {
    const Status feature = require_private_route_feature(session);
    if (!feature.ok()) return feature;
    if (!authority.connected || !authority.feature_negotiated ||
        !authority.remote_authorized ||
        authority.friend_number != session.friend_number ||
        authority.online_epoch != session.online_epoch ||
        authority.transport_public_key != session.public_key ||
        all_zero(authority.remote_principal)) {
        return Status{
            ErrorCode::unavailable,
            "private route inventory requires the exact authority-authenticated primary session"};
    }
    auto digest = security::authority_session_transcript_digest(
        session, sodium);
    if (!digest || digest.value() != authority.session_transcript_digest) {
        return Status{
            ErrorCode::protocol_error,
            "private route inventory authority transcript differs from the primary session"};
    }
    return Status::success();
}

Status validate_private_inventory_edge(
    const PrivateRouteInventory &inventory,
    const protocol::PeerSessionSnapshot &primary_session,
    const protocol::PeerSessionSnapshot &auxiliary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::Sodium &sodium) {
    const Status primary = validate_primary_authority(
        primary_session, primary_authority, sodium);
    if (!primary.ok()) return primary;
    const Status auxiliary = require_private_route_feature(auxiliary_session);
    if (!auxiliary.ok()) return auxiliary;
    auto coordinator = parse_transport_key(
        primary_authority.transport_public_key);
    auto auxiliary_peer = parse_transport_key(auxiliary_session.public_key);
    if (!coordinator || !auxiliary_peer ||
        inventory.primary_friend_number != primary_session.friend_number ||
        inventory.primary_online_epoch != primary_session.online_epoch ||
        !security::constant_time_equal(
            inventory.route_set.stable_device_principal,
            primary_authority.remote_principal) ||
        inventory.route_set.coordinator_tox_public_key !=
            coordinator.value() ||
        find_member(inventory.route_set, auxiliary_peer.value()) == nullptr) {
        return Status{
            ErrorCode::protocol_error,
            "auxiliary route is absent from the current authority-private inventory"};
    }
    return Status::success();
}

Result<PrivateRouteMemberBindingArtifact> make_private_member_binding(
    std::span<const std::uint8_t> signed_route_set,
    const RouteSet &route_set, const ToxPublicKey &local_route_key,
    const protocol::PeerSessionSnapshot &session,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    const Status shape = validate_route_set_shape(route_set);
    if (!shape.ok()) return shape;
    const Status feature = require_private_route_feature(session);
    if (!feature.ok()) return feature;
    if (!security::constant_time_equal(
            route_set.stable_device_principal, identity.public_key())) {
        return Status{
            ErrorCode::protocol_error,
            "private member-binding signer is not the route-set stable principal"};
    }
    auto authenticated = verify_route_set(
        signed_route_set, identity.public_key(), route_set.generation,
        sodium);
    if (!authenticated || authenticated.value() != route_set) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding is not anchored in the exact signed local inventory"};
    }
    const MemberPolicy *member = find_member(route_set, local_route_key);
    auto session_key = parse_transport_key(session.local_public_key);
    if (member == nullptr || !session_key ||
        session_key.value() != local_route_key) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding local key is absent or differs from the auxiliary session"};
    }
    auto transcript_digest =
        security::authority_session_transcript_digest(session, sodium);
    if (!transcript_digest) return transcript_digest.status();
    auto inventory_digest = route_set_artifact_digest(
        signed_route_set, sodium);
    if (!inventory_digest) return inventory_digest.status();

    PrivateRouteMemberBindingArtifact artifact{};
    std::copy(kPrivateMemberMagic.begin(), kPrivateMemberMagic.end(),
              artifact.begin());
    artifact[8U] = 2U;
    artifact[9U] = kRouteProtocolVersion;
    artifact[10U] = static_cast<std::uint8_t>(member->role);
    artifact[11U] = static_cast<std::uint8_t>(
        member->connection_class);
    write_u64(artifact, 16U, route_set.generation);
    std::copy(route_set.stable_device_principal.begin(),
              route_set.stable_device_principal.end(),
              artifact.begin() + 24U);
    std::copy(route_set.coordinator_tox_public_key.begin(),
              route_set.coordinator_tox_public_key.end(),
              artifact.begin() + 56U);
    std::copy(local_route_key.begin(), local_route_key.end(),
              artifact.begin() + 88U);
    std::copy(transcript_digest.value().begin(),
              transcript_digest.value().end(), artifact.begin() + 120U);
    std::copy(inventory_digest.value().begin(),
              inventory_digest.value().end(), artifact.begin() + 152U);
    auto body = std::span<const std::uint8_t,
                          kPrivateRouteMemberBindingBodyBytes>{
        artifact.data(), kPrivateRouteMemberBindingBodyBytes};
    auto signature = identity.sign(
        private_member_signature_message(body));
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              artifact.begin() + kPrivateRouteMemberBindingBodyBytes);
    return artifact;
}

Status verify_private_member_binding(
    std::span<const std::uint8_t> artifact,
    const PrivateRouteInventory &expected_inventory,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium) {
    const Status shape = validate_route_set_shape(
        expected_inventory.route_set);
    if (!shape.ok()) return shape;
    const Status feature = require_private_route_feature(session);
    if (!feature.ok()) return feature;
    if (artifact.size() != kPrivateRouteMemberBindingArtifactBytes ||
        !std::equal(kPrivateMemberMagic.begin(), kPrivateMemberMagic.end(),
                    artifact.begin()) ||
        artifact[8U] != 2U || artifact[9U] != kRouteProtocolVersion ||
        !all_zero(artifact.subspan(12U, 4U)) ||
        !all_zero(artifact.subspan(184U, 8U))) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding header, length, or reserved bytes are invalid"};
    }
    const auto role = static_cast<Role>(artifact[10U]);
    const auto connection_class =
        static_cast<ConnectionClass>(artifact[11U]);
    const std::uint64_t generation = read_u64(artifact, 16U);
    security::SigningPublicKey principal{};
    ToxPublicKey coordinator{};
    ToxPublicKey route_key{};
    security::Digest transcript_digest{};
    security::Digest inventory_digest{};
    std::copy_n(artifact.begin() + 24U, principal.size(),
                principal.begin());
    std::copy_n(artifact.begin() + 56U, coordinator.size(),
                coordinator.begin());
    std::copy_n(artifact.begin() + 88U, route_key.size(),
                route_key.begin());
    std::copy_n(artifact.begin() + 120U, transcript_digest.size(),
                transcript_digest.begin());
    std::copy_n(artifact.begin() + 152U, inventory_digest.size(),
                inventory_digest.begin());
    if (!security::constant_time_equal(
            principal,
            expected_inventory.route_set.stable_device_principal) ||
        coordinator !=
            expected_inventory.route_set.coordinator_tox_public_key ||
        generation != expected_inventory.route_set.generation ||
        !security::constant_time_equal(
            inventory_digest, expected_inventory.artifact_digest)) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding names a foreign, stale, or forked inventory"};
    }
    const MemberPolicy *member = find_member(
        expected_inventory.route_set, route_key);
    if (member == nullptr || member->role != role ||
        member->connection_class != connection_class) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding policy is absent or mismatched"};
    }
    auto peer_key = parse_transport_key(session.public_key);
    if (!peer_key || peer_key.value() != route_key) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding key differs from the auxiliary peer"};
    }
    auto expected_transcript =
        security::authority_session_transcript_digest(session, sodium);
    if (!expected_transcript ||
        expected_transcript.value() != transcript_digest) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding differs from the auxiliary transcript"};
    }
    security::Signature signature{};
    std::copy_n(
        artifact.begin() + kPrivateRouteMemberBindingBodyBytes,
        signature.size(), signature.begin());
    auto body = std::span<const std::uint8_t,
                          kPrivateRouteMemberBindingBodyBytes>{
        artifact.data(), kPrivateRouteMemberBindingBodyBytes};
    const Status verified = sodium.verify_detached(
        signature, private_member_signature_message(body), principal);
    if (!verified.ok()) {
        return Status{
            ErrorCode::protocol_error,
            "private member binding stable-device signature is invalid"};
    }
    return Status::success();
}

}  // namespace

Result<RouteBindingArtifact> make_route_binding(
    const RouteSet &route_set, const ToxPublicKey &local_route_key,
    const protocol::PeerSessionSnapshot &session,
    const security::DeviceIdentity &identity, const security::Sodium &sodium) {
    const Status shape = validate_route_set_shape(route_set);
    if (!shape.ok()) return shape;
    const Status negotiated = require_negotiated_route_binding(session);
    if (!negotiated.ok()) return negotiated;
    if (!security::constant_time_equal(route_set.stable_device_principal,
                                       identity.public_key())) {
        return Status{ErrorCode::protocol_error,
                      "route binding signer is not the route-set stable principal"};
    }
    const MemberPolicy *member = find_member(route_set, local_route_key);
    if (member == nullptr) {
        return Status{ErrorCode::protocol_error,
                      "local route key is absent from the authenticated route set"};
    }
    auto session_key = parse_transport_key(session.local_public_key);
    if (!session_key || session_key.value() != local_route_key) {
        return Status{ErrorCode::protocol_error,
                      "confirmed session local key does not match the route member"};
    }
    auto digest = security::authority_session_transcript_digest(session, sodium);
    if (!digest) return digest.status();

    RouteBindingArtifact artifact{};
    std::copy(kMagic.begin(), kMagic.end(), artifact.begin());
    artifact[8U] = kRouteBindingFormatVersion;
    artifact[9U] = kRouteProtocolVersion;
    artifact[10U] = static_cast<std::uint8_t>(member->role);
    artifact[11U] = static_cast<std::uint8_t>(member->connection_class);
    write_u64(artifact, 16U, route_set.generation);
    std::copy(route_set.stable_device_principal.begin(),
              route_set.stable_device_principal.end(), artifact.begin() + 24U);
    std::copy(route_set.coordinator_tox_public_key.begin(),
              route_set.coordinator_tox_public_key.end(), artifact.begin() + 56U);
    std::copy(local_route_key.begin(), local_route_key.end(),
              artifact.begin() + 88U);
    std::copy(digest.value().begin(), digest.value().end(),
              artifact.begin() + 120U);
    auto body = std::span<const std::uint8_t, kRouteBindingBodyBytes>{
        artifact.data(), kRouteBindingBodyBytes};
    auto signature = identity.sign(signature_message(body));
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              artifact.begin() + kRouteBindingBodyBytes);
    return artifact;
}

Status verify_route_binding(
    std::span<const std::uint8_t> artifact,
    const RouteSet &expected_remote_route_set,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium) {
    const Status shape = validate_route_set_shape(expected_remote_route_set);
    if (!shape.ok()) return shape;
    const Status negotiated = require_negotiated_route_binding(session);
    if (!negotiated.ok()) return negotiated;
    if (artifact.size() != kRouteBindingArtifactBytes ||
        !std::equal(kMagic.begin(), kMagic.end(), artifact.begin()) ||
        artifact[8U] != kRouteBindingFormatVersion ||
        artifact[9U] != kRouteProtocolVersion ||
        !all_zero(artifact.subspan(12U, 4U)) ||
        !all_zero(artifact.subspan(152U, 8U))) {
        return Status{ErrorCode::protocol_error,
                      "route binding header, length, or reserved bytes are invalid"};
    }
    const auto role = static_cast<Role>(artifact[10U]);
    const auto connection_class =
        static_cast<ConnectionClass>(artifact[11U]);
    const std::uint64_t generation = read_u64(artifact, 16U);
    security::SigningPublicKey principal{};
    ToxPublicKey coordinator{};
    ToxPublicKey route_key{};
    security::Digest transcript_digest{};
    std::copy_n(artifact.begin() + 24U, principal.size(), principal.begin());
    std::copy_n(artifact.begin() + 56U, coordinator.size(), coordinator.begin());
    std::copy_n(artifact.begin() + 88U, route_key.size(), route_key.begin());
    std::copy_n(artifact.begin() + 120U, transcript_digest.size(),
                transcript_digest.begin());
    if (!security::constant_time_equal(
            principal, expected_remote_route_set.stable_device_principal) ||
        coordinator != expected_remote_route_set.coordinator_tox_public_key ||
        generation != expected_remote_route_set.generation) {
        return Status{ErrorCode::protocol_error,
                      "route binding names a foreign or stale route set"};
    }
    const MemberPolicy *member = find_member(expected_remote_route_set, route_key);
    if (member == nullptr || member->role != role ||
        member->connection_class != connection_class) {
        return Status{ErrorCode::protocol_error,
                      "route binding member policy is absent or mismatched"};
    }
    auto peer_key = parse_transport_key(session.public_key);
    if (!peer_key || peer_key.value() != route_key) {
        return Status{ErrorCode::protocol_error,
                      "confirmed session peer key does not match the route binding"};
    }
    auto expected_digest =
        security::authority_session_transcript_digest(session, sodium);
    if (!expected_digest || expected_digest.value() != transcript_digest) {
        return Status{ErrorCode::protocol_error,
                      "route binding does not match the confirmed session transcript"};
    }
    security::Signature signature{};
    std::copy_n(artifact.begin() + kRouteBindingBodyBytes, signature.size(),
                signature.begin());
    auto body = std::span<const std::uint8_t, kRouteBindingBodyBytes>{
        artifact.data(), kRouteBindingBodyBytes};
    const Status verified = sodium.verify_detached(
        signature, signature_message(body), principal);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "route binding stable-device signature is invalid"};
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>> make_route_binding_exchange_payload(
    std::span<const std::uint8_t> signed_route_set,
    const RouteSet &route_set, const ToxPublicKey &local_route_key,
    const protocol::PeerSessionSnapshot &session,
    const security::DeviceIdentity &identity, const security::Sodium &sodium) {
    auto authenticated = verify_route_set(
        signed_route_set, identity.public_key(), route_set.generation, sodium);
    if (!authenticated || authenticated.value() != route_set) {
        return Status{
            ErrorCode::protocol_error,
            "route-binding exchange route set is not the exact authenticated local set"};
    }
    if (signed_route_set.size() > 0xffffU) {
        return Status{ErrorCode::resource_exhausted,
                      "route-binding exchange route set exceeds its length field"};
    }
    auto binding = make_route_binding(
        route_set, local_route_key, session, identity, sodium);
    if (!binding) return binding.status();
    const std::size_t payload_size = kRouteBindingSetLengthBytes +
        signed_route_set.size() + binding.value().size();
    if (payload_size > protocol::kMaxPayloadSize) {
        return Status{ErrorCode::resource_exhausted,
                      "route-binding exchange exceeds the IoTox frame payload"};
    }
    // Construct the already-bounded canonical payload at its final size. This
    // avoids allocator growth entirely and keeps GCC's optimized
    // -Wnull-dereference analysis from treating vector reallocation internals
    // as a possible null placement-new target.
    std::vector<std::uint8_t> payload(payload_size);
    const auto route_set_size =
        static_cast<std::uint16_t>(signed_route_set.size());
    payload[0U] = static_cast<std::uint8_t>(route_set_size >> 8U);
    payload[1U] = static_cast<std::uint8_t>(route_set_size & 0xffU);
    auto output = payload.begin() +
        static_cast<std::ptrdiff_t>(kRouteBindingSetLengthBytes);
    output = std::copy(signed_route_set.begin(), signed_route_set.end(), output);
    static_cast<void>(
        std::copy(binding.value().begin(), binding.value().end(), output));
    return payload;
}

Result<VerifiedRouteBinding> verify_route_binding_exchange_payload(
    std::span<const std::uint8_t> payload,
    const security::SigningPublicKey &expected_remote_principal,
    std::uint64_t minimum_remote_generation,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium) {
    if (payload.size() < kRouteBindingSetLengthBytes +
                             kRouteBindingArtifactBytes) {
        return Status{ErrorCode::protocol_error,
                      "route-binding exchange payload is truncated"};
    }
    const std::size_t route_set_size =
        (static_cast<std::size_t>(payload[0U]) << 8U) |
        static_cast<std::size_t>(payload[1U]);
    if (route_set_size == 0U ||
        payload.size() != kRouteBindingSetLengthBytes + route_set_size +
                              kRouteBindingArtifactBytes) {
        return Status{ErrorCode::protocol_error,
                      "route-binding exchange length is noncanonical"};
    }
    const auto route_set_bytes =
        payload.subspan(kRouteBindingSetLengthBytes, route_set_size);
    auto route_set = verify_route_set(
        route_set_bytes, expected_remote_principal,
        minimum_remote_generation, sodium);
    if (!route_set) return route_set.status();
    const auto binding_bytes = payload.last(kRouteBindingArtifactBytes);
    const Status binding_status = verify_route_binding(
        binding_bytes, route_set.value(), session, sodium);
    if (!binding_status.ok()) return binding_status;

    ToxPublicKey route_key{};
    std::copy_n(binding_bytes.begin() + 88U, route_key.size(),
                route_key.begin());
    const MemberPolicy *member = find_member(route_set.value(), route_key);
    if (member == nullptr) {
        return Status{ErrorCode::protocol_error,
                      "verified route binding lost its route-set member"};
    }
    const MemberPolicy verified_member = *member;
    VerifiedRouteBinding verified;
    verified.route_set = std::move(route_set).value();
    verified.member = verified_member;
    std::copy(binding_bytes.begin(), binding_bytes.end(),
              verified.binding.begin());
    return verified;
}

Result<protocol::Frame> make_route_binding_frame(
    std::span<const std::uint8_t> signed_route_set,
    const RouteSet &route_set, const ToxPublicKey &local_route_key,
    const protocol::PeerSessionSnapshot &session,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    std::uint64_t message_id) {
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "route-binding message identifier zero is reserved"};
    }
    auto payload = make_route_binding_exchange_payload(
        signed_route_set, route_set, local_route_key, session, identity,
        sodium);
    if (!payload) return payload.status();
    protocol::Frame frame;
    frame.major = session.negotiated.selected.major;
    frame.minor = session.negotiated.selected.minor;
    frame.type = protocol::MessageType::route_binding;
    frame.message_id = message_id;
    frame.sequence = kRouteBindingSequence;
    frame.payload = std::move(payload).value();
    return frame;
}

Result<protocol::Frame> make_private_route_inventory_frame(
    std::span<const std::uint8_t> signed_route_set,
    const RouteSet &route_set,
    const protocol::PeerSessionSnapshot &primary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium, std::uint64_t message_id) {
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "private route inventory message identifier zero is reserved"};
    }
    const Status authority = validate_primary_authority(
        primary_session, primary_authority, sodium);
    if (!authority.ok()) return authority;
    auto authenticated = verify_route_set(
        signed_route_set, identity.public_key(), route_set.generation,
        sodium);
    if (!authenticated || authenticated.value() != route_set) {
        return Status{
            ErrorCode::protocol_error,
            "private route inventory is not the exact authenticated local route set"};
    }
    auto primary_key = parse_transport_key(primary_session.local_public_key);
    if (!primary_key ||
        primary_key.value() != route_set.coordinator_tox_public_key) {
        return Status{
            ErrorCode::protocol_error,
            "private route inventory coordinator differs from the primary session"};
    }
    if (signed_route_set.size() >
        primary_session.negotiated.maximum_frame_payload_size) {
        return Status{ErrorCode::resource_exhausted,
                      "private route inventory exceeds the negotiated frame payload"};
    }
    protocol::Frame frame;
    frame.major = primary_session.negotiated.selected.major;
    frame.minor = primary_session.negotiated.selected.minor;
    frame.type = protocol::MessageType::private_route_inventory;
    frame.message_id = message_id;
    frame.sequence = kPrivateRouteInventorySequence;
    frame.payload.assign(signed_route_set.begin(), signed_route_set.end());
    return frame;
}

Result<PrivateRouteInventory> verify_private_route_inventory_frame(
    const protocol::Frame &frame,
    const protocol::PeerSessionSnapshot &primary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::Sodium &sodium) {
    const Status authority = validate_primary_authority(
        primary_session, primary_authority, sodium);
    if (!authority.ok()) return authority;
    const Status application =
        protocol::validate_application_frame_for_session(
            primary_session, frame);
    if (!application.ok()) return application;
    if (frame.type != protocol::MessageType::private_route_inventory ||
        frame.flags != 0U || frame.message_id == 0U ||
        frame.correlation_id != 0U ||
        frame.sequence != kPrivateRouteInventorySequence ||
        frame.expiry_unix_ms != 0U) {
        return Status{ErrorCode::protocol_error,
                      "private route inventory frame envelope is noncanonical"};
    }
    auto route_set = verify_route_set(
        frame.payload, primary_authority.remote_principal, 1U, sodium);
    if (!route_set) return route_set.status();
    auto primary_key = parse_transport_key(primary_session.public_key);
    if (!primary_key ||
        primary_key.value() != route_set.value().coordinator_tox_public_key) {
        return Status{
            ErrorCode::protocol_error,
            "private remote inventory coordinator differs from the authenticated primary"};
    }
    PrivateRouteInventory inventory;
    inventory.route_set = std::move(route_set).value();
    auto digest = route_set_artifact_digest(frame.payload, sodium);
    if (!digest) return digest.status();
    inventory.artifact_digest = digest.value();
    inventory.primary_friend_number = primary_session.friend_number;
    inventory.primary_online_epoch = primary_session.online_epoch;
    return inventory;
}

Result<protocol::Frame> make_private_route_member_binding_frame(
    std::span<const std::uint8_t> signed_local_route_set,
    const RouteSet &local_route_set, const ToxPublicKey &local_route_key,
    const PrivateRouteInventory &expected_remote_inventory,
    const protocol::PeerSessionSnapshot &primary_session,
    const protocol::PeerSessionSnapshot &auxiliary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium, std::uint64_t message_id) {
    if (message_id == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "private route member-binding message identifier zero is reserved"};
    }
    const Status edge = validate_private_inventory_edge(
        expected_remote_inventory, primary_session, auxiliary_session,
        primary_authority, sodium);
    if (!edge.ok()) return edge;
    auto binding = make_private_member_binding(
        signed_local_route_set, local_route_set, local_route_key,
        auxiliary_session, identity, sodium);
    if (!binding) return binding.status();
    protocol::Frame frame;
    frame.major = auxiliary_session.negotiated.selected.major;
    frame.minor = auxiliary_session.negotiated.selected.minor;
    frame.type = protocol::MessageType::private_route_member_binding;
    frame.message_id = message_id;
    frame.sequence = kPrivateRouteMemberBindingSequence;
    frame.payload.assign(binding.value().begin(), binding.value().end());
    return frame;
}

Status verify_private_route_member_binding_frame(
    const protocol::Frame &frame,
    const PrivateRouteInventory &expected_remote_inventory,
    const protocol::PeerSessionSnapshot &primary_session,
    const protocol::PeerSessionSnapshot &auxiliary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::Sodium &sodium) {
    const Status edge = validate_private_inventory_edge(
        expected_remote_inventory, primary_session, auxiliary_session,
        primary_authority, sodium);
    if (!edge.ok()) return edge;
    const Status application =
        protocol::validate_application_frame_for_session(
            auxiliary_session, frame);
    if (!application.ok()) return application;
    if (frame.type !=
            protocol::MessageType::private_route_member_binding ||
        frame.flags != 0U || frame.message_id == 0U ||
        frame.correlation_id != 0U ||
        frame.sequence != kPrivateRouteMemberBindingSequence ||
        frame.expiry_unix_ms != 0U ||
        frame.payload.size() != kPrivateRouteMemberBindingArtifactBytes) {
        return Status{
            ErrorCode::protocol_error,
            "private route member-binding frame envelope is noncanonical"};
    }
    return verify_private_member_binding(
        frame.payload, expected_remote_inventory, auxiliary_session, sodium);
}

PrivateRouteInventoryRegistry::PrivateRouteInventoryRegistry()
    : PrivateRouteInventoryRegistry(Config{}) {}

PrivateRouteInventoryRegistry::PrivateRouteInventoryRegistry(Config config)
    : config_(config) {}

Status PrivateRouteInventoryRegistry::validate_config() const {
    if (config_.maximum_active_primary_edges == 0U ||
        config_.maximum_active_primary_edges > 4096U ||
        config_.maximum_generation_high_water_records == 0U ||
        config_.maximum_generation_high_water_records > 4096U) {
        return Status{ErrorCode::invalid_argument,
                      "private route inventory registry bounds are invalid"};
    }
    return Status::success();
}

Result<PrivateRouteInventoryAdmission>
PrivateRouteInventoryRegistry::receive(
    const protocol::Frame &frame,
    const protocol::PeerSessionSnapshot &primary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::Sodium &sodium) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    auto verified = verify_private_route_inventory_frame(
        frame, primary_session, primary_authority, sodium);
    if (!verified) {
        std::scoped_lock lock(mutex_);
        ++rejected_;
        return verified.status();
    }
    auto encoded = protocol::encode(frame);
    if (!encoded) {
        std::scoped_lock lock(mutex_);
        ++rejected_;
        return encoded.status();
    }
    auto coordinator = parse_transport_key(primary_session.public_key);
    if (!coordinator) {
        std::scoped_lock lock(mutex_);
        ++rejected_;
        return coordinator.status();
    }

    PrivateRoutePrimaryContext context{
        verified.value(), primary_session, primary_authority};
    std::scoped_lock lock(mutex_);
    auto active = std::find_if(
        active_.begin(), active_.end(),
        [&primary_session](const ActiveEntry &entry) {
            return entry.context.session.friend_number ==
                primary_session.friend_number;
        });
    if (active != active_.end()) {
        const bool same_transport_peer =
            active->context.session.public_key == primary_session.public_key;
        const std::uint64_t retained_epoch =
            active->context.session.online_epoch;
        if (same_transport_peer &&
            primary_session.online_epoch < retained_epoch) {
            ++rejected_;
            return Status{ErrorCode::protocol_error,
                          "private route inventory belongs to a stale primary epoch"};
        }
        if (same_transport_peer &&
            primary_session.online_epoch == retained_epoch) {
            if (active->encoded_frame == encoded.value() &&
                active->context.authority.remote_principal ==
                    primary_authority.remote_principal &&
                active->context.authority.transport_public_key ==
                    primary_authority.transport_public_key) {
                ++exact_replays_;
                active->context.session = primary_session;
                active->context.authority = primary_authority;
                return PrivateRouteInventoryAdmission{
                    PrivateRouteInventoryAdmissionKind::exact_replay,
                    active->context};
            }
            ++rejected_;
            return Status{ErrorCode::protocol_error,
                          "private route inventory conflicts within one primary epoch"};
        }
    }
    if (active == active_.end() &&
        active_.size() >= config_.maximum_active_primary_edges) {
        ++rejected_;
        return Status{ErrorCode::resource_exhausted,
                      "private route inventory active-primary bound is exhausted"};
    }

    auto high_water = std::find_if(
        high_water_.begin(), high_water_.end(),
        [&primary_authority, &coordinator](const HighWaterEntry &entry) {
            return entry.stable_device_principal ==
                       primary_authority.remote_principal &&
                   entry.coordinator_tox_public_key == coordinator.value();
        });
    if (high_water != high_water_.end()) {
        if (verified.value().route_set.generation < high_water->generation ||
            (verified.value().route_set.generation == high_water->generation &&
             verified.value().artifact_digest != high_water->artifact_digest)) {
            ++rejected_;
            return Status{ErrorCode::protocol_error,
                          "private route inventory rolls back or forks observed generation"};
        }
    } else {
        if (high_water_.size() >=
            config_.maximum_generation_high_water_records) {
            ++rejected_;
            return Status{ErrorCode::resource_exhausted,
                          "private route inventory high-water bound is exhausted"};
        }
        high_water_.push_back(HighWaterEntry{
            primary_authority.remote_principal, coordinator.value(), 0U, {}});
        high_water = std::prev(high_water_.end());
    }
    if (verified.value().route_set.generation > high_water->generation) {
        high_water->generation = verified.value().route_set.generation;
        high_water->artifact_digest = verified.value().artifact_digest;
    }

    if (active == active_.end()) {
        active_.push_back(ActiveEntry{});
        active = std::prev(active_.end());
    }
    active->frame = frame;
    active->encoded_frame = std::move(encoded).value();
    active->context = context;
    ++accepted_;
    return PrivateRouteInventoryAdmission{
        PrivateRouteInventoryAdmissionKind::accepted, std::move(context)};
}

Status PrivateRouteInventoryRegistry::replace_active_edges(
    std::vector<PrivateRoutePrimaryEdge> edges,
    const security::Sodium &sodium) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (edges.size() > config_.maximum_active_primary_edges) {
        return Status{ErrorCode::resource_exhausted,
                      "private route inventory active-primary bound is exhausted"};
    }
    for (std::size_t index = 0U; index < edges.size(); ++index) {
        for (std::size_t later = index + 1U; later < edges.size(); ++later) {
            if (edges[index].session.friend_number ==
                edges[later].session.friend_number) {
                return Status{ErrorCode::invalid_argument,
                              "private route inventory primary edge is duplicated"};
            }
        }
    }

    std::scoped_lock lock(mutex_);
    std::erase_if(active_, [&edges, &sodium](ActiveEntry &entry) {
        const auto candidate = std::find_if(
            edges.begin(), edges.end(), [&entry](const auto &edge) {
                return edge.session.friend_number ==
                           entry.context.session.friend_number &&
                       edge.session.online_epoch ==
                           entry.context.session.online_epoch;
            });
        if (candidate == edges.end()) return true;
        auto verified = verify_private_route_inventory_frame(
            entry.frame, candidate->session, candidate->authority, sodium);
        if (!verified || verified.value() != entry.context.inventory) {
            return true;
        }
        entry.context.session = candidate->session;
        entry.context.authority = candidate->authority;
        return false;
    });
    return Status::success();
}

std::vector<PrivateRoutePrimaryContext>
PrivateRouteInventoryRegistry::contexts() const {
    std::scoped_lock lock(mutex_);
    std::vector<PrivateRoutePrimaryContext> result;
    result.reserve(active_.size());
    for (const ActiveEntry &entry : active_) {
        result.push_back(entry.context);
    }
    return result;
}

PrivateRouteInventoryRegistrySnapshot
PrivateRouteInventoryRegistry::snapshot() const {
    std::scoped_lock lock(mutex_);
    return PrivateRouteInventoryRegistrySnapshot{
        active_.size(), high_water_.size(), accepted_, exact_replays_,
        rejected_};
}

Result<VerifiedRouteBinding> verify_route_binding_frame(
    const protocol::Frame &frame,
    const security::SigningPublicKey &expected_remote_principal,
    std::uint64_t minimum_remote_generation,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium) {
    const Status application =
        protocol::validate_application_frame_for_session(session, frame);
    if (!application.ok()) return application;
    if (frame.type != protocol::MessageType::route_binding ||
        frame.flags != 0U || frame.correlation_id != 0U ||
        frame.sequence != kRouteBindingSequence ||
        frame.expiry_unix_ms != 0U) {
        return Status{ErrorCode::protocol_error,
                      "route-binding frame envelope is noncanonical"};
    }
    return verify_route_binding_exchange_payload(
        frame.payload, expected_remote_principal, minimum_remote_generation,
        session, sodium);
}

RouteBindingRegistry::RouteBindingRegistry()
    : RouteBindingRegistry(Config{}) {}

RouteBindingRegistry::RouteBindingRegistry(Config config)
    : config_(config) {}

Status RouteBindingRegistry::validate_config() const {
    if (config_.maximum_trusted_primary_routes == 0U ||
        config_.maximum_trusted_primary_routes > 4096U ||
        config_.maximum_workers == 0U ||
        config_.maximum_workers > kMaximumRouteMembers) {
        return Status{ErrorCode::invalid_argument,
                      "route-binding registry bounds are invalid"};
    }
    return Status::success();
}

Status RouteBindingRegistry::replace_trust(
    std::vector<RemoteRouteTrust> trust) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (trust.size() > config_.maximum_trusted_primary_routes) {
        return Status{ErrorCode::resource_exhausted,
                      "route-binding primary trust bound is exhausted"};
    }
    for (std::size_t index = 0U; index < trust.size(); ++index) {
        if (all_zero(trust[index].stable_device_principal) ||
            all_zero(trust[index].coordinator_tox_public_key) ||
            trust[index].minimum_generation == 0U ||
            trust[index].primary_online_epoch == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "route-binding primary trust record is incomplete"};
        }
        for (std::size_t later = index + 1U; later < trust.size(); ++later) {
            if (trust[index].coordinator_tox_public_key ==
                    trust[later].coordinator_tox_public_key) {
                return Status{ErrorCode::invalid_argument,
                              "route-binding primary coordinator trust is duplicated"};
            }
        }
    }

    std::scoped_lock lock(mutex_);
    std::vector<TrustState> replacement;
    replacement.reserve(trust.size());
    for (const RemoteRouteTrust &record : trust) {
        TrustState state;
        state.trust = record;
        const auto existing = std::find_if(
            trust_.begin(), trust_.end(),
            [&record](const TrustState &candidate) {
                return candidate.trust.stable_device_principal ==
                           record.stable_device_principal &&
                       candidate.trust.coordinator_tox_public_key ==
                           record.coordinator_tox_public_key;
            });
        if (existing != trust_.end()) {
            state.accepted_route_set = existing->accepted_route_set;
            if (state.accepted_route_set &&
                state.trust.minimum_generation <
                    state.accepted_route_set->generation) {
                state.trust.minimum_generation =
                    state.accepted_route_set->generation;
            }
        }
        replacement.push_back(std::move(state));
    }
    trust_ = std::move(replacement);
    workers_.erase(
        std::remove_if(
            workers_.begin(), workers_.end(),
            [this](const WorkerEntry &worker) {
                return std::none_of(
                    trust_.begin(), trust_.end(),
                    [&worker](const TrustState &state) {
                        return state.trust == worker.trust;
                    });
            }),
        workers_.end());
    return Status::success();
}

Result<RouteBindingAdmission> RouteBindingRegistry::receive(
    const ToxPublicKey &local_route_key, std::uint64_t worker_id,
    const protocol::Frame &frame,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (worker_id == 0U || all_zero(local_route_key)) {
        return Status{ErrorCode::invalid_argument,
                      "route-binding worker identity is incomplete"};
    }
    auto parsed_local_key = parse_transport_key(session.local_public_key);
    if (!parsed_local_key || parsed_local_key.value() != local_route_key) {
        return Status{ErrorCode::protocol_error,
                      "route-binding worker key differs from the confirmed local session"};
    }

    std::scoped_lock lock(mutex_);
    TrustState *matched_trust = nullptr;
    std::optional<VerifiedRouteBinding> verified;
    for (TrustState &candidate : trust_) {
        auto attempt = verify_route_binding_frame(
            frame, candidate.trust.stable_device_principal,
            candidate.trust.minimum_generation, session, sodium);
        if (!attempt ||
            attempt.value().route_set.coordinator_tox_public_key !=
                candidate.trust.coordinator_tox_public_key) {
            continue;
        }
        matched_trust = &candidate;
        verified.emplace(std::move(attempt).value());
        break;
    }
    if (matched_trust == nullptr || !verified) {
        ++rejected_;
        return Status{ErrorCode::protocol_error,
                      "route binding has no authority-authenticated primary association"};
    }

    if (matched_trust->accepted_route_set) {
        const RouteSet &accepted = *matched_trust->accepted_route_set;
        if (verified->route_set.generation < accepted.generation ||
            (verified->route_set.generation == accepted.generation &&
             verified->route_set != accepted)) {
            ++rejected_;
            return Status{ErrorCode::protocol_error,
                          "route binding replays or forks accepted remote inventory"};
        }
    }

    auto existing = std::find_if(
        workers_.begin(), workers_.end(),
        [&local_route_key](const WorkerEntry &entry) {
            return entry.local_route_key == local_route_key;
        });
    if (existing != workers_.end()) {
        if (existing->worker_id != worker_id ||
            session.online_epoch < existing->online_epoch) {
            ++rejected_;
            return Status{ErrorCode::protocol_error,
                          "route binding belongs to a stale or foreign worker incarnation"};
        }
        if (session.online_epoch == existing->online_epoch) {
            if (frame.message_id == existing->message_id &&
                matched_trust->trust == existing->trust &&
                verified->route_set == existing->verified.route_set &&
                verified->binding == existing->verified.binding) {
                ++exact_replays_;
                return RouteBindingAdmission{
                    RouteBindingAdmissionKind::exact_replay,
                    matched_trust->trust, std::move(*verified)};
            }
            ++rejected_;
            return Status{ErrorCode::protocol_error,
                          "route binding conflicts within one online epoch"};
        }
    } else {
        if (workers_.size() >= config_.maximum_workers) {
            ++rejected_;
            return Status{ErrorCode::resource_exhausted,
                          "route-binding worker replay bound is exhausted"};
        }
        workers_.push_back(WorkerEntry{});
        existing = std::prev(workers_.end());
    }

    matched_trust->accepted_route_set = verified->route_set;
    if (matched_trust->trust.minimum_generation <
        verified->route_set.generation) {
        matched_trust->trust.minimum_generation =
            verified->route_set.generation;
    }
    existing->local_route_key = local_route_key;
    existing->worker_id = worker_id;
    existing->online_epoch = session.online_epoch;
    existing->message_id = frame.message_id;
    existing->trust = matched_trust->trust;
    existing->verified = *verified;
    ++accepted_;
    return RouteBindingAdmission{
        RouteBindingAdmissionKind::accepted, matched_trust->trust,
        std::move(*verified)};
}

Status RouteBindingRegistry::retire_worker(
    const ToxPublicKey &local_route_key, std::uint64_t worker_id) {
    if (worker_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "route-binding worker identifier zero is reserved"};
    }
    std::scoped_lock lock(mutex_);
    const auto existing = std::find_if(
        workers_.begin(), workers_.end(),
        [&local_route_key](const WorkerEntry &entry) {
            return entry.local_route_key == local_route_key;
        });
    if (existing == workers_.end()) {
        return Status{ErrorCode::not_found,
                      "route-binding worker is not retained"};
    }
    if (existing->worker_id != worker_id) {
        return Status{ErrorCode::protocol_error,
                      "route-binding retirement names a foreign worker incarnation"};
    }
    workers_.erase(existing);
    return Status::success();
}

RouteBindingRegistrySnapshot RouteBindingRegistry::snapshot() const {
    std::scoped_lock lock(mutex_);
    return RouteBindingRegistrySnapshot{
        trust_.size(), workers_.size(), accepted_, exact_replays_, rejected_};
}

}  // namespace iotox::routes
