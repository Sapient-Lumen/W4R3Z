#pragma once

#include "iotox/network.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"
#include "iotox/toxcore/abi.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <vector>

namespace iotox::routes {

inline constexpr std::size_t kMaximumRouteMembers = 16U;
inline constexpr std::uint8_t kRouteSetFormatVersion = 1U;
inline constexpr std::uint8_t kRouteSetFormatVersionV2 = 2U;
inline constexpr std::uint8_t kRouteProtocolVersion = 1U;

using ToxPublicKey =
    std::array<std::uint8_t, toxcore::abi::kPublicKeySize>;

enum class Role : std::uint8_t { protected_route = 1U, bulk = 2U };
enum class ConnectionClass : std::uint8_t {
    tcp = 1U,
    udp = 2U,
    either = 3U,
};
// V1 leaves the member network class unspecified. V2 signs one exact
// deployment class without disclosing proxy, relay, router, or endpoint
// coordinates.
enum class NetworkClass : std::uint8_t {
    unspecified = 0U,
    tox_native = 1U,
    tox_tor = 2U,
    // Value 3 was first qualified under the laboratory spelling
    // `tox/i2p-construction`. ADR 0253 promotes the identical strict route to
    // canonical `tox/i2p` without changing signed bytes.
    tox_i2p = 3U,
};
enum class Lifecycle : std::uint8_t {
    configured = 1U,
    connecting = 2U,
    authenticated = 3U,
    ready = 4U,
    recovering = 5U,
    unavailable = 6U,
};
enum class Failure : std::uint8_t {
    none = 0U,
    connection = 1U,
    authentication = 2U,
    policy = 3U,
    restart_exhausted = 4U,
    worker = 5U,
    transport = 6U,
    internal = 7U,
};

struct MemberPolicy {
    ToxPublicKey tox_public_key{};
    Role role{Role::bulk};
    ConnectionClass connection_class{ConnectionClass::either};
    std::uint16_t maximum_active_work{0U};
    std::uint16_t restart_budget{0U};
    // Zero means no wall-clock expiry. Otherwise this is Unix milliseconds.
    std::uint64_t expires_unix_ms{0U};
    NetworkClass network_class{NetworkClass::unspecified};

    [[nodiscard]] bool operator==(const MemberPolicy &) const = default;
};

struct RouteSet {
    std::uint64_t generation{0U};
    security::SigningPublicKey stable_device_principal{};
    ToxPublicKey coordinator_tox_public_key{};
    std::uint8_t minimum_route_protocol{kRouteProtocolVersion};
    std::vector<MemberPolicy> members;
    std::uint8_t format_version{kRouteSetFormatVersion};

    [[nodiscard]] bool operator==(const RouteSet &) const = default;
};

// The artifact is canonical fixed-field binary followed by one detached
// Ed25519 signature from stable_device_principal. Member order is lexical by
// Tox public key and therefore has one representation.
[[nodiscard]] Result<std::vector<std::uint8_t>> sign_route_set(
    RouteSet route_set, const security::DeviceIdentity &identity);
[[nodiscard]] Result<RouteSet> verify_route_set(
    std::span<const std::uint8_t> artifact,
    const security::SigningPublicKey &expected_stable_device_principal,
    std::uint64_t minimum_generation, const security::Sodium &sodium);
// Digest of the complete signed artifact, shared by durable generation state
// and private member-scoped route proofs.
[[nodiscard]] Result<security::Digest> route_set_artifact_digest(
    std::span<const std::uint8_t> artifact,
    const security::Sodium &sodium);

struct RouteProof {
    ToxPublicKey tox_public_key{};
    security::SigningPublicKey stable_device_principal{};
    std::uint64_t route_set_generation{0U};
    std::uint8_t route_protocol_version{0U};
    ConnectionClass connection_class{ConnectionClass::either};
    std::uint64_t worker_id{0U};
    bool transcript_confirmed{false};
    NetworkClass network_class{NetworkClass::unspecified};
};

struct MemberSnapshot {
    MemberPolicy policy;
    Lifecycle lifecycle{Lifecycle::configured};
    std::uint64_t worker_id{0U};
    std::uint16_t restarts{0U};
    std::uint16_t admitted_work{0U};
    Failure last_failure{Failure::none};
};

struct CoordinatorSnapshot {
    security::SigningPublicKey stable_device_principal{};
    std::uint64_t generation{0U};
    std::vector<MemberSnapshot> members;
};

// Authority remains outside route workers. This coordinator admits only an
// exact signed-inventory member after the IoTox application transcript has
// confirmed the same stable principal and generation.
class Coordinator {
  public:
    [[nodiscard]] static Result<Coordinator> create(
        RouteSet route_set, std::uint64_t now_unix_ms = 0U);

    [[nodiscard]] Status begin_connecting(
        const ToxPublicKey &key, std::uint64_t worker_id);
    [[nodiscard]] Status authenticate(const RouteProof &proof);
    [[nodiscard]] Status mark_ready(
        const ToxPublicKey &key, std::uint64_t worker_id);
    [[nodiscard]] Status authentication_lost(
        const ToxPublicKey &key, std::uint64_t worker_id,
        Failure failure = Failure::authentication);
    [[nodiscard]] Status admit_work(
        const ToxPublicKey &key, std::uint64_t worker_id,
        std::uint16_t amount = 1U);
    [[nodiscard]] Status release_work(
        const ToxPublicKey &key, std::uint64_t worker_id,
        std::uint16_t amount = 1U);
    [[nodiscard]] Status begin_recovery(
        const ToxPublicKey &key, std::uint64_t worker_id,
        Failure failure);
    [[nodiscard]] Status mark_unavailable(
        const ToxPublicKey &key, std::uint64_t worker_id,
        Failure failure);

    [[nodiscard]] CoordinatorSnapshot snapshot() const;

  private:
    explicit Coordinator(RouteSet route_set, std::uint64_t now_unix_ms);

    [[nodiscard]] Result<std::size_t> member_index(
        const ToxPublicKey &key) const;
    [[nodiscard]] Status require_worker(
        const MemberSnapshot &member, std::uint64_t worker_id) const;

    RouteSet route_set_;
    std::uint64_t now_unix_ms_{0U};
    std::vector<MemberSnapshot> members_;
};

[[nodiscard]] const char *to_string(Role role) noexcept;
[[nodiscard]] const char *to_string(ConnectionClass connection_class) noexcept;
[[nodiscard]] const char *to_string(NetworkClass network_class) noexcept;
[[nodiscard]] Result<NetworkClass> network_class_from_stack(
    const NetworkStack &network);
[[nodiscard]] const char *to_string(Lifecycle lifecycle) noexcept;
[[nodiscard]] const char *to_string(Failure failure) noexcept;
[[nodiscard]] Result<std::string> render_coordinator_snapshot(
    const CoordinatorSnapshot &snapshot, const security::Sodium &sodium);

}  // namespace iotox::routes
