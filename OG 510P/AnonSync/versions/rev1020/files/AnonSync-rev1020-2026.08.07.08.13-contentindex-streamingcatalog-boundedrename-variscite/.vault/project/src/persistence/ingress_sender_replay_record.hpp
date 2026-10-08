#pragma once

#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync::persistence {

inline constexpr std::string_view kIngressSenderReplayRecordFormat =
    "anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction";
inline constexpr std::uint64_t kIngressSenderReplayMaximumTokenBytes = 512;
inline constexpr std::uint64_t kIngressSenderReplayMaximumPrincipalBytes = 4096;
inline constexpr std::uint64_t kIngressSenderReplayMinimumNonceBytes = 16;
inline constexpr std::uint64_t kIngressSenderReplayMaximumNonceBytes = 128;
inline constexpr std::int64_t kIngressSenderReplayMaximumWindowSeconds = 86400;
inline constexpr std::int64_t kIngressSenderReplayFutureSkewSeconds = 300;

// Evidence supplied by the authenticated ingress boundary.  This is not yet a
// durable replay reservation: it acquires that authority only after the owning
// ledger binds it to an exact prepared entry and verifies the complete record.
struct IngressSenderReplayEvidence final {
    std::string replay_key_sha256;
    std::string format;
    std::string service_config_sha256;
    std::string ingress_profile_sha256;
    std::string sender_replay_cache_instance_id;
    std::string sender_proof_kid;
    std::string principal;
    std::string nonce;
    std::int64_t issued_at_epoch = 0;
    std::int64_t observed_at_epoch = 0;
    std::int64_t replay_window_seconds = 0;
    std::string material_sha256;
};

struct PreparedEffectEvidence final {
    std::int64_t sequence = 0;
    std::string entry_hash;
    std::string effect_idempotency_key;
};

struct IngressSenderReplayRecord final {
    IngressSenderReplayEvidence replay;
    PreparedEffectEvidence prepared;
};

enum class IngressSenderReplayFailure : std::uint8_t {
    none,
    unsupported_format,
    malformed_replay_key_digest,
    malformed_service_config_digest,
    malformed_ingress_profile_digest,
    malformed_material_digest,
    malformed_cache_instance_id,
    malformed_sender_proof_kid,
    empty_principal,
    principal_too_large,
    principal_contains_control,
    malformed_nonce,
    invalid_replay_window,
    invalid_issued_at,
    invalid_observed_at,
    issued_before_window,
    issued_after_future_skew,
    invalid_prepared_sequence,
    malformed_prepared_entry_hash,
    malformed_effect_idempotency_key,
    prepared_binding_mismatch,
};

struct IngressSenderReplayValidation final {
    IngressSenderReplayFailure failure = IngressSenderReplayFailure::none;
    std::string_view field;

    [[nodiscard]] bool has_value() const noexcept {
        return failure == IngressSenderReplayFailure::none;
    }
    explicit operator bool() const noexcept { return has_value(); }
    [[nodiscard]] std::string safe_summary() const;
};

[[nodiscard]] std::string_view ingress_sender_replay_failure_name(
    IngressSenderReplayFailure failure) noexcept;

[[nodiscard]] IngressSenderReplayValidation
validate_ingress_sender_replay_evidence(
    const IngressSenderReplayEvidence& evidence) noexcept;

// Verifies both the row's self-contained field invariants and its exact binding
// to a prepared ledger entry that was independently reconstructed from the
// decision hash chain.
[[nodiscard]] IngressSenderReplayValidation verify_ingress_sender_replay_record(
    const IngressSenderReplayRecord& record,
    const PreparedEffectEvidence& expected_prepared) noexcept;

// Stable, length-delimited identity used for both staged and durable duplicate
// detection.  It intentionally excludes principal and material: the protocol's
// uniqueness scope is service/profile/cache-instance/key/nonce.
[[nodiscard]] std::string ingress_sender_replay_nonce_identity_key(
    const IngressSenderReplayEvidence& evidence);

}  // namespace anonsync::persistence
