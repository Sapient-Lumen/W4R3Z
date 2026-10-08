#include "effect_transition_intent_publication.hpp"
#include "sha256_digest.hpp"

#include <iostream>
#include <locale>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

using anonsync::persistence::EffectTransitionIntentPayloadFields;
using anonsync::persistence::EffectTransitionIntentSignatureFields;
using anonsync::persistence::EffectTransitionIntentV3Publication;
using anonsync::persistence::FrozenEffectTransitionIntentV3Payload;
using anonsync::persistence::effect_transition_intent_v2_signing_input_or_throw;
using anonsync::persistence::effect_transition_intent_v3_signing_input_or_throw;
using anonsync::persistence::encode_effect_transition_intent_v3_json_or_throw;

class GroupedNumberPunctuation final : public std::numpunct<char> {
protected:
    char do_thousands_sep() const override { return '_'; }
    std::string do_grouping() const override { return "\3"; }
};

class ScopedGlobalLocale final {
public:
    explicit ScopedGlobalLocale(const std::locale& replacement)
        : previous_(std::locale::global(replacement)) {}
    ScopedGlobalLocale(const ScopedGlobalLocale&) = delete;
    ScopedGlobalLocale& operator=(const ScopedGlobalLocale&) = delete;
    ~ScopedGlobalLocale() { std::locale::global(previous_); }

private:
    std::locale previous_;
};

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename Callable>
void require_throws(Callable&& callable, const std::string& message, int& checks) {
    try {
        callable();
    } catch (const std::exception&) {
        ++checks;
        return;
    }
    throw std::runtime_error(message);
}

EffectTransitionIntentPayloadFields valid_fields() {
    EffectTransitionIntentPayloadFields fields;
    fields.intent_id = std::string(64, '1');
    fields.intent_subject = "sqlite-wal-effect-terminal-transition";
    fields.issued_at = "2026-07-19T12:34:56Z";
    fields.ledger_backend = "sqlite-wal";
    fields.ledger_instance_id = std::string(64, '2');
    fields.prepared_ledger_head_hash = std::string(64, '3');
    fields.effect_transition_previous_hash = "GENESIS";
    fields.effect_idempotency_key = std::string(64, '4');
    fields.prepared_sequence = 7000;
    fields.prepared_entry_hash = std::string(64, '5');
    fields.terminal_state = "applied";
    fields.result_digest_sha256 = std::string(64, '6');
    fields.transition_reason = "relay applied exact result";
    return fields;
}

EffectTransitionIntentV3Publication publication_from(
    EffectTransitionIntentPayloadFields fields,
    std::string kid = "relay-signing-key-A",
    std::string signature = "AbCdEf0123_-") {
    auto frozen = FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
        std::move(fields));
    const std::string signing_input =
        effect_transition_intent_v3_signing_input_or_throw(frozen);
    return EffectTransitionIntentV3Publication::bind_or_throw(
        std::move(frozen), anonsync::sha256_hex(signing_input),
        EffectTransitionIntentSignatureFields{
            std::move(kid), std::move(signature)});
}

}  // namespace

