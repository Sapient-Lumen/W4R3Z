#include "iotox/protocol/session.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/security/sodium.hpp"
#include "test_harness.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <string>
#include <system_error>
#include <unistd.h>
#include <utility>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        const auto ticks =
            std::chrono::steady_clock::now().time_since_epoch().count();
        path_ = std::filesystem::temp_directory_path() /
                ("iotox-authority-session-test-" +
                 std::to_string(::getpid()) + "-" +
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

iotox::security::SigningSeed seed(std::uint8_t first) {
    iotox::security::SigningSeed output{};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        output[index] = static_cast<std::uint8_t>(first + index);
    }
    return output;
}

iotox::protocol::SessionNonce session_nonce(std::uint8_t first) {
    iotox::protocol::SessionNonce output{};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        output[index] = static_cast<std::uint8_t>(first + index);
    }
    return output;
}

iotox::security::AuthorityNonce authority_nonce(std::uint8_t first) {
    iotox::security::AuthorityNonce output{};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        output[index] = static_cast<std::uint8_t>(first + index);
    }
    return output;
}

struct SessionPair {
    iotox::protocol::PeerSessionSnapshot lower;
    iotox::protocol::PeerSessionSnapshot higher;
};

SessionPair confirmed_pair() {
    using namespace iotox::protocol;
    const std::string lower_key(64U, '1');
    const std::string higher_key(64U, 'E');
    const HelloPayload lower_hello =
        make_local_hello(1024U * 1024U, session_nonce(11U));
    const HelloPayload higher_hello =
        make_local_hello(1024U * 1024U, session_nonce(41U));
    const NegotiatedProtocol negotiated =
        negotiate_protocol(lower_hello, higher_hello);
    IOTOX_CHECK(negotiated.compatible);
    IOTOX_CHECK(
        (negotiated.shared_features &
         feature_bit(Feature::authorization_ledger_v1)) != 0U);

    PeerSessionSnapshot lower;
    lower.friend_number = 7U;
    lower.public_key = higher_key;
    lower.local_public_key = lower_key;
    lower.connection_status = 1;
    lower.state = PeerSessionState::confirmed;
    lower.connected = true;
    lower.hello_sent = true;
    lower.hello_received = true;
    lower.confirmation_sent = true;
    lower.confirmation_received = true;
    lower.application_ready = true;
    lower.local_role_known = true;
    lower.local_role = SessionRole::lower_transport_key;
    lower.online_epoch = 3U;
    lower.local_hello_message_id = 1001U;
    lower.peer_hello_message_id = 2001U;
    lower.local_confirmation_message_id = 3001U;
    lower.peer_confirmation_message_id = 4001U;
    lower.local = lower_hello;
    lower.peer = higher_hello;
    lower.negotiated = negotiated;

    PeerSessionSnapshot higher;
    higher.friend_number = 9U;
    higher.public_key = lower_key;
    higher.local_public_key = higher_key;
    higher.connection_status = 1;
    higher.state = PeerSessionState::confirmed;
    higher.connected = true;
    higher.hello_sent = true;
    higher.hello_received = true;
    higher.confirmation_sent = true;
    higher.confirmation_received = true;
    higher.application_ready = true;
    higher.local_role_known = true;
    higher.local_role = SessionRole::higher_transport_key;
    higher.online_epoch = 8U;
    higher.local_hello_message_id = 2001U;
    higher.peer_hello_message_id = 1001U;
    higher.local_confirmation_message_id = 4001U;
    higher.peer_confirmation_message_id = 3001U;
    higher.local = higher_hello;
    higher.peer = lower_hello;
    higher.negotiated = negotiated;
    return {lower, higher};
}

std::unique_ptr<iotox::security::AuthorityLedger> bootstrap_ledger(
    const std::filesystem::path &path,
    const iotox::security::SigningPublicKey &device,
    const iotox::security::SigningKeyPair &owner,
    const iotox::security::Sodium &sodium) {
    using namespace iotox::security;
    AuthorityLedger::Config config;
    config.path = path;
    auto ledger = AuthorityLedger::open(config, device, sodium);
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());

    AuthorityPrepareRequest bootstrap;
    bootstrap.action = AuthorityAction::bootstrap;
    bootstrap.role = PrincipalRole::owner;
    bootstrap.capabilities = kAllCapabilities;
    bootstrap.issuer = owner.public_key();
    bootstrap.subject = owner.public_key();
    auto body = ledger.value()->prepare(bootstrap);
    IOTOX_CHECK_MSG(body.ok(), body.status().message());
    auto record = sign_authority_record_body(
        body.value(), owner.secret_key(), sodium);
    IOTOX_CHECK_MSG(record.ok(), record.status().message());
    const iotox::Status appended = ledger.value()->append(record.value());
    IOTOX_CHECK_MSG(appended.ok(), appended.message());
    return std::move(ledger).value();
}

}  // namespace

IOTOX_TEST("canonical confirmed transcript is identical from both peer perspectives") {
    auto pair = confirmed_pair();
    auto lower = iotox::protocol::encode_canonical_session_transcript(
        pair.lower);
    auto higher = iotox::protocol::encode_canonical_session_transcript(
        pair.higher);
    IOTOX_CHECK_MSG(lower.ok(), lower.status().message());
    IOTOX_CHECK_MSG(higher.ok(), higher.status().message());
    IOTOX_CHECK(lower.value() == higher.value());

    pair.higher.local_confirmation_message_id += 1U;
    auto changed = iotox::protocol::encode_canonical_session_transcript(
        pair.higher);
    IOTOX_CHECK(changed.ok());
    IOTOX_CHECK(changed.value() != lower.value());
}

