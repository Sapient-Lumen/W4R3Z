#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync::persistence {

inline constexpr std::string_view kEffectTransitionIntentV2Format =
    "anonsync-effect-transition-intent-v2-ledger-instance";
inline constexpr std::string_view kEffectTransitionIntentV2PayloadFormat =
    "anonsync-effect-transition-intent-payload-v2-ledger-instance";
inline constexpr std::string_view kEffectTransitionIntentV3Format =
    "anonsync-effect-transition-intent-v3-framed-publication";
inline constexpr std::string_view kEffectTransitionIntentV3PayloadFormat =
    "anonsync-effect-transition-intent-payload-v3-framed-publication";
inline constexpr std::string_view kEffectTransitionIntentSubject =
    "sqlite-wal-effect-terminal-transition";
inline constexpr std::string_view kEffectTransitionIntentLedgerBackend =
    "sqlite-wal";

inline constexpr std::size_t kEffectTransitionIntentMaximumJsonBytes = 16 * 1024;
inline constexpr std::size_t kEffectTransitionTrustProfileMaximumJsonBytes =
    256 * 1024;
inline constexpr std::size_t kEffectTransitionIntentMaximumSigningInputBytes =
    4 * 1024;
inline constexpr std::size_t kEffectTransitionIntentMaximumLegacySigningInputBytes =
    16 * 1024;
inline constexpr std::size_t kEffectTransitionIntentMaximumReasonBytes = 1024;
inline constexpr std::size_t
    kEffectTransitionIntentMaximumLegacyIntentIdBytes = 1024;
inline constexpr std::size_t kEffectTransitionIntentMaximumSignerKidBytes = 256;
inline constexpr std::size_t kEffectTransitionIntentMaximumSignatureBytes = 8192;
inline constexpr std::int64_t kEffectTransitionIntentMaximumExactJsonInteger =
    9007199254740991LL;

// An owning copy of every value covered by an effect-transition signature.
// Fixed fields remain explicit so parsing, trust evaluation, signing, and
// publication can all consume one exact snapshot rather than rereading Json.
struct EffectTransitionIntentPayloadFields final {
    std::string intent_id;
    std::string intent_subject;
    std::string issued_at;
    std::string ledger_backend;
    std::string ledger_instance_id;
    std::string prepared_ledger_head_hash;
    std::string effect_transition_previous_hash;
    std::string effect_idempotency_key;
    std::int64_t prepared_sequence{};
    std::string prepared_entry_hash;
    std::string terminal_state;
    std::string result_digest_sha256;
    std::string transition_reason;
};

// V2 remains a read-compatibility format. This function preserves its exact
// newline-delimited bytes while making integer spelling independent of locale.
// The accepted legacy subset is control-free, bounded, well-formed UTF-8, and
// semantically identical to v3 so a signed claim cannot exploit delimiter text
// or bypass the frozen publication profile merely by selecting the old wire
// marker.
[[nodiscard]] std::string effect_transition_intent_v2_signing_input_or_throw(
    const EffectTransitionIntentPayloadFields& fields);

// V3 rejects delimiter-bearing controls and freezes every signed field before
// either the signing input or JSON document can be emitted.
class FrozenEffectTransitionIntentV3Payload final {
public:
    [[nodiscard]] static FrozenEffectTransitionIntentV3Payload freeze_or_throw(
        EffectTransitionIntentPayloadFields fields);

    [[nodiscard]] const EffectTransitionIntentPayloadFields& fields() const noexcept {
        return fields_;
    }

private:
    explicit FrozenEffectTransitionIntentV3Payload(
        EffectTransitionIntentPayloadFields fields)
        : fields_(std::move(fields)) {}

    EffectTransitionIntentPayloadFields fields_;
};

[[nodiscard]] std::string effect_transition_intent_v3_signing_input_or_throw(
    const FrozenEffectTransitionIntentV3Payload& payload);

struct EffectTransitionIntentSignatureFields final {
    std::string kid;
    std::string signature_b64url;
};

// Applies the same bounded, control-free signer identity and unpadded
// base64url signature grammar to both legacy-v2 verification and v3
// publication. This is also required by the durable transition hash material,
// which records the signer kid as one newline-delimited field.
void validate_effect_transition_intent_signature_fields_or_throw(
    const EffectTransitionIntentSignatureFields& signature);

class EffectTransitionIntentV3Publication final {
public:
    [[nodiscard]] static EffectTransitionIntentV3Publication bind_or_throw(
        FrozenEffectTransitionIntentV3Payload payload,
        std::string payload_signing_input_sha256,
        EffectTransitionIntentSignatureFields signature);

    [[nodiscard]] const FrozenEffectTransitionIntentV3Payload& payload() const noexcept {
        return payload_;
    }
    [[nodiscard]] const std::string& payload_signing_input_sha256() const noexcept {
        return payload_signing_input_sha256_;
    }
    [[nodiscard]] const EffectTransitionIntentSignatureFields& signature() const noexcept {
        return signature_;
    }

private:
    EffectTransitionIntentV3Publication(
        FrozenEffectTransitionIntentV3Payload payload,
        std::string payload_signing_input_sha256,
        EffectTransitionIntentSignatureFields signature)
        : payload_(std::move(payload)),
          payload_signing_input_sha256_(
              std::move(payload_signing_input_sha256)),
          signature_(std::move(signature)) {}

    FrozenEffectTransitionIntentV3Payload payload_;
    std::string payload_signing_input_sha256_;
    EffectTransitionIntentSignatureFields signature_;
};

[[nodiscard]] std::string encode_effect_transition_intent_v3_json_or_throw(
    const EffectTransitionIntentV3Publication& publication);

}  // namespace anonsync::persistence
