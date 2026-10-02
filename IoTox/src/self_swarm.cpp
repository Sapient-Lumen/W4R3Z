#include "iotox/self_swarm.hpp"

#include "iotox/peer_alias.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <charconv>
#include <cstring>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <string>
#include <system_error>
#include <vector>

namespace iotox::self_swarm {
namespace {

constexpr std::string_view kHeader = "iotox-self-swarm-v1";
constexpr std::string_view kFloorHeader = "iotox-self-swarm-floor-v1";
constexpr std::string_view kDigestDomain = "iotox-self-swarm-roster-digest-v1";
constexpr std::uint64_t kKnownCapabilityMask = security::kAuthorityV3Capabilities;

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t value) {
        return value == 0U;
    });
}

[[nodiscard]] bool nonzero_key(const security::SigningPublicKey &key) noexcept {
    return std::any_of(key.begin(), key.end(), [](std::uint8_t value) {
        return value != 0U;
    });
}

[[nodiscard]] std::string hex_u64(std::uint64_t value) {
    std::ostringstream output;
    output << std::uppercase << std::hex << std::setw(16)
           << std::setfill('0') << value;
    return output.str();
}

[[nodiscard]] Result<std::uint64_t> parse_u64_decimal(
    std::string_view text, std::string_view label) {
    if (text.empty()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is empty"};
    }
    std::uint64_t value = 0U;
    const auto result =
        std::from_chars(text.data(), text.data() + text.size(), value, 10);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not a canonical decimal integer"};
    }
    if (text.size() > 1U && text.front() == '0') {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " has a leading zero"};
    }
    return value;
}

[[nodiscard]] Result<std::uint64_t> parse_u64_hex(
    std::string_view text, std::string_view label) {
    if (text.size() != 16U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " must be 16 hexadecimal characters"};
    }
    std::uint64_t value = 0U;
    const auto result =
        std::from_chars(text.data(), text.data() + text.size(), value, 16);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not hexadecimal"};
    }
    if (hex_u64(value) != text) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not canonical uppercase hex"};
    }
    return value;
}

template <std::size_t Size>
[[nodiscard]] Result<std::array<std::uint8_t, Size>> parse_hex_array(
    std::string_view text, std::string_view label) {
    auto decoded = security::decode_hex_exact(text, Size, label);
    if (!decoded) return decoded.status();
    if (security::hex(decoded.value()) != text) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not canonical uppercase hex"};
    }
    std::array<std::uint8_t, Size> result{};
    std::copy_n(decoded.value().begin(), Size, result.begin());
    return result;
}

[[nodiscard]] Result<MemberStatus> parse_status(std::string_view text) {
    if (text == "active") return MemberStatus::active;
    if (text == "retired") return MemberStatus::retired;
    return Status{ErrorCode::protocol_error,
                  "self-swarm member status is not active or retired"};
}

[[nodiscard]] std::string status_text(MemberStatus status) {
    switch (status) {
        case MemberStatus::active:
            return "active";
        case MemberStatus::retired:
            return "retired";
    }
    return "unknown";
}

[[nodiscard]] std::vector<std::string_view> split_pipe(std::string_view text) {
    std::vector<std::string_view> fields;
    std::size_t begin = 0U;
    while (begin <= text.size()) {
        const std::size_t end = text.find('|', begin);
        if (end == std::string_view::npos) {
            fields.push_back(text.substr(begin));
            break;
        }
        fields.push_back(text.substr(begin, end - begin));
        begin = end + 1U;
    }
    return fields;
}

[[nodiscard]] Result<std::vector<std::string_view>> split_lines(
    std::span<const std::uint8_t> bytes) {
    if (bytes.empty() || bytes.back() != static_cast<std::uint8_t>('\n')) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster must end with exactly one LF"};
    }
    std::string_view text(reinterpret_cast<const char *>(bytes.data()),
                          bytes.size());
    std::vector<std::string_view> lines;
    std::size_t begin = 0U;
    while (begin < text.size()) {
        const std::size_t end = text.find('\n', begin);
        if (end == std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm roster line parser lost final LF"};
        }
        if (end > begin && text[end - 1U] == '\r') {
            return Status{ErrorCode::protocol_error,
                          "self-swarm roster may not contain CRLF"};
        }
        lines.push_back(text.substr(begin, end - begin));
        begin = end + 1U;
    }
    if (!lines.empty() && lines.back().empty()) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster has an extra blank trailing line"};
    }
    return lines;
}