IOTOX_TEST("authority challenge and proof have one strict canonical representation") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto claimant_seed = seed(31U);
    auto claimant = sodium.value().signing_keypair_from_seed(claimant_seed);
    IOTOX_CHECK_MSG(claimant.ok(), claimant.status().message());

    AuthorityChallenge challenge;
    challenge.verifier_device.fill(0x11U);
    challenge.ownership_epoch = 4U;
    challenge.authority_sequence = 19U;
    challenge.authority_tail_digest.fill(0x22U);
    challenge.session_transcript_digest.fill(0x33U);
    challenge.nonce = authority_nonce(51U);
    auto encoded_challenge = encode_authority_challenge(challenge);
    IOTOX_CHECK_MSG(encoded_challenge.ok(),
                    encoded_challenge.status().message());
    auto decoded_challenge =
        decode_authority_challenge(encoded_challenge.value());
    IOTOX_CHECK(decoded_challenge.ok());
    IOTOX_CHECK(decoded_challenge.value() == challenge);

    auto malformed_challenge = encoded_challenge.value();
    malformed_challenge[152U] = 1U;
    IOTOX_CHECK(!decode_authority_challenge(malformed_challenge).ok());

    AuthorityProof proof;
    proof.verifier_device = challenge.verifier_device;
    proof.claimant_principal = claimant.value().public_key();
    proof.ownership_epoch = challenge.ownership_epoch;
    proof.authority_sequence = challenge.authority_sequence;
    proof.authority_tail_digest = challenge.authority_tail_digest;
    proof.session_transcript_digest = challenge.session_transcript_digest;
    proof.challenge_nonce = challenge.nonce;
    proof.challenge_message_id = 991U;
    auto body = encode_authority_proof_body(proof);
    IOTOX_CHECK_MSG(body.ok(), body.status().message());
    auto signed_proof = sign_authority_proof_body(
        body.value(), claimant.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(signed_proof.ok(), signed_proof.status().message());
    auto decoded_proof = decode_authority_proof(signed_proof.value());
    IOTOX_CHECK(decoded_proof.ok());
    IOTOX_CHECK(verify_authority_proof(
                    decoded_proof.value(), sodium.value())
                    .ok());

    auto tampered = signed_proof.value();
    tampered[120U] ^= 1U;
    auto decoded_tampered = decode_authority_proof(tampered);
    IOTOX_CHECK(decoded_tampered.ok());
    IOTOX_CHECK(!verify_authority_proof(
                     decoded_tampered.value(), sodium.value())
                     .ok());
    secure_wipe(claimant_seed);
}

IOTOX_TEST("confirmed peers bind an active ledger principal to the exact session") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;
    auto device_seed = seed(1U);
    auto owner_seed = seed(65U);
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    auto ledger = bootstrap_ledger(
        temporary.path() / "authority.ledger",
        device.value().public_key(), owner.value(), sodium.value());

    auto pair = confirmed_pair();
    PeerAuthorityRegistry verifier(sodium.value());
    PeerAuthorityRegistry claimant(sodium.value());
    AuthoritySnapshot empty_authority;
    IOTOX_CHECK(verifier.synchronize_session(
                    pair.lower, ledger->snapshot(), 100U)
                    .ok());
    IOTOX_CHECK(claimant.synchronize_session(
                    pair.higher, empty_authority, 100U)
                    .ok());

    const AuthorityNonce nonce = authority_nonce(91U);
    auto challenge = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), nonce, 5001U, 101U);
    IOTOX_CHECK_MSG(challenge.ok(), challenge.status().message());
    IOTOX_CHECK(challenge.value().correlation_id ==
                pair.lower.peer_confirmation_message_id);
    IOTOX_CHECK(verifier.mark_challenge_send_failed(
                    pair.lower.friend_number,
                    iotox::ErrorCode::resource_exhausted,
                    "synthetic SENDQ", 102U)
                    .ok());
    IOTOX_CHECK(!verifier.make_challenge_frame(
                     pair.lower, ledger->snapshot(), nonce, 5002U, 103U)
                     .ok());
    auto challenge_retry = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), nonce, 5001U, 103U);
    IOTOX_CHECK(challenge_retry.ok());
    IOTOX_CHECK(challenge_retry.value().payload == challenge.value().payload);
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 5001U, 104U)
                    .ok());

    IOTOX_CHECK(claimant.receive_challenge(
                    pair.higher, challenge_retry.value(), 105U)
                    .ok());
    auto proof_body = claimant.prepare_proof_body(
        pair.higher.friend_number, owner.value().public_key(), 106U);
    IOTOX_CHECK_MSG(proof_body.ok(), proof_body.status().message());
    auto signed_proof = sign_authority_proof_body(
        proof_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(signed_proof.ok(), signed_proof.status().message());
    auto proof = claimant.make_proof_frame(
        pair.higher, signed_proof.value(), 6001U, 107U);
    IOTOX_CHECK_MSG(proof.ok(), proof.status().message());
    IOTOX_CHECK(proof.value().correlation_id == 5001U);
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 6001U, 108U)
                    .ok());

    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, proof.value(), *ledger, 109U)
                    .ok());
    IOTOX_CHECK(verifier.authorized(
        pair.lower.friend_number,
        static_cast<std::uint64_t>(Capability::read_telemetry)));
    IOTOX_CHECK(verifier.authorized_at(
        pair.lower.friend_number,
        static_cast<std::uint64_t>(Capability::read_telemetry),
        ledger->snapshot()));
    auto authorized = verifier.get(pair.lower.friend_number);
    IOTOX_CHECK(authorized.ok());
    IOTOX_CHECK(authorized.value().remote_principal ==
                owner.value().public_key());
    IOTOX_CHECK(authorized.value().remote_role == PrincipalRole::owner);

    // The signed proof body is the authority record. A claimant that loses
    // its local outer-frame state may wrap the same signed body in a new
    // transport message id; the verifier preserves the first id as evidence.
    auto duplicate = proof.value();
    duplicate.message_id = 6002U;
    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, duplicate, *ledger, 110U)
                    .ok());
    IOTOX_CHECK(verifier.get(pair.lower.friend_number)
                    .value()
                    .peer_proof_message_id == 6001U);

    // Changed signed proof bytes in the same online epoch are a conflict and
    // close authorization rather than providing a repair oracle.
    auto conflict = proof.value();
    conflict.message_id = 6003U;
    conflict.payload.back() ^= 1U;
    IOTOX_CHECK(!verifier.receive_proof(
                     pair.lower, conflict, *ledger, 111U)
                     .ok());
    IOTOX_CHECK(!verifier.authorized(pair.lower.friend_number, 0U));

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
}

