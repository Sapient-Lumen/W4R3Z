#include "effect_transition_intent_publication.hpp"
#include "frozen_publication_primitives.hpp"
#include "sha256_digest.hpp"

#include <stdexcept>
#include <utility>

namespace anonsync::persistence {
namespace {

using publication_detail::BoundedMachineText;
using publication_detail::append_component;
using publication_detail::append_json_member_prefix;
using publication_detail::append_json_string;
using publication_detail::append_line;
using publication_detail::append_named_component;
using publication_detail::decimal_text;
using publication_detail::is_base64url_without_padding;
using publication_detail::is_canonical_utc;
using publication_detail::is_lower_hex_sha256;
using publication_detail::is_sha256_or_genesis;
using publication_detail::require_nonempty_bounded_control_free;

void validate_common_fields_or_throw(
    const EffectTransitionIntentPayloadFields& fields,
    std::string_view version_label) {
    const std::string prefix = "effect transition " +
                               std::string(version_label) + " ";
    if (fields.intent_subject != kEffectTransitionIntentSubject) {
        throw std::runtime_error(prefix + "subject mismatch");
    }
    if (!is_canonical_utc(fields.issued_at)) {
        throw std::runtime_error(prefix +
                                 "issued_at is not canonical UTC");
    }
    if (fields.ledger_backend != kEffectTransitionIntentLedgerBackend) {
        throw std::runtime_error(prefix + "ledger backend mismatch");
    }
    if (!is_lower_hex_sha256(fields.ledger_instance_id)) {
        throw std::runtime_error(prefix + "ledger_instance_id is invalid");
    }
    if (!is_sha256_or_genesis(fields.prepared_ledger_head_hash)) {
        throw std::runtime_error(prefix +
                                 "prepared ledger head is invalid");
    }
    if (!is_sha256_or_genesis(fields.effect_transition_previous_hash)) {
        throw std::runtime_error(prefix +
                                 "previous transition head is invalid");
    }
    if (!is_lower_hex_sha256(fields.effect_idempotency_key)) {
        throw std::runtime_error(prefix + "effect key is invalid");
    }
    if (fields.prepared_sequence <= 0 ||
        fields.prepared_sequence > kEffectTransitionIntentMaximumExactJsonInteger) {
        throw std::runtime_error(
            prefix + "prepared_sequence is outside exact JSON range");
    }
    if (!is_lower_hex_sha256(fields.prepared_entry_hash)) {
        throw std::runtime_error(prefix + "prepared entry hash is invalid");
    }
    if (fields.terminal_state != "applied" && fields.terminal_state != "failed" &&
        fields.terminal_state != "compensated") {
        throw std::runtime_error(prefix + "terminal_state is invalid");
    }
    if (!is_lower_hex_sha256(fields.result_digest_sha256)) {
        throw std::runtime_error(prefix + "result digest is invalid");
    }
    require_nonempty_bounded_control_free(fields.transition_reason,
                                          kEffectTransitionIntentMaximumReasonBytes,
                                          prefix + "reason");
}

void validate_v2_fields_or_throw(
    const EffectTransitionIntentPayloadFields& fields) {
    require_nonempty_bounded_control_free(
        fields.intent_id,
        kEffectTransitionIntentMaximumLegacyIntentIdBytes,
        "effect transition v2 intent_id");
    validate_common_fields_or_throw(fields, "v2");
}

void validate_v3_fields_or_throw(
    const EffectTransitionIntentPayloadFields& fields) {
    if (!is_lower_hex_sha256(fields.intent_id)) {
        throw std::runtime_error(
            "effect transition v3 intent_id is not lowercase sha256 hex");
    }
    validate_common_fields_or_throw(fields, "v3");
}

}  // namespace

std::string effect_transition_intent_v2_signing_input_or_throw(
    const EffectTransitionIntentPayloadFields& fields) {
    validate_v2_fields_or_throw(fields);
    BoundedMachineText out(kEffectTransitionIntentMaximumLegacySigningInputBytes,
                           "effect transition v2 signing input");
    append_line(out, kEffectTransitionIntentV2Format);
    append_line(out, fields.intent_id);
    append_line(out, fields.intent_subject);
    append_line(out, fields.issued_at);
    append_line(out, fields.ledger_backend);
    append_line(out, fields.ledger_instance_id);
    append_line(out, fields.prepared_ledger_head_hash);
    append_line(out, fields.effect_transition_previous_hash);
    append_line(out, fields.effect_idempotency_key);
    out.append_decimal(fields.prepared_sequence);
    out.append('\n');
    append_line(out, fields.prepared_entry_hash);
    append_line(out, fields.terminal_state);
    append_line(out, fields.result_digest_sha256);
    append_line(out, fields.transition_reason);
    return std::move(out).finish();
}

FrozenEffectTransitionIntentV3Payload
FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
    EffectTransitionIntentPayloadFields fields) {
    validate_v3_fields_or_throw(fields);
    return FrozenEffectTransitionIntentV3Payload(std::move(fields));
}

