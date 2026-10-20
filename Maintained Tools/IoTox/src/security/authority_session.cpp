#include "iotox/security/authority_session.hpp"

#include <algorithm>
#include <array>
#include <iomanip>
#include <sstream>
#include <string_view>

namespace iotox::security {
namespace {

constexpr std::array<std::uint8_t, 4U> kChallengeMagic{'I', 'A', 'C', '1'};
constexpr std::array<std::uint8_t, 4U> kProofMagic{'I', 'A', 'P', '1'};
constexpr std::string_view kTranscriptDigestDomain =
    "iotox-session-transcript-v1";
constexpr std::string_view kProofSignatureDomainV1 =
    "iotox-authority-session-proof-v1";
constexpr std::string_view kProofSignatureDomainV2 =
    "iotox-authority-session-proof-v2";

constexpr std::string_view kProofSignatureDomainV3 =
    "iotox-authority-session-proof-v3";

bool known_authority_format(AuthorityLedgerFormat format) noexcept {
    return format == AuthorityLedgerFormat::v1 ||
           format == AuthorityLedgerFormat::v2 ||
           format == AuthorityLedgerFormat::v3;
}

bool session_supports_authority_format(
    const protocol::PeerSessionSnapshot &session,
    AuthorityLedgerFormat format) noexcept {
    const std::uint64_t shared = session.negotiated.shared_features;
    if (format == AuthorityLedgerFormat::v3) {
        return (shared & protocol::feature_bit(
                             protocol::Feature::authorization_ledger_v2)) !=
                   0U &&
               (shared & protocol::feature_bit(
                             protocol::Feature::authorization_ledger_v3)) != 0U;
    }
    const auto required = format == AuthorityLedgerFormat::v2
                              ? protocol::Feature::authorization_ledger_v2
                              : protocol::Feature::authorization_ledger_v1;
    return (shared & protocol::feature_bit(required)) != 0U;
}

std::uint8_t challenge_wire_format(
    AuthorityLedgerFormat format) noexcept {
    if (format == AuthorityLedgerFormat::v3) {
        return kAuthorityChallengeFormatV3;
    }
    return format == AuthorityLedgerFormat::v2 ? kAuthorityChallengeFormatV2
                                               : kAuthorityChallengeFormatV1;
}

std::uint8_t proof_wire_format(AuthorityLedgerFormat format) noexcept {
    if (format == AuthorityLedgerFormat::v3) {
        return kAuthorityProofFormatV3;
    }
    return format == AuthorityLedgerFormat::v2 ? kAuthorityProofFormatV2
                                               : kAuthorityProofFormatV1;
}

Result<AuthorityLedgerFormat> decode_challenge_authority_format(
    std::span<const std::uint8_t> bytes) {
    if (bytes[4U] == kAuthorityChallengeFormatV1) {
        if (bytes[5U] != 0U || bytes[6U] != 0U || bytes[7U] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority challenge v1 reserved bytes are nonzero"};
        }
        return AuthorityLedgerFormat::v1;
    }
    if (bytes[4U] == kAuthorityChallengeFormatV2) {
        if (bytes[5U] != static_cast<std::uint8_t>(AuthorityLedgerFormat::v2) ||
            bytes[6U] != 0U || bytes[7U] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority challenge v2 ledger format or reserved bytes are invalid"};
        }
        return AuthorityLedgerFormat::v2;
    }
    if (bytes[4U] == kAuthorityChallengeFormatV3) {
        if (bytes[5U] != static_cast<std::uint8_t>(AuthorityLedgerFormat::v3) ||
            bytes[6U] != 0U || bytes[7U] != 0U) {
            return Status{
                ErrorCode::protocol_error,
                "authority challenge v3 ledger format or reserved bytes are invalid"};
        }
        return AuthorityLedgerFormat::v3;
    }
    return Status{ErrorCode::unsupported,
                  "authority challenge format is unsupported"};
}

Result<AuthorityLedgerFormat> decode_proof_authority_format(
    std::span<const std::uint8_t> bytes) {
    if (bytes[4U] == kAuthorityProofFormatV1) {
        if (bytes[5U] != 0U || bytes[6U] != 0U || bytes[7U] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority proof v1 reserved bytes are nonzero"};
        }
        return AuthorityLedgerFormat::v1;
    }
    if (bytes[4U] == kAuthorityProofFormatV2) {
        if (bytes[5U] != static_cast<std::uint8_t>(AuthorityLedgerFormat::v2) ||
            bytes[6U] != 0U || bytes[7U] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority proof v2 ledger format or reserved bytes are invalid"};
        }
        return AuthorityLedgerFormat::v2;
    }
    if (bytes[4U] == kAuthorityProofFormatV3) {
        if (bytes[5U] != static_cast<std::uint8_t>(AuthorityLedgerFormat::v3) ||
            bytes[6U] != 0U || bytes[7U] != 0U) {
            return Status{
                ErrorCode::protocol_error,
                "authority proof v3 ledger format or reserved bytes are invalid"};
        }
        return AuthorityLedgerFormat::v3;
    }
    return Status{ErrorCode::unsupported,
                  "authority proof body format is unsupported"};
}

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    std::uint8_t combined = 0U;
    for (const std::uint8_t byte : bytes) {
        combined = static_cast<std::uint8_t>(combined | byte);
    }
    return combined == 0U;
}

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output[offset++] = static_cast<std::uint8_t>(
            (value >> static_cast<unsigned>(shift)) & 0xFFU);
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

template <std::size_t N>
void copy_field(std::span<const std::uint8_t> input, std::size_t offset,
                std::array<std::uint8_t, N> &output) {
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset), N,
                output.begin());
}

template <std::size_t N>
void write_field(std::span<std::uint8_t> output, std::size_t offset,
                 const std::array<std::uint8_t, N> &value) {
    std::copy(value.begin(), value.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
}

Status validate_challenge(const AuthorityChallenge &challenge) {
    if (!known_authority_format(challenge.authority_format)) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge ledger format is unknown"};
    }
    if (all_zero(challenge.verifier_device)) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge verifier device is zero"};
    }
    if (challenge.ownership_epoch == 0U ||
        challenge.authority_sequence == 0U) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge requires a nonzero ledger epoch and sequence"};
    }
    if (all_zero(challenge.authority_tail_digest)) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge ledger tail digest is zero"};
    }
    if (all_zero(challenge.session_transcript_digest)) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge session transcript digest is zero"};
    }
    if (all_zero(challenge.nonce)) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge nonce is zero"};
    }
    return Status::success();
}

Status validate_proof_fields(const AuthorityProof &proof) {
    if (!known_authority_format(proof.authority_format)) {
        return Status{ErrorCode::protocol_error,
                      "authority proof ledger format is unknown"};
    }
    if (all_zero(proof.verifier_device)) {
        return Status{ErrorCode::protocol_error,
                      "authority proof verifier device is zero"};
    }
    if (all_zero(proof.claimant_principal)) {
        return Status{ErrorCode::protocol_error,
                      "authority proof claimant principal is zero"};
    }
    if (proof.ownership_epoch == 0U || proof.authority_sequence == 0U) {
        return Status{ErrorCode::protocol_error,
                      "authority proof requires a nonzero ledger epoch and sequence"};
    }
    if (all_zero(proof.authority_tail_digest)) {
        return Status{ErrorCode::protocol_error,
                      "authority proof ledger tail digest is zero"};
    }
    if (all_zero(proof.session_transcript_digest)) {
        return Status{ErrorCode::protocol_error,
                      "authority proof session transcript digest is zero"};
    }
    if (all_zero(proof.challenge_nonce)) {
        return Status{ErrorCode::protocol_error,
                      "authority proof challenge nonce is zero"};
    }
    if (proof.challenge_message_id == 0U) {
        return Status{ErrorCode::protocol_error,
                      "authority proof challenge message identifier zero is reserved"};
    }
    return Status::success();
}

