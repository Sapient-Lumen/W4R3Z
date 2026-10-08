#pragma once

#include <cstdint>
#include <string>

#include "sync_sqlite_support.hpp"

namespace anonsync {

struct PeerTransportIngressWireLimits;

struct PeerTransportIngressStoredPayload {
    bool found = false;
    std::uint64_t codec_version = 0;
    std::string canonical_frame_sha256;
    std::string payload_digest;
    std::uint64_t canonical_frame_bytes = 0;
    std::string canonical_frame;
    std::uint64_t stored_at_epoch = 0;
};

enum class PeerTransportIngressPayloadStoreOutcome {
    Inserted,
    AlreadyPresent
};

// Capability proving that the exact payload-store schema was verified on this
// SQLite handle. Scan-oriented loaders require it so callers cannot express
// "already checked" as an ambient boolean or naming convention.
class VerifiedPeerTransportIngressPayloadStoreSchema final {
private:
    sqlite3* db_ = nullptr;
    SyncSqliteTransactionAuthority snapshot_authority_;

    VerifiedPeerTransportIngressPayloadStoreSchema(
        sqlite3* db,
        const SyncSqliteTransaction& transaction) noexcept
        : db_(db), snapshot_authority_(transaction.authority()) {}

    friend VerifiedPeerTransportIngressPayloadStoreSchema
    verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw(
        sqlite3* db,
        const SyncSqliteTransaction& transaction,
        const std::string& label);

public:
    VerifiedPeerTransportIngressPayloadStoreSchema(
        const VerifiedPeerTransportIngressPayloadStoreSchema&) = default;
    VerifiedPeerTransportIngressPayloadStoreSchema& operator=(
        const VerifiedPeerTransportIngressPayloadStoreSchema&) = default;

    [[nodiscard]] bool authorizes(sqlite3* db) const noexcept {
        return db_ != nullptr && db_ == db &&
               snapshot_authority_.authorizes_snapshot(db);
    }
};

void ensure_peer_transport_ingress_payload_store_schema_or_throw(
    sqlite3* db,
    const std::string& label);

// Fail closed on a look-alike or weakened existing table. This verifier is
// read-only and is also applied before loading persistent BLOB evidence.
void verify_peer_transport_ingress_payload_store_schema_or_throw(
    sqlite3* db,
    const std::string& label);

[[nodiscard]] VerifiedPeerTransportIngressPayloadStoreSchema
verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& label);

PeerTransportIngressStoredPayload load_peer_transport_ingress_stored_payload_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    std::uint64_t max_frame_bytes,
    const std::string& label);

// The caller must have verified the exact payload-store schema inside the same
// live SQLite snapshot before using this scan-oriented variant. The capability
// is revoked by commit, rollback, or guard destruction, so a verified schema
// cannot be carried into a later snapshot on the same connection. It avoids
// repeating PRAGMA/schema work for every candidate while preserving row/BLOB checks.
PeerTransportIngressStoredPayload
load_peer_transport_ingress_stored_payload_from_verified_schema_or_throw(
    sqlite3* db,
    const VerifiedPeerTransportIngressPayloadStoreSchema& verified_schema,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    std::uint64_t max_frame_bytes,
    const std::string& label);

// Requires an exact live write-transaction guard. The queue parent and payload
// evidence therefore cannot be accidentally committed in separate autocommit
// transactions. Existing evidence is accepted only when every byte and digest matches.
PeerTransportIngressPayloadStoreOutcome store_or_verify_peer_transport_ingress_payload_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    const std::string& canonical_frame,
    const std::string& payload_digest,
    const PeerTransportIngressWireLimits& wire_limits,
    std::uint64_t stored_at_epoch,
    const std::string& label);

}  // namespace anonsync
