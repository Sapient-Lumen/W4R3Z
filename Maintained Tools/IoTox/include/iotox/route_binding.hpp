#pragma once

#include "iotox/protocol/session.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/route_inventory.hpp"
#include "iotox/security/sodium.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <optional>
#include <span>
#include <vector>

namespace iotox::routes {

inline constexpr std::uint8_t kRouteBindingFormatVersion = 1U;
inline constexpr std::size_t kRouteBindingBodyBytes = 160U;
inline constexpr std::size_t kRouteBindingArtifactBytes =
    kRouteBindingBodyBytes + security::kSignatureBytes;
inline constexpr std::size_t kPrivateRouteMemberBindingBodyBytes = 192U;
inline constexpr std::size_t kPrivateRouteMemberBindingArtifactBytes =
    kPrivateRouteMemberBindingBodyBytes + security::kSignatureBytes;
inline constexpr std::uint64_t kRouteBindingSequence = 5U;
inline constexpr std::uint64_t kPrivateRouteInventorySequence = 6U;
inline constexpr std::uint64_t kPrivateRouteMemberBindingSequence = 7U;
inline constexpr std::size_t kRouteBindingSetLengthBytes = 2U;
using RouteBindingArtifact =
    std::array<std::uint8_t, kRouteBindingArtifactBytes>;
using PrivateRouteMemberBindingArtifact =
    std::array<std::uint8_t, kPrivateRouteMemberBindingArtifactBytes>;

struct VerifiedRouteBinding {
    RouteSet route_set;
    MemberPolicy member;
    RouteBindingArtifact binding{};
};

// A full signed route set admitted only on an authority-authenticated primary
// association. The primary friend/epoch fields prevent an auxiliary proof
// from surviving replacement of the authorization edge that disclosed it.
struct PrivateRouteInventory {
    RouteSet route_set;
    security::Digest artifact_digest{};
    std::uint32_t primary_friend_number{0U};
    std::uint64_t primary_online_epoch{0U};

    [[nodiscard]] bool operator==(const PrivateRouteInventory &) const = default;
};

// The complete primary edge retained with a privately admitted inventory.
// Consumers must use this exact session/authority pair when constructing or
// verifying an auxiliary member proof; neither field is ambient trust.
struct PrivateRoutePrimaryContext {
    PrivateRouteInventory inventory;
    protocol::PeerSessionSnapshot session;
    security::PeerAuthoritySnapshot authority;
};

struct PrivateRoutePrimaryEdge {
    protocol::PeerSessionSnapshot session;
    security::PeerAuthoritySnapshot authority;
};

enum class PrivateRouteInventoryAdmissionKind : std::uint8_t {
    accepted = 1U,
    exact_replay = 2U,
};

struct PrivateRouteInventoryAdmission {
    PrivateRouteInventoryAdmissionKind kind{
        PrivateRouteInventoryAdmissionKind::accepted};
    PrivateRoutePrimaryContext context;
};

struct PrivateRouteInventoryRegistrySnapshot {
    std::size_t active_primary_edges{0U};
    std::size_t generation_high_water_records{0U};
    std::uint64_t accepted{0U};
    std::uint64_t exact_replays{0U};
    std::uint64_t rejected{0U};
};

struct RemoteRouteTrust {
    security::SigningPublicKey stable_device_principal{};
    ToxPublicKey coordinator_tox_public_key{};
    std::uint64_t minimum_generation{0U};
    std::uint64_t primary_online_epoch{0U};