Result<AuthorityProof> decode_authority_proof_body(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kAuthorityProofBodyBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority proof body has an unexpected length"};
    }
    if (!std::equal(kProofMagic.begin(), kProofMagic.end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "authority proof body magic is invalid"};
    }
    auto authority_format = decode_proof_authority_format(bytes);
    if (!authority_format) {
        return authority_format.status();
    }

    AuthorityProof proof;
    proof.authority_format = authority_format.value();
    copy_field(bytes, 8U, proof.verifier_device);
    copy_field(bytes, 40U, proof.claimant_principal);
    proof.ownership_epoch = read_u64(bytes, 72U);
    proof.authority_sequence = read_u64(bytes, 80U);
    copy_field(bytes, 88U, proof.authority_tail_digest);
    copy_field(bytes, 120U, proof.session_transcript_digest);
    copy_field(bytes, 152U, proof.challenge_nonce);
    proof.challenge_message_id = read_u64(bytes, 184U);
    const Status valid = validate_proof_fields(proof);
    if (!valid.ok()) {
        return valid;
    }
    return proof;
}

Result<std::vector<std::uint8_t>> signature_message(
    std::span<const std::uint8_t, kAuthorityProofBodyBytes> body) {
    auto authority_format = decode_proof_authority_format(body);
    if (!authority_format) {
        return authority_format.status();
    }
    const std::string_view domain =
        authority_format.value() == AuthorityLedgerFormat::v3
            ? kProofSignatureDomainV3
            : (authority_format.value() == AuthorityLedgerFormat::v2
                   ? kProofSignatureDomainV2
                   : kProofSignatureDomainV1);
    // Keep the same explicit signature-domain envelope used by authority
    // records, but with an independent permanent domain string.
    constexpr std::array<std::uint8_t, 7U> kMagic{
        'I', 'O', 'T', 'O', 'X', 'S', '1'};
    std::vector<std::uint8_t> message;
    message.reserve(kMagic.size() + 2U + domain.size() + body.size());
    message.insert(message.end(), kMagic.begin(), kMagic.end());
    message.push_back(static_cast<std::uint8_t>(
        (domain.size() >> 8U) & 0xFFU));
    message.push_back(static_cast<std::uint8_t>(
        domain.size() & 0xFFU));
    message.insert(message.end(), domain.begin(), domain.end());
    message.insert(message.end(), body.begin(), body.end());
    return message;
}

bool challenge_matches_proof(const AuthorityChallenge &challenge,
                             std::uint64_t challenge_message_id,
                             const AuthorityProof &proof) noexcept {
    return challenge.authority_format == proof.authority_format &&
           challenge.verifier_device == proof.verifier_device &&
           challenge.ownership_epoch == proof.ownership_epoch &&
           challenge.authority_sequence == proof.authority_sequence &&
           challenge.authority_tail_digest == proof.authority_tail_digest &&
           challenge.session_transcript_digest ==
               proof.session_transcript_digest &&
           challenge.nonce == proof.challenge_nonce &&
           challenge_message_id == proof.challenge_message_id;
}

AuthorityChallenge challenge_from_snapshot(
    const PeerAuthoritySnapshot &snapshot) {
    AuthorityChallenge challenge;
    challenge.authority_format = snapshot.peer_authority_format;
    challenge.verifier_device = snapshot.peer_verifier_device;
    challenge.ownership_epoch = snapshot.peer_authority_epoch;
    challenge.authority_sequence = snapshot.peer_authority_sequence;
    challenge.authority_tail_digest = snapshot.peer_authority_tail_digest;
    challenge.session_transcript_digest = snapshot.session_transcript_digest;
    challenge.nonce = snapshot.peer_challenge_nonce;
    return challenge;
}

void clear_remote_authorization(PeerAuthoritySnapshot &snapshot) {
    snapshot.remote_authorized = false;
    snapshot.remote_principal.fill(0U);
    snapshot.remote_role = PrincipalRole::none;
    snapshot.remote_capabilities = 0U;
    snapshot.peer_proof_message_id = 0U;
}

template <typename EntryType>
void reset_verifier(EntryType &entry, const AuthoritySnapshot &authority,
                    std::uint64_t now_unix_ms) {
    entry.snapshot.local_authority_format = authority.format;
    entry.snapshot.local_authority_epoch = authority.ownership_epoch;
    entry.snapshot.local_authority_sequence = authority.sequence;
    entry.snapshot.local_authority_tail_digest = authority.tail_digest;
    entry.snapshot.local_challenge_message_id = 0U;
    entry.snapshot.local_challenge_nonce.fill(0U);
    entry.snapshot.challenge_send_attempts = 0U;
    entry.snapshot.peer_proof_candidate_count = 0U;
    entry.snapshot.last_challenge_send_error_code = ErrorCode::ok;
    entry.snapshot.last_challenge_send_error.clear();
    clear_remote_authorization(entry.snapshot);
    entry.frozen_local_challenge_payload.clear();
    entry.frozen_peer_proof_payload.clear();
    if (authority.initialized) {
        entry.snapshot.verifier_state = AuthorityVerifierState::challenge_ready;
        entry.snapshot.verifier_detail = "fresh authority challenge required";
    } else {
        entry.snapshot.verifier_state = AuthorityVerifierState::inactive;
        entry.snapshot.verifier_detail = "local authority ledger is uninitialized";
    }
    entry.snapshot.updated_unix_ms = now_unix_ms;
}

}  // namespace

Result<Digest> authority_session_transcript_digest(
    const protocol::PeerSessionSnapshot &session, const Sodium &sodium) {
    auto transcript = protocol::encode_canonical_session_transcript(session);
    if (!transcript) {
        return transcript.status();
    }
    return sodium.hash(kTranscriptDigestDomain, transcript.value());
}

Result<AuthorityChallengeBytes> encode_authority_challenge(
    const AuthorityChallenge &challenge) {
    const Status valid = validate_challenge(challenge);
    if (!valid.ok()) {
        return valid;
    }
    AuthorityChallengeBytes output{};
    std::copy(kChallengeMagic.begin(), kChallengeMagic.end(), output.begin());
    output[4U] = challenge_wire_format(challenge.authority_format);
    if (challenge.authority_format != AuthorityLedgerFormat::v1) {
        output[5U] = static_cast<std::uint8_t>(challenge.authority_format);
    }
    write_field(output, 8U, challenge.verifier_device);
    write_u64(output, 40U, challenge.ownership_epoch);
    write_u64(output, 48U, challenge.authority_sequence);
    write_field(output, 56U, challenge.authority_tail_digest);
    write_field(output, 88U, challenge.session_transcript_digest);
    write_field(output, 120U, challenge.nonce);
    return output;
}

Result<AuthorityChallenge> decode_authority_challenge(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kAuthorityChallengeBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge has an unexpected length"};
    }
    if (!std::equal(kChallengeMagic.begin(), kChallengeMagic.end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge magic is invalid"};
    }
    auto authority_format = decode_challenge_authority_format(bytes);
    if (!authority_format) {
        return authority_format.status();
    }
    for (std::size_t index : {152U, 153U, 154U, 155U,
                              156U, 157U, 158U, 159U}) {
        if (bytes[index] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority challenge reserved bytes are nonzero"};
        }
    }

    AuthorityChallenge challenge;
    challenge.authority_format = authority_format.value();
    copy_field(bytes, 8U, challenge.verifier_device);
    challenge.ownership_epoch = read_u64(bytes, 40U);
    challenge.authority_sequence = read_u64(bytes, 48U);
    copy_field(bytes, 56U, challenge.authority_tail_digest);
    copy_field(bytes, 88U, challenge.session_transcript_digest);
    copy_field(bytes, 120U, challenge.nonce);
    const Status valid = validate_challenge(challenge);
    if (!valid.ok()) {
        return valid;
    }
    return challenge;
}

