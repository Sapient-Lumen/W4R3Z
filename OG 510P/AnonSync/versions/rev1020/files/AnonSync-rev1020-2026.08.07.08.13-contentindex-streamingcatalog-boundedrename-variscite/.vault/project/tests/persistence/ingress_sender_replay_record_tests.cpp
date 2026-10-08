#include "ingress_sender_replay_record.hpp"

#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using namespace anonsync::persistence;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

IngressSenderReplayEvidence valid_evidence() {
    IngressSenderReplayEvidence evidence;
    evidence.replay_key_sha256 = std::string(64, 'a');
    evidence.format = std::string(kIngressSenderReplayRecordFormat);
    evidence.service_config_sha256 = std::string(64, 'b');
    evidence.ingress_profile_sha256 = std::string(64, 'c');
    evidence.sender_replay_cache_instance_id = "cache-instance-sensitive-marker";
    evidence.sender_proof_kid = "proof-kid-sensitive-marker";
    evidence.principal = "principal-sensitive-marker";
    evidence.nonce = "nonce-sensitive-01";
    evidence.issued_at_epoch = 1000;
    evidence.observed_at_epoch = 1000;
    evidence.replay_window_seconds = 300;
    evidence.material_sha256 = std::string(64, 'd');
    return evidence;
}

PreparedEffectEvidence valid_prepared() {
    PreparedEffectEvidence prepared;
    prepared.sequence = 7;
    prepared.entry_hash = std::string(64, 'e');
    prepared.effect_idempotency_key = std::string(64, 'f');
    return prepared;
}

IngressSenderReplayRecord valid_record() {
    return IngressSenderReplayRecord{valid_evidence(), valid_prepared()};
}

void require_failure(const IngressSenderReplayValidation& result,
                     IngressSenderReplayFailure failure,
                     std::string_view field,
                     const std::string& context,
                     std::uint64_t& checks) {
    require(!result, context + " was accepted", checks);
    require(result.failure == failure, context + " returned wrong failure", checks);
    require(result.field == field, context + " returned wrong field", checks);
    const std::string summary = result.safe_summary();
    require(summary.find(std::string(ingress_sender_replay_failure_name(failure))) !=
                std::string::npos,
            context + " summary omitted failure", checks);
    require(summary.find("sensitive-marker") == std::string::npos,
            context + " summary leaked observed value bytes", checks);
}

