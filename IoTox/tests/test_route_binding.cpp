#include "iotox/route_binding.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <atomic>
#include <filesystem>
#include <string>
#include <unistd.h>

namespace {

iotox::protocol::SessionNonce nonce(std::uint8_t value) {
    iotox::protocol::SessionNonce result{};
    result.fill(value);
    return result;
}

struct SessionPair {
    iotox::protocol::PeerSessionSnapshot lower;
    iotox::protocol::PeerSessionSnapshot higher;
};

SessionPair confirmed_pair(std::uint64_t online_epoch = 1U,
                           std::uint8_t lower_nonce = 0x31U,
                           std::uint8_t higher_nonce = 0x51U,
                           char lower_key = '1', char higher_key = 'E') {
    using namespace iotox::protocol;
    const std::uint64_t features =
        kImplementedFeatureMask | feature_bit(Feature::route_binding_v1) |
        feature_bit(Feature::private_route_binding_v2);
    const HelloPayload lower_hello =
        make_local_hello(4096U, nonce(lower_nonce), features);
    const HelloPayload higher_hello =
        make_local_hello(4096U, nonce(higher_nonce), features);
    const NegotiatedProtocol negotiated =
        negotiate_protocol(lower_hello, higher_hello);
    IOTOX_CHECK(negotiated.compatible);
    PeerSessionSnapshot lower;
    lower.friend_number = 1U;
    lower.public_key = std::string(64U, higher_key);
    lower.local_public_key = std::string(64U, lower_key);
    lower.connection_status = 1;
    lower.state = PeerSessionState::confirmed;
    lower.connected = lower.hello_sent = lower.hello_received = true;
    lower.confirmation_sent = lower.confirmation_received = true;
    lower.application_ready = lower.local_role_known = true;
    lower.local_role = SessionRole::lower_transport_key;
    lower.online_epoch = online_epoch;
    lower.local_hello_message_id = 11U;
    lower.peer_hello_message_id = 12U;
    lower.local_confirmation_message_id = 13U;
    lower.peer_confirmation_message_id = 14U;
    lower.local = lower_hello;
    lower.peer = higher_hello;
    lower.negotiated = negotiated;
    PeerSessionSnapshot higher = lower;
    higher.friend_number = 2U;
    higher.public_key = lower.local_public_key;
    higher.local_public_key = lower.public_key;
    higher.local_role = SessionRole::higher_transport_key;
    higher.local_hello_message_id = lower.peer_hello_message_id;
    higher.peer_hello_message_id = lower.local_hello_message_id;
    higher.local_confirmation_message_id = lower.peer_confirmation_message_id;
    higher.peer_confirmation_message_id = lower.local_confirmation_message_id;
    higher.local = higher_hello;
    higher.peer = lower_hello;
    return {lower, higher};
}

iotox::routes::ToxPublicKey key(std::uint8_t value) {
    iotox::routes::ToxPublicKey result{};
    result.fill(value);
    return result;
}

}  // namespace