[[nodiscard]] Result<std::string_view> field(
    std::string_view line, std::string_view prefix) {
    if (!line.starts_with(prefix)) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster expected field " + std::string(prefix)};
    }
    return line.substr(prefix.size());
}

[[nodiscard]] Result<Member> parse_member_line(std::string_view line) {
    auto payload = field(line, "member=");
    if (!payload) return payload.status();
    const auto parts = split_pipe(payload.value());
    if (parts.size() != 7U) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm member line must have seven fields"};
    }
    Member member;
    member.alias = std::string(parts[0U]);
    auto principal =
        parse_hex_array<security::kSigningPublicKeyBytes>(parts[1U],
                                                          "member principal");
    auto tox_key =
        parse_hex_array<security::kSigningPublicKeyBytes>(parts[2U],
                                                          "member tox key");
    auto role = security::parse_principal_role(parts[3U]);
    auto capabilities = parse_u64_hex(parts[4U], "member capabilities");
    auto status = parse_status(parts[5U]);
    auto retired_generation =
        parse_u64_decimal(parts[6U], "member retired generation");
    if (!principal) return principal.status();
    if (!tox_key) return tox_key.status();
    if (!role) return role.status();
    if (!capabilities) return capabilities.status();
    if (!status) return status.status();
    if (!retired_generation) return retired_generation.status();
    member.principal = principal.value();
    member.tox_public_key = tox_key.value();
    member.role = role.value();
    member.capabilities = capabilities.value();
    member.status = status.value();
    member.retired_generation = retired_generation.value();
    const Status valid = validate_member(member);
    if (!valid.ok()) return valid;
    return member;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_floor_bytes(
    const Floor &floor) {
    if (!nonzero_key(floor.owner)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm floor owner key is zero"};
    }
    if (floor.generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm floor generation must be nonzero"};
    }
    if (all_zero(floor.digest)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm floor digest is zero"};
    }
    std::ostringstream output;
    output << kFloorHeader << '\n'
           << "owner=" << security::hex(floor.owner) << '\n'
           << "generation=" << floor.generation << '\n'
           << "digest=" << security::hex(floor.digest) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

[[nodiscard]] Result<Floor> decode_floor_bytes(
    std::span<const std::uint8_t> bytes) {
    auto lines = split_lines(bytes);
    if (!lines) return lines.status();
    if (lines.value().size() != 4U || lines.value()[0U] != kFloorHeader) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm floor header or size is invalid"};
    }
    auto owner = field(lines.value()[1U], "owner=");
    auto generation = field(lines.value()[2U], "generation=");
    auto digest = field(lines.value()[3U], "digest=");
    if (!owner) return owner.status();
    if (!generation) return generation.status();
    if (!digest) return digest.status();
    auto owner_key =
        parse_hex_array<security::kSigningPublicKeyBytes>(owner.value(),
                                                          "floor owner");
    auto generation_value =
        parse_u64_decimal(generation.value(), "self-swarm floor generation");
    auto digest_value =
        parse_hex_array<security::kDigestBytes>(digest.value(), "floor digest");
    if (!owner_key) return owner_key.status();
    if (!generation_value) return generation_value.status();
    if (!digest_value) return digest_value.status();
    Floor floor;
    floor.owner = owner_key.value();
    floor.generation = generation_value.value();
    floor.digest = digest_value.value();
    auto canonical = encode_floor_bytes(floor);
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm floor bytes are noncanonical"};
    }
    return floor;
}

[[nodiscard]] bool member_less(const Member &left, const Member &right) {
    return left.alias < right.alias;
}