int main() {
    int checks = 0;
    try {
        const auto fields = valid_fields();
        auto frozen = FrozenEffectTransitionIntentV3Payload::freeze_or_throw(fields);
        const std::string v3 = effect_transition_intent_v3_signing_input_or_throw(frozen);
        require(v3.starts_with("anonsync-length-prefixed-tuple-v1"),
                "v3 signing input lost its framing domain", checks);
        require(v3.find("17:prepared_sequence4:7000") != std::string::npos,
                "v3 signing input does not frame prepared_sequence", checks);
        require(v3.find("transition_reason") != std::string::npos,
                "v3 signing input omitted transition reason", checks);

        const std::string v2 = effect_transition_intent_v2_signing_input_or_throw(fields);
        require(v2.starts_with(
                    "anonsync-effect-transition-intent-v2-ledger-instance\n"),
                "v2 compatibility prefix changed", checks);
        require(v2.find("\n7000\n") != std::string::npos,
                "v2 integer spelling changed", checks);

        {
            const std::locale grouped(std::locale::classic(),
                                      new GroupedNumberPunctuation);
            const ScopedGlobalLocale restore(grouped);
            const std::string grouped_v2 =
                effect_transition_intent_v2_signing_input_or_throw(fields);
            const std::string grouped_v3 =
                effect_transition_intent_v3_signing_input_or_throw(frozen);
            const std::string grouped_json =
                encode_effect_transition_intent_v3_json_or_throw(
                    publication_from(fields));
            require(grouped_v2 == v2,
                    "v2 signing bytes depend on the process-global locale", checks);
            require(grouped_v3 == v3,
                    "v3 signing bytes depend on the process-global locale", checks);
            require(grouped_json.find("\"prepared_sequence\": 7000") !=
                        std::string::npos,
                    "v3 JSON integer depends on the process-global locale", checks);
            require(grouped_json.find("7_000") == std::string::npos,
                    "v3 JSON contains a grouped integer", checks);
        }

        {
            auto mutable_fields = valid_fields();
            auto snapshot =
                FrozenEffectTransitionIntentV3Payload::freeze_or_throw(mutable_fields);
            const std::string before =
                effect_transition_intent_v3_signing_input_or_throw(snapshot);
            mutable_fields.prepared_sequence = 9000;
            mutable_fields.transition_reason = "mutated broad model";
            const std::string after =
                effect_transition_intent_v3_signing_input_or_throw(snapshot);
            require(before == after,
                    "frozen payload changed after source mutation", checks);
            require(snapshot.fields().prepared_sequence == 7000 &&
                        snapshot.fields().transition_reason ==
                            "relay applied exact result",
                    "frozen payload retained aliases to source fields", checks);
        }

        {
            auto escaped = valid_fields();
            escaped.transition_reason = "quoted \\\"value\\\" and slash \\\\";
            const std::string json = encode_effect_transition_intent_v3_json_or_throw(
                publication_from(std::move(escaped), "kid-with-dash", "A_b-9"));
            require(json.starts_with("{\n"), "v3 JSON lost object framing", checks);
            require(json.ends_with("}\n"), "v3 JSON lost final newline", checks);
            require(json.find("anonsync-effect-transition-intent-v3-framed-publication") !=
                        std::string::npos,
                    "v3 JSON omitted outer format", checks);
            require(json.find("anonsync-effect-transition-intent-payload-v3-framed-publication") !=
                        std::string::npos,
                    "v3 JSON omitted payload format", checks);
            require(json.find(R"(quoted \\\"value\\\" and slash \\\\)") !=
                        std::string::npos,
                    "v3 JSON did not escape string bytes", checks);
            require(json.size() <=
                        anonsync::persistence::kEffectTransitionIntentMaximumJsonBytes,
                    "v3 JSON exceeded its declared byte ceiling", checks);
        }

        {
            auto changed = valid_fields();
            changed.transition_reason = "different exact result";
            auto changed_frozen =
                FrozenEffectTransitionIntentV3Payload::freeze_or_throw(changed);
            require(effect_transition_intent_v3_signing_input_or_throw(changed_frozen) !=
                        v3,
                    "different payloads produced identical framed bytes", checks);
        }

        {
            auto maximum_reason = valid_fields();
            maximum_reason.transition_reason.assign(
                anonsync::persistence::kEffectTransitionIntentMaximumReasonBytes,
                'r');
            (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
                maximum_reason);
            ++checks;
            maximum_reason.transition_reason.push_back('r');
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
                        maximum_reason);
                },
                "v3 accepted an oversized transition reason", checks);
        }

        {
            auto control_reason = valid_fields();
            control_reason.transition_reason = "line one\nline two";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
                        control_reason);
                },
                "v3 accepted delimiter-bearing reason text", checks);
        }

        {
            auto malformed_reason = valid_fields();
            malformed_reason.transition_reason = std::string("\xc3\x28", 2);
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
                        malformed_reason);
                },
                "v3 accepted malformed UTF-8 reason text", checks);
        }

        {
            auto bad = valid_fields();
            bad.intent_id = "human-readable-id";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(bad);
                },
                "v3 accepted a non-digest intent id", checks);
            bad = valid_fields();
            bad.issued_at = "2026-02-30T00:00:00Z";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(bad);
                },
                "v3 accepted an impossible UTC date", checks);
            bad = valid_fields();
            bad.prepared_sequence = 0;
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(bad);
                },
                "v3 accepted a nonpositive sequence", checks);
            bad = valid_fields();
            bad.prepared_sequence =
                anonsync::persistence::kEffectTransitionIntentMaximumExactJsonInteger;
            const auto maximum_integer_payload =
                FrozenEffectTransitionIntentV3Payload::freeze_or_throw(bad);
            require(effect_transition_intent_v3_signing_input_or_throw(
                        maximum_integer_payload)
                        .find("16:9007199254740991") != std::string::npos,
                    "v3 did not preserve the maximum exact JSON integer", checks);
            bad = valid_fields();
            bad.prepared_sequence =
                anonsync::persistence::kEffectTransitionIntentMaximumExactJsonInteger + 1;
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(bad);
                },
                "v3 accepted an inexact JSON integer", checks);
            bad = valid_fields();
            bad.terminal_state = "prepared";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionIntentV3Payload::freeze_or_throw(bad);
                },
                "v3 accepted a nonterminal state", checks);
        }

        {
            require_throws(
                [&] {
                    (void)publication_from(valid_fields(), std::string(257, 'k'));
                },
                "v3 accepted an oversized signer kid", checks);
            require_throws(
                [&] {
                    (void)publication_from(valid_fields(), "kid\nline");
                },
                "v3 accepted a control-bearing signer kid", checks);
            require_throws(
                [&] {
                    (void)publication_from(
                        valid_fields(), std::string("kid-\xc3\x28", 6));
                },
                "v3 accepted a malformed UTF-8 signer kid", checks);
            require_throws(
                [&] {
                    (void)publication_from(valid_fields(), "kid", "has=padding");
                },
                "v3 accepted padded/non-base64url signature text", checks);
            require_throws(
                [&] {
                    auto payload =
                        FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
                            valid_fields());
                    (void)EffectTransitionIntentV3Publication::bind_or_throw(
                        std::move(payload), "not-a-digest",
                        EffectTransitionIntentSignatureFields{"kid", "Ab_9"});
                },
                "v3 accepted an invalid signing-input digest", checks);
            require_throws(
                [&] {
                    auto payload =
                        FrozenEffectTransitionIntentV3Payload::freeze_or_throw(
                            valid_fields());
                    (void)EffectTransitionIntentV3Publication::bind_or_throw(
                        std::move(payload), std::string(64, 'f'),
                        EffectTransitionIntentSignatureFields{"kid", "Ab_9"});
                },
                "v3 accepted a digest for a different frozen payload", checks);
        }

        std::cout << "effect transition intent publication: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "effect transition intent publication: " << error.what()
                  << '\n';
        return 1;
    }
}
