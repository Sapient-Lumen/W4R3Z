#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>

namespace bzip4 {

class Sha256 final {
public:
    Sha256();
    void update(std::span<const std::byte> data);
    [[nodiscard]] std::array<std::byte, 32> finish();

private:
    void transform(const std::byte* block);
    std::array<std::uint32_t, 8> state_{};
    std::array<std::byte, 64> buffer_{};
    std::uint64_t total_bytes_{};
    std::size_t buffered_{};
    bool finished_{};
};

[[nodiscard]] std::string hex_sha256(std::span<const std::byte> data);
[[nodiscard]] std::string hex_sha256_file(const std::filesystem::path& path);

} // namespace bzip4
