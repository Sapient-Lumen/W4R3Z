#include "canonical_projection_verifier.hpp"
#include "sqlite_projection_decoder.hpp"
#include <sqlite3.h>
#include <iostream>
#include <string>

using namespace anonsync::persistence;

int main() {
    sqlite3* db = nullptr;
    if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 2;
    sqlite3_stmt* stmt = nullptr;
    const char* sql =
        "SELECT 'env','shared','forged-key','peer','session','batch','path',"
        "'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd',"
        "1,2,3,4;";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return 3;

    ProjectionColumnMap columns{0,1,2,3,4,5,6,7,8,9,10,11};
    auto unstepped = SqliteProjectionDecoder::decode(stmt, columns);
    std::cout << "unstepped_has_value=" << (unstepped.has_value() ? "true" : "false");
    if (!unstepped) std::cout << " error=" << unstepped.error().safe_summary();
    std::cout << '\n';

    if (sqlite3_step(stmt) != SQLITE_ROW) return 4;
    columns.transport_key_id = columns.transport_instance_id;
    auto aliased = SqliteProjectionDecoder::decode(stmt, columns);
    std::cout << "duplicate_map_decode_has_value=" << (aliased.has_value() ? "true" : "false");
    if (!aliased) std::cout << " error=" << aliased.error().safe_summary();
    std::cout << '\n';

    CanonicalIngressProjection canonical;
    canonical.transport_envelope_idempotency_key = "env";
    canonical.transport_instance_id = "shared";
    canonical.transport_key_id = "shared";
    canonical.peer_id = "peer";
    canonical.peer_session_id = "session";
    canonical.peer_response_batch_idempotency_key = "batch";
    canonical.logical_path = "path";
    canonical.payload_digest_sha256 =
        "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd";
    canonical.response_count = 1;
    canonical.total_bytes = 2;
    canonical.issued_at_epoch = 3;
    canonical.expires_at_epoch = 4;
    if (aliased) {
        auto verified = CanonicalProjectionVerifier::verify(canonical, aliased.value());
        std::cout << "forged_omitted_column_verified=" << (verified.has_value() ? "true" : "false");
        if (!verified) std::cout << " error=" << verified.error().safe_summary();
        std::cout << '\n';
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return 0;
}
