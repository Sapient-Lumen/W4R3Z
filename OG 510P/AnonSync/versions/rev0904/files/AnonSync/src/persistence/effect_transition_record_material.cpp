#include "effect_transition_record_material.hpp"

#include "effect_transition_intent_publication.hpp"
#include "frozen_publication_primitives.hpp"
#include "sha256_digest.hpp"
#include "sqlite_replay_ledger_schema_contract.hpp"

#include <stdexcept>
#include <utility>

namespace anonsync::persistence {
namespace {

using publication_detail::BoundedMachineText;
using publication_detail::append_line;
using publication_detail::is_lower_hex_sha256;
using publication_detail::is_sha256_or_genesis;
using publication_detail::require_nonempty_bounded_control_free;

void validate_fields_or_throw(const EffectTransitionRecordFields& fields) {
    if (fields.sequence <= 0 ||
        fields.sequence >
            kEffectTransitionIntentMaximumExactJsonInteger) {
        throw std::runtime_error(
            "effect transition record sequence is outside exact JSON range");
    }
    if (!is_sha256_or_genesis(fields.previous_hash)) {
        throw std::runtime_error(
            "effect transition record previous hash is invalid");
    }
    if (!is_lower_hex_sha256(fields.ledger_instance_id)) {
        throw std::runtime_error(
            "effect transition record ledger instance id is invalid");
    }
    if (!is_lower_hex_sha256(fields.effect_idempotency_key)) {
        throw std::runtime_error(
            "effect transition record idempotency key is invalid");
    }
    if (fields.prepared_sequence <= 0 ||
        fields.prepared_sequence >
            kEffectTransitionIntentMaximumExactJsonInteger) {
        throw std::runtime_error(
            "effect transition record prepared sequence is outside exact JSON range");
    }
    if (!is_lower_hex_sha256(fields.prepared_entry_hash)) {
        throw std::runtime_error(
            "effect transition record prepared entry hash is invalid");
    }
    if (fields.terminal_state != "applied" &&
        fields.terminal_state != "failed" &&
        fields.terminal_state != "compensated") {
        throw std::runtime_error(
            "effect transition record terminal state is invalid");
    }
    if (!is_lower_hex_sha256(fields.result_digest_sha256)) {
        throw std::runtime_error(
            "effect transition record result digest is invalid");
    }
    require_nonempty_bounded_control_free(
        fields.transition_reason, kEffectTransitionIntentMaximumReasonBytes,
        "effect transition record reason");
    require_nonempty_bounded_control_free(
        fields.transition_intent_id,
        kEffectTransitionIntentMaximumLegacyIntentIdBytes,
        "effect transition record intent id");
    require_nonempty_bounded_control_free(
        fields.transition_intent_signer_kid,
        kEffectTransitionIntentMaximumSignerKidBytes,
        "effect transition record signer kid");
    if (!is_lower_hex_sha256(fields.transition_intent_sha256)) {
        throw std::runtime_error(
            "effect transition record intent digest is invalid");
    }
}

}  // namespace

FrozenEffectTransitionRecord FrozenEffectTransitionRecord::freeze_or_throw(
    EffectTransitionRecordFields fields) {
    validate_fields_or_throw(fields);
    return FrozenEffectTransitionRecord(std::move(fields));
}

std::string effect_transition_record_hash_material_or_throw(
    const FrozenEffectTransitionRecord& record) {
    const auto& fields = record.fields();
    BoundedMachineText out(kEffectTransitionRecordMaximumMaterialBytes,
                           "effect transition record hash material");
    append_line(out, kSqliteReplayLedgerEntryMaterialVersion);
    out.append_decimal(fields.sequence);
    out.append('\n');
    append_line(out, fields.previous_hash);
    append_line(out, fields.ledger_instance_id);
    append_line(out, fields.effect_idempotency_key);
    out.append_decimal(fields.prepared_sequence);
    out.append('\n');
    append_line(out, fields.prepared_entry_hash);
    append_line(out, fields.terminal_state);
    append_line(out, fields.result_digest_sha256);
    append_line(out, fields.transition_reason);
    append_line(out, fields.transition_intent_id);
    append_line(out, fields.transition_intent_signer_kid);
    out.append(fields.transition_intent_sha256);
    return std::move(out).finish();
}

std::string effect_transition_record_hash_or_throw(
    const FrozenEffectTransitionRecord& record) {
    return anonsync::sha256_hex(
        effect_transition_record_hash_material_or_throw(record));
}

}  // namespace anonsync::persistence
