#pragma once

#if !defined(_WIN32)

#include "resumable_sha256.hpp"
#include "sync_posix_descriptor_snapshot.hpp"

#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::string_view
    kSyncReplicaFilePayloadScrubStateBasename =
        ".anonsync-payload-scrub-state-v1";

enum class SyncReplicaFilePayloadScrubStateDisposition : std::uint8_t {
    Idle = 1,
    Progress = 2,
    IntegrityFailure = 3,
    // Durable write-ahead intent published before the first byte of a newly
    // selected payload is read. Keeping the new value after the established
    // v1 values preserves old Idle/Progress/IntegrityFailure encodings while
    // making an interrupted read conservatively visible after restart.
    Prepared = 4,
};

// One checksum-framed continuation for the rotating payload-byte scrub. This
// record is scheduling and failure evidence, never proof that a payload is
// valid: only finishing the resumable SHA-256 and comparing it with the exact
// digest basename grants a completed scrub result.
struct SyncReplicaFilePayloadScrubState final {
    std::string store_identity_sha256;
    SyncPosixRegularFileSnapshotMetadata store_identity_metadata;
    std::uint64_t generation = 1U;
    std::uint64_t completed_cycles = 0U;
    SyncReplicaFilePayloadScrubStateDisposition disposition =
        SyncReplicaFilePayloadScrubStateDisposition::Idle;

    // Last fully scrubbed digest. Empty means the next cycle begins at the
    // first lexicographic payload identity.
    std::string cursor_after_content_sha256;

    // Prepared/Progress/IntegrityFailure only. The exact metadata freezes the
    // file selected for the read. Prepared is the durable write-ahead form and
    // requires offset zero plus the initial SHA-256 checkpoint. Progress
    // requires 0 < active_offset_bytes < size. IntegrityFailure requires exact
    // completion and an observed digest different from the basename.
    std::string active_content_sha256;
    SyncPosixRegularFileSnapshotMetadata active_metadata;
    std::uint64_t active_offset_bytes = 0U;
    ResumableSha256Checkpoint active_hash;
    std::string observed_content_sha256;

    bool operator==(const SyncReplicaFilePayloadScrubState&) const = default;
};

[[nodiscard]] std::uint64_t
sync_replica_file_payload_scrub_state_exact_bytes() noexcept;

[[nodiscard]] SyncReplicaFilePayloadScrubState
initial_sync_replica_file_payload_scrub_state_or_throw(
    std::string store_identity_sha256,
    SyncPosixRegularFileSnapshotMetadata store_identity_metadata,
    std::string_view label = "payload scrub initial state");

[[nodiscard]] std::string
serialize_sync_replica_file_payload_scrub_state_or_throw(
    const SyncReplicaFilePayloadScrubState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label = "payload scrub state serialization");

[[nodiscard]] SyncReplicaFilePayloadScrubState
parse_sync_replica_file_payload_scrub_state_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_bytes,
    std::string_view label = "payload scrub state parsing");

}  // namespace anonsync

#endif
