#pragma once

#include "toxsync/hash.hpp"
#include "toxsync/wire.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <span>

namespace toxsync {

struct Ed25519PublicKey {
    std::array<std::byte, 32> bytes{};
    friend constexpr bool operator==(const Ed25519PublicKey&, const Ed25519PublicKey&) = default;
};

struct Ed25519PrivateKey {
    // Raw 32-byte Ed25519 seed, matching EVP_PKEY_new_raw_private_key.
    std::array<std::byte, 32> bytes{};
};

[[nodiscard]] bool ed25519_backend_available() noexcept;
[[nodiscard]] bool ed25519_generate_key(Ed25519PrivateKey& private_key,
                                        Ed25519PublicKey& public_key) noexcept;
[[nodiscard]] bool ed25519_sign(std::span<const std::byte> message,
                                const Ed25519PrivateKey& private_key,
                                std::span<std::byte, 64> signature) noexcept;
[[nodiscard]] bool ed25519_verify(std::span<const std::byte> message,
                                  const Ed25519PublicKey& public_key,
                                  std::span<const std::byte, 64> signature) noexcept;
[[nodiscard]] bool ed25519_public_key(const Ed25519PrivateKey& private_key,
                                      Ed25519PublicKey& public_key) noexcept;

[[nodiscard]] Digest256 mutable_head_record_digest(const MutableHead& head);
[[nodiscard]] bool sign_mutable_head(MutableHead& head,
                                     const Ed25519PrivateKey& private_key) noexcept;
[[nodiscard]] bool verify_mutable_head(const MutableHead& head,
                                       const Ed25519PublicKey& public_key) noexcept;

enum class HeadDecision : std::uint8_t {
    accept_genesis,
    accept_advance,
    accept_snapshot,
    duplicate,
    stale,
    fork,
    wrong_namespace,
    invalid_signature,
    generation_gap,
    parent_mismatch,
    engine_downgrade,
    resource_limit,
};

struct MutableHeadPolicy {
    std::uint64_t minimum_generation{1U};
    std::uint64_t maximum_generation_jump{1024U};
    std::uint64_t maximum_artifact_size{1ULL << 48U};
    std::uint64_t maximum_index_size{1ULL << 34U};
    bool require_signature{true};
    bool require_parent_link{true};
    bool allow_snapshot_rebase{true};
    bool forbid_engine_downgrade{true};
};

using MutableHeadSignatureVerifier = bool (*)(
    void* context,
    const MutableHead& head,
    std::span<const std::byte, kMutableHeadSigningBytes> signing_body,
    std::span<const std::byte, 64> signature);

struct MutableHeadEvaluation {
    HeadDecision decision{HeadDecision::invalid_signature};
    Digest256 candidate_record{};
    Digest256 current_record{};
    std::uint64_t generation_delta{};

    [[nodiscard]] bool accepted() const noexcept {
        return decision == HeadDecision::accept_genesis ||
               decision == HeadDecision::accept_advance ||
               decision == HeadDecision::accept_snapshot;
    }
};

[[nodiscard]] MutableHeadEvaluation evaluate_mutable_head(
    const MutableHead& candidate,
    const std::optional<MutableHead>& current,
    MutableHeadSignatureVerifier verifier,
    void* verifier_context,
    const MutableHeadPolicy& policy = {});

[[nodiscard]] const char* head_decision_name(HeadDecision decision) noexcept;

struct MutableHeadStateOptions {
    bool fsync_on_commit{true};
    bool create_parent_directories{true};
};

// Fixed-size, checksummed, atomic state snapshot. The state file contains the
// complete signed HEAD plus its record digest and a checksum over the snapshot.
void store_mutable_head_state(const std::filesystem::path& path,
                              const MutableHead& head,
                              const MutableHeadStateOptions& options = {});
[[nodiscard]] std::optional<MutableHead> load_mutable_head_state(
    const std::filesystem::path& path);

} // namespace toxsync
