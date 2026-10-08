#include "canonical_projection_verifier.hpp"
#include "sqlite_projection_decoder.hpp"

#include <sqlite3.h>

#include <cstdint>
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

void require_sqlite(int rc, sqlite3* db, const std::string& operation) {
    if (rc != SQLITE_OK && rc != SQLITE_ROW && rc != SQLITE_DONE) {
        fail(operation + ": " + (db != nullptr ? sqlite3_errmsg(db) : "SQLite error"));
    }
}

struct Database final {
    sqlite3* db = nullptr;

    Database() {
        require_sqlite(sqlite3_open(":memory:", &db), db, "open in-memory database");
    }
    ~Database() {
        if (db != nullptr) sqlite3_close_v2(db);
    }
    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;
};

struct Statement final {
    sqlite3_stmt* stmt = nullptr;

    Statement() = default;
    ~Statement() {
        if (stmt != nullptr) sqlite3_finalize(stmt);
    }
    Statement(const Statement&) = delete;
    Statement& operator=(const Statement&) = delete;
    Statement(Statement&& other) noexcept : stmt(other.stmt) {
        other.stmt = nullptr;
    }
    Statement& operator=(Statement&& other) noexcept {
        if (this != &other) {
            if (stmt != nullptr) sqlite3_finalize(stmt);
            stmt = other.stmt;
            other.stmt = nullptr;
        }
        return *this;
    }
};

struct Expressions final {
    std::string transport_envelope_idempotency_key =
        "'sync-peer-transport-envelope:v1:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'";
    std::string transport_instance_id = "'transport-a'";
    std::string transport_key_id = "'transport-key-a'";
    std::string peer_id = "'peer-sensitive-marker'";
    std::string peer_session_id = "'peer-session-a'";
    std::string peer_response_batch_idempotency_key = "'peer-response-a'";
    std::string logical_path = "'private/sensitive-marker.bin'";
    std::string payload_digest_sha256 =
        "'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'";
    std::string response_count = "2";
    std::string total_bytes = "16";
    std::string issued_at_epoch = "100";
    std::string expires_at_epoch = "200";
};