[[nodiscard]] Status validate_roster_shape(const Roster &roster) {
    if (!nonzero_key(roster.owner)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm roster owner key is zero"};
    }
    if (roster.generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm roster generation must be nonzero"};
    }
    if (roster.members.empty() || roster.members.size() > kMaximumMembers) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm roster must contain 1..64 members"};
    }
    if (roster.generation == 1U && !all_zero(roster.previous_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm generation 1 must have a zero previous digest"};
    }
    if (roster.generation > 1U && all_zero(roster.previous_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm mutation must carry previous digest"};
    }
    std::vector<security::SigningPublicKey> principals;
    std::vector<security::SigningPublicKey> tox_keys;
    principals.reserve(roster.members.size());
    tox_keys.reserve(roster.members.size());
    std::string previous_alias;
    bool active_seen = false;
    for (const Member &member : roster.members) {
        const Status valid = validate_member(member);
        if (!valid.ok()) return valid;
        if (!previous_alias.empty() && member.alias <= previous_alias) {
            return Status{ErrorCode::invalid_argument,
                          "self-swarm roster members are not sorted by alias"};
        }
        if (std::find(principals.begin(), principals.end(), member.principal) !=
            principals.end()) {
            return Status{ErrorCode::invalid_argument,
                          "self-swarm roster repeats a principal"};
        }
        if (std::find(tox_keys.begin(), tox_keys.end(), member.tox_public_key) !=
            tox_keys.end()) {
            return Status{ErrorCode::invalid_argument,
                          "self-swarm roster repeats a Tox route key"};
        }
        active_seen = active_seen || member.status == MemberStatus::active;
        previous_alias = member.alias;
        principals.push_back(member.principal);
        tox_keys.push_back(member.tox_public_key);
    }
    if (!active_seen) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm roster cannot retire every member"};
    }
    return Status::success();
}

}  // namespace

Status validate_member(const Member &member) {
    const Status alias = peer_alias::validate_name(member.alias);
    if (!alias.ok()) {
        return Status{alias.code(), "self-swarm alias is invalid: " + alias.message()};
    }
    if (!nonzero_key(member.principal)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm member principal is zero"};
    }
    if (!nonzero_key(member.tox_public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm member Tox public key is zero"};
    }
    if (member.role == security::PrincipalRole::none ||
        member.role == security::PrincipalRole::owner) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm member role must be a non-owner authority role"};
    }
    if ((member.capabilities & ~kKnownCapabilityMask) != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm member capabilities exceed authority v3"};
    }
    if (member.capabilities == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm member capabilities may not be empty"};
    }
    if (member.status == MemberStatus::active && member.retired_generation != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "active self-swarm member has retired generation"};
    }
    if (member.status == MemberStatus::retired && member.retired_generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "retired self-swarm member lacks retired generation"};
    }
    return Status::success();
}

Result<Roster> create_roster(
    const security::SigningPublicKey &owner, Member self_member) {
    Roster roster;
    roster.owner = owner;
    roster.generation = 1U;
    roster.previous_digest.fill(0U);
    auto valid = validate_member(self_member);
    if (!valid.ok()) return valid;
    roster.members.push_back(std::move(self_member));
    std::sort(roster.members.begin(), roster.members.end(), member_less);
    valid = validate_roster_shape(roster);
    if (!valid.ok()) return valid;
    return roster;
}

Result<Roster> add_member(
    const Roster &current, Member member, const security::Sodium &sodium) {
    Status valid = validate_roster_shape(current);
    if (!valid.ok()) return valid;
    valid = validate_member(member);
    if (!valid.ok()) return valid;
    if (member.status != MemberStatus::active) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm join adds only active members"};
    }
    for (const Member &existing : current.members) {
        if (existing.alias == member.alias) {
            return Status{ErrorCode::invalid_argument,
                          "self-swarm alias already exists"};
        }
        if (existing.principal == member.principal) {
            return Status{ErrorCode::invalid_argument,
                          "self-swarm principal already exists"};
        }
        if (existing.tox_public_key == member.tox_public_key) {
            return Status{ErrorCode::invalid_argument,
                          "self-swarm Tox route key already exists"};
        }
    }
    auto previous = roster_digest(current, sodium);
    if (!previous) return previous.status();
    Roster next = current;
    next.generation = current.generation + 1U;
    if (next.generation == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "self-swarm generation overflow"};
    }
    next.previous_digest = previous.value();
    next.signature.fill(0U);
    next.members.push_back(std::move(member));
    std::sort(next.members.begin(), next.members.end(), member_less);
    valid = validate_roster_shape(next);
    if (!valid.ok()) return valid;
    return next;
}

Result<Roster> retire_member(
    const Roster &current, std::string_view alias,
    const security::Sodium &sodium) {
    Status valid = validate_roster_shape(current);
    if (!valid.ok()) return valid;
    auto previous = roster_digest(current, sodium);
    if (!previous) return previous.status();
    Roster next = current;
    next.generation = current.generation + 1U;
    if (next.generation == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "self-swarm generation overflow"};
    }
    next.previous_digest = previous.value();
    next.signature.fill(0U);
    bool found = false;
    for (Member &member : next.members) {
        if (member.alias != alias) continue;
        found = true;
        if (member.status == MemberStatus::retired) {
            return Status{ErrorCode::invalid_argument,
                          "self-swarm member is already retired"};
        }
        member.status = MemberStatus::retired;
        member.retired_generation = next.generation;
    }
    if (!found) {
        return Status{ErrorCode::not_found,
                      "self-swarm member alias is not present"};
    }
    valid = validate_roster_shape(next);
    if (!valid.ok()) return valid;
    return next;
}

