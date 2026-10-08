#pragma once

#include <cstdint>
#include <limits>
#include <optional>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {

// Process-local operator evidence for one expected immutable payload digest.
// failure_persisted is deliberately scoped to the exact currently reported
// expected/observed pair. A durable witness for an older corrupt byte image
// must never be carried forward after the observed digest changes.
struct SyncReplicaPeerServicePayloadIntegrityEvidence final {
    std::string expected_content_sha256;
    std::string observed_content_sha256;
    bool failure_persisted = false;
    std::uint64_t detection_count = 0U;
    std::uint64_t observed_content_change_count = 0U;

    bool operator==(
        const SyncReplicaPeerServicePayloadIntegrityEvidence&) const = default;
};

enum class SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate
    : std::uint8_t {
    NewExpectedContent = 1U,
    RepeatedExactObservation = 2U,
    ChangedObservedContent = 3U,
};

inline void increment_sync_replica_peer_service_evidence_counter_saturating(
    std::uint64_t& value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) ++value;
}

// Merges one typed payload-integrity exception into initialized or default
// operator evidence. Repeated reports of the exact same pair may accumulate a
// durable publication proof without rebuilding either digest string. A changed
// observed digest is a new byte image and resets that proof to the new
// exception's exact publication result. Every potentially allocating string
// construction completes before counters or persistence evidence are changed.
[[nodiscard]] inline
SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate
merge_sync_replica_peer_service_payload_integrity_evidence(
    SyncReplicaPeerServicePayloadIntegrityEvidence& active,
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256,
    bool failure_persisted) {
    if (active.detection_count == 0U ||
        active.expected_content_sha256 != expected_content_sha256) {
        SyncReplicaPeerServicePayloadIntegrityEvidence replacement;
        replacement.expected_content_sha256 = expected_content_sha256;
        replacement.observed_content_sha256 = observed_content_sha256;
        replacement.failure_persisted = failure_persisted;
        replacement.detection_count = 1U;
        active = std::move(replacement);
        return SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate::
            NewExpectedContent;
    }

    if (active.observed_content_sha256 == observed_content_sha256) {
        increment_sync_replica_peer_service_evidence_counter_saturating(
            active.detection_count);
        active.failure_persisted =
            active.failure_persisted || failure_persisted;
        return SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate::
            RepeatedExactObservation;
    }

    std::string replacement_observed_content(observed_content_sha256);
    active.observed_content_sha256 =
        std::move(replacement_observed_content);
    active.failure_persisted = failure_persisted;
    increment_sync_replica_peer_service_evidence_counter_saturating(
        active.detection_count);
    increment_sync_replica_peer_service_evidence_counter_saturating(
        active.observed_content_change_count);
    return SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate::
        ChangedObservedContent;
}

// Convenience wrapper used by focused state-machine tests. Production owns
// timing separately and merges directly into the retained evidence object so a
// repeated exact alarm performs no optional or string copy.
[[nodiscard]] inline
SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate
merge_sync_replica_peer_service_payload_integrity_evidence(
    std::optional<SyncReplicaPeerServicePayloadIntegrityEvidence>& active,
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256,
    bool failure_persisted) {
    if (!active.has_value()) {
        SyncReplicaPeerServicePayloadIntegrityEvidence replacement;
        const auto update =
            merge_sync_replica_peer_service_payload_integrity_evidence(
                replacement, expected_content_sha256,
                observed_content_sha256, failure_persisted);
        active.emplace(std::move(replacement));
        return update;
    }
    return merge_sync_replica_peer_service_payload_integrity_evidence(
        *active, expected_content_sha256, observed_content_sha256,
        failure_persisted);
}

}  // namespace anonsync
