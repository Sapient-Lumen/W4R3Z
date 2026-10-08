#include "sync_replica_peer_service_integrity_evidence.hpp"

#include <cstdint>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>

namespace {

std::uint64_t checks = 0U;

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void test_exact_pair_persistence_and_change_accounting() {
    using Evidence =
        anonsync::SyncReplicaPeerServicePayloadIntegrityEvidence;
    using Update =
        anonsync::SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate;
    std::optional<Evidence> active;

    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, "expected-a", "observed-a", false) ==
            Update::NewExpectedContent,
        "first observation was not classified as a new expected payload");
    require(
        active.has_value() &&
            active->expected_content_sha256 == "expected-a" &&
            active->observed_content_sha256 == "observed-a" &&
            !active->failure_persisted && active->detection_count == 1U &&
            active->observed_content_change_count == 0U,
        "first observation did not initialize exact evidence");

    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, "expected-a", "observed-a", true) ==
            Update::RepeatedExactObservation,
        "repeated exact observation was misclassified");
    require(
        active->failure_persisted && active->detection_count == 2U &&
            active->observed_content_change_count == 0U,
        "exact repeated observation did not accumulate its durable proof");

    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, "expected-a", "observed-b", false) ==
            Update::ChangedObservedContent,
        "changed corrupt bytes were not classified as a new observation");
    require(
        active->observed_content_sha256 == "observed-b" &&
            !active->failure_persisted && active->detection_count == 3U &&
            active->observed_content_change_count == 1U,
        "an older durable witness was falsely attached to changed corrupt bytes");

    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, "expected-a", "observed-b", true) ==
            Update::RepeatedExactObservation,
        "new exact byte-image repetition was misclassified");
    require(
        active->failure_persisted && active->detection_count == 4U &&
            active->observed_content_change_count == 1U,
        "new exact byte image did not acquire its own durable proof");

    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, "expected-a", "observed-a", false) ==
            Update::ChangedObservedContent,
        "returning to an earlier byte image was not a content transition");
    require(
        !active->failure_persisted && active->detection_count == 5U &&
            active->observed_content_change_count == 2U,
        "returning to an older image resurrected stale persistence evidence");

    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, "expected-b", "observed-c", true) ==
            Update::NewExpectedContent,
        "different expected payload did not start a new alarm");
    require(
        active->expected_content_sha256 == "expected-b" &&
            active->observed_content_sha256 == "observed-c" &&
            active->failure_persisted && active->detection_count == 1U &&
            active->observed_content_change_count == 0U,
        "different expected payload inherited prior alarm accounting");
}

void test_counters_saturate() {
    using Update =
        anonsync::SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate;
    std::optional<anonsync::SyncReplicaPeerServicePayloadIntegrityEvidence>
        active;
    (void)anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
        active, "expected", "observed-a", false);
    active->detection_count = std::numeric_limits<std::uint64_t>::max();
    active->observed_content_change_count =
        std::numeric_limits<std::uint64_t>::max();
    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, "expected", "observed-b", false) ==
            Update::ChangedObservedContent,
        "saturated changed observation was misclassified");
    require(
        active->detection_count ==
                std::numeric_limits<std::uint64_t>::max() &&
            active->observed_content_change_count ==
                std::numeric_limits<std::uint64_t>::max(),
        "payload evidence counters wrapped after saturation");
}

void test_repeated_exact_merge_retains_digest_storage() {
    using Evidence =
        anonsync::SyncReplicaPeerServicePayloadIntegrityEvidence;
    using Update =
        anonsync::SyncReplicaPeerServicePayloadIntegrityEvidenceUpdate;

    const std::string expected(96U, 'e');
    const std::string observed(96U, 'o');
    Evidence active;
    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, expected, observed, false) ==
            Update::NewExpectedContent,
        "direct evidence initialization was not classified as new");
    const char* const expected_storage =
        active.expected_content_sha256.data();
    const char* const observed_storage =
        active.observed_content_sha256.data();
    require(
        anonsync::merge_sync_replica_peer_service_payload_integrity_evidence(
            active, expected, observed, true) ==
            Update::RepeatedExactObservation,
        "direct repeated evidence merge was misclassified");
    require(
        active.expected_content_sha256.data() == expected_storage &&
            active.observed_content_sha256.data() == observed_storage &&
            active.failure_persisted && active.detection_count == 2U,
        "repeated exact evidence rebuilt digest storage or lost accounting");
}

}  // namespace

int main() {
    try {
        test_exact_pair_persistence_and_change_accounting();
        test_counters_saturate();
        test_repeated_exact_merge_retains_digest_storage();
        std::cout
            << "sync replica peer-service integrity evidence tests passed ("
            << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "sync replica peer-service integrity evidence tests failed after "
            << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