Result<std::vector<std::uint8_t>> encode_unsigned_roster(const Roster &roster) {
    const Status valid = validate_roster_shape(roster);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kHeader << '\n';
    output << "owner=" << security::hex(roster.owner) << '\n';
    output << "generation=" << roster.generation << '\n';
    output << "previous-digest=" << security::hex(roster.previous_digest) << '\n';
    output << "member-count=" << roster.members.size() << '\n';
    for (const Member &member : roster.members) {
        output << "member=" << member.alias << '|'
               << security::hex(member.principal) << '|'
               << security::hex(member.tox_public_key) << '|'
               << security::to_string(member.role) << '|'
               << hex_u64(member.capabilities) << '|'
               << status_text(member.status) << '|'
               << member.retired_generation << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> roster_digest(
    const Roster &roster, const security::Sodium &sodium) {
    auto unsigned_bytes = encode_unsigned_roster(roster);
    if (!unsigned_bytes) return unsigned_bytes.status();
    return sodium.hash(kDigestDomain, unsigned_bytes.value());
}

Result<Floor> floor_from_roster(
    const Roster &roster, const security::Sodium &sodium) {
    auto digest = roster_digest(roster, sodium);
    if (!digest) return digest.status();
    Floor floor;
    floor.owner = roster.owner;
    floor.generation = roster.generation;
    floor.digest = digest.value();
    auto canonical = encode_floor_bytes(floor);
    if (!canonical) return canonical.status();
    return floor;
}

Status check_floor(
    const Roster &roster, const Floor &floor,
    const security::Sodium &sodium) {
    auto current = floor_from_roster(roster, sodium);
    if (!current) return current.status();
    if (current.value().owner != floor.owner) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster owner is not the durable floor owner"};
    }
    if (current.value().generation < floor.generation) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster generation is below the durable floor"};
    }
    if (current.value().generation == floor.generation &&
        current.value().digest != floor.digest) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster conflicts with the durable floor digest"};
    }
    return Status::success();
}

Status sign_roster(
    Roster &roster, const security::SigningKeyPair &owner_keys,
    const security::Sodium &sodium) {
    if (roster.owner != owner_keys.public_key()) {
        return Status{ErrorCode::invalid_argument,
                      "RecallRoot owner does not match self-swarm roster owner"};
    }
    auto digest = roster_digest(roster, sodium);
    if (!digest) return digest.status();
    auto signature = sodium.sign_detached(digest.value(), owner_keys.secret_key());
    if (!signature) return signature.status();
    roster.signature = signature.value();
    return Status::success();
}

