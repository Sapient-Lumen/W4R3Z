#include "iotox/protocol/delegation.hpp"
#include "iotox/security/authority.hpp"
#include "test_harness.hpp"

#include <algorithm>
#include <chrono>
#include <filesystem>
#include <string>
#include <system_error>
#include <unistd.h>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        const auto ticks =
            std::chrono::steady_clock::now().time_since_epoch().count();
        path_ = std::filesystem::temp_directory_path() /
                ("iotox-delegation-test-" + std::to_string(::getpid()) + "-" +
                 std::to_string(ticks));
        std::filesystem::create_directories(path_);
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

iotox::security::SigningSeed signing_seed(std::uint8_t first) {
    iotox::security::SigningSeed output{};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        output[index] = static_cast<std::uint8_t>(first + index);
    }
    return output;
}

iotox::security::AuthorityRecordBytes fixture_record() {
    using namespace iotox::security;
    AuthorityRecord record;
    record.action = AuthorityAction::grant;
    record.role = PrincipalRole::viewer;
    record.sequence = 2U;
    record.ownership_epoch = 1U;
    record.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry);
    record.device.fill(0x11U);
    record.issuer.fill(0x22U);
    record.subject.fill(0x33U);
    record.previous_digest.fill(0x44U);
    auto body = encode_authority_record_body(record);
    IOTOX_CHECK(body.ok());
    AuthorityRecordBytes bytes{};
    std::copy(body.value().begin(), body.value().end(), bytes.begin());
    std::fill(bytes.begin() + static_cast<std::ptrdiff_t>(kAuthorityRecordBodyBytes),
              bytes.end(), 0x55U);
    return bytes;
}

void bind_local_authority_head(
    iotox::security::PeerAuthoritySnapshot &peer,
    const iotox::security::AuthoritySnapshot &authority) {
    peer.local_authority_format = authority.format;
    peer.local_authority_epoch = authority.ownership_epoch;
    peer.local_authority_sequence = authority.sequence;
    peer.local_authority_tail_digest = authority.tail_digest;
}

}  // namespace

IOTOX_TEST("remote delegation request wraps one exact signed ledger record") {
    iotox::protocol::DelegationRequest request;
    request.signed_record = fixture_record();
    auto encoded = iotox::protocol::encode_delegation_request(request);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() ==
                iotox::protocol::kDelegationRequestBytes);
    auto decoded = iotox::protocol::decode_delegation_request(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == request);

    auto reserved = encoded.value();
    reserved[7U] = 1U;
    IOTOX_CHECK(!iotox::protocol::decode_delegation_request(reserved));
    auto malformed_record = encoded.value();
    malformed_record[8U] = 0U;
    IOTOX_CHECK(!iotox::protocol::decode_delegation_request(malformed_record));
}

IOTOX_TEST("remote delegation result freezes outcome and resulting ledger head") {
    iotox::protocol::DelegationResult result;
    result.outcome = iotox::protocol::DelegationOutcome::applied;
    result.ownership_epoch = 7U;
    result.authority_sequence = 19U;
    result.authority_tail_digest.fill(0xA5U);
    auto encoded = iotox::protocol::encode_delegation_result(result);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto decoded = iotox::protocol::decode_delegation_result(encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == result);

    auto reserved = encoded.value();
    reserved[6U] = 1U;
    IOTOX_CHECK(!iotox::protocol::decode_delegation_result(reserved));
    auto unknown = encoded.value();
    unknown[5U] = 0xffU;
    IOTOX_CHECK(!iotox::protocol::decode_delegation_result(unknown));
}

