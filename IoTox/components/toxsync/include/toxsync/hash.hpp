#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <string_view>

namespace toxsync {

struct Hash128 {
    std::uint64_t lo{};
    std::uint64_t hi{};
    friend constexpr bool operator==(const Hash128&, const Hash128&) = default;
};

struct Digest256 {
    std::array<std::byte, 32> bytes{};
    friend constexpr bool operator==(const Digest256&, const Digest256&) = default;
    [[nodiscard]] std::string hex() const;
    [[nodiscard]] static Digest256 from_hex(const std::string& text);
};

[[nodiscard]] Hash128 fast_hash128(std::span<const std::byte> bytes) noexcept;

class Sha256 final {
public:
    Sha256() noexcept;
    void update(std::span<const std::byte> bytes) noexcept;
    [[nodiscard]] Digest256 finish() noexcept;

private:
    void transform(const std::byte* block) noexcept;
    std::array<std::uint32_t, 8> state_{};
    std::array<std::byte, 64> buffer_{};
    std::uint64_t total_bytes_{};
    std::size_t buffered_{};
    bool finished_{};
};

[[nodiscard]] Digest256 sha256(std::span<const std::byte> bytes);
[[nodiscard]] Digest256 sha256_file(const std::string& path);
[[nodiscard]] std::string_view sha256_backend_name() noexcept;

} // namespace toxsync