Result<AuthorityProofBody> encode_authority_proof_body(
    const AuthorityProof &proof) {
    const Status valid = validate_proof_fields(proof);
    if (!valid.ok()) {
        return valid;
    }
    AuthorityProofBody output{};
    std::copy(kProofMagic.begin(), kProofMagic.end(), output.begin());
    output[4U] = proof_wire_format(proof.authority_format);
    if (proof.authority_format != AuthorityLedgerFormat::v1) {
        output[5U] = static_cast<std::uint8_t>(proof.authority_format);
    }
    write_field(output, 8U, proof.verifier_device);
    write_field(output, 40U, proof.claimant_principal);
    write_u64(output, 72U, proof.ownership_epoch);
    write_u64(output, 80U, proof.authority_sequence);
    write_field(output, 88U, proof.authority_tail_digest);
    write_field(output, 120U, proof.session_transcript_digest);
    write_field(output, 152U, proof.challenge_nonce);
    write_u64(output, 184U, proof.challenge_message_id);
    return output;
}

Result<AuthorityProof> decode_authority_proof(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kAuthorityProofBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority proof has an unexpected length"};
    }
    auto proof = decode_authority_proof_body(
        bytes.first(kAuthorityProofBodyBytes));
    if (!proof) {
        return proof.status();
    }
    copy_field(bytes, kAuthorityProofBodyBytes, proof.value().signature);
    return std::move(proof).value();
}

Result<AuthorityProofBytes> sign_authority_proof_body(
    std::span<const std::uint8_t, kAuthorityProofBodyBytes> body,
    std::span<const std::uint8_t, kSigningSecretKeyBytes> secret_key,
    const Sodium &sodium) {
    auto decoded = decode_authority_proof_body(body);
    if (!decoded) {
        return decoded.status();
    }
    auto message = signature_message(body);
    if (!message) {
        return message.status();
    }
    auto signature = sodium.sign_detached(message.value(), secret_key);
    if (!signature) {
        return signature.status();
    }
    AuthorityProofBytes output{};
    std::copy(body.begin(), body.end(), output.begin());
    std::copy(signature.value().begin(), signature.value().end(),
              output.begin() + static_cast<std::ptrdiff_t>(body.size()));
    return output;
}

Result<AuthorityProofBytes> sign_authority_proof_body(
    std::span<const std::uint8_t, kAuthorityProofBodyBytes> body,
    const DeviceIdentity &identity) {
    auto decoded = decode_authority_proof_body(body);
    if (!decoded) {
        return decoded.status();
    }
    if (!constant_time_equal(
            decoded.value().claimant_principal, identity.public_key())) {
        return Status{
            ErrorCode::invalid_argument,
            "authority proof claimant does not match the stable device identity"};
    }
    auto message = signature_message(body);
    if (!message) {
        return message.status();
    }
    auto signature = identity.sign(message.value());
    if (!signature) {
        return signature.status();
    }
    AuthorityProofBytes output{};
    std::copy(body.begin(), body.end(), output.begin());
    std::copy(signature.value().begin(), signature.value().end(),
              output.begin() + static_cast<std::ptrdiff_t>(body.size()));
    return output;
}

Status verify_authority_proof(const AuthorityProof &proof,
                              const Sodium &sodium) {
    auto body = encode_authority_proof_body(proof);
    if (!body) {
        return body.status();
    }
    auto message = signature_message(body.value());
    if (!message) {
        return message.status();
    }
    return sodium.verify_detached(
        proof.signature, message.value(), proof.claimant_principal);
}

Status validate_authority_challenge_frame(
    const protocol::PeerSessionSnapshot &session,
    const protocol::Frame &frame) {
    const Status admitted =
        protocol::validate_application_frame_for_session(session, frame);
    if (!admitted.ok()) {
        return admitted;
    }
    if ((session.negotiated.shared_features & protocol::feature_bit(
             protocol::Feature::authorization_ledger_v1)) == 0U) {
        return Status{ErrorCode::unsupported,
                      "authority challenge requires the negotiated authority-ledger-v1 feature"};
    }
    if (frame.type != protocol::MessageType::authority_challenge ||
        frame.flags != 0U || frame.message_id == 0U ||
        frame.correlation_id != session.local_confirmation_message_id ||
        frame.sequence != kAuthorityChallengeSequence ||
        frame.expiry_unix_ms != 0U ||
        frame.payload.size() != kAuthorityChallengeBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority challenge frame is not canonical"};
    }
    return Status::success();
}

Status validate_authority_proof_frame(
    const protocol::PeerSessionSnapshot &session,
    std::uint64_t expected_challenge_message_id,
    const protocol::Frame &frame) {
    const Status admitted =
        protocol::validate_application_frame_for_session(session, frame);
    if (!admitted.ok()) {
        return admitted;
    }
    if ((session.negotiated.shared_features & protocol::feature_bit(
             protocol::Feature::authorization_ledger_v1)) == 0U) {
        return Status{ErrorCode::unsupported,
                      "authority proof requires the negotiated authority-ledger-v1 feature"};
    }
    if (expected_challenge_message_id == 0U) {
        return Status{ErrorCode::unavailable,
                      "authority proof arrived before a local challenge"};
    }
    if (frame.type != protocol::MessageType::authority_proof ||
        frame.flags != 0U || frame.message_id == 0U ||
        frame.correlation_id != expected_challenge_message_id ||
        frame.sequence != kAuthorityProofSequence ||
        frame.expiry_unix_ms != 0U ||
        frame.payload.size() != kAuthorityProofBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority proof frame is not canonical"};
    }
    return Status::success();
}

std::string to_string(AuthorityVerifierState state) {
    switch (state) {
        case AuthorityVerifierState::inactive: return "inactive";
        case AuthorityVerifierState::challenge_ready: return "challenge-ready";
        case AuthorityVerifierState::challenge_send_failed: return "challenge-send-failed";
        case AuthorityVerifierState::awaiting_proof: return "awaiting-proof";
        case AuthorityVerifierState::authorized: return "authorized";
        case AuthorityVerifierState::denied: return "denied";
        case AuthorityVerifierState::malformed_proof: return "malformed-proof";
        case AuthorityVerifierState::conflicting_proof: return "conflicting-proof";
        case AuthorityVerifierState::stale_ledger: return "stale-ledger";
    }
    return "unknown";
}

std::string to_string(AuthorityClaimantState state) {
    switch (state) {
        case AuthorityClaimantState::inactive: return "inactive";
        case AuthorityClaimantState::awaiting_challenge: return "awaiting-challenge";
        case AuthorityClaimantState::challenge_received: return "challenge-received";
        case AuthorityClaimantState::malformed_challenge: return "malformed-challenge";
        case AuthorityClaimantState::conflicting_challenge: return "conflicting-challenge";
        case AuthorityClaimantState::proof_ready: return "proof-ready";
        case AuthorityClaimantState::proof_send_failed: return "proof-send-failed";
        case AuthorityClaimantState::proof_sent: return "proof-sent";
    }
    return "unknown";
}

