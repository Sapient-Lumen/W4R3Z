#include "iotox/route_inventory.hpp"
#include "iotox/state_store.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <filesystem>
#include <unistd.h>

namespace {

using namespace iotox;

security::SigningSeed seed(std::uint8_t value) {
    security::SigningSeed result{};
    result.fill(value);
    return result;
}

routes::ToxPublicKey tox_key(std::uint8_t value) {
    routes::ToxPublicKey result{};
    result.fill(value);
    return result;
}

struct Fixture {
    security::Sodium sodium;
    security::DeviceIdentity identity;
    std::filesystem::path root;

    Fixture() {
        auto loaded = security::Sodium::load();
        if (!loaded) throw std::runtime_error(loaded.status().message());
        sodium = std::move(loaded).value();
        root = std::filesystem::temp_directory_path() /
               ("iotox-route-inventory-" + std::to_string(::getpid()));
        std::filesystem::remove_all(root);
        std::filesystem::create_directories(root);
        auto keys = sodium.signing_keypair_from_seed(seed(0x31U));
        if (!keys) throw std::runtime_error(keys.status().message());
        // Write the established fixed identity format to exercise the real signer.
        std::array<std::uint8_t, security::kDeviceIdentityFileBytes> bytes{};
        const std::array<std::uint8_t, 8U> magic = {'I','O','T','O','X','I','D','1'};
        std::copy(magic.begin(), magic.end(), bytes.begin());
        bytes[8U] = 1U;
        bytes[9U] = 1U;
        const auto identity_seed = seed(0x31U);
        std::copy(identity_seed.begin(), identity_seed.end(), bytes.begin() + 16U);
        std::copy(keys.value().public_key().begin(), keys.value().public_key().end(),
                  bytes.begin() + 48U);
        const auto stored = StateStore::write_atomic(root / "device.identity", bytes);
        if (!stored.ok()) throw std::runtime_error(stored.message());
        auto opened = security::DeviceIdentity::load(root / "device.identity", sodium);
        if (!opened) throw std::runtime_error(opened.status().message());
        identity = std::move(opened).value();
    }

    ~Fixture() { std::filesystem::remove_all(root); }

    routes::RouteSet route_set() const {
        routes::RouteSet set;
        set.generation = 7U;
        set.stable_device_principal = identity.public_key();
        set.coordinator_tox_public_key = tox_key(0x71U);
        set.members = {
            {tox_key(0x22U), routes::Role::bulk,
             routes::ConnectionClass::tcp, 8U, 2U, 0U},
            {tox_key(0x11U), routes::Role::protected_route,
             routes::ConnectionClass::tcp, 1U, 1U, 0U},
        };
        return set;
    }
};

}  // namespace

IOTOX_TEST("signed route inventory is canonical and stable-principal bound") {
    Fixture fixture;
    auto artifact = routes::sign_route_set(fixture.route_set(), fixture.identity);
    IOTOX_CHECK_MSG(artifact.ok(), artifact.status().message());
    auto verified = routes::verify_route_set(
        artifact.value(), fixture.identity.public_key(), 7U, fixture.sodium);
    IOTOX_CHECK_MSG(verified.ok(), verified.status().message());
    IOTOX_CHECK(verified.value().members.front().tox_public_key == tox_key(0x11U));

    auto stale = routes::verify_route_set(
        artifact.value(), fixture.identity.public_key(), 8U, fixture.sodium);
    IOTOX_CHECK(!stale.ok());

    auto foreign_keys = fixture.sodium.signing_keypair_from_seed(seed(0x51U));
    IOTOX_CHECK(foreign_keys.ok());
    auto foreign = routes::verify_route_set(
        artifact.value(), foreign_keys.value().public_key(), 0U, fixture.sodium);
    IOTOX_CHECK(!foreign.ok());

    artifact.value()[100U] ^= 0x01U;
    auto tampered = routes::verify_route_set(
        artifact.value(), fixture.identity.public_key(), 0U, fixture.sodium);
    IOTOX_CHECK(!tampered.ok());
}

