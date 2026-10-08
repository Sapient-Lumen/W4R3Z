#pragma once

#include <cstdint>
#include <filesystem>
#include <string>

namespace anonsync {

// Reads one exact, bounded regular-file observation from an opened object.
// Embedded NUL path elements are rejected, and the final path component must
// not be a symbolic link or other reparse point.
// On POSIX, nonblocking open flags prevent a raced FIFO/device replacement from
// blocking before the descriptor can be type-checked. The implementation reads
// through EOF, enforces the byte ceiling with a one-byte sentinel, and rejects
// size or modification-metadata changes observed across the read.
std::string read_sync_bounded_regular_file_no_symlink_or_throw(
    const std::filesystem::path& path,
    std::uint64_t maximum_bytes,
    const std::string& label);

// Stronger authority boundary for mutable ledgers, journals, receipts, and
// lock records whose selected namespace object must have no writable alias.
// In addition to the exact bounded observation above, the opened object must
// have exactly one filesystem link before and after the read.
std::string read_sync_bounded_single_link_regular_file_no_symlink_or_throw(
    const std::filesystem::path& path,
    std::uint64_t maximum_bytes,
    const std::string& label);

// Secret-bearing configuration has a stronger admission boundary. On POSIX,
// the opened descriptor must be a stable single-link regular file owned by the
// effective user with exact mode 0600 before and after the bounded read. The
// current Windows implementation fails closed because it does not yet prove an
// equivalent owner-only DACL.
std::string read_sync_bounded_private_regular_file_no_symlink_or_throw(
    const std::filesystem::path& path,
    std::uint64_t maximum_bytes,
    const std::string& label);

}  // namespace anonsync