struct EvidenceMutation final {
    IngressSenderReplayFailure failure;
    std::string_view field;
    std::function<void(IngressSenderReplayEvidence&)> mutate;
};

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        {
            const auto result = validate_ingress_sender_replay_evidence(valid_evidence());
            require(result.has_value(), "valid replay evidence was rejected", checks);
            require(result.safe_summary() == "ingress_sender_replay[:none]",
                    "success summary changed unexpectedly", checks);
        }

        const std::vector<EvidenceMutation> mutations{
            {IngressSenderReplayFailure::unsupported_format, "format",
             [](auto& value) { value.format = "forged-sensitive-marker"; }},
            {IngressSenderReplayFailure::malformed_replay_key_digest,
             "replay_key_sha256", [](auto& value) { value.replay_key_sha256[0] = 'A'; }},
            {IngressSenderReplayFailure::malformed_service_config_digest,
             "service_config_sha256", [](auto& value) { value.service_config_sha256.resize(63); }},
            {IngressSenderReplayFailure::malformed_ingress_profile_digest,
             "ingress_profile_sha256", [](auto& value) { value.ingress_profile_sha256[1] = 'g'; }},
            {IngressSenderReplayFailure::malformed_material_digest,
             "material_sha256", [](auto& value) { value.material_sha256.clear(); }},
            {IngressSenderReplayFailure::malformed_cache_instance_id,
             "sender_replay_cache_instance_id", [](auto& value) { value.sender_replay_cache_instance_id = "bad space"; }},
            {IngressSenderReplayFailure::malformed_sender_proof_kid,
             "sender_proof_kid", [](auto& value) { value.sender_proof_kid.assign(513, 'x'); }},
            {IngressSenderReplayFailure::empty_principal, "principal",
             [](auto& value) { value.principal.clear(); }},
            {IngressSenderReplayFailure::principal_too_large, "principal",
             [](auto& value) { value.principal.assign(4097, 'p'); }},
            {IngressSenderReplayFailure::principal_contains_control, "principal",
             [](auto& value) { value.principal = std::string("principal\0hidden", 16); }},
            {IngressSenderReplayFailure::malformed_nonce, "nonce",
             [](auto& value) { value.nonce = "too-short"; }},
            {IngressSenderReplayFailure::invalid_replay_window,
             "replay_window_seconds", [](auto& value) { value.replay_window_seconds = 86401; }},
            {IngressSenderReplayFailure::invalid_issued_at, "issued_at_epoch",
             [](auto& value) { value.issued_at_epoch = 0; }},
            {IngressSenderReplayFailure::invalid_observed_at, "observed_at_epoch",
             [](auto& value) { value.observed_at_epoch = -1; }},
            {IngressSenderReplayFailure::issued_before_window, "issued_at_epoch",
             [](auto& value) { value.issued_at_epoch = 699; }},
            {IngressSenderReplayFailure::issued_after_future_skew, "issued_at_epoch",
             [](auto& value) { value.issued_at_epoch = 1301; }},
        };

        for (const auto& mutation : mutations) {
            IngressSenderReplayEvidence evidence = valid_evidence();
            mutation.mutate(evidence);
            require_failure(validate_ingress_sender_replay_evidence(evidence),
                            mutation.failure, mutation.field,
                            std::string(mutation.field), checks);
        }

        {
            IngressSenderReplayEvidence evidence = valid_evidence();
            evidence.observed_at_epoch = INT64_MAX;
            evidence.issued_at_epoch = INT64_MAX;
            require(validate_ingress_sender_replay_evidence(evidence).has_value(),
                    "maximum equal timestamps were rejected", checks);
            evidence.issued_at_epoch = INT64_MAX - 86400;
            evidence.replay_window_seconds = 86400;
            require(validate_ingress_sender_replay_evidence(evidence).has_value(),
                    "maximum in-window timestamps were rejected", checks);
        }

        {
            IngressSenderReplayRecord record = valid_record();
            require(verify_ingress_sender_replay_record(record, valid_prepared()).has_value(),
                    "valid replay record was rejected", checks);
        }
        {
            IngressSenderReplayRecord record = valid_record();
            record.prepared.sequence = 0;
            require_failure(verify_ingress_sender_replay_record(record, valid_prepared()),
                            IngressSenderReplayFailure::invalid_prepared_sequence,
                            "prepared_sequence", "zero prepared sequence", checks);
        }
        {
            IngressSenderReplayRecord record = valid_record();
            record.prepared.entry_hash[0] = 'G';
            require_failure(verify_ingress_sender_replay_record(record, valid_prepared()),
                            IngressSenderReplayFailure::malformed_prepared_entry_hash,
                            "prepared_entry_hash", "malformed prepared hash", checks);
        }
        {
            IngressSenderReplayRecord record = valid_record();
            record.prepared.effect_idempotency_key.resize(63);
            require_failure(verify_ingress_sender_replay_record(record, valid_prepared()),
                            IngressSenderReplayFailure::malformed_effect_idempotency_key,
                            "effect_idempotency_key", "malformed effect key", checks);
        }
        {
            IngressSenderReplayRecord record = valid_record();
            PreparedEffectEvidence expected = valid_prepared();
            expected.sequence++;
            require_failure(verify_ingress_sender_replay_record(record, expected),
                            IngressSenderReplayFailure::prepared_binding_mismatch,
                            "prepared_evidence", "prepared sequence alias", checks);
            expected = valid_prepared();
            expected.entry_hash[0] = 'a';
            require_failure(verify_ingress_sender_replay_record(record, expected),
                            IngressSenderReplayFailure::prepared_binding_mismatch,
                            "prepared_evidence", "prepared hash alias", checks);
            expected = valid_prepared();
            expected.effect_idempotency_key[0] = 'a';
            require_failure(verify_ingress_sender_replay_record(record, expected),
                            IngressSenderReplayFailure::prepared_binding_mismatch,
                            "prepared_evidence", "prepared effect alias", checks);
        }
        {
            const IngressSenderReplayEvidence first = valid_evidence();
            IngressSenderReplayEvidence same = first;
            same.principal = "different-principal";
            same.material_sha256 = std::string(64, '0');
            require(ingress_sender_replay_nonce_identity_key(first) ==
                        ingress_sender_replay_nonce_identity_key(same),
                    "nonce identity unexpectedly included non-uniqueness fields", checks);
            same = first;
            same.nonce.back() = '2';
            require(ingress_sender_replay_nonce_identity_key(first) !=
                        ingress_sender_replay_nonce_identity_key(same),
                    "nonce identity did not bind nonce", checks);
            same = first;
            same.sender_proof_kid += "-other";
            require(ingress_sender_replay_nonce_identity_key(first) !=
                        ingress_sender_replay_nonce_identity_key(same),
                    "nonce identity did not bind proof key", checks);
        }

        std::cout << "ingress_sender_replay_record_checks=" << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "ingress_sender_replay_record_failure=" << error.what() << "\n";
        return 1;
    }
}