IOTOX_TEST("route-set v2 signs exact member network classes without widening v1") {
    Fixture fixture;
    auto v2 = fixture.route_set();
    v2.format_version = routes::kRouteSetFormatVersionV2;
    v2.coordinator_tox_public_key = tox_key(0x11U);
    v2.members[0U].network_class = routes::NetworkClass::tox_tor;
    v2.members[1U].network_class = routes::NetworkClass::tox_native;
    auto artifact = routes::sign_route_set(v2, fixture.identity);
    IOTOX_CHECK_MSG(artifact.ok(), artifact.status().message());
    IOTOX_CHECK(artifact.value()[7U] == '2');
    IOTOX_CHECK(artifact.value()[8U] == routes::kRouteSetFormatVersionV2);
    auto verified = routes::verify_route_set(
        artifact.value(), fixture.identity.public_key(), 7U,
        fixture.sodium);
    IOTOX_CHECK_MSG(verified.ok(), verified.status().message());
    IOTOX_CHECK(verified.value().format_version ==
                routes::kRouteSetFormatVersionV2);
    IOTOX_CHECK(verified.value().members.front().network_class ==
                routes::NetworkClass::tox_native);
    IOTOX_CHECK(verified.value().members.back().network_class ==
                routes::NetworkClass::tox_tor);

    auto foreign_coordinator = v2;
    foreign_coordinator.coordinator_tox_public_key = tox_key(0x71U);
    IOTOX_CHECK(!routes::sign_route_set(
        foreign_coordinator, fixture.identity).ok());

    auto v1_with_class = fixture.route_set();
    v1_with_class.members.front().network_class =
        routes::NetworkClass::tox_native;
    IOTOX_CHECK(!routes::sign_route_set(
        v1_with_class, fixture.identity).ok());
    auto v2_without_class = fixture.route_set();
    v2_without_class.format_version = routes::kRouteSetFormatVersionV2;
    v2_without_class.coordinator_tox_public_key = tox_key(0x11U);
    IOTOX_CHECK(!routes::sign_route_set(
        v2_without_class, fixture.identity).ok());
}

IOTOX_TEST("route inventory rejects duplicate keys and foreign signing principal") {
    Fixture fixture;
    auto duplicated = fixture.route_set();
    duplicated.members[1U].tox_public_key = duplicated.members[0U].tox_public_key;
    IOTOX_CHECK(!routes::sign_route_set(duplicated, fixture.identity).ok());
    IOTOX_CHECK(!routes::Coordinator::create(duplicated).ok());

    auto foreign = fixture.route_set();
    foreign.stable_device_principal.fill(0x91U);
    IOTOX_CHECK(!routes::sign_route_set(foreign, fixture.identity).ok());
}

IOTOX_TEST("coordinator fails closed on unknown duplicate stale foreign and downgrade routes") {
    Fixture fixture;
    auto created = routes::Coordinator::create(fixture.route_set(), 1000U);
    IOTOX_CHECK(created.ok());
    auto coordinator = std::move(created).value();
    const auto protected_key = tox_key(0x11U);
    const auto unknown_key = tox_key(0x99U);

    IOTOX_CHECK(!coordinator.begin_connecting(unknown_key, 1U).ok());
    IOTOX_CHECK(coordinator.begin_connecting(protected_key, 1U).ok());
    IOTOX_CHECK(!coordinator.begin_connecting(protected_key, 2U).ok());

    routes::RouteProof proof;
    proof.tox_public_key = protected_key;
    proof.stable_device_principal = fixture.identity.public_key();
    proof.route_set_generation = 6U;
    proof.route_protocol_version = routes::kRouteProtocolVersion;
    proof.connection_class = routes::ConnectionClass::tcp;
    proof.worker_id = 1U;
    proof.transcript_confirmed = true;
    IOTOX_CHECK(!coordinator.authenticate(proof).ok());

    proof.route_set_generation = 7U;
    proof.stable_device_principal.fill(0x55U);
    IOTOX_CHECK(!coordinator.authenticate(proof).ok());
    proof.stable_device_principal = fixture.identity.public_key();
    proof.route_protocol_version = 0U;
    IOTOX_CHECK(!coordinator.authenticate(proof).ok());
    proof.route_protocol_version = routes::kRouteProtocolVersion;
    proof.transcript_confirmed = false;
    IOTOX_CHECK(!coordinator.authenticate(proof).ok());
    proof.transcript_confirmed = true;
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
    IOTOX_CHECK(coordinator.mark_ready(protected_key, 1U).ok());
    IOTOX_CHECK(coordinator.authentication_lost(
                    protected_key, 1U).ok());
    auto lost = coordinator.snapshot();
    IOTOX_CHECK(lost.members.front().lifecycle ==
                routes::Lifecycle::connecting);
    IOTOX_CHECK(lost.members.front().restarts == 0U);
    IOTOX_CHECK(lost.members.front().last_failure ==
                routes::Failure::authentication);
    IOTOX_CHECK(coordinator.authentication_lost(
                    protected_key, 1U).ok());
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
    IOTOX_CHECK(coordinator.mark_ready(protected_key, 1U).ok());
}

