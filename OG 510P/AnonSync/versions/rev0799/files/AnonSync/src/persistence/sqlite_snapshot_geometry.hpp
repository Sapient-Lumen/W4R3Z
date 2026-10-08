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

// Promote raw header bytes and an exact descriptor size into trusted SQLite
// file geometry.  A canonical sidecar-free snapshot has no unowned prefix or
// suffix: exact_file_bytes must equal header_page_count * header_page_size.
SqliteSnapshotGeometry verify_sqlite_snapshot_geometry_or_throw(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    std::uint64_t exact_file_bytes,
    std::string_view label,
    const SqliteSnapshotGeometryPolicy& policy = {});

}  // namespace anonsync::persistence
