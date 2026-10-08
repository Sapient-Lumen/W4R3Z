#pragma once

#if !defined(_WIN32)

#include "resumable_sha256.hpp"
#include "sync_posix_descriptor_snapshot.hpp"

#include <array>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::string_view
    kSyncReplicaFilePayloadTerminalVerificationBasenamePrefix =
        ".anonsync-payload-prefix-verification-v1-";

// One owner turn explicitly reads at most 32 MiB while verifying a complete
// staged target. The protocol may already have received the entire payload;
// this independent frontier keeps final whole-target SHA-256 restartable for
// multi-terabyte files without making the durable checkpoint publication
// authority.
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep =
        32ULL * 1024ULL * 1024ULL;

// Historical source checks and bounded helpers retain this exact alias to the
// one shipping owner frontier.
inline constexpr std::uint64_t
    kSyncReplicaFilePayloadTerminalVerificationMaximumAdvanceBytes =
        kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep;

// Fixed-width computational progress for one exact complete staged-prefix
// inode. The staged-prefix metadata always binds the complete file while the
// hash checkpoint remains strictly nonterminal. This is never publication
// authority: callers must still hold the exact store lease, re-prove the staged
// inode and pathname, finish SHA-256 in the current process, compare the trusted
// content digest, and publish that exact opened inode.
struct SyncReplicaFilePayloadTerminalVerificationState final {
    std::string store_identity_sha256;
    SyncPosixRegularFileSnapshotMetadata store_identity_metadata;
    std::uint64_t generation = 1U;

    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    SyncPosixRegularFileSnapshotMetadata staged_prefix_metadata;
    std::uint64_t verified_offset_bytes = 0U;
    ResumableSha256Checkpoint hash;

    bool operator==(
        const SyncReplicaFilePayloadTerminalVerificationState&) const = default;
};

// One fixed-size journal contains two independently checksum-framed slots. An
// update overwrites only the older slot and fsyncs the existing inode. A torn
// slot therefore leaves the prior generation available without an extra
// per-range pathname rename or directory fsync.
struct SyncReplicaFilePayloadTerminalVerificationJournal final {
    std::array<
        std::optional<SyncReplicaFilePayloadTerminalVerificationState>, 2U>
        slots;
    SyncReplicaFilePayloadTerminalVerificationState latest_state;
    std::uint32_t latest_slot_index = 0U;
    std::uint32_t valid_slot_count = 0U;
    std::uint32_t invalid_nonzero_slot_count = 0U;

    bool operator==(
        const SyncReplicaFilePayloadTerminalVerificationJournal&) const =
        default;
};

[[nodiscard]] std::uint64_t
sync_replica_file_payload_terminal_verification_slot_exact_bytes() noexcept;

[[nodiscard]] std::uint64_t
sync_replica_file_payload_terminal_verification_journal_exact_bytes() noexcept;

[[nodiscard]] std::string
serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
    const SyncReplicaFilePayloadTerminalVerificationState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label);

[[nodiscard]] SyncReplicaFilePayloadTerminalVerificationState
parse_sync_replica_file_payload_terminal_verification_state_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_bytes,
    std::string_view label);

[[nodiscard]] std::string
initial_sync_replica_file_payload_terminal_verification_journal_or_throw(
    const SyncReplicaFilePayloadTerminalVerificationState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label);

[[nodiscard]] SyncReplicaFilePayloadTerminalVerificationJournal
parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_bytes,
    std::string_view label);

[[nodiscard]] constexpr std::uint32_t
sync_replica_file_payload_terminal_verification_next_slot_index(
    const SyncReplicaFilePayloadTerminalVerificationJournal& journal) noexcept {
    return journal.latest_slot_index == 0U ? 1U : 0U;
}

}  // namespace anonsync

#endif
