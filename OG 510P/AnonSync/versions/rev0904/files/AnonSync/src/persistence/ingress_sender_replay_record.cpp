#include "ingress_sender_replay_record.hpp"

#include <string>

namespace anonsync::persistence {
namespace {

[[nodiscard]] bool is_lower_hex_sha256(std::string_view value) noexcept {
    if (value.size() != 64) return false;
    for (const char c : value) {
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

[[nodiscard]] bool is_printable_token(std::string_view value) noexcept {
    if (value.empty() || value.size() > kIngressSenderReplayMaximumTokenBytes) {
        return false;
    }
    for (const char raw : value) {
        const auto c = static_cast<unsigned char>(raw);
        const bool accepted =
            (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' ||
            c == '~' || c == ':' || c == '@' || c == '/';
        if (!accepted) return false;
    }
    return true;
}

[[nodiscard]] bool contains_security_control(std::string_view value) noexcept {
    for (const char raw : value) {
        const auto c = static_cast<unsigned char>(raw);
        if (c < 0x20 || c == 0x7f) return true;
    }
    return false;
}

[[nodiscard]] bool is_nonce(std::string_view value) noexcept {
    if (value.size() < kIngressSenderReplayMinimumNonceBytes ||
        value.size() > kIngressSenderReplayMaximumNonceBytes) {
        return false;
    }
    for (const char raw : value) {
        const auto c = static_cast<unsigned char>(raw);
        const bool accepted =
            (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' ||
            c == '~';
        if (!accepted) return false;
    }
    return true;
}

[[nodiscard]] IngressSenderReplayValidation failure(
    IngressSenderReplayFailure kind,
    std::string_view field) noexcept {
    return IngressSenderReplayValidation{kind, field};
}

void append_length_prefixed(std::string& output, std::string_view value) {
    output += std::to_string(value.size());
    output.push_back(':');
    output.append(value.data(), value.size());
}

}  // namespace

std::string_view ingress_sender_replay_failure_name(
    IngressSenderReplayFailure failure_value) noexcept {
    using Failure = IngressSenderReplayFailure;
    switch (failure_value) {
        case Failure::none: return "none";
        case Failure::unsupported_format: return "unsupported_format";
        case Failure::malformed_replay_key_digest: return "malformed_replay_key_digest";
        case Failure::malformed_service_config_digest: return "malformed_service_config_digest";
        case Failure::malformed_ingress_profile_digest: return "malformed_ingress_profile_digest";
        case Failure::malformed_material_digest: return "malformed_material_digest";
        case Failure::malformed_cache_instance_id: return "malformed_cache_instance_id";
        case Failure::malformed_sender_proof_kid: return "malformed_sender_proof_kid";
        case Failure::empty_principal: return "empty_principal";
        case Failure::principal_too_large: return "principal_too_large";
        case Failure::principal_contains_control: return "principal_contains_control";
        case Failure::malformed_nonce: return "malformed_nonce";
        case Failure::invalid_replay_window: return "invalid_replay_window";
        case Failure::invalid_issued_at: return "invalid_issued_at";
        case Failure::invalid_observed_at: return "invalid_observed_at";
        case Failure::issued_before_window: return "issued_before_window";
        case Failure::issued_after_future_skew: return "issued_after_future_skew";
        case Failure::invalid_prepared_sequence: return "invalid_prepared_sequence";
        case Failure::malformed_prepared_entry_hash: return "malformed_prepared_entry_hash";
        case Failure::malformed_effect_idempotency_key: return "malformed_effect_idempotency_key";
        case Failure::prepared_binding_mismatch: return "prepared_binding_mismatch";
    }
    return "unknown";
}

std::string IngressSenderReplayValidation::safe_summary() const {
    std::string output = "ingress_sender_replay[";
    output.append(field.data(), field.size());
    output.push_back(':');
    const std::string_view name = ingress_sender_replay_failure_name(failure);
    output.append(name.data(), name.size());
    output.push_back(']');
    return output;
}

IngressSenderReplayValidation validate_ingress_sender_replay_evidence(
    const IngressSenderReplayEvidence& evidence) noexcept {
    using Failure = IngressSenderReplayFailure;
    if (evidence.format != kIngressSenderReplayRecordFormat) {
        return failure(Failure::unsupported_format, "format");
    }
    if (!is_lower_hex_sha256(evidence.replay_key_sha256)) {
        return failure(Failure::malformed_replay_key_digest, "replay_key_sha256");
    }
    if (!is_lower_hex_sha256(evidence.service_config_sha256)) {
        return failure(Failure::malformed_service_config_digest,
                       "service_config_sha256");
    }
    if (!is_lower_hex_sha256(evidence.ingress_profile_sha256)) {
        return failure(Failure::malformed_ingress_profile_digest,
                       "ingress_profile_sha256");
    }
    if (!is_lower_hex_sha256(evidence.material_sha256)) {
        return failure(Failure::malformed_material_digest, "material_sha256");
    }
    if (!is_printable_token(evidence.sender_replay_cache_instance_id)) {
        return failure(Failure::malformed_cache_instance_id,
                       "sender_replay_cache_instance_id");
    }
    if (!is_printable_token(evidence.sender_proof_kid)) {
        return failure(Failure::malformed_sender_proof_kid, "sender_proof_kid");
    }
    if (evidence.principal.empty()) {
        return failure(Failure::empty_principal, "principal");
    }
    if (evidence.principal.size() > kIngressSenderReplayMaximumPrincipalBytes) {
        return failure(Failure::principal_too_large, "principal");
    }
    if (contains_security_control(evidence.principal)) {
        return failure(Failure::principal_contains_control, "principal");
    }
    if (!is_nonce(evidence.nonce)) {
        return failure(Failure::malformed_nonce, "nonce");
    }
    if (evidence.replay_window_seconds < 1 ||
        evidence.replay_window_seconds > kIngressSenderReplayMaximumWindowSeconds) {
        return failure(Failure::invalid_replay_window, "replay_window_seconds");
    }
    if (evidence.issued_at_epoch <= 0) {
        return failure(Failure::invalid_issued_at, "issued_at_epoch");
    }
    if (evidence.observed_at_epoch <= 0) {
        return failure(Failure::invalid_observed_at, "observed_at_epoch");
    }
    // Difference-based checks avoid signed overflow for hostile INTEGER values.
    if (evidence.issued_at_epoch <= evidence.observed_at_epoch &&
        evidence.observed_at_epoch - evidence.issued_at_epoch >
            evidence.replay_window_seconds) {
        return failure(Failure::issued_before_window, "issued_at_epoch");
    }
    if (evidence.issued_at_epoch > evidence.observed_at_epoch &&
        evidence.issued_at_epoch - evidence.observed_at_epoch >
            kIngressSenderReplayFutureSkewSeconds) {
        return failure(Failure::issued_after_future_skew, "issued_at_epoch");
    }
    return {};
}

IngressSenderReplayValidation verify_ingress_sender_replay_record(
    const IngressSenderReplayRecord& record,
    const PreparedEffectEvidence& expected_prepared) noexcept {
    using Failure = IngressSenderReplayFailure;
    const IngressSenderReplayValidation evidence_validation =
        validate_ingress_sender_replay_evidence(record.replay);
    if (!evidence_validation) return evidence_validation;
    if (record.prepared.sequence <= 0) {
        return failure(Failure::invalid_prepared_sequence, "prepared_sequence");
    }
    if (!is_lower_hex_sha256(record.prepared.entry_hash)) {
        return failure(Failure::malformed_prepared_entry_hash,
                       "prepared_entry_hash");
    }
    if (!is_lower_hex_sha256(record.prepared.effect_idempotency_key)) {
        return failure(Failure::malformed_effect_idempotency_key,
                       "effect_idempotency_key");
    }
    if (record.prepared.sequence != expected_prepared.sequence ||
        record.prepared.entry_hash != expected_prepared.entry_hash ||
        record.prepared.effect_idempotency_key !=
            expected_prepared.effect_idempotency_key) {
        return failure(Failure::prepared_binding_mismatch, "prepared_evidence");
    }
    return {};
}

std::string ingress_sender_replay_nonce_identity_key(
    const IngressSenderReplayEvidence& evidence) {
    std::string output = "anonsync-ingress-sender-replay-nonce-unique-v1";
    append_length_prefixed(output, evidence.service_config_sha256);
    append_length_prefixed(output, evidence.ingress_profile_sha256);
    append_length_prefixed(output, evidence.sender_replay_cache_instance_id);
    append_length_prefixed(output, evidence.sender_proof_kid);
    append_length_prefixed(output, evidence.nonce);
    return output;
}

}  // namespace anonsync::persistence