IOTOX_TEST("remote self delegation binds owner device controller and exact head") {
    using namespace iotox;
    using namespace iotox::security;
    AuthoritySnapshot local;
    local.initialized = true;
    local.device.fill(0x11U);
    local.ownership_epoch = 1U;
    local.sequence = 1U;
    local.tail_digest.fill(0x44U);
    PeerAuthoritySnapshot peer;
    peer.connected = true;
    peer.feature_negotiated = true;
    peer.remote_authorized = true;
    peer.remote_role = PrincipalRole::owner;
    peer.remote_capabilities = kAllCapabilities;
    peer.remote_principal.fill(0x22U);
    peer.peer_verifier_device.fill(0x33U);
    bind_local_authority_head(peer, local);
    auto decoded = decode_authority_record(fixture_record());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(protocol::validate_remote_self_delegation(
                    decoded.value(), local, peer).ok());

    auto wrong_subject = decoded.value();
    wrong_subject.subject.fill(0x99U);
    IOTOX_CHECK(!protocol::validate_remote_self_delegation(
                    wrong_subject, local, peer).ok());
    auto owner_grant = decoded.value();
    owner_grant.role = PrincipalRole::owner;
    IOTOX_CHECK(!protocol::validate_remote_self_delegation(
                    owner_grant, local, peer).ok());
    auto stale = decoded.value();
    stale.sequence = 3U;
    IOTOX_CHECK(protocol::validate_remote_self_delegation(
                    stale, local, peer).code() == ErrorCode::protocol_error);
    peer.remote_authorized = false;
    IOTOX_CHECK(protocol::validate_remote_self_delegation(
                    decoded.value(), local, peer).code() ==
                ErrorCode::unavailable);
}

