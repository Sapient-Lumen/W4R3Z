#pragma once

#include <array>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

namespace anonsync {

// Incremental, binary-safe SHA-256 owner for evidence that must be derived
// without first concatenating an unbounded in-memory material string. The
// builder is single-use: finish_hex() consumes the digest state. Moved-from
// and already-finished builders reject further updates.
class Sha256DigestBuilder final {
public:
    Sha256DigestBuilder();
    ~Sha256DigestBuilder();

    Sha256DigestBuilder(const Sha256DigestBuilder&) = delete;
    Sha256DigestBuilder& operator=(const Sha256DigestBuilder&) = delete;
    Sha256DigestBuilder(Sha256DigestBuilder&& other) noexcept;
    Sha256DigestBuilder& operator=(Sha256DigestBuilder&& other) noexcept;

    void update(std::string_view bytes);
    [[nodiscard]] std::string finish_hex();

private:
    struct State;
    std::unique_ptr<State> state_;
};

inline constexpr std::size_t kSha256DigestBytes = 32U;
inline constexpr std::size_t kSha256HexCharacters =
    kSha256DigestBytes * 2U;

// Canonical fixed-width SHA-256 value. The binary representation removes one
// heap owner from every retained or wire-facing digest while preserving exact
// lowercase-hex framing at serialization boundaries. Construction and
// assignment accept only canonical lowercase text; all instances are valid.
class Sha256DigestValue final {
public:
    Sha256DigestValue() noexcept = default;
    Sha256DigestValue(std::string_view lowercase_hex);
    explicit Sha256DigestValue(
        std::array<std::uint8_t, kSha256DigestBytes> bytes) noexcept
        : bytes_(std::move(bytes)) {}

    Sha256DigestValue& operator=(std::string_view lowercase_hex);

    [[nodiscard]] const std::array<std::uint8_t, kSha256DigestBytes>&
    bytes() const noexcept {
        return bytes_;
    }

    [[nodiscard]] std::array<char, kSha256HexCharacters>
    lowercase_hex_array() const noexcept;
    [[nodiscard]] std::string lowercase_hex() const;
    void append_lowercase_hex_to(std::string& destination) const;
    void append_binary_to(std::string& destination) const;
    void update_lowercase_hex(Sha256DigestBuilder& destination) const;

    [[nodiscard]] bool equals_lowercase_hex(
        std::string_view value) const noexcept;
    [[nodiscard]] int compare_lowercase_hex(
        std::string_view value) const noexcept;

    bool operator==(const Sha256DigestValue&) const = default;
    auto operator<=>(const Sha256DigestValue&) const = default;

    friend bool operator==(
        const Sha256DigestValue& left,
        std::string_view right) noexcept {
        return left.equals_lowercase_hex(right);
    }
    friend bool operator==(
        std::string_view left,
        const Sha256DigestValue& right) noexcept {
        return right.equals_lowercase_hex(left);
    }
    friend bool operator<(
        const Sha256DigestValue& left,
        std::string_view right) noexcept {
        return left.compare_lowercase_hex(right) < 0;
    }
    friend bool operator<(
        std::string_view left,
        const Sha256DigestValue& right) noexcept {
        return right.compare_lowercase_hex(left) > 0;
    }

private:
    std::array<std::uint8_t, kSha256DigestBytes> bytes_{};
};

static_assert(sizeof(Sha256DigestValue) == kSha256DigestBytes);
static_assert(std::is_trivially_copyable_v<Sha256DigestValue>);
static_assert(std::is_standard_layout_v<Sha256DigestValue>);

// Canonical lowercase SHA-256 text used throughout process-local and durable
// evidence. The verifier is deliberately colocated with the digest owner so a
// focused persistence boundary does not need the JSON/policy monolith merely
// to validate or mint one digest.
[[nodiscard]] std::string sha256_hex(const std::string& data);
[[nodiscard]] bool is_lowercase_sha256_hex(std::string_view value) noexcept;

}  // namespace anonsync
