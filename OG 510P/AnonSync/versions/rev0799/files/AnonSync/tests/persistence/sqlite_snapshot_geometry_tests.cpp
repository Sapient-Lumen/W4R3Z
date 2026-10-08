#include "sqlite_snapshot_geometry.hpp"

#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

using anonsync::persistence::SqliteSnapshotGeometryPolicy;
using anonsync::persistence::kMaximumUntrustedSqliteSnapshotBytes;
using anonsync::persistence::kMaximumUntrustedSqliteSnapshotPages;
using anonsync::persistence::kSqliteDatabaseHeaderBytes;
using anonsync::persistence::verify_sqlite_snapshot_geometry_or_throw;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void put_be16(std::array<unsigned char, kSqliteDatabaseHeaderBytes>& bytes,
              std::size_t offset,
              std::uint16_t value) {
    bytes[offset] = static_cast<unsigned char>((value >> 8U) & 0xffU);
    bytes[offset + 1U] = static_cast<unsigned char>(value & 0xffU);
}

void put_be32(std::array<unsigned char, kSqliteDatabaseHeaderBytes>& bytes,
              std::size_t offset,
              std::uint32_t value) {
    bytes[offset] = static_cast<unsigned char>((value >> 24U) & 0xffU);
    bytes[offset + 1U] = static_cast<unsigned char>((value >> 16U) & 0xffU);
    bytes[offset + 2U] = static_cast<unsigned char>((value >> 8U) & 0xffU);
    bytes[offset + 3U] = static_cast<unsigned char>(value & 0xffU);
}

std::array<unsigned char, kSqliteDatabaseHeaderBytes> make_header(
    std::uint32_t page_size,
    std::uint32_t page_count,
    std::uint32_t file_change_counter = 7U,
    std::uint32_t version_valid_for = 7U) {
    std::array<unsigned char, kSqliteDatabaseHeaderBytes> header{};
    constexpr std::array<unsigned char, 16> magic{
        'S', 'Q', 'L', 'i', 't', 'e', ' ', 'f',
        'o', 'r', 'm', 'a', 't', ' ', '3', 0};
    for (std::size_t index = 0; index < magic.size(); ++index) {
        header[index] = magic[index];
    }
    put_be16(header, 16U,
             page_size == 65536U ? 1U : static_cast<std::uint16_t>(page_size));
    put_be32(header, 24U, file_change_counter);
    put_be32(header, 28U, page_count);
    put_be32(header, 92U, version_valid_for);
    return header;
}

template <typename Callable>
void expect_rejection(Callable&& callable,
                      const std::string& fragment,
                      std::uint64_t& checks) {
    bool rejected = false;
    std::string reason;
    try {
        callable();
    } catch (const std::exception& error) {
        rejected = true;
        reason = error.what();
    }
    require(rejected, "expected geometry rejection did not occur", checks);
    require(reason.find(fragment) != std::string::npos,
            "unexpected geometry rejection: " + reason, checks);
}

void test_valid_geometry(std::uint64_t& checks) {
    const auto ordinary = verify_sqlite_snapshot_geometry_or_throw(
        make_header(4096U, 3U), 3ULL * 4096ULL, "ordinary geometry");
    require(ordinary.byte_count == 12288U, "ordinary byte count mismatch", checks);
    require(ordinary.page_size == 4096U, "ordinary page size mismatch", checks);
    require(ordinary.page_count == 3U, "ordinary page count mismatch", checks);

    const auto maximum_page_size = verify_sqlite_snapshot_geometry_or_throw(
        make_header(65536U, 2U), 2ULL * 65536ULL, "64KiB geometry");
    require(maximum_page_size.page_size == 65536U,
            "special 64KiB page-size encoding was not decoded", checks);
    require(maximum_page_size.page_count == 2U,
            "64KiB page count mismatch", checks);
}

void test_header_truth(std::uint64_t& checks) {
    auto invalid_magic = make_header(4096U, 1U);
    invalid_magic[0] = 'X';
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                invalid_magic, 4096U, "invalid magic");
        },
        "invalid database header magic", checks);

    auto invalid_page_size = make_header(4096U, 1U);
    put_be16(invalid_page_size, 16U, 513U);
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                invalid_page_size, 4096U, "invalid page size");
        },
        "invalid database page size", checks);

    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                make_header(4096U, 0U), 4096U, "zero page count");
        },
        "zero page count", checks);

    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                make_header(4096U, 1U, 8U, 7U), 4096U,
                "stale page count");
        },
        "header page count is stale", checks);
}

void test_exact_extent_binding(std::uint64_t& checks) {
    const auto header = make_header(4096U, 2U);
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 3ULL * 4096ULL, "trailing page");
        },
        "does not match exact file bytes", checks);
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 2ULL * 4096ULL + 1ULL, "trailing byte");
        },
        "does not match exact file bytes", checks);
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 2ULL * 4096ULL - 1ULL, "truncated page");
        },
        "does not match exact file bytes", checks);
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 99U, "short header");
        },
        "shorter than its 100-byte header", checks);
}

void test_monotone_policy(std::uint64_t& checks) {
    const auto header = make_header(512U, 2U);

    SqliteSnapshotGeometryPolicy zero_bytes;
    zero_bytes.maximum_bytes = 0U;
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 1024U, "zero bytes", zero_bytes);
        },
        "zero ceiling", checks);

    SqliteSnapshotGeometryPolicy zero_pages;
    zero_pages.maximum_pages = 0U;
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 1024U, "zero pages", zero_pages);
        },
        "zero ceiling", checks);

    SqliteSnapshotGeometryPolicy widened_bytes;
    widened_bytes.maximum_bytes = kMaximumUntrustedSqliteSnapshotBytes + 1U;
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 1024U, "widened bytes", widened_bytes);
        },
        "may tighten but not widen", checks);

    SqliteSnapshotGeometryPolicy widened_pages;
    widened_pages.maximum_pages = kMaximumUntrustedSqliteSnapshotPages + 1U;
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 1024U, "widened pages", widened_pages);
        },
        "may tighten but not widen", checks);

    SqliteSnapshotGeometryPolicy tight_bytes;
    tight_bytes.maximum_bytes = 1023U;
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 1024U, "tight bytes", tight_bytes);
        },
        "exceeds the byte ceiling", checks);

    SqliteSnapshotGeometryPolicy tight_pages;
    tight_pages.maximum_pages = 1U;
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                header, 1024U, "tight pages", tight_pages);
        },
        "exceeds the page ceiling", checks);

    const std::uint32_t excessive_pages =
        static_cast<std::uint32_t>(kMaximumUntrustedSqliteSnapshotPages + 1U);
    expect_rejection(
        [&] {
            (void)verify_sqlite_snapshot_geometry_or_throw(
                make_header(512U, excessive_pages),
                static_cast<std::uint64_t>(excessive_pages) * 512ULL,
                "hard page ceiling");
        },
        "exceeds the page ceiling", checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        test_valid_geometry(checks);
        test_header_truth(checks);
        test_exact_extent_binding(checks);
        test_monotone_policy(checks);
        std::cout << "anonsync sqlite snapshot geometry tests checks=" << checks
                  << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "anonsync sqlite snapshot geometry test failed after "
                  << checks << " checks: " << error.what() << "\n";
        return 1;
    }
}
