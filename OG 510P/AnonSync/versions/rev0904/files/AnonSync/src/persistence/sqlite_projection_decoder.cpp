#include "sqlite_projection_decoder.hpp"
#include "sqlite_exact_value.hpp"

#include <sqlite3.h>

#include <array>
#include <cstddef>
#include <cstdint>
#include <new>
#include <stdexcept>
#include <utility>

namespace anonsync::persistence {
namespace {

struct MappedProjectionColumn final {
    ProjectionField field;
    int index;
};

constexpr std::size_t kProjectionColumnCount = 12;

std::array<MappedProjectionColumn, kProjectionColumnCount> mapped_columns(
    const ProjectionColumnMap& columns) noexcept {
    return {{
        {ProjectionField::transport_envelope_idempotency_key,
         columns.transport_envelope_idempotency_key},
        {ProjectionField::transport_instance_id, columns.transport_instance_id},
        {ProjectionField::transport_key_id, columns.transport_key_id},
        {ProjectionField::peer_id, columns.peer_id},
        {ProjectionField::peer_session_id, columns.peer_session_id},
        {ProjectionField::peer_response_batch_idempotency_key,
         columns.peer_response_batch_idempotency_key},
        {ProjectionField::logical_path, columns.logical_path},
        {ProjectionField::payload_digest_sha256, columns.payload_digest_sha256},
        {ProjectionField::response_count, columns.response_count},
        {ProjectionField::total_bytes, columns.total_bytes},
        {ProjectionField::issued_at_epoch, columns.issued_at_epoch},
        {ProjectionField::expires_at_epoch, columns.expires_at_epoch},
    }};
}

std::optional<ProjectionDecodeError> validate_current_projection_row(
    sqlite3_stmt* statement,
    const ProjectionColumnMap& columns) noexcept {
    if (statement == nullptr) {
        return ProjectionDecodeError{
            ProjectionField::transport_envelope_idempotency_key,
            ProjectionDecodeFailure::invalid_statement};
    }

    const int column_count = sqlite3_column_count(statement);
    // sqlite3_column_* is defined only while the most recent step returned
    // SQLITE_ROW. sqlite3_data_count() is the public observation that a current
    // row is available. For a projection SELECT it must equal column_count.
    if (column_count <= 0 || sqlite3_data_count(statement) != column_count) {
        return ProjectionDecodeError{
            ProjectionField::transport_envelope_idempotency_key,
            ProjectionDecodeFailure::statement_not_positioned};
    }

    const auto mapped = mapped_columns(columns);
    for (std::size_t current = 0; current < mapped.size(); ++current) {
        if (mapped[current].index < 0 || mapped[current].index >= column_count) {
            return ProjectionDecodeError{
                mapped[current].field,
                ProjectionDecodeFailure::invalid_column_index};
        }
        for (std::size_t prior = 0; prior < current; ++prior) {
            if (mapped[current].index == mapped[prior].index) {
                // One stored value is not independent evidence for two fields,
                // even when the canonical values happen to be equal.
                return ProjectionDecodeError{
                    mapped[current].field,
                    ProjectionDecodeFailure::duplicate_column_index};
            }
        }
    }
    return std::nullopt;
}

ProjectionDecodeFailure projection_failure_from_exact(
    SqliteExactValueFailure failure) noexcept {
    switch (failure) {
        case SqliteExactValueFailure::invalid_statement:
            return ProjectionDecodeFailure::invalid_statement;
        case SqliteExactValueFailure::statement_not_positioned:
            return ProjectionDecodeFailure::statement_not_positioned;
        case SqliteExactValueFailure::invalid_column_index:
            return ProjectionDecodeFailure::invalid_column_index;
        case SqliteExactValueFailure::wrong_storage_class:
            return ProjectionDecodeFailure::wrong_storage_class;
        case SqliteExactValueFailure::negative_unsigned:
            return ProjectionDecodeFailure::negative_unsigned;
        case SqliteExactValueFailure::allocation_failure:
            return ProjectionDecodeFailure::allocation_failure;
        case SqliteExactValueFailure::null_value:
            // Optional exact readers preserve NULL and never emit this failure.
            return ProjectionDecodeFailure::wrong_storage_class;
        case SqliteExactValueFailure::byte_limit_exceeded:
            // This decoder does not impose a byte limit, so this is unreachable.
            return ProjectionDecodeFailure::allocation_failure;
    }
    return ProjectionDecodeFailure::allocation_failure;
}

std::optional<ProjectionDecodeError> read_text(
    sqlite3_stmt* statement,
    int index,
    ProjectionField field,
    std::optional<std::string>& output) noexcept {
    try {
        output = sqlite_exact_optional_text_or_throw(
            statement, index, projection_field_name(field));
        return std::nullopt;
    } catch (const SqliteExactValueException& error) {
        return ProjectionDecodeError{
            field, projection_failure_from_exact(error.failure())};
    } catch (...) {
        return ProjectionDecodeError{
            field, ProjectionDecodeFailure::allocation_failure};
    }
}

bool is_lowercase_sha256_hex_text(const std::string& value) noexcept {
    if (value.size() != 64) return false;
    for (const char raw : value) {
        const auto c = static_cast<unsigned char>(raw);
        const bool decimal = c >= static_cast<unsigned char>('0') &&
                             c <= static_cast<unsigned char>('9');
        const bool lower_hex = c >= static_cast<unsigned char>('a') &&
                               c <= static_cast<unsigned char>('f');
        if (!decimal && !lower_hex) return false;
    }
    return true;
}

std::optional<ProjectionDecodeError> read_sha256_text(
    sqlite3_stmt* statement,
    int index,
    ProjectionField field,
    std::optional<std::string>& output) noexcept {
    if (auto error = read_text(statement, index, field, output)) return error;
    if (output && !is_lowercase_sha256_hex_text(*output)) {
        return ProjectionDecodeError{
            field, ProjectionDecodeFailure::invalid_digest_encoding};
    }
    return std::nullopt;
}

std::optional<ProjectionDecodeError> read_u64(
    sqlite3_stmt* statement,
    int index,
    ProjectionField field,
    std::optional<std::uint64_t>& output) noexcept {
    try {
        output = sqlite_exact_optional_u64_or_throw(
            statement, index, projection_field_name(field));
        return std::nullopt;
    } catch (const SqliteExactValueException& error) {
        return ProjectionDecodeError{
            field, projection_failure_from_exact(error.failure())};
    } catch (...) {
        return ProjectionDecodeError{
            field, ProjectionDecodeFailure::allocation_failure};
    }
}

std::string_view failure_name(ProjectionDecodeFailure failure) noexcept {
    switch (failure) {
        case ProjectionDecodeFailure::invalid_statement: return "invalid_statement";
        case ProjectionDecodeFailure::statement_not_positioned:
            return "statement_not_positioned";
        case ProjectionDecodeFailure::invalid_column_index: return "invalid_column_index";
        case ProjectionDecodeFailure::duplicate_column_index:
            return "duplicate_column_index";
        case ProjectionDecodeFailure::wrong_storage_class: return "wrong_storage_class";
        case ProjectionDecodeFailure::negative_unsigned: return "negative_unsigned";
        case ProjectionDecodeFailure::invalid_digest_encoding: return "invalid_digest_encoding";
        case ProjectionDecodeFailure::allocation_failure: return "allocation_failure";
    }
    return "unknown";
}

}  // namespace

std::string ProjectionDecodeError::safe_summary() const {
    return std::string("sqlite_projection_decode[") +
           std::string(projection_field_name(field)) + ':' +
           std::string(failure_name(failure)) + ']';
}

ProjectionDecodeResult ProjectionDecodeResult::success(
    PersistedIngressProjection projection) {
    ProjectionDecodeResult result;
    result.value_.emplace(std::move(projection));
    return result;
}

ProjectionDecodeResult ProjectionDecodeResult::failure(
    ProjectionDecodeError error) {
    ProjectionDecodeResult result;
    result.error_.emplace(std::move(error));
    return result;
}

const PersistedIngressProjection& ProjectionDecodeResult::value() const {
    if (!value_) throw std::logic_error("projection decode result has no value");
    return *value_;
}

PersistedIngressProjection ProjectionDecodeResult::take_value() {
    if (!value_) throw std::logic_error("projection decode result has no value");
    return std::move(*value_);
}

const ProjectionDecodeError& ProjectionDecodeResult::error() const {
    if (!error_) throw std::logic_error("projection decode result has no error");
    return *error_;
}

ProjectionDecodeResult SqliteProjectionDecoder::decode(
    sqlite3_stmt* statement,
    const ProjectionColumnMap& columns) noexcept {
    try {
        if (auto error = validate_current_projection_row(statement, columns)) {
            return ProjectionDecodeResult::failure(*error);
        }
        PersistedIngressProjection projection;
        if (auto error = read_text(statement,
                                   columns.transport_envelope_idempotency_key,
                                   ProjectionField::transport_envelope_idempotency_key,
                                   projection.transport_envelope_idempotency_key)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_text(statement,
                                   columns.transport_instance_id,
                                   ProjectionField::transport_instance_id,
                                   projection.transport_instance_id)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_text(statement,
                                   columns.transport_key_id,
                                   ProjectionField::transport_key_id,
                                   projection.transport_key_id)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_text(statement,
                                   columns.peer_id,
                                   ProjectionField::peer_id,
                                   projection.peer_id)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_text(statement,
                                   columns.peer_session_id,
                                   ProjectionField::peer_session_id,
                                   projection.peer_session_id)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_text(statement,
                                   columns.peer_response_batch_idempotency_key,
                                   ProjectionField::peer_response_batch_idempotency_key,
                                   projection.peer_response_batch_idempotency_key)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_text(statement,
                                   columns.logical_path,
                                   ProjectionField::logical_path,
                                   projection.logical_path)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_sha256_text(statement,
                                          columns.payload_digest_sha256,
                                          ProjectionField::payload_digest_sha256,
                                          projection.payload_digest_sha256)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_u64(statement,
                                  columns.response_count,
                                  ProjectionField::response_count,
                                  projection.response_count)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_u64(statement,
                                  columns.total_bytes,
                                  ProjectionField::total_bytes,
                                  projection.total_bytes)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_u64(statement,
                                  columns.issued_at_epoch,
                                  ProjectionField::issued_at_epoch,
                                  projection.issued_at_epoch)) {
            return ProjectionDecodeResult::failure(*error);
        }
        if (auto error = read_u64(statement,
                                  columns.expires_at_epoch,
                                  ProjectionField::expires_at_epoch,
                                  projection.expires_at_epoch)) {
            return ProjectionDecodeResult::failure(*error);
        }
        return ProjectionDecodeResult::success(std::move(projection));
    } catch (const std::bad_alloc&) {
        return ProjectionDecodeResult::failure({
            ProjectionField::transport_envelope_idempotency_key,
            ProjectionDecodeFailure::allocation_failure});
    } catch (...) {
        // This noexcept boundary must not turn an unexpected decode exception
        // into process termination. The value-free fallback remains safe.
        return ProjectionDecodeResult::failure({
            ProjectionField::transport_envelope_idempotency_key,
            ProjectionDecodeFailure::allocation_failure});
    }
}

}  // namespace anonsync::persistence
