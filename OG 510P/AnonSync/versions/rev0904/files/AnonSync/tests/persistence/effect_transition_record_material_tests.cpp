#include "effect_transition_record_material.hpp"
#include "effect_transition_intent_publication.hpp"
#include "sqlite_replay_ledger_schema_contract.hpp"

#include <iostream>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

using anonsync::persistence::EffectTransitionRecordFields;
using anonsync::persistence::FrozenEffectTransitionRecord;
using anonsync::persistence::effect_transition_record_hash_material_or_throw;
using anonsync::persistence::effect_transition_record_hash_or_throw;

class HostileNumberFacet final : public std::num_put<char> {
protected:
    iter_type do_put(iter_type out, std::ios_base&, char_type,
                     long value) const override {
        const std::string text = "locale(" + std::to_string(value) + ")";
        for (const char c : text) *out++ = c;
        return out;
    }

    iter_type do_put(iter_type out, std::ios_base&, char_type,
                     unsigned long value) const override {
        const std::string text = "locale(" + std::to_string(value) + ")";
        for (const char c : text) *out++ = c;
        return out;
    }
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
void require_throws(Callable&& callable, const std::string& message,
                    int& checks) {
    try {
        callable();
    } catch (const std::exception&) {
        ++checks;
        return;
    }
    throw std::runtime_error(message);
}

EffectTransitionRecordFields valid_fields() {
    EffectTransitionRecordFields fields;
    fields.sequence = 42;
    fields.previous_hash = std::string(64, '1');
    fields.ledger_instance_id = std::string(64, '2');
    fields.effect_idempotency_key = std::string(64, '3');
    fields.prepared_sequence = 7000;
    fields.prepared_entry_hash = std::string(64, '4');
    fields.terminal_state = "applied";
    fields.result_digest_sha256 = std::string(64, '5');
    fields.transition_reason = "relay applied exact result";
    fields.transition_intent_id = std::string(64, '6');
    fields.transition_intent_signer_kid = "relay-key-A";
    fields.transition_intent_sha256 = std::string(64, '7');
    return fields;
}

std::string unchecked_parent_material(
    const EffectTransitionRecordFields& fields) {
    std::ostringstream out;
    out << anonsync::persistence::kSqliteReplayLedgerEntryMaterialVersion
        << '\n'
        << fields.sequence << '\n'
        << fields.previous_hash << '\n'
        << fields.ledger_instance_id << '\n'
        << fields.effect_idempotency_key << '\n'
        << fields.prepared_sequence << '\n'
        << fields.prepared_entry_hash << '\n'
        << fields.terminal_state << '\n'
        << fields.result_digest_sha256 << '\n'
        << fields.transition_reason << '\n'
        << fields.transition_intent_id << '\n'
        << fields.transition_intent_signer_kid << '\n'
        << fields.transition_intent_sha256;
    return out.str();
}

}  // namespace

int main() {
    int checks = 0;
    try {
        const auto source = valid_fields();
        const auto frozen =
            FrozenEffectTransitionRecord::freeze_or_throw(source);
        const std::string material =
            effect_transition_record_hash_material_or_throw(frozen);
        require(material.starts_with(
                    std::string(anonsync::persistence::
                                    kSqliteReplayLedgerEntryMaterialVersion) +
                    "\n42\n"),
                "effect transition material lost its domain and sequence",
                checks);
        require(material.find("\n7000\n") != std::string::npos,
                "effect transition material changed prepared sequence spelling",
                checks);
        require(effect_transition_record_hash_or_throw(frozen).size() == 64,
                "effect transition material did not produce a SHA-256 digest",
                checks);

        {
            const std::locale hostile(std::locale::classic(),
                                      new HostileNumberFacet);
            const ScopedGlobalLocale restore(hostile);
            require(effect_transition_record_hash_material_or_throw(frozen) ==
                        material,
                    "effect transition hash material depends on global locale",
                    checks);
            require(material.find("locale(") == std::string::npos,
                    "effect transition hash material contains locale output",
                    checks);
        }

        {
            auto mutable_fields = valid_fields();
            const auto snapshot =
                FrozenEffectTransitionRecord::freeze_or_throw(mutable_fields);
            const std::string before =
                effect_transition_record_hash_material_or_throw(snapshot);
            mutable_fields.sequence = 9000;
            mutable_fields.transition_reason = "mutated broad record";
            require(effect_transition_record_hash_material_or_throw(snapshot) ==
                        before,
                    "frozen effect transition record changed after source mutation",
                    checks);
            require(snapshot.fields().sequence == 42 &&
                        snapshot.fields().transition_reason ==
                            "relay applied exact result",
                    "frozen effect transition record retained source aliases",
                    checks);
        }

        {
            auto left = valid_fields();
            auto right = valid_fields();
            left.transition_reason = "A\nB";
            left.transition_intent_id = "C";
            right.transition_reason = "A";
            right.transition_intent_id = "B\nC";
            require(left.transition_reason != right.transition_reason &&
                        left.transition_intent_id !=
                            right.transition_intent_id,
                    "effect transition collision tuples are not distinct",
                    checks);
            require(unchecked_parent_material(left) ==
                        unchecked_parent_material(right),
                    "parent effect transition newline collision did not collide",
                    checks);
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(left);
                },
                "effect transition record accepted delimiter-bearing reason",
                checks);
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(right);
                },
                "effect transition record accepted delimiter-bearing intent id",
                checks);
        }

        {
            auto bad = valid_fields();
            bad.transition_intent_signer_kid = "kid\nnext";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted delimiter-bearing signer kid",
                checks);
            bad = valid_fields();
            bad.transition_intent_signer_kid = std::string("kid-\xc3\x28", 6);
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted malformed signer UTF-8",
                checks);
            bad = valid_fields();
            bad.transition_reason.assign(
                anonsync::persistence::
                        kEffectTransitionIntentMaximumReasonBytes +
                    1,
                'r');
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted oversized reason", checks);
        }

        {
            auto bad = valid_fields();
            bad.sequence = 0;
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted nonpositive sequence",
                checks);
            bad = valid_fields();
            bad.sequence =
                anonsync::persistence::
                    kEffectTransitionIntentMaximumExactJsonInteger +
                1;
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted an inexact chain sequence",
                checks);
            bad = valid_fields();
            bad.prepared_sequence =
                anonsync::persistence::
                    kEffectTransitionIntentMaximumExactJsonInteger +
                1;
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted inexact prepared sequence",
                checks);
            bad = valid_fields();
            bad.previous_hash = "not-a-hash";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted invalid previous hash",
                checks);
            bad = valid_fields();
            bad.terminal_state = "prepared";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted nonterminal state", checks);
            bad = valid_fields();
            bad.transition_intent_id = "human\nintent";
            require_throws(
                [&] {
                    (void)FrozenEffectTransitionRecord::freeze_or_throw(bad);
                },
                "effect transition record accepted control-bearing intent id",
                checks);
        }

        std::cout << "effect transition record material: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "effect transition record material: " << error.what()
                  << '\n';
        return 1;
    }
}