    [[nodiscard]] bool operator==(const RemoteRouteTrust &) const = default;
};

enum class RouteBindingAdmissionKind : std::uint8_t {
    accepted = 1U,
    exact_replay = 2U,
};

struct RouteBindingAdmission {
    RouteBindingAdmissionKind kind{RouteBindingAdmissionKind::accepted};
    RemoteRouteTrust trust;
    VerifiedRouteBinding verified;
};

struct RouteBindingRegistrySnapshot {
    std::size_t trusted_primary_routes{0U};
    std::size_t accepted_workers{0U};
    std::uint64_t accepted{0U};
    std::uint64_t exact_replays{0U};
    std::uint64_t rejected{0U};
};

// Creates a stable-device attestation for one local route and the exact
// transcript-confirmed peer session carrying it. No caller may supply or
// assert the transcript digest independently.
[[nodiscard]] Result<RouteBindingArtifact> make_route_binding(
    const RouteSet &route_set, const ToxPublicKey &local_route_key,
    const protocol::PeerSessionSnapshot &session,
    const security::DeviceIdentity &identity, const security::Sodium &sodium);

// Verifies a remote route against an already authenticated remote route set
// and the receiver's exact confirmed view of the same session.
[[nodiscard]] Status verify_route_binding(
    std::span<const std::uint8_t> artifact,
    const RouteSet &expected_remote_route_set,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium);

// The exchange payload carries one complete stable-device-signed route set
// followed by the exact transcript-derived member binding. This makes the
// verifier's generation and membership input explicit rather than relying on
// ambient worker assertions.
[[nodiscard]] Result<std::vector<std::uint8_t>>
make_route_binding_exchange_payload(
    std::span<const std::uint8_t> signed_route_set,
    const RouteSet &route_set, const ToxPublicKey &local_route_key,
    const protocol::PeerSessionSnapshot &session,
    const security::DeviceIdentity &identity, const security::Sodium &sodium);

[[nodiscard]] Result<VerifiedRouteBinding>
verify_route_binding_exchange_payload(
    std::span<const std::uint8_t> payload,
    const security::SigningPublicKey &expected_remote_principal,
    std::uint64_t minimum_remote_generation,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium);

[[nodiscard]] Result<protocol::Frame> make_route_binding_frame(
    std::span<const std::uint8_t> signed_route_set,
    const RouteSet &route_set, const ToxPublicKey &local_route_key,
    const protocol::PeerSessionSnapshot &session,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    std::uint64_t message_id);

// Private v2 moves the complete signed inventory to an already
// authority-authenticated primary session. The auxiliary session then carries
// only one fixed transcript/inventory-digest binding for a member present in
// that privately admitted inventory. V1 frame bytes and semantics remain
// unchanged.
[[nodiscard]] Result<protocol::Frame> make_private_route_inventory_frame(
    std::span<const std::uint8_t> signed_route_set,
    const RouteSet &route_set,
    const protocol::PeerSessionSnapshot &primary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium, std::uint64_t message_id);

[[nodiscard]] Result<PrivateRouteInventory>
verify_private_route_inventory_frame(
    const protocol::Frame &frame,
    const protocol::PeerSessionSnapshot &primary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::Sodium &sodium);

[[nodiscard]] Result<protocol::Frame>
make_private_route_member_binding_frame(
    std::span<const std::uint8_t> signed_local_route_set,
    const RouteSet &local_route_set, const ToxPublicKey &local_route_key,
    const PrivateRouteInventory &expected_remote_inventory,
    const protocol::PeerSessionSnapshot &primary_session,
    const protocol::PeerSessionSnapshot &auxiliary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium, std::uint64_t message_id);

[[nodiscard]] Status verify_private_route_member_binding_frame(
    const protocol::Frame &frame,
    const PrivateRouteInventory &expected_remote_inventory,
    const protocol::PeerSessionSnapshot &primary_session,
    const protocol::PeerSessionSnapshot &auxiliary_session,
    const security::PeerAuthoritySnapshot &primary_authority,
    const security::Sodium &sodium);

// Process-local admission and anti-replay state for the private primary
// inventory exchange. A frame is useful only while its exact primary
// authority edge remains current. Generation/digest high-water survives edge
// retirement for the process lifetime so reconnect cannot roll back or fork
// an already observed stable-principal inventory.
class PrivateRouteInventoryRegistry {
  public:
    struct Config {
        std::size_t maximum_active_primary_edges{64U};
        std::size_t maximum_generation_high_water_records{64U};
    };

    PrivateRouteInventoryRegistry();
    explicit PrivateRouteInventoryRegistry(Config config);

    PrivateRouteInventoryRegistry(const PrivateRouteInventoryRegistry &) =
        delete;
    PrivateRouteInventoryRegistry &operator=(
        const PrivateRouteInventoryRegistry &) = delete;