IOTOX_TEST("ledger mutation immediately invalidates a previously proven principal") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;
    auto device_seed = seed(2U);
    auto owner_seed = seed(66U);
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    auto ledger = bootstrap_ledger(
        temporary.path() / "authority.ledger",
        device.value().public_key(), owner.value(), sodium.value());

    auto pair = confirmed_pair();
    PeerAuthorityRegistry verifier(sodium.value());
    PeerAuthorityRegistry claimant(sodium.value());
    IOTOX_CHECK(verifier.synchronize_session(
                    pair.lower, ledger->snapshot(), 200U)
                    .ok());
    IOTOX_CHECK(claimant.synchronize_session(
                    pair.higher, AuthoritySnapshot{}, 200U)
                    .ok());
    auto challenge = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), authority_nonce(121U),
        7001U, 201U);
    IOTOX_CHECK(challenge.ok());
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 7001U, 202U)
                    .ok());
    IOTOX_CHECK(claimant.receive_challenge(
                    pair.higher, challenge.value(), 203U)
                    .ok());
    auto body = claimant.prepare_proof_body(
        pair.higher.friend_number, owner.value().public_key(), 204U);
    IOTOX_CHECK(body.ok());
    auto bytes = sign_authority_proof_body(
        body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(bytes.ok());
    auto proof = claimant.make_proof_frame(
        pair.higher, bytes.value(), 8001U, 205U);
    IOTOX_CHECK(proof.ok());
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 8001U, 206U)
                    .ok());
    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, proof.value(), *ledger, 207U)
                    .ok());
    IOTOX_CHECK(verifier.authorized(pair.lower.friend_number, 0U));

    // Adding another active principal changes the exact challenged head. Even
    // though the proven owner remains active, the old proof is no longer the
    // authorization statement for the current constitution.
    auto delegate_seed = seed(130U);
    auto delegate = sodium.value().signing_keypair_from_seed(delegate_seed);
    IOTOX_CHECK(delegate.ok());
    AuthorityPrepareRequest grant;
    grant.action = AuthorityAction::grant;
    grant.role = PrincipalRole::viewer;
    grant.capabilities = static_cast<std::uint64_t>(Capability::read_telemetry);
    grant.issuer = owner.value().public_key();
    grant.subject = delegate.value().public_key();
    auto grant_body = ledger->prepare(grant);
    IOTOX_CHECK(grant_body.ok());
    auto grant_record = sign_authority_record_body(
        grant_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(grant_record.ok());
    IOTOX_CHECK(ledger->append(grant_record.value()).ok());
    // Even before the event path publishes invalidation, effect admission
    // compares the proof to the ledger's exact current head and fails closed.
    IOTOX_CHECK(!verifier.authorized_at(
        pair.lower.friend_number, 0U, ledger->snapshot()));
    verifier.invalidate_local_authority(ledger->snapshot(), 208U);
    IOTOX_CHECK(!verifier.authorized(pair.lower.friend_number, 0U));

    // The old signed proof may already be in the transport queue when the
    // append invalidates its challenge. It targets the old exact head and is
    // not accepted, but it must not poison the fresh challenge round.
    const iotox::Status stale = verifier.receive_proof(
        pair.lower, proof.value(), *ledger, 209U);
    IOTOX_CHECK(!stale.ok());
    IOTOX_CHECK(stale.code() == iotox::ErrorCode::unavailable);
    auto invalidated = verifier.get(pair.lower.friend_number);
    IOTOX_CHECK(invalidated.ok());
    IOTOX_CHECK(invalidated.value().verifier_state ==
                AuthorityVerifierState::challenge_ready);
    IOTOX_CHECK(invalidated.value().local_challenge_message_id == 0U);

    auto fresh = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), authority_nonce(151U),
        7002U, 210U);
    IOTOX_CHECK(fresh.ok());
    IOTOX_CHECK(fresh.value().payload != challenge.value().payload);
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 7002U, 211U)
                    .ok());
    IOTOX_CHECK(claimant.receive_challenge(
                    pair.higher, fresh.value(), 212U)
                    .ok());

    // A second legitimate mutation can supersede this challenge before its
    // proof reaches toxcore. The same verifier/session and a strictly newer
    // authority head must replace the unfinished round rather than poison the
    // claimant until reconnect.
    auto second_delegate_seed = seed(131U);
    auto second_delegate =
        sodium.value().signing_keypair_from_seed(second_delegate_seed);
    IOTOX_CHECK(second_delegate.ok());
    grant.subject = second_delegate.value().public_key();
    auto second_grant_body = ledger->prepare(grant);
    IOTOX_CHECK(second_grant_body.ok());
    auto second_grant_record = sign_authority_record_body(
        second_grant_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(second_grant_record.ok());
    IOTOX_CHECK(ledger->append(second_grant_record.value()).ok());
    verifier.invalidate_local_authority(ledger->snapshot(), 213U);
    auto superseding = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), authority_nonce(181U), 7003U, 214U);
    IOTOX_CHECK(superseding.ok());
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 7003U, 215U)
                    .ok());
    IOTOX_CHECK_MSG(
        claimant.receive_challenge(pair.higher, superseding.value(), 216U).ok(),
        "strictly newer authority head must supersede an unfinished proof round");
    auto superseded = claimant.get(pair.higher.friend_number);
    IOTOX_CHECK(superseded.ok());
    IOTOX_CHECK(superseded.value().claimant_state ==
                AuthorityClaimantState::challenge_received);
    IOTOX_CHECK(superseded.value().peer_authority_sequence ==
                ledger->snapshot().sequence);

    auto fresh_body = claimant.prepare_proof_body(
        pair.higher.friend_number, owner.value().public_key(), 217U);
    IOTOX_CHECK(fresh_body.ok());
    auto fresh_bytes = sign_authority_proof_body(
        fresh_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(fresh_bytes.ok());
    auto fresh_proof = claimant.make_proof_frame(
        pair.higher, fresh_bytes.value(), 8002U, 218U);
    IOTOX_CHECK(fresh_proof.ok());
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 8002U, 219U)
                    .ok());
    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, fresh_proof.value(), *ledger, 220U)
                    .ok());
    IOTOX_CHECK(verifier.authorized_at(
        pair.lower.friend_number, 0U, ledger->snapshot()));

    auto equal_head_conflict = superseding.value();
    equal_head_conflict.message_id = 7004U;
    auto changed_challenge = decode_authority_challenge(
        equal_head_conflict.payload);
    IOTOX_CHECK(changed_challenge.ok());
    changed_challenge.value().nonce[0U] ^= 1U;
    auto changed_challenge_bytes =
        encode_authority_challenge(changed_challenge.value());
    IOTOX_CHECK(changed_challenge_bytes.ok());
    equal_head_conflict.payload.assign(changed_challenge_bytes.value().begin(),
                                       changed_challenge_bytes.value().end());
    const iotox::Status equal_conflict = claimant.receive_challenge(
        pair.higher, equal_head_conflict, 221U);
    IOTOX_CHECK(!equal_conflict.ok());
    IOTOX_CHECK(equal_conflict.code() == iotox::ErrorCode::protocol_error);

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
    secure_wipe(delegate_seed);
    secure_wipe(second_delegate_seed);
}