Result<std::vector<std::uint8_t>> encode_signed_roster(const Roster &roster) {
    const Status valid = validate_roster_shape(roster);
    if (!valid.ok()) return valid;
    if (all_zero(roster.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm roster signature is empty"};
    }
    auto bytes = encode_unsigned_roster(roster);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(roster.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(), signature.end());
    return bytes;
}

Result<Roster> decode_signed_roster(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes);
    if (!lines) return lines.status();
    if (lines.value().size() < 6U || lines.value()[0U] != kHeader) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster header is invalid"};
    }
    Roster roster;
    auto owner = field(lines.value()[1U], "owner=");
    auto generation = field(lines.value()[2U], "generation=");
    auto previous = field(lines.value()[3U], "previous-digest=");
    auto member_count = field(lines.value()[4U], "member-count=");
    if (!owner) return owner.status();
    if (!generation) return generation.status();
    if (!previous) return previous.status();
    if (!member_count) return member_count.status();
    auto owner_key =
        parse_hex_array<security::kSigningPublicKeyBytes>(owner.value(), "owner");
    auto generation_value =
        parse_u64_decimal(generation.value(), "self-swarm generation");
    auto previous_digest =
        parse_hex_array<security::kDigestBytes>(previous.value(),
                                                "previous digest");
    auto count =
        parse_u64_decimal(member_count.value(), "self-swarm member count");
    if (!owner_key) return owner_key.status();
    if (!generation_value) return generation_value.status();
    if (!previous_digest) return previous_digest.status();
    if (!count) return count.status();
    if (count.value() > kMaximumMembers) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm member count exceeds bound"};
    }
    if (lines.value().size() != 6U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster member count does not match line count"};
    }
    roster.owner = owner_key.value();
    roster.generation = generation_value.value();
    roster.previous_digest = previous_digest.value();
    roster.members.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto member = parse_member_line(lines.value()[5U + index]);
        if (!member) return member.status();
        roster.members.push_back(std::move(member).value());
    }
    auto signature_line = field(lines.value().back(), "signature=");
    if (!signature_line) return signature_line.status();
    auto signature =
        parse_hex_array<security::kSignatureBytes>(signature_line.value(),
                                                   "self-swarm signature");
    if (!signature) return signature.status();
    roster.signature = signature.value();
    const Status valid = validate_roster_shape(roster);
    if (!valid.ok()) return valid;

    auto canonical = encode_signed_roster(roster);
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster bytes are noncanonical"};
    }
    auto digest = roster_digest(roster, sodium);
    if (!digest) return digest.status();
    const Status verified =
        sodium.verify_detached(roster.signature, digest.value(), roster.owner);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster signature is invalid"};
    }
    return roster;
}

Result<Roster> load_roster(
    const std::filesystem::path &path, const security::Sodium &sodium) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    return decode_signed_roster(bytes.value(), sodium);
}

Status write_roster(const std::filesystem::path &path, const Roster &roster) {
    auto bytes = encode_signed_roster(roster);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Status create_roster_file(const std::filesystem::path &path, const Roster &roster) {
    std::error_code exists_error;
    if (std::filesystem::exists(path, exists_error)) {
        return Status{ErrorCode::invalid_argument,
                      "self-swarm roster already exists: " + path.string()};
    }
    if (exists_error) {
        return Status{ErrorCode::io_error,
                      "unable to inspect self-swarm roster path '" +
                          path.string() + "': " + exists_error.message()};
    }
    return write_roster(path, roster);
}

Result<Floor> load_floor(const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    return decode_floor_bytes(bytes.value());
}

Status write_floor(const std::filesystem::path &path, const Floor &floor) {
    auto bytes = encode_floor_bytes(floor);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<Floor> commit_floor(
    const std::filesystem::path &path, const Roster &roster,
    const security::Sodium &sodium) {
    auto next = floor_from_roster(roster, sodium);
    if (!next) return next.status();
    auto current = load_floor(path);
    if (current) {
        if (current.value().owner != next.value().owner) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm floor owner does not match roster owner"};
        }
        if (next.value().generation < current.value().generation) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm roster generation is below the durable floor"};
        }
        if (next.value().generation == current.value().generation &&
            next.value().digest != current.value().digest) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm roster conflicts with the durable floor digest"};
        }
        if (next.value().generation == current.value().generation) {
            return current.value();
        }
    } else if (current.status().code() != ErrorCode::not_found) {
        return current.status();
    }
    const Status written = write_floor(path, next.value());
    if (!written.ok()) return written;
    return next.value();
}

Status inspect_roster(
    const Roster &roster, const InspectionOptions &options) {
    const Status valid = validate_roster_shape(roster);
    if (!valid.ok()) return valid;
    if (options.minimum_generation != 0U &&
        roster.generation < options.minimum_generation) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster generation is below the required floor"};
    }
    if (options.have_expected_owner &&
        roster.owner != options.expected_owner) {
        return Status{ErrorCode::protocol_error,
                      "self-swarm roster owner does not match expectation"};
    }
    if (options.have_expected_member) {
        auto member = find_member(roster, options.expected_member_alias);
        if (!member) return member.status();
        if (member.value().principal != options.expected_member_principal) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm member principal does not match expectation"};
        }
        if (member.value().status != MemberStatus::active) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm expected member is retired"};
        }
    }
    if (options.have_expected_route) {
        auto member = find_member(roster, options.expected_route_alias);
        if (!member) return member.status();
        if (member.value().tox_public_key != options.expected_route_key) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm member route key does not match expectation"};
        }
        if (member.value().status != MemberStatus::active) {
            return Status{ErrorCode::protocol_error,
                          "self-swarm expected route member is retired"};
        }
    }
    return Status::success();
}

