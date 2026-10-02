#include "iotox/route_inventory.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <sstream>
#include <string_view>

namespace iotox::routes {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagicV1 = {
    'I', 'O', 'T', 'O', 'X', 'R', 'S', '1'};
constexpr std::array<std::uint8_t, 8U> kMagicV2 = {
    'I', 'O', 'T', 'O', 'X', 'R', 'S', '2'};
constexpr std::string_view kSignatureDomainV1{
    "IOTOX-ROUTE-SET-SIGNATURE-V1"};
constexpr std::string_view kSignatureDomainV2{
    "IOTOX-ROUTE-SET-SIGNATURE-V2"};
constexpr std::string_view kArtifactDigestDomain{
    "iotox-route-set-artifact-v1"};
constexpr std::size_t kHeaderBytes = 92U;
constexpr std::size_t kMemberBytes = 48U;

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

void append_u16(std::vector<std::uint8_t> &output, std::uint16_t value) {
    output.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xffU));
    output.push_back(static_cast<std::uint8_t>(value & 0xffU));
}

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>(
            (value >> static_cast<unsigned>(shift)) & 0xffU));
    }
}

std::uint16_t read_u16(std::span<const std::uint8_t> bytes, std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
        static_cast<std::uint16_t>(bytes[offset + 1U]));
}

std::uint64_t read_u64(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

bool valid_role(Role role) {
    return role == Role::protected_route || role == Role::bulk;
}

bool valid_connection_class(ConnectionClass value) {
    return value == ConnectionClass::tcp || value == ConnectionClass::udp ||
           value == ConnectionClass::either;
}

bool valid_network_class(NetworkClass value) {
    return value == NetworkClass::tox_native ||
           value == NetworkClass::tox_tor ||
           value == NetworkClass::tox_i2p;
}

Status validate(RouteSet &route_set) {
    if (route_set.generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "route-set generation must be non-zero"};
    }
    if (all_zero(route_set.stable_device_principal) ||
        all_zero(route_set.coordinator_tox_public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "route-set principals and coordinator key must be non-zero"};
    }
    if ((route_set.format_version != kRouteSetFormatVersion &&
         route_set.format_version != kRouteSetFormatVersionV2) ||
        route_set.minimum_route_protocol != kRouteProtocolVersion) {
        return Status{ErrorCode::protocol_error,
                      "route-set format or minimum protocol is unsupported"};
    }
    if (route_set.members.size() < 2U ||
        route_set.members.size() > kMaximumRouteMembers) {
        return Status{ErrorCode::invalid_argument,
                      "route set must contain 2..16 members"};
    }
    std::sort(route_set.members.begin(), route_set.members.end(),
              [](const MemberPolicy &left, const MemberPolicy &right) {
                  return left.tox_public_key < right.tox_public_key;
              });
    std::size_t protected_count = 0U;
    for (std::size_t index = 0U; index < route_set.members.size(); ++index) {
        const MemberPolicy &member = route_set.members[index];
        if (all_zero(member.tox_public_key) || !valid_role(member.role) ||
            !valid_connection_class(member.connection_class) ||
            member.maximum_active_work == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "route member contains a zero key, invalid enum, or zero budget"};
        }
        if ((route_set.format_version == kRouteSetFormatVersion &&
             member.network_class != NetworkClass::unspecified) ||
            (route_set.format_version == kRouteSetFormatVersionV2 &&
             !valid_network_class(member.network_class))) {
            return Status{
                ErrorCode::invalid_argument,
                "route member network class violates the route-set format"};
        }
        if (index > 0U && route_set.members[index - 1U].tox_public_key ==
                              member.tox_public_key) {
            return Status{ErrorCode::protocol_error,
                          "route set contains a duplicated Tox public key"};
        }
        if (member.role == Role::protected_route) ++protected_count;
    }
    if (protected_count != 1U) {
        return Status{ErrorCode::invalid_argument,
                      "route set must contain exactly one protected route"};
    }
    if (route_set.format_version == kRouteSetFormatVersionV2) {
        const auto coordinator = std::find_if(
            route_set.members.begin(), route_set.members.end(),
            [&route_set](const MemberPolicy &member) {
                return member.tox_public_key ==
                    route_set.coordinator_tox_public_key;
            });
        if (coordinator == route_set.members.end() ||
            coordinator->role != Role::protected_route) {
            return Status{
                ErrorCode::invalid_argument,
                "route-set-v2 coordinator must be its protected member"};
        }
    }
    return Status::success();
}