IOTOX_TEST("coordinator enforces signed budgets and bounded recovery") {
    Fixture fixture;
    auto created = routes::Coordinator::create(fixture.route_set());
    IOTOX_CHECK(created.ok());
    auto coordinator = std::move(created).value();
    const auto bulk_key = tox_key(0x22U);
    IOTOX_CHECK(coordinator.begin_connecting(bulk_key, 44U).ok());
    routes::RouteProof proof{
        bulk_key, fixture.identity.public_key(), 7U,
        routes::kRouteProtocolVersion, routes::ConnectionClass::tcp, 44U, true};
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
    IOTOX_CHECK(coordinator.mark_ready(bulk_key, 44U).ok());
    IOTOX_CHECK(coordinator.admit_work(bulk_key, 44U, 8U).ok());
    IOTOX_CHECK(!coordinator.admit_work(bulk_key, 44U, 1U).ok());
    IOTOX_CHECK(coordinator.release_work(bulk_key, 44U, 3U).ok());
    IOTOX_CHECK(coordinator.begin_recovery(
        bulk_key, 44U, routes::Failure::connection).ok());
    auto snapshot = coordinator.snapshot();
    IOTOX_CHECK(snapshot.members[1U].lifecycle == routes::Lifecycle::recovering);
    IOTOX_CHECK(snapshot.members[1U].restarts == 1U);
    IOTOX_CHECK(snapshot.members[1U].admitted_work == 0U);
    IOTOX_CHECK(snapshot.members[1U].last_failure == routes::Failure::connection);
    IOTOX_CHECK(coordinator.begin_connecting(bulk_key, 45U).ok());
    proof.worker_id = 45U;
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
    IOTOX_CHECK(coordinator.mark_ready(bulk_key, 45U).ok());
    IOTOX_CHECK(coordinator.begin_recovery(
        bulk_key, 45U, routes::Failure::transport).ok());
    IOTOX_CHECK(coordinator.begin_connecting(bulk_key, 46U).ok());
    proof.worker_id = 46U;
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
    IOTOX_CHECK(coordinator.mark_ready(bulk_key, 46U).ok());
    IOTOX_CHECK(!coordinator.begin_recovery(
        bulk_key, 46U, routes::Failure::transport).ok());
    snapshot = coordinator.snapshot();
    IOTOX_CHECK(snapshot.members[1U].lifecycle == routes::Lifecycle::unavailable);
    IOTOX_CHECK(snapshot.members[1U].last_failure ==
                routes::Failure::restart_exhausted);
    IOTOX_CHECK(!coordinator.begin_connecting(bulk_key, 47U).ok());
}

