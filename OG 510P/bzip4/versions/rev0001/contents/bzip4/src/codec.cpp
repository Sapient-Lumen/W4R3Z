#include "bzip4/codec.hpp"

#include <algorithm>
#include <limits>
#include <utility>

namespace bzip4 {

codec_error::codec_error(const int code, std::string message)
    : std::runtime_error(std::move(message)), code_(code) {}

int codec_error::code() const noexcept { return code_; }

block_codec::block_codec(const std::int32_t block_size) : block_size_(block_size) {
    if (block_size < min_block_size || block_size > max_block_size) {
        throw codec_error(BZ3_ERR_INIT, "bzip4: block size must be between 65 KiB and 511 MiB");
    }
    buffer_capacity_ = bz3_bound(static_cast<std::size_t>(block_size));
    state_ = bz3_new(block_size);
    if (state_ == nullptr) {
        throw codec_error(BZ3_ERR_INIT, "bzip4: failed to allocate codec state");
    }
}

block_codec::~block_codec() noexcept {
    if (state_ != nullptr) bz3_free(state_);
}

block_codec::block_codec(block_codec&& other) noexcept
    : state_(std::exchange(other.state_, nullptr)),
      block_size_(std::exchange(other.block_size_, 0)),
      buffer_capacity_(std::exchange(other.buffer_capacity_, 0)) {}

block_codec& block_codec::operator=(block_codec&& other) noexcept {
    if (this != &other) {
        if (state_ != nullptr) bz3_free(state_);
        state_ = std::exchange(other.state_, nullptr);
        block_size_ = std::exchange(other.block_size_, 0);
        buffer_capacity_ = std::exchange(other.buffer_capacity_, 0);
    }
    return *this;
}

std::int32_t block_codec::block_size() const noexcept { return block_size_; }
std::size_t block_codec::buffer_capacity() const noexcept { return buffer_capacity_; }

std::vector<std::uint8_t> block_codec::encode(const std::span<const std::uint8_t> input) {
    if (state_ == nullptr) {
        throw codec_error(BZ3_ERR_INIT, "bzip4: encode called on a moved-from codec");
    }
    if (input.empty()) {
        return {};
    }
    if (input.size() > static_cast<std::size_t>(block_size_) ||
        input.size() > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max())) {
        throw codec_error(BZ3_ERR_DATA_TOO_BIG, "bzip4: input does not fit in one configured block");
    }

    std::vector<std::uint8_t> buffer(buffer_capacity_);
    std::copy(input.begin(), input.end(), buffer.begin());
    const auto result = bz3_encode_block(state_, buffer.data(), static_cast<std::int32_t>(input.size()));
    if (result < 0) {
        throw_last_error("encode");
    }
    buffer.resize(static_cast<std::size_t>(result));
    return buffer;
}

std::vector<std::uint8_t> block_codec::decode(const std::span<const std::uint8_t> compressed,
                                               const std::size_t original_size) {
    if (state_ == nullptr) {
        throw codec_error(BZ3_ERR_INIT, "bzip4: decode called on a moved-from codec");
    }
    if (compressed.empty() && original_size == 0) {
        return {};
    }
    if (compressed.size() > buffer_capacity_ || original_size > static_cast<std::size_t>(block_size_) ||
        compressed.size() > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max()) ||
        original_size > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max())) {
        throw codec_error(BZ3_ERR_DATA_TOO_BIG, "bzip4: encoded or decoded block exceeds configured capacity");
    }

    std::vector<std::uint8_t> buffer(buffer_capacity_);
    std::copy(compressed.begin(), compressed.end(), buffer.begin());
    const auto result = bz3_decode_block(state_, buffer.data(), buffer.size(),
                                         static_cast<std::int32_t>(compressed.size()),
                                         static_cast<std::int32_t>(original_size));
    if (result < 0) {
        throw_last_error("decode");
    }
    if (static_cast<std::size_t>(result) != original_size) {
        throw codec_error(BZ3_ERR_MALFORMED_HEADER, "bzip4: decoded block size differs from the requested original size");
    }
    buffer.resize(static_cast<std::size_t>(result));
    return buffer;
}

void block_codec::throw_last_error(const char* operation) const {
    const int code = state_ == nullptr ? BZ3_ERR_INIT : bz3_last_error(state_);
    const char* detail = state_ == nullptr ? "invalid state" : bz3_strerror(state_);
    throw codec_error(code, std::string("bzip4: ") + operation + " failed: " + detail);
}

const char* codec_version() noexcept { return bz3_version(); }

} // namespace bzip4