std::string render_peer_authority(const PeerAuthoritySnapshot &snapshot) {
    std::ostringstream output;
    output << "friend-number=" << snapshot.friend_number << '\n'
           << "transport-public-key=" << snapshot.transport_public_key << '\n'
           << "connected=" << (snapshot.connected ? 1 : 0) << '\n'
           << "online-epoch=" << snapshot.online_epoch << '\n'
           << "feature-negotiated=" << (snapshot.feature_negotiated ? 1 : 0)
           << '\n'
           << "authority-v2-negotiated="
           << (snapshot.authority_v2_negotiated ? 1 : 0) << '\n'
           << "authority-v3-negotiated="
           << (snapshot.authority_v3_negotiated ? 1 : 0) << '\n'
           << "session-transcript-digest="
           << hex(snapshot.session_transcript_digest) << '\n'
           << "verifier-state=" << to_string(snapshot.verifier_state) << '\n'
           << "remote-authorized=" << (snapshot.remote_authorized ? 1 : 0)
           << '\n'
           << "remote-principal=" << hex(snapshot.remote_principal) << '\n'
           << "remote-role=" << to_string(snapshot.remote_role) << '\n'
           << "remote-capabilities="
           << render_capability_set(snapshot.remote_capabilities) << '\n'
           << "local-authority-format="
           << to_string(snapshot.local_authority_format) << '\n'
           << "local-authority-epoch=" << snapshot.local_authority_epoch << '\n'
           << "local-authority-sequence=" << snapshot.local_authority_sequence
           << '\n'
           << "local-authority-tail-digest="
           << hex(snapshot.local_authority_tail_digest) << '\n'
           << "local-challenge-message-id="
           << snapshot.local_challenge_message_id << '\n'
           << "challenge-send-attempts=" << snapshot.challenge_send_attempts
           << '\n'
           << "peer-proof-message-id=" << snapshot.peer_proof_message_id << '\n'
           << "verifier-detail=" << snapshot.verifier_detail << '\n'
           << "claimant-state=" << to_string(snapshot.claimant_state) << '\n'
           << "peer-verifier-device=" << hex(snapshot.peer_verifier_device)
           << '\n'
           << "peer-authority-format="
           << to_string(snapshot.peer_authority_format) << '\n'
           << "peer-authority-epoch=" << snapshot.peer_authority_epoch << '\n'
           << "peer-authority-sequence=" << snapshot.peer_authority_sequence
           << '\n'
           << "peer-authority-tail-digest="
           << hex(snapshot.peer_authority_tail_digest) << '\n'
           << "peer-challenge-message-id=" << snapshot.peer_challenge_message_id
           << '\n'
           << "local-claimant-principal="
           << hex(snapshot.local_claimant_principal) << '\n'
           << "peer-proof-candidate-count="
           << static_cast<unsigned>(snapshot.peer_proof_candidate_count) << '\n'
           << "local-proof-message-id=" << snapshot.local_proof_message_id
           << '\n'
           << "proof-send-attempts=" << snapshot.proof_send_attempts << '\n'
           << "claimant-detail=" << snapshot.claimant_detail << '\n'
           << "updated-unix-ms=" << snapshot.updated_unix_ms << '\n';
    if (!snapshot.last_challenge_send_error.empty()) {
        output << "last-challenge-send-error="
               << snapshot.last_challenge_send_error << '\n';
    }
    if (!snapshot.last_proof_send_error.empty()) {
        output << "last-proof-send-error="
               << snapshot.last_proof_send_error << '\n';
    }
    return output.str();
}

bool PeerAuthorityRegistry::same_session(
    const PeerAuthoritySnapshot &authority,
    const protocol::PeerSessionSnapshot &session,
    const Digest &transcript_digest) noexcept {
    return authority.friend_number == session.friend_number &&
           authority.transport_public_key == session.public_key &&
           authority.online_epoch == session.online_epoch &&
           authority.connected == session.connected &&
           authority.feature_negotiated &&
           authority.session_transcript_digest == transcript_digest;
}

bool PeerAuthorityRegistry::ledger_matches_challenge(
    const AuthoritySnapshot &ledger,
    const AuthorityChallenge &challenge) noexcept {
    return ledger.initialized && ledger.format == challenge.authority_format &&
           ledger.device == challenge.verifier_device &&
           ledger.ownership_epoch == challenge.ownership_epoch &&
           ledger.sequence == challenge.authority_sequence &&
           ledger.tail_digest == challenge.authority_tail_digest;
}

Status PeerAuthorityRegistry::validate_initialized_authority(
    const AuthoritySnapshot &authority) {
    if (!authority.initialized || !known_authority_format(authority.format) ||
        authority.ownership_epoch == 0U ||
        authority.sequence == 0U || all_zero(authority.device) ||
        all_zero(authority.tail_digest)) {
        return Status{ErrorCode::unavailable,
                      "local authority ledger is not initialized"};
    }
    return Status::success();
}

Status PeerAuthorityRegistry::synchronize_session(
    const protocol::PeerSessionSnapshot &session,
    const AuthoritySnapshot &local_authority,
    std::uint64_t now_unix_ms) {
    const bool ready = protocol::is_application_ready(session);
    const bool feature = ready &&
        (session.negotiated.shared_features & protocol::feature_bit(
             protocol::Feature::authorization_ledger_v1)) != 0U;
    const bool authority_v2 = feature &&
        (session.negotiated.shared_features & protocol::feature_bit(
             protocol::Feature::authorization_ledger_v2)) != 0U;

    const bool authority_v3 =
        authority_v2 &&
        (session.negotiated.shared_features &
         protocol::feature_bit(protocol::Feature::authorization_ledger_v3)) !=
            0U;

    Digest digest{};
    if (feature) {
        auto computed = authority_session_transcript_digest(session, *sodium_);
        if (!computed) {
            return computed.status();
        }
        digest = computed.value();
    }

    std::scoped_lock lock(mutex_);
    Entry &entry = entries_[session.friend_number];
    if (!feature) {
        entry = Entry{};
        entry.snapshot.friend_number = session.friend_number;
        entry.snapshot.transport_public_key = session.public_key;
        entry.snapshot.online_epoch = session.online_epoch;
        entry.snapshot.connected = session.connected;
        entry.snapshot.feature_negotiated = false;
        entry.snapshot.authority_v2_negotiated = false;
        entry.snapshot.authority_v3_negotiated = false;
        entry.snapshot.verifier_detail =
            ready ? "peer did not negotiate authority-ledger-v1"
                  : "protocol session is not transcript-confirmed";
        entry.snapshot.claimant_detail = entry.snapshot.verifier_detail;
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return Status::success();
    }

    if (!same_session(entry.snapshot, session, digest)) {
        entry = Entry{};
        entry.snapshot.friend_number = session.friend_number;
        entry.snapshot.transport_public_key = session.public_key;
        entry.snapshot.online_epoch = session.online_epoch;
        entry.snapshot.connected = true;
        entry.snapshot.feature_negotiated = true;
        entry.snapshot.authority_v2_negotiated = authority_v2;
        entry.snapshot.authority_v3_negotiated = authority_v3;
        entry.snapshot.session_transcript_digest = digest;
        entry.snapshot.claimant_state = AuthorityClaimantState::awaiting_challenge;
        entry.snapshot.claimant_detail = "awaiting peer authority challenge";
        reset_verifier(entry, local_authority, now_unix_ms);
        return Status::success();
    }

    const bool ledger_changed =
        entry.snapshot.local_authority_format != local_authority.format ||
        entry.snapshot.local_authority_epoch != local_authority.ownership_epoch ||
        entry.snapshot.local_authority_sequence != local_authority.sequence ||
        entry.snapshot.local_authority_tail_digest != local_authority.tail_digest ||
        (entry.snapshot.verifier_state == AuthorityVerifierState::inactive &&
         local_authority.initialized);
    if (ledger_changed) {
        reset_verifier(entry, local_authority, now_unix_ms);
    }
    entry.snapshot.authority_v2_negotiated = authority_v2;
    entry.snapshot.authority_v3_negotiated = authority_v3;
    entry.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

Status PeerAuthorityRegistry::peer_offline(
    std::uint32_t friend_number, std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "authority session does not exist for friend"};
    }
    const std::string key = found->second.snapshot.transport_public_key;
    const std::uint64_t epoch = found->second.snapshot.online_epoch;
    found->second = Entry{};
    found->second.snapshot.friend_number = friend_number;
    found->second.snapshot.transport_public_key = key;
    found->second.snapshot.online_epoch = epoch;
    found->second.snapshot.connected = false;
    found->second.snapshot.verifier_detail = "transport peer is offline";
    found->second.snapshot.claimant_detail = "transport peer is offline";
    found->second.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

