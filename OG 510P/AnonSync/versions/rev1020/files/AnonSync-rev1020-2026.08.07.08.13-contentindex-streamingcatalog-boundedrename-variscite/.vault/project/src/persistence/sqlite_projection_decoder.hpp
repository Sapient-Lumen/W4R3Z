#pragma once

#include "canonical_projection_verifier.hpp"

#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

struct sqlite3_stmt;

namespace anonsync::persistence {

// Column positions are explicit at each query boundary.  The decoder does not
// assume SELECT * ordering and checks every index before reading it.
struct ProjectionColumnMap final {
    int transport_envelope_idempotency_key{};
    int transport_instance_id{};
    int transport_key_id{};
    int peer_id{};
    int peer_session_id{};
    int peer_response_batch_idempotency_key{};
    int logical_path{};
    int payload_digest_sha256{};
    int response_count{};
    int total_bytes{};
    int issued_at_epoch{};
    int expires_at_epoch{};
};

enum class ProjectionDecodeFailure : std::uint8_t {
    invalid_statement,
    statement_not_positioned,
    invalid_column_index,
    duplicate_column_index,
    wrong_storage_class,
    negative_unsigned,
    invalid_digest_encoding,
    allocation_failure,
};

struct ProjectionDecodeError final {
    ProjectionField field{};
    ProjectionDecodeFailure failure{};

    // No observed values are retained: this is safe to place in an incident or
    // operator report without exposing peer/path/digest content.
    [[nodiscard]] std::string safe_summary() const;
};

class ProjectionDecodeResult final {
public:
    [[nodiscard]] static ProjectionDecodeResult success(
        PersistedIngressProjection projection);
    [[nodiscard]] static ProjectionDecodeResult failure(
        ProjectionDecodeError error);

    [[nodiscard]] bool has_value() const noexcept { return value_.has_value(); }
    [[nodiscard]] explicit operator bool() const noexcept { return has_value(); }
    [[nodiscard]] const PersistedIngressProjection& value() const;
    [[nodiscard]] PersistedIngressProjection take_value();
    [[nodiscard]] const ProjectionDecodeError& error() const;

private:
    std::optional<PersistedIngressProjection> value_;
    std::optional<ProjectionDecodeError> error_;
};

// Centralized SQLite conversion boundary. The statement must be positioned on
// a current SQLITE_ROW, and every projection field must own a distinct valid
// column. NULL remains std::nullopt so the canonical verifier can classify it
// as missing evidence. Non-NULL storage class and unsigned-range failures are
// rejected before C++ conversion.
class SqliteProjectionDecoder final {
public:
    [[nodiscard]] static ProjectionDecodeResult decode(
        sqlite3_stmt* statement,
        const ProjectionColumnMap& columns) noexcept;
};

}  // namespace anonsync::persistence
