#pragma once

#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <span>
#include <string>
#include <unordered_map>
#include <vector>

namespace iotox::security {

// AUTHORITY_CHALLENGE and AUTHORITY_PROOF are the first authority records
// after the transcript-confirmed Tox session. They bind a stable ledger
// principal to that exact online epoch. Tox authenticates the transport peer;
// this exchange authenticates the IoTox principal that may request operations.
inline constexpr std::uint8_t kAuthorityChallengeFormatV1 = 1U;
inline constexpr std::uint8_t kAuthorityChallengeFormatV2 = 2U;
inline constexpr std::uint8_t kAuthorityChallengeFormatV3 = 3U;
inline constexpr std::uint8_t kAuthorityChallengeFormat =
    kAuthorityChallengeFormatV1;
inline constexpr std::size_t kAuthorityChallengeBytes = 160U;
inline constexpr std::uint8_t kAuthorityProofFormatV1 = 1U;
inline constexpr std::uint8_t kAuthorityProofFormatV2 = 2U;
inline constexpr std::uint8_t kAuthorityProofFormatV3 = 3U;
inline constexpr std::uint8_t kAuthorityProofFormat = kAuthorityProofFormatV1;
inline constexpr std::size_t kAuthorityProofBodyBytes = 192U;
inline constexpr std::size_t kAuthorityProofBytes =
    kAuthorityProofBodyBytes + kSignatureBytes;
inline constexpr std::uint64_t kAuthorityChallengeSequence = 3U;
inline constexpr std::uint64_t kAuthorityProofSequence = 4U;

using AuthorityNonce = std::array<std::uint8_t, 32U>;
using AuthorityChallengeBytes =
    std::array<std::uint8_t, kAuthorityChallengeBytes>;
using AuthorityProofBody =
    std::array<std::uint8_t, kAuthorityProofBodyBytes>;
using AuthorityProofBytes =
    std::array<std::uint8_t, kAuthorityProofBytes>;

struct AuthorityChallenge {
    AuthorityLedgerFormat authority_format{AuthorityLedgerFormat::v1};
    SigningPublicKey verifier_device{};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t authority_sequence{0U};
    Digest authority_tail_digest{};
    Digest session_transcript_digest{};
    AuthorityNonce nonce{};

    [[nodiscard]] bool operator==(const AuthorityChallenge &) const = default;
};

struct AuthorityProof {
    AuthorityLedgerFormat authority_format{AuthorityLedgerFormat::v1};
    SigningPublicKey verifier_device{};
    SigningPublicKey claimant_principal{};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t authority_sequence{0U};
    Digest authority_tail_digest{};
    Digest session_transcript_digest{};
    AuthorityNonce challenge_nonce{};
    std::uint64_t challenge_message_id{0U};
    Signature signature{};

    [[nodiscard]] bool operator==(const AuthorityProof &) const = default;
};

enum class AuthorityVerifierState : std::uint8_t {
    inactive = 0U,
    challenge_ready = 1U,
    challenge_send_failed = 2U,
    awaiting_proof = 3U,
    authorized = 4U,
    denied = 5U,
    malformed_proof = 6U,
    conflicting_proof = 7U,
    stale_ledger = 8U,
};

enum class AuthorityClaimantState : std::uint8_t {
    inactive = 0U,
    awaiting_challenge = 1U,
    challenge_received = 2U,
    malformed_challenge = 3U,
    conflicting_challenge = 4U,
    proof_ready = 5U,
    proof_send_failed = 6U,
    proof_sent = 7U,
};

struct PeerAuthoritySnapshot {
    std::uint32_t friend_number{0U};
    std::string transport_public_key;
    std::uint64_t online_epoch{0U};
    bool connected{false};
    bool feature_negotiated{false};
    bool authority_v2_negotiated{false};
    bool authority_v3_negotiated{false};
    Digest session_transcript_digest{};

