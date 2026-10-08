#include "canonical_projection_verifier.hpp"

#include <sstream>
#include <stdexcept>

namespace anonsync::persistence {
namespace {

template <typename T>
void compare_optional(
    std::vector<ProjectionMismatch>& mismatches,
    ProjectionField field,
    const T& expected,
    const std::optional<T>& observed) {
    if (!observed.has_value()) {
        mismatches.push_back({field, ProjectionMismatchKind::missing});
    } else if (*observed != expected) {
        mismatches.push_back({field, ProjectionMismatchKind::value_mismatch});
    }
}

}  // namespace

bool ProjectionVerificationError::contains(ProjectionField field) const noexcept {
    for (const auto& mismatch : mismatches) {
        if (mismatch.field == field) return true;
    }
    return false;
}

std::string ProjectionVerificationError::safe_summary() const {
    std::ostringstream out;
    out << "canonical_projection_mismatch[";
    for (std::size_t i = 0; i < mismatches.size(); ++i) {
        if (i != 0) out << ',';
        out << projection_field_name(mismatches[i].field) << ':'
            << (mismatches[i].kind == ProjectionMismatchKind::missing
                    ? "missing"
                    : "different");
    }
    out << ']';
    return out.str();
}

ProjectionVerificationResult ProjectionVerificationResult::success(
    CanonicalIngressProjection canonical) {
    ProjectionVerificationResult result;
    result.value_.emplace(VerifiedIngressProjection(std::move(canonical)));
    return result;
}

ProjectionVerificationResult ProjectionVerificationResult::failure(
    ProjectionVerificationError error) {
    ProjectionVerificationResult result;
    result.error_.emplace(std::move(error));
    return result;
}

const VerifiedIngressProjection& ProjectionVerificationResult::value() const {
    if (!value_) throw std::logic_error("projection verification result has no value");
    return *value_;
}

VerifiedIngressProjection ProjectionVerificationResult::take_value() {
    if (!value_) throw std::logic_error("projection verification result has no value");
    return std::move(*value_);
}

const ProjectionVerificationError& ProjectionVerificationResult::error() const {
    if (!error_) throw std::logic_error("projection verification result has no error");
    return *error_;
}

ProjectionVerificationResult CanonicalProjectionVerifier::verify(
    const CanonicalIngressProjection& canonical,
    const PersistedIngressProjection& persisted) {
    ProjectionVerificationError error;
    compare_optional(error.mismatches,
                     ProjectionField::transport_envelope_idempotency_key,
                     canonical.transport_envelope_idempotency_key,
                     persisted.transport_envelope_idempotency_key);
    compare_optional(error.mismatches,
                     ProjectionField::transport_instance_id,
                     canonical.transport_instance_id,
                     persisted.transport_instance_id);
    compare_optional(error.mismatches,
                     ProjectionField::transport_key_id,
                     canonical.transport_key_id,
                     persisted.transport_key_id);
    compare_optional(error.mismatches,
                     ProjectionField::peer_id,
                     canonical.peer_id,
                     persisted.peer_id);
    compare_optional(error.mismatches,
                     ProjectionField::peer_session_id,
                     canonical.peer_session_id,
                     persisted.peer_session_id);
    compare_optional(error.mismatches,
                     ProjectionField::peer_response_batch_idempotency_key,
                     canonical.peer_response_batch_idempotency_key,
                     persisted.peer_response_batch_idempotency_key);
    compare_optional(error.mismatches,
                     ProjectionField::logical_path,
                     canonical.logical_path,
                     persisted.logical_path);
    compare_optional(error.mismatches,
                     ProjectionField::payload_digest_sha256,
                     canonical.payload_digest_sha256,
                     persisted.payload_digest_sha256);
    compare_optional(error.mismatches,
                     ProjectionField::response_count,
                     canonical.response_count,
                     persisted.response_count);
    compare_optional(error.mismatches,
                     ProjectionField::total_bytes,
                     canonical.total_bytes,
                     persisted.total_bytes);
    compare_optional(error.mismatches,
                     ProjectionField::issued_at_epoch,
                     canonical.issued_at_epoch,
                     persisted.issued_at_epoch);
    compare_optional(error.mismatches,
                     ProjectionField::expires_at_epoch,
                     canonical.expires_at_epoch,
                     persisted.expires_at_epoch);

    if (!error.mismatches.empty()) {
        return ProjectionVerificationResult::failure(std::move(error));
    }
    // Return canonical values, never duplicated row values. Verification is a
    // capability to use the canonical projection, not authentication of an
    // ambient cache object.
    return ProjectionVerificationResult::success(canonical);
}

std::string_view projection_field_name(ProjectionField field) noexcept {
    switch (field) {
        case ProjectionField::transport_envelope_idempotency_key:
            return "transport_envelope_idempotency_key";
        case ProjectionField::transport_instance_id: return "transport_instance_id";
        case ProjectionField::transport_key_id: return "transport_key_id";
        case ProjectionField::peer_id: return "peer_id";
        case ProjectionField::peer_session_id: return "peer_session_id";
        case ProjectionField::peer_response_batch_idempotency_key:
            return "peer_response_batch_idempotency_key";
        case ProjectionField::logical_path: return "logical_path";
        case ProjectionField::payload_digest_sha256: return "payload_digest_sha256";
        case ProjectionField::response_count: return "response_count";
        case ProjectionField::total_bytes: return "total_bytes";
        case ProjectionField::issued_at_epoch: return "issued_at_epoch";
        case ProjectionField::expires_at_epoch: return "expires_at_epoch";
    }
    return "unknown";
}


}  // namespace anonsync::persistence