std::vector<std::uint8_t> signature_message(
    std::span<const std::uint8_t> body, std::uint8_t format_version) {
    const std::string_view domain =
        format_version == kRouteSetFormatVersionV2
        ? kSignatureDomainV2 : kSignatureDomainV1;
    std::vector<std::uint8_t> message;
    message.reserve(domain.size() + body.size());
    message.insert(message.end(), domain.begin(), domain.end());
    message.insert(message.end(), body.begin(), body.end());
    return message;
}

Result<std::vector<std::uint8_t>> encode_body(RouteSet route_set) {
    const Status valid = validate(route_set);
    if (!valid.ok()) return valid;
    std::vector<std::uint8_t> output;
    output.reserve(kHeaderBytes + route_set.members.size() * kMemberBytes);
    const auto &magic = route_set.format_version == kRouteSetFormatVersionV2
        ? kMagicV2 : kMagicV1;
    output.insert(output.end(), magic.begin(), magic.end());
    output.push_back(route_set.format_version);
    output.push_back(route_set.minimum_route_protocol);
    output.insert(output.end(), 2U, 0U);
    append_u64(output, route_set.generation);
    output.insert(output.end(), route_set.stable_device_principal.begin(),
                  route_set.stable_device_principal.end());
    output.insert(output.end(), route_set.coordinator_tox_public_key.begin(),
                  route_set.coordinator_tox_public_key.end());
    append_u16(output, static_cast<std::uint16_t>(route_set.members.size()));
    output.insert(output.end(), 6U, 0U);
    for (const MemberPolicy &member : route_set.members) {
        output.insert(output.end(), member.tox_public_key.begin(),
                      member.tox_public_key.end());
        output.push_back(static_cast<std::uint8_t>(member.role));
        output.push_back(static_cast<std::uint8_t>(member.connection_class));
        append_u16(output, member.maximum_active_work);
        append_u16(output, member.restart_budget);
        output.push_back(
            route_set.format_version == kRouteSetFormatVersionV2
            ? static_cast<std::uint8_t>(member.network_class) : 0U);
        output.push_back(0U);
        append_u64(output, member.expires_unix_ms);
    }
    return output;
}

}  // namespace

Result<security::Digest> route_set_artifact_digest(
    std::span<const std::uint8_t> artifact,
    const security::Sodium &sodium) {
    return sodium.hash(kArtifactDigestDomain, artifact);
}

Result<std::vector<std::uint8_t>> sign_route_set(
    RouteSet route_set, const security::DeviceIdentity &identity) {
    if (!security::constant_time_equal(route_set.stable_device_principal,
                                       identity.public_key())) {
        return Status{ErrorCode::protocol_error,
                      "route set names a foreign stable device principal"};
    }
    const std::uint8_t format_version = route_set.format_version;
    auto body = encode_body(std::move(route_set));
    if (!body) return body.status();
    const auto message = signature_message(
        body.value(), format_version);
    auto signature = identity.sign(message);
    if (!signature) return signature.status();
    body.value().insert(body.value().end(), signature.value().begin(),
                        signature.value().end());
    return std::move(body).value();
}

