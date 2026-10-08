#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace anonsync::persistence {

// Replay-ledger snapshots are metadata journals, not bulk object stores.  These
// are reviewed hard ceilings: callers may tighten them, never widen them.
inline constexpr std::uint64_t kMaximumUntrustedSqliteSnapshotBytes =
    1024ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t kMaximumUntrustedSqliteSnapshotPages =
    262144ULL;
inline constexpr std::size_t kSqliteDatabaseHeaderBytes = 100U;

struct SqliteSnapshotGeometryPolicy {
    std::uint64_t maximum_bytes = kMaximumUntrustedSqliteSnapshotBytes;
    std::uint64_t maximum_pages = kMaximumUntrustedSqliteSnapshotPages;
};

struct SqliteSnapshotGeometry {
    std::uint64_t byte_count = 0;
    std::uint32_t page_size = 0;
    std::uint32_t page_count = 0;

    friend bool operator==(const SqliteSnapshotGeometry&,
                           const SqliteSnapshotGeometry&) = default;
};

// Validate one caller-supplied policy against the reviewed monotone ceiling.
// This is shared by path capture, live backup, and header verification so a
// narrower caller cannot be interpreted differently at adjacent boundaries.
void validate_sqlite_snapshot_geometry_policy_or_throw(
    const SqliteSnapshotGeometryPolicy& policy,
    std::string_view label);

// Promote exact SQLite page-size/page-count observations into bounded geometry.
// This does not prove that the observations describe a stable database; the
// caller must own that lifetime separately (for example with a pinned read
// transaction or a retained file descriptor).
SqliteSnapshotGeometry verify_sqlite_snapshot_page_geometry_or_throw(
    std::uint64_t page_size,
    std::uint64_t page_count,
    std::string_view label,
    const SqliteSnapshotGeometryPolicy& policy = {});

// Promote raw header bytes and an exact descriptor size into trusted SQLite
// file geometry.  A canonical sidecar-free snapshot has no unowned prefix or
// suffix: exact_file_bytes must equal header_page_count * header_page_size.
SqliteSnapshotGeometry verify_sqlite_snapshot_geometry_or_throw(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    std::uint64_t exact_file_bytes,
    std::string_view label,
    const SqliteSnapshotGeometryPolicy& policy = {});

}  // namespace anonsync::persistence
