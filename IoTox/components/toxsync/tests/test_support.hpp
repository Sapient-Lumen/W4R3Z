#pragma once

#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <random>
#include <span>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace test {
class TempDir final {
public:
    TempDir() {
        static std::atomic<std::uint64_t> sequence{1U};
        const auto base = std::filesystem::temp_directory_path();
        std::random_device entropy;
        const auto salt =
            (static_cast<std::uint64_t>(entropy()) << 32U) ^ entropy();
        for (std::size_t attempt = 0U; attempt < 128U; ++attempt) {
            const auto stamp = static_cast<std::uint64_t>(
                std::chrono::steady_clock::now().time_since_epoch().count());
            const auto number = sequence.fetch_add(1U);
            auto candidate = base /
                ("toxsync-test-" + std::to_string(stamp) + "-" +
                 std::to_string(salt) + "-" + std::to_string(number));
            std::error_code error;
            if (std::filesystem::create_directory(candidate, error)) {
                std::filesystem::permissions(
                    candidate, std::filesystem::perms::owner_all,
                    std::filesystem::perm_options::replace, error);
                if (error) {
                    std::filesystem::remove_all(candidate, error);
                    throw std::runtime_error(
                        "cannot make toxsync test directory private");
                }
                path_ = std::move(candidate);
                return;
            }
            if (error && error != std::errc::file_exists) {
                throw std::runtime_error(
                    "cannot create toxsync test directory: " +
                    error.message());
            }
        }
        throw std::runtime_error("cannot allocate toxsync test directory");
    }
    ~TempDir() { std::error_code ignored; std::filesystem::remove_all(path_, ignored); }
    const std::filesystem::path& path() const noexcept { return path_; }
private:
    std::filesystem::path path_;
};

inline void write_file(const std::filesystem::path& path, std::span<const std::byte> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create test file");
    output.write(reinterpret_cast<const char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    if (!output) throw std::runtime_error("cannot write test file");
}

inline std::vector<std::byte> read_file(const std::filesystem::path& path) {
    const auto size = std::filesystem::file_size(path);
    std::vector<std::byte> bytes(static_cast<std::size_t>(size));
    std::ifstream input(path, std::ios::binary);
    input.read(reinterpret_cast<char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    if (static_cast<std::size_t>(input.gcount()) != bytes.size()) throw std::runtime_error("cannot read test file");
    return bytes;
}

inline std::vector<std::byte> pattern(std::size_t size, std::uint64_t seed) {
    std::vector<std::byte> bytes(size);
    std::uint64_t value = seed;
    for (auto& byte : bytes) {
        value ^= value << 13U;
        value ^= value >> 7U;
        value ^= value << 17U;
        byte = static_cast<std::byte>(value & 0xffU);
    }
    return bytes;
}
} // namespace test
