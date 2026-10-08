#pragma once

#include <string>

namespace anonsync {

// Conflict resolution must be orientation-independent. The same two version
// identities presented as (local, remote) or (remote, local) must select one
// winner and one conflict-set identity. This leaf owns only the deterministic
// policy; filesystem actions and manifest validation remain in sync_domain.
enum class SyncConflictValueKind {
    File,
    Tombstone,
};

enum class SyncConflictDisposition {
    // The local version is the deterministic winner. Advertise it; the peer
    // that owns the losing file is responsible for preserving that file.
    PublishLocalWinner,

    // The remote tombstone is the deterministic winner and the local value is
    // also a tombstone, so no file bytes exist to preserve.
    ApplyRemoteWinner,

    // The remote version is the deterministic winner and the local value is a
    // file. Preserve the local file before applying the remote winner.
    PreserveLocalFileThenApplyRemoteWinner,
};

struct SyncConflictResolution final {
    SyncConflictDisposition disposition =
        SyncConflictDisposition::PublishLocalWinner;
    SyncConflictValueKind winner_kind = SyncConflictValueKind::File;
    SyncConflictValueKind loser_kind = SyncConflictValueKind::File;
    std::string winner_version_digest;
    std::string loser_version_digest;
    SyncConflictValueKind canonical_first_kind = SyncConflictValueKind::File;
    std::string canonical_first_version_digest;
    SyncConflictValueKind canonical_second_kind = SyncConflictValueKind::File;
    std::string canonical_second_version_digest;

    [[nodiscard]] bool local_is_winner() const noexcept {
        return disposition == SyncConflictDisposition::PublishLocalWinner;
    }
};

// Version digests must be distinct canonical lowercase SHA-256 strings.
// Tombstones win file/tombstone races to prevent uncoordinated resurrection;
// equal-kind versions use a total order over their immutable version digests.
// The returned canonical pair is lexicographically sorted and is therefore
// safe to bind into an orientation-independent conflict-set identifier.
[[nodiscard]] SyncConflictResolution resolve_sync_conflict_or_throw(
    SyncConflictValueKind local_kind,
    const std::string& local_version_digest,
    SyncConflictValueKind remote_kind,
    const std::string& remote_version_digest);

// Mints the shared conflict-set identity from the canonical version pair. It
// is intentionally independent of local/remote orientation and streams framed
// fields directly into SHA-256 rather than constructing ambient-locale text.
[[nodiscard]] std::string make_sync_conflict_set_id_or_throw(
    const std::string& folder_id,
    const std::string& canonical_path,
    SyncConflictValueKind local_kind,
    const std::string& local_version_digest,
    SyncConflictValueKind remote_kind,
    const std::string& remote_version_digest);

}  // namespace anonsync