Result<Member> find_member(const Roster &roster, std::string_view alias) {
    const auto found =
        std::find_if(roster.members.begin(), roster.members.end(),
                     [&](const Member &member) { return member.alias == alias; });
    if (found == roster.members.end()) {
        return Status{ErrorCode::not_found,
                      "self-swarm member alias is not present"};
    }
    return *found;
}

std::string render_roster(const Roster &roster) {
    std::ostringstream output;
    std::size_t active = 0U;
    std::size_t retired = 0U;
    for (const Member &member : roster.members) {
        if (member.status == MemberStatus::active) ++active;
        else ++retired;
    }
    output << "iotox-self-swarm-v1\n"
           << "owner=" << security::hex(roster.owner) << '\n'
           << "generation=" << roster.generation << '\n'
           << "previous-digest=" << security::hex(roster.previous_digest) << '\n'
           << "members=" << roster.members.size() << '\n'
           << "active-members=" << active << '\n'
           << "retired-members=" << retired << '\n';
    for (const Member &member : roster.members) {
        output << "member alias=" << member.alias
               << " status=" << status_text(member.status)
               << " role=" << security::to_string(member.role)
               << " capabilities="
               << security::render_capability_set(member.capabilities)
               << " principal=" << security::hex(member.principal)
               << " tox=" << security::hex(member.tox_public_key);
        if (member.status == MemberStatus::retired) {
            output << " retired-generation=" << member.retired_generation;
        }
        output << '\n';
    }
    output << "boundary=friendship-is-not-authority; self-roster-membership-still-needs-authority-grants\n";
    return output.str();
}

std::string render_grant_plan(
    const Roster &roster, std::string_view from_alias,
    std::optional<security::PrincipalRole> role_override,
    std::optional<std::uint64_t> capabilities_override) {
    std::ostringstream output;
    std::size_t commands = 0U;
    for (const Member &member : roster.members) {
        if (member.status != MemberStatus::active) continue;
        if (!from_alias.empty() && member.alias == from_alias) continue;
        ++commands;
    }
    output << "iotox-self-swarm-grant-plan-v1\n"
           << "roster-generation=" << roster.generation << '\n'
           << "owner=" << security::hex(roster.owner) << '\n'
           << "commands=" << commands << '\n';
    for (const Member &member : roster.members) {
        if (member.status != MemberStatus::active) continue;
        if (!from_alias.empty() && member.alias == from_alias) continue;
        const security::PrincipalRole role =
            role_override.value_or(member.role);
        const std::uint64_t capabilities =
            capabilities_override.value_or(member.capabilities);
        output << "grant target=" << member.alias
               << " principal=" << security::hex(member.principal)
               << " role=" << security::to_string(role)
               << " capabilities="
               << security::render_capability_set(capabilities) << '\n'
               << "grant-command=cat RECALLROOT.txt | iotox "
               << "authority-delegate-self-recall-stdin alias:"
               << member.alias << ' ' << security::to_string(role) << ' '
               << security::render_capability_set(capabilities) << '\n';
    }
    output << "boundary=review-before-running; no-sudo-without-profile; no-friendship-authority-collapse\n";
    return output.str();
}

Result<std::string> render_retire_plan(
    const Roster &roster, std::string_view alias) {
    auto member = find_member(roster, alias);
    if (!member) return member.status();
    std::ostringstream output;
    output << "iotox-self-swarm-retire-plan-v1\n"
           << "roster-generation=" << roster.generation << '\n'
           << "target=" << member.value().alias << '\n'
           << "target-status=" << status_text(member.value().status) << '\n'
           << "target-principal=" << security::hex(member.value().principal) << '\n'
           << "revoke-command=cat RECALLROOT.txt | iotox "
           << "authority-revoke-remote-recall-stdin alias:"
           << member.value().alias << ' '
           << security::hex(member.value().principal) << '\n'
           << "boundary=retirement-is-roster-state; revocation-still-requires-authority-command\n";
    return output.str();
}

std::string render_floor(const Floor &floor) {
    std::ostringstream output;
    output << "iotox-self-swarm-floor-v1\n"
           << "owner=" << security::hex(floor.owner) << '\n'
           << "generation=" << floor.generation << '\n'
           << "digest=" << security::hex(floor.digest) << '\n'
           << "boundary=local-high-water-floor; not-independent-rollback-witness\n";
    return output.str();
}

}  // namespace iotox::self_swarm
