#pragma once

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>
#include <vector>

namespace bzip4 {

/**
 * Descriptor-pinned, read-only regular-file input.
 *
 * The path is resolved once with O_NOFOLLOW and all reads use the retained file
 * descriptor. The initial device, inode, size, mtime, and ctime form a snapshot
 * fingerprint. require_unchanged() detects ordinary truncation, growth, and
 * in-place mutation that occurs while a caller is reading the descriptor.
 * Replacing the path after open does not redirect reads away from the pinned
 * inode.
 */
class PinnedFile final {
public:
    explicit PinnedFile(const std::filesystem::path& path);
    ~PinnedFile();

    PinnedFile(const PinnedFile&) = delete;
    PinnedFile& operator=(const PinnedFile&) = delete;
    PinnedFile(PinnedFile&&) = delete;
    PinnedFile& operator=(PinnedFile&&) = delete;

    [[nodiscard]] std::uint64_t size() const noexcept;

    /** Read exactly within the initial file-size boundary. */
    [[nodiscard]] bool read_exact(
        std::uint64_t offset,
        std::span<std::byte> output) const noexcept;

    /** Read exactly or throw on an invalid range, short read, or I/O error. */
    void read_into(
        std::uint64_t offset,
        std::span<std::byte> output) const;

    /** Read an owned range or throw on a short/erroring read. */
    [[nodiscard]] std::vector<std::byte> read(
        std::uint64_t offset,
        std::size_t size) const;

    /** Read the complete initial file and then require a stable fingerprint. */
    [[nodiscard]] std::vector<std::byte> read_all() const;

    /** Return false on fingerprint mismatch or a failed re-stat. */
    [[nodiscard]] bool unchanged() const noexcept;

    /** Throw when the descriptor fingerprint no longer matches its open state. */
    void require_unchanged() const;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace bzip4
