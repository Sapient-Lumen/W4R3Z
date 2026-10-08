#include "sqlite_snapshot_geometry.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <stdexcept>
#include <string>

namespace anonsync::persistence {
namespace {

constexpr std::array<unsigned char, 16> kSqliteMagic{
    'S', 'Q', 'L', 'i', 't', 'e', ' ', 'f',
    'o', 'r', 'm', 'a', 't', ' ', '3', 0};

std::uint16_t read_be16(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& bytes,
    std::size_t offset) noexcept {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
        static_cast<std::uint16_t>(bytes[offset + 1U]));
}

std::uint32_t read_be32(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& bytes,
    std::size_t offset) noexcept {
    return (static_cast<std::uint32_t>(bytes[offset]) << 24U) |
           (static_cast<std::uint32_t>(bytes[offset + 1U]) << 16U) |
           (static_cast<std::uint32_t>(bytes[offset + 2U]) << 8U) |
           static_cast<std::uint32_t>(bytes[offset + 3U]);
}

bool is_power_of_two(std::uint32_t value) noexcept {
    return value != 0U && (value & (value - 1U)) == 0U;
}

std::string diagnostic_prefix(std::string_view label) {
    if (label.empty()) {
        throw std::runtime_error(
            "SQLite snapshot geometry requires a nonempty diagnostic label");
    }
    return std::string(label);
}

}  // namespace

void validate_sqlite_snapshot_geometry_policy_or_throw(
    const SqliteSnapshotGeometryPolicy& policy,
    std::string_view label_view) {
    const std::string label = diagnostic_prefix(label_view);
    if (policy.maximum_bytes == 0U || policy.maximum_pages == 0U) {
        throw std::runtime_error(
            label + " SQLite snapshot geometry policy has a zero ceiling");
    }
    if (policy.maximum_bytes > kMaximumUntrustedSqliteSnapshotBytes ||
        policy.maximum_pages > kMaximumUntrustedSqliteSnapshotPages) {
        throw std::runtime_error(
            label +
            " SQLite snapshot geometry policy may tighten but not widen the reviewed ceiling");
    }
}

SqliteSnapshotGeometry verify_sqlite_snapshot_page_geometry_or_throw(
    std::uint64_t page_size_value,
    std::uint64_t page_count_value,
    std::string_view label_view,
    const SqliteSnapshotGeometryPolicy& policy) {
    const std::string label = diagnostic_prefix(label_view);
    validate_sqlite_snapshot_geometry_policy_or_throw(policy, label);

    if (page_size_value < 512U || page_size_value > 65536U ||
        !is_power_of_two(static_cast<std::uint32_t>(page_size_value))) {
        throw std::runtime_error(
            label + " SQLite snapshot has an invalid database page size");
    }
    if (page_count_value == 0U) {
        throw std::runtime_error(
            label + " SQLite snapshot has a zero page count");
    }
    if (page_count_value > policy.maximum_pages) {
        throw std::runtime_error(
            label + " SQLite snapshot exceeds the page ceiling");
    }
    if (page_count_value >
        static_cast<std::uint64_t>(std::numeric_limits<std::uint32_t>::max())) {
        throw std::runtime_error(
            label + " SQLite snapshot page count exceeds header addressability");
    }
    if (page_size_value >
        std::numeric_limits<std::uint64_t>::max() / page_count_value) {
        throw std::runtime_error(
            label + " SQLite snapshot geometry multiplication overflow");
    }
    const std::uint64_t byte_count = page_size_value * page_count_value;
    if (byte_count > policy.maximum_bytes) {
        throw std::runtime_error(
            label + " SQLite snapshot exceeds the byte ceiling");
    }
    if (byte_count >
        static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        throw std::runtime_error(
            label + " SQLite snapshot exceeds process addressability");
    }

    return SqliteSnapshotGeometry{
        byte_count,
        static_cast<std::uint32_t>(page_size_value),
        static_cast<std::uint32_t>(page_count_value),
    };
}

SqliteSnapshotGeometry verify_sqlite_snapshot_geometry_or_throw(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    std::uint64_t exact_file_bytes,
    std::string_view label_view,
    const SqliteSnapshotGeometryPolicy& policy) {
    const std::string label = diagnostic_prefix(label_view);
    validate_sqlite_snapshot_geometry_policy_or_throw(policy, label);

    if (exact_file_bytes < kSqliteDatabaseHeaderBytes) {
        throw std::runtime_error(
            label + " SQLite snapshot is shorter than its 100-byte header");
    }
    if (exact_file_bytes > policy.maximum_bytes) {
        throw std::runtime_error(
            label + " SQLite snapshot exceeds the byte ceiling");
    }
    if (!std::equal(kSqliteMagic.begin(), kSqliteMagic.end(), header.begin())) {
        throw std::runtime_error(
            label + " SQLite snapshot has an invalid database header magic");
    }

    const std::uint16_t encoded_page_size = read_be16(header, 16U);
    const std::uint32_t page_size =
        encoded_page_size == 1U ? 65536U
                                : static_cast<std::uint32_t>(encoded_page_size);
    if (page_size == 65536U && encoded_page_size != 1U) {
        throw std::runtime_error(
            label + " SQLite snapshot has an invalid database page size");
    }

    // SQLite defines the in-header database size as valid only when the file
    // change counter (offset 24) equals version-valid-for (offset 92).  A
    // mismatch means the page count is stale evidence and cannot authorize an
    // exact byte-to-page mapping.
    const std::uint32_t file_change_counter = read_be32(header, 24U);
    const std::uint32_t version_valid_for = read_be32(header, 92U);
    if (file_change_counter != version_valid_for) {
        throw std::runtime_error(
            label + " SQLite snapshot header page count is stale");
    }

    const std::uint32_t page_count = read_be32(header, 28U);
    SqliteSnapshotGeometry geometry =
        verify_sqlite_snapshot_page_geometry_or_throw(
            page_size, page_count, label, policy);
    if (geometry.byte_count != exact_file_bytes) {
        throw std::runtime_error(
            label +
            " SQLite snapshot header page count does not match exact file bytes");
    }
    return geometry;
}

}  // namespace anonsync::persistence
