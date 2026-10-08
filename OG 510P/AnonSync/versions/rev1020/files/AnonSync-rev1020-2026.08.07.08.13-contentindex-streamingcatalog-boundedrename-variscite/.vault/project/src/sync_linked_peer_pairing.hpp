#pragma once

#if !defined(_WIN32)

#include "sync_linked_peer_user_layout.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_tls_membership_snapshot.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::string_view kSyncLinkedPeerCardSchema =
    "anonsync.linked-peer-card.v1";
inline constexpr std::uint64_t kSyncLinkedPeerCardMaximumBytes = 64U * 1024U;
inline constexpr std::uint64_t kSyncLinkedPeerIdentityFileMaximumBytes =
    1024U * 1024U;

// Public-only, self-verifying material exchanged between two explicit
// operators. The exact canonical fields are signed by the private key whose
// public half is carried by certificate_pem. This proves card integrity and
// key possession, but not the human source of an otherwise valid substituted
// card. Compare or pin the exact card fingerprint over a trusted channel.
// Possessing a card is not a share grant; admission below is the local durable
// authorization step.
struct SyncLinkedPeerCard final {
    std::string schema{std::string(kSyncLinkedPeerCardSchema)};
    std::string folder_id;
    SyncReplicaActor actor;
    std::string spki_sha256;
    std::string certificate_pem;
    std::string signature_ed25519;

    bool operator==(const SyncLinkedPeerCard&) const = default;
};

enum class SyncLinkedPeerIdentityFileDisposition : std::uint8_t {
    Created = 1U,
    ReusedExact = 2U,
};

struct SyncLinkedPeerIdentityCreationResult final {
    SyncLinkedPeerIdentityLayout layout;
    SyncLinkedPeerCard card;
    SyncLinkedPeerIdentityFileDisposition private_key_disposition =
        SyncLinkedPeerIdentityFileDisposition::Created;
    SyncLinkedPeerIdentityFileDisposition certificate_disposition =
        SyncLinkedPeerIdentityFileDisposition::Created;
    SyncLinkedPeerIdentityFileDisposition pairing_card_disposition =
        SyncLinkedPeerIdentityFileDisposition::Created;
};

[[nodiscard]] const char* sync_linked_peer_identity_file_disposition_name(
    SyncLinkedPeerIdentityFileDisposition disposition) noexcept;

// Creates or resumes one share/peer-scoped Ed25519 identity under the supplied
// owner-only layout. Partial create-new attempts are recoverable: an existing
// exact key or certificate is re-opened and proved before any missing later
// artifact is published. Conflicting material is never overwritten.
[[nodiscard]] SyncLinkedPeerIdentityCreationResult
create_or_resume_sync_linked_peer_identity_or_throw(
    const SyncLinkedPeerIdentityLayout& layout,
    const SyncReplicaDeploymentManifest& deployment,
    std::string_view label = "sync linked-peer identity creation");

[[nodiscard]] SyncLinkedPeerCard
read_sync_linked_peer_card_file_or_throw(
    const std::filesystem::path& absolute_card_path,
    std::string_view label = "sync linked-peer card");

// SHA-256 of the exact canonical card bytes, including the signature. The
// grouped verification code is the first 128 bits of that digest and is meant
// for human comparison; admission may pin the complete digest.
[[nodiscard]] std::string sync_linked_peer_card_sha256_or_throw(
    const SyncLinkedPeerCard& card,
    std::string_view label = "sync linked-peer card fingerprint");
[[nodiscard]] std::string sync_linked_peer_card_verification_code_or_throw(
    const SyncLinkedPeerCard& card,
    std::string_view label = "sync linked-peer card verification code");

struct SyncLinkedPeerAdmissionResult final {
    bool peer_trust_created = false;
    bool membership_changed = false;
    std::uint64_t membership_state_generation = 0U;
    std::uint64_t membership_policy_epoch = 0U;
    std::uint64_t membership_entry_count = 0U;
    std::string membership_chain_digest;
};

// Explicitly admits one signed public card into this deployment's exact
// membership and installs its self-signed certificate as the one linked peer's
// trust anchor. Existing unrelated members are preserved. Exact replay is an
// idempotent no-op; actor/SPKI substitutions stop for a future rotation flow.
[[nodiscard]] SyncLinkedPeerAdmissionResult
admit_sync_linked_peer_card_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const SyncLinkedPeerCard& peer_card,
    const std::filesystem::path& absolute_peer_trust_path,
    std::string_view label = "sync linked-peer admission");

}  // namespace anonsync

#endif