IOTOX_TEST("remote self delegation applies once denies conflicts and survives restart") {
    using namespace iotox;
    using namespace iotox::protocol;
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto device_seed = signing_seed(7U);
    auto owner_seed = signing_seed(47U);
    auto controller_seed = signing_seed(87U);
    auto successor_seed = signing_seed(127U);
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    auto controller = sodium.value().signing_keypair_from_seed(controller_seed);
    auto successor = sodium.value().signing_keypair_from_seed(successor_seed);
    IOTOX_CHECK(device.ok() && owner.ok() && controller.ok() && successor.ok());
    TemporaryDirectory temporary;
    AuthorityLedger::Config config;
    config.path = temporary.path() / "authority.ledger";
    auto ledger = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(ledger.ok());

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAllCapabilities;
    bootstrap.issuer = owner.value().public_key();
    bootstrap.subject = owner.value().public_key();
    auto bootstrap_body = ledger.value()->prepare(bootstrap);
    IOTOX_CHECK(bootstrap_body.ok());
    auto bootstrap_record = sign_authority_record_body(
        bootstrap_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(bootstrap_record.ok());
    IOTOX_CHECK(ledger.value()->append(bootstrap_record.value()).ok());

    const AuthoritySnapshot head = ledger.value()->snapshot();
    AuthorityRecord grant;
    grant.action = AuthorityAction::grant;
    grant.role = PrincipalRole::automation;
    grant.sequence = head.sequence + 1U;
    grant.ownership_epoch = head.ownership_epoch;
    grant.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry);
    grant.device = head.device;
    grant.issuer = owner.value().public_key();
    grant.subject = controller.value().public_key();
    grant.previous_digest = head.tail_digest;
    auto grant_body = encode_authority_record_body(grant);
    IOTOX_CHECK(grant_body.ok());
    auto grant_record = sign_authority_record_body(
        grant_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(grant_record.ok());

    PeerAuthoritySnapshot peer;
    peer.connected = true;
    peer.feature_negotiated = true;
    peer.remote_role = PrincipalRole::owner;
    peer.remote_capabilities = kAllCapabilities;
    peer.remote_principal = owner.value().public_key();
    peer.peer_verifier_device = controller.value().public_key();
    bind_local_authority_head(peer, head);
    auto denied = apply_remote_self_delegation(
        grant_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(denied.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!denied.ledger_changed);
    IOTOX_CHECK(ledger.value()->snapshot().sequence == head.sequence);

    peer.remote_authorized = true;
    bind_local_authority_head(peer, head);
    auto applied = apply_remote_self_delegation(
        grant_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(applied.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(applied.ledger_changed);
    const AuthoritySnapshot delegated = ledger.value()->snapshot();
    IOTOX_CHECK(delegated.sequence == head.sequence + 1U);
    auto principal = ledger.value()->principal(controller.value().public_key());
    IOTOX_CHECK(principal.ok());
    IOTOX_CHECK(principal.value().active);
    IOTOX_CHECK(principal.value().role == PrincipalRole::automation);

    peer.remote_authorized = false;
    peer.remote_principal.fill(0U);
    auto duplicate = apply_remote_self_delegation(
        grant_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(duplicate.outcome == DelegationOutcome::exact_duplicate);
    IOTOX_CHECK(!duplicate.ledger_changed);
    IOTOX_CHECK(ledger.value()->snapshot().sequence == delegated.sequence);

    AuthorityRecord stale = grant;
    stale.sequence = delegated.sequence + 2U;
    stale.previous_digest = delegated.tail_digest;
    auto stale_body = encode_authority_record_body(stale);
    IOTOX_CHECK(stale_body.ok());
    auto stale_record = sign_authority_record_body(
        stale_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(stale_record.ok());
    peer.remote_authorized = true;
    peer.remote_principal = owner.value().public_key();
    bind_local_authority_head(peer, delegated);
    auto conflict = apply_remote_self_delegation(
        stale_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(conflict.outcome == DelegationOutcome::conflict);
    IOTOX_CHECK(!conflict.ledger_changed);

    ledger.value().reset();
    auto reopened = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(reopened.ok(), reopened.status().message());
    IOTOX_CHECK(reopened.value()->snapshot().sequence == delegated.sequence);
    auto replay = apply_remote_self_delegation(
        grant_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(replay.outcome == DelegationOutcome::exact_duplicate);
    IOTOX_CHECK(!replay.ledger_changed);

    peer.remote_authorized = true;
    peer.remote_principal = owner.value().public_key();
    const AuthoritySnapshot revoke_head = reopened.value()->snapshot();
    bind_local_authority_head(peer, revoke_head);
    AuthorityRecord revoke;
    revoke.action = AuthorityAction::revoke;
    revoke.role = PrincipalRole::none;
    revoke.sequence = revoke_head.sequence + 1U;
    revoke.ownership_epoch = revoke_head.ownership_epoch;
    revoke.device = revoke_head.device;
    revoke.issuer = owner.value().public_key();
    revoke.subject = controller.value().public_key();
    revoke.previous_digest = revoke_head.tail_digest;
    AuthorityRecord revoke_missing = revoke;
    revoke_missing.subject.fill(0xA5U);
    auto revoke_missing_body = encode_authority_record_body(revoke_missing);
    IOTOX_CHECK(revoke_missing_body.ok());
    auto revoke_missing_record = sign_authority_record_body(
        revoke_missing_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(revoke_missing_record.ok());
    auto missing_denied = apply_remote_owner_mutation(
        revoke_missing_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(missing_denied.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!missing_denied.ledger_changed);
    auto revoke_body = encode_authority_record_body(revoke);
    IOTOX_CHECK(revoke_body.ok());
    auto revoke_record = sign_authority_record_body(
        revoke_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(revoke_record.ok());
    auto revoked = apply_remote_owner_mutation(
        revoke_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(revoked.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(revoked.ledger_changed);
    auto revoked_principal = reopened.value()->principal(
        controller.value().public_key());
    IOTOX_CHECK(revoked_principal.ok());
    IOTOX_CHECK(!revoked_principal.value().active);

    peer.remote_authorized = false;
    peer.remote_principal.fill(0U);
    auto duplicate_revoke = apply_remote_owner_mutation(
        revoke_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(duplicate_revoke.outcome ==
                DelegationOutcome::exact_duplicate);
    IOTOX_CHECK(!duplicate_revoke.ledger_changed);

    AuthorityRecord revoke_inactive = revoke;
    revoke_inactive.sequence = reopened.value()->snapshot().sequence + 1U;
    revoke_inactive.previous_digest = reopened.value()->snapshot().tail_digest;
    auto revoke_inactive_body = encode_authority_record_body(revoke_inactive);
    IOTOX_CHECK(revoke_inactive_body.ok());
    auto revoke_inactive_record = sign_authority_record_body(
        revoke_inactive_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(revoke_inactive_record.ok());
    peer.remote_authorized = true;
    peer.remote_principal = owner.value().public_key();
    bind_local_authority_head(peer, reopened.value()->snapshot());
    auto inactive_denied = apply_remote_owner_mutation(
        revoke_inactive_record.value(), *reopened.value(), peer,
        sodium.value());
    IOTOX_CHECK(inactive_denied.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!inactive_denied.ledger_changed);

    AuthorityRecord revoke_owner = revoke;
    revoke_owner.sequence = reopened.value()->snapshot().sequence + 1U;
    revoke_owner.previous_digest = reopened.value()->snapshot().tail_digest;
    revoke_owner.subject = owner.value().public_key();
    auto revoke_owner_body = encode_authority_record_body(revoke_owner);
    IOTOX_CHECK(revoke_owner_body.ok());
    auto revoke_owner_record = sign_authority_record_body(
        revoke_owner_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(revoke_owner_record.ok());
    peer.remote_authorized = true;
    peer.remote_principal = owner.value().public_key();
    bind_local_authority_head(peer, reopened.value()->snapshot());
    auto owner_denied = apply_remote_owner_mutation(
        revoke_owner_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(owner_denied.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!owner_denied.ledger_changed);

    const AuthoritySnapshot nomination_head = reopened.value()->snapshot();
    bind_local_authority_head(peer, nomination_head);
    AuthorityRecord nomination;
    nomination.action = AuthorityAction::grant;
    nomination.role = PrincipalRole::owner;
    nomination.sequence = nomination_head.sequence + 1U;
    nomination.ownership_epoch = nomination_head.ownership_epoch;
    nomination.capabilities = kAllCapabilities;
    nomination.device = nomination_head.device;
    nomination.issuer = owner.value().public_key();
    nomination.subject = successor.value().public_key();
    nomination.previous_digest = nomination_head.tail_digest;

    AuthorityRecord same_owner_nomination = nomination;
    same_owner_nomination.subject = owner.value().public_key();
    auto same_owner_body = encode_authority_record_body(same_owner_nomination);
    IOTOX_CHECK(same_owner_body.ok());
    auto same_owner_record = sign_authority_record_body(
        same_owner_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(same_owner_record.ok());
    auto same_owner_denied = apply_remote_owner_mutation(
        same_owner_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(same_owner_denied.outcome == DelegationOutcome::denied);

    auto nomination_body = encode_authority_record_body(nomination);
    IOTOX_CHECK(nomination_body.ok());
    auto nomination_record = sign_authority_record_body(
        nomination_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(nomination_record.ok());
    auto nominated = apply_remote_owner_mutation(
        nomination_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(nominated.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(nominated.ledger_changed);
    IOTOX_CHECK(reopened.value()->snapshot().nominated_successor ==
                successor.value().public_key());

    peer.remote_authorized = false;
    peer.remote_principal.fill(0U);
    auto duplicate_nomination = apply_remote_owner_mutation(
        nomination_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(duplicate_nomination.outcome ==
                DelegationOutcome::exact_duplicate);
    IOTOX_CHECK(!duplicate_nomination.ledger_changed);

    const AuthoritySnapshot transition_head = reopened.value()->snapshot();
    AuthorityRecord transition;
    transition.action = AuthorityAction::epoch_transition;
    transition.role = PrincipalRole::owner;
    transition.sequence = 1U;
    transition.ownership_epoch = transition_head.ownership_epoch + 1U;
    transition.capabilities = kAllCapabilities;
    transition.device = transition_head.device;
    transition.issuer = successor.value().public_key();
    transition.subject = successor.value().public_key();
    transition.previous_digest = transition_head.tail_digest;
    auto transition_body = encode_authority_record_body(transition);
    IOTOX_CHECK(transition_body.ok());
    auto transition_record = sign_authority_record_body(
        transition_body.value(), successor.value().secret_key(), sodium.value());
    IOTOX_CHECK(transition_record.ok());

    peer.remote_authorized = true;
    peer.remote_principal = owner.value().public_key();
    bind_local_authority_head(peer, transition_head);
    auto old_owner_denied = apply_remote_owner_mutation(
        transition_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(old_owner_denied.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!old_owner_denied.ledger_changed);

    AuthorityRecord wrong_tail = transition;
    wrong_tail.previous_digest[0U] ^= 0x80U;
    auto wrong_tail_body = encode_authority_record_body(wrong_tail);
    IOTOX_CHECK(wrong_tail_body.ok());
    auto wrong_tail_record = sign_authority_record_body(
        wrong_tail_body.value(), successor.value().secret_key(), sodium.value());
    IOTOX_CHECK(wrong_tail_record.ok());
    peer.remote_principal = successor.value().public_key();
    bind_local_authority_head(peer, transition_head);
    auto wrong_tail_denied = apply_remote_owner_mutation(
        wrong_tail_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(wrong_tail_denied.outcome == DelegationOutcome::conflict);

    auto transitioned = apply_remote_owner_mutation(
        transition_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(transitioned.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(transitioned.ledger_changed);
    IOTOX_CHECK(reopened.value()->snapshot().ownership_epoch == 2U);
    IOTOX_CHECK(reopened.value()->snapshot().sequence == 1U);
    IOTOX_CHECK(reopened.value()->snapshot().principals.size() == 1U);
    IOTOX_CHECK(reopened.value()->authorized(
        successor.value().public_key(), kAllCapabilities));
    IOTOX_CHECK(!reopened.value()->authorized(owner.value().public_key(), 0U));

    peer.remote_authorized = false;
    peer.remote_principal.fill(0U);
    auto duplicate_transition = apply_remote_owner_mutation(
        transition_record.value(), *reopened.value(), peer, sodium.value());
    IOTOX_CHECK(duplicate_transition.outcome ==
                DelegationOutcome::exact_duplicate);
    IOTOX_CHECK(!duplicate_transition.ledger_changed);

    reopened.value().reset();
    auto transitioned_reopen = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(transitioned_reopen.ok(),
                    transitioned_reopen.status().message());
    IOTOX_CHECK(transitioned_reopen.value()->snapshot().ownership_epoch == 2U);
    IOTOX_CHECK(transitioned_reopen.value()->snapshot().sequence == 1U);
    IOTOX_CHECK(transitioned_reopen.value()->snapshot().principals.size() == 1U);

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
    secure_wipe(controller_seed);
    secure_wipe(successor_seed);
}

IOTOX_TEST("remote owner can migrate v2 without widening then explicitly grant terminal") {
    using namespace iotox;
    using namespace iotox::protocol;
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto device_seed = signing_seed(9U);
    auto owner_seed = signing_seed(59U);
    auto controller_seed = signing_seed(109U);
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    auto controller = sodium.value().signing_keypair_from_seed(controller_seed);
    IOTOX_CHECK(device.ok() && owner.ok() && controller.ok());

    TemporaryDirectory temporary;
    AuthorityLedger::Config config;
    config.path = temporary.path() / "authority.ledger";
    auto ledger = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAuthorityV1Capabilities;
    bootstrap.issuer = owner.value().public_key();
    bootstrap.subject = owner.value().public_key();
    auto bootstrap_body = ledger.value()->prepare(bootstrap);
    IOTOX_CHECK(bootstrap_body.ok());
    auto bootstrap_record = sign_authority_record_body(
        bootstrap_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(bootstrap_record.ok());
    IOTOX_CHECK(ledger.value()->append(bootstrap_record.value()).ok());

    PeerAuthoritySnapshot peer;
    peer.connected = true;
    peer.feature_negotiated = true;
    peer.authority_v2_negotiated = true;
    peer.remote_authorized = true;
    peer.remote_role = PrincipalRole::owner;
    peer.remote_capabilities = kAuthorityV1Capabilities;
    peer.remote_principal = owner.value().public_key();
    peer.peer_verifier_device = controller.value().public_key();
    const AuthoritySnapshot v1_head = ledger.value()->snapshot();
    bind_local_authority_head(peer, v1_head);

    AuthorityRecord migration;
    migration.format = AuthorityLedgerFormat::v2;
    migration.action = AuthorityAction::migrate_v2;
    migration.role = PrincipalRole::owner;
    migration.sequence = v1_head.sequence + 1U;
    migration.ownership_epoch = v1_head.ownership_epoch;
    migration.capabilities = kAuthorityV1Capabilities;
    migration.device = v1_head.device;
    migration.issuer = owner.value().public_key();
    migration.subject = owner.value().public_key();
    migration.previous_digest = v1_head.tail_digest;

    AuthorityRecord widened_migration = migration;
    widened_migration.capabilities = kAuthorityV2Capabilities;
    auto widened_body = encode_authority_record_body(widened_migration);
    IOTOX_CHECK(widened_body.ok());
    auto widened_record = sign_authority_record_body(
        widened_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(widened_record.ok());
    auto widened = apply_remote_owner_mutation(
        widened_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(widened.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!widened.ledger_changed);
    IOTOX_CHECK(ledger.value()->snapshot().format == AuthorityLedgerFormat::v1);

    auto migration_body = encode_authority_record_body(migration);
    IOTOX_CHECK(migration_body.ok());
    auto migration_record = sign_authority_record_body(
        migration_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(migration_record.ok());
    auto unnegotiated_peer = peer;
    unnegotiated_peer.authority_v2_negotiated = false;
    auto unnegotiated = apply_remote_owner_mutation(
        migration_record.value(), *ledger.value(), unnegotiated_peer,
        sodium.value());
    IOTOX_CHECK(unnegotiated.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!unnegotiated.ledger_changed);
    IOTOX_CHECK(ledger.value()->snapshot().format == AuthorityLedgerFormat::v1);
    auto migrated = apply_remote_owner_mutation(
        migration_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(migrated.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(migrated.ledger_changed);
    const AuthoritySnapshot v2_head = ledger.value()->snapshot();
    IOTOX_CHECK(v2_head.format == AuthorityLedgerFormat::v2);
    IOTOX_CHECK(v2_head.sequence == v1_head.sequence + 1U);
    auto v2_owner = ledger.value()->principal(owner.value().public_key());
    IOTOX_CHECK(v2_owner.ok());
    IOTOX_CHECK(v2_owner.value().capabilities == kAuthorityV1Capabilities);
    IOTOX_CHECK(!ledger.value()->authorized(
        owner.value().public_key(),
        static_cast<std::uint64_t>(Capability::interactive_terminal)));

    peer.remote_authorized = false;
    peer.remote_principal.fill(0U);
    auto duplicate = apply_remote_owner_mutation(
        migration_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(duplicate.outcome == DelegationOutcome::exact_duplicate);
    IOTOX_CHECK(!duplicate.ledger_changed);

    // A fresh proof against the migrated exact head is required before any
    // next mutation. The terminal bit is then requested explicitly rather
    // than inherited from the format transition.
    peer.remote_authorized = true;
    peer.remote_role = PrincipalRole::owner;
    peer.remote_capabilities = kAuthorityV1Capabilities;
    peer.remote_principal = owner.value().public_key();
    bind_local_authority_head(peer, v2_head);
    AuthorityRecord terminal_grant;
    terminal_grant.format = AuthorityLedgerFormat::v2;
    terminal_grant.action = AuthorityAction::grant;
    terminal_grant.role = PrincipalRole::operator_role;
    terminal_grant.sequence = v2_head.sequence + 1U;
    terminal_grant.ownership_epoch = v2_head.ownership_epoch;
    terminal_grant.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry) |
        static_cast<std::uint64_t>(Capability::interactive_terminal);
    terminal_grant.device = v2_head.device;
    terminal_grant.issuer = owner.value().public_key();
    terminal_grant.subject = controller.value().public_key();
    terminal_grant.previous_digest = v2_head.tail_digest;
    auto terminal_body = encode_authority_record_body(terminal_grant);
    IOTOX_CHECK(terminal_body.ok());
    auto terminal_record = sign_authority_record_body(
        terminal_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(terminal_record.ok());
    auto terminal_applied = apply_remote_self_delegation(
        terminal_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(terminal_applied.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(terminal_applied.ledger_changed);
    IOTOX_CHECK(ledger.value()->authorized(
        controller.value().public_key(),
        static_cast<std::uint64_t>(Capability::interactive_terminal)));

    const AuthoritySnapshot terminal_head = ledger.value()->snapshot();
    AuthorityRecord wrong_format = terminal_grant;
    wrong_format.format = AuthorityLedgerFormat::v1;
    wrong_format.sequence = terminal_head.sequence + 1U;
    wrong_format.previous_digest = terminal_head.tail_digest;
    wrong_format.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry);
    auto wrong_format_body = encode_authority_record_body(wrong_format);
    IOTOX_CHECK(wrong_format_body.ok());
    auto wrong_format_record = sign_authority_record_body(
        wrong_format_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(wrong_format_record.ok());
    peer.peer_verifier_device = controller.value().public_key();
    bind_local_authority_head(peer, terminal_head);
    auto wrong_format_result = apply_remote_self_delegation(
        wrong_format_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(wrong_format_result.outcome == DelegationOutcome::conflict);
    IOTOX_CHECK(!wrong_format_result.ledger_changed);

    peer.authority_v3_negotiated = true;
    bind_local_authority_head(peer, terminal_head);
    AuthorityRecord v3_migration;
    v3_migration.format = AuthorityLedgerFormat::v3;
    v3_migration.action = AuthorityAction::migrate_v3;
    v3_migration.role = PrincipalRole::owner;
    v3_migration.sequence = terminal_head.sequence + 1U;
    v3_migration.ownership_epoch = terminal_head.ownership_epoch;
    v3_migration.capabilities = kAuthorityV1Capabilities;
    v3_migration.device = terminal_head.device;
    v3_migration.issuer = owner.value().public_key();
    v3_migration.subject = owner.value().public_key();
    v3_migration.previous_digest = terminal_head.tail_digest;
    auto v3_body = encode_authority_record_body(v3_migration);
    IOTOX_CHECK(v3_body.ok());
    auto v3_record = sign_authority_record_body(
        v3_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(v3_record.ok());

    auto no_v3_peer = peer;
    no_v3_peer.authority_v3_negotiated = false;
    auto no_v3 = apply_remote_owner_mutation(v3_record.value(), *ledger.value(),
                                             no_v3_peer, sodium.value());
    IOTOX_CHECK(no_v3.outcome == DelegationOutcome::denied);
    IOTOX_CHECK(!no_v3.ledger_changed);
    auto v3_applied = apply_remote_owner_mutation(
        v3_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(v3_applied.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(v3_applied.ledger_changed);
    const AuthoritySnapshot v3_head = ledger.value()->snapshot();
    IOTOX_CHECK(v3_head.format == AuthorityLedgerFormat::v3);
    IOTOX_CHECK(!ledger.value()->authorized(
        owner.value().public_key(),
        static_cast<std::uint64_t>(Capability::sync_admin)));

    peer.remote_authorized = false;
    auto v3_duplicate = apply_remote_owner_mutation(
        v3_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(v3_duplicate.outcome == DelegationOutcome::exact_duplicate);
    IOTOX_CHECK(!v3_duplicate.ledger_changed);

    peer.remote_authorized = true;
    peer.remote_role = PrincipalRole::owner;
    peer.remote_capabilities = kAuthorityV1Capabilities;
    peer.remote_principal = owner.value().public_key();
    bind_local_authority_head(peer, v3_head);
    AuthorityRecord owner_sync;
    owner_sync.format = AuthorityLedgerFormat::v3;
    owner_sync.action = AuthorityAction::grant;
    owner_sync.role = PrincipalRole::owner;
    owner_sync.sequence = v3_head.sequence + 1U;
    owner_sync.ownership_epoch = v3_head.ownership_epoch;
    owner_sync.capabilities = kAuthorityV3Capabilities;
    owner_sync.device = v3_head.device;
    owner_sync.issuer = owner.value().public_key();
    owner_sync.subject = owner.value().public_key();
    owner_sync.previous_digest = v3_head.tail_digest;
    auto owner_sync_body = encode_authority_record_body(owner_sync);
    IOTOX_CHECK(owner_sync_body.ok());
    auto owner_sync_record = sign_authority_record_body(
        owner_sync_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(owner_sync_record.ok());
    auto owner_sync_applied = apply_remote_owner_mutation(
        owner_sync_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(owner_sync_applied.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(owner_sync_applied.ledger_changed);
    IOTOX_CHECK(ledger.value()->authorized(
        owner.value().public_key(),
        static_cast<std::uint64_t>(Capability::sync_admin)));

    const AuthoritySnapshot sync_owner_head = ledger.value()->snapshot();
    peer.remote_capabilities = kAuthorityV3Capabilities;
    bind_local_authority_head(peer, sync_owner_head);
    AuthorityRecord subscriber_grant;
    subscriber_grant.format = AuthorityLedgerFormat::v3;
    subscriber_grant.action = AuthorityAction::grant;
    subscriber_grant.role = PrincipalRole::viewer;
    subscriber_grant.sequence = sync_owner_head.sequence + 1U;
    subscriber_grant.ownership_epoch = sync_owner_head.ownership_epoch;
    subscriber_grant.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry) |
        static_cast<std::uint64_t>(Capability::sync_subscribe);
    subscriber_grant.device = sync_owner_head.device;
    subscriber_grant.issuer = owner.value().public_key();
    subscriber_grant.subject = controller.value().public_key();
    subscriber_grant.previous_digest = sync_owner_head.tail_digest;
    auto subscriber_body = encode_authority_record_body(subscriber_grant);
    IOTOX_CHECK(subscriber_body.ok());
    auto subscriber_record = sign_authority_record_body(
        subscriber_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(subscriber_record.ok());
    auto subscriber_applied = apply_remote_self_delegation(
        subscriber_record.value(), *ledger.value(), peer, sodium.value());
    IOTOX_CHECK(subscriber_applied.outcome == DelegationOutcome::applied);
    IOTOX_CHECK(subscriber_applied.ledger_changed);
    IOTOX_CHECK(ledger.value()->authorized(
        controller.value().public_key(),
        static_cast<std::uint64_t>(Capability::sync_subscribe)));

    ledger.value().reset();
    auto reopened = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(reopened.ok(), reopened.status().message());
    IOTOX_CHECK(reopened.value()->snapshot().format ==
                AuthorityLedgerFormat::v3);
    IOTOX_CHECK(reopened.value()->authorized(
        controller.value().public_key(),
        static_cast<std::uint64_t>(Capability::sync_subscribe)));

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
    secure_wipe(controller_seed);
}
