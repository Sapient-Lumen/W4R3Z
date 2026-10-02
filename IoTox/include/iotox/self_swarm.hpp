#pragma once

#include "iotox/security/authority.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::self_swarm {

inline constexpr std::size_t kMaximumMembers = 64U;

enum class MemberStatus : std::uint8_t {
    active = 1U,
    retired = 2U,
};

struct Member {
    std::string alias;
    security::SigningPublicKey principal{};
    security::SigningPublicKey tox_public_key{};
    security::PrincipalRole role{security::PrincipalRole::operator_role};
    std::uint64_t capabilities{0U};
    MemberStatus status{MemberStatus::active};
    std::uint64_t retired_generation{0U};

    [[nodiscard]] bool operator==(const Member &) const = default;
};

struct Roster {
    security::SigningPublicKey owner{};
    std::uint64_t generation{0U};
    security::Digest previous_digest{};
    std::vector<Member> members;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const Roster &) const = default;
};

struct Floor {
    security::SigningPublicKey owner{};
    std::uint64_t generation{0U};
    security::Digest digest{};

    [[nodiscard]] bool operator==(const Floor &) const = default;
};

struct InspectionOptions {
    std::uint64_t minimum_generation{0U};
    std::filesystem::path floor_path;
    bool have_floor_path{false};
    bool prove_routes{false};
    security::SigningPublicKey expected_owner{};
    bool have_expected_owner{false};
    std::string expected_member_alias;
    security::SigningPublicKey expected_member_principal{};
    bool have_expected_member{false};
    std::string expected_route_alias;
    security::SigningPublicKey expected_route_key{};
    bool have_expected_route{false};
};

[[nodiscard]] Status validate_member(const Member &member);
[[nodiscard]] Result<Roster> create_roster(
    const security::SigningPublicKey &owner, Member self_member);
[[nodiscard]] Result<Roster> add_member(
    const Roster &current, Member member, const security::Sodium &sodium);
[[nodiscard]] Result<Roster> retire_member(
    const Roster &current, std::string_view alias,
    const security::Sodium &sodium);

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned_roster(
    const Roster &roster);
[[nodiscard]] Result<security::Digest> roster_digest(
    const Roster &roster, const security::Sodium &sodium);
[[nodiscard]] Result<Floor> floor_from_roster(
    const Roster &roster, const security::Sodium &sodium);
[[nodiscard]] Status check_floor(
    const Roster &roster, const Floor &floor,
    const security::Sodium &sodium);
[[nodiscard]] Status sign_roster(
    Roster &roster, const security::SigningKeyPair &owner_keys,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed_roster(
    const Roster &roster);
[[nodiscard]] Result<Roster> decode_signed_roster(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);

[[nodiscard]] Result<Roster> load_roster(
    const std::filesystem::path &path, const security::Sodium &sodium);
[[nodiscard]] Status write_roster(
    const std::filesystem::path &path, const Roster &roster);
[[nodiscard]] Status create_roster_file(
    const std::filesystem::path &path, const Roster &roster);
[[nodiscard]] Result<Floor> load_floor(const std::filesystem::path &path);
[[nodiscard]] Status write_floor(
    const std::filesystem::path &path, const Floor &floor);
[[nodiscard]] Result<Floor> commit_floor(
    const std::filesystem::path &path, const Roster &roster,
    const security::Sodium &sodium);

[[nodiscard]] Status inspect_roster(
    const Roster &roster, const InspectionOptions &options);
[[nodiscard]] Result<Member> find_member(
    const Roster &roster, std::string_view alias);
[[nodiscard]] std::string render_roster(const Roster &roster);
[[nodiscard]] std::string render_grant_plan(
    const Roster &roster, std::string_view from_alias = {},
    std::optional<security::PrincipalRole> role_override = std::nullopt,
    std::optional<std::uint64_t> capabilities_override = std::nullopt);
[[nodiscard]] Result<std::string> render_retire_plan(
    const Roster &roster, std::string_view alias);
[[nodiscard]] std::string render_floor(const Floor &floor);

}  // namespace iotox::self_swarm
