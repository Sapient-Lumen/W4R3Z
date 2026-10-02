#pragma once

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>

namespace toxsync {

struct RangeRead {
    std::uint64_t offset{};
    std::span<std::byte> output{};
};

class RangeSource {
public:
    virtual ~RangeSource() = default;
    virtual std::size_t read_at(std::uint64_t offset, std::span<std::byte> output) = 0;

    // Exact-fill batch hook. The default implementation is serial and uses
    // read_at(); a Tox adapter may override it to schedule a bounded number of
    // logical range lanes over one peer connection.
    virtual void read_many(std::span<RangeRead> reads);
};

class FileRangeSource final : public RangeSource {
public:
    explicit FileRangeSource(const std::filesystem::path& path);
    ~FileRangeSource() override;
    FileRangeSource(FileRangeSource&&) noexcept;
    FileRangeSource& operator=(FileRangeSource&&) noexcept;
    FileRangeSource(const FileRangeSource&) = delete;
    FileRangeSource& operator=(const FileRangeSource&) = delete;

    std::size_t read_at(std::uint64_t offset, std::span<std::byte> output) override;

private:
    class Impl;
    Impl* impl_{};
};

} // namespace toxsync