void PeerAuthorityRegistry::erase(std::uint32_t friend_number) {
    std::scoped_lock lock(mutex_);
    entries_.erase(friend_number);
}

Result<protocol::Frame> PeerAuthorityRegistry::make_challenge_frame(
    const protocol::PeerSessionSnapshot &session,
    const AuthoritySnapshot &local_authority,
    const AuthorityNonce &nonce,
    std::uint64_t message_id,
    std::uint64_t now_unix_ms) {
    const Status initialized = validate_initialized_authority(local_authority);
    if (!initialized.ok()) {
        return initialized;
    }
    if (message_id == 0U || all_zero(nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "authority challenge requires nonzero random material"};
    }
    if (!session_supports_authority_format(session, local_authority.format)) {
        return Status{ErrorCode::unsupported,
                      "peer did not negotiate the active authority ledger format"};
    }
    const Status frame_session = protocol::is_application_ready(session)
        ? Status::success()
        : Status{ErrorCode::unavailable,
                 "authority challenge requires a confirmed session"};
    if (!frame_session.ok()) {
        return frame_session;
    }
    auto digest_result = authority_session_transcript_digest(session, *sodium_);
    if (!digest_result) {
        return digest_result.status();
    }

    std::scoped_lock lock(mutex_);
    auto found = entries_.find(session.friend_number);
    if (found == entries_.end() ||
        !same_session(found->second.snapshot, session, digest_result.value())) {
        return Status{ErrorCode::unavailable,
                      "authority registry is not synchronized with this online session"};
    }
    Entry &entry = found->second;
    if (!entry.frozen_local_challenge_payload.empty()) {
        if (entry.snapshot.local_challenge_message_id != message_id ||
            entry.snapshot.local_challenge_nonce != nonce) {
            return Status{ErrorCode::protocol_error,
                          "authority challenge is already frozen for this online epoch"};
        }
    } else {
        AuthorityChallenge challenge;
        challenge.authority_format = local_authority.format;
        challenge.verifier_device = local_authority.device;
        challenge.ownership_epoch = local_authority.ownership_epoch;
        challenge.authority_sequence = local_authority.sequence;
        challenge.authority_tail_digest = local_authority.tail_digest;
        challenge.session_transcript_digest = digest_result.value();
        challenge.nonce = nonce;
        auto payload = encode_authority_challenge(challenge);
        if (!payload) {
            return payload.status();
        }
        entry.frozen_local_challenge_payload.assign(
            payload.value().begin(), payload.value().end());
        entry.snapshot.local_authority_format = local_authority.format;
        entry.snapshot.local_authority_epoch = local_authority.ownership_epoch;
        entry.snapshot.local_authority_sequence = local_authority.sequence;
        entry.snapshot.local_authority_tail_digest = local_authority.tail_digest;
        entry.snapshot.local_challenge_message_id = message_id;
        entry.snapshot.local_challenge_nonce = nonce;
        entry.snapshot.verifier_state = AuthorityVerifierState::challenge_ready;
        entry.snapshot.verifier_detail = "canonical authority challenge reserved";
    }
    entry.snapshot.updated_unix_ms = now_unix_ms;

    protocol::Frame frame;
    frame.major = session.negotiated.selected.major;
    frame.minor = session.negotiated.selected.minor;
    frame.type = protocol::MessageType::authority_challenge;
    frame.message_id = entry.snapshot.local_challenge_message_id;
    frame.correlation_id = session.peer_confirmation_message_id;
    frame.sequence = kAuthorityChallengeSequence;
    frame.payload = entry.frozen_local_challenge_payload;
    return frame;
}

Status PeerAuthorityRegistry::mark_challenge_sent(
    std::uint32_t friend_number, std::uint64_t message_id,
    std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || found->second.frozen_local_challenge_payload.empty() ||
        found->second.snapshot.local_challenge_message_id != message_id) {
        return Status{ErrorCode::not_found,
                      "reserved authority challenge was not found"};
    }
    ++found->second.snapshot.challenge_send_attempts;
    found->second.snapshot.verifier_state = AuthorityVerifierState::awaiting_proof;
    found->second.snapshot.last_challenge_send_error_code = ErrorCode::ok;
    found->second.snapshot.last_challenge_send_error.clear();
    found->second.snapshot.verifier_detail = "authority challenge accepted by transport";
    found->second.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

Status PeerAuthorityRegistry::mark_challenge_send_failed(
    std::uint32_t friend_number, ErrorCode error_code,
    std::string error, std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || found->second.frozen_local_challenge_payload.empty()) {
        return Status{ErrorCode::not_found,
                      "reserved authority challenge was not found"};
    }
    ++found->second.snapshot.challenge_send_attempts;
    found->second.snapshot.verifier_state =
        AuthorityVerifierState::challenge_send_failed;
    found->second.snapshot.last_challenge_send_error_code = error_code;
    found->second.snapshot.last_challenge_send_error = std::move(error);
    found->second.snapshot.verifier_detail = "authority challenge did not enter transport queue";
    found->second.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