Result<RouteSet> verify_route_set(
    std::span<const std::uint8_t> artifact,
    const security::SigningPublicKey &expected_stable_device_principal,
    std::uint64_t minimum_generation, const security::Sodium &sodium) {
    if (artifact.size() < kHeaderBytes + security::kSignatureBytes) {
        return Status{ErrorCode::protocol_error,
                      "route-set artifact header is unsupported"};
    }
    const std::uint8_t format_version = artifact[8U];
    const bool v1 = format_version == kRouteSetFormatVersion &&
        std::equal(kMagicV1.begin(), kMagicV1.end(), artifact.begin());
    const bool v2 = format_version == kRouteSetFormatVersionV2 &&
        std::equal(kMagicV2.begin(), kMagicV2.end(), artifact.begin());
    if (!v1 && !v2) {
        return Status{ErrorCode::protocol_error,
                      "route-set artifact header is unsupported"};
    }
    if (artifact[10U] != 0U || artifact[11U] != 0U ||
        !all_zero(artifact.subspan(86U, 6U))) {
        return Status{ErrorCode::protocol_error,
                      "route-set reserved bytes are non-zero"};
    }
    const std::size_t count = read_u16(artifact, 84U);
    if (count < 2U || count > kMaximumRouteMembers ||
        artifact.size() != kHeaderBytes + count * kMemberBytes +
                               security::kSignatureBytes) {
        return Status{ErrorCode::protocol_error,
                      "route-set member count or exact length is invalid"};
    }
    const std::size_t body_size = artifact.size() - security::kSignatureBytes;
    RouteSet route_set;
    route_set.format_version = format_version;
    route_set.minimum_route_protocol = artifact[9U];
    route_set.generation = read_u64(artifact, 12U);
    std::copy_n(artifact.begin() + 20U, route_set.stable_device_principal.size(),
                route_set.stable_device_principal.begin());
    std::copy_n(artifact.begin() + 52U, route_set.coordinator_tox_public_key.size(),
                route_set.coordinator_tox_public_key.begin());
    route_set.members.reserve(count);
    for (std::size_t index = 0U; index < count; ++index) {
        const std::size_t offset = kHeaderBytes + index * kMemberBytes;
        if ((v1 && !all_zero(artifact.subspan(offset + 38U, 2U))) ||
            (v2 && artifact[offset + 39U] != 0U)) {
            return Status{ErrorCode::protocol_error,
                          "route member reserved bytes are non-zero"};
        }
        MemberPolicy member;
        std::copy_n(artifact.begin() + static_cast<std::ptrdiff_t>(offset),
                    member.tox_public_key.size(), member.tox_public_key.begin());
        member.role = static_cast<Role>(artifact[offset + 32U]);
        member.connection_class =
            static_cast<ConnectionClass>(artifact[offset + 33U]);
        member.maximum_active_work = read_u16(artifact, offset + 34U);
        member.restart_budget = read_u16(artifact, offset + 36U);
        member.network_class = v2
            ? static_cast<NetworkClass>(artifact[offset + 38U])
            : NetworkClass::unspecified;
        member.expires_unix_ms = read_u64(artifact, offset + 40U);
        route_set.members.push_back(member);
    }
    RouteSet canonical = route_set;
    const Status valid = validate(canonical);
    if (!valid.ok()) return valid;
    if (canonical.members != route_set.members) {
        return Status{ErrorCode::protocol_error,
                      "route-set members are not in canonical order"};
    }
    if (!security::constant_time_equal(route_set.stable_device_principal,
                                       expected_stable_device_principal)) {
        return Status{ErrorCode::protocol_error,
                      "route set is bound to a foreign stable device principal"};
    }
    if (route_set.generation < minimum_generation) {
        return Status{ErrorCode::protocol_error,
                      "route-set generation is stale"};
    }
    security::Signature signature{};
    std::copy_n(artifact.begin() + static_cast<std::ptrdiff_t>(body_size),
                signature.size(), signature.begin());
    const auto message = signature_message(
        artifact.first(body_size), format_version);
    const Status verified = sodium.verify_detached(
        signature, message, route_set.stable_device_principal);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "route-set stable-device signature is invalid"};
    }
    return route_set;
}

Coordinator::Coordinator(RouteSet route_set, std::uint64_t now_unix_ms)
    : route_set_(std::move(route_set)), now_unix_ms_(now_unix_ms) {
    std::sort(route_set_.members.begin(), route_set_.members.end(),
              [](const MemberPolicy &left, const MemberPolicy &right) {
                  return left.tox_public_key < right.tox_public_key;
              });
    members_.reserve(route_set_.members.size());
    for (const auto &policy : route_set_.members) {
        members_.push_back(MemberSnapshot{policy});
    }
}