std::string effect_transition_intent_v3_signing_input_or_throw(
    const FrozenEffectTransitionIntentV3Payload& payload) {
    const auto& fields = payload.fields();
    BoundedMachineText out(kEffectTransitionIntentMaximumSigningInputBytes);
    out.append("anonsync-length-prefixed-tuple-v1");
    append_component(out, kEffectTransitionIntentV3Format);
    append_named_component(out, "intent_id", fields.intent_id);
    append_named_component(out, "intent_subject", fields.intent_subject);
    append_named_component(out, "issued_at", fields.issued_at);
    append_named_component(out, "ledger_backend", fields.ledger_backend);
    append_named_component(out, "ledger_instance_id", fields.ledger_instance_id);
    append_named_component(out, "prepared_ledger_head_hash",
                           fields.prepared_ledger_head_hash);
    append_named_component(out, "effect_transition_previous_hash",
                           fields.effect_transition_previous_hash);
    append_named_component(out, "effect_idempotency_key",
                           fields.effect_idempotency_key);
    append_named_component(out, "prepared_sequence",
                           decimal_text(fields.prepared_sequence));
    append_named_component(out, "prepared_entry_hash", fields.prepared_entry_hash);
    append_named_component(out, "terminal_state", fields.terminal_state);
    append_named_component(out, "result_digest_sha256",
                           fields.result_digest_sha256);
    append_named_component(out, "transition_reason", fields.transition_reason);
    return std::move(out).finish();
}

void validate_effect_transition_intent_signature_fields_or_throw(
    const EffectTransitionIntentSignatureFields& signature) {
    require_nonempty_bounded_control_free(
        signature.kid, kEffectTransitionIntentMaximumSignerKidBytes,
        "effect transition signer kid");
    if (signature.signature_b64url.size() >
        kEffectTransitionIntentMaximumSignatureBytes) {
        throw std::runtime_error(
            "effect transition signature exceeds byte budget");
    }
    if (!is_base64url_without_padding(signature.signature_b64url)) {
        throw std::runtime_error(
            "effect transition signature is not unpadded base64url");
    }
}

EffectTransitionIntentV3Publication
EffectTransitionIntentV3Publication::bind_or_throw(
    FrozenEffectTransitionIntentV3Payload payload,
    std::string payload_signing_input_sha256,
    EffectTransitionIntentSignatureFields signature) {
    if (!is_lower_hex_sha256(payload_signing_input_sha256)) {
        throw std::runtime_error("effect transition v3 signing-input digest is invalid");
    }
    const std::string exact_signing_input =
        effect_transition_intent_v3_signing_input_or_throw(payload);
    if (payload_signing_input_sha256 != anonsync::sha256_hex(exact_signing_input)) {
        throw std::runtime_error(
            "effect transition v3 signing-input digest does not bind the frozen payload");
    }
    validate_effect_transition_intent_signature_fields_or_throw(signature);
    return EffectTransitionIntentV3Publication(
        std::move(payload), std::move(payload_signing_input_sha256),
        std::move(signature));
}

std::string encode_effect_transition_intent_v3_json_or_throw(
    const EffectTransitionIntentV3Publication& publication) {
    const auto& fields = publication.payload().fields();
    const auto& signature = publication.signature();
    BoundedMachineText out(kEffectTransitionIntentMaximumJsonBytes);

    out.append("{\n");
    append_json_member_prefix(out, "  ", "format");
    append_json_string(out, kEffectTransitionIntentV3Format);
    out.append(",\n  \"payload\": {\n");
    append_json_member_prefix(out, "    ", "format");
    append_json_string(out, kEffectTransitionIntentV3PayloadFormat);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "intent_id");
    append_json_string(out, fields.intent_id);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "intent_subject");
    append_json_string(out, fields.intent_subject);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "issued_at");
    append_json_string(out, fields.issued_at);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "ledger_backend");
    append_json_string(out, fields.ledger_backend);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "ledger_instance_id");
    append_json_string(out, fields.ledger_instance_id);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "prepared_ledger_head_hash");
    append_json_string(out, fields.prepared_ledger_head_hash);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "effect_transition_previous_hash");
    append_json_string(out, fields.effect_transition_previous_hash);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "effect_idempotency_key");
    append_json_string(out, fields.effect_idempotency_key);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "prepared_sequence");
    out.append_decimal(fields.prepared_sequence);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "prepared_entry_hash");
    append_json_string(out, fields.prepared_entry_hash);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "terminal_state");
    append_json_string(out, fields.terminal_state);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "result_digest_sha256");
    append_json_string(out, fields.result_digest_sha256);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "transition_reason");
    append_json_string(out, fields.transition_reason);
    out.append("\n  },\n");
    append_json_member_prefix(out, "  ", "payload_signing_input_sha256");
    append_json_string(out, publication.payload_signing_input_sha256());
    out.append(",\n  \"signature\": {\n");
    append_json_member_prefix(out, "    ", "alg");
    append_json_string(out, "RS256");
    out.append(",\n");
    append_json_member_prefix(out, "    ", "kid");
    append_json_string(out, signature.kid);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "signature_b64url");
    append_json_string(out, signature.signature_b64url);
    out.append("\n  },\n");
    append_json_member_prefix(out, "  ", "blocked_claim");
    append_json_string(
        out,
        "rev0841 frozen relay publication; not HSM custody, remote delivery proof, or distributed exactly-once semantics.");
    out.append("\n}\n");

    return std::move(out).finish();
}

}  // namespace anonsync::persistence
