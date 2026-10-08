#include "sqlite_snapshot_geometry.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <limits>

namespace {

using anonsync::persistence::SqliteSnapshotGeometryPolicy;
using anonsync::persistence::kMaximumUntrustedSqliteSnapshotBytes;
using anonsync::persistence::kMaximumUntrustedSqliteSnapshotPages;
using anonsync::persistence::kSqliteDatabaseHeaderBytes;
using anonsync::persistence::verify_sqlite_snapshot_geometry_or_throw;

std::uint64_t read_u64(const std::uint8_t* data,
                       std::size_t size,
                       std::size_t offset) noexcept {
    std::uint64_t value = 0;
    for (std::size_t index = 0; index < 8U && offset + index < size; ++index) {
        value |= static_cast<std::uint64_t>(data[offset + index]) << (index * 8U);
    }
    return value;
}

std::uint32_t read_be32(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    std::size_t offset) noexcept {
    return (static_cast<std::uint32_t>(header[offset]) << 24U) |
           (static_cast<std::uint32_t>(header[offset + 1U]) << 16U) |
           (static_cast<std::uint32_t>(header[offset + 2U]) << 8U) |
           static_cast<std::uint32_t>(header[offset + 3U]);
}

void put_be16(
    std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    std::size_t offset,
    std::uint16_t value) noexcept {
    header[offset] = static_cast<unsigned char>((value >> 8U) & 0xffU);
    header[offset + 1U] = static_cast<unsigned char>(value & 0xffU);
}

void put_be32(
    std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header,
    std::size_t offset,
    std::uint32_t value) noexcept {
    header[offset] = static_cast<unsigned char>((value >> 24U) & 0xffU);
    header[offset + 1U] = static_cast<unsigned char>((value >> 16U) & 0xffU);
    header[offset + 2U] = static_cast<unsigned char>((value >> 8U) & 0xffU);
    header[offset + 3U] = static_cast<unsigned char>(value & 0xffU);
}

std::uint32_t decoded_page_size(
    const std::array<unsigned char, kSqliteDatabaseHeaderBytes>& header) noexcept {
    const std::uint16_t encoded = static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(header[16]) << 8U) |
        static_cast<std::uint16_t>(header[17]));
    return encoded == 1U ? 65536U : static_cast<std::uint32_t>(encoded);
}

[[noreturn]] void invariant_failure() noexcept {
    std::abort();
}

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data,
                                      std::size_t size) {
    std::array<unsigned char, kSqliteDatabaseHeaderBytes> header{};
    const std::size_t header_bytes =
        size < header.size() ? size : header.size();
    for (std::size_t index = 0; index < header_bytes; ++index) {
        header[index] = data[index];
    }

    const std::uint8_t mode = size > 108U ? data[108U] : 0U;
    std::uint64_t exact_bytes = read_u64(data, size, 100U);
    if ((mode & 0x80U) != 0U) {
        constexpr std::array<unsigned char, 16> magic{
            'S', 'Q', 'L', 'i', 't', 'e', ' ', 'f',
            'o', 'r', 'm', 'a', 't', ' ', '3', 0};
        for (std::size_t index = 0; index < magic.size(); ++index) {
            header[index] = magic[index];
        }
        const std::uint32_t exponent =
            9U + static_cast<std::uint32_t>(size > 109U ? data[109U] % 8U : 0U);
        const std::uint32_t page_size = 1U << exponent;
        put_be16(header, 16U,
                 page_size == 65536U
                     ? 1U
                     : static_cast<std::uint16_t>(page_size));
        const std::uint32_t counter = read_be32(header, 36U);
        const std::uint32_t page_count =
            (read_be32(header, 32U) % 64U) + 1U;
        put_be32(header, 24U, counter);
        put_be32(header, 28U, page_count);
        put_be32(header, 92U, counter);
        exact_bytes = static_cast<std::uint64_t>(page_size) * page_count;
    } else if ((mode & 0x01U) != 0U) {
        exact_bytes = static_cast<std::uint64_t>(decoded_page_size(header)) *
                      static_cast<std::uint64_t>(read_be32(header, 28U));
    }

    SqliteSnapshotGeometryPolicy policy;
    if ((mode & 0x02U) != 0U) {
        policy.maximum_bytes =
            (read_u64(data, size, 109U) % kMaximumUntrustedSqliteSnapshotBytes) +
            1U;
    }
    if ((mode & 0x04U) != 0U) {
        policy.maximum_pages =
            (read_be32(header, 32U) % kMaximumUntrustedSqliteSnapshotPages) + 1U;
    }
    if ((mode & 0x08U) != 0U) {
        policy.maximum_bytes = kMaximumUntrustedSqliteSnapshotBytes + 1U;
    }
    if ((mode & 0x10U) != 0U) {
        policy.maximum_pages = kMaximumUntrustedSqliteSnapshotPages + 1U;
    }
    if ((mode & 0x20U) != 0U) policy.maximum_bytes = 0U;
    if ((mode & 0x40U) != 0U) policy.maximum_pages = 0U;

    try {
        const auto geometry = verify_sqlite_snapshot_geometry_or_throw(
            header, exact_bytes, "fuzz geometry", policy);
        if (geometry.byte_count != exact_bytes || geometry.page_size < 512U ||
            geometry.page_size > 65536U || geometry.page_count == 0U ||
            static_cast<std::uint64_t>(geometry.page_size) *
                    static_cast<std::uint64_t>(geometry.page_count) !=
                geometry.byte_count ||
            geometry.byte_count > policy.maximum_bytes ||
            static_cast<std::uint64_t>(geometry.page_count) >
                policy.maximum_pages ||
            policy.maximum_bytes > kMaximumUntrustedSqliteSnapshotBytes ||
            policy.maximum_pages > kMaximumUntrustedSqliteSnapshotPages) {
            invariant_failure();
        }
    } catch (const std::exception&) {
        // Rejection is the expected result for almost all arbitrary headers.
    }
    return 0;
}
