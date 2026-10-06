#pragma once

#include "bzip4/libbz3.hpp"

#include <cstddef>
#include <cstdint>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

namespace bzip4 {

class codec_error final : public std::runtime_error {
public:
    codec_error(int code, std::string message);
    [[nodiscard]] int code() const noexcept;

private:
    int code_;
};

class block_codec final {
public:
    static constexpr std::int32_t min_block_size = 65 * 1024;
    static constexpr std::int32_t max_block_size = 511 * 1024 * 1024;

    explicit block_codec(std::int32_t block_size);
    ~block_codec() noexcept;

    block_codec(const block_codec&) = delete;
    block_codec& operator=(const block_codec&) = delete;

    block_codec(block_codec&& other) noexcept;
    block_codec& operator=(block_codec&& other) noexcept;

    [[nodiscard]] std::int32_t block_size() const noexcept;
    [[nodiscard]] std::size_t buffer_capacity() const noexcept;

    [[nodiscard]] std::vector<std::uint8_t>
    encode(std::span<const std::uint8_t> input);

    [[nodiscard]] std::vector<std::uint8_t>
    decode(std::span<const std::uint8_t> compressed, std::size_t original_size);

private:
    void throw_last_error(const char* operation) const;

    bz3_state* state_ = nullptr;
    std::int32_t block_size_ = 0;
    std::size_t buffer_capacity_ = 0;
};

[[nodiscard]] const char* codec_version() noexcept;

} // namespace bzip4