    AuthorityLedgerFormat local_authority_format{AuthorityLedgerFormat::v1};
    std::uint64_t local_authority_epoch{0U};
    std::uint64_t local_authority_sequence{0U};
    Digest local_authority_tail_digest{};
    AuthorityVerifierState verifier_state{AuthorityVerifierState::inactive};
    bool remote_authorized{false};
    SigningPublicKey remote_principal{};
    PrincipalRole remote_role{PrincipalRole::none};
    std::uint64_t remote_capabilities{0U};
    std::uint64_t local_challenge_message_id{0U};
    AuthorityNonce local_challenge_nonce{};
    std::uint32_t challenge_send_attempts{0U};
    ErrorCode last_challenge_send_error_code{ErrorCode::ok};
    std::string last_challenge_send_error;
    std::uint64_t peer_proof_message_id{0U};
    std::string verifier_detail{"inactive"};

    AuthorityClaimantState claimant_state{AuthorityClaimantState::inactive};
    SigningPublicKey peer_verifier_device{};
    AuthorityLedgerFormat peer_authority_format{AuthorityLedgerFormat::v1};
    std::uint64_t peer_authority_epoch{0U};
    std::uint64_t peer_authority_sequence{0U};
    Digest peer_authority_tail_digest{};
    std::uint64_t peer_challenge_message_id{0U};
    AuthorityNonce peer_challenge_nonce{};
    std::uint64_t local_proof_message_id{0U};
    SigningPublicKey local_claimant_principal{};
    std::uint8_t peer_proof_candidate_count{0U};
    std::uint32_t proof_send_attempts{0U};
    ErrorCode last_proof_send_error_code{ErrorCode::ok};
    std::string last_proof_send_error;
    std::string claimant_detail{"inactive"};
    std::uint64_t updated_unix_ms{0U};

