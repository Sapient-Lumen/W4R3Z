#pragma once

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {

// Explicit history inspection is independently bounded from retained causal
// evidence. The path and cursor are advisory browsing selectors only: every
// restore still re-proves current replica, payload, catalog, and rooted-path
// authority from scratch.
inline constexpr std::uint64_t
    kSyncReplicaHistoricalVersionDefaultMaximumEntries = 64U;
inline constexpr std::uint64_t
    kSyncReplicaHistoricalVersionMaximumEntries = 1024U;
inline constexpr std::uint64_t
    kSyncReplicaHistoricalVersionMaximumCanonicalPathBytes = 4096U;

// History inspection has two deliberately different authority contracts.
// ExactPayloadAvailability preserves the existing complete payload-namespace
// observation and can report whether each predecessor is immediately
// restorable. CausalMetadataOnly reads only the immutable causal model; it is
// suitable for cheap browsing but must report payload availability as unknown.
enum class SyncReplicaHistoricalVersionInspectionMode : std::uint8_t {
    ExactPayloadAvailability = 1U,
    CausalMetadataOnly = 2U,
};

[[nodiscard]] constexpr std::string_view
sync_replica_historical_version_inspection_mode_name(
    SyncReplicaHistoricalVersionInspectionMode mode) noexcept {
    switch (mode) {
        case SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability:
            return "exact_payload_availability";
        case SyncReplicaHistoricalVersionInspectionMode::CausalMetadataOnly:
            return "causal_metadata_only";
    }
    return "unknown";
}

[[nodiscard]] inline SyncReplicaHistoricalVersionInspectionMode
sync_replica_historical_version_inspection_mode_from_name_or_throw(
    std::string_view name,
    std::string_view label =
        "sync replica historical-version inspection mode") {
    if (name == "exact_payload_availability") {
        return SyncReplicaHistoricalVersionInspectionMode::
            ExactPayloadAvailability;
    }
    if (name == "causal_metadata_only") {
        return SyncReplicaHistoricalVersionInspectionMode::
            CausalMetadataOnly;
    }
    throw std::invalid_argument(
        std::string(label) + " is invalid");
}

// Exact immutable inputs that determine one historical-version page. Every
// cutpoint binds the complete active operation set. New exact-payload pages
// also bind the complete retained evidence set because rev0972 reachability
// accounts for inactive pending/quarantined file evidence. Every new page binds
// the exact local historical-version pin set because pin state is returned in
// entries and reachability. Exact pages finally bind the retained payload
// snapshot. Metadata-only pages intentionally carry neither evidence nor
// payload digests because they perform no payload-store observation and return
// no reachability classification. This is browse consistency only. Restore
// still re-proves every mutable owner and the rooted destination from scratch.
struct SyncReplicaHistoricalVersionSourceCutpoint final {
    SyncReplicaHistoricalVersionInspectionMode inspection_mode =
        SyncReplicaHistoricalVersionInspectionMode::ExactPayloadAvailability;
    std::string operation_set_digest;
    // Present in rev0972 exact v3 cutpoints. Absent only when decoding the
    // compatible rev0968 v1 exact token or in metadata-only v2 tokens.
    std::optional<std::string> evidence_set_digest;
    // Present in new v4 exact and metadata tokens. Absent only when decoding a
    // compatible pre-pin source token.
    std::optional<std::string> historical_version_pin_set_digest;
    std::optional<std::string> payload_snapshot_digest;

    bool operator==(
        const SyncReplicaHistoricalVersionSourceCutpoint&) const = default;
};

inline void validate_sync_replica_historical_version_source_cutpoint_or_throw(
    const SyncReplicaHistoricalVersionSourceCutpoint& cutpoint,
    std::string_view label =
        "sync replica historical-version source cutpoint") {
    if (!is_lowercase_sha256_hex(cutpoint.operation_set_digest)) {
        throw std::invalid_argument(
            std::string(label) + " operation-set digest is invalid");
    }
    if (cutpoint.historical_version_pin_set_digest.has_value() &&
        !is_lowercase_sha256_hex(
            *cutpoint.historical_version_pin_set_digest)) {
        throw std::invalid_argument(
            std::string(label) + " historical-version pin-set digest is invalid");
    }
    switch (cutpoint.inspection_mode) {
        case SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability:
            if (cutpoint.evidence_set_digest.has_value() &&
                !is_lowercase_sha256_hex(
                    *cutpoint.evidence_set_digest)) {
                throw std::invalid_argument(
                    std::string(label) +
                    " evidence-set digest is invalid");
            }
            if (!cutpoint.payload_snapshot_digest.has_value() ||
                !is_lowercase_sha256_hex(
                    *cutpoint.payload_snapshot_digest)) {
                throw std::invalid_argument(
                    std::string(label) +
                    " payload-snapshot digest is invalid");
            }
            return;
        case SyncReplicaHistoricalVersionInspectionMode::CausalMetadataOnly:
            if (cutpoint.evidence_set_digest.has_value() ||
                cutpoint.payload_snapshot_digest.has_value()) {
                throw std::invalid_argument(
                    std::string(label) +
                    " metadata-only cutpoint carries an exact-mode digest");
            }
            return;
    }
    throw std::invalid_argument(
        std::string(label) + " inspection mode is invalid");
}

// Preserve decoding of the rev0968 v1, rev0970 v2 metadata, and rev0972 v3
// exact tokens byte-for-byte. New v4 tokens bind the local pin set as well as
// every mode-specific input.
[[nodiscard]] inline std::string
encode_sync_replica_historical_version_source_cutpoint_or_throw(
    const SyncReplicaHistoricalVersionSourceCutpoint& cutpoint,
    std::string_view label =
        "sync replica historical-version source cutpoint") {
    validate_sync_replica_historical_version_source_cutpoint_or_throw(
        cutpoint, label);
    switch (cutpoint.inspection_mode) {
        case SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability:
            if (cutpoint.evidence_set_digest.has_value() &&
                cutpoint.historical_version_pin_set_digest.has_value()) {
                return "v4:exact:" + cutpoint.operation_set_digest + ':' +
                    *cutpoint.evidence_set_digest + ':' +
                    *cutpoint.historical_version_pin_set_digest + ':' +
                    *cutpoint.payload_snapshot_digest;
            }
            if (cutpoint.evidence_set_digest.has_value()) {
                return "v3:exact:" + cutpoint.operation_set_digest + ':' +
                    *cutpoint.evidence_set_digest + ':' +
                    *cutpoint.payload_snapshot_digest;
            }
            return "v1:" + cutpoint.operation_set_digest + ':' +
                *cutpoint.payload_snapshot_digest;
        case SyncReplicaHistoricalVersionInspectionMode::CausalMetadataOnly:
            if (cutpoint.historical_version_pin_set_digest.has_value()) {
                return "v4:metadata:" + cutpoint.operation_set_digest + ':' +
                    *cutpoint.historical_version_pin_set_digest;
            }
            return "v2:metadata:" + cutpoint.operation_set_digest;
    }
    throw std::invalid_argument(
        std::string(label) + " inspection mode is invalid");
}

[[nodiscard]] inline SyncReplicaHistoricalVersionSourceCutpoint
decode_sync_replica_historical_version_source_cutpoint_or_throw(
    std::string_view token,
    std::string_view label =
        "sync replica historical-version source cutpoint") {
    constexpr std::string_view exact_v4_prefix = "v4:exact:";
    constexpr std::string_view metadata_v4_prefix = "v4:metadata:";
    constexpr std::string_view exact_v3_prefix = "v3:exact:";
    constexpr std::string_view exact_v1_prefix = "v1:";
    constexpr std::string_view metadata_prefix = "v2:metadata:";
    constexpr std::size_t digest_size = 64U;
    if (token.starts_with(exact_v4_prefix)) {
        constexpr std::size_t encoded_size =
            exact_v4_prefix.size() + digest_size + 1U + digest_size + 1U +
            digest_size + 1U + digest_size;
        const std::size_t operation_separator =
            exact_v4_prefix.size() + digest_size;
        const std::size_t evidence_separator =
            operation_separator + 1U + digest_size;
        const std::size_t pin_separator =
            evidence_separator + 1U + digest_size;
        if (token.size() != encoded_size ||
            token[operation_separator] != ':' ||
            token[evidence_separator] != ':' ||
            token[pin_separator] != ':') {
            throw std::invalid_argument(
                std::string(label) + " token framing is invalid");
        }
        SyncReplicaHistoricalVersionSourceCutpoint cutpoint{
            .inspection_mode = SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability,
            .operation_set_digest = std::string(
                token.substr(exact_v4_prefix.size(), digest_size)),
            .evidence_set_digest = std::string(token.substr(
                operation_separator + 1U, digest_size)),
            .historical_version_pin_set_digest = std::string(token.substr(
                evidence_separator + 1U, digest_size)),
            .payload_snapshot_digest = std::string(token.substr(
                pin_separator + 1U, digest_size)),
        };
        validate_sync_replica_historical_version_source_cutpoint_or_throw(
            cutpoint, label);
        return cutpoint;
    }
    if (token.starts_with(metadata_v4_prefix)) {
        constexpr std::size_t encoded_size =
            metadata_v4_prefix.size() + digest_size + 1U + digest_size;
        const std::size_t separator =
            metadata_v4_prefix.size() + digest_size;
        if (token.size() != encoded_size || token[separator] != ':') {
            throw std::invalid_argument(
                std::string(label) + " token framing is invalid");
        }
        SyncReplicaHistoricalVersionSourceCutpoint cutpoint{
            .inspection_mode = SyncReplicaHistoricalVersionInspectionMode::
                CausalMetadataOnly,
            .operation_set_digest = std::string(
                token.substr(metadata_v4_prefix.size(), digest_size)),
            .evidence_set_digest = std::nullopt,
            .historical_version_pin_set_digest = std::string(token.substr(
                separator + 1U, digest_size)),
            .payload_snapshot_digest = std::nullopt,
        };
        validate_sync_replica_historical_version_source_cutpoint_or_throw(
            cutpoint, label);
        return cutpoint;
    }
    if (token.starts_with(exact_v3_prefix)) {
        constexpr std::size_t encoded_size =
            exact_v3_prefix.size() + digest_size + 1U + digest_size + 1U +
            digest_size;
        const std::size_t operation_separator =
            exact_v3_prefix.size() + digest_size;
        const std::size_t evidence_separator =
            operation_separator + 1U + digest_size;
        if (token.size() != encoded_size ||
            token[operation_separator] != ':' ||
            token[evidence_separator] != ':') {
            throw std::invalid_argument(
                std::string(label) + " token framing is invalid");
        }
        SyncReplicaHistoricalVersionSourceCutpoint cutpoint{
            .inspection_mode = SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability,
            .operation_set_digest = std::string(
                token.substr(exact_v3_prefix.size(), digest_size)),
            .evidence_set_digest = std::string(token.substr(
                operation_separator + 1U, digest_size)),
            .historical_version_pin_set_digest = std::nullopt,
            .payload_snapshot_digest = std::string(token.substr(
                evidence_separator + 1U, digest_size)),
        };
        validate_sync_replica_historical_version_source_cutpoint_or_throw(
            cutpoint, label);
        return cutpoint;
    }
    if (token.starts_with(exact_v1_prefix)) {
        constexpr std::size_t encoded_size =
            exact_v1_prefix.size() + digest_size + 1U + digest_size;
        if (token.size() != encoded_size ||
            token[exact_v1_prefix.size() + digest_size] != ':') {
            throw std::invalid_argument(
                std::string(label) + " token framing is invalid");
        }
        SyncReplicaHistoricalVersionSourceCutpoint cutpoint{
            .inspection_mode = SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability,
            .operation_set_digest = std::string(
                token.substr(exact_v1_prefix.size(), digest_size)),
            .evidence_set_digest = std::nullopt,
            .historical_version_pin_set_digest = std::nullopt,
            .payload_snapshot_digest = std::string(token.substr(
                exact_v1_prefix.size() + digest_size + 1U, digest_size)),
        };
        validate_sync_replica_historical_version_source_cutpoint_or_throw(
            cutpoint, label);
        return cutpoint;
    }
    if (token.starts_with(metadata_prefix) &&
        token.size() == metadata_prefix.size() + digest_size) {
        SyncReplicaHistoricalVersionSourceCutpoint cutpoint{
            .inspection_mode = SyncReplicaHistoricalVersionInspectionMode::
                CausalMetadataOnly,
            .operation_set_digest =
                std::string(token.substr(metadata_prefix.size())),
            .evidence_set_digest = std::nullopt,
            .historical_version_pin_set_digest = std::nullopt,
            .payload_snapshot_digest = std::nullopt,
        };
        validate_sync_replica_historical_version_source_cutpoint_or_throw(
            cutpoint, label);
        return cutpoint;
    }
    throw std::invalid_argument(
        std::string(label) + " token framing is invalid");
}

enum class SyncReplicaHistoricalVersionSourceChangeStage : std::uint8_t {
    OperationSetBeforePayloadObservation = 1U,
    OperationSetDuringPayloadObservation = 2U,
    PayloadSnapshot = 3U,
    // An exact restore request named the visible head observed during browsing,
    // but that path no longer has that sole current operation. This check is
    // performed before catalog, rooted-path, or payload-store work.
    RestoreCurrentOperation = 4U,
    // A v3 exact page also binds inactive retained evidence because that
    // evidence participates in its payload-reachability result.
    EvidenceSetBeforePayloadObservation = 5U,
    EvidenceSetDuringPayloadObservation = 6U,
    HistoricalVersionPinSetBeforePayloadObservation = 7U,
    HistoricalVersionPinSetDuringPayloadObservation = 8U,
    // The deletion-free retention planner observed a different exact set of
    // live same-store-owner payload capabilities at its final cutpoint. This
    // includes capability registration identity, not merely aggregate counts.
    RetentionLiveCapabilitySet = 9U,
    // The exact durable candidate witness was proved and the payload mark was
    // published beneath its retained writer fence, but the SQLite source
    // generation or one of its bound digests changed before final settlement.
    // The persisted record is therefore conservative stale evidence, not a
    // successful grace-period mark.
    RetentionMarkPublication = 10U,
};

[[nodiscard]] constexpr std::string_view
sync_replica_historical_version_source_change_stage_name(
    SyncReplicaHistoricalVersionSourceChangeStage stage) noexcept {
    switch (stage) {
        case SyncReplicaHistoricalVersionSourceChangeStage::
                OperationSetBeforePayloadObservation:
            return "operation_set_before_payload_observation";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                OperationSetDuringPayloadObservation:
            return "operation_set_during_payload_observation";
        case SyncReplicaHistoricalVersionSourceChangeStage::PayloadSnapshot:
            return "payload_snapshot";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                RestoreCurrentOperation:
            return "restore_current_operation";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                EvidenceSetBeforePayloadObservation:
            return "evidence_set_before_payload_observation";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                EvidenceSetDuringPayloadObservation:
            return "evidence_set_during_payload_observation";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                HistoricalVersionPinSetBeforePayloadObservation:
            return "historical_version_pin_set_before_payload_observation";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                HistoricalVersionPinSetDuringPayloadObservation:
            return "historical_version_pin_set_during_payload_observation";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                RetentionLiveCapabilitySet:
            return "retention_live_capability_set";
        case SyncReplicaHistoricalVersionSourceChangeStage::
                RetentionMarkPublication:
            return "retention_mark_publication";
    }
    return "unknown";
}

// Typed drift lets the service report a restartable browse failure without
// parsing diagnostic prose. It deliberately carries no fabricated replacement
// token: a pre-scan operation mismatch has not observed the payload namespace.
class SyncReplicaHistoricalVersionSourceChangedError final
    : public std::runtime_error {
public:
    SyncReplicaHistoricalVersionSourceChangedError(
        SyncReplicaHistoricalVersionSourceChangeStage stage,
        std::string message)
        : std::runtime_error(std::move(message)), stage_(stage) {}

    [[nodiscard]] SyncReplicaHistoricalVersionSourceChangeStage stage()
        const noexcept {
        return stage_;
    }

private:
    SyncReplicaHistoricalVersionSourceChangeStage stage_;
};

struct SyncReplicaHistoricalVersionQuery final {
    SyncReplicaHistoricalVersionInspectionMode inspection_mode =
        SyncReplicaHistoricalVersionInspectionMode::ExactPayloadAvailability;
    std::uint64_t maximum_entries =
        kSyncReplicaHistoricalVersionDefaultMaximumEntries;
    std::optional<std::string> canonical_path;
    std::optional<std::string> start_after_operation_id;
    // Optional fail-closed browse pin. A later page can copy the exact source
    // token returned by its first page and will either observe the same active
    // operation set plus mode-specific inputs or fail without silent omission.
    std::optional<SyncReplicaHistoricalVersionSourceCutpoint>
        expected_source_cutpoint;

    bool operator==(const SyncReplicaHistoricalVersionQuery&) const = default;
};

// One deletion-free, exact physical-payload planning page. The planner is
// intentionally separate from historical-operation pagination: its cursor is
// one digest-named physical object, and every page requires the complete
// replica/evidence/pin/payload cutpoint. It explains roots and unreferenced
// objects but carries no quota, grace-window, or unlink authority.
inline constexpr std::uint64_t
    kSyncReplicaRetentionPlanDefaultMaximumEntries = 64U;
inline constexpr std::uint64_t
    kSyncReplicaRetentionPlanMaximumEntries = 1024U;

struct SyncReplicaRetentionPlanQuery final {
    std::uint64_t maximum_entries =
        kSyncReplicaRetentionPlanDefaultMaximumEntries;
    std::optional<std::string> start_after_content_sha256;
    std::optional<SyncReplicaHistoricalVersionSourceCutpoint>
        expected_source_cutpoint;

    bool operator==(const SyncReplicaRetentionPlanQuery&) const = default;
};

inline void validate_sync_replica_retention_plan_query_or_throw(
    const SyncReplicaRetentionPlanQuery& query,
    std::string_view label = "sync replica retention plan query") {
    if (query.maximum_entries == 0U ||
        query.maximum_entries > kSyncReplicaRetentionPlanMaximumEntries) {
        throw std::invalid_argument(
            std::string(label) + " entry limit is invalid");
    }
    if (query.start_after_content_sha256.has_value() &&
        !is_lowercase_sha256_hex(*query.start_after_content_sha256)) {
        throw std::invalid_argument(
            std::string(label) +
            " cursor is not one lowercase SHA-256 payload digest");
    }
    if (query.expected_source_cutpoint.has_value()) {
        validate_sync_replica_historical_version_source_cutpoint_or_throw(
            *query.expected_source_cutpoint,
            std::string(label) + " source cutpoint");
        const auto& cutpoint = *query.expected_source_cutpoint;
        if (cutpoint.inspection_mode !=
                SyncReplicaHistoricalVersionInspectionMode::
                    ExactPayloadAvailability ||
            !cutpoint.evidence_set_digest.has_value() ||
            !cutpoint.historical_version_pin_set_digest.has_value() ||
            !cutpoint.payload_snapshot_digest.has_value()) {
            throw std::invalid_argument(
                std::string(label) +
                " source cutpoint is not one current exact v4 cutpoint");
        }
    }
}

// One restore selection and, for the shipping command, the exact sole visible
// operation the operator reviewed with it. The optional form exists only so the
// rev0966 local-socket frame can remain accepted; new product callers should
// always bind expected_current_operation_id. Restore never treats this as
// publication authority: the folder owner still re-proves replica, catalog,
// rooted path, and retained payload before minting a new causal successor.
struct SyncReplicaHistoricalVersionRestoreRequest final {
    std::string operation_id;
    std::optional<std::string> expected_current_operation_id;

    bool operator==(const SyncReplicaHistoricalVersionRestoreRequest&) const =
        default;
};

inline void validate_sync_replica_historical_version_restore_request_or_throw(
    const SyncReplicaHistoricalVersionRestoreRequest& request,
    std::string_view label = "sync replica historical-version restore") {
    if (!is_lowercase_sha256_hex(request.operation_id)) {
        throw std::invalid_argument(
            std::string(label) + " operation ID is invalid");
    }
    if (request.expected_current_operation_id.has_value()) {
        if (!is_lowercase_sha256_hex(
                *request.expected_current_operation_id)) {
            throw std::invalid_argument(
                std::string(label) +
                " expected current operation ID is invalid");
        }
        if (*request.expected_current_operation_id == request.operation_id) {
            throw std::invalid_argument(
                std::string(label) +
                " historical and expected current operation IDs are equal");
        }
    }
}

inline void validate_sync_replica_historical_version_query_or_throw(
    const SyncReplicaHistoricalVersionQuery& query,
    std::string_view label = "sync replica historical-version query") {
    if (query.maximum_entries == 0U ||
        query.maximum_entries > kSyncReplicaHistoricalVersionMaximumEntries) {
        throw std::invalid_argument(
            std::string(label) + " entry limit is invalid");
    }
    if (query.canonical_path.has_value()) {
        if (query.canonical_path->empty() ||
            query.canonical_path->size() >
                kSyncReplicaHistoricalVersionMaximumCanonicalPathBytes) {
            throw std::invalid_argument(
                std::string(label) + " path size is invalid");
        }
        const SyncValidationResult validated =
            validate_sync_relative_path(*query.canonical_path);
        if (!validated.ok) {
            throw std::invalid_argument(
                std::string(label) + " path is not canonical: " +
                validated.reason);
        }
    }
    if (query.start_after_operation_id.has_value() &&
        !is_lowercase_sha256_hex(*query.start_after_operation_id)) {
        throw std::invalid_argument(
            std::string(label) +
            " cursor is not one lowercase SHA-256 operation ID");
    }
    switch (query.inspection_mode) {
        case SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability:
        case SyncReplicaHistoricalVersionInspectionMode::CausalMetadataOnly:
            break;
        default:
            throw std::invalid_argument(
                std::string(label) + " inspection mode is invalid");
    }
    if (query.expected_source_cutpoint.has_value()) {
        validate_sync_replica_historical_version_source_cutpoint_or_throw(
            *query.expected_source_cutpoint,
            std::string(label) + " expected source cutpoint");
        if (query.expected_source_cutpoint->inspection_mode !=
            query.inspection_mode) {
            throw std::invalid_argument(
                std::string(label) +
                " expected source cutpoint mode does not match the query");
        }
    }
}

}  // namespace anonsync
