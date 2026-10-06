#pragma once

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>

namespace bzip4 {

/**
 * A same-directory, descriptor-pinned atomic file publisher.
 *
 * Bytes are written to a private O_EXCL temporary file in the destination's
 * parent directory. commit() flushes and closes that file, renames it over the
 * destination through the pinned directory descriptor, and flushes the parent
 * directory. Destruction before publication closes and removes the temporary.
 *
 * A commit error before rename leaves the destination untouched. A parent
 * directory fsync error occurs after rename and therefore means the new name is
 * visible but its crash durability could not be confirmed.
 */
class AtomicFileWriter final {
public:
    explicit AtomicFileWriter(
        const std::filesystem::path& destination,
        std::uint32_t permissions = 0600U);
    ~AtomicFileWriter();

    AtomicFileWriter(const AtomicFileWriter&) = delete;
    AtomicFileWriter& operator=(const AtomicFileWriter&) = delete;
    AtomicFileWriter(AtomicFileWriter&&) = delete;
    AtomicFileWriter& operator=(AtomicFileWriter&&) = delete;

    void write(std::span<const std::byte> bytes);
    void commit();

    [[nodiscard]] std::uint64_t bytes_written() const noexcept;
    [[nodiscard]] bool published() const noexcept;
    [[nodiscard]] bool durable() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace bzip4
