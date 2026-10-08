#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync::persistence {

inline constexpr std::string_view kSqliteSnapshotManifestV2Format =
    "anonsync-sqlite-snapshot-manifest-v2";
inline constexpr std::string_view kSqliteSnapshotManifestV2PayloadFormat =
    "anonsync-sqlite-snapshot-manifest-payload-v2";
inline constexpr std::string_view kSqliteSnapshotTrustProfileV3Format =
    "anonsync-sqlite-snapshot-trust-profile-v3";

inline constexpr std::size_t kSqliteSnapshotManifestMaximumJsonBytes =
    64 * 1024;
inline constexpr std::size_t kSqliteSnapshotManifestMaximumTrustProfileBytes =
    256 * 1024;
inline constexpr std::size_t kSqliteSnapshotManifestMaximumSigningInputBytes =
    16 * 1024;
inline constexpr std::size_t kSqliteSnapshotManifestMaximumRevisionBytes = 256;
inline constexpr std::size_t kSqliteSnapshotManifestMaximumSubjectBytes = 512;
inline constexpr std::size_t kSqliteSnapshotManifestMaximumDurabilityCeilingBytes =
    2048;
inline constexpr std::size_t kSqliteSnapshotManifestMaximumSignerKidBytes = 256;
inline constexpr std::size_t kSqliteSnapshotManifestMaximumSignatureBytes = 8192;
inline constexpr std::int64_t kSqliteSnapshotManifestMaximumExactJsonInteger =
    9007199254740991LL;

// The exact owning representation of all sixteen v2 signature-covered fields.
// The payload format marker is checked separately because the legacy signing
// domain does not cover that JSON member.
struct SqliteSnapshotManifestPayloadFields final {
    std::string manifest_revision_id;
    std::string parent_revision;
    std::string manifest_issued_at;
    std::string snapshot_sha256;
    std::string backend_name;
    std::string backend_profile_backend_name;
    std::int64_t schema_version{};
    std::string entry_material_version;
    std::string hash_algorithm;
    std::string commit_protocol;
    std::int64_t line_count{};
    std::string head_hash;
    std::string expected_revision;
    std::string source_controls_revision;
    std::string manifest_subject;
    std::string durability_ceiling;
};

// V2 wire compatibility is retained, but delimiter-bearing controls are
// rejected before the legacy newline-delimited signing bytes are accepted.
// This turns a previously ambiguous tuple encoding into an injective subset
// without invalidating ordinary existing v2 manifests.
class FrozenSqliteSnapshotManifestV2Payload final {
public:
    [[nodiscard]] static FrozenSqliteSnapshotManifestV2Payload freeze_or_throw(
        SqliteSnapshotManifestPayloadFields fields);

    [[nodiscard]] const SqliteSnapshotManifestPayloadFields& fields() const noexcept {
        return fields_;
    }

private:
    explicit FrozenSqliteSnapshotManifestV2Payload(
        SqliteSnapshotManifestPayloadFields fields)
        : fields_(std::move(fields)) {}

    SqliteSnapshotManifestPayloadFields fields_;
};

[[nodiscard]] std::string sqlite_snapshot_manifest_v2_signing_input_or_throw(
    const FrozenSqliteSnapshotManifestV2Payload& payload);

struct SqliteSnapshotManifestSignatureFields final {
    std::string kid;
    std::string signature_b64url;
};

class SqliteSnapshotManifestV2Publication final {
public:
    [[nodiscard]] static SqliteSnapshotManifestV2Publication bind_or_throw(
        FrozenSqliteSnapshotManifestV2Payload payload,
        std::string payload_signing_input_sha256,
        SqliteSnapshotManifestSignatureFields signature);

    [[nodiscard]] const FrozenSqliteSnapshotManifestV2Payload& payload() const noexcept {
        return payload_;
    }
    [[nodiscard]] const std::string& payload_signing_input_sha256() const noexcept {
        return payload_signing_input_sha256_;
    }
    [[nodiscard]] const SqliteSnapshotManifestSignatureFields& signature() const noexcept {
        return signature_;
    }

private:
    SqliteSnapshotManifestV2Publication(
        FrozenSqliteSnapshotManifestV2Payload payload,
        std::string payload_signing_input_sha256,
        SqliteSnapshotManifestSignatureFields signature)
        : payload_(std::move(payload)),
          payload_signing_input_sha256_(
              std::move(payload_signing_input_sha256)),
          signature_(std::move(signature)) {}

    FrozenSqliteSnapshotManifestV2Payload payload_;
    std::string payload_signing_input_sha256_;
    SqliteSnapshotManifestSignatureFields signature_;
};

[[nodiscard]] std::string encode_sqlite_snapshot_manifest_v2_json_or_throw(
    const SqliteSnapshotManifestV2Publication& publication);

}  // namespace anonsync::persistence