Status PeerAuthorityRegistry::receive_challenge(
    const protocol::PeerSessionSnapshot &session,
    const protocol::Frame &frame,
    std::uint64_t now_unix_ms) {
    const Status frame_valid = validate_authority_challenge_frame(session, frame);
    if (!frame_valid.ok()) {
        return frame_valid;
    }
    auto decoded = decode_authority_challenge(frame.payload);
    if (!decoded) {
        return decoded.status();
    }
    if (!session_supports_authority_format(
            session, decoded.value().authority_format)) {
        return Status{ErrorCode::unsupported,
                      "authority challenge uses a ledger format not negotiated by this session"};
    }
    auto digest = authority_session_transcript_digest(session, *sodium_);
    if (!digest) {
        return digest.status();
    }

    std::scoped_lock lock(mutex_);
    auto found = entries_.find(session.friend_number);
    if (found == entries_.end() ||
        !same_session(found->second.snapshot, session, digest.value())) {
        return Status{ErrorCode::unavailable,
                      "authority registry is not synchronized with this online session"};
    }
    Entry &entry = found->second;
    if (decoded.value().session_transcript_digest != digest.value()) {
        entry.snapshot.claimant_state = AuthorityClaimantState::malformed_challenge;
        entry.snapshot.claimant_detail = "peer challenge names a different session transcript";
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return Status{ErrorCode::protocol_error,
                      "authority challenge session transcript digest does not match"};
    }
    if (!entry.frozen_peer_challenge_payload.empty()) {
        if (entry.snapshot.peer_challenge_message_id == frame.message_id &&
            entry.frozen_peer_challenge_payload == frame.payload) {
            return Status::success();
        }
        const bool newer_authority_head =
            decoded.value().ownership_epoch >
                entry.snapshot.peer_authority_epoch ||
            (decoded.value().ownership_epoch ==
                 entry.snapshot.peer_authority_epoch &&
             decoded.value().authority_sequence >
                 entry.snapshot.peer_authority_sequence);
        // A verifier may advance its durable authority head again before the
        // claimant has finished enqueueing the prior proof. The transcript,
        // verifier device, epoch/sequence ordering, and format floor make this
        // an unambiguous successor round. Requiring `proof_sent` here leaves a
        // permanently conflicting claimant when two legitimate grants occur
        // in quick succession. Equal/older heads, verifier replacement, and
        // format downgrade remain conflicts.
        const bool next_authority_round =
            decoded.value().verifier_device ==
                entry.snapshot.peer_verifier_device &&
            static_cast<std::uint8_t>(decoded.value().authority_format) >=
                static_cast<std::uint8_t>(
                    entry.snapshot.peer_authority_format) &&
            newer_authority_head;
        if (!next_authority_round) {
            entry.snapshot.claimant_state =
                AuthorityClaimantState::conflicting_challenge;
            entry.snapshot.claimant_detail =
                "peer changed its authority challenge without completing the prior authority round";
            entry.snapshot.updated_unix_ms = now_unix_ms;
            return Status{ErrorCode::protocol_error,
                          "conflicting authority challenge for one authority round"};
        }
        entry.frozen_peer_challenge_payload.clear();
        entry.frozen_local_proof_payload.clear();
        entry.snapshot.local_proof_message_id = 0U;
        entry.snapshot.local_claimant_principal.fill(0U);
        entry.snapshot.proof_send_attempts = 0U;
        entry.snapshot.last_proof_send_error_code = ErrorCode::ok;
        entry.snapshot.last_proof_send_error.clear();
        entry.local_recovery_override_used = false;
    }

    entry.frozen_peer_challenge_payload = frame.payload;
    entry.snapshot.peer_verifier_device = decoded.value().verifier_device;
    entry.snapshot.peer_authority_format = decoded.value().authority_format;
    entry.snapshot.peer_authority_epoch = decoded.value().ownership_epoch;
    entry.snapshot.peer_authority_sequence = decoded.value().authority_sequence;
    entry.snapshot.peer_authority_tail_digest = decoded.value().authority_tail_digest;
    entry.snapshot.peer_challenge_message_id = frame.message_id;
    entry.snapshot.peer_challenge_nonce = decoded.value().nonce;
    entry.snapshot.claimant_state = AuthorityClaimantState::challenge_received;
    entry.snapshot.claimant_detail = "peer challenge is ready for a local principal proof";
    entry.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

Result<AuthorityProofBody> PeerAuthorityRegistry::prepare_proof_body(
    std::uint32_t friend_number,
    const SigningPublicKey &claimant_principal,
    std::uint64_t now_unix_ms) {
    if (all_zero(claimant_principal)) {
        return Status{ErrorCode::invalid_argument,
                      "authority claimant principal is zero"};
    }
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || found->second.frozen_peer_challenge_payload.empty()) {
        return Status{ErrorCode::unavailable,
                      "no peer authority challenge is available"};
    }
    Entry &entry = found->second;
    if (!entry.frozen_local_proof_payload.empty()) {
        if (entry.snapshot.local_claimant_principal != claimant_principal) {
            return Status{ErrorCode::protocol_error,
                          "authority proof is already frozen for another principal"};
        }
        AuthorityProofBody existing{};
        std::copy_n(entry.frozen_local_proof_payload.begin(), existing.size(),
                    existing.begin());
        return existing;
    }

    AuthorityProof proof;
    proof.authority_format = entry.snapshot.peer_authority_format;
    proof.verifier_device = entry.snapshot.peer_verifier_device;
    proof.claimant_principal = claimant_principal;
    proof.ownership_epoch = entry.snapshot.peer_authority_epoch;
    proof.authority_sequence = entry.snapshot.peer_authority_sequence;
    proof.authority_tail_digest = entry.snapshot.peer_authority_tail_digest;
    proof.session_transcript_digest = entry.snapshot.session_transcript_digest;
    proof.challenge_nonce = entry.snapshot.peer_challenge_nonce;
    proof.challenge_message_id = entry.snapshot.peer_challenge_message_id;
    auto body = encode_authority_proof_body(proof);
    if (!body) {
        return body.status();
    }
    entry.snapshot.local_claimant_principal = claimant_principal;
    entry.snapshot.claimant_state = AuthorityClaimantState::proof_ready;
    entry.snapshot.claimant_detail = "canonical authority proof body prepared for local signing";
    entry.snapshot.updated_unix_ms = now_unix_ms;
    return body.value();
}

Result<AuthorityProofBody> PeerAuthorityRegistry::prepare_recovery_proof_body(
    std::uint32_t friend_number,
    const SigningPublicKey &expected_frozen_claimant,
    const SigningPublicKey &recovery_claimant,
    std::uint64_t now_unix_ms) {
    if (all_zero(expected_frozen_claimant) || all_zero(recovery_claimant) ||
        expected_frozen_claimant == recovery_claimant) {
        return Status{ErrorCode::invalid_argument,
                      "recovery proof replacement requires two distinct non-zero principals"};
    }
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() ||
        found->second.frozen_peer_challenge_payload.empty()) {
        return Status{ErrorCode::unavailable,
                      "no peer authority challenge is available"};
    }
    Entry &entry = found->second;
    if (entry.local_recovery_override_used) {
        return Status{ErrorCode::protocol_error,
                      "recovery proof replacement was already used for this online epoch"};
    }
    if (entry.frozen_local_proof_payload.empty() ||
        entry.snapshot.local_claimant_principal != expected_frozen_claimant ||
        entry.snapshot.claimant_state != AuthorityClaimantState::proof_sent) {
        return Status{ErrorCode::protocol_error,
                      "recovery proof may replace only the exact sent ordinary claimant"};
    }

    AuthorityProof proof;
    proof.authority_format = entry.snapshot.peer_authority_format;
    proof.verifier_device = entry.snapshot.peer_verifier_device;
    proof.claimant_principal = recovery_claimant;
    proof.ownership_epoch = entry.snapshot.peer_authority_epoch;
    proof.authority_sequence = entry.snapshot.peer_authority_sequence;
    proof.authority_tail_digest = entry.snapshot.peer_authority_tail_digest;
    proof.session_transcript_digest = entry.snapshot.session_transcript_digest;
    proof.challenge_nonce = entry.snapshot.peer_challenge_nonce;
    proof.challenge_message_id = entry.snapshot.peer_challenge_message_id;
    auto body = encode_authority_proof_body(proof);
    if (!body) {
        return body.status();
    }

    entry.frozen_local_proof_payload.clear();
    entry.snapshot.local_proof_message_id = 0U;
    entry.snapshot.local_claimant_principal = recovery_claimant;
    entry.snapshot.proof_send_attempts = 0U;
    entry.snapshot.last_proof_send_error_code = ErrorCode::ok;
    entry.snapshot.last_proof_send_error.clear();
    entry.snapshot.claimant_state = AuthorityClaimantState::proof_ready;
    entry.snapshot.claimant_detail =
        "explicit recovery claimant replaced the sent ordinary claimant";
    entry.snapshot.updated_unix_ms = now_unix_ms;
    entry.local_recovery_override_used = true;
    return body.value();
}