IOTOX_TEST("private route binding discloses inventory only on authorized primary") {
    static std::atomic<unsigned> sequence{0U};
    const auto root = std::filesystem::temp_directory_path() /
        ("iotox-private-route-binding-" + std::to_string(::getpid()) + "-" +
         std::to_string(sequence.fetch_add(1U)));
    std::filesystem::create_directories(root);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto local_identity = iotox::security::DeviceIdentity::load_or_create(
        root / "local.identity", sodium.value(), true);
    auto remote_identity = iotox::security::DeviceIdentity::load_or_create(
        root / "remote.identity", sodium.value(), true);
    IOTOX_CHECK(local_identity.ok());
    IOTOX_CHECK(remote_identity.ok());

    iotox::routes::RouteSet local_set;
    local_set.format_version = iotox::routes::kRouteSetFormatVersionV2;
    local_set.generation = 4U;
    local_set.stable_device_principal =
        local_identity.value().public_key();
    local_set.coordinator_tox_public_key = key(0x11U);
    local_set.members = {
        {key(0x11U), iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U,
         iotox::routes::NetworkClass::tox_native},
        {key(0x22U), iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 2U, 0U,
         iotox::routes::NetworkClass::tox_tor},
    };
    iotox::routes::RouteSet remote_set;
    remote_set.format_version = iotox::routes::kRouteSetFormatVersionV2;
    remote_set.generation = 7U;
    remote_set.stable_device_principal =
        remote_identity.value().public_key();
    remote_set.coordinator_tox_public_key = key(0xeeU);
    remote_set.members = {
        {key(0xddU), iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 2U, 0U,
         iotox::routes::NetworkClass::tox_tor},
        {key(0xeeU), iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U,
         iotox::routes::NetworkClass::tox_native},
    };
    auto signed_local = iotox::routes::sign_route_set(
        local_set, local_identity.value());
    auto signed_remote = iotox::routes::sign_route_set(
        remote_set, remote_identity.value());
    IOTOX_CHECK(signed_local.ok());
    IOTOX_CHECK(signed_remote.ok());

    const auto primary = confirmed_pair(3U);
    iotox::security::PeerAuthoritySnapshot local_authority;
    local_authority.friend_number = primary.lower.friend_number;
    local_authority.transport_public_key = primary.lower.public_key;
    local_authority.online_epoch = primary.lower.online_epoch;
    local_authority.connected = true;
    local_authority.feature_negotiated = true;
    local_authority.remote_authorized = true;
    local_authority.remote_principal =
        remote_identity.value().public_key();
    auto local_digest =
        iotox::security::authority_session_transcript_digest(
            primary.lower, sodium.value());
    IOTOX_CHECK(local_digest.ok());
    local_authority.session_transcript_digest = local_digest.value();

    iotox::security::PeerAuthoritySnapshot remote_authority;
    remote_authority.friend_number = primary.higher.friend_number;
    remote_authority.transport_public_key = primary.higher.public_key;
    remote_authority.online_epoch = primary.higher.online_epoch;
    remote_authority.connected = true;
    remote_authority.feature_negotiated = true;
    remote_authority.remote_authorized = true;
    remote_authority.remote_principal =
        local_identity.value().public_key();
    auto remote_digest =
        iotox::security::authority_session_transcript_digest(
            primary.higher, sodium.value());
    IOTOX_CHECK(remote_digest.ok());
    remote_authority.session_transcript_digest = remote_digest.value();

    auto local_inventory_frame =
        iotox::routes::make_private_route_inventory_frame(
            signed_local.value(), local_set, primary.lower,
            local_authority, local_identity.value(), sodium.value(), 101U);
    IOTOX_CHECK_MSG(local_inventory_frame.ok(),
                    local_inventory_frame.status().message());
    auto remote_inventory_frame =
        iotox::routes::make_private_route_inventory_frame(
            signed_remote.value(), remote_set, primary.higher,
            remote_authority, remote_identity.value(), sodium.value(), 201U);
    IOTOX_CHECK_MSG(remote_inventory_frame.ok(),
                    remote_inventory_frame.status().message());

    auto local_view_of_remote =
        iotox::routes::verify_private_route_inventory_frame(
            remote_inventory_frame.value(), primary.lower, local_authority,
            sodium.value());
    auto remote_view_of_local =
        iotox::routes::verify_private_route_inventory_frame(
            local_inventory_frame.value(), primary.higher, remote_authority,
            sodium.value());
    IOTOX_CHECK_MSG(local_view_of_remote.ok(),
                    local_view_of_remote.status().message());
    IOTOX_CHECK_MSG(remote_view_of_local.ok(),
                    remote_view_of_local.status().message());
    IOTOX_CHECK(local_view_of_remote.value().route_set == remote_set);
    IOTOX_CHECK(remote_view_of_local.value().route_set == local_set);

    const auto auxiliary = confirmed_pair(9U, 0x32U, 0x52U, '2', 'D');
    auto member_frame =
        iotox::routes::make_private_route_member_binding_frame(
            signed_local.value(), local_set, key(0x22U),
            local_view_of_remote.value(),
            primary.lower, auxiliary.lower, local_authority,
            local_identity.value(), sodium.value(), 301U);
    IOTOX_CHECK_MSG(member_frame.ok(), member_frame.status().message());
    IOTOX_CHECK(member_frame.value().payload.size() ==
                iotox::routes::kPrivateRouteMemberBindingArtifactBytes);
    constexpr std::array<std::uint8_t, 8U> private_magic{
        'I', 'O', 'T', 'O', 'X', 'R', 'B', '2'};
    IOTOX_CHECK(std::equal(
        private_magic.begin(), private_magic.end(),
        member_frame.value().payload.begin()));
    IOTOX_CHECK(std::equal(
        remote_view_of_local.value().artifact_digest.begin(),
        remote_view_of_local.value().artifact_digest.end(),
        member_frame.value().payload.begin() + 152U));
    IOTOX_CHECK(std::all_of(
        member_frame.value().payload.begin() + 184U,
        member_frame.value().payload.begin() + 192U,
        [](std::uint8_t value) { return value == 0U; }));
    IOTOX_CHECK(member_frame.value().payload.size() <
                signed_local.value().size() +
                    iotox::routes::kRouteBindingArtifactBytes);
    IOTOX_CHECK(iotox::routes::verify_private_route_member_binding_frame(
                    member_frame.value(), remote_view_of_local.value(),
                    primary.higher, auxiliary.higher, remote_authority,
                    sodium.value()).ok());

    auto same_generation_fork = local_set;
    ++same_generation_fork.members.back().maximum_active_work;
    auto signed_fork = iotox::routes::sign_route_set(
        same_generation_fork, local_identity.value());
    IOTOX_CHECK(signed_fork.ok());
    auto fork_member =
        iotox::routes::make_private_route_member_binding_frame(
            signed_fork.value(), same_generation_fork, key(0x22U),
            local_view_of_remote.value(), primary.lower, auxiliary.lower,
            local_authority, local_identity.value(), sodium.value(), 303U);
    IOTOX_CHECK(fork_member.ok());
    IOTOX_CHECK(!iotox::routes::verify_private_route_member_binding_frame(
                     fork_member.value(), remote_view_of_local.value(),
                     primary.higher, auxiliary.higher, remote_authority,
                     sodium.value()).ok());

    auto network_class_fork = local_set;
    network_class_fork.members.back().network_class =
        iotox::routes::NetworkClass::tox_i2p;
    auto signed_network_class_fork = iotox::routes::sign_route_set(
        network_class_fork, local_identity.value());
    IOTOX_CHECK(signed_network_class_fork.ok());
    auto network_class_member =
        iotox::routes::make_private_route_member_binding_frame(
            signed_network_class_fork.value(), network_class_fork,
            key(0x22U), local_view_of_remote.value(), primary.lower,
            auxiliary.lower, local_authority, local_identity.value(),
            sodium.value(), 304U);
    IOTOX_CHECK(network_class_member.ok());
    IOTOX_CHECK(!iotox::routes::verify_private_route_member_binding_frame(
                     network_class_member.value(),
                     remote_view_of_local.value(), primary.higher,
                     auxiliary.higher, remote_authority,
                     sodium.value()).ok());

    auto tampered_member = member_frame.value();
    tampered_member.payload[120U] ^= 1U;
    IOTOX_CHECK(!iotox::routes::verify_private_route_member_binding_frame(
                     tampered_member, remote_view_of_local.value(),
                     primary.higher, auxiliary.higher, remote_authority,
                     sodium.value()).ok());
    auto stale_authority = remote_authority;
    ++stale_authority.online_epoch;
    IOTOX_CHECK(!iotox::routes::verify_private_route_member_binding_frame(
                     member_frame.value(), remote_view_of_local.value(),
                     primary.higher, auxiliary.higher, stale_authority,
                     sodium.value()).ok());
    auto unauthorized = local_authority;
    unauthorized.remote_authorized = false;
    IOTOX_CHECK(!iotox::routes::make_private_route_inventory_frame(
                     signed_local.value(), local_set, primary.lower,
                     unauthorized, local_identity.value(), sodium.value(),
                     102U).ok());
    auto wrong_peer_inventory = local_view_of_remote.value();
    wrong_peer_inventory.route_set.members.front().tox_public_key =
        key(0xccU);
    IOTOX_CHECK(!iotox::routes::make_private_route_member_binding_frame(
                     signed_local.value(), local_set, key(0x22U),
                     wrong_peer_inventory,
                     primary.lower, auxiliary.lower, local_authority,
                     local_identity.value(), sodium.value(), 302U).ok());

    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("private route inventory registry fences epochs forks and authority loss") {
    static std::atomic<unsigned> sequence{0U};
    const auto root = std::filesystem::temp_directory_path() /
        ("iotox-private-route-registry-" + std::to_string(::getpid()) + "-" +
         std::to_string(sequence.fetch_add(1U)));
    std::filesystem::create_directories(root);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto local_identity = iotox::security::DeviceIdentity::load_or_create(
        root / "local.identity", sodium.value(), true);
    auto remote_identity = iotox::security::DeviceIdentity::load_or_create(
        root / "remote.identity", sodium.value(), true);
    IOTOX_CHECK(local_identity.ok());
    IOTOX_CHECK(remote_identity.ok());

    iotox::routes::RouteSet remote_set;
    remote_set.generation = 9U;
    remote_set.stable_device_principal =
        remote_identity.value().public_key();
    remote_set.coordinator_tox_public_key = key(0xeeU);
    remote_set.members = {
        {key(0xddU), iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 2U, 0U},
        {key(0xeeU), iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
    };

    const auto make_authority = [&](
        const iotox::protocol::PeerSessionSnapshot &session,
        const iotox::security::SigningPublicKey &principal) {
        iotox::security::PeerAuthoritySnapshot authority;
        authority.friend_number = session.friend_number;
        authority.transport_public_key = session.public_key;
        authority.online_epoch = session.online_epoch;
        authority.connected = true;
        authority.feature_negotiated = true;
        authority.remote_authorized = true;
        authority.remote_principal = principal;
        auto digest = iotox::security::authority_session_transcript_digest(
            session, sodium.value());
        IOTOX_CHECK(digest.ok());
        authority.session_transcript_digest = digest.value();
        return authority;
    };

    const auto epoch_three = confirmed_pair(3U);
    const auto local_authority = make_authority(
        epoch_three.lower, remote_identity.value().public_key());
    const auto remote_authority = make_authority(
        epoch_three.higher, local_identity.value().public_key());
    auto signed_remote = iotox::routes::sign_route_set(
        remote_set, remote_identity.value());
    IOTOX_CHECK(signed_remote.ok());
    auto frame = iotox::routes::make_private_route_inventory_frame(
        signed_remote.value(), remote_set, epoch_three.higher,
        remote_authority, remote_identity.value(), sodium.value(), 501U);
    IOTOX_CHECK(frame.ok());

    iotox::routes::PrivateRouteInventoryRegistry registry;
    auto accepted = registry.receive(
        frame.value(), epoch_three.lower, local_authority, sodium.value());
    IOTOX_CHECK(accepted.ok());
    IOTOX_CHECK(accepted.value().kind ==
                iotox::routes::PrivateRouteInventoryAdmissionKind::accepted);
    auto replay = registry.receive(
        frame.value(), epoch_three.lower, local_authority, sodium.value());
    IOTOX_CHECK(replay.ok());
    IOTOX_CHECK(replay.value().kind ==
                iotox::routes::PrivateRouteInventoryAdmissionKind::exact_replay);

    auto conflict = frame.value();
    conflict.message_id = 502U;
    IOTOX_CHECK(!registry.receive(
                     conflict, epoch_three.lower, local_authority,
                     sodium.value()).ok());

    auto active = registry.contexts();
    IOTOX_CHECK(active.size() == 1U);
    IOTOX_CHECK(registry.replace_active_edges(
                    {{active.front().session, active.front().authority}},
                    sodium.value()).ok());
    IOTOX_CHECK(registry.contexts().size() == 1U);
    IOTOX_CHECK(registry.replace_active_edges({}, sodium.value()).ok());
    IOTOX_CHECK(registry.contexts().empty());

    const auto epoch_four = confirmed_pair(4U);
    const auto local_authority_four = make_authority(
        epoch_four.lower, remote_identity.value().public_key());
    const auto remote_authority_four = make_authority(
        epoch_four.higher, local_identity.value().public_key());
    auto reconnected = iotox::routes::make_private_route_inventory_frame(
        signed_remote.value(), remote_set, epoch_four.higher,
        remote_authority_four, remote_identity.value(), sodium.value(), 601U);
    IOTOX_CHECK(reconnected.ok());
    IOTOX_CHECK(registry.receive(
                    reconnected.value(), epoch_four.lower,
                    local_authority_four, sodium.value()).ok());

    auto forked_set = remote_set;
    ++forked_set.members.front().maximum_active_work;
    auto signed_fork = iotox::routes::sign_route_set(
        forked_set, remote_identity.value());
    IOTOX_CHECK(signed_fork.ok());
    const auto epoch_five = confirmed_pair(5U);
    const auto local_authority_five = make_authority(
        epoch_five.lower, remote_identity.value().public_key());
    const auto remote_authority_five = make_authority(
        epoch_five.higher, local_identity.value().public_key());
    auto fork_frame = iotox::routes::make_private_route_inventory_frame(
        signed_fork.value(), forked_set, epoch_five.higher,
        remote_authority_five, remote_identity.value(), sodium.value(), 701U);
    IOTOX_CHECK(fork_frame.ok());
    IOTOX_CHECK(!registry.receive(
                     fork_frame.value(), epoch_five.lower,
                     local_authority_five, sodium.value()).ok());

    auto advanced_set = remote_set;
    ++advanced_set.generation;
    auto signed_advanced = iotox::routes::sign_route_set(
        advanced_set, remote_identity.value());
    IOTOX_CHECK(signed_advanced.ok());
    auto advanced_frame = iotox::routes::make_private_route_inventory_frame(
        signed_advanced.value(), advanced_set, epoch_five.higher,
        remote_authority_five, remote_identity.value(), sodium.value(), 702U);
    IOTOX_CHECK(advanced_frame.ok());
    IOTOX_CHECK(registry.receive(
                    advanced_frame.value(), epoch_five.lower,
                    local_authority_five, sodium.value()).ok());

    // toxcore may recycle a deleted friend number for a different transport
    // key. Its new epoch is independent and must not be compared with the old
    // transport association's retained epoch.
    auto replacement_set = remote_set;
    replacement_set.coordinator_tox_public_key = key(0xccU);
    replacement_set.members = {
        {key(0xccU), iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
        {key(0xddU), iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 2U, 0U},
    };
    auto signed_replacement = iotox::routes::sign_route_set(
        replacement_set, remote_identity.value());
    IOTOX_CHECK(signed_replacement.ok());
    const auto recycled_friend = confirmed_pair(
        1U, 0x41U, 0x61U, '1', 'C');
    const auto local_authority_recycled = make_authority(
        recycled_friend.lower, remote_identity.value().public_key());
    const auto remote_authority_recycled = make_authority(
        recycled_friend.higher, local_identity.value().public_key());
    auto replacement_frame = iotox::routes::make_private_route_inventory_frame(
        signed_replacement.value(), replacement_set, recycled_friend.higher,
        remote_authority_recycled, remote_identity.value(), sodium.value(),
        801U);
    IOTOX_CHECK(replacement_frame.ok());
    IOTOX_CHECK(registry.receive(
                    replacement_frame.value(), recycled_friend.lower,
                    local_authority_recycled, sodium.value()).ok());
    IOTOX_CHECK(registry.contexts().size() == 1U);
    IOTOX_CHECK(registry.contexts().front().session.public_key ==
                recycled_friend.lower.public_key);

    const auto snapshot = registry.snapshot();
    IOTOX_CHECK(snapshot.active_primary_edges == 1U);
    IOTOX_CHECK(snapshot.generation_high_water_records == 2U);
    IOTOX_CHECK(snapshot.accepted == 4U);
    IOTOX_CHECK(snapshot.exact_replays == 1U);
    IOTOX_CHECK(snapshot.rejected == 2U);

    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("route binding is stable-principal signed and transcript derived") {
    static std::atomic<unsigned> sequence{0U};
    const auto root = std::filesystem::temp_directory_path() /
        ("iotox-route-binding-" + std::to_string(::getpid()) + "-" +
         std::to_string(sequence.fetch_add(1U)));
    std::filesystem::create_directories(root);
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        root / "device.identity", sodium.value(), true);
    IOTOX_CHECK(identity.ok());
    iotox::routes::RouteSet set;
    set.generation = 9U;
    set.stable_device_principal = identity.value().public_key();
    set.coordinator_tox_public_key = key(0x71U);
    set.members = {
        {key(0x11U), iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
        {key(0x22U), iotox::routes::Role::bulk,
         iotox::routes::ConnectionClass::tcp, 8U, 2U, 0U},
    };
    auto pair = confirmed_pair();
    auto binding = iotox::routes::make_route_binding(
        set, key(0x11U), pair.lower, identity.value(), sodium.value());
    IOTOX_CHECK_MSG(binding.ok(), binding.status().message());
    IOTOX_CHECK(iotox::routes::verify_route_binding(
                    binding.value(), set, pair.higher, sodium.value()).ok());

    auto signed_set = iotox::routes::sign_route_set(set, identity.value());
    IOTOX_CHECK_MSG(signed_set.ok(), signed_set.status().message());
    auto exchange = iotox::routes::make_route_binding_exchange_payload(
        signed_set.value(), set, key(0x11U), pair.lower, identity.value(),
        sodium.value());
    IOTOX_CHECK_MSG(exchange.ok(), exchange.status().message());
    IOTOX_CHECK(exchange.value().size() <= iotox::protocol::kMaxPayloadSize);
    auto verified_exchange =
        iotox::routes::verify_route_binding_exchange_payload(
            exchange.value(), identity.value().public_key(), 9U,
            pair.higher, sodium.value());
    IOTOX_CHECK_MSG(verified_exchange.ok(),
                    verified_exchange.status().message());
    IOTOX_CHECK(verified_exchange.value().route_set == set);
    IOTOX_CHECK(verified_exchange.value().member == set.members.front());
    IOTOX_CHECK(!iotox::routes::verify_route_binding_exchange_payload(
                     exchange.value(), identity.value().public_key(), 10U,
                     pair.higher, sodium.value()).ok());
    auto foreign_principal = identity.value().public_key();
    foreign_principal[0U] ^= 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding_exchange_payload(
                     exchange.value(), foreign_principal, 9U, pair.higher,
                     sodium.value()).ok());

    auto tampered_exchange = exchange.value();
    tampered_exchange[20U] ^= 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding_exchange_payload(
                     tampered_exchange, identity.value().public_key(), 9U,
                     pair.higher, sodium.value()).ok());
    auto noncanonical_exchange = exchange.value();
    noncanonical_exchange.push_back(0U);
    IOTOX_CHECK(!iotox::routes::verify_route_binding_exchange_payload(
                     noncanonical_exchange, identity.value().public_key(), 9U,
                     pair.higher, sodium.value()).ok());

    auto frame = iotox::routes::make_route_binding_frame(
        signed_set.value(), set, key(0x11U), pair.lower, identity.value(),
        sodium.value(), 501U);
    IOTOX_CHECK_MSG(frame.ok(), frame.status().message());
    auto verified_frame = iotox::routes::verify_route_binding_frame(
        frame.value(), identity.value().public_key(), 9U, pair.higher,
        sodium.value());
    IOTOX_CHECK_MSG(verified_frame.ok(), verified_frame.status().message());
    IOTOX_CHECK(verified_frame.value().member == set.members.front());
    auto wrong_envelope = frame.value();
    wrong_envelope.sequence += 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding_frame(
                     wrong_envelope, identity.value().public_key(), 9U,
                     pair.higher, sodium.value()).ok());
    wrong_envelope = frame.value();
    wrong_envelope.correlation_id = 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding_frame(
                     wrong_envelope, identity.value().public_key(), 9U,
                     pair.higher, sodium.value()).ok());
    wrong_envelope = frame.value();
    wrong_envelope.flags = 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding_frame(
                     wrong_envelope, identity.value().public_key(), 9U,
                     pair.higher, sodium.value()).ok());
    wrong_envelope = frame.value();
    wrong_envelope.expiry_unix_ms = 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding_frame(
                     wrong_envelope, identity.value().public_key(), 9U,
                     pair.higher, sodium.value()).ok());
    IOTOX_CHECK(!iotox::routes::make_route_binding_frame(
                     signed_set.value(), set, key(0x11U), pair.lower,
                     identity.value(), sodium.value(), 0U).ok());

    auto maximum_set = set;
    maximum_set.members.clear();
    maximum_set.members.push_back(
        {key(0x11U), iotox::routes::Role::protected_route,
         iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U});
    for (std::uint8_t value = 0x12U; value <= 0x20U; ++value) {
        maximum_set.members.push_back(
            {key(value), iotox::routes::Role::bulk,
             iotox::routes::ConnectionClass::tcp, 8U, 2U, 0U});
    }
    IOTOX_CHECK(maximum_set.members.size() == 16U);
    auto maximum_signed =
        iotox::routes::sign_route_set(maximum_set, identity.value());
    IOTOX_CHECK_MSG(maximum_signed.ok(), maximum_signed.status().message());
    auto maximum_exchange = iotox::routes::make_route_binding_exchange_payload(
        maximum_signed.value(), maximum_set, key(0x11U), pair.lower,
        identity.value(), sodium.value());
    IOTOX_CHECK_MSG(maximum_exchange.ok(), maximum_exchange.status().message());
    IOTOX_CHECK(maximum_exchange.value().size() == 1150U);

    iotox::routes::RouteBindingRegistry registry;
    iotox::routes::RemoteRouteTrust trust;
    trust.stable_device_principal = identity.value().public_key();
    trust.coordinator_tox_public_key = set.coordinator_tox_public_key;
    trust.minimum_generation = 9U;
    trust.primary_online_epoch = 44U;
    IOTOX_CHECK(registry.replace_trust({trust}).ok());
    auto admitted = registry.receive(
        key(0xeeU), 77U, frame.value(), pair.higher, sodium.value());
    IOTOX_CHECK_MSG(admitted.ok(), admitted.status().message());
    IOTOX_CHECK(admitted.value().kind ==
                iotox::routes::RouteBindingAdmissionKind::accepted);
    auto replayed = registry.receive(
        key(0xeeU), 77U, frame.value(), pair.higher, sodium.value());
    IOTOX_CHECK_MSG(replayed.ok(), replayed.status().message());
    IOTOX_CHECK(replayed.value().kind ==
                iotox::routes::RouteBindingAdmissionKind::exact_replay);
    auto conflicting_id = frame.value();
    conflicting_id.message_id += 1U;
    IOTOX_CHECK(!registry.receive(
                     key(0xeeU), 77U, conflicting_id, pair.higher,
                     sodium.value()).ok());
    IOTOX_CHECK(!registry.receive(
                     key(0xedU), 77U, frame.value(), pair.higher,
                     sodium.value()).ok());
    IOTOX_CHECK(!registry.receive(
                     key(0xeeU), 78U, frame.value(), pair.higher,
                     sodium.value()).ok());

    auto next_pair = confirmed_pair(2U, 0x32U, 0x52U);
    auto forked_set = set;
    forked_set.members.back().maximum_active_work += 1U;
    auto forked_signed =
        iotox::routes::sign_route_set(forked_set, identity.value());
    IOTOX_CHECK(forked_signed.ok());
    auto forked_frame = iotox::routes::make_route_binding_frame(
        forked_signed.value(), forked_set, key(0x11U), next_pair.lower,
        identity.value(), sodium.value(), 502U);
    IOTOX_CHECK(forked_frame.ok());
    IOTOX_CHECK(!registry.receive(
                     key(0xeeU), 77U, forked_frame.value(), next_pair.higher,
                     sodium.value()).ok());

    auto next_set = set;
    next_set.generation = 10U;
    auto next_signed =
        iotox::routes::sign_route_set(next_set, identity.value());
    IOTOX_CHECK(next_signed.ok());
    auto next_frame = iotox::routes::make_route_binding_frame(
        next_signed.value(), next_set, key(0x11U), next_pair.lower,
        identity.value(), sodium.value(), 503U);
    IOTOX_CHECK(next_frame.ok());
    auto next_admitted = registry.receive(
        key(0xeeU), 77U, next_frame.value(), next_pair.higher,
        sodium.value());
    IOTOX_CHECK_MSG(next_admitted.ok(), next_admitted.status().message());
    IOTOX_CHECK(next_admitted.value().verified.route_set.generation == 10U);

    auto stale_pair = confirmed_pair(3U, 0x33U, 0x53U);
    auto stale_frame = iotox::routes::make_route_binding_frame(
        signed_set.value(), set, key(0x11U), stale_pair.lower,
        identity.value(), sodium.value(), 504U);
    IOTOX_CHECK(stale_frame.ok());
    IOTOX_CHECK(!registry.receive(
                     key(0xeeU), 77U, stale_frame.value(), stale_pair.higher,
                     sodium.value()).ok());

    auto registry_snapshot = registry.snapshot();
    IOTOX_CHECK(registry_snapshot.trusted_primary_routes == 1U);
    IOTOX_CHECK(registry_snapshot.accepted_workers == 1U);
    IOTOX_CHECK(registry_snapshot.accepted == 2U);
    IOTOX_CHECK(registry_snapshot.exact_replays == 1U);
    IOTOX_CHECK(registry_snapshot.rejected >= 4U);
    IOTOX_CHECK(!registry.retire_worker(key(0xeeU), 78U).ok());
    IOTOX_CHECK(registry.retire_worker(key(0xeeU), 77U).ok());
    IOTOX_CHECK(registry.snapshot().accepted_workers == 0U);

    auto current_third_frame = iotox::routes::make_route_binding_frame(
        next_signed.value(), next_set, key(0x11U), stale_pair.lower,
        identity.value(), sodium.value(), 505U);
    IOTOX_CHECK(current_third_frame.ok());
    IOTOX_CHECK(registry.receive(
                    key(0xeeU), 88U, current_third_frame.value(),
                    stale_pair.higher, sodium.value()).ok());
    IOTOX_CHECK(registry.snapshot().accepted_workers == 1U);
    trust.primary_online_epoch = 45U;
    trust.minimum_generation = 1U;
    IOTOX_CHECK(registry.replace_trust({trust}).ok());
    IOTOX_CHECK(registry.snapshot().accepted_workers == 0U);
    IOTOX_CHECK(registry.receive(
                    key(0xeeU), 88U, stale_frame.value(), stale_pair.higher,
                    sodium.value()).status().code() ==
                iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(registry.replace_trust({}).ok());
    IOTOX_CHECK(registry.snapshot().trusted_primary_routes == 0U);

    auto tampered = binding.value();
    tampered[120U] ^= 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding(
                     tampered, set, pair.higher, sodium.value()).ok());
    auto stale = set;
    stale.generation += 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding(
                     binding.value(), stale, pair.higher, sodium.value()).ok());
    pair.higher.peer_confirmation_message_id += 1U;
    IOTOX_CHECK(!iotox::routes::verify_route_binding(
                     binding.value(), set, pair.higher, sodium.value()).ok());
    pair.lower.application_ready = false;
    IOTOX_CHECK(!iotox::routes::make_route_binding(
                     set, key(0x11U), pair.lower, identity.value(),
                     sodium.value()).ok());
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);
}
