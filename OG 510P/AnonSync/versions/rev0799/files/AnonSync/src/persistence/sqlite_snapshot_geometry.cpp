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

void validate_policy_or_throw(const SqliteSnapshotGeometryPolicy& policy,
                              const std::string& label) {
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

}  // namespace

SqliteSnapshotGeometry verify_sqlite_snapshot_geometry_or_throw(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    std::uint64_t exact_file_bytes,
    std::string_view label_view,
    const SqliteSnapshotGeometryPolicy& policy) {
    const std::string label = diagnostic_prefix(label_view);
    validate_policy_or_throw(policy, label);

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
    if (page_size < 512U || page_size > 65536U ||
        !is_power_of_two(page_size) ||
        (page_size == 65536U && encoded_page_size != 1U)) {
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
    if (page_count == 0U) {
        throw std::runtime_error(
            label + " SQLite snapshot header has a zero page count");
    }
    if (static_cast<std::uint64_t>(page_count) > policy.maximum_pages) {
        throw std::runtime_error(
            label + " SQLite snapshot exceeds the page ceiling");
    }

    const std::uint64_t logical_bytes =
        static_cast<std::uint64_t>(page_count) *
        static_cast<std::uint64_t>(page_size);
    if (logical_bytes != exact_file_bytes) {
        throw std::runtime_error(
            label +
            " SQLite snapshot header page count does not match exact file bytes");
    }

    return SqliteSnapshotGeometry{
        exact_file_bytes,
        page_size,
        page_count,
    };
}

}  // namespace anonsync::persistence