Result<protocol::Frame> PeerAuthorityRegistry::make_proof_frame(
    const protocol::PeerSessionSnapshot &session,
    std::span<const std::uint8_t, kAuthorityProofBytes> proof_bytes,
    std::uint64_t message_id,
    std::uint64_t now_unix_ms) {
    if (message_id == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "authority proof message identifier zero is reserved"};
    }
    auto decoded = decode_authority_proof(proof_bytes);
    if (!decoded) {
        return decoded.status();
    }
    if (!session_supports_authority_format(
            session, decoded.value().authority_format)) {
        return Status{ErrorCode::unsupported,
                      "authority proof uses a ledger format not negotiated by this session"};
    }
    const Status signature = verify_authority_proof(decoded.value(), *sodium_);
    if (!signature.ok()) {
        return Status{ErrorCode::protocol_error,
                      "authority proof signature is invalid"};
    }
    auto digest = authority_session_transcript_digest(session, *sodium_);
    if (!digest) {
        return digest.status();
    }

    std::scoped_lock lock(mutex_);
    auto found = entries_.find(session.friend_number);
    if (found == entries_.end() ||
        !same_session(found->second.snapshot, session, digest.value()) ||
        found->second.frozen_peer_challenge_payload.empty()) {
        return Status{ErrorCode::unavailable,
                      "authority proof has no matching online peer challenge"};
    }
    Entry &entry = found->second;
    const AuthorityChallenge challenge = challenge_from_snapshot(entry.snapshot);
    if (!challenge_matches_proof(
            challenge, entry.snapshot.peer_challenge_message_id,
            decoded.value())) {
        return Status{ErrorCode::protocol_error,
                      "authority proof does not answer the frozen peer challenge"};
    }
    if (!entry.frozen_local_proof_payload.empty()) {
        if (entry.snapshot.local_proof_message_id != message_id ||
            !std::equal(proof_bytes.begin(), proof_bytes.end(),
                        entry.frozen_local_proof_payload.begin(),
                        entry.frozen_local_proof_payload.end())) {
            return Status{ErrorCode::protocol_error,
                          "authority proof is already frozen for this online epoch"};
        }
    } else {
        if (!all_zero(entry.snapshot.local_claimant_principal) &&
            entry.snapshot.local_claimant_principal !=
                decoded.value().claimant_principal) {
            return Status{ErrorCode::protocol_error,
                          "signed authority proof principal differs from prepared body"};
        }
        entry.frozen_local_proof_payload.assign(
            proof_bytes.begin(), proof_bytes.end());
        entry.snapshot.local_claimant_principal =
            decoded.value().claimant_principal;
        entry.snapshot.local_proof_message_id = message_id;
        entry.snapshot.claimant_state = AuthorityClaimantState::proof_ready;
        entry.snapshot.claimant_detail = "signed authority proof reserved";
    }
    entry.snapshot.updated_unix_ms = now_unix_ms;

    protocol::Frame frame;
    frame.major = session.negotiated.selected.major;
    frame.minor = session.negotiated.selected.minor;
    frame.type = protocol::MessageType::authority_proof;
    frame.message_id = entry.snapshot.local_proof_message_id;
    frame.correlation_id = entry.snapshot.peer_challenge_message_id;
    frame.sequence = kAuthorityProofSequence;
    frame.payload = entry.frozen_local_proof_payload;
    return frame;
}

Result<protocol::Frame> PeerAuthorityRegistry::make_frozen_proof_frame(
    const protocol::PeerSessionSnapshot &session,
    std::uint64_t now_unix_ms) {
    auto digest = authority_session_transcript_digest(session, *sodium_);
    if (!digest) {
        return digest.status();
    }
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(session.friend_number);
    if (found == entries_.end() ||
        !same_session(found->second.snapshot, session, digest.value()) ||
        found->second.frozen_local_proof_payload.empty() ||
        found->second.snapshot.local_proof_message_id == 0U ||
        found->second.snapshot.peer_challenge_message_id == 0U) {
        return Status{ErrorCode::unavailable,
                      "no frozen authority proof is available for retry"};
    }
    found->second.snapshot.updated_unix_ms = now_unix_ms;
    protocol::Frame frame;
    frame.major = session.negotiated.selected.major;
    frame.minor = session.negotiated.selected.minor;
    frame.type = protocol::MessageType::authority_proof;
    frame.message_id = found->second.snapshot.local_proof_message_id;
    frame.correlation_id = found->second.snapshot.peer_challenge_message_id;
    frame.sequence = kAuthorityProofSequence;
    frame.payload = found->second.frozen_local_proof_payload;
    return frame;
}

Status PeerAuthorityRegistry::mark_proof_sent(
    std::uint32_t friend_number, std::uint64_t message_id,
    std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || found->second.frozen_local_proof_payload.empty() ||
        found->second.snapshot.local_proof_message_id != message_id) {
        return Status{ErrorCode::not_found,
                      "reserved authority proof was not found"};
    }
    ++found->second.snapshot.proof_send_attempts;
    found->second.snapshot.claimant_state = AuthorityClaimantState::proof_sent;
    found->second.snapshot.last_proof_send_error_code = ErrorCode::ok;
    found->second.snapshot.last_proof_send_error.clear();
    found->second.snapshot.claimant_detail = "authority proof accepted by transport";
    found->second.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