IOTOX_TEST("one denied device proof may be replaced by one explicit recovery owner") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;
    auto verifier_device_seed = seed(5U);
    auto fresh_device_seed = seed(45U);
    auto owner_seed = seed(85U);
    auto verifier_device = sodium.value().signing_keypair_from_seed(
        verifier_device_seed);
    auto fresh_device = sodium.value().signing_keypair_from_seed(
        fresh_device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(verifier_device.ok() && fresh_device.ok() && owner.ok());
    auto ledger = bootstrap_ledger(
        temporary.path() / "authority.ledger",
        verifier_device.value().public_key(), owner.value(), sodium.value());

    auto pair = confirmed_pair();
    PeerAuthorityRegistry verifier(sodium.value());
    PeerAuthorityRegistry claimant(sodium.value());
    IOTOX_CHECK(verifier.synchronize_session(
                    pair.lower, ledger->snapshot(), 300U)
                    .ok());
    IOTOX_CHECK(claimant.synchronize_session(
                    pair.higher, AuthoritySnapshot{}, 300U)
                    .ok());
    auto challenge = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), authority_nonce(171U), 9001U, 301U);
    IOTOX_CHECK(challenge.ok());
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 9001U, 302U)
                    .ok());
    IOTOX_CHECK(claimant.receive_challenge(
                    pair.higher, challenge.value(), 303U)
                    .ok());

    auto device_body = claimant.prepare_proof_body(
        pair.higher.friend_number, fresh_device.value().public_key(), 304U);
    IOTOX_CHECK(device_body.ok());
    auto device_bytes = sign_authority_proof_body(
        device_body.value(), fresh_device.value().secret_key(), sodium.value());
    IOTOX_CHECK(device_bytes.ok());
    auto device_proof = claimant.make_proof_frame(
        pair.higher, device_bytes.value(), 9101U, 305U);
    IOTOX_CHECK(device_proof.ok());
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 9101U, 306U)
                    .ok());
    IOTOX_CHECK(!verifier.receive_proof(
                     pair.lower, device_proof.value(), *ledger, 307U)
                     .ok());
    auto denied = verifier.get(pair.lower.friend_number);
    IOTOX_CHECK(denied.ok());
    IOTOX_CHECK(denied.value().verifier_state ==
                AuthorityVerifierState::denied);
    IOTOX_CHECK(denied.value().peer_proof_candidate_count == 1U);

    auto owner_body = claimant.prepare_recovery_proof_body(
        pair.higher.friend_number, fresh_device.value().public_key(),
        owner.value().public_key(), 308U);
    IOTOX_CHECK_MSG(owner_body.ok(), owner_body.status().message());
    IOTOX_CHECK(!claimant.prepare_recovery_proof_body(
                     pair.higher.friend_number,
                     fresh_device.value().public_key(),
                     owner.value().public_key(), 309U)
                     .ok());
    auto owner_bytes = sign_authority_proof_body(
        owner_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(owner_bytes.ok());
    auto owner_proof = claimant.make_proof_frame(
        pair.higher, owner_bytes.value(), 9102U, 310U);
    IOTOX_CHECK_MSG(owner_proof.ok(), owner_proof.status().message());
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 9102U, 311U)
                    .ok());
    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, owner_proof.value(), *ledger, 312U)
                    .ok());
    auto recovered = verifier.get(pair.lower.friend_number);
    IOTOX_CHECK(recovered.ok());
    IOTOX_CHECK(recovered.value().remote_authorized);
    IOTOX_CHECK(recovered.value().remote_principal == owner.value().public_key());
    IOTOX_CHECK(recovered.value().remote_role == PrincipalRole::owner);
    IOTOX_CHECK(recovered.value().peer_proof_candidate_count == 2U);

    // The recovery action delegates the fresh device and advances the exact
    // ledger head. That is a new authority round inside the same confirmed
    // transport session, not a conflicting rewrite of the old challenge.
    AuthorityPrepareRequest grant;
    grant.action = AuthorityAction::grant;
    grant.role = PrincipalRole::automation;
    grant.capabilities =
        static_cast<std::uint64_t>(Capability::read_telemetry);
    grant.issuer = owner.value().public_key();
    grant.subject = fresh_device.value().public_key();
    auto grant_body = ledger->prepare(grant);
    IOTOX_CHECK(grant_body.ok());
    auto grant_record = sign_authority_record_body(
        grant_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(grant_record.ok());
    IOTOX_CHECK(ledger->append(grant_record.value()).ok());
    verifier.invalidate_local_authority(ledger->snapshot(), 313U);
    auto next_challenge = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), authority_nonce(191U), 9002U, 314U);
    IOTOX_CHECK(next_challenge.ok());
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 9002U, 315U)
                    .ok());
    IOTOX_CHECK(claimant.receive_challenge(
                    pair.higher, next_challenge.value(), 316U)
                    .ok());
    auto advanced = claimant.get(pair.higher.friend_number);
    IOTOX_CHECK(advanced.ok());
    IOTOX_CHECK(advanced.value().claimant_state ==
                AuthorityClaimantState::challenge_received);
    IOTOX_CHECK(advanced.value().peer_authority_sequence ==
                ledger->snapshot().sequence);
    auto delegated_body = claimant.prepare_proof_body(
        pair.higher.friend_number, fresh_device.value().public_key(), 317U);
    IOTOX_CHECK(delegated_body.ok());
    auto delegated_bytes = sign_authority_proof_body(
        delegated_body.value(), fresh_device.value().secret_key(),
        sodium.value());
    IOTOX_CHECK(delegated_bytes.ok());
    auto delegated_proof = claimant.make_proof_frame(
        pair.higher, delegated_bytes.value(), 9103U, 318U);
    IOTOX_CHECK(delegated_proof.ok());
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 9103U, 319U)
                    .ok());
    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, delegated_proof.value(), *ledger, 320U)
                    .ok());
    IOTOX_CHECK(verifier.get(pair.lower.friend_number)
                    .value()
                    .remote_principal == fresh_device.value().public_key());

    // A delegated controller can later enter an explicit administrative
    // ceremony. The one replacement is accepted only when the second valid
    // claimant is an active owner.
    auto admin_body = claimant.prepare_recovery_proof_body(
        pair.higher.friend_number, fresh_device.value().public_key(),
        owner.value().public_key(), 321U);
    IOTOX_CHECK(admin_body.ok());
    auto admin_bytes = sign_authority_proof_body(
        admin_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(admin_bytes.ok());
    auto admin_proof = claimant.make_proof_frame(
        pair.higher, admin_bytes.value(), 9104U, 322U);
    IOTOX_CHECK(admin_proof.ok());
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 9104U, 323U)
                    .ok());
    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, admin_proof.value(), *ledger, 324U)
                    .ok());
    IOTOX_CHECK(verifier.get(pair.lower.friend_number)
                    .value()
                    .remote_role == PrincipalRole::owner);

    // Sequence is scoped to an ownership epoch. A valid next-epoch challenge
    // is newer even though its sequence resets to one.
    AuthoritySnapshot transitioned = ledger->snapshot();
    ++transitioned.ownership_epoch;
    transitioned.sequence = 1U;
    transitioned.tail_digest.fill(0xD4U);
    verifier.invalidate_local_authority(transitioned, 325U);
    auto epoch_challenge = verifier.make_challenge_frame(
        pair.lower, transitioned, authority_nonce(211U), 9003U, 326U);
    IOTOX_CHECK(epoch_challenge.ok());
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 9003U, 327U)
                    .ok());
    IOTOX_CHECK_MSG(
        claimant.receive_challenge(pair.higher, epoch_challenge.value(), 328U).ok(),
        "claimant must accept a lexicographically newer ownership head");
    auto epoch_advanced = claimant.get(pair.higher.friend_number);
    IOTOX_CHECK(epoch_advanced.ok());
    IOTOX_CHECK(epoch_advanced.value().claimant_state ==
                AuthorityClaimantState::challenge_received);
    IOTOX_CHECK(epoch_advanced.value().peer_authority_epoch == 2U);
    IOTOX_CHECK(epoch_advanced.value().peer_authority_sequence == 1U);

    secure_wipe(verifier_device_seed);
    secure_wipe(fresh_device_seed);
    secure_wipe(owner_seed);
}

