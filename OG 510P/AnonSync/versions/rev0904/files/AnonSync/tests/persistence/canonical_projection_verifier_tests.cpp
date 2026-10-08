#include "canonical_projection_verifier.hpp"

#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace anonsync::persistence;

namespace {

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

CanonicalIngressProjection canonical_projection() {
    CanonicalIngressProjection out;
    out.transport_envelope_idempotency_key =
        "sync-peer-transport-envelope:v1:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    out.transport_instance_id = "transport-sensitive-marker";
    out.transport_key_id = "transport-key-sensitive-marker";
    out.peer_id = "peer-sensitive-marker";
    out.peer_session_id = "peer-session-sensitive-marker";
    out.peer_response_batch_idempotency_key = "peer-response-sensitive-marker";
    out.logical_path = "private/sensitive-marker.bin";
    out.payload_digest_sha256 =
        "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd";
    out.response_count = 2;
    out.total_bytes = 16;
    out.issued_at_epoch = 100;
    out.expires_at_epoch = 200;
    return out;
}

PersistedIngressProjection matching_projection() {
    const CanonicalIngressProjection canonical = canonical_projection();
    PersistedIngressProjection out;
    out.transport_envelope_idempotency_key =
        canonical.transport_envelope_idempotency_key;
    out.transport_instance_id = canonical.transport_instance_id;
    out.transport_key_id = canonical.transport_key_id;
    out.peer_id = canonical.peer_id;
    out.peer_session_id = canonical.peer_session_id;
    out.peer_response_batch_idempotency_key =
        canonical.peer_response_batch_idempotency_key;
    out.logical_path = canonical.logical_path;
    out.payload_digest_sha256 = canonical.payload_digest_sha256;
    out.response_count = canonical.response_count;
    out.total_bytes = canonical.total_bytes;
    out.issued_at_epoch = canonical.issued_at_epoch;
    out.expires_at_epoch = canonical.expires_at_epoch;
    return out;
}

void require_value_free_summary(const std::string& summary,
                                const std::string& context,
                                std::uint64_t& checks) {
    const std::vector<std::string> forbidden{
        "sensitive-marker",
        "private/",
        "aaaaaaaaaaaaaaaa",
        "dddddddddddddddd",
        "forged-value-marker",
    };
    for (const auto& value : forbidden) {
        require(summary.find(value) == std::string::npos,
                context + " leaked projection content: " + summary,
                checks);
    }
}

struct MismatchCase final {
    ProjectionField field;
    std::function<void(PersistedIngressProjection&)> mutate;
};

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        {
            ProjectionVerificationResult result = CanonicalProjectionVerifier::verify(
                canonical_projection(), matching_projection());
            require(result.has_value(), "matching projection was rejected", checks);
            VerifiedIngressProjection verified = result.take_value();
            require(verified.canonical().logical_path ==
                        canonical_projection().logical_path,
                    "verified capability did not retain canonical evidence",
                    checks);
            require(verified.canonical().total_bytes == 16,
                    "verified capability changed canonical numeric evidence",
                    checks);
        }

        const std::vector<MismatchCase> mismatch_cases{
            {ProjectionField::transport_envelope_idempotency_key,
             [](PersistedIngressProjection& row) {
                 row.transport_envelope_idempotency_key =
                     "sync-peer-transport-envelope:v1:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
             }},
            {ProjectionField::transport_instance_id,
             [](PersistedIngressProjection& row) {
                 row.transport_instance_id = "forged-value-marker";
             }},
            {ProjectionField::transport_key_id,
             [](PersistedIngressProjection& row) {
                 row.transport_key_id = "forged-value-marker";
             }},
            {ProjectionField::peer_id,
             [](PersistedIngressProjection& row) {
                 row.peer_id = "forged-value-marker";
             }},
            {ProjectionField::peer_session_id,
             [](PersistedIngressProjection& row) {
                 row.peer_session_id = "forged-value-marker";
             }},
            {ProjectionField::peer_response_batch_idempotency_key,
             [](PersistedIngressProjection& row) {
                 row.peer_response_batch_idempotency_key = "forged-value-marker";
             }},
            {ProjectionField::logical_path,
             [](PersistedIngressProjection& row) {
                 row.logical_path = "forged-value-marker";
             }},
            {ProjectionField::payload_digest_sha256,
             [](PersistedIngressProjection& row) {
                 row.payload_digest_sha256 =
                     "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";
             }},
            {ProjectionField::response_count,
             [](PersistedIngressProjection& row) { row.response_count = 3; }},
            {ProjectionField::total_bytes,
             [](PersistedIngressProjection& row) { row.total_bytes = 17; }},
            {ProjectionField::issued_at_epoch,
             [](PersistedIngressProjection& row) { row.issued_at_epoch = 101; }},
            {ProjectionField::expires_at_epoch,
             [](PersistedIngressProjection& row) { row.expires_at_epoch = 201; }},
        };