Status PeerAuthorityRegistry::mark_proof_send_failed(
    std::uint32_t friend_number, ErrorCode error_code,
    std::string error, std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    auto found = entries_.find(friend_number);
    if (found == entries_.end() || found->second.frozen_local_proof_payload.empty()) {
        return Status{ErrorCode::not_found,
                      "reserved authority proof was not found"};
    }
    ++found->second.snapshot.proof_send_attempts;
    found->second.snapshot.claimant_state =
        AuthorityClaimantState::proof_send_failed;
    found->second.snapshot.last_proof_send_error_code = error_code;
    found->second.snapshot.last_proof_send_error = std::move(error);
    found->second.snapshot.claimant_detail = "authority proof did not enter transport queue";
    found->second.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

Status PeerAuthorityRegistry::receive_proof(
    const protocol::PeerSessionSnapshot &session,
    const protocol::Frame &frame,
    const AuthorityLedger &local_authority,
    std::uint64_t now_unix_ms) {
    auto digest = authority_session_transcript_digest(session, *sodium_);
    if (!digest) {
        return digest.status();
    }

    // Snapshot the constitutional state before taking the per-session lock.
    // Authority mutations take the ledger lock before asking the registry to
    // invalidate sessions; taking those locks in the opposite order here
    // would create an avoidable lock-order cycle. The immutable snapshot also
    // gives every verification decision one coherent ledger view. The agent's
    // authority-mutation path invalidates all sessions after append; future
    // command admission must additionally compare the authorized ledger head
    // at the admission boundary rather than assuming this copy is a lock.
    const AuthoritySnapshot current = local_authority.snapshot();
    if (!session_supports_authority_format(session, current.format)) {
        return Status{ErrorCode::unsupported,
                      "peer did not negotiate the active authority ledger format"};
    }

    std::scoped_lock lock(mutex_);
    auto found = entries_.find(session.friend_number);
    if (found == entries_.end() ||
        !same_session(found->second.snapshot, session, digest.value())) {
        return Status{ErrorCode::unavailable,
                      "authority registry is not synchronized with this online session"};
    }
    Entry &entry = found->second;
    const Status frame_valid = validate_authority_proof_frame(
        session, entry.snapshot.local_challenge_message_id, frame);
    if (!frame_valid.ok()) {
        // A local ledger mutation resets the verifier and invalidates its
        // in-flight challenge. The peer may already have queued the signed
        // answer to that old challenge. It cannot authorize the new head, but
        // it also must not poison the fresh round before the Agent reserves
        // its replacement challenge. Leave challenge_ready intact; the old
        // proof remains unfrozen and the replacement challenge binds new
        // nonce, message id, exact ledger head, and the same transcript.
        if (frame_valid.code() == ErrorCode::unavailable &&
            entry.snapshot.local_challenge_message_id == 0U) {
            entry.snapshot.verifier_detail =
                "stale in-flight authority proof ignored while a fresh local challenge is pending";
            entry.snapshot.updated_unix_ms = now_unix_ms;
            return frame_valid;
        }
        entry.snapshot.verifier_state = AuthorityVerifierState::malformed_proof;
        entry.snapshot.verifier_detail = frame_valid.message();
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return frame_valid;
    }

    bool replacement_requires_owner = false;
    if (!entry.frozen_peer_proof_payload.empty()) {
        // The signed proof body binds the exact challenge, ledger head, and
        // transcript. A byte-identical body is therefore idempotent even if a
        // peer wrapped it in a fresh outer frame identifier after losing local
        // enqueue state. Preserve the first observed identifier for evidence.
        if (entry.frozen_peer_proof_payload == frame.payload) {
            return entry.snapshot.remote_authorized
                ? Status::success()
                : Status{ErrorCode::unsupported,
                         "peer principal is not authorized by the current ledger"};
        }
        // A fresh controller first presents its ordinary stable device key.
        // If and only if that valid claimant was denied, accept one distinct
        // recovery candidate against the same immutable challenge. An
        // authorized first proof stays frozen, and a second denial exhausts
        // the epoch, so this cannot become an unbounded proof oracle.
        const bool denied_recovery =
            entry.snapshot.verifier_state == AuthorityVerifierState::denied;
        const bool delegated_admin_upgrade =
            entry.snapshot.verifier_state == AuthorityVerifierState::authorized &&
            entry.snapshot.remote_role != PrincipalRole::owner;
        if ((denied_recovery || delegated_admin_upgrade) &&
            entry.snapshot.peer_proof_candidate_count == 1U) {
            replacement_requires_owner = delegated_admin_upgrade;
            entry.frozen_peer_proof_payload.clear();
            clear_remote_authorization(entry.snapshot);
        } else {
            entry.snapshot.verifier_state =
                AuthorityVerifierState::conflicting_proof;
            entry.snapshot.verifier_detail =
                "peer changed its authority proof within one online epoch";
            clear_remote_authorization(entry.snapshot);
            entry.snapshot.updated_unix_ms = now_unix_ms;
            return Status{ErrorCode::protocol_error,
                          "conflicting authority proof for one online epoch"};
        }
    }

    auto decoded = decode_authority_proof(frame.payload);
    if (!decoded) {
        entry.snapshot.verifier_state = AuthorityVerifierState::malformed_proof;
        entry.snapshot.verifier_detail = decoded.status().message();
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return decoded.status();
    }
    const Status signature = verify_authority_proof(decoded.value(), *sodium_);
    if (!signature.ok()) {
        entry.snapshot.verifier_state = AuthorityVerifierState::malformed_proof;
        entry.snapshot.verifier_detail = "authority proof signature is invalid";
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return Status{ErrorCode::protocol_error,
                      "authority proof signature is invalid"};
    }

    AuthorityChallenge expected;
    expected.authority_format = entry.snapshot.local_authority_format;
    expected.verifier_device = current.device;
    expected.ownership_epoch = entry.snapshot.local_authority_epoch;
    expected.authority_sequence = entry.snapshot.local_authority_sequence;
    expected.authority_tail_digest = entry.snapshot.local_authority_tail_digest;
    expected.session_transcript_digest = entry.snapshot.session_transcript_digest;
    expected.nonce = entry.snapshot.local_challenge_nonce;
    if (!challenge_matches_proof(
            expected, entry.snapshot.local_challenge_message_id,
            decoded.value())) {
        entry.snapshot.verifier_state = AuthorityVerifierState::malformed_proof;
        entry.snapshot.verifier_detail = "authority proof does not answer the frozen local challenge";
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return Status{ErrorCode::protocol_error,
                      "authority proof does not answer the frozen local challenge"};
    }

    if (!ledger_matches_challenge(current, expected)) {
        entry.snapshot.verifier_state = AuthorityVerifierState::stale_ledger;
        entry.snapshot.verifier_detail = "local authority head changed after the challenge";
        clear_remote_authorization(entry.snapshot);
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return Status{ErrorCode::unavailable,
                      "authority proof targets a stale local ledger head"};
    }

    entry.frozen_peer_proof_payload = frame.payload;
    ++entry.snapshot.peer_proof_candidate_count;
    entry.snapshot.peer_proof_message_id = frame.message_id;
    entry.snapshot.remote_principal = decoded.value().claimant_principal;
    const auto principal = std::find_if(
        current.principals.begin(), current.principals.end(),
        [&](const PrincipalState &candidate) {
            return constant_time_equal(
                candidate.public_key, decoded.value().claimant_principal);
        });
    if (principal == current.principals.end() || !principal->active) {
        entry.snapshot.verifier_state = AuthorityVerifierState::denied;
        entry.snapshot.remote_authorized = false;
        entry.snapshot.remote_role = PrincipalRole::none;
        entry.snapshot.remote_capabilities = 0U;
        entry.snapshot.verifier_detail = "valid proof principal is unknown or revoked";
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return Status{ErrorCode::not_found,
                      "valid authority proof principal is unknown or revoked"};
    }
    if (replacement_requires_owner &&
        principal->role != PrincipalRole::owner) {
        entry.snapshot.verifier_state =
            AuthorityVerifierState::conflicting_proof;
        entry.snapshot.verifier_detail =
            "an authorized delegated claimant may be replaced only by an owner";
        clear_remote_authorization(entry.snapshot);
        entry.snapshot.updated_unix_ms = now_unix_ms;
        return Status{ErrorCode::protocol_error,
                      "authority proof replacement is not an owner"};
    }

    entry.snapshot.verifier_state = AuthorityVerifierState::authorized;
    entry.snapshot.remote_authorized = true;
    entry.snapshot.remote_role = principal->role;
    entry.snapshot.remote_capabilities = principal->capabilities;
    entry.snapshot.verifier_detail = "remote principal is active in the exact challenged ledger head";
    entry.snapshot.updated_unix_ms = now_unix_ms;
    return Status::success();
}

void PeerAuthorityRegistry::invalidate_local_authority(
    const AuthoritySnapshot &local_authority,
    std::uint64_t now_unix_ms) {
    std::scoped_lock lock(mutex_);
    for (auto &[friend_number, entry] : entries_) {
        static_cast<void>(friend_number);
        if (!entry.snapshot.connected || !entry.snapshot.feature_negotiated) {
            continue;
        }
        reset_verifier(entry, local_authority, now_unix_ms);
    }
}

Result<PeerAuthoritySnapshot> PeerAuthorityRegistry::get(
    std::uint32_t friend_number) const {
    std::scoped_lock lock(mutex_);
    const auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return Status{ErrorCode::not_found,
                      "authority session does not exist for friend"};
    }
    return found->second.snapshot;
}

std::vector<PeerAuthoritySnapshot> PeerAuthorityRegistry::list() const {
    std::scoped_lock lock(mutex_);
    std::vector<PeerAuthoritySnapshot> output;
    output.reserve(entries_.size());
    for (const auto &[friend_number, entry] : entries_) {
        static_cast<void>(friend_number);
        output.push_back(entry.snapshot);
    }
    std::sort(output.begin(), output.end(),
              [](const PeerAuthoritySnapshot &left,
                 const PeerAuthoritySnapshot &right) {
                  return left.friend_number < right.friend_number;
              });
    return output;
}

bool PeerAuthorityRegistry::authorized(
    std::uint32_t friend_number,
    std::uint64_t required_capabilities) const {
    if ((required_capabilities & ~kAuthorityV3Capabilities) != 0U) {
        return false;
    }
    std::scoped_lock lock(mutex_);
    const auto found = entries_.find(friend_number);
    return found != entries_.end() &&
           found->second.snapshot.remote_authorized &&
           (found->second.snapshot.remote_capabilities & required_capabilities) ==
               required_capabilities;
}

bool PeerAuthorityRegistry::authorized_at(
    std::uint32_t friend_number,
    std::uint64_t required_capabilities,
    const AuthoritySnapshot &current_local_authority) const {
    if (!current_local_authority.initialized ||
        (required_capabilities &
         ~authority_capability_mask(current_local_authority.format)) != 0U) {
        return false;
    }
    std::scoped_lock lock(mutex_);
    const auto found = entries_.find(friend_number);
    if (found == entries_.end()) {
        return false;
    }
    const PeerAuthoritySnapshot &authority = found->second.snapshot;
    return authority.connected && authority.feature_negotiated &&
           authority.verifier_state == AuthorityVerifierState::authorized &&
           authority.remote_authorized &&
           authority.local_authority_format == current_local_authority.format &&
           authority.local_authority_epoch ==
               current_local_authority.ownership_epoch &&
           authority.local_authority_sequence ==
               current_local_authority.sequence &&
           constant_time_equal(authority.local_authority_tail_digest,
                               current_local_authority.tail_digest) &&
           (authority.remote_capabilities & required_capabilities) ==
               required_capabilities;
}

}  // namespace iotox::security
