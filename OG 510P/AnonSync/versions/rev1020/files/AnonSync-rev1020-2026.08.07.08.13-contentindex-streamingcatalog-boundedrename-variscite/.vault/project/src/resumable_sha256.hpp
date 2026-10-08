#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <string>
#include <string_view>

namespace anonsync {

// SHA-256 encodes the message length in one unsigned 64-bit bit count. The
// largest byte-aligned message accepted by the standard is therefore 2^61-1
// bytes. Payload ceilings and resumable checkpoints must reject larger extents
// rather than silently wrapping the terminal length field.
inline constexpr std::uint64_t kSha256MaximumMessageBytes =
    (std::numeric_limits<std::uint64_t>::max)() / 8U;

// Stable provider-independent continuation state for a byte-aligned SHA-256
// message. This is computation progress, not a digest proof: callers must
// validate the final digest against an independently trusted expected value.
// Unused buffered bytes are canonical zeroes so the state has one encoding.
struct ResumableSha256Checkpoint final {
    std::array<std::uint32_t, 8U> hash_words{};
    std::array<std::uint8_t, 64U> buffered_block{};
    std::uint64_t total_bytes = 0U;
    std::uint32_t buffered_bytes = 0U;

    bool operator==(const ResumableSha256Checkpoint&) const = default;
};

void validate_resumable_sha256_checkpoint_or_throw(
    const ResumableSha256Checkpoint& checkpoint,
    std::string_view label);

// A small FIPS 180-4 SHA-256 implementation whose exact continuation state can
// be durably serialized. The ordinary sha256_digest owner remains OpenSSL EVP;
// focused tests continuously compare this implementation with that independent
// provider-backed oracle. finish_hex() consumes the builder.
class ResumableSha256 final {
public:
    ResumableSha256();
    explicit ResumableSha256(
        ResumableSha256Checkpoint checkpoint,
        std::string_view label = "resumable SHA-256 checkpoint");

    void update(std::string_view bytes);
    [[nodiscard]] ResumableSha256Checkpoint checkpoint() const;
    // Fixed-width binary and canonical hex are the allocation-free terminal
    // forms. finish_hex() is the owning convenience form.
    [[nodiscard]] std::array<std::uint8_t, 32U> finish_binary_array();
    [[nodiscard]] std::array<char, 64U> finish_hex_array();
    [[nodiscard]] std::string finish_hex();

private:
    void process_block(const std::uint8_t* block);
    void require_updateable_or_throw() const;

    ResumableSha256Checkpoint state_;
    bool finished_ = false;
};

}  // namespace anonsync
