#pragma once

#include <memory>
#include <string>
#include <string_view>

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

// Canonical lowercase SHA-256 text used throughout process-local and durable
// evidence. The verifier is deliberately colocated with the digest owner so a
// focused persistence boundary does not need the JSON/policy monolith merely
// to validate or mint one digest.
[[nodiscard]] std::string sha256_hex(const std::string& data);
[[nodiscard]] bool is_lowercase_sha256_hex(std::string_view value) noexcept;

}  // namespace anonsync