IOTOX_TEST("authority v2 challenge and proof formats are explicit and domain separated") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto claimant_seed = seed(141U);
    auto claimant = sodium.value().signing_keypair_from_seed(claimant_seed);
    IOTOX_CHECK_MSG(claimant.ok(), claimant.status().message());

    AuthorityChallenge challenge;
    challenge.authority_format = AuthorityLedgerFormat::v2;
    challenge.verifier_device.fill(0x31U);
    challenge.ownership_epoch = 9U;
    challenge.authority_sequence = 27U;
    challenge.authority_tail_digest.fill(0x42U);
    challenge.session_transcript_digest.fill(0x53U);
    challenge.nonce = authority_nonce(161U);
    auto encoded_challenge = encode_authority_challenge(challenge);
    IOTOX_CHECK_MSG(encoded_challenge.ok(),
                    encoded_challenge.status().message());
    IOTOX_CHECK(encoded_challenge.value()[4U] ==
                kAuthorityChallengeFormatV2);
    IOTOX_CHECK(encoded_challenge.value()[5U] ==
                static_cast<std::uint8_t>(AuthorityLedgerFormat::v2));
    auto decoded_challenge = decode_authority_challenge(
        encoded_challenge.value());
    IOTOX_CHECK(decoded_challenge.ok());
    IOTOX_CHECK(decoded_challenge.value() == challenge);

    auto missing_ledger_version = encoded_challenge.value();
    missing_ledger_version[5U] = 0U;
    IOTOX_CHECK(!decode_authority_challenge(missing_ledger_version).ok());

    AuthorityProof proof;
    proof.authority_format = AuthorityLedgerFormat::v2;
    proof.verifier_device = challenge.verifier_device;
    proof.claimant_principal = claimant.value().public_key();
    proof.ownership_epoch = challenge.ownership_epoch;
    proof.authority_sequence = challenge.authority_sequence;
    proof.authority_tail_digest = challenge.authority_tail_digest;
    proof.session_transcript_digest = challenge.session_transcript_digest;
    proof.challenge_nonce = challenge.nonce;
    proof.challenge_message_id = 0x0102030405060708ULL;
    auto body = encode_authority_proof_body(proof);
    IOTOX_CHECK_MSG(body.ok(), body.status().message());
    IOTOX_CHECK(body.value()[4U] == kAuthorityProofFormatV2);
    IOTOX_CHECK(body.value()[5U] ==
                static_cast<std::uint8_t>(AuthorityLedgerFormat::v2));
    auto signed_proof = sign_authority_proof_body(
        body.value(), claimant.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(signed_proof.ok(), signed_proof.status().message());
    auto decoded_proof = decode_authority_proof(signed_proof.value());
    IOTOX_CHECK(decoded_proof.ok());
    IOTOX_CHECK(decoded_proof.value().authority_format ==
                AuthorityLedgerFormat::v2);
    IOTOX_CHECK(verify_authority_proof(
                    decoded_proof.value(), sodium.value())
                    .ok());

    // Reinterpreting the exact signature under the v1 wire marker produces a
    // structurally valid proof body but must fail because v1 and v2 use
    // independent permanent signature domains.
    auto cross_domain = signed_proof.value();
    cross_domain[4U] = kAuthorityProofFormatV1;
    cross_domain[5U] = 0U;
    auto decoded_cross_domain = decode_authority_proof(cross_domain);
    IOTOX_CHECK(decoded_cross_domain.ok());
    IOTOX_CHECK(decoded_cross_domain.value().authority_format ==
                AuthorityLedgerFormat::v1);
    IOTOX_CHECK(!verify_authority_proof(
                     decoded_cross_domain.value(), sodium.value())
                     .ok());

    secure_wipe(claimant_seed);
}