    [[nodiscard]] bool operator==(const PeerAuthoritySnapshot &) const = default;
};

[[nodiscard]] Result<Digest> authority_session_transcript_digest(
    const protocol::PeerSessionSnapshot &session, const Sodium &sodium);
[[nodiscard]] Result<AuthorityChallengeBytes> encode_authority_challenge(
    const AuthorityChallenge &challenge);
[[nodiscard]] Result<AuthorityChallenge> decode_authority_challenge(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<AuthorityProofBody> encode_authority_proof_body(
    const AuthorityProof &proof);
[[nodiscard]] Result<AuthorityProof> decode_authority_proof(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<AuthorityProofBytes> sign_authority_proof_body(
    std::span<const std::uint8_t, kAuthorityProofBodyBytes> body,
    std::span<const std::uint8_t, kSigningSecretKeyBytes> secret_key,
    const Sodium &sodium);
[[nodiscard]] Result<AuthorityProofBytes> sign_authority_proof_body(
    std::span<const std::uint8_t, kAuthorityProofBodyBytes> body,
    const DeviceIdentity &identity);
[[nodiscard]] Status verify_authority_proof(
    const AuthorityProof &proof, const Sodium &sodium);

[[nodiscard]] Status validate_authority_challenge_frame(
    const protocol::PeerSessionSnapshot &session,
    const protocol::Frame &frame);
[[nodiscard]] Status validate_authority_proof_frame(
    const protocol::PeerSessionSnapshot &session,
    std::uint64_t expected_challenge_message_id,
    const protocol::Frame &frame);

[[nodiscard]] std::string to_string(AuthorityVerifierState state);
[[nodiscard]] std::string to_string(AuthorityClaimantState state);
[[nodiscard]] std::string render_peer_authority(
    const PeerAuthoritySnapshot &snapshot);

// Directional authority state is deliberately independent. Each endpoint may
// challenge the other, and either side may remain unauthenticated while the
// opposite direction is authorized. The registry freezes the first valid
// challenge/proof bytes per online epoch. Transient transport failures retry
// one exact reserved frame; accepted frames are never resent by this layer.
class PeerAuthorityRegistry {
  public:
    explicit PeerAuthorityRegistry(const Sodium &sodium) : sodium_(&sodium) {}

    [[nodiscard]] Status synchronize_session(
        const protocol::PeerSessionSnapshot &session,
        const AuthoritySnapshot &local_authority,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status peer_offline(
        std::uint32_t friend_number, std::uint64_t now_unix_ms);
    void erase(std::uint32_t friend_number);

    [[nodiscard]] Result<protocol::Frame> make_challenge_frame(
        const protocol::PeerSessionSnapshot &session,
        const AuthoritySnapshot &local_authority,
        const AuthorityNonce &nonce,
        std::uint64_t message_id,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_challenge_sent(
        std::uint32_t friend_number, std::uint64_t message_id,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_challenge_send_failed(
        std::uint32_t friend_number, ErrorCode error_code,
        std::string error, std::uint64_t now_unix_ms);

    [[nodiscard]] Status receive_challenge(
        const protocol::PeerSessionSnapshot &session,
        const protocol::Frame &frame,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Result<AuthorityProofBody> prepare_proof_body(
        std::uint32_t friend_number,
        const SigningPublicKey &claimant_principal,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Result<AuthorityProofBody> prepare_recovery_proof_body(
        std::uint32_t friend_number,
        const SigningPublicKey &expected_frozen_claimant,
        const SigningPublicKey &recovery_claimant,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Result<protocol::Frame> make_proof_frame(
        const protocol::PeerSessionSnapshot &session,
        std::span<const std::uint8_t, kAuthorityProofBytes> proof,
        std::uint64_t message_id,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Result<protocol::Frame> make_frozen_proof_frame(
        const protocol::PeerSessionSnapshot &session,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_proof_sent(
        std::uint32_t friend_number, std::uint64_t message_id,
        std::uint64_t now_unix_ms);
    [[nodiscard]] Status mark_proof_send_failed(
        std::uint32_t friend_number, ErrorCode error_code,
        std::string error, std::uint64_t now_unix_ms);

    [[nodiscard]] Status receive_proof(
        const protocol::PeerSessionSnapshot &session,
        const protocol::Frame &frame,
        const AuthorityLedger &local_authority,
        std::uint64_t now_unix_ms);

    // A local ledger mutation invalidates every remote authorization. New
    // challenges are generated against the new exact head by make_challenge_frame.
    void invalidate_local_authority(
        const AuthoritySnapshot &local_authority,
        std::uint64_t now_unix_ms);

    [[nodiscard]] Result<PeerAuthoritySnapshot> get(
        std::uint32_t friend_number) const;
    [[nodiscard]] std::vector<PeerAuthoritySnapshot> list() const;
    [[nodiscard]] bool authorized(
        std::uint32_t friend_number,
        std::uint64_t required_capabilities) const;
    // Command admission must be bound to the exact local authority head that
    // was challenged and proven. The simpler overload is useful for
    // inspection, but effect admission should use this exact-head form so a
    // concurrent ledger mutation cannot silently reuse stale authority state.
    [[nodiscard]] bool authorized_at(
        std::uint32_t friend_number,
        std::uint64_t required_capabilities,
        const AuthoritySnapshot &current_local_authority) const;

  private:
    struct Entry {
        PeerAuthoritySnapshot snapshot;
        std::vector<std::uint8_t> frozen_peer_challenge_payload;
        std::vector<std::uint8_t> frozen_peer_proof_payload;
        std::vector<std::uint8_t> frozen_local_challenge_payload;
        std::vector<std::uint8_t> frozen_local_proof_payload;
        bool local_recovery_override_used{false};
    };

    [[nodiscard]] static bool same_session(
        const PeerAuthoritySnapshot &authority,
        const protocol::PeerSessionSnapshot &session,
        const Digest &transcript_digest) noexcept;
    [[nodiscard]] static bool ledger_matches_challenge(
        const AuthoritySnapshot &ledger,
        const AuthorityChallenge &challenge) noexcept;
    [[nodiscard]] static Status validate_initialized_authority(
        const AuthoritySnapshot &authority);

    const Sodium *sodium_{nullptr};
    mutable std::mutex mutex_;
    std::unordered_map<std::uint32_t, Entry> entries_;
};

}  // namespace iotox::security
