#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync::persistence {

// Canonical ingress-frame evidence is authoritative.  This type mirrors only
// the queue-parent columns that are redundant projections of that frame.  It
// deliberately excludes mutable scheduler/claim state and local enqueue time.
struct CanonicalIngressProjection final {
    std::string transport_envelope_idempotency_key;
    std::string transport_instance_id;
    std::string transport_key_id;
    std::string peer_id;
    std::string peer_session_id;
    std::string peer_response_batch_idempotency_key;
    std::string logical_path;
    std::string payload_digest_sha256;
    std::uint64_t response_count{};
    std::uint64_t total_bytes{};
    std::uint64_t issued_at_epoch{};
    std::uint64_t expires_at_epoch{};
};

// NULL remains explicit.  SQLite defaults, affinity coercion, and C++ zero
// initialization are not evidence that a projected value was durably present.
struct PersistedIngressProjection final {
    std::optional<std::string> transport_envelope_idempotency_key;
    std::optional<std::string> transport_instance_id;
    std::optional<std::string> transport_key_id;
    std::optional<std::string> peer_id;
    std::optional<std::string> peer_session_id;
    std::optional<std::string> peer_response_batch_idempotency_key;
    std::optional<std::string> logical_path;
    std::optional<std::string> payload_digest_sha256;
    std::optional<std::uint64_t> response_count;
    std::optional<std::uint64_t> total_bytes;
    std::optional<std::uint64_t> issued_at_epoch;
    std::optional<std::uint64_t> expires_at_epoch;
};

enum class ProjectionField : std::uint8_t {
    transport_envelope_idempotency_key,
    transport_instance_id,
    transport_key_id,
    peer_id,
    peer_session_id,
    peer_response_batch_idempotency_key,
    logical_path,
    payload_digest_sha256,
    response_count,
    total_bytes,
    issued_at_epoch,
    expires_at_epoch,
};

enum class ProjectionMismatchKind : std::uint8_t {
    missing,
    value_mismatch,
};

struct ProjectionMismatch final {
    ProjectionField field{};
    ProjectionMismatchKind kind{};
};

// Safe diagnostic data: callers can report the row identity they already own
// and these field names, but no peer/path/digest value is retained here.
struct ProjectionVerificationError final {
    std::vector<ProjectionMismatch> mismatches;

    [[nodiscard]] bool contains(ProjectionField field) const noexcept;
    [[nodiscard]] std::string safe_summary() const;
};

class VerifiedIngressProjection final {
public:
    VerifiedIngressProjection(const VerifiedIngressProjection&) = default;
    VerifiedIngressProjection& operator=(const VerifiedIngressProjection&) = default;
    VerifiedIngressProjection(VerifiedIngressProjection&&) noexcept = default;
    VerifiedIngressProjection& operator=(VerifiedIngressProjection&&) noexcept = default;

    [[nodiscard]] const CanonicalIngressProjection& canonical() const noexcept {
        return canonical_;
    }

private:
    explicit VerifiedIngressProjection(CanonicalIngressProjection canonical)
        : canonical_(std::move(canonical)) {}

    CanonicalIngressProjection canonical_;
    friend class CanonicalProjectionVerifier;
    friend class ProjectionVerificationResult;
};

class ProjectionVerificationResult final {
public:
    [[nodiscard]] static ProjectionVerificationResult success(
        CanonicalIngressProjection canonical);
    [[nodiscard]] static ProjectionVerificationResult failure(
        ProjectionVerificationError error);

    [[nodiscard]] bool has_value() const noexcept { return value_.has_value(); }
    [[nodiscard]] explicit operator bool() const noexcept { return has_value(); }
    [[nodiscard]] const VerifiedIngressProjection& value() const;
    [[nodiscard]] VerifiedIngressProjection take_value();
    [[nodiscard]] const ProjectionVerificationError& error() const;

private:
    std::optional<VerifiedIngressProjection> value_;
    std::optional<ProjectionVerificationError> error_;
};

class CanonicalProjectionVerifier final {
public:
    [[nodiscard]] static ProjectionVerificationResult verify(
        const CanonicalIngressProjection& canonical,
        const PersistedIngressProjection& persisted);
};

[[nodiscard]] std::string_view projection_field_name(ProjectionField field) noexcept;


}  // namespace anonsync::persistence