ProjectionColumnMap columns() {
    return {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
}

Statement prepare_row(Database& database, const Expressions& expressions = {}) {
    const std::vector<std::string> ordered{
        expressions.transport_envelope_idempotency_key,
        expressions.transport_instance_id,
        expressions.transport_key_id,
        expressions.peer_id,
        expressions.peer_session_id,
        expressions.peer_response_batch_idempotency_key,
        expressions.logical_path,
        expressions.payload_digest_sha256,
        expressions.response_count,
        expressions.total_bytes,
        expressions.issued_at_epoch,
        expressions.expires_at_epoch,
    };
    std::string sql = "SELECT ";
    for (std::size_t i = 0; i < ordered.size(); ++i) {
        if (i != 0) sql += ',';
        sql += ordered[i];
    }
    Statement statement;
    require_sqlite(sqlite3_prepare_v2(
                       database.db, sql.c_str(), -1, &statement.stmt, nullptr),
                   database.db,
                   "prepare projection row");
    return statement;
}

Statement select_row(Database& database, const Expressions& expressions = {}) {
    Statement statement = prepare_row(database, expressions);
    if (sqlite3_step(statement.stmt) != SQLITE_ROW) {
        fail("projection SELECT did not return one row");
    }
    return statement;
}

CanonicalIngressProjection canonical_projection() {
    CanonicalIngressProjection out;
    out.transport_envelope_idempotency_key =
        "sync-peer-transport-envelope:v1:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    out.transport_instance_id = "transport-a";
    out.transport_key_id = "transport-key-a";
    out.peer_id = "peer-sensitive-marker";
    out.peer_session_id = "peer-session-a";
    out.peer_response_batch_idempotency_key = "peer-response-a";
    out.logical_path = "private/sensitive-marker.bin";
    out.payload_digest_sha256 =
        "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd";
    out.response_count = 2;
    out.total_bytes = 16;
    out.issued_at_epoch = 100;
    out.expires_at_epoch = 200;
    return out;
}

void require_decode_failure(const ProjectionDecodeResult& decoded,
                            ProjectionField field,
                            ProjectionDecodeFailure failure,
                            const std::string& context,
                            std::uint64_t& checks) {
    require(!decoded, context + " was accepted", checks);
    require(decoded.error().field == field,
            context + " was attributed to the wrong field",
            checks);
    require(decoded.error().failure == failure,
            context + " was classified incorrectly",
            checks);
    const std::string summary = decoded.error().safe_summary();
    require(summary.find(std::string(projection_field_name(field))) !=
                std::string::npos,
            context + " summary omitted the field",
            checks);
    require(summary.find("sensitive-marker") == std::string::npos &&
                summary.find("private/") == std::string::npos,
            context + " summary leaked persisted content",
            checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        Database database;
        {
            Statement statement = select_row(database);
            const ProjectionDecodeResult decoded =
                SqliteProjectionDecoder::decode(statement.stmt, columns());
            require(decoded.has_value(), "valid projection row was rejected", checks);
            require(decoded.value().logical_path ==
                        canonical_projection().logical_path,
                    "text projection was not decoded byte-for-byte",
                    checks);
            require(decoded.value().total_bytes == 16,
                    "integer projection was not decoded exactly",
                    checks);
            require(CanonicalProjectionVerifier::verify(
                        canonical_projection(), decoded.value()).has_value(),
                    "decoded matching row did not verify",
                    checks);
        }
        {
            Expressions expressions;
            expressions.peer_id = "''";
            Statement statement = select_row(database, expressions);
            const ProjectionDecodeResult decoded =
                SqliteProjectionDecoder::decode(statement.stmt, columns());
            require(decoded.has_value(),
                    "empty SQLite TEXT was confused with allocation failure",
                    checks);
            require(decoded.value().peer_id.has_value() &&
                        decoded.value().peer_id->empty(),
                    "empty SQLite TEXT was not preserved exactly",
                    checks);
        }
        {
            Statement statement = prepare_row(database);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::transport_envelope_idempotency_key,
                ProjectionDecodeFailure::statement_not_positioned,
                "prepared but unstepped statement",
                checks);
        }
        {
            Statement statement = select_row(database);
            require(sqlite3_step(statement.stmt) == SQLITE_DONE,
                    "projection statement did not reach SQLITE_DONE",
                    checks);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::transport_envelope_idempotency_key,
                ProjectionDecodeFailure::statement_not_positioned,
                "exhausted statement",
                checks);
        }
        {
            Statement statement = select_row(database);
            require(sqlite3_reset(statement.stmt) == SQLITE_OK,
                    "projection statement reset failed",
                    checks);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::transport_envelope_idempotency_key,
                ProjectionDecodeFailure::statement_not_positioned,
                "reset statement",
                checks);
        }
        {
            // An incorrect query map could otherwise reuse transport_instance_id
            // as the evidence for transport_key_id. When the canonical values
            // happen to be equal, the omitted forged key column would verify.
            Expressions expressions;
            expressions.transport_instance_id = "'shared-id'";
            expressions.transport_key_id = "'forged-key-not-selected'";
            Statement statement = select_row(database, expressions);
            ProjectionColumnMap aliased_columns = columns();
            aliased_columns.transport_key_id =
                aliased_columns.transport_instance_id;
            require_decode_failure(
                SqliteProjectionDecoder::decode(
                    statement.stmt, aliased_columns),
                ProjectionField::transport_key_id,
                ProjectionDecodeFailure::duplicate_column_index,
                "duplicate projection column alias",
                checks);
        }
        {
            Expressions expressions;
            expressions.peer_id = "NULL";
            Statement statement = select_row(database, expressions);
            const ProjectionDecodeResult decoded =
                SqliteProjectionDecoder::decode(statement.stmt, columns());
            require(decoded.has_value(), "NULL was not preserved as optional evidence", checks);
            require(!decoded.value().peer_id.has_value(),
                    "NULL text projection became an ambient default",
                    checks);
            const ProjectionVerificationResult verified =
                CanonicalProjectionVerifier::verify(
                    canonical_projection(), decoded.value());
            require(!verified &&
                        verified.error().contains(ProjectionField::peer_id),
                    "missing peer evidence was not rejected by verification",
                    checks);
        }
        {
            Expressions expressions;
            expressions.peer_id = "x'70656572'";
            Statement statement = select_row(database, expressions);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::peer_id,
                ProjectionDecodeFailure::wrong_storage_class,
                "BLOB in text projection",
                checks);
        }
        {
            Expressions expressions;
            expressions.total_bytes = "'16'";
            Statement statement = select_row(database, expressions);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::total_bytes,
                ProjectionDecodeFailure::wrong_storage_class,
                "TEXT in integer projection",
                checks);
        }
        {
            Expressions expressions;
            expressions.total_bytes = "-1";
            Statement statement = select_row(database, expressions);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::total_bytes,
                ProjectionDecodeFailure::negative_unsigned,
                "negative unsigned projection",
                checks);
        }
        {
            Expressions expressions;
            expressions.payload_digest_sha256 =
                "'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD'";
            Statement statement = select_row(database, expressions);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::payload_digest_sha256,
                ProjectionDecodeFailure::invalid_digest_encoding,
                "uppercase SHA-256 projection",
                checks);
        }
        {
            Expressions expressions;
            expressions.payload_digest_sha256 = "'dddd'";
            Statement statement = select_row(database, expressions);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, columns()),
                ProjectionField::payload_digest_sha256,
                ProjectionDecodeFailure::invalid_digest_encoding,
                "short SHA-256 projection",
                checks);
        }
        {
            Expressions expressions;
            expressions.logical_path = "CAST(x'707269766174652F780079' AS TEXT)";
            Statement statement = select_row(database, expressions);
            const ProjectionDecodeResult decoded =
                SqliteProjectionDecoder::decode(statement.stmt, columns());
            require(decoded.has_value(),
                    "embedded-NUL SQLite TEXT could not be decoded byte-for-byte",
                    checks);
            require(decoded.value().logical_path->size() == 11,
                    "embedded-NUL SQLite TEXT was truncated",
                    checks);
            const ProjectionVerificationResult verified =
                CanonicalProjectionVerifier::verify(
                    canonical_projection(), decoded.value());
            require(!verified &&
                        verified.error().contains(ProjectionField::logical_path),
                    "embedded-NUL path contradiction was accepted",
                    checks);
        }
        {
            Statement statement = select_row(database);
            ProjectionColumnMap bad_columns = columns();
            bad_columns.logical_path = sqlite3_column_count(statement.stmt);
            require_decode_failure(
                SqliteProjectionDecoder::decode(statement.stmt, bad_columns),
                ProjectionField::logical_path,
                ProjectionDecodeFailure::invalid_column_index,
                "out-of-range column map",
                checks);
        }
        {
            require_decode_failure(
                SqliteProjectionDecoder::decode(nullptr, columns()),
                ProjectionField::transport_envelope_idempotency_key,
                ProjectionDecodeFailure::invalid_statement,
                "null SQLite statement",
                checks);
        }

        std::cout << "sqlite projection decoder: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sqlite projection decoder: " << error.what() << '\n';
        return 1;
    }
}