IOTOX_TEST("authority v2 is requalified end to end and requires negotiated support") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;
    auto device_seed = seed(12U);
    auto owner_seed = seed(76U);
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    auto ledger = bootstrap_ledger(
        temporary.path() / "authority.ledger",
        device.value().public_key(), owner.value(), sodium.value());

    AuthorityPrepareRequest migrate;
    migrate.action = AuthorityAction::migrate_v2;
    migrate.role = PrincipalRole::owner;
    migrate.capabilities = kAuthorityV1Capabilities;
    migrate.issuer = owner.value().public_key();
    migrate.subject = owner.value().public_key();
    auto migration_body = ledger->prepare(migrate);
    IOTOX_CHECK_MSG(migration_body.ok(), migration_body.status().message());
    auto migration_record = sign_authority_record_body(
        migration_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(migration_record.ok(), migration_record.status().message());
    IOTOX_CHECK_MSG(ledger->append(migration_record.value()).ok(),
                    "v2 migration must append before session requalification");
    IOTOX_CHECK(ledger->snapshot().format == AuthorityLedgerFormat::v2);

    auto pair = confirmed_pair();
    IOTOX_CHECK(
        (pair.lower.negotiated.shared_features &
         iotox::protocol::feature_bit(
             iotox::protocol::Feature::authorization_ledger_v2)) != 0U);
    PeerAuthorityRegistry verifier(sodium.value());
    PeerAuthorityRegistry claimant(sodium.value());
    IOTOX_CHECK(verifier.synchronize_session(
                    pair.lower, ledger->snapshot(), 400U)
                    .ok());
    IOTOX_CHECK(claimant.synchronize_session(
                    pair.higher, AuthoritySnapshot{}, 400U)
                    .ok());
    auto verifier_negotiation = verifier.get(pair.lower.friend_number);
    auto claimant_negotiation = claimant.get(pair.higher.friend_number);
    IOTOX_CHECK(verifier_negotiation.ok());
    IOTOX_CHECK(claimant_negotiation.ok());
    IOTOX_CHECK(verifier_negotiation.value().authority_v2_negotiated);
    IOTOX_CHECK(claimant_negotiation.value().authority_v2_negotiated);

    auto challenge = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), authority_nonce(201U), 12001U, 401U);
    IOTOX_CHECK_MSG(challenge.ok(), challenge.status().message());
    IOTOX_CHECK(challenge.value().payload[4U] ==
                kAuthorityChallengeFormatV2);
    IOTOX_CHECK(challenge.value().payload[5U] ==
                static_cast<std::uint8_t>(AuthorityLedgerFormat::v2));
    IOTOX_CHECK(verifier.mark_challenge_sent(
                    pair.lower.friend_number, 12001U, 402U)
                    .ok());
    IOTOX_CHECK(claimant.receive_challenge(
                    pair.higher, challenge.value(), 403U)
                    .ok());
    auto claimant_snapshot = claimant.get(pair.higher.friend_number);
    IOTOX_CHECK(claimant_snapshot.ok());
    IOTOX_CHECK(claimant_snapshot.value().peer_authority_format ==
                AuthorityLedgerFormat::v2);

    auto proof_body = claimant.prepare_proof_body(
        pair.higher.friend_number, owner.value().public_key(), 404U);
    IOTOX_CHECK_MSG(proof_body.ok(), proof_body.status().message());
    IOTOX_CHECK(proof_body.value()[4U] == kAuthorityProofFormatV2);
    IOTOX_CHECK(proof_body.value()[5U] ==
                static_cast<std::uint8_t>(AuthorityLedgerFormat::v2));
    auto proof_bytes = sign_authority_proof_body(
        proof_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(proof_bytes.ok(), proof_bytes.status().message());
    auto proof = claimant.make_proof_frame(
        pair.higher, proof_bytes.value(), 13001U, 405U);
    IOTOX_CHECK_MSG(proof.ok(), proof.status().message());
    IOTOX_CHECK(claimant.mark_proof_sent(
                    pair.higher.friend_number, 13001U, 406U)
                    .ok());
    IOTOX_CHECK(verifier.receive_proof(
                    pair.lower, proof.value(), *ledger, 407U)
                    .ok());
    auto verified = verifier.get(pair.lower.friend_number);
    IOTOX_CHECK(verified.ok());
    IOTOX_CHECK(verified.value().local_authority_format ==
                AuthorityLedgerFormat::v2);
    IOTOX_CHECK(verified.value().remote_authorized);
    IOTOX_CHECK(verified.value().remote_principal == owner.value().public_key());
    IOTOX_CHECK(verifier.authorized_at(
        pair.lower.friend_number,
        static_cast<std::uint64_t>(Capability::manage_principals),
        ledger->snapshot()));

    auto no_v2_pair = confirmed_pair();
    const auto v2_feature = iotox::protocol::feature_bit(
        iotox::protocol::Feature::authorization_ledger_v2);
    no_v2_pair.lower.negotiated.shared_features &= ~v2_feature;
    no_v2_pair.higher.negotiated.shared_features &= ~v2_feature;
    PeerAuthorityRegistry unsupported_verifier(sodium.value());
    PeerAuthorityRegistry unsupported_claimant(sodium.value());
    IOTOX_CHECK(unsupported_verifier.synchronize_session(
                    no_v2_pair.lower, ledger->snapshot(), 408U)
                    .ok());
    IOTOX_CHECK(unsupported_claimant.synchronize_session(
                    no_v2_pair.higher, AuthoritySnapshot{}, 408U)
                    .ok());
    auto unsupported_verifier_snapshot =
        unsupported_verifier.get(no_v2_pair.lower.friend_number);
    auto unsupported_claimant_snapshot =
        unsupported_claimant.get(no_v2_pair.higher.friend_number);
    IOTOX_CHECK(unsupported_verifier_snapshot.ok());
    IOTOX_CHECK(unsupported_claimant_snapshot.ok());
    IOTOX_CHECK(!unsupported_verifier_snapshot.value().authority_v2_negotiated);
    IOTOX_CHECK(!unsupported_claimant_snapshot.value().authority_v2_negotiated);
    auto unsupported_challenge = unsupported_verifier.make_challenge_frame(
        no_v2_pair.lower, ledger->snapshot(), authority_nonce(221U),
        12002U, 409U);
    IOTOX_CHECK(!unsupported_challenge.ok());
    IOTOX_CHECK(unsupported_challenge.status().code() ==
                iotox::ErrorCode::unsupported);
    const iotox::Status rejected = unsupported_claimant.receive_challenge(
        no_v2_pair.higher, challenge.value(), 410U);
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.code() == iotox::ErrorCode::unsupported);

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
}
IOTOX_TEST("authority v3 proof binds sync grants and requires v2 plus v3 "
           "negotiation") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory temporary;
    auto device_seed = seed(13U);
    auto owner_seed = seed(77U);
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    auto ledger = bootstrap_ledger(temporary.path() / "authority-v3.ledger",
                                   device.value().public_key(), owner.value(),
                                   sodium.value());

    const auto append_request = [&](const AuthorityPrepareRequest &request) {
        auto body = ledger->prepare(request);
        IOTOX_CHECK_MSG(body.ok(), body.status().message());
        auto record = sign_authority_record_body(
            body.value(), owner.value().secret_key(), sodium.value());
        IOTOX_CHECK_MSG(record.ok(), record.status().message());
        IOTOX_CHECK_MSG(ledger->append(record.value()).ok(),
                        "v3 session authority fixture must append");
    };

    AuthorityPrepareRequest migrate_v2;
    migrate_v2.action = AuthorityAction::migrate_v2;
    migrate_v2.role = PrincipalRole::owner;
    migrate_v2.capabilities = kAuthorityV1Capabilities;
    migrate_v2.issuer = owner.value().public_key();
    migrate_v2.subject = owner.value().public_key();
    append_request(migrate_v2);

    AuthorityPrepareRequest migrate_v3;
    migrate_v3.action = AuthorityAction::migrate_v3;
    migrate_v3.role = PrincipalRole::owner;
    migrate_v3.capabilities = kAuthorityV1Capabilities;
    migrate_v3.issuer = owner.value().public_key();
    migrate_v3.subject = owner.value().public_key();
    append_request(migrate_v3);

    AuthorityPrepareRequest activate_sync;
    activate_sync.action = AuthorityAction::grant;
    activate_sync.role = PrincipalRole::owner;
    activate_sync.capabilities = kAuthorityV3Capabilities;
    activate_sync.issuer = owner.value().public_key();
    activate_sync.subject = owner.value().public_key();
    append_request(activate_sync);
    IOTOX_CHECK(ledger->snapshot().format == AuthorityLedgerFormat::v3);

    auto pair = confirmed_pair();
    const std::uint64_t v2_feature = iotox::protocol::feature_bit(
        iotox::protocol::Feature::authorization_ledger_v2);
    const std::uint64_t v3_feature = iotox::protocol::feature_bit(
        iotox::protocol::Feature::authorization_ledger_v3);
    IOTOX_CHECK((pair.lower.negotiated.shared_features & v2_feature) != 0U);
    IOTOX_CHECK((pair.lower.negotiated.shared_features & v3_feature) != 0U);

    PeerAuthorityRegistry verifier(sodium.value());
    PeerAuthorityRegistry claimant(sodium.value());
    IOTOX_CHECK(
        verifier.synchronize_session(pair.lower, ledger->snapshot(), 500U)
            .ok());
    IOTOX_CHECK(
        claimant.synchronize_session(pair.higher, AuthoritySnapshot{}, 500U)
            .ok());
    auto negotiation = verifier.get(pair.lower.friend_number);
    IOTOX_CHECK(negotiation.ok());
    IOTOX_CHECK(negotiation.value().authority_v2_negotiated);
    IOTOX_CHECK(negotiation.value().authority_v3_negotiated);

    auto challenge = verifier.make_challenge_frame(
        pair.lower, ledger->snapshot(), authority_nonce(231U), 14001U, 501U);
    IOTOX_CHECK_MSG(challenge.ok(), challenge.status().message());
    IOTOX_CHECK(challenge.value().payload[4U] == kAuthorityChallengeFormatV3);
    IOTOX_CHECK(challenge.value().payload[5U] ==
                static_cast<std::uint8_t>(AuthorityLedgerFormat::v3));
    IOTOX_CHECK(
        verifier.mark_challenge_sent(pair.lower.friend_number, 14001U, 502U)
            .ok());
    IOTOX_CHECK(
        claimant.receive_challenge(pair.higher, challenge.value(), 503U).ok());

    auto proof_body = claimant.prepare_proof_body(
        pair.higher.friend_number, owner.value().public_key(), 504U);
    IOTOX_CHECK_MSG(proof_body.ok(), proof_body.status().message());
    IOTOX_CHECK(proof_body.value()[4U] == kAuthorityProofFormatV3);
    IOTOX_CHECK(proof_body.value()[5U] ==
                static_cast<std::uint8_t>(AuthorityLedgerFormat::v3));
    auto proof_bytes = sign_authority_proof_body(
        proof_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK_MSG(proof_bytes.ok(), proof_bytes.status().message());
    auto proof = claimant.make_proof_frame(pair.higher, proof_bytes.value(),
                                           15001U, 505U);
    IOTOX_CHECK_MSG(proof.ok(), proof.status().message());
    IOTOX_CHECK(
        claimant.mark_proof_sent(pair.higher.friend_number, 15001U, 506U).ok());
    IOTOX_CHECK(
        verifier.receive_proof(pair.lower, proof.value(), *ledger, 507U).ok());
    const auto sync_activate =
        static_cast<std::uint64_t>(Capability::sync_activate);
    IOTOX_CHECK(verifier.authorized_at(pair.lower.friend_number, sync_activate,
                                       ledger->snapshot()));

    // A v3 marker cannot borrow the exact v2 proof signature domain.
    auto decoded = decode_authority_proof(proof_bytes.value());
    IOTOX_CHECK(decoded.ok());
    auto cross_domain = proof_bytes.value();
    cross_domain[4U] = kAuthorityProofFormatV2;
    cross_domain[5U] = static_cast<std::uint8_t>(AuthorityLedgerFormat::v2);
    auto decoded_cross_domain = decode_authority_proof(cross_domain);
    IOTOX_CHECK(decoded_cross_domain.ok());
    IOTOX_CHECK(
        !verify_authority_proof(decoded_cross_domain.value(), sodium.value())
             .ok());

    for (const std::uint64_t missing : {v3_feature, v2_feature}) {
        auto unsupported = confirmed_pair();
        unsupported.lower.negotiated.shared_features &= ~missing;
        unsupported.higher.negotiated.shared_features &= ~missing;
        PeerAuthorityRegistry unsupported_verifier(sodium.value());
        IOTOX_CHECK(unsupported_verifier
                        .synchronize_session(unsupported.lower,
                                             ledger->snapshot(), 508U)
                        .ok());
        auto snapshot =
            unsupported_verifier.get(unsupported.lower.friend_number);
        IOTOX_CHECK(snapshot.ok());
        IOTOX_CHECK(!snapshot.value().authority_v3_negotiated);
        auto rejected = unsupported_verifier.make_challenge_frame(
            unsupported.lower, ledger->snapshot(), authority_nonce(241U),
            14002U, 509U);
        IOTOX_CHECK(!rejected.ok());
        IOTOX_CHECK(rejected.status().code() == iotox::ErrorCode::unsupported);
    }

    secure_wipe(device_seed);
    secure_wipe(owner_seed);
}
