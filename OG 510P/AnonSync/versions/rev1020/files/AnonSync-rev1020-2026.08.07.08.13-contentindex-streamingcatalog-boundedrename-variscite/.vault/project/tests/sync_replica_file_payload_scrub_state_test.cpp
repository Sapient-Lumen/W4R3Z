#include "sha256_digest.hpp"
#include "sync_replica_file_payload_scrub_state.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#include <sys/stat.h>

namespace {

std::uint64_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_invalid(
    Callable&& callable,
    std::string_view expected,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::invalid_argument& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected diagnostic: " + error.what());
    } catch (const std::exception& error) {
        fail(message + ": wrong exception type: " + error.what());
    }
    fail(message + ": no error was thrown");
}

anonsync::SyncPosixRegularFileSnapshotMetadata metadata(
    std::uint64_t inode,
    std::uint64_t size,
    std::int64_t seconds) {
    return {
        71U,
        inode,
        size,
        1U,
        1001U,
        1002U,
        static_cast<std::uint32_t>(S_IFREG | S_IRUSR | S_IWUSR),
        seconds,
        123456789U,
        seconds + 1,
        987654321U};
}

anonsync::SyncReplicaFilePayloadScrubState initial() {
    return anonsync::initial_sync_replica_file_payload_scrub_state_or_throw(
        anonsync::sha256_hex("identity-v3"), metadata(501U, 173U, -7),
        "scrub-state fixture");
}

void reseal(std::string& encoded) {
    encoded.replace(
        encoded.size() - 64U, 64U,
        anonsync::sha256_hex(encoded.substr(0U, encoded.size() - 64U)));
}

void test_idle_round_trip() {
    const auto state = initial();
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            state, 1024U, "idle scrub state");
    require(
        encoded.size() ==
            anonsync::sync_replica_file_payload_scrub_state_exact_bytes(),
        "scrub-state exact encoded size changed");
    require(
        anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
            encoded, 1024U, "idle scrub state") == state,
        "idle scrub-state round trip changed fields");
    require(
        anonsync::kSyncReplicaFilePayloadScrubStateBasename ==
            ".anonsync-payload-scrub-state-v1",
        "scrub-state basename drifted");
}

void test_prepared_round_trip() {
    auto prepared = initial();
    prepared.generation = 5U;
    prepared.completed_cycles = 2U;
    prepared.cursor_after_content_sha256 = anonsync::sha256_hex("previous");
    prepared.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Prepared;
    prepared.active_content_sha256 = anonsync::sha256_hex("");
    prepared.active_metadata = metadata(600U, 0U, 10);
    prepared.active_offset_bytes = 0U;
    prepared.active_hash = anonsync::ResumableSha256{}.checkpoint();

    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            prepared, 1024U, "prepared scrub state");
    require(
        anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
            encoded, 1024U, "prepared scrub state") == prepared,
        "prepared scrub-state round trip changed fields");
}

void test_progress_and_failure_round_trip() {
    auto progress = initial();
    progress.generation = 7U;
    progress.completed_cycles = 3U;
    progress.cursor_after_content_sha256 = anonsync::sha256_hex("previous");
    progress.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Progress;
    progress.active_content_sha256 = anonsync::sha256_hex("payload bytes");
    progress.active_metadata = metadata(601U, 13U, 11);
    anonsync::ResumableSha256 running;
    running.update("payload");
    progress.active_hash = running.checkpoint();
    progress.active_offset_bytes = 7U;

    const std::string encoded_progress =
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            progress, 1024U, "progress scrub state");
    require(
        anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
            encoded_progress, 1024U, "progress scrub state") == progress,
        "progress scrub-state round trip changed fields");

    auto failure = progress;
    running.update(" bytes");
    failure.active_hash = running.checkpoint();
    failure.active_offset_bytes = 13U;
    anonsync::ResumableSha256 finalized(failure.active_hash);
    failure.observed_content_sha256 = finalized.finish_hex();
    failure.active_content_sha256 = anonsync::sha256_hex("different bytes");
    require(
        failure.observed_content_sha256 != failure.active_content_sha256,
        "failure fixture accidentally matched expected digest");
    failure.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::IntegrityFailure;

    const std::string encoded_failure =
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            failure, 1024U, "failure scrub state");
    require(
        anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
            encoded_failure, 1024U, "failure scrub state") == failure,
        "failure scrub-state round trip changed fields");
}

