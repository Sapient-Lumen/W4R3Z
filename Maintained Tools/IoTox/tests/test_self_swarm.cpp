#include "test_harness.hpp"

#include "iotox/security/sodium.hpp"
#include "iotox/self_swarm.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <string>
#include <system_error>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-self-swarm-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        if (char *created = ::mkdtemp(bytes.data()); created != nullptr) {
            root_ = created;
        }
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(root_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &root() const { return root_; }

  private:
    std::filesystem::path root_;
};

iotox::security::SigningKeyPair keypair(
    iotox::security::Sodium &sodium, std::uint8_t tag) {
    iotox::security::SigningSeed seed{};
    seed.fill(tag);
    auto keys = sodium.signing_keypair_from_seed(seed);
    IOTOX_CHECK_MSG(keys.ok(), keys.status().message());
    return std::move(keys).value();
}

iotox::security::SigningPublicKey public_key(
    iotox::security::Sodium &sodium, std::uint8_t tag) {
    auto keys = keypair(sodium, tag);
    return keys.public_key();
}

iotox::self_swarm::Member member(
    iotox::security::Sodium &sodium, std::string alias,
    std::uint8_t principal_tag, std::uint8_t tox_tag,
    std::uint64_t capabilities =
        static_cast<std::uint64_t>(
            iotox::security::Capability::interactive_terminal)) {
    iotox::self_swarm::Member result;
    result.alias = std::move(alias);
    result.principal = public_key(sodium, principal_tag);
    result.tox_public_key = public_key(sodium, tox_tag);
    result.role = iotox::security::PrincipalRole::operator_role;
    result.capabilities = capabilities;
    return result;
}

}  // namespace

IOTOX_TEST("self swarm roster signs canonical joins and retirements") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xA1U);

    auto created = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "desktop", 0x11U, 0x21U));
    IOTOX_CHECK_MSG(created.ok(), created.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    created.value(), owner, sodium.value()).ok());
    auto encoded = iotox::self_swarm::encode_signed_roster(created.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto decoded =
        iotox::self_swarm::decode_signed_roster(encoded.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value().generation == 1U);
    IOTOX_CHECK(decoded.value().members.size() == 1U);

    auto joined = iotox::self_swarm::add_member(
        decoded.value(), member(sodium.value(), "laptop", 0x12U, 0x22U),
        sodium.value());
    IOTOX_CHECK_MSG(joined.ok(), joined.status().message());
    IOTOX_CHECK(joined.value().generation == 2U);
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    joined.value(), owner, sodium.value()).ok());
    auto joined_digest =
        iotox::self_swarm::roster_digest(joined.value(), sodium.value());
    IOTOX_CHECK_MSG(joined_digest.ok(), joined_digest.status().message());

    iotox::self_swarm::InspectionOptions stale_options;
    stale_options.minimum_generation = 2U;
    auto stale = iotox::self_swarm::inspect_roster(
        created.value(), stale_options);
    IOTOX_CHECK(!stale.ok());

    auto wrong_member = iotox::self_swarm::InspectionOptions{};
    wrong_member.expected_member_alias = "laptop";
    wrong_member.expected_member_principal = public_key(sodium.value(), 0x13U);
    wrong_member.have_expected_member = true;
    IOTOX_CHECK(!iotox::self_swarm::inspect_roster(
                    joined.value(), wrong_member).ok());

    auto retired = iotox::self_swarm::retire_member(
        joined.value(), "laptop", sodium.value());
    IOTOX_CHECK_MSG(retired.ok(), retired.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    retired.value(), owner, sodium.value()).ok());
    const std::string grant_plan =
        iotox::self_swarm::render_grant_plan(retired.value(), "desktop");
    IOTOX_CHECK(grant_plan.find("target=laptop") == std::string::npos);
    auto retire_plan =
        iotox::self_swarm::render_retire_plan(retired.value(), "laptop");
    IOTOX_CHECK_MSG(retire_plan.ok(), retire_plan.status().message());
    IOTOX_CHECK(retire_plan.value().find("authority-revoke-remote-recall-stdin "
                                         "alias:laptop") != std::string::npos);
}