Result<Coordinator> Coordinator::create(
    RouteSet route_set, std::uint64_t now_unix_ms) {
    const Status valid = validate(route_set);
    if (!valid.ok()) return valid;
    if (now_unix_ms == 0U &&
        std::any_of(route_set.members.begin(), route_set.members.end(),
                    [](const MemberPolicy &member) {
                        return member.expires_unix_ms != 0U;
                    })) {
        return Status{ErrorCode::invalid_argument,
                      "expiring route membership requires a trusted non-zero clock"};
    }
    return Coordinator(std::move(route_set), now_unix_ms);
}

Result<std::size_t> Coordinator::member_index(const ToxPublicKey &key) const {
    const auto found = std::lower_bound(
        members_.begin(), members_.end(), key,
        [](const MemberSnapshot &member, const ToxPublicKey &candidate) {
            return member.policy.tox_public_key < candidate;
        });
    if (found == members_.end() || found->policy.tox_public_key != key) {
        return Status{ErrorCode::protocol_error,
                      "route Tox key is not in the authenticated inventory"};
    }
    return static_cast<std::size_t>(found - members_.begin());
}

Status Coordinator::require_worker(
    const MemberSnapshot &member, std::uint64_t worker_id) const {
    if (worker_id == 0U || member.worker_id != worker_id) {
        return Status{ErrorCode::protocol_error,
                      "route worker does not own this inventory member"};
    }
    return Status::success();
}

