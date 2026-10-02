#pragma once

#include "iotox/mutorr/id.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace iotox::mutorr {

inline constexpr std::uint8_t kHeadWireVersion = 1U;
inline constexpr std::size_t kSignatureSize = 64U;
inline constexpr std::size_t kHeadSigningSize = 157U;
inline constexpr std::size_t kHeadWireSize = kHeadSigningSize + kSignatureSize;

struct HeadRecord {
    std::uint8_t wire_version{kHeadWireVersion};
    Id256 namespace_id{};
    Id256 writer_key{};
    std::uint64_t generation{1U};
    Id256 root{};
    Id256 previous{};
    std::uint64_t created_unix_ms{0U};
    std::uint64_t content_bytes{0U};
    std::uint32_t object_count{0U};
    std::array<std::uint8_t, kSignatureSize> signature{};

    friend bool operator==(const HeadRecord &, const HeadRecord &) = default;
};

enum class HeadDecision {
    accept_initial,
    accept_advance,
    duplicate,
    stale,
    conflict,
    requires_history,
    different_stream,
    invalid,
};

[[nodiscard]] Status validate_head(const HeadRecord &head);
[[nodiscard]] Result<std::vector<std::uint8_t>> head_signing_bytes(const HeadRecord &head);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_head(const HeadRecord &head);
[[nodiscard]] Result<HeadRecord> decode_head(std::span<const std::uint8_t> bytes);

// This comparison assumes the signature has already been verified by the
// application's selected signing implementation. rev0003 deliberately keeps
// cryptography behind a future narrow adapter rather than inventing one.
[[nodiscard]] HeadDecision evaluate_head(
    const HeadRecord *current, const HeadRecord &candidate);
[[nodiscard]] const char *to_string(HeadDecision decision) noexcept;

}  // namespace iotox::mutorr