        for (const auto& mismatch_case : mismatch_cases) {
            PersistedIngressProjection row = matching_projection();
            mismatch_case.mutate(row);
            const ProjectionVerificationResult result =
                CanonicalProjectionVerifier::verify(canonical_projection(), row);
            require(!result,
                    "mismatched projection field was accepted: " +
                        std::string(projection_field_name(mismatch_case.field)),
                    checks);
            require(result.error().mismatches.size() == 1,
                    "single-field mutation did not produce one mismatch",
                    checks);
            require(result.error().contains(mismatch_case.field),
                    "mismatch was attributed to the wrong field",
                    checks);
            const std::string summary = result.error().safe_summary();
            require(summary.find(
                        std::string(projection_field_name(mismatch_case.field)) +
                        ":different") != std::string::npos,
                    "safe summary omitted mismatched field",
                    checks);
            require_value_free_summary(summary, "single-field mismatch", checks);
        }

        {
            PersistedIngressProjection row = matching_projection();
            row.logical_path.reset();
            const ProjectionVerificationResult result =
                CanonicalProjectionVerifier::verify(canonical_projection(), row);
            require(!result, "missing projected path was accepted", checks);
            require(result.error().contains(ProjectionField::logical_path),
                    "missing path was attributed to the wrong field",
                    checks);
            require(result.error().safe_summary().find("logical_path:missing") !=
                        std::string::npos,
                    "missing path was not classified as missing evidence",
                    checks);
            require_value_free_summary(
                result.error().safe_summary(), "missing projection", checks);
        }

        {
            PersistedIngressProjection row = matching_projection();
            row.peer_id = "forged-value-marker";
            row.logical_path.reset();
            row.total_bytes = 99;
            const ProjectionVerificationResult result =
                CanonicalProjectionVerifier::verify(canonical_projection(), row);
            require(!result, "multi-field contradiction was accepted", checks);
            require(result.error().mismatches.size() == 3,
                    "multi-field contradiction lost evidence",
                    checks);
            require(result.error().contains(ProjectionField::peer_id) &&
                        result.error().contains(ProjectionField::logical_path) &&
                        result.error().contains(ProjectionField::total_bytes),
                    "multi-field contradiction omitted a field",
                    checks);
            require_value_free_summary(
                result.error().safe_summary(), "multi-field mismatch", checks);
        }

        const std::vector<std::pair<ProjectionField, std::string>> names{
            {ProjectionField::transport_envelope_idempotency_key,
             "transport_envelope_idempotency_key"},
            {ProjectionField::transport_instance_id, "transport_instance_id"},
            {ProjectionField::transport_key_id, "transport_key_id"},
            {ProjectionField::peer_id, "peer_id"},
            {ProjectionField::peer_session_id, "peer_session_id"},
            {ProjectionField::peer_response_batch_idempotency_key,
             "peer_response_batch_idempotency_key"},
            {ProjectionField::logical_path, "logical_path"},
            {ProjectionField::payload_digest_sha256, "payload_digest_sha256"},
            {ProjectionField::response_count, "response_count"},
            {ProjectionField::total_bytes, "total_bytes"},
            {ProjectionField::issued_at_epoch, "issued_at_epoch"},
            {ProjectionField::expires_at_epoch, "expires_at_epoch"},
        };
        for (const auto& [field, expected_name] : names) {
            require(projection_field_name(field) == expected_name,
                    "projection field name is unstable",
                    checks);
        }

        std::cout << "canonical projection verifier: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "canonical projection verifier: " << error.what() << '\n';
        return 1;
    }
}