IOTOX_TEST("self swarm roster rejects tamper duplicate and wrong owner signing") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xB1U);
    auto wrong_owner = keypair(sodium.value(), 0xB2U);

    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "alpha", 0x31U, 0x41U));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(!iotox::self_swarm::sign_roster(
                    roster.value(), wrong_owner, sodium.value()).ok());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), owner, sodium.value()).ok());
    IOTOX_CHECK(!iotox::self_swarm::add_member(
                    roster.value(), member(sodium.value(), "alpha", 0x32U, 0x42U),
                    sodium.value()).ok());
    IOTOX_CHECK(!iotox::self_swarm::add_member(
                    roster.value(), member(sodium.value(), "beta", 0x31U, 0x43U),
                    sodium.value()).ok());

    auto encoded = iotox::self_swarm::encode_signed_roster(roster.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    const std::string needle{"alpha"};
    const auto found = std::search(
        encoded.value().begin(), encoded.value().end(),
        needle.begin(), needle.end());
    IOTOX_CHECK(found != encoded.value().end());
    *found = static_cast<std::uint8_t>('o');
    auto decoded =
        iotox::self_swarm::decode_signed_roster(encoded.value(), sodium.value());
    IOTOX_CHECK(!decoded.ok());
}

IOTOX_TEST("self swarm roster files are no-clobber on create and replace on mutation") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xC1U);
    TemporaryDirectory directory;
    const std::filesystem::path path = directory.root() / "self.swarm";

    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "desktop", 0x51U, 0x61U));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), owner, sodium.value()).ok());
    IOTOX_CHECK(iotox::self_swarm::create_roster_file(path, roster.value()).ok());
    IOTOX_CHECK(!iotox::self_swarm::create_roster_file(path, roster.value()).ok());
    auto loaded = iotox::self_swarm::load_roster(path, sodium.value());
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value().generation == 1U);

    auto next = iotox::self_swarm::add_member(
        loaded.value(), member(sodium.value(), "laptop", 0x52U, 0x62U),
        sodium.value());
    IOTOX_CHECK_MSG(next.ok(), next.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    next.value(), owner, sodium.value()).ok());
    IOTOX_CHECK(iotox::self_swarm::write_roster(path, next.value()).ok());
    loaded = iotox::self_swarm::load_roster(path, sodium.value());
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value().generation == 2U);
    IOTOX_CHECK(loaded.value().members.size() == 2U);
}

IOTOX_TEST("self swarm durable floor rejects rollback and same generation fork") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xD1U);
    TemporaryDirectory directory;
    const std::filesystem::path floor_path = directory.root() / "self.floor";

    auto gen1 = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "desktop", 0x71U, 0x81U));
    IOTOX_CHECK_MSG(gen1.ok(), gen1.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    gen1.value(), owner, sodium.value()).ok());
    auto floor1 =
        iotox::self_swarm::commit_floor(floor_path, gen1.value(), sodium.value());
    IOTOX_CHECK_MSG(floor1.ok(), floor1.status().message());
    IOTOX_CHECK(floor1.value().generation == 1U);

    auto gen2 = iotox::self_swarm::add_member(
        gen1.value(), member(sodium.value(), "laptop", 0x72U, 0x82U),
        sodium.value());
    IOTOX_CHECK_MSG(gen2.ok(), gen2.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    gen2.value(), owner, sodium.value()).ok());
    auto floor2 =
        iotox::self_swarm::commit_floor(floor_path, gen2.value(), sodium.value());
    IOTOX_CHECK_MSG(floor2.ok(), floor2.status().message());
    IOTOX_CHECK(floor2.value().generation == 2U);
    auto loaded = iotox::self_swarm::load_floor(floor_path);
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value() == floor2.value());
    IOTOX_CHECK(!iotox::self_swarm::commit_floor(
                    floor_path, gen1.value(), sodium.value()).ok());
    IOTOX_CHECK(!iotox::self_swarm::check_floor(
                    gen1.value(), floor2.value(), sodium.value()).ok());

    auto fork = iotox::self_swarm::add_member(
        gen1.value(), member(sodium.value(), "tablet", 0x73U, 0x83U),
        sodium.value());
    IOTOX_CHECK_MSG(fork.ok(), fork.status().message());
    IOTOX_CHECK(fork.value().generation == 2U);
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    fork.value(), owner, sodium.value()).ok());
    IOTOX_CHECK(!iotox::self_swarm::check_floor(
                    fork.value(), floor2.value(), sodium.value()).ok());
    IOTOX_CHECK(!iotox::self_swarm::commit_floor(
                    floor_path, fork.value(), sodium.value()).ok());
    IOTOX_CHECK(
        iotox::self_swarm::render_floor(floor2.value()).find(
            "local-high-water-floor") != std::string::npos);
}
