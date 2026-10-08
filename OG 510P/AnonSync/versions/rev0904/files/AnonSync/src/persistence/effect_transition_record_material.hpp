#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <utility>

namespace anonsync::persistence {

inline constexpr std::size_t kEffectTransitionRecordMaximumMaterialBytes =
    16 * 1024;

// Every byte committed to the durable effect-transition hash chain. The legacy
// material version remains byte-compatible for ordinary records, but callers
// must first cross this owning validation boundary. That accepted subset makes
// the newline-delimited material injective by excluding delimiter-bearing
// controls from the only free-text and signer-identity fields.
struct EffectTransitionRecordFields final {
    std::int64_t sequence{};
    std::string previous_hash;
    std::string ledger_instance_id;
    std::string effect_idempotency_key;
    std::int64_t prepared_sequence{};
    std::string prepared_entry_hash;
    std::string terminal_state;
    std::string result_digest_sha256;
    std::string transition_reason;
    std::string transition_intent_id;
    std::string transition_intent_signer_kid;
    std::string transition_intent_sha256;
};

class FrozenEffectTransitionRecord final {
public:
    [[nodiscard]] static FrozenEffectTransitionRecord freeze_or_throw(
        EffectTransitionRecordFields fields);

    [[nodiscard]] const EffectTransitionRecordFields& fields() const noexcept {
        return fields_;
    }

private:
    explicit FrozenEffectTransitionRecord(EffectTransitionRecordFields fields)
        : fields_(std::move(fields)) {}

    EffectTransitionRecordFields fields_;
};

[[nodiscard]] std::string effect_transition_record_hash_material_or_throw(
    const FrozenEffectTransitionRecord& record);

[[nodiscard]] std::string effect_transition_record_hash_or_throw(
    const FrozenEffectTransitionRecord& record);

}  // namespace anonsync::persistence
