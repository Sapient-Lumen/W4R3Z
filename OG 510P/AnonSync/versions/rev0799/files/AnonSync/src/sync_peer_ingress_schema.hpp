#pragma once

#include <cstdint>
#include <string>

#include "sync_sqlite_connection_authority.hpp"

struct sqlite3;

namespace anonsync {

inline constexpr std::uint32_t kPeerTransportIngressSqliteApplicationId =
    0x414e5359U;  // "ANSY"
inline constexpr std::uint32_t kPeerTransportIngressSqliteUserVersion = 1U;

// A connection-scoped statement that the reserved peer-ingress schema was
// exact at one SQLite schema generation.  The capability also represents an
// intentionally absent schema for read-only probes of unrelated databases.
class PeerTransportIngressSchemaAttestation final {
private:
    sqlite3* db_ = nullptr;
    std::uint64_t schema_version_ = 0;
    std::string manifest_sha256_;
    SyncSqliteConnectionAuthorityProof connection_authority_;
    bool schema_present_ = false;
    bool legacy_unmarked_ = false;

    PeerTransportIngressSchemaAttestation(sqlite3* db,
                                          std::uint64_t schema_version,
                                          std::string manifest_sha256,
                                          SyncSqliteConnectionAuthorityProof connection_authority,
                                          bool schema_present,
                                          bool legacy_unmarked);

    friend PeerTransportIngressSchemaAttestation
    initialize_or_inspect_peer_transport_ingress_schema_or_throw(
        sqlite3* db,
        bool writable,
        bool allow_absent,
        const std::string& label);
    friend SyncSqliteConnectionAuthorityLease
    verify_peer_transport_ingress_schema_attestation_current_or_throw(
        sqlite3* db,
        const PeerTransportIngressSchemaAttestation& attestation,
        const std::string& label);

public:
    PeerTransportIngressSchemaAttestation() = default;

    [[nodiscard]] bool authorizes(sqlite3* db) const noexcept;
    [[nodiscard]] bool schema_present() const noexcept;
    [[nodiscard]] bool legacy_unmarked() const noexcept;
    [[nodiscard]] std::uint64_t schema_version() const noexcept;
    [[nodiscard]] std::uint64_t authorizer_generation() const noexcept;
    [[nodiscard]] const std::string& manifest_sha256() const noexcept;
};

// Write-capable callers atomically create an empty database or migrate an
// exact unmarked legacy schema to the application_id/user_version pair.  They
// never fill in a partial schema and never claim a nonempty foreign database.
// Read-only callers may request allow_absent for no-op/status semantics.
[[nodiscard]] PeerTransportIngressSchemaAttestation
initialize_or_inspect_peer_transport_ingress_schema_or_throw(
    sqlite3* db,
    bool writable,
    bool allow_absent,
    const std::string& label);

// Run only after a read or BEGIN IMMEDIATE snapshot has been established.
// This closes the race between connection-open attestation and statement use.
[[nodiscard]] SyncSqliteConnectionAuthorityLease
verify_peer_transport_ingress_schema_attestation_current_or_throw(
    sqlite3* db,
    const PeerTransportIngressSchemaAttestation& attestation,
    const std::string& label);

// Exposed for release/audit tooling and focused tests.  No persistent values
// are included; the hash commits only to the reviewed schema object manifest.
[[nodiscard]] std::string expected_peer_transport_ingress_schema_manifest_sha256();

}  // namespace anonsync
