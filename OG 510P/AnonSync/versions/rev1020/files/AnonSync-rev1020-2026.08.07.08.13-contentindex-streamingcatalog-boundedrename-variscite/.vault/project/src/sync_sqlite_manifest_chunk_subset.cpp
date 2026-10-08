#include "sync_sqlite_manifest_chunk_subset.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <limits>
#include <stdexcept>

#include <sqlite3.h>

namespace anonsync {
namespace {

void reset_and_clear_or_throw(sqlite3_stmt* stmt, const std::string& label) {
    const int reset_rc = sqlite3_reset(stmt);
    if (reset_rc != SQLITE_OK) {
        throw_sqlite_exception(
            sqlite3_db_handle(stmt), reset_rc, label + " reset");
    }
    const int clear_rc = sqlite3_clear_bindings(stmt);
    if (clear_rc != SQLITE_OK) {
        throw_sqlite_exception(
            sqlite3_db_handle(stmt), clear_rc, label + " clear bindings");
    }
}

void reset_and_clear_noexcept(sqlite3_stmt* stmt) noexcept {
    if (stmt == nullptr) return;
    (void)sqlite3_reset(stmt);
    (void)sqlite3_clear_bindings(stmt);
}

[[nodiscard]] std::uint64_t span_size_u64_or_throw(
    std::span<const SyncChunkRange> chunks,
    const std::string& label) {
    if (chunks.size() >
        static_cast<std::size_t>(std::numeric_limits<std::uint64_t>::max())) {
        throw std::runtime_error(label + " required chunk count exceeds uint64");
    }
    return static_cast<std::uint64_t>(chunks.size());
}

void validate_limits_or_throw(
    const SyncSqliteManifestChunkSubsetLimits& limits,
    const std::string& label) {
    if (limits.max_manifest_rows == 0 ||
        limits.max_required_rows == 0 ||
        limits.max_required_metadata_bytes == 0 ||
        limits.max_required_chunk_bytes == 0) {
        throw std::runtime_error(
            label + " all chunk subset limits must be positive");
    }
    if (limits.max_required_rows > limits.max_manifest_rows) {
        throw std::runtime_error(
            label + " required-row limit exceeds manifest-row limit");
    }
}

}  // namespace

std::uint64_t sync_manifest_chunk_subset_metadata_bytes_or_throw(
    std::uint64_t rows,
    const std::string& label) {
    if (rows > std::numeric_limits<std::uint64_t>::max() /
                   kSyncManifestChunkSubsetEvidenceBytesPerRow) {
        throw std::runtime_error(
            label + " required chunk metadata bytes overflow uint64");
    }
    return rows * kSyncManifestChunkSubsetEvidenceBytesPerRow;
}

SyncSqliteManifestChunkSubsetVerifier::
SyncSqliteManifestChunkSubsetVerifier(
    SyncSqliteDbHandleSlot& db,
    const std::string& label)
    : chunk_probe_(sqlite_prepare_or_throw(
          db,
          "SELECT chunk_offset, chunk_length, chunk_sha256, chunk_index "
          "FROM main.sync_session_manifest_chunks "
          "WHERE session_id=? AND role='source' AND path=? AND chunk_offset=? "
          "LIMIT 2;",
          label + " source manifest point probe prepare")) {}

SyncSqliteManifestChunkSubsetEvidence
SyncSqliteManifestChunkSubsetVerifier::verify_source_chunks_or_throw(
    const std::string& session_id,
    const std::string& normalized_path,
    std::uint64_t file_size_bytes,
    std::uint64_t expected_manifest_rows,
    std::span<const SyncChunkRange> required_chunks,
    const SyncSqliteManifestChunkSubsetLimits& limits,
    const std::string& label) {
    validate_limits_or_throw(limits, label);
    if (!sync_id_is_valid(session_id)) {
        throw std::runtime_error(label + " session id is invalid");
    }
    const SyncValidationResult path_result =
        validate_sync_relative_path(normalized_path);
    if (!path_result.ok) {
        throw std::runtime_error(
            label + " path is invalid: " + path_result.reason);
    }
    if (file_size_bytes == 0) {
        throw std::runtime_error(
            label + " nonempty required chunks need a nonempty file");
    }
    if (expected_manifest_rows == 0) {
        throw std::runtime_error(
            label + " expected manifest row count must be positive");
    }
    if (expected_manifest_rows > limits.max_manifest_rows) {
        throw std::runtime_error(
            label + " expected manifest row count exceeds its limit");
    }

    const std::uint64_t required_rows =
        span_size_u64_or_throw(required_chunks, label);
    if (required_rows == 0) {
        throw std::runtime_error(
            label + " required chunk subset must not be empty");
    }
    if (required_rows > limits.max_required_rows) {
        throw std::runtime_error(
            label + " required chunk count exceeds its limit");
    }
    if (required_rows > expected_manifest_rows) {
        throw std::runtime_error(
            label + " required chunk count exceeds expected manifest rows");
    }

    const std::uint64_t required_metadata_bytes =
        sync_manifest_chunk_subset_metadata_bytes_or_throw(
            required_rows, label);
    if (required_metadata_bytes > limits.max_required_metadata_bytes) {
        throw std::runtime_error(
            label + " required chunk metadata exceeds its limit");
    }

    // Complete semantic and arithmetic preflight before the first SQLite data
    // step. A malformed late element therefore cannot cause a prefix of the
    // caller's selected offsets to be observed from persistent state.
    std::uint64_t required_chunk_bytes = 0;
    std::uint64_t previous_end = 0;
    bool have_previous = false;
    constexpr std::uint64_t sqlite_i64_max =
        static_cast<std::uint64_t>(
            std::numeric_limits<sqlite3_int64>::max());
    for (const SyncChunkRange& required : required_chunks) {
        if (required.length == 0) {
            throw std::runtime_error(
                label + " required chunk length must be positive");
        }
        if (!is_lowercase_sha256_hex(required.sha256)) {
            throw std::runtime_error(
                label + " required chunk SHA-256 is invalid");
        }
        if (required.offset > sqlite_i64_max) {
            throw std::runtime_error(
                label + " required chunk offset exceeds SQLite integer range");
        }
        if (required.length >
            std::numeric_limits<std::uint64_t>::max() - required.offset) {
            throw std::runtime_error(
                label + " required chunk end overflows uint64");
        }
        if (required.length > sqlite_i64_max) {
            throw std::runtime_error(
                label + " required chunk length exceeds SQLite integer range");
        }
        const std::uint64_t end = required.offset + required.length;
        if (end > file_size_bytes) {
            throw std::runtime_error(
                label + " required chunk exceeds the file size");
        }
        if (have_previous && required.offset < previous_end) {
            throw std::runtime_error(
                label + " required chunks overlap or are out of order");
        }
        if (required.length >
            std::numeric_limits<std::uint64_t>::max() -
                required_chunk_bytes) {
            throw std::runtime_error(
                label + " required chunk bytes overflow uint64");
        }
        required_chunk_bytes += required.length;
        if (required_chunk_bytes > limits.max_required_chunk_bytes) {
            throw std::runtime_error(
                label + " required chunk bytes exceed their limit");
        }
        previous_end = end;
        have_previous = true;
    }

    SyncSqliteManifestChunkSubsetEvidence evidence;
    evidence.expected_manifest_rows = expected_manifest_rows;
    evidence.required_rows = required_rows;
    evidence.required_metadata_bytes = required_metadata_bytes;
    evidence.required_chunk_bytes = required_chunk_bytes;

    bool have_stored_index = false;
    std::uint64_t previous_stored_index = 0;
    for (const SyncChunkRange& required : required_chunks) {
        try {
            reset_and_clear_or_throw(
                chunk_probe_.stmt, label + " source manifest point probe");
            sqlite_bind_text_or_throw(
                chunk_probe_.stmt, 1, session_id,
                label + " source manifest session");
            sqlite_bind_text_or_throw(
                chunk_probe_.stmt, 2, normalized_path,
                label + " source manifest path");
            sqlite_bind_u64_or_throw(
                chunk_probe_.stmt, 3, required.offset,
                label + " source manifest offset");

            const int row_rc = sqlite3_step(chunk_probe_.stmt);
            if (row_rc == SQLITE_DONE) {
                throw std::runtime_error(
                    label +
                    " required chunk is absent from source manifest");
            }
            if (row_rc != SQLITE_ROW) {
                throw_sqlite_exception(
                    sqlite3_db_handle(chunk_probe_.stmt), row_rc,
                    label + " source manifest point probe");
            }

            const std::uint64_t stored_offset = sqlite_column_u64_or_throw(
                chunk_probe_.stmt, 0,
                label + " stored source chunk offset");
            const std::uint64_t stored_length = sqlite_column_u64_or_throw(
                chunk_probe_.stmt, 1,
                label + " stored source chunk length");
            const std::string stored_sha256 = sqlite_column_text_or_throw(
                chunk_probe_.stmt, 2, kSyncManifestSha256TextBytes,
                label + " stored source chunk SHA-256");
            const std::uint64_t stored_index = sqlite_column_u64_or_throw(
                chunk_probe_.stmt, 3,
                label + " stored source chunk index");

            if (stored_offset != required.offset ||
                stored_length != required.length ||
                stored_sha256 != required.sha256 ||
                !is_lowercase_sha256_hex(stored_sha256)) {
                throw std::runtime_error(
                    label +
                    " required chunk does not exactly match source manifest evidence");
            }
            if (stored_index >= expected_manifest_rows) {
                throw std::runtime_error(
                    label +
                    " stored chunk index exceeds expected manifest rows");
            }
            if (have_stored_index && stored_index <= previous_stored_index) {
                throw std::runtime_error(
                    label +
                    " stored chunk indices are not strictly increasing");
            }

            const int trailing_rc = sqlite3_step(chunk_probe_.stmt);
            if (trailing_rc == SQLITE_ROW) {
                throw std::runtime_error(
                    label + " source manifest point probe is not unique");
            }
            if (trailing_rc != SQLITE_DONE) {
                throw_sqlite_exception(
                    sqlite3_db_handle(chunk_probe_.stmt), trailing_rc,
                    label + " source manifest uniqueness probe");
            }

            if (!have_stored_index) {
                evidence.first_manifest_chunk_index = stored_index;
            }
            evidence.last_manifest_chunk_index = stored_index;
            previous_stored_index = stored_index;
            have_stored_index = true;
            reset_and_clear_or_throw(
                chunk_probe_.stmt, label + " source manifest point probe");
        } catch (...) {
            reset_and_clear_noexcept(chunk_probe_.stmt);
            throw;
        }
    }

    return evidence;
}

std::uint64_t
SyncSqliteManifestChunkSubsetVerifier::owner_generation() const noexcept {
    return chunk_probe_.owner_generation();
}

}  // namespace anonsync