Status Coordinator::begin_connecting(
    const ToxPublicKey &key, std::uint64_t worker_id) {
    if (worker_id == 0U) {
        return Status{ErrorCode::invalid_argument, "route worker ID must be non-zero"};
    }
    auto index = member_index(key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    if (member.worker_id != 0U && member.worker_id != worker_id &&
        member.lifecycle != Lifecycle::recovering) {
        return Status{ErrorCode::protocol_error,
                      "duplicate worker attempted to claim an inventory member"};
    }
    if (member.lifecycle != Lifecycle::configured &&
        member.lifecycle != Lifecycle::recovering) {
        return Status{ErrorCode::invalid_argument,
                      "route lifecycle cannot begin connecting from its current state"};
    }
    member.worker_id = worker_id;
    member.lifecycle = Lifecycle::connecting;
    return Status::success();
}

Status Coordinator::authenticate(const RouteProof &proof) {
    auto index = member_index(proof.tox_public_key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    const Status worker = require_worker(member, proof.worker_id);
    if (!worker.ok()) return worker;
    if (member.lifecycle != Lifecycle::connecting) {
        return Status{ErrorCode::invalid_argument,
                      "route may authenticate only while connecting"};
    }
    if (!proof.transcript_confirmed) {
        return Status{ErrorCode::protocol_error,
                      "route application transcript is not confirmed"};
    }
    if (!security::constant_time_equal(proof.stable_device_principal,
                                       route_set_.stable_device_principal)) {
        return Status{ErrorCode::protocol_error,
                      "route proof names a foreign stable device principal"};
    }
    if (proof.route_set_generation != route_set_.generation) {
        return Status{ErrorCode::protocol_error,
                      "route proof generation is stale or unknown"};
    }
    if (proof.route_protocol_version < route_set_.minimum_route_protocol) {
        return Status{ErrorCode::protocol_error,
                      "route proof attempts a protocol downgrade"};
    }
    if (member.policy.connection_class != ConnectionClass::either &&
        proof.connection_class != member.policy.connection_class) {
        return Status{ErrorCode::protocol_error,
                      "route connection class violates signed policy"};
    }
    if (member.policy.network_class != NetworkClass::unspecified &&
        proof.network_class != member.policy.network_class) {
        return Status{ErrorCode::protocol_error,
                      "route network class violates signed policy"};
    }
    if (member.policy.expires_unix_ms != 0U && now_unix_ms_ != 0U &&
        now_unix_ms_ >= member.policy.expires_unix_ms) {
        return Status{ErrorCode::protocol_error,
                      "route membership has expired"};
    }
    member.lifecycle = Lifecycle::authenticated;
    member.last_failure = Failure::none;
    return Status::success();
}

Status Coordinator::mark_ready(const ToxPublicKey &key, std::uint64_t worker_id) {
    auto index = member_index(key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    const Status worker = require_worker(member, worker_id);
    if (!worker.ok()) return worker;
    if (member.lifecycle != Lifecycle::authenticated) {
        return Status{ErrorCode::invalid_argument,
                      "route may become ready only after authentication"};
    }
    member.lifecycle = Lifecycle::ready;
    return Status::success();
}

Status Coordinator::authentication_lost(
    const ToxPublicKey &key, std::uint64_t worker_id, Failure failure) {
    auto index = member_index(key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    const Status worker = require_worker(member, worker_id);
    if (!worker.ok()) return worker;
    if (member.lifecycle == Lifecycle::connecting) return Status::success();
    if (member.lifecycle != Lifecycle::authenticated &&
        member.lifecycle != Lifecycle::ready) {
        return Status{ErrorCode::invalid_argument,
                      "route cannot lose authentication from its current state"};
    }
    member.admitted_work = 0U;
    member.lifecycle = Lifecycle::connecting;
    member.last_failure =
        failure == Failure::none ? Failure::authentication : failure;
    return Status::success();
}

Status Coordinator::admit_work(
    const ToxPublicKey &key, std::uint64_t worker_id, std::uint16_t amount) {
    auto index = member_index(key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    const Status worker = require_worker(member, worker_id);
    if (!worker.ok()) return worker;
    if (amount == 0U || member.lifecycle != Lifecycle::ready ||
        amount > member.policy.maximum_active_work - member.admitted_work) {
        return Status{ErrorCode::resource_exhausted,
                      "route is not ready or its signed work budget is exhausted"};
    }
    member.admitted_work = static_cast<std::uint16_t>(member.admitted_work + amount);
    return Status::success();
}

Status Coordinator::release_work(
    const ToxPublicKey &key, std::uint64_t worker_id, std::uint16_t amount) {
    auto index = member_index(key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    const Status worker = require_worker(member, worker_id);
    if (!worker.ok()) return worker;
    if (amount == 0U || amount > member.admitted_work) {
        return Status{ErrorCode::invalid_argument,
                      "route work release exceeds admitted work"};
    }
    member.admitted_work = static_cast<std::uint16_t>(member.admitted_work - amount);
    return Status::success();
}

Status Coordinator::begin_recovery(
    const ToxPublicKey &key, std::uint64_t worker_id, Failure failure) {
    auto index = member_index(key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    const Status worker = require_worker(member, worker_id);
    if (!worker.ok()) return worker;
    if (member.lifecycle != Lifecycle::ready &&
        member.lifecycle != Lifecycle::authenticated &&
        member.lifecycle != Lifecycle::connecting) {
        return Status{ErrorCode::invalid_argument,
                      "route cannot recover from its current state"};
    }
    member.admitted_work = 0U;
    member.last_failure = failure == Failure::none ? Failure::internal : failure;
    if (member.restarts >= member.policy.restart_budget) {
        member.lifecycle = Lifecycle::unavailable;
        member.last_failure = Failure::restart_exhausted;
        return Status{ErrorCode::resource_exhausted,
                      "route restart budget is exhausted"};
    }
    ++member.restarts;
    member.lifecycle = Lifecycle::recovering;
    return Status::success();
}

Status Coordinator::mark_unavailable(
    const ToxPublicKey &key, std::uint64_t worker_id, Failure failure) {
    auto index = member_index(key);
    if (!index) return index.status();
    auto &member = members_[index.value()];
    const Status worker = require_worker(member, worker_id);
    if (!worker.ok()) return worker;
    member.admitted_work = 0U;
    member.lifecycle = Lifecycle::unavailable;
    member.last_failure = failure == Failure::none ? Failure::internal : failure;
    return Status::success();
}

CoordinatorSnapshot Coordinator::snapshot() const {
    return CoordinatorSnapshot{
        route_set_.stable_device_principal, route_set_.generation, members_};
}

const char *to_string(Role role) noexcept {
    switch (role) {
        case Role::protected_route: return "protected";
        case Role::bulk: return "bulk";
    }
    return "unknown";
}

const char *to_string(ConnectionClass value) noexcept {
    switch (value) {
        case ConnectionClass::tcp: return "tcp";
        case ConnectionClass::udp: return "udp";
        case ConnectionClass::either: return "either";
    }
    return "unknown";
}

const char *to_string(NetworkClass value) noexcept {
    switch (value) {
        case NetworkClass::unspecified: return "unspecified";
        case NetworkClass::tox_native: return "tox/native";
        case NetworkClass::tox_tor: return "tox/tor";
        case NetworkClass::tox_i2p: return "tox/i2p";
    }
    return "unknown";
}

Result<NetworkClass> network_class_from_stack(
    const NetworkStack &network) {
    if (network.transport != TransportKind::tox) {
        return Status{ErrorCode::unsupported,
                      "signed route class requires a Tox transport"};
    }
    switch (network.tox_route) {
        case ToxRoute::native: return NetworkClass::tox_native;
        case ToxRoute::tor: return NetworkClass::tox_tor;
        case ToxRoute::i2p:
        case ToxRoute::i2p_construction:
            return NetworkClass::tox_i2p;
    }
    return Status{ErrorCode::unsupported,
                  "signed route class is unsupported"};
}

const char *to_string(Lifecycle lifecycle) noexcept {
    switch (lifecycle) {
        case Lifecycle::configured: return "configured";
        case Lifecycle::connecting: return "connecting";
        case Lifecycle::authenticated: return "authenticated";
        case Lifecycle::ready: return "ready";
        case Lifecycle::recovering: return "recovering";
        case Lifecycle::unavailable: return "unavailable";
    }
    return "unknown";
}

const char *to_string(Failure failure) noexcept {
    switch (failure) {
        case Failure::none: return "none";
        case Failure::connection: return "connection";
        case Failure::authentication: return "authentication";
        case Failure::policy: return "policy";
        case Failure::restart_exhausted: return "restart-exhausted";
        case Failure::worker: return "worker";
        case Failure::transport: return "transport";
        case Failure::internal: return "internal";
    }
    return "unknown";
}

Result<std::string> render_coordinator_snapshot(
    const CoordinatorSnapshot &snapshot, const security::Sodium &sodium) {
    if (snapshot.generation == 0U || all_zero(snapshot.stable_device_principal) ||
        snapshot.members.size() < 2U ||
        snapshot.members.size() > kMaximumRouteMembers) {
        return Status{ErrorCode::internal_error,
                      "route coordinator snapshot is structurally invalid"};
    }
    auto principal_digest = sodium.hash(
        "iotox-route-principal-display-v1", snapshot.stable_device_principal);
    if (!principal_digest) return principal_digest.status();
    std::ostringstream output;
    output << "mode=coordinated\n"
           << "route-set-configured=1\n"
           << "stable-principal-digest="
           << security::hex(principal_digest.value()) << '\n'
           << "route-set-generation=" << snapshot.generation << '\n'
           << "route-count=" << snapshot.members.size() << '\n';
    for (std::size_t index = 0U; index < snapshot.members.size(); ++index) {
        const MemberSnapshot &member = snapshot.members[index];
        if (member.admitted_work > member.policy.maximum_active_work ||
            member.restarts > member.policy.restart_budget) {
            return Status{ErrorCode::internal_error,
                          "route coordinator snapshot violates a signed budget"};
        }
        output << "route-index=" << index
               << " public-key=" << security::hex(member.policy.tox_public_key)
               << " role=" << to_string(member.policy.role)
               << " connection-class="
               << to_string(member.policy.connection_class)
               << " network-class="
               << to_string(member.policy.network_class)
               << " lifecycle=" << to_string(member.lifecycle)
               << " worker-id=" << member.worker_id
               << " admitted-work=" << member.admitted_work
               << " maximum-active-work="
               << member.policy.maximum_active_work
               << " restarts=" << member.restarts
               << " restart-budget=" << member.policy.restart_budget
               << " restart-budget-remaining="
               << (member.policy.restart_budget - member.restarts)
               << " expires-unix-ms=" << member.policy.expires_unix_ms
               << " last-failure=" << to_string(member.last_failure) << '\n';
    }
    return output.str();
}

}  // namespace iotox::routes