IOTOX_TEST("coordinator rejects expired and wrong-class members") {
    Fixture fixture;
    auto set = fixture.route_set();
    set.members[0U].expires_unix_ms = 999U;
    IOTOX_CHECK(!routes::Coordinator::create(set).ok());
    auto created = routes::Coordinator::create(set, 1000U);
    IOTOX_CHECK(created.ok());
    auto coordinator = std::move(created).value();
    const auto bulk_key = tox_key(0x22U);
    IOTOX_CHECK(coordinator.begin_connecting(bulk_key, 8U).ok());
    routes::RouteProof proof{
        bulk_key, fixture.identity.public_key(), 7U,
        routes::kRouteProtocolVersion, routes::ConnectionClass::udp, 8U, true};
    IOTOX_CHECK(!coordinator.authenticate(proof).ok());
    proof.connection_class = routes::ConnectionClass::tcp;
    IOTOX_CHECK(!coordinator.authenticate(proof).ok());
}

IOTOX_TEST("coordinator authenticates the exact v2 signed network class") {
    Fixture fixture;
    auto set = fixture.route_set();
    set.format_version = routes::kRouteSetFormatVersionV2;
    set.coordinator_tox_public_key = tox_key(0x11U);
    for (auto &member : set.members) {
        member.network_class = routes::NetworkClass::tox_native;
    }
    auto created = routes::Coordinator::create(set);
    IOTOX_CHECK(created.ok());
    auto coordinator = std::move(created).value();
    const auto protected_key = tox_key(0x11U);
    IOTOX_CHECK(coordinator.begin_connecting(protected_key, 19U).ok());
    routes::RouteProof proof;
    proof.tox_public_key = protected_key;
    proof.stable_device_principal = fixture.identity.public_key();
    proof.route_set_generation = 7U;
    proof.route_protocol_version = routes::kRouteProtocolVersion;
    proof.connection_class = routes::ConnectionClass::tcp;
    proof.worker_id = 19U;
    proof.transcript_confirmed = true;
    proof.network_class = routes::NetworkClass::tox_tor;
    IOTOX_CHECK(!coordinator.authenticate(proof).ok());
    proof.network_class = routes::NetworkClass::tox_native;
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
}

IOTOX_TEST("route coordinator rendering is bounded and content free") {
    Fixture fixture;
    auto created = routes::Coordinator::create(fixture.route_set());
    IOTOX_CHECK(created.ok());
    auto rendered = routes::render_coordinator_snapshot(
        created.value().snapshot(), fixture.sodium);
    IOTOX_CHECK(rendered.ok());
    IOTOX_CHECK(rendered.value().find("mode=coordinated\n") == 0U);
    IOTOX_CHECK(rendered.value().find("route-set-generation=7\n") !=
                std::string::npos);
    IOTOX_CHECK(rendered.value().find("role=protected") != std::string::npos);
    IOTOX_CHECK(rendered.value().find("role=bulk") != std::string::npos);
    IOTOX_CHECK(rendered.value().find("network-class=unspecified") !=
                std::string::npos);
    IOTOX_CHECK(rendered.value().find("lifecycle=configured") !=
                std::string::npos);
    IOTOX_CHECK(rendered.value().find(
                    "restarts=0 restart-budget=2 restart-budget-remaining=2") !=
                std::string::npos);
    IOTOX_CHECK(rendered.value().find("last-failure=none") !=
                std::string::npos);
}

IOTOX_TEST("route rendering distinguishes signed and remaining restart budgets") {
    Fixture fixture;
    auto created = routes::Coordinator::create(fixture.route_set());
    IOTOX_CHECK(created.ok());
    auto &coordinator = created.value();
    const auto bulk_key = tox_key(0x22U);
    IOTOX_CHECK(coordinator.begin_connecting(bulk_key, 17U).ok());
    IOTOX_CHECK(coordinator.begin_recovery(
                    bulk_key, 17U, routes::Failure::transport)
                    .ok());
    auto rendered = routes::render_coordinator_snapshot(
        coordinator.snapshot(), fixture.sodium);
    IOTOX_CHECK(rendered.ok());
    IOTOX_CHECK(rendered.value().find(
                    "restarts=1 restart-budget=2 restart-budget-remaining=1") !=
                std::string::npos);
}