    [[nodiscard]] Result<PrivateRouteInventoryAdmission> receive(
        const protocol::Frame &frame,
        const protocol::PeerSessionSnapshot &primary_session,
        const security::PeerAuthoritySnapshot &primary_authority,
        const security::Sodium &sodium);
    // Keep only entries whose byte-retained frame still verifies against one
    // supplied exact current edge. Empty input retires every active entry but
    // deliberately preserves generation high-water.
    [[nodiscard]] Status replace_active_edges(
        std::vector<PrivateRoutePrimaryEdge> edges,
        const security::Sodium &sodium);
    [[nodiscard]] std::vector<PrivateRoutePrimaryContext> contexts() const;
    [[nodiscard]] PrivateRouteInventoryRegistrySnapshot snapshot() const;

  private:
    struct ActiveEntry {
        protocol::Frame frame;
        std::vector<std::uint8_t> encoded_frame;
        PrivateRoutePrimaryContext context;
    };

    struct HighWaterEntry {
        security::SigningPublicKey stable_device_principal{};
        ToxPublicKey coordinator_tox_public_key{};
        std::uint64_t generation{0U};
        security::Digest artifact_digest{};
    };

    [[nodiscard]] Status validate_config() const;

    Config config_;
    mutable std::mutex mutex_;
    std::vector<ActiveEntry> active_;
    std::vector<HighWaterEntry> high_water_;
    std::uint64_t accepted_{0U};
    std::uint64_t exact_replays_{0U};
    std::uint64_t rejected_{0U};
};

[[nodiscard]] Result<VerifiedRouteBinding> verify_route_binding_frame(
    const protocol::Frame &frame,
    const security::SigningPublicKey &expected_remote_principal,
    std::uint64_t minimum_remote_generation,
    const protocol::PeerSessionSnapshot &session,
    const security::Sodium &sodium);

// Coordinator-owned trust and replay state for auxiliary routes. Trust enters
// only from an independently authority-authenticated primary session. A
// received route set must name that exact primary Tox key as coordinator;
// payload bytes cannot nominate their own stable principal or generation
// floor. One worker incarnation accepts one binding per online epoch, with
// byte-identical message retries treated idempotently and conflicts rejected.
class RouteBindingRegistry {
  public:
    struct Config {
        std::size_t maximum_trusted_primary_routes{64U};
        std::size_t maximum_workers{kMaximumRouteMembers};
    };

    RouteBindingRegistry();
    explicit RouteBindingRegistry(Config config);

    RouteBindingRegistry(const RouteBindingRegistry &) = delete;
    RouteBindingRegistry &operator=(const RouteBindingRegistry &) = delete;

    [[nodiscard]] Status replace_trust(
        std::vector<RemoteRouteTrust> trust);
    [[nodiscard]] Result<RouteBindingAdmission> receive(
        const ToxPublicKey &local_route_key, std::uint64_t worker_id,
        const protocol::Frame &frame,
        const protocol::PeerSessionSnapshot &session,
        const security::Sodium &sodium);
    [[nodiscard]] Status retire_worker(
        const ToxPublicKey &local_route_key, std::uint64_t worker_id);
    [[nodiscard]] RouteBindingRegistrySnapshot snapshot() const;

  private:
    struct TrustState {
        RemoteRouteTrust trust;
        std::optional<RouteSet> accepted_route_set;
    };

    struct WorkerEntry {
        ToxPublicKey local_route_key{};
        std::uint64_t worker_id{0U};
        std::uint64_t online_epoch{0U};
        std::uint64_t message_id{0U};
        RemoteRouteTrust trust;
        VerifiedRouteBinding verified;
    };

    [[nodiscard]] Status validate_config() const;

    Config config_;
    mutable std::mutex mutex_;
    std::vector<TrustState> trust_;
    std::vector<WorkerEntry> workers_;
    std::uint64_t accepted_{0U};
    std::uint64_t exact_replays_{0U};
    std::uint64_t rejected_{0U};
};

}  // namespace iotox::routes