void test_checksum_and_framing_rejection() {
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            initial(), 1024U, "corruption fixture");

    std::string corrupted = encoded;
    corrupted[17U] = static_cast<char>(corrupted[17U] ^ 0x01);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
                corrupted, 1024U, "corrupted scrub state");
        },
        "checksum",
        "scrub-state checksum corruption was accepted");

    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
                std::string_view(encoded).substr(0U, encoded.size() - 1U),
                1024U, "truncated scrub state");
        },
        "exact v1 size",
        "truncated scrub state was accepted");

    std::string extended = encoded;
    extended.push_back('x');
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
                extended, 1024U, "extended scrub state");
        },
        "exact v1 size",
        "extended scrub state was accepted");

    std::string incompatible = encoded;
    incompatible[0U] = 'A';
    reseal(incompatible);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
                incompatible, 1024U, "incompatible scrub state");
        },
        "incompatible format generation",
        "checksum-valid incompatible scrub generation was accepted");
}

void test_semantic_rejection() {
    auto idle_active = initial();
    idle_active.active_offset_bytes = 1U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                idle_active, 1024U, "idle active scrub state");
        },
        "idle form",
        "idle scrub state retained active progress");

    auto prepared = initial();
    prepared.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Prepared;
    prepared.active_content_sha256 = anonsync::sha256_hex("payload");
    prepared.active_metadata = metadata(601U, 7U, 14);
    anonsync::ResumableSha256 prepared_after_byte;
    prepared_after_byte.update("p");
    prepared.active_hash = prepared_after_byte.checkpoint();
    prepared.active_offset_bytes = 1U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                prepared, 1024U, "advanced prepared scrub state");
        },
        "initial cutpoint",
        "prepared state with consumed bytes was accepted");

    prepared.active_hash = anonsync::ResumableSha256{}.checkpoint();
    prepared.active_offset_bytes = 0U;
    prepared.observed_content_sha256 = anonsync::sha256_hex("premature");
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                prepared, 1024U, "terminal prepared scrub state");
        },
        "terminal digest",
        "prepared state retained a terminal digest");

    auto progress = initial();
    progress.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Progress;
    progress.active_content_sha256 = anonsync::sha256_hex("payload");
    progress.active_metadata = metadata(602U, 7U, 15);
    progress.active_hash = anonsync::ResumableSha256{}.checkpoint();
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                progress, 1024U, "zero progress scrub state");
        },
        "non-progressing",
        "zero-byte progress state was accepted");

    anonsync::ResumableSha256 first_byte;
    first_byte.update("p");
    progress.active_hash = first_byte.checkpoint();
    progress.active_offset_bytes = 1U;
    progress.observed_content_sha256 = anonsync::sha256_hex("premature");
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                progress, 1024U, "premature digest scrub state");
        },
        "terminal digest",
        "progress state retained a terminal digest");

    auto failure = progress;
    failure.observed_content_sha256.clear();
    failure.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::IntegrityFailure;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                failure, 1024U, "short failure scrub state");
        },
        "exact completion",
        "partial failure state was accepted");

    auto oversized = initial();
    oversized.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Progress;
    oversized.active_content_sha256 = anonsync::sha256_hex("oversized");
    oversized.active_metadata = metadata(603U, 2048U, 16);
    oversized.active_offset_bytes = 1U;
    oversized.active_hash = first_byte.checkpoint();
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                oversized, 1024U, "oversized scrub state");
        },
        "payload beyond",
        "scrub state exceeded configured payload ceiling");

    auto bad_identity = initial();
    bad_identity.store_identity_sha256[0U] = 'G';
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
                bad_identity, 1024U, "bad identity scrub state");
        },
        "store-identity digest",
        "invalid store identity digest was accepted");
}

}  // namespace

int main() {
    try {
        test_idle_round_trip();
        test_prepared_round_trip();
        test_progress_and_failure_round_trip();
        test_checksum_and_framing_rejection();
        test_semantic_rejection();
        std::cout << "payload scrub-state checks: " << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "payload scrub-state test failed after " << checks
                  << " checks: " << error.what() << "\n";
        return 1;
    }
}

#endif
